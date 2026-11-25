# -*- coding: utf-8 -*-
# Carte du « Restaurant Le Messager » (Douala) : la base de démonstration
# aite_messager, qui ressemble au vrai restaurant du client.
#
# Ce que fait ce script (après la mise en place du restaurant : caisse
# « Restaurant », salle et 12 tables, équipe à codes, comptes) :
#   - la société s'appelle « Restaurant Le Messager », à Douala (seulement si
#     elle porte encore un nom par défaut : un vrai nom n'est jamais écrasé) ;
#   - les familles de la caisse, sur trois niveaux au plus, sont les sections
#     de la carte, avec les mêmes noms en catégories de produit (PARAM-04) :
#       Petit déjeuner > Omelettes, Spécial petit déj
#       Plats > Plats chauds, Poulet DG, Poulet pané, Fruits de mer
#       Pizzas & burgers > Pizzas, Burgers, Pastas, Crêpes & glaces
#       Afternoon tea > Sucrée, Salée, Tea Time
#       Bar > Vins > Vins blancs, Vins rouges, Rosés, Vins mousseux
#       Bar > Whisky, Bières
#       Bar > Sans alcool > Eaux, Jus, Sodas, Café & thé
#   - toute la carte (4 pages), aux prix exacts de la carte, en FCFA, taxes
#     comprises : aucune taxe n'est posée sur les produits (ni à la vente ni à
#     l'achat), la TVA se règle avec le comptable du client ;
#   - les tailles sont des produits séparés (une touche par article au lieu de
#     trois avec une fenêtre de choix) : pizzas « Petit » / « Grand », bar et
#     sole « petite » / « grosse pièce », glaces 1, 2, 3 boules, Tea Time seul,
#     avec Rose Joven, avec Moscato ;
#   - l'accompagnement des plats de la page 2 (riz nature, riz Messager,
#     frites plantain, frites pomme) est un choix sans supplément (attribut
#     « Accompagnement », sans variante) : la caisse ouvre une petite fenêtre,
#     le premier choix (riz nature) est déjà coché — un « Ajouter » sans choix
#     envoie donc « (Riz nature) » en cuisine —, il part sur le bon de cuisine ;
#   - les boissons revendues (eaux, jus en bouteille, sodas, bières, vins,
#     whiskies) sont suivies en stock (« Suivre l'inventaire »), avec un coût
#     (standard_price) et un stock de départ ; leurs catégories de produits
#     (« Bar » et ses sous-catégories) sont en « Coût moyen (AVCO) » : le coût
#     suit les achats (« Prix standard », d'office dans Odoo, le laissait à
#     650 après un achat de Bière blonde à 700 : recette) ; les plats cuisinés n'ont ni
#     stock ni coût (aucun coût n'est inventé pour eux) ; le café, le thé et le
#     jus pressé maison ont un coût estimé, sans stock.
#   - conséquence pour l'analyse AITE (marge et CMV) : la marge n'a de sens
#     que pour les boissons ; un plat sans coût y paraît à 100 % de marge. Pour
#     les plats, il faut un coût de revient (fiche recette) fourni par le
#     client ; en démonstration, filtrer l'analyse sur la famille « Bar ».
#
# À FAIRE VALIDER PAR LE CLIENT (aussi écrit dans les « Notes internes » de
# chaque produit concerné, onglet « Informations générales ») :
#   - les produits ajoutés HORS CARTE (la carte n'en donne pas) et leurs prix
#     de vente : eaux 0,5 L 500 F et 1,5 L 1 000 F, jus 33 cl 1 000 F, jus
#     naturel pressé 2 000 F, sodas 1 000 F, bières 65 cl 1 500 F, bière
#     importée 2 000 F, café expresso 1 000 F, thé 1 000 F ;
#   - TOUS les coûts : estimations (ordre de grandeur du marché de Douala),
#     voir la liste BOISSONS plus bas — à remplacer par les prix d'achat réels ;
#   - le prix du whisky « Black » : masqué sur la photo de la carte,
#     40 000 F provisoires ;
#   - bar (5 000 - 10 000) et sole (8 000 - 12 000) : la carte donne une
#     fourchette « selon taille » ; deux pièces sont posées, aux deux bornes ;
#   - « Poulet pané 1/4 DG, 1/2 DG, entier » : lecture de la carte à confirmer ;
#   - l'accompagnement au choix posé sur toute la page 2 (le bandeau de la
#     carte est en bas de page), poulet pané et Ndolé compris ; et « Riz
#     nature » comme accompagnement par défaut (déjà coché à l'ouverture) ;
#   - le Tea Time « avec Rose Joven » ou « avec Moscato » : la bouteille
#     comprise n'est pas déduite du stock (Rose Joven n'est pas à la carte) ;
#   - les stocks de départ (fictifs, crédibles pour une démonstration) ;
#   - le coût de revient des plats (fiche recette), sans quoi leur marge n'a
#     pas de sens ;
#   - la TVA, avec le comptable du client (prix saisis tels quels, sans taxe).
#
# Rejouable : rien n'est créé deux fois (recherche par clé stable, voir plus
# bas) ; un nom, un prix, un coût, une famille, une note ou une taxe qui
# diffère du script est remis à jour ; un produit des familles de la carte qui
# n'est plus dans le script est retiré de la caisse ;
# le stock de départ n'est saisi que pour un produit suivi qui n'a encore
# aucun mouvement de stock ; le suivi en stock n'est changé que tant que le
# produit n'a aucun mouvement (Odoo le refuse ensuite).
# Refuse une base qui porte la carte de démonstration de seed_restaurant.py
# (Castel, Pizza Margherita...) : la base se crée avec --carte-messager. Écrit
# le paramètre système aite.carte_client = messager : seed_restaurant.py ne
# pose alors jamais sa carte de démonstration dans cette base.
#
# Usage (Odoo 18 à côté, dans ../odoo18) :
#   PG_HOST=localhost PYTHON=../venv312/bin/python dev/setup_env.sh --restaurant --carte-messager
#   (base aite_messager par défaut)
# ou, sur une base du restaurant créée sans carte de démonstration :
#   cd ../odoo18 && $PYTHON odoo-bin shell -c ../AITE-HOUSE/dev/odoo.conf -d aite_messager \
#       --no-http < ../AITE-HOUSE/dev/seeds/seed_carte_messager.py
from odoo.tools import html2plaintext

