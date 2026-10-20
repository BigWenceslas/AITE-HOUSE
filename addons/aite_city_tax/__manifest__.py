# -*- coding: utf-8 -*-
{
    'name': "AITE — Taxe de séjour",
    'summary': "Taxe de séjour calculée automatiquement sur chaque séjour, "
               "selon la catégorie de l'hôtel — et l'état mensuel à déclarer.",
    'description': """
AITE HOUSE — Taxe de séjour
===========================

Au Cameroun comme dans la plupart des pays d'Afrique francophone, l'hôtelier
collecte une **taxe de séjour** par nuitée et la reverse chaque mois à
l'administration fiscale. Ce module la gère **sans aucune saisie** :

* un **barème** par pays et par catégorie d'établissement (étoiles),
  livré pré-rempli pour le Cameroun (barème DGI : 5 000 / 4 000 / 3 000 /
  1 000 / 500 FCFA par nuitée), la Côte d'Ivoire, le Sénégal et la Guinée ;
* une **ligne « Taxe de séjour » ajoutée automatiquement au folio**, à chaque
  mise à jour des nuitées, hors base TVA, calculée sur nuits × personnes
  (ou nuits × chambres selon le barème) ;
* l'**état mensuel de reversement** : nuitées taxables, montant collecté,
  par hôtel et par mois — prêt pour la déclaration du 15.

Aucune action de la réception : choisir une fois la catégorie de l'hôtel
suffit.
""",
    'author': "AITE Consulting",
    'website': "https://aite-consulting.com",
    'category': 'Services/Hotel',
    'version': '18.0.1.0.1',
    'license': 'LGPL-3',
    'depends': ['aite_hotel_management'],
    'data': [
        'security/ir.model.access.csv',
        'data/city_tax_data.xml',
        'views/city_tax_rate_views.xml',
        'views/hotel_hotel_views.xml',
        'views/hotel_folio_views.xml',
        'views/city_tax_report_views.xml',
        'views/menus.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
