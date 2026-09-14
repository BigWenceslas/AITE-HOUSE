# AITE HOUSE — Rapport de campagne de tests

**Suite hôtelière AITE HOUSE · Odoo 18 · 13 modules**
AITE Consulting SARL

---

## 1. Résumé

La suite n'avait, avant cette campagne, **aucun test automatisé**. Elle en
compte aujourd'hui **572**, tous verts, doublés d'une **recette
utilisateur en navigateur** de 32 étapes jouée avec les profils métier
réels.

| Indicateur | Avant | Après |
|---|---:|---:|
| Tests automatisés | 0 | **572** |
| Modules couverts | 0 / 12 | **12 / 12** |
| Parcours métier bout-en-bout | 0 | **6** |
| Scénarios de recette (navigateur) | 0 | **6** (33 étapes) |
| Captures d'écran de recette | 0 | **33** |
| Anomalies corrigées | — | **11** |

La campagne a été validée sur une base **construite entièrement de
zéro** : création, installation des 13 modules, génération du jeu
d'essai, puis exécution des 572 tests et des 6 scénarios de recette.

Résultat de la dernière exécution complète :

```
odoo.tests.result: 0 failed, 0 error(s) of 572 tests
```

---

## 2. Anomalies trouvées et corrigées

Classées par gravité. Chacune est désormais protégée par un test de
non-régression, nommé dans la dernière colonne.

### 2.1 Bloquantes

#### A1 — La suite entière était ininstallable sur Odoo Community

`aite_hotel_management` dépendait de **`web_gantt`**, module réservé à
Odoo Enterprise, pour le seul planning des chambres. L'installation
s'arrêtait net :

> `You try to install module "aite_hotel_management" that depends on module "web_gantt".`

Comme tous les autres modules dépendent du socle hôtelier, **aucun**
n'était installable — alors que `INSTALLATION.md` annonçait « Odoo 18
(Community & Enterprise) » et listait `web_gantt` parmi les modules
standard installés automatiquement.

**Correction.** Le planning Gantt est extrait dans un module passerelle
**`aite_hotel_gantt`** (`auto_install`), qui dépend de `web_gantt` :

- sur **Community**, il ne s'installe pas et le planning s'affiche en vue
  **calendrier**, ajoutée au socle ;
- sur **Enterprise**, il s'installe seul et remet le Gantt en tête de
  l'action « Planning des chambres ».

Le socle ne porte plus aucune dépendance Enterprise.

> Vérifié par : installation complète sur une base Community (13 modules,
> `aite_hotel_gantt` correctement resté non installé).

---

#### A2 — La réservation en ligne ne fonctionnait pour aucun visiteur

Chaque envoi du formulaire public — créneau d'espace comme demande de
séjour — se terminait par une **page 403**. Les pages s'affichaient, mais
aucune réservation ne pouvait aboutir.

Cause : le contrôleur convertit l'heure saisie via `_tz()`, qui lit
`request.env.company.partner_id.tz`. Le visiteur public n'a pas le droit
de lire cette fiche partenaire :

> `Public user (id=4) doesn't have 'read' access to: Contact (res.partner)`

**Correction.** Lecture du fuseau de la société en `sudo()`.

> Vérifié par : `TestWebsiteBookingTunnel.test_slot_booking_end_to_end`,
> `test_stay_request_creates_a_draft_reservation` — le tunnel est joué en
> HTTP réel, jeton CSRF compris.

---

#### A3 — La réception ne pouvait pas encaisser

Enregistrer un règlement de folio déclenche l'écriture 411. La résolution
du **journal** et du **compte client** se faisait sans `sudo()` : un
utilisateur du profil *Réception*, qui n'a pas les droits comptables,
heurtait une `AccessError` au moment d'encaisser.

> `You are not allowed to access 'Journal' (account.journal) records.`

Le même défaut existait sur les remboursements d'ardoise, côté caisse.

**Correction.** Résolution du journal et du compte 411 en `sudo()` dans
les deux modules — le contrôle d'accès reste porté par le règlement
lui-même.

