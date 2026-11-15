# -*- coding: utf-8 -*-
"""Tutoriel 19 — Annuler sous le code du chef de salle.

Le quatrième des huit tutoriels du restaurant (lot 1 : aite_pos_restaurant, incrément 4 : REST-10, REST-11,
REST-12, REST-22). Un restaurant SANS hôtel (demo.RESTO, demo.SOCIETE_RESTO) : la caisse plein écran au service à
table contrôlé (ecrans.fenetre_resto, étapes 1 à 6), puis la gestion d'Odoo 18 sous le thème MuK (étape 7).
Storyboard : scratchpad videos_resto/storyboards/t19.md (adapté : voir « Écarts au storyboard »).

Abréviations : R/ = addons/aite_pos_restaurant/ ; S/ = R/static/src/ ; O/ = ../odoo18/addons/ ;
N = docs/NOTES_DE_VERSION_restaurant_lot1.md ; P = docs/PERIMETRE_FONCTIONNEL_RESTAURANT.md ;
rec = recette/cas_de_test.py ; C/nn = captures/restaurant/nn_*.jpg (modèles visuels, jamais incrustés).
Les phrases du produit sont relues dans le code au chargement (garde-fous plus bas) : une phrase changée dans le
module fait échouer la construction de la vidéo au lieu de la rendre fausse.

Personnages (la pastille change de personne par une classe, ecrans.css_personnage, comme t16 et t17) : Inès,
serveuse (demo.POSTES_RESTO['serveuse'], code 5913), étapes 1 et 2 ; Landry, chef de salle (demo.POSTES_RESTO['chef'],
code 7461), personnage du tutoriel, étapes 3 à 6 ; Edwige, la manager (demo.POSTES_RESTO['manager']), étape 7, qui
lit le journal (son groupe, responsable du Point de Vente, implique la lecture des rapports :
R/security/restaurant_security.xml:26-28). Les réactions sont celles de Landry (étapes 4 et 6). Loïc (serveur)
n'apparaît que par son nom (table 9, journal).

Le monde rejoué (conditions écrites ici, pour que chaque image soit vraie) :
- le 14/10/2026, jour de référence de la série, la caisse « Restaurant » ouverte, délai de 60 minutes ; aucune
  date ni heure n'est à la caisse (seulement les durées) ; dans la gestion, les dates du journal ;
- le bon d'annulation n'est PAS rejoué (relecture adverse) : avec des imprimantes de préparation, le poste imprime le
  bon de la seule ligne annulée et la notification ajoute « Bon d'annulation envoyé. » (S/store/pos_store.js:
  1350-1353, 1396-1409 ; S/utils/messages.js:129), mais ni le bon, ni ce qui part avec lui, ni cette phrase n'ont
  jamais été vus : N §8 l.639-648 (« À jouer avant de le promettre au client » ; « « Bon d'annulation envoyé. » n'a
  jamais été vu »), et les tours tournent sans imprimante de préparation (R/tests/test_tours.py:41-43). La vidéo
  montre donc la notification vue à l'écran (C/12, caisse sans imprimante de préparation) et ne promet aucun bon ;
  BON_VU (plus bas) la rétablit quand le bon aura été vu sur une imprimante réelle, et un garde-fou relit N §8 pour
  que la construction échoue le jour où la note change. Toute la série est sans imprimante de préparation (t18
  aussi, depuis l'intégration : sans imprimante, la pastille compte tous les produits, O/point_of_sale/static/src/
  app/models/utils/order_change.js:59) ; DESIGN.md, « Le restaurant » ;
- une seule tablette pour la salle : la famille choisie par Inès (Boisson › Alcoolisé › Bière) reste choisie
  quand Landry ouvre la table 9 (O/point_of_sale/static/src/app/store/pos_store.js:1058-1068 ; C/09) ;
- la chronologie des tables (heure d'ouverture : R/models/pos_order.py ; N l.107), suite de t18 (2 et 4 ouvertes
  par Loïc à 12:55 et 12:15 ; 6, 7 et 10 encaissées depuis) :

    table  ouverte par  à      13:30 (étapes 1-4)   13:48 (étapes 5-6)
    5      Inès         13:05  25 min               43 min
    9      Loïc         13:28  2 min                20 min
    2      Loïc         12:55  —                    53 min
    4      Loïc         12:15  —                    1 h 33 (orange)

  durées et couleurs calculées plus bas (DUREES) par la règle de la caisse (S/utils/alerte.js:18-27,
  S/utils/messages.js:165-171) ; aucune table à « 1 h 00 » (ECARTS.md n° 82) ;
- table 5, 2 personnes : Pizza quatre fromages et 3 Bière blonde 65 cl envoyées (11 500 FCFA), puis une 4ᵉ bière
  saisie et retirée (étape 1), une bière annulée (étape 2-4) : 10 000 FCFA, encaissés à 14:05 (storyboard t22) ;
- table 9, 2 personnes : Pizza Margherita et 2 Cola 33 cl envoyés (7 000 FCFA), annulés en entier (étapes 5 et 6) ;
- le journal du jour (étape 7) : ces quatre lignes, plus un « Retrait sans code » de 11:52 (table 1, 1 Jus de
  bissap 50 cl, Loïc), arrivé d'un poste en retard (R/models/pos_order.py:377-453 ; rec R52) ; ordre « date desc,
  id desc » (R/models/restaurant_annulation.py:37) : les deux lignes de la table 9, écrites ensemble dans l'ordre
  des lignes de l'addition (pos_order.py:663-689), Cola 33 cl d'abord ; « Demandée par » : la personne identifiée
  (pos_order.py:673-683), donc Landry pour la table 9 (C/22 : le même prénom dans les deux colonnes).

Écrans et libellés :
1-4. L'écran de commande de la table 5 (C/09, C/10, C/11, C/12) : « Plan », onglet « 5 », logo, « Rechercher des
   produits… », code-barres, « Inès », ≡ (O/pos_restaurant/…/navbar/navbar.xml:19-28 ; S/overrides/navbar.xml:18-20) ;
   « Table 5 · ouverte par Inès · 25 min » (S/store/pos_store.js:1136-1151 ; S/overrides/product_screen.xml:13-16 ;
   messages.js:114-116, 165-171) ; lignes, « Total », « 2 personnes », « Addition », « Client », « Note cuisine »,
   « Actions » (S/overrides/control_buttons.xml:17-34 ; « Note cuisine » grisé sans ligne choisie : O/point_of_sale/
   …/customer_note_button.xml:7) ; sans ligne choisie, pas de pavé (O/point_of_sale/…/product_screen.xml:12 ; C/09) ;
   « J'envoie » avec « Bière 1 », puis gris ; « J'encaisse » (S/overrides/actionpad_widget.xml:13-18) ; barre verte de
   la part pas envoyée (O/point_of_sale/…/orderline.scss:24-39 ; C/06) ; familles et tuiles de la famille Bière
   (demo.FAMILLES_RESTO, demo.CARTE_RESTO ; quantité sur la tuile : C/09, C/12).
   La fenêtre d'annulation (S/components/annulation_popup/annulation_popup.xml:7-82) : titre TITRES.annulerProduit
   (messages.js:85), sous-titre R9 (messages.js:58-60) gardé à toutes les étapes (pos_store.js:1261-1265 ; C/10,
   C/11), « Combien ? », « 1 », « 2 », « 3 (tout) » (messages.js:122-123 ; pos_store.js:1315-1316), « Code d'un chef
   de salle », points, pavé sans « Retour » (annulation_popup.xml:27-50), « Pourquoi ? » et les cinq motifs
   (R/data/restaurant_motif_data.xml:8-28), « Autre » choisi en primaire, « Précision », champ, « Valider »
   (annulation_popup.xml:53-73), R24 dessous (:74-75 ; messages.js:61), « Retour » (:78-80). Notifications : R8 en
   rouge (messages.js:55-57 ; pos_store.js:1274-1276), puis « Annulation faite : 1 Bière blonde 65 cl, par Landry. »
   en bleu (messages.js:127-128 ; pos_store.js:1352-1353 ; C/12 : la phrase vue à l'écran, sans le bon).
5-6. Le plan à 13:48 (C/08 : « Salle », phrase d'état, tables, légende ; messages.js:97, 150-158) ; « Table 9 — votre
   code » (messages.js:73 ; C/04) ; l'écran de commande de la table 9 (« Landry » en haut, avatar « L ») ; la
   fenêtre « Actions » d'Odoo (titre : O/point_of_sale/…/control_buttons/control_buttons.js:139-145 ; O/point_of_sale/
   i18n/fr.po:590-591), dans l'ordre que posent O/point_of_sale/…/control_buttons.xml:20-45, O/pos_restaurant/static/
   src/app/control_buttons/control_buttons.xml:4-36 et S/overrides/control_buttons.xml:27-85 : « Note générale »
   (fr.po:3290-3291), « Diviser l'addition », « Déplacer ou réunir » (messages.js:110-111), « Note au client »
   (fr.po:2432-2433), « Annuler la table » (messages.js:112) ; « Note générale » et « Note au client » grisés sans
   ligne choisie (customer_note_button.xml:7) ; ni « Remboursement » (manager seul : S/overrides/control_buttons.xml:
   28-30), ni liste de prix, ni « Modifier le nom » ; trois colonnes (O/point_of_sale/…/control_buttons.scss:1-2).
   Aucune capture de cette fenêtre (écart). Puis « Annuler la table 9 », « Déjà envoyé : 1 Pizza Margherita, 2 Cola
   33 cl » (messages.js:86, 119-121 ; pos_store.js:1415-1434), « Pourquoi ? », motifs, « Retour » (C/16) ; le plan,
   table 9 grise (pos_store.js:1531-1536), sans notification (N §6 l.420-422).
7. Restaurant › Annulations (R/views/restaurant_menus.xml:9-14 ; C/22) sous le compte de la manager (barre
   ecrans.APPS_PROFIL['resto_manager']) : titre « Annulations », facette « Aujourd'hui » posée d'office
   (R/views/restaurant_annulation_views.xml:75, 101-106), « Rechercher… » (O/web/i18n/fr.po:5761-5762), « 1-4 / 4 »,
   les trois vues (liste, tableau croisé, graphique : view_mode :104), pas de « Nouveau » (create="0" :14) ; colonnes
   (:20-28 ; libellés : R/models/restaurant_annulation.py:40, 48, 51-52, 57, 61, 67, 73-74) ; dates sans les secondes
   (:20) ; la ligne sans code en rouge (decoration-danger, :15) ; totaux (:23-24).

Règles dites par la voix, les légendes et les bulles :
- ce qui n'est pas parti s'en va librement, sans code ni trace : S/overrides/order_summary.js:52-57 ; rec R34, R36 ;
- ce qui est parti est verrouillé ; ⌫ ouvre la fenêtre d'annulation : order_summary.js:52-60 ; rec R09, R35, R36 ;
  N §1 règle 3 (l.44-45) ;
- le code d'une serveuse ne suffit pas : regles.DROITS['annuler_envoye'] = 'superviseur' (R/models/regles.py:41) ;
  pos_store.js:1274-1276 ; rec R45 ; tour R/static/tests/tours/annulation_tour.js:70-73 ;
- « Autre » demande une précision, sans elle la fenêtre refuse : annulation_popup.js:116-135 ; rec R50 ;
- le système central vérifie le code (« serveur » au sens de l'ordinateur, P l.120 : « système central ») :
  R/models/pos_order.py:632-649 ; N l.44-45, 121-122 ;
- la serveuse reste identifiée : pos_store.js:1246-1250 ; rec R44 ;
- la trace : « Demandée par » la personne identifiée, « Autorisée par » celle dont le code est vérifié :
  R/models/pos_order.py:672-689, restaurant_annulation.py:61-70 ; rec R46 (le bon d'annulation, jamais vu, n'est
  pas dit : voir le monde rejoué) ;
- une table entière : un motif, le code tapé à la table sert (pos_store.js:1261) ; une ligne de journal par produit
  (pos_order.py:669-689) ; rec R39 ;
- le journal : « Aujourd'hui » d'office, qui a demandé, qui a autorisé, pourquoi : rec R46, R47 ; ce qui arrive sans
  code n'est jamais bloqué, toujours tracé : N l.125-126, rec R52 ; une ligne ne se modifie pas et ne s'efface pas :
  R/models/restaurant_annulation.py:15-20, 90-99, rec R49 ; le chef de salle le lit avec le seul profil
  « Restaurant : lecture des rapports » : R/security/restaurant_security.xml:18-23, docs/INSTALLATION.md:306, rec R83 ;
- résultats : 9 et 8 touches mesurées (N §3 l.255, 257) ; 5 motifs posés d'office (restaurant_motif_data.xml:8-28) ;
- les douleurs de l'accroche : P l.305 (« Tout employé peut diminuer ou supprimer un produit déjà envoyé »), l.319
  (« le supérieur doit prendre la caisse à son nom »), l.326 (« ne pas reconstituer le rapport de mémoire en fin de
  service »), l.334 (« pas de motif, auteur incertain, pas de total » ; « sinon elle disparaît sans trace »).

Écarts au storyboard (le code fait foi) :
- l'équipe est celle de demo.EQUIPE_RESTO : Loïc pour le serveur du storyboard (un prénom déjà pris dans le dépôt,
  écarté par le socle) ;
- la notification est celle de C/12, sans « Bon d'annulation envoyé. », comme le storyboard ; mais la bulle du
  storyboard sur le bon (« Avec une imprimante de cuisine ou de bar… ») n'est pas reprise : jamais vu (N §8) ;
- « Écrivez en quelques mots pourquoi. » reste affiché pendant la saisie de la précision : la fenêtre ne l'efface
  qu'au toucher d'un motif (annulation_popup.js:120) et se ferme à la validation (:154-156) ;
- la fenêtre d'annulation est composée ici (fenetre_annulation) : ecrans.resto_annulation réserve la place de
  « Précision » sous les motifs, un blanc avant « Retour » que C/11 et C/16 n'ont pas (demande au socle) ;
- l'étape 7 est lue par la manager, sans la vue croisée : t23 montre la lecture du chef de salle et le regroupement
  par motif ; la vue croisée écrirait les montants sans « FCFA » (écart du storyboard, g) ;
- pas de bulle « sans réseau » (R27 jamais essayé : N §8 l.651-652 ; écart du storyboard, c).
"""

