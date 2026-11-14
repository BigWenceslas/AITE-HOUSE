# AITE HOUSE — Suite de gestion hôtelière sur Odoo 18
**Version du paquet : novembre 2026 (vague 1 et restaurant, lot 1) · 18 modules · Odoo 18 (Community & Enterprise)**

Un restaurant **sans hôtel** n'installe que les modules de la caisse : voir le §9, « Restaurant seul ».

Éditeur : AITE Consulting SARL — Douala, Makepe Bloc F
info@aite-consulting.com · (+237) 673 373 367 / 656 801 098 · https://aite-consulting.com

---

## 1. Contenu

```
AITE_HOUSE/
├── addons/            les 18 modules à déposer sur le serveur (16 pour l'hôtel ;
│                      un restaurant seul en dépose 4, voir §9)
├── docs/              ce fichier, notes de version, guides utilisateur, fiches
│                      produit, plaquette, guide de test, cahiers de recette
├── recette/           cahier de recette (139 cas) et plan de recette
├── tests/, tests_uat/ scénarios « utilisateur novice » et recette navigateur
└── ROADMAP.md         ce qui est livré, ce qui reste
```

## 2. Les modules

| Module | Version | Rôle |
|---|---|---|
| aite_hotel_management | 18.0.1.0.7 | **Socle hôtelier** : chambres, réservations, séjours, folios, main courante, facturation |
| aite_slot_booking | 18.0.1.0.5 | Espaces & prestations réservables au créneau (salles, piscine, billard…) |
| aite_website_booking | 18.0.1.0.2 | Réservation en ligne depuis le site web, acompte |
| aite_hotel_pos_link | 18.0.1.0.3 | **Note de chambre** : report des consommations du bar sur le folio |
| aite_pos_credit | 18.0.2.0.6 | Crédit clients (ardoises) : plafonds, encours, recouvrement ; l'ardoise ne naît que d'une commande réglée |
| aite_loyalty | 18.0.1.0.3 | Fidélité : points, niveaux VIP & VVIP |
| aite_pos_analytics | 18.0.2.1.6 | Analyses des ventes : heures de pointe, marges, CMV, ventes par famille sur trois niveaux |
| aite_stock_dashboard | 18.0.1.1.3 | Stock : ruptures, coulage, couverture, inventaires |
| aite_purchase_dashboard | 18.0.1.0.5 | Achats : échéancier fournisseurs, OTIF, hausses de prix |
| aite_direction_dashboard | 18.0.1.1.2 | **Cockpit Direction** : vue consolidée, cash à risque, actions |
| aite_exec_dashboard | 18.0.1.1.2 | **Activité par pôle** (Hôtel → Activité par pôle) : hébergement, restauration, prestations, RevPAR, pickup, pace |
| aite_hotel_gantt | 18.0.1.0.2 | **Enterprise uniquement** : planning Gantt des chambres (automatique sur une base neuve, **à installer à la main** sur une base existante — voir §3) |
| aite_demo_data | 18.0.1.2.4 | Jeu de démonstration (établissement complet pré-chargé) |
| aite_city_tax | 18.0.1.0.2 | **Taxe de séjour** automatique : barèmes par pays et étoiles, ligne sur le folio, état mensuel |
| aite_guest_registry | 18.0.1.0.3 | **Registre des clients** : fiche d'enregistrement au check-in, registre de police, statistiques |
| aite_housekeeping | 18.0.1.0.6 | **Gouvernante & maintenance** : tableau des chambres, « Ma journée », inspections, pannes, objets trouvés |
| aite_pos_restaurant | 18.0.1.0.6 | **Restaurant (service à table)** : code personnel et quatre niveaux, plan de salle verrouillé, personnes, annulations sous code et leur journal, couleurs des tables, refus des produits épuisés, « Personnes et tables » — voir §9 |
| aite_pos_analytics_hr | 18.0.1.0.0 | Passerelle : serveur (« ouverte par ») et « encaissée par » dans les analyses AITE ; s'installe seule avec les deux modules précédents |

## 3. Prérequis

- Odoo 18 (Community ou Enterprise), PostgreSQL, accès au serveur.
- Modules Odoo standard requis (installés automatiquement) : `point_of_sale`,
  `sale`, `account`, `purchase`, `stock`, `website`, `portal`, `mail`,
  `product`, `web`, `maintenance` (Community).
