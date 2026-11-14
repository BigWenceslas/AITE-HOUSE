# -*- coding: utf-8 -*-
{
    'name': "AITE — Analyses du restaurant par employé",
    'summary': "Le serveur (ouverte par) et la personne qui a encaissé dans "
               "l'analyse AITE du Point de Vente, quand toutes les additions "
               "passent sous le compte de la caisse.",
    'description': """
AITE — Analyses du restaurant par employé
=========================================

Module **passerelle** entre ``aite_pos_analytics`` (l'analyse AITE du Point
de Vente) et ``aite_pos_restaurant`` (la caisse du restaurant, à code
personnel) — exigence AH-03 de la spécification du restaurant, partie 5.5.

Dans un restaurant, toutes les additions passent sous le même compte Odoo,
celui de la caisse : regrouper l'analyse par compte ne dit plus qui a vendu.
Ce module ajoute à « Analyse AITE → Tableau croisé & graphique » :

* **Serveur (ouverte par)** : l'employé qui a ouvert la table (le vendeur
  d'un restaurant, qui n'encaisse pas) ;
* **Encaissée par** : l'employé qui a validé le paiement (sur une caisse à
  codes hors service à table, l'employé d'Odoo) ;
* le compte Odoo s'affiche « Compte Odoo ».

Recherche et regroupements « Serveur » et « Encaissée par ». Les employés sont
lus sur leur fiche publique : le lecteur des analyses n'a besoin d'aucun droit
sur les Employés.

Il s'installe seul (``auto_install``) quand le restaurant est installé sur une
base qui a l'analyse AITE ; il ne s'installe pas chez un client sans
restaurant, et ``aite_pos_analytics`` ne dépend toujours ni de ``hr`` ni de
``pos_hr``. Sur une base où les deux modules sont déjà installés, l'installer
une fois à la main (Applications → chercher « par employé » → Installer).
""",
    'version': '18.0.1.0.0',
    'author': "AITE Consulting",
    'website': "https://aiteconsulting.com",
    'category': 'Point of Sale',
    'license': 'LGPL-3',
    'depends': ['aite_pos_analytics', 'aite_pos_restaurant'],
    'data': [
        'views/pos_analytics_report_views.xml',
    ],
    'uninstall_hook': 'uninstall_hook',
    'installable': True,
    'application': False,
    # S'installe seul quand l'une des deux dépendances est installée et que
    # l'autre l'est déjà, ou l'est en même temps (base neuve du restaurant).
    'auto_install': True,
}
