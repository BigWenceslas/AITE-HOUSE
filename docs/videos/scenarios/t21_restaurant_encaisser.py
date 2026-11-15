# -*- coding: utf-8 -*-
"""Tutoriel 21 — Encaisser une table.

Le sixième des huit tutoriels du restaurant (lot 1 : aite_pos_restaurant, incrément 2 « J'encaisse » réservé et
incrément 3 « ouverte par » / « encaissée par », division ; restaurant SANS hôtel, comme t16 : demo.RESTO,
demo.SOCIETE_RESTO). Toute la vidéo se passe sur la caisse plein écran au service à table contrôlé (ecrans.py,
« La caisse du restaurant »), sans barre MuK. Storyboard : scratchpad videos_resto/storyboards/t21.md (adapté : voir
« Écarts au storyboard » ; le code et demo.TABLES_JOUR_RESTO font foi).

Abréviations : R/ = addons/aite_pos_restaurant/ ; S/ = R/static/src/ ; O/ = ../odoo18/addons/ ;
N = docs/NOTES_DE_VERSION_restaurant_lot1.md ; P = docs/PERIMETRE_FONCTIONNEL_RESTAURANT.md ;
rec = recette/cas_de_test.py ; C/nn = captures/restaurant/nn_*.jpg (modèles visuels, jamais incrustés). Les phrases
du produit sont relues dans le code au chargement (garde-fous plus bas) : une phrase changée dans le module fait
échouer la construction de la vidéo au lieu de la rendre fausse.

Personnages (la pastille du haut change de personne par une classe, ecrans.css_personnage, comme t16 à t20) :
Prisca, la caissière (demo.POSTES_RESTO['caisse'], code 6304), personnage du tutoriel (étapes 2 à 5) ; Loïc, le
serveur (demo.POSTES_RESTO['serveur'], code 4827), imprime l'addition à l'étape 1 ; Inès, la serveuse
(demo.POSTES_RESTO['serveuse'], code 5913), touche « J'encaisse » au début de l'étape 5. La réaction est celle de
Prisca.

Le monde rejoué (conditions écrites ici, pour que chaque image soit vraie) :
- le 14/10/2026, jour de référence de la série, la caisse « Restaurant » ouverte le matin par Prisca (t17), salle
  « Salle », douze tables, délai de 60 minutes (R/models/pos_config.py:36) ; aucune date ni heure à la caisse
  (seulement les durées) ; carte demo.CARTE_RESTO, société sans TVA (pas de ligne « Taxes ») ;
- une imprimante de tickets (« Addition » imprime et rend le plan : S/overrides/control_buttons.js:73-88 ; mesuré
  avec une imprimante simulée : N §3 l.251 ; jamais essayé sur une imprimante réelle : N §8), pas d'imprimante de
  préparation (DESIGN.md, « Le restaurant ») ; deux modes de paiement, « Espèces » et « Mobile Money »
  (R/models/pos_config.py:83-84, 189-199), aucun mode « payer plus tard » (réservé au manager s'il existait :
  S/overrides/payment_screen.js:1-25 ; rec R101) ;
- une seule tablette pour la salle (t19) : la famille choisie en dernier sur le poste reste choisie
  (O/point_of_sale/static/src/app/store/pos_store.js:1058-1068 ; ECARTS.md n° 96) : Boisson › Alcoolisé › Bière à midi
  (choisie par Inès sur la table 5 avant 13:48, t19) et le soir (Inès ajoute les bières brunes à la table 10, t20) ;
- une table rouverte n'a pas de ligne choisie : pas de pavé, « Note cuisine » grisé (O/point_of_sale/…/
  product_screen.xml:13 ; customer_note_button.xml:7 ; C/09 ; resto_commande(sans_ligne=True)) ; la part née d'une
  division et l'addition d'origine non plus (les lignes y sont créées ou retirées sans select_orderline :
  O/pos_restaurant/static/src/app/split_bill_screen/split_bill_screen.js:113-165 ; O/point_of_sale/static/src/app/
  models/pos_order.js:563, 587-592) ;
- la chronologie (demo.TABLES_JOUR_RESTO ; heures d'ouverture posées par le serveur : R/models/pos_order.py:11-16),
  durées et couleurs calculées plus bas (DUREES) par la règle de la caisse (S/utils/alerte.js:18-27 ;
  S/utils/messages.js:165-171), aucune table à « 1 h 00 » (ECARTS.md n° 82) :

    table  ouverte par  à      13:50 (ét. 1)   13:52 (ét. 2)   14:10 (ét. 3)   14:11 (ét. 4)   19:55 (ét. 5)
    2      Loïc         12:55  55 min          57 min          1 h 15 orange   1 h 16 (2B)     —
    4      Loïc         12:15  1 h 35 orange   1 h 37 orange   libre           libre           —
    5      Inès         13:05  45 min          47 min          libre           libre           —
    10     Inès         19:10  —               —               —               —               45 min

  à 13:48 (t19), 2, 4 et 5 sont les seules tables ouvertes (6, 7 et 10 de midi encaissées, 9 annulée) ; la table 5
  est encaissée à 14:05 (t19, en-tête) ; aucune autre table ne s'ouvre avant 14:11 ; le soir, la table 10 est la
  seule ouverte (t20) jusqu'à son encaissement (condition posée ici) ;
- table 4 (Loïc, 6 personnes) : ce que t17 a envoyé (Pizza Margherita, 2 Bière blonde 65 cl, 2 Cola 33 cl), plus
  une Pizza quatre fromages et 2 Eau minérale 50 cl ajoutées et envoyées entre 13:00 et 13:30 (aucune pastille sur
  les plans de t18 et t19 ; avant que la famille Bière soit choisie sur la tablette, qu'elle garde à 13:48 : t19) :
  18 000 FCFA, 8 articles, encaissée en espèces à 13:52 par Prisca ;
- table 2 (Loïc, 2 personnes : t18) : les 2 Cola 33 cl envoyés par Landry à 13:00 (t18), plus une Pizza Reine et
  une Pizza quatre fromages ajoutées et envoyées entre 13:00 et 13:30 (même raison) : 15 000 FCFA. Divisée à 14:11 :
  la part « 2B »
  (Pizza Reine, 6 000 FCFA, Mobile Money, 0 personne), puis la table 2 (9 000 FCFA, espèces, 2 personnes) ;
- table 10 du soir (Inès, 4 personnes : t20) : Pizza Reine, 2 Bière blonde 65 cl, Cola 33 cl, Pizza quatre
  fromages, 2 Bière brune 65 cl, tout envoyé, 20 000 FCFA ; encaissée en espèces à 19:56 par Prisca, au poste
  d'Inès. Ces encaissements sont à reporter dans demo.TABLES_JOUR_RESTO (t22 et t23 les reprennent).

Écrans et libellés (tous rejoués par ecrans.py, « La caisse du restaurant », sauf l'écran de division, composé ici) :
- le plan verrouillé (C/03, C/07, C/08) : « Plan », « Table », logo, ≡, sans nom ni « + » (S/overrides/navbar.xml:
  18-23 ; S/overrides/order_tabs.xml) ; bouton « Salle » (pos_config.py:82) ; phrase TEXTES.planEtat (messages.js:97) ;
  tables gris / vert / orange et durée (S/overrides/floor_screen.xml:31-44) ; légende TEXTES.legendeParties(60)
  (messages.js:150-158), dont « Orange : ouverte depuis plus de 60 min, proposez l'addition » ;
- la fenêtre du code « Table 4 — votre code », « Table 2 — votre code » (TITRES.table, messages.js:73 ; C/04 ;
  S/components/code_popup/code_popup.xml:10-37) ; une table occupée : le code seul (S/store/pos_store.js:897-910) ;
- l'écran de commande (C/06, C/09) : onglet « 4 », « 2 », « 2B », « 10 » (O/pos_restaurant/static/src/overrides/
  components/navbar/navbar.xml:19-28 : getName().slice(0, 7)), « Rechercher des produits… », code-barres, avatar et
  prénom (S/overrides/navbar.xml:18-20) ; phrase d'état « Table 4 · ouverte par Loïc · 1 h 35 » (pos_store.js:
  1136-1151 ; S/overrides/product_screen.xml:13-16 ; messages.js:114-116, 165-171) ; lignes (O/point_of_sale/…/
  orderline/orderline.xml), « Total » ; « 6 personnes », « Addition », « Client », « Note cuisine » (grisé),
  « Actions » (S/overrides/control_buttons.xml:17-34) ; « J'envoie » gris et centré, « J'encaisse » primaire, tout
  étant parti (S/overrides/actionpad_widget.xml:13-18 ; O/pos_restaurant/…/actionpad_widget.js:32-38, 56-62) ;
  familles et tuiles de Bière, avec la quantité de l'addition (O/point_of_sale/…/product_card.xml:24) ;
- l'écran de paiement (C/13 ; ecrans.resto_paiement) : « Espèces », « Mobile Money », « Client », « Facture »,
  pavé, « Retour », « Valider » ; le montant en vert ; « 3 000 FCFA / Convive » s'il y a plus d'une personne
  (O/pos_restaurant/static/src/overrides/components/payment_screen/payment_screen.xml:24-30, getTotalDue ÷ personnes :
  O/pos_restaurant/static/src/overrides/models/pos_order.js:20-25 ; « / Convive » : O/pos_restaurant/i18n/fr.po:
  44-46) ; « Veuillez sélectionner un mode de paiement », puis « Restant » « 0 FCFA » et la ligne du mode
  (O/point_of_sale/i18n/fr.po:5578-5579, 6618-6619) ; après « Valider », pas d'écran de ticket : le plan
  verrouillé (S/overrides/receipt_screen.js:1-19), ou la table d'origine après une part (:16) ;
- la fenêtre « Actions » d'Odoo (ecrans.resto_actions, relevée pour t19 ; titre : O/point_of_sale/…/control_buttons/
  control_buttons.js:139-145) : « Note générale » et « Note au client » grisés, « Diviser l'addition », « Déplacer ou
  réunir », « Annuler la table » (messages.js:110-112) ; pas de « Remboursement » pour la caissière
  (S/overrides/control_buttons.xml:28-30 ; regles.DROITS['rembourser'] = 'manager') ; aucune capture ;
- l'écran de division (O/pos_restaurant/static/src/app/split_bill_screen/split_bill_screen.xml:4-40 ; aucune
  capture) : en-tête, bouton de retour (chevron), titre « Partage d'addition » (msgid « Bill Splitting »,
  O/pos_restaurant/i18n/fr.po:262-265) ; à gauche les lignes, la ligne touchée choisie (« selected active »,
  orderline.scss) et sa quantité « 1 / 1,00 » (split_bill_screen.js:176-184 ; unité regroupable : :30-45,
  O/point_of_sale/data/point_of_sale_data.xml:35-37) ; à droite le montant de la part en vert (« text-success »,
  :26-30 ; taille : O/pos_restaurant/static/src/xml/Screens/SplitBillScreen/SplitBillScreen.scss:1-3), puis le
  bouton primaire « Créer l'addition à part » (S/overrides/split_bill_screen.xml:6-13 ; messages.js:113) ;
- la part : nommée « 2B » d'après sa table (split_bill_screen.js:56-82, 101-110), elle n'a pas de table : un onglet
  « 2B » paraît en plus dans la barre tant qu'elle est ouverte (O/point_of_sale/static/src/app/navbar/navbar.js:67-69,
  getOrderTabs ; order_tabs.xml : btn-secondary active) ; « Table 2B · ouverte par Loïc · 1 h 16 » (pos_store.js:
  1141, floating_order_name ; heure et « ouverte par » copiés : S/overrides/split_bill_screen.js:40-50) ; pas de
  bouton des personnes, sans table ni personne (S/overrides/control_buttons.xml:18) ;
- la fenêtre « Code de la personne qui encaisse » (TITRES.encaisser, messages.js:75), sous-titre « Inès ne peut pas
  encaisser : la caissière tape son code ici. » (TEXTES.neSaitPasEncaisser, messages.js:101-102 ; pos_store.js:
  789-807 ; rec R05), posée à 128 px du haut de la caisse, sous la phrase d'état.

Règles dites par la voix, les légendes et les bulles :
- « Addition » est un geste du serveur, encaisser non : regles.DROITS['servir'] (commentaire : « addition ») et
  ['encaisser'] = 'caissiere' (R/models/regles.py:33-37) ; rec R10 ;
- l'addition imprimée rend le plan, verrouillé : control_buttons.js:81-84 ; « Table, code, Addition » : 6 touches
  (N §3 l.251) ;
- la caissière qui a tapé son code à la table encaisse sans le retaper (pay() : pos_store.js:789-791) ; elle peut
  toucher la table d'un collègue (« table_collegue », regles.py:35 ; pos_store.js:504-517) ; « ouverte par » ne
  change pas (R/models/pos_order.py:11-12, CHAMPS_FIGES :73 ; N §3 l.265 ; rec R04) ; 8 touches (N §3 l.258) ;
- « Encaissée par » : l'employé de l'addition au paiement, écrit par Odoo (le serveur) seul, la caisse ne peut pas
  l'écrire (pos_order.py:17-18, CHAMPS_SERVEUR :67-72, champ « L'employé qui a validé le paiement avec son code »
  :92-95, 240-245) ; rec R04 ;
  vérifié après le tour du service : la table encaissée par la caissière au poste de la serveuse garde « ouverte par »
  la serveuse et « encaissée par » la caissière, la part aussi (R/tests/test_tours.py:774-790 ; N §3 l.269-274) ;
- pas d'écran de ticket, le plan revient, la table est libre : receipt_screen.js:1-19 ; tour R/static/tests/tours/
  parcours_tour.js:343-354 ;
- diviser : « Actions », « Diviser l'addition », le produit, « Créer l'addition à part » ; la caisse revient d'elle-même
  à la table d'origine, la caissière toujours identifiée ; 15 touches pour n = 1 (N §3 l.261 ; parcours_tour.js:
  431-452 ; rec R59) ; le mode coûte une touche, quel qu'il soit (un mode ajoute la ligne du restant dû) : 15 vaut
  avec Mobile Money, sans avoir été mesuré ainsi ;
- la part compte 0 personne, l'origine garde les siennes (S/overrides/split_bill_screen.js:9-11, 48, 51-57 ;
  regles.compteurs) ;
- « Remboursement » réservé au manager : control_buttons.xml:28-30 ; messages.js:40 (R16) ;
- au poste d'une serveuse restée identifiée : « J'encaisse » ouvre la fenêtre du code ; un code de serveur y est
  refusé (R10, messages.js:34) et la fenêtre attend ; le code reconnu devient la personne du poste, puis le paiement
  s'ouvre (pos_store.js:784-807, aiteIdentifier → aiteDevenir :169-188) ; 7 touches (N §3 l.259 ; rec R05) ;
- les douleurs de l'accroche : P l.154 (Odoo garde un seul nom par addition, réécrit à la validation du paiement au
  nom de l'employé alors connecté, C6, C7 : le nom de la serveuse disparaît, ou l'encaissement est enregistré à son
  nom si la caissière ne s'identifie pas ; le retour au plan laisse l'employé connecté, C4),
  l.194 (« le bouton de paiement n'est lié à aucun rôle »), l.364 (la division « fait passer une personne de
  l'addition d'origine à la nouvelle », C19, C33).

Écarts au storyboard (le code et la journée commune font foi) :
- l'équipe est celle de demo.EQUIPE_RESTO : Loïc (serveur) et Edwige (manager) au lieu des prénoms du storyboard ;
- la table 4 est encore ouverte à 13:48 (t19 ; demo.TABLES_JOUR_RESTO) : elle est encaissée à 13:52, orange, et non
  à 12:41, verte à « 50 min » ; la table 10 encaissée est celle du soir (Inès, t20), pas une table de midi ;
- la division se fait sur la table 2 de Loïc (2 personnes, t18), à 14:11, et non sur une table 9 encaissée à
  12:47 : à cette heure, l'état des tables 1, 6, 7 et 10 sur le plan n'est fixé par aucun tutoriel, alors qu'à 14:10
  le plan entier est connu (t19) ;
- pas d'étape « Personnes et tables » dans la gestion : sa liste du jour (« Aujourd'hui » d'office, R/views/
  pos_order_views.xml:132-140) montrerait toutes les additions réglées de la journée, dont celles de midi qu'aucun
  tutoriel n'a encore fixées (personnes, articles, montants, qui a encaissé) ; t23 la montre une fois la journée
  fixée. « Encaissée par » est dit par la voix et par une bulle à l'écran de paiement (étape 2), puis par la voix
  à l'étape 5, quand le prénom en haut de la caisse passe d'Inès à Prisca ;
- la vignette est l'écran de paiement de la table 4 après « Espèces », comme le storyboard.

Mise en forme propre à ce tutoriel (clé « css ») : la pastille et l'avatar de Loïc et d'Inès, l'onglet de la part
« 2B », l'écran de division. Les textes à l'écran écrits ici prennent une espace insécable dans les guillemets et
avant « : », « ; », « ? » (ecrans.typo_resto).
"""

