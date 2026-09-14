# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class PosCredit(models.Model):
    """
    Ardoise — une vente à crédit, née au POS **ou** dans le module Ventes.

    Représente une dette d'un client née d'une commande (POS ou vente)
    payée plus tard. Le montant restant dû (``amount_residual``) est suivi
    en propre et décrémenté par les remboursements
    (``aite.pos.credit.payment``) — le même circuit de recouvrement quel
    que soit le canal d'origine.

    L'ardoise reste rattachée à sa commande d'origine (``order_id`` pour
    le POS, ``sale_order_id`` pour les Ventes) et à son client. Les seuils
    d'ancienneté servent à classer la sévérité (récent / en retard /
    critique) pour le pilotage du recouvrement.
    """
    _name = 'aite.pos.credit'
    _description = "Ardoise POS (vente à crédit)"
    _order = 'create_date desc'
    _rec_name = 'name'

    # Seuils d'ancienneté en jours (surchageables dans un module dérivé).
    AGE_THRESHOLD_LATE = 30      # au-delà → en retard
    AGE_THRESHOLD_CRITICAL = 60  # au-delà → critique

    name = fields.Char(
        string="Référence", required=True, copy=False, readonly=True,
        index=True, default=lambda self: _("Nouveau"),
    )
    source = fields.Selection(
        selection=[
            ('pos', "Point de vente"),
            ('sale', "Ventes"),
        ],
        string="Origine", default='pos', required=True, index=True,
        help="Canal ayant généré l'ardoise : commande POS ou commande du "
             "module Ventes. Les ardoises existantes sont d'origine POS.",
    )
    partner_id = fields.Many2one(
        'res.partner', string="Client", required=True, index=True,
        ondelete='restrict',
    )
    order_id = fields.Many2one(
        'pos.order', string="Commande POS d'origine", ondelete='set null',
        index=True,
    )
    sale_order_id = fields.Many2one(
        'sale.order', string="Commande de vente d'origine",
        ondelete='set null', index=True,
    )
    order_amount_total = fields.Monetary(
        string="Total commande", related='order_id.amount_total',
        readonly=True, currency_field='currency_id',
        help="Montant total de la commande d'origine (comptant + ardoise).",
    )
    order_paid_direct = fields.Monetary(
        string="Payé comptant à la vente",
        related='order_id.amount_paid_direct', readonly=True,
        currency_field='currency_id',
        help="Part de la commande réglée immédiatement (espèces, carte…).",
    )
    config_id = fields.Many2one(
        'pos.config', string="Caisse d'origine",
        related='order_id.config_id', store=True, readonly=True,
    )
    company_id = fields.Many2one(
        'res.company', string="Société", required=True,
        default=lambda self: self.env.company,
    )
    currency_id = fields.Many2one(
        'res.currency', string="Devise",
        related='company_id.currency_id', store=True, readonly=True,
    )

    date_open = fields.Date(
        string="Date d'ouverture", required=True, index=True,
        default=fields.Date.context_today,
    )

    amount_total = fields.Monetary(
        string="Montant initial", required=True, currency_field='currency_id',
        help="Montant total mis sur ardoise à l'ouverture.",
    )
    amount_paid = fields.Monetary(
        string="Déjà remboursé", compute='_compute_amounts', store=True,
        currency_field='currency_id',
    )
    amount_residual = fields.Monetary(
        string="Reste dû", compute='_compute_amounts', store=True,
        currency_field='currency_id', index=True,
    )

    payment_ids = fields.One2many(
        'aite.pos.credit.payment', 'credit_id', string="Remboursements",
    )
    payment_count = fields.Integer(
        string="Nb remboursements", compute='_compute_payment_count',
    )

    state = fields.Selection(
        selection=[
            ('open', "Ouverte"),
            ('paid', "Réglée"),
            ('cancelled', "Annulée"),
        ],
        string="État", default='open', required=True, index=True, copy=False,
    )

    age_days = fields.Integer(
        string="Âge (jours)", compute='_compute_age', search='_search_age_days',
        help="Nombre de jours depuis l'ouverture de l'ardoise.",
    )
    severity = fields.Selection(
        selection=[
            ('recent', "Récente"),
            ('late', "En retard"),
            ('critical', "Critique"),
            ('settled', "Réglée"),
        ],
        string="Sévérité", compute='_compute_age',
    )

    note = fields.Text(string="Note")

    # ------------------------------------------------------------------
    # Compute
    # ------------------------------------------------------------------

    @api.depends('payment_ids.amount', 'payment_ids.state', 'amount_total')
    def _compute_amounts(self):
        for credit in self:
            paid = sum(
                p.amount for p in credit.payment_ids if p.state == 'posted'
            )
            credit.amount_paid = paid
            credit.amount_residual = max(0.0, credit.amount_total - paid)
            # Bascule automatique en "réglée" quand le reste atteint zéro.
            if credit.state == 'open' and credit.amount_total > 0 \
                    and credit.amount_residual <= 0.0:
                credit.state = 'paid'
            elif credit.state == 'paid' and credit.amount_residual > 0.0:
                # Un remboursement annulé peut rouvrir l'ardoise.
                credit.state = 'open'

    @api.depends('payment_ids.state')
    def _compute_payment_count(self):
        """
        Compte des remboursements validés — compute **distinct** de
        ``_compute_amounts`` : ce champ n'est pas stocké, et le mélanger
        aux champs stockés ferait écrire en base à chaque simple lecture
        (voire lever une AccessError en contexte lecture seule).
        """
        for credit in self:
            credit.payment_count = len(
                credit.payment_ids.filtered(lambda p: p.state == 'posted')
            )

    @api.depends('date_open', 'state', 'amount_residual')
    def _compute_age(self):
        today = fields.Date.context_today(self)
        for credit in self:
            if credit.date_open:
                credit.age_days = (today - credit.date_open).days
            else:
                credit.age_days = 0
            if credit.state in ('paid', 'cancelled'):
                credit.severity = 'settled'
            elif credit.age_days >= self.AGE_THRESHOLD_CRITICAL:
                credit.severity = 'critical'
            elif credit.age_days >= self.AGE_THRESHOLD_LATE:
                credit.severity = 'late'
            else:
                credit.severity = 'recent'

    def _search_age_days(self, operator, value):
        """
        Permet de filtrer/grouper sur ``age_days`` (champ non stocké) en
        traduisant la recherche vers ``date_open``. Ex. age_days > 30
        équivaut à date_open < (aujourd'hui - 30 jours).
        """
        from datetime import timedelta
        today = fields.Date.context_today(self)
        try:
            days = int(value)
        except (TypeError, ValueError):
            raise UserError(_("La recherche sur l'âge attend un entier."))
        threshold = today - timedelta(days=days)
        # Inverser l'opérateur : âge grand <=> date ancienne.
        inverse = {
            '>': '<', '>=': '<=', '<': '>', '<=': '>=',
            '=': '=', '!=': '!=',
        }.get(operator, operator)
        return [('date_open', inverse, threshold)]

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _("Nouveau")) == _("Nouveau"):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'aite.pos.credit') or _("Nouveau")
        return super().create(vals_list)

    @api.constrains('amount_total')
    def _check_amount_total(self):
        for credit in self:
            if credit.amount_total <= 0:
                raise ValidationError(
                    _("Le montant d'une ardoise doit être strictement positif."))

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def action_register_payment(self):
        """Ouvre le wizard de remboursement pré-rempli sur cette ardoise."""
        self.ensure_one()
        if self.state != 'open':
            raise UserError(
                _("Seules les ardoises ouvertes peuvent recevoir un remboursement."))
        return {
            'type': 'ir.actions.act_window',
            'name': _("Enregistrer un remboursement"),
            'res_model': 'aite.pos.credit.repay.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_credit_id': self.id,
                'default_amount': self.amount_residual,
                'default_partner_id': self.partner_id.id,
            },
        }

    def action_view_payments(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _("Remboursements"),
            'res_model': 'aite.pos.credit.payment',
            'view_mode': 'list,form',
            'domain': [('credit_id', '=', self.id)],
            'context': {'default_credit_id': self.id},
        }

    def action_cancel(self):
        for credit in self:
            if credit.amount_paid > 0:
                raise UserError(
                    _("Impossible d'annuler une ardoise ayant déjà reçu des "
                      "remboursements. Annulez d'abord les remboursements."))
            credit.state = 'cancelled'

    def action_reopen(self):
        for credit in self:
            if credit.state == 'cancelled':
                credit.state = 'open'
