# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class PosSession(models.Model):
    """
    Agrégats analytiques au niveau session POS et classification de la
    sévérité des écarts de caisse.

    Le champ natif ``cash_register_difference`` capture l'écart entre le
    montant théorique attendu en caisse et le montant réellement compté
    par le caissier à la clôture. On l'enrichit ici d'un classement
    métier (modéré / élevé / critique / excédent) utilisable pour
    déclencher des alertes, filtrer les vues, et colorer le dashboard.

    Les seuils sont définis comme des constantes de classe pour faciliter
    leur surcharge dans un module dérivé (overlay client).
    """
    _inherit = 'pos.session'

    # Seuils en valeur absolue de la devise de la session — par défaut
    # calibrés pour le FCFA, à surcharger si besoin pour d'autres
    # contextes (EUR, USD, ...).
    DISCREPANCY_THRESHOLD_HIGH = 200_000.0   # au-delà → critique
    DISCREPANCY_THRESHOLD_MED = 100_000.0    # au-delà → élevé

    # --- Agrégats CA / Marge / CMV ---

    total_ca = fields.Monetary(
        string="CA",
        compute='_compute_session_aggregates',
        store=True,
        currency_field='currency_id',
    )
    total_cost = fields.Monetary(
        string="CMV total",
        compute='_compute_session_aggregates',
        store=True,
        currency_field='currency_id',
    )
    total_margin = fields.Monetary(
        string="Marge totale",
        compute='_compute_session_aggregates',
        store=True,
        currency_field='currency_id',
    )
    margin_rate = fields.Float(
        string="Taux de marge (%)",
        compute='_compute_session_aggregates',
        store=True,
        digits=(5, 2),
    )
    order_count_computed = fields.Integer(
        string="Nb commandes",
        compute='_compute_session_aggregates',
        store=True,
    )
    total_qty = fields.Float(
        string="Qté totale vendue",
        compute='_compute_session_aggregates',
        store=True,
        digits=(12, 2),
    )
    average_basket = fields.Monetary(
        string="Panier moyen",
        compute='_compute_session_aggregates',
        store=True,
        currency_field='currency_id',
    )

    # --- Classification écart de caisse ---

    cash_discrepancy_severity = fields.Selection(
        selection=[
            ('none', _("Aucun écart")),
            ('over', _("Excédent")),
            ('low', _("Modéré")),
            ('med', _("Élevé")),
            ('high', _("Critique")),
        ],
        string="Sévérité écart caisse",
        compute='_compute_cash_discrepancy_severity',
        store=True,
        index=True,
        help="Classification métier de l'écart entre montant théorique "
             "et montant compté à la clôture de la session.",
    )

    @api.depends(
        'order_ids.total_cost',
        'order_ids.total_margin',
        'order_ids.amount_total',
        'order_ids.lines.qty',
        'order_ids.state',
    )
    def _compute_session_aggregates(self):
        for session in self:
            # On exclut les commandes annulées/abandonnées.
            valid_orders = session.order_ids.filtered(
                lambda o: o.state in ('paid', 'done', 'invoiced')
            )
            session.total_ca = sum(valid_orders.mapped('amount_total'))
            session.total_cost = sum(valid_orders.mapped('total_cost'))
            session.total_margin = sum(valid_orders.mapped('total_margin'))
            session.order_count_computed = len(valid_orders)
            session.total_qty = sum(valid_orders.mapped('lines.qty'))
            session.margin_rate = (
                (session.total_margin / session.total_ca * 100.0)
                if session.total_ca else 0.0
            )
            session.average_basket = (
                (session.total_ca / session.order_count_computed)
                if session.order_count_computed else 0.0
            )

    @api.depends('cash_register_difference', 'state',
                 'cash_register_balance_end_real',
                 'cash_register_balance_start',
                 'cash_real_transaction', 'payment_method_ids',
                 'order_ids.payment_ids.amount')
    def _compute_cash_discrepancy_severity(self):
        # ``cash_register_difference`` est calculé et NON stocké, et son
        # ``@api.depends`` natif omet ``cash_register_balance_end_real``
        # — précisément le montant que le caissier saisit en comptant sa
        # caisse. S'y fier laissait la sévérité figée sur l'état d'avant
        # clôture : un manquant de 250 000 restait classé d'après l'écart
        # qui précédait le comptage. On refait donc la soustraction sur
        # les deux termes, tous deux à jour au moment du recalcul.
        #
        # La garde d'Odoo est reprise telle quelle : sans moyen de
        # paiement espèces, la caisse n'a pas de solde et il n'y a pas
        # d'écart à classer.
        for session in self:
            if session.payment_method_ids.filtered('is_cash_count'):
                diff = (session.cash_register_balance_end_real
                        - session.cash_register_balance_end)
            else:
                diff = 0.0
            if diff == 0.0:
                session.cash_discrepancy_severity = 'none'
            elif diff > 0:
                # Excédent : moins critique mais à investiguer
                session.cash_discrepancy_severity = 'over'
            else:
                abs_diff = abs(diff)
                if abs_diff >= self.DISCREPANCY_THRESHOLD_HIGH:
                    session.cash_discrepancy_severity = 'high'
                elif abs_diff >= self.DISCREPANCY_THRESHOLD_MED:
                    session.cash_discrepancy_severity = 'med'
                else:
                    session.cash_discrepancy_severity = 'low'
