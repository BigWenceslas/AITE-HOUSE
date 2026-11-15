# -*- coding: utf-8 -*-
"""Tutoriel 17 — Ouvrir la caisse et servir une table.

Le deuxième des huit tutoriels du restaurant (lot 1 : aite_pos_restaurant ;
restaurant SANS hôtel, comme t16 : demo.RESTO, demo.SOCIETE_RESTO). Toute la
vidéo se passe sur la caisse plein écran au service à table contrôlé
(ecrans.py, « La caisse du restaurant »), sans barre MuK.

Personnages : Prisca, la caissière (demo.POSTES_RESTO['caisse'], code 6304),
ouvre la caisse à l'étape 1 ; Loïc, le serveur (demo.POSTES_RESTO['serveur'],
code 4827), sert la table 4 aux étapes 2 à 7. La pastille du haut passe de
l'une à l'autre au début de l'étape 2 (ecrans.css_personnage, comme t16).
Storyboard : scratchpad videos_resto/storyboards/t17.md (adapté : voir
« Écarts au storyboard »).

Abréviations : R/ = addons/aite_pos_restaurant/ ; S/ = R/static/src/ ;
O/ = ../odoo18/addons/. Les phrases de la caisse sont relues dans le code au
chargement (garde-fous en bas de l'en-tête) : une phrase changée dans le module
fait échouer la construction de la vidéo au lieu de la rendre fausse.

Le monde rejoué (conditions) :
- le jour de référence de la série, le 14/10/2026 ; aucune date ni heure
  n'est à l'écran (seules les durées « 0 min », « 12 min ») ;
- la caisse « Restaurant », salle « Salle », douze tables (demo, comme t16) ;
  la session est en « Contrôle d'ouverture » le matin ; le fond de caisse
  proposé est 25 000 FCFA, les espèces comptées à la fermeture précédente
  (O/point_of_sale/static/src/app/store/opening_control_popup/
  opening_control_popup.js:29-32 ; notes de version :272, « comptés à la
  fermeture et repris en fond le lendemain » ; storyboard t22 : la journée
  ferme avec 25 000 comptés) ;
- la table 4 est la première table de la journée sur cette tablette : aucune
  famille n'est encore choisie, l'écran de commande montre toute la carte
  (O/point_of_sale/static/src/app/store/pos_store.js:142 ; O/point_of_sale/
  static/src/app/screens/product_screen/product_screen.js:379-394), triée par
  nom (:417-419) ; le choix d'une famille reste ensuite sur le poste
  (pos_store.js:1058-1068) : à la deuxième visite, « Bière » est toujours
  choisie (capture 09) ;
- carte demo.CARTE_RESTO, sans TVA (pas de ligne « Taxes ») ; une table de 4
  personnes, puis 6 ; la table 4 reste ouverte à la fin (t21 l'encaisse) :
  Pizza Margherita, 2 Bière blonde 65 cl, 2 Cola 33 cl = 10 000 FCFA.

Écrans et libellés (modèles visuels : captures/restaurant/01 à 07, et 09) :

1. Plan « Salle », caisse en contrôle d'ouverture : « Plan », « Table », logo,
   ≡ (O/pos_restaurant/i18n/fr.po:892, 1198) ; bandeau « La caisse est
   fermée… » et « Ouvrir la caisse » (S/utils/messages.js:98-100 ;
   S/overrides/floor_screen.xml:21-26) ; fenêtre « Votre code pour ouvrir la
   caisse » (messages.js:74), quatre points, pavé, « Retour »
   (S/components/code_popup/code_popup.xml:10-37 ; messages.js:104) : elle
   s'ouvre d'elle-même à l'affichage du plan (S/store/pos_store.js:685-731).
   Le code est vérifié par le serveur (R/models/pos_session.py:199-228 : la
   caissière et au-dessus, R/models/regles.py:36). Puis le contrôle d'ouverture
   d'Odoo : « Contrôle à l'ouverture », « Espèces à l'ouverture », 25 000,
   « Note d'ouverture », « Ajouter une note d'ouverture... » (O/point_of_sale/
   i18n/fr.po:4846, 4868, 4899, 684), un seul bouton « J'ouvre la caisse »
   (R/static/src/overrides/opening_control_popup.xml:9 ; capture 02), le nom
   « Prisca » en haut (S/overrides/navbar.xml:18-20 ; capture 02). À sa
   fermeture, le plan se verrouille (S/overrides/opening_control_popup.js:17) :
   « Touchez une table, puis tapez votre code. » (messages.js:97 ;
   floor_screen.xml:27-28 ; capture 03). « Caisse ouverte par » est écrit sur
   la session (pos_session.py:51-53 ; notes de version :92-94).
2. Toucher une table demande toujours le code (pos_store.js:825-866) :
   « Table 4 — votre code » (messages.js:73 ; capture 04) ; table libre : la
   même fenêtre demande les personnes (pos_store.js:897-907) : « Table 4 —
   combien de personnes ? » (messages.js:81), huit boutons 1 à 8, « 9 et
   plus », « Retour » (code_popup.js:42 ; code_popup.xml:39-72 ; capture 05).
3. L'écran de commande : « Table 4 · ouverte par Loïc · 0 min »
   (pos_store.js:1136-1151 ; messages.js:114-116, 165-171 ;
   S/overrides/product_screen.xml:13-16) ; addition vide : panier,
   « Commencez à ajouter des produits » (O/point_of_sale/i18n/fr.po:7437),
   « Libérer la table » (O/pos_restaurant/i18n/fr.po:969 ; gardé par la
   spécification, partie 1.1 C) ; « 4 personnes »,
   « Addition » (S/overrides/control_buttons.xml:17-25 ; messages.js:108-109),
   « Client », « Note cuisine », « Actions » (O/point_of_sale/i18n/fr.po:2397,
   3878, 591) ; « Note cuisine » grisé sans ligne choisie (O/point_of_sale/
   static/src/app/screens/product_screen/control_buttons/customer_note_button/
   customer_note_button.xml:7) ; sans produit, pas de pavé (O/point_of_sale/…/
   product_screen.xml:13) ni « J'encaisse », et « J'envoie » prend toute la
   rangée (O/pos_restaurant/…/actionpad_widget.xml:15-17, 36 : flex-fill) ;
   familles (product_screen.js:113-152 ; recette R29-R31), tuiles (couleur de
   la famille : product_screen.xml:35) ; lignes, « Total », pavé (« Qté »,
   « % » et « Prix » grisés), « J'envoie » et ses compteurs « Pizzas 1 »,
   « Bière 2 » (R/static/src/overrides/actionpad_widget.xml:14 ; O/pos_restaurant/
   static/src/overrides/models/pos_store.js:74-93 ; capture 06), « J'encaisse »
   (actionpad_widget.xml:17), « Rechercher des produits… », code-barres,
   « Loïc » (capture 06).
4. « J'envoie » : notification « Envoyé : 1 Pizzas, 2 Bière. » et retour au
   plan (S/overrides/actionpad_widget.js:24-26, 43-44 ; messages.js:103 ;
   capture 07, même texte) ; tout retour au plan verrouille
   (pos_store.js:448-455) ; table 4 verte « 0 min » (floor_screen.xml:31-44 ;
   capture 07).
5. Table occupée : le code seul, sans étape des personnes (pos_store.js:
   897-907) ; écran de commande rouvert sans ligne choisie : pas de pavé,
   « Note cuisine » grisé, « J'envoie » gris, « J'encaisse » primaire, « 2 »
   sur la tuile (capture 09). « 4 personnes » ouvre l'étape des personnes seule
   (S/overrides/control_buttons.js:56-72 ; pos_store.js:193-207).
6. Deux bières de plus, puis ⌫ ⌫ : ce qui n'est pas parti redescend à ce qui
   est parti, sans code ni trace (S/overrides/order_summary.js:42-64 ;
   recette R34-R36 ; tour R/static/tests/tours/parcours_tour.js:271-281). La
   ligne qui a une part pas encore envoyée porte la barre verte (O/pos_restaurant/
   static/src/overrides/models/pos_order_line.js:31 ; capture 06).
7. Non alcoolisé › Sodas (la sœur déjà affichée : product_screen.js:113-152),
   deux Cola 33 cl, « J'envoie » : « Envoyé : 2 Sodas. », plan, table 4 verte.

Règles dites par la voix, les bulles, les réactions et les résultats :
- la fenêtre du code s'ouvre seule le matin : pos_store.js:685-692 ;
- le code d'un serveur n'ouvre pas la caisse : regles.py:36 (ouvrir_caisse :
  caissière), pos_session.py:224-226 (R3), recette R10 ;
- le fond de caisse est déjà rempli : notes de version :248 (« fond
  prérempli »), :272 ;
- la caisse garde le nom de qui l'a ouverte : pos_session.py:51-53 ;
- cinq touches pour ouvrir la caisse, sept pour ouvrir une table et l'envoyer
  plus le choix des produits, deux pour changer le nombre de personnes : notes
  de version §3 (:248, :249, :253), mesurées par AiteParcoursTour ;
- pas de bouton zéro : code_popup.js:14, 42 ; messages.js:25 (R5) ; R22 ;
- « 9 et plus » au-delà de huit : code_popup.xml:47-68 ; R26 ;
- « J'envoie » compte ce qui n'est pas parti, famille par famille :
  O/pos_restaurant/…/models/pos_store.js:74-93 (getOrderChanges) ;
- tout retour au plan oublie l'employé (« J'envoie », « Plan »,
  l'encaissement) : notes de version :41-43 ; pos_store.js:448-455 ; R08 ;
- l'addition rouverte ne redemande pas les personnes : pos_store.js:897-907 ;
- « ouverte par » reste figé : notes de version :107 ; R04 ;
- ce qui est parti ne s'efface plus sans le code d'un chef de salle :
  order_summary.js:52-60 ; messages.js:58-60 (R9) ; R35.

Écarts au storyboard :
- l'équipe est celle de demo.EQUIPE_RESTO : Loïc (serveur, 4827) au lieu du
  serveur proposé par le storyboard (prénom déjà présent dans le dépôt, écarté
  par le socle) ;
- accroche : quatre douleurs ; « un serveur qui encaisse » relève de t21 ;
- résultats : « 7 touches, plus le choix des produits » (7 + n, notes :249)
  au lieu de « 9 » : la vidéo montre aussi les touches des familles ; la
  troisième carte ne garde que le changement du nombre de personnes (retirer
  coûte 2 touches seulement si la ligne est déjà choisie, notes :252) ;
- bulle « 5 minutes » écartée (point à valider n° 1, non mesuré à l'écran :
  notes de version §5, §8) ;
- l'anneau « plus de nom en haut » désigne la phrase d'état du plan (rien à
  entourer à la place du nom) ;
- étape 3 : la carte entière avant le choix d'une famille ; addition vide sans
  pavé ; étape 5 : addition rouverte sans pavé (voir plus haut) ;
- la bulle « code d'un serveur » vient après l'ouverture, à côté de la table 4
  (avant la saisie, elle retardait le code sur la voix) ; pas de zoom sur
  « J'envoie » (au bord bas du navigateur, la légende le couvrirait) ;
- la voix des étapes suit l'ordre de l'image (famille, puis produit ; étape 7 :
  « Non alcoolisé, puis Sodas », puis les colas) ;
  « margherita » s'écrit « marguérita » pour la voix seulement (Kokoro lit
  maʁɡʁita).

Mise en forme propre à ce tutoriel (clé « css ») : deux colonnes de gauche dans
la même case de la grille (l'addition avant et après le premier toucher), la
pile des familles et des tuiles, l'avatar de Prisca, « J'envoie » centré quand il
n'y a rien à envoyer (O/pos_restaurant/…/actionpad_widget.js:32-38 ; capture 09),
et un gris un ton plus
foncé pour « % », « Prix » et la quantité des tuiles (contraste WCAG AA du
contrôle de HyperFrames : le gris d'Odoo #6C757D donne 4,2:1 et 2,3:1). Les
textes à l'écran écrits ici prennent une espace insécable dans les guillemets
et avant « : », « ; », « ? » (_typo, en bas du fichier).
"""

