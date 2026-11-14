# -*- coding: utf-8 -*-
"""Le journal des annulations (REST-12-P1, REST-22 ; spécification, parties
3.2, 4.2 et 5.1 ; incrément 4).

Une ligne par produit annulé, écrite par le serveur seul, en ``sudo()`` :
- avec le code d'un responsable, vérifié par le serveur
  (``pos.order.aite_autoriser_annulation``) : un produit, une table entière,
  ou les tables encore ouvertes à la fermeture ;
- sans code, détecté par le serveur, sans jamais rien refuser : un « retrait
  sans code » (une quantité envoyée qui baisse à la synchronisation, ou une
  ligne envoyée modifiée ou supprimée directement) et une « annulation sans
  code » (une addition qui porte encore des produits envoyés, annulée sans la
  fenêtre d'annulation).

Les noms sont recopiés (table, produit, employés, motif) : la trace ne change
pas si l'on renomme quelqu'un ou un produit, et le lecteur des rapports (le
chef de salle, profil « Restaurant : lecture des rapports ») n'a besoin
d'aucun droit sur les employés, la caisse ni les commandes. La trace survit à
la suppression de l'addition. Elle ne se modifie pas et ne s'efface pas, même
en ``sudo()`` ou pour l'administrateur.
"""
from odoo import _, fields, models
from odoo.exceptions import UserError

TYPES_ANNULATION = [
    ('produit', "Produit annulé"),
    ('table', "Table annulée"),
    ('fermeture', "Table annulée à la fermeture"),
    ('retrait_sans_code', "Retrait sans code"),
    ('annulation_sans_code', "Annulation sans code"),
]


class RestaurantAnnulation(models.Model):
    _name = 'aite.restaurant.annulation'
    _description = "Annulation"
    _order = 'date desc, id desc'
    _rec_name = 'produit_nom'

    date = fields.Datetime("Date", required=True, readonly=True, default=fields.Datetime.now)
    company_id = fields.Many2one('res.company', "Société", required=True, readonly=True,
                                 default=lambda self: self.env.company)
    config_id = fields.Many2one('pos.config', "Caisse", readonly=True)
    session_id = fields.Many2one('pos.session', "Session", readonly=True)
    order_id = fields.Many2one('pos.order', "Addition", readonly=True, index=True,
                               ondelete='set null')
    order_ref = fields.Char("Référence de l'addition", readonly=True)
    table_nom = fields.Char("Table", readonly=True)
    produit_id = fields.Many2one('product.product', "Article", readonly=True,
                                 ondelete='set null')
    produit_nom = fields.Char("Produit", readonly=True)
    quantite = fields.Float("Quantité", readonly=True, digits='Product Unit of Measure')
    currency_id = fields.Many2one(related='company_id.currency_id', string="Devise",
                                  store=True, readonly=True)
    prix_unitaire = fields.Monetary("Prix unitaire TTC", readonly=True,
                                    help="Remise de la ligne comprise.")
    montant = fields.Monetary("Montant TTC", readonly=True,
                              help="Quantité × prix unitaire TTC.")
    serveur_id = fields.Many2one('hr.employee', "Employé demandeur", readonly=True,
                                 ondelete='set null')
    serveur_nom = fields.Char("Demandée par", readonly=True,
                              help="La personne identifiée sur le poste au moment de "
                                   "l'annulation (pour une trace sans code : l'employé de "
                                   "l'addition, ou le compte Odoo s'il vient de la gestion).")
    superieur_id = fields.Many2one('hr.employee', "Responsable", readonly=True,
                                   ondelete='set null')
    superieur_nom = fields.Char("Autorisée par", readonly=True,
                                help="Le chef de salle, le superviseur ou le manager dont "
                                     "le code a été vérifié par le serveur. Vide pour un "
                                     "retrait ou une annulation sans code.")
    motif_id = fields.Many2one('aite.restaurant.motif', "Fiche du motif", readonly=True,
                               ondelete='set null')
    motif_nom = fields.Char("Motif", readonly=True)
    commentaire = fields.Char("Précision", readonly=True)
    autorisee = fields.Boolean("Avec le code d'un responsable", readonly=True,
                               help="Décoché : détecté par le serveur, sans code ni motif.")
    type_annulation = fields.Selection(TYPES_ANNULATION, string="Nature", required=True,
                                       readonly=True)
    ligne_uuid = fields.Char("Identifiant de la ligne", readonly=True)
    demande_uuid = fields.Char("Clé de la demande", readonly=True, index=True,
                               help="Technique : une demande renvoyée avec la même clé "
                                    "(réponse perdue) rend la première réponse sans rien "
                                    "refaire (T9).")

    _sql_constraints = [
        ('demande_ligne_unique', 'unique(demande_uuid, ligne_uuid)',
         "Cette annulation est déjà enregistrée."),
    ]

    def _aite_refus(self):
        return UserError(_(
            "Une annulation enregistrée ne se modifie pas et ne s'efface pas : "
            "c'est la trace demandée par le manager."))

    def write(self, vals):
        raise self._aite_refus()

    def unlink(self):
        raise self._aite_refus()
