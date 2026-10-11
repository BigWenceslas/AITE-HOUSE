# -*- coding: utf-8 -*-
"""
Tests de la logique métier du tableau de bord Stock & Inventaire.

Particularité : au lieu de dupliquer la fonction de calcul (risque de
dérive entre test et production), on **extrait le code source réel** de
``AiteStockDashboard._metrics`` depuis ``models/stock_dashboard.py`` et on
l'exécute. Toute modification du module est donc testée telle quelle.

Scénarios couverts (alignés sur le prototype HTML validé — 15 assertions —
plus des cas limites) : statuts Rupture/Critique/Sous seuil/OK/Ignorée,
priorité du seuil manuel, effet des paramètres globaux (sécurité, horizon,
critique, dormant), arrondis (plafond), classes de rotation, valeur.
"""
import os
import re
import textwrap
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ADDONS = os.path.normpath(os.path.join(HERE, '..', '..', 'addons'))
MODULE_FILE = os.path.join(
    ADDONS, 'aite_stock_dashboard', 'models', 'stock_dashboard.py')


def _load_real_metrics():
    """Extrait et exécute le VRAI code de ``_metrics`` du module."""
    src = open(MODULE_FILE, encoding='utf-8').read()
    match = re.search(
        r'^    def _metrics\(.*?(?=^    # -{10,}|^    def )',
        src, re.S | re.M)
    if not match:
        raise AssertionError(
            "_metrics introuvable dans models/stock_dashboard.py")
    code = textwrap.dedent(match.group(0))
    ns = {}
    exec(compile(code, MODULE_FILE, 'exec'), ns)
    return ns['_metrics']


_metrics = _load_real_metrics()

# Paramètres société par défaut (identiques aux defaults du module)
DFT = dict(sec_days=2, horizon_days=7, critical_days=3, dormant_days=60)


def M(stock, vday, lead=3, cost=650, manual=0.0, active=True, **over):
    cfg = {**DFT, **over}
    return _metrics(stock, vday, lead, cost,
                    cfg['sec_days'], cfg['horizon_days'],
                    cfg['critical_days'], cfg['dormant_days'],
                    manual, active)


class TestStatuts(unittest.TestCase):
    """Statuts Rupture / Critique / Sous seuil / OK / Ignorée."""

    def test_rupture(self):
        m = M(stock=0, vday=14)
        self.assertEqual(m['status'], 'Rupture')
        self.assertEqual(m['urgency'], 0)

    def test_critique(self):
        # Guinness du prototype : 48 en stock, 18/j → couverture 2,67 j < 3
        m = M(stock=48, vday=18, lead=5, cost=620)
        self.assertEqual(m['status'], 'Critique')
        self.assertAlmostEqual(m['couv'], 48 / 18, places=4)
        self.assertEqual(m['urgency'], 1)

    def test_sous_seuil(self):
        # stock 100, vday 25, lead 3, sec 2 → seuil 125 ; couv 4 j ≥ 3
        m = M(stock=100, vday=25)
        self.assertEqual(m['seuil'], 125)
        self.assertEqual(m['status'], 'Sous seuil')
        self.assertEqual(m['urgency'], 2)

    def test_ok(self):
        # Castel du prototype : 2520 en stock, 130/j → couverture 19,4 j
        m = M(stock=2520, vday=130)
        self.assertEqual(m['status'], 'OK')
        self.assertEqual(m['urgency'], 3)

    def test_ignoree(self):
        m = M(stock=0, vday=14, active=False)
        self.assertEqual(m['status'], 'Ignorée')
        self.assertEqual(m['urgency'], 4)
        self.assertEqual(m['cmd'], 0.0)