import ast
import os
import re
import unicodedata

import demo
from ecrans import (APPS_PROFIL, ICONES, MENUS_MUK, MESSAGES_RESTO, TEXTES_RESTO, TITRES_RESTO, _dialogue, _odoo_dir,
                    _pave_code, _points, css_personnage, duree_resto, e, etat_commande, fcfa, fenetre_muk, fenetre_resto,
                    navigateur, recherche, resto_code, resto_commande, resto_familles, resto_ligne, resto_notification,
                    resto_plan, resto_salle, resto_tuiles, superpose)
from marketing import bulle, reaction
from moteur import anneau, cacher, classe, clic, curseur, fermer, montrer, notifier, ouvrir, pause, saisir, texte, vue

RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
R = os.path.join(RACINE, 'addons', 'aite_pos_restaurant')
S = os.path.join(R, 'static', 'src')
O = os.path.join(_odoo_dir(), 'addons')


def _lire(*chemin):
    with open(os.path.join(*chemin), encoding='utf-8') as f:
        return f.read()


def _une_ligne(texte_):
    return ' '.join((texte_ or '').split())


def dans(source, extrait, ou):
    assert extrait in source, 't19 : « %s » introuvable dans %s' % (extrait, ou)


def _source(relatif, nom):
    """Une constante d'un fichier Python du module, lue sans importer Odoo (comme t16)."""
    for noeud in ast.parse(_lire(R, relatif)).body:
        if isinstance(noeud, ast.Assign) and any(getattr(c, 'id', None) == nom for c in noeud.targets):
            return ast.literal_eval(noeud.value)
    raise ValueError('t19 : %s introuvable dans %s' % (nom, relatif))


# ============================================================== garde-fous --
# 1. Les textes de la caisse : chaque phrase montrée est relue dans S/utils/messages.js (source JS, espaces ramenées
#    à une seule), puis comparée à ce que les composants d'ecrans.py affichent (comme t17).
_JS = _une_ligne(_lire(S, 'utils', 'messages.js'))


def _js(extrait, **valeurs):
    """Le texte d'un littéral de messages.js (``extrait`` y est mot pour mot), ``${ESP}`` → espace insécable,
    ``${x}`` → ``valeurs['x']`` (``nombre(x)`` → la quantité écrite comme ``nombre``)."""
    assert extrait in _JS, ('t19 : texte changé dans messages.js', extrait)
    t = re.search(r'(["`])(.*)\1', extrait).group(2).replace('${ESP}', ' ')
    for cle_, val in valeurs.items():
        t = t.replace('${nombre(%s)}' % cle_, str(val)).replace('${%s}' % cle_, str(val))
    assert '${' not in t, extrait
    return t


BLONDE, QUATRE, MARGHERITA, COLA = 'Bière blonde 65 cl', 'Pizza quatre fromages', 'Pizza Margherita', 'Cola 33 cl'
assert _js('annulerProduit: (produit, table) => `Annuler ${produit} — table ${table}`', produit=BLONDE, table=5) == \
    TITRES_RESTO['annulerProduit'](BLONDE, 5)
assert _js('annulerTable: (table) => `Annuler la table ${table}`', table=9) == TITRES_RESTO['annulerTable'](9)
# R9 est coupé en deux littéraux dans messages.js (l.59-60) : chaque moitié est relue.
dans(_JS, 'R9: (quantite, produit) => `Déjà envoyé${ESP}: ${nombre(quantite)} ${produit}. Pour l\'annuler, un chef '
          'de salle ` + "tape son code.",', 'S/utils/messages.js (R9)')
assert MESSAGES_RESTO['R9'](3, BLONDE) == 'Déjà envoyé : 3 %s. Pour l\'annuler, un chef de salle tape son code.' % BLONDE
dans(_JS, 'R8: "Ce code ne peut pas annuler. Il faut celui d\'un chef de salle, d\'un superviseur " + "ou du manager.",',
     'S/utils/messages.js (R8)')
assert MESSAGES_RESTO['R8'] == "Ce code ne peut pas annuler. Il faut celui d'un chef de salle, d'un superviseur ou du " \
                               "manager."
assert _js('R24: "Écrivez en quelques mots pourquoi."') == MESSAGES_RESTO['R24']
assert _js('combien: `Combien${ESP}?`') == TEXTES_RESTO['combien']
assert _js('tout: (quantite) => `${nombre(quantite)} (tout)`', quantite=3) == TEXTES_RESTO['tout'](3)
assert _js('codeChef: "Code d\'un chef de salle"') == TEXTES_RESTO['codeChef']
assert _js('pourquoi: `Pourquoi${ESP}?`') == TEXTES_RESTO['pourquoi']
assert _js('precision: "Précision"') == TEXTES_RESTO['precision']
assert _js('valider: "Valider"') == TEXTES_RESTO['valider']
assert _js('retour: "Retour"') == TEXTES_RESTO['retour']
dans(_JS, 'annulationFaite: (quantite, produit, nom) => `Annulation faite${ESP}: ${nombre(quantite)} ${produit}, par '
          '${nom}.`,', 'S/utils/messages.js (annulationFaite)')
assert _js('bonEnvoye: "Bon d\'annulation envoyé."') == TEXTES_RESTO['bonEnvoye']
assert _js('dejaEnvoyeListe: (liste) => `Déjà envoyé${ESP}: ${liste}`', liste='x') == TEXTES_RESTO['dejaEnvoyeListe']('x')
assert _js('envoi: (quantite, produit) => `${nombre(quantite)} ${produit}`', quantite=2, produit=COLA) == \
    TEXTES_RESTO['envoi'](2, COLA)
