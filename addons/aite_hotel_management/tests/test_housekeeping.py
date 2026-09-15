# -*- coding: utf-8 -*-
"""Gouvernante : tâches de ménage, états de chambre, générateurs."""
from odoo import fields
from odoo.exceptions import UserError
from odoo.tests import tagged

from .common import HotelCommon


@tagged('post_install', '-at_install', 'aite_hotel')
class TestHousekeeping(HotelCommon):

    def _task(self, **kwargs):
        vals = {'room_id': self.room_101.id, 'task_type': 'daily_clean'}
        vals.update(kwargs)
        return self.env['aite.hotel.housekeeping'].create(vals)

    # ------------------------------------------------------------------
    # Cycle de vie d'une tâche
    # ------------------------------------------------------------------

    def test_task_gets_sequence_and_related_fields(self):
        task = self._task()
        self.assertNotEqual(task.name, "Nouveau")
        self.assertEqual(task.hotel_id, self.hotel)
        self.assertEqual(task.floor_id, self.floor)
        self.assertEqual(task.state, 'todo')

    def test_start_sets_room_to_cleaning_and_assigns(self):
        task = self._task()
        task.action_start()
        self.assertEqual(task.state, 'in_progress')
        self.assertEqual(self.room_101.hk_state, 'cleaning')
        self.assertEqual(task.assigned_to, self.env.user)

    def test_start_refused_twice(self):
        task = self._task()
        task.action_start()
        with self.assertRaises(UserError):
            task.action_start()

    def test_done_makes_room_clean(self):
        task = self._task()
        task.action_start()
        task.action_done()
        self.assertEqual(task.state, 'done')
        self.assertEqual(self.room_101.hk_state, 'clean')

    def test_checkout_clean_goes_to_inspect_when_required(self):
        """Avec inspection obligatoire, la recouche passe « à inspecter »."""
        self.company.hotel_inspection_required = True
        task = self._task(task_type='checkout_clean')
        task.action_done()
        self.assertEqual(self.room_101.hk_state, 'inspect')

    def test_checkout_clean_goes_to_clean_without_inspection(self):
        self.company.hotel_inspection_required = False
        task = self._task(task_type='checkout_clean')
        task.action_done()
        self.assertEqual(self.room_101.hk_state, 'clean')

    def test_inspection_task_validates_the_room(self):
        self.room_101.hk_state = 'inspect'
        task = self._task(task_type='inspection')
        task.action_done()
        self.assertEqual(self.room_101.hk_state, 'clean')

    def test_maintenance_task_leaves_hk_state_untouched(self):
        self.room_101.hk_state = 'to_clean'
        task = self._task(task_type='maintenance')
        task.action_done()
        self.assertEqual(self.room_101.hk_state, 'to_clean')

    def test_done_task_cannot_be_cancelled(self):
        task = self._task()
        task.action_done()
        with self.assertRaises(UserError):
            task.action_cancel()

    def test_done_task_cannot_be_redone(self):
        task = self._task()
        task.action_done()
        with self.assertRaises(UserError):
            task.action_done()

    def test_cancelled_task_can_be_reactivated(self):
        task = self._task()
        task.action_cancel()
        self.assertEqual(task.state, 'cancelled')
        task.action_reset_todo()
        self.assertEqual(task.state, 'todo')

    def test_reset_refused_on_open_task(self):
        task = self._task()
        with self.assertRaises(UserError):
            task.action_reset_todo()

    # ------------------------------------------------------------------
    # Générateurs
    # ------------------------------------------------------------------

    def test_checkout_task_generator(self):
        tasks = self.env['aite.hotel.housekeeping']._create_checkout_task(
            self.room_101 | self.room_102)
        self.assertEqual(len(tasks), 2)
        self.assertEqual(set(tasks.mapped('task_type')), {'checkout_clean'})
        self.assertEqual(set(tasks.mapped('priority')), {'1'})
        self.assertEqual(self.room_101.hk_state, 'to_clean')
        self.assertEqual(self.room_102.hk_state, 'to_clean')

    def test_daily_generator_targets_occupied_rooms_only(self):
        reservation = self._make_reservation(checkin_offset=0,
                                             checkout_offset=3)
        reservation.action_confirm()
        reservation.action_checkin()
        Housekeeping = self.env['aite.hotel.housekeeping']
        Housekeeping._generate_daily_tasks(self.company)
        today = fields.Date.context_today(self.env.user)
        # Périmètre limité à l'hôtel de test : la base porte aussi le jeu
        # de démonstration, qui a ses propres chambres occupées.
        tasks = Housekeeping.search([
            ('hotel_id', '=', self.hotel.id),
            ('task_type', '=', 'daily_clean'), ('date', '=', today),
        ])
        self.assertEqual(tasks.mapped('room_id'), self.room_101)

    def test_daily_generator_is_idempotent(self):
        reservation = self._make_reservation(checkin_offset=0,
                                             checkout_offset=3)
        reservation.action_confirm()
        reservation.action_checkin()
        Housekeeping = self.env['aite.hotel.housekeeping']
        Housekeeping._generate_daily_tasks(self.company)
        Housekeeping._generate_daily_tasks(self.company)
        today = fields.Date.context_today(self.env.user)
        self.assertEqual(Housekeeping.search_count([
            ('room_id', '=', self.room_101.id),
            ('task_type', '=', 'daily_clean'),
            ('date', '=', today),
        ]), 1)

    def test_daily_generator_skips_out_of_order_rooms(self):
        reservation = self._make_reservation(checkin_offset=0,
                                             checkout_offset=3)
        reservation.action_confirm()
        reservation.action_checkin()
        self.room_101.out_of_order = True
        Housekeeping = self.env['aite.hotel.housekeeping']
        Housekeeping._generate_daily_tasks(self.company)
        self.assertFalse(Housekeeping.search([
            ('room_id', '=', self.room_101.id),
            ('task_type', '=', 'daily_clean'),
        ]))

    def test_cron_generates_daily_tasks_when_enabled(self):
        self.company.write({'hotel_auto_daily_hk': True,
                            'hotel_auto_no_show': False})
        reservation = self._make_reservation(checkin_offset=0,
                                             checkout_offset=3)
        reservation.action_confirm()
        reservation.action_checkin()
        self.env['aite.hotel.reservation']._cron_daily_tasks()
        self.assertTrue(self.env['aite.hotel.housekeeping'].search([
            ('room_id', '=', self.room_101.id),
            ('task_type', '=', 'daily_clean'),
        ]))

    # ------------------------------------------------------------------
    # Boutons rapides du room board
    # ------------------------------------------------------------------

    def test_quick_state_buttons(self):
        self.room_101.action_set_to_clean()
        self.assertEqual(self.room_101.hk_state, 'to_clean')
        self.room_101.action_start_cleaning()
        self.assertEqual(self.room_101.hk_state, 'cleaning')
        self.room_101.action_set_clean()
        self.assertEqual(self.room_101.hk_state, 'clean')
