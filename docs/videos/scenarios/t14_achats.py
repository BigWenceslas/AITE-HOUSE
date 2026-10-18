# -*- coding: utf-8 -*-
"""Tutoriel 14 — Achats & Fournisseurs : ce que vous devez, ce qu'on vous doit.

La directrice (Danielle Eyenga, demo.POSTES['direction']) ouvre le tableau de
bord Achats & Fournisseurs d'aite_purchase_dashboard et le parcourt dans
l'ordre où elle s'en sert : la photo du mois, les dettes triées par urgence,
ce que les fournisseurs lui doivent (casiers consignés, avoirs), le registre
des consignes qu'elle met à jour après un retour de casiers, l'OTIF des
livraisons, la dépendance à un fournisseur et ses seuils, enfin la dérive des
prix d'achat.

Profil rejoué : celui du compte demo.direction (Responsable Achats + droit
Facturation : addons/aite_demo_data/models/demo_generator.py:74-83), le seul
compte de démonstration qui ouvre ce tableau de bord et voit le bouton
« ⚙ Configurer les alertes » (réservé à purchase.group_purchase_manager :
static/src/xml/dashboard.xml:168-170, models/purchase_dashboard.py:206-208).
Applications de la barre : ecrans.APPS_PROFIL['direction'] ; menus de
l'application Achats relevés sur ../aite-videos/ref_muk/014-achats-tableau-
de-bord-aite.png (« Commandes », « Tableau de bord AITE », « Produits »,
« Analyse », « Configuration » : odoo18/addons/purchase/views/
purchase_views.xml:5-19 et :54, report/purchase_report_views.xml:103,
i18n/fr.po « Purchase » → Achats, « Orders » → Commandes, « Products » →
Produits, « Reporting » → Analyse ; menu AITE : addons/
aite_purchase_dashboard/views/purchase_dashboard_menus.xml:8-13).

Sources des libellés (tous relevés mot pour mot dans addons/
aite_purchase_dashboard, sauf mention) :

- titre et sous-titre : static/src/xml/dashboard.xml:29-30 ; filtres
  « Période », « Appliquer », « Fournisseur », « Tous », « → » :35-66 ;
  pastilles de période : static/src/js/services/utils.js:69-74 ; onglets :
  static/src/js/views/purchase_dashboard_view.js:154-163 ;
- onglet Tableau de bord : dashboard.xml:85-142 (« Vue d'ensemble »,
  « Indicateurs », « Répartition & flux », cartes et sous-titres, titres des
  graphiques, phrase « Un glissement vers +30/+60 j annonce une tension de
  trésorerie. » :136) ; séries « Factures fournisseurs » / « Paiements » :
  purchase_dashboard_view.js:380-386 ; mois « Mai … Oct » :
  models/purchase_dashboard.py:427-428 ; tranches « Non échu », « 1–30 j »,
  « 31–60 j », « 61–90 j », « +90 j » : purchase_dashboard_view.js:411 ;
- onglet Dettes & échéancier : dashboard.xml:217-288 ; « Échu / S0 », « S1 »
  … « S5+ » : purchase_dashboard_view.js:459 ; « dans N j », « auj. », « N j » :
  :240-248 ; tri par urgence : purchase_dashboard.py:262-267 ;
- onglet Avoirs & consignes : dashboard.xml:291-389 (« Gérer les consignes »
  :315-316, phrase du 4096 :350, « Réflexe : … » :384-388) ;
- onglet Commandes & réceptions : dashboard.xml:392-454 ; ✓ / ✗ / — :
  purchase_dashboard_view.js:250-255 ;
- onglet Fournisseurs : dashboard.xml:146-214 ; « … des achats · seuil de
  dépendance dépassé » : purchase_dashboard_view.js:284-289 ; fenêtre
  « ⚙ Alertes achats & fournisseurs » : dashboard.xml:525-566 (le glyphe ⚙,
  absent de la police Inter, est redessiné en SVG) ;
- onglet Prix & variations : dashboard.xml:457-520 ; « Δ » positif en rouge,
  négatif en vert :501-502 ; impact « −… » / « +… » / « — » :
  purchase_dashboard_view.js:265-278 ;
- statuts et badges : purchase_dashboard.py:63-135 (« En retard », « À payer
  bientôt », « À échoir », « En attente », « Reçue en retard », « Reçue
  incomplète », « Reçue conforme », « Hausse forte », « Hausse », « Baisse »,
  « Stable », « Dépendance », « Retards », « OK ») ; couleurs : utils.js:9-30
  (palette des graphiques, AGING_COLORS, BADGE_CLS) et purchase_dashboard.py:
  40-44 (une couleur par fournisseur, dans l'ordre alphabétique de
  _supplier_universe :177-194 — en Python, « É » se range après « Z ») ;
  badges foncés pour le contraste, comme scenarios/t13_stock.py ;
- registre « Consignes fournisseurs » : views/purchase_dashboard_actions.xml:
  9-11 (titre), views/purchase_deposit_views.xml:4-17 (liste éditable en bas,
  colonnes, somme de la valeur), models/purchase_deposit.py:20-57 (libellés
  « Fournisseur », « Casiers consignés », « Consigne / casier », « Valeur
  immobilisée », « Dernière déconsignation », « Note » ; valeur = casiers ×
  consigne ; tri « value desc ») ; boutons natifs d'une liste éditable :
  odoo18/addons/web/static/src/views/list/list_controller.xml:7-11 et
  :106-114 (« New » → Nouveau, « Save » → Enregistrer, « Discard » → Ignorer,
  web/i18n/fr.po) ; fil d'Ariane : le nom de l'action cliente
  « Achats & Fournisseurs — Tableau de bord » (purchase_dashboard_actions.xml:
  5) puis « Consignes fournisseurs ».

Les chiffres de l'écran sont calculés : statuts, tranches, urgences, OTIF,
variations de prix, impacts et badges sortent du VRAI code des six fonctions
pures de models/purchase_dashboard.py (_bucket, _invoice_metrics,
_order_metrics, _price_metrics, _supplier_badge, _dpo), extrait à l'import
comme le font tests/socle/test_purchase_logic.py:21-42 ; les agrégats
reprennent _open_bill_rows / get_open_invoices :225-267, _order_rows
:273-331, get_claims :343-410, get_price_moves :472-514, get_supplier_rows
:562-608 et get_kpis :610-721 ; les formats, ceux de utils.js:32-67 (montant
arrondi au franc, « 62,5 % », « 18,7 j ») et de purchase_dashboard_view.js:
203-289. Réglages par défaut : 7 j, 2 j, 40 %, 5 % (models/
res_config_settings.py:20-38). Le jeu est fictif : un bar-hôtel de Douala
et ses cinq fournisseurs (Boissons du Wouri SARL, Dépôt Akwa Distribution,
Épicerie Fine Bonapriso, Hygiène Pro Littoral — repris de scenarios/
c6_direction.py — et Primeurs de Deïdo), dix commandes du mois, huit factures
ouvertes, trois avoirs, trois lignes de consignes ; articles et coûts repris
de scenarios/t13_stock.py. Aujourd'hui : vendredi 16/10/2026, période « Ce
mois ». Références : commandes « P00151 », factures « BILL/2026/10/0001 »,
avoirs « RBILL/2026/10/0001 », au format relevé sur la base de démonstration
MuK (séquences d'odoo18/addons/account/models/account_move.py:3795-3798) ;
le motif d'un avoir est sa référence saisie (mv.ref, purchase_dashboard.py:
381) ; devise XAF, symbole « FCFA », sans décimale
(odoo18/odoo/addons/base/data/res_currency_data.xml:476-483).

Sources des affirmations : douleurs — models/purchase_deposit.py:7-14
(« Odoo ne suit pas nativement les casiers/bouteilles consignés », « le 4096
ne se solde jamais sans suivi à l'unité ») et dashboard.xml:350 ; « Un avoir
oublié est une perte sèche » :384-388 ; « les dérives passent par petites
touches » :516-519 ; « Un glissement vers +30/+60 j » :136 ; « ponctuel mais
livrer incomplet » :450-453 ; « Risque de concentration » :209-213 ;
« l'argent qui dort chez vos fournisseurs » :292. Promesse : le manifeste,
« piloter la relation fournisseurs dans les deux sens — ce que vous devez
(401) et ce qu'on vous doit (409) » (__manifest__.py:13-16). Résultats :
échéancier sur 6 semaines (purchase_dashboard_view.js:179-188, :459), balance
âgée en 5 tranches (purchase_dashboard.py:50-61), 4 seuils réglables
(res_config_settings.py:20-38, dashboard.xml:536-555). Fenêtres de prix
(45 jours contre 120 à 210 jours) : purchase_dashboard.py:476-479 ; impact
annuel = Δ prix × volume mensuel × 12 :114 et :502.

Captures de référence (modèle visuel, jamais incrustées) :
../aite-videos/ref_muk/014-achats-tableau-de-bord-aite.png, -pleine.png et
013-achats-configuration-consignes-fournisseurs.png ; docs/captures_uat/
r4-direction-04-ouvrir-achats-fournisseurs.png. Chapitre déjà rejoué dans
la présentation : scenarios/c6_direction.py (vue « Achats »).

Écarts rejoués tels quels (voir le rapport) :
1. « Créances fournisseurs (409) » et « Acomptes / soldes débiteurs (4091) »
   additionnent les factures ouvertes : le domaine de get_claims retient
   amount_residual < 0, c'est-à-dire les soldes CRÉDITEURS (purchase_
   dashboard.py:388-399). Rejoué : acomptes = dette 401 − avoirs, d'où une
   créance totale plus grosse que la dette. La voix et les bulles ne citent
   jamais ces deux chiffres ; si le code est corrigé, refaire CREANCES.
2. Dates ISO dans toutes les colonnes de date du tableau de bord
   (purchase_dashboard.py:251, 321-324, 356-357, 379-380), alors que le
   registre natif affiche 08/10/2026.
3. « Ce mois » démarre le 30/09/2026 à Douala : periodRange passe par
   toISOString, en UTC (utils.js:78, :94).
4. Sigles anglais « DPO » et « OTIF » dans les titres de cartes
   (dashboard.xml:100, :113).
"""

import math
import os
import re
import textwrap
from datetime import date, timedelta

import demo
from ecrans import APPS_PROFIL, ICONES, e, fenetre_muk, navigateur, recherche, tdb_entete, vue_libre, vue_tdb
from marketing import bulle, dezoom, reaction, zoom
from moteur import anneau, animer, cacher, clic, classe, compter, curseur, defiler, fermer, montrer, ouvrir, pause, saisir, texte, vue

NOM, ROLE = demo.POSTES['direction']
ICI = os.path.dirname(os.path.abspath(__file__))
MODULE = os.path.join(ICI, '..', '..', '..', 'addons', 'aite_purchase_dashboard', 'models', 'purchase_dashboard.py')


