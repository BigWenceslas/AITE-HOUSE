# -*- coding: utf-8 -*-
"""Formatage côté navigateur (``static/src/js/services/utils.js``).

Le VRAI fichier JavaScript est exécuté par Node.js dans un fuseau donné :
test sauté si Node.js (16 ou plus) n'est pas installé.

* n° 38 — les périodes rapides (« Aujourd'hui », « Ce mois »…) sont des
  dates LOCALES : à Douala (UTC+1), ``toISOString()`` faisait partir
  « Ce mois » du 30/09 ;
* n° 41 / n° 5 — pourcentages à la française (« 56,0 % », espace
  insécable), variations comprises (« ▲ +12,5 % ») ;
* n° 62 — un CMV (coût) en hausse est une mauvaise nouvelle : rouge ;
* n° 37 (même règle) — une date AAAA-MM-JJ s'affiche telle quelle en
  JJ/MM/AAAA, une date-heure du serveur (UTC) dans le fuseau local ; les
  bornes de « Toute la période » sont les jours LOCAUX des sessions.
"""
import json
import os
import pathlib
import re
import shutil
import subprocess
import tempfile

from odoo.tests import TransactionCase, tagged

UTILS = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                     'static', 'src', 'js', 'services', 'utils.js')

SCRIPT = """
const u = await import(%(path)s);
// 15/10/2026 à 0 h 30 heure locale.
const now = new Date(2026, 9, 15, 0, 30);
const p = u.getQuickPeriods(now);
console.log(JSON.stringify({
    today: [p.today.from, p.today.to],
    week: p.week.from,
    month: p.month.from,
    quarter: p.quarter.from,
    year: p.year.from,
    pct: [u.fmtPct(56), u.fmtPct(0.5), u.fmtPct(null)],
    delta: [u.fmtDelta(12.5), u.fmtDelta(-3), u.fmtDelta(0)],
    deltaClass: [u.deltaClass(5), u.deltaClass(-5), u.deltaClass(5, false),
                 u.deltaClass(-5, false), u.deltaClass(0, false)],
    date: u.fmtDate("2026-10-01"),
    datetime: u.fmtDate("2026-09-30 23:30:00"),
    localDay: [u.toLocalDay("2026-10-22 23:30:00"), u.toLocalDay("2026-10-01"),
               u.toLocalDay(now), u.toLocalDay(false)],
    units: [u.fmtUnits(0), u.fmtUnits(1), u.fmtUnits(1.4), u.fmtUnits(2),
            u.fmtUnits(926)],
}));
"""


def run_utils(script, tz):
    """Exécute ``script`` (module ES qui importe ``utils.js``) avec Node.js
    dans le fuseau ``tz`` ; rend (code retour, sortie, erreurs), ou None
    si Node.js est absent ou trop ancien.

    ``utils.js`` contient des ``export`` sans ``package.json`` déclarant
    ``"type": "module"`` : Node ne le lit comme module ES que depuis la
    22.7 (détection automatique de la syntaxe). Sur Node 18 ou 20 —
    Debian 12, Ubuntu 24.04 — l'import échouait et le test aussi. Une
    copie en ``.mjs`` est un module ES pour toutes les versions ; Node 16
    au minimum pour l'``await`` de premier niveau et ``Intl`` complet.
    """
    node = shutil.which('node')
    if not node:
        return None
    version = subprocess.run([node, '--version'], capture_output=True,
                             text=True, timeout=30, check=False).stdout
    major = re.match(r'v(\d+)\.', version or '')
    if not major or int(major.group(1)) < 16:
        return None
    with tempfile.TemporaryDirectory() as tmp:
        module = os.path.join(tmp, 'utils.mjs')
        shutil.copyfile(UTILS, module)
        out = subprocess.run(
            [node, '--input-type=module', '-e',
             script % {'path': json.dumps(pathlib.Path(module).as_uri())}],
            capture_output=True, text=True, env=dict(os.environ, TZ=tz),
            timeout=60, check=False)
    return out.returncode, out.stdout, out.stderr


@tagged('post_install', '-at_install', 'aite_analytics')
class TestPosJsUtils(TransactionCase):

    def _run(self, tz):
        out = run_utils(SCRIPT, tz)
        if out is None:
            self.skipTest("Node.js 16 ou plus absent : formatage JS non "
                          "vérifié")
        returncode, stdout, stderr = out
        self.assertEqual(returncode, 0, stderr)
        return json.loads(stdout)

    def test_quick_periods_are_local_dates(self):
        res = self._run('Africa/Douala')
        self.assertEqual(res['today'], ['2026-10-15', '2026-10-15'])
        self.assertEqual(res['week'], '2026-10-12')       # lundi
        self.assertEqual(res['month'], '2026-10-01')
        self.assertEqual(res['quarter'], '2026-10-01')
        self.assertEqual(res['year'], '2026-01-01')

    def test_percentages_and_variations_are_french(self):
        res = self._run('Africa/Douala')
        nbsp = '\u00a0'
        self.assertEqual(res['pct'], ['56,0' + nbsp + '%',
                                      '0,5' + nbsp + '%',
                                      '0,0' + nbsp + '%'])
        self.assertEqual(res['delta'], ['▲ +12,5' + nbsp + '%',
                                        '▼ −3,0' + nbsp + '%',
                                        '■ 0,0' + nbsp + '%'])

    def test_dates_are_day_month_year_in_the_local_zone(self):
        res = self._run('Africa/Douala')
        self.assertEqual(res['date'], '01/10/2026')
        # 30/09 à 23 h 30 UTC = 01/10 à 0 h 30 à Douala.
        self.assertEqual(res['datetime'], '01/10/2026')
        # Un poste à l'ouest de Greenwich ne recule pas la date d'un jour.
        res = self._run('America/New_York')
        self.assertEqual(res['date'], '01/10/2026')

    def test_all_time_bounds_are_local_days(self):
        """« Toute la période » part des dates de session du serveur
        (UTC) : leur jour local, celui que le serveur filtre."""
        res = self._run('Africa/Douala')
        # 22/10 à 23 h 30 UTC = 23/10 à 0 h 30 à Douala.
        self.assertEqual(res['localDay'],
                         ['2026-10-23', '2026-10-01', '2026-10-15', None])

    def test_quantities_are_written_out_and_agree(self):
        """« 926 unités », plus « 926 u » (relecture de l'écart n° 42)."""
        self.assertEqual(self._run('Africa/Douala')['units'], [
            '0 unité', '1 unité', '1 unité', '2 unités', '926 unités'])

    def test_a_rising_cost_is_shown_in_red(self):
        res = self._run('Africa/Douala')
        # up = vert, down = rouge : le CMV inverse le sens.
        self.assertEqual(res['deltaClass'],
                         ['up', 'down', 'down', 'up', 'flat'])
