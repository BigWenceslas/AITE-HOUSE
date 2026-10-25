# -*- coding: utf-8 -*-
"""Chapitre 6 — Le cockpit de la direction.

Source : fiche de recette n° 4 « Le cockpit de la direction » (Ventes —
Analyse AITE, Recouvrement, Stock, Achats & Fournisseurs, Espaces &
Prestations, Cockpit Direction, Activité par pôle) et cahier de recette,
domaine Q (F06 : RevPAR, pickup, pace, écarts N-1, tuile Hébergement du
cockpit).

Libellés relevés dans (livraison 4, écarts n° 37-77) :
- aite_direction_dashboard/static/src/xml/direction_dashboard.xml (titre
  « Direction — Vue consolidée », inchangé ; filtres Période / Caisse / Heure
  / Jour / Vue, :143-199, avec les notes « caisse, heure et jours filtrent les
  données de vente » et « multi-sélection — aucun = tous », aucun jour coché ; « Santé de l'affaire », « CA encaissé » et sa variation
  « vs période précédente », deltaLabel :219-224 ; « L'essentiel par pôle —
  cliquer une carte ouvre l'onglet » et ses sous-titres accordés « 5
  débiteurs · 101 500 en retard (+30 j) », « 2 références en alerte » ;
  rangée « Hébergement — écarts vs même période N-1 ; cliquer une carte ouvre
  « Direction — Activité par pôle » », pastilles « période » / « photo » des
  cartes (KpiCard badge, :10-12), cartes « Prix moyen par nuit (ADR) » et
  « Revenu par chambre disponible (RevPAR) », variations sans libellé
  :274-305), static/src/js/direction_dashboard.js (fmtMoney à l'espace fine,
  trait d'union des négatifs « -1 130 000 FCFA » :88-95 ; fmtDelta « ▲ +11,6
  % » :112-117 ; netPositionSub, hotelPaceSub « rythme du mois (pace) »,
  hotelPickupSub « réservations récentes (pickup) » :394-419) ;
- aite_exec_dashboard/static/src/xml/dashboard.xml (« Direction — Activité
  par pôle », écart n° 42, menu Hôtel → « Activité par pôle » ; « Du
  01/10/2026 au 14/10/2026 », « prix moyen 45 000 FCFA / nuit », « 46
  prestations réalisées », cartes « Réservations récentes (pickup) » et
  « Rythme du mois (pace) »), static/src/js/views/exec_dashboard_view.js
  (periodText :136-139, pickupSub, paceSub « mois oct. 26 » :155-169),
  static/src/js/services/utils.js (fmtPct « 63,9 % », fmtDelta, « vs N-1 »
  par défaut et « vs même date N-1 » pour le rythme, monthLabel « oct. 26 »),
  carte « Points fidélité émis » « Tous services confondus » (aite_loyalty
  installé, dashboard.xml:107-111), « Répartition & évolution », mix avec sa
  liste « montant · part » (mixLine) et évolution mensuelle en barres groupées
  par pôle, légende en bas, axe kTick « 20 M » … « 0 » (get_evolution,
  exec_dashboard.py:297-321, exec_dashboard_view.js:239-270, comme t15),
  models/exec_dashboard.py:31-33 (KPI_HINTS : infobulle RevPAR, attribut
  title, ouverte au survol du « ? », sous lui, dashboard.xml:5-11) ;
- aite_pos_analytics/static/src/xml/views.xml (« HT · … / jour · 14 j »,
  « Taux : … / ticket », « / unité », « Panier moyen … · 512 unités »,
  « 44,0 % », montants en FCFA, « Top 8 articles — CA vs Marge »,
  « Évolution mensuelle (CA · CMV · Marge) » au nom d'Odoo « octobre 2026 »,
  get_monthly_evolution, axe Chart.js cadré sur les données de 1,2 M à 3,2 M,
  dashboard_view.js:159-185 ; bande « Évolution par rapport à la période
  précédente de même durée (du 17/09/2026 au 30/09/2026) », :29-66, valeurs de
  t12_ventes.DELTAS ; en-tête de module « Ventes & évolution » « CA · Marge ·
  CMV », :114-128) et dashboard_shell.xml (onglets, filtres, rangée Caisse
  :143-160, bouton « Tous » des jours et raccourcis « Semaine (lun–ven) » /
  « Week-ends », :195-214) ; menu Point de Vente → Analyse, section « Analyse
  AITE » (pos_analytics_menus.xml, écart n° 67 ; ecrans.MENUS_MUK) ;
- aite_purchase_dashboard/static/src/xml/dashboard.xml (« Délai de paiement
  (DPO) » « 12,1 j », « Factures échues » en montant positif, sans liseré
  (carte non « mega », :5-6), « Livré à temps et complet (OTIF) », « part
  des commandes reçues · cible ≥ 90 % », « 1 facture » ; rangée Période
  avec ses dates « 01/10/2026 » → « 14/10/2026 » et « Appliquer », :37-52 ;
  une pastille de couleur par fournisseur, dans l'ordre de get_suppliers,
  :54-63 ; titres de rangée « Vue d'ensemble », « Indicateurs » et
  « Répartition & flux », :124-125 ; mois abrégés sans l'année), barre
  d'onglets (purchase_dashboard_view.js:169-177 ; un onglet sans bordure, seul
  l'actif a un fond, purchase_dashboard.scss:121-145). Les chiffres sont ceux de
  scenarios/t14_achats.py lus le 14/10 (période du 01/10 au 14/10, quatorze
  jours ; la commande P00158 du 15/10 n'existe pas encore), recalculés plus
  bas avec les fonctions du module (t14_achats._F) : « 7 commandes · 6
  réceptions », 1 742 000 FCFA (Wouri 964 000, Akwa 378 000, Bonapriso
  252 000, Hygiène 148 000) ; « 1 commande » en cours, P00157, « 116 000 FCFA
  attendus · 0 en retard » (un jour après la date prévue, sous la tolérance
  de 2 j) ; 5 des 6 réceptions à temps et complètes, « 83,3 % » ; DPO
  1 280 000 / 1 478 000 × 14 = « 12,1 j » ; 409 = 265 800 de consignes +
  53 400 d'avoirs = 319 200 FCFA (avant le retour des 20 casiers du 16/10).
  Dettes identiques à t14 et t15 : 1 280 000 sur 4 factures, 180 000 échus
  (1 facture), 420 000 sous 7 j. Barres « Factures vs Paiements » : la série
  de t14 (FLUX) sur un axe de 0 à 5 M ; les factures d'octobre sont les mêmes
  1 478 000 au 14 et au 16/10, les paiements sont des constantes de t14 ;
- aite_slot_booking/static/src/xml/dashboard.xml et js/views (« 5
  réalisées », « Non présentés » « 0,0 % », « 0 rendez-vous manqué », « 6
  réservations à venir », « Planning du 17/10/2026 » ; couloirs à l'échelle
  de chaque ressource, laneStyle / laneTicks :205-225, sans heures écrites ;
  « x/y créneaux libres », un créneau entamé restant libre, boardFreeText
  :231-245, écart n° 59).

Jour rejoué : le mercredi 14/10/2026, comme scenarios/t15_direction.py. La
période « Ce mois » démarre désormais le 1er en date locale (écart n° 38
corrigé) : « Du 01/10/2026 au 14/10/2026 », quatorze jours. Hébergement : une
seule source pour le cockpit, l'activité par pôle et le tableau de bord de la
réception (exec_dashboard.py:50-56), donc les chiffres de c1_reception.py et
t01_reception.py : 179 nuitées sur 20 chambres × 14 jours = 280 (les 192 d'avant
comptaient la nuit du 30/09), 8 055 000 FCFA à 45 000 FCFA la nuit, 63,9 %,
RevPAR 28 768 FCFA ; écarts sur la même période N-1 inchangés (+8,2 %, +3,1 %,
+11,6 %). Ventes du 01 au 13/10 (t12, t15) : 3 120 000 FCFA HT, 222 857 FCFA
par jour sur 14 jours, ▲ +9,4 % sur la période précédente ; top 8 du mois de
t12_ventes.py (TOP8_MOIS). Activité par pôle : 8 055 000 + 3 120 000 +
1 240 000 = 12 415 000 FCFA. Montants hors taxes (ECARTS n° 25). Position
nette négative (dettes > ardoises) : « vos fournisseurs financent
l'exploitation » (direction_dashboard.py:98-111, ECARTS n° 24).
Espaces & Prestations : les indicateurs de la période par défaut,
« Aujourd'hui » (slot_dashboard_view.js:30-34), et le planning du samedi 17/10,
celui de scenarios/t08_site_web.py (JOUR_17, mêmes huit ressources dont le
comptoir pressing de capacité 2, mêmes réservations) : la réservation en ligne
de Claire Durand (CRN/2026/0131, demo.CRENEAU_SALON, 16:00-17:00) est sur le
salon Wouri. Indicateurs du 14/10 repris de t08 : 61 800 FCFA réalisés (5
prestations), 20 h réservées sur 109 h ouvrées, aucun non-présenté, 2 retraits
pressing en attente, 6 réservations à venir.
"""

