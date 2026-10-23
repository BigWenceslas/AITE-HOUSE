# -*- coding: utf-8 -*-
"""
Tests du tableau de bord Direction (aite_exec_dashboard).

Extraction du code réel : ``_mix_rows`` (répartition par pôle),
``_last_months`` et ``_month_key`` (découpage mensuel) — puis miroirs de
la consolidation : sources par pôle, panier moyen, fenêtre de check-out
hébergement, fidélité optionnelle.
"""
import json
import os
import re
import shutil
import subprocess
import textwrap
import unittest
from datetime import date, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ADDONS = os.path.normpath(os.path.join(HERE, '..', '..', 'addons'))
SRC = os.path.join(ADDONS, 'aite_exec_dashboard', 'models',
                   'exec_dashboard.py')


def _extract(names):
    src = open(SRC, encoding='utf-8').read()
    ns = {'date': date}
    for name in names:
        m = re.search(
            r'^    def %s\(.*?(?=^    @staticmethod|^    @api\.|'
            r'^    # -{10,}|^    def )' % name,
            src, re.S | re.M)
        assert m, "%s introuvable" % name
        exec(compile(textwrap.dedent(m.group(0)), SRC, 'exec'), ns)
    return ns


_ns = _extract(['_mix_rows', '_month_key', '_last_months'])
_mix_rows = _ns['_mix_rows']
_month_key = _ns['_month_key']
_last_months = _ns['_last_months']


class TestMixRows(unittest.TestCase):

    def test_repartition_et_tri(self):
        # Hébergement 4,2 M · POS 2,8 M · prestations 1,0 M
        rows = _mix_rows(4200000, 2800000, 1000000)
        self.assertEqual([r['key'] for r in rows],
                         ['hotel', 'pos', 'slots'])
        self.assertEqual(rows[0]['pct'], 52.5)
        self.assertEqual(rows[1]['pct'], 35.0)
        self.assertEqual(rows[2]['pct'], 12.5)
        self.assertAlmostEqual(sum(r['pct'] for r in rows), 100.0)

    def test_pole_a_zero_conserve(self):
        rows = _mix_rows(0, 500000, 0)
        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[0]['key'], 'pos')
        self.assertEqual(rows[0]['pct'], 100.0)

    def test_tout_a_zero_sans_division(self):
        rows = _mix_rows(0, 0, 0)
        self.assertTrue(all(r['pct'] == 0.0 for r in rows))

    def test_valeurs_none_tolerees(self):
        rows = _mix_rows(None, 100000, None)
        self.assertEqual(rows[0]['amount'], 100000)


class TestMonthBuckets(unittest.TestCase):

    def test_month_key(self):
        self.assertEqual(_month_key(date(2026, 7, 20)), '2026-07')
        self.assertEqual(_month_key(date(2026, 1, 3)), '2026-01')

    def test_six_mois_ordre_chronologique(self):
        buckets = _last_months(6, date(2026, 7, 20))
        self.assertEqual(len(buckets), 6)
        self.assertEqual(buckets[0][0], '2026-02')
        self.assertEqual(buckets[-1][0], '2026-07')

    def test_bornes_de_bucket(self):
        buckets = _last_months(3, date(2026, 7, 20))
        key, start, nxt = buckets[-1]
        self.assertEqual((key, start, nxt),
                         ('2026-07', date(2026, 7, 1), date(2026, 8, 1)))

    def test_franchit_janvier(self):
        buckets = _last_months(6, date(2026, 2, 10))
        self.assertEqual([b[0] for b in buckets],
                         ['2025-09', '2025-10', '2025-11',
                          '2025-12', '2026-01', '2026-02'])

    def test_decembre_vers_janvier_borne(self):
        buckets = _last_months(2, date(2026, 1, 15))
        key, start, nxt = buckets[0]
        self.assertEqual((key, nxt), ('2025-12', date(2026, 1, 1)))


class TestConsolidation(unittest.TestCase):
    """Miroirs de get_kpis : une source par pôle, agrégats exacts."""

    def test_total_et_panier(self):
        hotel = 4200000
        pos_orders = [85000, 42000, 63000]     # réglées uniquement
        slots = [40000, 75000]
        pos_ca = sum(pos_orders)
        total = hotel + pos_ca + sum(slots)
        self.assertEqual(total, 4505000)
        basket = pos_ca / len(pos_orders)
        self.assertAlmostEqual(basket, 63333.33, places=2)

    def test_panier_sans_ticket(self):
        tickets = 0
        basket = 0.0 if not tickets else 1 / tickets
        self.assertEqual(basket, 0.0)

    def test_fenetre_checkout_hebergement(self):
        # Folio compté si le check-out (réel sinon prévu) est dans la
        # période — miroir de _hotel_folios.
        d0 = datetime(2026, 7, 1)
        d1 = datetime(2026, 7, 31, 23, 59, 59)
        folios = [
            (datetime(2026, 7, 5, 11), None, 300000),      # réel juillet
            (None, datetime(2026, 7, 28, 12), 450000),     # prévu juillet
            (datetime(2026, 8, 1, 10), None, 200000),      # août → exclu
            (None, None, 99000),                           # sans date → exclu
        ]
        kept = 0.0
        for (actual, planned, amount) in folios:
            out = actual or planned
            if out and d0 <= out <= d1:
                kept += amount
        self.assertEqual(kept, 750000)

    def test_fidelite_optionnelle(self):
        def points(has_loyalty, moves):
            if not has_loyalty:
                return 0
            return sum(p for p in moves if p > 0)
        self.assertEqual(points(False, [100, 50]), 0)
        self.assertEqual(points(True, [100, 50, -30]), 150)

    def test_series_evolution_alignees(self):
        # Miroir de get_evolution : 3 séries, même longueur que labels
        labels = [b[0] for b in _last_months(6, date(2026, 7, 20))]
        series = {'hotel': [0] * 6, 'pos': [0] * 6, 'slots': [0] * 6}
        self.assertTrue(all(len(s) == len(labels)
                            for s in series.values()))



