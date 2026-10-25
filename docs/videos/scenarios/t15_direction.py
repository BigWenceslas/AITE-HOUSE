# -*- coding: utf-8 -*-
"""Tutoriel 15 — Cockpit Direction : l'affaire lue d'un coup d'œil.

La directrice (Danielle Eyenga, demo.POSTES['direction']) ouvre l'application
Direction : la santé de l'affaire, l'essentiel par pôle, les filtres (le soir
du week-end), un clic sur une carte de pôle qui ouvre son onglet (Crédit
clients), la liste « À traiter », les tendances sur six mois (CA vs achats,
balance âgée en miroir), la rangée Hébergement comparée à l'an dernier, puis
un clic sur une carte de l'hôtel qui ouvre « Direction — Activité par pôle »
(l'ancien tableau de bord exécutif : réservations récentes, rythme du mois).

Profil rejoué : comptes demo.direction de la base MuK (Point de Vente :
Administrateur, Gestion hôtelière : Responsable…). Le menu racine
« Direction » est réservé à point_of_sale.group_pos_manager
(addons/aite_direction_dashboard/views/direction_views.xml:8-12) ; il n'a pas
de sous-menu : la barre du haut ne porte que le nom de l'application
(ref_muk/060-direction.png, 330-direction-accueil.png). Applications de la
barre MuK : ecrans.APPS_PROFIL['direction'] (relevées sur 330-direction-
accueil.png). Un clic sur une carte Hébergement ouvre l'activité par pôle
(action client « Direction — Activité par pôle », aite_exec_dashboard/views/
exec_dashboard_actions.xml:3-6) dans la même application « Direction », sans
fil d'Ariane (vérifié sur la base MuK : barre « Direction », aucun
.breadcrumb). Le même écran s'ouvre par Hôtel → Activité par pôle
(exec_menus.xml:7-14).

Sources des libellés (relevés mot pour mot, livraison 4 ; diff ae3aab6..HEAD) :

- Cockpit, gabarit addons/aite_direction_dashboard/static/src/xml/
  direction_dashboard.xml : carte (badge « période » / « photo », « ? »
  aria-label « Explication », écart dans la ligne de la valeur) :4-26 ;
  HBar :28-40 ; graphique et légende des tendances :42-79 ; miroir, « Vos
  clients vous doivent », « Vous devez aux fournisseurs », légende :81-107 ;
  titre « Direction — Vue consolidée » (inchangé) et « POS · Crédit
  clients · Stock · Achats — <société> » :136-142 ; PÉRIODE, Du, au,
  Appliquer :145-162 ; CAISSE, « Toutes les caisses », note « caisse, heure
  et jours filtrent les données de vente » :163-180 ; HEURE :181-189 ; JOUR,
  « multi-sélection — aucun = tous » :190-199 ; VUE et pastilles des
  onglets :201-213 ; SANTÉ DE L'AFFAIRE (« CA encaissé » et son écart « vs
  période précédente », « HT · 128 tickets · POS payés / facturés »)
  :222-243 ; « L'ESSENTIEL PAR PÔLE — cliquer une carte ouvre l'onglet »
  (« 5 débiteurs · 101 500 en retard (+30 j) », « 180 000 échues · 420 000
  sous 7 j », « 2 références en alerte · coulage 0,6 % ») :244-272 ;
  « HÉBERGEMENT — écarts vs même période N-1 ; cliquer une carte ouvre
  « Direction — Activité par pôle » », « Prix moyen par nuit (ADR) »,
  « Revenu par chambre disponible (RevPAR) », écarts sans libellé :273-307 ;
  TENDANCES, « CA vs Achats — 6 mois, et encours d'ardoises », « POS ·
  Achats · Crédit », « Balance âgée en miroir », « Crédit · Achats »
  :308-324 ; pied de page « Sources : Analyse AITE · POS Crédit · Stock &
  Inventaire · Achats & Fournisseurs. Les cartes « période » suivent les
  filtres ; les cartes « photo » sont des instantanés. Caisse, tranche
  horaire et jours s'appliquent aux données de vente. » (carte blanche sous
  le contenu de chaque onglet, scss:247-250) :843-849 ; onglet Crédit
  clients (ORIGINE, Toutes, Point de vente, Ventes
  / factures, CRÉDIT CLIENTS — ARDOISES, « Encours total » / « 5 débiteurs
  actifs », « En retard (+30 j) », « Plus ancienne dette », « Délai moyen de
  remboursement » / « 2 ardoises réglées », « Recouvré » et « Nouvelles
  ardoises » avec « vs période précédente » (une hausse des nouvelles
  ardoises en rouge, upIsBad), « Flux net », « Taux de recouvrement »,
  « Balance âgée clients » / « POS Crédit » / « 2 ardoises », « Encours —
  6 mois (fin de mois) », « Top débiteurs », pastille rouge au-delà de
  60 j, « Derniers remboursements », « Ouvrir POS Crédit ↗ ») :419-547 ;
  onglet À traiter (« À TRAITER — LA LISTE DU GÉRANT (11 actions) »,
  URGENT / À SURVEILLER, « Chaque ligne ouvre le tableau de bord spécialisé
  correspondant. ») :801-841. Couleurs et tailles : static/src/scss/
  direction_dashboard.scss (fond #e8e6e0, puces violettes, liserés, badges,
  « ? », écart en bloc insécable qui passe sous le montant :155-162).
- static/src/js/direction_dashboard.js : HEURE, JOUR, PÉRIODE, onglets
  :23-46 ; « Ce mois » en dates locales, du 1er au jour même (localIsoDate,
  rangeFor) :57-86 ; formats :88-154 — fmtMoney (toLocaleString fr-FR,
  espace fine U+202F, trait d'union devant un négatif), fmtPct « 56,0 % »,
  fmtDelta « ▲ +9,4 % » / « ▼ 63,0 % » / « ■ 0,0 % », deltaClass (upIsBad),
  fmtDays « 18,0 j », fmtAge « 104 j », fmtDate jj/mm/aaaa, fmtCount
  (accords) ; agingKey :165-174 ; KpiCard (deltaLabel) :193-199 ;
  graphique des tendances (maxBar commun au CA et aux achats) :213-264 ;
  miroir (tranches et couleurs) :266-294 ; position nette (phrase servie
  par le serveur) :394-403 ; sous-titres « rythme du mois (pace) » et
  « réservations récentes (pickup) » :405-419 ; ouverture de l'activité par
  pôle :424-429 ; balance âgée clients, couleur lue sur la clé :477-491 ;
  légende de l'encours :504-511 ; « Flux net » :512-519 ; pastilles des
  onglets :608-617 ; heure et jours ne rechargent que la vue d'ensemble et
  les ventes :689-702.
- models/direction_dashboard.py : orchestrateur des quatre moteurs :5-11 ;
  tranches d'âge (borne basse incluse) et seuil de relance (30 j) :40-50 ;
  mois « mai » … « oct. » :52-55, :137-143 ; cash à risque :88-91 ;
  position nette et sa phrase :93-122 ; phrase du flux net :124-135 ;
  factures ouvertes du moteur Achats traduites (residual → amount, due →
  planned) :160-179 ; échéancier et miroir fournisseurs :192-242 ;
  « à payer bientôt » au réglage des Achats (7 j) :244-257 ; encours à
  rebours :259-277 ; liste d'actions :328-450 (« Relancer %s », « %d j »,
  « Régulariser 1 facture échue », « échu », « Payer %s » et l'échéance
  « 17/10/2026 », « Commander %s », « perd / jour », « Lancer la commande
  suggérée (2 références) », « sous seuil », « Écarts d'inventaire
  négatifs », « contrôler », « Renégocier %s », « +8,3 % · <fournisseur> ») ;
  tendances alignées sur AAAA-MM :488-520 ; tuile Hébergement :546-583 ;
  get_overview :585-649 ; get_credit_tab :675-696 ; get_actions :740-771.
- Crédit : addons/aite_pos_credit/models/pos_credit.py:27-28 (30 et 60
  jours) ; pos_credit_dashboard.py get_kpis :129-246 (encours, retard,
  plus ancienne dette, flux net « nouveaux − recouvré », période précédente
  de même durée :202-206), get_aging :255-289 (tranches « 0–30 j »,
  « 30–60 j », « 60–90 j », « +90 j », clé et nombre d'ardoises),
  get_top_debtors :408 (tri par encours), get_evolution :490-540 (mois
  « mai » … « oct. »), get_recent_payments :541 ; moyens de paiement
  pos_credit_payment.py (« MTN Mobile Money », « Orange Money »,
  « Espèces »).
- Activité par pôle, gabarit addons/aite_exec_dashboard/static/src/xml/
  dashboard.xml:24-136 (« Direction — Activité par pôle » :29,
  « Hébergement · Restauration & boutique · Prestations » :30, Période, Du,
  au :34-49, quatre cartes :57-74 — « Du 01/10/2026 au 14/10/2026 »,
  « Nuitées HT, nuit par nuit · occupation … · prix moyen … / nuit »,
  « HT · 128 tickets · panier … », « 46 prestations réalisées » —,
  « Hébergement — indicateurs de performance », « écarts vs même période
  N-1 » :76-78, cinq cartes et leurs « ? » (« Prix moyen par nuit (ADR) »,
  « Revenu par chambre disponible (RevPAR) », « Réservations récentes
  (pickup) », « Rythme du mois (pace) » et « vs même date N-1 ») :79-105,
  « Points fidélité émis », « Tous services confondus » :107-111,
  « Répartition & évolution », « Mix du chiffre d'affaires par pôle »,
  « Évolution mensuelle — 6 mois » :113-132) ; static/src/js/components/
  kpi_card.js:12-39 (« vs N-1 » par défaut, écart sous la valeur, gris s'il
  est nul) ; static/src/js/views/exec_dashboard_view.js : periodText :136,
  mixLine « <montant> · <part> » :141, pickupSub et paceSub :155-171,
  graduations kTick « 20 M » :173-183, graphique Chart.js sans pas imposé
  :238-268 (dans une boîte de 280 px, scss:435, Chart.js 4.4.1 d'Odoo 18
  trace au plus 11 graduations : pas « rond » de 2 M pour 18,5 M, d'où 0,
  2 M … 20 M) ; static/src/js/services/utils.js :
  fmtMoney (espace fine) :5, fmtPct « 63,9 % » :16, fmtCount :29, fmtDelta
  :44, « Ce mois / Ce trimestre / Cette année » :53-57, période locale
  :64-91, mois « oct. 26 » :93-99 ; static/src/scss/exec_dashboard.scss
  (titre violet, liserés dont le teal des Prestations :201-203) ;
  models/exec_dashboard.py : libellés et couleurs des pôles :10-20, phrases
  d'explication KPI_HINTS :25-42, parts arrondies à une décimale et triées
  :74-92, get_kpis :236-295, get_evolution (mois entiers) :297-321.
- Hébergement : addons/aite_hotel_management/models/hotel_dashboard.py
  (chambres vendables × jours de la période :303-380, pickup et pace
  :183-239).
- Symbole « FCFA » de la devise XAF : odoo18/odoo/addons/base/data/
  res_currency_data.xml:476-483.

Sources des affirmations : douleurs — tests_uat/scenarios.py:323-353 et
docs/GUIDE_RECETTE_UAT.md:297-378 (la direction ouvre les tableaux de bord
un par un), docs/guides/AITE_HOUSE_plaquette_commerciale.pdf p. 10 (le
crédit « au lieu de le laisser dormir dans un cahier »),
direction_dashboard.xml:104 (« du cash qui s'évapore avec l'âge »),
tests/vague1/scenario_kpi.py:6-8 (le gérant « ne connaît pas le vocabulaire
hôtelier »), docs/etude_comparative/build_etude.py:167-168 et
benchmark_pms.md:161 (RevPAR / pace / pickup, standard chez 10 leaders sur
10, « à ajouter » avant F06) ; question — docs/guides/
AITE_Guide_Tableau_de_bord_Direction.pdf p. 1 (« comment va l'affaire ? »
— guide de l'activité par pôle, aujourd'hui Hôtel → Activité par pôle,
montrée à l'étape 7 ; sa promesse des « trente secondes » n'est pas
reprise : le titre dit « d'un coup d'œil », une seule page,
direction_dashboard.js:39-46) ; kicker — plaquette p. 16 (« Le pilotage du
gérant ») ; « qui relancer en premier » — plaquette p. 10 et tri par
encours décroissant (get_top_debtors) ; « de trente jours et plus » —
LATE_AGE (≥ 30 j, direction_dashboard.py:47-50) ; réservations récentes
(pickup) et rythme du mois (pace) dits par la voix — exec_dashboard.py:
34-39 ; bénéfices et résultats — direction_dashboard.js:39-46 (six
onglets), direction_dashboard.py:5-11 (quatre moteurs relus) et
addons/aite_direction_dashboard/tests/test_dashboard_api.py (mêmes chiffres
que les tableaux spécialisés), exec_dashboard.py:25-42 (six phrases
d'explication).

Données : demo.py (Complexe Hôtelier — Démo, Démo Hôtellerie SARL, les
cinq ardoises ouvertes de demo.ARDOISES, âges au 14/10/2026) ; caisses
« Bar de la terrasse » et « Restaurant », fournisseurs et chiffres de
l'hôtel repris de scenarios/c6_direction.py. Le jour rejoué est le
mercredi 14/10/2026 au matin (navigateur en français à Douala) ; « Ce
mois » va du 01/10 au 14/10 (quatorze jours ; période précédente de même
durée : 17/09 → 30/09). C'est avant le règlement d'Armand Mvogo à 15:30 et
la vente de Cédric Ngassa à 13:47 (t10_ardoises.py) : son ardoise ARD/0024
est encore due, d'où « Relancer Armand Mvogo » ; la voix dit « mercredi
matin ». Crédit clients : calculé ici depuis les ardoises et remboursements
de t10_ardoises.py (ARDOISES, SOLDEES, REMBOURSEMENTS, sans ARD/0043 ni le
règlement de 15:30), soit le tableau de bord Recouvrement de c3_caisse.py
et de t10_ardoises.py (indicateurs(True)) : encours 150 000 FCFA sur 5
débiteurs, 101 500 en retard (67,7 %), recouvré 37 000 FCFA en 4
remboursements (Armand Mvogo, 20 000 en espèces le 01/10 ; Ruth Bekolo,
3 000 en Orange Money le 02/10 ; Brigitte Essomba, 12 000 en MTN Mobile
Money le 06/10 ; Francis Tsala, 2 000 en MTN Mobile Money le 10/10),
▲ +12,1 % contre 33 000 du 17 au 30/09 ; nouvelles ardoises 18 500
(ARD/0042), ▼ 63,0 % contre 50 000, en vert ; flux net −18 500 (l'encours
baisse) ; taux 19,8 % ; 2 ardoises réglées (Ruth Bekolo en 20 j, Francis
Tsala en 16 j), délai moyen 18,0 j ; encours de fin de mois à rebours
(16 000, 19 000, 25 000, 94 500, 168 500, 150 000). Stock =
t13_stock.AGREGATS (vrai calcul, relu en nombres) : 2 références en
alerte, coulage 0,6 % (sous le seuil de 2,0 % : pas de ligne « Coulage
au-dessus du seuil »), « Commander » Bière blonde 65 cl 21 000 et Eau
minérale 1,5 L 12 000 FCFA perdus par jour, commande suggérée 2 références
pour 303 050 FCFA, écarts négatifs 41 500 FCFA. Prix d'achat : les deux
premières hausses de t14_achats.PX dans l'ordre de get_price_moves (Bière
blonde +8,3 %, Bière brune +2,9 %, Boissons du Wouri SARL). Dettes
fournisseurs = les factures ouvertes de t14_achats.FACTURES (1 280 000 sur
4 factures, 180 000 échus, 420 000 à payer sous 7 j : « Payer Boissons du
Wouri SARL », échéance 17/10/2026, d'où 11 actions). Ventes du 01 au 13/10
(rien n'est vendu le 14 au matin) : CA HT 3 120 000, marge 1 747 200
(56,0 %), 128 tickets, ▲ +9,4 % sur la période précédente de t12_ventes.py
(17/09 → 30/09, la même que celle du cockpit : _previous_period,
pos_dashboard.py:184-200) ; le soir du vendredi et du samedi : 1 405 000, ▲ +6,8 %, marge 790 400
(56,3 %), 52 tickets. Hôtel : une seule source pour le cockpit, l'activité
par pôle et la réception, donc les chiffres de t01_reception.py, c1 et c6 —
179 nuitées (192 moins les 13 de la nuit du 30/09) × 45 000 = 8 055 000
FCFA ; 20 chambres vendables × 14 jours = 280 nuitées disponibles, d'où
63,9 % et un RevPAR de 28 768 FCFA ; écarts sur la même période l'an dernier : CA des
nuitées et RevPAR ▲ +11,6 %, occupation ▲ +8,2 %, prix moyen ▲ +3,1 %
(1,082 × 1,031 = 1,116) ; réservations récentes 46 nuitées (18
réservations), rythme du mois 412 nuitées contre 387, ▲ +6,5 %. Cash à
risque = 101 500 + 41 500 ; position nette = 150 000 − 1 280 000.
Activité par pôle = celle de c6, hors taxes comme le cockpit : 8 055 000
(nuitées HT, nuit par nuit, le chiffre du cockpit) + 3 120 000 (HT ; panier
3 120 000 / 128 = 24 375) + 1 240 000 (46 prestations) = 12 415 000 FCFA,
mix 64,9 / 25,1 / 10,0 % trié et arrondi comme _mix_rows ; points fidélité
9 895 = les mouvements datés du 01 au 14/10 (_loyalty_points,
exec_dashboard.py:203-211), un point par 1 000 FCFA (barème par défaut).
Un folio est crédité quand il est facturé ou payé, sur tout son montant
hors taxe de séjour et hors lignes déjà créditées à leur source — notes de
chambre de la caisse, prestations reportées (hooks.py:78-130). Le jeu ne
détaille pas les folios facturés de la période : on y compte autant de
nuitées que de nuitées vendues, 8 055 000 FCFA (les nuitées de fin
septembre des séjours partis en octobre compensent celles des 13 séjours
encore en cours le 14 au matin, t01_reception.py) ; plus 1 240 000 de
prestations, créditées à leur source, et environ 600 000 FCFA de tickets
réglés par un client identifié. Le grand livre de t11_fidelite.py (21 734
points depuis novembre 2025) ne peut pas suivre ce rythme ; t11 le note
lui-même (la série ne compte que 211 folios depuis l'ouverture, t03).
Évolution mensuelle (get_evolution lit des mois
entiers) : l'hébergement d'octobre compte les nuitées déjà réservées
jusqu'au 31, les 412 du rythme du mois, soit 18,5 M à 45 000 FCFA — et non
plus 8,1 M, moins que les 8 055 000 du 01 au 14 ; restauration de
t12_ventes.py (EVO_TOUT), prestations réalisées. Tendances du cockpit : CA
HT des ventes de t12_ventes.py (EVO_TOUT), factures de t14_achats.py
(FLUX), encours ci-dessus ; miroir fournisseurs = les factures ouvertes de
t14 par ancienneté au 14/10 (1 100 000 à 0–30 j, 180 000 à 60–90 j). Top
débiteurs : à encours égal (30 000), Brigitte Essomba (ARD/0039, plus
récente) sort avant Sylvie Mbarga (ARD/0017) — tri stable sur des ardoises
lues en create_date desc (pos_credit.py:23).

Cadrages (les gestes sont calés sur les silences de chaque phrase de la
voix : un anneau ou un zoom tombe sur le mot qui le nomme) :
- étape 1 : le décompte de « CA encaissé » (geste compter, espace
  insécable) se termine sur le montant de fmtMoney (espace fine) ; anneaux
  sur « le chiffre encaissé », « la marge », zoom sur « l'argent à
  risque », anneau sur la position nette ;
- étape 2 : les clics tombent sur « Soir… » et « vendredi et samedi » ;
  les trois cartes de pôle qui ne bougent pas (ardoises, stock, dettes)
  sont entourées quand la voix les nomme ;
- étape 3 : défilement dès l'arrivée sur l'onglet Crédit clients, pour
  montrer la balance âgée, la courbe et le Top débiteurs ; les deux rangées
  de cartes (dont « Recouvré » et « Nouvelles ardoises » et leur « vs
  période précédente ») ne sont pas commentées ; le zoom sur le Top
  débiteurs vise le haut du tableau (fy) pour ne pas buter sur le bas du
  navigateur ;
- étape 4 : la bulle sur « dresse la liste du gérant », puis un anneau par
  section, dans l'ordre de la voix ;
- étape 5 : TENDANCES, défilé jusqu'en bas de la vue d'ensemble (pied de
  page lisible, DEFIL_TEND) ; l'anneau du zoom entoure tout le panneau du
  miroir (autour des seules barres, il barrait les titres et la légende),
  la caméra visant le haut du panneau (fy=0) pour ne pas buter sur le coin
  bas du navigateur ;
  étape 6 : retour vers le haut (-110), la rangée Hébergement entière au
  bas du cadre ; pas de zoom (en zoom, la légende de l'étape recouvrirait
  la rangée) ; l'infobulle du « ? » est la phrase de KPI_HINTS (dans le
  produit, l'infobulle native du navigateur) ;
- étape 7 : l'activité par pôle s'ouvre en haut de page (titre « Direction
  — Activité par pôle », dit par la voix), puis défile vers les indicateurs
  de l'hôtel et zoome sur réservations récentes / rythme du mois, la
  caméra visant sous la rangée (fy=2,0) : ni la barre grise ni le coin du
  navigateur dans le cadre ; la voix ne cite ni le total ni les pôles ;
- zooms des étapes 1, 3, 5 et 7 (1,85, 1,8, 1,45 et 1,5) : le cash à
  risque, le Top débiteurs, le miroir, les indicateurs de l'hôtel.

Captures de référence (modèle visuel, jamais incrustées) : ref_muk/060-
direction(-pleine).png, 053-h-tel-direction(-pleine).png, 330-direction-
accueil.png, 000-accueil.png ; captures prises en lecture seule sur la base
MuK (onglets À traiter et Crédit clients, tendances, tableau exécutif ouvert
depuis la carte RevPAR) ; docs/captures_uat/r4-direction-06 et -07 ;
captures/40_tableau_executif_indicateurs.png, 41_cockpit_direction_
hebergement.png — antérieures à la livraison 4 : les libellés viennent du
code. Chapitre déjà rejoué dans la présentation : scenarios/c6_direction.py.

Écarts de la version précédente, corrigés dans la livraison 4 (le produit
corrigé est rejoué) :
1. « Ce mois » démarrait la veille du 1er à Douala (n° 38) : « Du
   01/10/2026 » dans les deux écrans ; dates ISO (n° 37 et n° 2) : « Du
   01/10/2026 au 14/10/2026 » sous le total de l'activité par pôle, dates
   jj/mm/aaaa dans « Derniers remboursements » et l'échéance « 17/10/2026 »
   de « Payer … ».
2. Corrigé dès la livraison 3 (aite_exec_dashboard 18.0.1.1.1, n° 25) :
   tout est HT, « Hébergement » = les nuitées HT nuit par nuit du cockpit.
3. Corrigé dès la livraison 3 (n° 23) : barres du CA, côté fournisseurs du
   miroir et ligne « Payer <fournisseur> ».
4. Balance âgée clients (n° 70) : couleurs lues sur la clé de tranche
   (« 30–60 j » ocre, « +90 j » rouge) ; « 2 ardoises » au lieu de
   « 2 cl. ».
5. Pluriels figés et jours bruts (n° 41, 44) : « 1 ardoise ouverte »,
   « 2 ardoises réglées », « 5 débiteurs actifs », « 18,0 j », « 11
   actions », « 1 facture échue », « 2 références » ; le flux net et sa
   phrase servie par le serveur (n° 24) : « −18 500 FCFA », « nouveaux −
   recouvré : l'encours baisse ».
6. Pourcentages (n° 41) : une décimale partout (« 63,9 % » dans les deux
   écrans, « 19,8 % », « 64,9 % », « +8,3 % · … ») ; carte « Prestations »
   avec son liseré teal (n° 70) ; espace fine dans les montants des deux
   écrans ; titres distincts (n° 70) : « Direction — Vue consolidée » pour
   le cockpit, « Direction — Activité par pôle » pour l'exécutif (menu
   Hôtel → Activité par pôle).
7. Anglais résiduel (n° 42) : « Prix moyen par nuit (ADR) », « Revenu par
   chambre disponible (RevPAR) », « Réservations récentes (pickup) »,
   « Rythme du mois (pace) », infobulles reprises en tête ; cockpit aligné
   sur POS Crédit (relecture croisée) : origine « Point de vente » au lieu
   de « POS », « POS Crédit » au lieu de « Crédit v2 », « Ouvrir POS
   Crédit ↗ », « En retard (+30 j) », « Plus ancienne dette », « Nouvelles
   ardoises ». La voix dit les libellés français ; la douleur « RevPAR,
   pickup, pace : du jargon » reste celle de l'accroche, le sigle est
   désormais expliqué en tête de carte.
8. Écarts N-1 (n° 62) : « vs période précédente » sous « CA encaissé »,
   « Recouvré » et « Nouvelles ardoises » ; une hausse des nouvelles
   ardoises serait rouge (upIsBad).

Reste dans le produit, rejoué tel quel : deux signes moins dans le même
cockpit — « -1 130 000 FCFA » (trait d'union de toLocaleString, position
nette) et « −18 500 FCFA » (signe typographique de netFlowText, flux net).
"""

