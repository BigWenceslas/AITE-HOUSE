# -*- coding: utf-8 -*-
{
    'name': "AITE — Jeu d'essai démonstration",
    'summary': """Données de démonstration du complexe (FCFA / XAF) :
144 produits restaurant & boutique, 40 clients,
13 ressources, 333 réservations sur 7 semaines,
474 mouvements de fidélité calibrés VIP / VVIP.
NE PAS INSTALLER EN PRODUCTION.""",
    # Description en reStructuredText : sans cette clé, Odoo rabat la
    # fiche Apps sur README.md et rend du Markdown comme du RST — la page
    # s'affiche alors criblée de blocs d'erreur docutils.
    'description': """
AITE — Jeu d'essai de démonstration
===================================

**À installer uniquement sur une base de DÉMONSTRATION.** La
désinstallation retire l'ensemble du jeu d'essai.

Contenu
-------

============================================== ======
Domaine                                        Nombre
============================================== ======
Catégories (internes + caisse)                     43
Produits (restaurant, boutique, prestations)      144
Clients (dont profils VIP / VVIP calibrés)         40
Ressources à créneaux                              13
Prestations                                        22
Réservations (6 sem. passées + sem. à venir)      333
Mouvements de fidélité                            474
============================================== ======

Volet hôtelier
--------------

============================================== =======
Domaine                                         Nombre
============================================== =======
Hôtel, étages, types, chambres, produits folio      27
Séjours (réservations + lignes chambre)        188 × 2
Folios et lignes (nuitées datées, services)        602
============================================== =======

Volet boutique
--------------

63 articles stockables mis en stock, 20 seuils d'alerte posés — dont 3
ruptures et 6 articles sous seuil visibles immédiatement dans le tableau
de bord Stock. 5 fournisseurs et une caisse « Boutique (démo) ».

Points d'attention
------------------

* Les dates sont **relatives à l'installation** : le planning du jour et
  les périodes « semaine / mois » sont peuplés quel que soit le jour de
  la démonstration.
* Les statuts VIP / VVIP posés sur les fiches sont **reproduits par le
  moteur** : le recalcul nocturne aboutit aux mêmes statuts.
* Prix en FCFA (XAF), l'unité sur laquelle sont calibrés les seuils du
  produit. Aucune taxe n'est posée sur les produits : le paramétrage
  fiscal reste celui de l'atelier dédié.
* La rotation et les classes de vitesse du tableau de bord Stock exigent
  un historique de ventes réelles : elles s'animent après les premières
  commandes passées en caisse pendant la démonstration.
""",
    'version': '18.0.1.2.2',
    'author': 'AITE Consulting',
    'license': 'LGPL-3',
    'category': 'Hidden/Demo',
    # Le jeu d'essai couvre désormais TOUS les modules de la suite :
    # sans ces dépendances, les ardoises, notes de chambre, achats et
    # tableaux de bord restaient vides sur une base de démonstration.
    'depends': [
        'point_of_sale',
        'purchase',
        'aite_hotel_management',
        'aite_slot_booking',
        'aite_website_booking',
        'aite_loyalty',
        'aite_pos_analytics',
        'aite_pos_credit',
        'aite_hotel_pos_link',
        'aite_stock_dashboard',
        'aite_purchase_dashboard',
        'aite_direction_dashboard',
        'aite_exec_dashboard',
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
        'security/ir.model.access.csv',
        'views/demo_generator_views.xml',
    ],
    'post_init_hook': 'post_init_generate',
    'installable': True,
    'application': False,
}
