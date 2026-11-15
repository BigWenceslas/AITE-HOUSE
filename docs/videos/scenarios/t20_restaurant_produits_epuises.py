# -*- coding: utf-8 -*-
"""Tutoriel 20 — Produits épuisés.

Le cinquième des huit tutoriels du restaurant (lot 1 : aite_pos_restaurant, incrément 5, REST-19a et REST-19b
critère 4 ; restaurant SANS hôtel, comme t16 : demo.RESTO, demo.SOCIETE_RESTO). Une bière suivie en stock et
épuisée est refusée à la caisse ; la manager enregistre l'entrée de stock dans la gestion ; la vente repasse sans
recharger la caisse ; le réglage qui commande tout cela.

Personnages : Inès, la serveuse (demo.POSTES_RESTO['serveuse'], code 5913), sert la table 10 (étapes 1, 2 et 4) ;
Edwige, la manager (demo.POSTES_RESTO['manager']), enregistre l'entrée de stock (étape 3 ; le geste prévu pour le
manager : docs/INSTALLATION.md §9.6 point 4, l.339-341 ; recette R72) ; l'administrateur d'Odoo (AITE,
demo.ADMIN_RESTO) montre le réglage (étape 5 ; réglages du Point de Vente réservés à l'administrateur :
docs/INSTALLATION.md §9.5, comme t16). La pastille du haut passe de l'un à l'autre par une classe
(ecrans.css_personnage) ; les réactions sont celles d'Inès. Storyboard : scratchpad videos_resto/storyboards/t20.md
(adapté : voir « Écarts au storyboard »).

Abréviations : R/ = addons/aite_pos_restaurant/ ; S/ = R/static/src/ ; O/ = ../odoo18/addons/ ; C/nn =
captures/restaurant/nn_*.jpg (modèle visuel, jamais incrusté). Les phrases du produit sont relues dans le code au
chargement (garde-fous plus bas) : une phrase changée dans le module fait échouer la construction de la vidéo au
lieu de la rendre fausse.

Le monde rejoué (conditions) :
- le jour de référence de la série, le 14/10/2026, au service du soir (la table 10 ouverte à 19:10) : à midi, la
  table 10 est celle de Loïc (t18, ouverte à 11:52, encaissée avant 13:30 : t19) ; la journée commune est dans
  demo.TABLES_JOUR_RESTO (intégration de t17 à t20) ; aucune date ni heure à l'écran (seules les durées) ;
  la caisse « Restaurant » est ouverte (le matin, par la caissière : t17), salle « Salle », douze tables ;
- la table 10 est ouverte par Inès depuis 25 minutes, pour 4 personnes ; tout y est parti : Pizza Reine (6 000),
  Bière blonde 65 cl × 2 (3 000), Cola 33 cl (1 000) = 10 000 FCFA, dans cet ordre ; le cola est le dernier
  produit ajouté sur ce poste, si bien que la famille « Sodas » est encore choisie quand l'écran s'ouvre (le
  choix d'une famille reste sur le poste : O/point_of_sale/static/src/app/store/pos_store.js:1058-1068) ; plus
  tard, la table compte 20 000 FCFA (t21 l'encaisse : storyboard t21 §0) ;
- seule la table 10 est montrée ouverte sur le plan (le soir, les tables de midi sont encaissées ; t17 à t19 :
  demo.TABLES_JOUR_RESTO) ;
- carte demo.CARTE_RESTO, sans TVA (pas de ligne « Taxes ») ; seules les bières sont suivies en stock ;
- « Bière brune 65 cl » : 0 en stock, et aucune n'est partie sur une table encore ouverte : la manager en
  enregistre 24 (un casier, comme le cas R72), 0 → 24 (ECARTS.md n° 106 : « Mettre la quantité à jour » fixe la
  quantité, il ne l'ajoute pas) ;
- la case « Refuser la vente des produits épuisés » est cochée (d'office : R/models/pos_config.py:37, 103-105) ;
  le poste est en ligne.

Écrans et libellés :

1. Écran de commande de la table 10 (modèles C/06, C/09) : « Plan », onglet « 10 », logo, « Rechercher des
   produits… », code-barres, « I » + « Inès », ≡ (O/pos_restaurant/i18n/fr.po:892 ; O/point_of_sale/i18n/
   fr.po:6956 ; S/overrides/navbar.xml:18-20) ; phrase d'état « Table 10 · ouverte par Inès · 25 min »
   (S/store/pos_store.js:1136-1151 ; S/utils/messages.js:114-116, 165-171 ; S/overrides/product_screen.xml:13-16) ;
   lignes envoyées (pas de barre verte : O/point_of_sale/…/orderline.scss:24-39), « Total » ; « 4 personnes »,
   « Addition », « Client », « Note cuisine » (grisé sans ligne choisie), « Actions » (S/overrides/
   control_buttons.xml:17-34) ; addition rouverte sans ligne choisie : pas de pavé, « J'envoie » gris, « J'encaisse »
   primaire (C/09). Familles (O/point_of_sale/…/product_screen.js:113-152) : de Boisson › Non alcoolisé › Sodas à
   Boisson › Alcoolisé › Bière ; tuiles triées par nom (product_screen.js:417-419), quantité sur la tuile
   (product_card.xml:24) ; la tuile d'un produit épuisé ne se distingue pas (C/09 ; 19c au lot 2). Le toucher de
   « Bière brune 65 cl » passe par aiteGesteAjout (S/overrides/product_screen.js:28-30) et le premier ajout du
   geste est contrôlé (S/store/pos_store.js:1740-1762) : refus R11 sous le titre « Produit épuisé »
   (messages.js:67-69, 93 ; pos_store.js:1701-1705, type « danger » : barre rouge, C/09), rien n'est ajouté
   (return sans ajout, pos_store.js:1759-1762 ; tour R/static/tests/tours/parcours_tour.js:283-286).
2. Nourriture › Pizzas, « Pizza quatre fromages » : un produit sans « Suivre l'inventaire » passe sans lire le
   stock (pos_store.js:1663-1665 ; R77) ; la ligne neuve est choisie, barre verte, pavé, « J'envoie » primaire avec
   « Pizzas 1 » (O/pos_restaurant/static/src/overrides/models/pos_store.js:74-93 ; C/06). « J'envoie » :
   notification « Envoyé : 1 Pizzas. » et retour au plan verrouillé (S/overrides/actionpad_widget.js:24-26, 43-44 ;
   messages.js:103 ; C/07), « Touchez une table, puis tapez votre code. » (messages.js:97), légende
   (messages.js:150-158).
3. Gestion, compte de la manager (barre ecrans.APPS_PROFIL['resto_manager'], avatar « E ») : Point de Vente →
   Produits → la fiche « Bière brune 65 cl ». Modèle visuel : captures de référence prises sur une copie jetable de
   la base du restaurant, compte « manager » de la graine (Odoo 18 sans le thème MuK, qui n'habille que les barres),
   le 15/11/2026 : fiche d'une bière suivie, assistant, fiche après « Appliquer ». Libellés : panneau « Nouveau »,
   fil « Produits » / nom, engrenage, pagination ; boutons intelligents « Disponible », « Prévisions »
   (O/stock/views/product_views.xml:414-440 ; O/stock/i18n/fr.po:6104, 678), « Documents » (O/product/i18n/
   fr.po:1372), « Règles de réapprovisionnement » (stock fr.po:7859), « Entrée : » / « Sortie : » (stock fr.po:
   684, 735) ; en-tête « Mettre la quantité à jour », « Réapprovisionner » (O/stock/views/product_views.xml:404-412 ;
   stock fr.po:10634, 7874), « Imprimer les étiquettes » (O/product/i18n/fr.po:2657) ; feuille « Produit »
   (product fr.po:2686), étoile, nom, « Ventes », « Achats » (product fr.po:3177, 3018), « Point de Vente »
   (point_of_sale fr.po:5662) ; onglets « Informations générales », « Ventes », « Point de Vente », « Inventaire »
   (product fr.po:1637, 1926) ; « Type de produit » : « Biens », « Service », « Combo » (product fr.po:2915, 1666,
   3223, 901) ; « Politique de facturation » « Quantités commandées » (O/sale/i18n/fr.po:3278, 3979) ; « Suivre
   l'inventaire » ☑ (stock fr.po:10252) ; « Vous pouvez facturer des biens avant qu'ils ne soient livrés. » (sale
   fr.po:6110) ; « Prix de vente » 1 500,00 FCFA, « Taxes de vente », « Coût » 700,00 FCFA, « Taxes d'achat »
   (product fr.po:3193, 1052 ; O/account/i18n/fr.po:13836, 13006 ; vides : société sans TVA, DESIGN.md),
   « Catégorie » « Boisson / Alcoolisé / Bière » (product fr.po:832 ; INSTALLATION.md §9.6 point 2),
   « Référence », « Code-barres » (product fr.po:3080, 741). Pagination « 3 / 18 » : les 18 articles de la carte
   proposés en caisse (filtre d'office de l'action : O/point_of_sale/views/product_view.xml:20-24), rangés par nom
   (O/product/models/product_template.py:22). L'assistant « Changer la quantité de produits » (nom de l'action,
   stock fr.po:1814 ; capture), « Nouvelle quantité disponible » préremplie avec le stock (0,00 ; O/stock/wizard/
   stock_change_product_qty.py:21-23 ; capture), « Appliquer » (primaire), « Ignorer » (stock fr.po:5782, 1334,
   3220) ; après « Appliquer », la fiche affiche « 24,00 » « Disponible » et « Prévisions » (capture). On passe de
   la caisse à la fiche par un fondu (le clic sur une application ouvre son tableau de bord, que l'on ne rejoue
   pas : README, pièges de t16) ; l'anneau désigne « Produits » dans la barre, la légende donne le chemin.
4. La caisse, six minutes plus tard : plan, table 10 verte « 31 min » ; « Table 10 — votre code » (messages.js:73 ;
   S/components/code_popup/code_popup.xml:10-37 ; une table occupée n'a pas l'étape des personnes :
   pos_store.js:897-907) ; l'écran de commande relit le stock en s'ouvrant (pos_store.js:491-493), « Pizzas » est
   encore choisie ; Boisson › Alcoolisé › Bière ; « Bière brune 65 cl » deux fois : la ligne neuve, 2,00, total
   20 000 FCFA, « J'envoie » avec « Bière 2 » ; « Envoyé : 2 Bière. », plan.
5. Réglages du Point de Vente (compte de l'administrateur, avatar « A », barre ecrans.APPS_PROFIL['resto_admin']),
   même page que t16 (modèle C/25), défilée jusqu'à « Refuser la vente des produits épuisés » ☑ et sa phrase
   AIDE_REFUS_EPUISE (R/models/pos_config.py:59-67, 103-105 ; R/views/res_config_settings_views.xml:56-60).

Règles dites par la voix, les bulles, les réactions et les résultats :
- avant AITE, la caisse prend une bouteille qu'on n'a plus et le stock ne baisse qu'au paiement :
  docs/PERIMETRE_FONCTIONNEL_RESTAURANT.md:448 (C39, C40), :597 ;
- refus, « rien n'est ajouté », le message dit quoi faire : R11 ; recette R75 (recette/cas_de_test.py:1294-1300) ;
- le toucher, le code-barres, le pavé, la variante choisie : notes de version §2 l.138-139 ; S/overrides/
  product_screen.js:28-36 ; S/overrides/order_summary.js:66-89 ; S/store/pos_store.js:1795-1817 ;
- un plat, une pizza, un café ne sont jamais refusés : pos_store.js:1663-1665 ; R77 ; AIDE_REFUS_EPUISE ;
- la vente repasse sans recharger la caisse : R76 (cas_de_test.py:1301-1305), notes §2 l.140-141 ; un produit
  refusé a un reste connu de 0 : la caisse relit le stock avant de décider (pos_store.js:1638-1698) ;
- ce qui est parti sur les additions ouvertes, toutes caisses de l'entrepôt, est déduit : R/models/
  product_product.py:2-11, 51-73 ; R78 ;
- la saisie de stock est datée et signée : R73 (cas_de_test.py:1286-1289) ;
- le réglage est coché d'office et ne touche que les produits suivis ; le stock de départ avant le premier
  service : AIDE_REFUS_EPUISE, pos_config.py:37 ; INSTALLATION.md §9.6 point 4 ;
- hors connexion, la caisse vend sans contrôler le stock : pos_store.js:1615-1617, 1666-1667 (Q59) ; notes §7
  l.526-528 ; R79 ;
- résultats : 1 touche mesurée (notes §3 l.254, AiteParcoursTour) ; 4 gestes contrôlés (notes §2 l.138-139) ;
  60 secondes et 2 bouteilles (pos_store.js:83-86 : MEMOIRE_STOCK, SEUIL_STOCK ; SPEC partie 0.3, T20).

Écarts au storyboard :
- l'équipe est celle de demo.EQUIPE_RESTO : Edwige, manager (au lieu du nom proposé par le storyboard, déjà dans
  le dépôt) ;
- étape 3 écrite d'après les captures de référence prises pour ce tutoriel (le storyboard demandait de la
  prendre avant d'écrire) : le bouton intelligent est « Prévisions », et non « Prévu » ; les boutons intelligents
  sont dans le panneau, à côté du fil d'Ariane ; « Documents », « Règles de réapprovisionnement » et « Entrée :
  / Sortie : » en plus ; le titre de l'assistant est « Changer la quantité de produits » ;
- étape 1 : la famille « Sodas » encore choisie à l'ouverture (dernier produit ajouté), puis Alcoolisé › Bière ;
- seule la table 10 est ouverte sur le plan ;
- la réaction de fin vient à l'étape 4 (Inès), l'étape 5 étant jouée sous le compte de l'administrateur ;
- la bulle « saisie datée et signée » est gardée (recette R73) ;
- le personnage est Inès ; la pastille passe à Edwige (étape 3), revient à Inès (étape 4), puis à
  l'administrateur (étape 5) ;
- voix plus longues que celles du storyboard aux étapes 2 à 5 (Kokoro dit environ 17 caractères par seconde : les
  gestes auraient tourné plus de trois secondes sans voix) ; la bulle des postes est posée sous les tuiles, pour
  laisser voir la bière brune et sa quantité ; au zoom de l'étape 1, le curseur quitte la tuile.

Relecture adverse (15/11/2026) :
- gestes recalés sur la voix, d'après les pauses mesurées dans chaque piste (ffmpeg silencedetect) : l'image avait
  jusqu'à 3 s d'avance sur la voix aux étapes 2, 3 et 5 (« J'envoie » touché 2,4 s avant d'être dit, la bulle des
  gestes refermée quand la voix en parlait, l'assistant ouvert quand la voix disait encore « zéro disponible », la
  bulle « sans réseau » pendant « sinon ces bières seront refusées ») ; étape 1 : l'addition (anneau et bulle « Ni
  ligne, ni montant ») quand la voix dit « rien ne s'ajoute », puis le message (zoom) quand elle dit « le message dit
  quoi faire » ; étape 3 : un anneau sur le nom du produit quand la voix dit « ouvre la fiche » ; étape 4 : « Puis
  j'envoie » à la fin, au moment du toucher ;
- accroche : les cartes « Le stock ne baisse qu'à l'addition payée » et « Le stock caché dans la fiche du produit »
  sont retirées (deux constats que le lot 1 ne change pas ; voir le commentaire des douleurs) ;
- résultats : « 60 secondes au plus : l'âge du stock sur lequel la caisse décide » (la mémoire vieillit sans être
  relue, la caisse ne s'en sert plus passé 60 s : pos_store.js:1638-1644) ; la voix dit « jamais une décision sur un
  stock de plus d'une minute » ;
- bulle et voix de l'étape 4 : « le stock enregistré », et non « le stock compté » (ECARTS.md n° 106) ;
- étape 5 : zoom 1,33 (à 1,2 le haut du navigateur et le fond se voyaient : la caméra ne peut pas couvrir la hauteur
  à moins de 1,32) et bulles à gauche, sur la barre des réglages (à droite, elles sortaient du cadre).

Mise en forme propre à ce tutoriel (clé « css ») : deux colonnes de gauche dans la même case de la grille (l'addition
avant et après le premier produit touché, comme t17), la pile des familles et des tuiles, l'addition qui défile
jusqu'à la ligne choisie (Odoo la fait venir à l'écran), la fiche produit et l'assistant de la gestion (champ
sélectionné à l'ouverture, trait primaire au focus, comme la capture), les pastilles du personnage. Contraste WCAG AA
du contrôle de HyperFrames : « % », « Prix », la quantité des tuiles (comme t17), « Note cuisine » et « J'envoie »
grisés passent au gris atténué d'Odoo #6C757D (au lieu de #8C959D : 3,0:1 et 2,9:1). La page des réglages défile
jusqu'à -690 px : la rangée du refus se lit en entier et la page reste pleine jusqu'en bas, comme dans Odoo.
"""

