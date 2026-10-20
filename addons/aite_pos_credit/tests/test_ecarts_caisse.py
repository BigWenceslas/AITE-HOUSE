# -*- coding: utf-8 -*-
"""Écarts relevés en tournant les vidéos (n° 17, 20, 21 de ECARTS.md)."""
import ast

from lxml import etree

from odoo.exceptions import UserError
from odoo.tests import tagged

from .common import CreditCommon


@tagged('post_install', '-at_install', 'aite_credit')
class TestCreditEcarts(CreditCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.pos_config = cls.env['pos.config'].create({
            'name': "Caisse test écarts ardoise",
        })
        cls.product = cls.env['product.product'].create({
            'name': "Article test écarts",
            'type': 'consu',
            'available_in_pos': True,
            'list_price': 50000.0,
            'taxes_id': [(5, 0, 0)],
        })
        cls.method_credit = cls.env['pos.payment.method'].create({
            'name': "Ardoise (écarts)",
            'is_aite_credit': True,
            'company_id': cls.company.id,
        })
        # Un autre mode « payer plus tard » (sans journal), non marqué
        # ardoise : c'est la forme de « Note de chambre » (folio du séjour)
        # ou du « Compte client » standard d'Odoo.
        vals = {'name': "Note de chambre (écarts)",
                'company_id': cls.company.id}
        if 'is_room_charge' in cls.env['pos.payment.method']._fields:
            vals['is_room_charge'] = True
        cls.method_later = cls.env['pos.payment.method'].create(vals)
        cls.pos_config.write({
            'payment_method_ids': [
                (6, 0, (cls.method_credit | cls.method_later).ids)],
        })
        cls.pos_config.open_ui()
        cls.session = cls.pos_config.current_session_id

    def _order(self, method, total=50000.0):
        order = self.env['pos.order'].create({
            'session_id': self.session.id,
            'company_id': self.company.id,
            'partner_id': self.client_a.id,
            'amount_tax': 0.0,
            'amount_total': total,
            'amount_paid': total,
            'amount_return': 0.0,
            'lines': [(0, 0, {
                'product_id': self.product.id,
                'qty': 1,
                'price_unit': total,
                'price_subtotal': total,
                'price_subtotal_incl': total,
            })],
        })
        self.env['pos.payment'].create({
            'pos_order_id': order.id,
            'payment_method_id': method.id,
            'amount': total,
        })
        order.write({'state': 'paid'})
        return order

    # ------------------------------------------------------------------
    # N° 17 — « Note de chambre » n'ouvre pas d'ardoise
    # ------------------------------------------------------------------

    def test_other_pay_later_method_opens_no_slate(self):
        """Un ticket réglé en « Note de chambre » n'est réclamé qu'au folio."""
        self.assertEqual(self.method_later.type, 'pay_later')
        order = self._order(self.method_later)
        self.assertFalse(order.credit_id)
        self.assertFalse(order.is_on_credit)
        self.assertEqual(self.env['aite.pos.credit'].search_count(
            [('order_id', '=', order.id)]), 0)

    def test_room_charge_never_opens_a_slate(self):
        """Même coché « ardoise » par erreur, un mode note de chambre
        reste au folio : jamais deux créances pour une consommation."""
        if 'is_room_charge' not in self.method_later._fields:
            self.skipTest("Note de chambre (aite_hotel_pos_link) absente")
        both = self.env['pos.payment.method'].create({
            'name': "Note de chambre cochée ardoise",
            'company_id': self.company.id,
            'is_room_charge': True,
            'is_aite_credit': True,
        })
        self.assertFalse(both._is_aite_credit_method())

    def test_flagged_method_still_opens_a_slate(self):
        order = self._order(self.method_credit)
        self.assertTrue(order.credit_id)
        self.assertEqual(order.credit_id.amount_total, 50000.0)

    def test_credit_flag_is_loaded_in_the_till(self):
        """La caisse doit connaître le marqueur pour « Mettre sur ardoise »."""
        fields_loaded = self.env['pos.payment.method']._load_pos_data_fields(
            self.pos_config.id)
        self.assertIn('is_aite_credit', fields_loaded)

    # ------------------------------------------------------------------
    # N° 20 — un remboursement validé ne se modifie plus
    # ------------------------------------------------------------------

    def test_posted_repayment_is_locked(self):
        credit = self._credit(30000.0)
        payment = self._repay(credit, 10000.0)
        for vals in ({'amount': 5000.0}, {'method': 'mtn'},
                     {'transaction_ref': "MP-0001"},
                     {'date': '2020-01-01'}):
            with self.assertRaises(UserError):
                payment.write(vals)
        self.assertEqual(payment.amount, 10000.0)

    def test_posted_repayment_cannot_be_deleted(self):
        credit = self._credit(30000.0)
        payment = self._repay(credit, 10000.0)
        with self.assertRaises(UserError):
            payment.unlink()

    def test_cancel_then_reenter(self):
        """Le geste prévu : annuler, puis ressaisir le bon remboursement."""
        credit = self._credit(30000.0)
        payment = self._repay(credit, 10000.0)
        payment.action_cancel()
        payment.write({'amount': 8000.0, 'transaction_ref': "MP-0002"})
        payment.unlink()
        fixed = self._repay(credit, 8000.0)
        credit.invalidate_recordset()
        self.assertEqual(credit.amount_residual, 22000.0)
        self.assertEqual(fixed.state, 'posted')

    def test_repayment_changes_are_tracked(self):
        credit = self._credit(30000.0)
        payment = self._repay(credit, 10000.0)
        for name in ('date', 'amount', 'method', 'transaction_ref', 'state'):
            self.assertTrue(payment._fields[name].tracking, name)
        # Création et annulation sont deux requêtes distinctes : le suivi
        # ignore les changements faits dans la transaction de création.
        self.env.flush_all()
        self.env.cr.flush()
        payment.action_cancel()
        # Le suivi s'écrit au pré-commit : on le déclenche comme les tests
        # du module mail (``flush_tracking``).
        self.env.flush_all()
        self.env.cr.flush()
        tracked = payment.message_ids.tracking_value_ids.field_id.mapped(
            'name')
        self.assertIn('state', tracked)

    # ------------------------------------------------------------------
    # N° 21 — chaque « Regrouper par » fonctionne
    # ------------------------------------------------------------------

    def test_every_group_by_targets_a_stored_field(self):
        view = self.env.ref('aite_pos_credit.view_aite_pos_credit_search')
        arch = etree.fromstring(view.arch)
        Credit = self.env['aite.pos.credit']
        group_bys = []
        for node in arch.iter('filter'):
            ctx = node.get('context')
            if ctx and 'group_by' in ctx:
                group_bys.append(ast.literal_eval(ctx)['group_by'])
        self.assertTrue(group_bys)
        for fname in group_bys:
            self.assertTrue(Credit._fields[fname.split(':')[0]].store, fname)
            Credit.read_group([], [fname], [fname])
