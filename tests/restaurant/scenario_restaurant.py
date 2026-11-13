# -*- coding: utf-8 -*-
"""
Parcours « utilisateur novice » — la caisse du restaurant (lot 1).
Exécuté dans le shell Odoo, sur une base restaurant (créée comme l'écran de
création : pays Cameroun, français, sans démonstration) :
    cd ../odoo18 && $PYTHON odoo-bin shell -c <conf> -d <base> --no-http \
        < ../AITE-HOUSE/tests/restaurant/scenario_restaurant.py

Le scénario ne fait QUE ce qu'un utilisateur ferait, rôle par rôle : AITE
installe et règle les comptes, le manager saisit son équipe et règle la
caisse, la caissière ouvre la caisse, etc. Le côté caisse est joué par les
appels que fait la caisse (synchronisation, requêtes), sous le compte de la
caisse. Tout est annulé à la fin (rollback).

Il sert de spécification : chaque incrément y ajoute ses vérifications
(spécification, partie 6.5). Incrément 1 : installation, comptes, équipe,
réglage de la case, messages sans courriel, ardoise réglée (AH-01).
"""
import contextlib
import sys
from uuid import uuid4

from lxml import etree

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import Form

ok_count = 0
ko = []


def check(label, cond, detail=""):
    global ok_count
    if cond:
        ok_count += 1
        print("  ✓ " + label)
    else:
        ko.append(label)
        print("  ✗ " + label + ("  → " + str(detail) if detail else ""))


def refus(fonction):
    """Le message de refus affiché à l'utilisateur, ou None si rien n'est refusé."""
    try:
        with env.cr.savepoint():
            fonction()
    except ValidationError as erreur:
        return erreur.args[0]
    return None


company = env.company

print("\n═══ 1. AITE installe le module (incrément 1) ═══")
restaurant = env['pos.config'].search([
    ('company_id', '=', company.id), ('name', '=', "Restaurant")])
check("une caisse « Restaurant » existe", len(restaurant) == 1, restaurant)
check("la case « Service à table contrôlé » est cochée",
      restaurant.aite_mode_restaurant and restaurant._aite_actif())
check("« Contrôle des prix » coché", restaurant.restrict_price_control)
check("remises à la ligne et globales décochées",
      not restaurant.manual_discount and not restaurant.module_pos_discount)
check("partage et impression de l'addition cochés",
      restaurant.iface_splitbill and restaurant.iface_printbill)
check("« Suivi des modifications de commandes » décoché",
      not restaurant.order_edit_tracking)
check("« Ignorer l'écran de prévisualisation » décoché",
      not restaurant.iface_print_skip_screen)
modes = restaurant.payment_method_ids
check("modes « Espèces » et « Mobile Money » seuls",
      sorted(modes.mapped('name')) == ["Espèces", "Mobile Money"], modes.mapped('name'))
check("« Mobile Money » sur un journal de banque à son nom",
      modes.filtered(lambda m: m.name == "Mobile Money").journal_id.mapped('name')
      == ["Mobile Money"])
check("la salle s'appelle « Salle »", restaurant.floor_ids.mapped('name') == ["Salle"],
      restaurant.floor_ids.mapped('name'))
check("aucun modèle hôtelier (aite.hotel.*) dans la base",
      not env['ir.model'].search_count([('model', '=like', 'aite.hotel.%')]))
check("la société est en FCFA", company.currency_id.name == 'XAF',
      company.currency_id.name)

print("\n═══ 2. AITE règle les comptes (incrément 1) ═══")
Users = env['res.users'].with_context(no_reset_password=True)
caisse = Users.create({
    'name': "Caisse du restaurant", 'login': 'scenario_caisse_resto',
    'email': 'caisse@restaurant.example',
    'groups_id': [(6, 0, [env.ref('base.group_user').id,
                          env.ref('point_of_sale.group_pos_user').id,
                          env.ref('account.group_account_invoice').id])],
})
manager = Users.create({
    'name': "Manager du restaurant", 'login': 'scenario_manager_resto',
    'email': 'manager@restaurant.example',
    'groups_id': [(6, 0, [env.ref('base.group_user').id,
                          env.ref('point_of_sale.group_pos_manager').id,
                          env.ref('hr.group_hr_user').id])],
})
check("le compte de la caisse a un courriel et le droit Facturation",
      bool(caisse.email) and caisse.has_group('account.group_account_invoice'))
check("le compte de la caisse est « Utilisateur » du Point de Vente, sans droit RH",
      caisse.has_group('point_of_sale.group_pos_user')
      and not caisse.has_group('point_of_sale.group_pos_manager')
      and not caisse.has_group('hr.group_hr_user'))
