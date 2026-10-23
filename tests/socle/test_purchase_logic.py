# -*- coding: utf-8 -*-
"""
Tests de la logique métier du tableau de bord Achats & Fournisseurs.

Comme pour le module Stock : on **extrait le code source réel** des
fonctions pures depuis ``models/purchase_dashboard.py`` (``_bucket``,
``_invoice_metrics``, ``_order_metrics``, ``_price_metrics``,
``_supplier_badge``, ``_dpo``) et on l'exécute. Les scénarios reprennent
les 28 assertions du prototype HTML validé, plus les cas limites.
"""
import json
import os
import re
import shutil
import subprocess
import textwrap
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ADDONS = os.path.normpath(os.path.join(HERE, '..', '..', 'addons'))
MODULE_FILE = os.path.join(
    ADDONS, 'aite_purchase_dashboard', 'models', 'purchase_dashboard.py')


def _load(names):
    src = open(MODULE_FILE, encoding='utf-8').read()
    ns = {}
    for name in names:
        m = re.search(
            r'^    def %s\(.*?(?=^    @staticmethod|^    # -{10,}|^    def )'
            % name, src, re.S | re.M)
        assert m, "%s introuvable" % name
        exec(compile(textwrap.dedent(m.group(0)), MODULE_FILE, 'exec'), ns)
    return ns


_ns = _load(['_bucket', '_invoice_metrics', '_order_metrics',
             '_price_metrics', '_supplier_badge', '_dpo'])
_bucket = _ns['_bucket']
_invoice_metrics = _ns['_invoice_metrics']
_order_metrics = _ns['_order_metrics']
_price_metrics = _ns['_price_metrics']
_supplier_badge = _ns['_supplier_badge']
_dpo = _ns['_dpo']


class TestBuckets(unittest.TestCase):
    """Tranches de balance âgée par jours de retard (bornes incluses)."""

    def test_prototype_cases(self):
        self.assertEqual(_bucket(73), 3)   # SDV-1108 : 61–90 j
        self.assertEqual(_bucket(35), 2)   # UCB-3312 : 31–60 j
        self.assertEqual(_bucket(14), 1)   # GC-88412 : 1–30 j
        self.assertEqual(_bucket(0), 0)    # non échu

    def test_bornes(self):
        self.assertEqual(_bucket(30), 1)
        self.assertEqual(_bucket(31), 2)
        self.assertEqual(_bucket(60), 2)
        self.assertEqual(_bucket(61), 3)
        self.assertEqual(_bucket(90), 3)
        self.assertEqual(_bucket(91), 4)


class TestInvoiceStatus(unittest.TestCase):
    """Statuts de facture selon retard / fenêtre d'échéance."""

    def test_en_retard(self):
        m = _invoice_metrics(1140000, 7, 0, 7)
        self.assertEqual((m['status'], m['urgency']), ('En retard', 0))

    def test_retard_un_jour(self):
        m = _invoice_metrics(210000, 1, 0, 7)
        self.assertEqual(m['status'], 'En retard')

    def test_a_payer_bientot(self):
        m = _invoice_metrics(1980000, 0, 3, 7)
        self.assertEqual((m['status'], m['urgency']),
                         ('À payer bientôt', 1))

    def test_a_echoir(self):
        m = _invoice_metrics(1720000, 0, 16, 7)
        self.assertEqual(m['status'], 'À échoir')

    def test_fenetre_configurable(self):
        # soon 7 → À échoir ; soon 20 → À payer bientôt (le flip du proto)
        self.assertEqual(
            _invoice_metrics(1720000, 0, 16, 7)['status'], 'À échoir')
        self.assertEqual(
            _invoice_metrics(1720000, 0, 16, 20)['status'],
            'À payer bientôt')

    def test_payee(self):
        m = _invoice_metrics(0, 0, 0, 7)
        self.assertEqual((m['status'], m['urgency']), ('Payée', 5))


