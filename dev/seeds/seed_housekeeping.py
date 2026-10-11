# Jeu de données gouvernante : équipières, tâches du jour, panne, objet trouvé (commit volontaire)
hotel = env['aite.hotel.hotel'].search([('code', '=', 'LVR')], limit=1)
Room = env['aite.hotel.room']; rooms = {r.name: r for r in Room.search([('hotel_id', '=', hotel.id)])}
G = env.ref('aite_hotel_management.group_hotel_housekeeping')
amina = env['res.users'].search([('login', '=', 'amina')]) or env['res.users'].create({'name': "Amina", 'login': 'amina', 'groups_id': [(4, G.id)]})
rose = env['res.users'].search([('login', '=', 'rose')]) or env['res.users'].create({'name': "Rose", 'login': 'rose', 'groups_id': [(4, G.id)]})
U = env.ref('aite_hotel_management.group_hotel_user')
gouv = env['res.users'].search([('login', '=', 'gouv')]) or env['res.users'].create({'name': "Gouvernante", 'login': 'gouv', 'groups_id': [(4, U.id), (4, G.id)]})
for u in (amina, rose, gouv):   # mot de passe = identifiant (base de développement uniquement)
    u.write({'password': u.login, 'lang': 'fr_FR'})
rooms["101"].hk_state = 'to_clean'; rooms["102"].hk_state = 'to_clean'; rooms["201"].hk_state = 'inspect'
Task = env['aite.hotel.housekeeping']
for n, u in (("101", amina), ("102", rose)):
    t = rooms[n].today_task_id or Task.create({'room_id': rooms[n].id, 'task_type': 'checkout_clean'})
    t.assigned_to = u
Task.create({'room_id': rooms["201"].id, 'task_type': 'inspection', 'assigned_to': amina.id})
w = env['aite.hk.report.issue.wizard'].create({'room_id': rooms["202"].id, 'name': "Climatiseur en panne", 'blocks_room': False, 'priority': '2'}); w.action_submit()
env['aite.hk.lost.found'].create({'name': "Téléphone Samsung noir", 'room_id': rooms["202"].id, 'place': "sous le lit", 'storage': "casier 2"})
env.cr.commit(); print("seed3 OK")
