# -*- coding: utf-8 -*-
{
    'name': "AITE — Espaces & Prestations (réservation par créneaux)",
    'summary': "Moteur mutualisé de réservation par créneaux horaires : "
               "espaces VIP / VVIP, cabines SPA, fauteuils coiffure, "
               "pressing — conflits, confirmations e-mail, no-show, report "
               "au folio du séjour, planning du jour et tableau de bord.",
    'description': """
AITE Espaces & Prestations (D1 + D2)
====================================

Un seul moteur de réservation à créneaux pour deux usages :

* **D1 — Espaces VIP / VVIP** : salons réservés à l'heure, tarif horaire,
  capacité paramétrable, règles de conflit identiques aux chambres.
* **D2 — Prestations** : SPA, salon de coiffure H&F, pressing — catalogue
  de prestations (durée, prix, article), agenda par ressource, statuts
  planifié / réalisé / annulé / no-show, quantités (pressing), retrait.

Intégration hôtel : chaque réservation peut être **reportée au folio du
séjour** (ligne de service) ; confirmation e-mail automatique ; no-show
automatique après un délai de grâce ; planning du jour par ressource et
tableau de bord (remplissage, CA, mix de prestations) sur la charte AITE.

Le moteur expose une API de disponibilité (grille de créneaux) réutilisée
par le tableau de bord **et** par la réservation en ligne (module site
web) : une seule source de vérité pour les disponibilités.
""",
    'author': "AITE CONSULTING",
    'website': "https://aiteconsulting.com",
    'category': 'Industries',
    'version': '18.0.1.0.2',
    'license': 'LGPL-3',
    'depends': ['base', 'mail', 'product', 'account',
                'aite_hotel_management', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'data/slot_sequence_data.xml',
        'data/mail_template_data.xml',
        'data/ir_cron_data.xml',
        'views/booking_resource_views.xml',
        'views/booking_service_views.xml',
        'views/booking_booking_views.xml',
        'views/res_config_settings_views.xml',
        'views/slot_dashboard_actions.xml',
        'views/slot_menus.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'aite_slot_booking/static/src/scss/slot_dashboard.scss',
            'aite_slot_booking/static/src/js/services/utils.js',
            'aite_slot_booking/static/src/js/services/chartjs_loader.js',
            'aite_slot_booking/static/src/js/components/kpi_card.js',
            'aite_slot_booking/static/src/js/views/slot_dashboard_view.js',
            'aite_slot_booking/static/src/js/dashboard.js',
            'aite_slot_booking/static/src/xml/dashboard.xml',
        ],
    },
    'installable': True,
    'application': False,
}
