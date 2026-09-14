# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PosCreditRepayWizard(models.TransientModel):
    """
    Assistant d'enregistrement d'un remboursement d'ardoise.

    Pré-rempli depuis une ardoise (montant = reste dû), il crée un
    ``aite.pos.credit.payment`` et laisse le recompute de l'ardoise mettre à
    jour le reste dû et l'état.
    """
    _name = 'aite.pos.credit.repay.wizard'
    _description = "Assistant — remboursement d'ardoise"

    credit_id = fields.Many2one(
        'aite.pos.credit', string="Ardoise", required=True, readonly=True,
    )
    partner_id = fields.Many2one(
        'res.partner', string="Client", related='credit_id.partner_id',
        readonly=True,
    )
    currency_id = fields.Many2one(
        'res.currency', related='credit_id.currency_id', readonly=True,
    )
    residual = fields.Monetary(
        string="Reste dû actuel", related='credit_id.amount_residual',
        readonly=True, currency_field='currency_id',
    )

    amount = fields.Monetary(
        string="Montant à encaisser", required=True,
        currency_field='currency_id',
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

    @api.onchange('amount')
    def _onchange_amount_cap(self):
        """Avertit doucement si on dépasse le reste dû (sans bloquer la saisie)."""
        if self.amount and self.residual and self.amount > self.residual + 0.01:
            return {
                'warning': {
                    'title': _("Montant élevé"),
                    'message': _(
                        "Le montant saisi dépasse le reste dû (%(res)s). "
                        "Il sera plafonné à la validation.",
                        res=self.residual),
                }
            }

    def action_confirm(self):
        self.ensure_one()
        if self.amount <= 0:
            raise UserError(_("Le montant doit être positif."))
        # Plafonner au reste dû pour éviter la sur-imputation.
        amount = min(self.amount, self.credit_id.amount_residual)
        if amount <= 0:
            raise UserError(_("Cette ardoise est déjà soldée."))

        self.env['aite.pos.credit.payment'].create({
            'credit_id': self.credit_id.id,
            'amount': amount,
            'method': self.method,
            'transaction_ref': self.transaction_ref or False,
            'date': self.date,
            'note': self.note or False,
            'collected_by': self.env.user.id,
        })
        return {'type': 'ir.actions.act_window_close'}
