# -*- coding: utf-8 -*-
"""Socle commun des tests POS Analytics : une caisse et des ventes."""
from odoo import fields
from odoo.tests import common


class PosAnalyticsCommon(common.TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.env.user.tz = 'UTC'

        cls.categ = cls.env['product.category'].create({
            'name': "Boissons test",
        })
        cls.categ_food = cls.env['product.category'].create({
            'name': "Cuisine test",
        })
        cls.beer = cls.env['product.product'].create({
            'name': "Bière pression",
            'type': 'consu',
            'available_in_pos': True,
            'categ_id': cls.categ.id,
            'list_price': 5000.0,
            'standard_price': 2000.0,
            'taxes_id': [(5, 0, 0)],
        })
        cls.dish = cls.env['product.product'].create({
            'name': "Poulet braisé",
            'type': 'consu',
            'available_in_pos': True,
            'categ_id': cls.categ_food.id,
            'list_price': 20000.0,
            'standard_price': 12000.0,
            'taxes_id': [(5, 0, 0)],
        })

        # Journal dédié : Odoo n'autorise qu'UN moyen de paiement
        # « espèces » par journal, et la base peut déjà en porter un
        # (jeu de démonstration, autre caisse).
        cls.cash_journal = cls.env['account.journal'].create({
            'name': "Caisse Analytics (test)",
            'type': 'cash',
            'code': 'CATST',
            'company_id': cls.company.id,
        })
        cls.method_cash = cls.env['pos.payment.method'].create({
            'name': "Espèces Analytics",
            'journal_id': cls.cash_journal.id,
            'company_id': cls.company.id,
        })
        cls.pos_config = cls.env['pos.config'].create({
            'name': "Caisse Analytics",
            'payment_method_ids': [(6, 0, cls.method_cash.ids)],
        })
        cls.pos_config.open_ui()
        cls.session = cls.pos_config.current_session_id
        # ``open_ui`` n'initialise pas toujours ``start_at`` ; le tableau de
        # bord filtre dessus, on le fixe pour un jeu déterministe.
        if not cls.session.start_at:
            cls.session.start_at = fields.Datetime.now()
        cls.today = fields.Date.context_today(cls.env.user)

    # ------------------------------------------------------------------
    # Fabrique de commande
    # ------------------------------------------------------------------

    def _sale(self, lines, partner=None):
        """``lines`` = [(produit, qté, prix_unitaire)]."""
        total = sum(qty * price for _p, qty, price in lines)
        order = self.env['pos.order'].create({
            'session_id': self.session.id,
            'company_id': self.company.id,
            'partner_id': partner.id if partner else False,
            'amount_tax': 0.0,
            'amount_total': total,
            'amount_paid': total,
            'amount_return': 0.0,
            'lines': [(0, 0, {
                'product_id': product.id,
                'qty': qty,
                'price_unit': price,
                'price_subtotal': qty * price,
                'price_subtotal_incl': qty * price,
            }) for product, qty, price in lines],
        })
        self.env['pos.payment'].create({
            'pos_order_id': order.id,
            'payment_method_id': self.method_cash.id,
            'amount': total,
        })
        order.write({'state': 'paid'})
        # Le tableau de bord interroge une vue SQL (aite.pos.daily.report) :
        # elle ne voit que ce qui est écrit en base, pas le cache ORM.
        self.env.flush_all()
        return order

    def _draft_sale(self, lines):
        """Commande laissée en brouillon — ne doit compter nulle part."""
        total = sum(qty * price for _p, qty, price in lines)
        order = self.env['pos.order'].create({
            'session_id': self.session.id,
            'company_id': self.company.id,
            'amount_tax': 0.0,
            'amount_total': total,
            'amount_paid': 0.0,
            'amount_return': 0.0,
            'lines': [(0, 0, {
                'product_id': product.id,
                'qty': qty,
                'price_unit': price,
                'price_subtotal': qty * price,
                'price_subtotal_incl': qty * price,
            }) for product, qty, price in lines],
        })
        self.env.flush_all()
        return order
