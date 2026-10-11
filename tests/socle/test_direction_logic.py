# -*- coding: utf-8 -*-
"""
Tests — aite_direction_dashboard (couche transversale pure).

Les fonctions @staticmethod du backend sont extraites du fichier de
production et exécutées telles quelles (stub minimal pour
``fields.Date``). Aucune formule n'est recopiée dans les tests.
"""
import os
import re
import textwrap
import types
import unittest
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
ADDONS = os.path.normpath(os.path.join(HERE, '..', '..', 'addons'))
SRC = os.path.join(ADDONS, "aite_direction_dashboard", "models",
                   "direction_dashboard.py")
CODE = open(SRC, encoding="utf-8").read()

NS = {
    "fields": types.SimpleNamespace(
        Date=types.SimpleNamespace(to_date=date.fromisoformat)),
    "max": max, "min": min,
}
# constantes de module nécessaires aux purs
for const in ("TRANCHES", "AGE_BUCKETS"):
    m = re.search(r"^%s = .*?(?=^\w|\Z)" % const, CODE, re.S | re.M)
    exec(textwrap.dedent(m.group(0)), NS)


def _extract(name):
    m = re.search(
        r"^    @staticmethod\n    def " + name +
        r"\(.*?(?=^    @|^    # =|^\Z)", CODE, re.S | re.M)
    assert m, name
    exec(textwrap.dedent(m.group(0)), NS)
    return NS[name]


_rows = _extract("_rows")
_hours_for = _extract("_hours_for")
_cash_at_risk = _extract("_cash_at_risk")
_net_position = _extract("_net_position")
_age_bucket = _extract("_age_bucket")
NS["AiteDirectionDashboard"] = types.SimpleNamespace(
    _age_bucket=_age_bucket)
_bucket = _extract("_bucket_supplier_invoices")
_encours = _extract("_encours_series")
_zip = _extract("_zip_trends")
_penalty = _extract("_penalty_rows")
_actions = _extract("_build_actions")


class TestRowsNormalisation(unittest.TestCase):
    """Frontières moteur : toute réponse devient une liste de lignes."""

    def test_forme_reelle_coverage_qui_a_casse_l_ecran(self):
        # get_coverage_by_category renvoie {'rows': [...], 'crit', 'dorm'}
        raw = {"rows": [{"name": "Whisky", "couv": 26.0}],
               "crit": 3, "dorm": 60}
        self.assertEqual(_rows(raw), [{"name": "Whisky", "couv": 26.0}])

    def test_liste_nue_inchangee(self):
        self.assertEqual(_rows([{"a": 1}]), [{"a": 1}])

    def test_none_et_dict_sans_rows(self):
        self.assertEqual(_rows(None), [])
        self.assertEqual(_rows({"crit": 3}), [])
        self.assertEqual(_rows({"rows": "pas une liste"}), [])


class TestTranches(unittest.TestCase):
    def test_quatre_tranches(self):
        self.assertEqual(_hours_for("matin"), (6, 11))
        self.assertEqual(_hours_for("am"), (12, 17))
        self.assertEqual(_hours_for("soir"), (18, 22))
        self.assertEqual(_hours_for("nuit"), (23, 5))

    def test_none_et_inconnu(self):
        self.assertEqual(_hours_for(None), (None, None))
        self.assertEqual(_hours_for("brunch"), (None, None))

    def test_nuit_passe_minuit(self):
        hf, ht = _hours_for("nuit")
        self.assertGreater(hf, ht)  # contrat moteur POS : hf > ht = nuit


class TestSante(unittest.TestCase):
    def test_cash_a_risque_somme(self):
        self.assertEqual(_cash_at_risk(486000, 215975), 701975)

    def test_cash_a_risque_clampe_les_negatifs(self):
        self.assertEqual(_cash_at_risk(-50, 100), 100)
        self.assertEqual(_cash_at_risk(None, None), 0.0)

    def test_position_nette_fournisseurs(self):
        net, side = _net_position(1245000, 2870000)
        self.assertEqual(net, -1625000)
        self.assertEqual(side, "fournisseurs")

    def test_position_nette_clients_et_equilibre(self):
        self.assertEqual(_net_position(500, 100), (400, "clients"))
        self.assertEqual(_net_position(100.0, 100.0),
                         (0.0, "equilibre"))


