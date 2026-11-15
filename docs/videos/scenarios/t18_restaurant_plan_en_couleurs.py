# -*- coding: utf-8 -*-
"""Tutoriel 18 — Le plan en couleurs.

Le troisième des huit tutoriels du restaurant (lot 1 : aite_pos_restaurant ; incrément 5, REST-16 et REST-17).
Un restaurant SANS hôtel (demo.RESTO, demo.SOCIETE_RESTO) ; toute la vidéo se passe sur la caisse plein écran, au
service à table contrôlé (ecrans.fenetre_resto), sans écran de gestion. Storyboard : scratchpad videos_resto/
storyboards/t18.md (adapté : voir « Écarts au storyboard » plus bas).

Abréviations : R/ = addons/aite_pos_restaurant/ ; S/ = R/static/src/ ; O/ = ../odoo18/addons/ ;
N = docs/NOTES_DE_VERSION_restaurant_lot1.md ; P = docs/PERIMETRE_FONCTIONNEL_RESTAURANT.md ;
rec = recette/cas_de_test.py ; C/nn = captures/restaurant/nn_*.jpg (modèles visuels, jamais incrustés).
Les phrases du produit sont relues dans le code au chargement (garde-fous plus bas) : une phrase changée dans le
module fait échouer la construction de la vidéo au lieu de la rendre fausse.

Personnage : Loïc, serveur (demo.POSTES_RESTO['serveur']). Second rôle, par son nom seulement (barre de la caisse,
légende, voix) : Landry, chef de salle (demo.POSTES_RESTO['chef']) ; Inès (serveuse) n'apparaît que par ses tables.

Le monde rejoué (conditions écrites ici, pour que chaque image soit vraie) :
- le 14/10/2026, jour de référence de la série ; aucune date ni heure n'est affichée à la caisse ; la caisse
  « Restaurant » est ouverte (le matin, par la caissière : tutoriel 17) ; délai de la caisse : 60 minutes, celui
  que la case pose (R/models/pos_config.py:36, regles.DELAI_ALERTE) ; horloges des tablettes à l'heure (N §6,
  l.532-534 : durée et couleur sont comptées par chaque poste) ;
- la caisse a une imprimante de tickets : « Addition » imprime et rend le plan (S/overrides/control_buttons.js:
  73-88 ; sans imprimante, Odoo ouvre un aperçu, une touche de plus : N §8 l.663-666) ; pas d'imprimante de
  préparation, comme les captures et les tours (R/tests/test_tours.py:41-43), et comme t19 qui ne montre pas le bon
  d'annulation (DESIGN.md, « Le restaurant ») : la pastille rouge d'une table compte alors tous les produits pas
  encore envoyés (O/point_of_sale/static/src/app/models/utils/order_change.js:56-60, ``prepaCategoryIds.size === 0``).
  Avec des imprimantes de préparation, elle ne compterait que les produits d'une famille qui a la sienne
  (O/pos_restaurant/static/src/app/floor_screen/floor_screen.js:941-957 ; O/point_of_sale/static/src/app/store/
  pos_store.js:1101-1106) : sans effet sur ce que la vidéo montre si elles couvrent la Nourriture et la Boisson
  (``parentPosCategIds``), voir les écarts (ECARTS.md n° 95) ; la journée commune : demo.TABLES_JOUR_RESTO ;
- la chronologie des tables (heure d'ouverture posée par le serveur, R/models/pos_order.py ; N l.107) :

    table  ouverte par  à      12:50 (1)     12:51 (2)   12:53 (3-4)      12:55 (5)   13:00 (5-6)
    4      Loïc         12:15  35 min        36 min      38 min           —           45 min
    6      Inès         12:28  22 min        23 min      25 min           —           32 min
    7      Inès         11:45  1 h 05 orange 1 h 06      1 h 08           —           1 h 15
    10     Loïc         11:52  58 min        59 min      1 h 01 orange    —           1 h 08
    2      Loïc         12:55  libre         libre       libre            0 min       5 min (+ pastille « 2 »)

  calculée plus bas (DUREES) par la règle de la caisse : couleur ``alerte`` (S/utils/alerte.js:18-27, ``>=``),
  durée ``TEXTES.duree`` (S/utils/messages.js:165-171). Aucune table n'est montrée à « 1 h 00 » (orange alors que la
  légende dit « plus de 60 min » : ECARTS.md n° 82) : la table 10 passe de « 59 min » à « 1 h 01 ». Cohérente avec
  le storyboard de t19 (plan de 13:48 : 2 « 53 min », 4 « 1 h 33 » ; 6, 7 et 10 encaissées).
- la carte de demo.CARTE_RESTO : table 10, 2 × Pizza Reine et 4 × Bière blonde 65 cl, tout envoyé (18 000 FCFA) ;
  table 2, 2 × Cola 33 cl (famille « Sodas »).

Écrans et libellés (tous rejoués par ecrans.py, « La caisse du restaurant ») :
- le plan verrouillé (C/03, C/07, C/08) : barre « Plan », « Table », logo, ≡ ; pas de nom, pas de cadenas, pas de
  « + » (S/overrides/navbar.xml:18-23 ; S/overrides/order_tabs.xml) ; bouton « Salle » (pos_config.py:82) ;
  phrase d'état TEXTES.planEtat « Touchez une table, puis tapez votre code. » (S/utils/messages.js:97 ;
  S/overrides/floor_screen.xml:27-28) ; tables gris / vert / orange, durée sous le numéro
  (S/overrides/floor_screen.js:72-87 ; floor_screen.xml:31-44) ; légende TEXTES.legendeParties(60)
  (messages.js:150-158 ; floor_screen.xml:45-53 ; C/07 et C/08) ; pastille rouge de la table, cercle, chiffre
  des articles pas encore envoyés (O/pos_restaurant/static/src/app/floor_screen/floor_screen.xml:150-160 ;
  aucune capture) ;
- la fenêtre du code « Table 10 — votre code », « Table 2 — votre code » (TITRES.table, messages.js:73 ; C/04) :
  quatre points, pavé, « Retour » ; une table occupée n'a pas l'étape des personnes (S/store/pos_store.js:897-910) ;
- l'écran de commande (C/06) : « Plan », onglet « 10 » / « 2 », « Rechercher des produits… », code-barres, avatar
  et prénom (Loïc, puis Landry) ; phrase d'état « Table 10 · ouverte par Loïc · 1 h 01 » (pos_store.js:1136-1151 ;
  S/overrides/product_screen.xml:13-16 ; messages.js:114-116, 165-171) ; lignes, « Total » ; « 4 personnes »,
  « Addition » (grisé sans ligne), « Client », « Note cuisine », « Actions » (S/overrides/control_buttons.xml:17-34) ;
  pavé (« % » et « Prix » grisés pour un serveur), sauf sur la table 10 rouverte sans ligne choisie (pas de pavé,
  « Note cuisine » grisé : C/09) ; « J'envoie » (primaire avec « Sodas 2 », gris sans rien à
  envoyer) et « J'encaisse » (primaire quand tout est parti) (S/overrides/actionpad_widget.xml:13-18 ;
  O/pos_restaurant/…/actionpad_widget.js:56-62) ; addition vide : panier, « Commencez à ajouter des produits »,
  « Libérer la table » (t17) ;
- la notification « Envoyé : 2 Sodas. » (TEXTES.envoye, messages.js:103 ; S/overrides/actionpad_widget.js:24-26,
  43-44 ; C/07, C/08).

Règles dites par la voix, la légende et les bulles :
- le plan est l'écran de repos, verrouillé : N §1 règle 2 (l.40-43) ; pos_store.js:426-429, 440-455 ; rec R63 ;
- gris libre, vert ouverte, orange : légende ; rec R64, R66 ;
- durée sous le numéro, recalculée toutes les 30 secondes sans toucher l'écran : S/utils/alerte.js:11-14 (TIC),
  floor_screen.js:36-42 ; N §2 l.134-137 ; rec R66, R71 ; comptée depuis la première ouverture, même après un
  déplacement : N l.136 ; rec R70 ;
- 60 minutes par défaut, réglé caisse par caisse, appliqué à la réouverture : pos_config.py:36, 95-102 ; rec R69 ;
- « Table, code, Addition : 6 touches » : N §3 l.251 ; la même durée dans la phrase d'état : rec R71 ;
- l'addition imprimée rend le plan, verrouillé : control_buttons.js:81-84 ;
- 5 minutes sans toucher l'écran : fenêtres fermées, retour au plan verrouillé, sans écran de veille :
  pos_store.js:619-652, 440-443 ; regles.DELAI_RETOUR_PLAN (R/models/regles.py:50) ; N §1 l.43, §2 l.89, §5 ;
  rec R67 (choix écrit, écart à Q17 : point à valider n° 1, N §10 l.794-797) ;
- le chef de salle ouvre la table d'un collègue : droit « table_collegue », caissière et au-dessus
  (regles.py:35 ; pos_store.js:504-515) ; la voix le dit avec les mots de R4, « Seuls {Nom}, la caissière ou un
  chef de salle peuvent la modifier » (messages.js:26-28) ; « J'envoie » : notification puis plan verrouillé
  (S/overrides/actionpad_widget.js:16-45) ;
- les douleurs de l'accroche : P, REST-16 et REST-17, « Couverture » (l.394, 410 : pas de durée, écran de veille
  qui cache le plan, la table n'affiche que son numéro et une pastille, couleur de table choisie au dessin) ;
  §2 besoin 10 (l.93 : « Il arrive qu'une addition soit oubliée »).

Écarts au storyboard (le code fait foi) :
- l'équipe est celle de demo.EQUIPE_RESTO : Loïc pour « Yannick » (déjà dans le dépôt, t16) ;
- pas de pastille rouge sur le bouton « Salle » : Odoo l'affiche si ``getFloorChangeCount(floor) > 0``
  (floor_screen.xml:14-15), mais ce total additionne des objets ``{changes, skip}`` (floor_screen.js:896-907,
  ``changeCount += this.getChangeCount(table) || 0``) : il devient « 0[object Object]… », jamais > 0 (exécuté avec
  node). Le garde-fou ``_PASTILLE_SALLE`` relit ce code ;
- la table 2 est montrée dès son ouverture (« 0 min », 12:55) et le plan revient 5 minutes plus tard
  (« 5 min », 13:00), au lieu de 12:58 / 13:03 : le décompte des 5 minutes et la durée de la table se lisent
  ensemble ;
- la vidéo ne dit pas que la pastille compte « toutes » les familles : vrai sans imprimante de préparation, faux
  avec une imprimante qui ne couvre pas toute la carte (voir le monde rejoué) ;
- l'écran de commande de la table 10 montre les familles racines et toute la carte : Odoo garde la famille
  choisie par poste (``pos.selectedCategory``, O/point_of_sale/static/src/app/store/pos_store.js:1058-1067, jamais
  remise à zéro à l'ouverture d'une table) ; la vidéo prend l'état d'un poste où personne n'a encore choisi de
  famille (rec R29). Celui de la table 2 est sur Boisson › Non alcoolisé › Sodas, que Loïc vient de choisir.
"""

