# -*- coding: utf-8 -*-
"""Tutoriel 15 — Cockpit Direction : l'affaire lue d'un coup d'œil.

La directrice (Danielle Eyenga, demo.POSTES['direction']) ouvre l'application
Direction : la santé de l'affaire, l'essentiel par pôle, les filtres (le soir
du week-end), un clic sur une carte de pôle qui ouvre son onglet (Crédit
clients), la liste « À traiter », la rangée Hébergement comparée à l'an
dernier, puis un clic sur une carte de l'hôtel qui ouvre le tableau de bord
exécutif (pickup, pace).

Profil rejoué : comptes demo.direction de la base MuK (Point de Vente :
Administrateur, Gestion hôtelière : Responsable…). Le menu racine
« Direction » est réservé à point_of_sale.group_pos_manager
(addons/aite_direction_dashboard/views/direction_views.xml:8-12) ; il n'a pas
de sous-menu : la barre du haut ne porte que le nom de l'application
(ref_muk/060-direction.png, 330-direction-accueil.png). Applications de la
barre MuK : ecrans.APPS_PROFIL['direction'] (relevées sur 330-direction-
accueil.png). Un clic sur une carte Hébergement ouvre le tableau exécutif
dans la même application « Direction », sans fil d'Ariane (vérifié sur la
base MuK : barre « Direction », aucun .breadcrumb).

Sources des libellés (relevés mot pour mot) :

- Cockpit, gabarit addons/aite_direction_dashboard/static/src/xml/
  direction_dashboard.xml : carte (badge « période » / « photo », « ? »
  aria-label « Explication », écart dans la ligne de la valeur) :4-26 ;
  titre « Direction — Vue consolidée » et « POS · Crédit clients · Stock ·
  Achats — <société> » :136-142 ; PÉRIODE, Du, au, Appliquer :145-162 ;
  CAISSE, « Toutes les caisses », note « caisse, heure et jours filtrent les
  données de vente » :163-180 ; HEURE :181-189 ; JOUR, « multi-sélection —
  aucun = tous » :190-199 ; VUE et pastilles des onglets :201-213 ; SANTÉ DE
  L'AFFAIRE et ses quatre cartes (accents vert, teal, rouge, info) :222-242 ;
  « L'ESSENTIEL PAR PÔLE — cliquer une carte ouvre l'onglet » et ses cartes
  cliquables :243-268 ; « HÉBERGEMENT — écarts vs même période N-1 ; cliquer
  une carte ouvre le tableau de bord exécutif » :269-302 ; TENDANCES, « CA vs
  Achats — 6 mois, et encours d'ardoises », « POS · Achats · Crédit »,
  « Balance âgée en miroir », « Crédit · Achats » :303-319 ; graphique et
  légende :42-79 ; miroir, « Vos clients vous doivent », « Vous devez aux
  fournisseurs », légende :81-107 ; onglet Crédit clients (ORIGINE, Toutes,
  POS, Ventes / factures, CRÉDIT CLIENTS — ARDOISES, huit cartes, « Balance
  âgée clients », « Crédit v2 », « cl. », « Encours — 6 mois (fin de mois) »,
  « Top débiteurs », pastille rouge au-delà de 60 j, « Derniers
  remboursements », « Ouvrir Crédit clients ↗ ») :411-535 ; onglet À traiter
  (« À TRAITER — LA LISTE DU GÉRANT (<n> actions) », URGENT / À SURVEILLER,
  « Chaque ligne ouvre le tableau de bord spécialisé correspondant. ») :783-
  824. Couleurs et tailles : static/src/scss/direction_dashboard.scss
  (fond #e8e6e0, puces violettes, liserés, badges, « ? ») :7-157.
- static/src/js/direction_dashboard.js : HEURE, JOUR, PÉRIODE, onglets
  :23-46 ; « Ce mois » calculé en heure locale puis converti par
  toISOString :57-78 (voir écart 1) ; formats fmtMoney (espaces fines
  remplacées), fmtPct « 56,0 % », fmtDelta « ▲ +9,4 % » :81-94 ; miroir
  (tranches et couleurs) :184-212 ; phrase de la position nette :288-298 ;
  sous-titres pace et pickup :300-311 ; balance âgée clients et couleur par
  tranche :369-386 (écart 4) ; « Flux net » :407-412 ; pastilles des onglets
  :494-503 ; heure et jours ne rechargent que la vue d'ensemble et les
  ventes :575-588 ; ouverture du tableau exécutif :316-321.
- models/direction_dashboard.py : orchestrateur des quatre moteurs :5-11,
  :329-332 ; cash à risque :74-77 ; position nette :79-90 ; liste d'actions
  (« Relancer %s », « %d j », « Régulariser %d facture(s) échue(s) »,
  « échu », « Commander %s », « perd / jour », « Lancer la commande suggérée
  (%d réfs) », « sous seuil », « Écarts d'inventaire négatifs »,
  « contrôler », « Renégocier %s », « %+.0f %% · %s ») :219-314 et
  get_actions :570-606 (débiteurs de plus de 30 j pris dans les six plus
  gros encours) ; tranches horaires :33-38 ; tuile Hébergement :373-410 ;
  badges :469-474 ; courbes à rebours :149-166 ; alignement des tendances
  :168-191 (écart 3).
- Crédit : addons/aite_pos_credit/models/pos_credit.py:27-28 (30 et 60
  jours) ; pos_credit_dashboard.py get_kpis :120-242 (encours, retard,
  plus ancienne ardoise, flux net « nouveaux − recouvré »), get_aging
  :255-289 (tranches « 0–30 j », « 30–60 j », « 60–90 j », « +90 j »),
  get_top_debtors :382-428 (tri par encours), get_recent_payments :509-529
  (date en AAAA-MM-JJ) ; moyens de paiement pos_credit_payment.py:49-56
  (« MTN Mobile Money », « Orange Money », « Espèces »).
- Tableau exécutif, gabarit addons/aite_exec_dashboard/static/src/xml/
  dashboard.xml:4-136 (« Direction — Vue consolidée », « Hébergement ·
  Restauration & boutique · Prestations », Période, Du, au, quatre cartes,
  « Période <du> → <au> », « Hébergement — indicateurs de performance »,
  « écarts vs même période N-1 », cinq cartes et leurs « ? », « Points
  fidélité émis », « Tous services confondus », « Répartition &
  évolution », « Mix du chiffre d'affaires par pôle », « Évolution
  mensuelle — 6 mois ») ; static/src/js/components/kpi_card.js:22-37
  (« vs N-1 », écart sous la valeur) ; static/src/js/views/
  exec_dashboard_view.js:134-153 (« <montant> · <x %> », pickupSub,
  paceSub), :212-237 (graduations « k ») ; static/src/js/services/
  utils.js:5-57 (fmtMoney sans remplacement des espaces fines, fmtPct
  « 64 % », « Ce mois / Ce trimestre / Cette année », mois « oct 26 ») ;
  static/src/scss/exec_dashboard.scss (titre violet, liserés, « teal »
  sans classe) ; models/exec_dashboard.py : phrases d'explication
  KPI_HINTS :20-38, couleurs et libellés des pôles :8-18, parts arrondies
  à une décimale et triées :66-82 ; menu Hôtel → Direction :
  views/exec_menus.xml:3-8.
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
— guide du tableau exécutif, Hôtel → Direction, montré à l'étape 6 ; sa
promesse des « trente secondes » n'est pas reprise : le titre dit « d'un
coup d'œil », une seule page, direction_dashboard.js:39-46) ;
kicker — plaquette p. 16 (« Le pilotage du gérant ») ; « qui relancer en
premier » — plaquette p. 10 et tri par encours décroissant
(pos_credit_dashboard.py:427) ; pickup et pace dits par la voix —
exec_dashboard.py:31-34 ; bénéfices et résultats — direction_dashboard.js
:39-46 (six onglets), direction_dashboard.py:5-11 (quatre moteurs relus) et
addons/aite_direction_dashboard/tests/test_dashboard_api.py:84-124 (mêmes
chiffres que les tableaux spécialisés), exec_dashboard.py:20-38 (six
phrases d'explication).

Données : demo.py (Complexe Hôtelier — Démo, Démo Hôtellerie SARL, ardoises
ARD/0017 à ARD/0042 : encours 150 000 FCFA, 101 500 au-delà de 30 jours,
âges au 14/10/2026) ; caisses « Bar de la terrasse » et « Restaurant »,
fournisseurs et chiffres de l'hôtel repris de scenarios/c6_direction.py ;
Christian Atangana, Nadège Owona et Rodrigue Manga (ardoises soldées dans
la période) sont des noms fictifs ajoutés. Le jour rejoué est le
14/10/2026, navigateur en français à Douala. Les chiffres se tiennent :
CA des nuitées = 192 nuitées × 45 000 = 8 640 000 ; 20 chambres × 15 jours
= 300 nuitées disponibles, d'où 64,0 % et RevPAR 28 800 = 45 000 × 64 % ;
cash à risque = 101 500 + 41 500 ; position nette = 150 000 − 1 280 000 ;
restauration TTC = 3 120 000 HT × 1,1925 (écart 2) ; mix trié et arrondi
comme _mix_rows. Top débiteurs : à encours égal (30 000), Brigitte
Essomba (ARD/0039, plus récente) sort avant Sylvie Mbarga (ARD/0017) — tri
stable sur des ardoises lues en create_date desc (pos_credit.py:23).

Cadrages choisis pour ne pas filmer les défauts du produit (non corrigés :
les modules ne sont pas modifiés par les vidéos) :
- étape 3 : défilement dès l'arrivée sur l'onglet Crédit clients, la
  rangée Recouvré / Nouveaux / Flux net (phrase inversée, écart 5) ne
  reste pas lisible ; la voix ne commente que la balance âgée, la courbe
  et le Top débiteurs ;
- étape 5 : défilement court (-60) qui pose la rangée Hébergement au bas
  du cadre : TENDANCES (barres du CA à zéro, miroir fournisseurs à 0,
  écart 3) n'est jamais à l'écran ; pas de zoom (en zoom, la légende de
  l'étape recouvrirait la rangée) ;
- étape 6 : le tableau exécutif défile aussitôt ouvert (les quatre cartes
  de pôle et « Période 2026-09-30 → … » sortent du cadre), puis zoom sur
  pickup / pace : ni le total ni « Hébergement » / « Restauration &
  boutique » (écart 2) ne restent lisibles, la voix ne les cite pas ;
- zooms des étapes 1 et 3 assez serrés (1,85 et 1,8) pour que le champ
  « Du 30/09/2026 » (écart 1) ne soit jamais en gros plan.

Captures de référence (modèle visuel, jamais incrustées) : ref_muk/060-
direction(-pleine).png, 053-h-tel-direction(-pleine).png, 330-direction-
accueil.png, 000-accueil.png ; captures prises en lecture seule sur la base
MuK (onglets À traiter et Crédit clients, tendances, tableau exécutif ouvert
depuis la carte RevPAR) ; docs/captures_uat/r4-direction-06 et -07 ;
captures/40_tableau_executif_indicateurs.png, 41_cockpit_direction_
hebergement.png. Chapitre déjà rejoué dans la présentation :
scenarios/c6_direction.py (ses écarts « vs N-1 » dans le cockpit et le
signe « − » des montants négatifs ne sont pas repris : le cockpit n'ajoute
pas « vs N-1 » et toLocaleString écrit un trait d'union).

Écarts rejoués tels quels (voir le rapport) :
1. « Ce mois » démarre la veille du 1er à Douala : « Du 30/09/2026 » dans
   le cockpit, « Période 2026-09-30 → 2026-10-14 » dans l'exécutif
   (direction_dashboard.js:57-78, utils.js:36-49) ; date ISO dans
   l'exécutif et dans « Derniers remboursements ».
2. Deux chiffres d'hébergement et de restauration pour la même période :
   « CA des nuitées (HT) » 8 640 000 (nuit par nuit, direction_dashboard.py
   :399) contre « Hébergement » 7 912 400 (folios TTC datés au départ,
   exec_dashboard.py:142-161, :221) ; CA encaissé HT 3 120 000 (price_subtotal)
   contre « Restauration & boutique » TTC 3 720 600 (amount_total,
   exec_dashboard.py:247).
3. Graphique « CA vs Achats » : les barres du CA restent à zéro (clés de
   mois différentes) ; côté fournisseurs du miroir à 0 sur les quatre
   tranches (clés amount / date / planned absentes) ; aucune ligne « Payer
   <fournisseur> » dans « À traiter ».
4. Balance âgée clients : couleurs décalées d'une tranche (« 30–60 j » en
   vert, « +90 j » en ocre) ; « cl. » compte des ardoises.
5. « Flux net » : le moteur calcule nouveaux − recouvré
   (pos_credit_dashboard.py:177) mais le cockpit écrit « recouvré −
   nouveaux » et annonce « l'encours monte » quand il baisse
   (direction_dashboard.xml:461-465, js:407-412) ; « Délai moyen de
   remboursement » affiche le nombre brut, sans arrondi
   (direction_dashboard.xml:447 ; ici une moyenne entière).
6. Pourcentages : « 64,0 % » dans le cockpit, « 64 % » dans l'exécutif ;
   carte « Prestations » sans liseré teal (dashboard.xml:70, classe absente
   de exec_dashboard.scss:195-199) ; espaces fines des montants de
   l'exécutif ; même titre « Direction — Vue consolidée » pour les deux
   écrans ; phrase « vos clients vous financent » inversée quand le solde est
   positif (js:293-297, non rejouée ici : le solde est négatif).
7. Anglais résiduel (règle 6 du CLAUDE.md) : « RevPAR », « Pickup 7 j →
   30 j », « Pace du mois », infobulles « RevPAR : … » et « Pace : … »
   (exec_dashboard.py:28-34, dashboard.xml:95-104) ; rejoué tel quel. La
   douleur « RevPAR, pickup, pace : du jargon » reste vraie : la phrase
   explique le sigle, mais le sigle reste en tête.
"""