class TestAgeBucket(unittest.TestCase):
    def test_bornes(self):
        for d, k in ((0, "0_30"), (30, "0_30"), (31, "31_60"),
                     (60, "31_60"), (61, "61_90"), (90, "61_90"),
                     (91, "90p"), (400, "90p")):
            self.assertEqual(_age_bucket(d), k, d)

    def test_negatif_ramene_a_zero(self):
        self.assertEqual(_age_bucket(-5), "0_30")


class TestEcheancierFournisseurs(unittest.TestCase):
    TODAY = "2026-07-21"

    def test_repartition_complete(self):
        rows = [
            {"amount": 640000, "date": "2026-05-02", "planned":
             "2026-07-10", "days_late": 11},          # échue
            {"amount": 420000, "date": "2026-06-25", "planned":
             "2026-07-23", "days_late": 0},           # cette semaine
            {"amount": 460000, "date": "2026-06-30", "planned":
             "2026-07-30", "days_late": 0},           # S+1
            {"amount": 640000, "date": "2026-07-02", "planned":
             "2026-08-06", "days_late": 0},           # S+2
            {"amount": 240000, "date": "2026-04-01", "planned":
             "2026-08-20", "days_late": 0},           # S+3 et +
            {"amount": 100000, "date": "2026-07-15", "planned": None,
             "days_late": 0},                         # sans échéance
        ]
        out = _bucket(rows, self.TODAY)
        s = out["schedule"]
        self.assertEqual(s["overdue"], 640000)
        self.assertEqual(s["w0"], 420000)
        self.assertEqual(s["w1"], 460000)
        self.assertEqual(s["w2"], 640000)
        self.assertEqual(s["w3p"], 340000)
        self.assertEqual(out["schedule_counts"]["w3p"], 2)

    def test_planned_passe_sans_days_late_est_echu(self):
        out = _bucket([{"amount": 10, "date": "2026-07-01",
                        "planned": "2026-07-19", "days_late": 0}],
                      self.TODAY)
        self.assertEqual(out["schedule"]["overdue"], 10)

    def test_miroir_par_date_de_facture(self):
        rows = [
            {"amount": 100, "date": "2026-07-10", "planned": None,
             "days_late": 0},                          # 11 j → 0_30
            {"amount": 200, "date": "2026-06-01", "planned": None,
             "days_late": 0},                          # 50 j → 31_60
            {"amount": 300, "date": "2026-05-10", "planned": None,
             "days_late": 0},                          # 72 j → 61_90
            {"amount": 400, "date": "2026-03-01", "planned": None,
             "days_late": 0},                          # 142 j → 90p
        ]
        aging = _bucket(rows, self.TODAY)["aging"]
        self.assertEqual(aging, {"0_30": 100, "31_60": 200,
                                 "61_90": 300, "90p": 400})


class TestSerieEncours(unittest.TestCase):
    def test_reconstitution_a_rebours(self):
        rows = [{"period": "Mai", "opened": 100, "recovered": 80},
                {"period": "Juin", "opened": 120, "recovered": 90},
                {"period": "Juil", "opened": 60, "recovered": 110}]
        out = _encours(1000, rows)
        self.assertEqual([r["period"] for r in out],
                         ["Mai", "Juin", "Juil"])
        # Juil = actuel ; Juin = 1000 − (60−110) = 1050 ;
        # Mai = 1050 − (120−90) = 1020
        self.assertEqual([r["outstanding"] for r in out],
                         [1020, 1050, 1000])

    def test_jamais_negatif(self):
        out = _encours(10, [{"period": "M", "opened": 500,
                             "recovered": 0}])
        self.assertTrue(all(r["outstanding"] >= 0 for r in out))