company = env.company
compte = {'familles': 0, 'categories': 0, 'produits': 0, 'mis_a_jour': 0, 'stocks': 0,
          'accompagnements': 0, 'retires': 0, 'couts_moyens': 0}

caisse_pos = env['pos.config'].search([
    ('company_id', '=', company.id), ('aite_mode_restaurant', '=', True)], order='id', limit=1)


# MODE_MODULE : posé par le crochet d'installation du module (__init__.py) ;
# absent quand le script est joué dans odoo-bin shell (dev/seeds/seed_carte_messager.py).
MODE_MODULE = globals().get('MODE_MODULE', False)


def refuser(message):
    """Arrête la graine sans rien écrire : erreur lisible à l'installation du module,
    message sur la sortie (lu par setup_env.sh) dans odoo-bin shell."""
    if MODE_MODULE:
        from odoo.exceptions import UserError
        raise UserError(message)
    print(message)
    raise SystemExit(1)


if not caisse_pos:
    refuser("✗ aucune caisse au service à table contrôlé : installer d'abord le "
            "restaurant (dev/setup_env.sh --restaurant --carte-messager)")

# Des noms propres à la carte de démonstration (aucun n'est sur la carte du client).
DEMO = ["Castel 65 cl", "33 Export 65 cl", "Pizza Margherita", "Pizza Reine",
        "Petit déjeuner complet", "Beignets haricots bouillie"]
Produits = env['product.template'].with_context(active_test=False)
demo = Produits.search([('name', 'in', DEMO), ('available_in_pos', '=', True)])
if demo and MODE_MODULE:
    refuser("la carte de démonstration Le Messager n'est pas posée : cette base vend déjà "
            "d'autres produits (%s). Ce module de démonstration est fait pour une base neuve ; "
            "il ne mélange pas deux cartes." % ", ".join(demo.mapped('name')))
if demo:
    refuser("✗ cette base porte la carte de démonstration de seed_restaurant.py (%s) : rien "
            "n'est posé ; créer une base avec « ODOO_DB=aite_messager dev/setup_env.sh "
            "--restaurant --carte-messager »" % ", ".join(demo.mapped('name')))

# La société n'est renommée que dans la base de démonstration (odoo-bin shell),
# jamais à l'installation du module dans la base d'un client.
if not MODE_MODULE and company.name in ("My Company", "YourCompany", "Ma société", "Votre société",
                    "Restaurant de démonstration"):
    company.name = "Restaurant Le Messager"
if not MODE_MODULE and company.name == "Restaurant Le Messager" and not company.city:
    company.city = "Douala"

