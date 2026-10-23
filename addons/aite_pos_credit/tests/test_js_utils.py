# -*- coding: utf-8 -*-
"""Formatage côté navigateur du tableau de bord POS Crédit
(``static/src/js/services/utils.js``).

Le VRAI fichier JavaScript est exécuté par Node.js dans un fuseau donné :
test sauté si Node.js n'est pas installé.

* n° 38 — les périodes rapides (« Aujourd'hui », « Cette semaine »,
  « Ce mois ») sont des dates LOCALES : à Douala (UTC+1),
  ``toISOString()`` faisait partir « Ce mois » du 30/09 ;
* n° 41 (règle 6) — pourcentages à la française, une décimale fixe et une
  espace insécable (« 64,0 % », comme la même carte du cockpit Direction),
  variations comprises (« ▲ +12,5 % »).
"""
import json
import os
import shutil
import subprocess

from odoo.tests import TransactionCase, tagged

UTILS = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                     'static', 'src', 'js', 'services', 'utils.js')

SCRIPT = """
const u = await import(%(path)s);
// 01/10/2026 à 0 h 30 heure locale : minuit passé de 30 minutes, le cas
// où l'ancien code (toISOString) reculait au 30/09.
const now = new Date(2026, 9, 1, 0, 30);
const r = (k) => u.periodRange(k, now);
console.log(JSON.stringify({
    today: r("today"),
    week: r("week"),
    month: r("month"),
    all: r("all"),
    local: u.localIsoDate(now),
    pct: [u.fmtPct(64), u.fmtPct(12.46), u.fmtPct(0), u.fmtPct(null)],
    delta: [u.fmtDelta(12.5).text, u.fmtDelta(-3).text, u.fmtDelta(0).text,
            u.fmtDelta(12).text],
    deltaValue: [u.fmtDelta(12.46).value, u.fmtDelta(-3.04).value],
}));
"""


@tagged('post_install', '-at_install', 'aite_credit')
class TestCreditJsUtils(TransactionCase):

    def _run(self, tz):
        node = shutil.which('node')
        if not node:
            self.skipTest("Node.js absent : formatage JS non vérifié")
        env = dict(os.environ, TZ=tz)
        out = subprocess.run(
            [node, '--input-type=module', '-e',
             SCRIPT % {'path': json.dumps('file://' + UTILS)}],
            capture_output=True, text=True, env=env, timeout=60,
            check=False)
        self.assertEqual(out.returncode, 0, out.stderr)
        return json.loads(out.stdout)

    def test_periodes_rapides_en_date_locale(self):
        """N° 38 : « Ce mois » démarre le 1er, même à 0 h 30 à Douala."""
        for tz in ('Africa/Douala', 'America/New_York'):
            res = self._run(tz)
            self.assertEqual(res['local'], '2026-10-01', tz)
            self.assertEqual(res['today'], {'date_from': '2026-10-01',
                                            'date_to': '2026-10-01'}, tz)
            # Le 01/10/2026 est un jeudi : la semaine part du lundi 28/09.
            self.assertEqual(res['week'], {'date_from': '2026-09-28',
                                           'date_to': '2026-10-01'}, tz)
            self.assertEqual(res['month'], {'date_from': '2026-10-01',
                                            'date_to': '2026-10-01'}, tz)
            self.assertEqual(res['all']['date_from'], '2000-01-01', tz)

    def test_pourcentages_a_la_francaise(self):
        """N° 41 / règle 6 : « 64,0 % » (une décimale, espace insécable),
        comme la carte du cockpit Direction — et non « 64 % »."""
        res = self._run('Africa/Douala')
        nbsp = ' '
        self.assertEqual(res['pct'], ['64,0' + nbsp + '%',
                                      '12,5' + nbsp + '%',
                                      '0,0' + nbsp + '%',
                                      '0,0' + nbsp + '%'])
        self.assertEqual(res['delta'], ['▲ +12,5' + nbsp + '%',
                                        '▼ 3,0' + nbsp + '%',
                                        '■ 0,0' + nbsp + '%',
                                        '▲ +12,0' + nbsp + '%'])
        # La valeur arrondie (une décimale) reste fournie pour la couleur.
        self.assertEqual(res['deltaValue'], [12.5, -3])
