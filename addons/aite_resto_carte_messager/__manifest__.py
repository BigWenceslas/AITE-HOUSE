# -*- coding: utf-8 -*-
{
    'name': "AITE — Carte du restaurant Le Messager (démonstration)",
    'summary': "Pose la carte du restaurant Le Messager dans la caisse « Restaurant » : "
               "familles, produits et prix, accompagnements, coûts et stock des boissons",
    'description': """
Carte du restaurant Le Messager (Douala)
========================================

Activer ce seul module installe tout le restaurant AITE : la caisse au service
à table contrôlé (aite_pos_restaurant), l'ardoise (aite_pos_credit), l'analyse
des ventes (aite_pos_analytics) et sa passerelle (aite_pos_analytics_hr), et
sur Odoo Enterprise l'écran de cuisine (module aite_house_restaurant).

À l'installation, le module pose dans la caisse au service à table contrôlé
(module « AITE — Restaurant ») :

* une salle de 12 tables ;
* une équipe fictive aux quatre niveaux, avec son code de caisse : serveurs
  Brice 1001, Nadège 1002, Loïc 1003 ; caissières Clarisse 2001, Prisca 2002 ;
  chef de salle Hervé 3001 ; manager Sandrine 4001 ;
* trois comptes Odoo de démonstration (mot de passe = identifiant, à changer) :
  « caisse » (la tablette), « manager », « chef » (rapports du restaurant) ;

* les familles de la caisse sur trois niveaux au plus (Petit déjeuner, Plats,
  Pizzas & burgers, Afternoon tea, Bar), et les mêmes noms en catégories de
  produit ;
* les 101 produits de la carte, prix en FCFA, sans taxe (la TVA se règle avec
  le comptable) ; une taille = un produit (une touche en caisse) ;
* l'accompagnement au choix des plats (riz nature, riz Messager, frites
  plantain, frites pomme), sans supplément ;
* pour les boissons revendues : un coût d'achat, le suivi en stock et un stock
  de départ (les marges des boissons sont justes dans l'analyse AITE), et leurs
  catégories de produits (Bar et ses sous-catégories) en « Coût moyen (AVCO) » :
  le coût suit les achats ; les plats cuisinés n'ont ni coût ni stock.

À faire valider par le client : les boissons ajoutées hors carte (eaux, jus,
sodas, bières, café, thé) et leurs prix ; les coûts d'achat, tous estimés ;
le prix du whisky « Black » (40 000 provisoire). Chaque produit concerné le
dit dans sa note interne.

La carte est posée à l'installation et à chaque mise à niveau du module, dans
chaque société qui a un plan comptable (sinon juste après son chargement), et
à la demande : Point de Vente → Configuration → « Poser la carte Le Messager »
(une notification dit ce qui est en place et ce qui vient d'être fait, par
exemple « Carte posée : 101 produits en 30 familles ; salle : 12 tables ;
équipe : 7 employés, 3 comptes. Rien n'a été créé en double. »). Le nom de la société n'est pas changé. Désinstaller le module ne retire pas la carte.
""",
    'version': '18.0.1.3.3',
    'category': 'Sales/Point of Sale',
    'author': "AITE Consulting",
    'website': "https://aiteconsulting.com",
    'license': 'LGPL-3',
    # Activer ce seul module installe tout le restaurant (aite_house_restaurant :
    # caisse au service à table, ardoise, analyses, écran de cuisine sur Enterprise).
    'depends': ['aite_house_restaurant'],
    'data': ['data/carte_data.xml', 'views/carte_views.xml'],
    'installable': True,
    'application': False,
}
