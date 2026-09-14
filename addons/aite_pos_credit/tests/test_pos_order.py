# -*- coding: utf-8 -*-
"""Génération d'ardoise depuis une commande POS (paiement mixte compris)."""
from odoo.exceptions import UserError
from odoo.tests import tagged

from .common import CreditCommon


@tagged('post_install', '-at_install', 'aite_credit')
class TestPosOrderCredit(CreditCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.pos_config = cls.env['pos.config'].create({
            'name': "Caisse test ardoise",
        })
        cls.product = cls.env['product.product'].create({
            'name': "Article test crédit",
            'type': 'consu',
            'available_in_pos': True,
            'list_price': 50000.0,
            'taxes_id': [(5, 0, 0)],
        })
        # Journal dédié : un journal de caisse ne peut servir qu'à un
        # seul moyen de paiement « espèces », et la base peut déjà en
        # porter un (jeu de démonstration).
        cls.own_cash_journal = cls.env['account.journal'].create({
            'name': "Caisse ardoise (test)",
            'type': 'cash',
            'code': 'CARTS',
            'company_id': cls.company.id,
        })
        cls.method_cash = cls.env['pos.payment.method'].create({
            'name': "Espèces test",
            'journal_id': cls.own_cash_journal.id,
            'company_id': cls.company.id,
        })
        cls.method_credit = cls.env['pos.payment.method'].create({
            'name': "Ardoise test",
            'is_aite_credit': True,
            'company_id': cls.company.id,
        })
        cls.pos_config.write({
            'payment_method_ids': [
                (6, 0, (cls.method_cash | cls.method_credit).ids)],
        })
        cls.pos_config.open_ui()
        cls.session = cls.pos_config.current_session_id

    def _order(self, payments, partner=None, total=50000.0):
        """Crée une commande POS réglée par ``payments`` = [(méthode, mt)]."""
        order = self.env['pos.order'].create({
            'session_id': self.session.id,
            'company_id': self.company.id,
            'partner_id': (partner or self.client_a).id if partner is not False
                          else False,
            'amount_tax': 0.0,
            'amount_total': total,
            'amount_paid': sum(a for _m, a in payments),
            'amount_return': 0.0,
            'lines': [(0, 0, {
                'product_id': self.product.id,
                'qty': 1,
                'price_unit': total,
                'price_subtotal': total,
                'price_subtotal_incl': total,
            })],
        })
        for method, amount in payments:
            self.env['pos.payment'].create({
                'pos_order_id': order.id,
                'payment_method_id': method.id,
                'amount': amount,
            })
        order.invalidate_recordset()
        order._aite_create_credit_if_needed()
        return order

    # ------------------------------------------------------------------
    # Détection de la méthode « ardoise »
    # ------------------------------------------------------------------

    def test_flagged_method_is_a_credit_method(self):
        self.assertTrue(self.method_credit._is_aite_credit_method())

    def test_plain_cash_method_is_not(self):
        self.assertFalse(self.method_cash._is_aite_credit_method())

    # ------------------------------------------------------------------
    # Création automatique
    # ------------------------------------------------------------------

    def test_full_credit_sale_creates_the_slate(self):
        order = self._order([(self.method_credit, 50000.0)])
        self.assertTrue(order.credit_id)
        self.assertEqual(order.credit_id.amount_total, 50000.0)
        self.assertEqual(order.credit_id.partner_id, self.client_a)
        self.assertTrue(order.is_on_credit)

    def test_mixed_payment_puts_only_the_balance_on_credit(self):
        """30 000 espèces + 20 000 ardoise ⇒ ardoise de 20 000."""
        order = self._order([
            (self.method_cash, 30000.0),
            (self.method_credit, 20000.0),
        ])
        self.assertEqual(order.credit_amount, 20000.0)
        self.assertEqual(order.amount_paid_direct, 30000.0)
        self.assertEqual(order.credit_id.amount_total, 20000.0)

    def test_cash_only_sale_creates_no_slate(self):
        order = self._order([(self.method_cash, 50000.0)])
        self.assertFalse(order.credit_id)
        self.assertFalse(order.is_on_credit)
        self.assertEqual(order.amount_paid_direct, 50000.0)

    def test_credit_sale_without_customer_is_skipped(self):
        """Sans client, aucune dette ne peut être rattachée."""
        order = self._order([(self.method_credit, 50000.0)], partner=False)
        self.assertFalse(order.credit_id)

    def test_creation_is_idempotent(self):
        order = self._order([(self.method_credit, 50000.0)])
        first = order.credit_id
        order._aite_create_credit_if_needed()
        order._aite_create_credit_if_needed()
        self.assertEqual(order.credit_id, first)
        self.assertEqual(self.env['aite.pos.credit'].search_count(
            [('order_id', '=', order.id)]), 1)

    def test_slate_carries_the_order_reference(self):
        order = self._order([(self.method_credit, 50000.0)])
        credit = order.credit_id
        self.assertEqual(credit.order_id, order)
        self.assertEqual(credit.order_amount_total, 50000.0)
        self.assertEqual(credit.config_id, self.pos_config)

    def test_paid_direct_is_visible_from_the_slate(self):
        order = self._order([
            (self.method_cash, 15000.0),
            (self.method_credit, 35000.0),
        ])
        self.assertEqual(order.credit_id.order_paid_direct, 15000.0)

    # ------------------------------------------------------------------
    # Chemin manuel (rattrapage backend)
    # ------------------------------------------------------------------

    def test_manual_put_on_credit(self):
        order = self._order([(self.method_cash, 50000.0)])
        credit = order.action_put_on_credit()
        self.assertEqual(credit.amount_total, 50000.0)
        self.assertEqual(order.credit_id, credit)

    def test_manual_put_on_credit_with_down_payment(self):
        order = self._order([(self.method_cash, 50000.0)])
        credit = order.action_put_on_credit(down_payment=20000.0)
        self.assertEqual(credit.amount_total, 30000.0)

    def test_manual_refused_when_already_on_credit(self):
        order = self._order([(self.method_credit, 50000.0)])
        with self.assertRaises(UserError):
            order.action_put_on_credit()

    def test_manual_refused_without_customer(self):
        order = self._order([(self.method_cash, 50000.0)], partner=False)
        with self.assertRaises(UserError):
            order.action_put_on_credit()

    def test_manual_refused_when_down_payment_covers_everything(self):
        order = self._order([(self.method_cash, 50000.0)])
        with self.assertRaises(UserError):
            order.action_put_on_credit(down_payment=50000.0)
