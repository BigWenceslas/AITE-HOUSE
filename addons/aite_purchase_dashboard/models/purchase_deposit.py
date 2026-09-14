# -*- coding: utf-8 -*-
from odoo import api, fields, models


class AitePurchaseDeposit(models.Model):
    """
    Suivi des consignes d'emballages chez les fournisseurs (compte 4096).

    Odoo ne suit pas nativement les casiers/bouteilles consignés ; ce petit
    registre — une ligne par fournisseur — chiffre l'argent immobilisé et
    alimente l'onglet « Avoirs & consignes » du tableau de bord. Saisie
    manuelle assumée (v1) : c'est le comptage périodique des casiers qui
    fait foi, comme le veut la pratique (« le 4096 ne se solde jamais sans
    suivi à l'unité »).
    """
    _name = 'aite.purchase.deposit'
    _description = "Consignes d'emballages chez un fournisseur"
    _order = 'value desc, id'
    _rec_name = 'partner_id'

    partner_id = fields.Many2one(
        'res.partner', string="Fournisseur", required=True, index=True,
        domain="[('supplier_rank', '>', 0)]",
    )
    company_id = fields.Many2one(
        'res.company', string="Société", required=True,
        default=lambda self: self.env.company,
    )
    currency_id = fields.Many2one(
        related='company_id.currency_id', readonly=True)
    qty = fields.Integer(
        string="Casiers consignés", default=0,
        help="Nombre de casiers (ou unités d'emballage) actuellement "
             "consignés chez ce fournisseur.",
    )
    unit_value = fields.Monetary(
        string="Consigne / casier", default=0.0,
        currency_field='currency_id',
        help="Valeur de consigne unitaire (casier + bouteilles).",
    )
    value = fields.Monetary(
        string="Valeur immobilisée", compute='_compute_value', store=True,
        currency_field='currency_id',
    )
    last_return_date = fields.Date(string="Dernière déconsignation")
    note = fields.Char(string="Note")
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('partner_company_uniq', 'unique(partner_id, company_id)',
         "Une seule ligne de consignes par fournisseur et par société."),
    ]

    @api.depends('qty', 'unit_value')
    def _compute_value(self):
        for rec in self:
            rec.value = (rec.qty or 0) * (rec.unit_value or 0.0)
