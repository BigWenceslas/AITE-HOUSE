# -*- coding: utf-8 -*-
"""Assistants front desk : disponibilité, check-out, encaissement,
changement de chambre."""
from datetime import timedelta

from odoo import fields
from odoo.exceptions import UserError
from odoo.tests import tagged

from .common import HotelCommon


@tagged('post_install', '-at_install', 'aite_hotel')
class TestBookingWizard(HotelCommon):

    def _wizard(self, **kwargs):
        vals = {
            'hotel_id': self.hotel.id,
            'checkin_date': self._dt(0, 14.0),
            'checkout_date': self._dt(2, 12.0),
            'partner_id': self.guest.id,
            'adults': 1,
        }
        vals.update(kwargs)
        return self.env['aite.hotel.booking.wizard'].create(vals)

    def test_search_lists_free_rooms_with_price(self):
        wizard = self._wizard()
        wizard.action_search()
        self.assertTrue(wizard.searched)
        self.assertEqual(len(wizard.line_ids), 3)
        std_line = wizard.line_ids.filtered(
            lambda l: l.room_id == self.room_101)
        self.assertEqual(std_line.price_night, 50000.0)
        self.assertEqual(std_line.nights, 2)
        self.assertEqual(std_line.price_total, 100000.0)

    def test_search_excludes_busy_rooms(self):
        self._make_reservation(checkin_offset=0,
                               checkout_offset=2).action_confirm()
        wizard = self._wizard()
        wizard.action_search()
        self.assertNotIn(self.room_101, wizard.line_ids.mapped('room_id'))

    def test_search_excludes_out_of_order_rooms(self):
        self.room_102.out_of_order = True
        wizard = self._wizard()
        wizard.action_search()
        self.assertNotIn(self.room_102, wizard.line_ids.mapped('room_id'))

    def test_search_filters_by_capacity(self):
        """3 adultes : seules les chambres assez grandes remontent."""
        wizard = self._wizard(adults=3)
        wizard.action_search()
        self.assertEqual(wizard.line_ids.mapped('room_id'), self.room_201)

    def test_search_filters_by_room_type(self):
        wizard = self._wizard(room_type_id=self.type_suite.id)
        wizard.action_search()
        self.assertEqual(wizard.line_ids.mapped('room_id'), self.room_201)

    def test_search_refuses_inverted_dates(self):
        wizard = self._wizard(checkin_date=self._dt(3, 14.0),
                              checkout_date=self._dt(1, 12.0))
        with self.assertRaises(UserError):
            wizard.action_search()

    def test_book_creates_confirmed_reservation(self):
        wizard = self._wizard()
        wizard.action_search()
        wizard.line_ids.filtered(
            lambda l: l.room_id == self.room_101).selected = True
        action = wizard.action_book()
        reservation = self.env['aite.hotel.reservation'].browse(
            action['res_id'])
        self.assertEqual(reservation.state, 'confirmed')
        self.assertEqual(reservation.line_ids.room_id, self.room_101)
        self.assertTrue(reservation.folio_id)

    def test_book_in_draft_when_unchecked(self):
        wizard = self._wizard(confirm_immediately=False)
        wizard.action_search()
        wizard.line_ids[0].selected = True
        action = wizard.action_book()
        reservation = self.env['aite.hotel.reservation'].browse(
            action['res_id'])
        self.assertEqual(reservation.state, 'draft')

    def test_book_requires_a_selection(self):
        wizard = self._wizard()
        wizard.action_search()
        with self.assertRaises(UserError):
            wizard.action_book()

    def test_book_requires_a_guest(self):
        wizard = self._wizard(partner_id=False)
        wizard.action_search()
        wizard.line_ids[0].selected = True
        with self.assertRaises(UserError):
            wizard.action_book()

    def test_book_caps_occupancy_to_room_capacity(self):
        """L'occupation demandée est bornée par la capacité réelle."""
        wizard = self._wizard(adults=2, children=5)
        wizard.action_search()
        wizard.line_ids.filtered(
            lambda l: l.room_id == self.room_101).selected = True
        action = wizard.action_book()
        reservation = self.env['aite.hotel.reservation'].browse(
            action['res_id'])
        self.assertEqual(reservation.line_ids.adults, 2)
        self.assertEqual(reservation.line_ids.children, 1)

    def test_book_multiple_rooms_at_once(self):
        wizard = self._wizard()
        wizard.action_search()
        wizard.line_ids.filtered(
            lambda l: l.room_id in (self.room_101 | self.room_102)
        ).selected = True
        action = wizard.action_book()
        reservation = self.env['aite.hotel.reservation'].browse(
            action['res_id'])
        self.assertEqual(len(reservation.line_ids), 2)


