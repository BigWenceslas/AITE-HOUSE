# -*- coding: utf-8 -*-
""" Tableau de bord « Suivi des activités ».

Règles vérifiées ici :

- droits : chacun ne voit que ce qu'Odoo l'autorise à voir ; seul un
  responsable (droits « tous les documents ») peut réassigner, y compris par
  un appel direct au serveur ;
- opportunités perdues (archivées) : leurs activités ouvertes ne sont plus
  « à faire » (indicateurs, listes, tableau par commercial, plan de charge,
  montants), leurs activités réalisées restent comptées ;
- période des « Réalisées » : préréglages, période personnalisée (dates
  illisibles, inversées, trop longues, futures), période précédente et
  évolution en % (None quand la base est nulle), toujours calculées sur la
  date du jour de l'utilisateur côté serveur (fuseau de Douala compris) ;
- cohérence entre blocs : sans filtre de commercial, les lignes « Par
  commercial » et le plan de charge somment aux indicateurs, et le total de
  chaque liste est égal à l'indicateur correspondant ;
- propagation des filtres (équipe, type, commercial, « Non assigné »), avec
  les exceptions voulues : « Par commercial » et le plan de charge ignorent
  le filtre de commercial, les opportunités sans activité ignorent le type ;
- gravité des retards, montants en jeu (chaque opportunité une fois, seules
  celles que l'utilisateur peut lire), dernière action et opportunités
  dormantes, tendances hebdomadaires, aperçu d'une opportunité, réglages.
"""
import json
from datetime import date, datetime, timedelta
from unittest.mock import patch

from dateutil.relativedelta import MO, relativedelta

from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tests import freeze_time, new_test_user, tagged

from odoo.addons.aite_crm_activity.models import crm_activity_dashboard
from odoo.addons.aite_crm_activity.models.crm_activity_dashboard import (
    WEEKDAYS_SHORT, bucket_counts_by_week, bucket_done_by_week, delta_pct, iso_weeks, percentage,
    previous_period, resolve_period, week_index,
)
from odoo.addons.aite_crm_activity.models.crm_activity_params import (
    PARAM_CRITICAL_DAYS, PARAM_DASHBOARD_UPCOMING_DAYS, PARAM_DORMANT_DAYS, PARAM_HIGH_DAYS,
    get_thresholds,
)
from .common import THRESHOLD_PARAMS, AiteCrmActivityCase


class DashboardCase(AiteCrmActivityCase):
    """ Outils communs aux tests du tableau de bord (le jeu d'essai de
    ``common.py`` n'est pas modifié). """

    def setUp(self):
        super().setUp()
        self.Dashboard = self.env['aite.crm.activity.dashboard']
        self.currency = self.lead_alice.company_currency

    def _done(self, activity, date_done, feedback=False):
        """ Activité réalisée à une date donnée (date_done est écrite avec
        l'archivage, sinon Odoo y mettrait la date du jour). """
        activity.write({'active': False, 'date_done': date_done, 'feedback': feedback})
        return activity

    def _done_activity(self, lead, user, deadline, date_done, activity_type=None, summary="Réalisée"):
        activity = self._activity(lead, user, 0, activity_type or self.type_todo, summary)
        activity.date_deadline = deadline
        return self._done(activity, date_done)

    def _set_create_date(self, activities, when):
        self.env.flush_all()
        self.env.cr.execute("UPDATE mail_activity SET create_date = %s WHERE id IN %s",
                            (when, tuple(activities.ids)))
        activities.invalidate_recordset(['create_date'])

    def _set_stage_update(self, lead, when):
        self.env.flush_all()
        self.env.cr.execute("UPDATE crm_lead SET date_last_stage_update = %s WHERE id = %s",
                            (when, lead.id))
        lead.invalidate_recordset(['date_last_stage_update'])

    def _param(self, key, value):
        self.env['ir.config_parameter'].sudo().set_param(key, str(value))

    def _days(self, days):
        return self.today + timedelta(days=days)

    @staticmethod
    def _rows(data):
        return {row['user_id']: row for row in data['by_user']['rows']}

    @staticmethod
    def _ids(records):
        return [record['id'] for record in records]