import ast
import os
import re
import unicodedata

import demo
from ecrans import (MESSAGES_RESTO, TEXTES_RESTO, TITRES_RESTO, _odoo_dir, css_personnage, duree_resto, entier,
                    etat_commande, fcfa, fenetre_resto, navigateur, resto_code, resto_commande, resto_familles,
                    resto_ligne, resto_notification, resto_ouverture, resto_plan, resto_salle, resto_tuiles)
from marketing import bulle, dezoom, reaction, zoom
from moteur import anneau, cacher, classe, clic, curseur, fermer, montrer, notifier, ouvrir, pause, texte, vue

RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
R = os.path.join(RACINE, 'addons', 'aite_pos_restaurant')
S = os.path.join(R, 'static', 'src')


def _lire(*chemin):
    with open(os.path.join(*chemin), encoding='utf-8') as f:
        return f.read()


def _une_ligne(texte_):
    return ' '.join((texte_ or '').split())


# ============================================================== garde-fous --
# 1. Les textes de la caisse : chaque phrase montrée est relue dans S/utils/messages.js (source JS, espaces
#    ramenées à une seule), puis comparée à ce que les composants d'ecrans.py affichent.
_JS = _une_ligne(_lire(S, 'utils', 'messages.js'))


def _js(extrait, **valeurs):
    """Le texte d'un littéral de messages.js (``extrait`` doit y être mot pour mot), ``${ESP}`` → espace
    insécable, ``${x}`` → ``valeurs['x']``."""
    assert extrait in _JS, ('t17 : texte changé dans messages.js', extrait)
    t = re.search(r'(["`])(.*)\1', extrait).group(2).replace('${ESP}', ' ')
    for cle, val in valeurs.items():
        t = t.replace('${%s}' % cle, str(val))
    assert '${' not in t, extrait
    return t


