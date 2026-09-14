# -*- coding: utf-8 -*-
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    aite_roomcharge_product_id = fields.Many2one(
        'product.product', string="Article de report POS",
        help="Article utilisé pour la ligne de folio « Consommation "
             "POS » (le folio exige un article).",
    )


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    aite_roomcharge_product_id = fields.Many2one(
        related='company_id.aite_roomcharge_product_id', readonly=False)
