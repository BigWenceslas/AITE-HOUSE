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

La carte est posée UNE FOIS : à l'installation, dans chaque société qui a un
plan comptable (sinon juste après son chargement). Ensuite elle appartient au
client, qui la corrige à la main ou par un import Excel (colonne « id » =
identifiant externe __aite_messager__.produit_<clé> ; famille de caisse en
colonne « pos_categ_ids/id » = __aite_messager__.famille_<nom> ; procédure
complète dans les notes de version du restaurant). Une mise à niveau du
module (et le menu Point de Vente → Configuration → « Poser la carte Le
Messager ») :

* ne modifie AUCUN produit existant : nom, prix, coût, familles, catégorie,
  note, taxes, suivi en stock, accompagnement, présence en caisse, archivage
  restent ceux du client ;
* ne retire aucun produit de la caisse (les produits ajoutés par le client
  restent en vente) ;
* ne renomme, ne re-range ni ne repasse en coût moyen aucune famille ni
  catégorie existante ;
* ne pose que ce qui manque ET que la base n'a jamais reçu (un produit ajouté
  à la carte dans une version suivante du module) : un produit archivé, sorti
  de la caisse, renommé ou supprimé par le client ne revient pas (ce que la
  base a reçu est retenu dans le paramètre système
  aite_resto_carte_messager.elements_poses) ;
* complète la salle et l'équipe de démonstration si elles manquent ;
* coche une fois « Grouper les produits par famille sur l'addition et le
  ticket » sur la caisse du restaurant (18.0.1.3.6 ; aite_pos_restaurant
  18.0.1.0.14) : un client qui le décoche garde son choix.

Une notification dit ce qui est en place et ce qui vient d'être fait, par
exemple « Carte posée : 101 produits en 30 familles ; salle : 12 tables ;
équipe : 7 employés, 3 comptes. Rien n'a été créé en double. La carte est à
vous : une mise à niveau ne modifie aucun de vos produits… ». Le nom de la
société n'est pas changé. Désinstaller le module ne retire pas la carte.
""",
    'version': '18.0.1.3.6',
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
