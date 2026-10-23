# -*- coding: utf-8 -*-
"""Dates du tableau de bord Espaces & Prestations (écart n° 38, et n° 3).

Les fonctions de ``static/src/js/services/utils.js`` sont exécutées telles
quelles par Node.js, dans un fuseau choisi (variable ``TZ``) : c'est le seul
moyen de reproduire un poste réglé sur Douala (UTC+1) sans navigateur. Le
test est ignoré si Node.js n'est pas installé.

Constat d'origine : ``toISOString()`` convertit le minuit LOCAL en UTC ;
à Douala, « Ce mois » démarrait donc le 30 du mois précédent.
"""
import json
import os
import shutil
import subprocess
import unittest

from odoo.tests import TransactionCase, tagged

UTILS = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..',
    'static', 'src', 'js', 'services', 'utils.js'))

# Script Node : charge utils.js (sans les mots-clés « export ») puis évalue
# l'expression demandée. Les fonctions absentes sont signalées telles quelles.
_RUNNER = r"""
const fs = require('fs');
const src = fs.readFileSync(process.argv[1], 'utf8').replace(/^export /gm, '');
const lib = new Function(src + `
    return {
        periodRange: typeof periodRange === 'function' ? periodRange : null,
        shiftDay: typeof shiftDay === 'function' ? shiftDay : null,
        fmtDay: typeof fmtDay === 'function' ? fmtDay : null,
        fmtPct: typeof fmtPct === 'function' ? fmtPct : null,
    };`)();
const expr = new Function('lib', 'return (' + process.argv[2] + ');');
let out;
try { out = expr(lib); } catch (e) { out = 'ERREUR : ' + e.message; }
process.stdout.write(JSON.stringify(out));
"""


@tagged('post_install', '-at_install', 'aite_slot')
@unittest.skipUnless(shutil.which('node'), "Node.js absent : test JS ignoré")
class TestSlotDashboardDates(TransactionCase):

    def _js(self, expr, tz='Africa/Douala'):
        env = dict(os.environ, TZ=tz)
        res = subprocess.run(
            ['node', '-e', _RUNNER, UTILS, expr],
            capture_output=True, text=True, timeout=60, env=env)
        self.assertEqual(res.returncode, 0, res.stderr)
        return json.loads(res.stdout)

    # ------------------------------------------------------------------
    # Périodes envoyées au serveur : la date LOCALE, jamais l'UTC
    # ------------------------------------------------------------------

    def test_this_month_starts_on_the_first_in_douala(self):
        """15/10/2026 à 10 h, Douala : « Ce mois » = 01/10 → 15/10 (et non
        à partir du 30/09)."""
        got = self._js(
            "lib.periodRange('month', new Date(2026, 9, 15, 10, 0))")
        self.assertEqual(
            got, {'date_from': '2026-10-01', 'date_to': '2026-10-15'})

    def test_today_just_after_midnight_in_douala(self):
        """À 00 h 30 à Douala il est 23 h 30 la veille en UTC : la journée
        reste celle du poste."""
        got = self._js(
            "lib.periodRange('today', new Date(2026, 9, 15, 0, 30))")
        self.assertEqual(
            got, {'date_from': '2026-10-15', 'date_to': '2026-10-15'})

    def test_this_week_starts_on_monday(self):
        # Jeudi 15/10/2026 → lundi 12/10/2026.
        got = self._js(
            "lib.periodRange('week', new Date(2026, 9, 15, 0, 30))")
        self.assertEqual(
            got, {'date_from': '2026-10-12', 'date_to': '2026-10-15'})

    # ------------------------------------------------------------------
    # Navigation jour par jour (‹ ›) : aucun saut quel que soit le fuseau
    # ------------------------------------------------------------------

    def test_shift_day_far_east(self):
        # UTC+14 : midi local tombe la veille en UTC.
        self.assertEqual(
            self._js("lib.shiftDay('2026-10-15', 1)",
                     tz='Pacific/Kiritimati'), '2026-10-16')

    def test_shift_day_far_west(self):
        # UTC−12 : midi local tombe le lendemain en UTC.
        self.assertEqual(
            self._js("lib.shiftDay('2026-10-15', -1)", tz='Etc/GMT+12'),
            '2026-10-14')

    # ------------------------------------------------------------------
    # Écart n° 3 : titre « Planning du … » au format JJ/MM/AAAA
    # ------------------------------------------------------------------

    def test_planning_title_uses_the_french_date_format(self):
        self.assertEqual(
            self._js("lib.fmtDay('2026-10-15')"), '15/10/2026')

    # ------------------------------------------------------------------
    # Règle 6 : pourcentages « 56,0 % » (une décimale, espace insécable)
    # ------------------------------------------------------------------

    def test_percentages_keep_one_decimal(self):
        """Taux d'occupation et part des « Non présentés » : même format
        que les autres tableaux de bord (« 56,0 % », jamais « 56 % »)."""
        self.assertEqual(
            self._js("[lib.fmtPct(56), lib.fmtPct(12.34), lib.fmtPct(0),"
                     " lib.fmtPct(null)]"),
            ['56,0\u00a0%', '12,3\u00a0%', '0,0\u00a0%', '0,0\u00a0%'])
