# -*- coding: utf-8 -*-
from odoo import fields, models, _
from odoo.exceptions import UserError
from odoo.tools.misc import formatLang


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

    def _fmt_points(self, points, signed=False):
        """Points écrits comme à l'écran (règle 6) : « 12 500 », avec le
        séparateur de milliers de la langue, et « +50 » pour un crédit."""
        text = formatLang(self.env, points, digits=0)
        return ("+" + text) if signed and points > 0 else text

    def action_apply(self):
        self.ensure_one()
        if not self.points:
            raise UserError(_("Le nombre de points ne peut pas être nul."))
        if (self.partner_id.loyalty_points + self.points) < 0:
            raise UserError(_(
                "Le solde de %(p)s ne peut pas devenir négatif "
                "(actuel : %(s)s).",
                p=self.partner_id.name,
                s=self._fmt_points(self.partner_id.loyalty_points)))
        self.env['aite.loyalty.move'].create({
            'partner_id': self.partner_id.id,
            'points': self.points,
            'origin_detail': 'manual',
            'ref': _("Ajustement"),
            'note': self.note,
        })
        # La fenêtre se ferme en rechargeant l'écran du dessous (liste des
        # mouvements, clients VIP…) : le solde affiché n'est plus périmé.
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'type': 'success',
                'message': _(
                    "%(pts)s points pour %(p)s — nouveau solde : %(s)s.",
                    pts=self._fmt_points(self.points, signed=True),
                    p=self.partner_id.name,
                    s=self._fmt_points(self.partner_id.loyalty_points)),
                'next': {'type': 'ir.actions.client', 'tag': 'soft_reload'},
            },
        }