> Vérifié par :
> `TestHotelSecurity.test_receptionist_collects_payment_with_accounting_on`,
> `TestCreditSecurity.test_cashier_records_a_repayment_with_accounting_on`.

---

#### A4 — Le responsable hôtel ne pouvait créer ni type de chambre ni service

Créer un type de chambre crée son article support (`product.product`).
L'écriture n'était pas en `sudo()` : le profil *Responsable* du module
hôtelier n'ayant pas de droits sur les articles, la création échouait.

> `You are not allowed to create 'Product Variant' (product.product) records.`

Même défaut sur les services hôteliers, et sur le marquage
`is_hotel_guest` du client à la création d'une réservation — qui bloquait
la *Réception*.

**Correction.** Ces trois écritures techniques passent en `sudo()`.

> Vérifié par : `TestHotelSecurity.test_manager_creates_service_with_linked_product`,
> `test_manager_configures_everything`, `test_receptionist_books_and_checks_in`.

---

### 2.2 Majeures

#### A5 — Une chambre retirée d'un séjour restait facturée

Retirer une chambre d'une réservation confirmée laissait sa **nuitée sur
le folio**. Le client restait facturé pour une chambre qu'il n'occupait
plus.

Cause : `reservation_line_id` est en `ondelete='set null'`. Supprimer la
ligne de séjour vide la référence au lieu de retirer la nuitée ; la
boucle de nettoyage, qui cherchait les lignes « dont la réservation a
disparu », ne les voyait plus.

Constaté sur un cas réel : 2 chambres à 23 000, une chambre retirée, le
folio restait à 46 000 pour une seule chambre.

**Correction.** La resynchronisation retire aussi les nuitées orphelines
(type « chambre » sans ligne de séjour).

> Vérifié par : `TestFolio.test_removed_room_stops_being_billed`.

---

#### A6 — Le cockpit Direction présentait toute la dette comme critique

La **balance âgée en miroir** rangeait la totalité de l'encours client
dans la tranche « **+90 j** », quelle que soit l'ancienneté réelle.
Constaté à l'écran : 1 920 250 FG intégralement en « +90 j », alors que
le moteur Crédit répartissait correctement 4 / 6 / 3 / 3 ardoises sur les
quatre tranches.

Cause : le cockpit reventilait les tranches d'après `min` / `max`, que
`get_aging()` ne renvoyait pas. `max` valant `None`, la règle « pas de
borne haute ⇒ +90 j » s'appliquait à **toutes** les lignes. Les libellés
du composant OWL divergeaient de surcroît de ceux du moteur
(« 31–60 j » contre « 30–60 j »).

Conséquence : un gérant lisant son cockpit voyait 100 % de ses créances
comme gravement en retard.

**Correction.** `get_aging()` expose désormais la clé de tranche et ses
bornes ; le cockpit la reprend telle quelle et les libellés sont alignés.

> Vérifié par :
> `TestDirectionDashboard.test_mirror_aging_spreads_across_the_buckets`,
> `test_credit_engine_exposes_bucket_keys`.

---

#### A7 — Les ardoises n'étaient pas cloisonnées entre sociétés

`aite_pos_credit` ne posait **aucune règle multi-sociétés**, contrairement
au module hôtelier qui en pose cinq. Dans un groupe à plusieurs sociétés,
un utilisateur voyait les ardoises et les remboursements des autres
sociétés — dans la liste, sur la fiche client (encours) et dans le
tableau de bord du recouvrement.

**Correction.** Deux règles d'enregistrement ajoutées
(`aite.pos.credit`, `aite.pos.credit.payment`), et filtre société
explicite dans les domaines du tableau de bord.

---

#### A8 — Le module de démonstration faisait échouer l'installation

`aite_demo_data` déclarait une caisse (`pos.config`) en XML. Créer un
point de vente exige un journal de banque, donc un plan comptable : sur
une société qui n'en a pas encore, **l'installation entière échouait**.

> `Ensure that there is an existing bank journal. Check if chart of accounts is installed in your company.`