@tagged('post_install', '-at_install', 'aite_crm_activity')
class TestCrmActivityDashboard(DashboardCase):

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
        rows = self._rows(self.dashboard(self.manager))
        self.assertEqual(
            {k: rows[self.alice.id][k] for k in ('overdue', 'today', 'upcoming', 'done', 'stalled')},
            {'overdue': 1, 'today': 1, 'upcoming': 1, 'done': 0, 'stalled': 1})
        self.assertEqual(rows[self.bob.id]['upcoming'], 1)

    def test_by_user_rates_and_team_total(self):
        by_user = self.dashboard(self.manager)['by_user']
        self.assertEqual([row['user_id'] for row in by_user['rows']], [self.alice.id, self.bob.id])
        self.assertEqual(by_user['rows'][0], {
            'user_id': self.alice.id, 'name': "Alice Commerciale",
            'overdue': 1, 'today': 1, 'upcoming': 1, 'done': 0, 'stalled': 1,
            'high': 0, 'critical': 0, 'open': 3, 'overdue_rate': 33,
        })
        self.assertEqual(by_user['rows'][1], {
            'user_id': self.bob.id, 'name': "Bob Commercial",
            'overdue': 0, 'today': 0, 'upcoming': 1, 'done': 0, 'stalled': 0,
            'high': 0, 'critical': 0, 'open': 1, 'overdue_rate': 0,
        })
        self.assertEqual(by_user['total'], {
            'overdue': 1, 'today': 1, 'upcoming': 2, 'done': 0, 'stalled': 1,
            'high': 0, 'critical': 0, 'open': 4, 'overdue_rate': 25,
        })

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
        self.assertEqual(rows[0]['days_late'], 2)
        self.assertEqual(rows[0]['severity'], 'low')
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
        bob_row = next(r for r in data['by_user']['rows'] if r['user_id'] == self.bob.id)
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
        rows = self._rows(data)
        self.assertEqual(rows['unassigned']['today'], 1)
        self.assertEqual(rows['unassigned']['stalled'], 1)
        self.assertEqual(rows['unassigned']['name'], "Non assigné")

    def test_by_user_keeps_every_row_when_filtered(self):
        rows = set(self._rows(self.dashboard(self.manager, user_id=self.bob.id)))
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
        for method, args in (('get_dashboard_data', ({},)), ('get_trend_data', ({},)),
                             ('get_lead_preview', (self.lead_alice.id,))):
            with self.subTest(method=method), self.assertRaises(AccessError):
                getattr(self.Dashboard.with_user(clerk), method)(*args)

    def test_bad_filters_are_ignored(self):
        data = self.dashboard(self.manager, user_id='abc', bucket='nimporte', period='year',
                              activity_type_id=[1], date_from={'a': 1})
        self.assertFalse(data['filters']['user_id'])
        self.assertEqual(data['filters']['bucket'], 'all')
        self.assertEqual(data['filters']['period'], '7d')
        self.assertFalse(data['filters']['activity_type_id'])

    def test_payload_shape(self):
        """ Contrat des clés attendues par le navigateur. """
        self._activity(self.lead_alice, self.alice, -8, self.type_call, "Retard critique")
        self.lead_quiet.expected_revenue = 1000
        data = self.dashboard(self.manager)
        json.dumps(data)  # tout passe tel quel par JSON-RPC (dates en texte)
        self.assertEqual(set(data), {
            'filters', 'is_manager', 'today', 'upcoming_days', 'done_days', 'period', 'thresholds',
            'kpis', 'alerts', 'filter_notes', 'by_user', 'activities', 'stalled', 'workload', 'options',
        })
        self.assertEqual(set(data['filters']), {
            'user_id', 'team_id', 'activity_type_id', 'bucket', 'period', 'date_from', 'date_to'})
        self.assertEqual(data['today'], self.today.isoformat())
        self.assertEqual(data['upcoming_days'], 7)
        self.assertEqual(data['done_days'], 7)
        self.assertEqual(data['period'], {
            'key': '7d', 'label': "7 derniers jours",
            'date_from': self._days(-6).isoformat(), 'date_to': self.today.isoformat(),
            'prev_from': self._days(-13).isoformat(), 'prev_to': self._days(-7).isoformat(),
            'days': 7,
        })
        self.assertEqual(data['thresholds'], {
            'upcoming_days': 7, 'high_days': 3, 'critical_days': 7, 'dormant_days': 14})
        self.assertEqual(set(data['kpis']), {
            'overdue', 'today', 'upcoming', 'open', 'stalled',
            'done', 'done_prev', 'done_delta', 'created', 'created_prev', 'created_delta',
            'on_time_rate', 'on_time_rate_prev', 'high', 'critical',
            'overdue_leads', 'overdue_amounts', 'stalled_amounts',
        })
        self.assertEqual(data['alerts'], [{
            'level': 'danger', 'message': "1 activité en retard de 7 jours ou plus",
            'action': {'bucket': 'overdue'},
        }])
        self.assertEqual(data['filter_notes'], {'stalled_ignores_type': False})
        self.assertEqual(set(data['by_user']), {'rows', 'total'})
        self.assertEqual(set(data['by_user']['rows'][0]), {
            'user_id', 'name', 'overdue', 'today', 'upcoming', 'done', 'stalled', 'high', 'critical',
            'open', 'overdue_rate'})
        self.assertEqual(set(data['by_user']['total']), {
            'overdue', 'today', 'upcoming', 'done', 'stalled', 'high', 'critical', 'open', 'overdue_rate'})
        self.assertEqual(set(data['activities']['records'][0]), {
            'id', 'type', 'icon', 'summary', 'date_deadline', 'date_done', 'days', 'days_late',
            'severity', 'state', 'user_id', 'user', 'res_id', 'res_name', 'lead', 'can_write'})
        self.assertEqual(set(data['stalled']), {'records', 'total', 'limit', 'amounts', 'dormant'})
        self.assertEqual(set(data['stalled']['records'][0]), {
            'id', 'name', 'partner', 'stage', 'team', 'user', 'expected_revenue', 'currency_id',
            'probability', 'type', 'last_action_date', 'idle_days', 'dormant'})
        self.assertEqual(set(data['workload']), {'days', 'rows', 'max'})
        self.assertEqual(set(data['workload']['days'][0]), {'date', 'label', 'weekday', 'is_today', 'is_weekend'})
        self.assertEqual(set(data['workload']['rows'][0]), {'user_id', 'name', 'overdue', 'cells', 'total'})
        self.assertEqual(data['options']['periods'], [
            {'key': '7d', 'label': "7 derniers jours"},
            {'key': 'month', 'label': "Ce mois"},
            {'key': 'last_month', 'label': "Mois dernier"},
            {'key': 'quarter', 'label': "Ce trimestre"},
            {'key': 'custom', 'label': "Personnalisée"},
        ])

    def test_read_methods_can_use_a_read_only_cursor(self):
        Model = type(self.Dashboard)
        for method in ('get_dashboard_data', 'get_trend_data', 'get_lead_preview'):
            with self.subTest(method=method):
                self.assertTrue(getattr(getattr(Model, method), '_readonly', False))
        self.assertFalse(getattr(Model.action_reassign, '_readonly', False))

    def test_filter_note_when_type_filter_is_active(self):
        data = self.dashboard(self.manager, activity_type_id=self.type_call.id)
        self.assertEqual(data['filter_notes'], {'stalled_ignores_type': True})
        self.assertEqual(data['kpis']['stalled'], 1, "Le type ne s'applique pas aux opportunités sans activité")

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
        row = data['activities']['records'][0]
        self.assertEqual(row['state'], 'done')
        self.assertEqual(row['days_late'], 2, "Faite avec deux jours de retard")
        self.assertFalse(row['severity'], "Plus de gravité pour une activité réalisée")

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
        for preset, day in expected.items():
            with self.subTest(preset=preset):
                Dashboard.action_reschedule(self.act_today.id, preset)
                self.assertEqual(self.act_today.date_deadline, day)
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

    def test_salesman_cannot_reassign_via_rpc(self):
        # L'écran masque le bouton, mais Odoo accepterait l'écriture : Alice
        # a le droit d'écrire sur ses propres activités. Le serveur refuse.
        Dashboard = self.env['aite.crm.activity.dashboard'].with_user(self.alice)
        for activity in (self.act_overdue, self.act_on_bob_for_alice):
            with self.subTest(activity=activity.summary):
                with self.assertRaises(AccessError) as error:
                    Dashboard.action_reassign(activity.id, self.bob.id)
                self.assertIn("réassigner", str(error.exception))
                self.assertEqual(activity.user_id, self.alice)
        all_docs = new_test_user(self.env, login='aite_cad_all_docs_reassign',
                                 groups='sales_team.group_sale_salesman_all_leads',
                                 name="Commercial tous documents", tz='UTC')
        self.Dashboard.with_user(all_docs).action_reassign(self.act_overdue.id, self.bob.id)
        self.assertEqual(self.act_overdue.user_id, self.bob)

    def test_salesman_cannot_touch_colleague_activity(self):
        Dashboard = self.env['aite.crm.activity.dashboard'].with_user(self.alice)
        with self.assertRaises(AccessError):
            Dashboard.action_reschedule(self.act_bob.id, (self.today + timedelta(days=1)).isoformat())

    def test_unknown_activity(self):
        with self.assertRaises(UserError):
            self.env['aite.crm.activity.dashboard'].action_mark_done(0)

    def test_overdue_deep_link_action(self):
        action = self.env.ref('aite_crm_activity.action_crm_activity_dashboard_overdue')
        self.assertEqual(action.tag, 'aite_crm_activity_dashboard')
        self.assertEqual(action.tag, self.env.ref('aite_crm_activity.action_crm_activity_dashboard').tag)
        self.assertEqual(action.path, 'activites-en-retard')
        self.assertEqual(action.params, {'bucket': 'overdue'})
        self.assertFalse(self.env['ir.ui.menu'].search([('action', '=', 'ir.actions.client,%d' % action.id)]),
                         "Lien direct sans menu")
        data = self.dashboard(self.manager, **action.params)
        self.assertEqual(data['filters']['bucket'], 'overdue')
        self.assertEqual(self._ids(data['activities']['records']), [self.act_overdue.id])


@tagged('post_install', '-at_install', 'aite_crm_activity')
class TestDashboardLostLeads(DashboardCase):
    """ Opportunité perdue : Odoo l'archive sans fermer ses activités. """

    def test_lost_lead_open_activities_leave_the_dashboard(self):
        self.Dashboard.with_user(self.alice).action_mark_done(self.act_overdue.id, "Fait avant la perte")
        before = self.dashboard(self.manager)
        self.assertEqual((before['kpis']['today'], before['kpis']['open'], before['kpis']['done']), (1, 4, 1))

        self.lead_alice.action_set_lost()
        self.assertFalse(self.lead_alice.active)
        self.assertTrue(self.act_today.active, "Odoo laisse les activités ouvertes")

        data = self.dashboard(self.manager)
        kpis = data['kpis']
        self.assertEqual(
            {key: kpis[key] for key in ('overdue', 'today', 'upcoming', 'open', 'high', 'critical',
                                        'overdue_leads', 'overdue_amounts', 'done')},
            {'overdue': 0, 'today': 0, 'upcoming': 2, 'open': 2, 'high': 0, 'critical': 0,
             'overdue_leads': 0, 'overdue_amounts': [], 'done': 1})
        self.assertEqual(set(self._ids(data['activities']['records'])),
                         {self.act_on_bob_for_alice.id, self.act_bob.id})
        rows = self._rows(data)
        self.assertEqual({k: rows[self.alice.id][k] for k in ('overdue', 'today', 'upcoming', 'done')},
                         {'overdue': 0, 'today': 0, 'upcoming': 1, 'done': 1})
        workload = {row['user_id']: row for row in data['workload']['rows']}
        self.assertEqual(workload[self.alice.id]['overdue'], 0)
        self.assertEqual(workload[self.alice.id]['cells'][:2], [0, 1])
        self.assertEqual(workload[self.alice.id]['total'], 1)
        self.assertNotIn(self.lead_alice.id, self._ids(data['stalled']['records']))

        done = self.dashboard(self.manager, bucket='done')['activities']
        self.assertEqual(self._ids(done['records']), [self.act_overdue.id],
                         "Une activité faite avant la perte reste dans « Réalisées »")
        for bucket in ('all', 'today', 'upcoming'):
            with self.subTest(bucket=bucket):
                ids = self._ids(self.dashboard(self.manager, bucket=bucket)['activities']['records'])
                self.assertNotIn(self.act_today.id, ids)
                self.assertNotIn(self.act_far.id, ids)

    def test_lost_lead_for_the_salesman(self):
        self.lead_alice.action_set_lost()
        data = self.dashboard(self.alice, team_id=False)
        self.assertEqual(
            {key: data['kpis'][key] for key in ('overdue', 'today', 'upcoming', 'open')},
            {'overdue': 0, 'today': 0, 'upcoming': 1, 'open': 1})
        self.assertEqual(self._ids(data['activities']['records']), [self.act_on_bob_for_alice.id])

    def test_restored_lead_counts_again(self):
        self.lead_alice.action_set_lost()
        self.lead_alice.action_unarchive()
        self.assertEqual(self.dashboard(self.manager)['kpis']['overdue'], 1)


