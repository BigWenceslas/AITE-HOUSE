# -*- coding: utf-8 -*-
from odoo import fields, models


class ResCompany(models.Model):
    """
    Paramètres globaux des alertes de réapprovisionnement, par société.

    Ces valeurs alimentent les formules du tableau de bord Stock :

    * point de commande = ventes moy./jour × (délai réappro + sécurité) ;
    * quantité suggérée = ventes moy./jour × (délai + horizon) − stock ;
    * statut « Critique » si la couverture passe sous ``critical_days`` ;
    * classe « Dormant » si la couverture dépasse ``dormant_days`` ;
    * alerte coulage si les pertes dépassent ``coulage_threshold`` % du CA
      estimé de la période.
    """
    _inherit = 'res.company'

    aite_stock_security_days = fields.Integer(
        string="Stock de sécurité (jours)", default=2,
        help="Jours ajoutés au délai de réapprovisionnement pour calculer "
             "le point de commande.",
    )
    aite_stock_horizon_days = fields.Integer(
        string="Horizon de commande (jours)", default=7,
        help="Couverture visée après livraison ; sert au calcul de la "
             "quantité suggérée.",
    )
    aite_stock_critical_days = fields.Integer(
        string="Seuil critique (jours de couverture)", default=3,
        help="Sous ce nombre de jours de couverture, la référence passe en "
             "statut Critique.",
    )
    aite_stock_dormant_days = fields.Integer(
        string="Seuil dormant (jours de couverture)", default=60,
        help="Au-delà de ce nombre de jours de couverture, la référence est "
             "classée Dormante.",
    )
    aite_stock_default_lead_days = fields.Integer(
        string="Délai de réappro par défaut (jours)", default=3,
        help="Utilisé quand la fiche produit ne précise pas de délai.",
    )
    aite_stock_coulage_threshold = fields.Float(
        string="Seuil de coulage (% du CA)", default=2.0, digits=(5, 1),
        help="Seuil d'alerte des pertes (écarts d'inventaire négatifs + "
             "casse) rapportées au chiffre d'affaires estimé.",
    )


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    aite_stock_security_days = fields.Integer(
        related='company_id.aite_stock_security_days', readonly=False)
    aite_stock_horizon_days = fields.Integer(
        related='company_id.aite_stock_horizon_days', readonly=False)
    aite_stock_critical_days = fields.Integer(
        related='company_id.aite_stock_critical_days', readonly=False)
    aite_stock_dormant_days = fields.Integer(
        related='company_id.aite_stock_dormant_days', readonly=False)
    aite_stock_default_lead_days = fields.Integer(
        related='company_id.aite_stock_default_lead_days', readonly=False)
    aite_stock_coulage_threshold = fields.Float(
        related='company_id.aite_stock_coulage_threshold', readonly=False)
