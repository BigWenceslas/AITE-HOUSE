# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class HousekeepingChecklistItem(models.Model):
    """
    Point de contrôle d'une inspection (lit refait, salle de bain, linge,
    minibar, télécommande…). Paramétrable par le responsable ; livré avec
    une liste standard.
    """
    _name = 'aite.hk.checklist.item'
    _description = "Point de contrôle (inspection de chambre)"
    _order = 'sequence, id'

    name = fields.Char(string="Point de contrôle", required=True, translate=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)


class HousekeepingCheck(models.Model):
    """Une case de la checklist, sur une tâche d'inspection donnée."""
    _name = 'aite.hk.check'
    _description = "Case de checklist"
    _order = 'sequence, id'

    task_id = fields.Many2one(
        'aite.hotel.housekeeping', required=True, ondelete='cascade')
    item_id = fields.Many2one(
        'aite.hk.checklist.item', string="Point", required=True,
        ondelete='restrict')
    sequence = fields.Integer(related='item_id.sequence', store=True)
    ok = fields.Boolean(string="Conforme")
    remark = fields.Char(string="Remarque")


class HotelHousekeeping(models.Model):
    """
    La tâche du socle gagne : l'inspection avec checklist, la durée, et
    des étiquettes lisibles sur le tableau et le téléphone.
    """
    _inherit = 'aite.hotel.housekeeping'

    check_ids = fields.One2many(
        'aite.hk.check', 'task_id', string="Checklist")
    checks_ok = fields.Integer(compute='_compute_checks', string="Conformes")
    checks_total = fields.Integer(compute='_compute_checks', string="Points")
    checks_summary = fields.Char(compute='_compute_checks', string="Contrôle")
    started_at = fields.Datetime(string="Commencée à", readonly=True, copy=False)
    done_at = fields.Datetime(string="Terminée à", readonly=True, copy=False)
    duration_min = fields.Integer(
        string="Durée (min)", compute='_compute_duration', store=True)
    guest_name = fields.Char(
        string="Client", compute='_compute_guest', help="Client présent ou attendu.")
    room_status = fields.Selection(
        related='room_id.status', string="État de la chambre")
    task_label = fields.Char(string="Quoi faire", compute='_compute_label')

    @api.depends('check_ids.ok')
    def _compute_checks(self):
        for task in self:
            task.checks_total = len(task.check_ids)
            task.checks_ok = len(task.check_ids.filtered('ok'))
            task.checks_summary = (
                "%d / %d" % (task.checks_ok, task.checks_total)
                if task.checks_total else "")

    @api.depends('started_at', 'done_at')
    def _compute_duration(self):
        for task in self:
            if task.started_at and task.done_at:
                task.duration_min = int(
                    (task.done_at - task.started_at).total_seconds() // 60)
            else:
                task.duration_min = 0

    def _compute_guest(self):
        for task in self:
            line = task.room_id.current_line_id
            task.guest_name = line.partner_id.name if line else False

    @api.depends('task_type', 'priority')
    def _compute_label(self):
        labels = {
            'checkout_clean': "Recouche complète (départ)",
            'daily_clean': "Ménage quotidien (client présent)",
            'inspection': "Inspection — passer la checklist",
            'maintenance': "Intervention technique",
        }
        for task in self:
            lbl = labels.get(task.task_type, task.task_type or "")
            if task.priority == '1':
                lbl = "URGENT — " + lbl
            task.task_label = lbl

    # ------------------------------------------------------------------
    # Checklist
    # ------------------------------------------------------------------

    @api.model_create_multi
    def create(self, vals_list):
        tasks = super().create(vals_list)
        for task in tasks.filtered(lambda t: t.task_type == 'inspection'):
            task._ensure_checklist()
        return tasks

    def _ensure_checklist(self):
        Check = self.env['aite.hk.check']
        items = self.env['aite.hk.checklist.item'].search([])
        for task in self:
            if task.check_ids or not items:
                continue
            Check.create([{'task_id': task.id, 'item_id': it.id}
                          for it in items])

    def action_start(self):
        res = super().action_start()
        self.filtered(lambda t: not t.started_at).write(
            {'started_at': fields.Datetime.now()})
        return res

    def action_done(self):
        """
        Terminer : pour une inspection, toute case non conforme renvoie
        la chambre en nettoyage avec une tâche urgente qui reprend les
        remarques — l'équipière sait exactement quoi corriger.
        """
        for task in self:
            if task.task_type == 'inspection' and task.check_ids:
                bad = task.check_ids.filtered(lambda c: not c.ok)
                if bad:
                    task.write({'state': 'done',
                                'done_at': fields.Datetime.now()})
                    task.room_id.hk_state = 'to_clean'
                    notes = "; ".join(
                        "%s%s" % (c.item_id.name,
                                  (" — " + c.remark) if c.remark else "")
                        for c in bad)
                    last = self.search([
                        ('room_id', '=', task.room_id.id),
                        ('task_type', 'in', ('checkout_clean', 'daily_clean')),
                        ('assigned_to', '!=', False)],
                        order='id desc', limit=1)
                    self.create({
                        'room_id': task.room_id.id,
                        'task_type': 'checkout_clean', 'priority': '1',
                        'assigned_to': last.assigned_to.id or False,
                        'note': _("Inspection refusée. À reprendre : %s",
                                  notes),
                    })
                    continue
            super(HotelHousekeeping, task).action_done()
            task.done_at = fields.Datetime.now()
        return True

    def action_open_inspection(self):
        """Ouvre la checklist (créée à la volée si absente)."""
        self.ensure_one()
        self._ensure_checklist()
        return {
            'type': 'ir.actions.act_window',
            'name': _("Inspection — chambre %s", self.room_id.name),
            'res_model': 'aite.hotel.housekeeping',
            'view_mode': 'form',
            'res_id': self.id,
            'view_id': self.env.ref(
                'aite_housekeeping.view_housekeeping_inspection_form').id,
            'target': 'new',
        }

    def action_check_all(self):
        """
        « Tout cocher » : coche la checklist et garde la fenêtre
        d'inspection ouverte, pour corriger un point puis valider. Un
        bouton qui renvoie ``True`` ferme la fenêtre (ECARTS n° 52).
        """
        self.mapped('check_ids').write({'ok': True})
        if len(self) == 1:
            return self.action_open_inspection()
        return True
