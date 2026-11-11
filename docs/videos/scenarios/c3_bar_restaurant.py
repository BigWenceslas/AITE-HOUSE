# -*- coding: utf-8 -*-
"""Chapitre 3 — Le bar et le restaurant (le point de vente).

Le caissier du bar (demo.POSTES['caisse'], Hervé Tchakounté) ouvre sa caisse
depuis le tableau de bord du Point de Vente, sert au comptoir, encaisse en
espèces, porte le dîner d'une cliente de l'hôtel sur sa chambre, puis compte
et ferme sa caisse le soir. Au restaurant, Larissa Mbida (caissière du
restaurant dans scenarios/t12_ventes.py, SESSIONS) travaille sur sa propre
caisse. Pas de plan de salle ni de tables : AITE HOUSE n'installe pas
pos_restaurant ; le restaurant est une caisse simple, comme le bar.

Sources des libellés (odoo18/addons, relevés mot pour mot ; fr.po =
point_of_sale/i18n/fr.po ; PS = point_of_sale/static/src/app) :

1. Tableau de bord des caisses — point_of_sale/views/point_of_sale_dashboard.xml
   :101-140 (nom de la caisse en gras, « Ouvrir la caisse » / « Continuer la
   vente » selon l'état de la session :113-116, « Fermeture » et date,
   « Solde » et montant :120-131, avatar du responsable de la session ouverte
   :140) ; fr.po:4808-4809, :2182-2183, :1861-1862, :1165-1166 ; menus
   « Tableau de bord » (pos_config_view.xml:184, fr.po:2484-2485), « Commandes »
   (fr.po:5076-5077), « Produits » (product_view.xml:108, fr.po:6330-6331),
   « Analyse » (point_of_sale_view.xml:24-27, sans groupe, fr.po:6641-6642) ;
   « Point de Vente » (fr.po:5661-5662). Cartes de 500 px au moins
   (static/src/scss/pos_dashboard.scss:1-5) : deux colonnes à l'échelle de la
   vidéo, comme scenarios/t12_ventes.py (POS). Carte d'une caisse ouverte :
   « Continuer la vente » et l'avatar de qui l'a ouverte (current_user_id,
   pos_config.py:354-368 ; capture ref_muk/701c).
2. Ouverture — le bouton du tableau de bord ouvre la caisse sans l'écran de
   connexion (odoo.from_backend : PS/store/pos_store.js:169-182) ; fenêtre
   « Contrôle à l'ouverture » : PS/store/opening_control_popup/
   opening_control_popup.xml:7-37 (« Espèces à l'ouverture », bouton billets,
   « Note d'ouverture », « Ajouter une note d'ouverture... », « Ouvrir la
   caisse », « Ignorer » ; fr.po:4845-4846, :4867-4868, :4898-4899, :683-684,
   :2769-2770) ; montant proposé = solde compté à la dernière clôture
   (opening_control_popup.js:27-32 et models/pos_session.py:383), formaté sans
   symbole. Aspect : ref_muk/702.
3. Écran de vente — PS/screens/product_screen/product_screen.xml:4-40 (pavé et
   « Paiement » seulement quand la commande n'est pas vide), PS/generic_components/
   order_widget/order_widget.xml:4-40 (« Commencez à ajouter des produits »,
   fr.po:7436-7437 ; « Total » ; ligne « Taxes » seulement s'il y a des
   groupes de taxes : la société de démonstration est sans TVA, docs/videos/
   DESIGN.md), product_card/product_card.xml:22-24 (la quantité déjà au ticket
   sur la tuile) ; « Rechercher des produits… » (PS/navbar/navbar.xml:19,
   fr.po:6955-6956), « Client » / nom du client (select_partner_button.xml:4-7,
   fr.po:2396-2397), « Note interne » (fr.po:3664-3665), « Actions »
   (fr.po:590-591), « Qté », « Prix » (fr.po:6408-6409, :5961-5962),
   « Paiement » (fr.po:5248-5249), « Unité(s) » (uom/i18n/fr.po:378-379). Numéro
   de suivi : (identifiant de session % 10) × 100 + rang du ticket
   (models/pos_order.py:58-60). Barre de la caisse (PS/navbar/navbar.xml) : le
   logo d'Odoo au centre (:9-11, /web/static/img/logo.png, image d'Odoo
   incrustée telle quelle) ; la recherche seulement sur l'écran de vente
   (showSearchButton, store/pos_store.js:2279-2284) et l'onglet seulement pour
   une commande non finalisée (get_open_orders, pos_store.js:1502-1503 ;
   navbar.js:67-69) : ni recherche au paiement et au reçu, ni onglet au reçu ;
   nom du caissier tronqué (.cashier-name, 190 px : navbar/cashier_name/
   cashier_name.scss:1-3, « Hervé Tchako… »). Tuiles : la pastille « i »
   (productInfo="true", product_screen.xml:38 ; product_card.xml:12-14 ;
   coin gris product_card.scss:42-60) ; couleur de la tuile = celle de sa
   catégorie (product_screen.xml:35). Aspect : ref_muk/703, 704, 712.
4. Paiement — PS/screens/payment_screen/payment_screen.xml:95-140 (« Client »
   qui prend le nom du client en couleur d'action, « Facture », « Retour »,
   « Valider »), payment_status/payment_status.xml:4-22 et .js:8-20
   (« Veuillez sélectionner un mode de paiement », « Restant » en rouge et
   montant en gras tant qu'il reste dû, en vert et en graisse normale à zéro
   (fw-bolder seulement si get_due() > 0, :10-12) ; « Monnaie » en vert,
   montant NÉGATIF à l'écran : formatCurrency(-get_change())) ; fr.po:5578-5579, :6618-6619,
   :1674-1675, :1117-1118, :9032-9033, :3697-3698 ; pavé « +10 », « +20 »,
   « +50 » (payment_screen.js:73-75) ; icônes des modes selon leur type
   (payment_screen.js:413-421), celles de scenarios/t04_note_chambre.py
   (ICO_ESPECES, ICO_BANQUE, ICO_PLUS_TARD) ; avertissement d'un mode « payer
   plus tard » sans facture, qui n'empêche pas de valider : payment_screen.js
   :113-125, fr.po:9096-9097 et :8632-8636 (ECARTS n° 43). Les modes, dans
   l'ordre de t04 (MODES) et t10 : « Espèces », « Orange Money », « MTN
   MoMo », « Note de chambre » (aite_hotel_pos_link/models/pos_payment_method.py
   :9-13), « Ardoise client » (aite_pos_credit/hooks.py:30). Le bouton « Mettre
   sur ardoise », pleine largeur, icône fa-book, violet #714B67 codé en dur :
   aite_pos_credit/static/src/js/pos/payment_screen_button.xml:10-21,
   static/src/scss/pos_credit_pos.scss:3-16. Aspect : ref_muk/706, 707, 709.
5. Reçu — PS/screens/receipt_screen/receipt_screen.xml:4-60 (« Paiement
   réussi », « Modifier le paiement », « Imprimer le reçu complet », courriel
   au texte indicatif non traduit « e.g. john.doe@mail.com », ou le courriel
   du client du ticket, pré-rempli (receipt_screen.js:23-26 ; bouton d'envoi
   désactivé sans adresse, isValidEmail), « Nouvelle commande » ;
   fr.po:5317-5318, :2923-2924, :6062-6063, :4427-4428) ;
   receipt/receipt_header/receipt_header.xml (logo de la société :4, l'image
   par défaut de res.company « Your logo », la société de démonstration n'en
   ayant pas d'autre, odoo/addons/base/models/res_company.py:27-29 ;
   « Tel:<span>… » traduit « Tél. : », d'où « Tél. :+237 6 00 00 00 10 »
   sans espace, :12 et fr.po:7740-7741 ; « Servi par %s », pos_store.js:
   2289-2295, fr.po:7077-7078) ;
   receipt/order_receipt.xml:44-75 (« TOTAL », une ligne par paiement,
   « MONNAIE » en positif, fr.po:7596-7597, :1324-1325 ; « Généré par Odoo »,
   fr.po:5929-5930 ; « Commande %s », pos_store.js:1177, fr.po:4928-4929).
   Mise en page reprise de scenarios/t10_ardoises.py (RECU). Aspect : ref_muk/708
   (espèces) et 710 (note de chambre).
6. Clôture — menu ☰ de la caisse : PS/navbar/navbar.xml:34-72 (icône écran
   client, « Installer l'application », « Commandes » et sa pastille,
   « Backend », « Fermer la caisse » ; fr.po:3620, :5076-5077, :1830-1831) ;
   fenêtre de clôture : PS/navbar/closing_popup/closing_popup.xml:4-118
   (« Fermeture de la caisse » et « <n> commandes : <total> » :8-11 ; bloc
   espèces : montant attendu, « Ouverture », « Paiement en Espèces »,
   « Cash entrant/sortant » « + 0 FCFA » (components/payment_method_breakdown/
   payment_method_breakdown.xml:5-13), « Compté », « Différence » en rouge et
   gras dès qu'elle n'est pas nulle :15-42 ; un bloc par autre mode :43-58 ;
   « Comptage de caisse » et ses deux boutons :61-70 ; pour un mode de type
   banque qui a des paiements, un champ « <mode> Count », traduit « Nombre »
   (« Orange Money Nombre ») :71-77 et fr.po:2222-2223 ; « Note de clôture »,
   « Ajouter une note de fermeture... » :78-90 ; chaque champ de comptage a sa
   croix d'effacement dès qu'il porte une valeur (generic_components/inputs/
   input/input.xml:23 ; « 0 » au départ pour les espèces) ; (« Note d'ouverture » seulement
   si une note a été saisie à l'ouverture) ; « Fermer la caisse », « Ignorer »,
   « Cash entrant/sortant », « Ventes du jour » :92-111) ; fr.po:1891-1892,
   :9700-9701, :4831-4832, :5393-5394, :1471-1472, :2229-2230, :2710-2711,
   :1453-1454, :1927-1928, :656-657, :1478-1479, :2468-2469 ; compté initial
   « 0 » pour les espèces, montant attendu pour un mode banque
   (closing_popup.js:66-80). « Écart de règlement » : closing_popup.js:82-99
   (« L'argent comptabilisé ne correspond pas à ce qui était prévu. Voulez-vous
   enregistrer la différence dans la comptabilité ? », « Poursuivre »,
   « Ignorer », croix de fermeture dans l'en-tête ; fr.po:5382-5383,
   :7938-7942, :6166-6167) : proposé au
   caissier parce qu'aucun écart maximal n'est réglé sur la caisse
   (:166-174). Aspect : ref_muk/712a, 712b, 712, 712c.
7. La direction retrouve l'écart — aite_pos_analytics 18.0.2.1.4 : toute
   session comptée dont l'écart n'est pas nul est listée dans « Écarts de
   caisse », classée par sévérité (models/pos_dashboard.py:654-687,
   models/pos_session.py:145-200 ; un manquant sous le seuil « Élevé » est
   « Modéré »), comme au tutoriel 12 (t12_ventes.py, SESSIONS : 2 000 FCFA
   manquants pour Hervé le 06/10).

Données de la soirée (mercredi 14/10/2026, la journée de la série) :
- tableau de bord : les trois caisses de scenarios/t12_ventes.py (POS, lu le
  matin même) — Bar de la terrasse fermé le 13/10 avec 25 000 FCFA, Restaurant
  le 13/10 avec 20 000 FCFA, Boutique le 26/09 avec 10 000 FCFA. Larissa a
  déjà ouvert le restaurant (session 00134, d'où le suivi 4xx) quand Hervé
  ouvre le bar (session 00135, suivi 5xx : t10_ardoises.py, NUMERO 504, et
  t04_note_chambre.py, 508) ; la caisse lui propose le montant compté à la
  dernière clôture, 25 000 FCFA (règle du code, sans parler de « fond fixe » :
  le solde compté du 14/10, 119 500, sera proposé le lendemain). Tension de
  numérotation, signalée (ECARTS.md, chapitre 3) : la série compte environ une
  session par jour, toutes caisses confondues (t12 SESSIONS : Restaurant/00122
  le 01/10, Bar de la terrasse/00131 le 10/10 ; 00135 le 14/10 dans t04 et
  t10 ; 00137 le 16/10 dans t11) ; 00132 à 00134 doivent donc couvrir les
  sessions du bar et du restaurant du 11 au 14/10, ce qui suppose des sessions
  de plusieurs jours (le restaurant, une vingtaine de tickets en treize jours
  dans t12, ne ferme pas chaque soir) ; seul le suivi « 402 » est visible ;
- les neuf tickets du bar ce jour-là, « Bar de la terrasse/1353 » à « /1361 »
  (rythme de la caisse, environ 8,3 tickets par jour depuis le 04/05 :
  t11_fidelite.py, OUVERTURE_BAR et PAR_JOUR) : le premier, 501, à midi,
  Bière blonde 65 cl × 2, Brochettes de bœuf, Plantain frit (prix de
  t12_ventes.py, ARTICLES), 7 500 FCFA réglés avec un billet de 10 000 ; le
  quatrième, 504, celui de Cédric Ngassa (t10 : 5 000 en espèces, 7 500 sur
  l'ardoise) ; le huitième, 508, le dîner de Brigitte Essomba,
  « Bar de la terrasse/1360 », 13 500 FCFA en note de chambre, validé à
  20:47, reporté sur FOL/2026/0210 (t04) ; les six autres, fictifs
  (TICKETS_JOUR ; 506, 45 000 FCFA en espèces, est une table : par exemple
  12 Bière blonde 65 cl, 3 Poisson braisé et 4 Plantain frit, tous à la carte
  du bar). Clôture :
  9 commandes, 167 500 FCFA ; espèces attendues 25 000 + 95 000 =
  120 000 FCFA, comptées 119 500 : 500 FCFA manquants, « Modéré » ; Orange
  Money 27 000, MTN MoMo 24 500, Note de chambre 13 500, Ardoise client 7 500.
  Après clôture, la carte du bar affiche « Fermeture 14/10/2026 » et le solde
  compté. Ces ventes ne changent aucun chiffre de caisse déjà montré : t12,
  t15 et c6 lisent les ventes le 14 au matin, du 01 au 13/10 (le stock de
  t13 et c5 ne détaille pas les tickets) ;
- au restaurant, le deuxième ticket du jour, 402 : Ndolè, Poulet DG, Bâton de
  manioc × 2, Vin rouge 75 cl (prix de t12, ARTICLES), 27 000 FCFA en MTN
  MoMo ; panier dans la moyenne du restaurant (t12 : 573 500 FCFA pour 20
  tickets du 01 au 13/10) ;
- les deux cartes sortent d'une seule table, article → catégorie de caisse
  (CATEGORIE_ARTICLE) : Odoo choisit les articles d'une caisse par
  available_in_pos et sale_ok, puis, si ses catégories sont limitées, par
  catégorie (models/pos_config.py:779-804, models/product.py:74-77) ; une
  catégorie commune aux deux caisses y montre donc les mêmes tuiles, et les
  catégories ont un seul ordre pour toute la base (models/pos_category.py:15,
  _order = "sequence, name"). Le bar a les cinq catégories, les articles et
  les couleurs de scenarios/t04_note_chambre.py (CATEGORIES, CARTE_BAR) ; le
  restaurant les a aussi, plus « Vins & spiritueux », absente du bar, avec
  les vins que t12 y vend (Vin rouge, Vin blanc, Vin rosé 75 cl) : 27 tuiles,
  six catégories dans le même ordre qu'au bar. Le ticket de Brigitte et les
  icônes des modes : t04 (LIGNES_TICKET, MODES).
Société sans TVA (DESIGN.md) : ni ligne « Taxes » à l'écran de vente, ni
bloc des taxes au reçu. Base mono-société : le nom de la société dans la
barre, rien de réservé à base.group_multi_company.

Écarts du produit relevés en écrivant ce chapitre (signalés ; le n° 78 est
corrigé depuis, les autres non ; captures de référence ref_muk/701 à 720, base aite_demo ; repris
dans ECARTS.md : n° 78, 79, 80, et la ligne « Série, chapitre 3 ») :
1. BLOQUANT (ECARTS n° 78, qui rouvre le n° 10) — aite_hotel_pos_link 18.0.1.0.2 : un caissier au seul profil
   « Point de Vente / Utilisateur » ne peut valider AUCUNE vente, même en
   espèces. Le champ pos.order.aite_folio_line_ids (One2many vers
   aite.hotel.folio.line, models/pos_order.py:39-42, sans groups=) est relu
   à chaque synchronisation : sync_from_ui → read_pos_data lit tous les
   champs de la commande (point_of_sale/models/pos_order.py:1206-1212 ;
   pos.order ne restreint pas _load_pos_data_fields, pos_load_mixin.py:9-11).
   La lecture lève « Erreur d'accès … 'Ligne de folio' … Gestion
   Hôtelière/Réception » (ref_muk/720) et chaque essai consomme un numéro de
   commande. Le chapitre montre les ventes validées, comme la série
   (t04_note_chambre.py, « Conditions ») : l'écran de la caisse est le même
   avec le contournement (profil Réception ajouté au caissier). Le test
   test_cashier_without_hotel_profile_posts_to_folio crée la commande par
   l'ORM et ne joue pas cette relecture. Corrigé dans aite_hotel_pos_link
   18.0.1.0.3 (livraison 5) : le champ est réservé au profil Réception, et
   test_cashier_without_hotel_profile_reads_back_order joue read_pos_data
   sous un caissier sans profil hôtel. Le chapitre montre donc le produit
   tel qu'il est, sans contournement.
2. aite_pos_credit (ECARTS n° 79) : « Mettre sur ardoise » est violet #714B67 codé en dur
   (pos_credit_pos.scss:3-6), et non la couleur primaire de l'interface : sur
   Odoo Community (#71639E) comme sous le thème MuK, c'est le seul bouton de
   cette teinte. Rejoué tel quel.
3. Odoo standard, rejoués tels quels : monnaie négative à l'écran
   (« Monnaie -2 500 FCFA ») et positive au reçu ; avertissement « soldes
   dûs » (ECARTS n° 43) ; « e.g. john.doe@mail.com » non traduit ;
   « Cash entrant/sortant » ; « Orange Money Nombre » (« Count » traduit
   « Nombre ») ; une session ouverte depuis la caisse est renommée
   « POS/000NN » (pos_session.py:1786-1792) : la vidéo ne montre aucun nom de
   session.
4. Série vidéo : ecrans.MENUS_MUK['point_de_vente_caisse'] omet « Analyse »,
   que le caissier voit (menu « Reporting » sans groupe, entrée
   « Commandes », pos_order_report_view.xml:106 ; ref_muk/701b) ; la barre de
   ce chapitre l'affiche. La caisse range les tuiles par nom
   (product_screen.js:417-419), quand t04 et t10 les rangent par catégorie :
   ce chapitre suit le code, avec la carte de t04 (mêmes articles, mêmes
   couleurs). Les sessions du bar s'appellent « Bar de la terrasse/00131 »
   dans t12 (voir 3 : « POS/000NN » une fois ouvertes depuis la caisse).
   La carte du bar de t04 (et de t10) n'a ni vin ni spiritueux, alors que t12
   fait vendre au bar Vin rouge 75 cl (10), Champagne brut 75 cl (10),
   Whisky 12 ans 70 cl (11), Gin 70 cl (13)… et au restaurant des articles
   absents des deux cartes (Koki, Okok, Kondrè, Porc braisé, Riz blanc… :
   HORS_CARTE) ; ce chapitre garde la carte de t04 et ne met les vins qu'au
   restaurant, sans dire que le bar n'en vend pas. Le reçu de t10 écrit
   « Tél. : +237… » (le produit : « Tél. :+237… ») et omet « Commande »
   devant la référence (« Order %s », fr.po:4928-4929) ; ce chapitre suit le
   produit. Tous relevés dans ECARTS.md (présentation, chapitre 3).
5. Recette (ECARTS n° 80) : le cas E01 (recette/cas_de_test.py:279-284) attend que « le
   ticket mentionne la chambre » ; le reçu d'une note de chambre ne mentionne
   ni chambre ni folio (ref_muk/710), et la caisse ne signale pas le report.

Mise en scène : d'un écran plein à l'autre (tableau de bord, caisse du bar,
caisse du restaurant), le nouveau se pose sur l'ancien, ou l'ancien s'efface
au-dessus du nouveau (fondu croisé de 0,3 s) : jamais d'éclair de la barre du
back-office entre deux caisses. Les textes des fenêtres posées sur la caisse
portent data-layout-allow-overlap (superpose). Raccourcis signalés : après
« Poursuivre », Odoo recharge la caisse (closing_popup.js:179, 248) ; le
contrôleur /pos/ui, sans session ouverte, en crée une (controllers/main.py:
56-60, models/pos_config.py:700-702), le caissier oublié, l'écran d'accueil
s'affiche (« Ouvrir la caisse », « Backend », ref_muk/702a) et « Backend »
supprime cette session en contrôle d'ouverture (models/pos_session.py:
194-205) ; la vidéo passe droit au tableau de bord, dont l'état final est
juste. Les ventes 502 à 507 et 509 ne sont pas jouées (le numéro passe de 508
à 510) ; le reçu du restaurant n'est pas montré (la scène quitte le
restaurant au clic sur « Valider ») ; le reçu n'a pas de courriel de la
société (demo.py n'en donne pas). L'avertissement « soldes dûs » reste ses
sept secondes (autocloseDelay: 7000, payment_screen.js:113-125), jusque sur
le reçu, comme dans Odoo. « Valider », pâle tant que le paiement n'est pas
complet (bouton désactivé d'Odoo), et la ligne « Cash entrant/sortant » de la
clôture, à demi-opacité tant qu'il n'y a aucun mouvement (accordéon
désactivé), sont soustraits au contrôle de contraste (data-layout-ignore).
"""