# ------------------------------------------- familles (caisse) et catégories
# (nom, couleur de la famille dans la caisse, sous-familles)
ARBRE = [
    ("Petit déjeuner", 3, [("Omelettes", []), ("Spécial petit déj", [])]),
    ("Plats", 2, [("Plats chauds", []), ("Poulet DG", []), ("Poulet pané", []),
                  ("Fruits de mer", [])]),
    ("Pizzas & burgers", 1, [("Pizzas", []), ("Burgers", []), ("Pastas", []),
                             ("Crêpes & glaces", [])]),
    ("Afternoon tea", 9, [("Sucrée", []), ("Salée", []), ("Tea Time", [])]),
    ("Bar", 4, [
        ("Vins", [("Vins blancs", []), ("Vins rouges", []), ("Rosés", []),
                  ("Vins mousseux", [])]),
        ("Whisky", []), ("Bières", []),
        ("Sans alcool", [("Eaux", []), ("Jus", []), ("Sodas", []), ("Café & thé", [])]),
    ]),
]
familles, categories = {}, {}


def poser(modele, nom, parent, rang, cle, couleur=None):
    """La famille (pos.category) ou la catégorie (product.category) ``nom``
    sous ``parent`` : trouvée, sinon créée."""
    enregistrement = env[modele].search(
        [('name', '=', nom), ('parent_id', '=', parent.id if parent else False)], limit=1)
    if not enregistrement:
        valeurs = {'name': nom, 'parent_id': parent.id if parent else False}
        if modele == 'pos.category':
            valeurs['sequence'] = rang
            if couleur is not None:
                valeurs['color'] = couleur
        enregistrement = env[modele].create(valeurs)
        compte[cle] += 1
    return enregistrement


def descendre(branches, parent_famille=None, parent_categorie=None):
    for rang, branche in enumerate(branches, start=1):
        nom, couleur, enfants = branche if len(branche) == 3 else (branche[0], None, branche[1])
        assert nom not in familles, "famille en double : %s" % nom
        famille = poser('pos.category', nom, parent_famille, rang, 'familles', couleur)
        categorie = poser('product.category', nom, parent_categorie, rang, 'categories')
        familles[nom], categories[nom] = famille, categorie
        descendre(enfants, famille, categorie)


descendre(ARBRE)

# Les boissons revendues (« Bar » et ses sous-catégories) en « Coût moyen
# (AVCO) » : à chaque réception d'un achat, le coût devient la moyenne du stock
# et de l'achat. Le champ vient de stock_account (installé avec point_of_sale) :
# sans lui, rien n'est posé. Posé avant les produits et leur stock de départ ;
# une catégorie remise en « Prix standard » à la main l'est de nouveau ici.
if 'property_cost_method' in env['product.category']._fields:
    boissons = env['product.category'].search([('id', 'child_of', categories["Bar"].id)])
    a_regler = boissons.filtered(lambda c: c.property_cost_method != 'average')
    if a_regler:
        a_regler.write({'property_cost_method': 'average'})
        compte['couts_moyens'] += len(a_regler)

# ------------------------------------------------------------------ la carte
A_VALIDER = "À valider par le client (Le Messager) : "
HORS_CARTE = (A_VALIDER + "produit ajouté hors carte (la carte n'en donne pas) ; prix de vente "
              "et coût estimés (marché de Douala), à remplacer par les vrais.")
COUT_ESTIME = A_VALIDER + "coût estimé (ordre de grandeur), à remplacer par le prix d'achat réel."

