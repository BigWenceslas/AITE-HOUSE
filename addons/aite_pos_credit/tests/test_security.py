# -*- coding: utf-8 -*-
"""Droits d'accès du module Crédit clients."""
from odoo.exceptions import AccessError
from odoo.tests import tagged

from .common import CreditCommon


@tagged('post_install', '-at_install', 'aite_credit')
class TestCreditSecurity(CreditCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        base_group = cls.env.ref('base.group_user')
        cls.cashier = cls.env['res.users'].create({
            'name': "Caissier",
            'login': 'caissier.credit.test',
            'groups_id': [(6, 0, [
                base_group.id,
                cls.env.ref('aite_pos_credit.group_pos_credit_user').id,
            ])],
        })
        cls.credit_manager = cls.env['res.users'].create({
            'name': "Responsable crédit",
            'login': 'resp.credit.test',
            'groups_id': [(6, 0, [
                base_group.id,
                cls.env.ref('aite_pos_credit.group_pos_credit_manager').id,
            ])],
        })
        cls.outsider = cls.env['res.users'].create({
            'name': "Sans profil crédit",
            'login': 'outsider.credit.test',
            'groups_id': [(6, 0, [base_group.id])],
        })

    def test_cashier_opens_a_slate(self):
        credit = self.env['aite.pos.credit'].with_user(self.cashier).create({
            'partner_id': self.client_a.id,
            'company_id': self.company.id,
            'amount_total': 25000.0,
        })
        self.assertEqual(credit.amount_residual, 25000.0)

    def test_cashier_records_a_repayment_with_accounting_on(self):
        """Régression : encaisser déclenche une écriture 411.

        La résolution du journal et du compte client se faisait sans
        ``sudo`` — le caissier heurtait une AccessError.
        """
        self.company.pos_credit_auto_entries = True
        self.company.pos_credit_journal_id = False
        credit = self._credit(30000.0)
        payment = self.env['aite.pos.credit.payment'].with_user(
            self.cashier).create({
                'credit_id': credit.id,
                'amount': 12000.0,
                'method': 'cash',
            })
        self.assertEqual(payment.amount, 12000.0)
        self.assertTrue(payment.sudo().move_id)

    def test_cashier_cannot_delete_a_slate(self):
        credit = self._credit()
        with self.assertRaises(AccessError):
            credit.with_user(self.cashier).unlink()

    def test_cashier_cannot_delete_a_repayment(self):
        credit = self._credit(30000.0)
        payment = self._repay(credit, 10000.0)
        with self.assertRaises(AccessError):
            payment.with_user(self.cashier).unlink()

    def test_manager_deletes_a_slate(self):
        credit = self._credit()
        credit.with_user(self.credit_manager).unlink()
        self.assertFalse(credit.exists())

    def test_outsider_sees_nothing(self):
        with self.assertRaises(AccessError):
            self.env['aite.pos.credit'].with_user(self.outsider).search([])
