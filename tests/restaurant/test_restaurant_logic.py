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


class TestBilanLigne(unittest.TestCase):
    """Ce que le serveur conclut d'une ligne à chaque synchronisation
    (incrément 3 ; partie 6.1) :
    bilan_ligne(envoyee, prep_avant, prep, qte_avant, qte, deplacement)
    → (saisie, retrait, nouvelle_envoyee).

    Recopié de la partie 6.1, cas par cas. La saisie et l'envoi servent à
    l'incrément 3 (journal des saisies, quantité verrouillée) ; le retrait
    sert au journal des annulations de l'incrément 4."""

    CAS = [
        # (envoyee, prep_avant, prep, qte_avant, qte, deplacement) → attendu, pourquoi
        ((3, 3, 3, 3, 3, False), (0, 0, 3), "rien n'a changé"),
        ((3, 3, 4, 3, 4, False), (1, 0, 4), "saisie et envoi"),
        ((3, 3, 3, 3, 4, False), (1, 0, 3), "saisi, pas envoyé"),
        ((4, 4, 4, 4, 3, False), (0, 1, 3), "retrait sans code"),
        ((4, 4, 3, 4, 3, True), (0, 0, 3), "division, côté origine"),
        ((0, 0, 2, 0, 2, True), (0, 0, 2), "part née d'une division"),
        ((2, 3, 3, 3, 3, False), (0, 0, 2),
         "annulation autorisée, réponse perdue : la copie du poste ne relève pas le verrou"),
        ((2, 3, 2, 3, 2, False), (0, 0, 2), "annulation appliquée"),
        ((3, 3, 0, 3, 0, False), (0, 3, 0), "ligne supprimée"),
        ((0, 0, 0, 0, 2, False), (2, 0, 0), "ligne neuve, pas envoyée"),
    ]

    def test_les_cas_de_la_specification(self):
        for args, attendu, pourquoi in self.CAS:
            with self.subTest(pourquoi, args=args):
                self.assertEqual(tuple(regles.bilan_ligne(*args)), attendu)

    def test_une_reunion_n_est_pas_une_saisie(self):
        # Les lignes de la table absorbée arrivent sur la table d'arrivée.
        self.assertEqual(tuple(regles.bilan_ligne(2, 2, 5, 2, 5, True)), (0, 0, 5))

    def test_quantites_decimales(self):
        saisie, retrait, envoyee = regles.bilan_ligne(0.5, 0.5, 0.5, 0.5, 0.75, False)
        self.assertAlmostEqual(saisie, 0.25)
        self.assertEqual(retrait, 0)
        self.assertAlmostEqual(envoyee, 0.5)

    def test_ligne_de_remboursement(self):
        # Quantité négative : ni saisie, ni retrait, rien d'envoyé.
        self.assertEqual(tuple(regles.bilan_ligne(0, 0, 0, 0, -1, False)), (0, 0, 0))

    def test_valeurs_vides(self):
        self.assertEqual(tuple(regles.bilan_ligne(None, False, None, None, 2, False)),
                         (2, 0, 0))


class TestCompteurs(unittest.TestCase):
    """Personnes et tables d'une addition (partie 5.2) :
    compteurs(personnes, part, remboursement) → (tables, personnes, sans_table)."""

    CAS = [
        ((4, False, False), (1, 4, 0), "table ouverte à 4"),
        ((0, True, False), (0, 0, 0), "part 12B : les personnes restent sur l'origine"),
        ((0, False, False), (0, 0, 1), "vente sans table"),
        ((2, True, False), (1, 2, 0), "part portée sur une table libre"),
        ((3, False, True), (0, 0, 0), "remboursement"),
    ]

    def test_les_cas_de_la_specification(self):
        for args, attendu, pourquoi in self.CAS:
            with self.subTest(pourquoi, args=args):
                self.assertEqual(tuple(regles.compteurs(*args)), attendu)

    def test_personnes_vides(self):
        self.assertEqual(tuple(regles.compteurs(None, False, False)), (0, 0, 1))


if __name__ == '__main__':
    unittest.main()
