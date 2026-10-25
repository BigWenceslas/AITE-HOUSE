# -*- coding: utf-8 -*-
"""Ergonomie de l'analyse des ventes (écart non bloquant n° 67).

* une caisse garde la même couleur d'un onglet à l'autre (filtre,
  tableau de bord, onglet « Par caisse »), quel que soit son rang ;
* les seuils d'écart de caisse (« Élevé », « Critique ») se règlent
  par société, sans code, et reclassent les sessions déjà comptées ;
* un seul menu « Analyse » dans la barre du Point de Vente : la section
  AITE vit dans le menu Analyse standard.
"""
from datetime import timedelta

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import tagged

from .common import PosAnalyticsCommon


@tagged('post_install', '-at_install', 'aite_analytics')
class TestPosDisplay(PosAnalyticsCommon):

    def setUp(self):
        super().setUp()
        self.dash = self.env['aite.pos.dashboard']
        self.d_from = fields.Date.to_string(self.today - timedelta(days=1))
        self.d_to = fields.Date.to_string(self.today + timedelta(days=1))

    def _second_till(self):
        """Une deuxième caisse, ouverte, qui vendra PLUS que la première
        (son rang au chiffre d'affaires diffère de son rang de création)."""
        journal = self.env['account.journal'].create({
            'name': "Caisse terrasse (test)",
            'type': 'cash',
            'code': 'CTTST',
            'company_id': self.company.id,
        })
        method = self.env['pos.payment.method'].create({
            'name': "Espèces terrasse",
            'journal_id': journal.id,
            'company_id': self.company.id,
        })
        config = self.env['pos.config'].create({
            'name': "Bar terrasse",
            'payment_method_ids': [(6, 0, method.ids)],
        })
        config.open_ui()
        session = config.current_session_id
        if not session.start_at:
            session.start_at = fields.Datetime.now()
        return config, session, method

    def _sale_on(self, session, method, product, qty, price):
        total = qty * price
        order = self.env['pos.order'].create({
            'session_id': session.id,
            'company_id': self.company.id,
            'amount_tax': 0.0,
            'amount_total': total,
            'amount_paid': total,
            'amount_return': 0.0,
            'lines': [(0, 0, {
                'product_id': product.id,
                'qty': qty,
                'price_unit': price,
                'price_subtotal': total,
                'price_subtotal_incl': total,
            })],
        })
        self.env['pos.payment'].create({
            'pos_order_id': order.id,
            'payment_method_id': method.id,
            'amount': total,
        })
        order.write({'state': 'paid'})
        self.env.flush_all()
        return order

    # ------------------------------------------------------------------
    # Couleur d'une caisse
    # ------------------------------------------------------------------

    def test_a_till_keeps_its_colour_on_every_tab(self):
        terrace, session, method = self._second_till()
        self._sale([(self.beer, 1, 5000.0)])
        self._sale_on(session, method, self.dish, 3, 20000.0)
        filter_colours = {c['id']: c['color']
                          for c in self.dash.get_pos_configs()}
        breakdown = self.dash.get_caisse_breakdown(self.d_from, self.d_to)
        ranked = [c['config_id'] for c in breakdown['caisses']]
        # La terrasse, créée après, passe devant au chiffre d'affaires.
        self.assertEqual(ranked.index(terrace.id), 0)
        for row in breakdown['caisses']:
            with self.subTest(till=row['name']):
                self.assertEqual(row['color'], filter_colours[row['config_id']])
        # Filtrer sur une seule caisse ne la recolore pas.
        alone = self.dash.get_caisse_breakdown(
            self.d_from, self.d_to, config_id=self.pos_config.id)
        self.assertEqual(alone['caisses'][0]['color'],
                         filter_colours[self.pos_config.id])

    # ------------------------------------------------------------------
    # Seuils d'écart de caisse
    # ------------------------------------------------------------------

    def _count_the_till(self, shortfall):
        self.session.invalidate_recordset()
        theoretical = self.session.cash_register_balance_end
        self.session.write({
            'cash_register_balance_end_real': theoretical - shortfall,
        })

    def test_gap_thresholds_are_company_settings(self):
        Session = self.env['pos.session']
        self.assertEqual(self.company.aite_pos_gap_med,
                         Session.DISCREPANCY_THRESHOLD_MED)
        self.assertEqual(self.company.aite_pos_gap_high,
                         Session.DISCREPANCY_THRESHOLD_HIGH)
        settings = self.env['res.config.settings'].create({
            'aite_pos_gap_med': 5000.0,
            'aite_pos_gap_high': 8000.0,
        })
        settings.execute()
        self.assertEqual(self.company.aite_pos_gap_med, 5000.0)
        self._sale([(self.beer, 4, 5000.0)])          # 20 000 en caisse
        for shortfall, expected in ((1000.0, 'low'), (6000.0, 'med'),
                                    (9000.0, 'high')):
            with self.subTest(shortfall=shortfall):
                self._count_the_till(shortfall)
                self.assertEqual(self.session.cash_discrepancy_severity,
                                 expected)

    def test_changing_a_threshold_reclassifies_counted_sessions(self):
        self._sale([(self.beer, 4, 5000.0)])
        self._count_the_till(6000.0)
        self.assertEqual(self.session.cash_discrepancy_severity, 'low')
        self.company.write({'aite_pos_gap_med': 5000.0,
                            'aite_pos_gap_high': 8000.0})
        self.assertEqual(self.session.cash_discrepancy_severity, 'med')

    def test_thresholds_must_stay_ordered(self):
        with self.assertRaises(ValidationError):
            self.company.write({'aite_pos_gap_med': 300000.0,
                                'aite_pos_gap_high': 200000.0})

    # ------------------------------------------------------------------
    # Un seul menu « Analyse »
    # ------------------------------------------------------------------

    def test_a_single_analysis_menu_in_the_point_of_sale(self):
        root = self.env.ref('point_of_sale.menu_point_root')
        reporting = self.env.ref('point_of_sale.menu_point_rep')
        aite = self.env.ref('aite_pos_analytics.menu_aite_pos_analytics_root')
        self.assertEqual(aite.parent_id, reporting)
        self.assertNotIn(aite, root.child_id)
        pivot = self.env.ref('aite_pos_analytics.menu_aite_pos_daily_report')
        self.assertEqual(pivot.name, "Tableau croisé & graphique")

    # ------------------------------------------------------------------
    # Montants en FCFA (règle 6)
    # ------------------------------------------------------------------

    def test_amount_headers_say_fcfa(self):
        """L'en-tête de l'écart de caisse dit « FCFA », comme les montants
        du reste de l'écran — plus de « Écart (F) » dans l'onglet Écarts."""
        from odoo.tools import file_open
        with file_open('aite_pos_analytics/static/src/xml/views.xml') as f:
            xml = f.read()
        self.assertFalse('(F)<' in xml, "en-tête « (F) » au lieu de « FCFA »")
        self.assertTrue('Écart (FCFA)' in xml, "en-tête « Écart (FCFA) » absent")