import contextlib
import io
import re
from datetime import date, timedelta

import demo
from scenarios import t10_ardoises, t12_ventes, t13_stock
with contextlib.redirect_stderr(io.StringIO()):     # l'avertissement 409 de t14 ne concerne pas ce tutoriel
    from scenarios import t14_achats
from ecrans import (APPS_PROFIL, age, compte, date_fr, e, entier, fcfa, fenetre_muk, jours, mois_abrege, navigateur,
                    pct, sens, variation, vue_libre)
from marketing import bulle, dezoom, reaction, zoom
from moteur import anneau, cacher, classe, clic, compter, curseur, defiler, montrer, pause, texte, vue

NOM, ROLE = demo.POSTES['direction']
SOCIETE = demo.SOCIETE

# Le jour rejoué et la période « Ce mois » : du 1er au jour même, en dates LOCALES (rangeFor / localIsoDate,
# direction_dashboard.js:63-86 ; periodRange de l'exécutif, utils.js:65-89) — l'ancien « Du 30/09/2026 » (écart
# n° 38) a disparu. Quatorze jours ; la période précédente de même durée va du 17/09 au 30/09
# (pos_credit_dashboard.py:202-206).
AUJ = date(2026, 10, 14)
DU = AUJ.replace(day=1)
NB_JOURS = (AUJ - DU).days + 1
assert NB_JOURS == 14