import base64
import os
import re
import unicodedata
from datetime import date

import demo
from ecrans import ICONES, MENUS_MUK, e, entier, entree, fcfa, fenetre, icone, recherche, toast, vue_libre
from moteur import (animer, anneau, cacher, clic, classe, defiler, fermer, montrer, notifier, ouvrir, pause, saisir,
                    texte, vue)
from scenarios import t04_note_chambre as t04
from scenarios import t10_ardoises as t10
from scenarios import t11_fidelite as t11
from scenarios import t12_ventes as t12

NOM, ROLE = demo.POSTES['caisse']                   # Hervé Tchakounté, Caissier du bar
CAISSIERE = 'Larissa Mbida'                         # caissière du restaurant (t12_ventes.py, SESSIONS)
assert CAISSIERE in [s[2] for s in t12.SESSIONS if s[3] == t12.RESTO]
BAR, RESTO, BOUT = t12.BAR, t12.RESTO, t12.BOUT
JOUR = '14/10/2026'

# Les menus du caissier (point_of_sale/views) : ceux de ecrans.MENUS_MUK['point_de_vente_caisse'], plus « Analyse »
# (menu « Reporting » sans groupe, entrée « Commandes » ouverte au caissier : écart n° 4 de l'en-tête).
MENUS = MENUS_MUK['point_de_vente_caisse'] + ['Analyse']

# ---------------------------------------------------------------- la carte --
PRIX = {a[0]: a[2] for a in t12.ARTICLES}           # prix de vente de t12 (et de t13) ; sans taxe


def ligne(nom, qte):
    """(article, quantité, prix unitaire, montant) d'une ligne de ticket, au prix de t12."""
    return nom, qte, PRIX[nom], qte * PRIX[nom]


# Le ticket de Brigitte Essomba, celui de t04 (Bar de la terrasse/1360) : mêmes articles, mêmes prix.
BRIGITTE = [ligne('Poisson braisé', 1), ligne('Plantain frit', 1), ligne('Bière blonde 65 cl', 2),
            ligne('Jus de bissap 50 cl', 2)]
assert [(n, '%d,00' % q, fcfa(p), fcfa(m)) for n, q, p, m in BRIGITTE] == [l[1:] for l in t04.LIGNES_TICKET]
assert fcfa(sum(l[3] for l in BRIGITTE)) == t04.TICKET == fcfa(13500)
# Le premier ticket du jour au bar, à midi, et le dîner servi au restaurant.
MIDI = [ligne('Bière blonde 65 cl', 2), ligne('Brochettes de bœuf', 1), ligne('Plantain frit', 1)]
DINER = [ligne('Ndolè', 1), ligne('Poulet DG', 1), ligne('Bâton de manioc', 2), ligne('Vin rouge 75 cl', 1)]
T_MIDI, T_DINER = sum(l[3] for l in MIDI), sum(l[3] for l in DINER)
assert (T_MIDI, T_DINER) == (7500, 27000)
RECU, RENDU = 10000, 10000 - T_MIDI                 # un billet de 10 000 ; 2 500 rendus


