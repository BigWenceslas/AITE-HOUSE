# -*- coding: utf-8 -*-
"""Tutoriel 13 — Stock bar & cave : rien ne dort, rien ne fuit.

Le magasinier (profil Magasin, groupe Inventaire / Utilisateur) ouvre le
tableau de bord Stock & Inventaire d'aite_stock_dashboard et le parcourt
onglet par onglet : la photo du stock, les alertes triées par urgence, la
quantité à commander, le stock par emplacement, les dormants, le coulage.

Sources des libellés (tous relevés mot pour mot) :

- menu « Tableau de bord AITE » : addons/aite_stock_dashboard/views/
  stock_dashboard_menus.xml:9-14 (groupe stock.group_stock_user) ; menus
  natifs « Vue d'ensemble », « Opérations », « Produits », application
  « Inventaire » : odoo18/addons/stock/i18n/fr.po (Overview, Operations,
  Products, Inventory) ; menus du profil Magasin repris de
  scenarios/c5_magasin.py, applications de ecrans.APPS_PROFIL['magasin'] ;
- gabarit OWL static/src/xml/dashboard.xml : titre et sous-titre :30-31 ;
  filtres « Période », « Appliquer », « Emplacement », « Tous »,
  « Catégorie », « Toutes » :38-70 ; cartes du Tableau de bord :97-131 ;
  « Valorisation & flux » et titres des graphiques :133-140 ; onglet
  Alertes : section et cartes :159-175, « Références à traiter (triées par
  urgence) » :179, colonnes :188-194, « — » :207, note :218-219 ; le bouton
  « ⚙ Configurer les alertes » :180-182 n'est rendu que pour un responsable
  (is_manager), il n'apparaît donc pas chez le magasinier ; onglet Stock
  complet :225-264, note « Bonne pratique » :293-295, recherche « 🔍
  Rechercher un produit… » :247 (la loupe est redessinée en SVG) ; onglet
  Rotation :301-342 ; onglet Inventaires & écarts :369-407, note :426-430 ;
- static/src/js/views/stock_dashboard_view.js : onglets :170-175 ; tri des
  alertes par urgence puis couverture :183-186 ; recherche insensible à la
  casse :192-199 ; barre de valeur rapportée à la plus forte ligne :214-222 ;
  coulAccent (carte rouge au-delà du seuil), coulSub, marginSub,
  listMarginSub, rotSub :330-360 ; badges :BADGE_CLS ; séries
  « Entrées (réceptions) » / « Sorties (ventes) » :458-464, « Valeur
  dormante » :594, « Coulage (% CA estimé) » / « Seuil » :648-656, axe du
  coulage « v + " %" » :675 ;
- static/src/js/services/utils.js : formats fmtMoney, fmtCompact, fmtQty,
  fmtPct, fmtDays :35-73 (rejoués à l'identique ci-dessous) ; périodes
  :75-103 ;
- models/stock_dashboard.py : calcul par référence _metrics :47-103 (point de
  commande, quantité suggérée, statuts Rupture / Critique / Sous seuil / OK,
  classes Rapide / Normale / Lente / Dormant) ; réglages par défaut :130-139
  et models/res_config_settings.py:20-48 (sécurité 2 j, horizon 7 j,
  critique 3 j, dormant 60 j, délai 3 j, coulage 2 %) ; ventes moyennes sur
  30 jours glissants :28-33 et :147 ; agrégats get_kpis :301-352 ; nom
  d'emplacement = dernier segment :283 ; tri du Stock complet :363 ; journal
  des écarts trié par valeur signée :459, date ISO :656 ; types « Ajustement
  inv. » et « Casse / rebut » :670, :675 ; référence d'un rebut « SP/00007 » :
  odoo18/addons/stock/models/res_company.py:102-112 (préfixe SP/, 5
  chiffres) ; symbole « FCFA » de la devise XAF :
  odoo18/odoo/addons/base/data/res_currency_data.xml:476-483.

Les chiffres de l'écran sont calculés : les statuts, points de commande,
quantités à commander, couvertures et classes de rotation sortent du VRAI
code de _metrics, extrait de addons/ à l'import (comme tests/socle/
test_stock_logic.py), appliqué à un jeu fictif de 24 références d'un bar et
d'une cave, avec les réglages par défaut ; les cartes reprennent les
agrégats de get_kpis et les formats de utils.js. Deux emplacements internes
fictifs, WH/Bar et WH/Cave, s'affichent « Bar » et « Cave ». Aujourd'hui :
16/10/2026.

Sources des affirmations : douleurs — docs/guides/
AITE_HOUSE_plaquette_commerciale.pdf p. 12 (« Une rupture de bière un samedi
soir, c'est du CA perdu chaque heure », « la marge qui dort en cave », « vous
savez où est chaque casier »), dashboard.xml:427-429 (« offert non tracé »,
« ajuster pour que ça tombe juste »), __manifest__.py:13 (« piloter le stock
au lieu de le subir ») ; bénéfices et résultats — _metrics, get_kpis,
res_config_settings.py, stock_dashboard_view.js:170-175 (6 onglets).

Captures de référence (modèle visuel, jamais incrustées) :
../aite-videos/ref_muk/012-inventaire-tableau-de-bord-aite.png et
-pleine.png ; docs/captures_uat/r6-magasin-01-ouvrir-le-tableau-de-bord-stock.png.
Chapitre déjà rejoué dans la présentation : scenarios/c5_magasin.py.

Écarts rejoués tels quels (voir le rapport) : « Ce mois » démarre la veille
du 1er à Douala (utils.js:84,100, toISOString en UTC) d'où « 30/09/2026 » ;
dates ISO du journal (stock_dashboard.py:656) ; « 2 rupture » sans pluriel
(dashboard.xml:110) ; carte « Critiques » ambre et badge « Critique » rouge
(dashboard.xml:165, stock_dashboard.py:82) ; graduations « 0.5 % » à point
décimal (stock_dashboard_view.js:675) ; libellé « Pertes (écarts − + casse) »
(dashboard.xml:376).
"""

import math
import os
import re
import textwrap

import demo
from ecrans import APPS_PROFIL, ICONES, e, fenetre_muk, graphe_anneau, navigateur, tdb_entete, vue_tdb
from marketing import bulle, dezoom, reaction, zoom
from moteur import anneau, cacher, clic, compter, defiler, pause, saisir, texte, vue

NOM, ROLE = demo.POSTES['magasin']
ICI = os.path.dirname(os.path.abspath(__file__))
MODULE = os.path.join(ICI, '..', '..', '..', 'addons', 'aite_stock_dashboard', 'models', 'stock_dashboard.py')


# ------------------------------------------------------ le vrai calcul --

def _metrics_du_module():
    """Le code réel de ``AiteStockDashboard._metrics``, extrait du module."""
    with open(MODULE, encoding='utf-8') as f:
        src = f.read()
    m = re.search(r'^    def _metrics\(.*?(?=^    # -{10,}|^    def )', src, re.S | re.M)
    ns = {}
    exec(compile(textwrap.dedent(m.group(0)), MODULE, 'exec'), ns)
    return ns['_metrics']


