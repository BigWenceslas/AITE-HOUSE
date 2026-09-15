# -*- coding: utf-8 -*-
"""Moteur de fidélité : barème de points, grand livre, ajustements."""
from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install', 'aite_loyalty')
class TestLoyaltyEngine(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.engine = cls.env['aite.loyalty.engine']
        cls.partner = cls.env['res.partner'].create({
            'name': "Client Fidèle",
        })
        cls.company.write({
            'aite_loyalty_rate_per_1000': 1.0,
            'aite_loyalty_min_amount': 1000.0,
        })

    # ------------------------------------------------------------------
    # Barème (fonction pure)
    # ------------------------------------------------------------------

    def test_points_are_floored(self):
        """1 point par tranche de 1 000 entamée… non : tranche pleine."""
        self.assertEqual(self.engine._points_for(1999.0, 1.0, 0.0), 1)
        self.assertEqual(self.engine._points_for(2000.0, 1.0, 0.0), 2)

    def test_points_scale_with_the_rate(self):
        self.assertEqual(self.engine._points_for(10000.0, 2.5, 0.0), 25)

    def test_amount_below_minimum_earns_nothing(self):
        self.assertEqual(self.engine._points_for(500.0, 1.0, 1000.0), 0)

    def test_amount_at_minimum_earns_points(self):
        self.assertEqual(self.engine._points_for(1000.0, 1.0, 1000.0), 1)

    def test_zero_and_negative_amounts_earn_nothing(self):
        self.assertEqual(self.engine._points_for(0.0, 1.0, 0.0), 0)
        self.assertEqual(self.engine._points_for(-5000.0, 1.0, 0.0), 0)

    def test_zero_rate_earns_nothing(self):
        self.assertEqual(self.engine._points_for(100000.0, 0.0, 0.0), 0)

    def test_none_values_are_tolerated(self):
        self.assertEqual(self.engine._points_for(None, None, None), 0)

    # ------------------------------------------------------------------
    # Attribution
    # ------------------------------------------------------------------

    def test_award_creates_a_ledger_move(self):
        move = self.engine.award(self.partner, 50000.0, 'pos', ref='POS/001')
        self.assertTrue(move)
        self.assertEqual(move.points, 50)
        self.assertEqual(move.amount_base, 50000.0)
        self.assertEqual(move.origin_detail, 'pos')
        self.assertEqual(move.ref, 'POS/001')

    def test_award_below_minimum_creates_nothing(self):
        move = self.engine.award(self.partner, 500.0, 'pos')
        self.assertFalse(move)

    def test_award_without_partner_creates_nothing(self):
        move = self.engine.award(
            self.env['res.partner'], 50000.0, 'pos')
        self.assertFalse(move)

    def test_partner_balance_follows_the_ledger(self):
        self.engine.award(self.partner, 50000.0, 'pos')
        self.engine.award(self.partner, 30000.0, 'hotel')
        self.partner.invalidate_recordset()
        self.assertEqual(self.partner.loyalty_points, 80)
        self.assertEqual(self.partner.loyalty_move_count, 2)

    def test_deleting_a_move_updates_the_balance(self):
        move = self.engine.award(self.partner, 50000.0, 'pos')
        self.partner.invalidate_recordset()
        self.assertEqual(self.partner.loyalty_points, 50)
        move.unlink()
        self.partner.invalidate_recordset()
        self.assertEqual(self.partner.loyalty_points, 0)

    def test_every_origin_is_accepted(self):
        for origin in ('pos', 'hotel', 'slot_space', 'slot_spa',
                       'slot_hair', 'slot_pressing', 'manual'):
            move = self.engine.award(self.partner, 10000.0, origin)
            self.assertEqual(move.origin_detail, origin)

    def test_award_honours_company_settings(self):
        self.company.aite_loyalty_rate_per_1000 = 5.0
        move = self.engine.award(self.partner, 10000.0, 'pos')
        self.assertEqual(move.points, 50)

    # ------------------------------------------------------------------
    # Ajustement manuel
    # ------------------------------------------------------------------

    def test_manual_credit(self):
        wizard = self.env['aite.loyalty.adjust.wizard'].create({
            'partner_id': self.partner.id,
            'points': 100,
            'note': "Geste commercial",
        })
        wizard.action_apply()
        self.partner.invalidate_recordset()
        self.assertEqual(self.partner.loyalty_points, 100)
        move = self.partner.loyalty_move_ids
        self.assertEqual(move.origin_detail, 'manual')
        self.assertEqual(move.note, "Geste commercial")

    def test_manual_debit(self):
        self.engine.award(self.partner, 100000.0, 'pos')  # 100 pts
        self.partner.invalidate_recordset()
        wizard = self.env['aite.loyalty.adjust.wizard'].create({
            'partner_id': self.partner.id,
            'points': -40,
            'note': "Utilisation d'une récompense",
        })
        wizard.action_apply()
        self.partner.invalidate_recordset()
        self.assertEqual(self.partner.loyalty_points, 60)

    def test_manual_adjustment_cannot_go_negative(self):
        wizard = self.env['aite.loyalty.adjust.wizard'].create({
            'partner_id': self.partner.id,
            'points': -50,
            'note': "Retrait abusif",
        })
        with self.assertRaises(UserError):
            wizard.action_apply()

    def test_manual_adjustment_refuses_zero(self):
        wizard = self.env['aite.loyalty.adjust.wizard'].create({
            'partner_id': self.partner.id,
            'points': 0,
            'note': "Rien",
        })
        with self.assertRaises(UserError):
            wizard.action_apply()

    def test_partner_action_lists_its_moves(self):
        self.engine.award(self.partner, 50000.0, 'pos')
        action = self.partner.action_view_loyalty_moves()
        self.assertEqual(action['res_model'], 'aite.loyalty.move')
        self.assertIn(('partner_id', '=', self.partner.id), action['domain'])