class TestOrderMetrics(unittest.TestCase):
    """OTIF strict vs badge toléré — le cœur de la nuance OTD/OTIF."""

    def test_recue_conforme(self):
        m = _order_metrics(False, 0, True, 2)
        self.assertEqual(m['status'], 'Reçue conforme')
        self.assertTrue(m['otif'])

    def test_a_lheure_mais_incomplete(self):
        # PO-0295 du prototype : ponctuelle MAIS incomplète → OTIF ✗
        m = _order_metrics(False, 0, False, 2)
        self.assertTrue(m['on_time'])
        self.assertFalse(m['otif'])
        self.assertEqual(m['status'], 'Reçue incomplète')

    def test_retard_tolere_badge_mais_otif_strict(self):
        # PO-0288 : 2 j de retard, seuil 2 → badge conforme, OTIF ✗
        m = _order_metrics(False, 2, True, 2)
        self.assertEqual(m['status'], 'Reçue conforme')
        self.assertFalse(m['otif'])

    def test_seuil_un_jour_flip_badge(self):
        m = _order_metrics(False, 2, True, 1)
        self.assertEqual(m['status'], 'Reçue en retard')

    def test_en_attente(self):
        m = _order_metrics(True, 0, None, 2)
        self.assertEqual(m['status'], 'En attente')
        self.assertIsNone(m['otif'])

    def test_en_attente_en_retard(self):
        m = _order_metrics(True, 5, None, 2)
        self.assertEqual(m['status'], 'En retard')


class TestPriceMetrics(unittest.TestCase):
    """Badges de variation de prix et impact annuel."""

    def test_castel_hausse_forte(self):
        m = _price_metrics(7800, 8400, 340, 5.0)
        self.assertAlmostEqual(m['delta'], 7.6923, places=3)
        self.assertEqual(m['badge'], 'Hausse forte')
        self.assertEqual(m['impact'], 600 * 340 * 12)

    def test_seuil_10_plus_de_forte(self):
        m = _price_metrics(7800, 8400, 340, 10.0)
        self.assertEqual(m['badge'], 'Hausse')

    def test_baisse(self):
        m = _price_metrics(3400, 3300, 78, 5.0)
        self.assertEqual(m['badge'], 'Baisse')
        self.assertLess(m['impact'], 0)

    def test_stable(self):
        m = _price_metrics(10200, 10200, 82, 5.0)
        self.assertEqual(m['badge'], 'Stable')
        self.assertEqual(m['impact'], 0)

    def test_prix_zero_sans_division(self):
        m = _price_metrics(0, 500, 10, 5.0)
        self.assertEqual(m['delta'], 0.0)


class TestSupplierBadge(unittest.TestCase):
    """Badge fournisseur : dépendance > retards > OK > inactif."""

    def test_sabc_dependance(self):
        b = _supplier_badge(71.5, 1140000, 7700000, 40.0)
        self.assertEqual(b['badge'], 'Dépendance')

    def test_seuil_80_bascule_retards(self):
        # Le flip du prototype : dep=80 → SABC (retards>0) badge Retards
        b = _supplier_badge(71.5, 1140000, 7700000, 80.0)
        self.assertEqual(b['badge'], 'Retards')

    def test_ok(self):
        b = _supplier_badge(12.0, 0, 640000, 40.0)
        self.assertEqual(b['badge'], 'OK')

    def test_inactif(self):
        b = _supplier_badge(0, 0, 0, 40.0)
        self.assertEqual(b['badge'], 'Inactif')


class TestDpo(unittest.TestCase):

    def test_prototype(self):
        # 8 450 000 / 10 765 000 × 30 ≈ 23,55 j
        self.assertAlmostEqual(
            _dpo(8450000, 10765000, 30), 23.55, places=1)

    def test_sans_achats(self):
        self.assertEqual(_dpo(500000, 0, 30), 0.0)



# ----------------------------------------------------------------------
# Code JS du tableau de bord (écarts n° 6, 37, 38, 41, 69) : fonctions de
# ``static/src/js/services/utils.js`` exécutées par Node, dans le fuseau
# de Douala (UTC+1), horloge figée.
# ----------------------------------------------------------------------

JS_UTILS = os.path.join(ADDONS, 'aite_purchase_dashboard', 'static', 'src',
                        'js', 'services', 'utils.js')
JS_XML = os.path.join(ADDONS, 'aite_purchase_dashboard', 'static', 'src',
                      'xml', 'dashboard.xml')
