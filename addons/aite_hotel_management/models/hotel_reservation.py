# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class HotelReservation(models.Model):
    """
    Réservation de séjour.

    Une réservation couvre **une période** (arrivée → départ) et une ou
    plusieurs chambres via ses lignes. Workflow :

        brouillon → confirmée → arrivée (check-in) → départ (check-out)
                  ↘ annulée / no-show

    À la confirmation, le contrôle de disponibilité verrouille les
    chambres et un **folio** est ouvert : il portera nuitées, services et
    règlements jusqu'à la facturation au départ. Les séjours multi-
    périodes (dates différentes par chambre) se gèrent par réservations
    séparées — choix assumé, aligné sur la pratique des PMS du marché.
    """
    _name = 'aite.hotel.reservation'
    _description = "Réservation hôtelière"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'checkin_date desc, id desc'

    name = fields.Char(
        string="Référence", required=True, copy=False, readonly=True,
        index=True, default=lambda self: _("Nouveau"),
    )
    hotel_id = fields.Many2one(
        'aite.hotel.hotel', string="Hôtel", required=True, index=True,
        default=lambda self: self.env['aite.hotel.hotel'].search(
            [('company_id', '=', self.env.company.id)], limit=1),
        tracking=True,
    )
    company_id = fields.Many2one(
        'res.company', related='hotel_id.company_id', store=True,
        readonly=True, index=True,
    )
    currency_id = fields.Many2one(
        'res.currency', related='company_id.currency_id', store=True,
        readonly=True,
    )
    partner_id = fields.Many2one(
        'res.partner', string="Client", required=True, index=True,
        tracking=True, domain="[('is_company', '=', False)]",
    )
    partner_phone = fields.Char(
        related='partner_id.phone', string="Téléphone", readonly=True)
    partner_email = fields.Char(
        related='partner_id.email', string="E-mail", readonly=True)

    checkin_date = fields.Datetime(
        string="Arrivée", required=True, index=True, tracking=True,
        default=lambda self: self._default_checkin(),
    )
    checkout_date = fields.Datetime(
        string="Départ", required=True, index=True, tracking=True,
        default=lambda self: self._default_checkout(),
    )
    nights = fields.Integer(
        string="Nuits", compute='_compute_nights', store=True,
        help="Nombre de nuitées facturées : différence de dates "
             "calendaires, minimum 1 (day-use = 1 nuitée).",
    )

    source = fields.Selection(
        selection=[
            ('direct', "Direct / comptoir"),
            ('phone', "Téléphone / WhatsApp"),
            ('website', "Site web"),
            ('ota', "OTA (Booking, Expedia…)"),
            ('agent', "Agent / apporteur"),
        ],
        string="Canal", default='direct', required=True, index=True,
        tracking=True,
    )
    agent_id = fields.Many2one(
        'res.partner', string="Agent / apporteur",
        domain="[('is_booking_agent', '=', True)]",
        help="Apporteur d'affaires commissionné sur cette réservation.",
    )
    commission_type = fields.Selection(
        selection=[('percent', "Pourcentage"), ('fixed', "Montant fixe")],
        string="Type de commission", default='percent',
    )
    commission_rate = fields.Float(
        string="Taux / montant",
        help="Pourcentage du total hébergement HT, ou montant fixe selon "
             "le type.",
    )
    commission_amount = fields.Monetary(
        string="Commission", compute='_compute_commission', store=True,
        currency_field='currency_id',
        help="Commission due à l'agent (information de pilotage ; le "
             "règlement de l'agent se fait via une facture fournisseur "
             "classique).",
    )

    line_ids = fields.One2many(
        'aite.hotel.reservation.line', 'reservation_id', string="Chambres",
        copy=True,
    )
    room_count = fields.Integer(
        string="Nb chambres", compute='_compute_totals', store=True)
    adults = fields.Integer(
        string="Adultes", compute='_compute_totals', store=True)
    children = fields.Integer(
        string="Enfants", compute='_compute_totals', store=True)
    amount_room_total = fields.Monetary(
        string="Total hébergement (HT)", compute='_compute_totals',
        store=True, currency_field='currency_id',
    )

    folio_id = fields.Many2one(
        'aite.hotel.folio', string="Folio", readonly=True, copy=False,
    )
    folio_amount_residual = fields.Monetary(
        related='folio_id.amount_residual', string="Solde folio",
        readonly=True, currency_field='currency_id',
    )
    folio_amount_paid = fields.Monetary(
        related='folio_id.amount_paid', string="Encaissé",
        readonly=True, currency_field='currency_id',
    )

    state = fields.Selection(
        selection=[
            ('draft', "Brouillon"),
            ('confirmed', "Confirmée"),
            ('checked_in', "Arrivé"),
            ('checked_out', "Parti"),
            ('cancelled', "Annulée"),
            ('no_show', "No-show"),
        ],
        string="État", default='draft', required=True, index=True,
        copy=False, tracking=True,
    )

    actual_checkin = fields.Datetime(string="Check-in réel", readonly=True, copy=False)
    actual_checkout = fields.Datetime(string="Check-out réel", readonly=True, copy=False)
    note = fields.Text(string="Demandes particulières")

    # ------------------------------------------------------------------
    # Defaults
    # ------------------------------------------------------------------

    @api.model
    def _default_checkin(self):
        hotel = self.env['aite.hotel.hotel'].search(
            [('company_id', '=', self.env.company.id)], limit=1)
        hour = hotel.checkin_hour if hotel else 14.0
        today = fields.Date.context_today(self)
        return self._compose_datetime(today, hour)

    @api.model
    def _default_checkout(self):
        hotel = self.env['aite.hotel.hotel'].search(
            [('company_id', '=', self.env.company.id)], limit=1)
        hour = hotel.checkout_hour if hotel else 12.0
        tomorrow = fields.Date.context_today(self) + timedelta(days=1)
        return self._compose_datetime(tomorrow, hour)

    @api.model
    def _compose_datetime(self, day, float_hour):
        """Assemble une date + heure décimale (locale) en Datetime UTC."""
        hours = int(float_hour)
        minutes = int(round((float_hour - hours) * 60))
        naive = fields.Datetime.to_datetime(str(day)).replace(
            hour=hours, minute=minutes, second=0)
        # La saisie est pensée en heure locale de l'utilisateur : convertir
        # vers l'UTC de stockage.
        return self._local_to_utc(naive)

    @api.model
    def _local_to_utc(self, naive_dt):
        import pytz
        tz = pytz.timezone(self.env.user.tz or 'UTC')
        return tz.localize(naive_dt).astimezone(pytz.utc).replace(tzinfo=None)

    # ------------------------------------------------------------------
    # Compute
    # ------------------------------------------------------------------

    @api.depends('checkin_date', 'checkout_date')
    def _compute_nights(self):
        for res in self:
            if res.checkin_date and res.checkout_date:
                res.nights = max(
                    1, (res.checkout_date.date()
                        - res.checkin_date.date()).days)
            else:
                res.nights = 0

    @api.depends('line_ids.price_subtotal', 'line_ids.adults',
                 'line_ids.children')
    def _compute_totals(self):
        for res in self:
            res.room_count = len(res.line_ids)
            res.adults = sum(res.line_ids.mapped('adults'))
            res.children = sum(res.line_ids.mapped('children'))
            res.amount_room_total = sum(res.line_ids.mapped('price_subtotal'))

    @api.depends('agent_id', 'commission_type', 'commission_rate',
                 'amount_room_total')
    def _compute_commission(self):
        for res in self:
            if not res.agent_id:
                res.commission_amount = 0.0
            elif res.commission_type == 'fixed':
                res.commission_amount = res.commission_rate
            else:
                res.commission_amount = (
                    res.amount_room_total * res.commission_rate / 100.0)

    @api.onchange('source')
    def _onchange_source(self):
        if self.source != 'agent':
            self.agent_id = False

    @api.onchange('hotel_id')
    def _onchange_hotel_id(self):
        """Recaler les heures par défaut sur celles de l'hôtel choisi."""
        if self.hotel_id and self.checkin_date and self.checkout_date:
            self.checkin_date = self._compose_datetime(
                self.checkin_date.date(), self.hotel_id.checkin_hour)
            self.checkout_date = self._compose_datetime(
                self.checkout_date.date(), self.hotel_id.checkout_hour)
        # Les chambres appartiennent à l'hôtel : purge en cas de changement.
        self.line_ids = [(5, 0, 0)]

    # ------------------------------------------------------------------
    # Contraintes
    # ------------------------------------------------------------------

    @api.constrains('checkin_date', 'checkout_date')
    def _check_dates(self):
        for res in self:
            if res.checkout_date <= res.checkin_date:
                raise ValidationError(
                    _("La date de départ doit être postérieure à la date "
                      "d'arrivée."))

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _("Nouveau")) == _("Nouveau"):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'aite.hotel.reservation') or _("Nouveau")
        reservations = super().create(vals_list)
        for res in reservations:
            res.partner_id.is_hotel_guest = True
        return reservations

    def write(self, vals):
        res = super().write(vals)
        # Les dates ou lignes bougent sur une réservation vivante :
        # revalider la disponibilité et resynchroniser le folio.
        if {'checkin_date', 'checkout_date', 'line_ids'} & set(vals):
            for reservation in self.filtered(
                    lambda r: r.state in ('confirmed', 'checked_in')):
                reservation._check_lines_availability()
                reservation._sync_folio_room_lines()
        return res

    @api.ondelete(at_uninstall=False)
    def _unlink_guard(self):
        for res in self:
            if res.state not in ('draft', 'cancelled'):
                raise UserError(
                    _("Seules les réservations en brouillon ou annulées "
                      "peuvent être supprimées. Annulez d'abord %s.",
                      res.name))

    # ------------------------------------------------------------------
    # Disponibilité
    # ------------------------------------------------------------------

    def _check_lines_availability(self):
        """Vérifie chaque ligne ; message clair chambre par chambre."""
        for res in self:
            if not res.line_ids:
                raise UserError(
                    _("Ajoutez au moins une chambre à la réservation %s "
                      "avant de la confirmer.", res.name))
            for line in res.line_ids:
                if not line.room_id.is_available(
                        line.checkin_date, line.checkout_date,
                        ignore_line=line):
                    raise UserError(
                        _("La chambre %(room)s n'est pas disponible du "
                          "%(cin)s au %(cout)s (déjà réservée ou hors "
                          "service).",
                          room=line.room_id.display_name,
                          cin=fields.Datetime.to_string(line.checkin_date),
                          cout=fields.Datetime.to_string(line.checkout_date)))

    # ------------------------------------------------------------------
    # Folio
    # ------------------------------------------------------------------

    def _sync_folio_room_lines(self):
        for res in self.filtered('folio_id'):
            res.folio_id._sync_room_lines()

    # ------------------------------------------------------------------
    # Workflow
    # ------------------------------------------------------------------

    def action_confirm(self):
        for res in self:
            if res.state != 'draft':
                raise UserError(
                    _("Seule une réservation en brouillon peut être "
                      "confirmée."))
            res._check_lines_availability()
            res.state = 'confirmed'
            if not res.folio_id:
                res.folio_id = self.env['aite.hotel.folio'].create({
                    'reservation_id': res.id,
                })
            res._sync_folio_room_lines()
            if res.company_id.hotel_send_confirmation and res.partner_email:
                res._send_confirmation_mail()
        return True

    def _send_confirmation_mail(self):
        self.ensure_one()
        template = self.env.ref(
            'aite_hotel_management.mail_template_reservation_confirmation',
            raise_if_not_found=False)
        if template:
            template.send_mail(self.id, force_send=False)

    def action_send_confirmation(self):
        """Ouvre le composeur pré-rempli avec le gabarit de confirmation."""
        self.ensure_one()
        template = self.env.ref(
            'aite_hotel_management.mail_template_reservation_confirmation',
            raise_if_not_found=False)
        ctx = {
            'default_model': self._name,
            'default_res_ids': self.ids,
            'default_template_id': template.id if template else False,
            'default_composition_mode': 'comment',
        }
        return {
            'type': 'ir.actions.act_window',
            'name': _("Envoyer la confirmation"),
            'res_model': 'mail.compose.message',
            'view_mode': 'form',
            'target': 'new',
            'context': ctx,
        }

    def action_checkin(self):
        for res in self:
            if res.state != 'confirmed':
                raise UserError(
                    _("Le check-in n'est possible que sur une réservation "
                      "confirmée."))
            now = fields.Datetime.now()
            if res.checkin_date.date() > now.date() \
                    and not self.env.user.has_group(
                        'aite_hotel_management.group_hotel_manager'):
                raise UserError(
                    _("L'arrivée est prévue le %s : un check-in anticipé "
                      "nécessite le profil Responsable.",
                      res.checkin_date.date()))
            for line in res.line_ids:
                if line.room_id.out_of_order:
                    raise UserError(
                        _("La chambre %s est hors service.",
                          line.room_id.display_name))
            res.write({'state': 'checked_in', 'actual_checkin': now})
            res.line_ids.mapped('room_id').write({'hk_state': 'clean'})
        return True

    def action_open_checkout_wizard(self):
        self.ensure_one()
        if self.state != 'checked_in':
            raise UserError(
                _("Le check-out n'est possible que pour un client arrivé."))
        return {
            'type': 'ir.actions.act_window',
            'name': _("Check-out — %s", self.name),
            'res_model': 'aite.hotel.checkout.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_reservation_id': self.id},
        }

    def action_cancel(self):
        for res in self:
            if res.state in ('checked_out',):
                raise UserError(
                    _("Un séjour terminé ne peut pas être annulé."))
            if res.folio_id and res.folio_id.amount_paid > 0:
                raise UserError(
                    _("Le folio %s a déjà encaissé des règlements. "
                      "Annulez ou remboursez d'abord les paiements du "
                      "folio.", res.folio_id.name))
            res.state = 'cancelled'
            if res.folio_id and res.folio_id.state == 'open':
                res.folio_id.action_cancel()
        return True

    def action_set_no_show(self):
        for res in self:
            if res.state != 'confirmed':
                raise UserError(
                    _("Seule une réservation confirmée peut être marquée "
                      "no-show."))
            res.state = 'no_show'
            res.message_post(body=_(
                "Client non présenté (no-show). Les chambres sont "
                "libérées ; d'éventuels frais de no-show peuvent être "
                "ajoutés au folio %s.", res.folio_id.name or "-"))
        return True

    def action_reset_draft(self):
        for res in self:
            if res.state not in ('cancelled', 'no_show'):
                raise UserError(
                    _("Seule une réservation annulée ou no-show peut "
                      "repasser en brouillon."))
            res.state = 'draft'
            if res.folio_id and res.folio_id.state == 'cancelled':
                res.folio_id.state = 'open'
        return True

    def action_view_folio(self):
        self.ensure_one()
        if not self.folio_id:
            raise UserError(_("Aucun folio : confirmez d'abord la "
                              "réservation."))
        return {
            'type': 'ir.actions.act_window',
            'name': _("Folio"),
            'res_model': 'aite.hotel.folio',
            'view_mode': 'form',
            'res_id': self.folio_id.id,
        }

    def action_register_deposit(self):
        """Raccourci réception : encaisser un acompte sur le folio."""
        self.ensure_one()
        if not self.folio_id:
            raise UserError(_("Confirmez la réservation pour ouvrir le "
                              "folio avant d'encaisser un acompte."))
        return self.folio_id.action_register_payment()

    # ------------------------------------------------------------------
    # Cron
    # ------------------------------------------------------------------

    @api.model
    def _cron_daily_tasks(self):
        """
        Tâches quotidiennes du PMS.

        1. **No-show automatique** (si activé sur la société) : les
           réservations confirmées dont l'arrivée est dépassée du délai de
           grâce passent en no-show, libérant les chambres.
        2. **Ménage quotidien** (si activé) : une tâche de gouvernante
           « ménage quotidien » est créée pour chaque chambre occupée
           n'en ayant pas encore aujourd'hui.
        """
        now = fields.Datetime.now()
        for company in self.env['res.company'].search([]):
            if company.hotel_auto_no_show:
                limit = now - timedelta(
                    hours=company.hotel_no_show_grace or 24)
                stale = self.search([
                    ('company_id', '=', company.id),
                    ('state', '=', 'confirmed'),
                    ('checkin_date', '<', limit),
                ])
                for res in stale:
                    res.action_set_no_show()
            if company.hotel_auto_daily_hk:
                self.env['aite.hotel.housekeeping']._generate_daily_tasks(
                    company)
        return True


