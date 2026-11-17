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

    def test_salle_et_equipe(self):
        caisse = self.env['pos.config'].search([('aite_mode_restaurant', '=', True)], limit=1)
        self.assertGreaterEqual(len(caisse.floor_ids[:1].table_ids), 12)
        niveaux = set(self.env['hr.employee'].search([('aite_niveau_caisse', '!=', False)]).mapped('aite_niveau_caisse'))
        self.assertEqual(niveaux, {'serveur', 'caissiere', 'superviseur', 'manager'})
        for login in ('caisse', 'manager', 'chef'):
            self.assertTrue(self.env['res.users'].search_count([('login', '=', login)]), login)
        avant = self.env['hr.employee'].search_count([])
        jouer_carte(self.env)
        self.assertEqual(self.env['hr.employee'].search_count([]), avant, "rejouer ne crée rien")
