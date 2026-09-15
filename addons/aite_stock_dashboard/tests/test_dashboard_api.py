# -*- coding: utf-8 -*-
"""Contrat d'API du tableau de bord Stock, base vide puis peuplée."""
from datetime import timedelta

from odoo import fields
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install', 'aite_stock')
class TestStockDashboardApi(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.dashboard = cls.env['aite.stock.dashboard']
        cls.today = fields.Date.context_today(cls.env.user)

        cls.categ = cls.env['product.category'].create({
            'name': "Épicerie test",
        })
        cls.warehouse = cls.env['stock.warehouse'].search(
            [('company_id', '=', cls.company.id)], limit=1)
        cls.stock_loc = cls.warehouse.lot_stock_id

        cls.item = cls.env['product.product'].create({
            'name': "Riz 5 kg",
            'is_storable': True,
            'categ_id': cls.categ.id,
            'standard_price': 30000.0,
            'list_price': 45000.0,
            'taxes_id': [(5, 0, 0)],
        })
        cls.item_out = cls.env['product.product'].create({
            'name': "Huile 1 L (rupture)",
            'is_storable': True,
            'categ_id': cls.categ.id,
            'standard_price': 8000.0,
            'list_price': 12000.0,
            'taxes_id': [(5, 0, 0)],
        })

    def _put_in_stock(self, product, qty):
        self.env['stock.quant'].with_context(
            inventory_mode=True).create({
                'product_id': product.id,
                'location_id': self.stock_loc.id,
                'inventory_quantity': qty,
            })._apply_inventory()
        self.env.flush_all()

    def _endpoints(self):
        d = self.dashboard
        d_from = fields.Date.to_string(self.today - timedelta(days=30))
        d_to = fields.Date.to_string(self.today)
        return [
            ('get_meta', lambda: d.get_meta()),
            ('get_locations', lambda: d.get_locations()),
            ('get_categories', lambda: d.get_categories()),
            ('get_kpis', lambda: d.get_kpis(d_from, d_to)),
            ('get_alerts', lambda: d.get_alerts()),
            ('get_stock_list', lambda: d.get_stock_list()),
            ('get_stock_by_category', lambda: d.get_stock_by_category()),
            ('get_coverage_by_category',
             lambda: d.get_coverage_by_category()),
            ('get_top_value', lambda: d.get_top_value()),
            ('get_flux_months', lambda: d.get_flux_months()),
            ('get_coulage_series', lambda: d.get_coulage_series()),
            ('get_inventory_gaps', lambda: d.get_inventory_gaps(d_from, d_to)),
            ('get_moves_journal', lambda: d.get_moves_journal(d_from, d_to)),
            ('get_alert_products', lambda: d.get_alert_products()),
        ]

    # ------------------------------------------------------------------
    # Robustesse
    # ------------------------------------------------------------------

    def test_every_endpoint_answers_on_a_quiet_base(self):
        for name, call in self._endpoints():
            with self.subTest(endpoint=name):
                self.assertIsNotNone(call(), "%s ne renvoie rien" % name)

    def test_every_endpoint_answers_with_stock(self):
        self._put_in_stock(self.item, 40)
        for name, call in self._endpoints():
            with self.subTest(endpoint=name):
                self.assertIsNotNone(call(), "%s ne renvoie rien" % name)

    def test_bad_dates_fall_back_to_the_current_month(self):
        dt_from, dt_to = self.dashboard._parse_period('n importe quoi', None)
        self.assertEqual(dt_from, self.today.replace(day=1))
        self.assertEqual(dt_to, self.today)

    def test_inverted_dates_are_reordered(self):
        dt_from, dt_to = self.dashboard._parse_period(
            fields.Date.to_string(self.today),
            fields.Date.to_string(self.today - timedelta(days=10)))
        self.assertLess(dt_from, dt_to)

    # ------------------------------------------------------------------
    # Contenu
    # ------------------------------------------------------------------

    def test_stocked_item_appears_in_the_list(self):
        self._put_in_stock(self.item, 40)
        rows = self.dashboard.get_stock_list()
        row = next((r for r in rows if r['id'] == self.item.id), None)
        self.assertIsNotNone(row, "l'article en stock doit être listé")
        self.assertEqual(row['stock'], 40.0)
        self.assertEqual(row['cost'], 30000.0)
        self.assertEqual(row['value'], 40 * 30000.0)

    def test_item_never_moved_and_never_stocked_is_absent(self):
        rows = self.dashboard.get_stock_list()
        ids = {r['id'] for r in rows}
        self.assertNotIn(self.item_out.id, ids)

    def test_stock_value_reaches_the_kpis(self):
        self._put_in_stock(self.item, 10)
        kpis = self.dashboard.get_kpis(
            fields.Date.to_string(self.today - timedelta(days=30)),
            fields.Date.to_string(self.today))
        # Valorisation au coût et au prix de vente (double valorisation).
        self.assertGreaterEqual(kpis['total_value'], 10 * 30000.0)
        self.assertGreaterEqual(kpis['total_value_sale'], 10 * 45000.0)
        self.assertGreaterEqual(kpis['refs_count'], 1)
        self.assertGreaterEqual(kpis['total_units'], 10.0)

    def test_margin_percentage_is_consistent(self):
        """Marge % = (valeur de vente − valeur de coût) / valeur de vente."""
        self._put_in_stock(self.item, 10)
        kpis = self.dashboard.get_kpis(
            fields.Date.to_string(self.today - timedelta(days=30)),
            fields.Date.to_string(self.today))
        if kpis['total_value_sale']:
            expected = (kpis['total_value_sale'] - kpis['total_value']) \
                / kpis['total_value_sale'] * 100.0
            self.assertAlmostEqual(kpis['margin_pct'], expected, places=2)

    def test_kpis_expose_the_alert_counters(self):
        kpis = self.dashboard.get_kpis(
            fields.Date.to_string(self.today - timedelta(days=30)),
            fields.Date.to_string(self.today))
        for key in ('rupt_count', 'crit_count', 'seuil_count', 'dorm_count'):
            self.assertIn(key, kpis)
            self.assertIsInstance(kpis[key], int)

    def test_categories_listing_includes_ours(self):
        self._put_in_stock(self.item, 5)
        names = {c['name'] for c in self.dashboard.get_categories()}
        self.assertIn("Épicerie test", names)

    def test_locations_listing_carries_colors(self):
        rows = self.dashboard.get_locations()
        self.assertTrue(rows)
        self.assertTrue(all('color' in r for r in rows))

    def test_meta_exposes_the_thresholds(self):
        meta = self.dashboard.get_meta()
        for key in ('sec', 'hor', 'crit', 'dorm'):
            self.assertIn(key, meta.get('cfg', meta))

    def test_category_filter_narrows_the_list(self):
        self._put_in_stock(self.item, 10)
        other_categ = self.env['product.category'].create({
            'name': "Hors périmètre",
        })
        rows = self.dashboard.get_stock_list(categ_id=other_categ.id)
        ids = {r['id'] for r in rows}
        self.assertNotIn(self.item.id, ids)

    def test_alerts_payload_shape(self):
        self._put_in_stock(self.item, 1)
        alerts = self.dashboard.get_alerts()
        self.assertIsInstance(alerts, (dict, list))
