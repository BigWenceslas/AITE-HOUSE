# -*- coding: utf-8 -*-
"""Tutoriel 4 — Bar et restaurant sur la note de chambre.

Trois personnages, un par temps fort, chacun annoncé par la pastille du haut :
la direction (demo.POSTES['direction'], Danielle Eyenga) fait la mise en place
une fois (Point de Vente → Configuration → Modes de paiement, réservé au
responsable du point de vente) ; le caissier du bar (demo.POSTES['caisse'],
Hervé Tchakounté) encaisse ; la réception (demo.POSTES['reception'], Mireille
Ateba) traite le folio et la file d'attente (menu réservé à
aite_hotel_management.group_hotel_user, aite_hotel_pos_link/views/
roomcharge_menus.xml:3-8). Public visé du guide : « Caissiers (restaurant &
boutique), réception » (docs/guides/AITE_Guide_Note_de_chambre.pdf p.1).
Le titre reprend l'annonce du tutoriel 3 (t03_folio.py, TUTORIEL['cta']
['suivant']).

Conditions du monde rejoué (aite_hotel_pos_link 18.0.1.0.2, aite_pos_credit
18.0.2.0.5, livraison 4) :

- le caissier n'a que son profil de caisse (demo.caisse, APPS_PROFIL['caisse'],
  sans « Hôtel ») : le report au folio — recherche du folio ouvert, ligne de
  folio, note en attente — est une écriture technique en sudo()
  (aite_hotel_pos_link/models/pos_order.py:143-228). Corrigé (ECARTS n° 10) :
  avant 18.0.1.0.1, il fallait donner au caissier le profil « Réception »
  pour que le ticket se synchronise ; ce contournement et sa bulle ont été
  retirés. Symétrique depuis la livraison 4 : la réception tranche la file
  sans droit sur la caisse (lecture du ticket en sudo(),
  models/roomcharge_pending.py:81-84) ;
- aite_pos_credit est installé, comme au tutoriel 10 : application « POS
  Crédit » dans la barre de la direction, case « Vente à crédit (ardoise) »
  avec son libellé dans le groupe des réglages, suivie de la phrase « Case
  cochée : chaque ticket réglé avec ce mode ouvre une ardoise au nom du
  client (POS Crédit → Ardoises). », visible avant de cocher (aite_pos_credit/
  views/res_config_settings_views.xml:15-24 ; corrigé, ECARTS n° 65 : la case
  était injectée sans libellé après le nom du mode), mode « Ardoise client »
  et bouton « Mettre sur ardoise » à la caisse. Les deux modules posent leur
  case « après Journal » ; la vue d'aite_pos_credit, d'identifiant plus
  petit, s'applique la première, et « Note de chambre » s'insère donc devant
  elle (ordre relevé sur aite_t_final, aite_dev et aite_fresh :
  Paiement en ligne, Identifier le client, Journal, Note de chambre, Vente à
  crédit (ardoise), la phrase). Corrigé (ECARTS n° 17) : seul le mode
  coché « Vente à crédit » ouvre une ardoise, jamais « Note de chambre »,
  même cochée par erreur (aite_pos_credit/models/pos_payment_method.py:
  24-39, static/src/js/pos/payment_screen_button.js:35-38) — la case reste
  décochée à l'étape 1, et la consommation n'est réclamée qu'une fois, sur
  le folio (étape 4). aite_pos_analytics (« Analyse AITE ») est installé :
  depuis la livraison 4, c'est une section du menu « Analyse », plus une
  entrée de la barre (ecrans.MENUS_MUK['point_de_vente']) ;
- pas de TVA, comme aux tutoriels 1 et 3 et au chapitre 1 de la
  présentation (en-tête de t03_folio.py : « aucun taux n'est livré par les
  modules ») : la nuitée prend les taxes de l'article du type de chambre
  (aite_hotel_management/models/hotel_folio.py:253-278), l'article est créé
  sans taxe explicite (hotel_room.py:126) ; les articles du bar non plus,
  d'où l'absence de la ligne « Taxes » au ticket (point_of_sale/static/src/
  app/generic_components/order_widget/order_widget.xml:19-27, affichée
  seulement s'il y a des groupes de taxes).

Le séjour : Brigitte Essomba, chambre 202 [CFT] Confort du 13 au 16/10/2026
(t02_planning.py, SEJOURS), folio FOL/2026/0210 / RES/2026/0210 resté
« Ouvert » le 16/10 avec 198 000 FCFA TTC, 100 000 encaissés, 98 000 dus
(t03_folio.py, FOLIOS) — les 13 500 FCFA du bar du 14/10 y sont donc compris,
comme le massage du 15/10 (demo.CRENEAU_MASSAGE, CRN/2026/0158, 27 000 FCFA,
t09_espaces.py) ; le 14/10 au soir, ici, le folio vaut 157 500 FCFA.
Le folio d'Estelle Ngono (FOL/2026/0214) n'est pas utilisé : au tutoriel 3
son folio de départ n'a aucune ligne du bar. Les notes en attente datent du
16/10 au soir, après la liste des folios du tutoriel 3 : Martin Ebode
(FOL/2026/0209, séjour du 14 au 17/10, « Arrivé », demo.ARRIVEES) a confirmé
l'après-midi une réservation de novembre (folio FOL/2026/0227, ouvert dès la
confirmation, hotel_reservation.py:374-390), juste après une autre
réservation confirmée dans l'après-midi, au nom d'un autre client
(FOL/2026/0226 ; la série continue en FOL/2026/0228, t05_taxe_sejour.py) ;
Sylvie Mbarga (FOL/2026/0207 « Soldé », t03_folio.py, FOLIOS) et Boris
Ndzana (client du bar, t11_fidelite.py) n'ont aucun folio ouvert. Le
report automatique compte tout folio ouvert du client, séjour à venir
compris (pos_order.py:160-178) : d'où le motif « 2 folios ouverts » de
Martin (point laissé à trancher, ECARTS.md, « Restent à trancher »). « Folio choisi », lui, ne propose que les
séjours commencés — client arrivé, ou parti sans facture — et seulement ceux
du client du ticket s'il en a (roomcharge_pending.py:37-69, domaine
roomcharge_pending_views.xml:51-56, tests/test_room_charge.py:548-564) :
pour Martin, FOL/2026/0209 seul : ni sa réservation de novembre ni le
0226 (confirmés, pas commencés ; le 0226 n'est pas à son nom) n'y sont. Il
s'affiche « FOL/2026/0209 — Martin Ebode » (contexte aite_folio_with_partner,
roomcharge_pending.py:96-114). Corrigé (ECARTS n° 55) : la liste proposait
tous les folios ouverts de tous les clients, par leur seule référence, et
Mireille devait taper « 0209 ».

Tickets : la caisse du bar a ouvert le 04/05/2026 et compte environ 1 350
tickets au 13/10 (environ 8,3 par jour : 108 du 01 au 13/10, t12_ventes.py,
TICKETS ; 1 440 tickets toutes caisses depuis le 04/05, t12_ventes.py,
TOUT) ; le dîner de Brigitte, le 14/10 au soir, est donc « Bar de la
terrasse/1360 », 8e ticket de la session du jour (00135 : suivi 508,
pos_order.py:58-60), et la
note de Martin Ebode du 16/10 à 22:41 la /1377. Restaurant (environ 80
tickets) et Boutique (une vingtaine) vendent peu : Restaurant/0083 et
Boutique/0018 le 16/10.

Sources des libellés (relevés mot pour mot) :

1. Le mode de paiement — odoo18/addons/point_of_sale/views/
   pos_payment_method_views.xml:7-24 (fiche : nom, « Identifier le client »
   split_transactions, « Journal » requis sauf si l'on identifie le client
   :19-20, « Intégration », image) ; i18n/fr.po : « Mode » :4284-4285,
   « par ex. Espèces » :9547-9548, « Identifier le client » :3518-3519,
   « Laisser vide pour utiliser le compte débiteur du client » :4016-4017,
   « Intégration » :3641-3642, « Non requis » :4601-4602, « Modes de
   paiement » :5276-5277, menus « Tableau de bord », « Commandes »,
   « Produits », « Analyse », « Configuration » :2483, :5067, :6320, :6631,
   :2049 ; « Paiement en ligne » : pos_online_payment/i18n/fr.po:168-169 ;
   barre du Point de Vente de la direction : ecrans.MENUS_MUK['point_de_vente']
   (« Analyse AITE » est une section du menu « Analyse » depuis la livraison 4,
   aite_pos_analytics/views/pos_analytics_menus.xml:16-20).
   La case ajoutée par le module, juste après « Journal », et son infobulle :
   aite_hotel_pos_link/views/pos_payment_method_views.xml:8-10,
   models/pos_payment_method.py:9-13 (« Note de chambre », « Les
   encaissements sur ce moyen sont reportés au folio du séjour du client (ou
   en file d'attente si ambigu). »). Puis la case d'aite_pos_credit et sa
   phrase en gris (text-muted, sur toute la largeur du groupe) :
   aite_pos_credit/views/res_config_settings_views.xml:15-24,
   models/pos_payment_method.py:17-22 (« Vente à crédit (ardoise) », avec
   infobulle) ; la consigne « Laissez le journal vide… » ne s'affiche que
   case cochée : elle n'est pas montrée. Ordre des cases : relevé sur la base
   (voir « Conditions »). Mise en page et infobulle noire : capture en
   lecture seule de la base MuK (Point de Vente → Configuration → Modes de
   paiement → Note de chambre). Base mono-société, comme celle du client
   (DESIGN.md, « La base est mono-société » ; res_users.py:1907-1914) : pas
   de « Société », réservé à base.group_multi_company
   (pos_payment_method_views.xml:23).
   Applications de la direction : APPS_PROFIL['direction'] (avec « POS Crédit »).
2. La caisse — odoo18/addons/point_of_sale/static/src/app : écran de vente
   (ecrans.pos_produits, captures ref_muk/611 et 612) ; unité « Unité(s) »
   (uom/i18n/fr.po:376-379, nom traduit de uom.product_uom_unit) ; recherche
   « Rechercher des produits… » (point_of_sale/i18n/fr.po:6945-6946) ;
   bouton Client qui prend le nom du client screens/product_screen/
   control_buttons/select_partner_button/select_partner_button.xml:4-7 ;
   fenêtre des clients screens/partner_list/partner_list.xml:5-56 et
   partner_line/partner_line.xml:46-86 (« Créer », « Recherche des
   clients... », « Nom », « Adresse », « Contact », « Rechercher plus »,
   « Ignorer » : point_of_sale/i18n/fr.po:2261-2262, :6921-6922, :4363-4364,
   :721-722, :2170-2171, :6939-6940, :2768-2769) ; numéro de commande
   « <caisse>/<4 chiffres> » : models/pos_config.py:476-480 ; numéro de
   suivi à trois chiffres : models/pos_order.py:58-60. Adresses des clients :
   celles du tutoriel 11 (t11_fidelite.py, PROCHES) ; téléphones dans la
   plage de fiction « +237 6 00 00 00 xx », ceux de t10_ardoises.py
   (TELEPHONES) pour Armand Mvogo, Boris Ndzana, Brigitte Essomba et Carine
   Owona, demo.CLIENT_TEL pour Estelle Ngono, +33 6 39 98 21 47 pour Claire
   Durand (série).
3. Le paiement — screens/payment_screen/payment_screen.xml:27-140 (modes,
   « Client » qui prend le nom du client :100-107, « Facture », « Retour »,
   « Valider ») ; icône de chaque mode selon son type, espèces, banque ou
   payer plus tard : payment_screen.js:413-421 (money.png, card-bank.png,
   pay-later.png, redessinées) ; payment_status/payment_status.xml:4-22
   (« Veuillez sélectionner un mode de paiement », « Restant ») ;
   l'avertissement d'un mode « payer plus tard » sans facture, simple
   notification qui ne bloque pas la validation : payment_screen.js:113-125
   et fr.po:8607-8612, :9072-9073 (« Avertissement », « Pour assurer le suivi
   des soldes dûs, générez une facture ou téléchargez l'application
   comptabilité. ») ; « Client requis » si le client manque :
   payment_screen.js:424-439, fr.po:2442-2443. Aspect : ref_muk/613, 614.
4. Le folio — aite_hotel_management/views/hotel_folio_views.xml:31-128
   (« Encaisser », « Générer la facture » ; « Annuler » et « Recalculer la
   taxe de séjour » sont réservés au responsable :43-46 et
   aite_city_tax/views/hotel_folio_views.xml:17-24, la réception ne les voit
   pas ; « Règlements », « Séjour », « Montants », onglets, colonnes, note
   grise ; le champ « Hôtel » du groupe « Séjour », réservé à
   base.group_multi_company :73-74, est absent sur la base mono-société,
   voir le point 1) ; models/hotel_folio.py:29-118 et :398-440 (libellés, états
   Ouvert / Facturé / Soldé, types Nuitée / Service) ; libellé de nuitée
   « Nuitée 202 (Confort) — 13/10/2026 → 16/10/2026 », dates locales au
   format jj/mm/aaaa, ligne datée de l'arrivée : models/hotel_folio.py:253-276
   et hotel_reservation.py:193-195 (_fmt_local_date ; corrigé, ECARTS n° 37 et
   56) ; « Arrivé » : hotel_reservation.py:134 ; aite_city_tax :
   ligne « Taxe de séjour — 3 nuitée(s) × personne (3 ★, Cameroun) », sans
   TVA, et montant « Taxe de séjour » models/hotel_folio.py:10-13, :56-60,
   :119-160, seul champ du groupe « Montants » à porter le « ? » d'aide
   (help « Montant collecté pour le compte de l'État sur ce séjour. »,
   :56-60 ; les montants du socle n'ont pas de help,
   aite_hotel_management/models/hotel_folio.py:71-98 ;
   odoo18/addons/web/static/src/views/form/form_label.js:39-49,
   form_label.xml:6) ; barre de la réception ecrans.MENUS_MUK['hotel_reception']
   (« Réception », anciennement « Front Desk », hotel_menus.xml:18-25) ;
   menu Facturation → Folios hotel_menus.xml:69-79 ; ordre des
   folios « create_date desc » (hotel_folio.py:29) : FOL/2026/0210 est le
   12e des 14 folios « Avec solde dû » du tutoriel 3 (t03_folio.py, FOLIOS et DUS),
   d'où « 12 / 14 ». La ligne reportée :
   aite_hotel_pos_link/models/pos_order.py:76-141 (type service, quantité 1,
   une ligne par jeu de taxes du ticket, en HT avec ses taxes — ECARTS n° 18,
   corrigé dans 18.0.1.0.1 ; ticket sans taxe : une seule ligne, HT = TTC,
   colonne Taxes vide) et :212-222 (libellé « POS <commande> », date du jour).
   Aspect : ref_muk/029.
5. La file — aite_hotel_pos_link/views/roomcharge_pending_views.xml:3-24
   (liste sans « Nouveau », lignes orange « À rattacher », somme du montant
   sans libellé en pied, colonne « Reçue le » :9-11 — corrigé, ECARTS n° 42 :
   « Created on » —, « Folio choisi » vide tant que rien n'est choisi),
   :64-77 (action, filtre « À rattacher » par défaut ; l'aide de l'écran vide,
   réécrite, ECARTS n° 48, n'apparaît pas : la file n'est pas vide), :78-89
   (recherche) ; models/roomcharge_pending.py:12-50 (ordre « create_date
   desc », « Commande POS », « Client », « Montant », « Motif », « Folio
   choisi », « À rattacher » / « Rattachée ») ; motifs :
   models/pos_order.py:174-178 (« Aucun folio ouvert », « %(n)s folios
   ouverts »). Aspect : ref_muk/048.
6. Le rattachement — roomcharge_pending_views.xml:25-63 (fiche sans
   « Nouveau », create="0" :29-31 ; « Rattacher au folio », statusbar,
   « Folio choisi » limité aux folios proposés, sans création
   (options no_create), verrouillé une fois rattachée) ; fil d'Ariane au
   numéro du ticket : champ name « Ticket » lié à la commande
   (roomcharge_pending.py:16-20 ; corrigé, ECARTS n° 55 : la fiche
   s'intitulait « aite.roomcharge.pending,12 ») ; models/
   roomcharge_pending.py:71-93 (action_resolve) ; liste déroulante d'Odoo :
   odoo18/addons/web/static/src/views/fields/relational_utils.js:313-385
   (name_search sur le domaine du champ ; « Recherche avancée... » dès qu'il
   y a un résultat ; ni « Créer "%s" », ni « Créer et modifier... », ni
   « Commencer à écrire... » avec no_create : many2one_field.js:377-384) et
   web/i18n/fr.po:5713-5714 (« Recherche avancée... »). Aspect : ref_muk/048-…-fiche.png.

Sources des affirmations :

- accroche : « Un client en séjour ne doit pas sortir sa monnaie à chaque
  repas » (guide p.1 §1) ; ticket recopié à la main : sans report, le folio
  invite à « ajouter librement des lignes de service (restaurant,
  blanchisserie, minibar…) » (hotel_folio_views.xml:122-128) ; « Moitié
  espèces, moitié note de chambre » (tests/test_room_charge.py:196-205,
  guide p.1 §3) ; « Deux séjours au même nom » (guide p.2 FAQ) ; mauvais
  séjour : « le système ne devine jamais » (guide p.2 FAQ, pos_order.py:
  62-75). Chacune est résolue à l'écran (étapes 3, 4, 6) ;
- promesse : client identifié et un seul folio ouvert → report direct ;
  sinon file d'attente, la réception choisit (pos_order.py:62-75,
  :143-187) ;
- mise en place une fois, ajout aux caisses du bar, du restaurant et de la
  boutique : guide p.1 §2 ; sessions fermées : le champ des modes de
  paiement d'une caisse est en lecture seule tant qu'une session est ouverte
  (point_of_sale/views/res_config_settings_views.xml:57, fr.po:5482) ;
  « Identifier le client » obligatoire pour laisser le journal vide
  (pos_payment_method_views.xml:19-20) et « Client requis » à la caisse
  (payment_screen.js:424-439) ;
- caissier sans profil hôtel, report en sudo() : voir « Conditions » ci-dessus ;
- pas d'ardoise en double : aite_pos_credit/models/pos_payment_method.py:24-39
  (« Une note de chambre n'ouvre jamais d'ardoise, même cochée par
  erreur ») ; la case « Vente à crédit (ardoise) » reste décochée et sa
  phrase dit ce qu'elle ferait (res_config_settings_views.xml:16-19) ;
- lien par la fiche client, pas par le numéro de chambre : guide p.1 §3
  (« Bon réflexe ») et pos_order.py:160-166 (recherche par partner_id) ;
- l'avertissement n'empêche pas de valider : payment_screen.js:113-125
  (notification), aucune condition de facture dans _isOrderValid (:441 et
  suivantes) ;
- paiement mixte : pos_order.py:49-60, :96-139 (prorata) ;
  tests/test_room_charge.py:196-205 (5 000 en espèces + 7 000 en note de
  chambre → 7 000 sur le folio) ; guide p.1 §3 ;
- une ligne par ticket : pos_order.py:151-152 (garde d'idempotence),
  tests/test_room_charge.py:214-221 ; trois gestes et « C'est tout » : guide
  p.1 §3 (« Côté caisse : trois gestes », « C'est tout ») ;
- solde dû à jour : 157 500 − 100 000 = 57 500 FCFA (hotel_folio.py:
  _compute_amounts) ; « Services (HT) » vaut bien le HT du ticket (report HT
  + taxes, pos_order.py:96-139 ; sans TVA, HT = TTC) ;
- le motif dit pourquoi : guide p.2, légende de l'écran 3 ; une réservation
  confirmée a déjà son folio ouvert (d'où « 2 folios ouverts ») :
  hotel_reservation.py:374-390 ; seuls les séjours commencés, et ceux du
  client s'il en a, sont proposés : roomcharge_pending.py:50-69 (voir « Le
  séjour » ci-dessus) ;
- notes sans folio ouvert : guide p.2 FAQ (« rattachez-la plus tard à un
  folio s'il prend une chambre, ou réglez le ticket au comptoir et signalez
  la ligne à votre manager ») ; seul le responsable supprime une note
  (aite_hotel_pos_link/security/ir.model.access.csv:2-3) ;
- résultats : 3 gestes (guide p.1 §3) ; 1 ligne par ticket (ci-dessus) ;
  7 000 FCFA sur 12 000 (tests/test_room_charge.py:196-205).

Écart rejoué tel quel (voir ECARTS.md) : avertissement d'Odoo « soldes dûs »
au choix du mode (payment_screen.js:113-125 ; n° 43, chaîne standard du point
de vente laissée non surchargée). Corrigés dans la livraison 4 et montés
corrigés : « Created on » → « Reçue le » et « Front Desk » → « Réception »
(n° 42) ; fil d'Ariane technique « aite.roomcharge.pending,12 », « Nouveau »
sur la fiche et « Folio choisi » sans nom de client, ouvert à tous les
folios (n° 55) ; dates ISO dans le libellé de la nuitée (n° 37) ; case
« Vente à crédit (ardoise) » sans libellé (n° 65) ; aide de la file (n° 48,
non visible ici).

Données fictives : demo.py (Démo Hôtellerie SARL, nom de la société dans la
barre du haut ; Martin Ebode, RES/2026/0209 ; Hervé Tchakounté, Mireille
Ateba, Danielle Eyenga ; Brigitte Essomba et Sylvie Mbarga, clientes du
bar) ; Boris Ndzana, Carine Owona (t11) ; Thérèse Essomba ; caisses « Bar
de la terrasse », « Restaurant », « Boutique » ; carte du bar fictive.
"""

