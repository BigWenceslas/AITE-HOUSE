# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HotelPaymentWizard(models.TransientModel):
    """
    Assistant d'encaissement sur folio (acompte ou règlement).

    Pré-rempli avec le solde dû, il crée un
    ``aite.hotel.folio.payment`` ; le recompute du folio met à jour le
    solde et l'état, l'écriture 411 part si la société l'a activé —
    exactement le circuit du wizard de remboursement d'ardoise.
    """
    _name = 'aite.hotel.payment.wizard'
    _description = "Assistant — règlement de folio"

    folio_id = fields.Many2one(
        'aite.hotel.folio', string="Folio", required=True, readonly=True,
    )
    partner_id = fields.Many2one(
        'res.partner', string="Client", related='folio_id.partner_id',
        readonly=True,
    )
    currency_id = fields.Many2one(
        'res.currency', related='folio_id.currency_id', readonly=True,
    )
    residual = fields.Monetary(
        string="Solde dû actuel", related='folio_id.amount_residual',
        readonly=True, currency_field='currency_id',
    )
    amount = fields.Monetary(
        string="Montant à encaisser", required=True,
        currency_field='currency_id',
    )
    is_deposit = fields.Boolean(
        string="Acompte", compute='_compute_is_deposit', store=True,
        readonly=False,
        help="Coché automatiquement si le client n'est pas encore "
             "arrivé.",
    )
    method = fields.Selection(
        selection=[
            ('mtn', "MTN Mobile Money"),
            ('orange', "Orange Money"),
            ('cash', "Espèces"),
            ('card', "Carte bancaire"),
            ('transfer', "Virement / autre"),
        ],
        string="Moyen de paiement", required=True, default='cash',
    )
    transaction_ref = fields.Char(string="Réf. transaction")
    date = fields.Date(
        string="Date", required=True, default=fields.Date.context_today,
    )
    note = fields.Char(string="Note")

    @api.depends('folio_id')
    def _compute_is_deposit(self):
        for wiz in self:
            wiz.is_deposit = wiz.folio_id.reservation_state in (
                'draft', 'confirmed')

    @api.onchange('amount')
    def _onchange_amount_cap(self):
        """Avertit sans bloquer si l'encaissement dépasse le solde."""
        if self.amount and self.residual \
                and self.amount > self.residual + 0.01:
            return {
                'warning': {
                    'title': _("Montant élevé"),
                    'message': _(
                        "Le montant saisi dépasse le solde dû (%(res)s). "
                        "Il sera plafonné à la validation.",
                        res=self.residual),
                }
            }

    def action_confirm(self):
        self.ensure_one()
        if self.amount <= 0:
            raise UserError(_("Le montant doit être positif."))
        residual = self.folio_id.amount_residual
        amount = min(self.amount, residual) if residual else self.amount
        if amount <= 0:
            raise UserError(_("Ce folio est déjà soldé."))

        self.env['aite.hotel.folio.payment'].create({
            'folio_id': self.folio_id.id,
            'amount': amount,
            'is_deposit': self.is_deposit,
            'method': self.method,
            'transaction_ref': self.transaction_ref or False,
            'date': self.date,
            'note': self.note or False,
            'collected_by': self.env.user.id,
        })
        return {'type': 'ir.actions.act_window_close'}