import demo
from ecrans import APPS_PROFIL, ICONES, e, fenetre_muk, icone, navigateur, vue_libre
from marketing import bulle, dezoom, reaction, zoom
from moteur import anneau, cacher, classe, clic, compter, curseur, defiler, montrer, pause, texte, vue

NOM, ROLE = demo.POSTES['direction']
SOCIETE = demo.SOCIETE
FCFA = ' FCFA'
NNBSP = ' '          # l'espace fine que toLocaleString pose dans les montants de l'exécutif

CAL = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3.5" y="5" width="17" '
       'height="15.5" rx="1.5"/><path d="M3.5 10h17M8 3v4M16 3v4"/></svg>')


def ex(montant):
    """Un montant du tableau exécutif : fmtMoney sans remplacement des espaces fines (utils.js:5-9)."""
    return montant.replace(' ', NNBSP) + FCFA


# ------------------------------------------------------------ composants --
def chip(ident, libelle, on=False, point=None):
    p = '<i class="t15-dotc" style="background:%s"></i>' % point if point else ''
    return '<span class="t15-chip%s" id="%s">%s%s</span>' % (' on' if on else '', ident, p, e(libelle))


def barre(libelle, contenu, note=None, ident_note=None):
    n = '<span class="t15-note"%s>%s</span>' % (' id="%s"' % ident_note if ident_note else '', e(note)) if note else ''
    return '<div class="t15-bar"><span class="t15-lblf">%s</span>%s%s</div>' % (e(libelle), contenu, n)


