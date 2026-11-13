# -*- coding: utf-8 -*-
from odoo import Command
from odoo.exceptions import AccessError
from odoo.tests import TransactionCase, new_test_user, tagged

from .common import AiteLivechatCommon


@tagged('post_install', '-at_install', 'aite_website_livechat')
class TestLivechatSetup(TransactionCase):
    """ Installation : canal « Chat du site » créé et rattaché aux sites qui
    n'ont pas de chat, sans toucher aux canaux existants. """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Website = cls.env['website']
        cls.existing = cls.env['im_livechat.channel'].create({
            'name': "Canal existant",
            'button_text': "Texte existant",
            'aite_always_available': False,
            'aite_email_reply': False,
        })
        cls.website_with_chat = cls.Website.create({'name': "Site avec chat", 'channel_id': cls.existing.id})
        cls.websites_without_chat = cls.Website.create([{'name': "Site A"}, {'name': "Site B"}])
        # Les autres sites de la base ont déjà un chat.
        others = cls.Website.search([]) - cls.website_with_chat - cls.websites_without_chat
        others.channel_id = cls.existing

    def test_channel_created_and_attached_when_missing(self):
        channel = self.Website._aite_setup_livechat_channel()
        self.assertEqual(len(channel), 1)
        self.assertRecordValues(channel, [{
            'name': "Chat du site",
            'button_text': "Une question ? Écrivez-nous",
            'default_message': "Bonjour 👋 Comment pouvons-nous vous aider ?",
            'aite_always_available': True,
            'aite_email_reply': True,
        }])
        self.assertEqual(channel.user_ids, self.env.ref('base.user_admin'))
        self.assertEqual(channel.rule_ids.mapped('action'), ['display_button'])
        self.assertFalse(channel.rule_ids.regex_url)
        self.assertEqual(self.websites_without_chat.channel_id, channel)
        # Canal noté, pour le retrouver après une réinstallation.
        self.assertEqual(
            self.env['ir.config_parameter'].get_param('aite_website_livechat.created_channel_id'), str(channel.id))
        # Le site qui avait son chat le garde, et le canal reste inchangé.
        self.assertEqual(self.website_with_chat.channel_id, self.existing)
        self.assertRecordValues(self.existing, [{
            'name': "Canal existant",
            'button_text': "Texte existant",
            'aite_always_available': False,
            'aite_email_reply': False,
        }])
        self.assertTrue(channel._is_livechat_available())

    def test_nothing_done_when_every_website_has_a_chat(self):
        self.websites_without_chat.channel_id = self.existing
        channel_count = self.env['im_livechat.channel'].search_count([])
        self.assertFalse(self.Website._aite_setup_livechat_channel())
        self.assertEqual(self.env['im_livechat.channel'].search_count([]), channel_count)

    def test_untouched_native_demo_channel_is_replaced_on_the_website(self):
        # « YourWebsite.com », créé par Odoo sans opérateur capable de
        # répondre : le site reçoit le nouveau canal, le canal natif reste.
        native = self.env.ref('im_livechat.im_livechat_channel_data')
        native.write({'user_ids': [Command.clear()], 'rule_ids': [Command.clear()]})
        native.channel_ids.unlink()
        self.websites_without_chat.channel_id = native
        native_name = native.name
        channel = self.Website._aite_setup_livechat_channel()
        self.assertEqual(self.websites_without_chat.channel_id, channel)
        self.assertEqual(native.name, native_name)

    def test_native_demo_channel_kept_when_it_has_an_operator(self):
        native = self.env.ref('im_livechat.im_livechat_channel_data')
        native.user_ids = self.env.ref('base.user_admin')
        self.websites_without_chat.channel_id = native
        self.assertFalse(self.Website._aite_setup_livechat_channel())
        self.assertEqual(self.websites_without_chat.channel_id, native)

    def _archive_admin_and_other_managers(self):
        """ Administrateur archivé, et aucun autre utilisateur interne actif
        responsable du Live Chat ou administrateur. """
        groups = self.env.ref('im_livechat.im_livechat_group_manager') | self.env.ref('base.group_system')
        others = self.env['res.users'].search([('group_ids', 'in', groups.ids), ('share', '=', False)])
        (others - self.env.ref('base.user_root')).active = False
        self.assertFalse(self.env.ref('base.user_admin').active)

    def test_no_operator_when_admin_archived(self):
        self._archive_admin_and_other_managers()
        with self.assertLogs('odoo.addons.aite_website_livechat.models.website', level='WARNING') as logs:
            channel = self.Website._aite_setup_livechat_channel()
        self.assertIn("Ajoutez un opérateur", logs.output[0])
        self.assertFalse(channel.user_ids)
        self.assertFalse(channel._is_livechat_available())

    def test_livechat_manager_when_admin_archived(self):
        # L'administrateur générique est archivé, la direction gère le Live
        # Chat : elle devient l'opératrice du canal créé.
        self._archive_admin_and_other_managers()
        direction = new_test_user(
            self.env, login='aite_lc_direction', name="Direction",
            groups='base.group_user,base.group_system,im_livechat.im_livechat_group_manager',
        )
        channel = self.Website._aite_setup_livechat_channel()
        self.assertEqual(channel.user_ids, direction)
        self.assertTrue(channel._is_livechat_available())

    def test_reinstall_restores_the_created_channel(self):
        # Désinstallation puis réinstallation : les colonnes du module sont
        # recréées vides, le canal « Chat du site » créé auparavant retrouve
        # ses options. Les autres canaux restent tels quels.
        created = self.env['im_livechat.channel'].create({
            'name': "Chat du site", 'aite_always_available': False, 'aite_email_reply': False})
        self.env['ir.config_parameter'].set_param('aite_website_livechat.created_channel_id', created.id)
        self.websites_without_chat.channel_id = created
        self.assertFalse(self.Website._aite_setup_livechat_channel())
        self.assertRecordValues(created, [{'aite_always_available': True, 'aite_email_reply': True}])
        self.assertRecordValues(self.existing, [{'aite_always_available': False, 'aite_email_reply': False}])
        # Canal supprimé entre-temps : rien à faire.
        self.websites_without_chat.channel_id = self.existing
        created.unlink()
        self.assertFalse(self.Website._aite_setup_livechat_channel())


