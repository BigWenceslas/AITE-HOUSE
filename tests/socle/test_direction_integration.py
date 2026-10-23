# -*- coding: utf-8 -*-
"""
Tests d'intégration — aite_direction_dashboard.

Cohérence entre les artefacts du module (manifest, backend, JS, XML,
SCSS, vues) et avec les quatre moteurs orchestrés. Inclut la GATE
SCROLL : la classe racine du template Dashboard doit porter la règle
height 100 % + overflow-y auto (leçon du correctif défilement).
"""
import ast
import json
import os
import re
import shutil
import subprocess
import unittest
from xml.dom import minidom

HERE = os.path.dirname(os.path.abspath(__file__))
ADDONS = os.path.normpath(os.path.join(HERE, '..', '..', 'addons'))
MOD = os.path.join(ADDONS, "aite_direction_dashboard")


def read(*parts):
    with open(os.path.join(MOD, *parts), encoding="utf-8") as fh:
        return fh.read()


MANIFEST = ast.literal_eval(read("__manifest__.py"))
PY = read("models", "direction_dashboard.py")
JS = read("static", "src", "js", "direction_dashboard.js")
XML = read("static", "src", "xml", "direction_dashboard.xml")
SCSS = read("static", "src", "scss", "direction_dashboard.scss")
VIEWS = read("views", "direction_views.xml")

ENGINES = {
    "pos": os.path.join(ADDONS, "aite_pos_analytics",
                        "models", "pos_dashboard.py"),
    "cred": os.path.join(ADDONS, "aite_pos_credit",
                         "models", "pos_credit_dashboard.py"),
    "stock": os.path.join(ADDONS, "aite_stock_dashboard", "models",
                          "stock_dashboard.py"),
    "pur": os.path.join(ADDONS, "aite_purchase_dashboard",
                        "models", "purchase_dashboard.py"),
}


class TestManifest(unittest.TestCase):
    def test_version_et_application(self):
        self.assertTrue(MANIFEST["version"].startswith("18.0."))
        self.assertTrue(MANIFEST["application"])

    def test_depends_les_quatre_moteurs(self):
        self.assertEqual(set(MANIFEST["depends"]), {
            "aite_pos_analytics", "aite_pos_credit",
            "aite_stock_dashboard", "aite_purchase_dashboard"})

    def test_data_existent_sur_disque(self):
        for f in MANIFEST["data"]:
            self.assertTrue(
                os.path.isfile(os.path.join(MOD, f)), f)

    def test_assets_existent_sur_disque(self):
        assets = MANIFEST["assets"]["web.assets_backend"]
        self.assertEqual(len(assets), 3)
        for a in assets:
            rel = a.split("aite_direction_dashboard/", 1)[1]
            self.assertTrue(
                os.path.isfile(os.path.join(MOD, rel)), a)


class TestActionEtMenu(unittest.TestCase):
    def test_tag_action_xml_egale_registre_js(self):
        tag_xml = re.search(
            r'<field name="tag">([^<]+)</field>', VIEWS).group(1)
        tag_js = re.search(
            r'registry\.category\("actions"\)\.add\("([^"]+)"',
            JS).group(1)
        self.assertEqual(tag_xml, tag_js)
        self.assertEqual(tag_xml, "aite_direction_dashboard.dashboard")

    def test_menu_reserve_aux_responsables(self):
        self.assertIn('groups="point_of_sale.group_pos_manager"',
                      VIEWS)
        self.assertIn('action="action_direction_dashboard"', VIEWS)

    def test_vues_xml_valides(self):
        minidom.parseString(VIEWS)
        minidom.parseString(XML)


class TestGateScroll(unittest.TestCase):
    """Pattern Analytics (la reference qui defile en production) :
    racine unique flex plein cadre + corps interne qui scrolle.
    Interdit la resurgence du wrapper -root / o_action."""

    def test_wrapper_obsolete_absent(self):
        self.assertNotIn("add-dashboard-root", XML)
        self.assertNotIn("add-dashboard-root", SCSS)
        self.assertNotIn("add-dashboard-root", JS)

    def test_racine_unique_sans_o_action(self):
        i = XML.index('t-name="aite_direction_dashboard.Dashboard"')
        racine = XML[i:i + 200]
        self.assertIn('<div class="add-dashboard">', racine)
        self.assertNotIn("o_action", racine)

    def test_racine_flex_plein_cadre(self):
        i = SCSS.index(".add-dashboard {")
        bloc = SCSS[i:i + 900]
        for prop in ("display: flex", "flex-direction: column",
                     "height: 100%", "overflow: hidden"):
            self.assertIn(prop, bloc, prop)

    def test_corps_defilant(self):
        i = SCSS.index(".add-dashboard-body {")
        bloc = SCSS[i:SCSS.index("}", i)]
        for prop in ("flex: 1 1 auto", "overflow-y: auto",
                     "overflow-x: hidden", "min-height: 0"):
            self.assertIn(prop, bloc, prop)
        self.assertIn("add-dashboard-body", XML)

    def test_zone_fixe_filtres_et_onglets(self):
        self.assertIn("add-dashboard-top", XML)
        self.assertIn(".add-dashboard-top {", SCSS)


