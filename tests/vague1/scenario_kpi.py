# -*- coding: utf-8 -*-
"""
Parcours « gérant novice » — indicateurs RevPAR / pickup / pace (F06).
Exécuté dans le shell Odoo : python3 odoo-bin shell -c conf -d db < ce_fichier

Le gérant ouvre le tableau de bord exécutif puis le cockpit Direction. Il
ne connaît pas le vocabulaire hôtelier : chaque indicateur doit porter une
phrase qui l'explique, et les chiffres doivent être les mêmes partout.
"""
import sys
from datetime import timedelta

from dateutil.relativedelta import relativedelta

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


today = env['aite.hotel.dashboard']._today()
env.user.tz = 'UTC'

print("\n═══ 1. Le gérant crée un petit hôtel : 2 chambres à 20 000 F ═══")
hotel = env['aite.hotel.hotel'].create({
    'name': "Hôtel KPI", 'code': 'KPI', 'stars': '2',
    'country_id': env.ref('base.cm').id, 'city': 'Douala',
})
rtype = env['aite.hotel.room.type'].create({
    'name': "Standard KPI", 'code': 'SKP', 'base_price': 20000,
    'capacity_adults': 2, 'capacity_children': 1,
})
rtype.product_id.sudo().write({'taxes_id': [(5, 0, 0)]})
rooms = [env['aite.hotel.room'].create({
    'name': "K%d" % i, 'hotel_id': hotel.id, 'room_type_id': rtype.id})
    for i in (1, 2)]
guest = env['res.partner'].create({'name': "Client KPI"})
Res = env['aite.hotel.reservation']
Dash = env['aite.hotel.dashboard']


def stay(room, first_night, nights, created=None):
    """Réservation confirmée ; ``created`` antidate la prise (pace/pickup)."""
    res = Res.create({
        'hotel_id': hotel.id, 'partner_id': guest.id,
        'checkin_date': Res._compose_datetime(first_night, 14.0),
        'checkout_date': Res._compose_datetime(
            first_night + timedelta(days=nights), 12.0),
        'line_ids': [(0, 0, {'room_type_id': rtype.id, 'room_id': room.id,
                             'adults': 1})],
    })
    res.action_confirm()
    if created:
        env.cr.execute(
            "UPDATE aite_hotel_reservation_line SET create_date=%s "
            "WHERE reservation_id=%s", (created, res.id))
        res.line_ids.invalidate_recordset(['create_date'])
    return res


print("\n═══ 2. Deux semaines d'activité : 10 nuitées vendues sur 28 possibles ═══")
d0 = today - timedelta(days=13)          # période de 14 jours : d0 → today
stay(rooms[0], d0, 6)                    # 6 nuits chambre K1
stay(rooms[1], d0 + timedelta(days=2), 4)  # 4 nuits chambre K2
env.flush_all()
k = Dash.get_kpis(str(d0), str(today), hotel.id)
p = k['period']
check("nuitées vendues = 10", p['nights_sold'] == 10, p['nights_sold'])
check("taux d'occupation = 10/28 ≈ 35,7 %", round(p['occupancy'], 1) == 35.7,
      p['occupancy'])
check("ADR = 20 000 F (CA / nuitées vendues)", round(p['adr']) == 20000, p['adr'])
check("RevPAR = 200 000 / 28 ≈ 7 143 F (CA / nuitées disponibles)",
      round(p['revpar']) == 7143, p['revpar'])
check("RevPAR = ADR × TO", abs(p['revpar'] - p['adr'] * p['occupancy'] / 100) < 1)

print("\n═══ 3. L'an dernier à la même période, l'hôtel avait vendu 4 nuitées ═══")
ly0 = d0 - relativedelta(years=1)
stay(rooms[0], ly0 + timedelta(days=1), 4, created=ly0 - timedelta(days=10))
env.flush_all()
k = Dash.get_kpis(str(d0), str(today), hotel.id)
ly = k['last_year']
check("le tableau connaît la même période N-1", ly['nights_sold'] == 4,
      ly['nights_sold'])
check("écart N-1 d'occupation = +150 % (10 vs 4 nuitées)",
      round(k['deltas_ly']['occupancy']) == 150, k['deltas_ly']['occupancy'])
check("écart N-1 d'ADR = 0 % (même prix)", round(k['deltas_ly']['adr']) == 0,
      k['deltas_ly']['adr'])

print("\n═══ 4. Pickup : ce qui a été pris ces 7 derniers jours pour les 30 prochains ═══")
stay(rooms[1], today + timedelta(days=5), 3)                     # prise aujourd'hui
stay(rooms[0], today + timedelta(days=10), 2,
     created=today - timedelta(days=20))                        # prise il y a 20 j
stay(rooms[1], today + timedelta(days=40), 2)                    # hors horizon
env.flush_all()
k = Dash.get_kpis(str(d0), str(today), hotel.id)
pk = k['pickup']
check("pickup = 3 nuitées (prise d'aujourd'hui, dans les 30 j)",
      pk['nights'] == 3, pk)
check("la fenêtre est dite en clair : 7 jours → 30 jours",
      pk['window_days'] == 7 and pk['horizon_days'] == 30, pk)

