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

## Livraison 3 (19-20 octobre 2026) — 28 écarts bloquants corrigés

En tournant les tutoriels vidéo, 69 écarts ont été relevés et vérifiés dans le
code (`docs/videos/ECARTS.md`). Les 28 qui bloquaient un utilisateur sont
corrigés ; chaque correction est précédée d'un test qui reproduisait le défaut.

| Module | Version | Ce qui change pour l'utilisateur |
|---|---|---|
| `aite_hotel_management` | 18.0.1.0.6 | la réception seule valide un départ avec facture et encaisse le solde ; la gouvernante ouvre l'application Hôtel sur son tableau des chambres ; le prix d'un surclassement gracieux survit à une prolongation (« Prix fixé ») ; un client resté au-delà de son départ prévu garde sa chambre jusqu'au check-out ; deux confirmations simultanées ne vendent plus la même chambre ; plus de « Supprimer » dans le planning |
| `aite_hotel_gantt` | 18.0.1.0.1 | plus de « Supprimer » dans le planning Gantt |
| `aite_slot_booking` | 18.0.1.0.4 | un créneau ne se vend plus deux fois en même temps ; le pressing ne passe plus « No-show » ; l'e-mail donne l'heure de Douala |
| `aite_website_booking` | 18.0.1.0.1 | heures passées refusées ; prestation de 90 min réservable ; plus de contact en double ni de contact créé par une tentative refusée |
| `aite_hotel_pos_link` | 18.0.1.0.1 | le caissier reporte en note de chambre sans profil hôtel ; le ticket arrive au folio en HT + taxes |
| `aite_pos_credit` | 18.0.2.0.4 | une note de chambre n'ouvre plus d'ardoise ; un remboursement validé ne se modifie plus (annuler puis ressaisir), ses changements sont suivis ; « Regrouper par Sévérité » retiré |
| `aite_loyalty` | 18.0.1.0.2 | plus de points sur la taxe de séjour ni de points comptés deux fois ; « Autre prestation » valide ; statut VIP multi-société |
| `aite_city_tax` | 18.0.1.0.1 | première confirmation possible par la réception et le responsable |
| `aite_guest_registry` | 18.0.1.0.2 | « Mémoriser sur la fiche client » pour la réception ; le registre de police s'imprime ; le nom n'est plus coupé au premier espace ; plus de résidence par défaut |
| `aite_housekeeping` | 18.0.1.0.5 | le technicien passe une panne à « Réparé » et lit la chambre ; la chambre revient en vente quand plus aucune panne ne la bloque ; « Conforme » coche la checklist ; priorité Maintenance valide ; l'objet trouvé devine le séjour d'un client en dépassement |
| `aite_purchase_dashboard` | 18.0.1.0.4 | créances 409/4091 justes ; tableau de bord ouvert à l'acheteur sans Facturation |
| `aite_direction_dashboard` | 18.0.1.1.1 | barres CA vs Achats, échéancier, balance âgée, « Payer … » et carte heure × jour remplis ; phrases Flux net et position nette dans le bon sens |
| `aite_exec_dashboard` | 18.0.1.1.1 | une seule définition par chiffre : hors taxes partout (hébergement = nuitées du PMS) |
| `aite_pos_analytics` | 18.0.2.1.2 | CA des sessions HT (migration) ; taux de marge, compteurs de paiements, sessions ouvertes et classements justes ; heures de Douala |

Les trois modules de la vague 1 ont maintenant leurs tests Odoo. Campagne
complète sur base vierge (15 modules + données de démonstration) : 698 tests,
0 échec ; `dev/run_tests.sh` : tout est vert.

**À trancher par l'équipe** (détail dans `docs/videos/ECARTS.md`) : la double
créance comptable d'un ticket reporté au folio à la clôture de session ; la
nature HT/TTC des tarifs de prestation ; le no-show d'un linge jamais
retiré ; les niveaux d'urgence des pannes ; un vrai découpage nom / prénom
sur le contact (`partner_firstname`).