# ----------------------------------------------------------------------
# Code JS du tableau de bord (écarts n° 2, 38, 41, 42, 70) : les fonctions
# de ``static/src/js/services/utils.js`` sont extraites et exécutées par
# Node, dans le fuseau de Douala (UTC+1), avec une horloge figée.
# ----------------------------------------------------------------------

JS_UTILS = os.path.join(ADDONS, 'aite_exec_dashboard', 'static', 'src',
                        'js', 'services', 'utils.js')
JS_XML = os.path.join(ADDONS, 'aite_exec_dashboard', 'static', 'src',
                      'xml', 'dashboard.xml')
NODE = shutil.which('node')


def _js_functions(path, names):
    src = open(path, encoding='utf-8').read()
    out = []
    for name in names:
        m = re.search(r'^(?:export )?function %s\(.*?^}' % name, src,
                      re.S | re.M)
        assert m, "%s introuvable" % name
        out.append(re.sub(r'^export ', '', m.group(0)))
    return "\n".join(out)


def _node(code, now=None, tz='Africa/Douala'):
    """Exécute ``code`` (qui affiche un JSON) ; ``now`` = [a, m, j, h, mn]
    fige l'horloge locale (mois de 1 à 12)."""
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


@unittest.skipUnless(NODE, "node absent : code JS non exécuté")
class TestJsPeriodeEtFormats(unittest.TestCase):

    def _range(self, key, now):
        code = _js_functions(JS_UTILS, ['localIsoDate', 'periodRange'])
        return _node(code + "console.log(JSON.stringify(periodRange(%s)));"
                     % json.dumps(key), now=now)

    def test_ce_mois_commence_le_1er_a_douala(self):
        """n° 38 : minuit local passé par toISOString() devenait la veille
        en UTC (« Période 2026-09-30 → … »)."""
        r = self._range('month', (2026, 10, 15, 10, 0))
        self.assertEqual(r, {'date_from': '2026-10-01',
                             'date_to': '2026-10-15'})

    def test_aujourdhui_juste_apres_minuit(self):
        r = self._range('month', (2026, 10, 1, 0, 30))
        self.assertEqual(r, {'date_from': '2026-10-01',
                             'date_to': '2026-10-01'})

    def test_trimestre_et_annee(self):
        self.assertEqual(self._range('quarter', (2026, 11, 3, 9, 0)),
                         {'date_from': '2026-10-01',
                          'date_to': '2026-11-03'})
        self.assertEqual(self._range('year', (2026, 11, 3, 9, 0)),
                         {'date_from': '2026-01-01',
                          'date_to': '2026-11-03'})

    def test_pourcentages_a_la_francaise(self):
        """n° 41 : « 64 % » ici, « 64,0 % » au cockpit — une décimale
        fixe, virgule, espace insécable avant %."""
        code = _js_functions(JS_UTILS, ['fmtPct', 'fmtDelta'])
        out = _node(code + "console.log(JSON.stringify([fmtPct(64),"
                    " fmtPct(56.04), fmtPct(0), fmtDelta(12.5),"
                    " fmtDelta(-3)]));")
        self.assertEqual(out, ["64,0\u00a0%", "56,0\u00a0%", "0,0\u00a0%",
                               "▲ +12,5\u00a0%", "▼ 3,0\u00a0%"])

    def test_dates_affichees_jj_mm_aaaa(self):
        """n° 2 : « Période 2026-10-01 → 2026-10-15 »."""
        code = _js_functions(JS_UTILS, ['fmtDate'])
        out = _node(code + "console.log(JSON.stringify([fmtDate("
                    "'2026-10-01'), fmtDate(''), fmtDate(null),"
                    " fmtDate('01/10/2026')]));")
        self.assertEqual(out, ['01/10/2026', '', '', '01/10/2026'])

    def test_plus_de_date_iso_ni_sigle_anglais_seul_a_l_ecran(self):
        """n° 2 et 42 : la période s'écrit en dates françaises ; RevPAR,
        pickup, pace et ADR portent leur nom français."""
        with open(JS_XML, encoding='utf-8') as fh:
            xml = fh.read()
        with open(JS_UTILS, encoding='utf-8') as fh:
            utils = fh.read()
        self.assertFalse("state.dateFrom + ' → '" in xml,
                         "période affichée en dates ISO")
        for label in ("'RevPAR'", "'Pace du mois'", "'Pickup 7 j → 30 j'",
                      "'ADR — prix moyen par nuit'"):
            self.assertFalse(label in xml, label)
        self.assertFalse(".toISOString(" in utils)


if __name__ == '__main__':
    unittest.main(verbosity=1)
