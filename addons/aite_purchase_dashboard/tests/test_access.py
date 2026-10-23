# -*- coding: utf-8 -*-
"""Droits d'accès : le tableau de bord Achats s'ouvre pour un acheteur.

Le menu est ouvert au groupe Utilisateur des achats. Un acheteur n'a pas
— et n'a pas à avoir — le droit Facturation : aucun appel du tableau de
bord ne doit donc lever une erreur d'accès pour lui (écart n° 13).
"""
from datetime import timedelta

from odoo import fields
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install', 'aite_purchase')
class TestPurchaseDashboardAccess(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.today = fields.Date.context_today(cls.env.user)
        cls.buyer = cls.env['res.users'].create({
            'name': "Acheteur sans facturation",
            'login': 'acheteur.tdb.test',
            'groups_id': [(6, 0, [
                cls.env.ref('base.group_user').id,
                cls.env.ref('purchase.group_purchase_user').id,
            ])],
        })
        cls.supplier = cls.env['res.partner'].create({
            'name': "Brasseries Test Accès", 'supplier_rank': 1,
        })

    def _endpoints(self, dashboard):
        d_from = fields.Date.to_string(self.today - timedelta(days=60))
        d_to = fields.Date.to_string(self.today)
        return [
            ('get_meta', lambda: dashboard.get_meta()),
            ('get_suppliers', lambda: dashboard.get_suppliers()),
            ('get_kpis', lambda: dashboard.get_kpis(d_from, d_to)),
            ('get_open_invoices', lambda: dashboard.get_open_invoices()),
            ('get_orders_journal',
             lambda: dashboard.get_orders_journal(d_from, d_to)),
            ('get_claims', lambda: dashboard.get_claims()),
            ('get_flux_months', lambda: dashboard.get_flux_months()),
            ('get_price_moves', lambda: dashboard.get_price_moves()),
            ('get_price_index', lambda: dashboard.get_price_index()),
            ('get_supplier_rows',
             lambda: dashboard.get_supplier_rows(d_from, d_to)),
        ]

    def test_buyer_without_invoicing_opens_every_endpoint(self):
        self.assertFalse(
            self.buyer.has_group('account.group_account_invoice'),
            "le profil de test ne doit pas avoir le droit Facturation")
        dashboard = self.env['aite.purchase.dashboard'].with_user(self.buyer)
        for name, call in self._endpoints(dashboard):
            with self.subTest(endpoint=name):
                self.env.invalidate_all()
                self.assertIsNotNone(call(), "%s ne renvoie rien" % name)

    def test_deposit_register_access_is_the_one_documented(self):
        """Écart n° 50 : le menu « Consignes fournisseurs » annonçait les
        acheteurs, mais son parent Achats → Configuration est réservé aux
        responsables. Ce que dit le README est ce qui s'applique :
        l'acheteur lit le registre par le bouton du tableau de bord, le
        menu ne s'affiche qu'au responsable."""
        Action = self.env['ir.actions.act_window'].with_user(self.buyer)
        action = Action._for_xml_id(
            'aite_purchase_dashboard.action_aite_purchase_deposit')
        self.assertEqual(action['res_model'], 'aite.purchase.deposit')
        self.env['aite.purchase.deposit'].with_user(self.buyer).search_read(
            [], ['partner_id', 'qty', 'value'])

        menu = self.env.ref('aite_purchase_dashboard.menu_aite_purchase_deposit')
        self.assertEqual(menu.groups_id,
                         self.env.ref('purchase.group_purchase_manager'))
        Menu = self.env['ir.ui.menu']
        self.assertNotIn(menu.id,
                         Menu.with_user(self.buyer)._visible_menu_ids())
        manager = self.env['res.users'].create({
            'name': "Responsable achats (test)",
            'login': 'responsable.achats.tdb.test',
            'groups_id': [(6, 0, [
                self.env.ref('base.group_user').id,
                self.env.ref('purchase.group_purchase_manager').id,
            ])],
        })
        self.assertIn(menu.id, Menu.with_user(manager)._visible_menu_ids())

    def test_buyer_sees_the_same_payments_as_the_manager(self):
        """Les paiements du mois sont un agrégat : l'acheteur voit le
        même total que l'administrateur."""
        journal = self.env['account.journal'].search([
            ('type', '=', 'bank'),
            ('company_id', '=', self.env.company.id)], limit=1)
        if not journal:
            self.skipTest("aucun journal de banque (plan comptable absent)")
        payment = self.env['account.payment'].create({
            'payment_type': 'outbound',
            'partner_type': 'supplier',
            'partner_id': self.supplier.id,
            'amount': 37000.0,
            'journal_id': journal.id,
            'date': self.today,
        })
        payment.action_post()
        self.env.flush_all()
        admin = self.env['aite.purchase.dashboard'].get_flux_months(
            supplier_id=self.supplier.id)
        self.env.invalidate_all()
        buyer = self.env['aite.purchase.dashboard'].with_user(
            self.buyer).get_flux_months(supplier_id=self.supplier.id)
        self.assertEqual(admin[-1]['payments'], 37000.0)
        self.assertEqual([m['payments'] for m in buyer],
                         [m['payments'] for m in admin])
