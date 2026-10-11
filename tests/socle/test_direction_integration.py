# -*- coding: utf-8 -*-
"""
Tests d'intégration — aite_direction_dashboard.

Cohérence entre les artefacts du module (manifest, backend, JS, XML,
SCSS, vues) et avec les quatre moteurs orchestrés. Inclut la GATE
SCROLL : la classe racine du template Dashboard doit porter la règle
height 100 % + overflow-y auto (leçon du correctif défilement).
"""
import ast
import os
import re
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


if __name__ == "__main__":
    unittest.main(verbosity=1)
