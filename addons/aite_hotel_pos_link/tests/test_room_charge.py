# -*- coding: utf-8 -*-
"""Note de chambre : report d'une consommation POS sur le folio du séjour."""
from datetime import timedelta

from odoo import fields
from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install', 'aite_roomcharge')
class TestRoomCharge(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.env.user.tz = 'UTC'

        # --- Hôtel & séjour ------------------------------------------------
        cls.hotel = cls.env['aite.hotel.hotel'].create({
            'name': "Hôtel Note de chambre",
            'code': 'HNC',
            'company_id': cls.company.id,
        })
        cls.rtype = cls.env['aite.hotel.room.type'].create({
            'name': "Chambre NC",
            'company_id': cls.company.id,
            'base_price': 70000.0,
            'capacity_adults': 2,
        })
        cls.rtype.product_id.sudo().write({'taxes_id': [(5, 0, 0)]})
        cls.room = cls.env['aite.hotel.room'].create({
            'name': 'NC1',
            'hotel_id': cls.hotel.id,
            'room_type_id': cls.rtype.id,
        })
        cls.room_2 = cls.env['aite.hotel.room'].create({
            'name': 'NC2',
            'hotel_id': cls.hotel.id,
            'room_type_id': cls.rtype.id,
        })
        cls.guest = cls.env['res.partner'].create({'name': "Client Note"})
        cls.walkin = cls.env['res.partner'].create({'name': "Client Passage"})

        # --- Caisse --------------------------------------------------------
        # Journal dédié : un journal de caisse ne peut servir qu'à un
        # seul moyen de paiement « espèces », et la base peut déjà en
        # porter un (jeu de démonstration).
        cls.cash_journal = cls.env['account.journal'].create({
            'name': "Caisse note de chambre (test)",
            'type': 'cash',
            'code': 'CNCTS',
            'company_id': cls.company.id,
        })
        cls.method_cash = cls.env['pos.payment.method'].create({
            'name': "Espèces NC",
            'journal_id': cls.cash_journal.id,
            'company_id': cls.company.id,
        })
        cls.method_room = cls.env['pos.payment.method'].create({
            'name': "Note de chambre",
            'is_room_charge': True,
            'company_id': cls.company.id,
        })
        cls.pos_config = cls.env['pos.config'].create({
            'name': "Bar de l'hôtel",
            'payment_method_ids': [
                (6, 0, (cls.method_cash | cls.method_room).ids)],
        })
        cls.drink = cls.env['product.product'].create({
            'name': "Cocktail maison",
            'type': 'consu',
            'available_in_pos': True,
            'list_price': 12000.0,
            'taxes_id': [(5, 0, 0)],
        })
        cls.pos_config.open_ui()
        cls.session = cls.pos_config.current_session_id

    # ------------------------------------------------------------------
    # Fabriques
    # ------------------------------------------------------------------

    def _folio(self, partner=None, room=None, offset=0):
        Res = self.env['aite.hotel.reservation']
        today = fields.Date.context_today(self.env.user)
        reservation = Res.create({
            'hotel_id': self.hotel.id,
            'partner_id': (partner or self.guest).id,
            'checkin_date': Res._compose_datetime(
                today + timedelta(days=offset), 14.0),
            'checkout_date': Res._compose_datetime(
                today + timedelta(days=offset + 2), 12.0),
            'line_ids': [(0, 0, {
                'room_type_id': self.rtype.id,
                'room_id': (room or self.room).id,
                'adults': 1,
            })],
        })
        reservation.action_confirm()
        return reservation.folio_id

    def _pos_order(self, payments, partner=None, total=12000.0):
        order = self.env['pos.order'].create({
            'session_id': self.session.id,
            'company_id': self.company.id,
            'partner_id': partner.id if partner else False,
            'amount_tax': 0.0,
            'amount_total': total,
            'amount_paid': total,
            'amount_return': 0.0,
            'lines': [(0, 0, {
                'product_id': self.drink.id,
                'qty': 1,
                'price_unit': total,
                'price_subtotal': total,
                'price_subtotal_incl': total,
            })],
        })
        for method, amount in payments:
            self.env['pos.payment'].create({
                'pos_order_id': order.id,
                'payment_method_id': method.id,
                'amount': amount,
            })
        order.write({'state': 'paid'})
        return order

    # ------------------------------------------------------------------
    # Décisions (fonctions pures)
    # ------------------------------------------------------------------

    def test_room_charge_amount_sums_flagged_payments(self):
        Order = self.env['pos.order']
        self.assertEqual(
            Order._room_charge_amount(
                [(True, 5000.0), (False, 3000.0), (True, 2000.0)]),
            7000.0)

    def test_room_charge_amount_is_zero_without_flag(self):
        Order = self.env['pos.order']
        self.assertEqual(
            Order._room_charge_amount([(False, 5000.0)]), 0.0)

    def test_room_charge_amount_tolerates_none(self):
        Order = self.env['pos.order']
        self.assertEqual(
            Order._room_charge_amount([(True, None)]), 0.0)

    def test_decision_post_with_one_folio(self):
        Order = self.env['pos.order']
        self.assertEqual(Order._match_decision(True, 1), 'post')

    def test_decision_pending_without_customer(self):
        Order = self.env['pos.order']
        self.assertEqual(Order._match_decision(False, 1), 'pending')

    def test_decision_pending_without_folio(self):
        Order = self.env['pos.order']
        self.assertEqual(Order._match_decision(True, 0), 'pending')

    def test_decision_pending_with_several_folios(self):
        Order = self.env['pos.order']
        self.assertEqual(Order._match_decision(True, 3), 'pending')

    def test_folio_line_vals_shape(self):
        Order = self.env['pos.order']
        vals = Order._pos_folio_line_vals(
            1, 2, "POS/0001", '2026-01-01', 12000.0)
        self.assertEqual(vals['line_type'], 'service')
        self.assertEqual(vals['quantity'], 1)
        self.assertEqual(vals['price_unit'], 12000.0)

    # ------------------------------------------------------------------
    # Chemin nominal
    # ------------------------------------------------------------------

    def test_charge_posts_to_the_open_folio(self):
        folio = self._folio()
        before = folio.amount_total
        order = self._pos_order([(self.method_room, 12000.0)],
                                partner=self.guest)
        self.assertTrue(order.aite_folio_line_id)
        self.assertFalse(order.aite_roomcharge_pending_id)
        line = order.aite_folio_line_id
        self.assertEqual(line.folio_id, folio)
        self.assertEqual(line.price_unit, 12000.0)
        self.assertIn(order.name, line.name)
        folio.invalidate_recordset()
        self.assertEqual(folio.amount_total, before + 12000.0)

    def test_mixed_payment_posts_only_the_room_part(self):
        """Moitié espèces, moitié note de chambre."""
        folio = self._folio()
        before = folio.amount_total
        order = self._pos_order(
            [(self.method_cash, 5000.0), (self.method_room, 7000.0)],
            partner=self.guest)
        self.assertEqual(order.aite_folio_line_id.price_unit, 7000.0)
        folio.invalidate_recordset()
        self.assertEqual(folio.amount_total, before + 7000.0)

    def test_cash_only_order_touches_nothing(self):
        self._folio()
        order = self._pos_order([(self.method_cash, 12000.0)],
                                partner=self.guest)
        self.assertFalse(order.aite_folio_line_id)
        self.assertFalse(order.aite_roomcharge_pending_id)

    def test_posting_is_idempotent(self):
        self._folio()
        order = self._pos_order([(self.method_room, 12000.0)],
                                partner=self.guest)
        first = order.aite_folio_line_id
        order._aite_process_room_charge()
        order._aite_process_room_charge()
        self.assertEqual(order.aite_folio_line_id, first)

    def test_unpaid_order_is_not_posted(self):
        self._folio()
        order = self.env['pos.order'].create({
            'session_id': self.session.id,
            'company_id': self.company.id,
            'partner_id': self.guest.id,
            'amount_tax': 0.0,
            'amount_total': 12000.0,
            'amount_paid': 0.0,
            'amount_return': 0.0,
            'lines': [(0, 0, {
                'product_id': self.drink.id, 'qty': 1,
                'price_unit': 12000.0, 'price_subtotal': 12000.0,
                'price_subtotal_incl': 12000.0,
            })],
        })
        self.env['pos.payment'].create({
            'pos_order_id': order.id,
            'payment_method_id': self.method_room.id,
            'amount': 12000.0,
        })
        order._aite_process_room_charge()
        self.assertFalse(order.aite_folio_line_id)

    # ------------------------------------------------------------------
    # File d'attente
    # ------------------------------------------------------------------

    def test_anonymous_order_goes_to_the_queue(self):
        order = self._pos_order([(self.method_room, 12000.0)], partner=None)
        pending = order.aite_roomcharge_pending_id
        self.assertTrue(pending)
        self.assertEqual(pending.state, 'todo')
        self.assertEqual(pending.amount, 12000.0)
        self.assertIn("non identifié", pending.note)

    def test_customer_without_folio_goes_to_the_queue(self):
        order = self._pos_order([(self.method_room, 12000.0)],
                                partner=self.walkin)
        pending = order.aite_roomcharge_pending_id
        self.assertTrue(pending)
        self.assertIn("Aucun folio", pending.note)

    def test_several_open_folios_go_to_the_queue(self):
        self._folio(room=self.room, offset=0)
        self._folio(room=self.room_2, offset=10)
        order = self._pos_order([(self.method_room, 12000.0)],
                                partner=self.guest)
        pending = order.aite_roomcharge_pending_id
        self.assertTrue(pending)
        self.assertIn("2 folios", pending.note)

    def test_resolving_the_queue_posts_to_the_chosen_folio(self):
        folio = self._folio()
        order = self._pos_order([(self.method_room, 12000.0)], partner=None)
        pending = order.aite_roomcharge_pending_id
        pending.folio_id = folio.id
        pending.action_resolve()
        self.assertEqual(pending.state, 'done')
        self.assertTrue(order.aite_folio_line_id)
        self.assertEqual(order.aite_folio_line_id.folio_id, folio)

    def test_resolving_fills_in_the_missing_customer(self):
        folio = self._folio()
        order = self._pos_order([(self.method_room, 12000.0)], partner=None)
        pending = order.aite_roomcharge_pending_id
        pending.folio_id = folio.id
        pending.action_resolve()
        self.assertEqual(pending.partner_id, self.guest)

    def test_resolving_without_a_folio_is_refused(self):
        order = self._pos_order([(self.method_room, 12000.0)], partner=None)
        with self.assertRaises(UserError):
            order.aite_roomcharge_pending_id.action_resolve()

    def test_resolving_onto_a_closed_folio_is_refused(self):
        folio = self._folio()
        order = self._pos_order([(self.method_room, 12000.0)], partner=None)
        pending = order.aite_roomcharge_pending_id
        pending.folio_id = folio.id
        folio.action_create_invoice()
        with self.assertRaises(UserError):
            pending.action_resolve()

    def test_resolving_twice_is_harmless(self):
        folio = self._folio()
        order = self._pos_order([(self.method_room, 12000.0)], partner=None)
        pending = order.aite_roomcharge_pending_id
        pending.folio_id = folio.id
        pending.action_resolve()
        pending.action_resolve()
        self.assertEqual(
            self.env['aite.hotel.folio.line'].search_count([
                ('folio_id', '=', folio.id),
                ('name', 'like', order.name),
            ]), 1)

    # ------------------------------------------------------------------
    # Article de report
    # ------------------------------------------------------------------

    def test_default_product_is_used(self):
        self.company.aite_roomcharge_product_id = False
        self._folio()
        order = self._pos_order([(self.method_room, 12000.0)],
                                partner=self.guest)
        expected = self.env.ref(
            'aite_hotel_pos_link.product_roomcharge_pos')
        self.assertEqual(order.aite_folio_line_id.product_id, expected)

    def test_configured_product_takes_precedence(self):
        custom = self.env['product.product'].create({
            'name': "Report bar sur mesure",
            'type': 'service',
            'sale_ok': True,
            'taxes_id': [(5, 0, 0)],
        })
        self.company.aite_roomcharge_product_id = custom
        self._folio()
        order = self._pos_order([(self.method_room, 12000.0)],
                                partner=self.guest)
        self.assertEqual(order.aite_folio_line_id.product_id, custom)