class TestZipTendances(unittest.TestCase):
    def test_alignement_et_zeros(self):
        pos = [{"period": "Juin", "ca": 8}, {"period": "Juil", "ca": 9}]
        bills = [{"period": "Juil", "bills": 4}]
        enc = [{"period": "Juin", "outstanding": 1}]
        out = _zip(pos, bills, enc)
        self.assertEqual(len(out), 2)
        juil = next(r for r in out if r["period"] == "Juil")
        self.assertEqual((juil["ca"], juil["bills"],
                          juil["outstanding"]), (9, 4, 0.0))

    def test_limite_six_periodes(self):
        pos = [{"period": "M%d" % i, "ca": i} for i in range(9)]
        self.assertEqual(len(_zip(pos, [], [])), 6)
        self.assertEqual(_zip(pos, [], [])[0]["period"], "M3")


class TestPenalites(unittest.TestCase):
    ROWS = [
        {"name": "OK ref", "status": "OK", "vday": 9, "price": 9,
         "value": 9},
        {"name": "Bière 65", "status": "Rupture", "vday": 2.3,
         "price": 20000, "value": 78000},
        {"name": "Eau 1,5", "status": "Rupture", "vday": 1.5,
         "price": 12000, "value": 30000},
        {"name": "Whisky", "status": "Critique", "vday": 0,
         "price": 0, "value": 84000},
    ]

    def test_filtre_et_tri(self):
        out = _penalty(self.ROWS)
        self.assertEqual([r["name"] for r in out],
                         ["Bière 65", "Eau 1,5", "Whisky"])
        self.assertEqual(out[0]["loss_day"], 2.3 * 20000)

    def test_repli_valeur_quand_pas_de_ventes(self):
        self.assertEqual(_penalty(self.ROWS)[2]["loss_day"], 0)
        self.assertEqual(_penalty(self.ROWS)[2]["value"], 84000)

    def test_limite(self):
        self.assertEqual(len(_penalty(self.ROWS, limit=2)), 2)


class TestActions(unittest.TestCase):
    BASE = dict(
        debtors=[{"name": "Mballa J.", "outstanding": 186000,
                  "max_age": 74},
                 {"name": "Récent", "outstanding": 90000,
                  "max_age": 12}],
        overdue_amount=640000, overdue_count=2,
        week_bills=[{"partner": "Wouri", "amount": 420000,
                     "planned": "2026-07-23"}],
        penalties=[{"name": "Bière 65", "loss_day": 46000,
                    "status": "Rupture", "value": 0}],
        cmd_value=503526, cmd_refs=9,
        coul_pct=7.9, coul_seuil=2.0, coul_amount=215975,
        gap_net=-149574, price_up=[{"name": "Bière 65",
                                    "partner": "Wouri",
                                    "delta_pct": 9.0}],
        ann_amount=62000, ann_count=11, rem_amount=184000, rem_pct=2.2,
    )

    def test_sections_et_compte(self):
        out = _actions(dict(self.BASE))
        keys = [s["key"] for s in out["sections"]]
        self.assertEqual(keys, ["credit", "purchase", "stock",
                                "coulage", "pos", "prices"])
        self.assertEqual(out["count"],
                         sum(len(s["rows"]) for s in out["sections"]))

    def test_debiteurs_recents_exclus(self):
        out = _actions(dict(self.BASE))
        credit = next(s for s in out["sections"]
                      if s["key"] == "credit")
        self.assertEqual(len(credit["rows"]), 1)
        self.assertIn("Mballa", credit["rows"][0]["label"])

    def test_coulage_sous_seuil_absent(self):
        inp = dict(self.BASE, coul_pct=1.5, gap_net=0)
        out = _actions(inp)
        self.assertNotIn("coulage",
                         [s["key"] for s in out["sections"]])

    def test_remises_faibles_non_signalees(self):
        inp = dict(self.BASE, rem_pct=2.2)
        out = _actions(inp)
        pos = next(s for s in out["sections"] if s["key"] == "pos")
        self.assertEqual(len(pos["rows"]), 1)  # annulations seulement

    def test_priorites(self):
        out = _actions(dict(self.BASE))
        prio = {s["key"]: s["priority"] for s in out["sections"]}
        self.assertEqual(prio["credit"], "urgent")
        self.assertEqual(prio["prices"], "watch")


if __name__ == "__main__":
    unittest.main(verbosity=2)
