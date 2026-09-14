# -*- coding: utf-8 -*-
import re

from odoo import fields, models, tools


class PosDailyReport(models.Model):
    """
    Vue SQL d'analyse quotidienne du POS.

    Agrège ligne par ligne POS avec marge et CMV, regroupable par
    catégorie produit, point de vente, caissier, session, période.
    Sert de socle aux vues pivot/graph et au dashboard OWL.
    """
    _name = 'aite.pos.daily.report'
    _description = "POS Analytics - Rapport quotidien"
    _auto = False
    _order = 'date desc'
    _rec_name = 'date'

    date = fields.Datetime(string="Date", readonly=True)
    session_id = fields.Many2one('pos.session', string="Session", readonly=True)
    order_id = fields.Many2one('pos.order', string="Commande", readonly=True)
    config_id = fields.Many2one('pos.config', string="Point de vente", readonly=True)
    user_id = fields.Many2one('res.users', string="Caissier", readonly=True)
    product_id = fields.Many2one('product.product', string="Article", readonly=True)
    categ_id = fields.Many2one(
        'product.category',
        string="Catégorie produit",
        readonly=True,
        help="Catégorie produit interne (product.category). "
             "Toujours renseignée (au minimum la catégorie par défaut 'All').",
    )
    company_id = fields.Many2one('res.company', string="Société", readonly=True)
    currency_id = fields.Many2one('res.currency', string="Devise", readonly=True)

    qty = fields.Float(string="Quantité", readonly=True, digits=(12, 2))
    price_subtotal = fields.Monetary(
        string="CA HT", readonly=True, currency_field='currency_id'
    )
    price_subtotal_incl = fields.Monetary(
        string="CA TTC", readonly=True, currency_field='currency_id'
    )
    total_cost = fields.Monetary(
        string="CMV", readonly=True, currency_field='currency_id'
    )
    margin = fields.Monetary(
        string="Marge", readonly=True, currency_field='currency_id'
    )
    margin_rate = fields.Float(
        string="Taux marge (%)", readonly=True, digits=(5, 2),
        # Odoo 18 : 'group_operator' est déprécié au profit de 'aggregator'.
        aggregator='avg',
    )

    # Dimensions temporelles dérivées (pour filtres heure / jour de semaine
    # et heatmap). Calculées en SQL à partir de ``po.date_order``.
    hour = fields.Integer(
        string="Heure", readonly=True,
        help="Heure de la commande (0-23), en heure locale serveur.",
    )
    dow = fields.Integer(
        string="Jour de semaine", readonly=True,
        help="Jour de la semaine ISO : 1 = lundi … 7 = dimanche.",
    )

    def init(self):
        """
        Crée / recrée la vue SQL.

        Notes de compatibilité Odoo 17+ :

        * ``pos.order.currency_id`` n'est plus une colonne stockée
          (devenue ``related`` non-stocké). On récupère la devise via
          une jointure sur ``res_company`` — source stable.

        * On utilise ``product.template.categ_id`` (catégorie produit
          interne, Many2one direct) au lieu de ``pos_categ_ids``
          (Many2many sur catégorie POS). Avantages :
            - Toujours renseignée (champ obligatoire dans Odoo)
            - Jointure SQL directe, pas de sous-select sur table pivot
            - Cohérence avec la compta et l'inventaire

        Fuseau horaire :
          ``date_order`` est stocké en UTC. Pour que les filtres « heure »
          et la heatmap reflètent l'heure LOCALE d'exploitation, on
          convertit vers le fuseau de l'utilisateur courant
          (``self.env.user.tz``) avec repli sur ``UTC``. Le fuseau est
          résolu à la création de la vue ; il suffit de mettre à jour le
          module si le fuseau du parc change.
        """
        # Fuseau local d'exploitation (repli UTC si non défini).
        tz = self.env.user.tz or 'UTC'
        # Garde-fou : on n'autorise que des identifiants de fuseau plausibles
        # (lettres, chiffres, '/', '_', '+', '-') pour éviter toute injection
        # via un tz forgé. Repli UTC sinon.
        if not re.match(r'^[A-Za-z0-9_/+\-]+$', tz):
            tz = 'UTC'

        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f"""
            CREATE OR REPLACE VIEW {self._table} AS (
                SELECT
                    pol.id                          AS id,
                    po.date_order                   AS date,
                    po.session_id                   AS session_id,
                    pol.order_id                    AS order_id,
                    po.config_id                    AS config_id,
                    po.user_id                      AS user_id,
                    pol.product_id                  AS product_id,
                    pt.categ_id                     AS categ_id,
                    po.company_id                   AS company_id,
                    rc.currency_id                  AS currency_id,
                    pol.qty                         AS qty,
                    pol.price_subtotal              AS price_subtotal,
                    pol.price_subtotal_incl         AS price_subtotal_incl,
                    pol.total_cost                  AS total_cost,
                    pol.margin                      AS margin,
                    pol.margin_rate                 AS margin_rate,
                    EXTRACT(HOUR FROM (po.date_order AT TIME ZONE 'UTC'
                            AT TIME ZONE %(tz)s))::int      AS hour,
                    EXTRACT(ISODOW FROM (po.date_order AT TIME ZONE 'UTC'
                            AT TIME ZONE %(tz)s))::int      AS dow
                FROM pos_order_line pol
                INNER JOIN pos_order po
                    ON po.id = pol.order_id
                INNER JOIN product_product pp
                    ON pp.id = pol.product_id
                INNER JOIN product_template pt
                    ON pt.id = pp.product_tmpl_id
                INNER JOIN res_company rc
                    ON rc.id = po.company_id
                WHERE po.state IN ('paid', 'done', 'invoiced')
            )
        """, {'tz': tz})
