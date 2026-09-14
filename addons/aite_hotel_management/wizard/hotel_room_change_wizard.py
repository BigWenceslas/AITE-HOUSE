# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HotelRoomChangeWizard(models.TransientModel):
    """
    Assistant — changement de chambre.

    Déplace un séjour (surclassement, déclassement, panne) vers une autre
    chambre de l'hôtel : la disponibilité est contrôlée, le folio
    resynchronisé et le mouvement tracé au chatter par
    ``action_change_room``. L'option « conserver le prix » couvre le
    surclassement gracieux : le client garde le tarif de sa chambre
    d'origine.
    """
    _name = 'aite.hotel.room.change.wizard'
    _description = "Assistant — changement de chambre"

    line_id = fields.Many2one(
        'aite.hotel.reservation.line', string="Ligne de séjour",
        required=True, readonly=True,
    )
    reservation_id = fields.Many2one(
        related='line_id.reservation_id', readonly=True,
    )
    hotel_id = fields.Many2one(
        related='line_id.hotel_id', readonly=True,
    )
    currency_id = fields.Many2one(
        related='line_id.currency_id', readonly=True,
    )
    partner_id = fields.Many2one(
        related='line_id.partner_id', string="Client", readonly=True,
    )
    current_room_id = fields.Many2one(
        related='line_id.room_id', string="Chambre actuelle", readonly=True,
    )
    checkin_date = fields.Datetime(
        related='line_id.checkin_date', string="Arrivée", readonly=True,
    )
    checkout_date = fields.Datetime(
        related='line_id.checkout_date', string="Départ", readonly=True,
    )
    current_price = fields.Monetary(
        related='line_id.price_night', string="Prix actuel / nuit",
        readonly=True, currency_field='currency_id',
    )
    new_room_id = fields.Many2one(
        'aite.hotel.room', string="Nouvelle chambre", required=True,
        domain="[('hotel_id', '=', hotel_id),"
               " ('id', '!=', current_room_id),"
               " ('out_of_order', '=', False)]",
    )
    keep_price = fields.Boolean(
        string="Conserver le prix actuel",
        help="Surclassement gracieux : la nouvelle chambre est facturée "
             "au tarif de l'ancienne. Décoché, le prix de la nouvelle "
             "chambre s'applique.",
    )
    new_price = fields.Monetary(
        string="Nouveau prix / nuit", compute='_compute_new_price',
        currency_field='currency_id',
        help="Prix qui sera appliqué après le changement.",
    )

    @api.depends('new_room_id', 'keep_price', 'current_price',
                 'checkin_date', 'checkout_date')
    def _compute_new_price(self):
        for wiz in self:
            if wiz.keep_price or not wiz.new_room_id:
                wiz.new_price = wiz.current_price
            elif wiz.checkin_date and wiz.checkout_date:
                price, _nights = wiz.new_room_id._get_stay_price(
                    wiz.checkin_date.date(), wiz.checkout_date.date())
                wiz.new_price = price
            else:
                wiz.new_price = 0.0

    def action_confirm(self):
        self.ensure_one()
        line = self.line_id
        if line.state not in ('confirmed', 'checked_in'):
            raise UserError(
                _("Le changement de chambre n'est possible que sur un "
                  "séjour confirmé ou en cours."))
        old_price = line.price_night
        line.action_change_room(self.new_room_id.id)
        if self.keep_price and line.price_night != old_price:
            line.price_night = old_price
            line.reservation_id._sync_folio_room_lines()
            line.reservation_id.message_post(body=_(
                "Surclassement gracieux : le tarif de %(price)s / nuit "
                "est conservé.", price=old_price))
        return {'type': 'ir.actions.act_window_close'}
