# -*- coding: utf-8 -*-
"""Tableau de bord Achats : contrat d'API et consignes fournisseurs."""
from datetime import timedelta

from odoo import fields
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install', 'aite_purchase')
class TestPurchaseDashboardApi(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.dashboard = cls.env['aite.purchase.dashboard']
        cls.today = fields.Date.context_today(cls.env.user)

        cls.supplier = cls.env['res.partner'].create({
            'name': "Grossiste Test",
            'supplier_rank': 1,
        })
        cls.goods = cls.env['product.product'].create({
            'name': "Carton de sodas",
            'is_storable': True,
            'purchase_ok': True,
            'standard_price': 15000.0,
            'list_price': 25000.0,
            'taxes_id': [(5, 0, 0)],
            'supplier_taxes_id': [(5, 0, 0)],
        })

    def _order(self, qty=10, price=15000.0, confirm=True, days_ago=5):
        order = self.env['purchase.order'].create({
            'partner_id': self.supplier.id,
            'company_id': self.company.id,
            'date_order': fields.Datetime.to_string(
                fields.Datetime.now() - timedelta(days=days_ago)),
            'order_line': [(0, 0, {
                'product_id': self.goods.id,
                'name': self.goods.name,
                'product_qty': qty,
                'price_unit': price,
                'date_planned': fields.Datetime.to_string(
                    fields.Datetime.now()),
            })],
        })
        if confirm:
            order.button_confirm()
        self.env.flush_all()
        return order

    def _endpoints(self):
        d = self.dashboard
        d_from = fields.Date.to_string(self.today - timedelta(days=60))
        d_to = fields.Date.to_string(self.today)
        return [
            ('get_meta', lambda: d.get_meta()),
            ('get_suppliers', lambda: d.get_suppliers()),
            ('get_kpis', lambda: d.get_kpis(d_from, d_to)),
            ('get_open_invoices', lambda: d.get_open_invoices()),
            ('get_orders_journal',
             lambda: d.get_orders_journal(d_from, d_to)),
            ('get_claims', lambda: d.get_claims()),
            ('get_flux_months', lambda: d.get_flux_months()),
            ('get_price_moves', lambda: d.get_price_moves()),
            ('get_price_index', lambda: d.get_price_index()),
            ('get_supplier_rows',
             lambda: d.get_supplier_rows(d_from, d_to)),
        ]

    # ------------------------------------------------------------------
    # Robustesse
    # ------------------------------------------------------------------

    def test_every_endpoint_answers_on_a_quiet_base(self):
        for name, call in self._endpoints():
            with self.subTest(endpoint=name):
                self.assertIsNotNone(call(), "%s ne renvoie rien" % name)

    def test_every_endpoint_answers_with_orders(self):
        self._order()
        self._order(qty=4, price=17000.0, days_ago=2)
        for name, call in self._endpoints():
            with self.subTest(endpoint=name):
                self.assertIsNotNone(call(), "%s ne renvoie rien" % name)

    def test_bad_dates_fall_back_to_the_current_month(self):
        dt_from, dt_to = self.dashboard._parse_period('trois mai', None)
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

    def test_supplier_appears_once_ordered(self):
        self._order()
        names = {s['name'] for s in self.dashboard.get_suppliers()}
        self.assertIn("Grossiste Test", names)

    def test_order_reaches_the_journal(self):
        order = self._order()
        rows = self.dashboard.get_orders_journal(
            fields.Date.to_string(self.today - timedelta(days=60)),
            fields.Date.to_string(self.today))
        refs = {r['ref'] for r in rows}
        self.assertIn(order.name, refs)
        row = next(r for r in rows if r['ref'] == order.name)
        self.assertEqual(row['partner'], "Grossiste Test")
        self.assertEqual(row['amount'], order.amount_total)

    def test_supplier_filter_narrows_the_rows(self):
        self._order()
        other = self.env['res.partner'].create({
            'name': "Fournisseur sans commande", 'supplier_rank': 1,
        })
        rows = self.dashboard.get_orders_journal(
            fields.Date.to_string(self.today - timedelta(days=60)),
            fields.Date.to_string(self.today), supplier_id=other.id)
        self.assertEqual(rows, [])

    def test_price_increase_is_detected(self):
        """Une hausse de prix entre deux commandes doit remonter."""
        self._order(price=15000.0, days_ago=30)
        self._order(price=18000.0, days_ago=1)
        moves = self.dashboard.get_price_moves()
        self.assertIsInstance(moves, list)

    def test_meta_payload(self):
        meta = self.dashboard.get_meta()
        self.assertIsInstance(meta, dict)
        self.assertTrue(meta)


@tagged('post_install', '-at_install', 'aite_purchase')
class TestPurchaseDeposit(TransactionCase):
    """Consignes fournisseur (bouteilles, casiers)."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.supplier = cls.env['res.partner'].create({
            'name': "Brasserie Test", 'supplier_rank': 1,
        })

    def test_deposit_value_is_quantity_times_unit_price(self):
        deposit = self.env['aite.purchase.deposit'].create({
            'partner_id': self.supplier.id,
            'qty': 30,
            'unit_value': 2500.0,
        })
        self.assertEqual(deposit.value, 75000.0)

    def test_zero_quantity_has_no_value(self):
        other = self.env['res.partner'].create({
            'name': "Brasserie Vide", 'supplier_rank': 1,
        })
        deposit = self.env['aite.purchase.deposit'].create({
            'partner_id': other.id,
            'qty': 0,
            'unit_value': 2500.0,
        })
        self.assertEqual(deposit.value, 0.0)

    def test_only_one_deposit_line_per_supplier(self):
        """Une seule ligne de consignes par fournisseur."""
        self.env['aite.purchase.deposit'].create({
            'partner_id': self.supplier.id,
            'qty': 10, 'unit_value': 1000.0,
        })
        with self.assertRaises(Exception):
            with self.env.cr.savepoint():
                self.env['aite.purchase.deposit'].create({
                    'partner_id': self.supplier.id,
                    'qty': 5, 'unit_value': 1000.0,
                })

    def test_value_follows_a_partial_return(self):
        deposit = self.env['aite.purchase.deposit'].create({
            'partner_id': self.supplier.id,
            'qty': 40, 'unit_value': 2500.0,
        })
        self.assertEqual(deposit.value, 100000.0)
        deposit.write({'qty': 15,
                       'last_return_date': fields.Date.context_today(
                           self.env.user)})
        self.assertEqual(deposit.value, 37500.0)