@tagged('post_install', '-at_install', 'aite_hotel')
class TestCheckoutWizard(HotelCommon):

    def setUp(self):
        super().setUp()
        self.reservation = self._make_reservation(checkin_offset=0,
                                                  checkout_offset=3)
        self.reservation.action_confirm()
        self.reservation.action_checkin()

    def _wizard(self, **kwargs):
        vals = {'reservation_id': self.reservation.id}
        vals.update(kwargs)
        return self.env['aite.hotel.checkout.wizard'].create(vals)

    def test_checkout_closes_stay_and_invoices(self):
        wizard = self._wizard(checkout_now=self._dt(3, 12.0))
        wizard.action_confirm()
        self.assertEqual(self.reservation.state, 'checked_out')
        self.assertTrue(self.reservation.actual_checkout)
        self.assertTrue(self.reservation.folio_id.move_id)
        self.assertEqual(self.reservation.folio_id.state, 'invoiced')

    def test_checkout_creates_housekeeping_task(self):
        wizard = self._wizard(checkout_now=self._dt(3, 12.0))
        wizard.action_confirm()
        task = self.env['aite.hotel.housekeeping'].search([
            ('room_id', '=', self.room_101.id),
            ('task_type', '=', 'checkout_clean'),
        ])
        self.assertTrue(task)
        self.assertEqual(self.room_101.hk_state, 'to_clean')

    def test_early_checkout_flag(self):
        wizard = self._wizard(checkout_now=self._dt(1, 10.0))
        self.assertTrue(wizard.is_early)

    def test_early_checkout_recomputes_nights(self):
        """Départ anticipé : on ne facture que les nuits réellement passées."""
        self.assertEqual(self.reservation.nights, 3)
        wizard = self._wizard(checkout_now=self._dt(1, 10.0),
                              recompute_nights=True, create_invoice=False)
        wizard.action_confirm()
        self.assertEqual(self.reservation.nights, 1)
        room_line = self.reservation.folio_id.line_ids.filtered(
            lambda l: l.line_type == 'room')
        self.assertEqual(room_line.quantity, 1)

    def test_early_checkout_without_recompute_keeps_nights(self):
        wizard = self._wizard(checkout_now=self._dt(1, 10.0),
                              recompute_nights=False, create_invoice=False)
        wizard.action_confirm()
        self.assertEqual(self.reservation.nights, 3)

    def test_same_day_checkout_bills_one_night(self):
        """Départ le jour de l'arrivée : une nuitée minimum (day-use)."""
        wizard = self._wizard(checkout_now=self._dt(0, 18.0),
                              recompute_nights=True, create_invoice=False)
        wizard.action_confirm()
        self.assertEqual(self.reservation.nights, 1)

    def test_checkout_refused_when_not_checked_in(self):
        other = self._make_reservation(rooms=self.room_201,
                                       checkin_offset=0, checkout_offset=2)
        other.action_confirm()
        wizard = self.env['aite.hotel.checkout.wizard'].create({
            'reservation_id': other.id,
        })
        with self.assertRaises(UserError):
            wizard.action_confirm()

    def test_checkout_without_invoice_shows_folio(self):
        wizard = self._wizard(checkout_now=self._dt(3, 12.0),
                              create_invoice=False)
        action = wizard.action_confirm()
        self.assertEqual(action['res_model'], 'aite.hotel.folio')
        self.assertFalse(self.reservation.folio_id.move_id)

    def test_open_checkout_wizard_requires_checked_in(self):
        other = self._make_reservation(rooms=self.room_201,
                                       checkin_offset=0, checkout_offset=2)
        with self.assertRaises(UserError):
            other.action_open_checkout_wizard()


@tagged('post_install', '-at_install', 'aite_hotel')
class TestPaymentAndRoomChangeWizards(HotelCommon):

    def setUp(self):
        super().setUp()
        self.reservation = self._make_reservation(checkin_offset=0,
                                                  checkout_offset=2)
        self.reservation.action_confirm()
        self.folio = self.reservation.folio_id

    def test_payment_wizard_creates_payment(self):
        wizard = self.env['aite.hotel.payment.wizard'].create({
            'folio_id': self.folio.id,
            'amount': 45000.0,
            'method': 'orange',
            'transaction_ref': 'OM-TEST-001',
        })
        wizard.action_confirm()
        payment = self.folio.payment_ids
        self.assertEqual(len(payment), 1)
        self.assertEqual(payment.amount, 45000.0)
        self.assertEqual(payment.method, 'orange')
        self.assertEqual(payment.transaction_ref, 'OM-TEST-001')
        self.assertEqual(self.folio.amount_residual, 55000.0)

    def test_payment_wizard_default_amount_is_residual(self):
        action = self.folio.action_register_payment()
        self.assertEqual(action['context']['default_amount'],
                         self.folio.amount_residual)

    def test_room_change_wizard_moves_the_guest(self):
        self.reservation.action_checkin()
        wizard = self.env['aite.hotel.room.change.wizard'].create({
            'line_id': self.reservation.line_ids.id,
            'new_room_id': self.room_102.id,
        })
        wizard.action_confirm()
        self.assertEqual(self.reservation.line_ids.room_id, self.room_102)

    def test_room_change_wizard_refuses_busy_target(self):
        other = self._make_reservation(rooms=self.room_102,
                                       checkin_offset=0, checkout_offset=2,
                                       partner=self.guest_2)
        other.action_confirm()
        wizard = self.env['aite.hotel.room.change.wizard'].create({
            'line_id': self.reservation.line_ids.id,
            'new_room_id': self.room_102.id,
        })
        with self.assertRaises(UserError):
            wizard.action_confirm()