import ast
import os
import unicodedata

import demo
from ecrans import (ESP, TEXTES_RESTO, TITRES_RESTO, css_personnage, duree_resto, etat_commande, fcfa, fenetre_resto,
                    navigateur, resto_code, resto_commande, resto_familles, resto_ligne, resto_notification, resto_plan,
                    resto_salle, resto_tuiles)
from marketing import bulle, dezoom, reaction, zoom
from moteur import anneau, animer, cacher, clic, classe, curseur, fermer, montrer, notifier, ouvrir, pause, texte, vue

RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
R = os.path.join(RACINE, 'addons', 'aite_pos_restaurant')
S = os.path.join(R, 'static', 'src')
O = os.path.join(os.environ.get('ODOO_DIR', os.path.join(RACINE, '..', 'odoo18')), 'addons')


def _lire(*chemin):
    with open(os.path.join(*chemin), encoding='utf-8') as f:
        return f.read()


def source(relatif, nom):
    """Une constante d'un module Python du restaurant, lue dans son fichier (analyse, sans importer Odoo)."""
    for noeud in ast.parse(_lire(R, relatif)).body:
        if isinstance(noeud, ast.Assign) and any(getattr(c, 'id', None) == nom for c in noeud.targets):
            return ast.literal_eval(noeud.value)
    raise ValueError('t18 : %s introuvable dans %s' % (nom, relatif))


