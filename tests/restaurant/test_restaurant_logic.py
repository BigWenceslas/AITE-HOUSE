# -*- coding: utf-8 -*-
"""
Règles de la caisse du restaurant — tests sans Odoo (spécification, partie 6.1).

``addons/aite_pos_restaurant/models/regles.py`` est un fichier Python pur, sans
import d'Odoo (T12) : il est chargé tel quel, et c'est donc le code livré qui
est testé, pas une copie. Le tableau attendu ci-dessous est recopié de la
partie 3.3 de la spécification, case par case : il ne se déduit pas de
``DROITS``.

Lancer : python3 -m unittest discover -s tests/restaurant -p "test_*.py"
"""
import importlib.util
import os
import random
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, '..', '..', 'addons', 'aite_pos_restaurant',
                   'models', 'regles.py')


def _charger():
    spec = importlib.util.spec_from_file_location('aite_regles', SRC)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


regles = _charger()

NIVEAUX = ('serveur', 'caissiere', 'superviseur', 'manager')

# geste : (serveur, caissière, chef de salle ou superviseur, manager)
ATTENDU = {
    'servir':            (True, True, True, True),
    'table_collegue':    (False, True, True, True),
    'ouvrir_caisse':     (False, True, True, True),
    'encaisser':         (False, True, True, True),
    'rapport_ventes':    (False, True, True, True),
    'vente_sans_table':  (False, True, True, True),
    'annuler_envoye':    (False, False, True, True),
    'especes':           (False, False, True, True),
    'fermer_caisse':     (False, False, True, True),
    'fermer_avec_ecart': (False, False, False, True),
    'rembourser':        (False, False, False, True),
    'ardoise':           (False, False, False, True),
    'prix':              (False, False, False, True),
    'creer_produit':     (False, False, False, True),
}


class TestTableau(unittest.TestCase):

    def test_le_fichier_ne_depend_pas_d_odoo(self):
        with open(SRC, encoding='utf-8') as fichier:
            source = fichier.read()
        self.assertNotIn('import odoo', source)
        self.assertNotIn('from odoo', source)

    def test_quatre_niveaux_dans_l_ordre(self):
        self.assertEqual(tuple(code for code, _libelle in regles.NIVEAUX),
                         NIVEAUX)
        self.assertEqual(dict(regles.NIVEAUX)['superviseur'],
                         "Chef de salle ou superviseur")

    def test_quatorze_gestes(self):
        self.assertEqual(set(regles.DROITS), set(ATTENDU))

    def test_retour_au_plan_cinq_minutes(self):
        self.assertEqual(regles.DELAI_RETOUR_PLAN, 300)


class TestAutorise(unittest.TestCase):

    def test_les_56_cases_du_tableau(self):
        for geste, ligne in ATTENDU.items():
            for niveau, attendu in zip(NIVEAUX, ligne):
                with self.subTest(geste=geste, niveau=niveau):
                    self.assertIs(regles.autorise(niveau, geste), attendu)

    def test_niveau_inconnu_ou_vide(self):
        for niveau in (None, False, '', 'patron', 'Manager'):
            with self.subTest(niveau=niveau):
                self.assertFalse(regles.autorise(niveau, 'servir'))

    def test_geste_inconnu(self):
        for geste in (None, '', 'tout', 'remise'):
            with self.subTest(geste=geste):
                self.assertFalse(regles.autorise('manager', geste))


class TestRoleCaisse(unittest.TestCase):

    def test_seul_le_manager_a_le_role_manager(self):
        self.assertEqual(regles.role_caisse('manager'), 'manager')
        for niveau in ('serveur', 'caissiere', 'superviseur'):
            with self.subTest(niveau=niveau):
                self.assertEqual(regles.role_caisse(niveau), 'cashier')

    def test_sans_niveau(self):
        self.assertEqual(regles.role_caisse(None), 'cashier')


class TestCodeValide(unittest.TestCase):

    def test_quatre_chiffres(self):
        self.assertTrue(regles.code_valide('4821'))
        self.assertTrue(regles.code_valide('0000'))

    def test_refus(self):
        for code in ('482', '48211', '48a1', '', None, ' 482', '482 ',
                     '４８２１', 4821):
            with self.subTest(code=code):
                self.assertFalse(regles.code_valide(code))


class TestCodeLibre(unittest.TestCase):

    def test_jamais_un_code_pris_toujours_quatre_chiffres(self):
        rng = random.Random(1)
        pris = {'%04d' % i for i in range(0, 10000, 2)}  # tous les pairs
        for _ in range(200):
            code = regles.code_libre(pris, rng)
            self.assertTrue(regles.code_valide(code), code)
            self.assertNotIn(code, pris)

    def test_le_dernier_code_libre_est_trouve(self):
        pris = {'%04d' % i for i in range(10000)} - {'0427'}
        self.assertEqual(regles.code_libre(pris, random.Random(2)), '0427')

    def test_erreur_claire_si_tout_est_pris(self):
        pris = {'%04d' % i for i in range(10000)}
        with self.assertRaises(ValueError) as erreur:
            regles.code_libre(pris, random.Random(3))
        self.assertIn('10 000', str(erreur.exception))

    def test_accepte_une_liste_et_des_valeurs_vides(self):
        code = regles.code_libre(['1234', False, None, ''], random.Random(4))
        self.assertTrue(regles.code_valide(code))
        self.assertNotEqual(code, '1234')


if __name__ == '__main__':
    unittest.main()