def alpha(nom):
    """L'ordre des tuiles : la caisse les trie par nom (localeCompare, accents ignorés : product_screen.js:417-419)."""
    return ''.join(c for c in unicodedata.normalize('NFD', nom) if not unicodedata.combining(c)).casefold()


# Les deux cartes sortent d'une seule table : chaque article de caisse et sa catégorie de point de vente
# (pos.category). Odoo choisit les articles d'une caisse par available_in_pos et sale_ok, puis, si ses catégories sont
# limitées, par catégorie (pos_config.py:779-804) : une catégorie commune aux deux caisses y montre les mêmes tuiles.
# Les catégories ont un seul ordre pour toute la base (pos_category.py:15, _order = "sequence, name") : le même aux
# deux écrans. Le bar a les cinq catégories de t04 (mêmes articles, mêmes couleurs) ; le restaurant les a aussi, plus
# « Vins & spiritueux », absente du bar : les vins que t12 vend au restaurant (q_resto > 0, ou vendus puis remboursés
# au restaurant). Écart de série (en-tête, 4) : t12 fait vendre au bar des vins et des spiritueux que la carte de t04
# ne propose pas, et au restaurant des articles absents des deux cartes (HORS_CARTE).
VINS = '#F3D3DF'
CATEGORIES = t04.CATEGORIES + [('Vins & spiritueux', VINS)]
COULEUR_CAT = dict(CATEGORIES)
_CAT_T04 = {c: n for n, c in t04.CATEGORIES}                          # couleur de t04 → nom de la catégorie
CATEGORIE_ARTICLE = dict([(n, _CAT_T04[c]) for n, c in t04.CARTE_BAR]
                         + [(a[0], 'Vins & spiritueux') for a in t12.ARTICLES
                            if a[1] == 'Vins & spiritueux' and (a[5] > 0 or a[6] == RESTO)])
CATS_CAISSE = {BAR: [n for n, _ in t04.CATEGORIES], RESTO: [n for n, _ in CATEGORIES]}


def categories(caisse):
    """Les boutons de catégorie d'une caisse, dans l'ordre unique de la base."""
    return [(n, c) for n, c in CATEGORIES if n in CATS_CAISSE[caisse]]


def carte(caisse):
    """Les tuiles d'une caisse : tous les articles de ses catégories, triés par nom comme la caisse."""
    return sorted(((n, COULEUR_CAT[c]) for n, c in CATEGORIE_ARTICLE.items() if c in CATS_CAISSE[caisse]),
                  key=lambda x: alpha(x[0]))


CATS_BAR, CATS_RESTO = categories(BAR), categories(RESTO)
CARTE_BAR, CARTE_RESTO = carte(BAR), carte(RESTO)
assert sorted(CARTE_BAR) == sorted(t04.CARTE_BAR) and CATS_BAR == t04.CATEGORIES
assert [c for c in CATS_RESTO if c not in CATS_BAR] == [('Vins & spiritueux', VINS)]
assert all(c in CARTE_RESTO for c in CARTE_BAR) and len(CARTE_RESTO) <= 30
assert all(n in PRIX for n in CATEGORIE_ARTICLE)
assert all(n in [c[0] for c in CARTE_RESTO] for n, _, _, _ in DINER)
assert all(n in [c[0] for c in CARTE_BAR] for n, _, _, _ in MIDI + BRIGITTE)
# Ce que t12 vend à chaque caisse (q_bar / q_resto > 0, ou vendu puis remboursé là) sans que sa carte le propose.
HORS_CARTE = {k: [a[0] for a in t12.ARTICLES if (a[4 if k == BAR else 5] > 0 or a[6] == k)
                  and a[0] not in [c[0] for c in carte(k)]] for k in (BAR, RESTO)}
assert HORS_CARTE[BAR] == ['Soda orange 33 cl', 'Biscuits apéritifs', 'Chocolat noir 100 g', 'Vin rouge 75 cl',
                           'Vin blanc 75 cl', 'Champagne brut 75 cl', 'Whisky 12 ans 70 cl', 'Cognac VSOP 70 cl',
                           'Rhum ambré 70 cl', 'Gin 70 cl', 'Liqueur de café 70 cl', 'Whisky 12 ans (verre)',
                           'Cocktail maison']
assert HORS_CARTE[RESTO] == ['Eau minérale 1,5 L', 'Jus de gingembre 50 cl', 'Citronnade 50 cl', 'Porc braisé',
                             'Maquereau braisé', 'Koki', 'Okok', 'Kondrè', 'Riz blanc', 'Frites de pomme']

# ------------------------------------------------- les tickets de la soirée --
# La session du bar du 14/10 (00135) : neuf tickets, /1353 à /1361 (t11 : environ 8,3 par jour depuis le 04/05).
# (n° de commande, suivi, montant, [(mode, montant net)]) ; le net des espèces déduit la monnaie rendue.
ESP, OM, MOMO, NOTE, ARD = 'Espèces', 'Orange Money', 'MTN MoMo', 'Note de chambre', 'Ardoise client'
TICKETS_JOUR = [
    (1353, '501', T_MIDI, [(ESP, T_MIDI)]),                       # ce chapitre, à midi
    (1354, '502', 9000, [(OM, 9000)]),
    (1355, '503', 6000, [(ESP, 6000)]),
    (1356, '504', 12500, [(ESP, 5000), (ARD, 7500)]),             # Cédric Ngassa, 13:47 (t10_ardoises.py)
    (1357, '505', 24500, [(MOMO, 24500)]),
    (1358, '506', 45000, [(ESP, 45000)]),
    (1359, '507', 18000, [(OM, 18000)]),
    (1360, '508', 13500, [(NOTE, 13500)]),                       # Brigitte Essomba (t04_note_chambre.py)
    (1361, '509', 31500, [(ESP, 31500)]),
]
_j = (date(2026, 10, 14) - t11.OUVERTURE_BAR).days
assert all(t11.PAR_JOUR * _j <= n <= t11.PAR_JOUR * (_j + 1) for n, _, _, _ in TICKETS_JOUR)
assert all(sum(m for _, m in p) == mt for _, _, mt, p in TICKETS_JOUR)
assert (TICKETS_JOUR[3][1], '00135-001-0004') == (t10.NUMERO, t10.REF_TICKET)
assert t04.COMMANDE == '%s/%d' % (BAR, TICKETS_JOUR[7][0])
PAR_MODE = {m: sum(x for _, _, _, p in TICKETS_JOUR for mm, x in p if mm == m) for m in (ESP, OM, MOMO, NOTE, ARD)}
NB_CMD, CA_JOUR = len(TICKETS_JOUR), sum(t[2] for t in TICKETS_JOUR)
FOND = 25000                                         # solde de la clôture du 13/10 (t12_ventes.py, POS)
ATTENDU = FOND + PAR_MODE[ESP]
COMPTE = 119500
ECART = COMPTE - ATTENDU
assert (NB_CMD, CA_JOUR, PAR_MODE[ESP], ATTENDU, ECART) == (9, 167500, 95000, 120000, -500)
assert -ECART < t12.SEUIL_ELEVE                      # « Modéré » dans Écarts de caisse (t12_ventes.severite)


# ================================================== tableau de bord des caisses --
KANBAN = ('<svg viewBox="0 0 24 24" fill="currentColor"><rect x="3" y="4" width="7.5" height="16" rx="1"/>'
          '<rect x="12.5" y="4" width="8.5" height="7.5" rx="1"/></svg>')       # t12_ventes.py (KANBAN)


def carte_caisse(code, nom, fermeture, solde, ouverte=None):
    """Une carte du tableau de bord (point_of_sale_dashboard.xml:101-140) ; ``ouverte`` : (initiale, couleur)
    de qui a ouvert la session en cours."""
    bt = 'Continuer la vente' if ouverte else 'Ouvrir la caisse'
    av = ('<span class="cb-pc-av" style="background:%s">%s</span>' % (ouverte[1], e(ouverte[0]))) if ouverte else ''
    return ('<div class="cb-pc" id="cb-k-%s"><div class="cb-pc-n">%s</div><span class="cb-pc-bt" id="cb-k-%s-bt">%s</span>'
            '<div class="cb-pc-i" id="cb-k-%s-i"><span>Fermeture</span><span id="cb-k-%s-date">%s</span><span>Solde</span>'
            '<span id="cb-k-%s-solde">%s</span></div>%s</div>'
            % (code, e(nom), code, e(bt), code, code, e(fermeture), code, e(solde), av))


AV_LARISSA = '#0F6E56'
CP_DASH = ('<div class="cp"><span class="titre">Point de Vente</span>%s<span class="pager">1-3 / 3</span>'
           '<span class="cb-vues"><i class="on">%s</i><i>%s</i></span></div>' % (recherche(), KANBAN, ICONES['liste']))
# Ordre de création des caisses : Bar, Restaurant, Boutique (t12_ventes.py, COULEUR_CAISSE).
DASH = vue_libre('cb-dash', CP_DASH + '<div class="cb-pk">%s%s%s</div>' % (
    carte_caisse('bar', BAR, '13/10/2026', fcfa(FOND)),
    carte_caisse('res', RESTO, '13/10/2026', fcfa(20000), ouverte=(CAISSIERE[0], AV_LARISSA)),
    carte_caisse('bou', BOUT, '26/09/2026', fcfa(10000))), initiale=True)


# ============================================================== la caisse --
CHARIOT = ('<svg viewBox="0 0 24 24" fill="currentColor"><path d="M1 3h3.2l.7 2.6H22l-2.6 9H7.6l.5 1.9H20v2H6.6L3.1 5H1z"/>'
           '<circle cx="9" cy="21" r="1.8"/><circle cx="18" cy="21" r="1.8"/></svg>')
BILLETS = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="2" y="6" width="20" '
           'height="12" rx="2"/><circle cx="12" cy="12" r="2.8"/><path d="M5.5 9.5v5M18.5 9.5v5"/></svg>')
COPIER = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="8" y="8" width="13" '
          'height="13" rx="1.5"/><path d="M16 8V4.5A1.5 1.5 0 0014.5 3h-10A1.5 1.5 0 003 4.5v10A1.5 1.5 0 004.5 16H8"/></svg>')
ECRAN_CLI = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2.5" y="4" width="19" '
             'height="12.5" rx="1"/><path d="M8 20.5h8M12 16.5v4"/></svg>')
# La croix de fermeture d'une fenêtre (btn-close de Bootstrap, ref_muk/712c), dessinée sans texte.
CROIX = ('<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M2.5 2.5l11 11M13.5 2.5l-11 11"/>'
         '</svg>')
LIVRE = ('<svg viewBox="0 0 24 24" fill="currentColor"><path d="M6 3h11a2 2 0 012 2v12H7.5a1.5 1.5 0 000 3H19v1H7.5A3.5 3.5 '
         '0 014 17.5V5a2 2 0 012-2z"/></svg>')                                      # fa-book, comme t10_ardoises.py
CERCLE_OK = t10.CERCLE_OK
ENVOI = t10.ENVOI
# La pastille « i » des tuiles (productInfo="true", product_screen.xml:38 ; product_card.xml:12-14, fa-info en blanc
# sur un coin gris #9a9ea180, product_card.scss:42-60) : le « i » est dessiné en SVG, sans texte.
INFO = ('<svg viewBox="0 0 8 16" fill="#fff"><circle cx="4" cy="2.4" r="1.9"/><path d="M1.2 6h4.3v7.6H7V16H1v-2.4h1.5V8.4H1.2z"/>'
        '</svg>')
# Deux images d'Odoo, jamais redessinées : le logo de la barre de la caisse (navbar.xml:9-11,
# /web/static/img/logo.png) et le logo de la société en tête du reçu (receipt_header.xml:4) ; la société de
# démonstration n'a pas de logo à elle : c'est l'image par défaut de res.company (« Your logo »,
# odoo/addons/base/models/res_company.py:27-29), comme sur la capture ref_muk/708.
ODOO = os.environ.get('ODOO_DIR', os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'odoo18')))


