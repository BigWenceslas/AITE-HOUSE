# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AssignWizard(models.TransientModel):
    """
    Répartir les chambres du jour : la gouvernante coche ses équipières,
    les tâches ouvertes non affectées sont distribuées à tour de rôle,
    étage par étage pour limiter les déplacements.
    """
    _name = 'aite.hk.assign.wizard'
    _description = "Répartir les chambres du jour"

    hotel_id = fields.Many2one(
        'aite.hotel.hotel', string="Hôtel", required=True,
        default=lambda self: self.env['aite.hotel.hotel'].search(
            [('company_id', '=', self.env.company.id)], limit=1))
    date = fields.Date(string="Jour", required=True,
                       default=fields.Date.context_today)
    # L'équipe d'étage seulement : profil Gouvernante, sans « Gouvernante
    # générale » ni « Réception » (ECARTS n° 52). La Réception est écartée
    # explicitement, sans dépendre de son implication de « Gouvernante
    # générale » ; le Responsable et l'administrateur impliquent la
    # Réception et sont écartés avec elle.
    user_ids = fields.Many2many(
        'res.users', string="Équipières présentes",
        domain=lambda self: [
            ('groups_id', 'in', self.env.ref(
                'aite_hotel_management.group_hotel_housekeeping').ids),
            ('groups_id', 'not in', (
                self.env.ref('aite_housekeeping.group_hk_governess')
                | self.env.ref('aite_hotel_management.group_hotel_user')).ids),
        ])
    reassign = fields.Boolean(
        string="Redistribuer aussi les chambres déjà affectées")
    task_count = fields.Integer(string="Chambres à répartir",
                                compute='_compute_task_count')

    def _tasks(self):
        # Le ménage seulement : les inspections restent à la gouvernante
        # (elles s'ouvrent seules quand une chambre passe « À inspecter »).
        domain = [('hotel_id', '=', self.hotel_id.id), ('date', '=', self.date),
                  ('state', 'in', ('todo', 'in_progress')),
                  ('task_type', '!=', 'inspection')]
        if not self.reassign:
            domain.append(('assigned_to', '=', False))
        return self.env['aite.hotel.housekeeping'].search(
            domain, order='floor_id, room_id')

    @api.depends('hotel_id', 'date', 'reassign')
    def _compute_task_count(self):
        for wiz in self:
            wiz.task_count = len(wiz._tasks()) if wiz.hotel_id else 0

    @staticmethod
    def _distribute(task_ids, user_ids):
        """Tour de rôle sur une liste ordonnée — pure, testable."""
        if not user_ids:
            return {}
        return {t: user_ids[i % len(user_ids)] for i, t in enumerate(task_ids)}

    def action_assign(self):
        self.ensure_one()
        if not self.user_ids:
            raise UserError(_("Cochez au moins une équipière présente."))
        tasks = self._tasks()
        if not tasks:
            raise UserError(_("Aucune chambre à répartir pour ce jour."))
        plan = self._distribute(tasks.ids, self.user_ids.ids)
        for task in tasks:
            task.assigned_to = plan[task.id]
        return {
            'type': 'ir.actions.client', 'tag': 'display_notification',
            'params': {
                'type': 'success', 'sticky': False,
                'title': _("Chambres réparties"),
                'message': _("%(n)d chambre(s) réparties entre %(u)d "
                             "équipière(s).", n=len(tasks), u=len(self.user_ids)),
                # Ferme la fenêtre et recharge l'écran du dessous (tableau
                # des chambres) : les équipières y apparaissent aussitôt
                # (ECARTS n° 53).
                'next': {'type': 'ir.actions.client', 'tag': 'soft_reload'},
            },
        }