- **Un plan comptable installé sur la société** avant d'installer le Point
  de Vente ou le jeu de démonstration : Odoo exige un journal de banque
  pour créer une caisse. Sur une base neuve, installez le module de
  localisation comptable de votre pays (Comptabilité → Configuration), ou
  créez la base avec les données de démonstration Odoo.
- **Devise de la société en FCFA (`XAF`)** — celle sur laquelle sont
  calibrés les seuils du produit (écart de caisse, paliers de fidélité), à
  positionner **avant** toute écriture comptable — Odoo refuse ensuite
  d'en changer.

### Community ou Enterprise ?

La suite s'installe sur les **deux éditions**. Le seul écart est le
planning des chambres :

- sur **Community**, il s'affiche en vue **calendrier** ;
- sur **Enterprise**, le module `aite_hotel_gantt` ajoute la vue
  **Gantt** (barres par chambre) : Hôtel → Réservations → Planning des
  chambres s'ouvre alors sur le Gantt, le calendrier restant accessible.

Sur Enterprise, `aite_hotel_gantt` ne s'installe **tout seul** que
lorsqu'une de ses dépendances est elle-même en cours d'installation :
sur une **base neuve**, en même temps que le socle `aite_hotel_management`
(étape 1 du §4), ou plus tard si une application Enterprise installe
`web_gantt`. Odoo n'examine un module « auto-installable » qu'à ce
moment-là :

- **base où le socle est déjà installé** (cas d'une mise à jour, comme
  chez LAVERANDAH) : une mise à niveau du socle **ne l'installe pas**.
  Il faut l'installer **une fois, à la main** :
  1. déposer le dossier `aite_hotel_gantt` à côté des autres, redémarrer ;
  2. Apps → **« Mettre à jour la liste des applications »** ;
  3. Apps → retirer le filtre « Applications » → chercher **« Gantt »** →
     « AITE — Planning Gantt des chambres (Enterprise) » → **Installer**.

  En ligne de commande, c'est équivalent à
  `odoo-bin -c <odoo.conf> -d <base> -i aite_hotel_gantt --stop-after-init`.
  Si le module Odoo `web_gantt` n'était pas encore installé, il
  s'installe avec. Ensuite plus rien à faire : les mises à niveau suivantes
  le gardent.
- **Vérifier** : Hôtel → Réservations → **Planning des chambres** propose
  la vue Gantt dans le sélecteur de vues (en haut à droite) et s'ouvre
  dessus.

## 4. Installation

1. **Déposer** les 16 dossiers de `addons/` dans le répertoire des addons
   personnalisés du serveur — celui déclaré dans `addons_path` de
   `odoo.conf`. Les déposer **à côté** des dossiers existants ; ne jamais
   remplacer le répertoire entier.
2. **Redémarrer** le service Odoo.
3. Apps → retirer le filtre « Applications » → **« Mettre à jour la liste
   des applications »**.
4. **Installer dans cet ordre** (les dépendances font le reste) :
   1. `aite_hotel_management`
   2. `aite_slot_booking`, puis `aite_website_booking`
   3. `aite_pos_analytics`, `aite_pos_credit`, `aite_hotel_pos_link`
   4. `aite_loyalty`
   5. `aite_stock_dashboard`, `aite_purchase_dashboard`
   6. `aite_direction_dashboard`, `aite_exec_dashboard`
   7. `aite_city_tax`, `aite_guest_registry`, `aite_housekeeping` (vague 1 —
      voir `NOTES_DE_VERSION_vague1.md` : renseigner ensuite le **pays** et la
      **catégorie (étoiles)** de chaque hôtel, c'est tout ce que la taxe de
      séjour demande)
   8. `aite_demo_data` *(uniquement sur une base de démonstration)*

   Sur Enterprise, `aite_hotel_gantt` s'ajoute seul à l'étape 1 (base
   neuve) : il ne figure pas dans cette liste. Si le socle était **déjà
   installé** avant d'y déposer `aite_hotel_gantt`, installez-le à la main
   (voir « Community ou Enterprise ? » au §3).
5. **Ctrl+Shift+R** dans le navigateur (les assets sont recompilés).
6. Vérifier : l'écran **Paramètres** doit s'afficher jusqu'en bas, avec les
   sections AITE (Note de chambre, Fidélité, Crédit, Réservations…).

## 5. Mise à jour d'une installation existante

1. **Sauvegarder la base** (et le dossier `filestore`).
2. **Fermer toutes les sessions de caisse** : une caisse ouverte ne peut pas
   recevoir de nouveau mode de paiement (le journal le signale par un
   avertissement, la mise à niveau continue).
