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
Incrément 2 : ouverture et fermeture par code vérifié par le serveur (« ouverte
par » et « fermée par » écrits à l'ouverture et à la fermeture effectives, un
second poste resté sur la caisse fermée n'est pas refusé), espèces réservées au
chef de salle, modes « payer plus tard » réservés au manager (AH-02).
Incrément 3 : la table (personnes, « ouverte par » figé, heure posée par le
serveur, « encaissée par »), le journal des saisies (qui a saisi quoi, ni la
division ni la réunion ne comptent), la quantité verrouillée à l'envoi, le
numéro qui n'est pas sur le plan, la vente sans table fermée d'office.
Incrément 4 : le verrou après envoi (retrait sans code tracé), l'annulation
avec le code d'un chef de salle et un motif (refus d'un code de serveur, même
demande renvoyée sans double), la division et la réunion qui ne sont pas des
annulations, la table encore ouverte annulée sans code à la fermeture, le
rapport des annulations lu par le chef de salle avec le seul profil de
lecture.
Incrément 5 : le délai de l'orange (posé à 60, porté à 90 : la phrase suit le
nombre ; 0 refusé) et le refus des produits épuisés (réglage et sa phrase ;
produit suivi à 0, entrée de stock, bouteilles envoyées sur une table ouverte
déduites sur tous les postes, table encaissée comptée une seule fois).
Incrément 6 (partie 6a) : « Personnes et tables » (la table réunie compte une
fois avec ses personnes additionnées, la part « 12B » ne compte pas, les
additions ouvertes et annulées non plus), les quantités vendues de « Détails
des ventes », le rapport de fermeture (tables, personnes, annulations), les
ventes par famille (Boisson > Alcoolisé > Bière) et, si la passerelle
aite_pos_analytics_hr est installée, le serveur et la caissière dans les
analyses.
"""
import contextlib
import sys
from uuid import uuid4

from lxml import etree

from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tests import Form
from odoo.tools.safe_eval import safe_eval

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


def refus_utilisateur(fonction):
    """Le message d'un refus de la caisse (UserError), ou None."""
    try:
        with env.cr.savepoint():
            fonction()
    except UserError as erreur:
        return erreur.args[0]
    return None


def refus_acces(fonction):
    """Vrai si Odoo refuse l'accès (AccessError)."""
    try:
        with env.cr.savepoint():
            fonction()
    except AccessError:
        return True
    return False


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
motifs = env['aite.restaurant.motif'].search([], order='sequence, id') \
    if 'aite.restaurant.motif' in env else []
check("cinq motifs d'annulation posés d'office (incrément 4)",
      [m.name for m in motifs] == ["Erreur de saisie", "Client parti", "Plat refusé",
                                   "Produit manquant", "Autre"], [m.name for m in motifs])
check("« Autre » demande une précision",
      [m.name for m in motifs if m.precision_requise] == ["Autre"])

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
                          env.ref('hr.group_hr_user').id,
                          env.ref('account.group_account_invoice').id])],
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
# Revue de 6a, constat 2 : le rapport de session et « Détails des ventes »
# d'Odoo lisent les paiements comptables (account.payment) dès qu'une vente
# est payée ; sans le droit Facturation, Odoo refuse le rapport au manager.
check("le manager a aussi le droit Facturation : il ouvre le rapport de session",
      manager.has_group('account.group_account_invoice'))

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

print("\n═══ 4 ter. Le délai de l'orange et les produits épuisés (incrément 5) ═══")
# Réglés dans la même page que la case (qui les règle est à trancher par AITE,
# voir plus haut) ; ils ne sont proposés qu'au service à table contrôlé.
check("orange après 60 minutes, produits épuisés refusés : posés d'office",
      getattr(restaurant, 'aite_delai_alerte', None) == 60
      and getattr(restaurant, 'aite_refus_epuise', None) is True,
      (getattr(restaurant, 'aite_delai_alerte', None), getattr(restaurant, 'aite_refus_epuise', None)))
ids = [r.get('id') for r in bloc]
check("les deux réglages sont dans le bloc Restaurant, après la case",
      'aite_delai_alerte' in ids and 'aite_refus_epuise' in ids
      and ids.index('aite_mode_restaurant') < ids.index('aite_delai_alerte'), ids)
fiche = Form(Reglages)
fiche.pos_config_id = restaurant
phrase_60 = fiche.pos_aite_phrase_delai if 'pos_aite_phrase_delai' in Reglages._fields else ''
check("la phrase du délai dit « plus de 60 minutes »",
      "Une table ouverte depuis plus de 60 minutes passe à l'orange sur le plan" in (phrase_60 or ''),
      phrase_60)
message = None
if 'pos_aite_delai_alerte' in Reglages._fields:
    fiche.pos_aite_delai_alerte = 90
    check("le délai porté à 90 : la phrase dit « 90 minutes » avant même d'enregistrer",
          "ouverte depuis plus de 90 minutes passe à l'orange" in (fiche.pos_aite_phrase_delai or ''),
          fiche.pos_aite_phrase_delai)
    message = refus(fiche.save)
    check("enregistré : la caisse passe à 90 minutes",
          message is None and restaurant.aite_delai_alerte == 90,
          message or restaurant.aite_delai_alerte)
    message = enregistrer_reglages(pos_aite_delai_alerte=0)
    check("un délai de 0 minute est refusé, le message dit quoi faire",
          message == "Le délai avant l'orange doit être d'au moins 1 minute.", message)
else:
    check("le réglage « Délai avant l'orange (minutes) » existe", False)
reglage = vue.xpath("//setting[@id='aite_refus_epuise']")
check("« Refuser la vente des produits épuisés » porte sa phrase « ce qui va se passer »",
      bool(reglage) and "Saisissez le stock de départ avant le premier service"
      in (reglage[0].get('help') or ''))

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

print("\n═══ 6. La caissière ouvre la caisse, sans courriel (incréments 1 et 2) ═══")
# La caisse demande un code ; le serveur le vérifie (aite_ouvrir_caisse).
R3 = ("La caisse n'est pas encore ouverte. La caissière ou un chef de salle "
      "doit l'ouvrir avec son code.")
poste = session.with_user(caisse)
reponse = poste.aite_ouvrir_caisse(awa.pin)
check("Awa (serveuse) tape son code pour ouvrir : refusé (R3)",
      reponse == {'erreur': R3}, reponse)
message = refus_utilisateur(lambda: poste.set_opening_control(0, None))
check("ouvrir sans code (contrôle d'ouverture d'Odoo seul) : refusé (R3)",
      message == R3, message)
