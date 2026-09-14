# -*- coding: utf-8 -*-
"""Segmentation VIP / VVIP : règle de statut et recalcul de la fenêtre."""
from datetime import date, timedelta

from dateutil.relativedelta import relativedelta

from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install', 'aite_loyalty')
class TestLoyaltySegmentation(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.engine = cls.env['aite.loyalty.engine']
        cls.company.write({
            'aite_loyalty_rate_per_1000': 1.0,
            'aite_loyalty_min_amount': 1000.0,
            'aite_loyalty_window_months': 12,
            'aite_loyalty_vip_min_spend': 500000.0,
            'aite_loyalty_vip_min_visits': 10,
            'aite_loyalty_vvip_min_spend': 2000000.0,
            'aite_loyalty_vvip_min_visits': 25,
            'aite_loyalty_vvip_min_domains': 3,
        })
        cls.cfg = cls.engine._cfg(cls.company)

    def _partner(self, name):
        return self.env['res.partner'].create({'name': name})

    def _moves(self, partner, count, amount, origin='pos', start_days=1):
        """``count`` mouvements sur des jours distincts."""
        Move = self.env['aite.loyalty.move']
        today = date.today()
        for i in range(count):
            Move.create({
                'partner_id': partner.id,
                'company_id': self.company.id,
                'date': today - timedelta(days=start_days + i),
                'points': max(1, int(amount / 1000)),
                'amount_base': amount,
                'origin_detail': origin,
            })

    # ------------------------------------------------------------------
    # Règle de statut (fonction pure)
    # ------------------------------------------------------------------

    def test_standard_by_default(self):
        self.assertEqual(
            self.engine._tier_for(0.0, 0, 0, self.cfg), 'standard')

    def test_vip_needs_spend_and_visits(self):
        self.assertEqual(
            self.engine._tier_for(600000.0, 12, 1, self.cfg), 'vip')

    def test_spend_without_visits_stays_standard(self):
        self.assertEqual(
            self.engine._tier_for(5000000.0, 3, 5, self.cfg), 'standard')

    def test_visits_without_spend_stays_standard(self):
        self.assertEqual(
            self.engine._tier_for(10000.0, 50, 5, self.cfg), 'standard')

    def test_vvip_needs_the_third_criterion(self):
        self.assertEqual(
            self.engine._tier_for(3000000.0, 30, 3, self.cfg), 'vvip')

    def test_vvip_without_diversity_falls_back_to_vip(self):
        """Dépenses et visites VVIP mais un seul domaine ⇒ VIP."""
        self.assertEqual(
            self.engine._tier_for(3000000.0, 30, 1, self.cfg), 'vip')

    def test_thresholds_are_inclusive(self):
        self.assertEqual(
            self.engine._tier_for(500000.0, 10, 0, self.cfg), 'vip')
        self.assertEqual(
            self.engine._tier_for(2000000.0, 25, 3, self.cfg), 'vvip')

    def test_just_below_threshold_is_refused(self):
        self.assertEqual(
            self.engine._tier_for(499999.0, 10, 0, self.cfg), 'standard')
        self.assertEqual(
            self.engine._tier_for(1999999.0, 25, 3, self.cfg), 'vip')

    # ------------------------------------------------------------------
    # Recalcul sur la fenêtre glissante
    # ------------------------------------------------------------------

    def test_recompute_promotes_to_vip(self):
        partner = self._partner("Futur VIP")
        # 12 visites de 50 000 = 600 000 sur 12 jours distincts.
        self._moves(partner, 12, 50000.0)
        self.engine.recompute_tiers(partner_ids=[partner.id])
        partner.invalidate_recordset()
        self.assertEqual(partner.loyalty_tier, 'vip')
        self.assertEqual(partner.loyalty_tier_date, date.today())

    def test_recompute_promotes_to_vvip_with_three_domains(self):
        partner = self._partner("Futur VVIP")
        self._moves(partner, 9, 80000.0, origin='pos', start_days=1)
        self._moves(partner, 9, 80000.0, origin='hotel', start_days=20)
        self._moves(partner, 9, 80000.0, origin='slot_spa', start_days=40)
        self.engine.recompute_tiers(partner_ids=[partner.id])
        partner.invalidate_recordset()
        self.assertEqual(partner.loyalty_tier, 'vvip')

    def test_manual_moves_do_not_count_as_a_domain(self):
        """Un ajustement manuel ne crée pas de diversité artificielle."""
        partner = self._partner("Ajusté")
        self._moves(partner, 13, 80000.0, origin='pos', start_days=1)
        self._moves(partner, 13, 80000.0, origin='manual', start_days=20)
        self.engine.recompute_tiers(partner_ids=[partner.id])
        partner.invalidate_recordset()
        # Dépenses et visites VVIP atteintes, mais un seul vrai domaine.
        self.assertEqual(partner.loyalty_tier, 'vip')

    def test_visits_are_distinct_days_not_transactions(self):
        """Trois passages le même jour comptent pour une visite."""
        partner = self._partner("Habitué du jour")
        Move = self.env['aite.loyalty.move']
        same_day = date.today() - timedelta(days=1)
        for _i in range(30):
            Move.create({
                'partner_id': partner.id,
                'company_id': self.company.id,
                'date': same_day,
                'points': 50,
                'amount_base': 50000.0,
                'origin_detail': 'pos',
            })
        self.engine.recompute_tiers(partner_ids=[partner.id])
        partner.invalidate_recordset()
        # 1 500 000 dépensés mais une seule visite ⇒ pas de statut.
        self.assertEqual(partner.loyalty_tier, 'standard')

    def test_activity_outside_the_window_is_ignored(self):
        partner = self._partner("Ancien VIP")
        Move = self.env['aite.loyalty.move']
        old = date.today() - relativedelta(months=18)
        for i in range(12):
            Move.create({
                'partner_id': partner.id,
                'company_id': self.company.id,
                'date': old + timedelta(days=i),
                'points': 50,
                'amount_base': 50000.0,
                'origin_detail': 'pos',
            })
        self.engine.recompute_tiers(partner_ids=[partner.id])
        partner.invalidate_recordset()
        self.assertEqual(partner.loyalty_tier, 'standard')

    def test_inactive_vip_is_demoted(self):
        """Un VIP sans activité sur la fenêtre repasse Standard."""
        partner = self._partner("VIP dormant")
        partner.loyalty_tier = 'vip'
        self.engine.recompute_tiers(partner_ids=[partner.id])
        partner.invalidate_recordset()
        self.assertEqual(partner.loyalty_tier, 'standard')

    def test_recompute_is_idempotent(self):
        partner = self._partner("VIP stable")
        self._moves(partner, 12, 50000.0)
        self.engine.recompute_tiers(partner_ids=[partner.id])
        partner.invalidate_recordset()
        first_date = partner.loyalty_tier_date
        self.engine.recompute_tiers(partner_ids=[partner.id])
        partner.invalidate_recordset()
        self.assertEqual(partner.loyalty_tier, 'vip')
        self.assertEqual(partner.loyalty_tier_date, first_date)

    def test_recompute_scoped_to_given_partners(self):
        a = self._partner("Ciblé")
        b = self._partner("Non ciblé")
        self._moves(a, 12, 50000.0)
        self._moves(b, 12, 50000.0)
        self.engine.recompute_tiers(partner_ids=[a.id])
        (a | b).invalidate_recordset()
        self.assertEqual(a.loyalty_tier, 'vip')
        self.assertEqual(b.loyalty_tier, 'standard')
