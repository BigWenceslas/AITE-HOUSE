# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ResPartner(models.Model):
    """
    Fiche client enrichie pour l'hôtellerie.

    Marqueurs (client hôtel, agent commissionné) et informations du
    registre des voyageurs : pièce d'identité et nationalité, exigées par
    la réglementation dans la plupart des pays (fiche de police).
    """
    _inherit = 'res.partner'

    is_hotel_guest = fields.Boolean(
        string="Client hôtel", index=True,
        help="Coché automatiquement dès la première réservation.",
    )
    is_booking_agent = fields.Boolean(
        string="Agent / apporteur",
        help="Autorise ce contact comme apporteur d'affaires "
             "commissionné sur les réservations.",
    )
    guest_id_type = fields.Selection(
        selection=[
            ('cni', "Carte nationale d'identité"),
            ('passport', "Passeport"),
            ('permit', "Permis de conduire"),
            ('other', "Autre"),
        ],
        string="Type de pièce",
    )
    guest_id_number = fields.Char(string="N° de pièce")
    nationality_id = fields.Many2one(
        'res.country', string="Nationalité",
    )
    reservation_count = fields.Integer(
        string="Séjours", compute='_compute_reservation_count',
    )

    def _compute_reservation_count(self):
        data = self.env['aite.hotel.reservation']._read_group(
            [('partner_id', 'in', self.ids)],
            ['partner_id'], ['__count'],
        )
        counts = {partner.id: count for partner, count in data}
        for partner in self:
            partner.reservation_count = counts.get(partner.id, 0)

    def action_view_hotel_reservations(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _("Séjours — %s", self.name),
            'res_model': 'aite.hotel.reservation',
            'view_mode': 'list,form',
            'domain': [('partner_id', '=', self.id)],
            'context': {'default_partner_id': self.id},
        }
