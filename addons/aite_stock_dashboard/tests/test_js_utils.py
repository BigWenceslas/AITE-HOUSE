# -*- coding: utf-8 -*-
"""Formatage côté navigateur (``static/src/js/services/utils.js``).

Le VRAI fichier JavaScript est exécuté par Node.js, dans le fuseau de
Douala (UTC+1) : test sauté si Node.js (16 ou plus) n'est pas installé.

* n° 38 — « Ce mois » doit partir du 1er : un minuit local passé par
  ``toISOString()`` devenait la veille en UTC (« Du 30/09/2026 ») ;
* n° 41 — pourcentages à la française : virgule, une décimale, espace
  insécable avant « % » (« 0,5 % », « 2,0 % ») ;
* n° 44 — accord en nombre (« 1 rupture », « 2 ruptures », « 1 jour »,
  « 1,5 unité », « 24 unités »).
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
// 15/10/2026 à 0 h 30 à Douala, soit encore le 14/10 en UTC.
const now = new Date(2026, 9, 15, 0, 30);
console.log(JSON.stringify({
    today: u.periodRange("today", now),
    week: u.periodRange("week", now),
    month: u.periodRange("month", now),
    quarter: u.periodRange("quarter", now),
    pct: [u.fmtPct(0.5), u.fmtPct(2), u.fmtPct(56), u.fmtPct(null)],
    plural: [u.plural(0, "rupture", "ruptures"), u.plural(1, "rupture", "ruptures"),
             u.plural(2, "rupture", "ruptures")],
    days: [u.plural(1, "jour", "jours"), u.plural(3, "jour", "jours")],
    word: [u.pluralWord(1, "référence à zéro", "références à zéro"),
           u.pluralWord(4, "référence à zéro", "références à zéro")],
    units: [u.fmtUnits(0), u.fmtUnits(1), u.fmtUnits(1.5), u.fmtUnits(2),
            u.fmtUnits(24)],
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


@tagged('post_install', '-at_install', 'aite_stock')
class TestStockJsUtils(TransactionCase):

    def _run(self):
        out = run_utils(SCRIPT, 'Africa/Douala')
        if out is None:
            self.skipTest("Node.js 16 ou plus absent : formatage JS non "
                          "vérifié")
        returncode, stdout, stderr = out
        self.assertEqual(returncode, 0, stderr)
        return json.loads(stdout)

    def test_periods_are_local_dates(self):
        res = self._run()
        self.assertEqual(res['today'], {'date_from': '2026-10-15',
                                        'date_to': '2026-10-15'})
        # Le 15/10/2026 est un jeudi : la semaine part du lundi 12.
        self.assertEqual(res['week']['date_from'], '2026-10-12')
        self.assertEqual(res['month'], {'date_from': '2026-10-01',
                                        'date_to': '2026-10-15'})
        self.assertEqual(res['quarter']['date_from'], '2026-08-01')

    def test_percentages_are_french(self):
        nbsp = '\u00a0'
        self.assertEqual(self._run()['pct'], [
            '0,5' + nbsp + '%', '2,0' + nbsp + '%',
            '56,0' + nbsp + '%', '0,0' + nbsp + '%'])

    def test_counts_agree_in_number(self):
        res = self._run()
        self.assertEqual(res['plural'],
                         ['0 rupture', '1 rupture', '2 ruptures'])
        # Relecture de l'écart n° 44 : jours, unités et sous-titres aussi.
        self.assertEqual(res['days'], ['1 jour', '3 jours'])
        self.assertEqual(res['word'], ['référence à zéro',
                                       'références à zéro'])
        self.assertEqual(res['units'], ['0 unité', '1 unité', '1,5 unité',
                                        '2 unités', '24 unités'])
