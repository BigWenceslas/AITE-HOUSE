# -*- coding: utf-8 -*-
# La salle et l'équipe de la démonstration du restaurant Le Messager, posées
# avec la carte (__init__.jouer_carte) dans la société courante de ``env`` :
#   - la salle « Salle » de la caisse au service à table contrôlé porte
#     12 tables (3 rangées de 4 : carrées de 4 places, rondes de 2, deux
#     grandes de 6) ;
#   - une équipe FICTIVE aux quatre niveaux de la caisse, avec un code et sans
#     courriel : 3 serveurs, 2 caissières, 1 chef de salle, 1 manager ;
#   - trois comptes Odoo de démonstration (mot de passe = identifiant, à
#     changer) : « caisse » (la tablette), « manager », « chef » (lecture des
#     rapports du restaurant).
# Rejouable : rien n'est créé deux fois (recherche par numéro, nom, identifiant),
# rien d'existant n'est modifié (sauf la table 1 posée par Odoo, placée dans le plan).
company = env.company
equipe_compte = {'tables': 0, 'employes': 0, 'comptes': 0}

caisse_pos = env['pos.config'].search([
    ('company_id', '=', company.id), ('aite_mode_restaurant', '=', True)], order='id', limit=1)

# ------------------------------------------------------------------ la salle
salle = caisse_pos.floor_ids[:1]
if not salle:
    salle = env['restaurant.floor'].create({'name': "Salle", 'pos_config_ids': [(4, caisse_pos.id)]})
Tables = env['restaurant.table'].with_context(active_test=False)
for i in range(12):
    numero = i + 1
    rangee, colonne = divmod(i, 4)
    forme, places, largeur, hauteur = (
        ('square', 4, 120, 120) if rangee == 0 else
        ('round', 2, 110, 110) if rangee == 1 else
        ('square', 6 if numero in (9, 10) else 4, 160 if numero in (9, 10) else 120, 120))
    valeurs = {
        'table_number': numero, 'floor_id': salle.id, 'shape': forme, 'seats': places,
        'width': largeur, 'height': hauteur,
        'position_h': 60 + 220 * colonne, 'position_v': 50 + 180 * rangee,
    }
    table = Tables.search([('floor_id', '=', salle.id), ('table_number', '=', numero)], limit=1)
    if not table:
        Tables.create(valeurs)
        equipe_compte['tables'] += 1
    elif numero == 1 and (table.position_h, table.position_v, table.seats) == (100, 100, 1):
        table.write(valeurs)   # la table 1 posée par Odoo avec la salle, placée dans le plan

# ---------------------------------------------------------------- l'équipe
# Codes de démonstration : le premier chiffre suit le niveau.
EQUIPE = [
    ("Brice", 'serveur', '1001'),
    ("Nadège", 'serveur', '1002'),
    ("Loïc", 'serveur', '1003'),
    ("Clarisse", 'caissiere', '2001'),
    ("Prisca", 'caissiere', '2002'),
    ("Hervé", 'superviseur', '3001'),
    ("Sandrine", 'manager', '4001'),
]
Employes = env['hr.employee'].with_context(active_test=False)
codes_pris = set(Employes.search([('company_id', '=', company.id)]).mapped('pin'))
for nom, niveau, code in EQUIPE:
    if Employes.search([('name', '=', nom), ('company_id', '=', company.id)], limit=1):
        continue
    valeurs = {'name': nom, 'aite_niveau_caisse': niveau, 'company_id': company.id}
    if code not in codes_pris:     # sinon la fiche propose un code libre
        valeurs['pin'] = code
    Employes.create(valeurs)
    equipe_compte['employes'] += 1

# ---------------------------------------------------------------- les comptes
Users = env['res.users'].with_context(no_reset_password=True, active_test=False)


def groupes(*refs):
    return [(6, 0, [env.ref(r).id for r in ('base.group_user',) + refs])]


# Chaque compte a un courriel : Odoo écrit l'ouverture, la fermeture et la
# validation de la caisse au nom du compte connecté, et refuse sans courriel
# (« Impossible d'envoyer le message, veuillez configurer l'adresse e-mail de
# l'expéditeur »). Adresses de démonstration, à remplacer par celles du client.
COMPTES = [
    ('caisse', "Caisse de la salle", 'caisse@restaurant.example',
     groupes('point_of_sale.group_pos_user', 'account.group_account_invoice')),
    ('manager', "Manager de la salle", 'manager@restaurant.example', groupes(
        'point_of_sale.group_pos_manager', 'hr.group_hr_user', 'account.group_account_invoice',
        'aite_pos_analytics.group_aite_pos_analytics_manager')),
    ('chef', "Chef de salle (rapports)", 'chef@restaurant.example',
     groupes('aite_pos_restaurant.group_lecture_rapports')),
]
for login, nom, courriel, droits in COMPTES:
    user = Users.search([('login', '=', login)], limit=1)
    if not user:
        Users.create({'login': login, 'name': nom, 'email': courriel, 'password': login,
                      'lang': 'fr_FR', 'company_id': company.id,
                      'company_ids': [(6, 0, company.ids)], 'groups_id': droits})
        equipe_compte['comptes'] += 1
    elif not user.email:
        user.email = courriel   # compte de démonstration posé sans courriel (18.0.1.3.0)

RESULTAT_EQUIPE = ("équipe : %(tables)d tables, %(employes)d employés, %(comptes)d comptes créés"
                   % equipe_compte + " | en place : %d tables, %d employés à niveau" % (
                       len(salle.table_ids),
                       Employes.search_count([('aite_niveau_caisse', '!=', False), ('company_id', '=', company.id)])))
