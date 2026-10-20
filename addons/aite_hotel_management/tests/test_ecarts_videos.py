# -*- coding: utf-8 -*-
"""Écarts relevés en tournant les tutoriels vidéo (docs/videos/ECARTS.md).

Chaque classe reproduit un écart avant sa correction :

* n° 12 — profil Gouvernante seul : l'icône « Hôtel » doit ouvrir un
  écran qu'elle a le droit de lire (et non le Front Desk de la
  réception) ;
* n° 31 — le prix conservé par un surclassement gracieux doit survivre
  à une prolongation du séjour ;
* n° 32 — un séjour « Arrivé » dont le départ prévu est dépassé bloque
  toujours sa chambre, et la confirmation verrouille les chambres ;
* n° 33 — une ligne de réservation confirmée ne se supprime pas depuis
  le planning.
"""
from lxml import etree

from odoo.exceptions import UserError
from odoo.tests import tagged

from .common import HotelCommon


def _user(env, login, group_xmlid):
    return env['res.users'].create({
        'name': login,
        'login': login,
        'groups_id': [(6, 0, [
            env.ref('base.group_user').id, env.ref(group_xmlid).id,
        ])],
    })


@tagged('post_install', '-at_install', 'aite_hotel')
class TestHomeActionByProfile(HotelCommon):
    """Écart n° 12 : ce qu'ouvre l'icône « Hôtel » selon le profil."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.housekeeper = _user(
            cls.env, 'gouvernante.ecart12',
            'aite_hotel_management.group_hotel_housekeeping')
        cls.receptionist = _user(
            cls.env, 'reception.ecart12',
            'aite_hotel_management.group_hotel_user')

    def _open_hotel_app(self, user):
        """Rejoue le clic sur l'icône : action du menu racine, exécutée
        comme le ferait le client web pour ``user``."""
        self.env.invalidate_all()
        menu = self.env.ref('aite_hotel_management.menu_hotel_root')
        action = menu.action
        if action._name == 'ir.actions.server':
            return action.with_user(user).run()
        return action.with_user(user)._get_action_dict()

    def _render(self, user, action):
        """Charge ce que l'écran ouvert lit au premier affichage."""
        self.env.invalidate_all()
        if action.get('tag') == 'aite_hotel_dashboard':
            dashboard = self.env['aite.hotel.dashboard'].with_user(user)
            dashboard.get_dashboard_meta()
            dashboard.get_hotels()
            dashboard.get_kpis('2026-01-01', '2026-01-31')
            dashboard.get_room_board()
            dashboard.get_today_movements()
            dashboard.get_housekeeping_summary()
        else:
            self.assertEqual(action.get('type'), 'ir.actions.act_window')
            self.env[action['res_model']].with_user(user).search([])

    def test_housekeeper_opens_hotel_app_without_access_error(self):
        action = self._open_hotel_app(self.housekeeper)
        self.assertTrue(action, "L'icône Hôtel doit ouvrir un écran.")
        # Ne lève pas d'AccessError (folio.line réservé à la Réception).
        self._render(self.housekeeper, action)
        self.assertNotEqual(action.get('tag'), 'aite_hotel_dashboard')

    def test_receptionist_still_lands_on_front_desk(self):
        action = self._open_hotel_app(self.receptionist)
        self.assertEqual(action.get('tag'), 'aite_hotel_dashboard')
        self._render(self.receptionist, action)


@tagged('post_install', '-at_install', 'aite_hotel')
class TestKeptPriceOnExtension(HotelCommon):
    """Écart n° 31 : surclassement gracieux puis prolongation."""

    def test_graceful_upgrade_price_survives_extension(self):
        reservation = self._make_reservation(checkin_offset=0,
                                             checkout_offset=2)
        reservation.action_confirm()
        line = reservation.line_ids
        self.assertEqual(line.price_night, 50000.0)
        self.env['aite.hotel.room.change.wizard'].create({
            'line_id': line.id,
            'new_room_id': self.room_201.id,
            'keep_price': True,
        }).action_confirm()
        self.assertEqual(line.room_id, self.room_201)
        self.assertEqual(line.price_night, 50000.0)

        # Le client prolonge de deux nuits.
        self.env.invalidate_all()
        reservation.checkout_date = self._dt(4, 12.0)
        self.assertEqual(line.price_night, 50000.0,
                         "Le tarif accordé au client doit être conservé.")
        room_line = reservation.folio_id.line_ids.filtered(
            lambda l: l.line_type == 'room')
        self.assertEqual(room_line.quantity, 4)
        self.assertEqual(room_line.price_unit, 50000.0)

    def test_unlocking_restores_the_tariff(self):
        reservation = self._make_reservation(checkin_offset=0,
                                             checkout_offset=2)
        reservation.action_confirm()
        line = reservation.line_ids
        self.env['aite.hotel.room.change.wizard'].create({
            'line_id': line.id,
            'new_room_id': self.room_201.id,
            'keep_price': True,
        }).action_confirm()
        line.price_locked = False
        self.assertEqual(line.price_night, 120000.0)

    def test_change_without_keep_price_applies_new_tariff(self):
        reservation = self._make_reservation(checkin_offset=0,
                                             checkout_offset=2)
        reservation.action_confirm()
        line = reservation.line_ids
        self.env['aite.hotel.room.change.wizard'].create({
            'line_id': line.id,
            'new_room_id': self.room_201.id,
        }).action_confirm()
        self.assertFalse(line.price_locked)
        reservation.checkout_date = self._dt(4, 12.0)
        self.assertEqual(line.price_night, 120000.0)


