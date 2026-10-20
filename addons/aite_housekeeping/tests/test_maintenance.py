# -*- coding: utf-8 -*-
"""Pannes & réparations : la chambre suit les demandes qui la bloquent."""
from odoo.tests import tagged

from odoo.addons.aite_hotel_management.tests.common import HotelCommon


@tagged('post_install', '-at_install', 'aite_housekeeping')
class TestMaintenanceRoom(HotelCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        base_user = cls.env.ref('base.group_user')
        cls.housekeeper = cls.env['res.users'].create({
            'name': "Équipière pannes",
            'login': 'equipiere.pannes.test',
            'groups_id': [(6, 0, [
                base_user.id,
                cls.env.ref(
                    'aite_hotel_management.group_hotel_housekeeping').id,
            ])],
        })
        # Technicien de maintenance : aucun profil hôtel.
        cls.technician = cls.env['res.users'].create({
            'name': "Technicien",
            'login': 'technicien.test',
            'groups_id': [(6, 0, [
                base_user.id,
                cls.env.ref('maintenance.group_equipment_manager').id,
            ])],
        })
        cls.stage_done = cls.env.ref('maintenance.stage_3')

    def _report(self, issue, priority='1', user=None):
        wizard = self.env['aite.hk.report.issue.wizard'].with_user(
            user or self.housekeeper).create({
                'room_id': self.room_101.id, 'name': issue,
                'blocks_room': True, 'priority': priority,
            })
        wizard.action_submit()
        return self.env['maintenance.request'].search(
            [('room_id', '=', self.room_101.id)], order='id desc', limit=1)

    def test_technician_without_hotel_profile_repairs(self):
        """ECARTS n° 15 (a) : le technicien passe la demande à
        « Réparé » ; la chambre revient en vente."""
        req = self._report("Climatiseur en panne")
        self.assertTrue(self.room_101.out_of_order)
        self.env.invalidate_all()
        req.with_user(self.technician).write(
            {'stage_id': self.stage_done.id})
        self.env.invalidate_all()
        self.assertFalse(self.room_101.out_of_order)
        self.assertEqual(self.room_101.hk_state, 'to_clean')

    def test_two_blocking_requests_both_repaired(self):
        """ECARTS n° 15 (b) : deux demandes bloquantes ; la première
        réparée laisse la chambre hors service, la seconde la libère —
        quel que soit l'ordre."""
        req_a = self._report("Climatiseur en panne")
        req_b = self._report("Fuite lavabo")
        self.assertTrue(self.room_101.out_of_order)
        # Le motif est celui de la première demande ; on répare d'abord
        # celle-ci, puis la seconde.
        req_a.write({'stage_id': self.stage_done.id})
        self.assertTrue(self.room_101.out_of_order,
                        "Une demande bloquante reste ouverte.")
        self.assertEqual(self.room_101.out_of_order_reason, req_b.name)
        req_b.write({'stage_id': self.stage_done.id})
        self.assertFalse(self.room_101.out_of_order)

    def test_two_blocking_requests_repaired_in_reverse_order(self):
        req_a = self._report("Climatiseur en panne")
        req_b = self._report("Fuite lavabo")
        req_b.write({'stage_id': self.stage_done.id})
        self.assertTrue(self.room_101.out_of_order)
        req_a.write({'stage_id': self.stage_done.id})
        self.assertFalse(self.room_101.out_of_order)

    def test_manual_out_of_order_is_kept(self):
        """Une mise hors service manuelle (travaux) n'est pas levée par la
        réparation d'une panne qui n'en est pas la cause."""
        self.room_101.write({'out_of_order': True,
                             'out_of_order_reason': "Travaux de peinture"})
        req = self._report("Ampoule grillée")
        req.write({'stage_id': self.stage_done.id})
        self.assertTrue(self.room_101.out_of_order)
        self.assertEqual(self.room_101.out_of_order_reason,
                         "Travaux de peinture")

    def test_urgency_maps_to_maintenance_priority(self):
        """ECARTS n° 15 (c) : « Important » ne devient plus « Basse »."""
        Wizard = self.env['aite.hk.report.issue.wizard']
        expected = {'0': '2', '1': '3', '2': '3', '3': '3'}
        for urgency, priority in expected.items():
            self.assertEqual(Wizard._maintenance_priority(urgency), priority)
        req = self._report("Fuite lavabo", priority='1')
        self.assertEqual(req.priority, '3')
        self.assertIn("Important", req.description)