def dans(texte_source, extrait, ou):
    assert extrait in texte_source, 't18 : « %s » introuvable dans %s' % (extrait, ou)


# ============================================================ garde-fous --
# Les textes de la caisse : S/utils/messages.js (recopiés par ecrans.TEXTES_RESTO) ; relus ici, mot pour mot.
_MESSAGES = _lire(S, 'utils', 'messages.js')
for _extrait in ('planEtat: "Touchez une table, puis tapez votre code."',
                 'table: (numero) => `Table ${numero} — votre${ESP}code`',
                 'envoye: (compte) => `Envoyé${ESP}: ${compte}.`',
                 'table: (numero) => `Table ${numero}`',
                 'ouvertePar: (nom) => `ouverte par ${nom}`',
                 'addition: "Addition"',
                 'cle: "libre", texte: `Gris${ESP}: libre`',
                 'cle: "vert", texte: `Vert${ESP}: ouverte`',
                 "texte: `Orange${ESP}: ouverte depuis plus de ${delai}${ESP}min, proposez l'addition`",
                 'cle: "pastille", texte: `Pastille rouge${ESP}: pas encore envoyé`',
                 'return `${minutes} min`;',
                 'return `${heures} h ${String(minutes % 60).padStart(2, "0")}`;',
                 # R4 : la table d'un collègue, que « la caissière ou un chef de salle » peuvent modifier (voix, étape 6)
                 '"ou un chef de salle peuvent la modifier."'):
    dans(_MESSAGES, _extrait, 'S/utils/messages.js')
assert [t.replace(ESP, ' ') for _c, t in TEXTES_RESTO['legendeParties'](demo.DELAI_ORANGE)] == [
    'Gris : libre', 'Vert : ouverte', "Orange : ouverte depuis plus de 60 min, proposez l'addition",
    'Pastille rouge : pas encore envoyé']
# La couleur et la minuterie : S/utils/alerte.js (orange dès le délai atteint, « >= »), S/overrides/floor_screen.js.
_ALERTE = _lire(S, 'utils', 'alerte.js')
for _extrait in ('export const DELAI_ALERTE = 60;', 'export const TIC = 30000;',
                 'return (Number(minutes) || 0) >= seuil ? "orange" : "vert";'):
    dans(_ALERTE, _extrait, 'S/utils/alerte.js')
dans(_lire(S, 'overrides', 'floor_screen.js'), 'minuterie = setInterval(() => this.pos.aiteTic(), TIC);',
     'S/overrides/floor_screen.js')
_PLAN_XML = _lire(S, 'overrides', 'floor_screen.xml')
for _extrait in ('t-esc="aiteTextes.planEtat"', 't-foreach="aiteLegende"', 'class="aite-duree'):
    dans(_PLAN_XML, _extrait, 'S/overrides/floor_screen.xml')
# Le retour au plan : 5 minutes sans activité (regles.DELAI_RETOUR_PLAN, envoyé à la caisse), pas d'écran de veille,
# l'addition imprimée et « J'envoie » rendent le plan.
assert source('models/regles.py', 'DELAI_RETOUR_PLAN') == 300
assert source('models/regles.py', 'DELAI_ALERTE') == demo.DELAI_ORANGE
_STORE = _lire(S, 'store', 'pos_store.js')
for _extrait in ('timeout: (this.session._aite_delai_retour_plan || 300) * 1000,',
                 'action: () => this.aiteRetourAuPlanSansActivite(),',
                 'if (name === "SaverScreen") {\n            return false;',
                 'const nom = order.table_id?.table_number ?? order.floating_order_name;',
                 # une table déjà ouverte n'a pas l'étape des personnes (voix de l'étape 4)
                 'if (this.isOrderTransferMode || !this.aiteTableLibre(tete)) {\n            return false;'):
    dans(_STORE, _extrait, 'S/store/pos_store.js')
_BOUTONS = _lire(S, 'overrides', 'control_buttons.js')
dans(_BOUTONS, 'this.dialog.closeAll();\n            this.pos.showScreen("FloorScreen");',
     'S/overrides/control_buttons.js')
dans(_lire(S, 'overrides', 'control_buttons.xml'), '<button t-if="pos.config.iface_printbill"',
     'S/overrides/control_buttons.xml')
dans(_lire(R, 'models', 'pos_config.py'), "'iface_printbill': True,", 'R/models/pos_config.py (REGLAGES_DU_MODE)')
_ENVOI = _lire(S, 'overrides', 'actionpad_widget.js')
dans(_ENVOI, 'this.pos.notification.add(TEXTES.envoye(compte), { type: "info" });\n        '
             'this.pos.showScreen("FloorScreen");', 'S/overrides/actionpad_widget.js')
_ENVOI_XML = _lire(S, 'overrides', 'actionpad_widget.xml')
for _extrait in (">J'envoie</t>", '"J\'encaisse"'):
    dans(_ENVOI_XML, _extrait, 'S/overrides/actionpad_widget.xml')
