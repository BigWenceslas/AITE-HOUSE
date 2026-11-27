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
  autorisées ;
* la fenêtre de fermeture dit « Entrée ou sortie d'espèces », comme le menu
  de la caisse, et « 1 commande » au singulier (18.0.1.0.6).

Table divisée (18.0.1.0.11) :

* « Addition » sur une table divisée (l'origine, une part ou la part d'une
  part) imprime toutes les additions encore ouvertes de la table, un ticket
  par addition, dans l'ordre de création ; sans imprimante, une seule
  fenêtre les montre empilées (nom, lignes, total) et « J'imprime les
  additions » les imprime depuis le navigateur ; une addition payée n'y
  figure plus ; sans division, rien ne change ; une part portée sur une
  autre table devient l'addition de cette table ; le groupe tient même
  quand une part intermédiaire est payée et la caisse rechargée (champ
  « Table divisée ») ; une imprimante en panne en cours de route ne fait
  reprendre que les additions pas encore imprimées.

Partager à parts égales (18.0.1.0.12) :

* sur l'écran de paiement, « Partager à parts égales » ouvre « Combien de
  personnes paient ? » : gros boutons 2 à 8 et « Plus » jusqu'à 20, le
  nombre de personnes de la table présélectionné (2 s'il y en a moins), la
  phrase « Chaque personne paiera 33 333 FCFA ; le dernier paie ce qui
  reste. » ;
* un bandeau dit la part en cours (« Part 1 sur 3 : 33 333 FCFA ») : toucher
  un mode de paiement crée une ligne du montant de la part, la dernière est
  exactement le reste dû (100 000 en 3 : 33 333, 33 333, 33 334) ; avec des
  paiements déjà faits, le reste dû est partagé et le bandeau le dit ;
  supprimer une ligne (ou la ramener à 0) remet le compteur en cohérence ;
  « Annuler le partage » rend le comportement habituel, tant que toutes les
  parts ne sont pas encaissées ;
* monnaie : une part intermédiaire ne dépasse jamais le reste dû ; si la
  caissière tape ce que la personne donne en espèces (50 000 pour 33 333),
  le bandeau dit « Monnaie à rendre : 16 667 FCFA » et la ligne revient à la
  part au mode suivant ou à la validation (la caisse enregistre ce qui reste
  dans le tiroir) ; sur la dernière part, la monnaie d'Odoo, comme
  d'habitude ;
* arrondi des espèces : chaque part intermédiaire est un multiple de
  l'arrondi, les pas restants vont un chacun aux dernières personnes (1 000
  en 7 au pas de 25 : 125, 125, 150 × 5) ; la dernière part en espèces est
  arrondie par Odoo et le bandeau dit les deux montants ;
* revenir au panier puis au paiement retrouve le partage, tant que le total
  (produits, pourboire) n'a pas changé ; sinon il se refait d'un toucher ;
