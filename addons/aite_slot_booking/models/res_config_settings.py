# -*- coding: utf-8 -*-
from odoo import fields, models


class ResCompany(models.Model):
    """
    Paramètres du moteur Espaces & Prestations, par société.

    * ``no_show_hours``     — délai de grâce après l'heure de fin au-delà
      duquel une réservation confirmée non honorée passe en no-show
      (cron quotidien, même logique que le PMS).
    * ``auto_post_folio``   — au passage « Réalisée », reporter
      automatiquement la prestation au folio du séjour si un folio ouvert
      unique existe pour le client.
    * ``mail_on_confirm``   — envoyer l'e-mail de confirmation
      automatiquement à la confirmation.
    """
    _inherit = 'res.company'

    aite_slot_no_show_hours = fields.Integer(
        string="No-show après (heures)", default=6,
        help="Délai de grâce après l'heure de fin avant no-show "
             "automatique d'une réservation confirmée.",
    )
    aite_slot_auto_post_folio = fields.Boolean(
        string="Report automatique au folio", default=True,
        help="À la réalisation, porter la prestation sur le folio ouvert "
             "du client (s'il est unique).",
    )
    aite_slot_mail_on_confirm = fields.Boolean(
        # Libellé qualifié : ``aite_hotel_management`` porte un booléen
        # homonyme sur res.company (cf. hotel_send_confirmation).
        string="E-mail de confirmation automatique des réservations d'espaces",
        default=True,
    )


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    aite_slot_no_show_hours = fields.Integer(
        related='company_id.aite_slot_no_show_hours', readonly=False)
    aite_slot_auto_post_folio = fields.Boolean(
        related='company_id.aite_slot_auto_post_folio', readonly=False)
    aite_slot_mail_on_confirm = fields.Boolean(
        related='company_id.aite_slot_mail_on_confirm', readonly=False)
