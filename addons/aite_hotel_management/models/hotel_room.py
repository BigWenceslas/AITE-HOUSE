# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class HotelAmenity(models.Model):
    """
    Aménité / équipement (Wi-Fi, climatisation, TV, minibar…).

    Purement descriptif : rattachée aux types de chambre et aux chambres,
    affichée sur les documents et le site. L'icône est une classe
    Font Awesome (ex. ``fa-wifi``) exploitée par les vues.
    """
    _name = 'aite.hotel.amenity'
    _description = "Aménité de chambre"
    _order = 'sequence, name'

    name = fields.Char(string="Nom", required=True, translate=True)
    icon = fields.Char(
        string="Icône", default='fa-check',
        help="Classe Font Awesome, ex. fa-wifi, fa-snowflake-o, fa-tv.",
    )
    sequence = fields.Integer(string="Séquence", default=10)
    active = fields.Boolean(string="Active", default=True)


class HotelRoomType(models.Model):
    """
    Type de chambre (Standard, Deluxe, Suite…).

    Porte le tarif de base par nuit, les capacités et les aménités
    communes. Chaque type est adossé à un **article de service Odoo**
    (créé automatiquement) : c'est cet article qui alimente les lignes de
    folio puis la facture, avec ses taxes et comptes comptables — le PMS
    reste ainsi parfaitement aligné sur la comptabilité.
    """
    _name = 'aite.hotel.room.type'
    _description = "Type de chambre"
    _order = 'sequence, name'

    name = fields.Char(string="Nom", required=True, translate=True)
    code = fields.Char(string="Code", help="Code court (STD, DLX, STE…).")
    sequence = fields.Integer(string="Séquence", default=10)
    active = fields.Boolean(string="Actif", default=True)
    company_id = fields.Many2one(
        'res.company', string="Société", required=True, index=True,
        default=lambda self: self.env.company,
    )
    currency_id = fields.Many2one(
        'res.currency', related='company_id.currency_id', store=True,
        readonly=True,
    )
    image_1920 = fields.Image(string="Photo", max_width=1920, max_height=1920)

    base_price = fields.Monetary(
        string="Tarif de base / nuit", required=True,
        currency_field='currency_id',
        help="Prix par nuit hors saison. Les tarifs saisonniers "
             "(Configuration → Tarifs saisonniers) priment sur ce prix "
             "pour les dates qu'ils couvrent.",
    )
    extra_person_price = fields.Monetary(
        string="Suppl. personne / nuit", currency_field='currency_id',
        help="Supplément par personne au-delà de la capacité adultes de "
             "base, appliqué par nuit.",
    )
    capacity_adults = fields.Integer(string="Capacité adultes", default=2)
    capacity_children = fields.Integer(string="Capacité enfants", default=1)

    amenity_ids = fields.Many2many(
        'aite.hotel.amenity', 'hotel_room_type_amenity_rel',
        'room_type_id', 'amenity_id', string="Aménités",
    )
    description = fields.Text(string="Description", translate=True)

    product_id = fields.Many2one(
        'product.product', string="Article lié", readonly=True, copy=False,
        help="Article de service utilisé pour facturer les nuitées de ce "
             "type de chambre (taxes et comptes de la facture).",
    )
    room_ids = fields.One2many(
        'aite.hotel.room', 'room_type_id', string="Chambres",
    )
    room_count = fields.Integer(string="Nb chambres", compute='_compute_room_count')
    season_ids = fields.One2many(
        'aite.hotel.season.price', 'room_type_id', string="Tarifs saisonniers",
    )

    def _compute_room_count(self):
        data = self.env['aite.hotel.room']._read_group(
            [('room_type_id', 'in', self.ids)],
            ['room_type_id'], ['__count'],
        )
        counts = {room_type.id: count for room_type, count in data}
        for rtype in self:
            rtype.room_count = counts.get(rtype.id, 0)

    # ------------------------------------------------------------------
    # CRUD — article lié
    # ------------------------------------------------------------------

    def _prepare_product_vals(self):
        self.ensure_one()
        categ = self.env.ref(
            'aite_hotel_management.product_category_hotel',
            raise_if_not_found=False)
        return {
            'name': _("Nuitée — %s", self.name),
            'type': 'service',
            'invoice_policy': 'order',
            'list_price': self.base_price,
            'sale_ok': True,
            'purchase_ok': False,
            'categ_id': categ.id if categ else False,
            'company_id': self.company_id.id,
        }

    @api.model_create_multi
    def create(self, vals_list):
        room_types = super().create(vals_list)
        for rtype in room_types:
            if not rtype.product_id:
                rtype.product_id = self.env['product.product'].create(
                    rtype._prepare_product_vals())
        return room_types

    def write(self, vals):
        res = super().write(vals)
        # Garder l'article aligné sur le nom / tarif de base.
        if 'name' in vals or 'base_price' in vals:
            for rtype in self.filtered('product_id'):
                rtype.product_id.write({
                    'name': _("Nuitée — %s", rtype.name),
                    'list_price': rtype.base_price,
                })
        return res

    # ------------------------------------------------------------------
    # Moteur de prix
    # ------------------------------------------------------------------

    def _get_night_price(self, day, hotel=None):
        """
        Prix d'une nuit donnée pour ce type de chambre.

        Priorité : tarif saisonnier couvrant ``day`` (le plus spécifique —
        celui de l'hôtel prime sur un tarif « tous hôtels ») → tarif de
        base du type.
        """
        self.ensure_one()
        domain = [
            ('room_type_id', '=', self.id),
            ('date_from', '<=', day),
            ('date_to', '>=', day),
            ('active', '=', True),
        ]
        seasons = self.env['aite.hotel.season.price'].search(domain)
        if hotel:
            specific = seasons.filtered(lambda s: s.hotel_id == hotel)
            seasons = specific or seasons.filtered(lambda s: not s.hotel_id)
        else:
            seasons = seasons.filtered(lambda s: not s.hotel_id)
        if seasons:
            return seasons.sorted('price')[0].price
        return self.base_price

    def _get_stay_price(self, checkin_date, checkout_date, hotel=None):
        """
        Prix moyen par nuit sur un séjour [checkin, checkout).

        Renvoie ``(prix_moyen_par_nuit, nb_nuits)``. Le prix moyen lisse
        les éventuels changements de saison en cours de séjour, pour une
        ligne de facturation unique et lisible.
        """
        self.ensure_one()
        nights = max(1, (checkout_date - checkin_date).days)
        total = 0.0
        day = checkin_date
        for _i in range(nights):
            total += self._get_night_price(day, hotel=hotel)
            day = fields.Date.add(day, days=1)
        return total / nights, nights