import ast
import os
import re

import demo
from ecrans import (MESSAGES_RESTO, TEXTES_RESTO, TITRES_RESTO, _odoo_dir, cle_resto, css_personnage, duree_resto, e,
                    etat_commande, fcfa, fenetre_resto, navigateur, resto_actions, resto_code, resto_commande,
                    resto_familles, resto_ligne, resto_paiement, resto_plan, resto_produits, resto_salle, resto_tuiles,
                    typo_resto)
from marketing import bulle, reaction
from moteur import anneau, cacher, classe, clic, curseur, fermer, montrer, ouvrir, pause, texte, vue

RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
R = os.path.join(RACINE, 'addons', 'aite_pos_restaurant')
S = os.path.join(R, 'static', 'src')
O = os.path.join(_odoo_dir(), 'addons')


def _lire(*chemin):
    with open(os.path.join(*chemin), encoding='utf-8') as f:
        return f.read()


def _une_ligne(texte_):
    return ' '.join((texte_ or '').split())


# ============================================================== garde-fous --
# 1. Les textes de la caisse : chaque phrase montrée est relue dans S/utils/messages.js (source JS, espaces ramenées à
#    une seule), puis comparée à ce que les composants d'ecrans.py affichent (comme t17).
_JS = _une_ligne(_lire(S, 'utils', 'messages.js'))


