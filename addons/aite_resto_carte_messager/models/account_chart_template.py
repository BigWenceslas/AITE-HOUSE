# -*- coding: utf-8 -*-
"""Base neuve installée d'un seul geste : la carte est posée juste après le
premier chargement du plan comptable (et la caisse « Restaurant » qu'il
apporte), si elle ne l'a pas encore été."""
from odoo import models


class AccountChartTemplate(models.AbstractModel):
    _inherit = 'account.chart.template'

    def _load(self, template_code, company, install_demo, force_create=True):
        res = super()._load(template_code, company, install_demo, force_create)
        company = company or self.env.company
        deja = self.env['ir.config_parameter'].sudo().get_param('aite.carte_client')
        if not deja and company == self.env.company:
            from odoo.addons.aite_resto_carte_messager import caisse_restaurant, jouer_carte
            if caisse_restaurant(self.env, company):
                jouer_carte(self.env)
        return res
