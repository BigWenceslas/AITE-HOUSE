# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class HotelFolioLine(models.Model):
    """Troisième type de ligne : la taxe de séjour (hors hébergement)."""
    _inherit = 'aite.hotel.folio.line'

    line_type = fields.Selection(
        selection_add=[('city_tax', "Taxe de séjour")],
        ondelete={'city_tax': 'cascade'},
    )
    is_city_tax = fields.Boolean(
        string="Ligne de taxe de séjour", compute='_compute_is_city_tax',
        store=True, index=True,
    )
    city_tax_units = fields.Integer(
        string="Unités taxées",
        help="Nuitées × personnes (ou × chambres) ayant servi au calcul.",
    )

    @api.depends('line_type')
    def _compute_is_city_tax(self):
        for line in self:
            line.is_city_tax = line.line_type == 'city_tax'


class HotelFolio(models.Model):
    """
    Le folio reçoit une ligne « Taxe de séjour » calculée et entretenue
    automatiquement, au même rythme que les nuitées : confirmation,
    changement de dates, changement de chambre, modification des
    occupants. Jamais après facturation.
    """
    _inherit = 'aite.hotel.folio'

    amount_city_tax = fields.Monetary(
        string="Taxe de séjour", compute='_compute_amount_city_tax',
        store=True, currency_field='currency_id',
        help="Montant collecté pour le compte de l'État sur ce séjour.",
    )
    city_tax_units = fields.Integer(
        string="Nuitées taxées", compute='_compute_amount_city_tax',
        store=True,
    )

    @api.depends('line_ids.price_subtotal', 'line_ids.price_total',
                 'line_ids.line_type', 'payment_ids.amount',
                 'payment_ids.state', 'state')
    def _compute_amounts(self):
        """
        Les « Services (HT) » ne doivent pas inclure la taxe de séjour :
        elle est collectée pour l'État, pas vendue. On la retire après le
        calcul du socle ; les totaux HT/TTC restent inchangés.
        """
        super()._compute_amounts()
        for folio in self:
            city = sum(folio.line_ids.filtered(
                lambda l: l.line_type == 'city_tax').mapped('price_subtotal'))
            if city:
                folio.amount_service -= city

    @api.depends('line_ids.price_total', 'line_ids.line_type',
                 'line_ids.city_tax_units')
    def _compute_amount_city_tax(self):
        for folio in self:
            lines = folio.line_ids.filtered(
                lambda l: l.line_type == 'city_tax')
            folio.amount_city_tax = sum(lines.mapped('price_total'))
            folio.city_tax_units = sum(lines.mapped('city_tax_units'))

    # ------------------------------------------------------------------
    # Synchronisation
    # ------------------------------------------------------------------

    def _sync_room_lines(self):
        """Après les nuitées, la taxe — toujours dans cet ordre."""
        res = super()._sync_room_lines()
        self._sync_city_tax_line()
        return res

    def _compute_city_tax_values(self):
        """
        (montant unitaire, unités, barème) pour ce folio, ou (0, 0, vide)
        si la taxe ne s'applique pas. Fonction sans effet de bord.
        """
        self.ensure_one()
        hotel = self.hotel_id
        rate = hotel.city_tax_rate_id if hotel.city_tax_enabled else False
        if not rate:
            return 0.0, 0, self.env['aite.city.tax.rate']
        Rate = self.env['aite.city.tax.rate']
        units = 0
        for rline in self.reservation_id.line_ids:
            units += Rate._taxable_units(
                rate.basis, rline.nights, rline.adults, rline.children,
                rate.count_children, rooms=1)
        return rate.amount, units, rate

    def _sync_city_tax_line(self):
        """
        Crée, met à jour ou supprime la ligne de taxe de séjour du folio.

        Règles : une seule ligne par folio ; quantité = unités taxables ;
        prix unitaire = montant du barème ; aucune TVA ; libellé qui
        explique le calcul au client comme au comptable. Ne touche à rien
        si le folio est facturé, soldé ou annulé.
        """
        Line = self.env['aite.hotel.folio.line']
        for folio in self:
            if folio.move_id or folio.state in ('invoiced', 'paid',
                                                'cancelled'):
                continue
            existing = folio.line_ids.filtered(
                lambda l: l.line_type == 'city_tax')
            amount, units, rate = folio._compute_city_tax_values()
            if not rate or not units or not amount:
                existing.unlink()
                continue
            basis = (_("personne") if rate.basis == 'person'
                     else _("chambre"))
            name = _(
                "Taxe de séjour — %(units)d nuitée(s) × %(basis)s "
                "(%(stars)s, %(country)s)",
                units=units, basis=basis,
                stars=dict(rate._fields['stars'].selection).get(rate.stars),
                country=rate.country_id.name)
            vals = {
                'line_type': 'city_tax',
                'product_id': folio.hotel_id._get_city_tax_product().id,
                'name': name,
                'quantity': units,
                'price_unit': amount,
                'tax_ids': [(6, 0, [])],
                'city_tax_units': units,
                'date': fields.Date.context_today(self),
            }
            if existing:
                (existing[0]).write(vals)
                (existing[1:]).unlink()
            else:
                vals['folio_id'] = folio.id
                Line.create(vals)
        return True

    def action_refresh_city_tax(self):
        """Bouton de secours : recalculer la taxe de séjour du folio."""
        self._sync_city_tax_line()
        return True


class HotelReservationLine(models.Model):
    """
    Modifier les occupants d'une chambre depuis sa propre fiche doit aussi
    recalculer la taxe (barème « par personne »).
    """
    _inherit = 'aite.hotel.reservation.line'

    def write(self, vals):
        res = super().write(vals)
        if {'adults', 'children'} & set(vals):
            folios = self.mapped('reservation_id.folio_id').filtered(
                lambda f: f.state == 'open' and not f.move_id)
            folios._sync_city_tax_line()
        return res
