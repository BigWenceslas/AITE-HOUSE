# -*- coding: utf-8 -*-
"""Socle commun des tests du crédit clients (ardoises)."""
from odoo import fields
from odoo.tests import common


class CreditCommon(common.TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.env.user.tz = 'UTC'

        cls.client_a = cls.env['res.partner'].create({
            'name': "Client Ardoise A",
            'phone': '+224 600 11 11 11',
        })
        cls.client_b = cls.env['res.partner'].create({
            'name': "Client Ardoise B",
        })

        cls.cash_journal = cls.env['account.journal'].search([
            ('type', '=', 'cash'), ('company_id', '=', cls.company.id),
        ], limit=1)

    # ------------------------------------------------------------------
    # Fabriques
    # ------------------------------------------------------------------

    def _credit(self, amount=100000.0, partner=None, days_ago=0, **kwargs):
        from datetime import timedelta
        vals = {
            'partner_id': (partner or self.client_a).id,
            'company_id': self.env.company.id,
            'amount_total': amount,
            'date_open': fields.Date.context_today(self.env.user)
                         - timedelta(days=days_ago),
        }
        vals.update(kwargs)
        return self.env['aite.pos.credit'].create(vals)

    def _repay(self, credit, amount, method='cash', **kwargs):
        vals = {
            'credit_id': credit.id,
            'amount': amount,
            'method': method,
        }
        vals.update(kwargs)
        return self.env['aite.pos.credit.payment'].create(vals)