class HotelRoom(models.Model):
    """
    Chambre physique.

    Unité vendue par le PMS : disponibilité, état de propreté
    (gouvernante) et mise hors service se gèrent ici. Le prix effectif est
    celui du type de chambre, sauf surcharge propre à la chambre (vue mer,
    rénovée…).
    """
    _name = 'aite.hotel.room'
    _description = "Chambre"
    _order = 'hotel_id, floor_id, name'

    name = fields.Char(
        string="Numéro / nom", required=True,
        help="Ex. 101, 205, Suite Présidentielle.",
    )
    hotel_id = fields.Many2one(
        'aite.hotel.hotel', string="Hôtel", required=True, index=True,
        ondelete='restrict',
    )
    floor_id = fields.Many2one(
        'aite.hotel.floor', string="Étage", index=True,
        domain="[('hotel_id', '=', hotel_id)]", ondelete='set null',
    )
    room_type_id = fields.Many2one(
        'aite.hotel.room.type', string="Type", required=True, index=True,
        ondelete='restrict',
    )
    company_id = fields.Many2one(
        'res.company', related='hotel_id.company_id', store=True,
        readonly=True, index=True,
    )
    currency_id = fields.Many2one(
        'res.currency', related='company_id.currency_id', readonly=True,
    )
    active = fields.Boolean(string="Active", default=True)
    sequence = fields.Integer(string="Séquence", default=10)

    capacity_adults = fields.Integer(
        string="Capacité adultes", compute='_compute_capacity',
        store=True, readonly=False,
        help="Par défaut celle du type ; modifiable pour cette chambre.",
    )
    capacity_children = fields.Integer(
        string="Capacité enfants", compute='_compute_capacity',
        store=True, readonly=False,
    )
    price_override = fields.Monetary(
        string="Tarif spécifique / nuit", currency_field='currency_id',
        help="Laisser à 0 pour appliquer le tarif du type (et les "
             "saisons). Une valeur non nulle prime sur tout.",
    )
    effective_price = fields.Monetary(
        string="Tarif du jour", compute='_compute_effective_price',
        currency_field='currency_id',
        help="Tarif applicable aujourd'hui (surcharge chambre ou moteur "
             "saisonnier du type).",
    )
    amenity_ids = fields.Many2many(
        'aite.hotel.amenity', 'hotel_room_amenity_rel',
        'room_id', 'amenity_id', string="Aménités supplémentaires",
        help="En plus des aménités du type de chambre.",
    )
    telephone_ext = fields.Char(string="Poste téléphonique")
    note = fields.Text(string="Notes internes")

    # --- Axe gouvernante -------------------------------------------------
    hk_state = fields.Selection(
        selection=[
            ('clean', "Propre"),
            ('to_clean', "À nettoyer"),
            ('cleaning', "Nettoyage en cours"),
            ('inspect', "À inspecter"),
        ],
        string="État ménage", default='clean', required=True, index=True,
    )
    out_of_order = fields.Boolean(
        string="Hors service",
        help="Chambre retirée de la vente (travaux, panne). Exclue de la "
             "disponibilité et du calcul d'occupation.",
    )
    out_of_order_reason = fields.Char(string="Motif hors service")

    # --- Axe occupation (photo du moment, non stocké) --------------------
    occupancy_state = fields.Selection(
        selection=[
            ('free', "Libre"),
            ('arrival', "Arrivée prévue"),
            ('occupied', "Occupée"),
        ],
        string="Occupation", compute='_compute_occupancy',
    )
    status = fields.Selection(
        selection=[
            ('out_of_order', "Hors service"),
            ('occupied', "Occupée"),
            ('arrival', "Arrivée prévue"),
            ('cleaning', "Ménage"),
            ('free', "Libre"),
        ],
        string="Statut", compute='_compute_occupancy',
        help="Statut synthétique du room board : hors service > occupée > "
             "arrivée prévue > ménage > libre.",
    )
    current_line_id = fields.Many2one(
        'aite.hotel.reservation.line', string="Séjour en cours",
        compute='_compute_occupancy',
    )

    _sql_constraints = [
        ('name_hotel_uniq', 'unique(name, hotel_id)',
         "Ce numéro de chambre existe déjà dans cet hôtel."),
    ]

    # ------------------------------------------------------------------
    # Compute
    # ------------------------------------------------------------------

    @api.depends('room_type_id')
    def _compute_capacity(self):
        for room in self:
            room.capacity_adults = room.room_type_id.capacity_adults
            room.capacity_children = room.room_type_id.capacity_children

    @api.depends('price_override', 'room_type_id.base_price')
    def _compute_effective_price(self):
        today = fields.Date.context_today(self)
        for room in self:
            if room.price_override:
                room.effective_price = room.price_override
            elif room.room_type_id:
                room.effective_price = room.room_type_id._get_night_price(
                    today, hotel=room.hotel_id)
            else:
                room.effective_price = 0.0

    def _compute_occupancy(self):
        now = fields.Datetime.now()
        today = fields.Date.context_today(self)
        Line = self.env['aite.hotel.reservation.line']
        for room in self:
            occ, arrival = Line, Line
            if room.ids:
                occ = Line.search([
                    ('room_id', '=', room.id),
                    ('state', '=', 'checked_in'),
                ], limit=1)
                if not occ:
                    arrival = Line.search([
                        ('room_id', '=', room.id),
                        ('state', '=', 'confirmed'),
                        ('checkin_date', '<=',
                         fields.Datetime.to_datetime(str(today)).replace(
                             hour=23, minute=59, second=59)),
                        ('checkout_date', '>', now),
                    ], limit=1, order='checkin_date')
            if occ:
                room.occupancy_state = 'occupied'
                room.current_line_id = occ.id
            elif arrival:
                room.occupancy_state = 'arrival'
                room.current_line_id = arrival.id
            else:
                room.occupancy_state = 'free'
                room.current_line_id = False

            if room.out_of_order:
                room.status = 'out_of_order'
            elif room.occupancy_state == 'occupied':
                room.status = 'occupied'
            elif room.occupancy_state == 'arrival':
                room.status = 'arrival'
            elif room.hk_state in ('to_clean', 'cleaning', 'inspect'):
                room.status = 'cleaning'
            else:
                room.status = 'free'

    @api.depends('name', 'room_type_id.name')
    def _compute_display_name(self):
        for room in self:
            if room.room_type_id:
                room.display_name = "%s [%s]" % (
                    room.name, room.room_type_id.code or room.room_type_id.name)
            else:
                room.display_name = room.name

    # ------------------------------------------------------------------
    # Métier
    # ------------------------------------------------------------------

    def _get_night_price(self, day):
        """Prix d'une nuit pour cette chambre (surcharge ou moteur du type)."""
        self.ensure_one()
        if self.price_override:
            return self.price_override
        return self.room_type_id._get_night_price(day, hotel=self.hotel_id)

    def _get_stay_price(self, checkin_date, checkout_date):
        """Prix moyen / nuit et nombre de nuits pour cette chambre."""
        self.ensure_one()
        if self.price_override:
            nights = max(1, (checkout_date - checkin_date).days)
            return self.price_override, nights
        return self.room_type_id._get_stay_price(
            checkin_date, checkout_date, hotel=self.hotel_id)

    def is_available(self, checkin_dt, checkout_dt, ignore_line=None):
        """
        La chambre est-elle libre sur [checkin_dt, checkout_dt) ?

        Une chambre hors service n'est jamais disponible. Le chevauchement
        est évalué contre les lignes confirmées ou en séjour ; la borne de
        fin est exclusive : un départ à 12 h libère la chambre pour une
        arrivée le même jour à 14 h.
        """
        self.ensure_one()
        if self.out_of_order or not self.active:
            return False
        domain = [
            ('room_id', '=', self.id),
            ('state', 'in', ('confirmed', 'checked_in')),
            ('checkin_date', '<', checkout_dt),
            ('checkout_date', '>', checkin_dt),
        ]
        if ignore_line:
            domain.append(('id', 'not in', ignore_line.ids))
        return not bool(
            self.env['aite.hotel.reservation.line'].search_count(domain))

    # ------------------------------------------------------------------
    # Actions gouvernante (boutons kanban / form)
    # ------------------------------------------------------------------

    def action_set_to_clean(self):
        self.write({'hk_state': 'to_clean'})

    def action_start_cleaning(self):
        self.write({'hk_state': 'cleaning'})

    def action_set_clean(self):
        self.write({'hk_state': 'clean'})

    def action_toggle_out_of_order(self):
        for room in self:
            if not room.out_of_order and room.occupancy_state == 'occupied':
                raise UserError(
                    _("La chambre %s est occupée : elle ne peut pas être "
                      "mise hors service.", room.display_name))
            room.out_of_order = not room.out_of_order
            if not room.out_of_order:
                room.out_of_order_reason = False

    def action_view_reservations(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _("Séjours — chambre %s", self.name),
            'res_model': 'aite.hotel.reservation.line',
            'view_mode': 'list,form',
            'domain': [('room_id', '=', self.id)],
        }

    @api.constrains('capacity_adults')
    def _check_capacity(self):
        for room in self:
            if room.capacity_adults <= 0:
                raise ValidationError(
                    _("La capacité adultes d'une chambre doit être d'au "
                      "moins 1."))
