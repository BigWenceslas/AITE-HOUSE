# -*- coding: utf-8 -*-
"""
Tests du moteur de calcul de la taxe de séjour — sans Odoo.

Les fonctions pures ``_taxable_units`` et ``_tax_amount`` sont extraites du
source par regex et exécutées telles quelles : ce que l'on teste est le code
livré, pas une copie.
"""
import os
import re
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, '..', '..', 'addons', 'aite_city_tax', 'models',
                   'city_tax_rate.py')


def _extract(name):
    src = open(SRC, encoding='utf-8').read()
    pattern = re.compile(
        r'^    @staticmethod\n    def %s\((.*?)\):\n(.*?)(?=^    @|\Z)'
        % name, re.S | re.M)
    m = pattern.search(src)
    assert m, "fonction %s introuvable" % name
    args, body = m.group(1), m.group(2)
    # dédenter de 4 espaces
    body = "\n".join(l[4:] if l.startswith("    ") else l
                     for l in body.splitlines())
    code = "def %s(%s):\n%s" % (name, args, body)
    ns = {}
    exec(code, ns)
    return ns[name]


units = _extract('_taxable_units')
amount = _extract('_tax_amount')


class TestTaxableUnits(unittest.TestCase):

    def test_person_adults_only(self):
        # 3 nuits, 2 adultes, 1 enfant non compté → 6
        self.assertEqual(units('person', 3, 2, 1, False), 6)

    def test_person_with_children(self):
        self.assertEqual(units('person', 3, 2, 1, True), 9)

    def test_room_basis_ignores_persons(self):
        self.assertEqual(units('room', 3, 2, 1, True), 3)
        self.assertEqual(units('room', 3, 4, 2, True, rooms=2), 6)

    def test_day_use_counts_one_night(self):
        self.assertEqual(units('person', 0, 2, 0, False), 2)
        self.assertEqual(units('room', 0, 1, 0, False), 1)

    def test_negative_or_none_values(self):
        self.assertEqual(units('person', -2, -1, None, True), 0)
        self.assertEqual(units('person', None, None, None, False), 0)
        self.assertEqual(units('room', None, 0, 0, False, rooms=None), 1)

    def test_zero_adults_person_basis(self):
        # Pas d'adulte déclaré : rien à taxer (cas de saisie incomplète)
        self.assertEqual(units('person', 2, 0, 0, False), 0)


class TestTaxAmount(unittest.TestCase):

    def test_cameroon_3_stars(self):
        # 3 000 F × (2 nuits × 2 adultes) = 12 000 F
        self.assertEqual(amount(3000, units('person', 2, 2, 0, False)), 12000.0)

    def test_cameroon_5_stars_family(self):
        # 5★, 3 nuits, 2 adultes, 2 enfants non comptés → 30 000 F
        self.assertEqual(amount(5000, units('person', 3, 2, 2, False)), 30000.0)

    def test_ivory_coast_room_basis(self):
        # CI 3★ : 2 000 F × 4 nuits × 1 chambre = 8 000 F
        self.assertEqual(amount(2000, units('room', 4, 3, 1, False)), 8000.0)

    def test_guinea_gnf(self):
        self.assertEqual(amount(10000, units('person', 1, 1, 0, False)), 10000.0)

    def test_never_negative(self):
        self.assertEqual(amount(-500, 3), 0.0)
        self.assertEqual(amount(500, -3), 0.0)
        self.assertEqual(amount(None, None), 0.0)


class TestDataBaremes(unittest.TestCase):
    """Le fichier de données reflète bien les barèmes officiels relevés."""

    def setUp(self):
        self.xml = open(os.path.join(
            HERE, '..', '..', 'addons', 'aite_city_tax', 'data',
            'city_tax_data.xml'), encoding='utf-8').read()

    def _amount(self, rec_id):
        m = re.search(r'id="%s".*?<field name="amount">(\d+)</field>'
                      % rec_id, self.xml, re.S)
        return int(m.group(1)) if m else None

    def test_cameroon_scale(self):
        self.assertEqual(self._amount('rate_cm_5'), 5000)
        self.assertEqual(self._amount('rate_cm_4'), 4000)
        self.assertEqual(self._amount('rate_cm_3'), 3000)
        self.assertEqual(self._amount('rate_cm_2'), 1000)
        self.assertEqual(self._amount('rate_cm_1'), 500)
        self.assertEqual(self._amount('rate_cm_0'), 500)

    def test_each_country_has_six_categories(self):
        for cc in ('cm', 'ci', 'sn', 'gn'):
            for s in range(6):
                self.assertIn('id="rate_%s_%d"' % (cc, s), self.xml,
                              "barème %s %d★ manquant" % (cc, s))

    def test_noupdate_so_client_edits_survive_upgrades(self):
        self.assertIn('noupdate="1"', self.xml)


if __name__ == '__main__':
    unittest.main(verbosity=2)
