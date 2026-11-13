# -*- coding: utf-8 -*-
{
    'name': "AITE — Chat du site web",
    'summary': "Chat en direct toujours joignable : vos visiteurs vous écrivent "
               "même quand personne n'est connecté, et vous recevez leurs "
               "messages dans Discuss et en notification push.",
    'description': """
AITE — Chat du site web
=======================

S'appuie sur le chat en direct d'Odoo (Live Chat) et le rend **toujours
joignable** : la bulle de chat reste affichée sur le site même quand aucun
opérateur n'est connecté. Le visiteur écrit, la conversation est confiée à
un opérateur du canal, et chaque message arrive :

* dans Discuss (Odoo web) ;
* en notification push du navigateur ;
* en notification de l'application mobile Odoo (Enterprise).

En plus :

* message d'absence automatique au premier message du visiteur quand
  l'opérateur n'est pas en ligne (une fois par conversation) ;
* adresse e-mail et téléphone saisis par le visiteur repérés et affichés à
  l'opérateur ;
* réponse par e-mail : quand le visiteur a quitté le site, les réponses de
  l'opérateur lui sont envoyées par e-mail (au plus un e-mail toutes les
  10 minutes) ;
* canal « Chat du site » créé et rattaché au site à l'installation ;
* la bulle et le bouton WhatsApp (module aite_website_whatsapp) ne se
  chevauchent pas.

Réglages : Site web → Configuration → Paramètres → Live Chat.
""",
    'author': "AITE CONSULTING",
    'website': "https://aite-consulting.com",
    'category': 'Website/Live Chat',
    'version': '19.0.1.0.0',
    'license': 'LGPL-3',
    'depends': ['website_livechat'],
    'data': [
        'data/mail_template_data.xml',
        'views/im_livechat_channel_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'aite_website_livechat/static/src/scss/livechat_button.scss',
            'aite_website_livechat/static/src/frontend/**/*',
        ],
        'im_livechat.assets_embed_core': [
            'aite_website_livechat/static/src/embed/common/**/*',
        ],
        'web.assets_backend': [
            'aite_website_livechat/static/src/core/web/**/*',
        ],
        'web.assets_tests': [
            'aite_website_livechat/static/tests/tours/**/*',
        ],
    },
    'post_init_hook': '_aite_post_init_hook',
    'installable': True,
    'application': False,
}
