# -*- coding: utf-8 -*-
"""Le nombre d'exemplaires des bons de préparation (demande du Messager :
« imprimer 3 fois d'un coup en cuisine » ; 18.0.1.0.13).

Réglage de l'imprimante de préparation (Point de Vente → Configuration →
Imprimantes de préparation) : « Nombre d'exemplaires du bon », 1 d'office,
entre 1 et 5. Sur une caisse au service à table contrôlé, un bon qui porte
de nouveaux plats sort en autant d'exemplaires identiques, numérotés
« Exemplaire 1/3 »… ; un bon fait seulement d'annulations, de notes ou de
la note générale sort en un exemplaire. La règle est appliquée par la caisse
(``static/src/utils/bons.js``).
"""
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

EXEMPLAIRES_MIN = 1
EXEMPLAIRES_MAX = 5


class PosPrinter(models.Model):
    _inherit = 'pos.printer'

    aite_exemplaires = fields.Integer(
        "Nombre d'exemplaires du bon", default=1,
        help="Combien de fois chaque nouveau bon sort sur cette imprimante (de 1 à 5).")
    aite_exemplaires_phrase = fields.Char(
        "Ce qui va se passer", compute='_compute_aite_exemplaires_phrase')

    @api.depends('aite_exemplaires')
    def _compute_aite_exemplaires_phrase(self):
        for imprimante in self:
            imprimante.aite_exemplaires_phrase = self._phrase_exemplaires(
                imprimante.aite_exemplaires)

    @staticmethod
    def _phrase_exemplaires(nombre):
        """La phrase « ce qui va se passer » du réglage."""
        if not nombre or nombre <= 1:
            return ("Chaque nouveau bon envoyé à cette imprimante sort en un seul "
                    "exemplaire.")
        return ("Chaque nouveau bon envoyé à cette imprimante sort en %(n)d exemplaires "
                "identiques, marqués « Exemplaire 1/%(n)d » à « Exemplaire %(n)d/%(n)d ». "
                "Les annulations et les notes seules sortent en un exemplaire." % {'n': nombre})

    @api.constrains('aite_exemplaires')
    def _check_aite_exemplaires(self):
        for imprimante in self:
            if not EXEMPLAIRES_MIN <= imprimante.aite_exemplaires <= EXEMPLAIRES_MAX:
                raise ValidationError(_(
                    "Le nombre d'exemplaires du bon doit être entre 1 et 5 "
                    "(imprimante « %s »).", imprimante.name))

    @api.model
    def _load_pos_data_fields(self, config_id):
        champs = super()._load_pos_data_fields(config_id)
        return champs + ['aite_exemplaires'] if champs else champs
