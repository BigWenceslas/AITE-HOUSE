# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PoliceRegisterWizard(models.TransientModel):
    """
    Impression du registre chronologique sur une période.

    Deux champs, un bouton : c'est tout ce qu'un contrôle demande. Par
    défaut, les sept derniers jours.
    """
    _name = 'aite.police.register.wizard'
    _description = "Registre de police — période à imprimer"

    hotel_id = fields.Many2one(
        'aite.hotel.hotel', string="Hôtel", required=True,
        default=lambda self: self.env['aite.hotel.hotel'].search(
            [('company_id', '=', self.env.company.id)], limit=1),
    )
    date_from = fields.Date(
        string="Du", required=True,
        default=lambda self: fields.Date.context_today(self) - timedelta(days=7),
    )
    date_to = fields.Date(
        string="Au", required=True,
        default=fields.Date.context_today,
    )
    include_draft = fields.Boolean(
        string="Inclure les fiches incomplètes", default=True,
        help="Décochez pour n'imprimer que les fiches complètes.",
    )
    count = fields.Integer(string="Fiches trouvées", compute='_compute_count')

    @api.depends('hotel_id', 'date_from', 'date_to', 'include_draft')
    def _compute_count(self):
        for wiz in self:
            wiz.count = len(wiz._get_registrations()) if wiz.hotel_id else 0

    def _get_registrations(self):
        self.ensure_one()
        domain = [
            ('hotel_id', '=', self.hotel_id.id),
            ('arrival_date', '>=', self.date_from),
            ('arrival_date', '<=', self.date_to),
            ('reservation_id.state', 'in', ('checked_in', 'checked_out')),
        ]
        if not self.include_draft:
            domain.append(('state', '=', 'done'))
        return self.env['aite.guest.registration'].search(
            domain, order='arrival_date, room_id, last_name')

    def action_print(self):
        self.ensure_one()
        if self.date_to < self.date_from:
            raise UserError(_("La date de fin doit suivre la date de début."))
        regs = self._get_registrations()
        if not regs:
            raise UserError(_(
                "Aucune fiche d'enregistrement entre le %(a)s et le %(b)s "
                "pour %(h)s.", a=self.date_from, b=self.date_to,
                h=self.hotel_id.name))
        return self.env.ref(
            'aite_guest_registry.report_police_register').with_context(
                date_from=self.date_from, date_to=self.date_to,
                hotel_name=self.hotel_id.name).report_action(regs)
