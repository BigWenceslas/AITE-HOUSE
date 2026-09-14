# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class HotelFolio(models.Model):
    """
    Folio client — la « note de séjour ».

    Ouvert à la confirmation de la réservation, le folio agrège tout ce
    que le client doit : les **nuitées** (lignes synchronisées depuis la
    réservation tant que la facture n'existe pas) et les **services**
    (restaurant, blanchisserie, minibar…) ajoutés au fil du séjour.

    Les règlements — acomptes avant l'arrivée, paiements en cours de
    séjour, solde au départ — sont des ``aite.hotel.folio.payment`` qui,
    comme dans ``aite_pos_credit``, passent une écriture débit
    trésorerie / crédit client 411. Au check-out, la facture est générée
    depuis les lignes ; les 411 des paiements sont lettrés avec ceux de la
    facture (best-effort), soldant la créance.
    """
    _name = 'aite.hotel.folio'
    _description = "Folio client (note de séjour)"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(
        string="Référence", required=True, copy=False, readonly=True,
        index=True, default=lambda self: _("Nouveau"),
    )
    reservation_id = fields.Many2one(
        'aite.hotel.reservation', string="Réservation", required=True,
        ondelete='restrict', index=True,
    )
    hotel_id = fields.Many2one(
        related='reservation_id.hotel_id', store=True, readonly=True,
        index=True,
    )
    partner_id = fields.Many2one(
        related='reservation_id.partner_id', string="Client",
        store=True, readonly=True, index=True,
    )
    checkin_date = fields.Datetime(
        related='reservation_id.checkin_date', store=True, readonly=True)
    checkout_date = fields.Datetime(
        related='reservation_id.checkout_date', store=True, readonly=True)
    reservation_state = fields.Selection(
        related='reservation_id.state', string="Séjour", readonly=True)
    company_id = fields.Many2one(
        related='reservation_id.company_id', store=True, readonly=True,
        index=True,
    )
    currency_id = fields.Many2one(
        related='reservation_id.currency_id', store=True, readonly=True,
    )

    line_ids = fields.One2many(
        'aite.hotel.folio.line', 'folio_id', string="Lignes",
    )
    payment_ids = fields.One2many(
        'aite.hotel.folio.payment', 'folio_id', string="Règlements",
    )
    payment_count = fields.Integer(
        string="Nb règlements", compute='_compute_payment_count',
    )

    amount_room = fields.Monetary(
        string="Hébergement (HT)", compute='_compute_amounts', store=True,
        currency_field='currency_id',
    )
    amount_service = fields.Monetary(
        string="Services (HT)", compute='_compute_amounts', store=True,
        currency_field='currency_id',
    )
    amount_untaxed = fields.Monetary(
        string="Total HT", compute='_compute_amounts', store=True,
        currency_field='currency_id',
    )
    amount_tax = fields.Monetary(
        string="Taxes", compute='_compute_amounts', store=True,
        currency_field='currency_id',
    )
    amount_total = fields.Monetary(
        string="Total TTC", compute='_compute_amounts', store=True,
        currency_field='currency_id',
    )
    amount_paid = fields.Monetary(
        string="Encaissé", compute='_compute_amounts', store=True,
        currency_field='currency_id',
    )
    amount_residual = fields.Monetary(
        string="Solde dû", compute='_compute_amounts', store=True,
        currency_field='currency_id', index=True,
    )

    move_id = fields.Many2one(
        'account.move', string="Facture", readonly=True, copy=False,
    )
    move_payment_state = fields.Selection(
        related='move_id.payment_state', string="État facture",
        readonly=True,
    )

    state = fields.Selection(
        selection=[
            ('open', "Ouvert"),
            ('invoiced', "Facturé"),
            ('paid', "Soldé"),
            ('cancelled', "Annulé"),
        ],
        string="État", default='open', required=True, index=True,
        copy=False, tracking=True,
    )
    note = fields.Text(string="Note")

    # ------------------------------------------------------------------
    # Compute
    # ------------------------------------------------------------------

    @api.depends('line_ids.price_subtotal', 'line_ids.price_total',
                 'line_ids.line_type', 'payment_ids.amount',
                 'payment_ids.state', 'state')
    def _compute_amounts(self):
        for folio in self:
            room_lines = folio.line_ids.filtered(
                lambda l: l.line_type == 'room')
            service_lines = folio.line_ids - room_lines
            folio.amount_room = sum(room_lines.mapped('price_subtotal'))
            folio.amount_service = sum(
                service_lines.mapped('price_subtotal'))
            folio.amount_untaxed = folio.amount_room + folio.amount_service
            total = sum(folio.line_ids.mapped('price_total'))
            folio.amount_tax = total - folio.amount_untaxed
            folio.amount_total = total
            posted = folio.payment_ids.filtered(
                lambda p: p.state == 'posted')
            folio.amount_paid = sum(posted.mapped('amount'))
            folio.amount_residual = max(
                0.0, folio.amount_total - folio.amount_paid)
            # Bascule automatique facturé → soldé (et retour si un
            # règlement est annulé).
            if folio.state == 'invoiced' and folio.amount_total > 0 \
                    and folio.amount_residual <= 0.0:
                folio.state = 'paid'
            elif folio.state == 'paid' and folio.amount_residual > 0.0:
                folio.state = 'invoiced'

    @api.depends('payment_ids.state')
    def _compute_payment_count(self):
        """
        Nombre de règlements validés — compute **distinct** de
        ``_compute_amounts`` : ce champ n'est pas stocké, et le mélanger
        aux champs stockés ferait écrire en base à chaque simple lecture
        (voire lever une AccessError en contexte lecture seule).
        """
        for folio in self:
            folio.payment_count = len(
                folio.payment_ids.filtered(lambda p: p.state == 'posted'))

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _("Nouveau")) == _("Nouveau"):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'aite.hotel.folio') or _("Nouveau")
        return super().create(vals_list)

    @api.ondelete(at_uninstall=False)
    def _unlink_guard(self):
        for folio in self:
            if folio.move_id or folio.amount_paid > 0:
                raise UserError(
                    _("Le folio %s porte une facture ou des règlements : "
                      "il ne peut pas être supprimé.", folio.name))

    # ------------------------------------------------------------------
    # Synchronisation des nuitées
    # ------------------------------------------------------------------

    def _sync_room_lines(self):
        """
        Aligne les lignes « nuitées » du folio sur les lignes de la
        réservation (chambres, nuits, prix). Ne touche jamais aux lignes
        de service, ni à rien après facturation.
        """
        for folio in self:
            if folio.move_id or folio.state in ('invoiced', 'paid',
                                                'cancelled'):
                continue
            room_lines = folio.line_ids.filtered(
                lambda l: l.line_type == 'room')
            existing = {
                line.reservation_line_id.id: line
                for line in room_lines
                if line.reservation_line_id
            }
            seen = set()
            for rline in folio.reservation_id.line_ids:
                seen.add(rline.id)
                vals = folio._prepare_room_line_vals(rline)
                if rline.id in existing:
                    existing[rline.id].write(vals)
                else:
                    vals['folio_id'] = folio.id
                    self.env['aite.hotel.folio.line'].create(vals)
            # Nuitées orphelines (chambre retirée de la réservation).
            # Le champ ``reservation_line_id`` est en ``ondelete='set null'``
            # — supprimer la ligne de séjour le vide au lieu de retirer la
            # nuitée : sans ce second filtre, le client resterait facturé
            # pour une chambre qui ne fait plus partie du séjour.
            orphans = folio.env['aite.hotel.folio.line']
            for rline_id, fline in existing.items():
                if rline_id not in seen:
                    orphans |= fline
            orphans |= room_lines.filtered(
                lambda l: not l.reservation_line_id)
            if orphans:
                orphans.unlink()

    def _prepare_room_line_vals(self, rline):
        self.ensure_one()
        product = rline.room_type_id.product_id
        return {
            'line_type': 'room',
            'reservation_line_id': rline.id,
            'product_id': product.id,
            'name': _("Nuitée %(room)s (%(type)s) — %(cin)s → %(cout)s",
                      room=rline.room_id.name,
                      type=rline.room_type_id.name,
                      cin=rline.checkin_date.date(),
                      cout=rline.checkout_date.date()),
            'quantity': rline.nights,
            'price_unit': rline.price_night,
            'tax_ids': [(6, 0, product.taxes_id.filtered(
                lambda t: t.company_id == self.company_id).ids)],
            'date': fields.Date.context_today(self),
        }

    # ------------------------------------------------------------------
    # Facturation
    # ------------------------------------------------------------------

    def _prepare_invoice_vals(self):
        self.ensure_one()
        return {
            'move_type': 'out_invoice',
            'partner_id': self.partner_id.id,
            'company_id': self.company_id.id,
            'currency_id': self.currency_id.id,
            'invoice_date': fields.Date.context_today(self),
            'invoice_origin': "%s / %s" % (
                self.reservation_id.name, self.name),
            'ref': self.name,
            'invoice_line_ids': [
                (0, 0, {
                    'product_id': line.product_id.id,
                    'name': line.name,
                    'quantity': line.quantity,
                    'price_unit': line.price_unit,
                    'tax_ids': [(6, 0, line.tax_ids.ids)],
                }) for line in self.line_ids
            ],
        }

    def action_create_invoice(self):
        """
        Génère et comptabilise la facture client depuis les lignes du
        folio, puis lettre les acomptes déjà encaissés (best-effort).
        """
        self.ensure_one()
        if self.move_id:
            raise UserError(_("Le folio est déjà facturé (%s).",
                              self.move_id.name))
        if not self.line_ids:
            raise UserError(_("Le folio ne contient aucune ligne à "
                              "facturer."))
        move = self.env['account.move'].create(self._prepare_invoice_vals())
        move.action_post()
        self.write({'move_id': move.id, 'state': 'invoiced'})
        for payment in self.payment_ids.filtered(
                lambda p: p.state == 'posted' and p.move_id):
            payment._reconcile_with_invoice()
        # Le compute peut basculer 'invoiced' → 'paid' si tout est réglé.
        self._compute_amounts()
        return self.action_view_invoice()

    def action_view_invoice(self):
        self.ensure_one()
        if not self.move_id:
            raise UserError(_("Aucune facture liée à ce folio."))
        return {
            'type': 'ir.actions.act_window',
            'name': _("Facture"),
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': self.move_id.id,
        }

    # ------------------------------------------------------------------
    # Règlements
    # ------------------------------------------------------------------

    def action_register_payment(self):
        self.ensure_one()
        if self.state == 'cancelled':
            raise UserError(_("Ce folio est annulé."))
        default_amount = self.amount_residual or self.amount_total
        return {
            'type': 'ir.actions.act_window',
            'name': _("Encaisser un règlement"),
            'res_model': 'aite.hotel.payment.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_folio_id': self.id,
                'default_amount': default_amount,
            },
        }

    def action_view_payments(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _("Règlements"),
            'res_model': 'aite.hotel.folio.payment',
            'view_mode': 'list,form',
            'domain': [('folio_id', '=', self.id)],
            'context': {'default_folio_id': self.id},
        }

    def action_cancel(self):
        for folio in self:
            if folio.amount_paid > 0:
                raise UserError(
                    _("Impossible d'annuler un folio ayant encaissé des "
                      "règlements : annulez-les d'abord."))
            if folio.move_id and folio.move_id.state == 'posted':
                raise UserError(
                    _("Le folio est facturé : passez par un avoir sur la "
                      "facture %s.", folio.move_id.name))
            folio.state = 'cancelled'
        return True


