# -*- coding: utf-8 -*-
"""Journal des commandes : des dates dans le fuseau de l'utilisateur.

Écart n° 37 (règle 6) : les dates du journal (commande, livraison prévue,
réception) étaient la partie « date » de l'heure UTC enregistrée. Une
commande passée à 0 h 30 à Douala (23 h 30 UTC la veille) était datée du
jour précédent, et son retard de livraison calculé sur des dates UTC
comparées à la date du jour locale.
"""
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install', 'aite_purchase')
class TestPurchaseLocalDates(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.user.tz = 'Africa/Douala'          # UTC+1, sans heure d'été
        cls.dashboard = cls.env['aite.purchase.dashboard']
        cls.supplier = cls.env['res.partner'].create({
            'name': "Grossiste de minuit", 'supplier_rank': 1,
        })
        cls.goods = cls.env['product.product'].create({
            'name': "Casier de jus",
            'is_storable': True,
            'purchase_ok': True,
            'standard_price': 9000.0,
            'taxes_id': [(5, 0, 0)],
            'supplier_taxes_id': [(5, 0, 0)],
        })

    def test_order_journal_dates_follow_the_user_timezone(self):
        order = self.env['purchase.order'].create({
            'partner_id': self.supplier.id,
            'company_id': self.env.company.id,
            # 15/10/2026 à 0 h 30 à Douala
            'date_order': '2026-10-14 23:30:00',
            'order_line': [(0, 0, {
                'product_id': self.goods.id,
                'name': self.goods.name,
                'product_qty': 3,
                'price_unit': 9000.0,
                # 17/10/2026 à 0 h 30 à Douala
                'date_planned': '2026-10-16 23:30:00',
            })],
        })
        order.button_confirm()
        self.env.flush_all()
        rows = self.dashboard.get_orders_journal('2026-10-01', '2026-10-31')
        row = next(r for r in rows if r['ref'] == order.name)
        self.assertEqual(row['date'], '2026-10-15')
        self.assertEqual(row['planned'], '2026-10-17')

    def test_period_filter_uses_the_local_day_bounds(self):
        """Écart n° 37 (reprise) : la période filtrait ``date_order`` sur
        des bornes UTC. Une commande du 01/10/2026 à 0 h 30 à Douala
        (30/09 à 23 h 30 UTC) tombait dans le journal de SEPTEMBRE, datée
        « 01/10/2026 », et manquait à octobre — avec les achats de la
        période, l'OTIF et les meilleurs produits."""
        order = self.env['purchase.order'].create({
            'partner_id': self.supplier.id,
            'company_id': self.env.company.id,
            'date_order': '2026-09-30 23:30:00',
            'order_line': [(0, 0, {
                'product_id': self.goods.id,
                'name': self.goods.name,
                'product_qty': 2,
                'price_unit': 9000.0,
                'date_planned': '2026-10-02 08:00:00',
            })],
        })
        order.button_confirm()
        self.env.flush_all()
        october = self.dashboard.get_orders_journal(
            '2026-10-01', '2026-10-31', supplier_id=self.supplier.id)
        september = self.dashboard.get_orders_journal(
            '2026-09-01', '2026-09-30', supplier_id=self.supplier.id)
        self.assertEqual([(r['ref'], r['date']) for r in october],
                         [(order.name, '2026-10-01')])
        self.assertEqual(september, [])
        kpis_oct = self.dashboard.get_kpis(
            '2026-10-01', '2026-10-31', supplier_id=self.supplier.id)
        kpis_sep = self.dashboard.get_kpis(
            '2026-09-01', '2026-09-30', supplier_id=self.supplier.id)
        self.assertEqual(kpis_oct['achats'], 18000.0)
        self.assertEqual(kpis_sep['achats'], 0.0)
        self.assertIn(self.goods.display_name,
                      [p['name'] for p in kpis_oct['top_products']])
        self.assertNotIn(self.goods.display_name,
                         [p['name'] for p in kpis_sep['top_products']])

    def test_period_end_includes_the_last_local_evening(self):
        """Symétrique : le 31/10/2026 à 23 h 30 à Douala (22 h 30 UTC)
        appartient bien au 31/10, et le 01/11 à 0 h 30 (31/10 à 23 h 30
        UTC) n'appartient plus à octobre."""
        late = self.env['purchase.order'].create({
            'partner_id': self.supplier.id,
            'company_id': self.env.company.id,
            'date_order': '2026-10-31 22:30:00',
            'order_line': [(0, 0, {
                'product_id': self.goods.id, 'name': self.goods.name,
                'product_qty': 1, 'price_unit': 9000.0,
            })],
        })
        november = self.env['purchase.order'].create({
            'partner_id': self.supplier.id,
            'company_id': self.env.company.id,
            'date_order': '2026-10-31 23:30:00',
            'order_line': [(0, 0, {
                'product_id': self.goods.id, 'name': self.goods.name,
                'product_qty': 1, 'price_unit': 9000.0,
            })],
        })
        (late | november).button_confirm()
        self.env.flush_all()
        refs = [r['ref'] for r in self.dashboard.get_orders_journal(
            '2026-10-01', '2026-10-31', supplier_id=self.supplier.id)]
        self.assertIn(late.name, refs)
        self.assertNotIn(november.name, refs)
