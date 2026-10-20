# -*- coding: utf-8 -*-
"""Objets trouvés : le séjour se devine depuis la chambre et la date."""
from odoo import fields
from odoo.tests import tagged

from odoo.addons.aite_hotel_management.tests.common import HotelCommon


@tagged('post_install', '-at_install', 'aite_housekeeping')
class TestLostFoundGuess(HotelCommon):

    def _guess(self, room):
        item = self.env['aite.hk.lost.found'].new({
            'name': "Téléphone", 'room_id': room.id,
            'found_date': fields.Date.context_today(self.env.user),
        })
        item._onchange_room_guess_stay()
        return item.reservation_id

    def test_stay_in_progress_is_guessed(self):
        reservation = self._make_reservation(checkin_offset=0,
                                             checkout_offset=2)
        reservation.action_confirm()
        reservation.action_checkin()
        self.assertEqual(self._guess(self.room_101), reservation)

    def test_overdue_guest_is_still_the_occupant(self):
        """Client arrivé dont le départ prévu est passé, sans check-out :
        il occupe toujours la chambre (même règle que la disponibilité)."""
        reservation = self._make_reservation(checkin_offset=-3,
                                             checkout_offset=-1)
        reservation.action_confirm()
        reservation.action_checkin()
        self.assertEqual(reservation.state, 'checked_in')
        self.assertEqual(self._guess(self.room_101), reservation)