def m(n):
    """Un montant des deux tableaux de bord : fmtMoney (toLocaleString fr-FR : espace fine U+202F entre les
    milliers, trait d'union devant un négatif), puis une espace simple et le symbole de la société
    (direction_dashboard.js:92-95, exec utils.js:5-9)."""
    return fcfa(n, tdb=True)


def ms(n):
    """moneyShort : le montant sans symbole (direction_dashboard.js:362-364)."""
    return entier(n, tdb=True)


def nombre(texte_):
    """Le nombre d'un chiffre mis en forme par un autre scénario (« 41 500 FCFA », « 0,6 % »)."""
    return float(re.sub(r'[^\d,\-]', '', texte_).replace(',', '.'))


# Le stock de t13_stock.py (AGREGATS, calculé par le vrai code) et les prix d'achat de t14_achats.py (PX), relus
# en nombres puis remis au format du cockpit.
_AG = t13_stock.AGREGATS
STOCK_VALEUR, ALERTES = nombre(_AG['valeur']), _AG['alertes']
COULAGE_PCT, PERTES, ECARTS_NEG = nombre(_AG['coulage_pct']), nombre(_AG['pertes']), nombre(_AG['ecarts_negatifs'])
COMMANDER = [(n, nombre(v)) for n, v in _AG['commander']][:2]
NB_CMD, VAL_CMD = _AG['commande_suggeree'][0], nombre(_AG['commande_suggeree'][1])
SEUIL_COULAGE = 2.0                     # coul_seuil par défaut du moteur Stock (« seuil 2,0 % »)
assert COULAGE_PCT <= SEUIL_COULAGE     # pas de ligne « Coulage au-dessus du seuil » (direction_dashboard.py:413-419)
# price_up (get_actions, direction_dashboard.py:749-753) : les hausses dans l'ordre de get_price_moves (dépense
# décroissante), les deux premières seulement (:439-446) ; indication « +8,3 % · <fournisseur> » (une décimale,
# espace insécable avant « % »).
HAUSSES = [(p['nom'], '+%s · %s' % (pct((p['p1'] / float(p['p0']) - 1) * 100), p['four']))
           for p in t14_achats.PX if p['p1'] > p['p0']][:2]
assert [h[0] for h in HAUSSES] == ['Bière blonde 65 cl', 'Bière brune 65 cl']

# Les dettes fournisseurs : les factures ouvertes de t14_achats.py (FACTURES : fournisseur, n°, date, échéance,
# montant, payé), lues par le moteur Achats le 14/10 (get_kpis : encours, échues, à payer sous 7 j — réglage
# « soon » par défaut ; _due_soon, direction_dashboard.py:244-257).
_OUV = [(f[0], f[2], f[3], f[4] - f[5]) for f in t14_achats.FACTURES if f[4] > f[5]]
DETTES = sum(f[3] for f in _OUV)
ECHUES = [f for f in _OUV if f[2] < AUJ]
SOUS7 = [f for f in _OUV if 0 <= (f[2] - AUJ).days <= 7]
assert (DETTES, sum(f[3] for f in ECHUES), len(ECHUES), sum(f[3] for f in SOUS7)) == (1280000, 180000, 1, 420000)


# Le crédit clients le matin du 14/10, tel que le moteur Crédit le lit (pos_credit_dashboard.py : get_kpis
# :129-246, get_aging :255-289, get_top_debtors, get_recent_payments, get_evolution :490-540) : les ardoises et
# remboursements de t10_ardoises.py, sans la vente de Cédric Ngassa (ARD/0043) ni le règlement d'Armand Mvogo de
# 15:30 (t10_ardoises.indicateurs(True)), sur la période « Ce mois » qui démarre désormais le 01/10.
assert t10_ardoises.REMBOURSEMENTS[0][:3] == (AUJ, 'ARD/0024', 'Armand Mvogo')
assert t10_ardoises.ARDOISES[0][0] == 'ARD/0043'
REMB = t10_ardoises.REMBOURSEMENTS[1:]
ARDS = [a[:5] for a in t10_ardoises.ARDOISES[1:]] + list(t10_ardoises.SOLDEES)
RESTE = {a[0]: a[4] - sum(r[5] for r in REMB if r[1] == a[0]) for a in ARDS}
OUVERTES = [a for a in ARDS if RESTE[a[0]] > 0]                         # lues en create_date desc (pos_credit.py:23)
AGE = {a[0]: (AUJ - a[3]).days for a in OUVERTES}
# Tranches du moteur Crédit (borne basse incluse, haute exclue) et couleurs du cockpit, lues sur la clé
# (agingKey, AGING_COLORS : direction_dashboard.js:165-174, :477-491).
TRANCHES_CLI = [('0_30', '0–30 j', -10 ** 9, 30, '#3B6D11'), ('31_60', '30–60 j', 30, 60, '#854F0B'),
                ('61_90', '60–90 j', 60, 90, '#a3702a'), ('90p', '+90 j', 90, 10 ** 9, '#A32D2D')]


def _credit(du, au):
    """get_kpis du moteur Crédit sur [du, au], comparé à la période précédente de même durée."""
    prev_au = du - timedelta(days=1)
    prev_du = prev_au - timedelta(days=(au - du).days)
    remb = [r for r in REMB if du <= r[0] <= au]
    nouv = [a for a in ARDS if du <= a[3] <= au]
    reglees = []
    for a in ARDS:
        dates = [r[0] for r in REMB if r[1] == a[0]]
        if RESTE[a[0]] == 0 and dates and du <= max(dates) <= au:
            reglees.append((max(dates) - a[3]).days)
    k = dict(encours=sum(RESTE[a[0]] for a in OUVERTES), debiteurs=len(set(a[1] for a in OUVERTES)),
             retard=sum(RESTE[a[0]] for a in OUVERTES if AGE[a[0]] >= 30),
             recouvre=sum(r[5] for r in remb), remb=sorted(remb, key=lambda r: r[0], reverse=True),
             nouv=sum(a[4] for a in nouv), nb_nouv=len(nouv), reglees=len(reglees),
             delai=sum(reglees) / float(len(reglees)) if reglees else 0.0,
             prec_rec=sum(r[5] for r in REMB if prev_du <= r[0] <= prev_au),
             prec_nouv=sum(a[4] for a in ARDS if prev_du <= a[3] <= prev_au))
    k['taux'] = k['recouvre'] * 100.0 / (k['encours'] + k['recouvre'])
    k['d_rec'] = (k['recouvre'] - k['prec_rec']) * 100.0 / k['prec_rec']
    k['d_nouv'] = (k['nouv'] - k['prec_nouv']) * 100.0 / k['prec_nouv']
    k['flux'] = k['nouv'] - k['recouvre']
    return k


CR = _credit(DU, AUJ)
PLUS_VIEILLE = min(OUVERTES, key=lambda a: a[3])
assert (CR['encours'], CR['debiteurs'], CR['retard'], CR['recouvre'], len(CR['remb']), CR['nouv'], CR['nb_nouv'],
        CR['reglees'], CR['delai'], CR['prec_rec'], CR['prec_nouv'], CR['flux']) == (
    150000, 5, 101500, 37000, 4, 18500, 1, 2, 18.0, 33000, 50000, -18500)
assert (pct(CR['retard'] * 100.0 / CR['encours']), pct(CR['taux']), variation(CR['d_rec']),
        variation(CR['d_nouv'])) == ('67,7\xa0%', '19,8\xa0%', '▲ +12,1\xa0%', '▼ 63,0\xa0%')
AGING = [(cle, lib, sum(RESTE[a[0]] for a in OUVERTES if lo <= AGE[a[0]] < hi),
          len([a for a in OUVERTES if lo <= AGE[a[0]] < hi]), coul) for cle, lib, lo, hi, coul in TRANCHES_CLI]
assert [(x[2], x[3]) for x in AGING] == [(48500, 2), (71500, 2), (0, 0), (30000, 1)]
# Pastille de l'onglet Crédit clients : les ardoises hors de la tranche 0–30 j (get_overview, :613-631).
BADGE_CREDIT = sum(x[3] for x in AGING if x[0] != '0_30')
# Top débiteurs (photo) : tri par encours, stable sur des ardoises lues en create_date desc — à encours égal,
# ARD/0039 (Essomba, plus récente) sort avant ARD/0017 (Mbarga).
TOP = sorted(OUVERTES, key=lambda a: -RESTE[a[0]])
assert [a[1] for a in TOP] == ['Armand Mvogo', 'Brigitte Essomba', 'Sylvie Mbarga', 'Joël Kamga', 'Patrick Nkoulou']
# Encours de fin de mois, à rebours depuis l'encours du jour (_encours_series, direction_dashboard.py:260-277) :
# les flux mensuels de t10_ardoises.py (mai → août), septembre et octobre recalculés pour ce matin-là.
_OUV_MOIS = list(t10_ardoises.OUVERTES_MOIS[:4]) + [sum(a[4] for a in ARDS if a[3].month == mo) for mo in (9, 10)]
_REC_MOIS = list(t10_ardoises.RECOUVRE_MOIS[:4]) + [sum(r[5] for r in REMB if r[0].month == mo) for mo in (9, 10)]
ENCOURS = [CR['encours']]
for _o, _r in zip(reversed(_OUV_MOIS[1:]), reversed(_REC_MOIS[1:])):
    ENCOURS.insert(0, ENCOURS[0] - (_o - _r))
assert ENCOURS == [16000, 19000, 25000, 94500, 168500, 150000]
# Les six mois des courbes (mai → oct.) : MONTHS_FR des moteurs serveur (direction_dashboard.py:54-55,
# pos_credit_dashboard.py:508-509).
MOIS = [mois_abrege(mo) for mo in range(5, 11)]

CAL = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3.5" y="5" width="17" '
       'height="15.5" rx="1.5"/><path d="M3.5 10h17M8 3v4M16 3v4"/></svg>')


# ------------------------------------------------------------ composants --
def chip(ident, libelle, on=False, point=None):
    p = '<i class="t15-dotc" style="background:%s"></i>' % point if point else ''
    return '<span class="t15-chip%s" id="%s">%s%s</span>' % (' on' if on else '', ident, p, e(libelle))


def barre(libelle, contenu, note=None, ident_note=None):
    n = '<span class="t15-note"%s>%s</span>' % (' id="%s"' % ident_note if ident_note else '', e(note)) if note else ''
    return '<div class="t15-bar"><span class="t15-lblf">%s</span>%s%s</div>' % (e(libelle), contenu, n)


def date_in(ident, valeur):
    return '<span class="t15-date" id="%s">%s<span class="t15-cal">%s</span></span>' % (ident, e(valeur), CAL)


def ecart(v, libelle=None, hausse_mauvaise=False):
    """deltaText et deltaCls de KpiCard (direction_dashboard.js:193-199) : « ▲ +9,4 % », suivi du deltaLabel quand
    la carte en porte un (« vs période précédente ») ; vert, rouge ou gris selon le sens et upIsBad."""
    genre = {'haut': 'up', 'bas': 'down', 'nul': 'flat'}[sens(v, hausse_mauvaise)]
    return variation(v) + (' ' + libelle if libelle else ''), genre


def carte(ident, libelle, valeur, sous=None, badge=None, accent=None, mega=False, delta=None, aide=False):
    """Une carte du cockpit (KpiCard, direction_dashboard.xml:4-26) ; ``delta`` : sortie d'``ecart``. L'écart est un
    bloc insécable qui passe sous le montant quand la ligne est trop courte (direction_dashboard.scss:155-162)."""
    classes = 't15-card' + (' t15-mega' if mega else '') + (' t15-al-' + accent if accent else '')
    b = ('<span class="t15-badge t15-b-%s">%s</span>' % (badge, 'période' if badge == 'per' else 'photo')
         if badge else '')
    a = '<span class="t15-help" id="%s-aide">?</span>' % ident if aide else ''
    d = ('<span class="t15-delta %s" id="%s-d">%s</span>' % (delta[1], ident, e(delta[0])) if delta else '')
    s = '<div class="t15-sub" id="%s-s">%s</div>' % (ident, e(sous)) if sous else ''
    return ('<div class="%s" id="%s">%s<div class="t15-lbl">%s%s</div><div class="t15-val"><span class="t15-v" '
            'id="%s-v">%s</span>%s</div>%s</div>' % (classes, ident, b, e(libelle), a, ident, e(valeur), d, s))


def sect(texte_):
    return '<div class="t15-sect">%s</div>' % e(texte_)


def rangee(*cartes, ident=None):
    return '<div class="t15-row"%s>%s</div>' % (' id="%s"' % ident if ident else '', ''.join(cartes))


