# AITE — Crédit clients (Ardoises POS & Ventes)

Vente à crédit « ardoise » pour Odoo 18 — depuis le **Point de Vente** et,
depuis la v2.0.0, depuis le **module Ventes** : les deux canaux alimentent
la même ardoise, le même circuit de remboursement (espèces / MTN MoMo /
Orange Money) et le même tableau de bord de recouvrement.

## Nouveau en v18.0.2.0.0 — Ardoises depuis les Ventes

* **Devis / commande de vente** : onglet *Ardoise AITE* → cochez « Mettre
  sur ardoise à la confirmation » (acompte comptant optionnel, déduit du
  montant). Bouton « Mettre sur ardoise » en rattrapage sur une commande
  déjà confirmée, et bouton intelligent vers l'ardoise liée.
* **Ardoise** : champ *Origine* (Point de vente / Ventes), lien vers la
  commande de vente ; filtres et regroupement par origine dans la liste.
* **Tableau de bord** : filtre *Origine* (Toutes / Point de vente /
  Ventes) propagé à tous les KPI, graphiques et journaux ; le donut
  devient « Encours par origine » avec une part dédiée « Ventes (hors
  POS) » ; la carte Encours affiche la répartition POS / Ventes quand les
  deux canaux coexistent.
* Note : combiner le filtre d'une **caisse** avec l'origine **Ventes**
  donne logiquement un résultat vide (les ventes hors POS n'ont pas de
  caisse).

**Mise à niveau depuis la 1.x** : remplacez le dossier puis Apps →
*Mettre à jour* — ne désinstallez jamais le module (cela supprimerait les
ardoises). Les ardoises existantes sont automatiquement marquées d'origine
« Point de vente ». La dépendance au module *Ventes* (sale) est ajoutée et
s'installe automatiquement si absente.

Module Odoo 18 de **vente à crédit (ardoise)** pour le Point de Vente, pensé
pour le commerce de détail (bar, cave, restauration) en contexte camerounais
(FCFA, Mobile Money).

## Principe

Un client connu consomme au POS et **paie plus tard**. La vente crée une
*ardoise* (dette client). Le client rembourse ensuite, partiellement ou
totalement, en **Mobile Money** (MTN MoMo / Orange Money) ou en **espèces**.

> Cette version ne pose **pas de limite de crédit** : le caissier peut
> toujours mettre une vente sur ardoise. La limite/blocage et les relances
> automatiques sont prévues en évolution (sprint 2).

## Fonctionnalités

- **Mise sur ardoise** d'une commande POS, avec acompte optionnel.
- **Encours par client** (`res.partner.credit_outstanding`) + bouton
  intelligent « Ardoises » en fiche client.
- **Remboursements** multi-moyens (MTN, Orange, espèces, carte, virement)
  avec référence de transaction, encaisseur et historique.
- **Tableau de bord recouvrement** (OWL) :
  - encours total dû, débiteurs actifs, recouvré (période), taux de
    recouvrement ;
  - indicateurs de risque (ardoise moyenne, plus ancienne dette, montant en
    retard +30 j, nouvelles ardoises) ;
  - **balance âgée** (0-30 / 30-60 / 60-90 / +90 jours) ;
  - répartition des remboursements par moyen de paiement ;
  - évolution nouvelles ardoises vs recouvré (6 mois) ;
  - **top débiteurs** cliquables.

## Modèles

| Modèle | Rôle |
|--------|------|
| `aite.pos.credit` | L'ardoise (dette née d'une commande POS). |
| `aite.pos.credit.payment` | Un remboursement réduisant le reste dû (+ écriture 411). |
| `aite.pos.credit.dashboard` | Fournisseur de données du tableau de bord. |
| `aite.pos.credit.repay.wizard` | Assistant d'encaissement d'un remboursement. |

Extensions : `res.partner` (encours), `pos.order` (mise sur ardoise +
hook automatique), `pos.payment.method` (marqueur « ardoise »),
`res.company` / `res.config.settings` (paramètres comptables).

