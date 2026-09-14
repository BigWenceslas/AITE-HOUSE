# -*- coding: utf-8 -*-
"""Coût, marge et agrégats de session — le cœur chiffré du module."""
from odoo.tests import tagged

from .common import PosAnalyticsCommon


@tagged('post_install', '-at_install', 'aite_analytics')
class TestPosMargins(PosAnalyticsCommon):

    # ------------------------------------------------------------------
    # Coût figé à la vente
    # ------------------------------------------------------------------

    def test_cost_is_snapped_at_sale_time(self):
        order = self._sale([(self.beer, 2, 5000.0)])
        line = order.lines
        self.assertEqual(line.cost_unit, 2000.0)
        self.assertEqual(line.total_cost, 4000.0)

    def test_later_cost_change_does_not_rewrite_history(self):
        """La marge historique reste stable si le coût d'achat évolue."""
        order = self._sale([(self.beer, 2, 5000.0)])
        self.beer.standard_price = 3500.0
        order.lines.invalidate_recordset()
        self.assertEqual(order.lines.cost_unit, 2000.0)
        self.assertEqual(order.lines.margin, 6000.0)

    def test_manual_cost_override(self):
        order = self._sale([(self.beer, 1, 5000.0)])
        order.lines.cost_unit = 1000.0
        self.assertEqual(order.lines.total_cost, 1000.0)
        self.assertEqual(order.lines.margin, 4000.0)

    # ------------------------------------------------------------------
    # Marge de ligne
    # ------------------------------------------------------------------

    def test_line_margin_and_rate(self):
        order = self._sale([(self.beer, 2, 5000.0)])
        line = order.lines
        # CA 10 000 − CMV 4 000 = 6 000, soit 60 %
        self.assertEqual(line.margin, 6000.0)
        self.assertAlmostEqual(line.margin_rate, 60.0, places=2)

    def test_zero_price_line_has_no_rate(self):
        order = self._sale([(self.beer, 1, 0.0)])
        self.assertEqual(order.lines.margin_rate, 0.0)

    def test_negative_margin_on_a_loss_sale(self):
        order = self._sale([(self.beer, 1, 1000.0)])
        self.assertEqual(order.lines.margin, -1000.0)
        self.assertAlmostEqual(order.lines.margin_rate, -100.0, places=2)

    # ------------------------------------------------------------------
    # Agrégats de commande
    # ------------------------------------------------------------------

    def test_order_aggregates_sum_its_lines(self):
        order = self._sale([
            (self.beer, 2, 5000.0),    # CA 10 000, CMV 4 000
            (self.dish, 1, 20000.0),   # CA 20 000, CMV 12 000
        ])
        self.assertEqual(order.total_cost, 16000.0)
        self.assertEqual(order.total_margin, 14000.0)
        # 14 000 / 30 000
        self.assertAlmostEqual(order.margin_rate, 46.67, places=2)

    # ------------------------------------------------------------------
    # Agrégats de session
    # ------------------------------------------------------------------

    def test_session_aggregates(self):
        self._sale([(self.beer, 2, 5000.0)])
        self._sale([(self.dish, 1, 20000.0)])
        self.session.invalidate_recordset()
        self.assertEqual(self.session.total_ca, 30000.0)
        self.assertEqual(self.session.total_cost, 16000.0)
        self.assertEqual(self.session.total_margin, 14000.0)
        self.assertEqual(self.session.order_count_computed, 2)
        self.assertEqual(self.session.total_qty, 3.0)
        self.assertEqual(self.session.average_basket, 15000.0)

    def test_unpaid_orders_are_excluded(self):
        """Seules les commandes réglées alimentent les agrégats."""
        self._sale([(self.beer, 2, 5000.0)])
        self._draft_sale([(self.dish, 1, 20000.0)])
        self.session.invalidate_recordset()
        self.assertEqual(self.session.total_ca, 10000.0)
        self.assertEqual(self.session.order_count_computed, 1)

    def test_empty_session_has_no_basket(self):
        # Un journal de caisse ne peut servir qu'à un seul moyen « espèces ».
        other_journal = self.env['account.journal'].create({
            'name': "Caisse vide (test)",
            'type': 'cash',
            'code': 'CVT',
            'company_id': self.company.id,
        })
        other_method = self.env['pos.payment.method'].create({
            'name': "Espèces Caisse vide",
            'journal_id': other_journal.id,
            'company_id': self.company.id,
        })
        empty_config = self.env['pos.config'].create({
            'name': "Caisse vide",
            'payment_method_ids': [(6, 0, other_method.ids)],
        })
        empty_config.open_ui()
        session = empty_config.current_session_id
        self.assertEqual(session.total_ca, 0.0)
        self.assertEqual(session.average_basket, 0.0)
        self.assertEqual(session.margin_rate, 0.0)

    # ------------------------------------------------------------------
    # Écart de caisse
    # ------------------------------------------------------------------

    def test_no_discrepancy(self):
        self.session.cash_register_difference = 0.0
        self.session.invalidate_recordset(['cash_discrepancy_severity'])
        self.assertEqual(self.session.cash_discrepancy_severity, 'none')

    def test_surplus_is_flagged_apart(self):
        self.session.cash_register_difference = 5000.0
        self.session.invalidate_recordset(['cash_discrepancy_severity'])
        self.assertEqual(self.session.cash_discrepancy_severity, 'over')

    def test_shortfall_severity_scale(self):
        Session = self.env['pos.session']
        cases = [
            (-1.0, 'low'),
            (-(Session.DISCREPANCY_THRESHOLD_MED), 'med'),
            (-(Session.DISCREPANCY_THRESHOLD_HIGH), 'high'),
            (-(Session.DISCREPANCY_THRESHOLD_HIGH + 1000.0), 'high'),
        ]
        for difference, expected in cases:
            self.session.cash_register_difference = difference
            self.session.invalidate_recordset(['cash_discrepancy_severity'])
            self.assertEqual(
                self.session.cash_discrepancy_severity, expected,
                "écart %s attendu %s" % (difference, expected))

    def test_thresholds_are_ordered(self):
        Session = self.env['pos.session']
        self.assertLess(Session.DISCREPANCY_THRESHOLD_MED,
                        Session.DISCREPANCY_THRESHOLD_HIGH)
