# AITE HOUSE — Cahier de recette (UAT)

**Suite hôtelière AITE HOUSE sur Odoo 18 — recette applicative**
Généré le 2026-09-15 11:23 · instance recettée : `http://127.0.0.1:8069`

---

## Comment lire ce cahier

Chaque scénario correspond à **un poste de travail** et se joue avec le
profil utilisateur de ce poste — pas avec un compte administrateur. Les
captures d'écran sont celles obtenues lors de l'exécution : ce que le
document montre est ce que l'utilisateur voit.

Pour chaque étape :

| Colonne | Contenu |
|---|---|
| **Action** | Le geste effectué, dans l'ordre |
| **Attendu** | Le comportement exigé par la spécification |
| **Constaté** | Ce que l'écran a réellement produit |
| **Verdict** | ✅ conforme · ❌ écart |

### Comptes de recette

Les profils sont créés par le module `aite_demo_data`. Le mot de passe
est identique à l'identifiant (**base de démonstration uniquement**).

| Poste | Identifiant | Périmètre |
|---|---|---|
| Réception | `demo.reception` | Réservations, folios, encaissements, check-in / check-out |
| Gouvernante | `demo.gouvernante` | Tâches de ménage et états de chambre |
| Caisse | `demo.caisse` | Point de vente, ardoises, remboursements |
| Magasin | `demo.magasin` | Stock, inventaires, alertes |
| Direction | `demo.direction` | Tous les tableaux de bord, configuration |

### Rejouer la recette

```bash
python tests_uat/run_uat.py --url http://mon-serveur:8069
python tests_uat/build_guide.py
```

---

## Synthèse

