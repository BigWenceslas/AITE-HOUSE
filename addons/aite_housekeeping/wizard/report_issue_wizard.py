# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ReportIssueWizard(models.TransientModel):
    """Signaler une panne depuis la chambre : trois champs, un bouton."""
    _name = 'aite.hk.report.issue.wizard'
    _description = "Signaler un problème dans une chambre"

    room_id = fields.Many2one('aite.hotel.room', string="Chambre", required=True)
    name = fields.Char(
        string="Quel est le problème ?", required=True,
        help="Ex. : climatiseur en panne, fuite lavabo, ampoule grillée.")
    description = fields.Text(string="Précisions")
    blocks_room = fields.Boolean(
        string="La chambre ne peut pas être vendue en l'état",
        help="Elle sera mise hors service jusqu'à la réparation, puis "
             "remise en vente automatiquement.")
    priority = fields.Selection(
        selection=[('0', "Normal"), ('1', "Important"), ('2', "Urgent"),
                   ('3', "Très urgent")],
        string="Urgence", default='1')
    image = fields.Image(string="Photo", max_width=1280, max_height=1280)

    def action_submit(self):
        self.ensure_one()
        Request = self.env['maintenance.request']
        vals = {
            'name': _("Chambre %(room)s — %(issue)s",
                      room=self.room_id.name, issue=self.name),
            'description': self.description or False,
            'maintenance_type': 'corrective',
            'priority': self.priority,
            'room_id': self.room_id.id,
            'blocks_room': self.blocks_room,
            'reported_by_hk': True,
        }
        req = Request.create(vals)
        if self.image:
            self.env['ir.attachment'].create({
                'name': _("Photo — %s", req.name), 'datas': self.image,
                'res_model': 'maintenance.request', 'res_id': req.id,
                'mimetype': 'image/png',
            })
        return {
            'type': 'ir.actions.client', 'tag': 'display_notification',
            'params': {
                'type': 'success', 'sticky': False,
                'title': _("Problème signalé"),
                'message': _("La demande « %s » est transmise à la "
                             "maintenance.", req.name)
                + (_(" La chambre est hors service jusqu'à la réparation.")
                   if self.blocks_room and self.room_id.out_of_order else ""),
                'next': {'type': 'ir.actions.act_window_close'},
            },
        }
