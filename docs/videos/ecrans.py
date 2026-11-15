# -*- coding: utf-8 -*-
"""Les écrans d'AITE HOUSE, rejoués en HTML pour la vidéo de présentation.

Aucune capture d'écran dans la vidéo : chaque écran est reconstruit avec les
couleurs d'Odoo 18 (barre #71639E, boutons, pastilles, statusbar) et des
tableaux de bord AITE (violet #714B67, cartes à liseré), et avec les
libellés relevés dans les vues, les modèles et les assistants des modules
(``addons/*/views``, ``wizard``, ``models``). Les captures de recette
(``docs/captures_uat``, ``captures/``) n'ont servi que de modèle visuel.

Chaque fonction rend une chaîne HTML. Les identifiants posés sur les
éléments servent de cibles au curseur et aux gestes de la timeline : ils
doivent être uniques dans toute la vidéo (préfixer par le chapitre).
"""

import datetime as _dt
import math as _math
import re as _re
from html import escape as _e

import demo


def e(texte):
    """Échappe un texte destiné à l'écran."""
    return _e(str(texte), quote=True)


def _id(identifiant):
    return ' id="%s"' % identifiant if identifiant else ''


# ----------------------------------------------------- formats du produit --
# Les nombres tels que le produit les écrit depuis la livraison 4 (écarts
# n° 37-77, « formats unifiés »). Deux familles, à ne pas mélanger :
#  - les champs d'Odoo (fiches, listes, pivots) : milliers séparés par
#    l'espace insécable de la langue fr_FR (odoo/addons/base/data/
#    res.lang.csv), symbole monétaire après une espace insécable
#    (web/static/src/core/currency.js) ;
#  - les tableaux de bord OWL d'AITE (``fmtInt`` / ``fmtMoney`` des
#    ``static/src/js/services/utils.js``) : ``toLocaleString("fr-FR")``,
#    soit l'espace FINE insécable U+202F entre les milliers, une espace
#    simple avant le symbole, une espace insécable avant « % ».

NBSP = ' '     # espace insécable
NNBSP = ' '    # espace fine insécable (toLocaleString fr-FR)

# Mois abrégés des six moteurs serveur et de l'exécutif (MONTHS_FR de
# aite_*_dashboard/models/*_dashboard.py, monthLabel de
# aite_exec_dashboard/static/src/js/services/utils.js).
MOIS_ABREGES = ('janv.', 'févr.', 'mars', 'avr.', 'mai', 'juin', 'juil.', 'août', 'sept.', 'oct.', 'nov.', 'déc.')
# Mois en toutes lettres : regroupement « par mois » d'Odoo en français
# (pivots et listes groupées : « octobre 2026 »).
MOIS = ('janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août', 'septembre', 'octobre',
        'novembre', 'décembre')


def _rond(v):
    """``Math.round`` de JavaScript (le demi va vers le haut)."""
    return int(_math.floor(float(v or 0) + 0.5))


def _rond1(v):
    """``round1`` des utils.js : une décimale, jamais « -0,0 »."""
    return (_math.floor(float(v or 0) * 10 + 0.5) / 10.0) or 0.0


def _dec1(v):
    return ('%.1f' % _rond1(v)).replace('.', ',')


def entier(n, tdb=False):
    """Un entier à la française : « 2 159 ». ``tdb`` : tableau de bord OWL
    (``fmtInt`` : espace fine), sinon champ d'Odoo (espace insécable)."""
    v = _rond(n)
    return ('-' if v < 0 else '') + '{:,}'.format(abs(v)).replace(',', NNBSP if tdb else NBSP)


def fcfa(n, tdb=False, symbole='FCFA'):
    """Un montant en francs CFA : « 45 000 FCFA ». Champ d'Odoo (devise XAF,
    symbole « FCFA », arrondi 1) ou, avec ``tdb``, ``fmtMoney`` d'un tableau
    de bord (symbole de la société, « FCFA » et non plus « F » sur l'analyse
    des ventes : setCurrencySymbol)."""
    return entier(n, tdb) + (' ' if tdb else NBSP) + symbole


def pct(v):
    """« 56,0 % » : une décimale fixe, virgule, espace insécable (``fmtPct``
    de hotel_utils.js, pos_credit, pos_analytics, exec, direction)."""
    return _dec1(v) + NBSP + '%'


def variation(v):
    """« ▲ +12,5 % », « ▼ 3,0 % », « ■ 0,0 % » : le rendu unique des
    tableaux de bord AITE (``fmtDelta``) — la flèche dit le sens, jamais de
    « − » en plus, un écart nul n'est ni vert ni « +0,0 »."""
    r = _rond1(v)
    return ('▲ +' if r > 0 else '▼ ' if r < 0 else '■ ') + pct(abs(r))


def sens(v, hausse_mauvaise=False):
    """La couleur d'une variation, lue sur la valeur affichée (``deltaClass``) :
    'haut' (vert), 'bas' (rouge), 'nul' (gris). ``hausse_mauvaise`` : un coût,
    une dette, les nouvelles ardoises (``upIsBad``) — une hausse est rouge."""
    r = _rond1(v)
    if not r:
        return 'nul'
    return 'haut' if (r > 0) != bool(hausse_mauvaise) else 'bas'


def jours(v):
    """Une durée ou une moyenne en jours : « 12,3 j » (``fmtDays``)."""
    return _dec1(v) + ' j'


def age(v, tdb=True):
    """L'âge d'une ardoise en jours entiers : « 160 j » (``fmtAge``)."""
    return entier(v, tdb) + ' j'


def compte(n, un, plusieurs, tdb=True):
    """Un nombre suivi du mot accordé : « 1 remboursement », « 12 nuitées
    vendues » — pluriel à partir de 2, jamais de « (s) » (``fmtCount``)."""
    k = _rond(n)
    return entier(k, tdb) + ' ' + (plusieurs if abs(k) > 1 else un)


def date_fr(d):
    """« 14/10/2026 » (règle 6) : une date, ou une chaîne « AAAA-MM-JJ »."""
    if isinstance(d, str):
        a, m, j = d[:10].split('-')
        return '%s/%s/%s' % (j, m, a)
    return d.strftime('%d/%m/%Y')


def mois_abrege(mois, annee=None):
    """« sept. » ; avec l'année, « sept. 26 » (monthLabel de l'exécutif et
    graphiques mensuels de l'analyse des ventes)."""
    m = MOIS_ABREGES[mois - 1]
    return m if annee is None else '%s %s' % (m, str(annee)[2:])


def mois_long(mois, annee):
    """« octobre 2026 » : un regroupement par mois d'Odoo en français."""
    return '%s %d' % (MOIS[mois - 1], annee)


assert (entier(2159), fcfa(45000), pct(56), variation(12.46), variation(-3), variation(-0.04), jours(12.34),
        compte(1, 'fiche complète', 'fiches complètes'), date_fr(_dt.date(2026, 10, 14)), mois_abrege(9, 2026)) == (
    '2 159', '45 000 FCFA', '56,0 %', '▲ +12,5 %', '▼ 3,0 %', '■ 0,0 %', '12,3 j',
    '1 fiche complète', '14/10/2026', 'sept. 26')


# --------------------------------------------------------------- icônes --
# Redessinées en SVG (aucune police d'icônes, aucun émoji au rendu).

ICONES = {
    'grille': '<svg viewBox="0 0 24 24" fill="#fff"><rect x="2" y="2" width="5" height="5" rx="1"/><rect x="9.5" y="2" width="5" height="5" rx="1"/><rect x="17" y="2" width="5" height="5" rx="1"/><rect x="2" y="9.5" width="5" height="5" rx="1"/><rect x="9.5" y="9.5" width="5" height="5" rx="1"/><rect x="17" y="9.5" width="5" height="5" rx="1"/><rect x="2" y="17" width="5" height="5" rx="1"/><rect x="9.5" y="17" width="5" height="5" rx="1"/><rect x="17" y="17" width="5" height="5" rx="1"/></svg>',
    'loupe': '<svg viewBox="0 0 24 24" fill="none" stroke="#495057" stroke-width="2.4"><circle cx="10.5" cy="10.5" r="7"/><path d="M16 16l5 5"/></svg>',
    'filtre': '<svg viewBox="0 0 24 24" fill="#fff"><path d="M3 4h18l-7 8.5V19l-4 2v-8.5z"/></svg>',
    'plus': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"><path d="M12 5v14M5 12h14"/></svg>',
    'coche': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>',
    'play': '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M7 4.5v15l12.5-7.5z"/></svg>',
    'cle': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M14.7 6.3a4 4 0 00-5.4 5.4L3.5 17.5l3 3 5.8-5.8a4 4 0 005.4-5.4l-2.6 2.6-2.4-.6-.6-2.4z"/></svg>',
    'personne': '<svg viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="7.5" r="4.2"/><path d="M3.5 21c0-4.7 3.8-7.5 8.5-7.5s8.5 2.8 8.5 7.5z"/></svg>',
    'horloge': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3.5 2.5"/></svg>',
    'liste': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"><path d="M9 6h12M9 12h12M9 18h12"/><circle cx="4" cy="6" r="1.3" fill="currentColor"/><circle cx="4" cy="12" r="1.3" fill="currentColor"/><circle cx="4" cy="18" r="1.3" fill="currentColor"/></svg>',
    'imprimer': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linejoin="round"><path d="M6 9V3h12v6"/><rect x="2.5" y="9" width="19" height="9" rx="2"/><path d="M6 14h12v7H6z" fill="#fff"/></svg>',
    'fiche': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="4" width="20" height="16" rx="2"/><circle cx="8" cy="11" r="2.5"/><path d="M4.5 17c.6-2.2 2-3 3.5-3s2.9.8 3.5 3M14 9h5M14 13h5"/></svg>',
    'billet': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="6" width="20" height="12" rx="2"/><circle cx="12" cy="12" r="3"/></svg>',
    'document': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M14 2H6v20h12V6z"/><path d="M14 2v4h4M9 12h6M9 16h6"/></svg>',
    'lit': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><path d="M3 6v13M3 15h18v4M21 15v-3a3 3 0 00-3-3h-7v6"/><circle cx="7" cy="11" r="2"/></svg>',
    'cadenas': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><rect x="4" y="10.5" width="16" height="11" rx="2"/><path d="M8 10.5V7a4 4 0 018 0v3.5"/></svg>',
    'bulle': '<svg viewBox="0 0 24 24" fill="#fff"><path d="M3 5h18v11H9l-5 4v-4H3z"/></svg>',
    'echange': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 8h15l-4-4M20 16H5l4 4"/></svg>',
    'corbeille': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18M8 6V4h8v2M19 6l-1 14H6L5 6M10 11v6M14 11v6"/></svg>',
    'etoile': '<svg viewBox="0 0 24 24" fill="#F3B21B"><path d="M12 2.5l2.9 6.3 6.9.7-5.2 4.6 1.5 6.8L12 17.4l-6.1 3.5 1.5-6.8L2.2 9.5l6.9-.7z"/></svg>',
    'telephone': '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M6.6 10.8a15.2 15.2 0 006.6 6.6l2.2-2.2a1 1 0 011-.25 11.4 11.4 0 003.6.6 1 1 0 011 1V20a1 1 0 01-1 1A17 17 0 013 4a1 1 0 011-1h3.5a1 1 0 011 1 11.4 11.4 0 00.6 3.6 1 1 0 01-.25 1z"/></svg>',
    'fleche': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg>',
    'x': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg>',
}


def icone(nom, classe='ico'):
    return '<span class="%s">%s</span>' % (classe, ICONES[nom])


def curseur_svg():
    return ('<svg id="curseur-fleche" viewBox="0 0 32 32"><path d="M5 3l20 12-9 2.2L20.5 27l-4.2 2-4.4-9.6L5 25z" '
            'fill="#fff" stroke="#2A0F2B" stroke-width="2" stroke-linejoin="round"/></svg>')


# ---------------------------------------------------- éléments communs --

def puce(texte, genre='info', identifiant=None):
    """Une pastille Odoo : info, vert, rouge, orange, gris, violet, clair."""
    return '<span class="puce %s"%s>%s</span>' % (genre, _id(identifiant), e(texte))


def entree(identifiant, placeholder='', valeur='', classe='entree'):
    """Un champ de saisie : le texte indicatif s'efface quand la saisie commence."""
    ph = '<span class="ph" id="%s-ph">%s</span>' % (identifiant, e(placeholder))
    return ('<div class="%s" id="%s">%s<span class="val" id="%s-val">%s</span></div>'
            % (classe, identifiant, ph, identifiant, e(valeur)))


def bouton(identifiant, libelle, style='gris', ico=None):
    """Un bouton Odoo : primaire (violet), gris, lien, vert, contour, rouge-contour."""
    return '<span class="bt %s"%s>%s%s</span>' % (style, _id(identifiant), icone(ico) if ico else '', e(libelle))


def interrupteur(identifiant, actif=False):
    """L'interrupteur ``boolean_toggle`` d'Odoo."""
    return '<span class="toggle%s" id="%s"><i></i></span>' % (' on' if actif else '', identifiant)


# ------------------------------------------------------- fenêtre Odoo --

def fenetre(ident, app, menus, vues, actif=None, societe='', initiale='M', calques='', avatar='#7C5295'):
    """La fenêtre d'Odoo 18 : barre violette (application et menus), contenu."""
    entrees = ''.join('<span class="menu%s">%s</span>' % (' actif' if m == actif else '', e(m)) for m in menus)
    return (
        '<div class="app" id="%s">'
        '<div class="o-haut"><span class="grille">%s</span><span class="nom-app">%s</span>%s'
        '<span class="droite"><span class="pictos">%s</span><span class="societe">%s</span>'
        '<span class="avatar" style="background:%s">%s</span></span></div>'
        '<div class="o-contenu">%s</div>%s</div>'
        % (ident, ICONES['grille'], e(app), entrees, ICONES['bulle'], e(societe), avatar, e(initiale),
           ''.join(vues), calques))


def _vue(identifiant, initiale, contenu, classe='vue'):
    return '<div class="%s%s" id="%s">%s</div>' % (classe, ' initiale' if initiale else '', identifiant, contenu)


def vue_libre(identifiant, contenu, initiale=False, fond='gris'):
    """Une vue composée à la main avec les classes de ``shared/aite.css``."""
    return _vue(identifiant, initiale, '<div class="fond-%s">%s</div>' % (fond, contenu))


def recherche(facettes=(), identifiant=None, placeholder='Rechercher…'):
    """La barre de recherche d'Odoo 18 et ses facettes (filtres actifs)."""
    f = ''.join('<span class="facette"%s>%s<span class="ell">%s</span><span class="fx">×</span></span>'
                % (_id(i), icone('filtre', 'fic'), e(lib)) for i, lib in facettes)
    return ('<div class="recherche"%s>%s%s<span class="ph">%s</span><span class="deroule">▾</span></div>'
            % (_id(identifiant), icone('loupe', 'loupe'), f, e(placeholder)))


def cp_liste(titre, facettes=(), pager='', nouveau=True, ident=None):
    """Le panneau de contrôle d'une liste ou d'un kanban."""
    return ('<div class="cp">%s<span class="titre">%s</span>%s<span class="pager">%s</span></div>'
            % ('<span class="bt primaire">Nouveau</span>' if nouveau else '', e(titre),
               recherche(facettes, ident and ident + '-rech'), e(pager)))


def panneau_liste(titre, facettes=(), pager='', vues=('liste', 'pivot', 'graphe'), nouveau=False, ident=None):
    """Le panneau de contrôle complet d'une liste d'Odoo 18 sous le thème MuK (repris de t19, Restaurant ›
    Annulations, capture 22) : « Nouveau » (sauf ``create="0"`` : ``nouveau=False``), le titre, la recherche et ses
    facettes (``facettes`` = [(identifiant, libellé)]), la pagination « 1-4 / 4 », les flèches ‹ › et le
    sélecteur des vues (``vues`` : 'liste', 'pivot', 'graphe', la première active ; l'ordre de ``view_mode``).
    Identifiants : <ident>-titre, <ident>-rech (la recherche), <ident>-pager. Styles : ``.cp-l``,
    ``shared/aite-marketing.css``."""
    i = (lambda suffixe: ' id="%s-%s"' % (ident, suffixe)) if ident else (lambda suffixe: '')
    boutons = ''.join('<i%s>%s</i>' % (' class="actif"' if k == 0 else '', ICONES['vue-' + v]) for k, v in enumerate(vues))
    return ('<div class="cp cp-l">%s<span class="titre"%s>%s</span>%s<span class="pager"%s>%s</span>'
            '<span class="cp-fl"><i>‹</i><i>›</i></span><span class="cp-vues">%s</span></div>'
            % ('<span class="bt primaire">Nouveau</span>' if nouveau else '', i('titre'), e(titre),
               recherche(facettes, ident and ident + '-rech'), i('pager'), e(pager), boutons))


def cp_fiche(parent, reference, pager='', stats=(), nouveau=True):
    """Le panneau d'une fiche : « Nouveau », fil d'Ariane, boutons intelligents, pagination.

    ``stats`` : (identifiant, icône, libellé, valeur). ``nouveau=False`` pour
    une fiche ``create="0"``, qui n'a pas de bouton « Nouveau » (la note de
    chambre en attente depuis la livraison 4, roomcharge_pending_views.xml).
    """
    boutons = ''.join('<span class="stat"%s>%s<span class="st-t"><span>%s</span><b id="%s-v">%s</b></span></span>'
                      % (_id(i), icone(ic, 'sic'), e(l), i, e(v)) for i, ic, l, v in stats)
    return ('<div class="cp">%s'
            '<div class="fil"><span class="parent">%s</span><span class="ref">%s</span></div>'
            '<div class="stats">%s</div><span class="pager">%s</span></div>'
            % ('<span class="bt contour">Nouveau</span>' if nouveau else '', e(parent), e(reference), boutons,
               e(pager)))