METRICS = _metrics_du_module()
# Réglages par défaut de la société (res_config_settings.py:20-48).
SEC, HOR, CRIT, DORM, DELAI, SEUIL_COUL = 2, 7, 3, 60, 3, 2.0

# Le bar et la cave du Complexe Hôtelier — Démo (fictif) :
# (article, catégorie, coût, prix de vente, au bar, en cave, vendus sur 30 jours)
ARTICLES = [
    ('Bière blonde 65 cl', 'Bières', 650, 1500, 12, 18, 420),
    ('Bière brune 65 cl', 'Bières', 700, 1500, 24, 66, 240),
    ('Bière blonde 33 cl', 'Bières', 400, 1000, 0, 0, 270),
    ('Bière sans alcool 33 cl', 'Bières', 450, 1000, 12, 12, 30),
    ('Eau minérale 1,5 L', 'Eaux', 300, 1000, 0, 0, 360),
    ('Eau minérale 50 cl', 'Eaux', 150, 500, 36, 84, 300),
    ('Eau gazeuse 1 L', 'Eaux', 500, 1500, 12, 30, 120),
    ("Jus d'ananas 1 L", 'Jus & softs', 900, 2000, 6, 12, 120),
    ('Soda orange 33 cl', 'Jus & softs', 300, 1000, 10, 24, 210),
    ('Cola 33 cl', 'Jus & softs', 300, 1000, 24, 72, 270),
    ('Tonic 33 cl', 'Jus & softs', 350, 1000, 12, 36, 60),
    ('Jus de bissap 50 cl', 'Jus & softs', 400, 1000, 10, 20, 90),
    ('Arachides grillées', 'Snacks & confiseries', 250, 700, 10, 15, 180),
    ('Chips de plantain', 'Snacks & confiseries', 300, 800, 15, 25, 90),
    ('Chocolat noir 100 g', 'Snacks & confiseries', 900, 2000, 6, 24, 6),
    ('Vin rouge 75 cl', 'Vins & spiritueux', 4500, 12000, 4, 36, 60),
    ('Vin blanc 75 cl', 'Vins & spiritueux', 4000, 11000, 4, 20, 45),
    ('Vin rosé 75 cl', 'Vins & spiritueux', 4000, 11000, 2, 28, 12),
    ('Champagne brut 75 cl', 'Vins & spiritueux', 22000, 45000, 2, 10, 3),
    ('Whisky 12 ans 70 cl', 'Vins & spiritueux', 18000, 40000, 2, 6, 15),
    ('Cognac VSOP 70 cl', 'Vins & spiritueux', 28000, 60000, 1, 5, 0),
    ('Rhum ambré 70 cl', 'Vins & spiritueux', 9000, 20000, 2, 8, 9),
    ('Gin 70 cl', 'Vins & spiritueux', 10000, 22000, 2, 4, 12),
    ('Liqueur de café 70 cl', 'Vins & spiritueux', 8000, 18000, 1, 8, 3),
]


def _lignes():
    """_build_rows : une ligne par référence suivie, triée comme get_stock_list."""
    rows = []
    for nom, cat, cout, prix, bar, cave, v30 in ARTICLES:
        stock, vday = float(bar + cave), v30 / 30.0
        if stock <= 0 and vday <= 0:
            continue
        m = METRICS(stock, vday, DELAI, float(cout), SEC, HOR, CRIT, DORM, 0.0, True)
        rows.append(dict(nom=nom, cat=cat, cout=cout, prix=prix, bar=bar, cave=cave, stock=stock, vday=vday,
                         vente=stock * prix, **m))
    rows.sort(key=lambda r: (r['cat'], -r['value']))
    return rows


LIGNES = _lignes()
PAR_NOM = {r['nom']: r for r in LIGNES}


# --------------------------------------------- les formats de utils.js --

def _milliers(n):
    s = '{:,}'.format(abs(n)).replace(',', ' ')
    return ('-' if n < 0 else '') + s


def _arrondi(v):
    return int(math.floor(v + 0.5)) if v >= 0 else -int(math.floor(-v + 0.5))


def money(v):
    return _milliers(_arrondi(v)) + ' FCFA'


def signe_money(v):
    return ('+' if v > 0 else '') + money(v)


def _dixieme(v):
    r = int(v * 10 + (0.5 if v >= 0 else -0.5)) / 10.0
    return ('%.1f' % r).rstrip('0').rstrip('.')


def qty(v):
    s = _dixieme(v)
    entier, _, dec = s.partition('.')
    return _milliers(int(entier)) + (',' + dec if dec else '') if abs(v) >= 1000 else s.replace('.', ',')


def signe_qty(v):
    return ('+' if v > 0 else '') + qty(v)


def days(v):
    return '∞' if v >= 365 else _dixieme(v).replace('.', ',') + ' j'


def rotx(v):
    return _dixieme(v).replace('.', ',') + '×'


def pct(v):
    return _dixieme(v).replace('.', ',') + ' %'


# ------------------------------------------------------- les agrégats --

TOT_VAL = sum(r['value'] for r in LIGNES)
TOT_VENTE = sum(r['vente'] for r in LIGNES)
MARGE = TOT_VENTE - TOT_VAL
UNITES = sum(r['stock'] for r in LIGNES)
VDAY = sum(r['vday'] for r in LIGNES)
RUPT = [r for r in LIGNES if r['status'] == 'Rupture']
CRITQ = [r for r in LIGNES if r['status'] == 'Critique']
SOUS = [r for r in LIGNES if r['status'] == 'Sous seuil']
DORMANTS = sorted([r for r in LIGNES if r['classe'] == 'Dormant'], key=lambda r: -r['value'])
VAL_CMD = sum(r['cmd'] * r['cout'] for r in LIGNES)
VAL_DORM = sum(r['value'] for r in DORMANTS)

# La période « Ce mois », vue d'un poste à Douala le 16/10/2026 : periodRange
# convertit le 1er octobre à minuit local en UTC (toISOString), d'où le 30/09.
DU, AU, JOURS = '30/09/2026', '16/10/2026', 17
CA_EST = sum(r['vday'] * JOURS * r['prix'] for r in LIGNES)        # sorties clients × prix de vente
SORTIES = sum(r['vday'] * JOURS * r['cout'] for r in LIGNES)       # valorisées au coût (CMV)
# Le journal des écarts et casses de la période : (date ISO, type, article, quantité signée, référence).
ECARTS = [
    ('2026-10-14', 'Casse / rebut', 'Champagne brut 75 cl', -2, 'SP/00007'),
    ('2026-10-09', 'Ajustement inv.', 'Whisky 12 ans 70 cl', -1, 'Offert non tracé'),
    ('2026-10-12', 'Ajustement inv.', 'Bière blonde 65 cl', -7, 'Erreur de saisie'),
    ('2026-10-05', 'Casse / rebut', 'Vin rouge 75 cl', -1, 'SP/00006'),
    ('2026-10-12', 'Ajustement inv.', 'Arachides grillées', -4, 'Périmé'),
    ('2026-10-12', 'Ajustement inv.', 'Soda orange 33 cl', 2, 'Erreur de saisie'),
]
ECARTS = sorted(ECARTS, key=lambda g: g[3] * PAR_NOM[g[2]]['cout'])          # tri par valeur signée
PERTES = sum(-q * PAR_NOM[a]['cout'] for _, _, a, q, _ in ECARTS if q < 0)
ECART_NET = sum(q * PAR_NOM[a]['cout'] for _, _, a, q, _ in ECARTS)
COUL = PERTES / CA_EST * 100.0

