# -*- coding: utf-8 -*-
{
    'name': "AITE — Direction (vue consolidée)",
    'summary': """Cockpit du gérant : POS, crédit clients, stock et
achats sur une seule page — santé de l'affaire, cash à risque, balance
âgée en miroir, échéancier fournisseurs et liste d'actions. Filtres
période / caisse / heure / jours ; drill-down vers les quatre tableaux
de bord spécialisés, dont il orchestre les moteurs sans dupliquer les
formules.""",
    'description': "Tableau de bord consolidé multi-onglets pour la "
                   "direction (LAVERANDAH).",
    'version': '18.0.1.0.2',
    'author': 'AITE Consulting',
    'license': 'LGPL-3',
    'category': 'AITE/Dashboards',
    'depends': [
        'aite_pos_analytics',
        'aite_pos_credit',
        'aite_stock_dashboard',
        'aite_purchase_dashboard',
    ],
    'data': [
        'views/direction_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'aite_direction_dashboard/static/src/scss/direction_dashboard.scss',
            'aite_direction_dashboard/static/src/js/direction_dashboard.js',
            'aite_direction_dashboard/static/src/xml/direction_dashboard.xml',
        ],
    },
    'installable': True,
    'application': True,
}