def date_in(ident, valeur):
    return '<span class="t15-date" id="%s">%s<span class="t15-cal">%s</span></span>' % (ident, e(valeur), CAL)


def carte(ident, libelle, valeur, sous=None, badge=None, accent=None, mega=False, delta=None, aide=False,
          cliquable=False):
    """Une carte du cockpit (KpiCard, direction_dashboard.xml:4-26)."""
    classes = 't15-card' + (' t15-mega' if mega else '') + (' t15-al-' + accent if accent else '')
    b = ('<span class="t15-badge t15-b-%s">%s</span>' % (badge, 'période' if badge == 'per' else 'photo')
         if badge else '')
    a = '<span class="t15-help" id="%s-aide">?</span>' % ident if aide else ''
    d = ('<span class="t15-delta %s" id="%s-d">%s</span>' % ('up' if delta[0] == '▲' else 'down', ident, e(delta))
         if delta else '')
    s = '<div class="t15-sub" id="%s-s">%s</div>' % (ident, e(sous)) if sous else ''
    return ('<div class="%s" id="%s">%s<div class="t15-lbl">%s%s</div><div class="t15-val"><span id="%s-v">%s</span>%s'
            '</div>%s</div>' % (classes, ident, b, e(libelle), a, ident, e(valeur), d, s))


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
    """table.add-mini : [(libellé, montant, indication html)]."""
    corps = ''.join('<div class="t15-tr"%s><span class="t15-td">%s</span><span class="t15-r">%s</span>'
                    '<span class="t15-age">%s</span></div>'
                    % (' id="%s"' % i if i else '', e(l), e(m), h) for i, l, m, h in lignes)
    return '<div class="t15-mini"%s>%s</div>' % (' id="%s"' % ident if ident else '', corps)


def pill(texte_, rouge=False):
    return '<span class="t15-pill %s">%s</span>' % ('t15-p-rouge' if rouge else 't15-p-ambre', e(texte_))


def hbar(libelle, pct, couleur, valeur, indice=''):
    """HBar (direction_dashboard.xml:28-40) : largeur bornée entre 1 et 100 %."""
    ind = '<span class="t15-hint">%s</span>' % e(indice) if indice else ''
    return ('<div class="t15-hbar"><span class="t15-hl">%s</span><span class="t15-ht"><i style="width:%.1f%%;'
            'background:%s"></i></span><span class="t15-hv">%s%s</span></div>' % (e(libelle), pct, couleur, e(valeur), ind))


# ------------------------------------------------------------ le cockpit --
JOURS = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim']
ONGLETS = [('vue', "Vue d'ensemble", None), ('pos', 'Ventes (POS)', None), ('credit', 'Crédit clients', '3'),
           ('stock', 'Stock', '2'), ('achat', 'Achats', '1'), ('todo', 'À traiter', None)]


def onglet(cle, libelle, n):
    pastille = '<span class="t15-n" id="t15-tab-%s-n">%s</span>' % (cle, n) if n else ''
    if cle == 'todo':        # la pastille n'apparaît qu'une fois l'onglet ouvert (js:494-503)
        pastille = '<span class="t15-n t15-attente" id="t15-tab-todo-n">10</span>'
    return '<span class="t15-tab%s" id="t15-tab-%s">%s%s</span>' % (' on' if cle == 'vue' else '', cle, e(libelle),
                                                                   pastille)


TOP = ('<div class="t15-top"><div class="t15-head"><div class="t15-h1">Direction — Vue consolidée</div>'
       '<div class="t15-hsub">POS · Crédit clients · Stock · Achats — %s</div></div>%s</div>' % (e(SOCIETE), ''.join([
           barre('PÉRIODE', ''.join([chip('t15-pe-all', 'Toute la période'), chip('t15-pe-today', "Aujourd'hui"),
                                     chip('t15-pe-week', 'Cette semaine'), chip('t15-pe-month', 'Ce mois', True),
                                     chip('t15-pe-quarter', 'Ce trimestre'), chip('t15-pe-year', 'Cette année'),
                                     '<span class="t15-du">Du</span>', date_in('t15-du', '30/09/2026'),
                                     '<span class="t15-du">au</span>', date_in('t15-au', '14/10/2026'),
                                     chip('t15-apply', 'Appliquer')])),
           barre('CAISSE', chip('t15-ca-tout', 'Toutes les caisses', True)
                 + chip('t15-ca-bar', 'Bar de la terrasse', point='#714B67')
                 + chip('t15-ca-resto', 'Restaurant', point='#185FA5'),
                 'caisse, heure et jours filtrent les données de vente', 't15-note-caisse'),
           barre('HEURE', ''.join([chip('t15-h-tout', 'Toute la journée', True), chip('t15-h-matin', 'Matin 6–12h'),
                                   chip('t15-h-am', 'Après-midi 12–18h'), chip('t15-h-soir', 'Soir 18–23h'),
                                   chip('t15-h-nuit', 'Nuit 23–6h')])),
           barre('JOUR', ''.join(chip('t15-j-%d' % i, j) for i, j in enumerate(JOURS)), 'multi-sélection — aucun = tous'),
           barre('VUE', ''.join(onglet(*o) for o in ONGLETS)),
       ])))

