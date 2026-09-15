# AITE HOUSE — Rapport de campagne de tests

**Suite hôtelière AITE HOUSE · Odoo 18 · 13 modules**
AITE Consulting SARL

---

## 1. Résumé

La suite n'avait, avant cette campagne, **aucun test automatisé**. Elle en
compte aujourd'hui **604**, tous verts, doublés d'une **recette
utilisateur en navigateur** de 34 étapes jouée avec les profils métier
réels.

| Indicateur | Avant | Après |
|---|---:|---:|
| Tests automatisés | 0 | **604** |
| Modules couverts | 0 / 12 | **12 / 12** |
| Parcours métier bout-en-bout | 0 | **6** |
| Scénarios de recette (navigateur) | 0 | **6** (34 étapes) |
| Captures d'écran de recette | 0 | **34** |
| Anomalies corrigées | — | **14** |
| Décisions de cadrage appliquées | — | **3** |

La campagne a été validée sur une base **construite entièrement de
zéro** : création, installation des 13 modules, génération du jeu
d'essai, puis exécution des 604 tests et des 6 scénarios de recette.

Résultat de la dernière exécution complète :

```
odoo.tests.result: 0 failed, 0 error(s) of 604 tests
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

#### A12 — Un manquant en caisse restait classé « Modéré »

`cash_discrepancy_severity` classe l'écart de caisse d'une session en
cinq niveaux, jusqu'à « Critique ». Le champ est **stocké et indexé** :
c'est lui qui filtre les vues et alimente l'alerte du tableau de bord.

Il ne bougeait jamais après le comptage de la caisse.

Cause : il était calculé à partir de `cash_register_difference`, un champ
Odoo **calculé et non stocké** dont l'`@api.depends` natif **omet**
`cash_register_balance_end_real` — précisément le montant que le caissier
saisit en comptant son tiroir. Le comptage ne déclenchait donc aucun
recalcul, et la sévérité restait figée sur l'écart d'avant clôture.

Constaté sur un cas réel : une caisse close sur un **manquant de
250 000 FG** — au-delà du seuil critique — restait affichée « Modéré ».

**Correction.** La classification refait la soustraction sur les deux
termes qui, eux, sont à jour au moment du recalcul (montant compté et
solde théorique), et se déclenche sur les champs sous-jacents. La garde
d'Odoo est reprise telle quelle : sans moyen de paiement espèces, la
caisse n'a pas de solde et il n'y a pas d'écart à classer.

> Vérifié par : `TestPosMargins.test_counting_the_till_updates_the_severity`,
> `test_recounting_the_till_reclassifies_the_session`,
> `test_counting_the_till_walks_the_whole_scale`.

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

#### A13 — Aucune session de démonstration n'avait d'écart de caisse

Le générateur annonçait « des écarts de caisse à traiter » et écrivait
`cash_register_difference`. Ce champ étant **calculé et non stocké**, y
écrire ne produit rien : **toutes** les sessions du jeu d'essai
présentaient une caisse parfaitement juste, et l'écran des écarts de
caisse n'avait rien à montrer.

Le test censé le couvrir ne pouvait pas le voir : il cherchait
`[('cash_register_difference', '!=', 0)]`. Odoo ne sait pas filtrer sur
un champ non stocké — il journalise *« Non-stored field … cannot be
searched »* et **laisse passer toutes les lignes**. Le test trouvait donc
toujours des « écarts », y compris quand il n'y en avait aucun.

**Correction.**

- Le générateur pose le **montant compté** à côté du solde théorique —
  le geste réel du caissier — dans une passe finale, une fois toutes les
  sessions créées : le solde d'une session dépend du fonds hérité de la
  précédente, si bien que compter au fil de l'eau comparait un montant
  réel à un théorique déjà périmé. Les manquants passent au-delà du
  seuil critique, pour que l'alerte la plus forte soit servie.
- Une base montée avec la version précédente se remet d'aplomb en
  relançant la génération : les sessions déjà posées sont recomptées.
- Le test trie en Python, sur la valeur réellement calculée, et se
  limite aux sessions du jeu d'essai — une recherche globale rapporterait
  aussi celles d'une base déjà vécue.

> Vérifié par : `TestDemoGenerator.test_some_sessions_show_a_cash_gap`,
> `test_cash_gaps_do_not_touch_every_session`,
> `test_a_cash_gap_reaches_the_critical_grade`.

---

### 2.4 Décisions de cadrage appliquées

Ces trois points n'étaient pas des défauts : la campagne les avait
signalés comme relevant d'un choix. Le choix a été arrêté, puis mis en
œuvre et couvert par des tests.

#### D1 — Le tarif d'une chambre sort du périmètre de la gouvernante

La gouvernante doit pouvoir écrire sur `aite.hotel.room` — c'est là que
vit l'état de propreté. Mais ce même droit lui ouvrait le **tarif
spécifique**, le **type de chambre**, les **capacités** et l'archivage :
requalifier une chambre revient à en changer le prix de vente.

**Décision retenue : restreindre les champs tarifaires à la Réception et
au Responsable.**

- `price_override` et `effective_price` portent désormais
  `groups="…group_hotel_user"` : la gouvernante ne les voit plus, ni sur
  la fiche, ni sur le kanban (séparateur compris), ni dans `fields_get`.
- Une garde d'écriture sur `write()` refuse, pour elle seule, les champs
  qui reclassent ou revalorisent une chambre — type, capacités, hôtel,
  tarif, archivage. Le refus **nomme les champs** et indique vers qui se
  tourner.
- Elle conserve ses propres leviers : état de ménage, hors service et son
  motif, note interne, boutons rapides. La recouche automatique au départ
  du client continue de passer.

> Vérifié par : 11 tests de `TestHotelSecurity`, de
> `test_housekeeper_does_not_see_the_room_price` à
> `test_checkout_still_sends_the_room_to_cleaning`, plus l'étape 4 du
> scénario de recette *Le tour des chambres*.

---

#### D2 — Une période illisible ramène au mois courant, partout

Quatre tableaux de bord sur cinq retombaient sur le **mois courant**
quand la période était illisible — champ vidé, saisie partielle, appel
sans paramètre. POS Analytics, lui, **refusait** par une `UserError` :
le même geste ouvrait un tableau de bord ici, et une boîte d'erreur là.

**Décision retenue : aligner POS Analytics sur les quatre autres.**

`_parse_period` retombe sur le mois courant, et des bornes inversées sont
remises dans l'ordre. `_previous_period` passe par la même porte — la
comparaison porte donc toujours sur la période réellement affichée, et
non sur une période calculée à partir de bornes que l'écran a rejetées.

> Vérifié par : `TestPosDashboardApi.test_bad_dates_fall_back_to_the_current_month`,
> `test_inverted_period_is_reordered`,
> `test_every_endpoint_survives_illegible_dates`,
> `test_endpoints_without_dates_always_answer`.

---

#### D3 — Le jeu d'essai pose sa devise, mais seulement sur une base vierge

Le jeu d'essai annonce des prix en francs guinéens sans configurer la
devise de la société : les montants s'affichaient en dollars.

**Décision retenue : basculer en GNF si — et seulement si — la base est
vierge.**

Le générateur ne change la devise que si la société est **encore sur une
devise d'origine** (`USD` ou `EUR`) **et** qu'elle ne porte **aucune
écriture comptable**. Une devise délibérément choisie, ou une société
déjà en production, n'est jamais écrasée : le générateur le journalise et
passe son tour. La devise retenue figure dans le compte rendu de
génération.

> Vérifié par : `TestDemoGenerator.test_currency_switches_on_an_untouched_company`,
> `test_currency_is_left_alone_once_entries_exist`,
> `test_currency_is_left_alone_when_deliberately_chosen`,
> `test_currency_is_idempotent`, `test_generation_reports_the_currency`.

---

## 3. Points d'attention

Aucun point n'est laissé ouvert. Celui qui figurait ici — la bascule
d'état du folio — a été mesuré puis traité ; le constat de départ, trop
inquiet, est rectifié ci-dessous.

---

### A14 — Un folio pouvait se lire « soldé » alors qu'il ne l'était plus

**Le constat initial était exagéré.** Il annonçait qu'un traitement par
lot s'appuyant sur `state` pourrait lire une valeur périmée. La mesure,
faite sur les quatre chemins qui déplacent l'argent d'un folio en lisant
à chaque fois **la ligne réellement écrite en base**, dit l'inverse :

| Situation | En base | |
|---|---|---|
| Règlement total encaissé | `('paid', 0)` | ✅ |
| Règlement annulé | `('invoiced', 50 000)` | ✅ |
| Un règlement sur deux annulé | `('invoiced', 25 000)` | ✅ |
| Prestation ajoutée après facturation | `('invoiced', 15 000)` | ✅ |
| `search(state='paid')` après annulation | ne le trouve plus | ✅ |

La base ne porte jamais d'incohérence, et aucune recherche ne peut en
rapporter une : Odoo vide ses écritures en attente avant chaque requête.
**Les traitements par lot n'ont jamais été exposés.**

Le défaut réel était plus étroit — et bien réel. Dans une **même
transaction**, l'enregistrement relu juste après le geste gardait
l'ancien état :

> Une caissière annule un règlement saisi par erreur. Le solde dû
> remonte aussitôt à 50 000, mais la note continue d'afficher
> « Soldé » — les deux informations se contredisent à l'écran.

Cause : la bascule `facturé` ⇄ `soldé` est écrite depuis le calcul des
montants. Ce couplage est **délibéré et sûr** — en chevauchant le calcul,
la bascule attrape *tous* les chemins qui déplacent une somme, y compris
ceux qu'aucune action ne signale, comme l'ajout d'une prestation sur un
folio déjà facturé. Mais un calcul ne s'exécute qu'à la relecture d'un
montant : d'ici là, l'enregistrement en mémoire reste sur l'état
précédent.

Le contournement existait déjà à un seul endroit — `action_create_invoice`
forçait le recalcul — sans être appliqué ailleurs.

**Correction.** Une méthode `_refresh_settlement()` remet montants et
état d'accord immédiatement, appelée par tout ce qui déplace de l'argent :
encaissement, annulation de règlement, facturation, et écriture d'une
ligne de folio (création, changement de prix, suppression). Le couplage
au calcul des montants est conservé — c'est lui qui garantit qu'aucun
chemin n'est oublié ; seule la fraîcheur de la lecture est corrigée. Le
rafraîchissement des lignes est groupé, pour ne pas recalculer à chaque
passage de la boucle qui pose les nuitées.

> Vérifié par : 9 tests de `TestFolio`, de
> `test_settling_the_folio_marks_it_paid` à
> `test_removing_a_line_can_settle_the_folio`. Chacun contrôle l'état lu
> immédiatement **et** la ligne écrite en base — les deux garanties qui
> comptent.

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

Six scénarios joués dans Chromium, avec les profils métier, 34 étapes,
34 captures. Le détail figure dans
[`GUIDE_RECETTE_UAT.md`](GUIDE_RECETTE_UAT.md).

| Scénario | Poste | Étapes | Verdict |
|---|---|---:|---|
| La journée de la réception | Réception | 7 | ✅ |
| Le tour des chambres | Gouvernante | 5 | ✅ |
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

### Trois corrections apportées au dispositif de test lui-même

La relecture des captures et des journaux a mis au jour trois faiblesses
de la campagne, corrigées avant la livraison. Elles ne concernent pas le
produit, mais elles conditionnent la valeur du rapport.

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

3. **Un test vert qui ne testait rien.** Le contrôle des écarts de caisse
   du jeu d'essai filtrait sur un champ **calculé et non stocké**. Odoo
   ne sait pas le faire : il journalise *« Non-stored field … cannot be
   searched »* et laisse passer toutes les lignes. Le test trouvait donc
   toujours des écarts — y compris quand le jeu d'essai n'en produisait
   aucun, ce qui était le cas (**A13**). C'est une ligne d'erreur dans le
   journal d'une exécution pourtant annoncée « 0 failed » qui a mis sur
   la piste, et de là sur **A12**. Trois tests de classification qui
   posaient la valeur directement en cache ont été réécrits pour partir
   du geste réel — le caissier compte son tiroir — seul chemin qui
   existe en production.

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