**Correction.** La caisse est créée par le générateur, qui vérifie la
présence d'un journal de trésorerie et passe son tour avec un
avertissement clair le cas échéant. Le module s'installe désormais sur
n'importe quelle base.

---

### 2.3 Mineures

#### A9 — Lire un compteur écrivait en base

Sur le folio et sur l'ardoise, le champ non stocké `payment_count`
partageait sa méthode de calcul avec des champs **stockés**. Odoo le
signalait au chargement :

> `inconsistent 'store' for computed fields, accessing payment_count may recompute and update amount_paid, amount_residual`

Concrètement, afficher le bouton statistique déclenchait une écriture en
base — et pouvait lever une `AccessError` en contexte lecture seule.

**Correction.** Méthode de calcul distincte pour le compteur.

> Vérifié par : `TestFolio.test_payment_count_does_not_write_stored_fields`,
> `TestPosCredit.test_payment_count_uses_its_own_compute`.

---

#### A10 — Défauts de conformité Odoo 18

| Défaut | Correction |
|---|---|
| `aite.pos.credit.state` déclarait `tracking=True` sans `mail.thread` : la promesse d'audit n'était pas tenue et Odoo journalisait un avertissement | Paramètre retiré |
| `group_operator='avg'` — déprécié depuis Odoo 18 | Remplacé par `aggregator='avg'` |
| Deux champs de `res.company` portaient le libellé « E-mail de confirmation automatique » (hôtel et espaces), rendant l'écran Paramètres et les exports ambigus | Libellés qualifiés |
| `aite_demo_data` n'avait pas de clé `description` : Odoo rendait son `README.md` **comme du RST** et la fiche Apps s'affichait criblée de blocs d'erreur docutils | Description RST ajoutée |

---

#### A11 — Une tentative de réservation refusée laissait un fantôme

Sur le site, si le créneau venait d'être pris, la réservation était créée
puis la confirmation échouait — le **brouillon restait en base**. Chaque
tentative refusée polluait le back-office d'une demande fantôme.

**Correction.** Création et confirmation encadrées par un point de
sauvegarde : un échec ne laisse aucune trace.

> Vérifié par : `TestWebsiteBookingTunnel.test_refused_attempt_leaves_no_ghost_booking`.

---

## 3. Points d'attention signalés, non corrigés

Ces points ne sont pas des défauts, mais méritent une décision.

| Sujet | Constat | Recommandation |
|---|---|---|
| **Périmètre de la gouvernante** | Le profil *Gouvernante* a le droit d'écriture sur `aite.hotel.room` — nécessaire pour l'état de propreté, mais il ouvre aussi le tarif spécifique et la mise hors service | Restreindre par groupe au niveau des champs sensibles si le cloisonnement doit être strict |
| **Bascule d'état du folio** | L'état (`ouvert` → `soldé`) est écrit depuis une méthode de calcul : il ne bascule que lorsqu'un montant calculé est relu. Sans effet dans l'interface, qui lit toujours les montants | Documenté ; à revoir si un traitement par lot venait à s'appuyer sur `state` seul |
| **Dates invalides** | POS Analytics **refuse** une période illisible (`UserError`) ; Hôtel, Stock, Crédit et Achats **retombent** sur le mois courant | Choisir une convention unique pour la suite |
| **Devise du jeu d'essai** | Le jeu annonce des prix en GNF mais ne configure pas la devise de la société | Documenté en § 2.3 du guide de test ; une bascule automatique serait trop intrusive |

---

## 4. Le module de jeu d'essai

`aite_demo_data` a été vérifié et étendu.

### Ce qu'il couvrait

Référentiel seul : établissement, chambres, catalogue, clients,
réservations, folios, fidélité, stock. Les modules **Crédit clients**,
**Note de chambre**, **Achats** et **POS Analytics** restaient **vides** —
leurs tableaux de bord aussi.

### Ce qu'il couvre désormais

Un **générateur paramétrable** (`aite.demo.generator`) complète le
référentiel XML, en trois volumes et de façon idempotente :

