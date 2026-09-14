# AITE HOUSE — Suite de gestion hôtelière sur Odoo 18
**Version du paquet : septembre 2026 · 12 modules · Odoo 18 (Community & Enterprise)**

Éditeur : AITE Consulting SARL — Douala, Makepe Bloc F
info@aite-consulting.com · (+237) 673 373 367 / 656 801 098 · https://aite-consulting.com

---

## 1. Contenu

```
AITE_HOUSE/
├── addons/            les 12 modules à déposer sur le serveur
├── documentation/     guides utilisateur, fiches produit, plaquette, flyer
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
| aite_demo_data | 18.0.1.2.1 | Jeu de démonstration (établissement complet pré-chargé) |

## 3. Prérequis

- Odoo 18 (Community ou Enterprise), PostgreSQL, accès au serveur.
- Modules Odoo standard requis (installés automatiquement) : `point_of_sale`,
  `sale`, `account`, `purchase`, `stock`, `website`, `portal`, `mail`,
  `product`, `web`, `web_gantt`.
- Devise de la société en FCFA (XAF) ou GNF selon le pays.

## 4. Installation

1. **Déposer** les 12 dossiers de `addons/` dans le répertoire des addons
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
| `"champ aite_xxx" is undefined` sur Paramètres | Dossier(s) de module absent(s) du serveur alors que le module reste installé en base | Redéposer les 12 dossiers, redémarrer, mettre à jour la liste des applications |
| Un module n'apparaît pas dans Apps | `addons_path` ne pointe pas vers le répertoire utilisé | Vérifier `odoo.conf` et la commande de lancement du service |
| Écran blanc ou composant manquant | Cache navigateur | Ctrl+Shift+R ; sur le Point de Vente, fermer et rouvrir la session |
| Erreur à l'installation | Dépendance Odoo absente | Installer d'abord le module standard concerné (voir §3) |

En cas de blocage, transmettre à AITE Consulting les lignes `ERROR` /
`Traceback` du log Odoo et le contenu de `addons_path`.

## 8. Documentation fournie

- **Guides utilisateur** (PDF illustrés) : Note de chambre, Réservation en
  ligne, Fidélité, Espaces & prestations, Tableau de bord Direction.
- **Fiches produit** : POS Analytics, POS Crédit.
- **Plaquette commerciale** AITE HOUSE (19 pages) et **flyer**.

---
© AITE Consulting SARL — tous droits réservés.
