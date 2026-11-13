# -*- coding: utf-8 -*-
from odoo import Command
from odoo.tests import tagged
from odoo.tools import SQL

from .common import AWAY_TEXT, AiteLivechatCommon


@tagged('post_install', '-at_install', 'aite_website_livechat')
class TestLivechatAwayMessage(AiteLivechatCommon):
    """ Premier message du visiteur : l'opérateur hors ligne le reçoit (Discuss,
    push), et le visiteur reçoit une seule réponse automatique. """

    def setUp(self):
        super().setUp()
        # Destinataires réels des notifications push, message par message.
        self.web_push_recipients = []
        DiscussChannel = type(self.env['discuss.channel'])
        original = DiscussChannel._notify_thread_by_web_push
        test = self

        def _notify_thread_by_web_push(channel, message, recipients_data, msg_vals=False, **kwargs):
            test.web_push_recipients.append((message.id, [
                recipient['id'] for recipient in recipients_data if recipient['notif'] == 'web_push'
            ]))
            return original(channel, message, recipients_data, msg_vals=msg_vals, **kwargs)

        self.patch(DiscussChannel, '_notify_thread_by_web_push', _notify_thread_by_web_push)

    def _push_recipients(self, message):
        return [pid for message_id, pids in self.web_push_recipients if message_id == message.id for pid in pids]

    def test_offline_operator_notified_and_away_message_once(self):
        channel = self._start_session()
        data = self._visitor_post(channel, "Bonjour, j'ai une question sur vos tarifs.")
        visitor_message = self.env['mail.message'].browse(data['message_id'])

        # L'opératrice, hors ligne, est membre de la conversation, la voit
        # dans Discuss et reçoit le push du premier message du visiteur.
        agent = channel.channel_member_ids.filtered(lambda member: member.partner_id == self.operator.partner_id)
        self.assertEqual(agent.livechat_member_type, 'agent')
        self.assertTrue(agent.is_pinned, "La conversation doit apparaître dans Discuss.")
        self.assertIn(self.operator.partner_id.id, self._push_recipients(visitor_message))
        self.assertIn(channel, self.env['discuss.channel'].with_user(self.operator).search(
            [('is_member', '=', True), ('channel_type', '=', 'livechat')]))

        # Une réponse automatique, signée de l'opératrice, sans push.
        away = self._away_messages(channel)
        self.assertEqual(len(away), 1)
        self.assertEqual(away.author_id, self.operator.partner_id)
        self.assertIn(AWAY_TEXT, away.body)
        self.assertEqual(self._push_recipients(away), [])
        self.assertFalse(channel._notify_get_recipients(away, {}))
        # Renvoyée avec le message du visiteur : affichée aussitôt.
        self.assertIn(away.id, [message['id'] for message in data['store_data']['mail.message']])

        # Pas une réponse de l'opératrice : statistiques du Live Chat intactes.
        self.assertEqual(channel.livechat_failure, 'no_answer')
        agent_history = channel.livechat_agent_history_ids
        self.assertEqual(agent_history.message_count, 0)
        self.assertFalse(agent_history.response_time_hour)
        # … ni un message qu'elle aurait encore à lire : un message du
        # visiteur, un non lu.
        self.assertEqual(agent.message_unread_counter, 1)

        # Jamais deux fois dans la même conversation.
        self._visitor_post(channel, "Vous êtes là ?")
        self.assertEqual(len(self._away_messages(channel)), 1)

    def test_no_away_message_when_operator_online(self):
        self._set_online(self.operator)
        channel = self._start_session()
        self._visitor_post(channel, "Bonjour !")
        self.assertFalse(self._away_messages(channel))
        self.assertTrue(channel.aite_away_checked)
        # Elle se déconnecte ensuite : ce n'est plus le premier message.
        self._set_offline(self.operator)
        self._visitor_post(channel, "Toujours là ?")
        self.assertFalse(self._away_messages(channel))

    def test_do_not_disturb_counts_as_not_online(self):
        self._set_online(self.operator)
        self.operator.manual_im_status = 'busy'
        channel = self._start_session()
        self._visitor_post(channel, "Bonjour !")
        self.assertEqual(len(self._away_messages(channel)), 1)

    def test_no_away_message_when_empty_or_setting_off(self):
        self.livechat_channel.aite_away_message = False
        channel = self._start_session()
        self._visitor_post(channel, "Bonjour !")
        self.assertFalse(self._away_messages(channel))

        # Canal sans « Toujours joignable », opératrice partie entre
        # l'ouverture et le premier message : comportement natif.
        self.livechat_channel.write({
            'aite_always_available': False,
            'aite_away_message': "Absent",
        })
        self._set_online(self.operator)
        self.opener.cookies.clear()
        channel = self._start_session()
        self._set_offline(self.operator)
        self._visitor_post(channel, "Bonjour !")
        self.assertFalse(self._away_messages(channel))

    def test_away_message_not_an_answer_in_report(self):
        # Live Chat → Rapports → Sessions : pas de « première réponse » tant
        # que l'opératrice n'a pas répondu, le message d'absence n'est pas
        # compté.
        channel = self._start_session()
        self._visitor_post(channel, "Bonjour, j'ai une question.")
        self.assertEqual(len(self._away_messages(channel)), 1)
        # Lu en SQL : un délai vide (NULL) se distingue d'un délai nul.
        self.assertEqual(self._report_row(channel), {'time_to_answer': None, 'nbr_message': 1})

        self._operator_post(channel, "Bonjour, voici la réponse.")
        row = self._report_row(channel)
        self.assertIsNotNone(row['time_to_answer'])
        self.assertEqual(row['nbr_message'], 2)

    def _report_row(self, channel):
        Report = self.env['im_livechat.report.channel']
        self.env.flush_all()
        self.env.cr.execute(SQL(
            "SELECT report.time_to_answer, report.nbr_message FROM (%s) AS report WHERE report.channel_id = %s",
            Report._table_query, channel.id,
        ))
        rows = self.env.cr.dictfetchall()
        self.assertEqual(len(rows), 1)
        return rows[0]

    def test_contact_request_skipped_when_contact_already_given(self):
        # Le visiteur donne son e-mail dès le premier message : la dernière
        # phrase (« indiquez-nous votre adresse e-mail… ») n'est pas envoyée.
        channel = self._start_session()
        self._visitor_post(channel, "Bonjour, je voudrais un devis. Mon e-mail : visiteur.devis@exemple.cm")
        away = self._away_messages(channel)
        self.assertIn(AWAY_TEXT, away.body)
        self.assertNotIn("indiquez-nous", away.body)

        # Sans coordonnées : le message complet.
        self.opener.cookies.clear()
        channel = self._start_session()
        self._visitor_post(channel, "Bonjour, je voudrais un devis.")
        self.assertIn("indiquez-nous votre adresse e-mail", self._away_messages(channel).body)

        # Un message personnalisé est envoyé tel quel.
        self.livechat_channel.aite_away_message = "Absents jusqu'à lundi. Laissez-nous votre e-mail."
        self.opener.cookies.clear()
        channel = self._start_session()
        self._visitor_post(channel, "Mon e-mail : autre.visiteur@exemple.cm")
        self.assertIn("Laissez-nous votre e-mail.", self._away_messages(channel).body)

    def test_away_message_in_visitor_language(self):
        self.env['res.lang']._activate_lang('en_US')
        self.env['res.lang']._activate_lang('fr_FR')
        self.livechat_channel.with_context(lang='en_US').aite_away_message = "We are offline."
        self.livechat_channel.with_context(lang='fr_FR').aite_away_message = "Nous sommes absents."
        self.env.flush_all()
        # Le navigateur du visiteur consulte le site en anglais.
        data = self.make_jsonrpc_request(
            '/im_livechat/get_session',
            {'channel_id': self.livechat_channel.id, 'persisted': True},
            cookies={'frontend_lang': 'en_US'},
        )
        self.env.invalidate_all()
        channel = self.env['discuss.channel'].browse(data['channel_id'])
        self.assertEqual(channel.livechat_lang_id.code, 'en_US')
        self._visitor_post(channel, "Hello!")
        self.assertIn("We are offline.", self._away_messages(channel).body)


