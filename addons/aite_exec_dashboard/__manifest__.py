# -*- coding: utf-8 -*-
{
    'name': "AITE — Tableau de bord Direction",
    'summary': "Vue consolidée du complexe : hébergement (CA, occupation, "
               "ADR), restauration & boutique (CA POS, tickets, panier), "
               "prestations (SPA, coiffure, pressing, espaces) et points "
               "de fidélité — sur la charte AITE.",
    'description': """
AITE Tableau de bord Direction (adaptation A2)
==============================================

Une page unique pour la direction, qui consolide les trois pôles :

* **Hébergement** — chiffre d'affaires, taux d'occupation et ADR,
  fournis par le tableau de bord du PMS (même source, mêmes chiffres) ;
* **Restauration & boutique** — CA POS encaissé, nombre de tickets,
  panier moyen ;
* **Prestations** — CA réalisé des espaces VIP / VVIP, SPA, coiffure et
  pressing.

KPIs de période, mix par pôle (donut), évolution mensuelle comparée sur
six mois. Les points de fidélité émis apparaissent automatiquement si le
module Fidélité est installé (détection dynamique, aucune dépendance
dure).
""",
    'author': "AITE CONSULTING",
    'website': "https://aiteconsulting.com",
    'category': 'Industries',
    'version': '18.0.1.0.2',
    'license': 'LGPL-3',
    'depends': ['web', 'point_of_sale', 'aite_hotel_management',
                'aite_slot_booking'],
    'data': [
        'security/ir.model.access.csv',
        'views/exec_dashboard_actions.xml',
        'views/exec_menus.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'aite_exec_dashboard/static/src/scss/exec_dashboard.scss',
            'aite_exec_dashboard/static/src/js/services/utils.js',
            'aite_exec_dashboard/static/src/js/services/chartjs_loader.js',
            'aite_exec_dashboard/static/src/js/components/kpi_card.js',
            'aite_exec_dashboard/static/src/js/views/exec_dashboard_view.js',
            'aite_exec_dashboard/static/src/js/dashboard.js',
            'aite_exec_dashboard/static/src/xml/dashboard.xml',
        ],
    },
    'installable': True,
    'application': False,
}
