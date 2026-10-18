# -*- coding: utf-8 -*-
"""Tutoriel 10 — Fini le cahier d'ardoise : le crédit client sous contrôle.

Le caissier du bar (Hervé Tchakounté, demo.POSTES['caisse']) met le reste
d'une note sur l'ardoise du client depuis l'écran de paiement de la caisse,
retrouve l'ardoise dans POS Crédit, encaisse un remboursement Orange Money
qui solde une autre ardoise, puis lit le tableau de bord Recouvrement : où
dort la dette, et qui relancer en premier.

Profil rejoué : Caisse (point_of_sale.group_pos_user + aite_pos_credit.
group_pos_credit_user, « Consulte les ardoises, enregistre des
remboursements. », aite_pos_credit/security/pos_credit_security.xml:11-15 ;
les menus Recouvrement, Ardoises et Remboursements sont ouverts à ce groupe,
views/pos_credit_menus.xml:15-41). Applications de la barre MuK :
ecrans.APPS_PROFIL['caisse'] (compte demo.caisse) ; menus de POS Crédit et
mise en page : captures ref_muk/057-pos-cr-dit*.png, 058-pos-cr-dit-
ardoises*.png, 059-pos-cr-dit-remboursements.png ; caisse : ref_muk/612,
613, 614 (modèle visuel, jamais incrustées).

Sources des libellés (relevés mot pour mot) :

1. La caisse (Odoo 18, odoo18/addons/point_of_sale/static/src/app) — écran
   de vente : ecrans.pos_produits (ref_muk/612) ; écran de paiement :
   screens/payment_screen/payment_screen.xml:27-140 (modes, « Client » qui
   prend le nom du client :100-107, « Facture », « Retour », « Valider »
   grisé tant que la commande n'est pas payée) ; payment_status/
   payment_status.xml:4-22 (« Veuillez sélectionner un mode de paiement »,
   « Restant » en rouge tant qu'il reste dû, en vert à zéro) ; i18n/fr.po :
   « Restant » :6607-6609, « Valider » :9008-9009, « Retour » :1117-1118,
   « Facture » :3696-3697, « Client » :2395-2396. Le pavé : ecrans.pos_paiement
   (ref_muk/613). Le bouton « Mettre sur ardoise », pleine largeur, violet
   #714B67, icône fa-book : aite_pos_credit/static/src/js/pos/
   payment_screen_button.xml:10-20 et static/src/scss/pos_credit_pos.scss:
   3-16. Son geste : payment_screen_button.js:56-110 — sans client, la
   notification « Sélectionnez d'abord un client pour une vente à crédit. »
   (type warning, :64-73) puis la liste des clients s'ouvre et rien n'est
   validé ; avec un client, une ligne de la méthode ardoise égale au reste
   dû est ajoutée (add_paymentline, sans l'avertissement « soldes dûs » que
   seul addNewPaymentLine affiche, odoo18 payment_screen.js:112-125) puis la
   commande est validée (:96-109) : il faut donc toucher deux fois le bouton
   (la première fois, putOnCredit s'arrête après selectPartner, :64-73). Les
   méthodes « Ardoise client » (is_aite_credit) et « Note de chambre »
   (is_room_charge) sont celles que aite_demo_data crée et rattache à la
   caisse (models/demo_generator.py:288-320) ; la caisse du bar montre donc
   Espèces, Orange Money, MTN MoMo, Note de chambre, Ardoise client — les
   quatre premiers comme t04_note_chambre.py:310-311. L'ardoise est trouvée
   par payment_screen_button.js:24-40.
   La fenêtre des clients : screens/partner_list/partner_list.xml:5-56 et
   partner_line/partner_line.xml:46-86 ; fr.po « Créer » :2261-2262,
   « Recherche des clients... » :6921-6922, « Nom » :4363, « Adresse » :721,
   « Contact » :2170, « Rechercher plus » :6939, « Ignorer » :2768-2769.
   Le reçu : screens/receipt_screen/receipt_screen.xml:4-60 (« Paiement
   réussi » fr.po:5308-5309, « Modifier le paiement » :2922-2923, « Imprimer
   le reçu complet » :6052-6053, « Nouvelle commande » :4426-4427, champ
   courriel au texte indicatif non traduit « e.g. john.doe@mail.com » :27) ;
   le ticket : receipt/order_receipt.xml:4-75 et receipt_header/
   receipt_header.xml:4-27 (société, « Tél. : » fr.po:7730-7731, tirets puis
   caissier :20-23 — « Servi par Hervé Tchakounté » : getReceiptHeaderData,
   cashier: _t("Served by %s", …), store/pos_store.js:2289-2295, traduit
   « Servi par %s » fr.po:7067-7068 —, numéro de suivi), generic_components/orderline/orderline.xml:4-35
   (article, prix, « 1,00 x 7 000 FCFA / Unité(s) » — uom/i18n/fr.po:378-379),
   « Montant hors taxes » (account/i18n/fr.po:17758-17759), groupe de taxe
   « T.V.A. 19.25% » (l10n_cm/data/template/account.tax.group-cm.csv:3),
   « TOTAL » (models/pos_order.js:261, fr.po:7586-7587), puis une ligne par
   paiement (order_receipt.xml:59-63). TVA 19,25 % incluse arrondie ligne
   à ligne : 1 130 + 242 + 484 + 161 = 2 017 FCFA.
2. L'ardoise créée — aite_pos_credit/models/pos_order.py:9-27 (paiement
   mixte : seule la part payée par la méthode ardoise devient une dette),
   :103-135 (création à la synchronisation, idempotente, jamais sans
   client) ; référence ARD/ + 4 chiffres : data/pos_credit_data.xml:5-12.
   La liste : views/pos_credit_views.xml:5-36 (colonnes, texte orange « En
   retard », rouge « Critique », pastilles Origine / Sévérité / État, sommes
   en pied) ; recherche :131-170 (facette « Ouvertes » par défaut :178) ;
   tri par création décroissante : models/pos_credit.py:23 ; libellés des
   champs :30-127 ; sévérité recalculée d'après l'âge, Récente < 30 j,
   En retard ≥ 30 j, Critique ≥ 60 j : :26-28 et :162-177.
3. La fiche et l'assistant — pos_credit_views.xml:39-128 (« Enregistrer un
   remboursement », « Annuler » tant que l'ardoise est ouverte, barre
   Ouverte / Réglée, bouton « Remboursements », champs, infobulles « ? »,
   onglets « Remboursements » / « Note », colonnes Date, Moyen de paiement,
   Réf. transaction, Montant, Encaissé par, État, bouton « Annuler »
   fa-times par ligne validée, « Ajouter une ligne ») ; nombre de
   remboursements validés : pos_credit.py:149-160 ; « Total commande » et
   « Payé comptant à la vente » : :55-65. Assistant :
   wizard/pos_credit_repay_wizard_views.xml:8-31 (« Identifiant MoMo /
   réf. », « Note (optionnel)… », « Encaisser », « Annuler ») ;
   wizard/pos_credit_repay_wizard.py:17-50 (champs, Espèces par défaut),
   :53-63 (montant élevé : avertissement), :66-84 (plafonné au reste dû,
   « Encaissé par » = l'utilisateur) ; pré-rempli au reste dû :
   pos_credit.py:222-239. Bascule automatique en « Réglée » et sévérité
   « Réglée » : pos_credit.py:133-147, :170-171 ; plus aucun bouton
   d'en-tête sur une ardoise réglée (« Rouvrir » n'existe que pour une
   ardoise annulée, pos_credit_views.xml:52-54). Remboursements triés par
   date décroissante : models/pos_credit_payment.py:21 ; moyens :49-58 ;
   états Validé / Annulé :70-75.
4. Le tableau de bord — static/src/xml/dashboard.xml:24-231 (titre, filtres
   Période / Origine / Caisse, « Appliquer », sections, cartes, graphiques,
   « Tout voir », « Toutes les ardoises », colonnes, « Détail ») ; libellés
   en majuscules par la feuille de style (static/src/scss/
   pos_credit_dashboard.scss, .apc-flabel, .apc-section-title,
   .apc-kpi-label, en-têtes de tableau) ; « Ce mois » par défaut :
   static/src/js/views/dashboard_view.js:30-50 ; formats : :175-226
   (« 154 000 FCFA », « 104 j », « ▲ 156 % vs N-1 », vert quand c'est bon
   signe, « flux période : … ») et static/src/js/services/utils.js:21-45
   (couleurs des moyens, des tranches et des sévérités), :51-71 ; légendes
   masquées des barres : dashboard_view.js:255-290, 400-425 ; calculs :
   models/pos_credit_dashboard.py:120-244 (encours = photo, flux de la
   période, taux = recouvré / (encours + recouvré), retard ≥ 30 j, ardoise
   moyenne par débiteur, période précédente de même durée), :251-288
   (balance âgée 0–30 j / 30–60 j / 60–90 j / +90 j), :291-330 (encours par
   origine, palette des caisses :31-34), :336-376 (remboursements par jour,
   jj/mm), :382-429 (top 8 débiteurs par encours décroissant, âge max,
   dernier paiement, statut), :433-457 (répartition par moyen), :459-505
   (6 mois, Mai … Oct), :507-530 (derniers remboursements).

Sources des affirmations :
- douleurs : docs/guides/AITE_POS_Credit_fiche_produit.pdf p.3 (« le crédit
  client se tient sur un cahier, un carnet, ou de mémoire », « des dettes
  qui vieillissent sans relance », « une trésorerie qui se vide sans qu'on
  sache vraiment combien on doit récupérer », encadré « Qui doit combien ?
  Depuis quand ? […] Les remboursements partiels se notent mal ») ;
  docs/etude_comparative/benchmark_afrique_odoo.md:11 (« personne ne couvre
  MTN MoMo CM + Orange Money CM nativement dans un PMS ») ;
- promesse : fiche produit p.1 (« chaque dette a un nom, un montant, un âge
  et un historique de remboursements ») ; bouton : payment_screen_button.
  xml:10-20 ; sévérité selon l'âge : pos_credit.py:162-177 ; reste dû
  recalculé et « Réglée » : pos_credit.py:133-147 ;
- « Hervé sait qui relancer en premier » : fiche produit p.3 (« le gérant
  sait combien récupérer et qui relancer en priorité ») ; top débiteurs
  trié par encours (pos_credit_dashboard.py:428), et non par urgence : la
  voix ajoute « le statut dit qui est en retard » (statut = sévérité d'après
  l'âge max, :382-429) et les anneaux portent sur Sylvie Mbarga (104 j,
  Critique) et Joël Kamga (39 j, En retard, aucun paiement), pas sur la
  première ligne (Brigitte Essomba, 22 j, Récente) ;
- douleur « Remboursements MoMo et Orange Money notés nulle part » : fiche
  produit p.3 (« Les remboursements partiels se notent mal ») et benchmark
  :11 ; le module ne se branche pas aux opérateurs, il note le moyen et la
  « Réf. transaction » tapée à la main (pos_credit_payment.py:49-62,
  wizard/pos_credit_repay_wizard.py:37-45) — la vidéo ne promet aucune
  liaison MoMo / Orange Money ;
- bulles : part mise sur ardoise = dette, pos_order.py:9-27 ; seuils de
  sévérité, pos_credit.py:26-28 et :162-177 ; reste dû proposé et plafonné,
  pos_credit.py:222-239 et wizard/pos_credit_repay_wizard.py:53-84 ; part
  en retard, pos_credit_dashboard.py:120-244 et dashboard.xml:116-118 ;
  clic sur un débiteur = ses ardoises ouvertes (« Ardoises du client »,
  domaine state = open), dashboard_view.js:433-442 ;
- « Valider » s'allume dès que le reste à payer est nul et s'éteint sinon :
  odoo18 payment_screen.xml:67-77 (canBeValidated) ; les boutons des modes
  de paiement n'ont pas d'état sélectionné (payment_screen.xml:141-149) ;
  « Restant 0 FCFA » en vert : pos_order.js:886-891 (hasRemainingAmount
  vrai à zéro) et payment_status.xml:8-14 ;
- le remboursement « s'inscrit » sur la fiche (onglet Remboursements) : la
  vidéo ne dit pas « tracé » — les lignes restent modifiables après coup,
  sans historique (pos_credit_views.xml:155-170, pos_credit_payment.py:19-23) ;
- résultats : 1 bouton (payment_screen_button.xml:12-18) ; 5 moyens de
  remboursement (pos_credit_payment.py:49-58) ; 8 indicateurs
  (dashboard.xml:85-122) et balance âgée en 4 tranches
  (pos_credit_dashboard.py:262-271).

Données (fictives) : demo.py (Démo Hôtellerie SARL, Hervé Tchakounté ;
ardoises ARD/0042 Patrick Nkoulou, ARD/0039 Brigitte Essomba, ARD/0031 Joël
Kamga, ARD/0024 Armand Mvogo, ARD/0017 Sylvie Mbarga, mêmes dates et
montants ; remboursement de 20 000 FCFA en espèces du 30/09/2026 et
référence Orange Money OM261014.1530.A55120 repris de scenarios/
c3_caisse.py). Ajoutés ici, fictifs : Cédric Ngassa (client du bar, ARD/
0043), Ruth Bekolo (ARD/0036), Francis Tsala (ARD/0028), Hélène Eyidi
(ARD/0021) ; caisses « Bar de la terrasse », « Restaurant », « Boutique »
et carte du bar reprises de scenarios/t04_note_chambre.py ; fenêtre des
clients alignée sur t04_note_chambre.py:328-332 et t11_fidelite.py:469-471
(Boris Ndzana et Carine Owona, adresse et courriel de Brigitte Essomba,
courriel de Patrick Nkoulou de t11_fidelite.py:610) ; téléphones
neutralisés « +237 6 00 00 00 31 » à « … 41 » (série de t02_planning.py:199
et t08_site_web.py:195-205 ; numéro de la société « +237 6 00 00 00 10 »
comme TEL_HOTEL de t08) : aucun numéro au format d'un vrai mobile n'est
associé à une dette ; t04 et t11 gardent pour Armand Mvogo, Boris Ndzana,
Brigitte Essomba et Carine Owona des numéros de ce format — à neutraliser
de leur côté. Numérotation : vente de Cédric à 13:47, avant le règlement
Orange Money de 15:30, 4e commande de la session 33 (suivi 304,
« 00033-001-0004 ») ; commande d'origine de ARD/0024 du 18/08 : « Bar de la
terrasse/0017 », entre la /0016 du 14/08 et la /0027 du 12/09
(t11_fidelite.py:283) — le renvoi de t11 à « /0011 le 31/07 » (t11:161,
:279) est à corriger de son côté ; évolution des
mois de mai et juin (ardoises déjà soldées, non montrées). La journée est le
14/10/2026 : les âges des ardoises de demo.ARDOISES en découlent. Tous les
montants affichés sont recalculés plus bas à partir de la liste ARDOISES et
de la liste REMBOURSEMENTS, avec les règles du code.

Ce que la vidéo montre, et ce qu'elle évite :
- Le bouton suppose une méthode « ardoise » sur la caisse : l'installation
  ne la crée pas (hooks.py:46-55 en échec silencieux sous Odoo 18) ; ici la
  méthode « Ardoise client » est déjà en place, comme sur la base de
  démonstration. La vidéo ne dit pas « sans configuration ».
- Ni plafond de crédit, ni relance automatique, ni écriture 411 (case
  « Comptabiliser les remboursements » décochée par défaut,
  res_config_settings.py:61-64) ne sont montrés ou dits.
- Après « Encaisser », la fiche se recharge dès la fermeture de l'assistant
  (l'en-tête change dans le même geste) : aucune remise à jour à la main ;
  l'ardoise réglée n'a plus de bouton d'en-tête.
- La vignette est prise à l'étape 5 (« Réglée »), pas sur la carte
  « ▲ 156 % vs N-1 » (écart 5).
- « Regrouper par Sévérité » (erreur, champ non stocké) n'est pas montré.
- Deux tons de texte foncés pour le contraste AA, comme aite.css :
  orange #8A6100 des lignes « En retard », vert #1A6E2E du « Restant » nul.

Écarts relevés, rejoués tels quels (voir le rapport) :
1. Dates ISO dans le tableau de bord : « Dernier paiement » (top débiteurs)
   et « Date » (derniers remboursements) — pos_credit_dashboard.py:405-406,
   :520.
2. Le texte indicatif du courriel du reçu reste en anglais : « e.g.
   john.doe@mail.com » (odoo18 receipt_screen.xml:27, absent de fr.po).
3. Le message d'erreur du bouton (non montré) parle d'une méthode « Payer
   plus tard » et de la case « Vente à crédit » : Odoo 18 dit « Compte
   client » et la case n'a pas de libellé (payment_screen_button.js:78-82).
4. L'action « Remboursements » n'a pas d'aide d'écran vide
   (pos_credit_payment_views.xml:84-90).
5. La flèche « ▲ 156 % vs N-1 » compare à la période précédente de même
   durée (17/09–30/09), pas à l'année précédente
   (pos_credit_dashboard.py:197-220).
6. La méthode « ardoise » n'est jamais créée à l'installation : le
   post_init_hook cherche account.account.company_id, absent d'Odoo 18
   (hooks.py:46-55, erreur avalée) ; il faut la créer à la main, et sa case
   « Vente à crédit (ardoise) » s'affiche sans libellé dans le titre de la
   fiche (views/res_config_settings_views.xml:4-14).
7. L'icône fa-book du bouton « Mettre sur ardoise » n'a pas d'attribut
   title (payment_screen_button.xml:16), contre la règle de CLAUDE.md.
"""

