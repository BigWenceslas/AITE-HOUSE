# AITE HOUSE — instructions pour Claude Code

Suite de gestion hôtelière d'**AITE Consulting** (Douala) sur **Odoo 18**, client pilote
**LAVERANDAH** (bar-hôtel, Douala, FCFA, Odoo 18 **Enterprise** en production). Tout est en
**français** : code commenté en français, libellés, messages, documentation, commits.

Lis d'abord `ROADMAP.md` (ce qui est fait, ce qui reste, notes de conception) puis
`docs/NOTES_DE_VERSION_vague1.md`. Le travail en cours : **terminer la vague 1** dans
l'ordre **F05 → F07 → F08 → F09** (F06 livré ; voir ROADMAP §4).

Dépôt git : `BigWenceslas/AITE-HOUSE`. Chaque session Claude Code travaille sur sa branche
`claude/...`, commits en français, puis pull request vers `main`.

## Arborescence

```
addons/            les 16 modules livrables (c'est CECI qu'on livre au client) :
                   12 du socle + aite_hotel_gantt (passerelle Enterprise) + 3 de la vague 1
addons/<m>/tests/  tests unitaires Odoo (TransactionCase, 613 tests, étiquettes aite_*)
dev/               environnement : setup_env.sh, srv.sh, run_tests.sh, odoo.conf, seeds, audit
tests/vague1/      scénarios « utilisateur novice » (odoo shell) + tests purs + captures Playwright
tests/socle/       tests purs des 12 modules du socle (unittest, sans Odoo)
tests_uat/         recette navigateur (Playwright) : run_uat.py → build_guide.py / build_pdf.py
recette/           cahier de recette (139 cas) : cas_de_test.py → build_xlsx.py → build_plan.py
docs/              installation, notes de version, inventaire, guides PDF, étude comparative,
                   guide de test, recette UAT illustrée (captures_uat/), rapport de tests
captures/          captures d'écran de la vague 1 (documentation, plaquette)
```

## Démarrer

```bash
dev/setup_env.sh            # clone Odoo 18 à côté (../odoo18), deps, base aite_dev en fr_FR, seeds
dev/srv.sh start            # http://localhost:8069 — admin / admin (amina, rose, gouv : mdp = login)
dev/run_tests.sh            # tests purs + 4 scénarios + audit des menus → doit finir par « TOUT EST VERT »
```
PostgreSQL doit tourner (rôle `odoo`/`odoo`, créé par le script). Variables : `PYTHON`
(interpréteur ; Odoo 18 veut Python 3.10–3.12 → `uv venv --python 3.12 ../venv312` puis
`PYTHON=../venv312/bin/python`), `ODOO_DIR`, `ODOO_DB`, `PG_HOST` (`/tmp` = socket local,
`localhost` = service).

Tests unitaires Odoo d'un module (base de test séparée, jamais `aite_dev`) :
```bash
cd ../odoo18 && $PYTHON odoo-bin -c ../AITE-HOUSE/dev/odoo.conf -d aite_test \
   -i <module> --test-enable --test-tags /<module> --stop-after-init
```

**Odoo Community vs Enterprise.** Le socle `aite_hotel_management` s'installe **tel quel sur
les deux éditions** : la vue Gantt (`web_gantt`, Enterprise) vit dans le module passerelle
`aite_hotel_gantt` (`auto_install`), et le planning s'affiche en calendrier sur Community.
Aucune copie patchée n'est nécessaire : `dev/odoo.conf` pointe directement sur `addons/`.

## Conventions de code

- Odoo 18 : vues `<list>` (pas `<tree>`), `invisible="expr"` (pas `attrs`), `column_invisible`,
  `t-name="card"` dans les kanbans, `readonly="expr"`. **Odoo 18 refuse `@string` comme
  sélecteur xpath** d'héritage : viser `@name`. Icône `fa` → toujours un attribut `title`
  (sinon warning bloquant). `&lt;` obligatoire dans les domaines XML.
- Préfixes : modèles `aite.<domaine>.<objet>`, xml_id `view_/action_/menu_`, groupes du socle
  `aite_hotel_management.group_hotel_user|housekeeping|manager`.
- Logique métier pure dans des `@staticmethod` (ex. `_taxable_units`, `_hint_for`) → testée
  sans Odoo par extraction regex dans `tests/*/test_*_logic.py`.
- Vues SQL (`_auto = False`) : surcharger `_search` et `read_group` avec
  `self.env['<modèle source>'].flush_model()` sinon la vue lit des données périmées.
- Calculs sur le folio : réutiliser le modèle de `aite_city_tax` (`_sync_room_lines` →
  `_sync_<x>_line`, une ligne, jamais modifiée après facturation, `_compute_amounts` ajusté).
