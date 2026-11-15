# -*- coding: utf-8 -*-
"""Les données de démonstration de la vidéo AITE HOUSE.

Une seule source, pour que les mêmes séjours traversent toute la vidéo : la
réception accueille un client, la gouvernante prépare sa chambre, le bar
pose une consommation sur sa note, la direction retrouve les chiffres.

Toutes les personnes sont **fictives**. Les jeux d'essai de recette (base
de démonstration, base LAVERANDAH) portent des noms qu'on ne montre pas :
ils n'apparaissent jamais à l'écran. L'établissement reprend le nom de
démonstration du module ``aite_demo_data`` (« Complexe Hôtelier — Démo »),
qui ne désigne aucun hôtel réel.
"""

HOTEL = 'Complexe Hôtelier — Démo'
SOCIETE = 'Démo Hôtellerie SARL'
VILLE = 'Douala'
ETOILES = '3 ★'
TEL_HOTEL = '+237 6 00 00 00 10'      # plage de fiction, comme tous les numéros de la série

# Les postes, un collaborateur fictif par poste (nom, rôle, initiale de l'avatar).
POSTES = {
    'reception': ('Mireille Ateba', 'Réceptionniste'),
    'gouvernante': ('Josiane Fouda', 'Gouvernante'),
    'caisse': ('Hervé Tchakounté', 'Caissier du bar'),
    'client': ('Claire Durand', 'Cliente, sur le site web'),
    'magasin': ('Serge Nana', 'Magasinier'),
    'direction': ('Danielle Eyenga', 'Directrice'),
    'conformite': ('Danielle Eyenga', 'Directrice'),
}
EQUIPIERES = ('Clarisse', 'Sidonie')

# Les séjours qui traversent la vidéo.
RESA = 'RES/2026/0214'
FOLIO = 'FOL/2026/0214'
CLIENT = 'Estelle Ngono'
CLIENT_TEL = '+237 6 00 00 00 01'
CLIENT_MAIL = 'estelle.ngono@exemple.cm'
ARRIVEE = '14/10/2026 14:00:00'
DEPART = '16/10/2026 12:00:00'
CHAMBRE = '204 [CFT]'
TYPE = 'Confort'
PRIX_NUIT = '45 000 FCFA'
TOTAL_HEB = '90 000 FCFA'

# Les réservations de créneaux (espaces et prestations) qui reviennent d'une
# vidéo à l'autre. Depuis la livraison 4, leur référence a son propre préfixe
# et l'année sur quatre chiffres, comme les séjours (« CRN/2026/0131 » et non
# plus « RES/26/0131 ») : aite_slot_booking/data/slot_sequence_data.xml,
# préfixe « CRN/%(range_year)s/ », 4 chiffres, numérotation annuelle (écart
# n° 61). Les séjours gardent « RES/2026/… ».
CRENEAU_SALON = 'CRN/2026/0131'      # Claire Durand, salon VIP Wouri, samedi 17/10/2026 16:00
CRENEAU_MASSAGE = 'CRN/2026/0158'    # Brigitte Essomba, massage du 15/10, reporté sur FOL/2026/0210
CRENEAU_PRESSING = 'CRN/2026/0141'   # Samuel Etoga, pressing

ARRIVEES = [
    # (référence, client, arrivée, départ, nuits, chambres, total hébergement HT, solde du folio)
    # Solde d'Estelle après l'acompte de 45 000 : folio 102 000 (2 × 45 000 + taxe de séjour 12 000) − 45 000.
    ('RES/2026/0214', 'Estelle Ngono', '14/10/2026 14:00:00', '16/10/2026 12:00:00', '2', '1', '90 000 FCFA', '57 000 FCFA'),
    ('RES/2026/0209', 'Martin Ebode', '14/10/2026 14:00:00', '17/10/2026 12:00:00', '3', '1', '105 000 FCFA', '35 000 FCFA'),
    ('RES/2026/0201', 'Claire Durand', '14/10/2026 18:00:00', '15/10/2026 12:00:00', '1', '1', '120 000 FCFA', '0 FCFA'),
]

