# -*- coding: utf-8 -*-
# Jeu de données « restaurant seul » (lot 1, partie 7, incrément 6) : la base
# de travail du restaurant (aite_resto, créée par dev/setup_env.sh --restaurant).
#
# Ce que fait ce script, comme AITE puis le manager le feraient à la mise en
# service (spécification, partie 4.4) :
#   - la salle « Salle » de la caisse « Restaurant » (posée d'office par
#     aite_pos_restaurant) porte 12 tables, numérotées de 1 à 12 ;
#   - les familles de la caisse sur trois niveaux, et les mêmes noms en
#     catégories de produit (les deux classements, PARAM-04) :
#       Nourriture > Pizzas, Petit déjeuner, Plats
#       Boisson > Alcoolisé > Bière, Vin, Whisky
#       Boisson > Non alcoolisé > Sodas, Café
#   - une carte de pizzeria-café-bar, en FCFA (prix ronds, taxes comprises :
#     aucune taxe n'est posée sur les produits, la TVA se règle avec le
#     comptable du client) ; seules les bières sont suivies en stock
#     (« Suivre l'inventaire »), avec leur stock de départ ;
#   - cinq employés aux quatre niveaux, avec un code et SANS courriel (noms
#     fictifs ; codes de démonstration, le premier chiffre suit le niveau) ;
#   - trois comptes Odoo (mot de passe = identifiant, base de développement
#     uniquement) : « caisse » (compte de la tablette : Utilisateur du Point de
#     Vente, courriel, Facturation), « manager » (Administrateur du Point de
#     Vente, Employés « Agent », Facturation, Manager des analyses AITE) et
#     « chef » (Restaurant : lecture des rapports).
#
# Rejouable : rien n'est créé deux fois (recherche par nom), une table ou un
# produit existant n'est pas modifié, le stock de départ n'est saisi que pour
# une bière qui n'a encore aucun mouvement de stock.
#
# Usage (Odoo 18 à côté, dans ../odoo18) :
#   cd ../odoo18 && $PYTHON odoo-bin shell -c ../AITE-HOUSE/dev/odoo.conf -d aite_resto \
#       --no-http < ../AITE-HOUSE/dev/seeds/seed_restaurant.py
company = env.company
compte = {'tables': 0, 'familles': 0, 'categories': 0, 'produits': 0,
          'employes': 0, 'comptes': 0, 'stocks': 0}

caisse_pos = env['pos.config'].search([
    ('company_id', '=', company.id), ('aite_mode_restaurant', '=', True)], order='id', limit=1)
if not caisse_pos:
    raise SystemExit("✗ aucune caisse au service à table contrôlé : installer d'abord "
                     "aite_pos_restaurant (dev/setup_env.sh --restaurant)")

# Une base créée par l'écran de création garde le nom de société d'Odoo :
# la graine donne un nom fictif, rien de plus.
if company.name in ("My Company", "YourCompany", "Ma société", "Votre société"):
    company.name = "Restaurant de démonstration"

# ------------------------------------------------------------------ la salle
salle = caisse_pos.floor_ids[:1]
if not salle:
    salle = env['restaurant.floor'].create({'name': "Salle", 'pos_config_ids': [(4, caisse_pos.id)]})
Tables = env['restaurant.table'].with_context(active_test=False)
# 3 rangées de 4 : tables carrées de 4 places, rondes de 2, et deux grandes de 6.
PLAN = {}
for i in range(12):
    numero = i + 1
    rangee, colonne = divmod(i, 4)
    forme, places, largeur, hauteur = (
        ('square', 4, 120, 120) if rangee == 0 else
        ('round', 2, 110, 110) if rangee == 1 else
        ('square', 6 if numero in (9, 10) else 4, 160 if numero in (9, 10) else 120, 120))
    PLAN[numero] = {
        'table_number': numero, 'floor_id': salle.id, 'shape': forme, 'seats': places,
        'width': largeur, 'height': hauteur,
        'position_h': 60 + 220 * colonne, 'position_v': 50 + 180 * rangee,
    }
