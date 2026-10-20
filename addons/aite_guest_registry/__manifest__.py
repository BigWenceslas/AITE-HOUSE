# -*- coding: utf-8 -*-
{
    'name': "AITE — Registre des clients (fiche de police & statistiques)",
    'summary': "Fiche d'enregistrement de chaque occupant, registre "
               "chronologique pour la police, statistiques mensuelles "
               "du tourisme — tout depuis l'écran de check-in.",
    'description': """
AITE HOUSE — Registre des clients
=================================

La loi camerounaise (loi n° 2016/006, art. 28) impose à tout hébergeur
l'enregistrement de ses clients et la production de statistiques (art. 16).
Ce module le fait **au moment du check-in, sans écran supplémentaire** :

* **Fiche d'enregistrement** par occupant (identité, pièce, nationalité,
  provenance, destination) — pré-remplie depuis la fiche client, signée sur
  papier ou validée à l'écran, imprimable en un clic ;
* **Registre chronologique** des arrivées et départs, consultable et
  exportable (Excel / PDF) pour tout contrôle de police ;
* **Statistiques mensuelles** : arrivées, nuitées, résidents / non-résidents,
  nationalités, durée moyenne de séjour, taux d'occupation — le format
  attendu par le ministère du Tourisme (MINTOUL) ;
* Rappel automatique : un séjour arrivé sans fiche complète est signalé.

Prêt pour une future plateforme de télédéclaration (modèle HORA, Côte
d'Ivoire) : chaque fiche porte toutes les données requises.
""",
    'author': "AITE Consulting",
    'website': "https://aite-consulting.com",
    'category': 'Services/Hotel',
    'version': '18.0.1.0.2',
    'license': 'LGPL-3',
    'depends': ['aite_hotel_management'],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence_data.xml',
        'views/guest_registration_views.xml',
        'views/hotel_reservation_views.xml',
        'views/res_partner_views.xml',
        'views/guest_stats_views.xml',
        'report/registration_card_report.xml',
        'report/police_register_report.xml',
        'views/menus.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
