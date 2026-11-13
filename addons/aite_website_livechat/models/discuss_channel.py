# -*- coding: utf-8 -*-
import logging
import re
from datetime import timedelta
from urllib.parse import urlsplit

from markupsafe import Markup

from odoo import api, fields, models
from odoo.fields import Domain
from odoo.tools import email_normalize, html2plaintext, plaintext2html

from odoo.addons.im_livechat.models.discuss_channel import is_livechat_channel
from odoo.addons.mail.tools.discuss import Store

from .im_livechat_channel import AWAY_CONTACT_REQUEST

_logger = logging.getLogger(__name__)

# Conversations d'un canal toujours joignable : le nettoyage quotidien d'Odoo
# clôt une conversation au bout d'un jour sans activité. Celles qui attendent
# une réponse (question du visiteur sans réponse d'un opérateur) ou dont la
# réponse n'a pas encore été vue par le visiteur restent ouvertes jusqu'à
# 7 jours.
SESSION_KEEP_OPEN_DELAY = timedelta(days=7)

# Réponse par e-mail. Règle de cadence : un e-mail au plus toutes les
# 10 minutes par conversation. Le premier part 2 minutes après la première
# réponse écrite pendant l'absence du visiteur ; tout ce que les opérateurs
# écrivent d'ici l'envoi y est ajouté. Les réponses suivantes attendent
# l'e-mail suivant, au moins 10 minutes après le précédent, qui les reprend
# toutes.
EMAIL_GROUPING_DELAY = timedelta(minutes=2)
EMAIL_MIN_INTERVAL = timedelta(minutes=10)

# Coordonnées cherchées dans les 10 000 premiers caractères d'un message
# seulement : un message démesuré ne doit pas occuper le serveur.
CONTACT_SCAN_MAX_CHARS = 10000
# Adresse e-mail dans un texte libre (« écrivez-moi à jean.dupont@exemple.cm »).
# Longueurs bornées (64 caractères avant « @ », 63 par partie du domaine) et
# début d'adresse imposé : la recherche reste linéaire, même sur un texte
# fabriqué pour la ralentir.
_EMAIL_LOCAL_CHARS = r"A-Za-z0-9._%+\-"
EMAIL_IN_TEXT_RE = re.compile(
    rf"(?<![{_EMAIL_LOCAL_CHARS}])[{_EMAIL_LOCAL_CHARS}]{{1,64}}"
    r"@[A-Za-z0-9\-]{1,63}(?:\.[A-Za-z0-9\-]{1,63}){0,8}\.[A-Za-z]{2,24}"
)
# Un message court, qui ne contient guère qu'une adresse (« Pardon, plutôt
# jean@exemple.cm » : cinq mots au plus en dehors de l'adresse), corrige
# l'adresse déjà relevée ; une adresse citée au fil d'une phrase (« mon
# comptable, compta@…, attend aussi votre devis ») ne la remplace pas.
EMAIL_CORRECTION_MAX_WORDS = 5
# Numéro de téléphone : 8 à 15 chiffres, « + » ou « 00 » facultatif, séparés
# au plus par deux espaces, points, tirets ou parenthèses (pas de « / » :
# une date n'est pas un numéro).
PHONE_IN_TEXT_RE = re.compile(r"(?<![\w+])(?:\+|00)?\d(?:[ .\-()]{0,2}\d){7,18}(?!\w)")
PHONE_MIN_DIGITS = 8
PHONE_MAX_DIGITS = 15