def _js(extrait, **valeurs):
    """Le texte d'un littéral de messages.js (``extrait`` doit y être mot pour mot), ``${ESP}`` → espace
    insécable, ``${x}`` → ``valeurs['x']``."""
    assert extrait in _JS, ('t21 : texte changé dans messages.js', extrait)
    t = re.search(r'(["`])(.*)\1', extrait).group(2).replace('${ESP}', '\u00a0')
    for cle_, val in valeurs.items():
        t = t.replace('${%s}' % cle_, str(val))
    assert '${' not in t, extrait
    return t


assert _js('planEtat: "Touchez une table, puis tapez votre code."') == TEXTES_RESTO['planEtat']
assert _js('table: (numero) => `Table ${numero} — votre${ESP}code`', numero=4) == TITRES_RESTO['table'](4)
assert _js('encaisser: "Code de la personne qui encaisse"') == TITRES_RESTO['encaisser']
assert _js('`${nom} ne peut pas encaisser${ESP}: la caissière tape son code ici.`', nom='Inès') == \
    TEXTES_RESTO['neSaitPasEncaisser']('Inès')
assert _js('R10: `Vous ne pouvez pas encaisser. Appelez la caissière${ESP}: elle tapera son code ici.`') == \
    MESSAGES_RESTO['R10']
assert _js('R16: "Seul le manager peut rembourser une addition payée."')
assert _js('addition: "Addition"') == TEXTES_RESTO['addition']
assert _js('diviser: "Diviser l\'addition"') == TEXTES_RESTO['diviser']
assert _js('deplacer: "Déplacer ou réunir"') == TEXTES_RESTO['deplacer']
assert _js('annulerLaTable: "Annuler la table"') == TEXTES_RESTO['annulerLaTable']
assert _js('creerLaPart: "Créer l\'addition à part"') == TEXTES_RESTO['creerLaPart']
assert _js('retour: "Retour"') == TEXTES_RESTO['retour']
assert _js('`${nombre} personnes`', nombre=6) == TEXTES_RESTO['personnes'](6)
assert 'return `${heures} h ${String(minutes % 60).padStart(2, "0")}`;' in _JS and duree_resto(76) == '1 h 16'
assert ' · '.join((_js('table: (numero) => `Table ${numero}`', numero='2B'),
                   _js('ouvertePar: (nom) => `ouverte par ${nom}`', nom='Loïc'), '1 h 16')) == \
    etat_commande('2B', 'Loïc', 76)
assert [t for _c, t in TEXTES_RESTO['legendeParties'](demo.DELAI_ORANGE)][2] == _js(
    'texte: `Orange${ESP}: ouverte depuis plus de ${delai}${ESP}min, proposez l\'addition`', delai=demo.DELAI_ORANGE)

# 2. Les gabarits et le comportement que la vidéo montre.
_PAD = _lire(S, 'overrides', 'actionpad_widget.xml')
assert '"J\'encaisse"' in _PAD, "t21 : « J'encaisse » changé"
_CB_XML = _lire(S, 'overrides', 'control_buttons.xml')
assert 't-esc="aiteTextes.addition"' in _CB_XML and 'class="aite-addition-btn"' in _CB_XML
assert '<attribute name="t-if">pos.aitePeut(\'rembourser\')</attribute>' in _CB_XML, 't21 : « Remboursement » changé'
assert 't-esc="aiteTextes.diviser"' in _CB_XML and 'pos.config.iface_splitbill' in _CB_XML
assert 't-if="currentOrder?.table_id or currentOrder?.customer_count"' in _CB_XML, 't21 : bouton des personnes'
assert 't-esc="aiteTextes.creerLaPart"' in _lire(S, 'overrides', 'split_bill_screen.xml')
# « Addition » imprimée : retour au plan verrouillé.
assert ('if (imprime) { // L\'addition est partie à l\'imprimante : retour au plan verrouillé. this.dialog.closeAll(); '
        'this.pos.showScreen("FloorScreen");' in _une_ligne(_lire(S, 'overrides', 'control_buttons.js')))
# « J'encaisse » : la caissière passe ; sinon la fenêtre « Code de la personne qui encaisse », R10 pour un serveur.
_STORE = _une_ligne(_lire(S, 'store', 'pos_store.js'))
assert ('async pay() { if (!this.aiteActif || this.aitePeut("encaisser")) { return super.pay(...arguments); } '
        'const nom = this.cashier?.name; const employe = await this.aiteIdentifier({ titre: TITRES.encaisser, '
        'sousTitre: nom ? TEXTES.neSaitPasEncaisser(nom) : "",' in _STORE), 't21 : pay() changé'
assert 'this.notification.add(MESSAGES.R10, { type: "danger" }); return false;' in _STORE
assert 'const nom = order.table_id?.table_number ?? order.floating_order_name;' in _STORE
# Après le paiement : pas d'écran de ticket ; après une part, retour à la table d'origine.
assert ('onMounted(() => (this.isContinueSplitting() ? this.continueSplitting() : this.orderDone()));'
        in _lire(S, 'overrides', 'receipt_screen.js'))
