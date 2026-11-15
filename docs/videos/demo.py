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
# son parent (point_of_sale/models/pos_category.py:71-79).
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