# -- la vue d'ensemble : chiffres du 30/09 au 14/10/2026, toutes caisses --
SANTE = rangee(
    carte('t15-k-ca', 'CA encaissé', '3 120 000 FCFA', '128 tickets · POS payés / facturés', 'per', 'vert', True,
          '▲ +9,4 %'),
    carte('t15-k-marge', 'Marge brute réalisée', '1 747 200 FCFA', '56,0 % du CA · CA − coût des ventes', 'per', 'teal',
          True),
    carte('t15-k-risque', 'Cash à risque', '143 000 FCFA', 'ardoises +30 j (101 500) + coulage (41 500)', 'per', 'rouge',
          True),
    carte('t15-k-net', 'Crédits clients − dettes fournisseurs', '-1 130 000 FCFA',
          "150 000 d'ardoises · 1 280 000 de dettes — les fournisseurs financent l'exploitation", 'photo', 'info', True),
    ident='t15-sante')
POLES = rangee(
    carte('t15-p-tix', 'Ventes — tickets', '128', 'panier moyen 24 375 FCFA', 'per'),
    carte('t15-p-ard', 'Encours ardoises', '150 000 FCFA', '5 clients · 101 500 au-delà de 30 j', 'photo', 'ambre'),
    carte('t15-p-four', 'Dettes fournisseurs', '1 280 000 FCFA', '180 000 échues · 420 000 sous 7 j', 'photo', 'info'),
    carte('t15-p-stock', 'Stock — valeur / alertes', '3 185 000 FCFA', '2 réfs en alerte · coulage 1,3 %', 'photo'),
    ident='t15-poles')
HOTEL = rangee(
    carte('t15-x-ca', 'CA des nuitées (HT)', '8 640 000 FCFA', '192 nuitée(s) vendue(s) · pace du mois : 412 (N-1 : 387)',
          'per', 'vert', delta='▲ +11,6 %', aide=True),
    carte('t15-x-occ', "Taux d'occupation", '64,0 %', 'pickup 46 nuitée(s) prises ces 7 j pour les 30 prochains', 'per',
          delta='▲ +8,2 %', aide=True),
    carte('t15-x-adr', 'ADR — prix moyen par nuit', '45 000 FCFA', 'CA hébergement ÷ nuitées vendues', 'per',
          delta='▲ +3,1 %', aide=True),
    carte('t15-x-revpar', 'RevPAR', '28 800 FCFA', 'par chambre disponible, vendue ou non', 'per', 'teal',
          delta='▲ +11,6 %', aide=True),
    ident='t15-hr')

# Tendances (direction_dashboard.xml:42-107) : 6 mois, barres CA à zéro (écart 3).
MOIS = ['Mai', 'Juin', 'Juil', 'Août', 'Sep', 'Oct']
ACHATS = [1620000, 1710000, 1540000, 1880000, 1760000, 980000]
ENCOURS = [121000, 139500, 158000, 171500, 186500, 150000]


def trend_svg():
    mb, ml = max(ACHATS), max(ENCOURS)
    slot = 500.0 / 6
    corps = []
    pts = []
    for i, p in enumerate(MOIS):
        x0 = 45 + i * slot
        h = ACHATS[i] / float(mb) * 160
        corps.append('<rect x="%.1f" y="180" width="22" height="0" fill="#714B67"/>' % (x0 + slot / 2 - 24))
        corps.append('<rect x="%.1f" y="%.1f" width="22" height="%.1f" fill="#185FA5"/>' % (x0 + slot / 2 + 2, 180 - h, h))
        corps.append('<text x="%.1f" y="198" font-size="10" fill="#62615C" text-anchor="middle">%s</text>'
                     % (x0 + slot / 2, p))
        pts.append((x0 + slot / 2, 180 - ENCOURS[i] / float(ml) * 160))
    ligne = ' '.join('%.1f,%.1f' % p for p in pts)
    points = ''.join('<circle cx="%.1f" cy="%.1f" r="3.5" fill="#854F0B"/>' % p for p in pts)
    return ('<svg viewBox="0 0 560 212" class="t15-trend"><g stroke="#eeede8" stroke-width="1"><line x1="40" y1="20" '
            'x2="545" y2="20"/><line x1="40" y1="100" x2="545" y2="100"/><line x1="40" y1="180" x2="545" y2="180"/></g>'
            '<g font-size="9" fill="#62615C" text-anchor="end"><text x="36" y="23">1 880 000</text><text x="36" y="183">0'
            '</text></g><g font-size="9" fill="#854F0B" text-anchor="start"><text x="548" y="23">186 500</text>'
            '<text x="548" y="183">0</text></g>%s<polyline points="%s" fill="none" stroke="#854F0B" stroke-width="2.5"/>'
            '%s</svg>' % (''.join(corps), ligne, points))


LEGENDE_TREND = ('<div class="t15-legend"><i class="t15-dot" style="background:#714B67"></i>CA encaissé'
                 '<i class="t15-dot" style="background:#185FA5"></i>Achats (factures)'
                 '<i class="t15-dot" style="background:#854F0B"></i>Encours d\'ardoises (échelle droite)</div>')

MIROIR_CLI = [('0–30 j', '48 500', 67.8, '#3B6D11'), ('30–60 j', '71 500', 100, '#854F0B'),
              ('60–90 j', '0', 2, '#a3702a'), ('+90 j', '30 000', 42.0, '#A32D2D')]
