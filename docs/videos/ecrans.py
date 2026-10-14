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

from html import escape as _e


def e(texte):
    """Échappe un texte destiné à l'écran."""
    return _e(str(texte), quote=True)


def _id(identifiant):
    return ' id="%s"' % identifiant if identifiant else ''


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


def cp_fiche(parent, reference, pager='', stats=()):
    """Le panneau d'une fiche : « Nouveau », fil d'Ariane, boutons intelligents, pagination.

    ``stats`` : (identifiant, icône, libellé, valeur).
    """
    boutons = ''.join('<span class="stat"%s>%s<span class="st-t"><span>%s</span><b id="%s-v">%s</b></span></span>'
                      % (_id(i), icone(ic, 'sic'), e(l), i, e(v)) for i, ic, l, v in stats)
    return ('<div class="cp"><span class="bt contour">Nouveau</span>'
            '<div class="fil"><span class="parent">%s</span><span class="ref">%s</span></div>'
            '<div class="stats">%s</div><span class="pager">%s</span></div>'
            % (e(parent), e(reference), boutons, e(pager)))


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


def kpi(identifiant, libelle, valeur, sous='', accent=None, delta=None, aide=False):
    """Une carte d'indicateur : ``delta`` = (texte, 'haut' | 'bas')."""
    d = ''
    if delta:
        d = '<div class="kpi-d %s">%s %s</div>' % (delta[1], '▲' if delta[1] == 'haut' else '▼', e(delta[0]))
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

def site(identifiant, vues, nom_site, calques=''):
    """Le site web public de l'établissement : en-tête, page, vues empilées."""
    return ('<div class="app site" id="%s"><div class="s-nav"><span class="s-logo">%s</span>'
            '<span class="s-m">Accueil</span><span class="s-m actif">Réservation</span><span class="s-m">Nous contacter</span>'
            '<span class="s-tel">%s+237 6 99 00 00 00</span><span class="bt primaire s-bt">Nous contacter</span></div>'
            '<div class="s-page">%s</div>%s</div>'
            % (identifiant, e(nom_site), icone('telephone'), ''.join(vues), calques))


def s_vue(identifiant, contenu, initiale=False):
    return _vue(identifiant, initiale, '<div class="s-cadre">%s</div>' % contenu, classe='vue s-vue')