# Le chef de salle ouvre la table d'un collègue (droit « table_collegue », caissière et au-dessus).
_NIVEAUX = [c for c, _l in source('models/regles.py', 'NIVEAUX')]
_DROITS = source('models/regles.py', 'DROITS')
assert _NIVEAUX.index('superviseur') >= _NIVEAUX.index(_DROITS['table_collegue']) > _NIVEAUX.index('serveur')
# La pastille rouge d'une table (Odoo) : le nombre d'articles pas encore envoyés, en cercle rouge.
_PLAN_ODOO = _lire(O, 'pos_restaurant', 'static', 'src', 'app', 'floor_screen', 'floor_screen.xml')
dans(_PLAN_ODOO, "'text-bg-danger': data.changes,", 'O/pos_restaurant/…/floor_screen.xml')
# La pastille du bouton « Salle » n'apparaît jamais (somme d'objets) : si Odoo la corrige, la vidéo doit la montrer.
_PASTILLE_SALLE = _lire(O, 'pos_restaurant', 'static', 'src', 'app', 'floor_screen', 'floor_screen.js')
dans(_PASTILLE_SALLE, 'changeCount += this.getChangeCount(table) || 0;', 'O/pos_restaurant/…/floor_screen.js '
     '(la pastille du bouton « Salle » s\'afficherait : la montrer à l\'étape 5)')
# « Serveur — imprimer l'addition : 6 touches », mesuré (notes de version, partie 3).
dans(_lire(RACINE, 'docs', 'NOTES_DE_VERSION_restaurant_lot1.md'),
     "| Serveur — imprimer l'addition | 6 | **6** (imprimante de tickets simulée) |", 'N §3')
# Les cas de recette cités par la voix et les bulles.
_RECETTE = _lire(RACINE, 'recette', 'cas_de_test.py')
for _extrait in ('Verte à 59 minutes ; orange au plus tard à 61 minutes, sans que ',
                 'Après 5 minutes, le poste revient au plan, verrouillé (choix écrit : ',
                 'La durée affichée reste comptée depuis la première ouverture.'):
    dans(_RECETTE, _extrait, 'recette/cas_de_test.py')

# ========================================================== les données --
EQUIPE = {x[1]: x for x in demo.EQUIPE_RESTO}
LOIC, ROLE_LOIC = demo.POSTES_RESTO['serveur']
LANDRY = demo.POSTES_RESTO['chef'][0]
P_LOIC, P_LANDRY, P_INES = LOIC.split()[0], LANDRY.split()[0], demo.POSTES_RESTO['serveuse'][0].split()[0]
assert EQUIPE[P_LOIC][2] == 'Serveur' and EQUIPE[P_LANDRY][2] == 'Chef de salle ou superviseur'
CODE_LOIC, CODE_LANDRY = EQUIPE[P_LOIC][3], EQUIPE[P_LANDRY][3]


def _minutes(hhmm):
    h, m = hhmm.split(':')
    return int(h) * 60 + int(m)


# La chronologie (en-tête) : table → (ouverte par, heure d'ouverture).
OUVERTURES = {4: (P_LOIC, '12:15'), 6: (P_INES, '12:28'), 7: (P_INES, '11:45'), 10: (P_LOIC, '11:52'),
              2: (P_LOIC, '12:55')}
INSTANTS = {1: '12:50', 2: '12:51', 3: '12:53', 5: '12:55', 6: '13:00'}


def alerte(minutes, delai=demo.DELAI_ORANGE):
    """La couleur d'une table ouverte (S/utils/alerte.js:18-27)."""
    return 'orange' if minutes >= delai else 'vert'


def etat_table(n, instant):
    """(couleur, durée) de la table ``n`` à l'étape ``instant`` ; None si elle n'est pas encore ouverte."""
    ouverte = _minutes(OUVERTURES[n][1])
    maintenant = _minutes(INSTANTS[instant])
    if maintenant < ouverte:
        return None
    m = maintenant - ouverte
    assert m != demo.DELAI_ORANGE, 't18 : une table à « 1 h 00 » (ECARTS.md n° 82)'
    return alerte(m), duree_resto(m)


DUREES = {(n, i): etat_table(n, i) for n in OUVERTURES for i in INSTANTS}
assert [DUREES[(10, i)] for i in (1, 2, 3)] == [('vert', '58 min'), ('vert', '59 min'), ('orange', '1 h 01')]
assert DUREES[(7, 1)] == ('orange', '1 h 05') and DUREES[(4, 1)] == ('vert', '35 min')
assert DUREES[(2, 5)] == ('vert', '0 min') and DUREES[(2, 6)] == ('vert', '5 min')


def d(n, i):
    return DUREES[(n, i)][1]


# La carte : les produits et la couleur de leur famille (une sous-famille sans couleur prend celle de son parent :
# demo.FAMILLES_RESTO ; la tuile prend la couleur de la famille la plus fine, O/point_of_sale/…/product_screen.xml:35).
def _cle(nom):
    return ''.join(c for c in unicodedata.normalize('NFD', nom.lower()) if c.isalnum())


COULEURS = {}


def _couleurs(branches, parent=0):
    for nom, couleur, enfants in branches:
        COULEURS[nom] = couleur or parent
        _couleurs(enfants, COULEURS[nom])


_couleurs(demo.FAMILLES_RESTO)
CARTE = {nom: (famille, prix) for nom, famille, prix, _cout, _suivi in demo.CARTE_RESTO}
REINE, BLONDE, COLA = 'Pizza Reine', 'Bière blonde 65 cl', 'Cola 33 cl'
assert CARTE[COLA][0] == 'Sodas' and CARTE[REINE][1] == 6000 and CARTE[BLONDE][1] == 1500 and CARTE[COLA][1] == 1000


def tuiles(ident, noms, qtes=None):
    """Les tuiles, triées par nom comme Odoo (O/point_of_sale/…/product_screen.js:419 : localeCompare)."""
    noms = sorted(noms, key=lambda n: unicodedata.normalize('NFD', n.lower()))
    return resto_tuiles(ident, [(_cle(n), n, COULEURS[CARTE[n][0]]) for n in noms],
                        {_cle(k): v for k, v in (qtes or {}).items()})


# ============================================================== le plan --
def _plan_etats(i):
    return {n: (DUREES[(n, i)][0], DUREES[(n, i)][1], None) for n in OUVERTURES if DUREES[(n, i)]}


PLAN = resto_plan('t18-plan', resto_salle('t18-plan', _plan_etats(1)), delai=demo.DELAI_ORANGE,
                  salle=demo.SALLE_RESTO, initiale=True)