assert (len(RUPT), len(CRITQ), len(SOUS), len(DORMANTS)) == (2, 1, 3, 5)
assert COUL > SEUIL_COUL      # la carte « Coulage » passe au rouge


# ----------------------------------------------- les écrans rejoués --

CAL = ('<svg class="t13-cal" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">'
       '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/></svg>')
ONGLETS = ['Tableau de bord', 'Alertes & réappro', 'Stock complet', 'Rotation & dormants', 'Inventaires & écarts',
           'Mouvements']
CATEGORIES = ['Bières', 'Eaux', 'Jus & softs', 'Snacks & confiseries', 'Vins & spiritueux']
LIEUX = [('Bar', '#714B67'), ('Cave', '#185FA5')]
BADGE = {'red': 'rouge', 'amber': 'ambre', 'teal': 'vert', 'blue': 'bleu', 'gray': 'gris'}


def _tete(v, actif):
    """Titre, filtres et onglets : la tête commune à chaque onglet."""
    periode = ''.join('<span class="chip%s">%s</span>' % (' actif' if p == 'Ce mois' else '', e(p))
                      for p in ["Aujourd'hui", 'Cette semaine', 'Ce mois', '3 mois'])
    dates = ('<span class="t13-date t13-esp">%s%s</span><span class="t13-fl">→</span><span class="t13-date">%s%s</span>'
             '<span class="chip">Appliquer</span>' % (e(DU), CAL, e(AU), CAL))
    lieux = ''.join('<span class="chip"><i class="t13-pt" style="background:%s"></i>%s</span>' % (c, e(n)) for n, c in LIEUX)
    cats = ''.join('<span class="chip">%s</span>' % e(c) for c in CATEGORIES)
    filtres = ('<div class="tdb-filtres"><div class="tdb-rang"><span class="tdb-lib">Période</span>%s%s</div>'
               '<div class="tdb-rang"><span class="tdb-lib">Emplacement</span><span class="chip actif">Tous</span>%s</div>'
               '<div class="tdb-rang"><span class="tdb-lib">Catégorie</span><span class="chip actif">Toutes</span>%s</div>'
               '</div>' % (periode, dates, lieux, cats))
    onglets = ''.join('<span class="t13-onglet%s" id="t13-tab-%s-%d">%s</span>' % (' actif' if i == actif else '', v, i, e(o))
                      for i, o in enumerate(ONGLETS))
    return (tdb_entete('Stock & Inventaire — Tableau de bord', 'Valorisation · alertes de réappro · rotation · écarts & coulage')
            + filtres + '<div class="t13-onglets">%s</div>' % onglets)


def _kpi(ident, lib, val, sous, accent=None):
    """Une carte KpiCard : seules les cartes « mega » portent un liseré coloré."""
    return ('<div class="kpi%s" id="%s"><div class="kpi-l">%s</div><div class="kpi-v" id="%s-v">%s</div>'
            '<div class="kpi-s" id="%s-s">%s</div></div>'
            % (' acc-' + accent if accent else '', ident, e(lib), ident, e(val), ident, e(sous)))


def _section(titre, cartes):
    return '<div class="tdb-sect">%s</div><div class="tdb-grille c4">%s</div>' % (e(titre), ''.join(cartes))


def _table(ident, colonnes, lignes, cache=''):
    """Une table du tableau de bord : ``colonnes`` (libellé, largeur, 'd'),
    ``lignes`` (identifiant, [cellules HTML]) ; ``cache`` : des lignes en plus,
    groupées (``<id>-autres``) pour les faire disparaître d'un coup."""
    gab = ' '.join(c[1] for c in colonnes)
    tete = '<div class="t13-th" style="grid-template-columns:%s">%s</div>' % (
        gab, ''.join('<span%s>%s</span>' % (' class="t13-d"' if len(c) > 2 else '', e(c[0])) for c in colonnes))

    def rangs(lot):
        return ''.join('<div class="t13-tr" id="%s" style="grid-template-columns:%s">%s</div>' % (i, gab, ''.join(cs))
                       for i, cs in lot)
    autres = '<div id="%s-autres">%s</div>' % (ident, rangs(cache)) if cache else ''
    return '<div class="t13-tab" id="%s">%s%s%s</div>' % (ident, tete, rangs(lignes), autres)


def _c(txt, d=False, cls=''):
    classes = ' '.join(x for x in ('t13-d' if d else '', cls) if x)
    return '<span%s>%s</span>' % (' class="%s"' % classes if classes else '', e(txt))


def _badge(txt, cls, ident=None):
    return '<span><span class="t13-badge %s"%s>%s</span></span>' % (BADGE[cls], ' id="%s"' % ident if ident else '', e(txt))


def _barre(valeur, maxi):
    return '<span class="t13-d t13-barre"><i style="width:%.1f%%"></i>%s</span>' % (100.0 * valeur / maxi, e(money(valeur)))


def _note(ident, html):
    return '<div class="t13-note" id="%s">%s</div>' % (ident, html)


def _carte(titre, corps, ident=None, droite=''):
    return ('<div class="t13-carte"%s><div class="t13-ct"><h3>%s</h3>%s</div>%s</div>'
            % (' id="%s"' % ident if ident else '', e(titre), droite, corps))


# -- graphiques (Chart.js rejoué : barres, courbe, anneau)

def _g(ident, titre, corps):
    return '<div class="t13-g" id="%s"><h3>%s</h3>%s</div>' % (ident, e(titre), corps)


def _barres_h(items, vmax, couleur, ticks):
    """Barres horizontales (indexAxis 'y') : ``items`` (libellé, valeur)."""
    rangs = ''.join('<div class="t13-hb"><span class="l">%s</span><span class="p"><i style="width:%.1f%%;background:%s">'
                    '</i></span></div>' % (e(lib), 100.0 * v / vmax, couleur) for lib, v in items)
    axe = ''.join('<span style="left:%.1f%%">%s</span>' % (100.0 * v / vmax, e(t)) for v, t in ticks)
    return '<div class="t13-hbs">%s<div class="t13-hax"><span></span><span class="p">%s</span></div></div>' % (rangs, axe)


