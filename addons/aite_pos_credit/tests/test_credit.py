# -*- coding: utf-8 -*-
"""Ardoise : montants, sévérité, cycle de vie, encours client."""
from datetime import timedelta

from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests import tagged

from .common import CreditCommon


@tagged('post_install', '-at_install', 'aite_credit')
class TestPosCredit(CreditCommon):

    # ------------------------------------------------------------------
    # Création & montants
    # ------------------------------------------------------------------

    def test_sequence_prefix(self):
        credit = self._credit()
        self.assertTrue(credit.name.startswith('ARD/'))

    def test_initial_residual_equals_total(self):
        credit = self._credit(80000.0)
        self.assertEqual(credit.amount_paid, 0.0)
        self.assertEqual(credit.amount_residual, 80000.0)
        self.assertEqual(credit.state, 'open')

    def test_amount_must_be_positive(self):
        with self.assertRaises(ValidationError):
            self._credit(0.0)

    def test_negative_amount_refused(self):
        with self.assertRaises(ValidationError):
            self._credit(-5000.0)

    def test_partial_repayment_reduces_residual(self):
        credit = self._credit(100000.0)
        self._repay(credit, 30000.0)
        self.assertEqual(credit.amount_paid, 30000.0)
        self.assertEqual(credit.amount_residual, 70000.0)
        self.assertEqual(credit.state, 'open')

    def test_full_repayment_settles_the_slate(self):
        credit = self._credit(100000.0)
        self._repay(credit, 100000.0)
        self.assertEqual(credit.amount_residual, 0.0)
        self.assertEqual(credit.state, 'paid')

    def test_multiple_repayments_accumulate(self):
        credit = self._credit(100000.0)
        self._repay(credit, 40000.0, method='mtn')
        self._repay(credit, 35000.0, method='orange')
        self.assertEqual(credit.amount_paid, 75000.0)
        self.assertEqual(credit.payment_count, 2)

    def test_cancelled_repayment_reopens_the_slate(self):
        credit = self._credit(50000.0)
        payment = self._repay(credit, 50000.0)
        # ``state`` n'est pas lui-même calculé : il bascule quand le
        # compute des montants se rejoue. Lire le reste dû le déclenche —
        # c'est ce que fait toute vue qui affiche l'ardoise.
        self.assertEqual(credit.amount_residual, 0.0)
        self.assertEqual(credit.state, 'paid')
        payment.action_cancel()
        credit.invalidate_recordset()
        self.assertEqual(credit.amount_residual, 50000.0)
        self.assertEqual(credit.state, 'open')

    def test_payment_count_uses_its_own_compute(self):
        """Régression : champ non stocké isolé des champs stockés.

        Partagé avec ``_compute_amounts``, il déclenchait une écriture en
        base à chaque lecture du bouton statistique.
        """
        credit = self._credit(50000.0)
        self.assertEqual(
            credit._fields['payment_count'].compute,
            '_compute_payment_count')
        self.assertEqual(
            credit._fields['amount_residual'].compute, '_compute_amounts')
        self._repay(credit, 10000.0)
        self.env.flush_all()
        credit.invalidate_recordset()
        self.assertEqual(credit.payment_count, 1)

    def test_state_field_has_no_dead_tracking(self):
        """Régression : ``tracking`` sans ``mail.thread`` ne suit rien.

        Odoo journalisait un avertissement au chargement et la promesse
        d'audit n'était pas tenue.
        """
        credit = self._credit()
        self.assertNotIn('mail.thread', type(credit)._inherit_module
                         if hasattr(type(credit), '_inherit_module') else [])
        self.assertFalse(
            getattr(credit._fields['state'], 'tracking', False),
            "state ne doit pas déclarer tracking sans mail.thread")

    # ------------------------------------------------------------------
    # Ancienneté & sévérité
    # ------------------------------------------------------------------

    def test_recent_slate(self):
        credit = self._credit(days_ago=5)
        self.assertEqual(credit.age_days, 5)
        self.assertEqual(credit.severity, 'recent')

    def test_late_slate_after_thirty_days(self):
        credit = self._credit(days_ago=35)
        self.assertEqual(credit.severity, 'late')

    def test_critical_slate_after_sixty_days(self):
        credit = self._credit(days_ago=70)
        self.assertEqual(credit.severity, 'critical')

    def test_settled_slate_has_no_severity_alarm(self):
        credit = self._credit(50000.0, days_ago=90)
        self._repay(credit, 50000.0)
        credit.invalidate_recordset()
        self.assertEqual(credit.severity, 'settled')

    def test_threshold_boundaries(self):
        """Les seuils sont inclusifs : 30 j = en retard, 60 j = critique."""
        self.assertEqual(self._credit(days_ago=29).severity, 'recent')
        self.assertEqual(self._credit(days_ago=30).severity, 'late')
        self.assertEqual(self._credit(days_ago=59).severity, 'late')
        self.assertEqual(self._credit(days_ago=60).severity, 'critical')

    # ------------------------------------------------------------------
    # Recherche sur un champ calculé non stocké
    # ------------------------------------------------------------------

    def test_search_on_age_days_inverts_the_operator(self):
        old = self._credit(days_ago=45, partner=self.client_b)
        recent = self._credit(days_ago=2, partner=self.client_b)
        found = self.env['aite.pos.credit'].search([
            ('partner_id', '=', self.client_b.id),
            ('age_days', '>', 30),
        ])
        self.assertIn(old, found)
        self.assertNotIn(recent, found)

    def test_search_on_age_days_lower_bound(self):
        old = self._credit(days_ago=45, partner=self.client_b)
        recent = self._credit(days_ago=2, partner=self.client_b)
        found = self.env['aite.pos.credit'].search([
            ('partner_id', '=', self.client_b.id),
            ('age_days', '<', 10),
        ])
        self.assertIn(recent, found)
        self.assertNotIn(old, found)

    def test_search_on_age_days_rejects_garbage(self):
        with self.assertRaises(UserError):
            self.env['aite.pos.credit'].search([('age_days', '>', 'trente')])

    # ------------------------------------------------------------------
    # Cycle de vie
    # ------------------------------------------------------------------

    def test_cancel_an_untouched_slate(self):
        credit = self._credit()
        credit.action_cancel()
        self.assertEqual(credit.state, 'cancelled')

    def test_cancel_refused_after_a_repayment(self):
        credit = self._credit(50000.0)
        self._repay(credit, 10000.0)
        with self.assertRaises(UserError):
            credit.action_cancel()

    def test_reopen_a_cancelled_slate(self):
        credit = self._credit()
        credit.action_cancel()
        credit.action_reopen()
        self.assertEqual(credit.state, 'open')

    def test_register_payment_refused_when_settled(self):
        credit = self._credit(20000.0)
        self._repay(credit, 20000.0)
        credit.invalidate_recordset()
        with self.assertRaises(UserError):
            credit.action_register_payment()

    def test_register_payment_prefills_the_residual(self):
        credit = self._credit(60000.0)
        self._repay(credit, 20000.0)
        action = credit.action_register_payment()
        self.assertEqual(action['context']['default_amount'], 40000.0)
        self.assertEqual(action['context']['default_partner_id'],
                         self.client_a.id)

    # ------------------------------------------------------------------
    # Encours client
    # ------------------------------------------------------------------

    def test_partner_outstanding_sums_open_slates(self):
        self._credit(30000.0, partner=self.client_b)
        self._credit(20000.0, partner=self.client_b)
        self.client_b.invalidate_recordset()
        self.assertEqual(self.client_b.credit_outstanding, 50000.0)

    def test_partner_outstanding_excludes_settled(self):
        settled = self._credit(30000.0, partner=self.client_b)
        self._repay(settled, 30000.0)
        self._credit(20000.0, partner=self.client_b)
        self.client_b.invalidate_recordset()
        self.assertEqual(self.client_b.credit_outstanding, 20000.0)

    def test_partner_outstanding_excludes_cancelled(self):
        cancelled = self._credit(30000.0, partner=self.client_b)
        cancelled.action_cancel()
        self.client_b.invalidate_recordset()
        self.assertEqual(self.client_b.credit_outstanding, 0.0)

    def test_partner_action_opens_its_slates(self):
        self._credit(partner=self.client_b)
        action = self.client_b.action_view_ardoises()
        self.assertEqual(action['res_model'], 'aite.pos.credit')
        self.assertIn(('partner_id', '=', self.client_b.id),
                      action['domain'])
