# -*- coding: utf-8 -*-
from odoo import fields, models, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    registration_count = fields.Integer(
        string="Fiches d'enregistrement", compute='_compute_registration_count',
    )

    def _compute_registration_count(self):
        data = self.env['aite.guest.registration']._read_group(
            [('partner_id', 'in', self.ids)], ['partner_id'], ['__count'])
        counts = {p.id: c for p, c in data}
        for partner in self:
            partner.registration_count = counts.get(partner.id, 0)

    def action_view_registrations(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _("Fiches — %s", self.name),
            'res_model': 'aite.guest.registration',
            'view_mode': 'list,form',
            'domain': [('partner_id', '=', self.id)],
        }