# La part : origine, heure et « ouverte par » copiés, 0 personne ; l'origine garde les siennes.
_SPLIT = _une_ligne(_lire(S, 'overrides', 'split_bill_screen.js'))
assert 'aite_ouverte_par_id: originalOrder.aite_ouverte_par_id || this.pos.cashier,' in _SPLIT
assert 'newOrder.setCustomerCount(0);' in _SPLIT and 'originalOrder.customer_count += 1;' in _SPLIT


def _source(relatif, nom):
    """Une constante d'un fichier Python du module, lue sans importer Odoo (comme t16)."""
    for noeud in ast.parse(_lire(R, relatif)).body:
        if isinstance(noeud, ast.Assign) and any(getattr(c, 'id', None) == nom for c in noeud.targets):
            return ast.literal_eval(noeud.value)
    raise ValueError('t21 : %s introuvable dans %s' % (nom, relatif))


_DROITS = _source('models/regles.py', 'DROITS')
assert (_DROITS['servir'], _DROITS['encaisser'], _DROITS['table_collegue'], _DROITS['rembourser']) == (
    'serveur', 'caissiere', 'caissiere', 'manager'), 't21 : droits changés'
_CONFIG = _lire(R, 'models', 'pos_config.py')
assert ("'iface_splitbill': True," in _CONFIG and "'iface_printbill': True," in _CONFIG), \
    't21 : partage ou addition non posés par la case'
assert (_source('models/pos_config.py', 'NOM_ESPECES'), _source('models/pos_config.py', 'NOM_MOBILE_MONEY')) == \
    demo.MODES_RESTO
assert 'aite_encaissee_par_id' in _source('models/pos_order.py', 'CHAMPS_SERVEUR'), \
    "t21 : « Encaissée par » écrit par la caisse"
assert _source('models/pos_order.py', 'CHAMPS_FIGES') == ('aite_ouverte_par_id', 'aite_origine_uuid')
_PO_ORDER = _lire(R, 'models', 'pos_order.py')
assert 'string="Encaissée par"' in _PO_ORDER and 'string="Ouverte par"' in _PO_ORDER
assert ("# « Encaissée par » : l'employé de l'addition au paiement." in _PO_ORDER
        and "vals['aite_encaissee_par_id'] = employe.id" in _PO_ORDER)

# 3. Les touches mesurées (résultats, légendes) : notes de version §3.
_NOTES = _lire(RACINE, 'docs', 'NOTES_DE_VERSION_restaurant_lot1.md')
for _ligne in ("| Serveur — imprimer l'addition | 6 | **6** (imprimante de tickets simulée) |",
               '| Caissière — encaisser en espèces, somme exacte | 8 | **8** |',
               "| Caissière — encaisser au poste d'un serveur resté identifié | 7 | **7** |",
               "| Caissière — deux parts d'une addition divisée | 14 + n | **15** (n = 1) ; la caisse revient d'elle-même "
               "à la table, la caissière toujours identifiée |"):
    assert _ligne in _NOTES, ('t21 : mesure changée dans les notes de version', _ligne)

# 4. Odoo : l'écran de division, le paiement, les libellés (traductions françaises).
_SB_JS = _lire(O, 'pos_restaurant', 'static', 'src', 'app', 'split_bill_screen', 'split_bill_screen.js')
assert 'return `${originalOrderName}B`;' in _SB_JS and '`${splitQty} / ${line.get_quantity_str()}`' in _SB_JS
assert '<h4 class="mb-0">Bill Splitting</h4>' in _lire(O, 'pos_restaurant', 'static', 'src', 'app', 'split_bill_screen',
                                                       'split_bill_screen.xml')
assert 'currentOrder.getCustomerCount() > 1' in _lire(O, 'pos_restaurant', 'static', 'src', 'overrides', 'components',
                                                       'payment_screen', 'payment_screen.xml')
assert 'return this.pos.get_open_orders().filter((order) => !order.table_id);' in _lire(
    O, 'point_of_sale', 'static', 'src', 'app', 'navbar', 'navbar.js')
_PO = _lire(O, 'point_of_sale', 'i18n', 'fr.po') + _lire(O, 'pos_restaurant', 'i18n', 'fr.po')
for _id, _msg in (('Bill Splitting', "Partage d'addition"), ('/ Guest', '/ Convive'),
                  ('Please select a payment method', 'Veuillez sélectionner un mode de paiement'),
                  ('Remaining', 'Restant'), ('Validate', 'Valider'), ('Back', 'Retour'), ('Customer', 'Client'),
                  ('Invoice', 'Facture'), ('Actions', 'Actions'), ('Plan', 'Plan'), ('Table', 'Table')):
    assert 'msgid "%s"\nmsgstr "%s"' % (_id, _msg) in _PO, ("t21 : libellé d'Odoo introuvable", _msg)
for _msg in ('Note cuisine', 'Note générale', 'Note au client', 'Rechercher des produits…'):
    assert 'msgstr "%s"' % _msg in _PO, ("t21 : libellé d'Odoo introuvable", _msg)

# ============================================================== les données --
def _employe(poste):
    nom_complet = demo.POSTES_RESTO[poste][0]
    return next(x for x in demo.EQUIPE_RESTO if x[0] == nom_complet)


PRISCA, LOIC, INES = _employe('caisse'), _employe('serveur'), _employe('serveuse')
assert (PRISCA[2], LOIC[2], INES[2]) == ('Caissière', 'Serveur', 'Serveur')
P_PRISCA, CODE_P = PRISCA[1], PRISCA[3]
P_LOIC, CODE_L = LOIC[1], LOIC[3]
P_INES, CODE_I = INES[1], INES[3]
assert (CODE_P, CODE_L, CODE_I) == ('6304', '4827', '5913')
PRIX = {nom: prix for nom, _f, prix, _c, _s in demo.CARTE_RESTO}
MARGHERITA, REINE, QUATRE = 'Pizza Margherita', 'Pizza Reine', 'Pizza quatre fromages'
BLONDE, BRUNE, COLA, EAU = 'Bière blonde 65 cl', 'Bière brune 65 cl', 'Cola 33 cl', 'Eau minérale 50 cl'

# Les additions encaissées (voir l'en-tête), dans l'ordre de leurs lignes.
T4 = [(MARGHERITA, 1), (BLONDE, 2), (COLA, 2), (QUATRE, 1), (EAU, 2)]
T2 = [(COLA, 2), (REINE, 1), (QUATRE, 1)]
PART = [(REINE, 1)]
RESTE = [(COLA, 2), (QUATRE, 1)]
T10 = [(REINE, 1), (BLONDE, 2), (COLA, 1), (QUATRE, 1), (BRUNE, 2)]


def total(lignes):
    return sum(PRIX[n] * q for n, q in lignes)


assert (total(T4), total(T2), total(PART), total(RESTE), total(T10)) == (18000, 15000, 6000, 9000, 20000)
assert (sum(q for _n, q in T4), sum(q for _n, q in T10)) == (8, 7)

# La journée commune : ce que t17 à t20 ont fixé de ces tables (demo.TABLES_JOUR_RESTO) est relu ici.
_JOUR = {}
for _t, _qui, _heure, _pers, _contenu, _suite, _tutos in demo.TABLES_JOUR_RESTO:
    _JOUR.setdefault(_t, []).append((_qui, _heure, _pers, _contenu, _suite))