def _barres_v(groupes, vmin, vmax, ticks, couleurs, legende=()):
    """Barres verticales, groupées ou signées : ``groupes`` (libellé, [valeurs])."""
    h = 168.0
    zero = h * vmax / (vmax - vmin)

    def barre(v, coul):
        haut = h * abs(v) / (vmax - vmin)
        top = zero - haut if v >= 0 else zero
        return '<i style="top:%.1fpx;height:%.1fpx;background:%s"></i>' % (top, haut, coul(v))
    cols = ''.join('<div class="t13-vg">%s</div>' % ''.join(barre(v, couleurs[k]) for k, v in enumerate(vals))
                   for _, vals in groupes)
    graduations = ''.join('<span style="top:%.1fpx">%s</span>' % (zero - h * v / (vmax - vmin), e(t)) for v, t in ticks)
    lignes = ''.join('<b style="top:%.1fpx"></b>' % (zero - h * v / (vmax - vmin)) for v, _ in ticks)
    labs = ''.join('<span>%s</span>' % e(lib) for lib, _ in groupes)
    leg = ''.join('<span><i style="background:%s"></i>%s</span>' % (c, e(l)) for l, c in legende)
    return ('<div class="t13-vz"><div class="t13-vy">%s</div><div class="t13-vp">%s<div class="t13-vb">%s</div></div>'
            '<div class="t13-vx">%s</div>%s</div>'
            % (graduations, lignes, cols, labs, '<div class="t13-leg">%s</div>' % leg if leg else ''))


def _courbe(mois, valeurs, seuil, ymax, ticks):
    """La courbe « Coulage mensuel vs seuil » : une série remplie, le seuil en pointillés."""
    w, h = 600.0, 150.0
    xs = [w * (i + 0.5) / len(mois) for i in range(len(mois))]
    ys = [h - h * v / ymax for v in valeurs]
    pts = ' '.join('%.1f,%.1f' % p for p in zip(xs, ys))
    aire = 'M%.1f,%.1f L%s L%.1f,%.1f Z' % (xs[0], h, ' L'.join('%.1f,%.1f' % p for p in zip(xs, ys)), xs[-1], h)
    ys_seuil = h - h * seuil / ymax
    grille = ''.join('<line x1="0" x2="%d" y1="%.1f" y2="%.1f" stroke="#E9ECEF"/>' % (w, h - h * v / ymax, h - h * v / ymax)
                     for v, _ in ticks)
    points = ''.join('<circle cx="%.1f" cy="%.1f" r="4" fill="#854F0B"/>' % p for p in zip(xs, ys))
    svg = ('<svg width="%d" height="%d" viewBox="0 0 %d %d">%s<path d="%s" fill="#854F0B" fill-opacity=".13"/>'
           '<polyline points="%s" fill="none" stroke="#854F0B" stroke-width="3"/>%s'
           '<line x1="0" x2="%d" y1="%.1f" y2="%.1f" stroke="#A32D2D" stroke-width="2.5" stroke-dasharray="9 6"/></svg>'
           % (w, h, w, h, grille, aire, pts, points, w, ys_seuil, ys_seuil))
    graduations = ''.join('<span style="top:%.1fpx">%s</span>' % (h - h * v / ymax, e(t)) for v, t in ticks)
    labs = ''.join('<span>%s</span>' % e(m) for m in mois)
    leg = ('<span><i style="background:#854F0B"></i>Coulage (% CA estimé)</span>'
           '<span><i class="t13-tiret"></i>Seuil</span>')
    return ('<div class="t13-cz"><div class="t13-vy">%s</div><div class="t13-cp">%s</div>'
            '<div class="t13-vx t13-cx">%s</div><div class="t13-leg">%s</div></div>' % (graduations, svg, labs, leg))


# -- l'onglet Tableau de bord

def _vue_tableau():
    sous_marge = 'marge potentielle +%s (%s du PV)' % (money(MARGE), pct(MARGE / TOT_VENTE * 100))
    cartes1 = [
        _kpi('t13-k-cout', "Valeur stock — coût d'achat", '0 FCFA',
             '%d références · %s unités' % (len(LIGNES), qty(UNITES)), 'bleu'),
        _kpi('t13-k-pv', 'Valeur stock — prix de vente', money(TOT_VENTE), sous_marge, 'vert'),
        _kpi('t13-k-rupt', 'Ruptures & critiques', '%d réfs' % (len(RUPT) + len(CRITQ)),
             '%d rupture · %d sous %d j' % (len(RUPT), len(CRITQ), CRIT), 'rouge'),
        _kpi('t13-k-coul', 'Coulage (période)', money(PERTES),
             '%s du CA estimé · seuil %s' % (pct(COUL), pct(SEUIL_COUL)), 'rouge' if COUL > SEUIL_COUL else 'vert'),
    ]
    cartes2 = [
        _kpi('t13-k-couv', 'Couverture moyenne', days(UNITES / VDAY), 'rotation moyenne %s / mois' % rotx(VDAY * 30 / UNITES)),
        _kpi('t13-k-dorm', 'Stock dormant', money(VAL_DORM), '%d réfs (+%d j de couverture)' % (len(DORMANTS), DORM)),
        _kpi('t13-k-seuil', 'Sous seuil de commande', '%d réfs' % len(SOUS), 'valeur à commander %s' % money(VAL_CMD)),
        _kpi('t13-k-ecart', "Écarts d'inventaire (période)", money(ECART_NET), '%d réfs concernées' % len(ECARTS)),
    ]
    par_cat = {}
    for r in LIGNES:
        par_cat[r['cat']] = par_cat.get(r['cat'], 0) + r['value']
    palette = ['#714B67', '#185FA5', '#3B6D11', '#854F0B', '#A32D2D']
    parts = [(c, v, palette[i]) for i, (c, v) in enumerate(sorted(par_cat.items(), key=lambda kv: -kv[1]))]
    # entrées (réceptions) et sorties (ventes) au coût, de mai à octobre (au 16)
    flux = [('Mai', [2410000, 2290000]), ('Juin', [2050000, 2220000]), ('Juil', [2480000, 2300000]),
            ('Août', [2120000, 2260000]), ('Sep', [2330000, 2210000]), ('Oct', [980000, 1190000])]
    graphes = ('<div class="tdb-grille c2">%s%s</div>' % (
        graphe_anneau('t13-g-cat', 'Valeur du stock par catégorie', parts),
        _g('t13-g-flux', 'Entrées vs Sorties — 6 mois (au coût)',
           _barres_v(flux, 0, 2500000, [(0, '0'), (500000, '500 k'), (1000000, '1,0 M'), (1500000, '1,5 M'),
                                        (2000000, '2,0 M'), (2500000, '2,5 M')],
                     [lambda v: '#3B6D11', lambda v: '#714B67'],
                     [('Entrées (réceptions)', '#3B6D11'), ('Sorties (ventes)', '#714B67')]))))
    contenu = (_tete('dash', 0) + _section("Vue d'ensemble", cartes1) + _section('Indicateurs', cartes2)
               + '<div class="tdb-sect">Valorisation &amp; flux</div>' + graphes)
    return vue_tdb('t13-dash', '<div class="t13" id="t13-in-dash">%s</div>' % contenu, initiale=True)


# -- l'onglet Alertes & réappro

COLS_AL = [('Produit', '1fr'), ('Catégorie', '230px'), ('Stock', '80px', 'd'), ('Ventes/j', '100px', 'd'),
           ('Couverture', '120px', 'd'), ('Point de cmde', '140px', 'd'), ('À commander', '140px', 'd'),
           ('Statut', '130px')]