MIROIR_FOUR = ['#185FA5', '#5b83b0', '#8fa8c4', '#b9c9da']
MIROIR = ('<div class="t15-mhead"><span>Vos clients vous doivent</span><span class="t15-msp"></span>'
          '<span>Vous devez aux fournisseurs</span></div><div class="t15-mirror">%s</div>'
          '<div class="t15-legend">Gauche : du cash qui s\'évapore avec l\'âge. Droite : du crédit fournisseur — gratuit '
          'tant que les échéances tiennent.</div>'
          % ''.join('<div class="t15-mrow"><div class="t15-mside t15-left"><span class="t15-mval">%s</span>'
                    '<i style="width:%.1f%%;background:%s"></i></div><div class="t15-mlab">%s</div><div class="t15-mside">'
                    '<i style="width:2%%;background:%s"></i><span class="t15-mval">0</span></div></div>'
                    % (v, w, c, e(l), MIROIR_FOUR[i]) for i, (l, v, w, c) in enumerate(MIROIR_CLI)))
TENDANCES = ('<div class="t15-row">%s%s</div>'
             % (panneau('CA vs Achats — 6 mois, et encours d\'ardoises', 'POS · Achats · Crédit',
                        trend_svg() + LEGENDE_TREND),
                panneau('Balance âgée en miroir', 'Crédit · Achats', MIROIR)))

TIP_REVPAR = ('<div class="infobulle masque t15-tip" id="t15-tip-revpar" data-layout-allow-overlap '
              'data-layout-allow-occlusion>RevPAR : ce que rapporte chaque chambre disponible, vendue ou non — c\'est '
              'l\'indicateur qui combine prix et remplissage.</div>')
VUE_ENSEMBLE = ('<div class="vue initiale t15-pane" id="t15-b-vue"><div class="t15-defil" id="t15-vue-defil" '
                'data-layout-allow-overflow data-layout-allow-occlusion>%s%s%s%s%s%s%s%s%s%s</div></div>'
                % (sect("SANTÉ DE L'AFFAIRE"), SANTE, sect("L'ESSENTIEL PAR PÔLE — cliquer une carte ouvre l'onglet"),
                   POLES, sect('HÉBERGEMENT — écarts vs même période N-1 ; cliquer une carte ouvre le tableau de bord '
                               'exécutif'), HOTEL, sect('TENDANCES'), TENDANCES, TIP_REVPAR, ''))

# -- onglet Crédit clients (même période) --
CREDIT_KPI = (
    rangee(carte('t15-c-enc', 'Encours total', '150 000 FCFA', '5 clients débiteurs', 'photo', 'ambre', True),
           carte('t15-c-late', 'Au-delà de 30 j', '101 500 FCFA', "67,7 % de l'encours", 'photo', 'rouge'),
           carte('t15-c-old', 'Plus ancienne ardoise', '104 j', 'Sylvie Mbarga · 30 000 FCFA', 'photo'),
           carte('t15-c-delai', 'Délai moyen de remboursement', '10 j', '3 ardoises soldées', 'photo'))
    + rangee(carte('t15-c-rec', 'Recouvré', '82 500 FCFA', '6 remboursements', 'per', 'vert', delta='▲ +61,8 %'),
             carte('t15-c-new', 'Nouveaux crédits', '41 000 FCFA', '2 ardoises ouvertes', 'per', 'ambre',
                   delta='▼ 36,9 %'),
             carte('t15-c-flux', 'Flux net', '−41 500 FCFA', "recouvré − nouveaux : l'encours monte", 'per', 'teal'),
             carte('t15-c-taux', 'Taux de recouvrement', '35 %', 'ardoise moyenne 30 000 FCFA', 'per')))
# couleurs de la balance âgée telles que keyOf les choisit (écart 4)
AGING = (hbar('0–30 j', 67.8, '#3B6D11', '48 500', '2 cl.') + hbar('30–60 j', 100, '#3B6D11', '71 500', '2 cl.')
         + hbar('60–90 j', 2, '#854F0B', '0', '0 cl.') + hbar('+90 j', 42.0, '#a3702a', '30 000', '1 cl.'))
SPARK = ('<svg viewBox="0 0 520 120" class="t15-spark"><polyline points="%s" fill="none" stroke="#854F0B" '
         'stroke-width="2.5"/></svg>'
         % ' '.join('%.1f,%.1f' % (15 + i * 490 / 6.0 + 490 / 12.0, 105 - v / 186500.0 * 90) for i, v in enumerate(ENCOURS)))
# tri stable par encours sur des ardoises lues en create_date desc : à encours égal, ARD/0039 (Essomba, plus
# récente) sort avant ARD/0017 (Mbarga) — pos_credit.py:23, pos_credit_dashboard.py:388-427
TOP_DEB = mini([(None, 'Armand Mvogo', '44 500 FCFA', pill('57 j')), (None, 'Brigitte Essomba', '30 000 FCFA', pill('22 j')),
                (None, 'Sylvie Mbarga', '30 000 FCFA', pill('104 j', True)), (None, 'Joël Kamga', '27 000 FCFA', pill('39 j')),
                (None, 'Patrick Nkoulou', '18 500 FCFA', pill('5 j'))], 't15-c-top-t')
REMB = mini([(None, 'Christian Atangana', '15 000 FCFA', 'Orange Money · 2026-10-12'),
             (None, 'Armand Mvogo', '20 000 FCFA', 'MTN Mobile Money · 2026-10-08'),
             (None, 'Nadège Owona', '22 500 FCFA', 'Espèces · 2026-10-06'),
             (None, 'Brigitte Essomba', '12 000 FCFA', 'Orange Money · 2026-10-03'),
             (None, 'Rodrigue Manga', '8 000 FCFA', 'MTN Mobile Money · 2026-10-02')])
CREDIT_PANNEAUX = ('<div class="t15-row">%s%s</div>'
                   % (panneau('Balance âgée clients', 'Crédit v2',
                              AGING + '<h3 class="t15-mt">Encours — 6 mois (fin de mois)</h3>' + SPARK
                              + '<div class="t15-legend">Mai → Oct · dernier point : 150 000 FCFA</div>', 't15-c-aging'),
                      panneau('Top débiteurs', 'photo', TOP_DEB + '<h3 class="t15-mt">Derniers remboursements'
                              '<span class="t15-src">période</span></h3>' + REMB
                              + '<span class="t15-drill">Ouvrir Crédit clients ↗</span>', 't15-c-top')))
VUE_CREDIT = ('<div class="vue t15-pane" id="t15-b-credit"><div class="t15-defil" id="t15-credit-defil" '
              'data-layout-allow-overflow data-layout-allow-occlusion>%s%s%s%s</div></div>'
              % (barre('ORIGINE', chip('t15-o-tout', 'Toutes', True) + chip('t15-o-pos', 'POS')
                       + chip('t15-o-sale', 'Ventes / factures')),
                 sect('CRÉDIT CLIENTS — ARDOISES'), CREDIT_KPI, CREDIT_PANNEAUX))

