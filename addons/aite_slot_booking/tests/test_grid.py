# -*- coding: utf-8 -*-
"""Grille de disponibilité — source de vérité du planning et du site web."""
from odoo import fields
from odoo.tests import tagged

from .common import SlotCommon


@tagged('post_install', '-at_install', 'aite_slot')
class TestSlotGrid(SlotCommon):

    def setUp(self):
        super().setUp()
        self.Resource = self.env['aite.booking.resource']

    # ------------------------------------------------------------------
    # Chevauchements (fonction pure)
    # ------------------------------------------------------------------

    def test_no_overlap_when_intervals_touch(self):
        """Fin == début : les créneaux se suivent, ils ne se croisent pas."""
        self.assertEqual(
            self.Resource._overlap_count([(9.0, 10.0)], 10.0, 11.0), 0)

    def test_overlap_counted_once_per_interval(self):
        busy = [(9.0, 11.0), (10.0, 12.0), (14.0, 15.0)]
        self.assertEqual(
            self.Resource._overlap_count(busy, 10.5, 11.5), 2)

    def test_containment_counts_as_overlap(self):
        self.assertEqual(
            self.Resource._overlap_count([(9.0, 18.0)], 10.0, 11.0), 1)

    def test_empty_busy_list(self):
        self.assertEqual(self.Resource._overlap_count([], 9.0, 10.0), 0)

    # ------------------------------------------------------------------
    # Construction de la grille (fonction pure)
    # ------------------------------------------------------------------

    def test_hourly_grid_covers_opening_hours(self):
        slots = self.Resource._build_day_slots(9.0, 12.0, 60, [], 1)
        self.assertEqual([s['label'] for s in slots],
                         ['09:00', '10:00', '11:00'])
        self.assertTrue(all(s['state'] == 'free' for s in slots))

    def test_half_hour_grid(self):
        slots = self.Resource._build_day_slots(10.0, 12.0, 30, [], 1)
        self.assertEqual([s['label'] for s in slots],
                         ['10:00', '10:30', '11:00', '11:30'])

    def test_partial_slot_is_not_emitted(self):
        """Un créneau qui déborderait de la fermeture n'est pas proposé."""
        slots = self.Resource._build_day_slots(9.0, 11.5, 60, [], 1)
        self.assertEqual([s['label'] for s in slots], ['09:00', '10:00'])

    def test_busy_slot_is_full_at_capacity_one(self):
        slots = self.Resource._build_day_slots(
            9.0, 12.0, 60, [(10.0, 11.0)], 1)
        by_label = {s['label']: s for s in slots}
        self.assertEqual(by_label['09:00']['state'], 'free')
        self.assertEqual(by_label['10:00']['state'], 'full')
        self.assertEqual(by_label['10:00']['used'], 1)
        self.assertEqual(by_label['11:00']['state'], 'free')

    def test_partial_state_below_capacity(self):
        slots = self.Resource._build_day_slots(
            9.0, 12.0, 60, [(10.0, 11.0)], 2)
        by_label = {s['label']: s for s in slots}
        self.assertEqual(by_label['10:00']['state'], 'partial')
        self.assertEqual(by_label['10:00']['used'], 1)

    def test_full_when_capacity_reached(self):
        slots = self.Resource._build_day_slots(
            9.0, 12.0, 60, [(10.0, 11.0), (10.0, 11.0)], 2)
        by_label = {s['label']: s for s in slots}
        self.assertEqual(by_label['10:00']['state'], 'full')
        self.assertEqual(by_label['10:00']['used'], 2)

    def test_zero_capacity_is_always_full(self):
        slots = self.Resource._build_day_slots(9.0, 11.0, 60, [], 0)
        self.assertTrue(all(s['state'] == 'full' for s in slots))

    def test_half_hour_labels_are_formatted(self):
        slots = self.Resource._build_day_slots(9.5, 11.0, 30, [], 1)
        self.assertEqual([s['label'] for s in slots],
                         ['09:30', '10:00', '10:30'])

    # ------------------------------------------------------------------
    # API exposée au planning et au site web
    # ------------------------------------------------------------------

    def test_day_grid_payload_shape(self):
        day = fields.Date.to_string(
            fields.Date.context_today(self.env.user))
        grid = self.Resource.get_day_grid(self.salon.id, day)
        self.assertEqual(grid['resource']['name'], "Salon VIP")
        self.assertEqual(grid['resource']['capacity'], 1)
        self.assertEqual(grid['resource']['slot_minutes'], 60)
        self.assertEqual(len(grid['slots']), 13)  # 9 h → 22 h
        self.assertEqual(grid['bookings'], [])

    def test_day_grid_marks_confirmed_bookings(self):
        booking = self._booking(start_h=10.0, stop_h=12.0, days=0)
        booking.action_confirm()
        day = fields.Date.to_string(
            fields.Date.context_today(self.env.user))
        grid = self.Resource.get_day_grid(self.salon.id, day)
        by_label = {s['label']: s for s in grid['slots']}
        self.assertEqual(by_label['10:00']['state'], 'full')
        self.assertEqual(by_label['11:00']['state'], 'full')
        self.assertEqual(by_label['12:00']['state'], 'free')
        self.assertEqual(len(grid['bookings']), 1)
        self.assertEqual(grid['bookings'][0]['partner'], "Client Créneau")

    def test_day_grid_ignores_draft_bookings(self):
        self._booking(start_h=10.0, stop_h=12.0, days=0)
        day = fields.Date.to_string(
            fields.Date.context_today(self.env.user))
        grid = self.Resource.get_day_grid(self.salon.id, day)
        self.assertTrue(all(s['state'] == 'free' for s in grid['slots']))

    def test_day_grid_ignores_cancelled_bookings(self):
        booking = self._booking(start_h=10.0, stop_h=12.0, days=0)
        booking.action_confirm()
        booking.action_cancel()
        day = fields.Date.to_string(
            fields.Date.context_today(self.env.user))
        grid = self.Resource.get_day_grid(self.salon.id, day)
        self.assertTrue(all(s['state'] == 'free' for s in grid['slots']))

    def test_day_grid_of_another_day_is_free(self):
        booking = self._booking(start_h=10.0, stop_h=12.0, days=0)
        booking.action_confirm()
        tomorrow = fields.Date.to_string(
            fields.Date.context_today(self.env.user)
            + __import__('datetime').timedelta(days=1))
        grid = self.Resource.get_day_grid(self.salon.id, tomorrow)
        self.assertTrue(all(s['state'] == 'free' for s in grid['slots']))

    def test_day_grid_falls_back_on_a_bad_date(self):
        grid = self.Resource.get_day_grid(self.salon.id, 'pas-une-date')
        self.assertTrue(grid['slots'])

    # ------------------------------------------------------------------
    # Contraintes SQL de la ressource
    # ------------------------------------------------------------------

    def test_capacity_must_be_positive(self):
        with self.assertRaises(Exception):
            with self.env.cr.savepoint():
                self.env['aite.booking.resource'].create({
                    'name': "Ressource absurde",
                    'kind': 'other',
                    'capacity': 0,
                })

    def test_closing_must_follow_opening(self):
        with self.assertRaises(Exception):
            with self.env.cr.savepoint():
                self.env['aite.booking.resource'].create({
                    'name': "Horaires inversés",
                    'kind': 'other',
                    'open_hour': 18.0,
                    'close_hour': 9.0,
                })