def vue_liste(identifiant, titre, colonnes, lignes, facettes=(), pager='', initiale=False, total=None, nouveau=True,
              groupes=None):
    """Une vue liste.

    ``colonnes`` : (libellé, largeur CSS, alignement 'g' ou 'd') ; ``lignes`` :
    dict ``id``, ``cellules`` (texte, ou tuple (html,) déjà composé), ``classe``.
    ``total`` : cellules de la ligne de total (même gabarit). ``groupes`` :
    {index de ligne: libellé} pour les regroupements.
    """
    gabarit = ' '.join(c[1] for c in colonnes)
    tete = '<div class="tete" style="grid-template-columns:%s"><span class="cb"></span>%s</div>' % (
        '40px ' + gabarit, ''.join('<span class="ell%s">%s</span>' % (' d' if len(c) > 2 and c[2] == 'd' else '', e(c[0]))
                                   for c in colonnes))
    corps = []
    for i, ligne in enumerate(lignes):
        if groupes and i in groupes:
            corps.append('<div class="groupe">▾ %s</div>' % e(groupes[i]))
        cellules = []
        for k, c in enumerate(ligne['cellules']):
            droite = len(colonnes[k]) > 2 and colonnes[k][2] == 'd'
            cellules.append(c[0] if isinstance(c, tuple) else '<span class="ell%s">%s</span>' % (' d' if droite else '', e(c)))
        corps.append('<div class="ligne%s" id="%s" style="grid-template-columns:40px %s"><span class="cb"></span>%s</div>' % (
            (' ' + ligne['classe']) if ligne.get('classe') else '', ligne['id'], gabarit, ''.join(cellules)))
    pied = ''
    if total:
        pied = '<div class="total" style="grid-template-columns:40px %s"><span></span>%s</div>' % (
            gabarit, ''.join('<span class="d">%s</span>' % e(t) if t else '<span></span>' for t in total))
    contenu = cp_liste(titre, facettes, pager, nouveau, identifiant) + '<div class="liste">%s%s%s</div>' % (
        tete, ''.join(corps), pied)
    return _vue(identifiant, initiale, contenu)


def lien(texte, identifiant=None):
    return ('<span class="lien ell"%s>%s</span>' % (_id(identifiant), e(texte)),)


def num(texte, classe=''):
    return ('<span class="d %s">%s</span>' % (classe, e(texte)),)


def cell_puce(texte, genre, identifiant=None):
    return ('<span>%s</span>' % puce(texte, genre, identifiant),)


def cell_html(html):
    return (html,)


# -------------------------------------------------------------- la fiche --

def statusbar(identifiant, etats, actif):
    """La barre d'états d'Odoo (flèches) ; l'état actif porte ``actif``.

    Chaque étape a son identifiant ``<id>-<n>`` : le geste ``classe`` déplace
    l'état actif comme le fait l'application après un bouton.
    """
    items = ''.join('<span class="st-et%s" id="%s-%d">%s</span>' % (' actif' if i == actif else '', identifiant, i, e(x))
                    for i, x in enumerate(etats))
    return '<div class="statusbar" id="%s">%s</div>' % (identifiant, items)


def champ(libelle, valeur, identifiant=None, lien_=False, html=False, gras=False):
    v = valeur if html else e(valeur)
    return ('<div class="ch"><span class="l%s">%s</span><span class="v%s"%s>%s</span></div>'
            % (' gras' if gras else '', e(libelle), ' lien' if lien_ else '', _id(identifiant), v))


def groupe(titre, champs, identifiant=None):
    return '<div class="grp"%s><div class="grp-t">%s</div>%s</div>' % (_id(identifiant), e(titre), ''.join(champs))


def onglets(noms, actif=0):
    return '<div class="onglets">%s</div>' % ''.join(
        '<span class="onglet%s">%s</span>' % (' actif' if i == actif else '', e(n)) for i, n in enumerate(noms))


def table(colonnes, lignes, total=None, ajouter='Ajouter une ligne', identifiant=None):
    """Un tableau de lignes (one2many) : ``colonnes`` (libellé, largeur, 'd'),
    ``lignes`` : (identifiant, [cellules]), cellules texte ou (html,)."""
    gab = ' '.join(c[1] for c in colonnes)
    tete = '<div class="t-tete" style="grid-template-columns:%s">%s</div>' % (
        gab, ''.join('<span class="ell%s">%s</span>' % (' d' if len(c) > 2 else '', e(c[0])) for c in colonnes))
    corps = []
    for ident, cellules in lignes:
        cs = []
        for k, c in enumerate(cellules):
            d = len(colonnes[k]) > 2
            cs.append(c[0] if isinstance(c, tuple) else '<span class="ell%s">%s</span>' % (' d' if d else '', e(c)))
        corps.append('<div class="t-ligne"%s style="grid-template-columns:%s">%s</div>' % (_id(ident), gab, ''.join(cs)))
    ajout = '<div class="t-ajout">%s</div>' % e(ajouter) if ajouter else ''
    pied = ''
    if total:
        pied = '<div class="t-total" style="grid-template-columns:%s">%s</div>' % (
            gab, ''.join('<span class="d">%s</span>' % e(t) if t else '<span></span>' for t in total))
    return '<div class="table"%s>%s%s%s%s</div>' % (_id(identifiant), tete, ''.join(corps), ajout, pied)


def vue_fiche(identifiant, cp, boutons, statut, contenu, initiale=False, bandeau='', boutons_apres=None):
    """Une fiche Odoo 18 : panneau, bande de boutons + statusbar, feuille.

    ``boutons`` : HTML des boutons (``bouton``) ; ``statut`` : HTML de la
    statusbar (``statusbar``) ; ``bandeau`` : un avertissement posé sous la
    bande (masqué au départ s'il porte la classe ``masque``) ;
    ``boutons_apres`` : les bandes successives (groupes ``<id>-gb``, ``-gc``…).
    La feuille défile : ``<id>-defil``.
    """
    groupes = '<div class="bb-groupe" id="%s-ga">%s</div>' % (identifiant, ''.join(boutons))
    if boutons_apres:
        for lettre, lot in zip('bcdef', boutons_apres):
            groupes += '<div class="bb-groupe masque" id="%s-g%s">%s</div>' % (identifiant, lettre, ''.join(lot))
    bande = '<div class="bande">%s%s</div>' % (groupes, statut)
    feuille = ('<div class="feuille-cadre" id="%s-feuille" data-layout-allow-overflow data-layout-allow-occlusion>%s'
               '<div class="defil" id="%s-defil" data-layout-allow-overflow data-layout-allow-occlusion>'
               '<div class="feuille">%s</div></div></div>' % (identifiant, bandeau, identifiant, contenu))
    return _vue(identifiant, initiale, cp + bande + feuille)


def titre_fiche(texte, identifiant=None):
    return '<div class="f-titre"%s>%s</div>' % (_id(identifiant), e(texte))


def deux_colonnes(gauche, droite):
    return '<div class="f-cols"><div>%s</div><div>%s</div></div>' % (gauche, droite)


# ---------------------------------------------------------------- kanban --

def vue_kanban(identifiant, titre, colonnes, facettes=(), initiale=False, nouveau=True):
    """Un kanban groupé : ``colonnes`` = (titre, effectif, [cartes HTML], identifiant)."""
    cols = ''.join('<div class="k-col"%s><div class="k-titre">%s <span%s>(%s)</span></div>%s</div>'
                   % (_id(i), e(t), _id(i and i + '-n'), e(n), ''.join(cartes)) for t, n, cartes, i in colonnes)
    return _vue(identifiant, initiale, cp_liste(titre, facettes, '', nouveau, identifiant)
                + '<div class="kanban">%s</div>' % cols)


def carte(identifiant, contenu, classe=''):
    return '<div class="k-carte %s" id="%s">%s</div>' % (classe, identifiant, contenu)


# ----------------------------------------------------- tableaux de bord --

def tdb_entete(titre, sous, bouton_=None):
    b = '<span class="bt primaire tdb-bt">%s%s</span>' % (icone('plus'), e(bouton_)) if bouton_ else ''
    return '<div class="tdb-tete"><div><div class="tdb-titre">%s</div><div class="tdb-sous">%s</div></div>%s</div>' % (
        e(titre), e(sous), b)


def tdb_filtres(lignes):
    """Les puces de filtre : ``lignes`` = (libellé, [puces], index actif)."""
    rangs = []
    for lib, puces, actif in lignes:
        rangs.append('<div class="tdb-rang"><span class="tdb-lib">%s</span>%s</div>' % (
            e(lib), ''.join('<span class="chip%s">%s</span>' % (' actif' if i == actif else '', e(p))
                            for i, p in enumerate(puces))))
    return '<div class="tdb-filtres">%s</div>' % ''.join(rangs)


def _kpi_delta(delta):
    """La ligne de variation d'une carte, au rendu du produit (``variation``) :
    flèche, signe « + » d'une hausse, pas de « − » sous « ▼ », écart nul en
    gris (classe ``nul``)."""
    if isinstance(delta, (int, float)):
        delta = (delta,)
    premier = delta[0]
    if isinstance(premier, (int, float)):
        libelle = delta[1] if len(delta) > 1 else ''
        texte = variation(premier) + (' ' + libelle if libelle else '')
        genre = sens(premier, len(delta) > 2 and delta[2])
    else:
        texte, genre = premier.strip(), delta[1]
        if texte[:1] not in '▲▼■':
            if genre == 'haut':
                texte = '▲ ' + (texte if texte.startswith('+') else '+' + texte)
            elif genre == 'bas':
                texte = '▼ ' + texte.lstrip('-−')
            else:
                texte = '■ ' + texte
        texte = _re.sub(r'(\d) %', '\\1' + NBSP + '%', texte)
    return '<div class="kpi-d %s">%s</div>' % (genre, e(texte))


def kpi(identifiant, libelle, valeur, sous='', accent=None, delta=None, aide=False):
    """Une carte d'indicateur des tableaux de bord AITE.

    ``delta``, la variation, rendue comme le produit (« ▲ +12,5 % vs période
    précédente », « ▼ 3,0 % », « ■ 0,0 % ») :

    - un nombre (la variation en %), coloré par son signe ;
    - (nombre, libellé[, hausse_mauvaise]) : suivi du libellé de la carte
      (« vs période précédente » sur la Réception et POS Crédit ; « vs N-1 »
      sur l'exécutif, sauf le rythme du mois : « vs même date N-1 » ; aucun
      libellé sur les cartes Hébergement du cockpit) ; ``hausse_mauvaise``
      pour un coût ou les nouvelles ardoises (``upIsBad``) ;
    - (texte, 'haut' | 'bas' | 'nul') : un texte déjà composé ; la flèche, et
      le « + » d'une hausse, s'ajoutent s'il ne les porte pas. Ici le genre
      donne à la fois la flèche ET la couleur : une baisse qui est une bonne
      nouvelle (ardoises ▼ en vert) ou une hausse mauvaise (CMV ▲ en rouge)
      s'écrit OBLIGATOIREMENT sous la forme numérique (v, libellé, True).
    """
    d = _kpi_delta(delta) if delta is not None else ''
    a = '<span class="kpi-aide">?</span>' if aide else ''
    return ('<div class="kpi%s" id="%s"><div class="kpi-l">%s%s</div><div class="kpi-v" id="%s-v">%s</div>%s'
            '<div class="kpi-s">%s</div></div>' % (' acc-' + accent if accent else '', identifiant, e(libelle), a,
                                                  identifiant, e(valeur), d, e(sous)))


def tdb_section(titre, cartes, colonnes=4):
    return '<div class="tdb-sect">%s</div><div class="tdb-grille c%d">%s</div>' % (e(titre), colonnes, ''.join(cartes))


def vue_tdb(identifiant, contenu, initiale=False):
    return _vue(identifiant, initiale, '<div class="tdb">%s</div>' % contenu)


