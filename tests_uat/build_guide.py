#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Compose le cahier de recette illustré à partir des résultats UAT.

    python tests_uat/build_guide.py

Lit ``documentation/uat_resultats.json`` (produit par ``run_uat.py``) et
écrit ``documentation/GUIDE_RECETTE_UAT.md``, où chaque étape est
accompagnée de sa capture d'écran et de son constat.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DOC = os.path.abspath(os.path.join(HERE, '..', 'documentation'))
RESULTS = os.path.join(DOC, 'uat_resultats.json')
OUTPUT = os.path.join(DOC, 'GUIDE_RECETTE_UAT.md')

HEADER = """# AITE HOUSE — Cahier de recette (UAT)

**Suite hôtelière AITE HOUSE sur Odoo 18 — recette applicative**
Généré le {date} · instance recettée : `{url}`

---

## Comment lire ce cahier

Chaque scénario correspond à **un poste de travail** et se joue avec le
profil utilisateur de ce poste — pas avec un compte administrateur. Les
captures d'écran sont celles obtenues lors de l'exécution : ce que le
document montre est ce que l'utilisateur voit.

Pour chaque étape :

| Colonne | Contenu |
|---|---|
| **Action** | Le geste effectué, dans l'ordre |
| **Attendu** | Le comportement exigé par la spécification |
| **Constaté** | Ce que l'écran a réellement produit |
| **Verdict** | ✅ conforme · ❌ écart |

### Comptes de recette

Les profils sont créés par le module `aite_demo_data`. Le mot de passe
est identique à l'identifiant (**base de démonstration uniquement**).

| Poste | Identifiant | Périmètre |
|---|---|---|
| Réception | `demo.reception` | Réservations, folios, encaissements, check-in / check-out |
| Gouvernante | `demo.gouvernante` | Tâches de ménage et états de chambre |
| Caisse | `demo.caisse` | Point de vente, ardoises, remboursements |
| Magasin | `demo.magasin` | Stock, inventaires, alertes |
| Direction | `demo.direction` | Tous les tableaux de bord, configuration |

### Rejouer la recette

```bash
python tests_uat/run_uat.py --url http://mon-serveur:8069
python tests_uat/build_guide.py
```

---

## Synthèse

| Scénario | Poste | Étapes | Verdict |
|---|---|---|---|
{summary}

**Total : {total_steps} étapes — {ko} écart(s) constaté(s).**

---
"""

SCENARIO = """
## {index}. {title}

> **Poste :** {persona}
> **Objectif :** {goal}
> **Verdict global :** {verdict}

{steps}

---
"""

STEP = """
### {number}. {title}

| | |
|---|---|
| **Attendu** | {expected} |
| **Constaté** | {observed} |
| **Verdict** | {verdict} |

![{title}](captures/{screenshot})
"""

STEP_NO_SHOT = """
### {number}. {title}

| | |
|---|---|
| **Attendu** | {expected} |
| **Constaté** | {observed} |
| **Verdict** | {verdict} |

_(capture indisponible : {detail})_
"""


def badge(status):
    return "✅ Conforme" if status == 'OK' else "❌ Écart"


def main():
    if not os.path.exists(RESULTS):
        print("Relevé introuvable : %s\n"
              "Lancez d'abord : python tests_uat/run_uat.py" % RESULTS)
        return 1
    with open(RESULTS, encoding='utf-8') as handle:
        data = json.load(handle)

    scenarios = data['scenarios']
    total_steps = sum(len(s['steps']) for s in scenarios)
    ko = sum(1 for s in scenarios for st in s['steps']
             if st['status'] == 'KO')

    summary = "\n".join(
        "| [{title}](#{anchor}) | {persona} | {n} | {verdict} |".format(
            title=s['title'],
            anchor='%d-%s' % (i + 1, s['title'].lower()
                              .replace(' ', '-').replace("'", '')),
            persona=s['persona'],
            n=len(s['steps']),
            verdict=badge(s['status']))
        for i, s in enumerate(scenarios))

    parts = [HEADER.format(date=data['generated_at'],
                           url=data['base_url'],
                           summary=summary,
                           total_steps=total_steps,
                           ko=ko)]

    for index, scenario in enumerate(scenarios, start=1):
        steps = []
        for step in scenario['steps']:
            template = STEP if step['screenshot'] else STEP_NO_SHOT
            steps.append(template.format(
                number=step['number'],
                title=step['title'],
                expected=step['expected'],
                observed=step['observed'],
                verdict=badge(step['status']),
                screenshot=step['screenshot'],
                detail=step.get('detail') or "non précisé",
            ))
        parts.append(SCENARIO.format(
            index=index,
            title=scenario['title'],
            persona=scenario['persona'],
            goal=scenario['goal'],
            verdict=badge(scenario['status']),
            steps="\n".join(steps),
        ))

    parts.append(
        "\n_Cahier produit automatiquement par `tests_uat/build_guide.py` "
        "à partir de l'exécution réelle des scénarios._\n")

    with open(OUTPUT, 'w', encoding='utf-8') as handle:
        handle.write("".join(parts))
    print("Cahier de recette écrit : %s" % OUTPUT)
    print("  %d scénarios · %d étapes · %d écart(s)"
          % (len(scenarios), total_steps, ko))
    return 0


if __name__ == '__main__':
    sys.exit(main())
