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

Incrément 2 (le code et le plan verrouillé ; les gestes réservés) :

* le plan de salle est l'écran de repos de chaque poste, toujours
  verrouillé : toucher une table demande le code à 4 chiffres (validé seul au
  quatrième chiffre), et tout retour au plan fait oublier l'employé (après
  « J'envoie », après l'encaissement, après 5 minutes sans toucher l'écran) ;
  plus d'écran « Déverrouiller la caisse » ni d'écran de veille ;
* ouvrir et fermer la caisse : le code d'une caissière (ouverture) ou d'un
  chef de salle (fermeture), vérifié par le serveur ; « Caisse ouverte par »
  et « Caisse fermée par » sur la fiche de session, écrits à l'ouverture et à
  la fermeture effectives ; un poste resté sur la caisse fermée n'est pas
  refusé quand un autre poste l'a ouverte ;
* encaisser (caissière et au-dessus ; le code est demandé sur « J'encaisse »),
  sortir ou entrer des espèces (chef de salle), imprimer le rapport
  (caissière), rembourser et mettre sur ardoise (manager) ;
* « J'envoie », « J'encaisse », « J'ouvre la caisse », « Entrée ou sortie
  d'espèces », « Retour » ; pas de « + » (vente sans table) sur la caisse.

Incrément 3 (la table) :

* une table libre demande le nombre de personnes, dans la même fenêtre que le
  code (huit gros boutons, « 9 et plus », pas de zéro) ; l'addition est
  enregistrée aussitôt, sans produit : la table est occupée sur tous les
  postes ; « 4 personnes » sur l'écran de commande change le nombre en deux
  touches ;
* « Ouverte par », « Heure d'ouverture » (horloge du serveur) et « Encaissée
  par » sur la fiche de l'addition ; une division garde les personnes sur
  l'origine (la part « 12B » en a 0), une réunion les additionne et garde
  l'heure la plus ancienne ;
* le journal des saisies : qui a ajouté chaque produit, à quelle heure
  (bouton « Saisies » de la fiche) ; ni la division ni la réunion ne sont
  des saisies ; ce qui est parti en cuisine ou au bar est tenu par le
  serveur ;
* un numéro tapé qui n'est pas sur le plan ouvre une table à ce nom ; le
  réglage « Autoriser la vente sans table » (décoché d'office, se change
  caisse fermée) fait paraître le « + » (caissière et au-dessus) ;
* « Addition », « Diviser l'addition », « Déplacer ou réunir », « Annuler la
  table » ; « Liste de prix » retirée de la caisse.

Incrément 4 (annuler ce qui est parti) :

* ce qui est parti en cuisine ou au bar est verrouillé : sur la caisse, ⌫
  retire librement ce qui n'est pas encore envoyé ; sous ce qui est parti, il
  ouvre une seule fenêtre — combien, le code d'un chef de salle (vérifié par
  le serveur), le motif, qui valide ; un chef de salle identifié ne retape pas
  son code ; la personne identifiée ne change pas ;
* « Annuler la table » et la corbeille de « Commandes » ouvrent directement
  cette fenêtre pour une table qui a des produits envoyés ; à la fermeture,
  « Annuler ces tables » annule toutes les tables encore ouvertes avec un seul
  motif ; ni la division ni la réunion ne sont des annulations ;
* le journal des annulations (Restaurant → Annulations : aujourd'hui par
  défaut, semaine, mois, année, « Sans code », par motif, par employé, par
  produit) ; ce qui arrive sans code n'est jamais refusé mais tracé
  (« Retrait sans code », « Annulation sans code ») ; cinq motifs posés
  d'office (Point de Vente → Configuration → Motifs d'annulation) ;
* le profil « Restaurant : lecture des rapports » pour le chef de salle : il
  lit les annulations sans aucun droit sur la caisse.

Incrément 5 (le plan en couleurs ; les produits épuisés) :

* sur le plan, chaque table dit son état d'un coup d'œil : gris = libre,
  vert = ouverte, orange = ouverte depuis plus que le délai de la caisse
  (60 minutes d'office, réglage « Délai avant l'orange (minutes) ») ; la durée
  s'écrit sous le numéro (« 35 min », « 1 h 05 »), comptée depuis l'ouverture
  de la table, même après un déplacement, une division ou une réunion ; elle
  est recalculée toutes les 30 secondes, sans toucher l'écran ; une légende
  en bas du plan ;
* un produit dont on suit le stock (« Suivre l'inventaire ») et qui n'en a
  plus n'est pas ajouté à une table — toucher de la carte, code-barres,
  quantité tapée au pavé, variante choisie : « Produit épuisé », avec ce
  qu'il faut faire ; ce qui est déjà parti sur les tables ouvertes est
  déduit, sur tous les postes ; une entrée de stock rend la vente aussitôt,
  sans recharger la caisse ; les plats sans suivi se vendent toujours ;
  hors connexion, la caisse vend (réglage « Refuser la vente des produits
  épuisés », coché d'office).

Incrément 6 (les rapports) :

* « Personnes et tables » (Point de Vente → Analyse) : pour la période choisie
  (aujourd'hui d'office, la semaine, le mois, l'année ou d'une date à une
  autre), le nombre de tables, de personnes, de ventes sans table, d'articles
  et le total encaissé, par jour, par session, par « Ouverte par » ou par
  « Encaissée par » ; une table divisée ne compte qu'une fois, une réunion
  additionne les personnes, les additions ouvertes ou annulées et les
  remboursements ne comptent pas ;
* le rapport de fermeture (« Imprimer le rapport » de la caisse, rapport de
  session de la gestion) donne aussi les tables, les personnes, les ventes
  sans table et les annulations de la session, avec leur motif et qui les a
  autorisées.

Aucune dépendance au socle hôtelier.
""",
    'version': '18.0.1.0.5',
    'author': "AITE Consulting",
    'website': "https://aiteconsulting.com",
    'category': 'Point of Sale',
    'license': 'LGPL-3',
    'depends': ['pos_restaurant', 'pos_hr'],
    'data': [
        'security/restaurant_security.xml',
        'security/ir.model.access.csv',
        'data/restaurant_motif_data.xml',
        'views/hr_employee_views.xml',
        'views/res_config_settings_views.xml',
        'views/pos_order_views.xml',
        'views/pos_session_views.xml',
        'views/restaurant_saisie_views.xml',
        'views/restaurant_annulation_views.xml',
        'views/restaurant_motif_views.xml',
        'views/report_saledetails.xml',
        'views/restaurant_menus.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': ['aite_pos_restaurant/static/src/**/*'],
        'web.assets_tests': ['aite_pos_restaurant/static/tests/tours/**/*'],
    },
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': False,
}
