# -*- coding: utf-8 -*-
"""Registre des clients : écarts non bloquants relevés par les tutoriels.

Date de naissance mémorisée puis pré-remplie, chemins de menu exacts dans
l'aide, dates françaises dans les messages.
"""
from datetime import date

from odoo.exceptions import UserError
from odoo.tests import tagged

from odoo.addons.aite_hotel_management.tests.common import HotelCommon


@tagged('post_install', '-at_install', 'aite_guest_registry')
class TestRegistryEcarts(HotelCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.receptionist = cls.env['res.users'].create({
            'name': "Réception registre (écarts)",
            'login': 'reception.registre.ecarts',
            'groups_id': [(6, 0, [
                cls.env.ref('base.group_user').id,
                cls.env.ref('aite_hotel_management.group_hotel_user').id,
            ])],
        })
        cls.cameroon = cls.env.ref('base.cm')
        cls.hotel.country_id = cls.cameroon

    def _checked_in_reservation(self, room):
        reservation = self._make_reservation(rooms=room, checkin_offset=0,
                                             checkout_offset=1)
        reservation.action_confirm()
        reservation.action_checkin()
        return reservation

    # ------------------------------------------------------------------
    # ECARTS n° 54 : la date de naissance se mémorise et se pré-remplit
    # ------------------------------------------------------------------

    def test_birth_date_is_memorized_and_prefilled(self):
        """« Mémoriser sur la fiche client » garde aussi la date de
        naissance : au séjour suivant, elle n'est plus à ressaisir."""
        first = self._checked_in_reservation(self.room_101)
        reg = first.registration_ids
        reg.write({
            'first_name': "Jean",
            'birth_date': date(1985, 3, 12),
            'nationality_id': self.cameroon.id,
            'id_type': 'cni',
            'id_number': "123456789",
        })
        self.env.invalidate_all()
        reg.with_user(self.receptionist).action_copy_back_to_partner()
        self.env.invalidate_all()
        second = self._checked_in_reservation(self.room_102)
        reg2 = second.registration_ids
        self.assertEqual(len(reg2), 1)
        self.assertEqual(reg2.birth_date, date(1985, 3, 12))
        self.assertNotIn("naissance", reg2.missing_info or "")

    # ------------------------------------------------------------------
    # ECARTS n° 46 : l'aide du registre cite le vrai menu d'impression
    # ------------------------------------------------------------------

    def test_help_names_the_real_print_menu(self):
        menu = self.env.ref('aite_guest_registry.menu_police_register_report')
        path = " → ".join(menu.complete_name.split('/'))
        action = self.env.ref('aite_guest_registry.action_guest_registration')
        self.assertIn(path, " ".join(str(action.help).split()))

    # ------------------------------------------------------------------
    # ECARTS n° 43 (même défaut) : « Fiche … créée », au féminin
    # ------------------------------------------------------------------

    def test_creation_message_is_in_correct_french(self):
        reservation = self._checked_in_reservation(self.room_101)
        reg = reservation.registration_ids
        bodies = " ".join(str(body) for body in reg.message_ids.mapped('body'))
        self.assertIn("Fiche d'enregistrement créée", bodies)

    # ------------------------------------------------------------------
    # Règle 6 : dates au format jj/mm/aaaa dans les messages
    # ------------------------------------------------------------------

    def test_empty_police_register_message_uses_french_dates(self):
        wizard = self.env['aite.police.register.wizard'].create({
            'hotel_id': self.hotel.id,
            'date_from': date(2020, 1, 13),
            'date_to': date(2020, 1, 14),
        })
        with self.assertRaisesRegex(UserError, "13/01/2020"):
            wizard.action_print()

    # ------------------------------------------------------------------
    # Relecture : bandeau accordé en nombre, sans « (s) »
    # ------------------------------------------------------------------

    def test_hint_agrees_in_number(self):
        Res = self.env['aite.hotel.reservation']
        hint = Res._hint_text
        self.assertEqual(hint('done', 1, 1, 1),
                         "Registre à jour : 1 fiche complète.")
        self.assertEqual(hint('done', 2, 2, 2),
                         "Registre à jour : 2 fiches complètes.")
        self.assertEqual(hint('none', 0, 0, 1),
                         "Aucune fiche d'enregistrement : 1 occupant "
                         "attendu.")
        self.assertEqual(hint('none', 0, 0, 2),
                         "Aucune fiche d'enregistrement : 2 occupants "
                         "attendus.")
        self.assertEqual(hint('partial', 1, 0, 2),
                         "1 fiche à compléter · 1 occupant sans fiche")
        self.assertEqual(hint('partial', 3, 1, 5),
                         "2 fiches à compléter · 2 occupants sans fiche")

    def test_one_name_for_the_registration_card(self):
        """Un seul nom pour la fiche (« fiche d'enregistrement ») : la
        fenêtre ne s'appelle plus « Fiches clients » et l'imprimé ne parle
        plus de « Registre des voyageurs »."""
        reservation = self._checked_in_reservation(self.room_101)
        action = reservation.action_open_registrations()
        self.assertTrue(action['name'].startswith("Fiches d'enregistrement"),
                        action['name'])
        arch = self.env.ref(
            'aite_guest_registry.view_hotel_reservation_form_registry').arch
        self.assertNotIn("Fiches clients</span>", arch)
        report = self.env.ref(
            'aite_guest_registry.report_registration_card_document').arch
        self.assertNotIn("Registre des voyageurs", report)
        self.assertIn("Registre des clients", report)
