# -*- coding: utf-8 -*-
"""Tableau de bord hôtelier : occupation, ADR, RevPAR, room board."""
from datetime import timedelta

from odoo import fields
from odoo.tests import tagged

from .common import HotelCommon


@tagged('post_install', '-at_install', 'aite_hotel')
class TestHotelDashboard(HotelCommon):

    def setUp(self):
        super().setUp()
        self.Dashboard = self.env['aite.hotel.dashboard']
        self.today = fields.Date.context_today(self.env.user)
        self.d_from = fields.Date.to_string(self.today)
        self.d_to = fields.Date.to_string(self.today)

    # ------------------------------------------------------------------
    # Analyse de période
    # ------------------------------------------------------------------

    def test_parse_period_handles_garbage(self):
        """Une période illisible retombe sur le mois courant."""
        dt_from, dt_to = self.Dashboard._parse_period('pas-une-date', None)
        self.assertEqual(dt_from, self.today.replace(day=1))
        self.assertEqual(dt_to, self.today)

    def test_parse_period_reorders_inverted_dates(self):
        dt_from, dt_to = self.Dashboard._parse_period(
            fields.Date.to_string(self.today),
            fields.Date.to_string(self.today - timedelta(days=5)))
        self.assertLess(dt_from, dt_to)

    # ------------------------------------------------------------------
    # Nuitées occupées
    # ------------------------------------------------------------------

    def test_occupied_nights_counts_each_night_once(self):
        reservation = self._make_reservation(checkin_offset=0,
                                             checkout_offset=3)
        reservation.action_confirm()
        nights, per_day = self.Dashboard._occupied_room_nights(
            self.hotel, self.today, self.today + timedelta(days=5))
        self.assertEqual(nights, 3)
        self.assertEqual(per_day[self.today], 1)
        # La nuit du départ n'est pas occupée.
        self.assertEqual(per_day.get(self.today + timedelta(days=3), 0), 0)

    def test_occupied_nights_clipped_to_period(self):
        """Un séjour à cheval n'est compté que sur la fenêtre demandée."""
        reservation = self._make_reservation(checkin_offset=-2,
                                             checkout_offset=4)
        reservation.action_confirm()
        nights, _pd = self.Dashboard._occupied_room_nights(
            self.hotel, self.today, self.today + timedelta(days=1))
        self.assertEqual(nights, 2)

    def test_cancelled_stay_is_not_counted(self):
        reservation = self._make_reservation(checkin_offset=0,
                                             checkout_offset=3)
        reservation.action_confirm()
        reservation.action_cancel()
        nights, _pd = self.Dashboard._occupied_room_nights(
            self.hotel, self.today, self.today + timedelta(days=5))
        self.assertEqual(nights, 0)

    # ------------------------------------------------------------------
    # KPI
    # ------------------------------------------------------------------

    def test_kpis_structure(self):
        kpis = self.Dashboard.get_kpis(self.d_from, self.d_to,
                                       hotel_id=self.hotel.id)
        for key in ('today', 'period', 'deltas'):
            self.assertIn(key, kpis)
        for key in ('occupancy', 'adr', 'revpar', 'nights_sold',
                    'room_revenue', 'service_revenue', 'total_revenue'):
            self.assertIn(key, kpis['period'])

    def test_occupancy_rate_of_one_room_out_of_three(self):
        reservation = self._make_reservation(checkin_offset=0,
                                             checkout_offset=1)
        reservation.action_confirm()
        kpis = self.Dashboard.get_kpis(self.d_from, self.d_to,
                                       hotel_id=self.hotel.id)
        # 1 nuitée vendue sur 3 chambres × 1 jour.
        self.assertEqual(kpis['period']['nights_sold'], 1)
        self.assertAlmostEqual(kpis['period']['occupancy'], 100 / 3, places=2)

    def test_adr_and_revpar(self):
        """ADR = CA / nuitées vendues ; RevPAR = CA / chambres disponibles."""
        reservation = self._make_reservation(checkin_offset=0,
                                             checkout_offset=1)
        reservation.action_confirm()
        kpis = self.Dashboard.get_kpis(self.d_from, self.d_to,
                                       hotel_id=self.hotel.id)
        self.assertEqual(kpis['period']['room_revenue'], 50000.0)
        self.assertEqual(kpis['period']['adr'], 50000.0)
        # 3 chambres vendables × 1 jour
        self.assertAlmostEqual(kpis['period']['revpar'], 50000.0 / 3,
                               places=2)

    def test_out_of_order_room_leaves_the_denominator(self):
        self.room_201.out_of_order = True
        reservation = self._make_reservation(checkin_offset=0,
                                             checkout_offset=1)
        reservation.action_confirm()
        kpis = self.Dashboard.get_kpis(self.d_from, self.d_to,
                                       hotel_id=self.hotel.id)
        self.assertEqual(kpis['today']['total_rooms'], 2)
        self.assertAlmostEqual(kpis['period']['occupancy'], 50.0, places=2)

    def test_today_snapshot_counts_arrivals_and_departures(self):
        arriving = self._make_reservation(checkin_offset=0,
                                          checkout_offset=2)
        arriving.action_confirm()
        leaving = self._make_reservation(rooms=self.room_102,
                                         checkin_offset=-2, checkout_offset=0,
                                         partner=self.guest_2)
        leaving.action_confirm()
        leaving.action_checkin()
        kpis = self.Dashboard.get_kpis(self.d_from, self.d_to,
                                       hotel_id=self.hotel.id)
        self.assertEqual(kpis['today']['arrivals'], 1)
        self.assertEqual(kpis['today']['departures'], 1)

    def test_inhouse_guest_count(self):
        reservation = self._make_reservation(checkin_offset=0,
                                             checkout_offset=3)
        reservation.line_ids.children = 1
        reservation.action_confirm()
        reservation.action_checkin()
        kpis = self.Dashboard.get_kpis(self.d_from, self.d_to,
                                       hotel_id=self.hotel.id)
        self.assertEqual(kpis['today']['inhouse_reservations'], 1)
        self.assertEqual(kpis['today']['inhouse_guests'], 2)

    def test_service_revenue_is_separated(self):
        reservation = self._make_reservation(checkin_offset=0,
                                             checkout_offset=1)
        reservation.action_confirm()
        self.env['aite.hotel.folio.line'].create({
            'folio_id': reservation.folio_id.id,
            'line_type': 'service',
            'product_id': self.service_resto.product_id.id,
            'name': "Petit-déjeuner",
            'quantity': 2,
            'price_unit': 7500.0,
            'date': self.today,
        })
        kpis = self.Dashboard.get_kpis(self.d_from, self.d_to,
                                       hotel_id=self.hotel.id)
        self.assertEqual(kpis['period']['room_revenue'], 50000.0)
        self.assertEqual(kpis['period']['service_revenue'], 15000.0)
        self.assertEqual(kpis['period']['total_revenue'], 65000.0)

    def test_empty_period_returns_zeros_not_errors(self):
        kpis = self.Dashboard.get_kpis(
            fields.Date.to_string(self.today - timedelta(days=400)),
            fields.Date.to_string(self.today - timedelta(days=395)),
            hotel_id=self.hotel.id)
        self.assertEqual(kpis['period']['nights_sold'], 0)
        self.assertEqual(kpis['period']['adr'], 0.0)
        self.assertEqual(kpis['period']['occupancy'], 0.0)

    # ------------------------------------------------------------------
    # Room board & mouvements
    # ------------------------------------------------------------------

    def test_room_board_lists_every_room(self):
        board = self.Dashboard.get_room_board(hotel_id=self.hotel.id)
        self.assertEqual(len(board), 3)
        self.assertEqual({r['name'] for r in board}, {'101', '102', '201'})

    def test_room_board_shows_guest_when_occupied(self):
        reservation = self._make_reservation(checkin_offset=0,
                                             checkout_offset=2)
        reservation.action_confirm()
        reservation.action_checkin()
        board = self.Dashboard.get_room_board(hotel_id=self.hotel.id)
        entry = next(r for r in board if r['name'] == '101')
        self.assertEqual(entry['status'], 'occupied')
        self.assertEqual(entry['guest'], "Client Test")
        self.assertTrue(entry['until'])

    def test_today_movements_payload(self):
        arriving = self._make_reservation(checkin_offset=0,
                                          checkout_offset=2)
        arriving.action_confirm()
        movements = self.Dashboard.get_today_movements(hotel_id=self.hotel.id)
        self.assertEqual(len(movements['arrivals']), 1)
        self.assertEqual(movements['arrivals'][0]['guest'], "Client Test")
        self.assertIn('101', movements['arrivals'][0]['rooms'])

    # ------------------------------------------------------------------
    # Graphiques
    # ------------------------------------------------------------------

    def test_occupancy_evolution_has_one_point_per_day(self):
        data = self.Dashboard.get_occupancy_evolution(
            fields.Date.to_string(self.today),
            fields.Date.to_string(self.today + timedelta(days=4)),
            hotel_id=self.hotel.id)
        self.assertEqual(len(data['labels']), 5)
        self.assertEqual(len(data['values']), 5)

    def test_revenue_by_type_splits_correctly(self):
        std = self._make_reservation(checkin_offset=0, checkout_offset=1)
        std.action_confirm()
        suite = self._make_reservation(rooms=self.room_201,
                                       checkin_offset=0, checkout_offset=1,
                                       partner=self.guest_2)
        suite.action_confirm()
        data = self.Dashboard.get_revenue_by_type(
            self.d_from, self.d_to, hotel_id=self.hotel.id)
        self.assertEqual(data['labels'], ["Suite", "Standard"])
        self.assertEqual(data['values'], [120000.0, 50000.0])

    def test_housekeeping_summary(self):
        self.room_101.hk_state = 'to_clean'
        self.room_102.hk_state = 'cleaning'
        self.room_201.out_of_order = True
        summary = self.Dashboard.get_housekeeping_summary(hotel_id=self.hotel.id)
        self.assertEqual(summary['to_clean'], 1)
        self.assertEqual(summary['cleaning'], 1)
        self.assertEqual(summary['out_of_order'], 1)

    def test_meta_and_hotels_payload(self):
        meta = self.Dashboard.get_dashboard_meta()
        self.assertIn('currency_symbol', meta)
        self.assertIn('company_name', meta)
        hotels = self.Dashboard.get_hotels()
        self.assertTrue(any(h['name'] == "Hôtel de test" for h in hotels))
        self.assertTrue(all(h['color'].startswith('#') for h in hotels))
