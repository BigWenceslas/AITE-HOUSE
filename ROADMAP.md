# AITE HOUSE — Roadmap produit & état d'avancement

**Date : 11 octobre 2026 · Odoo 18 · AITE Consulting**
Référence : étude comparative AITE HOUSE vs marché (10 oct. 2026) — 63 fonctionnalités évaluées, 26 fonctionnalités proposées en 3 vagues.

---

## 1. En un coup d'œil

| | |
|---|---|
| **Modules livrables** | **16** = 12 modules du socle (sept. 2026) + `aite_hotel_gantt` (passerelle Enterprise) + 3 modules de la vague 1 (oct. 2026) — ≈ 50 000 lignes |
| **Vague 1 (9 fonctionnalités)** | **5 terminées** (F01 à F04, F06) · **1 partielle** (F07 : briques déjà dans le socle) · **3 à faire** (F05, F08, F09) |
| **Vague 2 (8)** | 2 partielles faites en avance (F14 statistiques, F16 objets trouvés) · 6 à faire |
| **Vague 3 (9)** | 1 partielle (F19 checklists d'inspection) · 8 à faire |
| **Grille marché (63 critères)** | avant la vague 1 : 18 couverts / 16 partiels / 29 absents → **aujourd'hui : 26 couverts / 18 partiels / 19 absents** |
| **Qualité** | 613 tests Odoo (`addons/*/tests`) + 143 vérifications de parcours « utilisateur novice » + 28 tests purs, sur Odoo 18 réel ; 33 écrans audités (0 erreur, chaque état vide explique quoi faire) ; cahier de recette : 146 cas, 17 domaines |

Légende des statuts : ✅ **Fait** (livré et testé) · 🟡 **Partiel** (une partie existe, le reste est décrit) · ⬜ **À faire**

---

## 2. Les modules livrés

| # | Module | Version | Rôle | Fichiers | État |
|---|---|---|---|---|---|
| 1 | `aite_hotel_management` | **18.0.1.0.7** | **Socle PMS** : hôtels, étages, chambres, types, équipements, réservations multi-chambres, check-in/out, folios (lignes hébergement/services, paiements, facture unique), main courante, tarifs saisonniers, commissions d'agents, planning Gantt, ménage de base, tableau de bord, cron quotidien (no-show, ménage) | 51 | ✅ corrigé le 11/10 |
| 2 | `aite_slot_booking` | **18.0.1.0.5** | Espaces & prestations au créneau (salles VIP/VVIP, SPA, coiffure, pressing), conflits, no-show, report au folio | 25 | ✅ |
| 3 | `aite_website_booking` | **18.0.1.0.2** | Réservation en ligne (site web) : espaces, prestations, demandes de séjour, acompte | 8 | ✅ |
| 4 | `aite_hotel_pos_link` | **18.0.1.0.2** | **Note de chambre** : moyen de paiement POS → folio du séjour, file de rattachement | 13 | ✅ |
| 5 | `aite_pos_credit` | **18.0.2.0.5** | Crédit clients (ardoises) POS + Ventes : encours et sévérité par âge (pas de plafond par client), remboursements, écritures 411, recouvrement | 38 | ✅ |
| 6 | `aite_loyalty` | **18.0.1.0.3** | Fidélité unifiée : points, historisation, statut Standard/VIP/VVIP automatique | 16 | ✅ |
| 7 | `aite_pos_analytics` | **18.0.2.1.4** | Analyses ventes POS : CA, marge, CMV, écarts de caisse, heures de pointe, produits | 36 | ✅ |
| 8 | `aite_stock_dashboard` | **18.0.1.1.3** | Stock : valorisation, couverture, ruptures, rotation, coulage, inventaires, dépôts | 19 | ✅ |
| 9 | `aite_purchase_dashboard` | **18.0.1.0.5** | Achats : dettes 401 / balance âgée / échéancier, créances 409, OTIF, hausses de prix | 19 | ✅ |
| 10 | `aite_direction_dashboard` | **18.0.1.1.2** | **Cockpit Direction** consolidé : POS + crédit + stock + achats + **hébergement (TO, ADR, RevPAR, N-1)**, cash à risque, actions | 9 | ✅ |
| 11 | `aite_exec_dashboard` | **18.0.1.1.2** | Tableau de bord exécutif du complexe : hébergement (CA, **TO, ADR, RevPAR, pickup, pace, écarts N-1**), POS, prestations, fidélité | 14 | ✅ |
| 12 | `aite_demo_data` | **18.0.1.2.4** | Jeu de démonstration complet (base de démo uniquement) | 17 | ✅ |
| 13 | `aite_city_tax` | **18.0.1.0.2** | **Taxe de séjour** automatique (barèmes CM/CI/SN/GN par étoiles), ligne auto sur folio hors TVA, état mensuel | 16 | ✅ **nouveau** |
| 14 | `aite_guest_registry` | **18.0.1.0.3** | **Registre des clients** : fiche d'enregistrement au check-in, registre de police, statistiques d'hébergement | 20 | ✅ **nouveau** |
| 15 | `aite_housekeeping` | **18.0.1.0.6** | **Gouvernante & maintenance** : tableau des chambres, « Ma journée » mobile, répartition, inspections, pannes → app Maintenance, hors service auto, objets trouvés | 21 | ✅ **nouveau** |

Dépendances Odoo standard : `point_of_sale`, `sale`, `account`, `purchase`, `stock`, `website`, `portal`, `mail`, `product`, `web`, `maintenance` (Community) et `web_gantt` (**Enterprise**, module passerelle `aite_hotel_gantt` uniquement, auto-installé : le socle s'installe tel quel sur Community, planning en calendrier).

### Correctif du socle livré le 11/10 (18.0.1.0.2 → 18.0.1.0.3)
Défauts trouvés par les tests « novice » :
- l'administrateur n'avait **aucun droit hôtel** après installation (erreur d'accès au premier clic) → profil Responsable attribué à `base.user_admin`, impliqué par `base.group_system` ;
- un utilisateur créé avec le seul profil « Gouvernante » **n'était pas interne** (rien ne s'ouvrait) → les groupes hôtel impliquent `base.group_user` ;
- le **room rack était vide à l'écran** (kanban groupé par étage, colonne « Aucun » repliée) → remplacé par le tableau des chambres de `aite_housekeeping`, menu francisé « Chambres (liste) » ;
- écrans Front Desk / Règlements **muets quand vides** → aides ajoutées.

---

## 3. Suivi des 26 fonctionnalités

### Vague 1 — socle du marché (0-3 mois)

| ID | Fonctionnalité | Statut | Module | Ce qui est fait | Ce qui reste |
|---|---|---|---|---|---|
| **F01** | Housekeeping : statut chambres, affectation, vue mobile | ✅ Fait | `aite_housekeeping` | Tableau des chambres par état (À nettoyer → En cours → À inspecter → Propre) avec phrase d'écran par carte, un bouton par étape ; « Ma journée » mobile (Je commence / C'est fait / Passer la checklist) ; répartition tour de rôle entre équipières ; inspection avec checklist 8 points (non conforme → retour en nettoyage, urgent, même équipière) ; durée mesurée ; colonnes dans l'ordre du travail (18.0.1.0.1). 40/40 vérifications. | — |
| **F02** | Maintenance : ordres de travail liés aux chambres, chambre HS retirée de la vente | ✅ Fait | `aite_housekeeping` (fusionné avec F01, pas de module `aite_hotel_maintenance` séparé) + app **Maintenance** (CE) | « Signaler un problème » depuis la chambre → `maintenance.request` (room_id, hotel_id, blocks_room) ; chambre hors service si demande bloquante ouverte et chambre non occupée ; **remise en vente automatique** + tâche « Remise en service » quand la réparation est terminée ; compteur de pannes sur la carte. | Préventif : utiliser les équipements de l'app Maintenance standard (climatiseurs, groupe) — pas de surcouche prévue. |
| **F03** | Fiche d'enregistrement + registre de police + photo de la pièce + export | ✅ Fait | `aite_guest_registry` | Fiche créée au check-in, pré-remplie depuis le contact ; bandeau « x fiche(s) à compléter » + bouton « Fiches clients x/y » ; liste éditable avec colonne « Il manque » ; photo de la pièce (`id_image`) ; fiche PDF signable ; **registre de police** A4 paysage sur période ; mémorisation de la pièce sur le contact. 35/35 vérifications. | Format officiel DGSN/MINTOUL à confirmer ; e-signature (Odoo Sign, EE) en option. |
| **F04** | Taxe de séjour automatique + état mensuel | ✅ Fait | `aite_city_tax` | 24 barèmes CM/CI/SN/GN (data `noupdate`) ; ligne « Taxe de séjour » ajoutée au folio à la confirmation, recalculée (dates, chambres, occupants, étoiles), figée après facture, hors TVA, exclue de « Services » ; onglet hôtel avec phrase « ce qui sera facturé » ; état mensuel pivot (vue SQL). 35/35 vérifications + 14 tests unitaires. | Articles CGI exacts et clé de répartition 80/20 à confirmer avant usage externe (barèmes modifiables sans code). |
| **F05** | Clôture journalière (night audit) | ⬜ À faire | `aite_hotel_management` (ou `aite_night_audit`) | Point d'accroche existant : cron `_cron_daily_tasks` (no-show, ménage) dans le socle. | Voir §4 — nuitées postées, rapport du jour, contrôles bloquants, verrouillage de la date. |
| **F06** | RevPAR / ADR / TO / pace / pickup | ✅ Fait | `aite_hotel_management` (fournisseur) + `aite_exec_dashboard` + `aite_direction_dashboard` | Fournisseur du PMS : **pickup** (nuitées prises ces 7 j pour les 30 prochains), **pace** (mois en cours vs même date N-1), **même période N-1** et écarts ; CA hébergement calculé **nuit par nuit** depuis les séjours. Tableau exécutif : rangée TO / ADR / RevPAR / pickup / pace, écart N-1 en couleur, une phrase d'explication par indicateur (« ? »). Cockpit Direction : rangée Hébergement (mêmes chiffres, mêmes phrases, clic → tableau exécutif). 33/33 vérifications + 14 tests purs + tests Odoo. | Vue SQL `aite.hotel.kpi.daily` non nécessaire (calcul direct, à reconsidérer au-delà de ~200 chambres). |
| **F07** | Saisons, packages, restrictions, tarifs sociétés/agences | 🟡 Partiel | `aite_hotel_management` | **Tarifs saisonniers** par type de chambre et plage de dates (`aite.hotel.season.price`, priorité hôtel > tous hôtels, prix le plus bas) ; **commissions d'agents** sur la réservation (`agent_id`, taux/montant). | Restrictions (séjour minimum, stop-sell, fermé à l'arrivée), packages pension (PDJ / demi-pension / complète = services auto), tarifs négociés par société/agence. Voir §4. |
| **F08** | Groupes & allotements | ⬜ À faire | `aite_hotel_management` (ou `aite_hotel_groups`) | — | Blocks par type/dates, rooming list importable, dates de release + cron, facture maître. Voir §4. |
| **F09** | Multi-folios & routage des charges | ⬜ À faire | `aite_hotel_management` | Un folio par séjour ; la note de chambre POS sait rattacher au folio ouvert. | Plusieurs folios par réservation (chambre / société / événement), règles de routage, split de facture. À faire **après F08**. Voir §4. |