from datetime import date

import demo
from ecrans import (APPS_PROFIL, ICONES, e, entree, fenetre_muk, fenetre_pos, icone, navigateur, pos_produits,
                    recherche, statusbar, vue_fiche)
from marketing import bulle, dezoom, reaction, zoom
from moteur import (animer, anneau, cacher, choisir, clic, classe, compter, curseur, defiler, fermer, montrer, notifier,
                    ouvrir, pause, saisir, texte, vue)

NOM, ROLE = demo.POSTES['caisse']                  # Hervé Tchakounté, caissier du bar
AUJ = date(2026, 10, 14)
JOUR = '14/10/2026'
CLIENT = 'Cédric Ngassa'                           # fictif : la note du bar mise sur ardoise
BAR, RESTO, BOUT = 'Bar de la terrasse', 'Restaurant', 'Boutique'
METHODE = 'Ardoise client'                         # aite_demo_data/models/demo_generator.py:294-303
REGLEE = 'ARD/0024'                                # l'ardoise d'Armand Mvogo, soldée en Orange Money
REF_OM = 'OM261014.1530.A55120'                    # scenarios/c3_caisse.py

# ------------------------------------------------------------------ données --
# (référence, client, caisse d'origine, ouverture, montant initial, déjà remboursé avant ce jour)
ARDOISES = [
    ('ARD/0043', CLIENT, BAR, date(2026, 10, 14), 7500, 0),
    ('ARD/0042', 'Patrick Nkoulou', BAR, date(2026, 10, 9), 18500, 0),
    ('ARD/0039', 'Brigitte Essomba', RESTO, date(2026, 9, 22), 42000, 12000),
    ('ARD/0036', 'Ruth Bekolo', BOUT, date(2026, 9, 16), 15000, 5000),
    ('ARD/0031', 'Joël Kamga', BAR, date(2026, 9, 5), 27000, 0),
    ('ARD/0028', 'Francis Tsala', RESTO, date(2026, 8, 29), 22500, 7500),
    ('ARD/0024', 'Armand Mvogo', BAR, date(2026, 8, 18), 64500, 20000),
    ('ARD/0021', 'Hélène Eyidi', BAR, date(2026, 7, 31), 16000, 0),
    ('ARD/0017', 'Sylvie Mbarga', RESTO, date(2026, 7, 2), 35000, 5000),
]
# (date, ardoise, client, moyen, réf. transaction, montant) — le premier est celui de la vidéo
REMBOURSEMENTS = [
    (date(2026, 10, 14), 'ARD/0024', 'Armand Mvogo', 'Orange Money', REF_OM, 44500),
    (date(2026, 10, 10), 'ARD/0028', 'Francis Tsala', 'Orange Money', 'OM261010.1912.C20418', 7500),
    (date(2026, 10, 6), 'ARD/0039', 'Brigitte Essomba', 'MTN Mobile Money', '7349218805', 12000),
    (date(2026, 9, 30), 'ARD/0024', 'Armand Mvogo', 'Espèces', '', 20000),
    (date(2026, 9, 28), 'ARD/0036', 'Ruth Bekolo', 'Espèces', '', 5000),
    (date(2026, 8, 12), 'ARD/0017', 'Sylvie Mbarga', 'Espèces', '', 5000),
]
# Numéros neutralisés (série « +237 6 00 00 00 xx » de t02_planning.py:199 et t08_site_web.py:195-205) :
# aucun numéro au format d'un vrai mobile n'est associé à une dette.
TELEPHONES = {'Armand Mvogo': '+237 6 00 00 00 31', 'Brigitte Essomba': '+237 6 00 00 00 32',
              CLIENT: '+237 6 00 00 00 33', 'Francis Tsala': '+237 6 00 00 00 34', 'Joël Kamga': '+237 6 00 00 00 35',
              'Patrick Nkoulou': '+237 6 00 00 00 36', 'Sylvie Mbarga': '+237 6 00 00 00 37',
              'Hélène Eyidi': '+237 6 00 00 00 38', 'Ruth Bekolo': '+237 6 00 00 00 39',
              'Boris Ndzana': '+237 6 00 00 00 40', 'Carine Owona': '+237 6 00 00 00 41'}
# Les remboursements d'avant ce jour expliquent « Déjà remboursé ».
for _ref, _cli, _c, _d, _mt, _deja in ARDOISES:
    assert _deja == sum(r[5] for r in REMBOURSEMENTS[1:] if r[1] == _ref), _ref
assert REMBOURSEMENTS[0][5] == 64500 - 20000


def fcfa(n):
    """Un montant au format d'Odoo pour le franc CFA (arrondi 1, symbole après)."""
    signe = '-' if n < 0 else ''
    return signe + '{:,}'.format(abs(int(round(n)))).replace(',', ' ') + ' FCFA'


def jj(d):
    return d.strftime('%d/%m/%Y')


def age(d):
    return (AUJ - d).days


def severite(jours):
    """pos_credit.py:162-177 : Récente, En retard ≥ 30 j, Critique ≥ 60 j."""
    if jours >= 60:
        return 'Critique', 'rouge'
    if jours >= 30:
        return 'En retard', 'orange'
    return 'Récente', 'vert'


def pct(v):
    """utils.js:69-71 : un chiffre après la virgule, virgule française."""
    r = round(v * 10) / 10.0
    return ('%d' % r if r == int(r) else ('%.1f' % r).replace('.', ',')) + ' %'


