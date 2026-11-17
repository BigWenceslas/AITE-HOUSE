# -*- coding: utf-8 -*-
"""Base neuve installée d'un seul geste : Odoo charge le plan comptable après
les données des modules ; la carte est posée juste après ce premier
chargement, dans la société concernée."""
from odoo import models


class AccountChartTemplate(models.AbstractModel):
    _inherit = 'account.chart.template'

    def _load(self, template_code, company, install_demo, force_create=True):
        company = company or self.env.company
        premier = not company.chart_template
        res = super()._load(template_code, company, install_demo, force_create)
        if premier:
            from odoo.addons.aite_resto_carte_messager import caisse_restaurant, jouer_carte
            env = self.env(context=dict(self.env.context, allowed_company_ids=[company.id]), su=True)
            if caisse_restaurant(env, company):
                jouer_carte(env)
        return res
