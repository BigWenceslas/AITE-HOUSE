# AITE HOUSE — Guide de déploiement (ligne de commande)

**Suite hôtelière AITE HOUSE sur Odoo 18**
AITE Consulting SARL

Ce guide rassemble les commandes d'**installation**, de **mise à jour** et
de **régénération du jeu d'essai**, telles qu'elles s'exécutent sur le
serveur. Il complète [`INSTALLATION.md`](../INSTALLATION.md), qui décrit
la même opération depuis l'interface Odoo.

Toutes les commandes ci-dessous ont été exécutées et vérifiées.

---

## 1. Repères

Les commandes utilisent les chemins de l'instance `odoo18c`. Adaptez-les
si votre installation diffère.

| Repère | Valeur |
|---|---|
| Interpréteur Python | `/opt/odoo18c/venv/bin/python3` |
| `odoo-bin` | `/opt/odoo18c/odoo/odoo-bin` |
| Fichier de configuration | `/opt/odoo18c/conf/odoo18c.conf` |
| Modules personnalisés | `/opt/odoo18c/custom_addons` |
| Base de production | `odoo18c_aite_house` |
| Base de démonstration | `odoo18c_aite_house_data_test` |

### Les options qui reviennent

| Option | Effet |
|---|---|
| `-i` | **Installe** les modules nommés (et leurs dépendances) |
| `-u` | **Met à jour** les modules déjà installés — recharge le code *et* les données XML |
| `--without-demo=all` | N'installe **aucune** donnée de démonstration Odoo. Sur une base de production, c'est obligatoire |
| `--no-http` | Ne démarre pas le serveur web : l'opération est purement batch |
| `--stop-after-init` | Rend la main dès l'opération terminée |
| `--log-level=info` | Affiche le compte rendu de génération du jeu d'essai |

> **Arrêtez le service Odoo** avant toute commande `-i` ou `-u` sur une
> base servie en production : deux processus qui écrivent le même
> registre se gênent.

---

## 2. Déposer ou remplacer les modules

### 2.1 Repérer ce qui est déjà en place

```bash
ls -d /opt/odoo18c/custom_addons/aite_hotel* \
      /opt/odoo18c/custom_addons/aite_slot* \
      /opt/odoo18c/custom_addons/aite_pos* \
      /opt/odoo18c/custom_addons/aite_website* \
      /opt/odoo18c/custom_addons/aite_loyalty* \
      /opt/odoo18c/custom_addons/aite_stock* \
      /opt/odoo18c/custom_addons/aite_purchase* \
      /opt/odoo18c/custom_addons/aite_direction* \
      /opt/odoo18c/custom_addons/aite_exec* \
      /opt/odoo18c/custom_addons/aite_demo* 2>/dev/null
```

Une installation qui a vécu accumule des dossiers hérités que la liste
officielle ne mentionne plus. Ce repérage évite d'en oublier.

### 2.2 Retirer les modules AITE HOUSE

```bash
rm -rf /opt/odoo18c/custom_addons/aite_demo_data \
       /opt/odoo18c/custom_addons/aite_direction_dashboard \
       /opt/odoo18c/custom_addons/aite_exec_dashboard \
       /opt/odoo18c/custom_addons/aite_hotel_gantt \
       /opt/odoo18c/custom_addons/aite_hotel_management \
       /opt/odoo18c/custom_addons/aite_hotel_pos_link \
       /opt/odoo18c/custom_addons/aite_loyalty \
       /opt/odoo18c/custom_addons/aite_pos_analytics \
       /opt/odoo18c/custom_addons/aite_pos_credit \
       /opt/odoo18c/custom_addons/aite_purchase_dashboard \
       /opt/odoo18c/custom_addons/aite_slot_booking \
       /opt/odoo18c/custom_addons/aite_stock_dashboard \
       /opt/odoo18c/custom_addons/aite_website_booking
```

> **Avertissement.** Si ces modules sont **installés dans une base que
> vous conservez**, désinstallez-les d'abord depuis Apps. Retirer les
> fichiers d'un module resté installé casse l'écran Paramètres sur
> `"champ aite_xxx" is undefined`. Pour une base que vous recréez juste
> après, aucun risque.

### 2.3 Déposer la nouvelle version

