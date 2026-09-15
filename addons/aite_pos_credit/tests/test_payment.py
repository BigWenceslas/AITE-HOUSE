# -*- coding: utf-8 -*-
"""Remboursements d'ardoise : contrôles, écritures, assistant."""
from odoo.exceptions import UserError, ValidationError
from odoo.tests import tagged

from .common import CreditCommon


@tagged('post_install', '-at_install', 'aite_credit')
class TestCreditPayment(CreditCommon):

    # ------------------------------------------------------------------
    # Contrôles
    # ------------------------------------------------------------------

    def test_amount_must_be_positive(self):
        credit = self._credit(50000.0)
        with self.assertRaises(ValidationError):
            self._repay(credit, 0.0)

    def test_overpayment_is_refused(self):
        credit = self._credit(50000.0)
        with self.assertRaises(ValidationError):
            self._repay(credit, 50001.0)

    def test_rounding_tolerance_is_accepted(self):
        """Un écart d'arrondi infime ne bloque pas l'encaissement."""
        credit = self._credit(50000.0)
        payment = self._repay(credit, 50000.005)
        self.assertTrue(payment)

    def test_tolerance_stops_at_one_cent(self):
        """Au-delà du centime, le dépassement est refusé."""
        credit = self._credit(50000.0)
        with self.assertRaises(ValidationError):
            self._repay(credit, 50000.5)

    def test_cumulated_overpayment_is_refused(self):
        credit = self._credit(50000.0)
        self._repay(credit, 30000.0)
        with self.assertRaises(ValidationError):
            self._repay(credit, 25000.0)

    def test_cancelled_payment_frees_the_ceiling(self):
        credit = self._credit(50000.0)
        first = self._repay(credit, 50000.0)
        first.action_cancel()
        credit.invalidate_recordset()
        second = self._repay(credit, 50000.0)
        self.assertEqual(second.amount, 50000.0)

    def test_collected_by_defaults_to_current_user(self):
        credit = self._credit()
        payment = self._repay(credit, 1000.0)
        self.assertEqual(payment.collected_by, self.env.user)

    def test_all_payment_methods_are_accepted(self):
        for method in ('mtn', 'orange', 'cash', 'card', 'transfer'):
            credit = self._credit(10000.0)
            payment = self._repay(credit, 10000.0, method=method)
            self.assertEqual(payment.method, method)

    # ------------------------------------------------------------------
    # Comptabilité
    # ------------------------------------------------------------------

    def test_entry_is_posted_when_enabled(self):
        self.company.pos_credit_auto_entries = True
        self.company.pos_credit_journal_id = self.cash_journal
        credit = self._credit(40000.0)
        payment = self._repay(credit, 40000.0)
        self.assertTrue(payment.move_id)
        self.assertEqual(payment.move_id.state, 'posted')
        receivable = payment.move_id.line_ids.filtered(
            lambda l: l.account_id.account_type == 'asset_receivable')
        self.assertEqual(sum(receivable.mapped('credit')), 40000.0)
        treasury = payment.move_id.line_ids - receivable
        self.assertEqual(sum(treasury.mapped('debit')), 40000.0)

    def test_entry_is_balanced(self):
        self.company.pos_credit_auto_entries = True
        self.company.pos_credit_journal_id = self.cash_journal
        credit = self._credit(25000.0)
        payment = self._repay(credit, 25000.0)
        lines = payment.move_id.line_ids
        self.assertEqual(sum(lines.mapped('debit')),
                         sum(lines.mapped('credit')))

    def test_no_entry_when_disabled(self):
        self.company.pos_credit_auto_entries = False
        credit = self._credit(40000.0)
        payment = self._repay(credit, 40000.0)
        self.assertFalse(payment.move_id)

    def test_incomplete_configuration_does_not_block(self):
        """Sans journal exploitable, l'encaissement passe quand même."""
        self.company.pos_credit_auto_entries = True
        self.company.pos_credit_journal_id = False
        credit = self._credit(40000.0)
        payment = self._repay(credit, 40000.0, method='transfer')
        self.assertEqual(payment.state, 'posted')
        self.assertEqual(credit.amount_residual, 0.0)

    def test_cancel_reverses_the_entry(self):
        self.company.pos_credit_auto_entries = True
        self.company.pos_credit_journal_id = self.cash_journal
        credit = self._credit(30000.0)
        payment = self._repay(credit, 30000.0)
        move = payment.move_id
        payment.action_cancel()
        self.assertEqual(payment.state, 'cancelled')
        self.assertIn(move.state, ('draft', 'cancel'))

    def test_journal_selection_follows_the_method(self):
        """Espèces → journal de caisse ; autres → journal de banque."""
        self.company.pos_credit_journal_id = False
        credit = self._credit(10000.0)
        cash_payment = self.env['aite.pos.credit.payment'].new({
            'credit_id': credit.id, 'amount': 1000.0, 'method': 'cash',
        })
        self.assertEqual(cash_payment._journal_for_method().type, 'cash')
        card_payment = self.env['aite.pos.credit.payment'].new({
            'credit_id': credit.id, 'amount': 1000.0, 'method': 'card',
        })
        self.assertEqual(card_payment._journal_for_method().type, 'bank')

    # ------------------------------------------------------------------
    # Assistant de remboursement
    # ------------------------------------------------------------------

    def test_wizard_creates_the_payment(self):
        credit = self._credit(60000.0)
        wizard = self.env['aite.pos.credit.repay.wizard'].create({
            'credit_id': credit.id,
            'amount': 25000.0,
            'method': 'mtn',
            'transaction_ref': 'MOMO-42',
        })
        wizard.action_confirm()
        self.assertEqual(credit.amount_paid, 25000.0)
        self.assertEqual(credit.payment_ids.transaction_ref, 'MOMO-42')

    def test_wizard_caps_at_residual(self):
        """Saisir plus que le reste dû n'entraîne pas de sur-imputation."""
        credit = self._credit(30000.0)
        wizard = self.env['aite.pos.credit.repay.wizard'].create({
            'credit_id': credit.id,
            'amount': 999999.0,
            'method': 'cash',
        })
        wizard.action_confirm()
        self.assertEqual(credit.amount_paid, 30000.0)
        self.assertEqual(credit.amount_residual, 0.0)

    def test_wizard_refuses_zero(self):
        credit = self._credit(30000.0)
        wizard = self.env['aite.pos.credit.repay.wizard'].create({
            'credit_id': credit.id, 'amount': 0.0, 'method': 'cash',
        })
        with self.assertRaises(UserError):
            wizard.action_confirm()

    def test_wizard_refuses_a_settled_slate(self):
        credit = self._credit(30000.0)
        self._repay(credit, 30000.0)
        credit.invalidate_recordset()
        wizard = self.env['aite.pos.credit.repay.wizard'].create({
            'credit_id': credit.id, 'amount': 5000.0, 'method': 'cash',
        })
        with self.assertRaises(UserError):
            wizard.action_confirm()

    def test_wizard_warns_above_residual(self):
        credit = self._credit(30000.0)
        wizard = self.env['aite.pos.credit.repay.wizard'].new({
            'credit_id': credit.id, 'amount': 50000.0, 'method': 'cash',
        })
        warning = wizard._onchange_amount_cap()
        self.assertIn('warning', warning)
