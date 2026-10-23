# -*- coding: utf-8 -*-
"""Registre des clients : pré-remplissage, mémorisation, impression."""
import json

from odoo.tests import tagged

from odoo.addons.aite_hotel_management.tests.common import HotelCommon


@tagged('post_install', '-at_install', 'aite_guest_registry')
class TestGuestRegistry(HotelCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        base_user = cls.env.ref('base.group_user')
        # Profil Réception tel que créé pour la démonstration : ses seuls
        # groupes métier, sans « Création de contacts ».
        cls.receptionist = cls.env['res.users'].create({
            'name': "Réception registre",
            'login': 'reception.registre.test',
            'groups_id': [(6, 0, [
                base_user.id,
                cls.env.ref('aite_hotel_management.group_hotel_user').id,
            ])],
        })
        cls.cameroon = cls.env.ref('base.cm')
        cls.france = cls.env.ref('base.fr')
        cls.hotel.country_id = cls.cameroon

    def _checked_in_reservation(self, partner=None):
        reservation = self._make_reservation(partner=partner,
                                             checkin_offset=0,
                                             checkout_offset=2)
        reservation.action_confirm()
        reservation.action_checkin()
        return reservation

    # ------------------------------------------------------------------
    # ECARTS n° 30 (a) : le nom n'est plus coupé au premier espace
    # ------------------------------------------------------------------

    def test_prefill_keeps_full_name_in_last_name(self):
        """« Ngo Bikaï Solange » ne devient pas Nom « Ngo » : sans champs
        nom / prénom distincts sur le contact, le nom complet reste dans
        Nom et la fiche signale le prénom à compléter."""
        partner = self.env['res.partner'].create(
            {'name': "Ngo Bikaï Solange"})
        reservation = self._checked_in_reservation(partner)
        reg = reservation.registration_ids
        self.assertEqual(len(reg), 1)
        self.assertEqual(reg.last_name, "Ngo Bikaï Solange")
        self.assertFalse(reg.first_name)
        self.assertIn("le prénom", reg.missing_info)

    def test_prefill_uses_partner_name_parts_when_available(self):
        """Si le contact porte nom et prénom distincts (module de
        découpage du nom installé), ils sont repris tels quels."""
        Reg = self.env['aite.guest.registration']
        reservation = self._make_reservation()

        class FakePartner:
            """Contact minimal muni de ``lastname`` / ``firstname``."""
            _fields = {'lastname': True, 'firstname': True}
            id = False
            name = "Ngono Estelle"
            lastname = "Ngono"
            firstname = "Estelle"
            nationality_id = country_id = self.env['res.country']
            guest_id_type = guest_id_number = guest_birth_date = False
            street = city = phone = mobile = email = False

        vals = Reg._vals_from_partner(FakePartner(), reservation)
        self.assertEqual(vals['last_name'], "Ngono")
        self.assertEqual(vals['first_name'], "Estelle")

    # ------------------------------------------------------------------
    # ECARTS n° 30 (b) : résidence vide par défaut
    # ------------------------------------------------------------------

    def test_new_line_has_no_default_residence(self):
        """Une nouvelle ligne ne reçoit pas d'office la résidence de
        l'hôtel : un étranger dont on ne change que la nationalité n'est
        pas compté résident."""
        reservation = self._checked_in_reservation()
        action = reservation.action_open_registrations()
        ctx = action['context']
        self.assertFalse(ctx.get('default_country_id'))
        reg = self.env['aite.guest.registration'].with_context(**ctx).create({
            'last_name': "Durand",
            'first_name': "Paul",
            'nationality_id': self.france.id,
        })
        self.assertFalse(reg.country_id)
        self.assertFalse(reg.is_resident)

    # ------------------------------------------------------------------
    # ECARTS n° 14 : « Mémoriser sur la fiche client » par la réception
    # ------------------------------------------------------------------

    def test_reception_copies_back_to_partner(self):
        reservation = self._checked_in_reservation()
        reg = reservation.registration_ids
        reg.write({'nationality_id': self.france.id, 'id_type': 'passport',
                   'id_number': "19FR12345"})
        self.env.invalidate_all()
        reg.with_user(self.receptionist).action_copy_back_to_partner()
        self.env.invalidate_all()
        self.assertEqual(self.guest.nationality_id, self.france)
        self.assertEqual(self.guest.guest_id_type, 'passport')
        self.assertEqual(self.guest.guest_id_number, "19FR12345")

    # ------------------------------------------------------------------
    # ECARTS n° 16 : le registre de police s'imprime depuis l'interface
    # ------------------------------------------------------------------

    def test_police_register_renders_with_web_client_context(self):
        """Le client web renvoie le contexte de l'action en JSON : les
        dates y deviennent des chaînes. Le rendu doit tenir."""
        reservation = self._checked_in_reservation()
        reg = reservation.registration_ids
        wizard = self.env['aite.police.register.wizard'].with_user(
            self.receptionist).create({'hotel_id': self.hotel.id})
        action = wizard.action_print()
        # Aller-retour JSON, comme le client web.
        ctx = json.loads(json.dumps(action.get('context') or {},
                                    default=str))
        report = self.env.ref('aite_guest_registry.report_police_register')
        html, _fmt = self.env['ir.actions.report'].with_user(
            self.receptionist).with_context(**ctx)._render_qweb_html(
                report.report_name, reg.ids)
        html = html.decode()
        self.assertIn(wizard.date_from.strftime('%d/%m/%Y'), html)
        self.assertIn(wizard.date_to.strftime('%d/%m/%Y'), html)

    def test_police_register_renders_with_string_dates(self):
        """Même avec ``date_from`` / ``date_to`` en chaînes ISO (ancien
        contexte), le gabarit ne plante pas."""
        reservation = self._checked_in_reservation()
        report = self.env.ref('aite_guest_registry.report_police_register')
        html, _fmt = self.env['ir.actions.report'].with_context(
            date_from='2026-10-13', date_to='2026-10-20',
            hotel_name=self.hotel.name)._render_qweb_html(
                report.report_name, reservation.registration_ids.ids)
        self.assertIn('13/10/2026', html.decode())