def panneau(titre, source, corps, ident=None, pastille=None):
    p = ''
    if pastille:
        p = '<span class="t15-pill %s">%s</span>' % ('t15-p-rouge' if pastille == 'URGENT' else 't15-p-ambre', pastille)
    return ('<div class="t15-panel"%s><h3>%s%s<span class="t15-src">%s</span></h3>%s</div>'
            % (' id="%s"' % ident if ident else '', p, e(titre), e(source), corps))


def mini(lignes, ident=None):
    """table.add-mini : [(id, libellé, montant, indication html)]."""
    corps = ''.join('<div class="t15-tr"%s><span class="t15-td">%s</span><span class="t15-r">%s</span>'
                    '<span class="t15-age">%s</span></div>'
                    % (' id="%s"' % i if i else '', e(lib), e(mt), h) for i, lib, mt, h in lignes)
    return '<div class="t15-mini"%s>%s</div>' % (' id="%s"' % ident if ident else '', corps)


def pill(texte_, rouge=False):
    return '<span class="t15-pill %s">%s</span>' % ('t15-p-rouge' if rouge else 't15-p-ambre', e(texte_))


def hbar(libelle, largeur, couleur, valeur, indice=''):
    """HBar (direction_dashboard.xml:28-40) : largeur bornée entre 1 et 100 %."""
    ind = '<span class="t15-hint">%s</span>' % e(indice) if indice else ''
    return ('<div class="t15-hbar"><span class="t15-hl">%s</span><span class="t15-ht"><i style="width:%.1f%%;'
            'background:%s"></i></span><span class="t15-hv">%s%s</span></div>'
            % (e(libelle), max(1, min(100, largeur)), couleur, e(valeur), ind))


# ------------------------------------------------------ les chiffres --
# Ventes du 01 au 14/10, toutes caisses (le 14 au matin, rien n'est encore vendu) : t12_ventes.py et c6_direction.py
# (harmonisation : CA HT 3 120 000, marge 1 747 200, 128 tickets, +9,4 % sur la période précédente de même durée —
# celle de t12, 17/09 → 30/09, la même que celle du cockpit).
CA, MARGE, TICKETS, D_CA = 3120000, 1747200, 128, (3120000 - 2852000) * 100.0 / 2852000
# Le soir (18–23h) du vendredi et du samedi : 52 tickets, ▲ +6,8 % sur les mêmes soirs de la période précédente.
CA_SOIR, MARGE_SOIR, TICKETS_SOIR, D_SOIR = 1405000, 790400, 52, 6.8
assert (variation(D_CA), pct(MARGE * 100.0 / CA), pct(MARGE_SOIR * 100.0 / CA_SOIR)) == (
    '▲ +9,4\xa0%', '56,0\xa0%', '56,3\xa0%')
# L'hôtel du 01 au 14/10 (tuile Hébergement, relue de aite.hotel.dashboard.get_kpis, hotel_dashboard.py:303-380) :
# une seule source pour le cockpit, l'activité par pôle et le tableau de bord de la réception, donc les chiffres
# de t01_reception.py, c1_reception.py et c6_direction.py — 179 nuitées vendues (les 192 d'avant comptaient les
# 13 de la nuit du 30/09) à 45 000 FCFA, 20 chambres vendables × 14 jours = 280 nuitées disponibles ; écarts sur
# la même période l'an dernier ; réservations récentes (pickup) et rythme du mois (pace) : _pickup / _pace,
# :183-239.
NUITS, ADR, CHAMBRES = 179, 45000, 20
CA_NUITS = NUITS * ADR
DISPO = CHAMBRES * NB_JOURS
OCC, REVPAR = NUITS * 100.0 / DISPO, CA_NUITS / float(DISPO)
D_CA_NUITS, D_OCC, D_ADR, D_REVPAR = 11.6, 8.2, 3.1, 11.6
PICKUP, PICKUP_RES, PACE, PACE_N1 = 46, 18, 412, 387
D_PACE = (PACE - PACE_N1) * 100.0 / PACE_N1
assert (CA_NUITS, DISPO, pct(OCC), m(REVPAR), variation(D_PACE)) == (
    8055000, 280, '63,9\xa0%', '28 768 FCFA', '▲ +6,5\xa0%')
# RevPAR et CA des nuitées ont le même écart (mêmes chambres disponibles d'une année à l'autre) ; occupation × prix.
assert round((1 + D_OCC / 100) * (1 + D_ADR / 100) * 100 - 100, 1) == D_REVPAR == D_CA_NUITS

# ------------------------------------------------------------ le cockpit --
JOURS = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim']

# -- À traiter (get_actions → _build_actions, direction_dashboard.py:329-450 et :741-771) --
RELANCES = [a for a in TOP if AGE[a[0]] >= 30][:3]                     # débiteurs de 30 j et plus (LATE_AGE)
PAYER = sorted(SOUS7, key=lambda f: f[2])[:3]
SECTIONS = [
    ('t15-s-credit', 'Ardoises anciennes', 'Crédit', 'URGENT',
     [('t15-r-%s' % a[1].split()[-1].lower(), 'Relancer %s' % a[1], m(RESTE[a[0]]), '%d j' % AGE[a[0]])
      for a in RELANCES]),
    ('t15-s-four', 'Fournisseurs', 'Achats', 'URGENT',
     [(None, 'Régulariser %s' % compte(len(ECHUES), 'facture échue', 'factures échues', tdb=False),
       m(sum(f[3] for f in ECHUES)), 'échu')]
     + [('t15-r-payer', 'Payer %s' % f[0], m(f[3]), date_fr(f[2])) for f in PAYER]),
    ('t15-s-stock', 'Stock', 'Stock', 'URGENT',
     [(None, 'Commander %s' % n, m(v), 'perd / jour') for n, v in COMMANDER]
     + [(None, 'Lancer la commande suggérée (%s)' % compte(NB_CMD, 'référence', 'références', tdb=False), m(VAL_CMD),
         'sous seuil')]),
    ('t15-s-coul', 'Coulage & écarts', 'Stock', 'À SURVEILLER',
     [(None, "Écarts d'inventaire négatifs", m(ECARTS_NEG), 'contrôler')]),
    ('t15-s-prix', "Prix d'achat", 'Achats', 'À SURVEILLER', [(None, 'Renégocier %s' % n, '', h) for n, h in HAUSSES]),
]
NB_ACTIONS = sum(len(s[4]) for s in SECTIONS)
assert [r[1] for r in SECTIONS[0][4]] == ['Relancer Armand Mvogo', 'Relancer Sylvie Mbarga', 'Relancer Joël Kamga']
assert [(f[0], f[2]) for f in PAYER] == [('Boissons du Wouri SARL', date(2026, 10, 17))] and NB_ACTIONS == 11

ONGLETS = [('vue', "Vue d'ensemble", None), ('pos', 'Ventes (POS)', None), ('credit', 'Crédit clients', BADGE_CREDIT),
           ('stock', 'Stock', ALERTES), ('achat', 'Achats', len(ECHUES)), ('todo', 'À traiter', None)]


def onglet(cle, libelle, n):
    pastille = '<span class="t15-n" id="t15-tab-%s-n">%s</span>' % (cle, entier(n, tdb=True)) if n else ''
    if cle == 'todo':        # la pastille n'apparaît qu'une fois l'onglet chargé (badges, js:608-617)
        pastille = '<span class="t15-n t15-attente" id="t15-tab-todo-n">%s</span>' % entier(NB_ACTIONS, tdb=True)
    return '<span class="t15-tab%s" id="t15-tab-%s">%s%s</span>' % (' on' if cle == 'vue' else '', cle, e(libelle),
                                                                   pastille)


TOP_COCKPIT = ('<div class="t15-top"><div class="t15-head"><div class="t15-h1">Direction — Vue consolidée</div>'
               '<div class="t15-hsub">POS · Crédit clients · Stock · Achats — %s</div></div>%s</div>' % (e(SOCIETE), ''.join([
                   barre('PÉRIODE', ''.join([chip('t15-pe-all', 'Toute la période'), chip('t15-pe-today', "Aujourd'hui"),
                                             chip('t15-pe-week', 'Cette semaine'), chip('t15-pe-month', 'Ce mois', True),
                                             chip('t15-pe-quarter', 'Ce trimestre'), chip('t15-pe-year', 'Cette année'),
                                             '<span class="t15-du">Du</span>', date_in('t15-du', date_fr(DU)),
                                             '<span class="t15-du">au</span>', date_in('t15-au', date_fr(AUJ)),
                                             chip('t15-apply', 'Appliquer')])),
                   barre('CAISSE', chip('t15-ca-tout', 'Toutes les caisses', True)
                         + chip('t15-ca-bar', 'Bar de la terrasse', point='#714B67')
                         + chip('t15-ca-resto', 'Restaurant', point='#185FA5'),
                         'caisse, heure et jours filtrent les données de vente', 't15-note-caisse'),
                   barre('HEURE', ''.join([chip('t15-h-tout', 'Toute la journée', True), chip('t15-h-matin', 'Matin 6–12h'),
                                           chip('t15-h-am', 'Après-midi 12–18h'), chip('t15-h-soir', 'Soir 18–23h'),
                                           chip('t15-h-nuit', 'Nuit 23–6h')])),
                   barre('JOUR', ''.join(chip('t15-j-%d' % i, j) for i, j in enumerate(JOURS)),
                         'multi-sélection — aucun = tous'),
                   barre('VUE', ''.join(onglet(*o) for o in ONGLETS)),
               ])))

# -- la vue d'ensemble : du 01 au 14/10/2026, toutes caisses (direction_dashboard.xml:218-325) --
PREC = 'vs période précédente'
SANTE = rangee(
    carte('t15-k-ca', 'CA encaissé', m(CA), 'HT · %s · POS payés / facturés' % compte(TICKETS, 'ticket', 'tickets'),
          'per', 'vert', True, ecart(D_CA, PREC)),
    carte('t15-k-marge', 'Marge brute réalisée', m(MARGE), '%s du CA · CA − coût des ventes' % pct(MARGE * 100.0 / CA),
          'per', 'teal', True),
    carte('t15-k-risque', 'Cash à risque', m(CR['retard'] + PERTES),
          'ardoises +30 j (%s) + coulage (%s)' % (ms(CR['retard']), ms(PERTES)), 'per', 'rouge', True),
    # phrase de la position nette servie par le serveur (_net_position_text, direction_dashboard.py:108-122)
    carte('t15-k-net', 'Crédits clients − dettes fournisseurs', m(CR['encours'] - DETTES),
          "%s d'ardoises · %s de dettes — vos fournisseurs financent l'exploitation" % (ms(CR['encours']), ms(DETTES)),
          'photo', 'info', True),
    ident='t15-sante')
POLES = rangee(
    carte('t15-p-tix', 'Ventes — tickets', entier(TICKETS, tdb=True), 'panier moyen %s' % m(CA / float(TICKETS)), 'per'),
    carte('t15-p-ard', 'Encours ardoises', m(CR['encours']),
          '%s · %s en retard (+30 j)' % (compte(CR['debiteurs'], 'débiteur', 'débiteurs'), ms(CR['retard'])),
          'photo', 'ambre'),
    carte('t15-p-four', 'Dettes fournisseurs', m(DETTES),
          '%s échues · %s sous 7 j' % (ms(sum(f[3] for f in ECHUES)), ms(sum(f[3] for f in SOUS7))), 'photo', 'info'),
    carte('t15-p-stock', 'Stock — valeur / alertes', m(STOCK_VALEUR),
          '%s · coulage %s' % (compte(ALERTES, 'référence en alerte', 'références en alerte'), pct(COULAGE_PCT)),
          'photo'),
    ident='t15-poles')
HOTEL = rangee(
    carte('t15-x-ca', 'CA des nuitées (HT)', m(CA_NUITS),
          '%s · rythme du mois (pace) : %s (N-1 : %s)' % (compte(NUITS, 'nuitée vendue', 'nuitées vendues'),
                                                         entier(PACE, tdb=True), entier(PACE_N1, tdb=True)),
          'per', 'vert', delta=ecart(D_CA_NUITS), aide=True),
    carte('t15-x-occ', "Taux d'occupation", pct(OCC),
          'réservations récentes (pickup) : %s ces 7 j pour les 30 prochains'
          % compte(PICKUP, 'nuitée prise', 'nuitées prises'), 'per', delta=ecart(D_OCC), aide=True),
    carte('t15-x-adr', 'Prix moyen par nuit (ADR)', m(ADR), 'CA hébergement ÷ nuitées vendues', 'per',
          delta=ecart(D_ADR), aide=True),
    carte('t15-x-revpar', 'Revenu par chambre disponible (RevPAR)', m(REVPAR), 'par chambre disponible, vendue ou non',
          'per', 'teal', delta=ecart(D_REVPAR), aide=True),
    ident='t15-hr')

# Tendances (direction_dashboard.xml:42-107) : six mois alignés sur la clé AAAA-MM (_month_trends,
# direction_dashboard.py:488-520), libellés courts « mai » … « oct. » (_month_label).
# CA HT des ventes par mois : l'évolution mensuelle de t12_ventes.py (EVO_TOUT ; octobre : du 01 au 13/10,
# rien n'est encore vendu le 14 au matin), relue sur les 183 derniers jours (get_overview).
VENTES = [x[1] for x in t12_ventes.EVO_TOUT]
assert [x[0] for x in t12_ventes.EVO_TOUT][0] == 'mai 2026' and VENTES[-1] == CA
# Factures fournisseurs par mois (get_flux_months) : celles de t14_achats.py (FLUX).
ACHATS = [f[1] for f in t14_achats.FLUX]
MAX_BARRE = max(VENTES + ACHATS)                     # maxBar : CA et achats sur la même échelle (js:216-222)


