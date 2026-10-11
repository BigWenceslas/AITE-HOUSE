# AITE HOUSE — Vague 1 · notes de version (11 octobre 2026)

Contenu : 3 nouveaux modules + 1 correctif du socle. Tous testés sur Odoo 18
avec des parcours « utilisateur qui n'a jamais vu la plateforme »
(110 vérifications automatisées de parcours réels + 14 tests unitaires,
26 écrans audités : aucune erreur, chaque état vide explique quoi faire).

## Nouveaux modules

### aite_city_tax 18.0.1.0.0 — Taxe de séjour
- Barèmes officiels livrés (Cameroun, Côte d'Ivoire, Sénégal, Guinée) par
  catégorie d'établissement ; modifiables (Configuration → Barèmes).
- Ligne « Taxe de séjour » ajoutée **automatiquement** au folio dès la
  confirmation ; recalculée si dates, chambres, occupants ou catégorie
  changent ; figée après facturation ; hors base TVA ; exclue du total
  « Services ».
- Fiche hôtel : onglet qui dit en une phrase ce qui sera facturé.
- Facturation → **Taxe de séjour** : état mensuel (nuitées taxées, montant
  à reverser) par hôtel et par mois, export Excel.

### aite_guest_registry 18.0.1.0.0 — Registre des clients
- Au **check-in**, la fiche du client principal est créée et pré-remplie
  depuis sa fiche contact ; bandeau sur la réservation : « 2 fiche(s) à
  compléter — compléter maintenant » ; bouton « Fiches clients 0/2 ».
- Saisie des occupants en liste, colonne « Il manque : … », fiche
  « Complète » automatiquement ; mémorisation de la pièce sur le contact.
- Impression : fiche individuelle (signatures) et **registre de police**
  sur une période (A4 paysage).
- Facturation → **Statistiques d'hébergement** : arrivées, nuitées,
  résidents / non-résidents, nationalités, motifs (format MINTOUL).

### aite_housekeeping 18.0.1.0.1 — Gouvernante & maintenance
- **Tableau des chambres** par état de ménage (À nettoyer → En cours →
  À inspecter → Propre), un bouton par étape, client et équipière visibles.
- **Ma journée** : vue téléphone de l'équipière (« Je commence » /
  « C'est fait » / « Passer la checklist »).
- **Répartir les chambres du jour** entre les équipières présentes.
- **Inspection avec checklist** (8 points livrés, paramétrables) : un
  point non conforme renvoie la chambre en nettoyage avec la remarque,
  en urgence, à la même équipière.
- **Signaler un problème** depuis la chambre → demande dans l'app
  Maintenance d'Odoo ; chambre hors service si invendable ; **remise en
  vente automatique** quand la réparation est terminée (jamais sur une
  chambre occupée).
- **Objets trouvés** : registre simple, séjour deviné, « Rendu au client ».
- Dépendance : app **Maintenance** (Odoo Community, installée automatiquement).
- 18.0.1.0.1 (11/10, après-midi) : les colonnes du tableau suivent l'ordre du
  travail (À nettoyer → En cours → À inspecter → Propre) ; Odoo 18 les triait par
  ordre alphabétique de la clé.

## Correctif du socle — aite_hotel_management 18.0.1.0.3
- **Droits** : l'administrateur reçoit le profil Responsable à
  l'installation (il voyait une erreur d'accès au premier clic) ; cocher
  un profil hôtel (Gouvernante, Réception, Responsable) rend l'utilisateur
  interne automatiquement.
- **États vides** : Arrivées du jour, Départs du jour, Clients présents,
  Règlements expliquent désormais quoi faire.
- Menu « Room rack » francisé ; masqué par le tableau des chambres quand
  aite_housekeeping est installé.
- Inchangé : dépendance web_gantt (planning Gantt, Odoo Enterprise).

## Livraison 2 (11 octobre 2026, soir) — indicateurs hôteliers (F06) et correctifs

