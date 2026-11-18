# -*- coding: utf-8 -*-
"""Les graphiques d'un onglet du tableau de bord sont dessinés dès le premier
clic (constat de recette)."""
from odoo.tests import HttpCase, tagged


@tagged('post_install', '-at_install', 'aite_stock')
class TestOnglets(HttpCase):

    def test_graphiques_au_premier_clic(self):
        action = self.env.ref('aite_stock_dashboard.action_aite_stock_dashboard')
        self.start_tour('/odoo/action-%s' % action.id, 'AiteStockOngletsTour', login='admin')