ALERTES = sorted(LIGNES, key=lambda r: (r['urgency'], r['couv']))


def _ligne_alerte(n, r):
    ident = 't13-al-r%d' % n
    return (ident, [_c(r['nom'], cls='t13-b'), _c(r['cat'], cls='t13-mu'), _c(qty(r['stock']), True),
                    _c(qty(r['vday']), True), _c(days(r['couv']), True), _c(qty(r['seuil']), True),
                    '<span class="t13-d t13-b" id="%s-cmd">%s</span>' % (ident, e(qty(r['cmd']) if r['cmd'] else '—')),
                    _badge(r['status'], r['status_cls'], ident + '-st')])


def _vue_alertes():
    cartes = [
        _kpi('t13-a-rupt', 'En rupture', str(len(RUPT)), 'références à zéro', 'rouge'),
        _kpi('t13-a-crit', 'Critiques', str(len(CRITQ)), 'couverture sous %d jours' % CRIT, 'ambre'),
        _kpi('t13-a-seuil', 'Sous seuil de commande', '%d réfs' % len(SOUS), 'point de commande atteint'),
        _kpi('t13-a-cmd', 'Valeur à commander', money(VAL_CMD), 'suggestion de réappro'),
    ]
    table = _table('t13-al', COLS_AL, [_ligne_alerte(n, r) for n, r in enumerate(ALERTES[:10], 1)])
    note = _note('t13-al-note', '<b>Point de commande</b> = ventes moy./jour × (délai réappro + <b>%d</b> j de sécurité). '
                 'Quantité suggérée : <b>%d</b> jours de couverture après livraison — à arrondir au casier.' % (SEC, HOR))
    contenu = (_tete('al', 1) + _section('Alertes de réapprovisionnement', cartes)
               + _carte('Références à traiter (triées par urgence)', '<div class="t13-wrap">%s</div>' % table) + note)
    return vue_tdb('t13-alertes', '<div class="t13" id="t13-in-al">%s</div>' % contenu)


# -- l'onglet Stock complet

COLS_ST = [('Produit', '1fr'), ('Catégorie', '200px'), ('Bar', '62px', 'd'), ('Cave', '66px', 'd'),
           ('Total', '66px', 'd'), ('Coût unit.', '124px', 'd'), ('Valeur', '170px', 'd'), ('Ventes/j', '96px', 'd'),
           ('Couverture', '116px', 'd'), ('Statut', '116px')]
MAXI = max(r['value'] for r in LIGNES)
BIERES = [r for r in LIGNES if 'bière' in r['nom'].lower()]


def _ligne_stock(n, r):
    ident = 't13-st-r%d' % n
    return (ident, [_c(r['nom'], cls='t13-b'), _c(r['cat'], cls='t13-mu'),
                    '<span class="t13-d" id="%s-bar">%s</span>' % (ident, qty(r['bar'])),
                    '<span class="t13-d" id="%s-cave">%s</span>' % (ident, qty(r['cave'])),
                    _c(qty(r['stock']), True, 't13-b'), _c(money(r['cout']), True, 't13-mu'), _barre(r['value'], MAXI),
                    _c(qty(r['vday']), True), _c(days(r['couv']), True), _badge(r['status'], r['status_cls'])])


def _totaux(rows):
    vente = sum(r['vente'] for r in rows)
    val = sum(r['value'] for r in rows)
    return {'ref': str(len(rows)), 'un': qty(sum(r['stock'] for r in rows)), 'val': money(val), 'pv': money(vente),
            'pv-s': 'marge potentielle +%s (%s)' % (money(vente - val), pct((vente - val) / vente * 100))}


TOUT, FILTRE = _totaux(LIGNES), _totaux(BIERES)


def _vue_stock():
    cartes = [
        _kpi('t13-s-ref', 'Références', TOUT['ref'], 'affichées (filtres appliqués)', 'bleu'),
        _kpi('t13-s-un', 'Unités en stock', TOUT['un'], 'tous emplacements filtrés'),
        _kpi('t13-s-val', "Valeur — coût d'achat", TOUT['val'], 'trésorerie immobilisée', 'violet'),
        _kpi('t13-s-pv', 'Valeur — prix de vente', TOUT['pv'], TOUT['pv-s'], 'vert'),
    ]
    bieres = [_ligne_stock(n, r) for n, r in enumerate(BIERES, 1)]
    autres = [_ligne_stock(n, r) for n, r in enumerate([r for r in LIGNES if r not in BIERES][:6], len(BIERES) + 1)]
    recherche = ('<div class="entree t13-search" id="t13-rech"><span class="ph" id="t13-rech-ph">%s'
                 'Rechercher un produit…</span><span class="val" id="t13-rech-val"></span></div>' % ICONES['loupe'])
    note = _note('t13-st-note', "<b>Bonne pratique :</b> base de l'<b>inventaire tournant</b> — filtrez une catégorie, "
                 "comptez, puis saisissez les écarts avec un motif dans Odoo (ajustement d'inventaire).")
    contenu = (_tete('st', 2) + _section('Inventaire complet — toutes les références', cartes)
               + _carte('Stock par référence', '<div class="t13-wrap">%s</div>' % _table('t13-st', COLS_ST, bieres, autres),
                        droite=recherche) + note)
    return vue_tdb('t13-stock', '<div class="t13" id="t13-in-st">%s</div>' % contenu)


# -- l'onglet Rotation & dormants

COLS_ROT = [('Produit', '1fr'), ('Catégorie', '230px'), ('Stock', '90px', 'd'), ('Sorties 30 j', '130px', 'd'),
            ('Rotation', '110px', 'd'), ('Couverture', '120px', 'd'), ('Valeur', '180px', 'd'), ('Classe', '120px')]


