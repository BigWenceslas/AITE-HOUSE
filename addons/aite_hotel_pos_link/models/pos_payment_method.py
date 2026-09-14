# -*- coding: utf-8 -*-
from odoo import fields, models


class PosPaymentMethod(models.Model):
    """Marqueur « Note de chambre » sur un moyen de paiement POS."""
    _inherit = 'pos.payment.method'

    is_room_charge = fields.Boolean(
        string="Note de chambre",
        help="Les encaissements sur ce moyen sont reportés au folio du "
             "séjour du client (ou en file d'attente si ambigu).",
    )
