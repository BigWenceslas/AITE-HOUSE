# -*- coding: utf-8 -*-
from odoo import Command, api, models

LIVECHAT_CHANNEL_NAME = "Chat du site"
LIVECHAT_BUTTON_TEXT = "Une question ? Écrivez-nous"
LIVECHAT_WELCOME_MESSAGE = "Bonjour 👋 Comment pouvons-nous vous aider ?"


class Website(models.Model):
    _inherit = 'website'

    def _aite_has_livechat_channel(self):
        """ Le site a déjà son chat. Le canal de démonstration d'Odoo, qui
        n'a aucun opérateur capable de répondre et n'a jamais servi, ne
        compte pas : il est laissé tel quel, mais remplacé sur le site. """
        self.ensure_one()
        channel = self.channel_id
        return bool(channel) and not channel.sudo()._aite_is_untouched_default()

    @api.model
    def _aite_livechat_channel_values(self):
        admin = self.env.ref('base.user_admin', raise_if_not_found=False)
        operators = admin if admin and admin.active and admin._is_internal() else self.env['res.users']
        return {
            'name': LIVECHAT_CHANNEL_NAME,
            'button_text': LIVECHAT_BUTTON_TEXT,
            'default_message': LIVECHAT_WELCOME_MESSAGE,
            'user_ids': [Command.set(operators.ids)],
            # Une règle « Afficher », sans adresse : toutes les pages.
            'rule_ids': [Command.create({'action': 'display_button', 'regex_url': False})],
            'aite_always_available': True,
            'aite_email_reply': True,
        }

    @api.model
    def _aite_setup_livechat_channel(self):
        """ Installation : crée le canal « Chat du site » et le rattache à
        chaque site qui n'a pas encore de chat. Les canaux existants ne sont
        jamais modifiés. """
        websites = self.sudo().search([]).filtered(lambda website: not website._aite_has_livechat_channel())
        if not websites:
            return self.env['im_livechat.channel']
        channel = self.env['im_livechat.channel'].sudo().create(self._aite_livechat_channel_values())
        websites.channel_id = channel
        return channel
