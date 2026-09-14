# -*- coding: utf-8 -*-
"""
Accroches d'attribution des points — un capital unique alimenté par
tous les services.

Règles communes :
* déclenchement au **moment où l'argent est acquis** : commande POS
  réglée, folio facturé / soldé, prestation réalisée ;
* **idempotence** par un champ ``aite_loyalty_move_id`` sur chaque
  document source : un document ne crée jamais deux mouvements ;
* triple accroche sur le POS (create / write / _process_order), comme
  le module Crédit clients v2 en production — l'interface POS ne passe
  pas toujours par les mêmes chemins.
"""
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)

_POS_PAID_STATES = ('paid', 'done', 'invoiced')


class PosOrder(models.Model):
    _inherit = 'pos.order'

    aite_loyalty_move_id = fields.Many2one(
        'aite.loyalty.move', string="Mouvement fidélité", readonly=True,
        copy=False,
    )

    def _aite_award_loyalty(self):
        """Attribue les points une seule fois, commande réglée."""
        engine = self.env['aite.loyalty.engine']
        for order in self:
            if order.aite_loyalty_move_id:
                continue
            if order.state not in _POS_PAID_STATES:
                continue
            if not order.partner_id:
                continue
            move = engine.award(
                order.partner_id, order.amount_total, 'pos',
                ref=order.name, company=order.company_id,
                when=fields.Date.context_today(order))
            if move:
                order.aite_loyalty_move_id = move.id
        return True

    @api.model_create_multi
    def create(self, vals_list):
        orders = super().create(vals_list)
        orders._aite_award_loyalty()
        return orders

    def write(self, vals):
        res = super().write(vals)
        if 'state' in vals or 'partner_id' in vals:
            self._aite_award_loyalty()
        return res

    @api.model
    def _process_order(self, order, existing_order):
        order_id = super()._process_order(order, existing_order)
        if order_id:
            self.browse(order_id)._aite_award_loyalty()
        return order_id


class HotelFolio(models.Model):
    _inherit = 'aite.hotel.folio'

    aite_loyalty_move_id = fields.Many2one(
        'aite.loyalty.move', string="Mouvement fidélité", readonly=True,
        copy=False,
    )

    def _aite_award_loyalty(self):
        engine = self.env['aite.loyalty.engine']
        for folio in self:
            if folio.aite_loyalty_move_id:
                continue
            if folio.state not in ('invoiced', 'paid'):
                continue
            if not folio.partner_id:
                continue
            move = engine.award(
                folio.partner_id, folio.amount_total, 'hotel',
                ref=folio.name, company=folio.company_id,
                when=fields.Date.context_today(folio))
            if move:
                folio.aite_loyalty_move_id = move.id
        return True

    def write(self, vals):
        res = super().write(vals)
        if vals.get('state') in ('invoiced', 'paid'):
            self._aite_award_loyalty()
        return res


class SlotBooking(models.Model):
    _inherit = 'aite.slot.booking'

    aite_loyalty_move_id = fields.Many2one(
        'aite.loyalty.move', string="Mouvement fidélité", readonly=True,
        copy=False,
    )

    def action_done(self):
        res = super().action_done()
        engine = self.env['aite.loyalty.engine']
        for booking in self:
            if booking.aite_loyalty_move_id:
                continue
            if booking.state != 'done' or not booking.partner_id:
                continue
            origin = 'slot_%s' % (booking.kind or 'space')
            move = engine.award(
                booking.partner_id, booking.amount, origin,
                ref=booking.name, company=booking.company_id,
                when=fields.Date.context_today(booking))
            if move:
                booking.aite_loyalty_move_id = move.id
        return res
