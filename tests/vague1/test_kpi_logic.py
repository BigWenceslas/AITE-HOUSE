# -*- coding: utf-8 -*-
"""
Tests des fonctions pures des indicateurs hôteliers (F06) — sans Odoo.

``_nights_in_window``, ``_month_bounds`` et ``_delta_pct`` sont extraites
du fournisseur du PMS par regex et exécutées telles quelles : ce que l'on
teste est le code livré, pas une copie. Les phrases d'explication du
tableau de bord exécutif sont relues de la même façon.
"""
import ast
import os
import re
import unittest
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, '..', '..', 'addons', 'aite_hotel_management',
                   'models', 'hotel_dashboard.py')
EXEC_SRC = os.path.join(HERE, '..', '..', 'addons', 'aite_exec_dashboard',
                        'models', 'exec_dashboard.py')


def _extract(name):
    src = open(SRC, encoding='utf-8').read()
    pattern = re.compile(
        r'^    @staticmethod\n    def %s\((.*?)\):\n(.*?)(?=^    @|\Z)'
        % name, re.S | re.M)
    m = pattern.search(src)
    assert m, "fonction %s introuvable" % name
    args, body = m.group(1), m.group(2)
    body = "\n".join(l[4:] if l.startswith("    ") else l
                     for l in body.splitlines())
    ns = {}
    exec("def %s(%s):\n%s" % (name, args, body), ns)
    return ns[name]


nights = _extract('_nights_in_window')
month_bounds = _extract('_month_bounds')
delta = _extract('_delta_pct')


class TestNightsInWindow(unittest.TestCase):

    def test_stay_inside_window(self):
        self.assertEqual(nights(date(2026, 10, 3), date(2026, 10, 6),
                                date(2026, 10, 1), date(2026, 11, 1)), 3)

    def test_stay_straddling_the_start(self):
        # 2 nuits avant la fenêtre, 2 dedans
        self.assertEqual(nights(date(2026, 9, 29), date(2026, 10, 3),
                                date(2026, 10, 1), date(2026, 11, 1)), 2)

    def test_stay_straddling_the_end(self):
        self.assertEqual(nights(date(2026, 10, 30), date(2026, 11, 2),
                                date(2026, 10, 1), date(2026, 11, 1)), 2)

    def test_stay_outside(self):
        self.assertEqual(nights(date(2026, 12, 1), date(2026, 12, 3),
                                date(2026, 10, 1), date(2026, 11, 1)), 0)

    def test_day_use_counts_zero(self):
        self.assertEqual(nights(date(2026, 10, 5), date(2026, 10, 5),
                                date(2026, 10, 1), date(2026, 11, 1)), 0)

    def test_missing_values(self):
        self.assertEqual(nights(None, date(2026, 10, 5),
                                date(2026, 10, 1), date(2026, 11, 1)), 0)


class TestMonthBounds(unittest.TestCase):

    def test_middle_of_month(self):
        self.assertEqual(month_bounds(date(2026, 10, 11)),
                         (date(2026, 10, 1), date(2026, 11, 1)))

    def test_december_rolls_the_year(self):
        self.assertEqual(month_bounds(date(2026, 12, 25)),
                         (date(2026, 12, 1), date(2027, 1, 1)))


class TestDeltaPct(unittest.TestCase):

    def test_growth(self):
        self.assertAlmostEqual(delta(150.0, 100.0), 50.0)

    def test_decline(self):
        self.assertAlmostEqual(delta(80.0, 100.0), -20.0)

    def test_no_base(self):
        self.assertIsNone(delta(10.0, 0.0))
        self.assertIsNone(delta(10.0, None))


class TestHints(unittest.TestCase):
    """Chaque indicateur porte une phrase, en français, assez longue
    pour expliquer — c'est ce que lit un gérant qui découvre l'écran."""

    def _hints(self):
        src = open(EXEC_SRC, encoding='utf-8').read()
        m = re.search(r'^KPI_HINTS = (\{.*?\n\})', src, re.S | re.M)
        assert m, "KPI_HINTS introuvable"
        return ast.literal_eval(m.group(1))

    def test_every_indicator_has_a_sentence(self):
        hints = self._hints()
        for key in ('occupancy', 'adr', 'revpar', 'pickup', 'pace',
                    'last_year'):
            self.assertGreaterEqual(len(hints.get(key, "")), 40, key)

    def test_revpar_sentence_is_the_one_of_the_roadmap(self):
        self.assertIn("vendue ou non", self._hints()['revpar'])

    def test_no_english_left(self):
        for key, text in self._hints().items():
            self.assertNotIn("Occupancy", text, key)
            self.assertNotIn("Revenue", text, key)


if __name__ == '__main__':
    unittest.main()