3. **Déposer** les dossiers `addons/aite_*` livrés **à côté** des autres, en
   remplaçant chaque dossier AITE par sa nouvelle version — jamais le
   répertoire `addons` entier.
4. Redémarrer le service Odoo, puis Apps → **« Mettre à jour la liste des
   applications »** → **« Mettre à niveau »** **chaque** module AITE installé
   (ou en ligne de commande : `-u` suivi de la liste des modules AITE). Les
   scripts de migration livrés s'exécutent à cette étape (voir les notes de
   version de la livraison).
5. Chaque utilisateur recharge la page (**Ctrl+F5**) : le JavaScript et les
   styles des tableaux de bord changent.
6. Faire les **vérifications** listées dans les notes de version de la
   livraison (barème de taxe de séjour, mode « Ardoise », profil
   « Gouvernante générale »…).

Ne rien désinstaller. Sur Enterprise, si `aite_hotel_gantt` est livré pour
la première fois sur une base où le socle est déjà installé, la mise à
niveau ne l'installe pas : l'installer à la main une fois (§3, « Community
ou Enterprise ? »). Ne jamais retirer des fichiers avant d'avoir désinstallé
proprement le module depuis Apps.

## 6. Désinstallation

Désinstaller **depuis Apps** avant toute suppression de fichiers, dans
l'ordre inverse : `aite_demo_data` en premier, `aite_hotel_management` en
dernier.

## 7. Dépannage

| Symptôme | Cause probable | Correction |
|---|---|---|
| `"champ aite_xxx" is undefined` sur Paramètres | Dossier(s) de module absent(s) du serveur alors que le module reste installé en base | Redéposer les 16 dossiers, redémarrer, mettre à jour la liste des applications |
| Un module n'apparaît pas dans Apps | `addons_path` ne pointe pas vers le répertoire utilisé | Vérifier `odoo.conf` et la commande de lancement du service |
| Écran blanc ou composant manquant | Cache navigateur | Ctrl+Shift+R ; sur le Point de Vente, fermer et rouvrir la session |
| Erreur à l'installation | Dépendance Odoo absente | Installer d'abord le module standard concerné (voir §3) |
| `Ensure that there is an existing bank journal` | Aucun plan comptable sur la société | Installer le module de localisation comptable du pays, puis relancer l'installation (voir §3) |
| `aite_hotel_gantt` reste « non installé » | Odoo Community : `web_gantt` n'existe pas | Comportement normal — le planning s'affiche en vue calendrier |
| Odoo Enterprise, pas de vue Gantt dans « Planning des chambres » | `aite_hotel_gantt` déposé sur une base où le socle était déjà installé : Odoo ne l'installe pas tout seul à la mise à niveau | Apps → retirer le filtre « Applications » → chercher « Gantt » → Installer (voir §3) |
| Montants affichés dans la mauvaise devise | Devise de la société non positionnée | Paramètres → Sociétés → Devise, **avant** toute écriture comptable |
| Tableaux de bord vides sur une base de démonstration | Jeu d'essai daté, devenu hors période | Paramètres → **Jeu d'essai AITE** → Générer |

En cas de blocage, transmettre à AITE Consulting les lignes `ERROR` /
`Traceback` du log Odoo et le contenu de `addons_path`.

## 8. Documentation fournie

- **Guides utilisateur** (PDF illustrés) : Note de chambre, Réservation en
  ligne, Fidélité, Espaces & prestations, Tableau de bord Direction.
- **Fiches produit** : POS Analytics, POS Crédit.
- **Plaquette commerciale** AITE HOUSE (19 pages) et **flyer**.

### Documentation de test

- **[`GUIDE_TESTS.md`](GUIDE_TESTS.md)** — monter un
  environnement de test, exécuter les 613 tests automatisés, régénérer le
  jeu d'essai.
- **[`GUIDE_RECETTE_UAT.md`](GUIDE_RECETTE_UAT.md)** —
  cahier de recette illustré : 6 scénarios, 34 étapes, une capture
  d'écran par étape, joués avec les profils métier réels.
- **[`CAHIER_RECETTE_AITE_HOUSE.pdf`](CAHIER_RECETTE_AITE_HOUSE.pdf)**
  — le même cahier en **PDF paginé** (38 pages), à imprimer ou à
  transmettre au client. Régénéré par `python tests_uat/build_pdf.py`.
- **[`RAPPORT_TESTS.md`](RAPPORT_TESTS.md)** — rapport de
  campagne : anomalies trouvées, corrections apportées, points
  d'attention.
