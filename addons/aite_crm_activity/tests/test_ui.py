# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import fields
from odoo.tests import HttpCase, tagged


@tagged('post_install', '-at_install', 'aite_crm_activity')
class TestCrmActivityDashboardUi(HttpCase):
    """ Le tableau de bord dans un vrai navigateur (tour JS). """

    def test_dashboard_tour(self):
        admin = self.env.ref('base.user_admin')
        admin.tz = 'UTC'
        today = fields.Date.context_today(admin.with_context(tz='UTC'))
        env = self.env(context=dict(self.env.context, mail_activity_quick_update=True))
        Lead = env['crm.lead']
        lead = Lead.create({'name': "Opportunité suivie (tour)", 'type': 'opportunity',
                            'user_id': admin.id})
        Lead.create({'name': "Opportunité à relancer (tour)", 'type': 'opportunity',
                     'user_id': admin.id, 'priority': '3', 'expected_revenue': 10 ** 12})

        def activity(days, summary):
            return env['mail.activity'].create({
                'res_model_id': env['ir.model']._get_id('crm.lead'),
                'res_id': lead.id,
                'user_id': admin.id,
                'activity_type_id': env.ref('mail.mail_activity_data_todo').id,
                'summary': summary,
                'date_deadline': today + timedelta(days=days),
            })

        overdue = activity(-1, "Rappeler le client (tour)")
        today_activity = activity(0, "Envoyer le devis (tour)")

        self.start_tour('/odoo/suivi-activites', 'aite_crm_activity_dashboard_tour', login='admin')

        self.assertFalse(overdue.active, "Marquée comme faite depuis le tableau de bord")
        self.assertEqual(overdue.feedback, "Client rappelé, devis vendredi")
        self.assertEqual(today_activity.date_deadline, today + timedelta(days=1))
