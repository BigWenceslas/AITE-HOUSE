# -*- coding: utf-8 -*-
"""Cockpit Direction : il orchestre les quatre moteurs spécialisés.

L'enjeu du module est la **cohérence** : les chiffres affichés doivent
être exactement ceux des tableaux de bord POS, Crédit, Stock et Achats,
sans formule dupliquée.
"""
from datetime import timedelta

from odoo import fields
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install', 'aite_direction')
class TestDirectionDashboard(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.env.user.tz = 'UTC'
        cls.direction = cls.env['aite.direction.dashboard']
        cls.pos = cls.env['aite.pos.dashboard']
        cls.credit = cls.env['aite.pos.credit.dashboard']
        cls.stock = cls.env['aite.stock.dashboard']
        cls.purchase = cls.env['aite.purchase.dashboard']
        cls.today = fields.Date.context_today(cls.env.user)

        cls.client = cls.env['res.partner'].create({
            'name': "Client Direction",
        })

    def setUp(self):
        super().setUp()
        # Société dédiée : le cockpit consolide toute la société, un jeu
        # de démonstration en base fausserait les totaux attendus.
        self.company = self.env['res.company'].create({
            'name': "Société Direction (test)",
        })
        self.env.user.write({
            'company_ids': [(4, self.company.id)],
            'company_id': self.company.id,
        })
        self.env = self.env(context=dict(
            self.env.context, allowed_company_ids=[self.company.id]))
        self.client = self.client.with_env(self.env)
        for name in ('direction', 'pos', 'credit', 'stock', 'purchase'):
            setattr(self, name, getattr(self, name).with_env(self.env))
        self.d_from = fields.Date.to_string(self.today - timedelta(days=30))
        self.d_to = fields.Date.to_string(self.today)

    def _endpoints(self, date_from, date_to):
        d = self.direction
        return [
            ('get_meta', lambda: d.get_meta()),
            ('get_overview', lambda: d.get_overview(date_from, date_to)),
            ('get_pos_tab', lambda: d.get_pos_tab(date_from, date_to)),
            ('get_credit_tab', lambda: d.get_credit_tab(date_from, date_to)),
            ('get_stock_tab', lambda: d.get_stock_tab(date_from, date_to)),
            ('get_purchase_tab',
             lambda: d.get_purchase_tab(date_from, date_to)),
            ('get_actions', lambda: d.get_actions(date_from, date_to)),
        ]

    # ------------------------------------------------------------------
    # Robustesse
    # ------------------------------------------------------------------

    def test_every_tab_answers(self):
        for name, call in self._endpoints(self.d_from, self.d_to):
            with self.subTest(endpoint=name):
                self.assertIsNotNone(call(), "%s ne renvoie rien" % name)

    def test_every_tab_answers_on_an_empty_period(self):
        far = fields.Date.to_string(self.today - timedelta(days=900))
        near = fields.Date.to_string(self.today - timedelta(days=895))
        for name, call in self._endpoints(far, near):
            with self.subTest(endpoint=name):
                self.assertIsNotNone(call(), "%s ne renvoie rien" % name)

    # ------------------------------------------------------------------
    # Cohérence avec les moteurs spécialisés
    # ------------------------------------------------------------------

    def test_credit_tab_matches_the_credit_dashboard(self):
        """Le cockpit ne doit pas recalculer l'encours à sa façon."""
        self.env['aite.pos.credit'].create({
            'partner_id': self.client.id,
            'company_id': self.env.company.id,
            'amount_total': 45000.0,
        })
        self.env.flush_all()
        direct = self.credit.get_kpis(self.d_from, self.d_to)
        tab = self.direction.get_credit_tab(self.d_from, self.d_to)
        self.assertEqual(tab['kpis']['outstanding'], direct['outstanding'])
        self.assertEqual(tab['kpis']['debtor_count'],
                         direct['debtor_count'])
        # La balance âgée doit se réconcilier avec l'encours affiché.
        self.assertAlmostEqual(
            sum(b['amount'] for b in tab['aging']),
            tab['kpis']['outstanding'], places=2)

    def test_stock_tab_matches_the_stock_dashboard(self):
        direct = self.stock.get_kpis(self.d_from, self.d_to)
        tab = self.direction.get_stock_tab(self.d_from, self.d_to)
        for key in ('total_value', 'rupt_count', 'refs_count'):
            self.assertEqual(tab['kpis'][key], direct[key],
                             "divergence sur %s" % key)

    def test_pos_tab_matches_the_pos_dashboard(self):
        direct = self.pos.get_kpis(self.d_from, self.d_to)
        tab = self.direction.get_pos_tab(self.d_from, self.d_to)
        for key in ('ca', 'margin', 'cost', 'order_count'):
            self.assertEqual(tab['kpis'][key], direct[key],
                             "divergence sur %s" % key)

    def test_purchase_tab_matches_the_purchase_dashboard(self):
        direct = self.purchase.get_kpis(self.d_from, self.d_to)
        tab = self.direction.get_purchase_tab(self.d_from, self.d_to)
        common = set(tab.get('kpis', {})) & set(direct)
        self.assertTrue(common, "le cockpit doit exposer les KPI achats")
        for key in common:
            self.assertEqual(tab['kpis'][key], direct[key],
                             "divergence sur %s" % key)

    def test_overview_aggregates_the_four_poles(self):
        overview = self.direction.get_overview(self.d_from, self.d_to)
        self.assertIsInstance(overview, dict)
        self.assertTrue(overview)

    def test_mirror_aging_spreads_across_the_buckets(self):
        """Régression : la balance âgée en miroir rangeait tout en +90 j.

        Le cockpit reventilait les tranches d'après ``min``/``max``, que
        le moteur Crédit ne renvoyait pas : ``max`` valant None, la règle
        « pas de borne haute ⇒ +90 j » s'appliquait à TOUTES les lignes.
        Le gérant voyait alors 100 % de son encours comme critique.
        """
        today = fields.Date.context_today(self.env.user)
        # Une ardoise par tranche d'ancienneté.
        for days, amount in ((5, 10000.0), (40, 20000.0),
                             (75, 30000.0), (150, 40000.0)):
            self.env['aite.pos.credit'].create({
                'partner_id': self.client.id,
                'company_id': self.env.company.id,
                'amount_total': amount,
                'date_open': today - timedelta(days=days),
            })
        self.env.flush_all()

        overview = self.direction.get_overview(self.d_from, self.d_to)
        aging = overview['aging_clients']
        self.assertEqual(aging['0_30'], 10000.0)
        self.assertEqual(aging['31_60'], 20000.0)
        self.assertEqual(aging['61_90'], 30000.0)
        self.assertEqual(aging['90p'], 40000.0)

    def test_credit_engine_exposes_bucket_keys(self):
        """Le contrat que consomme le cockpit : clé + bornes."""
        for bucket in self.credit.get_aging():
            for key in ('key', 'label', 'min', 'max', 'amount', 'count'):
                self.assertIn(key, bucket)
        keys = [b['key'] for b in self.credit.get_aging()]
        self.assertEqual(keys, ['0_30', '31_60', '61_90', '90p'])

    def test_actions_list_is_ordered_and_typed(self):
        self.env['aite.pos.credit'].create({
            'partner_id': self.client.id,
            'company_id': self.env.company.id,
            'amount_total': 90000.0,
            'date_open': self.today - timedelta(days=120),
        })
        self.env.flush_all()
        actions = self.direction.get_actions(self.d_from, self.d_to)
        self.assertIn('sections', actions)
        titles = {s['title'] for s in actions['sections']}
        self.assertIn("Ardoises anciennes", titles,
                      "une ardoise de 120 jours doit remonter à traiter")
        for section in actions['sections']:
            for key in ('key', 'title', 'priority', 'source', 'rows'):
                self.assertIn(key, section)

    def test_meta_payload(self):
        meta = self.direction.get_meta()
        self.assertIsInstance(meta, dict)
        self.assertTrue(meta)
