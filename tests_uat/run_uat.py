#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Exécute les scénarios de recette AITE HOUSE dans un vrai navigateur.

    python tests_uat/run_uat.py --url http://127.0.0.1:8069

Produit :
  * ``documentation/captures/*.png`` — une capture par étape ;
  * ``documentation/uat_resultats.json`` — le relevé des constats.
"""
import argparse
import os
import sys
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import uat_common  # noqa: E402
from uat_common import save_report  # noqa: E402

CHROMIUM_CANDIDATES = [
    '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
    '/opt/pw-browsers/chromium/chrome-linux/chrome',
    '/usr/bin/chromium',
    '/usr/bin/google-chrome',
]


def find_chromium():
    for path in CHROMIUM_CANDIDATES:
        if os.path.exists(path):
            return path
    return None  # Playwright choisira son navigateur par défaut.


def main():
    parser = argparse.ArgumentParser(
        description="Recette applicative AITE HOUSE")
    parser.add_argument('--url', default=uat_common.BASE_URL,
                        help="URL de l'instance Odoo à recetter")
    parser.add_argument('--shots', default=uat_common.SHOTS_DIR,
                        help="Dossier des captures d'écran")
    parser.add_argument('--report',
                        default=os.path.join(HERE, '..', 'documentation',
                                             'uat_resultats.json'))
    parser.add_argument('--headed', action='store_true',
                        help="Afficher le navigateur (débogage)")
    parser.add_argument('--only', default='',
                        help="Ne jouer que les scénarios dont la clé "
                             "contient ce texte")
    parser.add_argument('--keep-shots', action='store_true',
                        help="Conserver les captures des exécutions "
                             "précédentes")
    args = parser.parse_args()

    uat_common.BASE_URL = args.url.rstrip('/')
    uat_common.SHOTS_DIR = os.path.abspath(args.shots)

    # Repartir d'un dossier propre : sinon les captures d'une exécution
    # précédente se mélangent aux nouvelles et le guide illustre des
    # écrans qui n'ont plus cours.
    if not args.keep_shots and os.path.isdir(uat_common.SHOTS_DIR):
        prefix = args.only or ''
        for name in os.listdir(uat_common.SHOTS_DIR):
            if name.endswith('.png') and name.startswith(prefix):
                os.remove(os.path.join(uat_common.SHOTS_DIR, name))

    from playwright.sync_api import sync_playwright
    import scenarios  # après la mise à jour des constantes

    executable = find_chromium()
    results = []
    with sync_playwright() as pw:
        launch_kwargs = {
            'headless': not args.headed,
            'args': ['--no-sandbox', '--disable-dev-shm-usage'],
        }
        if executable:
            launch_kwargs['executable_path'] = executable
        browser = pw.chromium.launch(**launch_kwargs)
        for build in scenarios.ALL_SCENARIOS:
            # Un contexte neuf par scénario : chaque profil métier arrive
            # sur un poste vierge, sans session ni compte mémorisé du
            # précédent — c'est aussi ce qui se passe en salle.
            context = browser.new_context(
                viewport={'width': 1600, 'height': 1000},
                locale='fr-FR',
            )
            page = context.new_page()
            page.set_default_timeout(20000)
            try:
                scenario = build(page)
                if args.only and args.only not in scenario.key:
                    page.close()
                    continue
                results.append(scenario)
                status = scenario.status
                print("[%s] %-28s %s (%d étapes)" % (
                    status, scenario.key, scenario.title,
                    len(scenario.steps)))
                for step in scenario.steps:
                    if step.status == 'KO':
                        print("      ✗ étape %d — %s : %s" % (
                            step.number, step.title, step.observed))
            except Exception:  # noqa: BLE001
                print("[ERREUR] %s" % build.__name__)
                traceback.print_exc()
            finally:
                page.close()
                context.close()
        browser.close()

    path = save_report(results, args.report)
    total = sum(len(s.steps) for s in results)
    failed = sum(1 for s in results for st in s.steps if st.status == 'KO')
    print()
    print("Scénarios : %d — étapes : %d — constats KO : %d"
          % (len(results), total, failed))
    print("Relevé    : %s" % path)
    print("Captures  : %s" % uat_common.SHOTS_DIR)
    return 0


if __name__ == '__main__':
    sys.exit(main())