# (relecture) contenus lus comme un minimum : la journée commune peut recevoir les ajouts que t21 pose (compte rendu)
assert len(_JOUR[4]) == 1 and _JOUR[4][0][:3] == (P_LOIC, '12:15', 6)
assert all(_JOUR[4][0][3].get(n, 0) >= q for n, q in {MARGHERITA: 1, BLONDE: 2, COLA: 2}.items())
assert 'encore ouverte à 13:48' in _JOUR[4][0][4]
assert all(dict(T4).get(n, 0) >= q for n, q in _JOUR[4][0][3].items())
assert _JOUR[2][0][:2] == (P_LOIC, '12:55') and _JOUR[2][0][2] in (None, 2) and _JOUR[2][0][3].get(COLA) == 2
assert all(dict(T2).get(n, 0) >= q for n, q in _JOUR[2][0][3].items())
assert 'encore ouverte à 13:48' in _JOUR[2][0][4]
assert [x[:2] for x in _JOUR[5]] == [(P_INES, '13:05')]
assert _JOUR[10][-1][:4] == (P_INES, '19:10', 4, dict(T10)) and 't21' in _JOUR[10][-1][4]
assert _JOUR[9][0][4].endswith('annulés en entier à 13:48 par Landry')
PERSONNES = {4: _JOUR[4][0][2], 2: 2, 10: _JOUR[10][-1][2]}     # table 2 : 2 personnes (t18, resto_commande(…, 2, …))

# Les heures (voir l'en-tête) et ce que la caisse en affiche (S/utils/alerte.js:18-27 ; messages.js:165-171).
OUVERTURE = {2: '12:55', 4: '12:15', 5: '13:05', 10: '19:10'}
INSTANT = {1: '13:50', 2: '13:52', 3: '14:10', 4: '14:11', 5: '19:55'}


def _min(hm):
    h, m = hm.split(':')
    return int(h) * 60 + int(m)


def minutes(table, etape):
    return _min(INSTANT[etape]) - _min(OUVERTURE[table])


def couleur(table, etape):
    return 'orange' if minutes(table, etape) >= demo.DELAI_ORANGE else 'vert'


DUREES = {(n, k): (couleur(n, k), duree_resto(minutes(n, k))) for n in (2, 4, 5) for k in (1, 2, 3)}
assert DUREES[(4, 1)] == ('orange', '1 h 35') and DUREES[(2, 1)] == ('vert', '55 min') and DUREES[(5, 1)] == \
    ('vert', '45 min')
assert DUREES[(4, 2)] == ('orange', '1 h 37') and DUREES[(2, 2)] == ('vert', '57 min') and DUREES[(5, 2)] == \
    ('vert', '47 min')
assert DUREES[(2, 3)] == ('orange', '1 h 15') and duree_resto(minutes(2, 4)) == '1 h 16'
assert duree_resto(minutes(10, 5)) == '45 min' and couleur(10, 5) == 'vert'
assert all(d != '1 h 00' for _c, d in DUREES.values()), 'une table à « 1 h 00 » (ECARTS.md n° 82)'

# ================================================================ l'écran --
POS = 't21-pos'
PLAN_ID = 't21-plan'
PLAN = resto_plan(PLAN_ID, resto_salle(PLAN_ID, {n: (DUREES[(n, 1)][0], DUREES[(n, 1)][1], None) for n in (2, 4, 5)}),
                  delai=demo.DELAI_ORANGE, salle=demo.SALLE_RESTO, initiale=True)
# La partie orange de la légende, à désigner (pas d'identifiant par partie dans resto_plan : demande au socle).
_ORANGE = '<span class="rs-leg-p"><i class="rs-leg-orange"></i>'
assert PLAN.count(_ORANGE) == 1
PLAN = PLAN.replace(_ORANGE, '<span class="rs-leg-p" id="t21-leg-orange"><i class="rs-leg-orange"></i>')
T = {n: '#%s-t%d' % (PLAN_ID, n) for n in (2, 4, 5, 10)}

FAMILLE_BIERE = ('Boisson', 'Alcoolisé', 'Bière')


def lignes_html(ident, lignes):
    return ''.join(resto_ligne('%s-l%d' % (ident, k), n, q, PRIX[n]) for k, (n, q) in enumerate(lignes, 1))


def commande(ident, table, nom, mins, lignes, personnes):
    """L'écran de commande d'une table rouverte (aucune ligne choisie : pas de pavé, « Note cuisine » grisé) ; tout est
    parti : « J'envoie » gris, « J'encaisse » primaire ; la famille Bière choisie sur le poste, la quantité de
    l'addition sur les tuiles."""
    qtes = {cle_resto(n): q for n, q in lignes if n in (BLONDE, BRUNE)}
    html = resto_commande(ident, etat_commande(table, nom, mins), lignes_html(ident, lignes), fcfa(total(lignes)),
                          personnes, resto_familles(ident + '-fa', demo.FAMILLES_RESTO, FAMILLE_BIERE),
                          resto_tuiles(ident + '-tu', resto_produits('Bière'), qtes), encaisser=True, sans_ligne=True)
    if not personnes:
        # la part : ni table ni personne, pas de bouton des personnes (S/overrides/control_buttons.xml:18)
        _p = '<span class="" id="%s-pers">%s</span>' % (ident, e(TEXTES_RESTO['personnes'](0)))
        assert _p in html
        html = html.replace(_p, '', 1)
    return html


def paiement(ident, du, personnes, mode='Espèces'):
    html = resto_paiement(ident, du, convives=personnes, ligne_mode=mode)
    if personnes > 1:
        assert html.count('<div class="rs-convive">') == 1
        html = html.replace('<div class="rs-convive">', '<div class="rs-convive" id="%s-conv">' % ident, 1)
    return html


C4 = commande('t21-c4', 4, P_LOIC, minutes(4, 1), T4, PERSONNES[4])
P4 = paiement('t21-p4', total(T4), PERSONNES[4])
assert '3 000 FCFA / Convive' in P4.replace('\u00a0', ' ').replace('\u202f', ' ')
C2 = commande('t21-c2', 2, P_LOIC, minutes(2, 3), T2, PERSONNES[2])
C2B = commande('t21-c2b', '2B', P_LOIC, minutes(2, 4), PART, 0)
P2B = paiement('t21-p2b', total(PART), 0, mode=demo.MODES_RESTO[1])
C2R = commande('t21-c2r', 2, P_LOIC, minutes(2, 4), RESTE, PERSONNES[2])
P2 = paiement('t21-p2', total(RESTE), PERSONNES[2])
C10 = commande('t21-c10', 10, P_INES, minutes(10, 5), T10, PERSONNES[10])
P10 = paiement('t21-p10', total(T10), PERSONNES[10])

# L'écran « Partage d'addition » (O/pos_restaurant/static/src/app/split_bill_screen/split_bill_screen.xml:4-40), composé
# ici (aucune capture) : l'en-tête et son bouton de retour, les lignes à gauche, le montant de la part et « Créer
# l'addition à part » à droite.
CHEVRON = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" '
           'stroke-linejoin="round"><path d="M15 5l-7 7 7 7"/></svg>')
PARTAGE = ('<div class="vue rs-vue" id="t21-sp"><div class="t21-sp"><div class="t21-sp-h"><span class="t21-sp-ret" '
           'id="t21-sp-ret">%s</span><span class="t21-sp-titre">%s</span></div><div class="t21-sp-m">'
           '<div class="t21-sp-g"><div class="rs-lignes">%s</div></div><div class="t21-sp-d"><div class="t21-sp-info" '
           'id="t21-sp-info"><span id="t21-sp-v">%s</span></div><div class="t21-sp-bt" id="t21-sp-creer">%s</div>'
           '</div></div></div></div>'
           % (CHEVRON, e("Partage d'addition"), lignes_html('t21-sp', T2), e(fcfa(0)), e(TEXTES_RESTO['creerLaPart'])))
SP_REINE = '#t21-sp-l%d' % (1 + [n for n, _q in T2].index(REINE))

# Les fenêtres posées sur la caisse : le code à la table (205 px, sous la phrase du plan), le code de la personne qui
# encaisse (128 px, sous la phrase d'état de l'écran de commande : la fenêtre, plus haute avec son sous-titre,
# finit au-dessus du bas de la caisse), « Actions ».
CODE4L = resto_code('t21-k4l', TITRES_RESTO['table'](4))
CODE4P = resto_code('t21-k4p', TITRES_RESTO['table'](4))
CODE2 = resto_code('t21-k2', TITRES_RESTO['table'](2))
ENC = resto_code('t21-enc', TITRES_RESTO['encaisser'], sous_titre=TEXTES_RESTO['neSaitPasEncaisser'](P_INES), haut=128)
ACT = resto_actions('t21-act')