# ------------------------------------------------------ le vrai calcul --

def _fonctions_du_module(noms):
    """Le code réel des fonctions pures, extrait du module (même motif que
    tests/socle/test_purchase_logic.py:21-31)."""
    with open(MODULE, encoding='utf-8') as f:
        src = f.read()
    ns = {}
    for nom in noms:
        m = re.search(r'^    def %s\(.*?(?=^    @staticmethod|^    # -{10,}|^    def )' % nom, src, re.S | re.M)
        exec(compile(textwrap.dedent(m.group(0)), MODULE, 'exec'), ns)
    return ns


_F = _fonctions_du_module(['_bucket', '_invoice_metrics', '_order_metrics', '_price_metrics', '_supplier_badge', '_dpo'])
# Réglages par défaut de la société (res_config_settings.py:20-38).
CFG = {'soon': 7, 'late': 2, 'dep': 40.0, 'price': 5.0}
AUJ = date(2026, 10, 16)
# « Ce mois » vu d'un poste à Douala : le 1er octobre à minuit local, passé en
# UTC par toISOString, devient le 30 septembre (utils.js:78, :94 — écart 3).
DU = date(2026, 9, 30)
JOURS = (AUJ - DU).days + 1

# Les fournisseurs, rangés comme _supplier_universe (nom en minuscules) ; la
# palette suit cet ordre (purchase_dashboard.py:40-44, :211-219).
PALETTE = ['#714B67', '#185FA5', '#3B6D11', '#0F6E56', '#854F0B', '#A32D2D', '#5B4B8A', '#B0655A']
WOURI, AKWA, BONA = 'Boissons du Wouri SARL', 'Dépôt Akwa Distribution', 'Épicerie Fine Bonapriso'
HYG, DEIDO = 'Hygiène Pro Littoral', 'Primeurs de Deïdo'
FOURNISSEURS = sorted([WOURI, AKWA, BONA, HYG, DEIDO], key=lambda n: n.lower())
COULEUR = {n: PALETTE[i] for i, n in enumerate(FOURNISSEURS)}


def j(jour, mois, an=2026):
    return date(an, mois, jour)


# Les commandes du mois, avec leurs lignes (article, quantité, prix) :
# (date, fournisseur, référence, prévue, reçue, receipt_status, lignes)
COMMANDES = [
    (j(1, 10), WOURI, 'P00151', j(2, 10), j(2, 10), 'full',
     [('Bière blonde 65 cl', 360, 650), ('Bière brune 65 cl', 240, 700), ('Bière sans alcool 33 cl', 72, 450)]),
    (j(2, 10), AKWA, 'P00152', j(3, 10), j(4, 10), 'full',
     [('Eau minérale 1,5 L', 240, 300), ('Cola 33 cl', 240, 300), ("Jus d'ananas 1 L", 60, 900)]),
    (j(5, 10), HYG, 'P00153', j(7, 10), j(11, 10), 'full',
     [('Détergent sol 5 L', 30, 2750), ('Eau de Javel 5 L', 42, 1500)]),
    (j(6, 10), AKWA, 'P00154', j(7, 10), j(7, 10), 'full',
     [('Eau minérale 50 cl', 288, 150), ('Cola 33 cl', 216, 300), ('Eau minérale 1,5 L', 240, 300)]),
    (j(7, 10), WOURI, 'P00155', j(8, 10), j(8, 10), 'full',
     [('Bière blonde 65 cl', 480, 650), ('Bière brune 65 cl', 240, 700), ('Bière sans alcool 33 cl', 96, 450)]),
    (j(9, 10), BONA, 'P00156', j(12, 10), j(12, 10), 'partial',
     [('Whisky 12 ans 70 cl', 12, 18000), ('Vin rouge 75 cl', 24, 4500)]),
    (j(10, 10), DEIDO, 'P00157', j(11, 10), j(11, 10), 'full',
     [('Plantain (régime)', 16, 2500), ('Oignons (sac 25 kg)', 3, 14000)]),
    (j(12, 10), WOURI, 'P00158', j(13, 10), None, 'pending',
     [('Bière blonde 65 cl', 360, 650), ('Bière brune 65 cl', 240, 700), ('Bière sans alcool 33 cl', 120, 450)]),
    (j(14, 10), DEIDO, 'P00159', j(15, 10), j(15, 10), 'full',
     [('Plantain (régime)', 20, 2500), ('Tomates (cagette)', 6, 7500)]),
    (j(15, 10), AKWA, 'P00160', j(17, 10), None, 'pending',
     [('Eau minérale 1,5 L', 216, 300), ('Cola 33 cl', 216, 300), ("Jus d'ananas 1 L", 96, 900)]),
]


def _commandes():
    """_order_rows : une ligne par commande confirmée, les plus récentes d'abord."""
    rows = []
    for d_cmd, four, ref, prevue, recue, statut, lignes in COMMANDES:
        pending = statut == 'pending'
        is_full = (statut == 'full') if not pending else None
        days_late = max(0, (AUJ - prevue).days) if pending else max(0, (recue - prevue).days)
        delai = (recue - d_cmd).days if recue else None
        m = _F['_order_metrics'](pending, days_late, is_full, CFG['late'])
        rows.append(dict(date=d_cmd, four=four, ref=ref, prevue=prevue, recue=recue, pending=pending, is_full=is_full,
                         days_late=days_late, delai=delai, montant=sum(q * p for _, q, p in lignes), lignes=lignes, **m))
    rows.sort(key=lambda r: r['date'], reverse=True)
    return rows


CMD = _commandes()

# Les factures fournisseurs comptabilisées non soldées :
# (fournisseur, référence, date de facture, échéance, total, déjà payé)
FACTURES = [
    (BONA, 'BILL/2026/08/0014', j(9, 8), j(8, 9), 135000, 0),
    (HYG, 'BILL/2026/09/0003', j(7, 9), j(7, 10), 92000, 46000),
    (AKWA, 'BILL/2026/09/0011', j(16, 9), j(16, 10), 164000, 0),
    (WOURI, 'BILL/2026/10/0001', j(2, 10), j(17, 10), 434400, 0),
    (AKWA, 'BILL/2026/10/0002', j(4, 10), j(3, 11), 198000, 0),
    (AKWA, 'BILL/2026/10/0003', j(7, 10), j(6, 11), 180000, 0),
    (WOURI, 'BILL/2026/10/0004', j(8, 10), j(23, 10), 523200, 0),
    (HYG, 'BILL/2026/10/0006', j(11, 10), j(10, 11), 145500, 0),
]
# Les factures de la période déjà soldées (Primeurs de Deïdo, payées comptant).
FACTURES_PAYEES = [(DEIDO, 'BILL/2026/10/0005', j(11, 10), 82000), (DEIDO, 'BILL/2026/10/0007', j(15, 10), 95000)]


def _factures():
    """_open_bill_rows, triées comme get_open_invoices (urgence, échéance, retard)."""
    rows = []
    for four, ref, d_fac, due, total, paye in FACTURES:
        residual = total - paye
        days_late = max(0, (AUJ - due).days)
        days_to_due = max(0, (due - AUJ).days)
        m = _F['_invoice_metrics'](residual, days_late, days_to_due, CFG['soon'])
        rows.append(dict(four=four, ref=ref, date=d_fac, due=due, total=total, paid=total - residual,
                         residual=residual, days_late=days_late, days_to_due=days_to_due,
                         bucket=_F['_bucket'](days_late), **m))
    rows.sort(key=lambda r: (r['urgency'], r['days_to_due'], -r['days_late']))
    return rows


FAC = _factures()

# Le registre des consignes (purchase_deposit.py) : (fournisseur, casiers, consigne, dernière déconsignation, note)
CONSIGNES = [(WOURI, 48, 3600, j(8, 10), 'Casiers 65 cl'), (AKWA, 30, 2500, j(25, 9), 'Casiers eau et sodas'),
             (HYG, 12, 1500, None, 'Bidons 20 L')]
RENDUS = 20                       # casiers rendus au fournisseur de bières ce jour-là
# Les avoirs fournisseurs ouverts : (date, fournisseur, référence, motif, montant), du plus récent au plus ancien.
AVOIRS = [
    (j(13, 10), BONA, 'RBILL/2026/10/0003', 'Écart de prix whisky', 27000),
    (j(10, 10), AKWA, 'RBILL/2026/10/0002', 'Jus périmés', 10800),
    (j(3, 10), WOURI, 'RBILL/2026/10/0001', 'Casse à la livraison', 15600),
]

# Les prix d'achat (get_price_moves) : (article, fournisseur, prix d'il y a 4 à 7 mois, prix des 45 derniers
# jours, quantité achetée sur 45 jours) ; et les prix mensuels de mai à octobre (indice base 100).
PRIX = [
    ('Bière blonde 65 cl', WOURI, 600, 650, 1800, [600, 600, 615, 615, 640, 650]),
    ('Bière brune 65 cl', WOURI, 680, 700, 1080, [680, 680, 680, 690, 700, 700]),
    ('Eau minérale 1,5 L', AKWA, 300, 300, 1200, [300] * 6),
    ('Cola 33 cl', AKWA, 320, 300, 1104, [320, 320, 310, 310, 300, 300]),
    ('Whisky 12 ans 70 cl', BONA, 18000, 18000, 18, [18000] * 6),
    ("Jus d'ananas 1 L", AKWA, 850, 900, 228, [850, 850, 850, 900, 900, 900]),
    ('Vin rouge 75 cl', BONA, 4200, 4500, 42, [4200, 4200, 4350, 4350, 4500, 4500]),
    ('Bière sans alcool 33 cl', WOURI, 450, 450, 408, [450] * 6),
]
MOIS = ['Mai', 'Juin', 'Juil', 'Août', 'Sep', 'Oct']


def _prix():
    rows = []
    for nom, four, p0, p1, q45, mensuel in PRIX:
        vol = q45 / 45.0 * 30.0
        rows.append(dict(nom=nom, four=four, p0=p0, p1=p1, vol=vol, spend=p1 * q45, mensuel=mensuel,
                         **_F['_price_metrics'](p0, p1, vol, CFG['price'])))
    rows.sort(key=lambda r: -r['spend'])
    return rows[:8]


PX = _prix()


# --------------------------------------------- les formats de utils.js --

def _milliers(n):
    return ('-' if n < 0 else '') + '{:,}'.format(abs(n)).replace(',', ' ')


def _arrondi(v):
    return int(math.floor(v + 0.5)) if v >= 0 else -int(math.floor(-v + 0.5))


def money(v):
    return _milliers(_arrondi(v)) + ' FCFA'


def neg_money(v):
    return '−' + money(v)


def money_or_dash(v):
    return money(v) if v else '—'


def _dixieme(v):
    r = int(v * 10 + (0.5 if v >= 0 else -0.5)) / 10.0
    return ('%.1f' % r).rstrip('0').rstrip('.')


