# -*- coding: utf-8 -*-
"""Lignes d'addition : ce qui est parti en cuisine ou au bar, tenu par le
serveur seul (spécification, T9, partie 3.1 ; incrément 3).

``aite_qte_envoyee`` est ce que le serveur sait être parti et pas encore
annulé avec le code d'un responsable ; ``aite_qte_preparation`` est la
dernière quantité de préparation reçue de la caisse pour la ligne : seule sa
hausse (un nouvel envoi) augmente ``aite_qte_envoyee``. Les deux champs ne
sont pas chargés en caisse (la liste des champs de ligne d'Odoo est
explicite) ; ils sont retirés de toute écriture reçue (synchronisation,
écriture directe du compte de la caisse), sauf quand notre propre code
serveur écrit (``contexte_serveur`` : une clé de contexte envoyée par la
caisse n'autorise rien).
"""
from odoo import api, fields, models

from .pos_session import ecrit_par_le_serveur

CHAMPS_LIGNE_SERVEUR = ('aite_qte_envoyee', 'aite_qte_preparation')


def sans_champs_ligne_serveur(vals):
    return {champ: valeur for champ, valeur in vals.items()
            if champ not in CHAMPS_LIGNE_SERVEUR}


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    aite_qte_envoyee = fields.Float(
        "Quantité envoyée (non annulée)", readonly=True, copy=False,
        digits='Product Unit of Measure',
        help="Ce que le serveur sait être parti en cuisine ou au bar et pas "
             "encore annulé avec le code d'un responsable.")
    aite_qte_preparation = fields.Float(
        "Quantité de préparation reçue", readonly=True, copy=False,
        digits='Product Unit of Measure',
        help="Technique : la dernière quantité de préparation reçue de la caisse "
             "pour cette ligne ; seule sa hausse (un nouvel envoi) augmente la "
             "quantité envoyée.")

    @api.model_create_multi
    def create(self, vals_list):
        if not ecrit_par_le_serveur(self.env):
            vals_list = [sans_champs_ligne_serveur(vals) for vals in vals_list]
        return super().create(vals_list)

    def write(self, vals):
        if not ecrit_par_le_serveur(self.env):
            vals = sans_champs_ligne_serveur(vals)
        return super().write(vals)
