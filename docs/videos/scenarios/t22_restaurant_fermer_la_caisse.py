# -*- coding: utf-8 -*-
"""Tutoriel 22 — Fermer la caisse.

Le septième des huit tutoriels du restaurant (lot 1 : aite_pos_restaurant ;
restaurant SANS hôtel, comme t16 : demo.RESTO, demo.SOCIETE_RESTO). Le soir du
jour de référence de la série (14/10/2026), Landry, le chef de salle
(demo.POSTES_RESTO['chef'], code 7461), ferme la caisse ; le lendemain matin,
Prisca, la caissière (code 6304), la rouvre ; dans la gestion, Edwige, la
manager, lit le rapport de la session. La pastille du haut change de personne
par une classe (ecrans.css_personnage, comme t16 à t19). Storyboard : scratchpad
videos_resto/storyboards/t22.md (adapté : voir « Écarts au storyboard »).

Abréviations : R/ = addons/aite_pos_restaurant/ ; S/ = R/static/src/ ;
O/ = ../odoo18/addons/ ; N = docs/NOTES_DE_VERSION_restaurant_lot1.md ;
rec = recette/cas_de_test.py. Les phrases de la caisse et du rapport sont
relues dans le code au chargement (garde-fous plus bas) : une phrase changée
dans le module fait échouer la construction de la vidéo au lieu de la rendre
fausse.

Le monde rejoué (conditions) :
- la caisse « Restaurant », salle « Salle », douze tables, modes « Espèces » et
  « Mobile Money » (Mobile Money sur un journal de banque : R/models/
  pos_config.py:267-290), société sans taxe, une imprimante de tickets et pas
  d'imprimante de préparation (DESIGN.md, « Le restaurant ») ; la session du
  14/10 s'appelle POS/00014 (une session par jour depuis le 01/10 : donnée de
  démonstration, analyse/PLAN_ECRANS.md §5) ;
- la journée : JOURNEE ci-dessous, construite sur demo.TABLES_JOUR_RESTO (les
  tables de t17 à t20 gardent qui, quand et quoi) et sur les agrégats du
  storyboard (12 additions, 188 500 FCFA, 11 tables, 33 personnes), que
  t23 reprend ; ce qui n'était fixé nulle part est proposé ici et signalé
  (« Demandes au socle » du compte rendu) ; aucune heure n'est à l'écran ;
- le fond du matin : 25 000 FCFA (demo.FOND_RESTO, t17) ;
- à 22:30, deux tables encore ouvertes, clients partis : la 11 (Loïc, ouverte à
  21:40, « 50 min », verte), deux Bière blonde 65 cl envoyées ; la 12 (Inès,
  21:15, « 1 h 15 », orange), une Pizza Margherita et un Cola 33 cl envoyés ;
  personne n'est identifié sur le poste (le plan est l'écran de repos) ;
- le journal des annulations du jour : demo.ANNULATIONS_JOUR_RESTO (t19), puis
  les trois produits des tables 11 et 12, annulés à la fermeture.

Écrans et libellés (modèles visuels : captures/restaurant/01, 02, 03, 14, 15,
16, 26 ; aucune capture du menu ≡ en mode restaurant, de la fenêtre des
mouvements d'espèces ni de la fermeture avec Mobile Money : écarts) :

1. Plan verrouillé (resto_plan) ; menu ≡ : « Commandes » et sa pastille (les
   additions ouvertes du poste : O/point_of_sale/static/src/app/navbar/
   navbar.xml:47-49, navbar.js:71-73, O/point_of_sale/static/src/app/store/
   pos_store.js:1502-1504), « Entrée ou sortie d'espèces » (S/overrides/
   navbar.xml:39-43), « Imprimer le rapport » (avec une imprimante :
   navbar.xml:60-62), « Fermer la caisse » (navbar.xml:66-68, gardé en mode :
   S/overrides/navbar.xml:27-29) ; fr.po d'Odoo : « Commandes », « Imprimer le
   rapport », « Fermer la caisse ». Le code est demandé si personne n'est
   identifié, puis vérifié par le serveur (S/store/pos_store.js:739-771 ;
   R/models/pos_session.py:230-257) : « Votre code pour fermer la caisse »
   (S/utils/messages.js:76) ; la personne reconnue devient l'employé du poste
   (pos_store.js:169-188), son nom paraît en haut (S/overrides/navbar.xml:18-20 ;
   capture 14).
2. « Fermeture de la caisse » (O/point_of_sale/…/closing_popup/closing_popup.xml
   et le bloc de pos_hr, O/pos_hr/static/src/overrides/components/closing_popup/
   closing_popup.xml:9-44 ; textes d'AITE : S/overrides/closing_popup.xml:12-37,
   messages.js:140-146) : « 12 commandes : 188 500 FCFA », Espèces (Ouverture,
   ▸ Paiements, ▸ Entrées et sorties d'espèces, Compté, Différence), Mobile
   Money (▸ Paiements, Différence), « Comptage de caisse » (« 0 » d'office :
   closing_popup.js:66-72 ; le champ sélectionne tout au toucher :
   O/point_of_sale/static/src/app/generic_components/inputs/input/input.xml:15),
   « Mobile Money Nombre » prérempli (closing_popup.js:73-79, :71-77 du
   gabarit), « Note de clôture », puis « Fermer la caisse », « Ignorer »,
   « Entrée ou sortie d'espèces », « Ventes du jour ⤓ » et, avec une
   imprimante, le bouton d'impression (closing_popup.xml:109-111, absent du
   composant du socle : ajouté ici). « Entrée ou sortie d'espèces » depuis la
   fenêtre : la fenêtre des mouvements d'espèces d'Odoo s'ouvre par-dessus
   (Odoo closing_popup.js:61-65 ; O/point_of_sale/static/src/app/navbar/
   cash_move_popup/cash_move_popup.xml:4-39, sans en-tête) : « Cash entrant »,
   « Cash sortant » (rouge, choisi d'office : cash_move_popup.js:26-28),
   montant et « FCFA » à droite (la devise après le montant), « Motif »
   (étiquette flottante ; le texte indicatif est transparent), « Confirmer »
   (grisé tant que montant et motif manquent : :28-30, :95-97), « Ignorer » ;
   puis toutes les fenêtres se ferment et la fermeture se rouvre (closing_popup.
   js:63-64), sans code à retaper : Landry est identifié, avec le droit
   « especes » (pos_store.js:353-370, :773-783) puis « fermer_caisse » et son
   code de visite (:749-750) ; le plan ne se verrouille pas entre-temps
   (S/overrides/closing_popup.js:5-8, :28-34 ; pos_store.js:374-385).
   Ce chemin est lu dans le code, pas joué par un tour (AiteParcoursTour sort
   les espèces depuis le menu ≡ : R/static/tests/tours/parcours_tour.js:453-485).
   La notification d'Odoo « Vous avez réussi à faire un out en espèces de
   121 500 FCFA. » (cash_move_popup.js:62-65 ; fr.po : le type « out » n'est pas
   traduit) est rejouée, hors cadre : pendant ses trois secondes, la caméra est
   sur le bas de la fenêtre (zoom 1,92 sur la fenêtre des mouvements, le haut du
   cadre sous la notification et entre deux rangées de la fermeture ; écart).
3. Le comptage : « 25000 » tapé (sans espace, comme « 6000 » sur la capture
   14), « Compté » 25 000, « Différence » 0 FCFA, plus en rouge (pos_hr
   closing_popup.xml:27).
4. « Fermer la caisse » : le serveur refuse tant que des additions sont au
   brouillon (O/point_of_sale/models/pos_session.py:650-665, :713-715) ; AITE
   remplace la fenêtre d'Odoo (S/overrides/closing_popup.js:54-79) : « Fermer la
   caisse », « 2 tables sont encore ouvertes : 11, 12. Encaissez-les, ou
   annulez-les avec un motif, avant de fermer. » (messages.js:91, :131-136 ;
   liste triée : pos_store.js:1482-1496), « Voir les tables » (la liste des
   commandes), « Annuler ces tables » ; capture 15. « Annuler ces tables » :
   une seule fenêtre, sans « Combien ? » ni code (pos_store.js:1446-1480,
   :1261) : « Annuler les tables encore ouvertes : 11, 12 », « Pourquoi ? »,
   les cinq motifs, « Retour » (messages.js:87, :125, :104 ; S/components/
   annulation_popup/annulation_popup.xml ; capture 16). « Client parti » :
   chaque produit envoyé est tracé (R/models/pos_order.py:669-689, nature
   « Table annulée à la fermeture », R/models/restaurant_annulation.py:28),
   autorisé par Landry ; la caisse se ferme (closing_popup.js:74-75 ; Odoo
   closing_popup.js:199-248) et la page se recharge : une nouvelle session, en
   contrôle d'ouverture, la fenêtre du code ouverte d'elle-même
   (parcours_tour.js:573-575) ; « Caisse fermée par » Landry
   (R/models/pos_session.py:313-322).
5. Le lendemain : « Votre code pour ouvrir la caisse » (messages.js:74), le
   code de Prisca (pos_session.py:199-228 : caissière et au-dessus), puis
   « Contrôle à l'ouverture » : « Espèces à l'ouverture » 25 000, le montant
   compté la veille (O/point_of_sale/models/pos_session.py:381-383 ;
   opening_control_popup.js:27-33), « J'ouvre la caisse »
   (S/overrides/opening_control_popup.xml:9) ; puis le plan verrouillé
   (S/overrides/opening_control_popup.js:17) ; capture 02 (fond « 0 » au premier
   service) et 03.
6. Le rapport de la session, dans la gestion de la manager (Point de Vente ›
   Analyse › Rapport de session : O/point_of_sale/views/point_of_sale_view.xml:
   24-33 ; fr.po « Analyse », « Rapport de session ») ; le fichier « Détails des
   ventes.pdf » (rapport point_of_sale.sale_details_report, O/pos_hr/wizard/
   pos_daily_sales_reports.py:16-18 ; nom : O/web/controllers/report.py:130) dans
   la visionneuse du navigateur ; on voit la page à partir des taxes (cadrage
   de la capture 26) : « Taxes sur les ventes », « Pas de taxe »,
   « Paiements » (« Espèces POS/00014 » : O/point_of_sale/models/
   report_sale_details.py:342), « Total », « Remises » (« Nombre de remises :
   0 », « Montant des remises : 0 FCFA »), puis le bloc d'AITE
   (R/views/report_saledetails.xml:13-78 ; R/models/report_sale_details.py:
   75-124) : « Tables et personnes » (11, 33, 0), « Annulations » (sept lignes,
   ordre « date, id », motif « Autre : précision », « — » sans responsable,
   nature « Retrait sans code » pour la trace sans code), « Total » 9 et
   18 500 FCFA ; enfin « Contrôle de session », « Total : 188 500FCFA »,
   « Nombre de transactions : 12 » (pos_session_sales_details.xml:375-401). Les
   montants d'Odoo sans espace avant « FCFA » (capture 26 ; ECARTS.md n° 88).
   L'en-tête (« À la date du » au format mm/jj/aaaa) et le tableau du contrôle
   (« POS/00014-out-Recette au coffre ») restent hors cadre.

Règles dites par la voix, les bulles, les réactions et les résultats :
- un chef de salle ou le manager ferme, avec son code : R/models/regles.py:41-42
  (fermer_caisse : superviseur) ; pos_session.py:248-256 (R13) ; messages.js:35 ;
  docs/INSTALLATION.md §9.7 (« ≡ → Fermer la caisse → son code ») ; rec R10, R14 ;
- entrer ou sortir des espèces : chef de salle et au-dessus (regles.py:41 ;
  pos_session.py:324-341 ; messages.js:39, R15) ;
- au-delà de l'écart maximum, s'il est réglé, seul le manager ferme (R14 :
  S/overrides/closing_popup.js:36-53 ; regles.py:43 ; messages.js:36-38) ;
- des tables ouvertes empêchent de fermer ; « Annuler ces tables » : une
  fenêtre, un motif, le code déjà tapé sert (N l.121-124 ; closing_popup.js:
  9-13) ; chaque produit envoyé est tracé (pos_order.py:669-689 ; rec R42) ;
- « Voir les tables » ouvre la liste des commandes (closing_popup.js:65-68) ;
- le fond proposé le lendemain est le montant compté la veille
  (pos_session.py:381-383 d'Odoo ; N l.271-272) ;
- le rapport : tables, personnes, ventes sans table, annulations avec leur
  motif et qui les a autorisées (N l.150-152) ; ce qui arrive sans code est
  tracé « Retrait sans code », jamais refusé (N l.125-126) ;
- touches mesurées par AiteParcoursTour : fermer sans table ouverte « 7 +
  chiffres » (11 avec 4 chiffres), « + 2 » avec des tables ouvertes (13),
  rouvrir le lendemain 5 (N §3).

Écarts au storyboard :
- l'équipe est celle de demo.EQUIPE_RESTO : Loïc au lieu du serveur du
  storyboard, Edwige au lieu de la manager du storyboard (noms déjà pris dans
  le dépôt, écartés par le socle) ;
- la journée : les montants par table du storyboard contredisaient
  demo.TABLES_JOUR_RESTO (la table 4 encaissée à 12:41 mais encore ouverte à
  13:48 dans t19 ; la table 10 de midi est celle de Loïc) ; les agrégats sont
  gardés, la répartition est refaite (JOURNEE) ;
- ordre : le lendemain (étape 5) avant le rapport (étape 6) : la tablette reste
  sur la fenêtre du code après la fermeture, et la vidéo finit sur le rapport,
  que le tutoriel suivant prolonge ;
- la fenêtre des mouvements d'espèces s'ouvre par-dessus la fermeture (Odoo ne
  la ferme qu'après la saisie) ; le champ du comptage montre « 0 » d'office ;
- la fermeture porte le bouton d'impression (imprimante de tickets) ;
- « il signe » n'est pas dit : le rapport n'a pas de zone de signature (la
  phrase n'est qu'un commentaire du module, R/views/report_saledetails.xml:9-10) ;
- la bulle R15 vient au début de l'étape 2, sur le bouton, avant la sortie ;
  la bulle R13 pendant la saisie du code ; la réaction de fin est celle de la
  manager (texte, nom) ;
- le rapport : la page défile sous la caméra (zoom 1,5, la barre de la
  visionneuse hors cadre), jusqu'au « Contrôle de session » ; son tableau
  (« POS/00014-out-Recette au coffre ») et le bas de la page restent hors
  cadre ; le numéro de page de la visionneuse n'est pas montré (le nombre de
  pages n'est pas connu sans la base) ;
- la bulle « R14 » dit la règle sans citer le message entier.

Mise en forme propre à ce tutoriel (clé « css ») : la fenêtre des mouvements
d'espèces, le bouton d'impression, l'empilement des fenêtres (chaque fenêtre et
son voile au-dessus de la précédente, comme sur les captures 15 et 16), le
champ du comptage pendant la saisie, la page du rapport (deux colonnes d'Odoo,
« Total » en grand).
"""