# -- onglet À traiter (get_actions, sans ligne « Payer » : écart 3) --
VUE_TODO = ('<div class="vue t15-pane" id="t15-b-todo"><div class="t15-defil">%s<div class="t15-row t15-wrap">%s</div>'
            '<div class="t15-legend t15-pad">Chaque ligne ouvre le tableau de bord spécialisé correspondant.</div>'
            '</div></div>'
            % (sect('À TRAITER — LA LISTE DU GÉRANT (10 actions)'), ''.join([
                panneau('Ardoises anciennes', 'Crédit', mini([
                    ('t15-r-mvogo', 'Relancer Armand Mvogo', '44 500 FCFA', '57 j'),
                    ('t15-r-mbarga', 'Relancer Sylvie Mbarga', '30 000 FCFA', '104 j'),
                    ('t15-r-kamga', 'Relancer Joël Kamga', '27 000 FCFA', '39 j')]), 't15-s-credit', 'URGENT'),
                panneau('Fournisseurs', 'Achats', mini([
                    (None, 'Régulariser 1 facture(s) échue(s)', '180 000 FCFA', 'échu')]), 't15-s-four', 'URGENT'),
                panneau('Stock', 'Stock', mini([
                    (None, 'Commander Bière blonde 65 cl', '46 800 FCFA', 'perd / jour'),
                    (None, 'Commander Eau minérale 1,5 L', '12 000 FCFA', 'perd / jour'),
                    (None, 'Lancer la commande suggérée (5 réfs)', '385 000 FCFA', 'sous seuil')]), 't15-s-stock',
                        'URGENT'),
                panneau('Coulage & écarts', 'Stock', mini([
                    (None, "Écarts d'inventaire négatifs", '27 000 FCFA', 'contrôler')]), 't15-s-coul', 'À SURVEILLER'),
                panneau("Prix d'achat", 'Achats', mini([
                    (None, 'Renégocier Bière blonde 65 cl', '', '+8 % · Boissons du Wouri SARL'),
                    (None, 'Renégocier Savon liquide 5 L', '', '+12 % · Hygiène Pro Littoral')]), 't15-s-prix',
                        'À SURVEILLER')])))

COCKPIT = vue_libre('t15-cockpit', TOP + '<div class="t15-corps" id="t15-corps">%s%s%s</div>'
                    % (VUE_ENSEMBLE, VUE_CREDIT, VUE_TODO), initiale=True, fond='tdb')


# ------------------------------------------------- le tableau exécutif --
def ek(ident, libelle, valeur, sous, accent=None, delta=None, aide=False):
    """Une carte du tableau exécutif (dashboard.xml:4-16, kpi_card.js)."""
    classes = 't15-ek' + (' t15-ek-mega' + (' t15-ea-' + accent if accent in ('primary', 'info') else '')
                          if accent else '')
    a = '<span class="t15-ek-help" id="%s-aide">?</span>' % ident if aide else ''
    d = '<div class="t15-ek-d">%s</div>' % e(delta) if delta else ''
    return ('<div class="%s" id="%s"><div class="t15-ek-l">%s%s</div><div class="t15-ek-v" id="%s-v">%s</div>%s'
            '<div class="t15-ek-s">%s</div></div>' % (classes, ident, e(libelle), a, ident, e(valeur), d, e(sous)))


TIP_PACE = ('<div class="infobulle masque t15-tip" id="t15-tip-pace" data-layout-allow-overlap '
            'data-layout-allow-occlusion>Pace : nuitées déjà réservées pour le mois en cours, comparées à celles qui '
            'l\'étaient à la même date l\'an dernier.</div>')
MIX = [('Hébergement', '#714B67', 7912400, '7 912 400', '61,5 %'),
       ('Restauration & boutique', '#185FA5', 3720600, '3 720 600', '28,9 %'),
       ('Prestations', '#0F6E56', 1240000, '1 240 000', '9,6 %')]


def anneau_mix():
    total = float(sum(m[2] for m in MIX))
    r, c = 80, 2 * 3.14159265 * 80
    debut, arcs = 0.0, []
    for _, coul, v, _, _ in MIX:
        lg = c * v / total
        arcs.append('<circle r="%d" cx="110" cy="110" fill="none" stroke="%s" stroke-width="56" stroke-dasharray="%.1f %.1f" '
                    'stroke-dashoffset="%.1f"/>' % (r, coul, lg, c - lg, -debut))
        debut += lg
    leg = ''.join('<div><i style="background:%s"></i>%s</div>' % (coul, e(n)) for n, coul, _, _, _ in MIX)
    liste = ''.join('<div class="t15-mixrow"><i style="background:%s"></i><span>%s</span><b>%s · %s</b></div>'
                    % (coul, e(n), e(ex(m)), e(p)) for n, coul, _, m, p in MIX)
    return ('<div class="t15-mixbox"><svg viewBox="0 0 220 220" class="t15-ring"><g transform="rotate(-90 110 110)">%s'
            '</g></svg><div class="t15-mixleg">%s</div></div><div class="t15-mixlist">%s</div>'
            % (''.join(arcs), leg, liste))


EVO = [(14.2, 6.8, 2.1), (13.6, 6.5, 2.0), (16.9, 7.6, 2.6), (17.8, 7.9, 2.8), (16.4, 7.2, 2.4), (7.4, 3.5, 1.2)]
# millions de FCFA par mois : hébergement, restauration & boutique, prestations (octobre : au 14)
EVO_LAB = ['mai 26', 'juin 26', 'juil 26', 'août 26', 'sept 26', 'oct 26']


def evolution():
    groupes = ''.join('<div class="t15-evg"><div class="t15-evb">%s</div><span>%s</span></div>'
                      % (''.join('<i style="height:%.1f%%;background:%s"></i>' % (v / 20.0 * 100, coul)
                                 for v, coul in zip(vals, ('#714B67', '#185FA5', '#0F6E56'))), lab)
                      for vals, lab in zip(EVO, EVO_LAB))
    axe = ''.join('<span>%dk</span>' % k for k in (20000, 15000, 10000, 5000, 0))
    return ('<div class="t15-evo"><div class="t15-axe">%s</div><div class="t15-evz">%s</div></div>'
            '<div class="t15-legend t15-evleg"><i class="t15-dot" style="background:#714B67"></i>Hébergement'
            '<i class="t15-dot" style="background:#185FA5"></i>Restauration &amp; boutique'
            '<i class="t15-dot" style="background:#0F6E56"></i>Prestations</div>' % (axe, groupes))


