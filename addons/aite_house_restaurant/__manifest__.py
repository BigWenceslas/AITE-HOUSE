# -*- coding: utf-8 -*-
{
    'name': "AITE HOUSE — Restaurant (tout installer)",
    'summary': "Un seul module à activer : la caisse au service à table, l'ardoise, l'analyse "
               "des ventes et, sur Odoo Enterprise, l'écran de cuisine",
    'description': """
AITE HOUSE — Restaurant
=======================

Activer ce module installe tout le restaurant AITE :

* AITE — Restaurant (service à table) : aite_pos_restaurant, avec pos_restaurant et pos_hr ;
* AITE — Crédit clients (ardoise) : aite_pos_credit ;
* AITE — POS Analytics (analyse des ventes, familles, marges) : aite_pos_analytics ;
* AITE — Analyses du restaurant par employé : aite_pos_analytics_hr ;
* sur Odoo Enterprise seulement, l'écran de cuisine (pos_preparation_display, avec ses passerelles restaurant et employés),
  installé s'il est disponible sur le serveur ; sur Community, il n'existe pas
  et rien n'est fait.

La caisse au service à table contrôlé (« Restaurant ») reçoit d'office le mode
de paiement « Ardoise client » d'aite_pos_credit, à l'installation et à chaque
mise à niveau, jamais en double ; à la caisse, seul le manager s'en sert (règles
d'aite_pos_restaurant). Un client qui ne fait pas crédit archive le mode
(Point de Vente → Configuration → Modes de paiement) : un mode archivé n'est
jamais remis ; seulement retiré de la caisse, il revient à la mise à niveau.

Les modules optionnels sont aussi installés à la mise à niveau de ce module
s'ils manquent. Aucune donnée de démonstration : la carte de démonstration est
le module « AITE — Carte du restaurant Le Messager ».
""",
    'version': '18.0.1.0.2',
    'category': 'Sales/Point of Sale',
    'author': "AITE Consulting",
    'website': "https://aiteconsulting.com",
    'license': 'LGPL-3',
    'depends': ['aite_pos_restaurant', 'aite_pos_credit', 'aite_pos_analytics', 'aite_pos_analytics_hr'],
    'data': ['data/installer_data.xml'],
    'installable': True,
    'application': True,
}
