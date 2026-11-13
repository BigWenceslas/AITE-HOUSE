# -*- coding: utf-8 -*-
{
    'name': "AITE — Suivi des activités CRM",
    'summary': "Tableau de bord des tâches et activités sur les opportunités, "
               "analyse, et récapitulatif envoyé chaque matin à chaque commercial.",
    'description': """
AITE — Suivi des activités CRM
==============================

**Tableau de bord** (CRM → Suivi des activités) :

* indicateurs : activités en retard (gravité, montant en jeu), du jour,
  à venir, réalisées sur une période au choix avec comparaison à la période
  précédente et taux « à temps », opportunités sans activité planifiée ;
* onglet « À traiter » : liste des activités avec actions directes
  (fait avec compte rendu, reporter, réassigner) et opportunités sans
  activité ;
* onglet « Équipe » : tableau par commercial et plan de charge ;
* onglet « Tendances » : 12 dernières semaines et classements ;
* aperçu d'une opportunité dans un panneau latéral ;
* filtres par commercial, équipe, type d'activité et période.

**Rapport d'analyse** (CRM → Analyse) : tableau croisé, graphique et liste
des activités ouvertes et réalisées.

**Récapitulatif du matin** : chaque jour, à l'heure choisie, chaque
utilisateur reçoit par e-mail la liste de ses activités en cours sur les
opportunités — en retard (avec leur gravité), du jour et à venir — avec un
lien vers chacune. Réglages dans CRM → Configuration → Paramètres ; chaque
utilisateur peut s'en désabonner dans ses préférences.

Les droits d'accès d'Odoo s'appliquent partout : chacun ne voit que les
opportunités qu'il a le droit de voir.
""",
    'author': "AITE CONSULTING",
    'website': "https://aite-consulting.com",
    'category': 'Sales/CRM',
    'version': '19.0.2.0.0',
    'license': 'LGPL-3',
    'depends': ['crm'],
    'data': [
        'security/ir.model.access.csv',
        'security/aite_crm_activity_security.xml',
        'data/ir_cron_data.xml',
        'views/dashboard_views.xml',
        'report/crm_activity_report_views.xml',
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
