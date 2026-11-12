# -*- coding: utf-8 -*-
{
    'name': "AITE — Suivi des activités CRM",
    'summary': "Tableau de bord des tâches et activités sur les opportunités, "
               "et récapitulatif envoyé chaque matin à chaque commercial.",
    'description': """
AITE — Suivi des activités CRM
==============================

**Tableau de bord** (CRM → Suivi des activités) :

* indicateurs : activités en retard, du jour, à venir, réalisées sur
  7 jours, opportunités sans activité planifiée ;
* tableau par commercial ;
* liste des activités à traiter, avec actions directes : marquer comme
  fait (avec compte rendu), reporter, réassigner, ouvrir l'opportunité ;
* opportunités sans activité planifiée, avec planification en un clic ;
* filtres par commercial, équipe commerciale et type d'activité.

**Récapitulatif du matin** : chaque jour, à l'heure choisie, chaque
utilisateur reçoit par e-mail la liste de ses activités en cours sur les
opportunités — en retard, du jour et à venir — avec un lien vers chacune.
Réglages dans CRM → Configuration → Paramètres ; chaque utilisateur peut
s'en désabonner dans ses préférences.

Les droits d'accès d'Odoo s'appliquent partout : chacun ne voit que les
opportunités qu'il a le droit de voir.
""",
    'author': "AITE CONSULTING",
    'website': "https://aite-consulting.com",
    'category': 'Sales/CRM',
    'version': '19.0.1.0.0',
    'license': 'LGPL-3',
    'depends': ['crm'],
    'data': [
        'data/ir_cron_data.xml',
        'views/dashboard_views.xml',
        'views/digest_templates.xml',
        'views/res_config_settings_views.xml',
        'views/res_users_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'aite_crm_activity/static/src/dashboard/**/*',
        ],
        'web.assets_tests': [
            'aite_crm_activity/static/tests/tours/**/*',
        ],
    },
    'installable': True,
    'application': False,
}
