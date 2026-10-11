# -*- coding: utf-8 -*-
"""Parcours gouvernante & équipière novices — tableau, journée, inspection, panne."""
import sys
from datetime import timedelta

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


hotel = env['aite.hotel.hotel'].search([('code', '=', 'LVR')], limit=1)
rtype = env['aite.hotel.room.type'].search([('code', '=', 'STD')], limit=1)
Room = env['aite.hotel.room']; Task = env['aite.hotel.housekeeping']
rooms = {n: Room.search([('name', '=', n), ('hotel_id', '=', hotel.id)], limit=1)
         for n in ("101", "102", "201", "202", "501")}
# deux équipières + une gouvernante
G = env.ref('aite_hotel_management.group_hotel_housekeeping')
U = env.ref('aite_hotel_management.group_hotel_user')
# créés comme depuis l'écran Utilisateurs : utilisateur interne + profil hôtel
def user(name, login, group):
    u = env['res.users'].search([('login', '=', login)], limit=1)
    return u or env['res.users'].create({'name': name, 'login': login, 'groups_id': [(4, group.id)]})
amina = user("Amina", 'amina', G); rose = user("Rose", 'rose', G); gouv = user("Gouvernante", 'gouv', U)

print("\n═══ 1. Le tableau des chambres se lit sans explication ═══")
for r in rooms.values():
    r.hk_state = 'clean'; r.out_of_order = False
# annuler les réservations confirmées non arrivées pour avoir une chambre libre
env['aite.hotel.reservation'].search([('hotel_id', '=', hotel.id), ('state', '=', 'confirmed')]).action_cancel()
rooms["101"].hk_state = 'to_clean'; rooms["102"].hk_state = 'to_clean'; rooms["201"].hk_state = 'inspect'
hints = {n: r.hk_hint for n, r in rooms.items()}
check("101 : « À nettoyer » ou « Recouche à faire »", hints["101"] in ("À nettoyer", "Recouche à faire"), hints["101"])
check("201 : « À inspecter par la gouvernante »", hints["201"] == "À inspecter par la gouvernante", hints["201"])
check("libellé « Propre — libre » (fonction pure)", Room._hint_for('clean', 'free', False, False) == "Propre — libre")
check("libellé « Propre — prête pour l'arrivée »", Room._hint_for('clean', 'arrival', False, False) == "Propre — prête pour l'arrivée")
occ_rooms = [n for n, r in rooms.items() if r.occupancy_state == 'occupied' and r.hk_state == 'clean']
check("une chambre propre occupée dit « Propre — client présent »", all(rooms[n].hk_hint == "Propre — client présent" for n in occ_rooms), occ_rooms)
for n, r in rooms.items():
    print("     Chambre %s → %s" % (n, r.hk_hint))
# Les colonnes du tableau doivent suivre l'ordre du travail (Odoo 18 trie une
# sélection par ordre alphabétique de la clé : le kanban impose « hk_state desc »).
arch = Room.get_views([(env.ref('aite_housekeeping.view_room_board_kanban').id, 'kanban')])['views']['kanban']['arch']
ORDER = ['to_clean', 'cleaning', 'inspect', 'clean']
cols = [g['hk_state'] for g in Room.read_group([('hotel_id', '=', hotel.id)], ['id:count'], ['hk_state'], orderby='hk_state desc')]
check("colonnes du tableau : À nettoyer → En cours → À inspecter → Propre", 'default_order="hk_state desc' in arch and cols == sorted(cols, key=ORDER.index), cols)

print("\n═══ 2. La gouvernante répartit les chambres du jour entre Amina et Rose ═══")
Task.search([('date', '=', env['aite.hotel.housekeeping']._fields['date'].default(Task))]).unlink()
# les chambres « à nettoyer » ont une tâche du jour (créée par action_set_to_clean normalement) :
for n in ("101", "102"):
    if not rooms[n].today_task_id:
        Task.create({'room_id': rooms[n].id, 'task_type': 'checkout_clean'})
