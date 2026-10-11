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
- Base Community : le socle exige web_gantt (Enterprise). Une variante
  Community (planning calendrier) a été validée en test ; à packager si un
  prospect Community se présente.
- Vague 1 restante (prochaine itération) : night audit (F05), RevPAR/ADR
  (F06), saisons & restrictions (F07), groupes & allotements (F08),
  multi-folios (F09).
- Format officiel de la fiche de police camerounaise à confirmer (DGSN /
  MINTOUL) ; la fiche livrée reprend les champs des registres usuels.
