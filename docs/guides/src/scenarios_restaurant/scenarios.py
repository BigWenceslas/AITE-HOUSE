# -*- coding: utf-8 -*-
"""Scénarios de tests de bout en bout du restaurant (lot 1) — source unique.

Ce fichier produit le PDF (via generer.py → index.html → weasyprint) et le
classeur de recette (.xlsx). Chaque étape est un seul geste, avec ce que
l'écran doit montrer ; les textes entre « » sont ceux du code
(addons/aite_pos_restaurant/static/src/utils/messages.js, vues, modèles) ou
d'Odoo 18 en français (fichiers fr.po). Chaque étape renvoie aux cas R du
cahier de recette (recette/cas_de_test.py) qu'elle couvre : generer.py
vérifie qu'aucun des cas R01 à R104 n'est oublié.

Équipe et carte : celles du jeu d'essai (dev/seeds/seed_restaurant.py).
"""

TITRE = "AITE Restaurant — scénarios de tests (recette)"
TITRE_COURT = "Scénarios de tests du restaurant"
VERSION = "1.0 — novembre 2026"

MODULES = [
    ("aite_pos_restaurant", "18.0.1.0.6", "la caisse du service à table contrôlé"),
    ("aite_pos_analytics_hr", "18.0.1.0.0", "le serveur et « Encaissée par » dans les analyses"),
    ("aite_pos_credit", "18.0.2.0.6", "l'ardoise : née d'une addition réglée, réservée au manager"),
    ("aite_pos_analytics", "18.0.2.1.6", "les ventes par famille, la marge lue sans rien écrire"),
    ("aite_resto_carte_messager", "18.0.1.0.0", "données de démonstration : la carte d'un restaurant client"),
]

EQUIPE = [
    ("Brice", "Serveur", "1001", "ouvre ses tables, commande, envoie, imprime l'addition"),
    ("Nadège", "Serveur", "1002", "idem, sur ses propres tables"),
    ("Clarisse", "Caissière", "2001", "en plus : ouvre la caisse, encaisse toutes les tables"),
    ("Hervé", "Chef de salle ou superviseur", "3001",
     "en plus : annule ce qui est envoyé (avec un motif), sort des espèces, ferme la caisse"),
    ("Sandrine", "Manager", "4001", "tout, y compris les prix, les remboursements et l'ardoise"),
]

COMPTES = [
    ("caisse / caisse", "Caisse de la salle",
     "ouvert sur chaque tablette (Point de Vente : Utilisateur ; Facturation)"),
    ("manager / manager", "Manager de la salle",
     "la gestion : employés, carte, stock, rapports (Point de Vente : Administrateur)"),
    ("chef / chef", "Chef de salle (rapports)", "le profil « Restaurant : lecture des rapports », rien d'autre"),
    ("admin / admin", "Administrateur (AITE)", "les réglages de la caisse et l'installation"),
]

# Un scénario : id, titre, partie, roles, base, quand, prerequis, but,
# etapes [(geste, attendu, "R.. R..")], captures [(fichier, légende)],
# encadres [("reflexe"|"regle"|"attention", texte)].
# Une étape sans cas R porte "" (contrôle utile sans cas au cahier).

