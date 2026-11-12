# -*- coding: utf-8 -*-
from odoo import fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    aite_crm_digest_subscribed = fields.Boolean(
        string="Récapitulatif CRM du matin",
        default=True,
        help="Recevoir chaque matin par e-mail la liste de ses activités en "
             "cours sur les opportunités (en retard, du jour et à venir).",
    )

    # Journée (dans le fuseau de l'utilisateur) du dernier récapitulatif
    # mis en file : la tâche planifiée peut être relancée par Odoo après
    # une interruption, sans renvoyer deux fois le même e-mail.
    aite_crm_digest_last_sent = fields.Date(
        string="Dernier récapitulatif CRM", readonly=True, copy=False)

    # Chacun peut s'abonner ou se désabonner depuis ses préférences.
    @property
    def SELF_READABLE_FIELDS(self):
        return super().SELF_READABLE_FIELDS + ['aite_crm_digest_subscribed']

    @property
    def SELF_WRITEABLE_FIELDS(self):
        return super().SELF_WRITEABLE_FIELDS + ['aite_crm_digest_subscribed']