assert _js('planEtat: "Touchez une table, puis tapez votre code."') == TEXTES_RESTO['planEtat']
assert _js('caisseFermee: "La caisse est fermée. La caissière ou un chef de salle tape son code pour '
           'l\'ouvrir."') == TEXTES_RESTO['caisseFermee']
assert _js('ouvrirLaCaisse: "Ouvrir la caisse"') == TEXTES_RESTO['ouvrirLaCaisse']
assert _js('ouvrir: "Votre code pour ouvrir la caisse"') == TITRES_RESTO['ouvrir']
assert _js('table: (numero) => `Table ${numero} — votre${ESP}code`', numero=4) == TITRES_RESTO['table'](4)
assert _js('personnes: (numero) => `Table ${numero} — combien de personnes${ESP}?`', numero=4) == \
    TITRES_RESTO['personnes'](4)
assert _js('envoye: (compte) => `Envoyé${ESP}: ${compte}.`', compte='1 Pizzas, 2 Bière') == \
    TEXTES_RESTO['envoye']('1 Pizzas, 2 Bière')
assert _js('retour: "Retour"') == TEXTES_RESTO['retour']
assert _js('neufEtPlus: "9 et plus"') == TEXTES_RESTO['neufEtPlus']
assert _js('addition: "Addition"') == TEXTES_RESTO['addition']
assert _js('`${nombre} personnes`', nombre=6) == TEXTES_RESTO['personnes'](6)
assert ' · '.join((_js('table: (numero) => `Table ${numero}`', numero=4),
                   _js('ouvertePar: (nom) => `ouverte par ${nom}`', nom='Loïc'),
                   _js('return `${minutes} min`;', minutes=12))) == etat_commande(4, 'Loïc', 12)
assert duree_resto(12) == '12 min'
assert [_js('texte: `Gris${ESP}: libre`'), _js('texte: `Vert${ESP}: ouverte`'),
        _js('texte: `Pastille rouge${ESP}: pas encore envoyé`')] == \
    [t for c, t in TEXTES_RESTO['legendeParties'](demo.DELAI_ORANGE) if c != 'orange']
assert _js('R5: "Il faut au moins une personne à table."') == MESSAGES_RESTO['R5']

# 2. Les gabarits et le comportement que la vidéo montre.
_OCP = _lire(S, 'overrides', 'opening_control_popup.xml')
_PAD = _lire(S, 'overrides', 'actionpad_widget.xml')
assert '"J\'ouvre la caisse"' in _OCP, "t17 : « J'ouvre la caisse » changé"
assert ">J'envoie</t>" in _PAD and '"J\'encaisse"' in _PAD, "t17 : « J'envoie » ou « J'encaisse » changé"
assert 't-esc="aiteTextes.caisseFermee"' in _lire(S, 'overrides', 'floor_screen.xml')
assert 'pos.aiteEtatCommande(pos.get_order())' in _lire(S, 'overrides', 'product_screen.xml')
assert 'aiteTextes.personnes(currentOrder.customer_count || 0)' in _lire(S, 'overrides', 'control_buttons.xml')
_CODE_XML = _lire(S, 'components', 'code_popup', 'code_popup.xml')
assert 't-esc="textes.neufEtPlus"' in _CODE_XML and 't-esc="textes.retour"' in _CODE_XML
assert 'this.boutonsPersonnes = ["1", "2", "3", "4", "5", "6", "7", "8"];' in _lire(S, 'components', 'code_popup',
                                                                                     'code_popup.js')
# « J'envoie » : notification, puis retour au plan, qui verrouille ; l'ouverture verrouille aussi.
assert ('this.pos.notification.add(TEXTES.envoye(compte), { type: "info" }); this.pos.showScreen("FloorScreen");'
        in _une_ligne(_lire(S, 'overrides', 'actionpad_widget.js')))
assert ('this.aiteQuitterAddition(); this.aiteVerrouiller(); } return super.showScreen(name, props);'
        in _une_ligne(_lire(S, 'store', 'pos_store.js')))
assert 'this.pos.aiteVerrouillerSurPlan();' in _lire(S, 'overrides', 'opening_control_popup.js')
# ⌫ ⌫ : ce qui n'est pas parti redescend à ce qui est parti.
assert ('if (line.get_quantity() > envoye) { line.set_quantity(envoye); return; }'
        in _une_ligne(_lire(S, 'overrides', 'order_summary.js')))


def _source(relatif, nom):
    """Une constante d'un fichier Python du module, lue sans importer Odoo (comme t16)."""
    for noeud in ast.parse(_lire(R, relatif)).body:
        if isinstance(noeud, ast.Assign) and any(getattr(c, 'id', None) == nom for c in noeud.targets):
            return ast.literal_eval(noeud.value)
    raise ValueError('t17 : %s introuvable dans %s' % (nom, relatif))


_DROITS = _source('models/regles.py', 'DROITS')
assert (_DROITS['ouvrir_caisse'], _DROITS['servir']) == ('caissiere', 'serveur'), "t17 : droit d'ouvrir changé"
assert _source('models/pos_config.py', 'NOM_CAISSE') == demo.CAISSE_RESTO
assert _source('models/pos_config.py', 'NOM_SALLE') == demo.SALLE_RESTO

# 3. Les touches mesurées (résultats) : notes de version §3.
_NOTES = _lire(RACINE, 'docs', 'NOTES_DE_VERSION_restaurant_lot1.md')
for _ligne in ('| Caissière — ouvrir la caisse le matin | 5 | **5** (et **5** le lendemain, fond prérempli) |',
               '| Serveur — ouvrir une table et envoyer | 7 + n | **9** (n = 2), **8** (n = 1) |',
               '| Serveur — changer le nombre de personnes | 2 | **2** |'):
    assert _ligne in _NOTES, ('t17 : mesure changée dans les notes de version', _ligne)

# 4. Les libellés d'Odoo de la caisse (traductions françaises), si Odoo est à côté du dépôt (ecrans.py le lit
#    déjà pour le logo).
_PO = _lire(_odoo_dir(), 'addons', 'point_of_sale', 'i18n', 'fr.po') + _lire(_odoo_dir(), 'addons', 'pos_restaurant',
                                                                             'i18n', 'fr.po')
for _msg in ("Contrôle à l'ouverture", "Espèces à l'ouverture", "Note d'ouverture", "Ajouter une note d'ouverture...",
             'Commencez à ajouter des produits', 'Libérer la table', 'Note cuisine', 'Client', 'Actions',
             'Rechercher des produits…', 'Plan', 'Table', 'Qté', 'Prix'):
    assert 'msgstr "%s"' % _msg in _PO, ("t17 : libellé d'Odoo introuvable", _msg)