import demo
from ecrans import (APPS_PROFIL, MENUS_MUK, bouton, champ, cp_fiche, date_fr, deux_colonnes, e, entree, fcfa,
                    fenetre_muk, fenetre_pos, groupe, icone, navigateur, onglets, pos_ligne_paiement, pos_paiement,
                    pos_produits, statusbar, table, titre_fiche, toast, vue_fiche, vue_libre, vue_liste, cell_puce, num)
from marketing import bulle, dezoom, reaction, zoom
from moteur import (anneau, cacher, clic, classe, curseur, defiler, fermer, montrer, notifier, ouvrir, pause, saisir,
                    survol, texte, vue)

DIRECTION, ROLE_DIR = demo.POSTES['direction']     # Danielle Eyenga, Directrice
CAISSIER, ROLE_CAISSE = demo.POSTES['caisse']       # Hervé Tchakounté, Caissier du bar
RECEPTION, ROLE_REC = demo.POSTES['reception']      # Mireille Ateba, Réceptionniste
COMMANDE = 'Bar de la terrasse/1360'               # le ticket de Brigitte Essomba, le 14/10 au soir
TICKET = fcfa(13500)
CLIENTE = 'Brigitte Essomba'                        # chambre 202 [CFT], du 13 au 16/10 (tutoriels 2 et 3)
FOLIO_B, RESA_B = 'FOL/2026/0210', 'RES/2026/0210'   # t03_folio.py, FOLIOS


