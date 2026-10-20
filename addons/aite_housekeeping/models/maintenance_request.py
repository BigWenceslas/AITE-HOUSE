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

        ``sudo`` : la chambre est une écriture technique. Le technicien de
        maintenance n'a pas de profil hôtel et doit pouvoir passer sa
        demande à « Réparé » (ECARTS n° 15 a).
        """
        Task = self.env['aite.hotel.housekeeping'].sudo()
        rooms = self.sudo().mapped('room_id')
        for room in rooms:
            requests = room.maintenance_request_ids
            blocking = requests.filtered(
                lambda r: r.blocks_room and not r.stage_id.done
                and not r.archive)
            # Motifs posés par une demande bloquante : seuls ceux-là sont
            # levés par la maintenance. Une mise hors service manuelle
            # (travaux…) garde son propre motif et reste en place.
            request_reasons = set(
                requests.filtered('blocks_room').mapped('name'))
            set_by_request = room.out_of_order_reason in request_reasons
            if blocking and not room.out_of_order:
                if room.occupancy_state == 'occupied':
                    # On ne bloque pas une chambre occupée : on laisse la
                    # demande ouverte, la réception verra la panne.
                    continue
                room.write({
                    'out_of_order': True,
                    'out_of_order_reason': blocking[0].name,
                })
            elif blocking and room.out_of_order and set_by_request \
                    and room.out_of_order_reason not in blocking.mapped(
                        'name'):
                # La demande qui avait donné le motif est réparée, une
                # autre bloque encore : le motif suit la panne restante.
                room.out_of_order_reason = blocking[0].name
            elif not blocking and room.out_of_order and set_by_request:
                # Plus aucune demande ouverte ne bloque : remise en vente,
                # quel que soit l'ordre des réparations (ECARTS n° 15 b).
                room.write({'out_of_order': False,
                            'out_of_order_reason': False})
                room.hk_state = 'to_clean'
                repaired = self.filtered(lambda r: r.room_id == room)[:1]
                Task.create({
                    'room_id': room.id, 'task_type': 'checkout_clean',
                    'note': _("Remise en service après intervention : %s",
                              repaired.sudo().name or room.out_of_order_reason
                              or ""),
                })
