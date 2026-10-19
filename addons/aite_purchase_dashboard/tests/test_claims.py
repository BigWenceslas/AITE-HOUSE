# -*- coding: utf-8 -*-
"""Créances fournisseurs (409) : seuls les soldes débiteurs du compte
fournisseurs comptent — avoirs non imputés et paiements d'avance — jamais
le reste dû des factures ouvertes (soldes créditeurs, c'est la dette)."""
from odoo import fields
from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.tests import tagged


@tagged('post_install', '-at_install', 'aite_purchase')
class TestPurchaseClaims(AccountTestInvoicingCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.dashboard = cls.env['aite.purchase.dashboard']
        cls.supplier = cls.env['res.partner'].create({
            'name': "Brasserie Créances", 'supplier_rank': 1,
        })

    def _bill(self, move_type, amount):
        return self.init_invoice(
            move_type, partner=self.supplier,
            invoice_date=fields.Date.context_today(self.env.user),
            amounts=[amount], taxes=self.env['account.tax'], post=True)

    def _claims(self):
        self.env.flush_all()
        return self.dashboard.get_claims(supplier_id=self.supplier.id)

    def test_open_bill_is_a_debt_not_a_claim(self):
        """Une facture fournisseur non payée n'est pas une créance 409."""
        self._bill('in_invoice', 100000.0)
        claims = self._claims()
        self.assertEqual(claims['debit_total'], 0.0)
        self.assertEqual(claims['acomptes_est'], 0.0)
        self.assertEqual(claims['total'], 0.0)

    def test_advance_payment_is_a_claim(self):
        """Un paiement d'avance non lettré est une créance (4091)."""
        self._bill('in_invoice', 100000.0)
        payment = self.env['account.payment'].create({
            'payment_type': 'outbound',
            'partner_type': 'supplier',
            'partner_id': self.supplier.id,
            'amount': 50000.0,
            'journal_id': self.company_data['default_journal_bank'].id,
        })
        payment.action_post()
        claims = self._claims()
        self.assertEqual(claims['debit_total'], 50000.0)
        self.assertEqual(claims['acomptes_est'], 50000.0)
        self.assertEqual(claims['total'], 50000.0)

    def test_open_refund_is_counted_once(self):
        """Un avoir non imputé compte comme avoir, pas une seconde fois en acompte."""
        self._bill('in_refund', 30000.0)
        claims = self._claims()
        self.assertEqual(claims['avoirs_total'], 30000.0)
        self.assertEqual(claims['debit_total'], 30000.0)
        self.assertEqual(claims['acomptes_est'], 0.0)
        self.assertEqual(claims['total'], 30000.0)