import ast
import os
import re
import unicodedata
import xml.etree.ElementTree as ET

import demo
from ecrans import (APPS_PROFIL, ICONES, MENUS_MUK, MESSAGES_RESTO, NBSP, TEXTES_RESTO, TITRES_RESTO, _odoo_dir,
                    assistant, bloc_reglages, css_personnage, duree_resto, e, entier, entree, etat_commande,
                    etiquettes, fcfa, fenetre_muk, fenetre_resto, lien_fleche, navigateur, page_reglages, reglage,
                    resto_code, resto_commande, resto_familles, resto_ligne, resto_notification, resto_plan,
                    resto_salle, resto_tuiles, vue_libre)
from marketing import bulle, dezoom, reaction, zoom
from moteur import anneau, cacher, classe, clic, curseur, defiler, fermer, montrer, notifier, ouvrir, pause, saisir, \
    texte, vue

RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
R = os.path.join(RACINE, 'addons', 'aite_pos_restaurant')
S = os.path.join(R, 'static', 'src')


def _lire(*chemin):
    with open(os.path.join(*chemin), encoding='utf-8') as f:
        return f.read()


def _une_ligne(texte_):
    return ' '.join((texte_ or '').split())


def _source(relatif, nom):
    """Une constante d'un fichier Python du module, lue sans importer Odoo (comme t16)."""
    for noeud in ast.parse(_lire(R, relatif)).body:
        if isinstance(noeud, ast.Assign) and any(getattr(c, 'id', None) == nom for c in noeud.targets):
            return ast.literal_eval(noeud.value)
    raise ValueError('t20 : %s introuvable dans %s' % (nom, relatif))


# ============================================================== garde-fous --
# 1. Les textes de la caisse : chaque phrase montrée est relue dans S/utils/messages.js (source JS, espaces ramenées
#    à une seule), puis comparée à ce que les composants d'ecrans.py affichent.
_JS = _une_ligne(_lire(S, 'utils', 'messages.js'))


def _js(extrait, **valeurs):
    """Le texte d'un littéral de messages.js (``extrait`` doit y être mot pour mot), ``${ESP}`` → espace insécable,
    ``${x}`` → ``valeurs['x']`` (même lecture que t17)."""
    assert extrait in _JS, ('t20 : texte changé dans messages.js', extrait)
    t = re.search(r'(["`])(.*)\1', extrait).group(2).replace('${ESP}', NBSP)
    for cle_, val in valeurs.items():
        t = t.replace('${%s}' % cle_, str(val))
    assert '${' not in t, extrait
    return t