JS_VIEW = os.path.join(ADDONS, 'aite_purchase_dashboard', 'static', 'src',
                       'js', 'views', 'purchase_dashboard_view.js')
NODE = shutil.which('node')


def _js_functions(names):
    with open(JS_UTILS, encoding='utf-8') as fh:
        src = fh.read()
    out = []
    for name in names:
        m = re.search(r'^(?:export )?function %s\(.*?^}' % name, src,
                      re.S | re.M)
        assert m, "%s introuvable" % name
        out.append(re.sub(r'^export ', '', m.group(0)))
    return "\n".join(out)


def _node(code, now=None, tz='Africa/Douala'):
    clock = ""
    if now:
        y, mo, d, h, mi = now
        clock = (
            "const _RD = Date;"
            "class _FD extends _RD { constructor(...a) {"
            " if (a.length) { super(...a); } else {"
            " super(%d, %d, %d, %d, %d, 0); } }"
            " static now() { return new _FD().getTime(); } }"
            "globalThis.Date = _FD;" % (y, mo - 1, d, h, mi))
    env = dict(os.environ, TZ=tz)
    res = subprocess.run([NODE, '-e', clock + code], capture_output=True,
                         text=True, env=env, timeout=60)
    if res.returncode:
        raise AssertionError(res.stderr)
    return json.loads(res.stdout)


def _sp(text):
    """Espaces insécables (séparateur de milliers fr-FR) → espace simple."""
    return text.replace('\u202f', ' ').replace('\u00a0', ' ')


