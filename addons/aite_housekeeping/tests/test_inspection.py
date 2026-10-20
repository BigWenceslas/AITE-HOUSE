# -*- coding: utf-8 -*-
"""Inspection : « Conforme » sur le tableau = tout cocher puis clore."""
from odoo.tests import tagged

from odoo.addons.aite_hotel_management.tests.common import HotelCommon


@tagged('post_install', '-at_install', 'aite_housekeeping')
class TestInspectionOk(HotelCommon):

    def test_conforme_with_unchecked_checklist(self):
        """ECARTS n° 19 : la checklist existe mais n'est pas cochée ; le
        bouton « Conforme » coche tout et clôt l'inspection, sans tâche
        « Inspection refusée »."""
        Task = self.env['aite.hotel.housekeeping']
        if not self.env['aite.hk.checklist.item'].search([]):
            self.env['aite.hk.checklist.item'].create(
                {'name': "Lit refait"})
        self.room_101.hk_state = 'inspect'
        inspection = Task.create({'room_id': self.room_101.id,
                                  'task_type': 'inspection'})
        self.assertTrue(inspection.check_ids)
        self.assertFalse(inspection.check_ids.filtered('ok'))
        self.room_101.action_hk_inspect_ok()
        self.assertEqual(inspection.state, 'done')
        self.assertTrue(all(inspection.check_ids.mapped('ok')))
        self.assertEqual(self.room_101.hk_state, 'clean')
        refused = Task.search([('room_id', '=', self.room_101.id),
                               ('note', 'ilike', 'Inspection refusée')])
        self.assertFalse(refused)
        self.assertFalse(Task.search([
            ('room_id', '=', self.room_101.id),
            ('state', 'in', ('todo', 'in_progress'))]))
