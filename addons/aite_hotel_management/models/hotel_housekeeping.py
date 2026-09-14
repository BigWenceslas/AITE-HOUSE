# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HotelHousekeeping(models.Model):
    """
    Tâche de gouvernante (ménage, recouche, inspection, maintenance).

    Pilotée en kanban par état (à faire → en cours → terminé). La tâche
    entraîne l'état ménage de la chambre : démarrer passe la chambre en
    « nettoyage en cours », terminer la rend « propre » (ou « à
    inspecter » selon le type). Créée à la main, automatiquement au
    check-out, ou par le cron de ménage quotidien.
    """
    _name = 'aite.hotel.housekeeping'
    _description = "Tâche de gouvernante"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, priority desc, id desc'

    name = fields.Char(
        string="Référence", required=True, copy=False, readonly=True,
        index=True, default=lambda self: _("Nouveau"),
    )
    room_id = fields.Many2one(
        'aite.hotel.room', string="Chambre", required=True, index=True,
        ondelete='restrict',
    )
    hotel_id = fields.Many2one(
        related='room_id.hotel_id', store=True, readonly=True, index=True,
    )
    floor_id = fields.Many2one(
        related='room_id.floor_id', store=True, readonly=True,
    )
    company_id = fields.Many2one(
        related='room_id.company_id', store=True, readonly=True, index=True,
    )
    task_type = fields.Selection(
        selection=[
            ('checkout_clean', "Recouche (départ)"),
            ('daily_clean', "Ménage quotidien"),
            ('inspection', "Inspection"),
            ('maintenance', "Maintenance"),
        ],
        string="Type", required=True, default='daily_clean', index=True,
    )
    date = fields.Date(
        string="Date", required=True, index=True,
        default=fields.Date.context_today,
    )
    assigned_to = fields.Many2one(
        'res.users', string="Assignée à",
        domain=lambda self: [('groups_id', 'in', self.env.ref(
            'aite_hotel_management.group_hotel_housekeeping').ids)],
        tracking=True,
    )
    priority = fields.Selection(
        selection=[('0', "Normale"), ('1', "Urgente")],
        string="Priorité", default='0',
    )
    state = fields.Selection(
        selection=[
            ('todo', "À faire"),
            ('in_progress', "En cours"),
            ('done', "Terminé"),
            ('cancelled', "Annulé"),
        ],
        string="État", default='todo', required=True, index=True,
        copy=False, tracking=True,
    )
    note = fields.Text(string="Consignes / constat")

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _("Nouveau")) == _("Nouveau"):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'aite.hotel.housekeeping') or _("Nouveau")
        return super().create(vals_list)

    # ------------------------------------------------------------------
    # Workflow
    # ------------------------------------------------------------------

    def action_start(self):
        for task in self:
            if task.state != 'todo':
                raise UserError(
                    _("Seule une tâche à faire peut être démarrée."))
            task.state = 'in_progress'
            if task.task_type in ('checkout_clean', 'daily_clean'):
                task.room_id.hk_state = 'cleaning'
            if not task.assigned_to:
                task.assigned_to = self.env.user
        return True

    def action_done(self):
        for task in self:
            if task.state not in ('todo', 'in_progress'):
                raise UserError(
                    _("Cette tâche est déjà clôturée."))
            task.state = 'done'
            room = task.room_id
            if task.task_type == 'checkout_clean' \
                    and task.company_id.hotel_inspection_required:
                room.hk_state = 'inspect'
            elif task.task_type == 'inspection':
                room.hk_state = 'clean'
            elif task.task_type in ('checkout_clean', 'daily_clean'):
                room.hk_state = 'clean'
        return True

    def action_cancel(self):
        for task in self:
            if task.state == 'done':
                raise UserError(
                    _("Une tâche terminée ne peut pas être annulée."))
            task.state = 'cancelled'
        return True

    def action_reset_todo(self):
        for task in self:
            if task.state != 'cancelled':
                raise UserError(
                    _("Seule une tâche annulée peut être réactivée."))
            task.state = 'todo'
        return True

    # ------------------------------------------------------------------
    # Générateurs
    # ------------------------------------------------------------------

    @api.model
    def _create_checkout_task(self, rooms):
        """Recouche au départ : une tâche par chambre libérée."""
        tasks = self.browse()
        for room in rooms:
            room.hk_state = 'to_clean'
            tasks |= self.create({
                'room_id': room.id,
                'task_type': 'checkout_clean',
                'priority': '1',
            })
        return tasks

    @api.model
    def _generate_daily_tasks(self, company):
        """Ménage quotidien des chambres occupées (appelé par le cron)."""
        today = fields.Date.context_today(self)
        rooms = self.env['aite.hotel.room'].search([
            ('company_id', '=', company.id),
            ('out_of_order', '=', False),
        ]).filtered(lambda r: r.occupancy_state == 'occupied')
        for room in rooms:
            exists = self.search_count([
                ('room_id', '=', room.id),
                ('task_type', '=', 'daily_clean'),
                ('date', '=', today),
                ('state', '!=', 'cancelled'),
            ])
            if not exists:
                self.create({
                    'room_id': room.id,
                    'task_type': 'daily_clean',
                    'date': today,
                })
        return True