EXEC = vue_libre('t15-exec', '<div class="t15-x" id="t15-exec-defil" data-layout-allow-overflow '
                 'data-layout-allow-occlusion>%s</div>' % ''.join([
                     '<div class="t15-xtop"><div class="t15-xtitre">Direction — Vue consolidée</div>'
                     '<div class="t15-xsous">Hébergement · Restauration &amp; boutique · Prestations</div></div>',
                     '<div class="t15-xfiltre"><span class="t15-xlab">Période</span><span class="t15-xchip on">Ce mois</span>'
                     '<span class="t15-xchip">Ce trimestre</span><span class="t15-xchip">Cette année</span>'
                     '<span class="t15-xesp"></span><span class="t15-xlab t15-xdu">Du</span>%s<span class="t15-xlab t15-xdu">'
                     'au</span>%s</div>' % (date_in('t15-xdu', '30/09/2026'), date_in('t15-xau', '14/10/2026')),
                     '<div class="t15-xg4">%s</div>' % ''.join([
                         ek('t15-e-tot', "Chiffre d'affaires total", ex('12 873 000'), 'Période 2026-09-30 → 2026-10-14',
                            'primary'),
                         ek('t15-e-heb', 'Hébergement', ex('7 912 400'), 'Occupation 64 % · ADR ' + ex('45 000'),
                            'primary'),
                         ek('t15-e-pos', 'Restauration & boutique', ex('3 720 600'), '128 tickets · panier ' + ex('29 067'),
                            'info'),
                         ek('t15-e-pre', 'Prestations', ex('1 240 000'), '46 prestation(s) réalisée(s)', 'teal')]),
                     '<div class="t15-xsect">Hébergement — indicateurs de performance <span>écarts vs même période N-1'
                     '</span></div>',
                     '<div class="t15-xg5" id="t15-e-perf">%s</div>' % ''.join([
                         ek('t15-e-occ', "Taux d'occupation", '64 %', '192 nuitée(s) vendue(s)', delta='▲ +8,2 % vs N-1',
                            aide=True),
                         ek('t15-e-adr', 'ADR — prix moyen par nuit', ex('45 000'), 'CA hébergement ÷ nuitées vendues',
                            delta='▲ +3,1 % vs N-1', aide=True),
                         ek('t15-e-revpar', 'RevPAR', ex('28 800'), 'par chambre disponible, vendue ou non',
                            delta='▲ +11,6 % vs N-1', aide=True),
                         ek('t15-e-pick', 'Pickup 7 j → 30 j', '46 nuitée(s)',
                            '18 réservation(s) prise(s) ces 7 derniers jours', aide=True),
                         ek('t15-e-pace', 'Pace du mois', '412 nuitée(s)', 'mois oct 26 · N-1 à la même date : 387 nuitée(s)',
                            delta='▲ +6,5 % vs même date N-1', aide=True)]),
                     '<div class="t15-xg4">%s</div>' % ek('t15-e-fid', 'Points fidélité émis', '12' + NNBSP + '480',
                                                          'Tous services confondus'),
                     '<div class="t15-xsect">Répartition &amp; évolution</div>',
                     '<div class="t15-xg2"><div class="t15-xcard" id="t15-e-mix"><h3>Mix du chiffre d\'affaires par pôle</h3>'
                     '%s</div><div class="t15-xcard"><h3>Évolution mensuelle — 6 mois</h3>%s</div></div>'
                     % (anneau_mix(), evolution()),
                     TIP_PACE]), fond='tdb')

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
  white-space: nowrap; display: flex; align-items: center; }
.t15-help { width: 18px; height: 18px; border-radius: 50%; background: #714B67; color: #fff; font-size: 11.5px; margin-left: 7px;
  display: inline-flex; align-items: center; justify-content: center; letter-spacing: 0; flex: none; }
