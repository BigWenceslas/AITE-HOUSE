# -*- coding: utf-8 -*-
from unittest import skipUnless
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged

from odoo.addons.phone_validation.tools import phone_validation

try:
    import phonenumbers
except ImportError:
    phonenumbers = None

NUMBER_DIGITS = '237699000000'
WA_LINK = f'https://wa.me/{NUMBER_DIGITS}'


def _phone_format_without_lib(number, *args, **kwargs):
    """ Comportement de phone_validation quand phonenumbers est absent. """
    return number


@tagged('post_install', '-at_install', 'aite_whatsapp')
class TestWhatsappLink(TransactionCase):
    """ Lien wa.me, normalisation du numéro, contrôles et écran Paramètres. """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.website = cls.env['website'].create({'name': "Site WhatsApp (test)"})
        cls.website.company_id.country_id = cls.env.ref('base.cm')

    def _link(self, number, message=False):
        self.website.write({
            'aite_whatsapp_number': number,
            'aite_whatsapp_message': message,
        })
        return self.website.aite_whatsapp_url

    # Numéro -------------------------------------------------------------

    def test_international_formats(self):
        for number in ('+237 699 00 00 00', '+237-699-00-00-00',
                       '(+237) 699.00.00.00', '00237 699 00 00 00'):
            with self.subTest(number=number):
                self.assertEqual(self._link(number), WA_LINK)

    def test_international_formats_without_phonenumbers(self):
        with patch.object(phone_validation, 'phone_format', _phone_format_without_lib):
            for number in ('+237 699 00 00 00', '(+237) 699.00.00.00',
                           '00237 699 00 00 00'):
                with self.subTest(number=number):
                    self.assertEqual(self._link(number), WA_LINK)

    @skipUnless(phonenumbers, "bibliothèque phonenumbers absente")
    def test_local_number_gets_company_country_code(self):
        for number in ('699 00 00 00', '237699000000'):
            with self.subTest(number=number):
                self.assertEqual(self._link(number), WA_LINK)

    def test_local_number_refused_when_it_cannot_be_completed(self):
        # Sans phonenumbers, on ne devine pas l'indicatif : refus plutôt
        # qu'un lien vers un mauvais correspondant (wa.me/699000000).
        with patch.object(phone_validation, 'phone_format', _phone_format_without_lib), \
                self.assertRaises(ValidationError):
            self.website.write({'aite_whatsapp_enabled': True,
                                'aite_whatsapp_number': '699 00 00 00'})

    def test_pasted_number_with_invisible_marks(self):
        # Copié depuis WhatsApp ou les contacts : marques de sens d'écriture
        # invisibles autour du numéro, « ＋ » pleine chasse.
        with patch.object(phone_validation, 'phone_format', _phone_format_without_lib):
            for number in ('\u202a+237 699 00 00 00\u202c', '\u200e+237 699 00 00 00',
                           '＋237 699 00 00 00'):
                with self.subTest(number=repr(number)):
                    self.assertEqual(self._link(number), WA_LINK)

    def test_international_number_without_company_country(self):
        self.website.company_id.country_id = False
        self.assertEqual(self._link('+237 699 00 00 00'), WA_LINK)

    def test_no_number_no_link(self):
        self.assertFalse(self._link(False))
        self.assertFalse(self._link('   '))

    # Message ------------------------------------------------------------

    def test_message_is_url_encoded(self):
        message = "Bonjour, j'ai une question : 2+2 & café ?"
        url = self._link('+237 699 00 00 00', message)
        self.assertEqual(
            url,
            WA_LINK + '?text=Bonjour%2C%20j%27ai%20une%20question%20%3A'
                      '%202%2B2%20%26%20caf%C3%A9%20%3F',
        )
        self.assertEqual(parse_qs(urlsplit(url).query)['text'], [message])

    def test_empty_message_has_no_text_parameter(self):
        self.assertEqual(self._link('+237 699 00 00 00', ''), WA_LINK)

    def test_message_follows_visitor_language(self):
        self.env['res.lang']._activate_lang('fr_FR')
        self.website.aite_whatsapp_number = '+237 699 00 00 00'
        self.website.with_context(lang='en_US').aite_whatsapp_message = "Hello"
        self.website.with_context(lang='fr_FR').aite_whatsapp_message = "Bonjour"
        self.assertEqual(self.website.with_context(lang='en_US').aite_whatsapp_url,
                         WA_LINK + '?text=Hello')
        self.assertEqual(self.website.with_context(lang='fr_FR').aite_whatsapp_url,
                         WA_LINK + '?text=Bonjour')

    # Contrôles ----------------------------------------------------------

    def test_enabled_requires_a_number(self):
        with self.assertRaises(ValidationError):
            self.website.write({'aite_whatsapp_enabled': True,
                                'aite_whatsapp_number': False})

    def test_unrecognised_too_short_or_too_long_number_rejected(self):
        for number in ('12345', '+12345', '+1 234 567 890 123 456'):
            with self.subTest(number=number), self.assertRaises(ValidationError):
                self.website.write({'aite_whatsapp_enabled': True,
                                    'aite_whatsapp_number': number})

    def test_button_can_always_be_switched_off(self):
        # Bouton actif avec un numéro devenu non reconnu (reprise d'une
        # ancienne version, bibliothèque retirée…) : le désactiver doit
        # rester possible.
        self.env.cr.execute(
            "UPDATE website SET aite_whatsapp_enabled = TRUE,"
            " aite_whatsapp_number = '699 00 00 00' WHERE id = %s",
            [self.website.id])
        self.website.invalidate_recordset()
        with patch.object(phone_validation, 'phone_format', _phone_format_without_lib):
            self.website.aite_whatsapp_enabled = False
        self.assertFalse(self.website.aite_whatsapp_enabled)

    def test_disabled_without_number_is_allowed(self):
        self.website.write({'aite_whatsapp_enabled': False,
                            'aite_whatsapp_number': False})
        self.assertFalse(self.website.aite_whatsapp_enabled)

    def test_position_defaults_to_right(self):
        self.assertEqual(self.website.aite_whatsapp_position, 'right')

    # Écran Paramètres ---------------------------------------------------

    def _settings_values(self):
        # Dans l'ordre de l'écran : la case avant le numéro.
        return {
            'website_id': self.website.id,
            'aite_whatsapp_enabled': True,
            'aite_whatsapp_number': '+237 699 00 00 00',
            'aite_whatsapp_message': "Bonjour",
            'aite_whatsapp_label': "Écrivez-nous",
            'aite_whatsapp_position': 'left',
        }

    def _assert_website_configured(self):
        self.assertRecordValues(self.website, [{
            'aite_whatsapp_enabled': True,
            'aite_whatsapp_number': '+237 699 00 00 00',
            'aite_whatsapp_message': "Bonjour",
            'aite_whatsapp_label': "Écrivez-nous",
            'aite_whatsapp_position': 'left',
            'aite_whatsapp_url': WA_LINK + '?text=Bonjour',
        }])

    def test_settings_enable_and_number_in_one_save(self):
        # Le site n'a pas encore de numéro : cocher la case et saisir le
        # numéro dans le même enregistrement doit passer.
        self.assertFalse(self.website.aite_whatsapp_number)
        settings = self.env['res.config.settings'].create(self._settings_values())
        settings.execute()
        self._assert_website_configured()
        self.assertEqual(settings.aite_whatsapp_url, WA_LINK + '?text=Bonjour')

    def test_settings_write_on_existing_record(self):
        settings = self.env['res.config.settings'].create({'website_id': self.website.id})
        settings.write(self._settings_values())
        self._assert_website_configured()