```bash
cp -r /chemin/vers/AITE_HOUSE/addons/aite_* /opt/odoo18c/custom_addons/
chown -R odoo:odoo /opt/odoo18c/custom_addons/aite_*
```

Déposez les dossiers **à côté** des existants ; ne remplacez jamais le
répertoire `custom_addons` entier.

---

## 3. Installation

### 3.1 Le pays de la société, d'abord

C'est l'étape que l'on saute et qu'on regrette. Odoo choisit le plan
comptable **d'après le pays de la société**. Sans pays renseigné, il
applique le plan *générique* — 51 comptes — et laisse la devise en
**USD**, quel que soit le module de localisation installé.

Avec le pays renseigné, la localisation pose le plan **SYSCOHADA**
(1 143 comptes) **et la devise XAF**, sans autre manipulation.

| Pays renseigné ? | Plan obtenu | Devise |
|---|---|---|
| Non | `generic_coa`, 51 comptes | USD |
| Oui (`CM`) | `cm` — SYSCOHADA, 1 143 comptes | **XAF** |

C'est pourquoi l'installation se fait en **trois passes**.

### 3.2 Base de production — `odoo18c_aite_house`

Base vierge : la suite installée, un seul utilisateur (`admin`), aucune
donnée métier.

```bash
# Passe 1 — créer la base
/opt/odoo18c/venv/bin/python3 /opt/odoo18c/odoo/odoo-bin \
  -c /opt/odoo18c/conf/odoo18c.conf -d odoo18c_aite_house \
  -i base --without-demo=all --no-http --stop-after-init

# Passe 2 — renseigner le pays de la société
echo "env.company.write({'country_id': env['res.country'].search(
    [('code','=','CM')], limit=1).id}); env.cr.commit()" \
| /opt/odoo18c/venv/bin/python3 /opt/odoo18c/odoo/odoo-bin shell \
  -c /opt/odoo18c/conf/odoo18c.conf -d odoo18c_aite_house

# Passe 3 — comptabilité + suite AITE
/opt/odoo18c/venv/bin/python3 /opt/odoo18c/odoo/odoo-bin \
  -c /opt/odoo18c/conf/odoo18c.conf -d odoo18c_aite_house \
  -i l10n_cm,aite_hotel_management,aite_slot_booking,aite_website_booking,\
aite_pos_analytics,aite_pos_credit,aite_hotel_pos_link,aite_loyalty,\
aite_stock_dashboard,aite_purchase_dashboard,aite_direction_dashboard,\
aite_exec_dashboard \
  --without-demo=all --no-http --stop-after-init
```

Résultat vérifié : **11 modules AITE**, devise **XAF**, plan **SYSCOHADA
Cameroun**, `admin` seul utilisateur, aucune donnée métier.

> Hors Cameroun, remplacez `CM` / `l10n_cm` par le pays voulu —
> `GA` / `l10n_ga`, `CI` / `l10n_ci`, `SN` / `l10n_sn`… Toute la zone
> OHADA partage le plan SYSCOHADA. Attention : hors zone CEMAC, la
> devise posée ne sera pas le XAF sur lequel les seuils du produit sont
> calibrés.

### 3.3 Base de démonstration — `odoo18c_aite_house_data_test`

Même socle, plus le jeu d'essai complet.

```bash
# Passe 1 — créer la base
/opt/odoo18c/venv/bin/python3 /opt/odoo18c/odoo/odoo-bin \
  -c /opt/odoo18c/conf/odoo18c.conf -d odoo18c_aite_house_data_test \
  -i base --without-demo=all --no-http --stop-after-init

# Passe 2 — renseigner le pays de la société
echo "env.company.write({'country_id': env['res.country'].search(
    [('code','=','CM')], limit=1).id}); env.cr.commit()" \
| /opt/odoo18c/venv/bin/python3 /opt/odoo18c/odoo/odoo-bin shell \
  -c /opt/odoo18c/conf/odoo18c.conf -d odoo18c_aite_house_data_test

# Passe 3 — comptabilité et modules Odoo standard
/opt/odoo18c/venv/bin/python3 /opt/odoo18c/odoo/odoo-bin \
  -c /opt/odoo18c/conf/odoo18c.conf -d odoo18c_aite_house_data_test \
  -i l10n_cm,point_of_sale,purchase,stock,website \
  --without-demo=all --no-http --stop-after-init

# Passe 4 — suite AITE + jeu d'essai
/opt/odoo18c/venv/bin/python3 /opt/odoo18c/odoo/odoo-bin \
  -c /opt/odoo18c/conf/odoo18c.conf -d odoo18c_aite_house_data_test \
  -i aite_demo_data --no-http --stop-after-init --log-level=info
```

