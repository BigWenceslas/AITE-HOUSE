# -*- coding: utf-8 -*-
from odoo import Command
from odoo.tests import tagged

from .common import AiteLivechatCommon


@tagged('post_install', '-at_install', 'aite_website_livechat')
class TestLivechatAvailability(AiteLivechatCommon):
    """ Toujours joignable : bulle affichée et opérateur trouvé hors ligne,
    sans rien changer quand un opérateur est en ligne. """

    def _init_livechat(self):
        """ Ce que le navigateur du visiteur reçoit pour décider d'afficher
        la bulle. """
        result = self.make_jsonrpc_request('/mail/data', {
            'fetch_params': [['init_livechat', self.livechat_channel.id]],
        })
        return result['Store']['livechat_available']

    # Disponibilité -------------------------------------------------------

    def test_available_with_every_operator_offline(self):
        self.assertFalse(self.livechat_channel.available_operator_ids,
                         "Le natif ne voit toujours aucun opérateur en ligne.")
        self.assertTrue(self.livechat_channel._is_livechat_available())
        self.assertTrue(self._init_livechat())
        self.assertIn('can_load_livechat: true', self.url_open('/').text)

    def test_not_available_when_setting_off(self):
        self.livechat_channel.aite_always_available = False
        self.assertFalse(self.livechat_channel._is_livechat_available())
        self.assertFalse(self._init_livechat())
        self.assertIn('can_load_livechat: false', self.url_open('/').text)

    def test_not_available_without_an_active_internal_operator(self):
        portal = self.env['res.users'].create({
            'name': "Client portail", 'login': 'aite_lc_portal',
            'group_ids': [Command.set(self.env.ref('base.group_portal').ids)],
        })
        self.livechat_channel.user_ids = portal
        self.assertFalse(self.livechat_channel._is_livechat_available())
        self.livechat_channel.user_ids = self.operator
        self.operator.active = False
        self.assertFalse(self.livechat_channel._is_livechat_available())

    def test_hide_rule_still_hides_the_bubble(self):
        self.livechat_channel.rule_ids.action = 'hide_button'
        self.assertFalse(self._init_livechat())

    def test_native_availability_unchanged_when_operator_online(self):
        self.livechat_channel.aite_always_available = False
        self._set_online(self.operator)
        self.assertEqual(self.livechat_channel.available_operator_ids, self.operator)
        self.assertTrue(self.livechat_channel._is_livechat_available())
        self.assertTrue(self._init_livechat())

    def test_existing_channels_keep_native_behaviour(self):
        # Le canal créé par Odoo avant l'installation du module garde ses
        # cases décochées ; un canal créé ensuite les a cochées.
        native = self.env.ref('im_livechat.im_livechat_channel_data')
        self.assertFalse(native.aite_always_available)
        self.assertFalse(native.aite_email_reply)
        new_channel = self.env['im_livechat.channel'].create({'name': "Nouveau canal"})
        self.assertTrue(new_channel.aite_always_available)
        self.assertTrue(new_channel.aite_email_reply)
        self.assertIn("Nous ne sommes pas en ligne", new_channel.aite_away_message)

    # Choix de l'opérateur ---------------------------------------------------

    def test_offline_operator_chosen(self):
        self.assertEqual(self.livechat_channel._get_operator(), self.operator)
        self.livechat_channel.aite_always_available = False
        self.assertFalse(self.livechat_channel._get_operator())

    def test_online_operator_preferred(self):
        self.livechat_channel.user_ids = self.operator | self.operator_2
        self._set_online(self.operator_2)
        for _attempt in range(5):
            self.assertEqual(self.livechat_channel._get_operator(), self.operator_2)

    def test_previous_operator_kept(self):
        self.livechat_channel.user_ids = self.operator | self.operator_2
        for _attempt in range(5):
            self.assertEqual(
                self.livechat_channel._get_operator(previous_operator_id=self.operator_2.partner_id.id),
                self.operator_2,
            )

    def test_language_preference_kept(self):
        self.env['res.lang']._activate_lang('fr_FR')
        self.operator.partner_id.lang = 'en_US'
        self.operator_2.partner_id.lang = 'fr_FR'
        self.livechat_channel.user_ids = self.operator | self.operator_2
        for _attempt in range(5):
            self.assertEqual(self.livechat_channel._get_operator(lang='fr_FR'), self.operator_2)

    def test_explicit_candidates_respected(self):
        # Liste de candidats fournie par l'appelant (crm_livechat…) : pas
        # de repli sur les opérateurs hors ligne.
        self.assertFalse(self.livechat_channel._get_operator(users=self.env['res.users']))

    def test_session_created_with_offline_operator(self):
        channel = self._start_session()
        self.assertEqual(channel.livechat_operator_id, self.operator.partner_id)
        agent = channel.channel_member_ids.filtered(lambda member: member.livechat_member_type == 'agent')
        self.assertEqual(agent.partner_id, self.operator.partner_id)
        self.assertTrue(self._visitor_guest(channel))
