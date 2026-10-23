# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import AccessError
from odoo.tools import format_amount

# Champ de l'écran → champ de la société (barème et seuils, par société).
_COMPANY_FIELDS = {
    'rate_per_1000': 'aite_loyalty_rate_per_1000',
    'min_amount': 'aite_loyalty_min_amount',
    'window_months': 'aite_loyalty_window_months',
    'vip_min_spend': 'aite_loyalty_vip_min_spend',
    'vip_min_visits': 'aite_loyalty_vip_min_visits',
    'vvip_min_spend': 'aite_loyalty_vvip_min_spend',
    'vvip_min_visits': 'aite_loyalty_vvip_min_visits',
    'vvip_min_domains': 'aite_loyalty_vvip_min_domains',
}


class LoyaltyBaremeWizard(models.TransientModel):
    """
    Barème de fidélité — écran du Responsable (Hôtel → Fidélité →
    Configuration → Barème).

    Le barème vit sur la société et s'éditait seulement dans Paramètres →
    AITE Fidélité, que seule l'administration ouvre : la directrice (profil
    Responsable) ne l'atteignait pas. Cet écran lit le barème en vigueur et
    l'enregistre sur la société, en ``sudo()`` : le Responsable n'a pas (et
    n'a pas à avoir) le droit de modifier la fiche société ; l'accès à
    l'écran est réservé au profil Responsable (droits d'accès du modèle).
    """
    _name = 'aite.loyalty.bareme.wizard'
    _description = "Barème de fidélité"

    company_id = fields.Many2one(
        'res.company', string="Société", required=True, readonly=True,
        default=lambda self: self.env.company)
    currency_id = fields.Many2one(related='company_id.currency_id')

    rate_per_1000 = fields.Float(
        string="Points par 1 000", digits=(6, 2),
        help="Points gagnés par tranche de 1 000 de la devise.")
    min_amount = fields.Monetary(
        string="Montant minimum par transaction",
        currency_field='currency_id',
        help="En dessous, la transaction ne rapporte aucun point.")
    window_months = fields.Integer(
        string="Fenêtre de calcul (mois)",
        help="Période glissante sur laquelle le statut est calculé.")
    vip_min_spend = fields.Monetary(
        string="VIP — dépenses min.", currency_field='currency_id')
    vip_min_visits = fields.Integer(string="VIP — visites min.")
    vvip_min_spend = fields.Monetary(
        string="VVIP — dépenses min.", currency_field='currency_id')
    vvip_min_visits = fields.Integer(string="VVIP — visites min.")
    vvip_min_domains = fields.Integer(
        string="VVIP — familles de services min.",
        help="Familles distinctes utilisées : bar & restaurant, "
             "hébergement, SPA, coiffure, pressing, espaces réservés, "
             "autres prestations.")

    summary = fields.Text(
        string="Ce qui va se passer", compute='_compute_summary')

    @api.model
    def default_get(self, fields_list):
        """Pré-remplit l'écran avec le barème en vigueur de la société."""
        res = super().default_get(fields_list)
        company = self.env['res.company'].browse(
            res.get('company_id') or self.env.company.id)
        for wizard_field, company_field in _COMPANY_FIELDS.items():
            if wizard_field in fields_list:
                res[wizard_field] = company[company_field]
        return res

    @api.depends('company_id', *_COMPANY_FIELDS)
    def _compute_summary(self):
        for wiz in self:
            cur = wiz.currency_id or wiz.company_id.currency_id

            def amount(value):
                return format_amount(self.env, value or 0.0, cur)

            example = 25000.0
            points = self.env['aite.loyalty.engine']._points_for(
                example, wiz.rate_per_1000, wiz.min_amount)
            wiz.summary = _(
                "Une note de %(ex)s rapporte %(pts)s point(s) ; sous "
                "%(min)s, aucun point. Chaque jour, le statut est recalculé "
                "sur les %(win)s derniers mois : VIP à partir de %(vs)s "
                "dépensés et %(vv)s visites ; VVIP à partir de %(xs)s, "
                "%(xv)s visites et %(xd)s familles de services.",
                ex=amount(example), pts=points, min=amount(wiz.min_amount),
                win=wiz.window_months, vs=amount(wiz.vip_min_spend),
                vv=wiz.vip_min_visits, xs=amount(wiz.vvip_min_spend),
                xv=wiz.vvip_min_visits, xd=wiz.vvip_min_domains)

    def action_save(self):
        self.ensure_one()
        if not self.env.user.has_group(
                'aite_hotel_management.group_hotel_manager'):
            raise AccessError(_(
                "Le barème de fidélité est réservé au profil Responsable."))
        self.company_id.sudo().write({
            company_field: self[wizard_field]
            for wizard_field, company_field in _COMPANY_FIELDS.items()
        })
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'type': 'success',
                'message': _("Barème de fidélité enregistré. Les statuts "
                             "se recalculent lors du prochain passage "
                             "quotidien."),
                'next': {'type': 'ir.actions.act_window_close'},
            },
        }
