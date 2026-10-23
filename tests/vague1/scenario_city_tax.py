# -*- coding: utf-8 -*-
"""
Parcours « réceptionniste novice » — taxe de séjour.
Exécuté dans le shell Odoo : python3 odoo-bin shell -c conf -d db < ce_fichier

Le scénario ne fait QUE ce qu'un utilisateur ferait depuis l'écran :
créer l'hôtel, une chambre, un client, une réservation, confirmer, modifier
les occupants, changer les dates, facturer. À chaque étape on vérifie ce
que l'écran afficherait.
"""
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


cm = env.ref('base.cm')
XAF = env.ref('base.XAF')
company = env.company
# La société doit être en FCFA pour un test réaliste
if company.currency_id != XAF:
    XAF.active = True  # sinon Odoo refuse de valider la facture (devise inactive)
    env.cr.execute("UPDATE res_company SET currency_id=%s WHERE id=%s",
                   (XAF.id, company.id))
    company.invalidate_recordset()
company.country_id = cm

print("\n═══ 1. Le gérant crée son hôtel (3 étoiles, Douala) ═══")
hotel = env['aite.hotel.hotel'].create({
    'name': "Hôtel Test Douala", 'code': 'HTD', 'stars': '3',
    'country_id': cm.id, 'city': 'Douala',
})
check("le barème s'est appliqué tout seul", bool(hotel.city_tax_rate_id))
check("montant 3★ Cameroun = 3 000 F", hotel.city_tax_amount == 3000,
      hotel.city_tax_amount)
# Le symbole de la devise (« FCFA »), pas son code ISO (« XAF ») : ECARTS n° 7.
check("l'explication est lisible, en FCFA", "3 000 FCFA" in (hotel.city_tax_help or ""),
      hotel.city_tax_help)
check("le libellé du barème dit « FCFA » (ECARTS n° 39)",
      "3 000 FCFA" in hotel.city_tax_rate_id.display_name, hotel.city_tax_rate_id.display_name)
print("     Écran dit : « %s »" % hotel.city_tax_help)

print("\n═══ 2. Il crée un type de chambre et une chambre ═══")
rtype = env['aite.hotel.room.type'].create({
    'name': "Standard", 'code': 'STD', 'base_price': 25000,
    'capacity_adults': 2, 'capacity_children': 1,
})
room = env['aite.hotel.room'].create({
    'name': "101", 'hotel_id': hotel.id, 'room_type_id': rtype.id,
})
check("chambre créée et libre", room.status == 'free', room.status)

print("\n═══ 3. Un client arrive : réservation 2 nuits, 2 adultes ═══")
guest = env['res.partner'].create({'name': "Mballa Jean", 'phone': '690000000'})
Res = env['aite.hotel.reservation']
cin = Res._default_checkin()
cout = cin + timedelta(days=2)
res = Res.create({
    'hotel_id': hotel.id, 'partner_id': guest.id,
    'checkin_date': cin, 'checkout_date': cout,
    'line_ids': [(0, 0, {'room_type_id': rtype.id, 'room_id': room.id,
                         'adults': 2, 'children': 0})],
})
check("2 nuits calculées", res.nights == 2, res.nights)
check("avant confirmation : pas de folio, donc pas de taxe", not res.folio_id)

print("\n═══ 4. Il clique « Confirmer » ═══")
res.action_confirm()
folio = res.folio_id
check("un folio est ouvert", bool(folio))
tax_lines = folio.line_ids.filtered(lambda l: l.line_type == 'city_tax')
check("UNE ligne « Taxe de séjour » est apparue sans rien faire",
      len(tax_lines) == 1, len(tax_lines))
tl = tax_lines[:1]
check("quantité = 2 nuits × 2 adultes = 4", tl.quantity == 4, tl.quantity)
check("prix unitaire = 3 000 F", tl.price_unit == 3000, tl.price_unit)
check("montant = 12 000 F", folio.amount_city_tax == 12000, folio.amount_city_tax)
check("aucune TVA sur la taxe", not tl.tax_ids)
check("le libellé explique le calcul", "4 nuitée" in tl.name and "3 ★" in tl.name,
      tl.name)
print("     Ligne : « %s » — %s × %s = %s" % (tl.name, tl.quantity, tl.price_unit,
                                              tl.price_total))
room_lines = folio.line_ids.filtered(lambda l: l.line_type == 'room')
check("la nuitée est toujours là (50 000 F)",
      room_lines and room_lines[0].price_subtotal == 50000,
      room_lines.mapped('price_subtotal'))
check("total folio = 50 000 + 12 000 (+TVA éventuelle sur nuitée)",
      folio.amount_total >= 62000, folio.amount_total)

print("\n═══ 5. Le client annonce un 3e adulte… non, un enfant (non taxé au CM) ═══")
res.line_ids[0].children = 1
tl = folio.line_ids.filtered(lambda l: l.line_type == 'city_tax')
check("enfant non compté : toujours 4 unités", tl.quantity == 4, tl.quantity)