class DiscussChannel(models.Model):
    _inherit = 'discuss.channel'

    # Coordonnées du visiteur, réservées aux utilisateurs internes : un
    # visiteur (invité ou portail) ne peut pas les lire, même pour sa propre
    # conversation.
    aite_visitor_email = fields.Char(
        string="E-mail du visiteur",
        groups="base.group_user",
        readonly=True,
        copy=False,
        help="Première adresse que le visiteur écrit dans la conversation "
             "(hors adresses de l'entreprise), à défaut celle de son compte. "
             "Un message qui ne contient guère que sa nouvelle adresse la "
             "corrige. Les réponses par e-mail ne partent que vers elle.",
    )
    aite_visitor_phone = fields.Char(
        string="Téléphone du visiteur",
        groups="base.group_user",
        readonly=True,
        copy=False,
        help="Numéro saisi par le visiteur dans la conversation (le plus "
             "récent), affiché à l'opérateur.",
    )
    aite_away_checked = fields.Boolean(
        string="Absence vérifiée",
        groups="base.group_user",
        readonly=True,
        copy=False,
        help="Le premier message du visiteur à un opérateur a été traité : le "
             "message d'absence ne peut plus être envoyé dans cette conversation.",
    )
    aite_visitor_left_dt = fields.Datetime(
        string="Chat fermé par le visiteur",
        groups="base.group_user",
        readonly=True,
        copy=False,
        help="Le visiteur a fermé la fenêtre du chat avant d'avoir reçu une "
             "réponse : la conversation reste ouverte pour l'opérateur, dont "
             "la réponse part par e-mail.",
    )
    aite_email_mail_id = fields.Many2one(
        'mail.mail',
        string="Dernier e-mail au visiteur",
        groups="base.group_system",
        ondelete='set null',
        readonly=True,
        copy=False,
    )
    aite_email_first_message_id = fields.Many2one(
        'mail.message',
        string="Première réponse du dernier e-mail",
        groups="base.group_system",
        ondelete='set null',
        readonly=True,
        copy=False,
    )
    aite_email_scheduled_dt = fields.Datetime(
        string="Envoi du dernier e-mail",
        groups="base.group_user",
        readonly=True,
        copy=False,
    )
    aite_email_previous_dt = fields.Datetime(
        string="Envoi de l'e-mail précédent",
        groups="base.group_system",
        readonly=True,
        copy=False,
    )
    # Pour le modèle d'e-mail (calculés, non stockés).
    aite_email_reply_html = fields.Html(
        string="Réponses à envoyer",
        compute='_compute_aite_email_reply_html',
        compute_sudo=True,
        sanitize=False,
        groups="base.group_user",
    )
    aite_email_website_id = fields.Many2one(
        'website',
        string="Site de la conversation",
        compute='_compute_aite_email_website_id',
        compute_sudo=True,
        groups="base.group_user",
    )

    # ------------------------------------------------------------------
    # Champs calculés
    # ------------------------------------------------------------------

    def _compute_aite_email_reply_html(self):
        for channel in self:
            channel.aite_email_reply_html = channel._aite_email_reply_body()

    def _compute_aite_email_website_id(self):
        Website = self.env['website'].sudo()
        for channel in self:
            website = channel.sudo().livechat_visitor_id.website_id
            if not website and channel.livechat_channel_id:
                website = Website.search([('channel_id', '=', channel.livechat_channel_id.id)], limit=1)
            channel.aite_email_website_id = website or Website.search([], limit=1)

    # ------------------------------------------------------------------
    # Données envoyées à Discuss
    # ------------------------------------------------------------------

    def _to_store_defaults(self, target):
        fields_to_store = super()._to_store_defaults(target)
        if target.is_internal(self.env):
            fields_to_store += [
                Store.Attr("aite_visitor_email", predicate=is_livechat_channel),
                Store.Attr("aite_visitor_phone", predicate=is_livechat_channel),
            ]
        return fields_to_store

    def _get_last_messages(self):
        # Dernier message de chaque conversation, pour l'aperçu de la liste des
        # messages (Odoo web, application mobile) : la question du visiteur,
        # pas le message d'absence publié juste après elle.
        messages = super()._get_last_messages()
        away_messages = messages.filtered(lambda message: message.message_type == 'auto_comment')
        if not away_messages:
            return messages
        livechats = self.browse(away_messages.mapped('res_id')).filtered(lambda channel: channel.channel_type == 'livechat')
        # sudo: mail.message - comme le natif, qui lit en SQL le dernier
        # message des conversations demandées.
        Message = self.env['mail.message'].sudo()
        for channel in livechats:
            previous = Message.search([
                ('model', '=', 'discuss.channel'),
                ('res_id', '=', channel.id),
                ('message_type', '!=', 'auto_comment'),
            ], order='id desc', limit=1).with_env(self.env)
            if previous:
                away = away_messages.filtered(lambda message: message.res_id == channel.id)
                messages = (messages - away) | previous
        return messages

    def _sync_field_names(self):
        # Affichage en direct dans le panneau « Informations » de l'opérateur,
        # par le canal de bus réservé aux utilisateurs internes.
        field_names = super()._sync_field_names()
        field_names["internal_users"].extend([
            Store.Attr("aite_visitor_email", predicate=is_livechat_channel),
            Store.Attr("aite_visitor_phone", predicate=is_livechat_channel),
        ])
        return field_names

    # ------------------------------------------------------------------
    # Messages
    # ------------------------------------------------------------------

    def message_post(self, **kwargs):
        message = super().message_post(**kwargs)
        if (
            len(self) == 1
            and self.channel_type == 'livechat'
            and not self.env.context.get('aite_livechat_auto_reply')
        ):
            # sudo: discuss.channel - le visiteur (invité) n'a pas accès en
            # écriture à la conversation ni à ses champs internes.
            self.sudo()._aite_after_livechat_message(message.sudo())
        return message

    def _message_post_after_hook(self, message, msg_vals):
        if not self.env.context.get('aite_livechat_auto_reply'):
            return super()._message_post_after_hook(message, msg_vals)
        # Message d'absence : il est signé de l'opérateur, mais ce n'est pas
        # une réponse de sa part. Les statistiques du Live Chat (nombre de
        # messages, délai de première réponse, conversation « jamais
        # répondue ») restent celles d'avant.
        channel_sudo = self.sudo()
        histories = channel_sudo.livechat_channel_member_history_ids
        saved = {history: (history.message_count, history.response_time_hour) for history in histories}
        failure = channel_sudo.livechat_failure
        result = super()._message_post_after_hook(message, msg_vals)
        for history, (message_count, response_time) in saved.items():
            if (history.message_count, history.response_time_hour) != (message_count, response_time):
                history.write({'message_count': message_count, 'response_time_hour': response_time})
        if channel_sudo.livechat_failure != failure:
            channel_sudo.livechat_failure = failure
        return result

    def _forward_human_operator(self, chatbot_script_step=None, users=None):
        operator_before = self.livechat_operator_id
        posted_message = super()._forward_human_operator(chatbot_script_step=chatbot_script_step, users=users)
        if self.livechat_operator_id != operator_before:
            # Le chatbot passe la main à un opérateur : s'il n'est pas en
            # ligne, le visiteur en est averti tout de suite.
            # sudo: discuss.channel - le visiteur déclenche le transfert.
            self.sudo()._aite_post_away_message()
        return posted_message

    def _aite_after_livechat_message(self, message):
        """ Réagit à un message de la conversation (appelé en sudo). """
        self.ensure_one()
        if message.message_type != 'comment':
            return
        if self._aite_is_visitor_message(message):
            if self.aite_visitor_left_dt:
                # Il écrit de nouveau dans cette conversation : il y est revenu.
                self.aite_visitor_left_dt = False
            self._aite_detect_visitor_contact(message)
            self._aite_cancel_pending_email()
            self._aite_post_away_message()
        elif self._aite_is_operator_message(message):
            self._aite_email_operator_reply(message)

    def _aite_is_visitor_message(self, message):
        customers = self.livechat_customer_history_ids
        if message.author_guest_id:
            return message.author_guest_id in customers.guest_id
        return bool(message.author_id) and message.author_id in customers.partner_id

    def _aite_is_operator_message(self, message):
        """ Message écrit par un opérateur : utilisateur interne, pas le chatbot. """
        author = message.author_id
        return bool(
            author
            and author in self.livechat_agent_history_ids.partner_id
            and any(user._is_internal() for user in author.user_ids)
        )

    def _aite_human_operator(self):
        """ Partenaire de l'opérateur humain de la conversation, s'il y en a un
        (vide tant que c'est le chatbot qui répond). """
        operator = self.livechat_operator_id
        if (
            operator
            and operator in self.livechat_agent_history_ids.partner_id
            and any(user._is_internal() for user in operator.user_ids)
        ):
            return operator
        return self.env['res.partner']

    def _aite_visitor_lang(self):
        return self.livechat_lang_id.code or self.env.context.get('lang')

    # ------------------------------------------------------------------
    # Conversation en attente de réponse : jamais close trop tôt
    # ------------------------------------------------------------------

    def _aite_last_comments(self):
        """ Dernier message du visiteur et dernière réponse d'un opérateur
        humain (appelé en sudo). """
        self.ensure_one()
        Message = self.env['mail.message'].sudo()
        domain = Domain([
            ('model', '=', 'discuss.channel'),
            ('res_id', '=', self.id),
            ('message_type', '=', 'comment'),
        ])
        customers = self.livechat_customer_history_ids
        last_visitor_message = Message.search(domain & (
            Domain('author_guest_id', 'in', customers.guest_id.ids)
            | Domain('author_id', 'in', customers.partner_id.ids)
        ), order='id desc', limit=1)
        operators = self.livechat_agent_history_ids.partner_id.filtered(
            lambda partner: any(user._is_internal() for user in partner.user_ids))
        last_operator_message = Message.search(
            domain & Domain('author_id', 'in', operators.ids), order='id desc', limit=1)
        return last_visitor_message, last_operator_message

    def _aite_is_waiting_for_operator(self):
        """ Le dernier message du visiteur n'a pas encore de réponse d'un
        opérateur humain, dans un canal toujours joignable. """
        self.ensure_one()
        if self.livechat_end_dt or not self.livechat_channel_id.aite_always_available:
            return False
        if not self._aite_human_operator():
            return False
        last_visitor_message, last_operator_message = self._aite_last_comments()
        return bool(last_visitor_message) and last_operator_message.id < last_visitor_message.id

    def _aite_has_reply_unseen_by_visitor(self):
        """ Un opérateur a répondu, le visiteur (toujours là, il n'a pas fermé
        le chat) n'a pas encore vu la réponse : il peut revenir la lire. """
        self.ensure_one()
        if self.livechat_end_dt or self.aite_visitor_left_dt or not self.livechat_channel_id.aite_always_available:
            return False
        last_visitor_message, last_operator_message = self._aite_last_comments()
        if not last_operator_message or last_operator_message.id < last_visitor_message.id:
            return False
        visitors = self.channel_member_ids.filtered(lambda member: member.livechat_member_type == 'visitor')
        return any(member.seen_message_id.id < last_operator_message.id for member in visitors)

    @api.model
    def _aite_sessions_kept_open(self):
        """ Conversations que le nettoyage quotidien d'Odoo ne doit pas clore
        (au plus 7 jours après leur dernier message). """
        # sudo: discuss.channel - tâche planifiée de nettoyage.
        sessions = self.sudo().search([
            ('channel_type', '=', 'livechat'),
            ('livechat_end_dt', '=', False),
            ('livechat_channel_id.aite_always_available', '=', True),
            ('last_interest_dt', '>=', fields.Datetime.now() - SESSION_KEEP_OPEN_DELAY),
        ])
        return sessions.filtered(
            lambda session: session._aite_is_waiting_for_operator() or session._aite_has_reply_unseen_by_visitor()
        )

    def _close_livechat_session(self, **kwargs):
        # Le visiteur ferme le chat avant toute réponse, dans un canal toujours
        # joignable : la conversation reste ouverte, pour que l'opérateur
        # puisse encore répondre (la réponse part par e-mail). Odoo la
        # clôturerait, sans plus de saisie possible pour l'opérateur.
        self.ensure_one()
        if not kwargs.get('cancel') and self.sudo()._aite_is_waiting_for_operator():
            if not self.sudo().aite_visitor_left_dt:
                self._aite_visitor_left(**kwargs)
            return
        return super()._close_livechat_session(**kwargs)

    def _aite_visitor_left(self, **kwargs):
        self.ensure_one()
        member = self.channel_member_ids.filtered(lambda m: m.is_self)
        if member:
            # sudo: discuss.channel.rtc.session - comme le natif, le visiteur
            # quitte l'appel en cours.
            member.sudo()._rtc_leave_call()
        # sudo: discuss.channel - le visiteur ferme le chat.
        channel_sudo = self.sudo()
        channel_sudo.aite_visitor_left_dt = fields.Datetime.now()
        if channel_sudo.livechat_channel_id.aite_email_reply and channel_sudo.aite_visitor_email:
            hint = self.env._("Il a fermé le chat avant votre réponse : elle lui sera envoyée par e-mail.")
        else:
            hint = self.env._(
                "Il a fermé le chat avant votre réponse, sans laisser d'adresse e-mail : "
                "il ne la verra pas.")
        # sudo: mail.message - comme le natif, avis de départ du visiteur.
        channel_sudo.message_post(
            body=Markup('<div class="o_mail_notification o_hide_author">%s %s</div>') % (
                self._get_visitor_leave_message(**kwargs), hint),
            message_type='notification',
            subtype_xmlid='mail.mt_comment',
        )

    # ------------------------------------------------------------------
    # Message d'absence
    # ------------------------------------------------------------------

    def _aite_post_away_message(self):
        """ Au premier message du visiteur qui parvient à un opérateur humain :
        réponse automatique si cet opérateur n'est pas en ligne. Une seule
        vérification par conversation (appelé en sudo). """
        self.ensure_one()
        if self.aite_away_checked or self.livechat_end_dt:
            return self.env['mail.message']
        operator = self._aite_human_operator()
        if not operator:
            return self.env['mail.message']
        self.aite_away_checked = True
        livechat_channel = self.livechat_channel_id
        # « En ligne » : connecté et sans statut manuel « Absent » ou « Ne pas
        # déranger ».
        if not livechat_channel.aite_always_available or operator.im_status == 'online':
            return self.env['mail.message']
        text = (livechat_channel.with_context(lang=self._aite_visitor_lang()).aite_away_message or '').strip()
        if (self.aite_visitor_email or self.aite_visitor_phone) and text.endswith(AWAY_CONTACT_REQUEST):
            # Le visiteur a déjà donné son e-mail ou son téléphone (dans ce
            # message ou par son compte) : on ne le lui redemande pas.
            text = text.removesuffix(AWAY_CONTACT_REQUEST).strip()
        if not text:
            return self.env['mail.message']
        # Signé de l'opérateur, comme le message d'accueil natif : le visiteur
        # voit une réponse de la personne qui le recontactera. Type
        # « auto_comment » (message automatique) : personne n'est notifié,
        # l'opérateur ne reçoit donc pas de push pour un message qu'il n'a pas
        # écrit.
        away_message = self.with_context(aite_livechat_auto_reply=True).message_post(
            author_id=operator.id,
            body=plaintext2html(text),
            message_type='auto_comment',
            subtype_xmlid='mail.mt_comment',
        )
        # Renvoyé aussi dans la réponse à l'envoi du message du visiteur : la
        # fenêtre du chat l'ajoute aussitôt à la conversation
        # (static/src/embed/common/thread_model_patch.js), même quand la
        # connexion en temps réel (websocket) ne passe pas.
        if store := self.env.context.get('message_post_store'):
            store.add(away_message)
        return away_message

    # ------------------------------------------------------------------
    # Coordonnées du visiteur
    # ------------------------------------------------------------------

    @api.model
    def _aite_find_emails(self, text):
        text = (text or '')[:CONTACT_SCAN_MAX_CHARS]
        emails = (email_normalize(match) for match in EMAIL_IN_TEXT_RE.findall(text))
        return list(dict.fromkeys(email for email in emails if email))

    @api.model
    def _aite_find_phones(self, text):
        text = (text or '')[:CONTACT_SCAN_MAX_CHARS]
        phones = []
        for match in PHONE_IN_TEXT_RE.findall(EMAIL_IN_TEXT_RE.sub(' ', text)):
            digits = re.sub(r'\D', '', match)
            if PHONE_MIN_DIGITS <= len(digits) <= PHONE_MAX_DIGITS:
                phones.append(re.sub(r'\s+', ' ', match.strip()))
        return phones

    @api.model
    def _aite_is_own_address(self, email):
        """ Adresse de l'entreprise elle-même (société, utilisateurs internes,
        domaine de ses alias e-mail ou de ses sites) : le visiteur peut la
        citer (« j'ai déjà écrit à contact@… »), ce n'est jamais la sienne. """
        # sudo: res.company, res.users, mail.alias.domain, website - simple
        # comparaison d'adresses, appelée pour le message d'un visiteur.
        companies = self.env['res.company'].sudo().search([])
        users = self.env['res.users'].sudo().with_context(active_test=False).search([('share', '=', False)])
        if email in set(companies.partner_id.mapped('email_normalized') + users.mapped('email_normalized')):
            return True
        domains = set(self.env['mail.alias.domain'].sudo().search([]).mapped('name'))
        for website in self.env['website'].sudo().search([('domain', '!=', False)]):
            host = urlsplit(website.domain if '//' in website.domain else f'//{website.domain}').hostname or ''
            domains.add(host.removeprefix('www.'))
        email_domain = email.rpartition('@')[2]
        return any(
            domain and (email_domain == domain.lower() or email_domain.endswith(f'.{domain.lower()}'))
            for domain in domains
        )

    @api.model
    def _aite_count_words(self, text):
        return sum(1 for word in text.split() if re.search(r'\w', word))

    def _aite_known_visitor_email(self):
        """ Adresse déjà connue du visiteur : celle de son compte quand il est
        connecté, ou celle de sa fiche visiteur du site. """
        for partner in self.livechat_customer_history_ids.partner_id:
            if partner.email_normalized:
                return partner.email_normalized
        return email_normalize(self.livechat_visitor_id.email or '') or False

    def _aite_detect_visitor_contact(self, message):
        """ Relève l'e-mail et le téléphone que le visiteur écrit lui-même.

        E-mail : la première adresse donnée est gardée ; une adresse citée
        ensuite au fil d'une phrase (un collègue, un comptable…) ne la
        remplace pas, seul un message qui ne contient guère que la nouvelle
        adresse la corrige. Les adresses de l'entreprise sont ignorées. """
        text = html2plaintext(message.body or '', include_references=False)[:CONTACT_SCAN_MAX_CHARS]
        values = {}
        emails = [email for email in self._aite_find_emails(text) if not self._aite_is_own_address(email)]
        if emails and not self.aite_visitor_email:
            values['aite_visitor_email'] = emails[0]
        elif len(emails) == 1 and self._aite_count_words(EMAIL_IN_TEXT_RE.sub(' ', text)) <= EMAIL_CORRECTION_MAX_WORDS:
            values['aite_visitor_email'] = emails[0]
        elif not self.aite_visitor_email:
            values['aite_visitor_email'] = self._aite_known_visitor_email()
        if phones := self._aite_find_phones(text):
            values['aite_visitor_phone'] = phones[-1]
        values = {name: value for name, value in values.items() if (self[name] or False) != (value or False)}
        if values:
            self.write(values)

    # ------------------------------------------------------------------
    # Réponse par e-mail
    # ------------------------------------------------------------------

    def _aite_visitor_is_online(self):
        if self.aite_visitor_left_dt:
            # Il a fermé le chat : même encore sur le site, il ne verrait pas
            # la réponse.
            return False
        customers = self.livechat_customer_history_ids
        return any(guest.im_status == 'online' for guest in customers.guest_id) or any(
            partner.im_status == 'online' for partner in customers.partner_id
        )

    def _aite_email_reply_messages(self):
        """ Réponses des opérateurs à reprendre dans l'e-mail en cours. """
        self.ensure_one()
        first_message = self.aite_email_first_message_id
        agents = self.livechat_agent_history_ids.partner_id
        if not first_message or not agents:
            return self.env['mail.message']
        messages = self.env['mail.message'].sudo().search([
            ('model', '=', 'discuss.channel'),
            ('res_id', '=', self.id),
            ('id', '>=', first_message.id),
            ('message_type', '=', 'comment'),
            ('author_id', 'in', agents.ids),
        ], order='id asc')
        return messages.filtered(lambda message: self._aite_is_operator_message(message))

    def _aite_email_reply_body(self):
        """ Texte des réponses, échappé : seul ce que les opérateurs ont écrit,
        sans mise en forme ni contenu HTML. """
        self.ensure_one()
        parts = []
        previous_author = None
        for message in self._aite_email_reply_messages():
            text = html2plaintext(message.body or '', include_references=False).strip()
            attachments = message.attachment_ids
            if not text and not attachments:
                continue
            author = message.author_id
            if author != previous_author:
                parts.append(
                    Markup('<p style="margin:16px 0 4px 0;"><strong>%s</strong></p>')
                    % (author.user_livechat_username or author.name)
                )
                previous_author = author
            if text:
                parts.append(plaintext2html(text, container_tag='div'))
            if attachments:
                parts.append(
                    Markup('<p style="margin:4px 0;font-style:italic;">%s</p>')
                    % self.env._(
                        "Pièce jointe à consulter sur le site : %(names)s",
                        names=", ".join(attachments.mapped('name')),
                    )
                )
        return Markup('').join(parts)

    def _aite_cancel_pending_email(self):
        """ Le visiteur est revenu et a écrit : il a vu les réponses, l'e-mail
        qui ne serait pas encore parti est annulé. """
        mail = self.aite_email_mail_id.exists()
        if mail and mail.state == 'outgoing':
            mail.unlink()
            self.write({
                'aite_email_mail_id': False,
                'aite_email_scheduled_dt': self.aite_email_previous_dt,
            })

    def _aite_email_operator_reply(self, message):
        """ Réponse d'un opérateur pendant l'absence du visiteur : l'envoie
        aussi par e-mail, s'il a donné son adresse (appelé en sudo). """
        if not self.livechat_channel_id.aite_email_reply or not self.aite_visitor_email:
            return
        if self._aite_visitor_is_online():
            return
        template = self.env.ref('aite_website_livechat.mail_template_livechat_email_reply', raise_if_not_found=False)
        if not template:
            return
        # L'e-mail ne doit jamais empêcher l'opérateur d'écrire : en cas
        # d'erreur (modèle d'e-mail modifié et invalide, adresse refusée…),
        # le message est publié et l'erreur reste dans le journal.
        try:
            with self.env.cr.savepoint():
                self._aite_queue_email_reply(template, message)
        except Exception:
            _logger.exception(
                "aite_website_livechat : e-mail de réponse non préparé pour la conversation %s.", self.id)

    def _aite_queue_email_reply(self, template, message):
        self.ensure_one()
        mail = self.aite_email_mail_id.exists()
        if mail and mail.state == 'outgoing':
            # Un e-mail attend son heure d'envoi : la nouvelle réponse y est
            # ajoutée.
            values = self._aite_render_email_reply(template)
            if values:
                mail.write({
                    'subject': values['subject'],
                    'body_html': values['body_html'],
                    'body': values['body_html'],
                })
            return mail
        now = fields.Datetime.now()
        scheduled_dt = now + EMAIL_GROUPING_DELAY
        if self.aite_email_scheduled_dt:
            scheduled_dt = max(scheduled_dt, self.aite_email_scheduled_dt + EMAIL_MIN_INTERVAL)
        self.aite_email_first_message_id = message
        values = self._aite_render_email_reply(template)
        if not values:
            return self.env['mail.mail']
        mail = self.env['mail.mail'].sudo().create({
            **values,
            'body': values['body_html'],
            'email_to': self.aite_visitor_email,
            'recipient_ids': [],
            'auto_delete': True,
            'scheduled_date': scheduled_dt,
            # Hors de la conversation : l'e-mail n'apparaît ni dans Discuss
            # ni dans la fenêtre du visiteur.
            'model': False,
            'res_id': False,
        })
        self.write({
            'aite_email_mail_id': mail.id,
            'aite_email_previous_dt': self.aite_email_scheduled_dt,
            'aite_email_scheduled_dt': scheduled_dt,
        })
        # La file d'envoi ne tourne que toutes les heures : on la réveille à
        # l'heure prévue.
        self.env.ref('mail.ir_cron_mail_scheduler_action')._trigger(scheduled_dt)
        return mail

    def _aite_render_email_reply(self, template):
        """ Sujet, corps et expéditeur de l'e-mail, rendus par le modèle
        d'e-mail (modifiable dans Paramètres → Technique → E-mail → Modèles
        d'e-mail). """
        self.ensure_one()
        email_to = email_normalize(self.aite_visitor_email or '')
        if not email_to:
            return {}
        self.invalidate_recordset(['aite_email_reply_html'])
        if not self.aite_email_reply_html:
            return {}
        rendered = template.sudo()._generate_template(
            self.ids, ('subject', 'body_html', 'email_from', 'reply_to', 'mail_server_id'),
        )[self.id]
        company = self.aite_email_website_id.company_id or self.env.company
        email_from = (
            rendered.get('email_from') or company.email_formatted or company.catchall_formatted
        )
        if not email_from:
            _logger.warning(
                "aite_website_livechat : pas d'adresse d'expéditeur (e-mail de la société %s) : "
                "réponse par e-mail non envoyée pour la conversation %s.", company.name, self.id)
            return {}
        return {
            'subject': rendered.get('subject') or self.env._("Réponse à votre message"),
            'body_html': rendered.get('body_html') or '',
            'email_from': email_from,
            'reply_to': rendered.get('reply_to') or email_from,
            'mail_server_id': rendered.get('mail_server_id') or False,
        }
