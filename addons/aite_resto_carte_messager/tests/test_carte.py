# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase, tagged

from odoo.addons.aite_resto_carte_messager import jouer_carte


@tagged('post_install', '-at_install', 'aite_carte_messager')
class TestCarteMessager(TransactionCase):

    def test_carte_posee_et_rejouable(self):
        Produits = self.env['product.template']
        self.assertEqual(Produits.search_count([('name', '=', 'Pizza Marguerite Grand')]), 1)
        medoc = Produits.search([('name', '=', 'Médoc')])
        self.assertEqual((medoc.list_price, medoc.standard_price, medoc.is_storable), (20000, 9500, True))
        self.assertFalse(medoc.taxes_id, "aucune taxe sur les produits")
        self.assertFalse(Produits.search([('name', '=', 'Poulet DG')]).standard_price,
                         "aucun coût inventé pour un plat")
        avant = Produits.search_count([])
        jouer_carte(self.env)
        self.assertEqual(Produits.search_count([]), avant, "rejouer ne crée rien")

    def test_societe_non_renommee(self):
        nom = self.env.company.name
        jouer_carte(self.env)
        self.assertEqual(self.env.company.name, nom)
