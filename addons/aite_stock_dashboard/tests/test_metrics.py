# -*- coding: utf-8 -*-
"""Indicateurs de stock par référence — la règle d'alerte, testée nue."""
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install', 'aite_stock')
class TestStockMetrics(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.dashboard = cls.env['aite.stock.dashboard']
        # Paramètres de référence : sécurité 2 j, horizon 7 j,
        # critique 3 j, dormant 60 j.
        cls.cfg = dict(sec_days=2, horizon_days=7,
                       critical_days=3, dormant_days=60)

    def _m(self, stock, vday, lead=3, cost=1000.0, **kwargs):
        params = dict(self.cfg)
        params.update(kwargs)
        return self.dashboard._metrics(
            stock, vday, lead, cost,
            params['sec_days'], params['horizon_days'],
            params['critical_days'], params['dormant_days'],
            params.get('manual_threshold', 0.0),
            params.get('alert_active', True))

    # ------------------------------------------------------------------
    # Couverture
    # ------------------------------------------------------------------

    def test_coverage_in_days(self):
        """20 en stock, 4 vendus/jour ⇒ 5 jours de couverture."""
        self.assertEqual(self._m(20, 4)['couv'], 5.0)

    def test_no_sales_means_infinite_coverage(self):
        self.assertEqual(self._m(20, 0)['couv'], 999.0)

    # ------------------------------------------------------------------
    # Seuil et quantité à commander
    # ------------------------------------------------------------------

    def test_automatic_threshold(self):
        """Seuil = ventes/jour × (délai + sécurité), arrondi au supérieur."""
        # 4/j × (3 + 2) = 20
        self.assertEqual(self._m(100, 4)['seuil_auto'], 20.0)

    def test_threshold_is_rounded_up(self):
        # 1,5/j × 5 = 7,5 → 8
        self.assertEqual(self._m(100, 1.5)['seuil_auto'], 8.0)

    def test_manual_threshold_overrides_the_automatic_one(self):
        m = self._m(100, 4, manual_threshold=50.0)
        self.assertEqual(m['seuil'], 50.0)
        self.assertEqual(m['seuil_auto'], 20.0)

    def test_quantity_to_order_covers_lead_plus_horizon(self):
        """Besoin = ventes/jour × (délai + horizon) − stock."""
        # 4/j × (3 + 7) = 40 ; stock 10 ⇒ commander 30
        self.assertEqual(self._m(10, 4)['cmd'], 30.0)

    def test_nothing_to_order_when_well_stocked(self):
        self.assertEqual(self._m(500, 4)['cmd'], 0.0)

    def test_disabled_alert_orders_nothing(self):
        self.assertEqual(self._m(0, 10, alert_active=False)['cmd'], 0.0)

    # ------------------------------------------------------------------
    # Statut
    # ------------------------------------------------------------------

    def test_out_of_stock(self):
        m = self._m(0, 4)
        self.assertEqual(m['status'], 'Rupture')
        self.assertEqual(m['urgency'], 0)

    def test_critical_below_three_days(self):
        # 8 en stock, 4/j ⇒ 2 jours < 3
        m = self._m(8, 4)
        self.assertEqual(m['status'], 'Critique')
        self.assertEqual(m['urgency'], 1)

    def test_below_threshold(self):
        # 16 en stock, 4/j ⇒ 4 jours (> 3) mais ≤ seuil 20
        m = self._m(16, 4)
        self.assertEqual(m['status'], 'Sous seuil')
        self.assertEqual(m['urgency'], 2)

    def test_healthy_stock(self):
        m = self._m(200, 4)
        self.assertEqual(m['status'], 'OK')
        self.assertEqual(m['urgency'], 3)

    def test_ignored_reference_is_never_alerted(self):
        m = self._m(0, 10, alert_active=False)
        self.assertEqual(m['status'], 'Ignorée')
        self.assertEqual(m['urgency'], 4)

    def test_status_priority_out_of_stock_beats_critical(self):
        self.assertEqual(self._m(0, 100)['status'], 'Rupture')

    def test_urgency_is_ordered(self):
        """L'urgence classe bien du plus grave au moins grave."""
        urgencies = [
            self._m(0, 4)['urgency'],    # rupture
            self._m(8, 4)['urgency'],    # critique
            self._m(16, 4)['urgency'],   # sous seuil
            self._m(200, 4)['urgency'],  # OK
        ]
        self.assertEqual(urgencies, sorted(urgencies))

    # ------------------------------------------------------------------
    # Valorisation & rotation
    # ------------------------------------------------------------------

    def test_stock_value(self):
        self.assertEqual(self._m(20, 4, cost=2500.0)['value'], 50000.0)

    def test_rotation_over_thirty_days(self):
        """Rotation = ventes/jour × 30 / stock."""
        # 4/j × 30 / 20 = 6 rotations
        self.assertEqual(self._m(20, 4)['rot'], 6.0)

    def test_rotation_is_zero_without_stock(self):
        self.assertEqual(self._m(0, 4)['rot'], 0.0)

    def test_zero_sales_and_zero_stock(self):
        m = self._m(0, 0)
        self.assertEqual(m['value'], 0.0)
        self.assertEqual(m['rot'], 0.0)
        self.assertEqual(m['cmd'], 0.0)
        self.assertEqual(m['status'], 'Rupture')