check("le manager a Employés « Agent » et l'administration du Point de Vente",
      manager.has_group('hr.group_hr_user')
      and manager.has_group('point_of_sale.group_pos_manager'))

print("\n═══ 3. Le manager saisit son équipe (incrément 1) ═══")
Employes = env['hr.employee'].with_user(manager)
fiche = Form(Employes)
fiche.name = "Awa"
fiche.aite_niveau_caisse = 'serveur'
code_awa = fiche.pin
check("Awa serveuse : un code est proposé dès le niveau choisi", bool(code_awa))
check("le code proposé fait 4 chiffres",
      bool(code_awa) and len(code_awa) == 4 and code_awa.isdigit(), code_awa)
awa = fiche.save()
check("la fiche s'enregistre sans courriel", not awa.work_email and awa.pin == code_awa)
arch = etree.fromstring(Employes.get_view(view_type='form')['arch'])
check("niveau et code sur la première page de la fiche, hors des onglets",
      arch.xpath("//field[@name='pin']") and arch.xpath("//field[@name='aite_niveau_caisse']")
      and not arch.xpath("//notebook//field[@name='pin']")
      and not arch.xpath("//notebook//field[@name='aite_niveau_caisse']"))
check("le code s'appelle « Code caisse »",
      arch.xpath("//field[@name='pin']/@string") == ["Code caisse"])

carine = Employes.create({'name': "Carine", 'aite_niveau_caisse': 'caissiere', 'pin': '3333'})
message = refus(lambda: Employes.create(
    {'name': "Bertrand", 'aite_niveau_caisse': 'serveur', 'pin': '482'}))
check("un code de 3 chiffres est refusé, le message dit quoi faire",
      message == "Le code doit faire exactement 4 chiffres.", message)
message = refus(lambda: Employes.create(
    {'name': "Moussa", 'aite_niveau_caisse': 'serveur', 'pin': '3333'}))
check("le code de Carine donné à Moussa est refusé",
      bool(message) and "Choisissez quatre autres chiffres" in message, message)
check("le refus ne dit pas à qui est ce code", bool(message) and "Carine" not in message)
message = refus(lambda: Employes.create(
    {'name': "Bertrand", 'aite_niveau_caisse': 'serveur', 'pin': False}))
check("un niveau sans code est refusé, le message dit quoi faire",
      message == "Donnez un code à 4 chiffres à Bertrand : sans code, il ne peut "
                 "pas utiliser la caisse.", message)
fiche = Form(Employes)
fiche.name = "Moussa"
fiche.aite_niveau_caisse = 'serveur'
moussa = fiche.save()
fiche = Form(Employes)
fiche.name = "Paul"
fiche.aite_niveau_caisse = 'superviseur'
paul = fiche.save()
fiche = Form(Employes)
fiche.name = "Fanta"
fiche.aite_niveau_caisse = 'manager'
fanta = fiche.save()
check("Paul est chef de salle, Fanta manager",
      paul.aite_niveau_caisse == 'superviseur' and fanta.aite_niveau_caisse == 'manager')
equipe = awa | carine | moussa | paul | fanta
check("cinq codes, tous différents", len(set(equipe.mapped('pin'))) == 5,
      equipe.mapped('pin'))
check("aucun courriel demandé à l'équipe", not equipe.filtered('work_email'))
comptable = Employes.create({'name': "Comptable", 'pin': '9090'})
message = None
try:
    with env.cr.savepoint():
        copie = awa.with_user(manager).copy()  # bouton « Dupliquer » de la fiche
except ValidationError as erreur:
    message = erreur.args[0]
check("« Dupliquer » la fiche d'Awa : la copie s'enregistre", message is None, message)
check("la copie arrive sans niveau ni code : elle n'est pas sur la caisse",
      message is None and not copie.aite_niveau_caisse and not copie.pin)

print("\n═══ 4. AITE règle la caisse dans les réglages du Point de Vente (incrément 1) ═══")
# La page des réglages du Point de Vente est réservée à Administration /
# Paramètres (menu point_of_sale.menu_pos_global_settings) : le compte du
# manager (Administrateur du Point de Vente) ne l'ouvre pas. À l'incrément 1,
# c'est AITE qui coche ou décoche la case. Qui règle le délai de l'orange
# (incrément 5) est à trancher par AITE.
aite = env.ref('base.user_admin')
Reglages = env['res.config.settings'].with_user(aite)
vue = etree.fromstring(Reglages.get_view(view_type='form')['arch'])
reglage = vue.xpath("//setting[@id='aite_mode_restaurant']")
check("la case porte sa phrase « ce qui va se passer »",
      bool(reglage) and "chaque employé tape son code à 4 chiffres" in (reglage[0].get('help') or ''))