# ============================================================== les données --
PRISCA = next(x for x in demo.EQUIPE_RESTO if x[0] == demo.POSTES_RESTO['caisse'][0])
LOIC = next(x for x in demo.EQUIPE_RESTO if x[0] == demo.POSTES_RESTO['serveur'][0])
assert (PRISCA[2], LOIC[2]) == ('Caissière', 'Serveur')
NOM_P, CODE_P = PRISCA[1], PRISCA[3]
NOM_L, CODE_L = LOIC[1], LOIC[3]
TABLE = 4
FOND = 25000           # espèces comptées à la fermeture précédente, proposées à l'ouverture (voir l'en-tête)
assert FOND == demo.FOND_RESTO, 't17 : le fond de caisse a changé, reporter dans demo.py (t22)'
DUREE_RETOUR = 12      # minutes : la deuxième visite de Loïc

# La couleur de chaque famille (une sous-famille prend celle de son parent : demo.FAMILLES_RESTO), et ses
# descendantes (O/point_of_sale/static/src/app/models/pos_category.js:7-16, getAllChildren).
COULEUR, DESCENDANTES = {}, {}


def _parcourir(branches, couleur_parent=0):
    noms = []
    for nom, couleur, enfants in branches:
        COULEUR[nom] = couleur or couleur_parent
        DESCENDANTES[nom] = [nom] + _parcourir(enfants, COULEUR[nom])
        noms += DESCENDANTES[nom]
    return noms


_parcourir(demo.FAMILLES_RESTO)
PRIX = {nom: prix for nom, _f, prix, _c, _s in demo.CARTE_RESTO}
FAMILLE = {nom: f for nom, f, _p, _c, _s in demo.CARTE_RESTO}


def cle(nom):
    """« Bière blonde 65 cl » → « biereblonde65cl » (comme ecrans.resto_familles)."""
    return ''.join(c for c in unicodedata.normalize('NFD', nom.lower()) if c.isalnum())


def tri(nom):
    """L'ordre de localeCompare (product_screen.js:417-419) : sans accent ni casse."""
    return ''.join(c for c in unicodedata.normalize('NFD', nom.casefold()) if unicodedata.category(c) != 'Mn')


def produits(famille=None):
    """Les tuiles d'une famille et de ses descendantes (toute la carte sans famille), triées par nom."""
    noms = [n for n, _f, _p, _c, _s in demo.CARTE_RESTO if famille is None or FAMILLE[n] in DESCENDANTES[famille]]
    return [(cle(n), n, COULEUR[FAMILLE[n]]) for n in sorted(noms, key=tri)]


MARGHERITA, BLONDE, COLA = 'Pizza Margherita', 'Bière blonde 65 cl', 'Cola 33 cl'
assert [FAMILLE[MARGHERITA], FAMILLE[BLONDE], FAMILLE[COLA]] == ['Pizzas', 'Bière', 'Sodas']
assert [n for _k, n, _c in produits('Pizzas')] == ['Pizza Margherita', 'Pizza quatre fromages', 'Pizza Reine']
assert [n for _k, n, _c in produits('Sodas')] == ['Cola 33 cl', 'Eau minérale 50 cl', 'Jus de bissap 50 cl']
assert len(produits()) == len(demo.CARTE_RESTO) == 18
# L'addition : 1 Pizza Margherita, 2 Bière blonde 65 cl (8 000), puis 2 Cola 33 cl (10 000).
TOTAL_1 = PRIX[MARGHERITA] + 2 * PRIX[BLONDE]
TOTAL_2 = TOTAL_1 + 2 * PRIX[COLA]
assert (TOTAL_1, TOTAL_2) == (8000, 10000)
ENVOI_1 = '1 %s, 2 %s' % (FAMILLE[MARGHERITA], FAMILLE[BLONDE])
ENVOI_2 = '2 %s' % FAMILLE[COLA]

# ================================================================ l'écran --
POS = 't17-pos'
PLAN = resto_plan('t17-plan', resto_salle('t17-plan'), delai=demo.DELAI_ORANGE, salle=demo.SALLE_RESTO,
                  caisse_fermee=True, initiale=True)
T4 = '#t17-plan-t%d' % TABLE


def pile(ident, etats, visible=0):
    """Les états successifs des familles et des tuiles, empilés au même endroit (une grille d'une case) :
    ``etats`` = [(chemin, famille des tuiles, {clé: quantité})] ; on passe de l'un à l'autre par cacher /
    montrer. Identifiants : <ident>-e<k>, <ident>-e<k>-fa-f-<famille>, <ident>-e<k>-tu-<produit>(-q)."""
    blocs = []
    for k, (chemin, famille, qtes) in enumerate(etats):
        blocs.append('<div class="t17-et%s" id="%s-e%d">%s%s</div>'
                     % ('' if k == visible else ' masque', ident, k,
                        resto_familles('%s-e%d-fa' % (ident, k), demo.FAMILLES_RESTO, chemin),
                        resto_tuiles('%s-e%d-tu' % (ident, k), produits(famille), qtes)))
    return '<div class="t17-pile">%s</div>' % ''.join(blocs)


def commande(ident, avant, apres, familles):
    """L'écran de commande d'une visite : deux colonnes de gauche posées dans la même case de la grille —
    ``avant`` (dict d'arguments de resto_commande : l'addition à l'arrivée, sans ligne choisie, donc sans pavé)
    et ``apres`` (la même addition dès qu'un produit est touché : ligne choisie, pavé) —, et la pile des familles
    à droite. Identifiants : <ident>v-… (avant), <ident>-… (après), <ident>v-g et <ident>-g (les colonnes)."""
    b = resto_commande(ident, familles_html=familles, tuiles_html='', **apres)
    a = resto_commande(ident + 'v', familles_html='', tuiles_html='', **avant)
    gauche_a = a[a.index('<div class="rs-g">'):a.index('<div class="rs-d">')]
    gauche_a = gauche_a.replace('<div class="rs-g">', '<div class="rs-g" id="%sv-g">' % ident, 1)
    # sans ligne choisie, « Note cuisine » est grisé (customer_note_button.xml:7)
    gauche_a = gauche_a.replace('<span class="" id="%sv-note">' % ident, '<span class="gris" id="%sv-note">' % ident, 1)
    assert 'class="gris" id="%sv-note"' % ident in gauche_a
    b = b.replace('<div class="rs-g">', '<div class="rs-g masque" id="%s-g">' % ident, 1)
    return b.replace('<div class="rs-d">', gauche_a + '<div class="rs-d">', 1)


ETAT_0 = etat_commande(TABLE, NOM_L, 0)
ETAT_12 = etat_commande(TABLE, NOM_L, DUREE_RETOUR)


def L_PIZZA(ident, **kw):
    return resto_ligne(ident, MARGHERITA, 1, PRIX[MARGHERITA], **kw)


