# -*- coding: utf-8 -*-
"""Le français activé après l'installation (vérification finale du lot 1)."""
from odoo import models


class IrModuleModule(models.Model):
    _inherit = 'ir.module.module'

    def _load_module_terms(self, modules, langs, overwrite=False, imported_module=False):
        """Au chargement des traductions françaises (Paramètres → Langues,
        ou mise à niveau), les modes d'espèces nommés « Cash » reçoivent leur
        nom français « Espèces » (pos.config._aite_traduire_especes) : une
        base créée en anglais puis passée au français n'affiche pas « Cash »
        sur le bouton de paiement."""
        super()._load_module_terms(modules, langs, overwrite=overwrite,
                                   imported_module=imported_module)
        if 'aite_pos_restaurant' in modules and 'fr_FR' in langs:
            self.env['pos.config']._aite_traduire_especes()