bloc = vue.xpath("//block[@id='restaurant_section']/setting")
check("la case vient juste après « Est un bar/restaurant » (la phrase dit « ci-dessous »)",
      len(bloc) > 1 and bloc[0].xpath("./field[@name='pos_module_pos_restaurant']")
      and bloc[1].get('id') == 'aite_mode_restaurant')
R31 = ("Décochez d'abord « Service à table contrôlé » : sans les codes "
       "personnels, la caisse ne saurait plus qui fait quoi.")


def enregistrer_reglages(**valeurs):
    """AITE ouvre les réglages de la caisse « Restaurant », change des cases
    et enregistre ; rend le refus affiché, ou None."""
    def faire():
        fiche = Form(Reglages)
        fiche.pos_config_id = restaurant
        for champ, valeur in valeurs.items():
            setattr(fiche, champ, valeur)
        fiche.save()
    return refus(faire)


message = enregistrer_reglages(pos_module_pos_hr=False)
check("décocher « Se connecter avec Employés » est refusé (R31)", message == R31, message)
fiche = Form(Reglages)
fiche.pos_config_id = restaurant
fiche.pos_module_pos_restaurant = False
try:
    fiche.pos_aite_mode_restaurant = False
    visible = True
except AssertionError:
    visible = False
check("« Est un bar/restaurant » décoché : la case reste à l'écran pour être "
      "décochée d'abord", visible)
ardoise = env['pos.payment.method'].search([
    ('company_id', '=', company.id), ('is_aite_credit', '=', True)], limit=1) \
    if 'is_aite_credit' in env['pos.payment.method']._fields else env['pos.payment.method']
if ardoise:
    # AITE propose l'ardoise sur la caisse (caisse fermée).
    with Form(Reglages) as fiche:
        fiche.pos_config_id = restaurant
        fiche.pos_payment_method_ids.add(ardoise)
    check("AITE ajoute « Ardoise client » à la caisse", ardoise in restaurant.payment_method_ids)

print("\n═══ 4 bis. AITE recharge le plan comptable (incrément 1) ═══")
# Le client a arrêté le service à table contrôlé (case décochée), puis AITE
# recharge le plan comptable : la caisse « Restaurant » ne revient pas.
# Annulé aussitôt (la suite du parcours garde la caisse en mode).
with contextlib.closing(env.cr.savepoint()):
    restaurant.aite_mode_restaurant = False
    domaine = [('company_id', '=', company.id)]
    avant = (env['pos.config'].search_count(domaine),
             env['account.journal'].search_count(domaine),
             env['pos.payment.method'].search_count(domaine))
    env['account.chart.template'].try_loading(
        company.chart_template, company=company, install_demo=False, force_create=False)
    apres = (env['pos.config'].search_count(domaine),
             env['account.journal'].search_count(domaine),
             env['pos.payment.method'].search_count(domaine))
    check("aucune caisse, aucun journal, aucun mode de paiement de plus "
          "(caisses, journaux, modes)", apres == avant, (avant, apres))
env.invalidate_all()
check("la caisse « Restaurant » est de nouveau au service à table contrôlé",
      restaurant.aite_mode_restaurant)

print("\n═══ 5. Ce que la caisse reçoit au démarrage (incrément 1) ═══")
restaurant.with_user(caisse).open_ui()
session = restaurant.current_session_id
donnees = session.with_user(caisse).load_data(['pos.config', 'hr.employee'])
noms = {e['name'] for e in donnees['hr.employee']['data']}
check("les cinq employés à niveau arrivent en caisse, sous le compte de la caisse",
      noms == {"Awa", "Carine", "Moussa", "Paul", "Fanta"}, noms)
check("un employé sans niveau n'apparaît pas sur la caisse", "Comptable" not in noms)
roles = {e['name']: e['_role'] for e in donnees['hr.employee']['data']}
check("seule Fanta (manager) a le rôle manager d'Odoo",
      [n for n, r in roles.items() if r == 'manager'] == ["Fanta"], roles)
check("la caisse reçoit le tableau des droits",
      donnees['pos.session']['data'][0].get('_aite_droits', {}).get('encaisser') == 'caissiere')

