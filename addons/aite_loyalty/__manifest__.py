# -*- coding: utf-8 -*-
{
    'name': "AITE — Fidélité unifiée & segmentation",
    'summary': "Moteur de fidélité multi-services (restaurant, boutique, "
               "séjours, prestations) : points, historisation, et statut "
               "client Standard / VIP / VVIP recalculé automatiquement "
               "selon la fréquence, les dépenses et les types de "
               "services utilisés.",
    'description': """
AITE Fidélité unifiée (D3)
==========================

Un capital de points **unique** alimenté par tous les services :

* commandes POS (restaurant & boutique) réglées ;
* folios de séjour facturés / soldés (hébergement) ;
* prestations réalisées (SPA, coiffure, pressing, espaces VIP).

Chaque gain est historisé (grand livre de points, origine détaillée,
montant de base). Le **statut client** — Standard / VIP / VVIP — est
recalculé chaque nuit sur une fenêtre glissante, selon les trois
critères du cahier des charges : fréquence de visite (jours distincts),
montant des dépenses, et diversité des services utilisés.

Barème et seuils entièrement paramétrables (Réglages → AITE Fidélité) ;
ajustement manuel réservé aux responsables ; règles de calcul pures,
extraites et exécutées par les tests.
""",
    'author': "AITE CONSULTING",
    'website': "https://aiteconsulting.com",
    'category': 'Industries',
    'version': '18.0.1.0.0',
    'license': 'LGPL-3',
    'depends': ['base', 'mail', 'point_of_sale',
                'aite_hotel_management', 'aite_slot_booking'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_cron_data.xml',
        'views/loyalty_move_views.xml',
        'views/res_partner_views.xml',
        'views/res_config_settings_views.xml',
        'wizard/loyalty_adjust_wizard_views.xml',
        'views/loyalty_menus.xml',
    ],
    'installable': True,
    'application': False,
}