### Vague 2 — différenciateurs locaux (3-6 mois)

| ID | Fonctionnalité | Statut | Module proposé | Notes |
|---|---|---|---|---|
| F10 | Mobile Money intégré (MTN MoMo, Orange Money via Smobilpay/Maviance) : acompte web, lien de paiement, folio, POS, réconciliation | ⬜ À faire | `aite_momo_payments` | Aujourd'hui : MoMo saisi comme moyen de paiement manuel (folio, POS, ardoises). Passerelle Smobilpay gratuite en CE. |
| F11 | WhatsApp : confirmation, pré-arrivée, facture, relance d'ardoise, avis | ⬜ À faire | `aite_guest_messaging` | EE : WhatsApp natif ; CE : connecteur API Meta. |
| F12 | Pré-check-in en ligne (lien J-2) + check-out express | ⬜ À faire | `aite_online_checkin` | S'appuie sur `aite.guest.registration` (F03) : le client remplit sa fiche depuis le portail. |
| F13 | Channel manager / OTA via connecteur (Channex, WuBook, Beds24) | ⬜ À faire | `aite_channel_connector` | Effort L ; prérequis : F07 (plans tarifaires, restrictions) et F08 (allotements). |
| F14 | Statistiques MINTOUL mensuelles | 🟡 Partiel (fait en avance) | `aite_guest_registry` | Livré : vue « Statistiques d'hébergement » (arrivées, nuitées, résidents / non-résidents, nationalités, motifs). Reste : TO et durée moyenne de séjour, état mensuel imprimable au format officiel, export. |
| F15 | Conformité DGI : FEC, taxation en temps réel, accises/licences par point de vente | ⬜ À faire | `l10n_cm` + `aite_compliance` | Calendrier de la taxation en temps réel (LF 2026, art. L 8 sexies LPF) à suivre. |
| F16 | Objets trouvés + minibar depuis l'app housekeeping | 🟡 Partiel (fait en avance) | `aite_housekeeping` | Livré : **objets trouvés** (`aite.hk.lost.found`, séjour deviné, « Rendu au client »). Reste : minibar (consommation relevée par l'équipière → ligne sur le folio, recharge stock). |
| F17 | Mode dégradé réception (hors connexion) | ⬜ À faire | `aite_offline_desk` | Effort L ; PWA planning + arrivées du jour en cache, saisie différée. |