assert _js('annulerLaTable: "Annuler la table"') == TEXTES_RESTO['annulerLaTable']
assert _js('diviser: "Diviser l\'addition"') == TEXTES_RESTO['diviser']
assert _js('deplacer: "Déplacer ou réunir"') == TEXTES_RESTO['deplacer']
assert _js('table: (numero) => `Table ${numero} — votre${ESP}code`', numero=9) == TITRES_RESTO['table'](9)
assert _js('planEtat: "Touchez une table, puis tapez votre code."') == TEXTES_RESTO['planEtat']
assert ' · '.join((_js('table: (numero) => `Table ${numero}`', numero=5),
                   _js('ouvertePar: (nom) => `ouverte par ${nom}`', nom='Inès'),
                   _js('return `${minutes} min`;', minutes=25))) == etat_commande(5, 'Inès', 25)

# 2. Les gabarits et le comportement que la vidéo montre.
_POPUP = _lire(S, 'components', 'annulation_popup', 'annulation_popup.xml')
for _extrait in ('t-esc="textes.combien"', 't-esc="textes.codeChef"', 't-esc="textes.pourquoi"',
                 't-esc="textes.precision"', 't-esc="textes.valider"', 't-esc="textes.retour"',
                 "state.motif and state.motif.id === motif.id ? 'btn-primary' : 'btn-outline-primary'",
                 'class="aite-annulation-erreur text-danger text-center fw-bold mt-2"'):
    dans(_POPUP, _extrait, 'annulation_popup.xml')
_POPUP_JS = _une_ligne(_lire(S, 'components', 'annulation_popup', 'annulation_popup.js'))
for _extrait in ('etape: quantites.length > 1 ? "quantite" : this.etapeApresQuantite,',
                 'return this.props.codeRequis ? "code" : "motif";',
                 'if (motif.precision_requise) { this.state.motif = motif; return; } await this.envoyer(motif, false);',
                 'if (!precision) { this.state.erreur = MESSAGES.R24; return; }',
                 # le code refusé vide les points ; l'erreur R24 n'est effacée qu'au toucher d'un motif
                 'this.state.code = ""; this.state.erreur = typeof reponse === "string" ? reponse : "";',
                 'this.state.erreur = ""; if (motif.precision_requise)'):
    dans(_POPUP_JS, _extrait, 'annulation_popup.js')
_STORE = _une_ligne(_lire(S, 'store', 'pos_store.js'))
for _extrait in ('const codeRequis = !(this.aitePeut("annuler_envoye") && this.aiteCodeVisite);',
                 'sousTitre: (codeRequis ? sousTitreCode : sousTitre) || "",',
                 'if (!this.aiteEmployePeut(employe, "annuler_envoye")) { this.notification.add(MESSAGES.R8, '
                 '{ type: "danger" }); return false; }',
                 'const quantites = entieres.at(-1) === envoye ? entieres : [...entieres, envoye];',
                 'titre: TITRES.annulerProduit(produit, this.aiteNomAddition(order)),',
                 'sousTitreCode: MESSAGES.R9(envoye, produit),',
                 'this.notification.add(imprime ? `${texte} ${TEXTES.bonEnvoye}` : texte, { type: "info" });',
                 'if (this.printers_category_ids_set?.size && annules.length) {',
                 'titre: TITRES.annulerTable(this.aiteNomAddition(order)), sousTitre: TEXTES.dejaEnvoyeListe(liste), '
                 'sousTitreCode: TEXTES.dejaEnvoyeListe(liste),',
                 'if (!depuisCommandes) { this.showScreen("FloorScreen"); }'):
    dans(_STORE, _extrait, 'S/store/pos_store.js')
_PAVE = _une_ligne(_lire(S, 'overrides', 'order_summary.js'))
dans(_PAVE, 'if (val === "remove" || negative) { if (line.get_quantity() > envoye) { line.set_quantity(envoye); return; '
            '} this.numberBuffer.reset(); this.pos.aiteAnnulerLigne(line); return; }', 'S/overrides/order_summary.js')
_BOUTONS = _lire(S, 'overrides', 'control_buttons.xml')
for _extrait in ('<attribute name="t-if">pos.aitePeut(\'rembourser\')</attribute>',
                 't-on-click="() => this.pos.onDeleteOrder(this.pos.get_order())">',
                 '<t t-esc="aiteTextes.annulerLaTable"/>', '<t t-esc="aiteTextes.diviser"/>',
                 '<t t-esc="aiteTextes.deplacer"/>'):
    dans(_BOUTONS, _extrait, 'S/overrides/control_buttons.xml')
dans(_lire(S, 'overrides', 'actionpad_widget.xml'), ">J'envoie</t>", 'S/overrides/actionpad_widget.xml')
# La fenêtre « Actions » d'Odoo : son titre, l'ordre de ses boutons (pos_restaurant pose les siens après la note
# générale), les notes grisées sans ligne choisie.
_CB_ODOO = _lire(O, 'point_of_sale', 'static', 'src', 'app', 'screens', 'product_screen', 'control_buttons',
                 'control_buttons.js')
dans(_CB_ODOO, 'footer="false" title="\'Actions\'"', 'O/point_of_sale/…/control_buttons.js')
dans(_CB_ODOO, 'return _t("General Note");', 'O/point_of_sale/…/control_buttons.js')
dans(_lire(O, 'point_of_sale', 'static', 'src', 'app', 'screens', 'product_screen', 'control_buttons',
           'customer_note_button', 'customer_note_button.xml'),
     't-att-disabled="!pos.get_order()?.get_selected_orderline()"', 'O/…/customer_note_button.xml')
dans(_lire(O, 'point_of_sale', 'static', 'src', 'app', 'screens', 'product_screen', 'control_buttons',
           'control_buttons.scss'), 'grid-template-columns: repeat(3, 1fr);', 'O/…/control_buttons.scss')
_PO = _lire(O, 'point_of_sale', 'i18n', 'fr.po') + _lire(O, 'web', 'i18n', 'fr.po')
for _msg, _fr in (('General Note', 'Note générale'), ('Customer Note', 'Note au client'), ('Actions', 'Actions'),
                  ('Search...', 'Rechercher…'), ('Note cuisine', None), ('Client', None),
                  ('Rechercher des produits…', None)):
    if _fr:
        dans(_PO, 'msgid "%s"\nmsgstr "%s"' % (_msg, _fr), 'fr.po d\'Odoo')
    else:
        dans(_PO, 'msgstr "%s"' % _msg, 'fr.po d\'Odoo')

# 3. Les droits, les motifs, le journal et son menu.
_DROITS = _source('models/regles.py', 'DROITS')
_NIVEAUX = [c for c, _l in _source('models/regles.py', 'NIVEAUX')]
assert _DROITS['annuler_envoye'] == 'superviseur', 't19 : droit d\'annuler changé'
assert _NIVEAUX.index('superviseur') >= _NIVEAUX.index(_DROITS['table_collegue'])
_MOTIFS_XML = _lire(R, 'data', 'restaurant_motif_data.xml')
assert re.findall(r'<field name="name">([^<]+)</field>', _MOTIFS_XML) == demo.MOTIFS_RESTO
assert _MOTIFS_XML.count('precision_requise') == 1 and _MOTIFS_XML.index('precision_requise') > \
    _MOTIFS_XML.index('<field name="name">Autre</field>'), 't19 : seul « Autre » demande une précision'
_JOURNAL = _lire(R, 'models', 'restaurant_annulation.py')
for _extrait in ("_order = 'date desc, id desc'", 'fields.Datetime("Date"', 'fields.Char("Table"',
                 'fields.Char("Produit"', 'fields.Float("Quantité"', 'fields.Monetary("Montant TTC"',
                 'fields.Char("Demandée par"', 'fields.Char("Autorisée par"', 'fields.Char("Motif"',
                 'fields.Char("Précision"', "('retrait_sans_code', \"Retrait sans code\")",
                 'def write(self, vals):\n        raise self._aite_refus()',
                 'def unlink(self):\n        raise self._aite_refus()'):
    dans(_JOURNAL, _extrait, 'R/models/restaurant_annulation.py')
_VUES = _lire(R, 'views', 'restaurant_annulation_views.xml')
for _extrait in ('<list string="Annulations" create="0" edit="0" delete="0"', 'decoration-danger="not autorisee"',
                 '<field name="date" options="{\'show_seconds\': False}"', '<field name="quantite" sum="Total"',
                 '<field name="montant" sum="Total" widget="monetary"', '<filter name="aujourd_hui" string="Aujourd\'hui"',
                 "{'search_default_aujourd_hui': 1, 'create': False}", '<field name="view_mode">list,pivot,graph</field>',
                 '<field name="name">Annulations</field>'):
    dans(_VUES, _extrait, 'R/views/restaurant_annulation_views.xml')
assert re.findall(r'<field name="(\w+)"[^>]*/>', _VUES[_VUES.index('<list'):_VUES.index('</list>')])[:9] == [
    'date', 'table_nom', 'produit_nom', 'quantite', 'montant', 'serveur_nom', 'superieur_nom', 'motif_nom',
    'commentaire'], 't19 : colonnes de la liste changées'
_MENUS = _lire(R, 'views', 'restaurant_menus.xml')
dans(_MENUS, '<menuitem id="menu_restaurant_root" name="Restaurant"', 'R/views/restaurant_menus.xml')
dans(_MENUS, '<menuitem id="menu_restaurant_annulation" name="Annulations"', 'R/views/restaurant_menus.xml')
assert MENUS_MUK['restaurant'] == ['Annulations']
_SECU = _lire(R, 'security', 'restaurant_security.xml')
dans(_SECU, '<field name="name">Restaurant : lecture des rapports</field>', 'R/security/restaurant_security.xml')
dans(_SECU, '<record id="point_of_sale.group_pos_manager" model="res.groups">\n'
            '        <field name="implied_ids" eval="[(4, ref(\'group_lecture_rapports\'))]"/>',
     'R/security/restaurant_security.xml (le manager lit le journal)')