SCENARIOS = [
    # ════════════════════════════ A. MISE EN PLACE ═══════════════════════
    dict(
        id="S01", partie="A", titre="Préparer la base de recette et vérifier les réglages",
        roles="AITE (administrateur)", base="aite_resto (neuve)", quand="Avant le jour 1",
        prerequis="Odoo 18 et PostgreSQL installés à côté du dépôt AITE-HOUSE ; aucune autre "
                  "instance d'Odoo lancée ; la base aite_resto n'existe pas encore (sinon la "
                  "supprimer, voir les notes de version §9).",
        but="Disposer d'une base de restaurant neuve, avec sa caisse « Restaurant » jamais "
            "ouverte, et vérifier ce que l'installation a réglé seule.",
        etapes=[
            ("Dans le dépôt, lancer dev/setup_env.sh --restaurant.",
             "Le script se termine sans erreur ; sa dernière ligne de graine commence par "
             "« seed restaurant OK » et se termine par « en place : 12 tables, 33 produits à la "
             "carte, 5 employés à niveau ».", ""),
            ("Démarrer Odoo sur aite_resto, se connecter avec admin / admin.",
             "L'accueil s'ouvre ; aucun menu Hôtel.", ""),
            ("Point de Vente → Configuration → Paramètres ; choisir la caisse « Restaurant » ; "
             "descendre au bloc Restaurant.",
             "« Est un bar/restaurant » et « Service à table contrôlé » sont cochés ; sous la case, "
             "la phrase commence par « Coché : chaque employé tape son code à 4 chiffres » et finit "
             "par « Se change seulement caisse fermée. ». « Délai avant l'orange (minutes) » = 60 ; "
             "« Autoriser la vente sans table » décoché ; « Refuser la vente des produits "
             "épuisés » coché ; chaque réglage porte sa phrase (écran 1).", ""),
            ("Dans le même écran, décocher « Se connecter avec Employés », puis « Enregistrer ».",
             "Refus : « Décochez d'abord « Service à table contrôlé » : sans les codes personnels, "
             "la caisse ne saurait plus qui fait quoi. » Toucher « Ignorer ».", ""),
            ("Taper 0 dans « Délai avant l'orange (minutes) », puis « Enregistrer ».",
             "Refus : « Le délai avant l'orange doit être d'au moins 1 minute. » Toucher "
             "« Ignorer » : le délai reste 60.", ""),
            ("Bloc Paiement, champ « Modes de paiement » de la caisse : ajouter « Ardoise client » "
             "s'il n'y est pas, puis « Enregistrer ».",
             "La caisse a trois modes : Espèces, Mobile Money, Ardoise client (nécessaire aux "
             "scénarios de l'ardoise).", ""),
            ("Point de Vente → Configuration → Motifs d'annulation.",
             "Cinq motifs : Erreur de saisie, Client parti, Plat refusé, Produit manquant, Autre ; "
             "« Précision obligatoire » n'est cochée que pour « Autre ».", ""),
            ("Paramètres → Utilisateurs & Sociétés → Utilisateurs : ouvrir « Caisse de la salle », "
             "« Manager de la salle », « Chef de salle (rapports) ».",
             "Droits conformes au tableau « Les comptes Odoo » (chapitre 2) : la caisse en Utilisateur du "
             "Point de Vente avec Facturation et un courriel ; le chef de salle avec le seul "
             "profil « Restaurant : lecture des rapports ».", ""),
        ],
        captures=[("25_reglages_service_a_table_controle.jpg",
                   "Les réglages de la caisse « Restaurant » : chaque case dit ce qui va se passer.")],
        encadres=[("regle", "Ne jamais ouvrir la caisse avant d'avoir fini les réglages : après la "
                   "première ouverture, Odoo garde toujours une session « Contrôle à l'ouverture » "
                   "qui grise « Service à table contrôlé » et « Autoriser la vente sans table ».")],
    ),
    dict(
        id="S02", partie="A", titre="Le manager prépare l'équipe, la carte et le stock",
        roles="Manager (compte manager)", base="aite_resto", quand="Avant le jour 1",
        prerequis="S01 joué. Se connecter avec manager / manager.",
        but="Vérifier les trois écrans de gestion du manager : la fiche employé (niveau et code), "
            "la carte rangée en familles, le stock de départ.",
        etapes=[
            ("Employés → ouvrir « Brice ».",
             "Sur la première page, groupe « Caisse du restaurant » : « Niveau en caisse » = "
             "Serveur, « Code caisse » = 1001, chacun avec sa phrase d'aide ; aucun courriel "
             "demandé (écran 2).", ""),
            ("Employés → Nouveau : nom « Essai », « Niveau en caisse » = Serveur.",
             "Un code de 4 chiffres apparaît aussitôt dans « Code caisse », sans rien taper.", "R03"),
            ("Vider « Code caisse », enregistrer.",
             "Refus : « Donnez un code à 4 chiffres à Essai : sans code, il ne peut pas utiliser "
             "la caisse. »", "R03"),
            ("Taper 123 dans « Code caisse », enregistrer.",
             "Refus : « Le code doit faire exactement 4 chiffres. »", "R03"),
            ("Taper 1002 (le code de Nadège), enregistrer.",
             "Refus : « Le code 1002 est déjà celui d'un autre employé. Choisissez quatre autres "
             "chiffres : chaque employé a son propre code. » — le nom de Nadège n'apparaît "
             "jamais.", "R03"),
            ("Taper 1003, enregistrer ; puis archiver la fiche « Essai ».",
             "La fiche est enregistrée, puis archivée (elle ne sert plus).", "R03"),
            ("Point de Vente → Produits → Produits → Nouveau : « Jus de bissap », prix 1 000 FCFA, "
             "case « Point de Vente », onglet « Point de Vente » : catégorie du PdV « Sodas » ; "
             "enregistrer.",
             "Le produit est enregistré (il apparaîtra sous Boisson > Non alcoolisé > Sodas à "
             "l'ouverture de la caisse, scénario S04).", "R13"),
            ("Même geste avec « Verre de vin rosé », 2 000 FCFA, catégorie du PdV « Vin ».",
             "Le produit est enregistré (il apparaîtra sous Boisson > Alcoolisé > Vin).", "R33"),
            ("Point de Vente → Configuration → Plans de salle → « Salle ».",
             "La salle porte 12 tables numérotées de 1 à 12.", "R63"),
            ("Inventaire → Produits → Produits → « Castel 65 cl ».",
             "« Suivre l'inventaire » est coché ; stock de départ 48. Les plats et pizzas n'ont "
             "pas de suivi.", ""),
        ],
        captures=[("24_fiche_employe_niveau_et_code.jpg",
                   "La fiche employé : « Niveau en caisse » et « Code caisse » sur la première page.")],
        encadres=[("reflexe", "Ne communiquez un code qu'à son employé ; un employé sans niveau "
                   "n'apparaît pas sur la caisse.")],
    ),
    # ════════════════════════ B. LE SERVICE (JOUR 1) ═══════════════════════
    dict(
        id="S03", partie="B", titre="Ouvrir la caisse le matin",
        roles="Caissière (Clarisse 2001) ; Serveur (Brice 1001)", base="aite_resto", quand="Jour 1",
        prerequis="S01 et S02 joués. Sur la tablette (ou le navigateur) : se connecter avec "
                  "caisse / caisse.",
        but="La caisse s'ouvre avec le code d'une caissière, jamais avec celui d'un serveur ; "
            "le plan verrouillé devient l'écran de repos.",
        etapes=[
            ("Point de Vente → carte « Restaurant » → « Ouvrir la caisse ».",
             "Le plan s'affiche, avec le bandeau « La caisse est fermée. La caissière ou un chef "
             "de salle tape son code pour l'ouvrir. » et, ouverte d'elle-même, la fenêtre « Votre "
             "code pour ouvrir la caisse » (quatre ronds, un pavé, « Retour ») — écran 3.", "R63"),
            ("Brice tape 1001.",
             "Refus : « La caisse n'est pas encore ouverte. La caissière ou un chef de salle doit "
             "l'ouvrir avec son code. » ; la caisse reste fermée.", "R10"),
            ("Toucher « Retour », puis le bouton « Ouvrir la caisse » du bandeau.",
             "La fenêtre « Votre code pour ouvrir la caisse » se rouvre.", ""),
            ("Clarisse tape 2001.",
             "Le code est accepté au 4ᵉ chiffre, sans touche de validation ; la fenêtre "
             "« Contrôle à l'ouverture » s'ouvre (« Espèces à l'ouverture », « Note "
             "d'ouverture ») — écran 4.", "R10"),
            ("Toucher « J'ouvre la caisse ».",
             "Le plan s'affiche sans écran « Déverrouiller la caisse » : toutes les tables grises "
             "avec leur numéro, la phrase « Touchez une table, puis tapez votre code. », aucun "
             "nom en haut, la légende en bas « Gris : libre · Vert : ouverte · Orange : ouverte "
             "depuis plus de 60 min, proposez l'addition · Pastille rouge : pas encore envoyé » "
             "(écran 5).", "R63"),
            ("Toucher ≡ (en haut à droite).",
             "Le menu ne propose que « Commandes », « Entrée ou sortie d'espèces », « Fermer la "
             "caisse » (et « Imprimer le rapport » s'il y a une imprimante) ; pas de « Modifier "
             "le plan ». Refermer le menu.", "R65 R14"),
            ("Faire glisser la table 1 sur la table 2.",
             "Rien ne bouge : la table ne se déplace pas et ne se relie pas à l'autre.", "R65"),
        ],
        captures=[("01_ouverture_code_de_la_caissiere.jpg",
                   "La caisse fermée : la fenêtre du code s'ouvre d'elle-même."),
                  ("02_ouverture_j_ouvre_la_caisse.jpg",
                   "Après le code de Clarisse : « Contrôle à l'ouverture », puis « J'ouvre la caisse »."),
                  ("03_plan_verrouille.jpg",
                   "Le plan verrouillé, écran de repos de chaque poste, avec sa légende.")],
        encadres=[],
    ),
    dict(
        id="S04", partie="B", titre="Ouvrir une table, commander, envoyer",
        roles="Serveur (Brice 1001)", base="aite_resto", quand="Jour 1",
        prerequis="S03 joué : la caisse est ouverte, le plan affiché, personne d'identifié.",
        but="Le parcours de base d'un serveur : la table, le code, les personnes, la carte en "
            "familles, « J'envoie », retour au plan verrouillé.",
        etapes=[
            ("Regarder la barre du haut du plan.",
             "« Plan », « Table », ≡ ; pas de bouton « + » (vente sans table décochée).", "R19"),
            ("Toucher la table 4, puis « Retour » sans taper de code.",
             "La fenêtre « Table 4 — votre code » s'est ouverte (quatre ronds, un pavé) ; après "
             "« Retour », le plan reste affiché, verrouillé, la table 4 grise.", "R01"),
            ("Toucher la table 4, taper 9999.",
             "Les ronds se vident, la fenêtre affiche « Code inconnu. Retapez votre code. »", "R02"),
            ("Taper 1001.",
             "La même fenêtre enchaîne « Table 4 — combien de personnes ? » : huit gros boutons 1 à 8 "
             "et « 9 et plus » ; aucun bouton 0 ; aucun produit ne peut être saisi (écran 7).",
             "R02 R15 R20 R22"),
            ("Toucher « 9 et plus », ne rien taper.",
             "Un pavé s'ouvre sous les huit boutons ; « Valider » reste grisé (aucun message tant "
             "que rien n'est tapé).", "R21"),
            ("Taper 0.", "« Valider » reste grisé ; « Il faut au moins une personne à table. » "
             "s'affiche sous le nombre.", "R22"),
            ("Toucher « Retour ».", "Retour au plan ; la table 4 est toujours grise (libre).", "R21"),
            ("Toucher la table 4, taper 1001, toucher 4.",
             "L'écran de commande s'ouvre : « Brice » en haut, phrase « Table 4 · ouverte par "
             "Brice · 0 min », bouton « 4 personnes », familles racines « Nourriture » et "
             "« Boisson ».", "R02 R16 R23 R29"),
            ("Toucher « Boisson ».", "« Alcoolisé » et « Non alcoolisé » apparaissent.", "R30"),
            ("Toucher « Alcoolisé », puis « Bière ».",
             "Seules les bières : 33 Export 65 cl, Castel 65 cl, Guinness 33 cl, Mützig 65 cl "
             "(écran 8).", "R31"),
            ("Retoucher « Bière ».", "La caisse remonte d'un niveau (sous-familles d'Alcoolisé).", "R32"),
            ("Toucher « Bière », puis deux fois « Castel 65 cl ».",
             "Ligne « Castel 65 cl » 2,00, 2 000 FCFA ; le bouton « J'envoie » montre « Bière 2 ».", ""),
            ("Toucher « Nourriture », « Pizzas », « Pizza Margherita ».",
             "Ligne « Pizza Margherita » 1,00, 5 000 FCFA ; total 7 000 FCFA.", ""),
            ("Toucher « J'envoie ».",
             "Notification « Envoyé : Pizzas × 1, Bière × 2. », retour au plan, plus aucun nom en haut ; "
             "la table 4 est verte avec « 0 min » sous son numéro (écran 9).", "R08 R64"),
            ("Toucher de nouveau la table 4.",
             "La fenêtre « Table 4 — votre code » s'ouvre : le code est redemandé après chaque "
             "envoi. Toucher « Retour ».", "R08"),
        ],
        captures=[("04_table_4_votre_code.jpg", "Toucher une table demande toujours le code."),
                  ("05_table_4_combien_de_personnes.jpg",
                   "Une table libre demande ensuite les personnes, dans la même fenêtre."),
                  ("06_ecran_de_commande_familles.jpg",
                   "L'écran de commande : phrase d'état, « 4 personnes », familles, « J'envoie »."),
                  ("07_apres_j_envoie_plan_verrouille.jpg",
                   "Après « J'envoie » : la notification, le plan verrouillé, la table 4 verte.")],
        encadres=[("reflexe", "Un code se tape d'un trait : il est validé seul au quatrième chiffre. "
                   "Après « J'envoie », la tablette est de nouveau libre pour le collègue suivant.")],
    ),
    dict(
        id="S05", partie="B", titre="Les autres tables : collègue, numéro tapé, client",
        roles="Serveurs (Nadège 1002, Brice 1001)", base="aite_resto", quand="Jour 1",
        prerequis="S04 joué (table 4 ouverte par Brice). Un second poste (autre tablette ou autre "
                  "fenêtre du navigateur) connecté avec caisse / caisse, caisse ouverte.",
        but="Une table appartient à celui qui l'a ouverte ; le numéro tapé ouvre aussi une table ; "
            "le plan est le même sur tous les postes.",
        etapes=[
            ("Nadège touche la table 4 et tape 1002.",
             "Refus : « Table 4 : c'est la table de Brice. Seuls Brice, la caissière ou un chef de "
             "salle peuvent la modifier. » ; rien ne s'ouvre.", "R24"),
            ("Nadège touche la table 7, tape 1002, touche 2, ajoute deux fois « Café expresso » "
             "(Boisson > Non alcoolisé > Café), puis « J'envoie ».",
             "Notification « Envoyé : Café × 2. » ; retour au plan ; la table 7 est verte.", ""),
            ("Sur le second poste, regarder le plan.",
             "Les tables 4 et 7 y sont vertes, avec leur durée.", "R24 R64"),
            ("Nadège touche « Table » dans la barre du plan, tape 12, touche « Aller à/au ».",
             "La fenêtre du numéro propose « Retour » (jamais « Discard ») ; après « Aller à/au », "
             "la fenêtre « Table 12 — votre code » s'ouvre.", "R17"),
            ("Nadège tape 1002, touche 2.",
             "« Table 12 · ouverte par Nadège · 0 min ».", "R16 R17"),
            ("Toucher « Plan » sans rien saisir ; regarder le plan sur les deux postes.",
             "La table 12, ouverte sans produit, est verte sur les deux postes ; les tables libres "
             "sont grises.", "R24 R64"),
            ("Nadège rouvre la table 12 (code 1002), ajoute « Top Ananas 35 cl » (Sodas), « J'envoie ».",
             "Notification « Envoyé : Sodas × 1. »", ""),
            ("Nadège : « Table », tape 99, « Aller à/au », tape 1002, touche 2.",
             "Une table « 99 » s'ouvre à 2 personnes (le refus d'un numéro inconnu est au lot 2).",
             "R18"),
            ("Ajouter « Thé » (Café), « J'envoie ».", "Notification « Envoyé : Café × 1. »", "R18"),
            ("Brice touche la table 3, tape 1001, touche 1, ajoute « Coca-Cola 33 cl », « J'envoie ».",
             "La table 3 est verte (elle servira au scénario S08).", ""),
            ("Nadège touche la table 7, tape 1002, touche « Client » et choisit un contact (en créer "
             "un au besoin).",
             "Le client est rattaché à l'addition de la table 7 ; toucher « Plan ».", "R99"),
        ],
        captures=[],
        encadres=[("regle", "Une table est celle de qui l'a ouverte. Seuls cette personne, la "
                   "caissière, un chef de salle ou le manager peuvent y toucher.")],
    ),
    dict(
        id="S06", partie="B", titre="Retirer ce qui n'est pas encore parti",
        roles="Serveur (Brice 1001)", base="aite_resto", quand="Jour 1",
        prerequis="S04 joué : table 4 avec 2 Castel 65 cl et 1 Pizza Margherita envoyées. Base "
                  "sans imprimante de cuisine (cas du jeu d'essai).",
        but="⌫ retire librement ce qui n'est pas parti ; ce qui est parti est verrouillé sur tous "
            "les chemins.",
        etapes=[
            ("Brice touche la table 4, tape 1001, ajoute « Coca-Cola 33 cl ».",
             "Une ligne « Coca-Cola 33 cl » 1,00, sélectionnée.", ""),
            ("Toucher ⌫, puis ⌫.",
             "La ligne disparaît, sans code ni fenêtre (et sans trace).", "R34"),
            ("Ajouter une Castel 65 cl (Boisson > Alcoolisé > Bière).",
             "La ligne « Castel 65 cl » passe à 3,00 (2 envoyées + 1).", "R36"),
            ("Toucher ⌫, puis ⌫.",
             "La ligne revient à 2,00 librement : la troisième, pas envoyée, est retirée.", "R36"),
            ("Toucher encore ⌫, puis ⌫.",
             "La fenêtre « Annuler Castel 65 cl — table 4 » s'ouvre, sous-titre « Déjà envoyé : "
             "2 Castel 65 cl. Pour l'annuler, un chef de salle tape son code. » ; rien n'est "
             "retiré. Toucher « Retour ».", "R35 R36 R37"),
            ("Toucher la ligne Castel, taper 1 au pavé.",
             "La quantité reste 2,00 : un chiffre plus petit que ce qui est parti est ignoré.", "R35"),
            ("Regarder la touche « % » du pavé.",
             "Elle est grisée : aucune remise n'est proposée.", "R40"),
            ("Recharger la page (Ctrl+F5).",
             "Le plan verrouillé revient ; personne n'est identifié.", "R38"),
            ("Toucher la table 4, taper 1001, toucher la ligne Castel, ⌫, ⌫.",
             "La même fenêtre d'annulation s'ouvre (même refus sur un autre poste ou après un "
             "rechargement). Toucher « Retour », puis « Plan ».", "R38"),
        ],
        captures=[],
        encadres=[("reflexe", "Toucher une ligne remet le pavé à zéro : le premier ⌫ est absorbé, "
                   "il en faut toujours deux.")],
    ),
    dict(
        id="S07", partie="B", titre="Annuler un produit envoyé, sur le poste du serveur",
        roles="Serveur (Brice 1001) + Chef de salle (Hervé 3001) ; codes de Nadège et Clarisse",
        base="aite_resto", quand="Jour 1",
        prerequis="S06 joué : table 4, 2 Castel 65 cl envoyées.",
        but="Ce qui est parti ne s'annule qu'avec le code d'un chef de salle et un motif ; un code "
            "faux ou sans droit est refusé ; le serveur reste identifié.",
        etapes=[
            ("Brice touche la table 4, tape 1001, touche la ligne Castel, ⌫, ⌫.",
             "Fenêtre « Annuler Castel 65 cl — table 4 », « Déjà envoyé : 2 Castel 65 cl. Pour "
             "l'annuler, un chef de salle tape son code. », « Combien ? » avec « 1 » et « 2 (tout) » "
             "(écran 10).", "R09"),
            ("Toucher « 1 ».",
             "L'étape « Code d'un chef de salle » s'affiche (quatre ronds, un pavé) ; rien n'est "
             "encore retiré.", "R09"),
            ("Taper 9999.", "« Code inconnu. Retapez votre code. » dans la fenêtre.", ""),
            ("Taper 1002 (code de Nadège, serveur).",
             "Notification (en haut à droite, quelques secondes) : « Ce code ne peut pas annuler. "
             "Il faut celui d'un chef de salle, d'un superviseur ou du manager. » ; la fenêtre "
             "reste sur « Code d'un chef de salle » et attend un autre code.", "R45"),
            ("Taper 2001 (code de Clarisse, caissière).",
             "Même refus, en notification ; la fenêtre attend toujours.", "R45"),
            ("Hervé tape 3001.",
             "L'étape « Pourquoi ? » montre les cinq motifs en gros boutons (écran 11).", "R43"),
            ("Toucher « Retour » sans choisir de motif.",
             "La fenêtre se ferme ; la ligne est toujours à 2,00 : sans motif, rien n'est annulé.",
             "R50"),
            ("⌫, ⌫ de nouveau, « 1 », Hervé tape 3001, toucher « Autre », puis « Valider » sans "
             "rien écrire.",
             "Un champ « Précision » est apparu sous les motifs ; « Valider » vide affiche « Écrivez "
             "en quelques mots pourquoi. » ; rien n'est annulé.", "R50"),
            ("Écrire « Bouteille cassée au service » dans « Précision », « Valider ».",
             "Notification « Annulation faite : 1 Castel 65 cl, par Hervé. » ; la ligne passe à "
             "1,00 (1 000 FCFA). Avec une imprimante de cuisine seulement : « Bon d'annulation "
             "envoyé. » (écran 12).", "R43 R50"),
            ("Regarder le nom en haut de l'écran.",
             "« Brice » est toujours en haut : il continue sa table. Toucher « Plan ».", "R44"),
        ],
        captures=[("10_annulation_combien.jpg", "Plus d'une unité envoyée : « Combien ? »."),
                  ("11_annulation_pourquoi.jpg", "Après le code du chef de salle : « Pourquoi ? »."),
                  ("12_annulation_faite_brice_reste_identifie.jpg",
                   "L'annulation faite ; Brice reste identifié sur sa table.")],
        encadres=[("regle", "Ce qui est parti en cuisine ou au bar ne disparaît jamais sans une "
                   "trace : qui l'a demandé, qui l'a autorisé, pourquoi.")],
    ),
    dict(
        id="S08", partie="B", titre="Le chef de salle annule seul : un produit, une table",
        roles="Chef de salle (Hervé 3001) ; Manager (compte manager, gestion)",
        base="aite_resto", quand="Jour 1",
        prerequis="S05 joué (table 7 : 2 Café expresso ; table 12 : 1 Top Ananas ; table 99 : 1 Thé ; "
                  "table 3 : 1 Coca-Cola, tous envoyés). Un onglet du navigateur ouvert sur la "
                  "gestion avec manager / manager.",
        but="Un chef de salle identifié ne retape pas son code ; un motif ajouté est proposé "
            "aussitôt ; une table entière s'annule depuis l'écran de commande ou la liste.",
        etapes=[
            ("Gestion (manager) : Point de Vente → Configuration → Motifs d'annulation → Nouveau : "
             "« Casse », enregistrer.", "Le motif « Casse » est dans la liste.", "R51"),
            ("Caisse, sans la recharger : Hervé touche la table 7, tape 3001, touche la ligne "
             "« Café expresso », ⌫, ⌫.",
             "Fenêtre « Annuler Café expresso — table 7 », « Déjà envoyé : 2. », « Combien ? ».", ""),
            ("Toucher « 1 ».",
             "Le code n'est pas redemandé (Hervé est identifié) : « Pourquoi ? » propose six motifs, "
             "dont « Casse ».", "R51"),
            ("Toucher « Client parti ».",
             "« Annulation faite : 1 Café expresso, par Hervé. » ; il reste 1 Café expresso. "
             "Toucher « Plan ».", ""),
            ("Hervé touche la table 12, tape 3001, « Actions », « Annuler la table ».",
             "La fenêtre « Annuler la table 12 » s'ouvre directement (pas de confirmation "
             "d'Odoo), « Déjà envoyé : 1 Top Ananas 35 cl », « Pourquoi ? ».", "R39"),
            ("Toucher « Client parti ».",
             "Retour au plan ; la table 12 est grise (libérée).", "R39"),
            ("Hervé : ≡ → « Commandes ».",
             "Fenêtre « Votre code — liste des commandes » ; taper 3001 : la liste des additions "
             "ouvertes s'affiche.", ""),
            ("Toucher la corbeille de l'addition de la table 99.",
             "La fenêtre « Annuler la table 99 » s'ouvre (code déjà tapé, motif demandé).", "R39"),
            ("Toucher « Erreur de saisie ».",
             "L'addition 99 disparaît de la liste. Revenir au plan.", "R39"),
            ("Gestion (manager) : Point de Vente → Commandes → Commandes ; ouvrir l'addition de la "
             "table 3 (pas encore payée) ; ⚙ Action → « Annuler la commande ».",
             "L'addition est annulée, sans code ni motif : la gestion n'est jamais bloquée (la trace "
             "« Annulation sans code » se lit au scénario S14).", "R52"),
        ],
        captures=[],
        encadres=[],
    ),
    dict(
        id="S09", partie="B", titre="Diviser, déplacer, réunir",
        roles="Serveur (Brice 1001) ; Caissière (Clarisse 2001) ; Serveur (Nadège 1002)",
        base="aite_resto", quand="Jour 1",
        prerequis="Tables 5, 6, 9 libres ; table 7 ouverte par Nadège.",
        but="Diviser, déplacer et réunir ne sont ni des annulations ni des saisies, ne renvoient "
            "aucun bon et gardent la durée de la première ouverture.",
        etapes=[
            ("Brice ouvre la table 5 (code 1001, 3 personnes) : Poulet DG, Frites, deux Coca-Cola "
             "33 cl, Café crème, Thé ; « J'envoie ».", "La table 5 porte 6 produits, 12 000 FCFA.", ""),
            ("Brice ouvre la table 6 (code 1001, 4 personnes) : Ndolé crevettes ; « J'envoie ».",
             "La table 6 est verte.", ""),
            ("Clarisse touche la table 5, tape 2001, « Actions » → « Diviser l'addition » ; touche "
             "tous les produits, puis « Créer l'addition à part ».",
             "Refus : « Toute l'addition est sélectionnée : il n'y a rien à diviser. Encaissez la "
             "table directement. »", "R57"),
            ("Ne garder sélectionnés que « Café crème » et « Thé » ; « Créer l'addition à part ».",
             "Une part « 5B » porte ces deux produits ; aucune fenêtre d'annulation.", "R57 R41 R58"),
            ("Sur la part : « J'encaisse », « Espèces », « Valider ».",
             "La caisse revient d'elle-même à la table 5, toujours ouverte avec ses quatre produits ; "
             "« Clarisse » toujours en haut.", "R59"),
            ("Table 5 : « Actions » → « Diviser l'addition », toucher une fois « Coca-Cola 33 cl », "
             "« Créer l'addition à part » ; sur la part, « Actions » → « Déplacer ou réunir », "
             "toucher la table 6.",
             "Le Coca-Cola est sur l'addition de la table 6 et plus sur celle de la table 5 ; aucune "
             "fenêtre d'annulation.", "R60 R62 R41"),
            ("Table 5 : diviser « Poulet DG » et « Frites », puis « Déplacer ou réunir » la part vers "
             "la table 9 (libre).",
             "La fenêtre demande « Table 9 — combien de personnes ? » ; toucher 3 : la table 9 est "
             "occupée avec ces deux produits.", "R61 R25"),
            ("Clarisse ouvre la table 9 (code 2001), « Actions » → « Déplacer ou réunir », touche la "
             "table 6.",
             "La table 6 porte tous les produits des deux tables, avec « 7 personnes » ; la table 9 "
             "redevient grise ; la durée de la table 6 reste comptée depuis sa première ouverture.",
             "R53 R56 R70"),
            ("Nadège ouvre sa table 7 (code 1002), « Actions » → « Déplacer ou réunir », touche la "
             "table 6.",
             "Refus : « La table 6 est celle de Brice : la caissière ou un chef de salle peut "
             "réunir ces tables. » ; rien n'est réuni.", ""),
            ("Avec une imprimante de cuisine seulement : regarder l'imprimante pendant ces gestes.",
             "Aucun bon n'est renvoyé en cuisine pour la division, le déplacement ou la réunion.",
             "R54 R58 R62"),
        ],
        captures=[],
        encadres=[("reflexe", "Pour déplacer un seul produit : le diviser d'abord, puis déplacer "
                   "la part. Deux gestes, aucune annulation.")],
    ),
    dict(
        id="S10", partie="B", titre="Produit épuisé, entrée de stock, hors connexion",
        roles="Manager (compte manager, gestion) ; Serveurs (Brice 1001, Nadège 1002)",
        base="aite_resto", quand="Jour 1",
        prerequis="Table 4 ouverte par Brice ; un onglet de gestion ouvert avec manager / manager ; "
                  "le second poste de S05.",
        but="Un produit suivi en stock et épuisé n'est pas vendu ; une entrée de stock le rend "
            "vendable en moins d'une minute ; les plats se vendent toujours ; hors connexion, on vend.",
        etapes=[
            ("Gestion : Inventaire → Produits → Produits → « Guinness 33 cl » → « Mettre la "
             "quantité à jour » ; mettre la quantité en stock à 0 et l'enregistrer.",
             "Le stock de la Guinness vaut 0.", ""),
            ("Caisse : Brice ouvre la table 4 (1001), Boisson > Alcoolisé > Bière, touche « Guinness "
             "33 cl ».",
             "Notification « Produit épuisé » : « Plus de Guinness 33 cl en stock. Si la bouteille "
             "est bien là, demandez au manager d'enregistrer l'entrée de stock : la vente repassera "
             "aussitôt. » ; rien n'est ajouté (écran 13).", "R75"),
            ("Si un lecteur est disponible : donner un code-barres à la Guinness (gestion) et le "
             "lire à la caisse.", "Même refus, rien n'est ajouté.", "R75"),
            ("Gestion : « Mützig 65 cl » → « Mettre la quantité à jour » → 2.",
             "Le stock de la Mützig vaut 2.", ""),
            ("Caisse : Brice ajoute une Mützig, puis tape 5 au pavé sur sa ligne.",
             "Même refus « Produit épuisé » (« Plus de Mützig 65 cl en stock. … ») ; la ligne reste "
             "à 1. Retirer la ligne (⌫, ⌫) et toucher « Plan ».", "R75"),
            ("Nadège ouvre la table 2 (1002, 2 personnes), ajoute deux Mützig 65 cl, « J'envoie ».",
             "Les deux dernières Mützig sont parties sur la table 2 (non encaissée).", "R78"),
            ("Sur l'autre poste, Brice ouvre la table 4 (1001) et touche « Mützig 65 cl ».",
             "Refusé (« Produit épuisé ») au plus tard une minute après l'envoi.", "R78"),
            ("Gestion : « Guinness 33 cl » → « Mettre la quantité à jour » → 24.",
             "Le stock vaut 24.", "R72"),
            ("Caisse, sans recharger : dans la minute, Brice touche « Guinness 33 cl ».",
             "La vente passe : la ligne est ajoutée. La retirer (⌫, ⌫), elle n'est pas partie.",
             "R72 R76"),
            ("Toucher « Pizza Margherita » (non suivie en stock).",
             "La vente passe toujours. Retirer l'unité ajoutée (⌫, ⌫).", "R77"),
            ("Gestion : Inventaire → Analyse → Historique des mouvements ; filtrer sur la semaine.",
             "Les saisies de stock de la Guinness et de la Mützig y sont, datées et au nom de "
             "« Manager de la salle ».", "R73 R74"),
            ("Couper le réseau du poste de Brice (Wi-Fi coupé, ou outils de développement → Réseau → "
             "Hors ligne), ajouter « Guinness 33 cl ».",
             "La vente passe (aucun contrôle de stock hors connexion).", "R79"),
            ("Toucher la ligne Castel, ⌫, ⌫, « 1 » si demandé, code 3001.",
             "« Pas de réseau : annuler est impossible pour l'instant. Réessayez dans un moment. » ; "
             "la fenêtre reste ouverte.", "R79"),
            ("« Retour », retirer la Guinness (⌫, ⌫), rétablir le réseau, toucher « Plan ».",
             "La table 4 est comme avant : 1 Castel 65 cl, 1 Pizza Margherita, 6 000 FCFA.", ""),
        ],
        captures=[("09_produit_epuise.jpg", "Un produit suivi épuisé : refusé, avec ce qu'il faut faire.")],
        encadres=[("regle", "Saisir le stock de départ des boissons suivies avant le premier "
                   "service : sinon elles sont refusées à la caisse.")],
    ),
    dict(
        id="S11", partie="B", titre="Encaisser : au poste du serveur, prise de main, manager",
        roles="Caissière (Clarisse 2001) ; Manager (Sandrine 4001) ; Serveur (Brice 1001)",
        base="aite_resto", quand="Jour 1",
        prerequis="Tables 4, 5, 6 ouvertes (S04 à S10) ; table 1 libre.",
        but="Seuls la caissière et au-dessus encaissent ; « Ouverte par » ne change jamais ; "
            "« Encaissée par » dit qui a validé.",
        etapes=[
            ("Brice ouvre la table 4 (1001), touche « J'encaisse ».",
             "Fenêtre « Code de la personne qui encaisse », sous-titre « Brice ne peut pas "
             "encaisser : la caissière tape son code ici. »", "R05"),
            ("Brice tape 1001.",
             "Refus : « Vous ne pouvez pas encaisser. Appelez la caissière : elle tapera son code "
             "ici. » ; la fenêtre attend.", "R05 R10"),
            ("Clarisse tape 2001.",
             "L'écran de paiement s'ouvre : 6 000 FCFA, modes « Espèces » et « Mobile Money » "
             "(écran 14).", "R05"),
            ("Toucher « Espèces », puis « Valider ».",
             "Retour au plan verrouillé, sans écran « Paiement réussi » ; la table 4 est grise.",
             "R68"),
            ("Clarisse touche la table 5, tape 2001, « J'encaisse », « Espèces », « Valider ».",
             "La table 5 (1 Coca-Cola, 1 000 FCFA) est encaissée en 8 touches ; retour au plan.", ""),
            ("Clarisse ouvre la table 1 (2001, 2 personnes), ajoute « Crêpe au sucre », touche la "
             "ligne puis « Prix ».",
             "« Prix » est grisé : le prix ne change pas.", "R12"),
            ("Sandrine touche le nom « Clarisse » en haut.",
             "Fenêtre « Qui prend la main ? Tapez votre code ».", "R12"),
            ("Sandrine tape 4001, touche la ligne, puis « Prix ».",
             "« Sandrine » est en haut ; « Prix » est actif (ne rien changer : retoucher la ligne).",
             "R12"),
            ("Sandrine : « J'encaisse », « Espèces », « Valider ».",
             "La table 1 est encaissée ; retour au plan.", ""),
            ("Sandrine touche la table 6 (ouverte par Brice), tape 4001, « J'encaisse », "
             "« Espèces », « Valider ».", "La table 6 est encaissée (13 500 FCFA).", ""),
            ("Gestion (manager) : Point de Vente → Commandes → Commandes ; ouvrir l'addition de "
             "la table 4.",
             "« Ouverte par » : Brice ; « Encaissée par » : Clarisse ; « Heure d'ouverture » "
             "remplie ; « Convives » : 4.", "R04 R23"),
            ("Bouton « Saisies » de la fiche.",
             "Une ligne par ajout : produit, quantité ajoutée, employé, heure (la Castel et la "
             "Coca-Cola retirées avant envoi n'y sont pas).", "R06"),
            ("Ouvrir l'addition de la table 6 : « Ouverte par », « Encaissée par », « Saisies ».",
             "« Ouverte par » : Brice (figé) ; « Encaissée par » : Sandrine ; ni la division ni la "
             "réunion n'ont ajouté de saisie.", "R06"),
        ],
        captures=[("13_paiement_especes.jpg", "L'écran de paiement, ouvert par le code de la caissière.")],
        encadres=[("reflexe", "Caissière au poste d'un serveur resté identifié : « J'encaisse », "
                   "son code, « Espèces », « Valider » — 7 touches, sans retourner au plan.")],
    ),
    dict(
        id="S12", partie="B", titre="Le plan en couleurs et le retour au plan",
        roles="AITE (admin) ; Serveur (Brice 1001) ; Caissière (Clarisse 2001)",
        base="aite_resto", quand="Jour 1",
        prerequis="Caisse ouverte ; table 11 libre. Le délai se règle à tout moment ; il "
                  "s'applique quand la caisse est rechargée.",
        but="Une table ouverte passe à l'orange après le délai, sans que personne ne touche "
            "l'écran ; un poste laissé seul revient au plan verrouillé.",
        etapes=[
            ("Admin : Point de Vente → Configuration → Paramètres → caisse « Restaurant » → taper 90 "
             "dans « Délai avant l'orange (minutes) ».",
             "La phrase sous le réglage dit aussitôt « Une table ouverte depuis plus de 90 minutes "
             "passe à l'orange sur le plan… ».", "R69"),
            ("Taper 2 à la place, « Enregistrer ».", "Le délai vaut 2 (réglage de test).", "R69"),
            ("Caisse : recharger la page (Ctrl+F5).",
             "La légende dit « Orange : ouverte depuis plus de 2 min, proposez l'addition ».", "R69"),
            ("Brice ouvre la table 11 (1001, 1 personne), ajoute « Café crème », « J'envoie » ; puis "
             "ne plus toucher l'écran.",
             "La table 11 est verte, « 0 min », puis « 1 min ».", "R71"),
            ("Attendre, sans toucher l'écran.",
             "Verte avant 2 minutes ; orange au plus tard à 3 minutes (le plan se recalcule toutes "
             "les 30 secondes) — écran 15.", "R66"),
            ("Brice rouvre la table 11 (1001) ; ne plus toucher l'écran pendant 5 minutes.",
             "La phrase d'état donne la même durée que le plan ; après 5 minutes, le poste revient "
             "seul au plan verrouillé, sans écran de veille ; le plan et ses couleurs restent "
             "affichés.", "R67 R71"),
            ("Clarisse touche la table 11, tape 2001, « J'encaisse », « Espèces », « Valider ».",
             "La table 11 redevient grise, sans durée.", "R68"),
            ("Admin : remettre le délai à 60, « Enregistrer » ; recharger la caisse.",
             "La légende redit « plus de 60 min ». À jouer une fois en vrai service : une table "
             "verte à 59 minutes est orange au plus tard à 61 minutes.", "R66"),
            ("Pendant le service, regarder une table ouverte depuis plus d'une heure.",
             "Sa durée s'écrit « 1 h 05 » (heures, puis minutes sur deux chiffres).", "R71"),
        ],
        captures=[("08_plan_en_couleurs.jpg",
                   "Le plan en couleurs : orange après le délai, durée sous le numéro.")],
        encadres=[("reflexe", "Orange veut dire : proposez l'addition. La couleur vient seule, "
                   "le plan n'a pas besoin d'être touché.")],
    ),
    dict(
        id="S13", partie="B", titre="Espèces et fermeture de la caisse avec des tables ouvertes",
        roles="Serveur (Brice 1001) ; Chef de salle (Hervé 3001)", base="aite_resto",
        quand="Jour 1, fin de service",
        prerequis="Tables 2 (2 Mützig) et 7 (1 Café expresso) encore ouvertes, avec des produits "
                  "envoyés ; toutes les autres encaissées ou annulées.",
        but="Seul un chef de salle sort des espèces et ferme ; les tables encore ouvertes "
            "s'annulent en une fenêtre, avec un motif ; le rapport de fermeture se rédige seul.",
        etapes=[
            ("Brice : ≡ → « Entrée ou sortie d'espèces », tape 1001.",
             "Fenêtre « Votre code — entrée ou sortie d'espèces » ; après le code, elle se ferme et "
             "le refus s'affiche en notification (en haut à droite, quelques secondes) : « Seul un "
             "chef de salle ou le manager peut sortir ou entrer des espèces. »", "R14 R10"),
            ("Brice : ≡ → « Fermer la caisse », tape 1001.",
             "Fenêtre « Votre code pour fermer la caisse » ; elle reste ouverte et le refus "
             "s'affiche en notification (en haut à droite, quelques secondes) : « Seul un chef de "
             "salle ou le manager ferme la caisse. » ; toucher « Retour ».", "R14 R10"),
            ("Hervé : ≡ → « Entrée ou sortie d'espèces », tape 3001.",
             "La fenêtre d'espèces d'Odoo s'ouvre.", "R10"),
            ("Toucher « Cash sortant », taper 1000, motif « Monnaie », « Confirmer ».",
             "Notification d'Odoo : « Vous avez réussi à faire un out en espèces de 1 000 FCFA. » "
             "(texte d'Odoo, voir l'annexe B) ; avec une imprimante : un bon de sortie. Le plan se "
             "reverrouille.", ""),
            ("Hervé : ≡ → « Fermer la caisse », tape 3001.",
             "Fenêtre « Fermeture de la caisse » : en haut le nombre de commandes et leur montant "
             "(« 6 commandes : 25 500 FCFA » : part 5B, tables 4, 5, 1, 6 et 11), bouton « Entrée ou sortie d'espèces », ligne « Entrées "
             "et sorties d'espèces » où figure la sortie de 1 000 FCFA — écran 16.", ""),
            ("Taper 24 500 dans « Comptage de caisse » (25 500 encaissés en espèces − 1 000 sortis), "
             "toucher « Fermer la caisse ». Si un autre montant est tapé, Odoo demande d'abord "
             "« Écart de règlement » : toucher « Poursuivre ».",
             "Fenêtre « Fermer la caisse » : « 2 tables sont encore ouvertes : <numéros>. "
             "Encaissez-les, ou annulez-les avec un motif, avant de fermer. », boutons « Voir les "
             "tables » et « Annuler ces tables » (écran 17 : la variante à une table).", "R42"),
            ("Toucher « Annuler ces tables ».",
             "Fenêtre « Annuler les tables encore ouvertes : <numéros> », « Pourquoi ? » : le code "
             "n'est pas redemandé (écran 18).", "R42"),
            ("Toucher « Client parti ».",
             "La caisse se ferme ; chaque produit des deux tables est tracé (nature « Fermeture »). "
             "La tablette se recharge sur le plan, caisse fermée.", "R42"),
            ("Gestion (manager) : Point de Vente → Analyse → Rapport de session, ou bouton "
             "« Ventes du jour » de la fenêtre de fermeture ; lire le rapport de la session.",
             "Bloc « Tables et personnes » (Nombre de tables, Nombre de personnes, Ventes sans "
             "table) et bloc « Annulations » (Table, Produit, Quantité, Montant, Motif, Autorisée "
             "par), avec leur total : le chef de salle n'a rien à rédiger, il signe (écran 19). "
             "Les quantités vendues de chaque produit y figurent aussi.", "R95 R92"),
            ("Gestion : Point de Vente → Commandes → Sessions → la session du jour.",
             "« Caisse ouverte par » : Clarisse ; « Caisse fermée par » : Hervé.", ""),
        ],
        captures=[("14_fermeture_de_la_caisse.jpg",
                   "La fenêtre de fermeture : « Entrée ou sortie d'espèces », comme le menu ≡."),
                  ("15_fermeture_une_table_encore_ouverte.jpg",
                   "Une table encore ouverte : l'encaisser, ou l'annuler avec un motif."),
                  ("16_fermeture_annuler_ces_tables.jpg",
                   "« Annuler ces tables » : une fenêtre, un motif, sans retaper le code."),
                  ("26_rapport_de_fermeture.jpg",
                   "Le rapport de fermeture : tables, personnes, annulations et qui les a autorisées.")],
        encadres=[("attention", "Après chaque fermeture, Odoo rouvre seul une session en "
                   "« Contrôle à l'ouverture » : c'est normal. Le lendemain, la caissière ouvre la "
                   "caisse avec son code, le fond est prérempli.")],
    ),
    dict(
        id="S14", partie="B", titre="Le rapport des annulations",
        roles="Manager (compte manager) ; chef / chef", base="aite_resto", quand="Jour 1, après S13",
        prerequis="Jour 1 joué tel qu'écrit (S07, S08, S13).",
        but="Chaque annulation se lit : qui l'a demandée, qui l'a autorisée, pourquoi ; les "
            "déplacements n'y sont jamais ; ce qui arrive sans code est tracé à part.",
        etapes=[
            ("Restaurant → Annulations (filtre « Aujourd'hui » d'office).",
             "Colonnes Date, Table, Produit, Quantité, Montant TTC, Demandée par, Autorisée par, "
             "Motif, Précision, et les totaux en bas (écran 20).", "R47 R80"),
            ("Lire les lignes du jour 1.",
             "Sept lignes : Castel 65 cl (table 4, Brice → Hervé, Autre, « Bouteille cassée au "
             "service ») ; Café expresso (table 7, Client parti) ; Top Ananas 35 cl (table 12) ; "
             "Thé (table 99, Erreur de saisie) ; Coca-Cola 33 cl (table 3, sans « Autorisée par ») ; "
             "Mützig 65 cl × 2 (table 2) et Café expresso (table 7) à la fermeture. Total : 8 unités, "
             "7 500 FCFA.", "R46 R80"),
            ("Aucune ligne pour les tables 5, 6 et 9.",
             "La division, le déplacement et la réunion de S09 n'y figurent pas.",
             "R41 R48 R55 R58 R62 R82"),
            ("Filtre « Sans code ».",
             "La seule ligne de la table 3, sans « Autorisée par » ; colonne « Nature » (à afficher "
             "par le sélecteur de colonnes) : « Annulation sans code ». La vente n'a jamais été "
             "bloquée.", "R52"),
            ("« Regrouper par » « Autorisée par », puis « Motif » ; vue croisée.",
             "Un sous-total par responsable, puis par motif.", "R81"),
            ("Changer de compte : chef / chef, Restaurant → Annulations.",
             "Les mêmes lignes ; rien d'autre n'est accessible.", "R83"),
        ],
        captures=[("22_annulations_du_jour.jpg", "Restaurant → Annulations : la trace du jour.")],
        encadres=[],
    ),
    # ════════════════════════ C. RAPPORTS (JOUR 2) ═══════════════════════
    dict(
        id="S15", partie="C", titre="Personnes et tables : une journée qui se compte juste",
        roles="Caissière (Clarisse 2001) ; Serveurs ; Manager (gestion)", base="aite_resto",
        quand="Jour 2, en premier (aucune autre vente ce jour-là)",
        prerequis="Jour 1 terminé (S14). Clarisse rouvre la caisse : « Ouvrir la caisse », 2001, "
                  "« J'ouvre la caisse » (fond prérempli).",
        but="Les chiffres du manager : tables, personnes, ventes, une division comptée une fois, "
            "ni les tables ouvertes ni les annulées.",
        etapes=[
            ("Brice ouvre la table 2 (2 personnes) : « Bouteille de vin blanc » et trois « Poulet "
             "DG » ; « J'envoie ».", "Table 2 : 30 000 FCFA.", ""),
            ("Brice ouvre la table 4 (4 personnes) : quatre « Pizza Margherita » et quatre « Ndolé "
             "crevettes » ; « J'envoie ».", "Table 4 : 40 000 FCFA.", ""),
            ("Nadège ouvre la table 7 avec 5 personnes : « Bouteille de whisky » et cinq « Ndolé "
             "crevettes » ; « J'envoie ».", "Table 7 : 60 000 FCFA, « 5 personnes ».", ""),
            ("Nadège rouvre la table 7, touche « 5 personnes », puis 7.",
             "Le bouton dit « 7 personnes » (deux touches).", "R26"),
            ("Retoucher « 7 personnes » et chercher un 0.",
             "Aucun moyen de saisir 0 personne ; la table garde 7.", "R28"),
            ("Clarisse encaisse les tables 2, 4 et 7 (espèces).", "Les trois tables sont grises.", ""),
            ("Gestion (manager) : Point de Vente → Analyse → « Personnes et tables » (filtre "
             "« Aujourd'hui »).",
             "Tableau croisé : Tables 3, Personnes 13, Ventes sans table 0, Total 130 000 sur la "
             "même page (écran 21) ; la table 7 compte 7 personnes.", "R91 R27"),
            ("Point de Vente → Tableau de bord.",
             "Prix moyen par personne : 10 000 FCFA (tableau standard d'Odoo, qui compterait aussi "
             "les ventes sans table et les remboursements : à contrôler à l'écran).", "R97"),
            ("Brice ouvre la table 5 (6 personnes) : six « Café expresso » ; « J'envoie ». "
             "Clarisse divise trois cafés en une part, encaisse la part, puis la table 5.",
             "Deux additions payées pour la table 5.", ""),
            ("Relire « Personnes et tables ».",
             "Tables 4, Personnes 19 : la table divisée compte une fois, pour 6 personnes.", "R93"),
            ("Brice ouvre la table 8 (2 personnes) et la laisse ouverte ; il ouvre la table 9 "
             "(2 personnes), y envoie un « Thé » ; Hervé annule la table 9 (« Annuler la table », "
             "« Client parti »). Relire le rapport.",
             "Inchangé : ni la table ouverte ni la table annulée ne sont comptées (ni les "
             "remboursements).", "R94"),
            ("Vue Liste (icône en haut à droite), puis « Regrouper par » « Ouverte par », puis "
             "« Encaissée par ».",
             "Colonnes Date, Table, Personnes, Articles, Ouverte par, Encaissée par, Total en FCFA "
             "(écran 22) ; tables, personnes et montants se lisent par serveur, puis par personne "
             "qui a encaissé.", "R07"),
            ("Filtre « Cette semaine » ; puis Restaurant → Annulations, filtre « Cette semaine ».",
             "Les chiffres du lundi à aujourd'hui (jours 1 et 2).", "R88"),
            ("Filtres → « Ajouter un filtre personnalisé » : Date est entre le premier et le "
             "quinzième jour d'une période qui contient le jour 1 (format jj/mm/aaaa).",
             "Seules les ventes de ces quinze jours sont comptées.", "R89"),
            ("Choisir une période sans vente (« Période » → un mois passé), en vue Liste.",
             "« Aucune addition encaissée sur cette période. … Changez la période pour voir les "
             "autres jours. »", "R90"),
            ("Tableau de bord sur cette période sans table servie.",
             "Aucune moyenne par personne n'est affichée.", "R98"),
            ("Point de Vente → Analyse → « Détails des ventes » : même période (dates de début et "
             "de fin), imprimer.",
             "Quantité vendue et montant de chaque produit, par catégorie ; les mêmes quantités "
             "que dans le rapport de fermeture de la session.", "R92"),
        ],
        captures=[("20_personnes_et_tables.jpg",
                   "« Personnes et tables » : tables, personnes, ventes sans table, articles, total."),
                  ("21_personnes_et_tables_liste.jpg",
                   "La même analyse en liste : qui a ouvert, qui a encaissé.")],
        encadres=[("attention", "Le tableau croisé affiche « Articles » avec deux décimales et les "
                   "montants sans « FCFA » (format d'Odoo) ; la liste, elle, écrit « FCFA ».")],
    ),
    dict(
        id="S16", partie="C", titre="Les droits : ce qu'un serveur ne peut pas faire, le profil du chef",
        roles="Les cinq codes ; Manager ; compte chef / chef ; admin", base="aite_resto",
        quand="Jour 2, après S15",
        prerequis="S15 joué : caisse ouverte, des additions payées dans la journée (pour le "
                  "remboursement). L'ouverture de la caisse par niveau a été jouée en S03 et S13.",
        but="Le tableau des droits, niveau par niveau ; un niveau changé s'applique à la "
            "réouverture ; le chef de salle lit les rapports sans aucun accès à la caisse.",
        etapes=[
            ("Avec chaque code (1001, 2001, 3001, 4001), essayer : encaisser (« J'encaisse » puis "
             "« Retour »), ≡ → « Entrée ou sortie d'espèces » (puis abandonner), ≡ → « Fermer la "
             "caisse » (puis « Ignorer »), annuler un produit envoyé (puis « Retour »).",
             "Serveur : refusé partout, avec le message du geste ; caissière : encaisse ; chef de "
             "salle : en plus espèces, annulation et fermeture ; manager : tout. Cocher le "
             "tableau « Qui peut quoi » (chapitre 2).", "R10"),
            ("Identifié avec 1001 sur une table : « Actions ».",
             "Pas de « Remboursement » (réservé au manager) ; pas de « Liste de prix ».", "R10 R14"),
            ("Clarisse : ≡ → « Commandes » (2001), filtre des commandes payées, choisir une "
             "addition payée, « Remboursement ».",
             "Refus : « Seul le manager peut rembourser une addition payée. » ; avec 4001, le "
             "remboursement s'ouvre (ne pas valider).", "R10"),
            ("S'il y a une imprimante : Brice, ≡ → « Imprimer le rapport », tape 1001.",
             "Refus : « Seuls la caissière, le chef de salle et le manager impriment le rapport des "
             "ventes. »", "R14 R10"),
            ("Gestion (manager) : Employés → « Nadège » → « Niveau en caisse » = Caissière ; "
             "enregistrer. Caisse : recharger la page.", "Le niveau est enregistré.", "R11"),
            ("Nadège ouvre sa table, ajoute un produit, « J'encaisse », tape 1002.",
             "Le paiement s'ouvre : le nouveau niveau s'applique dès la réouverture. Toucher "
             "« Retour », retirer le produit, puis remettre Nadège en Serveur et recharger.", "R11"),
            ("Se connecter avec chef / chef.",
             "Seul le menu « Restaurant » est proposé ; ni Point de Vente, ni Commandes, ni "
             "configuration de la caisse.", "R83"),
            ("Restaurant → Annulations.",
             "Le rapport des annulations s'ouvre (filtre « Aujourd'hui »).", "R83"),
            ("Avec manager / manager, puis admin / admin : Restaurant → Annulations, ouvrir une "
             "ligne, essayer de la modifier ; puis la sélectionner et essayer de la supprimer.",
             "Refusé pour les deux comptes : « Une annulation enregistrée ne se modifie pas et ne "
             "s'efface pas : c'est la trace demandée par le manager. »", "R49"),
        ],
        captures=[],
        encadres=[],
    ),
    dict(
        id="S17", partie="C", titre="Ventes par famille, serveur et « Encaissée par »",
        roles="Manager (compte manager)", base="aite_resto", quand="Jour 2",
        prerequis="Des ventes de bières, de vins et de sodas (jours 1 et 2).",
        but="Les familles se lisent sur trois niveaux ; le serveur et la caissière apparaissent "
            "dans l'analyse AITE, même sous un seul compte de caisse.",
        etapes=[
            ("Point de Vente → Analyse → Analyse AITE → Tableau croisé & graphique ; « Favoris » → "
             "« Ventes par famille ».",
             "Lignes Famille > Sous-famille (« Nourriture / Pizzas », « Boisson / Alcoolisé »…), "
             "une seule colonne « Total » avec ses quatre mesures (écran 23) ; « Boisson » = "
             "Alcoolisé + Non alcoolisé.", "R84"),
            ("Taper « Pizzas » dans la recherche, choisir « Famille ».",
             "Seules les pizzas, avec quantités et montants.", "R85"),
            ("Remplacer par « Alcoolisé » (Famille).",
             "« Non alcoolisé » n'est pas ramené.", "R85"),
            ("Taper « Castel 65 cl », choisir « Produit ».", "Seules les ventes de la Castel.", "R86"),
            ("Sans filtre : comparer la somme des familles au total.",
             "La somme des familles est le total ; un produit rangé dans plusieurs familles ne "
             "compte que dans la première.", "R87"),
            ("« Regrouper par » « Serveur », puis « Encaissée par » ; ouvrir aussi « Compte Odoo ».",
             "Brice et Nadège sont distingués ; « Encaissée par » donne Clarisse, Sandrine ; le "
             "compte de la tablette s'affiche « Compte Odoo » (toutes les ventes sous « Caisse de "
             "la salle »).", "R102"),
        ],
        captures=[("23_ventes_par_famille.jpg",
                   "Le favori « Ventes par famille » : Famille > Sous-famille, une colonne « Total ».")],
        encadres=[("attention", "Sur la carte de démonstration, les plats n'ont pas de coût : leur "
                   "marge paraît à 100 %. C'est attendu.")],
    ),
    dict(
        id="S18", partie="C", titre="L'ardoise : réservée au manager, née d'une addition réglée",
        roles="Manager (Sandrine 4001) ; Caissière (Clarisse 2001) ; Chef (Hervé 3001) ; admin",
        base="aite_resto", quand="Jour 2",
        prerequis="« Ardoise client » parmi les modes de la caisse (S01). Caisse ouverte.",
        but="L'ardoise n'apparaît qu'au manager ; elle ne naît que d'une addition payée ; une "
            "addition annulée n'en laisse aucune.",
        etapes=[
            ("Brice ouvre la table 10 (2 personnes), « Poulet DG », « J'envoie ». Clarisse : table 10, "
             "2001, « J'encaisse ».",
             "Écran de paiement sans « Mettre sur ardoise » ni « Ardoise client ». « Retour », "
             "« Plan ».", "R101"),
            ("Sandrine : table 10, 4001, « J'encaisse ».",
             "« Mettre sur ardoise » et « Ardoise client » sont proposés.", "R101"),
            ("Toucher « Mettre sur ardoise » sans client.",
             "« Sélectionnez d'abord un client pour une vente à crédit. »", ""),
            ("Choisir un client (« Client »), choisir le mode « Ardoise client », puis « Plan » sans "
             "valider.", "Retour au plan ; la table 10 reste ouverte.", "R100"),
            ("Admin : POS Crédit → Ardoises.", "Aucune ardoise pour cette table.", "R100"),
            ("Hervé : table 10, 3001, « Actions » → « Annuler la table », « Client parti ». Relire "
             "POS Crédit → Ardoises.", "Toujours aucune ardoise ouverte.", "R100"),
            ("Brice ouvre la table 3, « Poulet DG », « J'envoie » ; Sandrine : table 3, 4001, "
             "« J'encaisse », client, « Ardoise client », « Valider ».",
             "Retour au plan ; POS Crédit → Ardoises : une ardoise de 6 000 FCFA au nom du client.",
             "R100"),
        ],
        captures=[],
        encadres=[],
    ),
    # ════════════════════ D. INSTALLATION ET NON-RÉGRESSION ══════════════════
    dict(
        id="S19", partie="D", titre="Installer le restaurant sur une base vierge",
        roles="AITE (admin)", base="nouvelle base (par l'écran de création)", quand="Indépendant",
        prerequis="Les 4 dossiers du §9.1 d'INSTALLATION déposés à côté des autres addons ; Odoo "
                  "redémarré.",
        but="Un restaurant seul s'installe sans aucun module hôtelier, en FCFA, avec une caisse "
            "prête au premier service ; un seul journal d'espèces.",
        etapes=[
            ("Écran de création de base d'Odoo : pays Cameroun, langue Français, sans données de "
             "démonstration.", "La base est créée ; la société est en FCFA.", "R103"),
            ("Paramètres → « Activer le mode développeur » ; Apps → « Mettre à jour la liste des "
             "Apps » → « Mettre à jour ».", "La liste est à jour.", "R103"),
            ("Apps, sans le filtre « Apps » : « service à table » → « AITE — Restaurant (service à "
             "table) » → « Activer » ; puis « POS Analytics » et « Crédit clients » → « Activer ».",
             "Installation sans erreur ; « AITE — Analyses du restaurant par employé » s'est "
             "installé seul.", "R103"),
            ("Ouvrir Point de Vente.",
             "Caisse « Restaurant » prête : Espèces, Mobile Money, salle « Salle », case « Service à "
             "table contrôlé » cochée ; aucun menu ni module hôtelier.", "R103"),
            ("Facturation → Configuration → Comptabilité → Journaux : regarder les journaux de type "
             "« Espèces ».",
             "Un seul journal d'espèces (« Espèces »), celui des Espèces de la caisse "
             "« Restaurant ».", "R104"),
            ("Point de Vente → Configuration → Point de vente → Nouveau : nom « Bar », Enregistrer.",
             "La caisse « Bar » est créée.", "R104"),
            ("Regarder les modes de paiement de « Bar », puis revenir aux journaux.",
             "« Bar » a « Espèces » et « Mobile Money » ; ses Espèces sont sur un nouveau journal "
             "« Espèces Bar » ; aucun journal d'espèces sans mode de paiement.", "R104"),
        ],
        captures=[],
        encadres=[("regle", "Créer la base avec le pays Cameroun : une base sans pays naît en "
                   "dollars, et Odoo refuse ensuite de changer la devise.")],
    ),
    dict(
        id="S20", partie="D", titre="Non-régression : une caisse hors restaurant",
        roles="AITE (admin)", base="base de S19", quand="Après S19",
        prerequis="La caisse « Bar » de S19 ; « Ardoise client » ajouté à ses modes de paiement "
                  "(Paramètres → caisse « Bar » → « Modes de paiement »).",
        but="Une caisse qui n'est pas au service à table contrôlé se comporte comme avant.",
        etapes=[
            ("Point de Vente → « Bar » → « Ouvrir la caisse ».",
             "La caisse d'Odoo s'ouvre comme avant : pas de fenêtre du code, pas de plan verrouillé, "
             "pas de légende.", ""),
            ("Ajouter un produit, aller au paiement.",
             "Le bouton « Mettre sur ardoise » est là, comme avant ; le mode « Ardoise client » "
             "aussi.", "R101"),
            ("Encaisser en espèces, puis Point de Vente → Analyse → « Personnes et tables ».",
             "La vente du Bar compte comme une « Vente sans table » (caisses mêlées, limite connue, "
             "point 12 des notes de version).", ""),
        ],
        captures=[],
        encadres=[],
    ),
    dict(
        id="S21", partie="D", titre="La carte du client sur une base de démonstration neuve",
        roles="AITE (admin) ; Serveur (Brice 1001) ; Caissière (Clarisse 2001)",
        base="aite_messager (neuve)", quand="Indépendant",
        prerequis="La base aite_messager n'existe pas ; un seul Odoo lancé à la fois.",
        but="La base de démonstration porte la carte du client ; la vente sans table se règle "
            "avant la première ouverture de la caisse.",
        etapes=[
            ("Lancer PG_HOST=localhost PYTHON=../venv312/bin/python dev/setup_env.sh --restaurant "
             "--carte-messager.",
             "La base aite_messager est créée ; la ligne de la carte commence par « seed carte Le "
             "Messager OK » et annonce « en place : 101 produits à la carte (101 attendus) » et "
             "la société « Restaurant Le Messager ».", ""),
            ("Admin : Point de Vente → Configuration → Produits → Catégories de produits du PdV.",
             "Petit déjeuner, Plats, Pizzas & burgers, Afternoon tea, Bar, avec leurs "
             "sous-familles (Bar > Vins > Vins rouges, Bar > Whisky, Bar > Sans alcool > Eaux…).", ""),
            ("Ouvrir « Médoc » et « Poulet DG ».",
             "Médoc : 20 000 FCFA, coût 9 500, « Suivre l'inventaire » coché, aucune taxe ; "
             "Poulet DG : 5 000 FCFA, sans coût ni suivi ; la note interne d'un produit à valider "
             "commence par « À valider par le client ».", ""),
            ("Avant toute ouverture de la caisse : Paramètres → caisse « Restaurant » → cocher "
             "« Autoriser la vente sans table », « Enregistrer ».",
             "La phrase sous la case dit qu'une fois cochée, le bouton « + » ouvre une vente au "
             "comptoir ou à emporter, sans table ni nombre de personnes ; la case s'enregistre "
             "(aucune session n'existe encore).", "R19"),
            ("Ouvrir la caisse (Clarisse 2001, « J'ouvre la caisse ») ; Brice touche « + » dans la "
             "barre du plan et tape 1001.",
             "Fenêtre « Qui prend la main ? Tapez votre code » ; refus : « La vente sans table "
             "n'est pas ouverte ici. Ouvrez une table du plan. »", "R19"),
            ("Clarisse touche « + » et tape 2001.",
             "Une vente sans table s'ouvre, sans demande de personnes (0 personne).", "R19"),
            ("Brice ouvre une table et touche « Poulet DG ».",
             "Une petite fenêtre propose l'accompagnement (Riz nature déjà coché) ; l'ajouter.", ""),
            ("Servir et encaisser deux tables (4 et 2 personnes) et trois ventes sans table ; "
             "Personnes et tables.",
             "2 tables, 6 personnes et, à part, 3 ventes sans table.", "R96"),
            ("Analyse AITE → Tableau croisé & graphique, recherche « Bar » (Famille).",
             "Les boissons ont une marge réelle (Médoc : coût 9 500 pour 20 000) ; un plat sans coût "
             "paraît à 100 % : en démonstration, filtrer sur « Bar ».", ""),
        ],
        captures=[],
        encadres=[("attention", "La base aite_messager est une démonstration : coûts, stocks de "
                   "départ et boissons hors carte sont des estimations à faire valider par le client.")],
    ),
    dict(
        id="S22", partie="D", titre="Installer la carte sur une base existante",
        roles="AITE (admin)", base="aite_resto, puis la base de S19", quand="Indépendant",
        prerequis="Le dossier aite_resto_carte_messager déposé à côté des modules du restaurant ; "
                  "Odoo redémarré ; « Mettre à jour la liste des Apps » fait.",
        but="Le module refuse une base qui porte la carte de démonstration ; ailleurs il pose la "
            "carte sans renommer la société ; rejouer la carte ne crée rien deux fois ; le "
            "désinstaller ne retire pas la carte.",
        etapes=[
            ("Sur aite_resto (carte de démonstration) : Apps → chercher « Messager » → « Activer ».",
             "Refus : le message dit que « cette base porte la carte de démonstration de "
             "seed_restaurant.py (…) : rien n'est posé » ; le module reste non installé.", ""),
            ("Sur la base de S19 : Paramètres → Sociétés → renommer la société « Mon restaurant ».",
             "Le nom est enregistré.", ""),
            ("Apps → « Messager » → « Activer ».",
             "Installation sans erreur ; la caisse « Restaurant » propose la carte du client "
             "(familles Petit déjeuner, Plats, Pizzas & burgers, Afternoon tea, Bar).", ""),
            ("Paramètres → Sociétés.", "La société s'appelle toujours « Mon restaurant ».", ""),
            ("AITE, en ligne de commande, sur aite_messager : rejouer deux fois odoo-bin shell … < "
             "dev/seeds/seed_carte_messager.py.",
             "La seconde fois : « créés : 0 familles, 0 catégories, 0 produits » ; le nombre de "
             "produits en place ne change pas.", ""),
            ("Base de S19 : Apps → « Messager » → « Désinstaller ».",
             "Le module est désinstallé ; les produits de la carte restent dans la caisse.", ""),
        ],
        captures=[],
        encadres=[],
    ),
]

