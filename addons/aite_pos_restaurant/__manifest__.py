# -*- coding: utf-8 -*-
{
    'name': "AITE — Restaurant (service à table)",
    'summary': "Caisse de restaurant : code personnel, quatre niveaux, plan de salle "
               "toujours affiché, personnes à l'ouverture, annulations tracées, "
               "alerte de durée, refus des produits épuisés.",
    'description': """
AITE — Restaurant (service à table)
===================================

Incrément 1 du lot 1 (spécification « Restaurant, lot 1 », partie 7) :

* case « Service à table contrôlé » sur la caisse (réglages du Point de Vente,
  bloc Restaurant), qui pose d'office la connexion par code, le contrôle des
  prix, les remises désactivées, le partage et l'impression de l'addition ;
* quatre niveaux en caisse sur la fiche employé (serveur, caissière, chef de
  salle ou superviseur, manager) et un code de 4 chiffres propre à chacun,
  proposé d'office ;
* une caisse « Restaurant » (Espèces, Mobile Money, salle « Salle ») créée au
  premier lancement, sans toucher aux caisses existantes : à l'installation
  si le plan comptable est déjà chargé, sinon au premier chargement du plan
  comptable de la société (une société créée plus tard reçoit la sienne) ;
  jamais recréée par un rechargement du plan comptable ;
* les messages de la caisse (ouverture, espèces) ne demandent plus de
  courriel aux employés.

Aucune dépendance au socle hôtelier.
""",
    'version': '18.0.1.0.0',
    'author': "AITE Consulting",
    'website': "https://aiteconsulting.com",
    'category': 'Point of Sale',
    'license': 'LGPL-3',
    'depends': ['pos_restaurant', 'pos_hr'],
    'data': [
        'views/hr_employee_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': ['aite_pos_restaurant/static/src/**/*'],
        'web.assets_tests': ['aite_pos_restaurant/static/tests/tours/**/*'],
    },
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': False,
}