# Première visite : la carte entière, puis Nourriture › Pizzas ; après la pizza, Boisson › Alcoolisé › Bière.
C1 = commande('t17-c1', dict(
    etat=ETAT_0, lignes_html='', total=fcfa(0), personnes=4, compteurs=[('Pizzas', 0), ('Bière', 0)], vide=True),
    dict(etat=ETAT_0, total=fcfa(PRIX[MARGHERITA]), personnes=4, compteurs=[('Pizzas', 1), ('Bière', 0)],
         lignes_html=L_PIZZA('t17-c1-l1', envoyee=False, choisie=True)
         + resto_ligne('t17-c1-l2', BLONDE, 1, PRIX[BLONDE], envoyee=False, choisie=True, cache=True)),
    pile('t17-c1', [((), None, {}), (('Nourriture',), 'Nourriture', {}), (('Nourriture', 'Pizzas'), 'Pizzas', {}),
                    (('Boisson',), 'Boisson', {}), (('Boisson', 'Alcoolisé'), 'Alcoolisé', {}),
                    (('Boisson', 'Alcoolisé', 'Bière'), 'Bière', {})]))
# Deuxième visite : « Bière » toujours choisie ; tout est parti ; après la première bière, Non alcoolisé › Sodas.
C2 = commande('t17-c2', dict(
    etat=ETAT_12, total=fcfa(TOTAL_1), personnes=4, compteurs=[('Bière', 0), ('Sodas', 0)], encaisser=True,
    lignes_html=L_PIZZA('t17-c2v-l1') + resto_ligne('t17-c2v-l2', BLONDE, 2, PRIX[BLONDE])),
    dict(etat=ETAT_12, total=fcfa(TOTAL_1 + PRIX[BLONDE]), personnes=6, compteurs=[('Bière', 1), ('Sodas', 0)],
         lignes_html=L_PIZZA('t17-c2-l1') + resto_ligne('t17-c2-l2', BLONDE, 3, PRIX[BLONDE], envoyee=False, choisie=True)
         + resto_ligne('t17-c2-l3', COLA, 1, PRIX[COLA], envoyee=False, choisie=True, cache=True)),
    pile('t17-c2', [(('Boisson', 'Alcoolisé', 'Bière'), 'Bière', {cle(BLONDE): 2}),
                    (('Boisson', 'Non alcoolisé'), 'Non alcoolisé', {}),
                    (('Boisson', 'Non alcoolisé', 'Sodas'), 'Sodas', {})]))

# Les fenêtres posées sur la caisse.
CODE = resto_code('t17-code', TITRES_RESTO['ouvrir'])
OUV = resto_ouverture('t17-ouv', entier(FOND))
TAB = resto_code('t17-tab', TITRES_RESTO['table'](TABLE), personnes=True)
TAB2 = resto_code('t17-tab2', TITRES_RESTO['table'](TABLE))
# « 4 personnes » : l'étape des personnes seule (code_popup.js:120, etape « personnes »).
PERS = resto_code('t17-pers', TITRES_RESTO['personnes'](TABLE), personnes=True)
for _avant, _apres in (('class="rs-pan masque" id="t17-pers-pers"', 'class="rs-pan" id="t17-pers-pers"'),
                       ('class="rs-pan" id="t17-pers-code"', 'class="rs-pan masque" id="t17-pers-code"')):
    assert _avant in PERS
    PERS = PERS.replace(_avant, _apres, 1)
N1 = resto_notification('t17-n1', TEXTES_RESTO['envoye'](ENVOI_1))
N2 = resto_notification('t17-n2', TEXTES_RESTO['envoye'](ENVOI_2))

CAISSE = fenetre_resto(POS, [PLAN, C1, C2], calques=CODE + OUV + TAB + TAB2 + PERS + N1 + N2, ecran='plan',
                       avatar=demo.AVATARS_RESTO[NOM_L])
ECRAN = navigateur(CAISSE)

CSS = ("/* -- la pastille : Prisca, la caissière, à l'étape 1 ; Loïc, le serveur, ensuite -- */\n"
       + css_personnage('#tu-perso:not(.t17-loic)', demo.POSTES_RESTO['caisse'][0], demo.POSTES_RESTO['caisse'][1],
                        NOM_P[0]) + """
/* -- l'avatar de Prisca en haut de la caisse (celui de Loïc est posé par fenetre_resto) -- */
.resto.t17-prisca .rs-emp .avatar { background: %s !important; }
/* -- l'écran de commande : deux colonnes de gauche dans la même case (avant / après le premier toucher) -- */
#t17-c1 .rs-cmd > .rs-g, #t17-c2 .rs-cmd > .rs-g { grid-column: 1; grid-row: 1; }
#t17-c1 .rs-cmd > .rs-d, #t17-c2 .rs-cmd > .rs-d { grid-column: 2; grid-row: 1; }
/* sans ligne choisie, pas de pavé (O/point_of_sale product_screen.xml:13) ; addition vide : pas de
   « J'encaisse », « J'envoie » prend la rangée (pos_restaurant actionpad_widget.xml:15-17, flex-fill) */
#t17-c1v-pave, #t17-c2v-pave, #t17-c1v-encaisser { display: none; }
#t17-c1v-g .rs-act { grid-template-columns: 1fr; }
/* « J'envoie » sans rien à envoyer : centré (O/pos_restaurant/…/actionpad_widget.js:35-36, swapButtonClasses :
   « btn-light pe-none disabled justify-content-center » ; capture 09) */
#t17-pos .rs-envoyer:not(.actif) { justify-content: center; }
#t17-pos .rs-envoyer:not(.actif) .rs-cpts { display: none; }
/* -- la pile des familles et des tuiles -- */
.t17-pile { flex: 1; min-height: 0; display: grid; }
.t17-et { grid-area: 1 / 1; display: flex; flex-direction: column; gap: 14px; min-height: 0; }
/* -- contraste WCAG AA (contrôle de hyperframes) : « %% » et « Prix » grisés, et la quantité sur la tuile, un ton
   plus foncés que le gris d'Odoo (#6C757D : 4,2:1 sur la touche, 2,3:1 sur la tuile lavande) -- */
#t17-pos .rs-pk.gris { color: #5C636A; }
#t17-pos .rs-tuile-q { color: #495057; }
""" % demo.AVATARS_RESTO[NOM_P])


# ================================================================ les gestes --
def touche(sel, *effets, d=0.5, fx=0.5, fy=0.5):
    """Un toucher : le curseur, l'appui, puis ses effets au moment de l'appui."""
    gestes = [clic(sel, d=d, fx=fx, fy=fy)]
    for k, effet in enumerate(effets):
        effet = dict(effet, avec=True)
        if k == 0:
            effet['decale'] = d + 0.08
        gestes.append(effet)
    return gestes


def taper(fen, chiffres, d=0.32):
    """Un code tapé dans la fenêtre ``fen`` : les points se remplissent, le chiffre ne s'affiche jamais."""
    gestes = []
    for k, c in enumerate(chiffres):
        gestes += touche('#%s-k%s' % (fen, c), classe('#%s-p%d' % (fen, k), ajouter=['plein']), d=d)
    return gestes


