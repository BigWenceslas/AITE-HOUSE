# -*- coding: utf-8 -*-
"""Cockpit Direction : les moteurs parlent la même langue que lui.

Écarts n° 23, 24 et 25 relevés en tournant les vidéos :

* n° 23 — les barres « CA vs Achats » restaient à zéro (mois « octobre
  2026 » côté ventes, « Oct » côté achats) ; l'échéancier et la balance
  âgée fournisseurs restaient vides (le cockpit lisait ``amount`` /
  ``planned`` quand le moteur Achats rend ``residual`` / ``due``) ;
* n° 24 — les phrases « Flux net » et « position nette » disaient
  l'inverse du calcul ;
* n° 25 — un même chiffre (hébergement, restauration) ne doit avoir
  qu'une valeur d'un écran à l'autre (cas K04 de la recette).
"""
from datetime import timedelta

from odoo import fields
from odoo.tests import tagged

from odoo.addons.aite_pos_analytics.tests.common import PosAnalyticsCommon


@tagged('post_install', '-at_install', 'aite_direction')
class TestDirectionConsistency(PosAnalyticsCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.direction = cls.env['aite.direction.dashboard']
        cls.supplier = cls.env['res.partner'].create({
            'name': "Grossiste Cockpit", 'supplier_rank': 1,
        })
        cls.d_from = fields.Date.to_string(cls.today.replace(day=1))
        cls.d_to = fields.Date.to_string(cls.today)

    def _bill(self, amount, due_in_days):
        if not self.env['account.journal'].search([
                ('type', '=', 'purchase'),
                ('company_id', '=', self.env.company.id)], limit=1):
            self.skipTest("aucun journal d'achat (plan comptable absent)")
        bill = self.env['account.move'].create({
            'move_type': 'in_invoice',
            'partner_id': self.supplier.id,
            'invoice_date': self.today,
            'invoice_date_due': self.today + timedelta(days=due_in_days),
            'invoice_line_ids': [(0, 0, {
                'name': "Casiers de bière",
                'quantity': 1,
                'price_unit': amount,
                'tax_ids': [(5, 0, 0)],
            })],
        })
        bill.action_post()
        self.env.flush_all()
        return bill

    # ------------------------------------------------------------------
    # n° 23 (a) — une seule clé de mois pour les trois sources
    # ------------------------------------------------------------------

    def test_sales_and_purchases_share_the_current_month(self):
        self._sale([(self.beer, 4, 5000.0)])
        self._bill(80000.0, due_in_days=3)
        trends = self.direction.get_overview(
            self.d_from, self.d_to)['trends']
        self.assertLessEqual(len(trends), 6)
        months = [t['month'] for t in trends]
        self.assertEqual(len(months), len(set(months)),
                         "un mois ne doit apparaître qu'une fois")
        current = trends[-1]
        self.assertEqual(current['month'], self.today.strftime('%Y-%m'))
        self.assertGreaterEqual(current['ca'], 20000.0,
                                "le CA du mois doit tomber sur sa barre")
        self.assertGreaterEqual(current['bills'], 80000.0)

    # ------------------------------------------------------------------
    # n° 23 (b) — échéancier, balance âgée, ligne « Payer »
    # ------------------------------------------------------------------

    def test_supplier_schedule_reads_the_open_invoices(self):
        self._bill(50000.0, due_in_days=3)
        buckets = self.direction.get_overview(
            self.d_from, self.d_to)['supplier_buckets']
        self.assertGreaterEqual(buckets['schedule']['w0'], 50000.0,
                                "facture due dans 3 jours : cette semaine")
        self.assertGreaterEqual(buckets['aging']['0_30'], 50000.0)

        tab = self.direction.get_purchase_tab(self.d_from, self.d_to)
        self.assertIn("Grossiste Cockpit",
                      [r.get('partner') for r in tab['week_bills']])
        row = next(r for r in tab['week_bills']
                   if r.get('partner') == "Grossiste Cockpit")
        self.assertEqual(row['amount'], 50000.0)
        self.assertTrue(row['planned'])

    def test_actions_ask_to_pay_the_supplier_due_this_week(self):
        self._bill(60000.0, due_in_days=2)
        actions = self.direction.get_actions(self.d_from, self.d_to)
        labels = [r['label'] for s in actions['sections']
                  for r in s['rows']]
        self.assertIn("Payer Grossiste Cockpit", labels)

    def test_actions_write_dates_and_rates_in_french(self):
        """Écarts n° 37 et 41 (règle 6) : la liste « À traiter » écrivait
        l'échéance en AAAA-MM-JJ et les taux au point décimal (« 7.9 % »)."""
        self._bill(60000.0, due_in_days=2)
        actions = self.direction.get_actions(self.d_from, self.d_to)
        row = next(r for s in actions['sections'] for r in s['rows']
                   if r['label'] == "Payer Grossiste Cockpit")
        due = self.today + timedelta(days=2)
        self.assertEqual(row['hint'], due.strftime('%d/%m/%Y'))

        D = type(self.direction)
        out = D._build_actions({
            'coul_pct': 7.9, 'coul_seuil': 2.0, 'coul_amount': 1000.0,
            'rem_pct': 3.5, 'rem_amount': 500.0,
        })
        labels = [r['label'] for s in out['sections'] for r in s['rows']]
        # Une décimale fixe, comme le tableau de bord Stock affiche le
        # même seuil (« 2,0 % ») — reprise de l'écart n° 41.
        self.assertIn(
            "Coulage au-dessus du seuil (7,9\u00a0% > 2,0\u00a0%)", labels)
        self.assertIn("Remises élevées (3,5\u00a0% du CA)", labels)

    def test_actions_write_rates_and_words_like_the_source_screens(self):
        """Reprise des écarts n° 41 et 42 : la hausse de prix s'écrivait
        « +13 % » ici et « +12,5 % » dans les Achats ; « (3 réfs) » était
        abrégé."""
        D = type(self.direction)
        out = D._build_actions({
            'cmd_value': 45000.0, 'cmd_refs': 3,
            'price_up': [{'name': "Casier 65 cl", 'partner': "Brasseries",
                          'delta_pct': 12.5}],
        })
        rows = {r['label']: r for s in out['sections'] for r in s['rows']}
        self.assertIn("Lancer la commande suggérée (3 références)", rows)
        self.assertEqual(rows["Renégocier Casier 65 cl"]['hint'],
                         "+12,5\u00a0% · Brasseries")
        one = D._build_actions({'cmd_value': 9000.0, 'cmd_refs': 1})
        self.assertIn("Lancer la commande suggérée (1 référence)",
                      [r['label'] for s in one['sections']
                       for r in s['rows']])

    # ------------------------------------------------------------------
    # n° 24 — phrases d'état justes
    # ------------------------------------------------------------------

    def test_net_flow_sentence_follows_the_engine(self):
        """Le moteur Crédit calcule nouveaux − recouvré : un flux positif
        fait MONTER l'encours."""
        D = type(self.direction)
        self.assertIn("monte", D._net_flow_sentence(25000.0))
        self.assertIn("baisse", D._net_flow_sentence(-25000.0))
        self.assertIn("nouveaux − recouvré", D._net_flow_sentence(1.0))
        tab = self.direction.get_credit_tab(self.d_from, self.d_to)
        self.assertEqual(tab['net_flow_text'], D._net_flow_sentence(
            tab['kpis'].get('net_flow') or 0.0))

    def test_net_position_sentence_names_who_finances_whom(self):
        D = type(self.direction)
        net, side = D._net_position(500000.0, 100000.0)   # ardoises > dettes
        self.assertEqual(side, 'clients')
        self.assertIn("vous financez vos clients",
                      D._net_position_text(side))
        net, side = D._net_position(100000.0, 500000.0)   # dettes > ardoises
        self.assertIn("fournisseurs financent",
                      D._net_position_text(side))
        overview = self.direction.get_overview(self.d_from, self.d_to)
        self.assertEqual(overview['net_side_text'],
                         D._net_position_text(overview['net_side']))

    # ------------------------------------------------------------------
    # n° 25 — un chiffre, une valeur (cas K04)
    # ------------------------------------------------------------------

    def test_restaurant_revenue_is_the_same_on_every_screen(self):
        self._taxed_sale()
        overview = self.direction.get_overview(self.d_from, self.d_to)
        self.assertEqual(overview['pos']['ca'], 10000.0, "CA HT attendu")
        if 'aite.exec.dashboard' in self.env:
            exec_kpis = self.env['aite.exec.dashboard'].get_kpis(
                self.d_from, self.d_to)
            self.assertEqual(exec_kpis['pos_ca'], overview['pos']['ca'])
        self.session.invalidate_recordset()
        self.assertEqual(self.session.total_ca, overview['pos']['ca'])

    def test_hotel_revenue_is_the_same_on_every_screen(self):
        if 'aite.exec.dashboard' not in self.env:
            self.skipTest("tableau de bord exécutif absent")
        hotel = self.direction.get_overview(self.d_from, self.d_to)['hotel']
        exec_kpis = self.env['aite.exec.dashboard'].get_kpis(
            self.d_from, self.d_to)
        self.assertAlmostEqual(exec_kpis['hotel_ca'],
                               hotel['room_revenue'], places=2)

    def _taxed_sale(self):
        """Un ticket de 10 000 HT + 1 925 de TVA (19,25 %)."""
        order = self.env['pos.order'].create({
            'session_id': self.session.id,
            'company_id': self.company.id,
            'amount_tax': 1925.0,
            'amount_total': 11925.0,
            'amount_paid': 11925.0,
            'amount_return': 0.0,
            'lines': [(0, 0, {
                'product_id': self.beer.id,
                'qty': 2,
                'price_unit': 5000.0,
                'price_subtotal': 10000.0,
                'price_subtotal_incl': 11925.0,
            })],
        })
        self.env['pos.payment'].create({
            'pos_order_id': order.id,
            'payment_method_id': self.method_cash.id,
            'amount': 11925.0,
        })
        order.write({'state': 'paid'})
        self.env.flush_all()
        return order

    # ------------------------------------------------------------------
    # n° 27 — la carte heure × jour du cockpit lit le rapport POS
    # ------------------------------------------------------------------

    def test_pos_tab_heatmap_is_filled_by_the_sales(self):
        self._sale([(self.beer, 2, 5000.0)])
        report = self.env['aite.pos.daily.report'].search(
            [('config_id', '=', self.pos_config.id)], limit=1)
        heat = self.direction.get_pos_tab(self.d_from, self.d_to)['heatmap']
        cell = [h for h in heat if h['weekday'] == report.dow
                and h['hour'] == report.hour]
        self.assertTrue(cell, "la vente doit apparaître sur la carte")
        self.assertGreaterEqual(cell[0]['ca'], 10000.0)
