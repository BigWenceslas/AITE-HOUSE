# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class HotelReservation(models.Model):
    """
    Le check-in ouvre le registre : la fiche du client principal est créée
    et pré-remplie ; la réception complète les autres occupants depuis le
    bouton « Fiches clients » de la réservation. Rien de bloquant — mais
    l'écran dit clairement ce qui manque.
    """
    _inherit = 'aite.hotel.reservation'

    registration_ids = fields.One2many(
        'aite.guest.registration', 'reservation_id',
        string="Fiches d'enregistrement",
    )
    # Compteurs et phrase d'écran : non stockés, recalculés à chaque
    # lecture. L'état (ci-dessous) est stocké pour filtrer les listes ;
    # Odoo exige deux méthodes de calcul distinctes dans ce cas.
    registration_count = fields.Integer(
        string="Fiches", compute='_compute_registration_figures',
    )
    registration_done_count = fields.Integer(
        string="Fiches complètes", compute='_compute_registration_figures',
    )
    expected_guests = fields.Integer(
        string="Occupants attendus", compute='_compute_registration_figures',
        help="Adultes + enfants de toutes les chambres.",
    )
    registration_status = fields.Selection(
        selection=[
            ('none', "Aucune fiche"),
            ('partial', "À compléter"),
            ('done', "Registre à jour"),
        ],
        string="Registre", compute='_compute_registration_status',
        store=True, index=True,
        help="État du registre des clients pour ce séjour.",
    )
    registration_hint = fields.Char(
        string="Registre — à faire", compute='_compute_registration_figures',
    )

    def _registration_figures(self):
        """(nb fiches, nb fiches complètes, occupants attendus, état)."""
        self.ensure_one()
        regs = self.registration_ids
        done = regs.filtered(lambda r: r.state == 'done')
        expected = sum(self.line_ids.mapped('adults')) + sum(
            self.line_ids.mapped('children'))
        if not regs:
            status = 'none'
        elif len(done) >= max(1, expected) and len(done) == len(regs):
            status = 'done'
        else:
            status = 'partial'
        return len(regs), len(done), expected, status

    @api.depends('registration_ids.state', 'line_ids.adults',
                 'line_ids.children', 'state')
    def _compute_registration_status(self):
        for res in self:
            res.registration_status = res._registration_figures()[3]

    @api.depends('registration_ids.state', 'line_ids.adults',
                 'line_ids.children', 'state')
    def _compute_registration_figures(self):
        for res in self:
            count, done, expected, status = res._registration_figures()
            res.registration_count = count
            res.registration_done_count = done
            res.expected_guests = expected
            res.registration_hint = res._hint_text(
                status, count, done, expected)

    def _hint_text(self, status, count, done, expected):
        """Phrase d'écran qui dit quoi faire."""
        if status == 'done':
            return _("Registre à jour : %d fiche(s) complète(s).", done)
        if status == 'none':
            return _("Aucune fiche d'enregistrement : %d occupant(s) "
                     "attendu(s).", expected)
        missing_people = max(0, expected - count)
        parts = []
        if count - done:
            parts.append(_("%d fiche(s) à compléter", count - done))
        if missing_people:
            parts.append(_("%d occupant(s) sans fiche", missing_people))
        return " · ".join(parts) or _("Registre à compléter.")

    # ------------------------------------------------------------------
    # Workflow
    # ------------------------------------------------------------------

    def action_checkin(self):
        res = super().action_checkin()
        for reservation in self:
            reservation._ensure_main_registration()
        return res

    def _ensure_main_registration(self):
        """Crée la fiche du client principal si elle n'existe pas."""
        self.ensure_one()
        Reg = self.env['aite.guest.registration']
        if self.registration_ids.filtered('is_main_guest'):
            return
        line = self.line_ids[:1]
        Reg.create(Reg._vals_from_partner(
            self.partner_id, self, line=line, main=True))

    def action_open_registrations(self):
        """
        Fenêtre unique du registre pour ce séjour : les fiches existantes
        en liste éditable, pré-filtrées, avec création rapide.
        """
        self.ensure_one()
        if self.state in ('confirmed', 'checked_in') \
                and not self.registration_ids:
            self._ensure_main_registration()
        line = self.line_ids[:1]
        return {
            'type': 'ir.actions.act_window',
            'name': _("Fiches clients — %s", self.name),
            'res_model': 'aite.guest.registration',
            'view_mode': 'list,form',
            'views': [
                (self.env.ref(
                    'aite_guest_registry.view_guest_registration_list_inline').id,
                 'list'),
                (self.env.ref(
                    'aite_guest_registry.view_guest_registration_form').id,
                 'form'),
            ],
            'domain': [('reservation_id', '=', self.id)],
            'context': {
                'default_reservation_id': self.id,
                'default_reservation_line_id': line.id if line else False,
                'default_arrival_date': self.checkin_date.date()
                if self.checkin_date else False,
                'default_departure_date': self.checkout_date.date()
                if self.checkout_date else False,
                'default_country_id': self.hotel_id.country_id.id,
                'default_nationality_id': self.hotel_id.country_id.id,
                'search_default_reservation_id': self.id,
            },
            'target': 'current',
        }

    def action_print_registration_cards(self):
        self.ensure_one()
        regs = self.registration_ids
        if not regs:
            self._ensure_main_registration()
            regs = self.registration_ids
        return self.env.ref(
            'aite_guest_registry.report_registration_card').report_action(regs)