rooms["202"].with_user(gouv).action_set_to_clean()
check("mettre « À nettoyer » crée la tâche du jour", bool(rooms["202"].today_task_id))
wiz = env['aite.hk.assign.wizard'].with_user(gouv).create({'hotel_id': hotel.id, 'user_ids': [(6, 0, [amina.id, rose.id])]})
check("l'assistant compte 3 chambres à répartir", wiz.task_count == 3, wiz.task_count)
wiz.action_assign()
assigned = sorted(t.assigned_to.name for t in Task.search([('room_id', 'in', [r.id for r in rooms.values()]), ('state', '=', 'todo')]))
check("réparties à tour de rôle (2 pour l'une, 1 pour l'autre)", assigned.count("Amina") + assigned.count("Rose") == 3 and abs(assigned.count("Amina") - assigned.count("Rose")) == 1, assigned)
try:
    env['aite.hk.assign.wizard'].with_user(gouv).create({'hotel_id': hotel.id}).action_assign(); check("sans équipière : message clair", False)
except Exception as e:
    check("sans équipière : message clair", "équipière" in str(e), str(e)[:60])

print("\n═══ 3. Amina, sur son téléphone : « Ma journée » ═══")
mine = Task.with_user(amina).search([('assigned_to', '=', amina.id), ('state', 'in', ('todo', 'in_progress'))])
check("elle voit ses chambres (et seulement les siennes)", len(mine) >= 1 and all(t.assigned_to == amina for t in mine), len(mine))
t = mine[0]
check("l'étiquette dit quoi faire", "Recouche" in t.task_label or "Ménage" in t.task_label, t.task_label)
t.with_user(amina).action_start()
check("« Je commence » → chambre en nettoyage", t.room_id.hk_state == 'cleaning' and t.started_at, t.room_id.hk_state)
check("… et sur le tableau : « Nettoyage en cours »", t.room_id.hk_hint == "Nettoyage en cours")
t.with_user(amina).action_done()
check("« C'est fait » → chambre propre (inspection non exigée)", t.room_id.hk_state == 'clean' and t.state == 'done' and t.done_at, t.room_id.hk_state)
check("durée mesurée (≥ 0 min)", t.duration_min >= 0)

print("\n═══ 4. La société exige une inspection après recouche ═══")
env.company.hotel_inspection_required = True
t2 = mine[1] if len(mine) > 1 else Task.search([('assigned_to', '=', rose.id), ('state', '=', 'todo')], limit=1)
t2.action_start(); t2.action_done()
check("après recouche → « À inspecter »", t2.room_id.hk_state == 'inspect', t2.room_id.hk_state)
insp = Task.with_user(gouv).create({'room_id': t2.room_id.id, 'task_type': 'inspection'})
check("la checklist est pré-remplie (8 points standard)", len(insp.check_ids) == 8, len(insp.check_ids))
check("résumé « 0 / 8 »", insp.checks_summary == "0 / 8", insp.checks_summary)
insp.action_start()
insp.action_check_all()
insp.check_ids[1].write({'ok': False, 'remark': "serviettes manquantes"})
check("résumé « 7 / 8 »", insp.checks_summary == "7 / 8", insp.checks_summary)
insp.with_user(gouv).action_done()
check("un point non conforme → chambre renvoyée « À nettoyer »", t2.room_id.hk_state == 'to_clean', t2.room_id.hk_state)
redo = Task.search([('room_id', '=', t2.room_id.id), ('state', '=', 'todo'), ('priority', '=', '1')], limit=1)
check("… avec une tâche URGENTE qui reprend la remarque", redo and "serviettes manquantes" in (redo.note or ""), redo.note)
check("… affectée à la même équipière", redo.assigned_to == t2.assigned_to, (redo.assigned_to.name, t2.assigned_to.name))
redo.action_start(); redo.action_done()
insp2 = Task.create({'room_id': t2.room_id.id, 'task_type': 'inspection'}); insp2.action_start(); insp2.action_check_all(); insp2.action_done()
check("inspection conforme → chambre propre", t2.room_id.hk_state == 'clean', t2.room_id.hk_state)
env.company.hotel_inspection_required = False