def trend_svg():
    mb, ml = MAX_BARRE, max(ENCOURS)
    slot = 500.0 / 6
    corps = []
    pts = []
    for i, p in enumerate(MOIS):
        x0 = 45 + i * slot
        h = ACHATS[i] / float(mb) * 160
        hc = VENTES[i] / float(mb) * 160
        corps.append('<rect x="%.1f" y="%.1f" width="22" height="%.1f" fill="#714B67"/>' % (x0 + slot / 2 - 24, 180 - hc, hc))
        corps.append('<rect x="%.1f" y="%.1f" width="22" height="%.1f" fill="#185FA5"/>' % (x0 + slot / 2 + 2, 180 - h, h))
        corps.append('<text x="%.1f" y="198" font-size="10" fill="#62615C" text-anchor="middle">%s</text>'
                     % (x0 + slot / 2, e(p)))
        pts.append((x0 + slot / 2, 180 - ENCOURS[i] / float(ml) * 160))
    ligne = ' '.join('%.1f,%.1f' % p for p in pts)
    points = ''.join('<circle cx="%.1f" cy="%.1f" r="3.5" fill="#854F0B"/>' % p for p in pts)
    # maxBarLabel / maxLineLabel : fmtMoney sans symbole (direction_dashboard.js:258-263)
    return ('<svg viewBox="0 0 560 212" class="t15-trend"><g stroke="#eeede8" stroke-width="1"><line x1="40" y1="20" '
            'x2="545" y2="20"/><line x1="40" y1="100" x2="545" y2="100"/><line x1="40" y1="180" x2="545" y2="180"/></g>'
            '<g font-size="9" fill="#62615C" text-anchor="end"><text x="36" y="23">%s</text><text x="36" y="183">0'
            '</text></g><g font-size="9" fill="#854F0B" text-anchor="start"><text x="548" y="23">%s</text>'
            '<text x="548" y="183">0</text></g>%s<polyline points="%s" fill="none" stroke="#854F0B" stroke-width="2.5"/>'
            '%s</svg>' % (ms(mb), ms(ml), ''.join(corps), ligne, points))


LEGENDE_TREND = ('<div class="t15-legend"><i class="t15-dot" style="background:#714B67"></i>CA encaissé'
                 '<i class="t15-dot" style="background:#185FA5"></i>Achats (factures)'
                 '<i class="t15-dot" style="background:#854F0B"></i>Encours d\'ardoises (échelle droite)</div>')

# Miroir (MirrorAging, direction_dashboard.js:266-294) : côté clients, la balance âgée du moteur Crédit ; côté
# fournisseurs, les factures ouvertes rangées par ancienneté depuis la date de facture au 14/10, borne basse
# incluse (_bucket_supplier_invoices et AGE_BUCKETS, direction_dashboard.py:40-45, :192-242).
MIROIR_FOUR = ['#185FA5', '#5b83b0', '#8fa8c4', '#b9c9da']
_FOUR = [sum(f[3] for f in _OUV if lo <= max(0, (AUJ - f[1]).days) < hi) for _c, _l, lo, hi, _k in TRANCHES_CLI]
assert _FOUR == [1100000, 0, 180000, 0] and sum(_FOUR) == DETTES
_MAX_C, _MAX_F = max(1, max(x[2] for x in AGING)), max(1, max(_FOUR))
MIROIR = ('<div class="t15-mhead"><span>Vos clients vous doivent</span><span class="t15-msp"></span>'
          '<span>Vous devez aux fournisseurs</span></div><div class="t15-mirror" id="t15-mirror">%s</div>'
          '<div class="t15-legend">Gauche : du cash qui s\'évapore avec l\'âge. Droite : du crédit fournisseur — gratuit '
          'tant que les échéances tiennent.</div>'
          % ''.join('<div class="t15-mrow"><div class="t15-mside t15-left"><span class="t15-mval">%s</span>'
                    '<i style="width:%.1f%%;background:%s"></i></div><div class="t15-mlab">%s</div><div class="t15-mside">'
                    '<i style="width:%.1f%%;background:%s"></i><span class="t15-mval">%s</span></div></div>'
                    % (ms(x[2]), max(2.0, x[2] * 100.0 / _MAX_C), x[4], e(x[1]),
                       max(2.0, _FOUR[i] * 100.0 / _MAX_F), MIROIR_FOUR[i], ms(_FOUR[i]))
                    for i, x in enumerate(AGING)))
TENDANCES = ('<div class="t15-row" id="t15-tend">%s%s</div>'
             % (panneau('CA vs Achats — 6 mois, et encours d\'ardoises', 'POS · Achats · Crédit',
                        trend_svg() + LEGENDE_TREND, 't15-tend-ca'),
                panneau('Balance âgée en miroir', 'Crédit · Achats', MIROIR, 't15-tend-mir')))

# L'infobulle du « ? » : la phrase du tableau exécutif reprise telle quelle (KPI_HINTS, exec_dashboard.py:31-33).
TIP_REVPAR = ('<div class="infobulle masque t15-tip" id="t15-tip-revpar" data-layout-allow-overlap '
              'data-layout-allow-occlusion>Revenu par chambre disponible (RevPAR) : ce que rapporte chaque chambre '
              'disponible, vendue ou non — c\'est l\'indicateur qui combine prix et remplissage.</div>')
# Le pied de page, carte blanche sous le contenu de l'onglet (direction_dashboard.xml:843-849, scss:247-250) ;
# espaces insécables de la typographie française seulement (le texte est celui du gabarit).
PIED = ('<div class="t15-footer" id="t15-footer">%s</div>'
        % e('Sources\xa0: Analyse AITE · POS Crédit · Stock & Inventaire · Achats & Fournisseurs. Les cartes '
            '«\xa0période\xa0» suivent les filtres\xa0; les cartes «\xa0photo\xa0» sont des instantanés. Caisse, '
            'tranche horaire et jours s\'appliquent aux données de vente.'))
VUE_ENSEMBLE = ('<div class="vue initiale t15-pane" id="t15-b-vue"><div class="t15-defil" id="t15-vue-defil" '
                'data-layout-allow-overflow data-layout-allow-occlusion>%s%s%s%s%s%s%s%s%s%s</div></div>'
                % (sect("SANTÉ DE L'AFFAIRE"), SANTE, sect("L'ESSENTIEL PAR PÔLE — cliquer une carte ouvre l'onglet"),
                   POLES, sect('HÉBERGEMENT — écarts vs même période N-1 ; cliquer une carte ouvre « Direction — '
                               'Activité par pôle »'), HOTEL, sect('TENDANCES'), TENDANCES, PIED, TIP_REVPAR))

# -- onglet Crédit clients, même période (direction_dashboard.xml:419-547) --
# netFlowText : signe seulement pour un flux non nul, « − » typographique devant un négatif (js:512-519) ;
# phrase servie par le serveur (_net_flow_sentence, direction_dashboard.py:124-135).
FLUX_NET = ('+' if CR['flux'] > 0 else '−' if CR['flux'] < 0 else '') + m(abs(CR['flux']))
PHRASE_FLUX = "nouveaux − recouvré : l'encours %s" % ('monte' if CR['flux'] > 0 else 'baisse')
CREDIT_KPI = (
    rangee(carte('t15-c-enc', 'Encours total', m(CR['encours']),
                 compte(CR['debiteurs'], 'débiteur actif', 'débiteurs actifs'), 'photo', 'ambre', True),
           carte('t15-c-late', 'En retard (+30 j)', m(CR['retard']),
                 "%s de l'encours" % pct(CR['retard'] * 100.0 / CR['encours']), 'photo', 'rouge'),
           carte('t15-c-old', 'Plus ancienne dette', age(AGE[PLUS_VIEILLE[0]]),
                 '%s · %s' % (PLUS_VIEILLE[1], m(RESTE[PLUS_VIEILLE[0]])), 'photo'),
           carte('t15-c-delai', 'Délai moyen de remboursement', jours(CR['delai']),
                 compte(CR['reglees'], 'ardoise réglée', 'ardoises réglées'), 'photo'))
    + rangee(carte('t15-c-rec', 'Recouvré', m(CR['recouvre']),
                   compte(len(CR['remb']), 'remboursement', 'remboursements'), 'per', 'vert',
                   delta=ecart(CR['d_rec'], PREC)),
             carte('t15-c-new', 'Nouvelles ardoises', m(CR['nouv']),
                   compte(CR['nb_nouv'], 'ardoise ouverte', 'ardoises ouvertes'), 'per', 'ambre',
                   delta=ecart(CR['d_nouv'], PREC, hausse_mauvaise=True)),
             carte('t15-c-flux', 'Flux net', FLUX_NET, PHRASE_FLUX, 'per', 'teal'),
             carte('t15-c-taux', 'Taux de recouvrement', pct(CR['taux']),
                   'ardoise moyenne %s' % m(CR['encours'] / float(CR['debiteurs'])), 'per')))
_MAX_AG = max(1, max(x[2] for x in AGING))
BALANCE = ''.join(hbar(x[1], max(2, x[2] * 100.0 / _MAX_AG), x[4], ms(x[2]), compte(x[3], 'ardoise', 'ardoises'))
                  for x in AGING)
SPARK = ('<svg viewBox="0 0 520 120" class="t15-spark"><polyline points="%s" fill="none" stroke="#854F0B" '
         'stroke-width="2.5"/></svg>'
         % ' '.join('%.1f,%.1f' % (15 + i * 490 / 6.0 + 490 / 12.0, 105 - v / float(max(ENCOURS)) * 90) for i, v in enumerate(ENCOURS)))
# Âge en jours entiers (fmtAge), pastille rouge au-delà de 60 j (direction_dashboard.xml:508-524).
TOP_DEB = mini([(None, a[1], m(RESTE[a[0]]), pill(age(AGE[a[0]]), AGE[a[0]] > 60)) for a in TOP], 't15-c-top-t')
# Derniers remboursements de la période, date en jj/mm/aaaa (fmtDate, js:143-148).
DERNIERS = mini([(None, r[2], m(r[5]), e('%s · %s' % (r[3], date_fr(r[0])))) for r in CR['remb'][:5]])
CREDIT_PANNEAUX = ('<div class="t15-row">%s%s</div>'
                   % (panneau('Balance âgée clients', 'POS Crédit',
                              BALANCE + '<h3 class="t15-mt">Encours — 6 mois (fin de mois)</h3>' + SPARK
                              + '<div class="t15-legend">%s → %s · dernier point : %s</div>'
                              % (e(MOIS[0]), e(MOIS[-1]), m(ENCOURS[-1])), 't15-c-aging'),
                      panneau('Top débiteurs', 'photo', TOP_DEB + '<h3 class="t15-mt">Derniers remboursements'
                              '<span class="t15-src">période</span></h3>' + DERNIERS
                              + '<span class="t15-drill">Ouvrir POS Crédit ↗</span>', 't15-c-top')))
VUE_CREDIT = ('<div class="vue t15-pane" id="t15-b-credit"><div class="t15-defil" id="t15-credit-defil" '
              'data-layout-allow-overflow data-layout-allow-occlusion>%s%s%s%s</div></div>'
              % (barre('ORIGINE', chip('t15-o-tout', 'Toutes', True) + chip('t15-o-pos', 'Point de vente')
                       + chip('t15-o-sale', 'Ventes / factures')),
                 sect('CRÉDIT CLIENTS — ARDOISES'), CREDIT_KPI, CREDIT_PANNEAUX))

# -- onglet À traiter (direction_dashboard.xml:801-841) --
VUE_TODO = ('<div class="vue t15-pane" id="t15-b-todo"><div class="t15-defil">%s<div class="t15-row t15-wrap">%s</div>'
            '<div class="t15-legend t15-pad">Chaque ligne ouvre le tableau de bord spécialisé correspondant.</div>'
            '</div></div>'
            % (sect('À TRAITER — LA LISTE DU GÉRANT (%s)' % compte(NB_ACTIONS, 'action', 'actions')),
               ''.join(panneau(titre, source, mini([(i, lib, mt, e(h)) for i, lib, mt, h in lignes]), ident, prio)
                       for ident, titre, source, prio, lignes in SECTIONS)))

COCKPIT = vue_libre('t15-cockpit', TOP_COCKPIT + '<div class="t15-corps" id="t15-corps">%s%s%s</div>'
                    % (VUE_ENSEMBLE, VUE_CREDIT, VUE_TODO), initiale=True, fond='tdb')