def image_odoo(relatif):
    with open(os.path.join(ODOO, relatif), 'rb') as f:
        return 'data:image/png;base64,' + base64.b64encode(f.read()).decode()


LOGO_ODOO = image_odoo('addons/web/static/img/logo.png')
LOGO_SOCIETE = image_odoo('odoo/addons/base/static/img/res_company_logo.png')
TOUCHES_VENTE = (('1', ''), ('2', ''), ('3', ''), ('Qté', ' sel'), ('4', ''), ('5', ''), ('6', ''), ('%', ' gr'),
                 ('7', ''), ('8', ''), ('9', ''), ('Prix', ' gr'), ('+/-', ' jaune'), ('0', ''), (',', ' rose'),
                 ('⌫', ' rouge'))
TOUCHES_PAIE = (('1', ''), ('2', ''), ('3', ''), ('+10', ' vert'), ('4', ''), ('5', ''), ('6', ''), ('+20', ' vert'),
                ('7', ''), ('8', ''), ('9', ''), ('+50', ' vert'), ('+/-', ' jaune'), ('0', ''), (',', ' rose'),
                ('⌫', ' rouge'))


def _code(t):
    return {'+/-': 'pm', ',': 'v', '⌫': 'eff', 'Qté': 'q', '%': 'pc', 'Prix': 'px'}.get(t, t.replace('+', 'p'))


def pave(ident, touches):
    return '<div class="pos-pave">%s</div>' % ''.join(
        '<span class="pk%s" id="%s-k%s">%s</span>' % (c, ident, _code(t), e(t)) for t, c in touches)


def ligne_ticket(ident, nom, qte, prix, montant, cache=False, sel=False):
    """Une ligne du ticket (generic_components/orderline) : article et montant, puis « 2,00 x 1 500 FCFA / Unité(s) »."""
    return ('<div class="pv-ligne%s%s" id="%s"><div class="a"><b>%s</b><span id="%s-m">%s</span></div>'
            '<div class="q"><b id="%s-q">%d,00</b> x %s / Unité(s)</div></div>'
            % (' masque' if cache else '', ' sel' if sel else '', ident, e(nom), ident, e(fcfa(montant)), ident, qte,
               e(fcfa(prix))))


def tuiles(ident, carte, qtes=None):
    """Les tuiles ; ``qtes`` : {article: quantité au ticket}, affichée sur la tuile (product_card.xml:22-24)."""
    qtes = qtes or {}
    return ''.join('<span class="pos-tuile" id="%s-t%d" style="background:%s"><span class="cb-info">%s</span><span>%s</span>'
                   '<b class="cb-qte%s" id="%s-t%d-q">%s</b></span>'
                   % (ident, i, c, INFO, e(n), '' if n in qtes else ' masque', ident, i, qtes.get(n, ''))
                   for i, (n, c) in enumerate(carte))


def droite_vente(ident, categories, carte, qtes=None):
    cats = ''.join('<span class="pos-cat" style="background:%s">%s</span>' % (c, e(n)) for n, c in categories)
    return ('<div class="pos-d"><div class="pos-cats" id="%s-cats">%s</div><div class="pos-tuiles">%s</div></div>'
            % (ident, cats, tuiles(ident, carte, qtes)))


def actions(ident, client=None):
    nom = ('<b class="cb-nomcli">%s</b>' % e(client)) if client else 'Client'
    return ('<div class="pos-acts"><span id="%s-cli">%s</span><span>Note interne</span><span class="dr">Actions</span></div>'
            % (ident, nom))


def gauche_pleine(ident, lignes_html, total, client=None):
    return ('<div class="pos-ticket" id="%s-ticket">%s</div><div class="pos-tot"><b>Total<span id="%s-total">%s</span></b>'
            '</div>%s%s<div class="pos-payer" id="%s-payer">Paiement</div>'
            % (ident, lignes_html, ident, e(total), actions(ident, client), pave(ident, TOUCHES_VENTE), ident))


def gauche_vide(ident):
    return ('<div class="cb-vide"><span class="cb-chariot">%s</span><span>Commencez à ajouter des produits</span></div>%s'
            % (CHARIOT, actions(ident + '-0')))


def vente_vide(ident, categories, carte, initiale=False):
    """L'écran de vente d'une commande vide : ni total, ni pavé, ni « Paiement » (product_screen.xml:13-20)."""
    return ('<div class="vue%s" id="%s"><div class="pos-vente"><div class="pos-g">%s</div>%s</div></div>'
            % (' initiale' if initiale else '', ident, gauche_vide(ident), droite_vente(ident, categories, carte)))


def vente_midi(ident, categories, carte, lignes):
    """L'écran de vente qui passe de vide à rempli au premier article."""
    lh = ''.join(ligne_ticket('%s-l%d' % (ident, i), n, 1, p, p, cache=True) for i, (n, q, p, m) in enumerate(lignes))
    return ('<div class="vue initiale" id="%s"><div class="pos-vente"><div class="pos-g cb-pile">'
            '<div class="cb-g" id="%s-vide">%s</div><div class="cb-g masque" id="%s-plein">%s</div></div>%s</div></div>'
            % (ident, ident, gauche_vide(ident), ident, gauche_pleine(ident, lh, fcfa(0)),
               droite_vente(ident, categories, carte)))


def vente_pleine(ident, categories, carte, lignes, client=None):
    n = len(lignes)
    lh = ''.join(ligne_ticket('%s-l%d' % (ident, i), nm, q, p, m, sel=(i == n - 1)) for i, (nm, q, p, m) in enumerate(lignes))
    return ('<div class="vue" id="%s"><div class="pos-vente"><div class="pos-g">%s</div>%s</div></div>'
            % (ident, gauche_pleine(ident, lh, fcfa(sum(l[3] for l in lignes)), client),
               droite_vente(ident, categories, carte, {nm: q for nm, q, _, _ in lignes})))


MODES = [('esp', ESP, t04.ICO_ESPECES), ('om', OM, t04.ICO_BANQUE), ('momo', MOMO, t04.ICO_BANQUE),
         ('note', NOTE, t04.ICO_PLUS_TARD), ('ard', ARD, t04.ICO_PLUS_TARD)]
assert [m[1] for m in MODES] == [m[1] for m in t04.MODES]


def paiement(ident, du, ligne_mode, client=None):
    """L'écran de paiement (payment_screen.xml) : les cinq modes, Client / Facture, « Mettre sur ardoise », le pavé,
    Retour / Valider ; à droite le montant dû, puis l'état (« Restant », « Monnaie ») et la ligne de paiement.
    « Valider » reste pâle tant que le paiement n'est pas complet (bouton désactivé d'Odoo) : volontairement peu
    contrasté, il est soustrait au contrôle de contraste (data-layout-ignore)."""
    modes = ''.join('<div class="pos-mode" id="%s-%s"><span class="ico">%s</span><span>%s</span></div>' % (ident, c, s, e(l))
                    for c, l, s in MODES)
    cli = ('<b class="cb-nomcli">%s</b>' % e(client)) if client else 'Client'
    gauche = ('<div class="pos-g"><div class="pos-modes" id="%s-modes">%s</div>'
              '<div class="pos-cf"><span id="%s-cli"><em class="cb-ico">%s</em>%s</span>'
              '<span><em class="cb-ico">%s</em>Facture<i></i></span></div>'
              '<div class="pos-ardoise" id="%s-ardoise"><span class="ico">%s</span>Mettre sur ardoise</div>%s'
              '<div class="pos-rv"><span>Retour</span><span class="v cb-off" id="%s-valider" data-layout-ignore>Valider'
              '</span></div></div>'
              % (ident, modes, ident, ICONES['personne'], cli, ICONES['document'], ident, LIVRE,
                 pave(ident, TOUCHES_PAIE), ident))
    droite = ('<div class="pos-d pos-pd"><div class="pos-du">%s</div>'
              '<div class="cb-choix" id="%s-msg">Veuillez sélectionner un mode de paiement</div>'
              '<div class="cb-zone"><div class="cb-pile">'
              '<div class="cb-st cb-vert cb-zero masque" id="%s-ok"><span>Restant</span><b>%s</b></div>'
              '<div class="cb-st cb-rouge masque" id="%s-du"><span>Restant</span><b id="%s-du-v">%s</b></div>'
              '<div class="cb-st cb-vert masque" id="%s-mon"><span>Monnaie</span><b id="%s-mon-v">%s</b></div></div>'
              '<div class="pos-pl masque" id="%s-pl"><span>%s</span><span id="%s-pl-v">%s</span><span class="x">×</span>'
              '</div></div></div>'
              % (e(fcfa(du)), ident, ident, e(fcfa(0)), ident, ident, e(fcfa(du)), ident, ident, e(fcfa(0)), ident,
                 e(ligne_mode), ident, e(fcfa(du))))
    return '<div class="vue" id="%s"><div class="pos-vente">%s%s</div></div>' % (ident, gauche, droite)


def recu(ident, numero, lignes, paiements, monnaie, reference, heure, courriel=None):
    """Le reçu (receipt_screen.xml, order_receipt.xml), mis en page comme celui de t10_ardoises.py (RECU), avec le
    logo de la société en tête (receipt_header.xml:4). ``courriel`` : celui du client du ticket, pré-rempli
    (receipt_screen.js:23-26) ; sans client, le texte indicatif et le bouton d'envoi désactivé (isValidEmail)."""
    tirets = '<div class="cb-tirets">--------------------------------</div>'
    lr = ''.join('<div class="pv-ligne cb-rl"><div class="a"><b>%s</b><b>%s</b></div><div class="q"><b>%d,00</b> x %s / '
                 'Unité(s)</div></div>' % (e(n), e(fcfa(m)), q, e(fcfa(p))) for n, q, p, m in lignes)
    total = sum(l[3] for l in lignes)
    pl = ''.join('<div class="cb-rm" id="%s-p%d"><span>%s</span><span>%s</span></div>' % (ident, i, e(m), e(fcfa(x)))
                 for i, (m, x) in enumerate(paiements))
    mon = ('<div class="cb-rm cb-grand cb-monnaie" id="%s-monnaie"><span>MONNAIE</span><span>%s</span></div>'
           % (ident, e(fcfa(monnaie))) if monnaie else '')
    champ = ('<span class="cb-in cb-in-v">%s</span>' % e(courriel) if courriel
             else '<span class="cb-in">e.g. john.doe@mail.com</span>')
    return (
        '<div class="vue" id="%s"><div class="cb-recu"><div class="cb-actions"><div class="cb-reussi">'
        '<span class="cb-okico">%s</span><b>Paiement réussi</b><div class="cb-mt"><span>%s</span>'
        '<span class="cb-modif">Modifier le paiement</span></div></div><hr>'
        '<span class="cb-imprimer"><span class="ico">%s</span>Imprimer le reçu complet</span>'
        '<div class="cb-mail">%s<span class="cb-envoi%s">%s</span></div>'
        '<div class="cb-nouv">Nouvelle commande</div></div>'
        '<div class="cb-recu-d"><div class="cb-ticket" id="%s-tk"><img class="cb-logo" src="%s" alt="">'
        '<div class="cb-ent"><div>%s</div><div>Tél. :%s</div>%s'
        '<div>Servi par %s</div><div class="cb-suivi">%s</div></div>%s%s'
        '<div class="cb-rm cb-grand cb-gras"><span>TOTAL</span><span>%s</span></div>%s%s'
        '<div class="cb-gen">Généré par Odoo<br>Commande %s<br>%s</div></div></div></div></div>'
        % (ident, CERCLE_OK, e(fcfa(total)), ICONES['imprimer'], champ, '' if courriel else ' cb-envoi-off', ENVOI, ident,
           LOGO_SOCIETE, e(demo.SOCIETE), e(demo.TEL_HOTEL), tirets, e(NOM), numero, lr, tirets, e(fcfa(total)), pl, mon,
           reference, heure))


