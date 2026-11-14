# -*- coding: utf-8 -*-
"""Règles de la caisse du restaurant — Python pur, sans import d'Odoo (T12).

Source unique du tableau des droits (spécification, partie 3.3) :
* le serveur appelle ``autorise`` dans chaque contrôle ;
* la caisse reçoit ``DROITS``, l'ordre des niveaux et ``DELAI_RETOUR_PLAN``
  au chargement (``pos.session._load_pos_data``) et applique le même
  algorithme (``PosStore.aitePeut``) ;
* le rôle de ``pos_hr`` est dérivé du niveau (``role_caisse``).

Incrément 5 : la couleur d'une table du plan (``alerte``, délai par défaut
``DELAI_ALERTE``) ; la caisse applique la même règle (``utils/alerte.js``),
avec le délai de la caisse (``pos.config.aite_delai_alerte``).

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
DELAI_ALERTE = 60  # minutes (Q11) : une table ouverte depuis ce délai passe à l'orange
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


def _nombre(valeur):
    """Une quantité reçue (None, False, entier, décimal) en décimal."""
    try:
        return float(valeur or 0)
    except (TypeError, ValueError):
        return 0.0


def bilan_ligne(envoyee, prep_avant, prep, qte_avant, qte, deplacement):
    """Ce que le serveur conclut d'une ligne d'addition à une synchronisation
    (T9, T19 ; partie 4.2).

    - ``envoyee`` : ce que le serveur sait être parti et pas encore annulé
      (``aite_qte_envoyee``) ;
    - ``prep_avant``, ``prep`` : la quantité de préparation de la ligne avant
      et après la synchronisation (``last_order_preparation_change``) ; seule
      sa **hausse** (un nouvel envoi) augmente ce qui est parti : une copie de
      poste en retard ne relève pas le verrou après une annulation ;
    - ``qte_avant``, ``qte`` : la quantité de la ligne avant et après (0 pour
      une ligne neuve ou retirée) ;
    - ``deplacement`` : division ou réunion (ni saisie, ni retrait).

    Rend ``(saisie, retrait, nouvelle_envoyee)`` : la quantité ajoutée à
    écrire au journal des saisies, la quantité partie retirée sans code (au
    journal des annulations), et ce qui reste parti sur la ligne.
    """
    envoyee, prep_avant, prep = _nombre(envoyee), _nombre(prep_avant), _nombre(prep)
    qte_avant, qte = _nombre(qte_avant), _nombre(qte)
    partie = max(envoyee, 0.0) + max(prep - prep_avant, 0.0)
    reste = max(qte, 0.0)
    nouvelle = min(partie, reste)
    if deplacement:
        saisie = retrait = 0.0
    else:
        saisie = max(qte - qte_avant, 0.0)
        retrait = max(partie - reste, 0.0)
    return round(saisie, 6), round(retrait, 6), round(nouvelle, 6)


def part_negative(qte_avant, qte):
    """La quantité négative ajoutée à une ligne d'addition qui n'est **pas**
    un remboursement, depuis la synchronisation précédente (revue de
    l'incrément 4, constat 1) : une ligne neuve à -1 (« +/- » sur une ligne
    neuve), ou une ligne qui s'enfonce sous zéro. Elle baisse l'addition comme
    un retrait de ce qui est parti : « Retrait sans code ». Une ligne de
    remboursement (``refunded_orderline_id``) n'est jamais passée ici.
    ``bilan_ligne`` ne compte, lui, que la part positive."""
    avant = max(-_nombre(qte_avant), 0.0)
    apres = max(-_nombre(qte), 0.0)
    return round(max(apres - avant, 0.0), 6)


def alerte(minutes, delai):
    """La couleur d'une table du plan (REST-17, incrément 5) : ``''`` pour
    une table libre (``minutes`` vaut ``None``), ``'vert'`` pour une table
    ouverte, ``'orange'`` quand elle l'est depuis ``delai`` minutes ou plus
    (« 60 minutes révolues », REST-17 critère 1) : c'est le moment de
    proposer l'addition. Un délai vide ou nul vaut ``DELAI_ALERTE`` (le
    réglage refuse moins d'une minute). La caisse applique la même règle
    (``utils/alerte.js``)."""
    if minutes is None:
        return ''
    try:
        delai = int(delai or 0)
    except (TypeError, ValueError):
        delai = 0
    if delai < 1:
        delai = DELAI_ALERTE
    return 'orange' if _nombre(minutes) >= delai else 'vert'


def compteurs(personnes, part, remboursement):
    """Ce qu'une addition réglée compte dans « Personnes et tables »
    (partie 5.2) : ``(tables, personnes, sans_table)``.

    Une table (ou un numéro tapé) compte pour une table et ses personnes ; une
    part née d'une division (« 12B ») n'a pas de personne et ne compte pas,
    sauf portée sur une table libre (elle a alors ses personnes) ; une vente
    sans table compte à part (Q76) ; un remboursement ne compte pas.
    """
    personnes = int(_nombre(personnes))
    if remboursement:
        return 0, 0, 0
    if personnes >= 1:
        return 1, personnes, 0
    if part:
        return 0, 0, 0
    return 0, 0, 1