for _cle_leg in ('libre', 'vert', 'orange', 'pastille'):
    _avant = '<span class="rs-leg-p"><i class="rs-leg-%s">' % _cle_leg
    assert _avant in PLAN
    PLAN = PLAN.replace(_avant, '<span class="rs-leg-p" id="t18-leg-%s"><i class="rs-leg-%s">' % (_cle_leg, _cle_leg))
assert 'id="t18-plan-t2-p"' in PLAN and 'id="t18-plan-salle-p"' in PLAN

# ======================================== l'écran de commande, table 10 --
TOTAL_10 = 2 * CARTE[REINE][1] + 4 * CARTE[BLONDE][1]
assert TOTAL_10 == 18000
CMD10 = resto_commande(
    't18-c10', etat_commande(10, P_LOIC, 61),
    resto_ligne('t18-c10-l1', REINE, 2, CARTE[REINE][1]) + resto_ligne('t18-c10-l2', BLONDE, 4, CARTE[BLONDE][1]),
    fcfa(TOTAL_10), 4, resto_familles('t18-c10-f', demo.FAMILLES_RESTO),
    tuiles('t18-c10-pr', CARTE, {REINE: 2, BLONDE: 4}), encaisser=True,
    # rouverte, aucune ligne choisie : pas de pavé, « Note cuisine » grisé (O/point_of_sale/…/product_screen.xml:13 ;
    # customer_note_button.xml:7 ; C/09) — relevé à l'intégration, le pavé y était montré
    sans_ligne=True)

# ========================================= l'écran de commande, table 2 --
SODAS = [n for n, (f, _p) in CARTE.items() if f == 'Sodas']
CMD2 = resto_commande(
    't18-c2', etat_commande(2, P_LOIC, 0),
    resto_ligne('t18-c2-l1', COLA, 1, CARTE[COLA][1], envoyee=False, choisie=True, cache=True),
    fcfa(CARTE[COLA][1]), 2, resto_familles('t18-c2-f', demo.FAMILLES_RESTO, ('Boisson', 'Non alcoolisé', 'Sodas')),
    tuiles('t18-c2-pr', SODAS), compteurs=[('Sodas', 0)], vide=True)
assert 'id="t18-c2-pr-cola33cl-q"' in CMD2 and 'id="t18-c2-env-0-v"' in CMD2

# ============================================================ la caisse --
CODE = resto_code('t18-code', TITRES_RESTO['table'](10))
ENVOYE = resto_notification('t18-envoye', TEXTES_RESTO['envoye']('2 Sodas'))
assert TEXTES_RESTO['envoye']('2 Sodas') == 'Envoyé%s: 2 Sodas.' % ESP
# Le nom posé d'office est le plus long des deux (Landry) : la case de l'employé est mesurée au chargement (anneau de
# l'étape 6) ; les gestes ``texte`` posent ensuite le nom de qui tape son code.
assert P_LOIC[0] == P_LANDRY[0] and len(P_LANDRY) >= len(P_LOIC)
CAISSE = fenetre_resto('t18-pos', [PLAN, CMD10, CMD2], calques=CODE + ENVOYE, employe=(P_LANDRY, P_LANDRY[0]),
                       avatar=demo.AVATARS_RESTO[P_LOIC])
# Sur le plan verrouillé, personne n'est identifié : le nom (posé d'office) n'est montré qu'avec la classe avec-emp.
assert 'class="app pos resto sur-plan avec-emp"' in CAISSE
CAISSE = CAISSE.replace('class="app pos resto sur-plan avec-emp"', 'class="app pos resto sur-plan"', 1)
ECRAN = navigateur(CAISSE)

ROLE_LANDRY = demo.POSTES_RESTO['chef'][1]
CSS = """
/* -- l'avatar de Landry à la caisse (demo.AVATARS_RESTO) : une classe, posée quand il prend la table -- */
#t18-pos-emp-av.t18-landry { background: %s !important; }
/* -- la case de l'employé, cachée sans être retirée tant que personne n'est identifié : le moteur la mesure au
   chargement (anneau de l'étape 6) ; à droite de la barre, elle est au même endroit sur le plan et à la commande -- */
#t18-pos .rs-emp { display: flex; visibility: hidden; }
#t18-pos.avec-emp .rs-emp { visibility: inherit; }
""" % demo.AVATARS_RESTO[P_LANDRY] + (
    "/* -- la pastille du personnage : Loïc, puis Landry quand il prend la table (étape 6), comme t17 et t19 ; "
    "la réaction de fin est la sienne -- */\n"
    + css_personnage('#tu-perso.t18-landry', LANDRY, ROLE_LANDRY, P_LANDRY[0]) + """
#t18-r-oubli b { font-size: 0; }
#t18-r-oubli b::before { content: "%s"; font-size: 18px; letter-spacing: .04em; }
""" % P_LANDRY)


# ============================================================ les gestes --
def vers_commande(table, nom=P_LOIC, landry=False, **kw):
    """Le plan laisse la place à l'écran de commande : barre de la caisse (« sur-commande », onglet, employé)."""
    g = [classe('#t18-pos', ajouter=['sur-commande', 'avec-emp'], retirer=['sur-plan'], **kw),
         texte('#t18-pos-onglet', str(table), avec=True), texte('#t18-pos-emp-n', nom, avec=True)]
    if landry:
        g.append(classe('#t18-pos-emp-av', ajouter=['t18-landry'], avec=True))
    return g


def vers_plan(**kw):
    """Retour au plan verrouillé : plus personne d'identifié (pos_store.js:448-455)."""
    return [classe('#t18-pos', ajouter=['sur-plan'], retirer=['sur-commande', 'avec-emp'], **kw),
            texte('#t18-pos-onglet', 'Table', avec=True), classe('#t18-pos-emp-av', retirer=['t18-landry'], avec=True)]


def taper_code(code, d=0.3, puis=0.1):
    """Quatre touches ; seuls les points se remplissent (le chiffre n'est jamais lisible)."""
    g = []
    for k, chiffre in enumerate(code):
        # le point se remplit à l'instant du toucher (après le déplacement du curseur : d + 0,08 s)
        g += [clic('#t18-code-k%s' % chiffre, d=d, puis=puis),
              classe('#t18-code-p%d' % k, ajouter=['plein'], avec=True, decale=round(d + 0.08, 2))]
    return g


