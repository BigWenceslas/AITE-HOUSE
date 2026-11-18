# -*- coding: utf-8 -*-
"""Scénarios de bout en bout pour l'intégrateur junior — source unique.

Périmètre : le restaurant AITE (aite_house_restaurant « tout installer »,
aite_pos_restaurant, aite_pos_credit, aite_pos_analytics, aite_pos_analytics_hr,
aite_resto_carte_messager), le stock (aite_stock_dashboard), les achats
(aite_purchase_dashboard) et la Direction (aite_direction_dashboard ;
aite_exec_dashboard exige l'hôtel, voir CAS_ECARTES).

Ce fichier produit le PDF (generer.py → index.html → weasyprint) et le
classeur (.xlsx). Chaque étape est un seul geste, avec ce que l'écran doit
montrer ; les textes entre « » sont ceux du code (vues, gabarits, messages)
ou d'Odoo 18 en français (fichiers fr.po). Chaque étape renvoie aux cas du
cahier de recette (recette/cas_de_test.py, domaines D, F, H, I, J, K, R)
qu'elle couvre : generer.py s'arrête si un cas n'est couvert par aucun
scénario sans être écarté (CAS_ECARTES, avec sa raison).

La base de recette est celle que l'intégrateur crée lui-même (scénario I01) :
la démonstration « Le Messager » (aite_resto_carte_messager) donne la salle de
12 tables, l'équipe fictive et la carte. Les scénarios marqués « joue » ont été
joués tels quels sur une base jetable (Odoo 18 Community, novembre 2026).
"""

TITRE = "AITE — scénarios de l'intégrateur (restaurant, stock, achats, Direction)"
VERSION = "1.0 — novembre 2026"

MODULES = [
    ("aite_house_restaurant", "18.0.1.0.1", "« tout installer » : les quatre modules du restaurant (et l'écran de cuisine sur Enterprise), l'« Ardoise client » sur la caisse au service à table"),
    ("aite_pos_restaurant", "18.0.1.0.9", "la caisse au service à table contrôlé"),
    ("aite_pos_credit", "18.0.2.0.6", "les ardoises et leur recouvrement"),
    ("aite_pos_analytics", "18.0.2.1.6", "l'analyse des ventes : familles, marges, caisses"),
    ("aite_pos_analytics_hr", "18.0.1.0.0", "le serveur et « Encaissée par » dans les analyses (s'installe seule)"),
    ("aite_resto_carte_messager", "18.0.1.3.3", "données de démonstration : salle, équipe, comptes, carte"),
    ("aite_stock_dashboard", "18.0.1.1.3", "le tableau de bord du stock (Inventaire)"),
    ("aite_purchase_dashboard", "18.0.1.0.5", "le tableau de bord des achats (Achats)"),
    ("aite_direction_dashboard", "18.0.1.1.2", "Direction — Vue consolidée"),
]

EQUIPE = [
    ("Brice", "Serveur", "1001"), ("Nadège", "Serveur", "1002"), ("Loïc", "Serveur", "1003"),
    ("Clarisse", "Caissière", "2001"), ("Prisca", "Caissière", "2002"),
    ("Hervé", "Chef de salle ou superviseur", "3001"), ("Sandrine", "Manager", "4001"),
]

COMPTES = [
    ("caisse / caisse", "Caisse de la salle", "la tablette : Point de Vente Utilisateur, Facturation, courriel"),
    ("manager / manager", "Manager de la salle", "la gestion : Point de Vente Administrateur, Employés, Facturation, Manager — Analyses POS"),
    ("chef / chef", "Chef de salle (rapports)", "« Restaurant : lecture des rapports », rien d'autre"),
    ("admin / admin", "Administrateur", "l'intégrateur : installation et réglages"),
]

PARTIES = [
    ("A", "Installation et mise en place", "tous"),
    ("B", "La caisse du restaurant", "aite_pos_restaurant"),
    ("C", "L'ardoise (crédit clients)", "aite_pos_credit"),
    ("D", "L'analyse des ventes", "aite_pos_analytics, aite_pos_analytics_hr"),
    ("E", "Le stock", "aite_stock_dashboard + Inventaire"),
    ("F", "Les achats", "aite_purchase_dashboard + Achats"),
    ("G", "La Direction", "aite_direction_dashboard"),
    ("H", "Non-régression", "tous"),
]

# Cas du cahier qui exigent l'hôtel : non joués sur une base de restaurant.
RAISON_HOTEL = ("aite_exec_dashboard dépend du socle hôtelier (aite_hotel_management, "
                "aite_slot_booking) ; son menu est Hôtel → Activité par pôle, réservé au "
                "groupe responsable hôtel. Il ne s'installe pas chez un restaurant seul : "
                "à jouer avec le cahier de recette de l'hôtel.")
CAS_ECARTES = {
    "K01": RAISON_HOTEL,
    "K02": RAISON_HOTEL + " Le taux d'occupation et les nuitées se lisent sur les séjours.",
    "K03": RAISON_HOTEL,
    "K04": RAISON_HOTEL + " La comparaison porte sur les chiffres hôtel et bar communs aux deux écrans.",
}

# Un scénario : id, partie, titre, role, base, prerequis, but,
# etapes [(geste, attendu, "cas cas")], captures [(fichier, légende)] avec
# fichier = "restaurant/xx.jpg" ou "integrateur/xx.jpg" (dans captures/),
# encadres [("reflexe"|"regle"|"attention", texte)], joue (bool).

BASE = "recette (I01 à I03)"