# 4. Les touches mesurées (résultats) et les cas de recette cités.
_NOTES = _lire(RACINE, 'docs', 'NOTES_DE_VERSION_restaurant_lot1.md')
# Le bon d'annulation (voir le monde rejoué) : tant que les notes le disent jamais vu et que les tours tournent sans
# imprimante de préparation, la vidéo ne le montre pas. Le jour où l'un des deux change, la construction échoue :
# passer BON_VU à True (la notification, la voix et la bulle de l'étape 4 le reprennent) ou relire.
BON_VU = False
assert BON_VU or "« Bon d'annulation envoyé. » n'a jamais été vu" in _une_ligne(_NOTES), \
    't19 : le bon d\'annulation a été vu (N §8) : passer BON_VU à True'
assert BON_VU or "{'printer_ids': [(5, 0, 0)], 'is_order_printer': False}" in _lire(R, 'tests', 'test_tours.py'), \
    't19 : les tours ont maintenant une imprimante de préparation : relire le bon d\'annulation (BON_VU)'
for _ligne in ('| Serveur — retirer un produit pas encore envoyé | 3 (2 si la ligne est sélectionnée) | **2** '
               '(ligne sélectionnée) |',
               '| Serveur + chef — annuler un produit envoyé, sur le poste du serveur | 3 + 5, + 1 si plus d\'une unité '
               '| **9** (2 unités envoyées) |',
               '| Chef seul — annuler une table qui a des produits envoyés | 8 | **8** |',
               '- Rien n\'est jamais refusé à la synchronisation : ce qui arrive sans code est\n  tracé « Retrait sans code » '
               'ou « Annulation sans code ».'):
    dans(_NOTES, _ligne, 'N (notes de version)')
_RECETTE = _lire(RACINE, 'recette', 'cas_de_test.py')
for _extrait in ('"La 4ᵉ est retirée librement, les trois envoyées restent ; la seconde "',
                 '"Refusé à chaque fois : « Ce code ne peut pas annuler. Il faut celui "',
                 '"en quelques mots pourquoi. » ; avec la précision, la ligne porte le "',
                 '"Le nom du serveur est toujours en haut : il continue sa table."',
                 '"La fenêtre « Annuler la table n » s\'ouvre directement (code d\'un chef "',
                 '"« Autorisée par » ; la vente n\'a jamais été bloquée."',
                 '"Refusé pour tous : « Une annulation enregistrée ne se modifie pas et "',
                 '"Le rapport s\'ouvre ; ni le menu Point de Vente, ni les commandes, ni la "'):
    dans(_RECETTE, _extrait, 'recette/cas_de_test.py')

# ========================================================== les données --
EQUIPE = {x[1]: x for x in demo.EQUIPE_RESTO}
LANDRY, ROLE_LANDRY = demo.POSTES_RESTO['chef']
INES, ROLE_INES = demo.POSTES_RESTO['serveuse']
EDWIGE, ROLE_EDWIGE = demo.POSTES_RESTO['manager']
P_INES, P_LANDRY, P_EDWIGE = INES.split()[0], LANDRY.split()[0], EDWIGE.split()[0]
P_LOIC = demo.POSTES_RESTO['serveur'][0].split()[0]
assert (EQUIPE[P_INES][2], EQUIPE[P_LANDRY][2], EQUIPE[P_EDWIGE][2]) == ('Serveur', 'Chef de salle ou superviseur',
                                                                         'Manager')
CODE_INES, CODE_LANDRY = EQUIPE[P_INES][3], EQUIPE[P_LANDRY][3]
assert CODE_INES != CODE_LANDRY


def _minutes(hhmm):
    h, m = hhmm.split(':')
    return int(h) * 60 + int(m)


# La chronologie (en-tête) : table → (ouverte par, heure d'ouverture) ; les deux instants rejoués.
OUVERTURES = {5: (P_INES, '13:05'), 9: (P_LOIC, '13:28'), 2: (P_LOIC, '12:55'), 4: (P_LOIC, '12:15')}
INSTANT_5, INSTANT_9 = '13:30', '13:48'


def etat_table(n, instant):
    """(couleur, durée) d'une table ouverte (S/utils/alerte.js:18-27, « >= » ; messages.js:165-171)."""
    m = _minutes(instant) - _minutes(OUVERTURES[n][1])
    assert m >= 0 and m != demo.DELAI_ORANGE, 't19 : une table à « 1 h 00 » (ECARTS.md n° 82)'
    return ('orange' if m >= demo.DELAI_ORANGE else 'vert'), duree_resto(m)


DUREES = {n: etat_table(n, INSTANT_9) for n in OUVERTURES}
assert DUREES == {5: ('vert', '43 min'), 9: ('vert', '20 min'), 2: ('vert', '53 min'), 4: ('orange', '1 h 33')}
M_5 = _minutes(INSTANT_5) - _minutes(OUVERTURES[5][1])
M_9 = _minutes(INSTANT_9) - _minutes(OUVERTURES[9][1])
assert (M_5, M_9) == (25, 20)

# La carte, et la couleur de chaque famille (une sous-famille sans couleur prend celle de son parent).
PRIX = {nom: prix for nom, _f, prix, _c, _s in demo.CARTE_RESTO}
FAMILLE = {nom: f for nom, f, _p, _c, _s in demo.CARTE_RESTO}
COULEUR = {}


def _couleurs(branches, parent=0):
    for nom, couleur, enfants in branches:
        COULEUR[nom] = couleur or parent
        _couleurs(enfants, COULEUR[nom])


_couleurs(demo.FAMILLES_RESTO)


def cle(nom):
    """« Bière blonde 65 cl » → « biereblonde65cl » (comme ecrans.resto_familles)."""
    return ''.join(c for c in unicodedata.normalize('NFD', nom.lower()) if c.isalnum())


def tri(nom):
    """L'ordre de localeCompare (O/point_of_sale/…/product_screen.js:417-419) : sans accent ni casse."""
    return ''.join(c for c in unicodedata.normalize('NFD', nom.casefold()) if unicodedata.category(c) != 'Mn')


BIERES = sorted([n for n in PRIX if FAMILLE[n] == 'Bière'], key=tri)
assert BIERES == ['Bière blonde 33 cl', BLONDE, 'Bière brune 65 cl']
assert [FAMILLE[x] for x in (QUATRE, MARGHERITA, COLA)] == ['Pizzas', 'Pizzas', 'Sodas']
CHEMIN = ('Boisson', 'Alcoolisé', 'Bière')

# Les additions : table 5 (11 500, 13 000 avec la 4ᵉ bière, 10 000 après l'annulation) ; table 9 (7 000).
T5_AVANT = PRIX[QUATRE] + 3 * PRIX[BLONDE]
assert (T5_AVANT, T5_AVANT + PRIX[BLONDE], T5_AVANT - PRIX[BLONDE]) == (11500, 13000, 10000)
T9 = PRIX[MARGHERITA] + 2 * PRIX[COLA]
assert T9 == 7000
ENVOYE_9 = ', '.join((TEXTES_RESTO['envoi'](1, MARGHERITA), TEXTES_RESTO['envoi'](2, COLA)))
assert ENVOYE_9 == '1 Pizza Margherita, 2 Cola 33 cl'
PRECISION = 'Bouteille cassée au service'      # texte libre de la démonstration, tapé par Landry

# Le journal du jour (étape 7), dans l'ordre de la liste : (date, table, produit, quantité, demandée par,
# autorisée par, motif, précision).
JOURNAL = [('14/10/2026 13:48', '9', COLA, 2, P_LANDRY, P_LANDRY, demo.MOTIFS_RESTO[1], ''),
           ('14/10/2026 13:48', '9', MARGHERITA, 1, P_LANDRY, P_LANDRY, demo.MOTIFS_RESTO[1], ''),
           ('14/10/2026 13:30', '5', BLONDE, 1, P_INES, P_LANDRY, demo.MOTIFS_RESTO[4], PRECISION),
           ('14/10/2026 11:52', '1', 'Jus de bissap 50 cl', 1, P_LOIC, '', '', '')]
assert demo.MOTIFS_RESTO[1] == 'Client parti' and demo.MOTIFS_RESTO[4] == 'Autre'
assert JOURNAL == demo.ANNULATIONS_JOUR_RESTO, 't19 : le journal du jour a changé, reporter dans demo.py (t22, t23)'
QTE_JOUR = sum(x[3] for x in JOURNAL)
MONTANT_JOUR = sum(x[3] * PRIX[x[2]] for x in JOURNAL)
assert (QTE_JOUR, MONTANT_JOUR) == (5, 9500)


def qte(q):
    """« 2,00 » : une quantité du journal (digits « Product Unit of Measure », C/22)."""
    return ('%.2f' % q).replace('.', ',')


# ============================================================ les écrans --
POS = 't19-pos'


def commande(ident, avant, apres, familles, tuiles):
    """L'écran de commande d'une table rouverte : deux colonnes de gauche posées dans la même case de la grille
    (comme t17) — ``avant`` (arguments de resto_commande : l'addition à l'arrivée, sans ligne choisie, donc sans
    pavé ni « Note cuisine » : C/09) et ``apres`` (la même addition dès qu'une tuile est touchée : ligne choisie,
    pavé) — puis les familles et les tuiles à droite. Identifiants : <ident>v-… (avant), <ident>-… (après),
    <ident>v-g et <ident>-g (les colonnes)."""
    b = resto_commande(ident, familles_html=familles, tuiles_html=tuiles, **apres)
    a = resto_commande(ident + 'v', familles_html='', tuiles_html='', **avant)
    gauche_a = a[a.index('<div class="rs-g">'):a.index('<div class="rs-d">')]
    gauche_a = gauche_a.replace('<div class="rs-g">', '<div class="rs-g" id="%sv-g">' % ident, 1)
    gauche_a = gauche_a.replace('<span class="" id="%sv-note">' % ident, '<span class="gris" id="%sv-note">' % ident, 1)
    assert 'class="gris" id="%sv-note"' % ident in gauche_a
    b = b.replace('<div class="rs-g">', '<div class="rs-g masque" id="%s-g">' % ident, 1)
    return b.replace('<div class="rs-d">', gauche_a + '<div class="rs-d">', 1)


