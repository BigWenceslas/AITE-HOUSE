# -*- coding: utf-8 -*-
"""Règles de la caisse du restaurant — Python pur, sans import d'Odoo (T12).

Source unique du tableau des droits (spécification, partie 3.3) :
* le serveur appelle ``autorise`` dans chaque contrôle ;
* la caisse reçoit ``DROITS``, l'ordre des niveaux et ``DELAI_RETOUR_PLAN``
  au chargement (``pos.session._load_pos_data``) et applique le même
  algorithme (``PosStore.aitePeut``) ;
* le rôle de ``pos_hr`` est dérivé du niveau (``role_caisse``).

Ce fichier est chargé tel quel par ``tests/restaurant/test_restaurant_logic.py``,
sans Odoo : il ne doit importer que la bibliothèque standard.
"""
import re

NIVEAUX = [
    ('serveur', "Serveur"),
    ('caissiere', "Caissière"),
    ('superviseur', "Chef de salle ou superviseur"),
    ('manager', "Manager"),
]

# geste : niveau minimal (Q8 : chaque case « à trancher » vaut « non » ;
# Q15, Q19, Q20, Q21, Q22)
DROITS = {
    'servir': 'serveur',             # ouvrir SES tables, saisir, envoyer, addition, personnes,
                                     # diviser, déplacer ou réunir SES tables
    'table_collegue': 'caissiere',   # Q19
    'ouvrir_caisse': 'caissiere',    # Q15
    'encaisser': 'caissiere',
    'rapport_ventes': 'caissiere',   # « Imprimer le rapport » du menu (Q22)
    'vente_sans_table': 'caissiere', # si la case est cochée
    'annuler_envoye': 'superviseur', # Q21 : produit, table, tables à la fermeture
    'especes': 'superviseur',
    'fermer_caisse': 'superviseur',
    'fermer_avec_ecart': 'manager',  # au-delà de l'écart maximum, s'il est réglé
    'rembourser': 'manager',
    'ardoise': 'manager',            # AH-02, T7
    'prix': 'manager',               # REST-04-P1
    'creer_produit': 'manager',
}

DELAI_RETOUR_PLAN = 300  # secondes (T10) : retour au plan verrouillé sans activité
# Remise, produit offert : personne en caisse à l'ouverture (Q20) — réglage, pas un droit.
# Plan de salle : dessiné dans la gestion par le compte Odoo du manager (T17).

_RANG = {code: rang for rang, (code, _libelle) in enumerate(NIVEAUX)}
_CODE = re.compile(r'[0-9]{4}')  # chiffres ASCII seulement (pas « ４８２１ »)
NOMBRE_DE_CODES = 10000


def autorise(niveau, geste):
    """Vrai si ``niveau`` suffit pour ``geste``. Niveau ou geste inconnu → faux."""
    if not isinstance(niveau, str) or not isinstance(geste, str):
        return False
    requis = DROITS.get(geste)
    if requis is None or niveau not in _RANG:
        return False
    return _RANG[niveau] >= _RANG[requis]


def role_caisse(niveau):
    """Rôle de ``pos_hr`` : 'manager' si le niveau a le droit de changer les
    prix, sinon 'cashier'. Le superviseur ne reçoit donc pas en bloc les
    droits avancés d'Odoo (prix, création d'article)."""
    return 'manager' if autorise(niveau, 'prix') else 'cashier'


def code_valide(code):
    """Vrai pour exactement 4 chiffres (« 0427 » compris)."""
    return isinstance(code, str) and _CODE.fullmatch(code) is not None


def code_libre(codes_pris, rng):
    """Un code de 4 chiffres que personne n'a, tiré par ``rng`` (un
    ``random.Random`` ; ``random.SystemRandom()`` en production).

    Lève ``ValueError`` si les 10 000 codes sont tous pris.
    """
    pris = {code for code in codes_pris if code}
    libres = [code for code in ('%04d' % i for i in range(NOMBRE_DE_CODES))
              if code not in pris]
    if not libres:
        raise ValueError(
            "Les 10 000 codes à 4 chiffres sont tous pris : archivez les "
            "employés partis pour libérer leur code.")
    return rng.choice(libres)
