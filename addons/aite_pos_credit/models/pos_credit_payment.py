# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class PosCreditPayment(models.Model):
    """
    Remboursement d'une ardoise.

    Encaissement (partiel ou total) réduisant le reste dû d'une ardoise.
    Le moyen de paiement reflète le contexte local : Mobile Money
    (MTN MoMo / Orange Money) et espèces, plus carte / virement.

    Comptabilité (optionnelle) : si la société active la génération
    d'écritures (``pos_credit_auto_entries``), la validation d'un
    remboursement passe une écriture débit Caisse/Banque (512/521) / crédit
    Client (411), rapprochant ainsi l'encours de la comptabilité OHADA.
    """
    _name = 'aite.pos.credit.payment'
    _description = "Remboursement d'ardoise"
    _order = 'date desc, id desc'
    _rec_name = 'credit_id'

    credit_id = fields.Many2one(
        'aite.pos.credit', string="Ardoise", required=True,
        ondelete='cascade', index=True,
    )
    partner_id = fields.Many2one(
        'res.partner', string="Client",
        related='credit_id.partner_id', store=True, readonly=True,
    )
    company_id = fields.Many2one(
        'res.company', related='credit_id.company_id', store=True,
        readonly=True,
    )
    currency_id = fields.Many2one(
        'res.currency', related='credit_id.currency_id', store=True,
        readonly=True,
    )

    date = fields.Date(
        string="Date", required=True, index=True,
        default=fields.Date.context_today,
    )
    amount = fields.Monetary(
        string="Montant", required=True, currency_field='currency_id',
    )

    method = fields.Selection(
        selection=[
            ('mtn', "MTN Mobile Money"),
            ('orange', "Orange Money"),
            ('cash', "Espèces"),
            ('card', "Carte bancaire"),
            ('transfer', "Virement / autre"),
        ],
        string="Moyen de paiement", required=True, default='cash', index=True,
    )
    transaction_ref = fields.Char(
        string="Réf. transaction",
        help="Identifiant Mobile Money ou référence de l'encaissement.",
    )
    collected_by = fields.Many2one(
        'res.users', string="Encaissé par", default=lambda self: self.env.user,
    )

    move_id = fields.Many2one(
        'account.move', string="Écriture comptable", readonly=True, copy=False,
        help="Écriture de remboursement (411) générée à la validation.",
    )

    state = fields.Selection(
        selection=[
            ('posted', "Validé"),
            ('cancelled', "Annulé"),
        ],
        string="État", default='posted', required=True, index=True, copy=False,
    )

    note = fields.Char(string="Note")

    # ------------------------------------------------------------------
    # Contraintes
    # ------------------------------------------------------------------

    @api.constrains('amount')
    def _check_amount(self):
        for pay in self:
            if pay.amount <= 0:
                raise ValidationError(
                    _("Le montant d'un remboursement doit être positif."))

    @api.constrains('amount', 'credit_id', 'state')
    def _check_not_overpaid(self):
        """Empêche de rembourser plus que le reste dû de l'ardoise."""
        for pay in self:
            if pay.state != 'posted':
                continue
            credit = pay.credit_id
            others = sum(
                p.amount for p in credit.payment_ids
                if p.state == 'posted' and p.id != pay.id
            )
            available = credit.amount_total - others
            if pay.amount - available > 0.01:  # tolérance d'arrondi
                raise ValidationError(_(
                    "Le remboursement (%(amt)s) dépasse le reste dû de "
                    "l'ardoise (%(res)s).",
                    amt=pay.amount, res=max(0.0, available),
                ))

    # ------------------------------------------------------------------
    # Création / comptabilisation
    # ------------------------------------------------------------------

    @api.model_create_multi
    def create(self, vals_list):
        payments = super().create(vals_list)
        for pay in payments:
            if pay.state == 'posted':
                pay._post_accounting_entry()
        return payments

    def _journal_for_method(self):
        """
        Détermine le journal d'encaissement selon le moyen de paiement.

        Stratégie : journal configuré sur la société en priorité ; sinon, on
        cherche un journal de caisse (espèces) ou de banque (MoMo / carte /
        virement) ; à défaut, le premier journal de trésorerie disponible.
        """
        self.ensure_one()
        company = self.company_id or self.env.company
        if company.pos_credit_journal_id:
            return company.pos_credit_journal_id

        # ``sudo`` : le caissier encaisse sans détenir les droits
        # comptables. Le choix du journal est une mécanique interne ; le
        # contrôle d'accès porte sur le remboursement lui-même.
        Journal = self.env['account.journal'].sudo()
        if self.method == 'cash':
            journal = Journal.search([
                ('type', '=', 'cash'), ('company_id', '=', company.id),
            ], limit=1)
        else:
            journal = Journal.search([
                ('type', '=', 'bank'), ('company_id', '=', company.id),
            ], limit=1)
        if not journal:
            journal = Journal.search([
                ('type', 'in', ('bank', 'cash')),
                ('company_id', '=', company.id),
            ], limit=1)
        return journal

    def _post_accounting_entry(self):
        """
        Passe l'écriture de remboursement et la rapproche de la créance.

        Débit  : compte du journal d'encaissement (512 / 521 / 571…)
        Crédit : compte client 411 (encours de l'ardoise)

        Puis tente de rapprocher la ligne 411 de cette écriture avec les
        lignes 411 ouvertes de la commande POS d'origine, pour solder
        progressivement la créance.

        N'effectue rien si la société n'a pas activé la génération
        d'écritures, ou si la configuration comptable est incomplète (le
        suivi de l'ardoise reste alors purement applicatif).
        """
        self.ensure_one()
        company = self.company_id or self.env.company
        if not company.pos_credit_auto_entries:
            return
        if self.move_id:
            return

        partner = self.partner_id
        # ``sudo`` pour la même raison que le journal : le caissier n'a pas
        # accès au plan comptable.
        receivable = company.sudo()._get_pos_credit_account(partner.sudo())
        journal = self._journal_for_method()
        if not receivable or not journal:
            # Configuration incomplète : on ne bloque pas l'encaissement.
            return

        # Compte de contrepartie (trésorerie) = compte par défaut du journal.
        counterpart = (
            journal.default_account_id
            or journal.suspense_account_id
        )
        if not counterpart:
            return

        label = _("Remboursement ardoise %s", self.credit_id.name)
        move_vals = {
            'journal_id': journal.id,
            'date': self.date,
            'ref': label,
            'company_id': company.id,
            'line_ids': [
                (0, 0, {
                    'name': label,
                    'account_id': counterpart.id,
                    'debit': self.amount,
                    'credit': 0.0,
                    'partner_id': partner.id,
                }),
                (0, 0, {
                    'name': label,
                    'account_id': receivable.id,
                    'debit': 0.0,
                    'credit': self.amount,
                    'partner_id': partner.id,
                }),
            ],
        }
        move = self.env['account.move'].sudo().create(move_vals)
        move.action_post()
        self.move_id = move.id

        self._reconcile_with_order(receivable, move)

    def _reconcile_with_order(self, receivable, move):
        """
        Rapproche la ligne 411 du remboursement avec les lignes 411 ouvertes
        de la commande POS d'origine (best-effort).
        """
        self.ensure_one()
        order = self.credit_id.order_id
        if not order:
            return
        # Lignes 411 non lettrées du remboursement.
        pay_lines = move.line_ids.filtered(
            lambda l: l.account_id == receivable and not l.reconciled)
        # Lignes 411 non lettrées issues de la commande POS.
        order_moves = order.account_move
        if not order_moves:
            return
        order_lines = order_moves.line_ids.filtered(
            lambda l: l.account_id == receivable and not l.reconciled)
        to_reconcile = pay_lines | order_lines
        if len(to_reconcile) >= 2:
            try:
                to_reconcile.reconcile()
            except Exception:
                # Le rapprochement est un confort ; on ne bloque jamais.
                pass

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def action_cancel(self):
        for pay in self:
            # Annuler l'écriture comptable associée le cas échéant.
            if pay.move_id and pay.move_id.state == 'posted':
                try:
                    pay.move_id.button_draft()
                    pay.move_id.button_cancel()
                except Exception:
                    pass
            pay.state = 'cancelled'

    def action_post(self):
        for pay in self:
            pay.state = 'posted'
            pay._post_accounting_entry()

    @api.model
    def method_label(self, code):
        """Libellé lisible d'un moyen de paiement (utilisé par le dashboard)."""
        return dict(self._fields['method'].selection).get(code, code)
