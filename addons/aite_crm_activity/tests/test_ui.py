# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import fields
from odoo.tests import HttpCase, new_test_user, tagged


@tagged('post_install', '-at_install', 'aite_crm_activity')
class TestCrmActivityDashboardUi(HttpCase):
    """ Le tableau de bord dans un vrai navigateur (tours JS de
    static/tests/tours/crm_activity_dashboard_tour.js). """

    def _clear_open_activities(self, env):
        """ La liste du tableau de bord s'arrête aux 80 premières activités
        (les plus anciennes d'abord) : sur une base qui en a déjà beaucoup
        (données de démonstration, copie d'une base réelle), celles du
        parcours n'y figureraient pas. Les autres activités ouvertes sont
        donc supprimées le temps du test (tout est annulé à la fin). """
        env['mail.activity'].search([('res_model', '=', 'crm.lead')]).unlink()

    def _activity(self, env, lead, user, days, summary):
        today = fields.Date.context_today(user.with_context(tz='UTC'))
        return env['mail.activity'].create({
            'res_model_id': env['ir.model']._get_id('crm.lead'),
            'res_id': lead.id,
            'user_id': user.id,
            'activity_type_id': env.ref('mail.mail_activity_data_todo').id,
            'summary': summary,
            'date_deadline': today + timedelta(days=days),
        })

    def test_dashboard_tour(self):
        """ Actions directes, aperçu, période, onglets Équipe et Tendances. """
        admin = self.env.ref('base.user_admin')
        admin.tz = 'UTC'
        colleague = new_test_user(
            self.env, login='aite_cad_tour_colleague', groups='sales_team.group_sale_salesman',
            name="Collègue (tour)", tz='UTC')
        today = fields.Date.context_today(admin.with_context(tz='UTC'))
        env = self.env(context=dict(self.env.context, mail_activity_quick_update=True))
        self._clear_open_activities(env)
        Lead = env['crm.lead']
        lead = Lead.create({'name': "Opportunité suivie (tour)", 'type': 'opportunity',
                            'user_id': admin.id})
        quiet_lead = Lead.create({'name': "Opportunité à relancer (tour)", 'type': 'opportunity',
                                  'user_id': admin.id, 'priority': '3',
                                  'expected_revenue': 10 ** 12})

        overdue = self._activity(env, lead, admin, -1, "Rappeler le client (tour)")
        today_activity = self._activity(env, lead, admin, 0, "Envoyer le devis (tour)")
        upcoming = self._activity(env, lead, admin, 2, "Préparer la réunion (tour)")

        self.start_tour('/odoo/suivi-activites', 'aite_crm_activity_dashboard_tour', login='admin')

        self.assertFalse(overdue.active, "Marquée comme faite depuis le tableau de bord")
        self.assertEqual(overdue.feedback, "Client rappelé, devis vendredi")
        self.assertEqual(today_activity.date_deadline, today + timedelta(days=1))
        self.assertEqual(upcoming.user_id, colleague, "Réassignée après confirmation")
        self.assertEqual(quiet_lead.activity_ids.mapped('summary'), ["Relancer le client - tour"])

    def test_overdue_link_tour(self):
        """ /odoo/activites-en-retard ouvre le tableau de bord sur « En retard »
        (paramètres de l'action aite_crm_activity.action_crm_activity_dashboard_overdue). """
        admin = self.env.ref('base.user_admin')
        admin.tz = 'UTC'
        env = self.env(context=dict(self.env.context, mail_activity_quick_update=True))
        self._clear_open_activities(env)
        lead = env['crm.lead'].create({'name': "Opportunité du lien (tour)", 'type': 'opportunity',
                                       'user_id': admin.id})
        self._activity(env, lead, admin, -3, "Relance en retard (tour)")
        self._activity(env, lead, admin, 0, "Appel du jour (tour)")

        self.start_tour('/odoo/activites-en-retard', 'aite_crm_activity_overdue_link_tour', login='admin')

    def test_panel_modal_tour(self):
        """ Aperçu plein écran : une fenêtre ou un menu ouvert depuis l'aperçu
        garde Échap et le focus quand la largeur change, et le focus revient
        à l'aperçu après une action refusée (activité supprimée ailleurs). """
        admin = self.env.ref('base.user_admin')
        admin.tz = 'UTC'
        today = fields.Date.context_today(admin.with_context(tz='UTC'))
        env = self.env(context=dict(self.env.context, mail_activity_quick_update=True))
        self._clear_open_activities(env)
        lead = env['crm.lead'].create({'name': "Opportunité de l'aperçu (tour)", 'type': 'opportunity',
                                       'user_id': admin.id})
        call = self._activity(env, lead, admin, -1, "Appeler (tour)")
        stale = self._activity(env, lead, admin, -2, "Relancer (tour)")

        self.start_tour('/odoo/activites-en-retard', 'aite_crm_activity_panel_modal_tour', login='admin')

        self.assertTrue(call.active, "Fenêtre « Fait » et menu fermés par Échap : rien n'est fait")
        self.assertEqual(call.date_deadline, today - timedelta(days=1))
        self.assertFalse(stale.exists(), "Supprimée pendant le parcours, report refusé")