def masque(nav):
    """Un second cadre de navigateur, superposé et caché : un changement d'écran."""
    return nav.replace('class="navigateur"', 'class="navigateur masque"', 1)


def remplacer(html, avant, apres):
    """Un remplacement qui doit porter : une chaîne absente est une erreur du scénario."""
    if avant not in html:
        raise ValueError('t04 : chaîne introuvable : %s' % avant[:80])
    return html.replace(avant, apres, 1)


def champ_aide(libelle, valeur, identifiant=None, lien_=False, html=False):
    """Un ecrans.champ dont le libellé porte le « ? » qu'Odoo 18 pose après le libellé d'un champ qui a une aide
    (help= du modèle, related compris, ou de la vue ; form_label.js:39-49, form_label.xml:6) ; rendu de
    .t1-aide (scenarios/t01_reception.py)."""
    return remplacer(champ(libelle, valeur, identifiant, lien_=lien_, html=html),
                     '<span class="l">%s</span>' % e(libelle),
                     '<span class="l">%s<sup class="t04-aide">?</sup></span>' % e(libelle))


# ===================================================== 1. la mise en place --
# Point de Vente → Configuration → Modes de paiement → Nouveau (direction).
APPAREIL = ('<svg viewBox="0 0 24 24" fill="none" stroke="#ADB5BD" stroke-width="1.6" stroke-linejoin="round">'
            '<path d="M3 8h4l2-3h6l2 3h4v11H3z"/><circle cx="12" cy="13" r="3.6"/>'
            '<circle cx="18" cy="17.5" r="4" fill="#fff"/><path d="M18 15.5v4M16 17.5h4" stroke-linecap="round"/></svg>')


def ligne_pm(libelle, valeur_html, ident=None, aide=True):
    sup = ('<sup%s>?</sup>' % (' id="%s-aide"' % ident if ident else '')) if aide else ''
    return ('<div class="t04-r"><span class="l"%s>%s%s</span>%s</div>'
            % (' id="%s"' % ident if ident else '', e(libelle), sup, valeur_html))