BRUNE = 'Bière brune 65 cl'
# R11 est écrit sur deux littéraux concaténés (messages.js:67-69) : relus l'un après l'autre.
assert (_js('R11: (produit) => `Plus de ${produit} en stock. Si la bouteille est bien là, demandez au manager `',
            produit=BRUNE)
        + _js('`d\'enregistrer l\'entrée de stock${ESP}: la vente repassera aussitôt.`')) \
    == MESSAGES_RESTO['R11'](BRUNE)
assert _js('produitEpuise: "Produit épuisé"') == TITRES_RESTO['produitEpuise']
assert _js('table: (numero) => `Table ${numero} — votre${ESP}code`', numero=10) == TITRES_RESTO['table'](10)
assert _js('envoye: (compte) => `Envoyé${ESP}: ${compte}.`', compte='1 Pizzas') == TEXTES_RESTO['envoye']('1 Pizzas')
assert _js('planEtat: "Touchez une table, puis tapez votre code."') == TEXTES_RESTO['planEtat']
assert _js('addition: "Addition"') == TEXTES_RESTO['addition']
assert _js('`${nombre} personnes`', nombre=4) == TEXTES_RESTO['personnes'](4)
assert ' · '.join((_js('table: (numero) => `Table ${numero}`', numero=10),
                   _js('ouvertePar: (nom) => `ouverte par ${nom}`', nom='Inès'),
                   _js('return `${minutes} min`;', minutes=25))) == etat_commande(10, 'Inès', 25)
assert [_js('texte: `Gris${ESP}: libre`'), _js('texte: `Vert${ESP}: ouverte`'),
        _js('texte: `Pastille rouge${ESP}: pas encore envoyé`')] == \
    [t for c, t in TEXTES_RESTO['legendeParties'](demo.DELAI_ORANGE) if c != 'orange']

# 2. Le comportement que la vidéo montre (S/store/pos_store.js, S/overrides/*.js).
_PS = _une_ligne(_lire(S, 'store', 'pos_store.js'))
for _extrait, _pourquoi in (
        ('const MEMOIRE_STOCK = 60000;', 'mémoire de 60 s (résultats)'),
        ('const SEUIL_STOCK = 2;', 'seuil de 2 (résultats)'),
        ('return this.aiteActif && Boolean(this.config.aite_refus_epuise);', 'le réglage (étape 5)'),
        ('if (name === "ProductScreen") { this.aiteRafraichirStock(); // sans attendre (T20)',
         "relecture à l'ouverture de l'écran de commande (étape 4)"),
        ('return true; // plat, pizza, café : jamais refusé, sans lire le stock', 'plats jamais refusés (étape 2)'),
        ('return true; // Q59 : hors connexion, on vend', 'hors connexion, on vend (étape 5)'),
        ('this.notification.add(MESSAGES.R11(product.display_name || product.name), { type: "danger", '
         'title: TITRES.produitEpuise, });', 'R11 en notification rouge, titrée (étape 1)'),
        ('if (!(await this.aiteProduitDisponible(order, product, this.aiteQuantiteAjoutee(vals, opts)))) { '
         'this.aiteNotifierEpuise(product); return; }', 'rien n\'est ajouté (étape 1)')):
    assert _extrait in _PS, ('t20 : pos_store.js a changé', _pourquoi)
_PSCR = _une_ligne(_lire(S, 'overrides', 'product_screen.js'))
for _geste in ('addProductToOrder', '_barcodeProductAction', '_barcodeGS1Action'):
    assert ('async %s(' % _geste) in _PSCR and ('this.pos.aiteGesteAjout(() => super.%s(...arguments))' % _geste) in \
        _PSCR, ('t20 : geste contrôlé changé', _geste)
assert 'this.pos.aiteNotifierEpuise(product);' in _lire(S, 'overrides', 'order_summary.js'), 't20 : pavé non contrôlé'
assert ('this.pos.notification.add(TEXTES.envoye(compte), { type: "info" }); this.pos.showScreen("FloorScreen");'
        in _une_ligne(_lire(S, 'overrides', 'actionpad_widget.js')))
# Ce qui est parti sur les additions ouvertes est retiré du stock (R/models/product_product.py:51-73).
_PP = _une_ligne(_lire(R, 'models', 'product_product.py'))
assert "('order_id.state', '=', 'draft')" in _PP and "('aite_qte_envoyee', '>', 0)" in _PP and \
    'quantite - partis.get(produit_id, 0.0)' in _PP, 't20 : le disponible ne déduit plus ce qui est parti'

# 3. Le réglage : la constante Python et la vue (comme t16), coché d'office.
AIDE_REFUS_EPUISE = _source('models/pos_config.py', 'AIDE_REFUS_EPUISE')
AIDE_MODE = _source('models/pos_config.py', 'AIDE_MODE')
AIDE_VENTE_SANS_TABLE = _source('models/pos_config.py', 'AIDE_VENTE_SANS_TABLE')
AIDE_DELAI = _source('models/pos_config.py', 'AIDE_DELAI').format(delai='%d minutes' % demo.DELAI_ORANGE)
assert _source('models/pos_config.py', 'NOM_CAISSE') == demo.CAISSE_RESTO
assert _source('models/pos_config.py', 'NOM_SALLE') == demo.SALLE_RESTO
_REGLAGES_XML = {n.get('id'): n
                 for n in ET.parse(os.path.join(R, 'views', 'res_config_settings_views.xml')).iter('setting')}
for _id_xml, _titre, _aide in (('aite_mode_restaurant', 'Service à table contrôlé', AIDE_MODE),
                               ('aite_delai_alerte', "Délai avant l'orange (minutes)", None),
                               ('aite_vente_sans_table', 'Autoriser la vente sans table', AIDE_VENTE_SANS_TABLE),
                               ('aite_refus_epuise', 'Refuser la vente des produits épuisés', AIDE_REFUS_EPUISE)):
    assert _REGLAGES_XML[_id_xml].get('string') == _titre, ('t20 : libellé changé dans la vue', _id_xml)
    assert _une_ligne(_REGLAGES_XML[_id_xml].get('help')) == (_aide or ''), \
        ('t20 : phrase changée dans la vue', _id_xml)
_PC = _une_ligne(_lire(R, 'models', 'pos_config.py'))
assert "'aite_refus_epuise': True," in _PC and \
    'aite_refus_epuise = fields.Boolean( string="Refuser la vente des produits épuisés", default=True,' in _PC, \
    "t20 : le refus des épuisés n'est plus coché d'office"
# Les mots de la phrase que les bulles reprennent (étape 5).
assert 'Saisissez le stock de départ avant le premier service, sinon ces produits seront refusés.' in AIDE_REFUS_EPUISE
assert 'Les produits sans suivi (plats, pizzas, café) se vendent toujours.' in AIDE_REFUS_EPUISE

# 4. Les mesures et la recette (résultats, bulles).
_NOTES = _lire(RACINE, 'docs', 'NOTES_DE_VERSION_restaurant_lot1.md')
assert '| Serveur — produit épuisé refusé | — | **1** (« Produit épuisé », rien n\'est ajouté) |' in _NOTES
assert ('Un produit suivi en stock et épuisé n\'est pas ajouté (toucher, code-barres,\n  pavé, variante choisie)'
        in _NOTES), 't20 : les quatre gestes contrôlés ont changé dans les notes de version'
assert '**Hors connexion**, on vend sans contrôle de stock' in _NOTES
_RECETTE = _lire(RACINE, 'recette', 'cas_de_test.py')
for _cas in ('"R72"', '"R73"', '"R75"', '"R76"', '"R77"', '"R78"', '"R79"'):
    assert ('(%s, "R"' % _cas) in _RECETTE, ('t20 : cas de recette absent', _cas)
assert "La saisie est datée et porte le nom de celui qui l'a faite." in _RECETTE
assert 'Sans recharger la "\n     "caisse, toucher le produit.' in _RECETTE

# 5. Les libellés d'Odoo (traductions françaises et vues), Odoo étant à côté du dépôt (ecrans.py le lit déjà pour le
#    logo). Ceux de la fiche produit et de l'assistant ont été relevés sur capture (voir l'en-tête).
_PO = {m: _lire(_odoo_dir(), 'addons', m, 'i18n', 'fr.po')
       for m in ('point_of_sale', 'pos_restaurant', 'stock', 'product', 'sale', 'account')}
for _module, _msgs in (
        ('stock', ('Mettre la quantité à jour', 'Réapprovisionner', 'Disponible', 'Règles de réapprovisionnement',
                   "Suivre l'inventaire", 'Changer la quantité de produits', 'Nouvelle quantité disponible',
                   'Appliquer', 'Ignorer', '<span class=\\"o_stat_text\\">Prévisions</span>',
                   '<span class=\\"o_stat_text\\">Entrée :</span>', '<span class=\\"o_stat_text\\">Sortie :</span>')),
        ('product', ('Imprimer les étiquettes', 'Documents', 'Produits', 'Produit', 'Ventes', 'Achats',
                     'Informations générales', 'Inventaire', 'Type de produit', 'Biens', 'Service', 'Combo',
                     'Prix de vente', 'Coût', 'Catégorie', 'Référence', 'Code-barres', 'Nouveau')),
        ('sale', ('Politique de facturation', 'Quantités commandées',
                  "Vous pouvez facturer des biens avant qu'ils ne soient livrés.")),
        ('account', ('Taxes de vente', "Taxes d'achat")),
        ('point_of_sale', ('Point de Vente', 'Rechercher des produits…', 'Client', 'Note cuisine', 'Actions', 'Qté',
                           'Prix')),
        ('pos_restaurant', ('Plan', 'Table'))):
    for _msg in _msgs:
        assert 'msgstr "%s"' % _msg in _PO[_module], ("t20 : libellé d'Odoo introuvable", _module, _msg)
