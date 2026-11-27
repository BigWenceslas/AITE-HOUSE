# -*- coding: utf-8 -*-
"""Scénarios de test du kit intégrateur — Restaurant Le Messager.

Périmètre UNIQUE : les nouvelles fonctionnalités de aite_pos_restaurant
18.0.1.0.11 à 18.0.1.0.14 et de aite_resto_carte_messager 18.0.1.3.5 et
18.0.1.3.6 (plus un test rapide de non-régression).

Ce fichier ne contient que des données : la liste SCENARIOS. Le script
build_scenarios.py (même dossier) en tire :
  - AITE_Scenarios_Test_Restaurant_v18.0.1.0.14.xlsx (à remplir OK / KO) ;
  - AITE_Scenarios_Test_Restaurant_v18.0.1.0.14.pdf (à imprimer et cocher).

Chaque étape est un couple (action, ce que l'on doit voir). Les libellés
entre « » sont ceux de l'écran. Chaque scénario a été joué une fois avant
livraison sur une base de test (carte Le Messager posée à neuf, imprimantes
Epson simulées) : le champ « verifie » le dit.
"""

VERSION = "18.0.1.0.14"
DATE_VERIFICATION = "27/11/2026"

# Fonctionnalités du lot (code, nom simple, module et version).
FONCTIONS = [
    ("F1", "« Addition » sur une table divisée", "aite_pos_restaurant 18.0.1.0.11"),
    ("F2", "Partager l'addition à parts égales", "aite_pos_restaurant 18.0.1.0.12"),
    ("F3", "Bon de cuisine en plusieurs exemplaires, bons en français, alerte de panne", "aite_pos_restaurant 18.0.1.0.13"),
    ("F4", "Notes de commande (6 corrections)", "aite_pos_restaurant 18.0.1.0.13"),
    ("F5", "Une imprimante par poste, imprimante « Autre », familles oubliées", "aite_pos_restaurant 18.0.1.0.14"),
    ("F6", "Impression directe sur les Epson (http et https)", "aite_pos_restaurant 18.0.1.0.14"),
    ("F7", "Addition et ticket groupés par famille", "aite_pos_restaurant 18.0.1.0.14"),
    ("F8", "La carte appartient au client (mise à niveau sans écrasement)", "aite_resto_carte_messager 18.0.1.3.5"),
    ("F9", "Réglage « grouper par famille » posé une seule fois", "aite_resto_carte_messager 18.0.1.3.6"),
    ("NR", "Non-régression : envoyer et encaisser", "aite_pos_restaurant 18.0.1.0.14"),
]

# Les personnes du test. Les prénoms et codes sont ceux de l'équipe de
# démonstration posée par la carte ; chez le client, prendre un employé réel
# du même niveau (fiche employé, « Niveau en caisse »).
PERSONNES = [
    ("Serveur 1", "Serveur", "Brice", "1001"),
    ("Serveur 2", "Serveur", "Nadège", "1002"),
    ("Caissière", "Caissière", "Clarisse", "2001"),
    ("Chef de salle", "Chef de salle ou superviseur", "Hervé", "3001"),
    ("Manager", "Manager", "Sandrine", "4001"),
    ("Intégrateur", "Compte Odoo administrateur", "—", "mot de passe admin"),
]

# Les cinq imprimantes de préparation recommandées (familles de la carte).
IMPRIMANTES = [
    ("Chaud", "192.168.1.51", "Plats, Petit déjeuner, Pizzas & burgers / Burgers, Pizzas & burgers / Pastas"),
    ("Pizza", "192.168.1.52", "Pizzas & burgers / Pizzas"),
    ("Froid", "192.168.1.53", "Pizzas & burgers / Crêpes & glaces, Afternoon tea"),
    ("Bar", "192.168.1.54", "Bar"),
    ("Autre", "192.168.1.55", "aucune famille ; case « Prend tout ce qu'aucune autre imprimante ne prend » cochée"),
]

# Prix de référence de la carte de démonstration (FCFA), utilisés dans les
# montants attendus. Chez le client, comparez avant de commencer.
PRIX = [
    ("Poulet DG", "5 000"), ("Ndolé viande", "3 000"), ("Pizza Marguerite Petit", "5 000"),
    ("Pizza Marguerite Grand", "10 000"), ("Crêpe nature", "2 000"), ("Bière blonde 65 cl", "1 500"),
    ("Tea Time 2 pers avec Moscato", "20 000"), ("Eau minérale 0,5 L", "500"),
    ("Café expresso", "1 000"), ("Gambas DG", "10 000"),
    ("Bougie d'anniversaire (créée en ST-05)", "500"),
]

JOUE = "Joué le %s sur une base de test : conforme." % DATE_VERIFICATION

# Chemins répétés.
PARAMETRES = ("Point de Vente → Configuration → Paramètres ; en haut, la caisse « Restaurant » "
              "est choisie")
LISTE_IMPRIMANTES = ("Point de Vente → Configuration → Paramètres → bloc « Préparation » → "
                     "lien « → Imprimantes » (ou, une fois la case cochée, Point de Vente → "
                     "Commandes → Imprimantes de préparation)")
REOUVRIR = ("Sur la tablette : rechargez la page (touche F5 ou glisser vers le bas), ou fermez "
            "puis rouvrez la caisse")
REIMPRIMER = ("touchez ≡ (en haut à droite) → « Commandes 1… » → tapez le code de la caissière si demandé → "
              "touchez le filtre « Toutes les commandes actives » → « Payé » → touchez la "
              "commande en haut de la liste → « Imprimer le ticket »")

