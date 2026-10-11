# -*- coding: utf-8 -*-
"""
Tests — aite_demo_data (jeu d'essai de démonstration).

Le jeu d'essai n'est pas décoratif : il doit passer les contraintes du
moteur de créneaux (alignement, capacité) et être REPRODUIT par le moteur
de fidélité réel. Ces tests :
  1. valident le plan (alignement, capacité, états, compatibilité
     service ↔ ressource) ;
  2. recoupent le plan avec les XML générés (dates eval, refs) ;
  3. rejouent les fonctions réelles ``_points_for`` / ``_tier_for``
     extraites d'aite_loyalty sur chaque mouvement et chaque client :
     les statuts posés dans la démo doivent être ceux que le moteur
     recalculerait.
"""
import json
import os
import re
import textwrap
import unittest
from xml.dom import minidom

HERE = os.path.dirname(os.path.abspath(__file__))
ADDONS = os.path.normpath(os.path.join(HERE, '..', '..', 'addons'))
MOD = os.path.join(ADDONS, "aite_demo_data")
PLAN = json.load(open(os.path.join(MOD, "plan.json"), encoding="utf-8"))
LOYALTY_SRC = os.path.join(ADDONS, "aite_loyalty", "models",
                           "loyalty_move.py")


def _extract(name):
    code = open(LOYALTY_SRC, encoding="utf-8").read()
    m = re.search(
        r"^    def " + name +
        r"\(.*?(?=^    @staticmethod|^    @api\.|^    # -{10,}|^    def )",
        code, re.S | re.M)
    assert m, name
    import math
    ns = {"math": math}
    exec(textwrap.dedent(m.group(0)), ns)
    return ns[name]


_points_for = _extract("_points_for")
_tier_for = _extract("_tier_for")
CFG = dict(rate_per_1000=1.0, min_amount=1000.0,
           vip_spend=500000.0, vip_visits=10,
           vvip_spend=2000000.0, vvip_visits=25, vvip_domains=3)


def _xml(name):
    return minidom.parse(os.path.join(MOD, "data", name))


class TestVolumes(unittest.TestCase):
    def test_au_moins_100_produits(self):
        self.assertGreaterEqual(PLAN["counts"]["products"], 100)

    def test_volumes_globaux(self):
        c = PLAN["counts"]
        self.assertGreaterEqual(c["bookings"], 100)
        self.assertGreaterEqual(c["loyalty_moves"], 100)
        self.assertGreaterEqual(c["partners"], 30)
        self.assertGreaterEqual(sum(c.values()), 1000)

    def test_xml_correspond_au_plan(self):
        n_prod = sum(len(_xml(f).getElementsByTagName("record"))
                     for f in ("02_products_restaurant.xml",
                               "03_products_boutique.xml",
                               "04_products_services.xml"))
        self.assertEqual(n_prod, PLAN["counts"]["products"])
        self.assertEqual(
            len(_xml("08_bookings.xml").getElementsByTagName("record")),
            PLAN["counts"]["bookings"])
        self.assertEqual(
            len(_xml("09_loyalty_moves.xml").getElementsByTagName("record")),
            PLAN["counts"]["loyalty_moves"])


class TestIntegriteRefs(unittest.TestCase):
    def test_toutes_les_refs_internes_resolues(self):
        defined, used = set(), set()
        for f in sorted(os.listdir(os.path.join(MOD, "data"))):
            dom = _xml(f)
            for r in dom.getElementsByTagName("record"):
                defined.add(r.getAttribute("id"))
            for fld in dom.getElementsByTagName("field"):
                if fld.getAttribute("ref"):
                    used.add(fld.getAttribute("ref"))
                ev = fld.getAttribute("eval")
                used.update(re.findall(r"ref\('([^']+)'\)", ev))
        autorisees = {"stock.stock_location_stock"}
        externes = {u for u in used if "." in u} - autorisees
        self.assertFalse(externes,
                         "refs externes fragiles : %s" % externes)
        manquantes = used - defined - autorisees
        self.assertFalse(manquantes, "refs non définies : %s" % manquantes)