# Chaque produit porte une CLÉ stable (premier élément) : la graine retrouve le
# produit par cette clé (identifiant externe __aite_messager__.produit_<clé>),
# puis par son nom pour une base posée avant les clés. Pour renommer un produit
# une fois validé par le client (« Black », « Rosé », « Soda 33 cl »...), on
# change le NOM, jamais la clé : le produit est renommé, pas dupliqué. Un
# produit retiré du script est retiré de la caisse (pas supprimé : il garde
# son historique et son stock).
#
# Plats cuisinés : (clé, nom, famille, prix FCFA[, note]) — ni stock, ni coût.
PLATS = [
    # Page 1 — Petit déjeuner & omelettes (7 h - 11 h, pain artisanal & café ou thé inclus)
    ("omelette_nature", "Omelette nature", "Omelettes", 2000),
    ("omelette_legumes", "Omelette légumes", "Omelettes", 2500),
    ("omelette_champignons", "Omelette champignons", "Omelettes", 3000),
    ("omelette_fromage", "Omelette fromage", "Omelettes", 3500),
    ("omelette_jambon_fromage", "Omelette jambon fromage", "Omelettes", 4000),
    ("oeufs_brouilles", "Œufs brouillés", "Omelettes", 2500),
    ("oeuf_benedict", "Œuf Bénédict", "Omelettes", 5000),
    ("acai_bowl", "Açaï Bowl", "Spécial petit déj", 3500),
    ("dejeuner_francais", "Déjeuner français", "Spécial petit déj", 5000),
    ("petit_dejeuner_americain", "Petit déjeuner américain", "Spécial petit déj", 5000),
    ("petit_dejeuner_continental", "Petit déjeuner continental", "Spécial petit déj", 5000),
    # Page 2 — Plats chauds, poulet, fruits de mer (accompagnement au choix)
    ("poulet_yassa", "Poulet Yassa", "Plats chauds", 4000),
    ("poulet_ail", "Poulet ail", "Plats chauds", 4000),
    ("roti_poulet", "Rôti poulet", "Plats chauds", 4000),
    ("roti_porc", "Rôti porc", "Plats chauds", 4000),
    ("roti_gesier", "Rôti gésier", "Plats chauds", 3000),
    ("poulet_mayo", "Poulet mayo", "Plats chauds", 4000),
    ("ndole_viande", "Ndolé viande", "Plats chauds", 3000),
    ("poulet_dg", "Poulet DG", "Poulet DG", 5000),
    ("porc_dg", "Porc DG", "Poulet DG", 5000),
    ("crevettes_dg", "Crevettes DG", "Poulet DG", 6000),
    ("gambas_dg", "Gambas DG", "Poulet DG", 10000),
    ("poulet_pane_3_morceaux", "Poulet pané 3 morceaux", "Poulet pané", 3500),
    ("poulet_pane_6_morceaux", "Poulet pané 6 morceaux", "Poulet pané", 6000),
    ("poulet_pane_12_morceaux", "Poulet pané 12 morceaux", "Poulet pané", 11000),
    ("poulet_pane_quart_dg", "Poulet pané 1/4 DG", "Poulet pané", 3500,
     A_VALIDER + "lecture de la carte (« 1/4 DG » sous « Poulet pané ») à confirmer."),
    ("poulet_pane_demi_dg", "Poulet pané 1/2 DG", "Poulet pané", 6000,
     A_VALIDER + "lecture de la carte (« 1/2 DG » sous « Poulet pané ») à confirmer."),
    ("poulet_pane_entier", "Poulet pané entier", "Poulet pané", 11000,
     A_VALIDER + "lecture de la carte (« Entier » sous « Poulet pané ») à confirmer."),
    ("filet_capitaine", "Filet capitaine", "Fruits de mer", 5000),
    ("bar_petite_piece", "Bar petite pièce", "Fruits de mer", 5000,
     A_VALIDER + "la carte donne « Bar 5000 - 10000 » (selon la taille) : deux pièces "
     "posées aux deux bornes."),
    ("bar_grosse_piece", "Bar grosse pièce", "Fruits de mer", 10000,
     A_VALIDER + "la carte donne « Bar 5000 - 10000 » (selon la taille) : deux pièces "
     "posées aux deux bornes."),
    ("sole_petite_piece", "Sole petite pièce", "Fruits de mer", 8000,
     A_VALIDER + "la carte donne « Sole 8000 - 12000 » (selon la taille) : deux pièces "
     "posées aux deux bornes."),
    ("sole_grosse_piece", "Sole grosse pièce", "Fruits de mer", 12000,
     A_VALIDER + "la carte donne « Sole 8000 - 12000 » (selon la taille) : deux pièces "
     "posées aux deux bornes."),
    ("crevettes", "Crevettes", "Fruits de mer", 6000),
    ("gambas", "Gambas", "Fruits de mer", 8000),
    # Page 3 — Pizzas (Petit / Grand ; mozzarella, sauce tomate maison), burgers, pastas, crêpes
    ("pizza_marguerite_petit", "Pizza Marguerite Petit", "Pizzas", 5000),
    ("pizza_marguerite_grand", "Pizza Marguerite Grand", "Pizzas", 10000),
    ("pizza_vegetarienne_petit", "Pizza Végétarienne Petit", "Pizzas", 5000),
    ("pizza_vegetarienne_grand", "Pizza Végétarienne Grand", "Pizzas", 10000),
    ("pizza_poulet_petit", "Pizza Poulet Petit", "Pizzas", 6000),
    ("pizza_poulet_grand", "Pizza Poulet Grand", "Pizzas", 12000),
    ("pizza_viande_petit", "Pizza Viande Petit", "Pizzas", 6000),
    ("pizza_viande_grand", "Pizza Viande Grand", "Pizzas", 12000),
    ("pizza_thon_petit", "Pizza Thon Petit", "Pizzas", 6000),
    ("pizza_thon_grand", "Pizza Thon Grand", "Pizzas", 12000),
    ("pizza_trois_fromages_petit", "Pizza Trois fromages Petit", "Pizzas", 8000),
    ("pizza_trois_fromages_grand", "Pizza Trois fromages Grand", "Pizzas", 15000),
    ("pizza_jambon_calzone_petit", "Pizza Jambon calzone Petit", "Pizzas", 6000),
    ("pizza_jambon_calzone_grand", "Pizza Jambon calzone Grand", "Pizzas", 10000),
    ("burger_viande", "Burger viande", "Burgers", 3000),
    ("burger_poulet", "Burger poulet", "Burgers", 3000),
    ("big_mac", "Big Mac", "Burgers", 4000),
    ("mini_burger", "Mini burger", "Burgers", 3000),
    ("nuggets", "Nuggets", "Burgers", 3000),
    ("penne_arrabiata", "Penne arrabiata", "Pastas", 3000),
    ("spaghetti_bolognaise", "Spaghetti bolognaise", "Pastas", 3500),
    ("tagliatelles_poulet", "Tagliatelles poulet", "Pastas", 4000),
    ("steak_boeuf", "Steak bœuf", "Pastas", 6000),
    ("crepe_nature", "Crêpe nature", "Crêpes & glaces", 2000),
    ("crepe_chocolat_banana", "Crêpe chocolat banana", "Crêpes & glaces", 3500),
    ("crepe_biscoff_oreo", "Crêpe Biscoff Oreo", "Crêpes & glaces", 4000),
    ("gaufre_fraise", "Gaufre fraise", "Crêpes & glaces", 4500),
    ("glace_1_boule", "Glace 1 boule", "Crêpes & glaces", 1000),
    ("glace_2_boules", "Glace 2 boules", "Crêpes & glaces", 1500),
    ("glace_3_boules", "Glace 3 boules", "Crêpes & glaces", 2500),
    # Page 4 — Afternoon tea (15 h - 18 h)
    ("posset_citron", "Posset citron", "Sucrée", 1200),
    ("tiramisu", "Tiramisu", "Sucrée", 1200),
    ("gateau_miel", "Gâteau miel", "Sucrée", 1200),
    ("macaron_chocolat", "Macaron chocolat", "Sucrée", 800),
    ("victoria_sponge", "Victoria sponge", "Sucrée", 1200),
    ("financier", "Financier", "Sucrée", 1000),
    ("scones_fruits", "Scones fruits", "Sucrée", 1000),
    ("sandwich_oeuf_mayo", "Sandwich œuf mayo", "Salée", 1500),
    ("sandwich_le_messager", "Sandwich Le Messager", "Salée", 2000),
    ("rouleau_dinde", "Rouleau dinde", "Salée", 1800),
    ("croissant_jambon_fromage", "Croissant jambon-fromage", "Salée", 1800),
    ("tea_time_2_pers", "Tea Time 2 pers", "Tea Time", 8000),
    ("tea_time_2_pers_avec_rose_joven", "Tea Time 2 pers avec Rose Joven", "Tea Time", 16000,
     A_VALIDER + "la bouteille de Rose Joven comprise n'est pas déduite du stock "
     "(Rose Joven n'est pas à la carte des vins)."),
    ("tea_time_2_pers_avec_moscato", "Tea Time 2 pers avec Moscato", "Tea Time", 20000,
     A_VALIDER + "la bouteille de Moscato comprise n'est pas déduite du stock."),
]

