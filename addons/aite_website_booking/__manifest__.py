# -*- coding: utf-8 -*-
{
    'name': "AITE — Réservation en ligne",
    'summary': "Site web : réservation en ligne des espaces VIP / VVIP, "
               "des prestations (SPA, coiffure) et demandes de séjour — "
               "disponibilités réelles du moteur de créneaux, "
               "confirmation e-mail, acompte Mobile Money au comptoir.",
    'description': """
AITE Réservation en ligne (D4)
==============================

Parcours public, compatible mobile, branché sur les **disponibilités
réelles** :

* **Espaces VIP / VVIP** — grille de créneaux du jour (la même API
  ``get_day_grid`` que le tableau de bord : une seule source de
  vérité), réservation confirmée + e-mail automatique ;
* **Prestations SPA & coiffure** — choix de la prestation, de la
  ressource et d'un créneau où la durée tient en continu ;
* **Séjours (chambres & suites)** — demande de réservation transmise à
  la réception (canal « Site web » du PMS), confirmée par l'équipe ;
* **Espace client** — « Mes réservations » pour les comptes portail.

Paiement en ligne : le tunnel affiche le **repli contractuel** — acompte
réglé au comptoir (Orange Money / MTN MoMo / espèces) — tant que
l'agrégateur n'est pas activé. Point d'ancrage : brancher un
``payment.provider`` Odoo sur la page de confirmation (voir
``controllers/main.py``, méthode ``_confirm_slot``), sans toucher au
reste du tunnel.
""",
    'author': "AITE CONSULTING",
    'website': "https://aiteconsulting.com",
    'category': 'Industries',
    'version': '18.0.1.0.0',
    'license': 'LGPL-3',
    'depends': ['website', 'portal', 'aite_slot_booking',
                'aite_hotel_management'],
    'data': [
        'views/website_templates.xml',
        'data/website_menu_data.xml',
    ],
    'installable': True,
    'application': False,
}