Compte rendu attendu en fin de journal :

```
Jeu d'essai AITE généré (normal) : {'currency': 'XAF', 'users': 5,
 'payment_methods': 2, 'hotel_services': 8, 'season_prices': 8,
 'pos_orders': 168, 'credits': 18, 'roomcharges': 5,
 'housekeeping': 12, 'purchases': 8, 'deposits': 5}
```

### 3.4 Pourquoi séparer la comptabilité du jeu d'essai

Tout installer d'un coup (`-i l10n_cm,aite_demo_data`) **réussit** —
code de sortie 0, aucune erreur — mais produit un jeu d'essai
**incomplet** :

```
WARNING  Jeu d'essai : pas de journal de trésorerie — caisse de
         démonstration non créée.
{'currency': 'XAF', ..., 'pos_orders': 0, 'roomcharges': 0, ...}
```

Le générateur s'exécute **avant** que le plan comptable soit appliqué :
il ne trouve aucun journal de trésorerie, saute la création de la caisse,
et les tableaux de bord Ventes, Analyses et Note de chambre restent
vides. C'est ce qui rend le piège vicieux — rien ne signale l'échec.

Vérifiez toujours `'pos_orders'` dans le compte rendu : **168** en volume
`normal`, **0** si la caisse a été sautée.

Une base déjà dans cet état se rattrape sans la refaire — voir § 5.

---

## 4. Mise à jour

Après avoir remplacé les fichiers (§ 2.3) et **redémarré le service**.

### 4.1 Un seul module

```bash
/opt/odoo18c/venv/bin/python3 /opt/odoo18c/odoo/odoo-bin \
  -c /opt/odoo18c/conf/odoo18c.conf -d odoo18c_aite_house \
  -u aite_hotel_management --no-http --stop-after-init
```

### 4.2 Toute la suite

```bash
/opt/odoo18c/venv/bin/python3 /opt/odoo18c/odoo/odoo-bin \
  -c /opt/odoo18c/conf/odoo18c.conf -d odoo18c_aite_house \
  -u aite_hotel_management,aite_slot_booking,aite_website_booking,\
aite_pos_analytics,aite_pos_credit,aite_hotel_pos_link,aite_loyalty,\
aite_stock_dashboard,aite_purchase_dashboard,aite_direction_dashboard,\
aite_exec_dashboard \
  --no-http --stop-after-init
```

Sur la base de démonstration, ajoutez `,aite_demo_data` à la liste.

### 4.3 Mettre à jour tout ce qui est installé

```bash
/opt/odoo18c/venv/bin/python3 /opt/odoo18c/odoo/odoo-bin \
  -c /opt/odoo18c/conf/odoo18c.conf -d odoo18c_aite_house \
  -u all --no-http --stop-after-init
```

`-u all` met aussi à jour les modules Odoo standard : plus long, et tout
écart dans un module tiers remonte au même moment. À réserver aux
montées de version.

### 4.4 Ajouter un module à une base existante

```bash
/opt/odoo18c/venv/bin/python3 /opt/odoo18c/odoo/odoo-bin \
  -c /opt/odoo18c/conf/odoo18c.conf -d odoo18c_aite_house \
  -i aite_loyalty --no-http --stop-after-init
```

### 4.5 Ce que `-u` recharge, et ce qu'il ne touche pas

`-u` recharge le code **et les fichiers de données XML** du module. Les
enregistrements posés à l'installation sont remis à leur valeur d'origine
— **sauf** ceux marqués `noupdate`, qui sont préservés.

Concrètement : une mise à jour de `aite_demo_data` ne réécrit pas les
données déjà générées, mais peut remettre à jour le référentiel XML
(catalogue, chambres, tarifs). Si vous avez modifié des tarifs de
démonstration à la main, ils seront écrasés.

Après toute mise à jour, **Ctrl+Shift+R** dans le navigateur : les
ressources front-end sont recompilées.

---

## 5. Régénérer ou purger le jeu d'essai

