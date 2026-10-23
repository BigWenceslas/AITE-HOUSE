# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class GuestRegistration(models.Model):
    """
    Fiche d'enregistrement d'un occupant (« fiche de police »).

    Une fiche par personne hébergée, rattachée à la chambre du séjour. La
    première fiche est créée automatiquement au check-in à partir de la
    fiche client ; la réception complète les autres occupants dans la
    même fenêtre. Les champs reprennent ceux exigés par les registres
    hôteliers (nom, prénoms, naissance, nationalité, pièce, adresse,
    provenance / destination, dates) pour être exportables tels quels.
    """
    _name = 'aite.guest.registration'
    _description = "Fiche d'enregistrement client"
    _inherit = ['mail.thread']
    _order = 'arrival_date desc, id desc'

    name = fields.Char(
        string="N° de fiche", required=True, copy=False, readonly=True,
        index=True, default=lambda self: _("Nouveau"),
    )
    reservation_id = fields.Many2one(
        'aite.hotel.reservation', string="Réservation", required=True,
        ondelete='cascade', index=True,
    )
    reservation_line_id = fields.Many2one(
        'aite.hotel.reservation.line', string="Chambre du séjour",
        domain="[('reservation_id', '=', reservation_id)]",
        ondelete='set null',
    )
    room_id = fields.Many2one(
        related='reservation_line_id.room_id', string="Chambre",
        store=True, readonly=True,
    )
    hotel_id = fields.Many2one(
        related='reservation_id.hotel_id', store=True, readonly=True,
        index=True,
    )
    company_id = fields.Many2one(
        related='reservation_id.company_id', store=True, readonly=True,
    )
    partner_id = fields.Many2one(
        'res.partner', string="Fiche client liée",
        help="Contact Odoo de l'occupant (le client principal, ou un "
             "contact créé pour lui). Facultatif pour un accompagnant.",
    )
    is_main_guest = fields.Boolean(
        string="Client principal",
        help="La personne au nom de qui la réservation est faite.",
    )

    # --- Identité --------------------------------------------------------
    last_name = fields.Char(string="Nom", required=True)
    first_name = fields.Char(string="Prénom(s)")
    gender = fields.Selection(
        selection=[('m', "Masculin"), ('f', "Féminin")], string="Sexe",
    )
    birth_date = fields.Date(string="Date de naissance")
    birth_place = fields.Char(string="Lieu de naissance")
    nationality_id = fields.Many2one(
        'res.country', string="Nationalité", index=True,
    )
    profession = fields.Char(string="Profession")

    # --- Pièce d'identité ------------------------------------------------
    id_type = fields.Selection(
        selection=[
            ('cni', "Carte nationale d'identité"),
            ('passport', "Passeport"),
            ('permit', "Permis de conduire"),
            ('residence', "Carte de séjour"),
            ('other', "Autre"),
        ],
        string="Type de pièce",
    )
    id_number = fields.Char(string="N° de pièce")
    id_issued_on = fields.Date(string="Délivrée le")
    id_issued_by = fields.Char(string="Délivrée par")
    id_expires_on = fields.Date(string="Expire le")
    id_image = fields.Image(
        string="Photo de la pièce", max_width=1920, max_height=1920,
        help="Photographiez la pièce avec la tablette ou le téléphone.",
    )

    # --- Adresse & déplacement -------------------------------------------
    address = fields.Char(string="Adresse / domicile")
    country_id = fields.Many2one(
        'res.country', string="Pays de résidence", index=True,
        help="Sert à distinguer résidents et non-résidents dans les "
             "statistiques.",
    )
    phone = fields.Char(string="Téléphone")
    email = fields.Char(string="E-mail")
    coming_from = fields.Char(
        string="Provenance", help="Ville ou pays d'où arrive le client.")
    going_to = fields.Char(
        string="Destination", help="Prochaine étape après le séjour.")
    purpose = fields.Selection(
        selection=[
            ('leisure', "Loisirs / tourisme"),
            ('business', "Affaires"),
            ('conference', "Séminaire / conférence"),
            ('transit', "Transit"),
            ('family', "Visite familiale"),
            ('other', "Autre"),
        ],
        string="Motif du séjour", default='leisure',
    )

    # --- Séjour ------------------------------------------------------------
    arrival_date = fields.Date(
        string="Arrivée", compute='_compute_stay_dates', store=True,
        readonly=False, index=True,
    )
    departure_date = fields.Date(
        string="Départ", compute='_compute_stay_dates', store=True,
        readonly=False, index=True,
    )
    nights = fields.Integer(
        string="Nuits", compute='_compute_nights', store=True,
    )
    is_resident = fields.Boolean(
        string="Résident", compute='_compute_is_resident', store=True,
        help="Réside dans le pays de l'hôtel (statistiques MINTOUL).",
    )

    # --- État ---------------------------------------------------------------
    state = fields.Selection(
        selection=[
            ('draft', "À compléter"),
            ('done', "Complète"),
        ],
        string="Fiche", default='draft', required=True, index=True,
        copy=False, tracking=True,
    )
    missing_info = fields.Char(
        string="Il manque", compute='_compute_missing_info',
        help="Ce qu'il reste à renseigner pour que la fiche soit "
             "complète.",
    )
    signed = fields.Boolean(
        string="Signée par le client",
        help="Cochez après signature de la fiche imprimée (ou "
             "validation à l'écran).",
    )
    note = fields.Char(string="Observation")

    # ------------------------------------------------------------------
    # Compute
    # ------------------------------------------------------------------

    @api.depends('reservation_id.checkin_date', 'reservation_id.checkout_date')
    def _compute_stay_dates(self):
        for reg in self:
            res = reg.reservation_id
            if res.checkin_date and not reg.arrival_date:
                reg.arrival_date = res.checkin_date.date()
            if res.checkout_date and not reg.departure_date:
                reg.departure_date = res.checkout_date.date()

    @api.depends('arrival_date', 'departure_date')
    def _compute_nights(self):
        for reg in self:
            if reg.arrival_date and reg.departure_date:
                reg.nights = max(
                    1, (reg.departure_date - reg.arrival_date).days)
            else:
                reg.nights = 0

    @api.depends('country_id', 'hotel_id.country_id', 'nationality_id')
    def _compute_is_resident(self):
        for reg in self:
            hotel_country = reg.hotel_id.country_id
            residence = reg.country_id or reg.nationality_id
            reg.is_resident = bool(
                hotel_country and residence and residence == hotel_country)

    REQUIRED_FOR_COMPLETE = (
        ('last_name', "le nom"),
        ('first_name', "le prénom"),
        ('birth_date', "la date de naissance"),
        ('nationality_id', "la nationalité"),
        ('id_type', "le type de pièce"),
        ('id_number', "le numéro de pièce"),
    )

    @staticmethod
    def _missing_labels(values, required=None):
        """
        Liste des libellés manquants dans ``values`` (dict champ → valeur).

        Fonction pure utilisée par le compute et testable sans base.
        """
        required = required or GuestRegistration.REQUIRED_FOR_COMPLETE
        return [label for field, label in required if not values.get(field)]

    @api.depends(*[f for f, _l in REQUIRED_FOR_COMPLETE])
    def _compute_missing_info(self):
        for reg in self:
            values = {f: reg[f] for f, _l in self.REQUIRED_FOR_COMPLETE}
            missing = self._missing_labels(values)
            reg.missing_info = ", ".join(missing) if missing else ""

    def _creation_message(self):
        # Le message standard « %s créé » donnait « Fiche d'enregistrement
        # client créé » dans le fil (accord au masculin, ECARTS n° 43).
        self.ensure_one()
        return _("Fiche d'enregistrement créée")

    @api.depends('last_name', 'first_name')
    def _compute_display_name(self):
        for reg in self:
            full = " ".join(filter(None, [reg.last_name, reg.first_name]))
            reg.display_name = full or reg.name

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _("Nouveau")) == _("Nouveau"):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'aite.guest.registration') or _("Nouveau")
        regs = super().create(vals_list)
        regs._auto_complete_state()
        return regs

    def write(self, vals):
        res = super().write(vals)
        if 'state' not in vals:
            self._auto_complete_state()
        return res

    def _auto_complete_state(self):
        """Dès que tout est renseigné, la fiche passe « Complète » seule."""
        for reg in self:
            complete = not reg.missing_info
            if complete and reg.state == 'draft':
                super(GuestRegistration, reg).write({'state': 'done'})
            elif not complete and reg.state == 'done':
                super(GuestRegistration, reg).write({'state': 'draft'})

    @api.constrains('arrival_date', 'departure_date')
    def _check_dates(self):
        for reg in self:
            if reg.arrival_date and reg.departure_date \
                    and reg.departure_date < reg.arrival_date:
                raise ValidationError(
                    _("La date de départ ne peut pas précéder l'arrivée."))

    # ------------------------------------------------------------------
    # Pré-remplissage depuis la fiche client
    # ------------------------------------------------------------------

    @api.model
    def _name_parts(self, partner):
        """
        (nom, prénom) d'un contact pour la fiche de police.

        Si le contact porte un nom et un prénom distincts (module de
        découpage du nom installé), on les reprend. Sinon, on ne devine
        pas : « Ngo Bikaï Solange » comme « Estelle Ngono » ne se coupent
        pas au premier espace sans risque d'erreur. Le nom complet reste
        dans « Nom », le prénom vide — le bandeau « Il manque » le signale
        à la réception (ECARTS n° 30).
        """
        fields_ = getattr(partner, '_fields', {})
        if 'lastname' in fields_ and 'firstname' in fields_ \
                and (partner.lastname or partner.firstname):
            return (partner.lastname or partner.firstname or "",
                    partner.firstname if partner.lastname else "")
        return (partner.name or "").strip(), ""

    @api.model
    def _vals_from_partner(self, partner, reservation, line=None,
                           main=False):
        """Valeurs d'une fiche pré-remplie depuis un contact Odoo."""
        last_name, first_name = self._name_parts(partner)
        id_map = {'cni': 'cni', 'passport': 'passport',
                  'permit': 'permit', 'other': 'other'}
        return {
            'reservation_id': reservation.id,
            'reservation_line_id': line.id if line else False,
            'partner_id': partner.id,
            'is_main_guest': main,
            'last_name': last_name,
            'first_name': first_name,
            'birth_date': partner.guest_birth_date or False,
            'nationality_id': (partner.nationality_id.id
                               or partner.country_id.id or False),
            'country_id': partner.country_id.id or False,
            'id_type': id_map.get(partner.guest_id_type or '', False),
            'id_number': partner.guest_id_number or False,
            'address': " ".join(filter(None, [
                partner.street, partner.city])) or False,
            'phone': partner.phone or partner.mobile or False,
            'email': partner.email or False,
        }

    def action_copy_back_to_partner(self):
        """
        Met à jour la fiche client Odoo avec la pièce, la nationalité et la
        date de naissance saisies : la prochaine réservation sera
        pré-remplie.
        """
        for reg in self.filtered('partner_id'):
            vals = {}
            if reg.nationality_id:
                vals['nationality_id'] = reg.nationality_id.id
            if reg.birth_date:
                vals['guest_birth_date'] = reg.birth_date
            if reg.id_type and reg.id_type in ('cni', 'passport',
                                               'permit', 'other'):
                vals['guest_id_type'] = reg.id_type
            if reg.id_number:
                vals['guest_id_number'] = reg.id_number
            if vals:
                # ``sudo`` : écriture technique sur le contact (comme le
                # marquage « client hôtel ») — la réception n'a pas, et
                # n'a pas à avoir, la création de contacts (ECARTS n° 14).
                reg.partner_id.sudo().write(vals)
        return True

    def action_mark_signed(self):
        self.write({'signed': True})
        return True

    def action_print_card(self):
        self.ensure_one()
        return self.env.ref(
            'aite_guest_registry.report_registration_card').report_action(self)
