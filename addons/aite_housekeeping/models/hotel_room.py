# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class HotelRoom(models.Model):
    """
    La chambre gagne ce dont la gouvernante a besoin sur son tableau :
    la tâche du jour, l'équipière affectée, l'arrivée attendue, le nombre
    de pannes ouvertes — et des libellés qui parlent.
    """
    _inherit = 'aite.hotel.room'

    # Les colonnes du tableau suivent l'ordre du travail (à nettoyer → en
    # cours → à inspecter → propre) : c'est l'ordre de la sélection
    # ``hk_state`` du socle (18.0.1.0.3), plus besoin de la redéfinir ici.
    today_task_id = fields.Many2one(
        'aite.hotel.housekeeping', string="Tâche du jour",
        compute='_compute_today', help="Tâche de ménage ouverte du jour.",
    )
    assigned_to = fields.Many2one(
        'res.users', string="Affectée à", compute='_compute_today',
        help="Équipière chargée de la chambre aujourd'hui.",
    )
    arrival_hint = fields.Char(
        string="Arrivée", compute='_compute_today',
        help="Heure d'arrivée attendue si un client est prévu.",
    )
    guest_name = fields.Char(string="Client", compute='_compute_today')
    maintenance_open_count = fields.Integer(
        string="Pannes ouvertes", compute='_compute_maintenance',
    )
    maintenance_request_ids = fields.One2many(
        'maintenance.request', 'room_id', string="Demandes de maintenance",
    )
    housekeeping_task_ids = fields.One2many(
        'aite.hotel.housekeeping', 'room_id', string="Tâches de ménage",
    )
    hk_hint = fields.Char(
        string="À faire", compute='_compute_today',
        help="Phrase d'écran pour l'équipe d'étage.",
    )

    @api.depends('hk_state', 'out_of_order', 'housekeeping_task_ids.state',
                 'housekeeping_task_ids.assigned_to',
                 'housekeeping_task_ids.date')
    def _compute_today(self):
        today = fields.Date.context_today(self)
        Task = self.env['aite.hotel.housekeeping']
        for room in self:
            task = Task.search([
                ('room_id', '=', room.id), ('date', '=', today),
                ('state', 'in', ('todo', 'in_progress')),
            ], order='priority desc, id', limit=1) if room.ids else Task
            room.today_task_id = task
            room.assigned_to = task.assigned_to
            line = room.current_line_id
            room.guest_name = line.partner_id.name if line else False
            if room.occupancy_state == 'arrival' and line:
                room.arrival_hint = _("Arrivée prévue %s",
                                      fields.Datetime.context_timestamp(
                                          room, line.checkin_date).strftime("%Hh%M"))
            else:
                room.arrival_hint = False
            room.hk_hint = room._hint_for(
                room.hk_state, room.occupancy_state, room.out_of_order,
                bool(task))

    @staticmethod
    def _hint_for(hk_state, occupancy, out_of_order, has_task):
        """Phrase courte, lisible par une équipière — pure, testable."""
        if out_of_order:
            return "Hors service — ne pas vendre"
        if hk_state == 'to_clean':
            return ("Recouche à faire" if occupancy == 'arrival'
                    else "À nettoyer")
        if hk_state == 'cleaning':
            return "Nettoyage en cours"
        if hk_state == 'inspect':
            return "À inspecter par la gouvernante"
        if occupancy == 'occupied':
            return "Propre — client présent"
        if occupancy == 'arrival':
            return "Propre — prête pour l'arrivée"
        return "Propre — libre"

    @api.depends('maintenance_request_ids.stage_id',
                 'maintenance_request_ids.archive',
                 'maintenance_request_ids.stage_id.done')
    def _compute_maintenance(self):
        for room in self:
            room.maintenance_open_count = len(
                room.maintenance_request_ids.filtered(
                    lambda r: not r.stage_id.done and not r.archive))

    # ------------------------------------------------------------------
    # Actions tableau (un bouton = une étape)
    # ------------------------------------------------------------------

    def action_hk_start(self):
        """Démarrer : la tâche du jour passe en cours (créée si besoin)."""
        Task = self.env['aite.hotel.housekeeping']
        for room in self:
            task = room.today_task_id
            if not task:
                task = Task.create({
                    'room_id': room.id,
                    'task_type': ('checkout_clean'
                                  if room.occupancy_state != 'occupied'
                                  else 'daily_clean'),
                    'assigned_to': self.env.user.id,
                })
            if task.state == 'todo':
                task.action_start()
        return True

    def action_hk_done(self):
        """Terminer : la tâche du jour est close, la chambre suit."""
        for room in self:
            task = room.today_task_id
            if task and task.state in ('todo', 'in_progress'):
                task.action_done()
            else:
                room.action_set_clean()
        return True

    def action_hk_inspect_ok(self):
        """
        Inspection validée : chambre propre. « Conforme » vaut « tout est
        conforme » : on coche la checklist avant de clore, sinon une liste
        non cochée était lue comme refusée (ECARTS n° 19).
        """
        for room in self:
            task = self.env['aite.hotel.housekeeping'].search([
                ('room_id', '=', room.id), ('task_type', '=', 'inspection'),
                ('state', 'in', ('todo', 'in_progress'))], limit=1)
            if task:
                task.action_check_all()
                task.action_done()
            room.hk_state = 'clean'
        return True

    def action_hk_inspect_ko(self):
        """Inspection refusée : retour en nettoyage, tâche urgente."""
        Task = self.env['aite.hotel.housekeeping']
        for room in self:
            room.hk_state = 'to_clean'
            Task.create({
                'room_id': room.id, 'task_type': 'checkout_clean',
                'priority': '1',
                'note': _("Inspection refusée — à reprendre."),
            })
        return True

    def action_report_issue(self):
        """Signaler une panne depuis la chambre (assistant léger)."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _("Signaler un problème — chambre %s", self.name),
            'res_model': 'aite.hk.report.issue.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_room_id': self.id},
        }

    def action_view_maintenance(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _("Maintenance — chambre %s", self.name),
            'res_model': 'maintenance.request',
            'view_mode': 'kanban,list,form',
            'domain': [('room_id', '=', self.id)],
            'context': {'default_room_id': self.id,
                        'default_name': _("Chambre %s — ", self.name)},
        }

    def action_set_to_clean(self):
        res = super().action_set_to_clean()
        # Une chambre à nettoyer sans tâche du jour : on en ouvre une.
        Task = self.env['aite.hotel.housekeeping']
        for room in self:
            if not room.today_task_id:
                Task.create({
                    'room_id': room.id,
                    'task_type': ('daily_clean'
                                  if room.occupancy_state == 'occupied'
                                  else 'checkout_clean'),
                })
        return res