@tagged('post_install', '-at_install', 'aite_crm_activity')
class TestDashboardPeriod(DashboardCase):
    """ Période des « Réalisées », période précédente et évolution. """

    TODAY = date(2026, 11, 13)

    def test_presets(self):
        TODAY = self.TODAY
        cases = {
            ('7d', TODAY): (date(2026, 11, 7), TODAY),
            ('month', TODAY): (date(2026, 11, 1), TODAY),
            ('last_month', TODAY): (date(2026, 10, 1), date(2026, 10, 31)),
            ('quarter', TODAY): (date(2026, 10, 1), TODAY),
            ('last_month', date(2026, 1, 15)): (date(2025, 12, 1), date(2025, 12, 31)),
            ('last_month', date(2024, 3, 31)): (date(2024, 2, 1), date(2024, 2, 29)),
            ('quarter', date(2026, 1, 15)): (date(2026, 1, 1), date(2026, 1, 15)),
            ('quarter', date(2026, 6, 30)): (date(2026, 4, 1), date(2026, 6, 30)),
            ('quarter', date(2026, 9, 1)): (date(2026, 7, 1), date(2026, 9, 1)),
            ('month', date(2026, 3, 1)): (date(2026, 3, 1), date(2026, 3, 1)),
        }
        for (key, today), (start, end) in cases.items():
            with self.subTest(key=key, today=today):
                self.assertEqual(resolve_period(key, False, False, today), (key, start, end))

    def test_unknown_period_falls_back_to_seven_days(self):
        for key in (None, '', 'year', 'week', 42, ['7d']):
            with self.subTest(key=key):
                self.assertEqual(resolve_period(key, '2026-10-01', '2026-10-31', self.TODAY),
                                 ('7d', date(2026, 11, 7), self.TODAY))

    def test_custom_period(self):
        today = self.TODAY
        cases = [
            # (date_from, date_to) → résultat
            (('2026-10-01', '2026-10-31'), ('custom', date(2026, 10, 1), date(2026, 10, 31))),
            ((date(2026, 10, 1), date(2026, 10, 31)), ('custom', date(2026, 10, 1), date(2026, 10, 31))),
            (('2026-10-31', '2026-10-01'), ('custom', date(2026, 10, 1), date(2026, 10, 31))),  # inversées
            (('2026-11-13', '2026-11-13'), ('custom', today, today)),
            (('2026-11-01', '2027-01-01'), ('custom', date(2026, 11, 1), today)),  # fin future
            (('2027-01-01', '2027-02-01'), ('custom', today, today)),  # entièrement future
            (('2024-01-01', '2026-10-31'), ('custom', date(2025, 10, 31), date(2026, 10, 31))),  # > 366 j
            (('2025-11-13', '2026-11-13'), ('custom', date(2025, 11, 13), today)),  # 366 j : gardé
            (('2025-11-12', '2026-11-13'), ('custom', date(2025, 11, 13), today)),  # 367 j : réduit
            (('abc', '2026-10-31'), ('7d', date(2026, 11, 7), today)),
            (('2026-10-01', False), ('7d', date(2026, 11, 7), today)),
            ((None, None), ('7d', date(2026, 11, 7), today)),
            (('2026-02-30', '2026-03-01'), ('7d', date(2026, 11, 7), today)),
            (({'a': 1}, 12), ('7d', date(2026, 11, 7), today)),
            (('0001-01-01', '0001-01-05'), ('7d', date(2026, 11, 7), today)),
        ]
        for (date_from, date_to), expected in cases:
            with self.subTest(date_from=date_from, date_to=date_to):
                result = resolve_period('custom', date_from, date_to, today)
                self.assertEqual(result, expected)
                self.assertLessEqual((result[2] - result[1]).days + 1, 366)

    def test_previous_period_and_delta(self):
        self.assertEqual(previous_period(date(2026, 11, 7), date(2026, 11, 13)),
                         (date(2026, 10, 31), date(2026, 11, 6)))
        self.assertEqual(previous_period(date(2026, 10, 1), date(2026, 10, 31)),
                         (date(2026, 8, 31), date(2026, 9, 30)))
        self.assertEqual(previous_period(date(2026, 3, 1), date(2026, 3, 1)),
                         (date(2026, 2, 28), date(2026, 2, 28)))
        self.assertEqual(delta_pct(12, 10), 20.0)
        self.assertEqual(delta_pct(5, 10), -50.0)
        self.assertEqual(delta_pct(1, 3), -66.7)
        self.assertEqual(delta_pct(10, 10), 0.0)
        self.assertIsNone(delta_pct(3, 0), "Pas de base de comparaison")
        self.assertIsNone(delta_pct(0, 0))
        self.assertEqual(delta_pct(5, -10), 150.0, "Le signe suit le sens de l'évolution")
        self.assertEqual(percentage(1, 3), 33.3)
        self.assertEqual(percentage(3, 3), 100.0)
        self.assertEqual(percentage(0, 4), 0.0)
        self.assertIsNone(percentage(0, 0))

    def _done_fixture(self):
        """ Réalisées : 2 sur les 7 derniers jours (dont 1 à temps), 3 sur
        la période précédente (dont 2 à temps), 1 avant. """
        return {
            'd0': self._done_activity(self.lead_alice, self.alice, self._days(0), self._days(0)),
            'd6': self._done_activity(self.lead_bob, self.bob, self._days(-8), self._days(-6)),
            'd7': self._done_activity(self.lead_alice, self.alice, self._days(-7), self._days(-7)),
            'd10': self._done_activity(self.lead_alice, self.alice, self._days(-11), self._days(-10)),
            'd13': self._done_activity(self.lead_alice, self.bob, self._days(-10), self._days(-13)),
            'd14': self._done_activity(self.lead_alice, self.alice, self._days(-20), self._days(-14)),
        }

    def test_default_period_drives_done(self):
        done = self._done_fixture()
        data = self.dashboard(self.manager)
        kpis = data['kpis']
        self.assertEqual(
            {key: kpis[key] for key in ('done', 'done_prev', 'done_delta', 'on_time_rate', 'on_time_rate_prev')},
            {'done': 2, 'done_prev': 3, 'done_delta': -33.3, 'on_time_rate': 50.0, 'on_time_rate_prev': 66.7})
        rows = self._rows(data)
        self.assertEqual((rows[self.alice.id]['done'], rows[self.bob.id]['done']), (1, 1))
        listed = self.dashboard(self.manager, bucket='done')['activities']
        self.assertEqual(self._ids(listed['records']), [done['d0'].id, done['d6'].id])
        self.assertEqual(listed['records'][1]['days_late'], 2)
        # Les instantanés ne dépendent pas de la période.
        self.assertEqual({key: kpis[key] for key in ('overdue', 'today', 'upcoming', 'open', 'stalled')},
                         {'overdue': 1, 'today': 1, 'upcoming': 2, 'open': 5, 'stalled': 1})

    def test_custom_period_drives_done(self):
        done = self._done_fixture()
        data = self.dashboard(self.manager, period='custom', date_from=self._days(-7).isoformat(),
                              date_to=self._days(-14).isoformat())  # bornes inversées
        self.assertEqual(data['filters']['period'], 'custom')
        self.assertEqual((data['filters']['date_from'], data['filters']['date_to']),
                         (self._days(-14).isoformat(), self._days(-7).isoformat()))
        self.assertEqual(data['period'], {
            'key': 'custom',
            'label': "Du %s au %s" % (self._days(-14).strftime('%d/%m/%Y'), self._days(-7).strftime('%d/%m/%Y')),
            'date_from': self._days(-14).isoformat(), 'date_to': self._days(-7).isoformat(),
            'prev_from': self._days(-22).isoformat(), 'prev_to': self._days(-15).isoformat(),
            'days': 8,
        })
        self.assertEqual(data['done_days'], 8)
        kpis = data['kpis']
        self.assertEqual(
            {key: kpis[key] for key in ('done', 'done_prev', 'done_delta', 'on_time_rate', 'on_time_rate_prev')},
            {'done': 4, 'done_prev': 0, 'done_delta': None, 'on_time_rate': 50.0, 'on_time_rate_prev': None})
        rows = self._rows(data)
        self.assertEqual((rows[self.alice.id]['done'], rows[self.bob.id]['done']), (3, 1))
        listed = self.dashboard(self.manager, bucket='done', period='custom',
                                date_from=self._days(-14).isoformat(), date_to=self._days(-7).isoformat())
        self.assertEqual(self._ids(listed['activities']['records']),
                         [done['d7'].id, done['d10'].id, done['d13'].id, done['d14'].id])

    def test_period_labels(self):
        labels = {'7d': "7 derniers jours", 'month': "Ce mois", 'last_month': "Mois dernier",
                  'quarter': "Ce trimestre"}
        for key, label in labels.items():
            with self.subTest(key=key):
                data = self.dashboard(self.manager, period=key)
                key_, start, end = resolve_period(key, False, False, self.today)
                self.assertEqual(data['period']['label'], label)
                self.assertEqual((data['period']['date_from'], data['period']['date_to']),
                                 (start.isoformat(), end.isoformat()))
                self.assertEqual(data['done_days'], (end - start).days + 1)

    def test_no_done_activity_gives_no_rate(self):
        kpis = self.dashboard(self.manager)['kpis']
        self.assertEqual((kpis['done'], kpis['on_time_rate'], kpis['done_delta']), (0, None, None))

    def test_created_activities(self):
        done = self._done_fixture()
        data = self.dashboard(self.manager)
        # 5 activités du jeu d'essai + 6 réalisées, toutes créées aujourd'hui.
        self.assertEqual((data['kpis']['created'], data['kpis']['created_prev']), (11, 0))
        self.assertIsNone(data['kpis']['created_delta'])
        self._set_create_date(done['d14'], datetime.combine(self._days(-10), datetime.min.time()))
        self._set_create_date(done['d13'], datetime.combine(self._days(-30), datetime.min.time()))
        kpis = self.dashboard(self.manager)['kpis']
        self.assertEqual((kpis['created'], kpis['created_prev'], kpis['created_delta']), (9, 1, 800.0))
        kpis = self.dashboard(self.manager, user_id=self.bob.id)['kpis']
        self.assertEqual(kpis['created'], 2, "act_bob et d6 (d13, assignée à Bob, est trop ancienne)")
        kpis = self.dashboard(self.manager, activity_type_id=self.type_call.id)['kpis']
        self.assertEqual(kpis['created'], 2, "act_overdue et act_bob")


