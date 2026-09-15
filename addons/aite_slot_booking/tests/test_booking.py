# -*- coding: utf-8 -*-
"""Réservation de créneau : tarif, alignement, conflits, workflow."""
from odoo.exceptions import UserError, ValidationError
from odoo.tests import tagged

from .common import SlotCommon


@tagged('post_install', '-at_install', 'aite_slot')
class TestSlotBooking(SlotCommon):

    # ------------------------------------------------------------------
    # Tarification (fonction pure)
    # ------------------------------------------------------------------

    def test_manual_price_wins(self):
        Booking = self.env['aite.slot.booking']
        self.assertEqual(
            Booking._slot_price(45000.0, 2, 3.0, 25000.0, 99000.0), 99000.0)

    def test_service_price_times_quantity(self):
        Booking = self.env['aite.slot.booking']
        self.assertEqual(
            Booking._slot_price(3000.0, 4, 1.0, 25000.0, 0.0), 12000.0)

    def test_zero_quantity_counts_as_one(self):
        Booking = self.env['aite.slot.booking']
        self.assertEqual(
            Booking._slot_price(3000.0, 0, 1.0, 0.0, 0.0), 3000.0)

    def test_hourly_rate_when_no_service(self):
        Booking = self.env['aite.slot.booking']
        self.assertEqual(
            Booking._slot_price(0.0, 1, 3.0, 25000.0, 0.0), 75000.0)

    def test_price_is_zero_without_anything(self):
        Booking = self.env['aite.slot.booking']
        self.assertEqual(Booking._slot_price(0.0, 1, 0.0, 0.0, 0.0), 0.0)

    def test_space_booking_uses_the_hourly_rate(self):
        booking = self._booking(start_h=10.0, stop_h=13.0)
        self.assertEqual(booking.duration_hours, 3.0)
        self.assertEqual(booking.amount, 75000.0)

    def test_service_booking_uses_the_catalogue_price(self):
        booking = self._booking(resource=self.cabine, start_h=10.0,
                                stop_h=11.0, service_id=self.service_spa.id)
        self.assertEqual(booking.amount, 45000.0)

    def test_pressing_multiplies_by_quantity(self):
        booking = self._booking(resource=self.cabine, start_h=10.0,
                                stop_h=10.5,
                                service_id=self.service_pressing.id, qty=5)
        self.assertEqual(booking.amount, 15000.0)

    def test_manual_price_overrides_the_engine(self):
        booking = self._booking(start_h=10.0, stop_h=13.0,
                                amount_manual=50000.0)
        self.assertEqual(booking.amount, 50000.0)

    # ------------------------------------------------------------------
    # Alignement (fonction pure)
    # ------------------------------------------------------------------

    def test_alignment_ok(self):
        Booking = self.env['aite.slot.booking']
        self.assertEqual(
            Booking._check_alignment(10.0, 11.0, 9.0, 22.0, 60), '')

    def test_alignment_detects_inverted_order(self):
        Booking = self.env['aite.slot.booking']
        self.assertEqual(
            Booking._check_alignment(11.0, 10.0, 9.0, 22.0, 60), 'order')

    def test_alignment_detects_zero_length(self):
        Booking = self.env['aite.slot.booking']
        self.assertEqual(
            Booking._check_alignment(10.0, 10.0, 9.0, 22.0, 60), 'order')

    def test_alignment_detects_before_opening(self):
        Booking = self.env['aite.slot.booking']
        self.assertEqual(
            Booking._check_alignment(8.0, 9.0, 9.0, 22.0, 60), 'hours')

    def test_alignment_detects_after_closing(self):
        Booking = self.env['aite.slot.booking']
        self.assertEqual(
            Booking._check_alignment(21.0, 23.0, 9.0, 22.0, 60), 'hours')

    def test_alignment_detects_off_grid(self):
        Booking = self.env['aite.slot.booking']
        self.assertEqual(
            Booking._check_alignment(10.25, 11.25, 9.0, 22.0, 60), 'grid')

    def test_half_hour_grid_accepts_half_hours(self):
        Booking = self.env['aite.slot.booking']
        self.assertEqual(
            Booking._check_alignment(10.5, 11.5, 10.0, 18.0, 30), '')

    # ------------------------------------------------------------------
    # Contraintes appliquées à l'enregistrement
    # ------------------------------------------------------------------

    def test_booking_outside_opening_hours_is_refused(self):
        with self.assertRaises(ValidationError):
            self._booking(start_h=7.0, stop_h=8.0)

    def test_booking_off_grid_is_refused(self):
        with self.assertRaises(ValidationError):
            self._booking(start_h=10.25, stop_h=11.25)

    def test_booking_across_midnight_is_refused(self):
        from datetime import timedelta
        with self.assertRaises(ValidationError):
            self.env['aite.slot.booking'].create({
                'resource_id': self.salon.id,
                'partner_id': self.client.id,
                'company_id': self.company.id,
                'start': self._at(1, 21.0),
                'stop': self._at(1, 21.0) + timedelta(hours=4),
            })

    def test_conflict_refused_at_capacity_one(self):
        self._booking(start_h=10.0, stop_h=12.0).action_confirm()
        clash = self._booking(start_h=11.0, stop_h=13.0,
                              partner=self.client_2)
        with self.assertRaises(ValidationError):
            clash.action_confirm()

    def test_second_booking_fits_within_capacity_two(self):
        first = self._booking(resource=self.cabine, start_h=10.0,
                              stop_h=11.0)
        first.action_confirm()
        second = self._booking(resource=self.cabine, start_h=10.0,
                               stop_h=11.0, partner=self.client_2)
        second.action_confirm()
        self.assertEqual(second.state, 'confirmed')

    def test_third_booking_exceeds_capacity_two(self):
        for partner in (self.client, self.client_2):
            self._booking(resource=self.cabine, start_h=10.0, stop_h=11.0,
                          partner=partner).action_confirm()
        third_partner = self.env['res.partner'].create({'name': "Troisième"})
        third = self._booking(resource=self.cabine, start_h=10.0,
                              stop_h=11.0, partner=third_partner)
        with self.assertRaises(ValidationError):
            third.action_confirm()

    def test_draft_booking_does_not_block(self):
        self._booking(start_h=10.0, stop_h=12.0)
        other = self._booking(start_h=10.0, stop_h=12.0,
                              partner=self.client_2)
        other.action_confirm()
        self.assertEqual(other.state, 'confirmed')

    def test_back_to_back_bookings_are_allowed(self):
        self._booking(start_h=10.0, stop_h=11.0).action_confirm()
        following = self._booking(start_h=11.0, stop_h=12.0,
                                  partner=self.client_2)
        following.action_confirm()
        self.assertEqual(following.state, 'confirmed')

    # ------------------------------------------------------------------
    # Workflow
    # ------------------------------------------------------------------

    def test_sequence_is_assigned(self):
        booking = self._booking()
        self.assertNotEqual(booking.name, "Nouveau")

    def test_confirm_then_done(self):
        booking = self._booking()
        booking.action_confirm()
        self.assertEqual(booking.state, 'confirmed')
        booking.action_done()
        self.assertEqual(booking.state, 'done')

    def test_done_requires_confirmed(self):
        booking = self._booking()
        with self.assertRaises(UserError):
            booking.action_done()

    def test_done_booking_cannot_be_cancelled(self):
        booking = self._booking()
        booking.action_confirm()
        booking.action_done()
        with self.assertRaises(UserError):
            booking.action_cancel()

    def test_no_show_requires_confirmed(self):
        booking = self._booking()
        with self.assertRaises(UserError):
            booking.action_no_show()

    def test_no_show_then_reset_to_draft(self):
        booking = self._booking()
        booking.action_confirm()
        booking.action_no_show()
        self.assertEqual(booking.state, 'no_show')
        booking.action_reset_draft()
        self.assertEqual(booking.state, 'draft')

    def test_pickup_flag(self):
        booking = self._booking(resource=self.cabine, start_h=10.0,
                                stop_h=10.5,
                                service_id=self.service_pressing.id)
        self.assertFalse(booking.pickup_done)
        booking.action_mark_picked_up()
        self.assertTrue(booking.pickup_done)

    def test_kind_follows_the_resource(self):
        booking = self._booking(resource=self.cabine, start_h=10.0,
                                stop_h=11.0)
        self.assertEqual(booking.kind, 'spa')

    # ------------------------------------------------------------------
    # Cron no-show
    # ------------------------------------------------------------------

    def test_cron_marks_stale_confirmed_bookings(self):
        self.company.aite_slot_no_show_hours = 6
        booking = self._booking(days=-2, start_h=10.0, stop_h=11.0)
        booking.action_confirm()
        self.env['aite.slot.booking']._cron_slot_no_show()
        self.assertEqual(booking.state, 'no_show')

    def test_cron_leaves_future_bookings_alone(self):
        self.company.aite_slot_no_show_hours = 6
        booking = self._booking(days=3, start_h=10.0, stop_h=11.0)
        booking.action_confirm()
        self.env['aite.slot.booking']._cron_slot_no_show()
        self.assertEqual(booking.state, 'confirmed')

    def test_cron_leaves_completed_bookings_alone(self):
        booking = self._booking(days=-2, start_h=10.0, stop_h=11.0)
        booking.action_confirm()
        booking.action_done()
        self.env['aite.slot.booking']._cron_slot_no_show()
        self.assertEqual(booking.state, 'done')