MODE = vue_libre('t4-mode', (
    cp_fiche('Modes de paiement', 'Nouveau')
    + '<div class="t04-pm" id="t4-pm">'
      '<div class="t04-lab">Mode<sup>?</sup></div>'
    + '<div class="t04-titre">' + entree('t4-nom', 'par ex. Espèces', classe='entree t04-nom') + '</div>'
    + '<div class="t04-cols"><div id="t4-pm-g">'
    + ligne_pm('Paiement en ligne', '<span class="t04-cb"></span>')
    + ligne_pm('Identifier le client', '<span class="t04-cb" id="t4-cb-ident"></span>', 't4-l-ident')
    + ligne_pm('Journal', '<span class="t04-in" id="t4-journal">Laisser vide pour utiliser le compte débiteur du '
                          'client</span>')
    + ligne_pm('Note de chambre', '<span class="t04-cb" id="t4-cb-note"></span>', 't4-l-note')
    # aite_pos_credit (livraison 4) : la case avec son libellé, puis la phrase « ce qui va se passer », visible
    # avant de cocher (res_config_settings_views.xml:15-24) ; la consigne ne s'affiche que case cochée.
    + '<div id="t4-ard">'
    + ligne_pm('Vente à crédit (ardoise)', '<span class="t04-cb" id="t4-cb-ard"></span>', 't4-l-ard')
    + '<div class="t04-muet">Case cochée : chaque ticket réglé avec ce mode ouvre une ardoise au nom du client '
      '(POS Crédit → Ardoises).</div></div>'
    # pas de « Société » : company_id est réservé à base.group_multi_company (pos_payment_method_views.xml:23),
    # absent sur la base mono-société (docs/videos/DESIGN.md)
    + '</div><div>'
    + ligne_pm('Intégration', '<span class="t04-in noir">Non requis</span>', aide=False)
    + '</div></div><div class="t04-img">%s</div>' % APPAREIL
    + '<div class="t04-tip masque" id="t4-tip">Les encaissements sur ce moyen sont reportés au folio du séjour du '
      'client (ou en file d\'attente si ambigu).</div></div>'), initiale=True)

MENUS_POS = MENUS_MUK['point_de_vente']           # direction (responsable du point de vente)
APPS_DIRECTION = APPS_PROFIL['direction']
NAV_CONFIG = navigateur(fenetre_muk('app-t4c', 'Point de Vente', MENUS_POS, [MODE], actif='Configuration',
                                    societe=demo.SOCIETE, initiale=DIRECTION[0], avatar='#8E3B46',
                                    apps=APPS_DIRECTION, app_active='Point de Vente'))

# ============================================================ 2. la caisse --
BIERES, SOFTS, GRILLADES, PLATS, ACCOMP = '#F9D7A6', '#CDE6F7', '#F7C6C0', '#D9EFC9', '#E6DAF2'
CATEGORIES = [('Bières', BIERES), ('Jus & softs', SOFTS), ('Grillades', GRILLADES), ('Plats', PLATS),
              ('Accompagnements', ACCOMP)]
CARTE_BAR = [
    ('Bière blonde 65 cl', BIERES), ('Bière brune 65 cl', BIERES), ('Bière blonde 33 cl', BIERES),
    ('Bière sans alcool 33 cl', BIERES), ('Jus de bissap 50 cl', SOFTS), ("Jus d'ananas 1 L", SOFTS),
    ('Cola 33 cl', SOFTS), ('Tonic 33 cl', SOFTS), ('Eau minérale 50 cl', SOFTS), ('Eau gazeuse 1 L', SOFTS),
    ('Poisson braisé', GRILLADES), ('Poulet braisé', GRILLADES), ('Brochettes de bœuf', GRILLADES),
    ('Soya', GRILLADES), ('Ndolè', PLATS), ('Poulet DG', PLATS), ('Eru', PLATS), ('Mbongo tchobi', PLATS),
    ('Plantain frit', ACCOMP), ('Bâton de manioc', ACCOMP), ('Miondo', ACCOMP), ('Frites de plantain', ACCOMP),
    ('Arachides grillées', ACCOMP), ('Chips de plantain', ACCOMP)]
# Le ticket de Brigitte Essomba : articles sans taxe (voir l'en-tête), donc pas de ligne « Taxes ».
LIGNES_TICKET = [('t4-l1', 'Poisson braisé', '1,00', fcfa(7000), fcfa(7000)),
                 ('t4-l2', 'Plantain frit', '1,00', fcfa(1500), fcfa(1500)),
                 ('t4-l3', 'Bière blonde 65 cl', '2,00', fcfa(1500), fcfa(3000)),
                 ('t4-l4', 'Jus de bissap 50 cl', '2,00', fcfa(1000), fcfa(2000))]
VENTE = pos_produits('t4-vente', CATEGORIES, [('t4-p%d' % i, n, c) for i, (n, c) in enumerate(CARTE_BAR)],
                     LIGNES_TICKET, TICKET, '', initiale=True)
VENTE = remplacer(VENTE, '<small>Taxes<span id="t4-vente-taxes"></span></small>', '')
VENTE = VENTE.replace(' / Unités</div>', ' / Unité(s)</div>')
VENTE = remplacer(VENTE, 'class="pv-ligne" id="t4-l4"', 'class="pv-ligne sel" id="t4-l4"')
VENTE = remplacer(VENTE, '<span>Client</span>', '<span id="t4-cli"><b id="t4-cli-t">Client</b></span>')
VENTE = remplacer(VENTE, '<div class="pos-acts">', '<div class="pos-acts" id="t4-acts">')

# Les icônes des modes, d'après celles d'Odoo (payment_screen.js:413-421) : espèces, banque, payer plus tard.
ICO_ESPECES = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round">'
               '<rect x="2" y="4.5" width="13.5" height="8.5" rx="1"/><circle cx="8.75" cy="8.75" r="1.9"/>'
               '<path d="M4.5 15h12.5V7.5"/><ellipse cx="18.5" cy="15.2" rx="3.5" ry="1.4"/>'
               '<path d="M15 15.2v3.4c0 .8 1.6 1.4 3.5 1.4s3.5-.6 3.5-1.4v-3.4M15 16.9c0 .8 1.6 1.4 3.5 1.4s3.5-.6 3.5-1.4"/>'
               '</svg>')
ICO_BANQUE = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round">'
              '<rect x="2.5" y="4.5" width="19" height="15" rx="1"/><path d="M2.5 7.6h19M2.5 10.2h19"/>'
              '<rect x="5" y="14.6" width="6.4" height="2.6" rx="1.3"/>'
              '<path d="M17.4 13v6M18.7 14.2c-.3-.4-.7-.6-1.3-.6-.7 0-1.3.4-1.3 1s.6.9 1.3 1 1.3.4 1.3 1-.6 1-1.3 1'
              'c-.6 0-1-.2-1.3-.6" stroke-linecap="round"/></svg>')
ICO_PLUS_TARD = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round" '
                 'stroke-linecap="round"><path d="M3.5 7a2 2 0 012-2h9.5a1.5 1.5 0 011.5 1.5v.5"/>'
                 '<path d="M3.5 7v9a2 2 0 002 2h6.5"/><path d="M5.5 7h12.5a2 2 0 012 2v2.5"/>'
                 '<circle cx="16.8" cy="11" r=".9"/><circle cx="17.5" cy="17.5" r="4"/><path d="M17.5 15.5v2.2h1.8"/></svg>')
MODES = [('t4-m-esp', 'Espèces', ICO_ESPECES), ('t4-m-om', 'Orange Money', ICO_BANQUE),
         ('t4-m-momo', 'MTN MoMo', ICO_BANQUE), ('t4-m-note', 'Note de chambre', ICO_PLUS_TARD),
         ('t4-m-ard', 'Ardoise client', ICO_PLUS_TARD)]       # comme au tutoriel 10 (t10_ardoises.py, MODES)
PAIEMENT = pos_paiement('t4-paie', [(i, l) for i, l, _ in MODES], TICKET)
for _i, _l, _svg in MODES:
    PAIEMENT = remplacer(PAIEMENT, 'id="%s">%s' % (_i, icone('carte')), 'id="%s"><span class="ico">%s</span>' % (_i, _svg))
PAIEMENT = remplacer(PAIEMENT, icone('personne') + 'Client</span>',
                     icone('personne') + '<b class="t04-nomcli">%s</b></span>' % e(CLIENTE))
PAIEMENT = remplacer(PAIEMENT, 'class="v" id="t4-paie-valider"', 'class="v t04-off" id="t4-paie-valider"')
PAIEMENT = remplacer(PAIEMENT, '<div class="pos-zone">', '<div class="t04-choix" id="t4-paie-msg">Veuillez sélectionner '
                                                         'un mode de paiement</div><div class="pos-zone">')
PAIEMENT = remplacer(PAIEMENT, 'class="pos-restant" id="t4-paie-restant"',
                     'class="pos-restant masque" id="t4-paie-restant"')
PAIEMENT = remplacer(PAIEMENT, '<span id="t4-paie-reste">%s</span>' % TICKET,
                     '<span id="t4-paie-reste">%s</span>' % fcfa(0))
PAIEMENT = remplacer(PAIEMENT, '<div id="t4-paie-lignes"></div>', '<div id="t4-paie-lignes">%s</div>'
                     % pos_ligne_paiement('t4-pl', 'Note de chambre', TICKET))

