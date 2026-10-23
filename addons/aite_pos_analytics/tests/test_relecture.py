# -*- coding: utf-8 -*-
"""Relecture croisée de l'intégration : cloisonnement par société.

La vue SQL ``aite.pos.daily.report`` n'avait aucune règle
d'enregistrement et le moteur Ventes ne filtrait pas la société : le
cockpit et l'analyse des ventes additionnaient les tickets de TOUTES les
sociétés de la base, quand l'activité par pôle de la Direction ne prenait
que la société courante (cas K04).
"""
from odoo import fields
from odoo.tests import tagged

from .common import PosAnalyticsCommon


@tagged('post_install', '-at_install', 'aite_analytics')
class TestPosAnalyticsRelecture(PosAnalyticsCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.dashboard = cls.env['aite.pos.dashboard']
        cls.other = cls.env['res.company'].create({
            'name': "Autre société (relecture)",
            'currency_id': cls.company.currency_id.id,
        })
        cls.analyst = cls.env['res.users'].create({
            'name': "Analyste mono-société",
            'login': 'analyste.mono.societe',
            'company_id': cls.company.id,
            'company_ids': [(6, 0, cls.company.ids)],
            'groups_id': [(6, 0, [
                cls.env.ref('base.group_user').id,
                cls.env.ref(
                    'aite_pos_analytics.group_aite_pos_analytics_user').id,
            ])],
        })

    def _move_to_other_company(self, order):
        """Le ticket passe dans l'autre société (la vue SQL relit
        ``pos_order.company_id``)."""
        self.env.cr.execute(
            "UPDATE pos_order SET company_id = %s WHERE id = %s",
            (self.other.id, order.id))
        self.env.invalidate_all()

    def test_dashboard_counts_the_current_company_only(self):
        day = fields.Date.to_string(self.today)
        order = self._sale([(self.beer, 2, 5000.0)])
        before = self.dashboard.get_kpis(day, day)
        self._move_to_other_company(order)
        after = self.dashboard.get_kpis(day, day)
        self.assertAlmostEqual(before['ca'] - after['ca'], 10000.0, places=2)
        self.assertEqual(before['order_count'] - after['order_count'], 1)

    def test_report_rows_of_another_company_are_hidden(self):
        order = self._sale([(self.beer, 2, 5000.0)])
        self._move_to_other_company(order)
        Report = self.env['aite.pos.daily.report'].with_user(self.analyst)
        self.assertFalse(Report.search([('order_id', '=', order.id)]))
