# -*- coding: utf-8 -*-
"""
Tests du suivi par catégories (aite_pos_analytics v2.1.0).

* ``_build_category_series`` — construction des séries mensuelles avec
  regroupement « Autres » : **code source réel extrait** du module et
  exécuté (technique du pipeline AITE).
* Miroirs du filtre de la vue Articles (drill catégorie + recherche).
"""
import os
import re
import textwrap
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ADDONS = os.path.normpath(os.path.join(HERE, '..', '..', 'addons'))
MODULE_FILE = os.path.join(
    ADDONS, 'aite_pos_analytics', 'models', 'pos_dashboard.py')


def _load_series_builder():
    src = open(MODULE_FILE, encoding='utf-8').read()
    m = re.search(
        r'^    def _build_category_series\(.*?(?=^    @api\.model|^    def )',
        src, re.S | re.M)
    assert m, "_build_category_series introuvable"
    ns = {}
    exec(compile(textwrap.dedent(m.group(0)), MODULE_FILE, 'exec'), ns)
    return ns['_build_category_series']


_series = _load_series_builder()


def M(**cats):
    """Un mois : {cid: {'name', 'ca'}} construit lisiblement."""
    return {cid: {'name': name, 'ca': ca}
            for cid, (name, ca) in cats.items()}


# 3 mois — Bières domine, Softs et Eaux suivent, Vins et Divers petits.
DATA = [
    {1: {'name': 'Bières', 'ca': 4200000},
     2: {'name': 'Softs', 'ca': 600000},
     3: {'name': 'Eaux', 'ca': 300000},
     4: {'name': 'Vins', 'ca': 150000},
     5: {'name': 'Divers', 'ca': 50000}},
    {1: {'name': 'Bières', 'ca': 4500000},
     2: {'name': 'Softs', 'ca': 550000},
     4: {'name': 'Vins', 'ca': 180000}},          # pas d'Eaux ce mois
    {1: {'name': 'Bières', 'ca': 4800000},
     3: {'name': 'Eaux', 'ca': 320000},
     5: {'name': 'Divers', 'ca': 40000}},
]


class TestBuildCategorySeries(unittest.TestCase):

    def test_top_par_ca_total(self):
        series = _series(DATA, top=3)
        names = [s['name'] for s in series]
        # Totaux : Bières 13,5M · Softs 1,15M · Eaux 620k · Vins 330k ·
        # Divers 90k → top 3 = Bières, Softs, Eaux + Autres
        self.assertEqual(names, ['Bières', 'Softs', 'Eaux', 'Autres'])

    def test_valeurs_alignees_avec_zeros(self):
        series = _series(DATA, top=3)
        eaux = next(s for s in series if s['name'] == 'Eaux')
        # Mois 2 sans vente d'Eaux → 0.0 à sa place, longueur = nb mois
        self.assertEqual(eaux['values'], [300000, 0.0, 320000])
        for s in series:
            self.assertEqual(len(s['values']), len(DATA))

    def test_autres_regroupe_le_reste(self):
        series = _series(DATA, top=3)
        autres = next(s for s in series if s['categ_id'] == 0)
        # Autres = Vins + Divers, mois par mois
        self.assertEqual(autres['values'],
                         [150000 + 50000, 180000, 40000])
        self.assertEqual(series[-1]['name'], 'Autres')  # toujours en dernier

    def test_moins_de_categories_que_top(self):
        series = _series(DATA, top=10)
        self.assertEqual(len(series), 5)                # pas d'Autres
        self.assertTrue(all(s['categ_id'] != 0 for s in series))

    def test_ordre_par_ca_decroissant(self):
        series = _series(DATA, top=5)
        totals = [sum(s['values']) for s in series]
        self.assertEqual(totals, sorted(totals, reverse=True))

    def test_mois_vides(self):
        series = _series([{}, {}], top=5)
        self.assertEqual(series, [])


class TestProductsDrillFilter(unittest.TestCase):
    """Miroir de ``filteredProducts`` : catégorie puis recherche."""

    PRODUCTS = [
        {'name': 'Castel 65cl', 'category': 'Bières', 'ca': 100},
        {'name': 'Guinness Smooth', 'category': 'Bières', 'ca': 80},
        {'name': 'Tangui 1,5L', 'category': 'Eaux', 'ca': 60},
        {'name': 'Djino Cocktail', 'category': 'Softs', 'ca': 40},
    ]

    @staticmethod
    def filt(products, categ, search):
        q = (search or "").lower().strip()
        lst = products
        if categ:
            lst = [p for p in lst if p['category'] == categ]
        if q:
            lst = [p for p in lst
                   if q in p['name'].lower()
                   or q in (p['category'] or '').lower()]
        return lst

    def test_drill_categorie_seule(self):
        rows = self.filt(self.PRODUCTS, 'Bières', '')
        self.assertEqual([p['name'] for p in rows],
                         ['Castel 65cl', 'Guinness Smooth'])

    def test_drill_plus_recherche(self):
        rows = self.filt(self.PRODUCTS, 'Bières', 'gui')
        self.assertEqual([p['name'] for p in rows], ['Guinness Smooth'])

    def test_toutes_categories(self):
        self.assertEqual(len(self.filt(self.PRODUCTS, None, '')), 4)

    def test_chips_liste_triee_unique(self):
        seen = {}
        for p in self.PRODUCTS:
            seen[p['category']] = True
        self.assertEqual(sorted(seen.keys()), ['Bières', 'Eaux', 'Softs'])


if __name__ == '__main__':
    unittest.main(verbosity=1)
