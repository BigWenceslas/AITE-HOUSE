# -*- coding: utf-8 -*-
"""Le journal des saisies : qui a saisi chaque produit (REST-02 critère 3,
Q14 ; spécification, T19, parties 3.2 et 4.2 ; incrément 3).

Choix (a) du périmètre : un journal, sans toucher aux lignes de l'addition.
Le serveur y écrit, à chaque synchronisation de la caisse, chaque hausse de
quantité d'une ligne, au nom de la personne identifiée sur le poste. Les noms
sont recopiés : la trace ne change pas si l'on renomme quelqu'un ou un
produit, et le lecteur n'a besoin d'aucun droit sur les employés.

Personne n'écrit ce journal à la main : il est créé par le serveur seul, en
``sudo()`` (écriture technique), et il ne se modifie ni ne s'efface, même en
``sudo()`` ou pour l'administrateur.
"""
from odoo import _, fields, models
from odoo.exceptions import UserError


class RestaurantSaisie(models.Model):
    _name = 'aite.restaurant.saisie'
    _description = "Saisie"
    _order = 'date desc, id desc'
    _rec_name = 'produit_nom'

    date = fields.Datetime("Date", required=True, readonly=True, default=fields.Datetime.now)
    company_id = fields.Many2one('res.company', "Société", required=True, readonly=True,
                                 default=lambda self: self.env.company)
    config_id = fields.Many2one('pos.config', "Caisse", readonly=True)
    order_id = fields.Many2one('pos.order', "Addition", readonly=True, index=True,
                               ondelete='set null')
    order_ref = fields.Char("Référence de l'addition", readonly=True)
    table_nom = fields.Char("Table", readonly=True)
    ligne_uuid = fields.Char("Identifiant de la ligne", readonly=True)
    produit_id = fields.Many2one('product.product', "Article", readonly=True,
                                 ondelete='set null')
    produit_nom = fields.Char("Produit", readonly=True)
    quantite = fields.Float("Quantité ajoutée", readonly=True,
                            digits='Product Unit of Measure')
    employe_id = fields.Many2one('hr.employee', "Employé", readonly=True, ondelete='set null')
    employe_nom = fields.Char("Saisie par", readonly=True)

    def _aite_refus(self):
        return UserError(_(
            "Une saisie enregistrée ne se modifie pas et ne s'efface pas : "
            "c'est la trace demandée par le manager."))

    def write(self, vals):
        raise self._aite_refus()

    def unlink(self):
        raise self._aite_refus()