print("\n═══ 6. Il prolonge le séjour d'une nuit depuis la réservation ═══")
res.checkout_date = cout + timedelta(days=1)
tl = folio.line_ids.filtered(lambda l: l.line_type == 'city_tax')
check("3 nuits × 2 adultes = 6 unités", tl.quantity == 6, tl.quantity)
check("montant recalculé = 18 000 F", folio.amount_city_tax == 18000,
      folio.amount_city_tax)
check("toujours une seule ligne de taxe", len(tl) == 1, len(tl))

print("\n═══ 7. Le gérant corrige : l'hôtel est en fait 4 étoiles ═══")
hotel.stars = '4'
tl = folio.line_ids.filtered(lambda l: l.line_type == 'city_tax')
check("le folio ouvert suit le nouveau barème (4 000 F)", tl.price_unit == 4000,
      tl.price_unit)
check("montant = 6 × 4 000 = 24 000 F", folio.amount_city_tax == 24000,
      folio.amount_city_tax)
hotel.stars = '3'

print("\n═══ 8. Check-in, puis facture au départ ═══")
res.action_checkin()
check("client arrivé", res.state == 'checked_in', res.state)
folio.action_create_invoice()
check("facture créée et comptabilisée", folio.move_id and folio.move_id.state == 'posted')
inv_tax = folio.move_id.invoice_line_ids.filtered(
    lambda l: l.product_id == hotel.city_tax_product_id)
check("la facture porte la ligne de taxe de séjour", len(inv_tax) == 1, len(inv_tax))
check("… pour 18 000 F sans TVA", inv_tax.price_subtotal == 18000 and not inv_tax.tax_ids,
      (inv_tax.price_subtotal, inv_tax.tax_ids))

print("\n═══ 9. Après facturation, plus rien ne bouge ═══")
hotel.stars = '5'
tl = folio.line_ids.filtered(lambda l: l.line_type == 'city_tax')
check("le folio facturé n'est pas recalculé", tl.price_unit == 3000, tl.price_unit)
hotel.stars = '3'

print("\n═══ 10. L'état mensuel ═══")
rows = env['aite.city.tax.report'].search([('folio_id', '=', folio.id)])
check("le séjour apparaît dans l'état", len(rows) == 1, len(rows))
check("montant collecté = 18 000 F, 6 nuitées", rows.amount == 18000 and rows.units == 6,
      (rows.amount, rows.units))
check("le mois est celui du départ", rows.month == res.checkout_date.strftime('%Y-%m'),
      rows.month)

print("\n═══ 11. Hôtel exonéré : on décoche, la taxe disparaît des folios ouverts ═══")
res2 = Res.create({
    'hotel_id': hotel.id, 'partner_id': guest.id,
    'checkin_date': cin + timedelta(days=10),
    'checkout_date': cin + timedelta(days=11),
    'line_ids': [(0, 0, {'room_type_id': rtype.id, 'room_id': room.id, 'adults': 1})],
})
res2.action_confirm()
check("nouveau séjour taxé (1 × 1 × 3 000)", res2.folio_id.amount_city_tax == 3000,
      res2.folio_id.amount_city_tax)
hotel.city_tax_enabled = False
check("exonération : ligne retirée du folio ouvert", res2.folio_id.amount_city_tax == 0,
      res2.folio_id.amount_city_tax)
check("message d'écran explicite", "désactivée" in hotel.city_tax_help)
hotel.city_tax_enabled = True
check("réactivation : la ligne revient", res2.folio_id.amount_city_tax == 3000,
      res2.folio_id.amount_city_tax)

print("\n═══ 12. Pays sans barème : pas de taxe, mais un message qui guide ═══")
hotel_td = env['aite.hotel.hotel'].create({
    'name': "Hôtel N'Djamena", 'code': 'NDJ', 'stars': '3',
    'country_id': env.ref('base.td').id,
})
check("aucun barème", not hotel_td.city_tax_rate_id)
check("l'écran dit où ajouter le barème (chemin réel du menu)",
      "Hôtel → Configuration → Barèmes de taxe de séjour" in hotel_td.city_tax_help,
      hotel_td.city_tax_help)
# Le responsable ajoute le barème du Tchad : l'hôtel le prend tout seul (ECARTS n° 73).
rate_td = env['aite.city.tax.rate'].create({
    'country_id': env.ref('base.td').id, 'stars': '3', 'amount': 1000,
    'currency_id': XAF.id,
})
check("barème ajouté après coup → appliqué à l'hôtel", hotel_td.city_tax_rate_id == rate_td,
      hotel_td.city_tax_rate_id)

print("\n═══ 13. La ligne de taxe ne se supprime pas à la main (ECARTS n° 57) ═══")
tl2 = res2.folio_id.line_ids.filtered(lambda l: l.line_type == 'city_tax')
try:
    tl2.unlink(); check("suppression à la main refusée", False)
except Exception as e:
    check("suppression à la main refusée, message qui dit quoi faire",
          "Collecter la taxe de séjour" in str(e), str(e)[:80])

env.cr.rollback()
print("\n══════════════════════════════════════")
print("RÉSULTAT : %d vérifications OK, %d KO" % (ok_count, len(ko)))
for k in ko:
    print("  KO : " + k)
sys.exit(1 if ko else 0)