def superpose(html):
    """Une fenêtre posée sur la caisse (ouverture, menu, clôture, écart, notification) : chacun de ses textes porte
    data-layout-allow-overlap, la superposition voulue que le contrôle de mise en page de HyperFrames attend sur le
    bloc de texte lui-même (layout-audit, hasAllowOverlapFlag)."""
    html = html.replace(' data-layout-allow-overlap', '')
    return re.sub(r'<(div|span|b|p|em)(?=[\s>])', r'<\1 data-layout-allow-overlap', html)


def couche_pos(ident, vues, caissier, numero, avatar, calques='', classe_=''):
    """La caisse plein écran (PS/navbar/navbar.xml) : nouvelle commande, onglet de la commande en cours, logo d'Odoo au
    centre, recherche, caissier, menu ; elle couvre la fenêtre d'Odoo, comme la page /pos/ui. La recherche n'existe
    que sur l'écran de vente (showSearchButton, pos_store.js:2279-2284) et l'onglet que pour une commande non finalisée
    (get_open_orders, pos_store.js:1502-1503) : les gestes les cachent au paiement et au reçu. Le nom du caissier est
    tronqué comme à l'écran (.cashier-name, 190 px : cashier_name.scss:1-3, « Hervé Tchako… » sur ref_muk/703)."""
    return ('<div class="cb-pos masque%s" id="%s"><div class="pos-haut"><span class="pos-plus">%s</span>'
            '<span class="pos-num" id="%s-num">%s</span><img class="cb-logo-odoo" src="%s" alt="">'
            '<span class="pos-cherche" id="%s-cherche">%sRechercher des produits…</span>'
            '<span class="pos-caissier" id="%s-cais"><span class="avatar" style="background:%s">%s</span>'
            '<span class="cb-cais-n">%s</span></span>'
            '<span class="pos-menu" id="%s-menu">☰</span></div><div class="pos-corps">%s</div>%s</div>'
            % (classe_, ident, ICONES['plus'], ident, e(numero), LOGO_ODOO, ident, icone('loupe'), ident, avatar,
               e(caissier[0]), e(caissier), ident, ''.join(vues), calques))


# -- la caisse du bar : le ticket de midi, son paiement et son reçu ; le dîner de Brigitte ; la clôture
I_BIERE, I_BROCH, I_PLANT = (next(i for i, c in enumerate(CARTE_BAR) if c[0] == n)
                             for n in ('Bière blonde 65 cl', 'Brochettes de bœuf', 'Plantain frit'))
V_MIDI = vente_midi('cb-v1', CATS_BAR, CARTE_BAR, MIDI)
P_MIDI = paiement('cb-p1', T_MIDI, ESP)
R_MIDI = recu('cb-r1', '501', MIDI, [(ESP, RECU)], RENDU, '00135-001-0001', '%s 12:18:40' % JOUR)
V_BRIG = vente_pleine('cb-v2', CATS_BAR, CARTE_BAR, BRIGITTE, client=t04.CLIENTE)
P_BRIG = paiement('cb-p2', 13500, NOTE, client=t04.CLIENTE)
# Le reçu du dîner de Brigitte (ref_muk/710) : une ligne « Note de chambre », pas de monnaie, son courriel pré-rempli
# (t04_note_chambre.py, BRIGITTE) ; ni chambre ni folio (écart n° 5 de l'en-tête).
assert t04.BRIGITTE[0] == t04.CLIENTE
R_BRIG = recu('cb-r2', TICKETS_JOUR[7][1], BRIGITTE, [(NOTE, 13500)], 0, '00135-001-0008', '%s 20:47:16' % JOUR,
              courriel=t04.BRIGITTE[3])
V_SOIR = vente_vide('cb-v3', CATS_BAR, CARTE_BAR)

# Le contrôle à l'ouverture : le solde de la veille, proposé sans symbole (formatCurrency(…, false)).
OUVERTURE = (
    '<div class="voile masque" id="cb-ouv-voile" data-layout-allow-overlap data-layout-allow-occlusion></div>'
    '<div class="modale masque cb-dlg" id="cb-ouv" style="top:150px;width:880px;margin-left:-440px" '
    'data-layout-allow-overlap data-layout-allow-occlusion><div class="cb-dlg-h">Contrôle à l\'ouverture</div>'
    '<div class="cb-dlg-c"><div class="cb-lab">Espèces à l\'ouverture</div><div class="cb-in-l">'
    '<span class="cb-champ" id="cb-ouv-mt"><span>%s</span><span class="cb-x">✖</span></span>'
    '<span class="cb-btn-ic">%s</span></div><div class="cb-lab">Note d\'ouverture</div>'
    '<div class="cb-zone-txt">Ajouter une note d\'ouverture...</div></div>'
    '<div class="cb-dlg-p"><span class="bt primaire" id="cb-ouv-ok">Ouvrir la caisse</span>'
    '<span class="bt gris">Ignorer</span></div></div>' % (e(entier(FOND)), BILLETS))

# Le menu ☰ de la caisse (navbar.xml:34-72) : la commande en cours compte pour une.
MENU = ('<div class="cb-menu masque" id="cb-menu" data-layout-allow-overlap data-layout-allow-occlusion>'
        '<div class="cb-menu-ecran"><span>%s</span></div><div class="cb-menu-l">'
        '<div>Installer l\'application</div><div>Commandes<span class="cb-pastille">1</span></div><div>Backend</div>'
        '<div id="cb-menu-fermer">Fermer la caisse</div></div></div>' % ECRAN_CLI)


def bloc_mode(ident, nom, attendu, compte, diff_html=None):
    diff = diff_html or '<span>%s</span>' % e(fcfa(0))
    return ('<div class="cb-cl-b"%s><div class="cb-cl-t"><span>%s</span><span>%s</span></div>'
            '<div class="cb-cl-s"><span>Compté</span><span>%s</span></div>'
            '<div class="cb-cl-s"><span>Différence</span>%s</div></div>'
            % (' id="%s"' % ident if ident else '', e(nom), e(fcfa(attendu)), e(fcfa(compte)), diff))


# La fenêtre de clôture : le corps défile (fenêtre modale d'Odoo) ; espèces comptées « 0 » au départ.
CLOTURE = (
    '<div class="voile masque" id="cb-clo-voile" data-layout-allow-overlap data-layout-allow-occlusion></div>'
    '<div class="modale masque cb-dlg cb-clo" id="cb-clo" data-layout-allow-overlap data-layout-allow-occlusion>'
    '<div class="cb-dlg-h"><span>Fermeture de la caisse</span><b class="cb-clo-n" id="cb-clo-n">%d commandes : %s</b></div>'
    '<div class="cb-clo-c"><div id="cb-clo-defil">'
    '<div class="cb-cl-b" id="cb-clo-esp"><div class="cb-cl-t"><span>Espèces</span><span>%s</span></div>'
    '<div class="cb-cl-s"><span>Ouverture</span><span>%s</span></div>'
    '<div class="cb-cl-s"><span>Paiement en Espèces</span><span>%s</span></div>'
    # « Cash entrant/sortant » sans mouvement : accordéon désactivé, toute la ligne à demi-opacité
    # (generic_components/accordion_item/accordion_item.scss:10-13), soustraite au contrôle de contraste
    '<div class="cb-cl-s cb-cl-acc" data-layout-ignore><span>▸ Cash entrant/sortant</span><span>+ %s</span></div>'
    '<div class="cb-cl-s"><span>Compté</span><span id="cb-clo-compte">%s</span></div>'
    '<div class="cb-cl-s cb-rougef" id="cb-clo-diffl"><span>Différence</span><span id="cb-clo-diff">%s</span></div></div>'
    '%s%s%s%s<hr><div class="cb-lab">Comptage de caisse</div><div class="cb-in-l">%s<span class="cb-btn-ic">%s</span>'
    '<span class="cb-btn-ic">%s</span></div>'
    '<div class="cb-lab">Orange Money Nombre</div><div class="cb-in-l"><span class="cb-champ cb-plein"><span>%s</span>'
    '<span class="cb-x">✖</span></span></div>'
    '<div class="cb-lab">MTN MoMo Nombre</div><div class="cb-in-l"><span class="cb-champ cb-plein"><span>%s</span>'
    '<span class="cb-x">✖</span></span></div>'
    '<div class="cb-lab">Note de clôture</div><div class="cb-zone-txt">Ajouter une note de fermeture...</div>'
    '</div></div><div class="cb-dlg-p"><span class="bt primaire" id="cb-clo-ok">Fermer la caisse</span>'
    '<span class="bt gris">Ignorer</span><span class="bt gris cb-dr">Cash entrant/sortant</span>'
    '<span class="bt gris">Ventes du jour<span class="cb-dl">⤓</span></span></div></div>'
    % (NB_CMD, e(fcfa(CA_JOUR)), e(fcfa(ATTENDU)), e(fcfa(FOND)), e(fcfa(PAR_MODE[ESP])), e(fcfa(0)), e(fcfa(0)),
       e(fcfa(-ATTENDU)),
       bloc_mode(None, OM, PAR_MODE[OM], PAR_MODE[OM]), bloc_mode(None, MOMO, PAR_MODE[MOMO], PAR_MODE[MOMO]),
       bloc_mode(None, NOTE, PAR_MODE[NOTE], 0), bloc_mode(None, ARD, PAR_MODE[ARD], 0),
       entree('cb-clo-in', '', '0', classe='cb-champ cb-saisie')[:-6] + '<span class="cb-x">✖</span></div>', BILLETS, COPIER,
       e(entier(PAR_MODE[OM])), e(entier(PAR_MODE[MOMO]))))

ECART_DLG = (
    '<div class="voile masque" id="cb-ecart-voile" data-layout-allow-overlap data-layout-allow-occlusion></div>'
    '<div class="modale masque cb-dlg" id="cb-ecart" style="top:230px;width:820px;margin-left:-410px" '
    'data-layout-allow-overlap data-layout-allow-occlusion><div class="cb-dlg-h"><span>Écart de règlement</span>'
    '<span class="cb-fermer">%s</span></div>'
    '<div class="cb-dlg-c"><p class="cb-ecart-txt" id="cb-ecart-txt">L\'argent comptabilisé ne correspond pas à ce qui '
    'était prévu. Voulez-vous enregistrer la différence dans la comptabilité ?</p></div>'
    '<div class="cb-dlg-p"><span class="bt primaire" id="cb-ecart-ok">Poursuivre</span><span class="bt gris">Ignorer</span>'
    '</div></div>' % CROIX)

AVERT = toast('cb-avert', 'Avertissement', "Pour assurer le suivi des soldes dûs, générez une facture ou téléchargez "
                                           "l'application comptabilité.", genre='alerte')

POS_BAR = couche_pos('cb-pb', [V_MIDI, P_MIDI, R_MIDI, V_BRIG, P_BRIG, R_BRIG, V_SOIR], NOM, '501', '#185FA5',
                     calques=superpose(OUVERTURE + MENU + CLOTURE + ECART_DLG + AVERT))

# -- la caisse du restaurant : le dîner, réglé en MTN MoMo
V_DINER = vente_pleine('cb-rv', CATS_RESTO, CARTE_RESTO, DINER).replace('class="vue"', 'class="vue initiale"', 1)
P_DINER = paiement('cb-rp', T_DINER, MOMO)
POS_RESTO = couche_pos('cb-pr', [V_DINER, P_DINER], CAISSIERE, '402', AV_LARISSA, classe_=' cb-resto')

ECRAN = fenetre('app-cb', 'Point de Vente', MENUS, [DASH], actif='Tableau de bord', societe=demo.SOCIETE,
                initiale=NOM[0], avatar='#185FA5', calques=POS_BAR + POS_RESTO)


