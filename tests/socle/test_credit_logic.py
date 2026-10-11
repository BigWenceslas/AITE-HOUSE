# -*- coding: utf-8 -*-
"""
Tests de logique pure pour aite_pos_credit.

Ré-implémente les calculs critiques (reste dû, bascule d'état, sévérité,
tranches d'aging, plafond de remboursement, inversion de recherche sur l'âge)
pour les valider sans démarrer Odoo. Les corps testés sont des copies fidèles
de la logique des modèles.
"""
import unittest
from datetime import date, timedelta


AGE_LATE = 30
AGE_CRITICAL = 60


# ----------------------------------------------------------------------
# Copies de logique (miroir des modèles)
# ----------------------------------------------------------------------

def compute_amounts(amount_total, payments):
    """payments: list of (amount, state). Retourne (paid, residual, state)."""
    paid = sum(a for a, s in payments if s == 'posted')
    residual = max(0.0, amount_total - paid)
    state = 'open'
    if amount_total > 0 and residual <= 0.0:
        state = 'paid'
    return paid, residual, state


def compute_severity(date_open, today, state):
    age = (today - date_open).days if date_open else 0
    if state in ('paid', 'cancelled'):
        return age, 'settled'
    if age >= AGE_CRITICAL:
        return age, 'critical'
    if age >= AGE_LATE:
        return age, 'late'
    return age, 'recent'


def aging_bucket(age):
    buckets = [(0, 30, '0_30'), (30, 60, '30_60'), (60, 90, '60_90'),
               (90, 10**9, '90_plus')]
    for lo, hi, key in buckets:
        if lo <= age < hi:
            return key
    return None


def cap_repayment(amount, residual):
    return min(amount, residual)


def is_overpaid(new_amount, amount_total, other_posted):
    available = amount_total - other_posted
    return (new_amount - available) > 0.01


def search_age_inverse(operator, value, today):
    inverse = {'>': '<', '>=': '<=', '<': '>', '<=': '>=',
               '=': '=', '!=': '!='}.get(operator, operator)
    threshold = today - timedelta(days=int(value))
    return ('date_open', inverse, threshold)


# ----------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------

class TestAmounts(unittest.TestCase):
    def test_no_payment(self):
        paid, res, st = compute_amounts(100000, [])
        self.assertEqual(paid, 0)
        self.assertEqual(res, 100000)
        self.assertEqual(st, 'open')

    def test_partial(self):
        paid, res, st = compute_amounts(100000, [(40000, 'posted')])
        self.assertEqual(paid, 40000)
        self.assertEqual(res, 60000)
        self.assertEqual(st, 'open')

    def test_full_settles(self):
        paid, res, st = compute_amounts(100000, [(60000, 'posted'),
                                                 (40000, 'posted')])
        self.assertEqual(res, 0)
        self.assertEqual(st, 'paid')

    def test_cancelled_payment_ignored(self):
        paid, res, st = compute_amounts(100000, [(40000, 'posted'),
                                                 (60000, 'cancelled')])
        self.assertEqual(paid, 40000)
        self.assertEqual(res, 60000)
        self.assertEqual(st, 'open')

    def test_overpay_clamped_residual(self):
        # Even if payments exceed total, residual floors at 0.
        paid, res, st = compute_amounts(100000, [(120000, 'posted')])
        self.assertEqual(res, 0)
        self.assertEqual(st, 'paid')


class TestSeverity(unittest.TestCase):
    def setUp(self):
        self.today = date(2026, 6, 30)

    def test_recent(self):
        age, sev = compute_severity(self.today - timedelta(days=10),
                                    self.today, 'open')
        self.assertEqual(sev, 'recent')

    def test_late_boundary(self):
        age, sev = compute_severity(self.today - timedelta(days=30),
                                    self.today, 'open')
        self.assertEqual(age, 30)
        self.assertEqual(sev, 'late')

    def test_critical_boundary(self):
        age, sev = compute_severity(self.today - timedelta(days=60),
                                    self.today, 'open')
        self.assertEqual(sev, 'critical')

    def test_settled_overrides_age(self):
        age, sev = compute_severity(self.today - timedelta(days=200),
                                    self.today, 'paid')
        self.assertEqual(sev, 'settled')


