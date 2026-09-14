# -*- coding: utf-8 -*-
{
    'name': "AITE — Jeu d'essai démonstration",
    'summary': """Données de démonstration du complexe (Guinée, GNF) :
144 produits restaurant & boutique, 40 clients,
13 ressources, 333 réservations sur 7 semaines,
474 mouvements de fidélité calibrés VIP / VVIP.
NE PAS INSTALLER EN PRODUCTION.""",
    'version': '18.0.1.2.1',
    'author': 'AITE Consulting',
    'license': 'LGPL-3',
    'category': 'Hidden/Demo',
    'depends': [
        'point_of_sale',
        'aite_hotel_management',
        'aite_slot_booking',
        'aite_loyalty',
        'aite_stock_dashboard',
    ],
    'data': [
        'data/01_product_categories.xml',
        'data/02_products_restaurant.xml',
        'data/03_products_boutique.xml',
        'data/04_products_services.xml',
        'data/05_partners.xml',
        'data/06_resources.xml',
        'data/07_services.xml',
        'data/08_bookings.xml',
        'data/09_loyalty_moves.xml',
        'data/10_hotel_structure.xml',
        'data/11_hotel_reservations.xml',
        'data/12_hotel_folios.xml',
        'data/13_boutique_stock.xml',
    ],
    'installable': True,
    'application': False,
}
