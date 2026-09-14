# -*- coding: utf-8 -*-
from odoo import fields, models


class ResCompany(models.Model):
    """
    Barème de fidélité et seuils de segmentation, par société.

    Points : ``rate_per_1000`` points gagnés par tranche de 1 000 de la
    devise, dès que la transaction atteint ``min_amount``.

    Statuts (fenêtre glissante de ``window_months`` mois) :
    * VIP  — dépenses ≥ ``vip_min_spend`` ET visites ≥ ``vip_min_visits``
    * VVIP — dépenses, visites ET diversité de services (familles
      distinctes utilisées) ≥ leurs seuils respectifs.
    """
    _inherit = 'res.company'

    aite_loyalty_rate_per_1000 = fields.Float(
        string="Points par 1 000", default=1.0, digits=(6, 2))
    aite_loyalty_min_amount = fields.Monetary(
        string="Montant minimum par transaction", default=1000.0,
        currency_field='currency_id')
    aite_loyalty_window_months = fields.Integer(
        string="Fenêtre de calcul (mois)", default=12)
    aite_loyalty_vip_min_spend = fields.Monetary(
        string="VIP — dépenses min.", default=500000.0,
        currency_field='currency_id')
    aite_loyalty_vip_min_visits = fields.Integer(
        string="VIP — visites min.", default=10)
    aite_loyalty_vvip_min_spend = fields.Monetary(
        string="VVIP — dépenses min.", default=2000000.0,
        currency_field='currency_id')
    aite_loyalty_vvip_min_visits = fields.Integer(
        string="VVIP — visites min.", default=25)
    aite_loyalty_vvip_min_domains = fields.Integer(
        string="VVIP — familles de services min.", default=3,
        help="Nombre de familles distinctes utilisées (restaurant/"
             "boutique, hébergement, SPA, coiffure, pressing, espaces).")


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    aite_loyalty_rate_per_1000 = fields.Float(
        related='company_id.aite_loyalty_rate_per_1000', readonly=False)
    aite_loyalty_min_amount = fields.Monetary(
        related='company_id.aite_loyalty_min_amount', readonly=False)
    aite_loyalty_window_months = fields.Integer(
        related='company_id.aite_loyalty_window_months', readonly=False)
    aite_loyalty_vip_min_spend = fields.Monetary(
        related='company_id.aite_loyalty_vip_min_spend', readonly=False)
    aite_loyalty_vip_min_visits = fields.Integer(
        related='company_id.aite_loyalty_vip_min_visits', readonly=False)
    aite_loyalty_vvip_min_spend = fields.Monetary(
        related='company_id.aite_loyalty_vvip_min_spend', readonly=False)
    aite_loyalty_vvip_min_visits = fields.Integer(
        related='company_id.aite_loyalty_vvip_min_visits', readonly=False)
    aite_loyalty_vvip_min_domains = fields.Integer(
        related='company_id.aite_loyalty_vvip_min_domains', readonly=False)
