# AITE HOUSE — Guide de test

**Suite hôtelière AITE HOUSE sur Odoo 18 — Community & Enterprise**
AITE Consulting SARL

Ce guide explique comment **monter un environnement de test**, **exécuter
les 604 tests automatisés**, **rejouer la recette utilisateur** et
**régénérer le jeu d'essai**. Le cahier de recette illustré, avec ses
captures d'écran, fait l'objet d'un document séparé :
[`GUIDE_RECETTE_UAT.md`](GUIDE_RECETTE_UAT.md).

---

## 1. Ce qui est couvert

La suite compte trois niveaux de vérification, chacun avec son rôle.

| Niveau | Ce qu'il protège | Où il vit |
|---|---|---|
| **Tests unitaires** | Les règles de calcul prises isolément : tarifs, marges, seuils de stock, barème de points, tranches d'ancienneté | `addons/<module>/tests/` |
| **Tests fonctionnels** | Les parcours qui traversent plusieurs modules : séjour complet, vente à crédit, note de chambre, consolidation | `addons/aite_demo_data/tests/test_journeys.py` |
| **Recette utilisateur (UAT)** | Ce que chaque poste voit et peut faire, dans un vrai navigateur | `tests_uat/` |

### Répartition des tests automatisés

| Module | Tests | Ce qui est vérifié |
|---|---:|---|
| `aite_hotel_management` | 207 | Moteur tarifaire, disponibilité, workflow de réservation, folio, taxes, facturation, gouvernante, assistants, droits par profil, tableau de bord |
| `aite_pos_credit` | 86 | Ardoises, sévérité, remboursements, écritures 411, génération depuis le POS (paiement mixte), balance âgée, droits |
| `aite_slot_booking` | 69 | Grille de créneaux, alignement, conflits par capacité, tarification, report au folio, cron no-show |
| `aite_website_booking` | 45 | Tunnel public de bout en bout, validation du formulaire, CSRF, fiche client unique, espace client |
| `aite_demo_data` | 36 | Générateur de jeu d'essai, devise, écarts de caisse, idempotence, purge, **6 parcours métier bout-en-bout** |
| `aite_pos_analytics` | 35 | Coût figé à la vente, marge, agrégats de session, écarts de caisse et leur sévérité, API du tableau de bord |
| `aite_loyalty` | 35 | Barème de points, grand livre, segmentation VIP / VVIP, fenêtre glissante, rétrogradation |
| `aite_stock_dashboard` | 33 | Couverture, seuils, quantité à commander, statuts d'alerte, valorisation, rotation |
| `aite_hotel_pos_link` | 23 | Note de chambre, décisions de rattachement, file d'attente, idempotence |
| `aite_purchase_dashboard` | 13 | API du tableau de bord Achats, consignes fournisseurs |
| `aite_exec_dashboard` | 11 | Consolidation des trois pôles, mix d'activité |
| `aite_direction_dashboard` | 11 | Cohérence du cockpit avec les quatre moteurs, balance âgée en miroir |
| **Total** | **604** | |

Les tests sont marqués par des **étiquettes** (`aite_hotel`, `aite_credit`,
`aite_slot`, …) pour pouvoir n'en jouer qu'une partie.

---

## 2. Monter l'environnement de test

### 2.1 Prérequis

- Odoo 18 (Community ou Enterprise), PostgreSQL 14 ou supérieur.
- Les dépendances Python d'Odoo (`requirements.txt` de la distribution).
- Pour la recette navigateur : **Playwright** et Chromium.

```bash
pip install playwright
playwright install chromium
```

### 2.2 Base de test

> **Important.** Créez la base **avec les données de démonstration
> Odoo** : elles apportent le plan comptable, sans lequel le Point de
> Vente ne peut pas être configuré.

```bash
# 1. Base avec les modules Odoo standard et leur plan comptable
odoo-bin -d aite_test --without-demo=False \
  -i base,point_of_sale,sale,account,purchase,stock,website,portal,mail,product,web \
  --stop-after-init

# 2. Suite AITE + jeu d'essai (installe toutes les dépendances)
odoo-bin -d aite_test -i aite_demo_data --stop-after-init
```