print("\n═══ 5. Rose signale une panne de climatiseur en 501 (chambre invendable) ═══")
r501 = Room.search([('hotel_id', '=', hotel.id)]).filtered(lambda r: r.occupancy_state == 'free' and not r.out_of_order)[:1]
check("une chambre libre existe pour le test de panne", bool(r501))
w = env['aite.hk.report.issue.wizard'].with_user(rose).create({'room_id': r501.id, 'name': "Climatiseur en panne", 'blocks_room': True, 'priority': '2'})
w.action_submit()
req = env['maintenance.request'].search([('room_id', '=', r501.id)], limit=1)
check("une demande de maintenance est créée", bool(req))
check("titrée « Chambre N — Climatiseur en panne »", req.name == "Chambre %s — Climatiseur en panne" % r501.name, req.name)
check("la chambre est passée hors service", r501.out_of_order and r501.out_of_order_reason == req.name, (r501.out_of_order, r501.out_of_order_reason))
check("… et n'est plus disponible à la vente", not r501.is_available(env['aite.hotel.reservation']._default_checkin(), env['aite.hotel.reservation']._default_checkout()))
check("tableau : « Hors service — ne pas vendre »", r501.hk_hint == "Hors service — ne pas vendre", r501.hk_hint)
check("compteur de pannes = 1 sur la chambre", r501.maintenance_open_count == 1)

print("\n═══ 6. Le technicien passe la demande en « Réparé » ═══")
done_stage = env['maintenance.stage'].search([('done', '=', True)], limit=1)
req.stage_id = done_stage
check("la chambre revient en vente toute seule", not r501.out_of_order, r501.out_of_order)
check("… en « À nettoyer » avec une tâche de remise en service", r501.hk_state == 'to_clean' and Task.search_count([('room_id', '=', r501.id), ('state', '=', 'todo'), ('note', 'ilike', 'Remise en service')]) == 1)
check("plus de panne ouverte", r501.maintenance_open_count == 0)

print("\n═══ 7. Une panne sur une chambre OCCUPÉE ne la bloque pas ═══")
occ = Room.search([('hotel_id', '=', hotel.id)]).filtered(lambda r: r.occupancy_state == 'occupied')[:1]
if occ:
    w2 = env['aite.hk.report.issue.wizard'].create({'room_id': occ.id, 'name': "Ampoule grillée", 'blocks_room': True})
    w2.action_submit()
    check("chambre occupée : reste en service (la demande est juste ouverte)", not occ.out_of_order)
else:
    check("(pas de chambre occupée dans le jeu de test — étape sautée)", True)

print("\n═══ 8. Objets trouvés : Amina trouve un téléphone en 202 ═══")
lf = env['aite.hk.lost.found'].with_user(amina).new({'name': "Téléphone Samsung noir", 'room_id': rooms["202"].id})
lf._onchange_room_guess_stay()
guess = lf.reservation_id
lf = env['aite.hk.lost.found'].with_user(amina).create({'name': "Téléphone Samsung noir", 'room_id': rooms["202"].id, 'place': "sous le lit", 'storage': "casier 2", 'reservation_id': guess.id if guess else False})
check("objet enregistré, statut « Conservé »", lf.state == 'stored')
check("le séjour est deviné depuis la chambre et la date", bool(guess) == bool(rooms["202"].current_line_id), guess)
lf.action_return()
check("« Rendu au client » date et nomme le client", lf.state == 'returned' and lf.returned_date and (lf.returned_to or not guess))

print("\n═══ 9. Droits : l'équipière ne configure pas la checklist, la gouvernante ne supprime pas une panne ═══")
try:
    env['aite.hk.checklist.item'].with_user(amina).create({'name': 'x'}); check("équipière ne crée pas de point de contrôle", False)
except Exception:
    check("équipière ne crée pas de point de contrôle", True)
try:
    req.with_user(amina).unlink(); check("équipière ne supprime pas une demande", False)
except Exception:
    check("équipière ne supprime pas une demande", True)

env.cr.rollback()
print("\n══════════════════════════════════════")
print("RÉSULTAT : %d vérifications OK, %d KO" % (ok_count, len(ko)))
for k in ko:
    print("  KO : " + k)
sys.exit(1 if ko else 0)
