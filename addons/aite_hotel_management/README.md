# Gestion Hôtelière (aite_hotel_management)

Module complet de gestion hôtelière (PMS — Property Management System)
pour **Odoo 18 Enterprise**, développé par **AITE CONSULTING**.

Il couvre le cycle de vie complet d'un séjour : réservation, check-in,
folio (compte client), consommation de services, encaissements
(Mobile Money inclus), facturation, check-out et ménage — avec un
tableau de bord Front Desk temps réel (Occupation, ADR, RevPAR, room
board interactif).

---

## 1. Fonctionnalités

### Front Desk
- **Tableau de bord temps réel** : photo du jour (occupation, arrivées,
  départs, clients présents), KPIs de période (taux d'occupation, ADR,
  RevPAR, chiffre d'affaires) avec variation vs période précédente,
  graphiques d'évolution, room board interactif et résumé gouvernante.
- **Réservation rapide** : assistant de recherche de disponibilités par
  dates / type / capacité, avec prix calculés (saisons comprises) et
  création de la réservation en un clic.
- **Vues opérationnelles** : arrivées du jour, départs du jour, clients
  présents (in-house).

### Réservations
- Workflow complet : Brouillon → Confirmée → Arrivé (check-in) → Parti
  (check-out), avec annulation et no-show (manuel ou automatique).
- Multi-chambres sur une même réservation, contrôle de disponibilité
  (chevauchements) et de capacité (adultes / enfants).
- Prix par nuit calculé automatiquement : prix spécifique chambre >
  tarif saisonnier > prix de base du type ; supplément personne
  supplémentaire.
- Canal de vente (direct, téléphone, e-mail, walk-in, agence, en ligne)
  et **commission d'agence** (pourcentage ou montant fixe).
- **Changement de chambre en cours de séjour** (bouton sur chaque ligne
  de chambre) avec option « surclassement gracieux » conservant le
  tarif d'origine.
- E-mail de confirmation automatique (modèle fourni, activable dans la
  configuration).
- **Planning Gantt** des chambres (vue Enterprise) + calendrier.
- Changement de chambre en cours de séjour (`action_change_room` sur la
  ligne de réservation).

### Folios & encaissements
- **Folio** créé automatiquement à la confirmation : nuitées
  synchronisées tant que non facturé, ajout libre de services
  (restaurant, blanchisserie, navette, minibar, spa…).
- **Encaissements multi-moyens** : espèces, **MTN Mobile Money**,
  **Orange Money**, carte bancaire, virement — avec référence de
  transaction obligatoire pour le Mobile Money.
- Acomptes possibles dès la confirmation (assistant d'encaissement).
- Écritures comptables automatiques (journal par méthode, contrepartie
  client 411 — plan OHADA) si la configuration comptable est complète ;
  lettrage automatique avec la facture (best-effort).
- Facturation client au check-out (ou manuelle), solde et statut de
  paiement suivis sur le folio.

### Gouvernante (housekeeping)
- États de chambre : Propre / À nettoyer / Ménage en cours / À
  contrôler, avec inspection optionnelle par la gouvernante.
- **Tâches de ménage** (kanban) : ménage de départ créé automatiquement
  au check-out, ménage quotidien des chambres occupées (cron
  optionnel), inspections et maintenance.
- Room rack kanban par étage avec actions de ménage directes ; chambres
  **hors service** (réservation bloquée) avec motif.

### Configuration & sécurité
- Multi-hôtels et multi-sociétés (règles d'enregistrement fournies).
- 3 groupes : **Gouvernante** (lecture + ménage), **Réception**
  (opérations courantes), **Manager** (configuration, annulations,
  check-in anticipé, hors service).
- Paramètres : compte client par défaut, journal d'encaissement,
  écritures automatiques, e-mail de confirmation, no-show automatique
  (avec délai de grâce), ménage quotidien automatique, inspection
  obligatoire.
- Rapports PDF : confirmation de réservation et folio détaillé.

---

## 2. Dépendances

| Module      | Usage                                    |
|-------------|------------------------------------------|
| `base`      | Socle                                     |
| `mail`      | Chatter, activités, e-mail de confirmation |
| `product`   | Articles liés aux types de chambre / services |
| `account`   | Factures clients, écritures d'encaissement |
| `sale`      | Paramétrage commercial de base            |
| `web_gantt` | Planning des chambres (**Odoo Enterprise**) |

> Le module vise **Odoo 18 Enterprise**. Pour une édition Community,
> retirer `web_gantt` des dépendances et la vue `gantt` du fichier
> `views/hotel_reservation_views.xml`.

## 3. Installation

1. Copier le dossier `aite_hotel_management` dans votre répertoire
   d'addons.
2. Redémarrer le serveur Odoo puis mettre à jour la liste des
   applications (mode développeur → *Mettre à jour la liste des Apps*).
3. Installer **Gestion Hôtelière** depuis le menu Applications.
4. (Optionnel) Charger les données de démonstration pour découvrir le
   module avec l'« Hôtel La Vérandah » (8 chambres, 3 types, services,
   clients).

## 4. Premiers pas

1. **Créer l'hôtel** : Gestion Hôtelière → Configuration → Hôtels
   (horaires check-in/check-out, étages, politique).
2. **Types de chambre** : prix de base, supplément personne, capacités,
   aménités, tarifs saisonniers.
3. **Chambres** : numéro, étage, type (prix spécifique possible).
4. **Services** : prestations facturables sur folio.
5. **Paramètres** (Configuration → Paramètres → Gestion Hôtelière) :
   comptabilité des règlements et automatisations.
6. Vérifier les **droits** des utilisateurs (Réception / Gouvernante /
   Manager) dans Paramètres → Utilisateurs.

## 5. Cycle d'un séjour (workflow type)

1. **Réserver** : menu *Réservation rapide* (recherche de dispo) ou
   création directe d'une réservation. → **Confirmer** : le folio est
   créé, l'e-mail de confirmation part (si activé).
2. **Acompte** (optionnel) : bouton *Encaisser un acompte*.
3. **Check-in** le jour d'arrivée (bouton *Check-in* ; anticipé réservé
   au manager). Les chambres passent « Occupées ».
4. **Pendant le séjour** : ajouter des services sur le folio ;
   encaisser à tout moment.
5. **Check-out** : bouton *Check-out* → assistant (départ anticipé
   recalculé, solde affiché, facture générée en option). Une tâche de
   ménage « départ » est créée pour chaque chambre.
6. **Gouvernante** : démarre puis termine le ménage (inspection si
   configurée) ; la chambre redevient « Propre ».
7. **Facturation / règlements** : depuis le folio (facture, paiements,
   lettrage automatique).

## 6. Indicateurs (définitions)

- **Taux d'occupation** = nuitées vendues / nuitées disponibles
  (chambres vendables × jours), hors chambres hors service.
- **ADR** (Average Daily Rate) = CA hébergement HT / nuitées vendues.
- **RevPAR** = CA hébergement HT / nuitées disponibles.
- Les variations affichées comparent la période sélectionnée à la
  période précédente de même durée (N-1).

## 7. Structure technique

```
aite_hotel_management/
├── __manifest__.py
├── data/            séquences, aménités, e-mail, cron quotidien
├── demo/            hôtel de démonstration complet
├── models/          hôtel, chambres, réservations, folios,
│                    gouvernante, dashboard (RPC), partenaires, config
├── wizard/          réservation rapide, check-out, encaissement,
│                    changement de chambre
├── security/        groupes, ACL, règles multi-sociétés
├── views/           toutes les vues + menus + action dashboard
├── report/          PDF confirmation & folio (QWeb)
└── static/src/      dashboard OWL (JS/XML/SCSS), icône
```

Modèles principaux : `aite.hotel.hotel`, `aite.hotel.floor`,
`aite.hotel.room.type`, `aite.hotel.room`, `aite.hotel.amenity`,
`aite.hotel.season.price`, `aite.hotel.service`,
`aite.hotel.reservation(.line)`, `aite.hotel.folio(.line/.payment)`,
`aite.hotel.housekeeping`, `aite.hotel.dashboard` (AbstractModel RPC).

## 8. Notes & limites connues

- Les **écritures comptables** d'encaissement ne sont générées que si
  le journal (ou un journal par défaut de la société) et le compte
  client sont configurés ; sinon le règlement est enregistré sans
  écriture (message dans le chatter du folio).
- La conversion des heures d'arrivée/départ utilise le **fuseau de
  l'utilisateur** ; vérifiez que le fuseau des utilisateurs de la
  réception est correct (ex. Africa/Douala).

## 9. Licence & auteur

- Licence : **LGPL-3**
- Auteur : **AITE CONSULTING** — Yaoundé, Cameroun
- Version : 18.0.1.0.0