def familles(ident):
    return resto_familles(ident, demo.FAMILLES_RESTO, CHEMIN)


def tuiles(ident, qtes=None):
    return resto_tuiles(ident, [(cle(n), n, COULEUR[FAMILLE[n]]) for n in BIERES], {cle(k): v for k, v in
                                                                                 (qtes or {}).items()})


def L_QUATRE(ident):
    return resto_ligne(ident, QUATRE, 1, PRIX[QUATRE])


# -- 1-4. table 5 : à l'arrivée (rien de choisi), puis la 4ᵉ bière touchée (choisie, pas encore envoyée)
CMD5 = commande('t19-c5', dict(
    etat=etat_commande(5, P_INES, M_5), total=fcfa(T5_AVANT), personnes=2, compteurs=[('Bière', 0)], encaisser=True,
    lignes_html=L_QUATRE('t19-c5v-l1') + resto_ligne('t19-c5v-l2', BLONDE, 3, PRIX[BLONDE]), initiale=True),
    dict(etat=etat_commande(5, P_INES, M_5), total=fcfa(T5_AVANT + PRIX[BLONDE]), personnes=2, compteurs=[('Bière', 1)],
         lignes_html=L_QUATRE('t19-c5-l1') + resto_ligne('t19-c5-l2', BLONDE, 4, PRIX[BLONDE], envoyee=False,
                                                          choisie=True), initiale=True),
    familles('t19-c5-f'), tuiles('t19-c5-tu', {BLONDE: 3}))
TUILE = '#t19-c5-tu-%s' % cle(BLONDE)
assert 'id="t19-c5-tu-%s-q"' % cle(BLONDE) in CMD5 and 'id="t19-c5-keff"' in CMD5 and 'id="t19-c5-env-0-v"' in CMD5

# -- 5. le plan à 13:48, puis la table 9 rouverte par Landry (rien de choisi : pas de pavé)
PLAN = resto_plan('t19-plan', resto_salle('t19-plan', {n: (c, d, None) for n, (c, d) in DUREES.items()}),
                  delai=demo.DELAI_ORANGE, salle=demo.SALLE_RESTO)
CMD9 = resto_commande('t19-c9', etat_commande(9, P_LOIC, M_9),
                      resto_ligne('t19-c9-l1', MARGHERITA, 1, PRIX[MARGHERITA]) + resto_ligne('t19-c9-l2', COLA, 2,
                                                                                              PRIX[COLA]),
                      fcfa(T9), 2, familles('t19-c9-f'), tuiles('t19-c9-tu'), compteurs=[('Bière', 0)], encaisser=True)
CMD9 = CMD9.replace('<span class="" id="t19-c9-note">', '<span class="gris" id="t19-c9-note">', 1)
assert 'class="gris" id="t19-c9-note"' in CMD9


# -- la fenêtre d'annulation (composée ici : voir l'en-tête, « Écarts au storyboard »)
def _retour(ident, cle_):
    return ('<span class="rs-kb rs-k-retour rs-k-large rs-k-plein" id="%s-retour-%s">%s</span>'
            % (ident, cle_, e(TEXTES_RESTO['retour'])))


def panneau_motifs(ident, cle_, choisi=None, champ=False, erreur=False, cache=True):
    """L'étape « Pourquoi ? » de la fenêtre d'annulation (annulation_popup.xml:52-76), dans l'état que montre
    l'application : sans motif à précision touché, les motifs et « Retour » seulement (C/11, C/16) ; « Autre »
    touché (``choisi`` = son rang), le bouton en primaire, « Précision », le champ et « Valider » (:64-73) ; après
    « Valider » sans rien écrire, R24 dessous (:74-75), qui reste jusqu'à la fermeture. Mêmes classes que
    ecrans.resto_annulation. Identifiants : <ident>-<cle_> (le panneau), <ident>-<cle_>-kbs, <ident>-<cle_>-m1…5,
    <ident>-<cle_>-pc (le champ : -ph, -val, pour le geste ``saisir``), <ident>-<cle_>-valider, <ident>-<cle_>-err."""
    p = '%s-%s' % (ident, cle_)
    boutons = ''.join('<span class="rs-kb rs-motif%s" id="%s-m%d">%s</span>' % (' choisi' if k == choisi else '', p, k,
                                                                               e(m))
                      for k, m in enumerate(demo.MOTIFS_RESTO, 1))
    prec = ''
    if champ:
        prec = ('<div class="rs-prec"><label>%s</label><span class="rs-champ t19-champ" id="%s-pc"><span id="%s-pc-ph">'
                '</span><span id="%s-pc-val"></span></span><span class="rs-kb rs-k-prim rs-k-large" id="%s-valider">%s'
                '</span></div>' % (e(TEXTES_RESTO['precision']), p, p, p, p, e(TEXTES_RESTO['valider'])))
    err = '<div class="rs-err" id="%s-err">%s</div>' % (p, e(MESSAGES_RESTO['R24'])) if erreur else ''
    return ('<div class="rs-pan%s" id="%s"><div class="rs-question">%s</div><div class="rs-kbs" id="%s-kbs">%s</div>%s%s%s'
            '</div>' % (' masque' if cache else '', p, e(TEXTES_RESTO['pourquoi']), p, boutons, prec, err,
                        _retour(ident, cle_)))


def fenetre_annulation(ident, titre, sous_titre, panneaux, haut=96):
    """AiteAnnulationPopup (annulation_popup.xml:7-82, taille « md ») : une tête (titre, sous-titre) et les étapes
    empilées au même endroit (le premier panneau dans le flux, les autres par-dessus), comme ecrans.resto_annulation ;
    on passe de l'une à l'autre par cacher / montrer. Identifiants : <ident>-voile, <ident>, <ident>-titre,
    <ident>-st."""
    st = '<div class="rs-st" id="%s-st">%s</div>' % (ident, e(sous_titre)) if sous_titre else ''
    corps = ('<div class="rs-fen-h"><div class="rs-titre" id="%s-titre">%s</div>%s</div><div class="rs-pans">%s</div>'
             % (ident, e(titre), st, ''.join(panneaux)))
    return superpose('<div class="voile masque rs-voile" id="%s-voile"></div>'
                     '<div class="rs-fen rs-annul masque" id="%s" style="top:%dpx">%s</div>' % (ident, ident, haut, corps))


# Le produit : « Combien ? » (3 parties : 1, 2, 3 (tout)), le code, puis « Pourquoi ? » en trois états.
_Q = ''.join('<span class="rs-kb rs-k-prim" id="t19-ann-q%d">%s</span>'
             % (q, e(TEXTES_RESTO['tout'](q) if q == 3 else str(q))) for q in (1, 2, 3))
# Posée à 124 px du haut de la caisse (96 par défaut) : la notification R8, en haut à droite, ne cache pas la fin du
# sous-titre ; l'étape la plus haute (« Pourquoi ? » avec la précision et R24) finit au-dessus du bas de la caisse.
ANNULER = fenetre_annulation('t19-ann', TITRES_RESTO['annulerProduit'](BLONDE, 5), MESSAGES_RESTO['R9'](3, BLONDE), [
    '<div class="rs-pan" id="t19-ann-q"><div class="rs-question">%s</div><div class="rs-kbs">%s</div>%s</div>'
    % (e(TEXTES_RESTO['combien']), _Q, _retour('t19-ann', 'q')),
    '<div class="rs-pan masque" id="t19-ann-c"><div class="rs-question">%s</div>%s%s%s</div>'
    % (e(TEXTES_RESTO['codeChef']), _points('t19-ann'), _pave_code('t19-ann', retour=False), _retour('t19-ann', 'c')),
    panneau_motifs('t19-ann', 'm'),
    panneau_motifs('t19-ann', 'mp', choisi=5, champ=True),
    panneau_motifs('t19-ann', 'me', choisi=5, champ=True, erreur=True)], haut=124)
assert ANNULER.count('id="t19-ann-k7"') == 1 and 'id="t19-ann-me-pc-val"' in ANNULER
# La table : sans « Combien ? » ni code (Landry est identifié : pos_store.js:1261), « Pourquoi ? » seul.
ANNULER_TABLE = fenetre_annulation('t19-at', TITRES_RESTO['annulerTable'](9), TEXTES_RESTO['dejaEnvoyeListe'](ENVOYE_9),
                                   [panneau_motifs('t19-at', 'm', cache=False)], haut=150)

# -- la fenêtre « Actions » d'Odoo (ControlButtonsPopup, taille « lg » : 800 points, ×1,34)
ICO_NOTE = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round">'
            '<path d="M4 4h16v10l-6 6H4z"/><path d="M14 20v-6h6"/></svg>')
BOUTONS_ACTIONS = [('note', '', 'Note générale', True), ('diviser', ICONES['copier'], TEXTES_RESTO['diviser'], False),
                   ('deplacer', ICONES['fleche-droite'], TEXTES_RESTO['deplacer'], False),
                   ('client', ICO_NOTE, 'Note au client', True),
                   ('annuler', ICONES['corbeille'], TEXTES_RESTO['annulerLaTable'], False)]
ACTIONS = _dialogue('t19-act', 'Actions', '<div class="t19-ag">%s</div>' % ''.join(
    '<span class="t19-ab%s" id="t19-act-%s">%s<span>%s</span></span>'
    % (' off' if grise else '', k, '<i class="t19-ai">%s</i>' % ico if ico else '', e(lib))
    for k, ico, lib, grise in BOUTONS_ACTIONS), '', 1072, 150, droite_titre='<span class="rs-x">%s</span>' % ICONES['croix'],
    classe_=' t19-act')

