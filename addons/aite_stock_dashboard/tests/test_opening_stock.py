# -*- coding: utf-8 -*-
"""Stock de départ et libellés des emplacements (recette de novembre 2026).

* Le premier inventaire d'un produit qui n'avait jamais bougé à cet
  emplacement est son **stock de départ** : sur une base neuve, le stock
  saisi par un inventaire apparaissait en « écarts d'inventaire »
  (848 600 FCFA le premier mois). Il n'est compté ni dans l'écart net,
  ni dans les pertes, ni dans le coulage ; il s'affiche à part.
* Le journal des mouvements montrait les noms techniques anglais des
  emplacements virtuels d'Odoo (« Virtual Locations/Inventory
  adjustment », « Partners/Customers », « Partners/Vendors ») : il donne
  un libellé français selon le type d'emplacement et garde le nom complet
  des emplacements internes.
"""
from odoo import fields
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install', 'aite_stock')
class TestOpeningStock(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env['res.lang']._activate_lang('fr_FR')
        cls.env = cls.env(context=dict(cls.env.context, lang='fr_FR'))
        cls.dashboard = cls.env['aite.stock.dashboard']
        cls.company = cls.env.company
        cls.warehouse = cls.env['stock.warehouse'].search(
            [('company_id', '=', cls.company.id)], limit=1)
        cls.stock_loc = cls.warehouse.lot_stock_id
        cls.bar_loc = cls.env['stock.location'].create({
            'name': "Bar test",
            'usage': 'internal',
            'location_id': cls.warehouse.view_location_id.id,
        })
        # Catégorie à part : le jeu de démonstration n'y touche pas.
        cls.categ = cls.env['product.category'].create(
            {'name': "Cave départ (test)"})
        cls.beer = cls._product("Castel 65 cl (départ)", 500.0, 800.0)
        cls.wine = cls._product("Vin rouge (départ)", 4000.0, 7000.0)

    @classmethod
    def _product(cls, name, cost, price):
        return cls.env['product.product'].create({
            'name': name,
            'is_storable': True,
            'categ_id': cls.categ.id,
            'standard_price': cost,
            'list_price': price,
            'taxes_id': [(5, 0, 0)],
        })

    def _count(self, product, qty, location=None):
        """Inventaire comme l'écran « Inventaire physique » : quantité
        comptée puis « Appliquer »."""
        quant = self.env['stock.quant'].with_context(
            inventory_mode=True).create({
                'product_id': product.id,
                'location_id': (location or self.stock_loc).id,
                'inventory_quantity': qty,
            })
        quant._apply_inventory()
        self.env.flush_all()
        return self.env['stock.move'].search(
            [('product_id', '=', product.id), ('is_inventory', '=', True)],
            order='id desc', limit=1)

    def _move(self, product, qty, src, dst):
        move = self.env['stock.move'].create({
            'name': product.name,
            'product_id': product.id,
            'product_uom_qty': qty,
            'product_uom': product.uom_id.id,
            'location_id': src.id,
            'location_dest_id': dst.id,
        })
        move._action_confirm()
        move._action_assign()
        move.quantity = qty
        move.picked = True
        move._action_done()
        self.env.flush_all()
        return move

    def _today(self):
        return fields.Date.to_string(
            fields.Date.context_today(self.dashboard))

    def _kpis(self):
        today = self._today()
        return self.dashboard.get_kpis(today, today, categ_id=self.categ.id)

    def _gaps(self):
        today = self._today()
        return {g['id']: g for g in self.dashboard.get_inventory_gaps(
            today, today, categ_id=self.categ.id)}

    def _journal(self):
        today = self._today()
        return self.dashboard.get_moves_journal(
            today, today, categ_id=self.categ.id)

    # ------------------------------------------------------------------
    # Stock de départ
    # ------------------------------------------------------------------

    def test_first_count_of_a_new_base_is_opening_stock(self):
        """Base neuve : le stock saisi par inventaire n'est pas un écart."""
        beer = self._count(self.beer, 120)
        wine = self._count(self.wine, 20)
        kpis = self._kpis()
        self.assertEqual(kpis['gap_net'], 0.0)
        self.assertEqual(kpis['gap_refs'], 0)
        self.assertEqual(kpis['pertes'], 0.0)
        self.assertEqual(kpis['coul_pct'], 0.0)
        # Montré à part : 120 × 500 + 20 × 4 000.
        self.assertEqual(kpis['opening_value'], 120 * 500.0 + 20 * 4000.0)
        self.assertEqual(kpis['opening_refs'], 2)
        gaps = self._gaps()
        for move in (beer, wine):
            with self.subTest(produit=move.product_id.name):
                self.assertTrue(gaps[move.id]['opening'])
                self.assertEqual(gaps[move.id]['gtype'], "Stock de départ")

    def test_the_next_count_is_a_real_gap(self):
        """Le deuxième inventaire compte : 120 saisis, 117 recomptés."""
        opening = self._count(self.beer, 120)
        recount = self._count(self.beer, 117)
        gaps = self._gaps()
        self.assertTrue(gaps[opening.id]['opening'])
        self.assertFalse(gaps[recount.id]['opening'])
        self.assertEqual(gaps[recount.id]['value'], -3 * 500.0)
        kpis = self._kpis()
        self.assertEqual(kpis['gap_net'], -3 * 500.0)
        self.assertEqual(kpis['pertes'], 3 * 500.0)
        self.assertEqual(kpis['gap_refs'], 1)
        self.assertEqual(kpis['opening_value'], 120 * 500.0)

    def test_a_product_received_before_its_first_count_has_a_gap(self):
        """Une réception avant le premier inventaire : le comptage qui
        suit est un vrai écart (la référence avait déjà bougé)."""
        supplier = self.env.ref('stock.stock_location_suppliers')
        self._move(self.beer, 48, supplier, self.stock_loc)
        count = self._count(self.beer, 45)
        gaps = self._gaps()
        self.assertFalse(gaps[count.id]['opening'])
        self.assertEqual(self._kpis()['pertes'], 3 * 500.0)

    def test_opening_stock_of_each_location(self):
        """Stock de départ saisi au magasin ET au bar : deux départs."""
        shop = self._count(self.beer, 100)
        bar = self._count(self.beer, 24, location=self.bar_loc)
        gaps = self._gaps()
        self.assertTrue(gaps[shop.id]['opening'])
        self.assertTrue(gaps[bar.id]['opening'])
        self.assertEqual(self._kpis()['opening_value'], 124 * 500.0)

    def test_coulage_series_ignores_opening_stock(self):
        self._count(self.beer, 120)
        series = self.dashboard.get_coulage_series(categ_id=self.categ.id)
        self.assertEqual(series['rows'][-1]['pertes'], 0.0)

    def test_moves_journal_shows_opening_stock_apart(self):
        opening = self._count(self.beer, 120)
        recount = self._count(self.beer, 118)
        journal = self._journal()
        rows = {r['id']: r for r in journal['rows']}
        self.assertEqual(rows[opening.id]['type'], "Stock de départ")
        self.assertEqual(rows[recount.id]['type'], "Ajustement inv.")
        self.assertEqual(journal['totals']['adj'], -2 * 500.0)
        self.assertEqual(journal['totals']['opening'], 120 * 500.0)

    # ------------------------------------------------------------------
    # Libellés des emplacements
    # ------------------------------------------------------------------

    def test_moves_journal_speaks_french_about_locations(self):
        supplier = self.env.ref('stock.stock_location_suppliers')
        customer = self.env.ref('stock.stock_location_customers')
        opening = self._count(self.beer, 120)
        receipt = self._move(self.beer, 24, supplier, self.stock_loc)
        sale = self._move(self.beer, 6, self.stock_loc, customer)
        transfer = self._move(self.beer, 12, self.stock_loc, self.bar_loc)
        rows = {r['id']: r for r in self._journal()['rows']}
        stock_name = self.stock_loc.complete_name
        expected = {
            opening.id: ("Ajustement d'inventaire", stock_name),
            receipt.id: ("Fournisseur", stock_name),
            sale.id: (stock_name, "Client"),
            transfer.id: (stock_name, self.bar_loc.complete_name),
        }
        for move_id, (src, dst) in expected.items():
            with self.subTest(mouvement=rows[move_id]['type']):
                self.assertEqual(rows[move_id]['src'], src)
                self.assertEqual(rows[move_id]['dst'], dst)
        for row in rows.values():
            for label in (row['src'], row['dst']):
                self.assertNotIn("Virtual Locations", label)
                self.assertNotIn("Partners", label)

    def test_location_label_of_each_usage(self):
        Location = self.env['stock.location']
        labels = {
            'inventory': "Ajustement d'inventaire",
            'customer': "Client",
            'supplier': "Fournisseur",
            'production': "Production",
            'transit': "Transit",
        }
        for usage, label in labels.items():
            with self.subTest(usage=usage):
                loc = Location.search([('usage', '=', usage)], limit=1) \
                    or Location.create({'name': "Test %s" % usage,
                                        'usage': usage})
                self.assertEqual(
                    self.dashboard._display_location(loc), label)
        scrap = Location.search([('scrap_location', '=', True)], limit=1) \
            or Location.create({'name': "Rebut test", 'usage': 'inventory',
                                'scrap_location': True})
        self.assertEqual(self.dashboard._display_location(scrap),
                         "Casse / rebut")
        view = self.warehouse.view_location_id
        self.assertEqual(self.dashboard._display_location(view),
                         view.complete_name)
        self.assertEqual(self.dashboard._display_location(self.stock_loc),
                         self.stock_loc.complete_name)
        self.assertEqual(
            self.dashboard._display_location(Location.browse()), "")