# Boissons : (clé, nom, famille, prix FCFA, coût FCFA, suivi en stock, stock de départ, note)
BOISSONS = [
    # Page 4 — Bar & vins (prix de la carte ; coûts estimés)
    ("tour_de_cantelou_blanc", "Tour de Cantelou blanc", "Vins blancs", 10000, 4500, True, 12, COUT_ESTIME),
    ("bordeaux_blanc", "Bordeaux blanc", "Vins blancs", 20000, 9000, True, 6, COUT_ESTIME),
    ("tour_de_cantelou_rouge", "Tour de Cantelou rouge", "Vins rouges", 10000, 4500, True, 12, COUT_ESTIME),
    ("bordeaux_rouge", "Bordeaux rouge", "Vins rouges", 20000, 9000, True, 6, COUT_ESTIME),
    ("medoc", "Médoc", "Vins rouges", 20000, 9500, True, 6, COUT_ESTIME),
    ("rose", "Rosé", "Rosés", 25000, 11000, True, 6,
     COUT_ESTIME + " La carte dit seulement « Rosés » : nom du vin à préciser."),
    ("moscato", "Moscato", "Vins mousseux", 20000, 9000, True, 6, COUT_ESTIME),
    ("yby", "YBY", "Vins mousseux", 25000, 11500, True, 6, COUT_ESTIME),
    ("jack_daniel", "Jack Daniel", "Whisky", 40000, 21000, True, 3, COUT_ESTIME),
    ("monkey_shoulder", "Monkey Shoulder", "Whisky", 45000, 25000, True, 3, COUT_ESTIME),
    ("chivas_12", "Chivas 12", "Whisky", 40000, 22000, True, 3, COUT_ESTIME),
    ("black", "Black", "Whisky", 40000, 21000, True, 3,
     A_VALIDER + "prix masqué sur la photo de la carte (« ?0 000 FCFA ») : 40 000 F "
     "provisoires ; nom exact et coût (estimé) à confirmer."),
    # Hors carte (prix de vente et coûts estimés)
    ("eau_minerale_05_l", "Eau minérale 0,5 L", "Eaux", 500, 250, True, 48, HORS_CARTE),
    ("eau_minerale_15_l", "Eau minérale 1,5 L", "Eaux", 1000, 450, True, 24, HORS_CARTE),
    ("jus_de_fruits_33_cl", "Jus de fruits 33 cl", "Jus", 1000, 450, True, 24, HORS_CARTE),
    ("jus_naturel_presse", "Jus naturel pressé", "Jus", 2000, 700, False, 0,
     HORS_CARTE + " Préparé sur place : coût estimé, sans stock."),
    ("soda_33_cl", "Soda 33 cl", "Sodas", 1000, 400, True, 48,
     HORS_CARTE + " Un seul article pour cola, orange, citron : à détailler si besoin."),
    ("biere_blonde_65_cl", "Bière blonde 65 cl", "Bières", 1500, 650, True, 48, HORS_CARTE),
    ("biere_brune_65_cl", "Bière brune 65 cl", "Bières", 1500, 700, True, 24, HORS_CARTE),
    ("biere_importee_33_cl", "Bière importée 33 cl", "Bières", 2000, 900, True, 24, HORS_CARTE),
    ("cafe_expresso", "Café expresso", "Café & thé", 1000, 250, False, 0,
     HORS_CARTE + " Préparé sur place : coût estimé, sans stock."),
    ("the", "Thé", "Café & thé", 1000, 200, False, 0,
     HORS_CARTE + " Préparé sur place : coût estimé, sans stock."),
]