class HotelFolioLine(models.Model):
    """
    Ligne de folio : une nuitée (synchronisée) ou un service (libre).

    Le montant TTC est calculé via ``taxes.compute_all`` sur les taxes de
    l'article, garantissant l'exacte égalité avec la future facture.
    """
    _name = 'aite.hotel.folio.line'
    _description = "Ligne de folio"
    _order = 'date, id'

    folio_id = fields.Many2one(
        'aite.hotel.folio', string="Folio", required=True,
        ondelete='cascade', index=True,
    )
    company_id = fields.Many2one(
        related='folio_id.company_id', store=True, readonly=True,
    )
    currency_id = fields.Many2one(
        related='folio_id.currency_id', store=True, readonly=True,
    )
    partner_id = fields.Many2one(
        related='folio_id.partner_id', store=True, readonly=True,
    )
    line_type = fields.Selection(
        selection=[('room', "Nuitée"), ('service', "Service")],
        string="Type", default='service', required=True, index=True,
    )
    reservation_line_id = fields.Many2one(
        'aite.hotel.reservation.line', string="Ligne séjour",
        ondelete='set null',
        help="Ligne de réservation d'origine pour les nuitées "
             "synchronisées.",
    )
    service_id = fields.Many2one(
        'aite.hotel.service', string="Service",
        domain="[('company_id', '=', company_id)]",
    )
    product_id = fields.Many2one(
        'product.product', string="Article", required=True,
    )
    name = fields.Char(string="Libellé", required=True)
    date = fields.Date(
        string="Date", required=True,
        default=fields.Date.context_today,
    )
    quantity = fields.Float(string="Qté", default=1.0, required=True)
    price_unit = fields.Monetary(
        string="Prix unitaire", required=True, currency_field='currency_id',
    )
    tax_ids = fields.Many2many(
        'account.tax', string="Taxes",
        domain="[('type_tax_use', '=', 'sale'),"
               " ('company_id', '=', company_id)]",
    )
    price_subtotal = fields.Monetary(
        string="Sous-total (HT)", compute='_compute_prices', store=True,
        currency_field='currency_id',
    )
    price_total = fields.Monetary(
        string="Total (TTC)", compute='_compute_prices', store=True,
        currency_field='currency_id',
    )

    @api.onchange('service_id')
    def _onchange_service_id(self):
        if self.service_id:
            self.product_id = self.service_id.product_id
            self.name = self.service_id.name
            self.price_unit = self.service_id.price
            self.tax_ids = self.service_id.product_id.taxes_id.filtered(
                lambda t: t.company_id == self.company_id)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            if not self.name:
                self.name = self.product_id.display_name
            if not self.price_unit:
                self.price_unit = self.product_id.lst_price
            self.tax_ids = self.product_id.taxes_id.filtered(
                lambda t: t.company_id == self.company_id)

    @api.depends('quantity', 'price_unit', 'tax_ids')
    def _compute_prices(self):
        for line in self:
            subtotal = line.quantity * line.price_unit
            if line.tax_ids:
                taxes = line.tax_ids.compute_all(
                    line.price_unit, currency=line.currency_id,
                    quantity=line.quantity, product=line.product_id,
                    partner=line.partner_id)
                line.price_subtotal = taxes['total_excluded']
                line.price_total = taxes['total_included']
            else:
                line.price_subtotal = subtotal
                line.price_total = subtotal

    @api.constrains('quantity', 'price_unit')
    def _check_positive(self):
        for line in self:
            if line.quantity <= 0:
                raise ValidationError(
                    _("La quantité d'une ligne de folio doit être "
                      "positive."))

    @api.ondelete(at_uninstall=False)
    def _unlink_guard(self):
        for line in self:
            if line.folio_id.move_id:
                raise UserError(
                    _("Le folio est facturé : ses lignes ne peuvent plus "
                      "être supprimées."))