@unittest.skipUnless(NODE, "node absent : code JS non exécuté")
class TestJsPeriodeEtFormats(unittest.TestCase):

    def _range(self, key, now):
        code = _js_functions(['localIsoDate', 'periodRange'])
        return _node(code + "console.log(JSON.stringify(periodRange(%s)));"
                     % json.dumps(key), now=now)

    def test_ce_mois_commence_le_1er_a_douala(self):
        """n° 38 : « Ce mois » démarrait le 30/09 (toISOString en UTC)."""
        self.assertEqual(self._range('month', (2026, 10, 15, 10, 0)),
                         {'date_from': '2026-10-01',
                          'date_to': '2026-10-15'})
        self.assertEqual(self._range('today', (2026, 10, 1, 0, 30)),
                         {'date_from': '2026-10-01',
                          'date_to': '2026-10-01'})
        # jeudi 15/10/2026 → semaine du lundi 12
        self.assertEqual(self._range('week', (2026, 10, 15, 0, 15)),
                         {'date_from': '2026-10-12',
                          'date_to': '2026-10-15'})
        self.assertEqual(self._range('quarter', (2026, 10, 15, 10, 0)),
                         {'date_from': '2026-08-01',
                          'date_to': '2026-10-15'})

    def test_pourcentages_a_la_francaise(self):
        """n° 41 : décimale fixe, virgule, espace insécable avant %."""
        out = _node(_js_functions(['fmtPct']) + "console.log(JSON.stringify("
                    "[fmtPct(40), fmtPct(5), fmtPct(87.54), fmtPct(0)]));")
        self.assertEqual(out, ["40,0\u00a0%", "5,0\u00a0%", "87,5\u00a0%",
                               "0,0\u00a0%"])

    def test_durees_une_decimale(self):
        """n° 41 : « 23 j » ici, « 23,0 j » au cockpit pour le même DPO."""
        out = _node(_js_functions(['fmtDays']) + "console.log(JSON.stringify("
                    "[fmtDays(23), fmtDays(2.46), fmtDays(null)]));")
        self.assertEqual(out, ["23,0 j", "2,5 j", "0,0 j"])

    def test_dates_affichees_jj_mm_aaaa(self):
        """n° 37 : colonnes de date des achats en AAAA-MM-JJ."""
        out = _node(_js_functions(['fmtDate']) + "console.log(JSON.stringify("
                    "[fmtDate('2026-10-14'), fmtDate(''), fmtDate(null)]));")
        self.assertEqual(out, ['14/10/2026', '', ''])

    def test_pas_de_moins_zero(self):
        """n° 6 et 69 : « −0 FCFA » quand rien n'est en retard."""
        out = _node(_js_functions(['fmtMoney', 'fmtNegMoney'])
                    + "console.log(JSON.stringify([fmtNegMoney(0, 'FCFA'),"
                    " fmtNegMoney(0.3, 'FCFA'), fmtNegMoney(null, 'FCFA'),"
                    " fmtNegMoney(1500, 'FCFA')]));")
        self.assertEqual([_sp(x) for x in out],
                         ['0 FCFA', '0 FCFA', '0 FCFA', '−1 500 FCFA'])

    def test_fenetre_des_echeances_suit_le_reglage(self):
        """n° 69 : « À payer sous 8–30 j » figé alors que la fenêtre
        d'alerte (7 j par défaut) se règle."""
        out = _node(_js_functions(['dueWindowLabel'])
                    + "console.log(JSON.stringify([dueWindowLabel(7),"
                    " dueWindowLabel(14), dueWindowLabel(29),"
                    " dueWindowLabel(30)]));")
        self.assertEqual(out[0], "À payer sous 8–30 j")
        self.assertEqual(out[1], "À payer sous 15–30 j")
        self.assertEqual(out[2], "À payer à 30 j")
        self.assertNotIn("31", out[3])

    def test_seuils_dits_comme_ils_sont_calcules(self):
        """n° 69 : le calcul se déclenche DÈS le seuil (≥) ; n° 42 : sigles
        DPO et OTIF expliqués en français."""
        with open(JS_XML, encoding='utf-8') as fh:
            xml = fh.read()
        # (la tolérance de retard de livraison, elle, est stricte : « au-delà »
        # y reste juste.)
        for wrong in ("'Hausses > '", "au-delà de\n",
                      "« Hausse forte » au-delà du seuil",
                      "Au-delà du seuil, renégociez",
                      "badge au-delà", "'À payer sous 8–30 j'",
                      "'DPO — délai moyen de paiement'",
                      "'Taux de service (OTIF)'", "'OTIF moyen'",
                      "'OTIF (période)'"):
            self.assertFalse(wrong in xml, wrong)
        self.assertTrue("'Hausses ≥ '" in xml)

    def test_mots_en_toutes_lettres(self):
        """Reprise du n° 42 : « 3 cmd », « auj. », axe « S1 … S5+ »."""
        with open(JS_XML, encoding='utf-8') as fh:
            xml = fh.read()
        with open(JS_VIEW, encoding='utf-8') as fh:
            view = fh.read()
        self.assertFalse("' cmd'" in xml)
        self.assertFalse('"auj."' in view)
        self.assertFalse('"S1"' in view)
        out = _node(_js_functions(['fmtInt', 'fmtCount', 'scheduleLabels'])
                    + "console.log(JSON.stringify([fmtCount(1, 'commande',"
                    " 'commandes'), fmtCount(0, 'commande', 'commandes'),"
                    " fmtCount(3, 'commande', 'commandes'),"
                    " scheduleLabels()]));")
        self.assertEqual(out[:3], ["1 commande", "0 commande",
                                   "3 commandes"])
        # Mêmes tranches que ``scheduleWeeks`` : semaine k = jours avant
        # échéance de 7k à 7k + 6 ; la première prend aussi les échues.
        self.assertEqual(out[3], ["Échu ou sous 7 j", "7 à 13 j",
                                  "14 à 20 j", "21 à 27 j", "28 à 34 j",
                                  "35 j et +"])



class TestGraphiquesDesOnglets(unittest.TestCase):
    """Relevé en vérifiant la reprise (n° 42) : à la première ouverture des
    onglets « Dettes & échéancier » et « Prix & variations », les graphiques
    restaient vides — ``setTab`` les dessinait dans un requestAnimationFrame
    qui passait AVANT le rendu de l'onglet par OWL (canevas absents)."""

    def test_graphiques_dessines_apres_le_rendu_de_l_onglet(self):
        with open(JS_VIEW, encoding='utf-8') as fh:
            view = fh.read()
        m = re.search(r"^    setTab\(tab\) \{.*?^    \}", view, re.S | re.M)
        self.assertTrue(m)
        self.assertNotIn("renderTabCharts", m.group(0))
        self.assertIn("onPatched(", view)


if __name__ == '__main__':
    unittest.main(verbosity=1)