class HotelReservationLine(models.Model):
    """
    Ligne de réservation = une chambre sur le séjour.

    Porte la chambre, l'occupation (adultes / enfants) et le prix par nuit
    calculé par le moteur tarifaire (surcharge chambre → saison → base du
    type), modifiable par la réception. Les dates sont celles de la
    réservation (liaison stockée) : c'est cette ligne qu'exploitent le
    planning Gantt et le contrôle de chevauchement.
    """
    _name = 'aite.hotel.reservation.line'
    _description = "Ligne de réservation (chambre)"
    _order = 'checkin_date, room_id'

    reservation_id = fields.Many2one(
        'aite.hotel.reservation', string="Réservation", required=True,
        ondelete='cascade', index=True,
    )
    hotel_id = fields.Many2one(
        related='reservation_id.hotel_id', store=True, readonly=True,
        index=True,
    )
    company_id = fields.Many2one(
        related='reservation_id.company_id', store=True, readonly=True,
    )
    currency_id = fields.Many2one(
        related='reservation_id.currency_id', store=True, readonly=True,
    )
    partner_id = fields.Many2one(
        related='reservation_id.partner_id', string="Client",
        store=True, readonly=True,
    )
    state = fields.Selection(
        related='reservation_id.state', store=True, readonly=True,
        index=True,
    )
    checkin_date = fields.Datetime(
        related='reservation_id.checkin_date', string="Arrivée",
        store=True, readonly=True, index=True,
    )
    checkout_date = fields.Datetime(
        related='reservation_id.checkout_date', string="Départ",
        store=True, readonly=True, index=True,
    )
    nights = fields.Integer(
        related='reservation_id.nights', store=True, readonly=True,
    )

    room_type_id = fields.Many2one(
        'aite.hotel.room.type', string="Type", required=True,
    )
    room_id = fields.Many2one(
        'aite.hotel.room', string="Chambre", required=True, index=True,
        domain="[('hotel_id', '=', hotel_id),"
               " ('room_type_id', '=', room_type_id),"
               " ('out_of_order', '=', False)]",
        ondelete='restrict',
    )
    adults = fields.Integer(string="Adultes", default=1)
    children = fields.Integer(string="Enfants", default=0)
    occupant_names = fields.Char(
        string="Occupants",
        help="Noms des occupants si différents du client (registre de "
             "police, petit-déjeuner…).",
    )
    price_night = fields.Monetary(
        string="Prix / nuit", currency_field='currency_id',
        compute='_compute_price_night', store=True, readonly=False,
        help="Proposé par le moteur tarifaire (moyenne sur le séjour, "
             "suppléments personnes inclus) ; ajustable tant que la "
             "réservation n'est pas terminée.",
    )
    price_subtotal = fields.Monetary(
        string="Sous-total (HT)", compute='_compute_subtotal', store=True,
        currency_field='currency_id',
    )

    # ------------------------------------------------------------------
    # Compute / onchange
    # ------------------------------------------------------------------

    @api.onchange('room_type_id')
    def _onchange_room_type_id(self):
        if self.room_id and self.room_id.room_type_id != self.room_type_id:
            self.room_id = False

    @api.onchange('room_id')
    def _onchange_room_id(self):
        if self.room_id:
            self.room_type_id = self.room_id.room_type_id
            if self.room_id.capacity_adults:
                self.adults = min(
                    max(self.adults, 1), self.room_id.capacity_adults)

    @api.depends('room_id', 'checkin_date', 'checkout_date', 'adults')
    def _compute_price_night(self):
        for line in self:
            if not (line.room_id and line.checkin_date
                    and line.checkout_date
                    and line.checkout_date > line.checkin_date):
                if not line.price_night:
                    line.price_night = 0.0
                continue
            price, _nights = line.room_id._get_stay_price(
                line.checkin_date.date(), line.checkout_date.date())
            rtype = line.room_id.room_type_id
            extra_persons = max(
                0, (line.adults or 0) - (rtype.capacity_adults or 0))
            line.price_night = price + extra_persons * rtype.extra_person_price

    @api.depends('price_night', 'nights')
    def _compute_subtotal(self):
        for line in self:
            line.price_subtotal = line.price_night * line.nights

    @api.depends('room_id.name', 'partner_id.name')
    def _compute_display_name(self):
        for line in self:
            room = line.room_id.name or "?"
            guest = line.partner_id.name or ""
            line.display_name = "%s · %s" % (room, guest) if guest else room

    # ------------------------------------------------------------------
    # Contraintes
    # ------------------------------------------------------------------

    @api.constrains('adults', 'children', 'room_id')
    def _check_capacity(self):
        for line in self:
            if line.adults < 1:
                raise ValidationError(
                    _("Chaque chambre réservée doit compter au moins un "
                      "adulte."))
            room = line.room_id
            if room and line.adults > room.capacity_adults:
                raise ValidationError(
                    _("La chambre %(room)s accueille au maximum %(cap)d "
                      "adulte(s).", room=room.display_name,
                      cap=room.capacity_adults))
            if room and line.children > room.capacity_children:
                raise ValidationError(
                    _("La chambre %(room)s accueille au maximum %(cap)d "
                      "enfant(s).", room=room.display_name,
                      cap=room.capacity_children))

    @api.constrains('room_id', 'checkin_date', 'checkout_date', 'state')
    def _check_no_overlap(self):
        """
        Pas de double réservation : deux lignes actives (confirmée ou en
        séjour) ne peuvent pas se chevaucher sur la même chambre. Borne de
        fin exclusive (départ 12 h / arrivée 14 h le même jour : OK).
        """
        Line = self.env['aite.hotel.reservation.line']
        for line in self:
            if line.state not in ('confirmed', 'checked_in'):
                continue
            clash = Line.search([
                ('id', '!=', line.id),
                ('room_id', '=', line.room_id.id),
                ('state', 'in', ('confirmed', 'checked_in')),
                ('checkin_date', '<', line.checkout_date),
                ('checkout_date', '>', line.checkin_date),
            ], limit=1)
            if clash:
                raise ValidationError(
                    _("Conflit de réservation : la chambre %(room)s est "
                      "déjà prise par %(ref)s sur cette période.",
                      room=line.room_id.display_name,
                      ref=clash.reservation_id.name))

    @api.constrains('room_id', 'reservation_id')
    def _check_room_unique_per_reservation(self):
        for line in self:
            twin = line.reservation_id.line_ids.filtered(
                lambda l: l.room_id == line.room_id and l.id != line.id)
            if twin:
                raise ValidationError(
                    _("La chambre %s figure deux fois sur la réservation.",
                      line.room_id.display_name))

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def action_change_room(self, new_room_id):
        """
        Change la chambre d'un séjour (déclassement / surclassement).

        Utilisé par le bouton du formulaire : vérifie la disponibilité de
        la nouvelle chambre, conserve le prix si demandé côté vue, trace
        le mouvement au chatter de la réservation et resynchronise le
        folio.
        """
        self.ensure_one()
        new_room = self.env['aite.hotel.room'].browse(new_room_id)
        if not new_room.is_available(
                self.checkin_date, self.checkout_date, ignore_line=self):
            raise UserError(
                _("La chambre %s n'est pas disponible sur la période du "
                  "séjour.", new_room.display_name))
        old = self.room_id
        self.write({
            'room_id': new_room.id,
            'room_type_id': new_room.room_type_id.id,
        })
        if self.state == 'checked_in':
            old.hk_state = 'to_clean'
        self.reservation_id.message_post(body=_(
            "Changement de chambre : %(old)s → %(new)s.",
            old=old.display_name, new=new_room.display_name))
        self.reservation_id._sync_folio_room_lines()
        return True
