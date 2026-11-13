# -*- coding: utf-8 -*-
"""Génération d'ardoise depuis une commande POS (paiement mixte compris)."""
from odoo.exceptions import UserError
from odoo.tests import tagged

from .common import ArdoiseCaisseCommon, CreditCommon


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
        # L'ardoise ne naît que d'une commande réglée (AH-01) : la commande
        # passe à « payée », comme dans test_ecarts_caisse.py. Une commande
        # encore ouverte (service à table) n'ouvre plus d'ardoise.
        order.write({'state': 'paid'})
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


@tagged('post_install', '-at_install', 'aite_credit')
class TestArdoiseCommandeOuverte(ArdoiseCaisseCommon):
    """AH-01 : l'ardoise naît seulement d'une commande réglée, et s'annule
    avec elle.

    Le service à table enregistre l'addition encore ouverte (état
    « brouillon ») à chaque envoi, avec les paiements déjà saisis : une
    ardoise ne doit pas en naître. Les commandes passent par ``sync_from_ui``,
    le chemin de la caisse, et non par un ``create`` direct.
    """

    def test_commande_ouverte_n_ouvre_pas_d_ardoise(self):
        order, _uuid = self._synchroniser('draft')
        self.assertEqual(order.state, 'draft')
        self.assertTrue(order.payment_ids, "le paiement ardoise est enregistré")
        self.assertFalse(order.credit_id)
        self.assertFalse(self._ardoises(order))

    def test_la_meme_commande_reglee_ouvre_une_ardoise(self):
        order, uuid = self._synchroniser('draft')
        order, _uuid = self._synchroniser('paid', uuid=uuid)
        self.assertEqual(order.state, 'paid')
        self.assertEqual(len(self._ardoises(order)), 1)
        self.assertEqual(order.credit_id.amount_total, 50000.0)
        self.assertEqual(order.credit_id.state, 'open')

    def test_commande_ouverte_annulee_laisse_aucune_ardoise_ouverte(self):
        order, _uuid = self._synchroniser('draft')
        order.action_pos_order_cancel()
        self.assertEqual(order.state, 'cancel')
        self.assertFalse(self._ardoises(order).filtered(
            lambda c: c.state == 'open'))

    def test_ardoise_existante_annulee_avec_sa_commande(self):
        """Données d'avant la correction : une ardoise ouverte sur une
        addition encore ouverte. Annuler l'addition annule l'ardoise."""
        order, _uuid = self._synchroniser('draft')
        credit = self._credit(50000.0, order_id=order.id)
        order.credit_id = credit
        order.action_pos_order_cancel()
        self.assertEqual(order.state, 'cancel')
        self.assertEqual(credit.state, 'cancelled')

    def test_ardoise_deja_remboursee_reste_ouverte_sans_erreur(self):
        """Une ardoise qui a déjà reçu un remboursement n'est pas annulée,
        et l'annulation de l'addition ne lève aucune erreur."""
        order, _uuid = self._synchroniser('draft')
        credit = self._credit(50000.0, order_id=order.id)
        order.credit_id = credit
        self._repay(credit, 10000.0)  # validé d'office
        self.assertGreater(credit.amount_paid, 0)
        order.action_pos_order_cancel()
        self.assertEqual(order.state, 'cancel')
        self.assertEqual(credit.state, 'open')
