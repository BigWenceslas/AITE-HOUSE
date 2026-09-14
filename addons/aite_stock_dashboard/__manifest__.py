# -*- coding: utf-8 -*-
{
    'name': "AITE — Stock & Inventaire (Tableau de bord)",
    'summary': "Tableau de bord de suivi du stock et des inventaires : "
               "valorisation, couverture, alertes de réapprovisionnement "
               "configurables, rotation & dormants, écarts d'inventaire et "
               "coulage, inventaire complet par emplacement.",
    'description': """
AITE Stock & Inventaire
=======================

Tableau de bord OWL pour Odoo 18 Inventaire, pensé pour le commerce de
détail (bar, cave, restauration) : piloter le stock au lieu de le subir.

Onglets
-------
* **Tableau de bord** — valeur du stock, couverture moyenne, ruptures &
  critiques, coulage de la période vs seuil, rotation, dormants, valeur à
  commander ; graphiques valeur/catégorie, entrées vs sorties, couverture
  par catégorie, top valeur immobilisée.
* **Alertes & réappro** — références triées par urgence (rupture, critique,
  sous seuil) avec point de commande et quantité suggérée.
* **Stock complet** — inventaire de toutes les références, quantités par
  emplacement interne, valeur, couverture, statut ; recherche & filtres.
* **Rotation & dormants** — classes Rapide / Normale / Lente / Dormant,
  valeur immobilisée.
* **Inventaires & écarts** — journal des ajustements d'inventaire et des
  casses (valorisés), coulage mensuel vs seuil.
* **Mouvements** — réceptions, livraisons, transferts, ajustements, casse.

Alertes configurables
---------------------
Paramètres globaux (Réglages) : stock de sécurité, horizon de commande,
seuil critique, seuil dormant, seuil de coulage. Réglages par produit
(fiche article) : délai de réapprovisionnement, seuil manuel, alerte
activée/désactivée. Modification possible directement depuis le tableau de
bord (réservée aux responsables inventaire).

Formules
--------
Point de commande = ventes moy./jour × (délai réappro + sécurité).
Quantité suggérée = ventes moy./jour × (délai + horizon) − stock.
Les ventes moyennes/jour sont calculées sur 30 jours glissants (sorties
vers clients), pour des alertes stables.

Compatible Odoo 18. Dépend uniquement de Stock (pas de POS requis).
""",
    'author': "AITE CONSULTING",
    'website': "https://aiteconsulting.com",
    'category': 'Inventory/Inventory',
    'version': '18.0.1.1.2',
    'license': 'LGPL-3',

    'depends': [
        'base',
        'product',
        'stock',
        'web',
    ],

    'data': [
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'views/product_views.xml',
        'views/stock_dashboard_actions.xml',
        'views/stock_dashboard_menus.xml',
    ],

    'assets': {
        'web.assets_backend': [
            'aite_stock_dashboard/static/src/scss/stock_dashboard.scss',
            'aite_stock_dashboard/static/src/js/services/utils.js',
            'aite_stock_dashboard/static/src/js/services/chartjs_loader.js',
            'aite_stock_dashboard/static/src/js/components/kpi_card.js',
            'aite_stock_dashboard/static/src/js/views/stock_dashboard_view.js',
            'aite_stock_dashboard/static/src/js/dashboard.js',
            'aite_stock_dashboard/static/src/xml/dashboard.xml',
        ],
    },

    'installable': True,
    'application': False,
    'auto_install': False,
}
