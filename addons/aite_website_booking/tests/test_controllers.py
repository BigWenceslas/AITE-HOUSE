# -*- coding: utf-8 -*-
"""Tunnel public de réservation : pages, tunnel de bout en bout, erreurs.

Ces tests parlent au serveur HTTP réel (``HttpCase``) : ils exercent le
routage, le rendu QWeb, le CSRF et l'écriture en base — le même chemin
qu'un visiteur du site.
"""
import re
from datetime import timedelta

from odoo import fields
from odoo.tests import HttpCase, tagged


@tagged('post_install', '-at_install', 'aite_web')
class TestWebsiteBookingTunnel(HttpCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.env.user.tz = 'UTC'

        cls.salon = cls.env['aite.booking.resource'].create({
            'name': "Salon Web",
            'kind': 'space',
            'company_id': cls.company.id,
            'capacity': 1,
            'open_hour': 9.0,
            'close_hour': 20.0,
            'slot_minutes': '60',
            'price_hour': 30000.0,
            'allow_online': True,
        })
        cls.salon_prive = cls.env['aite.booking.resource'].create({
            'name': "Salon privé (hors ligne)",
            'kind': 'space',
            'company_id': cls.company.id,
            'allow_online': False,
        })
        cls.cabine = cls.env['aite.booking.resource'].create({
            'name': "Cabine Web",
            'kind': 'spa',
            'company_id': cls.company.id,
            'capacity': 1,
            'open_hour': 10.0,
            'close_hour': 18.0,
            'slot_minutes': '30',
            'allow_online': True,
        })
        product = cls.env['product.product'].create({
            'name': "Soin Web",
            'type': 'service',
            'list_price': 40000.0,
            'sale_ok': True,
            'taxes_id': [(5, 0, 0)],
        })
        cls.service = cls.env['aite.booking.service'].create({
            'name': "Soin du visage",
            'kind': 'spa',
            'company_id': cls.company.id,
            'duration_minutes': 60,
            'price': 40000.0,
            'product_id': product.id,
        })
        cls.tomorrow = fields.Date.to_string(
            fields.Date.context_today(cls.env.user) + timedelta(days=1))

    def setUp(self):
        super().setUp()
        # Ouvre une session publique et pose son cookie sur le client HTTP :
        # sans cela, le jeton CSRF lu dans le formulaire appartiendrait à
        # une autre session et le POST serait rejeté (403).
        self.authenticate(None, None)

    # ------------------------------------------------------------------
    # Pages publiques
    # ------------------------------------------------------------------

    def test_landing_page_is_public(self):
        response = self.url_open('/reservation')
        self.assertEqual(response.status_code, 200)

    def test_spaces_page_lists_online_resources(self):
        response = self.url_open('/reservation/espaces')
        self.assertEqual(response.status_code, 200)
        self.assertIn("Salon Web", response.text)

    def test_spaces_page_hides_offline_resources(self):
        response = self.url_open('/reservation/espaces')
        self.assertNotIn("Salon privé (hors ligne)", response.text)

    def test_services_page_lists_the_catalogue(self):
        response = self.url_open('/reservation/prestations')
        self.assertEqual(response.status_code, 200)
        self.assertIn("Soin du visage", response.text)

    def test_space_grid_shows_free_slots(self):
        response = self.url_open(
            '/reservation/espace/%s?date=%s' % (self.salon.id, self.tomorrow))
        self.assertEqual(response.status_code, 200)
        self.assertIn("09:00", response.text)

    def test_offline_resource_redirects(self):
        response = self.url_open(
            '/reservation/espace/%s' % self.salon_prive.id)
        self.assertEqual(response.status_code, 200)
        # Redirigé vers la liste des espaces.
        self.assertIn("Salon Web", response.text)

    def test_unknown_resource_redirects(self):
        response = self.url_open('/reservation/espace/999999')
        self.assertEqual(response.status_code, 200)

    def test_bad_date_falls_back_to_today(self):
        response = self.url_open(
            '/reservation/espace/%s?date=pas-une-date' % self.salon.id)
        self.assertEqual(response.status_code, 200)

    def test_rooms_form_is_public(self):
        response = self.url_open('/reservation/chambres')
        self.assertEqual(response.status_code, 200)

    # ------------------------------------------------------------------
    # Tunnel de réservation d'un créneau
    # ------------------------------------------------------------------

    def test_slot_booking_end_to_end(self):
        """Un visiteur réserve un créneau : le client et la réservation
        existent, et le créneau n'est plus proposé."""
        before = self.env['aite.slot.booking'].search_count([])
        response = self.url_open(
            '/reservation/confirmer',
            data={
                'resource_id': self.salon.id,
                'date': self.tomorrow,
                'start_h': '10.0',
                'name': "Fatoumata Camara",
                'phone': "+224 600 55 44 33",
                'email': "fatoumata.web@example.com",
                'csrf_token': self._csrf(),
            })
        self.assertEqual(response.status_code, 200)
        bookings = self.env['aite.slot.booking'].search([])
        self.assertEqual(len(bookings), before + 1)
        booking = self.env['aite.slot.booking'].search(
            [], order='id desc', limit=1)
        self.assertEqual(booking.resource_id, self.salon)
        self.assertEqual(booking.state, 'confirmed')
        self.assertEqual(booking.source, 'online')
        self.assertEqual(booking.partner_id.name, "Fatoumata Camara")
        self.assertEqual(booking.partner_id.phone, "+224600554433")
        self.assertEqual(booking.amount, 30000.0)

    def test_double_booking_is_refused(self):
        """Le même créneau ne peut pas être vendu deux fois."""
        common = {
            'resource_id': self.salon.id,
            'date': self.tomorrow,
            'start_h': '14.0',
        }
        self.url_open('/reservation/confirmer', data=dict(
            common, name="Premier Client", phone="+224 600 11 00 11",
            csrf_token=self._csrf()))
        self.url_open('/reservation/confirmer', data=dict(
            common, name="Second Client", phone="+224 600 22 00 22",
            csrf_token=self._csrf()))
        self.assertEqual(
            self.env['aite.slot.booking'].search_count([
                ('resource_id', '=', self.salon.id),
                ('state', '=', 'confirmed'),
            ]), 1,
            "le second visiteur ne doit pas obtenir le même créneau")

    def test_refused_attempt_leaves_no_ghost_booking(self):
        """Régression : une tentative en conflit ne doit rien laisser.

        La réservation était créée puis la confirmation échouait ; le
        brouillon restait en base et polluait le back-office d'une
        demande fantôme à chaque tentative refusée.
        """
        common = {
            'resource_id': self.salon.id,
            'date': self.tomorrow,
            'start_h': '16.0',
        }
        self.url_open('/reservation/confirmer', data=dict(
            common, name="Client Légitime", phone="+224 600 33 00 33",
            csrf_token=self._csrf()))
        before = self.env['aite.slot.booking'].search_count(
            [('resource_id', '=', self.salon.id)])
        self.url_open('/reservation/confirmer', data=dict(
            common, name="Client Malchanceux", phone="+224 600 44 00 44",
            csrf_token=self._csrf()))
        self.assertEqual(
            self.env['aite.slot.booking'].search_count(
                [('resource_id', '=', self.salon.id)]), before,
            "aucune réservation fantôme ne doit subsister")

    def test_missing_name_is_rejected(self):
        before = self.env['aite.slot.booking'].search_count([])
        self.url_open('/reservation/confirmer', data={
            'resource_id': self.salon.id,
            'date': self.tomorrow,
            'start_h': '11.0',
            'name': "",
            'phone': "+224600112233",
            'csrf_token': self._csrf(),
        })
        self.assertEqual(
            self.env['aite.slot.booking'].search_count([]), before)

    def test_short_phone_is_rejected(self):
        before = self.env['aite.slot.booking'].search_count([])
        self.url_open('/reservation/confirmer', data={
            'resource_id': self.salon.id,
            'date': self.tomorrow,
            'start_h': '12.0',
            'name': "客 Test",
            'phone': "123",
            'csrf_token': self._csrf(),
        })
        self.assertEqual(
            self.env['aite.slot.booking'].search_count([]), before)

    def test_service_booking_uses_its_duration(self):
        self.url_open('/reservation/confirmer', data={
            'resource_id': self.cabine.id,
            'service_id': self.service.id,
            'date': self.tomorrow,
            'start_h': '10.0',
            'name': "Aïssatou Barry",
            'phone': "+224600778899",
            'csrf_token': self._csrf(),
        })
        booking = self.env['aite.slot.booking'].search(
            [('resource_id', '=', self.cabine.id)], order='id desc', limit=1)
        self.assertTrue(booking)
        self.assertEqual(booking.service_id, self.service)
        self.assertEqual(booking.duration_hours, 1.0)
        self.assertEqual(booking.amount, 40000.0)

    # ------------------------------------------------------------------
    # Demande de séjour
    # ------------------------------------------------------------------

    def test_stay_request_creates_a_draft_reservation(self):
        today = fields.Date.context_today(self.env.user)
        checkin = fields.Date.to_string(today + timedelta(days=10))
        checkout = fields.Date.to_string(today + timedelta(days=13))
        self.url_open('/reservation/chambres/envoyer', data={
            'name': "Ousmane Sow",
            'phone': "+224600445566",
            'email': "ousmane.web@example.com",
            'checkin': checkin,
            'checkout': checkout,
            'adults': '2',
            'message': "Chambre calme si possible",
            'csrf_token': self._csrf(),
        })
        partner = self.env['res.partner'].search(
            [('phone', '=', '+224600445566')], limit=1)
        self.assertTrue(partner, "le client doit avoir été créé")
        reservation = self.env['aite.hotel.reservation'].search(
            [('partner_id', '=', partner.id), ('source', '=', 'website')],
            limit=1)
        self.assertTrue(reservation)
        self.assertEqual(reservation.partner_id.name, "Ousmane Sow")
        self.assertEqual(reservation.state, 'draft')
        self.assertIn("2 adulte(s)", reservation.note)
        self.assertIn("Chambre calme", reservation.note)

    def test_stay_request_rejects_inverted_dates(self):
        today = fields.Date.context_today(self.env.user)
        before = self.env['aite.hotel.reservation'].search_count(
            [('source', '=', 'website')])
        self.url_open('/reservation/chambres/envoyer', data={
            'name': "Dates Fausses",
            'phone': "+224600000011",
            'checkin': fields.Date.to_string(today + timedelta(days=10)),
            'checkout': fields.Date.to_string(today + timedelta(days=5)),
            'csrf_token': self._csrf(),
        })
        self.assertEqual(
            self.env['aite.hotel.reservation'].search_count(
                [('source', '=', 'website')]), before)

    def test_stay_request_rejects_missing_checkout(self):
        today = fields.Date.context_today(self.env.user)
        before = self.env['aite.hotel.reservation'].search_count(
            [('source', '=', 'website')])
        self.url_open('/reservation/chambres/envoyer', data={
            'name': "Sans Départ",
            'phone': "+224600000022",
            'checkin': fields.Date.to_string(today + timedelta(days=10)),
            'checkout': '',
            'csrf_token': self._csrf(),
        })
        self.assertEqual(
            self.env['aite.hotel.reservation'].search_count(
                [('source', '=', 'website')]), before)

    # ------------------------------------------------------------------
    # Espace client
    # ------------------------------------------------------------------

    def test_my_bookings_requires_login(self):
        """L'espace client n'est pas accessible en anonyme."""
        response = self.url_open('/mes-reservations')
        self.assertEqual(response.status_code, 200)
        self.assertIn('/web/login', response.url)

    def test_my_bookings_lists_own_reservations(self):
        user = self.env['res.users'].create({
            'name': "Client Portail",
            'login': 'portail.web.test',
            'password': 'portail.web.test.pwd',
            'groups_id': [(6, 0, [self.env.ref('base.group_portal').id])],
        })
        # Créneau aligné sur la grille horaire de la ressource (9 h → 20 h).
        day = fields.Date.context_today(self.env.user) + timedelta(days=2)
        start = fields.Datetime.to_datetime(str(day)) + timedelta(hours=15)
        self.env['aite.slot.booking'].create({
            'resource_id': self.salon.id,
            'partner_id': user.partner_id.id,
            'company_id': self.company.id,
            'start': fields.Datetime.to_string(start),
            'stop': fields.Datetime.to_string(start + timedelta(hours=1)),
        })
        self.authenticate('portail.web.test', 'portail.web.test.pwd')
        response = self.url_open('/mes-reservations')
        self.assertEqual(response.status_code, 200)
        self.assertIn("Salon Web", response.text)

    # ------------------------------------------------------------------
    # Utilitaires
    # ------------------------------------------------------------------

    def _csrf(self, page='/reservation/chambres'):
        """
        Jeton CSRF lu dans le formulaire, comme le ferait un navigateur.

        Le tunnel est protégé par CSRF : poster sans jeton valide est
        rejeté. On récupère donc celui que le serveur a placé dans la
        page — ce qui vérifie au passage que le formulaire le porte bien.
        """
        html = self.url_open(page).text
        match = re.search(
            r'name="csrf_token"[^>]*\bvalue="([^"]+)"', html)
        self.assertTrue(match, "le formulaire doit porter un jeton CSRF")
        return match.group(1)

    def test_post_without_csrf_token_is_rejected(self):
        """Le tunnel est bien protégé contre le POST forgé."""
        before = self.env['aite.slot.booking'].search_count([])
        response = self.url_open('/reservation/confirmer', data={
            'resource_id': self.salon.id,
            'date': self.tomorrow,
            'start_h': '9.0',
            'name': "Sans Jeton",
            'phone': "+224600909090",
        })
        # Odoo répond 400 quand le jeton manque, 403 quand il est invalide.
        self.assertIn(response.status_code, (400, 403))
        self.assertEqual(
            self.env['aite.slot.booking'].search_count([]), before)

    def test_post_with_a_forged_csrf_token_is_rejected(self):
        before = self.env['aite.slot.booking'].search_count([])
        response = self.url_open('/reservation/confirmer', data={
            'resource_id': self.salon.id,
            'date': self.tomorrow,
            'start_h': '9.0',
            'name': "Jeton Forgé",
            'phone': "+224600919191",
            'csrf_token': 'deadbeef' * 5 + 'o9999999999',
        })
        self.assertIn(response.status_code, (400, 403))
        self.assertEqual(
            self.env['aite.slot.booking'].search_count([]), before)
