# -*- coding: utf-8 -*-
"""Référentiel des scénarios de recette AITE HOUSE.

Chaque cas : (id, domaine, module, priorité, prérequis, scénario,
              étapes, résultat attendu)
Priorités : 1 = critique (bloque la mise en production)
            2 = majeur   (à corriger avant démarrage)
            3 = mineur   (confort, à planifier)
"""

# Version du cahier (à changer quand les cas changent).
VERSION = "novembre 2026"

DOMAINES = [
    ("A", "Hébergement — chambres & séjours", "aite_hotel_management"),
    ("B", "Espaces & prestations", "aite_slot_booking"),
    ("C", "Réservation en ligne", "aite_website_booking"),
    ("D", "Point de vente & caisse", "aite_pos_analytics"),
    ("E", "Note de chambre", "aite_hotel_pos_link"),
    ("F", "Crédit clients (ardoises)", "aite_pos_credit"),
    ("G", "Fidélité", "aite_loyalty"),
    ("H", "Stock & inventaire", "aite_stock_dashboard"),
    ("I", "Achats & fournisseurs", "aite_purchase_dashboard"),
    ("J", "Pilotage — vue Direction", "aite_direction_dashboard"),
    ("K", "Tableau de bord exécutif", "aite_exec_dashboard"),
    ("L", "Jeu de démonstration", "aite_demo_data"),
    ("M", "Transverse — sécurité, données, exploitation", "tous modules"),
    ("N", "Taxe de séjour", "aite_city_tax"),
    ("O", "Registre des clients & statistiques", "aite_guest_registry"),
    ("P", "Gouvernante, inspections & maintenance", "aite_housekeeping"),
    ("Q", "Indicateurs hôteliers — RevPAR, pickup, pace",
     "aite_exec_dashboard, aite_direction_dashboard"),
    ("R", "Restaurant — service à table (lot 1)",
     "aite_pos_restaurant, aite_pos_credit, aite_pos_analytics, aite_pos_analytics_hr"),
]