# La case de l'employé est mesurée au chargement : posée d'office au nom le plus long (Prisca), puis cachée.
CAISSE = fenetre_resto(POS, [PLAN, C4, P4, C2, PARTAGE, C2B, P2B, C2R, P2, C10, P10],
                       calques=CODE4L + CODE4P + CODE2 + ENC + ACT, ecran='plan', employe=(P_PRISCA, P_PRISCA[0]),
                       avatar=demo.AVATARS_RESTO[P_PRISCA])
assert max(len(P_PRISCA), len(P_LOIC), len(P_INES)) == len(P_PRISCA)
CAISSE = CAISSE.replace('class="app pos resto sur-plan avec-emp"', 'class="app pos resto sur-plan"', 1)
# L'onglet de la part, tant qu'elle est ouverte (O/point_of_sale/…/navbar/navbar.xml:7 ; order_tabs.xml).
_SEP = '<i class="rs-sep"></i>'
assert CAISSE.count(_SEP) == 1
CAISSE = CAISSE.replace(_SEP, _SEP + '<span class="t21-tab" id="%s-tab">2B</span>' % POS, 1)
ECRAN = navigateur(CAISSE)

CSS = ("/* -- la pastille : Loïc à l'étape 1, Inès au début de l'étape 5, Prisca sinon -- */\n"
       + css_personnage('#tu-perso.t21-loic', demo.POSTES_RESTO['serveur'][0], demo.POSTES_RESTO['serveur'][1],
                        P_LOIC[0])
       + css_personnage('#tu-perso.t21-ines', demo.POSTES_RESTO['serveuse'][0], demo.POSTES_RESTO['serveuse'][1],
                        P_INES[0]) + """
/* -- l'avatar en haut de la caisse : Prisca (posé par fenetre_resto), Loïc, Inès -- */
.resto.t21-loic .rs-emp .avatar { background: %s !important; }
.resto.t21-ines .rs-emp .avatar { background: %s !important; }
/* -- l'onglet de la part « 2B » (btn-lg btn-secondary active), tant qu'elle est ouverte -- */
.resto .t21-tab { height: 52px; min-width: 86px; padding: 0 20px; border-radius: 4px; display: inline-flex;
  align-items: center; justify-content: center; background: #C6CBD0; color: #212529; visibility: hidden; }
.resto.t21-part .t21-tab { visibility: inherit; }
/* -- l'écran « Partage d'addition » (split_bill_screen.xml : bg-200, en-tête bg-view, deux colonnes p-2 gap-2) -- */
#t21-sp .t21-sp { position: absolute; inset: 0; display: flex; flex-direction: column; background: #E9ECEF; }
#t21-sp .t21-sp-h { flex: none; height: 80px; display: flex; align-items: center; padding: 0 11px; background: #fff;
  border-bottom: 1px solid #DEE2E6; }
#t21-sp .t21-sp-ret { flex: none; width: 66px; height: 58px; border-radius: 6px; background: #DEE2E6; color: #212529;
  display: flex; align-items: center; justify-content: center; }
#t21-sp .t21-sp-ret svg { width: 26px; height: 26px; }
#t21-sp .t21-sp-titre { flex: 1; padding-right: 66px; text-align: center; font-size: 30px; font-weight: 500; color: #212529; }
#t21-sp .t21-sp-m { flex: 1; min-height: 0; display: grid; grid-template-columns: 1fr 1fr; gap: 11px; padding: 11px; }
#t21-sp .t21-sp-g { min-height: 0; background: #fff; border-radius: 11px; overflow: hidden; padding-top: 6px; }
#t21-sp .t21-sp-info { height: 128px; margin-bottom: 11px; background: #fff; border-radius: 11px; display: flex;
  align-items: center; justify-content: center; font-size: 51px; color: #1E7B34; }
#t21-sp .t21-sp-bt { height: 168px; border-radius: 6px; background: var(--muk-prim); color: #fff; font-size: 27px;
  display: flex; align-items: center; justify-content: center; }
""" % (demo.AVATARS_RESTO[P_LOIC], demo.AVATARS_RESTO[P_INES]))


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


def taper(fen, chiffres, d=0.25):
    """Un code tapé dans la fenêtre ``fen`` : les points se remplissent, le chiffre ne s'affiche jamais. Le doigt
    passe d'un chiffre à l'autre sans attendre (``puis`` = 0)."""
    gestes = []
    for k, c in enumerate(chiffres):
        g = touche('#%s-k%s' % (fen, c), classe('#%s-p%d' % (fen, k), ajouter=['plein']), d=d)
        g[0] = dict(g[0], puis=0.0)
        gestes += g
    return gestes


PERSONNE_CLS = {P_LOIC: ['t21-loic'], P_INES: ['t21-ines'], P_PRISCA: []}


def employe(nom):
    """Le prénom et l'avatar en haut de la caisse."""
    autres = [c for n, cls in PERSONNE_CLS.items() if n != nom for c in cls]
    return [texte('#%s-emp-n' % POS, nom), texte('#%s-emp-av' % POS, nom[0]),
            classe('#' + POS, ajouter=PERSONNE_CLS[nom], retirer=autres)]


def vers_commande(vue_, onglet, nom=None):
    g = [vue(vue_, 'pos'), classe('#' + POS, ajouter=['sur-commande', 'avec-emp'], retirer=['sur-plan', 'sur-paiement']),
         texte('#%s-onglet' % POS, str(onglet))]
    return g + (employe(nom) if nom else [])


def vers_paiement(vue_):
    """L'écran de paiement, ou de division : ni recherche ni code-barres (showSearchButton, O/point_of_sale/static/src/
    app/store/pos_store.js:2279-2284 ; navbar.xml:23), l'onglet en primaire."""
    return [vue(vue_, 'pos'), classe('#' + POS, ajouter=['sur-paiement'], retirer=['sur-commande', 'sur-plan'])]


def vers_plan():
    """Retour au plan verrouillé : plus personne d'identifié (S/store/pos_store.js:448-455)."""
    return [vue(PLAN_ID, 'pos'), classe('#' + POS, ajouter=['sur-plan'], retirer=['sur-commande', 'sur-paiement',
                                                                                  'avec-emp', 't21-part']),
            texte('#%s-onglet' % POS, 'Table')]


def mode(ident, cle_):
    """Un mode touché : il s'éclaire, la ligne du restant dû s'ajoute, « Restant 0 FCFA », « Valider » s'allume
    (O/point_of_sale/…/payment_screen/payment_status/payment_status.xml:4-24 ; payment_screen.xml:69-77)."""
    return touche('#%s-%s' % (ident, cle_), classe('#%s-%s' % (ident, cle_), ajouter=['actif']),
                  cacher('#%s-msg' % ident, d=0.05), montrer('#%s-ok' % ident, d=0.1, y=0),
                  montrer('#%s-pl' % ident, d=0.15, y=0), classe('#%s-valider' % ident, retirer=['off']), d=0.5)


def table_libre(n):
    return [classe(T[n], ajouter=['libre'], retirer=['vert', 'orange', 'avec-duree']), texte(T[n] + '-d', '')]


def table_etat(n, etape):
    c, d = DUREES[(n, etape)]
    autre = 'vert' if c == 'orange' else 'orange'
    return [classe(T[n], ajouter=[c], retirer=[autre]), texte(T[n] + '-d', d)]


def ensemble(gestes):
    return [dict(g, avec=True) for g in gestes]