- `captures_uat/` — les captures d'écran de la recette navigateur ;
  `../recette/` — le cahier de recette fonctionnel (139 cas, 16 domaines) et son plan.


## 9. Restaurant seul (sans hôtel) — lot 1 du restaurant

Pour un restaurant, un bar ou une pizzeria **sans hébergement** : la caisse
de service à table (`aite_pos_restaurant`), ses analyses et l'ardoise.
Aucun module hôtelier n'est installé. Ce qui change à la caisse est décrit
dans [`NOTES_DE_VERSION_restaurant_lot1.md`](NOTES_DE_VERSION_restaurant_lot1.md).

### 9.1 Ce que le client installe

| Dossier à déposer | Version | Rôle |
|---|---|---|
| `aite_pos_restaurant` | 18.0.1.0.6 | la caisse du restaurant : code personnel, quatre niveaux, plan verrouillé, personnes, annulations sous code, couleurs, produits épuisés, rapports |
| `aite_pos_analytics` | 18.0.2.1.6 | analyses des ventes, dont les ventes par famille sur trois niveaux |
| `aite_pos_analytics_hr` | 18.0.1.0.0 | passerelle : le serveur et la caissière dans les analyses ; s'installe seule |
| `aite_pos_credit` | 18.0.2.0.6 | ardoises : réservées au manager en caisse, créées seulement sur une addition réglée |

Odoo installe avec eux, sans rien demander : Point de Vente, Restaurant,
Employés et la connexion des employés au Point de Vente, Inventaire,
Facturation et Ventes. Les autres modules AITE ne sont pas nécessaires.

### 9.2 Avant d'installer

- **Créer la base avec l'écran de création d'Odoo**, pays **Cameroun**,
  langue **Français**, **sans** données de démonstration : la société naît
  en **FCFA** avec le plan comptable camerounais. Une base créée en ligne de
  commande sans pays naît en dollars, et Odoo refuse ensuite de changer la
  devise. Sur une base existante : Paramètres → Sociétés → la devise doit
  être `XAF` avant toute vente.
- Ne pas lancer le **scénario « Restaurant »** qu'Odoo propose sur un Point
  de Vente vide : il charge des produits en anglais et des additions
  d'exemple, et laisse une caisse ouverte. Le module pose lui-même la
  caisse « Restaurant ».

### 9.3 Installer, dans cet ordre

1. **Déposer** les 4 dossiers du §9.1 à côté des autres dossiers d'addons
   (`addons_path` de `odoo.conf`) ; ne jamais remplacer le répertoire entier.
2. **Redémarrer** le service Odoo.
3. Activer le **mode développeur** (Paramètres → tout en bas → « Activer le
   mode développeur ») : sans lui, le menu suivant n'apparaît pas.
   Apps → **« Mettre à jour la liste des Apps »** → « Mettre à jour ».
4. Apps → retirer le filtre « Apps » de la recherche → chercher **« service
   à table »** → « AITE — Restaurant (service à table) » → **Activer**.
5. Chercher **« POS Analytics »** → « AITE — POS Analytics (LAVERANDAH) »
   (nom hérité du client pilote, voir les notes de version) → **Activer** ;
   puis **« Crédit clients »** → « AITE — Crédit clients (Ardoises POS &
   Ventes) » → **Activer**. La passerelle « AITE — Analyses du restaurant
   par employé » s'installe seule avec « POS Analytics » (sa carte n'a plus
   de bouton « Activer » : rien à faire).
6. **Ctrl+Shift+R** dans le navigateur.

En ligne de commande, c'est équivalent à
`odoo-bin -c <odoo.conf> -d <base> -i pos_restaurant,pos_hr,aite_pos_restaurant,aite_pos_credit,aite_pos_analytics --stop-after-init`.

### 9.4 Ce qui se passe à l'installation (rien à régler)

- Une **caisse « Restaurant »** est créée, prête au premier service : modes
  de paiement **Espèces** (sur le journal d'espèces du plan comptable : la
  société n'a qu'un journal d'espèces ; un journal n'est créé que si celui
  du plan sert déjà une autre caisse) et **Mobile Money** (journal de banque
  du même nom), salle **« Salle »** avec une table, case **« Service à table
  contrôlé »** cochée. Cette case règle d'office la connexion par code
  (« Se connecter avec Employés »), le contrôle des prix (le manager seul les
  change), les remises désactivées, le partage et l'impression de
  l'addition ; elle laisse « Suivi des modifications de commandes » décoché
  (le journal AITE le remplace). Délai avant l'orange : 60 minutes ; vente
  sans table : fermée ; produits épuisés : refusés. Si le plan comptable
  n'est pas encore chargé, la caisse est créée au moment où il l'est.
