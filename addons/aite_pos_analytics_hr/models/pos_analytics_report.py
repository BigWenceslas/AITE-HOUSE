# -*- coding: utf-8 -*-
"""L'employé dans l'analyse AITE (AH-03 ; spécification du restaurant,
partie 5.5).

La vue SQL ``aite.pos.daily.report`` reçoit, par son point d'extension
``_aite_colonnes_supplementaires``, deux colonnes lues sur l'addition :

- ``serveur_id`` : « Ouverte par » (``aite_ouverte_par_id``), la personne qui
  a ouvert la table — le vendeur d'un restaurant, qui n'encaisse pas (Q8,
  Q49 ; le cas de recette D12, « Suivre les ventes par vendeur », se rejoue
  sur « Serveur ») ;
- ``encaisse_par_id`` : « Encaissée par » (``aite_encaissee_par_id``), sinon
  l'employé d'Odoo (``employee_id`` de pos_hr) pour une caisse à codes hors
  service à table.

Les deux pointent vers ``hr.employee.public`` (vue SQL sur ``hr_employee``,
mêmes identifiants), lisible par tout utilisateur interne : le lecteur des
analyses n'a besoin d'aucun droit sur les Employés. ``user_id`` s'affiche
« Compte Odoo » : c'est vrai pour une boutique comme pour une caisse à codes,
où toutes les additions passent sous le compte de la caisse.
"""
from odoo import api, fields, models


class PosDailyReport(models.Model):
    _inherit = 'aite.pos.daily.report'

    user_id = fields.Many2one(string="Compte Odoo")
    serveur_id = fields.Many2one(
        'hr.employee.public', string="Serveur (ouverte par)", readonly=True,
        help="L'employé qui a ouvert la table, reconnu par son code : le vendeur "
             "d'un restaurant, qui n'encaisse pas.")
    encaisse_par_id = fields.Many2one(
        'hr.employee.public', string="Encaissée par", readonly=True,
        help="L'employé qui a validé le paiement avec son code.")

    @api.model
    def _aite_colonnes_supplementaires(self):
        # Le crochet de désinstallation recrée la vue sans ces colonnes, en
        # gardant celles des autres modules (aite_sans_employe).
        if self.env.context.get('aite_sans_employe'):
            return super()._aite_colonnes_supplementaires()
        return super()._aite_colonnes_supplementaires() + (
            ", po.aite_ouverte_par_id AS serveur_id"
            ", COALESCE(po.aite_encaissee_par_id, po.employee_id) AS encaisse_par_id")
