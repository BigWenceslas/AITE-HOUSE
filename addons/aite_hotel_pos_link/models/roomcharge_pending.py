# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class RoomchargePending(models.Model):
    """
    Notes de chambre en attente de rattachement : la réception choisit
    le folio et valide — le report réutilise le même chemin idempotent
    que le rattachement automatique.
    """
    _name = 'aite.roomcharge.pending'
    _description = "Note de chambre en attente"
    _order = 'create_date desc'

    order_id = fields.Many2one(
        'pos.order', string="Commande POS", required=True,
        ondelete='cascade', index=True,
    )
    partner_id = fields.Many2one('res.partner', string="Client")
    company_id = fields.Many2one(
        related='order_id.company_id', store=True, readonly=True)
    currency_id = fields.Many2one(
        related='order_id.currency_id', readonly=True)
    amount = fields.Monetary(
        string="Montant", currency_field='currency_id', readonly=True)
    note = fields.Char(string="Motif", readonly=True)
    folio_id = fields.Many2one(
        'aite.hotel.folio', string="Folio choisi",
        domain="[('state', '=', 'open')]",
    )
    state = fields.Selection(
        selection=[('todo', "À rattacher"), ('done', "Rattachée")],
        string="État", default='todo', required=True, index=True,
    )

    def action_resolve(self):
        for rec in self:
            if rec.state == 'done':
                continue
            if not rec.folio_id:
                raise UserError(_("Choisissez d'abord un folio ouvert."))
            if rec.folio_id.state != 'open':
                raise UserError(_(
                    "Le folio %(f)s n'est plus ouvert.",
                    f=rec.folio_id.name))
            order = rec.order_id
            if order.aite_folio_line_id:
                rec.state = 'done'
                continue
            if order._aite_post_to_folio(rec.folio_id, rec.amount):
                rec.state = 'done'
                # Complète le client si la commande n'en avait pas
                if not rec.partner_id:
                    rec.partner_id = rec.folio_id.partner_id.id
        return True
