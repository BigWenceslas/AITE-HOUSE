# -*- coding: utf-8 -*-
"""Réglages du Point de Vente : la case « Service à table contrôlé » et ce
qu'elle pose à l'écran, avant enregistrement (parties 4.3 et 4.4)."""
from odoo import api, fields, models

from .pos_config import REGLAGES_DU_MODE


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_aite_mode_restaurant = fields.Boolean(
        related='pos_config_id.aite_mode_restaurant', readonly=False)
    pos_aite_vente_sans_table = fields.Boolean(
        related='pos_config_id.aite_vente_sans_table', readonly=False)

    @api.onchange('pos_aite_mode_restaurant')
    def _onchange_pos_aite_mode_restaurant(self):
        if self.pos_aite_mode_restaurant:
            for champ, valeur in REGLAGES_DU_MODE.items():
                self['pos_' + champ] = valeur
