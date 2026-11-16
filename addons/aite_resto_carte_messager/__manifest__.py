# -*- coding: utf-8 -*-
{
    'name': "AITE — Carte du restaurant Le Messager (démonstration)",
    'summary': "Pose la carte du restaurant Le Messager dans la caisse « Restaurant » : "
               "familles, produits et prix, accompagnements, coûts et stock des boissons",
    'description': """
Carte du restaurant Le Messager (Douala)
========================================

À l'installation, le module pose dans la caisse au service à table contrôlé
(module « AITE — Restaurant ») :

* les familles de la caisse sur trois niveaux au plus (Petit déjeuner, Plats,
  Pizzas & burgers, Afternoon tea, Bar), et les mêmes noms en catégories de
  produit ;
* les 101 produits de la carte, prix en FCFA, sans taxe (la TVA se règle avec
  le comptable) ; une taille = un produit (une touche en caisse) ;
* l'accompagnement au choix des plats (riz nature, riz Messager, frites
  plantain, frites pomme), sans supplément ;
* pour les boissons revendues : un coût d'achat, le suivi en stock et un stock
  de départ (les marges des boissons sont justes dans l'analyse AITE) ; les
  plats cuisinés n'ont ni coût ni stock.

À faire valider par le client : les boissons ajoutées hors carte (eaux, jus,
sodas, bières, café, thé) et leurs prix ; les coûts d'achat, tous estimés ;
le prix du whisky « Black » (40 000 provisoire). Chaque produit concerné le
dit dans sa note interne.

Installer sur une base où la caisse « Restaurant » existe déjà. Le nom de la
société n'est pas changé. Désinstaller le module ne retire pas la carte.
""",
    'version': '18.0.1.0.0',
    'category': 'Sales/Point of Sale',
    'author': "AITE Consulting",
    'website': "https://aiteconsulting.com",
    'license': 'LGPL-3',
    'depends': ['aite_pos_restaurant'],
    'data': [],
    'post_init_hook': 'poser_carte',
    'installable': True,
    'application': False,
}
