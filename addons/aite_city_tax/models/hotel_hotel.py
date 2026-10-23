# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class HotelHotel(models.Model):
    """
    L'hôtel porte le réglage de la taxe de séjour : activée ou non, et le
    barème qui en découle (pays + catégorie). Tout est calculé ; le gérant
    ne saisit que la catégorie, qu'il connaît déjà.
    """
    _inherit = 'aite.hotel.hotel'

    city_tax_enabled = fields.Boolean(
        string="Collecter la taxe de séjour", default=True,
        help="Décochez si l'établissement est exonéré. Les séjours déjà "
             "facturés ne sont pas modifiés.",
    )
    city_tax_rate_id = fields.Many2one(
        'aite.city.tax.rate', string="Barème appliqué",
        compute='_compute_city_tax_rate', store=True,
        help="Déduit du pays de l'hôtel et de sa catégorie. Vide = aucun "
             "barème connu pour ce pays : la taxe n'est pas appliquée.",
    )
    city_tax_amount = fields.Float(
        related='city_tax_rate_id.amount', string="Montant par nuitée",
        readonly=True,
    )
    city_tax_basis = fields.Selection(
        related='city_tax_rate_id.basis', string="Base", readonly=True,
    )
    city_tax_help = fields.Char(
        string="Explication", compute='_compute_city_tax_help',
        help="Phrase lisible qui résume ce qui sera facturé.",
    )
    city_tax_product_id = fields.Many2one(
        'product.product', string="Article « Taxe de séjour »",
        readonly=True, copy=False,
        help="Article de service, sans TVA, utilisé sur le folio et la "
             "facture. Créé automatiquement.",
    )

    @api.depends('country_id', 'stars', 'city_tax_enabled')
    def _compute_city_tax_rate(self):
        Rate = self.env['aite.city.tax.rate']
        for hotel in self:
            if not hotel.city_tax_enabled:
                hotel.city_tax_rate_id = False
                continue
            hotel.city_tax_rate_id = Rate._find_rate(
                hotel.country_id, hotel.stars)

    @api.depends('city_tax_rate_id.amount', 'city_tax_rate_id.basis',
                 'city_tax_rate_id.currency_id', 'city_tax_enabled',
                 'country_id.name')
    @api.depends_context('lang')
    def _compute_city_tax_help(self):
        for hotel in self:
            if not hotel.city_tax_enabled:
                hotel.city_tax_help = _(
                    "Taxe de séjour désactivée : aucune ligne ne sera "
                    "ajoutée aux folios.")
            elif not hotel.country_id:
                hotel.city_tax_help = _(
                    "Renseignez le pays de l'hôtel pour appliquer le "
                    "barème officiel.")
            elif not hotel.city_tax_rate_id:
                # Chemin réel du menu (ECARTS n° 46) : menus.xml.
                hotel.city_tax_help = _(
                    "Aucun barème connu pour %s : ajoutez-le dans "
                    "Hôtel → Configuration → Barèmes de taxe de séjour.",
                    hotel.country_id.name)
            else:
                rate = hotel.city_tax_rate_id
                basis = (_("par personne et par nuit")
                         if rate.basis == 'person'
                         else _("par chambre et par nuit"))
                # Le symbole de la devise (« FCFA »), pas son code ISO
                # (« XAF ») : règle 6, montants en FCFA (ECARTS n° 7).
                hotel.city_tax_help = _(
                    "Chaque séjour portera une ligne « Taxe de séjour » de "
                    "%(amount)s %(cur)s %(basis)s, hors TVA.",
                    amount="{:,.0f}".format(rate.amount).replace(",", " "),
                    cur=rate.currency_id.symbol, basis=basis)

    # ------------------------------------------------------------------
    # Article de service dédié (sans TVA)
    # ------------------------------------------------------------------

    def _get_city_tax_product(self):
        """
        Article « Taxe de séjour » de l'hôtel, créé à la volée.

        Sans taxe de vente : la taxe de séjour n'entre pas dans la base de
        TVA. Le compte comptable peut être ajusté par le comptable sur
        l'article (compte de tiers « taxe collectée » recommandé).
        """
        self.ensure_one()
        if self.city_tax_product_id:
            return self.city_tax_product_id
        # ``sudo`` : l'article et son rattachement à l'hôtel sont des
        # écritures techniques (comme l'article des types de chambre). La
        # réception n'a que la lecture sur l'hôtel, le responsable n'a pas
        # la création d'articles : sans ``sudo``, la première confirmation
        # d'une base sans article échouait (ECARTS n° 11).
        categ = self.env.ref(
            'aite_hotel_management.product_category_hotel',
            raise_if_not_found=False)
        product = self.env['product.product'].sudo().create({
            'name': _("Taxe de séjour — %s", self.name),
            'type': 'service',
            'invoice_policy': 'order',
            'list_price': 0.0,
            'sale_ok': False,
            'purchase_ok': False,
            'taxes_id': [(6, 0, [])],
            'categ_id': categ.id if categ else False,
            'company_id': self.company_id.id,
        })
        self.sudo().city_tax_product_id = product.id
        return product.with_env(self.env)

    def write(self, vals):
        res = super().write(vals)
        # Le barème change (pays, étoiles, activation) : resynchroniser
        # les folios encore ouverts pour qu'ils reflètent la règle.
        if {'country_id', 'stars', 'city_tax_enabled'} & set(vals):
            folios = self.env['aite.hotel.folio'].search([
                ('hotel_id', 'in', self.ids),
                ('state', '=', 'open'),
                ('move_id', '=', False),
            ])
            folios._sync_city_tax_line()
        return res
