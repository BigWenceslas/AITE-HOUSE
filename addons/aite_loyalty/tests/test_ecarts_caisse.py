# -*- coding: utf-8 -*-
"""Écarts relevés en tournant les vidéos (n° 28 et 29 de ECARTS.md)."""
from datetime import date, timedelta

from odoo import fields
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install', 'aite_loyalty')
class TestLoyaltyEcarts(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.env.user.tz = 'UTC'
        cls.engine = cls.env['aite.loyalty.engine']
        cls.company.write({
            'aite_loyalty_rate_per_1000': 1.0,
            'aite_loyalty_min_amount': 1000.0,
            'aite_loyalty_window_months': 12,
            'aite_loyalty_vip_min_spend': 500000.0,
            'aite_loyalty_vip_min_visits': 10,
            'aite_loyalty_vvip_min_spend': 2000000.0,
            'aite_loyalty_vvip_min_visits': 25,
            'aite_loyalty_vvip_min_domains': 3,
            'aite_slot_auto_post_folio': False,
        })
        cls.guest = cls.env['res.partner'].create({
            'name': "Client Fidèle Séjour", 'email': 'fidele@example.com'})

        # --- Hôtel & séjour ------------------------------------------------
        cls.hotel = cls.env['aite.hotel.hotel'].create({
            'name': "Hôtel Fidélité",
            'code': 'HFI',
            'company_id': cls.company.id,
        })
        cls.rtype = cls.env['aite.hotel.room.type'].create({
            'name': "Chambre Fidélité",
            'company_id': cls.company.id,
            'base_price': 50000.0,
            'capacity_adults': 2,
        })
        cls.rtype.product_id.sudo().write({'taxes_id': [(5, 0, 0)]})
        cls.room = cls.env['aite.hotel.room'].create({
            'name': 'FI1',
            'hotel_id': cls.hotel.id,
            'room_type_id': cls.rtype.id,
        })
        cls.service_product = cls.env['product.product'].create({
            'name': "Soin SPA fidélité",
            'type': 'service',
            'list_price': 20000.0,
            'sale_ok': True,
            'taxes_id': [(5, 0, 0)],
        })

    def _folio(self):
        Res = self.env['aite.hotel.reservation']
        today = fields.Date.context_today(self.env.user)
        reservation = Res.create({
            'hotel_id': self.hotel.id,
            'partner_id': self.guest.id,
            'checkin_date': Res._compose_datetime(today, 14.0),
            'checkout_date': Res._compose_datetime(
                today + timedelta(days=2), 12.0),
            'line_ids': [(0, 0, {
                'room_type_id': self.rtype.id,
                'room_id': self.room.id,
                'adults': 1,
            })],
        })
        reservation.action_confirm()
        return reservation.folio_id

    def _folio_points(self, folio):
        folio.action_create_invoice()
        move = folio.aite_loyalty_move_id
        self.assertTrue(move)
        self.assertEqual(move.origin_detail, 'hotel')
        return move

    # ------------------------------------------------------------------
    # N° 28 — rien n'est crédité deux fois, la taxe de séjour ne compte pas
    # ------------------------------------------------------------------

    def test_folio_credits_its_own_lines(self):
        """Référence : sans report, le folio rapporte son montant."""
        folio = self._folio()
        total = folio.amount_total
        move = self._folio_points(folio)
        self.assertEqual(move.amount_base, total)

    def test_city_tax_earns_no_points(self):
        """La taxe de séjour est reversée à la commune : pas de points."""
        Line = self.env['aite.hotel.folio.line']
        types = dict(Line._fields['line_type']._description_selection(
            self.env))
        if 'city_tax' not in types:
            self.skipTest("Taxe de séjour (aite_city_tax) absente")
        folio = self._folio()
        stay = sum(folio.line_ids.filtered(
            lambda l: l.line_type != 'city_tax').mapped('price_total'))
        Line.create({
            'folio_id': folio.id,
            'line_type': 'city_tax',
            'product_id': self.service_product.id,
            'name': "Taxe de séjour (test)",
            'quantity': 1,
            'price_unit': 12000.0,
        })
        folio.invalidate_recordset()
        self.assertGreater(folio.amount_total, stay)
        move = self._folio_points(folio)
        self.assertEqual(move.amount_base, stay)

    def test_slot_posted_to_folio_is_not_credited_twice(self):
        """Une prestation créditée à sa réalisation puis reportée au folio
        ne rapporte rien une seconde fois."""
        folio = self._folio()
        stay = folio.amount_total
        cabine = self.env['aite.booking.resource'].create({
            'name': "Cabine fidélité",
            'kind': 'spa',
            'company_id': self.company.id,
            'capacity': 1,
            'open_hour': 0.0,
            'close_hour': 23.5,
            'slot_minutes': '30',
        })
        service = self.env['aite.booking.service'].create({
            'name': "Massage fidélité",
            'kind': 'spa',
            'company_id': self.company.id,
            'duration_minutes': 60,
            'price': 20000.0,
            'product_id': self.service_product.id,
        })
        start = fields.Datetime.now().replace(
            minute=0, second=0, microsecond=0) + timedelta(days=1)
        booking = self.env['aite.slot.booking'].create({
            'resource_id': cabine.id,
            'service_id': service.id,
            'partner_id': self.guest.id,
            'company_id': self.company.id,
            'start': start,
            'stop': start + timedelta(hours=1),
            'folio_id': folio.id,
        })
        booking.action_confirm()
        booking.action_done()
        self.assertEqual(booking.aite_loyalty_move_id.amount_base, 20000.0)
        booking.action_post_to_folio()
        self.assertTrue(booking.posted_line_id)
        folio.invalidate_recordset()
        self.assertEqual(folio.amount_total, stay + 20000.0)
        move = self._folio_points(folio)
        self.assertEqual(move.amount_base, stay)

    def test_room_charge_ticket_is_not_credited_twice(self):
        """Un ticket « Note de chambre » crédité au POS ne rapporte rien
        de plus au folio."""
        PosOrder = self.env['pos.order']
        if 'aite_folio_line_id' not in PosOrder._fields:
            self.skipTest("Note de chambre (aite_hotel_pos_link) absente")
        folio = self._folio()
        stay = folio.amount_total
        method = self.env['pos.payment.method'].create({
            'name': "Note de chambre (fidélité)",
            'is_room_charge': True,
            'company_id': self.company.id,
        })
        config = self.env['pos.config'].create({
            'name': "Bar fidélité",
            'payment_method_ids': [(6, 0, method.ids)],
        })
        drink = self.env['product.product'].create({
            'name': "Cocktail fidélité",
            'type': 'consu',
            'available_in_pos': True,
            'list_price': 15000.0,
            'taxes_id': [(5, 0, 0)],
        })
        config.open_ui()
        order = PosOrder.create({
            'session_id': config.current_session_id.id,
            'company_id': self.company.id,
            'partner_id': self.guest.id,
            'amount_tax': 0.0,
            'amount_total': 15000.0,
            'amount_paid': 15000.0,
            'amount_return': 0.0,
            'lines': [(0, 0, {
                'product_id': drink.id, 'qty': 1, 'price_unit': 15000.0,
                'price_subtotal': 15000.0, 'price_subtotal_incl': 15000.0,
            })],
        })
        self.env['pos.payment'].create({
            'pos_order_id': order.id,
            'payment_method_id': method.id,
            'amount': 15000.0,
        })
        order.write({'state': 'paid'})
        self.assertEqual(order.aite_loyalty_move_id.amount_base, 15000.0)
        self.assertEqual(order.aite_folio_line_id.folio_id, folio)
        folio.invalidate_recordset()
        self.assertEqual(folio.amount_total, stay + 15000.0)
        move = self._folio_points(folio)
        self.assertEqual(move.amount_base, stay)

    # ------------------------------------------------------------------
    # N° 29 — famille « Autre », rétrogradation par société
    # ------------------------------------------------------------------

    def test_other_family_is_a_valid_origin(self):
        move = self.engine.award(self.guest, 10000.0, 'slot_other')
        self.assertEqual(move.origin_detail, 'slot_other')

    def test_other_family_booking_can_be_done(self):
        resource = self.env['aite.booking.resource'].create({
            'name': "Atelier divers",
            'kind': 'other',
            'company_id': self.company.id,
            'capacity': 1,
            'open_hour': 0.0,
            'close_hour': 23.5,
            'slot_minutes': '60',
            'price_hour': 10000.0,
        })
        start = fields.Datetime.now().replace(
            minute=0, second=0, microsecond=0) + timedelta(days=1)
        booking = self.env['aite.slot.booking'].create({
            'resource_id': resource.id,
            'partner_id': self.guest.id,
            'company_id': self.company.id,
            'start': start,
            'stop': start + timedelta(hours=1),
        })
        booking.action_confirm()
        booking.action_done()
        self.assertEqual(booking.state, 'done')
        self.assertEqual(
            booking.aite_loyalty_move_id.origin_detail, 'slot_other')

    def test_vip_of_another_company_is_not_demoted(self):
        """Un VIP actif dans la société B ne redescend pas parce que la
        société A ne lui connaît aucune activité."""
        other = self.env['res.company'].create({
            'name': "AAA Société B (fidélité)",
            'sequence': 0,
            'aite_loyalty_window_months': 12,
            'aite_loyalty_vip_min_spend': 500000.0,
            'aite_loyalty_vip_min_visits': 10,
            'aite_loyalty_vvip_min_spend': 2000000.0,
            'aite_loyalty_vvip_min_visits': 25,
            'aite_loyalty_vvip_min_domains': 3,
        })
        partner = self.env['res.partner'].create({'name': "VIP de B"})
        Move = self.env['aite.loyalty.move']
        for i in range(12):
            Move.create({
                'partner_id': partner.id,
                'company_id': other.id,
                'date': date.today() - timedelta(days=1 + i),
                'points': 50,
                'amount_base': 50000.0,
                'origin_detail': 'pos',
            })
        self.engine.recompute_tiers(partner_ids=[partner.id])
        partner.invalidate_recordset()
        self.assertEqual(partner.loyalty_tier, 'vip')