# La fenêtre des clients (bouton « Client »), dans l'ordre des noms.
AVION = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M22 2L11 13M22 2l-7 20-4-9-9-4z"/></svg>'
# Téléphones de la plage de fiction de la série : ceux de t10_ardoises.py (TELEPHONES) pour Armand, Boris,
# Brigitte et Carine ; demo.CLIENT_TEL pour Estelle ; celui de Claire Durand partout dans la série.
BRIGITTE = (CLIENTE, 'Bonamoussadi Douala Cameroun', '+237 6 00 00 00 32', 'brigitte.essomba@exemple.cm')
CLIENTS = [('Armand Mvogo', 'Bastos Yaoundé Cameroun', '+237 6 00 00 00 31', 'armand.mvogo@exemple.cm'),
           ('Boris Ndzana', 'Akwa Douala Cameroun', '+237 6 00 00 00 40', 'boris.ndzana@exemple.cm'),
           BRIGITTE,
           ('Carine Owona', 'Bali Douala Cameroun', '+237 6 00 00 00 41', 'carine.owona@exemple.cm'),
           ('Claire Durand', 'Lyon France', '+33 6 39 98 21 47', 'claire.durand@exemple.fr'),
           (demo.CLIENT, 'Bonapriso Douala Cameroun', demo.CLIENT_TEL, demo.CLIENT_MAIL)]
TROUVES = [BRIGITTE, ('Thérèse Essomba', 'Mfandena Yaoundé Cameroun', '+237 6 00 00 00 63',
                      'therese.essomba@exemple.cm')]


def ligne_client(ident, nom, adresse, tel, mail):
    return ('<div class="t04-cl"%s><b>%s</b><span>%s</span><span class="t04-ct"><span>%s%s</span><span>%s%s</span>'
            '</span><span class="t04-menu">☰</span></div>'
            % (' id="%s"' % ident if ident else '', e(nom), e(adresse), icone('telephone', 't04-ci'), e(tel),
               '<span class="t04-ci">%s</span>' % AVION, e(mail)))


TETE_CLIENTS = '<div class="t04-cl t04-cl-tete"><span>Nom</span><span>Adresse</span><span>Contact</span><span></span></div>'
DIALOGUE = (
    '<div class="voile masque" id="t4-dlg-voile" data-layout-allow-overlap data-layout-allow-occlusion></div>'
    '<div class="modale masque t04-dlg" id="t4-dlg" data-layout-allow-overlap data-layout-allow-occlusion>'
    '<div class="t04-dlg-h"><span class="bt primaire t04-creer">Créer</span>%s</div>'
    '<div class="t04-dlg-c">%s<div class="t04-pile"><div id="t4-tous">%s</div>'
    '<div class="masque" id="t4-trouves">%s<div class="t04-plus"><span class="bt primaire">Rechercher plus</span></div>'
    '</div></div></div><div class="t04-dlg-p"><span class="bt gris">Ignorer</span></div></div>'
    % (entree('t4-q', 'Recherche des clients...', classe='entree t04-q'), TETE_CLIENTS,
       ''.join(ligne_client(None, *c) for c in CLIENTS),
       ligne_client('t4-c-brigitte', *TROUVES[0]) + ligne_client(None, *TROUVES[1])))
AVERT = toast('t4-avert', 'Avertissement', "Pour assurer le suivi des soldes dûs, générez une facture ou téléchargez "
                                           "l'application comptabilité.", genre='alerte')
POS = fenetre_pos('app-t4p', [VENTE, PAIEMENT], CAISSIER, numero='508', calques=DIALOGUE + AVERT)
POS = remplacer(POS, 'Rechercher des produits...', 'Rechercher des produits…')
POS = remplacer(POS, '<span class="pos-caissier">', '<span class="pos-caissier" id="t4-caissier">')
NAV_POS = masque(navigateur(POS, 'nav-pos'))

# ============================================================= 3. l'hôtel --
MENUS_HOTEL = MENUS_MUK['hotel_reception']        # « Réception » (anciennement « Front Desk »)

# -- le folio de Brigitte Essomba, la ligne du bar déjà reportée (le 14/10 au soir)
# colonnes resserrées : le libellé de nuitée, au format français, se lit en entier jusqu'au départ
COLS_F = [('Date', '116px'), ('Type', '150px'), ('Service', '72px'), ('Libellé', '1fr'), ('Qté', '64px', 'd'),
          ('Prix unitaire', '134px', 'd'), ('Taxes', '64px'), ('Sous-total (HT)', '148px', 'd'),
          ('Total (TTC)', '140px', 'd')]
LIGNES_F = table(COLS_F, [
    # libellé de nuitée au format français, dates locales (hotel_folio.py:253-276, livraison 4)
    ('t4-fl1', [date_fr('2026-10-13'), ('<span><span class="puce info">Nuitée</span></span>',), '',
                'Nuitée 202 (Confort) — %s → %s' % (date_fr('2026-10-13'), date_fr('2026-10-16')), '3,00',
                fcfa(45000), '', fcfa(135000), fcfa(135000)]),
    ('t4-fl2', [date_fr('2026-10-13'), ('<span><span class="puce orange">Taxe de séjour</span></span>',), '',
                'Taxe de séjour — 3 nuitée(s) × personne (3 ★, Cameroun)', '3,00', fcfa(3000), '', fcfa(9000),
                fcfa(9000)]),
    ('t4-fl3', [date_fr('2026-10-14'), ('<span><span class="puce violet">Service</span></span>',), '',
                'POS ' + COMMANDE, '1,00', TICKET, '', TICKET, TICKET])],
    total=['', '', '', '', '', '', '', fcfa(157500), fcfa(157500)], identifiant='t4-lignes')
LIGNES_F = remplacer(LIGNES_F, 'class="t-ligne" id="t4-fl1"', 'class="t-ligne t04-nuitee" id="t4-fl1"')
LIGNES_F = remplacer(LIGNES_F, 'class="t-ligne" id="t4-fl2"', 'class="t-ligne taxe" id="t4-fl2"')
FEUILLE_FOLIO = (
    titre_fiche(FOLIO_B)
    + deux_colonnes(
        # « Hôtel » (hotel_folio_views.xml:73-74) est réservé à base.group_multi_company : absent sur la base
        # mono-société (docs/videos/DESIGN.md)
        groupe('Séjour', [champ('Client', CLIENTE, lien_=True), champ('Réservation', RESA_B, lien_=True),
                          champ('Séjour', 'Arrivé'), champ('Arrivée', '13/10/2026 14:00:00'),
                          champ('Départ', '16/10/2026 12:00:00')]),
        groupe('Montants', [champ('Hébergement (HT)', fcfa(135000)), champ('Services (HT)', TICKET),
                            # le « ? » : help d'amount_city_tax (aite_city_tax/models/hotel_folio.py:56-60)
                            champ_aide('Taxe de séjour', fcfa(9000)), champ('Total HT', fcfa(157500)),
                            champ('Taxes', fcfa(0)), champ('Total TTC', '<b>%s</b>' % fcfa(157500), html=True),
                            champ('Encaissé', fcfa(100000)),
                            champ('Solde dû', '<b>%s</b>' % fcfa(57500), 't4-f-solde', html=True)], 't4-f-montants'))
    + onglets(['Lignes du folio', 'Règlements', 'Note']) + LIGNES_F
    + '<div class="note-pied">Les lignes « nuitée » sont synchronisées depuis la réservation ; ajoutez librement des '
      'lignes de service (restaurant, blanchisserie, minibar…).</div>')
FOLIO = vue_fiche('t4-folio', cp_fiche('Folios', FOLIO_B, '12 / 14', stats=[('t4-st-regl', 'billet', 'Règlements', '1')]),
                  [bouton('t4-f-enc', 'Encaisser', 'primaire'), bouton('t4-f-fact', 'Générer la facture')],
                  statusbar('t4-fsb', ['Ouvert', 'Facturé', 'Soldé'], 0), FEUILLE_FOLIO, initiale=True)

# -- la file « Notes de chambre en attente » (filtre À rattacher), le 16/10 au soir
COLS_N = [('Reçue le', '212px'), ('Commande POS', '262px'), ('Client', '196px'), ('Montant', '150px', 'd'),
          ('Motif', '1fr'), ('Folio choisi', '170px'), ('État', '140px')]
NOTE_MARTIN = 'Bar de la terrasse/1377'            # le 16/10 à 22:41 (voir l'en-tête)
ATTENTE = [('16/10/2026 22:41:17', NOTE_MARTIN, 'Martin Ebode', fcfa(9500), '2 folios ouverts'),
           ('16/10/2026 20:18:03', 'Restaurant/0083', 'Boris Ndzana', fcfa(21000), 'Aucun folio ouvert'),
           ('16/10/2026 16:52:40', 'Boutique/0018', 'Sylvie Mbarga', fcfa(6000), 'Aucun folio ouvert')]