for numero, valeurs in PLAN.items():
    table = Tables.search([('floor_id', '=', salle.id), ('table_number', '=', numero)], limit=1)
    if not table:
        Tables.create(valeurs)
        compte['tables'] += 1
    elif numero == 1 and (table.position_h, table.position_v, table.seats) == (100, 100, 1):
        # La table 1 posée par Odoo avec la salle : placée dans le plan.
        table.write(valeurs)

# ------------------------------------------- familles (caisse) et catégories
ARBRE = [
    ("Nourriture", [("Pizzas", []), ("Petit déjeuner", []), ("Plats", [])]),
    ("Boisson", [
        ("Alcoolisé", [("Bière", []), ("Vin", []), ("Whisky", [])]),
        ("Non alcoolisé", [("Sodas", []), ("Café", [])]),
    ]),
]
familles, categories = {}, {}


def poser(modele, nom, parent, rang, cle):
    """La famille (pos.category) ou la catégorie (product.category) ``nom``
    sous ``parent`` : trouvée, sinon créée."""
    enregistrement = env[modele].search(
        [('name', '=', nom), ('parent_id', '=', parent.id if parent else False)], limit=1)
    if not enregistrement:
        valeurs = {'name': nom, 'parent_id': parent.id if parent else False}
        if modele == 'pos.category':
            valeurs['sequence'] = rang
        enregistrement = env[modele].create(valeurs)
        compte[cle] += 1
    return enregistrement


def descendre(branches, parent_famille=None, parent_categorie=None):
    for rang, (nom, enfants) in enumerate(branches, start=1):
        famille = poser('pos.category', nom, parent_famille, rang, 'familles')
        categorie = poser('product.category', nom, parent_categorie, rang, 'categories')
        familles[nom], categories[nom] = famille, categorie
        descendre(enfants, famille, categorie)


descendre(ARBRE)

# ------------------------------------------------------------------ la carte
# (nom, famille de rangement, prix FCFA, suivi en stock, stock de départ)
CARTE = [
    ("Pizza Margherita", "Pizzas", 5000, False, 0),
    ("Pizza Reine", "Pizzas", 6000, False, 0),
    ("Pizza quatre fromages", "Pizzas", 7000, False, 0),
    ("Pizza poulet braisé", "Pizzas", 6500, False, 0),
    ("Petit déjeuner complet", "Petit déjeuner", 3500, False, 0),
    ("Omelette garnie", "Petit déjeuner", 2000, False, 0),
    ("Beignets haricots bouillie", "Petit déjeuner", 1500, False, 0),
    ("Crêpe au sucre", "Petit déjeuner", 1000, False, 0),
    ("Poulet DG", "Plats", 6000, False, 0),
    ("Ndolé crevettes", "Plats", 5000, False, 0),
    ("Poisson braisé", "Plats", 7000, False, 0),
    ("Brochettes de bœuf", "Plats", 3000, False, 0),
    ("Plantains frits", "Plats", 1000, False, 0),
    ("Frites", "Plats", 1500, False, 0),
    ("Castel 65 cl", "Bière", 1000, True, 48),
    ("33 Export 65 cl", "Bière", 1000, True, 48),
    ("Mützig 65 cl", "Bière", 1000, True, 24),
    ("Guinness 33 cl", "Bière", 1000, True, 24),
    ("Verre de vin rouge", "Vin", 2000, False, 0),
    ("Bouteille de vin rouge", "Vin", 12000, False, 0),
    ("Verre de vin blanc", "Vin", 2000, False, 0),
    ("Bouteille de vin blanc", "Vin", 12000, False, 0),
    ("Whisky (verre)", "Whisky", 3000, False, 0),
    ("Whisky 12 ans (verre)", "Whisky", 5000, False, 0),
    ("Bouteille de whisky", "Whisky", 35000, False, 0),
    ("Coca-Cola 33 cl", "Sodas", 1000, False, 0),
    ("Top Ananas 35 cl", "Sodas", 500, False, 0),
    ("Eau minérale 1,5 l", "Sodas", 1000, False, 0),
    ("Jus de foléré", "Sodas", 1000, False, 0),
    ("Café expresso", "Café", 1000, False, 0),
    ("Café crème", "Café", 1500, False, 0),
    ("Thé", "Café", 1000, False, 0),
    ("Chocolat chaud", "Café", 1500, False, 0),
]
Produits = env['product.template'].with_context(active_test=False)
entrepot = caisse_pos.picking_type_id.warehouse_id
for nom, famille, prix, suivi, depart in CARTE:
    modele = Produits.search([('name', '=', nom)], limit=1)
    if not modele:
        modele = Produits.create({
            'name': nom, 'type': 'consu', 'is_storable': suivi, 'available_in_pos': True,
            'list_price': prix, 'taxes_id': [(6, 0, [])],
            'pos_categ_ids': [(6, 0, familles[famille].ids)],
            'categ_id': categories[famille].id,
        })
        compte['produits'] += 1
    produit = modele.product_variant_id
    if suivi and depart and modele.is_storable and entrepot and not env['stock.move'].search_count(
            [('product_id', '=', produit.id)]):
        # « Mettre la quantité à jour » sur la fiche du produit (stock de départ).
        quant = env['stock.quant'].with_context(inventory_mode=True).create({
            'product_id': produit.id, 'location_id': entrepot.lot_stock_id.id,
            'inventory_quantity': depart})
        quant.action_apply_inventory()
        compte['stocks'] += 1