`aite_demo_data` entraîne l'ensemble de la suite. Sur Odoo **Enterprise**,
`aite_hotel_gantt` s'installe en plus, automatiquement, et ajoute le
planning Gantt des chambres.

### 2.3 Devise

Le jeu d'essai est calibré en **GNF** (contexte Guinée) et **positionne
lui-même la devise** de la société — mais seulement si la base est
encore vierge : société sur une devise d'origine (`USD` ou `EUR`) **et**
aucune écriture comptable.

Le compte rendu de génération affiche la devise retenue :

```
{'currency': 'GNF', 'users': 5, ..., 'pos_orders': 168, 'credits': 18, ...}
```

Si la valeur renvoyée n'est pas `GNF`, c'est que la société a déjà été
engagée — devise délibérément choisie, ou écritures déjà passées. Le
générateur n'y touche pas et le journalise. Pour basculer malgré tout :

> Paramètres → Sociétés → *votre société* → Devise → `GNF` (ou `XAF`)

Odoo refuse de changer la devise une fois des écritures comptabilisées.

---

## 3. Exécuter les tests automatisés

### 3.1 Toute la suite

```bash
odoo-bin -d aite_test --test-enable --stop-after-init \
  -u aite_hotel_management,aite_slot_booking,aite_website_booking,\
aite_pos_analytics,aite_pos_credit,aite_hotel_pos_link,aite_loyalty,\
aite_stock_dashboard,aite_purchase_dashboard,aite_direction_dashboard,\
aite_exec_dashboard,aite_demo_data \
  --test-tags aite_hotel,aite_slot,aite_web,aite_analytics,aite_credit,\
aite_roomcharge,aite_loyalty,aite_stock,aite_purchase,aite_direction,\
aite_exec,aite_demo,aite_journey
```

Résultat attendu, en fin de journal :

```
odoo.tests.result: 0 failed, 0 error(s) of 604 tests
```

### 3.2 Un seul module

```bash
odoo-bin -d aite_test -u aite_pos_credit --test-enable \
  --test-tags aite_credit --stop-after-init
```

### 3.3 Les seuls parcours métier

```bash
odoo-bin -d aite_test -u aite_demo_data --test-enable \
  --test-tags aite_journey --stop-after-init
```

Ces six parcours sont les plus parlants pour une revue : ils suivent
l'argent d'un bout à l'autre.

| Parcours | Ce qu'il démontre |
|---|---|
| Séjour complet | Réservation → acompte → check-in → bar + SPA sur la note → check-out → facture soldée |
| Vente à crédit | Paiement mixte au POS → ardoise → encours client → remboursements → solde |
| Note de chambre ambiguë | Consommation anonyme → file d'attente → arbitrage de la réception → folio |
| Fidélité multi-services | Points d'un capital unique, diversité des domaines et statut VVIP |
| Consolidation direction | Le cockpit reprend sans divergence les chiffres des moteurs |
| Gouvernante après départ | Recouche automatique → ménage → chambre revendable |

### 3.4 Interprétation

- `0 failed, 0 error(s)` : la suite est verte.
- Un `FAIL` indique un écart de **comportement** (une assertion démentie).
- Un `ERROR` indique une **exception** (accès refusé, champ absent…).

Les avertissements `no translation language detected` émis au chargement
proviennent d'Odoo lui-même et sont sans conséquence.

---

## 4. Rejouer la recette utilisateur

La recette se joue dans un vrai navigateur, avec les profils métier.

```bash
# Démarrer l'instance à recetter
odoo-bin -d aite_test --db-filter='aite_test'

# Dans un autre terminal
python tests_uat/run_uat.py --url http://127.0.0.1:8069
python tests_uat/build_guide.py
python tests_uat/build_pdf.py        # version PDF, à transmettre
```

- `run_uat.py` joue les six scénarios, capture chaque écran dans
  `documentation/captures/` et écrit le relevé `uat_resultats.json`.
- `build_guide.py` en compose le cahier illustré
  `GUIDE_RECETTE_UAT.md`, pour la lecture en ligne.
- `build_pdf.py` en compose la version paginée
  `CAHIER_RECETTE_AITE_HOUSE.pdf`, prête à imprimer ou à envoyer : page
  de garde, couverture des tests automatisés, puis un scénario par page.
  Le rendu passe par le Chromium déjà installé pour la recette — rien de
  plus à installer.