# ------------------------------------------------------------------ styles --
# Le point de vente d'Odoo 18 Community, rejoué à l'échelle de la vidéo : les classes pos-* d'ecrans.py (styles des
# tutoriels, shared/aite-marketing.css, que la présentation ne charge pas), ici sous #app-cb et à la couleur
# primaire d'Odoo (--o-prim, #71639E) ; « Mettre sur ardoise » garde son violet codé en dur (écart n° 2).
CSS = """
/* -- tableau de bord des caisses (point_of_sale_dashboard.xml) -- */
#app-cb .cb-vues { margin-left: 18px; display: flex; }
#app-cb .cb-vues i { width: 48px; height: 42px; display: flex; align-items: center; justify-content: center; background: #E9ECEF; color: #343A40; }
#app-cb .cb-vues i + i { border-left: 1px solid #fff; }
#app-cb .cb-vues i.on { background: #E6E3EF; box-shadow: inset 0 0 0 1px var(--o-prim); }
#app-cb .cb-vues svg { width: 20px; height: 20px; }
#app-cb .cb-pk { position: absolute; left: 0; right: 0; top: 80px; padding: 18px 22px; display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
#app-cb .cb-pc { position: relative; height: 204px; background: #fff; border: 1px solid var(--o-filet); padding: 20px 26px; }
#app-cb .cb-pc-n { font-size: 25px; font-weight: 700; color: var(--o-texte); }
#app-cb .cb-pc-bt { position: absolute; left: 26px; top: 96px; height: 48px; padding: 0 18px; display: inline-flex; align-items: center;
  background: var(--o-prim); color: #fff; font-size: 20px; font-weight: 500; border-radius: 4px; }
/* largeur fixe : l'anneau de la fin mesure le bloc avant que le solde ne passe de 25 000 à 119 500 FCFA */
#app-cb .cb-pc-i { position: absolute; left: 50%; top: 92px; display: grid; grid-template-columns: 210px 170px; row-gap: 8px; font-size: 20px; color: var(--o-texte); }
#app-cb .cb-pc-av { position: absolute; right: 18px; bottom: 16px; width: 32px; height: 32px; border-radius: 5px; color: #fff;
  font-size: 17px; font-weight: 700; display: flex; align-items: center; justify-content: center; }

/* -- la caisse plein écran -- */
#app-cb .cb-pos { position: absolute; inset: 0; z-index: 25; background: #E9ECEF; color: var(--o-texte); }
#app-cb .cb-pos.cb-resto { z-index: 26; }
#app-cb .pos-haut { position: absolute; left: 0; top: 0; right: 0; height: 64px; background: #fff; display: flex; align-items: center; gap: 12px; padding: 0 10px; font-size: 19px; border-bottom: 1px solid var(--o-filet); }
#app-cb .pos-plus { width: 50px; height: 44px; border-radius: 4px; background: #DEE2E6; display: flex; align-items: center; justify-content: center; color: #343A40; }
#app-cb .pos-plus svg { width: 20px; height: 20px; }
#app-cb .pos-num { height: 44px; min-width: 74px; justify-content: center; padding: 0 18px; border-radius: 4px; background: #E6E3EF; border: 1px solid var(--o-prim); display: flex; align-items: center; font-weight: 500; }
#app-cb .pos-cherche { margin-left: auto; width: 420px; height: 44px; border: 1px solid var(--o-filet); border-radius: 4px; display: flex; align-items: center; gap: 10px; padding: 0 12px; color: var(--o-texte-3); }
#app-cb .pos-cherche .ico { width: 20px; height: 20px; display: inline-flex; }
#app-cb .cb-logo-odoo { position: absolute; left: 50%; top: 10px; height: 44px; transform: translateX(-50%); }
#app-cb .pos-caissier { display: flex; align-items: center; gap: 10px; margin-left: 12px; max-width: 230px; padding: 0 16px; overflow: hidden; }
#app-cb .pos-caissier .avatar { flex: none; width: 34px; height: 34px; font-size: 16px; }
#app-cb .cb-cais-n { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
#app-cb .pos-menu { font-size: 28px; padding: 0 12px; color: #343A40; border-radius: 4px; }
#app-cb .pos-menu.actif { background: #E9ECEF; }
#app-cb .pos-corps { position: absolute; left: 0; top: 64px; right: 0; bottom: 0; }
#app-cb .pos-corps .vue { background: #E9ECEF; }
#app-cb .pos-vente { position: absolute; inset: 0; display: grid; grid-template-columns: 540px 1fr; gap: 10px; padding: 8px; }
#app-cb .pos-g { display: flex; flex-direction: column; gap: 8px; min-height: 0; }
#app-cb .cb-pile { position: relative; display: block; }
#app-cb .cb-g { position: absolute; inset: 0; display: flex; flex-direction: column; gap: 8px; }
#app-cb .cb-vide { flex: 1; border-radius: 6px; background: #F8F9FA; display: flex; flex-direction: column; align-items: center;
  justify-content: center; gap: 14px; font-size: 21px; font-weight: 500; color: #343A40; }
#app-cb .cb-chariot { width: 64px; height: 64px; display: inline-flex; color: #495057; }
#app-cb .cb-chariot svg { width: 64px; height: 64px; }
#app-cb .pos-ticket { flex: 1; background: #fff; border-radius: 6px; padding: 10px; overflow: hidden; }
#app-cb .pv-ligne { padding: 10px 12px; border-radius: 6px; font-size: 17px; }
#app-cb .pv-ligne.sel { background: #ECEAF3; box-shadow: inset 0 0 0 1px var(--o-prim); }
#app-cb .pv-ligne .a { display: flex; justify-content: space-between; }
#app-cb .pv-ligne .q { margin-top: 3px; color: var(--o-texte-2); font-size: 15px; }
#app-cb .pv-ligne .q b { padding: 0 4px; border: 1px solid var(--o-filet); border-radius: 3px; color: var(--o-texte); }
#app-cb .pos-tot { background: #fff; border-radius: 6px; padding: 8px 16px; }
#app-cb .pos-tot b { display: flex; justify-content: space-between; font-size: 26px; font-weight: 700; }
#app-cb .pos-acts { display: flex; gap: 8px; }
#app-cb .pos-acts > span, #app-cb .pos-cf > span { height: 50px; padding: 0 16px; background: #fff; border-radius: 4px; display: flex; align-items: center; gap: 8px; font-size: 19px; white-space: nowrap; }
#app-cb .pos-acts > span:nth-child(2) { color: #5C636A; background: #F1F3F5; }
#app-cb .pos-acts .dr { margin-left: auto; }
#app-cb .cb-nomcli { font-weight: 500; color: var(--o-prim); }
#app-cb .pos-pave { display: grid; grid-template-columns: repeat(4, 1fr); gap: 6px; }
#app-cb .pk { height: 50px; background: #fff; border-radius: 4px; display: flex; align-items: center; justify-content: center; font-size: 20px; }
#app-cb .pk.sel { background: #E6E3EF; box-shadow: inset 0 0 0 1px var(--o-prim); }
#app-cb .pk.jaune { background: #FBE7A0; } #app-cb .pk.rose { background: #F8E1D9; } #app-cb .pk.rouge { background: #F6A6A6; } #app-cb .pk.vert { background: #CDEFD0; }
#app-cb .pos-payer { height: 66px; border-radius: 4px; background: var(--o-prim); color: #fff; font-size: 22px; display: flex; align-items: center; justify-content: center; }
#app-cb .pos-d { min-height: 0; overflow: hidden; }
#app-cb .pos-cats { display: flex; gap: 8px; flex-wrap: wrap; }
#app-cb .pos-cat { height: 60px; min-width: 150px; padding: 0 22px; border-radius: 4px; display: flex; align-items: center; justify-content: center; font-size: 18px; color: #212529; }
#app-cb .pos-tuiles { margin-top: 12px; display: grid; grid-template-columns: repeat(6, 1fr); gap: 8px; }
#app-cb .pos-tuile { position: relative; height: 108px; border-radius: 4px; padding: 10px; display: flex; align-items: center; justify-content: center; text-align: center; font-size: 19px; line-height: 1.2; color: #212529; }
#app-cb .cb-info { position: absolute; top: 0; right: 0; width: 0; height: 0; border-style: solid; border-width: 0 38px 38px 0;
  border-color: transparent rgba(154,158,161,.5) transparent transparent; border-top-right-radius: 4px; }
#app-cb .cb-info svg { position: absolute; left: 24px; top: 4px; width: 7px; height: 14px; }
#app-cb .cb-qte { position: absolute; right: 10px; bottom: 2px; font-size: 34px; font-weight: 800; color: #6C757D; line-height: 1; }
/* l'écran de paiement */
#app-cb .pos-modes { display: flex; flex-direction: column; gap: 8px; }
#app-cb .pos-mode { height: 62px; background: #fff; border-radius: 4px; display: flex; align-items: center; gap: 18px; padding: 0 22px; font-size: 20px; }
#app-cb .pos-mode .ico { width: 28px; height: 28px; display: inline-flex; color: #495057; }
#app-cb .pos-mode .ico svg { width: 28px; height: 28px; }
#app-cb .pos-cf { margin-top: auto; display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
#app-cb .pos-cf > span { justify-content: center; }
#app-cb .pos-cf em { font-style: normal; }
#app-cb .cb-ico { width: 18px; height: 18px; display: inline-flex; color: #343A40; }
#app-cb .cb-ico svg { width: 18px; height: 18px; }
#app-cb .pos-cf i { width: 16px; height: 16px; border: 1px solid #495057; border-radius: 3px; margin-left: 8px; }
#app-cb .pos-ardoise { height: 56px; border-radius: 4px; background: #714B67; color: #fff; font-size: 19px; display: flex; align-items: center; justify-content: center; gap: 10px; }
#app-cb .pos-ardoise .ico { width: 20px; height: 20px; display: inline-flex; }
#app-cb .pos-ardoise .ico svg { width: 20px; height: 20px; }
#app-cb .pos-rv { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
#app-cb .pos-rv span { height: 66px; background: #fff; border-radius: 4px; display: flex; align-items: center; justify-content: center; font-size: 20px; }
#app-cb .pos-rv .v { background: var(--o-prim); color: #fff; }
#app-cb .pos-rv .v.cb-off { background: #B9B1D1; }
#app-cb .pos-pd { background: #fff; border-radius: 6px; position: relative; }
#app-cb .pos-du { height: 126px; display: flex; align-items: center; justify-content: center; font-size: 60px; font-weight: 500; color: #1E7B34; border-bottom: 8px solid #E9ECEF; }
#app-cb .cb-choix { position: absolute; left: 0; right: 0; top: 420px; text-align: center; font-size: 24px; color: var(--o-texte); }
#app-cb .cb-zone { position: absolute; left: 150px; right: 150px; top: 380px; }
#app-cb .cb-zone .cb-pile { height: 66px; }
#app-cb .cb-st { position: absolute; inset: 0; border: 1px solid; border-radius: 6px; display: flex; justify-content: space-between; align-items: center; padding: 0 22px; font-size: 24px; }
#app-cb .cb-st b { font-weight: 800; }
#app-cb .cb-st.cb-zero b { font-weight: 400; }
#app-cb .cb-st.cb-vert { background: #D1E7DD; border-color: #1A6E2E; color: #1A6E2E; }
#app-cb .cb-st.cb-rouge { background: #F8D7DA; border-color: #B02A37; color: #8E1F2A; }
#app-cb .pos-pl { margin-top: 10px; height: 66px; background: #E9ECEF; border-radius: 4px; display: grid; grid-template-columns: 1fr auto 40px; align-items: center; gap: 20px; padding: 0 18px; font-size: 22px; color: var(--o-texte-2); }
#app-cb .pos-pl .x { color: #B02A37; text-align: center; }
#app-cb .toast { top: 76px; width: 600px; }
/* le reçu (mise en page de t10_ardoises.py) */
#app-cb .cb-recu { position: absolute; inset: 0; display: grid; grid-template-columns: 1fr 860px; background: #E9ECEF; }
#app-cb .cb-actions { position: relative; background: #F8F9FA; border-right: 1px solid var(--o-filet); padding: 22px 120px; }
#app-cb .cb-reussi { display: flex; flex-direction: column; align-items: center; gap: 6px; padding: 20px; border: 1px solid #1A6E2E;
  border-radius: 12px; background: #D1E7DD; color: #13532A; }
#app-cb .cb-okico { width: 64px; height: 64px; color: #1A6E2E; }
#app-cb .cb-okico svg { width: 64px; height: 64px; }
#app-cb .cb-reussi b { font-size: 32px; font-weight: 800; }
#app-cb .cb-mt { display: flex; align-items: center; gap: 12px; font-size: 26px; font-weight: 700; }
#app-cb .cb-modif { font-size: 16px; font-weight: 600; background: #1A6E2E; color: #fff; border-radius: 5px; padding: 3px 9px; }
#app-cb .cb-actions hr { border: 0; border-top: 1px solid var(--o-filet); margin: 22px 0; }
#app-cb .cb-imprimer { height: 66px; border-radius: 6px; background: #E2E5E9; color: var(--o-texte); font-size: 21px; display: flex;
  align-items: center; justify-content: center; gap: 10px; }
#app-cb .cb-imprimer .ico { width: 22px; height: 22px; display: inline-flex; }
#app-cb .cb-imprimer .ico svg { width: 22px; height: 22px; }
#app-cb .cb-mail { margin-top: 12px; display: flex; height: 66px; }
#app-cb .cb-in { flex: 1; border: 1px solid var(--o-filet); border-right: 0; border-radius: 6px 0 0 6px; background: #fff; display: flex;
  align-items: center; padding: 0 18px; font-size: 20px; color: #6C757D; }
#app-cb .cb-envoi { width: 130px; border-radius: 0 6px 6px 0; background: var(--o-prim); color: #fff; display: flex; align-items: center; justify-content: center; }
#app-cb .cb-envoi svg { width: 24px; height: 24px; }
#app-cb .cb-envoi.cb-envoi-off { background: #A79FC2; }
#app-cb .cb-in.cb-in-v { color: var(--o-texte); }
#app-cb .cb-logo { display: block; width: 50%; margin: 0 auto 14px; }
#app-cb .cb-nouv { position: absolute; left: 10px; right: 10px; bottom: 10px; height: 96px; border-radius: 6px; background: var(--o-prim);
  color: #fff; font-size: 26px; display: flex; align-items: center; justify-content: center; }
#app-cb .cb-recu-d { position: relative; overflow: hidden; display: flex; justify-content: center; padding-top: 24px; }
#app-cb .cb-ticket { width: 470px; height: 740px; overflow: hidden; background: #fff; border: 1px solid var(--o-filet); border-radius: 6px;
  padding: 18px 22px; font-size: 17px; color: #212529; }
#app-cb .cb-ent { text-align: center; line-height: 1.45; }
#app-cb .cb-ent > div:first-child { font-weight: 700; }
#app-cb .cb-suivi { font-size: 36px; font-weight: 500; margin-top: 4px; }
#app-cb .cb-tirets { text-align: center; color: #495057; letter-spacing: 1px; overflow: hidden; white-space: nowrap; margin: 4px 0; }
#app-cb .cb-rl { padding: 6px 0; font-size: 16px; }
#app-cb .cb-rl .a b { font-weight: 700; }
#app-cb .cb-rm { display: flex; justify-content: space-between; line-height: 1.6; }
#app-cb .cb-rm.cb-grand { font-size: 21px; }
#app-cb .cb-rm.cb-gras { font-weight: 700; margin-bottom: 4px; }
/* un peu d'air au-dessus du premier paiement et de MONNAIE : leur anneau ne barre pas la ligne du dessus */
#app-cb .cb-rm.cb-gras + .cb-rm, #app-cb .cb-rm.cb-monnaie { margin-top: 12px; }
#app-cb .cb-gen { margin-top: 18px; text-align: center; color: #495057; }
/* fenêtres de la caisse : ouverture, clôture, écart de règlement */
#app-cb .cb-dlg { border-radius: 8px; }
#app-cb .cb-dlg-h { height: 68px; display: flex; align-items: center; justify-content: space-between; padding: 0 26px;
  border-bottom: 1px solid var(--o-filet); font-size: 23px; font-weight: 500; }
#app-cb .cb-dlg-c { padding: 18px 26px 22px; font-size: 19px; }
#app-cb .cb-dlg-p { display: flex; gap: 10px; padding: 16px 26px 18px; border-top: 1px solid var(--o-filet); }
#app-cb .cb-dlg-p .bt { height: 50px; font-size: 21px; }
#app-cb .cb-dlg-p .cb-dr { margin-left: auto; }
#app-cb .cb-dl { margin-left: 8px; }
#app-cb .cb-lab { margin: 6px 0 8px; font-size: 18px; color: var(--o-texte); }
#app-cb .cb-in-l { display: flex; gap: 8px; margin-bottom: 18px; }
#app-cb .cb-champ { position: relative; flex: 0 0 auto; width: 420px; height: 54px; border: 1px solid #CED4DA; border-radius: 6px; background: #fff;
  display: flex; align-items: center; justify-content: space-between; padding: 0 18px; font-size: 21px; color: var(--o-texte); }
#app-cb .cb-saisie { flex: 1; width: auto; }
#app-cb .cb-saisie .ph, #app-cb .cb-saisie .val { position: absolute; left: 18px; top: 50%; transform: translateY(-50%); }
#app-cb .cb-saisie.focus { border-color: var(--o-prim); box-shadow: 0 0 0 4px rgba(113,99,158,.22); }
#app-cb .cb-x { margin-left: auto; font-size: 18px; color: #343A40; }
#app-cb .cb-plein { flex: 1; width: auto; }
#app-cb .cb-fermer { width: 22px; height: 22px; display: inline-flex; color: #343A40; }
#app-cb .cb-fermer svg { width: 22px; height: 22px; }
#app-cb .cb-btn-ic { width: 54px; height: 54px; border-radius: 6px; background: #E9ECEF; display: flex; align-items: center; justify-content: center; color: #343A40; }
#app-cb .cb-btn-ic svg { width: 24px; height: 24px; }
#app-cb .cb-zone-txt { height: 84px; border: 1px solid #CED4DA; border-radius: 6px; padding: 12px 14px; font-size: 18px; color: #6C757D; }
/* la clôture : le corps défile entre le détail par mode et le comptage */
#app-cb .cb-clo { top: 28px; width: 1000px; margin-left: -500px; }
#app-cb .cb-clo-n { font-size: 19px; font-weight: 800; }
#app-cb .cb-clo-c { position: relative; height: 560px; overflow: hidden; padding: 0 26px; }
#app-cb #cb-clo-defil { padding: 16px 0 20px; }
#app-cb .cb-cl-b { margin-bottom: 14px; }
#app-cb .cb-cl-t { display: flex; justify-content: space-between; font-size: 23px; line-height: 1.5; }
#app-cb .cb-cl-s { display: flex; justify-content: space-between; margin-left: 2px; padding-left: 10px; border-left: 1px solid var(--o-filet);
  font-size: 18px; line-height: 1.6; color: #6C757D; }
#app-cb .cb-cl-acc { opacity: .5; }
#app-cb .cb-cl-s.cb-rougef { color: #B02A37; font-weight: 700; }
/* un peu d'air au-dessus de la Différence des espèces : son anneau ne barre pas le montant compté */
#app-cb #cb-clo-diffl { margin-top: 10px; }
#app-cb .cb-clo-c hr { border: 0; border-top: 1px solid var(--o-filet); margin: 8px 0 14px; }
#app-cb .cb-ecart-txt { margin: 4px 0; font-size: 20px; line-height: 1.5; }
#app-cb #cb-ecart-voile { z-index: 32; }
#app-cb #cb-ecart { z-index: 33; }
/* le menu ☰ */
#app-cb .cb-menu { position: absolute; right: 8px; top: 62px; width: 280px; z-index: 29; background: #fff; border: 1px solid var(--o-filet);
  border-radius: 6px; box-shadow: 0 14px 34px rgba(0,0,0,.2); }
#app-cb .cb-menu-ecran { padding: 10px; border-bottom: 1px solid var(--o-filet); }
#app-cb .cb-menu-ecran span { height: 46px; border-radius: 4px; background: #DEE2E6; display: flex; align-items: center; justify-content: center; color: #343A40; }
#app-cb .cb-menu-ecran svg { width: 24px; height: 24px; }
#app-cb .cb-menu-l { padding: 8px 0; }
#app-cb .cb-menu-l div { height: 46px; display: flex; align-items: center; padding: 0 20px; font-size: 19px; color: var(--o-texte); }
#app-cb .cb-pastille { margin-left: auto; min-width: 26px; height: 26px; border-radius: 13px; background: #017E84; color: #fff; font-size: 15px;
  display: flex; align-items: center; justify-content: center; }
"""