### Vague 3 — back-office (modèle EISI) & innovation (6-12 mois)

| ID | Fonctionnalité | Statut | Module proposé | Notes |
|---|---|---|---|---|
| F18 | Consommations & énergie (eau, électricité, carburant) par chambre occupée | ⬜ À faire | `aite_utilities` | |
| F19 | Qualité & audits : checklists chambres, HACCP simplifié, audits de standards avec photos | 🟡 Partiel | `aite_quality_audits` | Livré : checklist d'inspection de chambre paramétrable (`aite.hk.checklist.item`). Reste : photos, HACCP, audits de standards. |
| F20 | Incidents & voix du client | ⬜ À faire | `aite_guest_requests` | |
| F21 | Planning des équipes (shifts) | ⬜ À faire | Planning (EE) / module CE | |
| F22 | Upsell pré-arrivée | ⬜ À faire | `aite_online_checkin` | Après F12. |
| F23 | Tarification par règles d'occupation | ⬜ À faire | `aite_revenue` | Après F07. |
| F24 | Assistant IA du gérant + agent WhatsApp | ⬜ À faire | `aite_assistant` | Après F11. |
| F25 | Portail de séjour QR en chambre + bons cadeaux | ⬜ À faire | `aite_guest_portal` | `pos_self_order` (CE) à relier à la chambre. |
| F26 | E-réputation & enquêtes post-séjour | ⬜ À faire | `aite_guest_messaging` | Surveys (CE). |