# Les ardoises du bar (référence, client, ouverture, montant, remboursé, reste dû, âge, sévérité, genre).
ARDOISES = [
    ('ARD/0042', 'Patrick Nkoulou', '09/10/2026', '18 500 FCFA', '0 FCFA', '18 500 FCFA', '5', 'Récente', 'vert'),
    ('ARD/0039', 'Brigitte Essomba', '22/09/2026', '42 000 FCFA', '12 000 FCFA', '30 000 FCFA', '22', 'Récente', 'vert'),
    ('ARD/0031', 'Joël Kamga', '05/09/2026', '27 000 FCFA', '0 FCFA', '27 000 FCFA', '39', 'En retard', 'orange'),
    ('ARD/0024', 'Armand Mvogo', '18/08/2026', '64 500 FCFA', '20 000 FCFA', '44 500 FCFA', '57', 'En retard', 'orange'),
    ('ARD/0017', 'Sylvie Mbarga', '02/07/2026', '35 000 FCFA', '5 000 FCFA', '30 000 FCFA', '104', 'Critique', 'rouge'),
]


# =============================================== le restaurant (tutoriels 16 à 23)
# Un restaurant SANS hôtel : aite_pos_restaurant ne dépend pas du socle hôtelier
# (addons/aite_pos_restaurant/__manifest__.py:119, 126) et n'est pas installé chez
# le client pilote de l'hôtel (docs/NOTES_DE_VERSION_restaurant_lot1.md:13-15). Les
# tutoriels 16 à 23 montrent donc un autre établissement, une autre société et une
# autre barre d'applications (ni « Hôtel », ni réservation). Personnes, établissement
# et carte sont fictifs : ni le jeu d'essai (dev/seeds/seed_restaurant.py : prénoms,
# marques de boissons), ni les captures, ni le client du restaurant n'y paraissent ;
# les noms ont été cherchés dans tout le dépôt (aucune occurrence) le 15/11/2026.
RESTO = 'Café-Restaurant — Démo'          # pizza, café, petit déjeuner, bar et cuisine
SOCIETE_RESTO = 'Démo Restauration SARL'
TEL_RESTO = '+237 6 00 00 00 50'          # plage de fiction ; 50-59 réservés au restaurant dans la série
CAISSE_RESTO = 'Restaurant'               # NOM_CAISSE, aite_pos_restaurant/models/pos_config.py:81
SALLE_RESTO = 'Salle'                     # NOM_SALLE, pos_config.py:82
MODES_RESTO = ('Espèces', 'Mobile Money')  # pos_config.py:83-84 (deux modes seulement, Q56)
DELAI_ORANGE = 60                         # regles.DELAI_ALERTE ; pos_config.py:36
JOUR_RESTO = '14/10/2026'                 # le jour de référence de la série (DESIGN.md)
# La marque de fin des tutoriels du restaurant (marketing.scene_cta, clé cta.sous_marque) : un restaurant sans
# hôtel ne reçoit pas une « Suite hôtelière » (moteur.SOUS_MARQUE) ; « Caisse de restaurant » est le résumé du
# module (addons/aite_pos_restaurant/__manifest__.py:4).
SOUS_MARQUE_RESTO = 'Caisse de restaurant sur Odoo 18'

# L'administrateur d'Odoo qui règle la caisse : pas une personne, le rôle d'AITE (les
# réglages du Point de Vente sont réservés à l'administrateur : docs/INSTALLATION.md §9.5).
ADMIN_RESTO = ('AITE Consulting', "administrateur d'Odoo", 'A')

# L'équipe : (nom complet, nom sur la fiche et à la caisse, niveau en caisse, code caisse).
# Prénom seul sur la fiche, comme le jeu d'essai et les captures : la phrase d'état de la
# caisse se coupe par des points de suspension (static/src/scss/restaurant.scss:71-75).
# Niveaux : models/regles.py:23-28. Codes : quatre chiffres « tirés au hasard », comme ceux
# que la fiche propose en production (models/hr_employee.py:69-79), propres à chacun.
EQUIPE_RESTO = [
    ('Edwige Bilongo', 'Edwige', 'Manager', '9150'),
    ('Prisca Tamo', 'Prisca', 'Caissière', '6304'),
    ('Loïc Ewodo', 'Loïc', 'Serveur', '4827'),
    ('Inès Fotabong', 'Inès', 'Serveur', '5913'),
    ('Landry Essola', 'Landry', 'Chef de salle ou superviseur', '7461'),
]
# Les personnages des tutoriels (nom, rôle) et la couleur de leur avatar à la caisse.
POSTES_RESTO = {
    'manager': ('Edwige Bilongo', 'Manager du restaurant'),
    'caisse': ('Prisca Tamo', 'Caissière'),
    'serveur': ('Loïc Ewodo', 'Serveur'),
    'serveuse': ('Inès Fotabong', 'Serveuse'),
    'chef': ('Landry Essola', 'Chef de salle'),
}
AVATARS_RESTO = {'Edwige': '#A0446E', 'Prisca': '#B26A2B', 'Loïc': '#3F7D5A', 'Inès': '#6B5BA8', 'Landry': '#2F6690',
                 'A': '#7C5295'}

