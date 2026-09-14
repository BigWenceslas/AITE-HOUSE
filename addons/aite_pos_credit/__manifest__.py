# -*- coding: utf-8 -*-
{
    'name': "AITE — Crédit clients (Ardoises POS & Ventes)",
    'summary': "Vente à crédit (ardoise) pour le Point de Vente ET le "
               "module Ventes — encours "
               "client, remboursements Mobile Money / espèces, écritures "
               "comptables 411, tableau de bord de recouvrement.",
    'description': """
AITE POS Crédit
===============

Gestion de la **vente à crédit (ardoise)** pour Odoo Point of Sale, pensée
pour le commerce de détail (bar, cave, restauration) en contexte camerounais.

Principe
--------
Un client connu peut consommer au POS et **payer plus tard**. La vente crée
une *ardoise* (dette client) adossée à la comptabilité client (compte 411).
Le client rembourse ensuite, partiellement ou totalement, en **Mobile Money**
(MTN MoMo / Orange Money) ou en **espèces**.

Intégration POS & comptable
---------------------------
* Bouton **« Mettre sur ardoise »** dans l'écran de paiement POS, adossé à
  une méthode de paiement native de type *pay_later*.
* Création automatique de l'ardoise à la clôture de la commande.
* **Écritures comptables 411** : la mise sur ardoise porte l'encours au
  compte client ; chaque remboursement passe une écriture
  (débit caisse/banque / crédit client) rapprochée de la créance.
* Tableau de bord de recouvrement : encours, débiteurs, taux de
  recouvrement, balance âgée (aging), top débiteurs.

Pas de limite de crédit dans cette version (le caissier peut toujours mettre
sur ardoise). La limite/blocage et les relances automatiques sont prévues en
évolution.

Compatible Odoo 18 Enterprise.
""",
    'author': "AITE CONSULTING",
    'website': "https://aiteconsulting.com",
    'category': 'Point of Sale',
    'version': '18.0.2.0.2',
    'license': 'LGPL-3',

    'depends': [
        'base',
        'product',
        'point_of_sale',
        'sale',
        'account',
    ],

    'data': [
        'security/pos_credit_security.xml',
        'security/ir.model.access.csv',
        'data/pos_credit_data.xml',
        'views/pos_credit_views.xml',
        'views/sale_order_views.xml',
        'views/pos_credit_payment_views.xml',
        'views/res_partner_views.xml',
        'views/res_config_settings_views.xml',
        'wizard/pos_credit_repay_wizard_views.xml',
        'views/pos_credit_dashboard_actions.xml',
        'views/pos_credit_menus.xml',
    ],

    'assets': {
        'web.assets_backend': [
            'aite_pos_credit/static/src/scss/pos_credit_dashboard.scss',
            'aite_pos_credit/static/src/js/services/utils.js',
            'aite_pos_credit/static/src/js/services/chartjs_loader.js',
            'aite_pos_credit/static/src/js/components/kpi_card.js',
            'aite_pos_credit/static/src/js/views/dashboard_view.js',
            'aite_pos_credit/static/src/js/dashboard.js',
            'aite_pos_credit/static/src/xml/dashboard.xml',
        ],
        # Bundle chargé dans l'interface POS (frontend).
        'point_of_sale._assets_pos': [
            'aite_pos_credit/static/src/scss/pos_credit_pos.scss',
            'aite_pos_credit/static/src/js/pos/payment_screen_button.js',
            'aite_pos_credit/static/src/js/pos/payment_screen_button.xml',
        ],
    },

    'post_init_hook': 'post_init_hook',

    'installable': True,
    'application': False,
    'auto_install': False,
}
