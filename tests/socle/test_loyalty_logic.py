# -*- coding: utf-8 -*-
"""
Tests du moteur de fidélité (aite_loyalty).

Technique signature AITE : le barème ``_points_for`` et le
classificateur ``_tier_for`` sont **extraits du code source réel** puis
exécutés — les tests valident exactement ce qui tournera en production.
"""
import math
import os
import re
import textwrap
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ADDONS = os.path.normpath(os.path.join(HERE, '..', '..', 'addons'))
SRC = os.path.join(ADDONS, 'aite_loyalty', 'models', 'loyalty_move.py')


def _extract(names):
    src = open(SRC, encoding='utf-8').read()
    ns = {'math': math}
    for name in names:
        m = re.search(
            r'^    def %s\(.*?(?=^    @staticmethod|^    @api\.|'
            r'^    # -{10,}|^    def )' % name,
            src, re.S | re.M)
        assert m, "%s introuvable" % name
        exec(compile(textwrap.dedent(m.group(0)), SRC, 'exec'), ns)
    return ns


_ns = _extract(['_points_for', '_tier_for'])
_points_for = _ns['_points_for']
_tier_for = _ns['_tier_for']

CFG = {
    'vip_spend': 500000, 'vip_visits': 10,
    'vvip_spend': 2000000, 'vvip_visits': 25, 'vvip_domains': 3,
}


class TestPointsFor(unittest.TestCase):
    """Barème : floor(montant / 1000 × taux), plancher au minimum."""

    def test_bareme_nominal(self):
        # 45 000 F à 1 pt / 1 000 → 45 points
        self.assertEqual(_points_for(45000, 1.0, 1000), 45)

    def test_arrondi_inferieur(self):
        # 45 900 F → 45 points (jamais d'arrondi supérieur)
        self.assertEqual(_points_for(45900, 1.0, 1000), 45)

    def test_taux_double(self):
        self.assertEqual(_points_for(45000, 2.0, 1000), 90)

    def test_taux_demi(self):
        # 0,5 pt / 1000 : 45 000 → 22 (floor de 22,5)
        self.assertEqual(_points_for(45000, 0.5, 1000), 22)

    def test_sous_le_minimum(self):
        self.assertEqual(_points_for(900, 1.0, 1000), 0)

    def test_au_minimum_exact(self):
        self.assertEqual(_points_for(1000, 1.0, 1000), 1)

    def test_montants_invalides(self):
        self.assertEqual(_points_for(0, 1.0, 0), 0)
        self.assertEqual(_points_for(-5000, 1.0, 0), 0)
        self.assertEqual(_points_for(None, 1.0, 1000), 0)

    def test_taux_zero(self):
        self.assertEqual(_points_for(50000, 0.0, 1000), 0)


class TestTierFor(unittest.TestCase):
    """Segmentation : les trois critères du cahier des charges."""

    def test_standard(self):
        self.assertEqual(_tier_for(100000, 3, 1, CFG), 'standard')

    def test_vip_les_deux_criteres_requis(self):
        # dépenses seules → non ; visites seules → non ; les deux → VIP
        self.assertEqual(_tier_for(600000, 5, 1, CFG), 'standard')
        self.assertEqual(_tier_for(300000, 15, 1, CFG), 'standard')
        self.assertEqual(_tier_for(600000, 12, 1, CFG), 'vip')

    def test_vip_seuils_exacts(self):
        self.assertEqual(_tier_for(500000, 10, 1, CFG), 'vip')

    def test_vvip_trois_criteres(self):
        self.assertEqual(_tier_for(2500000, 30, 3, CFG), 'vvip')

    def test_vvip_diversite_insuffisante_reste_vip(self):
        # Gros dépensier assidu mais 2 familles seulement → VIP
        self.assertEqual(_tier_for(2500000, 30, 2, CFG), 'vip')

    def test_vvip_visites_insuffisantes_reste_vip(self):
        self.assertEqual(_tier_for(2500000, 20, 4, CFG), 'vip')

    def test_vvip_seuils_exacts(self):
        self.assertEqual(_tier_for(2000000, 25, 3, CFG), 'vvip')

    def test_cfg_incomplete_sans_crash(self):
        # Seuils absents → inf → jamais atteints → standard
        self.assertEqual(_tier_for(9e9, 999, 9, {}), 'standard')


if __name__ == '__main__':
    unittest.main(verbosity=1)
