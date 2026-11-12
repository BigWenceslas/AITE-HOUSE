# -*- coding: utf-8 -*-
from lxml import html as lxml_html

from odoo.tests import HttpCase, new_test_user, tagged

WA_HREF = 'href="https://wa.me/237699000000?text=Bonjour%2C%20une%20question"'
WA_CLASS = 'o_aite_wa_button o_aite_wa_button_'


@tagged('post_install', '-at_install', 'aite_whatsapp')
class TestWhatsappButton(HttpCase):
    """ Le bouton tel que le visiteur le reçoit, page par page. """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.website = cls.env.ref('website.default_website')
        cls.website_values = {
            'aite_whatsapp_enabled': True,
            'aite_whatsapp_number': '+237 699 00 00 00',
            'aite_whatsapp_message': "Bonjour, une question",
            'aite_whatsapp_label': "Écrivez-nous",
            'aite_whatsapp_position': 'right',
        }

    def _get(self, url):
        response = self.url_open(url)
        self.assertIn(response.status_code, (200, 404), url)
        return response.text

    def test_button_on_every_page(self):
        self.website.write(self.website_values)
        for url in ('/', '/contactus', '/web/login', '/aite-page-introuvable'):
            with self.subTest(url=url):
                html = self._get(url)
                self.assertIn(WA_CLASS + 'right', html)
                self.assertIn(WA_HREF, html)
                self.assertIn('Écrivez-nous', html)

    def test_button_inside_wrapwrap(self):
        # Enfant direct de #wrapwrap, après le pied de page : les fenêtres
        # modales et le menu mobile, qui y sont aussi, passent au-dessus.
        self.website.write(self.website_values)
        doc = lxml_html.fromstring(self._get('/'))
        button_xpath = "contains(concat(' ', normalize-space(@class), ' '), ' o_aite_wa_button ')"
        buttons = doc.xpath(f"//div[@id='wrapwrap']/a[{button_xpath}]")
        self.assertEqual(len(buttons), 1)
        self.assertEqual(buttons[0].get('href'),
                         'https://wa.me/237699000000?text=Bonjour%2C%20une%20question')
        self.assertTrue(buttons[0].xpath("preceding-sibling::footer[@id='bottom']"))
        self.assertFalse(doc.xpath(f"//a[{button_xpath}][not(ancestor::div[@id='wrapwrap'])]"))

    def test_button_in_customer_portal(self):
        self.website.write(self.website_values)
        new_test_user(self.env, login='aite_wa_portal', groups='base.group_portal')
        self.authenticate('aite_wa_portal', 'aite_wa_portal')
        self.assertIn(WA_HREF, self._get('/my'))

    def test_button_visible_to_logged_in_administrator(self):
        # Odoo rend « editable » vrai pour tout concepteur du site, même hors
        # édition : le bouton ne doit pas en dépendre.
        self.website.write(self.website_values)
        self.authenticate('admin', 'admin')
        self.assertIn(WA_HREF, self._get('/'))

    def test_no_button_when_disabled(self):
        self.website.write(dict(self.website_values, aite_whatsapp_enabled=False))
        self.assertNotIn('o_aite_wa_button', self._get('/'))

    def test_left_position_and_icon_only(self):
        self.website.write(dict(self.website_values,
                                aite_whatsapp_position='left',
                                aite_whatsapp_label=False))
        html = self._get('/')
        self.assertIn(WA_CLASS + 'left', html)
        self.assertNotIn('o_aite_wa_label', html)
        # Sans accroche, le lien garde un nom pour les lecteurs d'écran.
        self.assertIn('<span class="visually-hidden">WhatsApp</span>', html)

    def test_saved_settings_show_without_waiting_for_page_cache(self):
        # Les pages servies aux visiteurs anonymes sont mises en cache : un
        # changement de réglage doit pourtant être visible tout de suite.
        self.website.write(dict(self.website_values, aite_whatsapp_enabled=False))
        self.assertNotIn('o_aite_wa_button', self._get('/'))
        self.website.write(self.website_values)
        self.assertIn(WA_HREF, self._get('/'))
