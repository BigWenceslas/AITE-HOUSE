# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # Réglages du canal de chat du site choisi en tête de l'écran Paramètres.
    # Le message d'absence est traduisible côté canal, mais pas ici : la
    # saisie s'enregistre dans la langue de l'utilisateur (un écran de
    # réglages n'a pas de traductions propres).
    aite_livechat_always_available = fields.Boolean(
        related='website_id.channel_id.aite_always_available', readonly=False)
    aite_livechat_away_message = fields.Text(
        related='website_id.channel_id.aite_away_message', readonly=False,
        translate=False)
    aite_livechat_email_reply = fields.Boolean(
        related='website_id.channel_id.aite_email_reply', readonly=False)

    def action_aite_livechat_operators(self):
        """ Ouvre le canal de chat du site : opérateurs, textes, règles. """
        self.ensure_one()
        channel = self.website_id.channel_id
        if not channel:
            return False
        return {
            'type': 'ir.actions.act_window',
            'name': channel.display_name,
            'res_model': 'im_livechat.channel',
            'res_id': channel.id,
            'view_mode': 'form',
            'views': [(False, 'form')],
            'target': 'current',
        }
