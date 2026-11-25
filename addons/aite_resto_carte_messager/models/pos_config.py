# -*- coding: utf-8 -*-
import logging

from odoo import _, api, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class PosConfig(models.Model):
    _inherit = 'pos.config'

    @api.model
    def _aite_poser_carte_messager(self):
        """Pose la carte dans chaque société qui a un plan comptable ; rend une
        ligne de bilan par société (aussi écrite dans le journal du serveur)."""
        from odoo.addons.aite_resto_carte_messager import caisse_restaurant, jouer_carte
        bilans = []
        for company in self.env['res.company'].sudo().search([]):
            env = self.env(context=dict(self.env.context, allowed_company_ids=[company.id]),
                           su=True)
            if not company.chart_template:
                bilan = _("%s : pas encore de plan comptable — la carte sera posée juste après "
                          "son chargement.", company.name)
            elif not caisse_restaurant(env, company):
                bilan = _("%s : aucune caisse au service à table contrôlé — la carte n'est pas "
                          "posée.", company.name)
            else:
                # Un refus (la base a déjà une autre carte) ne doit jamais bloquer
                # l'installation ni la mise à niveau des modules : rien n'est posé
                # pour cette société (retour au point de sauvegarde), le bilan dit pourquoi.
                try:
                    with self.env.cr.savepoint():
                        bilan = "%s : %s" % (company.name, jouer_carte(env))
                except UserError as refus:
                    bilan = "%s : %s" % (company.name, refus.args[0])
                    _logger.warning("Carte Le Messager — %s", bilan)
                    bilans.append(bilan)
                    continue
            _logger.info("Carte Le Messager — %s", bilan)
            bilans.append(bilan)
        return bilans

    @api.model
    def _aite_action_poser_carte_messager(self):
        """Le bouton du menu : pose (ou remet à jour) la carte et dit ce qui s'est passé."""
        bilans = self._aite_poser_carte_messager()
        return {
            'type': 'ir.actions.client', 'tag': 'display_notification',
            'params': {'title': _("Carte Le Messager"), 'message': "\n".join(bilans),
                       'sticky': True, 'type': 'info'},
        }