_VUE_STOCK = _une_ligne(_lire(_odoo_dir(), 'addons', 'stock', 'views', 'product_views.xml'))
assert ('<xpath expr="//header/button" position="before"> <button string="Update Quantity" type="object" '
        'name="action_update_quantity_on_hand" invisible="not is_storable"/> <button string="Replenish"'
        in _VUE_STOCK), "t20 : l'en-tête de la fiche produit a changé"

# ============================================================== les données --
INES = next(x for x in demo.EQUIPE_RESTO if x[0] == demo.POSTES_RESTO['serveuse'][0])
EDWIGE = next(x for x in demo.EQUIPE_RESTO if x[0] == demo.POSTES_RESTO['manager'][0])
assert (INES[2], EDWIGE[2]) == ('Serveur', 'Manager')
NOM_I, CODE_I = INES[1], INES[3]
NOM_E = EDWIGE[1]
ADMIN, ROLE_ADMIN, INITIALE_ADMIN = demo.ADMIN_RESTO
TABLE = 10
PERSONNES = 4
DUREE_1 = 25          # minutes : la table 10 au début du tutoriel
DUREE_2 = 31          # six minutes plus tard (étape 4)
ENTREE = 24           # un casier (recette R72)

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
COUT = {nom: cout for nom, _f, _p, cout, _s in demo.CARTE_RESTO}
FAMILLE = {nom: f for nom, f, _p, _c, _s in demo.CARTE_RESTO}
SUIVI = {nom: s for nom, _f, _p, _c, s in demo.CARTE_RESTO}


def cle(nom):
    """« Bière brune 65 cl » → « bierebrune65cl » (comme ecrans.resto_familles)."""
    return ''.join(c for c in unicodedata.normalize('NFD', nom.lower()) if c.isalnum())


def tri(nom):
    """L'ordre de localeCompare (product_screen.js:417-419) : sans accent ni casse."""
    return ''.join(c for c in unicodedata.normalize('NFD', nom.casefold()) if unicodedata.category(c) != 'Mn')


def produits(famille):
    """Les tuiles d'une famille et de ses descendantes, triées par nom."""
    noms = [n for n, _f, _p, _c, _s in demo.CARTE_RESTO if FAMILLE[n] in DESCENDANTES[famille]]
    return [(cle(n), n, COULEUR[FAMILLE[n]]) for n in sorted(noms, key=tri)]


REINE, BLONDE, COLA, FROMAGES = 'Pizza Reine', 'Bière blonde 65 cl', 'Cola 33 cl', 'Pizza quatre fromages'
assert [FAMILLE[x] for x in (REINE, BLONDE, COLA, FROMAGES, BRUNE)] == ['Pizzas', 'Bière', 'Sodas', 'Pizzas', 'Bière']
assert SUIVI[BRUNE] and not SUIVI[FROMAGES], 't20 : la bière brune doit être suivie, la pizza non'
assert [n for _k, n, _c in produits('Bière')] == ['Bière blonde 33 cl', BLONDE, BRUNE]
assert [n for _k, n, _c in produits('Pizzas')] == ['Pizza Margherita', FROMAGES, REINE]
# L'addition : 10 000 au début, 17 000 après la pizza, 20 000 après les deux bières brunes (t21 l'encaisse).
TOTAL_1 = PRIX[REINE] + 2 * PRIX[BLONDE] + PRIX[COLA]
TOTAL_2 = TOTAL_1 + PRIX[FROMAGES]
TOTAL_3 = TOTAL_2 + 2 * PRIX[BRUNE]
assert (TOTAL_1, TOTAL_2, TOTAL_3) == (10000, 17000, 20000)
ENVOI_1 = '1 %s' % FAMILLE[FROMAGES]
ENVOI_2 = '2 %s' % FAMILLE[BRUNE]
# La pagination de la fiche : les articles proposés en caisse (toute la carte), rangés par nom (_order
# « is_favorite desc, name », aucun favori ; base en collation C : l'ordre des octets, celui de sorted).
CARTE = sorted(n for n, _f, _p, _c, _s in demo.CARTE_RESTO)
RANG = CARTE.index(BRUNE) + 1
assert (RANG, len(CARTE)) == (3, 18)


def montant(n):
    """Un montant de la fiche produit d'Odoo : « 1 500,00 FCFA » (capture de référence : « 1 000,00 FCFA »)."""
    return '%s,00%sFCFA' % (entier(n), NBSP)


def quantite(n):
    """« 24,00 », comme le bouton « Disponible » (capture de référence)."""
    return ('%.2f' % n).replace('.', ',')


assert montant(1500) == '1%s500,00%sFCFA' % (NBSP, NBSP)

# ======================================================== l'écran : la caisse --
POS = 't20-pos'
PLAN = resto_plan('t20-plan', resto_salle('t20-plan', {TABLE: ('vert', duree_resto(DUREE_1), None)}),
                  delai=demo.DELAI_ORANGE, salle=demo.SALLE_RESTO)
T10 = '#t20-plan-t%d' % TABLE


def pile(ident, etats, visible=0):
    """Les états successifs des familles et des tuiles, empilés au même endroit (comme t17) : ``etats`` =
    [(chemin, famille des tuiles, {clé: quantité})] ; on passe de l'un à l'autre par cacher / montrer.
    Identifiants : <ident>-e<k>, <ident>-e<k>-fa-f-<famille>, <ident>-e<k>-tu-<produit>(-q)."""
    blocs = []
    for k, (chemin, famille, qtes) in enumerate(etats):
        blocs.append('<div class="t20-et%s" id="%s-e%d">%s%s</div>'
                     % ('' if k == visible else ' masque', ident, k,
                        resto_familles('%s-e%d-fa' % (ident, k), demo.FAMILLES_RESTO, chemin),
                        resto_tuiles('%s-e%d-tu' % (ident, k), produits(famille), qtes)))
    return '<div class="t20-pile">%s</div>' % ''.join(blocs)


def commande(ident, avant, apres, familles):
    """L'écran de commande d'une visite (comme t17) : deux colonnes de gauche dans la même case de la grille —
    ``avant`` (l'addition rouverte, sans ligne choisie : ni pavé, ni « Note cuisine ») et ``apres`` (dès qu'un
    produit est ajouté : ligne choisie, pavé) —, et la pile des familles à droite. Identifiants : <ident>v-…
    (avant), <ident>-… (après), <ident>v-g et <ident>-g (les colonnes)."""
    b = resto_commande(ident, familles_html=familles, tuiles_html='', **apres)
    a = resto_commande(ident + 'v', familles_html='', tuiles_html='', **avant)
    gauche_a = a[a.index('<div class="rs-g">'):a.index('<div class="rs-d">')]
    gauche_a = gauche_a.replace('<div class="rs-g">', '<div class="rs-g" id="%sv-g">' % ident, 1)
    # sans ligne choisie, « Note cuisine » est grisé (O/point_of_sale/…/customer_note_button.xml:7 ; C/09)
    gauche_a = gauche_a.replace('<span class="" id="%sv-note">' % ident, '<span class="gris" id="%sv-note">' % ident, 1)
    assert 'class="gris" id="%sv-note"' % ident in gauche_a
    b = b.replace('<div class="rs-g">', '<div class="rs-g masque" id="%s-g">' % ident, 1)
    return b.replace('<div class="rs-d">', gauche_a + '<div class="rs-d">', 1)


ETAT_1 = etat_commande(TABLE, NOM_I, DUREE_1)
ETAT_2 = etat_commande(TABLE, NOM_I, DUREE_2)


def lignes_envoyees(prefixe, avec_fromages=False):
    noms = [(REINE, 1), (BLONDE, 2), (COLA, 1)] + ([(FROMAGES, 1)] if avec_fromages else [])
    return ''.join(resto_ligne('%s-l%d' % (prefixe, k), nom, q, PRIX[nom]) for k, (nom, q) in enumerate(noms, 1))


# Première visite (étapes 1-2) : « Sodas » encore choisie ; Alcoolisé › Bière (refus) ; Nourriture › Pizzas.
C1 = commande('t20-c1', dict(
    etat=ETAT_1, lignes_html=lignes_envoyees('t20-c1v'), total=fcfa(TOTAL_1), personnes=PERSONNES,
    compteurs=[('Pizzas', 0)], encaisser=True),
    dict(etat=ETAT_1, total=fcfa(TOTAL_2), personnes=PERSONNES, compteurs=[('Pizzas', 1)], initiale=True,
         lignes_html=lignes_envoyees('t20-c1') + resto_ligne('t20-c1-l4', FROMAGES, 1, PRIX[FROMAGES], envoyee=False,
                                                             choisie=True)),
    pile('t20-c1', [(('Boisson', 'Non alcoolisé', 'Sodas'), 'Sodas', {cle(COLA): 1}),
                    (('Boisson', 'Alcoolisé'), 'Alcoolisé', {cle(BLONDE): 2}),
                    (('Boisson', 'Alcoolisé', 'Bière'), 'Bière', {cle(BLONDE): 2}),
                    (('Nourriture',), 'Nourriture', {cle(REINE): 1}),
                    (('Nourriture', 'Pizzas'), 'Pizzas', {cle(REINE): 1})]), )