---

## 4. Reste de la vague 1 — notes de conception

Ordre recommandé : ~~F06~~ (livré) → **F05 → F07 → F08 → F09** (du plus court au plus long ; F09 dépend de F08). Chaque fonctionnalité suit la méthode du §6 : parcours novice joués sur un Odoo réel, audit des menus, captures, puis ajout au cahier de recette.

### F06 — Indicateurs RevPAR / ADR / TO / pace / pickup — ✅ livré le 11/10
- **Choix** : pas de vue SQL `aite.hotel.kpi.daily` ; le fournisseur `aite.hotel.dashboard` calcule à la demande (volumes LAVERANDAH : quelques dizaines de chambres). Le tableau exécutif et le cockpit Direction **relisent** ce fournisseur : aucune formule dupliquée, mêmes chiffres partout.
- **Correction de fond** : la nuitée du folio est une seule ligne datée du jour de confirmation ; le CA hébergement des indicateurs se calcule désormais nuit par nuit depuis les lignes de séjour (`_room_revenue_by_line`), sinon toute période passée — et la comparaison N-1 — était vide.
- **Phrases** : `KPI_HINTS` dans `aite_exec_dashboard` (servies par `get_meta`, reprises par le cockpit).

### F05 — Clôture journalière / night audit (effort M)
- **Où** : Hôtel → Facturation → **Clôture du jour** ; modèle `aite.hotel.night.audit` (date, hôtel, état brouillon/clôturé, lignes de contrôle, totaux).
- **Quoi** : (1) **contrôles** affichés avant clôture, en français courant : réservations attendues non arrivées (→ no-show ou report), départs prévus non partis (→ prolonger ou check-out), folios de départs non soldés, chambres hors service, fiches d'enregistrement incomplètes (F03) ; (2) **nuitées postées** : s'assurer que chaque séjour présent porte sa ligne de la nuit (hébergement + taxe de séjour F04) ; (3) **rapport du jour** PDF : occupation, arrivées/départs, CA hébergement / services / POS note de chambre, encaissements par mode (espèces, MoMo, carte…), taxe de séjour du jour, no-shows, chambres HS ; (4) **verrouillage** : la date d'exploitation avance ; aucune modification de ligne de folio datée d'un jour clôturé sans profil Responsable.
- **Accroche** : le cron existant `_cron_daily_tasks` fait le no-show et le ménage ; la clôture manuelle doit rester possible (le gérant garde la main) avec un cron de rappel « clôture non faite ».

