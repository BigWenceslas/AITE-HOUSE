# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HotelBookingWizard(models.TransientModel):
    """
    Assistant « Disponibilité & réservation rapide ».

    Flux front desk phare des PMS du marché : saisir les dates et
    l'occupation, voir instantanément les chambres libres avec le tarif
    calculé, cocher, réserver. Crée la réservation (brouillon ou
    directement confirmée) avec ses lignes.
    """
    _name = 'aite.hotel.booking.wizard'
    _description = "Assistant — disponibilité & réservation"

    hotel_id = fields.Many2one(
        'aite.hotel.hotel', string="Hôtel", required=True,
        default=lambda self: self.env['aite.hotel.hotel'].search(
            [('company_id', '=', self.env.company.id)], limit=1),
    )
    currency_id = fields.Many2one(
        'res.currency', related='hotel_id.currency_id', readonly=True,
    )
    checkin_date = fields.Datetime(
        string="Arrivée", required=True,
        default=lambda self: self.env[
            'aite.hotel.reservation']._default_checkin(),
    )
    checkout_date = fields.Datetime(
        string="Départ", required=True,
        default=lambda self: self.env[
            'aite.hotel.reservation']._default_checkout(),
    )
    room_type_id = fields.Many2one(
        'aite.hotel.room.type', string="Type de chambre",
        help="Vide = tous les types.",
    )
    adults = fields.Integer(string="Adultes", default=1)
    children = fields.Integer(string="Enfants", default=0)
    partner_id = fields.Many2one(
        'res.partner', string="Client",
        domain="[('is_company', '=', False)]",
    )
    confirm_immediately = fields.Boolean(
        string="Confirmer immédiatement", default=True,
        help="Décoché : la réservation est créée en brouillon.",
    )
    line_ids = fields.One2many(
        'aite.hotel.booking.wizard.line', 'wizard_id',
        string="Chambres disponibles",
    )
    searched = fields.Boolean(default=False)

    @api.onchange('hotel_id', 'checkin_date', 'checkout_date',
                  'room_type_id', 'adults')
    def _onchange_reset_search(self):
        self.searched = False
        self.line_ids = [(5, 0, 0)]

    def action_search(self):
        """Peuple les lignes avec les chambres libres et leur tarif."""
        self.ensure_one()
        if self.checkout_date <= self.checkin_date:
            raise UserError(
                _("La date de départ doit suivre la date d'arrivée."))
        domain = [
            ('hotel_id', '=', self.hotel_id.id),
            ('out_of_order', '=', False),
            ('capacity_adults', '>=', max(1, self.adults)),
        ]
        if self.room_type_id:
            domain.append(('room_type_id', '=', self.room_type_id.id))
        rooms = self.env['aite.hotel.room'].search(
            domain, order='room_type_id, name')
        lines = []
        for room in rooms:
            if not room.is_available(self.checkin_date, self.checkout_date):
                continue
            price, nights = room._get_stay_price(
                self.checkin_date.date(), self.checkout_date.date())
            lines.append((0, 0, {
                'room_id': room.id,
                'price_night': price,
                'nights': nights,
            }))
        self.write({'line_ids': [(5, 0, 0)] + lines, 'searched': True})
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_book(self):
        """Crée la réservation avec les chambres cochées."""
        self.ensure_one()
        selected = self.line_ids.filtered('selected')
        if not selected:
            raise UserError(_("Cochez au moins une chambre à réserver."))
        if not self.partner_id:
            raise UserError(_("Renseignez le client avant de réserver."))
        reservation = self.env['aite.hotel.reservation'].create({
            'hotel_id': self.hotel_id.id,
            'partner_id': self.partner_id.id,
            'checkin_date': self.checkin_date,
            'checkout_date': self.checkout_date,
            'line_ids': [(0, 0, {
                'room_type_id': line.room_id.room_type_id.id,
                'room_id': line.room_id.id,
                'adults': min(max(1, self.adults),
                              line.room_id.capacity_adults),
                'children': min(self.children,
                                line.room_id.capacity_children),
                'price_night': line.price_night,
            }) for line in selected],
        })
        if self.confirm_immediately:
            reservation.action_confirm()
        return {
            'type': 'ir.actions.act_window',
            'name': _("Réservation"),
            'res_model': 'aite.hotel.reservation',
            'view_mode': 'form',
            'res_id': reservation.id,
        }


class HotelBookingWizardLine(models.TransientModel):
    """Ligne de résultat de recherche de disponibilité."""
    _name = 'aite.hotel.booking.wizard.line'
    _description = "Assistant réservation — chambre disponible"

    wizard_id = fields.Many2one(
        'aite.hotel.booking.wizard', required=True, ondelete='cascade',
    )
    currency_id = fields.Many2one(
        related='wizard_id.currency_id', readonly=True,
    )
    selected = fields.Boolean(string="Réserver")
    room_id = fields.Many2one(
        'aite.hotel.room', string="Chambre", required=True, readonly=True,
    )
    room_type_id = fields.Many2one(
        related='room_id.room_type_id', string="Type", readonly=True,
    )
    floor_id = fields.Many2one(
        related='room_id.floor_id', string="Étage", readonly=True,
    )
    capacity_adults = fields.Integer(
        related='room_id.capacity_adults', string="Cap. adultes",
        readonly=True,
    )
    nights = fields.Integer(string="Nuits", readonly=True)
    price_night = fields.Monetary(
        string="Prix / nuit", currency_field='currency_id', readonly=True,
    )
    price_total = fields.Monetary(
        string="Total séjour (HT)", compute='_compute_total',
        currency_field='currency_id',
    )

    @api.depends('price_night', 'nights')
    def _compute_total(self):
        for line in self:
            line.price_total = line.price_night * line.nights
