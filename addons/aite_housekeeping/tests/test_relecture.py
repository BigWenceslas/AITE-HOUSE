# -*- coding: utf-8 -*-
"""Relecture croisée de l'intégration : heures, accords, menu.

* L'heure d'arrivée s'écrivait « 14h00 » sur le tableau des chambres et
  « 14:00 » partout ailleurs (tableau de bord Réception, réservations).
* La notification de répartition disait « 1 chambre(s) réparties entre
  1 équipière(s) » : forme « (s) » fausse même au pluriel.
* Le menu « Répartir les chambres du jour » ne doit plus être lié au
  groupe Réception, y compris sur une base livrée mise à niveau.
"""
from odoo.tests import tagged

from .test_board_ecarts import HousekeepingCommon


@tagged('post_install', '-at_install', 'aite_housekeeping')
class TestHousekeepingRelecture(HousekeepingCommon):

    def test_arrival_hour_is_written_like_everywhere_else(self):
        reservation = self._make_reservation(rooms=self.room_101,
                                             checkin_offset=0,
                                             checkout_offset=1)
        reservation.action_confirm()
        self.room_101.invalidate_recordset()
        self.assertEqual(self.room_101.occupancy_state, 'arrival')
        hint = self.room_101.arrival_hint or ''
        self.assertRegex(hint, r"Arrivée prévue \d\d:\d\d$")
        self.assertNotIn("h", hint.replace("Arrivée prévue", ""))

    def test_assign_message_agrees_in_number(self):
        wizard = self.Wizard.create({'hotel_id': self.hotel.id})
        self.assertEqual(wizard._assign_message(1, 1),
                         "1 chambre confiée à 1 équipière.")
        self.assertEqual(wizard._assign_message(3, 1),
                         "3 chambres confiées à 1 équipière.")
        self.assertEqual(wizard._assign_message(5, 2),
                         "5 chambres réparties entre 2 équipières.")
        for n, u in ((1, 1), (3, 1), (1, 2), (5, 2)):
            self.assertNotIn("(s)", wizard._assign_message(n, u))

    def test_assign_menu_is_for_the_governess_only(self):
        menu = self.env.ref('aite_housekeeping.menu_assign')
        self.assertEqual(
            menu.groups_id,
            self.env.ref('aite_housekeeping.group_hk_governess'))