SCENARIOS = [
    # ═════════════════════════ A. INSTALLATION ══════════════════════════
    dict(
        id="I01", partie="A", joue='partiel', vu="Base créée comme l'écran de création (Cameroun, Français, sans démonstration) puis « tout installer » en ligne de commande (1 min 30, aucune ligne ERROR) ; cartes AITE vues dans Apps ; caisse « Restaurant » avec Espèces et Mobile Money. Étapes 8 et 9 non jouées.",
        titre="Créer une base neuve et activer « AITE HOUSE — Restaurant (tout installer) »",
        role="Intégrateur (admin)", base="nouvelle base",
        prerequis="Odoo 18 à jour ; les dossiers de addons/ déposés à côté des autres addons "
                  "(addons_path) ; service Odoo redémarré.",
        but="Une base de restaurant en FCFA, sans hôtel, avec sa caisse « Restaurant » prête, "
            "installée par un seul module.",
        etapes=[
            ("Écran de création de base d'Odoo (/web/database/manager, en anglais) : « Database Name » "
             "recette_resto, « Language » Français, « Country » Cameroun, « Demo Data » décoché ; "
             "« Create database ».",
             "La base s'ouvre sur l'accueil ; Paramètres → Utilisateurs & Sociétés → Sociétés : la "
             "devise de la société est XAF (FCFA).", "R103"),
            ("Paramètres → tout en bas → « Activer le mode développeur ».",
             "La page se recharge ; le menu Apps propose « Mettre à jour la liste des Apps ».", ""),
            ("Apps → « Mettre à jour la liste des Apps » → « Mettre à jour ».",
             "La liste se recharge sans erreur.", ""),
            ("Apps : retirer le filtre « Apps » de la recherche, taper « AITE ».",
             "Les cartes AITE apparaissent, dont « AITE HOUSE — Restaurant (tout installer) » et deux "
             "« AITE — Direction » : « (vue consolidée) » et « (activité par pôle) » (écran #1).", ""),
            ("Carte « AITE HOUSE — Restaurant (tout installer) » → « Activer ».",
             "Après une à deux minutes, Odoo revient à l'accueil : Restaurant, POS Crédit, Point de "
             "Vente, Facturation, Inventaire, Employés ; aucun menu Hôtel.", "R103"),
            ("Apps, recherche « AITE » : regarder les cartes du restaurant.",
             "« AITE — Restaurant (service à table) », « AITE — Crédit clients (Ardoises POS & "
             "Ventes) », « AITE — POS Analytics (LAVERANDAH) » et « AITE — Analyses du restaurant par "
             "employé » sont installés (plus de bouton « Activer »).", "R103"),
            ("Point de Vente → Configuration → Point de vente → « Restaurant ».",
             "La caisse « Restaurant » existe : modes Espèces et Mobile Money, salle « Salle », case "
             "« Service à table contrôlé » cochée.", "R103"),
            ("Facturation → Configuration → Comptabilité → Journaux : filtrer le type Espèces.",
             "Un seul journal d'espèces (« Espèces »), celui des Espèces de la caisse « Restaurant ».",
             "R104"),
            ("Point de Vente → Configuration → Point de vente → Nouveau : nom « Bar », enregistrer ; "
             "ouvrir ses « Modes de paiement ».",
             "« Bar » a « Espèces » (sur un nouveau journal « Espèces Bar ») et « Mobile Money ». "
             "Cette caisse sert aux scénarios D02, D03 et H01.", "R104"),
        ],
        captures=[("integrateur/01_apps_modules_aite.jpg",
                   "Apps, recherche « AITE » : « tout installer » et les deux « AITE — Direction ».")],
        encadres=[("regle", "Créer la base par l'écran de création d'Odoo, pays Cameroun : une base "
                   "créée sans pays naît en dollars, et Odoo refuse ensuite de changer la devise. "
                   "Ne pas lancer le scénario « Restaurant » qu'Odoo propose sur un Point de Vente "
                   "vide.")],
    ),
    dict(
        id="I02", partie="A", joue='oui', vu='Installation sans erreur ; notification rejouée : « … en place : 12 tables, 7 employés à niveau … 101 produits à la carte (101 attendus) », « créés : 0 … » ; Bière blonde 65 cl : coût 650, stock 48.',
        titre="Poser les données de démonstration : la carte « Le Messager »",
        role="Intégrateur (admin)", base="recette",
        prerequis="I01 joué. Base de démonstration ou de formation seulement (jamais la base de "
                  "production du client).",
        but="Une salle de 12 tables, l'équipe fictive aux quatre niveaux, trois comptes Odoo avec "
            "courriel et 101 produits rangés en familles, pour former et recetter.",
        etapes=[
            ("Apps : retirer le filtre « Apps », chercher « Messager » ; carte « AITE — Carte du "
             "restaurant Le Messager (démonstration) » → « Activer ».",
             "Installation sans erreur ; retour à l'accueil.", ""),
            ("Point de Vente → Configuration.",
             "Le menu se termine par « Motifs d'annulation » et « Poser la carte Le Messager » "
             "(écran #1).", ""),
            ("Toucher « Poser la carte Le Messager ».",
             "Notification « Carte Le Messager » qui reste affichée : « <société> : Carte posée : 101 "
             "produits en 30 familles ; salle : 12 tables ; équipe : 7 employés, 3 comptes. Rien n'a "
             "été créé en double. » ; la première fois, elle dit aussi ce qui vient d'être créé "
             "(« Créés cette fois : … ») ; la seconde fois, rien n'est créé (écran #2, capture de "
             "la version 18.0.1.3.2, au bilan technique).", ""),
            ("Employés.",
             "Sept fiches : Brice, Nadège, Loïc, Clarisse, Prisca, Hervé, Sandrine ; chacune a un "
             "« Niveau en caisse » et un « Code caisse » (1001, 1002, 1003, 2001, 2002, 3001, 4001).", ""),
            ("Paramètres → Utilisateurs & Sociétés → Utilisateurs : ouvrir « Caisse de la salle », "
             "« Manager de la salle », « Chef de salle (rapports) ».",
             "Identifiants caisse, manager, chef ; chacun a une adresse e-mail "
             "(caisse@restaurant.example…) ; mot de passe = identifiant, à changer.", ""),
            ("Point de Vente → Configuration → Catégories de produits du PdV.",
             "Petit déjeuner, Plats, Pizzas & burgers, Afternoon tea, Bar, avec leurs sous-familles "
             "(Bar > Vins > Vins rouges, Bar > Bières, Bar > Sans alcool > Sodas…).", ""),
            ("Inventaire → Produits → Produits → « Bière blonde 65 cl ».",
             "Prix de vente 1 500 FCFA, « Coût » 650 FCFA, « Suivre l'inventaire » coché, stock de "
             "départ 48 ; « Poulet DG » (5 000 FCFA) n'a ni coût ni suivi.", ""),
            ("Inventaire → Configuration → Catégories de produits → « Bar / Bières ».",
             "« Méthode de coût » : « Coût moyen (AVCO) » (comme « Bar » et toutes ses "
             "sous-catégories) ; « Plats » reste en « Prix standard ». Un achat de Bière blonde à "
             "700 FCFA fera monter son « Coût » (moyenne du stock et de l'achat).", ""),
        ],
        captures=[("integrateur/02_menu_configuration_point_de_vente.jpg",
                   "Point de Vente → Configuration : « Motifs d'annulation » et « Poser la carte Le Messager »."),
                  ("integrateur/03_poser_la_carte_le_messager.jpg",
                   "La notification de « Poser la carte Le Messager » rejoué : rien n'est créé deux fois.")],
        encadres=[("attention", "La carte de démonstration se pose seulement si la société a un plan "
                   "comptable et une caisse au service à table contrôlé ; sinon la notification le dit. "
                   "Désinstaller le module ne retire pas la carte.")],
    ),
    dict(
        id="I03", partie="A", joue='partiel', vu="aite_direction_dashboard installé en ligne de commande, sans ERROR ; menus Inventaire, Achats et Direction relevés tels qu'écrits.",
        titre="Installer le stock, les achats et la Direction",
        role="Intégrateur (admin)", base="recette",
        prerequis="I01 joué.",
        but="Les trois tableaux de bord de gestion, installés d'un geste avec leurs modules Odoo "
            "(Inventaire, Achats).",
        etapes=[
            ("Apps : retirer le filtre « Apps », chercher « Direction ».",
             "Deux cartes : « AITE — Direction (vue consolidée) » et « AITE — Direction (activité par "
             "pôle) ». La seconde installe le socle hôtelier : ne pas l'activer chez un restaurant "
             "seul.", ""),
            ("« AITE — Direction (vue consolidée) » → « Activer ».",
             "Installation sans erreur ; les modules « AITE — Stock & Inventaire (Tableau de bord) », "
             "« AITE — Achats & Fournisseurs (Tableau de bord) » et l'application Achats sont "
             "installés avec lui.", ""),
            ("Ouvrir le menu principal (icône en haut à gauche).",
             "Nouvelles applications : Achats et Direction.", ""),
            ("Inventaire.",
             "Barre de menus : « Vue d'ensemble », « Opérations », « Tableau de bord AITE », "
             "« Produits », « Analyse », « Configuration ».", ""),
            ("Achats.",
             "Barre de menus : « Commandes », « Tableau de bord AITE », « Produits », « Analyse », "
             "« Configuration » ; Configuration propose « Consignes fournisseurs ».", ""),
            ("Direction.",
             "Titre « Direction — Vue consolidée », sous-titre « POS · Crédit clients · Stock · "
             "Achats — » suivi du nom de la société ; les blocs PÉRIODE, CAISSE, HEURE, JOUR, VUE.", "J01"),
            ("Recharger avec Ctrl+Maj+R.",
             "Mêmes écrans, aucune fenêtre d'erreur.", ""),
        ],
        captures=[],
        encadres=[("reflexe", "En ligne de commande, l'équivalent est : odoo-bin -c <odoo.conf> -d "
                   "<base> -i aite_direction_dashboard --stop-after-init. Lire ensuite le journal : "
                   "aucune ligne ERROR.")],
    ),
    dict(
        id="I04", partie="A", joue=False,
        titre="Mettre à niveau une base existante",
        role="Intégrateur (admin)", base="base du client (copie de recette d'abord)",
        prerequis="Sauvegarde de la base et du filestore ; toutes les caisses fermées ; nouvelles "
                  "versions des dossiers AITE reçues.",
        but="Passer aux versions livrées sans rien perdre ; vérifier la version de la caisse "
            "(aite_pos_restaurant 18.0.1.0.9).",
        etapes=[
            ("Remplacer chaque dossier AITE livré par sa nouvelle version, dossier par dossier "
             "(jamais le répertoire addons entier) ; redémarrer le service Odoo.",
             "Odoo redémarre ; le journal n'a pas de ligne ERROR.", ""),
            ("Apps → « Mettre à jour la liste des Apps » → « Mettre à jour ».",
             "La liste se recharge.", ""),
            ("Apps, recherche « AITE », vue Liste (icône en haut à droite).",
             "Colonnes « Nom de module », « Nom technique » (mode développeur), « Dernière version » "
             "(celle des dossiers déposés) et « Statut ».", ""),
            ("Ouvrir « AITE HOUSE — Restaurant (tout installer) » → « Mettre à niveau ».",
             "Les modules du restaurant sont mis à niveau ; sur Enterprise, l'écran de cuisine "
             "s'installe s'il manque.", ""),
            ("Même geste pour « AITE — Direction (vue consolidée) » et, si installée, la carte « Le "
             "Messager ».",
             "Mise à niveau sans erreur ; la carte posée n'est pas doublée.", ""),
            ("Apps, vue Liste : relire « AITE — Restaurant (service à table) ».",
             "« Dernière version » : 18.0.1.0.9 ; « Statut » : Installé.", ""),
            ("Sur chaque tablette et chaque poste : Ctrl+Maj+R (sur tablette : vider le cache du "
             "navigateur ou fermer et rouvrir l'onglet).",
             "La caisse se recharge sur le plan verrouillé ; les tableaux de bord s'affichent.", ""),
            ("Si « AITE — Analyses du restaurant par employé » n'est pas installé : Apps → chercher "
             "« par employé » → « Activer ».",
             "La passerelle est installée (regroupements « Serveur », « Encaissée par »).", ""),
        ],
        captures=[],
        encadres=[("regle", "Ne jamais retirer le dossier d'un module installé, ni désinstaller "
                   "pour « réinstaller propre » : Odoo perdrait les données du module (ardoises, "
                   "annulations, codes).")],
    ),
    dict(
        id="I05", partie="A", joue='partiel', vu="Étapes 1, 2 et 4 : « Opération invalide » / « Impossible d'envoyer le message… » reproduit en vidant le courriel du compte caisse ; « Erreur d'accès » du manager sur Direction ; avec POS Crédit : Utilisateur, les six onglets et les trois tableaux de bord s'ouvrent.",
        titre="Les comptes Odoo et leurs droits",
        role="Intégrateur (admin) ; comptes manager et chef", base="recette",
        prerequis="I02 et I03 joués.",
        but="Chaque compte ouvre ses écrans, et seulement eux ; le courriel est présent.",
        etapes=[
            ("Utilisateurs → « Caisse de la salle » → vider l'« Adresse e-mail », enregistrer ; à la "
             "caisse, encaisser une table (scénario B07).",
             "À la validation : fenêtre « Opération invalide », « Impossible d'envoyer le message, "
             "veuillez configurer l'adresse e-mail de l'expéditeur. » (écran #1). Remettre l'adresse, "
             "puis valider de nouveau : la validation passe.", ""),
            ("Se connecter avec manager / manager ; ouvrir Direction.",
             "Fenêtre « Erreur d'accès » : « Vous n'êtes pas autorisé à accéder aux enregistrements "
             "'Ardoise POS (vente à crédit)' (aite.pos.credit). » (écran #2).", "J01"),
            ("Admin : « Manager de la salle » → onglet « Droits d'accès » → POS Crédit : Utilisateur "
             "(ou Responsable) ; Achats : Utilisateur ; enregistrer.",
             "Les droits sont enregistrés.", ""),
            ("Manager : recharger Direction ; toucher chaque onglet de VUE.",
             "Le cockpit s'affiche, les six onglets s'ouvrent sans erreur ; le menu Achats est "
             "apparu.", "J01"),
            ("Se connecter avec chef / chef.",
             "Seul le menu « Restaurant » est proposé ; Restaurant → Annulations s'ouvre.", "R83"),
        ],
        captures=[("integrateur/20_caisse_sans_courriel.jpg",
                   "Le compte de la tablette sans adresse e-mail : la validation est refusée."),
                  ("integrateur/18_direction_erreur_d_acces.jpg",
                   "Un manager sans le droit « POS Crédit » ouvre Direction : « Erreur d'accès ».")],
        encadres=[("reflexe", "Le droit Point de Vente : Administrateur donne déjà Inventaire : "
                   "Utilisateur (le tableau de bord AITE du stock s'ouvre). Pour Direction, ajouter "
                   "POS Crédit et, pour voir l'application Achats, Achats : Utilisateur.")],
    ),
    # ═════════════════════════ B. LA CAISSE DU RESTAURANT ═══════════════════
    dict(
        id="B01", partie="B", joue=False,
        titre="Les réglages de la caisse « Restaurant », avant la première ouverture",
        role="Intégrateur (admin)", base=BASE,
        prerequis="I01 et I02 joués ; la caisse « Restaurant » n'a jamais été ouverte.",
        but="Vérifier ce que l'installation a réglé, mode « Ardoise client » compris.",
        etapes=[
            ("Point de Vente → Configuration → Paramètres ; choisir « Restaurant » ; bloc Restaurant.",
             "« Est un bar/restaurant » et « Service à table contrôlé » cochés ; la phrase commence par "
             "« Coché : chaque employé tape son code à 4 chiffres » ; « Délai avant l'orange "
             "(minutes) » = 60 ; « Autoriser la vente sans table » décoché ; « Refuser la vente des "
             "produits épuisés » coché (écran #1).", ""),
            ("Décocher « Se connecter avec Employés », « Enregistrer ».",
             "Refus : « Décochez d'abord « Service à table contrôlé » : sans les codes personnels, la "
             "caisse ne saurait plus qui fait quoi. » ; « Ignorer ».", ""),
            ("Cocher « Autoriser la vente sans table », « Enregistrer ».",
             "La case s'enregistre (aucune session n'existe encore).", "R19"),
            ("Bloc Paiement, « Modes de paiement ».",
             "La caisse a déjà trois modes, posés par l'installation : Espèces, Mobile Money, "
             "Ardoise client (rien à ajouter ; un client sans crédit : archiver le mode « Ardoise client », sinon la mise à niveau suivante le remet).",
             "F01"),
            ("Point de Vente → Configuration → Motifs d'annulation.",
             "Cinq motifs : Erreur de saisie, Client parti, Plat refusé, Produit manquant, Autre.", ""),
        ],
        captures=[("restaurant/25_reglages_service_a_table_controle.jpg",
                   "Le bloc Restaurant : chaque réglage dit ce qui va se passer.")],
        encadres=[("regle", "Régler « Service à table contrôlé » et « Autoriser la vente sans "
                   "table » avant la première ouverture : ensuite Odoo garde une session « Contrôle "
                   "à l'ouverture » qui grise ces deux cases.")],
    ),
    dict(
        id="B02", partie="B", joue=False,
        titre="Le manager prépare l'équipe et la carte",
        role="Manager (compte manager)", base=BASE,
        prerequis="B01 joué. Se connecter avec manager / manager.",
        but="La fiche employé (niveau, code) et un produit nouveau rangé dans sa famille.",
        etapes=[
            ("Employés → « Brice ».",
             "Groupe « Caisse du restaurant » : « Niveau en caisse » = Serveur, « Code caisse » = 1001, "
             "chacun avec sa phrase d'aide (écran #1).", ""),
            ("Employés → Nouveau : « Essai », « Niveau en caisse » = Serveur.",
             "Un code de 4 chiffres apparaît aussitôt dans « Code caisse ».", "R03"),
            ("Taper 123 dans « Code caisse », enregistrer.",
             "Refus : « Le code doit faire exactement 4 chiffres. »", "R03"),
            ("Taper 1002 (code de Nadège), enregistrer.",
             "Refus : « Le code 1002 est déjà celui d'un autre employé. Choisissez quatre autres "
             "chiffres : chaque employé a son propre code. » — le nom de Nadège n'apparaît pas.", "R03"),
            ("Taper 1009, enregistrer, puis archiver « Essai ».",
             "La fiche est enregistrée, puis archivée.", "R03"),
            ("Point de Vente → Produits → Produits → Nouveau : « Jus de bissap », 1 000 FCFA, case "
             "« Point de Vente », onglet « Point de Vente » : catégorie « Sodas » ; enregistrer.",
             "Le produit est enregistré ; il apparaîtra sous Bar > Sans alcool > Sodas (B04).", "R13"),
            ("Même geste : « Verre de vin rouge », 3 000 FCFA, catégorie « Vins rouges ».",
             "Il apparaîtra sous Bar > Vins > Vins rouges (B04).", "R33"),
            ("Point de Vente → Configuration → Plans de salle → « Salle ».",
             "12 tables numérotées de 1 à 12.", "R63"),
        ],
        captures=[("restaurant/24_fiche_employe_niveau_et_code.jpg",
                   "La fiche employé : « Niveau en caisse » et « Code caisse » sur la première page.")],
        encadres=[],
    ),
    dict(
        id="B03", partie="B", joue='partiel', vu="Étapes 1 à 4 : refus de Brice (bandeau rouge), « Contrôle à l'ouverture » de Clarisse, plan verrouillé et sa légende.",
        titre="Ouvrir la caisse le matin",
        role="Caissière (Clarisse 2001) ; Serveur (Brice 1001)", base=BASE,
        prerequis="B01 et B02 joués. Sur la tablette : se connecter avec caisse / caisse.",
        but="La caisse s'ouvre avec le code d'une caissière, jamais d'un serveur ; le plan "
            "verrouillé devient l'écran de repos.",
        etapes=[
            ("Point de Vente → carte « Restaurant » → « Ouvrir la caisse ».",
             "Le plan s'affiche avec la fenêtre « Votre code pour ouvrir la caisse » (quatre ronds, "
             "un pavé, « Retour »).", "R63"),
            ("Brice tape 1001.",
             "Refus : « La caisse n'est pas encore ouverte. La caissière ou un chef de salle doit "
             "l'ouvrir avec son code. »", "R10"),
            ("Clarisse tape 2001.",
             "Code accepté au 4ᵉ chiffre ; fenêtre « Contrôle à l'ouverture » (« Espèces à "
             "l'ouverture », « Note d'ouverture ») — écran #1.", "R10"),
            ("Toucher « J'ouvre la caisse ».",
             "Le plan : tables grises numérotées 1 à 12, « Touchez une table, puis tapez votre "
             "code. », la légende « Gris : libre · Vert : ouverte · Orange : ouverte depuis plus de "
             "60 min, proposez l'addition · Pastille rouge : pas encore envoyé ».", "R63 D01"),
            ("Toucher ≡.",
             "« Commandes », « Entrée ou sortie d'espèces », « Fermer la caisse » (et « Imprimer le "
             "rapport » avec une imprimante) ; pas de « Modifier le plan ».", "R65 R14"),
            ("Faire glisser la table 1 sur la table 2.",
             "Rien ne bouge.", "R65"),
        ],
        captures=[("integrateur/04_caisse_controle_a_l_ouverture.jpg",
                   "Brice refusé (bandeau rouge), puis Clarisse : « Contrôle à l'ouverture »."),
                  ("restaurant/03_plan_verrouille.jpg", "Le plan verrouillé et sa légende.")],
        encadres=[],
    ),
    dict(
        id="B04", partie="B", joue='partiel', vu="Table 4 par Brice (1001, 2 personnes), Bar > Bières, deux Bière blonde 65 cl et un Soda 33 cl, « J'envoie » : « Envoyé : Bières × 2, Sodas × 1. », retour au plan. Vente sans table, jus et vin non joués.",
        titre="Ouvrir une table, commander, envoyer",
        role="Serveur (Brice 1001)", base=BASE,
        prerequis="B03 joué : caisse ouverte, plan affiché.",
        but="Le parcours de base d'un serveur : la table, le code, les personnes, la carte en "
            "familles, « J'envoie », retour au plan verrouillé.",
        etapes=[
            ("Regarder la barre du haut du plan.",
             "« Plan », « Table », un bouton « + » (vente sans table cochée en B01), ≡.", "R19"),
            ("Brice touche « + » et tape 1001.",
             "Refus : « La vente sans table n'est pas ouverte ici. Ouvrez une table du plan. »", "R19"),
            ("Toucher la table 4, puis « Retour » sans code.",
             "La fenêtre « Table 4 — votre code » s'est ouverte ; après « Retour », la table 4 reste "
             "grise.", "R01"),
            ("Toucher la table 4, taper 9999.",
             "« Code inconnu. Retapez votre code. »", "R02"),
            ("Taper 1001.",
             "« Table 4 — combien de personnes ? » : boutons 1 à 8 et « 9 et plus », aucun 0 ; aucun "
             "produit ne peut être saisi.", "R02 R15 R20 R22"),
            ("Toucher « 9 et plus », taper 0.",
             "« Valider » reste grisé ; « Il faut au moins une personne à table. »", "R21 R22"),
            ("« Retour ».", "Retour au plan ; la table 4 est grise.", "R21"),
            ("Table 4, 1001, toucher 2.",
             "Écran de commande : « Brice » en haut, « Table 4 · ouverte par Brice · 0 min », bouton "
             "« 2 personnes », familles « Petit déjeuner », « Plats », « Pizzas & burgers », "
             "« Afternoon tea », « Bar ».", "R16 R23 R29"),
            ("Toucher « Bar ».", "Sous-familles : « Vins », « Whisky », « Bières », « Sans alcool ».",
             "R30"),
            ("Toucher « Bières ».",
             "Seules les bières : Bière blonde 65 cl, Bière brune 65 cl, Bière importée 33 cl.", "R31"),
            ("Retoucher « Bières ».", "La caisse remonte d'un niveau (sous-familles de Bar).", "R32"),
            ("« Bières », deux fois « Bière blonde 65 cl » ; « Sans alcool » → « Sodas » : "
             "« Soda 33 cl » et « Jus de bissap » ; « Vins » → « Vins rouges ».",
             "Lignes « Bière blonde 65 cl » 2,00 (3 000 FCFA), « Soda 33 cl », « Jus de bissap » ; "
             "« Verre de vin rouge » est proposé sous Vins rouges (écran #1). Retirer le jus "
             "(⌫, ⌫).", "R13 R33"),
            ("Toucher « J'envoie ».",
             "Notification « Envoyé : Bières × 2, Sodas × 1. » ; retour au plan, plus aucun nom ; la "
             "table 4 est verte, « 0 min ».", "R08 R64"),
            ("Toucher de nouveau la table 4.",
             "La fenêtre « Table 4 — votre code » s'ouvre : le code est redemandé. « Retour ».", "R08"),
        ],
        captures=[("integrateur/05_caisse_commande_table_4.jpg",
                   "La table 4 de Brice : la carte « Le Messager » en familles.")],
        encadres=[],
    ),
    dict(
        id="B05", partie="B", joue=False,
        titre="Les autres tables : collègue, numéro tapé, client",
        role="Serveurs (Nadège 1002, Brice 1001)", base=BASE,
        prerequis="B04 joué. Un second poste (autre fenêtre) connecté avec caisse / caisse.",
        but="Une table appartient à son serveur ; les tables se voient sur tous les postes.",
        etapes=[
            ("Nadège touche la table 4 et tape 1002.",
             "Refus : « Table 4 : c'est la table de Brice. Seuls Brice, la caissière ou un chef de "
             "salle peuvent la modifier. »", "R24"),
            ("Nadège ouvre la table 7 (1002, 2 personnes), deux « Café expresso » (Bar > Sans alcool "
             "> Café & thé), « J'envoie ».",
             "La table 7 est verte ; sur le second poste, les tables 4 et 7 sont vertes.", "R24 R64"),
            ("Nadège : « Table », tape 12, « Aller à/au ».",
             "La fenêtre propose « Retour » (jamais « Discard ») ; puis « Table 12 — votre code ».",
             "R17"),
            ("Nadège tape 1002, touche 2.", "« Table 12 · ouverte par Nadège · 0 min ».", "R16 R17"),
            ("« Table », tape 99, « Aller à/au », 1002, 2 ; « Thé », « J'envoie ».",
             "Une table « 99 » s'ouvre à 2 personnes et compte comme une table.", "R18"),
            ("Brice ouvre la table 3 (1001, 1), « Soda 33 cl », « J'envoie ».",
             "La table 3 est verte (elle sert en B06).", ""),
            ("Nadège rouvre la table 7 (1002), « Client », choisir ou créer un contact.",
             "Le client est rattaché à l'addition ; « Plan ».", "R99"),
        ],
        captures=[], encadres=[],
    ),
    dict(
        id="B06", partie="B", joue=False,
        titre="Retirer, puis annuler ce qui est parti",
        role="Serveur (Brice 1001) ; Chef de salle (Hervé 3001) ; manager", base=BASE,
        prerequis="B04 et B05 joués (table 4 : 2 bières blondes et 1 soda envoyés).",
        but="Ce qui n'est pas parti se retire librement ; ce qui est parti ne s'annule qu'avec un "
            "chef de salle et un motif.",
        etapes=[
            ("Brice, table 4 (1001) : ajouter « Eau minérale 0,5 L », ⌫, ⌫.",
             "La ligne disparaît, sans code ni trace.", "R34"),
            ("Ajouter une « Bière blonde 65 cl » (3,00), ⌫, ⌫.",
             "La ligne revient à 2,00 librement.", "R36"),
            ("Encore ⌫, ⌫ sur la ligne des bières.",
             "Fenêtre « Annuler Bière blonde 65 cl — table 4 » : « Déjà envoyé : 2 Bière blonde 65 "
             "cl. Pour l'annuler, un chef de salle tape son code. », « Combien ? ».", "R09 R35 R36 R37"),
            ("« Retour » ; toucher la ligne, taper 1 au pavé.",
             "La quantité reste 2,00 : un chiffre plus petit que ce qui est parti est ignoré.", "R35"),
            ("Regarder la touche « % ».", "Grisée : aucune remise.", "R40"),
            ("Recharger la page (Ctrl+F5), table 4, 1001, ligne des bières, ⌫, ⌫.",
             "La même fenêtre d'annulation s'ouvre.", "R38"),
            ("« 1 », puis taper 1002, puis 2001.",
             "Refusés tous deux : « Ce code ne peut pas annuler. Il faut celui d'un chef de salle, d'un "
             "superviseur ou du manager. »", "R09 R45"),
            ("Hervé tape 3001 ; « Retour » sans motif.",
             "« Pourquoi ? » montrait les motifs ; sans motif, rien n'est annulé.", "R50"),
            ("⌫, ⌫, « 1 », 3001, « Autre », « Valider » vide.",
             "« Écrivez en quelques mots pourquoi. »", "R50"),
            ("« Précision » : « Bouteille cassée », « Valider ».",
             "« Annulation faite : 1 Bière blonde 65 cl, par Hervé. » ; la ligne passe à 1,00 ; "
             "« Brice » reste en haut. Avec une imprimante de cuisine seulement : « Bon d'annulation "
             "envoyé. »", "R43 R44 R50"),
            ("Manager (gestion) : Motifs d'annulation → Nouveau « Casse ». Caisse : Hervé, table 7, "
             "3001, ligne « Café expresso », ⌫, ⌫, « 1 ».",
             "« Pourquoi ? » propose six motifs, dont « Casse » ; choisir « Client parti ».", "R51"),
            ("Hervé, table 12, 3001, « Actions » → « Annuler la table » → « Client parti ».",
             "La fenêtre « Annuler la table 12 » s'ouvre directement ; la table redevient grise.", "R39"),
            ("Hervé : ≡ → « Commandes », 3001 ; corbeille de l'addition 99 ; « Erreur de saisie ».",
             "L'addition 99 disparaît de la liste.", "R39"),
            ("Manager : Point de Vente → Commandes → Commandes ; addition de la table 3 ; ⚙ Action → "
             "« Annuler la commande ».",
             "L'addition est annulée sans code : la gestion n'est jamais bloquée (trace « Annulation "
             "sans code », B11).", "R52"),
        ],
        captures=[("restaurant/10_annulation_combien.jpg", "« Déjà envoyé : … », « Combien ? »."),
                  ("restaurant/11_annulation_pourquoi.jpg", "Le code du chef de salle, puis « Pourquoi ? ».")],
        encadres=[],
    ),
    dict(
        id="B07", partie="B", joue='partiel', vu='Clarisse (2001) encaisse la table 4 en Espèces : 4 000 FCFA, retour au plan, commande « payée ».',
        titre="Encaisser",
        role="Serveur (Brice 1001) ; Caissière (Clarisse 2001) ; Manager (Sandrine 4001)", base=BASE,
        prerequis="B04 à B06 joués ; table 1 libre.",
        but="Seuls la caissière, le chef de salle et le manager encaissent ; la fiche de l'addition "
            "dit qui a ouvert et qui a encaissé.",
        etapes=[
            ("Brice, table 4 (1001), « J'encaisse ».",
             "« Code de la personne qui encaisse », sous-titre « Brice ne peut pas encaisser : la "
             "caissière tape son code ici. »", "R05"),
            ("Brice tape 1001.", "Refus ; la fenêtre attend.", "R05 R10"),
            ("Clarisse tape 2001.",
             "L'écran de paiement : modes « Espèces », « Mobile Money » (pas d'« Ardoise client » "
             "pour une caissière).", "R05 R101"),
            ("« Espèces », « Valider ».",
             "Retour au plan, sans écran « Paiement réussi » ; la table 4 redevient grise.", "R68 D02"),
            ("Clarisse ouvre la table 1 (2001, 2), « Crêpe nature », touche la ligne puis « Prix ».",
             "« Prix » est grisé.", "R12"),
            ("Sandrine touche « Clarisse » en haut, tape 4001, touche la ligne, « Prix ».",
             "« Sandrine » en haut ; « Prix » actif (ne rien changer).", "R12"),
            ("Sandrine : « J'encaisse », « Mobile Money », « Valider ».",
             "La table 1 est encaissée en Mobile Money.", "D03"),
            ("Manager : Point de Vente → Commandes → Commandes ; addition de la table 4.",
             "« Ouverte par » : Brice ; « Encaissée par » : Clarisse ; heure d'ouverture remplie ; "
             "2 convives ; total 4 000 FCFA.", "R04 R23 D02"),
            ("Bouton « Saisies » de la fiche.",
             "Une ligne par ajout : produit, quantité, employé, heure (l'eau retirée avant envoi n'y "
             "est pas).", "R06"),
        ],
        captures=[("restaurant/13_paiement_especes.jpg", "L'écran de paiement de Clarisse.")],
        encadres=[],
    ),
    dict(
        id="B08", partie="B", joue=False,
        titre="Diviser, déplacer, réunir ; l'addition d'une part",
        role="Serveur (Brice 1001) ; Caissière (Clarisse 2001)", base=BASE,
        prerequis="Tables 5, 6, 9 libres.",
        but="Diviser et déplacer ne sont pas des annulations ; l'addition d'une part s'imprime sans "
            "que la part disparaisse (18.0.1.0.8).",
        etapes=[
            ("Brice ouvre la table 5 (1001, 3) : Poulet DG, deux Soda 33 cl, Café expresso, Thé ; "
             "« J'envoie ». Il ouvre la table 6 (1001, 4) : « Ndolé viande » ; « J'envoie ».",
             "Tables 5 et 6 vertes.", ""),
            ("Clarisse, table 5, 2001, « Actions » → « Diviser l'addition », tout sélectionner, "
             "« Créer l'addition à part ».",
             "Refus : « Toute l'addition est sélectionnée : il n'y a rien à diviser. Encaissez la "
             "table directement. »", "R57"),
            ("Ne garder que « Café expresso » et « Thé » ; « Créer l'addition à part ».",
             "Une part « 5B » porte ces deux produits ; aucune fenêtre d'annulation.", "R57 R41 R58"),
            ("Sur la part : « Addition ».",
             "L'aperçu de l'addition de la part s'affiche ; après l'impression, la caisse reste sur la "
             "part (elle ne disparaît plus).", ""),
            ("Sur la part : « J'encaisse », « Espèces », « Valider ».",
             "Retour à la table 5, ouverte avec ses trois produits, « Clarisse » en haut.", "R59"),
            ("Table 5 : diviser un « Soda 33 cl », puis sur la part « Déplacer ou réunir » → table 6.",
             "Le soda est sur la table 6 et plus sur la 5 ; aucune annulation.", "R60 R62 R41"),
            ("Table 5 : diviser « Poulet DG », « Déplacer ou réunir » → table 9 (libre).",
             "« Table 9 — combien de personnes ? » ; toucher 3 : la table 9 est occupée.", "R61 R25"),
            ("Clarisse ouvre la table 9 (2001), « Déplacer ou réunir » → table 6.",
             "La table 6 porte tout, « 7 personnes », sa durée reste celle de sa première ouverture ; "
             "la table 9 redevient grise.", "R53 R56 R70"),
            ("Avec une imprimante de cuisine seulement : regarder l'imprimante.",
             "Aucun bon renvoyé pour la division, le déplacement, la réunion.", "R54 R58 R62"),
        ],
        captures=[], encadres=[("attention", "Une part qui n'est plus sur le plan se retrouve par "
                                 "≡ → « Commandes » (code de la caissière).")],
    ),
    dict(
        id="B09", partie="B", joue=False,
        titre="Produit épuisé, entrée de stock, hors connexion",
        role="Manager (gestion) ; Serveurs (Brice 1001, Nadège 1002)", base=BASE,
        prerequis="Table 4 ouverte par Brice ; un onglet de gestion avec manager / manager.",
        but="Un produit suivi sans stock est refusé ; une entrée de stock le rend vendable en moins "
            "d'une minute.",
        etapes=[
            ("Gestion : Inventaire → Produits → Produits → « Bière importée 33 cl » → « Mettre la "
             "quantité à jour » → 0.", "Le stock vaut 0.", ""),
            ("Caisse : Brice, table 4, Bar > Bières, « Bière importée 33 cl ».",
             "Notification « Produit épuisé » : « Plus de Bière importée 33 cl en stock. Si la "
             "bouteille est bien là, demandez au manager d'enregistrer l'entrée de stock : la vente "
             "repassera aussitôt. »", "R75"),
            ("Gestion : « Bière brune 65 cl » → 2. Nadège ouvre la table 2 (1002, 2), deux « Bière "
             "brune 65 cl », « J'envoie ».", "Les deux dernières sont parties sur la table 2.", "R78"),
            ("Sur l'autre poste, Brice (table 4) touche « Bière brune 65 cl ».",
             "Refusé (« Produit épuisé ») au plus tard une minute après l'envoi.", "R78"),
            ("Gestion : « Bière importée 33 cl » → 24.", "Le stock vaut 24.", "R72"),
            ("Caisse, sans recharger : dans la minute, « Bière importée 33 cl ».",
             "La vente passe. Retirer la ligne (⌫, ⌫).", "R72 R76"),
            ("« Poulet DG » (non suivi).", "La vente passe toujours ; retirer.", "R77"),
            ("Gestion : Inventaire → Analyse → Historique des mouvements, filtre de la semaine.",
             "Les saisies de stock y sont, datées et au nom du manager.", "R73 R74"),
            ("Couper le réseau du poste de Brice ; ajouter « Bière importée 33 cl ».",
             "La vente passe (aucun contrôle de stock hors connexion).", "R79"),
            ("Ligne des bières envoyées, ⌫, ⌫, « 1 », 3001.",
             "« Pas de réseau : annuler est impossible pour l'instant. Réessayez dans un moment. » ; "
             "« Retour », retirer la bière, rétablir le réseau.", "R79"),
        ],
        captures=[("restaurant/09_produit_epuise.jpg", "« Produit épuisé ».")],
        encadres=[("reflexe", "Saisir le stock de départ de chaque boisson suivie avant le premier "
                   "service : sinon la caisse refuse ces produits dès l'ouverture.")],
    ),
    dict(
        id="B10", partie="B", joue=False,
        titre="Le plan en couleurs et le retour au plan",
        role="Intégrateur (admin) ; Brice 1001 ; Clarisse 2001", base=BASE,
        prerequis="Caisse ouverte ; table 11 libre.",
        but="Le délai de l'orange se règle et s'applique à la réouverture ; un poste laissé seul "
            "revient au plan.",
        etapes=[
            ("Admin : Paramètres → « Restaurant » → « Délai avant l'orange (minutes) » : 90.",
             "La phrase dit aussitôt « Une table ouverte depuis plus de 90 minutes passe à l'orange "
             "sur le plan… ».", "R69"),
            ("Taper 2, « Enregistrer » ; recharger la caisse.",
             "Légende « Orange : ouverte depuis plus de 2 min, proposez l'addition ».", "R69"),
            ("Brice ouvre la table 11 (1001, 1), « Thé », « J'envoie » ; ne plus toucher l'écran.",
             "Table verte « 0 min », « 1 min », orange au plus tard à 3 minutes.", "R66 R71"),
            ("Brice rouvre la table 11 ; ne plus toucher l'écran pendant 5 minutes.",
             "La phrase d'état donne la même durée ; après 5 minutes, retour seul au plan verrouillé.",
             "R67 R71"),
            ("Clarisse encaisse la table 11.", "La table redevient grise, sans durée.", "R68"),
            ("Remettre 60, enregistrer, recharger la caisse. En vrai service : une table de plus d'une "
             "heure.", "Légende « plus de 60 min » ; durée écrite « 1 h 05 ».", "R66 R71"),
        ],
        captures=[("restaurant/08_plan_en_couleurs.jpg", "Le plan en couleurs.")],
        encadres=[],
    ),
    dict(
        id="B11", partie="B", joue=False,
        titre="Espèces, fermeture de la caisse et rapports du soir",
        role="Brice 1001 ; Hervé 3001 ; Manager ; chef / chef", base=BASE,
        prerequis="B04 à B10 joués ; la table 2 (B09) encore ouverte.",
        but="Seul un chef de salle sort des espèces et ferme ; les tables encore ouvertes sont "
            "annulées avec un motif ; le rapport de fermeture et celui des annulations.",
        etapes=[
            ("Brice : ≡ → « Entrée ou sortie d'espèces », 1001.",
             "« Seul un chef de salle ou le manager peut sortir ou entrer des espèces. »", "R14 R10"),
            ("Brice : ≡ → « Fermer la caisse », 1001.",
             "« Seul un chef de salle ou le manager ferme la caisse. »", "R14 R10"),
            ("Hervé : ≡ → « Fermer la caisse », 3001.",
             "Fenêtre de fermeture : nombre de commandes et montant ; ligne « Entrées et sorties "
             "d'espèces ».", "D04"),
            ("Taper dans « Comptage de caisse » 1 000 de moins que le montant attendu, « Fermer la "
             "caisse ».",
             "Odoo affiche l'écart et demande « Écart de règlement » : « Poursuivre ».", "D04"),
            ("Message suivant.",
             "« 1 table est encore ouverte : 2. Encaissez-la, ou annulez-la avec un motif, avant de "
             "fermer. », « Voir les tables », « Annuler ces tables ».", "R42"),
            ("« Annuler ces tables », « Client parti ».",
             "Le code n'est pas redemandé ; la caisse se ferme.", "R42"),
            ("Manager : Point de Vente → Analyse → Rapport de session (session du jour).",
             "Blocs « Tables et personnes » et « Annulations » ; quantités vendues de chaque "
             "produit ; l'écart de caisse.", "R95 R92 D04 D07"),
            ("Point de Vente → Analyse → Analyse AITE → Écarts de caisse.",
             "La session du jour avec son écart de 1 000 FCFA.", "D04"),
            ("Restaurant → Annulations (filtre « Aujourd'hui »).",
             "Colonnes Date, Table, Produit, Quantité, Montant TTC, Demandée par, Autorisée par, "
             "Motif, Précision, totaux ; « Demandée par » Brice, « Autorisée par » Hervé pour la bière.",
             "R46 R47 R80"),
            ("Chercher les tables 5, 6, 9.", "Aucune ligne : division, déplacement, réunion n'y sont "
             "pas.", "R41 R48 R55 R58 R62 R82"),
            ("Filtre « Sans code ».", "La ligne de la table 3, sans « Autorisée par ».", "R52"),
            ("« Regrouper par » « Autorisée par », puis « Motif ».",
             "Un sous-total par responsable, puis par motif.", "R81"),
            ("Ouvrir une ligne, essayer de la modifier, puis de la supprimer.",
             "« Une annulation enregistrée ne se modifie pas et ne s'efface pas : c'est la trace "
             "demandée par le manager. »", "R49"),
            ("chef / chef : Restaurant → Annulations.",
             "Les mêmes lignes ; aucun autre menu.", "R83"),
        ],
        captures=[("restaurant/15_fermeture_une_table_encore_ouverte.jpg",
                   "Fermeture : une table encore ouverte."),
                  ("restaurant/22_annulations_du_jour.jpg", "Restaurant → Annulations.")],
        encadres=[],
    ),
    dict(
        id="B12", partie="B", joue=False,
        titre="Personnes et tables, une journée qui se compte juste",
        role="Serveurs ; Clarisse 2001 ; Manager", base=BASE,
        prerequis="B11 joué. Clarisse rouvre la caisse (2001, « J'ouvre la caisse »).",
        but="Le rapport « Personnes et tables » compte les tables servies et leurs personnes.",
        etapes=[
            ("Brice : table 2 (2 personnes), « Médoc » et deux « Poulet DG », « J'envoie ». "
             "Table 4 (4 personnes) : quatre « Pizza Marguerite Petit », « J'envoie ».",
             "Table 2 : 30 000 FCFA ; table 4 : 20 000 FCFA.", ""),
            ("Nadège : table 7 avec 5 personnes, cinq « Poulet DG », « J'envoie » ; rouvrir, toucher "
             "« 5 personnes », puis 7.", "Le bouton dit « 7 personnes ».", "R26"),
            ("Retoucher « 7 personnes », chercher un 0.", "Aucun moyen de saisir 0.", "R28"),
            ("Clarisse encaisse les tables 2, 4, 7.", "Les trois tables sont grises.", ""),
            ("Manager : Point de Vente → Analyse → Personnes et tables (« Aujourd'hui »).",
             "Tables 3, Personnes 13, Total 75 000 sur la même page ; la table 7 compte 7.",
             "R91 R27"),
            ("Point de Vente → Tableau de bord.",
             "Prix moyen par personne affiché (tableau d'Odoo ; il compte aussi les ventes sans "
             "table).", "R97"),
            ("Brice : table 5 (6 personnes), six « Café expresso » ; Clarisse divise trois cafés, "
             "encaisse la part puis la table. Relire le rapport.",
             "Tables 4, Personnes 19 : la table divisée compte une fois.", "R93"),
            ("Brice laisse la table 8 ouverte ; Hervé annule la table 9 après un « Thé ». Relire.",
             "Inchangé : ni ouverte ni annulée ne comptent.", "R94"),
            ("Clarisse touche « + » (2001) et encaisse trois ventes sans table. Relire.",
             "Les ventes sans table sont à part (colonne « Ventes sans table »).", "R96"),
            ("Vue Liste, « Regrouper par » « Ouverte par », puis « Encaissée par ».",
             "Tables, personnes et montants par serveur, puis par personne qui a encaissé.", "R07"),
            ("Filtre « Cette semaine » ; puis un filtre personnalisé sur quinze jours (jj/mm/aaaa).",
             "Du lundi à aujourd'hui ; puis seules les ventes de la période.", "R88 R89"),
            ("Une période sans vente, en vue Liste ; Tableau de bord sur cette période.",
             "« Aucune addition encaissée sur cette période. … Changez la période pour voir les autres "
             "jours. » ; aucune moyenne par personne.", "R90 R98"),
            ("Point de Vente → Analyse → Détails des ventes, même période.",
             "Quantité et montant de chaque produit, par catégorie.", "R92"),
        ],
        captures=[("restaurant/20_personnes_et_tables.jpg", "Personnes et tables.")],
        encadres=[],
    ),
    dict(
        id="B13", partie="B", joue=False,
        titre="Les droits niveau par niveau",
        role="Les codes 1001, 2001, 3001, 4001 ; Manager", base=BASE,
        prerequis="Caisse ouverte, des additions payées dans la journée.",
        but="Le tableau des droits du guide est appliqué par la caisse ; un niveau changé "
            "s'applique à la réouverture.",
        etapes=[
            ("Avec chaque code : « J'encaisse », ≡ → « Entrée ou sortie d'espèces », ≡ → « Fermer la "
             "caisse », annuler un produit envoyé (abandonner chaque geste).",
             "Serveur : refusé partout ; caissière : encaisse ; chef de salle : en plus espèces, "
             "annulation, fermeture ; manager : tout.", "R10"),
            ("Brice identifié sur une table : « Actions ».",
             "Pas de « Remboursement », pas de « Liste de prix ».", "R10 R14"),
            ("Clarisse : ≡ → « Commandes » (2001), une addition payée, « Remboursement ».",
             "« Seul le manager peut rembourser une addition payée. » ; avec 4001, le remboursement "
             "s'ouvre (ne pas valider).", "R10"),
            ("Avec une imprimante : Brice, ≡ → « Imprimer le rapport », 1001.",
             "« Seuls la caissière, le chef de salle et le manager impriment le rapport des ventes. »",
             "R14 R10"),
            ("Manager : Employés → « Nadège » → « Niveau en caisse » = Caissière ; recharger la caisse ; "
             "Nadège encaisse une table.",
             "Le paiement s'ouvre. Remettre Nadège en Serveur.", "R11"),
        ],
        captures=[], encadres=[],
    ),
    # ═════════════════════════ C. L'ARDOISE ═══════════════════════════════
    dict(
        id="C01", partie="C", joue=False,
        titre="Le mode « Ardoise client » et l'ardoise à la caisse",
        role="Intégrateur (admin) ; Sandrine 4001 ; Clarisse 2001 ; Hervé 3001", base=BASE,
        prerequis="B01 joué (« Ardoise client » parmi les modes de la caisse) ; caisse ouverte.",
        but="L'ardoise ne naît que d'une addition réglée, et seul le manager la propose en "
            "restaurant.",
        etapes=[
            ("Point de Vente → Configuration → Modes de paiement → « Ardoise client ».",
             "« Vente à crédit (ardoise) » cochée, phrase « Case cochée : chaque ticket réglé avec ce "
             "mode ouvre une ardoise au nom du client (POS Crédit → Ardoises). » ; pas de plafond par "
             "client.", "F01"),
            ("Brice ouvre la table 10 (2), « Poulet DG », « J'envoie » ; Clarisse : table 10, 2001, "
             "« J'encaisse ».", "Ni « Mettre sur ardoise » ni « Ardoise client ».", "R101"),
            ("Sandrine : table 10, 4001, « J'encaisse ».",
             "« Mettre sur ardoise » et « Ardoise client » sont proposés.", "R101"),
            ("« Mettre sur ardoise » sans client.",
             "« Sélectionnez d'abord un client pour une vente à crédit. »", ""),
            ("Choisir un client, le mode « Ardoise client », puis « Plan » sans valider ; admin : POS "
             "Crédit → Ardoises.", "Aucune ardoise pour cette table.", "R100"),
            ("Hervé annule la table 10 (« Client parti »). Relire Ardoises.",
             "Toujours aucune ardoise.", "R100"),
            ("Brice : table 3, « Poulet DG », « J'envoie » ; Sandrine : 4001, « J'encaisse », client "
             "« Client Ardoise A », « Ardoise client », « Valider ».",
             "POS Crédit → Ardoises : une ardoise de 5 000 FCFA au nom du client, état « Ouverte », "
             "sévérité « Récente ».", "R100 F02"),
            ("Ouvrir le contact « Client Ardoise A ».", "Bouton « Ardoises » : 1.", "F02"),
        ],
        captures=[], encadres=[],
    ),
    dict(
        id="C02", partie="C", joue=False,
        titre="Rembourser une ardoise : en partie, en Mobile Money, en totalité",
        role="Manager ou responsable du crédit (POS Crédit)", base=BASE,
        prerequis="C01 joué (ardoise de 5 000 FCFA).",
        but="Le reste dû baisse du montant exact ; chaque remboursement garde sa date et son moyen.",
        etapes=[
            ("POS Crédit → Ardoises → l'ardoise → « Enregistrer un remboursement ».",
             "Fenêtre « Enregistrer un remboursement » : « Reste dû actuel » 5 000, « Montant à "
             "encaisser », « Moyen de paiement » (Espèces d'office), « Date ».", "F04"),
            ("« Montant à encaisser » 2 000, « Espèces », « Encaisser ».",
             "« Déjà remboursé » 2 000, « Reste dû » 3 000 ; une ligne de remboursement datée, "
             "« Espèces ».", "F04"),
            ("« Enregistrer un remboursement » : 1 000, « MTN Mobile Money », « Réf. transaction » "
             "« MP-0001 », « Encaisser ».",
             "Reste dû 2 000 ; la ligne porte « MTN Mobile Money » et sa référence.", "F09"),
            ("POS Crédit → Remboursements, « Regrouper par » « Moyen de paiement ».",
             "Espèces et MTN Mobile Money séparés.", "F09"),
            ("Rembourser 2 000 en espèces.",
             "« Reste dû » 0 ; état « Réglée » ; le client n'apparaît plus dans « Top débiteurs » de "
             "Recouvrement.", "F05"),
            ("Point de Vente → Configuration → Paramètres, bloc « Ardoises / Crédit POS ».",
             "« Comptabiliser les remboursements », « Compte client (ardoises) », « Journal des "
             "remboursements » : régler avec le comptable.", "F10"),
            ("Si la comptabilisation est cochée : Facturation → Comptabilité → Pièces comptables, "
             "filtrer sur le client.",
             "L'octroi (vente au compte client) et chaque remboursement mouvementent le compte "
             "client, sans écriture en double.", "F10"),
        ],
        captures=[], encadres=[],
    ),
    dict(
        id="C03", partie="C", joue='partiel', vu="Étape 1 seulement, sur une base sans ardoise : « POS Crédit — Recouvrement » s'affiche, tous les compteurs à 0.",
        titre="Suivre et relancer les ardoises : âge, balance âgée, recouvrement",
        role="Manager ou responsable du crédit", base=BASE,
        prerequis="C01 joué ; trois clients avec une ardoise ouverte chacun (Client Ardoise A, B, C).",
        but="Les ardoises se classent par âge ; le tableau « Recouvrement » se lit juste.",
        etapes=[
            ("POS Crédit → Recouvrement.",
             "Titre « POS Crédit — Recouvrement » ; « Encours total (dû) », « Recouvré (période) », "
             "« Nouvelles ardoises (période) », « Taux de recouvrement » (écran #1).", "F08"),
            ("Ouvrir l'ardoise de B : « Date d'ouverture » 45 jours plus tôt ; celle de C : 95 jours "
             "plus tôt ; enregistrer.",
             "Âge (j) 45 et 95 ; sévérité « En retard » puis « Critique ».", "F03"),
            ("POS Crédit → Ardoises : colonnes « Âge (j) », « Sévérité » ; filtres « En retard "
             "(+30j) », « Critiques (+60j) ».", "A Récente, B En retard, C Critique.", "F03"),
            ("Recouvrement : « Balance âgée (aging) de l'encours ».",
             "Chaque reste dû dans sa tranche ; la somme égale « Encours total (dû) ».", "F06"),
            ("« Top débiteurs ».",
             "Classés par montant ; « Âge max » = l'ardoise la plus ancienne du client.", "F07"),
            ("Période « Ce mois » : comparer « Recouvré (période) » et « Nouvelles ardoises "
             "(période) » aux remboursements et ardoises du mois.",
             "Les montants correspondent ; « Taux de recouvrement » = recouvré / (encours + recouvré).",
             "F08"),
            ("Bloc CAISSE : choisir « Restaurant », puis « Bar » (si une ardoise y a été faite en H01), "
             "puis « Toutes les caisses ».",
             "L'encours se répartit par caisse ; le total est retrouvé sur « Toutes les caisses ».", "F11"),
            ("Contact « Client Ardoise C » → bouton « Ardoises ».",
             "La liste de ses ardoises avec « Date d'ouverture », « Montant initial », « Déjà "
             "remboursé », « Reste dû » et leurs totaux : c'est le relevé à remettre (Imprimer ou "
             "exporter la liste). La relance se fait à la main.", "F12"),
        ],
        captures=[("integrateur/19_pos_credit_recouvrement.jpg",
                   "POS Crédit → Recouvrement sur une base neuve.")],
        encadres=[("attention", "Il n'y a pas de relevé imprimable dédié : la liste des ardoises "
                   "du client, filtrée, sert de relevé.")],
    ),
    # ═════════════════════════ D. ANALYSE DES VENTES ══════════════════════
    dict(
        id="D01", partie="D", joue='partiel', vu="Étapes 1 et 2 : menu Analyse tel qu'écrit ; tableau de bord : CA 4 000, marge 2 300, CMV 1 700, 1 transaction.",
        titre="Lire l'analyse des ventes après un service",
        role="Manager (Manager — Analyses POS)", base=BASE,
        prerequis="Des ventes encaissées (B07, B12) ; produits du Bar avec leur coût (I02).",
        but="Le chiffre d'affaires, les tickets, le panier et la marge correspondent aux ventes.",
        etapes=[
            ("Point de Vente → Analyse.",
             "« Commandes », « Détails des ventes », « Rapport de session », « Personnes et tables », "
             "puis « Analyse AITE » : « Tableau de bord », « Par caisse », « Sessions POS », « Par "
             "catégorie », « Écarts de caisse », « Tableau croisé & graphique ».", ""),
            ("Analyse AITE → Tableau de bord, période « Aujourd'hui ».",
             "« Chiffre d'affaires », « Marge brute », « CMV (coût marchandises) », « Transactions », "
             "« Panier moyen » ; après la seule vente de B04 (2 bières, 1 soda) : 4 000 FCFA, 1 "
             "transaction, CMV 1 700, marge 2 300 (écran #1).", "D09 D11"),
            ("Bloc HEURE : « Soir 18–23h », puis JOUR : le jour du service.",
             "Les indicateurs ne retiennent que les ventes de la tranche et du jour.", "D09"),
            ("Onglet « Marges & CMV ».",
             "Pour chaque produit : marge = prix de vente − coût (Bière blonde 65 cl : 1 500 − 650 = "
             "850 par unité) ; un plat sans coût paraît à 100 %.", "D11"),
            ("Onglet « Par catégorie ».",
             "« Bar / Bières », « Bar / Sans alcool / Sodas » avec leur marge et leur CMV.", "D11"),
            ("Direction → onglet « Ventes (POS) » : « Chaleur des ventes — jours × heures ».",
             "Les cases foncées tombent sur les jours et heures des ventes jouées ; aucune case "
             "ailleurs.", "D10"),
            ("Analyse AITE → Tableau croisé & graphique ; « Regrouper par » « Serveur », puis "
             "« Encaissée par ».",
             "Brice et Nadège distingués ; « Encaissée par » donne Clarisse, Sandrine ; le compte de "
             "la tablette s'affiche « Compte Odoo ».", "D12 R102 R07"),
            ("Même écran, « Regrouper par » « Caissier ».",
             "Le compte Odoo de la caisse (« Caisse de la salle ») : en restaurant, c'est « Serveur » "
             "qui donne le vendeur.", "D12"),
        ],
        captures=[("integrateur/15_analyse_aite_tableau_de_bord.jpg",
                   "Analyse AITE → Tableau de bord après la table 4.")],
        encadres=[],
    ),
    dict(
        id="D02", partie="D", joue=False,
        titre="Deux caisses : cartes cloisonnées, remise tracée",
        role="Intégrateur (admin) ; vendeur du Bar", base=BASE,
        prerequis="La caisse « Bar » de I01.",
        but="Chaque caisse ne montre que sa carte ; une remise (hors restaurant) se retrouve dans "
            "les analyses.",
        etapes=[
            ("Paramètres → caisse « Bar » : « Limiter les catégories » → « Bar » ; « Remises » "
             "cochée ; « Enregistrer ».", "Réglages enregistrés.", "D05"),
            ("Point de Vente → « Bar » → « Ouvrir la caisse ».",
             "Caisse d'Odoo classique (ni code ni plan) ; seule la famille « Bar » et ses produits.",
             "D05"),
            ("Ouvrir la caisse « Restaurant » sur un autre poste.",
             "Toutes les familles de la carte ; les deux caisses n'affichent pas la même carte.", "D05"),
            ("Bar : « Médoc », « Rem.% » au pavé, 10 ; « Paiement », « Espèces », « Valider ».",
             "Ligne remisée de 10 % : 18 000 FCFA ; ticket validé.", "D06"),
            ("Gestion : Point de Vente → Commandes → Commandes → la commande du Bar.",
             "La ligne porte la remise de 10 % ; la commande, le vendeur.", "D06"),
            ("Direction → « À traiter » (période « Aujourd'hui »).",
             "Si les remises dépassent 3 % du CA : « Remises élevées (… du CA) », « par vendeur ».", "D06"),
        ],
        captures=[], encadres=[("attention", "Sur la caisse « Restaurant », les remises sont "
                                 "désactivées pour tous (touche « % » grisée) : la remise se teste "
                                 "sur une autre caisse.")],
    ),
    dict(
        id="D03", partie="D", joue=False,
        titre="Vendre hors connexion",
        role="Vendeur du Bar", base=BASE,
        prerequis="Caisse « Bar » ouverte.",
        but="Les ventes continuent sans réseau et remontent sans doublon.",
        etapes=[
            ("Couper le réseau du poste (Wi-Fi, ou outils de développement → Réseau → Hors ligne).",
             "La caisse reste affichée.", "D08"),
            ("Encaisser deux ventes en espèces.", "Les deux tickets sont validés.", "D08"),
            ("Rétablir le réseau, attendre une minute.",
             "Point de Vente → Commandes → Commandes : les deux ventes, une fois chacune.", "D08"),
        ],
        captures=[], encadres=[],
    ),
    dict(
        id="D04", partie="D", joue=False,
        titre="Les ventes par famille",
        role="Manager", base=BASE,
        prerequis="Ventes de bières, vins, sodas et plats (B12).",
        but="Une famille additionne ses sous-familles ; un produit ne compte qu'une fois.",
        etapes=[
            ("Analyse AITE → Tableau croisé & graphique ; « Favoris » → « Ventes par famille ».",
             "Lignes Famille > Sous-famille (« Bar / Bières »…), une colonne « Total ».", "R84"),
            ("Rechercher « Pizzas », choisir « Famille ».", "Seules les pizzas.", "R85"),
            ("Remplacer par « Sans alcool ».", "« Vins » n'est pas ramené.", "R85"),
            ("Rechercher « Médoc », choisir « Produit ».", "Seules les ventes du Médoc.", "R86"),
            ("Sans filtre : additionner les familles.", "La somme est le total.", "R87"),
        ],
        captures=[("restaurant/23_ventes_par_famille.jpg", "Ventes par famille (base du restaurant AITE).")],
        encadres=[],
    ),
    # ═════════════════════════ E. LE STOCK ════════════════════════════════
    dict(
        id="E01", partie="E", joue='partiel', vu='Étapes 1, 2, 4 et 5 : tableau de bord, réglages « AITE Stock » (valeurs par défaut écrites), fenêtre « ⚙ Configurer les alertes ».',
        titre="Le tableau de bord du stock : valeur et réglages des alertes",
        role="Responsable Inventaire (admin)", base=BASE,
        prerequis="I02 et I03 joués (19 boissons suivies avec coût et stock de départ).",
        but="La valeur du stock se lit juste ; les alertes se règlent sans code.",
        etapes=[
            ("Inventaire → Tableau de bord AITE.",
             "« Stock & Inventaire — Tableau de bord » ; onglets « Tableau de bord », « Alertes & "
             "réappro », « Stock complet », « Rotation & dormants », « Inventaires & écarts », "
             "« Mouvements » (écran #1).", ""),
            ("Lire « Valeur stock — coût d'achat » et « Valeur stock — prix de vente ».",
             "Sur la base de démonstration avant toute vente : 19 références ; la valeur au coût est "
             "la somme quantité × « Coût » (Bière blonde 65 cl : 48 × 650 = 31 200).", "H01"),
            ("Onglet « Stock complet », rechercher « Bière blonde ».",
             "Quantité par emplacement, valeur, couverture, statut.", "H01"),
            ("Paramètres → « AITE Stock ».",
             "Bloc « Alertes de réapprovisionnement » : « Stock de sécurité » 2, « Horizon de "
             "commande » 7, « Seuil critique » 3, « Seuil dormant » 60, « Délai réappro par défaut » "
             "3, « Seuil de coulage » 2,0 % ; chacun avec sa phrase (écran #2).", ""),
            ("Onglet « Alertes & réappro » → « ⚙ Configurer les alertes ».",
             "Fenêtre « Paramètres globaux » et « Réglages par produit » (délai, seuil manuel, "
             "alerte), « Enregistrer la configuration » (écran #3).", "H03"),
            ("Produit « Bière brune 65 cl » → onglet « Réappro AITE » : « Seuil manuel (point de "
             "commande) » 30, enregistrer.",
             "Tableau de bord : « Bière brune 65 cl » passe « Sous seuil » ; « Sous seuil de "
             "commande » compte 1 référence.", "H02"),
        ],
        captures=[("integrateur/09_tableau_de_bord_stock.jpg", "Inventaire → Tableau de bord AITE."),
                  ("integrateur/06_reglages_aite_stock.jpg", "Paramètres → AITE Stock."),
                  ("integrateur/07_configurer_les_alertes.jpg", "« ⚙ Configurer les alertes ».")],
        encadres=[("attention", "Ces alertes sont celles d'AITE (ventes des 30 derniers jours, "
                   "délai, sécurité). Les « Règles de réapprovisionnement » d'Odoo (Opérations → "
                   "Réassort) sont indépendantes : elles proposent des demandes de prix, pas les "
                   "statuts du tableau de bord.")],
    ),
    dict(
        id="E02", partie="E", joue='partiel', vu='Étapes 1 et 2 : Bière blonde 48 → 46 après la table 4 ; Ventes/j 0,1, point de commande 1.',
        titre="Ventes en caisse : stock, couverture, statuts",
        role="Responsable Inventaire ; caisse", base=BASE,
        prerequis="E01 joué ; des ventes de bières à la caisse (B04, B12).",
        but="La caisse décrémente le stock une fois ; ventes/jour, couverture et suggestion suivent.",
        etapes=[
            ("Inventaire → Produits → « Bière blonde 65 cl » avant puis après la table 4 de B04.",
             "48, puis 46 : la vente de 2 bières décrémente de 2, une seule fois.", "H09"),
            ("Tableau de bord AITE → « Alertes & réappro ».",
             "Colonnes « Stock », « Ventes/j », « Couverture », « Point de cmde », « À commander », "
             "« Statut » ; Bière blonde : Ventes/j 0,1 (2 en 30 jours), point de commande 1.", "H06"),
            ("Produit « Bière importée 33 cl » : « Mettre la quantité à jour » → 1 ; puis vendre 1 à la "
             "caisse (Sandrine, une table).",
             "Statut « Critique » (couverture sous 3 jours), puis « Rupture » à zéro ; « En rupture » "
             "compte 1.", "H02"),
            ("Lire « À commander » de la Bière importée.",
             "La quantité suggérée = ventes moy./jour × (délai + horizon) − stock (formule rappelée "
             "dans l'onglet « Réappro AITE »).", "H03"),
            ("Onglet « Rotation & dormants ».",
             "Les vins et whiskies non vendus depuis 30 jours sont « Dormant », avec leur valeur "
             "immobilisée.", "H07"),
        ],
        captures=[], encadres=[],
    ),
    dict(
        id="E03", partie="E", joue='oui', vu='Bière brune comptée 20 au lieu de 24 : -4, -2 800 FCFA ; pertes 2 800 FCFA, coulage 70,0 % du CA estimé (4 000), seuil 2,0 %.',
        titre="Inventaire tournant, écarts et coulage",
        role="Magasinier (Inventaire : Utilisateur) ; Responsable Inventaire", base=BASE,
        prerequis="E01 joué.",
        but="Un comptage différent du stock donne un écart valorisé, et le coulage le suit.",
        etapes=[
            ("Inventaire → Opérations → Inventaire physique ; rechercher « Bière brune ».",
             "Colonnes « Produit », « Quantité en stock », « Quantité comptée », « Différence » "
             "(écran #1).", "H04"),
            ("« Quantité comptée » 20 au lieu de 24 ; enregistrer.",
             "« Différence » -4,00 ; boutons « Historique », « Appliquer », « Effacer ».", "H04"),
            ("« Appliquer ».", "« Quantité en stock » 20.", "H04"),
            ("Tableau de bord AITE → « Inventaires & écarts ».",
             "« Journal des écarts & casses » : « Ajustement inv. », Bière brune 65 cl, -4, -2 800 FCFA "
             "(4 × 700) ; « Pertes (écarts négatifs + casse) » 2 800 FCFA (écran #2).", "H04 H05"),
            ("Lire « Coulage (période) » et « Seuil de coulage ».",
             "Coulage = pertes / « CA estimé (période) » ; au-dessus de 2,0 % la carte passe en "
             "alerte et Direction → « À traiter » affiche « Coulage au-dessus du seuil (… > 2,0 %) ».",
             "H05"),
        ],
        captures=[("integrateur/08_inventaire_physique.jpg", "Inventaire physique : la quantité comptée."),
                  ("integrateur/10_stock_inventaires_et_ecarts.jpg", "« Inventaires & écarts ».")],
        encadres=[("attention", "Le stock de départ saisi en « Mettre la quantité à jour » est lui "
                   "aussi un ajustement : le premier mois, « Écarts d'inventaire (période) » et "
                   "« Écart net » le comptent. Le coulage, lui, ne lit que les écarts négatifs et la "
                   "casse.")],
    ),
    dict(
        id="E04", partie="E", joue=False,
        titre="Deux emplacements : cave et bar",
        role="Responsable Inventaire (admin)", base=BASE,
        prerequis="E01 joué.",
        but="Un transfert cave → bar se trace et se lit par emplacement.",
        etapes=[
            ("Inventaire → Configuration → Paramètres : cocher « Emplacements de stockage », "
             "« Enregistrer ».", "Le menu Configuration propose « Emplacements ».", "H08"),
            ("Configuration → Emplacements → Nouveau : « Bar », « Emplacement parent » WH, type "
             "« Emplacement interne » ; idem « Cave ».", "WH/Bar et WH/Cave existent.", "H08"),
            ("Opérations → Transferts → Nouveau : « Type d'opération » « Transferts internes », de "
             "WH/Stock vers WH/Bar, 12 « Bière blonde 65 cl » ; « Marquer comme à faire », "
             "« Valider ».", "Le transfert est « Terminé ».", "H08"),
            ("Tableau de bord AITE : bloc EMPLACEMENT, choisir WH/Stock puis WH/Bar.",
             "La bière a 12 de moins dans WH/Stock et 12 dans WH/Bar ; « Mouvements » montre le "
             "transfert ; « Transferts internes » compte 12 unités.", "H08"),
        ],
        captures=[], encadres=[("attention", "La caisse vend depuis l'emplacement de son type "
                                 "d'opération (WH/Stock d'office) : un stock déplacé ailleurs n'est "
                                 "plus vendable par elle, et le refus des épuisés s'applique.")],
    ),
    # ═════════════════════════ F. LES ACHATS ══════════════════════════════
    dict(
        id="F01", partie="F", joue='partiel', vu='Étapes 2 à 5 : 24 × 700 = 16 800 FCFA, « Bon de commande fournisseur », réception de 18, « Créer un reliquat ? », stock 46 → 64.',
        titre="Commander à un fournisseur et réceptionner",
        role="Acheteur (Achats : Utilisateur)", base=BASE,
        prerequis="I03 joué. Un fournisseur « Fournisseur Boissons (démo) » (contact société).",
        but="Une commande confirmée au bon montant ; une réception partielle laisse un reliquat.",
        etapes=[
            ("Produit « Bière blonde 65 cl » → onglet « Achats » : ajouter le fournisseur, « Prix » "
             "700 ; enregistrer.", "Le prix d'achat du fournisseur est enregistré.", "I01"),
            ("Achats → Commandes → Demandes de prix → Nouveau ; « Fournisseur » ; « Ajouter un "
             "produit » « Bière blonde 65 cl », quantité 24.",
             "« Prix unitaire » 700 proposé ; « Montant hors taxes » 16 800 FCFA.", "I01"),
            ("« Confirmer la commande ».",
             "État « Bon de commande fournisseur » ; « Total » 16 800 FCFA ; bouton « 1 Réception » "
             "(écran #1).", "I01"),
            ("« Réceptionner les produits » ; « Quantité » 18 au lieu de 24 ; « Valider ».",
             "Fenêtre « Créer un reliquat ? » : « Créer un reliquat », « AUCUN RELIQUAT », "
             "« Ignorer » (écran #2).", "I03"),
            ("« Créer un reliquat ».",
             "Réception « Terminé » ; stock de la bière +18 seulement ; un reliquat de 6 reste attendu.",
             "I03"),
            ("Ouvrir le reliquat, « Valider » les 6.",
             "La commande est entièrement reçue ; stock +24 au total.", "I02"),
            ("Tableau de bord AITE (Achats) → « Commandes & réceptions ».",
             "« Journal des commandes » : la commande, « Prévue », « Reçue », « Complète », « Statut ».",
             "I02 I03"),
        ],
        captures=[("integrateur/11_commande_fournisseur_confirmee.jpg", "La commande confirmée."),
                  ("integrateur/12_reception_partielle_reliquat.jpg", "« Créer un reliquat ? ».")],
        encadres=[],
    ),
    dict(
        id="F02", partie="F", joue='partiel', vu='Facture 18 × 700 = 12 600 FCFA, échéance à 14 jours, « Comptabilisé » ; « Dette fournisseurs (401) » 12 600, « À payer sous 8–30 j » 12 600, « À échoir », « dans 14 j ». Étape 5 non jouée.',
        titre="La facture fournisseur et l'échéancier",
        role="Acheteur ; comptable (Facturation)", base=BASE,
        prerequis="F01 joué (réception de 18 validée).",
        but="La facture se rattache à la commande et tombe dans l'échéancier à la bonne semaine.",
        etapes=[
            ("Bon de commande → « Créer une facture fournisseur ».",
             "Facture brouillon reliée à la commande ; lignes des quantités reçues (18 × 700 = 12 600).",
             "I04"),
            ("« Date de facturation » aujourd'hui, « Date d'échéance » dans 14 jours ; « Confirmer ».",
             "Facture « Comptabilisé » ; boutons « Payer », « Avoir ».", "I04"),
            ("Achats → Tableau de bord AITE.",
             "« Dette fournisseurs (401) » 12 600 FCFA, 1 facture ouverte ; « À payer sous 7 j » 0 "
             "(écran #1).", "I05"),
            ("Onglet « Dettes & échéancier ».",
             "« À payer sous 8–30 j » 12 600 ; « Échéancier — 6 prochaines semaines » : la barre dans "
             "la semaine de l'échéance ; la facture « À échoir », « dans 14 j » (écran #2).", "I04 I05"),
            ("Ajouter une facture déjà échue (échéance il y a 10 jours) d'un autre fournisseur.",
             "« Factures échues » et la balance âgée (tranche 1-30 j) la comptent ; le total égale "
             "la somme des factures ouvertes.", "I05"),
        ],
        captures=[("integrateur/13_tableau_de_bord_achats.jpg", "Achats → Tableau de bord AITE."),
                  ("integrateur/14_achats_dettes_et_echeancier.jpg", "« Dettes & échéancier ».")],
        encadres=[],
    ),
    dict(
        id="F03", partie="F", joue='partiel', vu="Étape 1 : « Pas assez d'historique d'achats pour comparer les prix » ; « Avoirs & consignes » vide : « Aucune consigne enregistrée — cliquez « Gérer les consignes » ».",
        titre="Prix d'achat, ponctualité (OTIF) et consignes",
        role="Responsable Achats (Achats : Administrateur)", base=BASE,
        prerequis="F01 et F02 joués.",
        but="Lire la hausse de prix, l'OTIF et les consignes de casiers.",
        etapes=[
            ("Onglet « Prix & variations ».",
             "Sur une base neuve : « Pas assez d'historique d'achats pour comparer les prix » (fenêtre "
             "récente de 45 jours contre 120 à 210 jours).", "I06"),
            ("Avec un historique (base du client) : commander la même bière à 800 au lieu de 700.",
             "« Variations par produit » : « Prix N−6m » 700, « Prix actuel » 800, Δ +14,3 %, statut "
             "« Hausse forte » (seuil 5 %).", "I06"),
            ("Commande à « Arrivée prévue » hier, réceptionnée aujourd'hui en entier ; une autre reçue "
             "à temps mais incomplète.",
             "« Commandes & réceptions » : « Livré à temps et complet (OTIF) » ne compte ni la "
             "commande en retard ni l'incomplète (« Reçue incomplète »).", "I07"),
            ("Achats → Configuration → Consignes fournisseurs → Nouveau : le fournisseur, « Casiers "
             "consignés » 10, « Consigne / casier » 3 000.",
             "« Valeur immobilisée » 30 000.", "I08"),
            ("Tableau de bord → « Avoirs & consignes ».",
             "« Consignes en cours (4096) » 30 000 FCFA, 10 casiers ; ramener « Casiers consignés » "
             "à 4 : 12 000.", "I08"),
            ("Paramètres → « AITE Achats ».",
             "« Alerte échéance », « Tolérance retard livraison », « Seuil de dépendance "
             "fournisseur », « Seuil de hausse de prix », chacun avec sa phrase.", ""),
        ],
        captures=[], encadres=[("attention", "Le menu « Consignes fournisseurs » n'est visible "
                                 "que des responsables Achats ; les acheteurs lisent le registre par "
                                 "« Gérer les consignes ».")],
    ),
    # ═════════════════════════ G. LA DIRECTION ════════════════════════════
    dict(
        id="G01", partie="G", joue='partiel', vu="Étape 1 et PÉRIODE « Ce mois » : cockpit sans erreur, cartes telles qu'écrites.",
        titre="Ouvrir la vue Direction et filtrer",
        role="Gérant (Point de Vente : Administrateur + POS Crédit)", base=BASE,
        prerequis="Ventes (B07), ardoise (C01), stock (E03), facture fournisseur (F02) ; droits de I05.",
        but="Le cockpit s'affiche sans erreur et se recalcule à chaque filtre.",
        etapes=[
            ("Direction ; F12 → Console.",
             "« Direction — Vue consolidée », aucune erreur rouge en console ; « SANTÉ DE "
             "L'AFFAIRE » : « CA encaissé », « Marge brute réalisée », « Cash à risque », « Crédits "
             "clients − dettes fournisseurs » (écran #1).", "J01"),
            ("PÉRIODE : « Aujourd'hui », « Cette semaine », « Ce mois », puis Du … au … et "
             "« Appliquer ».",
             "Les cartes « période » changent à chaque clic ; les cartes « photo » (encours, dettes, "
             "stock) restent.", "J02"),
            ("CAISSE : « Restaurant », puis « Bar », puis « Toutes les caisses ».",
             "Le CA suit la caisse choisie ; « Toutes les caisses » retrouve la somme.", "J03"),
            ("HEURE : « Soir 18–23h » ; JOUR : un jour de la semaine.",
             "Seules les ventes de la tranche et du jour sont comptées.", "J04"),
            ("Faire défiler chaque onglet de VUE jusqu'en bas.",
             "Tout défile ; aucun bloc coupé.", "J10"),
        ],
        captures=[("integrateur/16_direction_vue_consolidee.jpg", "Direction — Vue consolidée.")],
        encadres=[],
    ),
    dict(
        id="G02", partie="G", joue='partiel', vu="Cash à risque « ardoises +30 j (0) + coulage (2 800) » = 2 800 FCFA ; crédits − dettes −12 600, « vos fournisseurs financent l'exploitation » ; « À traiter » : « Coulage au-dessus du seuil (70,0 % > 2,0 %) ». Étapes 3 et 5 non jouées.",
        titre="Contrôler les chiffres de la Direction",
        role="Gérant ; intégrateur", base=BASE,
        prerequis="G01 joué.",
        but="Chaque indicateur transversal se recalcule à la main depuis les tableaux spécialisés.",
        etapes=[
            ("Lire « Cash à risque ».",
             "« ardoises +30 j (…) + coulage (…) » : la somme des ardoises de plus de 30 jours (POS "
             "Crédit) et des pertes du stock (E03) ; jamais négatif. Sur la base jouée : 0 + 2 800 = "
             "2 800 FCFA.", "J05"),
            ("Lire « Crédits clients − dettes fournisseurs ».",
             "Encours des ardoises − dette 401 ; ici 0 − 12 600 = -12 600 FCFA, « vos fournisseurs "
             "financent l'exploitation ».", "J06"),
            ("« TENDANCES » : « CA vs Achats — 6 mois, et encours d'ardoises ».",
             "Les points du mois courant égalent le CA et les factures du mois.", "J07"),
            ("VUE « À traiter ».",
             "« À TRAITER — LA LISTE DU GÉRANT » : lignes priorisées « Relancer … », « Payer … », "
             "« Commander … », « Coulage au-dessus du seuil (… > 2,0 %) » selon la base (écran #1).",
             "J08"),
            ("Toucher la carte « DETTES FOURNISSEURS », puis une ligne d'« À traiter ».",
             "L'onglet ou le tableau de bord spécialisé s'ouvre ; ses chiffres égalent ceux du "
             "cockpit.", "J09"),
        ],
        captures=[("integrateur/17_direction_a_traiter.jpg", "VUE « À traiter ».")],
        encadres=[],
    ),
    # ═════════════════════════ H. NON-RÉGRESSION ══════════════════════════
    dict(
        id="H01", partie="H", joue=False,
        titre="Une caisse hors restaurant reste une caisse d'Odoo",
        role="Intégrateur (admin)", base=BASE,
        prerequis="Caisse « Bar » de I01 ; « Ardoise client » ajouté à ses « Modes de paiement ».",
        but="Le service à table contrôlé ne touche que la caisse cochée.",
        etapes=[
            ("Point de Vente → « Bar » → « Ouvrir la caisse ».",
             "Pas de fenêtre du code, pas de plan verrouillé.", ""),
            ("Ajouter un produit, « Paiement ».",
             "« Mettre sur ardoise » et « Ardoise client » sont là, comme avant.", "R101"),
            ("Encaisser en espèces ; Point de Vente → Analyse → Personnes et tables.",
             "La vente du Bar compte en « Ventes sans table » (limite connue).", ""),
        ],
        captures=[], encadres=[],
    ),
    dict(
        id="H02", partie="H", joue=False,
        titre="Après une mise à niveau : les corrections de novembre",
        role="Intégrateur ; Brice 1001 ; Clarisse 2001", base="base du client mise à niveau (I04)",
        prerequis="I04 joué ; Ctrl+Maj+R sur chaque tablette.",
        but="Les trois défauts constatés en production ne reviennent pas.",
        etapes=[
            ("Clarisse : une table avec deux produits, « Diviser l'addition », un produit, « Créer "
             "l'addition à part » ; toucher l'onglet de la part (« 4B »), puis celui de la table.",
             "Aucune fenêtre « Oups ! » ni « order.getCommand is not a function » (corrigé en "
             "18.0.1.0.7).", ""),
            ("Sur la part : « Addition ».",
             "La caisse reste sur la part après l'impression (18.0.1.0.8).", ""),
            ("Encaisser la part et la table avec le compte caisse.",
             "Aucun « Impossible d'envoyer le message, veuillez configurer l'adresse e-mail de "
             "l'expéditeur. » (comptes avec courriel, carte 18.0.1.3.1).", ""),
            ("Ouvrir chaque tableau de bord : Analyse AITE, POS Crédit → Recouvrement, Inventaire → "
             "Tableau de bord AITE, Achats → Tableau de bord AITE, Direction.",
             "Chacun s'affiche, sans erreur en console (F12).", "J01"),
        ],
        captures=[], encadres=[],
    ),
]

