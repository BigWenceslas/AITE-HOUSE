# -*- coding: utf-8 -*-
from odoo import fields, models

from .booking_resource import KINDS


class BookingService(models.Model):
    """
    Prestation du catalogue : soin SPA, coupe homme/femme, pressing
    chemise, location d'espace au forfait…

    La durée alimente le calcul automatique de fin de créneau ; l'article
    (obligatoire) permet le report au folio du séjour (le folio exige un
    ``product_id``) et la facturation.
    """
    _name = 'aite.booking.service'
    _description = "Prestation (SPA / coiffure / pressing / espace)"
    _order = 'kind, sequence, name'

    name = fields.Char(string="Prestation", required=True, translate=True)
    kind = fields.Selection(
        selection=KINDS, string="Famille", required=True, default='spa',
        index=True,
    )
    sequence = fields.Integer(string="Séquence", default=10)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company', string="Société", required=True,
        default=lambda self: self.env.company,
    )
    currency_id = fields.Many2one(
        related='company_id.currency_id', readonly=True)

    duration_minutes = fields.Integer(
        string="Durée (min)", default=60,
        help="Durée standard — propose automatiquement l'heure de fin.",
    )
    price = fields.Monetary(
        string="Prix", required=True, currency_field='currency_id',
    )
    product_id = fields.Many2one(
        'product.product', string="Article lié", required=True,
        domain="[('sale_ok', '=', True)]",
        help="Article utilisé pour le report au folio et la facturation.",
    )
    description = fields.Text(string="Description")

    _sql_constraints = [
        ('duration_positive', 'CHECK(duration_minutes > 0)',
         "La durée doit être strictement positive."),
        ('price_positive', 'CHECK(price >= 0)',
         "Le prix ne peut pas être négatif."),
    ]
