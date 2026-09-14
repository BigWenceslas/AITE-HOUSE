# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HotelHotel(models.Model):
    """
    Établissement hôtelier.

    Point d'ancrage du multi-établissements : chaque chambre, réservation,
    folio ou tâche de gouvernante appartient à un hôtel. L'hôtel porte les
    horaires standards d'arrivée / départ (utilisés comme valeurs par
    défaut des réservations) ainsi que les informations d'identité
    imprimées sur les documents (confirmation, note de séjour).
    """
    _name = 'aite.hotel.hotel'
    _description = "Hôtel (établissement)"
    _order = 'sequence, name'

    name = fields.Char(string="Nom de l'hôtel", required=True, translate=True)
    code = fields.Char(
        string="Code", required=True, copy=False,
        help="Code court de l'établissement (ex. LVD), repris dans les "
             "références internes.",
    )
    sequence = fields.Integer(string="Séquence", default=10)
    active = fields.Boolean(string="Actif", default=True)
    company_id = fields.Many2one(
        'res.company', string="Société", required=True, index=True,
        default=lambda self: self.env.company,
    )
    currency_id = fields.Many2one(
        'res.currency', string="Devise",
        related='company_id.currency_id', store=True, readonly=True,
    )
    image_1920 = fields.Image(string="Photo", max_width=1920, max_height=1920)

    # Identité / coordonnées (imprimées sur les documents).
    street = fields.Char(string="Rue")
    city = fields.Char(string="Ville")
    country_id = fields.Many2one(
        'res.country', string="Pays",
        default=lambda self: self.env.company.country_id,
    )
    phone = fields.Char(string="Téléphone")
    email = fields.Char(string="E-mail")
    website = fields.Char(string="Site web")
    stars = fields.Selection(
        selection=[(str(i), "%d ★" % i) for i in range(1, 6)],
        string="Catégorie", default='3',
    )

    # Horaires standards — heures décimales (14.0 = 14 h 00).
    checkin_hour = fields.Float(
        string="Heure d'arrivée standard", default=14.0,
        help="Heure de check-in proposée par défaut sur les réservations "
             "(format décimal : 14,5 = 14 h 30).",
    )
    checkout_hour = fields.Float(
        string="Heure de départ standard", default=12.0,
        help="Heure de check-out proposée par défaut sur les réservations.",
    )

    note = fields.Html(
        string="Politique / informations",
        help="Conditions de séjour imprimées au bas de la confirmation de "
             "réservation (annulation, acompte, animaux…).",
    )

    room_ids = fields.One2many('aite.hotel.room', 'hotel_id', string="Chambres")
    room_count = fields.Integer(
        string="Nb chambres", compute='_compute_counts',
    )
    sellable_room_count = fields.Integer(
        string="Chambres vendables", compute='_compute_counts',
        help="Chambres actives hors 'hors service' : dénominateur du taux "
             "d'occupation et du RevPAR.",
    )
    floor_ids = fields.One2many('aite.hotel.floor', 'hotel_id', string="Étages")

    _sql_constraints = [
        ('code_company_uniq', 'unique(code, company_id)',
         "Ce code d'hôtel est déjà utilisé dans la société."),
    ]

    # ------------------------------------------------------------------
    # Compute
    # ------------------------------------------------------------------

    def _compute_counts(self):
        Room = self.env['aite.hotel.room']
        for hotel in self:
            rooms = Room.search([('hotel_id', '=', hotel.id)])
            hotel.room_count = len(rooms)
            hotel.sellable_room_count = len(
                rooms.filtered(lambda r: not r.out_of_order))

    # ------------------------------------------------------------------
    # Contraintes
    # ------------------------------------------------------------------

    @api.constrains('checkin_hour', 'checkout_hour')
    def _check_hours(self):
        for hotel in self:
            for value in (hotel.checkin_hour, hotel.checkout_hour):
                if not 0.0 <= value < 24.0:
                    raise ValidationError(
                        _("Les heures standards doivent être comprises "
                          "entre 0 et 24."))

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def action_view_rooms(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _("Chambres — %s", self.name),
            'res_model': 'aite.hotel.room',
            'view_mode': 'kanban,list,form',
            'domain': [('hotel_id', '=', self.id)],
            'context': {'default_hotel_id': self.id},
        }


class HotelFloor(models.Model):
    """
    Étage (ou aile / bâtiment) d'un hôtel.

    Sert au regroupement opérationnel des chambres — parcours de la
    gouvernante, room board — sans logique propre.
    """
    _name = 'aite.hotel.floor'
    _description = "Étage d'hôtel"
    _order = 'hotel_id, sequence, name'

    name = fields.Char(string="Nom", required=True, translate=True)
    sequence = fields.Integer(string="Séquence", default=10)
    hotel_id = fields.Many2one(
        'aite.hotel.hotel', string="Hôtel", required=True,
        ondelete='cascade', index=True,
    )
    company_id = fields.Many2one(
        'res.company', related='hotel_id.company_id', store=True,
        readonly=True,
    )
    room_ids = fields.One2many('aite.hotel.room', 'floor_id', string="Chambres")
