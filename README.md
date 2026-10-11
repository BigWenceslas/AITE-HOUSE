# AITE HOUSE — dépôt de développement (Odoo 18)

Suite de gestion hôtelière d'AITE Consulting : **16 modules Odoo 18** (12 du socle, la
passerelle Gantt Enterprise et les 3 modules de la vague 1), leurs tests, le cahier de recette,
l'environnement de développement reproductible et la documentation. Lire `CLAUDE.md` pour
travailler avec **Claude Code**.

| Je veux… | Voir |
|---|---|
| savoir ce qui est développé et ce qui reste | `ROADMAP.md` |
| travailler avec Claude Code (conventions, commandes, méthode) | `CLAUDE.md` |
| monter l'environnement et lancer les tests | `dev/setup_env.sh`, `dev/run_tests.sh`, `docs/GUIDE_TESTS.md` |
| installer chez un client | `docs/INSTALLATION.md`, `docs/NOTES_DE_VERSION_vague1.md` |
| recetter | `recette/` (cahier 139 cas + plan PDF), `docs/GUIDE_RECETTE_UAT.md` (recette navigateur illustrée) |
| comprendre le positionnement marché | `docs/etude_comparative/` |

## Démarrage rapide

```bash
dev/setup_env.sh          # Odoo 18 cloné dans ../odoo18, base aite_dev (fr_FR), seeds LAVERANDAH
dev/srv.sh start          # http://localhost:8069 — admin / admin
dev/run_tests.sh          # tests purs + scénarios novice + audit des menus
```

Prérequis : Python 3.10 à 3.12 (variable `PYTHON`), PostgreSQL 14+ (rôle créé par le script), git, `patch`. Pour les
captures : `pip install playwright && playwright install chromium`.

## Contenu

```
addons/        16 modules livrables (+ leurs tests Odoo)   dev/        environnement & scripts
tests/         scénarios novice + tests purs               tests_uat/  recette navigateur (Playwright)
recette/       cahier et plan de recette                   captures/   écrans de la vague 1
docs/          installation, notes de version, guides PDF, étude comparative, guide de test,
               recette UAT illustrée, rapport de tests
```

## Modules

| Module | Version | Rôle |
|---|---|---|
| aite_hotel_management | 18.0.1.0.3 | Socle PMS (chambres, réservations, folios, facture unique, main courante) |
| aite_hotel_gantt | 18.0.1.0.0 | Planning Gantt des chambres — Enterprise uniquement, auto-installé |
| aite_slot_booking | 18.0.1.0.3 | Espaces & prestations au créneau |
| aite_website_booking | 18.0.1.0.0 | Réservation en ligne |
| aite_hotel_pos_link | 18.0.1.0.0 | Note de chambre (POS → folio) |
| aite_pos_credit | 18.0.2.0.3 | Crédit clients (ardoises) |
| aite_loyalty | 18.0.1.0.1 | Fidélité VIP / VVIP |
| aite_pos_analytics | 18.0.2.1.1 | Analyses des ventes POS |
| aite_stock_dashboard | 18.0.1.1.2 | Stock & inventaires |
| aite_purchase_dashboard | 18.0.1.0.2 | Achats & fournisseurs |
| aite_direction_dashboard | 18.0.1.0.2 | Cockpit Direction |
| aite_exec_dashboard | 18.0.1.0.2 | Tableau de bord exécutif |
| aite_demo_data | 18.0.1.2.3 | Jeu de démonstration |
| aite_city_tax | 18.0.1.0.0 | Taxe de séjour automatique |
| aite_guest_registry | 18.0.1.0.1 | Registre des clients, fiche de police, statistiques |
| aite_housekeeping | 18.0.1.0.2 | Gouvernante, inspections, maintenance, objets trouvés |

La suite s'installe sur **Community et Enterprise** : le planning des chambres est en vue
calendrier sur Community ; sur Enterprise (production LAVERANDAH), `aite_hotel_gantt`
s'installe seul et ajoute la vue Gantt.

---
© AITE Consulting SARL — Douala, Makepe Bloc F · info@aite-consulting.com · https://aite-consulting.com