class TestPointDeCommande(unittest.TestCase):
    """Formules seuil auto et quantité suggérée (avec plafond)."""

    def test_seuil_auto_castel(self):
        # 130/j × (3+2) = 650 exactement
        m = M(stock=2520, vday=130, lead=3)
        self.assertEqual(m['seuil_auto'], 650.0)

    def test_seuil_auto_arrondi_plafond(self):
        # 3,2/j × (10+2) = 38,4 → plafond 39
        m = M(stock=60, vday=3.2, lead=10)
        self.assertEqual(m['seuil_auto'], 39.0)

    def test_securite_modifiee(self):
        # sécurité 4 j : 130 × (3+4) = 910
        m = M(stock=2520, vday=130, lead=3, sec_days=4)
        self.assertEqual(m['seuil_auto'], 910.0)

    def test_cmd_guinness(self):
        # 18/j × (5+7) − 48 = 168 (prototype)
        m = M(stock=48, vday=18, lead=5)
        self.assertEqual(m['cmd'], 168.0)

    def test_cmd_plafond(self):
        # 3,2 × (10+7) − 50 = 4,4 → 5
        m = M(stock=50, vday=3.2, lead=10)
        self.assertEqual(m['cmd'], 5.0)

    def test_cmd_zero_si_stock_suffisant(self):
        m = M(stock=2520, vday=130, lead=3)
        self.assertEqual(m['cmd'], 0.0)

    def test_horizon_modifie(self):
        # horizon 14 j : 18 × (5+14) − 48 = 294
        m = M(stock=48, vday=18, lead=5, horizon_days=14)
        self.assertEqual(m['cmd'], 294.0)


class TestSeuilManuel(unittest.TestCase):
    """Le seuil manuel remplace toujours le calcul automatique."""

    def test_manuel_prioritaire(self):
        m = M(stock=2520, vday=130, manual=3000.0)
        self.assertEqual(m['seuil'], 3000.0)
        self.assertEqual(m['status'], 'Sous seuil')  # 2520 ≤ 3000

    def test_manuel_zero_donne_auto(self):
        m = M(stock=2520, vday=130, manual=0.0)
        self.assertEqual(m['seuil'], m['seuil_auto'])

    def test_manuel_bas_repasse_ok(self):
        m = M(stock=100, vday=25, manual=50.0)   # auto serait 125
        self.assertEqual(m['seuil'], 50.0)
        self.assertEqual(m['status'], 'OK')


class TestParametresGlobaux(unittest.TestCase):
    """Effet des seuils critique et dormant configurables."""

    def test_critique_eleve_bascule_heineken(self):
        # Heineken prototype : 336 stock, 42/j → couverture 8 j
        base = M(stock=336, vday=42, lead=5, critical_days=3)
        self.assertEqual(base['status'], 'OK')
        strict = M(stock=336, vday=42, lead=5, critical_days=10)
        self.assertEqual(strict['status'], 'Critique')

    def test_dormant_reclassement(self):
        # Mauberts prototype : 14 en stock, 0,15/j → couverture ≈ 93 j
        base = M(stock=14, vday=0.15, lead=10, dormant_days=60)
        self.assertEqual(base['classe'], 'Dormant')
        souple = M(stock=14, vday=0.15, lead=10, dormant_days=200)
        self.assertNotEqual(souple['classe'], 'Dormant')
        self.assertEqual(souple['classe'], 'Lente')


class TestRotationEtValeur(unittest.TestCase):

    def test_classes_rotation(self):
        rapide = M(stock=100, vday=12)       # rot 3,6
        self.assertEqual(rapide['classe'], 'Rapide')
        normale = M(stock=100, vday=6)       # rot 1,8
        self.assertEqual(normale['classe'], 'Normale')
        lente = M(stock=100, vday=3)         # rot 0,9 · couv 33 j
        self.assertEqual(lente['classe'], 'Lente')

    def test_rotation_castel(self):
        m = M(stock=2520, vday=130)
        self.assertAlmostEqual(m['rot'], 130 * 30 / 2520, places=4)

    def test_valeur(self):
        m = M(stock=48, vday=18, cost=620)
        self.assertEqual(m['value'], 48 * 620)

    def test_stock_zero_rotation_nulle_couv_infinie(self):
        m = M(stock=0, vday=0)
        self.assertEqual(m['rot'], 0.0)
        self.assertEqual(m['couv'], 999.0)


if __name__ == '__main__':
    unittest.main(verbosity=1)
