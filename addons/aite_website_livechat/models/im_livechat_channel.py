# -*- coding: utf-8 -*-
from odoo import fields, models
from odoo.tools.sql import column_exists, create_column

DEFAULT_AWAY_MESSAGE = (
    "Merci pour votre message ! Nous ne sommes pas en ligne pour le moment : "
    "nous vous répondons ici dès que possible. Pour être sûr de recevoir notre "
    "réponse, indiquez-nous votre adresse e-mail ou votre numéro de téléphone."
)


class ImLivechatChannel(models.Model):
    _inherit = 'im_livechat.channel'

    aite_always_available = fields.Boolean(
        string="Toujours joignable",
        default=True,
        help="La bulle du chat reste affichée sur le site même quand aucun "
             "opérateur n'est en ligne. La conversation est alors confiée à "
             "un opérateur du canal, qui la reçoit dans Discuss et en "
             "notification push.",
    )
    aite_away_message = fields.Text(
        string="Message d'absence",
        translate=True,
        default=lambda self: DEFAULT_AWAY_MESSAGE,
        help="Réponse automatique au premier message du visiteur quand "
             "l'opérateur n'est pas en ligne (une fois par conversation). "
             "Vide : pas de message d'absence.",
    )
    aite_email_reply = fields.Boolean(
        string="Réponse par e-mail",
        default=True,
        help="Quand le visiteur a quitté le site, les réponses des opérateurs "
             "lui sont aussi envoyées par e-mail, s'il a donné son adresse "
             "(au plus un e-mail toutes les 10 minutes par conversation).",
    )

    def _auto_init(self):
        # Les canaux qui existent avant l'installation gardent le comportement
        # natif : leurs cases restent décochées. Sans cela, l'ORM remplirait
        # les nouvelles colonnes avec la valeur par défaut (cochée), qui ne
        # vaut que pour les canaux créés ensuite.
        for column in ('aite_always_available', 'aite_email_reply'):
            if not column_exists(self.env.cr, self._table, column):
                create_column(self.env.cr, self._table, column, 'boolean')
        return super()._auto_init()

    def write(self, vals):
        result = super().write(vals)
        if {'aite_always_available', 'user_ids'} & set(vals):
            # Les pages servies aux visiteurs anonymes sont gardées en cache
            # une heure, avec la décision de charger le chat : un réglage
            # changé doit se voir tout de suite.
            self.env.registry.clear_cache('templates')
        return result

    # ------------------------------------------------------------------
    # Toujours joignable
    # ------------------------------------------------------------------

    def _aite_reachable_operators(self):
        """ Opérateurs du canal à qui confier une conversation quand personne
        n'est en ligne : les utilisateurs internes actifs, connectés ou non. """
        self.ensure_one()
        return self.user_ids.filtered(lambda user: user.active and user._is_internal())

    def _aite_is_always_reachable(self):
        self.ensure_one()
        return bool(self.aite_always_available and self._aite_reachable_operators())

    def _aite_is_untouched_default(self):
        """ Canal de démonstration créé par Odoo (« YourWebsite.com »), jamais
        utilisé : aucun opérateur capable de répondre (seul l'utilisateur
        système, archivé), aucune règle, aucune conversation. """
        self.ensure_one()
        default = self.env.ref('im_livechat.im_livechat_channel_data', raise_if_not_found=False)
        return bool(
            self == default
            and not self.rule_ids
            and not self.with_context(active_test=False).channel_ids
            and not self._aite_reachable_operators()
        )

    def _is_livechat_available(self):
        # Natif : un chatbot ou un opérateur « en ligne ». En plus : un canal
        # toujours joignable qui a au moins un opérateur.
        return super()._is_livechat_available() or self._aite_is_always_reachable()

    def _get_operator(self, previous_operator_id=None, lang=None, country_id=None,
                      expertises=None, users=None):
        operator = super()._get_operator(
            previous_operator_id=previous_operator_id,
            lang=lang,
            country_id=country_id,
            expertises=expertises,
            users=users,
        )
        # Un opérateur en ligne a été trouvé : choix natif inchangé. Quand
        # l'appelant fournit lui-même les candidats (users), on respecte sa
        # liste : il compte retrouver l'opérateur choisi parmi eux (c'est le
        # cas du transfert vers un commercial de crm_livechat).
        if operator or users is not None or not self.aite_always_available:
            return operator
        candidates = self._aite_reachable_operators()
        if not candidates:
            return operator
        # Personne en ligne : même logique de choix que le natif (opérateur
        # précédent du visiteur, langue, pays, compétences, le moins occupé),
        # mais parmi tous les opérateurs du canal.
        return super()._get_operator(
            previous_operator_id=previous_operator_id,
            lang=lang,
            country_id=country_id,
            expertises=expertises,
            users=candidates,
        )