assert 'class="vue rs-vue initiale" id="t20-c1"' in C1
# Deuxième visite (étape 4) : « Pizzas » encore choisie ; Boisson › Alcoolisé › Bière ; deux bières brunes.
C2 = commande('t20-c2', dict(
    etat=ETAT_2, lignes_html=lignes_envoyees('t20-c2v', True), total=fcfa(TOTAL_2), personnes=PERSONNES,
    compteurs=[('Bière', 0)], encaisser=True),
    dict(etat=ETAT_2, total=fcfa(TOTAL_2 + PRIX[BRUNE]), personnes=PERSONNES, compteurs=[('Bière', 1)],
         lignes_html=lignes_envoyees('t20-c2', True) + resto_ligne('t20-c2-l5', BRUNE, 1, PRIX[BRUNE], envoyee=False,
                                                                   choisie=True)),
    pile('t20-c2', [(('Nourriture', 'Pizzas'), 'Pizzas', {cle(REINE): 1, cle(FROMAGES): 1}),
                    (('Boisson',), 'Boisson', {cle(BLONDE): 2, cle(COLA): 1}),
                    (('Boisson', 'Alcoolisé'), 'Alcoolisé', {cle(BLONDE): 2}),
                    (('Boisson', 'Alcoolisé', 'Bière'), 'Bière', {cle(BLONDE): 2})]))

# Les fenêtres posées sur la caisse.
EPUISE = resto_notification('t20-epuise', MESSAGES_RESTO['R11'](BRUNE), titre=TITRES_RESTO['produitEpuise'],
                            genre='danger')
N1 = resto_notification('t20-n1', TEXTES_RESTO['envoye'](ENVOI_1))
N2 = resto_notification('t20-n2', TEXTES_RESTO['envoye'](ENVOI_2))
CODE = resto_code('t20-code', TITRES_RESTO['table'](TABLE))
CAISSE = fenetre_resto(POS, [PLAN, C1, C2], calques=EPUISE + N1 + N2 + CODE, ecran='commande', onglet=str(TABLE),
                       employe=(NOM_I, NOM_I[0]), avatar=demo.AVATARS_RESTO[NOM_I])

# ============================================ l'écran : la fiche produit (3) --
SVG = {
    # fa-cubes, fa-area-chart, fa-file-text-o, fa-refresh, fa-exchange : les icônes des boutons intelligents (capture)
    'cubes': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round">'
             '<path d="M12 2.8l4.6 2.4v5L12 12.6 7.4 10.2v-5z"/><path d="M7.4 10.2L2.8 12.6v5l4.6 2.4 4.6-2.4"/>'
             '<path d="M16.6 10.2l4.6 2.4v5l-4.6 2.4-4.6-2.4v-5"/><path d="M7.4 5.2L12 7.6l4.6-2.4M12 7.6v5"/></svg>',
    'aire': '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M2 3h1.6v16.4H22V21H2z"/>'
            '<path d="M5 18V12l4-4.5 4 3.5 3.5-5.5L21 9v9z"/></svg>',
    'doc': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round">'
           '<path d="M5 2.8h9.5L19 7.3v13.9H5z"/><path d="M14.5 2.8v4.5H19"/><path d="M8 11h8M8 14h8M8 17h6"/></svg>',
    'cycle': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round">'
             '<path d="M19.5 10A7.8 7.8 0 005.6 7.4"/><path d="M4.5 14a7.8 7.8 0 0013.9 2.6"/>'
             '<path d="M5.2 3.4v4.4h4.4M18.8 20.6v-4.4h-4.4"/></svg>',
    'echange': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" '
               'stroke-linejoin="round"><path d="M3 8h17M15.5 3.5L20 8l-4.5 4.5"/><path d="M21 16H4M8.5 11.5L4 16l4.5 '
               '4.5"/></svg>',
    'etoile': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round">'
              '<path d="M12 2.6l2.9 6.1 6.6.8-4.9 4.6 1.3 6.6L12 17.4l-5.9 3.3 1.3-6.6-4.9-4.6 6.6-.8z"/></svg>',
    'photo': '<svg viewBox="0 0 64 64" fill="#ADB5BD"><path d="M8 18h11l4-6h18l4 6h11v32H8z"/>'
             '<circle cx="34" cy="33" r="10" fill="#fff"/><circle cx="34" cy="33" r="7"/>'
             '<circle cx="47" cy="45" r="11" fill="#fff"/><circle cx="47" cy="45" r="9"/>'
             '<path d="M46 39h2v5h5v2h-5v5h-2v-5h-5v-2h5z" fill="#fff"/></svg>',
}


def _stat(ident, ico, libelle, valeur):
    """Un bouton intelligent du panneau (capture : le libellé en haut, la valeur dessous, en couleur de lien)."""
    return ('<span class="t20-st" id="%s"><span class="t20-st-i">%s</span><span class="t20-st-t"><span>%s</span>'
            '<b id="%s-v">%s</b></span></span>' % (ident, SVG[ico], e(libelle), ident, e(valeur)))


def _ch(libelle, valeur_html='', aide=False, ident=None):
    q = '<sup class="t20-q">?</sup>' if aide else ''
    return ('<div class="t20-ch"%s><span class="t20-l">%s%s</span><span class="t20-v">%s</span></div>'
            % (' id="%s"' % ident if ident else '', e(libelle), q, valeur_html))


def _case(coche=True, ident=None):
    return ('<span class="rg-case%s t20-case"%s>%s</span>'
            % (' coche' if coche else '', ' id="%s"' % ident if ident else '', ICONES['coche']))


def _radio(libelle, choisi=False):
    return '<span class="t20-radio%s"><i></i>%s</span>' % (' choisi' if choisi else '', e(libelle))


def fiche_produit(ident, nom, dispo):
    """La fiche produit d'Odoo 18 (O/product/views/product_template_views.xml, O/stock/views/product_views.xml:
    396-490, O/sale, O/point_of_sale) telle que la capture de référence la montre au compte du manager : panneau
    (« Nouveau », fil d'Ariane, engrenage, cinq boutons intelligents, pagination), en-tête (trois boutons gris),
    feuille (« Produit », étoile, nom, cases, photo, onglets, champs). Identifiants : <id>-produits (le menu),
    <id>-dispo (bouton « Disponible », valeur <id>-dispo-v), <id>-prev(-v), <id>-maj (« Mettre la quantité à jour »),
    <id>-suivi (« Suivre l'inventaire »), <id>-nom (le nom du produit)."""
    stats = (_stat(ident + '-dispo', 'cubes', 'Disponible', quantite(dispo))
             + _stat(ident + '-prev', 'aire', 'Prévisions', quantite(dispo))
             + _stat(ident + '-docs', 'doc', 'Documents', '0')
             + _stat(ident + '-regles', 'cycle', 'Règles de réapprovisionnement', '0')
             + '<span class="t20-st"><span class="t20-st-i">%s</span><span class="t20-st-t"><span>Entrée : <b>0</b>'
               '</span><span>Sortie : <b>0</b></span></span></span>' % SVG['echange'])
    cp = ('<div class="cp t20-cp"><span class="bt contour">Nouveau</span><div class="fil">'
          '<span class="parent">Produits</span><span class="ref">%s <span class="fe-eng">%s</span></span></div>'
          '<div class="t20-stats">%s</div><span class="pager">%d / %d</span><span class="fe-nav">‹</span>'
          '<span class="fe-nav">›</span></div>' % (e(nom), ICONES['engrenage'], stats, RANG, len(CARTE)))
    entete = ('<div class="t20-bande"><span class="bt gris" id="%s-maj">Mettre la quantité à jour</span>'
              '<span class="bt gris">Réapprovisionner</span><span class="bt gris">Imprimer les étiquettes</span></div>'
              % ident)
    tete = ('<div class="t20-tete"><div><div class="t20-type">Produit</div><div class="t20-nom">'
            '<span class="t20-etoile">'
            '%s</span><span id="%s-nom">%s</span></div><div class="t20-cases"><span>%sVentes</span><span>%sAchats</span>'
            '<span>%sPoint de Vente<sup class="t20-q">?</sup></span></div></div><div class="t20-photo">%s</div></div>'
            % (SVG['etoile'], ident, e(nom), _case(), _case(), _case(), SVG['photo']))
    onglets_ = ('<div class="onglets t20-onglets"><span class="onglet actif">Informations générales</span>'
                '<span class="onglet">Ventes</span><span class="onglet">Point de Vente</span>'
                '<span class="onglet">Inventaire</span></div>')
    gauche = (_ch('Type de produit', _radio('Biens', True) + _radio('Service') + _radio('Combo'), aide=True)
              + _ch('Politique de facturation', e('Quantités commandées'), aide=True)
              + _ch("Suivre l'inventaire", _case(ident=ident + '-suivi-case'), aide=True, ident=ident + '-suivi')
              + '<div class="t20-astuce">%s</div>' % e("Vous pouvez facturer des biens avant qu'ils ne soient livrés."))
    droite = (_ch('Prix de vente', e(montant(PRIX[nom])), aide=True) + _ch('Taxes de vente', aide=True)
              + _ch('Coût', e(montant(COUT[nom])), aide=True) + _ch("Taxes d'achat", aide=True)
              + _ch('Catégorie', e('Boisson / Alcoolisé / Bière')) + _ch('Référence') + _ch('Code-barres'))
    feuille = ('<div class="t20-feuille">%s%s<div class="t20-cols"><div>%s</div><div>%s</div></div></div>'
               % (tete, onglets_, gauche, droite))
    contenu = ('%s<div class="t20-cadre" data-layout-allow-overflow data-layout-allow-occlusion>%s%s</div>'
               % (cp, entete, feuille))
    return vue_libre(ident, contenu, initiale=True, fond='gris')