AVEC_ACCOMPAGNEMENT = ("Plats chauds", "Poulet DG", "Poulet pané", "Fruits de mer")
ACCOMPAGNEMENTS = ["Riz nature", "Riz Messager", "Frites plantain", "Frites pomme"]

cles = [p[0] for p in PLATS] + [b[0] for b in BOISSONS]
noms = [p[1] for p in PLATS] + [b[1] for b in BOISSONS]
assert len(cles) == len(set(cles)), "clé de produit en double dans la carte"
assert len(noms) == len(set(noms)), "nom de produit en double dans la carte"

# L'accompagnement : un choix sans supplément et sans variante.
Attributs = env['product.attribute']
accompagnement = Attributs.search([('name', '=', "Accompagnement")], limit=1) or Attributs.create({
    'name': "Accompagnement", 'create_variant': 'no_variant', 'display_type': 'pills'})
valeurs_acc = env['product.attribute.value']
for rang, nom in enumerate(ACCOMPAGNEMENTS, start=1):
    valeur = accompagnement.value_ids.filtered(lambda v, n=nom: v.name == n)
    if not valeur:
        valeur = env['product.attribute.value'].create(
            {'name': nom, 'attribute_id': accompagnement.id, 'sequence': rang})
    valeurs_acc |= valeur

entrepot = caisse_pos.picking_type_id.warehouse_id
Mouvements = env['stock.move']


