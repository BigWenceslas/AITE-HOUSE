# -*- coding: utf-8 -*-
from odoo import api, fields, models


class PosOrder(models.Model):
    """
    Agrégat marge / CMV au niveau de la commande POS.

    Ces champs sont ``stored=True`` pour permettre les analyses pivot/graph
    sans recalculer à chaque lecture. Le ``depends`` sur les lignes garantit
    la propagation automatique lors d'une modification de marge en ligne.
    """
    _inherit = 'pos.order'

    total_cost = fields.Monetary(
        string="CMV total",
        compute='_compute_margin_data',
        store=True,
        currency_field='currency_id',
    )
    total_margin = fields.Monetary(
        string="Marge totale",
        compute='_compute_margin_data',
        store=True,
        currency_field='currency_id',
    )
    margin_rate = fields.Float(
        string="Taux de marge (%)",
        compute='_compute_margin_data',
        store=True,
        digits=(5, 2),
    )

    @api.depends('lines.total_cost', 'lines.margin', 'lines.price_subtotal')
    def _compute_margin_data(self):
        for order in self:
            order.total_cost = sum(order.lines.mapped('total_cost'))
            order.total_margin = sum(order.lines.mapped('margin'))
            subtotal = sum(order.lines.mapped('price_subtotal'))
            order.margin_rate = (
                (order.total_margin / subtotal * 100.0) if subtotal else 0.0
            )
