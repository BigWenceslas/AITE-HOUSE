# -*- coding: utf-8 -*-
from odoo import fields, models


class ProductTemplate(models.Model):
    """
    Réglages d'alerte de réapprovisionnement au niveau de l'article.

    ``product.product`` hérite de ces champs par délégation (_inherits),
    le tableau de bord les lit donc directement sur les variantes.

    * ``aite_lead_days`` — délai de réappro propre à l'article ; 0 = utiliser
      le délai par défaut de la société.
    * ``aite_manual_threshold`` — point de commande fixé à la main ; 0 =
      calcul automatique (ventes/j × (délai + sécurité)).
    * ``aite_alert_active`` — décoché, l'article est ignoré des alertes
      (statut « Ignorée », aucune quantité suggérée).
    """
    _inherit = 'product.template'

    aite_lead_days = fields.Integer(
        string="Délai réappro (jours)", default=0,
        help="Délai moyen entre la commande fournisseur et la réception. "
             "0 = utiliser le délai par défaut de la société.",
    )
    aite_manual_threshold = fields.Float(
        string="Seuil manuel (point de commande)", default=0.0,
        help="Remplace le point de commande calculé. 0 = automatique.",
    )
    aite_alert_active = fields.Boolean(
        string="Alerte de réappro active", default=True,
        help="Décochez pour exclure l'article des alertes de "
             "réapprovisionnement (produit saisonnier, fin de gamme…).",
    )
