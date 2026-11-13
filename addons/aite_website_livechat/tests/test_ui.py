# -*- coding: utf-8 -*-
from unittest.mock import patch

from werkzeug.exceptions import ServiceUnavailable

from odoo.tests import tagged
from odoo.tests.common import ChromeBrowser

from odoo.addons.bus.websocket import WebsocketConnectionHandler

from .common import AWAY_TEXT, AiteLivechatCommon

# Navigateur d'un téléphone Android (la colonne de bulles du chat y est plus
# haute : classe « o-mobile »).
ANDROID_USER_AGENT = (
    "Mozilla/5.0 (Linux; Android 13; Pixel 5) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
)


@tagged('post_install', '-at_install', 'aite_website_livechat')
class TestLivechatTour(AiteLivechatCommon):
    """ Parcours réel d'un visiteur public dans le navigateur, aucun
    opérateur en ligne. """

    def test_public_visitor_reaches_offline_operator(self):
        self.start_tour('/', 'aite_website_livechat_offline_tour')
        channel = self.env['discuss.channel'].search([
            ('livechat_channel_id', '=', self.livechat_channel.id),
        ])
        self.assertEqual(len(channel), 1)
        # La conversation de l'opératrice contient le message du visiteur.
        self.assertEqual(channel.livechat_operator_id, self.operator.partner_id)
        self.assertIn(self.operator.partner_id, channel.channel_member_ids.partner_id)
        visitor_messages = channel.message_ids.filtered('author_guest_id')
        self.assertEqual(len(visitor_messages), 1)
        self.assertIn('visiteur.tour@exemple.cm', visitor_messages.body)
        self.assertEqual(channel.aite_visitor_email, 'visiteur.tour@exemple.cm')
        self.assertIn(channel, self.env['discuss.channel'].with_user(self.operator).search(
            [('is_member', '=', True)]))
        self.assertEqual(len(self._away_messages(channel)), 1)
        self.assertIn(AWAY_TEXT, self._away_messages(channel).body)


    def test_away_message_shown_without_websocket(self):
        # Connexion en temps réel refusée (proxy mal réglé, réseau
        # d'entreprise) : le message d'absence s'affiche quand même, avec la
        # réponse à l'envoi du message du visiteur.
        with patch.object(
            WebsocketConnectionHandler, 'open_connection',
            side_effect=ServiceUnavailable("websocket refusé pour le test"),
        ) as open_connection:
            self.start_tour('/', 'aite_website_livechat_offline_tour')
        self.assertTrue(open_connection.called, "Le navigateur a tenté la connexion en temps réel.")
        channel = self.env['discuss.channel'].search([('livechat_channel_id', '=', self.livechat_channel.id)])
        self.assertEqual(len(self._away_messages(channel)), 1)

    def test_operator_sees_the_visitor_question(self):
        # Liste des messages de l'opératrice : la question du visiteur, un
        # message non lu, pas « Vous : Merci pour votre message ! … ».
        channel = self._start_session()
        self._visitor_post(channel, "Bonjour, avez-vous ce modèle en stock ?")
        self.assertEqual(len(self._away_messages(channel)), 1)
        self.start_tour('/odoo', 'aite_website_livechat_operator_preview_tour', login=self.operator.login)


class LivechatWhatsappOverlapMixin:
    """ Bulle du chat et bouton WhatsApp sur la même page. """

    def _check_no_overlap(self, tour='aite_website_livechat_whatsapp_overlap_tour'):
        whatsapp = self.env['ir.module.module']._get('aite_website_whatsapp')
        if whatsapp.state != 'installed':
            self.skipTest("module aite_website_whatsapp non installé")
        self.website.write({
            'aite_whatsapp_enabled': True,
            'aite_whatsapp_number': '+237 699 00 00 00',
            'aite_whatsapp_label': "Écrivez-nous sur WhatsApp",
            'aite_whatsapp_position': 'right',
        })
        self.start_tour('/contactus', tour)


@tagged('post_install', '-at_install', 'aite_website_livechat')
class TestLivechatWhatsappDesktop(LivechatWhatsappOverlapMixin, AiteLivechatCommon):
    browser_size = '1440x900'

    def test_bubble_and_whatsapp_do_not_overlap(self):
        self._check_no_overlap()

    def test_folded_conversation_and_whatsapp_do_not_overlap(self):
        # Une conversation réduite s'empile au-dessus de la bulle, avec le
        # bouton d'options (invisible tant que la souris ne le survole pas).
        self._check_no_overlap('aite_website_livechat_whatsapp_folded_tour')


@tagged('post_install', '-at_install', 'aite_website_livechat')
class TestLivechatWhatsappMobile(LivechatWhatsappOverlapMixin, AiteLivechatCommon):
    browser_size = '375x800'
    touch_enabled = True

    def test_bubble_and_whatsapp_do_not_overlap(self):
        self._check_no_overlap()


@tagged('post_install', '-at_install', 'aite_website_livechat')
class TestLivechatWhatsappAndroid(LivechatWhatsappOverlapMixin, AiteLivechatCommon):
    """ Vrai téléphone : Odoo reconnaît Android ou iOS au navigateur et
    remonte la bulle du chat de 35 px. """
    browser_size = '393x727'
    touch_enabled = True

    def setUp(self):
        super().setUp()
        original = ChromeBrowser._websocket_request

        def _websocket_request(browser, method, *, params=None, timeout=10.0):
            result = original(browser, method, params=params, timeout=timeout)
            if method == 'Emulation.setDeviceMetricsOverride':
                original(browser, 'Emulation.setUserAgentOverride', params={'userAgent': ANDROID_USER_AGENT})
            return result

        self.patch(ChromeBrowser, '_websocket_request', _websocket_request)

    def test_bubble_folded_conversation_and_whatsapp_do_not_overlap(self):
        self._check_no_overlap('aite_website_livechat_whatsapp_android_tour')
