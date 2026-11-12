# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # Champs liés au site choisi en tête de l'écran Paramètres, comme les
    # réglages standards du module Site web. Le message et l'accroche sont
    # traduisibles côté site, mais pas ici : la saisie s'enregistre dans la
    # langue de l'utilisateur (un écran de réglages n'a pas de traductions
    # propres).
    aite_whatsapp_enabled = fields.Boolean(
        related='website_id.aite_whatsapp_enabled', readonly=False)
    aite_whatsapp_number = fields.Char(
        related='website_id.aite_whatsapp_number', readonly=False)
    aite_whatsapp_message = fields.Char(
        related='website_id.aite_whatsapp_message', readonly=False,
        translate=False)
    aite_whatsapp_label = fields.Char(
        related='website_id.aite_whatsapp_label', readonly=False,
        translate=False)
    aite_whatsapp_position = fields.Selection(
        related='website_id.aite_whatsapp_position', readonly=False)
    aite_whatsapp_url = fields.Char(
        related='website_id.aite_whatsapp_url')