def file_attente(ident, lignes, total):
    vue_html = vue_liste(ident, 'Notes de chambre en attente', COLS_N, [
        {'id': '%s-%s' % (ident, i), 'classe': 'avert',
         'cellules': [d, ref, cli, num(mt), (('<span class="ell" id="%s-%s-motif">%s</span>' % (ident, i, e(motif))),),
                      '', cell_puce('À rattacher', 'orange')]}
        for i, (d, ref, cli, mt, motif) in enumerate(lignes)],
        facettes=[('%s-fac' % ident, 'À rattacher')], pager='1-%d / %d' % (len(lignes), len(lignes)),
        total=['', '', '', total, '', '', ''], nouveau=False)
    pied = '<span class="d">%s</span><span></span>' % e(total)
    return remplacer(vue_html, pied, '<span class="d">%s</span><span id="%s-ancre"></span>' % (e(total), ident))


FILE = file_attente('t4-file', ATTENTE, fcfa(36500))
FILE_APRES = file_attente('t4-file2', ATTENTE[1:], fcfa(27000))

# -- la note en attente de Martin Ebode : deux folios ouverts (séjour en cours et réservation de novembre),
# d'où le motif. « Folio choisi » ne propose que les séjours commencés, et ceux du client s'il en a
# (roomcharge_pending.py:37-69, livraison 4) : le seul séjour arrivé de Martin, affiché « référence — client »
# (contexte aite_folio_with_partner) ; la réservation de novembre, confirmée mais pas commencée, n'y est pas.
# Champ sans création (options no_create) : ni « Créer… » ni « Commencer à écrire... » ; « Recherche
# avancée... » dès qu'il y a un résultat (relational_utils.js:313-385, many2one_field.js:377-384).
FOLIO_MARTIN = 'FOL/2026/0209 — Martin Ebode'
DEROULANT = ('<div class="t04-dd masque" id="t4-dd" data-layout-allow-overlap data-layout-allow-occlusion>'
             '<div class="t04-dd-o" id="t4-dd-0209">%s</div><div class="t04-dd-o lien">Recherche avancée...</div>'
             '</div>' % e(FOLIO_MARTIN))
FOLIO_CHOISI = ('<div class="t04-m2o" id="t4-fc"><span class="t04-m2o-v" id="t4-fc-val"></span>'
                '<span class="t04-car">▾</span>%s</div>' % DEROULANT)
FEUILLE_NOTE = deux_colonnes(
    '<div class="grp">%s</div>' % ''.join([champ('Commande POS', NOTE_MARTIN, lien_=True),
                                         champ('Client', 'Martin Ebode', 't4-n-client', lien_=True),
                                         champ('Montant', fcfa(9500)),
                                         champ('Motif', '2 folios ouverts', 't4-motif')]),
    '<div class="grp">%s</div>' % champ('Folio choisi', FOLIO_CHOISI, html=True, gras=True))
# Fil d'Ariane au numéro du ticket (champ « Ticket », roomcharge_pending.py:16-20) ; fiche create="0", sans
# « Nouveau » (roomcharge_pending_views.xml:29-31).
NOTE = vue_fiche('t4-note', cp_fiche('Notes de chambre en attente', NOTE_MARTIN, '1 / 3', nouveau=False),
                 [bouton('t4-b-ratt', 'Rattacher au folio', 'primaire')],
                 statusbar('t4-nsb', ['À rattacher', 'Rattachée'], 0), FEUILLE_NOTE)
NOTE = remplacer(NOTE, '<span class="parent">', '<span class="parent" id="t4-fil">')

HOTEL = fenetre_muk('app-t4h', 'Hôtel', MENUS_HOTEL, [FOLIO, FILE, NOTE, FILE_APRES], actif='Facturation',
                    societe=demo.SOCIETE, initiale=RECEPTION[0], avatar='#7C5295', apps=APPS_PROFIL['reception'],
                    app_active='Hôtel')
HOTEL = remplacer(HOTEL, '<span class="menu">Notes de chambre en attente</span>',
                  '<span class="menu" id="t4-menu-file">Notes de chambre en attente</span>')
HOTEL = remplacer(HOTEL, '<span class="menu actif">Facturation</span>',
                  '<span class="menu actif" id="t4-menu-fact">Facturation</span>')
NAV_HOTEL = masque(navigateur(HOTEL, 'nav-hotel'))

ECRAN = NAV_CONFIG + NAV_POS + NAV_HOTEL


# ============================================== la pastille du personnage --
# La pastille (marketing.py) porte le nom en gras puis le rôle ; à chaque temps
# fort elle passe au personnage qui agit : une classe sur #tu-perso, le texte
# rendu par ::before / ::after, l'initiale par le geste « texte ».
def pastille_css(classe_, nom, role):
    return ('#tu-perso.%s > span:last-child { font-size: 0; }\n'
            '#tu-perso.%s > span:last-child::before { content: "%s"; font-size: 21px; font-weight: 700; }\n'
            '#tu-perso.%s > span:last-child::after { content: " · %s"; font-size: 21px; white-space: pre; }\n'
            % (classe_, classe_, nom, classe_, role))


def personnage(classe_, initiale, retirer=()):
    return [classe('#tu-perso', ajouter=[classe_], retirer=list(retirer)),
            texte('#tu-perso .av', initiale, avec=True)]


