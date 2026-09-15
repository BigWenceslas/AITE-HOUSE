# -*- coding: utf-8 -*-
"""Assistant de (re)génération du jeu d'essai, depuis l'interface."""
from odoo import api, fields, models, _


class AiteDemoGenerateWizard(models.TransientModel):
    """
    Relance la génération du jeu opérationnel sans passer par le shell.

    Utile pour rafraîchir une base de démonstration vieillissante : les
    ardoises, tâches de gouvernante et achats sont datés **relativement
    à aujourd'hui**, donc régénérer les ramène dans la période affichée
    par les tableaux de bord.
    """
    _name = 'aite.demo.generate.wizard'
    _description = "Assistant — (re)générer le jeu d'essai"

    scale = fields.Selection(
        selection=[
            ('small', "Léger — démonstration rapide"),
            ('normal', "Standard — atelier client"),
            ('large', "Étendu — test de charge"),
        ],
        string="Volume", default='normal', required=True,
    )
    purge_first = fields.Boolean(
        string="Purger l'existant d'abord", default=False,
        help="Retire les enregistrements déjà générés (repérés « [démo] ») "
             "avant d'en produire de nouveaux. Le référentiel posé à "
             "l'installation n'est pas touché.",
    )
    result = fields.Text(string="Résultat", readonly=True)

    def action_generate(self):
        self.ensure_one()
        generator = self.env['aite.demo.generator']
        lines = []
        if self.purge_first:
            purged = generator.purge_generated()
            lines.append(_("Purgé : %s",
                           ", ".join("%s=%s" % (k, v)
                                     for k, v in sorted(purged.items()))))
        created = generator.generate_all(scale=self.scale)
        lines.append(_("Créé : %s",
                       ", ".join("%s=%s" % (k, v)
                                 for k, v in sorted(created.items()))))
        self.result = "\n".join(lines)
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_purge(self):
        self.ensure_one()
        purged = self.env['aite.demo.generator'].purge_generated()
        self.result = _("Purgé : %s",
                        ", ".join("%s=%s" % (k, v)
                                  for k, v in sorted(purged.items())))
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }
