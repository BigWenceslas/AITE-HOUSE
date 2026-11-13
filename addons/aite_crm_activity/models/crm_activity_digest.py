# -*- coding: utf-8 -*-
import logging
from collections import defaultdict
from datetime import timedelta
from urllib.parse import urlencode

import pytz

from odoo import api, fields, models, tools

from .crm_activity_params import actionable_activity_domain, get_thresholds, severity

_logger = logging.getLogger(__name__)

PARAM_UPCOMING_DAYS = 'aite_crm_activity.digest_upcoming_days'
DEFAULT_UPCOMING_DAYS = 3
PARAM_TZ = 'aite_crm_activity.digest_tz'
DEFAULT_TZ = 'Africa/Douala'
MAX_ROWS_PER_SECTION = 50


class AiteCrmActivityDigest(models.AbstractModel):
    """ Récapitulatif quotidien : chaque utilisateur reçoit, le matin, la
    liste de ses activités en cours sur les pistes et opportunités — en
    retard, du jour et à venir. """
    _name = 'aite.crm.activity.digest'
    _description = "Récapitulatif quotidien des activités CRM"

    # ------------------------------------------------------------------
    # Destinataires
    # ------------------------------------------------------------------

    @api.model
    def _get_upcoming_days(self):
        value = self.env['ir.config_parameter'].sudo().get_param(PARAM_UPCOMING_DAYS)
        try:
            return max(0, int(value)) if value not in (None, False, '') else DEFAULT_UPCOMING_DAYS
        except ValueError:
            return DEFAULT_UPCOMING_DAYS

    @api.model
    def _user_today(self, user, now=None):
        """ Date du jour dans le fuseau horaire de l'utilisateur. """
        return fields.Date.context_today(self.with_context(tz=user.tz or 'UTC'), timestamp=now)

    @api.model
    def _get_tz_name(self):
        """ Fuseau horaire de l'heure d'envoi (Paramètres du CRM). """
        value = self.env['ir.config_parameter'].sudo().get_param(PARAM_TZ)
        return value if value in pytz.all_timezones_set else DEFAULT_TZ

    @api.model
    def _get_recipients(self):
        """ Utilisateurs internes actifs, abonnés, ayant une adresse e-mail et
        au moins une activité ouverte sur une piste ou opportunité dont
        l'échéance tombe dans la fenêtre du récapitulatif, et qui n'ont pas
        encore reçu celui de leur journée (date de leur propre fuseau
        horaire). La fenêtre est élargie d'un jour pour couvrir les fuseaux
        horaires ; chaque utilisateur est ensuite filtré selon sa propre
        date du jour.

        Une personne sans droits sur le CRM à qui une activité a été
        confiée sur une opportunité reçoit aussi le récapitulatif (Odoo lui
        montre ces activités) ; l'e-mail ne lui propose alors pas le
        tableau de bord.

        Les activités restées ouvertes sur une opportunité perdue (archivée)
        ne comptent pas : personne ne les traitera, elles ne justifient
        donc pas un e-mail. """
        horizon = fields.Date.today() + timedelta(days=self._get_upcoming_days() + 1)
        groups = self.env['mail.activity'].sudo()._read_group(
            [('res_model', '=', 'crm.lead'), ('date_deadline', '<=', horizon),
             ('user_id', '!=', False)] + actionable_activity_domain(self.env),
            ['user_id'],
        )
        users = self.env['res.users'].sudo().union(*(user for (user,) in groups))
        return users.filtered(
            lambda u: u.active and not u.share and u.email and u.aite_crm_digest_subscribed
            and u.aite_crm_digest_last_sent != self._user_today(u)
        )

    # ------------------------------------------------------------------
    # Contenu
    # ------------------------------------------------------------------

    @api.model
    def _get_user_digest(self, user, now=None):
        """ Activités de l'utilisateur, lues avec ses propres droits, dans
        son fuseau horaire et sa langue. Renvoie None s'il n'a rien.

        Les activités restées ouvertes sur une opportunité perdue (archivée)
        n'y figurent pas : elles ne sont plus à faire.

        :param now: instant de référence (datetime UTC naïf), pour les tests
        """
        env = self.with_user(user).with_context(
            lang=user.lang or self.env.lang or 'en_US', tz=user.tz or 'UTC').env
        today = self._user_today(user, now=now)
        horizon = today + timedelta(days=self._get_upcoming_days())
        activities = env['mail.activity'].search([
            ('res_model', '=', 'crm.lead'),
            ('user_id', '=', user.id),
            ('date_deadline', '<=', horizon),
        ] + actionable_activity_domain(env), order='date_deadline asc, id asc')
        if not activities:
            return None

        leads = env['crm.lead'].browse(activities.mapped('res_id'))
        # Droit de lecture vérifié sur l'opportunité, libellés lus en sudo
        # (comme dans le tableau de bord).
        readable = {lead.id: lead for lead in leads._filtered_access('read').sudo()}
        base_url = self.get_base_url()
        # Gravité du retard : mêmes seuils que le tableau de bord (Paramètres).
        thresholds = get_thresholds(env)

        # Tri par échéance croissante : la section « En retard » commence par
        # le retard le plus ancien.
        sections = {'overdue': [], 'today': [], 'upcoming': []}
        overdue_lead_ids = set()
        for activity in activities:
            deadline = activity.date_deadline
            key = 'overdue' if deadline < today else 'today' if deadline == today else 'upcoming'
            late_days = (today - deadline).days if key == 'overdue' else 0
            if key == 'overdue':
                overdue_lead_ids.add(activity.res_id)
            lead = readable.get(activity.res_id)
            sections[key].append({
                'type': activity.activity_type_id.name or '',
                'summary': activity.summary or '',
                'deadline': tools.format_date(env, deadline),
                'late_days': late_days,
                'severity': severity(late_days, thresholds),
                'lead_name': (lead.name if lead else activity.res_name) or '',
                'partner': (lead.partner_id.display_name if lead else '') or '',
                'stage': (lead.stage_id.name if lead else '') or '',
                'revenue': tools.format_amount(env, lead.expected_revenue, lead.company_currency)
                           if lead and lead.expected_revenue else '',
                # Lien seulement vers une opportunité que l'utilisateur peut
                # ouvrir (sinon Odoo le renverrait vers Discussion).
                'url': '%s/mail/view?%s' % (base_url, urlencode({
                    'model': 'crm.lead', 'res_id': activity.res_id})) if lead else False,
            })
        # Comptages et montant sur toutes les activités, avant la limite
        # d'affichage de chaque section.
        counts = {key: len(rows) for key, rows in sections.items()}
        critical_count = sum(1 for row in sections['overdue'] if row['severity'] == 'critical')
        overdue_amounts = self._get_overdue_amounts(env, user, readable, overdue_lead_ids)
        for key in sections:
            sections[key] = sections[key][:MAX_ROWS_PER_SECTION]
        # Le tableau de bord est réservé aux utilisateurs du CRM. Avec des
        # activités en retard, le bouton ouvre directement la liste « En
        # retard » (action client au chemin « activites-en-retard »).
        can_open_dashboard = user.has_group('sales_team.group_sale_salesman')
        path = 'activites-en-retard' if counts['overdue'] and can_open_dashboard else 'suivi-activites'
        return {
            'lang_env': env,
            'user': user,
            'company': user.company_id,
            'today': tools.format_date(env, today, date_format='EEEE d MMMM y'),
            'sections': sections,
            'counts': counts,
            'total': sum(counts.values()),
            'critical_count': critical_count,
            'critical_label': self._critical_label(env, critical_count) if critical_count else '',
            'overdue_amounts': overdue_amounts,
            'upcoming_days': self._get_upcoming_days(),
            'max_rows': MAX_ROWS_PER_SECTION,
            'dashboard_url': '%s/odoo/%s' % (base_url, path),
            'can_open_dashboard': can_open_dashboard,
        }

    @api.model
    def _get_overdue_amounts(self, env, user, readable, lead_ids):
        """ Montant en jeu : somme du revenu attendu des opportunités derrière
        les activités en retard, par devise de leur société.

        Chaque opportunité ne compte qu'une fois, même avec plusieurs
        activités en retard ; seules comptent celles que l'utilisateur peut
        lire (une activité confiée sur l'opportunité d'un collègue n'en
        dévoile pas le montant). Les devises à zéro sont omises ; la devise
        de la société de l'utilisateur vient en premier.

        :param readable: {id: opportunité lisible par l'utilisateur (en sudo)}
        :param lead_ids: ids des opportunités ayant une activité en retard
        :return: [{'currency_id', 'amount', 'label'}], ``label`` mis en forme
                 par ``tools.format_amount`` dans la langue de l'utilisateur
        """
        totals = defaultdict(float)
        for lead_id in lead_ids:
            lead = readable.get(lead_id)
            if lead and lead.expected_revenue:
                totals[lead.company_currency] += lead.expected_revenue
        main_currency = user.company_id.currency_id
        return [
            {'currency_id': currency.id, 'amount': amount,
             'label': tools.format_amount(env, amount, currency)}
            for currency, amount in sorted(
                totals.items(), key=lambda item: (item[0] != main_currency, item[0].name))
            if not currency.is_zero(amount)
        ]

    @api.model
    def _critical_label(self, env, count):
        """ « 1 critique », « 2 critiques » : accord en nombre. """
        if count > 1:
            return env._("%(count)s critiques", count=count)
        return env._("%(count)s critique", count=count)

    @api.model
    def _prepare_mail_values(self, user, digest):
        env = digest['lang_env']
        values = {key: value for key, value in digest.items() if key != 'lang_env'}
        body = env['ir.qweb']._render('aite_crm_activity.digest_email', values)
        counts = digest['counts']
        if counts['overdue'] and digest['critical_count']:
            # « Vos activités CRM du jour : 5, dont 2 en retard (1 critique) »
            subject = env._(
                "Vos activités CRM du jour : %(total)s, dont %(overdue)s en retard (%(critical)s)",
                total=digest['total'], overdue=counts['overdue'], critical=digest['critical_label'])
        elif counts['overdue']:
            subject = env._(
                "Vos activités CRM du jour : %(total)s, dont %(overdue)s en retard",
                total=digest['total'], overdue=counts['overdue'])
        else:
            subject = env._("Vos activités CRM du jour : %(total)s", total=digest['total'])
        company = user.company_id
        return {
            'subject': subject,
            'body_html': body,
            'email_from': (company.partner_id.email_formatted
                           or self.env.ref('base.user_root').email_formatted),
            'email_to': user.email_formatted,
            'author_id': self.env.ref('base.partner_root').id,
            'auto_delete': True,
            'state': 'outgoing',
            'headers': {'X-Auto-Response-Suppress': 'OOF'},
        }

    @api.model
    def _send_to_user(self, user):
        """ Met en file le récapitulatif d'un utilisateur. Renvoie le
        mail.mail créé, ou un enregistrement vide s'il n'a rien à faire. """
        digest = self._get_user_digest(user)
        if not digest:
            return self.env['mail.mail']
        return self.env['mail.mail'].sudo().create(self._prepare_mail_values(user, digest))

    # ------------------------------------------------------------------
    # Envoi
    # ------------------------------------------------------------------

    @api.model
    def _cron_send_daily_digest(self):
        users = self._get_recipients()
        in_cron = bool(self.env.context.get('ir_cron_progress_id'))
        if in_cron:
            self.env['ir.cron']._commit_progress(remaining=len(users))
        sent = 0
        for user in users:
            try:
                with self.env.cr.savepoint():
                    if self._send_to_user(user):
                        sent += 1
                    # Date de la journée de l'utilisateur : une relance de la
                    # tâche le même jour ne renvoie rien, l'envoi du lendemain
                    # passe même si l'heure d'envoi tombe juste après minuit.
                    user.sudo().aite_crm_digest_last_sent = self._user_today(user)
            except Exception:
                _logger.exception("Récapitulatif CRM : échec pour l'utilisateur %s", user.id)
            if in_cron:
                self.env['ir.cron']._commit_progress(1)
        if sent:
            # Les e-mails partent avec la file d'attente d'Odoo, qui ne passe
            # qu'une fois par heure : on la réveille pour un envoi immédiat.
            queue = self.env.ref('mail.ir_cron_mail_scheduler_action', raise_if_not_found=False)
            if queue:
                queue.sudo()._trigger()
        _logger.info("Récapitulatif CRM : %s e-mail(s) mis en file sur %s destinataire(s).",
                     sent, len(users))
        return sent

    @api.model
    def action_send_my_digest(self):
        """ Bouton des Paramètres : envoie tout de suite son propre
        récapitulatif à l'utilisateur, pour voir à quoi il ressemble — et
        vérifier que l'envoi des e-mails fonctionne. """
        user = self.env.user
        sticky = False
        if not user.email:
            message = self.env._("Renseignez votre adresse e-mail dans vos préférences.")
            kind = 'warning'
        else:
            mail = self._send_to_user(user)
            if not mail:
                message = self.env._("Aucune activité en cours : rien à envoyer pour l'instant.")
                kind = 'info'
            else:
                mail.send(raise_exception=False)
                mail = mail.exists()
                if not mail or mail.state == 'sent':
                    # Envoyé (puis supprimé : auto_delete).
                    message = self.env._("Récapitulatif envoyé à %(email)s.", email=user.email)
                    kind = 'success'
                elif mail.state == 'exception':
                    message = self.env._(
                        "L'envoi à %(email)s a échoué : %(reason)s. Vérifiez le serveur de "
                        "messagerie sortant (Paramètres → Technique → E-mail → Serveurs de "
                        "messagerie sortants).",
                        email=user.email, reason=mail.failure_reason or self.env._("erreur inconnue"))
                    kind = 'danger'
                    sticky = True
                else:
                    message = self.env._(
                        "Récapitulatif mis en file d'attente pour %(email)s.", email=user.email)
                    kind = 'info'
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {'message': message, 'type': kind, 'sticky': sticky},
        }