ETAPES = [
    # 1. Loïc imprime l'addition de la table 4, orange : la table, son code, « Addition » (6 touches : N §3 l.251).
    {'temps': 0, 'titre': "L'addition, par le serveur",
     'texte': "La table, son code, « Addition » : 6 touches. L'addition part à l'imprimante, et le plan revient.",
     # « Addition » dit quand le doigt y arrive (relecture : il était dit 2,3 s avant le toucher, pendant le code) ;
     # « son nom paraît en haut » : l'écran de la table s'ouvre au nom de Loïc (S/overrides/navbar.xml:18-20)
     'voix': "La table quatre est orange : il est temps de proposer l'addition. Loïc touche sa table et tape son "
             "code : son nom paraît en haut. Puis Addition : elle part à l'imprimante, et le plan revient, verrouillé. "
             "Encaisser, ce n'est pas son geste : c'est celui de la caissière.",
     'gestes': [classe('#tu-perso', ajouter=['t21-loic']), pause(0.3), anneau(T[4], d=1.1),
                anneau('#t21-leg-orange', d=1.4)]
               + touche(T[4], ouvrir('t21-k4l'), d=0.6, fy=0.3)
               + [pause(0.1)] + taper('t21-k4l', CODE_L)
               + [fermer('t21-k4l')] + ensemble(vers_commande('t21-c4', 4, P_LOIC))
               + touche('#t21-c4-addition', *vers_plan(), d=0.5)
               # le doigt quitte la place d'« Addition » (sur le plan : la table 9) pour la table 4 ; la bulle avec
               # « Encaisser, ce n'est pas son geste »
               + [pause(0.2), curseur(T[4], fx=0.8, fy=0.85, d=0.5), pause(1.2),
                  bulle('b-serveur', T[4], cote='droite', d=3.0), pause(2.6)]},
    # 2. Prisca encaisse la table 4 : la table, son code, « J'encaisse », « Espèces », « Valider » (8 touches).
    {'temps': 1, 'titre': 'La caissière encaisse : 8 touches',
     'texte': "La table, son code, « J'encaisse », « Espèces », « Valider ». La table reste « ouverte par Loïc ».",
     'voix': "Deux minutes plus tard, Prisca, la caissière, touche la table quatre et tape son code. La table reste "
             "ouverte par Loïc. J'encaisse : dix-huit mille francs CFA, trois mille par personne. Espèces. À la "
             "validation, Odoo note qui a encaissé : Prisca. Valider : huit touches. Pas d'écran de ticket : le plan "
             "revient aussitôt, et la table quatre est libre.",
     'gestes': [classe('#tu-perso', retirer=['t21-loic'])] + ensemble(table_etat(2, 2) + table_etat(4, 2)
                                                                      + table_etat(5, 2))
               + [pause(0.3)]
               + touche(T[4], ouvrir('t21-k4p'), d=0.6, fy=0.3)
               + [pause(0.1)] + taper('t21-k4p', CODE_P)
               + [pause(0.1), fermer('t21-k4p'), texte('#t21-c4-etat', etat_commande(4, P_LOIC, minutes(4, 2)),
                                                       avec=True)]
               + ensemble(vers_commande('t21-c4', 4, P_PRISCA))
               + [pause(0.1), anneau('#t21-c4-etat', d=0.9)]
               # le doigt quitte aussitôt la place de « J'encaisse », où paraît « Valider » (pâle tant que rien n'est payé)
               + touche('#t21-c4-encaisser', *vers_paiement('t21-p4'),
                        curseur('#t21-p4-conv', fx=0.85, fy=0.9, d=0.6, decale=0.3), d=0.6)
               + [pause(0.1), anneau('#t21-p4-conv', d=1.1)]
               + mode('t21-p4', 'esp')
               # « Valider » touché quand la voix le dit (relecture : 1,1 à 1,5 s après)
               + [pause(0.1), bulle('b-encaissee', '#t21-p4-pl', cote='bas', d=2.8), pause(1.6)]
               + touche('#t21-p4-valider', *vers_plan(), *table_libre(4), d=0.5)
               + [pause(0.2), curseur(T[4], fx=0.8, fy=0.85, d=0.5), anneau(T[4], d=1.0, avec=True, decale=0.3),
                  pause(0.2)]},
    # 3. Plus tard, la table 2 : la table, son code, « Actions », « Diviser l'addition », la Pizza Reine, « Créer
    #    l'addition à part » (9 des 15 touches : 1 + 4 + 4 ; parcours_tour.js:431-442).
    {'temps': 2, 'titre': "Diviser l'addition",
     'texte': "« Actions », « Diviser l'addition », on touche ce qui part à part, puis « Créer l'addition à part » : "
              "la part 2B.",
     'voix': "Plus tard, à la table deux, deux amis paient chacun leur part. Prisca tape son code et touche Actions. "
             "Pas de remboursement dans la liste : il est réservé au manager. Diviser l'addition : elle touche la "
             "pizza reine, puis crée l'addition à part. Voici la part deux B, ouverte par Loïc, elle aussi.",
     'gestes': ensemble(table_etat(2, 3) + table_libre(5)) + [pause(0.3)]
               + touche(T[2], ouvrir('t21-k2'), d=0.6, fy=0.3)
               + [pause(0.1)] + taper('t21-k2', CODE_P)
               + [fermer('t21-k2')] + ensemble(vers_commande('t21-c2', 2, P_PRISCA))
               + [pause(0.1)]
               + touche('#t21-c2-actions', ouvrir('t21-act'), d=0.6)
               + [pause(1.6)]
               + touche('#t21-act-diviser', fermer('t21-act'), *vers_paiement('t21-sp'), d=0.6)
               + [pause(0.3)]
               + touche(SP_REINE, classe(SP_REINE, ajouter=['choisie']), texte(SP_REINE + '-q', '1 / 1,00'),
                        texte('#t21-sp-v', fcfa(total(PART))), d=0.6)
               # l'anneau entoure la case du montant (mesurée au chargement, quand elle dit encore « 0 FCFA »)
               + [anneau('#t21-sp-info', d=0.8)]
               + touche('#t21-sp-creer', *vers_commande('t21-c2b', '2B'), classe('#' + POS, ajouter=['t21-part']),
                        d=0.6)
               + [pause(0.3), anneau('#t21-c2b-etat', d=1.3)]},
    # 4. La part en Mobile Money, puis la table 2 en espèces ; la caisse revient seule à la table (15 touches en tout).
    {'temps': 2, 'titre': 'Une part, puis l\'autre',
     'texte': '2B en Mobile Money, puis la table 2 en espèces : la caisse revient seule à la table. 15 touches en tout.',
     'voix': "J'encaisse la part : Mobile Moni, valider. La caisse revient d'elle-même à la table deux, Prisca toujours "
             "identifiée, et les deux personnes y restent. La seconde part, en espèces : quinze touches pour les deux, "
             "puis le plan revient, et la table est libre.",
     # « Mobile Moni » : pour la voix seulement (comme « Orange Moni », README)
     'gestes': [pause(0.1)] + touche('#t21-c2b-encaisser', *vers_paiement('t21-p2b'), d=0.6)
               + [pause(0.1)] + mode('t21-p2b', 'mm')
               + [pause(0.05)]
               + touche('#t21-p2b-valider', *vers_commande('t21-c2r', 2), classe('#' + POS, retirer=['t21-part']), d=0.5)
               # Prisca toujours identifiée (son nom en haut), puis « 2 personnes » : les deux personnes restent sur la
               # table ; le curseur quitte « J'encaisse » (relecture : la bulle était ancrée sur une ligne, l'anneau
               # en avance d'une phrase)
               + [pause(0.8), curseur('#%s-emp' % POS, fx=0.3, fy=0.9, d=0.5),
                  anneau('#%s-emp' % POS, d=1.0, avec=True, decale=0.3),
                  curseur('#t21-c2r-pers', fx=0.7, fy=0.85, d=0.5),
                  anneau('#t21-c2r-pers', d=1.1, avec=True, decale=0.3),
                  bulle('b-part', '#t21-c2r-l2', cote='bas', d=1.8, avec=True, decale=0.3), pause(0.3)]
               + touche('#t21-c2r-encaisser', *vers_paiement('t21-p2'), d=0.6)
               + [pause(0.1)] + mode('t21-p2', 'esp')
               + [pause(0.05)] + touche('#t21-p2-valider', *vers_plan(), *table_libre(2), d=0.5)
               + [pause(0.2), curseur(T[2], fx=0.8, fy=0.85, d=0.5), anneau(T[2], d=1.0, avec=True, decale=0.3)]},
    # 5. Le soir, au poste d'Inès restée identifiée : « J'encaisse », le code de Prisca, « Espèces », « Valider »
    #    (7 touches : N §3 l.259).
    {'temps': 3, 'titre': "Au poste d'une serveuse",
     'texte': "« J'encaisse » au nom d'Inès : « Code de la personne qui encaisse ». Prisca tape le sien : 7 touches.",
     'voix': "Le soir, à la table dix, Inès touche elle-même J'encaisse. La caisse demande le code de la personne qui "
             "encaisse : un code de serveur y est refusé. Prisca tape le sien, sur ce poste : le paiement s'ouvre à son "
             "nom. Espèces, valider : sept touches, et l'addition est encaissée par Prisca, pas par Inès.",
     'gestes': [classe('#tu-perso', ajouter=['t21-ines'])] + ensemble(vers_commande('t21-c10', 10, P_INES))
               + [pause(0.5), anneau('#t21-c10-etat', d=1.0)]
               + touche('#t21-c10-encaisser', ouvrir('t21-enc'), d=0.6)
               + [pause(0.3), anneau('#t21-enc-st', d=1.3),
                  bulle('b-r10', '#t21-enc', cote='droite', d=3.2), pause(2.1)]
               + [classe('#tu-perso', retirer=['t21-ines'])] + taper('t21-enc', CODE_P)
               # le code reconnu : Prisca devient la personne du poste, et le paiement s'ouvre (pos_store.js:793-807)
               + [pause(0.1), fermer('t21-enc')]
               + ensemble(vers_paiement('t21-p10') + employe(P_PRISCA)
                          + [curseur('#%s-emp' % POS, fx=0.3, fy=0.9, d=0.5)])
               + [anneau('#%s-emp' % POS, d=0.8, avec=True, decale=0.4)]
               + mode('t21-p10', 'esp')
               + [pause(0.05)] + touche('#t21-p10-valider', *vers_plan(), curseur(T[10], fx=0.8, fy=0.85, d=0.6),
                                       d=0.5)
               + [pause(0.3), reaction('r-nom', d=2.6), pause(0.5)]},
]

