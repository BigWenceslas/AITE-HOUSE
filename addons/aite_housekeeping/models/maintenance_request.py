# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class MaintenanceRequest(models.Model):
    """
    Une demande de maintenance peut concerner une chambre. Si elle rend la
    chambre invendable, celle-ci passe hors service — et revient en vente
    toute seule quand la demande est terminée. Personne n'a à y penser.
    """
    _inherit = 'maintenance.request'

    room_id = fields.Many2one(
        'aite.hotel.room', string="Chambre", index=True, ondelete='set null',
        help="Chambre concernée par l'intervention.",
    )
    hotel_id = fields.Many2one(
        related='room_id.hotel_id', store=True, readonly=True)
    blocks_room = fields.Boolean(
        string="Chambre invendable pendant l'intervention",
        help="Coché : la chambre est mise hors service jusqu'à la fin de "
             "l'intervention, puis remise en vente automatiquement.",
    )
    reported_by_hk = fields.Boolean(
        string="Signalée par l'équipe d'étage", readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        requests = super().create(vals_list)
        requests._sync_room_out_of_order()
        return requests

    def write(self, vals):
        res = super().write(vals)
        if {'stage_id', 'blocks_room', 'room_id', 'archive'} & set(vals):
            self._sync_room_out_of_order()
        return res

    def _sync_room_out_of_order(self):
        """
        Règle unique : une chambre est hors service tant qu'au moins une
        demande ouverte la bloque. Sinon, elle est (re)mise en vente.
        """
        rooms = self.mapped('room_id')
        for room in rooms:
            blocking = room.maintenance_request_ids.filtered(
                lambda r: r.blocks_room and not r.stage_id.done
                and not r.archive)
            should_block = bool(blocking)
            if should_block and not room.out_of_order:
                if room.occupancy_state == 'occupied':
                    # On ne bloque pas une chambre occupée : on laisse la
                    # demande ouverte, la réception verra la panne.
                    continue
                room.write({
                    'out_of_order': True,
                    'out_of_order_reason': blocking[0].name,
                })
            elif not should_block and room.out_of_order \
                    and room.out_of_order_reason \
                    and room.out_of_order_reason in self.mapped('name'):
                room.write({'out_of_order': False,
                            'out_of_order_reason': False})
                room.hk_state = 'to_clean'
                self.env['aite.hotel.housekeeping'].create({
                    'room_id': room.id, 'task_type': 'checkout_clean',
                    'note': _("Remise en service après intervention : %s",
                              self.filtered(lambda r: r.room_id == room)[:1].name),
                })