OUVERTES = [a for a in ARDOISES if a[0] != REGLEE]          # après le remboursement de l'étape 4
DEBUT_MOIS, AVANT_DEBUT, AVANT_FIN = date(2026, 10, 1), date(2026, 9, 17), date(2026, 9, 30)
ENCOURS = sum(a[4] - a[5] for a in OUVERTES)
RECOUVRE = sum(r[5] for r in REMBOURSEMENTS if DEBUT_MOIS <= r[0] <= AUJ)
NB_REMB = len([r for r in REMBOURSEMENTS if DEBUT_MOIS <= r[0] <= AUJ])
OUVERT_MOIS = [a for a in ARDOISES if DEBUT_MOIS <= a[3] <= AUJ]
RECOUVRE_AVANT = sum(r[5] for r in REMBOURSEMENTS if AVANT_DEBUT <= r[0] <= AVANT_FIN)
OUVERT_AVANT = sum(a[4] for a in ARDOISES if AVANT_DEBUT <= a[3] <= AVANT_FIN)
NOUVELLES = sum(a[4] for a in OUVERT_MOIS)
RETARD = sum(a[4] - a[5] for a in OUVERTES if age(a[3]) >= 30)
DEBITEURS = len(set(a[1] for a in OUVERTES))
PLUS_VIEILLE = min(OUVERTES, key=lambda a: a[3])
DELTA_REC = (RECOUVRE - RECOUVRE_AVANT) * 100.0 / RECOUVRE_AVANT
DELTA_NEW = (NOUVELLES - OUVERT_AVANT) * 100.0 / OUVERT_AVANT
TRANCHES = [('0–30 j', -10 ** 9, 30), ('30–60 j', 30, 60), ('60–90 j', 60, 90), ('+90 j', 90, 10 ** 9)]
AGING = [sum(a[4] - a[5] for a in OUVERTES if lo <= age(a[3]) < hi) for _, lo, hi in TRANCHES]
assert sum(AGING) == ENCOURS
assert (ENCOURS, RECOUVRE, NOUVELLES, RETARD) == (154000, 64000, 26000, 88000)

# ======================================================== 1. la caisse du bar --
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
# Le ticket de Cédric Ngassa (prix TTC, TVA 19,25 % incluse, arrondie ligne à ligne : 2 017 FCFA).
TICKET = [('t10-l1', 'Poisson braisé', '1,00', '7 000 FCFA', '7 000 FCFA'),
          ('t10-l2', 'Plantain frit', '1,00', '1 500 FCFA', '1 500 FCFA'),
          ('t10-l3', 'Bière blonde 65 cl', '2,00', '1 500 FCFA', '3 000 FCFA'),
          ('t10-l4', 'Jus de bissap 50 cl', '1,00', '1 000 FCFA', '1 000 FCFA')]
TOTAL, TAXES, HT = '12 500 FCFA', '2 017 FCFA', '10 483 FCFA'
COMPTANT, A_CREDIT = '5 000 FCFA', '7 500 FCFA'
NUMERO = '304'                                     # (session 33 % 10) × 100 + 4 : pos_order.py:58-60
REF_TICKET, HEURE = '00033-001-0004', '14/10/2026 13:47:05'   # pos_store.js:1141-1159
VENTE = (pos_produits('t10-vente', CATEGORIES, [('t10-p%d' % i, n, c) for i, (n, c) in enumerate(CARTE_BAR)],
                      TICKET, TOTAL, TAXES, initiale=True)
         .replace('/ Unités', '/ Unité(s)')
         .replace('class="pv-ligne" id="t10-l4"', 'class="pv-ligne sel" id="t10-l4"'))

# -- l'écran de paiement (payment_screen.xml), composé ici pour poser des cibles sur le pavé
LIVRE = '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M6 3h11a2 2 0 012 2v12H7.5a1.5 1.5 0 000 3H19v1H7.5A3.5 3.5 0 014 17.5V5a2 2 0 012-2z"/></svg>'
ESPECES = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="2" y="6" width="20" '
           'height="12" rx="2"/><circle cx="12" cy="12" r="2.8"/><path d="M5.5 9.5v5M18.5 9.5v5"/></svg>')
PLUS_TARD = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="2" y="5" width="17" '
             'height="12" rx="2"/><path d="M2 9h17"/><circle cx="18" cy="17" r="4.5" fill="#fff"/><path d="M18 15v2.2l1.4 '
             '1" stroke-linecap="round"/></svg>')
MODES = [('t10-m-esp', 'Espèces', ESPECES), ('t10-m-om', 'Orange Money', ICONES['carte']),
         ('t10-m-momo', 'MTN MoMo', ICONES['carte']), ('t10-m-note', 'Note de chambre', PLUS_TARD),
         ('t10-m-ard', METHODE, PLUS_TARD)]
TOUCHES = [('1', ''), ('2', ''), ('3', ''), ('+10', ' vert'), ('4', ''), ('5', ''), ('6', ''), ('+20', ' vert'),
           ('7', ''), ('8', ''), ('9', ''), ('+50', ' vert'), ('+/-', ' jaune'), ('0', ''), (',', ' rose'),
           ('⌫', ' rouge')]
PAVE = ''.join('<span class="pk%s" id="t10-k%s">%s</span>' % (c, {'+/-': 'pm', ',': 'v', '⌫': 'eff'}.get(t, t.replace('+', 'p')), e(t))
               for t, c in TOUCHES)
PAIEMENT = (
    '<div class="vue" id="t10-paie"><div class="pos-vente">'
    '<div class="pos-g"><div class="pos-modes">%s</div>'
    '<div class="pos-cf"><span id="t10-cli"><em class="t10-ico">%s</em><em class="t10-cli-p">'
    '<b id="t10-cli-0">Client</b><b class="t10-nomcli masque" id="t10-cli-1">%s</b></em></span>'
    '<span><em class="t10-ico">%s</em>Facture<i></i></span></div>'
    '<div class="pos-ardoise" id="t10-ard"><span class="ico">%s</span>Mettre sur ardoise</div>'
    '<div class="pos-pave">%s</div>'
    '<div class="pos-rv"><span>Retour</span><span class="v t10-off" id="t10-valider">Valider</span></div></div>'
    '<div class="pos-d pos-pd"><div class="pos-du">%s</div>'
    '<div class="t10-choix" id="t10-msg">Veuillez sélectionner un mode de paiement</div>'
    '<div class="t10-zone"><div class="pile"><div class="pos-restant masque t10-ok" id="t10-st-ok"><span>Restant</span>'
    '<span>0 FCFA</span></div><div class="pos-restant masque t10-du" id="t10-st-du"><span>Restant</span>'
    '<b id="t10-st-du-v">12 495 FCFA</b></div></div>'
    '<div class="pos-pl masque t10-pl" id="t10-pl-esp"><span>Espèces</span><span id="t10-pl-esp-mt">%s</span>'
    '<span class="x">×</span></div></div></div></div></div>'
    % (''.join('<div class="pos-mode" id="%s"><span class="ico">%s</span><span>%s</span></div>' % (i, s, e(l))
               for i, l, s in MODES),
       ICONES['personne'], e(CLIENT), ICONES['document'], LIVRE, PAVE, TOTAL, TOTAL))

# -- la fenêtre des clients (pos.selectPartner)
ENVOI = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round">'
         '<path d="M22 2L11 13M22 2l-7 20-4-9-9-4z"/></svg>')
CLIENTS = [('Armand Mvogo', 'Bastos Yaoundé Cameroun', 'armand.mvogo@exemple.cm'),
           ('Boris Ndzana', 'Akwa Douala Cameroun', 'boris.ndzana@exemple.cm'),
           ('Brigitte Essomba', 'Bonamoussadi Douala Cameroun', 'brigitte.essomba@exemple.cm'),
           ('Carine Owona', 'Bali Douala Cameroun', 'carine.owona@exemple.cm'),
           (CLIENT, 'Deïdo Douala Cameroun', 'cedric.ngassa@exemple.cm'),
           ('Francis Tsala', 'Makepe Douala Cameroun', 'f.tsala@exemple.cm'),
           ('Joël Kamga', 'Bonamoussadi Douala Cameroun', 'joel.kamga@exemple.cm'),
           ('Patrick Nkoulou', 'Bali Douala Cameroun', 'patrick.nkoulou@exemple.cm')]


def ligne_client(nom, adresse, mail, ident=None):
    return ('<div class="t10-cl"%s><b>%s</b><span>%s</span><span class="t10-ct"><span><i>%s</i>%s</span>'
            '<span><i>%s</i>%s</span></span><span class="t10-cl-m">☰</span></div>'
            % (' id="%s"' % ident if ident else '', e(nom), e(adresse), ICONES['telephone'], e(TELEPHONES[nom]),
               ENVOI, e(mail)))


DIALOGUE = (
    '<div class="voile masque" id="t10-dlg-voile" data-layout-allow-overlap data-layout-allow-occlusion></div>'
    '<div class="modale masque t10-dlg" id="t10-dlg" data-layout-allow-overlap data-layout-allow-occlusion>'
    '<div class="t10-dlg-h"><span class="bt primaire t10-creer">Créer</span>%s</div>'
    '<div class="t10-dlg-c"><div class="t10-cl t10-cl-tete"><span>Nom</span><span>Adresse</span><span>Contact</span>'
    '<span></span></div><div class="pile"><div id="t10-tous">%s</div><div class="masque" id="t10-trouves">%s'
    '<div class="t10-plus"><span class="bt primaire">Rechercher plus</span></div></div></div></div>'
    '<div class="t10-dlg-p"><span class="bt gris">Ignorer</span></div></div>'
    % (entree('t10-q', 'Recherche des clients...', classe='entree t10-q'), ''.join(ligne_client(*c) for c in CLIENTS),
       ligne_client(*CLIENTS[4], ident='t10-c-ngassa')))
# La notification d'Odoo (type warning, sans titre), en haut à droite de la caisse.
TOAST_CLI = ('<div class="toast masque alerte t10-toast" id="t10-toast-cli" data-layout-allow-overlap '
             'data-layout-allow-occlusion>Sélectionnez d\'abord un client pour une vente à crédit.</div>')

# -- le reçu (receipt_screen.xml, order_receipt.xml)
CERCLE_OK = ('<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="11" fill="currentColor"/>'
             '<path d="M6.5 12.5l3.6 3.6 7.4-7.6" fill="none" stroke="#D1E7DD" stroke-width="2.6" stroke-linecap="round" '
             'stroke-linejoin="round"/></svg>')
TIRETS = '<div class="t10-tirets">--------------------------------</div>'


def ligne_recu(article, qte, prix, montant):
    return ('<div class="pv-ligne t10-rl"><div class="a"><b>%s</b><b>%s</b></div><div class="q"><b>%s</b> x %s / Unité(s)'
            '</div></div>' % (e(article), e(montant), e(qte), e(prix)))


def montant(lib, val, classe_=''):
    return '<div class="t10-rm%s"><span>%s</span><span>%s</span></div>' % (classe_, e(lib), e(val))


RECU = (
    '<div class="vue" id="t10-recu"><div class="t10-recu">'
    '<div class="t10-actions"><div class="t10-reussi" id="t10-reussi"><span class="t10-okico">%s</span>'
    '<b>Paiement réussi</b><div class="t10-mt"><span>%s</span><span class="t10-modif">Modifier le paiement</span></div>'
    '</div><hr><span class="t10-imprimer"><span class="ico">%s</span>Imprimer le reçu complet</span>'
    '<div class="t10-mail"><span class="t10-in">e.g. john.doe@mail.com</span><span class="t10-envoi">%s</span></div>'
    '<div class="t10-nouv">Nouvelle commande</div></div>'
    '<div class="t10-recu-d"><div class="t10-ticket"><div class="t10-ent"><div>%s</div><div>Tél. : +237 6 00 00 00 10</div>'
    '%s<div>Servi par %s</div><div class="t10-suivi">%s</div></div>%s%s'
    '<div class="t10-tx">%s%s</div>%s<div class="t10-tk-paie" id="t10-tk-paie">%s%s%s</div>'
    '<div class="t10-gen">Généré par Odoo<br>%s<br>%s</div></div></div></div></div>'
    % (CERCLE_OK, TOTAL, ICONES['imprimer'], ENVOI, e(demo.SOCIETE), TIRETS, e(NOM), NUMERO,
       ''.join(ligne_recu(a, q, p, m) for _, a, q, p, m in TICKET), TIRETS,
       montant('Montant hors taxes', HT), montant('T.V.A. 19.25%', TAXES), TIRETS,
       montant('TOTAL', TOTAL, ' t10-total'), montant('Espèces', COMPTANT), montant(METHODE, A_CREDIT, ' t10-ard-l'),
       REF_TICKET, HEURE))