TUTORIEL = {
    'slug': 't21-restaurant-encaisser',
    'profil': 't21_restaurant_encaisser',
    'numero': 21,
    'titre': 'Encaisser une table',
    'fonction': 'Encaissement réservé',
    'personnage': demo.POSTES_RESTO['caisse'],
    'accroche': {
        'kicker': 'À la caisse',
        # Les douleurs : P l.194 (« le bouton de paiement n'est lié à aucun rôle ») ; l.154 (un seul nom par addition,
        # réécrit à la validation du paiement au nom de l'employé alors connecté, C6, C7 : le nom de la serveuse
        # disparaît, ou l'encaissement est enregistré à son nom si le restaurateur ne s'identifie pas ; le retour au
        # plan laisse l'employé connecté, C4) ; l.364 (la division fait passer une personne à la nouvelle addition,
        # C19, C33).
        'question': 'Qui a *encaissé* la table 4 ?',
        'douleurs': [('pieces', 'Le bouton de paiement ouvert à tous'),
                     ('personne', 'Le paiement au nom du dernier connecté'),
                     ('interrogation', 'Qui a ouvert la table ? Effacé au paiement'),
                     ('echange', 'Diviser : une personne passe sur la part'),
                     ('cadenas', 'Après le paiement, le poste reste ouvert')],
        'voix': "Qui a encaissé la table quatre ? Quand le bouton de paiement est ouvert à tous, n'importe qui encaisse, "
                "et le dernier connecté signe le paiement.",
    },
    'revelation': {
        # « J'encaisse » réservé : regles.DROITS['encaisser'] = 'caissiere' (R/models/regles.py:37) ; le code :
        # pos_store.js:784-807 ; les deux noms : R/models/pos_order.py:11-18, 240-245.
        'promesse': "« J'encaisse » est réservé à la caissière et au-dessus : son code suffit, et l'addition garde qui "
                    "l'a ouverte et qui l'a encaissée.",
        'voix': "Avec Aïte haousse, on encaisse avec son propre code, et chaque addition garde ses deux noms.",
    },
    'temps': ['Addition', 'Encaisser', 'Diviser', 'Chez un serveur'],
    'app': POS,
    'ecran': ECRAN,
    'css': CSS,
    'vues_initiales': {'pos': PLAN_ID},
    'bulles': {
        # « au-dessus » : un gluon (U+2060) après le trait d'union : « dessus » ne passe pas seul à la ligne
        'b-serveur': "Imprimer l'addition, oui ; encaisser, non : c'est la caissière et au-\u2060dessus.",
        'b-encaissee': '« Encaissée par » : Odoo note la personne qui valide le paiement, ici %s.' % P_PRISCA,
        'b-part': 'Les personnes restent sur la table 2 : la part 2B en compte 0.',
        'b-r10': 'Un code de serveur ici : « %s »' % MESSAGES_RESTO['R10'],
    },
    'reactions': {
        'r-nom': "Ce que j'encaisse est à mon nom.",
    },
    'etapes': ETAPES,
    'resultats': {
        'titre': 'Encaisser, touche par touche',
        'cartes': [
            {'valeur': '8', 'compter': 8, 'unite': 'touches', 'icone': 'billets',
             'texte': "pour encaisser une table en espèces : la table, le code, « J'encaisse », « Espèces », "
                      "« Valider »"},
            {'valeur': '7', 'compter': 7, 'unite': 'touches', 'icone': 'cle',
             'texte': "au poste d'un serveur resté identifié : « J'encaisse », le code de la caissière, le mode, "
                      "« Valider »"},
            {'valeur': '15', 'compter': 15, 'unite': 'touches', 'icone': 'echange',
             'texte': "pour deux parts d'une addition divisée, sans retaper de code"},
        ],
        'voix': "Huit touches pour encaisser une table, sept au poste d'un serveur, quinze pour deux parts.",
    },
    'cta': {
        'appel': 'Demandez votre démonstration',
        'sous_marque': demo.SOUS_MARQUE_RESTO,
        'suivant': 'Fermer la caisse',
        'voix': "Aïte haousse, par Aïte Consulting. Demandez votre démonstration. Prochain tutoriel : fermer la caisse.",
    },
    # l'écran de paiement de la table 4 juste après « Espèces » : « 18 000 FCFA », « 3 000 FCFA / Convive »,
    # « Restant 0 FCFA », « Valider » allumé, avant la bulle (C/13)
    'vignette': {'etape': 2, 'apres': 10.85},
}


for _etape in ETAPES:
    _etape['titre'], _etape['texte'] = typo_resto(_etape['titre']), typo_resto(_etape['texte'])
for _groupe in ('bulles', 'reactions'):
    TUTORIEL[_groupe] = {_k: typo_resto(_v) for _k, _v in TUTORIEL[_groupe].items()}
for _carte in TUTORIEL['resultats']['cartes']:
    _carte['texte'] = typo_resto(_carte['texte'])
TUTORIEL['revelation']['promesse'] = typo_resto(TUTORIEL['revelation']['promesse'])
TUTORIEL['accroche']['douleurs'] = [(_i, typo_resto(_t)) for _i, _t in TUTORIEL['accroche']['douleurs']]
