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

    name = fields.Char(
        string="Libellé", compute='_compute_name', store=True,
    )
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
    amount = fields.Float(
        string="Montant par nuitée", required=True, digits=(16, 0),
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

    @api.depends('country_id.name', 'stars', 'amount', 'currency_id.name')
    def _compute_name(self):
        labels = dict(self._fields['stars'].selection)
        for rate in self:
            rate.name = "%s — %s : %s %s" % (
                rate.country_id.name or "?",
                labels.get(rate.stars, "?"),
                "{:,.0f}".format(rate.amount or 0).replace(",", " "),
                rate.currency_id.name or "",
            )

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