def pct(v):
    return _dixieme(v).replace('.', ',') + ' %'


def signed_pct(v):
    return ('+' if v > 0 else '') + pct(v)


def days(v):
    return _dixieme(v).replace('.', ',') + ' j'


def iso(d):
    return d.strftime('%Y-%m-%d') if d else '—'


def fr(d):
    return d.strftime('%d/%m/%Y') if d else ''


def late_text(f):
    if f['days_late'] > 0:
        return '%d j' % f['days_late']
    if f['days_to_due'] > 0:
        return 'dans %d j' % f['days_to_due']
    return 'auj.'


def impact_text(p):
    n = p['impact']
    return '−' + money(n) if n > 0 else ('+' + money(-n) if n < 0 else '—')


# ------------------------------------------------------- les agrégats --

ACHATS = sum(c['montant'] for c in CMD)
RECUS = [c for c in CMD if not c['pending']]
EN_COURS = [c for c in CMD if c['pending']]
OTIF = 100.0 * len([c for c in RECUS if c['otif']]) / len(RECUS)
DELAI = sum(c['delai'] for c in RECUS) / float(len(RECUS))
PENDING_LATE = len([c for c in EN_COURS if c['days_late'] > CFG['late']])
RECV_LATE = len([c for c in RECUS if c['days_late'] > CFG['late']])