# Les points se vident une fois la fenêtre fermée (fondu de 0,25 s), pour la table suivante.
VIDER_POINTS = [classe('#t18-code-p%d' % k, retirer=['plein'], avec=True, decale=0.0 if k else 0.4) for k in range(4)]


def plan_a(i, tables=(4, 6, 7, 10), **kw):
    """Les durées (et couleurs) du plan à l'étape ``i``."""
    g = []
    for k, n in enumerate(tables):
        g.append(texte('#t18-plan-t%d-d' % n, d(n, i), avec=bool(k) or kw.get('avec', False)))
    return g


TUTORIEL = {
    'slug': 't18-restaurant-plan-en-couleurs',
    'profil': 't18_restaurant_plan_en_couleurs',
    'numero': 18,
    'titre': 'Le plan en couleurs',
    'fonction': 'Plan de salle en couleurs',
    'personnage': (LOIC, ROLE_LOIC),
    'accroche': {
        'kicker': 'En salle, pendant le service',
        # Les douleurs : P, REST-16 « Couverture » (l.394 : la table n'affiche que son numéro et une pastille),
        # REST-17 « Couverture » (l.410 : aucune durée sur le plan ; l'écran de veille remplace le plan coloré ;
        # une table occupée prend la couleur choisie au dessin, « Propositions » l.401) ; §2 besoin 10 (l.93).
        'question': 'Depuis *quand* cette table est-elle ouverte ?',
        'douleurs': [('sablier', 'Aucune durée sur le plan de salle'),
                     ('interrogation', 'Des additions qu\'on oublie'),
                     ('horloge', 'Un écran de veille qui cache la salle'),
                     ('grille', 'Une couleur choisie au dessin, pas une alerte'),
                     ('liste', 'Un numéro, une pastille : rien de plus')],
        'voix': "Depuis quand la table sept est-elle ouverte ? Sans durée sur le plan, une addition s'oublie, et "
                "l'écran de veille finit par cacher la salle.",
    },
    'revelation': {
        # Couleurs et durée : S/utils/messages.js:150-171, S/utils/alerte.js:18-27, S/overrides/floor_screen.js:72-87.
        'promesse': 'Gris, vert, orange : chaque table ouverte dit depuis quand, et quand proposer l\'addition.',
        'voix': "Avec Aïte haousse, le plan se lit d'un coup d'œil, et il change de couleur tout seul.",
    },
    'temps': ['Lire', 'Compter', 'Alerter', 'Rattraper'],
    'app': 't18-pos',
    'ecran': ECRAN,
    'css': CSS,
    'vues_initiales': {'pos': 't18-plan'},
    'bulles': {
        'b-tic': 'Recalculée toutes les 30 secondes, et comptée depuis la première ouverture, même après un '
                 'déplacement.',
        'b-delai': '60 minutes par défaut ; le délai se règle pour chaque caisse et s\'applique à sa réouverture.',
        'b-5min': '5 minutes sans toucher l\'écran : fenêtres fermées, retour au plan verrouillé.',
        'b-pastille': 'Le chiffre de la pastille : les articles saisis, pas encore envoyés.',
    },
    'reactions': {
        't18-r-orange': 'L\'addition, au bon moment.',
        't18-r-oubli': 'Rien ne reste en attente.',
    },
    'etapes': [
        {'temps': 0, 'titre': 'Le plan, l\'écran de repos',
         'texte': 'Entre deux commandes, chaque tablette affiche le plan, verrouillé ; la légende, en bas, donne le '
                  'sens des couleurs.',
         'voix': "Entre deux commandes, chaque tablette montre le plan de la salle, verrouillé : personne n'y est "
                 "identifié. En bas, la légende donne le sens de chaque couleur. Gris : la table est libre. Vert : "
                 "elle est ouverte.",
         'gestes': [pause(0.4), curseur('#t18-plan-etat', fx=0.2, d=0.6), anneau('#t18-plan-etat', d=1.6),
                    pause(1.4), curseur('#t18-plan-legende', fx=0.3, d=0.6), anneau('#t18-plan-legende', d=1.8),
                    pause(0.6), anneau('#t18-leg-libre', d=1.2), anneau('#t18-plan-t1', d=1.0),
                    anneau('#t18-leg-vert', d=1.2), anneau('#t18-plan-t4', d=1.0)]},
        {'temps': 1, 'titre': 'Vert, et depuis quand',
         'texte': 'Sous le numéro, la durée depuis l\'ouverture de la table ; elle se recalcule toutes les 30 '
                  'secondes, sans toucher l\'écran.',
         'voix': "Sous chaque numéro, la durée depuis l'ouverture de la table : la quatre de Loïc, trente-cinq "
                 "minutes. Toutes les trente secondes, la caisse recalcule, sans que personne ne touche l'écran : "
                 "trente-six.",
         # Personne ne touche l'écran : le curseur reste sur la légende (étape 1), hors du cadre pendant le zoom.
         'gestes': [zoom('#t18-plan-t4', s=1.6, d=0.9), pause(1.75),
                    anneau('#t18-plan-t4-d', d=1.6), pause(3.6)] + plan_a(2) +
                   [anneau('#t18-plan-t4-d', d=1.2), bulle('b-tic', '#t18-plan-t4', cote='droite', d=3.4),
                    pause(1.6), dezoom(d=0.6)]},
        {'temps': 2, 'titre': 'Orange : proposez l\'addition',
         'texte': 'Le délai atteint, 60 minutes par défaut, la table passe à l\'orange : c\'est le moment de proposer '
                  'l\'addition.',
         'voix': "La table dix vient de passer l'heure : la voilà orange, toute seule. La sept l'était déjà. La "
                 "légende le dit : proposez l'addition. Le délai, soixante minutes par défaut, se règle caisse par "
                 "caisse.",
         # Pas de zoom : la caméra, qui ne montre jamais le bord du navigateur, poserait la rangée du bas sous la
         # légende de l'étape (la durée de la table 10 serait cachée). La bulle du délai se pose dans la moitié vide
         # du plan (à droite de la table 12) : au-dessus de la légende du plan, elle cacherait la table 10.
         'gestes': [pause(0.6),
                    classe('#t18-plan-t10', ajouter=['orange'], retirer=['vert'])] + plan_a(3, avec=True) +
                   [pause(0.3), anneau('#t18-plan-t10', d=2.1), pause(0.6), anneau('#t18-plan-t7', d=1.2), pause(0.2),
                    curseur('#t18-leg-orange', fx=0.3, d=0.5), anneau('#t18-leg-orange', d=1.6),
                    bulle('b-delai', '#t18-plan-t12', cote='droite', d=3.2), pause(2.0),
                    reaction('t18-r-orange', d=2.6), pause(1.0)]},
        {'temps': 2, 'titre': 'Loïc propose l\'addition',
         'texte': 'Table, code, « Addition » : 6 touches. En tête, la même durée qu\'au plan ; l\'addition '
                  'imprimée, le plan revient.',
         'voix': "Loïc touche sa table et tape son code ; une table déjà ouverte ne redemande pas le nombre de "
                 "personnes. En tête de l'addition, la même durée qu'au plan : une heure et une minute. Il touche "
                 "Addition : elle sort à l'imprimante, et le plan revient, verrouillé.",
         'gestes': [clic('#t18-plan-t10', d=0.6), ouvrir('t18-code')] + taper_code(CODE_LOIC) +
                   [pause(0.2), fermer('t18-code'), vue('t18-c10', 'pos', avec=True)] + vers_commande(10, avec=True) +
                   VIDER_POINTS +
                   [curseur('#t18-c10-etat', fx=0.6, d=0.5), anneau('#t18-c10-etat', d=1.8), pause(0.6),
                    clic('#t18-c10-addition', d=0.6), pause(0.5), vue('t18-plan', 'pos')] + vers_plan(avec=True) +
                   [curseur('#t18-plan-carte', fx=0.72, fy=0.45, d=0.6), pause(0.6)]},
        {'temps': 3, 'titre': 'Cinq minutes sans toucher : le plan revient',
         'texte': 'Deux colas saisis, pas envoyés, et Loïc est appelé ailleurs : 5 minutes sans toucher l\'écran, le '
                  'poste revient au plan.',
         'voix': "Table deux, Loïc saisit deux colas, puis on l'appelle ailleurs : rien n'est parti. Cinq minutes "
                 "sans toucher l'écran, et le poste revient de lui-même au plan, verrouillé, sans écran de veille. "
                 "Sur la table deux, une pastille rouge.",
         # « J'envoie » désigné sans être touché (rien n'est parti) ; Loïc parti, le curseur (son doigt) disparaît :
         # personne ne touche plus l'écran. La bulle se pose dans le vide de l'addition, sous la ligne, et se ferme
         # avant le retour au plan. La pastille est posée avec le plan, qui la dessine dès qu'il s'affiche (O/
         # pos_restaurant/…/floor_screen.xml:150-160) ; puis la phrase d'état (verrouillé), puis la pastille.
         'gestes': [vue('t18-c2', 'pos')] + vers_commande(2, avec=True) +
                   [pause(0.4), clic('#t18-c2-pr-cola33cl', d=0.6, puis=0.0),
                    cacher('#t18-c2-vide', d=0.15), montrer('#t18-c2-l1', d=0.25, y=0, avec=True),
                    montrer('#t18-c2-pave', d=0.25, y=0, avec=True), montrer('#t18-c2-tot', d=0.25, y=0, avec=True),
                    montrer('#t18-c2-encaisser', d=0.25, y=0, avec=True),
                    classe('#t18-c2-addition', retirer=['gris'], avec=True),
                    classe('#t18-c2-envoyer', ajouter=['actif'], avec=True),
                    texte('#t18-c2-env-0-v', '1', avec=True), classe('#t18-c2-env-0', ajouter=['on'], avec=True),
                    texte('#t18-c2-pr-cola33cl-q', '1', avec=True),
                    classe('#t18-c2-pr-cola33cl-q', ajouter=['on'], avec=True),
                    clic('#t18-c2-pr-cola33cl', d=0.3, puis=0.0),
                    texte('#t18-c2-l1-q', '2,00'), texte('#t18-c2-l1-m', fcfa(2 * CARTE[COLA][1]), avec=True),
                    texte('#t18-c2-total', fcfa(2 * CARTE[COLA][1]), avec=True),
                    texte('#t18-c2-env-0-v', '2', avec=True), texte('#t18-c2-pr-cola33cl-q', '2', avec=True),
                    anneau('#t18-c2-envoyer', d=1.2),
                    bulle('b-5min', '#t18-c2-l1', cote='bas', d=2.6),
                    animer('#curseur', {'autoAlpha': 1}, {'autoAlpha': 0}, d=0.4, avec=True), pause(1.95),
                    vue('t18-plan', 'pos')] + vers_plan(avec=True) +
                   [classe('#t18-plan-t2', ajouter=['vert', 'avec-duree'], retirer=['libre'], avec=True),
                    texte('#t18-plan-t2-d', d(2, 6), avec=True)] + plan_a(6, avec=True) +
                   [texte('#t18-plan-t2-p', '2', avec=True), classe('#t18-plan-t2-p', ajouter=['on'], avec=True),
                    anneau('#t18-plan-etat', d=1.4), pause(0.4), anneau('#t18-plan-t2-p', d=1.6)]},
        {'temps': 3, 'titre': 'Pastille rouge : rien n\'est parti',
         'texte': 'Pastille rouge : saisi, pas encore envoyé. Landry, chef de salle, ouvre la table avec son code et '
                  'touche « J\'envoie ».',
         'voix': "La pastille rouge compte ce qui est saisi, mais pas encore envoyé : ici, les deux colas de Loïc. "
                 "Landry, le chef de salle, la repère en passant. Il touche la table et tape son code : un chef de "
                 "salle peut modifier la table d'un collègue. Son prénom s'affiche en haut, et la table reste "
                 "ouverte par Loïc. Il touche J'envoie : les colas partent, le plan revient, verrouillé, et la "
                 "pastille s'efface.",
         # La bulle s'ouvre au-dessus de la pastille qu'elle explique (elle couvre un moment la fin de la phrase
         # d'état) : posée à côté d'une autre table, elle faisait lire son « chiffre » comme le numéro de cette table.
         # Landry arrive : la pastille du personnage passe à son nom, le curseur réapparaît. Les points du code se
         # remplissent pendant que la voix dit pourquoi il le peut (R4, messages.js:26-28 ; regles.py:35) ; son
         # prénom, puis « ouverte par Loïc », sont désignés quand la voix les dit.
         'gestes': [anneau('#t18-plan-t2-p', d=1.4), anneau('#t18-leg-pastille', d=1.6),
                    bulle('b-pastille', '#t18-plan-t2-p', cote='haut', d=3.0),
                    anneau('#t18-plan-t2-p', d=1.4, avec=True, decale=0.2), pause(0.2),
                    classe('#tu-perso', ajouter=['t18-landry']),
                    animer('#curseur', {'autoAlpha': 0}, {'autoAlpha': 1}, d=0.3, avec=True),
                    curseur('#t18-plan-t2', fx=0.4, fy=0.6, d=0.8), pause(0.8),
                    clic('#t18-plan-t2', fx=0.4, fy=0.6, d=0.1), texte('#t18-code-titre', TITRES_RESTO['table'](2)),
                    ouvrir('t18-code')] + taper_code(CODE_LANDRY, d=0.25, puis=0.05) +
                   [pause(0.2), fermer('t18-code'), vue('t18-c2', 'pos', avec=True)] +
                   vers_commande(2, nom=P_LANDRY, landry=True, avec=True) +
                   [texte('#t18-c2-etat', etat_commande(2, P_LOIC, 5), avec=True)] + VIDER_POINTS +
                   [anneau('#t18-pos-emp', d=1.0, avec=True),
                    curseur('#t18-c2-ticket', fx=0.6, fy=0.55, d=0.5, avec=True), anneau('#t18-c2-etat', d=1.5),
                    clic('#t18-c2-envoyer', d=0.5), pause(0.3), vue('t18-plan', 'pos')] +
                   vers_plan(avec=True) +
                   [classe('#t18-plan-t2-p', retirer=['on'], avec=True), notifier('t18-envoye', duree=3.0, avec=True),
                    curseur('#t18-plan-carte', fx=0.72, fy=0.45, d=0.6, avec=True),
                    pause(1.0), anneau('#t18-plan-t2', d=1.2), reaction('t18-r-oubli', d=2.4), pause(0.3)]},
    ],
    'resultats': {
        'titre': 'Le plan qui veille pour vous',
        'cartes': [
            # regles.DELAI_ALERTE, pos_config.py:36, 100-102 ; S/utils/alerte.js:9.
            {'valeur': '60', 'compter': 60, 'unite': 'minutes', 'icone': 'horloge',
             'texte': 'avant l\'orange, par défaut ; le délai se règle pour chaque caisse'},
            # S/utils/alerte.js:14 (TIC = 30000) ; S/overrides/floor_screen.js:40.
            {'valeur': '30', 'compter': 30, 'unite': 'secondes', 'icone': 'sablier',
             'texte': 'entre deux calculs des couleurs et des durées, sans toucher l\'écran'},
            # regles.DELAI_RETOUR_PLAN (300 s) ; S/store/pos_store.js:624-633 ; rec R67.
            {'valeur': '5', 'compter': 5, 'unite': 'minutes', 'icone': 'cadenas',
             'texte': 'sans toucher l\'écran, et le poste revient au plan, verrouillé'},
        ],
        'voix': "Soixante minutes avant l'orange, un calcul toutes les trente secondes, et le plan qui revient seul "
                "après cinq minutes.",
    },
    'cta': {
        'appel': 'Demandez votre démonstration',
        'sous_marque': demo.SOUS_MARQUE_RESTO,
        'suivant': 'Annuler sous le code du chef de salle',
        'voix': "Aïte haousse, par Aïte Consulting. Demandez votre démonstration. Prochain tutoriel : annuler sous le "
                "code du chef de salle.",
    },
    # Le plan revenu, la pastille posée, entre deux anneaux : les quatre parties de la légende, gris, vert, orange
    # et la pastille rouge sur une image (revue du 15/11 : plan à +7,7 s, anneau de la phrase d'état jusqu'à
    # +10,2 s, anneau de la pastille à +10,4 s).
    'vignette': {'etape': 5, 'apres': 10.3},
}


