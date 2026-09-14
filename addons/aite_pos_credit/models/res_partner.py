# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResPartner(models.Model):
    """
    Extension client : encours d'ardoise (somme des restes dus).

    ``credit_outstanding`` agrège le reste dû de toutes les ardoises ouvertes
    du client. Sert d'indicateur rapide en fiche client et au POS.
    """
    _inherit = 'res.partner'

    aite_credit_ids = fields.One2many(
        'aite.pos.credit', 'partner_id', string="Ardoises",
    )
    credit_outstanding = fields.Monetary(
        string="Encours ardoise", compute='_compute_credit_outstanding',
        store=True, currency_field='currency_id',
        help="Total restant dû sur l'ensemble des ardoises ouvertes.",
    )
    credit_ardoise_count = fields.Integer(
        string="Nb ardoises ouvertes", compute='_compute_credit_outstanding',
        store=True,
    )

    @api.depends('aite_credit_ids.amount_residual', 'aite_credit_ids.state')
    def _compute_credit_outstanding(self):
        for partner in self:
            open_credits = partner.aite_credit_ids.filtered(
                lambda c: c.state == 'open'
            )
            partner.credit_outstanding = sum(
                open_credits.mapped('amount_residual'))
            partner.credit_ardoise_count = len(open_credits)

    def action_view_ardoises(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': "Ardoises",
            'res_model': 'aite.pos.credit',
            'view_mode': 'list,form',
            'domain': [('partner_id', '=', self.id)],
            'context': {'default_partner_id': self.id},
        }
