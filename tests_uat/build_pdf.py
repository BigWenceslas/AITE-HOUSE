#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Compose le cahier de recette en **PDF paginé**, prêt à transmettre.

    python tests_uat/build_pdf.py

Même source que ``build_guide.py`` — le relevé ``uat_resultats.json``
produit par ``run_uat.py`` — mais destiné à être imprimé ou envoyé : page
de garde, couverture des tests automatisés, puis un scénario par page
avec ses captures d'écran.

Le rendu passe par Chromium (Playwright), déjà requis pour jouer la
recette : aucun outil supplémentaire à installer.
"""
import argparse
import json
import os
import re
import sys
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
DOC = os.path.join(ROOT, 'documentation')
RESULTS = os.path.join(DOC, 'uat_resultats.json')
GUIDE_TESTS = os.path.join(DOC, 'GUIDE_TESTS.md')
OUTPUT = os.path.join(DOC, 'CAHIER_RECETTE_AITE_HOUSE.pdf')

ACCOUNTS = [
    ("Réception", "demo.reception",
     "Réservations, folios, encaissements, check-in / check-out"),
    ("Gouvernante", "demo.gouvernante",
     "Tâches de ménage et états de chambre"),
    ("Caisse", "demo.caisse",
     "Point de vente, ardoises, remboursements"),
    ("Magasin", "demo.magasin",
     "Stock, inventaires, alertes"),
    ("Direction", "demo.direction",
     "Tous les tableaux de bord, configuration"),
]


def read_automated_coverage():
    """
    Répartition des tests automatisés, lue dans le guide de test.

    La table y est déjà tenue à jour à chaque campagne : la relire évite
    d'entretenir deux fois le même chiffre, et un PDF qui contredirait le
    guide serait pire que pas de PDF du tout.

    :returns: (lignes [(module, nb, objet)], total) ou ([], None).
    """
    if not os.path.exists(GUIDE_TESTS):
        return [], None
    rows, total = [], None
    with open(GUIDE_TESTS, encoding='utf-8') as handle:
        for line in handle:
            cells = [c.strip() for c in line.strip().strip('|').split('|')]
            if len(cells) != 3:
                continue
            label, count, purpose = cells
            module = label.strip('`* ')
            if module.lower() == 'total':
                digits = re.sub(r'\D', '', count)
                total = int(digits) if digits else None
            elif module.startswith('aite_') and count.isdigit():
                rows.append((module, int(count), purpose))
    return rows, total


def badge(status):
    ok = status == 'OK'
    return ('<span class="badge %s">%s</span>'
            % ('ok' if ok else 'ko', "Conforme" if ok else "Écart"))


def step_block(step):
    shot = step.get('screenshot')
    if shot and os.path.exists(os.path.join(DOC, 'captures', shot)):
        figure = ('<figure><img src="captures/%s" alt="%s"></figure>'
                  % (escape(shot), escape(step['title'])))
    else:
        figure = ('<p class="missing">Capture indisponible : %s</p>'
                  % escape(step.get('detail') or "non précisé"))
    return """
    <section class="step">
      <h3><span class="num">%(number)d</span>%(title)s</h3>
      <table class="verdict">
        <tr><th>Attendu</th><td>%(expected)s</td></tr>
        <tr><th>Constaté</th><td>%(observed)s</td></tr>
        <tr><th>Verdict</th><td>%(badge)s</td></tr>
      </table>
      %(figure)s
    </section>""" % {
        'number': step['number'],
        'title': escape(step['title']),
        'expected': escape(step['expected']),
        'observed': escape(step['observed']),
        'badge': badge(step['status']),
        'figure': figure,
    }


def build_html(data, coverage, total_tests):
    scenarios = data['scenarios']
    total_steps = sum(len(s['steps']) for s in scenarios)
    ko = sum(1 for s in scenarios for st in s['steps']
             if st['status'] == 'KO')

    summary_rows = "\n".join(
        "<tr><td>%d</td><td>%s</td><td>%s</td>"
        "<td class=\"n\">%d</td><td>%s</td></tr>"
        % (i, escape(s['title']), escape(s['persona']),
           len(s['steps']), badge(s['status']))
        for i, s in enumerate(scenarios, start=1))

    accounts_rows = "\n".join(
        "<tr><td>%s</td><td><code>%s</code></td><td>%s</td></tr>"
        % (escape(poste), escape(login), escape(scope))
        for poste, login, scope in ACCOUNTS)

    if coverage:
        coverage_rows = "\n".join(
            "<tr><td><code>%s</code></td><td class=\"n\">%d</td>"
            "<td>%s</td></tr>" % (escape(m), n, escape(p))
            for m, n, p in coverage)
        coverage_total = (
            "<tr class=\"total\"><td>Total</td>"
            "<td class=\"n\">%s</td><td></td></tr>"
            % (total_tests if total_tests else
               sum(n for _m, n, _p in coverage)))
        coverage_block = """
    <h2>Couverture des tests automatisés</h2>
    <p>La recette manuelle décrite dans ce cahier s'appuie sur une suite
    de tests automatisés, rejouée avant chaque livraison. Les deux
    niveaux sont complémentaires : les tests vérifient les règles de
    calcul et les droits, la recette vérifie ce que l'utilisateur voit
    réellement à l'écran.</p>
    <table class="data">
      <thead><tr><th>Module</th><th class="n">Tests</th>
      <th>Ce qui est vérifié</th></tr></thead>
      <tbody>%s%s</tbody>
    </table>""" % (coverage_rows, coverage_total)
    else:
        coverage_block = ""

    body = [
        """
    <section class="cover">
      <p class="brand">AITE Consulting SARL</p>
      <h1>Cahier de recette</h1>
      <p class="subtitle">Suite hôtelière AITE HOUSE · Odoo 18</p>
      <table class="facts">
        <tr><th>Scénarios</th><td>%d</td></tr>
        <tr><th>Étapes vérifiées</th><td>%d</td></tr>
        <tr><th>Écarts constatés</th><td>%d</td></tr>
        <tr><th>Tests automatisés</th><td>%s</td></tr>
        <tr><th>Exécution</th><td>%s</td></tr>
        <tr><th>Instance recettée</th><td><code>%s</code></td></tr>
      </table>
      <p class="verdict-global">%s</p>
    </section>""" % (
            len(scenarios), total_steps, ko,
            total_tests if total_tests else "—",
            escape(data['generated_at']), escape(data['base_url']),
            "Recette conforme — aucun écart constaté." if not ko
            else "%d écart(s) constaté(s) — voir le détail." % ko),

        """
    <section class="page">
      <h2>Comment lire ce cahier</h2>
      <p>Chaque scénario correspond à <strong>un poste de travail</strong>
      et se joue avec le profil de ce poste — jamais avec un compte
      administrateur. Les captures sont celles obtenues pendant
      l'exécution : ce que ce document montre est ce que l'utilisateur
      voit.</p>
      <table class="data">
        <thead><tr><th>Rubrique</th><th>Contenu</th></tr></thead>
        <tbody>
          <tr><th>Attendu</th><td>Le comportement exigé par la
          spécification</td></tr>
          <tr><th>Constaté</th><td>Ce que l'écran a réellement
          produit</td></tr>
          <tr><th>Verdict</th><td>Conforme, ou écart à traiter</td></tr>
        </tbody>
      </table>

      <h2>Comptes de recette</h2>
      <p>Ces profils sont créés par le module <code>aite_demo_data</code>.
      Le mot de passe est identique à l'identifiant —
      <strong>base de démonstration uniquement</strong>.</p>
      <table class="data">
        <thead><tr><th>Poste</th><th>Identifiant</th>
        <th>Périmètre</th></tr></thead>
        <tbody>%s</tbody>
      </table>
      %s
    </section>""" % (accounts_rows, coverage_block),

        """
    <section class="page">
      <h2>Synthèse des scénarios</h2>
      <table class="data">
        <thead><tr><th class="n">#</th><th>Scénario</th><th>Poste</th>
        <th class="n">Étapes</th><th>Verdict</th></tr></thead>
        <tbody>%s</tbody>
      </table>
      <p class="total-line">Total : <strong>%d étapes</strong> —
      %d écart(s) constaté(s).</p>
    </section>""" % (summary_rows, total_steps, ko),
    ]

    for index, scenario in enumerate(scenarios, start=1):
        steps = "\n".join(step_block(s) for s in scenario['steps'])
        body.append("""
    <section class="page scenario">
      <h2><span class="num">%d</span>%s</h2>
      <table class="meta">
        <tr><th>Poste</th><td>%s</td></tr>
        <tr><th>Objectif</th><td>%s</td></tr>
        <tr><th>Verdict global</th><td>%s</td></tr>
      </table>
      %s
    </section>""" % (index, escape(scenario['title']),
                     escape(scenario['persona']), escape(scenario['goal']),
                     badge(scenario['status']), steps))

    # ``replace`` et non ``%`` : la feuille de style est pleine de
    # pourcents (largeurs), qui seraient pris pour des marqueurs.
    return TEMPLATE.replace('<!--BODY-->', "\n".join(body))


TEMPLATE = """<!doctype html>
<html lang="fr"><head><meta charset="utf-8">
<title>Cahier de recette — AITE HOUSE</title>
<style>
  @page { size: A4; margin: 18mm 15mm 20mm; }
  :root {
    --ink: #1c1a22;
    --muted: #5f5a6b;
    --rule: #d9d5e0;
    --brand: #714B67;
    --ok-bg: #e7f4ec; --ok-ink: #1c6b3f;
    --ko-bg: #fdeaea; --ko-ink: #a3241f;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0; color: var(--ink);
    font: 10pt/1.5 "DejaVu Sans", "Liberation Sans", Arial, sans-serif;
  }
  h1, h2, h3 { color: var(--brand); font-weight: 600; }
  h1 { font-size: 30pt; margin: 0 0 4mm; letter-spacing: -0.4pt; }
  h2 {
    font-size: 16pt; margin: 0 0 5mm;
    padding-bottom: 2.5mm; border-bottom: 1.5pt solid var(--brand);
  }
  h3 { font-size: 11.5pt; margin: 0 0 3mm; }
  h2 .num, h3 .num {
    display: inline-block; min-width: 7mm; margin-right: 3mm;
    padding: 0.4mm 1.6mm; border-radius: 2mm;
    background: var(--brand); color: #fff;
    font-size: 0.82em; text-align: center;
  }
  code { font-family: "DejaVu Sans Mono", monospace; font-size: 0.9em; }

  /* Une section = une page : un scénario ne commence jamais en bas
     d'une page déjà entamée. */
  .page { page-break-before: always; }
  .cover {
    height: 250mm; display: flex; flex-direction: column;
    justify-content: center;
  }
  .cover .brand {
    color: var(--brand); font-weight: 600; letter-spacing: 1.4pt;
    text-transform: uppercase; font-size: 9pt; margin: 0 0 10mm;
  }
  .cover .subtitle {
    font-size: 13pt; color: var(--muted); margin: 0 0 14mm;
  }
  .cover .verdict-global {
    margin-top: 12mm; padding: 4mm 5mm; border-radius: 2mm;
    background: var(--ok-bg); color: var(--ok-ink); font-weight: 600;
  }
  .facts { border-top: 1pt solid var(--rule); width: 100%; }
  .facts th, .facts td {
    padding: 2.4mm 0; border-bottom: 1pt solid var(--rule);
    text-align: left; vertical-align: top;
  }
  .facts th { width: 45mm; color: var(--muted); font-weight: 400; }

  table { border-collapse: collapse; width: 100%; margin: 0 0 6mm; }
  .data th, .data td {
    padding: 2.2mm 3mm; border-bottom: 0.75pt solid var(--rule);
    text-align: left; vertical-align: top;
  }
  .data thead th {
    background: #f4f2f7; color: var(--brand);
    border-bottom: 1.2pt solid var(--brand); font-size: 9pt;
  }
  .data tbody th { font-weight: 600; width: 30mm; }
  .data .total td { font-weight: 700; border-top: 1.2pt solid var(--brand); }
  .n { text-align: right; white-space: nowrap; }
  .data td.n, .data th.n { text-align: right; }
  .total-line { color: var(--muted); }

  .meta { margin-bottom: 7mm; }
  .meta th, .meta td {
    padding: 2mm 0; border-bottom: 0.75pt solid var(--rule);
    text-align: left; vertical-align: top;
  }
  .meta th { width: 32mm; color: var(--muted); font-weight: 400; }

  /* Une étape reste d'un seul tenant : le verdict ne doit jamais se
     retrouver séparé de la capture qui le justifie. */
  .step {
    page-break-inside: avoid; break-inside: avoid;
    margin: 0 0 8mm; padding: 4mm 0 0;
    border-top: 0.75pt solid var(--rule);
  }
  .step:first-of-type { border-top: none; padding-top: 0; }
  .verdict { margin-bottom: 3.5mm; }
  .verdict th, .verdict td {
    padding: 1.6mm 0; text-align: left; vertical-align: top;
  }
  .verdict th {
    width: 26mm; color: var(--muted); font-weight: 400; font-size: 9pt;
  }
  .badge {
    display: inline-block; padding: 0.6mm 2.4mm; border-radius: 1.5mm;
    font-size: 8.5pt; font-weight: 600;
  }
  .badge.ok { background: var(--ok-bg); color: var(--ok-ink); }
  .badge.ko { background: var(--ko-bg); color: var(--ko-ink); }
  figure { margin: 0; }
  img {
    width: 100%; height: auto; display: block;
    border: 0.75pt solid var(--rule); border-radius: 1mm;
  }
  .missing { color: var(--ko-ink); font-style: italic; }