# Questions fréquentes du testeur (réponses tirées des notes de version §7 et §10).
FAQ = [
    ("« Tableau » s'affiche au lieu de « Table » dans la barre du plan.",
     "Collision de traductions d'Odoo, connue et instable (notes §7, point 17). Noter l'écart dans "
     "« Observations », ne pas compter KO pour le restaurant."),
    ("« Bon d'annulation envoyé. » n'apparaît pas.",
     "Il n'apparaît qu'avec une imprimante de cuisine réelle ; la base de recette n'en a pas."),
    ("Je ne peux plus cocher « Service à table contrôlé » ni « Autoriser la vente sans table ».",
     "Une session « Contrôle à l'ouverture » existe depuis la première ouverture : ces deux cases "
     "se règlent avant (point 25). Pour la vente sans table, jouer S21 sur une base neuve."),
    ("La notification dit « Envoyé : Pizzas × 1, Bière × 2. »",
     "Elle compte par famille la plus fine du produit, sous la forme « famille × quantité » : le nom de la famille est repris tel quel, sans accord à faire (point 26)."),
    ("Un poste a été laissé sur l'écran de commande et est revenu au plan.",
     "Retour automatique après 5 minutes sans toucher l'écran (point 1, écart Q17)."),
    ("La fenêtre d'espèces dit « Cash entrant » / « Cash sortant ».",
     "Fenêtre d'Odoo non reprise par le module ; le menu ≡ et la fermeture disent « Entrée ou "
     "sortie d'espèces »."),
    ("Hors connexion, une bouteille épuisée a été vendue.",
     "Attendu : hors connexion, la caisse vend sans contrôle de stock (limite connue)."),
]