# ------------------------------------------- « Direction — Activité par pôle » --
def ek(ident, libelle, valeur, sous, accent=None, delta=None, aide=False):
    """Une carte de l'activité par pôle (dashboard.xml:4-16, kpi_card.js) ; ``delta`` : (texte, genre)."""
    classes = 't15-ek' + (' t15-ek-mega t15-ea-' + accent if accent else '')
    a = '<span class="t15-ek-help" id="%s-aide">?</span>' % ident if aide else ''
    d = '<div class="t15-ek-d %s">%s</div>' % (delta[1], e(delta[0])) if delta else ''
    return ('<div class="%s" id="%s"><div class="t15-ek-l">%s%s</div><div class="t15-ek-v" id="%s-v">%s</div>%s'
            '<div class="t15-ek-s">%s</div></div>' % (classes, ident, e(libelle), a, ident, e(valeur), d, e(sous)))


# deltaLabel par défaut « vs N-1 » ; « vs même date N-1 » pour le rythme du mois (kpi_card.js:22-33,
# dashboard.xml:99-104).
N1, N1_DATE = 'vs N-1', 'vs même date N-1'
# L'infobulle du « ? » : la phrase de KPI_HINTS (exec_dashboard.py:37-39).
TIP_PACE = ('<div class="infobulle masque t15-tip" id="t15-tip-pace" data-layout-allow-overlap '
            'data-layout-allow-occlusion>Rythme du mois (pace) : nuitées déjà réservées pour le mois en cours, comparées '
            'à celles qui l\'étaient à la même date l\'an dernier.</div>')
# Les chiffres de l'activité par pôle de la présentation (c6_direction.py), hors taxes comme le cockpit : les
# nuitées (8 055 000, le chiffre du cockpit), la restauration (3 120 000 ; panier 3 120 000 / 128 = 24 375) et
# 46 prestations réalisées (1 240 000) = 12 415 000 FCFA ; parts arrondies à une décimale et triées
# (_mix_rows, exec_dashboard.py:74-92), écrites par fmtPct à une décimale fixe (utils.js:11-19).
PRESTATIONS, NB_PRESTATIONS = 1240000, 46
MIX = [('Hébergement', '#714B67', CA_NUITS), ('Restauration & boutique', '#185FA5', CA),
       ('Prestations', '#0F6E56', PRESTATIONS)]
TOTAL_EXEC = sum(x[2] for x in MIX)
MIX = sorted([x + (pct(round(x[2] * 100.0 / TOTAL_EXEC, 1)),) for x in MIX], key=lambda x: -x[2])
assert TOTAL_EXEC == 12415000 and [x[3] for x in MIX] == ['64,9\xa0%', '25,1\xa0%', '10,0\xa0%']
# Points fidélité émis : les mouvements datés du 01 au 14/10 (_loyalty_points, exec_dashboard.py:203-211), un point
# par tranche de 1 000 FCFA (aite_loyalty, _points_for, comme t11_fidelite.py). Un folio est crédité quand il est
# facturé ou payé, sur tout son montant hors taxe de séjour et hors lignes déjà créditées à leur source — notes de
# chambre, prestations reportées (hooks.py:78-130, ECARTS.md n° 28). Le jeu ne détaille pas les folios facturés
# du 01 au 14/10 : on y compte autant de nuitées que de nuitées vendues (8 055 000 FCFA, 8 055 points ; les nuitées
# de fin septembre des séjours partis en octobre compensent celles des 13 séjours encore en cours le 14 au matin,
# t01_reception.py), plus les prestations réalisées, créditées à leur source (1 240), et les tickets réglés par un
# client identifié (environ 600 000 FCFA, 600 points) : 9 895 points.
POINTS = CA_NUITS // 1000 + PRESTATIONS // 1000 + 600
assert POINTS == 9895


def anneau_mix():
    total = float(TOTAL_EXEC)
    r, c = 80, 2 * 3.14159265 * 80
    debut, arcs = 0.0, []
    for _, coul, v, _ in MIX:
        lg = c * v / total
        arcs.append('<circle r="%d" cx="110" cy="110" fill="none" stroke="%s" stroke-width="56" stroke-dasharray="%.1f %.1f" '
                    'stroke-dashoffset="%.1f"/>' % (r, coul, lg, c - lg, -debut))
        debut += lg
    leg = ''.join('<div><i style="background:%s"></i>%s</div>' % (coul, e(n)) for n, coul, _, _ in MIX)
    # mixLine : « <montant> · <part> » (exec_dashboard_view.js:141-143)
    liste = ''.join('<div class="t15-mixrow"><i style="background:%s"></i><span>%s</span><b>%s · %s</b></div>'
                    % (coul, e(n), e(m(v)), e(p)) for n, coul, v, p in MIX)
    return ('<div class="t15-mixbox"><svg viewBox="0 0 220 220" class="t15-ring"><g transform="rotate(-90 110 110)">%s'
            '</g></svg><div class="t15-mixleg">%s</div></div><div class="t15-mixlist">%s</div>'
            % (''.join(arcs), leg, liste))


# Évolution mensuelle (get_evolution, exec_dashboard.py:296-320), en millions de FCFA : hébergement nuit par nuit
# sur le mois entier — octobre compte donc les nuitées déjà réservées jusqu'au 31, celles du rythme du mois (412 à
# 45 000 FCFA) —, restauration & boutique (les mois de t12_ventes.py, EVO_TOUT ; octobre : du 01 au 13), prestations
# réalisées (octobre : du 01 au 14). Libellés monthLabel « mai 26 » … « oct. 26 » (utils.js:91-99), graduations
# kTick « 20 M » (exec_dashboard_view.js:172-183). Chart.js (4.4.1 dans Odoo 18) choisit seul le pas de l'axe :
# au plus 11 graduations dans la boîte de 280 px (.aed-chartbox-tall), donc un pas « rond » de 18,5 M / 10 → 2 M,
# de 0 à 20 M.
_HEB = [14.2, 13.6, 16.9, 17.8, 16.4, PACE * ADR / 1e6]
_PRE = [2.1, 2.0, 2.6, 2.8, 2.4, PRESTATIONS / 1e6]
EVO = list(zip(_HEB, [x[1] / 1e6 for x in t12_ventes.EVO_TOUT], _PRE))
EVO_LAB = [mois_abrege(mo, 2026) for mo in range(5, 11)]
assert EVO_LAB[-2:] == ['sept. 26', 'oct. 26'] and max(max(x) for x in EVO) < 20


def evolution():
    groupes = ''.join('<div class="t15-evg"><div class="t15-evb">%s</div><span>%s</span></div>'
                      % (''.join('<i style="height:%.1f%%;background:%s"></i>' % (v / 20.0 * 100, coul)
                                 for v, coul in zip(vals, ('#714B67', '#185FA5', '#0F6E56'))), e(lab))
                      for vals, lab in zip(EVO, EVO_LAB))
    axe = ''.join('<span>%s</span>' % (('%d\xa0M' % k) if k else '0') for k in range(20, -1, -2))
    return ('<div class="t15-evo"><div class="t15-axe">%s</div><div class="t15-evz">%s</div></div>'
            '<div class="t15-legend t15-evleg"><i class="t15-dot" style="background:#714B67"></i>Hébergement'
            '<i class="t15-dot" style="background:#185FA5"></i>Restauration &amp; boutique'
            '<i class="t15-dot" style="background:#0F6E56"></i>Prestations</div>' % (axe, groupes))


EXEC = vue_libre('t15-exec', '<div class="t15-x" id="t15-exec-defil" data-layout-allow-overflow '
                 'data-layout-allow-occlusion>%s</div>' % ''.join([
                     '<div class="t15-xtop" id="t15-x-titre"><div class="t15-xtitre">Direction — Activité par pôle</div>'
                     '<div class="t15-xsous">Hébergement · Restauration &amp; boutique · Prestations</div></div>',
                     '<div class="t15-xfiltre"><span class="t15-xlab">Période</span><span class="t15-xchip on">Ce mois</span>'
                     '<span class="t15-xchip">Ce trimestre</span><span class="t15-xchip">Cette année</span>'
                     '<span class="t15-xesp"></span><span class="t15-xlab t15-xdu">Du</span>%s<span class="t15-xlab t15-xdu">'
                     'au</span>%s</div>' % (date_in('t15-xdu', date_fr(DU)), date_in('t15-xau', date_fr(AUJ))),
                     '<div class="t15-xg4">%s</div>' % ''.join([
                         ek('t15-e-tot', "Chiffre d'affaires total", m(TOTAL_EXEC),
                            'Du %s au %s' % (date_fr(DU), date_fr(AUJ)), 'primary'),
                         ek('t15-e-heb', 'Hébergement', m(CA_NUITS),
                            'Nuitées HT, nuit par nuit · occupation %s · prix moyen %s / nuit' % (pct(OCC), m(ADR)),
                            'primary'),
                         ek('t15-e-pos', 'Restauration & boutique', m(CA),
                            'HT · %s · panier %s' % (compte(TICKETS, 'ticket', 'tickets'), m(CA / float(TICKETS))), 'info'),
                         ek('t15-e-pre', 'Prestations', m(PRESTATIONS),
                            compte(NB_PRESTATIONS, 'prestation réalisée', 'prestations réalisées'), 'teal')]),
                     '<div class="t15-xsect">Hébergement — indicateurs de performance <span>écarts vs même période N-1'
                     '</span></div>',
                     '<div class="t15-xg5" id="t15-e-perf">%s</div>' % ''.join([
                         ek('t15-e-occ', "Taux d'occupation", pct(OCC), compte(NUITS, 'nuitée vendue', 'nuitées vendues'),
                            delta=ecart(D_OCC, N1), aide=True),
                         ek('t15-e-adr', 'Prix moyen par nuit (ADR)', m(ADR), 'CA hébergement ÷ nuitées vendues',
                            delta=ecart(D_ADR, N1), aide=True),
                         ek('t15-e-revpar', 'Revenu par chambre disponible (RevPAR)', m(REVPAR),
                            'par chambre disponible, vendue ou non', delta=ecart(D_REVPAR, N1), aide=True),
                         ek('t15-e-pick', 'Réservations récentes (pickup)', compte(PICKUP, 'nuitée', 'nuitées'),
                            '%s ces 7 derniers jours pour les 30 prochains'
                            % compte(PICKUP_RES, 'réservation prise', 'réservations prises'), aide=True),
                         ek('t15-e-pace', 'Rythme du mois (pace)', compte(PACE, 'nuitée', 'nuitées'),
                            'mois %s · N-1 à la même date : %s' % (mois_abrege(10, 2026), compte(PACE_N1, 'nuitée', 'nuitées')),
                            delta=ecart(D_PACE, N1_DATE), aide=True)]),
                     '<div class="t15-xg4">%s</div>' % ek('t15-e-fid', 'Points fidélité émis', entier(POINTS, tdb=True),
                                                          'Tous services confondus'),
                     '<div class="t15-xsect">Répartition &amp; évolution</div>',
                     '<div class="t15-xg2"><div class="t15-xcard" id="t15-e-mix"><h3>Mix du chiffre d\'affaires par pôle</h3>'
                     '%s</div><div class="t15-xcard"><h3>Évolution mensuelle — 6 mois</h3>%s</div></div>'
                     % (anneau_mix(), evolution()),
                     TIP_PACE]), fond='tdb')

# Le défilement « tout en bas » (mesuré sur la planche) : les deux panneaux de TENDANCES entiers sous la barre VUE,
# et le pied de page lisible au bas du cadre (seuls sa marge et son bord inférieurs dépassent) ; le petit titre
# « TENDANCES » passe sous la barre VUE.
DEFIL_TEND = -498

ECRAN = navigateur(fenetre_muk('t15-app', 'Direction', [], [COCKPIT, EXEC], societe=SOCIETE, initiale=NOM[0],
                               avatar='#854F0B', apps=APPS_PROFIL['direction'], app_active='Direction'))