# ---------------------------------------------------------------- l'équipe
# Noms fictifs. Codes de démonstration (le premier chiffre suit le niveau) ;
# en production, laisser la fiche proposer un code au hasard.
EQUIPE = [
    ("Brice", 'serveur', '1001'),
    ("Nadège", 'serveur', '1002'),
    ("Clarisse", 'caissiere', '2001'),
    ("Hervé", 'superviseur', '3001'),
    ("Sandrine", 'manager', '4001'),
]
Employes = env['hr.employee'].with_context(active_test=False)
for nom, niveau, code in EQUIPE:
    if not Employes.search([('name', '=', nom), ('company_id', '=', company.id)], limit=1):
        Employes.create({'name': nom, 'aite_niveau_caisse': niveau, 'pin': code,
                         'company_id': company.id})
        compte['employes'] += 1

# ---------------------------------------------------------------- les comptes
Users = env['res.users'].with_context(no_reset_password=True, active_test=False)
groupes = lambda *refs: [(6, 0, [env.ref(r).id for r in ('base.group_user',) + refs])]
COMPTES = [
    ('caisse', "Caisse de la salle", 'caisse@restaurant.example',
     groupes('point_of_sale.group_pos_user', 'account.group_account_invoice')),
    ('manager', "Manager de la salle", 'manager@restaurant.example',
     groupes('point_of_sale.group_pos_manager', 'hr.group_hr_user',
             'account.group_account_invoice',
             'aite_pos_analytics.group_aite_pos_analytics_manager')),
    ('chef', "Chef de salle (rapports)", False,
     groupes('aite_pos_restaurant.group_lecture_rapports')),
]
for login, nom, courriel, droits in COMPTES:
    if not Users.search([('login', '=', login)], limit=1):
        Users.create({'login': login, 'name': nom, 'email': courriel, 'password': login,
                      'lang': 'fr_FR', 'company_id': company.id,
                      'company_ids': [(6, 0, company.ids)], 'groups_id': droits})
        compte['comptes'] += 1

env.cr.commit()
print("seed restaurant OK — créés : %(tables)d tables, %(familles)d familles, "
      "%(categories)d catégories, %(produits)d produits, %(employes)d employés, "
      "%(comptes)d comptes, %(stocks)d stocks de départ" % compte
      + " | en place : %d tables, %d produits à la carte, %d employés à niveau" % (
          len(salle.table_ids), env['product.template'].search_count([('available_in_pos', '=', True)]),
          env['hr.employee'].search_count([('aite_niveau_caisse', '!=', False)])))