class TestPlanBookings(unittest.TestCase):
    def setUp(self):
        self.res = PLAN["resources"]
        self.bookings = PLAN["bookings"]

    def test_alignement_grille(self):
        for b in self.bookings:
            r = self.res[b["res"]]
            step = r["step"]
            offset = b["start_min"] - r["open"] * 60
            self.assertEqual(offset % step, 0, b["xid"])
            self.assertEqual(b["dur"] % step, 0, b["xid"])
            self.assertGreaterEqual(b["start_min"], r["open"] * 60, b["xid"])
            self.assertLessEqual(b["start_min"] + b["dur"],
                                 r["close"] * 60, b["xid"])

    def test_capacite_jamais_depassee(self):
        occ = {}
        for b in self.bookings:
            step = self.res[b["res"]]["step"]
            for s in range(b["start_min"], b["start_min"] + b["dur"], step):
                k = (b["res"], b["day"], s)
                occ[k] = occ.get(k, 0) + 1
        for (rx, _, _), n in occ.items():
            self.assertLessEqual(n, self.res[rx]["cap"], rx)

    def test_etats_selon_le_temps(self):
        for b in self.bookings:
            if b["day"] < 0:
                self.assertIn(b["state"],
                              ("done", "no_show", "cancelled"), b["xid"])
            else:
                self.assertEqual(b["state"], "confirmed", b["xid"])

    def test_service_compatible_ressource(self):
        kind_of_res = {"res_vip_nongo": "space", "res_vip_kaloum": "space",
                       "res_vvip_kakimbo": "space",
                       "res_vvip_terrasse": "space",
                       "res_spa1": "spa", "res_spa2": "spa",
                       "res_spa_duo": "spa", "res_hammam": "spa",
                       "res_coif_h1": "hair", "res_coif_h2": "hair",
                       "res_coif_f1": "hair", "res_coif_f2": "hair",
                       "res_pressing": "pressing"}
        for b in self.bookings:
            self.assertEqual(b["kind"], kind_of_res[b["res"]], b["xid"])
            if b["kind"] == "space":
                self.assertIsNone(b["svc"], b["xid"])
            else:
                self.assertIsNotNone(b["svc"], b["xid"])

    def test_montants_espaces_egal_duree_fois_tarif(self):
        tarifs = {"res_vip_nongo": 150000, "res_vip_kaloum": 150000,
                  "res_vvip_kakimbo": 300000, "res_vvip_terrasse": 300000}
        for b in self.bookings:
            if b["kind"] == "space":
                self.assertEqual(
                    b["amount"], tarifs[b["res"]] * b["dur"] // 60, b["xid"])

    def test_planning_du_jour_non_vide(self):
        # La démo doit montrer un planning vivant le jour J.
        self.assertGreaterEqual(
            sum(1 for b in self.bookings if b["day"] == 0), 3)

    def test_xml_evals_concordent_avec_le_plan(self):
        xml = open(os.path.join(MOD, "data", "08_bookings.xml"),
                   encoding="utf-8").read()
        blocks = dict(re.findall(
            r'<record id="(bk_\d+)"[^>]*>(.*?)</record>', xml, re.S))
        for b in self.bookings:
            blk = blocks[b["xid"]]
            h1, m1 = divmod(b["start_min"], 60)
            self.assertIn(f"days={b['day']}, hour={h1}, minute={m1},", blk)
            h2, m2 = divmod(b["start_min"] + b["dur"], 60)
            self.assertIn(f"days={b['day']}, hour={h2}, minute={m2},", blk)
            self.assertIn(f'ref="{b["res"]}"', blk)
            self.assertIn(f'ref="{b["partner"]}"', blk)


class TestFideliteMoteurReel(unittest.TestCase):
    def test_points_conformes_au_bareme_reel(self):
        for m in PLAN["moves"]:
            if m["amount"] is not None:
                self.assertEqual(
                    m["points"],
                    _points_for(m["amount"], CFG["rate_per_1000"],
                                CFG["min_amount"]),
                    m)

    def test_moves_slots_refletent_les_reservations_realisees(self):
        done = [(b["partner"], b["day"], b["amount"])
                for b in PLAN["bookings"]
                if b["state"] == "done" and b["amount"] >= 1000]
        slots = [(m["partner"], m["day"], m["amount"])
                 for m in PLAN["moves"]
                 if m["origin"].startswith("slot_")]
        self.assertEqual(sorted(done), sorted(slots))

    def test_tiers_reproduits_par_le_moteur_reel(self):
        by_partner = {}
        for m in PLAN["moves"]:
            if m["points"] <= 0:
                continue
            d = by_partner.setdefault(
                m["partner"], dict(spend=0.0, days=set(), domains=set()))
            d["spend"] += m["amount"] or 0
            d["days"].add(m["day"])
            if m["origin"] != "manual":
                d["domains"].add(m["origin"])
        for pxid, exp in PLAN["expected_tiers"].items():
            d = by_partner.get(
                pxid, dict(spend=0.0, days=set(), domains=set()))
            self.assertEqual(
                _tier_for(d["spend"], len(d["days"]),
                          len(d["domains"]), CFG),
                exp["tier"], pxid)

    def test_partners_xml_portent_le_tier_attendu(self):
        xml = open(os.path.join(MOD, "data", "05_partners.xml"),
                   encoding="utf-8").read()
        blocks = dict(re.findall(
            r'<record id="(partner_[^"]+)"[^>]*>(.*?)</record>', xml, re.S))
        for pxid, exp in PLAN["expected_tiers"].items():
            self.assertIn(
                f'<field name="loyalty_tier">{exp["tier"]}</field>',
                blocks[pxid], pxid)

    def test_mix_de_statuts_pour_la_demo(self):
        tiers = [e["tier"] for e in PLAN["expected_tiers"].values()]
        self.assertGreaterEqual(tiers.count("vvip"), 2)
        self.assertGreaterEqual(tiers.count("vip"), 4)
        self.assertGreaterEqual(tiers.count("standard"), 15)

    def test_ajustements_manuels_traces(self):
        manuels = [m for m in PLAN["moves"] if m["origin"] == "manual"]
        self.assertGreaterEqual(len(manuels), 3)
        self.assertTrue(any(m["points"] < 0 for m in manuels))



class TestHotelDemo(unittest.TestCase):
    """Volet hôtelier : ce que le dashboard PMS lit doit être vivant."""

    @classmethod
    def setUpClass(cls):
        cls.h = PLAN["hotel"]
        cls.stays = cls.h["stays"]
        cls.sellable = [r for r, v in cls.h["rooms"].items()
                        if not v["out"]]

    def test_aucun_chevauchement_par_chambre(self):
        nights = {}
        for s in self.stays:
            if s["state"] in ("cancelled", "no_show"):
                continue
            for n in range(s["cin"], s["cout"]):
                k = (s["room"], n)
                self.assertNotIn(k, nights,
                                 "%s chevauche %s" % (s["xid"], nights.get(k)))
                nights[k] = s["xid"]

    def test_etats_coherents_au_temps(self):
        for s in self.stays:
            st = s["state"]
            if st == "checked_out":
                self.assertLessEqual(s["cout"], 0, s["xid"])
            elif st == "checked_in":
                self.assertLessEqual(s["cin"], 0, s["xid"])
                self.assertGreaterEqual(s["cout"], 0, s["xid"])
            elif st in ("confirmed", "draft"):
                self.assertGreaterEqual(s["cin"], 0, s["xid"])
            elif st == "no_show":
                self.assertLess(s["cout"], 0, s["xid"])

    def test_photo_du_jour_garantie(self):
        inhouse = [s for s in self.stays if s["state"] == "checked_in"]
        arrivals = [s for s in self.stays
                    if s["state"] == "confirmed" and s["cin"] == 0]
        departs = [s for s in inhouse if s["cout"] == 0]
        self.assertGreaterEqual(len(inhouse), 3)
        self.assertGreaterEqual(len(arrivals), 2)
        self.assertGreaterEqual(len(departs), 1)

    def test_occupation_passee_credible(self):
        occ = {}
        for s in self.stays:
            if s["state"] in ("cancelled", "no_show", "draft"):
                continue
            for n in range(s["cin"], s["cout"]):
                occ[n] = occ.get(n, 0) + 1
        rates = [occ.get(d, 0) / len(self.sellable)
                 for d in range(-30, 0)]
        avg = sum(rates) / len(rates)
        self.assertGreater(avg, 0.5, "occupation moyenne trop basse")
        self.assertLess(avg, 0.95, "occupation irréaliste")
        self.assertTrue(all(r <= 1.0 for r in rates))

    def test_adultes_dans_la_capacite(self):
        for s in self.stays:
            cap = self.h["types"][s["type"]]["cap"]
            self.assertGreaterEqual(s["adults"], 1, s["xid"])
            self.assertLessEqual(s["adults"], cap, s["xid"])

    def test_folios_bijection_et_etats(self):
        by_stay = {f["stay"]: f for f in self.h["folios"]}
        for s in self.stays:
            if s["state"] in ("checked_in", "checked_out"):
                self.assertIn(s["xid"], by_stay, s["xid"])
                fstate = by_stay[s["xid"]]["state"]
                if s["state"] == "checked_in":
                    self.assertEqual(fstate, "open", s["xid"])
                else:
                    self.assertIn(fstate, ("paid", "invoiced"), s["xid"])
            else:
                self.assertNotIn(s["xid"], by_stay, s["xid"])

    def test_lignes_nuitee_exactes_dans_le_xml(self):
        xml = open(os.path.join(MOD, "data", "12_hotel_folios.xml"),
                   encoding="utf-8").read()
        lines = re.findall(
            r'<record id="fl_\d+" model="aite.hotel.folio.line">(.*?)'
            r"</record>", xml, re.S)
        per_folio, dates = {}, {}
        for blk in lines:
            if '<field name="line_type">room</field>' not in blk:
                continue
            fol = re.search(r'name="folio_id" ref="(folio_stay_\d+)"',
                            blk).group(1)
            per_folio[fol] = per_folio.get(fol, 0) + 1
            day = int(re.search(r"days=(-?\d+)", blk).group(1))
            dates.setdefault(fol, []).append(day)
            self.assertIn('ref="' + fol.replace("folio_", "") + '_l"', blk)
        stay_by_xid = {s["xid"]: s for s in self.stays}
        for f in self.h["folios"]:
            s = stay_by_xid[f["stay"]]
            self.assertEqual(per_folio.get(f["xid"], 0),
                             s["cout"] - s["cin"], f["xid"])
            self.assertEqual(sorted(dates[f["xid"]]),
                             list(range(s["cin"], s["cout"])), f["xid"])

    def test_prix_nuit_egal_tarif_du_type(self):
        for s in self.stays:
            self.assertEqual(
                s["price"], self.h["types"][s["type"]]["price"], s["xid"])

    def test_chaque_type_a_du_chiffre(self):
        types_avec_ca = {s["type"] for s in self.stays
                         if s["state"] in ("checked_in", "checked_out")}
        self.assertEqual(types_avec_ca, set(self.h["types"]))

    def test_volume_hotel(self):
        self.assertGreaterEqual(len(self.stays), 100)
        self.assertGreaterEqual(len(self.h["folios"]), 60)



class TestBoutiqueDemo(unittest.TestCase):
    """Volet boutique : stocks, seuils et statuts prouvés par _metrics."""

    @classmethod
    def setUpClass(cls):
        cls.b = PLAN["boutique"]
        code = open(os.path.join(
            ADDONS, "aite_stock_dashboard", "models",
            "stock_dashboard.py"), encoding="utf-8").read()
        m = re.search(
            r"^    def _metrics\(.*?(?=^    @staticmethod|^    @api\.|"
            r"^    # -{10,}|^    def )", code, re.S | re.M)
        ns = {}
        exec(textwrap.dedent(m.group(0)), ns)
        cls._metrics = staticmethod(ns["_metrics"])

    def test_tous_les_stockables_ont_une_quantite(self):
        self.assertGreaterEqual(self.b["storables"], 55)
        self.assertEqual(len(self.b["quants"]), self.b["storables"])

    def test_ruptures_a_zero_et_les_autres_positifs(self):
        for xid, qty in self.b["quants"].items():
            if xid in self.b["expected"]["rupture"]:
                self.assertEqual(qty, 0.0, xid)
            else:
                self.assertGreater(qty, 0.0, xid)

    def test_statuts_reproduits_par_le_moteur_reel(self):
        expected_r = set(self.b["expected"]["rupture"])
        expected_s = set(self.b["expected"]["sous_seuil"])
        got_r, got_s = set(), set()
        for xid, seuil in self.b["thresholds"].items():
            m = self._metrics(
                stock=self.b["quants"][xid], vday=0.0, lead=5,
                cost=10000.0, sec_days=3, horizon_days=7,
                critical_days=2, dormant_days=60,
                manual_threshold=seuil, alert_active=True)
            if m["status"] == "Rupture":
                got_r.add(xid)
            elif m["status"] == "Sous seuil":
                got_s.add(xid)
            else:
                self.assertEqual(m["status"], "OK", xid)
        self.assertEqual(got_r, expected_r)
        self.assertEqual(got_s, expected_s)

    def test_sous_seuil_strictement_sous_le_seuil(self):
        for xid in self.b["expected"]["sous_seuil"]:
            self.assertLessEqual(
                self.b["quants"][xid], self.b["thresholds"][xid], xid)

    def test_fournisseurs_presents(self):
        xml = open(os.path.join(MOD, "data", "13_boutique_stock.xml"),
                   encoding="utf-8").read()
        self.assertGreaterEqual(self.b["suppliers"], 5)
        self.assertEqual(
            xml.count('<field name="supplier_rank" eval="1"/>'),
            self.b["suppliers"])
        # La caisse n'est plus déclarée en XML : créer un pos.config exige
        # un plan comptable, et l'installation échouait sur une base qui
        # n'en a pas. Elle est créée par le générateur (voir test suivant).
        self.assertNotIn('model="pos.config"', xml)

    def test_caisse_boutique_creee_par_le_generateur(self):
        src = open(os.path.join(MOD, "models", "demo_generator.py"),
                   encoding="utf-8").read()
        body = re.search(r"def _ensure_pos_config\(self\):(.*?)\n    def ",
                         src, re.S)
        self.assertIsNotNone(body)
        body = body.group(1)
        # passe son tour proprement sans journal de trésorerie
        self.assertIn("has_bank_journal", body)
        self.assertIn("'limit_categories': True", body)
        allowed = set(re.findall(r"'(pos_cat_[a-z]+)'", body))
        self.assertIn("pos_cat_boutique", allowed)
        # chaque produit boutique porte une catégorie POS autorisée
        prods = open(os.path.join(MOD, "data",
                                  "03_products_boutique.xml"),
                     encoding="utf-8").read()
        used = set(re.findall(r"ref\('pos_(cat_[a-z]+)'\)", prods))
        used = {"pos_" + u for u in used}
        manquantes = used - allowed
        self.assertFalse(
            manquantes,
            "catégories produits absentes de la caisse : %s" % manquantes)

    def test_quants_uniques_par_produit(self):
        xml = open(os.path.join(MOD, "data", "13_boutique_stock.xml"),
                   encoding="utf-8").read()
        refs = re.findall(
            r'<record id="quant_(prod_\d+)" model="stock.quant"', xml)
        self.assertEqual(len(refs), len(set(refs)))
        self.assertEqual(
            len(refs),
            sum(1 for q in self.b["quants"].values() if q > 0))


if __name__ == "__main__":
    unittest.main(verbosity=2)