CODE9 = resto_code('t19-code', TITRES_RESTO['table'](9))
N_R8 = resto_notification('t19-n-r8', MESSAGES_RESTO['R8'], genre='danger')
FAITE = TEXTES_RESTO['annulationFaite'](1, BLONDE, P_LANDRY)
if BON_VU:   # pos_store.js:1353 : la phrase du bon, quand il est sorti
    FAITE = '%s %s' % (FAITE, TEXTES_RESTO['bonEnvoye'])
assert FAITE == 'Annulation faite : 1 Bière blonde 65 cl, par Landry.' + (
    ' Bon d\'annulation envoyé.' if BON_VU else '')   # C/12 : la phrase vue à l'écran
N_FAITE = resto_notification('t19-n-faite', FAITE)

CAISSE = fenetre_resto(POS, [CMD5, PLAN, CMD9], calques=ANNULER + ANNULER_TABLE + ACTIONS + CODE9 + N_R8 + N_FAITE,
                       ecran='commande', onglet='5', employe=(P_INES, P_INES[0]), avatar=demo.AVATARS_RESTO[P_INES])

# -- 6. Restaurant › Annulations, sous le compte de la manager
COLS = [('Date', '176px'), ('Table', '62px'), ('Produit', '196px'), ('Quantité', '96px', 'd'),
        ('Montant TTC', '140px', 'd'), ('Demandée par', '150px'), ('Autorisée par', '146px'), ('Motif', '132px'),
        ('Précision', '1fr')]
GABARIT = '34px ' + ' '.join(c[1] for c in COLS)
ICO_LISTE = ('<svg viewBox="0 0 24 24" fill="currentColor"><rect x="3" y="5" width="18" height="2.4"/>'
             '<rect x="3" y="10.8" width="18" height="2.4"/><rect x="3" y="16.6" width="18" height="2.4"/></svg>')
ICO_PIVOT = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3" y="4" width="18" '
             'height="16"/><path d="M3 9h18M3 14.5h18M9 4v16M15 4v16"/></svg>')
ICO_GRAPHE = '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M3 20V9l5 4 4-7 5 5 4-3v12z"/></svg>'
ICO_COLONNES = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round">'
                '<path d="M4 8h16M4 16h16"/><circle cx="15" cy="8" r="2.2" fill="#fff"/><circle cx="9" cy="16" r="2.2" '
                'fill="#fff"/></svg>')


def _cellule(texte_, droite=False):
    return '<span class="ell%s">%s</span>' % (' d' if droite else '', e(texte_))


LIGNES = ''.join(
    '<div class="ligne%s" id="t19-r%d" style="grid-template-columns:%s"><span class="cb"></span>%s</div>'
    % ('' if autorise else ' t19-rouge', k, GABARIT, ''.join([
        _cellule(date), _cellule(table), _cellule(produit), _cellule(qte(q), True), _cellule(fcfa(q * PRIX[produit]), True),
        _cellule(dem), _cellule(autorise), _cellule(motif), _cellule(precision)]))
    for k, (date, table, produit, q, dem, autorise, motif, precision) in enumerate(JOURNAL, 1))
TETE = ('<div class="tete" style="grid-template-columns:%s"><span class="cb"></span>%s<i class="t19-col">%s</i></div>'
        % (GABARIT, ''.join('<span class="ell%s" id="t19-h%d">%s</span>' % (' d' if len(c) > 2 else '', k, e(c[0]))
                            for k, c in enumerate(COLS, 1)), ICO_COLONNES))
TOTAL = ('<div class="total" id="t19-tot" style="grid-template-columns:%s"><span></span>%s</div>'
         % (GABARIT, '<span></span>' * 3 + '<span class="d" id="t19-tot-q">%s</span><span class="d" id="t19-tot-m">%s'
            '</span>' % (qte(QTE_JOUR), fcfa(MONTANT_JOUR)) + '<span></span>' * 4))
CP = ('<div class="cp t19-cp"><span class="titre" id="t19-titre">Annulations</span>%s<span class="pager">1-%d / %d</span>'
      '<span class="t19-fl"><i>‹</i><i>›</i></span><span class="t19-vues"><i class="actif">%s</i><i>%s</i><i>%s</i></span>'
      '</div>' % (recherche([('t19-fac', "Aujourd'hui")]), len(JOURNAL), len(JOURNAL), ICO_LISTE, ICO_PIVOT, ICO_GRAPHE))
LISTE = ('<div class="vue initiale" id="t19-liste">%s<div class="liste t19-liste" id="t19-liste-l">%s%s%s</div></div>'
         % (CP, TETE, LIGNES, TOTAL))
GESTION = fenetre_muk('t19-ges', 'Restaurant', MENUS_MUK['restaurant'], [LISTE], actif='Annulations',
                      societe=demo.SOCIETE_RESTO, initiale=P_EDWIGE[0], avatar=demo.AVATARS_RESTO[P_EDWIGE],
                      apps=APPS_PROFIL['resto_manager'], app_active='Restaurant')
GESTION = GESTION.replace('class="app muk"', 'class="app muk masque"', 1)
GESTION = GESTION.replace('<span class="menu actif">Annulations</span>',
                          '<span class="menu actif" id="t19-ges-menu">Annulations</span>', 1)
assert 'id="t19-ges-menu"' in GESTION and 'id="t19-ges-app-restaurant"' in GESTION

ECRAN = navigateur(CAISSE + GESTION)

CSS = ("/* -- la pastille : Inès (étapes 1-2), Landry (3-6, le personnage), Edwige (7) -- */\n"
       + css_personnage('#tu-perso:not(.t19-landry):not(.t19-edwige)', INES, ROLE_INES, P_INES[0])
       + css_personnage('#tu-perso.t19-edwige', EDWIGE, demo.POSTES_RESTO['manager'][1], P_EDWIGE[0]) + """
/* -- l'avatar de Landry à la caisse (demo.AVATARS_RESTO) : une classe, posée quand il prend la table 9 -- */
#t19-pos-emp-av.t19-landry { background: %s !important; }
/* -- la table 5 : deux colonnes de gauche dans la même case (avant / après le toucher de la tuile, comme t17) -- */
#t19-c5 .rs-cmd > .rs-g { grid-column: 1; grid-row: 1; }
#t19-c5 .rs-cmd > .rs-d { grid-column: 2; grid-row: 1; }
/* sans ligne choisie, pas de pavé (O/point_of_sale product_screen.xml:12 ; capture 09) */
#t19-c5v-pave, #t19-c9-pave { display: none; }
/* -- contraste WCAG AA (contrôle de hyperframes, comme t17) : « %% », « Prix », la quantité sur la tuile -- */
#t19-pos .rs-pk.gris { color: #5C636A; }
#t19-pos .rs-tuile-q { color: #495057; }
/* -- la réaction de Landry sur le plan : dans la moitié vide de la salle, au-dessus de la légende -- */
#t19-r-table { bottom: 360px; }
/* -- la fenêtre d'annulation : le champ de la précision (form-control-lg) -- */
#t19-pos .t19-champ { justify-content: flex-start; }
#t19-pos .t19-champ.focus { border-color: var(--muk-prim); box-shadow: 0 0 0 4px rgba(74,120,146,.22); }
/* -- la fenêtre « Actions » d'Odoo : en-tête et croix, sans pied ; boutons btn-secondary btn-lg py-5 en trois
   colonnes (control_buttons.scss:1-2), grisés (opacité 0,65) sans ligne choisie -- */
#t19-act .rs-dlg-p { display: none; }
#t19-act .rs-dlg-c { padding: 10px 21px 21px; }
.t19-ag { display: grid; grid-template-columns: repeat(3, 1fr); gap: 11px; margin-top: 11px; }
.t19-ab { height: 168px; border-radius: 8px; background: #E2E5E9; color: #212529; font-size: 26px; display: flex;
  align-items: center; justify-content: center; gap: 8px; text-align: center; padding: 0 16px; }
.t19-ab.off { opacity: .65; }
.t19-ai { width: 26px; height: 26px; display: inline-flex; font-style: normal; flex: none; }
.t19-ai svg { width: 26px; height: 26px; }
/* -- Restaurant › Annulations (capture 22) : panneau, flèches, vues, liste -- */
.t19-cp .titre { font-size: 24px; }
.t19-cp .recherche { margin-left: auto; width: 640px; }
.t19-cp .pager { margin-left: auto; }
.t19-fl { display: flex; gap: 2px; }
.t19-fl i { width: 38px; height: 38px; display: flex; align-items: center; justify-content: center; background: #E9ECEF;
  color: #343A40; font-style: normal; font-size: 24px; border-radius: 4px; }
.t19-vues { display: flex; gap: 0; margin-left: 8px; }
.t19-vues i { width: 50px; height: 42px; display: flex; align-items: center; justify-content: center; background: #E9ECEF;
  color: #343A40; }
.t19-vues i:first-child { border-radius: 4px 0 0 4px; } .t19-vues i:last-child { border-radius: 0 4px 4px 0; }
.t19-vues i.actif { background: #D5E1E8; box-shadow: inset 0 0 0 1px var(--muk-prim); }
.t19-vues svg { width: 22px; height: 22px; }
.t19-liste .tete { position: relative; height: 52px; font-size: 18px; column-gap: 12px; padding: 0 44px 0 6px; }
.t19-liste .ligne { height: 52px; font-size: 18px; column-gap: 12px; padding: 0 44px 0 6px; }
.t19-liste .total { height: 52px; font-size: 18px; column-gap: 12px; padding: 0 44px 0 6px; }
.t19-liste .cb { margin-left: 8px; }
.t19-liste .ligne.survol { background: #E3ECF2; }
.t19-liste .ligne.t19-rouge { color: #DC3545; }
.t19-col { position: absolute; right: 12px; top: 14px; width: 24px; height: 24px; display: inline-flex; color: #343A40; }
.t19-col svg { width: 24px; height: 24px; }
""" % demo.AVATARS_RESTO[P_LANDRY])