assert FAMILLE[BRUNE] == 'Bière' and DESCENDANTES['Boisson'][:3] == ['Boisson', 'Alcoolisé', 'Bière']
FICHE = fiche_produit('t20-fp', BRUNE, 0)
# L'assistant « Changer la quantité de produits » : le champ prérempli avec le stock (0,00), sélectionné à
# l'ouverture comme sur la capture ; « Appliquer » primaire, « Ignorer ».
CORPS_QTE = ('<div class="t20-m-ch"><span class="t20-m-l">Nouvelle quantité disponible<sup class="t20-q">?</sup></span>'
             '%s</div>' % entree('t20-nqd', '', quantite(0), classe='entree t20-m-in'))
QTE = assistant('t20-qte', 'Changer la quantité de produits', CORPS_QTE,
                [('t20-appliquer', 'Appliquer', 'primaire', None), ('t20-ignorer', 'Ignorer', 'gris', None)],
                haut=300, largeur=1180)
# la valeur préremplie est sélectionnée à l'ouverture (capture) : la saisie la remplace
QTE = QTE.replace('<span class="val" id="t20-nqd-val">', '<span class="val t20-sel" id="t20-nqd-val">', 1)
assert 't20-sel' in QTE
GESTION = fenetre_muk('t20-gest', 'Point de Vente', MENUS_MUK['point_de_vente'], [FICHE], actif='Produits',
                      societe=demo.SOCIETE_RESTO, initiale=NOM_E[0], avatar=demo.AVATARS_RESTO[NOM_E],
                      apps=APPS_PROFIL['resto_manager'], app_active='Point de Vente', calques=QTE)
GESTION = GESTION.replace('class="app muk"', 'class="app muk masque"', 1)
GESTION = GESTION.replace('<span class="menu actif">Produits</span>',
                          '<span class="menu actif" id="t20-gest-produits">Produits</span>', 1)
assert 'id="t20-gest-produits"' in GESTION

# =================================================== l'écran : le réglage (5) --
# La page des réglages de t16 (même ordre, mêmes phrases, relues plus haut), sous le compte de l'administrateur.
SALLE_HTML = ('<div class="rg-ligne"><span>Salles</span>%s</div>%s'
              % (etiquettes([demo.SALLE_RESTO]), lien_fleche('Salles')))
REGLAGES = bloc_reglages('Mode restaurant', [
    reglage('t20-ebr', 'Est un bar/restaurant', case=True),
    reglage('t20-stc', 'Service à table contrôlé', aide=AIDE_MODE, case=True),
    reglage('t20-delai', "Délai avant l'orange (minutes)",
            contenu='<div class="rg-champ">%d</div><div class="rg-aide">%s</div>' % (demo.DELAI_ORANGE, e(AIDE_DELAI))),
    reglage('t20-vst', 'Autoriser la vente sans table', aide=AIDE_VENTE_SANS_TABLE, case=False),
    reglage('t20-refus', 'Refuser la vente des produits épuisés', aide=AIDE_REFUS_EPUISE, case=True),
    reglage('t20-plan-sal', 'Plan des salles & des tables',
            aide='Créer un plan de salle et attribuer des commandes à des tables', contenu=SALLE_HTML, point=True),
    reglage('t20-emporter', 'Manger sur place / À emporter',
            aide="Ajuster la taxe selon que les clients mangent sur place ou qu'ils optent pour un plat à emporter.",
            case=False),
    reglage('t20-impression', 'Impression du reçu avant le paiement',
            aide="Autoriser l'impression du reçu avant le paiement", case=True),
    reglage('t20-partage', "Autoriser le partage d'addition", aide='Partager le total ou les lignes de commande',
            case=True, point=True),
], identifiant='t20-bloc')
PAGE = page_reglages('t20-rg', [('Paramètres généraux', 'parametres'), ('Inventaire', 'inventaire'),
                                ('Facturation', 'facturation'), ('Employés', 'employes'),
                                ('Point de Vente', 'point-de-vente')],
                     'Point de Vente', ('Point de Vente', demo.CAISSE_RESTO, '+ Nouvelle boutique'), [REGLAGES],
                     initiale=True)
ADMIN_ECRAN = fenetre_muk('t20-adm', 'Point de Vente', MENUS_MUK['point_de_vente'], [PAGE], actif='Configuration',
                          societe=demo.SOCIETE_RESTO, initiale=INITIALE_ADMIN, avatar=demo.AVATARS_RESTO['A'],
                          apps=APPS_PROFIL['resto_admin'], app_active='Point de Vente')
ADMIN_ECRAN = ADMIN_ECRAN.replace('class="app muk"', 'class="app muk masque"', 1)

ECRAN = navigateur(CAISSE + GESTION + ADMIN_ECRAN)

CSS = ("/* -- la pastille : Inès ; Edwige à l'étape 3 ; l'administrateur d'Odoo (AITE) à l'étape 5 -- */\n"
       + css_personnage('#tu-perso.t20-edwige', demo.POSTES_RESTO['manager'][0], demo.POSTES_RESTO['manager'][1],
                        NOM_E[0])
       + css_personnage('#tu-perso.t20-admin', ADMIN, ROLE_ADMIN, INITIALE_ADMIN) + """
/* -- l'écran de commande : deux colonnes de gauche dans la même case (avant / après le premier produit) -- */
#t20-c1 .rs-cmd > .rs-g, #t20-c2 .rs-cmd > .rs-g { grid-column: 1; grid-row: 1; }
#t20-c1 .rs-cmd > .rs-d, #t20-c2 .rs-cmd > .rs-d { grid-column: 2; grid-row: 1; }
/* addition rouverte sans ligne choisie : pas de pavé (O/point_of_sale product_screen.xml:13 ; C/09) */
#t20-c1v-pave, #t20-c2v-pave { display: none; }
/* l'addition défile jusqu'à la ligne choisie, la dernière (Odoo la fait venir à l'écran) */
#t20-c1-lignes, #t20-c2-lignes { display: flex; flex-direction: column; justify-content: flex-end; }
#t20-c1-lignes > .rs-ligne, #t20-c2-lignes > .rs-ligne { flex: none; }
/* -- la pile des familles et des tuiles -- */
.t20-pile { flex: 1; min-height: 0; display: grid; }
.t20-et { grid-area: 1 / 1; display: flex; flex-direction: column; gap: 14px; min-height: 0; }
/* -- contraste WCAG AA (contrôle de hyperframes, comme t17) : « % », « Prix » et la quantité des tuiles -- */
#t20-pos .rs-pk.gris { color: #5C636A; }
#t20-pos .rs-tuile-q { color: #495057; }
/* « Note cuisine » et « J'envoie » grisés (C/09) : le gris d'Odoo pour le texte atténué (#6C757D), au lieu de #8C959D
   (3,0:1 et 2,9:1 au contrôle de hyperframes) */
#t20-pos .rs-ctrl > span.gris, #t20-pos .rs-envoyer:not(.actif) { color: #6C757D; }
/* -- 3. la fiche produit (capture de référence, ×1,2 environ) -- */
.t20-cp { gap: 14px; }
.t20-stats { display: flex; margin-left: 40px; }
.t20-st { display: flex; align-items: center; gap: 10px; height: 58px; padding: 0 14px; background: #fff;
  border: 1px solid #DEE2E6; }
.t20-st + .t20-st { border-left: 0; }
.t20-st-i { width: 30px; height: 30px; display: inline-flex; color: #3F6A83; flex: none; }
.t20-st-i svg { width: 30px; height: 30px; }
.t20-st-t { display: flex; flex-direction: column; line-height: 1.15; font-size: 18px; color: #495057;
  white-space: nowrap; }
.t20-st-t b { font-weight: 500; color: #3F6A83; }
.t20-cp .pager { margin-left: auto; }
.t20-cp .fil .ref { display: inline-flex; align-items: center; gap: 10px; white-space: nowrap; }
.t20-cadre { position: absolute; left: 0; right: 0; top: 80px; bottom: 0; overflow: hidden; background: #F8F9FA;
  padding: 0 22px; }
.t20-bande { height: 72px; display: flex; align-items: center; gap: 8px; }
.t20-bande .bt { height: 50px; font-size: 20px; }
.t20-feuille { background: #fff; border: 1px solid #DEE2E6; padding: 30px 44px 30px; }
.t20-tete { display: flex; justify-content: space-between; align-items: flex-start; }
.t20-type { font-size: 20px; color: #212529; font-weight: 500; }
.t20-nom { display: flex; align-items: center; gap: 30px; margin-top: 4px; font-size: 44px; font-weight: 500;
  color: #212529; line-height: 1.2; }
.t20-etoile { width: 36px; height: 36px; display: inline-flex; color: #6C757D; }
.t20-cases { display: flex; gap: 26px; margin-top: 18px; font-size: 21px; color: #212529; }
.t20-cases > span { display: inline-flex; align-items: center; gap: 10px; }
.t20-case { margin-top: 0; }
.t20-photo { width: 120px; height: 120px; border: 1px solid #DEE2E6; display: flex; align-items: center;
  justify-content: center; }
.t20-photo svg { width: 92px; height: 92px; }
.t20-onglets { margin: 26px -44px 0; padding: 0 44px; }
.t20-onglets .onglet { font-size: 20px; padding: 13px 24px; }
.t20-onglets .onglet:not(.actif) { color: #3F6A83; }
.t20-cols { display: grid; grid-template-columns: 1fr 1fr; column-gap: 60px; margin-top: 22px; }
.t20-ch { display: grid; grid-template-columns: 260px 1fr; align-items: center; min-height: 56px; font-size: 21px; }
.t20-l { font-weight: 500; color: #212529; line-height: 1.3; }
.t20-v { color: #212529; display: flex; align-items: center; gap: 22px; }
.t20-q { margin-left: 4px; font-size: 14px; font-weight: 700; color: #3F6A83; }
.t20-radio { display: inline-flex; align-items: center; gap: 9px; }
.t20-radio i { width: 21px; height: 21px; border-radius: 50%; border: 2px solid #ADB5BD; background: #fff; }
.t20-radio.choisi i { border: 6px solid var(--muk-prim); }
.t20-astuce { margin: 4px 0 0 260px; font-size: 20px; font-style: italic; color: #5C636A; }
/* -- 3. l'assistant -- */
.t20-m-ch { display: grid; grid-template-columns: 380px 170px; align-items: center; min-height: 72px; font-size: 21px;
  padding-left: 24px; }
.t20-m-l { font-weight: 500; color: #212529; }
.t20-m-in { margin-top: 0; height: 48px; border-width: 0 0 1px 0; border-radius: 0; padding: 0 6px; }
.t20-m-in .ph, .t20-m-in .val { left: 6px; font-size: 22px; font-weight: 400; }
#t20-nqd-val.t20-sel { background: #3A6FD8; color: #fff; padding: 1px 2px; }
/* le champ qui a le curseur : son trait passe à la couleur primaire, sans cadre (capture) */
.app.muk .t20-m-in.focus { box-shadow: none; border-color: var(--muk-prim); }
""")


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


