# -*- coding: utf-8 -*-
"""
Tests logiques — aite_website_booking (D4).

Pipeline AITE : les fonctions pures sont EXTRAITES du fichier de
production ``models/website_booking.py`` par regex, puis exécutées
telles quelles. Si le module change, les tests testent le nouveau code.
"""
import re
import textwrap
import unittest

import os
SRC = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "addons", "aite_website_booking", "models", "website_booking.py"))


def _extract(name):
    with open(SRC, encoding="utf-8") as fh:
        code = fh.read()
    pattern = (
        r"^    def " + name +
        r"\(.*?(?=^    @staticmethod|^    @api\.|^    # -{10,}|^    def )"
    )
    match = re.search(pattern, code, re.S | re.M)
    if not match:
        raise AssertionError("Fonction %s introuvable dans %s" % (name, SRC))
    return textwrap.dedent(match.group(0))


NS = {}
for fn in ("_norm_phone", "_validate_online_booking", "_fit_starts"):
    exec(_extract(fn), NS)
_norm_phone = NS["_norm_phone"]
_validate = NS["_validate_online_booking"]
_fit_starts = NS["_fit_starts"]


def S(states):
    """Grille compacte : 'ffpxf' → slots free/partial/full."""
    m = {"f": "free", "p": "partial", "x": "full"}
    return [{"state": m[c]} for c in states]


class TestNormPhone(unittest.TestCase):
    """Normalisation téléphone : chiffres + « + » de tête uniquement."""

    def test_espaces_et_separateurs_retires(self):
        self.assertEqual(_norm_phone(" 620 12-34.56 "), "6201234 56".replace(" ", ""))

    def test_plus_de_tete_conserve(self):
        self.assertEqual(_norm_phone("+224 620 123 456"), "+224620123456")

    def test_plus_interieur_ignore(self):
        # Un « + » ailleurs qu'en tête est du bruit de saisie.
        self.assertEqual(_norm_phone("620+123456"), "620123456")

    def test_vide_et_none(self):
        self.assertEqual(_norm_phone(""), "")
        self.assertEqual(_norm_phone(None), "")

    def test_entier_accepte(self):
        self.assertEqual(_norm_phone(620123456), "620123456")


class TestValidateOnlineBooking(unittest.TestCase):
    """Ordre des erreurs : name → phone → slot ; '' si tout est bon."""

    def test_ok(self):
        self.assertEqual(_validate("Mamadou Bah", "+224620123456", True), "")

    def test_nom_trop_court(self):
        self.assertEqual(_validate("A", "620123456", True), "name")
        self.assertEqual(_validate("  ", "620123456", True), "name")
        self.assertEqual(_validate(None, "620123456", True), "name")

    def test_telephone_moins_de_8_chiffres(self):
        self.assertEqual(_validate("Mamadou", "62012", True), "phone")
        self.assertEqual(_validate("Mamadou", "", True), "phone")
        self.assertEqual(_validate("Mamadou", None, True), "phone")

    def test_telephone_8_chiffres_exactement_accepte(self):
        self.assertEqual(_validate("Mamadou", "62012345", True), "")

    def test_separateurs_ne_comptent_pas(self):
        # 7 chiffres + tirets → invalide malgré la longueur de chaîne.
        self.assertEqual(_validate("Mamadou", "6-2-0-1-2-3-4", True), "phone")

    def test_slot_manquant(self):
        self.assertEqual(_validate("Mamadou", "620123456", False), "slot")

    def test_priorite_nom_avant_telephone(self):
        self.assertEqual(_validate("", "", False), "name")


class TestFitStarts(unittest.TestCase):
    """Départs possibles pour k créneaux consécutifs libres."""

    def test_k1_tous_les_non_complets(self):
        # Écart n° 59 : le créneau « partial » (index 3) reste proposé.
        self.assertEqual(_fit_starts(S("fxfpf"), 1), [0, 2, 3, 4])

    def test_k2_paires_consecutives(self):
        # ffxff → paires libres en 0-1 et 3-4.
        self.assertEqual(_fit_starts(S("ffxff"), 2), [0, 3])

    def test_partial_reste_reservable(self):
        # partial = capacité entamée mais pas atteinte (écart n° 59) :
        # le créneau reste proposé ; seul « full » bloque.
        self.assertEqual(_fit_starts(S("fpf"), 2), [0, 1])
        self.assertEqual(_fit_starts(S("fpx"), 2), [0])

    def test_k_egal_longueur(self):
        self.assertEqual(_fit_starts(S("fff"), 3), [0])
        self.assertEqual(_fit_starts(S("ffx"), 3), [])

    def test_k_trop_grand(self):
        self.assertEqual(_fit_starts(S("ff"), 3), [])

    def test_k_zero_ou_negatif(self):
        self.assertEqual(_fit_starts(S("fff"), 0), [])
        self.assertEqual(_fit_starts(S("fff"), -2), [])

    def test_grille_vide(self):
        self.assertEqual(_fit_starts([], 1), [])

    def test_fenetre_glissante_longue(self):
        # 6 libres, k=3 → départs 0,1,2,3.
        self.assertEqual(_fit_starts(S("ffffff"), 3), [0, 1, 2, 3])


class TestArrondiCreneaux(unittest.TestCase):
    """Miroir du calcul k du contrôleur : plafond entier sans math."""

    @staticmethod
    def _k(duration, step):
        return max(1, -(-(duration or step) // step))

    def test_duree_exacte(self):
        self.assertEqual(self._k(60, 30), 2)

    def test_duree_arrondie_au_dessus(self):
        self.assertEqual(self._k(45, 30), 2)
        self.assertEqual(self._k(61, 60), 2)

    def test_duree_plus_courte_qu_un_pas(self):
        self.assertEqual(self._k(20, 30), 1)

    def test_duree_nulle_retombe_sur_un_pas(self):
        self.assertEqual(self._k(0, 30), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