def touche(sel, d, effets, deplacer=True, **kw):
    """Un clic et ses effets, posés à l'instant même du clic (et non après la respiration du geste) ; ``kw`` : options
    du clic (avec, decale)."""
    gestes = [clic(sel, d=d, deplacer=deplacer, puis=0, **kw)]
    for i, g in enumerate(effets):
        g = dict(g, avec=True)
        if i == 0:
            g['decale'] = (d + 0.08 if deplacer else 0) + 0.02
        gestes.append(g)
    return gestes


# Les pauses de chaque étape, réglées pour que chaque geste tombe sur les mots qui le disent (instants mesurés sur les
# silences des voix Kokoro, mots placés au prorata des caractères entre deux silences).
P = {1: (1.85, 0.15, 1.4), 2: (0.5, 0.9, 0.3), 3: (0.6, 0.0, 0.2, 0.0, 0.0, 0.0), 4: (0.05, 0.3, 0.1, 0.0, 0.3, 0.45),
     5: (0.5, 0.2, 0.0, 0.3, 3.2, 0.28, 0.12, 0.0), 6: (0.3, 0.3, 0.1, 0.0, 0.0, 0.0, 3.6)}

CHAPITRE = {
    'court': 'Bar & resto',             # « Bar & restaurant » ne tient pas dans le sommaire de huit cases
    'poste': 'Bar et restaurant',
    'titre': 'Le bar et le restaurant',
    'personne': (NOM, ROLE),
    'objectif': "Ouvrir sa caisse, servir, encaisser en espèces ou en mobile money, porter une note sur la chambre, "
                "puis compter et fermer la caisse.",
    'voix': "Troisième chapitre : le bar et le restaurant. Hervé ouvre sa caisse, sert, encaisse, porte une note sur "
            "la chambre, et compte sa caisse le soir.",
    'app': 'app-cb',
    'ecran': ECRAN,
    'css': CSS,
    'vues_initiales': {'odoo': 'cb-dash', 'pos': 'cb-v1', 'resto': 'cb-rv'},
    'etapes': [
        {'titre': 'Une caisse par point de vente', 'texte': "Le bar, le restaurant, la boutique : chacun sa caisse et son "
                                                           "fond de caisse.",
         'voix': "Chaque point de vente a sa caisse : le bar de la terrasse, le restaurant, la boutique. Larissa a déjà "
                 "ouvert le restaurant. Hervé ouvre le bar : la caisse lui propose ce qui a été compté à la dernière "
                 "clôture, vingt-cinq mille francs, et il confirme.",
         # chaque carte désignée quand la voix la nomme ; celle du restaurant (avatar L) pendant la phrase sur Larissa
         'gestes': [pause(P[1][0]), anneau('#cb-k-bar', d=0.9), pause(0.2), anneau('#cb-k-res', d=0.75),
                    anneau('#cb-k-bou', d=0.75), pause(0.1), anneau('#cb-k-res', d=1.6), pause(P[1][1]),
                    clic('#cb-k-bar-bt', d=0.6),
                    # la caisse se pose sur le tableau de bord, qui s'efface dessous : pas d'écran intermédiaire
                    montrer('#cb-pb', d=0.3, y=0), cacher('#cb-dash', d=0.05),
                    ouvrir('cb-ouv'), pause(P[1][2]), anneau('#cb-ouv-mt', d=1.7), clic('#cb-ouv-ok', d=0.5),
                    fermer('cb-ouv')]},
        {'titre': 'La commande au bar', 'texte': 'Une tuile par article, à la couleur de sa catégorie : le ticket et '
                                                 'le total se font seuls.',
         'voix': "En tête, les catégories du bar : bières, jus, grillades, plats ; chaque tuile prend la couleur de la "
                 "sienne. Une touche par article : deux bières, des brochettes, un plantain frit. Le ticket se construit "
                 "à gauche, et le total suit.",
         'gestes': [pause(P[2][0]), anneau('#cb-v1-cats', d=2.8), anneau('#cb-v1 .pos-tuiles', d=2.0), pause(P[2][1])]
                   # chaque touche change d'un coup la ligne, le total et la quantité de la tuile
                   + touche('#cb-v1-t%d' % I_BIERE, 0.5, [
                       cacher('#cb-v1-vide', d=0.15), texte('#cb-v1-total', fcfa(PRIX['Bière blonde 65 cl'])),
                       montrer('#cb-v1-plein', d=0.2, y=0), montrer('#cb-v1-l0', d=0.25, y=8),
                       classe('#cb-v1-l0', ajouter=['sel']), montrer('#cb-v1-t%d-q' % I_BIERE, d=0.2, y=0),
                       texte('#cb-v1-t%d-q' % I_BIERE, '1')])
                   + touche('#cb-v1-t%d' % I_BIERE, 0, [
                       texte('#cb-v1-l0-q', '2,00'), texte('#cb-v1-l0-m', fcfa(MIDI[0][3])),
                       texte('#cb-v1-total', fcfa(MIDI[0][3])), texte('#cb-v1-t%d-q' % I_BIERE, '2')], deplacer=False)
                   + touche('#cb-v1-t%d' % I_BROCH, 0.35, [
                       classe('#cb-v1-l0', retirer=['sel']), montrer('#cb-v1-l1', d=0.25, y=8),
                       classe('#cb-v1-l1', ajouter=['sel']), texte('#cb-v1-total', fcfa(MIDI[0][3] + MIDI[1][3])),
                       montrer('#cb-v1-t%d-q' % I_BROCH, d=0.2, y=0), texte('#cb-v1-t%d-q' % I_BROCH, '1')])
                   + touche('#cb-v1-t%d' % I_PLANT, 0.35, [
                       classe('#cb-v1-l1', retirer=['sel']), montrer('#cb-v1-l2', d=0.25, y=8),
                       classe('#cb-v1-l2', ajouter=['sel']), texte('#cb-v1-total', fcfa(T_MIDI)),
                       montrer('#cb-v1-t%d-q' % I_PLANT, d=0.2, y=0), texte('#cb-v1-t%d-q' % I_PLANT, '1')])
                   + [pause(P[2][2]), anneau('#cb-v1-ticket', d=1.5), anneau('#cb-v1-total', d=1.0)]},
        {'titre': 'Encaisser', 'texte': 'Espèces, Orange Money, MTN MoMo : la monnaie à rendre est calculée.',
         'voix': "Au paiement, la caisse propose ses modes : espèces, Orange Moni, MTN Momo, et deux modes réglés plus "
                 "tard. Le client tend dix mille francs : la caisse affiche la monnaie à rendre, deux mille cinq cents. "
                 "Hervé valide, et le reçu reprend le total, le billet reçu et la monnaie rendue.",
         # la recherche n'existe que sur l'écran de vente, l'onglet que pour une commande non finalisée (couche_pos)
         'gestes': touche('#cb-v1-payer', 0.3, [vue('cb-p1', 'pos'), cacher('#cb-pb-cherche', d=0.2)])
                   + [pause(P[3][0]), anneau('#cb-p1-modes', d=3.8), pause(P[3][1])]
                   + touche('#cb-p1-esp', 0.4, [cacher('#cb-p1-msg', d=0.15), montrer('#cb-p1-ok', d=0.2, y=0),
                                                montrer('#cb-p1-pl', d=0.2, y=0),
                                                classe('#cb-p1-valider', retirer=['cb-off'])])
                   + touche('#cb-p1-k1', 0.35, [texte('#cb-p1-pl-v', fcfa(1)), cacher('#cb-p1-ok', d=0.1),
                                                montrer('#cb-p1-du', d=0.1, y=0), texte('#cb-p1-du-v', fcfa(T_MIDI - 1)),
                                                classe('#cb-p1-valider', ajouter=['cb-off'])])
                   + touche('#cb-p1-k0', 0.15, [texte('#cb-p1-pl-v', fcfa(10)), texte('#cb-p1-du-v', fcfa(T_MIDI - 10))])
                   + touche('#cb-p1-k0', 0, [texte('#cb-p1-pl-v', fcfa(100)), texte('#cb-p1-du-v', fcfa(T_MIDI - 100))],
                            deplacer=False)
                   + touche('#cb-p1-k0', 0, [texte('#cb-p1-pl-v', fcfa(1000)), texte('#cb-p1-du-v', fcfa(T_MIDI - 1000))],
                            deplacer=False)
                   + touche('#cb-p1-k0', 0, [texte('#cb-p1-pl-v', fcfa(RECU)), cacher('#cb-p1-du', d=0.1),
                                             texte('#cb-p1-mon-v', fcfa(-RENDU)), montrer('#cb-p1-mon', d=0.15, y=0),
                                             classe('#cb-p1-valider', retirer=['cb-off'])], deplacer=False)
                   + [pause(P[3][2]), anneau('#cb-p1-mon', d=1.7), pause(P[3][3])]
                   + touche('#cb-p1-valider', 0.45, [vue('cb-r1', 'pos'), cacher('#cb-pb-num', d=0.2)])
                   + [pause(P[3][4]), anneau('#cb-r1-tk', d=1.1), pause(P[3][5]), anneau('#cb-r1-p0', d=0.75),
                      anneau('#cb-r1-monnaie', d=1.0)]},
        {'titre': 'Au restaurant', 'texte': 'Sa caisse, sa carte, sa caissière : un dîner réglé en MTN MoMo.',
         'voix': "Au restaurant, Larissa travaille sur sa propre caisse, avec sa carte, vins compris. Ce dîner de "
                 "vingt-sept mille francs se règle en MTN Momo : le reste à payer tombe à zéro, et Larissa valide.",
         # la caisse du restaurant se pose sur celle du bar (fondu croisé, pas d'éclair du back-office) ; la caisse du
         # bar, cachée dessous, est déjà remise sur la commande de Brigitte pour l'étape suivante
         'gestes': [montrer('#cb-pr', d=0.3, y=0), cacher('#cb-pb', d=0.05),
                    texte('#cb-pb-num', TICKETS_JOUR[7][1]), vue('cb-v2', 'pos', avec=True),
                    animer('#cb-pb-num', {'autoAlpha': 0}, {'autoAlpha': 1}, d=0.05, avec=True),
                    animer('#cb-pb-cherche', {'autoAlpha': 0}, {'autoAlpha': 1}, d=0.05, avec=True),
                    pause(P[4][0]), anneau('#cb-pr-cais', d=1.6), pause(P[4][1]), anneau('#cb-rv-cats', d=1.5),
                    pause(P[4][2]), anneau('#cb-rv-ticket', d=1.1)]
                   + touche('#cb-rv-payer', 0.3, [vue('cb-rp', 'resto'), cacher('#cb-pr-cherche', d=0.2)])
                   + [pause(P[4][3])]
                   + touche('#cb-rp-momo', 0.35, [cacher('#cb-rp-msg', d=0.15), montrer('#cb-rp-ok', d=0.2, y=0),
                                                  montrer('#cb-rp-pl', d=0.2, y=0),
                                                  classe('#cb-rp-valider', retirer=['cb-off'])])
                   + [pause(P[4][4]), anneau('#cb-rp-ok', d=1.4), pause(P[4][5])]
                   # « Valider » mène au reçu : la scène quitte le restaurant aussitôt le clic donné
                   + touche('#cb-rp-valider', 0.45, [animer('#cb-pb', {'autoAlpha': 0}, {'autoAlpha': 1}, d=0.05)])
                   + [cacher('#cb-pr', d=0.3)]},
        {'titre': "Sur la chambre ou sur l'ardoise",
         'texte': '« Note de chambre » part sur le folio du séjour ; « Mettre sur ardoise » ouvre une ardoise.',
         'voix': "Au bar, Brigitte Essomba, cliente de l'hôtel, a dîné ; sa fiche est déjà sur le ticket. Au paiement, "
                 "pour un habitué, Mettre sur ardoise ouvre une ardoise à son nom ; le chapitre suivant montre comment "
                 "on les suit. Pour Brigitte, Hervé touche Note de chambre : l'avertissement n'empêche pas de valider. "
                 "Il valide, et le dîner part tout seul sur le folio de son séjour.",
         # « Mettre sur ardoise » est désigné avant le choix du mode, sans être touché ; le report au folio suit la
         # validation (aite_hotel_pos_link/models/pos_order.py:142-156, _PAID_STATES), d'où le clic sur « Valider »
         # et le reçu (ref_muk/710) ; l'avertissement d'Odoo reste ses sept secondes (autocloseDelay)
         'gestes': [pause(P[5][0]), anneau('#cb-v2-ticket', d=2.2), pause(P[5][1]), anneau('#cb-v2-cli', d=1.2),
                    pause(P[5][2])]
                   + touche('#cb-v2-payer', 0.4, [vue('cb-p2', 'pos'), cacher('#cb-pb-cherche', d=0.2)])
                   + [pause(P[5][3]), anneau('#cb-p2-ardoise', d=2.4), pause(P[5][4])]
                   + touche('#cb-p2-note', 0.5, [cacher('#cb-p2-msg', d=0.15), montrer('#cb-p2-ok', d=0.2, y=0),
                                                 montrer('#cb-p2-pl', d=0.2, y=0),
                                                 classe('#cb-p2-valider', retirer=['cb-off']),
                                                 notifier('cb-avert', duree=7.0)])
                   + [pause(P[5][5]), anneau('#cb-avert', d=1.4), pause(P[5][6])]
                   + touche('#cb-p2-valider', 0.5, [vue('cb-r2', 'pos'), cacher('#cb-pb-num', d=0.2)])
                   + [pause(P[5][7]), anneau('#cb-r2-p0', d=2.0)]},
        {'titre': 'La clôture de la caisse', 'texte': 'Ce qui est attendu par mode, le comptage, et l\'écart, signalé '
                                                      'puis enregistré.',
         'voix': "Le soir, Hervé ferme sa caisse : neuf commandes, et pour chaque mode, le montant attendu. Il compte "
                 "ses espèces et tape ce qu'il trouve : il manque cinq cents francs. La caisse le signale avant de "
                 "clôturer ; Hervé confirme, et l'écart est enregistré : la direction le retrouvera dans Écarts de "
                 "caisse. Sur la carte du bar, la clôture du jour et le solde compté.",
         # Après « Poursuivre », Odoo recharge la caisse et passe par son écran d'accueil (« Backend ») : raccourci
         # signalé dans l'en-tête (Mise en scène) ; la vidéo revient droit au tableau de bord.
         'gestes': [texte('#cb-pb-num', '510'), vue('cb-v3', 'pos', avec=True),
                    animer('#cb-pb-num', {'autoAlpha': 0}, {'autoAlpha': 1}, d=0.05, avec=True),
                    animer('#cb-pb-cherche', {'autoAlpha': 0}, {'autoAlpha': 1}, d=0.05, avec=True)]
                   # le bouton ☰ s'enfonce au clic, pas avant
                   + touche('#cb-pb-menu', 0.5, [classe('#cb-pb-menu', ajouter=['actif']), montrer('#cb-menu', d=0.2, y=-6)],
                            avec=True, decale=P[6][0])
                   + touche('#cb-menu-fermer', 0.35, [cacher('#cb-menu', d=0.15), classe('#cb-pb-menu', retirer=['actif']),
                                                      ouvrir('cb-clo'), anneau('#cb-clo-n', d=0.8, decale=P[6][1])])
                   + [anneau('#cb-clo-esp', d=1.4),
                      defiler('#cb-clo-defil', -400, d=0.4), clic('#cb-clo-in', d=0.3, puis=0),
                      saisir('cb-clo-in', str(COMPTE), d=0.4),
                      texte('#cb-clo-compte', fcfa(COMPTE)), texte('#cb-clo-diff', fcfa(ECART), avec=True),
                      defiler('#cb-clo-defil', 0, d=0.4), anneau('#cb-clo-diffl', d=1.0), pause(P[6][2])]
                   + touche('#cb-clo-ok', 0.4, [ouvrir('cb-ecart')])
                   + [pause(P[6][3]), anneau('#cb-ecart-txt', d=0.8), pause(P[6][4])]
                   + touche('#cb-ecart-ok', 0.35, [fermer('cb-ecart'), fermer('cb-clo')])
                   + [pause(P[6][5]),
                      # le tableau de bord se pose sous la caisse, qui s'efface : la carte du bar a sa clôture du jour
                      animer('#cb-dash', {'autoAlpha': 0}, {'autoAlpha': 1}, d=0.05), texte('#cb-k-bar-date', JOUR, avec=True),
                      texte('#cb-k-bar-solde', fcfa(COMPTE), avec=True), cacher('#cb-pb', d=0.35),
                      pause(P[6][6]), anneau('#cb-k-bar-i', d=2.6)]},
    ],
}
