# -*- coding: utf-8 -*-
{
    'name': "AITE — Planning Gantt des chambres (Enterprise)",
    'summary': "Ajoute le planning Gantt des chambres au PMS AITE lorsque "
               "Odoo Enterprise (web_gantt) est disponible.",
    'description': """
AITE — Planning Gantt des chambres
==================================

Module **passerelle**. La vue Gantt (``web_gantt``) n'existe que dans
Odoo Enterprise : la placer dans le socle ``aite_hotel_management``
rendrait tout le PMS ininstallable sur Odoo Community.

Ce module isole donc la dépendance Enterprise :

* sur **Community**, il n'apparaît pas (``web_gantt`` absent) et le
  planning des chambres s'affiche en vue **calendrier** ;
* sur **Enterprise**, il s'installe automatiquement (``auto_install``)
  dès que ``aite_hotel_management`` et ``web_gantt`` sont présents, et
  le planning s'ouvre par défaut sur la vue **Gantt**.

Aucune configuration : l'action « Planning des chambres » du menu
Réception bascule seule.
""",
    'author': "AITE CONSULTING",
    'website': "https://aiteconsulting.com",
    'category': 'Industries',
    'version': '18.0.1.0.0',
    'license': 'LGPL-3',

    'depends': [
        'aite_hotel_management',
        'web_gantt',
    ],

    'data': [
        'views/hotel_reservation_gantt_views.xml',
    ],

    'installable': True,
    'application': False,
    # S'installe tout seul si — et seulement si — les deux dépendances
    # sont déjà installées (donc jamais sur Community).
    'auto_install': True,
}