@tagged('post_install', '-at_install', 'aite_hotel')
class TestDoubleSale(HotelCommon):
    """Écart n° 32 (partie hôtel) : double vente d'une chambre."""

    def _overdue_stay(self):
        """Client arrivé il y a trois jours, départ prévu hier, toujours
        là (check-out pas encore fait)."""
        stay = self._make_reservation(checkin_offset=-3, checkout_offset=-1)
        stay.action_confirm()
        stay.action_checkin()
        self.assertEqual(stay.state, 'checked_in')
        return stay

    def test_overdue_checked_in_stay_still_blocks_its_room(self):
        self._overdue_stay()
        self.assertFalse(self.room_101.is_available(
            self._dt(0, 14.0), self._dt(1, 12.0)))
        walk_in = self._make_reservation(checkin_offset=0, checkout_offset=1,
                                         partner=self.guest_2)
        with self.assertRaises(UserError):
            walk_in.action_confirm()

    def test_room_is_released_by_the_real_checkout(self):
        stay = self._overdue_stay()
        self.env['aite.hotel.checkout.wizard'].create({
            'reservation_id': stay.id,
            'create_invoice': False,
        }).action_confirm()
        self.assertTrue(self.room_101.is_available(
            self._dt(0, 14.0), self._dt(1, 12.0)))

    def test_on_time_stay_does_not_block_after_departure(self):
        """Un séjour arrivé dont le départ est demain ne bloque pas la
        semaine suivante (seul le dépassement prolonge le blocage)."""
        stay = self._make_reservation(checkin_offset=0, checkout_offset=1)
        stay.action_confirm()
        stay.action_checkin()
        self.assertTrue(self.room_101.is_available(
            self._dt(7, 14.0), self._dt(8, 12.0)))

    def _room_xmin(self, room):
        self.env.flush_all()
        self.env.cr.execute(
            "SELECT xmin::text FROM aite_hotel_room WHERE id = %s",
            [room.id])
        return self.env.cr.fetchone()[0]

    def test_confirmation_locks_the_rooms(self):
        """La confirmation réécrit la ligne SQL de la chambre : une
        seconde confirmation concurrente sur la même chambre se heurte
        au verrou puis à l'erreur de sérialisation, et Odoo la rejoue
        avec des données fraîches (où elle voit la première)."""
        reservation = self._make_reservation(rooms=self.room_102)
        before = self._room_xmin(self.room_102)
        untouched = self._room_xmin(self.room_201)
        reservation.action_confirm()
        self.assertNotEqual(self._room_xmin(self.room_102), before)
        self.assertEqual(self._room_xmin(self.room_201), untouched)


@tagged('post_install', '-at_install', 'aite_hotel')
class TestPlanningDeletion(HotelCommon):
    """Écart n° 33 : suppression depuis la fenêtre du planning."""

    def test_planning_calendar_offers_no_delete(self):
        view = self.env.ref(
            'aite_hotel_management.view_hotel_reservation_line_calendar')
        arch = etree.fromstring(view.arch)
        self.assertIn(arch.get('delete'), ('0', 'false', 'False'))

    def test_confirmed_line_cannot_be_deleted(self):
        reservation = self._make_reservation(
            rooms=self.room_101 | self.room_102)
        reservation.action_confirm()
        with self.assertRaises(UserError):
            reservation.line_ids[0].unlink()
        self.assertEqual(len(reservation.line_ids), 2)

    def test_checked_in_line_cannot_be_deleted(self):
        reservation = self._make_reservation()
        reservation.action_confirm()
        reservation.action_checkin()
        with self.assertRaises(UserError):
            reservation.line_ids.unlink()

    def test_draft_line_can_be_deleted(self):
        reservation = self._make_reservation(
            rooms=self.room_101 | self.room_102)
        reservation.line_ids[0].unlink()
        self.assertEqual(len(reservation.line_ids), 1)

    def test_room_removed_from_reservation_form_resyncs_folio(self):
        """Retirer une chambre depuis le formulaire de la réservation
        reste possible : la réservation resynchronise son folio."""
        reservation = self._make_reservation(
            rooms=self.room_101 | self.room_201)
        reservation.action_confirm()
        reservation.write({'line_ids': [(2, reservation.line_ids[0].id)]})
        self.assertEqual(len(reservation.line_ids), 1)
        self.assertEqual(len(reservation.folio_id.line_ids), 1)