CSS = """
#t15-app { --t15-muet: #62615C; --t15-muet-fond: #575651; }
#t15-app .o-haut .nom-app { font-size: 23px; }
/* le cockpit (direction_dashboard.scss, à l'échelle de la vidéo) */
#t15-cockpit .fond-tdb, #t15-exec .fond-tdb { color: #46414E; }
.t15-top { position: absolute; left: 14px; right: 14px; top: 10px; }
.t15-head { background: #fff; border: 1px solid rgba(0,0,0,.08); border-radius: 10px; padding: 9px 18px 10px; }
.t15-h1 { font-size: 23px; font-weight: 500; color: #2b2a28; line-height: 1.2; }
.t15-hsub { font-size: 15px; color: var(--t15-muet); margin-top: 2px; }
.t15-bar { margin-top: 7px; height: 46px; background: #fff; border: 1px solid rgba(0,0,0,.08); border-radius: 10px; padding: 0 14px;
  display: flex; align-items: center; gap: 8px; }
.t15-lblf { width: 100px; flex: none; font-size: 13px; letter-spacing: .05em; font-weight: 700; color: var(--t15-muet); }
.t15-chip { height: 32px; padding: 0 14px; border: 1px solid #d8d4cf; border-radius: 16px; font-size: 15px; color: #5c5861; background: #fff;
  display: inline-flex; align-items: center; white-space: nowrap; flex: none; }
.t15-chip.on { background: #714B67; border-color: #714B67; color: #fff; font-weight: 700; }
.t15-dotc { width: 10px; height: 10px; border-radius: 50%; margin-right: 7px; display: inline-block; }
.t15-du { font-size: 14px; color: var(--t15-muet); margin-left: 4px; }
.t15-date { height: 32px; padding: 0 9px 0 11px; border: 1px solid #d8d4cf; border-radius: 8px; font-size: 14.5px; color: #43404a; background: #fff;
  display: inline-flex; align-items: center; gap: 22px; white-space: nowrap; flex: none; }
.t15-cal { width: 16px; height: 16px; display: inline-flex; color: #43404a; }
.t15-cal svg { width: 16px; height: 16px; }
.t15-note { margin-left: auto; font-size: 13.5px; color: var(--t15-muet); font-style: italic; white-space: nowrap; }
.t15-tab { height: 38px; padding: 0 18px; border: 1px solid #d8d4cf; border-radius: 19px; font-size: 16.5px; font-weight: 600; color: #5c5861;
  background: #fff; display: inline-flex; align-items: center; gap: 7px; white-space: nowrap; flex: none; }
.t15-tab.on { background: #714B67; border-color: #714B67; color: #fff; }
.t15-n { font-size: 13px; font-weight: 700; border-radius: 8px; padding: 0 7px; line-height: 19px; background: #f4e3e3; color: #A32D2D; }
.t15-tab.on .t15-n { background: rgba(255,255,255,.16); color: #fff; }
.t15-attente { display: none; }
.t15-tab.vu .t15-attente { display: inline-block; }
.t15-corps { position: absolute; left: 0; right: 0; top: 348px; bottom: 0; overflow: hidden; }
.t15-pane { background: transparent; }
.t15-defil { position: absolute; left: 14px; right: 14px; top: 0; }
.t15-sect { margin: 6px 4px 8px; font-size: 13.5px; letter-spacing: .07em; font-weight: 700; color: var(--t15-muet-fond); white-space: nowrap; }
.t15-row { display: flex; gap: 12px; margin-bottom: 10px; }
.t15-card { flex: 1 1 0; min-width: 0; position: relative; background: #fff; border: 1px solid rgba(0,0,0,.08); border-left: 4px solid #714B67;
  border-radius: 10px; padding: 11px 15px 12px; }
.t15-mega { border-left-width: 5px; }
.t15-al-vert { border-left-color: #3B6D11; } .t15-al-ambre { border-left-color: #854F0B; } .t15-al-rouge { border-left-color: #A32D2D; }
.t15-al-info { border-left-color: #185FA5; } .t15-al-teal { border-left-color: #0F6E56; }
.t15-badge { position: absolute; top: 10px; right: 11px; font-size: 12px; border-radius: 9px; padding: 1px 8px; font-weight: 700; }
.t15-b-photo { background: #eeede8; color: #575651; }
.t15-b-per { background: #f3eff2; color: #714B67; }
.t15-lbl { font-size: 12.5px; letter-spacing: .02em; color: var(--t15-muet); font-weight: 700; text-transform: uppercase; padding-right: 66px;
  line-height: 1.3; }
.t15-help { width: 18px; height: 18px; border-radius: 50%; background: #714B67; color: #fff; font-size: 11.5px; margin-left: 7px;
  display: inline-flex; align-items: center; justify-content: center; letter-spacing: 0; vertical-align: -3px; }
.t15-val { margin-top: 4px; font-size: 27px; font-weight: 800; color: #46414E; line-height: 1.2; }
.t15-v { white-space: nowrap; }
.t15-mega .t15-val { font-size: 32px; }
/* l'écart, bloc insécable qui passe sous le montant quand la ligne manque de place (direction_dashboard.scss:155-162) */
.t15-delta { display: inline-block; margin-left: 9px; font-size: 15px; font-weight: 700; white-space: nowrap; line-height: 1.4; }
.t15-delta.up { color: #3B6D11; } .t15-delta.down { color: #A32D2D; } .t15-delta.flat { color: var(--t15-muet); }
.t15-sub { margin-top: 3px; font-size: 14.5px; color: var(--t15-muet); line-height: 1.35; }
.t15-panel { flex: 1 1 0; min-width: 0; background: #fff; border: 1px solid rgba(0,0,0,.08); border-radius: 10px; padding: 12px 16px; }
.t15-panel h3 { margin: 0 0 9px; font-size: 15px; font-weight: 600; color: #5c5861; display: flex; align-items: center; gap: 9px; }
.t15-panel h3.t15-mt { margin-top: 12px; }
.t15-src { margin-left: auto; font-size: 12.5px; font-weight: 400; font-style: italic; color: var(--t15-muet); }
.t15-legend { margin-top: 6px; font-size: 13.5px; color: #55525A; }
.t15-dot { display: inline-block; width: 11px; height: 11px; border-radius: 2px; margin: 0 6px 0 16px; vertical-align: -1px; }
.t15-dot:first-child { margin-left: 0; }
.t15-trend { width: 100%; height: 238px; display: block; }
.t15-mhead { display: flex; font-size: 13.5px; font-weight: 700; color: #5c5861; margin-bottom: 6px; }
.t15-mhead span { flex: 1; text-align: center; } .t15-mhead .t15-msp { flex: none; width: 64px; }
.t15-mirror { display: flex; flex-direction: column; gap: 9px; }
.t15-mrow { display: flex; align-items: center; gap: 8px; }
.t15-mlab { width: 64px; text-align: center; font-size: 13.5px; font-weight: 700; color: var(--t15-muet); flex: none; }
.t15-mside { flex: 1; display: flex; align-items: center; }
.t15-mside.t15-left { justify-content: flex-end; }
.t15-mside i { height: 18px; border-radius: 3px; display: block; }
.t15-mval { font-size: 13.5px; color: #5c5861; margin: 0 7px; min-width: 60px; white-space: nowrap; }
.t15-left .t15-mval { text-align: right; }
.t15-hbar { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
.t15-hl { width: 120px; flex: none; font-size: 14.5px; color: #43404a; }
.t15-ht { flex: 1; height: 16px; background: #f5f5f4; border-radius: 3px; overflow: hidden; }
.t15-ht i { display: block; height: 16px; }
.t15-hv { min-width: 120px; text-align: right; font-size: 14px; color: #5c5861; white-space: nowrap; }
.t15-hint { color: var(--t15-muet); margin-left: 5px; }
.t15-spark { width: 100%; height: auto; max-height: 150px; display: block; background: #fbfaf9; border-radius: 6px; }
.t15-mini .t15-tr { display: flex; align-items: center; gap: 10px; min-height: 36px; border-bottom: 1px solid #efedea; font-size: 15px; }
.t15-mini .t15-tr:last-child { border-bottom: 0; }
.t15-td { flex: 1; min-width: 0; color: #43404a; line-height: 1.3; padding: 4px 0; }
.t15-r { font-weight: 700; white-space: nowrap; text-align: right; color: #46414E; }
.t15-age { min-width: 52px; text-align: right; font-size: 14px; color: var(--t15-muet); white-space: nowrap; }
.t15-pill { display: inline-block; border-radius: 9px; padding: 1px 9px; font-size: 13px; font-weight: 700; white-space: nowrap; }
.t15-p-rouge { background: #f4e3e3; color: #A32D2D; } .t15-p-ambre { background: #f5ead6; color: #854F0B; }
.t15-drill { display: inline-block; margin-top: 8px; font-size: 14px; font-weight: 600; color: #714B67; }
.t15-wrap { flex-wrap: wrap; }
.t15-wrap .t15-panel { flex: 1 1 330px; }
.t15-pad { margin: 0 6px; }
.t15-footer { margin-top: 14px; padding: 12px 18px; background: #fff; border: 1px solid rgba(0,0,0,.08); border-radius: 10px;
  font-size: 14.5px; color: var(--t15-muet); line-height: 1.6; }
.t15-tip { width: 470px; font-size: 18px; }
#t15-tip-revpar { left: 944px; top: 233px; width: 560px; }
/* le tableau exécutif (exec_dashboard.scss, à l'échelle de la vidéo) ; le contenu défile sous la barre */
#t15-exec .fond-tdb { overflow: hidden; }
.t15-x { position: absolute; left: 14px; right: 14px; top: 12px; }
.t15-xtop { background: #fff; border: 1px solid rgba(0,0,0,.08); border-radius: 12px; padding: 10px 16px; }
.t15-xtitre { font-size: 23px; font-weight: 700; color: #714B67; line-height: 1.2; }
.t15-xsous { margin-top: 2px; font-size: 15px; color: var(--t15-muet); }
.t15-xfiltre { margin-top: 10px; height: 52px; background: #fff; border: 1px solid rgba(0,0,0,.08); border-radius: 12px; padding: 0 12px;
  display: flex; align-items: center; gap: 7px; }
.t15-xlab { min-width: 100px; font-size: 13.5px; font-weight: 600; letter-spacing: .5px; text-transform: uppercase; color: var(--t15-muet); }
.t15-xdu { min-width: 0; margin: 0 6px 0 14px; }
.t15-xchip { height: 34px; padding: 0 13px; border: 1px solid rgba(0,0,0,.1); border-radius: 8px; font-size: 15px; color: #5f5e5a;
  display: inline-flex; align-items: center; white-space: nowrap; }
.t15-xchip.on { background: #714B67; border-color: #714B67; color: #fff; }
.t15-xesp { flex: 1; }
.t15-xg4, .t15-xg5, .t15-xg2 { display: grid; gap: 10px; margin-top: 10px; }
.t15-xg4 { grid-template-columns: repeat(4, 1fr); } .t15-xg5 { grid-template-columns: repeat(5, 1fr); margin-top: 0; }
.t15-xg2 { grid-template-columns: repeat(2, 1fr); margin-top: 0; }
.t15-ek { min-width: 0; background: #fff; border: 1px solid rgba(0,0,0,.08); border-radius: 12px; padding: 12px 15px; }
.t15-ek-mega { border-left: 4px solid #714B67; }
.t15-ea-info { border-left-color: #185FA5; } .t15-ea-teal { border-left-color: #0F6E56; }
.t15-ek-l { font-size: 13px; font-weight: 600; letter-spacing: .5px; text-transform: uppercase; color: var(--t15-muet); line-height: 1.3; }
.t15-ek-help { width: 18px; height: 18px; border-radius: 50%; background: #714B67; color: #fff; font-size: 12px; margin-left: 7px;
  display: inline-flex; align-items: center; justify-content: center; vertical-align: -3px; letter-spacing: 0; }
.t15-ek-v { margin-top: 6px; font-size: 27px; font-weight: 700; line-height: 1.15; color: #2b2a28; white-space: nowrap; }
.t15-ek-d { margin-top: 5px; font-size: 14px; font-weight: 600; color: #3B6D11; white-space: nowrap; }
.t15-ek-d.down { color: #A32D2D; } .t15-ek-d.flat { color: var(--t15-muet); }
.t15-ek-s { margin-top: 4px; font-size: 13.5px; color: var(--t15-muet); line-height: 1.3; }
.t15-xsect { margin: 15px 4px 8px; font-size: 14px; font-weight: 700; letter-spacing: .6px; text-transform: uppercase; color: var(--t15-muet-fond); }
.t15-xsect span { margin-left: 8px; font-size: 13.5px; font-weight: 400; letter-spacing: 0; text-transform: none; }
.t15-xcard { min-width: 0; background: #fff; border: 1px solid rgba(0,0,0,.08); border-radius: 12px; padding: 12px 16px; height: 300px; }
.t15-xcard h3 { margin: 0 0 8px; font-size: 16px; font-weight: 600; color: #2b2a28; }
.t15-mixbox { display: flex; align-items: center; gap: 40px; padding-left: 90px; }
.t15-ring { width: 190px; height: 190px; flex: none; }
.t15-mixleg div, .t15-mixrow { display: flex; align-items: center; gap: 8px; font-size: 14px; color: #5f5e5a; margin: 5px 0; }
.t15-mixleg i { width: 13px; height: 13px; display: inline-block; }
.t15-mixlist { margin-top: 4px; }
.t15-mixrow { font-size: 15px; margin: 4px 0; }
.t15-mixrow i { width: 11px; height: 11px; border-radius: 50%; display: inline-block; }
.t15-mixrow b { margin-left: auto; font-weight: 400; color: #5f5e5a; }
.t15-evo { display: flex; height: 214px; gap: 8px; }
.t15-axe { display: flex; flex-direction: column; justify-content: space-between; font-size: 12px; color: var(--t15-muet); padding-bottom: 22px; text-align: right; }
.t15-evz { flex: 1; display: flex; border-left: 1px solid #e5e2dd; border-bottom: 1px solid #e5e2dd; margin-bottom: 22px; position: relative; }
.t15-evg { flex: 1; position: relative; }
.t15-evb { position: absolute; left: 14%; right: 14%; top: 0; bottom: 0; display: flex; align-items: flex-end; gap: 3px; }
.t15-evb i { flex: 1; border-radius: 3px 3px 0 0; display: block; }
.t15-evg span { position: absolute; left: 0; right: 0; bottom: -22px; text-align: center; font-size: 12.5px; color: var(--t15-muet); }
.t15-evleg { text-align: center; }
#t15-tip-pace { left: 1036px; top: 446px; }
"""

