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

* sur **Community**, il ne s'installe pas (``web_gantt`` absent) et le
  planning des chambres s'affiche en vue **calendrier** ;
* sur **Enterprise**, il s'installe automatiquement (``auto_install``)
  quand le socle ``aite_hotel_management`` est installé **en même temps**
  (base neuve), et le planning s'ouvre par défaut sur la vue **Gantt**.

**Base où le socle est déjà installé** (mise à jour d'une installation
existante) : Odoo ne retient un module ``auto_install`` que si l'une de
ses dépendances est en cours d'installation ; une simple mise à niveau
du socle ne l'installe donc pas. L'installer une fois à la main :
Applications → retirer le filtre « Applications » → chercher « Gantt »
→ **Installer** (voir ``docs/INSTALLATION.md``).

Aucune configuration ensuite : l'action « Planning des chambres » du
menu Réservations bascule seule.
""",
    'author': "AITE CONSULTING",
    'website': "https://aiteconsulting.com",
    'category': 'Industries',
    'version': '18.0.1.0.2',
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
    # S'installe tout seul quand l'une de ses dépendances est en cours
    # d'installation et que l'autre est installée (jamais sur Community,
    # où ``web_gantt`` n'existe pas). Odoo n'évalue ``auto_install`` qu'à
    # l'installation d'une dépendance : sur une base où le socle et
    # ``web_gantt`` sont déjà installés, il faut l'installer à la main
    # (ECARTS n° 72, docs/INSTALLATION.md). On garde ``True`` : c'est le
    # bon comportement sur une base neuve, et aucune clé du manifeste ne
    # déclenche l'installation depuis une mise à niveau.
    'auto_install': True,
}
