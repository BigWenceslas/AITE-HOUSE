# Jeu de données registre : pièce d'identité sur le contact, séjour en cours, fiche d'un second occupant (commit volontaire)
from datetime import timedelta, date
cm = env.ref('base.cm'); fr = env.ref('base.fr')
hotel = env['aite.hotel.hotel'].search([('code', '=', 'LVR')], limit=1)
rtype = env['aite.hotel.room.type'].search([('code', '=', 'STD')], limit=1)
room = env['aite.hotel.room'].search([('name', '=', '202'), ('hotel_id', '=', hotel.id)], limit=1)
guest = env['res.partner'].search([('name', '=', "Ngo Bikaï Solange")], limit=1)
guest.write({'country_id': cm.id, 'nationality_id': cm.id, 'guest_id_type': 'cni', 'guest_id_number': '113366998', 'street': 'Bonapriso', 'city': 'Douala'})
Res = env['aite.hotel.reservation']
old = Res.search([('partner_id', '=', guest.id), ('state', 'in', ('confirmed', 'checked_in'))])
for r in old:
    if r.state == 'confirmed': r.action_cancel()
cin = Res._default_checkin()
res = Res.create({'hotel_id': hotel.id, 'partner_id': guest.id, 'checkin_date': cin, 'checkout_date': cin + timedelta(days=3),
                  'line_ids': [(0, 0, {'room_type_id': rtype.id, 'room_id': room.id, 'adults': 2})]})
res.action_confirm(); res.action_checkin()
env['aite.guest.registration'].create({'reservation_id': res.id, 'reservation_line_id': res.line_ids[0].id,
    'last_name': "Durand", 'first_name': "Paul", 'nationality_id': fr.id, 'country_id': fr.id,
    'id_type': 'passport', 'id_number': '19AB12345', 'coming_from': "Paris", 'going_to': "Kribi"})
env.cr.commit()
print("RES_ID", res.id, "REG_MAIN", res.registration_ids.filtered('is_main_guest').id)