### F07 — Plans tarifaires : restrictions, packages, tarifs négociés (effort M)
- **Existant** : `aite.hotel.season.price` (prix / nuit par type et plage) ; `agent_id` + commission sur la réservation.
- **Restrictions** : sur la saison (ou une nouvelle entité « règle de vente ») : séjour minimum, stop-sell, fermé à l'arrivée / au départ, par type de chambre et plage de dates ; appliquées à la **création de réservation** (message clair : « Séjour minimum 2 nuits du 20 au 31 décembre ») et au moteur web (`aite_website_booking`).
- **Packages (pension)** : sur le type de chambre ou la réservation : Chambre seule / PDJ / Demi-pension / Pension complète → services (`aite.hotel.service`) ajoutés automatiquement au folio par nuit × personne, comme la taxe de séjour (modèle à réutiliser : `_sync_room_lines`).
- **Tarifs négociés** : `aite.hotel.rate.plan` lié à un partenaire société/agence (remise % ou grille par type), sélectionné automatiquement quand le payeur est cette société ; commission d'agence déjà en place.

### F08 — Groupes & allotements (effort M)
- **Modèle** `aite.hotel.group` : nom, hôtel, organisateur (société/agence), dates, **blocks** par type de chambre (quantité réservée, quantité confirmée), **date de release** (les chambres non confirmées retournent à la vente ; cron + alerte J-3), **rooming list** (import xlsx : nom, prénom, type, arrivée, départ → crée les réservations liées), **facture maître** (folio du groupe) vs factures individuelles.
- **Intuitif** : un assistant en 3 écrans (Qui / Combien de chambres et quand / Qui dort où), état d'avancement « 12 chambres bloquées · 7 nommées · release le 15/12 ».

### F09 — Multi-folios & routage des charges (effort M, après F08)
- `aite.hotel.folio` : plusieurs folios par réservation (`folio_ids`, un folio **principal**) avec un **payeur** chacun (client, société, groupe).
- **Règles de routage** sur la réservation : hébergement → folio société ; extras/POS → folio client ; taxe de séjour → suit l'hébergement. La note de chambre (`aite_hotel_pos_link`) route vers le folio « extras ».
- **Split de facture** : assistant « Déplacer ces lignes vers… » ; facture par folio ; facture maître du groupe (F08).

---

## 5. Hors fonctionnalités : livrables produits et documentation

