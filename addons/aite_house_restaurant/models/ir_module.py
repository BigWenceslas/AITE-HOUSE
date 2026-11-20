# -*- coding: utf-8 -*-
"""Installe les modules optionnels du restaurant quand le serveur les a
(Odoo Enterprise) : l'écran de cuisine. Appelé à l'installation et à chaque
mise à niveau (data/installer_data.xml) ; Odoo installe dans la même passe
les modules marqués « à installer »."""
import logging

from odoo import api, models

_logger = logging.getLogger(__name__)

# L'écran de cuisine (« Preparation Display ») : module d'Odoo Enterprise.
OPTIONNELS_RESTAURANT = ['pos_preparation_display', 'pos_restaurant_preparation_display', 'pos_hr_preparation_display']


class IrModuleModule(models.Model):
    _inherit = 'ir.module.module'

    @api.model
    def _aite_restaurant_installer_optionnels(self):
        modules = self.sudo().search([('name', 'in', OPTIONNELS_RESTAURANT), ('state', '=', 'uninstalled')])
        modules = modules.filtered(lambda m: m.get_module_info(m.name).get('installable', True))
        if modules:
            _logger.info("AITE HOUSE Restaurant : installation de %s", ", ".join(modules.mapped('name')))
            modules.button_install()
        else:
            _logger.info("AITE HOUSE Restaurant : aucun module optionnel à installer "
                         "(écran de cuisine absent du serveur ou déjà installé)")
