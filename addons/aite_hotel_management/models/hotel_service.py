# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HotelService(models.Model):
    """
    Service hôtelier facturable (restaurant, blanchisserie, transport…).

    Catalogue curaté des extras imputables au folio d'un client. Comme les
    types de chambre, chaque service est adossé à un article Odoo (créé
    automatiquement) qui porte prix, taxes et comptes : la ligne de folio
    référence l'article, la facture hérite de tout.
    """
    _name = 'aite.hotel.service'
    _description = "Service hôtelier"
    _order = 'category, sequence, name'

    name = fields.Char(string="Nom", required=True, translate=True)
    sequence = fields.Integer(string="Séquence", default=10)
    active = fields.Boolean(string="Actif", default=True)
    category = fields.Selection(
        selection=[
            ('restaurant', "Restaurant / Bar"),
            ('laundry', "Blanchisserie"),
            ('transport', "Transport"),
            ('spa', "Spa & bien-être"),
            ('minibar', "Minibar"),
            ('other', "Divers"),
        ],
        string="Catégorie", required=True, default='other', index=True,
    )
    company_id = fields.Many2one(
        'res.company', string="Société", required=True,
        default=lambda self: self.env.company,
    )
    currency_id = fields.Many2one(
        'res.currency', related='company_id.currency_id', readonly=True,
    )
    price = fields.Monetary(
        string="Prix unitaire", required=True, currency_field='currency_id',
    )
    product_id = fields.Many2one(
        'product.product', string="Article lié", readonly=True, copy=False,
    )
    description = fields.Text(string="Description")

    def _prepare_product_vals(self):
        self.ensure_one()
        categ = self.env.ref(
            'aite_hotel_management.product_category_hotel',
            raise_if_not_found=False)
        return {
            'name': self.name,
            'type': 'service',
            'invoice_policy': 'order',
            'list_price': self.price,
            'sale_ok': True,
            'purchase_ok': False,
            'categ_id': categ.id if categ else False,
            'company_id': self.company_id.id,
        }

    @api.model_create_multi
    def create(self, vals_list):
        services = super().create(vals_list)
        for service in services:
            if not service.product_id:
                # ``sudo`` : écriture technique de l'article support —
                # le responsable hôtel n'a pas les droits product.product.
                service.product_id = self.env[
                    'product.product'].sudo().create(
                        service._prepare_product_vals())
        return services

    def write(self, vals):
        res = super().write(vals)
        if 'name' in vals or 'price' in vals:
            for service in self.filtered('product_id'):
                service.product_id.sudo().write({
                    'name': service.name,
                    'list_price': service.price,
                })
        return res

    @api.constrains('price')
    def _check_price(self):
        for service in self:
            if service.price < 0:
                raise ValidationError(
                    _("Le prix d'un service ne peut pas être négatif."))


class HotelSeasonPrice(models.Model):
    """
    Tarif saisonnier d'un type de chambre.

    Prix par nuit appliqué sur une plage de dates (haute saison, fêtes,
    événements). Un tarif rattaché à un hôtel précis prime sur un tarif
    « tous hôtels » ; à dates égales, le moteur retient le prix le plus
    bas parmi les tarifs restants (comportement pro-client, documenté).
    """
    _name = 'aite.hotel.season.price'
    _description = "Tarif saisonnier"
    _order = 'date_from desc'

    name = fields.Char(
        string="Libellé", required=True,
        help="Ex. Haute saison 2026, Fêtes de fin d'année.",
    )
    active = fields.Boolean(string="Actif", default=True)
    room_type_id = fields.Many2one(
        'aite.hotel.room.type', string="Type de chambre", required=True,
        ondelete='cascade', index=True,
    )
    hotel_id = fields.Many2one(
        'aite.hotel.hotel', string="Hôtel",
        help="Vide = tous les hôtels de la société.",
    )
    company_id = fields.Many2one(
        'res.company', related='room_type_id.company_id', store=True,
        readonly=True,
    )
    currency_id = fields.Many2one(
        'res.currency', related='company_id.currency_id', readonly=True,
    )
    date_from = fields.Date(string="Du", required=True)
    date_to = fields.Date(string="Au", required=True)
    price = fields.Monetary(
        string="Prix / nuit", required=True, currency_field='currency_id',
    )

    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        for season in self:
            if season.date_to < season.date_from:
                raise ValidationError(
                    _("La date de fin d'un tarif saisonnier doit être "
                      "postérieure ou égale à la date de début."))

    @api.constrains('price')
    def _check_price(self):
        for season in self:
            if season.price <= 0:
                raise ValidationError(
                    _("Le prix d'un tarif saisonnier doit être positif."))