check("la caisse n'est toujours pas ouverte", session.state == 'opening_control',
      session.state)
session.employee_id = awa  # ce qu'un autre poste écrit quand Awa tape son code
reponse = poste.aite_ouvrir_caisse('3333')
check("Carine tape son code pour ouvrir : accepté", reponse.get('id') == carine.id, reponse)
check("tant que le fond de caisse n'est pas validé, personne n'a « ouvert » la caisse",
      not session.aite_ouverte_par_id and not session.message_ids.filtered(
          lambda m: "Caisse ouverte par" in (m.body or '')), session.aite_ouverte_par_id.name)
try:
    with env.cr.savepoint():
        session.employee_id = carine  # ce que pos_hr écrit sur ce poste
        poste.set_opening_control(0, None)
    erreur = None
except Exception as exc:  # noqa: BLE001 — l'erreur est le constat
    erreur = exc
check("le fond de caisse validé : la caisse s'ouvre, sans courriel", erreur is None, erreur)
check("la session est ouverte", session.state == 'opened', session.state)
check("« Caisse ouverte par » : Carine, vérifiée par le serveur",
      session.aite_ouverte_par_id == carine, session.aite_ouverte_par_id.name)
check("l'historique de la session dit « Caisse ouverte par Carine »",
      bool(session.message_ids.filtered(
          lambda m: "Caisse ouverte par Carine" in (m.body or ''))))
reponse = poste.aite_ouvrir_caisse(awa.pin)
check("un second poste, resté sur la caisse fermée : Awa tape son code, la caisse "
      "lui répond qu'elle est déjà ouverte (pas R3)", reponse == {'deja_ouverte': True}, reponse)
check("« Caisse ouverte par » reste Carine", session.aite_ouverte_par_id == carine,
      session.aite_ouverte_par_id.name)

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
R15 = "Seul un chef de salle ou le manager peut sortir ou entrer des espèces."
for qui in (awa, carine):
    message = refus_utilisateur(lambda: poste.try_cash_in_out(
        'out', 1000, "Monnaie", {'translatedType': 'out', 'employee_id': qui.id}))
    check("%s sort des espèces : refusé (R15)" % qui.name, message == R15, message)
check("toujours une seule sortie d'espèces", len(session.statement_line_ids) == 1)

print("\n═══ 7 bis. Ce que la caisse sait des modes de paiement (AH-02, incrément 2) ═══")
modes = session.with_user(caisse).load_data(['pos.config', 'pos.payment.method'])
marques = {m['name']: m.get('_aite_reserve_manager') for m in modes['pos.payment.method']['data']
           if m['id'] in restaurant.payment_method_ids.ids}
check("Espèces et Mobile Money : proposés à toute personne qui encaisse",
      marques.get("Espèces") is False and marques.get("Mobile Money") is False, marques)
if ardoise:
    check("« Ardoise client » : réservé au manager en caisse",
          marques.get(ardoise.name) is True, marques)

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

print("\n═══ 10. Le manager règle la vente sans table et dessine ses tables (incrément 3) ═══")
reglage = vue.xpath("//setting[@id='aite_vente_sans_table']")
check("le réglage « Autoriser la vente sans table » porte sa phrase « ce qui va se passer »",
      bool(reglage) and "le bouton « + » n'apparaît pas" in (reglage[0].get('help') or ''))
check("la vente sans table est fermée d'office (le « + » n'apparaît pas)",
      not restaurant.aite_vente_sans_table)
# Les postes gardent la valeur chargée à l'ouverture : la case se change
# caisse fermée, comme celle du service à table contrôlé (revue de
# l'incrément 3).
check("la phrase dit que la case se change seulement caisse fermée",
      bool(reglage) and "Se change seulement caisse fermée." in (reglage[0].get('help') or ''))
message = refus_utilisateur(lambda: restaurant.write({'aite_vente_sans_table': True}))
check("pendant le service, cocher la vente sans table est refusé",
      bool(message) and not restaurant.aite_vente_sans_table, message)
# Le plan se dessine dans la gestion (Point de Vente → Configuration → Plans de salle).
Tables = env['restaurant.table'].with_user(manager)
salle = restaurant.floor_ids[:1]
table_12 = Tables.create({'floor_id': salle.id, 'table_number': 12, 'seats': 4})
table_7 = Tables.create({'floor_id': salle.id, 'table_number': 7, 'seats': 4})
table_9 = Tables.create({'floor_id': salle.id, 'table_number': 9, 'seats': 2})
check("le manager ajoute les tables 7 et 12 à la salle",
      {7, 12} <= set(salle.table_ids.mapped('table_number')))
castel = env['product.product'].search([('name', '=', "Castel")], limit=1) or \
    env['product.product'].create({'name': "Castel", 'type': 'consu', 'available_in_pos': True,
                                   'list_price': 1000, 'taxes_id': [(5, 0, 0)]})
especes = restaurant.payment_method_ids.filtered(lambda m: m.name == "Espèces")


def nouvelle_addition(table=None, personnes=4, ouverte_par=None, nom=False):
    """La copie d'une addition sur un poste de la caisse."""
    return {
        'uuid': str(uuid4()), 'lignes': {}, 'supprimees': [],
        'preparation': {'lines': {}, 'metadata': {}, 'generalNote': '', 'sittingMode': 'dine in'},
        'valeurs': {'table_id': table.id if table else False, 'customer_count': personnes,
                    'aite_ouverte_par_id': ouverte_par.id if ouverte_par else False,
                    'employee_id': ouverte_par.id if ouverte_par else False,
                    'floating_order_name': nom, 'aite_heure_ouverture': False,
                    'aite_origine_uuid': False},
    }


def ajouter(addition, produit, qty):
    cle = str(uuid4())
    addition['lignes'][cle] = {'id': False, 'produit': produit, 'qty': qty, 'modifiee': True}
    return cle


def envoyer(addition):
    """« J'envoie » : la caisse note ce qui est parti."""
    addition['preparation']['lines'] = {
        cle: {'uuid': cle, 'product_id': l['produit'].id, 'name': l['produit'].name,
              'note': '', 'quantity': l['qty']} for cle, l in addition['lignes'].items()}
    addition['preparation']['metadata'] = {
        'serverDate': fields.Datetime.to_string(fields.Datetime.now())}