- **168 commandes en caisse** sur 21 sessions closes, réparties sur les
  pics de midi et du soir, avec des écarts de caisse à traiter ;
- **18 ardoises** de 3 à 160 jours, dont 9 partiellement remboursées,
  couvrant les quatre tranches de la balance âgée ;
- **5 notes de chambre en attente**, illustrant les trois motifs
  d'ambiguïté ;
- **12 tâches de gouvernante**, tous types, à différents stades ;
- **8 services hôteliers** et **2 tarifs saisonniers** par type de chambre ;
- **8 commandes d'achat** et **5 consignes fournisseurs** ;
- **5 profils utilisateurs** métier, sur lesquels s'appuie la recette.

Un assistant (Paramètres → **Jeu d'essai AITE**) permet de régénérer ou
de purger sans passer par le shell — utile sur une base de démonstration
qui vieillit, les données étant datées relativement au jour
d'installation.

---

## 5. Recette utilisateur

Six scénarios joués dans Chromium, avec les profils métier, 32 étapes,
32 captures. Le détail figure dans
[`GUIDE_RECETTE_UAT.md`](GUIDE_RECETTE_UAT.md).

| Scénario | Poste | Étapes | Verdict |
|---|---|---:|---|
| La journée de la réception | Réception | 7 | ✅ |
| Le tour des chambres | Gouvernante | 4 | ✅ |
| Ardoises clients et recouvrement | Caisse | 7 | ✅ |
| Le cockpit de la direction | Direction | 7 | ✅ |
| La réservation en ligne | Client (public) | 6 | ✅ |
| Stock, ruptures et réapprovisionnement | Magasin | 2 | ✅ |

Les scénarios vérifient aussi le **cloisonnement** : la gouvernante ne
doit pas atteindre les folios, le caissier ne doit pas atteindre le PMS,
le magasinier ne doit pas atteindre les ardoises. Ces trois refus sont
constatés à l'écran, et l'assertion exige la boîte « Access Error »
d'Odoo **nommant le modèle concerné** — chercher le mot « accès » dans la
page laisserait passer n'importe quel écran.

C'est la recette qui a révélé l'anomalie **A6** : le calcul était juste
côté serveur, seul l'affichage mentait. Aucun test unitaire ne l'aurait
vue.

### Deux corrections apportées au dispositif de test lui-même

La relecture des captures a mis au jour deux faiblesses de la campagne,
corrigées avant la livraison. Elles ne concernent pas le produit, mais
elles conditionnent la valeur du rapport.

1. **Un faux positif sur la réservation en ligne.** Le scénario tentait
   de choisir le créneau avec `select_option`, alors que les créneaux
   sont des **boutons radio** : le formulaire n'était jamais envoyé, et
   l'assertion — trop large — passait quand même parce que la page
   contenait encore le mot « réserv ». L'étape affirmait une réussite
   sans réservation. Le scénario coche désormais un créneau et exige la
   **référence de la réservation** sur la page de remerciement.

2. **Des fixtures qui ne tenaient que sur une base vierge.** Quatre jeux
   de test créaient un moyen de paiement « espèces » sur le journal de
   caisse de la société. Sur une base portant le jeu d'essai — c'est-à-dire
   l'installation documentée — Odoo refusait : *« You cannot use the same
   journal on multiples cash payment methods »*, et cinq classes de test
   ne démarraient pas. Chaque fixture crée maintenant son propre journal.
   La suite passe donc aussi bien sur une base neuve que sur une base
   chargée.

---

## 6. Comment reproduire

Voir [`GUIDE_TESTS.md`](GUIDE_TESTS.md), § 2 à 4.

```bash
# Tests automatisés
odoo-bin -d aite_test --test-enable --stop-after-init \
  -u aite_demo_data --test-tags aite_journey

# Recette navigateur
python tests_uat/run_uat.py --url http://127.0.0.1:8069
python tests_uat/build_guide.py
```

---

© AITE Consulting SARL — tous droits réservés.
