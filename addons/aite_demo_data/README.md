# AITE — Jeu d'essai de démonstration

**À installer uniquement sur la base de DÉMONSTRATION.** La désinstallation
retire l'ensemble du jeu d'essai.

> **Prérequis :** un **plan comptable** installé sur la société. Odoo
> exige un journal de banque pour créer une caisse ; à défaut, le volet
> Point de Vente est ignoré avec un avertissement et le reste du jeu
> s'installe normalement.
>
> **Devise :** le jeu est calibré en **GNF**. Positionnez la devise de la
> société *avant* toute écriture comptable — Odoo refuse d'en changer
> ensuite.

## Deux étages

Le module se compose d'un **référentiel** (fichiers XML, posé à
l'installation) et d'un **jeu opérationnel** produit par le générateur
`aite.demo.generator`, daté **relativement au jour d'installation**.

Le générateur se relance depuis l'interface —
Paramètres → **Jeu d'essai AITE** — en trois volumes (*léger*,
*standard*, *étendu*), avec purge optionnelle. Il est **idempotent** :
le relancer ne duplique rien.

### Ce que produit le générateur (volume « standard »)

| Domaine | Volume |
|---|---|
| Commandes en caisse | 168, sur 21 sessions closes (pics midi / soir, écarts de caisse) |
| Ardoises clients | 18, de 3 à 160 jours, dont 9 partiellement remboursées |
| Notes de chambre en attente | 5, couvrant les trois motifs d'ambiguïté |
| Tâches de gouvernante | 12, tous types, à différents stades |
| Services hôteliers | 8 (restaurant, minibar, blanchisserie, transferts…) |
| Tarifs saisonniers | 2 par type de chambre |
| Commandes d'achat | 8, confirmées et en demande de prix |
| Consignes fournisseurs | 5 |
| Profils utilisateurs | 5 postes métier (mot de passe = identifiant) |

Les profils `demo.reception`, `demo.gouvernante`, `demo.caisse`,
`demo.magasin` et `demo.direction` servent aux démonstrations et à la
recette applicative.

> La purge **conserve l'historique de caisse** : une vente encaissée
> porte des écritures comptables et des mouvements de stock, qu'Odoo
> interdit de supprimer.

## Contenu (1069 enregistrements)
| Domaine | Nombre |
|---|---|
| Catégories (internes + caisse) | 43 |
| Produits (restaurant, boutique, prestations) | 144 |
| Clients (dont profils VIP / VVIP calibrés) | 40 |
| Ressources à créneaux | 13 |
| Prestations | 22 |
| Réservations (6 sem. passées + sem. à venir) | 333 |
| Mouvements de fidélité | 474 |

## Points d'attention
- Les dates sont **relatives à l'installation** : le planning du jour et les
  périodes « semaine / mois » sont peuplés quel que soit le jour de la démo.
- Les statuts VIP / VVIP posés sur les fiches sont **reproduits par le
  moteur** : le recalcul nocturne aboutit aux mêmes statuts (données
  calibrées au-dessus des seuils par construction).
- Prix en GNF (contexte Guinée). Aucune taxe n'est posée sur les produits :
  le paramétrage fiscal reste celui de l'atelier dédié.
- Les commandes en caisse sont désormais fournies par le générateur (elles
  exigent des sessions, que le générateur ouvre et clôture). Créer deux ou
  trois ventes en direct pendant la démonstration reste le meilleur
  exercice : elles alimentent la rotation du stock et la fidélité.

## Volet hôtelier (v1.1)
| Domaine | Nombre |
|---|---|
| Hôtel, étages, types, chambres, produits folio | 27 |
| Séjours (réservations + lignes chambre) | 188 × 2 |
| Folios et lignes (nuitées datées, services) | 602 |

La « photo du jour » est garantie quel que soit le jour d'installation :
séjours en cours, arrivées attendues et départ du jour sont pilotés en
relatif. Les KPI ADR / RevPAR / CA se calculent sur les lignes de folio
« nuitée » datées, ventilées par type via la ligne de réservation —
exactement les chemins que lit le tableau de bord.

## Volet boutique (v1.2)
63 articles stockables mis en stock (emplacement principal),
20 seuils d'alerte posés — dont 3 ruptures et
6 articles sous seuil visibles immédiatement dans le
tableau de bord Stock (double valorisation comprise). 5
fournisseurs et une caisse « Boutique (démo) » (affectez vos moyens de
paiement avant d'ouvrir une session). La rotation et les classes de
vitesse s'animent après les premières ventes passées en caisse pendant
la démo — elles exigent un historique de mouvements réels.
