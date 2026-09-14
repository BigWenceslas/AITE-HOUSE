# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HotelCheckoutWizard(models.TransientModel):
    """
    Assistant de check-out.

    Récapitule le folio, gère le **départ anticipé** (les nuitées sont
    recalculées sur la durée réelle si l'option est cochée), clôture le
    séjour, déclenche la recouche des chambres et génère la facture
    depuis le folio — avec lettrage des acomptes déjà encaissés.
    """
    _name = 'aite.hotel.checkout.wizard'
    _description = "Assistant — check-out"

    reservation_id = fields.Many2one(
        'aite.hotel.reservation', string="Réservation", required=True,
        readonly=True,
    )
    partner_id = fields.Many2one(
        related='reservation_id.partner_id', readonly=True,
    )
    currency_id = fields.Many2one(
        related='reservation_id.currency_id', readonly=True,
    )
    folio_id = fields.Many2one(
        related='reservation_id.folio_id', readonly=True,
    )
    planned_checkout = fields.Datetime(
        related='reservation_id.checkout_date', string="Départ prévu",
        readonly=True,
    )
    checkout_now = fields.Datetime(
        string="Départ réel", required=True,
        default=fields.Datetime.now,
    )
    is_early = fields.Boolean(
        string="Départ anticipé", compute='_compute_is_early',
    )
    recompute_nights = fields.Boolean(
        string="Recalculer les nuitées", default=True,
        help="En cas de départ anticipé, ramène la date de départ (et "
             "donc les nuitées facturées) à la durée réelle du séjour.",
    )
    create_invoice = fields.Boolean(
        string="Générer la facture", default=True,
    )
    amount_total = fields.Monetary(
        related='folio_id.amount_total', string="Total TTC", readonly=True,
        currency_field='currency_id',
    )
    amount_paid = fields.Monetary(
        related='folio_id.amount_paid', string="Déjà encaissé",
        readonly=True, currency_field='currency_id',
    )
    amount_residual = fields.Monetary(
        related='folio_id.amount_residual', string="Solde dû",
        readonly=True, currency_field='currency_id',
    )

    @api.depends('checkout_now', 'planned_checkout')
    def _compute_is_early(self):
        for wiz in self:
            wiz.is_early = bool(
                wiz.checkout_now and wiz.planned_checkout
                and wiz.checkout_now.date()
                < wiz.planned_checkout.date())

    def action_confirm(self):
        self.ensure_one()
        reservation = self.reservation_id
        if reservation.state != 'checked_in':
            raise UserError(
                _("Le check-out n'est possible que pour un client "
                  "arrivé."))

        # Départ anticipé : ajuster la date de départ (le compute des
        # nuits et la synchro folio suivent).
        if self.is_early and self.recompute_nights:
            new_checkout = reservation._compose_datetime(
                self.checkout_now.date(),
                reservation.hotel_id.checkout_hour)
            if new_checkout <= reservation.checkin_date:
                # Départ le jour même de l'arrivée : on facture 1 nuitée
                # minimum (day-use), le départ est calé à arrivée + 1 h.
                new_checkout = reservation.checkin_date \
                    + timedelta(hours=1)
            reservation.checkout_date = new_checkout

        reservation._sync_folio_room_lines()
        reservation.write({
            'state': 'checked_out',
            'actual_checkout': self.checkout_now,
        })
        # Recouche des chambres libérées.
        self.env['aite.hotel.housekeeping']._create_checkout_task(
            reservation.line_ids.mapped('room_id'))

        folio = reservation.folio_id
        if self.create_invoice and folio and not folio.move_id:
            return folio.action_create_invoice()
        if folio:
            return reservation.action_view_folio()
        return {'type': 'ir.actions.act_window_close'}
