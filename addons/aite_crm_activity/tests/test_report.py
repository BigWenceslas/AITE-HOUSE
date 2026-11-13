# -*- coding: utf-8 -*-
""" Rapport d'analyse des activités (aite.crm.activity.report).

Règles vérifiées :

- R1 : les nombres du rapport (en retard, du jour, à venir, réalisées,
  en cours) sont ceux du tableau de bord, pour un responsable comme pour
  un commercial ;
- R2 : un commercial « mes documents » voit ses activités, celles de ses
  opportunités (même assignées à un collègue) et celles des opportunités
  sans commercial ; jamais celles d'un collègue sur l'opportunité de ce
  collègue. C'est exactement ce que lui montre mail.activity ;
- R3 : société : rien d'une société non active ;
- R4 : état, jours de retard et gravité calculés à la date du jour de la
  personne assignée, avec les seuils des Paramètres lus à chaque requête ;
- R5 : réalisées à temps (0/100 par activité réalisée, vide pour les
  activités en cours : la moyenne donne le taux) ;
- R6 : une activité ouverte sur une opportunité perdue (archivée) sort du
  rapport, une activité réalisée y reste ;
- R7 : vues, filtres, action (chemin analyse-activites) et menu se
  chargent et répondent aux appels du tableau croisé, du graphique et de
  la liste ;
- R8 : sur une ligne de l'opportunité d'un collègue qu'il ne peut pas lire,
  le commercial ne voit que le nom de l'opportunité (client, étape,
  commercial, issue restent vides, en liste, regroupement, filtre et
  export), et l'export de ses lignes fonctionne.
"""
from datetime import datetime, time, timedelta

from freezegun import freeze_time
from lxml import etree

from odoo import Command
from odoo.exceptions import AccessError
from odoo.tests import new_test_user, tagged
from odoo.tools import SQL
from odoo.tools.safe_eval import safe_eval

from odoo.addons.aite_crm_activity.models import crm_activity_params
from odoo.addons.aite_crm_activity.models.crm_activity_params import (
    PARAM_CRITICAL_DAYS, PARAM_HIGH_DAYS, actionable_activity_domain, get_thresholds,
)
from .common import AiteCrmActivityCase

REPORT = 'aite.crm.activity.report'


