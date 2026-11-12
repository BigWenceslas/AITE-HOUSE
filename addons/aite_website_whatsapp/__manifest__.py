# -*- coding: utf-8 -*-
{
    'name': "AITE — Bouton WhatsApp du site web",
    'summary': "Bouton flottant sur toutes les pages du site : un clic "
               "ouvre directement une discussion WhatsApp avec vous.",
    'description': """
AITE — Bouton WhatsApp
======================

Affiche sur **toutes les pages du site web** (accueil, pages, boutique,
blog, espace client, connexion, page 404…) un bouton flottant aux couleurs
de WhatsApp. Un clic ouvre une discussion avec votre numéro, dans
l'application sur mobile et dans WhatsApp Web sur ordinateur, avec le
message d'accueil de votre choix déjà saisi.

Réglages : Site web → Configuration → Paramètres → bloc « WhatsApp » :

* activation du bouton, par site web (multi-sites) ;
* numéro au format international (+237 6 99 00 00 00) ; un numéro local
  (699 00 00 00) est complété par l'indicatif du pays de la société quand
  la bibliothèque phonenumbers est installée ;
* message pré-rempli et texte d'accroche, traduisibles ;
* position du bouton : en bas à droite ou en bas à gauche ;
* lien de test, pour vérifier le numéro en un clic.
""",
    'author': "AITE CONSULTING",
    'website': "https://aite-consulting.com",
    'category': 'Website/Website',
    'version': '19.0.2.0.0',
    'license': 'LGPL-3',
    'depends': ['website', 'phone_validation'],
    'data': [
        'views/res_config_settings_views.xml',
        'views/website_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'aite_website_whatsapp/static/src/scss/whatsapp_button.scss',
        ],
    },
    'installable': True,
    'application': False,
}
