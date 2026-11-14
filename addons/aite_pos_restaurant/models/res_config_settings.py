# -*- coding: utf-8 -*-
"""Réglages du Point de Vente : la case « Service à table contrôlé » et ce
qu'elle pose à l'écran, avant enregistrement (parties 4.3 et 4.4) ; le délai
de l'orange et le refus des produits épuisés (incrément 5)."""
from odoo import api, fields, models

from .pos_config import REGLAGES_DU_MODE, phrase_delai


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_aite_mode_restaurant = fields.Boolean(
        related='pos_config_id.aite_mode_restaurant', readonly=False)
    pos_aite_vente_sans_table = fields.Boolean(
        related='pos_config_id.aite_vente_sans_table', readonly=False)
    pos_aite_delai_alerte = fields.Integer(
        related='pos_config_id.aite_delai_alerte', readonly=False)
    pos_aite_refus_epuise = fields.Boolean(
        related='pos_config_id.aite_refus_epuise', readonly=False)
    # La phrase « ce qui va se passer » du délai : le nombre suit le réglage,
    # à l'écran, pendant que le manager le tape (partie 4.3).
    pos_aite_phrase_delai = fields.Char(
        string="Ce qui va se passer", compute='_compute_pos_aite_phrase_delai')

    @api.depends('pos_aite_delai_alerte')
    def _compute_pos_aite_phrase_delai(self):
        for reglages in self:
            reglages.pos_aite_phrase_delai = phrase_delai(reglages.pos_aite_delai_alerte)

    @api.onchange('pos_aite_mode_restaurant')
    def _onchange_pos_aite_mode_restaurant(self):
        if self.pos_aite_mode_restaurant:
            for champ, valeur in REGLAGES_DU_MODE.items():
                self['pos_' + champ] = valeur