class TestAging(unittest.TestCase):
    def test_buckets(self):
        self.assertEqual(aging_bucket(0), '0_30')
        self.assertEqual(aging_bucket(29), '0_30')
        self.assertEqual(aging_bucket(30), '30_60')
        self.assertEqual(aging_bucket(59), '30_60')
        self.assertEqual(aging_bucket(60), '60_90')
        self.assertEqual(aging_bucket(89), '60_90')
        self.assertEqual(aging_bucket(90), '90_plus')
        self.assertEqual(aging_bucket(365), '90_plus')

    def test_partition_is_complete(self):
        # Every age 0..200 lands in exactly one bucket.
        for a in range(0, 200):
            self.assertIsNotNone(aging_bucket(a))


class TestRepaymentGuards(unittest.TestCase):
    def test_cap(self):
        self.assertEqual(cap_repayment(80000, 60000), 60000)
        self.assertEqual(cap_repayment(50000, 60000), 50000)

    def test_overpaid_detection(self):
        # total 100k, 40k already posted, available 60k
        self.assertTrue(is_overpaid(60001, 100000, 40000))  # > tolerance
        self.assertFalse(is_overpaid(60000, 100000, 40000))
        self.assertFalse(is_overpaid(59000, 100000, 40000))

    def test_overpaid_tolerance(self):
        # within 1 cent tolerance -> not overpaid
        self.assertFalse(is_overpaid(60000.005, 100000, 40000))


class TestAgeSearchInversion(unittest.TestCase):
    def setUp(self):
        self.today = date(2026, 6, 30)

    def test_greater_age_means_older_date(self):
        # age_days > 30  ->  date_open < today-30
        field, op, thr = search_age_inverse('>', 30, self.today)
        self.assertEqual(field, 'date_open')
        self.assertEqual(op, '<')
        self.assertEqual(thr, date(2026, 5, 31))

    def test_ge(self):
        _, op, thr = search_age_inverse('>=', 60, self.today)
        self.assertEqual(op, '<=')
        self.assertEqual(thr, self.today - timedelta(days=60))

    def test_less_age_means_newer_date(self):
        _, op, _thr = search_age_inverse('<', 7, self.today)
        self.assertEqual(op, '>')




# ======================================================================
# v2.0.0 — Ardoises depuis le module Ventes
# ======================================================================

import os as _os
import re as _re
import textwrap as _tw

_SALE_FILE = _os.path.join(
    _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..', '..', 'addons'),
    'aite_pos_credit', 'models', 'sale_order.py')


def _load_sale_credit_amount():
    """Extrait et exécute le VRAI code de ``_aite_sale_credit_amount``."""
    src = open(_SALE_FILE, encoding='utf-8').read()
    m = _re.search(
        r'^    def _aite_sale_credit_amount\(.*?(?=^    # -{10,}|^    def )',
        src, _re.S | _re.M)
    assert m, "_aite_sale_credit_amount introuvable"
    ns = {}
    exec(compile(_tw.dedent(m.group(0)), _SALE_FILE, 'exec'), ns)
    return ns['_aite_sale_credit_amount']


_sale_amount = _load_sale_credit_amount()


class TestSaleCreditAmount(unittest.TestCase):
    """Montant d'ardoise d'une vente = total − acompte (code réel)."""

    def test_nominal_avec_acompte(self):
        # Vente 145 000 F, acompte 45 000 comptant → ardoise 100 000
        self.assertEqual(_sale_amount(145000, 45000), 100000)

    def test_sans_acompte(self):
        self.assertEqual(_sale_amount(86500, 0), 86500)

    def test_acompte_none_traite_comme_zero(self):
        self.assertEqual(_sale_amount(50000, None), 50000)

    def test_acompte_egal_total_refuse(self):
        with self.assertRaises(ValueError):
            _sale_amount(50000, 50000)

    def test_acompte_superieur_refuse(self):
        with self.assertRaises(ValueError):
            _sale_amount(50000, 60000)

    def test_commande_vide_refusee(self):
        with self.assertRaises(ValueError):
            _sale_amount(0, 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