def caisse_envoie(addition, employe, etat='draft', deplacement=False, payer=None):
    """Ce que la caisse envoie (sync_from_ui), sous le compte de la caisse,
    avec la personne identifiée sur le poste ; la copie reprend la réponse."""
    import json
    maintenant = fields.Datetime.to_string(fields.Datetime.now())
    addition['valeurs']['employee_id'] = employe.id
    lignes, total = [], 0
    for cle, l in addition['lignes'].items():
        valeurs = {'uuid': cle, 'product_id': l['produit'].id, 'qty': l['qty'],
                   'price_unit': l['produit'].lst_price, 'discount': 0, 'tax_ids': [(6, 0, [])],
                   'price_subtotal': l['produit'].lst_price * l['qty'],
                   'price_subtotal_incl': l['produit'].lst_price * l['qty']}
        total += l['produit'].lst_price * l['qty']
        if not l['id']:
            lignes.append([0, 0, valeurs])
        elif l['modifiee']:
            lignes.append([1, l['id'], valeurs])
    lignes += [[2, i] for i in addition['supprimees']]
    donnees = {
        'uuid': addition['uuid'], 'name': "Commande %s" % addition['uuid'], 'session_id': session.id,
        'state': etat, 'user_id': caisse.id, 'pricelist_id': restaurant.pricelist_id.id or False,
        'fiscal_position_id': False, 'sequence_number': 1, 'to_invoice': False,
        'date_order': maintenant, 'amount_tax': 0, 'amount_total': total,
        'amount_paid': total if payer else 0, 'amount_return': 0,
        'last_order_preparation_change': json.dumps(addition['preparation']),
        'lines': lignes, **addition['valeurs'],
        'payment_ids': [[0, 0, {'amount': total, 'name': maintenant,
                                'payment_method_id': payer.id}]] if payer else [],
    }
    reponse = env['pos.order'].with_user(caisse).with_context(
        config_id=restaurant.id, aite_employee_id=employe.id,
        aite_deplacement=deplacement).sync_from_ui([donnees])
    lu = reponse['pos.order'][0]
    par_cle = {l['uuid']: l['id'] for l in reponse['pos.order.line']}
    for cle, l in addition['lignes'].items():
        l.update(id=par_cle.get(cle, l['id']), modifiee=False)
    addition['supprimees'] = []
    addition['preparation'] = json.loads(lu['last_order_preparation_change'] or '{}')
    for champ in ('customer_count', 'aite_ouverte_par_id', 'aite_origine_uuid'):
        addition['valeurs'][champ] = lu.get(champ)
    heure = lu.get('aite_heure_ouverture')
    addition['valeurs']['aite_heure_ouverture'] = (
        fields.Datetime.to_string(heure) if heure and not isinstance(heure, str) else heure)
    return env['pos.order'].browse(lu['id'])


Saisies = env['aite.restaurant.saisie']

print("\n═══ 11. Awa ouvre la table 12 : 4 personnes (incrément 3) ═══")
# Sur la caisse : la table 12, son code, « 4 » ; l'addition part aussitôt au serveur.
avant = fields.Datetime.now()
t12 = nouvelle_addition(table_12, 4, awa)
table = caisse_envoie(t12, awa)
check("l'addition de la table 12 est enregistrée à 4 personnes, sans produit",
      table.state == 'draft' and table.customer_count == 4 and not table.lines,
      (table.state, table.customer_count, len(table.lines)))
check("« Ouverte par » : Awa", table.aite_ouverte_par_id == awa, table.aite_ouverte_par_id.name)
check("l'heure d'ouverture est posée par le serveur",
      bool(table.aite_heure_ouverture) and avant <= table.aite_heure_ouverture <= fields.Datetime.now(),
      table.aite_heure_ouverture)
t12['valeurs']['aite_ouverte_par_id'] = moussa.id
caisse_envoie(t12, moussa)
check("« Ouverte par » ne change plus ensuite (Moussa renvoyé par un poste)",
      table.aite_ouverte_par_id == awa, table.aite_ouverte_par_id.name)
t1 = nouvelle_addition(restaurant.floor_ids.table_ids.filtered(lambda t: t.table_number == 1), 0, awa)
table_1 = caisse_envoie(t1, awa)
check("une table arrivée à 0 personne est ramenée à 1, et c'est noté",
      table_1.customer_count == 1 and any("0 personne" in (m.body or '')
                                           for m in table_1.message_ids), table_1.customer_count)
table_1.with_user(caisse).action_pos_order_cancel()

print("\n═══ 12. Awa saisit 3 Castel et les envoie (incrément 3) ═══")
c12 = ajouter(t12, castel, 3)
caisse_envoie(t12, awa)
saisie = Saisies.search([('order_id', '=', table.id)])
check("le journal des saisies : 3 Castel, par Awa, à l'heure",
      len(saisie) == 1 and saisie.quantite == 3 and saisie.produit_nom == "Castel"
      and saisie.employe_nom == "Awa" and bool(saisie.date), saisie.read(['quantite', 'employe_nom']))
check("pas encore envoyé : rien n'est verrouillé", table.lines.aite_qte_envoyee == 0)
envoyer(t12)
caisse_envoie(t12, awa)
check("« J'envoie » : 3 Castel verrouillées", table.lines.aite_qte_envoyee == 3,
      table.lines.aite_qte_envoyee)

print("\n═══ 13. Paul complète la table 12 (incrément 3) ═══")
t12['lignes'][c12].update(qty=4, modifiee=True)
caisse_envoie(t12, paul)
saisies = Saisies.search([('order_id', '=', table.id)], order='id')
check("1 Castel ajoutée sous le code de Paul : une saisie à son nom",
      saisies.mapped('employe_nom') == ["Awa", "Paul"] and saisies.mapped('quantite') == [3, 1],
      saisies.mapped('employe_nom'))
envoyer(t12)
caisse_envoie(t12, paul)

Annulations = env['aite.restaurant.annulation'] if 'aite.restaurant.annulation' in env else None
R8 = ("Ce code ne peut pas annuler. Il faut celui d'un chef de salle, d'un "
      "superviseur ou du manager.")

print("\n═══ 13 bis. Awa retire une Castel envoyée sans code : c'est tracé (incrément 4) ═══")
# Table 9 : 3 Castel envoyées ; puis une copie de poste trafiquée renvoie 2
# (le pavé, lui, ouvrirait la fenêtre d'annulation).
t9 = nouvelle_addition(table_9, 2, awa)
c9 = ajouter(t9, castel, 3)
envoyer(t9)
table_9_cmd = caisse_envoie(t9, awa)
t9['lignes'][c9].update(qty=2, modifiee=True)
caisse_envoie(t9, awa)
retrait = Annulations.with_user(manager).search(
    [('order_id', '=', table_9_cmd.id), ('autorisee', '=', False)]) if Annulations is not None else []
