# -*- coding: utf-8 -*-
"""Moteur tarifaire, capacités et disponibilité des chambres."""
from datetime import timedelta

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import tagged

from .common import HotelCommon


@tagged('post_install', '-at_install', 'aite_hotel')
class TestRoomPricing(HotelCommon):

    # ------------------------------------------------------------------
    # Tarif de base et saisons
    # ------------------------------------------------------------------

    def test_night_price_falls_back_to_base(self):
        """Sans saison, le prix d'une nuit est le tarif de base du type."""
        day = fields.Date.context_today(self.env.user)
        self.assertEqual(self.type_std._get_night_price(day), 50000.0)

    def test_season_price_takes_precedence(self):
        """Un tarif saisonnier couvrant le jour prime sur le tarif de base."""
        day = fields.Date.context_today(self.env.user)
        self.env['aite.hotel.season.price'].create({
            'name': "Haute saison",
            'room_type_id': self.type_std.id,
            'date_from': day,
            'date_to': day + timedelta(days=10),
            'price': 75000.0,
        })
        self.assertEqual(self.type_std._get_night_price(day), 75000.0)

    def test_season_outside_range_is_ignored(self):
        """Une saison qui ne couvre pas la date ne s'applique pas."""
        day = fields.Date.context_today(self.env.user)
        self.env['aite.hotel.season.price'].create({
            'name': "Saison passée",
            'room_type_id': self.type_std.id,
            'date_from': day - timedelta(days=30),
            'date_to': day - timedelta(days=20),
            'price': 90000.0,
        })
        self.assertEqual(self.type_std._get_night_price(day), 50000.0)

    def test_hotel_specific_season_beats_global_season(self):
        """Le tarif rattaché à l'hôtel prime sur le tarif « tous hôtels »."""
        day = fields.Date.context_today(self.env.user)
        common_vals = {
            'room_type_id': self.type_std.id,
            'date_from': day,
            'date_to': day + timedelta(days=5),
        }
        self.env['aite.hotel.season.price'].create(
            dict(common_vals, name="Globale", price=60000.0))
        self.env['aite.hotel.season.price'].create(
            dict(common_vals, name="Hôtel", price=80000.0,
                 hotel_id=self.hotel.id))
        # Le tarif de l'hôtel gagne, même s'il est plus cher.
        self.assertEqual(
            self.type_std._get_night_price(day, hotel=self.hotel), 80000.0)
        # Sans hôtel en contexte, seul le tarif global s'applique.
        self.assertEqual(self.type_std._get_night_price(day), 60000.0)

    def test_cheapest_season_wins_among_equals(self):
        """À portée égale, le moteur retient le prix le plus bas."""
        day = fields.Date.context_today(self.env.user)
        for label, price in (("A", 70000.0), ("B", 55000.0)):
            self.env['aite.hotel.season.price'].create({
                'name': label,
                'room_type_id': self.type_std.id,
                'date_from': day,
                'date_to': day + timedelta(days=3),
                'price': price,
            })
        self.assertEqual(self.type_std._get_night_price(day), 55000.0)

    def test_stay_price_averages_across_seasons(self):
        """Le prix du séjour lisse les changements de saison."""
        day = fields.Date.context_today(self.env.user)
        # Nuit 1 en saison à 100 000, nuit 2 au tarif de base 50 000.
        self.env['aite.hotel.season.price'].create({
            'name': "Une nuit chère",
            'room_type_id': self.type_std.id,
            'date_from': day,
            'date_to': day,
            'price': 100000.0,
        })
        price, nights = self.type_std._get_stay_price(
            day, day + timedelta(days=2))
        self.assertEqual(nights, 2)
        self.assertEqual(price, 75000.0)

    def test_day_use_counts_as_one_night(self):
        """Arrivée et départ le même jour = une nuitée facturée."""
        day = fields.Date.context_today(self.env.user)
        price, nights = self.type_std._get_stay_price(day, day)
        self.assertEqual(nights, 1)
        self.assertEqual(price, 50000.0)

    # ------------------------------------------------------------------
    # Surcharge au niveau de la chambre
    # ------------------------------------------------------------------

    def test_room_price_override_beats_everything(self):
        """La surcharge de la chambre prime sur le type ET sur la saison."""
        day = fields.Date.context_today(self.env.user)
        self.env['aite.hotel.season.price'].create({
            'name': "Saison",
            'room_type_id': self.type_std.id,
            'date_from': day,
            'date_to': day + timedelta(days=5),
            'price': 90000.0,
        })
        self.room_101.price_override = 65000.0
        self.assertEqual(self.room_101._get_night_price(day), 65000.0)
        price, nights = self.room_101._get_stay_price(
            day, day + timedelta(days=3))
        self.assertEqual((price, nights), (65000.0, 3))

    def test_effective_price_reflects_override(self):
        """Le « tarif du jour » affiché suit la surcharge."""
        self.assertEqual(self.room_101.effective_price, 50000.0)
        self.room_101.price_override = 42000.0
        self.room_101.invalidate_recordset(['effective_price'])
        self.assertEqual(self.room_101.effective_price, 42000.0)

    # ------------------------------------------------------------------
    # Article lié au type de chambre
    # ------------------------------------------------------------------

    def test_room_type_creates_linked_product(self):
        """Chaque type de chambre reçoit son article de service."""
        self.assertTrue(self.type_std.product_id)
        self.assertEqual(self.type_std.product_id.type, 'service')
        self.assertEqual(self.type_std.product_id.list_price, 50000.0)

    def test_room_type_rename_syncs_product(self):
        """Renommer / retarifer le type met l'article à jour."""
        self.type_std.write({'name': "Standard rénovée",
                             'base_price': 58000.0})
        self.assertIn("Standard rénovée", self.type_std.product_id.name)
        self.assertEqual(self.type_std.product_id.list_price, 58000.0)

    def test_service_creates_linked_product(self):
        """Idem pour les services hôteliers."""
        self.assertTrue(self.service_resto.product_id)
        self.assertEqual(self.service_resto.product_id.list_price, 7500.0)

    def test_service_price_cannot_be_negative(self):
        with self.assertRaises(ValidationError):
            self.env['aite.hotel.service'].create({
                'name': "Service absurde",
                'category': 'other',
                'price': -1.0,
            })

    def test_season_price_must_be_positive(self):
        day = fields.Date.context_today(self.env.user)
        with self.assertRaises(ValidationError):
            self.env['aite.hotel.season.price'].create({
                'name': "Gratuit",
                'room_type_id': self.type_std.id,
                'date_from': day,
                'date_to': day,
                'price': 0.0,
            })

    def test_season_dates_must_be_ordered(self):
        day = fields.Date.context_today(self.env.user)
        with self.assertRaises(ValidationError):
            self.env['aite.hotel.season.price'].create({
                'name': "À l'envers",
                'room_type_id': self.type_std.id,
                'date_from': day,
                'date_to': day - timedelta(days=1),
                'price': 1000.0,
            })

    # ------------------------------------------------------------------
    # Capacités
    # ------------------------------------------------------------------

    def test_room_inherits_type_capacity(self):
        self.assertEqual(self.room_101.capacity_adults, 2)
        self.assertEqual(self.room_101.capacity_children, 1)
        self.assertEqual(self.room_201.capacity_adults, 3)

    def test_room_capacity_must_be_positive(self):
        with self.assertRaises(ValidationError):
            self.room_101.capacity_adults = 0

    def test_room_number_is_unique_per_hotel(self):
        """Deux chambres ne peuvent pas porter le même numéro dans un hôtel."""
        with self.assertRaises(Exception):
            with self.env.cr.savepoint():
                self.env['aite.hotel.room'].create({
                    'name': '101',
                    'hotel_id': self.hotel.id,
                    'room_type_id': self.type_std.id,
                })

    # ------------------------------------------------------------------
    # Disponibilité
    # ------------------------------------------------------------------

    def test_free_room_is_available(self):
        self.assertTrue(self.room_101.is_available(
            self._dt(0, 14.0), self._dt(1, 12.0)))

    def test_out_of_order_room_is_never_available(self):
        self.room_101.out_of_order = True
        self.assertFalse(self.room_101.is_available(
            self._dt(0, 14.0), self._dt(1, 12.0)))

    def test_archived_room_is_never_available(self):
        self.room_101.active = False
        self.assertFalse(self.room_101.is_available(
            self._dt(0, 14.0), self._dt(1, 12.0)))

    def test_confirmed_stay_blocks_the_room(self):
        self._make_reservation(checkin_offset=0,
                               checkout_offset=2).action_confirm()
        self.assertFalse(self.room_101.is_available(
            self._dt(1, 14.0), self._dt(3, 12.0)))

    def test_checkout_frees_the_room_same_day(self):
        """Départ 12 h / arrivée 14 h le même jour : pas de conflit."""
        self._make_reservation(checkin_offset=0,
                               checkout_offset=1).action_confirm()
        # Nouvelle arrivée le jour du départ, après l'heure de départ.
        self.assertTrue(self.room_101.is_available(
            self._dt(1, 14.0), self._dt(2, 12.0)))

    def test_draft_reservation_does_not_block(self):
        """Une réservation non confirmée ne verrouille rien."""
        self._make_reservation(checkin_offset=0, checkout_offset=2)
        self.assertTrue(self.room_101.is_available(
            self._dt(0, 14.0), self._dt(2, 12.0)))

    def test_ignore_line_excludes_itself(self):
        """Une ligne ne se bloque pas elle-même (re-validation d'un séjour)."""
        reservation = self._make_reservation(checkin_offset=0,
                                             checkout_offset=2)
        reservation.action_confirm()
        line = reservation.line_ids
        self.assertTrue(self.room_101.is_available(
            self._dt(0, 14.0), self._dt(2, 12.0), ignore_line=line))

    # ------------------------------------------------------------------
    # États opérationnels de la chambre
    # ------------------------------------------------------------------

    def test_status_priority_out_of_order_wins(self):
        self.room_101.hk_state = 'to_clean'
        self.room_101.out_of_order = True
        self.room_101.invalidate_recordset(['status', 'occupancy_state'])
        self.assertEqual(self.room_101.status, 'out_of_order')

    def test_status_cleaning_when_dirty_and_free(self):
        self.room_101.hk_state = 'to_clean'
        self.room_101.invalidate_recordset(['status', 'occupancy_state'])
        self.assertEqual(self.room_101.status, 'cleaning')

    def test_status_free_when_clean_and_empty(self):
        self.room_101.hk_state = 'clean'
        self.room_101.invalidate_recordset(['status', 'occupancy_state'])
        self.assertEqual(self.room_101.status, 'free')

    def test_status_occupied_beats_dirty(self):
        reservation = self._make_reservation(checkin_offset=0,
                                             checkout_offset=2)
        reservation.action_confirm()
        reservation.action_checkin()
        self.room_101.hk_state = 'to_clean'
        self.room_101.invalidate_recordset(
            ['status', 'occupancy_state', 'current_line_id'])
        self.assertEqual(self.room_101.status, 'occupied')
        self.assertEqual(self.room_101.current_line_id,
                         reservation.line_ids)

    def test_cannot_put_occupied_room_out_of_order(self):
        reservation = self._make_reservation(checkin_offset=0,
                                             checkout_offset=2)
        reservation.action_confirm()
        reservation.action_checkin()
        self.room_101.invalidate_recordset(['occupancy_state'])
        with self.assertRaises(Exception):
            self.room_101.action_toggle_out_of_order()

    def test_toggle_out_of_order_clears_reason(self):
        self.room_101.write({'out_of_order': True,
                             'out_of_order_reason': "Travaux"})
        self.room_101.action_toggle_out_of_order()
        self.assertFalse(self.room_101.out_of_order)
        self.assertFalse(self.room_101.out_of_order_reason)

    def test_hotel_sellable_room_count_excludes_out_of_order(self):
        self.assertEqual(self.hotel.room_count, 3)
        self.room_101.out_of_order = True
        self.hotel.invalidate_recordset(['sellable_room_count'])
        self.assertEqual(self.hotel.sellable_room_count, 2)

    def test_hotel_hours_are_validated(self):
        with self.assertRaises(ValidationError):
            self.hotel.checkin_hour = 25.0