| Scénario | Poste | Étapes | Verdict |
|---|---|---|---|
| [La journée de la réception](#1-la-journée-de-la-réception) | Réception (Awa Diallo) | 7 | ✅ Conforme |
| [Le tour des chambres](#2-le-tour-des-chambres) | Gouvernante (Fanta Souaré) | 5 | ✅ Conforme |
| [Ardoises clients et recouvrement](#3-ardoises-clients-et-recouvrement) | Caisse (Ibrahima Sylla) | 7 | ✅ Conforme |
| [Le cockpit de la direction](#4-le-cockpit-de-la-direction) | Direction (Aminata Bah) | 7 | ✅ Conforme |
| [La réservation en ligne](#5-la-réservation-en-ligne) | Client (visiteur du site) | 6 | ✅ Conforme |
| [Stock, ruptures et réapprovisionnement](#6-stock,-ruptures-et-réapprovisionnement) | Magasin (Moussa Camara) | 2 | ✅ Conforme |

**Total : 34 étapes — 0 écart(s) constaté(s).**

---

## 1. La journée de la réception

> **Poste :** Réception (Awa Diallo)
> **Objectif :** Prendre connaissance de la journée, retrouver une réservation, ouvrir un folio et encaisser un acompte.
> **Verdict global :** ✅ Conforme


### 1. Ouvrir le Front Desk

| | |
|---|---|
| **Attendu** | Le tableau de bord affiche l'occupation du jour, les arrivées, les départs et le room board. |
| **Constaté** | Occupation, arrivées, départs et room board sont affichés. |
| **Verdict** | ✅ Conforme |

![Ouvrir le Front Desk](captures/r1-front-desk-01-ouvrir-le-front-desk.png)


### 2. Consulter les arrivées du jour

| | |
|---|---|
| **Attendu** | La liste ne montre que les réservations confirmées arrivant aujourd'hui. |
| **Constaté** | La liste des arrivées du jour s'affiche. |
| **Verdict** | ✅ Conforme |

![Consulter les arrivées du jour](captures/r1-front-desk-02-consulter-les-arrivees-du-jour.png)


### 3. Ouvrir le planning des chambres

| | |
|---|---|
| **Attendu** | Le planning s'affiche — calendrier sur Community, Gantt sur Enterprise — avec les séjours de la période. |
| **Constaté** | Le planning s'ouvre et présente les séjours. |
| **Verdict** | ✅ Conforme |

![Ouvrir le planning des chambres](captures/r1-front-desk-03-ouvrir-le-planning-des-chambres.png)


### 4. Lister les réservations

| | |
|---|---|
| **Attendu** | La liste des réservations du séjour s'affiche. |
| **Constaté** | La liste des réservations du séjour s'affiche. |
| **Verdict** | ✅ Conforme |

![Lister les réservations](captures/r1-front-desk-04-lister-les-reservations.png)


### 5. Ouvrir une réservation

| | |
|---|---|
| **Attendu** | La fiche montre le client, les chambres, le folio et les boutons du workflow. |
| **Constaté** | La fiche réservation s'ouvre avec son folio. |
| **Verdict** | ✅ Conforme |

![Ouvrir une réservation](captures/r1-front-desk-05-ouvrir-une-reservation.png)


### 6. Consulter les folios

| | |
|---|---|
| **Attendu** | Les notes de séjour listent hébergement, services et solde dû. |
| **Constaté** | Les folios s'affichent avec leur solde. |
| **Verdict** | ✅ Conforme |

![Consulter les folios](captures/r1-front-desk-06-consulter-les-folios.png)


### 7. Ouvrir la réservation rapide

| | |
|---|---|
| **Attendu** | L'assistant propose dates, occupation et recherche de disponibilité. |
| **Constaté** | L'assistant de réservation rapide s'ouvre. |
| **Verdict** | ✅ Conforme |

![Ouvrir la réservation rapide](captures/r1-front-desk-07-ouvrir-la-reservation-rapide.png)


---

## 2. Le tour des chambres

> **Poste :** Gouvernante (Fanta Souaré)
> **Objectif :** Prendre ses tâches du jour, démarrer une recouche, la terminer et voir l'état des chambres changer.
> **Verdict global :** ✅ Conforme


### 1. Ouvrir les tâches de gouvernante

| | |
|---|---|
| **Attendu** | Les tâches du jour s'affichent, groupées par état. |
| **Constaté** | Les tâches de ménage du jour sont listées. |
| **Verdict** | ✅ Conforme |

![Ouvrir les tâches de gouvernante](captures/r2-gouvernante-01-ouvrir-les-taches-de-gouvernante.png)


### 2. Démarrer une recouche depuis le kanban

| | |
|---|---|
| **Attendu** | La carte bascule dans la colonne « En cours » et la chambre passe en « Nettoyage en cours ». |
| **Constaté** | La tâche est démarrée : elle quitte la colonne « À faire ». |
| **Verdict** | ✅ Conforme |

![Démarrer une recouche depuis le kanban](captures/r2-gouvernante-02-demarrer-une-recouche-depuis-le-kanban.png)


### 3. Terminer la tâche

| | |
|---|---|
| **Attendu** | La tâche passe « Terminé » et la chambre redevient propre (ou « à inspecter » si l'inspection est exigée). |
| **Constaté** | La tâche est clôturée, la chambre est rendue au service. |
| **Verdict** | ✅ Conforme |

![Terminer la tâche](captures/r2-gouvernante-03-terminer-la-tache.png)


### 4. Consulter les chambres

| | |
|---|---|
| **Attendu** | La gouvernante voit l'état de chaque chambre, mais ni le tarif spécifique ni le tarif du jour : ces données relèvent de la Réception. |
| **Constaté** | Les chambres s'affichent sans aucune donnée tarifaire. |
| **Verdict** | ✅ Conforme |

![Consulter les chambres](captures/r2-gouvernante-04-consulter-les-chambres.png)


### 5. Tenter d'ouvrir les folios

| | |
|---|---|
| **Attendu** | Le profil Gouvernante n'a pas accès aux notes de séjour : Odoo doit afficher un refus nommant le modèle concerné. |
| **Constaté** | L'accès aux folios est refusé, avec le motif affiché. |
| **Verdict** | ✅ Conforme |

![Tenter d'ouvrir les folios](captures/r2-gouvernante-05-tenter-d-ouvrir-les-folios.png)


---

## 3. Ardoises clients et recouvrement

> **Poste :** Caisse (Ibrahima Sylla)
> **Objectif :** Suivre l'encours, ouvrir une ardoise, enregistrer un remboursement et vérifier le solde.
> **Verdict global :** ✅ Conforme


### 1. Ouvrir le tableau de bord Recouvrement

| | |
|---|---|
| **Attendu** | Encours total, balance âgée et top débiteurs sont affichés. |
| **Constaté** | Le tableau de bord du recouvrement s'affiche. |
| **Verdict** | ✅ Conforme |

![Ouvrir le tableau de bord Recouvrement](captures/r3-ardoises-01-ouvrir-le-tableau-de-bord-recouvrement.png)


### 2. Lister les ardoises

| | |
|---|---|
| **Attendu** | Les ardoises s'affichent avec client, montant, reste dû et ancienneté. |
| **Constaté** | Les ardoises sont listées avec leur reste dû. |
| **Verdict** | ✅ Conforme |

![Lister les ardoises](captures/r3-ardoises-02-lister-les-ardoises.png)


### 3. Filtrer les ardoises ouvertes

| | |
|---|---|
| **Attendu** | Seules les ardoises encore dues restent affichées. |
| **Constaté** | Seules les ardoises encore dues restent affichées. |
| **Verdict** | ✅ Conforme |

![Filtrer les ardoises ouvertes](captures/r3-ardoises-03-filtrer-les-ardoises-ouvertes.png)


### 4. Ouvrir une ardoise

| | |
|---|---|
| **Attendu** | La fiche montre le reste dû et le bouton « Enregistrer un remboursement ». |
| **Constaté** | La fiche montre le reste dû et le bouton « Enregistrer un remboursement ». |
| **Verdict** | ✅ Conforme |

![Ouvrir une ardoise](captures/r3-ardoises-04-ouvrir-une-ardoise.png)


### 5. Assistant de remboursement

| | |
|---|---|
| **Attendu** | Le montant est pré-rempli avec le reste dû et le moyen de paiement est proposé. |
| **Constaté** | Le montant est pré-rempli avec le reste dû et le moyen de paiement est proposé. |
| **Verdict** | ✅ Conforme |

![Assistant de remboursement](captures/r3-ardoises-05-assistant-de-remboursement.png)


### 6. Enregistrer le remboursement

| | |
|---|---|
| **Attendu** | Le reste dû tombe à zéro et l'ardoise passe « Réglée ». |
| **Constaté** | Le remboursement est enregistré : l'ardoise est soldée. |
| **Verdict** | ✅ Conforme |

![Enregistrer le remboursement](captures/r3-ardoises-06-enregistrer-le-remboursement.png)


### 7. Tenter d'ouvrir les réservations hôtel

| | |
|---|---|
| **Attendu** | Le profil Caisse n'a pas de droits hôteliers : Odoo doit afficher un refus nommant le modèle concerné. |
| **Constaté** | L'accès au PMS est refusé, avec le motif affiché. |
| **Verdict** | ✅ Conforme |

![Tenter d'ouvrir les réservations hôtel](captures/r3-ardoises-07-tenter-d-ouvrir-les-reservations-hotel.png)


---

## 4. Le cockpit de la direction

> **Poste :** Direction (Aminata Bah)
> **Objectif :** Consulter les tableaux de bord consolidés et vérifier que les chiffres concordent entre les vues.
> **Verdict global :** ✅ Conforme


### 1. Ouvrir — Ventes (POS Analytics)

| | |
|---|---|
| **Attendu** | Chiffre d'affaires, marge, CMV et panier moyen sont affichés. |
| **Constaté** | Le tableau de bord s'affiche et présente ses indicateurs. |
| **Verdict** | ✅ Conforme |

![Ouvrir — Ventes (POS Analytics)](captures/r4-direction-01-ouvrir-ventes-pos-analytics.png)


### 2. Ouvrir — Recouvrement (Crédit clients)

| | |
|---|---|
| **Attendu** | Encours, balance âgée et débiteurs à relancer sont affichés. |
| **Constaté** | Le tableau de bord s'affiche et présente ses indicateurs. |
| **Verdict** | ✅ Conforme |

![Ouvrir — Recouvrement (Crédit clients)](captures/r4-direction-02-ouvrir-recouvrement-credit-clients.png)


### 3. Ouvrir — Stock & Inventaire

| | |
|---|---|
| **Attendu** | Valorisation, ruptures, couverture et alertes sont affichées. |
| **Constaté** | Le tableau de bord s'affiche et présente ses indicateurs. |
| **Verdict** | ✅ Conforme |

![Ouvrir — Stock & Inventaire](captures/r4-direction-03-ouvrir-stock-inventaire.png)


### 4. Ouvrir — Achats & Fournisseurs

| | |
|---|---|
| **Attendu** | Échéancier fournisseurs et évolution des prix sont affichés. |
| **Constaté** | Le tableau de bord s'affiche et présente ses indicateurs. |
| **Verdict** | ✅ Conforme |

![Ouvrir — Achats & Fournisseurs](captures/r4-direction-04-ouvrir-achats-fournisseurs.png)


### 5. Ouvrir — Espaces & Prestations

| | |
|---|---|
| **Attendu** | Taux d'occupation des espaces et planning du jour s'affichent. |
| **Constaté** | Le tableau de bord s'affiche et présente ses indicateurs. |
| **Verdict** | ✅ Conforme |

![Ouvrir — Espaces & Prestations](captures/r4-direction-05-ouvrir-espaces-prestations.png)


### 6. Ouvrir — Cockpit Direction

| | |
|---|---|
| **Attendu** | La vue consolidée reprend les quatre pôles et la balance âgée en miroir. |
| **Constaté** | Le tableau de bord s'affiche et présente ses indicateurs. |
| **Verdict** | ✅ Conforme |

![Ouvrir — Cockpit Direction](captures/r4-direction-06-ouvrir-cockpit-direction.png)


### 7. Ouvrir — Tableau de bord exécutif

| | |
|---|---|
| **Attendu** | Hébergement, restauration et prestations sont consolidés. |
| **Constaté** | Le tableau de bord s'affiche et présente ses indicateurs. |
| **Verdict** | ✅ Conforme |

![Ouvrir — Tableau de bord exécutif](captures/r4-direction-07-ouvrir-tableau-de-bord-executif.png)


---

## 5. La réservation en ligne

> **Poste :** Client (visiteur du site)
> **Objectif :** Réserver un espace depuis le site public, sans compte, et recevoir la confirmation.
> **Verdict global :** ✅ Conforme


### 1. Ouvrir la page de réservation

| | |
|---|---|
| **Attendu** | La page publique s'affiche sans authentification. |
| **Constaté** | La page de réservation est accessible au public. |
| **Verdict** | ✅ Conforme |

![Ouvrir la page de réservation](captures/r5-site-web-01-ouvrir-la-page-de-reservation.png)


### 2. Choisir un espace

| | |
|---|---|
| **Attendu** | Les espaces réservables en ligne sont listés ; ceux réservés au comptoir n'apparaissent pas. |
| **Constaté** | La liste des espaces réservables s'affiche. |
| **Verdict** | ✅ Conforme |

![Choisir un espace](captures/r5-site-web-02-choisir-un-espace.png)


### 3. Voir les créneaux libres

| | |
|---|---|
| **Attendu** | La grille du jour montre les créneaux encore disponibles. |
| **Constaté** | La grille du jour montre les créneaux encore disponibles. |
| **Verdict** | ✅ Conforme |

![Voir les créneaux libres](captures/r5-site-web-03-voir-les-creneaux-libres.png)


### 4. Choisir un créneau et se présenter

| | |
|---|---|
| **Attendu** | Un créneau est coché et les coordonnées sont saisies ; le formulaire est prêt à partir. |
| **Constaté** | Créneau sélectionné, coordonnées renseignées. |
| **Verdict** | ✅ Conforme |

![Choisir un créneau et se présenter](captures/r5-site-web-04-choisir-un-creneau-et-se-presenter.png)


### 5. Valider la réservation

| | |
|---|---|
| **Attendu** | La page de remerciement affiche la référence de la réservation, preuve de son enregistrement côté back-office. |
| **Constaté** | La réservation est confirmée et sa référence s'affiche. |
| **Verdict** | ✅ Conforme |

![Valider la réservation](captures/r5-site-web-05-valider-la-reservation.png)


### 6. Demander un séjour

| | |
|---|---|
| **Attendu** | Le formulaire de demande de chambre s'affiche (dates, occupation, coordonnées). |
| **Constaté** | Le formulaire de demande de séjour s'affiche. |
| **Verdict** | ✅ Conforme |

![Demander un séjour](captures/r5-site-web-06-demander-un-sejour.png)


---

## 6. Stock, ruptures et réapprovisionnement

> **Poste :** Magasin (Moussa Camara)
> **Objectif :** Repérer les ruptures et les articles sous seuil, et consulter la valorisation du stock.
> **Verdict global :** ✅ Conforme


### 1. Ouvrir le tableau de bord Stock

| | |
|---|---|
| **Attendu** | Valorisation, nombre de références, ruptures et couverture moyenne sont affichés. |
| **Constaté** | Le tableau de bord Stock s'affiche avec ses indicateurs. |
| **Verdict** | ✅ Conforme |

![Ouvrir le tableau de bord Stock](captures/r6-magasin-01-ouvrir-le-tableau-de-bord-stock.png)


### 2. Tenter d'ouvrir les ardoises clients

| | |
|---|---|
| **Attendu** | Le profil Magasin n'a pas de droits sur le crédit clients : Odoo doit afficher un refus nommant le modèle concerné. |
| **Constaté** | L'accès au crédit clients est refusé, avec le motif affiché. |
| **Verdict** | ✅ Conforme |

![Tenter d'ouvrir les ardoises clients](captures/r6-magasin-02-tenter-d-ouvrir-les-ardoises-clients.png)


---

_Cahier produit automatiquement par `tests_uat/build_guide.py` à partir de l'exécution réelle des scénarios._
