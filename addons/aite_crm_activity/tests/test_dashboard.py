# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo.exceptions import AccessError, UserError
from odoo.tests import tagged

from .common import AiteCrmActivityCase


@tagged('post_install', '-at_install', 'aite_crm_activity')
class TestCrmActivityDashboard(AiteCrmActivityCase):

    # Indicateurs -------------------------------------------------------

    def test_manager_sees_the_whole_team(self):
        data = self.dashboard(self.manager)
        self.assertTrue(data['is_manager'])
        self.assertFalse(data['filters']['user_id'], "Un responsable voit toute l'équipe par défaut")
        self.assertEqual(data['kpis']['overdue'], 1)
        self.assertEqual(data['kpis']['today'], 1)
        # J+1 (aide à Bob) et J+3 (Bob) ; J+30 hors fenêtre
        self.assertEqual(data['kpis']['upcoming'], 2)
        self.assertEqual(data['kpis']['open'], 5)
        self.assertEqual(data['kpis']['done'], 0)
        self.assertEqual(data['kpis']['stalled'], 1, "Seule l'opportunité ouverte sans activité compte")

    def test_salesman_defaults_to_own_activities(self):
        data = self.dashboard(self.alice, team_id=False)
        self.assertFalse(data['is_manager'])
        self.assertEqual(data['filters']['user_id'], self.alice.id)
        self.assertEqual(data['kpis']['open'], 4)  # 3 sur son opportunité + 1 sur celle de Bob
        self.assertEqual(data['kpis']['stalled'], 1)

    def test_salesman_cannot_see_colleague_activities(self):
        data = self.dashboard(self.alice, user_id=False)
        ids = {a['id'] for a in data['activities']['records']}
        self.assertNotIn(self.act_bob.id, ids, "L'activité de Bob sur son opportunité reste privée")
        self.assertIn(self.act_on_bob_for_alice.id, ids, "Une activité assignée reste visible")

    def test_activity_on_unreadable_lead_shows_without_details(self):
        data = self.dashboard(self.alice, team_id=False)
        row = next(a for a in data['activities']['records'] if a['id'] == self.act_on_bob_for_alice.id)
        self.assertFalse(row['lead'], "Pas de détails d'une opportunité qu'Alice ne peut pas lire")
        self.assertEqual(row['res_name'], "Opportunité Bob")

    def test_by_user_rows(self):
        rows = {r['user_id']: r for r in self.dashboard(self.manager)['by_user']}
        self.assertEqual(
            {k: rows[self.alice.id][k] for k in ('overdue', 'today', 'upcoming', 'done', 'stalled')},
            {'overdue': 1, 'today': 1, 'upcoming': 1, 'done': 0, 'stalled': 1})
        self.assertEqual(rows[self.bob.id]['upcoming'], 1)

    def test_filters_user_and_type(self):
        data = self.dashboard(self.manager, user_id=self.bob.id)
        self.assertEqual([a['id'] for a in data['activities']['records']], [self.act_bob.id])
        data = self.dashboard(self.manager, activity_type_id=self.type_call.id)
        self.assertEqual({a['id'] for a in data['activities']['records']},
                         {self.act_overdue.id, self.act_bob.id})

    def test_buckets(self):
        def ids(bucket):
            return [a['id'] for a in self.dashboard(self.manager, bucket=bucket)['activities']['records']]
        self.assertEqual(ids('overdue'), [self.act_overdue.id])
        self.assertEqual(ids('today'), [self.act_today.id])
        self.assertEqual(ids('upcoming'), [self.act_on_bob_for_alice.id, self.act_bob.id])
        self.assertEqual(ids('all')[0], self.act_overdue.id, "Trié par échéance, retards en tête")

    def test_activity_rows_carry_lead_details(self):
        rows = self.dashboard(self.manager, bucket='overdue')['activities']['records']
        self.assertEqual(rows[0]['state'], 'overdue')
        self.assertEqual(rows[0]['days'], -2)
        self.assertEqual(rows[0]['lead']['name'], "Opportunité Alice")
        self.assertEqual(rows[0]['lead']['partner'], "Client Test")
        self.assertEqual(rows[0]['lead']['expected_revenue'], 1500000)

    def test_stalled_list(self):
        stalled = self.dashboard(self.manager)['stalled']
        self.assertEqual([r['id'] for r in stalled['records']], [self.lead_quiet.id])

    def test_bad_filters_are_ignored(self):
        data = self.dashboard(self.manager, user_id='abc', bucket='nimporte')
        self.assertFalse(data['filters']['user_id'])
        self.assertEqual(data['filters']['bucket'], 'all')

    # Actions -----------------------------------------------------------

    def test_mark_done_with_feedback(self):
        Dashboard = self.env['aite.crm.activity.dashboard'].with_user(self.alice)
        Dashboard.action_mark_done(self.act_overdue.id, "Client rappelé, devis vendredi")
        self.assertFalse(self.act_overdue.active)
        message = self.lead_alice.message_ids.filtered('mail_activity_type_id')[:1]
        self.assertIn("Client rappelé, devis vendredi", message.body)
        data = self.dashboard(self.manager, bucket='done')
        self.assertEqual(data['kpis']['done'], 1)
        self.assertEqual([a['id'] for a in data['activities']['records']], [self.act_overdue.id])
        self.assertEqual(data['activities']['records'][0]['state'], 'done')

    def test_mark_done_twice_is_refused(self):
        Dashboard = self.env['aite.crm.activity.dashboard'].with_user(self.alice)
        Dashboard.action_mark_done(self.act_today.id)
        with self.assertRaises(UserError):
            Dashboard.action_mark_done(self.act_today.id)

    def test_reschedule(self):
        Dashboard = self.env['aite.crm.activity.dashboard'].with_user(self.alice)
        new_date = self.today + timedelta(days=7)
        Dashboard.action_reschedule(self.act_overdue.id, new_date.isoformat())
        self.assertEqual(self.act_overdue.date_deadline, new_date)
        with self.assertRaises(UserError):
            Dashboard.action_reschedule(self.act_overdue.id, False)

    def test_reassign_by_manager(self):
        Dashboard = self.env['aite.crm.activity.dashboard'].with_user(self.manager)
        Dashboard.action_reassign(self.act_bob.id, self.alice.id)
        self.assertEqual(self.act_bob.user_id, self.alice)
        portal = self.env['res.users'].create({
            'name': "Portail", 'login': 'aite_cad_portal',
            'group_ids': [(6, 0, [self.env.ref('base.group_portal').id])],
        })
        with self.assertRaises(UserError):
            Dashboard.action_reassign(self.act_bob.id, portal.id)

    def test_salesman_cannot_touch_colleague_activity(self):
        Dashboard = self.env['aite.crm.activity.dashboard'].with_user(self.alice)
        with self.assertRaises(AccessError):
            Dashboard.action_reschedule(self.act_bob.id, (self.today + timedelta(days=1)).isoformat())

    def test_unknown_activity(self):
        with self.assertRaises(UserError):
            self.env['aite.crm.activity.dashboard'].action_mark_done(0)