# ============================================================ les gestes --
def touche(sel, *effets, d=0.5, fx=0.5, fy=0.5):
    """Un toucher : le curseur, l'appui, puis ses effets au moment de l'appui (comme t17)."""
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


def vider(fen, decale=0.0):
    """Les points se vident (code refusé, ou fenêtre fermée)."""
    return [classe('#%s-p%d' % (fen, k), retirer=['plein'], avec=True, decale=decale if k == 0 else 0.0)
            for k in range(4)]


def bascule(avant, apres):
    """Un état remplace l'autre, sans transition (une colonne, une étape de fenêtre)."""
    return [cacher(avant, d=0.05), montrer(apres, d=0.05, y=0, avec=True)]


def vers_plan(**kw):
    """Retour au plan verrouillé : plus personne d'identifié (S/store/pos_store.js:448-455)."""
    return [classe('#' + POS, ajouter=['sur-plan'], retirer=['sur-commande', 'avec-emp'], **kw),
            texte('#%s-onglet' % POS, 'Table', avec=True)]


def vers_commande_landry(table):
    """La table ouverte par le code de Landry : l'écran de commande, son prénom et son avatar en haut."""
    return [classe('#' + POS, ajouter=['sur-commande', 'avec-emp'], retirer=['sur-plan'], avec=True),
            texte('#%s-onglet' % POS, str(table), avec=True), texte('#%s-emp-n' % POS, P_LANDRY, avec=True),
            texte('#%s-emp-av' % POS, P_LANDRY[0], avec=True), classe('#%s-emp-av' % POS, ajouter=['t19-landry'], avec=True)]


Q_TUILE = TUILE + '-q'

ETAPES = [
    # 1. La 4ᵉ bière, pas encore envoyée : ⌫ ⌫, sans code ni trace (2 touches, la ligne déjà choisie : N §3 l.252).
    {'temps': 0, 'titre': 'Pas encore parti : rien à demander',
     'texte': 'Une 4ᵉ bière saisie, pas encore envoyée : ⌫ ⌫, elle s\'en va, sans code ni trace.',
     'voix': "Table cinq, Inès ajoute une quatrième bière, puis se ravise. Celle-ci n'est pas encore partie : deux fois "
             "la touche effacer, et elle s'en va, sans code ni trace.",
     'gestes': [pause(0.5), curseur(TUILE, fx=0.4, fy=0.4, d=0.7), pause(0.3)]
               + touche(TUILE, *bascule('#t19-c5v-g', '#t19-c5-g'), texte(Q_TUILE, '4'), d=0.3)
               + [pause(0.3), anneau('#t19-c5-l2', d=1.5), pause(0.6)]
               + touche('#t19-c5-keff', d=0.7) + [pause(0.2)]
               + touche('#t19-c5-keff', texte('#t19-c5-l2-q', '3,00'), texte('#t19-c5-l2-m', fcfa(3 * PRIX[BLONDE])),
                        classe('#t19-c5-l2', ajouter=['envoyee']), texte('#t19-c5-total', fcfa(T5_AVANT)),
                        classe('#t19-c5-env-0', retirer=['on']), classe('#t19-c5-envoyer', retirer=['actif']),
                        classe('#t19-c5-encaisser', ajouter=['actif']), texte(Q_TUILE, '3'), d=0.3)
               + [pause(0.5), anneau('#t19-c5-l2', d=1.6), pause(0.5)]},
    # 2. Les 3 bières envoyées : ⌫ ⌫ ouvre la fenêtre ; « Combien ? » 1 ; le code d'Inès : R8.
    {'temps': 1, 'titre': 'Déjà parti : verrouillé',
     'texte': 'Les 3 bières envoyées sont verrouillées : ⌫ ⌫ ouvre la fenêtre d\'annulation. Le code d\'une serveuse ne '
              'suffit pas.',
     'voix': "Sur les trois bières déjà parties au bar, effacer ne retire plus rien : la fenêtre d'annulation s'ouvre. "
             "Combien ? Une seule. Inès essaie son propre code : refusé, il faut celui d'un chef de salle.",
     'gestes': touche('#t19-c5-keff', d=0.6) + [pause(0.2)]
               + touche('#t19-c5-keff', ouvrir('t19-ann'), d=0.3)
               + [pause(0.3), anneau('#t19-ann-st', d=1.6), pause(0.3)]
               + touche('#t19-ann-q1', *bascule('#t19-ann-q', '#t19-ann-c'), d=0.6)
               + [pause(0.5)] + taper('t19-ann', CODE_INES)
               + [notifier('t19-n-r8', duree=4.0, decale=0.1)] + vider('t19-ann')
               + [pause(0.4), anneau('#t19-n-r8', d=1.6)]},
    # 3. Le code de Landry, puis « Pourquoi ? » ; « Autre » demande une précision (R24 sans elle).
    {'temps': 1, 'titre': 'Le code du chef, puis pourquoi',
     'texte': 'Landry tape son code, puis touche un motif ; « Autre » demande une précision. Le système central vérifie '
              'le code.',
     'voix': "Landry, le chef de salle, arrive et tape son code. La fenêtre demande pourquoi : cinq motifs, une touche. "
             "Autre demande quelques mots : sans eux, la fenêtre refuse de valider. Landry écrit, valide, et le système "
             "central vérifie son code.",
     'gestes': [classe('#tu-perso', ajouter=['t19-landry']), pause(0.4)] + taper('t19-ann', CODE_LANDRY)
               + [dict(g, decale=0.15) if k == 0 else g for k, g in enumerate(bascule('#t19-ann-c', '#t19-ann-m'))]
               + vider('t19-ann', decale=0.1)
               + [pause(0.4), anneau('#t19-ann-m-kbs', d=1.8), pause(0.3)]
               + touche('#t19-ann-m-m5', *bascule('#t19-ann-m', '#t19-ann-mp'), d=0.6)
               + [pause(0.4)]
               + touche('#t19-ann-mp-valider', *bascule('#t19-ann-mp', '#t19-ann-me'), d=0.6)
               + [pause(0.2), anneau('#t19-ann-me-err', d=1.3)]
               # le doigt touche le champ à droite : le texte tapé, à gauche, reste lisible
               + touche('#t19-ann-me-pc', d=0.5, fx=0.88)
               + [saisir('t19-ann-me-pc', PRECISION), pause(0.3)]
               # la baisse appliquée aussitôt l'autorisation reçue, puis la notification (pos_store.js:1336-1353)
               + touche('#t19-ann-me-valider', fermer('t19-ann'), texte('#t19-c5-l2-q', '2,00'),
                        texte('#t19-c5-l2-m', fcfa(2 * PRIX[BLONDE])), texte('#t19-c5-total', fcfa(T5_AVANT - PRIX[BLONDE])),
                        texte(Q_TUILE, '2'), d=0.6)},
    # 4. « Annulation faite : 1 Bière blonde 65 cl, par Landry. » (C/12) ; Inès reste identifiée. Le bon d'annulation,
    #    jamais vu (N §8), n'est ni montré ni dit : la voix et la bulle disent la trace (R46), que l'étape 7 relit.
    {'temps': 2, 'titre': 'Annulation faite, Inès reste à sa table',
     'texte': ('Une bière de moins, un bon d\'annulation au bar' if BON_VU else 'Une bière de moins, autorisée par '
               + P_LANDRY) + ' ; Inès reste identifiée et continue sa table.',
     'voix': "Annulation faite, par Landry : la bière quitte l'addition, et " + (
         "un bon d'annulation part aussitôt au bar. " if BON_VU else
         "le journal note qui l'a demandée, et qui l'a autorisée. ")
             + "Inès, elle, n'a pas cédé sa place : elle reste identifiée, et continue sa table.",
     'gestes': [notifier('t19-n-faite', duree=6.0), pause(0.4), anneau('#t19-n-faite', d=1.8),
                # la bulle de la trace sous la tuile de la bière, dans la partie vide : sous la ligne, elle cacherait
                # le total ; sous la notification, elle survivrait à celle-ci (6 s)
                anneau('#t19-c5-l2', d=1.3), bulle('b-bon', '#t19-n-faite', cote='bas', d=2.8) if BON_VU else
                bulle('b-trace', TUILE, cote='bas', d=2.8),
                pause(2.3), curseur('#%s-emp' % POS, fx=0.3, fy=0.9, d=0.5), anneau('#%s-emp' % POS, d=1.4),
                # la réaction s'efface avant le retour au plan de l'étape 5
                reaction('t19-r-code', d=2.0), pause(0.6)]},
    # 5. La table 9 : la table, le code de Landry, « Actions » (6 touches sur les 8 : N §3 l.257).
    {'temps': 2, 'titre': 'Une table entière : la table, son code',
     'texte': 'Table 9, client parti : Landry touche la table, tape son code, puis « Actions ».',
     'voix': "Plus tard, le client de la table neuf est parti. Landry touche la table de Loïc et tape son code : c'est "
             "son prénom qui s'affiche en haut, et la table reste ouverte par Loïc. Puis il touche Actions.",
     # la barre du plan change quand l'écran de commande s'est effacé (vue : 0,25 s), pas par-dessus lui
     'gestes': [vue('t19-plan', 'pos')] + vers_plan(avec=True, decale=0.25)
               + [pause(0.3)]
               + touche('#t19-plan-t9', ouvrir('t19-code'), d=0.7, fy=0.3)
               + [pause(0.3)] + taper('t19-code', CODE_LANDRY)
               + [pause(0.2), fermer('t19-code'), vue('t19-c9', 'pos', avec=True)] + vers_commande_landry(9)
               + vider('t19-code', decale=0.4)
               + [pause(0.3), anneau('#%s-emp' % POS, d=1.2), anneau('#t19-c9-etat', d=1.5)]
               + touche('#t19-c9-actions', ouvrir('t19-act'), d=0.6) + [pause(0.3)]},
    # 6. « Annuler la table », « Client parti » : la table libre, sans code à retaper (8 touches en tout).
    {'temps': 2, 'titre': 'Un seul motif pour toute la table',
     'texte': '« Annuler la table », puis un motif : la table est libre. Table, code, « Actions », « Annuler la '
              'table », motif : 8 touches.',
     'voix': "Annuler la table : la fenêtre rappelle tout ce qui est déjà parti. Son code sert déjà : pas de code à "
             "retaper, un motif suffit. La table redevient libre, et chaque produit est tracé.",
     # le curseur quitte la place d'« Annuler la table », où s'ouvre « Retour », dès que la fenêtre paraît
     'gestes': touche('#t19-act-annuler', fermer('t19-act'), ouvrir('t19-at', decale=0.15),
                      curseur('#t19-at-m-m2', fx=0.6, fy=0.8, d=0.5, decale=0.05), d=0.6)
               + [pause(0.3), anneau('#t19-at-st', d=1.8), pause(0.3)]
               + touche('#t19-at-m-m2', fermer('t19-at'), vue('t19-plan', 'pos'), *vers_plan(),
                        classe('#t19-plan-t9', ajouter=['libre'], retirer=['vert', 'avec-duree']),
                        texte('#t19-plan-t9-d', ''), curseur('#t19-plan-t9', fx=0.8, fy=0.2, d=0.5, decale=0.1), d=0.3)
               + [pause(0.5), anneau('#t19-plan-t9', d=1.4),
                  bulle('b-table', '#t19-plan-t12', cote='droite', d=3.0), pause(2.4),
                  # la réaction de Landry s'efface avant que la gestion d'Edwige paraisse (étape 7)
                  reaction('t19-r-table', d=1.9), pause(0.6)]},
    # 7. Restaurant › Annulations, sous le compte de la manager.
    {'temps': 3, 'titre': 'Restaurant › Annulations',
     'texte': 'Aujourd\'hui d\'office : qui a demandé, qui a autorisé, pourquoi. En rouge : arrivé sans code, jamais '
              'bloqué.',
     'voix': "Dans la gestion, Edwige, la manager, ouvre Restaurant, puis Annulations : aujourd'hui, d'office. Chaque "
             "ligne dit qui a demandé, qui a autorisé, et pourquoi. En rouge, un retrait arrivé sans code, par un poste "
             "en retard : jamais bloqué, toujours tracé. Le chef de salle peut le relire aussi, sans accès au Point de "
             "Vente.",
     'gestes': [montrer('#t19-ges', d=0.5, y=0), classe('#tu-perso', ajouter=['t19-edwige'], retirer=['t19-landry'],
                                                         avec=True),
                pause(0.3), curseur('#t19-ges-app-restaurant', fx=0.6, d=0.6), anneau('#t19-ges-app-restaurant', d=1.0),
                curseur('#t19-ges-menu', fx=0.5, d=0.4), anneau('#t19-ges-menu', d=1.0),
                anneau('#t19-fac', d=1.3), curseur('#t19-r3', fx=0.5, fy=0.7, d=0.5), anneau('#t19-h6', d=1.0),
                anneau('#t19-h7', d=1.0), anneau('#t19-h8', d=1.0), curseur('#t19-r4', fx=0.62, fy=0.7, d=0.5),
                anneau('#t19-r4', d=1.6), bulle('b-fige', '#t19-tot', cote='bas', d=2.8), pause(2.3),
                bulle('b-profil', '#t19-tot', cote='bas', d=3.0), pause(1.2)]},
]