class TestTemplates(unittest.TestCase):
    NAMES = re.findall(r't-name="([^"]+)"', XML)

    def test_t_names_uniques_et_prefixes(self):
        self.assertEqual(len(self.NAMES), len(set(self.NAMES)))
        for n in self.NAMES:
            self.assertTrue(
                n.startswith("aite_direction_dashboard."), n)

    def test_composants_utilises_declares_dans_js(self):
        used = set(re.findall(r"<([A-Z]\w+)", XML))
        m = re.search(r"static components = \{([^}]*)\}", JS)
        declared = set(re.findall(r"(\w+)", m.group(1)))
        self.assertTrue(used <= declared, used - declared)

    def _attrs(self, tag):
        chunks = re.findall(r"<%s\b(.*?)/>" % tag, XML, re.S)
        attrs = set()
        for c in chunks:
            attrs |= set(re.findall(r'([\w-]+)="', c))
        return attrs - {"t-key", "t-if"}

    def test_props_kpicard(self):
        self.assertTrue(self._attrs("KpiCard") <= {
            "label", "value", "sub", "badge", "accent", "delta",
            "deltaLabel", "hint", "mega", "onClick"})

    def test_props_autres_composants(self):
        self.assertTrue(self._attrs("HBar") <= {
            "label", "pct", "color", "value", "hint"})
        self.assertTrue(self._attrs("TrendChart") <= {
            "rows", "currency"})
        self.assertTrue(self._attrs("MirrorAging") <= {
            "clients", "suppliers", "currency"})
        self.assertTrue(self._attrs("Heatmap") <= {"rows"})


class TestRpcCroises(unittest.TestCase):
    def test_appels_js_existent_en_python(self):
        calls = set(re.findall(
            r'orm\.call\(\s*(?:M|"aite\.direction\.dashboard")\s*,'
            r'\s*"(\w+)"', JS, re.S))
        self.assertEqual(calls, {
            "get_meta", "get_overview", "get_pos_tab",
            "get_credit_tab", "get_stock_tab", "get_purchase_tab",
            "get_actions"})
        for c in calls:
            self.assertIn("def %s(" % c, PY, c)

    def test_appels_python_existent_dans_les_moteurs(self):
        calls = re.findall(r"\b(pos|cred|stock|pur)\.(get_\w+)\(", PY)
        self.assertGreaterEqual(len(set(calls)), 18)
        for engine, meth in set(calls):
            path = ENGINES[engine]
            if not os.path.isfile(path):
                self.skipTest("source moteur absente : %s" % path)
            with open(path, encoding="utf-8") as fh:
                src = fh.read()
            self.assertIn("def %s(" % meth, src,
                          "%s.%s" % (engine, meth))

    def test_tags_drill_connus(self):
        m = re.search(r"const DRILL_TAGS = \{(.*?)\};", JS, re.S)
        tags = set(re.findall(r'"([\w.]+)"', m.group(1)))
        self.assertEqual(tags, {
            "aite_pos_analytics.dashboard",
            "aite_pos_credit_dashboard",
            "aite_stock_dashboard",
            "aite_purchase_dashboard"})


