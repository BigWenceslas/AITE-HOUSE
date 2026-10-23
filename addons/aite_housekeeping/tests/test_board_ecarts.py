# -*- coding: utf-8 -*-
"""Tableau des chambres et parcours gouvernante : écarts non bloquants.

Ordre des colonnes, tâche d'inspection créée au bon moment, « Tout cocher »
qui garde la checklist ouverte, écran rechargé après la répartition, liste
des équipières limitée à l'équipe d'étage.
"""
import re

from odoo.tests import tagged

from odoo.addons.aite_hotel_management.tests.common import HotelCommon


class HousekeepingCommon(HotelCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Task = cls.env['aite.hotel.housekeeping']
        cls.Wizard = cls.env['aite.hk.assign.wizard']
        cls.Room = cls.env['aite.hotel.room']
        cls.board = cls.env.ref('aite_housekeeping.view_room_board_kanban')
        cls.maid = cls._hotel_user(
            'equipiere.ecarts', 'aite_hotel_management.group_hotel_housekeeping')
        cls.receptionist = cls._hotel_user(
            'reception.ecarts', 'aite_hotel_management.group_hotel_user')

    @classmethod
    def _hotel_user(cls, login, group_xmlid):
        """Utilisateur interne avec un seul groupe métier, comme à l'écran
        Utilisateurs."""
        return cls.env['res.users'].create({
            'name': login,
            'login': login,
            'groups_id': [(6, 0, [
                cls.env.ref('base.group_user').id,
                cls.env.ref(group_xmlid).id,
            ])],
        })

    def _floor_staff(self):
        """Utilisateurs proposés dans « Équipières présentes »."""
        domain = self.Wizard._fields['user_ids'].get_domain_list(self.Wizard)
        return self.env['res.users'].search(domain)


@tagged('post_install', '-at_install', 'aite_housekeeping')
class TestBoardEcarts(HousekeepingCommon):

    # ------------------------------------------------------------------
    # ECARTS n° 50 : colonnes dans l'ordre du travail
    # ------------------------------------------------------------------

    def test_board_columns_follow_the_work_order(self):
        """Les colonnes se lisent À nettoyer → Nettoyage en cours → À
        inspecter → Propre. On rejoue la requête du client web : il ne
        garde, de l'ordre par défaut de la vue, que le champ regroupé."""
        self.room_101.hk_state = 'to_clean'
        self.room_102.hk_state = 'inspect'
        self.room_201.hk_state = 'clean'
        arch = self.Room.get_views(
            [(self.board.id, 'kanban')])['views']['kanban']['arch']
        match = re.search(r'default_order="([^"]*)"', arch)
        terms = []
        for term in (match.group(1).split(',') if match else []):
            parts = term.split()
            if parts and parts[0] == 'hk_state':
                direction = parts[1].upper() if len(parts) > 1 else 'ASC'
                terms.append('hk_state %s' % direction)
        result = self.Room.web_read_group(
            [('hotel_id', '=', self.hotel.id)], ['hk_state'], ['hk_state'],
            orderby=','.join(terms))
        states = [group['hk_state'] for group in result['groups']]
        self.assertEqual(states, ['to_clean', 'cleaning', 'inspect', 'clean'])

    # ------------------------------------------------------------------
    # ECARTS n° 52 : parcours gouvernante
    # ------------------------------------------------------------------

    def test_floor_staff_list_excludes_other_hotel_profiles(self):
        """« Équipières présentes » ne propose plus la réception ni la
        direction (leur profil implique celui de l'équipe d'étage).

        L'exclusion passe par deux chemins indépendants : le profil
        Réception implique « Gouvernante générale » (exclue de la liste),
        et le domaine écarte aussi explicitement le profil Réception (que
        la Direction et l'administrateur impliquent). Le second chemin est
        vérifié seul, implication retirée, dans
        TestGovernessProfile.test_reception_excluded_without_the_governess_chain.
        """
        staff = self._floor_staff()
        self.assertIn(self.maid, staff)
        self.assertNotIn(self.receptionist, staff)
        self.assertNotIn(self.env.ref('base.user_admin'), staff)

    def test_inspection_task_created_when_cleaning_is_done(self):
        """Inspection exigée : « Terminé » passe la chambre « À inspecter »
        et ouvre la tâche d'inspection avec sa checklist — plus de
        création à la main."""
        self.company.hotel_inspection_required = True
        task = self.Task.create({'room_id': self.room_101.id,
                                 'task_type': 'checkout_clean'})
        task.action_start()
        task.action_done()
        self.assertEqual(self.room_101.hk_state, 'inspect')
        inspection = self.Task.search([
            ('room_id', '=', self.room_101.id),
            ('task_type', '=', 'inspection'),
            ('state', 'in', ('todo', 'in_progress'))])
        self.assertEqual(len(inspection), 1)
        if self.env['aite.hk.checklist.item'].search_count([]):
            self.assertTrue(inspection.check_ids)
        # Une seconde recouche terminée ne crée pas de doublon.
        again = self.Task.create({'room_id': self.room_101.id,
                                  'task_type': 'checkout_clean'})
        again.action_done()
        self.assertEqual(self.Task.search_count([
            ('room_id', '=', self.room_101.id),
            ('task_type', '=', 'inspection'),
            ('state', 'in', ('todo', 'in_progress'))]), 1)
        # Le bouton « Conforme » du tableau clôt cette inspection.
        self.room_101.action_hk_inspect_ok()
        self.assertEqual(inspection.state, 'done')
        self.assertEqual(self.room_101.hk_state, 'clean')

    def test_no_inspection_task_when_not_required(self):
        self.company.hotel_inspection_required = False
        task = self.Task.create({'room_id': self.room_101.id,
                                 'task_type': 'checkout_clean'})
        task.action_done()
        self.assertEqual(self.room_101.hk_state, 'clean')
        self.assertFalse(self.Task.search([
            ('room_id', '=', self.room_101.id),
            ('task_type', '=', 'inspection')]))

    def test_inspections_are_not_given_to_floor_staff(self):
        """« Répartir » distribue le ménage, pas les inspections : elles
        restent à la gouvernante."""
        self.Task.create({'room_id': self.room_101.id,
                          'task_type': 'checkout_clean'})
        inspection = self.Task.create({'room_id': self.room_102.id,
                                       'task_type': 'inspection'})
        wizard = self.Wizard.create({
            'hotel_id': self.hotel.id,
            'user_ids': [(6, 0, self.maid.ids)],
        })
        self.assertEqual(wizard.task_count, 1)
        wizard.action_assign()
        self.assertFalse(inspection.assigned_to)

    def test_check_all_keeps_the_inspection_open(self):
        """« Tout cocher » coche et laisse la fenêtre ouverte sur la
        checklist (avant : la méthode renvoyait True et Odoo fermait la
        fenêtre)."""
        inspection = self.Task.create({'room_id': self.room_101.id,
                                       'task_type': 'inspection'})
        action = inspection.action_check_all()
        self.assertIsInstance(action, dict)
        self.assertEqual(action.get('res_model'), 'aite.hotel.housekeeping')
        self.assertEqual(action.get('res_id'), inspection.id)
        self.assertEqual(action.get('target'), 'new')
        self.assertTrue(all(inspection.check_ids.mapped('ok')))

    # ------------------------------------------------------------------
    # ECARTS n° 53 : l'écran du dessous est rechargé après « Répartir »
    # ------------------------------------------------------------------

    def test_assign_reloads_the_screen_below(self):
        task = self.Task.create({'room_id': self.room_101.id,
                                 'task_type': 'checkout_clean'})
        wizard = self.Wizard.create({
            'hotel_id': self.hotel.id,
            'user_ids': [(6, 0, self.maid.ids)],
        })
        action = wizard.action_assign()
        self.assertEqual(task.assigned_to, self.maid)
        self.assertEqual(action['params'].get('next'),
                         {'type': 'ir.actions.client', 'tag': 'soft_reload'})


@tagged('post_install', '-at_install', 'aite_housekeeping')
class TestGovernessProfile(HousekeepingCommon):
    """ECARTS n° 52 (et n° 1) : la gouvernante répartit et inspecte sans
    le profil Réception."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.governess = cls._hotel_user(
            'gouvernante.ecarts', 'aite_housekeeping.group_hk_governess')

    def test_governess_sees_assign_menu_and_inspection_buttons(self):
        menu = self.env.ref('aite_housekeeping.menu_assign')
        Menu = self.env['ir.ui.menu']
        self.assertIn(menu.id,
                      Menu.with_user(self.governess)._visible_menu_ids())
        self.assertNotIn(menu.id,
                         Menu.with_user(self.maid)._visible_menu_ids())
        arch = self.Room.with_user(self.governess).get_views(
            [(self.board.id, 'kanban')])['views']['kanban']['arch']
        self.assertIn('action_hk_inspect_ok', arch)
        self.assertIn('action_hk_inspect_ko', arch)
        arch_maid = self.Room.with_user(self.maid).get_views(
            [(self.board.id, 'kanban')])['views']['kanban']['arch']
        self.assertNotIn('action_hk_inspect_ok', arch_maid)
        self.assertNotIn('action_hk_inspect_ko', arch_maid)

    def test_governess_assigns_the_rooms(self):
        task = self.Task.create({'room_id': self.room_101.id,
                                 'task_type': 'checkout_clean'})
        self.env.invalidate_all()
        wizard = self.Wizard.with_user(self.governess).create({
            'hotel_id': self.hotel.id,
            'user_ids': [(6, 0, self.maid.ids)],
        })
        wizard.action_assign()
        self.env.invalidate_all()
        self.assertEqual(task.assigned_to, self.maid)

    def test_governess_validates_and_refuses_inspections(self):
        self.room_101.hk_state = 'inspect'
        self.room_102.hk_state = 'inspect'
        self.env.invalidate_all()
        self.room_101.with_user(self.governess).action_hk_inspect_ok()
        self.room_102.with_user(self.governess).action_hk_inspect_ko()
        self.env.invalidate_all()
        self.assertEqual(self.room_101.hk_state, 'clean')
        self.assertEqual(self.room_102.hk_state, 'to_clean')

    def test_governess_is_not_offered_as_floor_staff(self):
        staff = self._floor_staff()
        self.assertIn(self.maid, staff)
        self.assertNotIn(self.governess, staff)

    def test_governess_with_both_profiles_is_never_floor_staff(self):
        """Profils cochés explicitement — « Gouvernante » ET « Gouvernante
        générale », ou « Gouvernante générale » ET « Réception » (une
        gouvernante qui tient aussi la réception) : jamais proposée comme
        équipière."""
        both = self.env['res.users'].create({
            'name': 'gouvernante.double',
            'login': 'gouvernante.double',
            'groups_id': [(6, 0, [
                self.env.ref('base.group_user').id,
                self.env.ref('aite_hotel_management.group_hotel_housekeeping').id,
                self.env.ref('aite_housekeeping.group_hk_governess').id,
            ])],
        })
        governess_at_desk = self.env['res.users'].create({
            'name': 'gouvernante.reception',
            'login': 'gouvernante.reception',
            'groups_id': [(6, 0, [
                self.env.ref('base.group_user').id,
                self.env.ref('aite_housekeeping.group_hk_governess').id,
                self.env.ref('aite_hotel_management.group_hotel_user').id,
            ])],
        })
        staff = self._floor_staff()
        self.assertIn(self.maid, staff)
        self.assertNotIn(both, staff)
        self.assertNotIn(governess_at_desk, staff)

    def test_reception_excluded_without_the_governess_chain(self):
        """La réception reste hors de « Équipières présentes » même si
        l'implication Réception → Gouvernante générale est retirée un jour
        (décision métier encore ouverte : ôter à la réception le droit de
        répartir et d'inspecter)."""
        governess_group = self.env.ref('aite_housekeeping.group_hk_governess')
        self.env.ref('aite_hotel_management.group_hotel_user').write(
            {'implied_ids': [(3, governess_group.id)]})
        receptionist = self._hotel_user(
            'reception.sans.gouvernante',
            'aite_hotel_management.group_hotel_user')
        self.assertFalse(receptionist.has_group(
            'aite_housekeeping.group_hk_governess'))
        self.assertTrue(receptionist.has_group(
            'aite_hotel_management.group_hotel_housekeeping'))
        staff = self._floor_staff()
        self.assertIn(self.maid, staff)
        self.assertNotIn(receptionist, staff)

    def test_reception_keeps_the_governess_rights(self):
        """La réception garde ce qu'elle avait : répartir et inspecter."""
        self.assertTrue(self.receptionist.has_group(
            'aite_housekeeping.group_hk_governess'))