@tagged('post_install', '-at_install', 'aite_crm_activity')
class TestDashboardLocalMidnight(DashboardCase):
    """ Date du jour du tableau de bord : celle de l'utilisateur (Douala,
    UTC+1), jamais celle du navigateur ni celle du serveur en UTC. """

    def setUp(self):
        super().setUp()
        self.manager.tz = 'Africa/Douala'
        self.team_douala = self.env['crm.team'].create({'name': "Équipe Douala (test)"})
        self.lead_douala = self.env['crm.lead'].create({
            'name': "Opportunité Douala", 'type': 'opportunity', 'user_id': self.manager.id,
            'team_id': self.team_douala.id,
        })
        self.act_10, self.act_11, self.act_12 = (
            self.env['mail.activity'].create({
                'res_model_id': self.env['ir.model']._get_id('crm.lead'),
                'res_id': self.lead_douala.id, 'user_id': self.manager.id,
                'activity_type_id': self.type_call.id, 'summary': "Échéance du %s" % day,
                'date_deadline': date(2026, 3, day),
            }) for day in (10, 11, 12))

    def _data(self, **filters):
        return self.dashboard(self.manager, team_id=self.team_douala.id, **filters)

    def test_late_evening_is_still_the_same_day(self):
        with freeze_time('2026-03-10 22:30:00'):  # 23 h 30 à Douala, le 10
            data = self._data()
        self.assertEqual(data['today'], '2026-03-10')
        self.assertEqual({k: data['kpis'][k] for k in ('overdue', 'today', 'upcoming')},
                         {'overdue': 0, 'today': 1, 'upcoming': 2})
        self.assertEqual((data['filters']['date_from'], data['filters']['date_to']), ('2026-03-04', '2026-03-10'))
        row = next(r for r in data['activities']['records'] if r['id'] == self.act_10.id)
        self.assertEqual((row['state'], row['days'], row['days_late'], row['severity']), ('today', 0, 0, False))

    def test_after_local_midnight_is_the_next_day(self):
        with freeze_time('2026-03-10 23:30:00'):  # 0 h 30 à Douala, le 11 ; encore le 10 en UTC
            data = self._data()
            utc_data = self.Dashboard.with_user(self.manager).with_context(tz='UTC').get_dashboard_data(
                {'team_id': self.team_douala.id})
            Dashboard = self.Dashboard.with_user(self.manager)
            self.assertEqual(Dashboard.action_reschedule(self.act_12.id, 'tomorrow'), '2026-03-12')
            Dashboard.action_mark_done(self.act_11.id)
            done_7d = self._data()['kpis']['done']
            done_11 = self._data(period='custom', date_from='2026-03-11', date_to='2026-03-11')['kpis']['done']
            done_10 = self._data(period='custom', date_from='2026-03-10', date_to='2026-03-10')['kpis']['done']
        self.assertEqual(data['today'], '2026-03-11')
        self.assertEqual({k: data['kpis'][k] for k in ('overdue', 'today', 'upcoming')},
                         {'overdue': 1, 'today': 1, 'upcoming': 1})
        self.assertEqual((data['filters']['date_from'], data['filters']['date_to']), ('2026-03-05', '2026-03-11'))
        rows = {r['id']: r for r in data['activities']['records']}
        self.assertEqual((rows[self.act_10.id]['state'], rows[self.act_10.id]['days'],
                          rows[self.act_10.id]['days_late'], rows[self.act_10.id]['severity']),
                         ('overdue', -1, 1, 'low'))
        self.assertEqual(rows[self.act_11.id]['state'], 'today')
        self.assertEqual(rows[self.act_12.id]['state'], 'planned')
        self.assertEqual(data['workload']['days'][0], {
            'date': '2026-03-11', 'label': "mer. 11", 'weekday': 2, 'is_today': True, 'is_weekend': False})
        self.assertEqual(data['workload']['rows'][0]['overdue'], 1)
        self.assertEqual(data['workload']['rows'][0]['cells'][:2], [1, 1])
        # Le même instant pour un utilisateur en UTC : encore le 10.
        self.assertEqual(utc_data['today'], '2026-03-10')
        self.assertEqual(utc_data['kpis']['today'], 1)
        # Odoo enregistre la date de réalisation en UTC : faite à 0 h 30 à
        # Douala, elle compte pour le 10 (limite documentée).
        self.assertEqual(self.act_11.date_done, date(2026, 3, 10))
        self.assertEqual((done_7d, done_11, done_10), (1, 0, 1))

    def test_created_follows_the_local_day(self):
        self._set_create_date(self.act_12, datetime(2026, 3, 10, 23, 15))  # 0 h 15 le 11 à Douala
        with freeze_time('2026-03-11 10:00:00'):
            on_11 = self._data(period='custom', date_from='2026-03-11', date_to='2026-03-11')['kpis']['created']
            on_10 = self._data(period='custom', date_from='2026-03-10', date_to='2026-03-10')['kpis']['created']
        self.assertEqual((on_11, on_10), (1, 0))


@tagged('post_install', '-at_install', 'aite_crm_activity')
class TestDashboardSeverityAndAmounts(DashboardCase):

    def test_severity_counts_rows_and_alert(self):
        act_high = self._activity(self.lead_alice, self.alice, -3, self.type_call, "Relance élevée")
        act_critical = self._activity(self.lead_bob, self.bob, -7, self.type_call, "Relance critique")
        data = self.dashboard(self.manager)
        self.assertEqual({k: data['kpis'][k] for k in ('overdue', 'high', 'critical')},
                         {'overdue': 3, 'high': 2, 'critical': 1})
        rows = {r['id']: r for r in data['activities']['records']}
        self.assertEqual(
            {activity.id: (rows[activity.id]['severity'], rows[activity.id]['days_late'])
             for activity in (self.act_overdue, act_high, act_critical, self.act_today, self.act_bob)},
            {self.act_overdue.id: ('low', 2), act_high.id: ('high', 3), act_critical.id: ('critical', 7),
             self.act_today.id: (False, 0), self.act_bob.id: (False, 0)})
        by_user = self._rows(data)
        self.assertEqual({k: by_user[self.alice.id][k] for k in ('overdue', 'high', 'critical')},
                         {'overdue': 2, 'high': 1, 'critical': 0})
        self.assertEqual({k: by_user[self.bob.id][k] for k in ('overdue', 'high', 'critical')},
                         {'overdue': 1, 'high': 1, 'critical': 1})
        self.assertEqual(data['alerts'], [{
            'level': 'danger', 'message': "1 activité en retard de 7 jours ou plus",
            'action': {'bucket': 'overdue'}}])

    def test_thresholds_come_from_settings(self):
        self._activity(self.lead_alice, self.alice, -3, self.type_call, "Relance élevée")
        self._activity(self.lead_bob, self.bob, -7, self.type_call, "Relance critique")
        self._param(PARAM_HIGH_DAYS, 2)
        self._param(PARAM_CRITICAL_DAYS, 3)
        data = self.dashboard(self.manager)
        self.assertEqual(data['thresholds'], {
            'upcoming_days': 7, 'high_days': 2, 'critical_days': 3, 'dormant_days': 14})
        self.assertEqual({k: data['kpis'][k] for k in ('overdue', 'high', 'critical')},
                         {'overdue': 3, 'high': 3, 'critical': 2})
        self.assertEqual(data['alerts'][0]['message'], "2 activités en retard de 3 jours ou plus")
        overdue = self.dashboard(self.manager, bucket='overdue')['activities']['records']
        self.assertEqual([row['severity'] for row in overdue], ['critical', 'critical', 'high'])
        # Réglages incohérents (élevé ≥ critique) : valeurs par défaut.
        self._param(PARAM_HIGH_DAYS, 9)
        self.assertEqual(self.dashboard(self.manager)['thresholds']['high_days'], 3)

    def test_no_alert_without_critical_or_dormant(self):
        self.assertEqual(self.dashboard(self.manager)['alerts'], [])

    def test_overdue_amounts_count_each_lead_once(self):
        self._activity(self.lead_alice, self.alice, -5, self.type_todo, "Second retard")
        kpis = self.dashboard(self.manager)['kpis']
        self.assertEqual((kpis['overdue'], kpis['overdue_leads']), (2, 1))
        self.assertEqual(kpis['overdue_amounts'], [{'currency_id': self.currency.id, 'amount': 1500000.0}])

        self._activity(self.lead_bob, self.alice, -1, self.type_todo, "Retard chez Bob, pour Alice")
        kpis = self.dashboard(self.manager)['kpis']
        self.assertEqual((kpis['overdue'], kpis['overdue_leads']), (3, 2))
        self.assertEqual(kpis['overdue_amounts'], [{'currency_id': self.currency.id, 'amount': 2300000.0}])

    def test_overdue_amounts_exclude_unreadable_leads(self):
        self._activity(self.lead_bob, self.alice, -1, self.type_todo, "Retard chez Bob, pour Alice")
        kpis = self.dashboard(self.alice, team_id=False)['kpis']
        self.assertEqual((kpis['overdue'], kpis['overdue_leads']), (2, 2),
                         "Le nombre compte aussi l'opportunité de Bob")
        self.assertEqual(kpis['overdue_amounts'], [{'currency_id': self.currency.id, 'amount': 1500000.0}],
                         "Le montant de l'opportunité de Bob, illisible pour Alice, n'est pas compté")

    def test_no_amount_when_nothing_at_stake(self):
        self.lead_alice.expected_revenue = 0
        kpis = self.dashboard(self.manager)['kpis']
        self.assertEqual((kpis['overdue_leads'], kpis['overdue_amounts'], kpis['stalled_amounts']), (1, [], []))

    def test_stalled_amounts(self):
        self.lead_quiet.expected_revenue = 250000
        orphan = self.env['crm.lead'].create({
            'name': "Opportunité sans commercial", 'type': 'opportunity', 'user_id': False,
            'team_id': self.team.id, 'expected_revenue': 100000,
        })
        data = self.dashboard(self.manager)
        expected = [{'currency_id': self.currency.id, 'amount': 350000.0}]
        self.assertEqual(data['kpis']['stalled_amounts'], expected)
        self.assertEqual(data['stalled']['amounts'], expected)
        self.assertEqual(self.dashboard(self.manager, user_id='unassigned')['kpis']['stalled_amounts'],
                         [{'currency_id': self.currency.id, 'amount': 100000.0}])
        self.assertIn(orphan.id, self._ids(data['stalled']['records']))

    def test_amounts_per_company_currency(self):
        main_currency = self.env.company.currency_id
        other_currency = self.env.ref('base.EUR') if main_currency != self.env.ref('base.EUR') \
            else self.env.ref('base.USD')
        other_currency.active = True
        other_company = self.env['res.company'].create({
            'name': "Filiale AITE (test)", 'currency_id': other_currency.id})
        lead_other = self.env['crm.lead'].create({
            'name': "Opportunité de la filiale", 'type': 'opportunity', 'user_id': False,
            'team_id': False, 'company_id': other_company.id, 'expected_revenue': 1000,
        })
        amounts = self.Dashboard._amounts(self.lead_alice | self.lead_bob | lead_other)
        self.assertEqual(amounts, sorted([
            {'currency_id': main_currency.id, 'amount': 2300000.0},
            {'currency_id': other_currency.id, 'amount': 1000.0},
        ], key=lambda a: a['currency_id']))
        self.assertEqual(self.Dashboard._amounts(self.env['crm.lead']), [])