class TestGettersEtContrats(unittest.TestCase):
    GETTERS = ["netPositionSub", "qtyPerTicket", "posQty",
               "caisseLabel", "posCategories", "posPayments",
               "creditAging", "creditLinePoints", "creditLineLegend",
               "netFlowText", "stockByCat", "stockUnits",
               "stockCoverage", "penaltyText", "supplierChips",
               "purchaseSchedule", "priceUp", "priceUpCount",
               "dpoText"]

    def test_getters_du_xml_presents_dans_le_js(self):
        for g in self.GETTERS:
            self.assertIn(g, XML, "non utilisé : " + g)
            self.assertTrue(
                ("get %s(" % g) in JS or ("%s(" % g) in JS, g)

    def test_tranches_js_egales_python(self):
        py_keys = set(re.findall(
            r"'(\w+)':\s*\(\d+,\s*\d+\)",
            re.search(r"TRANCHES = \{(.*?)\}", PY, re.S).group(1)))
        js_keys = set(re.findall(
            r'key: "(\w+)"',
            re.search(r"const TRANCHES = \[(.*?)\];", JS,
                      re.S).group(1)))
        self.assertEqual(py_keys, js_keys)
        self.assertEqual(py_keys, {"matin", "am", "soir", "nuit"})

    def test_pas_de_math_dans_les_templates(self):
        self.assertNotIn("Math.", XML)


class TestFrontieresMoteurs(unittest.TestCase):
    """Leçon de l'incident coverage : normalisation systématique."""

    CLES_LISTES = ["'top_products': self._rows(",
                   "'categories': self._rows(",
                   "'payments': self._rows(",
                   "'aging': self._rows(",
                   "'top_debtors': self._rows(",
                   "'recent_payments': self._rows(",
                   "'by_category': self._rows(",
                   "'coverage': self._rows(",
                   "'top_value': self._rows(",
                   "'suppliers': self._rows(",
                   "'price_moves': self._rows("]

    def test_backend_normalise_chaque_liste_moteur(self):
        for cle in self.CLES_LISTES:
            self.assertIn(cle, PY, cle)
        self.assertGreaterEqual(PY.count("self._rows("), 15)

    def test_js_garde_aslist_en_double_filet(self):
        self.assertIn("function asList(", JS)
        i = JS.index("get stockCoverage()")
        self.assertIn("asList(", JS[i:i + 400])


class TestScss(unittest.TestCase):
    def test_accolades_equilibrees(self):
        self.assertEqual(SCSS.count("{"), SCSS.count("}"))

    def test_prefixe_add_sur_les_classes_racines(self):
        for line in SCSS.splitlines():
            m = re.match(r"^\.([\w-]+)", line)
            if m:
                self.assertTrue(m.group(1).startswith("add-"),
                                line.strip())


# ----------------------------------------------------------------------
# Code JS exécuté par Node dans le fuseau de Douala (UTC+1) — écarts
# n° 37, 38, 41, 42 et 70 (règle 6 : dates, pourcentages, période).
# ----------------------------------------------------------------------

NODE = shutil.which("node")


def _js_functions(names):
    out = []
    for name in names:
        m = re.search(r"^(?:export )?function %s\(.*?^}" % name, JS,
                      re.S | re.M)
        assert m, "%s introuvable" % name
        out.append(re.sub(r"^export ", "", m.group(0)))
    return "\n".join(out)


def _node(code, tz="Africa/Douala"):
    env = dict(os.environ, TZ=tz)
    res = subprocess.run([NODE, "-e", code], capture_output=True,
                         text=True, env=env, timeout=60)
    if res.returncode:
        raise AssertionError(res.stderr)
    return json.loads(res.stdout)


