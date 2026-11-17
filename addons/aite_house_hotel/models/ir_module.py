# -*- coding: utf-8 -*-
"""Installe le planning Gantt des chambres quand le serveur est sous Odoo
Enterprise (web_gantt présent). Appelé à l'installation et à chaque mise à
niveau (data/installer_data.xml) : sur une base où le socle était déjà
installé, aite_hotel_gantt ne s'installe pas tout seul (ECARTS n° 72)."""
import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class IrModuleModule(models.Model):
    _inherit = 'ir.module.module'

    @api.model
    def _aite_hotel_installer_optionnels(self):
        Modules = self.sudo()
        if not Modules.search_count([('name', '=', 'web_gantt')]):
            _logger.info("AITE HOUSE Hôtel : web_gantt absent (Odoo Community) : "
                         "le planning Gantt n'est pas installé")
            return
        gantt = Modules.search([('name', '=', 'aite_hotel_gantt'), ('state', '=', 'uninstalled')])
        if gantt:
            _logger.info("AITE HOUSE Hôtel : installation d'aite_hotel_gantt")
            gantt.button_install()