</style></head>
<body>
<!--BODY-->
</body></html>
"""


def render(html_path, pdf_path):
    from playwright.sync_api import sync_playwright
    # Même résolution de navigateur que la recette : sur cette image le
    # binaire est hors du chemin par défaut de Playwright, qui réclamerait
    # sinon un « playwright install » inutile.
    sys.path.insert(0, HERE)
    from run_uat import find_chromium

    footer = (
        '<div style="width:100%;font-size:7pt;color:#7a7484;'
        'font-family:sans-serif;padding:0 15mm;display:flex;'
        'justify-content:space-between;">'
        '<span>AITE HOUSE — Cahier de recette</span>'
        # Les trois éléments dans UN span : sinon le « space-between »
        # les écarte et le numéro de page se lit « 5    /    38 ».
        '<span><span class="pageNumber"></span> / '
        '<span class="totalPages"></span></span>'
        '</div>')
    with sync_playwright() as p:
        executable = find_chromium()
        browser = p.chromium.launch(
            **({'executable_path': executable} if executable else {}))
        page = browser.new_page()
        page.goto('file://%s' % html_path, wait_until='load')
        page.pdf(path=pdf_path, format='A4', print_background=True,
                 display_header_footer=True,
                 header_template='<div></div>', footer_template=footer,
                 margin={'top': '18mm', 'bottom': '20mm',
                         'left': '15mm', 'right': '15mm'})
        browser.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default=OUTPUT,
                        help="chemin du PDF à produire")
    parser.add_argument('--keep-html', action='store_true',
                        help="conserver le HTML intermédiaire")
    args = parser.parse_args()

    if not os.path.exists(RESULTS):
        print("Relevé introuvable : %s\n"
              "Lancez d'abord : python tests_uat/run_uat.py" % RESULTS)
        return 1
    with open(RESULTS, encoding='utf-8') as handle:
        data = json.load(handle)

    coverage, total_tests = read_automated_coverage()
    html = build_html(data, coverage, total_tests)

    # Le HTML vit dans documentation/ le temps du rendu : les captures y
    # sont référencées en chemin relatif.
    html_path = os.path.join(DOC, '.cahier_recette.html')
    with open(html_path, 'w', encoding='utf-8') as handle:
        handle.write(html)
    try:
        render(html_path, args.output)
    finally:
        if not args.keep_html and os.path.exists(html_path):
            os.remove(html_path)

    scenarios = data['scenarios']
    steps = sum(len(s['steps']) for s in scenarios)
    ko = sum(1 for s in scenarios for st in s['steps']
             if st['status'] == 'KO')
    size = os.path.getsize(args.output) / 1024.0 / 1024.0
    print("Cahier de recette PDF : %s (%.1f Mo)" % (args.output, size))
    print("  %d scénarios · %d étapes · %d écart(s) · %s tests automatisés"
          % (len(scenarios), steps, ko, total_tests or "?"))
    return 0


if __name__ == '__main__':
    sys.exit(main())
