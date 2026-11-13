# -*- coding: utf-8 -*-
"""Employés de la caisse : niveau, code unique de 4 chiffres, chargement en
caisse (spécification, parties 3.1, 3.3 et 4.2 ; REST-01, REST-03)."""
import random

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

from . import regles

AIDE_NIVEAU = (
    "Serveur : ouvre ses tables, commande, envoie, imprime l'addition ; "
    "n'encaisse pas et n'annule pas ce qui est envoyé. Caissière : en plus, "
    "ouvre la caisse et encaisse toutes les tables. Chef de salle ou "
    "superviseur : en plus, annule ce qui est envoyé (avec un motif), sort des "
    "espèces et ferme la caisse. Manager : tout, y compris les prix et les "
    "remboursements. Vide : l'employé n'apparaît pas sur la caisse."
)
AIDE_CODE = (
    "4 chiffres, propres à cet employé. Il le tape sur la caisse pour ouvrir "
    "une table, encaisser ou annuler : la caisse sait ainsi qui a fait quoi. "
    "Deux employés ne peuvent pas avoir le même code. Proposé d'office quand "
    "vous choisissez un niveau ; ne le communiquez qu'à l'employé."
)


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    # copy=False : le code d'Odoo (``pin``) n'est pas copié par « Dupliquer » ;
    # une copie qui garderait le niveau serait refusée (R23, code absent).
    # La copie arrive sans niveau, donc hors de la caisse ; choisir son
    # niveau lui propose un code.
    aite_niveau_caisse = fields.Selection(
        regles.NIVEAUX, string="Niveau en caisse", copy=False,
        groups="hr.group_hr_user", tracking=True, help=AIDE_NIVEAU)

    # ------------------------------------------------------------------
    # Le code : obligatoire, 4 chiffres, unique (R23)
    # ------------------------------------------------------------------

    @api.constrains('pin', 'aite_niveau_caisse', 'active', 'company_id')
    def _aite_verifier_code(self):
        """Tout employé actif qui a un niveau a un code de 4 chiffres que
        personne d'autre n'a dans la société. La recherche se fait en
        ``sudo()`` : celui qui enregistre ne voit pas forcément les codes des
        autres. Le message ne nomme jamais le collègue, pour ne pas révéler
        son code."""
        for employe in self.sudo():
            if not employe.active or not employe.aite_niveau_caisse:
                continue
            code = employe.pin
            if not code:
                raise ValidationError(_(
                    "Donnez un code à 4 chiffres à %(nom)s : sans code, il ne "
                    "peut pas utiliser la caisse.", nom=employe.name))
            if not regles.code_valide(code):
                raise ValidationError(_("Le code doit faire exactement 4 chiffres."))
            if self.sudo().search_count([
                    ('id', '!=', employe.id),
                    ('company_id', '=', employe.company_id.id),
                    ('aite_niveau_caisse', '!=', False),
                    ('pin', '=', code)], limit=1):
                raise ValidationError(_(
                    "Le code %(code)s est déjà celui d'un autre employé. "
                    "Choisissez quatre autres chiffres : chaque employé a son "
                    "propre code.", code=code))

    @api.onchange('aite_niveau_caisse')
    def _onchange_aite_niveau_caisse(self):
        """Un niveau choisi sans code : un code libre est proposé d'office
        (tiré au hasard parmi ceux que personne n'a, archivés compris)."""
        if self.aite_niveau_caisse and not self.pin:
            company = self.company_id or self.env.company
            pris = self.sudo().with_context(active_test=False).search([
                ('company_id', '=', company.id),
                ('pin', '!=', False),
            ]).mapped('pin')
            self.pin = regles.code_libre(pris, random.SystemRandom())

    # ------------------------------------------------------------------
    # Chargement en caisse
    # ------------------------------------------------------------------

    @api.model
    def _load_pos_data_domain(self, data):
        """En mode, la société seule : le niveau décide qui arrive en caisse.
        Les listes « droits de base / avancés » de pos_hr sont ignorées
        (pos_hr y remet les managers à chaque écriture de la caisse)."""
        config = self.env['pos.config'].browse(data['pos.config']['data'][0]['id'])
        if not config._aite_actif():
            return super()._load_pos_data_domain(data)
        return self._check_company_domain(config.company_id)

    def _load_pos_data(self, data):
        """En mode : seuls les employés qui ont un niveau et un code arrivent
        en caisse ; le niveau, réservé aux RH, est lu par le serveur en
        ``sudo()`` et injecté (T5), comme l'empreinte du code (``_pin``). Le
        rôle de pos_hr suit le niveau ; le badge est retiré (le lecteur
        identifierait l'employé sans son code)."""
        res = super()._load_pos_data(data)
        config = self.env['pos.config'].browse(data['pos.config']['data'][0]['id'])
        if not config._aite_actif():
            return res
        ids = [employe['id'] for employe in res['data']]
        niveaux = {e.id: e.aite_niveau_caisse for e in self.sudo().browse(ids)}
        employes = []
        for employe in res['data']:
            niveau = niveaux.get(employe['id'])
            if not niveau or not employe.get('_pin'):
                continue
            employe['_aite_niveau'] = niveau
            employe['_role'] = regles.role_caisse(niveau)
            employe['_barcode'] = False
            employes.append(employe)
        res['data'] = employes
        return res
