# -*- coding: utf-8 -*-
from odoo import api, fields, models


class PosOrderLine(models.Model):
    """
    Extension de la ligne POS pour calculer le coût et la marge.

    Stratégie de stockage
    ---------------------
    - ``cost_unit`` est un champ ``Monetary`` **non-computed**, snappé à la
      création de la ligne via override de ``create()``. Cela fige le coût
      au moment de la vente : la marge historique reste stable même si
      le ``standard_price`` du produit évolue ensuite.
    - ``total_cost``, ``margin`` et ``margin_rate`` sont ``stored=True`` pour
      permettre tri, filtrage, group_by et lecture rapide dans le dashboard.
    """
    _inherit = 'pos.order.line'

    cost_unit = fields.Monetary(
        string="Coût unitaire",
        currency_field='currency_id',
        help="Coût d'achat unitaire snappé au moment de la vente. "
             "Renseigné automatiquement à la création de la ligne à partir "
             "du standard_price du produit. Modifiable manuellement.",
    )
    total_cost = fields.Monetary(
        string="CMV",
        compute='_compute_margin_data',
        store=True,
        currency_field='currency_id',
        help="Coût des marchandises vendues = qté × coût unitaire.",
    )
    margin = fields.Monetary(
        string="Marge brute",
        compute='_compute_margin_data',
        store=True,
        currency_field='currency_id',
        help="Marge brute = sous-total HT − CMV.",
    )
    margin_rate = fields.Float(
        string="Taux de marge (%)",
        compute='_compute_margin_data',
        store=True,
        digits=(5, 2),
        help="Taux de marge sur prix de vente = marge / sous-total HT × 100.",
    )

    @api.depends('qty', 'price_subtotal', 'cost_unit')
    def _compute_margin_data(self):
        for line in self:
            line.total_cost = (line.qty or 0.0) * (line.cost_unit or 0.0)
            line.margin = (line.price_subtotal or 0.0) - line.total_cost
            line.margin_rate = (
                (line.margin / line.price_subtotal * 100.0)
                if line.price_subtotal else 0.0
            )

    @api.model_create_multi
    def create(self, vals_list):
        """Snapshot le coût d'achat au moment de la création de la ligne."""
        Product = self.env['product.product']
        for vals in vals_list:
            # On respecte une valeur explicitement fournie (import, correction
            # manuelle, etc.) et on ne snapshot que si rien n'est passé.
            if 'cost_unit' not in vals and vals.get('product_id'):
                product = Product.browse(vals['product_id'])
                vals['cost_unit'] = product.standard_price or 0.0
        return super().create(vals_list)
