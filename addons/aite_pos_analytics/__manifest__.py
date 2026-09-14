# -*- coding: utf-8 -*-
{
    'name': "AITE — POS Analytics (LAVERANDAH)",
    'summary': "Tableau de bord analytique avancé pour le Point de Vente "
               "— CA, Marge, CMV, écarts de caisse, analyses produits & catégories",
    'description': """
AITE POS Analytics
==================

Module d'analyse avancée pour Odoo Point of Sale, destiné aux clients en
contexte commerce de détail (bar, cave, restauration, alimentation générale).

Fonctionnalités principales
---------------------------
* Calcul de marge brute, CMV (Coût des Marchandises Vendues) et taux de marge
  au niveau de chaque ligne de commande POS, avec snapshot du coût à la vente.
* Agrégation performante (champs stored) sur sessions, commandes et catégories.
* Modèle SQL ``aite.pos.daily.report`` pour analyses temporelles (pivot / graph).
* Détection automatique des écarts de caisse avec classification de sévérité.
* Dashboard OWL custom (livré en Sprint 2).

Compatible Odoo 18 Enterprise.
""",
    'author': "AITE CONSULTING",
    'website': "https://aiteconsulting.com",
    'category': 'Point of Sale',
    'version': '18.0.2.1.0',
    'license': 'LGPL-3',

    'depends': [
        'base',
        'product',
        'point_of_sale',
        'account',
    ],

    'data': [
        'security/pos_analytics_security.xml',
        'security/ir.model.access.csv',
        'views/pos_order_views.xml',
        'views/pos_session_views.xml',
        'views/pos_analytics_report_views.xml',
        'views/pos_dashboard_actions.xml',
        'views/pos_analytics_menus.xml',
    ],

    'assets': {
        'web.assets_backend': [
            # Styles
            'aite_pos_analytics/static/src/scss/pos_dashboard.scss',
            # Services (utils + chargement Chart.js)
            'aite_pos_analytics/static/src/js/services/utils.js',
            'aite_pos_analytics/static/src/js/services/chartjs_loader.js',
            # Composants partagés
            'aite_pos_analytics/static/src/js/components/kpi_card.js',
            'aite_pos_analytics/static/src/js/components/rank_row.js',
            'aite_pos_analytics/static/src/js/components/filter_bar.js',
            'aite_pos_analytics/static/src/js/components/tab_bar.js',
            'aite_pos_analytics/static/src/js/components/product_panel.js',
            # Vues (9)
            'aite_pos_analytics/static/src/js/views/dashboard_view.js',
            'aite_pos_analytics/static/src/js/views/caisse_view.js',
            'aite_pos_analytics/static/src/js/views/sessions_view.js',
            'aite_pos_analytics/static/src/js/views/products_view.js',
            'aite_pos_analytics/static/src/js/views/margins_view.js',
            'aite_pos_analytics/static/src/js/views/categories_view.js',
            'aite_pos_analytics/static/src/js/views/discrepancies_view.js',
            'aite_pos_analytics/static/src/js/views/payments_view.js',
            'aite_pos_analytics/static/src/js/views/config_view.js',
            # Racine (dépend de tous les précédents)
            'aite_pos_analytics/static/src/js/dashboard.js',
            # Templates OWL
            'aite_pos_analytics/static/src/xml/dashboard_shell.xml',
            'aite_pos_analytics/static/src/xml/views.xml',
        ],
    },

    'post_init_hook': '_init_pos_margin_data',

    'installable': True,
    'application': False,
    'auto_install': False,
}