SCENARIOS = [
    # ================================================================ A
    # Contrôles après la mise à niveau (intégrateur, écrans de gestion)
    dict(
        id="ST-01", f="F8", version="18.0.1.0.14 / 1.3.6", bloc="A. Contrôles après la mise à niveau",
        titre="Les bonnes versions sont installées",
        role="Intégrateur (compte admin)",
        prerequis="La mise à niveau du serveur est faite (procédure du guide, étapes 1 à 8).",
        donnees="Aucune.",
        etapes=[
            ("Dans le navigateur, ajoutez ?debug=1 après /odoo dans l'adresse "
             "(ex. https://votre-serveur/odoo?debug=1), puis ouvrez Apps.",
             "Une petite icône d'insecte apparaît en haut : le mode développeur est actif."),
            ("Dans la barre de recherche, retirez le filtre « Apps » (croix), puis passez en vue liste "
             "(icône liste, en haut à droite).",
             "La liste des modules, avec les colonnes « Nom technique », « Dernière version » et « Statut »."),
            ("Cherchez aite_pos_restaurant.",
             "« AITE — Restaurant (service à table) » : Dernière version 18.0.1.0.14, Statut « Installé »."),
            ("Cherchez aite_resto_carte_messager.",
             "« AITE — Carte du restaurant Le Messager (démonstration) » : 18.0.1.3.6, « Installé »."),
            ("Cherchez pos_epson_printer.",
             "« Imprimante Epson PdV » : Statut « Installé »."),
        ],
        attendu="Les trois modules sont « Installé », aux versions 18.0.1.0.14 et 18.0.1.3.6. "
                "Faites ce contrôle sur CHAQUE base mise à niveau.",
        recette="—", verifie=JOUE,
    ),
    dict(
        id="ST-02", f="F9", version="carte 18.0.1.3.6", bloc="A. Contrôles après la mise à niveau",
        titre="Le réglage « grouper par famille » a été coché une fois par la mise à niveau",
        role="Intégrateur (compte admin)",
        prerequis="ST-01 OK.",
        donnees="Aucune.",
        etapes=[
            ("Ouvrez " + PARAMETRES + ". Descendez jusqu'au bloc « Mode restaurant ».",
             "La case « Service à table contrôlé » est cochée."),
            ("Juste en dessous, lisez la case « Grouper les produits par famille sur l'addition et le ticket ».",
             "Elle est cochée. Sa phrase commence par « Coché : sur l'addition (bouton « Addition », y compris "
             "les additions d'une table divisée) et sur le ticket remis au client… »."),
            ("Montrez ce réglage au gérant et demandez-lui s'il le garde.",
             "S'il ne le veut pas : décochez, « Enregistrer ». Notez sa décision dans « Observations »."),
        ],
        attendu="Après la mise à niveau, la case est cochée (posée une seule fois par la carte 18.0.1.3.6).",
        recette="R111 (préalable)", verifie=JOUE,
    ),
    dict(
        id="ST-03", f="F8", version="carte 18.0.1.3.5", bloc="A. Contrôles après la mise à niveau",
        titre="Un produit modifié par le client n'est pas écrasé",
        role="Intégrateur (compte admin)",
        prerequis="ST-01 OK. Le produit « Poulet DG » existe (5 000 FCFA). Faites ce test hors service.",
        donnees="Nom de test « Poulet DG maison », prix de test 7 777 FCFA.",
        etapes=[
            ("Point de Vente → Produits → Produits. Cherchez « Poulet DG », ouvrez la fiche.",
             "La fiche « Poulet DG », Prix de vente 5 000 FCFA."),
            ("Renommez-la « Poulet DG maison », mettez le prix de vente à 7 777, « Enregistrer » (icône nuage).",
             "La fiche est enregistrée."),
            ("Point de Vente → Configuration → « Poser la carte Le Messager ».",
             "Une notification « Carte Le Messager » : « <société> : Carte posée : 101 produits en 30 familles ; "
             "salle : 12 tables ; équipe : 7 employés, 3 comptes. Rien n'a été créé en double. La carte est à "
             "vous : une mise à niveau ne modifie aucun de vos produits… » (les nombres peuvent différer chez le client)."),
            ("Retournez dans Produits, cherchez « Poulet DG ».",
             "Une seule fiche : « Poulet DG maison », « Prix : 7 777,00 FCFA ». Aucun nouveau « Poulet DG » n'a été créé."),
            ("Remettez le nom « Poulet DG » et le prix 5 000, « Enregistrer ».",
             "La fiche est revenue à son état de départ."),
        ],
        attendu="Le nom et le prix modifiés restent ; rien n'est créé en double. "
                "(Une mise à niveau du module se comporte comme ce menu.)",
        recette="— (tests test_carte_du_client.py)", verifie=JOUE,
    ),
    dict(
        id="ST-04", f="F8", version="carte 18.0.1.3.5 / 1.3.6", bloc="A. Contrôles après la mise à niveau",
        titre="Un produit archivé ne revient pas ; le réglage décoché reste décoché",
        role="Intégrateur (compte admin)",
        prerequis="ST-03 OK.",
        donnees="Produit de test « Gambas DG » (10 000 FCFA).",
        etapes=[
            ("Produits → ouvrez « Gambas DG » → roue dentée ⚙ à côté du nom → « Archiver » → confirmez « Archiver ».",
             "La fiche porte le bandeau « Archivé »."),
            ("Ouvrez " + PARAMETRES + ", décochez « Grouper les produits par famille sur l'addition et le ticket », "
             "« Enregistrer ».",
             "La case est décochée."),
            ("Point de Vente → Configuration → « Poser la carte Le Messager ».",
             "La notification « … Rien n'a été créé en double… »."),
            ("Produits : cherchez « Gambas DG ».",
             "Aucune fiche trouvée : le produit reste archivé."),
            ("Paramètres : relisez la case « Grouper les produits… ».",
             "Elle est toujours décochée."),
            ("Remettez en état : recochez la case (si le gérant la garde, voir ST-02), « Enregistrer » ; "
             "Produits → filtre « Archivé » → « Gambas DG » → roue dentée ⚙ → « Désarchiver ».",
             "« Gambas DG » est de nouveau en vente."),
        ],
        attendu="Le produit archivé ne revient pas, le réglage décoché n'est pas recoché.",
        recette="—", verifie=JOUE,
    ),
    # ================================================================ B
    # Réglage des imprimantes (intégrateur)
    dict(
        id="ST-05", f="F5", version="18.0.1.0.14", bloc="B. Réglage des imprimantes",
        titre="Préparer un produit de test sans famille",
        role="Intégrateur (compte admin)",
        prerequis="Aucun. Ce produit sert à ST-07, ST-11, ST-13 et ST-21 ; archivez-le à la fin de la recette.",
        donnees="« Bougie d'anniversaire », 500 FCFA, sans taxe, sans famille de caisse.",
        etapes=[
            ("Point de Vente → Produits → Produits → « Nouveau ».",
             "Une fiche produit vide."),
            ("Nom « Bougie d'anniversaire » ; Prix de vente 500 ; dans « Taxes de vente », retirez la taxe "
             "proposée (croix sur l'étiquette « 19.25% »).",
             "Prix de vente 500 FCFA, aucune taxe. Sous le nom, la case « Point de Vente » est cochée "
             "(cochez-la sinon)."),
            ("Onglet « Point de Vente » : laissez le champ « Catégorie » vide. « Enregistrer » (icône nuage).",
             "La fiche est enregistrée, sans famille de caisse."),
        ],
        attendu="Le produit existe, à 500 FCFA sans taxe, en vente en caisse, sans famille. "
                "(Sans retirer la taxe, la caisse ajouterait la TVA : 596 FCFA.)",
        recette="—", verifie=JOUE,
    ),
    dict(
        id="ST-06", f="F5", version="18.0.1.0.14", bloc="B. Réglage des imprimantes",
        titre="Créer les cinq imprimantes Epson et les relier à la caisse",
        role="Intégrateur (compte admin)",
        prerequis="Les Epson sont allumées, en Wi-Fi, avec une adresse IP réservée dans la box (voir le guide). "
                  "Une caisse fermée, ou rechargée après le réglage.",
        donnees="Chaud 192.168.1.51 · Pizza .52 · Froid .53 · Bar .54 · Autre .55 (remplacez par les vraies "
                "adresses). Familles : voir le tableau du mode d'emploi.",
        etapes=[
            ("Ouvrez " + PARAMETRES + ". Bloc « Préparation » : cochez « Imprimantes de préparation » "
             "(« Imprimer les commandes en cuisine, au bar, etc. »), « Enregistrer ».",
             "Sous la case : un champ « Imprimantes » et un lien « → Imprimantes »."),
            ("Touchez le lien « → Imprimantes », puis « Nouveau ».",
             "Le fil d'Ariane dit « Paramètres / Imprimantes de préparation ». Le formulaire a les champs "
             "« Nom de l'imprimante », « Type d'imprimante », « Catégories de produit imprimées », "
             "« Nombre d'exemplaires du bon », « Prend tout ce qu'aucune autre imprimante ne prend »."),
            ("Nom : effacez « Printer » (pré-rempli par Odoo) et tapez « Chaud » ; Type d'imprimante « Utiliser "
             "une imprimante Epson » ; « Adresse IP de l'imprimante Epson » = l'adresse réservée (ne la laissez "
             "jamais vide).",
             "Avant le choix du type, le formulaire montre « Adresse IP du proxy » (IoT Box). Dès que « Utiliser "
             "une imprimante Epson » est choisi, ce champ disparaît et « Adresse IP de l'imprimante Epson » apparaît."),
            ("« Catégories de produit imprimées » → « Ajouter une ligne » → cochez Plats, Petit déjeuner, "
             "« Pizzas & burgers / Burgers », « Pizzas & burgers / Pastas » → « Sélectionner ». « Enregistrer ».",
             "Les 4 familles sont listées. Sous « Nombre d'exemplaires du bon » (1) : « Chaque nouveau bon envoyé "
             "à cette imprimante sort en un seul exemplaire. »"),
            ("Revenez à « Imprimantes de préparation » (fil d'Ariane) et créez de même Pizza, Froid, Bar et "
             "Autre (Autre : aucune famille, case « Prend tout… » laissée décochée pour l'instant).",
             "La liste montre 5 imprimantes, avec les colonnes « Exemplaires » et « Autre ». La colonne « Adresse IP "
             "du proxy » reste vide pour les Epson : c'est normal ; l'IP se contrôle en ouvrant l'imprimante."),
            ("Revenez aux Paramètres. Dans le champ « Imprimantes » du bloc « Préparation », ajoutez les 5 "
             "imprimantes. « Enregistrer ».",
             "Les 5 noms sont dans le champ. Un cadre orange dit : « 1 produit sans famille (Bougie "
             "d'anniversaire). Leurs plats ne sortiront sur aucun bon de préparation. Cochez ces familles sur une "
             "imprimante, ou cochez « Prend tout ce qu'aucune autre imprimante ne prend » sur votre imprimante "
             "« Autre ». » Si une famille n'est cochée nulle part, la phrase commence par « Ces familles de la "
             "carte ne sont prises par aucune imprimante : … »."),
            ("Ouvrez le menu « Commandes » en haut.",
             "Il contient maintenant « Imprimantes de préparation »."),
        ],
        attendu="Cinq imprimantes Epson avec leur adresse IP et leurs familles, reliées à la caisse. "
                "Le cadre orange ne cite que ce qu'aucune imprimante ne prend (ici la bougie).",
        recette="R110", verifie=JOUE,
    ),
    dict(
        id="ST-07", f="F5", version="18.0.1.0.14", bloc="B. Réglage des imprimantes",
        titre="Une famille oubliée est signalée pendant la saisie",
        role="Intégrateur (compte admin)",
        prerequis="ST-06 OK ; la case « Prend tout… » de « Autre » est encore décochée.",
        donnees="Imprimante « Froid », famille « Afternoon tea ».",
        etapes=[
            ("Ouvrez l'imprimante « Froid » (" + LISTE_IMPRIMANTES + ").",
             "Ses familles : « Pizzas & burgers / Crêpes & glaces » et « Afternoon tea »."),
            ("Touchez la croix ✖ au bout de la ligne « Afternoon tea ». N'enregistrez pas.",
             "Aussitôt, un cadre orange : « Ces familles de la carte ne sont prises par aucune imprimante : "
             "Afternoon tea. 1 produit sans famille (Bougie d'anniversaire). Leurs plats ne sortiront sur aucun bon de préparation. Cochez ces familles sur "
             "une imprimante, ou cochez « Prend tout ce qu'aucune autre imprimante ne prend » sur votre "
             "imprimante « Autre ». »"),
            ("Touchez la croix ✖ à droite du nuage, en haut à côté du nom (infobulle « Ignorer tous les "
             "changements »).",
             "La modification est abandonnée : « Afternoon tea » reste sur Froid."),
        ],
        attendu="Le cadre orange nomme la famille oubliée avant même l'enregistrement.",
        recette="R110, R112", verifie=JOUE,
    ),
    dict(
        id="ST-08", f="F5", version="18.0.1.0.14", bloc="B. Réglage des imprimantes",
        titre="L'imprimante « Autre » prend tout ce que les autres ne prennent pas",
        role="Intégrateur (compte admin)",
        prerequis="ST-07 OK.",
        donnees="Imprimante « Autre ».",
        etapes=[
            ("Ouvrez l'imprimante « Autre ». Cochez « Prend tout ce qu'aucune autre imprimante ne prend ».",
             "La phrase devient : « Tout plat qu'aucune autre imprimante de la caisse ne prend (sa famille n'est "
             "cochée nulle part, ou il n'a pas de famille) sort sur cette imprimante, en plus des familles "
             "cochées ici : un plat envoyé n'est jamais perdu. … Il ne peut y avoir qu'une seule imprimante "
             "« Autre » par caisse. … »"),
            ("« Enregistrer ». Ouvrez les Paramètres, bloc « Préparation ».",
             "Plus de cadre orange."),
            ("Rejouez ST-07 (Froid, retirer « Afternoon tea »), puis la croix ✖ à droite du nuage (Ignorer).",
             "Cette fois, aucun cadre orange : la famille partirait sur « Autre »."),
        ],
        attendu="Avec une imprimante « Autre », plus aucune famille n'est signalée.",
        recette="R110", verifie=JOUE,
    ),
    dict(
        id="ST-09", f="F5", version="18.0.1.0.14", bloc="B. Réglage des imprimantes",
        titre="Une seule imprimante « Autre » par caisse",
        role="Intégrateur (compte admin)",
        prerequis="ST-08 OK.",
        donnees="Imprimante « Bar ».",
        etapes=[
            ("Ouvrez l'imprimante « Bar », cochez « Prend tout ce qu'aucune autre imprimante ne prend », "
             "« Enregistrer ».",
             "Une fenêtre « Oh mince ! » : « La caisse « Restaurant » ne peut avoir qu'une seule imprimante "
             "« Autre » (case « Prend tout ce qu'aucune autre imprimante ne prend ») ; elle en a 2 : Bar, Autre. "
             "Décochez la case sur l'une d'elles, ou retirez-la de la caisse. »"),
            ("Dans la fenêtre, touchez « Rester sur la page », puis la croix ✖ à droite du nuage (Ignorer).",
             "« Bar » garde sa case décochée. (La fenêtre n'a pas de croix « fermer » : ses boutons sont « Rester "
             "sur la page » et « Ignorer les changements ».)"),
        ],
        attendu="La seconde « Autre » est refusée par un message qui nomme les deux imprimantes.",
        recette="R110", verifie=JOUE,
    ),
    dict(
        id="ST-10", f="F3", version="18.0.1.0.13", bloc="B. Réglage des imprimantes",
        titre="Nombre d'exemplaires du bon : refus hors de 1 à 5, puis 3 exemplaires",
        role="Intégrateur (compte admin)",
        prerequis="ST-06 OK.",
        donnees="Imprimante « Chaud » ; valeurs 6, 0, puis 3.",
        etapes=[
            ("Ouvrez « Chaud ». « Nombre d'exemplaires du bon » = 6, « Enregistrer ».",
             "Fenêtre « Oh mince ! » : « Le nombre d'exemplaires du bon doit être entre 1 et 5 "
             "(imprimante « Chaud »). » Ses boutons : « Rester sur la page » et « Ignorer les changements »."),
            ("Touchez « Rester sur la page ». Mettez 0, « Enregistrer ».",
             "Le même message."),
            ("Touchez « Rester sur la page ». Mettez 3.",
             "La phrase dit : « Chaque nouveau bon envoyé à cette imprimante sort en 3 exemplaires identiques, "
             "marqués « Exemplaire 1/3 » à « Exemplaire 3/3 ». Les annulations et les notes seules sortent en un "
             "exemplaire. »"),
            ("« Enregistrer ». Revenez à la liste des imprimantes.",
             "Colonne « Exemplaires » : 3 pour Chaud, 1 pour les autres."),
            (REOUVRIR + ".",
             "La caisse se recharge (elle lit les imprimantes à son ouverture)."),
        ],
        attendu="0 et 6 sont refusés ; 3 est accepté avec sa phrase. "
                "Après le test, gardez le nombre choisi par le gérant (3 dans la suite).",
        recette="R107", verifie=JOUE,
    ),
    # ================================================================ C
    # Envoi en cuisine et au bar (serveur)
    dict(
        id="ST-11", f="F5", version="18.0.1.0.14", bloc="C. Envoi en cuisine et au bar",
        titre="Un seul « J'envoie » : chaque plat sort sur son poste (Epson en direct)",
        role="Serveur 1",
        prerequis="ST-05 à ST-10 OK, caisse rechargée. Les 5 imprimantes sont allumées, avec du papier.",
        donnees="Table 5 (ou toute table libre), 2 personnes. Poulet DG (accompagnement « Riz nature ») 5 000, "
                "Penne arrabiata 3 000, Pizza Marguerite Petit 5 000, Crêpe nature 2 000, "
                "Tour de Cantelou blanc 10 000, Bougie d'anniversaire 500 → total 25 500 FCFA.",
        etapes=[
            ("Sur le plan, touchez la table 5, tapez le code du serveur, touchez « 2 ».",
             "L'écran de commande de la table 5."),
            ("Touchez Poulet DG.",
             "La fenêtre « Sélection d'attributs » s'ouvre : « Accompagnement » Riz nature, Riz Messager, Frites "
             "plantain, Frites pomme. Gardez « Riz nature », touchez « Ajouter »."),
            ("Ajoutez Penne arrabiata, Pizza Marguerite Petit, Crêpe nature, Tour de Cantelou blanc, "
             "Bougie d'anniversaire (cherchez-la par la loupe, en haut).",
             "6 lignes ; total : 25 500 FCFA."),
            ("Touchez « J'envoie ».",
             "Aucune fenêtre, aucun aperçu d'impression. Retour au plan. Notification : « Envoyé : Sans famille × 1, "
             "Poulet DG × 1, Pizzas × 1, Pastas × 1, Crêpes & glaces × 1, Vins blancs × 1. »"),
            ("Allez voir chaque imprimante.",
             "Chaud : 3 bons identiques (Poulet DG et Penne). Pizza : 1 bon (Pizza Marguerite Petit). "
             "Froid : 1 bon (Crêpe nature). Bar : 1 bon (Tour de Cantelou blanc — un vin blanc, sous-famille de Bar). "
             "Autre : 1 bon (Bougie d'anniversaire)."),
        ],
        attendu="7 feuilles en tout, chacune sur le bon poste, sans geste de plus que « J'envoie ».",
        recette="R110 (étape 4), R107", verifie=JOUE + " (Epson simulées au niveau du réseau : la caisse a "
                "réellement envoyé 7 requêtes ePOS aux adresses .51 ×3, .52, .53, .54, .55.)",
    ),
    dict(
        id="ST-12", f="F3", version="18.0.1.0.13", bloc="C. Envoi en cuisine et au bar",
        titre="Le bon est en français et numéroté « Exemplaire k/N »",
        role="Serveur 1 (lecture des bons)",
        prerequis="ST-11 fait : gardez les bons.",
        donnees="Les 3 bons de « Chaud » et le bon de « Pizza » de ST-11.",
        etapes=[
            ("Prenez les 3 bons de Chaud.",
             "En haut, dans un cadre : « Exemplaire 1/3 », « Exemplaire 2/3 », « Exemplaire 3/3 »."),
            ("Lisez l'en-tête d'un bon.",
             "« Sur place », « Restaurant : <heure> », « Par : <prénom du serveur> » (démo : Brice), "
             "« Table 5 # <numéro> ». Le mot « Table » (jamais « Tableau »)."),
            ("Lisez le corps.",
             "Section « Nouveau » : « 1 Poulet DG », « - Riz nature », « 1 Penne arrabiata »."),
            ("Prenez le bon de Pizza.",
             "Pas de cadre « Exemplaire » (1 seul exemplaire)."),
        ],
        attendu="Un seul bon par imprimante et par envoi, tout en français, numéroté quand N > 1. "
                "(Avant : jusqu'à 4 feuilles « New / Cancelled / Note / Message ». Prévenez la cuisine.)",
        recette="R107", verifie=JOUE,
    ),
    dict(
        id="ST-13", f="F3", version="18.0.1.0.13 / 1.0.14", bloc="C. Envoi en cuisine et au bar",
        titre="Une annulation sort en 1 exemplaire, sur le bon poste",
        role="Serveur 1 + Chef de salle",
        prerequis="ST-11 fait (table 5 envoyée).",
        donnees="Table 5 : annuler la Bougie d'anniversaire, puis le Poulet DG.",
        etapes=[
            ("Touchez la table 5, code du serveur. Touchez la ligne « Bougie d'anniversaire », puis ⌫ deux fois.",
             "La fenêtre d'annulation demande le « Code d'un chef de salle »."),
            ("Le chef de salle tape son code (démo : 3001), puis touche un motif.",
             "Notification : « Annulation faite : 1 Bougie d'anniversaire, par <chef de salle>. Bon d'annulation "
             "envoyé. » Un seul bon sort, sur « Autre » : section « Annulé », « 1 Bougie d'anniversaire »."),
            ("Faites de même avec la ligne « Poulet DG ».",
             "Un seul bon sur « Chaud » (pas 3), sans cadre « Exemplaire » : « Annulé », « 1 Poulet DG - Riz nature »."),
            ("Lisez le total.",
             "20 000 FCFA."),
        ],
        attendu="Les annulations sortent en un exemplaire, sur l'imprimante qui avait reçu le plat (même « Autre »).",
        recette="R107, R110", verifie=JOUE,
    ),
    dict(
        id="ST-14", f="F3", version="18.0.1.0.13", bloc="C. Envoi en cuisine et au bar",
        titre="Une imprimante en panne : une seule alerte, la commande est gardée",
        role="Serveur 1",
        prerequis="ST-13 fait. Prévenez le poste pizza.",
        donnees="Table 5 : ajouter 1 Pizza Marguerite Petit (5 000). Débranchez l'imprimante « Pizza » (ou son câble réseau).",
        etapes=[
            ("Débranchez l'imprimante Pizza. Touchez la table 5, code du serveur, ajoutez Pizza Marguerite Petit, "
             "« J'envoie ».",
             "Après quelques secondes, UNE fenêtre « Bon non imprimé » : « L'imprimante « Pizza » n'a pas répondu : "
             "le bon n'est pas sorti. La commande est enregistrée comme envoyée : prévenez le poste de vive voix, "
             "puis vérifiez que l'imprimante est allumée et reliée au réseau. »"),
            ("Touchez le bouton de la fenêtre (« Ok »).",
             "Retour au plan. Notification : « Envoyé : Pizzas × 1, mais le bon « Pizza » n'est pas sorti : "
             "prévenez de vive voix. »"),
            ("Rebranchez l'imprimante. Rouvrez la table 5.",
             "La ligne Pizza Marguerite Petit est à 2 et « J'envoie » est grisé : la pizza est comptée comme "
             "partie. Il n'y a pas de bouton « Réimprimer » : le poste est prévenu de vive voix."),
        ],
        attendu="Une seule alerte, qui nomme l'imprimante ; la pizza est enregistrée ; le serveur sait qu'il "
                "doit prévenir de vive voix.",
        recette="R107", verifie=JOUE + " (panne simulée : connexion refusée à l'adresse de Pizza.)",
    ),
    dict(
        id="ST-15", f="F6", version="18.0.1.0.14", bloc="C. Envoi en cuisine et au bar",
        titre="Odoo en https : accepter le certificat de chaque Epson",
        role="Intégrateur, sur chaque tablette",
        prerequis="Seulement si l'adresse d'Odoo commence par https:// (sinon : cochez S.O.). "
                  "SSL/TLS et ePOS-Print activés dans la page de réglage de chaque Epson (voir le guide).",
        donnees="Les 5 adresses IP des imprimantes.",
        etapes=[
            ("Sur une tablette qui n'a jamais imprimé : ouvrez une table, ajoutez un Café expresso, « J'envoie ».",
             "Si le certificat n'est pas encore accepté : la fenêtre « Bon non imprimé » se termine par "
             "« Odoo est ouvert en https : si c'est la première fois sur cette tablette, ouvrez une fois "
             "https://<IP> dans le navigateur et acceptez le certificat de l'imprimante, puis revenez à la caisse. »"),
            ("Dans un nouvel onglet, ouvrez https://<IP de l'imprimante> → « Paramètres avancés » → « Continuer ».",
             "La page de l'imprimante Epson s'affiche."),
            ("Faites de même pour les 5 adresses, revenez à la caisse, rechargez la page, renvoyez un produit.",
             "Le bon sort, sans fenêtre."),
        ],
        attendu="Après acceptation des 5 certificats, chaque tablette imprime en https sans alerte.",
        recette="R110 (étape 4)",
        verifie="Non joué : il faut une vraie Epson et un Odoo servi en https. Le texte de l'alerte est celui du "
                "code (messages.js).",
    ),
    # ================================================================ D
    # Notes de commande (serveur)
    dict(
        id="ST-16", f="F4", version="18.0.1.0.13", bloc="D. Notes de commande",
        titre="Note cuisine sur un plat dont une partie est déjà partie",
        role="Serveur 1",
        prerequis="ST-10 fait (Chaud en 3 exemplaires).",
        donnees="Table 6, 4 personnes : 3 Poulet DG (Riz nature) envoyés, puis un 4e avec la note « bien cuit ».",
        etapes=[
            ("Table 6, code du serveur, « 4 ». Ajoutez 3 fois Poulet DG (Riz nature), « J'envoie ».",
             "« Envoyé : Poulet DG × 3. »"),
            ("Rouvrez la table 6. Ajoutez 1 Poulet DG (Riz nature).",
             "La ligne passe à 4 ; total 20 000 FCFA."),
            ("La ligne Poulet DG choisie, touchez « Note cuisine », tapez « bien cuit », « Appliquer ».",
             "La fenêtre s'appelait « Ajouter Note cuisine » ; ses boutons de modèles (Wait, To Serve… en anglais, "
             "sauf si le guide 4.6 a été fait) ne servent pas ici. Pas de fenêtre des accompagnements. Deux lignes : "
             "Poulet DG × 3 (sans note) et Poulet DG × 1 « bien cuit ». Total toujours 20 000 FCFA."),
            ("« J'envoie ».",
             "« Envoyé : Poulet DG × 1. » Sur Chaud, 3 exemplaires : « Nouveau », « 1 Poulet DG », "
             "« - Riz nature », « bien cuit »."),
        ],
        attendu="La note va au seul 4e poulet ; la quantité et le total ne changent pas.",
        recette="R108", verifie=JOUE,
    ),
    dict(
        id="ST-17", f="F4", version="18.0.1.0.13", bloc="D. Notes de commande",
        titre="« Ignorer » ne change rien ; effacer une note la retire du poste",
        role="Serveur 2",
        prerequis="Aucun.",
        donnees="Table 8, 2 personnes : Bière blonde 65 cl (1 500) avec la note « sans glaçon ».",
        etapes=[
            ("Table 8, code du serveur 2 (démo : 1002), « 2 ». Ajoutez Bière blonde 65 cl, « Note cuisine », "
             "« sans glaçon », « Appliquer », « J'envoie ».",
             "Bar : « Nouveau », « 1 Bière blonde 65 cl », « sans glaçon »."),
            ("Rouvrez la table 8, touchez la ligne, « Note cuisine ». Remplacez par « avec glaçon », puis « Ignorer ».",
             "La fenêtre s'ouvrait avec « sans glaçon ». Après « Ignorer » : toujours une seule ligne, note « sans glaçon »."),
            ("« Note cuisine » de nouveau : videz le champ, « Appliquer ». « J'envoie ».",
             "« Envoyé : Note × 1. » Bar : section « Note », « 1 Bière blonde 65 cl », « Note retirée : sans glaçon »."),
        ],
        attendu="« Ignorer » (ou la croix) n'efface rien ; vider puis « Appliquer » prévient le bar.",
        recette="R108", verifie=JOUE,
    ),
    dict(
        id="ST-18", f="F4", version="18.0.1.0.13", bloc="D. Notes de commande",
        titre="Note au client sur un plat déjà parti",
        role="Serveur 1",
        prerequis="ST-16 fait (table 6).",
        donnees="Table 6 : note au client « Anniversaire de Paul » sur la ligne Poulet DG × 3.",
        etapes=[
            ("Rouvrez la table 6, touchez la ligne Poulet DG × 3, puis « Actions » → « Note au client ».",
             "La fenêtre « Ajouter Note au client » s'ouvre (avant, la caisse plantait)."),
            ("Tapez « Anniversaire de Paul », « Appliquer ».",
             "La ligne reste à 3 (elle n'est pas coupée) et porte la note. Aucun bon ne sort : la note au client "
             "ne va pas en cuisine."),
        ],
        attendu="La note au client s'enregistre sur un plat parti, sans couper la ligne.",
        recette="R108", verifie=JOUE,
    ),
    dict(
        id="ST-19", f="F4", version="18.0.1.0.13", bloc="D. Notes de commande",
        titre="Note générale tapée seule : elle part, en 1 exemplaire, au bon poste",
        role="Serveur 1",
        prerequis="ST-18 fait (table 6 ouverte).",
        donnees="Table 6 : note générale « Servir le dessert à 21 h ».",
        etapes=[
            ("Sur la table 6 : « Actions » → « Note générale », tapez « Servir le dessert à 21 h », « Appliquer ».",
             "La fenêtre s'appelait « Ajouter Note générale »."),
            ("« J'envoie ».",
             "Notification : « Envoyé : Note générale × 1. » (plus « Message »)."),
            ("Regardez les imprimantes.",
             "Un seul bon, sur Chaud (le poste qui a servi la table), en 1 exemplaire : section « Note générale », "
             "« Servir le dessert à 21 h ». Rien sur Pizza, Froid, Bar, Autre."),
        ],
        attendu="La note générale seule est imprimée, une fois, sur les postes qui ont servi la table.",
        recette="R109", verifie=JOUE,
    ),
    dict(
        id="ST-20", f="F4", version="18.0.1.0.13", bloc="D. Notes de commande",
        titre="L'addition montre la note au client, jamais la note générale",
        role="Serveur 1",
        prerequis="ST-19 fait (table 6).",
        donnees="Table 6 : 4 Poulet DG = 20 000 FCFA.",
        etapes=[
            ("Rouvrez la table 6, touchez « Addition ».",
             "Avec une imprimante de tickets : le ticket sort. Sans : la fenêtre « Impression de l'addition » "
             "montre le ticket et un bouton « Imprimer »."),
            ("Lisez l'addition.",
             "Rubrique PLATS ; « Anniversaire de Paul » sous la ligne Poulet DG × 3 ; « Servir le dessert à 21 h » "
             "n'apparaît nulle part ; « Sous-total Plats : 20 000 FCFA » ; « TOTAL 20 000 FCFA » ; la mention "
             "« PRO FORMA » (addition non payée)."),
            ("S'il y a un écran tourné vers le client : regardez-le.",
             "Même règle : la note au client y est, la note générale non (si pas d'écran client : notez « pas d'écran »)."),
        ],
        attendu="La note générale reste interne (cuisine et bar) ; la note au client est imprimée pour le client.",
        recette="R109", verifie=JOUE + " (sans imprimante de tickets ; l'écran client n'a pas été essayé.)",
    ),
    # ================================================================ E
    # Addition (serveur, caissière)
    dict(
        id="ST-21", f="F7", version="18.0.1.0.14", bloc="E. Addition",
        titre="Addition groupée par famille, avec sous-totaux",
        role="Serveur 1",
        prerequis="ST-02 : case « Grouper les produits par famille… » cochée. ST-05 fait.",
        donnees="Table 9, 4 personnes : Poulet DG 5 000, Ndolé viande 3 000, Pizza Marguerite Petit 5 000, "
                "Crêpe nature 2 000, 2 × Bière blonde 65 cl 3 000, Bougie d'anniversaire 500 → 18 500 FCFA.",
        etapes=[
            ("Table 9, code du serveur, « 4 ». Ajoutez les produits (Riz nature pour les plats à accompagnement), "
             "« J'envoie ».",
             "Total 18 500 FCFA."),
            ("Rouvrez la table 9, touchez « Addition ».",
             "Le ticket (ou la fenêtre « Impression de l'addition »)."),
            ("Lisez l'addition de haut en bas.",
             "PLATS : Poulet DG, Ndolé viande, « Sous-total Plats : 8 000 FCFA » ; PIZZAS & BURGERS : Pizza "
             "Marguerite Petit, Crêpe nature, « Sous-total Pizzas & burgers : 7 000 FCFA » ; BAR : Bière blonde "
             "65 cl × 2, « Sous-total Bar : 3 000 FCFA » ; AUTRES : Bougie d'anniversaire, « Sous-total Autres : "
             "500 FCFA » ; « TOTAL 18 500 FCFA »."),
            ("Vérifiez : 8 000 + 7 000 + 3 000 + 500.",
             "= 18 500 FCFA, le TOTAL."),
        ],
        attendu="Les produits sont rangés par famille de 1er niveau (la crêpe est sous PIZZAS & BURGERS), "
                "chaque famille a son sous-total, le total ne change pas.",
        recette="R111, R112", verifie=JOUE + " (avec une imprimante de tickets simulée.)",
    ),
    dict(
        id="ST-22", f="F7", version="18.0.1.0.14", bloc="E. Addition",
        titre="Réglage décoché : l'addition redevient celle d'Odoo",
        role="Intégrateur + Serveur 1",
        prerequis="ST-21 fait (table 9 ouverte).",
        donnees="Table 9.",
        etapes=[
            (PARAMETRES + " : décochez « Grouper les produits par famille sur l'addition et le ticket », "
             "« Enregistrer ». " + REOUVRIR + ".",
             "La caisse se recharge."),
            ("Table 9, code du serveur, « Addition ».",
             "Plus de titres ni de « Sous-total » : les produits dans l'ordre de la saisie (Poulet DG, Ndolé viande, "
             "Pizza…, Crêpe…, Bière…, Bougie…) ; « TOTAL 18 500 FCFA »."),
            ("Recochez la case (ou laissez-la selon la décision du gérant), « Enregistrer », rechargez la caisse.",
             "Réglage remis comme le gérant le veut."),
        ],
        attendu="Décoché, l'addition est la liste habituelle ; le total est le même.",
        recette="R111", verifie=JOUE,
    ),
    dict(
        id="ST-23", f="F7", version="18.0.1.0.14", bloc="E. Addition",
        titre="Ticket final groupé, et sa réimpression",
        role="Caissière",
        prerequis="ST-22 fait, case recochée et caisse rechargée.",
        donnees="Table 9 (18 500 FCFA), payée en espèces avec 20 000 FCFA.",
        etapes=[
            ("Table 9, code de la caissière (démo : 2001), « J'encaisse ». Touchez « Espèces », tapez 20000 au pavé.",
             "La ligne « Monnaie » affiche -1 500 FCFA (Odoo écrit la monnaie avec un signe moins) : rendez 1 500 FCFA."),
            ("« Valider ».",
             "Retour au plan. Si « Impression automatique du reçu » est coché (Paramètres) et qu'une imprimante "
             "de tickets est réglée, le ticket sort seul. Sinon, rien ne sort : c'est normal."),
            (REIMPRIMER + ".",
             "Le ticket est groupé comme l'addition (sous-totaux 8 000, 7 000, 3 000, 500), « TOTAL 18 500 FCFA », "
             "« Espèces 20 000 FCFA », « MONNAIE 1 500 FCFA »."),
        ],
        attendu="Le ticket final et sa réimpression sont groupés par famille ; les paiements ne changent pas.",
        recette="R111", verifie=JOUE + " (sans « Impression automatique du reçu » : ticket obtenu par réimpression.)",
    ),
    dict(
        id="ST-24", f="F1", version="18.0.1.0.11", bloc="E. Addition",
        titre="Table divisée : « Addition » montre toutes les additions",
        role="Serveur 2",
        prerequis="Aucun.",
        donnees="Table 7, 4 personnes : Poulet DG 5 000, Pizza Marguerite Petit 5 000, Bière blonde 65 cl 1 500, "
                "Crêpe nature 2 000 → 13 500 FCFA. Parts : la pizza (7B), puis la bière (7C).",
        etapes=[
            ("Table 7, code du serveur 2, « 4 ». Ajoutez les 4 produits, « J'envoie ».",
             "Retour au plan."),
            ("Rouvrez la table 7 : « Actions » → « Diviser l'addition » → touchez Pizza Marguerite Petit → "
             "« Créer l'addition à part ».",
             "La caisse est sur la part « 7B » (en haut : un onglet « 7B »)."),
            ("Retour au plan (« Plan »), rouvrez la table 7, divisez de nouveau : Bière blonde 65 cl.",
             "Une part « 7C »."),
            ("Rouvrez la table 7, touchez « Addition ». Sans imprimante de tickets :",
             "Fenêtre « Les additions de la table 7 », « 3 additions encore ouvertes, une par ticket. » : "
             "« Table 7 » 7 000 FCFA, « Table 7B » 5 000 FCFA, « Table 7C » 1 500 FCFA, chacune avec son ticket ; "
             "« Total des additions 13 500 FCFA » ; bouton « J'imprime les additions »."),
            ("Touchez « J'imprime les additions » (avec une imprimante de tickets : touchez « Addition »).",
             "Sans imprimante : l'impression du navigateur, un ticket par page. Avec : 3 tickets d'un seul geste."),
        ],
        attendu="Toutes les additions encore ouvertes de la table sont montrées et imprimées ensemble.",
        recette="R105", verifie=JOUE + " (les deux cas : sans imprimante de tickets, et avec une imprimante simulée.)",
    ),
    dict(
        id="ST-25", f="F1", version="18.0.1.0.11", bloc="E. Addition",
        titre="Une part payée n'est plus reprise",
        role="Caissière + Serveur 2",
        prerequis="ST-24 fait.",
        donnees="La part 7B (5 000 FCFA), payée en espèces.",
        etapes=[
            ("En haut, touchez l'onglet « 7B » (code si demandé), « J'encaisse », code de la caissière, "
             "« Espèces », « Valider ».",
             "Retour au plan."),
            ("Rouvrez la table 7, « Addition ».",
             "« 2 additions encore ouvertes, une par ticket. » : « Table 7 » 7 000 FCFA, « Table 7C » 1 500 FCFA ; "
             "« Total des additions 8 500 FCFA ». 7B n'y est plus."),
            ("Fermez la fenêtre (croix). Encaissez 7 et 7C (ou annulez-les avec un motif) pour libérer la table.",
             "La table 7 redevient grise."),
        ],
        attendu="Seules les additions encore ouvertes sont montrées.",
        recette="R105", verifie=JOUE,
    ),
    # ================================================================ F
    # Paiement à parts égales (caissière)
    dict(
        id="ST-26", f="F2", version="18.0.1.0.12", bloc="F. Paiement à parts égales",
        titre="100 000 FCFA à 3 personnes : 33 333, 33 333, 33 334",
        role="Serveur 1 + Caissière",
        prerequis="Aucun.",
        donnees="Table 3, 3 personnes : 5 × Tea Time 2 pers avec Moscato (20 000) = 100 000 FCFA. "
                "Paiements : Espèces, Mobile Money, Espèces.",
        etapes=[
            ("Table 3, code du serveur, « 3 ». Ajoutez 5 Tea Time 2 pers avec Moscato, « J'envoie ».",
             "Total 100 000 FCFA."),
            ("Rouvrez la table 3 avec le code de la caissière, « J'encaisse ».",
             "Sous « Client » et « Facture », le bouton « Partager à parts égales » (icône camembert)."),
            ("Touchez « Partager à parts égales ».",
             "Fenêtre « Combien de personnes paient ? » : boutons 2 à 8 et « Plus » ; 3 est déjà choisi ; "
             "« Chaque personne paiera 33 333 FCFA ; le dernier paie ce qui reste. » ; « Valider », « Retour »."),
            ("« Valider ».",
             "Bandeau « Part 1 sur 3 : 33 333 FCFA » et bouton « Annuler le partage »."),
            ("Touchez « Espèces ».",
             "Ligne Espèces 33 333 FCFA ; bandeau « Part 2 sur 3 : 33 333 FCFA »."),
            ("Touchez « Mobile Money ».",
             "Ligne Mobile Money 33 333 FCFA ; bandeau « Part 3 sur 3 : 33 334 FCFA »."),
            ("Touchez « Espèces ».",
             "Ligne Espèces 33 334 FCFA ; bandeau « Les 3 parts sont encaissées. Validez le paiement. » ; "
             "« Annuler le partage » a disparu."),
            ("« Valider ». Puis : " + REIMPRIMER + ".",
             "Retour au plan. Le ticket montre les 3 paiements et, dessous, « Partagée en 3 parts égales »."),
        ],
        attendu="33 333 + 33 333 + 33 334 = 100 000 FCFA ; une seule vente ; mention sur le ticket.",
        recette="R106", verifie=JOUE,
    ),
    dict(
        id="ST-27", f="F2", version="18.0.1.0.12", bloc="F. Paiement à parts égales",
        titre="Monnaie à rendre sur une part payée en espèces",
        role="Serveur 1 + Caissière",
        prerequis="Aucun.",
        donnees="Table 4, 3 personnes, 100 000 FCFA (5 Tea Time 2 pers avec Moscato). La 1re personne donne "
                "50 000 FCFA en espèces.",
        etapes=[
            ("Préparez la table 4 comme ST-26 (envoi), « J'encaisse » (caissière), « Partager à parts égales », "
             "3, « Valider ».",
             "« Part 1 sur 3 : 33 333 FCFA »."),
            ("Touchez « Espèces », puis tapez 50000 au pavé.",
             "Le bandeau ajoute « Monnaie à rendre : 16 667 FCFA ». Rendez 16 667 FCFA."),
            ("Touchez « Mobile Money ».",
             "La ligne Espèces revient à 33 333 FCFA ; Mobile Money 33 333 FCFA ; « Part 3 sur 3 : 33 334 FCFA »."),
            ("Touchez « Espèces », « Valider ».",
             "Retour au plan. Ticket (réimpression) : « Partagée en 3 parts égales »."),
        ],
        attendu="La monnaie d'une part est annoncée ; la caisse n'enregistre que la part (33 333).",
        recette="R106", verifie=JOUE,
    ),
    dict(
        id="ST-28", f="F2", version="18.0.1.0.12", bloc="F. Paiement à parts égales",
        titre="Supprimer une ligne, puis « Annuler le partage »",
        role="Serveur 1 + Caissière",
        prerequis="Aucun.",
        donnees="Table 10, 3 personnes, 100 000 FCFA.",
        etapes=[
            ("Préparez la table 10 comme ST-26, partagez en 3. Touchez « Espèces » puis « Mobile Money ».",
             "Lignes 33 333 et 33 333 ; « Part 3 sur 3 : 33 334 FCFA »."),
            ("Supprimez la ligne Mobile Money (croix rouge au bout de la ligne).",
             "Le bandeau recule : « Part 2 sur 3 : 33 333 FCFA »."),
            ("Touchez « Annuler le partage ».",
             "Le bandeau disparaît ; le bouton « Partager à parts égales » revient."),
            ("Touchez « Mobile Money ».",
             "La ligne prend tout le reste : 66 667 FCFA."),
            ("« Valider », puis réimprimez le ticket.",
             "Espèces 33 333 FCFA, Mobile Money 66 667 FCFA, « TOTAL 100 000 FCFA », sans « Partagée en … »."),
        ],
        attendu="Le compteur suit les lignes ; « Annuler le partage » rend le paiement habituel.",
        recette="R106", verifie=JOUE,
    ),
    dict(
        id="ST-29", f="F2", version="18.0.1.0.12", bloc="F. Paiement à parts égales",
        titre="Partager ce qui reste après un premier paiement",
        role="Serveur 1 + Caissière",
        prerequis="Aucun.",
        donnees="Table 11, 3 personnes, 100 000 FCFA. Un premier paiement de 10 000 FCFA en espèces, "
                "puis 90 000 à partager en 3.",
        etapes=[
            ("Préparez la table 11 comme ST-26, « J'encaisse ». Touchez « Espèces », tapez 10000.",
             "Ligne Espèces 10 000 FCFA."),
            ("« Partager à parts égales ».",
             "La fenêtre dit « Reste dû partagé : 90 000 FCFA. » et « Chaque personne paiera 30 000 FCFA ; le dernier "
             "paie ce qui reste. » (3 choisi)."),
            ("« Valider ».",
             "Bandeau « Part 1 sur 3 : 30 000 FCFA » et « Reste dû partagé : 90 000 FCFA. »"),
            ("Touchez « Mobile Money », « Mobile Money », « Espèces », puis « Valider ».",
             "Lignes 10 000 / 30 000 / 30 000 / 30 000. Ticket : « Partagée en 3 parts égales »."),
        ],
        attendu="C'est le reste dû qui est partagé.",
        recette="R106", verifie=JOUE,
    ),
    dict(
        id="ST-30", f="F2", version="18.0.1.0.12", bloc="F. Paiement à parts égales",
        titre="Retour à la commande : le partage est gardé, sauf si le total change",
        role="Serveur 1 + Caissière",
        prerequis="Aucun.",
        donnees="Table 12, 3 personnes, 100 000 FCFA ; ajout d'une Eau minérale 0,5 L (500).",
        etapes=[
            ("Préparez la table 12 comme ST-26, partagez en 3, touchez « Espèces ».",
             "« Part 2 sur 3 : 33 333 FCFA »."),
            ("Touchez « Retour » (en bas de l'écran de paiement), puis « J'encaisse » (code de la caissière si demandé).",
             "Le bandeau est retrouvé : « Part 2 sur 3 : 33 333 FCFA »."),
            ("« Retour », ajoutez Eau minérale 0,5 L, « J'encaisse ».",
             "Total 100 500 FCFA ; plus de bandeau ; le bouton « Partager à parts égales » est revenu."),
            ("Touchez « Espèces », « Valider ».",
             "La ligne Espèces prend le reste : 67 167 FCFA."),
        ],
        attendu="Le partage survit à un aller-retour ; un produit ajouté l'efface (on le refait d'un toucher).",
        recette="R106", verifie=JOUE,
    ),
    dict(
        id="ST-31", f="F2", version="18.0.1.0.12", bloc="F. Paiement à parts égales",
        titre="Avec l'arrondi des espèces : parts multiples du pas",
        role="Serveur 1 + Caissière",
        prerequis="Seulement si « Arrondi des paiements en espèces » est coché dans les Paramètres de la caisse "
                  "(sinon cochez S.O.). Exemple écrit pour un pas de 25 FCFA (« Moitié supérieure »).",
        donnees="Table 2, 6 personnes : Pizza Marguerite Grand 10 000 FCFA ; 6 parts en espèces.",
        etapes=[
            ("Table 2, code du serveur, « 6 », Pizza Marguerite Grand, « J'envoie ». Caissière : « J'encaisse », "
             "« Partager à parts égales ».",
             "6 est choisi ; « Chaque personne paiera entre 1 650 FCFA et 1 675 FCFA ; le dernier paie ce qui reste. »"),
            ("« Valider », puis touchez 6 fois « Espèces ».",
             "Lignes 1 650, 1 650, 1 675, 1 675, 1 675, 1 675 (total 10 000)."),
            ("« Valider », réimprimez.",
             "« Partagée en 6 parts égales »."),
        ],
        attendu="Avec un autre pas, chaque part (sauf la dernière) est un multiple du pas et deux parts diffèrent "
                "d'un pas au plus.",
        recette="R106", verifie=JOUE + " (arrondi de 25 FCFA activé pour le test, puis retiré.)",
    ),
    dict(
        id="ST-32", f="F2", version="18.0.1.0.12", bloc="F. Paiement à parts égales",
        titre="Dernière part mise sur ardoise par le manager",
        role="Caissière + Manager",
        prerequis="Le mode « Ardoise client » est sur la caisse. Un client de test (ex. « Client ardoise test ») "
                  "existe dans Contacts.",
        donnees="Table 3 (libérée par ST-26), 3 personnes, 100 000 FCFA : Espèces, Mobile Money, puis ardoise 33 334.",
        etapes=[
            ("Préparez la table 3 comme ST-26, partagez en 3, touchez « Espèces » puis « Mobile Money ».",
             "« Part 3 sur 3 : 33 334 FCFA ». La caissière ne voit pas « Mettre sur ardoise »."),
            ("Touchez le nom en haut à droite : le manager tape son code (démo : 4001).",
             "Fenêtre « Qui prend la main ? Tapez votre code ». Puis le bouton « Mettre sur ardoise » apparaît ; "
             "le bandeau reste « Part 3 sur 3 : 33 334 FCFA »."),
            ("Touchez « Client », choisissez le client, puis « Mettre sur ardoise ».",
             "Le paiement est validé, retour au plan ; le « Bon d'ardoise » sort : « Montant dû 33 334 FCFA », "
             "« Je reconnais devoir la somme ci-dessus. »"),
            (REIMPRIMER + " (code du manager).",
             "« Ardoise client 33 334 FCFA » et « Partagée en 3 parts égales »."),
        ],
        attendu="L'ardoise compte comme la dernière part ; la mention reste sur le ticket.",
        recette="R106", verifie=JOUE,
    ),
    # ================================================================ G
    dict(
        id="ST-33", f="NR", version="18.0.1.0.14", bloc="G. Non-régression",
        titre="Envoyer et encaisser une table simple",
        role="Serveur 1 + Caissière",
        prerequis="Toute table libre.",
        donnees="Table 4, 2 personnes : 2 Café expresso (1 000) = 2 000 FCFA, payés en espèces.",
        etapes=[
            ("Table 4, code du serveur, « 2 », 2 Café expresso, « J'envoie ».",
             "« Envoyé : Café & thé × 2. » ; un bon au Bar « Nouveau », « 2 Café expresso »."),
            ("Table 4, code de la caissière, « J'encaisse », « Espèces ».",
             "Ligne Espèces 2 000 FCFA."),
            ("« Valider ».",
             "Retour au plan ; la table 4 est libre (grise)."),
        ],
        attendu="Le service habituel marche comme avant.",
        recette="—", verifie=JOUE,
    ),
]
