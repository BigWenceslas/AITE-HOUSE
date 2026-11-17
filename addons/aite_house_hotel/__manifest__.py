# -*- coding: utf-8 -*-
{
    'name': "AITE HOUSE — Hôtel (tout installer)",
    'summary': "Un seul module à activer : toute la suite hôtelière AITE HOUSE "
               "(réception, taxe de séjour, registre, gouvernante, caisses, fidélité, "
               "espaces, réservation en ligne, tableaux de bord)",
    'description': """
AITE HOUSE — Hôtel
==================

Activer ce module installe toute la suite hôtelière AITE HOUSE :

* Gestion Hôtelière (PMS) : aite_hotel_management ;
* Taxe de séjour : aite_city_tax ; Registre des clients : aite_guest_registry ;
* Gouvernante & maintenance : aite_housekeeping ;
* Note de chambre (caisse → folio) : aite_hotel_pos_link ;
* Crédit clients (ardoise) : aite_pos_credit ; POS Analytics : aite_pos_analytics ;
* Fidélité : aite_loyalty ; Espaces & Prestations : aite_slot_booking ;
* Réservation en ligne : aite_website_booking ;
* tableaux de bord Stock, Achats, Direction (deux vues) ;
* sur Odoo Enterprise seulement, le planning Gantt des chambres
  (aite_hotel_gantt), installé si web_gantt est disponible sur le serveur.

Aucune donnée de démonstration (le jeu d'essai est le module aite_demo_data).
""",
    'version': '18.0.1.0.0',
    'category': 'Services/Hotel',
    'author': "AITE Consulting",
    'website': "https://aiteconsulting.com",
    'license': 'LGPL-3',
    'depends': [
        'aite_hotel_management', 'aite_city_tax', 'aite_guest_registry', 'aite_housekeeping',
        'aite_hotel_pos_link', 'aite_pos_credit', 'aite_pos_analytics', 'aite_loyalty',
        'aite_slot_booking', 'aite_website_booking', 'aite_stock_dashboard',
        'aite_purchase_dashboard', 'aite_direction_dashboard', 'aite_exec_dashboard',
    ],
    'data': ['data/installer_data.xml'],
    'installable': True,
    'application': True,
}
