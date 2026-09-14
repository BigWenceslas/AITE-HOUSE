# AITE — POS Analytics (LAVERANDAH)

Module Odoo 18 Enterprise d'analyse avancée pour le Point of Sale.

## Objectif

Apporter au gérant et à l'équipe de management un dashboard fin sur :

- Chiffre d'affaires, marge brute, CMV
- Analyse par article, par catégorie, par session
- Détection et classification des écarts de caisse
- Évolution mensuelle CA / CMV / marge

Compatible **Odoo 18.0 Enterprise**, testé sur **Ubuntu 22.04 / 24.04**.

## Architecture

| Composant | Rôle |
|---|---|
| `models/pos_order_line.py` | Snapshot du coût + calcul marge ligne (stored) |
| `models/pos_order.py` | Agrégats marge / CMV par commande (stored) |
| `models/pos_session.py` | Agrégats session + sévérité écart caisse (stored) |
| `models/pos_analytics_report.py` | Vue SQL pour pivot / graph / dashboard |
| `views/*.xml` | Extensions de vues + vues du rapport |
| `security/*` | Groupes utilisateur / manager + ACL |

## Installation

```bash
# Copier le module dans le addons-path
sudo cp -r aite_pos_analytics /opt/odoo/custom-addons/

# Restart Odoo
sudo systemctl restart odoo

# Mettre à jour la liste des modules dans Odoo puis installer
```

Le **post-init hook** `_init_pos_margin_data` rétro-peuple le champ
`cost_unit` sur les lignes POS existantes en utilisant le `standard_price`
courant des produits. Pour les bases avec beaucoup d'historique POS
(>50k lignes), prévoir une fenêtre de maintenance pour l'installation.

## Recompute manuel après import de coûts

Si vous modifiez en masse les `standard_price` après installation et
voulez **resyncer** les marges historiques sur les nouveaux coûts :

```python
# Dans le shell Odoo (CAUTION: écrase les snapshots historiques)
lines = env['pos.order.line'].search([])
for line in lines:
    line.cost_unit = line.product_id.standard_price
env.cr.commit()
```

À utiliser avec parcimonie : par design, le snapshot du coût à la vente
garantit la stabilité des marges historiques.

## Sprint 2 — livré

- Dashboard OWL (action client `aite_pos_analytics.dashboard`)
- Composants : KPI cards, FilterBar, Top 8 articles, classements, table détaillée
- Chart.js intégré pour Top 8 CA/Marge et évolution mensuelle
- Panneau détail article (slide-over)

## Sprint 3 — analyse multi-caisses & temporelle (nouveau)

Ajouts à la version `18.0.2.0.0` :

- **Filtre par caisse** : la barre de filtre permet de cibler une caisse
  précise (`pos.config`) ou toutes les caisses.
- **Filtre par plage horaire** : raccourcis (matin / après-midi / soir /
  nuit) + plage personnalisée. Gère le passage minuit (ex. 22h→2h).
- **Filtre par jour de semaine** : sélection individuelle (lun→dim) et
  raccourcis « semaine » / « week-ends ».
- **Onglet « Par caisse »** : tableau comparatif complet (CA, marge,
  taux, CMV, panier moyen, qté, écart de caisse) avec ligne de total —
  répond au besoin « marge totale ET par caisse sur une période ».
- **Comparaison vs période précédente** : variations CA / marge / CMV /
  commandes affichées sur le dashboard (période N-1 de même durée).
- **Heatmap heure × jour** : intensité = CA, pour caler les plannings et
  les happy hours, avec insights (meilleur créneau, jour le plus fort).

### Note technique — fuseau horaire du filtre heure

Le filtre par heure et la heatmap convertissent `pos_order.date_order`
(stocké en UTC) vers le fuseau de l'utilisateur courant
(`self.env.user.tz`, repli `UTC`) avant d'extraire l'heure et le jour. Les
créneaux (« soir 18–23h ») correspondent donc à l'heure **locale**
d'exploitation. Le fuseau est figé à l'installation/mise à jour du module :
si le fuseau du parc change, relancer une mise à jour du module pour
recréer la vue SQL.

## Auteur

AITE CONSULTING — Yaoundé, Cameroun