@tagged('post_install', '-at_install', 'aite_crm_activity')
class TestDashboardStalled(DashboardCase):
    """ Dernière action et opportunités dormantes. """

    def test_last_action_from_stage_change(self):
        record = self.dashboard(self.manager)['stalled']['records'][0]
        self.assertEqual((record['id'], record['last_action_date'], record['idle_days'], record['dormant']),
                         (self.lead_quiet.id, self.today.isoformat(), 0, False))

    def test_dormant_lead_and_alert(self):
        self._set_stage_update(self.lead_quiet, datetime.combine(self._days(-20), datetime.min.time()))
        data = self.dashboard(self.manager)
        record = data['stalled']['records'][0]
        self.assertEqual((record['last_action_date'], record['idle_days'], record['dormant']),
                         (self._days(-20).isoformat(), 20, True))
        self.assertEqual(data['stalled']['dormant'], 1)
        self.assertEqual(data['alerts'], [{
            'level': 'warning', 'message': "1 opportunité sans action depuis 14 jours ou plus",
            'action': {'focus': 'stalled'}}])

    def test_last_done_activity_counts_as_an_action(self):
        self._set_stage_update(self.lead_quiet, datetime.combine(self._days(-20), datetime.min.time()))
        self._done_activity(self.lead_quiet, self.alice, self._days(-6), self._days(-5))
        self._done_activity(self.lead_quiet, self.alice, self._days(-9), self._days(-9))
        data = self.dashboard(self.manager)
        record = data['stalled']['records'][0]
        self.assertEqual((record['last_action_date'], record['idle_days'], record['dormant']),
                         (self._days(-5).isoformat(), 5, False))
        self.assertEqual((data['stalled']['dormant'], data['alerts']), (0, []))
        self.assertEqual(data['kpis']['stalled'], 1, "Une activité réalisée ne planifie rien")

    def test_dormant_threshold_setting_and_plural(self):
        second = self.env['crm.lead'].create({
            'name': "Deuxième opportunité dormante", 'type': 'opportunity', 'user_id': self.alice.id,
            'team_id': self.team.id,
        })
        for lead in (self.lead_quiet, second):
            self._set_stage_update(lead, datetime.combine(self._days(-4), datetime.min.time()))
        self.assertEqual(self.dashboard(self.manager)['stalled']['dormant'], 0)
        self._param(PARAM_DORMANT_DAYS, 4)
        data = self.dashboard(self.manager)
        self.assertEqual(data['stalled']['dormant'], 2)
        self.assertEqual(data['alerts'][0]['message'], "2 opportunités sans action depuis 4 jours ou plus")
        self._param(PARAM_DORMANT_DAYS, 1)
        self.assertEqual(self.dashboard(self.manager)['alerts'][0]['message'],
                         "2 opportunités sans action depuis 1 jour ou plus")

    def test_dormant_count_covers_leads_beyond_the_list(self):
        extra = self.env['crm.lead'].create([{
            'name': "Opportunité %s" % index, 'type': 'opportunity', 'user_id': self.alice.id,
            'team_id': self.team.id, 'expected_revenue': 1000 * index,
        } for index in range(1, 4)])
        self._set_stage_update(self.lead_quiet, datetime.combine(self._days(-30), datetime.min.time()))
        with patch.object(crm_activity_dashboard, 'STALLED_LIMIT', 2):
            stalled = self.dashboard(self.manager)['stalled']
        self.assertEqual(stalled['total'], 4)
        self.assertEqual(self._ids(stalled['records']), [extra[2].id, extra[1].id])
        self.assertEqual(stalled['dormant'], 1, "lead_quiet, absente des lignes affichées")


@tagged('post_install', '-at_install', 'aite_crm_activity')
class TestDashboardWorkload(DashboardCase):
    """ Plan de charge : personnes × jours. """

    def test_matrix_values(self):
        data = self.dashboard(self.manager)
        workload = data['workload']
        self.assertEqual(len(workload['days']), 8, "Aujourd'hui + 7 jours")
        for index, day in enumerate(workload['days']):
            current = self._days(index)
            with self.subTest(day=index):
                self.assertEqual(day, {
                    'date': current.isoformat(),
                    'label': '%s %d' % (WEEKDAYS_SHORT[current.weekday()], current.day),
                    'weekday': current.weekday(),
                    'is_today': index == 0,
                    'is_weekend': current.weekday() in (5, 6),
                })
        self.assertEqual(workload['rows'], [
            {'user_id': self.alice.id, 'name': "Alice Commerciale", 'overdue': 1,
             'cells': [1, 1, 0, 0, 0, 0, 0, 0], 'total': 3},
            {'user_id': self.bob.id, 'name': "Bob Commercial", 'overdue': 0,
             'cells': [0, 0, 0, 1, 0, 0, 0, 0], 'total': 1},
        ])
        self.assertEqual(workload['max'], 1)

    def test_matrix_unassigned_max_and_filters(self):
        self.env['mail.activity'].create({
            'res_model_id': self.env['ir.model']._get_id('crm.lead'), 'res_id': self.lead_bob.id,
            'user_id': False, 'activity_type_id': self.type_todo.id, 'summary': "À attribuer",
            'date_deadline': self._days(2),
        })
        for __ in range(2):
            self._activity(self.lead_alice, self.alice, 0, self.type_call, "Encore aujourd'hui")
        workload = self.dashboard(self.manager)['workload']
        rows = {row['user_id']: row for row in workload['rows']}
        self.assertEqual(rows[self.alice.id]['cells'][0], 3)
        self.assertEqual(rows['unassigned'], {
            'user_id': 'unassigned', 'name': "Non assigné", 'overdue': 0,
            'cells': [0, 0, 1, 0, 0, 0, 0, 0], 'total': 1})
        self.assertEqual(workload['max'], 3)
        # Le filtre de commercial ne s'applique pas (outil de navigation)…
        self.assertEqual(self.dashboard(self.manager, user_id=self.bob.id)['workload']['rows'], workload['rows'])
        # … le type et l'équipe, si.
        typed = self.dashboard(self.manager, activity_type_id=self.type_call.id)['workload']
        self.assertEqual({row['user_id']: (row['overdue'], row['cells'], row['total']) for row in typed['rows']}, {
            self.alice.id: (1, [2, 0, 0, 0, 0, 0, 0, 0], 3),
            self.bob.id: (0, [0, 0, 0, 1, 0, 0, 0, 0], 1),
        })
        other_team = self.env['crm.team'].create({'name': "Équipe vide (test)"})
        empty = self.dashboard(self.manager, team_id=other_team.id)['workload']
        self.assertEqual((empty['rows'], empty['max'], len(empty['days'])), ([], 0, 8))

    def test_matrix_window_follows_the_setting_and_is_capped(self):
        self._param(PARAM_DASHBOARD_UPCOMING_DAYS, 30)
        data = self.dashboard(self.manager)
        self.assertEqual(data['upcoming_days'], 30)
        self.assertEqual(data['kpis']['upcoming'], 3, "J+30 entre dans la fenêtre « À venir »")
        self.assertEqual(len(data['workload']['days']), 14, "Deux semaines au plus")
        rows = {row['user_id']: row for row in data['workload']['rows']}
        self.assertEqual(rows[self.alice.id]['total'], 3, "J+30 reste hors du plan de charge")
        self._param(PARAM_DASHBOARD_UPCOMING_DAYS, 2)
        data = self.dashboard(self.manager)
        self.assertEqual((data['kpis']['upcoming'], len(data['workload']['days'])), (1, 3))