TUTORIEL = {
    'slug': 't19-restaurant-annulations',
    'profil': 't19_restaurant_annulations',
    'numero': 19,
    'titre': 'Annuler sous le code du chef de salle',
    'fonction': 'Annulations contrôlées',
    'personnage': (LANDRY, ROLE_LANDRY),
    'accroche': {
        'kicker': 'Ce qui est parti en cuisine',
        # Les douleurs : P l.305 (REST-10), l.319 (REST-11), l.326 et l.334 (REST-12), reformulées sans aucun nom.
        'question': 'Qui a *annulé* cette bière, et pourquoi ?',
        'douleurs': [('corbeille', 'N\'importe qui retire un produit déjà envoyé'),
                     ('cle', 'Le chef doit prendre la caisse à son nom pour annuler'),
                     ('interrogation', 'Des annulations sans motif, à l\'auteur incertain'),
                     ('alerte', 'Une table annulée d\'un coup, sans trace'),
                     ('cahier', 'Le rapport refait de mémoire en fin de service'),
                     ('graphe', 'Aucun total des annulations')],
        'voix': "Une bière déjà partie au bar disparaît de l'addition. Qui l'a retirée, et pourquoi ? Sans code ni "
                "motif, le rapport du soir se refait de mémoire.",
    },
    'revelation': {
        # N §1 règle 3 (l.44-45) ; verrou : S/overrides/order_summary.js:52-60 ; code et motif vérifiés par le système
        # central : R/models/pos_order.py:632-649 ; trace : R/models/restaurant_annulation.py:1-20.
        'promesse': 'Ce qui est parti en cuisine ou au bar se verrouille. Pour l\'annuler : combien, le code d\'un chef '
                    'de salle, un motif. Chaque annulation est tracée.',
        'voix': "Avec Aïte haousse, ce qui est parti ne s'annule qu'avec le code d'un chef de salle, et un motif.",
    },
    'temps': ['Retirer', 'Autoriser', 'Tracer', 'Relire'],
    'app': POS,
    'ecran': ECRAN,
    'css': CSS,
    'vues_initiales': {'pos': 't19-c5'},
    'bulles': {
        # S/store/pos_store.js:1357-1363 (le bon de la seule ligne annulée, REST-11 critère 1) si BON_VU ; sinon
        # R/models/pos_order.py:672-689 (serveur = la personne identifiée, superieur = le code vérifié),
        # R/models/restaurant_annulation.py:61-70, rec R46.
        **({'b-bon': 'Le bon d\'annulation ne porte que la ligne annulée.'} if BON_VU else
           {'b-trace': 'Au journal : demandée par %s, autorisée par %s.' % (P_INES, P_LANDRY)}),
        # R/models/pos_order.py:669-689 (une ligne de journal par produit envoyé, nature « table »).
        'b-table': 'Chaque produit de la table est tracé, avec le motif et le nom de Landry.',
        # R/models/restaurant_annulation.py:15-20, 90-99 ; rec R49.
        'b-fige': 'Une ligne ne se modifie pas et ne s\'efface pas, même par l\'administrateur.',
        # R/security/restaurant_security.xml:18-23 ; docs/INSTALLATION.md:306 ; rec R83.
        'b-profil': 'Le chef de salle le lit avec le seul profil « Restaurant : lecture des rapports ».',
    },
    'reactions': {
        't19-r-code': 'Mon code, un motif : c\'est tracé.',
        't19-r-table': 'Un motif, et la table est libre.',
    },
    'etapes': ETAPES,
    'resultats': {
        'titre': 'Chaque annulation a un nom et une raison',
        'cartes': [
            # N §3 l.255 (mesuré par AiteParcoursTour, deux unités envoyées, un motif d'une touche).
            {'valeur': '9', 'compter': 9, 'unite': 'touches', 'icone': 'cle',
             'texte': 'pour annuler un produit envoyé, au poste du serveur, code du chef compris, avec un motif '
                      'd\'une touche'},
            # N §3 l.257 (mesuré).
            {'valeur': '8', 'compter': 8, 'unite': 'touches', 'icone': 'corbeille',
             'texte': 'pour que le chef de salle annule seul une table entière'},
            # R/data/restaurant_motif_data.xml:8-28 (noupdate : le manager les change).
            {'valeur': '5', 'compter': 5, 'unite': 'motifs', 'icone': 'liste',
             'texte': 'posés d\'office ; « Autre » demande une précision'},
        ],
        'voix': "Neuf touches pour annuler un produit, huit pour une table entière, et cinq motifs déjà prêts.",
    },
    'cta': {
        'appel': 'Demandez votre démonstration',
        'sous_marque': demo.SOUS_MARQUE_RESTO,
        'suivant': 'Produits épuisés',
        'voix': "Aïte haousse, par Aïte Consulting. Demandez votre démonstration. Prochain tutoriel : les produits "
                "épuisés.",
    },
    # La fenêtre d'annulation à l'étape « Pourquoi ? », juste après le code de Landry, avant « Autre » (C/11).
    'vignette': {'etape': 3, 'apres': 5.4},
}


def _typo(texte_):
    """Les textes à l'écran écrits ici (pas la voix) : une espace insécable dans les guillemets et avant « : »,
    « ; », « ? », pour qu'un signe ne passe pas seul à la ligne (comme S/utils/messages.js:7-9 ; t17)."""
    for avant, apres in (('« ', '« '), (' »', ' »'), (' :', ' :'), (' ;', ' ;'), (' ?', ' ?')):
        texte_ = texte_.replace(avant, apres)
    return texte_


for _etape in ETAPES:
    _etape['titre'], _etape['texte'] = _typo(_etape['titre']), _typo(_etape['texte'])
for _groupe in ('bulles', 'reactions'):
    TUTORIEL[_groupe] = {_k: _typo(_v) for _k, _v in TUTORIEL[_groupe].items()}
for _carte in TUTORIEL['resultats']['cartes']:
    _carte['texte'] = _typo(_carte['texte'])
TUTORIEL['revelation']['promesse'] = _typo(TUTORIEL['revelation']['promesse'])
TUTORIEL['accroche']['question'] = _typo(TUTORIEL['accroche']['question'])
TUTORIEL['accroche']['douleurs'] = [(_i, _typo(_t)) for _i, _t in TUTORIEL['accroche']['douleurs']]