check("la synchronisation passe (jamais refusée), la table garde 2 Castel",
      table_9_cmd.lines.qty == 2, table_9_cmd.lines.qty)
check("une ligne « Retrait sans code » au rapport des annulations : 1 Castel, par Awa, "
      "sans responsable",
      len(retrait) == 1 and retrait.type_annulation == 'retrait_sans_code'
      and retrait.quantite == 1 and retrait.serveur_nom == "Awa" and not retrait.superieur_nom,
      [(r.type_annulation, r.quantite, r.serveur_nom) for r in retrait])

print("\n═══ 13 ter. Paul annule une Castel avec son code et un motif (incrément 4) ═══")
motif_parti = env.ref('aite_pos_restaurant.motif_client_parti', raise_if_not_found=False)
demande = str(uuid4())
Commandes = env['pos.order'].with_user(caisse)
if Annulations is not None and motif_parti:
    reponse = Commandes.aite_autoriser_annulation(
        table_9_cmd.ids, [{'uuid': c9, 'quantite': 1}], awa.pin, motif_parti.id, False,
        awa.id, str(uuid4()), 'produit')
    check("Awa tape son propre code dans la fenêtre d'annulation : refusé (R8)",
          reponse == {'erreur': R8}, reponse)
    reponse = Commandes.aite_autoriser_annulation(
        table_9_cmd.ids, [{'uuid': c9, 'quantite': 1}], paul.pin, motif_parti.id, False,
        awa.id, demande, 'produit')
    autorisee = Annulations.with_user(manager).search(
        [('order_id', '=', table_9_cmd.id), ('autorisee', '=', True)])
    check("Paul tape son code et touche « Client parti » : accepté",
          reponse.get('superieur_nom') == "Paul", reponse)
    check("une ligne au rapport : 1 Castel, autorisée par Paul, demandée par Awa, "
          "« Client parti »",
          len(autorisee) == 1 and autorisee.quantite == 1 and autorisee.superieur_nom == "Paul"
          and autorisee.serveur_nom == "Awa" and autorisee.motif_nom == "Client parti",
          [(a.quantite, a.superieur_nom, a.serveur_nom, a.motif_nom) for a in autorisee])
    check("le montant est en FCFA : 1 000", autorisee.montant == 1000
          and autorisee.currency_id.name == 'XAF', (autorisee.montant, autorisee.currency_id.name))
    Commandes.aite_autoriser_annulation(
        table_9_cmd.ids, [{'uuid': c9, 'quantite': 1}], paul.pin, motif_parti.id, False,
        awa.id, demande, 'produit')
    check("la même demande renvoyée (réponse perdue) : toujours une seule ligne",
          Annulations.search_count([('order_id', '=', table_9_cmd.id),
                                    ('autorisee', '=', True)]) == 1)
    # La caisse applique la baisse et note ce qui reste parti (bon d'annulation).
    t9['lignes'][c9].update(qty=1, modifiee=True)
    for entree in t9['preparation']['lines'].values():
        entree['quantity'] = 1
    t9['preparation']['metadata'] = {'serverDate': fields.Datetime.to_string(fields.Datetime.now())}
    caisse_envoie(t9, awa)
    check("la baisse appliquée par la caisse ne crée rien de plus au rapport",
          Annulations.search_count([('order_id', '=', table_9_cmd.id)]) == 2
          and table_9_cmd.lines.qty == 1 and table_9_cmd.lines.aite_qte_envoyee == 1)
    aujourdhui = Annulations.with_user(manager).read_group(
        [('date', '>=', fields.Datetime.to_string(fields.Datetime.now().replace(
            hour=0, minute=0, second=0)))], ['montant:sum'], [])
    check("rapport du jour : le total suit (2 000 F : un retrait, une annulation)",
          aujourdhui and aujourdhui[0]['montant'] == 2000, aujourdhui)
else:
    check("le journal des annulations existe (incrément 4)", False)

print("\n═══ 13 quater. Les contournements fermés à la revue (incrément 4) ═══")
# Table 1 : 2 Castel envoyées. Un poste trafiqué renvoie une ligne neuve à
# -1 (sur la caisse, « +/- » sur une ligne neuve la retire, comme ⌫).
if Annulations is not None:
    table_1_ter = restaurant.floor_ids.table_ids.filtered(lambda t: t.table_number == 1)
    t1b = nouvelle_addition(table_1_ter, 2, awa)
    ajouter(t1b, castel, 2)
    envoyer(t1b)
    cmd_1 = caisse_envoie(t1b, awa)
    ajouter(t1b, castel, -1)
    caisse_envoie(t1b, awa)
    negatif = Annulations.search([('order_id', '=', cmd_1.id)])
    check("une ligne négative qui n'est pas un remboursement baisse l'addition : tracée "
          "« Retrait sans code » (1 Castel, Awa)",
          len(negatif) == 1 and negatif.type_annulation == 'retrait_sans_code'
          and negatif.quantite == 1 and negatif.serveur_nom == "Awa",
          [(a.type_annulation, a.quantite, a.serveur_nom) for a in negatif])
    # Le manager annule l'addition d'Awa depuis la gestion (« Cancel Order »).
    env.ref('point_of_sale.pos_order_set_cancel').with_user(manager).with_context(
        active_model='pos.order', active_ids=cmd_1.ids, active_id=cmd_1.id).run()
    gestion = Annulations.search([('order_id', '=', cmd_1.id),
                                  ('type_annulation', '=', 'annulation_sans_code')])
    check("annulée depuis la gestion : « Demandée par » le manager, pas Awa",
          cmd_1.state == 'cancel' and len(gestion) == 1 and gestion.quantite == 2
          and gestion.serveur_nom == "Manager du restaurant" and not gestion.serveur_id,
          [(a.quantite, a.serveur_nom, a.serveur_id.name) for a in gestion])

print("\n═══ 14. Division et réunion : pas des saisies (incrément 3) ═══")
# Division : 1 Castel dans la part « 12B » (même personne, même heure).
part = nouvelle_addition(None, 0, awa, "12B")
part['valeurs']['aite_origine_uuid'] = table.uuid
part['valeurs']['aite_heure_ouverture'] = t12['valeurs']['aite_heure_ouverture']
c_part = ajouter(part, castel, 1)
part['preparation']['lines'] = {c_part: {'uuid': c_part, 'product_id': castel.id, 'quantity': 1, 'note': ''}}
t12['lignes'][c12].update(qty=3, modifiee=True)
t12['preparation']['lines'][c12]['quantity'] = 3
caisse_envoie(t12, awa, deplacement=True)
part_12b = caisse_envoie(part, awa, deplacement=True)
check("la part « 12B » : 0 personne, l'origine et l'heure de la table 12",
      part_12b.customer_count == 0 and part_12b.aite_origine_uuid == table.uuid
      and part_12b.aite_heure_ouverture == table.aite_heure_ouverture)