ENCOURS = sum(f['residual'] for f in FAC)
RETARD = [f for f in FAC if f['days_late'] > 0]
SOON = [f for f in FAC if f['days_late'] == 0 and f['days_to_due'] <= CFG['soon']]
MONTH = sum(f['residual'] for f in FAC if f['days_late'] == 0 and CFG['soon'] < f['days_to_due'] <= 30)
FAC_PERIODE = sum(t for _, _, d, _, t, _ in FACTURES if DU <= d <= AUJ) + sum(t for _, _, d, t in FACTURES_PAYEES)
DPO = _F['_dpo'](ENCOURS, FAC_PERIODE or ACHATS, JOURS)
AGING = [sum(f['residual'] for f in FAC if f['bucket'] == b) for b in range(5)]
SEMAINES = [0] * 6
for _f in FAC:
    SEMAINES[0 if _f['days_late'] > 0 else min(5, _f['days_to_due'] // 7)] += _f['residual']


def _creances(consignes):
    """get_claims : consignes + avoirs + « acomptes ». Rejoué tel que le code
    le calcule (écart 1) : le domaine amount_residual < 0 prend les lignes
    CRÉDITRICES du compte fournisseurs, soit le reste dû des factures ouvertes."""
    depots = sum(q * u for _, q, u, _, _ in consignes)
    avoirs = sum(a[4] for a in AVOIRS)
    soldes = sum(f['residual'] for f in FAC)          # lignes créditrices (écart 1)
    acomptes = max(0.0, soldes - avoirs)
    return dict(depots=depots, qty=sum(q for _, q, _, _, _ in consignes), avoirs=avoirs, acomptes=acomptes,
                total=depots + avoirs + acomptes)


CREANCES = _creances(CONSIGNES)
APRES = [(f, q - RENDUS if f == WOURI else q, u, AUJ if f == WOURI else d, n) for f, q, u, d, n in CONSIGNES]
CREANCES_APRES = _creances(APRES)


def _fournisseurs():
    """get_supplier_rows : achats de la période, part, encours, retards, délai, OTIF, badge."""
    rows = []
    for four in FOURNISSEURS:
        po = [c for c in CMD if c['four'] == four]
        bi = [f for f in FAC if f['four'] == four]
        achats = sum(c['montant'] for c in po)
        part = achats / ACHATS * 100.0
        retard = sum(f['residual'] for f in bi if f['days_late'] > 0)
        recus = [c for c in po if not c['pending']]
        delai = sum(c['delai'] for c in recus) / float(len(recus)) if recus else 0.0
        otif = 100.0 * len([c for c in recus if c['otif']]) / len(recus) if recus else 0.0
        rows.append(dict(nom=four, achats=achats, part=part, du=sum(f['residual'] for f in bi), retard=retard,
                         delai=delai, otif=otif, **_F['_supplier_badge'](part, retard, achats, CFG['dep'])))
    rows.sort(key=lambda r: -r['achats'])
    return rows


FOUR = _fournisseurs()
TOP = FOUR[0]

W = sum(p['p1'] * p['vol'] for p in PX)
VAR_MOY = sum(p['delta'] * p['p1'] * p['vol'] for p in PX) / W
TOP_HAUSSE = max(PX, key=lambda p: p['delta'])
NB_HAUSSES = len([p for p in PX if p['delta'] >= CFG['price']])
IMPACT = sum(p['impact'] for p in PX if p['impact'] > 0)

# Les achats de la période par article (Top produits achetés, 8 au plus).
_PAR_ARTICLE = {}
for _c in CMD:
    for _a, _q, _p in _c['lignes']:
        _PAR_ARTICLE[_a] = _PAR_ARTICLE.get(_a, 0) + _q * _p
TOP_ARTICLES = sorted(_PAR_ARTICLE.items(), key=lambda kv: -kv[1])[:8]

# Les flux des six derniers mois (factures fournisseurs / paiements) ; octobre
# reprend les factures de la période.
FLUX = [('Mai', 3980000, 3760000), ('Juin', 3620000, 3900000), ('Juil', 4310000, 4050000),
        ('Août', 3870000, 3640000), ('Sep', 4420000, 4180000), ('Oct', FAC_PERIODE, 1214000)]

assert (len(CMD), len(RECUS), len(FAC)) == (10, 8, 8)
assert [f['status'] for f in FAC] == ['En retard'] * 2 + ['À payer bientôt'] * 3 + ['À échoir'] * 3
assert TOP['nom'] == WOURI and TOP['badge'] == 'Dépendance' and 50 < TOP['part'] < 60
assert PX[0]['nom'] == 'Bière blonde 65 cl' and PX[0]['badge'] == 'Hausse forte' and NB_HAUSSES == 3
assert [c['status'] for c in CMD if c['ref'] == 'P00156'] == ['Reçue incomplète']


# ----------------------------------------------- les écrans rejoués --

CAL = ('<svg class="t14-cal" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">'
       '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/></svg>')
ENGRENAGE = ('<svg class="t14-gear" viewBox="0 0 24 24" fill="currentColor"><path d="M19.4 13a7.5 7.5 0 000-2l2.1-1.6-2-3.5'
             '-2.5 1a7.6 7.6 0 00-1.7-1L15 3.3h-4l-.4 2.6a7.6 7.6 0 00-1.7 1l-2.5-1-2 3.5L6.5 11a7.5 7.5 0 000 2l-2.1 1.6 '
             '2 3.5 2.5-1a7.6 7.6 0 001.7 1l.4 2.6h4l.4-2.6a7.6 7.6 0 001.7-1l2.5 1 2-3.5zM12 15.5a3.5 3.5 0 110-7 3.5 '
             '3.5 0 010 7z"/></svg>')
ONGLETS = ['Tableau de bord', 'Fournisseurs', 'Dettes & échéancier', 'Avoirs & consignes', 'Commandes & réceptions',
           'Prix & variations']
BADGE = {'red': 'rouge', 'amber': 'ambre', 'teal': 'vert', 'blue': 'bleu', 'gray': 'gris'}


def _point(four):
    return '<i class="t14-pt" style="background:%s"></i>' % COULEUR[four]


def _tete(v, actif):
    """Titre, filtres et onglets : la tête commune à chaque onglet."""
    periode = ''.join('<span class="chip%s">%s</span>' % (' actif' if p == 'Ce mois' else '', e(p))
                      for p in ["Aujourd'hui", 'Cette semaine', 'Ce mois', '3 mois'])
    dates = ('<span class="t14-date t14-esp">%s%s</span><span class="t14-fl">→</span><span class="t14-date">%s%s</span>'
             '<span class="chip">Appliquer</span>' % (e(fr(DU)), CAL, e(fr(AUJ)), CAL))
    fours = ''.join('<span class="chip">%s%s</span>' % (_point(f), e(f)) for f in FOURNISSEURS)
    filtres = ('<div class="tdb-filtres"><div class="tdb-rang"><span class="tdb-lib">Période</span>%s%s</div>'
               '<div class="tdb-rang"><span class="tdb-lib">Fournisseur</span><span class="chip actif">Tous</span>%s</div>'
               '</div>' % (periode, dates, fours))
    onglets = ''.join('<span class="t14-onglet%s" id="t14-tab-%s-%d">%s</span>' % (' actif' if i == actif else '', v, i, e(o))
                      for i, o in enumerate(ONGLETS))
    return (tdb_entete('Achats & Fournisseurs — Tableau de bord', 'Dettes (401) & créances fournisseurs (409) · '
                       'échéancier · OTIF · prix') + filtres + '<div class="t14-onglets">%s</div>' % onglets)


def _kpi(ident, lib, val, sous, accent=None):
    """Une carte KpiCard : seules les cartes « mega » portent un liseré coloré."""
    return ('<div class="kpi%s" id="%s"><div class="kpi-l">%s</div><div class="kpi-v" id="%s-v">%s</div>'
            '<div class="kpi-s" id="%s-s">%s</div></div>'
            % (' acc-' + accent if accent else '', ident, e(lib), ident, e(val), ident, e(sous)))


def _section(titre, cartes):
    return '<div class="tdb-sect">%s</div><div class="tdb-grille c4">%s</div>' % (e(titre), ''.join(cartes))


def _table(ident, colonnes, lignes, classe_=''):
    """Une table du tableau de bord : ``colonnes`` (libellé, largeur, 'd' ou 'c'),
    ``lignes`` (identifiant, [cellules HTML]) ; ``classe_`` : une table resserrée."""
    gab = ' '.join(c[1] for c in colonnes)
    tete = '<div class="t14-th" style="grid-template-columns:%s">%s</div>' % (
        gab, ''.join('<span%s>%s</span>' % (' class="t14-%s"' % c[2] if len(c) > 2 else '', e(c[0])) for c in colonnes))
    rangs = ''.join('<div class="t14-tr" id="%s" style="grid-template-columns:%s">%s</div>' % (i, gab, ''.join(cs))
                    for i, cs in lignes)
    return '<div class="t14-tab%s" id="%s">%s%s</div>' % (' ' + classe_ if classe_ else '', ident, tete, rangs)


def _c(txt, al='', cls='', ident=None):
    classes = ' '.join(x for x in ('t14-' + al if al else '', cls) if x)
    return '<span%s%s>%s</span>' % (' class="%s"' % classes if classes else '', ' id="%s"' % ident if ident else '',
                                    e(txt))


def _four(four, gras=False, wrap=False):
    return '<span class="t14-nom%s%s">%s<span>%s</span></span>' % (' t14-b' if gras else '', ' t14-wrap' if wrap else '',
                                                                 _point(four), e(four))


def _badge(txt, cls, ident=None):
    return '<span><span class="t14-badge %s"%s>%s</span></span>' % (BADGE[cls], ' id="%s"' % ident if ident else '', e(txt))


def _note(ident, html):
    return '<div class="t14-note" id="%s">%s</div>' % (ident, html)


def _carte(titre, corps, ident=None, droite='', pied=''):
    return ('<div class="t14-carte"%s><div class="t14-ct"><h3>%s</h3>%s</div>%s%s</div>'
            % (' id="%s"' % ident if ident else '', e(titre), droite, corps, pied))


def _bt_contour(ident, libelle, svg=''):
    return '<span class="t14-btc" id="%s">%s%s</span>' % (ident, svg, e(libelle))


# -- graphiques (Chart.js rejoué : anneau, barres, courbes)

def _g(ident, titre, corps, pied=''):
    return '<div class="t14-g" id="%s"><h3>%s</h3>%s%s</div>' % (ident, e(titre), corps, pied)


def _compact(v):
    """fmtCompact (utils.js:38-49), pour les graduations des axes."""
    if v >= 1e6:
        return ('%.1f' % (v / 1e6)).replace('.', ',') + ' M'
    if v >= 1e3:
        return '%d k' % _arrondi(v / 1e3)
    return '%d' % v


def _anneau(parts):
    """Le doughnut « Achats par fournisseur » : découpe à 56 %, légende à droite."""
    total = float(sum(v for _, v, _ in parts))
    ext = 106.0
    ep = ext * (1 - 0.56)
    r = ext - ep / 2
    tour = 2 * math.pi * r
    debut, arcs = 0.0, []
    for _, v, coul in parts:
        long_ = tour * v / total
        arcs.append('<circle r="%.1f" cx="110" cy="110" fill="none" stroke="%s" stroke-width="%.1f" '
                    'stroke-dasharray="%.2f %.2f" stroke-dashoffset="%.2f"/>' % (r, coul, ep, max(0.1, long_ - 2.2),
                                                                             tour - long_ + 2.2, -debut))
        debut += long_
    leg = ''.join('<div><i style="background:%s"></i>%s</div>' % (c, e(n)) for n, _, c in parts)
    return ('<div class="t14-an"><svg viewBox="0 0 220 220"><g transform="rotate(-90 110 110)">%s</g></svg>'
            '<div class="t14-an-leg">%s</div></div>' % (''.join(arcs), leg))


def _barres_v(groupes, vmax, ticks, couleurs, legende=(), hauteur=190, par_barre=None):
    """Barres verticales (groupées si plusieurs séries) : ``groupes`` (libellé, [valeurs]) ;
    ``par_barre`` : une couleur par groupe, pour une série unique (balance âgée)."""
    h = float(hauteur)
    cols = ''.join('<div class="t14-vg">%s</div>' % ''.join(
        '<i style="height:%.1fpx;background:%s"></i>' % (h * v / vmax, par_barre[g] if par_barre else couleurs[k])
        for k, v in enumerate(vals)) for g, (_, vals) in enumerate(groupes))
    grad = ''.join('<span style="top:%.1fpx">%s</span>' % (h - h * v / vmax, e(t)) for v, t in ticks)
    lignes = ''.join('<b style="top:%.1fpx"></b>' % (h - h * v / vmax) for v, _ in ticks)
    labs = ''.join('<span>%s</span>' % e(lib) for lib, _ in groupes)
    leg = ''.join('<span><i style="background:%s"></i>%s</span>' % (c, e(l)) for l, c in legende)
    return ('<div class="t14-vz" style="--h:%dpx"><div class="t14-vy">%s</div><div class="t14-vp">%s<div class="t14-vb">%s'
            '</div></div><div class="t14-vx">%s</div>%s</div>'
            % (hauteur, grad, lignes, cols, labs, '<div class="t14-leg">%s</div>' % leg if leg else ''))


def _barres_h(items, vmax, couleur, ticks):
    """Barres horizontales (indexAxis 'y') : ``items`` (libellé, valeur)."""
    rangs = ''.join('<div class="t14-hb"><span class="l">%s</span><span class="p"><i style="width:%.1f%%;background:%s">'
                    '</i></span></div>' % (e(lib), 100.0 * v / vmax, couleur) for lib, v in items)
    axe = ''.join('<span style="left:%.1f%%">%s</span>' % (100.0 * v / vmax, e(t)) for v, t in ticks)
    return '<div class="t14-hbs">%s<div class="t14-hax"><span></span><span class="p">%s</span></div></div>' % (rangs, axe)


def _courbes(series, vmin, vmax, ticks):
    """L'indice des prix d'achat (base 100) : une courbe par article clé, légende en bas."""
    w, h = 640.0, 210.0
    n = len(MOIS)
    xs = [w * (i + 0.5) / n for i in range(n)]

    def y(v):
        return h - h * (v - vmin) / (vmax - vmin)
    grille = ''.join('<line x1="0" x2="%d" y1="%.1f" y2="%.1f" stroke="#E9ECEF"/>' % (w, y(v), y(v)) for v, _ in ticks)
    traces = ''
    for _, coul, vals in series:
        pts = ' '.join('%.1f,%.1f' % (x, y(v)) for x, v in zip(xs, vals))
        traces += ('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>%s'
                   % (pts, coul, ''.join('<circle cx="%.1f" cy="%.1f" r="3.5" fill="%s"/>' % (x, y(v), coul)
                                         for x, v in zip(xs, vals))))
    svg = '<svg width="%d" height="%d" viewBox="0 0 %d %d">%s%s</svg>' % (w, h, w, h, grille, traces)
    grad = ''.join('<span style="top:%.1fpx">%s</span>' % (y(v), e(t)) for v, t in ticks)
    labs = ''.join('<span>%s</span>' % e(m) for m in MOIS)
    leg = ''.join('<span><i style="background:%s"></i>%s</span>' % (c, e(nm)) for nm, c, _ in series)
    return ('<div class="t14-cz"><div class="t14-vy t14-cy">%s</div><div class="t14-cp">%s</div>'
            '<div class="t14-cx">%s</div><div class="t14-leg t14-cleg">%s</div></div>' % (grad, svg, labs, leg))


# AGING_COLORS (utils.js:19-21) : une couleur par tranche, du vert au bordeaux.
AGING_COLORS = ['#0F6E56', '#854F0B', '#A85A18', '#A32D2D', '#5e1b1b']


def _balance_agee():
    return _barres_v([(lib, [v]) for lib, v in zip(['Non échu', '1–30 j', '31–60 j', '61–90 j', '+90 j'], AGING)],
                     2000000, [(v, _compact(v) if v else '0') for v in range(0, 2000001, 500000)], [],
                     par_barre=AGING_COLORS)


def _vue(ident, v, actif, contenu, initiale=False):
    return vue_tdb(ident, '<div class="t14" data-layout-allow-overflow id="t14-in-%s">%s</div>'
                   % (v, _tete(v, actif) + contenu), initiale=initiale)


# -- l'onglet Tableau de bord

def _vue_tableau():
    cartes1 = [
        _kpi('t14-k-achats', 'Achats (période)', money(ACHATS), '%d commandes · %d réceptions' % (len(CMD), len(RECUS)),
             'bleu'),
        _kpi('t14-k-dette', 'Dette fournisseurs (401)', money(ENCOURS), '%d factures ouvertes' % len(FAC), 'rouge'),
        _kpi('t14-k-soon', 'À payer sous %d j' % CFG['soon'], money(sum(f['residual'] for f in SOON)),
             '%d facture(s) · trésorerie à prévoir' % len(SOON), 'ambre'),
        _kpi('t14-k-dpo', 'DPO — délai moyen de paiement', days(DPO),
             'encours / factures période · tenir les délais négociés', 'violet'),
    ]
    retard = sum(f['residual'] for f in RETARD)
    cartes2 = [
        _kpi('t14-k-retard', 'En retard de paiement', neg_money(retard),
             "%d facture(s) · %s de l'encours" % (len(RETARD), pct(retard / ENCOURS * 100))),
        _kpi('t14-k-409', 'Créances fournisseurs (409)', money(CREANCES['total']), 'consignes + avoirs + acomptes'),
        _kpi('t14-k-otif', 'Taux de service (OTIF)', pct(OTIF), "livré à l'heure et complet · cible ≥ 90 %"),
        _kpi('t14-k-cours', 'Commandes en cours', '%d cmd' % len(EN_COURS),
             '%s attendus · %d en retard' % (money(sum(c['montant'] for c in EN_COURS)), PENDING_LATE)),
    ]
    parts = [(r['nom'], r['achats'], COULEUR[r['nom']]) for r in FOUR if r['achats'] > 0]
    flux = _barres_v([(m, [b, p]) for m, b, p in FLUX], 5000000,
                     [(v, _compact(v) if v else '0') for v in range(0, 5000001, 1000000)], ['#714B67', '#3B6D11'],
                     [('Factures fournisseurs', '#714B67'), ('Paiements', '#3B6D11')], hauteur=176)
    graphes1 = '<div class="tdb-grille c2">%s%s</div>' % (
        _g('t14-g-sup', 'Achats par fournisseur (période)', _anneau(parts)),
        _g('t14-g-flux', 'Factures vs Paiements — 6 mois', flux))
    aging = _balance_agee()
    top = _barres_h(TOP_ARTICLES, 800000, '#714B67', [(v, _compact(v) if v else '0') for v in range(0, 800001, 200000)])
    graphes2 = '<div class="tdb-grille c2 t14-gg">%s%s</div>' % (
        _g('t14-g-aging', 'Balance âgée de la dette (par retard)', aging,
           '<div class="t14-mini">Un glissement vers +30/+60 j annonce une tension de trésorerie.</div>'),
        _g('t14-g-top', 'Top produits achetés (période)', top))
    contenu = (_section("Vue d'ensemble", cartes1) + _section('Indicateurs', cartes2)
               + '<div class="tdb-sect">Répartition &amp; flux</div>' + graphes1 + graphes2)
    return _vue('t14-dash', 'dash', 0, contenu, initiale=True)



# -- l'onglet Dettes & échéancier

COLS_DT = [('Échéance', '140px'), ('Fournisseur', '1fr'), ('Réf.', '230px'), ('Montant', '160px', 'd'),
           ('Payé', '140px', 'd'), ('Reste dû', '160px', 'd'), ('Retard', '120px', 'd'), ('Statut', '170px')]


def _vue_dettes():
    retard = sum(f['residual'] for f in RETARD)
    cartes = [
        _kpi('t14-d-enc', 'Encours total dû', money(ENCOURS), '%d factures ouvertes' % len(FAC), 'rouge'),
        _kpi('t14-d-ret', 'En retard', neg_money(retard), '%d facture(s) échue(s)' % len(RETARD), 'ambre'),
        _kpi('t14-d-soon', 'À payer sous %d j' % CFG['soon'], money(sum(f['residual'] for f in SOON)),
             'échéances imminentes'),
        _kpi('t14-d-mois', 'À payer sous 8–30 j', money(MONTH), 'à provisionner'),
    ]
    aging = _balance_agee()
    ech = _barres_v([(lib, [v]) for lib, v in zip(['Échu / S0', 'S1', 'S2', 'S3', 'S4', 'S5+'], SEMAINES)], 800000,
                    [(v, _compact(v) if v else '0') for v in range(0, 800001, 100000)], ['#185FA5'])
    graphes = '<div class="tdb-grille c2 t14-gg">%s%s</div>' % (
        _g('t14-g-aging2', 'Balance âgée (retard de paiement)', aging),
        _g('t14-g-ech', 'Échéancier — 6 prochaines semaines', ech))
    lignes = []
    for n, f in enumerate(FAC, 1):
        i = 't14-dt-r%d' % n
        lignes.append((i, [_c(iso(f['due'])), _four(f['four']), _c(f['ref'], cls='t14-mu'), _c(money(f['total']), 'd'),
                           _c(money_or_dash(f['paid']), 'd'), _c(money(f['residual']), 'd', 't14-b'),
                           _c(late_text(f), 'd', 't14-neg' if f['days_late'] > 0 else '', ident=i + '-ret'),
                           _badge(f['status'], f['status_cls'], i + '-st')]))
    note = _note('t14-dt-note', "<b>Bonne pratique :</b> payer à l'échéance protège vos <b>conditions</b> (délais, "
                 "remises, escomptes) et votre réputation fournisseur.")
    contenu = (_section('Dettes fournisseurs (401)', cartes) + graphes
               + _carte('Factures fournisseurs ouvertes (triées par urgence)', _table('t14-dt', COLS_DT, lignes),
                        ident='t14-dt-carte') + note)
    return _vue('t14-dettes', 'dettes', 2, contenu)


# -- l'onglet Avoirs & consignes

def _vue_avoirs():
    c = CREANCES
    cartes = [
        _kpi('t14-c-tot', 'Créances totales (409)', money(c['total']), 'consignes + avoirs + acomptes', 'violet'),
        _kpi('t14-c-dep', 'Consignes en cours (4096)', money(c['depots']), '%d casiers chez les fournisseurs' % c['qty'],
             'bleu'),
        _kpi('t14-c-avr', 'Avoirs à déduire (4097/4098)', money(c['avoirs']), '%d avoir(s) ouvert(s)' % len(AVOIRS),
             'ambre'),
        _kpi('t14-c-acp', 'Acomptes / soldes débiteurs (4091)', money(c['acomptes']),
             'paiements non lettrés (estimation)'),
    ]
    cs = _table('t14-cs-tab', [('Fournisseur', '1fr'), ('Casiers', '70px', 'd'), ('Consigne/casier', '108px', 'd'),
                               ('Valeur', '116px', 'd'), ('Dernière déconsignation', '140px')],
                [('t14-ac-r%d' % n, [_four(f), _c(str(q), 'd'), _c(money(u), 'd'), _c(money(q * u), 'd', 't14-b'),
                                     _c(iso(d), cls='t14-mu')]) for n, (f, q, u, d, _) in enumerate(CONSIGNES, 1)],
                't14-serre')
    av = _table('t14-av-tab', [('Date', '98px'), ('Fournisseur', '150px'), ('Réf.', '160px'), ('Motif', '1fr'),
                               ('Montant', '100px', 'd')],
                [('t14-av-r%d' % n, [_c(iso(d), cls='t14-mu'), _four(f, wrap=True), _c(r, cls='t14-mu'),
                                     _c(m, cls='t14-mu t14-wrap'), _c(money(a), 'd', 't14-b')])
                 for n, (d, f, r, m, a) in enumerate(AVOIRS, 1)], 't14-serre')
    gerer = _bt_contour('t14-gerer', 'Gérer les consignes')
    tables = '<div class="tdb-grille c2 t14-gg t14-ac">%s%s</div>' % (
        _carte("Consignes d'emballages (4096)", cs, 't14-cs-carte', gerer,
               "<div class=\"t14-mini\">Sans suivi à l'unité, le compte 4096 ne se solde jamais — comptez vos casiers "
               "périodiquement.</div>"),
        _carte('Avoirs fournisseurs ouverts', av, 't14-av-carte'))
    note = _note('t14-av-note', '<b>Réflexe :</b> chaque casse à la livraison, écart de facturation ou retour doit '
                 'générer un <b>avoir tracé</b> — et être <b>déduit du prochain paiement</b>. Un avoir oublié est une '
                 'perte sèche.')
    contenu = (_section("Créances fournisseurs (409) — l'argent qui dort chez vos fournisseurs", cartes) + tables + note)
    return _vue('t14-avoirs', 'avoirs', 3, contenu)


# -- le registre « Consignes fournisseurs » (liste éditable native)

COLS_CS = [('', '44px'), ('Fournisseur', '1fr'), ('Casiers consignés', '200px', 'd'), ('Consigne / casier', '200px', 'd'),
           ('Valeur immobilisée', '220px', 'd'), ('Dernière déconsignation', '250px'), ('Note', '240px'), ('', '40px')]
REGLAGES = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">'
            '<path d="M4 7h10M18 7h2M4 17h4M12 17h8"/><circle cx="16" cy="7" r="2"/><circle cx="10" cy="17" r="2"/></svg>')


def _vue_consignes():
    gab = ' '.join(c[1] for c in COLS_CS)
    tete = '<div class="t14-lt" style="grid-template-columns:%s">%s</div>' % (gab, ''.join(
        '<span%s>%s</span>' % (' class="t14-d"' if len(c) > 2 else '', '<i class="t14-cb"></i>' if k == 0 else (
            '<span class="t14-opt">%s</span>' % REGLAGES if k == len(COLS_CS) - 1 else e(c[0])))
        for k, c in enumerate(COLS_CS)))
    rangs = []
    for n, (f, q, u, d, note) in enumerate(CONSIGNES, 1):
        i = 't14-cs-r%d' % n
        if n == 1:
            qty = '<span class="t14-d t14-cel" id="%s-qty"><span class="entree t14-in" id="t14-cs-qty"><span class="ph" ' \
                  'id="t14-cs-qty-ph">%d</span><span class="val" id="t14-cs-qty-val"></span></span></span>' % (i, q)
            dte = '<span class="t14-cel" id="%s-date"><span class="entree t14-in" id="t14-cs-date"><span class="ph" ' \
                  'id="t14-cs-date-ph">%s</span><span class="val" id="t14-cs-date-val"></span></span></span>' % (i, fr(d))
        else:
            qty, dte = _c(str(q), 'd'), _c(fr(d))
        cells = ['<span><i class="t14-cb"></i></span>', '<span class="t14-cel t14-m2o">%s</span>' % e(f), qty,
                 '<span class="t14-d t14-cel t14-mon">%s</span>' % e(money(u)),
                 '<span class="t14-d" id="%s-val">%s</span>' % (i, e(money(q * u))), dte,
                 '<span class="t14-cel">%s</span>' % e(note), '<span></span>']
        rangs.append('<div class="t14-lr" id="%s" style="grid-template-columns:%s">%s</div>' % (i, gab, ''.join(cells)))
    total = ('<div class="t14-ltot" style="grid-template-columns:%s"><span></span><span></span><span></span><span></span>'
             '<span class="t14-d" id="t14-cs-tot">%s</span><span></span><span></span><span></span></div>'
             % (gab, e(money(CREANCES['depots']))))
    boutons = ('<span class="pile t14-cs-bts"><span class="bt primaire" id="t14-cs-new">Nouveau</span>'
               '<span class="t14-cs-save masque" id="t14-cs-save"><span class="bt primaire" id="t14-cs-save-bt">Enregistrer'
               '</span><span class="bt gris">Ignorer</span></span></span>')
    cp = ('<div class="cp t14-cpl">%s<div class="fil"><span class="parent" id="t14-cs-parent">Achats &amp; Fournisseurs — '
          'Tableau de bord</span><span class="ref">Consignes fournisseurs <span class="t14-gear-cp">%s</span></span></div>'
          '%s<span class="pager">1-3 / 3</span><span class="t14-nav"><i>‹</i><i>›</i></span></div>'
          % (boutons, ENGRENAGE, recherche()))
    return vue_libre('t14-consignes', cp + '<div class="t14-liste">%s%s%s</div>' % (tete, ''.join(rangs), total))


# -- l'onglet Commandes & réceptions

COLS_OD = [('Date', '130px'), ('Fournisseur', '1fr'), ('Réf.', '100px'), ('Montant', '140px', 'd'), ('Prévue', '130px'),
           ('Reçue', '130px'), ('Retard', '90px', 'd'), ('Complète', '110px', 'c'), ('Statut', '180px')]


def _vue_commandes():
    cartes = [
        _kpi('t14-o-nb', 'Commandes (période)', str(len(CMD)), '%s engagés' % money(ACHATS), 'bleu'),
        _kpi('t14-o-ret', 'En retard de livraison', str(PENDING_LATE + RECV_LATE),
             '%d en attente · %d reçues en retard' % (PENDING_LATE, RECV_LATE), 'ambre'),
        _kpi('t14-o-otif', 'OTIF (période)', pct(OTIF), "à l'heure et complètes"),
        _kpi('t14-o-delai', 'Délai moyen de réception', days(DELAI), 'commande → réception'),
    ]
    lignes = []
    for n, c in enumerate(CMD, 1):
        i = 't14-od-r%d' % n
        complet = '—' if c['is_full'] is None else ('✓' if c['is_full'] else '✗')
        lignes.append((i, [_c(iso(c['date'])), _four(c['four']), _c(c['ref'], cls='t14-mu'), _c(money(c['montant']), 'd'),
                           _c(iso(c['prevue'])), _c(iso(c['recue'])),
                           _c('%d j' % c['days_late'] if c['days_late'] else '—', 'd',
                              't14-neg' if c['days_late'] > 0 else ''),
                           _c(complet, 'c', 't14-ok' if complet == '✓' else ('t14-ko' if complet == '✗' else ''),
                              ident=i + '-full'),
                           _badge(c['status'], c['status_cls'], i + '-st')]))
    note = _note('t14-od-note', "<b>OTIF</b> = livré <b>à l'heure ET complet</b>. Un fournisseur peut être ponctuel mais "
                 "livrer incomplet — c'est l'OTIF qui révèle l'écart. Cible PME : ≥ 90 %.")
    contenu = (_section('Commandes &amp; réceptions'.replace('&amp;', '&'), cartes)
               + _carte('Journal des commandes', _table('t14-od', COLS_OD, lignes), 't14-od-carte') + note)
    return _vue('t14-cmd', 'cmd', 4, contenu)


# -- l'onglet Fournisseurs

COLS_FR = [('Fournisseur', '1fr'), ('Achats période', '180px', 'd'), ('Part', '100px', 'd'), ('Encours dû', '170px', 'd'),
           ('En retard', '160px', 'd'), ('Délai moy.', '120px', 'd'), ('OTIF', '100px', 'd'), ('Statut', '150px')]


def _vue_fournisseurs():
    over = TOP['part'] >= CFG['dep']
    cartes = [
        _kpi('t14-f-nb', 'Fournisseurs actifs', str(len([r for r in FOUR if r['achats'] > 0])), 'avec achats sur la période',
             'bleu'),
        _kpi('t14-f-top', 'Top fournisseur', TOP['nom'],
             pct(TOP['part']) + ' des achats' + (' · seuil de dépendance dépassé' if over else ''), 'ambre'),
        _kpi('t14-f-delai', 'Délai moyen de livraison', days(DELAI), 'commande → réception'),
        _kpi('t14-f-otif', 'OTIF moyen', pct(OTIF), "à l'heure et complet"),
    ]
    lignes = []
    for n, r in enumerate(FOUR, 1):
        i = 't14-fr-r%d' % n
        lignes.append((i, [_four(r['nom'], True), _c(money(r['achats']), 'd'), _c(pct(r['part']), 'd', ident=i + '-part'),
                           _c(money_or_dash(r['du']), 'd'),
                           _c(money_or_dash(r['retard']), 'd', 't14-neg' if r['retard'] > 0 else ''),
                           _c(days(r['delai']) if r['delai'] else '—', 'd'), _c(pct(r['otif']) if r['achats'] else '—', 'd'),
                           _badge(r['badge'], r['badge_cls'], i + '-st')]))
    cfg = _bt_contour('t14-cfg', 'Configurer les alertes', ENGRENAGE)
    note = _note('t14-fr-note', '<b>Risque de concentration :</b> au-delà de <b>%s</b> des achats chez un seul fournisseur, '
                 'une rupture ou une hausse de tarif vous expose fortement — négociez ou diversifiez.' % pct(CFG['dep']))
    contenu = (_section('Performance fournisseurs', cartes)
               + _carte('Détail par fournisseur', _table('t14-fr', COLS_FR, lignes), 't14-fr-carte', cfg) + note)
    return _vue('t14-four', 'four', 1, contenu)


# -- l'onglet Prix & variations

COLS_PX = [('Produit', '1.1fr'), ('Fournisseur', '1fr'), ('Prix N−6m', '84px', 'd'), ('Prix actuel', '84px', 'd'),
           ('Δ', '58px', 'd'), ('Impact annuel', '106px', 'd'), ('Statut', '112px')]


def _vue_prix():
    cartes = [
        _kpi('t14-p-var', 'Variation moyenne pondérée', signed_pct(VAR_MOY), "sur le panier d'achats récent", 'ambre'),
        _kpi('t14-p-top', 'Plus forte hausse', signed_pct(TOP_HAUSSE['delta']), TOP_HAUSSE['nom'], 'rouge'),
        _kpi('t14-p-nb', 'Hausses > %s' % pct(CFG['price']), str(NB_HAUSSES), 'références concernées'),
        _kpi('t14-p-imp', 'Impact annuel estimé', neg_money(IMPACT), 'Δ prix × volumes annuels'),
    ]
    series = []
    for k, p in enumerate(PX[:5]):
        base = p['mensuel'][0]
        series.append((p['nom'], PALETTE[k], [round(v / base * 100.0, 1) for v in p['mensuel']]))
    idx = _g('t14-g-idx', "Indice des prix d'achat (base 100)",
             _courbes(series, 92, 110, [(v, str(v)) for v in range(92, 111, 2)]))
    lignes = []
    for n, p in enumerate(PX, 1):
        i = 't14-pr-r%d' % n
        lignes.append((i, ['<span class="t14-b t14-wrap">%s</span>' % e(p['nom']),
                           '<span class="t14-mu t14-wrap">%s</span>' % e(p['four']),
                           _c(money(p['p0']), 'd'), _c(money(p['p1']), 'd'),
                           _c(signed_pct(p['delta']), 'd', 't14-neg' if p['delta'] > 0 else ('t14-pos' if p['delta'] < 0 else '')),
                           _c(impact_text(p), 'd', 't14-neg' if p['impact'] > 0 else 't14-pos', ident=i + '-imp'),
                           _badge(p['badge'], p['badge_cls'], i + '-st')]))
    table = _carte('Variations par produit', _table('t14-pr', COLS_PX, lignes, 't14-serre t14-px-tab'), 't14-pr-carte')
    note = _note('t14-px-note', '<b>Contrôle des prix facturés :</b> comparez chaque facture au prix négocié — les dérives '
                 'passent par petites touches. Au-delà du seuil, renégociez ou mettez en concurrence.')
    contenu = (_section("Prix d'achat — variations", cartes)
               + '<div class="tdb-grille c2 t14-gg t14-px">%s%s</div>' % (idx, table) + note)
    return _vue('t14-prix', 'prix', 5, contenu)


# -- la fenêtre « ⚙ Alertes achats & fournisseurs »

def _modale():
    champs = [('Alerte échéance (jours avant)', CFG['soon']), ('Tolérance retard livraison (jours)', CFG['late']),
              ('Seuil de dépendance fournisseur (%)', int(CFG['dep'])), ('Seuil de hausse de prix (%)', int(CFG['price']))]
    grille = ''.join('<label>%s<span class="t14-inp">%d</span></label>' % (e(l), v) for l, v in champs)
    return ('<div class="t14-voile masque" id="t14-modal-voile" data-layout-allow-overlap data-layout-allow-occlusion></div>'
            '<div class="t14-modal masque" id="t14-modal" data-layout-allow-overlap data-layout-allow-occlusion>'
            '<div class="t14-mh"><div><div class="t14-mt">%sAlertes achats &amp; fournisseurs</div>'
            '<div class="t14-ms">Valeurs globales de la société</div></div><span class="t14-mx">×</span></div>'
            '<div class="t14-mb"><div class="t14-cfg">%s</div>'
            '<div class="t14-mini" id="t14-m-aide">Échéance : factures dues sous ce délai → « À payer bientôt ». '
            'Livraison : au-delà du seuil → « En retard » (l\'OTIF reste strict). Dépendance : badge au-delà de cette '
            'part d\'achats. Prix : « Hausse forte » au-delà du seuil.</div>'
            '<div class="t14-ma"><span class="t14-mbt prim">Enregistrer la configuration</span>'
            '<span class="t14-mbt sec" id="t14-m-annuler">Annuler</span></div></div></div>' % (ENGRENAGE, grille))


MENUS = ['Commandes', 'Tableau de bord AITE', 'Produits', 'Analyse', 'Configuration']
ECRAN = navigateur(fenetre_muk('app-t14', 'Achats', MENUS,
                               [_vue_tableau(), _vue_dettes(), _vue_avoirs(), _vue_consignes(), _vue_commandes(),
                                _vue_fournisseurs(), _vue_prix()],
                               actif='Tableau de bord AITE', societe=demo.SOCIETE, initiale=NOM[0], avatar='#854F0B',
                               apps=APPS_PROFIL['direction'], app_active='Achats', calques=_modale()))

CSS = """
.t14 .tdb-tete { padding: 13px 22px; }
.t14 .tdb-titre { font-size: 26px; }
.t14 .tdb-filtres { padding: 6px 22px; }
.t14 .tdb-rang { height: 48px; }
.t14 .tdb-lib { width: 150px; flex: none; }
.t14 .chip { font-size: 16px; padding: 0 12px; height: 36px; }
.t14 .tdb-sect { margin: 14px 2px 8px; color: #57564F; }
.t14 .kpi { min-height: 0; padding: 13px 18px 12px; }
.t14 .kpi-l { font-size: 14px; }
.t14 .kpi-v { margin-top: 6px; font-size: 31px; color: #212529; }
.t14 .kpi-s { white-space: normal; overflow: visible; line-height: 1.3; color: #5F666D; }
#t14-f-top-v { white-space: normal; font-size: 27px; line-height: 1.15; }
.t14-pt { display: inline-block; width: 11px; height: 11px; border-radius: 50%; margin-right: 8px; flex: none; }
.t14-date { height: 36px; padding: 0 12px; border: 1px solid #DEE2E6; border-radius: 8px; display: inline-flex; align-items: center;
  gap: 14px; font-size: 16px; color: #212529; }
.t14-esp { margin-left: auto; }
.t14-cal { width: 17px; height: 17px; color: #495057; }
.t14-fl { font-size: 18px; color: #6C757D; }
.t14-onglets { margin-top: 12px; background: #fff; border-radius: 12px; padding: 7px 10px; display: flex; gap: 6px; }
.t14-onglet { height: 40px; padding: 0 18px; border-radius: 8px; display: inline-flex; align-items: center; font-size: 17px;
  color: #5F5E5A; white-space: nowrap; }
.t14-onglet.actif { background: #714B67; color: #fff; }
.t14-carte { margin-top: 14px; background: #fff; border-radius: 12px; padding: 12px 18px 12px; }
.t14-ct { display: flex; align-items: center; justify-content: space-between; height: 42px; margin-bottom: 6px; }
.t14-carte h3, .t14-g h3 { font-size: 19px; font-weight: 600; color: #2B2A28; white-space: nowrap; }
.t14-th, .t14-tr { display: grid; align-items: center; column-gap: 12px; padding: 0 12px; }
.t14-th { height: 38px; background: #F5F5F4; font-size: 13px; font-weight: 700; letter-spacing: .05em; text-transform: uppercase;
  color: #5F5E5A; white-space: nowrap; }
.t14-tr { min-height: 44px; border-bottom: 1px solid #EEF0F2; font-size: 17px; color: #212529; white-space: nowrap; }
.t14-d { text-align: right; font-variant-numeric: tabular-nums; }
.t14-c { text-align: center; }
.t14-b { font-weight: 700; }
.t14-mu { color: #5F666D; }
.t14-ell { overflow: hidden; text-overflow: ellipsis; }
.t14-wrap { white-space: normal; line-height: 1.2; }
.t14-neg { color: #C82333; }
.t14-pos { color: #1E7B34; }
.t14-ok { color: #1E7B34; font-weight: 700; }
.t14-ko { color: #C82333; font-weight: 700; }
.t14-nom { display: inline-flex; align-items: center; min-width: 0; overflow: hidden; text-overflow: ellipsis; }
.t14-badge { display: inline-flex; align-items: center; height: 26px; padding: 0 9px; border-radius: 6px; font-size: 14px; font-weight: 700; }
.t14-badge.rouge { background: #C82333; color: #fff; }
.t14-badge.ambre { background: #F0AD00; color: #2B1D00; }
.t14-badge.vert { background: #1E7B34; color: #fff; }
.t14-badge.bleu { background: #0E7490; color: #fff; }
.t14-badge.gris { background: #E9ECEF; color: #212529; }
.t14-note { margin-top: 12px; background: #FAF6E9; border: 1px solid #E8DFB8; border-radius: 10px; padding: 11px 16px; font-size: 17px;
  color: #6B5D20; line-height: 1.45; }
.t14-mini { margin-top: 6px; font-size: 15px; color: #6C6B66; line-height: 1.4; }
.t14-btc { height: 36px; padding: 0 12px; border: 1px solid var(--muk-prim); border-radius: 6px; color: #3F6A83; background: #fff;
  display: inline-flex; align-items: center; gap: 8px; font-size: 16px; white-space: nowrap; }
.t14-gear { width: 17px; height: 17px; }
.t14-gg { margin-top: 14px; }
.t14-g { position: relative; background: #fff; border-radius: 12px; padding: 14px 18px; height: 318px; }
.t14-g .t14-mini { position: absolute; left: 18px; bottom: 10px; }
.t14-ac .t14-carte { margin-top: 0; }
/* anneau */
.t14-an { position: absolute; left: 18px; right: 18px; top: 58px; bottom: 14px; display: flex; align-items: center; gap: 46px; padding-left: 80px; }
.t14-an svg { width: 230px; height: 230px; flex: none; }
.t14-an-leg { display: flex; flex-direction: column; gap: 9px; font-size: 15px; color: #495057; }
.t14-an-leg div { display: flex; align-items: center; gap: 10px; white-space: nowrap; }
.t14-an-leg i { width: 26px; height: 13px; display: inline-block; }
/* barres verticales */
.t14-vz { position: absolute; left: 18px; right: 18px; top: 58px; bottom: 10px; }
.t14-vy { position: absolute; left: 0; top: 0; width: 56px; height: var(--h); }
.t14-vy span { position: absolute; right: 6px; transform: translateY(-50%); font-size: 13px; color: #6C757D; white-space: nowrap; }
.t14-vp { position: absolute; left: 60px; right: 0; top: 0; height: var(--h); }
.t14-vp b { position: absolute; left: 0; right: 0; height: 1px; background: #E9ECEF; }
.t14-vb { position: absolute; inset: 0; display: flex; justify-content: space-around; align-items: flex-end; }
.t14-vg { position: relative; width: 70px; height: 100%; display: flex; gap: 6px; align-items: flex-end; }
.t14-vg i { flex: 1; border-radius: 3px 3px 0 0; }
.t14-vx { position: absolute; left: 60px; right: 0; top: calc(var(--h) + 6px); display: flex; justify-content: space-around; font-size: 13px;
  color: #495057; white-space: nowrap; }
.t14-vx span { width: 0; display: flex; justify-content: center; }
.t14-leg { position: absolute; left: 60px; right: 0; top: calc(var(--h) + 30px); display: flex; justify-content: center; gap: 26px; font-size: 14px;
  color: #495057; }
.t14-leg span { display: inline-flex; align-items: center; gap: 8px; white-space: nowrap; }
.t14-leg i { width: 26px; height: 11px; display: inline-block; }
/* barres horizontales */
.t14-hbs { position: absolute; left: 18px; right: 22px; top: 54px; bottom: 12px; display: flex; flex-direction: column; }
.t14-hb { flex: 1; display: grid; grid-template-columns: 200px 1fr; column-gap: 10px; align-items: center; }
.t14-hb .l { font-size: 13px; color: #495057; text-align: right; white-space: nowrap; }
.t14-hb .p { position: relative; height: 100%; border-left: 1px solid #CED4DA; }
.t14-hb .p i { position: absolute; left: 0; top: 18%; bottom: 18%; border-radius: 0 3px 3px 0; }
.t14-hax { height: 22px; display: grid; grid-template-columns: 200px 1fr; column-gap: 10px; }
.t14-hax .p { position: relative; }
.t14-hax .p span { position: absolute; top: 3px; transform: translateX(-50%); font-size: 13px; color: #6C757D; white-space: nowrap; }
/* courbes */
.t14-cz { position: absolute; left: 18px; right: 18px; top: 60px; bottom: 10px; }
.t14-cy { height: 210px; }
.t14-cp { position: absolute; left: 60px; top: 0; }
.t14-cx { position: absolute; left: 60px; top: 216px; width: 640px; display: flex; justify-content: space-around; font-size: 13px; color: #495057; }
.t14-cx span { width: 0; display: flex; justify-content: center; }
.t14-cleg { top: 240px; left: 10px; right: 0; flex-wrap: wrap; gap: 6px 18px; font-size: 13px; }
.t14-px .t14-g { height: auto; min-height: 520px; }
.t14-px .t14-carte { margin-top: 0; }
.t14-serre .t14-th { height: 50px; white-space: normal; line-height: 1.2; column-gap: 10px; padding: 0 10px; font-size: 12px; }
.t14-serre .t14-tr { font-size: 15px; column-gap: 10px; padding: 4px 10px; min-height: 46px; }
.t14-px-tab .t14-tr { font-size: 14px; column-gap: 8px; padding: 3px 10px; }
.t14-px-tab .t14-th { column-gap: 8px; }
.t14-px-tab .t14-badge { font-size: 13px; padding: 0 7px; }
.t14-nom.t14-wrap { white-space: normal; align-items: flex-start; }
.t14-nom.t14-wrap .t14-pt { margin-top: 6px; }
/* registre des consignes (liste éditable native) */
.t14-cpl .fil { margin-left: 4px; }
.t14-cpl .fil .parent { color: #3F6A83; }
.t14-cpl .fil .ref { display: inline-flex; align-items: center; gap: 10px; font-size: 22px; }
.t14-gear-cp { width: 18px; height: 18px; color: #495057; display: inline-flex; }
.t14-gear-cp svg { width: 18px; height: 18px; }
.t14-cpl .recherche { margin-left: 180px; }
.t14-cs-bts { width: 236px; height: 44px; flex: none; }
.t14-cs-save { display: flex; gap: 6px; }
.t14-nav { display: flex; gap: 2px; margin-left: 12px; }
.t14-nav i { width: 38px; height: 38px; border-radius: 4px; background: #E9ECEF; color: #343A40; font-style: normal; font-size: 22px;
  display: flex; align-items: center; justify-content: center; }
.t14-liste { background: #fff; }
.t14-lt, .t14-lr, .t14-ltot { display: grid; align-items: center; column-gap: 14px; padding: 0 18px 0 8px; }
.t14-lt { height: 54px; border-bottom: 1px solid var(--o-filet); font-size: 19px; font-weight: 600; color: var(--o-texte); white-space: nowrap; }
.t14-lr { height: 56px; border-bottom: 1px solid #EEF0F2; font-size: 19px; color: var(--o-texte); white-space: nowrap; }
.t14-ltot { height: 54px; font-size: 19px; font-weight: 700; color: var(--o-texte); }
.t14-cb { display: inline-block; width: 18px; height: 18px; border: 1px solid #ADB5BD; border-radius: 3px; margin-left: 10px; }
.t14-opt { display: inline-flex; width: 22px; height: 22px; color: #495057; }
.t14-opt svg { width: 22px; height: 22px; }
.t14-cel { position: relative; }
.t14-lr .entree.t14-in { margin: 0; height: 40px; border: 0; border-radius: 0; padding: 0; font-size: 19px; background: transparent; }
.t14-lr .entree.t14-in .ph { color: var(--o-texte); }
.t14-lr .t14-d .entree.t14-in .ph, .t14-lr .t14-d .entree.t14-in .val { left: auto; right: 0; }
.t14-lr .entree.t14-in .ph, .t14-lr .entree.t14-in .val { left: 0; font-weight: 400; }
.t14-lr.t14-edit { background: #fff; box-shadow: inset 0 0 0 1px #CED4DA; }
.t14-lr.t14-edit .t14-cel { border-bottom: 1px solid #9AA4AD; height: 38px; display: flex; align-items: center; }
.t14-lr.t14-edit .t14-cel.t14-d { justify-content: flex-end; }
/* fenêtre de configuration */
.t14-voile { position: absolute; inset: 0; background: rgba(0,0,0,.35); z-index: 30; }
.t14-modal { position: absolute; left: 50%; top: 170px; width: 900px; margin-left: -450px; z-index: 31; background: #fff; border-radius: 12px;
  overflow: hidden; box-shadow: 0 24px 64px rgba(0,0,0,.32); }
.t14-mh { background: #714B67; color: #fff; padding: 18px 22px; display: flex; justify-content: space-between; align-items: center; }
.t14-mt { font-size: 21px; font-weight: 700; display: flex; align-items: center; gap: 10px; }
.t14-mt .t14-gear { width: 21px; height: 21px; }
.t14-ms { font-size: 15px; margin-top: 2px; color: #F1E8EF; }
.t14-mx { font-size: 28px; line-height: 1; }
.t14-mb { padding: 18px 22px 22px; }
.t14-cfg { display: grid; grid-template-columns: 1fr 1fr; gap: 14px 18px; }
.t14-cfg label { font-size: 17px; font-weight: 600; color: #46414E; display: flex; flex-direction: column; gap: 6px; }
.t14-inp { height: 42px; border: 1px solid #D9D9D9; border-radius: 8px; padding: 0 12px; font-size: 18px; font-weight: 400; color: #212529;
  display: flex; align-items: center; }
#t14-m-aide { margin-top: 12px; font-size: 16px; }
.t14-ma { display: flex; gap: 10px; margin-top: 18px; }
.t14-mbt { height: 46px; border-radius: 6px; display: inline-flex; align-items: center; justify-content: center; padding: 0 20px; font-size: 18px; }
.t14-mbt.prim { flex: 1; background: var(--muk-prim); color: #fff; }
.t14-mbt.sec { background: #E9ECEF; color: #212529; }
"""

TUTORIEL = {
    'slug': 't14-achats',
    'profil': 't14_achats',
    'numero': 14,
    'titre': "Achats & Fournisseurs : ce que vous devez, ce qu'on vous doit",
    'fonction': 'Achats & fournisseurs',
    'personnage': (NOM, ROLE),
    'accroche': {
        'kicker': 'Achats & fournisseurs',
        'question': 'Et ce que vos fournisseurs vous *doivent* ?',
        'douleurs': [('boite', 'Des casiers consignés suivis nulle part'),
                     ('document', 'Un avoir oublié : une perte sèche'),
                     ('graphe', 'Des prix qui montent par petites touches'),
                     ('sablier', 'Des factures qui glissent à +60 jours'),
                     ('alerte', 'Livré à l’heure… mais incomplet'),
                     ('cible', 'Tout acheté chez un seul fournisseur')],
        'voix': "Et ce que vos fournisseurs vous doivent ? Casiers consignés, avoirs oubliés : c'est votre argent qui "
                "dort chez eux.",
    },
    'revelation': {
        'promesse': "Ce que vous devez, trié par urgence. Ce qu'on vous doit : casiers consignés et avoirs. "
                    "Et la ponctualité comme les prix de chaque fournisseur.",
        'voix': "Avec Aïte haousse, un seul écran montre ce que vous devez, et ce qu'on vous doit.",
    },
    'temps': ['Ce que je dois', "Ce qu'on me doit", 'Mes fournisseurs'],
    'app': 'app-t14',
    'ecran': ECRAN,
    'vues_initiales': {'odoo': 't14-dash'},
    'css': CSS,
    'bulles': {
        'b-urgence': "Triées par urgence : les retards d'abord, puis les échéances les plus proches.",
        'b-consigne': 'Valeur immobilisée = casiers × consigne : calculée toute seule.',
        'b-otif': "À l'heure ET complète : il manque une condition, la commande sort de l'OTIF.",
        'b-dep': "Au-delà de 40 % des achats chez un seul fournisseur : badge Dépendance.",
        'b-prix': 'Impact sur un an = écart de prix × volume mensuel × 12.',
    },
    'reactions': {
        'r-avoir': 'Ces avoirs, je les déduis du prochain paiement.',
        'r-prix': 'Avec ces chiffres, je renégocie.',
    },
    'etapes': [
        {'temps': 0, 'titre': 'Le tableau de bord Achats',
         'texte': 'Achats du mois, dette fournisseurs, factures à payer sous 7 jours : tout sur un écran.',
         'voix': "Danielle ouvre le tableau de bord Achats : achats du mois, dette fournisseurs, factures à payer sous "
                 "sept jours. Tout vient des commandes et des factures déjà saisies.",
         'gestes': [curseur('#app-t14 .o-haut .menu.actif', d=0.6), anneau('#app-t14 .o-haut .menu.actif', d=1.1),
                    compter('#t14-k-dette-v', 0, ENCOURS, d=1.2, apres=' FCFA', avec=True),
                    anneau('#t14-k-dette', d=1.2), anneau('#t14-k-soon', d=1.4),
                    defiler('#t14-in-dash', -300, d=0.9), anneau('#t14-g-sup', d=1.4), anneau('#t14-g-flux', d=1.2)]},
        {'temps': 0, 'titre': 'Dettes & échéancier',
         'texte': 'Balance âgée, décaissements des 6 prochaines semaines, factures triées par urgence.',
         'voix': "Dettes et échéancier : la balance âgée montre ce qui glisse en retard, l'échéancier ce qu'il faudra "
                 "payer semaine après semaine. Les factures se trient seules : les retards d'abord, puis les échéances "
                 "proches.",
         'gestes': [defiler('#t14-in-dash', 0, d=0.5), clic('#t14-tab-dash-2', d=0.6), vue('t14-dettes'),
                    anneau('#t14-g-aging2', d=1.1), anneau('#t14-g-ech', d=1.1),
                    defiler('#t14-in-dettes', -548, d=0.9), curseur('#t14-dt-r1-st', fx=1.45, fy=0.9, d=0.5),
                    zoom('#t14-dt-r3', s=1.3, fx=0.5, d=0.8, avec=True),
                    bulle('b-urgence', '#t14-dt-r1-st', cote='haut', d=2.4), anneau('#t14-dt-r1-st', d=0.8),
                    anneau('#t14-dt-r3-st', d=0.8), anneau('#t14-dt-r6-st', d=0.8), dezoom(d=0.6)]},
        {'temps': 1, 'titre': 'Avoirs & consignes',
         'texte': "Les casiers consignés chez vos fournisseurs, et les avoirs à déduire du prochain paiement.",
         'voix': "De l'autre côté, ce qu'on vous doit : les casiers consignés chez vos fournisseurs, en valeur, et les "
                 "avoirs ouverts, à déduire du prochain paiement. Car un avoir oublié, c'est une perte sèche.",
         'gestes': [defiler('#t14-in-dettes', 0, d=0.5), clic('#t14-tab-dettes-3', d=0.6), vue('t14-avoirs'),
                    curseur('#t14-c-dep', fx=0.93, fy=0.86, d=0.5), anneau('#t14-c-dep', d=1.1, avec=True),
                    anneau('#t14-c-avr', d=1.1), defiler('#t14-in-avoirs', -62, d=0.6), anneau('#t14-cs-tab', d=1.2),
                    anneau('#t14-av-tab', d=1.2), anneau('#t14-av-note', d=1.4), reaction('r-avoir', d=2.6), pause(1.6)]},
        {'temps': 1, 'titre': 'Le registre des consignes',
         'texte': 'Une ligne par fournisseur : la valeur immobilisée se recalcule seule.',
         'voix': "Vingt casiers viennent d'être rendus au fournisseur de bières. Dans le registre des consignes, Danielle "
                 "passe la ligne de quarante-huit à vingt-huit casiers et note la date : la valeur immobilisée se "
                 "recalcule seule.",
         'gestes': [clic('#t14-gerer', d=0.6), vue('t14-consignes'), zoom('#t14-cs-r1', s=1.3, fx=0.48, d=0.8),
                    clic('#t14-cs-r1-qty', fx=0.85, d=0.5), classe('#t14-cs-r1', ajouter=['t14-edit']),
                    cacher('#t14-cs-new', d=0.15), montrer('#t14-cs-save', d=0.2, y=0, avec=True),
                    saisir('t14-cs-qty', str(CONSIGNES[0][1] - RENDUS)),
                    texte('#t14-cs-r1-val', money((CONSIGNES[0][1] - RENDUS) * CONSIGNES[0][2])),
                    clic('#t14-cs-r1-date', fx=0.3, d=0.4), saisir('t14-cs-date', fr(AUJ)),
                    bulle('b-consigne', '#t14-cs-r1-val', cote='bas', d=2.6), pause(1.8),
                    clic('#t14-cs-save-bt', d=0.6), classe('#t14-cs-r1', retirer=['t14-edit']),
                    cacher('#t14-cs-save', d=0.15),
                    animer('#t14-cs-new', {'autoAlpha': 0}, {'autoAlpha': 1}, d=0.2, avec=True),
                    texte('#t14-cs-tot', money(CREANCES_APRES['depots'])), anneau('#t14-cs-tot', d=1.0),
                    dezoom(d=0.6)]},
        {'temps': 2, 'titre': 'Commandes & réceptions',
         'texte': "L'OTIF ne compte que les livraisons à l'heure ET complètes.",
         'voix': "Commandes et réceptions : chaque commande dit si elle est arrivée à l'heure, et complète. L'OTIF exige "
                 "les deux à la fois : la commande de l'épicerie, livrée à temps mais incomplète, n'y compte pas.",
         'gestes': [clic('#t14-cs-parent', d=0.6), texte('#t14-k-409-v', money(CREANCES_APRES['total'])),
                    vue('t14-dash'), pause(0.2), clic('#t14-tab-dash-4', d=0.6), vue('t14-cmd'),
                    anneau('#t14-o-otif', d=1.1), defiler('#t14-in-cmd', -323, d=0.8),
                    curseur('#t14-od-r5-st', fx=1.25, fy=0.8, d=0.5),
                    zoom('#t14-od-r5', s=1.35, fx=0.62, d=0.8, avec=True), anneau('#t14-od-r5-full', d=1.0),
                    bulle('b-otif', '#t14-od-r5-full', cote='haut', d=2.8), pause(2.0), dezoom(d=0.6)]},
        {'temps': 2, 'titre': 'Fournisseurs',
         'texte': 'Part des achats, encours, retards, OTIF ; au-delà de 40 %, le badge Dépendance.',
         'voix': "Côté fournisseurs, Boissons du Wouri pèse plus de la moitié des achats du mois : au-delà de quarante "
                 "pour cent, le badge Dépendance s'allume. Les quatre seuils se règlent ici, chacun avec sa phrase "
                 "d'explication.",
         'gestes': [defiler('#t14-in-cmd', 0, d=0.5), clic('#t14-tab-cmd-1', d=0.6), vue('t14-four'),
                    anneau('#t14-f-top', d=1.2), defiler('#t14-in-four', -150, d=0.7), anneau('#t14-fr-r1-part', d=0.9),
                    bulle('b-dep', '#t14-fr-r1-st', cote='haut', d=2.6), anneau('#t14-fr-r1-st', d=1.2), pause(0.6),
                    clic('#t14-cfg', d=0.6), ouvrir('t14-modal'), anneau('#t14-m-aide', d=1.6),
                    clic('#t14-m-annuler', d=0.5), fermer('t14-modal')]},
        {'temps': 2, 'titre': 'Prix & variations',
         'texte': "Les 45 derniers jours face aux prix d'il y a 4 à 7 mois : la hausse, chiffrée sur un an.",
         'voix': "Enfin, Prix et variations compare le prix payé ces quarante-cinq derniers jours à celui d'il y a quatre "
                 "à sept mois. La bière blonde a pris plus de huit pour cent : hausse forte, et l'impact sur un an est "
                 "chiffré.",
         'gestes': [defiler('#t14-in-four', 0, d=0.5), clic('#t14-tab-four-5', d=0.6), vue('t14-prix'),
                    compter('#t14-p-imp-v', 0, IMPACT, d=1.2, avant='−', apres=' FCFA'), anneau('#t14-p-top', d=1.1),
                    defiler('#t14-in-prix', -293, d=0.8), curseur('#t14-g-idx', fx=0.9, fy=0.42, d=0.5),
                    anneau('#t14-g-idx', d=1.1, avec=True), zoom('#t14-pr-r1', s=1.4, d=0.8), bulle('b-prix', '#t14-pr-r1-imp', cote='bas', d=2.6), pause(2.0),
                    dezoom(d=0.6), reaction('r-prix', d=2.8, avec=True), pause(1.8)]},
    ],
    'resultats': {
        'titre': 'La relation fournisseurs, pilotée dans les deux sens',
        'cartes': [
            {'valeur': '6', 'compter': 6, 'unite': 'semaines', 'icone': 'horloge',
             'texte': "d'échéancier : ce qu'il faudra payer, semaine par semaine"},
            {'valeur': '5', 'compter': 5, 'unite': 'tranches', 'icone': 'sablier',
             'texte': "de balance âgée, du non échu à plus de 90 jours de retard"},
            {'valeur': '4', 'compter': 4, 'unite': 'seuils', 'icone': 'cloche',
             'texte': 'réglables sans code : échéance, retard de livraison, dépendance, hausse de prix'},
        ],
        'voix': "Six semaines d'échéancier, cinq tranches de retard, quatre seuils réglables : la relation fournisseurs "
                "se pilote dans les deux sens.",
    },
    'cta': {
        'appel': 'Demandez votre démonstration',
        'suivant': 'Le cockpit de la direction',
        'voix': "Aïte haousse, par Aïte Consulting. Demandez votre démonstration. Prochain tutoriel : le cockpit de la "
                "direction.",
    },
    'vignette': {'etape': 2, 'apres': 9.0},
}
