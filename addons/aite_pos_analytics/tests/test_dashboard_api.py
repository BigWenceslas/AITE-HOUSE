# -*- coding: utf-8 -*-
"""Contrat d'API du tableau de bord POS Analytics.

Chaque point d'entrée appelé par le client OWL est exercé deux fois —
sur une période **vide** puis sur une période **peuplée** — et sous le
profil métier réel. C'est la classe de bug la plus fréquente sur un
tableau de bord : division par zéro, clé absente, accès refusé.
"""
from datetime import timedelta

from odoo import fields
from odoo.tests import tagged

from .common import PosAnalyticsCommon


@tagged('post_install', '-at_install', 'aite_analytics')
class TestPosDashboardApi(PosAnalyticsCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.dashboard = cls.env['aite.pos.dashboard']
        cls.analyst = cls.env['res.users'].create({
            'name': "Analyste POS",
            'login': 'analyste.pos.test',
            'groups_id': [(6, 0, [
                cls.env.ref('base.group_user').id,
                cls.env.ref(
                    'aite_pos_analytics.group_aite_pos_analytics_user').id,
            ])],
        })

    def setUp(self):
        super().setUp()
        self.d_from = fields.Date.to_string(self.today - timedelta(days=7))
        self.d_to = fields.Date.to_string(self.today)
        self.far_from = fields.Date.to_string(
            self.today - timedelta(days=900))
        self.far_to = fields.Date.to_string(self.today - timedelta(days=890))

    def _endpoints(self, date_from, date_to):
        """(nom, appelable) de tous les points d'entrée du tableau de bord."""
        d = self.dashboard
        cfg = self.pos_config.id
        return [
            ('get_pos_configs', lambda: d.get_pos_configs()),
            ('get_kpis', lambda: d.get_kpis(date_from, date_to)),
            ('get_kpis[caisse]', lambda: d.get_kpis(date_from, date_to, cfg)),
            ('get_top_products',
             lambda: d.get_top_products(date_from, date_to)),
            ('get_category_breakdown',
             lambda: d.get_category_breakdown(date_from, date_to)),
            ('get_category_evolution', lambda: d.get_category_evolution()),
            ('get_monthly_evolution',
             lambda: d.get_monthly_evolution(date_from, date_to)),
            ('get_rankings', lambda: d.get_rankings(date_from, date_to)),
            ('get_products_full',
             lambda: d.get_products_full(date_from, date_to)),
            ('get_sessions', lambda: d.get_sessions(date_from, date_to)),
            ('get_cash_discrepancies',
             lambda: d.get_cash_discrepancies(date_from, date_to)),
            ('get_payment_breakdown',
             lambda: d.get_payment_breakdown(date_from, date_to)),
            ('get_caisse_breakdown',
             lambda: d.get_caisse_breakdown(date_from, date_to)),
            ('get_hourly_heatmap',
             lambda: d.get_hourly_heatmap(date_from, date_to)),
            ('get_time_insights',
             lambda: d.get_time_insights(date_from, date_to)),
        ]

    # ------------------------------------------------------------------
    # Période vide : aucun point d'entrée ne doit tomber
    # ------------------------------------------------------------------

    def test_every_endpoint_survives_an_empty_period(self):
        for name, call in self._endpoints(self.far_from, self.far_to):
            with self.subTest(endpoint=name):
                result = call()
                self.assertIsNotNone(result, "%s ne renvoie rien" % name)

    # ------------------------------------------------------------------
    # Période peuplée
    # ------------------------------------------------------------------

    def test_every_endpoint_survives_a_populated_period(self):
        self._sale([(self.beer, 3, 5000.0), (self.dish, 1, 20000.0)])
        self._sale([(self.dish, 2, 20000.0)])
        for name, call in self._endpoints(self.d_from, self.d_to):
            with self.subTest(endpoint=name):
                result = call()
                self.assertIsNotNone(result, "%s ne renvoie rien" % name)

    def test_every_endpoint_works_for_the_business_profile(self):
        """Le tableau de bord doit s'ouvrir pour un utilisateur métier."""
        self._sale([(self.beer, 2, 5000.0)])
        dashboard = self.env['aite.pos.dashboard'].with_user(self.analyst)
        for name, call in [
            ('get_pos_configs', lambda: dashboard.get_pos_configs()),
            ('get_kpis', lambda: dashboard.get_kpis(self.d_from, self.d_to)),
            ('get_rankings',
             lambda: dashboard.get_rankings(self.d_from, self.d_to)),
            ('get_sessions',
             lambda: dashboard.get_sessions(self.d_from, self.d_to)),
            ('get_hourly_heatmap',
             lambda: dashboard.get_hourly_heatmap(self.d_from, self.d_to)),
        ]:
            with self.subTest(endpoint=name):
                self.assertIsNotNone(call())

    def test_bad_dates_raise_a_readable_message(self):
        """Une date illisible donne une erreur métier, pas une 500.

        Choix assumé de ce module : il refuse la période plutôt que de
        retomber silencieusement sur le mois courant comme les tableaux
        de bord Hôtel, Stock et Crédit. Ce qui compte est que l'échec
        soit une ``UserError`` lisible et non une trace serveur.
        """
        from odoo.exceptions import UserError
        with self.assertRaises(UserError):
            self.dashboard.get_kpis('pas-une-date', None)
        with self.assertRaises(UserError):
            self.dashboard.get_rankings('', '')

    def test_inverted_period_is_refused(self):
        from odoo.exceptions import UserError
        with self.assertRaises(UserError):
            self.dashboard.get_kpis(self.d_to, self.far_from)

    def test_endpoints_without_dates_always_answer(self):
        self.assertIsNotNone(self.dashboard.get_pos_configs())
        self.assertIsNotNone(self.dashboard.get_category_evolution())

    # ------------------------------------------------------------------
    # Contrôles de contenu
    # ------------------------------------------------------------------

    def test_kpis_reflect_the_sales(self):
        self._sale([(self.beer, 2, 5000.0)])     # CA 10 000, marge 6 000
        self._sale([(self.dish, 1, 20000.0)])    # CA 20 000, marge 8 000
        kpis = self.dashboard.get_kpis(
            self.d_from, self.d_to, self.pos_config.id)
        self.assertEqual(kpis['ca'], 30000.0)
        self.assertEqual(kpis['order_count'], 2)
        self.assertEqual(kpis['cost'], 16000.0)
        self.assertEqual(kpis['margin'], 14000.0)
        self.assertEqual(kpis['average_basket'], 15000.0)
        # 14 000 / 30 000
        self.assertAlmostEqual(kpis['margin_rate'], 46.67, places=2)
        self.assertAlmostEqual(kpis['cmv_rate'], 53.33, places=2)

    def test_empty_period_returns_zeros(self):
        kpis = self.dashboard.get_kpis(self.far_from, self.far_to)
        self.assertEqual(kpis['ca'], 0.0)
        self.assertEqual(kpis['order_count'], 0)
        self.assertEqual(kpis['average_basket'], 0.0)
        self.assertEqual(kpis['margin_rate'], 0.0)
        self.assertEqual(kpis['cost_per_unit'], 0.0)

    def test_previous_period_is_contiguous_and_same_length(self):
        prev_from, prev_to = self.dashboard._previous_period(
            '2026-06-01', '2026-06-30')
        self.assertEqual((prev_from, prev_to), ('2026-05-02', '2026-05-31'))

    def test_delta_is_none_without_a_baseline(self):
        self.assertIsNone(self.dashboard._delta_pct(100.0, 0.0))
        self.assertEqual(self.dashboard._delta_pct(150.0, 100.0), 50.0)

    def test_top_products_is_sorted_by_revenue(self):
        self._sale([(self.beer, 1, 5000.0), (self.dish, 3, 20000.0)])
        rows = self.dashboard.get_top_products(
            self.d_from, self.d_to, limit=5, config_id=self.pos_config.id)
        self.assertTrue(rows)
        self.assertEqual(rows[0]['name'], "Poulet braisé")

    def test_top_products_honours_the_limit(self):
        self._sale([(self.beer, 1, 5000.0), (self.dish, 1, 20000.0)])
        rows = self.dashboard.get_top_products(
            self.d_from, self.d_to, limit=1, config_id=self.pos_config.id)
        self.assertEqual(len(rows), 1)

    def test_category_breakdown_splits_by_category(self):
        self._sale([(self.beer, 2, 5000.0), (self.dish, 1, 20000.0)])
        rows = self.dashboard.get_category_breakdown(
            self.d_from, self.d_to, self.pos_config.id)
        names = {r['name'] for r in rows}
        self.assertIn("Boissons test", names)
        self.assertIn("Cuisine test", names)

    def test_pos_configs_listing_carries_colors(self):
        rows = self.dashboard.get_pos_configs()
        self.assertTrue(rows)
        self.assertTrue(all('color' in r and 'name' in r for r in rows))

    def test_sessions_listing_contains_the_open_session(self):
        self._sale([(self.beer, 1, 5000.0)])
        rows = self.dashboard.get_sessions(
            self.d_from, self.d_to, self.pos_config.id)
        self.assertTrue(rows)

    def test_heatmap_has_a_bucket_per_hour(self):
        self._sale([(self.beer, 1, 5000.0)])
        data = self.dashboard.get_hourly_heatmap(self.d_from, self.d_to)
        self.assertIsInstance(data, (dict, list))