def taper(fen, chiffres, d=0.3):
    """Un code tapé dans la fenêtre ``fen`` : les points se remplissent, le chiffre ne s'affiche jamais."""
    gestes = []
    for k, c in enumerate(chiffres):
        gestes += touche('#%s-k%s' % (fen, c), classe('#%s-p%d' % (fen, k), ajouter=['plein']), d=d)
    return gestes


def bascule(avant, apres):
    """Un état remplace l'autre, sans transition (une colonne, une rangée de familles)."""
    return [cacher(avant, d=0.05), montrer(apres, d=0.05, y=0, avec=True)]


def tuile(ident, nom, q, *effets, d=0.45):
    """Un produit touché : sa quantité sur la tuile (product_card.xml:24), puis ses effets sur l'addition."""
    sel = '#%s-%s' % (ident, cle(nom))
    return touche(sel, texte(sel + '-q', str(q)), classe(sel + '-q', ajouter=['on']), *effets, d=d)


def vers_commande(vue_):
    return [vue(vue_, 'pos'), classe('#' + POS, ajouter=['sur-commande', 'avec-emp'], retirer=['sur-plan']),
            texte('#%s-onglet' % POS, str(TABLE))]


def vers_plan():
    return [vue('t20-plan', 'pos'), classe('#' + POS, ajouter=['sur-plan'], retirer=['sur-commande', 'avec-emp']),
            texte('#%s-onglet' % POS, 'Table')]


E1, E2 = '#t20-c1-e%d', '#t20-c2-e%d'
TU_BRUNE_1 = '#t20-c1-e2-tu-%s' % cle(BRUNE)

ETAPES = [
    # 1. La bière brune : refusée, rien n'est ajouté (1 touche, notes §3 l.254).
    {'temps': 0, 'titre': 'Une bière brune ? Refusée',
     'texte': '%s : « %s ». Rien n\'est ajouté, et le message dit quoi faire.' % (BRUNE, TITRES_RESTO['produitEpuise']),
     'voix': "À la table dix, Inès passe aux bières et touche la bière brune. La caisse refuse : produit épuisé. Rien "
             "ne s'ajoute à l'addition, et le message dit quoi faire : si la bouteille est bien là, le manager "
             "enregistre l'entrée de stock.",
     # Calé sur la voix (pauses mesurées dans la piste) : le refus quand elle dit « la caisse refuse », l'addition
     # quand elle dit « rien ne s'ajoute », le message (zoom) quand elle dit « le message dit quoi faire ».
     'gestes': [pause(0.3), anneau('#t20-c1v-etat', d=1.2), pause(0.1)]
               + touche(E1 % 0 + '-fa-f-alcoolise', *bascule(E1 % 0, E1 % 1), d=0.5)
               + touche(E1 % 1 + '-fa-f-biere', *bascule(E1 % 1, E1 % 2), d=0.4)
               + touche(TU_BRUNE_1, notifier('t20-epuise', duree=6.6), d=0.45)
               + [pause(0.95), curseur('#t20-c1v-total', fx=0.8, d=0.4), anneau('#t20-c1v-total', d=1.2),
                  bulle('b-rien', '#t20-c1v-total', cote='haut', d=1.9, avec=True),
                  zoom('#t20-epuise', s=1.4, d=0.7), pause(2.0), dezoom(d=0.6)]},
    # 2. Une pizza passe toujours ; « J'envoie » : le plan revient.
    {'temps': 0, 'titre': 'Une pizza, elle, passe toujours',
     'texte': 'Plats, pizzas, café : pas de suivi de stock, jamais refusés. « J\'envoie » : « %s »'
              % TEXTES_RESTO['envoye'](ENVOI_1),
     'voix': "Le client prend aussi une pizza quatre fromages : Nourriture, puis Pizzas. Les plats ne sont pas suivis "
             "en stock : la caisse ne les refuse jamais. Le code-barres, le pavé et la variante choisie, eux, passent "
             "par le même contrôle que le toucher. J'envoie, et le plan revient.",
     # Calé sur la voix : « Nourriture, puis Pizzas » à la fin de la première phrase ; la bulle des gestes quand elle
     # dit « le code-barres, le pavé… » ; « J'envoie » quand elle le dit.
     'gestes': [pause(2.2)]
               + touche(E1 % 2 + '-fa-f-nourriture', *bascule(E1 % 2, E1 % 3), d=0.6)
               + touche(E1 % 3 + '-fa-f-pizzas', *bascule(E1 % 3, E1 % 4), d=0.45)
               + tuile('t20-c1-e4-tu', FROMAGES, 1, *bascule('#t20-c1v-g', '#t20-c1-g'), d=0.5)
               + [pause(0.3), anneau('#t20-c1-l4', d=1.4), pause(0.8),
                  bulle('b-gestes', '#t20-c1-e4-tu', cote='bas', d=3.6), pause(2.9),
                  curseur('#t20-c1-envoyer', fx=0.3, d=0.5)]
               + touche('#t20-c1-envoyer', *vers_plan(), notifier('t20-n1', duree=3.0), d=0.35)
               + [pause(0.2), curseur(T10, fx=0.75, fy=0.75, d=0.4), anneau(T10, d=1.0, avec=True, decale=0.2)]},
    # 3. La manager enregistre l'entrée de stock : 0 → 24.
    {'temps': 1, 'titre': "La manager enregistre l'entrée de stock",
     'texte': 'Produits › %s › « Mettre la quantité à jour » : %d, « Appliquer ». La fiche affiche %s.'
              % (BRUNE, ENTREE, quantite(ENTREE)),
     'voix': "Un casier de vingt-quatre bières brunes arrive. Dans la gestion, Edwige, la manager, ouvre la fiche de "
             "la bière brune : zéro disponible. Elle touche Mettre la quantité à jour, tape vingt-quatre, puis "
             "appliquer : la fiche affiche vingt-quatre disponibles. Chaque saisie garde sa date et son auteur.",
     # Calé sur la voix : « Produits » quand elle dit « dans la gestion », la fiche quand elle dit « ouvre la fiche »,
     # « zéro disponible », puis chaque toucher quand elle le nomme ; la bulle sur la dernière phrase.
     'gestes': [montrer('#t20-gest', d=0.5, y=0), classe('#tu-perso', ajouter=['t20-edwige'], avec=True),
                pause(2.05), curseur('#t20-gest-produits', d=0.5), anneau('#t20-gest-produits', d=1.1), pause(0.5),
                curseur('#t20-fp-nom', fx=0.97, fy=0.9, d=0.5), anneau('#t20-fp-nom', d=1.0),
                curseur('#t20-fp-dispo', fx=0.12, d=0.4), anneau('#t20-fp-dispo', d=1.1)]
               + touche('#t20-fp-maj', ouvrir('t20-qte'), d=0.5)
               + [pause(0.3), curseur('#t20-nqd', fx=0.7, d=0.4),
                  classe('#t20-nqd-val', retirer=['t20-sel']), saisir('t20-nqd', str(ENTREE), d=0.5, avec=True),
                  pause(0.3)]
               + touche('#t20-appliquer', fermer('t20-qte'), texte('#t20-fp-dispo-v', quantite(ENTREE)),
                        texte('#t20-fp-prev-v', quantite(ENTREE)), d=0.5)
               + [pause(0.1), curseur('#t20-fp-dispo', fx=0.12, d=0.4), anneau('#t20-fp-dispo', d=1.2),
                  bulle('b-trace', '#t20-fp-dispo', cote='bas', d=2.6)]},
    # 4. De retour à la table : la bière brune passe, sans recharger ; « J'envoie ».
    {'temps': 2, 'titre': 'La vente repasse, sans recharger',
     'texte': 'Même tablette, sans recharger : la bière brune passe. Ce qui est parti sur les tables ouvertes est '
              'déduit.',
     'voix': "Six minutes plus tard, Inès revient à sa table et tape son code. En s'ouvrant, l'écran de commande "
             "relit le stock enregistré. Boisson, alcoolisé, bière : elle retouche la bière brune, et cette fois la "
             "vente passe, sans recharger la caisse. Deux bières brunes. Pour décider, la caisse prend le stock "
             "enregistré, moins ce qui est déjà parti sur les tables ouvertes, à tous les postes. Puis j'envoie.",
     'gestes': [cacher('#t20-gest', d=0.4), classe('#tu-perso', retirer=['t20-edwige'], avec=True),
                texte(T10 + '-d', duree_resto(DUREE_2), avec=True), pause(0.1)]
               + touche(T10, ouvrir('t20-code'), d=0.5, fy=0.35)
               + [pause(0.1)] + taper('t20-code', CODE_I, d=0.22)
               + [pause(0.1), fermer('t20-code')] + [dict(g, avec=True) for g in vers_commande('t20-c2')]
               + [pause(0.2)]
               + touche(E2 % 0 + '-fa-f-boisson', *bascule(E2 % 0, E2 % 1), d=0.55)
               + touche(E2 % 1 + '-fa-f-alcoolise', *bascule(E2 % 1, E2 % 2), d=0.4)
               + touche(E2 % 2 + '-fa-f-biere', *bascule(E2 % 2, E2 % 3), d=0.4)
               + tuile('t20-c2-e3-tu', BRUNE, 1, *bascule('#t20-c2v-g', '#t20-c2-g'), d=0.5)
               + tuile('t20-c2-e3-tu', BRUNE, 2, texte('#t20-c2-l5-q', '2,00'),
                       texte('#t20-c2-l5-m', fcfa(2 * PRIX[BRUNE])), texte('#t20-c2-total', fcfa(TOTAL_3)),
                       texte('#t20-c2-env-0-v', '2'), d=0.4)
               + [pause(0.2), anneau('#t20-c2-l5', d=1.0),
                  bulle('b-postes', '#t20-c2-e3-tu', cote='bas', d=4.8), pause(4.4)]
               + touche('#t20-c2-envoyer', *vers_plan(), notifier('t20-n2', duree=3.0), d=0.45)
               # la réaction part avec l'envoi et se referme avant la fin de l'étape (pas plus de 3 s sans voix
               # jusqu'à la voix de l'étape 5)
               + [reaction('r-fin', d=1.9, avec=True, decale=0.3), pause(1.05)]},
    # 5. Le réglage : coché d'office ; le stock de départ ; hors connexion, on vend.
    {'temps': 3, 'titre': "Un réglage, coché d'office",
     'texte': 'Réglages du Point de Vente : « Refuser la vente des produits épuisés », coché d\'office. Hors '
              'connexion, la caisse vend.',
     'voix': "Ce refus est un réglage du Point de Vente, coché d'office. Il ne touche que les produits dont on suit "
             "le stock : saisissez le stock de départ avant le premier service, sinon ces bières seront refusées. Et "
             "sans réseau, la caisse vend quand même, sans contrôler le stock.",
     'gestes': [montrer('#t20-adm', d=0.5, y=0), classe('#tu-perso', ajouter=['t20-admin'], avec=True), pause(0.3),
                defiler('#t20-rg-defil', -690, d=1.0), pause(0.2), curseur('#t20-refus-case', d=0.5),
                anneau('#t20-refus-case', d=1.4), pause(0.2),
                # calé sur la voix : « saisissez le stock de départ… », puis « et sans réseau… »
                zoom('#t20-refus', s=1.33, d=0.8), pause(0.6),
                bulle('b-depart', '#t20-refus-aide', cote='gauche', d=4.2), pause(3.9),
                bulle('b-hors', '#t20-refus-aide', cote='gauche', d=3.1), pause(2.25), dezoom(d=0.6)]},
]

