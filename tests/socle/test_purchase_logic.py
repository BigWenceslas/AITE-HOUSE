# -*- coding: utf-8 -*-
"""
Tests de la logique métier du tableau de bord Achats & Fournisseurs.

Comme pour le module Stock : on **extrait le code source réel** des
fonctions pures depuis ``models/purchase_dashboard.py`` (``_bucket``,
``_invoice_metrics``, ``_order_metrics``, ``_price_metrics``,
``_supplier_badge``, ``_dpo``) et on l'exécute. Les scénarios reprennent
les 28 assertions du prototype HTML validé, plus les cas limites.
"""
import os
import re
import textwrap
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ADDONS = os.path.normpath(os.path.join(HERE, '..', '..', 'addons'))
MODULE_FILE = os.path.join(
    ADDONS, 'aite_purchase_dashboard', 'models', 'purchase_dashboard.py')


def _load(names):
    src = open(MODULE_FILE, encoding='utf-8').read()
    ns = {}
    for name in names:
        m = re.search(
            r'^    def %s\(.*?(?=^    @staticmethod|^    # -{10,}|^    def )'
            % name, src, re.S | re.M)
        assert m, "%s introuvable" % name
        exec(compile(textwrap.dedent(m.group(0)), MODULE_FILE, 'exec'), ns)
    return ns


_ns = _load(['_bucket', '_invoice_metrics', '_order_metrics',
             '_price_metrics', '_supplier_badge', '_dpo'])
_bucket = _ns['_bucket']
_invoice_metrics = _ns['_invoice_metrics']
_order_metrics = _ns['_order_metrics']
_price_metrics = _ns['_price_metrics']
_supplier_badge = _ns['_supplier_badge']
_dpo = _ns['_dpo']


class TestBuckets(unittest.TestCase):
    """Tranches de balance âgée par jours de retard (bornes incluses)."""

    def test_prototype_cases(self):
        self.assertEqual(_bucket(73), 3)   # SDV-1108 : 61–90 j
        self.assertEqual(_bucket(35), 2)   # UCB-3312 : 31–60 j
        self.assertEqual(_bucket(14), 1)   # GC-88412 : 1–30 j
        self.assertEqual(_bucket(0), 0)    # non échu

    def test_bornes(self):
        self.assertEqual(_bucket(30), 1)
        self.assertEqual(_bucket(31), 2)
        self.assertEqual(_bucket(60), 2)
        self.assertEqual(_bucket(61), 3)
        self.assertEqual(_bucket(90), 3)
        self.assertEqual(_bucket(91), 4)


class TestInvoiceStatus(unittest.TestCase):
    """Statuts de facture selon retard / fenêtre d'échéance."""

    def test_en_retard(self):
        m = _invoice_metrics(1140000, 7, 0, 7)
        self.assertEqual((m['status'], m['urgency']), ('En retard', 0))

    def test_retard_un_jour(self):
        m = _invoice_metrics(210000, 1, 0, 7)
        self.assertEqual(m['status'], 'En retard')

    def test_a_payer_bientot(self):
        m = _invoice_metrics(1980000, 0, 3, 7)
        self.assertEqual((m['status'], m['urgency']),
                         ('À payer bientôt', 1))

    def test_a_echoir(self):
        m = _invoice_metrics(1720000, 0, 16, 7)
        self.assertEqual(m['status'], 'À échoir')

    def test_fenetre_configurable(self):
        # soon 7 → À échoir ; soon 20 → À payer bientôt (le flip du proto)
        self.assertEqual(
            _invoice_metrics(1720000, 0, 16, 7)['status'], 'À échoir')
        self.assertEqual(
            _invoice_metrics(1720000, 0, 16, 20)['status'],
            'À payer bientôt')

    def test_payee(self):
        m = _invoice_metrics(0, 0, 0, 7)
        self.assertEqual((m['status'], m['urgency']), ('Payée', 5))