Le jeu est daté **relativement au jour de génération**. Une base de
démonstration qui vieillit sort de la période affichée par les tableaux
de bord : il suffit de la régénérer.

### Depuis l'interface

> Paramètres → **Jeu d'essai AITE** → Générer

C'est aussi le rattrapage d'une base installée en une seule passe
(§ 3.4) : les journaux existent désormais, la caisse et ses 168 ventes
se créent.

### Depuis la ligne de commande

```bash
echo "print(env['aite.demo.generator'].generate_all(scale='normal')); env.cr.commit()" \
| /opt/odoo18c/venv/bin/python3 /opt/odoo18c/odoo/odoo-bin shell \
  -c /opt/odoo18c/conf/odoo18c.conf -d odoo18c_aite_house_data_test
```

Trois volumes : `small`, `normal` (défaut), `large`.

| Volume | Ardoises | Jours de caisse | Ventes / jour |
|---|---:|---:|---:|
| `small` | 6 | 5 | 4 |
| `normal` | 18 | 21 | 8 |
| `large` | 60 | 60 | 14 |

La génération est **idempotente** : la relancer ne duplique rien.

### Purger

```bash
echo "print(env['aite.demo.generator'].purge_generated()); env.cr.commit()" \
| /opt/odoo18c/venv/bin/python3 /opt/odoo18c/odoo/odoo-bin shell \
  -c /opt/odoo18c/conf/odoo18c.conf -d odoo18c_aite_house_data_test
```

La purge **conserve les ventes encaissées** — l'historique de caisse
n'est jamais détruit — ainsi que le référentiel XML posé à
l'installation.

---

## 6. Vérifier après l'opération

```bash
psql -d odoo18c_aite_house_data_test -At -c "
SELECT 'devise ' || (SELECT name FROM res_currency WHERE id = currency_id)
    || ' · plan ' || chart_template FROM res_company;"

psql -d odoo18c_aite_house_data_test -At -c "
SELECT 'modules AITE installés : ' || count(*)
FROM ir_module_module WHERE name LIKE 'aite%' AND state = 'installed';"

psql -d odoo18c_aite_house_data_test -At -c "
SELECT (SELECT count(*) FROM aite_hotel_room)  || ' chambres · '
    || (SELECT count(*) FROM pos_order)        || ' ventes · '
    || (SELECT count(*) FROM aite_pos_credit)  || ' ardoises';"
```

Valeurs attendues sur la base de démonstration :

| Contrôle | Attendu |
|---|---|
| Devise et plan | `devise XAF · plan cm` |
| Modules AITE | **12** (11 sur la base de production, sans `aite_demo_data`) |
| Données | 16 chambres · 168 ventes · 18 ardoises |

Sur Odoo **Enterprise**, comptez **un module de plus** :
`aite_hotel_gantt` s'installe seul et ajoute le planning Gantt.

---

## 7. Dépannage

| Symptôme | Cause | Correction |
|---|---|---|
| `'pos_orders': 0` dans le compte rendu | Générateur exécuté avant le plan comptable | Régénérer le jeu d'essai (§ 5) |
| `Ensure that there is an existing bank journal` | Aucun plan comptable sur la société | Installer la localisation, pays renseigné (§ 3.1) |
| Montants en `$` | Pays de la société non renseigné avant la localisation | § 3.1 ; sur une base déjà écrite, Odoo refuse de changer la devise |
| `"champ aite_xxx" is undefined` | Dossier de module retiré alors que le module reste installé | Redéposer les dossiers, redémarrer, mettre à jour la liste des applications |
| Un module n'apparaît pas dans Apps | `addons_path` ne pointe pas vers `custom_addons` | Vérifier `odoo18c.conf` |
| Écran blanc après mise à jour | Ressources front-end en cache | **Ctrl+Shift+R** ; sur le Point de Vente, fermer et rouvrir la session |
| `aite_hotel_gantt` reste « non installé » | Odoo Community : `web_gantt` n'existe pas | Normal — le planning s'affiche en vue calendrier |
| Tableaux de bord vides | Jeu d'essai daté, sorti de la période | Régénérer (§ 5) |

En cas de blocage, transmettre à AITE Consulting les lignes `ERROR` /
`Traceback` du journal Odoo et le contenu de `addons_path`.

---

© AITE Consulting SARL — tous droits réservés.