### Mise à jour
Déposer les dossiers des modules ci-dessus (à côté des autres), redémarrer,
Apps → Mettre à jour la liste → **Mettre à niveau** chacun ; Ctrl+Shift+R.
Le script de migration d'`aite_pos_analytics` recalcule le CA des sessions
existantes.

## Livraison 4 (23 octobre 2026) — écarts non bloquants, relecture croisée

Les 41 écarts non bloquants relevés par les tutoriels (n° 37 à 77 de
`docs/videos/ECARTS.md`) sont corrigés, puis une relecture croisée des
écrans a aligné les formats et les définitions d'un tableau de bord à
l'autre. La livraison s'applique sur une base en livraison 2 (production
LAVERANDAH) comme en livraison 3 : les scripts de migration ne tournent que
sur les modules qui en ont besoin.

| Module | Version | Ce qui change pour l'utilisateur |
|---|---|---|
| `aite_hotel_management` | 18.0.1.0.7 | dates locales et françaises ; tableau de bord « Tableau de bord — Réception » : taux « 56,0 % », écarts « ▲ +12,5 % », mêmes libellés ADR / RevPAR que la Direction ; tâche quotidienne renommée (migration) |
| `aite_hotel_gantt` | 18.0.1.0.2 | libellés français du planning |
| `aite_slot_booking` | 18.0.1.0.5 | numérotation CRN/2026/0001 par année ; refus « hors horaires (08:00 – 22:30) » ; tableau de bord en jours locaux |
| `aite_website_booking` | 18.0.1.0.2 | formats et libellés du site |
| `aite_hotel_pos_link` | 18.0.1.0.2 | lien ticket ↔ ligne de folio rétabli sur les séjours en cours (migration, fidélité) |
| `aite_pos_credit` | 18.0.2.0.5 | mode « Ardoise client » créé s'il manque (migration) ; mois en français ; délais « 12,3 j » ; libellés accordés |
| `aite_loyalty` | 18.0.1.0.3 | libellés et aides |
| `aite_pos_analytics` | 18.0.2.1.3 | montants en FCFA (et non « F ») ; écarts « ▼ 3,0 % » ; badge « Aucun écart » ; seuils d'écart de caisse réglables ; société courante seulement (règle multi-sociétés) |
| `aite_stock_dashboard` | 18.0.1.1.3 | « 3 références » (plus de « réfs ») ; couverture « 12,0 j » ou « ∞ » |
| `aite_purchase_dashboard` | 18.0.1.0.5 | « Factures échues » en positif, comme le cockpit ; libellés accordés |
| `aite_direction_dashboard` | 18.0.1.1.2 | « À payer sous N j », barre « Sous 7 jours », liste « Échéances » et lignes « Payer … » d'accord ; seuil de 30 jours du moteur Crédit ; filtre d'origine appliqué aux remboursements ; nouvelles ardoises en hausse = rouge ; libellés de POS Crédit ; mois « janv. », « sept. » |
| `aite_exec_dashboard` | 18.0.1.1.2 | menu « Hôtel → Activité par pôle » ; ventes et prestations en jours locaux (même chiffre que le cockpit, cas K04) |
| `aite_demo_data` | 18.0.1.2.4 | jeu d'essai aligné |
| `aite_city_tax` | 18.0.1.0.2 | barème réappliqué aux hôtels créés avant le module (migration) |
| `aite_guest_registry` | 18.0.1.0.3 | un seul nom : « Fiches d'enregistrement » (bouton, fenêtre, imprimé « Registre des clients ») ; bandeau accordé |
| `aite_housekeeping` | 18.0.1.0.6 | profil « Gouvernante générale » ; heure d'arrivée « 14:00 » ; menu « Répartir » réservé à la gouvernante générale |

### Ce que la mise à niveau fait seule (migrations)
- `aite_pos_analytics` : CA des sessions de caisse recalculé hors taxes.
- `aite_hotel_management` : tâche planifiée renommée « Hôtel : tâches
  quotidiennes (non-présentations, ménage) » (un nom choisi par le client
  est conservé).