def bascule(avant, apres):
    """Un état remplace l'autre, sans transition (une colonne, une rangée de familles)."""
    return [cacher(avant, d=0.05), montrer(apres, d=0.05, y=0, avec=True)]


def tuile(ident, nom, q, *effets, d=0.5):
    """Un produit touché : sa quantité sur la tuile (product_card.xml:24), puis ses effets sur l'addition."""
    sel = '#%s-%s' % (ident, cle(nom))
    return touche(sel, texte(sel + '-q', str(q)), classe(sel + '-q', ajouter=['on']), *effets, d=d)


def vers_commande(vue_):
    return [vue(vue_, 'pos'), classe('#' + POS, ajouter=['sur-commande', 'avec-emp'], retirer=['sur-plan']),
            texte('#%s-onglet' % POS, str(TABLE))]


def vers_plan():
    return [vue('t17-plan', 'pos'), classe('#' + POS, ajouter=['sur-plan'], retirer=['sur-commande', 'avec-emp']),
            texte('#%s-onglet' % POS, 'Table')]


C1E, C2E = '#t17-c1-e%d', '#t17-c2-e%d'

ETAPES = [
    # 1. Prisca ouvre la caisse : son code, le contrôle d'ouverture, « J'ouvre la caisse » (5 touches).
    {'temps': 0, 'titre': 'La caissière ouvre la caisse',
     'texte': 'Son code, puis « J\'ouvre la caisse » : 5 touches. Le fond de caisse est déjà rempli.',
     'voix': "Le matin, sur la tablette, la fenêtre du code s'ouvre toute seule : la caisse est encore fermée. "
             "Prisca, la caissière, tape son code. Le fond de caisse est déjà rempli. J'ouvre la caisse : cinq "
             "touches. La caisse garde le nom de celle qui l'a ouverte, et le plan se verrouille aussitôt.",
     'gestes': [pause(0.4), ouvrir('t17-code'), pause(0.2), anneau('#t17-code-titre', d=1.0),
                anneau('#t17-plan-fermee', d=1.6), pause(0.1)]
               + taper('t17-code', CODE_P)
               # le code accepté, le contrôle d'ouverture d'Odoo s'ouvre aussitôt, au nom de Prisca
               + [fermer('t17-code'), texte('#%s-emp-n' % POS, NOM_P, avec=True),
                  texte('#%s-emp-av' % POS, NOM_P[0], avec=True),
                  classe('#' + POS, ajouter=['avec-emp', 't17-prisca'], avec=True), ouvrir('t17-ouv', avec=True, decale=0.1),
                  curseur('#t17-ouv-fond', fx=0.3, d=0.5), anneau('#t17-ouv-fond', d=1.3, avec=True, decale=0.2)]
               + touche('#t17-ouv-ok', fermer('t17-ouv'), classe('#' + POS, retirer=['avec-emp', 't17-prisca']),
                        classe('#t17-plan-ecran', ajouter=['ouverte']), d=0.5)
               + [pause(0.3), anneau('#t17-plan-etat', d=1.4),
                  bulle('b-r3', T4, cote='droite', d=2.8), pause(1.8)]},
    # 2. Loïc touche la table 4, tape son code ; la table est libre : combien de personnes ?
    {'temps': 1, 'titre': 'Toucher la table, taper son code',
     'texte': 'Table 4 : votre code, puis combien de personnes. Un gros bouton, et la table est ouverte.',
     'voix': "Loïc accueille quatre clients. Sur le plan, il touche la table quatre et tape son code. La table est "
             "libre : la même fenêtre demande combien ils sont. Il touche quatre, et la table s'ouvre à son nom.",
     'gestes': [classe('#tu-perso', ajouter=['t17-loic']), pause(0.3)]
               + touche(T4, ouvrir('t17-tab'), d=0.7)
               + [pause(0.3)] + taper('t17-tab', CODE_L)
               + [pause(0.3), cacher('#t17-tab-code', d=0.12), montrer('#t17-tab-pers', d=0.15, y=0, avec=True),
                  texte('#t17-tab-titre', TITRES_RESTO['personnes'](TABLE), avec=True),
                  curseur('#t17-tab-n4', fx=0.7, fy=0.75, d=0.5),
                  bulle('b-zero', '#t17-tab-pers', cote='droite', d=2.6), pause(1.6)]
               + touche('#t17-tab-n4', fermer('t17-tab'), *vers_commande('t17-c1'),
                        texte('#%s-emp-n' % POS, NOM_L), texte('#%s-emp-av' % POS, NOM_L[0]), d=0.5)
               + [pause(0.6)]},
    # 3. L'écran de commande : la phrase d'état, puis la carte par familles.
    {'temps': 1, 'titre': "L'écran de commande, par familles",
     'texte': 'Table 4 · ouverte par Loïc. Nourriture › Pizzas, puis Boisson › Alcoolisé › Bière.',
     'voix': "L'écran de commande dit d'abord où l'on en est : table quatre, ouverte par Loïc. La carte est rangée "
             "par familles. Nourriture, puis Pizzas : une marguérita. Boisson, Alcoolisé, puis Bière : deux blondes. "
             "Sur J'envoie, la caisse compte ce qui va partir, famille par famille.",
     # « marguérita » : pour la voix seulement (Kokoro lit « margherita » maʁɡʁita, sans le « é »)
     # (revue) les touches suivent la voix : « Nourriture, puis Pizzas » est dit après « La carte est rangée par
     # familles » ; la seconde rangée (Boisson › Alcoolisé › Bière, deux blondes) se dit plus vite qu'elle ne se
     # touche : touches resserrées (d=0.25), les deux blondes tombent sur « la caisse compte ce qui va partir ».
     'gestes': [pause(0.5), anneau('#t17-c1v-etat', d=2.4), pause(0.6), curseur(C1E % 0 + '-fa-f-nourriture', d=0.8),
                pause(1.1)]
               + touche(C1E % 0 + '-fa-f-nourriture', *bascule(C1E % 0, C1E % 1), d=0.38)
               + touche(C1E % 1 + '-fa-f-pizzas', *bascule(C1E % 1, C1E % 2), d=0.38)
               + tuile('t17-c1-e2-tu', MARGHERITA, 1, *bascule('#t17-c1v-g', '#t17-c1-g'), d=0.38)
               + touche(C1E % 2 + '-fa-f-boisson', *bascule(C1E % 2, C1E % 3), d=0.25)
               + touche(C1E % 3 + '-fa-f-alcoolise', *bascule(C1E % 3, C1E % 4), d=0.25)
               + touche(C1E % 4 + '-fa-f-biere', *bascule(C1E % 4, C1E % 5), d=0.25)
               + tuile('t17-c1-e5-tu', BLONDE, 1, classe('#t17-c1-l1', retirer=['choisie']),
                       montrer('#t17-c1-l2', d=0.15, y=0), texte('#t17-c1-total', fcfa(PRIX[MARGHERITA] + PRIX[BLONDE])),
                       texte('#t17-c1-env-1-v', '1'), classe('#t17-c1-env-1', ajouter=['on']), d=0.25)
               + tuile('t17-c1-e5-tu', BLONDE, 2, texte('#t17-c1-l2-q', '2,00'),
                       texte('#t17-c1-l2-m', fcfa(2 * PRIX[BLONDE])), texte('#t17-c1-total', fcfa(TOTAL_1)),
                       texte('#t17-c1-env-1-v', '2'), d=0.25)
               # pas de zoom : « J'envoie » est au bord bas du navigateur, que la légende couvrirait
               + [pause(0.1), curseur('#t17-c1-envoyer', fx=0.3, d=0.4),
                  bulle('b-compte', '#t17-c1-envoyer', cote='haut', d=2.6), pause(1.4)]},
    # 4. « J'envoie » : la notification, le plan verrouillé, la table 4 verte.
    {'temps': 2, 'titre': "J'envoie, et le plan revient",
     'texte': '« %s » La table 4 passe au vert ; plus personne n\'est identifié.' % TEXTES_RESTO['envoye'](ENVOI_1),
     'voix': "J'envoie : la commande part, la caisse le confirme et revient au plan. La table quatre est verte, et le "
             "nom de Loïc a disparu : pour retoucher à sa table, il lui faudra de nouveau son code.",
     # (revue) dans l'ordre de la voix : la notification se lit pendant « la caisse le confirme » ; l'anneau sur la
     # table 4 tombe sur « La table quatre est verte », celui de la phrase d'état sur « le nom de Loïc a disparu » ;
     # la réaction se referme avec l'étape.
     'gestes': touche('#t17-c1-envoyer', *vers_plan(), classe(T4, ajouter=['vert', 'avec-duree'], retirer=['libre']),
                      texte(T4 + '-d', duree_resto(0)), notifier('t17-n1', duree=3.8), d=0.6)
               + [pause(1.0), curseur(T4, fx=0.75, fy=0.75, d=1.0),
                  anneau(T4, d=1.4, avec=True, decale=1.1), pause(0.3), anneau('#t17-plan-etat', d=1.4),
                  bulle('b-verrou', T4, cote='droite', d=2.8), pause(2.3), reaction('r-verrou', d=2.2),
                  pause(1.4)]},
    # 5. Douze minutes plus tard : la table, le code ; « 4 personnes », puis 6.
    {'temps': 3, 'titre': 'Revenir à sa table',
     'texte': '12 minutes plus tard : la table, le code, l\'addition s\'ouvre. « 4 personnes », puis 6 : deux touches.',
     'voix': "Douze minutes plus tard, deux amis les rejoignent. Loïc touche sa table et tape son code : l'addition "
             "s'ouvre telle qu'il l'a laissée, sans redemander les personnes. Il touche quatre personnes ; au-delà "
             "de huit, il y a neuf et plus. Puis six : deux touches, et c'est corrigé.",
     'gestes': [texte(T4 + '-d', duree_resto(DUREE_RETOUR)), pause(0.2), anneau(T4, d=1.0)]
               + touche(T4, ouvrir('t17-tab2'), d=0.6, fy=0.3)
               + [pause(0.15)] + taper('t17-tab2', CODE_L)
               + [pause(0.15), fermer('t17-tab2')] + [dict(g, avec=True) for g in vers_commande('t17-c2')]
               + [pause(0.4), anneau('#t17-c2v-l2', d=1.2), pause(0.1)]
               + touche('#t17-c2v-pers', ouvrir('t17-pers'))
               # (revue) « 6 » est touché sur « Puis six », avant « c'est corrigé » ; la bulle se referme avant la fenêtre
               + [pause(0.2), bulle('b-plus', '#t17-pers-plus', cote='droite', d=2.1), pause(0.75)]
               + touche('#t17-pers-n6', fermer('t17-pers'), texte('#t17-c2v-pers', TEXTES_RESTO['personnes'](6)))
               + [pause(0.4), reaction('r-table', d=2.6), pause(0.3)]},
    # 6. Deux bières de plus, puis ⌫ ⌫ : elles s'en vont ; les deux parties restent.
    {'temps': 3, 'titre': "Retirer ce qui n'est pas parti",
     'texte': '⌫ ⌫ : les bières pas encore envoyées s\'en vont, sans code ni trace ; les deux déjà parties restent.',
     'voix': "Il ajoute deux bières, puis les amis se ravisent. Deux fois la touche effacer : les bières pas encore "
             "envoyées s'en vont, sans code ni trace. Les deux déjà parties, elles, restent sur l'addition.",
     'gestes': tuile('t17-c2-e0-tu', BLONDE, 3, *bascule('#t17-c2v-g', '#t17-c2-g'))
               + tuile('t17-c2-e0-tu', BLONDE, 4, texte('#t17-c2-l2-q', '4,00'),
                       texte('#t17-c2-l2-m', fcfa(4 * PRIX[BLONDE])), texte('#t17-c2-total', fcfa(TOTAL_1 + 2 * PRIX[BLONDE])),
                       texte('#t17-c2-env-0-v', '2'))
               + [pause(0.5)] + touche('#t17-c2-keff', d=0.6) + [pause(0.2)]
               + touche('#t17-c2-keff', texte('#t17-c2-l2-q', '2,00'), texte('#t17-c2-l2-m', fcfa(2 * PRIX[BLONDE])),
                        classe('#t17-c2-l2', ajouter=['envoyee']), texte('#t17-c2-total', fcfa(TOTAL_1)),
                        classe('#t17-c2-env-0', retirer=['on']), classe('#t17-c2-envoyer', retirer=['actif']),
                        classe('#t17-c2-encaisser', ajouter=['actif']), texte('#t17-c2-e0-tu-%s-q' % cle(BLONDE), '2'),
                        d=0.25)
               + [pause(0.5), zoom('#t17-c2-l2', s=1.5, d=0.8), bulle('b-parti', '#t17-c2-l2', cote='droite', d=2.8),
                  pause(2.3), dezoom(d=0.6)]},
    # 7. Deux colas, « J'envoie » : « Envoyé : 2 Sodas. », le plan revient.
    {'temps': 3, 'titre': 'Ajouter, et renvoyer',
     'texte': 'Deux colas dans Sodas, « J\'envoie » : « %s », et le plan revient, verrouillé.'
              % TEXTES_RESTO['envoye'](ENVOI_2),
     # (revue) dans l'ordre de l'image : les familles, puis les deux colas
     'voix': "Non alcoolisé, puis Sodas : les amis prendront plutôt deux colas. J'envoie : la caisse annonce deux "
             "sodas partis, et le plan revient, verrouillé. La table quatre reste verte, ouverte depuis douze minutes.",
     'gestes': touche(C2E % 0 + '-fa-f-nonalcoolise', *bascule(C2E % 0, C2E % 1), d=0.45)
               + touche(C2E % 1 + '-fa-f-sodas', *bascule(C2E % 1, C2E % 2), d=0.38)
               + tuile('t17-c2-e2-tu', COLA, 1, classe('#t17-c2-l2', retirer=['choisie']),
                       montrer('#t17-c2-l3', d=0.15, y=0), texte('#t17-c2-total', fcfa(TOTAL_1 + PRIX[COLA])),
                       texte('#t17-c2-env-1-v', '1'), classe('#t17-c2-env-1', ajouter=['on']),
                       classe('#t17-c2-envoyer', ajouter=['actif']), classe('#t17-c2-encaisser', retirer=['actif']),
                       d=0.38)
               + tuile('t17-c2-e2-tu', COLA, 2, texte('#t17-c2-l3-q', '2,00'), texte('#t17-c2-l3-m', fcfa(2 * PRIX[COLA])),
                       texte('#t17-c2-total', fcfa(TOTAL_2)), texte('#t17-c2-env-1-v', '2'), d=0.38)
               + [pause(0.2)]
               + touche('#t17-c2-envoyer', *vers_plan(), notifier('t17-n2', duree=3.6), d=0.5)
               + [pause(0.3), curseur(T4, fx=0.75, fy=0.75, d=0.6), pause(1.6),
                  anneau(T4, d=1.8), pause(1.2)]},
]