TUTORIEL = {
    'slug': 't20-restaurant-produits-epuises',
    'profil': 't20_restaurant_produits_epuises',
    'numero': 20,
    'titre': 'Produits épuisés',
    'fonction': 'Stock suivi en caisse',
    'personnage': demo.POSTES_RESTO['serveuse'],
    'accroche': {
        'kicker': 'Au bar',
        # Les douleurs : docs/PERIMETRE_FONCTIONNEL_RESTAURANT.md, REST-19 (:432, « que le système ne prenne même
        # pas ») ; couverture d'Odoo 18 (:448 : la caisse ne consulte pas le stock, il ne baisse qu'au paiement, il
        # peut devenir négatif, il ne se lit qu'à la demande dans la fiche du produit — C39, C40, C41) ; :597 (tant
        # qu'une table est ouverte, ses consommations ne sont pas déduites).
        'question': 'Vendre une bouteille qu\'on n\'a *plus* ?',
        # Seules les douleurs que la vidéo résout (les cartes sont « aspirées » par la révélation) : le stock qui ne
        # baisse qu'au paiement (C40) reste vrai avec AITE (la caisse déduit ce qui est parti pour décider, le stock
        # d'Inventaire ne bouge pas : ECARTS.md n° 106) et le stock lu dans la fiche (C41) aussi (la tuile ne le montre pas,
        # 19c au lot 2 ; l'étape 3 va le lire dans la fiche) : ces deux cartes sont retirées, la voix garde le
        # constat.
        'douleurs': [('boite', 'On vend une bouteille qu\'on n\'a plus'),
                     ('echange', 'Les bouteilles servies, pas encore payées, ne comptent pas'),
                     ('alerte', 'Un stock qui passe sous zéro')],
        'voix': "Une bière brune pour la table dix ? Le bar n'en a plus, mais la caisse la prend quand même. Le stock "
                "ne baisse qu'à l'addition payée : les bouteilles servies ne comptent pas encore.",
    },
    'revelation': {
        # Notes de version §2 l.138-141 ; S/store/pos_store.js:1701-1705 (R11 sous le titre), :1759-1762 (rien
        # n'est ajouté) ; recette R75, R76.
        'promesse': 'Un produit suivi en stock et épuisé n\'est pas ajouté : « Produit épuisé », avec ce qu\'il faut '
                    'faire. Une entrée de stock, et il se vend de nouveau, sans recharger la caisse.',
        'voix': "Avec Aïte haousse, la caisse refuse la bouteille qu'on n'a plus, et dit quoi faire.",
    },
    'temps': ['Refusé', 'Entrée de stock', 'Revendu', 'Réglage'],
    'app': POS,
    'ecran': ECRAN,
    'css': CSS,
    'vues_initiales': {'pos': 't20-c1'},
    'bulles': {
        # pos_store.js:1759-1762 (return sans ajout) ; R75 ; parcours_tour.js:283-286 (pasDeLigne).
        'b-rien': 'Ni ligne, ni montant : la bouteille n\'est pas vendue.',
        # product_screen.js:31-36 ; order_summary.js:66-89 ; pos_store.js:1795-1817 ; notes §2 l.138-139 ; R75.
        'b-gestes': 'Code-barres, quantité tapée au pavé, variante choisie : la caisse contrôle aussi.',
        # Recette R73 (Inventaire → Rapports → Historique des mouvements).
        'b-trace': 'Chaque saisie de stock garde sa date et son auteur.',
        # R/models/product_product.py:2-11, 51-73 ; AIDE_REFUS_EPUISE ; R78.
        # « enregistré », et non « compté » : la caisse part du stock saisi dans Odoo (ECARTS.md n° 106 : un stock compté au
        # rayon, saisi tel quel, ferait déduire deux fois ce qui est parti).
        'b-postes': 'Le stock enregistré, moins ce qui est déjà parti sur les tables ouvertes, à tous les postes.',
        # AIDE_REFUS_EPUISE (pos_config.py:65-66) ; INSTALLATION.md §9.6 point 4.
        'b-depart': 'Sans stock de départ, chaque bière suivie serait refusée.',
        # pos_store.js:1615-1617, 1666-1667 (Q59) ; notes §7 l.526-528 ; R79.
        'b-hors': 'Sans réseau, la caisse vend sans contrôler le stock.',
    },
    'reactions': {
        'r-fin': 'Je ne promets plus une bouteille qu\'on n\'a pas.',
    },
    'etapes': ETAPES,
    'resultats': {
        'titre': 'Le stock, tenu à la caisse',
        'cartes': [
            {'valeur': '1', 'compter': 1, 'unite': 'touche', 'icone': 'x',
             'texte': 'pour voir une bouteille épuisée refusée : rien n\'est ajouté'},
            {'valeur': '4', 'compter': 4, 'unite': 'gestes contrôlés', 'icone': 'bouclier',
             'texte': 'le toucher, le code-barres, le pavé, la variante choisie'},
            {'valeur': '60', 'compter': 60, 'unite': 'secondes', 'icone': 'horloge',
             # la mémoire vieillit sans être relue : passé 60 s, la caisse ne s'en sert plus (aiteDisponible)
             'texte': 'au plus : l\'âge du stock sur lequel la caisse décide ; à 2 bouteilles ou moins, elle le '
                      'relit'},
        ],
        'voix': "Une touche pour voir le refus, quatre gestes contrôlés, et jamais une décision sur un stock de plus "
                "d'une minute.",
    },
    'cta': {
        'appel': 'Demandez votre démonstration',
        'sous_marque': demo.SOUS_MARQUE_RESTO,
        'suivant': 'Encaisser une table',
        'voix': "Aïte haousse, par Aïte Consulting. Demandez votre démonstration. Prochain tutoriel : encaisser une "
                "table.",
    },
    'vignette': {'etape': 1, 'apres': 6.0},
}


def _typo(texte_):
    """Les textes à l'écran écrits ici (pas la voix) : une espace insécable dans les guillemets et avant « : »,
    « ; », « ? », pour qu'un signe ne passe pas seul à la ligne (comme S/utils/messages.js:7-9 ; comme t17)."""
    for avant, apres in (('« ', '«' + NBSP), (' »', NBSP + '»'), (' :', NBSP + ':'), (' ;', NBSP + ';'),
                         (' ?', NBSP + '?')):
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
