# -*- coding: utf-8 -*-
"""AITE HOUSE — la vidéo de présentation de la solution complète.

La trame suit les **fiches de recette** (docs/GUIDE_RECETTE_UAT.md : six
scénarios joués poste par poste, 34 étapes, aucun écart), complétées par le
cahier de recette (recette/cas_de_test.py, domaines N à Q) pour les modules
de la vague 1 : taxe de séjour, registre des clients, gouvernante et
maintenance, indicateurs RevPAR / pickup / pace.

Chaque chapitre vit dans son module (``scenarios/cN_<poste>.py``) : l'écran
rejoué, ses libellés et leurs sources, les gestes et la voix.

Chiffres de la carte « La solution » : 16 modules livrés (``addons/``) ;
874 tests automatisés, recomptés pour la livraison 4 (``def test_`` dans
``addons/*/tests/``, écarts n° 37-77 compris, et le test de l'en-tête
« Écart (FCFA) » d'aite_pos_analytics 18.0.2.1.4 ; 613 avant) ; recette UAT de
6 scénarios et 34 étapes, sans écart (docs/GUIDE_RECETTE_UAT.md) ; cahier de
recette de 146 cas sur 17 domaines (recette/cas_de_test.py).

Le moteur ne lit qu'une feuille de style par vidéo (``SCENARIO['css']``,
moteur.py:671) : elle réunit le CSS propre à chaque chapitre
(``CHAPITRE['css']``, par exemple le « ? » d'aide ``.c1-aide``).
"""

import importlib

CHAPITRES = ['c1_reception', 'c2_gouvernante', 'c3_caisse', 'c4_site_web', 'c5_magasin', 'c6_direction',
             'c7_conformite']


def _chapitres():
    liste = []
    for nom in CHAPITRES:
        try:
            module = importlib.import_module('scenarios.%s' % nom)
        except ModuleNotFoundError as erreur:
            if erreur.name == 'scenarios.%s' % nom:
                continue      # chapitre pas encore écrit
            raise
        importlib.reload(module)
        liste.append(module.CHAPITRE)
    return liste


_CHAPITRES = _chapitres()


SCENARIO = {
    'slug': '01-presentation',
    'profil': 'presentation',
    'titre': 'La suite hôtelière complète',
    'kicker': 'Présentation de la solution',
    'mission': "Réservations, séjours, bar, ménage, ardoises, stock et pilotage : tout l'établissement dans un "
               "seul outil, sur Odoo 18.",
    'poste_kicker': '1 · La solution',
    'poste_titre': "AITE HOUSE en un coup d'œil",
    'cartes': [
        ('Accueillir', "Site web, réception, séjours, folio et facture unique, registre des clients."),
        ('Servir', "Bar et restaurant reliés à la chambre, ardoises clients, fidélité, ménage et maintenance."),
        ('Piloter', "Stock, achats et tableaux de bord de la direction, avec les mêmes chiffres partout."),
    ],
    'poste': [
        ('Pour qui', "Hôtels, résidences et complexes hôteliers, en francs CFA"),
        ('Ce qu\'elle couvre', "16 modules : hébergement, espaces, site web, caisse, crédit, fidélité, stock, achats, direction"),
        ('Où elle tourne', "Odoo 18, édition Community ou Enterprise"),
        ('Comment elle est validée', "Une recette poste par poste : 6 scénarios, 34 étapes, aucun écart ; 874 tests automatisés"),
    ],
    'circuit': {
        'kicker': '2 · Le parcours',
        'titre': "Le parcours d'un client dans l'établissement",
        'noeuds': [('web', 'Site web'), ('recep', 'Réception'), ('sejour', 'Séjour & folio'), ('bar', 'Bar & restaurant'),
                   ('gouv', 'Gouvernante'), ('depart', 'Départ & facture'), ('dir', 'Direction'), ('fin', 'Client fidélisé')],
        'zones': [('Avant le séjour', 0, 0), ('Pendant le séjour', 1, 4), ('Après', 5, 7)],
        'note': "Chaque poste ne voit que <b>ses menus</b> : la réception, la gouvernante, la caisse, le magasin et "
                "la direction ont chacun leur profil, et travaillent sur <b>les mêmes données</b>.",
        'fin_coche': True,
    },
    'connexion': {
        'kicker': '3 · Prise en main',
        'identifiant': 'm.ateba@demo-hotellerie.cm',
        'items': [
            ('Votre identifiant', "Créé par l'administrateur : un compte par personne, jamais partagé."),
            ('Votre mot de passe', "Personnel ; il se change depuis vos préférences."),
            ('Votre profil', "Il décide de vos menus : Réception, Gouvernante, Caisse, Magasin ou Direction."),
        ],
    },
    'chapitres': _CHAPITRES,
    'css': '\n'.join(chap['css'] for chap in _CHAPITRES if chap.get('css')),
    'retenir': {
        'kicker': 'À retenir',
        'regle': "Un seul outil, un seul folio, une seule vérité : chaque geste du terrain alimente les chiffres de la direction.",
        'puces': [
            "La taxe de séjour, le registre de police et les statistiques se font tout seuls, sans saisie de plus.",
            "Chaque poste a ses menus : ce qui ne le concerne pas lui est refusé, avec un message clair.",
            "La solution est recettée poste par poste et tourne sur Odoo 18 Community ou Enterprise.",
        ],
    },
    'voix': {
        'ouverture': "Aïte haousse, la suite hôtelière complète sur Odoo 18. Réservations, séjours, bar, ménage, "
                     "ardoises, stock et pilotage : tout l'établissement, dans un seul outil.",
        'poste': "La solution tient en trois verbes : accueillir, servir et piloter. Seize modules, en francs CFA, "
                 "sur Odoo 18, et une recette jouée poste par poste, sans aucun écart.",
        'circuit': "Suivons un client : il réserve sur le site, la réception l'accueille, son séjour s'inscrit sur "
                   "un folio, le bar y pose ses consommations, la gouvernante prépare sa chambre, puis la facture "
                   "part et la direction retrouve les chiffres.",
        'connexion': "Chacun se connecte avec son identifiant et son mot de passe. Le profil fait le reste : il "
                     "décide des menus que la personne voit.",
        'retenir': "À retenir : un seul outil, un seul folio, une seule vérité. Chaque geste du terrain alimente "
                   "les chiffres de la direction, et la conformité se fait toute seule.",
        'fin': "Aïte haousse, par Aïte Consulting. Le cahier de recette détaille chaque écran que vous venez de voir.",
    },
    'guide': 'Cahier de recette AITE HOUSE — 146 cas, 17 domaines',
    'vignette': {'chapitre': 1, 'etape': 1, 'apres': 3.0},
}