* le ticket dit « Partagée en 3 parts égales » sous les paiements (champ
  « Partagée à parts égales » de l'addition, gardé pour la réimpression ; le
  serveur ne garde qu'un nombre possible) ; l'addition reste une seule
  commande (stock, cuisine, rapports, personnes, Ouverte par / Encaissée
  par inchangés) ; une table divisée se partage addition par addition ;
  une caisse hors mode n'a pas le bouton.

Bons de préparation et notes (18.0.1.0.13) :

* « Nombre d'exemplaires du bon » sur chaque imprimante de préparation (1
  d'office, de 1 à 5), avec la phrase « ce qui va se passer » ; un bon qui
  porte de nouveaux plats (même mêlés d'annulations) sort en autant
  d'exemplaires identiques, marqués « Exemplaire 1/3 » à « Exemplaire 3/3 »
  (rien s'il n'y en a qu'un) ; un bon fait seulement d'annulations, de notes
  ou de la note générale sort en un exemplaire ; une imprimante qui ne
  répond pas n'est pas relancée pour ses autres exemplaires et une seule
  alerte, en français, la nomme ; le réglage est lu par la caisse au
  démarrage ;
* un envoi donne un seul bon par imprimante, en français : « Sur place »,
  « Par : Awa », « Table 7 », puis « Nouveau », « Annulé », « Note » (note
  changée d'un plat déjà parti) et « Note générale » (plus de « New »,
  « Cancelled », « Message », ni de « Tableau 7 ») ;
* « Note cuisine » sur une ligne en partie envoyée (3 poulets partis, un 4ᵉ
  saisi) : la note va au 4ᵉ, sur une ligne à part, sans rouvrir la fenêtre
  des accompagnements ; l'addition garde sa quantité et son montant, et le
  journal des saisies compte 4 poulets (la coupure est un déplacement) ;
* une note posée sur un plat parti puis une unité de plus au pavé : le bon
  dit « Nouveau 1 Poulet DG » et « Note 3 Poulet DG » (Odoo écrivait
  « Nouveau 3 ») ; une note effacée sur un plat parti : « Note retirée :
  sans glaçon » ;
* « Ignorer » dans la fenêtre de note ne change plus rien (ni la note du
  plat, ni la note générale, ni la ligne) ; pour effacer une note, on vide
  le champ et on touche « Appliquer » ;
* « Note au client » s'ouvre sur une ligne déjà envoyée (elle plantait) ;
  elle ne coupe jamais la ligne : elle ne va pas en cuisine ;
* une note générale tapée seule est imprimée : sur les imprimantes qui ont
  déjà reçu un plat de la table, ou sur toutes si aucune n'en a reçu ; elle
  reste rappelée sous les nouveaux plats, comme avant ;
* la note générale (consigne pour la cuisine) ne figure plus sur l'addition,
  le ticket ni l'écran tourné vers le client ; la note au client, si ;
* « J'envoie » et la notification « Envoyé : … » disent « Note générale »
  (plus « Message ») ; si une imprimante de préparation n'a pas répondu, la
  notification dit quel bon n'est pas sorti ; une erreur au rendu d'un bon
  donne la même alerte « Bon non imprimé » qu'une imprimante en panne.

Les familles de la carte (18.0.1.0.14) :

* « J'envoie » imprime chaque plat sur l'imprimante de son poste (chaud,
  froid, bar, pizza…) d'après les familles cochées sur l'imprimante de
  préparation ; cocher une famille (« Bar ») couvre toutes ses sous-familles
  (vins blancs, bières…) ;
* nouvelle case « Prend tout ce qu'aucune autre imprimante ne prend » sur
  l'imprimante (l'imprimante « Autre »), avec sa phrase « ce qui va se
  passer » : un plat dont aucune autre imprimante de la caisse ne prend la
  famille, ou sans famille, sort sur cette imprimante, jamais perdu ; les
  annulations et la note générale suivent le même chemin ; une seule
  imprimante « Autre » par caisse (message clair sinon) ; les exemplaires et
  l'alerte de panne de 18.0.1.0.13 restent ; la case n'agit qu'au service à
  table contrôlé ; pourboire, remises, récompenses et ligne mère d'un menu
  ne partent jamais seuls sur « Autre » ;
* sans imprimante « Autre », le formulaire de l'imprimante et les réglages
  de la caisse (Imprimantes de préparation) listent les familles de la carte
  qu'aucune imprimante ne prend, et les produits sans famille (le cadre suit
  la saisie ; hors service à table contrôlé, il reste malgré l'« Autre » et
  le dit ; une caisse aux familles restreintes ne cite que ce qu'elle vend) ;
* envoi direct depuis la tablette, sans boîtier IoT, aux Epson en Wi-Fi
  (TM-m30III…) : le module dépend de pos_epson_printer (type « Epson » et
  adresse IP sur l'imprimante) ; « J'envoie » imprime sans aucune fenêtre ;
  en https, l'alerte « Bon non imprimé » dit d'accepter le certificat de
  l'imprimante (https://<IP>) ;
* réglage de la caisse « Grouper les produits par famille sur l'addition et
  le ticket » (décoché d'office) : l'addition (y compris les additions d'une
  table divisée), le ticket final et sa réimpression rangent les produits
  sous leur famille de niveau 1, dans l'ordre de la caisse, chacune suivie
  de « Sous-total Plats : 21 000 FCFA » ; produits sans famille sous
  « Autres » ; pourboire et remise globale ensuite, sans rubrique ni
  sous-total ; total, taxes, paiements, partage à parts égales et note au
  client inchangés ; le ticket final sort au paiement si « Impression
  automatique du reçu » est coché.

Aucune dépendance au socle hôtelier.
""",
    'version': '18.0.1.0.14',
    'author': "AITE Consulting",
    'website': "https://aiteconsulting.com",
    'category': 'Point of Sale',
    'license': 'LGPL-3',
    # pos_epson_printer : les tablettes impriment les bons directement sur les
    # imprimantes Epson du réseau (Wi-Fi), sans boîtier IoT (18.0.1.0.14).
    'depends': ['pos_restaurant', 'pos_hr', 'pos_epson_printer'],
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
        'views/pos_printer_views.xml',
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