print("\n═══ 5. Pace : le mois en cours face au même mois l'an dernier ═══")
pc = k['pace']
m_first = today.replace(day=1)
in_month = sum(1 for r in Res.search([('hotel_id', '=', hotel.id)])
               for d in range(r.nights)
               if m_first <= r.checkin_date.date() + timedelta(days=d)
               < m_first + relativedelta(months=1))
check("pace du mois = nuitées déjà réservées pour le mois (%d)" % in_month,
      pc['nights'] == in_month, pc)
stay(rooms[0], (m_first - relativedelta(years=1)) + timedelta(days=3), 5,
     created=today - relativedelta(years=1) - timedelta(days=30))   # prise avant « même date N-1 »
stay(rooms[1], (m_first - relativedelta(years=1)) + timedelta(days=10), 2,
     created=today - relativedelta(years=1) + timedelta(days=2))    # prise APRÈS : ne compte pas
env.flush_all()
k = Dash.get_kpis(str(d0), str(today), hotel.id)
pc = k['pace']
ly_first = m_first - relativedelta(years=1)
same_date_ly = today - relativedelta(years=1)
expected_ly = sum(
    1 for r in Res.search([('hotel_id', '=', hotel.id)])
    if r.line_ids[0].create_date.date() <= same_date_ly
    for d in range(r.nights)
    if ly_first <= r.checkin_date.date() + timedelta(days=d)
    < ly_first + relativedelta(months=1))
check("pace N-1 = nuitées du même mois déjà prises à la même date l'an "
      "dernier (%d, la réservation prise après ne compte pas)" % expected_ly,
      pc['nights_ly'] == expected_ly and expected_ly >= 5, pc)
check("le mois comparé est nommé (AAAA-MM)", pc['month'] == m_first.strftime('%Y-%m'), pc)
check("un écart en % est fourni", isinstance(pc['delta'], (int, float)), pc)

print("\n═══ 6. Le tableau de bord exécutif reprend ces chiffres, avec une phrase par indicateur ═══")
Exec = env['aite.exec.dashboard']
meta = Exec.get_meta()
hints = meta.get('hints') or {}
for key in ('occupancy', 'adr', 'revpar', 'pickup', 'pace'):
    check("infobulle « %s » : une phrase d'explication" % key,
          len(hints.get(key, "")) >= 40, hints.get(key))
check("l'infobulle du RevPAR parle de chambre disponible, vendue ou non",
      "disponible" in hints.get('revpar', "") and "vendue ou non" in hints.get('revpar', ""),
      hints.get('revpar'))
# Le tableau exécutif consolide TOUS les hôtels de la société : on le
# compare au PMS interrogé sans filtre d'hôtel.
k_all = Dash.get_kpis(str(d0), str(today))
p_all = k_all['period']
ek = Exec.get_kpis(str(d0), str(today))
check("RevPAR identique entre PMS et exécutif", round(ek['revpar']) == round(p_all['revpar']),
      (ek['revpar'], p_all['revpar']))
check("occupation identique", round(ek['occupancy'], 1) == round(p_all['occupancy'], 1))
check("pickup et pace transmis", ek['pickup']['nights'] == k_all['pickup']['nights']
      and ek['pace']['nights_ly'] == k_all['pace']['nights_ly'], (ek['pickup'], ek['pace']))
check("écarts N-1 transmis (occupation, ADR, RevPAR)",
      all(key in ek['deltas_ly'] for key in ('occupancy', 'adr', 'revpar')), ek['deltas_ly'])

print("\n═══ 7. Le cockpit Direction montre une tuile Hébergement avec les mêmes chiffres ═══")
if 'aite.direction.dashboard' in env:
    o = env['aite.direction.dashboard'].get_overview(str(d0), str(today))
    h = o.get('hotel')
    check("la tuile Hébergement est présente", bool(h), o.keys())
    if h:
        check("RevPAR identique au PMS", round(h['revpar']) == round(p_all['revpar']),
              (h['revpar'], p_all['revpar']))
        check("TO identique au PMS", round(h['occupancy'], 1) == round(p_all['occupancy'], 1),
              (h['occupancy'], p_all['occupancy']))
        check("écart N-1 fourni pour l'occupation", h['deltas_ly'].get('occupancy') is not None, h)
        check("chaque tuile porte sa phrase", all(len(h['hints'].get(x, "")) >= 40
                                                for x in ('occupancy', 'adr', 'revpar')), h['hints'])
        check("un lien vers le tableau de bord exécutif est proposé",
              bool(h.get('exec_action')), h.get('exec_action'))
else:
    print("  (cockpit Direction non installé : étape sautée)")

print("\n═══ 8. Sans aucune activité, tout reste lisible (zéros, pas d'erreur) ═══")
far = today - timedelta(days=900)
k0 = Dash.get_kpis(str(far), str(far + timedelta(days=5)), hotel.id)
check("RevPAR = 0 sur une période vide", k0['period']['revpar'] == 0.0)
check("écart N-1 absent (pas de base de comparaison)", k0['deltas_ly']['revpar'] is None)
ek0 = Exec.get_kpis('pas-une-date', None)
check("le tableau exécutif répond même avec une date invalide", 'revpar' in ek0)

env.cr.rollback()
print("\nRÉSULTAT : %d vérifications OK, %d KO" % (ok_count, len(ko)))
for label in ko:
    print("  KO :", label)
sys.exit(1 if ko else 0)