import ast
import os
import re

import demo
from ecrans import (ICONES, MESSAGES_RESTO, TEXTES_RESTO, TITRES_RESTO, _odoo_dir, css_personnage, duree_resto, e,
                    entier, fcfa, fenetre_resto, navigateur, rapport_page, rapport_section, rapport_tables_annulations,
                    resto_annulation, resto_code, resto_confirmation, resto_fermeture, resto_menu, resto_notification,
                    resto_ouverture, resto_plan, resto_salle, superpose, visionneuse_pdf)
from marketing import bulle, dezoom, reaction, zoom
from moteur import (anneau, cacher, classe, clic, curseur, defiler, fermer, montrer, notifier, ouvrir, pause, saisir,
                    texte, vue)

RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
R = os.path.join(RACINE, 'addons', 'aite_pos_restaurant')
S = os.path.join(R, 'static', 'src')
O = os.path.join(_odoo_dir(), 'addons')


def _lire(*chemin):
    with open(os.path.join(*chemin), encoding='utf-8') as f:
        return f.read()


def _une_ligne(texte_):
    return ' '.join((texte_ or '').split())


def dans(extrait, source, quoi):
    """Garde-fou : ``extrait`` doit être mot pour mot dans ``source`` (espaces ramenées à une seule)."""
    assert _une_ligne(extrait) in _une_ligne(source), ('t22 : %s changé' % quoi, extrait)


# ============================================================== garde-fous --
# 1. Les textes de la caisse : chaque phrase montrée est relue dans S/utils/messages.js, puis comparée à ce que les
#    composants d'ecrans.py affichent (comme t17).
_JS = _une_ligne(_lire(S, 'utils', 'messages.js'))


def _js(extrait, **valeurs):
    """Le texte d'un littéral de messages.js (``extrait`` doit y être mot pour mot), ``${ESP}`` → espace
    insécable, ``${x}`` → ``valeurs['x']``."""
    assert extrait in _JS, ('t22 : texte changé dans messages.js', extrait)
    t = re.search(r'(["`])(.*)\1', extrait).group(2).replace('${ESP}', ' ')
    for cle_, val in valeurs.items():
        t = t.replace('${%s}' % cle_, str(val))
    assert '${' not in t, extrait
    return t


assert _js('fermer: "Votre code pour fermer la caisse"') == TITRES_RESTO['fermer']
assert _js('ouvrir: "Votre code pour ouvrir la caisse"') == TITRES_RESTO['ouvrir']
assert _js('fermerLaCaisse: "Fermer la caisse"') == TITRES_RESTO['fermerLaCaisse']
assert _js('annulerTables: (liste) => `Annuler les tables encore ouvertes${ESP}: ${liste}`', liste='11, 12') == \
    TITRES_RESTO['annulerTables']('11, 12')