import re
from datetime import date

import demo
from scenarios import t12_ventes, t14_achats
from ecrans import (ICONES, MENUS_MUK, NBSP, NNBSP, compte, e, entier, fcfa, fenetre, graphe_anneau, graphe_barres,
                    graphes, jours, kpi, mois_abrege, pct, sens, tdb_entete, tdb_filtres, tdb_section, variation, vue_tdb)
from moteur import anneau, cacher, clic, compter, curseur, defiler, montrer, pause, vue

NOM, ROLE = demo.POSTES['direction']


def barre(ident, app, menus, actif=None, societe=demo.SOCIETE):
    """Une barre d'application de rechange, posée sur celle de la fenêtre. Les neuf menus de l'Hôtel ne tiennent
    dans la fenêtre de la vidéo qu'avec un espacement resserré (et sans le nom de la société, comme c7)."""
    entrees = ''.join('<span class="menu%s">%s</span>' % (' actif' if m == actif else '', e(m)) for m in menus)
    serre = ' style="gap:17px"' if len(menus) > 8 else ''
    return ('<div class="o-haut barre-app masque" id="%s"%s><span class="grille">%s</span><span class="nom-app">%s</span>%s'
            '<span class="droite"><span class="pictos">%s</span><span class="societe">%s</span>'
            '<span class="avatar" style="background:#854F0B">%s</span></span></div>'
            % (ident, serre, ICONES['grille'], e(app), entrees, ICONES['bulle'], e(societe), e(NOM[0])))


# Les barres du profil Direction (responsable) : Hôtel avec « Activité par pôle » en tête (exec_menus.xml) ;
# Point de Vente sans « Analyse AITE », devenue une section du menu « Analyse » (écart n° 67) ; Achats.
MENUS_HOTEL = MENUS_MUK['hotel_direction']
BARRES = (barre('c6-nav-pos', 'Point de Vente', MENUS_MUK['point_de_vente'], 'Analyse')
          + barre('c6-nav-achats', 'Achats', MENUS_MUK['achats'], 'Tableau de bord AITE')
          + barre('c6-nav-esp', 'Hôtel', MENUS_HOTEL, 'Espaces & Prestations', '')
          + barre('c6-nav-exec', 'Hôtel', MENUS_HOTEL, 'Activité par pôle', ''))


def m(n):
    """fmtMoney des tableaux de bord (toLocaleString fr-FR : espace fine, trait d'union d'un négatif) + « FCFA »."""
    return fcfa(n, tdb=True)


def court(n):
    """moneyShort du cockpit (direction_dashboard.js:362-364) : le nombre seul, sans symbole."""
    return entier(n, tdb=True)


def _sp(t):
    return t.replace(NBSP, ' ').replace(NNBSP, ' ')


def libelles_larges(html):
    """« Fournisseur », « Période stats » ne tiennent pas dans la colonne des libellés de filtre (130 px)."""
    return html.replace('<span class="tdb-lib">', '<span class="tdb-lib" style="width:156px">')


def contenir(html, n):
    """Une rangée de cartes qui tient dans la largeur : colonnes égales (minmax(0, 1fr)), libellés et sous-titres
    qui passent à la ligne comme dans l'application (au lieu de pousser la dernière carte hors de la fenêtre)."""
    grille = '<div class="tdb-grille c%d">' % n
    assert html.count(grille) == 1
    return (html.replace(grille, '<div class="tdb-grille c%d" style="grid-template-columns:repeat(%d,minmax(0,1fr))">'
                         % (n, n))
            .replace('<div class="kpi-l">', '<div class="kpi-l" style="white-space:normal">')
            .replace('<div class="kpi-s">', '<div class="kpi-s" style="white-space:normal">'))


def note(html, apres, texte_):
    """Une note grise en bout de rangée de filtres (add-note, direction_dashboard.xml:181-182 et :194)."""
    fin = '%s</span></div>' % e(apres)          # la dernière puce de la rangée, pastille comprise
    assert html.count(fin) == 1
    return html.replace(fin, '%s</span><span style="margin-left:16px;font-size:15px;color:var(--o-texte-3)">%s</span>'
                        '</div>' % (e(apres), e(texte_)))


def pastilles(html, couleurs):
    """La pastille de couleur de chaque caisse (add-dotc, direction_dashboard.xml:172-177)."""
    for nom, coul in couleurs:
        puce_ = '<span class="chip">%s</span>' % e(nom)
        assert html.count(puce_) == 1
        html = html.replace(puce_, '<span class="chip"><i style="display:inline-block;width:10px;height:10px;'
                            'border-radius:50%%;background:%s;margin-right:8px"></i>%s</span>' % (coul, e(nom)))
    return html


# ------------------------------------------------------------ les chiffres --
# Période « Ce mois » : du 01/10 au 14/10/2026, quatorze jours (dates locales depuis la livraison 4).
JOURS_PERIODE = 14
# Ventes (t12_ventes.py, t15) : 128 tickets du 01 au 13/10.
CA, MARGE, TICKETS, UNITES = 3120000, 1747200, 128, 512
CMV = CA - MARGE
# Hébergement (c1_reception.py, t01) : 179 nuitées à 45 000 FCFA, 20 chambres vendables × 14 jours.
NUITEES, ADR, CHAMBRES = 179, 45000, 20
CA_NUITEES = NUITEES * ADR
DISPO = CHAMBRES * JOURS_PERIODE
OCC, REVPAR = NUITEES * 100.0 / DISPO, CA_NUITEES / float(DISPO)
D_CA_NUITEES, D_OCC, D_ADR, D_REVPAR = 11.6, 8.2, 3.1, 11.6        # vs la même période l'an dernier
PICKUP, PICKUP_RES, PACE, PACE_N1 = 46, 18, 412, 387
D_PACE = (PACE - PACE_N1) * 100.0 / PACE_N1
# Prestations (t09, t15) et total de l'activité par pôle.
PRESTATIONS, NB_PRESTATIONS = 1240000, 46
TOTAL = CA_NUITEES + CA + PRESTATIONS
MIX = [('Hébergement', CA_NUITEES, '#714B67'), ('Restauration & boutique', CA, '#185FA5'),
       ('Prestations', PRESTATIONS, '#0F6E56')]
assert _sp(pct(OCC) + m(REVPAR) + m(CA / JOURS_PERIODE) + m(MARGE / TICKETS) + m(CMV / UNITES)) == (
    '63,9 %28 768 FCFA222 857 FCFA13 650 FCFA2 681 FCFA')
assert (CA_NUITEES, TOTAL, round((1 + D_OCC / 100) * (1 + D_ADR / 100) * 100 - 100, 1)) == (8055000, 12415000, D_REVPAR)
assert [pct(v * 100.0 / TOTAL) for _, v, _ in MIX] == [pct(64.9), pct(25.1), pct(10.0)]

