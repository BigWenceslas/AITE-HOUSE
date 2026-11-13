# -*- coding: utf-8 -*-
from odoo import Command
from odoo.tests import HttpCase, new_test_user

AWAY_TEXT = "Nous ne sommes pas en ligne pour le moment"


class AiteLivechatCommon(HttpCase):
    """ Un canal toujours joignable, rattaché au site, avec une opératrice
    hors ligne (aucune présence enregistrée). """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.website = cls.env.ref('website.default_website')
        cls.company = cls.website.company_id
        cls.company.write({'name': "AITE Consulting (test)", 'email': 'contact@aite.example.com'})
        cls.operator = new_test_user(
            cls.env, login='aite_lc_awa', name="Awa Opératrice", email='awa@aite.example.com',
            groups='base.group_user,im_livechat.im_livechat_group_user',
        )
        cls.operator_2 = new_test_user(
            cls.env, login='aite_lc_paul', name="Paul Opérateur", email='paul@aite.example.com',
            groups='base.group_user,im_livechat.im_livechat_group_user',
        )
        cls.livechat_channel = cls.env['im_livechat.channel'].create({
            'name': "Chat du site (test)",
            'user_ids': [Command.set(cls.operator.ids)],
            'rule_ids': [Command.create({'action': 'display_button'})],
            'aite_always_available': True,
            'aite_email_reply': True,
        })
        cls.website.channel_id = cls.livechat_channel

    # Présence ----------------------------------------------------------

    def _set_online(self, user_or_guest):
        self.env['mail.presence']._update_presence(user_or_guest)

    def _set_offline(self, user_or_guest):
        user_or_guest.sudo().presence_ids.status = 'offline'

    # Conversation, côté visiteur (requêtes HTTP réelles, invité public) --

    def _start_session(self, **params):
        data = self.make_jsonrpc_request('/im_livechat/get_session', {
            'channel_id': self.livechat_channel.id,
            'persisted': True,
            **params,
        })
        self.env.invalidate_all()
        return self.env['discuss.channel'].browse(data['channel_id'])

    def _visitor_post(self, channel, body):
        data = self.make_jsonrpc_request('/mail/message/post', {
            'thread_model': 'discuss.channel',
            'thread_id': channel.id,
            'post_data': {
                'body': body,
                'message_type': 'comment',
                'subtype_xmlid': 'mail.mt_comment',
            },
        })
        self.env.invalidate_all()
        return data

    def _operator_post(self, channel, body, operator=None):
        message = channel.with_user(operator or self.operator).message_post(
            body=body, message_type='comment', subtype_xmlid='mail.mt_comment')
        self.env.invalidate_all()
        return message

    # Lecture -------------------------------------------------------------

    def _visitor_guest(self, channel):
        return channel.livechat_customer_history_ids.guest_id

    def _away_messages(self, channel):
        return channel.message_ids.filtered(lambda message: message.message_type == 'auto_comment')

    def _mails_to(self, email):
        return self.env['mail.mail'].sudo().search([('email_to', '=', email)])