MODULE = '__aite_messager__'
Identifiants = env['ir.model.data'].sudo()
poses = env['product.template']


def cout_suit_les_achats(modele):
    """Vrai pour un produit en coût moyen qui a déjà reçu un achat : son coût
    est alors celui des achats, pas l'estimation du script."""
    return getattr(modele, 'cost_method', None) == 'average' and bool(Mouvements.search_count([
        ('product_id', 'in', modele.product_variant_ids.ids), ('state', '=', 'done'),
        ('location_id.usage', '=', 'supplier')]))


def retrouver(cle, nom):
    """Le produit de clé ``cle`` : par son identifiant externe, sinon par son
    nom (base posée avant les clés, produit créé à la main) ; l'identifiant
    est alors posé. Vide s'il n'existe pas encore."""
    lien = Identifiants.search([('module', '=', MODULE), ('name', '=', 'produit_' + cle),
                                ('model', '=', 'product.template')], limit=1)
    modele = Produits.browse(lien.res_id).exists() if lien else Produits
    if not modele:
        modele = Produits.search([('name', '=', nom), ('id', 'not in', poses.ids)], limit=1)
        # Un produit déjà lié à une autre clé n'est jamais repris sous celle-ci.
        if modele and Identifiants.search_count([('module', '=', MODULE), ('model', '=', 'product.template'),
                                                 ('res_id', '=', modele.id)]):
            modele = Produits
        if modele:
            lier(cle, modele, lien)
    return modele


def lier(cle, modele, lien=None):
    if lien:
        lien.res_id = modele.id
    else:
        Identifiants.create({'module': MODULE, 'name': 'produit_' + cle,
                             'model': 'product.template', 'res_id': modele.id, 'noupdate': True})


def poser_produit(cle, nom, famille, prix, cout, suivi, depart, note):
    """Le produit de clé ``cle`` à la carte : créé, sinon remis aux valeurs
    du script (nom compris)."""
    global poses
    attendu = {
        'list_price': prix, 'standard_price': cout,  # cout None : plat, coût jamais touché
        'pos_categ_ids': familles[famille], 'categ_id': categories[famille],
    }
    modele = retrouver(cle, nom)
    if modele and cout_suit_les_achats(modele):
        attendu['standard_price'] = None   # le coût moyen des achats n'est jamais écrasé
    if not modele:
        modele = Produits.create({
            'name': nom, 'type': 'consu', 'is_storable': suivi, 'available_in_pos': True,
            'list_price': prix, 'standard_price': cout or 0,
            'taxes_id': [(6, 0, [])], 'supplier_taxes_id': [(6, 0, [])],
            'pos_categ_ids': [(6, 0, familles[famille].ids)],
            'categ_id': categories[famille].id,
            'description': note and "<p>%s</p>" % note or False,
        })
        lier(cle, modele)
        compte['produits'] += 1
    else:
        valeurs = {}
        if modele.name != nom:
            valeurs['name'] = nom
        for champ in ('list_price', 'standard_price'):
            if attendu[champ] is not None and modele[champ] != attendu[champ]:
                valeurs[champ] = attendu[champ]
        if modele.pos_categ_ids != attendu['pos_categ_ids']:
            valeurs['pos_categ_ids'] = [(6, 0, attendu['pos_categ_ids'].ids)]
        if modele.categ_id != attendu['categ_id']:
            valeurs['categ_id'] = attendu['categ_id'].id
        if modele.taxes_id:
            valeurs['taxes_id'] = [(6, 0, [])]
        if modele.supplier_taxes_id:
            valeurs['supplier_taxes_id'] = [(6, 0, [])]
        if not modele.available_in_pos or not modele.active:
            valeurs.update(available_in_pos=True, active=True)
        # Une note du script remise si elle a changé ; une note écrite par le
        # client sur un produit sans note du script n'est pas effacée.
        if note and html2plaintext(modele.description or '').strip() != note:
            valeurs['description'] = "<p>%s</p>" % note
        if modele.is_storable != suivi and not Mouvements.search_count(
                [('product_id', 'in', modele.product_variant_ids.ids)]):
            valeurs['is_storable'] = suivi
        if valeurs:
            modele.write(valeurs)
            compte['mis_a_jour'] += 1
    if famille in AVEC_ACCOMPAGNEMENT:
        ligne = modele.attribute_line_ids.filtered(lambda l: l.attribute_id == accompagnement)
        if not ligne:
            env['product.template.attribute.line'].create({
                'product_tmpl_id': modele.id, 'attribute_id': accompagnement.id,
                'value_ids': [(6, 0, valeurs_acc.ids)]})
            compte['accompagnements'] += 1
        elif ligne.value_ids != valeurs_acc:
            ligne.value_ids = [(6, 0, valeurs_acc.ids)]
            compte['accompagnements'] += 1
    poses |= modele
    produit = modele.product_variant_id
    if suivi and depart and modele.is_storable and entrepot and not Mouvements.search_count(
            [('product_id', '=', produit.id)]):
        # « Mettre la quantité à jour » sur la fiche du produit (stock de départ).
        quant = env['stock.quant'].with_context(inventory_mode=True).create({
            'product_id': produit.id, 'location_id': entrepot.lot_stock_id.id,
            'inventory_quantity': depart})
        quant.action_apply_inventory()
        compte['stocks'] += 1