.t15-val { margin-top: 4px; font-size: 27px; font-weight: 800; color: #46414E; white-space: nowrap; line-height: 1.2; }
.t15-mega .t15-val { font-size: 32px; }
.t15-delta { margin-left: 9px; font-size: 15px; font-weight: 700; }
.t15-delta.up { color: #3B6D11; } .t15-delta.down { color: #A32D2D; }
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
.t15-mval { font-size: 13.5px; color: #5c5861; margin: 0 7px; min-width: 60px; }
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
.t15-tip { width: 470px; font-size: 18px; }
#t15-tip-revpar { left: 1010px; top: 212px; }
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
.t15-ea-info { border-left-color: #185FA5; }
.t15-ek-l { font-size: 13px; font-weight: 600; letter-spacing: .5px; text-transform: uppercase; color: var(--t15-muet); white-space: nowrap;
  display: flex; align-items: center; }
.t15-ek-help { width: 18px; height: 18px; border-radius: 50%; background: #714B67; color: #fff; font-size: 12px; margin-left: 7px;
  display: inline-flex; align-items: center; justify-content: center; flex: none; }
.t15-ek-v { margin-top: 6px; font-size: 27px; font-weight: 700; line-height: 1.15; color: #2b2a28; white-space: nowrap; }
.t15-ek-d { margin-top: 5px; font-size: 14px; font-weight: 600; color: #3B6D11; white-space: nowrap; }
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
#t15-tip-pace { left: 1036px; top: 428px; }
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
        'b-risque': 'Ardoises de 30 jours et plus + coulage du stock : calculé, rien à saisir.',
        'b-filtre': 'Heure et jours ne filtrent que les ventes.',
        'b-todo': 'Chaque ligne ouvre le tableau de bord spécialisé.',
        'b-n1': "Vert : mieux que l'an dernier. Rouge : moins bien.",
    },
    'reactions': {
        'r-relance': 'Je sais qui relancer en premier.',
        'r-fin': 'Je sais où creuser.',
    },
    'etapes': [
        {'temps': 0, 'titre': "La santé de l'affaire",
         'texte': 'Le chiffre encaissé, la marge, le cash à risque, et vos ardoises face à vos dettes.',
         'voix': "Danielle ouvre Direction. En tête, la santé de l'affaire : le chiffre encaissé et son écart, la "
                 "marge réalisée, l'argent à risque, et ce que vos clients vous doivent face à vos dettes "
                 "fournisseurs.",
         'gestes': [clic('#t15-app-app-direction', d=0.6), compter('#t15-k-ca-v', 0, 3120000, d=1.2, apres=' FCFA'),
                    curseur('#t15-sante', fx=0.62, fy=-0.22, d=0.6, avec=True), anneau('#t15-k-ca', d=1.2),
                    anneau('#t15-k-marge', d=1.0), zoom('#t15-k-risque', s=1.85, d=0.8),
                    bulle('b-risque', '#t15-k-risque', cote='haut', d=3.0), pause(2.8), dezoom(d=0.6),
                    anneau('#t15-k-net', d=1.6)]},
        {'temps': 0, 'titre': 'Le soir du week-end',
         'texte': 'Heure et jours recalculent les ventes ; ardoises, stock et dettes ne bougent pas.',
         'voix': "Et les soirs de fin de semaine ? Soir, dix-huit, vingt-trois heures, puis vendredi et samedi : le chiffre, "
                 "la marge et les tickets se recalculent. Les ardoises, le stock et les dettes ne bougent pas.",
         'gestes': [clic('#t15-h-soir', d=0.6), classe('#t15-h-tout', retirer=['on']),
                    classe('#t15-h-soir', ajouter=['on'], avec=True), clic('#t15-j-4', d=0.5),
                    classe('#t15-j-4', ajouter=['on']), clic('#t15-j-5', d=0.4), classe('#t15-j-5', ajouter=['on']),
                    texte('#t15-k-ca-v', '1 405 000 FCFA'), texte('#t15-k-ca-d', '▲ +6,8 %', avec=True),
                    texte('#t15-k-ca-s', '52 tickets · POS payés / facturés', avec=True),
                    texte('#t15-k-marge-v', '790 400 FCFA', avec=True),
                    texte('#t15-k-marge-s', '56,3 % du CA · CA − coût des ventes', avec=True),
                    texte('#t15-p-tix-v', '52', avec=True), texte('#t15-p-tix-s', 'panier moyen 27 019 FCFA', avec=True),
                    anneau('#t15-k-ca', d=1.3), bulle('b-filtre', '#t15-note-caisse', cote='bas', d=3.2),
                    anneau('#t15-p-tix', d=1.2), anneau('#t15-k-risque', d=1.2), anneau('#t15-p-ard', d=1.2)]},
        {'temps': 1, 'titre': 'Un clic sur un pôle',
         'texte': "La carte « Encours ardoises » ouvre l'onglet Crédit clients.",
         'voix': "Pour creuser, un clic sur une carte de pôle. L'encours des ardoises ouvre l'onglet Crédit clients : "
                 "la balance âgée, l'encours sur six mois, et les débiteurs, du plus gros encours au plus petit.",
         'gestes': [clic('#t15-p-ard', d=0.7), classe('#t15-tab-vue', retirer=['on']),
                    classe('#t15-tab-credit', ajouter=['on'], avec=True), vue('t15-b-credit', 'corps'),
                    defiler('#t15-credit-defil', -316, d=0.7, avec=True), pause(0.2), anneau('#t15-c-aging', d=1.4),
                    zoom('#t15-c-top-t', s=1.8, d=0.7),
                    reaction('r-relance', d=2.8), pause(2.6), dezoom(d=0.5), anneau('#t15-c-top', d=1.0)]},
        {'temps': 2, 'titre': 'À traiter : la liste du gérant',
         'texte': 'Relancer, régulariser, commander, renégocier : la liste se construit seule.',
         'voix': "Reste à agir. L'onglet À traiter dresse la liste du gérant : relancer les ardoises de plus de trente "
                 "jours, régulariser la facture échue, commander la bière en rupture, renégocier une hausse de prix.",
         'gestes': [clic('#t15-tab-todo', d=0.7), classe('#t15-tab-credit', retirer=['on']),
                    classe('#t15-tab-todo', ajouter=['on', 'vu'], avec=True), vue('t15-b-todo', 'corps'), pause(0.3),
                    anneau('#t15-s-credit', d=1.2), bulle('b-todo', '#t15-s-four', cote='bas', d=3.0), pause(2.4),
                    anneau('#t15-s-four', d=1.1), anneau('#t15-s-stock', d=1.2), anneau('#t15-s-prix', d=1.2)]},
        {'temps': 3, 'titre': "L'hôtel face à l'an dernier",
         'texte': "Occupation, prix moyen, RevPAR : l'écart N-1 en couleur, et un « ? » qui explique.",
         'voix': "Retour à la vue d'ensemble, côté hôtel. Occupation, prix moyen par nuit, revpar : chaque carte se "
                 "compare à la même période l'an dernier, et son point d'interrogation l'explique en une phrase.",
         'gestes': [clic('#t15-tab-vue', d=0.7), classe('#t15-tab-todo', retirer=['on']),
                    classe('#t15-tab-vue', ajouter=['on'], avec=True), vue('t15-b-vue', 'corps'),
                    defiler('#t15-vue-defil', -60, d=0.6), anneau('#t15-x-occ', d=1.2), anneau('#t15-x-adr', d=1.2),
                    bulle('b-n1', '#t15-x-revpar', cote='haut', d=2.8), pause(2.4),
                    curseur('#t15-x-revpar-aide', d=0.6), montrer('#t15-tip-revpar', d=0.3, y=6), pause(2.6),
                    cacher('#t15-tip-revpar', d=0.2), curseur('#t15-x-revpar', fx=0.6, fy=-0.25, d=0.5)]},
        {'temps': 3, 'titre': 'Pickup et pace : le tableau exécutif',
         'texte': 'Une carte Hébergement ouvre le tableau de bord exécutif : le pickup et le pace du mois.',
         'voix': "Un clic sur une carte de l'hôtel ouvre le tableau de bord exécutif. Le pikeup : les nuitées prises ces "
                 "sept derniers jours pour les trente prochains. Le pace : les nuitées déjà réservées pour le mois, face "
                 "à l'an dernier à la même date.",
         'gestes': [clic('#t15-x-revpar', d=0.8), vue('t15-exec'), defiler('#t15-exec-defil', -262, d=0.6, avec=True),
                    zoom('#t15-e-pace', s=1.5, fx=0.0, d=0.7), anneau('#t15-e-pick', d=1.6),
                    curseur('#t15-e-pace-aide', d=0.6), montrer('#t15-tip-pace', d=0.3, y=6), pause(2.8),
                    cacher('#t15-tip-pace', d=0.2), curseur('#t15-e-pace', fx=0.5, fy=1.6, d=0.5),
                    reaction('r-fin', d=2.6), pause(1.8)]},
    ],
    'resultats': {
        'titre': 'Lire, creuser, agir, comparer',
        'cartes': [
            {'valeur': '6', 'compter': 6, 'unite': 'onglets', 'icone': 'liste',
             'texte': "vue d'ensemble, ventes, crédit, stock, achats, à traiter : une seule page"},
            {'valeur': '4', 'compter': 4, 'unite': 'tableaux de bord', 'icone': 'piles',
             'texte': 'relus par le cockpit : ventes, crédit clients, stock, achats, sans ressaisie'},
            {'valeur': '6', 'compter': 6, 'unite': "phrases d'explication", 'icone': 'interrogation',
             'texte': 'occupation, prix moyen, RevPAR, pickup, pace et écart N-1'},
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