NAV_POS = navigateur(fenetre_pos('t10-pos', [VENTE, PAIEMENT, RECU], NOM, numero=NUMERO,
                                 calques=DIALOGUE + TOAST_CLI))

# ===================================================== 2. POS Crédit (bureau) --
ENGRENAGE = ('<svg viewBox="0 0 24 24" fill="currentColor"><path d="M10.3 2h3.4l.5 2.6c.6.2 1.2.5 1.7.9l2.5-.9 1.7 '
             '2.9-2 1.7c.1.6.1 1.2 0 1.8l2 1.7-1.7 2.9-2.5-.9c-.5.4-1.1.7-1.7.9l-.5 2.6h-3.4l-.5-2.6c-.6-.2-1.2-.5-1.7'
             '-.9l-2.5.9-1.7-2.9 2-1.7a6 6 0 010-1.8l-2-1.7 1.7-2.9 2.5.9c.5-.4 1.1-.7 1.7-.9zM12 9a3 3 0 100 6 3 3 0 '
             '000-6z" transform="translate(0 1.5) scale(.9) translate(1.3 0)"/></svg>')
FLECHES = '<span class="t10-fl"><i>‹</i><i>›</i></span>'
MENUS = ['Recouvrement', 'Ardoises', 'Remboursements']

# -- la liste des ardoises ouvertes
COLS = [('Référence', '108px'), ('Client', '172px'), ('Origine', '138px'), ("Caisse d'origine", '164px'),
        ("Date d'ouverture", '118px'), ('Montant initial', '128px', 'd'), ('Déjà remboursé', '134px', 'd'),
        ('Reste dû', '124px', 'd'), ('Âge (j)', '62px', 'd'), ('Sévérité', '104px'), ('État', '1fr')]
GABARIT = '34px ' + ' '.join(c[1] for c in COLS)


def cellule(texte_, droite=False, ident=None):
    return '<span class="ell%s"%s>%s</span>' % (' d' if droite else '', ' id="%s"' % ident if ident else '', e(texte_))


def badge(texte_, genre, ident=None):
    return '<span%s><span class="puce %s">%s</span></span>' % (' id="%s"' % ident if ident else '', genre, e(texte_))


LIGNES = []
for _i, (_ref, _cli, _caisse, _d, _mt, _deja) in enumerate(ARDOISES):
    _sev, _genre = severite(age(_d))
    LIGNES.append('<div class="ligne%s" id="t10-r%d" style="grid-template-columns:%s"><span class="cb"></span>%s</div>' % (
        {'orange': ' retard', 'rouge': ' critique'}.get(_genre, ''), _i, GABARIT, ''.join([
            cellule(_ref), cellule(_cli), badge('Point de vente', 'info'), cellule(_caisse), cellule(jj(_d)),
            cellule(fcfa(_mt), True), cellule(fcfa(_deja), True), cellule(fcfa(_mt - _deja), True),
            cellule(str(age(_d)), True), badge(_sev, _genre, 't10-r%d-sev' % _i), badge('Ouverte', 'info')])))
TETE = '<div class="tete" style="grid-template-columns:%s"><span class="cb"></span>%s</div>' % (
    GABARIT, ''.join('<span class="ell%s"%s>%s</span>' % (' d' if len(c) > 2 else '',
                                                       ' id="t10-h-sev"' if c[0] == 'Sévérité' else '', e(c[0]))
                     for c in COLS))
SOMME = '<div class="total" id="t10-tot" style="grid-template-columns:%s"><span></span>%s</div>' % (
    GABARIT, '<span></span>' * 5 + ''.join('<span class="d">%s</span>' % fcfa(v) for v in (
        sum(a[4] for a in ARDOISES), sum(a[5] for a in ARDOISES), sum(a[4] - a[5] for a in ARDOISES)))
    + '<span></span>' * 3)
CP_LISTE = ('<div class="cp t10-cp"><span class="bt primaire">Nouveau</span><span class="titre">Ardoises</span>'
            '<span class="t10-engr">%s</span>%s<span class="pager">1-%d / %d</span>%s</div>'
            % (ENGRENAGE, recherche([('t10-fac', 'Ouvertes')], placeholder='Rechercher...'), len(ARDOISES),
               len(ARDOISES), FLECHES))
LISTE = ('<div class="vue initiale" id="t10-liste">%s<div class="liste t10-liste">%s%s%s'
         '<div class="t10-ancre" id="t10-ancre-sev"></div></div></div>'
         % (CP_LISTE, TETE, ''.join(LIGNES), SOMME))

# -- la fiche ARD/0024
_A = ARDOISES[6]
assert _A[0] == REGLEE
POS_FICHE = '%d / %d' % (7, len(ARDOISES))
CP_FICHE = ('<div class="cp t10-cp"><span class="bt contour">Nouveau</span><div class="fil"><span class="parent">Ardoises'
            '</span><span class="ref">%s <span class="t10-engr">%s</span></span></div>'
            '<span class="t10-stat" id="t10-stat"><span class="sic">%s</span><span class="st-t"><span>Remboursements</span>'
            '<b id="t10-stat-v">1</b></span></span><span class="pager">%s</span>%s</div>'
            % (REGLEE, ENGRENAGE, ICONES['billet'], POS_FICHE, FLECHES))


def ch(libelle, valeur, ident=None, gras=False, aide=False, saisie=False, lien_=False, lid=None):
    return ('<div class="ch t10-ch"><span class="l%s"%s>%s%s</span><span class="v%s%s"%s>%s</span></div>'
            % (' gras' if gras else '', ' id="%s"' % lid if lid else '', e(libelle),
               '<sup class="t10-aide">?</sup>' if aide else '', ' t10-saisie' if saisie else '',
               ' t10-lien' if lien_ else '', ' id="%s"' % ident if ident else '', valeur))


GAUCHE = ''.join([
    ch('Client', e(_A[1]), gras=True, saisie=True, lid='t10-l-cli', ident='t10-v-cli'),
    ch("Date d'ouverture", jj(_A[3]), gras=True, saisie=True, lid='t10-l-date', ident='t10-v-date'),
    ch('Origine', '<span class="puce gris t10-pg">Point de vente</span>', aide=True),
    ch("Commande POS d'origine", e('%s/0017' % BAR), lien_=True),
    ch("Caisse d'origine", e(BAR), lien_=True),
    ch('Total commande', fcfa(74500), aide=True),
    ch('Payé comptant à la vente', fcfa(10000), aide=True)])
DROITE = ''.join([
    ch('Montant initial', fcfa(_A[4]), aide=True),
    ch('Déjà remboursé', fcfa(_A[5]), 't10-f-deja'),
    ch('Reste dû', fcfa(_A[4] - _A[5]), 't10-f-reste'),
    ch('Âge (jours)', str(age(_A[3])), aide=True),
    ch('Sévérité', severite(age(_A[3]))[0], 't10-f-sev')])
COLS_R = '128px 220px 250px 140px 210px 110px 1fr'
X_ANNULER = '<span class="t10-xa">%s</span>' % ICONES['x']


def table_remb(ident, lignes, total):
    tete = ('<div class="t-tete" style="grid-template-columns:%s"><span>Date</span><span>Moyen de paiement</span>'
            '<span>Réf. transaction</span><span class="d">Montant</span><span>Encaissé par</span><span>État</span>'
            '<span></span></div>' % COLS_R)
    corps = ''.join('<div class="t-ligne" id="%s-%d" style="grid-template-columns:%s"><span>%s</span><span>%s</span>'
                    '<span class="ell">%s</span><span class="d">%s</span><span class="ell">%s</span>'
                    '<span><span class="puce vert">Validé</span></span>%s</div>'
                    % (ident, i, COLS_R, jj(d), e(moyen), e(ref), fcfa(mt), e(NOM), X_ANNULER)
                    for i, (d, _r, _c, moyen, ref, mt) in enumerate(lignes))
    return ('<div class="table t10-table%s" id="%s">%s%s<div class="t-ajout">Ajouter une ligne</div>'
            '<div class="t-total" style="grid-template-columns:%s"><span></span><span></span><span></span>'
            '<span class="d">%s</span><span></span><span></span><span></span></div></div>'
            % ('' if ident == 't10-ta' else ' masque', ident, tete, corps, COLS_R, fcfa(total)))


_REMB_A = [r for r in REMBOURSEMENTS if r[1] == REGLEE]
FEUILLE = ('<div class="f-titre t10-titre">%s</div><div class="f-cols t10-cols"><div>%s</div><div id="t10-g-mt">%s</div>'
           '</div><div class="onglets t10-onglets"><span class="onglet actif">Remboursements</span>'
           '<span class="onglet">Note</span></div><div class="pile">%s%s</div>'
           % (REGLEE, GAUCHE, DROITE, table_remb('t10-ta', _REMB_A[1:], _A[5]), table_remb('t10-tb', _REMB_A, _A[4])))
FICHE = vue_fiche('t10-fiche', CP_FICHE,
                  ['<span class="bt primaire" id="t10-b-remb">Enregistrer un remboursement</span>',
                   '<span class="bt gris">Annuler</span>'],
                  statusbar('t10-sb', ['Ouverte', 'Réglée'], 0), FEUILLE)

# -- l'assistant « Enregistrer un remboursement »
CALENDRIER = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="5" width="18" '
              'height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/></svg>')


def lm(libelle, valeur_html, gras=False, ident=None):
    return ('<div class="m-ch t10-mch"%s><span class="l%s">%s</span><span class="v">%s</span></div>'
            % (' id="%s"' % ident if ident else '', ' t10-gras' if gras else '', e(libelle), valeur_html))


ASSISTANT = (
    '<div class="voile masque" id="t10-as-voile" data-layout-allow-overlap data-layout-allow-occlusion></div>'
    '<div class="modale masque t10-as" id="t10-as" data-layout-allow-overlap data-layout-allow-occlusion>'
    '<div class="m-tete"><span>Enregistrer un remboursement</span><span class="m-x">%s</span></div>'
    '<div class="m-corps"><div class="m-grille"><div>%s%s%s</div><div>%s%s%s%s</div></div>'
    '<div class="t10-note">Note (optionnel)…</div></div>'
    '<div class="m-pied"><span class="bt primaire" id="t10-as-ok">Encaisser</span><span class="bt gris">Annuler</span>'
    '</div></div>'
    % (ICONES['x'],
       lm('Ardoise', '<span class="t10-lien">%s</span>' % REGLEE),
       lm('Client', '<span class="t10-lien">%s</span>' % e(_A[1])),
       lm('Reste dû actuel', fcfa(_A[4] - _A[5])),
       lm('Montant à encaisser', '<span class="t10-mon" id="t10-as-mt"><span>%s</span><small>FCFA</small></span>'
          % fcfa(_A[4] - _A[5])[:-5], gras=True),
       lm('Moyen de paiement', entree('t10-as-moy', '', 'Espèces', classe='entree t10-sel'), gras=True),
       lm('Réf. transaction', entree('t10-as-ref', 'Identifiant MoMo / réf.', classe='entree t10-ref'), gras=True),
       lm('Date', '<span class="t10-date">%s<span class="ico">%s</span></span>' % (JOUR, CALENDRIER), gras=True)))

# -- le tableau de bord « POS Crédit — Recouvrement »
AXE = '#E5E7EB'


