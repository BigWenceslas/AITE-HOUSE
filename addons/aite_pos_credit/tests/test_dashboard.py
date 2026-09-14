# -*- coding: utf-8 -*-
"""Tableau de bord du recouvrement : encours, balance âgée, KPI."""
from datetime import timedelta

from odoo import fields
from odoo.tests import tagged

from .common import CreditCommon


@tagged('post_install', '-at_install', 'aite_credit')
class TestCreditDashboard(CreditCommon):

    def setUp(self):
        super().setUp()
        # Société dédiée : le tableau de bord agrège tout l'encours de la
        # société courante. Sans cloisonnement, un jeu de démonstration
        # présent en base fausserait chaque total attendu.
        self.company = self.env['res.company'].create({
            'name': "Société Recouvrement (test)",
        })
        self.env.user.write({
            'company_ids': [(4, self.company.id)],
            'company_id': self.company.id,
        })
        self.env = self.env(context=dict(
            self.env.context, allowed_company_ids=[self.company.id]))
        self.client_a = self.client_a.with_env(self.env)
        self.client_b = self.client_b.with_env(self.env)
        self.Dashboard = self.env['aite.pos.credit.dashboard']
        self.today = fields.Date.context_today(self.env.user)
        self.d_from = fields.Date.to_string(self.today - timedelta(days=30))
        self.d_to = fields.Date.to_string(self.today)

    # ------------------------------------------------------------------
    # Balance âgée
    # ------------------------------------------------------------------

    def test_aging_has_four_buckets(self):
        buckets = self.Dashboard.get_aging()
        self.assertEqual([b['label'] for b in buckets],
                         ["0–30 j", "30–60 j", "60–90 j", "+90 j"])

    def test_aging_places_each_slate_in_its_bucket(self):
        self._credit(10000.0, days_ago=5)
        self._credit(20000.0, days_ago=40)
        self._credit(30000.0, days_ago=75)
        self._credit(40000.0, days_ago=200)
        buckets = {b['label']: b for b in self.Dashboard.get_aging()}
        self.assertEqual(buckets["0–30 j"]['amount'], 10000.0)
        self.assertEqual(buckets["30–60 j"]['amount'], 20000.0)
        self.assertEqual(buckets["60–90 j"]['amount'], 30000.0)
        self.assertEqual(buckets["+90 j"]['amount'], 40000.0)

    def test_aging_boundaries_are_left_inclusive(self):
        self._credit(10000.0, days_ago=30)
        buckets = {b['label']: b for b in self.Dashboard.get_aging()}
        self.assertEqual(buckets["0–30 j"]['amount'], 0.0)
        self.assertEqual(buckets["30–60 j"]['amount'], 10000.0)

    def test_aging_totals_match_outstanding(self):
        """Aucun montant ne doit se perdre entre les tranches."""
        self._credit(10000.0, days_ago=1)
        self._credit(20000.0, days_ago=45)
        self._credit(30000.0, days_ago=120)
        buckets = self.Dashboard.get_aging()
        kpis = self.Dashboard.get_kpis(self.d_from, self.d_to)
        self.assertEqual(sum(b['amount'] for b in buckets),
                         kpis['outstanding'])

    def test_aging_keeps_future_dated_slates(self):
        """Une ardoise mal datée (dans le futur) reste dans la balance.

        Sans borne basse ouverte, un âge négatif ne tombait dans aucune
        tranche et le montant disparaissait silencieusement du total.
        """
        self._credit(15000.0, days_ago=-3)
        buckets = self.Dashboard.get_aging()
        kpis = self.Dashboard.get_kpis(self.d_from, self.d_to)
        self.assertEqual(sum(b['amount'] for b in buckets),
                         kpis['outstanding'])
        self.assertEqual(sum(b['amount'] for b in buckets), 15000.0)

    def test_aging_excludes_settled_slates(self):
        credit = self._credit(10000.0, days_ago=10)
        self._repay(credit, 10000.0)
        buckets = self.Dashboard.get_aging()
        self.assertEqual(sum(b['amount'] for b in buckets), 0.0)

    # ------------------------------------------------------------------
    # KPI
    # ------------------------------------------------------------------

    def test_outstanding_and_debtor_count(self):
        self._credit(10000.0, partner=self.client_a)
        self._credit(20000.0, partner=self.client_a)
        self._credit(30000.0, partner=self.client_b)
        kpis = self.Dashboard.get_kpis(self.d_from, self.d_to)
        self.assertEqual(kpis['outstanding'], 60000.0)
        self.assertEqual(kpis['debtor_count'], 2)

    def test_late_amount_uses_the_threshold(self):
        self._credit(10000.0, days_ago=10)
        self._credit(25000.0, days_ago=45)
        kpis = self.Dashboard.get_kpis(self.d_from, self.d_to)
        self.assertEqual(kpis['late_amount'], 25000.0)

    def test_recovered_amount_of_the_period(self):
        credit = self._credit(50000.0, days_ago=10)
        self._repay(credit, 20000.0)
        kpis = self.Dashboard.get_kpis(self.d_from, self.d_to)
        self.assertEqual(kpis['recovered'], 20000.0)
        self.assertEqual(kpis['outstanding'], 30000.0)

    def test_average_slate_per_debtor(self):
        self._credit(40000.0, partner=self.client_a)
        self._credit(20000.0, partner=self.client_b)
        kpis = self.Dashboard.get_kpis(self.d_from, self.d_to)
        self.assertEqual(kpis['avg_ardoise'], 30000.0)

    def test_empty_dashboard_returns_zeros(self):
        kpis = self.Dashboard.get_kpis(self.d_from, self.d_to)
        self.assertEqual(kpis['outstanding'], 0.0)
        self.assertEqual(kpis['debtor_count'], 0)
        self.assertEqual(kpis['avg_ardoise'], 0.0)

    def test_oldest_slate_is_reported(self):
        self._credit(10000.0, days_ago=5, partner=self.client_a)
        self._credit(30000.0, days_ago=120, partner=self.client_b)
        kpis = self.Dashboard.get_kpis(self.d_from, self.d_to)
        self.assertEqual(kpis['oldest_partner'], "Client Ardoise B")
        self.assertEqual(kpis['oldest_age'], 120)
        self.assertEqual(kpis['oldest_amount'], 30000.0)

    # ------------------------------------------------------------------
    # Classements & répartitions
    # ------------------------------------------------------------------

    def test_top_debtors_is_sorted_desc(self):
        self._credit(10000.0, partner=self.client_a)
        self._credit(90000.0, partner=self.client_b)
        rows = self.Dashboard.get_top_debtors(limit=5)
        self.assertEqual(rows[0]['name'], "Client Ardoise B")
        self.assertEqual(rows[0]['outstanding'], 90000.0)
        self.assertEqual(rows[1]['name'], "Client Ardoise A")

    def test_top_debtors_carry_severity_and_contact(self):
        self._credit(10000.0, days_ago=75, partner=self.client_a)
        rows = self.Dashboard.get_top_debtors(limit=5)
        row = next(r for r in rows if r['name'] == "Client Ardoise A")
        self.assertEqual(row['severity'], 'critical')
        self.assertEqual(row['max_age'], 75)
        self.assertEqual(row['phone'], '+224 600 11 11 11')

    def test_top_debtors_honours_the_limit(self):
        for i in range(6):
            partner = self.env['res.partner'].create({'name': f"Débiteur {i}"})
            self._credit(1000.0 * (i + 1), partner=partner)
        rows = self.Dashboard.get_top_debtors(limit=3)
        self.assertEqual(len(rows), 3)

    def test_payment_breakdown_by_method(self):
        credit = self._credit(60000.0)
        self._repay(credit, 20000.0, method='mtn')
        self._repay(credit, 10000.0, method='cash')
        rows = self.Dashboard.get_payment_breakdown(self.d_from, self.d_to)
        by_method = {r['label']: r['amount'] for r in rows}
        self.assertEqual(by_method.get("MTN Mobile Money"), 20000.0)
        self.assertEqual(by_method.get("Espèces"), 10000.0)

    def test_daily_recoveries_series_fills_empty_days(self):
        credit = self._credit(30000.0)
        self._repay(credit, 30000.0)
        rows = self.Dashboard.get_daily_recoveries(self.d_from, self.d_to)
        # Une entrée par jour de la période, zéros compris.
        self.assertEqual(len(rows), 31)
        self.assertEqual(sum(r['amount'] for r in rows), 30000.0)

    def test_long_period_switches_to_monthly_buckets(self):
        rows = self.Dashboard.get_daily_recoveries(
            fields.Date.to_string(self.today - timedelta(days=300)),
            fields.Date.to_string(self.today))
        self.assertLess(len(rows), 62)
        self.assertRegex(rows[0]['label'], r'^[A-ZÉÀÛ][a-zûéô]+ \d{2}$')

    def test_recent_payments_listing(self):
        credit = self._credit(30000.0)
        self._repay(credit, 12000.0, method='orange')
        rows = self.Dashboard.get_recent_payments(self.d_from, self.d_to)
        self.assertTrue(rows)
        self.assertEqual(rows[0]['amount'], 12000.0)

    def test_meta_payload(self):
        meta = self.Dashboard.get_dashboard_meta()
        self.assertIn('currency_symbol', meta)
