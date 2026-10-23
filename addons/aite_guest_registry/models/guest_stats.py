# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools


class GuestStats(models.Model):
    """
    Statistiques d'hébergement (format ministère du Tourisme).

    Une ligne par fiche d'enregistrement, datée du mois d'arrivée. En pivot
    mois × hôtel on obtient : arrivées (nombre de fiches), nuitées
    (somme des nuits), résidents / non-résidents, répartition par
    nationalité et par motif. La durée moyenne de séjour n'est pas une
    mesure : elle se déduit (nuitées ÷ arrivées).
    """
    _name = 'aite.guest.stats'
    _description = "Statistiques d'hébergement (MINTOUL)"
    _auto = False
    _order = 'arrival_date desc'
    _rec_name = 'registration_id'

    registration_id = fields.Many2one(
        'aite.guest.registration', string="Fiche", readonly=True)
    reservation_id = fields.Many2one(
        'aite.hotel.reservation', string="Réservation", readonly=True)
    hotel_id = fields.Many2one('aite.hotel.hotel', string="Hôtel", readonly=True)
    company_id = fields.Many2one('res.company', string="Société", readonly=True)
    arrival_date = fields.Date(string="Arrivée", readonly=True)
    departure_date = fields.Date(string="Départ", readonly=True)
    # Mois technique (AAAA-MM), gardé pour les exports. Les vues regroupent
    # sur ``arrival_date:month`` : « octobre 2026 » plutôt que « 2026-10 »
    # (ECARTS n° 4).
    month = fields.Char(string="Mois (AAAA-MM)", readonly=True)
    nationality_id = fields.Many2one(
        'res.country', string="Nationalité", readonly=True)
    residence_country_id = fields.Many2one(
        'res.country', string="Pays de résidence", readonly=True)
    resident_type = fields.Selection(
        selection=[('resident', "Résident"), ('non_resident', "Non-résident")],
        string="Type", readonly=True,
    )
    purpose = fields.Selection(
        selection=[
            ('leisure', "Loisirs / tourisme"), ('business', "Affaires"),
            ('conference', "Séminaire / conférence"), ('transit', "Transit"),
            ('family', "Visite familiale"), ('other', "Autre"),
        ],
        string="Motif", readonly=True,
    )
    gender = fields.Selection(
        selection=[('m', "Masculin"), ('f', "Féminin")], string="Sexe",
        readonly=True)
    arrivals = fields.Integer(string="Arrivées", readonly=True)
    nights = fields.Integer(string="Nuitées", readonly=True)
    reservation_state = fields.Selection(
        selection=[
            ('draft', "Brouillon"), ('confirmed', "Confirmée"),
            ('checked_in', "Arrivé"), ('checked_out', "Parti"),
            ('cancelled', "Annulée"), ('no_show', "Non présenté"),
        ],
        string="Séjour", readonly=True,
    )

    @api.model
    def _search(self, domain, offset=0, limit=None, order=None):
        self.env['aite.guest.registration'].flush_model()
        return super()._search(domain, offset=offset, limit=limit, order=order)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None,
                   orderby=False, lazy=True):
        self.env['aite.guest.registration'].flush_model()
        return super().read_group(domain, fields, groupby, offset=offset,
                                  limit=limit, orderby=orderby, lazy=lazy)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f"""
            CREATE OR REPLACE VIEW {self._table} AS (
                SELECT
                    g.id                                    AS id,
                    g.id                                    AS registration_id,
                    g.reservation_id                        AS reservation_id,
                    g.hotel_id                              AS hotel_id,
                    g.company_id                            AS company_id,
                    g.arrival_date                          AS arrival_date,
                    g.departure_date                        AS departure_date,
                    to_char(g.arrival_date, 'YYYY-MM')      AS month,
                    g.nationality_id                        AS nationality_id,
                    g.country_id                            AS residence_country_id,
                    CASE WHEN g.is_resident THEN 'resident'
                         ELSE 'non_resident' END            AS resident_type,
                    g.purpose                               AS purpose,
                    g.gender                                AS gender,
                    1                                       AS arrivals,
                    COALESCE(g.nights, 0)                   AS nights,
                    r.state                                 AS reservation_state
                FROM aite_guest_registration g
                JOIN aite_hotel_reservation r ON r.id = g.reservation_id
                WHERE r.state IN ('checked_in', 'checked_out')
            )
        """)