check("la table 12 garde ses 4 personnes", table.customer_count == 4)
# Réunion : la table 7 (2 personnes, 2 Castel envoyées) versée dans la table 12.
t7 = nouvelle_addition(table_7, 2, awa)
ajouter(t7, castel, 2)
envoyer(t7)
table_7_cmd = caisse_envoie(t7, awa)
t12['lignes'][c12].update(qty=5, modifiee=True)
t12['preparation']['lines'][c12]['quantity'] = 5
t12['valeurs']['customer_count'] = 6
caisse_envoie(t12, awa, deplacement=True)
# La caisse signale la réunion avant d'annuler la table absorbée (incrément 4).
if hasattr(Commandes, 'aite_marquer_fusion'):
    Commandes.aite_marquer_fusion(table_7_cmd.id)
table_7_cmd.with_user(caisse).action_pos_order_cancel()
check("réunion : la table 12 a 6 personnes et 5 Castel verrouillées",
      table.customer_count == 6 and table.lines.aite_qte_envoyee == 5,
      (table.customer_count, table.lines.aite_qte_envoyee))
check("ni la division ni la réunion ne sont des saisies",
      Saisies.search_count([('order_id', 'in', (table | part_12b).ids)]) == 2)
check("ni la division ni la réunion ne sont des annulations (incrément 4)",
      Annulations is not None and not Annulations.search_count(
          [('order_id', 'in', (table | part_12b | table_7_cmd).ids)]))
check("la table 7 absorbée est marquée « Réunie à une autre table »",
      'aite_fusionnee' in table_7_cmd._fields and table_7_cmd.aite_fusionnee)

print("\n═══ 15. La caissière encaisse (incrément 3) ═══")
caisse_envoie(t12, carine, etat='paid', payer=especes)
check("la table 12 est encaissée", table.state == 'paid', table.state)
check("« Encaissée par » : Carine ; « Ouverte par » : toujours Awa (REST-02 critère 1)",
      table.aite_encaissee_par_id == carine and table.aite_ouverte_par_id == awa,
      (table.aite_encaissee_par_id.name, table.aite_ouverte_par_id.name))
caisse_envoie(part, carine, etat='paid', payer=especes)
check("la part « 12B » est encaissée par Carine",
      part_12b.state == 'paid' and part_12b.aite_encaissee_par_id == carine)
fiche = table.with_user(manager)
action = fiche.action_aite_saisies()
check("le manager ouvre les saisies depuis la fiche de l'addition (bouton « Saisies »)",
      Saisies.with_user(manager).search_count(action['domain']) == 2)
vue_fiche = etree.fromstring(env['pos.order'].with_user(manager).get_view(view_type='form')['arch'])
check("la fiche de l'addition montre « Ouverte par », « Heure d'ouverture », « Encaissée par »",
      all(vue_fiche.xpath("//field[@name='%s']" % champ) for champ in
          ('aite_ouverte_par_id', 'aite_heure_ouverture', 'aite_encaissee_par_id')))
check("le compte de la caisse ne lit pas le journal des saisies",
      refus_acces(lambda: Saisies.with_user(caisse).search([])))

print("\n═══ 15 bis. Le manager lit « Personnes et tables » (incrément 6) ═══")
# Point de Vente → Analyse → « Personnes et tables » : la vue croisée du jour.
# Déjà encaissées dans cette session : la table 12 (réunie à la table 7, 6
# personnes), sa part « 12B » et, si l'ardoise est proposée, la table de
# l'ardoise (2 personnes).
Commandes_manager = env['pos.order'].with_user(manager)
action_pt = env.ref('aite_pos_restaurant.action_personnes_tables', raise_if_not_found=False)
deja = (1, 2) if ardoise else (0, 0)


def personnes_et_tables():
    """Les totaux de la vue croisée « Personnes et tables » sur la session."""
    domaine = safe_eval(action_pt.domain or '[]') + [('session_id', '=', session.id)]
    ligne = Commandes_manager.read_group(
        domaine, ['aite_tables:sum', 'aite_personnes:sum', 'aite_sans_table:sum',
                  'aite_articles:sum', 'amount_total:sum'], [])[0]
    return (ligne['aite_tables'] or 0, ligne['aite_personnes'] or 0,
            ligne['aite_sans_table'] or 0)


if action_pt and 'aite_tables' in env['pos.order']._fields:
    menus_manager = env['ir.ui.menu'].with_user(manager)._visible_menu_ids()
    check("le menu Point de Vente → Analyse → « Personnes et tables » est au manager",
          env.ref('aite_pos_restaurant.menu_personnes_tables').id in menus_manager)
    check("l'écran vide dit quoi faire (plus de 120 caractères), « Aujourd'hui » d'office",
          'o_view_nocontent' in (action_pt.help or '') and len(action_pt.help) >= 120
          and 'search_default_aujourd_hui' in (action_pt.context or ''))
    check("la table 12 réunie compte pour 1 table et 6 personnes ; la part « 12B » ne compte pas",
          (table.aite_tables, table.aite_personnes, part_12b.aite_tables, part_12b.aite_personnes)
          == (1, 6, 0, 0),
          (table.aite_tables, table.aite_personnes, part_12b.aite_tables, part_12b.aite_personnes))
    lues_pt = env['pos.order'].with_user(manager).search(
        safe_eval(action_pt.domain or '[]') + [('session_id', '=', session.id)])
    ecartees = table_7_cmd | table_1 | table_9_cmd
    check("la table 7 absorbée par la réunion, la table 1 annulée, la table 9 encore ouverte : "
          "aucune n'est comptée",
          (table_7_cmd.state, table_1.state, table_9_cmd.state) == ('cancel', 'cancel', 'draft')
          and not (lues_pt & ecartees) and table in lues_pt,
          ((table_7_cmd.state, table_1.state, table_9_cmd.state), (lues_pt & ecartees).ids))
    check("« Personnes et tables » du jour : tables %d, personnes %d" % (deja[0] + 1,
                                                                       deja[1] + 6),
          personnes_et_tables() == (deja[0] + 1, deja[1] + 6, 0), personnes_et_tables())
    par_serveur = Commandes_manager.read_group(
        [('session_id', '=', session.id), ('state', 'in', ('paid', 'done', 'invoiced')),
         ('aite_ouverte_par_id', '!=', False)],
        ['aite_personnes:sum'], ['aite_ouverte_par_id'])
    check("regroupé par « Ouverte par » : Awa a servi la table 12 (REST-02 critère 4)",
          any(l['aite_ouverte_par_id'][1] == "Awa" and l['aite_personnes'] >= 6
              for l in par_serveur), par_serveur)