## Intégration POS (bouton réel)

Le module ajoute un bouton **« Mettre sur ardoise »** directement dans
l'écran de paiement du POS. Techniquement, il s'appuie sur une **méthode de
paiement native de type *pay_later*** (créée automatiquement à l'installation
via le `post_init_hook`, et marquée `is_aite_credit`). Le bouton :

1. exige qu'un client soit sélectionné (sinon ouvre la sélection client) ;
2. impute le solde dû sur la méthode « ardoise » ;
3. valide la commande.

### Paiement mixte (comptant + ardoise)

Un client peut **régler une partie immédiatement** (espèces, carte, Mobile
Money…) et **porter le reste sur ardoise**. Dans l'écran de paiement, on
ajoute simplement plusieurs lignes : par exemple 30 000 en espèces puis
20 000 sur « Ardoise / Crédit ». Le module ne met sur ardoise **que la part
réglée via la méthode ardoise** — ici 20 000, pas le total de 50 000. La
commande est soldée au POS, et l'ardoise reflète exactement le crédit
accordé. La fiche de l'ardoise affiche le total commande et la part payée
comptant pour la traçabilité.

À la synchronisation de la commande, `pos.order` détecte le paiement crédit
et crée l'ardoise (`_aite_create_credit_if_needed`). Aucune réécriture du
flux de paiement POS : on orchestre les briques natives, ce qui reste
robuste entre versions.

## Intégration comptable (OHADA / compte 411)

- **Mise sur ardoise** : le mécanisme *pay_later* d'Odoo porte le montant de
  la vente au **compte client (411)** — l'encours est donc comptable dès
  l'origine.
- **Remboursement** : si l'option *« Comptabiliser les remboursements »* est
  activée (Réglages POS), la validation d'un remboursement passe une écriture
  **débit trésorerie (512/521/571) / crédit client (411)**, puis tente de
  **rapprocher** la ligne 411 avec la créance de la commande POS d'origine.
- Le **compte 411** et le **journal d'encaissement** sont paramétrables par
  société ; à défaut, le module utilise le compte client de la fiche
  partenaire et un journal de caisse/banque.

Tout est défensif : sans configuration comptable, le suivi d'ardoise reste
applicatif et n'interrompt jamais une vente.

## Sévérité d'une ardoise

Basée sur l'ancienneté (`age_days`) :

- **Récente** : < 30 j
- **En retard** : ≥ 30 j
- **Critique** : ≥ 60 j
- **Réglée** : ardoise soldée ou annulée

Seuils surchargeables (`AGE_THRESHOLD_LATE`, `AGE_THRESHOLD_CRITICAL`).

## Dépendances

`base`, `product`, `point_of_sale`, `account`.

## Installation

1. Copier `aite_pos_credit` dans le dossier addons.
2. Mettre à jour la liste des apps, installer **AITE — POS Crédit**.
3. Donner aux utilisateurs les droits *POS Crédit / Utilisateur* ou
   *Responsable*.

## Notes d'intégration comptable

L'ardoise est conçue pour s'adosser à la **comptabilité client (compte 411
OHADA)** : une vente à crédit correspond à une créance client, un
remboursement à un encaissement partiel. Le branchement comptable fin
(génération d'écritures) est à activer selon le plan comptable de la société.

## Tests

- `test_credit_logic.py` — 17 tests de logique pure (reste dû, sévérité,
  aging, plafond de remboursement, inversion de recherche sur l'âge).
- `test_credit_integration.py` — 24 tests : logique du tableau de bord (KPI,
  aging, répartition paiements, encours client) **et** intégration comptable
  (équilibre débit/crédit de l'écriture 411, choix du compte de trésorerie
  par moyen de paiement, détection de la part « à crédit » d'une commande).

---

© AITE Consulting — Licence LGPL-3.