# Les familles de la caisse, sur trois niveaux (noms de la recette R29-R33 et de
# docs/INSTALLATION.md §9.6) : (nom, couleur d'Odoo, sous-familles). Couleurs relevées
# sur la base du restaurant (Nourriture 7, Boisson 8) ; une sous-famille prend celle de
# son parent, à la création comme au déplacement (point_of_sale/models/pos_category.py:67-81).
FAMILLES_RESTO = [
    ('Nourriture', 7, [('Pizzas', 0, []), ('Petit déjeuner', 0, []), ('Plats', 0, [])]),
    ('Boisson', 8, [
        ('Alcoolisé', 0, [('Bière', 0, []), ('Vin', 0, []), ('Whisky', 0, [])]),
        ('Non alcoolisé', 0, [('Sodas', 0, []), ('Café', 0, [])]),
    ]),
]

# La carte : (nom, famille, prix de vente, coût, suivi en stock), en FCFA, sans aucune
# marque. Société sans TVA, comme toute la série (DESIGN.md) : pas de ligne « Taxes ».
# Seules les bières sont suivies en stock (« par exemple une bière » : pos_config.py:59-67 ;
# « les seules boissons vendues à l'unité » : INSTALLATION.md §9.6).
CARTE_RESTO = [
    ('Pizza Margherita', 'Pizzas', 5000, 1800, False),
    ('Pizza Reine', 'Pizzas', 6000, 2200, False),
    ('Pizza quatre fromages', 'Pizzas', 7000, 2800, False),
    ('Petit déjeuner complet', 'Petit déjeuner', 3500, 1300, False),
    ('Omelette garnie', 'Petit déjeuner', 2000, 700, False),
    ('Poulet DG', 'Plats', 6000, 2600, False),
    ('Poisson braisé', 'Plats', 7000, 3200, False),
    ('Brochettes de bœuf', 'Plats', 3000, 1300, False),
    ('Bière blonde 65 cl', 'Bière', 1500, 650, True),
    ('Bière brune 65 cl', 'Bière', 1500, 700, True),
    ('Bière blonde 33 cl', 'Bière', 1000, 400, True),
    ('Vin rouge (verre)', 'Vin', 2000, 700, False),
    ('Whisky 12 ans (verre)', 'Whisky', 5000, 1600, False),
    ('Cola 33 cl', 'Sodas', 1000, 300, False),
    ('Jus de bissap 50 cl', 'Sodas', 1000, 400, False),
    ('Eau minérale 50 cl', 'Sodas', 500, 150, False),
    ('Café expresso', 'Café', 1000, 250, False),
    ('Café crème', 'Café', 1500, 400, False),
]

# Les cinq motifs d'annulation posés d'office (addons/aite_pos_restaurant/data/
# restaurant_motif_data.xml:8-28) ; « Autre » demande une précision.
MOTIFS_RESTO = ['Erreur de saisie', 'Client parti', 'Plat refusé', 'Produit manquant', 'Autre']

# Le fond de caisse du 14/10 : les espèces comptées à la fermeture précédente, proposées à l'ouverture
# (tutoriel 17 ; point_of_sale opening_control_popup.js:29-32) ; la fermeture du jour les recompte (t22).
FOND_RESTO = 25000