def _vue_rotation():
    sorties = money(SORTIES)
    cartes = [
        _kpi('t13-r-rot', 'Rotation moyenne', rotx(VDAY * 30 / UNITES), 'renouvellements / mois', 'violet'),
        _kpi('t13-r-dorm', 'Stock dormant', '0 FCFA', '%d réfs (+%d j)' % (len(DORMANTS), DORM), 'rouge'),
        _kpi('t13-r-ref', 'Références suivies', str(len(LIGNES)), 'stock ou ventes sur 30 j'),
        _kpi('t13-r-sort', 'Sorties (période)', sorties, 'valorisées au coût (CMV)'),
    ]
    top = sorted([r for r in LIGNES if r['rot'] > 0], key=lambda r: -r['rot'])[:8]
    g_rot = _g('t13-g-rot', 'Top 8 — rotation la plus rapide',
               _barres_h([(r['nom'], r['rot']) for r in top], 16, '#0F6E56',
                         [(v, str(v)) for v in range(0, 17, 2)]))
    g_dorm = _g('t13-g-dorm', 'Dormants — valeur immobilisée',
                _barres_h([(r['nom'], r['value']) for r in DORMANTS[:8]], 300000, '#A32D2D',
                          [(v, '0' if v == 0 else '%d k' % (v // 1000)) for v in range(0, 300001, 50000)]))
    rot = sorted(LIGNES, key=lambda r: -r['rot'])[:6]
    table = _table('t13-rt', COLS_ROT, [
        ('t13-rt-r%d' % n, [_c(r['nom'], cls='t13-b'), _c(r['cat'], cls='t13-mu'), _c(qty(r['stock']), True),
                            _c(qty(r['vday'] * 30), True), _c(rotx(r['rot']), True, 't13-b'), _c(days(r['couv']), True),
                            _barre(r['value'], MAXI), _badge(r['classe'], r['classe_cls'])])
        for n, r in enumerate(rot, 1)])
    contenu = (_tete('rot', 3) + _section('Rotation des stocks', cartes)
               + '<div class="tdb-grille c2 t13-gg">%s%s</div>' % (g_rot, g_dorm)
               + _carte('Rotation par référence', table))
    return vue_tdb('t13-rotation', '<div class="t13" id="t13-in-rot">%s</div>' % contenu)


# -- l'onglet Inventaires & écarts

COLS_EC = [('Date', '140px'), ('Type', '180px'), ('Produit', '1fr'), ('Qté ±', '100px', 'd'), ('Valeur ±', '170px', 'd'),
           ('Référence', '240px')]


def _vue_ecarts():
    cartes = [
        _kpi('t13-e-net', 'Écart net (période)', money(ECART_NET), '%d réfs concernées' % len(ECARTS), 'ambre'),
        _kpi('t13-e-pertes', 'Pertes (écarts − + casse)', money(PERTES),
             '%s du CA estimé · seuil %s' % (pct(COUL), pct(SEUIL_COUL)), 'rouge' if COUL > SEUIL_COUL else 'vert'),
        _kpi('t13-e-ca', 'CA estimé (période)', money(CA_EST), 'sorties clients × prix de vente'),
        _kpi('t13-e-seuil', 'Seuil de coulage', pct(SEUIL_COUL), 'paramétrable dans les Réglages'),
    ]
    par_cat = {}
    for _, _, a, q, _ in ECARTS:
        par_cat[PAR_NOM[a]['cat']] = par_cat.get(PAR_NOM[a]['cat'], 0) + q * PAR_NOM[a]['cout']
    cats = sorted(par_cat.items(), key=lambda kv: kv[1])
    g_ecart = _g('t13-g-ecart', 'Écarts valorisés par catégorie',
                 _barres_v([(c, [v]) for c, v in cats], -70000, 10000,
                           [(v, '0' if v == 0 else '%d k' % (v // 1000)) for v in range(-70000, 10001, 10000)],
                           [lambda v: '#A32D2D' if v < 0 else '#3B6D11']))
    g_coul = _g('t13-g-coul', 'Coulage mensuel vs seuil (6 mois)',
                _courbe(['Mai', 'Juin', 'Juil', 'Août', 'Sep', 'Oct'], [1.2, 0.9, 1.6, 1.1, 1.4, round(COUL, 1)],
                        SEUIL_COUL, 3.0, [(x / 2.0, ('%g' % (x / 2.0)) + ' %') for x in range(0, 7)]))
    lignes = []
    for n, (date, typ, art, q, ref) in enumerate(ECARTS, 1):
        valeur = q * PAR_NOM[art]['cout']
        sens = 't13-neg' if q < 0 else 't13-pos'
        lignes.append(('t13-j-r%d' % n, [_c(date, cls='t13-mu'), _badge(typ, 'red' if typ.startswith('Casse') else 'amber'),
                                         _c(art, cls='t13-b'), _c(signe_qty(q), True, sens),
                                         _c(signe_money(valeur), True, sens + ' t13-b'), _c(ref, cls='t13-mu')]))
    note = _note('t13-j-note', '<b>Bonne pratique :</b> chaque ajustement doit porter un <b>motif</b> (vol, casse, offert '
                 'non tracé, périmé, erreur de saisie) — jamais « ajuster pour que ça tombe juste ». Inventaire complet '
                 'mensuel, comptages tournants hebdomadaires sur les fortes rotations.')
    contenu = (_tete('ec', 4) + _section("Écarts d'inventaire & coulage (période)", cartes)
               + '<div class="tdb-grille c2 t13-gg">%s%s</div>' % (g_ecart, g_coul)
               + _carte('Journal des écarts & casses', _table('t13-j', COLS_EC, lignes)) + note)
    return vue_tdb('t13-ecarts', '<div class="t13" id="t13-in-ec">%s</div>' % contenu)


ECRAN = navigateur(fenetre_muk('app-t13', 'Inventaire', ["Vue d'ensemble", 'Opérations', 'Tableau de bord AITE', 'Produits'],
                               [_vue_tableau(), _vue_alertes(), _vue_stock(), _vue_rotation(), _vue_ecarts()],
                               actif='Tableau de bord AITE', societe=demo.SOCIETE, initiale=NOM[0], avatar='#0F6E56',
                               apps=APPS_PROFIL['magasin'], app_active='Inventaire'))

CSS = """
.t13 .tdb-tete { padding: 13px 22px; }
.t13 .tdb-titre { font-size: 26px; }
.t13 .tdb-filtres { padding: 6px 22px; }
.t13 .tdb-rang { height: 48px; }
.t13 .tdb-lib { width: 160px; flex: none; }
.t13 .tdb-sect { margin: 14px 2px 8px; }
.t13 .kpi { min-height: 0; padding: 13px 18px 12px; }
.t13 .kpi-l { font-size: 14px; }
.t13 .kpi-v { margin-top: 6px; font-size: 32px; color: #212529; }
.t13 .kpi-s { white-space: normal; overflow: visible; line-height: 1.3; }
.t13-pt { display: inline-block; width: 11px; height: 11px; border-radius: 50%; margin-right: 8px; }
.t13-date { height: 38px; padding: 0 12px; border: 1px solid #DEE2E6; border-radius: 8px; display: inline-flex; align-items: center;
  gap: 14px; font-size: 17px; color: #212529; }
.t13-esp { margin-left: auto; }
.t13-cal { width: 17px; height: 17px; color: #495057; }
.t13-fl { font-size: 18px; color: #6C757D; }
.t13-onglets { margin-top: 12px; background: #fff; border-radius: 12px; padding: 7px 10px; display: flex; gap: 6px; }
.t13-onglet { height: 40px; padding: 0 18px; border-radius: 8px; display: inline-flex; align-items: center; font-size: 17px;
  color: #5F5E5A; white-space: nowrap; }
.t13-onglet.actif { background: #714B67; color: #fff; }
.t13-carte { margin-top: 14px; background: #fff; border-radius: 12px; padding: 14px 18px 12px; }
.t13-ct { display: flex; align-items: center; justify-content: space-between; height: 44px; margin-bottom: 8px; }
.t13-carte h3, .t13-g h3 { font-size: 19px; font-weight: 600; color: #2B2A28; white-space: nowrap; }
.t13-wrap { height: 480px; overflow: hidden; }
.t13-th, .t13-tr { display: grid; align-items: center; column-gap: 12px; padding: 0 12px; }
.t13-th { height: 40px; background: #F5F5F4; font-size: 13px; font-weight: 700; letter-spacing: .05em; text-transform: uppercase;
  color: #5F5E5A; white-space: nowrap; }
.t13-tr { height: 44px; border-bottom: 1px solid #EEF0F2; font-size: 17px; color: #212529; white-space: nowrap; }
.t13-d { text-align: right; font-variant-numeric: tabular-nums; }
.t13-b { font-weight: 700; }
.t13-mu { color: #6C757D; }
.t13-neg { color: #C82333; }
.t13-pos { color: #1E7B34; }
.t13-badge { display: inline-flex; align-items: center; height: 26px; padding: 0 9px; border-radius: 6px; font-size: 14px; font-weight: 700; }
.t13-badge.rouge { background: #C82333; color: #fff; }
.t13-badge.ambre { background: #F0AD00; color: #2B1D00; }
.t13-badge.vert { background: #1E7B34; color: #fff; }
.t13-badge.bleu { background: #0E7490; color: #fff; }
.t13-badge.gris { background: #E9ECEF; color: #212529; }
.t13-barre { position: relative; }
.t13-barre i { position: absolute; left: 0; top: -6px; bottom: -6px; border-radius: 4px; background: rgba(113,75,103,.14); }
.t13-note { margin-top: 12px; background: #FAF6E9; border: 1px solid #E8DFB8; border-radius: 10px; padding: 11px 16px; font-size: 17px;
  color: #6B5D20; line-height: 1.45; }
.entree.t13-search { margin-top: 0; width: 340px; height: 42px; border: 1px solid #DEE2E6; border-radius: 8px; font-size: 17px; }
.entree.t13-search .ph { left: 12px; display: inline-flex; align-items: center; gap: 8px; }
.entree.t13-search .ph svg { width: 18px; height: 18px; }
.entree.t13-search .val { left: 12px; }
.t13-gg { margin-top: 14px; }
.t13-g { position: relative; background: #fff; border-radius: 12px; padding: 14px 18px; height: 300px; }
.t13-hbs { position: absolute; left: 18px; right: 22px; top: 54px; bottom: 12px; display: flex; flex-direction: column; }
.t13-hb { flex: 1; display: grid; grid-template-columns: 210px 1fr; column-gap: 10px; align-items: center; }
.t13-hb .l { font-size: 14px; color: #495057; text-align: right; white-space: nowrap; }
.t13-hb .p { position: relative; height: 100%; border-left: 1px solid #CED4DA; }
.t13-hb .p i { position: absolute; left: 0; top: 18%; bottom: 18%; border-radius: 0 3px 3px 0; }
.t13-hax { height: 22px; display: grid; grid-template-columns: 210px 1fr; column-gap: 10px; }
.t13-hax .p { position: relative; }
.t13-hax .p span { position: absolute; top: 3px; transform: translateX(-50%); font-size: 13px; color: #6C757D; white-space: nowrap; }
.t13-vz, .t13-cz { position: absolute; left: 18px; right: 18px; top: 52px; bottom: 10px; }
.t13-vy { position: absolute; left: 0; top: 0; width: 56px; height: 168px; }
.t13-vy span { position: absolute; right: 6px; transform: translateY(-50%); font-size: 13px; color: #6C757D; white-space: nowrap; }
.t13-vp { position: absolute; left: 60px; right: 0; top: 0; height: 168px; }
.t13-vp b { position: absolute; left: 0; right: 0; height: 1px; background: #E9ECEF; }
.t13-vb { position: absolute; inset: 0; display: flex; justify-content: space-around; }
.t13-vg { position: relative; width: 70px; display: flex; gap: 6px; }
.t13-vg i { position: relative; flex: 1; border-radius: 3px; }
.t13-vx { position: absolute; left: 60px; right: 0; top: 174px; display: flex; justify-content: space-around; font-size: 13px;
  color: #495057; white-space: nowrap; }
.t13-vx span { width: 0; display: flex; justify-content: center; }
.t13-leg { position: absolute; left: 60px; right: 0; top: 204px; display: flex; justify-content: center; gap: 26px; font-size: 14px;
  color: #495057; }
.t13-leg span { display: inline-flex; align-items: center; gap: 8px; }
.t13-leg i { width: 26px; height: 11px; display: inline-block; }
.t13-leg i.t13-tiret { height: 0; border-top: 3px dashed #A32D2D; }
.t13-cp { position: absolute; left: 60px; top: 9px; }
.t13-cz .t13-vy { top: 9px; height: 150px; }
.t13-cx { top: 168px; left: 60px; width: 600px; right: auto; }
.t13-cz .t13-leg { top: 198px; width: 600px; right: auto; }
"""

TUTORIEL = {
    'slug': 't13-stock',
    'profil': 't13_stock',
    'numero': 13,
    'titre': 'Stock bar & cave : rien ne dort, rien ne fuit',
    'fonction': 'Stock bar & cave',
    'personnage': (NOM, ROLE),
    'accroche': {
        'kicker': 'Stock bar & cave',
        'question': 'Combien *dort* en cave, combien *fuit* au bar ?',
        'douleurs': [('alerte', 'Rupture de bière un samedi soir'), ('pieces', "L'argent qui dort en cave"),
                     ('interrogation', "La casse et l'offert jamais notés"),
                     ('calculatrice', '« Ajuster pour que ça tombe juste »'),
                     ('boite', 'Cave, bar : où est chaque casier ?'), ('sablier', "Le stock subi au lieu d'être piloté")],
        'voix': "Combien dort en cave, combien fuit au bar ? Une bière en rupture un samedi soir, c'est du chiffre "
                "perdu chaque heure.",
    },
    'revelation': {
        'promesse': "Chaque référence classée de la rupture à l'OK, la commande calculée sur vos ventes, le coulage "
                    "face à son seuil.",
        'voix': "Avec Aïte haousse, chaque référence est classée par urgence, et la commande se calcule sur vos ventes.",
    },
    'temps': ['Voir', 'Commander', 'Contrôler'],
    'app': 'app-t13',
    'ecran': ECRAN,
    'vues_initiales': {'odoo': 't13-dash'},
    'css': CSS,
    'bulles': {
        'b-marge': "Valorisé deux fois : au coût d'achat et au prix de vente.",
        'b-urgence': "Trié par urgence : la rupture d'abord, l'OK en dernier.",
        'b-calcul': 'Calculé sur les ventes des 30 derniers jours : rien à saisir.',
        'b-dormant': 'Dormant : 60 jours de couverture ou plus.',
        'b-coulage': 'Pertes au-dessus du seuil de 2 % : la carte passe au rouge.',
    },
    'reactions': {
        'r-cmd': "La commande est chiffrée : il ne reste qu'à la passer.",
        'r-fin': "Le coulage du mois se voit d'un coup d'œil.",
    },
    'etapes': [
        {'temps': 0, 'titre': 'La photo du stock',
         'texte': "Valeur au coût et au prix de vente, ruptures, coulage : tout sur un écran.",
         'voix': "Serge, le magasinier, ouvre le tableau de bord Stock et Inventaire. Le stock y est valorisé deux fois, "
                 "au coût d'achat et au prix de vente : la marge qui dort en réserve se lit d'un coup d'œil. À côté, "
                 "les ruptures et le coulage du mois.",
         'gestes': [compter('#t13-k-cout-v', 0, TOT_VAL, d=1.2, apres=' FCFA'),
                    anneau('#app-t13 .o-haut .menu.actif', d=1.1, avec=True),
                    zoom('#t13-k-pv', s=1.6, d=0.8), bulle('b-marge', '#t13-k-pv', cote='bas', d=3.0), pause(2.6),
                    dezoom(d=0.6), anneau('#t13-k-rupt', d=1.3), anneau('#t13-k-coul', d=1.6)]},
        {'temps': 1, 'titre': "Les alertes, par ordre d'urgence",
         'texte': 'Rupture, critique, sous seuil, puis OK : la liste se trie seule.',
         'voix': "Dans Alertes et réappro, chaque référence reçoit un statut, calculé tout seul. La liste se trie par "
                 "urgence : les ruptures d'abord, puis les critiques, puis ce qui passe sous le point de commande.",
         'gestes': [clic('#t13-tab-dash-1'), vue('t13-alertes'), pause(0.3), anneau('#t13-a-rupt', d=0.9),
                    anneau('#t13-a-crit', d=0.9), defiler('#t13-in-al', -330, d=0.9),
                    anneau('#t13-al-r1-st', d=0.8), anneau('#t13-al-r3-st', d=0.8), anneau('#t13-al-r4-st', d=0.8),
                    bulle('b-urgence', '#t13-al-r6-st', cote='bas', d=2.8), pause(2.6)]},
        {'temps': 1, 'titre': 'Combien commander',
         'texte': 'Point de commande et quantité suggérée, calculés sur les ventes réelles.',
         'voix': "Le point de commande et la quantité à commander se calculent sur les ventes des trente derniers jours "
                 "et le délai de livraison. Pour la bière blonde en soixante-cinq centilitres : cent dix à commander.",
         'gestes': [zoom('#t13-al-r3', s=1.5, fx=0.74, d=0.8), anneau('#t13-al-r3-cmd', d=1.4),
                    bulle('b-calcul', '#t13-al-r3-cmd', cote='bas', d=3.0), pause(2.8), dezoom(d=0.6),
                    defiler('#t13-in-al', -470, d=0.7), anneau('#t13-al-note', d=1.6),
                    reaction('r-cmd', d=3.0), pause(2.4)]},
        {'temps': 2, 'titre': 'Chaque casier, dépôt par dépôt',
         'texte': 'Stock complet : la quantité au bar et en cave, la valeur, la couverture.',
         'voix': "Dans Stock complet, Serge tape bière : il ne reste que les bières, avec la quantité au bar et en cave, "
                 "la valeur au coût et la couverture en jours.",
         'gestes': [defiler('#t13-in-al', 0, d=0.7), clic('#t13-tab-al-2'), vue('t13-stock'), pause(0.2),
                    defiler('#t13-in-st', -300, d=0.8), clic('#t13-rech'), saisir('t13-rech', 'Bière'),
                    cacher('#t13-st-autres', d=0.3),
                    texte('#t13-s-ref-v', FILTRE['ref']), texte('#t13-s-un-v', FILTRE['un'], avec=True),
                    texte('#t13-s-val-v', FILTRE['val'], avec=True), texte('#t13-s-pv-v', FILTRE['pv'], avec=True),
                    texte('#t13-s-pv-s', FILTRE['pv-s'], avec=True),
                    zoom('#t13-st-r2', s=1.5, fx=0.42, d=0.8), anneau('#t13-st-r1-bar', d=1.0),
                    anneau('#t13-st-r1-cave', d=1.0), pause(1.0), dezoom(d=0.6)]},
        {'temps': 2, 'titre': "L'argent qui dort",
         'texte': 'Rotation par référence, et la valeur immobilisée des dormants.',
         'voix': "Rotation et dormants montre ce qui tourne et ce qui dort. Dès soixante jours de couverture, une "
                 "référence est dormante : ici, cinq références immobilisent six cent cinquante et un mille francs.",
         'gestes': [defiler('#t13-in-st', 0, d=0.7), clic('#t13-tab-st-3'), vue('t13-rotation'),
                    compter('#t13-r-dorm-v', 0, VAL_DORM, d=1.2, apres=' FCFA'), anneau('#t13-r-dorm', d=1.2),
                    defiler('#t13-in-rot', -330, d=0.8), anneau('#t13-g-rot', d=1.2),
                    zoom('#t13-g-dorm', s=1.4, d=0.8), bulle('b-dormant', '#t13-g-dorm', cote='gauche', d=3.0),
                    pause(2.8), dezoom(d=0.6)]},
        {'temps': 2, 'titre': 'Le coulage, face au seuil',
         'texte': 'Chaque écart et chaque casse valorisés ; au-delà du seuil, la carte passe au rouge.',
         'voix': "Enfin, Inventaires et écarts valorise chaque ajustement et chaque casse. Ce mois-ci, les pertes "
                 "dépassent le seuil de deux pour cent du chiffre estimé : la carte passe au rouge, et le journal "
                 "montre d'où elles viennent.",
         'gestes': [defiler('#t13-in-rot', 0, d=0.7), clic('#t13-tab-rot-4'), vue('t13-ecarts'), pause(0.3),
                    anneau('#t13-e-pertes', d=1.2), bulle('b-coulage', '#t13-e-pertes', cote='bas', d=2.8), pause(2.4),
                    defiler('#t13-in-ec', -330, d=0.8), anneau('#t13-g-coul', d=1.3), defiler('#t13-in-ec', -560, d=0.8),
                    zoom('#t13-j-r1', s=1.4, fx=0.4, d=0.8), anneau('#t13-j-r1', d=1.2), anneau('#t13-j-r2', d=1.0),
                    dezoom(d=0.6), reaction('r-fin', d=3.0), pause(2.4)]},
    ],
    'resultats': {
        'titre': "Un stock piloté, au lieu d'être subi",
        'cartes': [
            {'valeur': '30', 'compter': 30, 'unite': 'jours', 'icone': 'calculatrice',
             'texte': 'de ventes glissantes pour calculer chaque quantité à commander'},
            {'valeur': '6', 'compter': 6, 'unite': 'onglets', 'icone': 'graphe',
             'texte': 'de la photo du stock au journal des mouvements, sur un seul écran'},
            {'valeur': '2', 'compter': 2, 'unite': '%', 'icone': 'alerte',
             'texte': 'seuil de coulage par défaut : au-delà, la carte passe au rouge'},
        ],
        'voix': "Trente jours de ventes derrière chaque commande, six onglets, un seuil de coulage qui alerte : le stock "
                "se pilote, au lieu de se subir.",
    },
    'cta': {
        'appel': 'Demandez votre démonstration',
        'suivant': 'Achats et fournisseurs',
        'voix': "Aïte haousse, par Aïte Consulting. Demandez votre démonstration, et retrouvez le tutoriel suivant : "
                "achats et fournisseurs.",
    },
    'vignette': {'etape': 2, 'apres': 9.0},
}