@tagged('post_install', '-at_install', 'aite_crm_activity')
class TestCrmActivityReport(AiteCrmActivityCase):
    """ Jeu d'essai commun (tests/common.py), complété ici :

    - act_bob_on_alice : activité de Bob sur l'opportunité d'Alice (J+4) ;
    - lead_free / act_free : opportunité sans commercial, activité de Bob (J+2) ;
    - act_done_late : activité d'Alice échue à J-5, faite aujourd'hui (en retard) ;
    - act_done_on_time : activité de Bob échue à J+2, faite aujourd'hui (à temps).
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.lead_free = cls.env['crm.lead'].create({
            'name': "Opportunité sans commercial", 'type': 'opportunity', 'user_id': False,
            'team_id': cls.team.id,
        })
        cls.act_bob_on_alice = cls._activity(
            cls.lead_alice, cls.bob, 4, cls.type_call, "Visite technique")
        cls.act_free = cls._activity(cls.lead_free, cls.bob, 2, cls.type_todo, "Qualifier")
        cls.act_done_late = cls._activity(cls.lead_alice, cls.alice, -5, cls.type_call, "Relance")
        cls.act_done_on_time = cls._activity(cls.lead_bob, cls.bob, 2, cls.type_todo, "Devis")
        (cls.act_done_late | cls.act_done_on_time).action_feedback(feedback="Fait")

    # Outils ------------------------------------------------------------

    def report(self, user=None):
        Report = self.env[REPORT]
        return Report.with_user(user) if user else Report

    def team_domain(self):
        return [('team_id', '=', self.team.id)]

    def rows(self, user=None, domain=None):
        """ Lignes du rapport de l'équipe de test, par activité. """
        records = self.report(user).search(self.team_domain() + (domain or []))
        return {r.activity_id.id: r for r in records}

    def counts_by_state(self, user=None, domain=None):
        groups = self.report(user)._read_group(
            self.team_domain() + (domain or []), ['state'], ['__count'])
        return dict(groups)

    def report_vs_dashboard(self, data, counts, user=None, domain=None):
        """ Nombres du rapport rangés comme les indicateurs du tableau de
        bord : « À venir » du tableau de bord = activités à venir dont
        l'échéance tombe dans sa fenêtre. """
        upcoming_end = self.today + timedelta(days=data['upcoming_days'])
        upcoming = self.report(user).search_count(self.team_domain() + (domain or []) + [
            ('state', '=', 'planned'), ('date_deadline', '<=', upcoming_end)])
        report = {
            'overdue': counts.get('overdue', 0),
            'today': counts.get('today', 0),
            'upcoming': upcoming,
            'done': counts.get('done', 0),
            'open': counts.get('overdue', 0) + counts.get('today', 0) + counts.get('planned', 0),
        }
        dashboard = {key: data['kpis'][key] for key in report}
        return report, dashboard

    # R1 : mêmes nombres que le tableau de bord ----------------------------

    def test_counts_match_dashboard_for_manager(self):
        counts = self.counts_by_state(self.manager)
        self.assertEqual(counts, {'overdue': 1, 'today': 1, 'planned': 5, 'done': 2})
        report, dashboard = self.report_vs_dashboard(self.dashboard(self.manager), counts, self.manager)
        self.assertEqual(report, {'overdue': 1, 'today': 1, 'upcoming': 4, 'done': 2, 'open': 7})
        self.assertEqual(report, dashboard)

    def test_counts_match_dashboard_per_salesperson(self):
        for user, expected in (
            (self.alice, {'overdue': 1, 'today': 1, 'upcoming': 1, 'done': 1, 'open': 4}),
            (self.bob, {'overdue': 0, 'today': 0, 'upcoming': 3, 'done': 1, 'open': 3}),
        ):
            with self.subTest(user=user.name):
                domain = [('user_id', '=', user.id)]
                counts = self.counts_by_state(self.manager, domain)
                data = self.dashboard(self.manager, user_id=user.id)
                report, dashboard = self.report_vs_dashboard(data, counts, self.manager, domain)
                self.assertEqual(report, expected)
                self.assertEqual(report, dashboard)

    def test_counts_match_dashboard_for_salesman(self):
        """ Sans filtre de commercial, Alice voit dans le tableau de bord ce
        que les droits d'Odoo lui montrent : le rapport donne les mêmes
        nombres. """
        counts = self.counts_by_state(self.alice)
        self.assertEqual(counts, {'overdue': 1, 'today': 1, 'planned': 4, 'done': 1})
        report, dashboard = self.report_vs_dashboard(
            self.dashboard(self.alice, user_id=False), counts, self.alice)
        self.assertEqual(report, {'overdue': 1, 'today': 1, 'upcoming': 3, 'done': 1, 'open': 6})
        self.assertEqual(report, dashboard)

    def test_activity_marked_done_moves_to_done_at_once(self):
        """ Les champs lus par la requête sont écrits en base avant chaque
        lecture : une activité tout juste faite est déjà « réalisée ». """
        self.act_today.action_feedback(feedback="Devis envoyé")
        row = self.rows(self.manager)[self.act_today.id]
        self.assertEqual(row.state, 'done')
        self.assertEqual(row.date_done, self.today)
        self.assertEqual(row.done_on_time, 100)
        counts = self.counts_by_state(self.manager)
        self.assertEqual(counts, {'overdue': 1, 'planned': 5, 'done': 3})
        report, dashboard = self.report_vs_dashboard(self.dashboard(self.manager), counts, self.manager)
        self.assertEqual(report, dashboard)

    # R2 : droits par profil --------------------------------------------

    def test_salesman_sees_own_rows_and_rows_of_own_leads(self):
        alice_rows = set(self.rows(self.alice))
        self.assertEqual(alice_rows, {
            self.act_overdue.id, self.act_today.id, self.act_far.id,  # ses activités, son opportunité
            self.act_done_late.id,                                    # réalisée, son opportunité
            self.act_on_bob_for_alice.id,   # assignée à elle sur l'opportunité de Bob
            self.act_bob_on_alice.id,       # de Bob, sur son opportunité
            self.act_free.id,               # opportunité sans commercial
        })
        self.assertNotIn(self.act_bob.id, alice_rows, "L'activité de Bob sur son opportunité reste privée")
        self.assertNotIn(self.act_done_on_time.id, alice_rows)

        bob_rows = set(self.rows(self.bob))
        self.assertEqual(bob_rows, {
            self.act_bob.id, self.act_done_on_time.id, self.act_on_bob_for_alice.id,
            self.act_bob_on_alice.id, self.act_free.id,
        })

    def test_salesman_rows_are_the_activities_odoo_shows_him(self):
        """ La règle du rapport reproduit l'accès de mail.activity : ses
        activités + celles des opportunités qu'il peut lire. """
        lead_ids = self.env['crm.lead'].with_context(active_test=False).search(self.team_domain()).ids
        for user in (self.alice, self.bob):
            with self.subTest(user=user.name):
                activities = self.env['mail.activity'].with_user(user).with_context(
                    active_test=False).search([('res_model', '=', 'crm.lead'), ('res_id', 'in', lead_ids)])
                self.assertEqual(set(self.rows(user)), set(activities.ids))

    def test_all_documents_profiles_see_everything(self):
        all_leads = new_test_user(
            self.env, login='aite_cad_all_leads', groups='sales_team.group_sale_salesman_all_leads',
            name="Commercial tous documents", tz='UTC')
        expected = {
            self.act_overdue.id, self.act_today.id, self.act_far.id, self.act_bob.id,
            self.act_on_bob_for_alice.id, self.act_bob_on_alice.id, self.act_free.id,
            self.act_done_late.id, self.act_done_on_time.id,
        }
        for user in (self.manager, all_leads):
            with self.subTest(user=user.name):
                self.assertEqual(set(self.rows(user)), expected)

    def test_unassigned_activity_on_own_lead_is_visible(self):
        unassigned = self.env['mail.activity'].create({
            'res_model_id': self.env['ir.model']._get_id('crm.lead'),
            'res_id': self.lead_alice.id, 'user_id': False,
            'activity_type_id': self.type_todo.id, 'date_deadline': self.today - timedelta(days=1),
        })
        self.assertIn(unassigned.id, self.rows(self.alice))
        self.assertNotIn(unassigned.id, self.rows(self.bob))
        row = self.rows(self.manager)[unassigned.id]
        # Sans personne assignée : jour UTC.
        self.assertEqual((row.state, row.days_late, row.user_id.id), ('overdue', 1, False))

    def test_non_crm_user_has_no_access(self):
        accountant = new_test_user(self.env, login='aite_cad_report_none', groups='base.group_user')
        with self.assertRaises(AccessError):
            self.report(accountant).search([])

    def test_report_is_read_only(self):
        row = self.rows(self.manager)[self.act_overdue.id]
        with self.assertRaises(AccessError):
            row.with_user(self.manager).write({'summary': "Modifié"})
        with self.assertRaises(AccessError):
            row.with_user(self.manager).unlink()

    # R3 : multi-société ------------------------------------------------

    def test_multi_company_rule(self):
        company2 = self.env['res.company'].create({'name': "Filiale AITE Test"})
        lead2 = self.env['crm.lead'].sudo().create({
            'name': "Opportunité filiale", 'type': 'opportunity', 'user_id': False,
            'team_id': False, 'company_id': company2.id,
        })
        self.assertEqual(lead2.company_id, company2)
        act2 = self._activity(lead2, self.alice, -1, self.type_call, "Appel filiale")
        domain = [('activity_id', '=', act2.id)]

        self.assertEqual(self.report(self.manager).search_count(domain), 0,
                         "Le responsable de la société principale ne voit pas la filiale")
        self.assertEqual(self.report(self.alice).search_count(domain), 0,
                         "Même assignée à Alice, l'activité d'une autre société reste hors du rapport")
        self.assertEqual(self.report().sudo().search_count(domain), 1)

        self.manager.write({'company_ids': [(4, company2.id)]})
        main = self.env.company
        both = self.report(self.manager).with_context(allowed_company_ids=[main.id, company2.id])
        self.assertEqual(both.search_count(domain), 1)
        only_main = self.report(self.manager).with_context(allowed_company_ids=[main.id])
        self.assertEqual(only_main.search_count(domain), 0, "Société non cochée : ligne masquée")
        row = both.search(domain)
        self.assertEqual((row.company_id, row.state, row.lead_user_id.id), (company2, 'overdue', False))

    # R4 : état, retard, gravité ----------------------------------------

    def test_state_days_late_and_severity(self):
        late = {
            days: self._activity(self.lead_alice, self.alice, -days, self.type_call, f"Retard {days} j")
            for days in (1, 2, 3, 6, 7, 10)
        }
        rows = self.rows(self.manager)
        thresholds = get_thresholds(self.env)
        self.assertEqual((thresholds['high_days'], thresholds['critical_days']), (3, 7))
        expected = {1: 'low', 2: 'low', 3: 'high', 6: 'high', 7: 'critical', 10: 'critical'}
        for days, activity in late.items():
            with self.subTest(days=days):
                row = rows[activity.id]
                self.assertEqual(
                    (row.state, row.days_late, row.is_overdue, row.severity),
                    ('overdue', days, 1, expected[days]))
                # Même gravité que celle du tableau de bord et du récapitulatif.
                self.assertEqual(row.severity, crm_activity_params.severity(days, thresholds))
        for activity, state in ((self.act_today, 'today'), (self.act_far, 'planned'), (self.act_bob, 'planned')):
            with self.subTest(state=state, activity=activity.summary):
                row = rows[activity.id]
                self.assertEqual((row.state, row.days_late, row.is_overdue, row.severity),
                                 (state, 0, 0, False))
        self.assertEqual(rows[self.act_overdue.id].days_late, 2)
        self.assertEqual(rows[self.act_overdue.id].severity, 'low')
        self.assertEqual(rows[self.act_far.id].date_deadline, self.today + timedelta(days=30))

        # Mesures du tableau croisé (overdue : 6 nouvelles + act_overdue).
        [(overdue, late_days_sum, count)] = self.report(self.manager)._read_group(
            self.team_domain() + [('state', '=', 'overdue')], [],
            ['is_overdue:sum', 'days_late:sum', '__count'])
        self.assertEqual((overdue, late_days_sum, count), (7, 1 + 2 + 3 + 6 + 7 + 10 + 2, 7))
        severities = dict(self.report(self.manager)._read_group(
            self.team_domain() + [('severity', '!=', False)], ['severity'], ['__count']))
        self.assertEqual(severities, {'low': 3, 'high': 2, 'critical': 2})

    def test_thresholds_are_read_at_query_time(self):
        late = {
            days: self._activity(self.lead_alice, self.alice, -days, self.type_call, f"Retard {days} j")
            for days in (1, 3, 6)
        }
        rows = self.rows(self.manager)
        self.assertEqual([rows[late[d].id].severity for d in (1, 3, 6)], ['low', 'high', 'high'])

        params = self.env['ir.config_parameter'].sudo()
        params.set_param(PARAM_HIGH_DAYS, '2')
        params.set_param(PARAM_CRITICAL_DAYS, '5')
        self.env.invalidate_all()
        rows = self.rows(self.manager)
        self.assertEqual([rows[late[d].id].severity for d in (1, 3, 6)], ['low', 'high', 'critical'])

        # Seuils incohérents (élevé ≥ critique) : valeurs par défaut (3 et 7).
        params.set_param(PARAM_HIGH_DAYS, '9')
        self.env.invalidate_all()
        rows = self.rows(self.manager)
        self.assertEqual([rows[late[d].id].severity for d in (1, 3, 6)], ['low', 'high', 'high'])

    def test_today_follows_the_assignee_timezone(self):
        """ À 23 h 30 UTC, il est déjà 0 h 30 le lendemain à Douala : une
        activité du jour (UTC) y est déjà en retard d'un jour, comme dans
        l'état natif des activités d'Odoo. """
        charlie = new_test_user(
            self.env, login='aite_cad_charlie', groups='sales_team.group_sale_salesman',
            name="Charlie Douala", tz='Africa/Douala')
        late_evening = datetime.combine(self.today, time(23, 30))
        model_id = self.env['ir.model']._get_id('crm.lead')

        def create(user, days, summary):
            return self.env['mail.activity'].create({
                'res_model_id': model_id, 'res_id': self.lead_alice.id, 'user_id': user.id,
                'activity_type_id': self.type_todo.id, 'summary': summary,
                'date_deadline': self.today + timedelta(days=days),
            })

        douala_today = create(charlie, 0, "Douala J")
        douala_tomorrow = create(charlie, 1, "Douala J+1")
        utc_today = create(self.alice, 0, "UTC J")
        # Odoo ignore une date de création fournie à create() : posée en SQL.
        self.env.flush_all()
        self.env.cr.execute(SQL(
            "UPDATE mail_activity SET create_date = %s WHERE id IN %s",
            late_evening, (douala_today | douala_tomorrow | utc_today)._ids))
        with freeze_time(late_evening):
            self.env.invalidate_all()
            rows = self.rows(self.manager)
            for activity, state, days_late in (
                (douala_today, 'overdue', 1),
                (douala_tomorrow, 'today', 0),
                (utc_today, 'today', 0),
            ):
                with self.subTest(activity=activity.summary):
                    row = rows[activity.id]
                    self.assertEqual((row.state, row.days_late), (state, days_late))
                    self.assertEqual(row.state, activity.state, "Même état que celui d'Odoo")
        # Créées à 23 h 30 UTC : le lendemain à Douala.
        self.assertEqual(rows[douala_today.id].create_date, self.today + timedelta(days=1))
        self.assertEqual(rows[utc_today.id].create_date, self.today)

    # R5 : réalisées à temps --------------------------------------------

    def test_done_rows(self):
        rows = self.rows(self.manager)
        late, on_time = rows[self.act_done_late.id], rows[self.act_done_on_time.id]
        self.assertEqual(
            (late.state, late.date_done, late.days_late, late.done_on_time, late.is_overdue, late.severity),
            ('done', self.today, 5, 0, 0, False))
        self.assertEqual(
            (on_time.state, on_time.date_done, on_time.days_late, on_time.done_on_time, on_time.is_overdue),
            ('done', self.today, 0, 100, 0))

    def test_on_time_rate_ignores_open_activities(self):
        """ Moyenne de done_on_time = taux de réalisation à temps : les
        activités en cours (vides) n'entrent pas dans la moyenne. """
        Report = self.report(self.manager)
        [(rate, count)] = Report._read_group(self.team_domain(), [], ['done_on_time:avg', '__count'])
        self.assertEqual((rate, count), (50.0, 9))
        # Faite le jour même de l'échéance : à temps.
        self.act_today.action_feedback()
        [(rate,)] = Report._read_group(self.team_domain(), [], ['done_on_time:avg'])
        self.assertAlmostEqual(float(rate), 200 / 3)
        by_user = dict(Report._read_group(
            self.team_domain() + [('state', '=', 'done')], ['user_id'], ['done_on_time:avg']))
        self.assertEqual(by_user, {self.alice: 50.0, self.bob: 100.0})

    # R6 : opportunités perdues -----------------------------------------

    def test_open_activities_of_lost_leads_leave_the_report(self):
        self.lead_alice.action_set_lost()
        self.assertFalse(self.lead_alice.active)
        rows = self.rows(self.manager)
        for activity in (self.act_overdue, self.act_today, self.act_far, self.act_bob_on_alice):
            self.assertNotIn(activity.id, rows, f"{activity.summary} : opportunité perdue, plus à faire")
        done = rows[self.act_done_late.id]
        self.assertEqual((done.state, done.lead_active, done.won_status), ('done', False, 'lost'))
        self.assertEqual(self.counts_by_state(self.manager), {'planned': 3, 'done': 2})

        # Même règle que actionable_activity_domain (tableau de bord, récapitulatif).
        lead_ids = self.env['crm.lead'].with_context(active_test=False).search(self.team_domain()).ids
        open_activities = self.env['mail.activity'].search(
            [('res_model', '=', 'crm.lead'), ('res_id', 'in', lead_ids)]
            + actionable_activity_domain(self.env))
        open_rows = self.rows(self.manager, [('state', '!=', 'done')])
        self.assertEqual(set(open_rows), set(open_activities.ids))

        # Opportunité restaurée : ses activités reviennent.
        self.lead_alice.action_unarchive()
        self.assertEqual(self.counts_by_state(self.manager), {'overdue': 1, 'today': 1, 'planned': 5, 'done': 2})

    # Dimensions --------------------------------------------------------

    def test_lead_dimensions(self):
        rows = self.rows(self.manager)
        row = rows[self.act_overdue.id]
        self.assertEqual(
            (row.lead_id, row.lead_user_id, row.user_id, row.team_id, row.partner_id,
             row.stage_id, row.company_id, row.activity_type_id, row.summary),
            (self.lead_alice, self.alice, self.alice, self.team, self.partner,
             self.lead_alice.stage_id, self.lead_alice.company_id, self.type_call, "Rappeler le client"))
        self.assertEqual((row.lead_type, row.won_status, row.lead_active, row.nbr), ('opportunity', 'pending', True, 1))
        self.assertEqual(row.create_date, self.today)
        self.assertEqual(row.display_name, "Rappeler le client")
        free = rows[self.act_free.id]
        self.assertEqual((free.lead_id, free.lead_user_id.id, free.user_id), (self.lead_free, False, self.bob))
        self.assertNotIn('expected_revenue', self.env[REPORT]._fields,
                         "Pas de montant par activité : une opportunité serait comptée plusieurs fois")

    def test_action_open_lead(self):
        row = self.rows(self.alice)[self.act_overdue.id]
        action = row.action_open_lead()
        self.assertEqual(
            (action['res_model'], action['res_id'], action['views'], action['type']),
            ('crm.lead', self.lead_alice.id, [(False, 'form')], 'ir.actions.act_window'))
        row = self.rows(self.alice)[self.act_on_bob_for_alice.id]
        with self.assertRaises(AccessError):
            row.action_open_lead()

    # R8 : opportunité d'un collègue -----------------------------------

    def test_colleague_lead_details_stay_hidden(self):
        """ Activité assignée à Alice sur l'opportunité de Bob, qu'elle ne
        peut pas ouvrir : la ligne reste dans son rapport avec le nom de
        l'opportunité (ce que lui montre Odoo), mais rien d'autre sur elle,
        même une fois l'activité faite et l'opportunité perdue. """
        secret = self.env['res.partner'].create({'name': "Client confidentiel"})
        self.lead_bob.partner_id = secret
        self.assertFalse(self.lead_bob.with_user(self.alice)._filtered_access('read'))
        domain = [('activity_id', '=', self.act_on_bob_for_alice.id)]
        hidden = ['lead_active', 'lead_type', 'lead_user_id', 'partner_id', 'stage_id', 'won_status']

        # Lu d'abord en sudo et par le responsable (qui voient tout), dans la
        # même transaction : le cache ne doit rien en passer à Alice.
        raw = self.report().sudo().search(domain)
        self.assertEqual((raw.partner_id, raw.lead_user_id, raw.won_status), (secret, self.bob, 'pending'))
        manager_row = self.report(self.manager).search(domain)
        self.assertEqual((manager_row.partner_id, manager_row.stage_id), (secret, self.lead_bob.stage_id))

        Report = self.report(self.alice)
        row = Report.search(domain)
        self.assertEqual((row.lead_id, row.user_id, row.team_id, row.state),
                         (self.lead_bob, self.alice, self.team, 'planned'))
        [values] = row.read(hidden)
        self.assertEqual({fname: values[fname] for fname in hidden}, dict.fromkeys(hidden, False))

        # Ni en regroupement, ni en filtre.
        groups = Report.formatted_read_group([('user_id', '=', self.alice.id)], ['partner_id'], ['__count'])
        self.assertNotIn(secret.id, [group['partner_id'] and group['partner_id'][0] for group in groups])
        self.assertEqual(Report.search_count([('partner_id', '=', secret.id)]), 0)
        self.assertEqual(Report.search_count(domain + [('lead_user_id', '=', self.bob.id)]), 0)

        # Les lignes de Bob sur son opportunité restent invisibles pour Alice
        # (la règle d'accès lit toujours le vrai commercial).
        self.assertNotIn(self.act_bob.id, self.rows(self.alice))
        self.assertEqual(self.rows(self.bob)[self.act_on_bob_for_alice.id].partner_id, secret)

        # Activité faite, puis opportunité perdue : Alice ne l'apprend pas
        # par le rapport.
        self.act_on_bob_for_alice.action_feedback(feedback="Fait")
        self.lead_bob.action_set_lost()
        self.env.invalidate_all()
        row = Report.search(domain)
        self.assertEqual((row.state, row.won_status, row.partner_id.id), ('done', False, False))
        self.assertEqual(Report.search_count(self.team_domain() + [('won_status', '=', 'lost')]), 0)
        self.assertEqual(self.report(self.manager).search(domain).won_status, 'lost')

    def test_export_with_rows_on_a_colleague_lead(self):
        """ Liste → Exporter, pour Alice dont une ligne porte sur
        l'opportunité de Bob : l'export se fait, avec le nom de
        l'opportunité comme dans la liste et sans son client. Le détail de
        l'opportunité de Bob, lui, reste refusé. """
        # « Export : autorisé » (Paramètres → Utilisateurs), exigé par Odoo 19.
        (self.alice | self.manager).write({
            'group_ids': [Command.link(self.env.ref('base.group_allow_export').id)]})
        secret = self.env['res.partner'].create({'name': "Client confidentiel"})
        self.lead_bob.partner_id = secret
        rows = self.report(self.alice).search(self.team_domain())
        self.assertIn(self.act_on_bob_for_alice, rows.activity_id)

        for lead_path in ('lead_id', 'lead_id/display_name'):
            with self.subTest(path=lead_path):
                datas = rows.export_data(['summary', lead_path, 'partner_id', 'user_id'])['datas']
                by_summary = {line[0]: line[1:] for line in datas}
                self.assertEqual(len(datas), 7)
                self.assertEqual(by_summary["Aider Bob"], ["Opportunité Bob", '', "Alice Commerciale"])
                self.assertEqual(by_summary["Rappeler le client"],
                                 ["Opportunité Alice", "Client Test", "Alice Commerciale"])
                self.assertEqual(by_summary["Qualifier"], ["Opportunité sans commercial", '', "Bob Commercial"])
        # Import compatible (identifiants externes) : déjà permis par Odoo.
        rows.with_context(import_compat=True).export_data(['lead_id/id'])
        with self.assertRaises(AccessError):
            rows.export_data(['summary', 'lead_id/expected_revenue'])

        manager_rows = self.report(self.manager).search(self.team_domain())
        datas = manager_rows.export_data(['summary', 'lead_id', 'partner_id'])['datas']
        self.assertIn(["Aider Bob", "Opportunité Bob", "Client confidentiel"], datas)

    # R7 : vues, action, menu -------------------------------------------

    def test_action_and_menu(self):
        action = self.env.ref('aite_crm_activity.action_crm_activity_report')
        self.assertEqual(
            (action.res_model, action.path, action.view_mode, action.search_view_id),
            (REPORT, 'analyse-activites', 'pivot,graph,list',
             self.env.ref('aite_crm_activity.crm_activity_report_view_search')))
        context = safe_eval(action.context)
        self.assertEqual(context, {
            'pivot_measures': ['nbr'],
            'pivot_row_groupby': ['user_id'],
            'pivot_column_groupby': ['state'],
            'graph_mode': 'bar',
            'graph_measure': 'nbr',
            'graph_groupbys': ['date_deadline:week', 'state'],
        })
        self.assertNotIn('group_by', context)
        self.assertIn("opportunités perdues", action.help)

        menu = self.env.ref('aite_crm_activity.menu_crm_activity_report')
        self.assertEqual(
            (menu.name, menu.parent_id, menu.sequence, menu.action, menu.group_ids),
            ("Suivi des activités (analyse)", self.env.ref('crm.crm_menu_report'), 5, action,
             self.env.ref('sales_team.group_sale_salesman')))
        self.assertIn(menu, self.env['ir.ui.menu'].with_user(self.alice).search([('id', '=', menu.id)]))

        # /odoo/analyse-activites : le client web retrouve l'action par son
        # chemin (/web/action/load), puis la charge.
        found = self.env['ir.actions.actions'].sudo().search([('path', '=', 'analyse-activites')])
        self.assertEqual(found.id, action.id)
        loaded = self.env['ir.actions.act_window'].sudo().browse(found.id)._get_action_dict()
        self.assertEqual(
            (loaded['res_model'], loaded['path'], loaded['view_mode'], safe_eval(loaded['context'])),
            (REPORT, 'analyse-activites', 'pivot,graph,list', context))

    def test_views_load_for_salesman(self):
        views = self.env[REPORT].with_user(self.alice).get_views(
            [(False, 'pivot'), (False, 'graph'), (False, 'list'), (False, 'search')])['views']
        for view_type, xmlid in (
            ('pivot', 'crm_activity_report_view_pivot'),
            ('graph', 'crm_activity_report_view_graph'),
            ('list', 'crm_activity_report_view_list'),
            ('search', 'crm_activity_report_view_search'),
        ):
            with self.subTest(view_type=view_type):
                self.assertEqual(views[view_type]['id'], self.env.ref(f'aite_crm_activity.{xmlid}').id)
        pivot = etree.fromstring(views['pivot']['arch'])
        self.assertEqual(
            [(f.get('name'), f.get('type')) for f in pivot.iter('field')],
            [('user_id', 'row'), ('state', 'col'), ('nbr', 'measure')])
        graph = etree.fromstring(views['graph']['arch'])
        self.assertEqual((graph.get('type'), graph.get('stacked')), ('bar', '1'))
        self.assertEqual(
            [(f.get('name'), f.get('interval')) for f in graph.iter('field')],
            [('date_deadline', 'week'), ('state', None), ('nbr', None)])
        listing = etree.fromstring(views['list']['arch'])
        self.assertEqual((listing.get('create'), listing.get('edit'), listing.get('delete')), ('0', '0', '0'))

    def test_search_filters(self):
        """ Chaque filtre du panneau de recherche, évalué comme le fait le
        client web (dates relatives d'Odoo 19 comprises), pour Alice. """
        act_critical = self._activity(self.lead_alice, self.alice, -8, self.type_call, "Très en retard")
        arch = etree.fromstring(self.env.ref('aite_crm_activity.crm_activity_report_view_search').arch)
        filters = {f.get('name'): f.get('domain') for f in arch.iter('filter') if f.get('domain')}
        expected = {
            'overdue': 2, 'today': 1, 'planned': 4, 'done': 1,
            'my_activities': 6, 'my_leads': 6,
            'late_high': 1, 'late_critical': 1,
            'done_this_month': 1,
            # « Aider Bob » (opportunité de Bob) : Alice n'en voit ni le type
            # ni l'issue (R8).
            'lead': 0, 'opportunity': 7,
            'pending': 7, 'won': 0, 'lost': 0,
        }
        self.assertEqual(set(filters), set(expected))
        Report = self.report(self.alice)
        for name, domain in filters.items():
            with self.subTest(filter=name):
                domain = safe_eval(domain, {'uid': self.alice.id})
                self.assertEqual(Report.search_count(self.team_domain() + domain), expected[name])
        critical = Report.search(self.team_domain() + safe_eval(filters['late_critical']))
        self.assertEqual(critical.activity_id, act_critical)

        # « Réalisées ce mois-ci » : une activité faite le mois dernier n'y est plus.
        self.act_done_late.write({'date_done': self.today.replace(day=1) - timedelta(days=1)})
        this_month = self.team_domain() + safe_eval(filters['done_this_month'])
        self.assertEqual(Report.search_count(this_month), 0)
        self.assertEqual(Report.search_count(self.team_domain() + safe_eval(filters['done'])), 1)

    def test_pivot_graph_and_list_requests(self):
        """ Les appels faits par le tableau croisé (formatted_read_grouping_sets),
        le graphique (formatted_read_group) et la liste (web_search_read). """
        Report = self.report(self.manager)
        total, by_user, by_state = Report.formatted_read_grouping_sets(
            self.team_domain(), [[], ['user_id'], ['state']], ['nbr:sum'])
        self.assertEqual(total[0]['nbr:sum'], 9)
        self.assertEqual(
            {g['user_id'][0]: g['nbr:sum'] for g in by_user}, {self.alice.id: 5, self.bob.id: 4})
        self.assertEqual(
            {g['state']: g['nbr:sum'] for g in by_state},
            {'overdue': 1, 'today': 1, 'planned': 5, 'done': 2})

        # Liste regroupée (web_read_group), par exemple par gravité du retard.
        grouped = Report.web_read_group(self.team_domain(), ['severity'], ['nbr:sum'])
        self.assertEqual(grouped['length'], 2)
        self.assertEqual({g['severity']: g['nbr:sum'] for g in grouped['groups']}, {'low': 1, False: 8})

        groups = Report.formatted_read_group(self.team_domain(), ['date_deadline:week', 'state'], ['nbr:sum'])
        self.assertEqual(sum(g['nbr:sum'] for g in groups), 9)
        overdue_week = [g for g in groups if g['state'] == 'overdue']
        self.assertEqual([g['nbr:sum'] for g in overdue_week], [1])

        # Alice : le nom de l'opportunité de Bob s'affiche sans erreur de
        # droits, en regroupement comme dans la liste.
        by_lead = self.report(self.alice).formatted_read_group(
            self.team_domain(), ['lead_id'], ['nbr:sum'])
        self.assertEqual(
            {g['lead_id'][1]: g['nbr:sum'] for g in by_lead},
            {"Opportunité Alice": 5, "Opportunité Bob": 1, "Opportunité sans commercial": 1})
        result = self.report(self.alice).web_search_read(self.team_domain(), {
            'activity_id': {}, 'state': {}, 'severity': {}, 'days_late': {},
            'lead_id': {'fields': {'display_name': {}}},
            'user_id': {'fields': {'display_name': {}}},
        })
        self.assertEqual(result['length'], 7)
        by_activity = {r['activity_id']: r for r in result['records']}
        self.assertEqual(by_activity[self.act_on_bob_for_alice.id]['lead_id']['display_name'], "Opportunité Bob")
        self.assertEqual(by_activity[self.act_overdue.id]['severity'], 'low')
        # Ordre par défaut : échéance la plus lointaine d'abord.
        self.assertEqual(result['records'][0]['activity_id'], self.act_far.id)