# La journée du 14/10 en salle, telle que la montrent les tutoriels 17 à 20 (relus) : la référence des
# tutoriels qui suivent (t21 encaisse, t22 ferme la caisse, t23 lit les rapports). Une table, une ligne :
# (table, ouverte par, heure d'ouverture, personnes, contenu {article: quantité} quand le tutoriel le
# fixe, ce qui est sûr de la suite, tutoriels). Les heures ne sont jamais à l'écran de la caisse (seules
# les durées) ; elles le sont dans la gestion (journal des annulations, commandes, rapports).
# - midi : t18 montre le plan de 12:50 à 13:00 (4, 6, 7, 10 et 2 ouvertes, les autres libres), t19 celui
#   de 13:30 et de 13:48 (6, 7 et 10 encaissées entre-temps) ;
# - la table 10 du soir (t20) n'est pas celle de midi (t18) : à midi, la 10 est à Loïc de 11:52 à son
#   encaissement, avant 13:30 ; le soir, Inès la rouvre. t21 l'encaisse (20 000 FCFA, 4 personnes) ;
# - les tables 4 et 2 sont encore ouvertes à 13:48 (t19) : un encaissement de la table 4 avant 13:48
#   (storyboards t21 et t22 : 12:41) contredirait t18 et t19 ;
# - t21 encaisse les tables 4 (13:52), 2 (divisée à 14:11) et 10 du soir (19:56). Ce qui leur est ajouté
#   l'après-midi l'est entre 13:00 et 13:30 : à 13:48, la tablette unique a encore la famille Bière choisie
#   (t19), donc rien n'a été saisi d'une autre famille après 13:30 (O pos_store.js:1058-1068 ; ECARTS n° 96).
#   Aucune table ne s'ouvre entre 13:48 et 14:11 en dehors de 2, 4 et 5 ; la 5 est encaissée à 14:05.
TABLES_JOUR_RESTO = [
    (1, 'Loïc', '11:52', None, {}, "un Jus de bissap 50 cl retiré sans code à 11:52 (poste en retard) ; libre à 12:50",
     ('t19',)),
    (7, 'Inès', '11:45', None, {}, 'orange à 12:45 ; encaissée entre 13:00 et 13:30', ('t18', 't19')),
    (10, 'Loïc', '11:52', None, {'Pizza Reine': 2, 'Bière blonde 65 cl': 4}, 'encaissée entre 13:00 et 13:30',
     ('t18', 't19')),
    (4, 'Loïc', '12:15', 6, {'Pizza Margherita': 1, 'Bière blonde 65 cl': 2, 'Cola 33 cl': 2},
     '4 personnes, puis 6 (t17) ; 10 000 FCFA envoyés à la fin de t17 ; encore ouverte à 13:48 (1 h 33) ; '
     'Pizza quatre fromages et 2 Eau minérale 50 cl ajoutées et envoyées entre 13:00 et 13:30 ; 18 000 FCFA, '
     '8 articles ; encaissée en espèces à 13:52 par Prisca (t21)',
     ('t17', 't18', 't19', 't21')),
    (6, 'Inès', '12:28', None, {}, 'encaissée entre 13:00 et 13:30', ('t18', 't19')),
    (2, 'Loïc', '12:55', 2, {'Cola 33 cl': 2}, 'envoyés par Landry à 13:00 (t18) ; encore ouverte à 13:48 ; '
     'Pizza Reine et Pizza quatre fromages ajoutées et envoyées entre 13:00 et 13:30 (15 000 FCFA) ; divisée à '
     '14:11 : part 2B (Pizza Reine, 6 000 FCFA, Mobile Money, 0 personne), puis table 2 (9 000 FCFA, espèces), '
     'encaissées par Prisca (t21)',
     ('t18', 't19', 't21')),
    (5, 'Inès', '13:05', 2, {'Pizza quatre fromages': 1, 'Bière blonde 65 cl': 2},
     "une 4ᵉ bière saisie puis retirée, une bière envoyée annulée à 13:30 : 10 000 FCFA", ('t19',)),
    (9, 'Loïc', '13:28', 2, {}, 'Pizza Margherita et 2 Cola 33 cl (7 000 FCFA) annulés en entier à 13:48 par Landry',
     ('t19',)),
    (10, 'Inès', '19:10', 4, {'Pizza Reine': 1, 'Bière blonde 65 cl': 2, 'Cola 33 cl': 1, 'Pizza quatre fromages': 1,
                              'Bière brune 65 cl': 2},
     "service du soir : 25 min puis 31 min dans t20 ; 20 000 FCFA, encaissée en espèces à 19:56 par Prisca, au "
     "poste d'Inès (t21) ; seule table ouverte le soir jusque-là", ('t20', 't21')),
]

# Le journal des annulations du 14/10 (tutoriel 19, étape 7), dans l'ordre de la liste (« date desc, id
# desc » : aite_pos_restaurant/models/restaurant_annulation.py:37) : (date, table, produit, quantité,
# demandée par, autorisée par, motif, précision). La ligne de 11:52 est arrivée sans code d'un poste en retard.
ANNULATIONS_JOUR_RESTO = [
    ('14/10/2026 13:48', '9', 'Cola 33 cl', 2, 'Landry', 'Landry', 'Client parti', ''),
    ('14/10/2026 13:48', '9', 'Pizza Margherita', 1, 'Landry', 'Landry', 'Client parti', ''),
    ('14/10/2026 13:30', '5', 'Bière blonde 65 cl', 1, 'Inès', 'Landry', 'Autre', 'Bouteille cassée au service'),
    ('14/10/2026 11:52', '1', 'Jus de bissap 50 cl', 1, 'Loïc', '', '', ''),
]

