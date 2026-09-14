# AITE HOUSE — Suite de gestion hôtelière sur Odoo 18
**Version du paquet : septembre 2026 · 13 modules · Odoo 18 (Community & Enterprise)**

Éditeur : AITE Consulting SARL — Douala, Makepe Bloc F
info@aite-consulting.com · (+237) 673 373 367 / 656 801 098 · https://aite-consulting.com

---

## 1. Contenu

```
AITE_HOUSE/
├── addons/            les 13 modules à déposer sur le serveur
├── documentation/     guides utilisateur, fiches produit, plaquette, flyer,
│                      guide de test, cahier de recette et captures
├── tests_uat/         scénarios de recette (navigateur)
└── INSTALLATION.md    ce fichier
```

## 2. Les modules

| Module | Version | Rôle |
|---|---|---|
| aite_hotel_management | 18.0.1.0.2 | **Socle hôtelier** : chambres, réservations, séjours, folios, main courante, facturation |
| aite_slot_booking | 18.0.1.0.2 | Espaces & prestations réservables au créneau (salles, piscine, billard…) |
| aite_website_booking | 18.0.1.0.0 | Réservation en ligne depuis le site web, acompte |
| aite_hotel_pos_link | 18.0.1.0.0 | **Note de chambre** : report des consommations du bar sur le folio |
| aite_pos_credit | 18.0.2.0.2 | Crédit clients (ardoises) : plafonds, encours, recouvrement |
| aite_loyalty | 18.0.1.0.0 | Fidélité : points, niveaux VIP & VVIP |
| aite_pos_analytics | 18.0.2.1.0 | Analyses des ventes : heures de pointe, marges, CMV |
| aite_stock_dashboard | 18.0.1.1.2 | Stock : ruptures, coulage, couverture, inventaires |
| aite_purchase_dashboard | 18.0.1.0.2 | Achats : échéancier fournisseurs, OTIF, hausses de prix |
| aite_direction_dashboard | 18.0.1.0.2 | **Cockpit Direction** : vue consolidée, cash à risque, actions |
| aite_exec_dashboard | 18.0.1.0.2 | Tableau de bord exécutif hôtel |
| aite_hotel_gantt | 18.0.1.0.0 | **Enterprise uniquement** : planning Gantt des chambres (auto-installé) |
| aite_demo_data | 18.0.1.2.1 | Jeu de démonstration (établissement complet pré-chargé) |

## 3. Prérequis

- Odoo 18 (Community ou Enterprise), PostgreSQL, accès au serveur.
- Modules Odoo standard requis (installés automatiquement) : `point_of_sale`,
  `sale`, `account`, `purchase`, `stock`, `website`, `portal`, `mail`,
  `product`, `web`.
- **Un plan comptable installé sur la société** avant d'installer le Point
  de Vente ou le jeu de démonstration : Odoo exige un journal de banque
  pour créer une caisse. Sur une base neuve, installez le module de
  localisation comptable de votre pays (Comptabilité → Configuration), ou
  créez la base avec les données de démonstration Odoo.
- **Devise de la société en GNF ou FCFA (XAF)** selon le pays, à
  positionner **avant** toute écriture comptable — Odoo refuse ensuite
  d'en changer.

### Community ou Enterprise ?

La suite s'installe sur les **deux éditions**. Le seul écart est le
planning des chambres :

- sur **Community**, il s'affiche en vue **calendrier** ;
- sur **Enterprise**, le module `aite_hotel_gantt` s'installe
  automatiquement et le planning s'ouvre en vue **Gantt** (barres par
  chambre). Aucune action n'est requise.

## 4. Installation

1. **Déposer** les 13 dossiers de `addons/` dans le répertoire des addons
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
   7. `aite_demo_data` *(uniquement sur une base de démonstration)*

   Sur Enterprise, `aite_hotel_gantt` s'ajoute seul à l'étape 1 : il ne
   figure pas dans cette liste et ne demande aucune manipulation.
5. **Ctrl+Shift+R** dans le navigateur (les assets sont recompilés).
6. Vérifier : l'écran **Paramètres** doit s'afficher jusqu'en bas, avec les
   sections AITE (Note de chambre, Fidélité, Crédit, Réservations…).

## 5. Mise à jour d'une installation existante

Remplacer le dossier du module concerné, redémarrer le service, puis
Apps → **« Mettre à niveau »** sur ce module. Ne jamais retirer des
fichiers avant d'avoir désinstallé proprement le module depuis Apps.

## 6. Désinstallation

Désinstaller **depuis Apps** avant toute suppression de fichiers, dans
l'ordre inverse : `aite_demo_data` en premier, `aite_hotel_management` en
dernier.

## 7. Dépannage

| Symptôme | Cause probable | Correction |
|---|---|---|
| `"champ aite_xxx" is undefined` sur Paramètres | Dossier(s) de module absent(s) du serveur alors que le module reste installé en base | Redéposer les 13 dossiers, redémarrer, mettre à jour la liste des applications |
| Un module n'apparaît pas dans Apps | `addons_path` ne pointe pas vers le répertoire utilisé | Vérifier `odoo.conf` et la commande de lancement du service |
| Écran blanc ou composant manquant | Cache navigateur | Ctrl+Shift+R ; sur le Point de Vente, fermer et rouvrir la session |
| Erreur à l'installation | Dépendance Odoo absente | Installer d'abord le module standard concerné (voir §3) |
| `Ensure that there is an existing bank journal` | Aucun plan comptable sur la société | Installer le module de localisation comptable du pays, puis relancer l'installation (voir §3) |
| `aite_hotel_gantt` reste « non installé » | Odoo Community : `web_gantt` n'existe pas | Comportement normal — le planning s'affiche en vue calendrier |
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

- **[`GUIDE_TESTS.md`](documentation/GUIDE_TESTS.md)** — monter un
  environnement de test, exécuter les 572 tests automatisés, régénérer le
  jeu d'essai.
- **[`GUIDE_RECETTE_UAT.md`](documentation/GUIDE_RECETTE_UAT.md)** —
  cahier de recette illustré : 6 scénarios, 32 étapes, une capture
  d'écran par étape, joués avec les profils métier réels.
- **[`RAPPORT_TESTS.md`](documentation/RAPPORT_TESTS.md)** — rapport de
  campagne : anomalies trouvées, corrections apportées, points
  d'attention.
- `documentation/captures/` — les captures d'écran de la recette.

---
© AITE Consulting SARL — tous droits réservés.