| Livrable | État |
|---|---|
| Plaquette commerciale AITE HOUSE (19 pages, générateur WeasyPrint) + flyer | ✅ (11 emplacements de captures réelles restent à fournir) |
| Guides utilisateur PDF (Note de chambre, Réservation en ligne, Fidélité, Espaces & prestations, Tableau de bord Direction) | ✅ |
| Fiches produit POS Analytics, POS Crédit | ✅ |
| Étude comparative (19 pages) + benchmarks | ✅ |
| Cahier de recette (146 cas, 17 domaines A-Q) + plan de recette (15 pages) | ✅ |
| Kit éditorial (relance chaîne, contenu #1, 5 articles de blog) | ✅ |
| Guides utilisateur des 3 nouveaux modules | ⬜ À produire (captures disponibles dans `captures/`) |

---

## 6. Méthode de développement et de test (à conserver)

1. **Odoo 18 réel** dans l'environnement de développement (Community + PostgreSQL) ; jamais de validation « statique » seule.
2. Pour chaque fonctionnalité : un scénario `tests/<module>/scenario_*.py` joué dans `odoo-bin shell`, écrit **du point de vue d'un utilisateur qui découvre l'écran** (réceptionniste, équipière, gouvernante, gérant) ; `env.cr.rollback()` à la fin ; sortie 1 si un contrôle échoue.
3. Logique pure dans des `@staticmethod` testées sans Odoo (`tests/*/test_*_logic.py`).
4. **Audit des menus** (`dev/audit_menus.py`) : chaque action s'ouvre, chaque état vide a une aide d'au moins 120 caractères, pas d'anglais résiduel.
5. **Installation à froid** sur une base vierge avant livraison.
6. **Captures** Playwright (`tests/shots.py`) pour la documentation ; attendre des sélecteurs, jamais `networkidle`.
7. Ajout des cas au **cahier de recette** (`recette/cas_de_test.py` → `build_xlsx.py` → `build_plan.py`).
8. Règles d'intuitivité : chaque réglage porte une phrase « ce qui va se passer » ; les états vides disent quoi faire ; aucune saisie demandée à la réception pour la conformité ; un bouton = une étape ; s'accrocher aux écrans existants plutôt que créer des menus.

---

## 7. Questions ouvertes / décisions à prendre

| Sujet | Question | Impact |
|---|---|---|
| Fiche de police CM | Format officiel DGSN / MINTOUL à confirmer (la fiche livrée reprend les champs des registres usuels) | F03 — ajustement du PDF |
| Taxe de séjour | Articles CGI exacts, clé de répartition 80/20 commune/État, calendrier de la taxation en temps réel | F04 / F15 — texte légal dans l'onglet |
| Édition Odoo | ✅ Réglé : le socle s'installe sur Community (planning calendrier) ; `aite_hotel_gantt` ajoute le Gantt sur Enterprise | — |
| Plaquette | Mentions légales page Contact : RC/DLA/2022/A/80 · NUI P029416901505B (ancienne brochure) ou RC/DLA/2019/B/1043 · NUI M021912751893C (offre 2025) ? | Documentation commerciale |
| POS LAVERANDAH | Impression du ticket : les 4 informations de diagnostic n'ont pas été reçues (modèle d'imprimante, mode d'impression, navigateur, message d'erreur) | Support client |

---

## 8. Historique

| Date | Événement |
|---|---|
| 2026-08 | Incident « field is undefined » résolu : bundle complet des 12 modules |
| 2026-09 | Paquet `AITE_HOUSE_suite_complete` (12 modules, documentation) ; plaquette 19 pages ; kit éditorial |
| 2026-10-10 | Étude comparative (63 critères, 26 fonctionnalités, 3 vagues) ; cahier de recette 114 cas (domaines A-M) |
| 2026-10-11 | **Vague 1 — livraison 1** : `aite_city_tax`, `aite_guest_registry` 18.0.1.0.0, `aite_housekeeping` 18.0.1.0.1 ; socle 18.0.1.0.3 ; cahier de recette 139 cas ; export développement pour Claude Code |
| 2026-10-11 | Dépôt git unifié (`BigWenceslas/AITE-HOUSE`) : export vague 1 + campagne de tests de septembre ; environnement Odoo 18 reproductible (`dev/`) |
| 2026-10-11 | **F06 livré** : RevPAR, pickup, pace, écarts N-1 (tableau exécutif 18.0.1.1.0, cockpit Direction 18.0.1.1.0) ; correctifs trouvés en campagne : droits admin POS/Crédit, fuseau des créneaux, jeu d'essai ; cahier de recette 146 cas (domaine Q) |
