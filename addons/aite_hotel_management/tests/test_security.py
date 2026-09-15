# -*- coding: utf-8 -*-
"""Droits d'accès : ce que chaque profil métier peut réellement faire."""
from odoo.exceptions import AccessError
from odoo.tests import tagged

from .common import HotelCommon


@tagged('post_install', '-at_install', 'aite_hotel')
class TestHotelSecurity(HotelCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        base_user = cls.env.ref('base.group_user')

        def _user(login, group_xmlid):
            return cls.env['res.users'].create({
                'name': login,
                'login': login,
                'groups_id': [(6, 0, [
                    base_user.id, cls.env.ref(group_xmlid).id,
                ])],
            })

        cls.housekeeper = _user(
            'gouvernante.test',
            'aite_hotel_management.group_hotel_housekeeping')
        cls.receptionist = _user(
            'reception.sec.test',
            'aite_hotel_management.group_hotel_user')
        cls.manager = _user(
            'responsable.test',
            'aite_hotel_management.group_hotel_manager')
        cls.outsider = cls.env['res.users'].create({
            'name': "Sans profil hôtel",
            'login': 'outsider.test',
            'groups_id': [(6, 0, [base_user.id])],
        })

    # ------------------------------------------------------------------
    # Hiérarchie des groupes
    # ------------------------------------------------------------------

    def test_group_hierarchy(self):
        """Responsable ⊃ Réception ⊃ Gouvernante."""
        hk = self.env.ref('aite_hotel_management.group_hotel_housekeeping')
        user = self.env.ref('aite_hotel_management.group_hotel_user')
        self.assertTrue(self.receptionist.has_group(
            'aite_hotel_management.group_hotel_housekeeping'))
        self.assertTrue(self.manager.has_group(
            'aite_hotel_management.group_hotel_user'))
        self.assertIn(hk, user.implied_ids)

    # ------------------------------------------------------------------
    # Gouvernante
    # ------------------------------------------------------------------

    def test_housekeeper_reads_rooms(self):
        room = self.room_101.with_user(self.housekeeper)
        self.assertEqual(room.name, '101')

    def test_housekeeper_updates_room_state(self):
        room = self.room_101.with_user(self.housekeeper)
        room.hk_state = 'to_clean'
        self.assertEqual(self.room_101.hk_state, 'to_clean')

    def test_housekeeper_cannot_create_rooms(self):
        with self.assertRaises(AccessError):
            self.env['aite.hotel.room'].with_user(self.housekeeper).create({
                'name': '999',
                'hotel_id': self.hotel.id,
                'room_type_id': self.type_std.id,
            })

    def test_housekeeper_cannot_create_reservations(self):
        with self.assertRaises(AccessError):
            self.env['aite.hotel.reservation'].with_user(
                self.housekeeper).create({
                    'hotel_id': self.hotel.id,
                    'partner_id': self.guest.id,
                    'checkin_date': self._dt(0, 14.0),
                    'checkout_date': self._dt(1, 12.0),
                })

    def test_housekeeper_manages_own_tasks(self):
        task = self.env['aite.hotel.housekeeping'].with_user(
            self.housekeeper).create({
                'room_id': self.room_101.id,
                'task_type': 'daily_clean',
            })
        task.action_start()
        task.action_done()
        self.assertEqual(task.state, 'done')

    def test_housekeeper_cannot_delete_tasks(self):
        task = self.env['aite.hotel.housekeeping'].create({
            'room_id': self.room_101.id,
            'task_type': 'daily_clean',
        })
        with self.assertRaises(AccessError):
            task.with_user(self.housekeeper).unlink()

    # ------------------------------------------------------------------
    # Périmètre de la gouvernante sur la fiche chambre
    # ------------------------------------------------------------------

    def test_housekeeper_does_not_see_the_room_price(self):
        """Le tarif d'une chambre n'est pas du ressort de la gouvernante."""
        room = self.room_101.with_user(self.housekeeper)
        fields_for_her = room.fields_get()
        self.assertNotIn('price_override', fields_for_her)
        self.assertNotIn('effective_price', fields_for_her)
        # La réception, elle, y a accès.
        self.assertIn('price_override',
                      self.room_101.with_user(self.receptionist).fields_get())

    def test_housekeeper_cannot_change_the_room_price(self):
        with self.assertRaises(AccessError):
            self.room_101.with_user(self.housekeeper).write(
                {'price_override': 1.0})

    def test_housekeeper_cannot_reclassify_a_room(self):
        """Changer le type reviendrait à changer le tarif de vente."""
        with self.assertRaises(AccessError):
            self.room_101.with_user(self.housekeeper).write(
                {'room_type_id': self.type_suite.id})

    def test_housekeeper_cannot_change_capacities(self):
        with self.assertRaises(AccessError):
            self.room_101.with_user(self.housekeeper).write(
                {'capacity_adults': 8})

    def test_housekeeper_cannot_move_a_room_to_another_hotel(self):
        other_hotel = self.env['aite.hotel.hotel'].create({
            'name': "Second établissement",
            'code': 'TS2',
            'company_id': self.company.id,
        })
        with self.assertRaises(AccessError):
            self.room_101.with_user(self.housekeeper).write(
                {'hotel_id': other_hotel.id})

    def test_housekeeper_cannot_archive_a_room(self):
        with self.assertRaises(AccessError):
            self.room_101.with_user(self.housekeeper).write(
                {'active': False})

    def test_the_refusal_names_the_fields_and_the_way_out(self):
        """Le message doit dire quoi, et vers qui se tourner."""
        with self.assertRaises(AccessError) as caught:
            self.room_101.with_user(self.housekeeper).write(
                {'capacity_adults': 4})
        message = str(caught.exception)
        self.assertIn("Capacité adultes", message)
        self.assertIn("Réception", message)

    def test_housekeeper_keeps_her_own_levers(self):
        """Elle garde l'état de ménage et le signalement hors service."""
        room = self.room_101.with_user(self.housekeeper)
        room.write({'hk_state': 'cleaning'})
        self.assertEqual(self.room_101.hk_state, 'cleaning')
        room.write({'out_of_order': True,
                    'out_of_order_reason': "Climatisation en panne"})
        self.assertTrue(self.room_101.out_of_order)
        room.write({'note': "Rideau à remplacer"})
        self.assertEqual(self.room_101.note, "Rideau à remplacer")

    def test_housekeeper_quick_buttons_still_work(self):
        room = self.room_101.with_user(self.housekeeper)
        room.action_set_to_clean()
        self.assertEqual(self.room_101.hk_state, 'to_clean')
        room.action_start_cleaning()
        self.assertEqual(self.room_101.hk_state, 'cleaning')
        room.action_set_clean()
        self.assertEqual(self.room_101.hk_state, 'clean')

    def test_receptionist_still_prices_a_room(self):
        room = self.room_101.with_user(self.receptionist)
        room.write({'price_override': 77000.0})
        self.assertEqual(self.room_101.price_override, 77000.0)

    def test_checkout_still_sends_the_room_to_cleaning(self):
        """La recouche automatique passe malgré la garde d'écriture."""
        reservation = self._make_reservation(checkin_offset=0,
                                             checkout_offset=2)
        reservation.action_confirm()
        reservation.action_checkin()
        self.env['aite.hotel.housekeeping'].with_user(
            self.receptionist)._create_checkout_task(self.room_101)
        self.assertEqual(self.room_101.hk_state, 'to_clean')

    def test_housekeeper_cannot_read_folios(self):
        """La note de séjour n'est pas du ressort de la gouvernante."""
        reservation = self._make_reservation()
        reservation.action_confirm()
        with self.assertRaises(AccessError):
            reservation.folio_id.with_user(self.housekeeper).read(['name'])

    # ------------------------------------------------------------------
    # Réception
    # ------------------------------------------------------------------

    def test_receptionist_books_and_checks_in(self):
        reservation = self.env['aite.hotel.reservation'].with_user(
            self.receptionist).create({
                'hotel_id': self.hotel.id,
                'partner_id': self.guest.id,
                'checkin_date': self._dt(0, 14.0),
                'checkout_date': self._dt(2, 12.0),
                'line_ids': [(0, 0, {
                    'room_type_id': self.type_std.id,
                    'room_id': self.room_101.id,
                    'adults': 1,
                })],
            })
        reservation.action_confirm()
        reservation.action_checkin()
        self.assertEqual(reservation.state, 'checked_in')

    def test_receptionist_collects_payment(self):
        reservation = self._make_reservation()
        reservation.action_confirm()
        payment = self.env['aite.hotel.folio.payment'].with_user(
            self.receptionist).create({
                'folio_id': reservation.folio_id.id,
                'amount': 10000.0,
                'method': 'cash',
            })
        self.assertEqual(payment.amount, 10000.0)

    def test_receptionist_collects_payment_with_accounting_on(self):
        """Régression : encaisser génère une écriture 411.

        La résolution du journal et du compte client se faisait sans
        ``sudo`` — la réception, qui n'a pas les droits comptables,
        heurtait une AccessError au moment d'encaisser.
        """
        self.company.hotel_auto_entries = True
        self.company.hotel_payment_journal_id = False
        reservation = self._make_reservation()
        reservation.action_confirm()
        payment = self.env['aite.hotel.folio.payment'].with_user(
            self.receptionist).create({
                'folio_id': reservation.folio_id.id,
                'amount': 15000.0,
                'method': 'cash',
            })
        self.assertEqual(payment.amount, 15000.0)
        self.assertTrue(payment.sudo().move_id)

    def test_manager_creates_service_with_linked_product(self):
        """Régression : créer un service crée son article support.

        L'article était créé sans ``sudo`` — le responsable hôtel n'a pas
        les droits de création sur product.product.
        """
        service = self.env['aite.hotel.service'].with_user(
            self.manager).create({
                'name': "Navette aéroport",
                'category': 'transport',
                'company_id': self.company.id,
                'price': 25000.0,
            })
        self.assertTrue(service.sudo().product_id)
        self.assertEqual(service.sudo().product_id.list_price, 25000.0)

    def test_receptionist_cannot_delete_reservations(self):
        reservation = self._make_reservation()
        with self.assertRaises(AccessError):
            reservation.with_user(self.receptionist).unlink()

    def test_receptionist_cannot_delete_folios(self):
        reservation = self._make_reservation()
        reservation.action_confirm()
        with self.assertRaises(AccessError):
            reservation.folio_id.with_user(self.receptionist).unlink()

    def test_receptionist_cannot_create_room_types(self):
        """Le paramétrage tarifaire reste au responsable."""
        with self.assertRaises(AccessError):
            self.env['aite.hotel.room.type'].with_user(
                self.receptionist).create({
                    'name': "Type pirate",
                    'base_price': 1.0,
                })

    def test_receptionist_cannot_change_season_prices(self):
        with self.assertRaises(AccessError):
            self.env['aite.hotel.season.price'].with_user(
                self.receptionist).create({
                    'name': "Promo sauvage",
                    'room_type_id': self.type_std.id,
                    'date_from': self._dt(0, 0.0).date(),
                    'date_to': self._dt(5, 0.0).date(),
                    'price': 1000.0,
                })

    # ------------------------------------------------------------------
    # Responsable
    # ------------------------------------------------------------------

    def test_manager_configures_everything(self):
        rtype = self.env['aite.hotel.room.type'].with_user(
            self.manager).create({
                'name': "Junior Suite",
                'base_price': 90000.0,
                'company_id': self.company.id,
            })
        self.assertTrue(rtype.product_id)
        room = self.env['aite.hotel.room'].with_user(self.manager).create({
            'name': '301',
            'hotel_id': self.hotel.id,
            'room_type_id': rtype.id,
        })
        self.assertTrue(room)

    def test_manager_deletes_draft_reservation(self):
        reservation = self._make_reservation()
        reservation.with_user(self.manager).unlink()
        self.assertFalse(reservation.exists())

    # ------------------------------------------------------------------
    # Hors périmètre
    # ------------------------------------------------------------------

    def test_user_without_hotel_group_sees_nothing(self):
        with self.assertRaises(AccessError):
            self.env['aite.hotel.reservation'].with_user(
                self.outsider).search([])

    def test_outsider_cannot_read_rooms(self):
        with self.assertRaises(AccessError):
            self.room_101.with_user(self.outsider).read(['name'])
