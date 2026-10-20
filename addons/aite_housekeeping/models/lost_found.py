# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class LostAndFound(models.Model):
    """
    Objets trouvés : quoi, où, quand, par qui — puis rendu à qui.
    Un registre simple, avec photo, rattachable au séjour pour retrouver le
    client.
    """
    _name = 'aite.hk.lost.found'
    _description = "Objet trouvé"
    _inherit = ['mail.thread']
    _order = 'found_date desc, id desc'

    name = fields.Char(string="Objet", required=True,
                       help="Ex. : téléphone Samsung noir, montre, chargeur.")
    found_date = fields.Date(string="Trouvé le", required=True,
                             default=fields.Date.context_today)
    room_id = fields.Many2one('aite.hotel.room', string="Chambre / lieu")
    place = fields.Char(string="Précision du lieu",
                        help="Ex. : sous le lit, salle de bain, terrasse.")
    hotel_id = fields.Many2one(
        'aite.hotel.hotel', string="Hôtel",
        default=lambda self: self.env['aite.hotel.hotel'].search(
            [('company_id', '=', self.env.company.id)], limit=1))
    found_by = fields.Many2one('res.users', string="Trouvé par",
                               default=lambda self: self.env.user)
    reservation_id = fields.Many2one(
        'aite.hotel.reservation', string="Séjour probable",
        help="Le client qui occupait la chambre à cette date.")
    partner_id = fields.Many2one(
        related='reservation_id.partner_id', string="Client", store=True)
    image = fields.Image(string="Photo", max_width=1280, max_height=1280)
    storage = fields.Char(string="Rangé où", help="Ex. : casier 3, bureau de la gouvernante.")
    state = fields.Selection(
        selection=[('stored', "Conservé"), ('returned', "Rendu"),
                   ('disposed', "Détruit / donné")],
        string="Statut", default='stored', required=True, tracking=True)
    returned_date = fields.Date(string="Rendu le")
    returned_to = fields.Char(string="Rendu à")
    note = fields.Text(string="Observation")

    @api.onchange('room_id', 'found_date')
    def _onchange_room_guess_stay(self):
        """Devine le séjour : qui occupait la chambre ce jour-là ?"""
        if self.room_id and self.found_date:
            line = self.env['aite.hotel.reservation.line'].search([
                ('room_id', '=', self.room_id.id),
                ('state', 'in', ('checked_in', 'checked_out', 'confirmed')),
                ('checkin_date', '<=', fields.Datetime.to_datetime(
                    str(self.found_date)).replace(hour=23, minute=59)),
                # Un client arrivé occupe la chambre jusqu'à son check-out
                # réel, même si son départ prévu est dépassé.
                '|', ('state', '=', 'checked_in'),
                ('checkout_date', '>=', fields.Datetime.to_datetime(
                    str(self.found_date))),
            ], order='checkin_date desc', limit=1)
            self.reservation_id = line.reservation_id

    def action_return(self):
        for rec in self:
            rec.write({'state': 'returned',
                       'returned_date': fields.Date.context_today(self),
                       'returned_to': rec.returned_to or rec.partner_id.name})
        return True