def grille_y(ymax, pas, w, h, gauche=46):
    """Les graduations de Chart.js : « 0 », « 10 k »… (utils.js fmtCompact)."""
    out = []
    n = ymax // pas
    for k in range(n + 1):
        y = h - k * h / float(n)
        lib = '0' if k == 0 else '%d k' % (k * pas // 1000)
        out.append('<line x1="%d" x2="%d" y1="%.1f" y2="%.1f" stroke="%s"/>' % (gauche, w, y, y, AXE))
        out.append('<text x="%d" y="%.1f" text-anchor="end" class="t10-tick">%s</text>' % (gauche - 8, y + 4, lib))
    return ''.join(out)


def barres(ident, valeurs, couleurs, etiquettes, ymax, pas, w=700, h=190):
    n = len(valeurs)
    zone = (w - 46) / float(n)
    larg = zone * 0.62
    bars = ''.join('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="3" fill="%s"/>'
                   % (46 + zone * i + (zone - larg) / 2, h - v * h / float(ymax), larg, v * h / float(ymax), c)
                   for i, (v, c) in enumerate(zip(valeurs, couleurs)))
    labs = ''.join('<text x="%.1f" y="%d" text-anchor="middle" class="t10-tick">%s</text>'
                   % (46 + zone * i + zone / 2, h + 22, e(t)) for i, t in enumerate(etiquettes) if t)
    return ('<svg class="t10-svg" viewBox="0 -6 %d %d" width="%d" height="%d">%s<g class="t10-barres" id="%s">%s</g>%s</svg>'
            % (w, h + 34, w, h + 34, grille_y(ymax, pas, w, h), ident, bars, labs))


def courbe(points):
    """Une courbe lissée (tension 0,3 de Chart.js), en Bézier cubiques."""
    d = 'M%.1f,%.1f' % points[0]
    for i in range(len(points) - 1):
        p0 = points[max(0, i - 1)]
        p1, p2 = points[i], points[i + 1]
        p3 = points[min(len(points) - 1, i + 2)]
        c1 = (p1[0] + (p2[0] - p0[0]) * 0.15, p1[1] + (p2[1] - p0[1]) * 0.15)
        c2 = (p2[0] - (p3[0] - p1[0]) * 0.15, p2[1] - (p3[1] - p1[1]) * 0.15)
        d += ' C%.1f,%.1f %.1f,%.1f %.1f,%.1f' % (c1 + c2 + p2)
    return d


def courbes(ident, series, etiquettes, ymax, pas, w=700, h=170):
    n = len(etiquettes)
    xs = [46 + 12 + i * (w - 46 - 24) / float(n - 1) for i in range(n)]
    tracés = []
    for valeurs, coul in series:
        pts = [(x, h - v * h / float(ymax)) for x, v in zip(xs, valeurs)]
        ligne = courbe(pts)
        tracés.append('<path d="%s L%.1f,%d L%.1f,%d Z" fill="%s" fill-opacity=".13"/>'
                      '<path d="%s" fill="none" stroke="%s" stroke-width="3"/>%s'
                      % (ligne, xs[-1], h, xs[0], h, coul, ligne, coul,
                         ''.join('<circle cx="%.1f" cy="%.1f" r="3.5" fill="#fff" stroke="%s" stroke-width="2"/>'
                                 % (x, y, coul) for x, y in pts)))
    labs = ''.join('<text x="%.1f" y="%d" text-anchor="middle" class="t10-tick">%s</text>' % (x, h + 22, e(t))
                   for x, t in zip(xs, etiquettes))
    return ('<svg class="t10-svg" viewBox="0 -6 %d %d" width="%d" height="%d">%s<g id="%s">%s</g>%s</svg>'
            % (w, h + 30, w, h + 30, grille_y(ymax, pas, w, h), ident, ''.join(tracés), labs))


def donut(parts, r=78):
    """Un anneau Chart.js (cutout 56 %, bord blanc de 2 px) et sa légende à droite."""
    total = float(sum(p[1] for p in parts))
    rm = r * 0.78
    c = 2 * 3.14159265 * rm
    debut, arcs = 0.0, []
    for _lib, v, coul in parts:
        lg = c * v / total
        arcs.append('<circle r="%.1f" cx="100" cy="100" fill="none" stroke="%s" stroke-width="%.1f" '
                    'stroke-dasharray="%.1f %.1f" stroke-dashoffset="%.1f"/>' % (rm, coul, r * 0.44, lg, c - lg, -debut))
        debut += lg
    import math
    sep, ang = [], 0.0
    for _lib, v, _c in parts:
        x1, y1 = 100 + (r - r * 0.44) * math.cos(ang), 100 + (r - r * 0.44) * math.sin(ang)
        x2, y2 = 100 + (r + 2) * math.cos(ang), 100 + (r + 2) * math.sin(ang)
        sep.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#fff" stroke-width="2"/>' % (x1, y1, x2, y2))
        ang += 2 * math.pi * v / total
    arcs.extend(sep)
    leg = ''.join('<div class="t10-leg"><i style="background:%s"></i>%s</div>' % (coul, e(lib)) for lib, _v, coul in parts)
    return ('<div class="t10-donut"><svg viewBox="0 0 200 200" width="200" height="200"><g transform="rotate(-90 100 100)">'
            '%s</g></svg><div class="t10-legs">%s</div></div>' % (''.join(arcs), leg))


def kpi_(ident, lib, val, sous, accent=None, delta=None):
    d = '<div class="t10-kd %s">%s</div>' % (delta[1], e(delta[0])) if delta else ''
    return ('<div class="t10-kpi%s" id="%s"><div class="t10-kl">%s</div><div class="t10-kv" id="%s-v">%s</div>%s'
            '<div class="t10-ks">%s</div></div>' % (' mega acc-' + accent if accent else '', ident, e(lib), ident,
                                                   e(val), d, e(sous)))


def chips(lib, liste, actif=0, dots=None):
    return ('<div class="t10-frang"><span class="t10-flab">%s</span>%s</div>'
            % (e(lib), ''.join('<span class="t10-chip%s">%s%s</span>' % (
                ' actif' if i == actif else '', '<i class="t10-dot" style="background:%s"></i>' % dots[i] if dots and dots[i]
                else '', e(x)) for i, x in enumerate(liste))))


def section(titre, droite=''):
    return '<div class="t10-sect"><span>%s</span>%s</div>' % (e(titre), droite)


def carte_g(titre, contenu, mini='', ident=None):
    return ('<div class="t10-card"%s><h3>%s</h3><div class="t10-chart">%s</div>%s</div>'
            % (' id="%s"' % ident if ident else '', e(titre), contenu,
               '<div class="t10-mini">%s</div>' % e(mini) if mini else ''))


def flux(n):
    """dashboard_view.js:200-204 : « flux période : » + signe + montant."""
    return 'flux période : %s%s' % ('+' if n > 0 else '', fcfa(n))


def delta(v, bon_si_hausse):
    r = round(v * 10) / 10.0
    fl = '▲' if r > 0 else ('▼' if r < 0 else '■')
    bon = r >= 0 if bon_si_hausse else r <= 0
    txt = ('%d' % abs(r) if abs(r) == int(abs(r)) else ('%.1f' % abs(r)).replace('.', ','))
    return '%s %s %% vs N-1' % (fl, txt), 'haut' if bon else 'bas'


MOIS = ['Mai', 'Juin', 'Juil', 'Août', 'Sep', 'Oct']
OUVERTES_MOIS = [38000, 44000] + [sum(a[4] for a in ARDOISES if a[3].month == m) for m in (7, 8, 9, 10)]
RECOUVRE_MOIS = [29000, 47500, 31000, 26000] + [sum(r[5] for r in REMBOURSEMENTS if r[0].month == m) for m in (9, 10)]
PALETTE = {BAR: '#714B67', RESTO: '#185FA5', BOUT: '#3B6D11'}      # pos_credit_dashboard.py:31-34, par caisse
PAR_CAISSE = sorted(((c, sum(a[4] - a[5] for a in OUVERTES if a[2] == c)) for c in (BAR, RESTO, BOUT)),
                    key=lambda x: -x[1])
PAR_MOYEN = sorted(((m, sum(r[5] for r in REMBOURSEMENTS if r[3] == m and r[0] >= DEBUT_MOIS))
                    for m in ('Orange Money', 'MTN Mobile Money')), key=lambda x: -x[1])
COUL_MOYEN = {'Orange Money': '#FF7900', 'MTN Mobile Money': '#FFC403'}
JOURS = [date(2026, 10, j) for j in range(1, 15)]
PAR_JOUR = [sum(r[5] for r in REMBOURSEMENTS if r[0] == j) for j in JOURS]

# le top débiteurs (pos_credit_dashboard.py:382-429) : encours décroissant, à égalité l'ordre de création décroissant
TOP = []
for _cli in dict.fromkeys(a[1] for a in OUVERTES):
    _sienne = [a for a in OUVERTES if a[1] == _cli]
    _dern = [r for r in REMBOURSEMENTS if r[2] == _cli]
    TOP.append((_cli, sum(a[4] - a[5] for a in _sienne), max(age(a[3]) for a in _sienne),
                max(r[0] for r in _dern).isoformat() if _dern else '—'))
TOP.sort(key=lambda x: -x[1])
TOP = TOP[:8]
MAX_TOP = float(max(t[1] for t in TOP))
COLS_TOP = '250px 220px 250px 130px 200px 140px 1fr'
TOP_HTML = ('<div class="t10-tab" id="t10-top"><div class="t10-th" style="grid-template-columns:%s"><span>Client</span>'
            '<span>Téléphone</span><span class="d">Encours</span><span class="d">Âge max</span><span>Dernier paiement'
            '</span><span>Statut</span><span></span></div>%s</div>' % (COLS_TOP, ''.join(
                '<div class="t10-tr" id="t10-d%d" style="grid-template-columns:%s"><b>%s</b><span class="t10-gris">%s</span>'
                '<span class="t10-barc"><i style="width:%.0f%%"></i><b>%s</b></span><span class="d">%d j</span>'
                '<span class="t10-gris">%s</span>%s<span><span class="t10-det" id="t10-d%d-det">Détail</span></span></div>'
                % (i, COLS_TOP, e(c), e(TELEPHONES[c]), mt * 100 / MAX_TOP, fcfa(mt), ag, dp,
                   badge(*severite(ag)), i) for i, (c, mt, ag, dp) in enumerate(TOP))))
DERNIERS = ('<div class="t10-tab t10-tab-p"><div class="t10-th" style="grid-template-columns:150px 1fr 200px 150px">'
            '<span>Date</span><span>Client</span><span>Moyen</span><span class="d">Montant</span></div>%s</div>'
            % ''.join('<div class="t10-tr" style="grid-template-columns:150px 1fr 200px 150px"><span>%s</span><span>%s</span>'
                      '<span>%s</span><span class="d">%s</span></div>' % (d.isoformat(), e(c), e(m), fcfa(mt))
                      for d, _r, c, m, _ref, mt in REMBOURSEMENTS if d >= DEBUT_MOIS))

TDB = (
    '<div class="vue" id="t10-tdb"><div class="t10-tdb"><div class="t10-defil" id="t10-defil" '
    'data-layout-allow-overflow data-layout-allow-occlusion>'
    '<div class="t10-top"><div class="t10-titre-tdb">POS Crédit — Recouvrement</div>'
    '<div class="t10-sous">Ardoises &amp; remboursements · suivi des dettes clients</div></div>'
    '<div class="t10-filtres">'
    '<div class="t10-frang"><span class="t10-flab">Période</span><span class="t10-chip">Aujourd\'hui</span>'
    '<span class="t10-chip">Cette semaine</span><span class="t10-chip actif">Ce mois</span><span class="t10-chip">Tout</span>'
    '<span class="t10-esp"></span><span class="t10-dt">%s<span class="ico">%s</span></span><span class="t10-fl2">→</span>'
    '<span class="t10-dt">%s<span class="ico">%s</span></span><span class="t10-chip actif">Appliquer</span></div>'
    '%s%s</div>'
    '%s<div class="t10-g4">%s</div>'
    '%s<div class="t10-g4">%s</div>'
    '%s<div class="t10-g2">%s%s</div>'
    '%s<div class="t10-g2">%s%s</div>'
    '%s<div class="t10-g2">%s%s</div>'
    '%s<div class="t10-card t10-card-top">%s</div>'
    '</div></div></div>'
    % (jj(DEBUT_MOIS), CALENDRIER, JOUR, CALENDRIER,
       chips('Origine', ['Toutes', 'Point de vente', 'Ventes']),
       chips('Caisse', ['Toutes les caisses', BAR, RESTO, BOUT], dots=[None, PALETTE[BAR], PALETTE[RESTO],
                                                                        PALETTE[BOUT]]),
       section('Encours & recouvrement'),
       kpi_('t10-k-enc', 'Encours total (dû)', fcfa(ENCOURS), flux(NOUVELLES - RECOUVRE), 'danger')
       + kpi_('t10-k-rec', 'Recouvré (période)', fcfa(RECOUVRE), '%d remboursements' % NB_REMB, 'success',
              delta(DELTA_REC, True))
       + kpi_('t10-k-new', 'Nouvelles ardoises (période)', fcfa(NOUVELLES), '%d ardoises ouvertes' % len(OUVERT_MOIS),
              'warning', delta(DELTA_NEW, False))
       + kpi_('t10-k-taux', 'Taux de recouvrement', pct(RECOUVRE * 100.0 / (ENCOURS + RECOUVRE)),
              'recouvré / (encours + recouvré)', 'primary'),
       section('Indicateurs de risque'),
       kpi_('t10-k-moy', 'Ardoise moyenne', fcfa(ENCOURS / DEBITEURS), '%d débiteurs actifs' % DEBITEURS)
       + kpi_('t10-k-anc', 'Plus ancienne dette', '%d j' % age(PLUS_VIEILLE[3]), PLUS_VIEILLE[1])
       + kpi_('t10-k-ret', 'En retard (+30j)', fcfa(RETARD), pct(RETARD * 100.0 / ENCOURS) + " de l'encours")
       + kpi_('t10-k-reg', 'Ardoises réglées (période)', '1', 'délai moyen %d j' % age(_A[3])),
       section('Âge de la dette & évolution'),
       carte_g("Balance âgée (aging) de l'encours", barres('t10-g-age', AGING, ['#3B6D11', '#854F0B', '#A32D2D',
                                                                                 '#5E1B1B'],
                                                           [t[0] for t in TRANCHES], 70000, 10000, h=160),
               "Plus la dette est ancienne, plus le risque d'impayé est élevé.", 't10-c-age'),
       carte_g('Nouvelles ardoises vs Recouvré (6 mois)',
               courbes('t10-g-evo', [(OUVERTES_MOIS, '#A32D2D'), (RECOUVRE_MOIS, '#3B6D11')], MOIS, 90000, 10000)
               + '<div class="t10-legc"><span><i class="r"></i>Nouvelles ardoises</span><span><i class="v"></i>'
                 'Recouvré</span></div>'),
       section('Répartition & rythme'),
       carte_g('Encours par origine', donut([(c, v, PALETTE[c]) for c, v in PAR_CAISSE]),
               "Où le crédit est accordé — toutes périodes (photo de l'encours)."),
       carte_g('Remboursements par jour (période)', barres('t10-g-jour', PAR_JOUR, ['#714B67'] * len(JOURS),
                                                            [j.strftime('%d/%m') for j in JOURS], 45000, 5000,
                                                            h=190)),
       section('Remboursements (période)'),
       carte_g('Répartition par moyen de paiement', donut([(m, v, COUL_MOYEN[m]) for m, v in PAR_MOYEN])),
       '<div class="t10-card"><div class="t10-ch-h"><h3>Derniers remboursements</h3><span class="t10-lk">Tout voir</span>'
       '</div>%s</div>' % DERNIERS,
       section('Top débiteurs', '<span class="t10-lk">Toutes les ardoises</span>'),
       TOP_HTML))

BUREAU = (fenetre_muk('t10-bo', 'POS Crédit', MENUS, [LISTE, FICHE, TDB], actif='Ardoises', societe=demo.SOCIETE,
                      initiale=NOM[0], avatar='#185FA5', apps=APPS_PROFIL['caisse'], app_active='POS Crédit',
                      calques=ASSISTANT)
          .replace('<span class="menu">Recouvrement</span>', '<span class="menu" id="t10-menu-rec">Recouvrement</span>', 1)
          .replace('<span class="menu actif">Ardoises</span>', '<span class="menu actif" id="t10-menu-ard">Ardoises</span>',
                   1))
NAV_BUREAU = navigateur(BUREAU, 'nav-bo').replace('class="navigateur"', 'class="navigateur masque"', 1)

ECRAN = NAV_POS + NAV_BUREAU

CSS = """
/* ---------------------------------------------------------------- caisse -- */
#t10-pos .pos-num { min-width: 70px; justify-content: center; }
#t10-paie .pos-mode .ico { width: 28px; height: 28px; color: #495057; }
#t10-paie .pos-mode .ico svg { width: 28px; height: 28px; }
#t10-paie .pos-cf em { font-style: normal; }
.t10-ico { width: 18px; height: 18px; display: inline-flex; color: #343A40; }
.t10-ico svg { width: 18px; height: 18px; }
#t10-cli { gap: 10px; }
.t10-cli-p { display: inline-grid; }
.t10-cli-p b { grid-area: 1 / 1; font-weight: 400; text-align: center; }
.t10-cli-p .t10-nomcli { font-weight: 500; color: #3F6A83; }
#t10-paie .pos-ardoise .ico svg { width: 20px; height: 20px; }
.pos-rv .v.t10-off { background: #A3BCCB; }
.t10-choix { position: absolute; left: 0; right: 0; top: 400px; text-align: center; font-size: 24px; color: var(--o-texte); }
.t10-zone { position: absolute; left: 150px; right: 150px; top: 330px; }
.pos-restant.t10-ok { color: #1A6E2E; border-color: #1A6E2E; }
.pos-restant.t10-du { background: #F8D7DA; border-color: #B02A37; color: #8E1F2A; }
.pos-restant.t10-du b { font-weight: 800; }
.t10-pl { background: #DCE6EC; box-shadow: inset 0 0 0 1px var(--muk-prim); color: var(--o-texte); }
.t10-pl .x { color: #B02A37; }
.toast.t10-toast { top: 76px; width: 520px; font-size: 20px; }
/* la fenêtre des clients */
.t10-dlg { top: 40px; width: 1240px; margin-left: -620px; }
.t10-dlg-h { display: flex; align-items: center; height: 84px; padding: 0 24px; border-bottom: 1px solid var(--o-filet); }
.t10-creer { height: 50px; font-size: 21px; padding: 0 22px; }
.entree.t10-q { margin: 0 0 0 auto; width: 480px; height: 52px; font-size: 21px; }
.t10-dlg-c { position: relative; height: 534px; padding: 0 24px; }
.t10-cl { display: grid; grid-template-columns: 280px 330px 1fr 60px; align-items: center; gap: 16px; min-height: 60px;
  padding: 0 12px; border-bottom: 1px solid #EEF0F2; font-size: 19px; color: var(--o-texte); }
.t10-cl b { font-weight: 700; }
.t10-cl-tete { min-height: 52px; font-weight: 600; border-bottom: 1px solid var(--o-filet); }
.t10-ct { display: flex; flex-direction: column; gap: 4px; font-size: 17px; color: var(--o-texte-2); }
.t10-ct span { display: flex; align-items: center; gap: 8px; }
.t10-ct i { width: 16px; height: 16px; display: inline-flex; color: var(--o-texte-2); }
.t10-ct svg { width: 16px; height: 16px; }
.t10-cl-m { width: 44px; height: 44px; border: 1px solid var(--o-filet); border-radius: 5px; background: #F8F9FA;
  display: flex; align-items: center; justify-content: center; font-size: 20px; color: var(--o-texte-2); }
.t10-plus { display: flex; justify-content: center; padding: 16px 0; }
.t10-plus .bt { height: 50px; font-size: 20px; }
.t10-dlg-p { height: 76px; display: flex; align-items: center; padding: 0 24px; border-top: 1px solid var(--o-filet); }
.t10-dlg-p .bt { height: 50px; font-size: 20px; }
/* le reçu */
.t10-recu { position: absolute; inset: 0; display: grid; grid-template-columns: 1fr 860px; background: #E9ECEF; }
.t10-actions { position: relative; background: #F8F9FA; border-right: 1px solid var(--o-filet); padding: 22px 120px; }
.t10-reussi { display: flex; flex-direction: column; align-items: center; gap: 6px; padding: 20px; border: 1px solid #1A6E2E;
  border-radius: 12px; background: #D1E7DD; color: #13532A; }
.t10-okico { width: 64px; height: 64px; color: #1A6E2E; }
.t10-okico svg { width: 64px; height: 64px; }
.t10-reussi b { font-size: 32px; font-weight: 800; }
.t10-mt { display: flex; align-items: center; gap: 12px; font-size: 26px; font-weight: 700; }
.t10-modif { font-size: 16px; font-weight: 600; background: #1A6E2E; color: #fff; border-radius: 5px; padding: 3px 9px; }
.t10-actions hr { border: 0; border-top: 1px solid var(--o-filet); margin: 22px 0; }
.t10-imprimer { height: 66px; border-radius: 6px; background: #E2E5E9; color: var(--o-texte); font-size: 21px; display: flex;
  align-items: center; justify-content: center; gap: 10px; }
.t10-imprimer .ico { width: 22px; height: 22px; display: inline-flex; }
.t10-imprimer .ico svg { width: 22px; height: 22px; }
.t10-mail { margin-top: 12px; display: flex; height: 66px; }
.t10-in { flex: 1; border: 1px solid var(--o-filet); border-right: 0; border-radius: 6px 0 0 6px; background: #fff; display: flex;
  align-items: center; padding: 0 18px; font-size: 20px; color: #6C757D; }
.t10-envoi { width: 130px; border-radius: 0 6px 6px 0; background: var(--muk-prim); color: #fff; display: flex; align-items: center;
  justify-content: center; }
.t10-envoi svg { width: 24px; height: 24px; }
.t10-nouv { position: absolute; left: 10px; right: 10px; bottom: 10px; height: 96px; border-radius: 6px; background: var(--muk-prim);
  color: #fff; font-size: 26px; display: flex; align-items: center; justify-content: center; }
.t10-recu-d { position: relative; overflow: hidden; display: flex; justify-content: center; padding-top: 24px; }
.t10-ticket { width: 470px; height: 690px; overflow: hidden; background: #fff; border: 1px solid var(--o-filet); border-radius: 6px;
  padding: 18px 22px; font-size: 17px; color: #212529; }
.t10-ent { text-align: center; line-height: 1.45; }
.t10-ent > div:first-child { font-weight: 700; }
.t10-suivi { font-size: 36px; font-weight: 500; margin-top: 4px; }
.t10-tirets { text-align: center; color: #495057; letter-spacing: 1px; overflow: hidden; white-space: nowrap; margin: 4px 0; }
.t10-rl { padding: 6px 0; font-size: 16px; }
.t10-rl .a b { font-weight: 700; }
.t10-rm { display: flex; justify-content: space-between; line-height: 1.6; }
.t10-tx .t10-rm:first-child span:first-child { font-weight: 700; }
.t10-rm.t10-total { font-size: 21px; font-weight: 700; margin-bottom: 4px; }
.t10-tk-paie { padding: 4px 6px; margin: 0 -6px; }
.t10-gen { margin-top: 18px; text-align: center; color: #495057; }
/* ------------------------------------------------------------ POS Crédit -- */
#t10-bo .cp.t10-cp { gap: 14px; }
.t10-cp .titre { font-size: 24px; }
.t10-engr { width: 18px; height: 18px; display: inline-flex; color: #343A40; }
.t10-engr svg { width: 18px; height: 18px; }
.t10-cp .recherche { margin-left: auto; width: 620px; }
.t10-cp .pager { margin-left: auto; }
.t10-fl { display: flex; gap: 2px; }
.t10-fl i { width: 38px; height: 38px; display: flex; align-items: center; justify-content: center; background: #E9ECEF;
  color: #343A40; font-style: normal; font-size: 24px; border-radius: 4px; }
.t10-liste .tete { height: 50px; font-size: 17px; column-gap: 12px; padding: 0 18px 0 6px; }
.t10-liste .ligne { height: 47px; font-size: 17px; column-gap: 12px; padding: 0 18px 0 6px; }
.t10-liste .total { height: 50px; font-size: 17px; column-gap: 12px; padding: 0 18px 0 6px; }
.t10-liste .cb { margin-left: 8px; }
.t10-liste .puce { height: 27px; font-size: 15px; padding: 0 10px; }
.t10-liste .ligne.survol { background: #E3ECF2; }
.t10-ancre { height: 1px; width: 420px; margin-left: auto; }
/* les réactions se posent là où elles ne cachent rien de ce que l'étape montre */
#t10-r-regle { bottom: 386px; }
#t10-r-relance { bottom: auto; top: 330px; right: auto; left: 560px; }
/* la fiche */
.t10-stat { margin-left: 250px; display: flex; align-items: center; gap: 10px; height: 54px; padding: 0 16px; border: 1px solid var(--o-filet);
  background: #fff; }
.t10-stat .sic { width: 30px; height: 30px; display: inline-flex; color: var(--o-texte-2); }
.t10-stat .st-t { display: flex; flex-direction: column; line-height: 1.15; font-size: 17px; color: var(--o-texte-2); }
.t10-stat .st-t b { font-weight: 600; color: #3F6A83; }
#t10-fiche .feuille { padding: 18px 30px 30px; min-height: 0; }
#t10-sb .st-et { color: #5C636A; }
#t10-sb .st-et.actif { color: var(--o-texte); }
.t10-titre { font-size: 34px; margin-bottom: 12px; }
.t10-cols { gap: 50px; }
.t10-ch { grid-template-columns: 238px 1fr; min-height: 35px; font-size: 18px; }
.t10-ch .v { padding: 2px 4px; }
.t10-ch .v.t10-saisie { border-bottom: 1px solid #CED4DA; }
.t10-ch .v.t10-lien, .t10-lien { color: #3F6A83; }
.t10-aide { color: #3F6A83; font-size: 12px; margin-left: 3px; font-weight: 700; }
.puce.t10-pg { height: 26px; font-size: 15px; }
.t10-onglets { margin-top: 10px; }
.t10-onglets .onglet { padding: 9px 18px; font-size: 18px; }
.t10-table { margin: 0 -30px; }
.t10-table .t-tete, .t10-table .t-ligne, .t10-table .t-total { padding: 0 30px; }
.t10-table .t-tete { height: 44px; font-size: 17px; }
.t10-table .t-ligne { height: 46px; font-size: 17px; }
.t10-table .t-ajout { height: 40px; padding: 0 30px; font-size: 17px; }
.t10-table .t-total { height: 44px; font-size: 17px; }
.t10-table .puce { height: 26px; font-size: 14px; }
.t10-xa { width: 16px; height: 16px; display: inline-flex; color: var(--o-texte-2); }
.t10-xa svg { width: 16px; height: 16px; }
.pile > .t10-table:nth-child(2) { position: absolute; left: 0; right: 0; top: 0; }
/* l'assistant */
.t10-as { top: 96px; width: 1180px; margin-left: -590px; }
.t10-mch { min-height: 54px; }
.t10-mch .l { font-weight: 400 !important; color: var(--o-texte-2) !important; }
.t10-mch .l.t10-gras { font-weight: 600 !important; color: var(--o-texte) !important; }
.t10-mon { display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #CED4DA; padding: 6px 4px; }
.t10-mon small { font-size: 19px; color: var(--o-texte); }
.m-ch .v .entree.t10-sel::after { content: '▾'; position: absolute; right: 6px; top: 50%; transform: translateY(-50%);
  font-size: 15px; color: var(--o-texte-2); }
.t10-date { display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #CED4DA; padding: 6px 4px; }
.t10-date .ico { width: 18px; height: 18px; display: inline-flex; color: var(--o-texte-2); }
.t10-date .ico svg { width: 18px; height: 18px; }
.m-ch .v .entree.t10-sel, .m-ch .v .entree.t10-ref { font-size: 19px; }
.t10-note { margin-top: 16px; padding: 8px 4px; border-bottom: 1px solid #CED4DA; color: #6C757D; font-size: 19px; }
/* le tableau de bord */
.t10-tdb { position: absolute; inset: 0; background: #E8E6E0; overflow: hidden; }
.t10-defil { position: absolute; left: 0; right: 0; top: 0; padding: 14px 18px 14px; }
.t10-top { height: 76px; background: #fff; border-radius: 12px; padding: 12px 20px; }
.t10-titre-tdb { font-size: 25px; font-weight: 700; color: #714B67; }
.t10-sous { margin-top: 3px; font-size: 16px; color: #6E6D68; }
.t10-filtres { margin-top: 10px; height: 168px; background: #fff; border-radius: 12px; padding: 4px 16px; }
.t10-frang { display: flex; align-items: center; gap: 8px; height: 52px; }
.t10-frang + .t10-frang { border-top: 1px dashed #E3E1DC; }
.t10-flab { width: 110px; font-size: 14px; font-weight: 600; letter-spacing: .06em; text-transform: uppercase; color: #6E6D68; }
.t10-chip { height: 38px; padding: 0 14px; border: 1px solid #E3E1DC; border-radius: 8px; display: inline-flex; align-items: center;
  gap: 8px; font-size: 16px; color: #45443F; white-space: nowrap; }
.t10-chip.actif { background: #714B67; border-color: #714B67; color: #fff; }
.t10-dot { width: 11px; height: 11px; border-radius: 50%; display: inline-block; }
.t10-esp { flex: 1; }
.t10-dt { height: 38px; width: 170px; border: 1px solid #E3E1DC; border-radius: 8px; display: inline-flex; align-items: center;
  justify-content: space-between; padding: 0 10px; font-size: 16px; color: #212529; }
.t10-dt .ico { width: 16px; height: 16px; display: inline-flex; }
.t10-dt .ico svg { width: 16px; height: 16px; }
.t10-fl2 { color: #6E6D68; }
.t10-sect { height: 40px; display: flex; align-items: center; justify-content: space-between; padding: 6px 2px 0;
  font-size: 15px; font-weight: 700; letter-spacing: .07em; text-transform: uppercase; color: #55544F; }
.t10-lk { font-size: 16px; font-weight: 500; letter-spacing: 0; text-transform: none; color: #3F6A83; }
.t10-g4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
.t10-g2 { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }
.t10-kpi { height: 104px; background: #fff; border-radius: 12px; padding: 14px 18px; }
.t10-kpi.mega { height: 124px; border-left: 5px solid transparent; }
.t10-kpi.acc-danger { border-left-color: #A32D2D; }
.t10-kpi.acc-success { border-left-color: #3B6D11; }
.t10-kpi.acc-warning { border-left-color: #854F0B; }
.t10-kpi.acc-primary { border-left-color: #714B67; }
.t10-kl { font-size: 14px; font-weight: 600; letter-spacing: .06em; text-transform: uppercase; color: #5F5E5A; white-space: nowrap; }
.t10-kv { margin-top: 6px; font-size: 30px; font-weight: 700; color: #2B2A27; white-space: nowrap; font-variant-numeric: tabular-nums; }
.t10-kd { margin-top: 2px; font-size: 15px; font-weight: 700; }
.t10-kd.haut { color: #1D7A33; }
.t10-kd.bas { color: #B4232C; }
.t10-ks { margin-top: 2px; font-size: 15px; color: #6E6D68; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.t10-card { height: 290px; background: #fff; border-radius: 12px; padding: 14px 20px; position: relative; overflow: hidden; }
.t10-card h3 { font-size: 19px; font-weight: 500; color: #2B2A27; }
.t10-chart { margin-top: 8px; }
.t10-svg { display: block; overflow: visible; }
.t10-tick { font-size: 13px; fill: #6E6D68; font-family: var(--sans); }
.t10-mini { position: absolute; left: 20px; bottom: 12px; font-size: 15px; color: #6E6D68; }
.t10-legc { display: flex; justify-content: center; gap: 18px; margin-top: 4px; font-size: 14px; color: #45443F; }
.t10-legc span { display: flex; align-items: center; gap: 6px; }
.t10-legc i { width: 34px; height: 12px; border: 3px solid; display: inline-block; }
.t10-legc i.r { border-color: #A32D2D; background: rgba(163,45,45,.13); }
.t10-legc i.v { border-color: #3B6D11; background: rgba(59,109,17,.13); }
.t10-donut { display: flex; align-items: center; gap: 30px; margin: 4px 0 0 120px; }
.t10-legs { display: flex; flex-direction: column; gap: 10px; }
.t10-leg { display: flex; align-items: center; gap: 10px; font-size: 16px; color: #45443F; }
.t10-leg i { width: 24px; height: 14px; display: inline-block; }
.t10-ch-h { display: flex; justify-content: space-between; align-items: center; }
.t10-tab { margin-top: 10px; font-size: 16px; color: #2B2A27; }
.t10-th, .t10-tr { display: grid; align-items: center; column-gap: 14px; padding: 0 8px; }
.t10-th { height: 40px; border-bottom: 2px solid #DEE2E6; font-size: 14px; font-weight: 700; letter-spacing: .05em; text-transform: uppercase;
  color: #45443F; }
.t10-tr { height: 44px; border-bottom: 1px solid #EEF0F2; }
.t10-tr b { font-weight: 700; }
.t10-gris { color: #6C757D; }
.t10-barc { position: relative; text-align: right; height: 32px; display: flex; align-items: center; justify-content: flex-end; }
.t10-barc i { position: absolute; left: 0; top: 10%; height: 80%; background: rgba(113,75,103,.14); border-radius: 4px; }
.t10-barc b { position: relative; }
.t10-tr .puce { height: 26px; font-size: 14px; }
.t10-det { display: inline-flex; height: 30px; align-items: center; padding: 0 12px; border: 1px solid #6C757D; border-radius: 5px;
  font-size: 15px; color: #495057; }
.t10-card-top { height: 440px; padding-top: 4px; }
.t10-card-top .t10-tab { margin-top: 4px; }
"""

TUTORIEL = {
    'slug': 't10-ardoises',
    'profil': 't10_ardoises',
    'numero': 10,
    'titre': "Fini le cahier d'ardoise : le crédit client sous contrôle",
    'fonction': 'Ardoises & recouvrement',
    'personnage': (NOM, ROLE),
    'accroche': {
        'kicker': 'Le crédit au bar',
        'question': 'Qui vous doit *combien,* et depuis quand ?',
        'douleurs': [('cahier', "L'ardoise tenue sur un cahier"),
                     ('interrogation', 'Des montants oubliés'),
                     ('calculatrice', 'Les remboursements partiels mal notés'),
                     ('sablier', 'Des dettes qui vieillissent sans relance'),
                     ('telephone', 'Remboursements MoMo et Orange Money notés nulle part'),
                     ('pieces', 'Combien récupérer ? Personne ne sait')],
        'voix': "Qui vous doit combien, et depuis quand ? Sur un cahier d'ardoise, les dettes vieillissent sans "
                "relance, et la trésorerie part en fumée.",
    },
    'revelation': {
        'promesse': "Au bar, un bouton : « Mettre sur ardoise ». Chaque dette a un nom, un montant et un âge ; chaque "
                    "remboursement fait baisser le reste dû, jusqu'à « Réglée ».",
        'voix': "Avec Aïte haousse, chaque ardoise a un nom, un montant, et un âge.",
    },
    'temps': ['Au bar', 'Suivre', 'Encaisser', 'Piloter'],
    'app': 't10-pos',
    'ecran': ECRAN,
    'css': CSS,
    'vues_initiales': {'pos': 't10-vente', 'odoo': 't10-liste'},
    'bulles': {
        'b-part': 'Seule la part mise sur ardoise devient une dette.',
        'b-sev': 'Récente, En retard dès 30 jours, Critique dès 60 jours.',
        'b-pre': 'Le reste dû est proposé ; un montant trop élevé est plafonné.',
        'b-retard': 'Les ardoises de 30 jours et plus, et leur part dans l\'encours.',
        'b-top': 'Un clic sur un débiteur ouvre ses ardoises ouvertes.',
    },
    'reactions': {
        't10-r-regle': 'Le reste dû se calcule tout seul.',
        't10-r-relance': 'Je sais qui relancer en premier.',
    },
    'etapes': [
        {'temps': 0, 'titre': 'Au bar : une partie comptant',
         'texte': 'Cédric Ngassa règle 5 000 FCFA en espèces : il reste 7 500 FCFA à payer.',
         'voix': "Au bar de la terrasse, Cédric Ngassa a consommé pour douze mille cinq cents francs. Il en règle cinq "
                 "mille en espèces : Hervé les encaisse, il reste sept mille cinq cents à payer.",
         'gestes': [pause(0.3), anneau('#t10-vente-ticket', d=1.1), clic('#t10-vente-payer', d=0.6),
                    vue('t10-paie', 'pos'), pause(0.3), clic('#t10-m-esp', d=0.6), cacher('#t10-msg', d=0.15),
                    montrer('#t10-st-ok', d=0.25, y=0, avec=True), montrer('#t10-pl-esp', d=0.25, y=0, avec=True),
                    classe('#t10-valider', retirer=['t10-off'], avec=True), pause(0.3),
                    clic('#t10-k5', d=0.5), texte('#t10-pl-esp-mt', '5 FCFA'),
                    classe('#t10-valider', ajouter=['t10-off'], avec=True),
                    cacher('#t10-st-ok', d=0.1, avec=True), montrer('#t10-st-du', d=0.15, y=0, avec=True),
                    clic('#t10-k0', d=0.25), texte('#t10-pl-esp-mt', '50 FCFA'), texte('#t10-st-du-v', '12 450 FCFA', avec=True),
                    clic('#t10-k0', d=0.15), texte('#t10-pl-esp-mt', '500 FCFA'), texte('#t10-st-du-v', '12 000 FCFA', avec=True),
                    clic('#t10-k0', d=0.15), texte('#t10-pl-esp-mt', COMPTANT), texte('#t10-st-du-v', A_CREDIT, avec=True),
                    anneau('#t10-st-du', d=1.4)]},
        {'temps': 0, 'titre': 'Mettre sur ardoise',
         'texte': "Pas de client, pas d'ardoise : la caisse ouvre la liste des clients, un second appui valide la vente.",
         'voix': "Le reste part sur l'ardoise. Mais sans client, pas d'ardoise : la caisse le signale, et ouvre la "
                 "liste des clients. Hervé choisit Cédric, touche à nouveau Mettre sur ardoise, et la vente est validée. "
                 "Sur le ticket, les deux paiements : cinq mille en espèces, sept mille cinq cents sur l'ardoise.",
         'gestes': [clic('#t10-ard', d=0.6), notifier('t10-toast-cli', duree=1.7), pause(0.3), ouvrir('t10-dlg'),
                    pause(0.9), saisir('t10-q', 'Ngassa', d=0.6), cacher('#t10-tous', d=0.15),
                    montrer('#t10-trouves', d=0.25, y=0, avec=True), clic('#t10-c-ngassa', fx=0.2, d=0.5),
                    fermer('t10-dlg'), cacher('#t10-cli-0', d=0.15), montrer('#t10-cli-1', d=0.25, y=0, avec=True),
                    pause(0.3), clic('#t10-ard', d=0.5), vue('t10-recu', 'pos'), pause(0.4),
                    zoom('#t10-tk-paie', s=2.0, d=0.7, fx=0.8), bulle('b-part', '#t10-tk-paie', cote='gauche', d=2.6),
                    anneau('#t10-tk-paie', d=1.6), pause(1.0), dezoom(d=0.5)]},
        {'temps': 1, 'titre': "L'ardoise est déjà là",
         'texte': 'ARD/0043, en tête de liste, avec sa caisse : 7 500 FCFA dus, pas un de plus.',
         'voix': "Côté bureau, dans le suivi des ardoises, elle est déjà là, en tête de liste, avec sa caisse d'origine : "
                 "sept mille cinq cents francs dus, pas un de plus. Les couleurs suivent l'âge de la dette.",
         'gestes': [montrer('#nav-bo', d=0.45, y=0), curseur('#t10-r0', fx=0.06, d=0.6, avec=True), pause(0.2),
                    zoom('#t10-r0', s=1.45, d=0.7, fx=0.42),
                    anneau('#t10-r0', d=1.6), pause(0.9), dezoom(d=0.5), anneau('#t10-r4-sev', d=0.9),
                    anneau('#t10-r7-sev', d=0.9), bulle('b-sev', '#t10-ancre-sev', cote='bas', d=2.8), pause(1.4),
                    anneau('#t10-tot', d=1.2)]},
        {'temps': 2, 'titre': 'Encaisser un remboursement',
         'texte': 'Reste dû proposé, moyen de paiement, référence de la transaction : Encaisser.',
         'voix': "Armand Mvogo passe régler son ardoise, ouverte il y a cinquante-sept jours. Enregistrer un "
                 "remboursement : le reste dû est déjà proposé. Il paie en Orange Moni : Hervé choisit le moyen, saisit "
                 "la référence, et encaisse.",
         'gestes': [classe('#t10-r6', ajouter=['survol']), clic('#t10-r6', fx=0.25, d=0.6), vue('t10-fiche'),
                    pause(0.3), anneau('#t10-f-reste', d=1.0), clic('#t10-b-remb', d=0.5), ouvrir('t10-as'),
                    bulle('b-pre', '#t10-as-mt', cote='haut', d=2.4), anneau('#t10-as-mt', d=1.2),
                    clic('#t10-as-moy', d=0.5), choisir('t10-as-moy', 'Orange Money'),
                    clic('#t10-as-ref', d=0.4), saisir('t10-as-ref', REF_OM, d=1.0), clic('#t10-as-ok', d=0.5),
                    # la fiche se recharge dès la fermeture de l'assistant
                    fermer('t10-as'), texte('#t10-f-deja', fcfa(_A[4])), texte('#t10-f-reste', '0 FCFA', avec=True),
                    texte('#t10-f-sev', 'Réglée', avec=True), classe('#t10-sb-0', retirer=['actif'], avec=True),
                    classe('#t10-sb-1', ajouter=['actif'], avec=True), cacher('#t10-fiche-ga', d=0.2, avec=True),
                    texte('#t10-stat-v', '2', avec=True),
                    classe('#t10-l-cli', retirer=['gras'], avec=True), classe('#t10-l-date', retirer=['gras'], avec=True),
                    classe('#t10-v-cli', retirer=['t10-saisie'], avec=True),
                    classe('#t10-v-date', retirer=['t10-saisie'], avec=True),
                    cacher('#t10-ta', d=0.2, avec=True), montrer('#t10-tb', d=0.3, y=0, avec=True),
                    pause(0.4)]},
        {'temps': 2, 'titre': 'Réglée, toute seule',
         'texte': 'Reste dû à zéro, ardoise Réglée ; le remboursement est inscrit avec son moyen et son encaisseur.',
         'voix': "Le reste dû tombe à zéro, et l'ardoise passe Réglée, toute seule. Le remboursement s'inscrit sur la "
                 "fiche : le moyen, la référence, et qui l'a encaissé.",
         'gestes': [zoom('#t10-g-mt', s=1.5, d=0.7, fx=0.3), anneau('#t10-f-reste', d=1.2),
                    anneau('#t10-sb', d=1.0), dezoom(d=0.5), anneau('#t10-tb-0', d=1.6),
                    reaction('t10-r-regle', d=2.6), pause(1.6)]},
        {'temps': 3, 'titre': 'Le tableau de bord Recouvrement',
         'texte': "L'encours, le recouvré du mois, le taux, la part en retard, et la balance âgée.",
         'voix': "Le tableau de bord Recouvrement fait les comptes : l'encours, ce qui est rentré ce mois, le taux de "
                 "recouvrement, et la part en retard. La balance âgée montre où dort le risque.",
         'gestes': [clic('#t10-menu-rec', d=0.6), classe('#t10-menu-ard', retirer=['actif']),
                    classe('#t10-menu-rec', ajouter=['actif'], avec=True), vue('t10-tdb'),
                    compter('#t10-k-enc-v', 0, ENCOURS, d=1.0, apres=' FCFA', avec=True),
                    compter('#t10-k-rec-v', 0, RECOUVRE, d=1.0, apres=' FCFA', avec=True),
                    compter('#t10-k-new-v', 0, NOUVELLES, d=1.0, apres=' FCFA', avec=True),
                    anneau('#t10-k-taux', d=1.0), anneau('#t10-k-ret', d=1.2),
                    bulle('b-retard', '#t10-k-ret', cote='gauche', d=2.6),
                    defiler('#t10-defil', -200, d=0.9, decale=1.2),
                    animer('#t10-g-age', {'scaleY': 0, 'transformOrigin': '50% 100%'},
                           {'scaleY': 1, 'immediateRender': True}, d=0.8),
                    anneau('#t10-c-age', d=1.6)]},
        {'temps': 3, 'titre': 'Qui relancer en premier',
         'texte': 'Les débiteurs par encours, avec l\'âge de leur dette, leur dernier paiement et leur statut.',
         'voix': "Plus bas, les débiteurs, du plus gros encours au plus petit, avec l'âge de leur dette et leur "
                 "dernier paiement ; le statut dit qui est en retard. Hervé sait qui relancer en premier.",
         'gestes': [defiler('#t10-defil', -1312, d=1.1), pause(0.3), anneau('#t10-d1', d=1.2),
                    anneau('#t10-d1 .puce', d=0.9), anneau('#t10-d2', d=1.1), anneau('#t10-d2 .puce', d=0.9),
                    bulle('b-top', '#t10-top', cote='haut', d=2.6), pause(1.0),
                    reaction('t10-r-relance', d=2.6), pause(1.4)]},
    ],
    'resultats': {
        'titre': 'Le crédit client, enfin sous contrôle',
        'cartes': [
            {'valeur': '1', 'compter': 1, 'unite': 'bouton', 'icone': 'cahier',
             'texte': "à la caisse : « Mettre sur ardoise », client exigé, vente validée"},
            {'valeur': '5', 'compter': 5, 'unite': 'moyens de remboursement', 'icone': 'pieces',
             'texte': 'MTN Mobile Money, Orange Money, espèces, carte bancaire, virement ou autre'},
            {'valeur': '8', 'compter': 8, 'unite': 'indicateurs', 'icone': 'graphe',
             'texte': 'sur le tableau de bord Recouvrement, avec la balance âgée en 4 tranches'},
        ],
        'voix': "Un bouton au bar, cinq moyens de remboursement, huit indicateurs : le crédit client est sous contrôle.",
    },
    'cta': {
        'appel': 'Demandez votre démonstration',
        'suivant': 'La fidélité',
        'voix': "Aïte haousse, par Aïte Consulting. Demandez votre démonstration, et retrouvez tous nos tutoriels sur "
                "notre chaîne.",
    },
    'vignette': {'etape': 5, 'apres': 0.3},
}
