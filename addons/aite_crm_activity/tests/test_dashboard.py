# -*- coding: utf-8 -*-
from datetime import timedelta
from unittest.mock import patch

from dateutil.relativedelta import MO, relativedelta

from odoo.exceptions import AccessError, UserError
from odoo.tests import new_test_user, tagged

from odoo.addons.aite_crm_activity.models import crm_activity_dashboard
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

    def test_stalled_includes_lead_whose_last_activity_was_done(self):
        # Cas courant : la dernière activité est marquée comme faite (donc
        # archivée) et rien n'est planifié ensuite.
        Dashboard = self.env['aite.crm.activity.dashboard'].with_user(self.manager)
        for activity in (self.act_bob, self.act_on_bob_for_alice):
            Dashboard.action_mark_done(activity.id)
        data = self.dashboard(self.manager)
        self.assertIn(self.lead_bob.id, [r['id'] for r in data['stalled']['records']])
        self.assertEqual(data['kpis']['stalled'], 2)
        bob_row = next(r for r in data['by_user'] if r['user_id'] == self.bob.id)
        self.assertEqual(bob_row['stalled'], 1)

    def test_activity_list_is_not_emptied_by_access_rules(self):
        # Odoo filtre les activités selon les droits après la requête : une
        # limite SQL appliquée avant viderait la liste d'un commercial dont
        # les collègues ont des activités plus anciennes.
        for __ in range(4):
            self._activity(self.lead_bob, self.bob, -10, self.type_call, "Ancienne relance de Bob")
        with patch.object(crm_activity_dashboard, 'ACTIVITY_LIMIT', 2):
            data = self.dashboard(self.alice, user_id=False)
        activities = data['activities']
        self.assertEqual(activities['total'], 4, "Les 4 activités qu'Alice peut voir")
        self.assertEqual([a['id'] for a in activities['records']],
                         [self.act_overdue.id, self.act_today.id])

    def test_unreadable_partner_does_not_break_the_dashboard(self):
        # Client passé ensuite dans une autre société : Alice peut toujours
        # lire l'opportunité, pas la fiche du client.
        other_company = self.env['res.company'].create({'name': "Autre société AITE"})
        self.partner.company_id = other_company
        data = self.dashboard(self.alice, bucket='overdue')
        self.assertEqual(data['activities']['records'][0]['lead']['partner'], "Client Test")

    def test_unassigned_filter(self):
        orphan = self.env['crm.lead'].create({
            'name': "Opportunité sans commercial", 'type': 'opportunity',
            'user_id': False, 'team_id': self.team.id,
        })
        orphan_activity = self.env['mail.activity'].create({
            'res_model_id': self.env['ir.model']._get_id('crm.lead'),
            'res_id': self.lead_alice.id, 'user_id': False,
            'activity_type_id': self.type_todo.id, 'summary': "À attribuer",
            'date_deadline': self.today,
        })
        data = self.dashboard(self.manager, user_id='unassigned')
        self.assertEqual(data['filters']['user_id'], 'unassigned')
        self.assertEqual([a['id'] for a in data['activities']['records']], [orphan_activity.id])
        self.assertEqual([r['id'] for r in data['stalled']['records']], [orphan.id])
        rows = {r['user_id']: r for r in data['by_user']}
        self.assertEqual(rows['unassigned']['today'], 1)
        self.assertEqual(rows['unassigned']['stalled'], 1)

    def test_by_user_keeps_every_row_when_filtered(self):
        rows = {r['user_id'] for r in self.dashboard(self.manager, user_id=self.bob.id)['by_user']}
        self.assertTrue({self.alice.id, self.bob.id} <= rows,
                        "Le tableau « Par commercial » reste un outil de navigation")

    def test_user_options_cover_salesperson_without_activity(self):
        carol = new_test_user(self.env, login='aite_cad_carol', groups='sales_team.group_sale_salesman',
                              name="Carol Commerciale", tz='UTC')
        self.env['crm.lead'].create({
            'name': "Opportunité Carol", 'type': 'opportunity', 'user_id': carol.id,
            'team_id': self.team.id,
        })
        data = self.dashboard(self.manager, user_id=carol.id)
        self.assertIn(carol.id, [u['id'] for u in data['options']['users']],
                      "Le commercial filtré figure toujours dans la liste")
        self.assertEqual(data['kpis']['stalled'], 1)

    def test_all_documents_profile_gets_the_team_view(self):
        all_docs = new_test_user(self.env, login='aite_cad_all_docs',
                                 groups='sales_team.group_sale_salesman_all_leads',
                                 name="Commercial tous documents", tz='UTC')
        data = self.dashboard(all_docs)
        self.assertTrue(data['is_manager'])
        self.assertFalse(data['filters']['user_id'])
        self.assertTrue(data['options']['assignable_users'])

    def test_non_crm_user_gets_a_clear_error(self):
        clerk = new_test_user(self.env, login='aite_cad_clerk', groups='base.group_user', name="Comptable")
        with self.assertRaises(AccessError):
            self.dashboard(clerk)

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
        self.assertEqual(Dashboard.action_reschedule(self.act_overdue.id, new_date.isoformat()),
                         new_date.isoformat())
        self.assertEqual(self.act_overdue.date_deadline, new_date)
        with self.assertRaises(UserError):
            Dashboard.action_reschedule(self.act_overdue.id, False)
        with self.assertRaises(UserError):
            Dashboard.action_reschedule(self.act_overdue.id, "n'importe quoi")

    def test_reschedule_presets_use_the_server_date(self):
        Dashboard = self.env['aite.crm.activity.dashboard'].with_user(self.alice).with_context(tz='UTC')
        expected = {
            'tomorrow': self.today + timedelta(days=1),
            'monday': self.today + relativedelta(weeks=1, weekday=MO(-1)),
            'week': self.today + timedelta(days=7),
        }
        for preset, date in expected.items():
            Dashboard.action_reschedule(self.act_today.id, preset)
            self.assertEqual(self.act_today.date_deadline, date, preset)
        self.assertEqual(expected['monday'].weekday(), 0)
        self.assertTrue(1 <= (expected['monday'] - self.today).days <= 7)

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
