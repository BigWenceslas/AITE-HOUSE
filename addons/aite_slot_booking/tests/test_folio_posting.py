# -*- coding: utf-8 -*-
"""Report d'une prestation sur le folio du séjour (note de séjour)."""
from datetime import timedelta

from odoo import fields
from odoo.exceptions import UserError
from odoo.tests import tagged

from .common import SlotCommon


@tagged('post_install', '-at_install', 'aite_slot')
class TestSlotFolioPosting(SlotCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.hotel = cls.env['aite.hotel.hotel'].create({
            'name': "Hôtel Créneaux",
            'code': 'HSL',
            'company_id': cls.company.id,
        })
        cls.rtype = cls.env['aite.hotel.room.type'].create({
            'name': "Chambre Créneaux",
            'company_id': cls.company.id,
            'base_price': 60000.0,
            'capacity_adults': 2,
        })
        cls.rtype.product_id.sudo().write({'taxes_id': [(5, 0, 0)]})
        cls.room = cls.env['aite.hotel.room'].create({
            'name': 'SL1',
            'hotel_id': cls.hotel.id,
            'room_type_id': cls.rtype.id,
        })

    def _open_folio(self, partner=None):
        partner = partner or self.client
        Res = self.env['aite.hotel.reservation']
        today = fields.Date.context_today(self.env.user)
        reservation = Res.create({
            'hotel_id': self.hotel.id,
            'partner_id': partner.id,
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

    # ------------------------------------------------------------------
    # Contrat de ligne (fonction pure)
    # ------------------------------------------------------------------

    def test_folio_line_vals_shape(self):
        Booking = self.env['aite.slot.booking']
        vals = Booking._folio_line_vals(
            1, 2, "Massage", '2026-01-01', 3, 15000.0)
        self.assertEqual(vals['line_type'], 'service')
        self.assertEqual(vals['product_id'], 2)
        self.assertEqual(vals['quantity'], 3)
        self.assertEqual(vals['price_unit'], 15000.0)

    def test_folio_line_vals_forces_positive_quantity(self):
        Booking = self.env['aite.slot.booking']
        vals = Booking._folio_line_vals(
            1, 2, "Massage", '2026-01-01', 0, 15000.0)
        self.assertEqual(vals['quantity'], 1)

    # ------------------------------------------------------------------
    # Report
    # ------------------------------------------------------------------

    def test_posting_adds_a_service_line(self):
        folio = self._open_folio()
        booking = self._booking(resource=self.cabine, start_h=10.0,
                                stop_h=11.0, service_id=self.service_spa.id)
        booking.action_confirm()
        booking.action_post_to_folio()
        self.assertTrue(booking.posted_line_id)
        line = booking.posted_line_id
        self.assertEqual(line.folio_id, folio)
        self.assertEqual(line.line_type, 'service')
        self.assertEqual(line.price_unit, 45000.0)
        self.assertIn("Massage relaxant", line.name)

    def test_posting_is_idempotent(self):
        self._open_folio()
        booking = self._booking(resource=self.cabine, start_h=10.0,
                                stop_h=11.0, service_id=self.service_spa.id)
        booking.action_confirm()
        booking.action_post_to_folio()
        with self.assertRaises(UserError):
            booking.action_post_to_folio()

    def test_silent_mode_skips_an_already_posted_booking(self):
        self._open_folio()
        booking = self._booking(resource=self.cabine, start_h=10.0,
                                stop_h=11.0, service_id=self.service_spa.id)
        booking.action_confirm()
        booking.action_post_to_folio()
        first = booking.posted_line_id
        booking.action_post_to_folio(silent=True)
        self.assertEqual(booking.posted_line_id, first)

    def test_pressing_posts_quantity_and_unit_price(self):
        self._open_folio()
        booking = self._booking(resource=self.cabine, start_h=10.0,
                                stop_h=10.5,
                                service_id=self.service_pressing.id, qty=4)
        booking.action_confirm()
        booking.action_post_to_folio()
        line = booking.posted_line_id
        self.assertEqual(line.quantity, 4)
        self.assertEqual(line.price_unit, 3000.0)
        self.assertEqual(line.price_subtotal, 12000.0)

    def test_posting_refused_without_an_open_folio(self):
        booking = self._booking(resource=self.cabine, start_h=10.0,
                                stop_h=11.0, service_id=self.service_spa.id,
                                partner=self.client_2)
        booking.action_confirm()
        with self.assertRaises(UserError):
            booking.action_post_to_folio()

    def test_posting_refused_without_a_service(self):
        """Le folio exige un article : une location nue ne peut pas partir."""
        self._open_folio()
        booking = self._booking(start_h=10.0, stop_h=12.0)
        booking.action_confirm()
        with self.assertRaises(UserError):
            booking.action_post_to_folio()

    def test_posting_refused_when_several_folios_are_open(self):
        self._open_folio()
        second_room = self.env['aite.hotel.room'].create({
            'name': 'SL2',
            'hotel_id': self.hotel.id,
            'room_type_id': self.rtype.id,
        })
        Res = self.env['aite.hotel.reservation']
        today = fields.Date.context_today(self.env.user)
        other = Res.create({
            'hotel_id': self.hotel.id,
            'partner_id': self.client.id,
            'checkin_date': Res._compose_datetime(
                today + timedelta(days=10), 14.0),
            'checkout_date': Res._compose_datetime(
                today + timedelta(days=12), 12.0),
            'line_ids': [(0, 0, {
                'room_type_id': self.rtype.id,
                'room_id': second_room.id,
                'adults': 1,
            })],
        })
        other.action_confirm()
        booking = self._booking(resource=self.cabine, start_h=10.0,
                                stop_h=11.0, service_id=self.service_spa.id)
        booking.action_confirm()
        with self.assertRaises(UserError):
            booking.action_post_to_folio()

    def test_explicit_folio_wins_over_the_search(self):
        folio = self._open_folio()
        booking = self._booking(resource=self.cabine, start_h=10.0,
                                stop_h=11.0, service_id=self.service_spa.id,
                                folio_id=folio.id)
        booking.action_confirm()
        booking.action_post_to_folio()
        self.assertEqual(booking.posted_line_id.folio_id, folio)

    # ------------------------------------------------------------------
    # Report automatique à la réalisation
    # ------------------------------------------------------------------

    def test_auto_posting_on_done(self):
        self.company.aite_slot_auto_post_folio = True
        self._open_folio()
        booking = self._booking(resource=self.cabine, start_h=10.0,
                                stop_h=11.0, service_id=self.service_spa.id)
        booking.action_confirm()
        booking.action_done()
        self.assertTrue(booking.posted_line_id)

    def test_auto_posting_disabled(self):
        self.company.aite_slot_auto_post_folio = False
        self._open_folio()
        booking = self._booking(resource=self.cabine, start_h=10.0,
                                stop_h=11.0, service_id=self.service_spa.id)
        booking.action_confirm()
        booking.action_done()
        self.assertFalse(booking.posted_line_id)

    def test_auto_posting_never_blocks_completion(self):
        """Sans folio exploitable, la prestation se clôture quand même."""
        self.company.aite_slot_auto_post_folio = True
        booking = self._booking(resource=self.cabine, start_h=10.0,
                                stop_h=11.0, service_id=self.service_spa.id,
                                partner=self.client_2)
        booking.action_confirm()
        booking.action_done()
        self.assertEqual(booking.state, 'done')
        self.assertFalse(booking.posted_line_id)

    def test_posted_amount_reaches_the_folio_total(self):
        folio = self._open_folio()
        before = folio.amount_total
        booking = self._booking(resource=self.cabine, start_h=10.0,
                                stop_h=11.0, service_id=self.service_spa.id)
        booking.action_confirm()
        booking.action_post_to_folio()
        folio.invalidate_recordset()
        self.assertEqual(folio.amount_total, before + 45000.0)
