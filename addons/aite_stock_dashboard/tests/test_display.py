# -*- coding: utf-8 -*-
"""Ce que l'écran affiche : dates, références, emplacements (écarts
non bloquants n° 37, 43 et 68).

* n° 37 — les journaux (écarts & casses, mouvements) donnent leurs dates
  au format de la langue (``%d/%m/%Y`` en français) et dans le fuseau de
  l'utilisateur, pas en ISO et en UTC ; la période sélectionnée est faite
  des MÊMES jours locaux : un mouvement affiché « 15/10/2026 » appartient
  à la période du 15/10, pas à celle du 14/10 ;
* n° 43 — la raison d'inventaire par défaut d'Odoo, « Quantity Updated »
  (chaîne non traduisible du standard), s'affiche en français ;
* n° 68 — deux entrepôts ont chacun un emplacement « Stock » : le filtre
  et les colonnes doivent les distinguer (nom complet).
"""
from datetime import datetime

from odoo import fields
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install', 'aite_stock')
class TestStockDashboardDisplay(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env['res.lang']._activate_lang('fr_FR')
        cls.env.user.tz = 'Africa/Douala'
        cls.env = cls.env(context=dict(cls.env.context, lang='fr_FR',
                                       tz='Africa/Douala'))
        cls.dashboard = cls.env['aite.stock.dashboard']
        cls.company = cls.env.company
        cls.warehouse = cls.env['stock.warehouse'].search(
            [('company_id', '=', cls.company.id)], limit=1)
        cls.stock_loc = cls.warehouse.lot_stock_id
        cls.item = cls.env['product.product'].create({
            'name': "Castel 65 cl",
            'is_storable': True,
            'standard_price': 500.0,
            'list_price': 800.0,
        })

    def _adjust(self, qty, reason=None):
        """Ajustement d'inventaire comme le fait l'écran standard ; avec
        ``reason``, comme l'assistant « Appliquer » (raison par défaut
        « Quantity Updated »)."""
        ctx = {'inventory_mode': True}
        if reason:
            ctx['inventory_name'] = reason
        quant = self.env['stock.quant'].with_context(**ctx).create({
            'product_id': self.item.id,
            'location_id': self.stock_loc.id,
            'inventory_quantity': qty,
        })
        quant.with_context(**ctx)._apply_inventory()
        self.env.flush_all()
        return self.env['stock.move'].search(
            [('product_id', '=', self.item.id), ('is_inventory', '=', True)],
            order='id desc', limit=1)

    # ------------------------------------------------------------------
    # n° 37 — dates des journaux
    # ------------------------------------------------------------------

    def test_journal_dates_are_french_and_local(self):
        move = self._adjust(24)
        # 14/10 à 23 h 30 UTC = 15/10 à 0 h 30 à Douala (UTC+1).
        move.write({'date': datetime(2026, 10, 14, 23, 30)})
        self.env.flush_all()
        gaps = self.dashboard.get_inventory_gaps('2026-10-14', '2026-10-15')
        gap = next(g for g in gaps if g['id'] == move.id)
        self.assertEqual(gap['date'], '15/10/2026')
        journal = self.dashboard.get_moves_journal('2026-10-14', '2026-10-15')
        row = next(r for r in journal['rows'] if r['id'] == move.id)
        self.assertEqual(row['date'], '15/10/2026')

    def _ids(self, date_from, date_to):
        """Mouvements retenus par chaque bloc daté de l'écran."""
        gaps = self.dashboard.get_inventory_gaps(date_from, date_to)
        journal = self.dashboard.get_moves_journal(date_from, date_to)
        return ({g['id'] for g in gaps},
                {r['id'] for r in journal['rows']})

    def test_the_period_is_made_of_local_days(self):
        """La période suit le jour que l'écran affiche (relecture n° 37).

        Les dates s'affichent dans le fuseau de l'utilisateur ; si la
        période restait en jours UTC, le journal du 14/10 listerait un
        mouvement affiché « 15/10/2026 » — un bar qui travaille après
        minuit le verrait tous les soirs.
        """
        move = self._adjust(24)
        # 14/10 à 23 h 30 UTC = 15/10 à 0 h 30 à Douala (UTC+1).
        move.write({'date': datetime(2026, 10, 14, 23, 30)})
        late = self._adjust(30)
        # 15/10 à 22 h 30 UTC = 15/10 à 23 h 30 à Douala : encore le 15.
        late.write({'date': datetime(2026, 10, 15, 22, 30)})
        self.env.flush_all()
        for label, ids in zip(("écarts", "journal"),
                              self._ids('2026-10-14', '2026-10-14')):
            with self.subTest(bloc=label, jour="14/10"):
                self.assertNotIn(move.id, ids)
                self.assertNotIn(late.id, ids)
        for label, ids in zip(("écarts", "journal"),
                              self._ids('2026-10-15', '2026-10-15')):
            with self.subTest(bloc=label, jour="15/10"):
                self.assertIn(move.id, ids)
                self.assertIn(late.id, ids)
        # Les indicateurs (pertes, écart net) comptent les mêmes jours —
        # sur une catégorie à part, que le jeu de démonstration ne touche pas.
        categ = self.env['product.category'].create({'name': "Cave (test)"})
        self.item.categ_id = categ
        self.env.flush_all()
        for day, refs in (('2026-10-14', 0), ('2026-10-15', 1)):
            with self.subTest(indicateurs=day):
                kpis = self.dashboard.get_kpis(day, day, categ_id=categ.id)
                self.assertEqual(kpis['gap_refs'], refs)

    # ------------------------------------------------------------------
    # n° 43 — « Quantity Updated » du standard
    # ------------------------------------------------------------------

    def test_default_inventory_reason_is_shown_in_french(self):
        move = self._adjust(12, reason="Quantity Updated")
        self.assertTrue(move.reference.startswith("Quantity Updated"))
        # Jour LOCAL du mouvement : la période est faite de jours locaux.
        today = fields.Date.to_string(
            fields.Date.context_today(self.dashboard, move.date))
        gaps = self.dashboard.get_inventory_gaps(today, today)
        gap = next(g for g in gaps if g['id'] == move.id)
        self.assertNotIn("Quantity Updated", gap['ref'])
        self.assertTrue(gap['ref'].startswith("Quantité mise à jour"))

    def test_a_reason_typed_by_the_user_is_kept(self):
        move = self._adjust(6, reason="Casse au bar")
        today = fields.Date.to_string(
            fields.Date.context_today(self.dashboard, move.date))
        gaps = self.dashboard.get_inventory_gaps(today, today)
        gap = next(g for g in gaps if g['id'] == move.id)
        self.assertEqual(gap['ref'], "Casse au bar")

    # ------------------------------------------------------------------
    # n° 68 — emplacements de deux entrepôts
    # ------------------------------------------------------------------

    def test_two_warehouses_are_told_apart(self):
        other = self.env['stock.warehouse'].create({
            'name': "Bar du jardin",
            'code': 'BJ',
            'company_id': self.company.id,
        })
        rows = self.dashboard.get_locations()
        names = {r['id']: r['name'] for r in rows}
        self.assertIn(self.stock_loc.id, names)
        self.assertIn(other.lot_stock_id.id, names)
        self.assertNotEqual(names[self.stock_loc.id],
                            names[other.lot_stock_id.id])
        self.assertEqual(names[other.lot_stock_id.id],
                         other.lot_stock_id.complete_name)