class HotelFolioPayment(models.Model):
    """
    Règlement d'un folio (acompte ou paiement).

    Reprend à l'identique la mécanique éprouvée de
    ``aite.pos.credit.payment`` : moyens de paiement du contexte local
    (MTN MoMo, Orange Money, espèces, carte, virement) et, si la société
    l'active, écriture **débit trésorerie / crédit client 411** à la
    validation, lettrée ensuite avec la facture du folio.
    """
    _name = 'aite.hotel.folio.payment'
    _description = "Règlement de folio"
    _order = 'date desc, id desc'
    _rec_name = 'folio_id'

    folio_id = fields.Many2one(
        'aite.hotel.folio', string="Folio", required=True,
        ondelete='cascade', index=True,
    )
    partner_id = fields.Many2one(
        related='folio_id.partner_id', string="Client", store=True,
        readonly=True,
    )
    company_id = fields.Many2one(
        related='folio_id.company_id', store=True, readonly=True,
    )
    currency_id = fields.Many2one(
        related='folio_id.currency_id', store=True, readonly=True,
    )
    hotel_id = fields.Many2one(
        related='folio_id.hotel_id', store=True, readonly=True,
    )

    date = fields.Date(
        string="Date", required=True, index=True,
        default=fields.Date.context_today,
    )
    amount = fields.Monetary(
        string="Montant", required=True, currency_field='currency_id',
    )
    is_deposit = fields.Boolean(
        string="Acompte",
        help="Coché pour un versement reçu avant l'arrivée ; purement "
             "indicatif (même circuit comptable).",
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
        index=True,
    )
    transaction_ref = fields.Char(
        string="Réf. transaction",
        help="Identifiant Mobile Money ou référence de l'encaissement.",
    )
    collected_by = fields.Many2one(
        'res.users', string="Encaissé par",
        default=lambda self: self.env.user,
    )
    move_id = fields.Many2one(
        'account.move', string="Écriture comptable", readonly=True,
        copy=False,
        help="Écriture d'encaissement (411) générée à la validation.",
    )
    state = fields.Selection(
        selection=[
            ('posted', "Validé"),
            ('cancelled', "Annulé"),
        ],
        string="État", default='posted', required=True, index=True,
        copy=False,
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
                    _("Le montant d'un règlement doit être positif."))

    @api.constrains('amount', 'folio_id', 'state')
    def _check_not_overpaid(self):
        """Empêche d'encaisser au-delà du total du folio."""
        for pay in self:
            if pay.state != 'posted':
                continue
            folio = pay.folio_id
            others = sum(
                p.amount for p in folio.payment_ids
                if p.state == 'posted' and p.id != pay.id)
            available = folio.amount_total - others
            if pay.amount - available > 0.01:  # tolérance d'arrondi
                raise ValidationError(_(
                    "Le règlement (%(amt)s) dépasse le solde du folio "
                    "(%(res)s).",
                    amt=pay.amount, res=max(0.0, available)))

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
        Journal d'encaissement selon le moyen de paiement.

        Priorité : journal configuré sur la société → journal de caisse
        pour les espèces / de banque pour le reste → premier journal de
        trésorerie disponible.
        """
        self.ensure_one()
        company = self.company_id or self.env.company
        if company.hotel_payment_journal_id:
            return company.hotel_payment_journal_id

        # ``sudo`` : la réception encaisse sans détenir les droits
        # comptables. Le choix du journal est une mécanique interne ; le
        # contrôle d'accès porte sur le règlement de folio lui-même.
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
        Écriture d'encaissement : débit trésorerie / crédit client 411.

        Silencieux si la société n'a pas activé la comptabilisation ou si
        la configuration est incomplète — le suivi du folio reste alors
        purement applicatif, comme sur les ardoises POS.
        """
        self.ensure_one()
        company = self.company_id or self.env.company
        if not company.hotel_auto_entries:
            return
        if self.move_id:
            return

        partner = self.partner_id
        # ``sudo`` sur la résolution du compte 411 pour la même raison que
        # le journal : la réception n'a pas accès au plan comptable.
        receivable = company.sudo()._get_hotel_receivable_account(
            partner.sudo())
        journal = self._journal_for_method()
        if not receivable or not journal:
            return
        counterpart = (
            journal.default_account_id or journal.suspense_account_id)
        if not counterpart:
            return

        label = _("Règlement folio %s", self.folio_id.name)
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
        self._reconcile_with_invoice()

    def _reconcile_with_invoice(self):
        """
        Lettre le 411 du règlement avec le 411 de la facture du folio
        (best-effort : jamais bloquant).
        """
        self.ensure_one()
        invoice = self.folio_id.move_id
        if not (invoice and self.move_id):
            return
        pay_lines = self.move_id.line_ids.filtered(
            lambda l: l.account_id.account_type == 'asset_receivable'
            and not l.reconciled)
        inv_lines = invoice.line_ids.filtered(
            lambda l: l.account_id.account_type == 'asset_receivable'
            and not l.reconciled)
        to_reconcile = pay_lines | inv_lines
        if len(to_reconcile) >= 2:
            try:
                to_reconcile.reconcile()
            except Exception:
                # Le lettrage est un confort : on ne bloque jamais.
                pass

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def action_cancel(self):
        for pay in self:
            if pay.move_id and pay.move_id.state == 'posted':
                try:
                    pay.move_id.button_draft()
                    pay.move_id.button_cancel()
                except Exception:
                    pass
            pay.state = 'cancelled'
        return True

    def action_post(self):
        for pay in self:
            pay.state = 'posted'
            pay._post_accounting_entry()
        return True

    @api.model
    def method_label(self, code):
        """Libellé lisible d'un moyen de paiement (dashboard)."""
        return dict(self._fields['method'].selection).get(code, code)