- **Une caisse créée ensuite** (un bar, par exemple) reçoit d'office ses
  propres **Espèces** (son journal d'espèces, nommé « Espèces Bar ») et
  **Mobile Money**.
- **Base créée en anglais** puis passée au français : le chargement du
  français (Paramètres → Langues) renomme « Espèces » les modes d'espèces
  encore nommés « Cash ».
- **Une caisse qui existait déjà n'est jamais modifiée.** Pour la passer au
  service à table contrôlé : Point de Vente → Configuration → Paramètres →
  choisir la caisse → bloc Restaurant → cocher « Est un bar/restaurant »,
  puis **« Service à table contrôlé »** (caisse fermée ; la phrase sous la
  case dit ce qui va se passer).
- « Caisse fermée » veut dire : **aucune session** de cette caisse, pas même
  une session « Contrôle d'ouverture ». Or, après chaque fermeture, la
  tablette se recharge et Odoo rouvre aussitôt une session en « Contrôle
  d'ouverture », qui grise la case et « Autoriser la vente sans table » (et
  que l'administrateur ne peut pas supprimer) : **régler ces deux cases avant
  d'ouvrir la caisse pour la première fois**. Le délai de l'orange et le
  refus des épuisés se changent à tout moment (ils s'appliquent à la
  réouverture).
- Cinq **motifs d'annulation** (Erreur de saisie, Client parti, Plat refusé,
  Produit manquant, Autre — avec une précision) : Point de Vente →
  Configuration → Motifs d'annulation.
- Les rapports : **Restaurant → Annulations** ; Point de Vente → Analyse →
  **Personnes et tables** et **Détails des ventes** (quantités vendues de
  chaque produit) ; Point de Vente → Analyse → Analyse AITE → Tableau croisé
  & graphique, favori **« Ventes par famille »** ; le rapport de fermeture de
  la caisse donne aussi les tables, les personnes et les annulations.

### 9.5 Ce que règle AITE : les comptes Odoo

Paramètres → Utilisateurs & Sociétés → Utilisateurs → **Nouveau**. Les
employés de salle n'ont **pas** de compte Odoo : ils ont un code (§9.6).

| Compte | Droits à donner | Pourquoi |
|---|---|---|
| **la caisse** (ouvert sur chaque tablette) | Point de Vente : **Utilisateur** ; Comptabilité : **Facturation** ; **un courriel** | Facturation : sans lui, les entrées et sorties d'espèces sont refusées ; le courriel : Odoo publie à son nom à la fermeture. Jamais « Administrateur » : chaque tablette resterait connectée avec ces droits |
| **le manager** | Point de Vente : **Administrateur** ; Employés : **Gestionnaire : Gérer tous les employés** ; Comptabilité : **Facturation** ; POS Analytics AITE : **Manager — Analyses POS** | les niveaux et les codes de la fiche employé ; Facturation : sans lui, Odoo refuse le rapport de session dès qu'une vente est payée ; les analyses AITE |
| **le chef de salle** qui lit les rapports | Restaurant AITE : **Restaurant : lecture des rapports**, rien d'autre | il lit les annulations sans aucun accès à la caisse ni à sa configuration |

Les réglages de la caisse (Point de Vente → Configuration → Paramètres)
sont réservés à l'administrateur d'Odoo (AITE). Dans le bloc Restaurant,
chaque réglage dit sous lui ce qui va se passer : « Délai avant l'orange
(minutes) », « Autoriser la vente sans table » (caisse fermée), « Refuser
la vente des produits épuisés ». Les **imprimantes de cuisine et de bar** se
déclarent dans le même bloc (« Imprimantes de préparation », une par poste,
avec ses familles).

### 9.6 Ce que fait le manager avant le premier service