Options utiles :

| Option | Effet |
|---|---|
| `--headed` | Affiche le navigateur (utile pour observer ou déboguer) |
| `--only r3` | Ne joue que les scénarios dont la clé contient `r3` |
| `--keep-shots` | Conserve les captures des exécutions précédentes |
| `--output` | *(build_pdf)* Chemin du PDF à produire |

---

## 5. Régénérer le jeu d'essai

Le jeu est daté **relativement au jour d'installation**. Sur une base de
démonstration qui vieillit, les tableaux de bord se vident : il suffit de
le régénérer.

### Depuis l'interface

> Paramètres → **Jeu d'essai AITE** (profil Administrateur)

Trois volumes : *léger* (démonstration rapide), *standard* (atelier
client), *étendu* (test de charge). L'option « Purger l'existant
d'abord » remet le compteur à zéro.

### Depuis le shell

```bash
odoo-bin shell -d aite_test
>>> env['aite.demo.generator'].generate_all(scale='normal')
>>> env.cr.commit()
```

### Ce que produit le générateur

| Domaine | Volume « standard » |
|---|---|
| Commandes en caisse | 168, sur 21 sessions closes, réparties midi et soir |
| Ardoises clients | 18, de 3 à 160 jours d'ancienneté, dont 9 partiellement remboursées |
| Notes de chambre en attente | 5, avec les trois motifs d'ambiguïté |
| Tâches de gouvernante | 12, tous types, à différents stades |
| Services hôteliers | 8 (restaurant, minibar, blanchisserie, transferts…) |
| Tarifs saisonniers | 2 par type de chambre (haute et basse saison) |
| Commandes d'achat | 8, confirmées et en demande de prix |
| Consignes fournisseurs | 5 |
| Profils utilisateurs | 5 postes métier |

La génération est **idempotente** : la relancer ne duplique rien.

> **Note.** La purge conserve volontairement l'historique de caisse : une
> vente encaissée porte des écritures comptables et des mouvements de
> stock, qu'Odoo interdit — à juste titre — de supprimer.

---

## 6. Écrire un nouveau test

### Test unitaire

Placez-le dans `addons/<module>/tests/`, déclarez-le dans `__init__.py`
et étiquetez-le :

```python
@tagged('post_install', '-at_install', 'aite_hotel')
class TestQuelqueChose(HotelCommon):

    def test_la_regle_metier(self):
        """Une phrase qui dit la règle, pas le code."""
        ...
```

### Deux pièges à connaître

1. **Les tableaux de bord agrègent toute la société.** Si la base porte
   un jeu d'essai, un total « global » sera faussé. Travaillez dans une
   société dédiée (voir `aite_pos_credit/tests/test_dashboard.py`) ou
   filtrez sur votre propre établissement.

2. **POS Analytics lit une vue SQL.** Elle ne voit que ce qui est écrit
   en base : appelez `self.env.flush_all()` après avoir créé des
   commandes, avant d'interroger le tableau de bord.

### Scénario de recette

Ajoutez une fonction dans `tests_uat/scenarios.py` et référencez-la dans
`ALL_SCENARIOS`. Visez les boutons par leur **nom technique**
(`button[name="action_start"]`) plutôt que par leur libellé : c'est
stable et cela survit aux traductions.

---

## 7. Dépannage

| Symptôme | Cause | Correction |
|---|---|---|
| `Ensure that there is an existing bank journal` | Pas de plan comptable sur la société | Créer la base avec `--without-demo=False`, ou installer un module de localisation comptable |
| `depends on module "web_gantt"` | Enterprise attendu | Normal sur Community : le planning s'affiche en calendrier et `aite_hotel_gantt` reste non installé |
| `Port 8069 is in use` | Une instance tourne déjà | Lancer les tests avec `--http-port=8070 --gevent-port=8073` |
| Tableaux de bord vides | Jeu d'essai périmé | Régénérer (§ 5) |
| Montants en `$` au lieu de `FG` | Devise de la société | Positionner `GNF` / `XAF` avant toute écriture (§ 2.3) |
| `Timeout` sur la recette | Instance lente à répondre | Augmenter le délai : `page.set_default_timeout()` dans `run_uat.py` |

---

© AITE Consulting SARL — tous droits réservés.