assert (_js('`${nombreDeTables} tables sont encore ouvertes${ESP}: ${liste}. Encaissez-les, ` +', nombreDeTables=2,
            liste='11, 12') + _js('"ou annulez-les avec un motif, avant de fermer."')) == \
    TEXTES_RESTO['tablesOuvertes'](2, '11, 12')
assert _js('voirLesTables: "Voir les tables"') == TEXTES_RESTO['voirLesTables']
assert _js('annulerCesTables: "Annuler ces tables"') == TEXTES_RESTO['annulerCesTables']
assert _js('especes: "Entrée ou sortie d\'espèces"') == TEXTES_RESTO['especes']
assert _js('mouvementsEspeces: "Entrées et sorties d\'espèces"') == TEXTES_RESTO['mouvementsEspeces']
assert _js('`${nombreDeCommandes} commandes${ESP}:`', nombreDeCommandes=12) == TEXTES_RESTO['commandes'](12)
assert _js('planEtat: "Touchez une table, puis tapez votre code."') == TEXTES_RESTO['planEtat']
assert _js('caisseFermee: "La caisse est fermée. La caissière ou un chef de salle tape son code pour '
           'l\'ouvrir."') == TEXTES_RESTO['caisseFermee']
assert _js('pourquoi: `Pourquoi${ESP}?`') == TEXTES_RESTO['pourquoi']
assert _js('retour: "Retour"') == TEXTES_RESTO['retour']
assert _js('R13: "Seul un chef de salle ou le manager ferme la caisse."') == MESSAGES_RESTO['R13']
assert _js('R15: "Seul un chef de salle ou le manager peut sortir ou entrer des espèces."') == MESSAGES_RESTO['R15']
assert _js('"fermer. Recomptez, ou appelez le manager."') in MESSAGES_RESTO['R14']
assert _js('return `${minutes} min`;', minutes=50) == duree_resto(50) == '50 min'
assert duree_resto(75) == '1 h 15'

# 2. Les gabarits et le comportement que la vidéo montre.
_CLO_XML = _lire(S, 'overrides', 'closing_popup.xml')
dans('<t t-esc="aiteTextes.commandes(props.orders_details.quantity)"/>', _CLO_XML, 'le nombre de commandes')
dans('title="aiteTextes.mouvementsEspeces"', _CLO_XML, 'le détail des espèces')
dans('t-on-click="() => this.cashMove()" t-esc="aiteTextes.especes"', _CLO_XML, "le bouton « Entrée ou sortie »")
_CLO_JS = _lire(S, 'overrides', 'closing_popup.js')
for _x in ('title: TITRES.fermerLaCaisse,', 'body: TEXTES.tablesOuvertes(ids.length, this.pos.aiteListeDesTables(ouvertes, ids)),',
           'confirmLabel: TEXTES.voirLesTables,', 'cancelLabel: TEXTES.annulerCesTables,',
           'this.pos.showScreen("TicketScreen");', 'await this.pos.deleteOrders(tables, ids); this.closeSession();',
           'return this.pos.aitePeut("fermer_avec_ecart") || this.allowedDifference();',
           # la fenêtre rouverte après une sortie d'espèces faite depuis elle ne verrouille pas le plan
           'après une sortie d\'espèces faite depuis elle'):
    dans(_x, _CLO_JS, 'la fenêtre de fermeture')
_STORE = _lire(S, 'store', 'pos_store.js')
for _x in ('if (this.cashier && this.aiteCodeVisite && this.aitePeut("fermer_caisse")) {',
           'autorise = await this.aiteIdentifier({ titre: TITRES.fermer, verifier });',
           'titre: TITRES.especes, geste: "especes", refus: MESSAGES.R15,',
           'if (!this.cashier && !(await this.aiteIdentifier({ titre }))) {',
           'titre: TITRES.annulerTables(this.aiteListeDesTables(ouvertes, ids)),', 'nature: "fermeture",',
           'const codeRequis = !(this.aitePeut("annuler_envoye") && this.aiteCodeVisite);',
           '.sort((a, b) => a.localeCompare(b, undefined, { numeric: true }))'):
    dans(_x, _STORE, 'pos_store.js')
dans('<DropdownItem t-if="showCashMoveButton and pos.aiteActif" onSelected="() => this.pos.cashMove()"> '
     'Entrée ou sortie d\'espèces </DropdownItem>', _lire(S, 'overrides', 'navbar.xml'), 'le menu ≡')
dans('<attribute name="t-if" add="pos.aiteActif" separator=" or "/>', _lire(S, 'overrides', 'navbar.xml'),
     '« Fermer la caisse » dans le menu ≡')
dans('<attribute name="t-out">pos.aiteActif ? "J\'ouvre la caisse" : undefined</attribute>',
     _lire(S, 'overrides', 'opening_control_popup.xml'), "« J'ouvre la caisse »")
dans('this.pos.aiteVerrouillerSurPlan();', _lire(S, 'overrides', 'opening_control_popup.js'), "le verrou à l'ouverture")
_ANN_XML = _lire(S, 'components', 'annulation_popup', 'annulation_popup.xml')
dans('t-esc="textes.pourquoi"', _ANN_XML, '« Pourquoi ? »')


def _source(relatif, nom):
    """Une constante d'un fichier Python du module, lue sans importer Odoo (comme t16)."""
    for noeud in ast.parse(_lire(R, relatif)).body:
        if isinstance(noeud, ast.Assign) and any(getattr(c, 'id', None) == nom for c in noeud.targets):
            return ast.literal_eval(noeud.value)
    raise ValueError('t22 : %s introuvable dans %s' % (nom, relatif))


_DROITS = _source('models/regles.py', 'DROITS')
assert (_DROITS['fermer_caisse'], _DROITS['especes'], _DROITS['annuler_envoye'], _DROITS['fermer_avec_ecart'],
        _DROITS['ouvrir_caisse']) == ('superviseur', 'superviseur', 'superviseur', 'manager', 'caissiere'), \
    't22 : droits changés (fermer, espèces, annuler, écart, ouvrir)'
_NIVEAUX = dict(_source('models/regles.py', 'NIVEAUX'))
_NATURES = dict(_source('models/restaurant_annulation.py', 'TYPES_ANNULATION'))
assert (_NATURES['fermeture'], _NATURES['retrait_sans_code']) == ('Table annulée à la fermeture', 'Retrait sans code')
assert _source('models/pos_config.py', 'NOM_CAISSE') == demo.CAISSE_RESTO
assert (_source('models/pos_config.py', 'NOM_ESPECES'), _source('models/pos_config.py', 'NOM_MOBILE_MONEY')) == \
    demo.MODES_RESTO
_MOTIFS_XML = _lire(R, 'data', 'restaurant_motif_data.xml')
assert all('<field name="name">%s</field>' % m in _MOTIFS_XML for m in demo.MOTIFS_RESTO)

# 3. Le rapport de la session : le bloc d'AITE (vue et modèle).
_RP_XML = _lire(R, 'views', 'report_saledetails.xml')
for _x in ('<h6 class="bg-secondary p-1 fw-bold">Tables et personnes</h6>', '<td class="ps-2">Nombre de tables</td>',
           '<td class="ps-2">Nombre de personnes</td>', '<td class="ps-2">Ventes sans table</td>',
           '<h6 class="bg-secondary p-1 fw-bold">Annulations</h6>', '<th class="ps-2">Table</th>', '<th>Produit</th>',
           '<th class="text-end">Quantité</th>', '<th class="text-end">Montant</th>', '<th>Motif</th>',
           '<th>Autorisée par</th>', "<span t-out=\"annulation['autorisee_par'] or '—'\">",
           '<td class="ps-2" colspan="2">Total</td>', '<xpath expr="//div[@id=\'discounts\']" position="after">'):
    dans(_x, _RP_XML, 'le rapport de fermeture (vue)')
_RP_PY = _lire(R, 'models', 'report_sale_details.py')
for _x in ("order='date, id'", 'motif = trace.motif_nom or natures.get(trace.type_annulation) or',
           '_("%(motif)s : %(precision)s", motif=motif,', "'aite_tables': sum(commandes.mapped('aite_tables')),",
           "'aite_personnes': sum(commandes.mapped('aite_personnes')),"):
    dans(_x, _RP_PY, 'le rapport de fermeture (modèle)')

# 4. Les touches mesurées (résultats) et les phrases des notes de version citées.
_NOTES = _lire(RACINE, 'docs', 'NOTES_DE_VERSION_restaurant_lot1.md')
for _x in ('| Caissière — ouvrir la caisse le matin | 5 | **5** (et **5** le lendemain, fond prérempli) |',
           '| Chef — fermer la caisse, sans table ouverte | 7 + chiffres | **11** (4 chiffres) |',
           '| Chef — fermer avec des tables ouvertes et les annuler | + 2 | **13** (7 + 4 chiffres + 2), avec 2 '
           'tables ouvertes |',
           'comptés à la fermeture et repris en fond le lendemain',
           'tracé « Retrait sans code » ou « Annulation sans code ».',
           'sans table, annulations de la session avec leur motif et qui les a autorisées.'):
    dans(_x, _NOTES, 'les notes de version')
