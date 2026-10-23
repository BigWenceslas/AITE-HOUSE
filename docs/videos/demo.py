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
