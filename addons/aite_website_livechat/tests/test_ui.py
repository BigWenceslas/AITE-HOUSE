# -*- coding: utf-8 -*-
from odoo.tests import tagged

from .common import AWAY_TEXT, AiteLivechatCommon


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


class LivechatWhatsappOverlapMixin:
    """ Bulle du chat et bouton WhatsApp sur la même page. """

    def _check_no_overlap(self):
        whatsapp = self.env['ir.module.module']._get('aite_website_whatsapp')
        if whatsapp.state != 'installed':
            self.skipTest("module aite_website_whatsapp non installé")
        self.website.write({
            'aite_whatsapp_enabled': True,
            'aite_whatsapp_number': '+237 699 00 00 00',
            'aite_whatsapp_label': "Écrivez-nous sur WhatsApp",
            'aite_whatsapp_position': 'right',
        })
        self.start_tour('/contactus', 'aite_website_livechat_whatsapp_overlap_tour')


@tagged('post_install', '-at_install', 'aite_website_livechat')
class TestLivechatWhatsappDesktop(LivechatWhatsappOverlapMixin, AiteLivechatCommon):
    browser_size = '1440x900'

    def test_bubble_and_whatsapp_do_not_overlap(self):
        self._check_no_overlap()


@tagged('post_install', '-at_install', 'aite_website_livechat')
class TestLivechatWhatsappMobile(LivechatWhatsappOverlapMixin, AiteLivechatCommon):
    browser_size = '375x800'
    touch_enabled = True

    def test_bubble_and_whatsapp_do_not_overlap(self):
        self._check_no_overlap()
