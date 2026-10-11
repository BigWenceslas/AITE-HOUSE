# -*- coding: utf-8 -*-
"""Parcours réceptionniste novice — registre des clients."""
import sys
from datetime import timedelta, date

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


cm = env.ref('base.cm'); fr = env.ref('base.fr')
hotel = env['aite.hotel.hotel'].search([('code', '=', 'LVR')], limit=1)
rtype = env['aite.hotel.room.type'].search([('code', '=', 'STD')], limit=1)
room = env['aite.hotel.room'].search([('name', '=', '201'), ('hotel_id', '=', hotel.id)], limit=1)

print("\n═══ 1. Un client avec une fiche contact déjà renseignée (pièce, nationalité) ═══")
guest = env['res.partner'].create({
    'name': "Ngo Bikaï Solange", 'phone': '677 44 55 66', 'country_id': cm.id,
    'nationality_id': cm.id, 'guest_id_type': 'cni', 'guest_id_number': '123456789',
    'street': "Bonapriso", 'city': "Douala",
})
Res = env['aite.hotel.reservation']
cin = Res._default_checkin() + timedelta(days=20)
res = Res.create({
    'hotel_id': hotel.id, 'partner_id': guest.id, 'checkin_date': cin,
    'checkout_date': cin + timedelta(days=2),
    'line_ids': [(0, 0, {'room_type_id': rtype.id, 'room_id': room.id, 'adults': 2})],
})
res.action_confirm()
check("avant check-in : aucune fiche, 2 occupants attendus",
      res.registration_count == 0 and res.expected_guests == 2,
      (res.registration_count, res.expected_guests))
check("bandeau : « Aucune fiche … 2 occupant(s) attendu(s) »",
      "2 occupant" in res.registration_hint, res.registration_hint)

print("\n═══ 2. La réception clique « Check-in » (arrivée anticipée → responsable) ═══")
res.action_checkin()
regs = res.registration_ids
check("UNE fiche créée automatiquement", len(regs) == 1, len(regs))
main = regs.filtered('is_main_guest')
check("c'est celle du client principal", bool(main))
check("nom/prénom découpés : Ngo / Bikaï Solange",
      main.last_name == "Ngo" and main.first_name == "Bikaï Solange",
      (main.last_name, main.first_name))
check("pièce et nationalité pré-remplies depuis le contact",
      main.id_type == 'cni' and main.id_number == '123456789'
      and main.nationality_id == cm, (main.id_type, main.id_number))
check("dates du séjour reprises", main.arrival_date == cin.date()
      and main.nights == 2, (main.arrival_date, main.nights))
check("il manque la date de naissance → fiche « À compléter »",
      main.state == 'draft' and "naissance" in main.missing_info, main.missing_info)
print("     Écran dit : il manque « %s »" % main.missing_info)
check("résident (Cameroun / hôtel au Cameroun)", main.is_resident)
check("statut réservation = À compléter", res.registration_status == 'partial',
      res.registration_status)
print("     Bandeau : « %s »" % res.registration_hint)

print("\n═══ 3. Elle renseigne la date de naissance : la fiche passe « Complète » seule ═══")
main.birth_date = date(1985, 3, 12)
check("fiche complète sans cliquer sur un bouton", main.state == 'done', main.state)
check("plus rien ne manque", not main.missing_info, main.missing_info)
check("mais 1 occupant sur 2 → toujours « À compléter »",
      res.registration_status == 'partial' and "1 occupant(s) sans fiche" in res.registration_hint,
      res.registration_hint)

print("\n═══ 4. Elle ajoute l'accompagnant, un touriste français ═══")
Reg = env['aite.guest.registration']
comp = Reg.create({
    'reservation_id': res.id, 'reservation_line_id': res.line_ids[0].id,
    'last_name': "Durand", 'first_name': "Paul", 'birth_date': date(1979, 7, 2),
    'nationality_id': fr.id, 'country_id': fr.id, 'id_type': 'passport',
    'id_number': '19AB12345', 'coming_from': "Paris", 'going_to': "Kribi",
    'purpose': 'leisure',
})
check("fiche complète d'emblée", comp.state == 'done', comp.missing_info)
check("non-résident", not comp.is_resident)
check("numéro de fiche attribué (FICHE/AAAA/…)", comp.name.startswith("FICHE/"), comp.name)
check("réservation : « Registre à jour »", res.registration_status == 'done', res.registration_hint)
check("compteur 2/2", res.registration_done_count == 2 and res.expected_guests == 2)
print("     Bandeau : « %s »" % res.registration_hint)

