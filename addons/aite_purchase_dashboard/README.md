# AITE — Achats & Fournisseurs (Tableau de bord)

Tableau de bord OWL pour Odoo 18 Achats : piloter la relation fournisseurs
dans les deux sens — les **dettes (401)** et les **créances (409)**.

## Accès

Menu **Achats → Tableau de bord AITE** (groupe *Utilisateur* des achats).
Registre des consignes : **Achats → Configuration → Consignes fournisseurs**.
Réservé aux *Responsables Achats* : bouton **⚙** et bloc de Réglages.

## Onglets

| Onglet | Contenu |
|---|---|
| **Tableau de bord** | Achats de la période, dette 401, échéances sous N jours, DPO ; retards, créances 409, OTIF, commandes en cours ; achats/fournisseur, factures vs paiements 6 mois, balance âgée, top produits. |
| **Fournisseurs** | Achats, part (concentration), encours dû, retards, délai moyen, OTIF, badge Dépendance/Retards/OK. |
| **Dettes & échéancier** | Balance âgée 5 tranches (non échu / 1-30 / 31-60 / 61-90 / +90 j de retard), décaissements sur 6 semaines, factures triées par urgence. |
| **Avoirs & consignes** | Consignes d'emballages (registre dédié — 4096), avoirs ouverts (4097/4098), acomptes estimés (4091). |
| **Commandes & réceptions** | Journal des commandes, retards, réceptions complètes/incomplètes, OTIF strict. |
| **Prix & variations** | Δ prix récent vs ~6 mois, impact annuel, indice base 100 des produits clés. |

## Alertes configurables

Réglages → **AITE Achats**, ou modal **⚙** : fenêtre d'alerte avant
échéance (7 j), tolérance de retard de livraison (2 j), seuil de
dépendance fournisseur (40 %), seuil de hausse de prix (5 %).

## Définitions & sources de données

* **OTIF strict** : reçue à l'heure ET complète — un badge toléré distinct
  absorbe les petits retards sous le seuil (mais ne compte pas OTIF).
* **DPO** = encours 401 / factures fournisseurs de la période × jours.
* **Dettes** : `account.move` (in_invoice) comptabilisées non soldées,
  échéance `invoice_date_due` ; balance âgée par jours de retard.
* **Créances 409** : consignes = registre `aite.purchase.deposit`
  (saisie manuelle assumée — le comptage des casiers fait foi) ; avoirs =
  in_refund ouverts ; acomptes = soldes **débiteurs** du compte
  fournisseurs (paiements non lettrés) moins avoirs — estimation
  documentée.
* **Réceptions** : `receipt_status` natif si présent, sinon repli sur les
  quantités reçues des lignes (détection défensive).
* **Prix** : lignes d'achat — fenêtre récente (45 j) vs ancienne
  (120-210 j) ; nécessite un historique d'achats dans Odoo.

## Robustesse (pipeline AITE)

Aucun global JS dans les templates OWL ; une source de vérité (les
factures ouvertes alimentent tableau, balance âgée ET échéancier) ;
`read_group` sur champs stockés uniquement ; menus dans l'app Achats
native avec actions explicites ; ancrage Réglages générique (`//form`).

## Tests

* `test_purchase_logic.py` — **exécute le code réel** des 6 fonctions
  pures extraites du module : 25 tests (buckets, statuts, OTIF strict vs
  badge toléré, prix, dépendance, DPO).
* `test_purchase_integration.py` — 18 tests d'agrégation (tranches,
  échéancier, 409, flux mensuels, détection défensive, indice base 100).
