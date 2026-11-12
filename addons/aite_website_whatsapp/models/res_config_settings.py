# -*- coding: utf-8 -*-
from odoo import api, fields, models

# Réglages modifiables depuis l'écran Paramètres.
WHATSAPP_SETTINGS = (
    'aite_whatsapp_enabled',
    'aite_whatsapp_number',
    'aite_whatsapp_message',
    'aite_whatsapp_label',
    'aite_whatsapp_position',
)


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

    # Laissé à l'ORM, chaque champ lié serait recopié sur le site par une
    # écriture distincte, dans l'ordre de l'écran : la case « Bouton
    # WhatsApp » avant le numéro. Le contrôle du site (« activé ⇒ numéro
    # renseigné ») échouerait alors entre les deux. Les réglages WhatsApp
    # sont donc retirés des valeurs et appliqués au site en une seule
    # écriture, contrôlée sur l'état final.

    @api.model_create_multi
    def create(self, vals_list):
        vals_list = [dict(vals) for vals in vals_list]
        pending = [self._aite_whatsapp_pop(vals) for vals in vals_list]
        records = super().create(vals_list)
        for record, whatsapp_vals in zip(records, pending):
            record._aite_whatsapp_apply(whatsapp_vals)
        return records

    def write(self, vals):
        vals = dict(vals)
        whatsapp_vals = self._aite_whatsapp_pop(vals)
        result = super().write(vals)
        for record in self:
            record._aite_whatsapp_apply(whatsapp_vals)
        return result

    @api.model
    def _aite_whatsapp_pop(self, vals):
        return {name: vals.pop(name) for name in WHATSAPP_SETTINGS if name in vals}

    def _aite_whatsapp_apply(self, whatsapp_vals):
        self.ensure_one()
        website = self.website_id
        if not website or not whatsapp_vals:
            return
        # N'écrire que ce qui change : réécrire un texte traduisible à
        # l'identique, ou le vider, toucherait aussi ses autres langues.
        changed = {
            name: value for name, value in whatsapp_vals.items()
            if (website[name] or False) != (value or False)
        }
        if changed:
            website.write(changed)