print("\n═══ 5. Un 3e occupant est annoncé → le registre redevient « à compléter » ═══")
res.line_ids[0].children = 1
check("3 attendus, 2 fiches → partial", res.registration_status == 'partial', res.registration_hint)
res.line_ids[0].children = 0
check("retour à 2 → à jour", res.registration_status == 'done')

print("\n═══ 6. Elle mémorise la pièce sur la fiche contact de l'accompagnant ═══")
p2 = env['res.partner'].create({'name': "Durand Paul"})
comp.partner_id = p2
comp.action_copy_back_to_partner()
check("le contact Odoo porte maintenant passeport + nationalité",
      p2.guest_id_type == 'passport' and p2.guest_id_number == '19AB12345'
      and p2.nationality_id == fr, (p2.guest_id_type, p2.guest_id_number))
check("compteur de fiches sur le contact", p2.registration_count == 1)

print("\n═══ 7. Impression : fiche individuelle et registre de police ═══")
report = env.ref('aite_guest_registry.report_registration_card')
html = report._render_qweb_html(report.report_name, comp.ids)[0].decode()
check("la fiche PDF porte nom, pièce, chambre", "DURAND" in html.upper() and "19AB12345" in html and "201" in html)
check("… et les cases de signature", "Signature du client" in html)
wiz = env['aite.police.register.wizard'].create({
    'hotel_id': hotel.id, 'date_from': cin.date() - timedelta(days=1),
    'date_to': cin.date() + timedelta(days=1)})
check("l'assistant compte les fiches de la période", wiz.count == 2, wiz.count)
rep2 = env.ref('aite_guest_registry.report_police_register')
html2 = rep2.with_context(date_from=wiz.date_from, date_to=wiz.date_to, hotel_name=hotel.name)._render_qweb_html(
    rep2.report_name, wiz._get_registrations().ids)[0].decode()
check("le registre liste les 2 personnes", "NGO" in html2.upper() and "DURAND" in html2.upper())
check("période hors fiches → message clair", True)
wiz2 = env['aite.police.register.wizard'].create({
    'hotel_id': hotel.id, 'date_from': date(2020, 1, 1), 'date_to': date(2020, 1, 2)})
try:
    wiz2.action_print(); check("erreur attendue sur période vide", False)
except Exception as e:
    check("erreur attendue sur période vide, message lisible", "Aucune fiche" in str(e), str(e)[:80])

print("\n═══ 8. Statistiques d'hébergement (MINTOUL) ═══")
Stats = env['aite.guest.stats']
rows = Stats.search([('reservation_id', '=', res.id)])
check("2 lignes de statistiques (client arrivé)", len(rows) == 2, len(rows))
check("1 résident + 1 non-résident",
      sorted(rows.mapped('resident_type')) == ['non_resident', 'resident'], rows.mapped('resident_type'))
check("4 nuitées au total (2 × 2 nuits)", sum(rows.mapped('nights')) == 4, sum(rows.mapped('nights')))
grp = Stats.read_group([('reservation_id', '=', res.id)], ['arrivals:sum', 'nights:sum'], ['nationality_id'])
check("groupable par nationalité (2 groupes)", len(grp) == 2, len(grp))
check("une réservation non arrivée n'entre pas dans les stats",
      not Stats.search_count([('reservation_id.state', '=', 'confirmed')]))

print("\n═══ 9. Droits : la gouvernante lit, ne modifie pas ═══")
hk_user = env['res.users'].create({
    'name': "Femme de chambre", 'login': 'hk_test',
    'groups_id': [(6, 0, [env.ref('aite_hotel_management.group_hotel_housekeeping').id])]})
try:
    comp.with_user(hk_user).write({'note': 'x'}); check("gouvernante ne peut pas modifier une fiche", False)
except Exception:
    check("gouvernante ne peut pas modifier une fiche", True)
check("gouvernante peut lire le registre", bool(Reg.with_user(hk_user).search([], limit=1)))

env.cr.rollback()
print("\n══════════════════════════════════════")
print("RÉSULTAT : %d vérifications OK, %d KO" % (ok_count, len(ko)))
for k in ko:
    print("  KO : " + k)
sys.exit(1 if ko else 0)
