# -*- coding: utf-8 -*-
{
    'name': "AITE — Gouvernante & maintenance des chambres",
    'summary': "Le tableau des chambres de la gouvernante, sa journée sur "
               "mobile, les inspections avec checklist, et les pannes "
               "signalées depuis la chambre jusqu'à la remise en service.",
    'description': """
AITE HOUSE — Gouvernante & maintenance
======================================

Pensé pour une équipe d'étage qui n'a jamais utilisé de logiciel :

* **Tableau des chambres** par état de ménage — À nettoyer · En cours ·
  À inspecter · Propre — avec le client présent, l'heure d'arrivée
  attendue et un seul bouton par étape ;
* **Ma journée** : chaque femme de chambre voit ses chambres, dans l'ordre,
  sur son téléphone, et coche au fur et à mesure ;
* **Répartition en un clic** : la gouvernante distribue les chambres du
  jour entre ses équipières ;
* **Inspection avec checklist** (lit, salle de bain, minibar, linge…) :
  une case non cochée renvoie la chambre en nettoyage avec le motif ;
* **Signaler une panne** depuis la chambre : la demande de maintenance
  est créée (app Maintenance d'Odoo), la chambre peut être mise hors
  service, et **revient en vente automatiquement** quand la réparation est
  terminée ;
* **Objets trouvés** : un registre simple — quoi, où, quand, rendu à qui.
""",
    'author': "AITE Consulting",
    'website': "https://aite-consulting.com",
    'category': 'Services/Hotel',
    'version': '18.0.1.0.5',
    'license': 'LGPL-3',
    'depends': ['aite_hotel_management', 'maintenance'],
    'data': [
        'security/ir.model.access.csv',
        'data/housekeeping_data.xml',
        'views/hotel_room_views.xml',
        'views/housekeeping_task_views.xml',
        'views/maintenance_views.xml',
        'views/lost_found_views.xml',
        'wizard/assign_wizard_views.xml',
        'wizard/report_issue_wizard_views.xml',
        'views/menus.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