# La session du 14/10 (t22 la ferme, t23 en lit les rapports).
SESSION_RESTO = 'POS/00014'

# Les additions réglées de la session du 14/10, dans l'ordre des paiements : (payée à, table ou part, ouverte par,
# personnes, contenu {article: quantité}, mode, encaissée par). Elles tiennent ensemble ce que montrent t17 à t21
# (TABLES_JOUR_RESTO) et ce qu'affichent t22 (12 commandes, 188 500 FCFA, 121 500 en espèces, 67 000 en Mobile
# Money, 11 tables, 33 personnes) et t23 (les rapports). Une part d'addition divisée (« 2B ») compte 0 table et
# 0 personne (R/models/regles.py, ``compteurs``). Les tables 3 et 8, les dernières du soir, sont encaissées par
# Landry (Prisca partie ; le droit : regles.py, 'encaisser' = caissière, Landry est superviseur) ; jamais montré
# ailleurs que dans t23.
JOURNEE_RESTO = [
    ('12:35', '1', 'Loïc', 3, {'Pizza Reine': 1, 'Pizza Margherita': 2, 'Cola 33 cl': 2, 'Jus de bissap 50 cl': 1},
     'Mobile Money', 'Prisca'),
    ('13:15', '7', 'Inès', 4, {'Pizza Margherita': 2, 'Pizza Reine': 2, 'Bière blonde 65 cl': 4}, 'Mobile Money',
     'Prisca'),
    ('13:20', '10', 'Loïc', 2, {'Pizza Reine': 2, 'Bière blonde 65 cl': 4}, 'Espèces', 'Prisca'),
    ('13:25', '6', 'Inès', 2, {'Pizza quatre fromages': 1, 'Bière blonde 65 cl': 2}, 'Espèces', 'Prisca'),
    ('13:52', '4', 'Loïc', 6, {'Pizza Margherita': 1, 'Bière blonde 65 cl': 2, 'Cola 33 cl': 2, 'Pizza quatre fromages': 1,
                               'Eau minérale 50 cl': 2}, 'Espèces', 'Prisca'),
    ('14:05', '5', 'Inès', 2, {'Pizza quatre fromages': 1, 'Bière blonde 65 cl': 2}, 'Espèces', 'Prisca'),
    ('14:11', '2B', 'Loïc', 0, {'Pizza Reine': 1}, 'Mobile Money', 'Prisca'),
    ('14:12', '2', 'Loïc', 2, {'Cola 33 cl': 2, 'Pizza quatre fromages': 1}, 'Espèces', 'Prisca'),
    ('19:56', '10', 'Inès', 4, {'Pizza Reine': 1, 'Bière blonde 65 cl': 2, 'Cola 33 cl': 1, 'Pizza quatre fromages': 1,
                                'Bière brune 65 cl': 2}, 'Espèces', 'Prisca'),
    ('20:48', '9', 'Loïc', 2, {'Pizza quatre fromages': 1, 'Bière blonde 65 cl': 2, 'Cola 33 cl': 1}, 'Espèces',
     'Prisca'),
    ('21:20', '3', 'Loïc', 4, {'Pizza quatre fromages': 2, 'Pizza Margherita': 1, 'Bière blonde 65 cl': 3,
                               'Cola 33 cl': 2}, 'Espèces', 'Landry'),
    ('21:35', '8', 'Inès', 2, {'Pizza Reine': 2, 'Bière blonde 33 cl': 2}, 'Mobile Money', 'Landry'),
]

# Les deux tables encore ouvertes à 22:30, tout envoyé (t22) : (table, ouverte par, ouverte à, produits).
OUVERTES_FERMETURE_RESTO = [(11, 'Loïc', '21:40', [('Bière blonde 65 cl', 2)]),
                            (12, 'Inès', '21:15', [('Pizza Margherita', 1), ('Cola 33 cl', 1)])]

# Leurs produits, annulés à la fermeture par Landry (t22), au format de ANNULATIONS_JOUR_RESTO ; l'heure (22:31) et
# l'ordre des trois lignes sont posés par la série, aucune source ne les fixe (lu, non vu).
ANNULATIONS_FERMETURE_RESTO = [
    ('14/10/2026 22:31', '12', 'Cola 33 cl', 1, 'Landry', 'Landry', 'Client parti', ''),
    ('14/10/2026 22:31', '12', 'Pizza Margherita', 1, 'Landry', 'Landry', 'Client parti', ''),
    ('14/10/2026 22:31', '11', 'Bière blonde 65 cl', 2, 'Landry', 'Landry', 'Client parti', ''),
]
