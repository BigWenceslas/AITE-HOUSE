# -*- coding: utf-8 -*-
{
    'name': "AITE — Achats & Fournisseurs (Tableau de bord)",
    'summary': "Tableau de bord des achats : dettes fournisseurs (401) avec "
               "balance âgée et échéancier, créances fournisseurs (409) — "
               "consignes, avoirs, acomptes —, performance fournisseurs "
               "(OTIF, dépendance), commandes & réceptions, variations de "
               "prix d'achat. Alertes configurables.",
    'description': """
AITE Achats & Fournisseurs
==========================

Tableau de bord OWL pour Odoo 18 Achats, pensé pour le commerce de détail
(bar, cave, restauration) : piloter la relation fournisseurs dans les deux
sens — ce que vous devez (401) et ce qu'on vous doit (409).

Onglets
-------
* **Tableau de bord** — achats de la période, dette fournisseurs, échéances
  imminentes, DPO ; retards, créances 409, OTIF, commandes en cours ;
  achats par fournisseur, achats vs paiements 6 mois, balance âgée, top
  produits achetés.
* **Fournisseurs** — achats, part (risque de concentration), encours dû,
  retards, délai moyen de livraison, OTIF, badge d'alerte.
* **Dettes & échéancier** — balance âgée 5 tranches (non échu / 1-30 /
  31-60 / 61-90 / +90 j de retard), décaissements des 6 prochaines
  semaines, factures ouvertes triées par urgence.
* **Avoirs & consignes** — créances fournisseurs : consignes d'emballages
  (casiers — suivi dédié), avoirs à déduire, acomptes/soldes débiteurs.
* **Commandes & réceptions** — journal des commandes, retards de
  livraison, réceptions complètes ou non, OTIF strict.
* **Prix & variations** — dérive des prix d'achat, impact annuel estimé,
  indice base 100 des produits clés.

Alertes configurables (Réglages ou modal ⚙, responsables Achats) :
fenêtre d'alerte avant échéance, tolérance de retard de livraison, seuil
de dépendance fournisseur, seuil de hausse de prix.

Définitions
-----------
* **OTIF** : livré à l'heure ET complet (strict) — un badge toléré
  distinct signale les petits retards sous le seuil.
* **DPO** : encours fournisseurs / factures de la période × jours.
* **Créances 409** : soldes débiteurs du compte fournisseurs (paiements
  non lettrés, avoirs) + consignes suivies à part.

Compatible Odoo 18. Dépend d'Achats (purchase) et Comptabilité (account).
""",
    'author': "AITE CONSULTING",
    'website': "https://aiteconsulting.com",
    'category': 'Inventory/Purchase',
    'version': '18.0.1.0.2',
    'license': 'LGPL-3',

    'depends': [
        'base',
        'purchase',
        'account',
        'web',
    ],

    'data': [
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'views/purchase_deposit_views.xml',
        'views/purchase_dashboard_actions.xml',
        'views/purchase_dashboard_menus.xml',
    ],

    'assets': {
        'web.assets_backend': [
            'aite_purchase_dashboard/static/src/scss/purchase_dashboard.scss',
            'aite_purchase_dashboard/static/src/js/services/utils.js',
            'aite_purchase_dashboard/static/src/js/services/chartjs_loader.js',
            'aite_purchase_dashboard/static/src/js/components/kpi_card.js',
            'aite_purchase_dashboard/static/src/js/views/purchase_dashboard_view.js',
            'aite_purchase_dashboard/static/src/js/dashboard.js',
            'aite_purchase_dashboard/static/src/xml/dashboard.xml',
        ],
    },

    'installable': True,
    'application': False,
    'auto_install': False,
}
