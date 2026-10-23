# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class CityTaxRate(models.Model):
    """
    Barème de taxe de séjour.

    Une ligne = un montant par nuitée pour un pays et une catégorie
    d'établissement (étoiles). Le montant s'applique soit **par personne et
    par nuit** (Cameroun, Guinée), soit **par chambre et par nuit** (barème
    communal ivoirien) — c'est la « base » du barème.

    Les barèmes officiels sont livrés en données ; l'hôtelier n'a rien à
    saisir, mais peut corriger un montant si la loi de finances change.
    """
    _name = 'aite.city.tax.rate'
    _description = "Barème de taxe de séjour"
    _order = 'country_id, stars desc'
    # Le libellé n'est plus stocké : la recherche par nom passe par le pays.
    _rec_names_search = ['country_id']

    # Libellé calculé à l'affichage, pas stocké : stocké, il restait figé
    # dans la langue et la devise de l'installation (« Cameroon — 3 ★ :
    # 3 000 XAF », ECARTS n° 39). Calculé à la lecture, il suit la langue
    # de l'utilisateur (pays traduit) et le symbole de la devise (« FCFA »).
    name = fields.Char(string="Libellé", compute='_compute_name')
    country_id = fields.Many2one(
        'res.country', string="Pays", required=True, index=True,
        ondelete='restrict',
    )
    stars = fields.Selection(
        selection=[
            ('0', "Non classé / meublé"),
            ('1', "1 ★"), ('2', "2 ★"), ('3', "3 ★"),
            ('4', "4 ★"), ('5', "5 ★"),
        ],
        string="Catégorie", required=True, index=True,
        help="Catégorie de l'établissement : la taxe dépend du classement.",
    )
    # Pas d'agrégat : additionner les montants par nuitée de plusieurs
    # catégories (« Cameroun 14 000 » dans la liste groupée par pays) n'a
    # aucun sens (ECARTS n° 57).
    amount = fields.Float(
        string="Montant par nuitée", required=True, digits=(16, 0),
        aggregator=None,
        help="Montant fixe en devise locale, par nuit.",
    )
    currency_id = fields.Many2one(
        'res.currency', string="Devise", required=True,
        help="Devise du barème (XAF, XOF, GNF…).",
    )
    basis = fields.Selection(
        selection=[
            ('person', "Par personne et par nuit"),
            ('room', "Par chambre et par nuit"),
        ],
        string="Base de calcul", required=True, default='person',
        help="Par personne : nuits × (adultes + enfants comptés). "
             "Par chambre : nuits × chambres.",
    )
    count_children = fields.Boolean(
        string="Compter les enfants",
        help="Décoché : seuls les adultes sont taxés.",
    )
    legal_reference = fields.Char(
        string="Référence légale",
        help="Texte qui fixe ce montant (loi de finances, article du CGI…). "
             "Information affichée sur l'état mensuel.",
    )
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('country_stars_uniq', 'unique(country_id, stars)',
         "Il existe déjà un barème pour ce pays et cette catégorie."),
    ]

    @api.depends('country_id.name', 'stars', 'amount', 'currency_id.symbol')
    @api.depends_context('lang')
    def _compute_name(self):
        labels = dict(self._fields['stars'].selection)
        for rate in self:
            rate.name = "%s — %s : %s %s" % (
                rate.country_id.name or "?",
                labels.get(rate.stars, "?"),
                "{:,.0f}".format(rate.amount or 0).replace(",", " "),
                rate.currency_id.symbol or "",
            )

    @api.depends('name')
    @api.depends_context('lang')
    def _compute_display_name(self):
        # Le nom affiché suit le libellé, donc la langue de l'utilisateur.
        super()._compute_display_name()

    # ------------------------------------------------------------------
    # Barème ajouté, modifié ou archivé : les hôtels suivent
    # ------------------------------------------------------------------

    @api.model_create_multi
    def create(self, vals_list):
        rates = super().create(vals_list)
        self._recompute_hotel_rates()
        return rates

    def write(self, vals):
        res = super().write(vals)
        if {'country_id', 'stars', 'active'} & set(vals):
            self._recompute_hotel_rates()
        return res

    def unlink(self):
        res = super().unlink()
        self._recompute_hotel_rates()
        return res

    @api.model
    def _recompute_hotel_rates(self):
        """
        Fait recalculer le « Barème appliqué » de tous les hôtels.

        Ce champ stocké dépend du pays et de la catégorie de l'hôtel, pas
        de la table des barèmes : un hôtel créé avant l'installation du
        module (cas d'une mise à jour en production) était calculé avant
        le chargement des barèmes et restait sans taxe, l'écran disant
        « Aucun barème connu » (ECARTS n° 73). Même chose pour un barème
        ajouté ensuite pour un nouveau pays. Les barèmes livrés passent
        par ``create`` au chargement des données : l'installation est
        couverte sans crochet d'installation. ``sudo`` : recalcul
        technique, quels que soient les hôtels visibles de l'utilisateur.
        """
        hotels = self.env['aite.hotel.hotel'].sudo().with_context(
            active_test=False).search([])
        if hotels:
            self.env.add_to_compute(hotels._fields['city_tax_rate_id'], hotels)

    @api.constrains('amount')
    def _check_amount(self):
        for rate in self:
            if rate.amount < 0:
                raise ValidationError(
                    _("Le montant d'une taxe de séjour ne peut pas être "
                      "négatif."))

    # ------------------------------------------------------------------
    # Moteur de calcul — fonctions pures, testables sans base de données
    # ------------------------------------------------------------------

    @staticmethod
    def _taxable_units(basis, nights, adults, children, count_children,
                       rooms=1):
        """
        Nombre d'unités taxables d'une chambre sur un séjour.

        * ``person`` : nuits × (adultes [+ enfants]).
        * ``room``   : nuits × chambres.

        Les valeurs négatives ou absentes comptent pour zéro ; une nuit
        minimum est toujours facturée (day-use = 1 nuitée, comme le PMS).
        """
        nights = max(1, int(nights or 0))
        if basis == 'room':
            return nights * max(1, int(rooms or 1))
        persons = max(0, int(adults or 0))
        if count_children:
            persons += max(0, int(children or 0))
        return nights * persons

    @staticmethod
    def _tax_amount(amount, units):
        """Montant de taxe = montant unitaire × unités, jamais négatif."""
        return max(0.0, float(amount or 0.0)) * max(0, int(units or 0))

    @api.model
    def _find_rate(self, country, stars):
        """
        Barème applicable à un hôtel : celui de son pays et de sa catégorie.

        Un hôtel « non classé » (étoiles vides) tombe sur la ligne
        « 0 — Non classé » du pays. Renvoie un recordset vide si le pays n'a
        pas de barème : la taxe n'est alors simplement pas appliquée.
        """
        if not country:
            return self.browse()
        return self.search([
            ('country_id', '=', country.id),
            ('stars', '=', stars or '0'),
        ], limit=1)
