# -*- coding: utf-8 -*-
import logging
from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class PosOrder(models.Model):
    """
    Extension commande POS : mise sur ardoise (vente à crédit).

    Prend en charge le **paiement mixte** : une partie de la commande peut
    être réglée immédiatement (espèces, carte, Mobile Money…) et le reste
    porté sur ardoise. Seule la part payée via une méthode « ardoise »
    (type *pay_later* ou marquée ``is_aite_credit``) devient une dette.

    Exemple : commande 50 000 → 30 000 espèces + 20 000 ardoise ⇒ une ardoise
    de 20 000 est créée, la commande est soldée au POS.

    Deux chemins créent l'ardoise :

    1. **Automatique** — à la synchronisation de la commande (hooks ``create``
       / ``write`` / ``_process_order``), on lit la part « ardoise » des
       paiements et on crée la dette correspondante.
    2. **Manuel** — ``action_put_on_credit`` (rattrapage backend).
    """
    _inherit = 'pos.order'

    credit_id = fields.Many2one(
        'aite.pos.credit', string="Ardoise générée", readonly=True,
        copy=False, index=True,
    )
    is_on_credit = fields.Boolean(
        string="Vendu à crédit", compute='_compute_credit_split', store=True,
    )
    credit_amount = fields.Monetary(
        string="Part sur ardoise", compute='_compute_credit_split',
        store=True,
        help="Montant de la commande réglé via une méthode de type ardoise.",
    )
    amount_paid_direct = fields.Monetary(
        string="Payé comptant", compute='_compute_credit_split', store=True,
        help="Part de la commande réglée immédiatement (hors ardoise).",
    )

    # ------------------------------------------------------------------
    # Calcul de la répartition comptant / ardoise
    # ------------------------------------------------------------------

    @api.depends('payment_ids.amount', 'payment_ids.payment_method_id',
                 'credit_id')
    def _compute_credit_split(self):
        for order in self:
            credit_amt = 0.0
            direct_amt = 0.0
            for pay in order.payment_ids:
                method = pay.payment_method_id
                if method and method._is_aite_credit_method():
                    credit_amt += pay.amount
                else:
                    direct_amt += pay.amount
            order.credit_amount = credit_amt
            order.amount_paid_direct = direct_amt
            order.is_on_credit = bool(order.credit_id) or credit_amt > 0

    def _aite_credit_amount(self):
        """Somme des paiements effectués via une méthode « ardoise »."""
        self.ensure_one()
        total = 0.0
        for pay in self.payment_ids:
            method = pay.payment_method_id
            if method and method._is_aite_credit_method():
                total += pay.amount
        return total

    # ------------------------------------------------------------------
    # Hooks automatiques (plusieurs points d'accroche pour robustesse)
    # ------------------------------------------------------------------

    @api.model_create_multi
    def create(self, vals_list):
        orders = super().create(vals_list)
        for order in orders:
            order._aite_create_credit_if_needed()
        return orders

    def write(self, vals):
        res = super().write(vals)
        if 'payment_ids' in vals or 'state' in vals or 'lines' in vals:
            for order in self:
                order._aite_create_credit_if_needed()
        return res

    def _process_order(self, order, existing_order):
        order_id = super()._process_order(order, existing_order)
        try:
            self.browse(order_id)._aite_create_credit_if_needed()
        except Exception as e:  # pragma: no cover
            _logger.warning("POS Crédit : hook _process_order ignoré (%s)", e)
        return order_id

    def _aite_create_credit_if_needed(self):
        """
        Crée l'ardoise pour la part « à crédit » de la commande, si elle
        n'existe pas déjà. Idempotent.

        Le montant de l'ardoise = somme des paiements via méthode ardoise
        (donc la part crédit d'un paiement mixte, pas le total commande).
        """
        for order in self:
            if order.credit_id:
                continue
            credit_amount = order._aite_credit_amount()
            if credit_amount <= 0:
                continue
            if not order.partner_id:
                _logger.info(
                    "POS Crédit : commande %s à crédit sans client, "
                    "ardoise non créée.", order.name or order.id)
                continue

            credit = self.env['aite.pos.credit'].sudo().create({
                'partner_id': order.partner_id.id,
                'order_id': order.id,
                'company_id': order.company_id.id,
                'amount_total': credit_amount,
                'date_open': fields.Date.context_today(order),
            })
            order.credit_id = credit.id
            _logger.info(
                "POS Crédit : ardoise %s de %s créée pour la commande %s "
                "(payé comptant : %s).",
                credit.name, credit_amount, order.name or order.id,
                order.amount_paid_direct)

    # ------------------------------------------------------------------
    # Chemin manuel (rattrapage backend)
    # ------------------------------------------------------------------

    def action_put_on_credit(self, down_payment=0.0):
        """
        Met manuellement la commande sur ardoise.

        :param down_payment: acompte déjà réglé comptant (réduit la part
            mise sur ardoise). Par défaut 0 (tout à crédit).
        :returns: l'ardoise créée.
        """
        self.ensure_one()
        if self.credit_id:
            raise UserError(
                _("Cette commande est déjà sur ardoise (%s).",
                  self.credit_id.name))
        if not self.partner_id:
            raise UserError(
                _("Un client doit être sélectionné pour une vente à crédit."))

        amount = (self.amount_total or 0.0) - (down_payment or 0.0)
        if amount <= 0:
            raise UserError(
                _("Le montant à mettre sur ardoise doit être positif "
                  "(acompte trop élevé ?)."))

        credit = self.env['aite.pos.credit'].create({
            'partner_id': self.partner_id.id,
            'order_id': self.id,
            'company_id': self.company_id.id,
            'amount_total': amount,
            'date_open': fields.Date.context_today(self),
        })
        self.credit_id = credit.id
        return credit