@tagged('post_install', '-at_install', 'aite_crm_activity')
class TestDashboardConsistency(DashboardCase):
    """ Les blocs du tableau de bord racontent la même histoire. """

    def setUp(self):
        super().setUp()
        self._activity(self.lead_alice, self.alice, -9, self.type_call, "Retard critique")
        self._activity(self.lead_bob, self.bob, -4, self.type_todo, "Retard élevé")
        self.env['mail.activity'].create({
            'res_model_id': self.env['ir.model']._get_id('crm.lead'), 'res_id': self.lead_bob.id,
            'user_id': False, 'activity_type_id': self.type_todo.id, 'summary': "À attribuer",
            'date_deadline': self._days(-1),
        })
        self.env['crm.lead'].create({
            'name': "Opportunité sans commercial", 'type': 'opportunity', 'user_id': False,
            'team_id': self.team.id,
        })
        self._done_activity(self.lead_alice, self.alice, self._days(-1), self._days(-1))
        self._done_activity(self.lead_bob, self.bob, self._days(-5), self._days(-2), self.type_call)
        self._done_activity(self.lead_bob, self.bob, self._days(-20), self._days(-20))  # hors période

    def test_blocks_add_up_to_the_kpis(self):
        filter_sets = {
            "équipe": {},
            "type appel": {'activity_type_id': self.type_call.id},
            "type à faire": {'activity_type_id': self.type_todo.id},
            "ce mois": {'period': 'month'},
            "sans équipe": {'team_id': False},
        }
        for label, filters in filter_sets.items():
            with self.subTest(filters=label):
                data = self.dashboard(self.manager, **filters)
                kpis, by_user = data['kpis'], data['by_user']
                for key in ('overdue', 'today', 'upcoming', 'done', 'stalled', 'high', 'critical'):
                    self.assertEqual(sum(row[key] for row in by_user['rows']), kpis[key], key)
                    self.assertEqual(by_user['total'][key], kpis[key], key)
                for bucket in ('overdue', 'today', 'upcoming', 'done'):
                    listed = self.dashboard(self.manager, bucket=bucket, **filters)['activities']
                    self.assertEqual(listed['total'], kpis[bucket], bucket)
                self.assertEqual(self.dashboard(self.manager, bucket='all', **filters)['activities']['total'],
                                 kpis['open'])
                self.assertEqual(data['stalled']['total'], kpis['stalled'])
                workload = data['workload']['rows']
                self.assertEqual(sum(row['overdue'] for row in workload), kpis['overdue'])
                self.assertEqual(sum(row['cells'][0] for row in workload), kpis['today'])
                self.assertEqual(sum(sum(row['cells'][1:]) for row in workload), kpis['upcoming'])

    def test_expected_values_of_the_fixture(self):
        kpis = self.dashboard(self.manager)['kpis']
        self.assertEqual(
            {key: kpis[key] for key in ('overdue', 'today', 'upcoming', 'open', 'done', 'stalled',
                                        'high', 'critical', 'overdue_leads', 'on_time_rate')},
            {'overdue': 4, 'today': 1, 'upcoming': 2, 'open': 8, 'done': 2, 'stalled': 2,
             'high': 2, 'critical': 1, 'overdue_leads': 2, 'on_time_rate': 50.0})


@tagged('post_install', '-at_install', 'aite_crm_activity')
class TestDashboardFilterMatrix(DashboardCase):
    """ Propagation de chaque filtre à chaque bloc, exceptions comprises. """

    def setUp(self):
        super().setUp()
        self.act_unassigned = self.env['mail.activity'].create({
            'res_model_id': self.env['ir.model']._get_id('crm.lead'), 'res_id': self.lead_bob.id,
            'user_id': False, 'activity_type_id': self.type_todo.id, 'summary': "À attribuer",
            'date_deadline': self._days(-1),
        })
        self.lead_orphan = self.env['crm.lead'].create({
            'name': "Opportunité sans commercial", 'type': 'opportunity', 'user_id': False,
            'team_id': self.team.id,
        })

    def test_matrix(self):
        everyone = {self.act_overdue, self.act_today, self.act_far, self.act_bob,
                    self.act_on_bob_for_alice, self.act_unassigned}
        empty_team = self.env['crm.team'].create({'name': "Équipe vide (test)"})
        cases = {
            # libellé : (filtres, (retard, jour, à venir, ouvertes, sans activité), activités, sans activité)
            "équipe": ({}, (2, 1, 2, 6, 2), everyone, {self.lead_quiet, self.lead_orphan}),
            "type appel": ({'activity_type_id': self.type_call.id}, (1, 0, 1, 2, 2),
                           {self.act_overdue, self.act_bob}, {self.lead_quiet, self.lead_orphan}),
            "type à faire": ({'activity_type_id': self.type_todo.id}, (1, 1, 1, 4, 2),
                             {self.act_today, self.act_far, self.act_on_bob_for_alice, self.act_unassigned},
                             {self.lead_quiet, self.lead_orphan}),
            "Alice": ({'user_id': self.alice.id}, (1, 1, 1, 4, 1),
                      {self.act_overdue, self.act_today, self.act_far, self.act_on_bob_for_alice},
                      {self.lead_quiet}),
            "Bob": ({'user_id': self.bob.id}, (0, 0, 1, 1, 0), {self.act_bob}, set()),
            "non assigné": ({'user_id': 'unassigned'}, (1, 0, 0, 1, 1), {self.act_unassigned},
                            {self.lead_orphan}),
            "Alice + appel": ({'user_id': self.alice.id, 'activity_type_id': self.type_call.id},
                              (1, 0, 0, 1, 1), {self.act_overdue}, {self.lead_quiet}),
            "équipe vide": ({'team_id': empty_team.id}, (0, 0, 0, 0, 0), set(), set()),
        }
        reference_rows = self._rows(self.dashboard(self.manager))
        typed_rows = {key: self._rows(self.dashboard(self.manager, activity_type_id=key))
                      for key in (self.type_call.id, self.type_todo.id)}
        for label, (filters, counts, activities, stalled) in cases.items():
            with self.subTest(filters=label):
                data = self.dashboard(self.manager, **filters)
                kpis = data['kpis']
                self.assertEqual(tuple(kpis[k] for k in ('overdue', 'today', 'upcoming', 'open', 'stalled')),
                                 counts)
                self.assertEqual(set(self._ids(data['activities']['records'])), {a.id for a in activities})
                self.assertEqual(set(self._ids(data['stalled']['records'])), {lead.id for lead in stalled})
                self.assertEqual(data['filter_notes']['stalled_ignores_type'],
                                 bool(filters.get('activity_type_id')))
                if 'team_id' in filters:
                    self.assertEqual(data['by_user']['rows'], [])
                    self.assertEqual(data['workload']['rows'], [])
                    continue
                # Exception voulue : « Par commercial » ignore le filtre de
                # commercial, mais suit le type.
                expected_rows = typed_rows.get(filters.get('activity_type_id'), reference_rows)
                self.assertEqual(self._rows(data), expected_rows)

    def test_type_filter_changes_by_user_but_not_its_stalled_column(self):
        rows = self._rows(self.dashboard(self.manager, activity_type_id=self.type_call.id))
        self.assertEqual({key: (row['overdue'], row['upcoming'], row['stalled']) for key, row in rows.items()}, {
            self.alice.id: (1, 0, 1), self.bob.id: (0, 1, 0), 'unassigned': (0, 0, 1)})