TUTORIEL = {
    'slug': 't17-restaurant-servir-une-table',
    'profil': 't17_restaurant_servir_une_table',
    'numero': 17,
    'titre': 'Ouvrir la caisse et servir une table',
    'fonction': 'Service à table',
    'personnage': demo.POSTES_RESTO['serveur'],
    'accroche': {
        'kicker': 'En salle',
        # Les douleurs : docs/PERIMETRE_FONCTIONNEL_RESTAURANT.md, REST-02 (:154 : la session ouverte sous le compte
        # Odoo, « qui n'est pas un employé à code », C74 ; « ce nom unique est réécrit à chaque produit ajouté »,
        # C7), REST-06 (:240 : « il n'est pas demandé ; il vaut 1 d'office », C18), C4 (:1215 : verrouillage à la
        # main seulement, retour au plan sans déconnexion).
        'question': 'Qui a servi la *table* 4 ?',
        'douleurs': [('cle', 'La caisse ouverte sous un compte, pas par une personne'),
                     ('personne', 'Le nom du serveur réécrit à chaque produit'),
                     ('interrogation', 'Combien de personnes ? Jamais demandé'),
                     ('cadenas', 'Le poste reste au nom du dernier serveur')],
        'voix': "Qui a ouvert la caisse, qui a servi la table quatre, et pour combien de personnes ? Quand le poste "
                "reste au nom du dernier serveur, plus personne ne le sait.",
    },
    'revelation': {
        # Notes de version :37-43 (le parcours en trois règles) ; pos_store.js:825-922 ; actionpad_widget.js:43-44.
        'promesse': 'On touche la table, on tape son code, on dit combien on est ; après « J\'envoie », le plan revient, '
                    'verrouillé.',
        'voix': "Avec Aïte haousse, chaque table commence par un code, et chaque envoi rend le plan.",
    },
    'temps': ['Ouvrir', 'Servir', 'Envoyer', 'Corriger'],
    'app': POS,
    'ecran': ECRAN,
    'css': CSS,
    'vues_initiales': {'pos': 't17-plan'},
    'bulles': {
        'b-r3': "Le code d'un serveur n'ouvre pas la caisse : il faut la caissière ou un chef de salle.",
        'b-zero': 'Pas de bouton zéro : il faut au moins une personne à table.',
        'b-compte': '« J\'envoie » compte ce qui n\'est pas encore parti, famille par famille.',
        'b-verrou': '« J\'envoie », « Plan », l\'encaissement : tout retour au plan oublie l\'employé.',
        'b-plus': 'Plus de huit ? « 9 et plus », puis le nombre.',
        'b-parti': 'Ce qui est parti ne s\'efface plus sans le code d\'un chef de salle.',
    },
    'reactions': {
        'r-verrou': 'Rien à verrouiller : le plan s\'en charge.',
        'r-table': 'Ma table reste à mon nom.',
    },
    'etapes': ETAPES,
    'resultats': {
        'titre': 'Le service, touche par touche',
        'cartes': [
            {'valeur': '5', 'compter': 5, 'unite': 'touches', 'icone': 'cle',
             'texte': 'pour ouvrir la caisse le matin : le code de la caissière, puis « J\'ouvre la caisse »'},
            {'valeur': '7', 'compter': 7, 'unite': 'touches', 'icone': 'personne',
             'texte': 'pour ouvrir une table et l\'envoyer : la table, le code, les personnes, « J\'envoie », '
                      'plus le choix des produits'},
            {'valeur': '2', 'compter': 2, 'unite': 'touches', 'icone': 'echange',
             'texte': 'pour changer le nombre de personnes : le bouton, puis le nombre'},
        ],
        'voix': "Cinq touches pour ouvrir la caisse, sept pour ouvrir une table et l'envoyer, plus les produits, deux "
                "pour changer le nombre de personnes.",
    },
    'cta': {
        'appel': 'Demandez votre démonstration',
        'sous_marque': demo.SOUS_MARQUE_RESTO,
        'suivant': 'Le plan en couleurs',
        'voix': "Aïte haousse, par Aïte Consulting. Demandez votre démonstration. Prochain tutoriel : le plan en "
                "couleurs.",
    },
    'vignette': {'etape': 3, 'apres': 13.2},
}


def _typo(texte_):
    """Les textes à l'écran écrits ici (pas la voix) : une espace insécable dans les guillemets et avant « : »,
    « ; », « ? », pour qu'un signe ne passe pas seul à la ligne (comme S/utils/messages.js:7-9)."""
    for avant, apres in (('« ', '«\u00a0'), (' »', '\u00a0»'), (' :', '\u00a0:'), (' ;', '\u00a0;'), (' ?', '\u00a0?')):
        texte_ = texte_.replace(avant, apres)
    return texte_


for _etape in ETAPES:
    _etape['titre'], _etape['texte'] = _typo(_etape['titre']), _typo(_etape['texte'])
for _groupe in ('bulles', 'reactions'):
    TUTORIEL[_groupe] = {_k: _typo(_v) for _k, _v in TUTORIEL[_groupe].items()}
for _carte in TUTORIEL['resultats']['cartes']:
    _carte['texte'] = _typo(_carte['texte'])
TUTORIEL['revelation']['promesse'] = _typo(TUTORIEL['revelation']['promesse'])
TUTORIEL['accroche']['douleurs'] = [(_i, _typo(_t)) for _i, _t in TUTORIEL['accroche']['douleurs']]