dans('Le soir, un chef de salle ferme la caisse (≡ → Fermer la caisse → son code).',
     _lire(RACINE, 'docs', 'INSTALLATION.md'), 'INSTALLATION §9.7')

# 5. Odoo : le fond du lendemain, les libellés français (fr.po), le refus des additions au brouillon.
dans("session.cash_register_balance_start = last_session.cash_register_balance_end_real",
     _lire(O, 'point_of_sale', 'models', 'pos_session.py'), "le fond repris d'Odoo")
dans("type: \"out\",", _lire(O, 'point_of_sale', 'static', 'src', 'app', 'navbar', 'cash_move_popup',
                             'cash_move_popup.js'), '« Cash sortant » choisi d\'office')
_PO = (_lire(O, 'point_of_sale', 'i18n', 'fr.po') + _lire(O, 'pos_restaurant', 'i18n', 'fr.po')
       + _lire(O, 'pos_hr', 'i18n', 'fr.po'))
for _msg in ('Commandes', 'Imprimer le rapport', 'Fermer la caisse', 'Fermeture de la caisse', 'Ouverture', 'Paiements',
             'Compté', 'Différence', 'Comptage de caisse', 'Nombre', 'Note de clôture', 'Ajouter une note de fermeture...',
             'Ignorer', 'Ventes du jour', 'Cash entrant', 'Cash sortant', 'Motif', 'Confirmer',
             "Vous avez réussi à faire un %s en espèces de %s.", "Contrôle à l'ouverture", "Espèces à l'ouverture",
             "Note d'ouverture", "Ajouter une note d'ouverture...", 'Taxes sur les ventes', 'Pas de taxe', 'Total',
             'Remises', '<strong>Nombre de remises</strong> :', '<strong>Montant des remises</strong> :',
             'Contrôle de session', 'Total :', 'Nombre de transactions :', 'Détails des ventes', 'Rapport de session',
             'Analyse', 'Plan', 'Table'):
    assert 'msgstr "%s"' % _msg.replace('"', '\\"') in _PO, ("t22 : libellé d'Odoo introuvable", _msg)

# ============================================================== les données --
LANDRY = next(x for x in demo.EQUIPE_RESTO if x[0] == demo.POSTES_RESTO['chef'][0])
PRISCA = next(x for x in demo.EQUIPE_RESTO if x[0] == demo.POSTES_RESTO['caisse'][0])
EDWIGE = next(x for x in demo.EQUIPE_RESTO if x[0] == demo.POSTES_RESTO['manager'][0])
assert (LANDRY[2], PRISCA[2], EDWIGE[2]) == (_NIVEAUX['superviseur'], _NIVEAUX['caissiere'], _NIVEAUX['manager'])
NOM_L, CODE_L = LANDRY[1], LANDRY[3]
NOM_P, CODE_P = PRISCA[1], PRISCA[3]
NOM_E = EDWIGE[1]
PRIX = {nom: prix for nom, _f, prix, _c, _s in demo.CARTE_RESTO}
SESSION = 'POS/00014'
FOND = demo.FOND_RESTO
assert FOND == 25000

# La journée du 14/10 : les additions réglées de la session, une par ligne : (payée à, table ou part, ouverte par,
# personnes, tables, contenu, mode). Les tables de demo.TABLES_JOUR_RESTO (t17 à t20) gardent qui les a ouvertes et
# ce qu'elles portent ; ce qui n'était fixé nulle part est proposé ici (compte rendu, « Demandes au socle »). Une part
# d'addition divisée compte 0 table et 0 personne (R/models/regles.py, ``compteurs``). Toutes encaissées par Prisca.
ESP, MM = demo.MODES_RESTO
JOURNEE = [
    ('12:35', '1', 'Loïc', 3, 1, {'Pizza Reine': 1, 'Pizza Margherita': 2, 'Cola 33 cl': 2, 'Jus de bissap 50 cl': 1}, MM),
    ('13:15', '7', 'Inès', 4, 1, {'Pizza Margherita': 2, 'Pizza Reine': 2, 'Bière blonde 65 cl': 4}, MM),
    ('13:20', '10', 'Loïc', 2, 1, {'Pizza Reine': 2, 'Bière blonde 65 cl': 4}, ESP),
    ('13:25', '6', 'Inès', 2, 1, {'Pizza quatre fromages': 1, 'Bière blonde 65 cl': 2}, ESP),
    ('14:00', '4', 'Loïc', 6, 1, {'Pizza Margherita': 1, 'Bière blonde 65 cl': 2, 'Cola 33 cl': 2,
                                  'Pizza quatre fromages': 1, 'Eau minérale 50 cl': 2}, ESP),
    ('14:05', '5', 'Inès', 2, 1, {'Pizza quatre fromages': 1, 'Bière blonde 65 cl': 2}, ESP),
    ('14:10', '2', 'Loïc', 2, 1, {'Cola 33 cl': 2, 'Pizza Margherita': 1, 'Bière blonde 65 cl': 2}, ESP),
    ('20:05', '10', 'Inès', 4, 1, {'Pizza Reine': 1, 'Bière blonde 65 cl': 2, 'Cola 33 cl': 1,
                                   'Pizza quatre fromages': 1, 'Bière brune 65 cl': 2}, ESP),
    ('20:47', '9B', 'Loïc', 0, 0, {'Pizza Reine': 1}, MM),
    ('20:48', '9', 'Loïc', 2, 1, {'Pizza quatre fromages': 1, 'Bière blonde 65 cl': 2}, ESP),
    ('21:20', '3', 'Loïc', 4, 1, {'Pizza quatre fromages': 2, 'Pizza Margherita': 1, 'Bière blonde 65 cl': 3,
                                  'Cola 33 cl': 2}, ESP),
    ('21:35', '8', 'Inès', 2, 1, {'Pizza Reine': 2, 'Bière blonde 33 cl': 2}, MM),
]


def _total(contenu):
    return sum(PRIX[p] * q for p, q in contenu.items())


# Ce que demo.TABLES_JOUR_RESTO fixe déjà : qui a ouvert, combien de personnes, ce que porte la table (sans l'ajout de
# t21 pour la table 4 : quatre fromages et deux eaux, storyboard t21).
_FIXE = {(t, ouv, h): (pers, contenu) for t, ouv, h, pers, contenu, _s, _tu in demo.TABLES_JOUR_RESTO}
assert _FIXE[(10, 'Loïc', '11:52')][1] == JOURNEE[2][5]
assert _FIXE[(5, 'Inès', '13:05')] == (JOURNEE[5][3], JOURNEE[5][5])
assert _FIXE[(10, 'Inès', '19:10')] == (JOURNEE[7][3], JOURNEE[7][5])
assert _FIXE[(4, 'Loïc', '12:15')][0] == JOURNEE[4][3]
assert all(JOURNEE[4][5][p] >= q for p, q in _FIXE[(4, 'Loïc', '12:15')][1].items())
assert all(JOURNEE[6][5][p] >= q for p, q in _FIXE[(2, 'Loïc', '12:55')][1].items())
assert _total(JOURNEE[7][5]) == 20000
NB_COMMANDES = len(JOURNEE)
TOTAL_JOUR = sum(_total(c) for *_x, c, _m in JOURNEE)
ESPECES_JOUR = sum(_total(c) for *_x, c, m in JOURNEE if m == ESP)
MOMO_JOUR = sum(_total(c) for *_x, c, m in JOURNEE if m == MM)
TABLES = sum(t for _h, _n, _o, _p, t, _c, _m in JOURNEE)
PERSONNES = sum(p for _h, _n, _o, p, _t, _c, _m in JOURNEE)
assert (NB_COMMANDES, TOTAL_JOUR, ESPECES_JOUR, MOMO_JOUR, TABLES, PERSONNES) == (12, 188500, 121500, 67000, 11, 33), \
    't22 : la journée a changé (storyboard t22 §0, repris par t23)'

# 22:30 : deux tables encore ouvertes, tout envoyé. (table, ouverte par, ouverte à, minutes à 22:30, produits)
OUVERTES = [(11, 'Loïc', '21:40', 50, [('Bière blonde 65 cl', 2)]),
            (12, 'Inès', '21:15', 75, [('Pizza Margherita', 1), ('Cola 33 cl', 1)])]
assert all(n not in [int(x[1]) for x in JOURNEE if x[1].isdigit() and x[0] > '21:00'] for n, *_r in OUVERTES)
LISTE = ', '.join(str(n) for n, *_r in OUVERTES)
assert LISTE == '11, 12'

