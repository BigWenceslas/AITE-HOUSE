# Jeu de données LAVERANDAH : société en FCFA, hôtel LVR 3★, types, chambres, clients, réservations (commit volontaire)
# Données réalistes persistées pour les captures (commit volontaire)
from datetime import timedelta
cm = env.ref('base.cm'); XAF = env.ref('base.XAF')
XAF.active = True  # inactive sur une base créée hors zone FCFA : les factures seraient refusées
env.cr.execute("UPDATE res_company SET currency_id=%s WHERE id=%s", (XAF.id, env.company.id))
env.company.invalidate_recordset()
env.company.name = "LAVERANDAH SARL"; env.company.country_id = cm
H = env['aite.hotel.hotel']
hotel = H.search([('code', '=', 'LVR')], limit=1) or H.create({
    'name': "LAVERANDAH Hôtel", 'code': 'LVR', 'stars': '3', 'country_id': cm.id,
    'city': 'Douala', 'street': 'Makepe', 'phone': '673 37 33 67'})
RT = env['aite.hotel.room.type']
std = RT.search([('code', '=', 'STD')], limit=1) or RT.create({'name': "Chambre classique", 'code': 'STD', 'base_price': 25000, 'capacity_adults': 2, 'capacity_children': 1})
ste = RT.search([('code', '=', 'STE')], limit=1) or RT.create({'name': "Suite", 'code': 'STE', 'base_price': 60000, 'capacity_adults': 3, 'capacity_children': 2})
R = env['aite.hotel.room']
rooms = {}
for n, t in [("101", std), ("102", std), ("201", std), ("202", std), ("501", ste)]:
    rooms[n] = R.search([('name', '=', n), ('hotel_id', '=', hotel.id)], limit=1) or R.create({'name': n, 'hotel_id': hotel.id, 'room_type_id': t.id})
P = env['res.partner']
def partner(name, phone):
    return P.search([('name', '=', name)], limit=1) or P.create({'name': name, 'phone': phone, 'country_id': cm.id})
g1 = partner("Mballa Jean", "690 11 22 33"); g2 = partner("Ngo Bikaï Solange", "677 44 55 66"); g3 = partner("Fotso Paul", "699 77 88 99")
Res = env['aite.hotel.reservation']
if not Res.search_count([('hotel_id', '=', hotel.id)]):
    cin = Res._default_checkin()
    r1 = Res.create({'hotel_id': hotel.id, 'partner_id': g1.id, 'checkin_date': cin, 'checkout_date': cin + timedelta(days=2),
                     'line_ids': [(0, 0, {'room_type_id': std.id, 'room_id': rooms["101"].id, 'adults': 2})]})
    r1.action_confirm(); r1.action_checkin()
    r2 = Res.create({'hotel_id': hotel.id, 'partner_id': g2.id, 'checkin_date': cin + timedelta(days=1), 'checkout_date': cin + timedelta(days=3),
                     'line_ids': [(0, 0, {'room_type_id': std.id, 'room_id': rooms["102"].id, 'adults': 1})]})
    r2.action_confirm()
    r3 = Res.create({'hotel_id': hotel.id, 'partner_id': g3.id, 'checkin_date': cin - timedelta(days=5), 'checkout_date': cin - timedelta(days=2),
                     'line_ids': [(0, 0, {'room_type_id': ste.id, 'room_id': rooms["501"].id, 'adults': 2, 'children': 1})]})
    r3.action_confirm()
    # séjour passé : check-in forcé par un responsable puis facturé
    r3.with_context(force=True).write({'state': 'checked_in', 'actual_checkin': r3.checkin_date})
    r3.folio_id.action_create_invoice()
env.cr.commit()
print("seed OK — hôtel", hotel.name, "| réservations", Res.search_count([]), "| folios", env['aite.hotel.folio'].search_count([]))