else:
    check("« Personnes et tables » existe (incrément 6)", False)


def details_des_ventes(utilisateur):
    """Les données du rapport de session (« Détails des ventes » d'Odoo et
    nos lignes), lues par ``utilisateur`` ; ``{'erreur': …}`` si Odoo refuse."""
    try:
        with env.cr.savepoint():
            return env['report.point_of_sale.report_saledetails'].with_user(
                utilisateur).get_sale_details(False, False, False, [session.id])
    except AccessError as erreur:
        return {'erreur': str(erreur), 'products': []}


details = details_des_ventes(manager)
check("le manager ouvre « Détails des ventes » de la session (droit Facturation)",
      'erreur' not in details, details.get('erreur'))
vendus = {}
for categorie in details['products']:
    for l in categorie['products']:
        vendus[l['product_id']] = vendus.get(l['product_id'], 0) + l['quantity']
payees = env['pos.order'].search([('session_id', '=', session.id),
                                  ('state', 'in', ('paid', 'done', 'invoiced'))])
castel_vendues = sum(l.qty for l in payees.lines if l.product_id == castel)
check("« Détails des ventes » donne la quantité de Castel vendue (REST-25 critère 2) : %g"
      % castel_vendues, vendus.get(castel.id) == castel_vendues and castel_vendues > 0,
      (vendus.get(castel.id), castel_vendues))

print("\n═══ 16. Un numéro qui n'est pas sur le plan (incrément 3) ═══")
t99 = nouvelle_addition(None, 2, awa, "99")
numero = caisse_envoie(t99, awa)
check("« 99 » ouvre une table à ce nom, à 2 personnes, ouverte par Awa",
      numero.floating_order_name == "99" and numero.customer_count == 2
      and numero.aite_ouverte_par_id == awa and bool(numero.aite_heure_ouverture))
ajouter(t99, castel, 1)
# Le manager a mis un jus à la carte ; Awa en sert un à la table 99.
jus = env['product.product'].with_user(manager).create({
    'name': "Jus de gingembre", 'type': 'consu', 'available_in_pos': True,
    'list_price': 500, 'taxes_id': [(5, 0, 0)]})
ajouter(t99, jus, 1)
caisse_envoie(t99, carine, etat='paid', payer=especes)
check("encaissée : ce n'est pas une vente sans table (pas de note)",
      numero.state == 'paid' and not any("vente sans table" in (m.body or '')
                                         for m in numero.message_ids))

print("\n═══ 16 bis. Les produits épuisés (incrément 5) ═══")
# Le manager met la Guinness à la carte en cochant « Suivre l'inventaire »
# (la Castel, déjà vendue, ne peut plus changer de suivi : Odoo le refuse).
Produits = env['product.product'].with_user(manager)
if hasattr(env['product.product'], 'aite_stock_disponible'):
    guinness = Produits.create({'name': "Guinness", 'type': 'consu', 'is_storable': True,
                                'available_in_pos': True, 'list_price': 1500,
                                'taxes_id': [(5, 0, 0)]})
    poste_stock = env['product.product'].with_user(caisse)

    def disponible():
        """Ce que la caisse reçoit (une requête pour toute la carte)."""
        return poste_stock.aite_stock_disponible(restaurant.id)

    check("la Guinness, suivie en stock et jamais rentrée : disponible 0 (la caisse refuse)",
          disponible().get(guinness.id) == 0, disponible().get(guinness.id))
    check("la Castel n'est pas suivie : elle n'est pas contrôlée, elle se vend toujours",
          castel.id not in disponible())
    # « Mettre la quantité à jour » sur la fiche du produit : 24 bouteilles.
    entrepot = restaurant.picking_type_id.warehouse_id
    erreur = None
    try:
        with env.cr.savepoint():
            quant = env['stock.quant'].with_user(manager).with_context(inventory_mode=True).create({
                'product_id': guinness.id, 'location_id': entrepot.lot_stock_id.id,
                'inventory_quantity': 24})
            quant.action_apply_inventory()
    except Exception as exc:  # noqa: BLE001
        erreur = exc
    check("le manager enregistre l'entrée de 24 bouteilles", erreur is None, erreur)
    check("entrée de 24 : disponible 24, sans recharger la caisse",
          disponible().get(guinness.id) == 24, disponible().get(guinness.id))
    # Awa ouvre la table 7 (libre depuis la réunion) et envoie 2 Guinness.
    t7b = nouvelle_addition(table_7, 2, awa)
    ajouter(t7b, guinness, 2)
    envoyer(t7b)
    table_7_bis = caisse_envoie(t7b, awa)
    check("2 Guinness envoyées sur une table ouverte : disponible 22 sur tous les postes (19b)",
          disponible().get(guinness.id) == 22, disponible().get(guinness.id))
    caisse_envoie(t7b, carine, etat='paid', payer=especes)
    check("la table encaissée sort du stock une seule fois : 22 en stock, disponible 22",
          table_7_bis.state == 'paid'
          and guinness.with_context(warehouse_id=entrepot.id).qty_available == 22
          and disponible().get(guinness.id) == 22,
          (table_7_bis.state, guinness.with_context(warehouse_id=entrepot.id).qty_available,
           disponible().get(guinness.id)))
else:
    check("la caisse sait ce qui reste en stock (aite_stock_disponible, incrément 5)", False)

print("\n═══ 9. Fermeture de la caisse par code (incréments 2 et 4) ═══")
R13 = "Seul un chef de salle ou le manager ferme la caisse."
# La table 9 est encore ouverte, 1 Castel envoyée : « Annuler les commandes »
# d'Odoo, sans la fenêtre d'annulation (copie de poste en retard).
erreur = None
try:
    with env.cr.savepoint():
        table_9_cmd.with_user(caisse).action_pos_order_cancel()
except Exception as exc:  # noqa: BLE001
    erreur = exc