# Les espèces : le fond, les paiements ; Landry sort la recette ; il reste le fond, compté et repris le lendemain.
ATTENDU = FOND + ESPECES_JOUR
SORTIE = ESPECES_JOUR
MOTIF_SORTIE = 'Recette au coffre'
COMPTE = ATTENDU - SORTIE
assert (ATTENDU, COMPTE) == (146500, FOND)

# Les annulations de la session, dans l'ordre du rapport (« date, id »), avec le motif tel que le rapport l'écrit :
# le journal de t19 (demo.ANNULATIONS_JOUR_RESTO, rangé « date desc, id desc ») retourné, puis les produits des tables
# annulées à la fermeture, par Landry (ordre des additions : lu, non vu).
ANNULATIONS = []
for _d, _t, _p, _q, _dem, _aut, _motif, _prec in reversed(demo.ANNULATIONS_JOUR_RESTO):
    _m = _motif or _NATURES['retrait_sans_code']
    ANNULATIONS.append((_t, _p, _q, _q * PRIX[_p], _m + (' : ' + _prec if _prec else ''), _aut))
for _n, _o, _h, _min, _produits in OUVERTES:
    for _p, _q in _produits:
        ANNULATIONS.append((str(_n), _p, _q, _q * PRIX[_p], demo.MOTIFS_RESTO[1], NOM_L))
QTE_ANN = sum(a[2] for a in ANNULATIONS)
MONTANT_ANN = sum(a[3] for a in ANNULATIONS)
assert (len(ANNULATIONS), QTE_ANN, MONTANT_ANN) == (7, 9, 18500)
assert ANNULATIONS[0][4] == 'Retrait sans code' and ANNULATIONS[0][5] == ''
assert demo.MOTIFS_RESTO[1] == 'Client parti'

# ================================================================ l'écran --
POS = 't22-pos'
ETATS_SOIR = {n: ('orange' if m >= demo.DELAI_ORANGE else 'vert', duree_resto(m), None)
              for n, _o, _h, m, _p in OUVERTES}
assert ETATS_SOIR == {11: ('vert', '50 min', None), 12: ('orange', '1 h 15', None)}
PLAN = resto_plan('t22-plan', resto_salle('t22-plan', ETATS_SOIR), delai=demo.DELAI_ORANGE, salle=demo.SALLE_RESTO,
                  initiale=True)
# Après la fermeture, la page se recharge : une nouvelle session, en contrôle d'ouverture, toutes les tables libres.
PLAN2 = resto_plan('t22-plan2', resto_salle('t22-plan2'), delai=demo.DELAI_ORANGE, salle=demo.SALLE_RESTO,
                   caisse_fermee=True)

MENU = resto_menu('t22-menu', commandes=len(OUVERTES), imprimante=True)
CODE = resto_code('t22-code', TITRES_RESTO['fermer'])


def fermeture(ident, mouvements):
    """« Fermeture de la caisse » (resto_fermeture), avec ce que le composant du socle ne pose pas : le champ du
    comptage à « 0 » (Odoo, closing_popup.js:68-72), son texte indicatif vide (pour le geste ``saisir``), le signe d'un
    mouvement négatif (« - 121 500 FCFA » : payment_method_breakdown.xml:8-9) et le bouton d'impression (avec une
    imprimante : closing_popup.xml:109-111 ; icône fa-print de SaleDetailsButton)."""
    html = resto_fermeture(ident, NB_COMMANDES, TOTAL_JOUR, FOND, ESPECES_JOUR, mouvements=mouvements, compte=0,
                           autres=[(MM, MOMO_JOUR)])
    remplacements = [('<span class="val" id="%s-in-val">0</span>' % ident,
                      '<span id="%s-in-ph"></span><span class="val" id="%s-in-val">0</span>' % (ident, ident)),
                     ('Ventes du jour<span class="ico">%s</span></span>' % ICONES['telecharger'],
                      'Ventes du jour<span class="ico">%s</span></span><span class="rs-bt t22-imp" id="%s-imp">'
                      '<span class="ico">%s</span></span>' % (ICONES['telecharger'], ident, ICONES['imprimer']))]
    if mouvements < 0:
        remplacements.append(('<span>+ %s</span>' % fcfa(mouvements), '<span>- %s</span>' % fcfa(-mouvements)))
    # le composant passe par ``superpose`` (chaque texte porte data-layout-allow-overlap) : les morceaux aussi
    for avant, apres in remplacements:
        avant, apres = superpose(avant), superpose(apres)
        assert html.count(avant) == 1, (ident, avant)
        html = html.replace(avant, apres)
    # le détail des espèces, désigné par la caméra et l'anneau
    marque = superpose('<div class="rs-cl-s fonce"><span><i class="rs-tri">')
    i = html.index(marque, html.index(marque) + 1)
    html = (html[:i] + superpose('<div class="rs-cl-s fonce" id="%s-mvt"><span><i class="rs-tri">' % ident)
            + html[i + len(marque):])
    return html


F1 = fermeture('t22-f1', 0)
F2 = fermeture('t22-f2', -SORTIE)
assert '- 121 500 FCFA' in F2 and 'id="t22-f2-mvt"' in F2 and 'class="rs-cl-s fonce off" id' not in F1


