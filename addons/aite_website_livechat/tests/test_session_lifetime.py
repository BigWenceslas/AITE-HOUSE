# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import fields
from odoo.tests import tagged

from .common import AiteLivechatCommon

VISITOR_EMAIL = 'parti.vendredi@exemple.cm'


@tagged('post_install', '-at_install', 'aite_website_livechat')
class TestLivechatSessionLifetime(AiteLivechatCommon):
    """ Une conversation qui attend la réponse d'un opérateur n'est pas close
    trop tôt : ni quand le visiteur ferme le chat, ni par le nettoyage
    quotidien d'Odoo. """

    def _visitor_leaves(self, channel):
        self.make_jsonrpc_request('/im_livechat/visitor_leave_session', {'channel_id': channel.id})
        self.env.invalidate_all()

    def _member(self, channel, member_type):
        return channel.channel_member_ids.filtered(lambda member: member.livechat_member_type == member_type)

    def _idle_since(self, member, delay):
        """ Le membre a tout lu, puis n'est plus revenu depuis `delay`. """
        last_message = member.channel_id.message_ids[:1]
        member.sudo().write({
            'seen_message_id': last_message.id,
            'new_message_separator': last_message.id + 1,
            'last_seen_dt': fields.Datetime.now() - delay,
        })
        self.assertEqual(member.message_unread_counter, 0)

    def _run_daily_cleanup(self):
        self.env['discuss.channel.member']._gc_unpin_livechat_sessions()
        self.env.invalidate_all()

    # Le visiteur ferme le chat ---------------------------------------------

    def test_visitor_closes_chat_before_any_answer(self):
        # Vendredi soir : le visiteur écrit, lit le message d'absence et ferme
        # la fenêtre du chat.
        channel = self._start_session()
        self._visitor_post(channel, f"Bonjour, un devis svp. Mon e-mail : {VISITOR_EMAIL}")
        self._visitor_leaves(channel)

        # La conversation reste ouverte : l'opératrice peut toujours répondre.
        self.assertFalse(channel.livechat_end_dt)
        self.assertTrue(channel.aite_visitor_left_dt)
        notification = channel.message_ids.filtered(lambda message: message.message_type == 'notification')[:1]
        self.assertIn("quitté la conversation", notification.body)
        self.assertIn("envoyée par e-mail", notification.body)

        # Lundi : elle répond. Le visiteur, même revenu sur le site (en
        # ligne), a fermé le chat : la réponse part par e-mail.
        self._set_online(self._visitor_guest(channel))
        self._operator_post(channel, "Bonjour, voici votre devis.")
        mail = self._mails_to(VISITOR_EMAIL)
        self.assertEqual(len(mail), 1)
        self.assertIn("voici votre devis", mail.body_html)
        self.assertIn("répondez simplement à cet e-mail", mail.body_html)

        # Il réécrit dans la conversation (autre onglet) : il est revenu, et
        # l'e-mail pas encore parti est annulé.
        self._visitor_post(channel, "Merci, bien reçu.")
        self.assertFalse(channel.aite_visitor_left_dt)
        self.assertFalse(self._mails_to(VISITOR_EMAIL))

    def test_visitor_closes_chat_without_email(self):
        channel = self._start_session()
        self._visitor_post(channel, "Bonjour, une question.")
        self._visitor_leaves(channel)
        self.assertFalse(channel.livechat_end_dt)
        notification = channel.message_ids.filtered(lambda message: message.message_type == 'notification')[:1]
        self.assertIn("sans laisser d'adresse e-mail", notification.body)

    def test_visitor_closes_answered_chat_natively(self):
        # Réponse déjà donnée : fermer le chat termine la conversation,
        # comme dans Odoo.
        channel = self._start_session()
        self._visitor_post(channel, "Bonjour")
        self._operator_post(channel, "Bonjour, que puis-je pour vous ?")
        self._visitor_leaves(channel)
        self.assertTrue(channel.livechat_end_dt)
        self.assertFalse(channel.aite_visitor_left_dt)

    def test_visitor_closes_chat_natively_without_always_available(self):
        self.livechat_channel.aite_always_available = False
        self._set_online(self.operator)
        channel = self._start_session()
        self._visitor_post(channel, "Bonjour")
        self._visitor_leaves(channel)
        self.assertTrue(channel.livechat_end_dt)

    # Nettoyage quotidien d'Odoo ---------------------------------------------

    def test_daily_cleanup_keeps_a_session_waiting_for_an_answer(self):
        channel = self._start_session()
        self._visitor_post(channel, "Bonjour, une question.")
        self._idle_since(self._member(channel, 'visitor'), timedelta(days=1, hours=1))
        self._run_daily_cleanup()
        self.assertFalse(channel.livechat_end_dt, "Sans réponse : la conversation reste ouverte.")

        # Au-delà de 7 jours sans le moindre message : règle d'Odoo.
        channel.sudo().last_interest_dt = fields.Datetime.now() - timedelta(days=8)
        self._run_daily_cleanup()
        self.assertTrue(channel.livechat_end_dt)

    def test_daily_cleanup_keeps_an_answer_the_visitor_has_not_seen(self):
        channel = self._start_session()
        self._visitor_post(channel, f"Bonjour, mon e-mail : {VISITOR_EMAIL}")
        self._operator_post(channel, "Bonjour, voici la réponse.")
        self._idle_since(self._member(channel, 'agent'), timedelta(days=1, hours=1))
        self._run_daily_cleanup()
        self.assertFalse(channel.livechat_end_dt, "Le visiteur peut encore revenir lire la réponse.")

        # Il l'a lue, puis plus rien depuis un jour : règle d'Odoo.
        self._idle_since(self._member(channel, 'visitor'), timedelta(days=1, hours=1))
        self._run_daily_cleanup()
        self.assertTrue(channel.livechat_end_dt)

    def test_daily_cleanup_native_without_always_available(self):
        self.livechat_channel.aite_always_available = False
        self._set_online(self.operator)
        channel = self._start_session()
        self._visitor_post(channel, "Bonjour, une question.")
        self._idle_since(self._member(channel, 'visitor'), timedelta(days=1, hours=1))
        self._run_daily_cleanup()
        self.assertTrue(channel.livechat_end_dt)
