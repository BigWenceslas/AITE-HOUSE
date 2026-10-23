# -*- coding: utf-8 -*-
"""Référentiel des scénarios de recette AITE HOUSE.

Chaque cas : (id, domaine, module, priorité, prérequis, scénario,
              étapes, résultat attendu)
Priorités : 1 = critique (bloque la mise en production)
            2 = majeur   (à corriger avant démarrage)
            3 = mineur   (confort, à planifier)
"""

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
     "qu'il reste à faire ; bouton « Fiches clients x/y »."),
    ("O02", "O", 1, "Fiche pré-remplie incomplète",
     "Compléter la fiche jusqu'à « Complète »",
     "1. Cliquer « compléter maintenant ».\n2. Renseigner la date de "
     "naissance.",
     "La colonne « Il manque » disparaît et la fiche passe « Complète » "
     "sans bouton ; le bandeau devient vert quand tous les occupants sont "
     "enregistrés."),
    ("O03", "O", 1, "Séjour à 2 occupants",
     "Ajouter un accompagnant",
     "1. Dans la fenêtre Fiches clients, ajouter une ligne pour "
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
     "1. Hôtel → Direction.\n2. Période « Ce mois ».\n3. Lire la rangée "
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
     "1. Hôtel → Direction (tableau exécutif) : noter TO, ADR, RevPAR.\n"
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
]