@tagged('post_install', '-at_install', 'aite_website_livechat')
class TestLivechatSettings(AiteLivechatCommon):
    """ Écran Paramètres et droits d'accès. """

    def test_settings_round_trip(self):
        settings = self.env['res.config.settings'].create({
            'website_id': self.website.id,
            'aite_livechat_always_available': False,
            'aite_livechat_away_message': "Absents, on revient vite.",
            'aite_livechat_email_reply': False,
        })
        settings.execute()
        self.assertRecordValues(self.livechat_channel, [{
            'aite_always_available': False,
            'aite_away_message': "Absents, on revient vite.",
            'aite_email_reply': False,
        }])
        settings = self.env['res.config.settings'].create({'website_id': self.website.id})
        self.assertFalse(settings.aite_livechat_always_available)
        self.assertEqual(settings.aite_livechat_away_message, "Absents, on revient vite.")
        settings.write({'aite_livechat_always_available': True, 'aite_livechat_email_reply': True})
        settings.execute()
        self.assertTrue(self.livechat_channel.aite_always_available)
        self.assertTrue(self.livechat_channel.aite_email_reply)

    def test_settings_open_operators(self):
        settings = self.env['res.config.settings'].create({'website_id': self.website.id})
        action = settings.action_aite_livechat_operators()
        self.assertEqual(action['res_model'], 'im_livechat.channel')
        self.assertEqual(action['res_id'], self.livechat_channel.id)

    def test_settings_view_renders(self):
        admin = self.env.ref('base.user_admin')
        arch = self.env['res.config.settings'].with_user(admin).get_views([(False, 'form')])['views']['form']['arch']
        self.assertIn('aite_livechat_always_available', arch)
        self.assertIn('action_aite_livechat_operators', arch)

    def test_visitor_cannot_read_contact_fields(self):
        channel = self._start_session()
        self._visitor_post(channel, "Mon e-mail : secret@exemple.cm, tél. +237 699 11 22 33")
        self.assertEqual(channel.aite_visitor_email, 'secret@exemple.cm')
        guest = self._visitor_guest(channel)

        # Le visiteur (invité public) ne lit pas ces champs, même pour sa
        # propre conversation.
        public_channel = channel.with_user(self.env.ref('base.public_user')).with_context(guest=guest)
        with self.assertRaises(AccessError):
            public_channel.read(['aite_visitor_email'])
        portal = new_test_user(self.env, login='aite_lc_portal_reader', groups='base.group_portal')
        with self.assertRaises(AccessError):
            channel.with_user(portal).read(['aite_visitor_phone'])

        # Les données de la conversation envoyées au navigateur du visiteur
        # ne les contiennent pas…
        result = self.make_jsonrpc_request('/mail/data', {
            'fetch_params': [['discuss.channel', [channel.id]]],
        })
        visitor_data = next(data for data in result['discuss.channel'] if data['id'] == channel.id)
        self.assertNotIn('aite_visitor_email', visitor_data)
        self.assertNotIn('aite_visitor_phone', visitor_data)

        # … et un autre visiteur n'a pas accès à cette conversation.
        self.opener.cookies.clear()
        other = self._start_session()
        self.assertNotEqual(other, channel)
        result = self.make_jsonrpc_request('/mail/data', {
            'fetch_params': [['discuss.channel', [channel.id]]],
        })
        self.assertNotIn(channel.id, [data['id'] for data in result.get('discuss.channel', [])])
        self.assertNotIn('secret@exemple.cm', str(result))

        # L'opératrice, elle, les reçoit dans Discuss.
        self.authenticate(self.operator.login, self.operator.login)
        result = self.make_jsonrpc_request('/mail/data', {
            'fetch_params': [['discuss.channel', [channel.id]]],
        })
        operator_data = next(data for data in result['discuss.channel'] if data['id'] == channel.id)
        self.assertEqual(operator_data.get('aite_visitor_email'), 'secret@exemple.cm')
        self.assertEqual(operator_data.get('aite_visitor_phone'), '+237 699 11 22 33')
