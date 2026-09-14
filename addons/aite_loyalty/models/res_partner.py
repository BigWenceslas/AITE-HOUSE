# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

from .loyalty_move import TIERS


class ResPartner(models.Model):
    """
    Vision fidélité du client : solde de points (somme du grand livre),
    statut Standard / VIP / VVIP (recalculé par le cron du moteur) et
    accès direct à l'historique des mouvements.
    """
    _inherit = 'res.partner'

    loyalty_move_ids = fields.One2many(
        'aite.loyalty.move', 'partner_id', string="Mouvements de points",
    )
    loyalty_points = fields.Integer(
        string="Points fidélité", compute='_compute_loyalty_points',
        store=True,
    )
    loyalty_move_count = fields.Integer(
        string="Nb mouvements", compute='_compute_loyalty_points',
        store=True,
    )
    loyalty_tier = fields.Selection(
        selection=TIERS, string="Statut client", default='standard',
        required=True, index=True, tracking=True,
    )
    loyalty_tier_date = fields.Date(
        string="Statut depuis", readonly=True, copy=False,
    )

    @api.depends('loyalty_move_ids.points')
    def _compute_loyalty_points(self):
        for partner in self:
            moves = partner.loyalty_move_ids
            partner.loyalty_points = sum(moves.mapped('points'))
            partner.loyalty_move_count = len(moves)

    def action_view_loyalty_moves(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _("Points de %(p)s", p=self.name),
            'res_model': 'aite.loyalty.move',
            'view_mode': 'list',
            'domain': [('partner_id', '=', self.id)],
            'context': {'default_partner_id': self.id},
        }
