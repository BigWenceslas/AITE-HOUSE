# -*- coding: utf-8 -*-
from odoo import fields, models, _
from odoo.exceptions import UserError


class LoyaltyAdjustWizard(models.TransientModel):
    """
    Ajustement manuel de points (geste commercial, correction) —
    réservé aux responsables, historisé dans le grand livre comme tout
    autre mouvement (origine « Ajustement manuel »).
    """
    _name = 'aite.loyalty.adjust.wizard'
    _description = "Ajustement manuel de points"

    partner_id = fields.Many2one(
        'res.partner', string="Client", required=True)
    points = fields.Integer(
        string="Points (±)", required=True,
        help="Positif pour créditer, négatif pour retirer.")
    note = fields.Char(string="Motif", required=True)

    def action_apply(self):
        self.ensure_one()
        if not self.points:
            raise UserError(_("Le nombre de points ne peut pas être nul."))
        if (self.partner_id.loyalty_points + self.points) < 0:
            raise UserError(_(
                "Le solde de %(p)s ne peut pas devenir négatif "
                "(actuel : %(s)s).",
                p=self.partner_id.name, s=self.partner_id.loyalty_points))
        self.env['aite.loyalty.move'].create({
            'partner_id': self.partner_id.id,
            'points': self.points,
            'origin_detail': 'manual',
            'ref': _("Ajustement"),
            'note': self.note,
        })
        return {'type': 'ir.actions.act_window_close'}