@unittest.skipUnless(NODE, "node absent : code JS non exécuté")
class TestJsPeriodeEtFormats(unittest.TestCase):

    def _range(self, key, today):
        code = _js_functions(["localIsoDate", "rangeFor"])
        return _node(code + "console.log(JSON.stringify(rangeFor(%s, %s)));"
                     % (json.dumps(key), json.dumps(today)))

    def test_ce_mois_commence_le_1er_a_douala(self):
        """n° 38 : « Du 30/09/2026 » — minuit local passé par
        toISOString() devenait la veille en UTC."""
        self.assertEqual(self._range("month", "2026-10-15"),
                         ["2026-10-01", "2026-10-15"])
        self.assertEqual(self._range("quarter", "2026-11-03"),
                         ["2026-10-01", "2026-11-03"])
        self.assertEqual(self._range("year", "2026-11-03"),
                         ["2026-01-01", "2026-11-03"])
        # jeudi 15/10/2026 → semaine du lundi 12
        self.assertEqual(self._range("week", "2026-10-15"),
                         ["2026-10-12", "2026-10-15"])
        self.assertEqual(self._range("today", "2026-10-01"),
                         ["2026-10-01", "2026-10-01"])

    def test_pourcentages_a_la_francaise(self):
        """n° 41 : virgule, espace insécable avant %, décimales fixées."""
        code = _js_functions(["fmtPct", "fmtDelta"])
        out = _node(code + "console.log(JSON.stringify([fmtPct(64),"
                    " fmtPct(64.25, 0), fmtPct(null), fmtDelta(12.5),"
                    " fmtDelta(-3)]));")
        self.assertEqual(out, ["64,0\u00a0%", "64\u00a0%", "—",
                               "▲ +12,5\u00a0%", "▼ 3,0\u00a0%"])

    def test_dates_affichees_jj_mm_aaaa(self):
        """n° 37 : échéances et remboursements affichés en AAAA-MM-JJ."""
        code = _js_functions(["fmtDate"])
        out = _node(code + "console.log(JSON.stringify([fmtDate("
                    "'2026-10-14'), fmtDate(''), fmtDate(null),"
                    " fmtDate('14/10/2026')]));")
        self.assertEqual(out, ["14/10/2026", "", "", "14/10/2026"])

    def test_delai_moyen_arrondi(self):
        """n° 41 : « Délai moyen de remboursement » sans arrondi."""
        code = _js_functions(["fmtDays"])
        out = _node(code + "console.log(JSON.stringify([fmtDays("
                    "12.3333333), fmtDays(0), fmtDays(null)]));")
        self.assertEqual(out, ["12,3 j", "0,0 j", "0,0 j"])

    def test_balance_agee_clients_classee_par_cle(self):
        """n° 70 : les bornes 30 / 60 / 90 du moteur Crédit étaient
        comparées à 31 / 61 / 91 — couleurs décalées d'une tranche."""
        code = _js_functions(["agingKey"])
        rows = [{"key": "0_30", "min": 0, "max": 30},
                {"key": "31_60", "min": 30, "max": 60},
                {"key": "61_90", "min": 60, "max": 90},
                {"key": "90p", "min": 90, "max": 10 ** 9},
                # format ancien, sans clé : repli sur les bornes
                {"min": 30, "max": 60}, {"min": 90, "max": None}]
        out = _node(code + "console.log(JSON.stringify(%s.map(agingKey)));"
                    % json.dumps(rows))
        self.assertEqual(out, ["0_30", "31_60", "61_90", "90p",
                               "31_60", "90p"])

    def test_libelles_sans_abreviation_ni_sigle_seul(self):
        """n° 42 et 70 : « cl. » compte des ardoises ; sigles anglais
        expliqués en français."""
        self.assertFalse("' cl.'" in XML)
        for label in ("label=\"'RevPAR'\"", "label=\"'OTIF'\"",
                      "'ADR — prix moyen par nuit'"):
            self.assertFalse(label in XML, label)
        self.assertFalse(".toISOString(" in JS)

    def test_taux_une_decimale_comme_les_ecrans_sources(self):
        """Reprise du n° 41 : OTIF « 88 % » ici, « 87,5 % » dans les
        Achats ; part échue « (12 %) » contre « 12,3 % » ; hausse de prix
        « +13 % » contre « +12,5 % »."""
        self.assertEqual(re.findall(r"pct\([^()]*?,\s*0\)", XML), [])
        self.assertEqual(re.findall(r"fmtPct\([^;]*?,\s*0\)", JS), [])

    def test_echeances_suivent_le_reglage_des_achats(self):
        """Reprise du n° 69 : « À payer sous 7 j » figé alors que le
        montant suit la fenêtre réglable du tableau de bord Achats."""
        self.assertFalse("'À payer sous 7 j'" in XML)
        self.assertFalse("' sous 7 j'" in XML)
        code = _js_functions(["dueSoonLabel"])
        out = _node(code + "console.log(JSON.stringify([dueSoonLabel(7),"
                    " dueSoonLabel(14), dueSoonLabel(undefined)]));")
        self.assertEqual(out, ["À payer sous 7 j", "À payer sous 14 j",
                               "À payer sous 7 j"])

    def test_mots_en_toutes_lettres(self):
        """Reprise du n° 42 : « réfs », « fact. », « S + 1 »."""
        self.assertFalse("réfs" in XML)
        self.assertFalse("' fact.'" in XML)
        self.assertFalse('"S + 1"' in JS)
        code = _js_functions(["fmtCount"])
        out = _node(code + "console.log(JSON.stringify([fmtCount(1,"
                    " 'facture', 'factures'), fmtCount(0, 'facture',"
                    " 'factures'), fmtCount(4, 'facture', 'factures'),"
                    " fmtCount(undefined, 'facture', 'factures')]));")
        self.assertEqual(out, ["1 facture", "0 facture", "4 factures",
                               "0 facture"])


if __name__ == "__main__":
    unittest.main(verbosity=1)
