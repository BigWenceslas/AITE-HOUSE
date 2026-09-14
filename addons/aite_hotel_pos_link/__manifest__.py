# -*- coding: utf-8 -*-
{
    'name': "AITE — Note de chambre (POS → folio)",
    'summary': "Report des consommations restaurant & boutique au folio "
               "du séjour : moyen de paiement « Note de chambre » au "
               "POS, rattachement automatique au folio ouvert du client, "
               "file de rattachement manuel pour les cas ambigus.",
    'description': """
AITE Note de chambre (adaptation A1)
====================================

Dans la continuité du module **Crédit clients v2** (en production) : au
POS restaurant ou boutique, le serveur encaisse sur le moyen de paiement
« Note de chambre ». Le montant est alors **reporté automatiquement sur
le folio ouvert du client** (ligne de service du PMS), réglé au départ
avec le séjour.

Sécurité du rattachement :

* client identifié + **un seul** folio ouvert → report automatique,
  idempotent (une commande ne crée jamais deux lignes) ;
* aucun folio, plusieurs folios ou client manquant → la commande entre
  dans la file **« Notes de chambre en attente »**, où la réception
  choisit le folio et valide — rien ne se perd, rien ne se devine.

L'article de report est paramétrable (Réglages) ; un article
« Consommation POS » est fourni.
""",
    'author': "AITE CONSULTING",
    'website': "https://aiteconsulting.com",
    'category': 'Industries',
    'version': '18.0.1.0.0',
    'license': 'LGPL-3',
    'depends': ['point_of_sale', 'aite_hotel_management'],
    'data': [
        'security/ir.model.access.csv',
        'data/product_data.xml',
        'views/pos_payment_method_views.xml',
        'views/roomcharge_pending_views.xml',
        'views/res_config_settings_views.xml',
        'views/roomcharge_menus.xml',
    ],
    'installable': True,
    'application': False,
}
