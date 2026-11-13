# -*- coding: utf-8 -*-
import logging

from odoo import Command, api, models

_logger = logging.getLogger(__name__)

# Canal « Chat du site » créé par le module. Noté dans un paramètre système,
# qui survit à la désinstallation : une réinstallation retrouve le canal et
# recoche ses options (les colonnes du module ont été supprimées entre-temps).
CREATED_CHANNEL_PARAM = 'aite_website_livechat.created_channel_id'

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
    def _aite_default_livechat_operator(self):
        """ Opérateur du canal créé : l'administrateur ; s'il est archivé, le
        premier responsable du Live Chat, à défaut le premier administrateur
        (Paramètres) encore actif. """
        Users = self.env['res.users'].sudo()
        admin = self.env.ref('base.user_admin', raise_if_not_found=False)
        if admin and admin.active and admin._is_internal():
            return admin
        for group_xmlid in ('im_livechat.im_livechat_group_manager', 'base.group_system'):
            group = self.env.ref(group_xmlid, raise_if_not_found=False)
            if not group:
                continue
            users = Users.search([('group_ids', 'in', group.ids), ('share', '=', False)], order='id')
            if user := users.filtered(lambda user: user._is_internal() and not user._is_superuser())[:1]:
                return user
        return Users

    @api.model
    def _aite_livechat_channel_values(self):
        operators = self._aite_default_livechat_operator()
        if not operators:
            _logger.warning(
                "aite_website_livechat : aucun utilisateur actif pour répondre au chat du site "
                "(administrateur archivé, aucun responsable du Live Chat). Ajoutez un opérateur : "
                "Site Web → Configuration → Paramètres → Live Chat → Opérateurs du chat → Agents.")
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
        jamais modifiés, sauf le « Chat du site » d'une installation
        précédente, à la réinstallation. """
        self._aite_restore_created_channel()
        websites = self.sudo().search([]).filtered(lambda website: not website._aite_has_livechat_channel())
        if not websites:
            return self.env['im_livechat.channel']
        channel = self.env['im_livechat.channel'].sudo().create(self._aite_livechat_channel_values())
        websites.channel_id = channel
        self.env['ir.config_parameter'].sudo().set_param(CREATED_CHANNEL_PARAM, channel.id)
        return channel

    @api.model
    def _aite_restore_created_channel(self):
        """ Réinstallation : le canal « Chat du site » créé lors d'une
        installation précédente retrouve « Toujours joignable » et « Réponse
        par e-mail ». Les autres canaux ne sont pas touchés. """
        channel_id = self.env['ir.config_parameter'].sudo().get_param(CREATED_CHANNEL_PARAM)
        if not channel_id or not channel_id.isdigit():
            return
        channel = self.env['im_livechat.channel'].sudo().browse(int(channel_id)).exists()
        if channel and not channel.aite_always_available and not channel.aite_email_reply:
            channel.write({'aite_always_available': True, 'aite_email_reply': True})
