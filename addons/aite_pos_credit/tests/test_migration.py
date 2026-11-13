# -*- coding: utf-8 -*-
"""Mise à niveau d'une base livrée (LAVERANDAH, livraison 2).

ECARTS n° 74 : le crochet d'installation livré ne créait jamais le mode de
paiement « Ardoise client » (recherche sur ``account.account.company_id``,
absent d'Odoo 18, erreur avalée). Le crochet est corrigé, mais il ne
s'exécute qu'à l'installation : une base déjà installée restait sans mode.
Le script de migration 18.0.2.0.5 fait, pour chaque société qui n'a aucun
mode « ardoise », ce que fait désormais l'installation.

AH-01 : le script 18.0.2.0.6 annule les ardoises restées ouvertes sur une
commande annulée et signale celles qui demandent un contrôle.
"""
from odoo.tests import tagged

from odoo.addons.aite_hotel_management.tests.test_migration import (
    load_migration,
)

from .common import ArdoiseCaisseCommon, CreditCommon


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


@tagged('post_install', '-at_install', 'aite_credit')
class TestMigrationArdoisesAH01(ArdoiseCaisseCommon):
    """Mise à niveau 18.0.2.0.6 d'une base où l'ardoise naissait aussi d'une
    addition encore ouverte (AH-01, constat de revue n° 9).

    Avant la correction, une addition envoyée en brouillon avec un paiement
    « ardoise » ouvrait une dette ; annulée ensuite, elle la laissait
    ouverte. La migration annule ces ardoises (commande annulée, aucun
    remboursement) et signale pour contrôle celles qu'elle ne peut pas
    trancher seule. Elle ne touche à rien d'autre.
    """

    LOGGER = 'odoo.addons.aite_pos_credit.migrations'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.migration = load_migration('aite_pos_credit', '18.0.2.0.6')

    def _ardoise_d_avant(self, annulee=False):
        """Une ardoise comme l'ancien code la créait sur une addition encore
        ouverte ; ``annulee`` : l'addition a ensuite été annulée, et
        l'ancien code laissait l'ardoise ouverte."""
        order, _uuid = self._synchroniser('draft')
        self.assertFalse(order.credit_id)  # le nouveau code n'en crée plus
        credit = self._credit(50000.0, order_id=order.id)
        order.credit_id = credit
        if annulee:
            order.write({'state': 'cancel'})
        return order, credit

    def test_ardoise_d_une_commande_annulee_annulee(self):
        order, credit = self._ardoise_d_avant(annulee=True)
        with self.assertLogs(self.LOGGER, level='INFO') as journal:
            self.migration.migrate(self.env.cr, '18.0.2.0.5')
        self.assertEqual(order.state, 'cancel')
        self.assertEqual(credit.state, 'cancelled')
        self.assertIn(credit.name, "\n".join(journal.output))

    def test_ardoise_deja_remboursee_signalee_pas_annulee(self):
        _order, credit = self._ardoise_d_avant(annulee=True)
        self._repay(credit, 10000.0)
        with self.assertLogs(self.LOGGER, level='WARNING') as journal:
            self.migration.migrate(self.env.cr, '18.0.2.0.5')
        self.assertEqual(credit.state, 'open')
        self.assertIn(credit.name, "\n".join(journal.output))

    def test_ardoise_d_une_table_encore_ouverte_signalee(self):
        order, credit = self._ardoise_d_avant()
        with self.assertLogs(self.LOGGER, level='WARNING') as journal:
            self.migration.migrate(self.env.cr, '18.0.2.0.5')
        self.assertEqual(order.state, 'draft')
        self.assertEqual(credit.state, 'open')
        self.assertIn(credit.name, "\n".join(journal.output))

    def test_ardoises_ordinaires_intactes(self):
        """Une ardoise née d'une commande réglée et une ardoise saisie à la
        main (sans commande) ne bougent pas, et rien n'est signalé."""
        order, uuid = self._synchroniser('draft')
        order, _uuid = self._synchroniser('paid', uuid=uuid)
        reglee = order.credit_id
        self.assertTrue(reglee)
        manuelle = self._credit(20000.0)
        with self.assertNoLogs(self.LOGGER, level='WARNING'):
            self.migration.migrate(self.env.cr, '18.0.2.0.5')
        self.assertEqual(reglee.state, 'open')
        self.assertEqual(manuelle.state, 'open')

    def test_installation_neuve_ignoree(self):
        _order, credit = self._ardoise_d_avant(annulee=True)
        self.migration.migrate(self.env.cr, None)
        self.assertEqual(credit.state, 'open')
