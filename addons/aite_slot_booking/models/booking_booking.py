# -*- coding: utf-8 -*-
import logging
from datetime import timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

from .booking_resource import KINDS

_logger = logging.getLogger(__name__)


class SlotBooking(models.Model):
    """
    Réservation d'un créneau : espace VIP/VVIP à l'heure, rendez-vous
    SPA / coiffure, dépôt pressing.

    Règles clés (fonctions pures, extraites et exécutées par les tests) :

    * ``_slot_price`` — tarif : prix manuel > prestation × quantité >
      heures × tarif horaire de la ressource ;
    * ``_check_alignment`` — le créneau respecte l'ordre, les horaires
      d'ouverture et la grille (pas de 30/60 min) de la ressource ;
    * conflits — ``_overlap_count`` (ressource) sur les réservations
      confirmées/réalisées, comparé à la capacité.

    Workflow : brouillon → confirmée (e-mail auto optionnel) → réalisée
    (report au folio optionnel) ; annulation, no-show (manuel ou cron).
    Pressing : quantité d'articles + date/indicateur de retrait.
    """
    _name = 'aite.slot.booking'
    _description = "Réservation de créneau (espace / prestation)"
    _inherit = ['mail.thread']
    _order = 'start desc, id desc'

    name = fields.Char(
        string="Référence", required=True, copy=False, readonly=True,
        index=True, default=lambda self: _("Nouveau"),
    )
    resource_id = fields.Many2one(
        'aite.booking.resource', string="Ressource", required=True,
        ondelete='restrict', index=True,
    )
    kind = fields.Selection(
        related='resource_id.kind', store=True, string="Famille",
        index=True,
    )
    color = fields.Char(related='resource_id.color')
    partner_id = fields.Many2one(
        'res.partner', string="Client", required=True, index=True,
        ondelete='restrict',
    )
    partner_phone = fields.Char(
        related='partner_id.phone', string="Téléphone", readonly=True)
    company_id = fields.Many2one(
        'res.company', string="Société", required=True,
        default=lambda self: self.env.company,
    )
    currency_id = fields.Many2one(
        related='company_id.currency_id', readonly=True)

    service_id = fields.Many2one(
        'aite.booking.service', string="Prestation",
        domain="[('kind', '=', kind), ('company_id', '=', company_id)]",
        help="Optionnelle pour les espaces (tarif horaire) ; recommandée "
             "pour SPA, coiffure et pressing.",
    )
    qty = fields.Integer(
        string="Quantité", default=1,
        help="Nombre d'articles (pressing : chemises, costumes…).",
    )
    start = fields.Datetime(string="Début", required=True, index=True)
    stop = fields.Datetime(string="Fin", required=True, index=True)
    duration_hours = fields.Float(
        string="Durée (h)", compute='_compute_duration', store=True,
    )

    amount_manual = fields.Monetary(
        string="Prix manuel", currency_field='currency_id',
        help="Si renseigné (> 0), remplace le calcul automatique.",
    )
    amount = fields.Monetary(
        string="Montant", compute='_compute_amount', store=True,
        currency_field='currency_id',
    )

    state = fields.Selection(
        selection=[
            ('draft', "Brouillon"),
            ('confirmed', "Confirmée"),
            ('done', "Réalisée"),
            ('cancelled', "Annulée"),
            ('no_show', "No-show"),
        ],
        string="État", default='draft', required=True, index=True,
        copy=False, tracking=True,
    )
    source = fields.Selection(
        selection=[('desk', "Comptoir"), ('online', "En ligne")],
        string="Origine", default='desk', required=True, index=True,
    )

    folio_id = fields.Many2one(
        'aite.hotel.folio', string="Folio du séjour",
        domain="[('partner_id', '=', partner_id), ('state', '=', 'open')]",
        help="Folio sur lequel reporter la prestation (note de séjour).",
    )
    posted_line_id = fields.Many2one(
        'aite.hotel.folio.line', string="Ligne de folio", readonly=True,
        copy=False,
        help="Ligne créée sur le folio — garantit l'idempotence du "
             "report.",
    )

    # Pressing
    pickup_date = fields.Datetime(string="Retrait prévu")
    pickup_done = fields.Boolean(string="Retiré", default=False)

    note = fields.Text(string="Note")

    # ------------------------------------------------------------------
    # Calcul pur (extrait et exécuté tel quel par les tests)
    # ------------------------------------------------------------------

    @staticmethod
    def _slot_price(service_price, qty, duration_hours, price_hour,
                    manual_price):
        """
        Tarif d'une réservation, par ordre de priorité :
        prix manuel (> 0) → prestation × quantité → heures × tarif
        horaire de la ressource.
        """
        if manual_price and manual_price > 0:
            return manual_price
        if service_price and service_price > 0:
            q = qty if qty and qty > 0 else 1
            return service_price * q
        return (duration_hours or 0.0) * (price_hour or 0.0)

    @staticmethod
    def _check_alignment(start_h, stop_h, open_h, close_h, step_min):
        """
        Vérifie qu'un créneau [start_h, stop_h) (heures locales
        décimales) est valide pour une ressource.

        :returns: '' si OK, sinon un code : 'order' (fin avant début),
            'hours' (hors horaires d'ouverture), 'grid' (non aligné sur
            le pas de créneau).
        """
        eps = 1e-6
        if stop_h <= start_h + eps:
            return 'order'
        if start_h < open_h - eps or stop_h > close_h + eps:
            return 'hours'
        step = (step_min or 60) / 60.0
        for x in (start_h, stop_h):
            k = (x - open_h) / step
            if abs(k - round(k)) > eps:
                return 'grid'
        return ''

    @staticmethod
    def _folio_line_vals(folio_id, product_id, label, date_str, quantity,
                         price_unit):
        """
        Valeurs de la ligne de folio (contrat du PMS : ``line_type``
        'service', ``product_id`` requis, ``quantity``/``price_unit``).
        Construit ici pour être testé avec le code réel.
        """
        return {
            'folio_id': folio_id,
            'line_type': 'service',
            'product_id': product_id,
            'name': label,
            'date': date_str,
            'quantity': quantity if quantity and quantity > 0 else 1,
            'price_unit': price_unit,
        }

    # ------------------------------------------------------------------
    # Computes & onchange
    # ------------------------------------------------------------------

    @api.depends('start', 'stop')
    def _compute_duration(self):
        for rec in self:
            if rec.start and rec.stop and rec.stop > rec.start:
                rec.duration_hours = \
                    (rec.stop - rec.start).total_seconds() / 3600.0
            else:
                rec.duration_hours = 0.0

    @api.depends('service_id.price', 'qty', 'duration_hours',
                 'resource_id.price_hour', 'amount_manual')
    def _compute_amount(self):
        for rec in self:
            rec.amount = rec._slot_price(
                rec.service_id.price if rec.service_id else 0.0,
                rec.qty,
                rec.duration_hours,
                rec.resource_id.price_hour if rec.resource_id else 0.0,
                rec.amount_manual,
            )

    @api.onchange('service_id', 'start')
    def _onchange_service_start(self):
        if self.service_id and self.start:
            self.stop = self.start + timedelta(
                minutes=self.service_id.duration_minutes or 60)

    @api.onchange('resource_id')
    def _onchange_resource(self):
        if self.resource_id and self.service_id \
                and self.service_id.kind != self.resource_id.kind:
            self.service_id = False

    # ------------------------------------------------------------------
    # Contraintes
    # ------------------------------------------------------------------

    @api.constrains('start', 'stop', 'resource_id')
    def _check_slot_valid(self):
        for rec in self:
            if not (rec.start and rec.stop and rec.resource_id):
                continue
            res = rec.resource_id
            s_local = fields.Datetime.context_timestamp(rec, rec.start)
            e_local = fields.Datetime.context_timestamp(rec, rec.stop)
            if s_local.date() != e_local.date():
                raise ValidationError(_(
                    "Un créneau ne peut pas franchir minuit "
                    "(%(res)s).", res=res.name))
            s_h = s_local.hour + s_local.minute / 60.0
            e_h = e_local.hour + e_local.minute / 60.0
            code = rec._check_alignment(
                s_h, e_h, res.open_hour, res.close_hour,
                int(res.slot_minutes or '60'))
            if code == 'order':
                raise ValidationError(
                    _("La fin doit être après le début."))
            if code == 'hours':
                raise ValidationError(_(
                    "Créneau hors horaires de « %(res)s » "
                    "(%(o).2f – %(c).2f).",
                    res=res.name, o=res.open_hour, c=res.close_hour))
            if code == 'grid':
                raise ValidationError(_(
                    "Le créneau doit être aligné sur le pas de "
                    "%(m)s minutes de « %(res)s ».",
                    m=res.slot_minutes, res=res.name))

    @api.constrains('start', 'stop', 'resource_id', 'state')
    def _check_no_conflict(self):
        Resource = self.env['aite.booking.resource']
        for rec in self:
            if rec.state not in ('confirmed', 'done'):
                continue
            if not (rec.start and rec.stop and rec.resource_id):
                continue
            others = self.search([
                ('id', '!=', rec.id),
                ('resource_id', '=', rec.resource_id.id),
                ('state', 'in', ('confirmed', 'done')),
                ('start', '<', rec.stop),
                ('stop', '>', rec.start),
            ])
            busy = [(o.start, o.stop) for o in others]
            used = Resource._overlap_count(busy, rec.start, rec.stop)
            if used + 1 > rec.resource_id.capacity:
                raise ValidationError(_(
                    "Conflit : « %(res)s » est complète sur ce créneau "
                    "(capacité %(cap)s).",
                    res=rec.resource_id.name,
                    cap=rec.resource_id.capacity))

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _("Nouveau")) == _("Nouveau"):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'aite.slot.booking') or _("Nouveau")
        return super().create(vals_list)

    # ------------------------------------------------------------------
    # Workflow
    # ------------------------------------------------------------------

    def action_confirm(self):
        for rec in self:
            if rec.state != 'draft':
                continue
            rec.state = 'confirmed'
            if rec.company_id.aite_slot_mail_on_confirm:
                rec._send_confirmation(raise_if_fail=False)
        return True

    def action_send_confirmation(self):
        self.ensure_one()
        self._send_confirmation(raise_if_fail=True)
        return True

    def _send_confirmation(self, raise_if_fail=False):
        self.ensure_one()
        template = self.env.ref(
            'aite_slot_booking.mail_template_slot_confirmation',
            raise_if_not_found=False)
        if not template:
            if raise_if_fail:
                raise UserError(_("Modèle d'e-mail introuvable."))
            return
        if not self.partner_id.email:
            if raise_if_fail:
                raise UserError(_(
                    "Le client n'a pas d'adresse e-mail."))
            _logger.info(
                "Slot %s : pas d'e-mail client, confirmation non "
                "envoyée.", self.name)
            return
        template.send_mail(self.id, force_send=False)

    def action_done(self):
        for rec in self:
            if rec.state != 'confirmed':
                raise UserError(_(
                    "Seule une réservation confirmée peut être marquée "
                    "réalisée."))
            rec.state = 'done'
            if rec.company_id.aite_slot_auto_post_folio:
                try:
                    rec.action_post_to_folio(silent=True)
                except UserError:
                    pass  # pas de folio ouvert unique : report manuel
        return True

    def action_cancel(self):
        for rec in self:
            if rec.state in ('done',):
                raise UserError(_(
                    "Une prestation réalisée ne peut pas être annulée."))
            rec.state = 'cancelled'
        return True

    def action_no_show(self):
        for rec in self:
            if rec.state != 'confirmed':
                raise UserError(_(
                    "Seule une réservation confirmée peut passer en "
                    "no-show."))
            rec.state = 'no_show'
        return True

    def action_reset_draft(self):
        for rec in self:
            if rec.state in ('cancelled', 'no_show'):
                rec.state = 'draft'
        return True

    def action_mark_picked_up(self):
        for rec in self:
            rec.pickup_done = True
        return True

    # ------------------------------------------------------------------
    # Report au folio (note de séjour)
    # ------------------------------------------------------------------

    def _find_open_folio(self):
        self.ensure_one()
        if self.folio_id and self.folio_id.state == 'open':
            return self.folio_id
        folios = self.env['aite.hotel.folio'].search([
            ('partner_id', '=', self.partner_id.id),
            ('state', '=', 'open'),
            ('company_id', '=', self.company_id.id),
        ])
        if len(folios) == 1:
            return folios
        return self.env['aite.hotel.folio']

    def action_post_to_folio(self, silent=False):
        for rec in self:
            if rec.posted_line_id:
                if not silent:
                    raise UserError(_(
                        "Déjà reportée au folio (%(f)s).",
                        f=rec.posted_line_id.folio_id.name))
                continue
            folio = rec._find_open_folio()
            if not folio:
                raise UserError(_(
                    "Aucun folio ouvert unique pour %(p)s — choisissez "
                    "le folio sur la réservation.",
                    p=rec.partner_id.name))
            product = rec.service_id.product_id if rec.service_id \
                else False
            if not product:
                raise UserError(_(
                    "Une prestation avec article est requise pour le "
                    "report au folio (le folio exige un article)."))
            unit = rec.amount / (rec.qty or 1) if rec.qty else rec.amount
            label = _("%(srv)s — %(ref)s",
                      srv=rec.service_id.name, ref=rec.name)
            vals = rec._folio_line_vals(
                folio.id, product.id, label,
                fields.Date.to_string(
                    fields.Date.context_today(rec)),
                rec.qty or 1, unit)
            line = self.env['aite.hotel.folio.line'].create(vals)
            rec.posted_line_id = line.id
            rec.folio_id = folio.id
            _logger.info(
                "Slot %s : reporté au folio %s (%.0f).",
                rec.name, folio.name, rec.amount)
        return True

    # ------------------------------------------------------------------
    # Cron
    # ------------------------------------------------------------------

    @api.model
    def _cron_slot_no_show(self):
        """Confirmées dont la fin + délai de grâce est dépassée →
        no-show."""
        for company in self.env['res.company'].search([]):
            grace = company.aite_slot_no_show_hours or 6
            limit = fields.Datetime.now() - timedelta(hours=grace)
            stale = self.search([
                ('company_id', '=', company.id),
                ('state', '=', 'confirmed'),
                ('stop', '<', limit),
            ])
            for rec in stale:
                rec.state = 'no_show'
            if stale:
                _logger.info(
                    "Slot cron : %s réservation(s) passée(s) en "
                    "no-show (%s).", len(stale), company.name)
        return True