CSS = """
/* -- la pastille du personnage, d'un temps fort à l'autre -- */
""" + pastille_css('t04-pc', CAISSIER, ROLE_CAISSE) + pastille_css('t04-pr', RECEPTION, ROLE_REC) + """
/* -- 1. fiche du mode de paiement (thème MuK) -- */
#t4-mode .cp { height: 80px; }
.t04-pm { position: absolute; left: 22px; right: 22px; top: 102px; height: 496px; background: #fff;
  border: 1px solid var(--o-filet); padding: 22px 30px; color: var(--o-texte); }
.t04-lab { font-size: 19px; font-weight: 600; }
.t04-pm sup { margin-left: 3px; font-size: 13px; color: #3F6A83; font-weight: 600; }
.t04-titre { display: flex; align-items: center; gap: 18px; }
.t04-nom { margin-top: 4px; width: 640px; height: 64px; border-width: 0 0 1px 0; border-radius: 0; padding: 0 4px; font-size: 40px; }
.t04-nom .ph, .t04-nom .val { left: 4px; }
.t04-nom .val { font-weight: 400; }
.t04-cols { display: grid; grid-template-columns: 780px 420px; column-gap: 56px; margin-top: 24px; }
.t04-r { display: grid; grid-template-columns: 286px 1fr; align-items: center; min-height: 52px; font-size: 19px; }
.t04-r .l { font-weight: 600; white-space: nowrap; }
/* la phrase d'aite_pos_credit, text-muted sur toute la largeur du groupe */
.t04-muet { padding: 2px 0 12px; font-size: 19px; line-height: 1.4; color: #6C757D; }
.t04-cb { width: 20px; height: 20px; border: 1px solid #ADB5BD; border-radius: 3px; background: #fff; display: inline-flex;
  align-items: center; justify-content: center; }
.t04-cb.on { background: var(--muk-prim); border-color: var(--muk-prim); }
.t04-cb.on::after { content: '✓'; color: #fff; font-size: 15px; font-weight: 700; }
.t04-in { height: 42px; border-bottom: 1px solid #CED4DA; display: block; line-height: 42px; padding: 0 4px; color: #6C757D;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.t04-in.noir { color: var(--o-texte); }
.t04-img { position: absolute; left: 1330px; top: 130px; width: 130px; height: 130px; border: 1px solid var(--o-filet);
  display: flex; align-items: center; justify-content: center; }
.t04-img svg { width: 82px; height: 82px; }
.t04-tip { position: absolute; left: 30px; top: 352px; width: 560px; padding: 14px 22px; background: #000; color: #fff;
  font-size: 19px; line-height: 1.45; z-index: 5; }
.t04-tip::before { content: ''; position: absolute; left: 155px; top: -9px; border: 9px solid transparent; border-top: 0;
  border-bottom-color: #000; }

/* -- 2. la caisse -- */
#t4-cli .t04-cli-t, #t4-cli b { font-weight: 400; }
#t4-cli.t04-actif b { color: #3F6A83; font-weight: 500; }
.t04-nomcli { font-weight: 500; color: #3F6A83; }
.pos-rv .v.t04-off { background: #A3BCCB; }
.t04-choix { position: absolute; left: 0; right: 0; top: 410px; text-align: center; font-size: 24px; color: var(--o-texte); }
.pos-pd .pos-zone { top: 380px; }
#t4-paie-restant { color: #1A6E2E; border-color: #1A6E2E; }
.pos-mode.actif { background: #E9ECEF; }
.pos-mode .ico svg { width: 26px; height: 26px; }
/* les icônes de « Client » et « Facture » : la règle .pos-cf span ne vise que les boutons */
#t4-paie .pos-cf > span .ico { height: 18px; padding: 0; background: none; border-radius: 0; }
.t04-dlg { top: 50px; width: 1260px; margin-left: -630px; }
.t04-dlg-h { display: flex; align-items: center; height: 84px; padding: 0 24px; border-bottom: 1px solid var(--o-filet); }
.t04-creer { height: 50px; font-size: 21px; padding: 0 22px; }
.t04-q { margin: 0 0 0 auto; width: 480px; height: 52px; font-size: 21px; }
.t04-dlg-c { position: relative; height: 520px; padding: 0 24px; }
.t04-pile { position: relative; }
.t04-pile > div:nth-child(2) { position: absolute; left: 0; right: 0; top: 0; }
.t04-cl { display: grid; grid-template-columns: 300px 360px 1fr 60px; align-items: center; gap: 16px; min-height: 76px;
  padding: 0 12px; border-bottom: 1px solid #EEF0F2; font-size: 19px; color: var(--o-texte); }
.t04-cl b { font-weight: 700; }
.t04-cl-tete { min-height: 52px; font-weight: 600; border-bottom: 1px solid var(--o-filet); }
.t04-cl.survol { background: #E3ECF2; }
.t04-ct { display: flex; flex-direction: column; gap: 3px; font-size: 17px; color: var(--o-texte-2); }
.t04-ct > span { display: flex; align-items: center; gap: 8px; white-space: nowrap; }
.t04-ci { width: 16px; height: 16px; display: inline-flex; color: var(--o-texte-2); }
.t04-ci svg { width: 16px; height: 16px; }
.t04-menu { width: 46px; height: 42px; border: 1px solid var(--o-filet); border-radius: 4px; display: flex; align-items: center;
  justify-content: center; font-size: 20px; color: var(--o-texte); background: #F8F9FA; }
.t04-plus { display: flex; justify-content: center; margin-top: 16px; }
.t04-plus .bt { height: 50px; font-size: 20px; }
.t04-dlg-p { height: 84px; display: flex; align-items: center; padding: 0 24px; border-top: 1px solid var(--o-filet); }
.t04-dlg-p .bt { height: 50px; font-size: 20px; }
#t4-avert { top: 74px; width: 600px; }

/* -- 3. l'hôtel -- */
#t4-fsb .st-et, #t4-nsb .st-et { color: #5C636A; }
#b-ident { max-width: 780px; }
#b-aucun { max-width: 640px; }
.table .t-ligne.t04-nuitee { color: var(--info); }
#t4-folio .ch { min-height: 38px; }
/* le « ? » d'aide d'Odoo 18 (form_label.xml:6), rendu de .t1-aide (scenarios/t01_reception.py) */
.t04-aide { color: var(--o-lien); font-size: 13px; margin-left: 3px; font-weight: 700; }
#t4-folio .f-titre { margin-bottom: 14px; }
#t4-note .feuille { min-height: 0; border-bottom: 1px solid var(--o-filet); padding-bottom: 26px; }
.t04-m2o { position: relative; height: 42px; border-bottom: 1px solid #CED4DA; }
.t04-m2o.focus { border-bottom-color: var(--muk-prim); }
.t04-m2o.lecture { border-bottom-color: transparent; }
.t04-m2o-v { position: absolute; left: 4px; top: 50%; transform: translateY(-50%); color: var(--o-texte); white-space: nowrap; }
.t04-m2o.lecture .t04-m2o-v { color: #3F6A83; }
.t04-car { position: absolute; right: 6px; top: 50%; transform: translateY(-50%); font-size: 14px; color: var(--o-texte-2); }
.t04-m2o.lecture .t04-car { opacity: 0; }
.t04-dd { position: absolute; left: 0; top: 44px; width: 380px; background: #fff; border: 1px solid var(--o-filet);
  box-shadow: 0 10px 24px rgba(0,0,0,.14); padding: 6px 0; z-index: 6; }
.t04-dd-o { height: 40px; display: flex; align-items: center; padding: 0 20px; font-size: 19px; color: var(--o-texte); white-space: nowrap; }
.t04-dd-o.survol { background: #E9ECEF; }
.t04-dd-o.lien { color: #3F6A83; padding-left: 30px; }
.t04-dd-o.ital { font-style: italic; color: var(--o-texte-2); padding-left: 30px; }
"""

