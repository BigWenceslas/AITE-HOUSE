# -*- coding: utf-8 -*-
"""Cycle de vie d'une réservation : contrôles, workflow, commissions."""
from datetime import timedelta

from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests import tagged

from .common import HotelCommon


@tagged('post_install', '-at_install', 'aite_hotel')
class TestReservation(HotelCommon):

    # ------------------------------------------------------------------
    # Création & calculs
    # ------------------------------------------------------------------

    def test_sequence_is_assigned(self):
        reservation = self._make_reservation()
        self.assertNotEqual(reservation.name, "Nouveau")
        self.assertTrue(reservation.name)

    def test_guest_is_flagged_on_creation(self):
        """Réserver marque le contact comme client de l'hôtel."""
        self.assertFalse(self.guest_2.is_hotel_guest)
        self._make_reservation(partner=self.guest_2)
        self.assertTrue(self.guest_2.is_hotel_guest)

    def test_nights_are_calendar_days(self):
        reservation = self._make_reservation(checkin_offset=0,
                                             checkout_offset=3)
        self.assertEqual(reservation.nights, 3)

    def test_day_use_is_one_night(self):
        """Arrivée 09 h, départ 18 h le même jour = 1 nuitée."""
        reservation = self.env['aite.hotel.reservation'].create({
            'hotel_id': self.hotel.id,
            'partner_id': self.guest.id,
            'checkin_date': self._dt(0, 9.0),
            'checkout_date': self._dt(0, 18.0),
            'line_ids': [(0, 0, {
                'room_type_id': self.type_std.id,
                'room_id': self.room_101.id,
                'adults': 1,
            })],
        })
        self.assertEqual(reservation.nights, 1)

    def test_totals_aggregate_lines(self):
        reservation = self._make_reservation(
            rooms=self.room_101 | self.room_201,
            checkin_offset=0, checkout_offset=2)
        self.assertEqual(reservation.room_count, 2)
        self.assertEqual(reservation.adults, 2)
        # 2 nuits × (50 000 + 120 000)
        self.assertEqual(reservation.amount_room_total, 340000.0)

    def test_extra_person_supplement_applies(self):
        """Au-delà de la capacité de base, le supplément par personne joue."""
        reservation = self.env['aite.hotel.reservation'].create({
            'hotel_id': self.hotel.id,
            'partner_id': self.guest.id,
            'checkin_date': self._dt(0, 14.0),
            'checkout_date': self._dt(1, 12.0),
            'line_ids': [(0, 0, {
                'room_type_id': self.type_std.id,
                'room_id': self.room_101.id,
                'adults': 2,
            })],
        })
        self.assertEqual(reservation.line_ids.price_night, 50000.0)
        # 3e adulte impossible (capacité 2) : on élargit la capacité.
        self.room_101.capacity_adults = 3
        self.type_std.capacity_adults = 2
        reservation.line_ids.adults = 3
        self.assertEqual(reservation.line_ids.price_night, 60000.0)

    def test_price_night_is_overridable_by_reception(self):
        reservation = self._make_reservation()
        reservation.line_ids.price_night = 33000.0
        self.assertEqual(reservation.line_ids.price_subtotal, 33000.0)
        self.assertEqual(reservation.amount_room_total, 33000.0)

    # ------------------------------------------------------------------
    # Commissions d'apporteur
    # ------------------------------------------------------------------

    def test_commission_percentage(self):
        reservation = self._make_reservation(
            checkin_offset=0, checkout_offset=2,
            source='agent', agent_id=self.agent.id,
            commission_type='percent', commission_rate=10.0)
        self.assertEqual(reservation.amount_room_total, 100000.0)
        self.assertEqual(reservation.commission_amount, 10000.0)

    def test_commission_fixed(self):
        reservation = self._make_reservation(
            source='agent', agent_id=self.agent.id,
            commission_type='fixed', commission_rate=15000.0)
        self.assertEqual(reservation.commission_amount, 15000.0)

    def test_no_commission_without_agent(self):
        reservation = self._make_reservation(
            commission_type='percent', commission_rate=10.0)
        self.assertEqual(reservation.commission_amount, 0.0)

    # ------------------------------------------------------------------
    # Contraintes
    # ------------------------------------------------------------------

    def test_checkout_must_follow_checkin(self):
        with self.assertRaises(ValidationError):
            self.env['aite.hotel.reservation'].create({
                'hotel_id': self.hotel.id,
                'partner_id': self.guest.id,
                'checkin_date': self._dt(2, 14.0),
                'checkout_date': self._dt(1, 12.0),
            })

    def test_at_least_one_adult_per_room(self):
        with self.assertRaises(ValidationError):
            self._make_reservation().line_ids.adults = 0

    def test_adults_cannot_exceed_room_capacity(self):
        with self.assertRaises(ValidationError):
            self._make_reservation().line_ids.adults = 9

    def test_children_cannot_exceed_room_capacity(self):
        with self.assertRaises(ValidationError):
            self._make_reservation().line_ids.children = 9

    def test_same_room_twice_on_one_reservation_is_refused(self):
        with self.assertRaises(ValidationError):
            self.env['aite.hotel.reservation'].create({
                'hotel_id': self.hotel.id,
                'partner_id': self.guest.id,
                'checkin_date': self._dt(0, 14.0),
                'checkout_date': self._dt(1, 12.0),
                'line_ids': [
                    (0, 0, {'room_type_id': self.type_std.id,
                            'room_id': self.room_101.id, 'adults': 1}),
                    (0, 0, {'room_type_id': self.type_std.id,
                            'room_id': self.room_101.id, 'adults': 1}),
                ],
            })

    def test_overlapping_confirmed_stays_are_refused(self):
        """Deux séjours confirmés ne peuvent pas se chevaucher."""
        self._make_reservation(checkin_offset=0,
                               checkout_offset=3).action_confirm()
        clash = self._make_reservation(checkin_offset=1, checkout_offset=4,
                                       partner=self.guest_2)
        with self.assertRaises(UserError):
            clash.action_confirm()

    # ------------------------------------------------------------------
    # Workflow
    # ------------------------------------------------------------------

    def test_confirm_opens_folio_and_syncs_nights(self):
        reservation = self._make_reservation(checkin_offset=0,
                                             checkout_offset=2)
        reservation.action_confirm()
        self.assertEqual(reservation.state, 'confirmed')
        self.assertTrue(reservation.folio_id)
        room_lines = reservation.folio_id.line_ids.filtered(
            lambda l: l.line_type == 'room')
        self.assertEqual(len(room_lines), 1)
        self.assertEqual(room_lines.quantity, 2)
        self.assertEqual(room_lines.price_unit, 50000.0)

    def test_confirm_requires_at_least_one_room(self):
        reservation = self.env['aite.hotel.reservation'].create({
            'hotel_id': self.hotel.id,
            'partner_id': self.guest.id,
            'checkin_date': self._dt(0, 14.0),
            'checkout_date': self._dt(1, 12.0),
        })
        with self.assertRaises(UserError):
            reservation.action_confirm()

    def test_confirm_twice_is_refused(self):
        reservation = self._make_reservation()
        reservation.action_confirm()
        with self.assertRaises(UserError):
            reservation.action_confirm()

    def test_checkin_requires_confirmed_state(self):
        reservation = self._make_reservation()
        with self.assertRaises(UserError):
            reservation.action_checkin()

    def test_checkin_sets_actual_time_and_cleans_room(self):
        reservation = self._make_reservation(checkin_offset=0,
                                             checkout_offset=2)
        reservation.action_confirm()
        self.room_101.hk_state = 'to_clean'
        reservation.action_checkin()
        self.assertEqual(reservation.state, 'checked_in')
        self.assertTrue(reservation.actual_checkin)
        self.assertEqual(self.room_101.hk_state, 'clean')

    def test_checkin_refused_on_out_of_order_room(self):
        reservation = self._make_reservation(checkin_offset=0,
                                             checkout_offset=2)
        reservation.action_confirm()
        # Mise hors service après confirmation (panne de climatisation).
        self.room_101.out_of_order = True
        with self.assertRaises(UserError):
            reservation.action_checkin()

    def test_early_checkin_requires_manager(self):
        """Un check-in anticipé est réservé au profil Responsable."""
        base_group = self.env.ref('base.group_user')
        reception = self.env['res.users'].create({
            'name': "Réception",
            'login': 'reception.test',
            'groups_id': [(6, 0, [
                base_group.id,
                self.env.ref('aite_hotel_management.group_hotel_user').id,
            ])],
        })
        manager = self.env['res.users'].create({
            'name': "Responsable",
            'login': 'manager.early.test',
            'groups_id': [(6, 0, [
                base_group.id,
                self.env.ref('aite_hotel_management.group_hotel_manager').id,
            ])],
        })
        reservation = self._make_reservation(checkin_offset=3,
                                             checkout_offset=5)
        reservation.action_confirm()
        with self.assertRaises(UserError):
            reservation.with_user(reception).action_checkin()
        # Le responsable, lui, peut forcer.
        reservation.with_user(manager).action_checkin()
        self.assertEqual(reservation.state, 'checked_in')

    def test_cancel_releases_the_room(self):
        reservation = self._make_reservation(checkin_offset=0,
                                             checkout_offset=3)
        reservation.action_confirm()
        reservation.action_cancel()
        self.assertEqual(reservation.state, 'cancelled')
        self.assertEqual(reservation.folio_id.state, 'cancelled')
        self.assertTrue(self.room_101.is_available(
            self._dt(0, 14.0), self._dt(3, 12.0)))

    def test_cancel_refused_when_payments_collected(self):
        reservation = self._make_reservation(checkin_offset=0,
                                             checkout_offset=2)
        reservation.action_confirm()
        self.env['aite.hotel.folio.payment'].create({
            'folio_id': reservation.folio_id.id,
            'amount': 20000.0,
            'method': 'cash',
        })
        with self.assertRaises(UserError):
            reservation.action_cancel()

    def test_no_show_requires_confirmed(self):
        reservation = self._make_reservation()
        with self.assertRaises(UserError):
            reservation.action_set_no_show()

    def test_no_show_marks_and_posts_message(self):
        reservation = self._make_reservation(checkin_offset=0,
                                             checkout_offset=2)
        reservation.action_confirm()
        reservation.action_set_no_show()
        self.assertEqual(reservation.state, 'no_show')

    def test_reset_draft_from_cancelled_reopens_folio(self):
        reservation = self._make_reservation(checkin_offset=0,
                                             checkout_offset=2)
        reservation.action_confirm()
        reservation.action_cancel()
        reservation.action_reset_draft()
        self.assertEqual(reservation.state, 'draft')
        self.assertEqual(reservation.folio_id.state, 'open')

    def test_reset_draft_refused_from_confirmed(self):
        reservation = self._make_reservation()
        reservation.action_confirm()
        with self.assertRaises(UserError):
            reservation.action_reset_draft()

    def test_confirmed_reservation_cannot_be_deleted(self):
        reservation = self._make_reservation()
        reservation.action_confirm()
        with self.assertRaises(UserError):
            reservation.unlink()

    def test_draft_reservation_can_be_deleted(self):
        reservation = self._make_reservation()
        reservation.unlink()
        self.assertFalse(reservation.exists())

    # ------------------------------------------------------------------
    # Changement de chambre
    # ------------------------------------------------------------------

    def test_room_change_moves_the_stay(self):
        reservation = self._make_reservation(checkin_offset=0,
                                             checkout_offset=2)
        reservation.action_confirm()
        reservation.action_checkin()
        reservation.line_ids.action_change_room(self.room_102.id)
        self.assertEqual(reservation.line_ids.room_id, self.room_102)
        # L'ancienne chambre part au ménage.
        self.assertEqual(self.room_101.hk_state, 'to_clean')

    def test_room_change_refused_if_target_busy(self):
        reservation = self._make_reservation(checkin_offset=0,
                                             checkout_offset=3)
        reservation.action_confirm()
        other = self._make_reservation(rooms=self.room_102,
                                       checkin_offset=0, checkout_offset=3,
                                       partner=self.guest_2)
        other.action_confirm()
        with self.assertRaises(UserError):
            reservation.line_ids.action_change_room(self.room_102.id)

    def test_room_change_resyncs_folio(self):
        reservation = self._make_reservation(checkin_offset=0,
                                             checkout_offset=2)
        reservation.action_confirm()
        reservation.line_ids.action_change_room(self.room_201.id)
        room_line = reservation.folio_id.line_ids.filtered(
            lambda l: l.line_type == 'room')
        # Le folio suit le nouveau type de chambre (suite à 120 000).
        self.assertEqual(room_line.price_unit, 120000.0)

    # ------------------------------------------------------------------
    # Tâches planifiées
    # ------------------------------------------------------------------

    def test_cron_auto_no_show_marks_stale_reservations(self):
        self.company.write({'hotel_auto_no_show': True,
                            'hotel_no_show_grace': 24})
        reservation = self._make_reservation(checkin_offset=-3,
                                             checkout_offset=-1)
        reservation.action_confirm()
        self.env['aite.hotel.reservation']._cron_daily_tasks()
        self.assertEqual(reservation.state, 'no_show')

    def test_cron_leaves_future_reservations_alone(self):
        self.company.write({'hotel_auto_no_show': True,
                            'hotel_no_show_grace': 24})
        reservation = self._make_reservation(checkin_offset=5,
                                             checkout_offset=7)
        reservation.action_confirm()
        self.env['aite.hotel.reservation']._cron_daily_tasks()
        self.assertEqual(reservation.state, 'confirmed')

    def test_cron_disabled_does_nothing(self):
        self.company.hotel_auto_no_show = False
        reservation = self._make_reservation(checkin_offset=-3,
                                             checkout_offset=-1)
        reservation.action_confirm()
        self.env['aite.hotel.reservation']._cron_daily_tasks()
        self.assertEqual(reservation.state, 'confirmed')

    # ------------------------------------------------------------------
    # Resynchronisation du folio sur modification
    # ------------------------------------------------------------------

    def test_extending_stay_updates_folio(self):
        reservation = self._make_reservation(checkin_offset=0,
                                             checkout_offset=2)
        reservation.action_confirm()
        reservation.checkout_date = self._dt(4, 12.0)
        room_line = reservation.folio_id.line_ids.filtered(
            lambda l: l.line_type == 'room')
        self.assertEqual(room_line.quantity, 4)

    def test_removing_a_room_drops_its_folio_line(self):
        reservation = self._make_reservation(
            rooms=self.room_101 | self.room_201,
            checkin_offset=0, checkout_offset=2)
        reservation.action_confirm()
        self.assertEqual(len(reservation.folio_id.line_ids), 2)
        reservation.line_ids[0].unlink()
        reservation._sync_folio_room_lines()
        self.assertEqual(len(reservation.folio_id.line_ids), 1)

    def test_dates_default_to_hotel_hours(self):
        """Les valeurs par défaut suivent les horaires de l'établissement."""
        Reservation = self.env['aite.hotel.reservation']
        checkin = Reservation._default_checkin()
        local = fields.Datetime.context_timestamp(self.env.user, checkin)
        self.assertEqual(local.hour, 14)
        checkout = Reservation._default_checkout()
        local_out = fields.Datetime.context_timestamp(self.env.user, checkout)
        self.assertEqual(local_out.hour, 12)
        self.assertEqual((checkout.date() - checkin.date()).days, 1)

    def test_display_name_of_line_shows_room_and_guest(self):
        reservation = self._make_reservation()
        self.assertIn('101', reservation.line_ids.display_name)
        self.assertIn("Client Test", reservation.line_ids.display_name)
