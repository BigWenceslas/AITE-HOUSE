# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools


class CityTaxReport(models.Model):
    """
    État de la taxe de séjour collectée.

    Une ligne par ligne de folio « taxe de séjour », datée du **départ du
    séjour** (fait générateur retenu : la taxe est due sur les nuitées
    consommées ; le départ borne le séjour). Groupable par mois et par
    hôtel : c'est l'état à reporter sur la déclaration mensuelle.

    Les folios annulés sont exclus ; les folios ouverts (séjour en cours)
    sont inclus mais distingués par l'état, pour anticiper le mois.
    """
    _name = 'aite.city.tax.report'
    _description = "Taxe de séjour — état mensuel"
    _auto = False
    _order = 'checkout_date desc'
    _rec_name = 'folio_id'

    folio_id = fields.Many2one('aite.hotel.folio', string="Folio", readonly=True)
    reservation_id = fields.Many2one(
        'aite.hotel.reservation', string="Réservation", readonly=True)
    hotel_id = fields.Many2one('aite.hotel.hotel', string="Hôtel", readonly=True)
    company_id = fields.Many2one('res.company', string="Société", readonly=True)
    currency_id = fields.Many2one('res.currency', string="Devise", readonly=True)
    partner_id = fields.Many2one('res.partner', string="Client", readonly=True)
    checkin_date = fields.Date(string="Arrivée", readonly=True)
    checkout_date = fields.Date(string="Départ", readonly=True)
    month = fields.Char(string="Mois", readonly=True,
                        help="Mois du départ (AAAA-MM) : mois de déclaration.")
    folio_state = fields.Selection(
        selection=[
            ('open', "Séjour en cours"),
            ('invoiced', "Facturé"),
            ('paid', "Soldé"),
        ],
        string="État du folio", readonly=True,
    )
    units = fields.Integer(string="Nuitées taxées", readonly=True)
    amount = fields.Monetary(
        string="Taxe collectée", readonly=True, currency_field='currency_id')

    @api.model
    def _search(self, domain, offset=0, limit=None, order=None):
        """
        Vue SQL : garantir que les lignes de folio calculées en mémoire
        (quantité, montant) sont écrites en base avant de les lire.
        """
        self.env['aite.hotel.folio.line'].flush_model()
        self.env['aite.hotel.folio'].flush_model()
        return super()._search(domain, offset=offset, limit=limit, order=order)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None,
                   orderby=False, lazy=True):
        self.env['aite.hotel.folio.line'].flush_model()
        self.env['aite.hotel.folio'].flush_model()
        return super().read_group(domain, fields, groupby, offset=offset,
                                  limit=limit, orderby=orderby, lazy=lazy)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f"""
            CREATE OR REPLACE VIEW {self._table} AS (
                SELECT
                    fl.id                                   AS id,
                    f.id                                    AS folio_id,
                    f.reservation_id                        AS reservation_id,
                    f.hotel_id                              AS hotel_id,
                    f.company_id                            AS company_id,
                    f.currency_id                           AS currency_id,
                    f.partner_id                            AS partner_id,
                    (f.checkin_date)::date                  AS checkin_date,
                    (f.checkout_date)::date                 AS checkout_date,
                    to_char(f.checkout_date, 'YYYY-MM')     AS month,
                    f.state                                 AS folio_state,
                    COALESCE(fl.city_tax_units, 0)          AS units,
                    COALESCE(fl.price_total, 0)             AS amount
                FROM aite_hotel_folio_line fl
                JOIN aite_hotel_folio f ON f.id = fl.folio_id
                WHERE fl.line_type = 'city_tax'
                  AND f.state IN ('open', 'invoiced', 'paid')
            )
        """)
