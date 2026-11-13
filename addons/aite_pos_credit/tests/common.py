# -*- coding: utf-8 -*-
"""Socle commun des tests du crédit clients (ardoises)."""
from uuid import uuid4

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


class ArdoiseCaisseCommon(CreditCommon):
    """Une caisse ouverte qui accepte l'ardoise, et des additions envoyées
    comme le fait la caisse (``sync_from_ui``), jamais par un ``create``
    direct (AH-01 ; tests de la commande ouverte et de la migration
    18.0.2.0.6). Aucun test ici : la classe sert de socle.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env['product.product'].create({
            'name': "Plat test ardoise",
            'type': 'consu',
            'available_in_pos': True,
            'list_price': 50000.0,
            'taxes_id': [(5, 0, 0)],
        })
        cash_journal = cls.env['account.journal'].create({
            'name': "Caisse ardoise ouverte (test)",
            'type': 'cash',
            'code': 'CAOUV',
            'company_id': cls.company.id,
        })
        cls.method_cash = cls.env['pos.payment.method'].create({
            'name': "Espèces (ardoise ouverte)",
            'journal_id': cash_journal.id,
            'company_id': cls.company.id,
        })
        cls.method_credit = cls.env['pos.payment.method'].create({
            'name': "Ardoise (ardoise ouverte)",
            'is_aite_credit': True,
            'company_id': cls.company.id,
        })
        cls.pos_config = cls.env['pos.config'].create({
            'name': "Caisse test ardoise ouverte",
            'payment_method_ids': [
                (6, 0, (cls.method_cash | cls.method_credit).ids)],
        })
        cls.pos_config.open_ui()
        cls.session = cls.pos_config.current_session_id
        cls.session.set_opening_control(0, None)

    def _synchroniser(self, state, uuid=None, total=50000.0):
        """Envoie la commande comme la caisse : ``sync_from_ui``.

        Au second envoi de la même addition (même ``uuid``), la caisse
        renvoie ses lignes et ses paiements déjà enregistrés en mise à jour
        (``[1, id, valeurs]``), pas en création.
        """
        uuid = uuid or str(uuid4())
        existante = self.env['pos.order'].search([('uuid', '=', uuid)])
        data = {
            'uuid': uuid,
            'name': "Commande %s" % uuid,
            'session_id': self.session.id,
            'state': state,
            'partner_id': self.client_a.id,
            'user_id': self.env.uid,
            'pricelist_id': self.pos_config.pricelist_id.id or False,
            'fiscal_position_id': False,
            'sequence_number': 1,
            'to_invoice': False,
            'date_order': fields.Datetime.to_string(fields.Datetime.now()),
            'amount_tax': 0.0,
            'amount_total': total,
            'amount_paid': total,
            'amount_return': 0.0,
            'last_order_preparation_change': '{}',
            'lines': [(0, 0, {
                'product_id': self.product.id,
                'qty': 1,
                'price_unit': total,
                'price_subtotal': total,
                'price_subtotal_incl': total,
                'tax_ids': [(6, 0, [])],
            })],
            'payment_ids': [(0, 0, {
                'amount': total,
                'name': fields.Datetime.now(),
                'payment_method_id': self.method_credit.id,
            })],
        }
        if existante:
            data['lines'] = [(1, line.id, {'qty': line.qty})
                             for line in existante.lines]
            data['payment_ids'] = [(1, pay.id, {'amount': pay.amount})
                                   for pay in existante.payment_ids]
        self.env['pos.order'].sync_from_ui([data])
        return self.env['pos.order'].search([('uuid', '=', uuid)]), uuid

    def _ardoises(self, order):
        return self.env['aite.pos.credit'].search([('order_id', '=', order.id)])