- `aite_city_tax` : barème de taxe de séjour réappliqué à l'hôtel qui en
  était privé (créé avant le module) ; ligne « Taxe de séjour » ajoutée aux
  folios **ouverts et non facturés** de cet hôtel — y compris ceux d'un
  client déjà parti dont le folio est resté ouvert.
- `aite_pos_credit` : mode « Ardoise client » créé et ajouté aux caisses
  **si aucun mode n'est coché « Vente à crédit (ardoise) »**.
- `aite_hotel_pos_link` : chaque ligne de folio reportée par la caisse est
  rattachée à son ticket — la fidélité ne crédite plus deux fois les
  consommations de bar d'un séjour en cours.

### Mise à jour
Voir `docs/INSTALLATION.md` §5 : sauvegarder ; **fermer toutes les sessions
de caisse** ; déposer les dossiers à côté des autres ; redémarrer ; Apps →
Mettre à jour la liste → **Mettre à niveau chaque module AITE** ; Ctrl+F5
pour chaque utilisateur. Ne rien désinstaller.

### À vérifier après la mise à niveau
1. **Ardoises — avant de rouvrir les caisses.** Jusqu'ici, tout mode
   « payer plus tard » ouvrait une ardoise ; désormais seul le mode coché
   « Vente à crédit (ardoise) » le fait. Point de Vente → Configuration →
   Modes de paiement : repérer le mode que les caissiers utilisaient pour
   les ardoises (souvent « Compte client »). Soit le cocher « Vente à crédit
   (ardoise) » et retirer des caisses le mode « Ardoise client » créé par la
   mise à niveau ; soit garder « Ardoise client » et retirer l'ancien mode
   des caisses. **Un seul bouton d'ardoise par caisse.** Contrôler le compte
   client (Point de Vente → Paramètres → Ardoises / Crédit POS, compte 411).
2. Hôtel → Configuration → Hôtels → onglet Taxe de séjour : « Cameroun —
   3 ★ : 3 000 FCFA ». Prévenir la réception que les séjours ouverts portent
   la ligne de taxe ; vérifier le solde des folios restés ouverts après un
   départ. Un folio oublié se rattrape avec « Recalculer la taxe de séjour ».
3. Paramètres → Utilisateurs : donner « Gouvernante générale » à la
   gouvernante (répartition, validation des inspections) ; les équipières
   restent « Gouvernante ». Les utilisateurs Réception l'ont d'office.
4. Point de Vente → Configuration → Paramètres → « Analyse AITE — écarts de
   caisse » : seuils Élevé 100 000 FCFA, Critique 200 000 FCFA par défaut.
5. Créneaux : nouvelles réservations numérotées CRN/2026/0001 ; les
   références RES/26/… déjà attribuées ne changent pas.
6. Enterprise : si `aite_hotel_gantt` n'est pas installé, Apps → retirer le
   filtre « Applications » → « Gantt » → Installer ; sinon le mettre à
   niveau.

### À trancher par l'équipe (relecture croisée)
- Le mode d'ardoise à garder après la mise à niveau (point 1 ci-dessus) :
  reprise automatique du mode qui a porté des ardoises, ou choix manuel.
- Les ardoises ouvertes en livraison 2 par des tickets « Note de chambre »
  (déjà portés au folio) : annulation automatique ou liste pour la
  comptable.
- La taxe ajoutée aux folios restés ouverts d'un client déjà parti.
- Les données antérieures non rattrapées : prix fixé des surclassements
  gracieux, dates de naissance des fiches, pressing passé « Non présenté ».
- Cockpit : base HT ou TTC de « Ventes à crédit … % du CA » et des barres
  « CA vs Achats » ; références comptées dans « Lancer la commande
  suggérée » ; seuil des « Prix en hausse » ; définition de la balance âgée
  fournisseurs (âge de facture ou retard) ; un seul mot pour une vente en
  caisse (ticket, commande, transaction).

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