CAS = [
    # ══════════ A — HÉBERGEMENT ══════════
    ("A01", "A", 1, "Base installée, 1 type de chambre créé",
     "Créer une chambre et la rendre réservable",
     "1. Hôtel → Configuration → Chambres → Créer.\n"
     "2. Renseigner numéro, type, capacité, tarif de base en FCFA.\n"
     "3. Enregistrer, puis ouvrir le planning.",
     "La chambre est enregistrée sans erreur et apparaît dans le "
     "planning, en statut Libre sur toute la période."),
    ("A02", "A", 1, "Au moins 2 chambres disponibles",
     "Créer une réservation directe (walk-in)",
     "1. Hôtel → Réservations → Créer.\n"
     "2. Sélectionner client, chambre, dates d'arrivée et de départ.\n"
     "3. Confirmer la réservation.",
     "La réservation passe en statut Confirmée, le nombre de nuits et "
     "le montant total sont calculés automatiquement en FCFA."),
    ("A03", "A", 1, "Une réservation confirmée existe sur la période",
     "Empêcher la double réservation d'une même chambre",
     "1. Créer une seconde réservation sur la même chambre avec des "
     "dates qui se chevauchent.\n2. Tenter de confirmer.",
     "Le système refuse la confirmation ou signale explicitement le "
     "conflit ; la chambre n'est pas réservée deux fois."),
    ("A04", "A", 1, "Réservation confirmée du jour",
     "Effectuer un check-in",
     "1. Ouvrir la réservation du jour.\n2. Cliquer sur Check-in.",
     "Le statut passe à Arrivée / En cours, la chambre devient Occupée "
     "dans le planning, et le folio du séjour est créé."),
    ("A05", "A", 1, "Séjour en cours avec folio ouvert",
     "Ajouter un extra au folio (petit-déjeuner)",
     "1. Ouvrir le folio du séjour.\n2. Ajouter la ligne "
     "« Petit-déjeuner » × 2.\n3. Enregistrer.",
     "La ligne s'ajoute avec sa date et son montant ; le total du "
     "folio est recalculé immédiatement."),
    ("A06", "A", 1, "Séjour en cours, folio alimenté",
     "Effectuer un check-out et facturer le séjour",
     "1. Ouvrir la réservation.\n2. Cliquer sur Check-out.\n"
     "3. Générer la facture.",
     "Une facture unique reprend nuitées et extras, la chambre "
     "redevient Libre, et le séjour passe en statut Terminé."),
    ("A07", "A", 2, "Réservation confirmée, acompte prévu",
     "Enregistrer un acompte et le déduire à la facturation",
     "1. Saisir un acompte de 20 000 F sur la réservation.\n"
     "2. Aller jusqu'au check-out et générer la facture.",
     "L'acompte apparaît sur le folio et est déduit du net à payer ; "
     "le solde restant dû est exact."),
    ("A08", "A", 2, "Réservation confirmée",
     "Éditer une proforma avant le départ",
     "1. Ouvrir le séjour en cours.\n2. Demander l'impression de la "
     "proforma.",
     "La proforma s'édite en PDF avec l'en-tête de l'établissement, "
     "les lignes du folio et les montants en FCFA."),
    ("A09", "A", 2, "Plusieurs chambres, dont une en maintenance",
     "Déclarer une chambre hors service",
     "1. Passer une chambre en statut Hors service / Maintenance sur "
     "une période.\n2. Consulter le planning.",
     "La chambre apparaît en Hors service sur la période et n'est plus "
     "proposée à la réservation."),
    ("A10", "A", 2, "Journée avec arrivées, départs et présents",
     "Consulter la main courante du jour",
     "1. Ouvrir la main courante / photo du jour.",
     "Les compteurs Présents, Arrivées, Départs et Hors service "
     "correspondent exactement à la réalité du planning."),
    ("A11", "A", 2, "Réservation confirmée non arrivée",
     "Annuler une réservation et gérer un client non présenté",
     "1. Annuler une réservation confirmée.\n2. Marquer une autre "
     "« Non présenté » (bouton de la réservation).",
     "Les statuts sont mis à jour, les chambres se libèrent, et le "
     "motif reste consultable dans l'historique."),
    ("A12", "A", 2, "Deux types de chambre avec tarifs différents",
     "Appliquer un tarif par type de chambre et par période",
     "1. Créer une réservation sur chaque type de chambre.\n"
     "2. Comparer les montants calculés.",
     "Chaque réservation applique le tarif du type de chambre "
     "concerné ; les éventuelles listes de prix saisonnières sont "
     "respectées."),
    ("A13", "A", 3, "Séjour en cours",
     "Changer un client de chambre en cours de séjour",
     "1. Ouvrir le séjour.\n2. Effectuer un transfert vers une autre "
     "chambre libre.",
     "Le folio suit le client sans perte de lignes ; les deux chambres "
     "ont un statut cohérent dans le planning."),
    ("A14", "A", 3, "Plusieurs séjours facturés sur le mois",
     "Vérifier la ventilation comptable par type de prestation",
     "1. Comptabilité → journal des ventes.\n2. Contrôler les écritures "
     "issues des factures de séjour.",
     "Hébergement, restauration et prestations sont ventilés sur des "
     "comptes distincts, conformément au paramétrage."),

    # ══════════ B — ESPACES & PRESTATIONS ══════════
    ("B01", "B", 1, "Module installé",
     "Créer un espace réservable avec son tarif",
     "1. Créer l'espace « Salle de réunion » avec tarif horaire et "
     "capacité.\n2. Enregistrer.",
     "L'espace est créé et apparaît dans le planning des ressources."),
    ("B02", "B", 1, "Un espace créé",
     "Réserver un créneau pour un client externe",
     "1. Réserver la salle de 9 h à 12 h pour un client.\n"
     "2. Confirmer.",
     "Le créneau apparaît occupé dans le planning et le montant est "
     "calculé selon la durée et le tarif."),
    ("B03", "B", 1, "Un créneau déjà réservé",
     "Empêcher la double réservation d'un créneau",
     "1. Tenter de réserver le même espace sur un créneau qui "
     "chevauche.",
     "Le système refuse ou alerte explicitement ; aucun double "
     "engagement n'est enregistré."),
    ("B04", "B", 2, "Séjour hôtel en cours",
     "Rattacher une prestation au folio d'une chambre",
     "1. Réserver la piscine pour un client résident.\n"
     "2. Rattacher au séjour.\n3. Ouvrir le folio.",
     "La prestation apparaît sur le folio de la chambre et sera "
     "facturée avec le séjour."),
    ("B05", "B", 2, "Prestation réservée et payée",
     "Facturer une prestation seule",
     "1. Facturer une prestation à un client non résident.",
     "La facture est éditée en FCFA et l'écriture comptable est "
     "générée."),
    ("B06", "B", 2, "Créneau réservé",
     "Annuler une réservation d'espace",
     "1. Annuler le créneau.\n2. Consulter le planning.",
     "Le créneau redevient disponible ; l'acompte éventuel suit les "
     "conditions définies."),
    ("B07", "B", 3, "Plusieurs espaces et créneaux sur le mois",
     "Mesurer le chiffre d'affaires par espace",
     "1. Ouvrir le récapitulatif par espace sur le mois.",
     "Le CA par espace et le taux d'occupation sont cohérents avec les "
     "réservations saisies."),
    ("B08", "B", 3, "Espace avec tarifs multiples",
     "Appliquer les tarifs heure / demi-journée / journée",
     "1. Réserver successivement 1 h, une demi-journée et une journée.",
     "Le tarif appliqué correspond à la durée choisie pour chacune des "
     "trois réservations."),

    # ══════════ C — RÉSERVATION EN LIGNE ══════════
    ("C01", "C", 1, "Site web publié, chambres disponibles",
     "Rechercher une disponibilité depuis le site",
     "1. Ouvrir le site public.\n2. Saisir des dates et un nombre de "
     "voyageurs.\n3. Lancer la recherche.",
     "Seules les chambres réellement disponibles sont proposées, avec "
     "leur tarif en FCFA."),
    ("C02", "C", 1, "Recherche effectuée",
     "Envoyer une demande de séjour en ligne",
     "1. Choisir une chambre.\n2. Renseigner les informations client.\n"
     "3. Envoyer la demande.",
     "Une réservation en brouillon est créée au nom du client (sans "
     "doublon de contact) ; la réception la confirme et encaisse "
     "l'acompte au comptoir (pas de paiement en ligne)."),
    ("C03", "C", 1, "Réservation en ligne confirmée",
     "Vérifier la retombée dans le planning de la réception",
     "1. Côté back-office, ouvrir le planning et la main courante.",
     "La réservation apparaît sans aucune ressaisie, avec le statut "
     "acompte reçu et les dates exactes."),
    ("C04", "C", 1, "Une chambre unique disponible",
     "Gérer la concurrence entre deux réservations simultanées",
     "1. Lancer deux parcours de réservation en parallèle sur la même "
     "chambre.\n2. Confirmer le premier, puis le second.",
     "La première confirmation bloque la chambre ; la seconde est "
     "refusée ou redirigée vers une alternative."),
    ("C05", "C", 2, "Paramétrage d'acompte défini",
     "Contrôler le montant d'acompte appliqué",
     "1. Réserver et comparer l'acompte demandé au paramétrage "
     "(pourcentage ou montant fixe).",
     "L'acompte prélevé correspond exactement à la règle définie."),
    ("C06", "C", 2, "Réservation en ligne effectuée",
     "Réceptionner le client à l'arrivée",
     "1. Faire le check-in de la réservation venue du web.",
     "Le séjour démarre normalement et l'acompte est déjà déduit du "
     "folio."),
    ("C07", "C", 2, "Site en ligne",
     "Réserver depuis un téléphone",
     "1. Refaire le parcours complet sur smartphone.",
     "Le parcours est lisible et utilisable sur petit écran, sans "
     "débordement ni bouton inaccessible."),
    ("C08", "C", 3, "Espaces ouverts à la réservation en ligne",
     "Réserver un espace depuis le site",
     "1. Réserver une salle ou un espace via le site public.",
     "Le créneau est bloqué dans le planning des ressources, avec "
     "acompte le cas échéant."),

    # ══════════ D — POINT DE VENTE & CAISSE ══════════
    ("D01", "D", 1, "Caisse configurée, produits en stock",
     "Ouvrir une session de caisse",
     "1. Point de Vente → Nouvelle session.\n2. Saisir le fond de "
     "caisse.",
     "La session s'ouvre, le fond de caisse est enregistré et "
     "l'interface de vente s'affiche."),
    ("D02", "D", 1, "Session ouverte",
     "Encaisser une vente en espèces",
     "1. Sélectionner 3 produits.\n2. Paiement → Espèces.\n"
     "3. Valider.",
     "Le total est correct en FCFA, le ticket est généré et la vente "
     "apparaît dans la liste des commandes."),
    ("D03", "D", 1, "Session ouverte",
     "Encaisser en Mobile Money",
     "1. Réaliser une vente.\n2. Payer via le mode Mobile Money.",
     "Le paiement est enregistré sur le bon journal et distinct des "
     "espèces dans le récapitulatif de session."),
    ("D04", "D", 1, "Session ouverte avec ventes",
     "Clôturer la session et contrôler les écarts de caisse",
     "1. Clôturer la session.\n2. Saisir le montant réellement "
     "compté.\n3. Valider.",
     "L'écart entre théorique et compté est affiché, journalisé, et la "
     "session passe en statut Clôturée."),
    ("D05", "D", 1, "Deux points de vente configurés (bar, boutique)",
     "Vérifier le cloisonnement des cartes par caisse",
     "1. Ouvrir successivement les deux caisses.\n2. Comparer les "
     "produits affichés.",
     "Chaque caisse n'affiche que les produits de sa propre carte ; "
     "aucun produit de l'autre point de vente n'apparaît."),
    ("D06", "D", 2, "Session ouverte",
     "Appliquer une remise et la tracer",
     "1. Appliquer une remise sur une ligne de ticket.\n2. Encaisser.",
     "La remise est appliquée au bon montant, tracée avec le vendeur, "
     "et visible dans les analyses."),
    ("D07", "D", 2, "Vente encaissée",
     "Imprimer un ticket de caisse",
     "1. Demander l'impression du ticket après paiement.",
     "Le ticket s'imprime (ou s'affiche pour impression) avec les "
     "lignes, le total et le mode de règlement."),
    ("D08", "D", 2, "Session ouverte, connexion réseau active",
     "Encaisser hors connexion",
     "1. Couper la connexion réseau.\n2. Encaisser 2 ventes.\n"
     "3. Rétablir la connexion.",
     "Les ventes se poursuivent hors ligne puis se synchronisent sans "
     "perte ni doublon au retour du réseau."),
    ("D09", "D", 2, "Ventes réalisées sur plusieurs jours et heures",
     "Consulter les analyses de ventes",
     "1. Ouvrir POS Analytics.\n2. Filtrer par période et par caisse.",
     "Le CA, le nombre de tickets et le panier moyen correspondent aux "
     "ventes réelles de la période filtrée."),
    ("D10", "D", 2, "Ventes sur plusieurs tranches horaires",
     "Vérifier la carte de chaleur jours × heures",
     "1. Ouvrir la heatmap des ventes.",
     "Les heures de forte activité correspondent aux ventes "
     "effectivement saisies ; aucune case aberrante."),
    ("D11", "D", 2, "Produits avec prix d'achat renseignés",
     "Contrôler la marge et le coût des ventes",
     "1. Consulter les marges par produit et par catégorie.",
     "La marge affichée correspond à (prix de vente − coût) et le CMV "
     "est cohérent avec les ventes."),
    ("D12", "D", 3, "Session avec plusieurs vendeurs",
     "Suivre les ventes par vendeur",
     "1. Filtrer les ventes par vendeur sur la session.",
     "Le détail par vendeur est exact et exploitable pour le suivi "
     "d'équipe."),

    # ══════════ E — NOTE DE CHAMBRE ══════════
    ("E01", "E", 1, "Un séjour en cours (chambre occupée), caisse ouverte",
     "Encaisser une consommation sur la note de chambre",
     "1. Au POS, composer un ticket.\n2. Sélectionner le client du "
     "séjour.\n3. Paiement → Note de chambre.\n4. Valider.",
     "Le paiement est accepté, le ticket mentionne la chambre, et "
     "aucun encaissement espèces n'est enregistré."),
    ("E02", "E", 1, "Consommation reportée (cas E01)",
     "Vérifier l'alimentation du folio",
     "1. Ouvrir le folio de la chambre concernée.",
     "La consommation du bar apparaît, datée, au bon montant, "
     "identifiée par sa caisse d'origine."),
    ("E03", "E", 1, "Client sans séjour ouvert (ou avec plusieurs)",
     "Ne jamais reporter au hasard",
     "1. Au POS, régler en Note de chambre un ticket d'un client sans "
     "folio ouvert (ou sans client).\n2. Ouvrir Hôtel → Notes de "
     "chambre en attente.",
     "Le ticket n'est rattaché à aucun folio : il attend dans « Notes "
     "de chambre en attente », où la réception choisit le folio."),
    ("E04", "E", 1, "Folio alimenté par un report bar",
     "Facturer le séjour incluant le bar",
     "1. Effectuer le check-out.\n2. Générer la facture.",
     "La facture unique comprend nuitées, extras et consommations du "
     "bar, avec un total exact."),
    ("E05", "E", 2, "Report effectué",
     "Valider ou corriger un report côté réception",
     "1. Ouvrir la liste des reports en attente.\n2. Valider l'un, "
     "corriger ou refuser l'autre.",
     "Le folio reflète la décision de la réception ; toute correction "
     "est tracée."),
    ("E06", "E", 2, "Deux caisses actives, un séjour en cours",
     "Reporter depuis deux caisses différentes",
     "1. Reporter une consommation depuis chaque caisse.",
     "Les deux reports arrivent sur le même folio en conservant "
     "l'identification de leur caisse."),
    ("E07", "E", 2, "Séjour avec reports facturés",
     "Contrôler la ventilation comptable du bar",
     "1. Consulter les écritures de la facture de séjour.",
     "Le chiffre d'affaires du bar est ventilé sur son propre compte, "
     "distinct de l'hébergement."),
    ("E08", "E", 3, "Séjour en cours",
     "Vérifier le comportement après départ du client",
     "1. Effectuer le check-out.\n2. Tenter un report sur cette "
     "chambre.",
     "Le report est impossible sur un séjour clôturé ; un message "
     "clair est affiché."),

    # ══════════ F — CRÉDIT CLIENTS ══════════
    ("F01", "F", 1, "Module installé",
     "Activer la vente à crédit sur un mode de paiement",
     "1. Point de Vente → Configuration → Modes de paiement.\n2. Ouvrir "
     "« Ardoise client ».\n3. Vérifier la case « Vente à crédit ».",
     "Le mode « Ardoise client » existe dès l'installation, case cochée ; "
     "seul un mode coché ouvre une ardoise (pas la Note de chambre). "
     "Il n'y a pas de plafond de crédit par client."),
    ("F02", "F", 1, "Client identifié, session de caisse ouverte",
     "Accorder un crédit à la caisse",
     "1. Composer un ticket.\n2. Paiement → Crédit.\n3. Sélectionner "
     "le client.\n4. Valider.",
     "La vente est enregistrée en crédit, l'encours du client augmente "
     "du montant exact."),
    ("F03", "F", 1, "Ardoises d'âges différents",
     "Repérer les ardoises à relancer",
     "1. Ouvrir POS Crédit → Ardoises.\n2. Lire la colonne Sévérité et "
     "le tableau de bord du crédit.",
     "Chaque ardoise est classée selon son âge (Récente, En retard, "
     "Critique ; Réglée une fois soldée) ; les plus anciennes ressortent "
     "dans le tableau de bord. La relance se fait à la main."),
    ("F04", "F", 1, "Client avec encours",
     "Enregistrer un remboursement partiel",
     "1. Saisir un remboursement inférieur à l'encours (espèces).",
     "L'encours diminue du montant exact ; le règlement est tracé avec "
     "sa date et son mode."),
    ("F05", "F", 1, "Client avec encours",
     "Solder complètement une ardoise",
     "1. Enregistrer un remboursement égal au solde.",
     "L'encours passe à zéro et le client n'apparaît plus parmi les "
     "débiteurs."),
    ("F06", "F", 2, "Plusieurs clients avec des crédits d'âges variés",
     "Contrôler la balance âgée",
     "1. Ouvrir le tableau de bord Crédit.\n2. Examiner les tranches "
     "0–30, 31–60, 61–90 et +90 jours.",
     "Chaque créance est classée dans la bonne tranche d'ancienneté et "
     "le total correspond à l'encours global."),
    ("F07", "F", 2, "Encours réparti sur plusieurs clients",
     "Vérifier le top débiteurs",
     "1. Consulter la liste des principaux débiteurs.",
     "Le classement par montant est exact et l'ancienneté affichée "
     "correspond à la plus vieille créance."),
    ("F08", "F", 2, "Remboursements du mois enregistrés",
     "Contrôler le taux de recouvrement et le flux net",
     "1. Consulter les indicateurs de recouvrement du mois.",
     "Recouvré, nouveaux crédits et flux net sont cohérents avec les "
     "mouvements saisis."),
    ("F09", "F", 2, "Client avec crédit en cours",
     "Rembourser par Mobile Money",
     "1. Enregistrer un remboursement via Mobile Money.",
     "Le règlement est imputé au bon journal et distingué des espèces "
     "dans les états."),
    ("F10", "F", 2, "Crédits accordés et remboursés",
     "Vérifier les écritures comptables du crédit",
     "1. Contrôler les écritures générées à l'octroi et au "
     "remboursement.",
     "Les comptes clients sont mouvementés correctement, sans écriture "
     "orpheline ni double comptabilisation."),
    ("F11", "F", 3, "Plusieurs caisses accordant du crédit",
     "Suivre le crédit par caisse",
     "1. Filtrer l'encours par point de vente.",
     "La répartition par caisse est exacte et le total consolidé est "
     "conservé."),
    ("F12", "F", 3, "Client débiteur de plus de 30 jours",
     "Éditer un relevé ou une relance client",
     "1. Générer le relevé de compte du client.",
     "Le document liste les créances avec leurs dates et le solde dû "
     "exact."),

    # ══════════ G — FIDÉLITÉ ══════════
    ("G01", "G", 1, "Module installé",
     "Paramétrer le taux de points et les seuils VIP",
     "1. Paramètres → Fidélité.\n2. Définir les points par 1 000 F et "
     "les seuils VIP / VVIP.\n3. Enregistrer.",
     "Les règles sont enregistrées et reprises lors des calculs "
     "suivants."),
    ("G02", "G", 1, "Règles définies, client identifié en caisse",
     "Cumuler des points sur une vente",
     "1. Encaisser une vente avec le client sélectionné.",
     "Les points crédités correspondent exactement au montant dépensé "
     "et au taux paramétré."),
    ("G03", "G", 1, "Client proche du seuil VIP",
     "Déclencher le passage au niveau VIP",
     "1. Réaliser la vente qui fait franchir le seuil.\n2. Consulter "
     "la fiche client.",
     "Le niveau passe à VIP au recalcul quotidien des statuts (tâche "
     "planifiée « Fidélité : recalcul des statuts clients »), dès que "
     "les seuils de dépenses ET de visites sont atteints."),
    ("G04", "G", 2, "Client VIP proche du seuil VVIP",
     "Déclencher le passage VVIP",
     "1. Franchir les seuils de dépenses, de visites et de pôles "
     "(hébergement, restauration, prestations) requis.",
     "Le niveau VVIP n'est attribué que si les trois conditions "
     "paramétrées sont remplies."),
    ("G05", "G", 2, "Catégorie comptant double paramétrée",
     "Vérifier les catégories à points doublés",
     "1. Vendre un produit de la catégorie concernée.",
     "Les points crédités sont doublés uniquement pour cette "
     "catégorie."),
    ("G06", "G", 2, "Clients avec points cumulés",
     "Consulter le classement des clients fidèles",
     "1. Ouvrir le classement des meilleurs clients.",
     "Les totaux de points et les niveaux affichés correspondent aux "
     "fiches clients."),
    ("G07", "G", 2, "Client fidèle identifié",
     "Afficher le niveau du client au moment de l'encaissement",
     "1. Sélectionner le client au POS.",
     "Le niveau (VIP / VVIP) est visible par le caissier avant "
     "validation du paiement."),
    ("G08", "G", 3, "Client sans fiche",
     "Vendre sans client identifié",
     "1. Encaisser une vente sans sélectionner de client.",
     "La vente aboutit normalement ; aucun point n'est attribué et "
     "aucune erreur n'est levée."),

    # ══════════ H — STOCK & INVENTAIRE ══════════
    ("H01", "H", 1, "Articles avec stock initial et prix d'achat",
     "Contrôler la valorisation du stock",
     "1. Ouvrir le tableau de bord Stock.",
     "Les valeurs au coût et au prix de vente correspondent aux "
     "quantités multipliées par les prix renseignés."),
    ("H02", "H", 1, "Article avec seuil d'alerte défini",
     "Déclencher une alerte de rupture",
     "1. Vendre jusqu'à passer sous le seuil, puis jusqu'à zéro.\n"
     "2. Consulter les alertes.",
     "L'article apparaît successivement en Sous seuil, Critique puis "
     "Rupture, selon les règles définies."),
    ("H03", "H", 1, "Articles en alerte",
     "Vérifier les quantités suggérées à commander",
     "1. Consulter la colonne des quantités suggérées.",
     "La suggestion tient compte du seuil, de la consommation et du "
     "délai de réapprovisionnement."),
    ("H04", "H", 1, "Stock théorique connu sur plusieurs articles",
     "Réaliser un inventaire tournant avec écarts",
     "1. Saisir un inventaire avec des quantités comptées "
     "différentes.\n2. Valider.",
     "Les écarts sont calculés, valorisés, et le stock est ajusté "
     "après validation."),
    ("H05", "H", 1, "Ventes et inventaires sur le mois",
     "Contrôler le calcul du coulage",
     "1. Consulter l'indicateur de coulage du mois.",
     "Le coulage correspond aux écarts constatés, et l'alerte se "
     "déclenche si le seuil défini est dépassé."),
    ("H06", "H", 2, "Ventes régulières sur un article",
     "Vérifier la couverture de stock en jours",
     "1. Consulter la couverture affichée pour l'article.",
     "La couverture est cohérente avec le rythme de vente constaté."),
    ("H07", "H", 2, "Article sans vente depuis plus de 30 jours",
     "Identifier les articles dormants",
     "1. Consulter la liste des articles dormants.",
     "L'article apparaît avec sa valeur immobilisée."),
    ("H08", "H", 2, "Plusieurs dépôts configurés (cave, bar)",
     "Transférer du stock entre deux dépôts",
     "1. Effectuer un transfert cave → bar.\n2. Contrôler les deux "
     "dépôts.",
     "Les quantités sont décrémentées et incrémentées correctement ; "
     "le mouvement est tracé."),
    ("H09", "H", 3, "Ventes au POS sur des articles stockés",
     "Vérifier la décrémentation automatique du stock",
     "1. Vendre un article au POS.\n2. Contrôler son stock.",
     "Le stock diminue de la quantité vendue, sans décalage ni double "
     "décrémentation."),

    # ══════════ I — ACHATS & FOURNISSEURS ══════════
    ("I01", "I", 1, "Fournisseur créé, articles référencés",
     "Créer un bon de commande fournisseur",
     "1. Achats → Créer une commande.\n2. Ajouter les articles et les "
     "quantités.\n3. Confirmer.",
     "La commande est confirmée avec un montant total exact en FCFA."),
    ("I02", "I", 1, "Commande fournisseur confirmée",
     "Réceptionner une commande complète",
     "1. Valider la réception des quantités commandées.",
     "Le stock est mis à jour et la commande passe au statut reçu."),
    ("I03", "I", 1, "Commande fournisseur confirmée",
     "Réceptionner partiellement une commande",
     "1. Réceptionner une quantité inférieure à la commande.",
     "L'écart est visible, le reliquat reste attendu, et le stock "
     "n'augmente que des quantités réellement reçues."),
    ("I04", "I", 1, "Réception effectuée",
     "Enregistrer la facture fournisseur et son échéance",
     "1. Créer la facture depuis la réception.\n2. Renseigner "
     "l'échéance.",
     "La facture est rattachée à la commande et apparaît dans "
     "l'échéancier à la bonne semaine."),
    ("I05", "I", 2, "Factures fournisseurs à diverses échéances",
     "Contrôler l'échéancier fournisseurs",
     "1. Ouvrir le tableau de bord Achats.",
     "Les montants échus et à venir sont classés correctement par "
     "semaine ; le total correspond aux dettes réelles."),
    ("I06", "I", 2, "Historique de prix d'achat sur un article",
     "Détecter une hausse de prix à la réception",
     "1. Réceptionner le même article à un prix supérieur.",
     "La variation est détectée et signalée avec l'ancien et le "
     "nouveau prix."),
    ("I07", "I", 2, "Plusieurs réceptions avec retards",
     "Calculer la ponctualité fournisseur (OTIF)",
     "1. Consulter l'indicateur OTIF.",
     "Le taux reflète les livraisons complètes et à l'heure sur la "
     "période."),
    ("I08", "I", 3, "Consignes de casiers en cours",
     "Suivre les consignes fournisseurs",
     "1. Consulter l'encours des consignes.",
     "Le montant des consignes à rendre est exact et évolue avec les "
     "retours."),

    # ══════════ J — PILOTAGE VUE DIRECTION ══════════
    ("J01", "J", 1, "Données de ventes, crédit, stock et achats présentes",
     "Ouvrir la vue Direction sans erreur",
     "1. Menu Direction → Vue consolidée.\n2. Ouvrir la console du "
     "navigateur (F12).",
     "L'écran s'affiche entièrement, sans erreur JavaScript en "
     "console, et tous les onglets sont accessibles."),
    ("J02", "J", 1, "Ventes sur plusieurs périodes",
     "Filtrer par période",
     "1. Appliquer successivement Aujourd'hui, Cette semaine, Ce mois "
     "et une période personnalisée.",
     "Les indicateurs se recalculent à chaque changement et "
     "correspondent aux ventes de la période choisie."),
    ("J03", "J", 1, "Deux caisses avec des ventes distinctes",
     "Filtrer par caisse",
     "1. Sélectionner une seule caisse, puis toutes.",
     "Les chiffres filtrés correspondent à la caisse sélectionnée ; le "
     "total consolidé est retrouvé sans filtre."),
    ("J04", "J", 1, "Ventes réparties sur la journée",
     "Filtrer par tranche horaire et par jour",
     "1. Appliquer une tranche (soir) puis un jour de la semaine.",
     "Seules les ventes de la tranche ou du jour sélectionné sont "
     "prises en compte."),
    ("J05", "J", 1, "Ardoises en retard et coulage constaté",
     "Vérifier le calcul du cash à risque",
     "1. Relever la valeur affichée.\n2. La comparer à la somme des "
     "ardoises de plus de 30 jours et du coulage estimé.",
     "La valeur affichée correspond au calcul attendu et n'est jamais "
     "négative."),
    ("J06", "J", 1, "Encours clients et dettes fournisseurs connus",
     "Vérifier le solde crédits − dettes",
     "1. Relever l'indicateur et le comparer aux tableaux de bord "
     "Crédit et Achats.",
     "Le solde correspond exactement à la différence entre les deux "
     "encours."),
    ("J07", "J", 2, "Données sur plusieurs semaines",
     "Contrôler la cohérence des tendances",
     "1. Comparer la courbe de tendance aux chiffres détaillés.",
     "La tendance et le pourcentage d'évolution reflètent les données "
     "réelles de la période."),
    ("J08", "J", 2, "Situations à traiter présentes (retards, ruptures)",
     "Vérifier la liste d'actions « À traiter »",
     "1. Ouvrir l'onglet À traiter.",
     "Les actions proposées (relancer, payer, commander) correspondent "
     "à des situations réelles et sont priorisées."),
    ("J09", "J", 2, "Vue Direction ouverte",
     "Naviguer du chiffre vers le détail",
     "1. Cliquer sur un indicateur pour ouvrir le tableau de bord "
     "spécialisé.",
     "L'écran détaillé s'ouvre sur le bon périmètre, avec des chiffres "
     "cohérents avec le cockpit."),
    ("J10", "J", 2, "Écran affiché sur un poste de travail",
     "Vérifier le défilement et l'affichage",
     "1. Faire défiler la page jusqu'en bas sur chaque onglet.",
     "Le contenu défile correctement, les filtres restent visibles, "
     "aucun bloc n'est coupé."),

    # ══════════ K — TABLEAU DE BORD EXÉCUTIF ══════════
    ("K01", "K", 2, "Activité hôtelière enregistrée",
     "Ouvrir le tableau de bord exécutif",
     "1. Ouvrir le tableau de bord.\n2. Contrôler la console (F12).",
     "L'écran s'affiche sans erreur et les indicateurs sont "
     "renseignés."),
    ("K02", "K", 2, "Séjours et réservations sur la période",
     "Contrôler les indicateurs d'occupation",
     "1. Comparer le taux d'occupation affiché au planning réel.",
     "Le taux et le nombre de nuitées correspondent aux séjours "
     "enregistrés."),
    ("K03", "K", 3, "Plusieurs périodes disponibles",
     "Filtrer la période du tableau de bord",
     "1. Changer la période analysée.",
     "Les indicateurs se recalculent de façon cohérente."),
    ("K04", "K", 3, "Données hôtel et bar présentes",
     "Vérifier la cohérence avec la vue Direction",
     "1. Comparer les chiffres communs aux deux écrans.",
     "Les valeurs communes sont identiques d'un écran à l'autre."),

    # ══════════ L — JEU DE DÉMONSTRATION ══════════
    ("L01", "L", 2, "Base vierge dédiée à la démonstration",
     "Installer le jeu de démonstration",
     "1. Installer aite_demo_data sur une base de test.",
     "L'installation aboutit sans erreur et charge un établissement "
     "complet (chambres, produits, clients, historique)."),
    ("L02", "L", 2, "Jeu de démonstration installé",
     "Vérifier que tous les écrans sont alimentés",
     "1. Parcourir planning, caisse, crédit, fidélité, stock, achats "
     "et Direction.",
     "Chaque écran présente des données réalistes, en FCFA, sans zone "
     "vide."),
    ("L03", "L", 3, "Base de production",
     "Vérifier l'absence de données de démonstration en production",
     "1. Contrôler que le module n'est pas installé sur la base de "
     "production.",
     "Aucune donnée fictive n'apparaît dans l'environnement réel."),

    # ══════════ M — TRANSVERSE ══════════
    ("M01", "M", 1, "Les 12 modules déposés sur le serveur",
     "Installer la suite complète dans l'ordre prévu",
     "1. Suivre la procédure d'installation du fichier "
     "INSTALLATION.md.\n2. Installer les modules dans l'ordre "
     "indiqué.",
     "Tous les modules s'installent sans erreur ; aucun message "
     "d'échec dans le log Odoo."),
    ("M02", "M", 1, "Suite installée",
     "Ouvrir l'écran Paramètres en entier",
     "1. Paramètres → faire défiler jusqu'en bas.",
     "L'écran s'affiche complètement, toutes les sections AITE sont "
     "présentes, sans erreur « field is undefined »."),
    ("M03", "M", 1, "Profils utilisateurs créés (serveur, gérant)",
     "Vérifier le cloisonnement des droits",
     "1. Se connecter en profil serveur, puis en profil gérant.",
     "Le serveur n'accède ni aux marges ni aux tableaux de bord de "
     "direction ; le gérant accède à l'ensemble."),
    ("M04", "M", 1, "Société configurée en FCFA",
     "Contrôler la devise et les arrondis",
     "1. Vérifier les montants sur un ticket, une facture et un "
     "tableau de bord.",
     "Tous les montants sont en FCFA, sans décimale parasite ni "
     "erreur d'arrondi."),
    ("M05", "M", 2, "Suite installée et utilisée",
     "Redémarrer le serveur et recharger l'application",
     "1. Redémarrer le service Odoo.\n2. Ctrl+Shift+R dans le "
     "navigateur.",
     "Aucune régression après redémarrage ; les écrans se rechargent "
     "normalement."),
    ("M06", "M", 2, "Données réelles d'un mois d'activité",
     "Vérifier les temps de réponse",
     "1. Ouvrir les principaux tableaux de bord sur un mois complet.",
     "Chaque écran s'affiche en moins de 5 secondes dans des "
     "conditions normales d'exploitation."),
    ("M07", "M", 2, "Base de production active",
     "Vérifier la sauvegarde et la restauration",
     "1. Réaliser une sauvegarde.\n2. La restaurer sur une base de "
     "test.",
     "La restauration aboutit et les données sont intègres et "
     "complètes."),
    ("M08", "M", 2, "Tableaux de bord alimentés",
     "Exporter des données en Excel et PDF",
     "1. Exporter une liste et un tableau de bord.",
     "Les exports s'ouvrent correctement et contiennent les données "
     "affichées à l'écran."),
    ("M09", "M", 3, "Utilisateur sur poste et sur tablette",
     "Vérifier l'usage sur tablette",
     "1. Ouvrir la caisse et les principaux écrans sur tablette.",
     "Les écrans sont utilisables au doigt, sans élément inaccessible."),
    ("M10", "M", 1, "Un module mis à jour",
     "Mettre à niveau un module sans perte de données",
     "1. Remplacer le dossier d'un module.\n2. Apps → Mettre à "
     "niveau.\n3. Contrôler les données existantes.",
     "La mise à niveau aboutit et aucune donnée antérieure n'est "
     "perdue ni altérée."),
    # ══════════ N — TAXE DE SÉJOUR ══════════
    ("N01", "N", 1, "Hôtel avec pays et catégorie (étoiles) renseignés",
     "Vérifier le barème appliqué sur la fiche hôtel",
     "1. Ouvrir la fiche de l'hôtel → onglet Taxe de séjour.",
     "Le barème du pays et de la catégorie s'affiche (ex. Cameroun 3 ★ : "
     "3 000 F) avec une phrase expliquant ce qui sera facturé."),
    ("N02", "N", 1, "Réservation 2 nuits, 2 adultes, hôtel 3 ★ Cameroun",
     "Taxe ajoutée automatiquement à la confirmation",
     "1. Confirmer la réservation.\n2. Ouvrir le folio.",
     "Une ligne « Taxe de séjour » apparaît sans saisie : 4 nuitées × "
     "3 000 F = 12 000 F, sans TVA ; le total « Services » ne l'inclut pas."),
    ("N03", "N", 1, "Folio ouvert avec taxe",
     "Recalcul si le séjour change",
     "1. Prolonger le séjour d'une nuit.\n2. Ajouter un adulte.\n"
     "3. Changer la catégorie de l'hôtel (4 ★) puis revenir.",
     "La ligne est recalculée à chaque changement ; une seule ligne de "
     "taxe subsiste ; le montant suit le barème."),
    ("N04", "N", 1, "Séjour facturé",
     "Gel après facturation",
     "1. Facturer le folio.\n2. Modifier la catégorie de l'hôtel.",
     "La facture porte la ligne de taxe sans TVA ; le folio facturé n'est "
     "plus recalculé."),
    ("N05", "N", 1, "Plusieurs séjours terminés sur le mois",
     "État mensuel à déclarer",
     "1. Facturation → Taxe de séjour.\n2. Regrouper par mois.",
     "Le tableau donne, par mois et par hôtel, les nuitées taxées et le "
     "montant collecté ; le total correspond aux folios ; export Excel OK."),
    ("N06", "N", 2, "Hôtel exonéré",
     "Désactiver la collecte",
     "1. Décocher « Collecter la taxe de séjour » sur l'hôtel.",
     "Les folios ouverts perdent leur ligne de taxe ; les facturés ne "
     "bougent pas ; l'onglet affiche « désactivée »."),
    ("N07", "N", 2, "Pays sans barème (ex. Tchad)",
     "Message guidant vers la configuration",
     "1. Créer un hôtel dans un pays non couvert.",
     "Aucune taxe appliquée ; l'onglet indique où ajouter le barème ; "
     "l'ajout d'un barème l'active."),
    ("N08", "N", 2, "Nouvelle loi de finances",
     "Modifier un montant de barème",
     "1. Configuration → Barèmes → changer un montant.\n2. Confirmer une "
     "nouvelle réservation.",
     "Le nouveau montant s'applique aux nouveaux folios ; l'ancien reste "
     "sur les folios facturés."),

    # ══════════ O — REGISTRE DES CLIENTS ══════════
    ("O01", "O", 1, "Client avec pièce et nationalité sur sa fiche contact",
     "Fiche créée et pré-remplie au check-in",
     "1. Faire le check-in.\n2. Observer la réservation.",
     "Une fiche d'enregistrement existe pour le client principal, "
     "pré-remplie (nom, pièce, nationalité, dates) ; un bandeau indique ce "
     "qu'il reste à faire ; bouton « Fiches d'enregistrement x/y »."),
    ("O02", "O", 1, "Fiche pré-remplie incomplète",
     "Compléter la fiche jusqu'à « Complète »",
     "1. Cliquer « compléter maintenant ».\n2. Renseigner la date de "
     "naissance.",
     "La colonne « Il manque » disparaît et la fiche passe « Complète » "
     "sans bouton ; le bandeau devient vert quand tous les occupants sont "
     "enregistrés."),
    ("O03", "O", 1, "Séjour à 2 occupants",
     "Ajouter un accompagnant",
     "1. Dans la fenêtre Fiches d'enregistrement, ajouter une ligne pour "
     "l'accompagnant (étranger).",
     "La fiche est complète d'emblée ; « Registre à jour 2/2 » ; le "
     "non-résident est identifié."),
    ("O04", "O", 1, "Fiche complète",
     "Imprimer la fiche d'enregistrement",
     "1. Cliquer l'icône imprimante (ou Imprimer la fiche).",
     "PDF avec identité, pièce, séjour, chambre, cases de signature client "
     "et établissement."),
    ("O05", "O", 1, "Plusieurs séjours sur une semaine",
     "Imprimer le registre de police sur une période",
     "1. Facturation → Registre de police (impression).\n2. Choisir les "
     "dates.\n3. Imprimer.",
     "Le registre liste chronologiquement toutes les personnes hébergées "
     "sur la période (A4 paysage) ; une période vide affiche un message "
     "clair."),
    ("O06", "O", 2, "Fiches complètes sur plusieurs mois",
     "Statistiques d'hébergement",
     "1. Facturation → Statistiques d'hébergement.\n2. Regrouper par "
     "nationalité, puis par motif.",
     "Arrivées, nuitées, résidents / non-résidents et répartitions "
     "correspondent aux fiches des clients arrivés ; export Excel."),
    ("O07", "O", 2, "Accompagnant sans fiche contact",
     "Mémoriser la pièce sur le contact",
     "1. Lier un contact à la fiche.\n2. « Mémoriser sur la fiche "
     "client ».",
     "Le contact porte désormais pièce et nationalité : la prochaine "
     "réservation sera pré-remplie."),
    ("O08", "O", 2, "Utilisateur Gouvernante",
     "Droits de lecture seule",
     "1. Se connecter en Gouvernante.\n2. Ouvrir le registre.",
     "Lecture possible, modification refusée."),

    # ══════════ P — GOUVERNANTE & MAINTENANCE ══════════
    ("P01", "P", 1, "Chambres dans divers états",
     "Lire le tableau des chambres sans formation",
     "1. Gouvernante → Tableau des chambres.",
     "Toutes les chambres sont visibles, classées À nettoyer / En cours / "
     "À inspecter / Propre ; chaque carte dit quoi faire, le client, "
     "l'équipière ; un bouton par étape."),
    ("P02", "P", 1, "Chambres à nettoyer non affectées, 2 équipières",
     "Répartir les chambres du jour",
     "1. Gouvernante → Répartir les chambres du jour.\n2. Cocher les "
     "équipières.\n3. Répartir.",
     "Les tâches sont distribuées à tour de rôle ; sans équipière cochée, "
     "message clair."),
    ("P03", "P", 1, "Équipière connectée sur téléphone",
     "Ma journée : commencer et terminer",
     "1. Ouvrir « Ma journée ».\n2. « Je commence » puis « C'est fait ».",
     "Elle ne voit que ses chambres ; la chambre passe « Nettoyage en "
     "cours » puis « Propre » ; durée mesurée."),
    ("P04", "P", 1, "Inspection après recouche activée",
     "Inspection avec checklist",
     "1. Après recouche, ouvrir l'inspection.\n2. Laisser un point non "
     "coché avec remarque.\n3. Valider.",
     "La chambre repasse « À nettoyer » avec une tâche URGENTE reprenant "
     "la remarque, affectée à la même équipière ; une inspection conforme "
     "la rend propre."),
    ("P05", "P", 1, "Chambre libre",
     "Signaler une panne qui bloque la chambre",
     "1. Sur la carte, clé → « Signaler un problème ».\n2. Cocher "
     "« chambre invendable ».",
     "Demande créée dans Pannes & réparations ; chambre hors service, "
     "indisponible à la réservation ; badge de panne sur la carte."),
    ("P06", "P", 1, "Demande bloquante ouverte",
     "Remise en vente automatique après réparation",
     "1. Passer la demande en « Réparé ».",
     "La chambre revient en service, « À nettoyer », avec une tâche de "
     "remise en service ; plus de panne ouverte."),
    ("P07", "P", 2, "Chambre occupée",
     "Panne sur chambre occupée",
     "1. Signaler une panne bloquante sur une chambre occupée.",
     "La demande est créée mais la chambre n'est pas mise hors service."),
    ("P08", "P", 2, "Objet oublié trouvé en chambre",
     "Objets trouvés",
     "1. Gouvernante → Objets trouvés → créer.\n2. Choisir la chambre.\n"
     "3. « Rendu au client ».",
     "Le séjour est deviné depuis la chambre et la date ; le statut passe "
     "« Rendu » daté."),
    ("P09", "P", 3, "Responsable",
     "Personnaliser la checklist d'inspection",
     "1. Configuration → Points de contrôle.\n2. Ajouter un point.",
     "Les nouvelles inspections incluent le point ajouté."),

    # ══════════ Q — INDICATEURS HÔTELIERS (F06) ══════════
    ("Q01", "Q", 1, "Séjours confirmés sur la période, 2 chambres ou plus",
     "Lire le taux d'occupation, l'ADR et le RevPAR",
     "1. Hôtel → Activité par pôle.\n2. Période « Ce mois ».\n3. Lire la rangée "
     "« Hébergement — indicateurs de performance ».",
     "TO = nuitées vendues ÷ (chambres en service × jours) ; ADR = CA "
     "des nuitées ÷ nuitées vendues ; RevPAR = CA des nuitées ÷ chambres "
     "disponibles, et RevPAR = ADR × TO. Une chambre hors service ne "
     "compte pas comme disponible."),
    ("Q02", "Q", 2, "Tableau exécutif ouvert",
     "Comprendre un indicateur sans formation",
     "1. Survoler le « ? » de chaque carte (TO, ADR, RevPAR, pickup, "
     "pace).",
     "Chaque carte affiche une phrase en français qui dit ce que mesure "
     "l'indicateur ; celle du RevPAR précise « chaque chambre "
     "disponible, vendue ou non »."),
    ("Q03", "Q", 2, "Séjours sur la même période l'année précédente",
     "Comparer avec l'an dernier",
     "1. Choisir une période qui a un historique N-1.\n2. Lire l'écart "
     "sous TO, ADR et RevPAR.",
     "Un écart en % s'affiche, vert s'il est positif, rouge s'il est "
     "négatif ; sans historique N-1, aucun écart n'est affiché (pas de "
     "« 0 % » trompeur)."),
    ("Q04", "Q", 2, "Réservations prises cette semaine pour le mois à venir",
     "Lire le pickup",
     "1. Créer et confirmer une réservation pour dans 10 jours.\n2. "
     "Recharger le tableau exécutif.",
     "La carte « Réservations récentes (pickup) » augmente du nombre de nuits de la "
     "réservation ; une réservation pour dans 40 jours ne le change "
     "pas."),
    ("Q05", "Q", 3, "Réservations du mois en cours et historique N-1",
     "Lire le pace du mois",
     "1. Lire la carte « Rythme du mois (pace) ».",
     "Elle donne les nuitées déjà réservées pour le mois, et celles qui "
     "l'étaient à la même date l'an dernier pour le même mois ; une "
     "réservation N-1 prise après cette date n'est pas comptée."),
    ("Q06", "Q", 1, "Modules hôtel et Direction installés",
     "Retrouver les mêmes chiffres dans le cockpit Direction",
     "1. Hôtel → Activité par pôle (tableau exécutif) : noter TO, ADR, RevPAR.\n"
     "2. Direction → Vue d'ensemble, même période.\n3. Cliquer une carte "
     "de la rangée « Hébergement ».",
     "TO, ADR et RevPAR sont identiques sur les deux écrans ; le clic "
     "ouvre le tableau de bord exécutif."),
    ("Q07", "Q", 1, "Base neuve, administrateur sans réglage de droits",
     "Ouvrir le cockpit Direction au premier clic",
     "1. Se connecter en administrateur.\n2. Ouvrir Direction → Vue "
     "d'ensemble, puis chaque onglet.",
     "Aucune erreur d'accès : l'administrateur reçoit d'office les "
     "profils Manager (Analyses POS) et Responsable (Crédit clients)."),

    # ══════════ R — RESTAURANT, SERVICE À TABLE (LOT 1) ══════════
    # Un cas par critère d'acceptation du lot 1 (périmètre, partie 3 ;
    # spécification « Restaurant, lot 1 »). Rôles : un serveur, la
    # caissière, un chef de salle, le manager (Employés → « Niveau en
    # caisse »). La caisse « Restaurant » est au service à table contrôlé,
    # ouverte sous le compte de la caisse sur chaque tablette.
    ("R01", "R", 1, "Caisse ouverte, plan affiché, personne d'identifié",
     "REST-01 c.1 — Aucune table sans code",
     "1. Toucher une table du plan.\n2. Toucher « Retour » sans taper de code.",
     "La fenêtre « Table n — votre code » s'ouvre (quatre points, un pavé) ; "
     "sans code, aucune table ne s'ouvre et le plan reste affiché, "
     "verrouillé."),
    ("R02", "R", 1, "Un serveur avec un niveau et un code",
     "REST-01 c.2 — Le code identifie l'employé",
     "1. Toucher une table libre.\n2. Taper son code (4 chiffres).\n"
     "3. Toucher le nombre de personnes.",
     "Le code est validé seul au 4ᵉ chiffre ; l'écran de commande s'ouvre, "
     "le nom du serveur est en haut ; un code faux vide les points et "
     "affiche « Code inconnu. Retapez votre code. »."),
    ("R03", "R", 1, "Compte du manager (Employés : Gestionnaire)",
     "REST-01 c.3 — Code obligatoire et unique",
     "1. Employés → Nouveau : nom, « Niveau en caisse » = Serveur.\n"
     "2. Vider le code, enregistrer.\n3. Taper 3 chiffres, enregistrer.\n"
     "4. Taper le code d'un collègue, enregistrer.",
     "Un code de 4 chiffres est proposé dès le niveau choisi, sur la "
     "première page, sans courriel demandé ; chaque enregistrement fautif "
     "est refusé et le message dit quoi corriger, sans jamais nommer le "
     "collègue dont le code est pris."),
    ("R04", "R", 1, "Une table ouverte par un serveur",
     "REST-02 c.1 — Ouverte par, encaissée par",
     "1. La caissière touche la table, tape son code, « J'encaisse », "
     "Espèces, Valider.\n2. Point de Vente → Commandes → ouvrir l'addition.",
     "La fiche indique « Ouverte par » : le serveur, « Encaissée par » : la "
     "caissière, et l'heure d'ouverture ; « Ouverte par » n'a pas changé."),
    ("R05", "R", 1, "Un serveur identifié sur l'écran de commande",
     "REST-02 c.2 — Le code est demandé avant d'encaisser",
     "1. Toucher « J'encaisse ».\n2. Taper le code du serveur.\n"
     "3. Taper le code de la caissière.",
     "La fenêtre « Code de la personne qui encaisse » s'ouvre, sous-titre « … "
     "ne peut pas encaisser : la caissière tape son code ici. » ; le code du "
     "serveur est refusé (« Vous ne pouvez pas encaisser. Appelez la "
     "caissière : elle tapera son code ici. ») ; celui de la caissière ouvre "
     "le paiement."),
    ("R06", "R", 2, "Une table où deux employés ont saisi des produits",
     "REST-02 c.3 — Qui a saisi quoi",
     "1. Point de Vente → Commandes → ouvrir l'addition.\n"
     "2. Bouton « Saisies ».",
     "Une ligne par ajout : produit, quantité ajoutée, nom de l'employé, "
     "heure ; ni une division ni une réunion de tables n'y ajoutent de "
     "ligne."),
    ("R07", "R", 2, "Des additions encaissées sur la période",
     "REST-02 c.4 — Regrouper par « Ouverte par » et « Encaissée par »",
     "1. Point de Vente → Analyse → Personnes et tables.\n2. Regrouper par "
     "« Ouverte par », puis par « Encaissée par ».",
     "Les tables, personnes et montants se lisent par serveur, puis par "
     "personne qui a encaissé."),
    ("R08", "R", 1, "Un serveur sur l'écran de commande",
     "REST-02 c.5 — Le code après chaque envoi",
     "1. Ajouter un produit, toucher « J'envoie ».\n2. Toucher de nouveau "
     "la table.",
     "Après « J'envoie » : notification « Envoyé : … », retour au plan, plus "
     "aucun nom en haut ; toucher la table redemande le code."),
    ("R09", "R", 1, "Un produit envoyé sur la table d'un serveur",
     "REST-03 c.1 — Un serveur n'annule pas seul",
     "1. Le serveur touche la ligne, puis ⌫ ⌫.",
     "La fenêtre d'annulation s'ouvre : « Déjà envoyé : … Pour l'annuler, un "
     "chef de salle tape son code. », puis « Code d'un chef de salle » ; "
     "rien n'est retiré sans ce code."),
    ("R10", "R", 1, "Un employé de chaque niveau",
     "REST-03 c.2 — Le tableau des droits, niveau par niveau",
     "1. Avec chaque code, essayer : ouvrir la caisse, encaisser, imprimer "
     "le rapport, sortir des espèces, fermer la caisse, annuler un produit "
     "envoyé, rembourser, changer un prix.",
     "Serveur : refusé partout, avec le message du geste ; caissière : "
     "ouvre, encaisse, imprime le rapport ; chef de salle : en plus, espèces, "
     "annulation et fermeture ; manager : tout, y compris rembourser et le "
     "prix."),
    ("R11", "R", 2, "Un serveur, caisse fermée",
     "REST-03 c.3 — Le nouveau niveau s'applique à la réouverture",
     "1. Le manager passe l'employé en « Caissière ».\n2. Rouvrir la caisse "
     "(recharger la page).\n3. Avec son code, « J'encaisse ».",
     "Le paiement s'ouvre : le niveau changé s'applique dès la réouverture."),
    ("R12", "R", 2, "« Contrôle des prix » coché (posé par la case)",
     "REST-04 c.1 — Le prix au seul manager",
     "1. La caissière touche une ligne.\n2. Toucher « Prix ».\n3. Le manager "
     "prend la main (nom en haut, son code), touche « Prix ».",
     "Pour la caissière, la touche « Prix » est grisée et le prix ne change "
     "pas ; pour le manager, elle est active."),
    ("R13", "R", 2, "Compte du manager",
     "REST-04 c.2 — Le manager crée un produit",
     "1. Point de Vente → Produits → Nouveau : nom, prix en FCFA, "
     "catégorie du PdV.\n2. Recharger la caisse.",
     "Le produit est proposé dans sa famille à l'écran de commande."),
    ("R14", "R", 2, "Un serveur identifié",
     "REST-04 c.3 — Pas de configuration ni de rapport pour un serveur",
     "1. Ouvrir le menu ≡.\n2. Toucher « Imprimer le rapport » (s'il y a une "
     "imprimante), « Entrée ou sortie d'espèces », « Fermer la caisse ».",
     "Le menu ne propose que Commandes, Entrée ou sortie d'espèces, Fermer "
     "la caisse (et Imprimer le rapport avec une imprimante) ; chaque geste "
     "réservé est refusé au serveur avec son message ; pas de « Modifier le "
     "plan »."),
    ("R15", "R", 1, "Un serveur qui vient de taper son code",
     "REST-05 c.1 — Le numéro, puis les personnes, avant tout produit",
     "1. Toucher une table libre du plan, taper son code.",
     "La fenêtre enchaîne « Table n — combien de personnes ? » ; aucun "
     "produit ne peut être saisi avant."),
    ("R16", "R", 1, "Plan affiché",
     "REST-05 c.2 — La table touchée s'ouvre à son nom",
     "1. Toucher la table 12, taper son code, choisir les personnes.",
     "L'écran de commande s'ouvre sur la table 12 : « Table 12 · ouverte "
     "par … · 0 min »."),
    ("R17", "R", 2, "Plan affiché",
     "REST-05 c.3 — Le numéro tapé au clavier",
     "1. Bouton « Table » de la barre, taper 12, valider.\n2. Taper son "
     "code.",
     "La table 12 s'ouvre ; la fenêtre du clavier propose « Retour » (jamais "
     "« Discard »)."),
    ("R18", "R", 2, "Aucune table 99 sur le plan",
     "Q25 — Un numéro qui n'est pas sur le plan",
     "1. Bouton « Table », taper 99, valider.\n2. Taper son code, choisir "
     "2 personnes.",
     "Une table « 99 » s'ouvre à 2 personnes et compte comme une table "
     "(le refus d'un numéro inconnu est au lot 2)."),
    ("R19", "R", 3, "Caisse fermée ; réglage « Autoriser la vente sans "
     "table »",
     "REST-05 c.5 — La vente sans table (option)",
     "1. Réglage décoché : regarder la barre du plan.\n2. AITE le coche "
     "(caisse fermée), rouvrir la caisse.\n3. Un serveur, puis la caissière, "
     "touchent « + ».",
     "Décoché : pas de « + ». Coché : la caissière ouvre une vente sans table "
     "ni personnes (0 personne) ; le serveur est refusé (« La vente sans "
     "table n'est pas ouverte ici. Ouvrez une table du plan. »)."),
    ("R20", "R", 1, "Une table libre",
     "REST-06 c.1 — Les personnes avant tout produit",
     "1. Toucher la table, taper son code.",
     "Huit gros boutons 1 à 8 et « 9 et plus » ; l'écran de commande ne "
     "s'ouvre qu'après le choix."),
    ("R21", "R", 1, "L'étape des personnes est affichée",
     "REST-06 c.2 — Sans nombre, la table ne s'ouvre pas",
     "1. Toucher « 9 et plus », ne rien taper.\n2. Toucher « Retour ».",
     "« Valider » reste grisé (« Il faut au moins une personne à table. ») ; "
     "« Retour » ramène au plan, la table reste libre."),
    ("R22", "R", 2, "L'étape des personnes est affichée",
     "REST-06 c.3 — Zéro n'existe pas",
     "1. Chercher un bouton 0.\n2. « 9 et plus », taper 0.",
     "Aucun bouton 0 ; 0 tapé laisse « Valider » grisé."),
    ("R23", "R", 1, "Une table ouverte pour 4 personnes",
     "REST-06 c.4 — Le nombre est sur l'addition",
     "1. Regarder la rangée de boutons de l'écran de commande.\n2. Ouvrir "
     "l'addition dans Point de Vente → Commandes.",
     "Le bouton indique « 4 personnes » ; la fiche de l'addition indique 4 "
     "convives."),
    ("R24", "R", 1, "Une table ouverte pour 4, sans produit",
     "REST-06 c.5 — Occupée dès la validation",
     "1. Revenir au plan (« Plan »).\n2. Regarder le plan sur un autre "
     "poste.",
     "La table est verte, avec sa durée, sur les deux postes ; un autre "
     "serveur qui la touche est refusé (c'est la table d'un collègue)."),
    ("R25", "R", 3, "Une table divisée ; la table 9 libre",
     "REST-06 c.6 — Une part portée sur une table libre",
     "1. « Déplacer ou réunir » la part (« 12B ») vers la table 9.",
     "Le nombre de personnes de la table 9 est demandé."),
    ("R26", "R", 1, "Une table ouverte pour 5 personnes",
     "REST-07 c.1 — Corriger le nombre en deux touches",
     "1. Toucher « 5 personnes ».\n2. Toucher 7 (« 9 et plus » au-delà de "
     "8).",
     "Le bouton indique « 7 personnes »."),
    ("R27", "R", 2, "Cette table encaissée",
     "REST-07 c.2 — Le rapport compte le nombre corrigé",
     "1. Point de Vente → Analyse → Personnes et tables (Aujourd'hui).",
     "La table compte pour 7 personnes."),
    ("R28", "R", 2, "Une table qui porte des produits",
     "REST-07 c.3 — Zéro refusé en cours de repas",
     "1. Toucher « 7 personnes » et chercher 0.",
     "Aucun moyen de saisir 0 personne : la table garde son nombre."),
    ("R29", "R", 2, "La carte rangée en familles par le manager",
     "REST-09 c.1 — Les familles à l'ouverture d'une table",
     "1. Ouvrir une table.",
     "L'écran de commande montre les familles racines Nourriture et "
     "Boisson."),
    ("R30", "R", 2, "Écran de commande ouvert",
     "REST-09 c.2 — Les sous-familles",
     "1. Toucher Boisson.",
     "Alcoolisé et Non alcoolisé apparaissent."),
    ("R31", "R", 2, "Boisson > Alcoolisé affiché",
     "REST-09 c.3 — Une sous-sous-famille",
     "1. Toucher Bière.",
     "Seules les bières sont proposées."),
    ("R32", "R", 3, "Une sous-famille affichée",
     "REST-09 c.4 — Remonter d'un niveau",
     "1. Retoucher la famille active.",
     "La caisse remonte d'un niveau."),
    ("R33", "R", 3, "Compte du manager",
     "REST-09 c.5 — Un produit rangé dans « Vin »",
     "1. Ranger un produit dans la catégorie du PdV « Vin ».\n2. Recharger "
     "la caisse.",
     "Le produit apparaît sous Boisson > Alcoolisé > Vin."),
    ("R34", "R", 1, "Un produit saisi, pas encore envoyé",
     "REST-10 c.1 — Retirer ce qui n'est pas parti",
     "1. Toucher la ligne, ⌫, ⌫.",
     "La ligne disparaît, sans code ni trace."),
    ("R35", "R", 1, "Un produit envoyé",
     "REST-10 c.2 — Ce qui est parti ne se retire plus",
     "1. Toucher la ligne, taper un chiffre plus petit.\n2. ⌫, ⌫.",
     "Le chiffre plus petit est ignoré ; ⌫ ⌫ ouvre la fenêtre d'annulation "
     "qui demande le code d'un chef de salle."),
    ("R36", "R", 1, "Trois bières envoyées, une quatrième saisie",
     "REST-10 c.3 — La 4ᵉ part librement",
     "1. ⌫, ⌫ sur la ligne des bières.\n2. ⌫, ⌫ encore.",
     "La 4ᵉ est retirée librement, les trois envoyées restent ; la seconde "
     "fois, la fenêtre d'annulation s'ouvre."),
    ("R37", "R", 1, "Une famille sans imprimante de préparation",
     "REST-10 c.4 — Verrouillé même sans imprimante",
     "1. Envoyer un produit de cette famille.\n2. ⌫, ⌫.",
     "La fenêtre d'annulation s'ouvre, comme pour les autres produits."),
    ("R38", "R", 1, "Un produit envoyé depuis un poste",
     "REST-10 c.5 — Même refus sur un autre poste ou après rechargement",
     "1. Sur un autre poste (ou après Ctrl+F5), ouvrir la table.\n2. ⌫, ⌫ "
     "sur la ligne envoyée.",
     "La fenêtre d'annulation s'ouvre de la même façon."),
    ("R39", "R", 1, "Une table qui porte des produits envoyés",
     "REST-10 c.6 — Annuler une table entière",
     "1. Actions → « Annuler la table ».\n2. Recommencer depuis ≡ → "
     "Commandes → corbeille.",
     "La fenêtre « Annuler la table n » s'ouvre directement (code d'un chef "
     "de salle, motif), sans la confirmation d'Odoo ; avec le code et le "
     "motif, la table est libérée et chaque produit est tracé."),
    ("R40", "R", 1, "Un produit envoyé",
     "REST-10 c.7 — Pas de remise pour le ramener à zéro",
     "1. Toucher la ligne, regarder la touche « % ».",
     "La touche « % » est grisée pour tous : aucune remise n'est proposée."),
    ("R41", "R", 1, "Des produits envoyés sur deux tables",
     "REST-10 c.8 — Diviser et déplacer restent libres",
     "1. Actions → « Diviser l'addition ».\n2. Actions → « Déplacer ou "
     "réunir » vers l'autre table.",
     "Aucune fenêtre d'annulation, aucune ligne dans Restaurant → "
     "Annulations."),
    ("R42", "R", 1, "Deux tables encore ouvertes avec des produits envoyés",
     "REST-10 c.9 — Fermer la caisse avec des tables ouvertes",
     "1. ≡ → Fermer la caisse, code d'un chef de salle, espèces comptées, "
     "« Fermer la caisse ».\n2. « Annuler ces tables », toucher un motif.",
     "Message « 2 tables sont encore ouvertes : … Encaissez-les, ou "
     "annulez-les avec un motif, avant de fermer. » ; le motif seul suffit "
     "(le code est déjà tapé) ; chaque produit est tracé « Fermeture », la "
     "caisse se ferme."),
    ("R43", "R", 1, "Un produit envoyé ; un chef de salle ; une imprimante "
     "de cuisine",
     "REST-11 c.1 — Le code du chef de salle annule",
     "1. ⌫ ⌫ sur la ligne, « Combien ? » si besoin.\n2. Le chef de salle "
     "tape son code, touche un motif.",
     "Notification « Annulation faite : 1 … , par … » ; la quantité baisse ; "
     "un bon d'annulation part en cuisine (« Bon d'annulation envoyé. »)."),
    ("R44", "R", 2, "Après l'annulation (R43)",
     "REST-11 c.2 — Le serveur reste identifié",
     "1. Regarder le nom en haut de l'écran.",
     "Le nom du serveur est toujours en haut : il continue sa table."),
    ("R45", "R", 1, "La fenêtre d'annulation ouverte",
     "REST-11 c.3 — Le code d'un serveur ou d'une caissière ne suffit pas",
     "1. Taper le code d'un serveur.\n2. Taper celui de la caissière.",
     "Refusé à chaque fois : « Ce code ne peut pas annuler. Il faut celui "
     "d'un chef de salle, d'un superviseur ou du manager. »."),
    ("R46", "R", 1, "Une annulation faite (R43)",
     "REST-11 c.4 — La trace dit qui a demandé et qui a autorisé",
     "1. Restaurant → Annulations.",
     "« Demandée par » : le serveur ; « Autorisée par » : le chef de salle."),
    ("R47", "R", 1, "Des annulations dans la journée",
     "REST-12 c.1 — Ce que lit le manager",
     "1. Restaurant → Annulations (Aujourd'hui d'office).",
     "Chaque ligne donne la date et l'heure, la table, le produit, la "
     "quantité, le montant en FCFA, demandée par, autorisée par, le motif "
     "et la précision ; les totaux sont en bas."),
    ("R48", "R", 1, "Une division, un déplacement, une réunion faits",
     "REST-12 c.2 — Les déplacements ne sont pas des annulations",
     "1. Restaurant → Annulations.",
     "Aucune ligne pour ces gestes."),
    ("R49", "R", 1, "Une ligne du journal des annulations",
     "REST-12 c.3 — Le journal ne se modifie pas",
     "1. Avec le compte du manager, puis de l'administrateur, tenter de "
     "modifier ou supprimer la ligne.",
     "Refusé pour tous : « Une annulation enregistrée ne se modifie pas et "
     "ne s'efface pas : c'est la trace demandée par le manager. »."),
    ("R50", "R", 1, "La fenêtre d'annulation, code tapé",
     "REST-12 c.4 — Pas d'annulation sans motif",
     "1. Toucher « Retour » sans motif.\n2. Rouvrir, toucher « Autre », "
     "valider sans précision.\n3. Écrire une précision, valider.",
     "Sans motif, rien n'est annulé ; « Autre » sans précision : « Écrivez "
     "en quelques mots pourquoi. » ; avec la précision, la ligne porte le "
     "motif et la précision."),
    ("R51", "R", 2, "Compte du manager",
     "REST-12 c.5 — Un motif ajouté est proposé aussitôt",
     "1. Point de Vente → Configuration → Motifs d'annulation → Nouveau.\n"
     "2. Annuler un produit sur la caisse, sans la recharger.",
     "Le nouveau motif est proposé dans la fenêtre d'annulation."),
    ("R52", "R", 2, "Une baisse d'un produit envoyé arrivée sans code "
     "(poste en retard, gestion)",
     "REST-12 — Ce qui arrive sans code est tracé",
     "1. Restaurant → Annulations, filtre « Sans code ».",
     "Une ligne « Retrait sans code » ou « Annulation sans code », sans "
     "« Autorisée par » ; la vente n'a jamais été bloquée."),
    ("R53", "R", 1, "Tables 4 et 5 occupées",
     "REST-13 c.1 — Réunir deux tables",
     "1. Sur la table 5 : Actions → « Déplacer ou réunir ».\n2. Toucher la "
     "table 4.",
     "La table 4 porte tous les produits des deux tables ; la table 5 est "
     "libre."),
    ("R54", "R", 2, "Produits envoyés sur les deux tables ; imprimante de "
     "cuisine",
     "REST-13 c.2 — Pas de bon renvoyé à la réunion",
     "1. Réunir les tables.",
     "Aucun bon n'est renvoyé en cuisine pour ces produits."),
    ("R55", "R", 1, "Une réunion faite",
     "REST-13 c.3 — Pas d'annulation à la réunion",
     "1. Restaurant → Annulations.",
     "Aucune ligne pour la table absorbée."),
    ("R56", "R", 2, "Une table de 3 personnes et une de 4",
     "REST-13 c.4 — Les personnes s'additionnent",
     "1. Réunir les deux tables.",
     "L'addition compte 7 personnes et garde l'heure d'ouverture la plus "
     "ancienne."),
    ("R57", "R", 1, "Table 5 avec six produits",
     "REST-14 c.1 — Diviser par produits",
     "1. Actions → « Diviser l'addition ».\n2. Choisir deux produits, "
     "« Créer l'addition à part ».",
     "Une addition « 5B » porte ces deux produits, la table 5 garde les "
     "quatre autres ; tout sélectionner est refusé (« Toute l'addition est "
     "sélectionnée : il n'y a rien à diviser. Encaissez la table "
     "directement. »)."),
    ("R58", "R", 1, "Produits déjà envoyés",
     "REST-14 c.2 — Pas de bon ni d'annulation à la division",
     "1. Diviser l'addition.",
     "Aucun bon renvoyé, aucune ligne dans Restaurant → Annulations."),
    ("R59", "R", 2, "L'addition « 5B » créée",
     "REST-14 c.3 — Après la part, la table reste ouverte",
     "1. Encaisser « 5B ».",
     "La caisse revient à la table 5, toujours ouverte avec ses quatre "
     "produits, même personne identifiée."),
    ("R60", "R", 2, "Tables 3 et 7 occupées",
     "REST-15 c.1 — Déplacer une bière vers une autre table",
     "1. Table 3 : « Diviser l'addition », choisir la bière, « Créer "
     "l'addition à part ».\n2. Sur la part : « Déplacer ou réunir » vers la "
     "table 7.",
     "La bière est sur l'addition de la 7 et plus sur celle de la 3 (en "
     "deux gestes)."),
    ("R61", "R", 2, "Table 9 libre",
     "REST-15 c.2 — Vers une table libre",
     "1. Diviser deux produits de la table 3, puis « Déplacer ou réunir » "
     "la part vers la table 9.",
     "La caisse demande les personnes de la table 9, qui devient occupée "
     "avec ces deux produits."),
    ("R62", "R", 1, "Produits envoyés",
     "REST-15 c.3 — Pas de bon ni d'annulation au déplacement",
     "1. Déplacer des produits envoyés.",
     "Aucun bon renvoyé, aucune ligne dans Restaurant → Annulations."),
    ("R63", "R", 1, "Salle dessinée (Point de Vente → Configuration → "
     "Plans de salle)",
     "REST-16 c.1 — Le plan est l'écran de repos",
     "1. Ouvrir la caisse sur une tablette.",
     "Le plan s'affiche avec toutes les tables et leurs numéros, sans écran "
     "« Déverrouiller la caisse » ; phrase « Touchez une table, puis tapez "
     "votre code. »."),
    ("R64", "R", 1, "Une table ouverte pour 4, sans produit",
     "REST-16 c.2 — Une table ouverte se distingue",
     "1. Regarder le plan.",
     "Elle est verte, les tables libres sont grises."),
    ("R65", "R", 2, "Un serveur",
     "REST-16 c.3 — Le plan ne se modifie pas depuis la caisse",
     "1. Chercher « Modifier le plan ».\n2. Glisser une table sur une autre.",
     "« Modifier le plan » n'est pas proposé ; glisser une table ne la "
     "déplace pas et ne relie pas deux tables."),
    ("R66", "R", 1, "Délai de la caisse : 60 minutes",
     "REST-17 c.1 — Verte, puis orange",
     "1. Ouvrir une table, ne plus toucher l'écran.\n2. Regarder à 59, puis "
     "à 61 minutes.",
     "Verte à 59 minutes ; orange au plus tard à 61 minutes, sans que "
     "personne n'ait touché l'écran ; la légende dit « Orange : ouverte "
     "depuis plus de 60 min, proposez l'addition »."),
    ("R67", "R", 1, "Un poste sur l'écran de commande",
     "REST-17 c.2 — Poste laissé seul 10 minutes",
     "1. Ne plus toucher l'écran pendant 10 minutes.",
     "Après 5 minutes, le poste revient au plan, verrouillé (choix écrit : "
     "écart à Q17) ; le plan et ses couleurs restent affichés, sans écran de "
     "veille."),
    ("R68", "R", 1, "Une table orange",
     "REST-17 c.3 — Encaissée, elle redevient libre",
     "1. La caissière l'encaisse.",
     "La table redevient grise, sans durée."),
    ("R69", "R", 2, "Caisse fermée ; compte d'AITE",
     "REST-17 c.4 — Un autre délai",
     "1. Réglages du Point de Vente → « Délai avant l'orange (minutes) » = "
     "90.\n2. Rouvrir la caisse.",
     "La phrase sous le réglage dit « plus de 90 minutes » dès la saisie ; "
     "à la réouverture, l'orange vient après 90 minutes."),
    ("R70", "R", 2, "Une table ouverte depuis 50 minutes",
     "REST-17 c.5 — La durée suit la première ouverture",
     "1. La déplacer, la diviser ou la réunir.",
     "La durée affichée reste comptée depuis la première ouverture."),
    ("R71", "R", 2, "Une table ouverte depuis 40 minutes",
     "REST-17 c.6 — La durée se lit sur la table",
     "1. Regarder le plan.",
     "« 40 min » sous le numéro ; à partir d'une heure, « 1 h 05 » ; la "
     "même durée dans la phrase d'état de l'écran de commande."),
    ("R72", "R", 1, "Un produit suivi (« Suivre l'inventaire »), stock nul",
     "REST-18 c.1 — Le stock de départ",
     "1. Fiche du produit → « Mettre à jour la quantité » : 24.",
     "Le stock vaut 24 ; la caisse le vend de nouveau en moins d'une "
     "minute."),
    ("R73", "R", 3, "Une saisie de stock faite",
     "REST-18 c.2 — La saisie est datée et signée",
     "1. Inventaire → Rapports → Historique des mouvements.",
     "La saisie est datée et porte le nom de celui qui l'a faite."),
    ("R74", "R", 3, "Des saisies dans la semaine",
     "REST-18 c.4 — Retrouver les saisies de la semaine",
     "1. Historique des mouvements, filtrer la semaine.",
     "Chaque saisie est retrouvée."),
    ("R75", "R", 1, "Un produit suivi dont le stock est nul",
     "REST-19 c.1 — Produit épuisé",
     "1. Le toucher sur l'écran de commande.\n2. Le lire au code-barres.\n"
     "3. Taper une quantité au pavé sur sa ligne.",
     "Refus titré « Produit épuisé » : « Plus de … en stock. Si la bouteille "
     "est bien là, demandez au manager d'enregistrer l'entrée de stock : la "
     "vente repassera aussitôt. » ; rien n'est ajouté."),
    ("R76", "R", 1, "Ce produit épuisé",
     "REST-19 c.2 — Vendable en moins d'une minute après une entrée",
     "1. Le manager enregistre une entrée de stock.\n2. Sans recharger la "
     "caisse, toucher le produit.",
     "La vente passe."),
    ("R77", "R", 1, "Un plat non suivi en stock",
     "REST-19 c.3 — Les plats se vendent toujours",
     "1. Toucher le plat.",
     "La vente passe."),
    ("R78", "R", 1, "Un produit suivi dont il reste 2 unités",
     "REST-19 c.4 — Ce qui est parti compte sur tous les postes",
     "1. Envoyer ces 2 unités sur une table non encaissée.\n2. Sur un autre "
     "poste, ajouter le produit.",
     "Refusé (« Produit épuisé ») au plus tard une minute après l'envoi."),
    ("R79", "R", 3, "Réseau coupé",
     "Q59 — Hors connexion, la caisse vend",
     "1. Couper le réseau, ajouter un produit suivi.",
     "La vente passe (aucun contrôle de stock hors connexion) ; annuler, "
     "ouvrir et fermer la caisse sont impossibles (« Pas de réseau : … »)."),
    ("R80", "R", 1, "Trois annulations dans la journée",
     "REST-22 c.1 — Le rapport du jour",
     "1. Restaurant → Annulations.",
     "Trois lignes et leur total (quantité, montant en FCFA)."),
    ("R81", "R", 2, "Ce rapport ouvert",
     "REST-22 c.2 — Sous-totaux par responsable ou par motif",
     "1. Regrouper par « Autorisée par », puis par motif ; vue croisée.",
     "Un sous-total par responsable, puis par motif."),
    ("R82", "R", 1, "Deux tables réunies, une table divisée, un produit "
     "déplacé dans la journée",
     "REST-22 c.3 — Les déplacements n'y figurent pas",
     "1. Lire le rapport des annulations.",
     "Aucun de ces gestes n'y figure."),
    ("R83", "R", 1, "Compte du chef de salle : « Restaurant : lecture des "
     "rapports » seul",
     "REST-22 c.4, AH-05 — Le chef de salle lit sans accès à la caisse",
     "1. Se connecter avec ce compte.\n2. Ouvrir Restaurant → Annulations.",
     "Le rapport s'ouvre ; ni le menu Point de Vente, ni les commandes, ni la "
     "configuration de la caisse ne lui sont accessibles."),
    ("R84", "R", 1, "Ventes de bières, de vins et de sodas",
     "REST-23 c.1 — Une famille additionne ses sous-familles",
     "1. Point de Vente → Analyse → Analyse AITE → Tableau croisé & "
     "graphique.\n2. Favori « Ventes par famille ».",
     "Lignes Famille > Sous-famille, une seule colonne « Total » (quatre "
     "mesures, pas de colonne par catégorie) : « Boisson » = Alcoolisé + Non "
     "alcoolisé, et chaque sous-famille la somme de ses produits."),
    ("R85", "R", 2, "Ce tableau ouvert",
     "REST-23 c.2 — Une seule famille",
     "1. Taper « Pizzas » dans la recherche, choisir « Famille ».",
     "Seules les pizzas, avec quantités et montants ; « Alcoolisé » tapé ne "
     "ramène pas « Non alcoolisé »."),
    ("R86", "R", 2, "Ce tableau ouvert",
     "REST-23 c.3 — Un seul produit",
     "1. Taper le nom d'un produit, choisir « Produit ».",
     "Seules les ventes de ce produit."),
    ("R87", "R", 2, "Ventes de la période",
     "REST-23 c.4 — Un produit compté une seule fois",
     "1. Comparer la somme des familles au total.",
     "La somme des familles est le total ; un produit rangé dans plusieurs "
     "familles ne compte que dans la première."),
    ("R88", "R", 2, "Ventes et annulations sur plusieurs semaines",
     "REST-24 c.1 — Cette semaine",
     "1. Personnes et tables, puis Annulations : filtre « Cette semaine ».",
     "Les chiffres du lundi à aujourd'hui."),
    ("R89", "R", 2, "Ventes en décembre 2026",
     "REST-24 c.2 — Une période libre",
     "1. Filtre de date : du 01/12/2026 au 15/12/2026.",
     "Seules les ventes de ces quinze jours sont comptées."),
    ("R90", "R", 2, "Une période sans vente",
     "REST-24 c.3 — Une période vide dit quoi faire",
     "1. Ouvrir Personnes et tables sur cette période.",
     "L'écran dit qu'il n'y a rien sur cette période et invite à la "
     "changer."),
    ("R91", "R", 1, "Trois tables encaissées de 2, 4 et 7 personnes pour "
     "130 000 FCFA",
     "REST-25 c.1 — Tables, personnes et ventes sur la même page",
     "1. Point de Vente → Analyse → Personnes et tables (Aujourd'hui).",
     "3 tables, 13 personnes et 130 000 FCFA sur la même page."),
    ("R92", "R", 1, "Des ventes sur la période",
     "REST-25 c.2 — Les quantités vendues de chaque produit",
     "1. Point de Vente → Analyse → « Détails des ventes ».\n2. Choisir la "
     "même période (dates de début et de fin), imprimer.",
     "Le rapport donne la quantité vendue et le montant de chaque produit, "
     "par catégorie ; les mêmes quantités figurent dans le rapport de "
     "fermeture de la session."),
    ("R93", "R", 1, "Une table de 6 personnes divisée en deux additions",
     "REST-25 c.3 — Une table divisée compte une fois",
     "1. Encaisser les deux additions.\n2. Personnes et tables.",
     "1 table et 6 personnes."),
    ("R94", "R", 1, "Une table encore ouverte et une table annulée",
     "REST-25 c.4 — Ni ouverte ni annulée",
     "1. Personnes et tables.",
     "Ni l'une ni l'autre n'est comptée (ni les remboursements)."),
    ("R95", "R", 1, "Caisse fermée le soir",
     "REST-25 c.5 — Le rapport de fermeture",
     "1. Point de Vente → Analyse → Rapport de session (ou « Imprimer le "
     "rapport » à la caisse).",
     "Le rapport indique le nombre de tables et de personnes, les ventes "
     "sans table et les annulations de la session (table, produit, "
     "quantité, montant, motif, autorisée par) : le chef de salle n'a rien à "
     "rédiger, il signe."),
    ("R96", "R", 3, "Vente sans table ouverte ; deux tables de 4 et 2 et "
     "trois ventes sans table",
     "REST-25 c.6 — Les ventes sans table à part",
     "1. Personnes et tables.",
     "2 tables, 6 personnes et, à part, 3 ventes sans table."),
    ("R97", "R", 3, "130 000 FCFA pour 13 personnes servies",
     "REST-26 c.1 — Prix moyen par personne (tableau de bord standard)",
     "1. Point de Vente → Tableau de bord.",
     "Le prix moyen par personne est de 10 000 FCFA (le tableau standard "
     "compte aussi les ventes sans table et les remboursements : à contrôler "
     "à l'écran ; le calcul selon nos règles est au lot 2)."),
    ("R98", "R", 3, "Une période sans table servie",
     "REST-26 c.2 — Pas de moyenne sans table",
     "1. Tableau de bord sur cette période.",
     "Aucune moyenne n'est affichée."),
    ("R99", "R", 2, "Une table ouverte",
     "REST-08 c.4 — Le client sur la table (bouton « Client »)",
     "1. Toucher « Client », choisir un client.\n2. Encaisser une autre "
     "table sans client.",
     "Le client est rattaché à l'addition ; une table sans client "
     "s'encaisse sans rien réclamer."),
    ("R100", "R", 1, "Mode « Ardoise client » sur la caisse ; une table "
     "ouverte",
     "AH-01 — L'ardoise naît seulement d'une addition réglée",
     "1. Le manager choisit l'ardoise au paiement, revient au plan sans "
     "valider.\n2. Annuler la table.\n3. Une autre table : ardoise, "
     "Valider.",
     "Aucune ardoise tant que l'addition n'est pas réglée ; aucune ardoise "
     "ouverte après l'annulation ; une ardoise du bon montant après la "
     "validation (POS Crédit → Ardoises)."),
    ("R101", "R", 1, "Mode « Ardoise client » sur la caisse du restaurant "
     "et sur une caisse sans service à table",
     "AH-02 — L'ardoise réservée au manager en restaurant",
     "1. Caisse du restaurant : écran de paiement avec la caissière, puis "
     "avec le manager.\n2. Autre caisse : écran de paiement.",
     "Restaurant : « Mettre sur ardoise » et l'ardoise n'apparaissent que "
     "pour le manager. Autre caisse : le bouton est là, comme avant."),
    ("R102", "R", 1, "Deux tables ouvertes par deux serveurs, encaissées par "
     "la caissière, sous le même compte de caisse",
     "AH-03 — Le serveur dans les analyses",
     "1. Analyse AITE → Tableau croisé : regrouper par « Serveur (ouverte "
     "par) », puis par « Encaissée par ».",
     "Les deux serveurs sont distingués ; « Encaissée par » donne la "
     "caissière ; le compte Odoo s'affiche « Compte Odoo »."),
    ("R103", "R", 1, "Base vierge créée avec le pays Cameroun, en "
     "français, sans démonstration",
     "AH-12 — Restaurant seul, sans hôtel",
     "1. Installer les 4 modules (INSTALLATION.md, §9).\n2. Ouvrir Point "
     "de Vente.",
     "Installation sans erreur ; aucun menu ni module hôtelier ; société en "
     "FCFA ; caisse « Restaurant » prête (Espèces, Mobile Money, salle "
     "« Salle », case « Service à table contrôlé » cochée)."),
    ("R104", "R", 2, "Base du restaurant installée (cas R103)",
     "Mise en service — un seul journal d'espèces, et une caisse créée "
     "ensuite a ses Espèces",
     "1. Facturation → Configuration → Comptabilité → Journaux : regarder "
     "les journaux de type « Espèces ».\n2. Point de Vente → Configuration "
     "→ Point de vente → Nouveau : nom « Bar », Enregistrer.\n3. Regarder "
     "les modes de paiement de « Bar », puis revenir aux journaux.",
     "Étape 1 : un seul journal d'espèces (« Espèces »), celui des Espèces "
     "de la caisse « Restaurant ». Étape 3 : « Bar » a « Espèces » et "
     "« Mobile Money » ; ses Espèces sont sur un nouveau journal « Espèces "
     "Bar » ; aucun journal d'espèces n'est resté sans mode de paiement."),
]