TUTORIEL = {
    'slug': 't15-direction',
    'profil': 't15_direction',
    'numero': 15,
    'titre': "Cockpit Direction : l'affaire lue d'un coup d'œil",
    'fonction': 'Cockpit Direction',
    'personnage': (NOM, ROLE),
    'accroche': {
        'kicker': 'Le pilotage du gérant',
        'question': "Comment va *vraiment* l'affaire ?",
        'douleurs': [('piles', 'Ventes, ardoises, stock, achats : un écran chacun'),
                     ('cahier', 'Des ardoises qui dorment dans un cahier'),
                     ('pieces', "Du cash qui s'évapore avec l'âge"),
                     ('interrogation', 'RevPAR, pickup, pace : du jargon'),
                     ('graphe', "Et l'an dernier, à la même date ?")],
        'voix': "Comment va vraiment l'affaire ? Ventes, ardoises, stock, achats : un écran chacun. Et des sigles "
                "hôteliers à décoder.",
    },
    'revelation': {
        'promesse': "Ventes, ardoises, stock, achats et hôtel sur une seule page, une liste « À traiter » qui se "
                    "construit seule, et chaque indicateur hôtelier expliqué en une phrase.",
        'voix': "Avec Aïte haousse, le cockpit Direction réunit l'affaire sur une seule page, et dit quoi faire.",
    },
    'temps': ['Lire', 'Creuser', 'Agir', 'Comparer'],
    'app': 't15-app',
    'ecran': ECRAN,
    'css': CSS,
    'vues_initiales': {'odoo': 't15-cockpit', 'corps': 't15-b-vue'},
    'bulles': {
        # espace insécable devant les deux-points : « Rouge » ne reste pas seul en bout de ligne
        'b-risque': 'Ardoises de 30 jours et plus + coulage du stock\xa0: calculé, rien à saisir.',
        'b-filtre': 'Heure et jours ne filtrent que les ventes.',
        'b-todo': 'Chaque ligne ouvre le tableau de bord spécialisé.',
        'b-n1': "Vert\xa0: mieux que l'an dernier. Rouge\xa0: moins bien.",
    },
    'reactions': {
        'r-relance': 'Je sais qui relancer en premier.',
        'r-fin': 'Je sais où creuser.',
    },
    'etapes': [
        {'temps': 0, 'titre': "La santé de l'affaire",
         'texte': 'Le chiffre encaissé, la marge, le cash à risque, et vos ardoises face à vos dettes.',
         'voix': "Mercredi matin, Danielle ouvre Direction. En tête, la santé de l'affaire : le chiffre encaissé et son écart, la "
                 "marge réalisée, l'argent à risque, et ce que vos clients vous doivent face à vos dettes "
                 "fournisseurs.",
         # compter pose une espace insécable entre les milliers (aite-motion.js:68-70) : le montant final reprend
         # l'espace fine de fmtMoney dès la fin du décompte. Les anneaux suivent la voix : le chiffre, la marge,
         # le risque (zoom et bulle), puis la position nette.
         'gestes': [clic('#t15-app-app-direction', d=0.6), compter('#t15-k-ca-v', 0, CA, d=1.2, apres=' FCFA'),
                    curseur('#t15-sante', fx=0.62, fy=-0.22, d=0.6, avec=True),
                    texte('#t15-k-ca-v', m(CA), avec=True, decale=1.22), pause(2.2), anneau('#t15-k-ca', d=1.3),
                    anneau('#t15-k-marge', d=1.2), zoom('#t15-k-risque', s=1.85, d=0.8),
                    bulle('b-risque', '#t15-k-risque', cote='haut', d=2.8), pause(0.5), dezoom(d=0.6),
                    anneau('#t15-k-net', d=1.6)]},
        {'temps': 0, 'titre': 'Le soir du week-end',
         'texte': 'Heure et jours recalculent les ventes ; ardoises, stock et dettes ne bougent pas.',
         'voix': "Et les soirs de fin de semaine ? Soir, dix-huit, vingt-trois heures, puis vendredi et samedi : le chiffre, "
                 "la marge et les tickets se recalculent. Les ardoises, le stock et les dettes ne bougent pas.",
         # les clics tombent sur « Soir… », puis « vendredi et samedi » ; les anneaux de la fin sur « les ardoises,
         # le stock et les dettes » (les cartes de pôle qui ne bougent pas).
         'gestes': [pause(1.4), clic('#t15-h-soir', d=0.6), classe('#t15-h-tout', retirer=['on']),
                    classe('#t15-h-soir', ajouter=['on'], avec=True), clic('#t15-j-4', d=0.5),
                    classe('#t15-j-4', ajouter=['on']), clic('#t15-j-5', d=0.4), classe('#t15-j-5', ajouter=['on']),
                    texte('#t15-k-ca-v', m(CA_SOIR)), texte('#t15-k-ca-d', ecart(D_SOIR, PREC)[0], avec=True),
                    texte('#t15-k-ca-s', 'HT · %s · POS payés / facturés' % compte(TICKETS_SOIR, 'ticket', 'tickets'),
                          avec=True),
                    texte('#t15-k-marge-v', m(MARGE_SOIR), avec=True),
                    texte('#t15-k-marge-s', '%s du CA · CA − coût des ventes' % pct(MARGE_SOIR * 100.0 / CA_SOIR),
                          avec=True),
                    texte('#t15-p-tix-v', entier(TICKETS_SOIR, tdb=True), avec=True),
                    texte('#t15-p-tix-s', 'panier moyen %s' % m(CA_SOIR / float(TICKETS_SOIR)), avec=True),
                    anneau('#t15-k-ca', d=1.3), bulle('b-filtre', '#t15-note-caisse', cote='bas', d=3.2),
                    anneau('#t15-p-tix', d=1.0), anneau('#t15-p-ard', d=0.9), anneau('#t15-p-stock', d=0.9),
                    anneau('#t15-p-four', d=0.9)]},
        {'temps': 1, 'titre': 'Un clic sur un pôle',
         'texte': "La carte « Encours ardoises » ouvre l'onglet Crédit clients.",
         'voix': "Pour creuser, un clic sur une carte de pôle. L'encours des ardoises ouvre l'onglet Crédit clients : "
                 "la balance âgée, l'encours sur six mois, et les débiteurs, du plus gros encours au plus petit.",
         # le clic tombe sur « un clic sur une carte de pôle », l'anneau de la balance âgée sur « la balance âgée,
         # l'encours sur six mois », le zoom sur « et les débiteurs » ; zoom décentré vers le haut (fy) pour ne
         # pas buter sur le bas du navigateur (son coin arrondi restait visible).
         'gestes': [pause(0.8), clic('#t15-p-ard', d=0.7), classe('#t15-tab-vue', retirer=['on']),
                    classe('#t15-tab-credit', ajouter=['on'], avec=True), vue('t15-b-credit', 'corps'),
                    defiler('#t15-credit-defil', -336, d=0.7, avec=True), pause(2.4), anneau('#t15-c-aging', d=2.1),
                    zoom('#t15-c-top-t', s=1.8, fy=0.17, d=0.7),
                    reaction('r-relance', d=2.6), pause(1.9), dezoom(d=0.5)]},
        {'temps': 2, 'titre': 'À traiter : la liste du gérant',
         'texte': 'Relancer, régulariser, payer, commander, renégocier : la liste se construit seule.',
         # « la bière et l'eau qui manquent » : les deux lignes « Commander » (_penalty_rows retient la rupture,
         # Eau minérale 1,5 L, et la référence critique, Bière blonde 65 cl ; t13_stock.py).
         'voix': "Reste à agir. L'onglet À traiter dresse la liste du gérant : relancer les ardoises de trente jours "
                 "et plus, régulariser la facture échue, payer celle qui tombe cette semaine, commander la bière et "
                 "l'eau qui manquent, renégocier une hausse de prix.",
         'gestes': [clic('#t15-tab-todo', d=0.7), classe('#t15-tab-credit', retirer=['on']),
                    classe('#t15-tab-todo', ajouter=['on', 'vu'], avec=True), vue('t15-b-todo', 'corps'), pause(0.3),
                    bulle('b-todo', '#t15-s-four', cote='bas', d=3.0), pause(0.4), anneau('#t15-s-credit', d=2.2),
                    anneau('#t15-s-four', d=1.8), anneau('#t15-r-payer', d=1.6), anneau('#t15-s-stock', d=1.9),
                    anneau('#t15-s-prix', d=1.4)]},
        {'temps': 3, 'titre': 'Six mois, dans les deux sens',
         'texte': "Le chiffre encaissé face aux achats, l'encours des ardoises, et la balance âgée en miroir.",
         'voix': "Retour à la vue d'ensemble. Tout en bas, six mois d'un coup d'œil : le chiffre encaissé face aux "
                 "achats, et l'encours des ardoises. À côté, la balance âgée en miroir : ce que vos clients vous "
                 "doivent, face à ce que vous devez à vos fournisseurs.",
         'gestes': [clic('#t15-tab-vue', d=0.7), classe('#t15-tab-todo', retirer=['on']),
                    classe('#t15-tab-vue', ajouter=['on'], avec=True), vue('t15-b-vue', 'corps'),
                    defiler('#t15-vue-defil', DEFIL_TEND, d=1.0), pause(0.2),
                    curseur('#t15-tend-ca', fx=0.5, fy=0.55, d=0.6), anneau('#t15-tend-ca', d=3.0),
                    zoom('#t15-tend-mir', s=1.45, fy=0.0, d=0.8), anneau('#t15-tend-mir', d=3.2), pause(1.0),
                    dezoom(d=0.6)]},
        {'temps': 3, 'titre': "L'hôtel face à l'an dernier",
         'texte': "Occupation, prix moyen, revenu par chambre : l'écart N-1 en couleur, et un « ? » qui explique.",
         'voix': "Plus haut, côté hôtel. Occupation, prix moyen par nuit, revenu par chambre disponible : chaque carte "
                 "se compare à la même période l'an dernier, et son point d'interrogation l'explique en une phrase.",
         'gestes': [defiler('#t15-vue-defil', -110, d=0.9), anneau('#t15-x-occ', d=1.2), anneau('#t15-x-adr', d=1.2),
                    anneau('#t15-x-revpar', d=1.4), bulle('b-n1', '#t15-x-revpar', cote='haut', d=2.8), pause(1.6),
                    curseur('#t15-x-revpar-aide', d=0.6), montrer('#t15-tip-revpar', d=0.3, y=6), pause(2.4),
                    cacher('#t15-tip-revpar', d=0.2), curseur('#t15-x-revpar', fx=0.6, fy=-0.25, d=0.5)]},
        # voix : « pikeup », « ritme » et « peïsse » pour Kokoro (ecouter.py lisait « rythme » en anglais et
        # « pace » comme « passe ») ; l'écran garde les libellés du code, le titre les libellés français (n° 42).
        # Zoom : la caméra vise sous la rangée (fy=2,0) pour garder le haut du cadre sur la barre MuK, sans la
        # barre grise ni le coin du navigateur ; l'infobulle du rythme du mois tombe sur « Le ritme du mois ».
        {'temps': 3, 'titre': 'Réservations récentes et rythme du mois',
         'texte': 'Une carte Hébergement ouvre « Direction — Activité par pôle » : réservations récentes et rythme du '
                  'mois.',
         'voix': "Un clic sur une carte de l'hôtel ouvre l'activité par pôle. Les réservations récentes, le pikeup : les "
                 "nuitées prises ces sept derniers jours pour les trente prochains. Le ritme du mois, le peïsse : les "
                 "nuitées déjà réservées pour le mois, face à l'an dernier à la même date.",
         'gestes': [clic('#t15-x-revpar', d=0.8), vue('t15-exec'), anneau('#t15-x-titre', d=1.1),
                    defiler('#t15-exec-defil', -276, d=0.7), zoom('#t15-e-pace', s=1.5, fx=0.0, fy=2.0, d=0.7),
                    anneau('#t15-e-pick', d=3.0), pause(0.3),
                    curseur('#t15-e-pace-aide', d=0.6), montrer('#t15-tip-pace', d=0.3, y=6), pause(3.6),
                    cacher('#t15-tip-pace', d=0.2), curseur('#t15-e-pace', fx=0.5, fy=1.6, d=0.5),
                    reaction('r-fin', d=2.4), pause(1.3)]},
    ],
    'resultats': {
        'titre': 'Lire, creuser, agir, comparer',
        'cartes': [
            {'valeur': '6', 'compter': 6, 'unite': 'onglets', 'icone': 'liste',
             'texte': "vue d'ensemble, ventes, crédit, stock, achats, à traiter : une seule page"},
            {'valeur': '4', 'compter': 4, 'unite': 'tableaux de bord', 'icone': 'piles',
             'texte': 'relus par le cockpit : ventes, crédit clients, stock, achats, sans ressaisie'},
            {'valeur': '6', 'compter': 6, 'unite': "phrases d'explication", 'icone': 'interrogation',
             'texte': 'occupation, prix moyen, revenu par chambre, réservations récentes, rythme du mois, écart N-1'},
        ],
        'voix': "Six onglets sur une seule page, quatre tableaux de bord relus sans ressaisie, six phrases pour "
                "comprendre l'hôtel : la direction lit, puis agit.",
    },
    'cta': {
        'appel': 'Demandez votre démonstration',
        'suivant': "La présentation complète d'AITE HOUSE",
        'voix': "Aïte haousse, par Aïte Consulting. Demandez votre démonstration, et retrouvez la présentation "
                "complète sur notre chaîne.",
    },
    'vignette': {'etape': 1, 'apres': 3.0},
}