def mouvement(ident, haut=226, largeur=1072):
    """La fenêtre des mouvements d'espèces d'Odoo (CashMovePopup, cash_move_popup.xml:4-39 ; Dialog sans en-tête,
    taille « lg » : 800 points × 1,34) : « Cash entrant », « Cash sortant » (btn-danger, choisi d'office), le montant
    et la devise à droite (Input, icône « FCFA » après le montant), la croix ; « Motif » en étiquette flottante
    (form-floating : le texte indicatif « Laissez une explication ici » est transparent) ; « Confirmer » (grisé tant
    que montant et motif manquent) et « Ignorer ». Aucune capture. Identifiants : <id>-voile, <id>, <id>-m (montant,
    -ph, -val), <id>-r (motif, -ph, -val), <id>-ok, <id>-ignorer."""
    corps = ('<div class="rs-dlg-c"><div class="t22-mv-l"><span class="t22-mv-g"><span class="t22-mv-b">Cash entrant'
             '</span><span class="t22-mv-b t22-mv-out" id="%s-out">Cash sortant</span></span>'
             '<span class="rs-champ t22-mv-m" id="%s-m"><span id="%s-m-ph"></span><span class="val" id="%s-m-val"></span>'
             '<span class="t22-mv-dev">FCFA</span><span class="rs-x t22-mv-x t22-cache" id="%s-m-x">%s</span></span></div>'
             '<div class="t22-mv-f" id="%s-r"><label>Motif</label><span id="%s-r-ph"></span>'
             '<span class="val" id="%s-r-val"></span></div></div>'
             % (ident, ident, ident, ident, ident, ICONES['croix-pleine'], ident, ident, ident))
    pied = ('<div class="rs-dlg-p"><span class="rs-bt rs-bt-p t22-off" id="%s-ok" data-layout-ignore>Confirmer</span>'
            '<span class="rs-bt" id="%s-ignorer">Ignorer</span></div>' % (ident, ident))
    return superpose('<div class="voile masque rs-voile" id="%s-voile"></div>'
                     '<div class="rs-dlg masque t22-mv" id="%s" style="top:%dpx;width:%dpx;margin-left:-%dpx">%s%s</div>'
                     % (ident, ident, haut, largeur, largeur // 2, corps, pied))


MVT = mouvement('t22-mvt')
# Odoo : _t("Successfully made a cash %s of %s.", type, montant), le type « out » passé tel quel (cash_move_popup.js:
# 62-65) ; rejouée hors cadre (voir l'en-tête).
NOTIF_OUT = resto_notification('t22-n-out', 'Vous avez réussi à faire un out en espèces de %s.' % fcfa(SORTIE))
REFUS = resto_confirmation('t22-refus', TITRES_RESTO['fermerLaCaisse'], TEXTES_RESTO['tablesOuvertes'](len(OUVERTES),
                                                                                                      LISTE),
                           TEXTES_RESTO['voirLesTables'], TEXTES_RESTO['annulerCesTables'], haut=252)
ANNUL = resto_annulation('t22-ann', TITRES_RESTO['annulerTables'](LISTE), motifs=demo.MOTIFS_RESTO, code=False,
                         haut=208)
CODE_O = resto_code('t22-codeo', TITRES_RESTO['ouvrir'])
OUV = resto_ouverture('t22-ouv', entier(FOND))


# ------------------------------------------------- le rapport de la session --
def _odoo(montant):
    """Un montant du rapport d'Odoo : chiffres groupés à la française, « FCFA » collé (pos_session_sales_details.xml :
    widget « float » puis le symbole, sans espace ; capture 26, ECARTS.md n° 88)."""
    return entier(montant) + 'FCFA'


RP_ANN = rapport_tables_annulations(TABLES, PERSONNES, 0, ANNULATIONS, ident='t22-rp')
_LIGNE_SANS_CODE = '<tr><td>%s</td><td>%s</td>' % (e(ANNULATIONS[0][0]), e(ANNULATIONS[0][1]))
assert RP_ANN.count(_LIGNE_SANS_CODE) == 1
RP_ANN = RP_ANN.replace(_LIGNE_SANS_CODE, '<tr id="t22-rp-sc"><td>%s</td><td>%s</td>'
                        % (e(ANNULATIONS[0][0]), e(ANNULATIONS[0][1])))
RP_ANN = RP_ANN.replace('<tr><td>Nombre de personnes</td>', '<tr id="t22-rp-pers"><td>Nombre de personnes</td>')
assert 'id="t22-rp-pers"' in RP_ANN
RAPPORT = rapport_page('t22-rp-page', (
    # « Taxes sur les ventes » (w-50 ms-auto), puis « Paiements » et son « Total » (pos_session_sales_details.xml:112-158,
    # :268-311)
    '<div class="t22-w50"><h6 class="t22-h6">Taxes sur les ventes</h6><table class="rs-rp-t t22-rp3">'
    '<tr><td class="g">Pas de taxe</td><td class="d">%s</td><td class="d">%s</td></tr>'
    '<tr class="gras"><td>Total</td><td class="d">%s</td><td class="d">%s</td></tr></table>'
    '<h6 class="t22-h6" id="t22-rp-pai">Paiements</h6><table class="rs-rp-t t22-rp2">%s</table>'
    '<div class="t22-rp-tot"><span>Total</span><span>%s</span></div></div>'
    % (_odoo(0), _odoo(TOTAL_JOUR), _odoo(0), _odoo(TOTAL_JOUR),
       ''.join('<tr><td class="g">%s %s</td><td class="d">%s</td></tr>' % (e(mode), SESSION, _odoo(montant))
               for mode, montant in ((ESP, ESPECES_JOUR), (MM, MOMO_JOUR))), _odoo(TOTAL_JOUR))
    + rapport_section('Remises', '<p class="t22-rp-l"><b>Nombre de remises</b> : 0</p>'
                                 '<p class="t22-rp-l"><b>Montant des remises</b> : 0 FCFA</p>')
    + RP_ANN
    + rapport_section('Contrôle de session', '<p class="t22-rp-l"><b>Total : %s</b></p>'
                                             '<p class="t22-rp-l"><b>Nombre de transactions : %d</b></p>'
                      % (_odoo(TOTAL_JOUR), NB_COMMANDES), 't22-rp-ctl')))
PDF = visionneuse_pdf('t22-pdf', 'Détails des ventes.pdf', RAPPORT)

CAISSE = fenetre_resto(POS, [PLAN, PLAN2], calques=MENU + CODE + F1 + MVT + F2 + NOTIF_OUT + REFUS + ANNUL + CODE_O
                       + OUV + PDF, avatar=demo.AVATARS_RESTO[NOM_L])
ECRAN = navigateur(CAISSE)

CSS = ("/* -- la pastille : Landry (le personnage), Prisca à l'étape 5, Edwige à l'étape 6 -- */\n"
       + css_personnage('#tu-perso.t22-prisca', PRISCA[0], demo.POSTES_RESTO['caisse'][1], NOM_P[0])
       + css_personnage('#tu-perso.t22-edwige', EDWIGE[0], demo.POSTES_RESTO['manager'][1], NOM_E[0]) + """
/* -- l'avatar de Prisca en haut de la caisse (celui de Landry est posé par fenetre_resto) -- */
.resto.t22-prisca .rs-emp .avatar { background: %s !important; }
/* -- les fenêtres empilées : chacune et son voile au-dessus de la précédente (captures 15 et 16) -- */
#t22-mvt-voile { z-index: 32; } #t22-mvt { z-index: 33; }
#t22-refus-voile { z-index: 32; } #t22-refus { z-index: 33; }
#t22-ann-voile { z-index: 32; } #t22-ann { z-index: 33; }
#t22-n-out { z-index: 40; }
/* -- la fermeture : le pied tient sur une ligne avec le bouton d'impression (btn-lg icône) -- */
#t22-f1 .rs-dlg-p, #t22-f2 .rs-dlg-p { gap: 10px; padding: 18px 26px 20px; }
#t22-f1 .rs-dlg-p .rs-bt, #t22-f2 .rs-dlg-p .rs-bt { padding: 0 19px; }
.resto .t22-imp .ico, .resto .t22-imp .ico svg { width: 26px; height: 26px; }
/* le champ du comptage pendant la saisie (form-control:focus) */
#t22-f2-in.focus { border-color: var(--muk-prim); box-shadow: 0 0 0 4px rgba(74,120,146,.22); }
/* -- la fenêtre des mouvements d'espèces d'Odoo (cash_move_popup.xml) -- */
#t22-mvt .rs-dlg-c { padding: 30px 32px 26px; }
.t22-mv-l { display: flex; gap: 11px; margin-bottom: 11px; }
.t22-mv-g { display: flex; }
.t22-mv-b { height: 64px; padding: 0 26px; display: flex; align-items: center; font-size: 24px; background: #E2E5E9;
  color: #212529; }
.t22-mv-g .t22-mv-b:first-child { border-radius: 6px 0 0 6px; }
.t22-mv-g .t22-mv-b:last-child { border-radius: 0 6px 6px 0; }
.resto .t22-mv-out { background: #DC3545; color: #fff; }   /* btn-danger d'Odoo */
.resto .t22-mv-m { width: 252px; height: 64px; padding: 0 14px; justify-content: flex-start; gap: 10px; }
.resto .t22-mv-m.focus, .t22-mv-f.focus { border-color: var(--muk-prim); box-shadow: 0 0 0 4px rgba(74,120,146,.22); }
.t22-mv-dev { margin-left: auto; font-size: 24px; color: #212529; }
.resto .t22-mv-x svg { width: 18px; height: 18px; }
.t22-mv-f { position: relative; height: 134px; border: 1px solid #CED4DA; border-radius: 6px; background: #fff;
  padding: 50px 17px 0; font-size: 22px; color: #212529; }
.t22-mv-f label { position: absolute; left: 17px; top: 22px; font-size: 22px; color: #5C636A; }
.t22-mv-f.rempli label { top: 12px; font-size: 18px; }
.resto .t22-cache { visibility: hidden; }
/* le texte indicatif vide des champs saisis : hors de la mise en page (le champ garde son alignement) */
#t22-f1-in-ph, #t22-f2-in-ph, #t22-mvt-m-ph, #t22-mvt-r-ph { display: none; }
/* « Mobile Money Nombre » sous le bord de la zone qui défile, pas à moitié coupé */
#t22-f1 .rs-in-l:has(#t22-f1-in), #t22-f2 .rs-in-l:has(#t22-f2-in) { margin-bottom: 44px; }
#t22-rp-page { width: 1280px; }
.resto .t22-off { opacity: .65; }
/* -- le rapport de la session : la page vue à partir des taxes (cadrage de la capture 26) -- */
#t22-pdf-defil { padding-top: 0; margin-top: -30px; }
#t22-rp-page { padding-top: 56px; }
.t22-w50 { width: 50%%; margin-left: auto; }
.t22-h6 { margin: 20px 0 10px; padding: 6px 10px; background: #DEE2E6; font-size: 20px; font-weight: 700; }
.resto .rs-rp-t td.g { font-weight: 700; }
.resto .t22-rp2 td { border-bottom: 0; }
.t22-rp-tot { display: flex; justify-content: space-between; padding: 12px 12px 6px; border-top: 1px solid #343A40;
  font-size: 25px; font-weight: 700; }
.t22-rp-l { margin: 4px 0; }
.resto .rs-pdf-p { display: none; }
""" % demo.AVATARS_RESTO[NOM_P])


# ================================================================ les gestes --
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


def employe(nom, *classes_):
    """Le nom et l'initiale de l'employé en haut de la caisse."""
    return [texte('#%s-emp-n' % POS, nom), texte('#%s-emp-av' % POS, nom[0], avec=True),
            classe('#' + POS, ajouter=['avec-emp'] + list(classes_), avec=True)]


ETAPES = [
    # 1. ≡, « Fermer la caisse », le code de Landry : la fenêtre de fermeture s'ouvre à son nom.
    {'temps': 0, 'titre': 'Fermer la caisse, avec son code',
     'texte': '≡ › « Fermer la caisse » : « %s ». Un chef de salle ou le manager.' % TITRES_RESTO['fermer'],
     'voix': "Le service est fini, mais deux tables sont restées ouvertes. Landry, le chef de salle, ouvre le menu et "
             "touche Fermer la caisse. Il tape son code : seuls un chef de salle ou le manager peuvent fermer.",
     # calé sur la voix : les deux tables sur « deux tables sont restées ouvertes », le menu sur « ouvre le menu », le
     # code sur « Il tape son code ».
     'gestes': [pause(0.3), curseur('#t22-plan-t11', fx=0.8, fy=0.8, d=0.6), anneau('#t22-plan-t11', d=1.0),
                anneau('#t22-plan-t12', d=1.0), pause(0.6), curseur('#%s-menu' % POS, d=0.7), pause(0.4)]
               + touche('#%s-menu' % POS, montrer('#t22-menu', d=0.2, y=-8), d=0.25)
               + [pause(0.2), curseur('#t22-menu-fermer', fx=0.4, d=0.4)]
               + touche('#t22-menu-fermer', cacher('#t22-menu', d=0.15), ouvrir('t22-code'), d=0.25)
               + [pause(0.1), bulle('b-r13', '#t22-code', cote='droite', d=3.8), pause(0.3)]
               + taper('t22-code', CODE_L, d=0.26)
               + [fermer('t22-code'), *employe(NOM_L), ouvrir('t22-f1', avec=True, decale=0.15)]},
    # 2. La recette au coffre, depuis la fenêtre de fermeture ; la fenêtre revient, sans code à retaper.
    {'temps': 1, 'titre': 'La recette au coffre',
     'texte': '« %s » depuis la fermeture : la fenêtre revient, sans code à retaper.' % TEXTES_RESTO['especes'],
     'voix': "Avant de compter, il sort la recette en espèces : Entrée ou sortie d'espèces, cent vingt et un mille cinq "
             "cents francs CFA, recette au coffre. La fenêtre de fermeture revient, sans retaper son code : il "
             "n'attend plus que vingt-cinq mille francs CFA.",
     # calé sur la voix : la bulle sur « il sort la recette en espèces », le bouton sur « Entrée ou sortie
     # d'espèces », le montant puis le motif sur leurs mots, « Confirmer » sur « La fenêtre de fermeture revient » ;
     # la caméra reste sur le bas de la fenêtre tant que la notification d'Odoo (3 s, en haut à droite) est là.
     'gestes': [curseur('#t22-f1-especes', d=0.6), bulle('b-r15', '#t22-f1-especes', cote='haut', d=2.5), pause(1.2)]
               + touche('#t22-f1-especes', ouvrir('t22-mvt'), d=0.4)
               # le haut du cadre tombe entre deux rangées de la fermeture : sous le titre « Espèces » (1,82), puis sous
               # « Ouverture » (1,92), plus bas que la notification
               + [zoom('#t22-mvt', s=1.82, fy=1.0, d=0.6),
                  saisir('t22-mvt-m', entier(SORTIE).replace(' ', ''), d=0.9),
                  classe('#t22-mvt-m-x', retirer=['t22-cache'], avec=True, decale=0.1), pause(0.4),
                  saisir('t22-mvt-r', MOTIF_SORTIE, d=1.0), classe('#t22-mvt-r', ajouter=['rempli'], avec=True),
                  classe('#t22-mvt-ok', retirer=['t22-off'], decale=0.2),
                  # plus serré avant « Confirmer » : le haut du cadre passe sous la notification qui va paraître
                  zoom('#t22-mvt', s=1.92, fy=1.0, d=0.3, avec=True)]
               + touche('#t22-mvt-ok', fermer('t22-mvt'), fermer('t22-f1'), notifier('t22-n-out', duree=3.0),
                        ouvrir('t22-f2', decale=0.35), d=0.4)
               + [pause(0.5), anneau('#t22-f2-mvt', d=1.3), pause(0.5), dezoom(d=0.4), anneau('#t22-f2-esp', d=1.3),
                  pause(0.3)]},
    # 3. Le comptage : il reste le fond ; « 25000 », différence 0 ; « Fermer la caisse ».
    {'temps': 1, 'titre': 'Compter le fond',
     'texte': '« Comptage de caisse » : %s. « Différence » : %s. Puis « Fermer la caisse ».'
              % (entier(COMPTE), fcfa(0)),
     'voix': "Dans le tiroir, il reste le fond de caisse. Landry le compte et tape vingt-cinq mille : la différence "
             "tombe à zéro, il touche Fermer la caisse.",
     # calé sur la voix : le comptage sur « tape vingt-cinq mille », la différence sur « tombe à zéro », « Fermer la
     # caisse » sur « il touche Fermer la caisse ».
     'gestes': [zoom('#t22-f2-esp', s=1.4, fy=0.85, d=0.6), anneau('#t22-f2-diffl', d=1.0),
                defiler('#t22-f2-defil', -128, d=0.5), curseur('#t22-f2-in', fx=0.2, d=0.4), pause(0.5),
                saisir('t22-f2-in', str(COMPTE), d=0.8),
                texte('#t22-f2-compte', fcfa(COMPTE)), texte('#t22-f2-diff', fcfa(0), avec=True),
                classe('#t22-f2-diffl', retirer=['rouge'], avec=True), pause(0.1), anneau('#t22-f2-diffl', d=1.0),
                bulle('b-r14', '#t22-f2-diffl', cote='bas', d=2.2), pause(0.5), dezoom(d=0.5)]
               + touche('#t22-f2-ok', d=0.5)},
    # 4. Le refus : deux tables encore ouvertes ; « Annuler ces tables », un motif ; la caisse se ferme.
    {'temps': 2, 'titre': 'Deux tables encore ouvertes',
     'texte': 'Refus : « %s » ou « %s ». Le code est déjà tapé : un motif suffit, chaque produit est tracé.'
              % (TEXTES_RESTO['voirLesTables'], TEXTES_RESTO['annulerCesTables']),
     'voix': "Refusé : deux tables sont encore ouvertes, onze et douze. Il pourrait les encaisser, mais leurs clients "
             "sont partis. Annuler ces tables : son code est déjà tapé, un seul motif suffit. Chaque produit envoyé "
             "est tracé, et la caisse se ferme.",
     # calé sur la voix : la bulle sur « Il pourrait les encaisser », « Annuler ces tables » sur ses mots, le motif
     # sur « un seul motif suffit », la page qui se recharge sur « et la caisse se ferme ».
     'gestes': [ouvrir('t22-refus'), pause(0.3), anneau('#t22-refus-c', d=1.6), pause(0.4),
                curseur('#t22-refus-ok', d=0.4), bulle('b-voir', '#t22-refus-ok', cote='bas', d=2.6), pause(2.1)]
               + touche('#t22-refus-autre', fermer('t22-refus'), ouvrir('t22-ann', decale=0.1), d=0.5)
               + [pause(0.2), curseur('#t22-ann-m-m2', d=0.5),
                  bulle('b-trace', '#t22-ann-m-kbs', cote='bas', d=2.3), pause(1.8)]
               # « Client parti » : les tables sont annulées, la caisse se ferme, la page se recharge (une nouvelle
               # session, en contrôle d'ouverture : la fenêtre du code s'ouvre d'elle-même)
               + touche('#t22-ann-m-m2', fermer('t22-ann'), fermer('t22-f2'), vue('t22-plan2', 'pos', decale=0.4),
                        classe('#' + POS, retirer=['avec-emp']), d=0.4)
               + [pause(0.2), ouvrir('t22-codeo'), reaction('r-ferme', d=2.2), pause(0.9)]},
    # 5. Le lendemain : Prisca tape son code ; le fond compté la veille est inscrit ; « J'ouvre la caisse ».
    {'temps': 3, 'titre': 'Le lendemain, le fond repris',
     'texte': 'Son code, puis « J\'ouvre la caisse » : 5 touches. Le fond compté la veille est déjà inscrit.',
     'voix': "Le lendemain matin, la fenêtre du code attend toujours. Prisca, la caissière, tape le sien : le fond "
             "compté la veille est déjà inscrit, vingt-cinq mille francs CFA. J'ouvre la caisse : cinq touches, et le "
             "plan se verrouille.",
     # calé sur la voix : le code sur « tape le sien », le fond sur « vingt-cinq mille », « J'ouvre la caisse » sur
     # ses mots, la phrase d'état sur « le plan se verrouille ».
     'gestes': [classe('#tu-perso', ajouter=['t22-prisca']), pause(0.9), anneau('#t22-codeo-titre', d=1.3)]
               + taper('t22-codeo', CODE_P, d=0.26)
               + [fermer('t22-codeo'), *employe(NOM_P, 't22-prisca'), ouvrir('t22-ouv', avec=True, decale=0.1),
                  pause(0.2), curseur('#t22-ouv-fond', fx=0.6, d=0.3), anneau('#t22-ouv-fond', d=1.0),
                  bulle('b-fond', '#t22-ouv-fond', cote='bas', d=2.4, avec=True, decale=0.3), pause(0.6)]
               + touche('#t22-ouv-ok', fermer('t22-ouv'), classe('#' + POS, retirer=['avec-emp', 't22-prisca']),
                        classe('#t22-plan2-ecran', ajouter=['ouverte']), d=0.4)
               + [pause(0.4), anneau('#t22-plan2-etat', d=1.1), pause(0.6)]},
    # 6. Le rapport de la session, dans la gestion de la manager.
    {'temps': 3, 'titre': 'Le rapport de la session',
     'texte': 'Point de Vente › Analyse › Rapport de session : tables, personnes, ventes sans table, annulations.',
     'voix': "Dans la gestion, Edwige, la manager, ouvre le rapport de la session. Les paiements, puis onze tables, "
             "trente-trois personnes, aucune vente sans table. Et les sept annulations du jour, avec leur motif et qui "
             "les a autorisées, même celle arrivée sans code.",
     # calé sur la voix : le rapport sur « ouvre le rapport », les paiements, puis les tables et les personnes, les
     # annulations sur « les sept annulations », la ligne sans code sur « même celle arrivée sans code ».
     'gestes': [pause(0.7), montrer('#t22-pdf', d=0.5, y=0),
                classe('#tu-perso', ajouter=['t22-edwige'], retirer=['t22-prisca'], avec=True),
                pause(2.0), curseur('#t22-rp-pai', fx=0.3, d=0.5), anneau('#t22-rp-pai', d=1.2),
                # la page défile, puis la caméra s'approche, le haut du cadre sous la barre de la visionneuse (son nom
                # de fichier n'est pas coupé) ; la page défile encore sous la caméra jusqu'aux annulations, sans que
                # son bas paraisse (le tableau du contrôle de session, avec « out », reste hors cadre : écart)
                defiler('#t22-pdf-defil', -250, d=0.5), zoom('#t22-rp-tp', s=1.5, fy=0.36, d=0.6),
                curseur('#t22-rp-pers', fx=0.75, d=0.4), anneau('#t22-rp-pers', d=1.2),
                defiler('#t22-pdf-defil', -640, d=0.8), pause(2.0),
                curseur('#t22-rp-sc', fx=0.3, d=0.4),
                bulle('b-sans-code', '#t22-rp-sc', cote='bas', d=2.5), pause(1.9), dezoom(d=0.5),
                reaction('r-rapport', d=2.2, avec=True), pause(0.6)]},
]

TUTORIEL = {
    'slug': 't22-restaurant-fermer-la-caisse',
    'profil': 't22_restaurant_fermer_la_caisse',
    'numero': 22,
    'titre': 'Fermer la caisse',
    'fonction': 'Fermeture contrôlée',
    'personnage': demo.POSTES_RESTO['chef'],
    'accroche': {
        'kicker': 'En fin de service',
        # Les douleurs : docs/PERIMETRE_FONCTIONNEL_RESTAURANT.md:574 (à la fermeture, un bouton annule toutes les
        # tables ouvertes d'un coup, C30 ; « précisément pour les additions oubliées »), :578 (espèces ouvertes à tout
        # employé identifié, C11, C57), :536 (REST-25 : AITE HOUSE compte des additions, pas des tables ni des
        # personnes), :493 (REST-22 : le rapport « Détails des ventes » n'a aucune rubrique d'annulations).
        'question': 'Qui *ferme* la caisse ?',
        'douleurs': [('corbeille', 'Un bouton annule toutes les tables ouvertes, sans motif'),
                     ('interrogation', 'Des additions oubliées au moment de fermer'),
                     ('pieces', 'Entrer ou sortir des espèces : ouvert à tous'),
                     ('graphe', 'Le rapport du soir compte des additions, pas des personnes'),
                     ('liste', 'Aucune annulation dans le rapport de fermeture')],
        'voix': "Vingt-deux heures trente : qui ferme la caisse ? Et les tables restées ouvertes ? Trop souvent, un seul "
                "bouton les efface toutes, sans motif ni trace.",
    },
    'revelation': {
        # regles.py:41-42 ; S/overrides/closing_popup.js:54-79 ; R/views/report_saledetails.xml:13-78.
        'promesse': 'Le chef de salle ferme avec son code ; aucune table ne part sans motif ; le rapport compte tables, '
                    'personnes et annulations.',
        'voix': "Avec Aïte haousse, le chef de salle ferme avec son code, aucune table ne part sans motif, et le rapport "
                "compte les personnes et les annulations.",
    },
    'temps': ['Le code', 'Les espèces', 'Les tables', 'Lendemain et rapport'],
    'app': POS,
    'ecran': ECRAN,
    'css': CSS,
    'vues_initiales': {'pos': 't22-plan'},
    'bulles': {
        # messages.js:35 (R13) ; pos_session.py:248-256 ; regles.py:42 ; rec R10.
        'b-r13': 'Le code d\'une caissière ou d\'un serveur : « %s »' % MESSAGES_RESTO['R13'],
        # messages.js:39 (R15) ; regles.py:41 ; pos_session.py:324-341 (vérifié par le serveur aussi).
        'b-r15': 'Pour une caissière ou un serveur : « %s »' % MESSAGES_RESTO['R15'],
        # S/overrides/closing_popup.js:36-53 ; regles.py:43 ; messages.js:36-38 (R14).
        'b-r14': 'Un écart au-delà du maximum réglé : seul le manager peut fermer.',
        # S/overrides/closing_popup.js:65-68 (la liste des commandes).
        'b-voir': '« %s » ouvre la liste des commandes : on peut encore les encaisser.' % TEXTES_RESTO['voirLesTables'],
        # R/models/pos_order.py:669-689 ; R/models/restaurant_annulation.py:28 ; rec R42.
        'b-trace': 'Chaque produit envoyé est tracé : « %s », autorisé par %s.' % (demo.MOTIFS_RESTO[1], NOM_L),
        # O/point_of_sale/models/pos_session.py:381-383 ; N l.271-272.
        'b-fond': 'Le fond proposé : les espèces comptées hier soir à la fermeture.',
        # N l.125-126 ; R/models/restaurant_annulation.py:9-13 ; la trace de t19 (demo.ANNULATIONS_JOUR_RESTO).
        'b-sans-code': '« %s » : arrivé d\'un poste en retard, jamais refusé, toujours tracé.'
                       % _NATURES['retrait_sans_code'],
    },
    'reactions': {
        'r-ferme': 'Un motif, et la caisse est fermée.',
        'r-rapport': ('Tout y est, sans rien recompter.', EDWIGE[0]),
    },
    'etapes': ETAPES,
    'resultats': {
        'titre': 'Fermer, touche par touche',
        'cartes': [
            # N §3 (mesuré par AiteParcoursTour : 11 avec 4 chiffres comptés).
            {'valeur': '7', 'compter': 7, 'unite': 'touches', 'icone': 'cadenas',
             'texte': '+ les chiffres comptés, pour fermer quand tout est encaissé'},
            # N §3 (13 mesurées, 2 tables ouvertes).
            {'valeur': '2', 'compter': 2, 'unite': 'touches', 'icone': 'corbeille',
             'texte': 'de plus pour annuler les tables encore ouvertes, avec un motif'},
            # N §3 (5 le lendemain, fond prérempli).
            {'valeur': '5', 'compter': 5, 'unite': 'touches', 'icone': 'billet',
             'texte': 'pour rouvrir le lendemain, fond déjà inscrit'},
        ],
        'voix': "Sept touches et le comptage pour fermer, deux de plus pour les tables oubliées, cinq pour rouvrir.",
    },
    'cta': {
        'appel': 'Demandez votre démonstration',
        'sous_marque': demo.SOUS_MARQUE_RESTO,
        'suivant': 'Les rapports du restaurant',
        'voix': "Aïte haousse, par Aïte Consulting. Demandez votre démonstration. Prochain tutoriel : les rapports du "
                "restaurant.",
    },
    # La fenêtre « Fermer la caisse » sur la fermeture (capture 15), zoom posé.
    'vignette': {'etape': 4, 'apres': 2.6},
}


def _typo(texte_):
    """Les textes à l'écran écrits ici (pas la voix) : une espace insécable dans les guillemets et avant « : »,
    « ; », « ? », pour qu'un signe ne passe pas seul à la ligne (comme S/utils/messages.js:7-9 ; t17, t19)."""
    for avant, apres in (('« ', '« '), (' »', ' »'), (' :', ' :'), (' ;', ' ;'), (' ?', ' ?')):
        texte_ = texte_.replace(avant, apres)
    return texte_


for _etape in ETAPES:
    _etape['titre'], _etape['texte'] = _typo(_etape['titre']), _typo(_etape['texte'])
TUTORIEL['bulles'] = {_k: _typo(_v) for _k, _v in TUTORIEL['bulles'].items()}
TUTORIEL['reactions'] = {_k: (_typo(_v[0]), _v[1]) if isinstance(_v, tuple) else _typo(_v)
                         for _k, _v in TUTORIEL['reactions'].items()}
for _carte in TUTORIEL['resultats']['cartes']:
    _carte['texte'] = _typo(_carte['texte'])
TUTORIEL['revelation']['promesse'] = _typo(TUTORIEL['revelation']['promesse'])
TUTORIEL['accroche']['question'] = _typo(TUTORIEL['accroche']['question'])
TUTORIEL['accroche']['douleurs'] = [(_i, _typo(_t)) for _i, _t in TUTORIEL['accroche']['douleurs']]