def _typo(texte_):
    """Les textes à l'écran écrits ici (pas la voix) : une espace insécable dans les guillemets et avant « : »,
    « ; », « ? », pour qu'un signe ne passe pas seul à la ligne (comme S/utils/messages.js:7-9, et t17, t19, t20)."""
    for avant, apres in (('« ', '« '), (' »', ' »'), (' :', ' :'), (' ;', ' ;'), (' ?', ' ?')):
        texte_ = texte_.replace(avant, apres)
    return texte_


for _etape in TUTORIEL['etapes']:
    _etape['titre'], _etape['texte'] = _typo(_etape['titre']), _typo(_etape['texte'])
for _groupe in ('bulles', 'reactions'):
    TUTORIEL[_groupe] = {_k: _typo(_v) for _k, _v in TUTORIEL[_groupe].items()}
for _carte in TUTORIEL['resultats']['cartes']:
    _carte['texte'] = _typo(_carte['texte'])
TUTORIEL['revelation']['promesse'] = _typo(TUTORIEL['revelation']['promesse'])
TUTORIEL['accroche']['question'] = _typo(TUTORIEL['accroche']['question'])
TUTORIEL['accroche']['douleurs'] = [(_i, _typo(_t)) for _i, _t in TUTORIEL['accroche']['douleurs']]