for cle, nom, famille, prix, *note in PLATS:
    poser_produit(cle, nom, famille, prix, None, False, 0, note[0] if note else None)
for cle, nom, famille, prix, cout, suivi, depart, note in BOISSONS:
    poser_produit(cle, nom, famille, prix, cout, suivi, depart, note)

# Un produit des familles de la carte qui n'est plus dans le script (renommé
# avec une nouvelle clé, retiré par le client) quitte la caisse ; il n'est
# pas supprimé (historique des ventes, stock).
toutes_familles = env['pos.category'].browse([f.id for f in familles.values()])
orphelins = Produits.search([('available_in_pos', '=', True), ('id', 'not in', poses.ids),
                             ('pos_categ_ids', 'in', toutes_familles.ids)])
if orphelins:
    orphelins.write({'available_in_pos': False})
    compte['retires'] += len(orphelins)

# La base porte la carte du client : seed_restaurant.py n'y posera jamais la
# carte de démonstration.
env['ir.config_parameter'].sudo().set_param('aite.carte_client', 'messager')

if not MODE_MODULE:
    env.cr.commit()


def nombre(n, singulier, pluriel=None):
    return "%d %s" % (n, singulier if n in (0, 1) else (pluriel or singulier + 's'))


# Le bilan lisible du bouton « Poser la carte Le Messager » (mode module) :
# ce qui est en place, puis ce qui vient d'être fait (__init__.jouer_carte).
nb_en_place = Produits.search_count([('available_in_pos', '=', True),
                                     ('pos_categ_ids', 'in', toutes_familles.ids)])
BILAN = "Carte posée : %s en %s" % (nombre(nb_en_place, "produit"),
                                     nombre(len(toutes_familles), "famille"))
BILAN_CREES = [nombre(n, singulier, pluriel) for n, singulier, pluriel in (
    (compte['familles'], "famille", None), (compte['produits'], "produit", None),
    (compte['stocks'], "stock de départ", "stocks de départ"),
    (compte['accompagnements'], "choix d'accompagnement", "choix d'accompagnement")) if n]
BILAN_AUTRES = []
if compte['mis_a_jour']:
    BILAN_AUTRES.append("%s aux valeurs de la carte" % nombre(
        compte['mis_a_jour'], "produit remis", "produits remis"))
if compte['couts_moyens']:
    BILAN_AUTRES.append("%s en coût moyen (AVCO)" % nombre(
        compte['couts_moyens'], "catégorie de boissons passée", "catégories de boissons passées"))
if orphelins:
    BILAN_AUTRES.append("%s de la caisse (%s)" % (
        nombre(len(orphelins), "produit retiré", "produits retirés"),
        ", ".join(orphelins.mapped('name'))))

RESULTAT = ("seed carte Le Messager OK — créés : %(familles)d familles, %(categories)d catégories, "
      "%(produits)d produits, %(stocks)d stocks de départ, %(accompagnements)d choix "
      "d'accompagnement ; mis à jour : %(mis_a_jour)d produits ; retirés de la caisse : "
      "%(retires)d ; catégories passées en coût moyen : %(couts_moyens)d" % compte
      + (" (%s)" % ", ".join(orphelins.mapped('name')) if orphelins else "")
      + " | en place : %d produits à la carte (%d attendus), %d dans les familles de la "
        "carte, société « %s »" % (
          Produits.search_count([('available_in_pos', '=', True), ('name', 'in', noms)]),
          len(noms), Produits.search_count([('available_in_pos', '=', True),
                                            ('pos_categ_ids', 'in', toutes_familles.ids)]),
          company.name))
if not MODE_MODULE:
    print(RESULTAT)