- Un `@api.depends` complet sur tout compute, même non stocké (sinon valeurs périmées à l'écran).
- Données de référence (barèmes, checklists) en `noupdate="1"` : le client les modifie sans code.
- Textes QWeb : `env.context.get(...)` (pas `ctx`) ; `_()` toujours dans une méthode d'instance
  (sinon « no translation language detected »).
- Manifest : `'version': '18.0.x.y.z'`, auteur AITE Consulting, LGPL-3 ; **incrémenter la
  version à chaque modification de vue ou de données** (le client doit « Mettre à niveau »).
- Chaque module porte ses tests Odoo dans `addons/<module>/tests/` (`@tagged('post_install',
  '-at_install', 'aite_<x>')`) ; une correction de bug commence par le test qui la reproduit.
- Les écritures techniques (article support d'un type de chambre, contact marqué « client
  hôtel », journal d'encaissement) passent en `sudo()` : la réception et le responsable hôtel
  n'ont pas — et n'ont pas à avoir — les droits produit / comptabilité.

## Règles d'intuitivité (la demande du client : « un utilisateur qui n'a jamais vu la plateforme »)

1. Chaque réglage porte une **phrase « ce qui va se passer »** (ex. onglet Taxe de séjour de l'hôtel).
2. Chaque action/menu a une aide `o_view_nocontent` qui **dit quoi faire** quand l'écran est vide
   (≥ 120 caractères) — contrôlé par `dev/audit_menus.py`.
3. **Aucune saisie demandée à la réception pour la conformité** : la taxe se calcule seule, la fiche
   d'enregistrement se pré-remplit, le bandeau dit ce qui manque.
4. **Un bouton = une étape**, libellé à la première personne pour le terrain (« Je commence »,
   « C'est fait »), phrase d'état lisible (« Propre — prête pour l'arrivée »).
5. S'accrocher aux **écrans existants** (réservation, folio, check-in) plutôt que créer des menus ;
   masquer un menu du socle plutôt que le dupliquer.
6. Pas d'anglais résiduel, dates au format `%d/%m/%Y`, montants en FCFA.

## Méthode de livraison d'une fonctionnalité (obligatoire)

1. Concevoir à partir des notes de `ROADMAP.md` §4 ; écrire d'abord le **scénario novice**
   (`tests/vague1/scenario_<f>.py`, rôle par rôle, `check(label, cond)`, `env.cr.rollback()` final,
   `sys.exit(1)` si KO) — il sert de spécification.
2. Développer dans `addons/`, installer/mettre à niveau sur `aite_dev`
   (`$PYTHON odoo-bin -c dev/odoo.conf -d aite_dev -u <module> --stop-after-init`), lire le log.
3. `dev/run_tests.sh` → tout vert, y compris l'audit des menus ; tests Odoo du module
   (`--test-enable --test-tags /<module>`) verts.
4. **Installation à froid** sur une base vierge : `-d aite_fresh -i <modules> --without-demo=all`.
5. Captures Playwright (`tests/vague1/shots.py`, ajouter une étape) ; regarder réellement les images.
6. Ajouter les cas au cahier de recette (`recette/cas_de_test.py`, domaine suivant après P), puis
   `python3 recette/build_xlsx.py && python3 recette/build_plan.py`.
7. Mettre à jour `ROADMAP.md` (statut, version) et `docs/NOTES_DE_VERSION_vague1.md`.
8. Livrer : zip `AITE_HOUSE_vague1/` = `addons/` des modules touchés + `tests/` + `captures/` +
   notes ; procédure client : déposer les dossiers à côté des autres (jamais remplacer le répertoire),
   redémarrer, Apps → Mettre à jour la liste → Mettre à niveau ; ne jamais désinstaller avant retrait
   des fichiers.

## Pièges connus (déjà payés)

- `pkill -f`/`pgrep` tuent le shell courant dans certains environnements → utiliser `dev/srv.sh` (pidfile).
- Playwright : `networkidle` n'arrive jamais sur Odoo (long-polling) → attendre un sélecteur.
  Le module Site web ajoute des boutons `submit` cachés à la page de connexion → cliquer
  `button[type=submit]:visible`. Après une modification JS/XML, le serveur garde l'ancien
  paquet d'assets : mettre le module à niveau (`-u`) avant de reprendre une capture.
- Le serveur lancé par `dev/srv.sh` meurt avec le shell dans les sessions Claude Code cloud :
  le lancer en tâche de fond (`exec $PYTHON odoo-bin -c dev/odoo.conf -d aite_dev`).
- Un kanban groupé par étage avec colonne « Aucun » repliée paraît **vide** ; Odoo 18 trie les
  colonnes d'une sélection par **ordre alphabétique de la clé** → `default_order` explicite.
- Un utilisateur créé avec un seul groupe « hôtel » n'est pas interne si le groupe n'implique pas
  `base.group_user` ; l'admin n'a aucun droit métier si le groupe manager n'est pas impliqué par
  `base.group_system` (corrigé dans le socle 18.0.1.0.3 — garder ce schéma pour tout nouveau groupe).
- `hk_state` : ne jamais ajouter une valeur « hors service » — `out_of_order` (booléen) est la
  seule source de vérité.
- Les tests `tests/socle/*` sont des tests purs hérités : ils lisent le code dans `../../addons/`.
- Le dépôt a deux lignées fusionnées le 11/10 : la campagne de tests de septembre (604 tests Odoo,
  25 correctifs, `aite_hotel_gantt`) et l'export vague 1 (3 modules, socle 18.0.1.0.3). Le socle
  du dépôt contient les deux.

## Données de test (`dev/seeds/`)

Hôtel **LAVERANDAH Hôtel** (code `LVR`, 3 ★, Cameroun), types `STD` 25 000 F / `STE` 60 000 F,
chambres 101, 102, 201, 202, 501, clients Mballa Jean, Ngo Bikaï Solange (+ Durand Paul, FR), Fotso
Paul ; utilisateurs `amina`, `rose` (équipières), `gouv` (gouvernante). Réglementation de
référence : taxe de séjour CM 5 000/4 000/3 000/1 000/500 F par nuitée selon étoiles (DGI), loi
2016/006 art. 28 (enregistrement des clients) et art. 16 (statistiques MINTOUL).
