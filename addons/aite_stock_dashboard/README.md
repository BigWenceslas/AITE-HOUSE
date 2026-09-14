# AITE — Stock & Inventaire (Tableau de bord)

Tableau de bord OWL pour Odoo 18 Inventaire, pensé pour le commerce de
détail (bar, cave, restauration). Dépend uniquement de **Stock** — aucun
module POS requis.

## Accès

Menu **Inventaire → Tableau de bord AITE** (groupe *Utilisateur* de
l'inventaire). Réservé aux *Responsables* : le bouton **⚙ Configurer les
alertes** et le bloc de Réglages.

## Onglets

| Onglet | Contenu |
|---|---|
| **Tableau de bord** | Valeur du stock (coût), couverture moyenne, ruptures & critiques, coulage vs seuil ; rotation, dormants, valeur à commander, écart net ; 4 graphiques (valeur/catégorie, entrées vs sorties 6 mois, couverture/catégorie, top valeur). |
| **Alertes & réappro** | Références triées par urgence : Rupture → Critique → Sous seuil, avec point de commande et quantité suggérée. |
| **Stock complet** | Toutes les références, quantités **par emplacement interne**, valeur (barres proportionnelles), couverture, statut ; recherche. |
| **Rotation & dormants** | Classes Rapide / Normale / Lente / Dormant, top rotation, valeur dormante. |
| **Inventaires & écarts** | Journal des ajustements d'inventaire et des casses (signés, valorisés), écarts par catégorie, **coulage mensuel vs seuil**. |
| **Mouvements** | Réceptions, ventes, transferts, ajustements, casse, retours — avec totaux. |

## Alertes configurables

**Globaux** (Réglages → AITE Stock, ou modal ⚙) : stock de sécurité,
horizon de commande, seuil critique, seuil dormant, délai réappro par
défaut, seuil de coulage.

**Par produit** (fiche article, onglet *Réappro AITE*, ou modal ⚙) :
délai de réappro (0 = défaut société), seuil manuel (0 = automatique),
alerte active/inactive.

### Formules

```
point de commande  = ventes moy./jour × (délai réappro + sécurité)
quantité suggérée  = ventes moy./jour × (délai + horizon) − stock
```

Les **ventes moyennes/jour** sont calculées sur **30 jours glissants**
(mouvements faits vers un emplacement *client*) : les alertes restent
stables quelle que soit la période affichée. La période sélectionnée
s'applique aux flux : entrées/sorties, écarts, casse, coulage, CA estimé.

Le **coulage** = |écarts d'inventaire négatifs| + casse, rapporté au **CA
estimé** (quantités livrées × prix de vente) — étiqueté comme estimation.

## Robustesse (leçons de production AITE)

* Aucune fonction globale JS dans les templates OWL — tout le formatage
  passe par des méthodes du composant.
* `read_group` uniquement sur des champs stockés (`stock.quant.quantity`,
  quantités de mouvements) ; le reste est sommé en Python.
* Détection à l'exécution du champ « quantité faite » des mouvements
  (`quantity` / `quantity_done` / repli) — résiste aux renommages entre
  versions.
* Menu unique dans l'app Inventaire native (pas de menu racine fragile) ;
  ancrages de vues volontairement génériques (`//form`, `//notebook`).
* Un seul appel `get_stock_list` alimente Alertes, Stock complet, Rotation
  et 4 graphiques : cohérence garantie entre les vues.

## Tests

* `test_stock_logic.py` — **exécute le code réel** de `_metrics` (extrait
  du module) : 21 tests (statuts, seuils, arrondis, config).
* `test_stock_integration.py` — 24 tests des règles d'agrégation
  (ventes/jour, quants par emplacement, signature des écarts, typage des
  mouvements, coulage, tris, totaux).
