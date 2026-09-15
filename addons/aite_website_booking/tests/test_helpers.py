# -*- coding: utf-8 -*-
"""Règles du tunnel public : validation, téléphone, créneaux de départ."""
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install', 'aite_web')
class TestWebsiteHelpers(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.helper = cls.env['aite.website.booking']

    # ------------------------------------------------------------------
    # Normalisation du téléphone
    # ------------------------------------------------------------------

    def test_phone_keeps_digits_only(self):
        self.assertEqual(
            self.helper._norm_phone("+224 600 11 22 33"), "+224600112233")

    def test_phone_drops_inner_plus(self):
        self.assertEqual(self.helper._norm_phone("00+224600"), "00224600")

    def test_phone_strips_separators(self):
        self.assertEqual(
            self.helper._norm_phone("(224) 600-11.22"), "2246001122")

    def test_empty_phone(self):
        self.assertEqual(self.helper._norm_phone(None), '')
        self.assertEqual(self.helper._norm_phone(''), '')

    # ------------------------------------------------------------------
    # Validation du formulaire
    # ------------------------------------------------------------------

    def test_valid_submission(self):
        self.assertEqual(
            self.helper._validate_online_booking(
                "Mariama Diallo", "+224600112233", True), '')

    def test_missing_name(self):
        self.assertEqual(
            self.helper._validate_online_booking("", "+224600112233", True),
            'name')

    def test_name_too_short(self):
        self.assertEqual(
            self.helper._validate_online_booking("A", "+224600112233", True),
            'name')

    def test_whitespace_name_is_refused(self):
        self.assertEqual(
            self.helper._validate_online_booking(
                "   ", "+224600112233", True), 'name')

    def test_phone_too_short(self):
        self.assertEqual(
            self.helper._validate_online_booking("Mariama", "12345", True),
            'phone')

    def test_phone_with_exactly_eight_digits_passes(self):
        self.assertEqual(
            self.helper._validate_online_booking(
                "Mariama", "60011223", True), '')

    def test_missing_slot(self):
        self.assertEqual(
            self.helper._validate_online_booking(
                "Mariama", "+224600112233", False), 'slot')

    def test_name_error_takes_precedence(self):
        self.assertEqual(
            self.helper._validate_online_booking("", "1", False), 'name')

    # ------------------------------------------------------------------
    # Créneaux de départ possibles
    # ------------------------------------------------------------------

    def _slots(self, states):
        return [{'state': s} for s in states]

    def test_single_slot_service(self):
        slots = self._slots(['free', 'full', 'free'])
        self.assertEqual(self.helper._fit_starts(slots, 1), [0, 2])

    def test_two_slot_service_needs_two_consecutive(self):
        slots = self._slots(['free', 'free', 'full', 'free'])
        self.assertEqual(self.helper._fit_starts(slots, 2), [0])

    def test_no_room_for_a_long_service(self):
        slots = self._slots(['free', 'full', 'free'])
        self.assertEqual(self.helper._fit_starts(slots, 2), [])

    def test_partial_slots_do_not_count_as_free(self):
        slots = self._slots(['free', 'partial', 'free'])
        self.assertEqual(self.helper._fit_starts(slots, 2), [])

    def test_zero_length_service(self):
        self.assertEqual(
            self.helper._fit_starts(self._slots(['free']), 0), [])

    def test_empty_grid(self):
        self.assertEqual(self.helper._fit_starts([], 1), [])

    def test_whole_day_free(self):
        slots = self._slots(['free'] * 5)
        self.assertEqual(self.helper._fit_starts(slots, 3), [0, 1, 2])

    # ------------------------------------------------------------------
    # Fiche client unique
    # ------------------------------------------------------------------

    def test_creates_a_new_partner(self):
        partner = self.helper.find_or_create_partner(
            "Nouveau Client", "+224 600 99 88 77", "nouveau@example.com")
        self.assertTrue(partner)
        self.assertEqual(partner.name, "Nouveau Client")
        self.assertEqual(partner.phone, "+224600998877")

    def test_reuses_the_partner_by_phone(self):
        first = self.helper.find_or_create_partner(
            "Client Tel", "+224600112200", "tel@example.com")
        again = self.helper.find_or_create_partner(
            "Client Tel (saisi autrement)", "+224 600 11 22 00", "")
        self.assertEqual(first, again)

    def test_reuses_the_partner_by_email(self):
        first = self.helper.find_or_create_partner(
            "Client Mail", "", "mail.unique@example.com")
        again = self.helper.find_or_create_partner(
            "Client Mail bis", "", "MAIL.UNIQUE@example.com")
        self.assertEqual(first, again)

    def test_phone_lookup_wins_over_email(self):
        by_phone = self.helper.find_or_create_partner(
            "Par téléphone", "+224600333444", "a@example.com")
        found = self.helper.find_or_create_partner(
            "Autre nom", "+224600333444", "b@example.com")
        self.assertEqual(by_phone, found)
