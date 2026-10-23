# -*- coding: utf-8 -*-
"""Cockpit Direction : contrats avec les moteurs (relecture croisée).

* « À payer sous N j » (moteur Achats, réglage ``soon``) et l'échéancier,
  la liste « Échéances » et les lignes « Payer … » de « À traiter » disent
  la même chose : une facture due dans exactement 7 jours était dans la
  carte, absente de la barre « Sous 7 jours », de la liste et des actions.
* Seuil de 30 jours : borne basse incluse, haute exclue, comme le moteur
  Crédit — une facture fournisseur de 30 jours est en « 30–60 j » comme
  une ardoise de 30 jours, et un débiteur de 30 jours est à relancer.
* Onglet Crédit : le filtre d'origine (Point de vente / Ventes) s'applique
  aussi aux « Derniers remboursements ».
* Libellés des mois en abréviations françaises (« janv. », « sept. »).
"""
from datetime import timedelta
from unittest.mock import patch

from odoo import fields
from odoo.tests import tagged

from odoo.addons.aite_pos_analytics.tests.common import PosAnalyticsCommon


@tagged('post_install', '-at_install', 'aite_direction')
class TestDirectionRelecture(PosAnalyticsCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.direction = cls.env['aite.direction.dashboard']
        cls.supplier = cls.env['res.partner'].create({
            'name': "Fournisseur Échéances", 'supplier_rank': 1,
        })
        cls.d_from = fields.Date.to_string(cls.today.replace(day=1))
        cls.d_to = fields.Date.to_string(cls.today)

    def _bill(self, amount, due_in_days, invoice_days_ago=0):
        if not self.env['account.journal'].search([
                ('type', '=', 'purchase'),
                ('company_id', '=', self.env.company.id)], limit=1):
            self.skipTest("aucun journal d'achat (plan comptable absent)")
        bill = self.env['account.move'].create({
            'move_type': 'in_invoice',
            'partner_id': self.supplier.id,
            'invoice_date': self.today - timedelta(days=invoice_days_ago),
            'invoice_date_due': self.today + timedelta(days=due_in_days),
            'invoice_line_ids': [(0, 0, {
                'name': "Casiers",
                'quantity': 1,
                'price_unit': amount,
                'tax_ids': [(5, 0, 0)],
            })],
        })
        bill.action_post()
        self.env.flush_all()
        return bill

    def _mine(self, rows):
        return [r for r in rows if r.get('partner') == self.supplier.name]

    def _payer_rows(self, actions):
        rows = []
        for section in actions['sections']:
            if section['key'] == 'purchase':
                rows += [r for r in section['rows']
                         if r['label'] == "Payer %s" % self.supplier.name]
        return rows

    # ------------------------------------------------------------------
    # Échéances fournisseurs : une seule définition (moteur Achats)
    # ------------------------------------------------------------------

    def test_bill_due_in_seven_days_is_everywhere_with_the_default(self):
        self.env.company.aite_purchase_due_soon_days = 7
        self._bill(100000.0, due_in_days=7)
        tab = self.direction.get_purchase_tab(self.d_from, self.d_to)
        self.assertGreaterEqual(tab['kpis']['soon'], 100000.0, "carte")
        self.assertGreaterEqual(tab['buckets']['schedule']['w0'], 100000.0,
                                "barre « Sous 7 jours »")
        self.assertEqual(len(self._mine(tab['week_bills'])), 1, "liste")
        self.assertEqual(tab['soon_days'], 7)
        actions = self.direction.get_actions(self.d_from, self.d_to)
        self.assertEqual(len(self._payer_rows(actions)), 1, "À traiter")

    def test_bills_follow_a_fourteen_day_setting(self):
        self.env.company.aite_purchase_due_soon_days = 14
        self._bill(100000.0, due_in_days=7)
        self._bill(70000.0, due_in_days=10)
        self._bill(50000.0, due_in_days=20)   # hors fenêtre
        tab = self.direction.get_purchase_tab(self.d_from, self.d_to)
        self.assertEqual(tab['soon_days'], 14)
        mine = self._mine(tab['week_bills'])
        self.assertEqual(sorted(r['amount'] for r in mine),
                         [70000.0, 100000.0])
        sched = tab['buckets']['schedule']
        # Les barres « Sous 7 jours » + « Dans 8 à 14 jours » couvrent la
        # carte « À payer sous 14 j ».
        self.assertGreaterEqual(sched['w0'], 100000.0)
        self.assertGreaterEqual(sched['w1'], 70000.0)
        actions = self.direction.get_actions(self.d_from, self.d_to)
        self.assertEqual(len(self._payer_rows(actions)), 2)

    # ------------------------------------------------------------------
    # Seuil de 30 jours
    # ------------------------------------------------------------------

    def test_supplier_invoice_of_thirty_days_is_in_the_second_band(self):
        self._bill(150000.0, due_in_days=30, invoice_days_ago=30)
        aging = self.direction.get_overview(
            self.d_from, self.d_to)['supplier_buckets']['aging']
        self.assertGreaterEqual(aging['31_60'], 150000.0)

    # ------------------------------------------------------------------
    # Filtre d'origine transmis aux derniers remboursements
    # ------------------------------------------------------------------

    def test_origin_filter_reaches_the_recent_payments(self):
        Engine = type(self.env['aite.pos.credit.dashboard'])
        seen = {}
        original = Engine.get_recent_payments

        def spy(engine, *args, **kwargs):
            seen.update(kwargs)
            return original(engine, *args, **kwargs)
        with patch.object(Engine, 'get_recent_payments', spy):
            self.direction.get_credit_tab(self.d_from, self.d_to,
                                          source='sale')
        self.assertEqual(seen.get('source'), 'sale')

    # ------------------------------------------------------------------
    # Mois en français
    # ------------------------------------------------------------------

    def test_month_labels_are_french_abbreviations(self):
        D = type(self.direction)
        self.assertEqual(D._month_label('2026-01'), "janv.")
        self.assertEqual(D._month_label('2026-09'), "sept.")
        self.assertEqual(D._month_label('2026-05'), "mai")
