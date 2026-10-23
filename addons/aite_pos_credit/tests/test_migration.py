# -*- coding: utf-8 -*-
"""Mise à niveau d'une base livrée (LAVERANDAH, livraison 2).

ECARTS n° 74 : le crochet d'installation livré ne créait jamais le mode de
paiement « Ardoise client » (recherche sur ``account.account.company_id``,
absent d'Odoo 18, erreur avalée). Le crochet est corrigé, mais il ne
s'exécute qu'à l'installation : une base déjà installée restait sans mode.
Le script de migration 18.0.2.0.5 fait, pour chaque société qui n'a aucun
mode « ardoise », ce que fait désormais l'installation.
"""
from odoo.tests import tagged

from odoo.addons.aite_hotel_management.tests.test_migration import (
    load_migration,
)

from .common import CreditCommon


@tagged('post_install', '-at_install', 'aite_credit')
class TestCreditMigration(CreditCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.migration = load_migration('aite_pos_credit', '18.0.2.0.5')
        cls.Method = cls.env['pos.payment.method'].with_context(
            active_test=False)

    def _credit_methods(self):
        return self.Method.search([
            ('is_aite_credit', '=', True),
            ('company_id', '=', self.company.id),
        ])

    def _as_delivered(self):
        """État de la base livrée : aucun mode « ardoise » (ceux du jeu de
        test redeviennent des modes ordinaires)."""
        self._credit_methods().write({'is_aite_credit': False})
        self.assertFalse(self._credit_methods())

    def test_mode_ardoise_cree_a_la_mise_a_niveau(self):
        self._as_delivered()
        config = self.env['pos.config'].create({
            'name': "Caisse livrée sans ardoise",
        })

        self.migration.migrate(self.env.cr, '18.0.2.0.3')

        method = self._credit_methods()
        self.assertEqual(len(method), 1)
        self.assertEqual(method.name, "Ardoise client")
        self.assertEqual(method.type, 'pay_later')
        self.assertTrue(method.split_transactions)
        self.assertIn(method, config.payment_method_ids)

    def test_mode_existant_conserve(self):
        """Le client a déjà son mode (même archivé, même autrement nommé) :
        la migration n'en ajoute pas un second."""
        self._as_delivered()
        own = self.Method.create({
            'name': "Crédit bar",
            'is_aite_credit': True,
            'split_transactions': True,
            'company_id': self.company.id,
            'active': False,
        })
        self.migration.migrate(self.env.cr, '18.0.2.0.3')
        self.assertEqual(self._credit_methods(), own)

    def test_installation_neuve_ignoree(self):
        self._as_delivered()
        self.migration.migrate(self.env.cr, None)
        self.assertFalse(self._credit_methods())
