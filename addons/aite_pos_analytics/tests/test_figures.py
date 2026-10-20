# -*- coding: utf-8 -*-
"""Chiffres justes hors de l'écran principal (écarts n° 25, 26, 27).

* n° 25 — le CA d'une session est HT, comme celui du tableau de bord ;
* n° 26 — taux de marge affiché tel quel (pas ×100), nombre de
  paiements, session ouverte non comptée, articles remboursés, filtres
  Heure / Jour transmis à tous les blocs du tableau de bord ;
* n° 27 — heure locale de l'établissement, pas celle de l'utilisateur
  qui a installé le module.
"""
from datetime import datetime, timedelta

from lxml import etree

from odoo import fields
from odoo.tests import tagged

from .common import PosAnalyticsCommon


@tagged('post_install', '-at_install', 'aite_analytics')
class TestPosFigures(PosAnalyticsCommon):

    def setUp(self):
        super().setUp()
        self.dash = self.env['aite.pos.dashboard']
        self.d_from = fields.Date.to_string(self.today - timedelta(days=1))
        self.d_to = fields.Date.to_string(self.today + timedelta(days=1))

    def _order(self, lines, tax=0.0, date_order=None):
        """``lines`` = [(produit, qté, prix_unitaire HT)] ; ``tax`` ajoutée
        au total du ticket (réparti sur la première ligne)."""
        total_ht = sum(qty * price for _p, qty, price in lines)
        total = total_ht + tax
        vals = {
            'session_id': self.session.id,
            'company_id': self.company.id,
            'amount_tax': tax,
            'amount_total': total,
            'amount_paid': total,
            'amount_return': 0.0,
            'lines': [(0, 0, {
                'product_id': product.id,
                'qty': qty,
                'price_unit': price,
                'price_subtotal': qty * price,
                'price_subtotal_incl': qty * price + (tax if i == 0 else 0.0),
            }) for i, (product, qty, price) in enumerate(lines)],
        }
        if date_order:
            vals['date_order'] = date_order
        order = self.env['pos.order'].create(vals)
        self.env['pos.payment'].create({
            'pos_order_id': order.id,
            'payment_method_id': self.method_cash.id,
            'amount': total,
        })
        order.write({'state': 'paid'})
        self.env.flush_all()
        return order

    # ------------------------------------------------------------------
    # n° 25 — CA de session HT, comme le tableau de bord
    # ------------------------------------------------------------------

    def test_session_revenue_is_excluding_tax_like_the_dashboard(self):
        self._order([(self.beer, 2, 5000.0)], tax=1925.0)
        self.session.invalidate_recordset()
        kpis = self.dash.get_kpis(self.d_from, self.d_to,
                                  config_id=self.pos_config.id)
        self.assertEqual(kpis['ca'], 10000.0)
        self.assertEqual(self.session.total_ca, kpis['ca'])
        self.assertAlmostEqual(self.session.margin_rate,
                               kpis['margin_rate'], places=2)
        rows = self.dash.get_sessions(self.d_from, self.d_to,
                                      config_id=self.pos_config.id)
        self.assertEqual(rows[0]['total_ca'], 10000.0)

    # ------------------------------------------------------------------
    # n° 26 — taux de marge, comptage, session ouverte, remboursement
    # ------------------------------------------------------------------

    def test_margin_rate_is_not_shown_as_a_fraction(self):
        """``margin_rate`` est déjà en % : le widget ``percentage``
        (qui multiplie par 100) affichait 6 000 % pour 60 %."""
        for xmlid in ('aite_pos_analytics.view_pos_order_form_inherit_analytics',
                      'aite_pos_analytics.view_pos_order_list_inherit_analytics',
                      'aite_pos_analytics.view_pos_session_list_inherit_analytics',
                      'aite_pos_analytics.view_pos_daily_report_list'):
            view = self.env.ref(xmlid, raise_if_not_found=False)
            if not view:
                continue
            arch = etree.fromstring(view.arch_db.encode())
            for node in arch.iter('field'):
                if node.get('name') == 'margin_rate':
                    with self.subTest(view=xmlid):
                        self.assertNotEqual(node.get('widget'), 'percentage')

    def test_payment_breakdown_counts_the_payments(self):
        self._sale([(self.beer, 1, 5000.0)])
        self._sale([(self.dish, 1, 20000.0)])
        rows = self.dash.get_payment_breakdown(
            self.d_from, self.d_to, config_id=self.pos_config.id)
        row = next(r for r in rows if r['method_id'] == self.method_cash.id)
        self.assertEqual(row['count'], 2)

    def test_open_session_not_yet_counted_has_no_shortfall(self):
        """Une caisse ouverte que personne n'a encore comptée n'a pas de
        manquant : elle ne doit être ni « Critique » ni listée."""
        self._sale([(self.beer, 60, 5000.0)])          # 300 000 en caisse
        self.session.invalidate_recordset()
        self.assertIn(self.session.state, ('opening_control', 'opened'))
        self.assertFalse(self.session.cash_register_balance_end_real)
        self.assertEqual(self.session.cash_discrepancy_severity, 'none')
        disc = self.dash.get_cash_discrepancies(
            self.d_from, self.d_to, config_id=self.pos_config.id)
        self.assertNotIn(self.session.id, [s['id'] for s in disc['sessions']])
        caisse = self.dash.get_caisse_breakdown(
            self.d_from, self.d_to, config_id=self.pos_config.id)
        self.assertEqual(caisse['total']['cash_difference'], 0.0)

    def test_refunded_product_leaves_the_rankings(self):
        """Vendu puis remboursé : l'article n'a rien vendu."""
        self._sale([(self.dish, 1, 20000.0)])
        self._sale([(self.beer, 1, 5000.0)])
        self._sale([(self.beer, -1, 5000.0)])         # remboursement
        rankings = self.dash.get_rankings(
            self.d_from, self.d_to, config_id=self.pos_config.id)
        best = [r['product_id'] for r in rankings['best_margins']]
        low = [r['product_id'] for r in rankings['low_sellers']]
        self.assertNotIn(self.beer.id, best)
        self.assertNotIn(self.beer.id, low)
        self.assertIn(self.dish.id, best)
        self.assertIn(self.dish.id, low)

    def test_hour_and_day_filters_reach_every_dashboard_block(self):
        self._sale([(self.beer, 2, 5000.0)])
        report = self.env['aite.pos.daily.report'].search(
            [('config_id', '=', self.pos_config.id)], limit=1)
        other_hour = (report.hour + 12) % 24
        none = {'hour_from': other_hour, 'hour_to': other_hour}
        same = {'hour_from': report.hour, 'hour_to': report.hour,
                'weekdays': [report.dow]}
        cfg = self.pos_config.id
        d = self.dash
        calls = {
            'top': lambda f: d.get_top_products(
                self.d_from, self.d_to, 8, cfg, filters=f),
            'evolution': lambda f: d.get_monthly_evolution(
                self.d_from, self.d_to, cfg, filters=f),
            'categories': lambda f: d.get_category_breakdown(
                self.d_from, self.d_to, cfg, filters=f),
            'products': lambda f: d.get_products_full(
                self.d_from, self.d_to, cfg, filters=f),
            'rankings': lambda f: d.get_rankings(
                self.d_from, self.d_to, cfg, filters=f)['low_sellers'],
        }
        for name, call in calls.items():
            with self.subTest(block=name):
                self.assertTrue(call(same), "%s : vente attendue" % name)
                self.assertFalse(call(none),
                                 "%s : le filtre horaire est ignoré" % name)

    # ------------------------------------------------------------------
    # n° 27 — heure locale de l'établissement
    # ------------------------------------------------------------------

    def test_heatmap_hour_is_the_local_hour_of_the_company(self):
        """Douala = UTC+1 : une vente à 18 h 30 UTC est une vente de 19 h,
        quel que soit le fuseau de l'utilisateur qui (ré)installe."""
        self.company.partner_id.tz = 'Africa/Douala'
        order = self._order([(self.beer, 1, 5000.0)],
                            date_order=datetime(2026, 10, 14, 18, 30))
        Report = self.env['aite.pos.daily.report']
        for installer_tz in ('UTC', 'Asia/Tokyo', False):
            with self.subTest(installer_tz=installer_tz):
                self.env.user.tz = installer_tz
                Report.init()
                Report.invalidate_model()
                row = Report.search([('order_id', '=', order.id)], limit=1)
                self.assertEqual(row.hour, 19)
                self.assertEqual(row.dow, 3)          # mercredi 14/10/2026
