# -*- coding: utf-8 -*-
"""Base neuve installée d'un seul geste : Odoo charge le plan comptable après
les données des modules, et aite_pos_restaurant crée la caisse « Restaurant »
juste après ce premier chargement. Le mode « Ardoise client » (créé par
aite_pos_credit à son installation) lui est ajouté ici, aussitôt.

Seulement au premier chargement du plan de la société, et sans créer de mode :
une société créée plus tard reçoit son mode d'ardoise à la mise à niveau du
module (pos_config.py)."""
import logging

from odoo import models

_logger = logging.getLogger(__name__)


class AccountChartTemplate(models.AbstractModel):
    _inherit = 'account.chart.template'

    def _load(self, template_code, company, install_demo, force_create=True):
        company = company or self.env.company
        premier_chargement = not company.chart_template
        res = super()._load(template_code, company, install_demo, force_create)
        if premier_chargement:
            try:
                with self.env.cr.savepoint():
                    self.env['pos.config']._aite_restaurant_ajouter_ardoise(company, creer=False)
            except Exception:
                _logger.warning("Restaurant : mode d'ardoise non ajouté à la caisse de la société %s.",
                                company.name, exc_info=True)
        return res