class TestOrderMetrics(unittest.TestCase):
    """OTIF strict vs badge toléré — le cœur de la nuance OTD/OTIF."""

    def test_recue_conforme(self):
        m = _order_metrics(False, 0, True, 2)
        self.assertEqual(m['status'], 'Reçue conforme')
        self.assertTrue(m['otif'])

    def test_a_lheure_mais_incomplete(self):
        # PO-0295 du prototype : ponctuelle MAIS incomplète → OTIF ✗
        m = _order_metrics(False, 0, False, 2)
        self.assertTrue(m['on_time'])
        self.assertFalse(m['otif'])
        self.assertEqual(m['status'], 'Reçue incomplète')

    def test_retard_tolere_badge_mais_otif_strict(self):
        # PO-0288 : 2 j de retard, seuil 2 → badge conforme, OTIF ✗
        m = _order_metrics(False, 2, True, 2)
        self.assertEqual(m['status'], 'Reçue conforme')
        self.assertFalse(m['otif'])

    def test_seuil_un_jour_flip_badge(self):
        m = _order_metrics(False, 2, True, 1)
        self.assertEqual(m['status'], 'Reçue en retard')

    def test_en_attente(self):
        m = _order_metrics(True, 0, None, 2)
        self.assertEqual(m['status'], 'En attente')
        self.assertIsNone(m['otif'])

    def test_en_attente_en_retard(self):
        m = _order_metrics(True, 5, None, 2)
        self.assertEqual(m['status'], 'En retard')


class TestPriceMetrics(unittest.TestCase):
    """Badges de variation de prix et impact annuel."""

    def test_castel_hausse_forte(self):
        m = _price_metrics(7800, 8400, 340, 5.0)
        self.assertAlmostEqual(m['delta'], 7.6923, places=3)
        self.assertEqual(m['badge'], 'Hausse forte')
        self.assertEqual(m['impact'], 600 * 340 * 12)

    def test_seuil_10_plus_de_forte(self):
        m = _price_metrics(7800, 8400, 340, 10.0)
        self.assertEqual(m['badge'], 'Hausse')

    def test_baisse(self):
        m = _price_metrics(3400, 3300, 78, 5.0)
        self.assertEqual(m['badge'], 'Baisse')
        self.assertLess(m['impact'], 0)

    def test_stable(self):
        m = _price_metrics(10200, 10200, 82, 5.0)
        self.assertEqual(m['badge'], 'Stable')
        self.assertEqual(m['impact'], 0)

    def test_prix_zero_sans_division(self):
        m = _price_metrics(0, 500, 10, 5.0)
        self.assertEqual(m['delta'], 0.0)


class TestSupplierBadge(unittest.TestCase):
    """Badge fournisseur : dépendance > retards > OK > inactif."""

    def test_sabc_dependance(self):
        b = _supplier_badge(71.5, 1140000, 7700000, 40.0)
        self.assertEqual(b['badge'], 'Dépendance')

    def test_seuil_80_bascule_retards(self):
        # Le flip du prototype : dep=80 → SABC (retards>0) badge Retards
        b = _supplier_badge(71.5, 1140000, 7700000, 80.0)
        self.assertEqual(b['badge'], 'Retards')

    def test_ok(self):
        b = _supplier_badge(12.0, 0, 640000, 40.0)
        self.assertEqual(b['badge'], 'OK')

    def test_inactif(self):
        b = _supplier_badge(0, 0, 0, 40.0)
        self.assertEqual(b['badge'], 'Inactif')


class TestDpo(unittest.TestCase):

    def test_prototype(self):
        # 8 450 000 / 10 765 000 × 30 ≈ 23,55 j
        self.assertAlmostEqual(
            _dpo(8450000, 10765000, 30), 23.55, places=1)

    def test_sans_achats(self):
        self.assertEqual(_dpo(500000, 0, 30), 0.0)


if __name__ == '__main__':
    unittest.main(verbosity=1)
