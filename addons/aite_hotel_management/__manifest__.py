# -*- coding: utf-8 -*-
{
    'name': "AITE — Gestion Hôtelière (PMS)",
    'summary': "PMS complet : chambres, réservations, check-in/out, folios "
               "clients, acomptes Mobile Money, gouvernante (housekeeping), "
               "tarifs saisonniers, commissions d'agents, planning Gantt des "
               "chambres et tableau de bord (occupation, ADR, RevPAR).",
    'description': """
AITE Gestion Hôtelière
======================

Property Management System (PMS) complet pour Odoo 18 Enterprise, inspiré
des meilleures pratiques du marché (Opera Cloud, Mews, Cloudbeds) et pensé
pour le contexte camerounais (OHADA, Mobile Money).

Fonctionnel
-----------
* **Configuration** : hôtels (multi-établissements), étages, types de
  chambre, chambres, aménités, services (restaurant, blanchisserie,
  transport…), tarifs saisonniers.
* **Réservations** : contrôle de disponibilité, réservation rapide,
  workflow brouillon → confirmée → arrivée (check-in) → départ
  (check-out), annulation et no-show, changement de chambre,
  commissions d'agents / apporteurs.
* **Front desk** : planning Gantt des chambres (Enterprise), calendrier,
  arrivées / départs / clients présents du jour.
* **Folio client** : note de séjour regroupant nuitées et services
  (restaurant, blanchisserie, minibar…), acomptes et règlements
  Mobile Money (MTN MoMo / Orange Money), espèces, carte ; écritures
  comptables 411 et facturation au départ, lettrage automatique.
* **Gouvernante** : états de chambre (propre / à nettoyer / en cours /
  à inspecter), tâches de ménage auto au départ, chambres hors service.
* **Pilotage** : tableau de bord OWL — taux d'occupation, ADR, RevPAR,
  chiffre d'affaires, room board temps réel, mouvements du jour,
  graphiques d'évolution.

Compatible Odoo 18 Enterprise. Conçu dans la continuité du module
``aite_pos_credit`` (mêmes conventions, même charte de tableau de bord).
""",
    'author': "AITE CONSULTING",
    'website': "https://aiteconsulting.com",
    'category': 'Industries',
    'version': '18.0.1.0.2',
    'license': 'LGPL-3',

    'depends': [
        'base',
        'mail',
        'product',
        'account',
        'sale',
        'web_gantt',  # planning des chambres (Odoo Enterprise)
    ],

    'data': [
        'security/hotel_security.xml',
        'security/ir.model.access.csv',
        'data/hotel_sequence_data.xml',
        'data/hotel_data.xml',
        'data/mail_template_data.xml',
        'data/ir_cron_data.xml',
        'views/hotel_hotel_views.xml',
        'views/hotel_room_views.xml',
        'views/hotel_service_views.xml',
        'wizard/hotel_room_change_wizard_views.xml',
        'views/hotel_reservation_views.xml',
        'views/hotel_folio_views.xml',
        'views/hotel_housekeeping_views.xml',
        'views/res_partner_views.xml',
        'views/res_config_settings_views.xml',
        'wizard/hotel_booking_wizard_views.xml',
        'wizard/hotel_checkout_wizard_views.xml',
        'wizard/hotel_payment_wizard_views.xml',
        'report/hotel_reports.xml',
        'report/report_reservation.xml',
        'report/report_folio.xml',
        'views/hotel_dashboard_actions.xml',
        'views/hotel_menus.xml',
    ],

    'demo': [
        'demo/hotel_demo.xml',
    ],

    'assets': {
        'web.assets_backend': [
            'aite_hotel_management/static/src/scss/hotel_dashboard.scss',
            'aite_hotel_management/static/src/js/services/hotel_utils.js',
            'aite_hotel_management/static/src/js/services/chartjs_loader.js',
            'aite_hotel_management/static/src/js/components/kpi_card.js',
            'aite_hotel_management/static/src/js/views/hotel_dashboard_view.js',
            'aite_hotel_management/static/src/js/hotel_dashboard.js',
            'aite_hotel_management/static/src/xml/hotel_dashboard.xml',
        ],
    },

    'installable': True,
    'application': True,
    'auto_install': False,
}
