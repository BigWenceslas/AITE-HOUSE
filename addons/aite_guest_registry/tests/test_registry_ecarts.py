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