FAQ = [
    ("La caisse affiche « Oups ! » avec « order.getCommand is not a function ».",
     "Version d'Odoo 18 plus ancienne que celle de développement : mettre à niveau "
     "aite_pos_restaurant en 18.0.1.0.9 (I04), puis Ctrl+Maj+R sur la tablette."),
    ("Une part divisée (« 6B ») a disparu du plan.",
     "Une part n'a pas de table : ≡ → « Commandes », code de la caissière, la retrouver dans la "
     "liste."),
    ("« Impossible d'envoyer le message, veuillez configurer l'adresse e-mail de l'expéditeur. »",
     "Le compte Odoo connecté n'a pas d'adresse e-mail : Paramètres → Utilisateurs → le compte → "
     "« Adresse e-mail »."),
    ("La carte de démonstration n'apparaît pas.",
     "Apps → la carte « Le Messager » → « Mettre à niveau », ou Point de Vente → Configuration → "
     "« Poser la carte Le Messager » : la notification dit ce qui manque."),
    ("Un produit créé n'apparaît pas à la caisse.",
     "Case « Point de Vente » et catégorie du PdV sur la fiche ; puis recharger la caisse (Ctrl+Maj+R)."),
    ("Un tableau de bord est vide.",
     "Pas de données sur la période (changer la période) ou droits manquants (scénario I05)."),
]