@tagged('post_install', '-at_install', 'aite_website_livechat')
class TestLivechatChatbotForward(AiteLivechatCommon):
    """ Un chatbot passe la main à un humain alors que personne n'est en
    ligne : la conversation est confiée à un opérateur hors ligne. """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.chatbot = cls.env['chatbot.script'].create({
            'title': "Assistant AITE",
            'script_step_ids': [
                Command.create({'step_type': 'free_input_single', 'message': "Quelle est votre question ?"}),
                Command.create({'step_type': 'forward_operator', 'message': "Je vous passe un conseiller."}),
            ],
        })
        cls.livechat_channel.rule_ids = [Command.clear(), Command.create({
            'action': 'display_button',
            'chatbot_script_id': cls.chatbot.id,
        })]

    def test_forward_to_offline_operator(self):
        channel = self._start_session(chatbot_script_id=self.chatbot.id)
        self.assertEqual(channel.livechat_operator_id, self.chatbot.operator_partner_id)
        self._visitor_post(channel, "Je voudrais un devis.")
        self.make_jsonrpc_request('/chatbot/step/trigger', {'channel_id': channel.id})
        self.env.invalidate_all()

        self.assertEqual(channel.livechat_operator_id, self.operator.partner_id)
        self.assertIn(self.operator.partner_id, channel.channel_member_ids.partner_id)
        # Opératrice hors ligne : le visiteur en est averti tout de suite,
        # une seule fois.
        self.assertEqual(len(self._away_messages(channel)), 1)
        self._visitor_post(channel, "Merci.")
        self.assertEqual(len(self._away_messages(channel)), 1)

    def test_forward_without_always_available_stays_native(self):
        self.livechat_channel.aite_always_available = False
        channel = self._start_session(chatbot_script_id=self.chatbot.id)
        self._visitor_post(channel, "Je voudrais un devis.")
        self.make_jsonrpc_request('/chatbot/step/trigger', {'channel_id': channel.id})
        self.env.invalidate_all()
        self.assertEqual(channel.livechat_operator_id, self.chatbot.operator_partner_id)
        self.assertEqual(channel.livechat_failure, 'no_agent')
        self.assertFalse(self._away_messages(channel))