check("une table encore ouverte annulée sans code : jamais d'erreur", erreur is None, erreur)
sans_code = Annulations.search([('order_id', '=', table_9_cmd.id),
                                ('type_annulation', '=', 'annulation_sans_code')]) \
    if Annulations is not None else []
check("la table 9 est annulée et tracée « Annulation sans code » (1 Castel, Awa)",
      table_9_cmd.state == 'cancel' and len(sans_code) == 1 and sans_code.quantite == 1
      and sans_code.serveur_nom == "Awa",
      [(a.type_annulation, a.quantite, a.serveur_nom) for a in sans_code])
message = refus_utilisateur(lambda: poste.post_closing_cash_details(0))
check("fermer sans code (fenêtre de fermeture d'Odoo seule) : refusé (R13)",
      message == R13, message)
check("la session reste ouverte", session.state == 'opened', session.state)
reponse = poste.aite_fermer_caisse('3333')
check("Carine (caissière) tape son code pour fermer : refusé (R13)",
      reponse == {'erreur': R13}, reponse)
session.employee_id = awa  # un autre poste : Awa vient de taper son code
reponse = poste.aite_fermer_caisse(paul.pin)
check("Paul (chef de salle) tape son code : accepté", reponse.get('id') == paul.id, reponse)
check("tant que la caisse n'est pas fermée, elle n'est pas « fermée par Paul »",
      not session.aite_fermee_par_id and not session.message_ids.filtered(
          lambda m: "Caisse fermée par" in (m.body or '')), session.aite_fermee_par_id.name)
try:
    with env.cr.savepoint():
        resultat = poste.post_closing_cash_details(session.cash_register_balance_end)
        poste.update_closing_control_state_session("Fin du service")
        resultat = poste.close_session_from_ui()
    erreur = None if resultat.get('successful') else resultat
except Exception as exc:  # noqa: BLE001
    erreur = exc
check("la caisse se ferme alors que le dernier code tapé ailleurs est celui d'Awa",
      erreur is None and session.state == 'closed', erreur or session.state)
check("« Caisse fermée par » : Paul", session.aite_fermee_par_id == paul,
      session.aite_fermee_par_id.name)
check("l'historique de la session dit une fois « Caisse fermée par Paul »",
      len(session.message_ids.filtered(
          lambda m: "Caisse fermée par Paul" in (m.body or ''))) == 1)

print("\n═══ 9 bis. Le rapport de fermeture : tables, personnes, annulations (incrément 6) ═══")
# Encaissées dans la session : la table 12 (6 personnes), le numéro 99
# (2 personnes), la table 7 de la Guinness (2 personnes, incrément 5) et la
# table de l'ardoise (2 personnes) si elle est proposée ; la part « 12B » ne
# compte pas.
attendu = (deja[0] + 2 + (1 if hasattr(env['product.product'], 'aite_stock_disponible') else 0),
           deja[1] + 8 + (2 if hasattr(env['product.product'], 'aite_stock_disponible') else 0),
           0)
fermeture = details_des_ventes(manager)
check("le rapport de fermeture donne %d tables et %d personnes, 0 vente sans table"
      % attendu[:2], (fermeture.get('aite_tables'), fermeture.get('aite_personnes'),
                      fermeture.get('aite_sans_table')) == attendu,
      (fermeture.get('aite_tables'), fermeture.get('aite_personnes'),
       fermeture.get('aite_sans_table'), attendu))
annulees = Annulations.search([('session_id', '=', session.id)]) if Annulations is not None else []
check("il liste les %d annulations de la session, autorisées ou non, et leur total"
      % len(annulees),
      len(fermeture.get('aite_annulations') or []) == len(annulees) == 5
      and (fermeture.get('aite_annulations_total') or {}).get('montant')
      == sum(annulees.mapped('montant')),
      (len(fermeture.get('aite_annulations') or []), len(annulees),
       fermeture.get('aite_annulations_total')))
check("une annulation autorisée y porte son motif et le nom de Paul",
      any(a['motif'] == "Client parti" and a['autorisee_par'] == "Paul"
          for a in fermeture.get('aite_annulations') or []), fermeture.get('aite_annulations'))
try:
    html, _format = env['ir.actions.report'].with_user(manager)._render_qweb_html(
        'point_of_sale.sale_details_report', session.ids)
    html = str(html)
except Exception as exc:  # noqa: BLE001
    html = repr(exc)
check("le rapport imprimé depuis la gestion montre « Nombre de tables », « Nombre de "
      "personnes » et les annulations : le chef de salle n'a rien à rédiger, il signe",
      'Nombre de tables' in html and 'Nombre de personnes' in html and 'Client parti' in html,
      html[:300])

print("\n═══ 17. Le chef de salle lit le rapport des annulations (incrément 4) ═══")
groupe = env.ref('aite_pos_restaurant.group_lecture_rapports', raise_if_not_found=False)
if groupe and Annulations is not None:
    # AITE donne au chef de salle le seul profil « Restaurant : lecture des rapports ».
    chef = Users.create({'name': "Chef de salle", 'login': 'scenario_chef_resto',
                         'groups_id': [(6, 0, [groupe.id])]})
    check("le chef de salle est un utilisateur interne, sans droit sur la caisse",
          chef._is_internal() and not chef.has_group('point_of_sale.group_pos_user'))
    lu = Annulations.with_user(chef).search([])
    check("il lit les annulations (retraits, annulation autorisée, annulations sans code)",
          sorted(lu.mapped('type_annulation')) ==
          ['annulation_sans_code', 'annulation_sans_code', 'produit', 'retrait_sans_code',
           'retrait_sans_code'], lu.mapped('type_annulation'))
    check("il ne lit pas les commandes", refus_acces(lambda: env['pos.order'].with_user(
        chef).search([])))
    check("il ne lit pas la configuration de la caisse", refus_acces(
        lambda: env['pos.config'].with_user(chef).search([])))
    menus = env['ir.ui.menu'].with_user(chef)._visible_menu_ids()
    racine = env.ref('aite_pos_restaurant.menu_restaurant_root')
    check("le menu « Restaurant » est le sien ; pas le Point de Vente",
          racine.id in menus and env.ref('point_of_sale.menu_point_root').id not in menus)
    action = env.ref('aite_pos_restaurant.action_restaurant_annulation')
    vues = Annulations.with_user(chef).get_views(
        [(False, mode) for mode in action.view_mode.split(',')] + [(False, 'search')])
    champs = vues['models']['aite.restaurant.annulation']['fields']
    lignes = Annulations.with_user(chef).web_search_read(
        [], {nom: {} for nom in champs if nom not in ('currency_id',)})
    check("« Restaurant → Annulations » s'ouvre (liste, vue croisée, graphique)",
          lignes['length'] == 5 and {'list', 'pivot', 'graph'} <= set(vues['views']))
    check("l'écran vide dit quoi faire (plus de 120 caractères)",
          'o_view_nocontent' in (action.help or '') and len(action.help) >= 120,
          len(action.help or ''))
    check("la période par défaut est « Aujourd'hui »",
          'search_default_aujourd_hui' in (action.context or ''), action.context)