def graphe_courbe(identifiant, titre, valeurs, couleur='#714B67', etiquettes=()):
    """Une courbe d'évolution, révélée de gauche à droite (cache ``<id>``)."""
    n = len(valeurs)
    w, h = 760, 210
    pts = ['%.1f,%.1f' % (i * w / (n - 1), h - v * h / 100.0) for i, v in enumerate(valeurs)]
    aire = 'M0,%d L%s L%d,%d Z' % (h, ' L'.join(pts), w, h)
    grille = ''.join('<line x1="0" x2="%d" y1="%d" y2="%d" stroke="#E5E7EB"/>' % (w, y, y) for y in range(0, h + 1, h // 5))
    lab = ''.join('<span>%s</span>' % e(x) for x in etiquettes)
    return ('<div class="g-carte"><div class="g-titre">%s</div><div class="g-zone"><svg viewBox="0 0 %d %d" preserveAspectRatio="none">'
            '%s<path d="%s" fill="%s" fill-opacity=".12"/><polyline points="%s" fill="none" stroke="%s" stroke-width="3.5"/></svg>'
            '<div class="cache-graphe" id="%s"></div></div><div class="g-lab">%s</div></div>'
            % (e(titre), w, h, grille, aire, couleur, ' '.join(pts), couleur, identifiant, lab))


def graphe_anneau(identifiant, titre, parts):
    """Un anneau de répartition : ``parts`` = (libellé, valeur, couleur)."""
    total = float(sum(p[1] for p in parts)) or 1.0
    r, c = 80, 2 * 3.14159265 * 80
    debut = 0.0
    arcs = []
    for lib, v, coul in parts:
        long_ = c * v / total
        arcs.append('<circle r="%d" cx="110" cy="110" fill="none" stroke="%s" stroke-width="42" '
                    'stroke-dasharray="%.1f %.1f" stroke-dashoffset="%.1f"/>' % (r, coul, long_, c - long_, -debut))
        debut += long_
    leg = ''.join('<div class="g-leg"><i style="background:%s"></i>%s</div>' % (coul, e(lib)) for lib, _, coul in parts)
    return ('<div class="g-carte"><div class="g-titre">%s</div><div class="g-anneau"><svg id="%s" viewBox="0 0 220 220">'
            '<g transform="rotate(-90 110 110)">%s</g></svg><div class="g-legs">%s</div></div></div>'
            % (e(titre), identifiant, ''.join(arcs), leg))


def graphe_barres(identifiant, titre, barres, etiquettes=()):
    """Des barres verticales : ``barres`` = (valeur 0–100, couleur)."""
    b = ''.join('<i class="g-b" style="height:%d%%;background:%s"></i>' % (v, coul) for v, coul in barres)
    lab = ''.join('<span>%s</span>' % e(x) for x in etiquettes)
    return ('<div class="g-carte"><div class="g-titre">%s</div><div class="g-barres" id="%s">%s</div>'
            '<div class="g-lab">%s</div></div>' % (e(titre), identifiant, b, lab))


def graphes(*cartes):
    return '<div class="tdb-grille c%d">%s</div>' % (len(cartes), ''.join(cartes))


# ------------------------------------------------------------- assistants --

def assistant(identifiant, titre, corps, boutons, haut=110, largeur=1180):
    """Une fenêtre d'assistant Odoo 18, posée sur un voile.

    ``boutons`` : (identifiant, libellé, style, icône).
    """
    pied = ''.join(bouton(i, l, s, ic) for i, l, s, ic in boutons)
    return ('<div class="voile masque" id="%s-voile" data-layout-allow-overlap data-layout-allow-occlusion></div>'
            '<div class="modale masque" id="%s" style="top:%dpx;width:%dpx;margin-left:-%dpx" '
            'data-layout-allow-overlap data-layout-allow-occlusion>'
            '<div class="m-tete"><span>%s</span><span class="m-x">%s</span></div>'
            '<div class="m-corps">%s</div><div class="m-pied">%s</div></div>'
            % (identifiant, identifiant, haut, largeur, largeur // 2, e(titre), ICONES['x'], corps, pied))


def m_champs(gauche, droite=None):
    """Les champs d'un assistant, sur une ou deux colonnes."""
    if droite is None:
        return '<div class="m-grille un">%s</div>' % ''.join(gauche)
    return '<div class="m-grille"><div>%s</div><div>%s</div></div>' % (''.join(gauche), ''.join(droite))


def m_champ(libelle, valeur_html, identifiant=None):
    return '<div class="m-ch"%s><span class="l">%s</span><span class="v">%s</span></div>' % (
        _id(identifiant), e(libelle), valeur_html)


def erreur_acces(identifiant, modele, technique, groupes):
    """Le refus d'accès d'Odoo, tel qu'il s'affiche en français."""
    g = ''.join('<div class="g">- %s</div>' % e(x) for x in groupes)
    corps = ('<p>Vous n\'êtes pas autorisé à accéder aux enregistrements \'%s\' (%s).</p>'
             '<p>Cette opération est autorisée pour les groupes suivants :</p>%s'
             '<p>Contactez votre administrateur pour demander l\'accès si nécessaire.</p>' % (e(modele), e(technique), g))
    return assistant(identifiant, "Erreur d'accès", '<div class="refus">%s</div>' % corps,
                     [(identifiant + '-ok', 'Fermer', 'primaire', None)], haut=200, largeur=1140)


def toast(identifiant, titre, texte, genre=''):
    return ('<div class="toast masque %s" id="%s" data-layout-allow-overlap data-layout-allow-occlusion><b>%s</b>%s</div>'
            % (genre, identifiant, e(titre), e(texte)))


# ------------------------------------------------------- téléphone --

def telephone(identifiant, titre, contenu):
    """Un téléphone posé sur l'écran : la vue « Ma journée » d'une équipière."""
    return ('<div class="voile masque" id="%s-voile" data-layout-allow-overlap data-layout-allow-occlusion></div>'
            '<div class="tel masque" id="%s" data-layout-allow-overlap data-layout-allow-occlusion><div class="tel-ecran">'
            '<div class="tel-haut"><span class="burger">≡</span>%s</div><div class="tel-corps">%s</div></div></div>'
            % (identifiant, identifiant, e(titre), contenu))


# ------------------------------------------------------- calendrier --

def calendrier(identifiant, mois, numeros, gris, aujourdhui, evenements, initiale=False):
    """Le planning des chambres en vue calendrier (Community), cinq semaines.

    ``numeros`` : les 35 numéros de jour affichés ; ``gris`` : les index des
    jours hors du mois ; ``aujourdhui`` : l'index du jour pastillé.
    ``evenements`` : (semaine 0–4, jour de début 0–6, durée en jours, libellé, couleur).
    """
    jours = ['LUN.', 'MAR.', 'MER.', 'JEU.', 'VEN.', 'SAM.', 'DIM.']
    tete = ''.join('<span>%s</span>' % j for j in jours)
    cases = []
    for i, n in enumerate(numeros):
        s, j = divmod(i, 7)
        pastille = '<b class="auj">%d</b>' % n if i == aujourdhui else str(n)
        cases.append('<div class="c-case%s" style="grid-column:%d;grid-row:%d"><span class="c-n">%s</span></div>'
                     % (' gris' if i in gris else '', j + 1, s + 1, pastille))
    ev = ''
    occupe = {}
    for s, j, d, lib, coul in evenements:
        rang = 0
        while any(occupe.get((s, k, rang)) for k in range(j, min(7, j + d))):
            rang += 1
        for k in range(j, min(7, j + d)):
            occupe[(s, k, rang)] = True
        ev += ('<div class="c-ev" style="left:calc(%d * 100%% / 7 + 4px);width:calc(%d * 100%% / 7 - 8px);'
               'top:calc(%d * 20%% + 46px + %d * 31px);background:%s"><span class="ell">%s</span></div>'
               % (j, min(d, 7 - j), s, rang, coul, e(lib)))
    cp = ('<div class="cp"><span class="titre">Planning des chambres</span>%s</div>'
          '<div class="c-barre"><span class="bt gris">←</span><span class="bt gris">→</span><span class="bt gris">Mois ▾</span>'
          '<span class="bt gris">Aujourd\'hui</span><span class="c-mois">%s</span></div>' % (recherche(), e(mois)))
    grille = ('<div class="cal"><div class="c-tete">%s</div><div class="c-grille">%s<div class="c-evs" id="%s-evs">%s</div></div></div>'
              % (tete, ''.join(cases), identifiant, ev))
    return _vue(identifiant, initiale, cp + grille)


# ------------------------------------------------------------- site web --

def site(identifiant, vues, nom_site, calques='', tel=None):
    """Le site web public de l'établissement : en-tête, page, vues empilées.

    Menus « Accueil » et « Contactez-nous » (website, i18n/fr.po : « Home »,
    « Contact us ») et « Réservation » (aite_website_booking,
    data/website_menu_data.xml) ; bouton « Contactez-nous » (« Contact Us ») ;
    le téléphone de l'hôtel (``demo.TEL_HOTEL``).
    """
    return ('<div class="app site" id="%s"><div class="s-nav"><span class="s-logo">%s</span>'
            '<span class="s-m">Accueil</span><span class="s-m actif">Réservation</span><span class="s-m">Contactez-nous</span>'
            '<span class="s-tel">%s%s</span><span class="bt primaire s-bt">Contactez-nous</span></div>'
            '<div class="s-page">%s</div>%s</div>'
            % (identifiant, e(nom_site), icone('telephone'), e(tel or demo.TEL_HOTEL), ''.join(vues), calques))


def s_vue(identifiant, contenu, initiale=False):
    return _vue(identifiant, initiale, '<div class="s-cadre">%s</div>' % contenu, classe='vue s-vue')


# ------------------------------------------------- thème MuK (tutoriels) --
# Le client web d'Odoo 18 habillé par le thème MuK (muk_web_theme
# 18.0.1.2.5 et ses dépendances) : barre du haut ardoise, barre des
# applications sombre à gauche, accent bleu acier. Couleurs relevées dans
# muk_web_colors/static/src/scss/colors_light.scss et
# muk_web_appsbar/static/src/scss/variables.scss ; forme d'après les captures
# de référence prises sur une base de démonstration où le thème est installé.

ICONES.update({
    'cahier': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M5 3h12a2 2 0 012 2v16H7a2 2 0 01-2-2z"/><path d="M5 17a2 2 0 012-2h12M9 7h6M9 10.5h6"/></svg>',
    'calculatrice': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><rect x="5" y="2.5" width="14" height="19" rx="2"/><rect x="8" y="5.5" width="8" height="4" rx=".6"/><path d="M8.5 13h.01M12 13h.01M15.5 13h.01M8.5 16.5h.01M12 16.5h.01M15.5 16.5h.01" stroke-width="2.6" stroke-linecap="round"/></svg>',
    'alerte': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linejoin="round" stroke-linecap="round"><path d="M12 3l10 18H2z"/><path d="M12 10v5M12 18h.01"/></svg>',
    'sablier': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linejoin="round" stroke-linecap="round"><path d="M6 2.5h12M6 21.5h12M7 2.5c0 5 10 5 10 9.5S7 16.5 7 21.5M17 2.5c0 5-10 5-10 9.5s10 4.5 10 9.5"/></svg>',
    'piles': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M8 3h10v14H8z"/><path d="M5 6v15h10"/><path d="M11 7h4M11 10h4M11 13h3"/></svg>',
    'pieces': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><ellipse cx="9" cy="7" rx="6" ry="3"/><path d="M3 7v4c0 1.7 2.7 3 6 3s6-1.3 6-3V7"/><path d="M9 14v3c0 1.7 2.7 3 6 3s6-1.3 6-3v-4c0-1.7-2.7-3-6-3"/></svg>',
    'graphe': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"/><path d="M7 15l4-5 3 3 6-7"/></svg>',
    'interrogation': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><circle cx="12" cy="12" r="9.5"/><path d="M9.3 9.2a2.8 2.8 0 015.4 1c0 1.9-2.7 2.4-2.7 4"/><path d="M12 17.5h.01" stroke-width="3"/></svg>',
    'message': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M4 4h16v12H10l-5 4v-4H4z"/><path d="M8 9h8M8 12h5"/></svg>',
    'boite': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M3 7.5L12 3l9 4.5v9L12 21l-9-4.5z"/><path d="M3 7.5l9 4.5 9-4.5M12 12v9"/></svg>',
    'cloche': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"><path d="M6 16V11a6 6 0 0112 0v5l2 2H4z"/><path d="M10 20.5a2 2 0 004 0"/></svg>',
    'carte': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2.5" y="5" width="19" height="14" rx="2"/><path d="M2.5 10h19M6 15h4"/></svg>',
    'balai': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"><path d="M19 3l-7.5 7.5"/><path d="M10 9l5 5-3 7-9-9z"/><path d="M6 14l2 2M8.5 11.5l3 3"/></svg>',
    'globe': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9.5"/><path d="M2.5 12h19M12 2.5c3 3 3 16 0 19M12 2.5c-3 3-3 16 0 19"/></svg>',
    'cible': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9.5"/><circle cx="12" cy="12" r="5.5"/><circle cx="12" cy="12" r="1.6" fill="currentColor"/></svg>',
    'eclair': '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M13.5 2L4 13.5h6.5L9 22l11-12.5h-6.8z"/></svg>',
    'bouclier': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"><path d="M12 2.5l8 3v6c0 5-3.5 8.5-8 10-4.5-1.5-8-5-8-10v-6z"/><path d="M8.5 12l2.5 2.5 4.5-5"/></svg>',
})

# Les applications de la barre MuK : (nom affiché, icône livrée avec le
# module, copiée dans le projet par produire.py sous assets/icones/).
APPS_MUK = {
    'Direction': 'direction', 'Discussion': 'discussion', 'Hôtel': 'hotel', 'Tableaux de bord': 'tableaux',
    'POS Crédit': 'pos-credit', 'Point de Vente': 'point-de-vente', 'Facturation': 'facturation',
    'Site Web': 'site-web', 'Achats': 'achats', 'Inventaire': 'inventaire', 'Maintenance': 'maintenance',
    'Apps': 'apps', 'Paramètres': 'parametres',
}
# Les applications que voit chaque profil, relevées dans la barre MuK des
# comptes de démonstration (demo.reception, demo.gouvernante, demo.caisse,
# demo.magasin, demo.direction) sur la base où le thème est installé.
APPS_PROFIL = {
    'admin': ['Direction', 'Discussion', 'Hôtel', 'Tableaux de bord', 'POS Crédit', 'Point de Vente', 'Facturation',
              'Site Web', 'Achats', 'Inventaire', 'Maintenance', 'Apps', 'Paramètres'],
    'direction': ['Direction', 'Discussion', 'Hôtel', 'Tableaux de bord', 'POS Crédit', 'Point de Vente', 'Facturation',
                  'Site Web', 'Achats', 'Inventaire', 'Maintenance', 'Apps'],
    'reception': ['Discussion', 'Hôtel', 'Tableaux de bord', 'Site Web', 'Maintenance', 'Apps'],
    'gouvernante': ['Discussion', 'Hôtel', 'Tableaux de bord', 'Site Web', 'Maintenance', 'Apps'],
    'caisse': ['Discussion', 'Tableaux de bord', 'POS Crédit', 'Point de Vente', 'Site Web', 'Maintenance', 'Apps'],
    'magasin': ['Discussion', 'Tableaux de bord', 'Site Web', 'Inventaire', 'Maintenance', 'Apps'],
}

# Les menus de la barre du haut, par application et par profil (livraison 4).
# Ordre = séquence des menuitem, puis ordre de création ; un menu réservé à
# un groupe n'apparaît que pour ce profil.
#  - Hôtel : aite_hotel_management/views/hotel_menus.xml (« Réception »,
#    anciennement « Front Desk », écart n° 42 ; Réservations ; Facturation ;
#    Gouvernante ; Configuration, Responsable), aite_exec_dashboard/views/
#    exec_menus.xml (« Activité par pôle », anciennement « Direction »,
#    Responsable), aite_slot_booking/views/slot_menus.xml (Espaces &
#    Prestations), aite_hotel_pos_link/views/roomcharge_menus.xml (Notes de
#    chambre en attente), aite_loyalty/views/loyalty_menus.xml (Fidélité) ;
#    le profil Gouvernante seul ne voit que « Gouvernante ».
#  - Point de Vente : point_of_sale (fr.po : Tableau de bord, Commandes,
#    Produits, Analyse, Configuration). « Analyse AITE » n'est plus dans la
#    barre : c'est une section du menu « Analyse » (aite_pos_analytics/views/
#    pos_analytics_menus.xml, parent point_of_sale.menu_point_rep, écart n° 67).
#  - Achats, Inventaire : purchase et stock (fr.po), plus « Tableau de bord
#    AITE » (aite_purchase_dashboard, aite_stock_dashboard) ; « Analyse » et
#    « Configuration » sont réservés aux responsables (profil Direction).
#  - POS Crédit : aite_pos_credit/views/pos_credit_menus.xml.
#  - Direction : aucun sous-menu (aite_direction_dashboard).
MENUS_MUK = {
    'hotel_reception': ['Réception', 'Réservations', 'Espaces & Prestations', 'Notes de chambre en attente',
                        'Facturation', 'Fidélité', 'Gouvernante'],
    'hotel_direction': ['Activité par pôle', 'Réception', 'Réservations', 'Espaces & Prestations',
                        'Notes de chambre en attente', 'Facturation', 'Fidélité', 'Gouvernante', 'Configuration'],
    'hotel_gouvernante': ['Gouvernante'],
    # Profils responsables (Direction) : « Analyse » et « Configuration »
    # n'apparaissent qu'aux groupes group_pos_manager / group_purchase_manager.
    'point_de_vente': ['Tableau de bord', 'Commandes', 'Produits', 'Analyse', 'Configuration'],
    'achats': ['Commandes', 'Tableau de bord AITE', 'Produits', 'Analyse', 'Configuration'],
    # Profil Caisse (group_pos_user seul) : ni « Analyse » ni « Configuration ».
    'point_de_vente_caisse': ['Tableau de bord', 'Commandes', 'Produits'],
    'inventaire': ["Vue d'ensemble", 'Opérations', 'Tableau de bord AITE', 'Produits'],
    'pos_credit': ['Recouvrement', 'Ardoises', 'Remboursements'],
    'direction': [],
}
# Les entrées du menu « Analyse » du Point de Vente, section « Analyse AITE »
# (pos_analytics_menus.xml ; « Pivot & Graph » est devenu « Tableau croisé &
# graphique »).
MENU_ANALYSE_AITE = ['Tableau de bord', 'Par caisse', 'Sessions POS', 'Par catégorie', 'Écarts de caisse',
                     'Tableau croisé & graphique']


def icone_app(app):
    return '<img class="muk-ico" src="assets/icones/%s.png" alt="">' % APPS_MUK[app]


def fenetre_muk(ident, app, menus, vues, actif=None, societe='', initiale='M', calques='', avatar='#7C5295',
                apps=None, app_active=None):
    """La fenêtre d'Odoo 18 avec le thème MuK : barre du haut (application et
    menus), barre des applications à gauche, contenu. ``apps`` : les noms de
    la barre (``APPS_PROFIL``), ``app_active`` : l'application en surbrillance."""
    apps = apps or APPS_PROFIL['direction']
    app_active = app_active or app
    entrees = ''.join('<span class="menu%s">%s</span>' % (' actif' if m == actif else '', e(m)) for m in menus)
    # un nom trop long se termine en « … », comme dans la barre MuK
    barre = ''.join('<div class="muk-app%s" id="%s-app-%s">%s<span data-layout-allow-overflow>%s</span></div>'
                    % (' actif' if a == app_active else '', ident, APPS_MUK[a], icone_app(a), e(a)) for a in apps)
    return (
        '<div class="app muk" id="%s">'
        '<div class="o-haut"><span class="grille">%s</span><span class="nom-app">%s</span>%s'
        '<span class="droite"><span class="pictos">%s</span><span class="societe">%s</span>'
        '<span class="avatar" style="background:%s">%s</span></span></div>'
        '<div class="muk-apps" id="%s-apps">%s</div>'
        '<div class="o-contenu">%s</div>%s</div>'
        % (ident, ICONES['grille'], e(app), entrees, ICONES['bulle'], e(societe), avatar, e(initiale),
           ident, barre, ''.join(vues), calques))


def menu_apps_muk(identifiant, apps, initiale=False):
    """Le menu des applications du thème MuK : des tuiles blanches sur un fond
    bleu-gris, qui couvre le contenu (une vue du groupe ``odoo``)."""
    tuiles = ''.join('<div class="muk-tuile" id="%s-%s"><span class="t">%s</span><span class="n">%s</span></div>'
                     % (identifiant, APPS_MUK[a], icone_app(a), e(a)) for a in apps)
    return _vue(identifiant, initiale, '<div class="muk-menu">%s</div>' % tuiles, classe='vue muk-menu-vue')


def navigateur(contenu, identifiant='navigateur'):
    """Le cadre d'une fenêtre de navigateur, sans adresse : trois pastilles."""
    return ('<div class="navigateur" id="%s"><div class="nav-barre"><i></i><i></i><i></i></div>%s</div>'
            % (identifiant, contenu))


# ------------------------------------------------- composants des tutoriels --

def avec_chatter(vue_html, messages=(), identifiant=None):
    """Ajoute à une fiche (``vue_fiche``) la discussion que le thème MuK place
    à droite : « Envoyer message », « Note », « Activités », puis les messages
    [(auteur, date, texte)]."""
    msgs = ''.join('<div class="ch-msg"><span class="ch-av">%s</span><div><div class="ch-a"><b>%s</b> <small>%s</small></div>'
                   '<div class="ch-t">%s</div></div></div>' % (e(a[0]), e(a), e(d), e(t)) for a, d, t in messages)
    panneau = ('<div class="chatter"%s><div class="ch-bts"><span class="bt primaire">%sEnvoyer message</span>'
               '<span class="bt gris">Note</span><span class="bt gris">%sActivités</span></div>%s</div>'
               % (_id(identifiant), icone('message'), icone('horloge'), msgs))
    debut = vue_html.index('>') + 1
    tete = vue_html[:debut].replace('class="vue', 'class="vue avec-chatter', 1)
    return tete + vue_html[debut:-len('</div>')] + panneau + '</div>'


def vue_pivot(identifiant, titre, facette, entetes, lignes, total, initiale=False, sous_lignes=None):
    """Une vue pivot d'Odoo : ``entetes`` = lignes d'en-tête déjà composées
    (``<tr>…</tr>``), ``lignes`` = [(libellé, [valeurs])], ``total`` =
    [valeurs]. Les lignes portent ``<id>-<n>``, le total ``<id>-tot``."""
    corps = ''.join('<tr id="%s-%d"><td class="r n2">⊞ %s</td>%s</tr>'
                    % (identifiant, i, e(lib), ''.join('<td>%s</td>' % v for v in vals))
                    for i, (lib, vals) in enumerate(lignes))
    tot = '<tr class="tot" id="%s-tot"><td class="r">⊟ Total</td>%s</tr>' % (
        identifiant, ''.join('<td>%s</td>' % v for v in total))
    barre = ('<div class="pv-barre"><span class="bt primaire">Mesures ▾</span><span class="bt gris">⇄</span>'
             '<span class="bt gris">✥</span><span class="bt gris" id="%s-export">%s</span></div>'
             % (identifiant, icone('document')))
    tete = ('<div class="cp"><div class="fil"><span class="ref" style="font-size:24px">%s</span></div>%s'
            '<span class="pager"></span></div>' % (e(titre), recherche([(None, facette)] if facette else [])))
    return _vue(identifiant, initiale, '<div class="fond-gris">%s%s<table class="pv">%s%s%s</table></div>'
                % (tete, barre, entetes, tot, corps))


def vue_gantt(identifiant, titre, jours, lignes, echelle='Semaine', periode='', initiale=False, facettes=()):
    """La vue Gantt d'Odoo 18 Enterprise : ``jours`` = libellés des colonnes,
    ``lignes`` = [(ressource, [(identifiant, début, durée, libellé, couleur)])],
    début et durée en colonnes (demi-colonnes permises)."""
    n = len(jours)
    tete = ''.join('<span>%s</span>' % e(j) for j in jours)
    rangs = []
    for nom, barres in lignes:
        b = ''.join('<span class="gt-b" id="%s" style="left:calc(%s * 100%% / %d + 3px);width:calc(%s * 100%% / %d - 6px);'
                    'background:%s"><span class="ell">%s</span></span>' % (i, d, n, l, n, c, e(t)) for i, d, l, t, c in barres)
        rangs.append('<div class="gt-l"><span class="gt-n ell">%s</span><div class="gt-p" style="background-size:calc(100%% / %d) 100%%">%s</div></div>'
                     % (e(nom), n, b))
    barre = ('<div class="gt-barre"><span class="bt gris">←</span><span class="bt gris">Aujourd\'hui</span>'
             '<span class="bt gris">→</span><span class="gt-periode">%s</span><span class="gt-echelles">%s</span></div>'
             % (e(periode), ''.join('<span class="bt%s">%s</span>' % (' actif' if x == echelle else ' gris', x)
                                     for x in ('Jour', 'Semaine', 'Mois'))))
    cp = '<div class="cp"><span class="bt primaire">Nouveau</span><span class="titre">%s</span>%s</div>' % (
        e(titre), recherche(list(facettes)))
    grille = ('<div class="gt"><div class="gt-l gt-tete"><span class="gt-n"></span><div class="gt-jours" '
              'style="grid-template-columns:repeat(%d,1fr)">%s</div></div>%s</div>' % (n, tete, ''.join(rangs)))
    return _vue(identifiant, initiale, '<div class="fond-gris">%s%s%s</div>' % (cp, barre, grille))


# -- le point de vente d'Odoo 18 (interface plein écran, sans la barre MuK) --

def fenetre_pos(identifiant, vues, caissier, numero='801', calques=''):
    """L'interface du point de vente : barre du haut (nouvelle commande,
    numéro, recherche, caissier, menu), puis les vues empilées."""
    return ('<div class="app pos" id="%s"><div class="pos-haut"><span class="pos-plus">%s</span><span class="pos-num">%s</span>'
            '<span class="pos-cherche">%sRechercher des produits...</span><span class="pos-caissier"><span class="avatar" '
            'style="background:#185FA5">%s</span>%s</span><span class="pos-menu">☰</span></div>'
            '<div class="pos-corps">%s</div>%s</div>'
            % (identifiant, ICONES['plus'], e(numero), icone('loupe'), e(caissier[0]), e(caissier), ''.join(vues), calques))


def pos_produits(identifiant, categories, produits, lignes, total, taxes, initiale=False):
    """L'écran de vente : le ticket à gauche (``lignes`` = [(id, article,
    quantité, prix unitaire, montant)]), le pavé, les catégories et les
    tuiles produits (``produits`` = [(id, nom, couleur)])."""
    tick = ''.join('<div class="pv-ligne" id="%s"><div class="a"><b>%s</b><span>%s</span></div>'
                   '<div class="q"><b>%s</b> x %s / Unités</div></div>' % (i, e(a), e(m), e(q), e(p))
                   for i, a, q, p, m in lignes)
    pave = ''.join('<span class="pk%s">%s</span>' % (c, e(t)) for t, c in (
        ('1', ''), ('2', ''), ('3', ''), ('Qté', ' sel'), ('4', ''), ('5', ''), ('6', ''), ('%', ' gr'), ('7', ''),
        ('8', ''), ('9', ''), ('Prix', ' gr'), ('+/-', ' jaune'), ('0', ''), (',', ' rose'), ('⌫', ' rouge')))
    gauche = ('<div class="pos-g"><div class="pos-ticket" id="%s-ticket">%s</div><div class="pos-tot"><small>Taxes'
              '<span id="%s-taxes">%s</span></small><b>Total<span id="%s-total">%s</span></b></div>'
              '<div class="pos-acts"><span>Client</span><span>Note interne</span><span class="dr">Actions</span></div>'
              '<div class="pos-pave">%s</div><div class="pos-payer" id="%s-payer">Paiement</div></div>'
              % (identifiant, tick, identifiant, e(taxes), identifiant, e(total), pave, identifiant))
    cats = ''.join('<span class="pos-cat" style="background:%s">%s</span>' % (c, e(n)) for n, c in categories)
    tuiles = ''.join('<span class="pos-tuile" id="%s" style="background:%s">%s</span>' % (i, c, e(n))
                     for i, n, c in produits)
    droite = '<div class="pos-d"><div class="pos-cats">%s</div><div class="pos-tuiles">%s</div></div>' % (cats, tuiles)
    return _vue(identifiant, initiale, '<div class="pos-vente">%s%s</div>' % (gauche, droite))


def pos_paiement(identifiant, modes, total, ardoise=True, initiale=False):
    """L'écran de paiement : les modes (``modes`` = [(id, libellé)]), Client /
    Facture, « Mettre sur ardoise » (aite_pos_credit), le pavé, et à droite le
    montant dû, « Restant » et les lignes de paiement (``<id>-lignes``)."""
    m = ''.join('<div class="pos-mode" id="%s">%s<span>%s</span></div>' % (i, icone('carte'), e(l)) for i, l in modes)
    pave = ''.join('<span class="pk%s">%s</span>' % (c, e(t)) for t, c in (
        ('1', ''), ('2', ''), ('3', ''), ('+10', ' vert'), ('4', ''), ('5', ''), ('6', ''), ('+20', ' vert'), ('7', ''),
        ('8', ''), ('9', ''), ('+50', ' vert'), ('+/-', ' jaune'), ('0', ''), (',', ' rose'), ('⌫', ' rouge')))
    ard = '<div class="pos-ardoise" id="%s-ardoise">%sMettre sur ardoise</div>' % (identifiant, icone('cahier')) if ardoise else ''
    gauche = ('<div class="pos-g"><div class="pos-modes">%s</div><div class="pos-cf"><span id="%s-client">%sClient</span>'
              '<span>%sFacture<i></i></span></div>%s<div class="pos-pave">%s</div>'
              '<div class="pos-rv"><span>Retour</span><span class="v" id="%s-valider">Valider</span></div></div>'
              % (m, identifiant, icone('personne'), icone('document'), ard, pave, identifiant))
    droite = ('<div class="pos-d pos-pd"><div class="pos-du" id="%s-du">%s</div><div class="pos-zone">'
              '<div class="pos-restant" id="%s-restant"><span>Restant</span><span id="%s-reste">%s</span></div>'
              '<div id="%s-lignes"></div></div></div>' % (identifiant, e(total), identifiant, identifiant, e(total), identifiant))
    return _vue(identifiant, initiale, '<div class="pos-vente">%s%s</div>' % (gauche, droite))


def pos_ligne_paiement(identifiant, mode, montant):
    """Une ligne de paiement de l'écran de paiement, masquée au départ."""
    return ('<div class="pos-pl masque" id="%s"><span>%s</span><span>%s</span><span class="x">×</span></div>'
            % (identifiant, e(mode), e(montant)))


# =========================================================================
# La caisse du restaurant (tutoriels 16 à 23 : aite_pos_restaurant, lot 1)
# =========================================================================
# Un restaurant SANS hôtel (aite_pos_restaurant ne dépend pas du socle :
# __manifest__.py:119, 126) : la caisse plein écran au service à table
# contrôlé, puis les écrans de gestion du thème MuK qui la règlent. Les
# libellés de la caisse sont ceux de ``static/src/utils/messages.js``
# (recopiés ci-dessous, espace insécable comprise) et des gabarits
# ``static/src/**/*.xml`` ; les couleurs, celles de ``scss/restaurant.scss``
# et d'Odoo 18 (``point_of_sale``, ``pos_restaurant``, ``web``). Les captures
# ``captures/restaurant/*.jpg`` n'ont servi que de modèle visuel. Abréviations
# des sources : R/ = addons/aite_pos_restaurant/, S/ = R/static/src/,
# O/ = ../odoo18/addons/.
#
# Échelle : la caisse occupe 1720 × 796 px du navigateur des tutoriels, soit
# 1,34 fois la tablette de 1 280 × 800 points des captures en largeur ; en
# hauteur, le plan est tassé (``resto_plan``). Les composants posés sur la
# caisse (fenêtres, menu, notifications) passent par ``superpose``.
# Les styles sont dans ``shared/aite-marketing.css``, section « caisse du
# restaurant », sous ``.resto`` (classes rs-*), et « réglages » (rg-*).

import base64 as _base64
import colorsys as _colorsys
import os as _os

ESP = ' '      # espace insécable de messages.js:12, avant « : » et « ? »


def nombre_resto(quantite):
    """« 2 », « 1,5 » : ``nombre`` de S/utils/messages.js:15-18."""
    n = float(quantite or 0)
    return str(int(n)) if n == int(n) else ('%g' % round(n, 3)).replace('.', ',')


def duree_resto(minutes):
    """« 35 min » ; à partir d'une heure, « 1 h 05 » (``TEXTES.duree``, messages.js:165-171)."""
    if minutes < 60:
        return '%d min' % minutes
    return '%d h %02d' % (minutes // 60, minutes % 60)


# Les textes de la caisse, mot pour mot (S/utils/messages.js:20-172).
MESSAGES_RESTO = {
    'R1': "Code inconnu. Retapez votre code.",
    'R3': "La caisse n'est pas encore ouverte. La caissière ou un chef de salle doit l'ouvrir avec son code.",
    'R5': "Il faut au moins une personne à table.",
    'R4': lambda table, nom: ("Table %s%s: c'est la table de %s. Seuls %s, la caissière ou un chef de salle "
                              "peuvent la modifier." % (table, ESP, nom, nom)),
    'R10': "Vous ne pouvez pas encaisser. Appelez la caissière%s: elle tapera son code ici." % ESP,
    'R13': "Seul un chef de salle ou le manager ferme la caisse.",
    'R14': ("L'écart de caisse dépasse le maximum autorisé%s: seul le manager peut fermer. Recomptez, ou appelez "
            "le manager." % ESP),
    'R15': "Seul un chef de salle ou le manager peut sortir ou entrer des espèces.",
    'R16': "Seul le manager peut rembourser une addition payée.",
    'R21': "Seuls la caissière, le chef de salle et le manager impriment le rapport des ventes.",
    'R8': "Ce code ne peut pas annuler. Il faut celui d'un chef de salle, d'un superviseur ou du manager.",
    'R9': lambda q, produit: ("Déjà envoyé%s: %s %s. Pour l'annuler, un chef de salle tape son code."
                              % (ESP, nombre_resto(q), produit)),
    'R24': "Écrivez en quelques mots pourquoi.",
    'R11': lambda produit: ("Plus de %s en stock. Si la bouteille est bien là, demandez au manager d'enregistrer "
                            "l'entrée de stock%s: la vente repassera aussitôt." % (produit, ESP)),
}
TITRES_RESTO = {
    'table': lambda n: 'Table %s — votre%scode' % (n, ESP),
    'ouvrir': 'Votre code pour ouvrir la caisse',
    'encaisser': 'Code de la personne qui encaisse',
    'fermer': 'Votre code pour fermer la caisse',
    'especes': "Votre code — entrée ou sortie d'espèces",
    'commandes': 'Votre code — liste des commandes',
    'rapport': 'Votre code — rapport des ventes',
    'prendreLaMain': 'Qui prend la main%s? Tapez votre code' % ESP,
    'personnes': lambda n: 'Table %s — combien de personnes%s?' % (n, ESP),
    'annulerProduit': lambda produit, table: 'Annuler %s — table %s' % (produit, table),
    'annulerTable': lambda table: 'Annuler la table %s' % table,
    'annulerTables': lambda liste: 'Annuler les tables encore ouvertes%s: %s' % (ESP, liste),
    'fermerLaCaisse': 'Fermer la caisse',
    'produitEpuise': 'Produit épuisé',
}
TEXTES_RESTO = {
    'planEtat': 'Touchez une table, puis tapez votre code.',
    'caisseFermee': "La caisse est fermée. La caissière ou un chef de salle tape son code pour l'ouvrir.",
    'ouvrirLaCaisse': 'Ouvrir la caisse',
    'neSaitPasEncaisser': lambda nom: '%s ne peut pas encaisser%s: la caissière tape son code ici.' % (nom, ESP),
    'envoye': lambda compte: 'Envoyé%s: %s.' % (ESP, compte),
    'retour': 'Retour',
    'neufEtPlus': '9 et plus',
    'valider': 'Valider',
    'personnes': lambda n: '%d personne' % n if n in (0, 1) else '%d personnes' % n,
    'addition': 'Addition',
    'diviser': "Diviser l'addition",
    'deplacer': 'Déplacer ou réunir',
    'annulerLaTable': 'Annuler la table',
    'creerLaPart': "Créer l'addition à part",
    'table': lambda n: 'Table %s' % n,
    'ouvertePar': lambda nom: 'ouverte par %s' % nom,
    'dejaEnvoye': lambda q: 'Déjà envoyé%s: %s.' % (ESP, nombre_resto(q)),
    'dejaEnvoyeListe': lambda liste: 'Déjà envoyé%s: %s' % (ESP, liste),
    'envoi': lambda q, produit: '%s %s' % (nombre_resto(q), produit),
    'combien': 'Combien%s?' % ESP,
    'tout': lambda q: '%s (tout)' % nombre_resto(q),
    'codeChef': "Code d'un chef de salle",
    'pourquoi': 'Pourquoi%s?' % ESP,
    'precision': 'Précision',
    'annulationFaite': lambda q, produit, nom: 'Annulation faite%s: %s %s, par %s.' % (ESP, nombre_resto(q), produit, nom),
    'bonEnvoye': "Bon d'annulation envoyé.",
    'tablesOuvertes': lambda k, liste: (
        '1 table est encore ouverte%s: %s. Encaissez-la, ou annulez-la avec un motif, avant de fermer.' % (ESP, liste)
        if k == 1 else '%d tables sont encore ouvertes%s: %s. Encaissez-les, ou annulez-les avec un motif, avant de '
                       'fermer.' % (k, ESP, liste)),
    'voirLesTables': 'Voir les tables',
    'annulerCesTables': 'Annuler ces tables',
    'especes': "Entrée ou sortie d'espèces",
    'mouvementsEspeces': "Entrées et sorties d'espèces",
    'commandes': lambda n: '%d commandes%s:' % (n, ESP) if n > 1 else '%d commande%s:' % (n, ESP),
    'legendeParties': lambda delai: [('libre', 'Gris%s: libre' % ESP), ('vert', 'Vert%s: ouverte' % ESP),
                                     ('orange', "Orange%s: ouverte depuis plus de %s%smin, proposez l'addition"
                                      % (ESP, delai, ESP)),
                                     ('pastille', 'Pastille rouge%s: pas encore envoyé' % ESP)],
}


def etat_commande(table, nom, minutes):
    """La phrase d'état de l'écran de commande : « Table 4 · ouverte par Loïc · 0 min »
    (S/store/pos_store.js:1136-1150 ; TEXTES.table, ouvertePar, duree)."""
    return ' · '.join((TEXTES_RESTO['table'](table), TEXTES_RESTO['ouvertePar'](nom), duree_resto(minutes)))


assert (TITRES_RESTO['table'](4), TEXTES_RESTO['envoye']('2 Pizzas, 2 Bière'), duree_resto(65), duree_resto(35),
        TEXTES_RESTO['commandes'](1), etat_commande(4, 'Loïc', 0)) == (
    'Table 4 — votre code', 'Envoyé : 2 Pizzas, 2 Bière.', '1 h 05', '35 min', '1 commande :',
    'Table 4 · ouverte par Loïc · 0 min')

# Les couleurs d'Odoo (O/web/static/src/scss/secondary_variables.scss:8-9, $o-colors), éclaircies comme
# .o_colorlist_item_color_N (O/web/static/src/core/colorlist/colorlist.scss:14-21 : +25 % de luminosité,
# +15 % de saturation ; texte −40 % / −15 %) et ..._transparent_N (O/point_of_sale/static/src/scss/pos.scss:
# 166-172 : +28 %) : les familles et les tuiles de l'écran de commande.
COULEURS_ODOO = ('#a2a2a2', '#ee2d2d', '#dc8534', '#e8bb1d', '#5794dd', '#9f628f', '#db8865', '#41a9a2', '#304be0',
                 '#ee2f8a', '#61c36e', '#9872e6')


def _ajuster(hexa, dl, ds):
    """``adjust-color($c, $lightness: dl, $saturation: ds)`` de Sass (HSL, bornes 0-100 %)."""
    r, g, b = [int(hexa[i:i + 2], 16) / 255.0 for i in (1, 3, 5)]
    h, l, s = _colorsys.rgb_to_hls(r, g, b)
    r, g, b = _colorsys.hls_to_rgb(h, min(1.0, max(0.0, l + dl)), min(1.0, max(0.0, s + ds)))
    return '#%02X%02X%02X' % tuple(int(round(x * 255)) for x in (r, g, b))


def couleur_odoo(n, transparent=False):
    """(fond, texte) d'une couleur d'Odoo 1-11 ; ``transparent`` : la teinte des tuiles et des familles
    ni choisies ni enfants. ``n`` = 0 (sans couleur) : None."""
    if not n:
        return None
    base = COULEURS_ODOO[n]
    return _ajuster(base, 0.28 if transparent else 0.25, 0.15), _ajuster(base, -0.40, -0.15)


assert couleur_odoo(8) == ('#97A6F9', '#0E1436') and couleur_odoo(8, True)[0] == '#A5B2FA'

# Les couleurs du plan (S/scss/restaurant.scss:110-126 ; fond de salle rgb(249,250,251) :
# O/pos_restaurant/models/pos_restaurant.py:18 ; darken(…, 12 %) calculé).
PLAN_LIBRE, PLAN_VERT, PLAN_ORANGE = 'rgba(0,0,0,.125)', '#35D374', '#FF9800'

ICONES.update({
    'codebarres': '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M2 4h1.6v16H2zM4.6 4h.8v16h-.8zM6.6 4h1.6v16H6.6zM9.4 4h.8v16h-.8zM11.2 4h.8v16h-.8zM13.2 4h1.6v16h-1.6zM16 4h.8v16H16zM17.8 4h.8v16h-.8zM19.6 4h.8v16h-.8zM21.4 4h.6v16h-.6z"/></svg>',
    'burger': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"><path d="M4 6h16M4 12h16M4 18h16"/></svg>',
    'effacer': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"><path d="M8.5 5H21v14H8.5L2.5 12z"/><path d="M11.5 9l6 6M17.5 9l-6 6"/></svg>',
    'panier': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round" stroke-linecap="round"><path d="M2.5 4h3l2.4 10.5h10.6L21 7H7"/><circle cx="9.5" cy="19" r="1.6"/><circle cx="17.5" cy="19" r="1.6"/></svg>',
    'telecharger': '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M10.5 3h3v8h3.5L12 16.5 7 11h3.5z"/><path d="M3 15h3v3h12v-3h3v6H3z"/></svg>',
    'copier': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><rect x="8" y="8" width="12" height="12" rx="1.5"/><path d="M16 8V5.5A1.5 1.5 0 0014.5 4h-9A1.5 1.5 0 004 5.5v9A1.5 1.5 0 005.5 16H8"/></svg>',
    'billets': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="2.5" y="6" width="19" height="12" rx="1.5"/><circle cx="12" cy="12" r="2.6"/><path d="M5.5 9v6M18.5 9v6"/></svg>',
    'croix': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M5 5l14 14M19 5L5 19"/></svg>',
    'croix-pleine': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3.4" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg>',
    'info': '<svg viewBox="0 0 8 16" fill="#fff"><circle cx="4" cy="2.4" r="1.9"/><path d="M1.2 6h4.3v7.6H7V16H1v-2.4h1.5V8.4H1.2z"/></svg>',
    'triangle': '<svg viewBox="0 0 10 10" fill="currentColor"><path d="M3 1.5l4.5 3.5L3 8.5z"/></svg>',
    'fleche-droite': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M4 12h15M13 6l6 6-6 6"/></svg>',
    'nuage': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"><path d="M7 18.5H6a4 4 0 01-.6-7.95A6 6 0 0117 8.6a4.5 4.5 0 01.5 8.9H17"/><path d="M12 12v8M9 15l3-3 3 3"/></svg>',
    'engrenage': '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M10.3 2h3.4l.5 2.6 1.9.8 2.2-1.5 2.4 2.4-1.5 2.2.8 1.9 2.6.5v3.4l-2.6.5-.8 1.9 1.5 2.2-2.4 2.4-2.2-1.5-1.9.8-.5 2.6h-3.4l-.5-2.6-1.9-.8-2.2 1.5-2.4-2.4 1.5-2.2-.8-1.9L2 13.7v-3.4l2.6-.5.8-1.9-1.5-2.2 2.4-2.4 2.2 1.5 1.9-.8zM12 8.5a3.5 3.5 0 100 7 3.5 3.5 0 000-7z"/></svg>',
    'poignee': '<svg viewBox="0 0 24 24" fill="currentColor"><circle cx="9" cy="6" r="1.6"/><circle cx="15" cy="6" r="1.6"/><circle cx="9" cy="12" r="1.6"/><circle cx="15" cy="12" r="1.6"/><circle cx="9" cy="18" r="1.6"/><circle cx="15" cy="18" r="1.6"/></svg>',
    'contacts': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><rect x="2" y="4.5" width="20" height="15" rx="1.5"/><circle cx="8" cy="11" r="2.4"/><path d="M4.5 17c.5-2 1.9-3 3.5-3s3 1 3.5 3M14 9h5M14 12h5M14 15h3"/></svg>',
    # la fenêtre « Actions » et le panneau d'une liste (repris de t19)
    'note': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"><path d="M4 4h16v10l-6 6H4z"/><path d="M14 20v-6h6"/></svg>',
    'vue-liste': '<svg viewBox="0 0 24 24" fill="currentColor"><rect x="3" y="5" width="18" height="2.4"/><rect x="3" y="10.8" width="18" height="2.4"/><rect x="3" y="16.6" width="18" height="2.4"/></svg>',
    'vue-pivot': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3" y="4" width="18" height="16"/><path d="M3 9h18M3 14.5h18M9 4v16M15 4v16"/></svg>',
    'vue-graphe': '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M3 20V9l5 4 4-7 5 5 4-3v12z"/></svg>',
    'colonnes': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M4 8h16M4 16h16"/><circle cx="15" cy="8" r="2.2" fill="#fff"/><circle cx="9" cy="16" r="2.2" fill="#fff"/></svg>',
})

# Les applications de la base « restaurant seul » (aite_resto), et ce que chaque compte voit dans la barre
# (relevé en lecture sur la base, ir_ui_menu et res_groups_users_rel, le 15/11/2026) : Discussion (5), Restaurant
# (31), Tableaux de bord (37), POS Crédit (46), Point de Vente (50), Facturation (55), Inventaire (140), Employés
# (185), Apps (500), Paramètres (550). « Tracker de liens » (base.group_no_one, mode développeur) et « Tests »
# (module de test de la base de développement) ne paraissent pas sur une base livrée. « Restaurant » a une
# icône « fa » (R/views/restaurant_menus.xml:9-11) : sans image, le thème MuK pose l'icône de base d'Odoo
# (muk_web_appsbar/static/src/webclient/appsbar/appsbar.xml:19-27 ; O/web/static/src/webclient/menus/
# menu_helpers.js:41-50).
APPS_MUK.update({'Restaurant': 'restaurant', 'Employés': 'employes'})
APPS_PROFIL.update({
    'resto_admin': ['Discussion', 'Restaurant', 'Tableaux de bord', 'POS Crédit', 'Point de Vente', 'Facturation',
                    'Inventaire', 'Employés', 'Apps', 'Paramètres'],
    'resto_manager': ['Discussion', 'Restaurant', 'Tableaux de bord', 'Point de Vente', 'Facturation', 'Inventaire',
                      'Employés', 'Apps'],
    'resto_chef': ['Discussion', 'Restaurant', 'Tableaux de bord', 'Employés', 'Apps'],
    'resto_caisse': ['Discussion', 'Tableaux de bord', 'Point de Vente', 'Facturation', 'Employés', 'Apps'],
})
# Les menus de la barre (même relevé) : « Restaurant » → « Annulations » (restaurant_menus.xml:12-14) ;
# « Employés » du manager (gestionnaire RH) : « Employés », « Départements », « Analyse », « Configuration »
# (« Annuaire » est retiré aux gestionnaires : O/hr/models/ir_ui_menu.py:9-13 ; capture 24).
MENUS_MUK.update({
    'restaurant': ['Annulations'],
    'employes': ['Employés', 'Départements', 'Analyse', 'Configuration'],
})
# Le menu « Analyse » du Point de Vente pour le manager du restaurant (point_of_sale ; « Personnes et tables » :
# R/views/restaurant_menus.xml:18-20) ; la section « Analyse AITE » : MENU_ANALYSE_AITE.
MENU_ANALYSE_RESTO = ['Commandes', 'Détails des ventes', 'Rapport de session', 'Personnes et tables']


def _odoo_dir():
    return _os.environ.get('ODOO_DIR', _os.path.abspath(_os.path.join(_os.path.dirname(__file__), '..', '..', '..',
                                                                         'odoo18')))


_IMAGES_ODOO = {}


def image_odoo(relatif):
    """Une image d'Odoo, jamais redessinée, en data: URI (lue au premier besoin)."""
    if relatif not in _IMAGES_ODOO:
        with open(_os.path.join(_odoo_dir(), relatif), 'rb') as f:
            _IMAGES_ODOO[relatif] = 'data:image/png;base64,' + _base64.b64encode(f.read()).decode()
    return _IMAGES_ODOO[relatif]


def superpose(html):
    """Une fenêtre posée sur la caisse : chacun de ses textes porte data-layout-allow-overlap, la superposition
    voulue que le contrôle de mise en page de HyperFrames attend sur le bloc de texte lui-même (comme
    scenarios/c3_bar_restaurant.py, ``superpose``)."""
    html = html.replace(' data-layout-allow-overlap', '')
    return _re.sub(r'<(div|span|b|p|em|i|small|label)(?=[\s>])', r'<\1 data-layout-allow-overlap', html)


# ------------------------------------------------ la caisse plein écran --

def fenetre_resto(ident, vues, calques='', ecran='plan', onglet='Table', employe=None, avatar='#185FA5',
                  cache=False):
    """La caisse du restaurant (O/point_of_sale/static/src/app/navbar/navbar.xml, O/pos_restaurant/…/navbar.xml:
    19-28, S/overrides/navbar.xml) : « Plan », l'onglet (« Table » sur le plan, le numéro ailleurs), le logo d'Odoo,
    puis à droite « Rechercher des produits… » et le code-barres (écran de commande seulement), l'employé identifié
    (personne tant que personne ne l'est, pas de cadenas), le menu ≡. Pas de « + » : la vente sans table est fermée
    d'office (S/overrides/order_tabs.xml:6-10).

    ``ecran`` : 'plan' | 'commande' | 'paiement' (classe sur-<ecran> du cadre, que le geste ``classe`` change) ;
    ``employe`` : (nom, initiale) affiché d'office, ou None (la classe avec-emp le montre ensuite, et les gestes
    ``texte`` posent son nom et son initiale dans <id>-emp-n et <id>-emp-av). Sans avec-emp, la case est cachée
    sans être retirée (visibility) : le moteur mesure les cibles au chargement, un anneau ou le curseur sur
    <id>-emp vise donc la case telle qu'elle est alors ; pour la désigner, poser d'office le nom le plus long que
    la vidéo y affichera, puis retirer avec-emp du HTML (comme t18). Identifiants : <id>-plan,
    <id>-onglet, <id>-cherche, <id>-cb, <id>-emp, <id>-menu ; le corps : <id>-corps."""
    nom, initiale = employe or ('', '')
    classes = 'app pos resto sur-%s%s%s' % (ecran, ' avec-emp' if employe else '', ' masque' if cache else '')
    return ('<div class="%s" id="%s"><div class="rs-haut">'
            '<span class="rs-plan" id="%s-plan">Plan</span><span class="rs-onglet" id="%s-onglet">%s</span>'
            '<i class="rs-sep"></i><img class="rs-logo" src="%s" alt="">'
            '<span class="rs-droite"><span class="rs-cherche" id="%s-cherche"><span class="ico">%s</span>'
            'Rechercher des produits…</span><span class="rs-cb" id="%s-cb">%s</span>'
            '<span class="rs-emp" id="%s-emp"><span class="avatar" id="%s-emp-av" style="background:%s">%s</span>'
            '<span class="rs-emp-n" id="%s-emp-n">%s</span></span>'
            '<span class="rs-menu" id="%s-menu">%s</span></span></div>'
            '<div class="rs-corps" id="%s-corps">%s</div>%s</div>'
            % (classes, ident, ident, ident, e(onglet), image_odoo('addons/web/static/img/logo.png'),
               ident, ICONES['loupe'], ident, ICONES['codebarres'], ident, ident, avatar, e(initiale), ident, e(nom),
               ident, ICONES['burger'], ident, ''.join(vues), calques))


# --------------------------------------------------------------- le plan --
# La salle du jeu d'essai (dev/seeds/seed_restaurant.py:52-75, disposition de la capture 03) : 3 rangées de 4,
# tables carrées de 120 × 120 (4 places), rondes de 110 × 110 (2 places), puis 9 et 10 de 160 × 120 (6 places),
# 11 et 12 de 120 × 120 ; x = 60 + 220 × colonne, y = 50 + 180 × rangée. Rejouée ×1,05 en largeur, tassée en
# hauteur pour tenir sous la fente du bandeau (``resto_plan``) : x = 63 + 231 c, y = 16 + 186 r.

def tables_salle(etats=None):
    """Les douze tables, prêtes pour ``resto_table`` : {numéro: (forme, x, y, l, h)} ; ``etats`` n'est pas lu ici."""
    salle = {}
    for i in range(12):
        n = i + 1
        rangee, colonne = divmod(i, 4)
        if rangee == 0:
            forme, l, h = 'carree', 126, 126
        elif rangee == 1:
            forme, l, h = 'ronde', 116, 116
        else:
            forme, l, h = ('carree', 168, 126) if n in (9, 10) else ('carree', 126, 126)
        salle[n] = (forme, 63 + 231 * colonne, 16 + 186 * rangee, l, h)
    return salle


def resto_table(ident, numero, forme='carree', x=0, y=0, l=126, h=126, etat='libre', duree='', pastille=None):
    """Une table du plan (O/pos_restaurant/static/src/app/floor_screen/floor_screen.xml:113-158 ; S/overrides/
    floor_screen.xml:31-44) : ``etat`` 'libre' | 'vert' | 'orange' (une classe, jamais un fondu) ; ``duree`` sous
    le numéro (« 35 min », « 1 h 05 », vide pour une table libre ; la classe avec-duree remonte le numéro,
    restaurant.scss:129-131) ; ``pastille`` : le nombre pas encore envoyé (cercle rouge en haut à droite), ou
    None. Identifiants : <id> (la table), <id>-n, <id>-d (durée, texte), <id>-p (pastille, classe « on »)."""
    return ('<div class="rs-table rs-%s %s%s" id="%s" style="left:%dpx;top:%dpx;width:%dpx;height:%dpx">'
            '<span class="rs-num" id="%s-n">%s</span><span class="rs-duree" id="%s-d">%s</span>'
            '<span class="rs-pastille%s" id="%s-p">%s</span></div>'
            % (forme, etat, ' avec-duree' if duree else '', ident, x, y, l, h, ident, e(numero), ident, e(duree),
               ' on' if pastille else '', ident, e(pastille or '')))


def resto_salle(prefixe, etats=None):
    """Les douze tables de la salle : ``etats`` = {numéro: (etat, durée, pastille)} ; les autres sont libres.
    Identifiants : <prefixe>-t1 … <prefixe>-t12."""
    etats = etats or {}
    html = []
    for n, (forme, x, y, l, h) in tables_salle().items():
        etat, duree, pastille = etats.get(n, ('libre', '', None))
        html.append(resto_table('%s-t%d' % (prefixe, n), n, forme, x, y, l, h, etat, duree, pastille))
    return ''.join(html)


def resto_plan(ident, tables, delai=60, salle='Salle', caisse_fermee=False, initiale=False, badge=None):
    """Le plan verrouillé, écran de repos de la caisse (O/pos_restaurant FloorScreen + S/overrides/
    floor_screen.xml) : le bouton de la salle (btn-outline-secondary actif, avec sa pastille rouge ``badge`` des
    articles pas encore envoyés : floor_screen.xml:10-17 ; dans Odoo 18, elle ne s'affiche jamais : le total
    additionne des objets {changes, skip}, floor_screen.js:896-907, ECARTS.md n° 94 ; laisser ``badge`` à None tant
    que ce n'est pas corrigé), puis la phrase d'état ou, caisse fermée, le bandeau
    jaune et « Ouvrir la caisse » (S/overrides/floor_screen.xml:21-28), la salle (``tables`` = HTML de
    ``resto_salle``) et la légende (:45-53). Pas de « Obtenir des codes QR » (restaurant.scss:39-41).

    Le bandeau et la phrase occupent la même fente (la salle ne bouge pas quand la caisse s'ouvre) : la classe
    ``ouverte`` de <id>-ecran montre la phrase et cache le bandeau. Identifiants : <id>-ecran, <id>-salle,
    <id>-salle-p, <id>-fermee, <id>-ouvrir, <id>-etat, <id>-carte, <id>-legende."""
    parties = ' · '.join('<span class="rs-leg-p"><i class="rs-leg-%s"></i>%s</span>' % (cle, e(texte))
                         for cle, texte in TEXTES_RESTO['legendeParties'](delai))
    return _vue(ident, initiale, (
        '<div class="rs-plan-ecran%s" id="%s-ecran">'
        '<div class="rs-salles"><span class="rs-salle actif" id="%s-salle">%s<b class="rs-badge%s" id="%s-salle-p">%s</b>'
        '</span></div><div class="rs-fente">'
        '<div class="rs-fermee" id="%s-fermee"><span>%s</span><span class="rs-bt-prim" id="%s-ouvrir">%s</span></div>'
        '<div class="rs-etat" id="%s-etat">%s</div></div>'
        '<div class="rs-carte" id="%s-carte">%s</div>'
        '<div class="rs-legende" id="%s-legende">%s</div></div>'
        % ('' if caisse_fermee else ' ouverte', ident, ident, e(salle), ' on' if badge else '', ident, e(badge or ''),
           ident, e(TEXTES_RESTO['caisseFermee']), ident, e(TEXTES_RESTO['ouvrirLaCaisse']),
           ident, e(TEXTES_RESTO['planEtat']), ident, tables, ident, parties)), classe='vue rs-vue')


# ------------------------------------------------ la fenêtre du code --

def _points(ident):
    return '<div class="rs-points">%s</div>' % ''.join('<i id="%s-p%d"></i>' % (ident, k) for k in range(4))


def _pave_code(ident, retour=True):
    """Le pavé 3 × 4 de la fenêtre du code (code_popup.xml:23-37) : 1-9, « Retour » (gris), 0, ⌫ ; sans
    « Retour », une case vide (annulation_popup.xml, étape du code)."""
    touches = ''.join('<span class="rs-k" id="%s-k%s">%s</span>' % (ident, c, c) for c in '123456789')
    gauche = ('<span class="rs-k rs-k-retour" id="%s-retour">%s</span>' % (ident, e(TEXTES_RESTO['retour']))
              if retour else '<span></span>')
    return ('<div class="rs-pave">%s%s<span class="rs-k" id="%s-k0">0</span><span class="rs-k rs-k-eff" id="%s-eff">'
            '%s</span></div>' % (touches, gauche, ident, ident, ICONES['effacer']))


def resto_code(ident, titre, sous_titre='', erreur='', personnes=False, haut=205):
    """La fenêtre du code (AiteCodePopup, S/components/code_popup/code_popup.xml:10-74 ; taille « sm »), posée
    sur un voile : titre, sous-titre (S/utils/messages.js : ``neSaitPasEncaisser``), quatre points, erreur (R1),
    pavé. Un seul « Retour », pas d'en-tête. Le code est validé seul au 4ᵉ chiffre ; le chiffre n'est jamais
    lisible, seuls les points se remplissent (classe ``plein`` sur <id>-p0 … <id>-p3).

    La fenêtre est faite d'une tête (le titre) et de panneaux empilés au même endroit, chacun avec son fond :
    la fenêtre a toujours la hauteur de l'étape affichée. ``personnes`` : l'étape des personnes (code_popup.xml:
    39-72), cachée : huit boutons 1-8 (primaires), « 9 et plus », « Retour » ; pour y passer :
    ``cacher('#<id>-code')``, ``montrer('#<id>-pers')`` et le titre par ``texte('#<id>-titre', …)``.
    ``erreur`` : la ligne d'erreur, réservée et cachée (``montrer('#<id>-err')``).
    ``haut`` : le haut de la fenêtre dans la caisse. 205 px (défaut) la pose sous la ligne de texte du bandeau
    « La caisse est fermée… » ou de la phrase d'état du plan, qui reste lisible en entier, comme sur la capture 01
    (haut de la fenêtre à 24 % de l'écran, sous le texte du bandeau, à 17-22 %), et au-dessus de la légende (la
    fenêtre du code fait 525 px : elle finit à 730 px dans un cadre de 796 px). Centrée comme dans Odoo, elle
    cacherait la phrase : la caisse de la vidéo est plus large que haute par rapport à la tablette.
    Identifiants : <id>-voile, <id>, <id>-titre, <id>-st, <id>-p0…3, <id>-err, <id>-k0…9, <id>-retour, <id>-eff,
    <id>-code, <id>-pers, <id>-n1…8, <id>-plus, <id>-pretour."""
    pers = ''
    if personnes:
        pers = ('<div class="rs-pan masque" id="%s-pers"><div class="rs-pers-b">%s</div>'
                '<span class="rs-k rs-k-large" id="%s-plus">%s</span>'
                '<span class="rs-k rs-k-retour rs-k-large" id="%s-pretour">%s</span></div>'
                % (ident, ''.join('<span class="rs-k rs-k-prim" id="%s-n%d">%d</span>' % (ident, k, k)
                                  for k in range(1, 9)),
                   ident, e(TEXTES_RESTO['neufEtPlus']), ident, e(TEXTES_RESTO['retour'])))
    st = '<div class="rs-st" id="%s-st">%s</div>' % (ident, e(sous_titre)) if sous_titre else ''
    err = '<div class="rs-err masque" id="%s-err">%s</div>' % (ident, e(erreur)) if erreur else ''
    corps = ('<div class="rs-fen-h"><div class="rs-titre" id="%s-titre">%s</div></div><div class="rs-pans">'
             '<div class="rs-pan" id="%s-code">%s%s%s%s</div>%s</div>'
             % (ident, e(titre), ident, st, _points(ident), err, _pave_code(ident), pers))
    return superpose('<div class="voile masque rs-voile" id="%s-voile"></div>'
                     '<div class="rs-fen rs-code masque" id="%s" style="top:%dpx">%s</div>' % (ident, ident, haut, corps))


# ------------------------------------------------- la notification --

def resto_notification(ident, texte, titre='', genre='info'):
    """La notification d'Odoo 18 en haut à droite de la caisse : barre de couleur à gauche (info #17A2B8,
    danger #DC3545 : O/web/static/src/scss/primary_variables.scss:85, 87), titre gras s'il y en a un, texte,
    croix de fermeture (captures 07, 09, 12). Geste : ``notifier(ident)``."""
    t = '<b>%s</b>' % e(titre) if titre else ''
    return superpose('<div class="rs-notif masque %s" id="%s"><div class="rs-notif-c">%s<span>%s</span></div>'
                     '<span class="rs-notif-x">%s</span></div>' % (genre, ident, t, e(texte), ICONES['croix']))


# ------------------------------------------- l'écran de commande --

def resto_familles(ident, arbre, chemin=()):
    """Les familles de l'écran de commande, comme ``getCategoriesAndSub`` (O/point_of_sale/static/src/app/screens/
    product_screen/product_screen.js:113-152) : les racines, et sous chaque famille du chemin choisi ses enfants, à
    plat. ``arbre`` = [(nom, couleur, enfants)] (une famille sans couleur hérite de son parent :
    O/point_of_sale/models/pos_category.py:67-81) ; ``chemin`` = noms choisis, de la racine à la famille active.
    Choisie ou enfant de la famille active (toutes les racines, sans chemin) : o_colorlist_item_color_N ; sinon,
    teinte « transparent » et opacité 50 % (category_selector.xml:6-10). Identifiants : <id>-f-<clé> (nom sans
    accent ni espace, en minuscules)."""
    boutons = []

    def cle(nom):
        import unicodedata
        return ''.join(c for c in unicodedata.normalize('NFD', nom.lower()) if c.isalnum())

    def parcourir(branches, profondeur, couleur_parent, parent_actif):
        for nom, couleur, enfants in branches:
            couleur = couleur or couleur_parent
            choisie = profondeur < len(chemin) and chemin[profondeur] == nom
            dans_chemin = nom in chemin[:len(chemin)]
            if chemin:
                enfant = parent_actif
            else:
                enfant = profondeur == 0
            if dans_chemin or enfant:
                fond, texte_ = couleur_odoo(couleur) or ('#F8F9FA', '#212529')
                classe_ = 'sel' if dans_chemin else 'enfant'
            else:
                fond, texte_ = couleur_odoo(couleur, True) or ('#F8F9FA', '#212529')
                classe_ = 'autre'
            boutons.append('<span class="rs-fam %s" id="%s-f-%s" style="background:%s;color:%s">%s</span>'
                           % (classe_, ident, cle(nom), fond, texte_, e(nom)))
            if choisie and enfants:
                actif = profondeur == len(chemin) - 1
                parcourir(enfants, profondeur + 1, couleur, actif)

    parcourir(arbre, 0, 0, not chemin)
    return '<div class="rs-familles" id="%s">%s</div>' % (ident, ''.join(boutons))


def resto_tuiles(ident, produits, qtes=None):
    """Les tuiles des produits (O/point_of_sale/static/src/app/generic_components/product_card/product_card.xml) :
    ``produits`` = [(clé, nom, couleur de la famille)], teinte « transparent » de la famille (product_screen.xml:35),
    pastille « i » ; ``qtes`` : {clé: quantité} à l'addition, en grand en bas à droite (cachée sinon : geste
    ``texte`` sur <id>-<clé>-q puis ``classe(…, ajouter=['on'])``). Identifiants : <id>-<clé>, <id>-<clé>-q."""
    qtes = qtes or {}
    tuiles = []
    for c, nom, couleur in produits:
        fond, texte_ = couleur_odoo(couleur, True) or ('#F8F9FA', '#212529')
        q = qtes.get(c)
        tuiles.append('<span class="rs-tuile" id="%s-%s" style="background:%s;color:%s"><i class="rs-info">%s</i>'
                      '<span class="rs-tuile-n">%s</span><b class="rs-tuile-q%s" id="%s-%s-q">%s</b></span>'
                      % (ident, c, fond, texte_, ICONES['info'], e(nom), ' on' if q else '', ident, c,
                         e(nombre_resto(q) if q else '')))
    return '<div class="rs-tuiles" id="%s">%s</div>' % (ident, ''.join(tuiles))


def resto_ligne(ident, article, qte, prix, envoyee=True, choisie=False, cache=False):
    """Une ligne de l'addition (O/point_of_sale/static/src/app/generic_components/orderline/orderline.xml) :
    l'article en gras et son montant ; dessous, la quantité encadrée « 2,00 » et « x 1 500 FCFA / Unité(s) ».
    Pas encore envoyée : une barre verte de 6 px à gauche (orderline.scss:24-39, $o-success #28A745 ; capture 06) ;
    la classe ``envoyee`` la retire. ``choisie`` : bordée de la couleur primaire. Identifiants : <id>, <id>-q
    (« 2,00 »), <id>-m (montant)."""
    return ('<div class="rs-ligne%s%s%s" id="%s"><div class="a"><b>%s</b><span id="%s-m">%s</span></div>'
            '<div class="q"><b id="%s-q">%s</b> x %s / Unité(s)</div></div>'
            % (' envoyee' if envoyee else '', ' choisie' if choisie else '', ' masque' if cache else '', ident,
               e(article), ident, e(fcfa(qte * prix)), ident, ('%.2f' % qte).replace('.', ','), e(fcfa(prix))))


TOUCHES_COMMANDE = (('1', ''), ('2', ''), ('3', ''), ('Qté', 'sel'), ('4', ''), ('5', ''), ('6', ''), ('%', 'gris'),
                    ('7', ''), ('8', ''), ('9', ''), ('Prix', 'gris'), ('+/-', 'jaune'), ('0', ''), (',', 'rose'),
                    ('⌫', 'rouge'))
TOUCHES_PAIEMENT = (('1', ''), ('2', ''), ('3', ''), ('+10', 'vert'), ('4', ''), ('5', ''), ('6', ''), ('+20', 'vert'),
                    ('7', ''), ('8', ''), ('9', ''), ('+50', 'vert'), ('+/-', 'jaune'), ('0', ''), (',', 'rose'),
                    ('⌫', 'rouge'))


def _code_touche(t):
    return {'+/-': 'pm', ',': 'v', '⌫': 'eff', 'Qté': 'q', '%': 'pc', 'Prix': 'px'}.get(t, t.replace('+', 'p'))


def resto_pave(ident, touches=TOUCHES_COMMANDE, prix_actif=False, cache=False):
    """Le pavé de l'écran de commande ou de paiement (O/point_of_sale/static/src/app/screens/product_screen/
    product_screen.js:153-170) : « Qté » choisi ; « % » grisé (remises désactivées par la case : R/models/
    pos_config.py:29) ; « Prix » grisé sauf pour le manager (``prix_actif`` ; product_screen.js:165-168,
    R/models/regles.py:46) ; « +/- » jaune, « , » rose, « ⌫ » rouge (teintes transparent_3, _6, _1).
    Identifiants : <id>-k1 … <id>-k9, <id>-k0, <id>-kq, <id>-kpc, <id>-kpx, <id>-kpm, <id>-kv, <id>-keff,
    <id>-kp10…"""
    ks = []
    for t, c in touches:
        if t == 'Prix' and prix_actif:
            c = ''
        contenu = ICONES['effacer'] if t == '⌫' else e(t)
        ks.append('<span class="rs-pk %s" id="%s-k%s">%s</span>' % (c, ident, _code_touche(t), contenu))
    return '<div class="rs-pave4%s" id="%s-pave">%s</div>' % (' masque' if cache else '', ident, ''.join(ks))


def resto_envoi(ident, compteurs=()):
    """« J'envoie » (S/overrides/actionpad_widget.xml:13-15 ; O/pos_restaurant/static/src/overrides/components/
    product_screen/actionpad_widget/actionpad_widget.xml:14-35) : en primaire avec, à droite, une ligne par famille
    « Pizzas [1] » quand il y a quelque chose à envoyer ; gris, inactif et centré sinon, sans compteurs
    (O/pos_restaurant/…/actionpad_widget.js:32-38 ; capture 09 ; la CSS le fait) ; au-delà de deux familles, le mot
    « J'envoie » laisse la place aux compteurs, sur deux colonnes. ``compteurs`` = [(famille, nombre)]. Les
    compteurs se changent par ``texte`` (<id>-env-<n>-v) et se montrent par la classe ``on`` ; la classe
    ``actif`` met le bouton en primaire."""
    cpts = ''.join('<span class="rs-cpt%s" id="%s-env-%d"><span id="%s-env-%d-f">%s</span><i id="%s-env-%d-v">%s</i>'
                   '</span>' % (' on' if n else '', ident, k, ident, k, e(f), ident, k, e(n or ''))
                   for k, (f, n) in enumerate(compteurs))
    actif = any(n for _f, n in compteurs)
    return ('<span class="rs-envoyer%s%s" id="%s-envoyer"><b class="rs-envoyer-t">J\'envoie</b>'
            '<span class="rs-cpts" id="%s-cpts">%s</span></span>'
            % (' actif' if actif else '', ' deux-col' if len([1 for _f, n in compteurs if n]) > 2 else '', ident, ident,
               cpts))


def resto_commande(ident, etat, lignes_html, total, personnes, familles_html, tuiles_html, compteurs=(),
                   encaisser=False, vide=False, initiale=False, addition=True, prix_actif=False, sans_ligne=False):
    """L'écran de commande (O/point_of_sale ProductScreen + O/pos_restaurant + S/overrides) : à gauche la phrase
    d'état (S/overrides/product_screen.xml:13-16 ; ``etat_commande``), l'addition (``lignes_html`` de
    ``resto_ligne``) et son total, la rangée « N personnes · Addition · Client · Note cuisine · Actions »
    (S/overrides/control_buttons.xml:17-34 ; « Addition » grisé sans ligne), le pavé, « J'envoie » et « J'encaisse »
    (primaire quand tout est envoyé : O/pos_restaurant/…/actionpad_widget.js:56-62 ; classe ``actif``) ; à droite
    les familles (``resto_familles``) et les tuiles (``resto_tuiles``).

    ``vide`` : l'addition sans ligne (O/point_of_sale/…/order_widget.xml:38-42 ; O/pos_restaurant/…/order_summary.xml
    :7-10) : panier, « Commencez à ajouter des produits », « Libérer la table » ; pavé et « J'encaisse » cachés
    (product_screen.xml:13-20). Pour passer au premier article : ``cacher('#<id>-vide')``, ``montrer`` la ligne,
    ``montrer('#<id>-pave')``, ``montrer('#<id>-tot')``, ``montrer('#<id>-encaisser')``.
    ``sans_ligne`` : l'addition rouverte, aucune ligne choisie (C/09) : pas de pavé (O/point_of_sale/…/
    product_screen.xml:13, ``t-if`` sur la ligne choisie) et « Note cuisine » grisé (O/point_of_sale/…/
    customer_note_button.xml:7) ; ``resto_visite`` enchaîne cet état et la même addition après le premier toucher.
    Pas de ligne « Taxes » : la société de démonstration est sans TVA (DESIGN.md).
    Identifiants : <id>-etat, <id>-ticket, <id>-vide, <id>-liberer, <id>-lignes, <id>-tot, <id>-total, <id>-pers,
    <id>-addition, <id>-client, <id>-note, <id>-actions, <id>-pave et ses touches, <id>-envoyer, <id>-env-<n>,
    <id>-encaisser."""
    vide_html = ('<div class="rs-vide%s" id="%s-vide"><span class="rs-panier">%s</span>'
                 '<span>Commencez à ajouter des produits</span>'
                 '<span class="rs-bt-prim rs-liberer" id="%s-liberer">Libérer la table</span></div>'
                 % ('' if vide else ' masque', ident, ICONES['panier'], ident))
    tot = ('<div class="rs-tot%s" id="%s-tot"><span>Total</span><span id="%s-total">%s</span></div>'
           % (' masque' if vide else '', ident, ident, e(total)))
    ctrl = ''.join('<span class="%s" id="%s-%s">%s</span>' % (c, ident, i, e(t)) for i, t, c in (
        ('pers', TEXTES_RESTO['personnes'](personnes), ''),
        ('addition', TEXTES_RESTO['addition'], 'gris' if vide else '') if addition else ('', '', 'absent'),
        ('client', 'Client', ''), ('note', 'Note cuisine', 'gris' if sans_ligne else ''), ('actions', 'Actions', 'dr'))
        if c != 'absent')
    gauche = ('<div class="rs-g"><div class="rs-cmd-etat" id="%s-etat">%s</div>'
              '<div class="rs-ticket" id="%s-ticket">%s<div class="rs-lignes" id="%s-lignes">%s</div>%s</div>'
              '<div class="rs-ctrl">%s</div>%s'
              '<div class="rs-act">%s<span class="rs-encaisser%s%s" id="%s-encaisser">J\'encaisse</span></div></div>'
              % (ident, e(etat), ident, vide_html, ident, lignes_html, tot, ctrl,
                 '' if sans_ligne else resto_pave(ident, prix_actif=prix_actif, cache=vide), resto_envoi(ident, compteurs),
                 ' actif' if encaisser else '', ' masque' if vide else '', ident))
    droite = '<div class="rs-d">%s%s</div>' % (familles_html, tuiles_html)
    return _vue(ident, initiale, '<div class="rs-cmd">%s%s</div>' % (gauche, droite), classe='vue rs-vue')


def typo_resto(texte):
    """Un texte à l'écran écrit par un scénario (pas la voix) : une espace insécable dans les guillemets et avant
    « : », « ; », « ? », pour qu'un signe ne passe pas seul à la ligne (comme S/utils/messages.js:7-9 ; la fonction
    ``_typo`` de t17 à t20)."""
    for avant, apres in (('« ', '«' + NBSP), (' »', NBSP + '»'), (' :', NBSP + ':'), (' ;', NBSP + ';'),
                         (' ?', NBSP + '?')):
        texte = texte.replace(avant, apres)
    return texte


def cle_resto(nom):
    """« Bière blonde 65 cl » → « biereblonde65cl » : la clé d'une famille ou d'un produit dans les identifiants
    (comme ``resto_familles``)."""
    import unicodedata
    return ''.join(c for c in unicodedata.normalize('NFD', nom.lower()) if c.isalnum())


def _tri_resto(nom):
    import unicodedata
    return ''.join(c for c in unicodedata.normalize('NFD', nom.casefold()) if unicodedata.category(c) != 'Mn')


def resto_produits(famille=None, carte=None, arbre=None):
    """Les tuiles d'une famille et de ses descendantes (O/point_of_sale/static/src/app/models/pos_category.js:7-16,
    getAllChildren), toute la carte sans ``famille``, prêtes pour ``resto_tuiles`` : [(clé, nom, couleur)]. Triées
    par nom comme la caisse (localeCompare, sans accent ni casse : O/point_of_sale/…/product_screen.js:417-419) ;
    la couleur est celle de la famille, ou de son parent (O/point_of_sale/models/pos_category.py:67-81).
    ``carte`` et ``arbre`` : demo.CARTE_RESTO et demo.FAMILLES_RESTO par défaut."""
    carte = demo.CARTE_RESTO if carte is None else carte
    arbre = demo.FAMILLES_RESTO if arbre is None else arbre
    couleur, descendantes = {}, {}

    def parcourir(branches, couleur_parent=0):
        noms = []
        for nom, c, enfants in branches:
            couleur[nom] = c or couleur_parent
            descendantes[nom] = [nom] + parcourir(enfants, couleur[nom])
            noms += descendantes[nom]
        return noms

    parcourir(arbre)
    famille_de = {x[0]: x[1] for x in carte}
    noms = [x[0] for x in carte if famille is None or famille_de[x[0]] in descendantes[famille]]
    return [(cle_resto(n), n, couleur[famille_de[n]]) for n in sorted(noms, key=_tri_resto)]


def resto_pile(ident, etats, visible=0, arbre=None):
    """Les états successifs des familles et des tuiles, empilés au même endroit (une grille d'une case), comme
    t17 : ``etats`` = [(chemin, famille des tuiles ou None, {clé: quantité})] ; on passe de l'un à l'autre par
    ``cacher`` / ``montrer`` (un toucher de famille = un état). Identifiants : <ident>-e<k>, <ident>-e<k>-fa-f-<clé>
    (familles), <ident>-e<k>-tu-<clé>(-q) (tuiles). À poser dans ``resto_commande(familles_html=…, tuiles_html='')``."""
    arbre = demo.FAMILLES_RESTO if arbre is None else arbre
    blocs = []
    for k, (chemin, famille, qtes) in enumerate(etats):
        blocs.append('<div class="rs-et%s" id="%s-e%d">%s%s</div>'
                     % ('' if k == visible else ' masque', ident, k,
                        resto_familles('%s-e%d-fa' % (ident, k), arbre, chemin),
                        resto_tuiles('%s-e%d-tu' % (ident, k), resto_produits(famille, arbre=arbre), qtes)))
    return '<div class="rs-pile">%s</div>' % ''.join(blocs)


def resto_visite(ident, avant, apres, familles_html='', tuiles_html='', initiale=False):
    """Une visite à une table : deux colonnes de gauche posées dans la même case de la grille (comme t17, t19,
    t20) — ``avant``, l'addition à l'arrivée, sans ligne choisie (arguments de ``resto_commande``, posée avec
    ``sans_ligne`` : pas de pavé, « Note cuisine » grisé ; avec ``vide``, « J'envoie » prend toute la rangée :
    O/pos_restaurant/…/actionpad_widget.xml:15-17) — et ``apres``, la même addition dès qu'un produit est touché
    (ligne choisie, pavé) ; à droite, les familles et les tuiles (``resto_pile`` par exemple).
    Pour passer de l'une à l'autre : ``cacher('#<id>v-g')``, ``montrer('#<id>-g')``. Identifiants : <id>v-…
    (avant), <id>-… (après), <id>v-g et <id>-g (les colonnes)."""
    b = resto_commande(ident, familles_html=familles_html, tuiles_html=tuiles_html, initiale=initiale, **apres)
    a = resto_commande(ident + 'v', familles_html='', tuiles_html='', sans_ligne=True, **avant)
    gauche_a = a[a.index('<div class="rs-g">'):a.index('<div class="rs-d">')]
    gauche_a = gauche_a.replace('<div class="rs-g">', '<div class="rs-g%s" id="%sv-g">'
                                % (' rs-g-vide' if avant.get('vide') else '', ident), 1)
    b = b.replace('<div class="rs-g">', '<div class="rs-g masque" id="%s-g">' % ident, 1)
    b = b.replace('<div class="rs-cmd">', '<div class="rs-cmd rs-visite">', 1)
    return b.replace('<div class="rs-d">', gauche_a + '<div class="rs-d">', 1)


# -------------------------------------------------- la fenêtre d'annulation --

def _retour_annulation(ident, cle):
    return ('<span class="rs-kb rs-k-retour rs-k-large rs-k-plein" id="%s-retour-%s">%s</span>'
            % (ident, cle, e(TEXTES_RESTO['retour'])))


def resto_motifs(ident, cle, motifs, choisi=None, precision=False, erreur='', cache=True):
    """L'étape « Pourquoi ? » de la fenêtre d'annulation (annulation_popup.xml:52-80), dans un des états que montre
    l'application : sans motif à précision touché, les motifs et « Retour » seulement (C/11, C/16) ; un motif à
    précision touché (``choisi`` = son rang, à partir de 1), le bouton en primaire, puis ``precision`` :
    « Précision », le champ et « Valider » (:64-73) ; après « Valider » sans rien écrire, ``erreur`` (R24) dessous
    (:74-75), qui reste jusqu'à la fermeture. Identifiants : <ident>-<cle> (le panneau), <ident>-<cle>-kbs,
    <ident>-<cle>-m1…, <ident>-<cle>-pc (le champ, avec -ph et -val pour le geste ``saisir``),
    <ident>-<cle>-valider, <ident>-<cle>-err, <ident>-retour-<cle>."""
    p = '%s-%s' % (ident, cle)
    boutons = ''.join('<span class="rs-kb rs-motif%s" id="%s-m%d">%s</span>' % (' choisi' if k == choisi else '', p, k,
                                                                               e(m))
                      for k, m in enumerate(motifs, 1))
    prec = ''
    if precision:
        prec = ('<div class="rs-prec"><label>%s</label><span class="rs-champ rs-champ-prec" id="%s-pc">'
                '<span id="%s-pc-ph"></span><span id="%s-pc-val"></span></span>'
                '<span class="rs-kb rs-k-prim rs-k-large" id="%s-valider">%s</span></div>'
                % (e(TEXTES_RESTO['precision']), p, p, p, p, e(TEXTES_RESTO['valider'])))
    err = '<div class="rs-err" id="%s-err">%s</div>' % (p, e(erreur)) if erreur else ''
    return ('<div class="rs-pan%s" id="%s"><div class="rs-question">%s</div><div class="rs-kbs" id="%s-kbs">%s</div>'
            '%s%s%s</div>' % (' masque' if cache else '', p, e(TEXTES_RESTO['pourquoi']), p, boutons, prec, err,
                              _retour_annulation(ident, cle)))


def resto_annulation(ident, titre, sous_titre='', quantites=(), motifs=(), code=True, precision=None, erreur='',
                     haut=96):
    """La fenêtre d'annulation (AiteAnnulationPopup, S/components/annulation_popup/annulation_popup.xml:7-82 ;
    taille « md »), reprise de t19 : une tête (titre ; sous-titre : R9 quand un chef de salle doit taper son code,
    ``dejaEnvoye`` / ``dejaEnvoyeListe`` sinon) et des étapes empilées au même endroit, chacune avec son fond et sa
    copie de « Retour » (le même bouton dans l'application, sous l'étape en cours) ; la première est visible, les
    autres cachées : on passe de l'une à l'autre par ``cacher`` / ``montrer``, la fenêtre prend la hauteur de
    l'étape affichée.

    Les étapes, dans l'ordre : « Combien ? » (<id>-q : un bouton primaire par quantité, le dernier « n (tout) » ;
    ``quantites`` = [1, 2, 3] ; seulement si plus d'une unité est partie), « Code d'un chef de salle » (<id>-c :
    points et pavé, sans « Retour » dans le pavé ; ``code``), « Pourquoi ? » (<id>-m : les ``motifs``,
    R/data/restaurant_motif_data.xml:8-28 ; aucun choisi) ; avec ``precision`` (le rang du motif qui demande une
    précision, « Autre » = 5), deux étapes de plus : <id>-mp (ce motif choisi, « Précision », le champ, « Valider »)
    et, avec ``erreur`` (R24), <id>-me (le même, R24 dessous). Le motif à précision ne laisse donc aucun blanc sous
    les motifs tant qu'il n'est pas touché (C/11, C/16 ; relecture de t19).
    Identifiants : <id>-voile, <id>, <id>-titre, <id>-st, <id>-q1…, <id>-p0…3, <id>-k0…9, <id>-eff, et ceux de
    ``resto_motifs`` (<id>-m-m1…, <id>-mp-pc, <id>-mp-valider, <id>-me-err…) ; « Retour » : <id>-retour-q, -c, -m,
    -mp, -me."""
    etapes = []
    if quantites:
        bq = ''.join('<span class="rs-kb rs-k-prim" id="%s-q%d">%s</span>'
                     % (ident, q, e(TEXTES_RESTO['tout'](q) if k == len(quantites) - 1 else nombre_resto(q)))
                     for k, q in enumerate(quantites))
        etapes.append('<div class="rs-pan%s" id="%s-q"><div class="rs-question">%s</div><div class="rs-kbs">%s</div>%s'
                      '</div>' % (' masque' if etapes else '', ident, e(TEXTES_RESTO['combien']), bq,
                                  _retour_annulation(ident, 'q')))
    if code:
        etapes.append('<div class="rs-pan%s" id="%s-c"><div class="rs-question">%s</div>%s%s%s</div>'
                      % (' masque' if etapes else '', ident, e(TEXTES_RESTO['codeChef']), _points(ident),
                         _pave_code(ident, retour=False), _retour_annulation(ident, 'c')))
    etapes.append(resto_motifs(ident, 'm', motifs, cache=bool(etapes)))
    if precision:
        etapes.append(resto_motifs(ident, 'mp', motifs, choisi=precision, precision=True))
        if erreur:
            etapes.append(resto_motifs(ident, 'me', motifs, choisi=precision, precision=True, erreur=erreur))
    st = '<div class="rs-st" id="%s-st">%s</div>' % (ident, e(sous_titre)) if sous_titre else ''
    corps = ('<div class="rs-fen-h"><div class="rs-titre" id="%s-titre">%s</div>%s</div><div class="rs-pans">%s</div>'
             % (ident, e(titre), st, ''.join(etapes)))
    return superpose('<div class="voile masque rs-voile" id="%s-voile"></div>'
                     '<div class="rs-fen rs-annul masque" id="%s" style="top:%dpx">%s</div>' % (ident, ident, haut, corps))


# ------------------------------------------------------ l'écran de paiement --
# Les icônes des modes, d'après celles d'Odoo (payment_screen.js:413-421) : espèces, banque.
ICO_ESPECES_POS = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round">'
                   '<rect x="2" y="4.5" width="13.5" height="8.5" rx="1"/><circle cx="8.75" cy="8.75" r="1.9"/>'
                   '<path d="M4.5 15h12.5V7.5"/><ellipse cx="18.5" cy="15.2" rx="3.5" ry="1.4"/>'
                   '<path d="M15 15.2v3.4c0 .8 1.6 1.4 3.5 1.4s3.5-.6 3.5-1.4v-3.4M15 16.9c0 .8 1.6 1.4 3.5 1.4s3.5-.6 '
                   '3.5-1.4"/></svg>')
ICO_BANQUE_POS = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round">'
                  '<rect x="2.5" y="4.5" width="19" height="15" rx="1"/><path d="M2.5 7.6h19M2.5 10.2h19"/>'
                  '<rect x="5" y="14.6" width="6.4" height="2.6" rx="1.3"/>'
                  '<path d="M17.4 13v6M18.7 14.2c-.3-.4-.7-.6-1.3-.6-.7 0-1.3.4-1.3 1s.6.9 1.3 1 1.3.4 1.3 1-.6 1-1.3 1'
                  'c-.6 0-1-.2-1.3-.6" stroke-linecap="round"/></svg>')


def resto_paiement(ident, du, modes=(('esp', 'Espèces', 'especes'), ('mm', 'Mobile Money', 'banque')), convives=0,
                   ligne_mode='Espèces', initiale=False):
    """L'écran de paiement de la caisse du restaurant (O/point_of_sale/…/payment_screen/payment_screen.xml ;
    capture 13) : les modes posés d'office (« Espèces », « Mobile Money » : R/models/pos_config.py:83-84), Client /
    Facture, le pavé (+10, +20, +50), « Retour » / « Valider » ; à droite le montant dû en vert (payment_screen.xml:
    63), « 1 500 FCFA / Convive » s'il y a plus d'une personne (O/pos_restaurant/static/src/overrides/components/
    payment_screen/payment_screen.xml:24-29 ; « / Convive » : O/pos_restaurant/i18n/fr.po:45-46), puis l'état
    « Restant » et la ligne de paiement. Ni « Mettre sur ardoise » ni « payer plus tard » : réservés au manager en
    mode restaurant (S/overrides/payment_screen.js ; notes de version :165-168 ; cas R101).

    États, empilés et cachés : <id>-msg (« Veuillez sélectionner un mode de paiement », visible au départ),
    <id>-du (« Restant » rouge, <id>-du-v), <id>-ok (« Restant 0 FCFA » vert), <id>-mon (« Monnaie », <id>-mon-v) ;
    la ligne <id>-pl (mode, <id>-pl-v). « Valider » reste pâle tant que le paiement n'est pas complet (classe
    ``off`` à retirer). Identifiants : <id>-<clé du mode>, <id>-client, <id>-facture, le pavé, <id>-retour,
    <id>-valider."""
    icones = {'especes': ICO_ESPECES_POS, 'banque': ICO_BANQUE_POS}
    m = ''.join('<div class="rs-mode" id="%s-%s"><span class="ico">%s</span><span>%s</span></div>'
                % (ident, c, icones.get(ic, ICO_BANQUE_POS), e(l)) for c, l, ic in modes)
    gauche = ('<div class="rs-g"><div class="rs-modes">%s</div><div class="rs-cf"><span id="%s-client"><span class="ico">'
              '%s</span>Client</span><span id="%s-facture"><span class="ico">%s</span>Facture<i></i></span></div>%s'
              '<div class="rs-rv"><span id="%s-retour">Retour</span><span class="v off" id="%s-valider" data-layout-ignore>'
              'Valider</span></div></div>'
              % (m, ident, ICONES['personne'], ident, ICONES['document'], resto_pave(ident, TOUCHES_PAIEMENT), ident,
                 ident))
    convive = ('<div class="rs-convive">%s / Convive</div>' % e(fcfa(round(du / float(convives)))) if convives > 1
               else '')
    droite = ('<div class="rs-pd"><div class="rs-du-bloc"><div class="rs-du-v" id="%s-dueg">%s</div>%s</div>'
              '<div class="rs-pzone"><div class="rs-choix" id="%s-msg">Veuillez sélectionner un mode de paiement</div>'
              '<div class="rs-etats"><div class="rs-stt rouge masque" id="%s-du"><span>Restant</span><b id="%s-du-v">%s</b>'
              '</div><div class="rs-stt vert masque" id="%s-ok"><span>Restant</span><b>%s</b></div>'
              '<div class="rs-stt vert masque" id="%s-mon"><span>Monnaie</span><b id="%s-mon-v">%s</b></div></div>'
              '<div class="rs-pl masque" id="%s-pl"><span>%s</span><span id="%s-pl-v">%s</span><span class="x">×</span>'
              '</div></div></div>'
              % (ident, e(fcfa(du)), convive, ident, ident, ident, e(fcfa(du)), ident, e(fcfa(0)), ident, ident,
                 e(fcfa(0)), ident, e(ligne_mode), ident, e(fcfa(du))))
    return _vue(ident, initiale, '<div class="rs-paie">%s%s</div>' % (gauche, droite), classe='vue rs-vue')


# ------------------------------------------------------------ le menu ≡ --

def resto_menu(ident, commandes=0, imprimante=False):
    """Le menu ≡ de la caisse au service à table contrôlé (O/point_of_sale/static/src/app/navbar/navbar.xml:34-72 ;
    S/overrides/navbar.xml:17-43) : « Commandes » (pastille du nombre, badge text-bg-info), « Entrée ou sortie
    d'espèces » (remplace « Cash In/Out »), « Imprimer le rapport » avec une imprimante seulement (navbar.xml:60-62),
    « Fermer la caisse » ; sans « Installer l'application », « Changer de vue de salle », cadenas ni « Backend »
    (caché tant que l'employé n'a pas le compte de la session : O/pos_hr/…/navbar.js:5-8). Recette R14.
    Identifiants : <id>, <id>-commandes, <id>-especes, <id>-rapport, <id>-fermer."""
    badge = '<b class="rs-menu-b">%d</b>' % commandes if commandes else ''
    rapport = '<div id="%s-rapport">Imprimer le rapport</div>' % ident if imprimante else ''
    return superpose('<div class="rs-menu-l masque" id="%s"><div id="%s-commandes">Commandes%s</div>'
                     '<div id="%s-especes">%s</div>%s<div id="%s-fermer">Fermer la caisse</div></div>'
                     % (ident, ident, badge, ident, e(TEXTES_RESTO['especes']), rapport, ident))


# -------------------------------------------- les fenêtres d'Odoo sur la caisse --

def _dialogue(ident, titre, corps, pied, largeur, haut, droite_titre='', classe_=''):
    return superpose('<div class="voile masque rs-voile" id="%s-voile"></div>'
                     '<div class="rs-dlg masque%s" id="%s" style="top:%dpx;width:%dpx;margin-left:-%dpx">'
                     '<div class="rs-dlg-h"><span>%s</span>%s</div><div class="rs-dlg-c" id="%s-c">%s</div>'
                     '<div class="rs-dlg-p">%s</div></div>'
                     % (ident, classe_, ident, haut, largeur, largeur // 2, e(titre), droite_titre, ident, corps, pied))


def actions_resto(notes_grises=True):
    """Les boutons de la fenêtre « Actions » d'une table, en mode restaurant, pour un serveur ou un chef de salle
    (relevés pour t19) : (clé, icône, libellé, grisé), dans l'ordre que posent O/point_of_sale/…/control_buttons/
    control_buttons.xml:20-45, O/pos_restaurant/static/src/app/control_buttons/control_buttons.xml:4-36 et
    S/overrides/control_buttons.xml:27-85 : « Note générale » (O/point_of_sale/i18n/fr.po:3290-3291), « Diviser
    l'addition », « Déplacer ou réunir » (messages.js:110-111), « Note au client » (fr.po:2432-2433), « Annuler la
    table » (messages.js:112). Les deux notes sont grisées sans ligne choisie (customer_note_button.xml:7). Ni
    « Remboursement » (manager seul : S/overrides/control_buttons.xml:28-30), ni « Taxe » (seulement avec des
    positions fiscales). Aucune capture de cette fenêtre."""
    return [('note', '', 'Note générale', notes_grises), ('diviser', ICONES['copier'], TEXTES_RESTO['diviser'], False),
            ('deplacer', ICONES['fleche-droite'], TEXTES_RESTO['deplacer'], False),
            ('client', ICONES['note'], 'Note au client', notes_grises),
            ('annuler', ICONES['corbeille'], TEXTES_RESTO['annulerLaTable'], False)]


def resto_actions(ident, boutons=None, haut=150, largeur=1072):
    """La fenêtre « Actions » d'Odoo (ControlButtonsPopup, taille « lg » : 800 points, ×1,34 ; titre :
    O/point_of_sale/…/control_buttons/control_buttons.js:139-145, fr.po:590-591), reprise de t19 : en-tête et croix,
    sans pied ; boutons btn-secondary btn-lg py-5 en trois colonnes (control_buttons.scss:1-2), grisés (opacité
    0,65). ``boutons`` = [(clé, icône SVG ou '', libellé, grisé)], ``actions_resto()`` par défaut. Geste :
    ``ouvrir(ident)``. Identifiants : <id>-voile, <id>, <id>-<clé>."""
    boutons = actions_resto() if boutons is None else boutons
    grille = '<div class="rs-act-g">%s</div>' % ''.join(
        '<span class="rs-act-b%s" id="%s-%s">%s<span>%s</span></span>'
        % (' off' if grise else '', ident, k, '<i class="rs-act-i">%s</i>' % ico if ico else '', e(lib))
        for k, ico, lib, grise in boutons)
    return _dialogue(ident, 'Actions', grille, '', largeur, haut, droite_titre='<span class="rs-x">%s</span>'
                     % ICONES['croix'], classe_=' rs-actions')


def resto_ouverture(ident, fond='0', haut=200):
    """« Contrôle à l'ouverture » (O/point_of_sale/static/src/app/store/opening_control_popup/
    opening_control_popup.xml:5-26 ; capture 02) : « Espèces à l'ouverture » (montant sans symbole, croix
    d'effacement, bouton billets : le solde compté à la dernière fermeture, opening_control_popup.js:29-32),
    « Note d'ouverture » et son texte indicatif, un seul bouton « J'ouvre la caisse » (S/overrides/
    opening_control_popup.xml:7-11 ; pas d'« Ignorer » avec la connexion par code : O/pos_hr/…/
    opening_control_popup.xml:4-6). Identifiants : <id>-voile, <id>, <id>-fond, <id>-ok."""
    corps = ('<div class="rs-lab">Espèces à l\'ouverture</div><div class="rs-in-l"><span class="rs-champ" id="%s-fond">'
             '<span>%s</span><span class="rs-x">%s</span></span><span class="rs-btn-ic">%s</span></div>'
             '<div class="rs-lab">Note d\'ouverture</div><div class="rs-zone-txt">Ajouter une note d\'ouverture...</div>'
             % (ident, e(fond), ICONES['croix-pleine'], ICONES['billets']))
    pied = '<span class="rs-bt rs-bt-p" id="%s-ok">J\'ouvre la caisse</span>' % ident
    return _dialogue(ident, "Contrôle à l'ouverture", corps, pied, 1060, haut)


def resto_fermeture(ident, nb_commandes, total, ouverture, especes, mouvements=0, compte=None, autres=(),
                    note='', haut=62):
    """« Fermeture de la caisse » avec les textes d'AITE (S/overrides/closing_popup.xml:12-37 ; capture 14) :
    « 1 commande : 6 000 FCFA » accordé ; le bloc Espèces (attendu, Ouverture, ▸ Paiements, ▸ Entrées et sorties
    d'espèces, Compté, Différence) ; un bloc par autre mode ``autres`` = [(nom, montant)] (▸ Paiements, Différence) ;
    « Comptage de caisse » (champ, billets, copier) ; un champ « <mode> Nombre » par mode de type banque qui a des
    paiements (O/point_of_sale, closing_popup.xml ; « Count » traduit « Nombre ») ; « Note de clôture » ; puis
    « Fermer la caisse », « Ignorer », « Entrée ou sortie d'espèces », « Ventes du jour ⤓ ». Le corps défile
    (<id>-defil, geste ``defiler``). ``compte`` : le montant compté (None : champ vide, différence = −attendu).
    Identifiants : <id>-voile, <id>, <id>-n, <id>-esp, <id>-compte, <id>-diff, <id>-diffl, <id>-in (champ,
    <id>-in-val), <id>-ok, <id>-ignorer, <id>-especes, <id>-ventes."""
    attendu = ouverture + especes + mouvements
    compte_v = attendu if compte is None else compte
    diff = compte_v - attendu if compte is not None else -attendu
    acc = '' if mouvements else ' off'
    blocs = ('<div class="rs-cl-b" id="%s-esp"><div class="rs-cl-t"><span>Espèces</span><span>%s</span></div>'
             '<div class="rs-cl-s"><span>Ouverture</span><span>%s</span></div>'
             '<div class="rs-cl-s fonce"><span><i class="rs-tri">%s</i>Paiements</span><span>+ %s</span></div>'
             '<div class="rs-cl-s fonce%s"><span><i class="rs-tri">%s</i>%s</span><span>+ %s</span></div>'
             '<div class="rs-cl-s"><span>Compté</span><span id="%s-compte">%s</span></div>'
             '<div class="rs-cl-s%s" id="%s-diffl"><span>Différence</span><span id="%s-diff">%s</span></div></div>'
             % (ident, e(fcfa(attendu)), e(fcfa(ouverture)), ICONES['triangle'], e(fcfa(especes)), acc, ICONES['triangle'],
                e(TEXTES_RESTO['mouvementsEspeces']), e(fcfa(mouvements)), ident,
                e(fcfa(compte_v if compte is not None else 0)), ' rouge' if diff else '', ident, ident, e(fcfa(diff))))
    for nom, montant in autres:
        blocs += ('<div class="rs-cl-b"><div class="rs-cl-t"><span>%s</span><span>%s</span></div>'
                  '<div class="rs-cl-s fonce%s"><span><i class="rs-tri">%s</i>Paiements</span><span>+ %s</span></div>'
                  '<div class="rs-cl-s"><span>Différence</span><span>%s</span></div></div>'
                  % (e(nom), e(fcfa(montant)), '' if montant else ' off', ICONES['triangle'], e(fcfa(montant)),
                     e(fcfa(0))))
    nombres = ''.join('<div class="rs-lab">%s Nombre</div><div class="rs-in-l"><span class="rs-champ rs-plein"><span>%s'
                      '</span><span class="rs-x">%s</span></span></div>' % (e(nom), e(entier(montant)),
                                                                              ICONES['croix-pleine'])
                      for nom, montant in autres if montant)
    comptage = ('<div class="rs-lab">Comptage de caisse</div><div class="rs-in-l"><span class="rs-champ rs-plein rs-saisie" '
                'id="%s-in"><span class="val" id="%s-in-val">%s</span><span class="rs-x">%s</span></span>'
                '<span class="rs-btn-ic">%s</span><span class="rs-btn-ic">%s</span></div>'
                % (ident, ident, e(str(compte)) if compte is not None else '', ICONES['croix-pleine'],
                   ICONES['billets'], ICONES['copier']))
    corps = ('<div class="rs-cl-defil" id="%s-defil">%s<hr>%s%s<div class="rs-lab">Note de clôture</div>'
             '<div class="rs-zone-txt">%s</div></div>'
             % (ident, blocs, comptage, nombres, e(note) if note else 'Ajouter une note de fermeture...'))
    pied = ('<span class="rs-bt rs-bt-p" id="%s-ok">Fermer la caisse</span><span class="rs-bt" id="%s-ignorer">Ignorer'
            '</span><span class="rs-bt rs-dr" id="%s-especes">%s</span><span class="rs-bt" id="%s-ventes">Ventes du jour'
            '<span class="ico">%s</span></span>'
            % (ident, ident, ident, e(TEXTES_RESTO['especes']), ident, ICONES['telecharger']))
    droite = '<b class="rs-cl-n" id="%s-n">%s %s</b>' % (ident, e(TEXTES_RESTO['commandes'](nb_commandes)), e(fcfa(total)))
    return _dialogue(ident, 'Fermeture de la caisse', corps, pied, 1060, haut, droite_titre=droite, classe_=' rs-clo')


def resto_confirmation(ident, titre, texte, ok, autre, haut=230, largeur=880):
    """La ConfirmationDialog d'Odoo posée sur la caisse (capture 15) : en-tête et croix, texte, bouton primaire,
    bouton gris. À la fermeture avec des tables ouvertes : ``TITRES_RESTO['fermerLaCaisse']``,
    ``TEXTES_RESTO['tablesOuvertes'](1, '12')``, « Voir les tables », « Annuler ces tables »
    (S/overrides/closing_popup.js:54-79). Identifiants : <id>-voile, <id>, <id>-ok, <id>-autre."""
    corps = '<p class="rs-conf">%s</p>' % e(texte)
    pied = ('<span class="rs-bt rs-bt-p" id="%s-ok">%s</span><span class="rs-bt" id="%s-autre">%s</span>'
            % (ident, e(ok), ident, e(autre)))
    return _dialogue(ident, titre, corps, pied, largeur, haut, droite_titre='<span class="rs-x">%s</span>' % ICONES['croix'])


# ------------------------------------------------- le rapport en PDF --

def visionneuse_pdf(ident, fichier, pages_html, pager='1 / 1'):
    """La visionneuse PDF du navigateur (comme scenarios/t06_registre.py) : barre sombre avec le nom du fichier et
    la page, puis les pages blanches (``pages_html``). Cachée ; ``montrer('#<id>')``. Le contenu défile :
    <id>-defil (geste ``defiler``)."""
    return superpose('<div class="rs-pdf masque" id="%s"><div class="rs-pdf-b"><span>%s</span><span class="rs-pdf-p">%s'
                     '</span></div><div class="rs-pdf-z"><div class="rs-pdf-pages" id="%s-defil">%s</div></div></div>'
                     % (ident, e(fichier), e(pager), ident, pages_html))


def rapport_section(titre, contenu, identifiant=None):
    """Une section du rapport de session d'Odoo (O/point_of_sale/views/pos_session_sales_details.xml) : un titre
    sur fond gris (h6 bg-secondary), puis son contenu."""
    return '<div class="rs-rp-s"%s><h6>%s</h6>%s</div>' % (_id(identifiant), e(titre), contenu)


def rapport_tables_annulations(tables, personnes, sans_table, annulations, ident='rp'):
    """Le bloc d'AITE du rapport de fermeture (R/views/report_saledetails.xml:11-80 ; capture 26) : « Tables et
    personnes » (« Nombre de tables », « Nombre de personnes », « Ventes sans table »), puis « Annulations » :
    colonnes « Table », « Produit », « Quantité », « Montant », « Motif », « Autorisée par » et une ligne « Total »
    (``annulations`` = [(table, produit, quantité, montant, motif, autorisée par ou '')]) ; sans annulation :
    « Aucune annulation sur cette période. ». Montants « 1 000 FCFA » (espace insécable, :52-57)."""
    tp = ''.join('<tr><td>%s</td><td class="d">%s</td></tr>' % (e(l), e(v)) for l, v in (
        ('Nombre de tables', tables), ('Nombre de personnes', personnes), ('Ventes sans table', sans_table)))
    if annulations:
        lignes = ''.join('<tr><td>%s</td><td>%s</td><td class="d">%s</td><td class="d">%s</td><td>%s</td><td>%s</td></tr>'
                         % (e(t), e(p), e(nombre_resto(q)), e(fcfa(m)), e(mo), e(a or '—'))
                         for t, p, q, m, mo, a in annulations)
        total = ('<tr class="gras"><td colspan="2">Total</td><td class="d">%s</td><td class="d">%s</td><td colspan="2"></td></tr>'
                 % (e(nombre_resto(sum(a[2] for a in annulations))), e(fcfa(sum(a[3] for a in annulations)))))
        ann = ('<table class="rs-rp-t"><tr class="tete"><td>Table</td><td>Produit</td><td class="d">Quantité</td>'
               '<td class="d">Montant</td><td>Motif</td><td>Autorisée par</td></tr>%s%s</table>' % (lignes, total))
    else:
        ann = '<p class="rs-rp-p">Aucune annulation sur cette période.</p>'
    return (rapport_section('Tables et personnes', '<table class="rs-rp-t">%s</table>' % tp, ident + '-tp')
            + rapport_section('Annulations', ann, ident + '-ann'))


def rapport_page(ident, contenu):
    """Une page A4 du rapport, à l'échelle de la visionneuse."""
    return '<div class="rs-rp-page" id="%s">%s</div>' % (ident, contenu)


# =================================================== gestion : réglages --
# La page des réglages d'Odoo 18 (O/web/static/src/webclient/settings_form_view/) dans le thème MuK : panneau
# « Enregistrer » / « Ignorer » / « Paramètres » / recherche (O/web/i18n/fr.po:5629-5630, 2205-2206, 5761-5762),
# barre des applications réglables à gauche, puis la page de l'application : bande d'en-tête (setting
# type="header", settings/setting_header.xml:4 : fond bg-warning à 25 %), blocs titrés et réglages sur deux
# colonnes (case, titre, phrase grise). Modèle visuel : capture 25.

def reglage(ident, titre, aide='', case=None, contenu='', point=False):
    """Un réglage : ``case`` True / False (case à cocher, cochée ou non), None (pas de case) ; ``titre`` ; ``aide``
    (la phrase grise, <id>-aide) ; ``contenu`` : HTML posé sous l'aide (champ, étiquettes, lien) ; ``point`` : le
    « ? » de la documentation (O/web/…/settings/setting.xml). Identifiants : <id>, <id>-case, <id>-aide."""
    c = ('<span class="rg-case%s" id="%s-case">%s</span>' % (' coche' if case else '', ident, ICONES['coche'])
         if case is not None else '<span class="rg-case rg-sans"></span>')
    p = '<span class="rg-doc">?</span>' if point else ''
    a = '<div class="rg-aide" id="%s-aide">%s</div>' % (ident, e(aide)) if aide else ''
    return ('<div class="rg-reglage" id="%s">%s<div class="rg-droite"><div class="rg-titre">%s%s</div>%s%s</div></div>'
            % (ident, c, e(titre), p, a, contenu))


def bloc_reglages(titre, reglages, identifiant=None):
    """Un bloc (« Mode restaurant », « Paiement ») : son titre, puis ses réglages sur deux colonnes."""
    return ('<div class="rg-bloc"%s><div class="rg-bloc-t">%s</div><div class="rg-grille">%s</div></div>'
            % (_id(identifiant), e(titre), ''.join(reglages)))


def etiquettes(valeurs, identifiant=None):
    """Un champ many2many_tags : des étiquettes grises avec leur croix, soulignées comme un champ d'Odoo."""
    t = ''.join('<span class="rg-etiq">%s<i>×</i></span>' % e(v) for v in valeurs)
    return '<span class="rg-etiqs"%s>%s<span class="rg-dd">▾</span></span>' % (_id(identifiant), t)


def lien_fleche(texte, identifiant=None):
    """Un bouton-lien d'Odoo avec la flèche oi-arrow-right (« → Salles », « → Modes de paiement »)."""
    return '<div class="rg-lien"%s><span class="ico">%s</span>%s</div>' % (_id(identifiant), ICONES['fleche-droite'],
                                                                         e(texte))


def page_reglages(ident, apps, active, entete, blocs, initiale=False):
    """La page « Paramètres » : ``apps`` = [(nom, clé de l'icône : un nom de fichier de produire.ICONES_APPS, ou None)] (la barre de gauche),
    ``active`` = le nom surligné ; ``entete`` = (libellé, valeur, lien) de la bande d'en-tête de l'application
    (« Point de Vente », « Restaurant », « + Nouvelle boutique ») ; ``blocs`` = HTML de ``bloc_reglages``. Le
    contenu défile : <id>-defil. Identifiants : <id>-enr, <id>-ign, <id>-app-<clé>, <id>-sel (la valeur)."""
    cp = ('<div class="cp rg-cp"><span class="bt primaire" id="%s-enr">Enregistrer</span>'
          '<span class="bt gris" id="%s-ign">Ignorer</span><span class="titre">Paramètres</span>%s</div>'
          % (ident, ident, recherche()))
    gauche = ''.join('<div class="rg-app%s" id="%s-app-%s">%s<span>%s</span></div>'
                     % (' actif' if nom == active else '', ident, cle or 'x',
                        '<img class="muk-ico" src="assets/icones/%s.png" alt="">' % cle if cle else '', e(nom))
                     for nom, cle in apps)
    lib, val, lien_ = entete
    tete = ('<div class="rg-entete"><span class="rg-entete-l">%s</span><span class="rg-sel" id="%s-sel">%s'
            '<span class="rg-dd">▾</span></span><span class="rg-nouv">%s</span></div>' % (e(lib), ident, e(val), e(lien_)))
    contenu = ('<div class="rg-page">%s<div class="rg-apps">%s</div><div class="rg-defil-cadre" data-layout-allow-overflow '
               'data-layout-allow-occlusion><div class="rg-defil" id="%s-defil" data-layout-allow-overflow '
               'data-layout-allow-occlusion>%s%s</div></div></div>' % (cp, gauche, ident, tete, ''.join(blocs)))
    return _vue(ident, initiale, contenu)


# ============================================== gestion : la fiche employé --

def fiche_employe(ident, nom, initiale, couleur, niveau='', code='', pager='1 / 1', aide_niveau='', aide_code='',
                  options=(), initiale_vue=False):
    """La fiche employé d'Odoo 18 (O/hr/views/hr_employee_views.xml:58-110) avec le groupe d'AITE « Caisse du
    restaurant » (R/views/hr_employee_views.xml:11-44) : panneau (« Nouveau », fil d'Ariane « Employés » / nom,
    engrenage, bouton intelligent « Contacts 1 », pagination), « Plan de lancement », la feuille : nom en grand,
    « Titre du poste », avatar carré à l'initiale, les champs de travail (e-mail, téléphones, étiquettes ;
    département, poste, manager, mentor « ? »), puis CAISSE DU RESTAURANT : « Niveau en caisse ? » (liste
    déroulante, ``options``), sa phrase, « Code caisse ? », sa phrase ; les onglets. Modèle visuel : capture 24.

    Les boutons d'enregistrement (nuage, croix : O/web/…/form_status_indicator.xml) sont cachés : ``montrer``.
    ``aide_niveau`` : la phrase sous le niveau, d'un bloc, ou découpée en phrases (une liste, jointe par des
    espaces : le texte reste celui du code) pour les désigner une à une.
    Identifiants : <id>-fil, <id>-statut (les boutons d'enregistrement), <id>-save, <id>-annul, <id>-niveau
    (champ ``entree`` : <id>-niveau-val), <id>-liste (la liste déroulante, cachée), <id>-opt-<n>, <id>-niveau-aide
    et ses phrases <id>-aide-1, -2…, <id>-code (le code, <id>-code-val), <id>-code-aide, <id>-defil."""
    cp = ('<div class="cp fe-cp"><span class="bt contour">Nouveau</span><div class="fil" id="%s-fil">'
          '<span class="parent">Employés</span><span class="ref">%s <span class="fe-eng">%s</span>'
          '<span class="fe-statut masque" id="%s-statut"><span class="fe-ic" id="%s-save">%s</span>'
          '<span class="fe-ic" id="%s-annul">%s</span></span></span></div>'
          '<span class="stat fe-stat"><span class="sic">%s</span><span class="st-t"><span>Contacts</span><b>1</b></span>'
          '</span><span class="pager">%s</span><span class="fe-nav">‹</span><span class="fe-nav">›</span></div>'
          % (ident, e(nom), ICONES['engrenage'], ident, ident, ICONES['nuage'], ident, ICONES['x'], ICONES['contacts'],
             e(pager)))
    bande = '<div class="fe-bande"><span class="bt gris">Plan de lancement</span></div>'

    def ch(lib, val='', ph='', aide=False, ident_=None):
        q = '<sup class="fe-q">?</sup>' if aide else ''
        # le texte indicatif d'Odoo est pâle (volontairement peu contrasté) : soustrait au contrôle de contraste
        v = ('<span class="fe-v">%s</span>' % e(val)) if val else '<span class="fe-ph" data-layout-ignore>%s</span>' % e(ph)
        return '<div class="fe-ch"%s><span class="fe-l">%s%s</span>%s</div>' % (_id(ident_), e(lib), q, v)

    gauche = (ch('Adresse e-mail professionnelle', ph='par ex. johndoe@example.com') + ch('Téléphone professionnel')
              + ch('Téléphone portable professionnel') + ch('Étiquettes', ph='Étiquettes'))
    droite = (ch('Département') + ch('Poste', ph='par ex. Directeur Commercial') + ch('Manager')
              + ch('Mentor', aide=True))
    phrases = [aide_niveau] if isinstance(aide_niveau, str) else list(aide_niveau or ())
    aide_n = ' '.join('<span id="%s-aide-%d">%s</span>' % (ident, k, e(p)) for k, p in enumerate(phrases, 1))
    liste = ''.join('<div class="fe-opt" id="%s-opt-%d">%s</div>' % (ident, k, e(o) or '&nbsp;')
                    for k, o in enumerate(options))
    caisse = ('<div class="fe-grp-t">Caisse du restaurant</div>'
              '<div class="fe-ch fe-ch-l"><span class="fe-l">Niveau en caisse<sup class="fe-q">?</sup></span>'
              '<div class="fe-sel">%s<span class="fe-dd">▾</span><div class="fe-liste masque" id="%s-liste">%s</div>'
              '</div></div>'
              '<div class="fe-aide" id="%s-niveau-aide">%s</div>'
              '<div class="fe-ch fe-ch-l"><span class="fe-l">Code caisse<sup class="fe-q">?</sup></span>%s</div>'
              '<div class="fe-aide" id="%s-code-aide">%s</div>'
              % (entree(ident + '-niveau', '', niveau, classe='entree fe-in'), ident, liste, ident, aide_n,
                 entree(ident + '-code', '', code, classe='entree fe-in fe-code'), ident, e(aide_code)))
    onglets_ = onglets(['CV', 'Informations professionnelles', 'Informations privées', 'Paramètres'])
    feuille = ('<div class="fe-feuille"><div class="fe-tete"><div><div class="fe-nom">%s</div>'
               '<div class="fe-poste" data-layout-ignore>Titre du poste</div></div><div class="fe-avatar" style="background:%s">%s</div></div>'
               '<div class="fe-cols"><div>%s</div><div>%s</div></div>%s%s</div>'
               % (e(nom), couleur, e(initiale), gauche, droite, caisse, onglets_))
    contenu = ('%s<div class="fe-cadre" data-layout-allow-overflow data-layout-allow-occlusion><div class="fe-defil" '
               'id="%s-defil" data-layout-allow-overflow data-layout-allow-occlusion>%s%s</div></div>'
               % (cp, ident, bande, feuille))
    return _vue(ident, initiale_vue, contenu)


# ---------------------------------------- la pastille du personnage, par étape --

def css_personnage(selecteur, nom, role, initiale):
    """Les règles qui font dire à la pastille du personnage (``marketing.Tutoriel``, #tu-perso) un autre nom, un
    autre rôle et une autre initiale, tant que ``selecteur`` (par exemple ``#tu-perso.t17-pc`` ou
    ``#tu-perso:not(.t16-moi)``) s'applique : le geste ``classe('#tu-perso', …)`` passe d'un personnage à l'autre
    (mécanisme de scenarios/t04_note_chambre.py, ``pastille_css``)."""
    return ('%(s)s > span:last-child { font-size: 0; }\n'
            '%(s)s > span:last-child::before { content: "%(n)s"; font-size: 21px; font-weight: 700; }\n'
            '%(s)s > span:last-child::after { content: " · %(r)s"; font-size: 21px; white-space: pre; }\n'
            '%(s)s .av { font-size: 0; }\n'
            '%(s)s .av::before { content: "%(i)s"; font-size: 20px; }\n'
            % {'s': selecteur, 'n': nom, 'r': role, 'i': initiale})