TUTORIEL = {
    'slug': 't04-note-chambre',
    'profil': 't04_note_chambre',
    'numero': 4,
    'titre': 'Bar et restaurant sur la note de chambre',
    'fonction': 'Note de chambre',
    # la pastille part sur la direction (étape 1), puis passe au caissier et à la réception
    'personnage': (DIRECTION, ROLE_DIR),
    'accroche': {
        'kicker': 'Bar, restaurant, boutique',
        'question': 'Le dîner pris au bar est-il *déjà* sur la note de la chambre ?',
        'douleurs': [('pieces', 'La monnaie sortie à chaque verre'),
                     ('cahier', 'Le ticket du bar recopié sur le folio'),
                     ('billet', 'Moitié en espèces, moitié sur la chambre'),
                     ('interrogation', 'Deux séjours au même nom : lequel ?'),
                     ('alerte', 'Une consommation sur le mauvais séjour')],
        'voix': "Le dîner pris au bar est-il déjà sur la note de la chambre ? Ou faut-il encore recopier le ticket ?",
    },
    'revelation': {
        'promesse': 'La consommation rejoint seule le folio du séjour. Au moindre doute, c\'est la réception qui '
                    'choisit.',
        'voix': "Avec Aïte haousse, la consommation rejoint toute seule le folio du séjour. Au moindre doute, c'est la "
                "réception qui choisit.",
    },
    'temps': ['Mettre en place', 'Encaisser', 'Reporter', 'Rattacher'],
    'app': 'app-t4c',
    'ecran': ECRAN,
    'css': CSS,
    'vues_initiales': {'odoo': 't4-mode', 'pos': 't4-vente', 'hotel': 't4-folio'},
    'bulles': {
        'b-ident': 'Sans client, la caisse demande « Client requis » avant de valider.',
        'b-avert': 'Avertissement standard d\'Odoo : il n\'empêche pas de valider.',
        'b-mixte': 'Paiement mixte : seule la part « Note de chambre » part sur la chambre.',
        'b-ligne': 'Une seule ligne par ticket, avec sa référence. Et aucune ardoise en double.',
        'b-motif': 'Le motif dit pourquoi le rattachement automatique n\'a pas eu lieu.',
        'b-folio': 'Seuls les séjours commencés sont proposés : ceux du client, s\'il en a.',
        'b-aucun': 'Aucun folio ouvert : on rattache plus tard si le client prend une chambre ; sinon, le ticket se '
                   'règle au comptoir et le responsable est prévenu.',
    },
    'reactions': {
        'r-caisse': "Je choisis le client, je touche Note de chambre, je valide. C'est tout.",
    },
    'etapes': [
        {'temps': 0, 'titre': 'Une case, une fois pour toutes',
         'texte': 'Le mode « Note de chambre », ajouté aux caisses du bar, du restaurant et de la boutique, '
                  'sessions fermées.',
         'voix': "Une fois pour toutes, la direction crée le mode de paiement Note de chambre : Identifier le client "
                 "coché, journal laissé vide, et la case Note de chambre. Vente à crédit reste décochée : pas "
                 "d'ardoise. On l'ajoute ensuite aux caisses du bar, du restaurant et de la boutique, sessions fermées.",
         'gestes': [clic('#t4-nom', fx=0.3), saisir('t4-nom', 'Note de chambre'), clic('#t4-cb-ident'),
                    classe('#t4-cb-ident', ajouter=['on']), zoom('#t4-pm', s=1.45, d=0.8, fx=0.43, fy=0.50),
                    bulle('b-ident', '#t4-cb-ident', cote='droite', d=2.2), pause(0.15), anneau('#t4-journal', d=1.2),
                    clic('#t4-cb-note', d=0.5), classe('#t4-cb-note', ajouter=['on']), pause(0.25),
                    anneau('#t4-ard', d=2.3),
                    curseur('#t4-l-note-aide', fx=0.3, fy=0.2, d=0.5), montrer('#t4-tip', d=0.35, y=8),
                    pause(2.3), cacher('#t4-tip', d=0.3), dezoom(d=0.6)]},
        {'temps': 1, 'titre': 'Au bar : le ticket et le client',
         'texte': 'Le bouton Client relie le ticket à la fiche du client, pas au numéro de chambre.',
         'voix': "Au bar de la terrasse, Brigitte Essomba, cliente de la chambre deux cent deux, termine son dîner. "
                 "Hervé touche Client et la choisit. C'est sa fiche, et non le numéro de chambre, qui relie le ticket à son séjour.",
         'gestes': personnage('t04-pc', CAISSIER[0]) + [
                    texte('#r-caisse .av', CAISSIER[0], avec=True), texte('#r-caisse b', CAISSIER.split()[0], avec=True),
                    montrer('#nav-pos', d=0.5, y=0, avec=True), pause(0.4),
                    anneau('#t4-vente-ticket', d=1.2), clic('#t4-cli'),
                    ouvrir('t4-dlg'), saisir('t4-q', 'Essomba', d=0.6), cacher('#t4-tous', d=0.25),
                    montrer('#t4-trouves', d=0.3, y=0), pause(0.3), curseur('#t4-c-brigitte', fx=0.15, d=0.5),
                    survol('#t4-c-brigitte'), anneau('#t4-c-brigitte', d=1.4), clic('#t4-c-brigitte', fx=0.15),
                    fermer('t4-dlg'), texte('#t4-cli-t', CLIENTE), classe('#t4-cli', ajouter=['t04-actif']),
                    curseur('#t4-cli', fx=0.5, fy=0.7, d=0.5), anneau('#t4-acts', d=1.6)]},
        {'temps': 1, 'titre': 'Paiement : « Note de chambre »',
         'texte': 'Le reste à payer tombe à zéro ; le ticket se valide comme d\'habitude.',
         'voix': "Au paiement, il touche Note de chambre : le reste à payer tombe à zéro. Odoo affiche un "
                 "avertissement, qui n'empêche pas de valider. Un paiement mixte est possible, une part en espèces et "
                 "le reste sur la chambre : seule cette part sera reportée. Puis il valide, comme d'habitude.",
         'gestes': [clic('#t4-vente-payer'), vue('t4-paie', 'pos'), cacher('#app-t4p .pos-cherche', d=0.2, avec=True),
                    pause(0.4), clic('#t4-m-note'), classe('#t4-m-note', ajouter=['actif']),
                    cacher('#t4-paie-msg', d=0.2), montrer('#t4-paie-restant', d=0.3, y=0), montrer('#t4-pl', d=0.3, y=0),
                    classe('#t4-paie-valider', retirer=['t04-off']), notifier('t4-avert', duree=4.4),
                    bulle('b-avert', '#t4-avert', cote='bas', d=2.8), pause(3.0),
                    zoom('#t4-paie-restant', s=1.3, d=0.7), bulle('b-mixte', '#t4-paie-restant', cote='haut', d=2.6),
                    pause(2.2), dezoom(d=0.6), reaction('r-caisse', d=3.0), clic('#t4-paie-valider'), pause(1.0)]},
        {'temps': 2, 'titre': 'Sur le folio, sans ressaisie',
         'texte': 'Une ligne de service « POS Bar de la terrasse/1360 », et le solde dû à jour.',
         'voix': "À la réception, Mireille ouvre le folio de Brigitte : le dîner y est déjà, en ligne de service, avec "
                 "la référence du ticket, et aucune ardoise n'est ouverte en double. Le solde dû est à jour, sans rien "
                 "ressaisir.",
         'gestes': personnage('t04-pr', RECEPTION[0], retirer=['t04-pc']) + [
                    montrer('#nav-hotel', d=0.5, y=0, avec=True), pause(0.5), defiler('#t4-folio-defil', -400, d=0.9),
                    anneau('#t4-fl3', d=1.2), zoom('#t4-fl3', s=1.3, d=0.7),
                    bulle('b-ligne', '#t4-fl3', cote='bas', d=2.6), pause(2.4), dezoom(d=0.6),
                    defiler('#t4-folio-defil', 0, d=0.8), anneau('#t4-f-solde', d=1.4)]},
        {'temps': 3, 'titre': 'Un doute ? La file d\'attente',
         'texte': 'Notes de chambre en attente : chaque ticket avec son motif, en orange.',
         'voix': "Quand le rattachement n'est pas certain, le système ne devine pas : le ticket attend dans Notes de "
                 "chambre en attente, avec son motif. Aucun folio ouvert, ou deux folios au même nom.",
         'gestes': [clic('#t4-menu-file'), classe('#t4-menu-fact', retirer=['actif']),
                    classe('#t4-menu-file', ajouter=['actif']), vue('t4-file', 'hotel'), pause(0.5),
                    anneau('#t4-file-fac', d=1.2), curseur('#t4-file-0', fx=0.3, d=0.6), survol('#t4-file-0'),
                    anneau('#t4-file-0-motif', d=1.4), bulle('b-motif', '#t4-file-ancre', cote='bas', d=2.6),
                    pause(1.8), anneau('#t4-file-1-motif', d=1.2)]},
        {'temps': 3, 'titre': 'Choisir le bon folio',
         'texte': 'Folio choisi : seulement les séjours commencés, au nom du client.',
         'voix': "Mireille ouvre la note de Martin Ebode : deux folios ouverts, son séjour en cours et une "
                 "réservation confirmée pour novembre. Elle déroule Folio choisi : seul le séjour commencé est "
                 "proposé, à son nom. Elle le prend.",
         'gestes': [clic('#t4-file-0', fx=0.3), vue('t4-note', 'hotel'), pause(0.3), anneau('#t4-motif', d=2.5),
                    clic('#t4-fc', fx=0.3), classe('#t4-fc', ajouter=['focus']), montrer('#t4-dd', d=0.3, y=-6),
                    # fx=0.48 : le fil d'Ariane au numéro du ticket reste lisible en entier pendant le zoom
                    zoom('#t4-note .feuille', s=1.3, d=0.6, fx=0.48, fy=0.9),
                    bulle('b-folio', '#t4-dd', cote='gauche', d=3.0),
                    curseur('#t4-dd-0209', fx=0.3, d=0.4), survol('#t4-dd-0209'), anneau('#t4-dd-0209', d=1.2),
                    clic('#t4-dd-0209', fx=0.3), cacher('#t4-dd', d=0.2), texte('#t4-fc-val', FOLIO_MARTIN),
                    classe('#t4-fc', retirer=['focus']), dezoom(d=0.5), anneau('#t4-fc', d=1.0)]},
        {'temps': 3, 'titre': '« Rattacher au folio »',
         'texte': 'La note passe « Rattachée » et quitte la file d\'attente.',
         'voix': "Un clic sur Rattacher au folio : la note passe Rattachée, la consommation rejoint le séjour, et la "
                 "ligne quitte la file. Sans folio ouvert, la note attend que le client prenne une chambre, ou se "
                 "règle au comptoir.",
         'gestes': [clic('#t4-b-ratt'), cacher('#t4-b-ratt', d=0.2), classe('#t4-nsb-0', retirer=['actif']),
                    classe('#t4-nsb-1', ajouter=['actif']), classe('#t4-fc', ajouter=['lecture']),
                    anneau('#t4-nsb', d=1.3), anneau('#t4-fc', d=1.0), clic('#t4-fil'), vue('t4-file2', 'hotel'),
                    pause(0.3), anneau('#t4-file2 .liste', d=1.4), curseur('#t4-file2-0-motif', fx=0.95, fy=0.85, d=0.5),
                    bulle('b-aucun', '#t4-file2-ancre', cote='bas', d=3.4), pause(3.0)]},
    ],
    'resultats': {
        'titre': 'Le bar encaisse, le folio suit',
        'cartes': [
            {'valeur': '3', 'compter': 3, 'unite': 'gestes', 'icone': 'coche',
             'texte': 'à la caisse : le client, « Note de chambre », Valider'},
            {'valeur': '1', 'compter': 1, 'unite': 'ligne', 'icone': 'document',
             'texte': 'par ticket sur le folio du séjour, avec la référence du ticket'},
            {'valeur': '7 000', 'compter': 7000, 'unite': 'FCFA', 'icone': 'pieces',
             'texte': 'reportés sur un ticket de 12 000 réglé 5 000 en espèces : seule la part « Note de chambre »'},
        ],
        'voix': "Trois gestes à la caisse, une seule ligne par ticket sur le folio, et seule la part réglée en note de "
                "chambre reportée.",
    },
    'cta': {
        'appel': 'Demandez votre démonstration',
        'suivant': 'La taxe de séjour',
        'voix': "Aïte haousse, par Aïte Consulting. Demandez votre démonstration. Prochain tutoriel : la taxe de "
                "séjour.",
    },
    'vignette': {'etape': 4, 'apres': 2.95},
}