else:
    check("le profil « Restaurant : lecture des rapports » existe (incrément 4)", False)

print("\n═══ 18. Le manager lit les ventes par famille (incrément 6, REST-23-P1) ═══")
Report = env['aite.pos.daily.report'] if 'aite.pos.daily.report' in env else None
if Report is not None and 'famille_n1_id' in Report._fields:
    # AITE donne au manager le profil « Manager — Analyses POS » ; le manager
    # range la carte en familles de caisse (celles de l'écran de commande).
    manager.groups_id += env.ref('aite_pos_analytics.group_aite_pos_analytics_manager')
    Familles = env['pos.category'].with_user(manager)
    boisson = Familles.create({'name': "Boisson"})
    alcool = Familles.create({'name': "Alcoolisé", 'parent_id': boisson.id})
    biere = Familles.create({'name': "Bière", 'parent_id': alcool.id})
    sans_alcool = Familles.create({'name': "Non alcoolisé", 'parent_id': boisson.id})
    famille_jus = Familles.create({'name': "Jus", 'parent_id': sans_alcool.id})
    bieres = castel | (globals().get('guinness') or env['product.product'])
    bieres.with_user(manager).write({'pos_categ_ids': [(6, 0, biere.ids)]})
    jus.with_user(manager).write({'pos_categ_ids': [(6, 0, famille_jus.ids)]})
    Analyse = Report.with_user(manager)
    dans_session = [('session_id', '=', session.id)]
    total = Analyse.read_group(dans_session, ['price_subtotal_incl:sum'], [])[0][
        'price_subtotal_incl']
    par_famille = {(l['famille_n1_id'] or (False, "sans famille"))[1]: l['price_subtotal_incl']
                   for l in Analyse.read_group(dans_session, ['price_subtotal_incl:sum'],
                                               ['famille_n1_id'])}
    encaissees = env['pos.order'].search([('session_id', '=', session.id),
                                          ('state', 'in', ('paid', 'done', 'invoiced'))])
    biere_vendue = sum(l.price_subtotal_incl for l in encaissees.lines if l.product_id in bieres)
    jus_vendu = sum(l.price_subtotal_incl for l in encaissees.lines if l.product_id == jus)
    par_sous_famille = {
        l['famille_n2_id'][0]: l['price_subtotal_incl'] for l in Analyse.read_group(
            dans_session + [('famille_n1_id', '=', boisson.id)],
            ['price_subtotal_incl:sum'], ['famille_n2_id'])}
    check("« Boisson » additionne ses deux sous-familles : %d F de bières et %d F de jus"
          % (biere_vendue, jus_vendu),
          par_famille.get("Boisson") == biere_vendue + jus_vendu and biere_vendue > 0
          and jus_vendu > 0
          and par_sous_famille == {alcool.id: biere_vendue, sans_alcool.id: jus_vendu},
          (par_famille, par_sous_famille, biere_vendue, jus_vendu))
    check("la somme des familles est le total des ventes (rien ne disparaît)",
          sum(par_famille.values()) == total, (par_famille, total))
    vue = etree.fromstring(Analyse.get_views([(False, 'search')])['views']['search']['arch'])
    champ_famille = vue.xpath("//field[@string='Famille']")

    def cherche_famille(texte=None, famille=None):
        """Le champ « Famille » de la recherche, comme le client web : un
        texte tapé puis Entrée (« ilike »), ou une famille choisie dans la
        liste (son identifiant, « = »)."""
        champ = champ_famille[0]
        libelle, valeur = (famille.display_name, famille.id) if famille else (texte, texte)
        if champ.get('filter_domain'):
            domaine = safe_eval(champ.get('filter_domain'), {'self': libelle, 'raw_value': valeur})
        else:
            domaine = [(champ.get('name'), '=' if famille else 'ilike', valeur)]
        return Analyse.search(dans_session + domaine)

    trouve = cherche_famille("Alcoolisé") if champ_famille else Analyse
    check("le manager tape « Alcoolisé » dans « Famille » : il trouve les bières, pas le jus "
          "« Non alcoolisé », sans savoir à quel niveau est la famille",
          bool(trouve) and set(trouve.mapped('product_id')) <= set(bieres)
          and sum(trouve.mapped('price_subtotal_incl')) == biere_vendue,
          (trouve.mapped('product_id.name'), sum(trouve.mapped('price_subtotal_incl'))))
    trouve = cherche_famille(famille=sans_alcool) if champ_famille else Analyse
    check("il choisit « Boisson / Non alcoolisé » dans la liste : le jus seul",
          trouve.mapped('product_id') == jus, trouve.mapped('product_id.name'))
else:
    check("l'analyse AITE connaît les familles (aite_pos_analytics 18.0.2.1.5)", False)

if Report is not None and 'serveur_id' in Report._fields:
    print("\n═══ 19. Le serveur et la caissière dans les analyses (incrément 6, AH-03) ═══")
    Analyse = Report.with_user(manager)
    lignes_12 = Analyse.search([('order_id', '=', table.id)])
    check("la table 12 : « Serveur (ouverte par) » Awa, « Encaissée par » Carine, sous le "
          "compte de la caisse",
          set(lignes_12.mapped('serveur_id.name')) == {"Awa"}
          and set(lignes_12.mapped('encaisse_par_id.name')) == {"Carine"}
          and set(lignes_12.mapped('user_id')) == {caisse},
          (lignes_12.mapped('serveur_id.name'), lignes_12.mapped('encaisse_par_id.name')))
    check("le compte Odoo s'affiche « Compte Odoo »",
          Report.fields_get(['user_id'])['user_id']['string'] == "Compte Odoo")
else:
    print("\n(aite_pos_analytics_hr absent : le serveur dans les analyses n'est pas vérifié)")

env.cr.rollback()
print("\n══════════════════════════════════════")
print("RÉSULTAT : %d vérifications OK, %d KO" % (ok_count, len(ko)))
for k in ko:
    print("  KO : " + k)
sys.exit(1 if ko else 0)