@tagged('post_install', '-at_install', 'aite_crm_activity')
class TestDashboardTrend(DashboardCase):
    """ Tendances sur 12 semaines ISO. """

    def test_iso_weeks(self):
        weeks = iso_weeks(date(2026, 1, 7))
        self.assertEqual(len(weeks), 12)
        self.assertEqual(weeks[-1], {'key': '2026-W02', 'label': '05/01',
                                     'date_from': date(2026, 1, 5), 'date_to': date(2026, 1, 11)})
        self.assertEqual(weeks[0], {'key': '2025-W43', 'label': '20/10',
                                    'date_from': date(2025, 10, 20), 'date_to': date(2025, 10, 26)})
        self.assertTrue(all((b['date_from'] - a['date_from']).days == 7 for a, b in zip(weeks, weeks[1:])))
        # Semaine 53 et année ISO différente de l'année civile.
        self.assertEqual(iso_weeks(date(2027, 1, 3))[-1]['key'], '2026-W53')
        self.assertEqual(iso_weeks(date(2027, 1, 4))[-1]['key'], '2027-W01')
        self.assertEqual([w['key'] for w in iso_weeks(date(2026, 11, 13), count=2)], ['2026-W45', '2026-W46'])

    def test_weekly_buckets_without_database(self):
        monday = date(2026, 1, 5)
        self.assertEqual(week_index(monday, date(2026, 1, 11), 2), 0)
        self.assertEqual(week_index(monday, date(2026, 1, 12), 2), 1)
        self.assertEqual(week_index(monday, datetime(2026, 1, 18, 23, 59), 2), 1)
        self.assertIsNone(week_index(monday, date(2026, 1, 19), 2))
        self.assertIsNone(week_index(monday, date(2026, 1, 4), 2))
        self.assertIsNone(week_index(monday, False, 2))
        rows = [
            (date(2026, 1, 5), date(2026, 1, 5), 2),    # semaine 0, le jour même : à temps
            (date(2026, 1, 6), date(2026, 1, 5), 1),    # semaine 0, un jour après : en retard
            (date(2026, 1, 12), date(2026, 1, 20), 3),  # semaine 1, en avance
            (date(2026, 1, 18), False, 1),              # sans échéance : à temps
            (date(2026, 1, 19), date(2026, 1, 1), 5),   # hors période
            (date(2026, 1, 4), date(2026, 1, 1), 1),    # hors période
            (None, date(2026, 1, 1), 1),                # sans date
        ]
        self.assertEqual(bucket_done_by_week(rows, monday, 2), ([2, 4], [1, 0]))
        self.assertEqual(bucket_done_by_week([], monday, 3), ([0, 0, 0], [0, 0, 0]))
        self.assertEqual(bucket_counts_by_week(
            [(datetime(2026, 1, 5, 0, 0), 4), (date(2026, 1, 13), 2), (date(2026, 2, 1), 9)], monday, 2),
            [4, 2])

    def test_trend_data(self):
        weeks = iso_weeks(self.today)
        first_monday = weeks[0]['date_from']
        t0 = self._done_activity(self.lead_alice, self.alice, self.today, self.today, self.type_call)
        t1 = self._done_activity(self.lead_bob, self.bob, self._days(-10), self._days(-7), self.type_todo)
        t2 = self._done_activity(self.lead_alice, self.alice, first_monday, first_monday, self.type_call)
        t3 = self._done_activity(self.lead_alice, self.alice, first_monday, first_monday - timedelta(days=1))
        self._set_create_date(t2, datetime.combine(first_monday, datetime.min.time()) + timedelta(hours=10))
        self._set_create_date(t3, datetime.combine(first_monday, datetime.min.time()) - timedelta(days=3))

        data = self.Dashboard.with_user(self.manager).get_trend_data({'team_id': self.team.id})
        json.dumps(data)
        self.assertEqual(set(data), {'weeks', 'done_on_time', 'done_late', 'created', 'on_time_rate',
                                     'by_type', 'by_user'})
        self.assertEqual(data['weeks'][-1]['date_to'], (weeks[-1]['date_to']).isoformat())
        self.assertEqual(data['weeks'][0], {
            'key': weeks[0]['key'], 'label': first_monday.strftime('%d/%m'),
            'date_from': first_monday.isoformat(), 'date_to': (first_monday + timedelta(days=6)).isoformat()})
        self.assertEqual(data['done_on_time'], [1] + [0] * 10 + [1])
        self.assertEqual(data['done_late'], [0] * 10 + [1, 0])
        # 5 activités du jeu d'essai + t0 et t1 créées cette semaine ; t2 la
        # première semaine ; t3 avant la période.
        self.assertEqual(data['created'], [1] + [0] * 10 + [7])
        self.assertEqual(data['on_time_rate'], 66.7)
        self.assertEqual(data['by_type'], [
            {'type_id': self.type_call.id, 'name': self.type_call.name, 'done': 2, 'late': 0, 'on_time_rate': 100.0},
            {'type_id': self.type_todo.id, 'name': self.type_todo.name, 'done': 1, 'late': 1, 'on_time_rate': 0.0},
        ])
        self.assertEqual(data['by_user'], [
            {'user_id': self.alice.id, 'name': "Alice Commerciale", 'done': 2, 'late': 0, 'on_time_rate': 100.0},
            {'user_id': self.bob.id, 'name': "Bob Commercial", 'done': 1, 'late': 1, 'on_time_rate': 0.0},
        ])
        self.assertTrue(t1.date_done > t1.date_deadline)

    def test_trend_follows_filters_not_period(self):
        self._done_activity(self.lead_alice, self.alice, self.today, self.today, self.type_call)
        self._done_activity(self.lead_bob, self.bob, self._days(-10), self._days(-7), self.type_todo)
        Dashboard = self.Dashboard.with_user(self.manager)
        bob = Dashboard.get_trend_data({'team_id': self.team.id, 'user_id': self.bob.id})
        self.assertEqual((sum(bob['done_on_time']), sum(bob['done_late']), bob['on_time_rate']), (0, 1, 0.0))
        self.assertEqual([row['user_id'] for row in bob['by_user']], [self.bob.id])
        self.assertEqual(bob['created'][-1], 2, "act_bob et la réalisée de Bob")
        calls = Dashboard.get_trend_data({'team_id': self.team.id, 'activity_type_id': self.type_call.id})
        self.assertEqual((sum(calls['done_on_time']), sum(calls['done_late']), calls['on_time_rate']), (1, 0, 100.0))
        period = Dashboard.get_trend_data({'team_id': self.team.id, 'period': 'custom',
                                           'date_from': '2000-01-01', 'date_to': '2000-01-31'})
        self.assertEqual(sum(period['done_on_time']) + sum(period['done_late']), 2, "La période ne compte pas")
        empty_team = self.env['crm.team'].create({'name': "Équipe vide (test)"})
        empty = Dashboard.get_trend_data({'team_id': empty_team.id})
        self.assertEqual((empty['done_on_time'], empty['created'], empty['on_time_rate'],
                          empty['by_type'], empty['by_user']), ([0] * 12, [0] * 12, None, [], []))

    def test_trend_for_salesman_is_her_own_by_default(self):
        self._done_activity(self.lead_alice, self.alice, self.today, self.today, self.type_call)
        self._done_activity(self.lead_bob, self.bob, self._days(-10), self._days(-7), self.type_todo)
        data = self.Dashboard.with_user(self.alice).get_trend_data({})
        self.assertEqual((sum(data['done_on_time']), sum(data['done_late'])), (1, 0))
        self.assertEqual([row['user_id'] for row in data['by_user']], [self.alice.id])


