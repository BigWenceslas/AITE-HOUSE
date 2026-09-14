# -*- coding: utf-8 -*-
from odoo import fields, models


class ResCompany(models.Model):
    """
    Paramètres globaux des alertes Achats & Fournisseurs, par société.

    * ``due_soon_days``    — les factures dues sous ce délai passent en
      « À payer bientôt » (échéancier / trésorerie).
    * ``late_days``        — tolérance de retard de livraison avant badge
      « En retard » (l'OTIF, lui, reste strict).
    * ``dependency_pct``   — au-delà de cette part des achats chez un seul
      fournisseur, badge « Dépendance » (risque de concentration).
    * ``price_increase_pct`` — hausse de prix d'achat au-delà de laquelle
      la référence est badgée « Hausse forte ».
    """
    _inherit = 'res.company'

    aite_purchase_due_soon_days = fields.Integer(
        string="Alerte échéance (jours avant)", default=7,
        help="Fenêtre d'alerte : factures fournisseurs dues sous ce délai.",
    )
    aite_purchase_late_days = fields.Integer(
        string="Tolérance retard livraison (jours)", default=2,
        help="Au-delà, la commande est signalée en retard de livraison.",
    )
    aite_purchase_dependency_pct = fields.Float(
        string="Seuil de dépendance fournisseur (%)", default=40.0,
        digits=(5, 1),
        help="Part des achats chez un fournisseur au-delà de laquelle le "
             "risque de concentration est signalé.",
    )
    aite_purchase_price_increase_pct = fields.Float(
        string="Seuil de hausse de prix (%)", default=5.0, digits=(5, 1),
        help="Variation de prix d'achat au-delà de laquelle une référence "
             "est signalée en hausse forte.",
    )


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    aite_purchase_due_soon_days = fields.Integer(
        related='company_id.aite_purchase_due_soon_days', readonly=False)
    aite_purchase_late_days = fields.Integer(
        related='company_id.aite_purchase_late_days', readonly=False)
    aite_purchase_dependency_pct = fields.Float(
        related='company_id.aite_purchase_dependency_pct', readonly=False)
    aite_purchase_price_increase_pct = fields.Float(
        related='company_id.aite_purchase_price_increase_pct', readonly=False)
