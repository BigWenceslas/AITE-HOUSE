# -*- coding: utf-8 -*-
"""Les motifs d'annulation (spécification, partie 3.2 ; Q35 ; incrément 4).

Cinq motifs sont posés d'office (``data/restaurant_motif_data.xml``,
``noupdate="1"`` : le manager les renomme, les range ou en ajoute sans code).
Le compte de la caisse ne les lit pas : la fenêtre d'annulation les demande à
son ouverture, par une requête en ``sudo()`` (``pos.session
.aite_motifs_annulation``) ; un motif ajouté pendant le service est donc
proposé à l'annulation suivante (REST-12 critère 5). On n'efface pas un
motif : on l'archive (les droits n'ont pas la suppression).
"""
from odoo import fields, models


class RestaurantMotif(models.Model):
    _name = 'aite.restaurant.motif'
    _description = "Motif d'annulation"
    _order = 'sequence, id'

    name = fields.Char("Motif", required=True)
    sequence = fields.Integer("Ordre", default=10)
    active = fields.Boolean("Actif", default=True)
    precision_requise = fields.Boolean(
        "Précision obligatoire",
        help="Cochée : le chef de salle doit écrire quelques mots, comme pour « Autre ».")