# ----------------------------------------------------------- le cockpit --
VUES = ["Vue d'ensemble", 'Ventes (POS)', 'Crédit clients', 'Stock', 'Achats', 'À traiter']
COCKPIT = vue_tdb('c6-cockpit', '<div id="c6-in">%s</div>' % (
    tdb_entete('Direction — Vue consolidée', 'POS · Crédit clients · Stock · Achats — %s' % demo.SOCIETE)
    # Rangées PÉRIODE, CAISSE, HEURE, JOUR (multi-sélection, aucun jour coché), VUE (direction_dashboard.xml:143-199).
    + note(note(pastilles(tdb_filtres([
        ('Période', ['Toute la période', "Aujourd'hui", 'Cette semaine', 'Ce mois', 'Ce trimestre', 'Cette année'], 3),
        # toutes les caisses de la société (get_meta, direction_dashboard.py:531-532), couleur par rang
        # (CAISSE_COLORS, direction_dashboard.js:21, :599-603)
        ('Caisse', ['Toutes les caisses', 'Bar de la terrasse', 'Restaurant', 'Boutique'], 0),
        ('Heure', ['Toute la journée', 'Matin 6–12h', 'Après-midi 12–18h', 'Soir 18–23h', 'Nuit 23–6h'], 0),
        ('Jour', ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'], -1),
        ('Vue', VUES, 0)]), [('Bar de la terrasse', '#714B67'), ('Restaurant', '#185FA5'), ('Boutique', '#3B6D11')]),
        'Boutique', 'caisse, heure et jours filtrent les données de vente'), 'Dim', 'multi-sélection — aucun = tous')
    + tdb_section("Santé de l'affaire", [
        kpi('c6-k-ca', 'CA encaissé', m(CA), 'HT · %s · POS payés / facturés' % compte(TICKETS, 'ticket', 'tickets'),
            'vert', (9.4, 'vs période précédente')),
        kpi('c6-k-marge', 'Marge brute réalisée', m(MARGE), '%s du CA · CA − coût des ventes' % pct(MARGE * 100.0 / CA),
            'teal'),
        kpi('c6-k-risque', 'Cash à risque', m(143000),
            'ardoises +30 j (%s) + coulage (%s)' % (court(101500), court(41500)), 'rouge'),
        kpi('c6-k-net', 'Crédits clients − dettes fournisseurs', m(150000 - 1280000),
            "%s d'ardoises · %s de dettes — vos fournisseurs financent l'exploitation" % (court(150000), court(1280000)),
            'bleu')])
    + tdb_section("L'essentiel par pôle — cliquer une carte ouvre l'onglet", [
        kpi('c6-p-tix', 'Ventes — tickets', entier(TICKETS, tdb=True), 'panier moyen ' + m(CA / TICKETS), 'violet'),
        kpi('c6-p-ard', 'Encours ardoises', m(150000),
            '%s · %s en retard (+30 j)' % (compte(5, 'débiteur', 'débiteurs'), court(101500)), 'ambre'),
        kpi('c6-p-four', 'Dettes fournisseurs', m(1280000), '%s échues · %s sous 7 j' % (court(180000), court(420000)),
            'bleu'),
        kpi('c6-p-stock', 'Stock — valeur / alertes', m(3185000),
            '%s · coulage %s' % (compte(2, 'référence en alerte', 'références en alerte'), pct(0.6)), 'violet')])
    + contenir(tdb_section('Hébergement — écarts vs même période N-1 ; cliquer une carte ouvre « Direction — '
                           'Activité par pôle »', [
        kpi('c6-h-ca', 'CA des nuitées (HT)', m(CA_NUITEES),
            '%s · rythme du mois (pace) : %s (N-1 : %s)' % (compte(NUITEES, 'nuitée vendue', 'nuitées vendues'),
                                                         entier(PACE, tdb=True), entier(PACE_N1, tdb=True)),
            'vert', D_CA_NUITEES, aide=True),
        kpi('c6-h-occ', "Taux d'occupation", pct(OCC),
            'réservations récentes (pickup) : %s ces 7 j pour les 30 prochains'
            % compte(PICKUP, 'nuitée prise', 'nuitées prises'), None, D_OCC, aide=True),
        kpi('c6-h-adr', 'Prix moyen par nuit (ADR)', m(ADR), 'CA hébergement ÷ nuitées vendues', None, D_ADR,
            aide=True),
        kpi('c6-h-revpar', 'Revenu par chambre disponible (RevPAR)', m(REVPAR), 'par chambre disponible, vendue ou non',
            'teal', D_REVPAR, aide=True)]), 4)),
    initiale=True)

# Les pastilles « période » / « photo » des cartes du cockpit (KpiCard badge, direction_dashboard.xml:10-12,
# :222-305 ; add-badge, direction_dashboard.scss:144-148) : une mesure sur la période, ou l'état à l'instant.
BADGES = [('c6-k-ca', 'per'), ('c6-k-marge', 'per'), ('c6-k-risque', 'per'), ('c6-k-net', 'photo'),
          ('c6-p-tix', 'per'), ('c6-p-ard', 'photo'), ('c6-p-four', 'photo'), ('c6-p-stock', 'photo'),
          ('c6-h-ca', 'per'), ('c6-h-occ', 'per'), ('c6-h-adr', 'per'), ('c6-h-revpar', 'per')]


def pastille_carte(html, ident, sorte):
    motif = re.compile(r'id="%s"><div class="kpi-l"(?: style="([^"]*)")?>' % re.escape(ident))
    assert len(motif.findall(html)) == 1, ident
    style = 'background:#f3eff2;color:#714B67' if sorte == 'per' else 'background:#eeede8;color:#62615C'
    return motif.sub(lambda m: 'id="%s" style="position:relative"><span style="position:absolute;top:10px;right:12px;'
                     'font-size:13px;font-weight:700;border-radius:9px;padding:1px 8px;%s">%s</span>'
                     '<div class="kpi-l" style="%spadding-right:78px">'
                     % (ident, style, 'période' if sorte == 'per' else 'photo', (m.group(1) or '') + ';'), html)


for _ident, _sorte in BADGES:
    COCKPIT = pastille_carte(COCKPIT, _ident, _sorte)

# ------------------------------------------------------ ventes (POS) --
# Analyse AITE : onglets (TABS, utils.js:318-329) et filtres (dashboard_shell.xml:120-215 : jours avec « Tous »).
ONGLETS_POS = ['Tableau de bord', 'Par caisse', 'Sessions POS', 'Articles', 'Marges & CMV', 'Par catégorie',
               'Écarts de caisse', 'Paiements']
# Top 8 du mois (t12_ventes.TOP8_MOIS) : (article, CA, marge) ; étiquettes coupées à 9 caractères + « … »
# au-delà de 10 (dashboard_view.js:133-134).
TOP8 = [('Bière blonde 65 cl', 486000, 275400), ('Champagne brut 75 cl', 450000, 230000),
        ('Whisky 12 ans 70 cl', 440000, 242000), ('Cognac VSOP 70 cl', 420000, 224000),
        ('Vin rouge 75 cl', 312000, 195000), ('Gin 70 cl', 286000, 156000), ('Rhum ambré 70 cl', 220000, 121000),
        ('Vin blanc 75 cl', 132000, 84000)]


def etiquette(nom):
    return nom if len(nom) <= 10 else nom[:9] + '…'


def top8(identifiant):
    """« Top 8 articles — CA vs Marge » : barres CA (violet) et marge (vert) par article."""
    haut = 500000.0
    barres = ''.join('<div style="flex:1;display:flex;align-items:flex-end;justify-content:center;gap:3px;height:100%%">'
                     '<i class="g-b" style="flex:none;width:22px;height:%.0f%%;background:#714B67"></i>'
                     '<i class="g-b" style="flex:none;width:22px;height:%.0f%%;background:#3B6D11"></i></div>'
                     % (ca * 100 / haut, mg * 100 / haut) for _, ca, mg in TOP8)
    labs = ''.join('<span style="flex:1;text-align:center;font-size:12px">%s</span>' % e(etiquette(n)) for n, _, _ in TOP8)
    return ('<div class="g-carte" style="height:226px"><div class="g-titre">Top 8 articles — CA vs Marge</div>'
            '<div class="g-barres" id="%s" style="gap:0;justify-content:stretch">%s</div>'
            '<div class="g-lab" style="justify-content:stretch">%s</div></div>' % (identifiant, barres, labs))


def evolution_mois():
    """« Évolution mensuelle (CA · CMV · Marge) » sur la période « Ce mois » : un seul point, « octobre 2026 »
    (get_monthly_evolution, regroupement date:month d'Odoo), CA plein, CMV et marge en pointillés. Chart.js
    (dashboard_view.js:159-185) cadre l'axe sur les données, sans partir de zéro : de 1,2 M à 3,2 M, pas de
    0,2 M, graduations fmtCompact « 1,2 M » ; les trois points restent donc séparés. Les points sont posés hors
    du SVG étiré, pour rester ronds."""
    bas, haut_, h = 1200000.0, 3200000.0, 150
    points = ''.join('<i style="position:absolute;left:50%%;top:%.1f%%;width:12px;height:12px;margin:-6px 0 0 -6px;'
                     'border-radius:50%%;background:#fff;border:3px solid %s;box-sizing:border-box"></i>'
                     % ((haut_ - v) * 100 / (haut_ - bas), c) for v, c in ((CA, '#714B67'), (CMV, '#A32D2D'),
                                                                          (MARGE, '#3B6D11')))
    axe = ''.join('<span style="position:absolute;right:calc(100%% + 8px);top:%.1f%%;transform:translateY(-50%%);'
                  'font-size:11px;color:var(--o-texte-3);white-space:nowrap">%s</span>'
                  % ((haut_ - k * 100000.0) * 100 / (haut_ - bas), ('%.1f' % (k / 10.0)).replace('.', ',') + NBSP + 'M')
                  for k in range(12, 33, 2))
    leg = ('<span style="display:inline-flex;gap:14px;font-size:14px;color:var(--o-texte-2);margin-left:18px">'
           '<span><i style="display:inline-block;width:16px;border-top:3px solid #714B67;vertical-align:middle"></i> CA</span>'
           '<span><i style="display:inline-block;width:16px;border-top:3px dashed #A32D2D;vertical-align:middle"></i> CMV</span>'
           '<span><i style="display:inline-block;width:16px;border-top:3px dashed #3B6D11;vertical-align:middle"></i> Marge'
           '</span></span>')
    grille = ''.join('<line x1="0" x2="760" y1="%.1f" y2="%.1f" stroke="#E5E7EB"/>' % (y, y)
                     for y in [i * h / 10.0 for i in range(11)])
    return ('<div class="g-carte" style="height:226px"><div class="g-titre">Évolution mensuelle (CA · CMV · Marge)%s</div>'
            '<div class="g-zone" style="left:66px;top:50px;bottom:36px"><svg viewBox="0 0 760 %d" '
            'preserveAspectRatio="none">%s</svg>%s%s</div>'
            '<div class="g-lab" style="left:66px;bottom:10px;justify-content:center"><span>%s</span></div></div>'
            % (leg, h, grille, points, axe, e('octobre 2026')))


def raccourcis(html):
    """« Semaine (lun–ven) » et « Week-ends », poussés à droite de la rangée Jour (dashboard_shell.xml:200-214)."""
    fin = '<span class="chip">Dim</span></div>'
    assert html.count(fin) == 1
    return html.replace(fin, '<span class="chip">Dim</span><span style="flex:1"></span><span class="chip">Semaine '
                        '(lun–ven)</span><span class="chip">Week-ends</span></div>')


# La bande « Évolution par rapport à la période précédente de même durée » (views.xml:29-66, écart n° 62) :
# les quatre variations de t12_ventes.DELTAS, un CMV qui monte en rouge.
BANDE = ('<div style="margin:14px 2px 6px;font-size:15px;color:var(--o-texte-3)">Évolution par rapport à la période '
         'précédente de même durée (du %s au %s)</div><div class="tdb-grille c4" style="gap:12px">%s</div>'
         % (t12_ventes.PREC_DU, t12_ventes.PREC_AU, ''.join(
             '<div style="height:50px;background:#fff;border:1px solid rgba(0,0,0,.08);border-radius:10px;padding:0 18px;'
             'display:flex;align-items:center;justify-content:space-between"><span style="font-size:16px;'
             'color:var(--o-texte-3)">%s</span><b style="font-size:19px;color:%s">%s</b></div>'
             % (e(lib), {'haut': '#3B6D11', 'bas': '#A32D2D', 'nul': 'var(--o-texte-3)'}[sens(v, mauvaise)],
                variation(v)) for lib, v, mauvaise in t12_ventes.DELTAS)))
assert variation(t12_ventes.DELTAS[0][1]) == variation(9.4)
# L'en-tête du module des graphiques (views.xml:114-128).
MODULE_VENTES = ('<div style="display:flex;align-items:center;gap:12px;margin:16px 2px 10px"><span style="width:38px;'
                 'height:38px;border-radius:9px;background:#714B67;color:#fff;display:inline-flex;align-items:center;'
                 'justify-content:center"><span style="width:20px;height:20px;display:inline-flex">%s</span></span><div>'
                 '<div style="font-size:19px;font-weight:700;color:#714B67">Ventes &amp; évolution</div>'
                 '<div style="font-size:14px;color:var(--o-texte-3)">CA · Marge · CMV</div></div></div>' % ICONES['graphe'])

VENTES = vue_tdb('c6-ventes', '<div id="c6-in-v">%s</div>' % (
    '<div class="tdb-filtres" style="margin-top:0"><div class="tdb-rang">%s</div></div>'
    % ''.join('<span class="chip%s">%s</span>' % (' actif' if i == 0 else '', e(o)) for i, o in enumerate(ONGLETS_POS))
    # Période, Caisse (pastille de chaque caisse, dashboard_shell.xml:143-160), Heure, Jour.
    + raccourcis(pastilles(tdb_filtres([
        ('Période', ['Toute la période', "Aujourd'hui", 'Cette semaine', 'Ce mois', 'Ce trimestre', 'Cette année'], 3),
        ('Caisse', ['Toutes les caisses', t12_ventes.BAR, t12_ventes.RESTO, t12_ventes.BOUT], 0),
        ('Heure', ['Toute la journée', 'Matin 6–12h', 'Après-midi 12–18h', 'Soir 18–23h', 'Nuit 23–6h'], 0),
        ('Jour', ['Tous', 'Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'], 0)]),
        [(c, t12_ventes.COULEUR_CAISSE[c]) for c in (t12_ventes.BAR, t12_ventes.RESTO, t12_ventes.BOUT)]))
    + '<div style="height:14px"></div><div class="tdb-grille c4">%s</div>' % ''.join([
        kpi('c6-v-ca', "Chiffre d'affaires", m(CA),
            'HT · %s / jour · %d j' % (m(CA / JOURS_PERIODE), JOURS_PERIODE), 'bleu'),
        kpi('c6-v-marge', 'Marge brute', m(MARGE),
            'Taux%s: %s · %s / ticket' % (NBSP, pct(MARGE * 100.0 / CA), m(MARGE / TICKETS)), 'vert'),
        kpi('c6-v-cmv', 'CMV (coût marchandises)', m(CMV), '%s du CA · %s / unité' % (pct(CMV * 100.0 / CA),
                                                                                   m(CMV / UNITES)), 'rouge'),
        kpi('c6-v-tx', 'Transactions', entier(TICKETS, tdb=True),
            'Panier moyen %s · %s' % (m(CA / TICKETS), compte(UNITES, 'unité', 'unités')), 'violet')])
    + BANDE
    + '<div style="height:14px"></div><div class="tdb-grille c4">%s</div>' % ''.join([
        kpi('c6-v-ratio', 'Ratio CMV/CA', pct(CMV * 100.0 / CA), 'Bonne maîtrise ✓'),
        kpi('c6-v-taux', 'Taux de marge', pct(MARGE * 100.0 / CA), 'Objectif atteint ✓'),
        kpi('c6-v-art', 'Articles actifs', '42 / 48', 'références vendues'),
        kpi('c6-v-best', 'Meilleur article', TOP8[0][0], m(TOP8[0][1]) + ' CA')])
    + MODULE_VENTES
    + graphes(top8('c6-g-top'), evolution_mois())
    + '<div style="height:24px"></div>'))

# --------------------------------------------------------------- achats --
# Les pièces de scenarios/t14_achats.py (COMMANDES, FACTURES, FACTURES_PAYEES, CONSIGNES, AVOIRS, FLUX), lues par le
# moteur Achats le 14/10 et non le 16/10 comme t14 : « Ce mois » va du 01/10 au 14/10, quatorze jours. Le calcul est
# celui du module (t14_achats._F : _order_metrics, _invoice_metrics, _dpo, extraits de purchase_dashboard.py), avec
# les réglages par défaut (t14_achats.CFG : à payer sous 7 j, tolérance de retard 2 j).
T14, F14, CFG = t14_achats, t14_achats._F, t14_achats.CFG
AUJ, DU = date(2026, 10, 14), date(2026, 10, 1)
assert (AUJ - DU).days + 1 == JOURS_PERIODE


def commandes_achats():
    """_order_rows (purchase_dashboard.py:300-358) : les commandes datées de la période. P00158, passée le 15/10,
    n'existe pas encore ; P00157, prévue le 13/10, n'a qu'un jour de retard, sous la tolérance : « En attente »."""
    rows = []
    for d_cmd, four, ref, prevue, recue, statut, lignes in T14.COMMANDES:
        if not DU <= d_cmd <= AUJ:
            continue
        assert recue is None or recue <= AUJ, ref
        pending = statut == 'pending'
        retard = max(0, ((AUJ if pending else recue) - prevue).days)
        rows.append(dict(four=four, ref=ref, pending=pending, days_late=retard, montant=sum(q * p for _, q, p in lignes),
                         **F14['_order_metrics'](pending, retard, None if pending else statut == 'full', CFG['late'])))
    return rows


def factures_achats():
    """_open_bill_rows (purchase_dashboard.py:248-287) : les factures comptabilisées non soldées, au 14/10."""
    rows = []
    for four, ref, d_fac, due, total, paye in T14.FACTURES:
        assert d_fac <= AUJ, ref
        rows.append(dict(four=four, ref=ref, residual=total - paye, days_late=max(0, (AUJ - due).days),
                         days_to_due=max(0, (due - AUJ).days)))
    return rows


CMD = commandes_achats()
ACHATS = sum(c['montant'] for c in CMD)
RECUES = [c for c in CMD if not c['pending']]
EN_COURS = [c for c in CMD if c['pending']]
A_TEMPS = len([c for c in RECUES if c['otif']])
EN_RETARD = len([c for c in EN_COURS if c['days_late'] > CFG['late']])
FAC = factures_achats()
ENCOURS = sum(f['residual'] for f in FAC)
ECHUES = [f for f in FAC if f['days_late'] > 0]
SOUS7 = [f for f in FAC if f['days_late'] == 0 and f['days_to_due'] <= CFG['soon']]
# DPO : encours / factures fournisseurs de la période (soldées comprises) × jours (get_kpis, :684-696).
FAC_PERIODE = (sum(t for _, _, d, _, t, _ in T14.FACTURES if DU <= d <= AUJ)
               + sum(t for _, _, d, t in T14.FACTURES_PAYEES if DU <= d <= AUJ))
DPO = F14['_dpo'](ENCOURS, FAC_PERIODE or ACHATS, JOURS_PERIODE)
# 409 (get_claims, domaine corrigé : lignes débitrices du 401) : consignes + avoirs + acomptes, le registre avant le
# retour des 20 casiers du 16/10 ; les trois avoirs sont antérieurs au 14/10.
assert T14.DOMAINE_409 == 'debit' and all(a[0] <= AUJ for a in T14.AVOIRS)
CREANCES = T14._creances(T14.CONSIGNES)['total']
# L'anneau : achats de la période par fournisseur, triés par montant (get_supplier_rows, :609-654), couleur de chacun
# dans l'ordre de _supplier_universe (t14_achats.COULEUR), comme les puces du filtre (get_suppliers, :200-217).
PARTS = sorted(((f, sum(c['montant'] for c in CMD if c['four'] == f), T14.COULEUR[f]) for f in T14.FOURNISSEURS),
               key=lambda p: -p[1])
# Les barres : la série de t14 (FLUX, factures / paiements de mai à octobre) sur l'axe de t14, de 0 à 5 M ; les
# factures d'octobre sont celles de la période, les mêmes au 14 et au 16/10.
FLUX_AXE = 5000000.0
assert T14.FLUX[-1][1] == FAC_PERIODE
BARRES_FLUX = [(int(round(v * 100 / FLUX_AXE)), coul) for _, fac, pay in T14.FLUX
               for v, coul in ((fac, '#714B67'), (pay, '#3B6D11'))]
assert (ACHATS, len(CMD), len(RECUES), A_TEMPS, sum(c['montant'] for c in EN_COURS), EN_RETARD) == (
    1742000, 7, 6, 5, 116000, 0)
assert (ENCOURS, len(FAC), sum(f['residual'] for f in ECHUES), len(ECHUES), sum(f['residual'] for f in SOUS7),
        len(SOUS7)) == (1280000, 4, 180000, 1, 420000, 1)
assert (FAC_PERIODE, jours(DPO), CREANCES, _sp(pct(A_TEMPS * 100.0 / len(RECUES)))) == (1478000, '12,1 j', 319200, '83,3 %')
assert [(n, v) for n, v, _ in PARTS] == [('Boissons du Wouri SARL', 964000), ('Dépôt Akwa Distribution', 378000),
                                        ('Épicerie Fine Bonapriso', 252000), ('Hygiène Pro Littoral', 148000)]
assert BARRES_FLUX == [(80, '#714B67'), (75, '#3B6D11'), (72, '#714B67'), (78, '#3B6D11'), (86, '#714B67'),
                       (81, '#3B6D11'), (77, '#714B67'), (73, '#3B6D11'), (88, '#714B67'), (84, '#3B6D11'),
                       (30, '#714B67'), (24, '#3B6D11')]
# La dette du cockpit (« Crédits clients − dettes fournisseurs », « Dettes fournisseurs ») est la même.
assert (ENCOURS, sum(f['residual'] for f in ECHUES), sum(f['residual'] for f in SOUS7)) == (1280000, 180000, 420000)

ONGLETS_ACHATS = ['Tableau de bord', 'Fournisseurs', 'Dettes & échéancier', 'Avoirs & consignes',
                  'Commandes & réceptions', 'Prix & variations']          # purchase_dashboard_view.js:169-177
# Le champ de date du navigateur (input type="date", dashboard.xml:44-52) : la date et son calendrier, comme t14.
CAL = ('<svg class="c6-cal" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">'
       '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/></svg>')


def filtres_achats():
    """Période (et ses dates, poussées à droite par apd-spacer, puis « Appliquer ») ; Fournisseur : « Tous », puis
    chaque fournisseur dans l'ordre de get_suppliers, avec sa pastille (apd-dot)."""
    html = libelles_larges(tdb_filtres([('Période', ["Aujourd'hui", 'Cette semaine', 'Ce mois', '3 mois'], 2),
                                        ('Fournisseur', ['Tous'] + T14.FOURNISSEURS, 0)]))
    fin = '<span class="chip">3 mois</span></div>'
    assert html.count(fin) == 1
    html = html.replace(fin, '<span class="chip">3 mois</span><span class="c6-date c6-esp">%s%s</span>'
                        '<span class="c6-fl">→</span><span class="c6-date">%s%s</span><span class="chip">Appliquer</span>'
                        '</div>' % (e(DU.strftime('%d/%m/%Y')), CAL, e(AUJ.strftime('%d/%m/%Y')), CAL))
    for four in T14.FOURNISSEURS:
        puce_ = '<span class="chip">%s</span>' % e(four)
        assert html.count(puce_) == 1
        html = html.replace(puce_, '<span class="chip"><i class="c6-pt" style="background:%s"></i>%s</span>'
                            % (T14.COULEUR[four], e(four)))
    return html


ACHATS_VUE = vue_tdb('c6-achats', (
    tdb_entete('Achats & Fournisseurs — Tableau de bord', 'Dettes (401) & créances fournisseurs (409) · échéancier · OTIF · prix')
    + filtres_achats()
    # La barre d'onglets (apd-tabbar) : un onglet sans bordure, seul l'actif a un fond (purchase_dashboard.scss
    # :121-145), comme t14 (.t14-onglets).
    + '<div class="c6-onglets">%s</div>'
    % ''.join('<span class="c6-onglet%s">%s</span>' % (' actif' if i == 0 else '', e(o)) for i, o in enumerate(ONGLETS_ACHATS))
    + tdb_section("Vue d'ensemble", [
        kpi('c6-a-achats', 'Achats (période)', m(ACHATS),
            compte(len(CMD), 'commande', 'commandes') + ' · ' + compte(len(RECUES), 'réception', 'réceptions'), 'bleu'),
        kpi('c6-a-dette', 'Dette fournisseurs (401)', m(ENCOURS), compte(len(FAC), 'facture ouverte', 'factures ouvertes'),
            'rouge'),
        kpi('c6-a-7j', 'À payer sous %s j' % entier(CFG['soon'], tdb=True), m(sum(f['residual'] for f in SOUS7)),
            compte(len(SOUS7), 'facture', 'factures') + ' · trésorerie à prévoir', 'ambre'),
        kpi('c6-a-dpo', 'Délai de paiement (DPO)', jours(DPO), 'encours / factures période · tenir les délais négociés',
            'violet')])
    # « Factures échues » : une dette en montant positif, sans liseré (seules les cartes « mega » en portent un,
    # dashboard.xml:5-6 et :110-112).
    + tdb_section('Indicateurs', [
        kpi('c6-a-retard', 'Factures échues', m(sum(f['residual'] for f in ECHUES)),
            "%s · %s de l'encours" % (compte(len(ECHUES), 'facture', 'factures'),
                                      pct(sum(f['residual'] for f in ECHUES) * 100.0 / ENCOURS))),
        kpi('c6-a-409', 'Créances fournisseurs (409)', m(CREANCES), 'consignes + avoirs + acomptes'),
        kpi('c6-a-otif', 'Livré à temps et complet (OTIF)', pct(A_TEMPS * 100.0 / len(RECUES)),
            'part des commandes reçues · cible ≥ 90 %'),
        kpi('c6-a-cmd', 'Commandes en cours', compte(len(EN_COURS), 'commande', 'commandes'),
            '%s attendus · %s en retard' % (m(sum(c['montant'] for c in EN_COURS)), entier(EN_RETARD, tdb=True)))])
    # « Répartition & flux » sépare les indicateurs des graphiques (dashboard.xml:124-125), comme t14 (_vue_tableau).
    + '<div class="tdb-sect">Répartition &amp; flux</div>'
    + graphes(graphe_anneau('c6-g-four', 'Achats par fournisseur (période)', [p for p in PARTS if p[1] > 0]),
              graphe_barres('c6-g-fp', 'Factures vs Paiements — 6 mois', BARRES_FLUX,
                            etiquettes=[mois_abrege(x) for x in range(5, 11)]))))

# ---------------------------------------------------- espaces & prestations --
# Les huit ressources (scenarios/t09_espaces.py, même ordre ; couleur de la famille) et le planning du
# samedi 17/10 (scenarios/t08_site_web.py, JOUR_17) : (nom, couleur, ouverture, fermeture, pas en minutes, capacité,
# [(début h, fin h, client, identifiant)]). Chaque couloir a sa propre échelle, de l'ouverture à la fermeture
# de la ressource, avec un repère toutes les deux heures (laneStyle, laneTicks) ; un créneau n'est pris que
# plein (boardFreeText, booking_resource.py:106-142).
RESSOURCES = [
    ('Salon VIP Wouri', '#714B67', 9, 23, 60, 1, [(12, 14, 'Aline Nkengue', None),
                                                  (16, 17, demo.POSTES['client'][0], 'c6-bk-claire'),
                                                  (19, 21, 'Gilbert Tchoua', None)]),
    ('Salon VIP Sanaga', '#714B67', 9, 23, 60, 1, [(10, 12, 'Josué Mbida', None), (18, 20, 'Joseph Ekani', None)]),
    ('Salon VVIP Bonabéri', '#714B67', 10, 23, 60, 1, [(15, 19, 'Grâce Nguene', None)]),
    ('Cabine SPA 1', '#0F6E56', 9, 21, 30, 1, [(11, 12, 'Nadège Owona', None), (15, 16.5, 'Sandrine Kemajou', None)]),
    ('Cabine SPA 2', '#0F6E56', 9, 21, 30, 1, [(10, 11, 'Pauline Etame', None)]),
    ('Fauteuil homme 1', '#185FA5', 9, 20, 30, 1, [(9, 9.5, 'Armel Tsala', None), (14, 14.5, 'Hugo Biyong', None)]),
    ('Fauteuil femme 1', '#185FA5', 9, 20, 30, 1, [(9.5, 11.5, 'Gisèle Kouam', None), (14, 15, 'Odile Ekwalla', None)]),
    ('Comptoir pressing', '#854F0B', 8, 19, 30, 2, []),
]


def libres(ouv, ferm, pas, capacite, creneaux):
    """« x/y créneaux libres » : un créneau du pas n'est pris que s'il est plein (autant de réservations que la
    capacité) ; entamé, il reste libre (écart n° 59) ; « créneau libre » au singulier."""
    step, h, n, total = pas / 60.0, float(ouv), 0, 0
    while h + step <= ferm + 1e-6:
        total += 1
        n += 1 if sum(1 for d, f, _, _ in creneaux if d < h + step and f > h) < capacite else 0
        h += step
    return '%d/%d %s' % (n, total, 'créneaux libres' if n > 1 else 'créneau libre')


assert [libres(*r[2:]).split()[0] for r in RESSOURCES] == ['9/14', '10/14', '9/13', '19/24', '22/24', '20/22', '16/22',
                                                            '22/22']


def ligne_planning(i, nom, couleur, ouv, ferm, pas, capacite, creneaux):
    span = float(ferm - ouv)
    reperes = ''.join('<i style="position:absolute;top:0;bottom:0;left:%.2f%%;border-left:1px dashed #E1DBD7"></i>'
                      % ((h - ouv) * 100 / span) for h in range(ouv + 2, ferm, 2))
    barres = ''.join('<span class="pl-b"%s style="left:%.2f%%;width:%.2f%%">%s</span>'
                     % (' id="%s"' % ident if ident else '', (d - ouv) * 100 / span, (f - d) * 100 / span, e(c))
                     for d, f, c, ident in creneaux)
    return ('<div class="pl-l" id="c6-pl%d"><span class="pl-n"><i style="background:%s"></i>%s</span>'
            '<div class="pl-p" style="background-image:none">%s%s</div><span class="pl-x">%s</span></div>'
            % (i, couleur, e(nom), reperes, barres, libres(ouv, ferm, pas, capacite, creneaux)))


ESPACES = vue_tdb('c6-espaces', (
    tdb_entete('Espaces & Prestations', 'Planning des créneaux · SPA, coiffure, pressing, espaces VIP / VVIP',
               'Nouvelle réservation')
    + libelles_larges(tdb_filtres([('Jour', ['‹', '17/10/2026', '›', "Aujourd'hui"], -1),
                                   ('Période stats', ["Aujourd'hui", 'Cette semaine', 'Ce mois'], 0),
                                   ('Famille', ['Toutes', 'Espace VIP / VVIP', 'SPA', 'Coiffure', 'Pressing', 'Autre'],
                                    0)]))
    + tdb_section('Activité de la période', [
        kpi('c6-e-ca', 'CA prestations réalisées', m(61800), compte(5, 'réalisée', 'réalisées'), 'violet'),
        kpi('c6-e-remp', 'Taux de remplissage', pct(20 * 100.0 / 109), '20 h réservées / 109 h ouvrées', 'bleu'),
        kpi('c6-e-ns', 'Non présentés', pct(0), compte(0, 'rendez-vous manqué', 'rendez-vous manqués'), 'rouge'),
        kpi('c6-e-pr', 'Retraits pressing en attente', '2', compte(6, 'réservation à venir', 'réservations à venir'),
            'ambre')])
    + '<div class="tdb-sect">Planning du 17/10/2026</div><div class="pl">%s</div>'
      % ''.join(ligne_planning(i, *r) for i, r in enumerate(RESSOURCES))))

# ------------------------------------------------- Direction — Activité par pôle --
# L'infobulle s'ouvre sous le « ? » de la carte RevPAR (coordonnées dans #c6-in-x), sur la carte elle-même, sans
# couvrir les cartes pickup et pace.
INFOBULLE = ('<div class="infobulle masque" id="c6-bulle" style="left:690px;top:424px;width:356px">Revenu par chambre disponible '
             "(RevPAR) : ce que rapporte chaque chambre disponible, vendue ou non — c'est l'indicateur qui combine prix "
             'et remplissage.</div>')
# Points fidélité émis du 01 au 14/10 (aite_loyalty installé : has_loyalty, dashboard.xml:107-111), ceux de
# t15_direction.POINTS : un point par tranche de 1 000 FCFA sur les nuitées, les prestations et ~600 000 FCFA de
# tickets de clients identifiés.
POINTS = CA_NUITEES // 1000 + PRESTATIONS // 1000 + 600
assert POINTS == 9895
# Évolution mensuelle (get_evolution, exec_dashboard.py:297-321), en millions de FCFA : trois séries par mois,
# barres groupées, légende en bas (exec_dashboard_view.js:239-270), axe kTick « 20 M » … « 0 » au pas de 2 M ;
# les valeurs de t15_direction.py (EVO) : hébergement nuit par nuit (octobre : les 412 nuitées du rythme du mois),
# ventes HT de t12_ventes.EVO_TOUT, prestations réalisées.
EVO_HEB = [14.2, 13.6, 16.9, 17.8, 16.4, PACE * ADR / 1e6]
EVO_POS = [x[1] / 1e6 for x in t12_ventes.EVO_TOUT]
EVO_PRE = [2.1, 2.0, 2.6, 2.8, 2.4, PRESTATIONS / 1e6]
assert t12_ventes.EVO_TOUT[-1][1] == CA and len(EVO_POS) == 6


def evolution_poles(identifiant):
    groupes = ''.join(
        '<div style="flex:1;position:relative"><div style="position:absolute;left:16%%;right:16%%;top:0;bottom:0;'
        'display:flex;align-items:flex-end;gap:3px">%s</div><span style="position:absolute;left:0;right:0;bottom:-24px;'
        'text-align:center;font-size:13px;color:var(--o-texte-3)">%s</span></div>'
        % (''.join('<i style="flex:1;display:block;height:%.1f%%;background:%s;border-radius:3px 3px 0 0"></i>'
                   % (v / 20.0 * 100, c) for v, c in zip(vals, ('#714B67', '#185FA5', '#0F6E56'))), e(lab))
        for vals, lab in zip(zip(EVO_HEB, EVO_POS, EVO_PRE), [mois_abrege(x, 2026) for x in range(5, 11)]))
    axe = ''.join('<span>%s</span>' % (('%d' % k + NBSP + 'M') if k else '0') for k in range(20, -1, -2))
    leg = ''.join('<span style="display:inline-flex;align-items:center;gap:6px;margin:0 9px"><i style="width:12px;'
                  'height:12px;background:%s;display:inline-block"></i>%s</span>' % (c, e(l))
                  for l, _, c in MIX)
    return ('<div class="g-carte" style="height:330px"><div class="g-titre">Évolution mensuelle — 6 mois</div>'
            '<div style="position:absolute;left:20px;right:20px;top:54px;bottom:76px;display:flex;gap:8px">'
            '<div style="display:flex;flex-direction:column;justify-content:space-between;font-size:11px;'
            'color:var(--o-texte-3);text-align:right;margin:-7px 0">%s</div>'
            '<div id="%s" style="flex:1;display:flex;border-left:1px solid #E5E2DD;border-bottom:1px solid #E5E2DD">%s'
            '</div></div><div style="position:absolute;left:20px;right:20px;bottom:14px;text-align:center;'
            'font-size:14px;color:var(--o-texte-2)">%s</div></div>' % (axe, identifiant, groupes, leg))


def mix_poles(identifiant):
    """« Mix du chiffre d'affaires par pôle » : l'anneau, sa légende à droite, puis la liste « montant · part »
    (mixLine, exec_dashboard_view.js:141-143)."""
    html = graphe_anneau(identifiant, "Mix du chiffre d'affaires par pôle", [(lib, v, c) for lib, v, c in MIX])
    liste = ''.join('<div style="display:flex;align-items:center;gap:10px;font-size:16px;padding:5px 0;'
                    'border-top:1px solid #EFEDEA"><i style="width:12px;height:12px;border-radius:50%%;background:%s;'
                    'display:inline-block"></i><span style="color:var(--o-texte-2)">%s</span><b style="margin-left:auto;'
                    'font-weight:600;color:var(--o-texte)">%s · %s</b></div>' % (c, e(lib), m(v), pct(v * 100.0 / TOTAL))
                    for lib, v, c in MIX)
    assert html.startswith('<div class="g-carte">') and html.endswith('</div>')
    return (html.replace('<div class="g-carte">', '<div class="g-carte" style="height:330px">', 1)
            .replace('<div class="g-anneau">', '<div class="g-anneau" style="margin-top:2px;gap:24px">')
            .replace('<svg id="%s" ' % identifiant, '<svg id="%s" style="width:150px;height:150px" ' % identifiant)
            [:-6] + '<div style="margin-top:8px">%s</div></div>' % liste)


EXEC = vue_tdb('c6-exec', '<div id="c6-in-x" style="position:relative">%s</div>' % (
    tdb_entete('Direction — Activité par pôle', 'Hébergement · Restauration & boutique · Prestations')
    + tdb_filtres([('Période', ['Ce mois', 'Ce trimestre', 'Cette année'], 0)])
    + '<div style="height:14px"></div><div class="tdb-grille c4">%s</div>' % ''.join([
        kpi('c6-x-tot', "Chiffre d'affaires total", m(TOTAL), 'Du 01/10/2026 au 14/10/2026', 'violet'),
        kpi('c6-x-heb', 'Hébergement', m(CA_NUITEES),
            'Nuitées HT, nuit par nuit · occupation %s · prix moyen %s / nuit' % (pct(OCC), m(ADR)), 'violet'),
        kpi('c6-x-pos', 'Restauration & boutique', m(CA),
            'HT · %s · panier %s' % (compte(TICKETS, 'ticket', 'tickets'), m(CA / TICKETS)), 'bleu'),
        kpi('c6-x-pre', 'Prestations', m(PRESTATIONS),
            compte(NB_PRESTATIONS, 'prestation réalisée', 'prestations réalisées'), 'teal')])
    + '<div class="tdb-sect">Hébergement — indicateurs de performance <span style="text-transform:none;'
      'letter-spacing:0;font-weight:500;color:var(--o-texte-3)">écarts vs même période N-1</span></div>'
    + contenir('<div class="tdb-grille c5">%s</div>' % ''.join([
        kpi('c6-x-occ', "Taux d'occupation", pct(OCC), compte(NUITEES, 'nuitée vendue', 'nuitées vendues'), None,
            (D_OCC, 'vs N-1'), aide=True),
        kpi('c6-x-adr', 'Prix moyen par nuit (ADR)', m(ADR), 'CA hébergement ÷ nuitées vendues', None,
            (D_ADR, 'vs N-1'), aide=True),
        kpi('c6-x-revpar', 'Revenu par chambre disponible (RevPAR)', m(REVPAR), 'par chambre disponible, vendue ou non',
            None, (D_REVPAR, 'vs N-1'), aide=True),
        kpi('c6-x-pick', 'Réservations récentes (pickup)', compte(PICKUP, 'nuitée', 'nuitées'),
            '%s ces 7 derniers jours pour les 30 prochains' % compte(PICKUP_RES, 'réservation prise',
                                                                     'réservations prises'), None, aide=True),
        kpi('c6-x-pace', 'Rythme du mois (pace)', compte(PACE, 'nuitée', 'nuitées'),
            'mois %s · N-1 à la même date : %s' % (mois_abrege(10, 2026), compte(PACE_N1, 'nuitée', 'nuitées')), None,
            (D_PACE, 'vs même date N-1'), aide=True)]), 5)
    + '<div style="height:14px"></div>'
    + contenir('<div class="tdb-grille c4">%s</div>'
               % kpi('c6-x-fid', 'Points fidélité émis', entier(POINTS, tdb=True), 'Tous services confondus'), 4)
    + '<div class="tdb-sect">Répartition &amp; évolution</div>'
    + graphes(mix_poles('c6-g-mix'), evolution_poles('c6-g-mois'))
    + '<div style="height:24px"></div>'
    + INFOBULLE))

# Défilements de l'activité par pôle : jusqu'aux graphiques (étape 6), puis retour aux indicateurs (étape 7).
DEFIL_X, DEFIL_X2 = -300, -150
DEFIL_V = -250            # l'analyse des ventes, jusqu'au module « Ventes & évolution »
ECRAN = fenetre('app-c6', 'Direction', MENUS_MUK['direction'], [COCKPIT, VENTES, ACHATS_VUE, ESPACES, EXEC],
                societe=demo.SOCIETE, initiale=NOM[0], avatar='#854F0B', calques=BARRES)


def changer_app(depuis, vers, vue_):
    """Le menu des applications : on quitte une application pour une autre."""
    gestes = [clic('#app-c6 .o-haut .grille', d=0.5)]
    if depuis:
        gestes.append(cacher('#%s' % depuis, d=0.15))
    gestes += [montrer('#%s' % vers, d=0.2, y=0, avec=True), vue(vue_)]
    return gestes


# La rangée Période, les pastilles des fournisseurs et la barre d'onglets du tableau de bord Achats
# (dashboard.xml:37-63, purchase_dashboard.scss:121-145), comme scenarios/t14_achats.py ; presentation.py réunit le
# CSS des chapitres.
CSS = '''
.c6-pt { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 8px; flex: none; }
.c6-date { height: 36px; padding: 0 12px; border: 1px solid var(--o-filet); border-radius: 8px; display: inline-flex;
  align-items: center; gap: 14px; font-size: 16px; color: var(--o-texte); }
.c6-esp { margin-left: auto; }
.c6-cal { width: 17px; height: 17px; color: #495057; }
.c6-fl { font-size: 18px; color: var(--o-texte-3); }
.c6-onglets { margin-top: 12px; background: #fff; border-radius: 12px; padding: 7px 10px; display: flex; gap: 6px; }
.c6-onglet { height: 40px; padding: 0 18px; border-radius: 8px; display: inline-flex; align-items: center; font-size: 17px;
  color: #5F5E5A; white-space: nowrap; }
.c6-onglet.actif { background: #714B67; color: #fff; }
'''

CHAPITRE = {
    'court': 'Direction',
    'poste': 'Direction',
    'titre': 'Le cockpit de la direction',
    'personne': (NOM, ROLE),
    'objectif': "Lire la santé de l'établissement d'un coup d'œil, puis descendre pôle par pôle : ventes, achats, "
                "espaces, hébergement.",
    'voix': "Sixième chapitre : la direction. Danielle ne saisit rien : elle lit les chiffres que le terrain vient "
            "de produire, avec les mêmes montants dans chaque tableau de bord.",
    'app': 'app-c6',
    'ecran': ECRAN,
    'css': CSS,
    'vues_initiales': {'odoo': 'c6-cockpit'},
    'etapes': [
        {'titre': 'Le cockpit Direction', 'texte': "Ce qui rentre, ce qu'on gagne, ce qui est à risque.",
         'voix': "Le cockpit Direction réunit les ventes, le crédit clients, le stock et les achats. En tête, la "
                 "santé de l'affaire : le chiffre encaissé hors taxes, la marge réalisée, et le cash à risque, ardoises en "
                 "retard et pertes de stock comprises.",
         'gestes': [compter('#c6-k-ca-v', 0, CA, d=1.1, apres=' FCFA'), anneau('#c6-k-marge', d=1.2),
                    anneau('#c6-k-risque', d=1.6), anneau('#c6-k-net', d=1.4)]},
        {'titre': "L'essentiel par pôle", 'texte': "Les mêmes chiffres qu'à la caisse, au magasin et à l'hôtel.",
         'voix': "Dessous, l'essentiel par pôle : on retrouve l'encours des ardoises vu à la caisse et la valeur du "
                 "stock vue au magasin. Et l'hébergement, comparé à l'an dernier : occupation, prix moyen, revpar.",
         'gestes': [defiler('#c6-in', -280, d=0.9), anneau('#c6-p-ard', d=1.2), anneau('#c6-p-stock', d=1.2),
                    anneau('#c6-h-occ', d=1.0), anneau('#c6-h-revpar', d=1.2)]},
        {'titre': 'Les ventes du bar et du restaurant', 'texte': "Chiffre d'affaires, marge, coût des marchandises.",
         'voix': "Dans le point de vente, l'analyse des ventes détaille le chiffre d'affaires, la marge et le coût "
                 "des marchandises, par article, par heure et par jour. Le ratio dit tout de suite si la marge est "
                 "maîtrisée.",
         'gestes': changer_app(None, 'c6-nav-pos', 'c6-ventes')
                   + [pause(0.4), anneau('#c6-v-ca', d=1.0), anneau('#c6-v-marge', d=1.0),
                      defiler('#c6-in-v', DEFIL_V, d=0.8), anneau('#c6-v-ratio', d=1.2), anneau('#c6-v-best', d=1.0),
                      anneau('#c6-g-top', d=1.0)]},
        {'titre': 'Les achats et les fournisseurs', 'texte': 'Ce qui est dû, ce qui tombe cette semaine, la ponctualité.',
         'voix': "Côté achats : la dette fournisseurs, ce qui est à payer dans les sept jours, le délai de "
                 "paiement, et la part des commandes livrées à temps et complètes.",
         'gestes': changer_app('c6-nav-pos', 'c6-nav-achats', 'c6-achats')
                   # Chaque anneau sur le mot qui le nomme : la dette, les sept jours, le délai, la part livrée.
                   + [anneau('#c6-a-dette', d=0.8), anneau('#c6-a-7j', d=1.2), anneau('#c6-a-dpo', d=0.9),
                      anneau('#c6-a-otif', d=1.4)]},
        {'titre': 'Les espaces et prestations', 'texte': 'Le remplissage du jour, et le planning de samedi, ressource par ressource.',
         'voix': "Les espaces et prestations montrent le remplissage du jour et le planning de chaque salon, cabine "
                 "ou fauteuil. Samedi, la réservation faite par Claire sur le site est déjà là, sur le salon Wouri.",
         'gestes': changer_app('c6-nav-achats', 'c6-nav-esp', 'c6-espaces')
                   + [pause(0.4), anneau('#c6-e-remp', d=1.0), anneau('#c6-bk-claire', d=1.8), anneau('#c6-pl0 .pl-x', d=0.9)]},
        {'titre': "L'activité par pôle", 'texte': 'Hébergement, restauration et prestations, consolidés.',
         'voix': "L'activité par pôle consolide les trois pôles : hébergement, restauration et boutique, "
                 "prestations. La restauration y affiche exactement le chiffre de l'analyse des ventes.",
         'gestes': [cacher('#c6-nav-esp', d=0.15), montrer('#c6-nav-exec', d=0.2, y=0, avec=True),
                    clic('#c6-nav-exec .menu:nth-child(3)', d=0.5), vue('c6-exec'), pause(0.4),
                    compter('#c6-x-tot-v', 0, TOTAL, d=1.1, apres=' FCFA'), anneau('#c6-x-pos', d=1.6),
                    defiler('#c6-in-x', DEFIL_X, d=0.9), anneau('#c6-g-mix', d=1.4)]},
        # Voix : « ritme » et « pikeup » sont écrits pour Kokoro (« rythme » est lu à l'anglaise), jamais à l'écran.
        {'titre': 'RevPAR, pickup et pace', 'texte': 'Chaque indicateur a sa phrase « ? » pour qui le découvre.',
         'voix': "Pour l'hôtel, le revpar combine prix et remplissage. Les réservations récentes, le pikeup, "
                 "mesurent la demande qui arrive cette semaine, et le ritme du mois compare les nuitées déjà "
                 "réservées à l'an dernier, à la même date. Chaque indicateur porte sa phrase d'explication.",
         # L'infobulle (title) n'apparaît qu'au survol du « ? » de la carte (dashboard.xml:5-11).
         'gestes': [defiler('#c6-in-x', DEFIL_X2, d=0.7), anneau('#c6-x-revpar', d=1.0),
                    curseur('#c6-x-revpar .kpi-aide', d=0.6), montrer('#c6-bulle', d=0.3, y=8), pause(2.2),
                    cacher('#c6-bulle', d=0.2), anneau('#c6-x-pick', d=1.4), anneau('#c6-x-pace', d=1.6)]},
    ],
}
