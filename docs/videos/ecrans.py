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