1. **L'équipe** — Employés → Nouveau : le nom, puis **« Niveau en caisse »**
   (Serveur, Caissière, Chef de salle ou superviseur, Manager) ; le **« Code
   caisse »** (4 chiffres, propre à l'employé) est proposé d'office, sur la
   première page de la fiche. Aucun courriel. Un employé sans niveau
   n'apparaît pas sur la caisse.
2. **La carte** — Point de Vente → Configuration → Produits →
   **Catégories de produits du PdV** : les familles de l'écran de commande,
   sur trois niveaux (par exemple Nourriture > Pizzas ; Boisson >
   Alcoolisé > Bière) ; les mêmes noms en catégories de produit (Inventaire →
   Configuration → Produits → Catégories de produits), que lisent encore le
   tableau de bord AITE et l'onglet « Par catégorie ». Sur chaque produit :
   le prix en FCFA, la case « Point de Vente » (en haut de la fiche), sa
   catégorie dans l'onglet « Point de Vente », et **« Suivre
   l'inventaire »** sur les seules boissons vendues à l'unité (les bières,
   par exemple). **Taxes** : Odoo pose d'office la TVA
   de 19,25 % **hors taxes** (un prix de 1 000 FCFA est encaissé 1 193 FCFA) ;
   pour des prix de carte taxes comprises, AITE règle avec le comptable du
   client une taxe « prix TTC » avant de saisir la carte.
3. **Le plan** — Point de Vente → Configuration → **Plans de salle** →
   « Salle » : les tables, avec leur numéro et leurs places. Le plan ne se
   modifie pas depuis la caisse.
4. **Le stock de départ** — sur la fiche de chaque produit suivi : « Mettre
   la quantité à jour ». Un produit suivi sans stock est refusé à la caisse
   (« Produit épuisé »).

### 9.7 Le premier service

Sur chaque tablette : se connecter avec le **compte de la caisse** → Point
de Vente → « Restaurant » → **Ouvrir la caisse**. La fenêtre du code s'ouvre
d'elle-même : la caissière (ou un chef de salle) tape son code, puis
**« J'ouvre la caisse »**. Le plan reste ensuite affiché, verrouillé :
« Touchez une table, puis tapez votre code. » Le soir, un chef de salle
ferme la caisse (≡ → Fermer la caisse → son code).

### 9.8 Mise à niveau d'une base qui a déjà ces modules

1. Sauvegarder la base et le `filestore` ; **fermer toutes les caisses**.
2. Déposer les nouveaux dossiers à la place des anciens (chaque dossier
   AITE, jamais le répertoire entier), redémarrer.
3. Apps (mode développeur) → « Mettre à jour la liste des Apps » →
   **Mettre à niveau** `aite_pos_restaurant`, `aite_pos_analytics` et
   `aite_pos_credit`.
4. Si « AITE — Analyses du restaurant par employé » n'est pas installé
   (base où les deux modules étaient installés avant son arrivée) : Apps →
   retirer le filtre « Apps » → chercher **« par employé »** → **Activer**.
5. Ctrl+Shift+R sur chaque tablette.

Ne rien désinstaller pour une mise à niveau ; ne jamais retirer des fichiers
avant d'avoir désinstallé proprement le module depuis Apps.

### 9.9 Vérifier

- Point de Vente : la caisse **« Restaurant »**, case « Service à table
  contrôlé » cochée ; ouverte, la caisse demande le code de la caissière,
  puis affiche le plan verrouillé, en couleurs, avec la légende en bas.
- Employés : une fiche à niveau a son code ; un code déjà pris est refusé
  sans dire à qui il est.
- Restaurant → Annulations et Point de Vente → Analyse → Personnes et tables
  s'ouvrent ; vides, ils disent quoi faire.
- Aucun menu Hôtel.

### 9.10 Ce qu'il ne faut pas faire

- Cocher « Suivi des modifications de commandes » : avec des employés sans
  courriel, une baisse de quantité échoue ; le journal AITE suffit.
- Décocher « Se connecter avec Employés » ou « Est un bar/restaurant » sur
  la caisse : c'est refusé tant que « Service à table contrôlé » est coché
  (décocher d'abord la case, caisse fermée).
- Ouvrir la caisse d'une tablette sous un autre compte que celui de la
  caisse : les traces « sans code » seraient alors attribuées à ce compte.

**Environnement de développement** (AITE) : `dev/setup_env.sh --restaurant`
crée la base `aite_resto` de la même façon, avec un jeu de données de
démonstration (12 tables, une carte en trois niveaux, cinq employés,
comptes « caisse », « manager », « chef ») et refuse une base existante qui
n'est pas celle du restaurant (une base hôtelière, par exemple) ;
`dev/run_tests.sh restaurant` la teste, même après un service (les captures,
elles, se prennent sur une copie : voir `tests/restaurant/shots.py`).
**Enterprise** : non essayé à ce jour (aucune base disponible).

---
© AITE Consulting SARL — tous droits réservés.