print("\n═══ 6. La caissière ouvre la caisse, sans courriel (incrément 1) ═══")
session.employee_id = carine  # ce que pos_hr écrit quand Carine tape son code
try:
    with env.cr.savepoint():
        session.with_user(caisse).set_opening_control(0, None)
    erreur = None
except Exception as exc:  # noqa: BLE001 — l'erreur est le constat
    erreur = exc
check("la caisse s'ouvre alors que Carine n'a pas de courriel", erreur is None, erreur)
check("la session est ouverte", session.state == 'opened', session.state)

print("\n═══ 7. Paul sort des espèces, sans courriel (incrément 1) ═══")
try:
    with env.cr.savepoint():
        session.with_user(caisse).try_cash_in_out(
            'out', 2000, "Glace pour le bar", {'translatedType': 'out', 'employee_id': paul.id})
        session.with_user(caisse).log_partner_message(
            paul.work_contact_id.id, "Sortie de 2 000 F", 'CASH_DRAWER_ACTION')
    erreur = None
except Exception as exc:  # noqa: BLE001
    erreur = exc
check("la sortie d'espèces se termine sans erreur", erreur is None, erreur)
check("une seule sortie enregistrée, au nom de Paul",
      len(session.statement_line_ids) == 1 and session.statement_line_ids.employee_id == paul)
check("l'historique de la session dit « Tiroir-caisse ouvert », signé Paul",
      bool(session.message_ids.filtered(
          lambda m: m.author_id == paul.work_contact_id
          and "Tiroir-caisse ouvert" in (m.body or ''))))

if ardoise:
    print("\n═══ 8. Ardoise sur une table encore ouverte (AH-01, incrément 1) ═══")
    client = env['res.partner'].create({'name': "Client habitué"})
    castel = env['product.product'].create({
        'name': "Castel", 'type': 'consu', 'available_in_pos': True,
        'list_price': 1000, 'taxes_id': [(5, 0, 0)]})

    def synchroniser(uuid, state, existante=None):
        """L'addition telle que la caisse l'envoie (sync_from_ui)."""
        data = {
            'uuid': uuid, 'name': "Commande %s" % uuid, 'session_id': session.id,
            'state': state, 'partner_id': client.id, 'user_id': caisse.id,
            'pricelist_id': restaurant.pricelist_id.id or False,
            'fiscal_position_id': False, 'sequence_number': 1, 'to_invoice': False,
            'date_order': fields.Datetime.to_string(fields.Datetime.now()),
            'amount_tax': 0, 'amount_total': 2000, 'amount_paid': 2000,
            'amount_return': 0, 'last_order_preparation_change': '{}',
            'table_id': restaurant.floor_ids.table_ids[:1].id, 'customer_count': 2,
            'lines': [(0, 0, {'product_id': castel.id, 'qty': 2, 'price_unit': 1000,
                              'price_subtotal': 2000, 'price_subtotal_incl': 2000,
                              'tax_ids': [(6, 0, [])]})],
            'payment_ids': [(0, 0, {'amount': 2000, 'name': fields.Datetime.now(),
                                    'payment_method_id': ardoise.id})],
        }
        if existante:
            data['lines'] = [(1, l.id, {'qty': l.qty}) for l in existante.lines]
            data['payment_ids'] = [(1, p.id, {'amount': p.amount})
                                   for p in existante.payment_ids]
        env['pos.order'].with_user(caisse).sync_from_ui([data])
        return env['pos.order'].search([('uuid', '=', uuid)])

    Ardoises = env['aite.pos.credit']
    table = synchroniser(str(uuid4()), 'draft')
    check("table ouverte avec un paiement ardoise : aucune ardoise",
          table.state == 'draft' and not Ardoises.search_count([('order_id', '=', table.id)]))
    table.with_user(caisse).action_pos_order_cancel()
    check("table annulée : aucune ardoise ouverte",
          table.state == 'cancel' and not Ardoises.search_count(
              [('order_id', '=', table.id), ('state', '=', 'open')]))
    uuid = str(uuid4())
    table = synchroniser(uuid, 'draft')
    table = synchroniser(uuid, 'paid', existante=table)
    check("la même table réglée ouvre une ardoise de 2 000 F",
          table.state == 'paid' and Ardoises.search([('order_id', '=', table.id)]).amount_total == 2000)
else:
    print("\n(aite_pos_credit absent : vérifications de l'ardoise sautées)")

env.cr.rollback()
print("\n══════════════════════════════════════")
print("RÉSULTAT : %d vérifications OK, %d KO" % (ok_count, len(ko)))
for k in ko:
    print("  KO : " + k)
sys.exit(1 if ko else 0)