@tagged('post_install', '-at_install', 'aite_crm_activity')
class TestLeadPreview(DashboardCase):
    """ Panneau d'aperçu d'une opportunité. """

    def test_preview_values(self):
        self.lead_alice.write({
            'date_deadline': self._days(20), 'priority': '2', 'phone': '+237 699 00 00 00',
            'email_from': 'client@aite.example',
        })
        self.Dashboard.with_user(self.alice).action_mark_done(self.act_overdue.id, "Client rappelé")
        older = self._done_activity(self.lead_alice, self.bob, self._days(-9), self._days(-3),
                                    self.type_call, "Démonstration")
        older.feedback = "<p>Devis <b>envoyé</b> &amp; relancé</p>"
        data = self.Dashboard.with_user(self.manager).get_lead_preview(self.lead_alice.id)
        json.dumps(data)
        self.assertEqual({k: v for k, v in data.items() if k not in ('open_activities', 'done_activities')}, {
            'id': self.lead_alice.id, 'name': "Opportunité Alice", 'partner': "Client Test",
            'phone': '+237 699 00 00 00', 'email': 'client@aite.example',
            'stage': self.lead_alice.stage_id.name, 'team': "Équipe de test AITE", 'user': "Alice Commerciale",
            'expected_revenue': 1500000.0, 'currency_id': self.currency.id,
            'probability': self.lead_alice.probability, 'priority': '2',
            'date_deadline': self._days(20).isoformat(),
            'last_action_date': self.today.isoformat(), 'idle_days': 0,
        })
        self.assertEqual(data['open_activities'], [
            {'id': self.act_today.id, 'type': self.type_todo.name, 'icon': self.type_todo.icon or 'fa-tasks',
             'summary': "Envoyer le devis", 'date_deadline': self.today.isoformat(), 'days': 0,
             'state': 'today', 'severity': False, 'user': "Alice Commerciale", 'can_write': True},
            {'id': self.act_far.id, 'type': self.type_todo.name, 'icon': self.type_todo.icon or 'fa-tasks',
             'summary': "Point trimestriel", 'date_deadline': self._days(30).isoformat(), 'days': 30,
             'state': 'planned', 'severity': False, 'user': "Alice Commerciale", 'can_write': True},
        ])
        self.assertEqual(data['done_activities'], [
            {'type': self.type_call.name, 'icon': self.type_call.icon or 'fa-tasks', 'summary': "Rappeler le client",
             'date_done': self.today.isoformat(), 'feedback': "Client rappelé", 'user': "Alice Commerciale"},
            {'type': self.type_call.name, 'icon': self.type_call.icon or 'fa-tasks', 'summary': "Démonstration",
             'date_done': self._days(-3).isoformat(), 'feedback': "Devis envoyé & relancé", 'user': "Bob Commercial"},
        ])

    def test_preview_feedback_is_plain_text(self):
        """ mail.activity.feedback est un champ Text : « < » et « > » saisis
        par l'utilisateur et les retours à la ligne sont rendus tels quels. """
        done = self._done_activity(self.lead_alice, self.alice, self._days(-2), self._days(-2),
                                   self.type_call, "Appel")
        Dashboard = self.Dashboard.with_user(self.manager)
        for feedback, expected in (
            ("Rappeler <Jean>\nsuite : devis", "Rappeler <Jean>\nsuite : devis"),
            ("Premier point\nDeuxième ligne <b>gras</b>  ", "Premier point\nDeuxième ligne <b>gras</b>"),
            ("<p>Devis <b>envoyé</b></p>", "Devis envoyé"),
        ):
            with self.subTest(feedback=feedback):
                done.feedback = feedback
                data = Dashboard.get_lead_preview(self.lead_alice.id)
                self.assertEqual(data['done_activities'][0]['feedback'], expected)

    def test_preview_open_activity_severity(self):
        late = self._activity(self.lead_alice, self.alice, -8, self.type_call, "Très en retard")
        data = self.Dashboard.with_user(self.manager).get_lead_preview(self.lead_alice.id)
        rows = {row['id']: row for row in data['open_activities']}
        self.assertEqual([row['id'] for row in data['open_activities']],
                         [late.id, self.act_overdue.id, self.act_today.id, self.act_far.id])
        self.assertEqual((rows[late.id]['days'], rows[late.id]['state'], rows[late.id]['severity']),
                         (-8, 'overdue', 'critical'))
        self.assertEqual((rows[self.act_overdue.id]['state'], rows[self.act_overdue.id]['severity']),
                         ('overdue', 'low'))

    def test_preview_keeps_the_last_five_done_newest_first(self):
        done = [self._done_activity(self.lead_alice, self.alice, self._days(-index), self._days(-index),
                                    summary="Réalisée %s" % index) for index in range(1, 7)]
        data = self.Dashboard.with_user(self.manager).get_lead_preview(self.lead_alice.id)
        self.assertEqual([row['summary'] for row in data['done_activities']],
                         ["Réalisée %s" % index for index in range(1, 6)])
        self.assertEqual(data['done_activities'][0]['date_done'], done[0].date_done.isoformat())
        self.assertEqual((data['last_action_date'], data['idle_days']), (self.today.isoformat(), 0),
                         "Le changement d'étape d'aujourd'hui est plus récent")
        self._set_stage_update(self.lead_alice, datetime.combine(self._days(-30), datetime.min.time()))
        data = self.Dashboard.with_user(self.manager).get_lead_preview(self.lead_alice.id)
        self.assertEqual((data['last_action_date'], data['idle_days']), (self._days(-1).isoformat(), 1))

    def test_preview_access(self):
        Dashboard = self.Dashboard.with_user(self.alice)
        with self.assertRaises(AccessError):
            Dashboard.get_lead_preview(self.lead_bob.id)
        # Libellés lus en sudo après le contrôle : un client passé dans une
        # autre société ne bloque pas l'aperçu.
        self.partner.company_id = self.env['res.company'].create({'name': "Autre société AITE"})
        data = Dashboard.get_lead_preview(self.lead_alice.id)
        self.assertEqual(data['partner'], "Client Test")
        self.assertTrue(all(row['can_write'] for row in data['open_activities']))
        self.assertEqual([row['id'] for row in data['open_activities']],
                         [self.act_overdue.id, self.act_today.id, self.act_far.id])
        for bad in (0, -1, 'abc', None, 10 ** 9):
            with self.subTest(lead_id=bad), self.assertRaises(UserError):
                Dashboard.get_lead_preview(bad)

    def test_preview_of_a_lost_lead(self):
        self.Dashboard.with_user(self.alice).action_mark_done(self.act_overdue.id)
        self.lead_alice.action_set_lost()
        data = self.Dashboard.with_user(self.manager).get_lead_preview(self.lead_alice.id)
        self.assertEqual(data['open_activities'], [], "Plus rien à faire sur une opportunité perdue")
        self.assertEqual([row['summary'] for row in data['done_activities']], ["Rappeler le client"])


@tagged('post_install', '-at_install', 'aite_crm_activity')
class TestDashboardSettings(DashboardCase):
    """ Réglages du tableau de bord et des seuils (CRM → Paramètres). """

    def test_defaults(self):
        settings = self.env['res.config.settings'].create({})
        self.assertEqual(
            (settings.aite_crm_dashboard_upcoming_days, settings.aite_crm_late_high_days,
             settings.aite_crm_late_critical_days, settings.aite_crm_dormant_days),
            (7, 3, 7, 14))

    def test_valid_values_are_stored(self):
        self.env['res.config.settings'].create({
            'aite_crm_dashboard_upcoming_days': 10, 'aite_crm_late_high_days': 2,
            'aite_crm_late_critical_days': 5, 'aite_crm_dormant_days': 30,
        }).set_values()
        self.assertEqual(get_thresholds(self.env), {
            'upcoming_days': 10, 'high_days': 2, 'critical_days': 5, 'dormant_days': 30})
        self.assertEqual(self.dashboard(self.manager)['thresholds'], {
            'upcoming_days': 10, 'high_days': 2, 'critical_days': 5, 'dormant_days': 30})
        settings = self.env['res.config.settings'].create({})
        self.assertEqual((settings.aite_crm_dashboard_upcoming_days, settings.aite_crm_dormant_days), (10, 30))

    def test_invalid_values_are_refused(self):
        """ Rien n'est enregistré, que les Paramètres aient déjà été
        enregistrés une fois ou non. """
        params = self.env['ir.config_parameter'].sudo()
        stored = {key: params.get_param(key) for key in THRESHOLD_PARAMS}
        self.assertEqual(stored, dict.fromkeys(THRESHOLD_PARAMS, False), "Base neuve (tests/common.py)")
        cases = {
            "fenêtre à 0": {'aite_crm_dashboard_upcoming_days': 0},
            "fenêtre trop longue": {'aite_crm_dashboard_upcoming_days': 366},
            "élevé à 0": {'aite_crm_late_high_days': 0},
            "critique trop long": {'aite_crm_late_critical_days': 400},
            "dormante négative": {'aite_crm_dormant_days': -1},
            "élevé = critique": {'aite_crm_late_high_days': 5, 'aite_crm_late_critical_days': 5},
            "élevé > critique": {'aite_crm_late_high_days': 8, 'aite_crm_late_critical_days': 5},
        }
        defaults = {'upcoming_days': 7, 'high_days': 3, 'critical_days': 7, 'dormant_days': 14}

        def assert_refused():
            for label, values in cases.items():
                with self.subTest(case=label), self.assertRaises(ValidationError):
                    self.env['res.config.settings'].create(values).set_values()
            self.assertEqual(get_thresholds(self.env), defaults, "Rien n'a été enregistré")
            self.assertEqual({key: params.get_param(key) for key in THRESHOLD_PARAMS}, stored)

        assert_refused()
        # Paramètres enregistrés une fois sans rien changer (bouton
        # « Enregistrer ») : les valeurs par défaut sont alors stockées.
        self.env['res.config.settings'].create({}).set_values()
        stored = {key: params.get_param(key) for key in THRESHOLD_PARAMS}
        self.assertEqual(stored, {
            PARAM_DASHBOARD_UPCOMING_DAYS: '7', PARAM_HIGH_DAYS: '3',
            PARAM_CRITICAL_DAYS: '7', PARAM_DORMANT_DAYS: '14'})
        assert_refused()

    def test_fields_are_in_the_activity_block(self):
        arch = self.env['res.config.settings'].get_view(view_type='form')['arch']
        block = arch[arch.index('id="aite_crm_activity_settings"'):]
        block = block[:block.index('</block>')]
        for fname in ('aite_crm_digest_active', 'aite_crm_dashboard_upcoming_days', 'aite_crm_late_high_days',
                      'aite_crm_late_critical_days', 'aite_crm_dormant_days'):
            with self.subTest(field=fname):
                self.assertIn('name="%s"' % fname, block)

    def test_error_message_is_french(self):
        with self.assertRaises(ValidationError) as error:
            self.env['res.config.settings'].create({'aite_crm_dormant_days': 0}).set_values()
        self.assertIn("Opportunité dormante après (jours)", str(error.exception))
        self.assertIn("entre 1 et 365", str(error.exception))
        with self.assertRaises(ValidationError) as error:
            self.env['res.config.settings'].create({
                'aite_crm_late_high_days': 7, 'aite_crm_late_critical_days': 7}).set_values()
        self.assertIn("doit commencer avant le retard critique", str(error.exception))