### aite_exec_dashboard 18.0.1.1.0 — RevPAR, pickup, pace
- Nouvelle rangée **Hébergement — indicateurs de performance** : taux
  d'occupation, ADR (prix moyen par nuit), **RevPAR**, **pickup** (nuitées
  prises ces 7 derniers jours pour les 30 prochains) et **pace** (nuitées
  déjà réservées pour le mois, face à la même date l'an dernier).
- Sous chaque indicateur, l'**écart avec la même période l'an dernier**,
  en vert ou en rouge ; rien n'est affiché quand il n'y a pas d'historique.
- Un « ? » sur chaque carte donne une phrase d'explication (« RevPAR : ce
  que rapporte chaque chambre disponible, vendue ou non »).

### aite_direction_dashboard 18.0.1.1.0 — rangée Hébergement
- Vue d'ensemble : CA des nuitées, taux d'occupation, ADR, RevPAR, avec
  écart N-1, pickup et pace ; mêmes chiffres et mêmes phrases que le
  tableau exécutif ; un clic sur une carte l'ouvre. La rangée n'apparaît
  que si le module hôtelier est installé.

### Correctifs
- **aite_hotel_management** : les indicateurs comptent le CA hébergement
  **nuit par nuit** sur la période (il était daté au jour de confirmation :
  périodes passées et comparaison N-1 vides).
- **aite_pos_analytics 18.0.2.1.1, aite_pos_credit 18.0.2.0.3** :
  l'administrateur reçoit d'office les profils Manager (Analyses POS) et
  Responsable (Crédit clients) ; le cockpit Direction s'ouvrait sur une
  erreur d'accès sur une base neuve.
- **aite_slot_booking 18.0.1.0.3** : les horaires d'ouverture et la règle
  « un créneau ne franchit pas minuit » suivent le fuseau de
  l'établissement, plus celui de l'utilisateur connecté.
- **aite_guest_registry 18.0.1.0.1, aite_housekeeping 18.0.1.0.2** :
  avertissements de chargement supprimés (calculs séparés, libellé en
  double) ; ordre des colonnes du tableau des chambres porté par le socle.
- **aite_loyalty 18.0.1.0.1** : l'écran « Clients VIP / VVIP » explique
  quoi faire quand il est vide.
- **aite_demo_data 18.0.1.2.3** : fuseau de l'établissement de démo fixé,
  moyen de paiement espèces ajouté à la caisse de démo (écarts de caisse
  visibles).

### Mise à jour
Déposer les dossiers des modules ci-dessus (à côté des autres), redémarrer,
Apps → Mettre à jour la liste → **Mettre à niveau** chacun ; Ctrl+Shift+R.
Vérifier : Hôtel → Direction → rangée « Indicateurs de performance ».

## Installation / mise à jour
1. Déposer les 4 dossiers de `addons/` à côté des autres modules AITE
   (remplacer `aite_hotel_management`).
2. Redémarrer Odoo → Apps → Mettre à jour la liste.
3. **Mettre à niveau** `aite_hotel_management` (18.0.1.0.3), puis
   **installer** `aite_city_tax`, `aite_guest_registry`, `aite_housekeeping`
   (déjà installé en 18.0.1.0.0 ? → **Mettre à niveau**).
4. Ctrl+Shift+R. Vérifier : fiche hôtel → onglet « Taxe de séjour » ;
   Gouvernante → « Tableau des chambres ».
5. Renseigner sur chaque hôtel : **pays** et **catégorie (étoiles)** — c'est
   tout ce que la taxe de séjour demande.

## Connu / à venir
- Base Community : réglé — le socle s'installe tel quel (planning en vue
  calendrier) ; `aite_hotel_gantt` ajoute le Gantt sur Enterprise.
- Vague 1 restante (prochaine itération) : night audit (F05), saisons &
  restrictions (F07), groupes & allotements (F08), multi-folios (F09).
- Format officiel de la fiche de police camerounaise à confirmer (DGSN /
  MINTOUL) ; la fiche livrée reprend les champs des registres usuels.
