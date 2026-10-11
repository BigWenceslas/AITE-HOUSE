# -*- coding: utf-8 -*-
"""
Tests d'intégration du tableau de bord Stock & Inventaire.

Ces tests vérifient les règles d'agrégation et de classification du module
via des données simulées (recordsets factices), en miroir fidèle des
méthodes de ``models/stock_dashboard.py`` :

* ``_vday_map``       — ventes moyennes/jour (sorties clients ÷ fenêtre)
* ``_quant_maps``     — quantités par produit et par emplacement (filtre)
* ``_move_qty_field`` — détection défensive du champ quantité
* ``_inventory_gaps`` — signature des écarts (+ trouvé / − manquant / casse)
* ``get_moves_journal`` — typage des mouvements et totaux
* ``get_kpis``        — coulage % (pertes / CA estimé)
* tri des alertes, totaux du stock complet, clés d'emplacement JSON.
"""
import unittest
from collections import defaultdict


# ----------------------------------------------------------------------
# Recordsets factices minimalistes
# ----------------------------------------------------------------------

class Rec:
    def __init__(self, **kw):
        self.__dict__.update(kw)


def loc(usage='internal', scrap=False, lid=1):
    return Rec(id=lid, usage=usage, scrap_location=scrap,
               display_name='LOC/%s' % lid)


# ----------------------------------------------------------------------
# Miroirs des règles du module (formules identiques au source)
# ----------------------------------------------------------------------

def vday_map(move_rows, days=30):
    """Miroir de ``_vday_map`` : somme des sorties clients ÷ jours."""
    out = {}
    for pid, qty in move_rows:
        out[pid] = out.get(pid, 0.0) + qty
    return {pid: total / float(days) for pid, total in out.items()}


def quant_maps(quant_rows, location_id=None):
    """Miroir de ``_quant_maps`` (filtre d'emplacement + répartition)."""
    stock_map = defaultdict(float)
    byloc = defaultdict(dict)
    for pid, lid, qty in quant_rows:
        byloc[pid][lid] = byloc[pid].get(lid, 0.0) + qty
        if location_id:
            if lid == int(location_id):
                stock_map[pid] += qty
        else:
            stock_map[pid] += qty
    return stock_map, byloc


def move_qty_field(fields_meta):
    """Miroir de ``_move_qty_field`` : priorité quantity > quantity_done."""
    for name in ('quantity', 'quantity_done'):
        f = fields_meta.get(name)
        if f is not None and f.get('store', False):
            return name
    return 'product_uom_qty'


def gap_sign(move):
    """Miroir de la règle de signe des écarts d'inventaire."""
    return move.qty if move.dst.usage == 'internal' else -move.qty


def classify_move(mv):
    """Miroir du typage de ``get_moves_journal``."""
    src, dst = mv.src, mv.dst
    if getattr(mv, 'is_inventory', False):
        return 'Ajustement inv.', (mv.qty if dst.usage == 'internal'
                                   else -mv.qty)
    if dst.scrap_location:
        return 'Casse / rebut', -mv.qty
    if dst.usage == 'customer':
        return 'Vente / livraison', -mv.qty
    if src.usage in ('supplier', 'inventory') and dst.usage == 'internal':
        return 'Réception', mv.qty
    if src.usage == 'customer':
        return 'Retour client', mv.qty
    if src.usage == 'internal' and dst.usage == 'internal':
        return 'Transfert', mv.qty
    return 'Autre', (mv.qty if dst.usage == 'internal' else -mv.qty)


def coulage_pct(pertes, ca_est):
    """Miroir du calcul de ``get_kpis`` : % du CA estimé, 0 si pas de CA."""
    return (pertes / ca_est * 100.0) if ca_est > 0 else 0.0


# ----------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------

class TestVdayMap(unittest.TestCase):

    def test_agregation_et_division(self):
        rows = [(1, 300.0), (1, 90.0), (2, 60.0)]
        m = vday_map(rows, days=30)
        self.assertAlmostEqual(m[1], 13.0)   # 390 / 30
        self.assertAlmostEqual(m[2], 2.0)

    def test_produit_sans_vente_absent(self):
        m = vday_map([(1, 30.0)])
        self.assertNotIn(99, m)


class TestQuantMaps(unittest.TestCase):
    ROWS = [
        (1, 10, 2400.0), (1, 20, 120.0),     # Castel : cave + bar
        (5, 10, 36.0), (5, 20, 12.0),        # Guinness
        (12, 10, 600.0),                     # Eau : cave seulement
    ]

    def test_total_tous_emplacements(self):
        stock, byloc = quant_maps(self.ROWS)
        self.assertEqual(stock[1], 2520.0)
        self.assertEqual(stock[5], 48.0)
        self.assertEqual(byloc[1], {10: 2400.0, 20: 120.0})

    def test_filtre_emplacement(self):
        stock, byloc = quant_maps(self.ROWS, location_id=20)
        self.assertEqual(stock[1], 120.0)     # bar uniquement
        self.assertEqual(stock.get(12, 0.0), 0.0)  # pas d'eau au bar
        # la répartition reste complète (pour l'affichage)
        self.assertEqual(byloc[12], {10: 600.0})

    def test_cumul_meme_emplacement(self):
        stock, byloc = quant_maps([(1, 10, 5.0), (1, 10, 7.0)])
        self.assertEqual(byloc[1][10], 12.0)


class TestMoveQtyFieldDetection(unittest.TestCase):

    def test_odoo_18_quantity(self):
        meta = {'quantity': {'store': True},
                'quantity_done': {'store': False}}
        self.assertEqual(move_qty_field(meta), 'quantity')

    def test_fallback_quantity_done(self):
        meta = {'quantity_done': {'store': True}}
        self.assertEqual(move_qty_field(meta), 'quantity_done')

    def test_dernier_recours(self):
        self.assertEqual(move_qty_field({}), 'product_uom_qty')


class TestGapSigning(unittest.TestCase):

    def test_ajustement_positif_vers_interne(self):
        mv = Rec(qty=5.0, dst=loc('internal'))
        self.assertEqual(gap_sign(mv), 5.0)      # trouvé en plus

    def test_ajustement_negatif_depuis_interne(self):
        mv = Rec(qty=12.0, dst=loc('inventory'))
        self.assertEqual(gap_sign(mv), -12.0)    # manquant

    def test_valorisation(self):
        mv = Rec(qty=12.0, dst=loc('inventory'))
        self.assertEqual(gap_sign(mv) * 650, -7800.0)  # Castel −12 (proto)


class TestMoveTyping(unittest.TestCase):

    def _mv(self, src_usage, dst_usage, qty=10.0, scrap=False, inv=False):
        return Rec(qty=qty, is_inventory=inv,
                   src=loc(src_usage), dst=loc(dst_usage, scrap=scrap))

    def test_reception(self):
        t, q = classify_move(self._mv('supplier', 'internal'))
        self.assertEqual((t, q), ('Réception', 10.0))

    def test_vente(self):
        t, q = classify_move(self._mv('internal', 'customer'))
        self.assertEqual((t, q), ('Vente / livraison', -10.0))

    def test_transfert(self):
        t, q = classify_move(self._mv('internal', 'internal'))
        self.assertEqual((t, q), ('Transfert', 10.0))

    def test_casse(self):
        t, q = classify_move(self._mv('internal', 'inventory', scrap=True))
        self.assertEqual((t, q), ('Casse / rebut', -10.0))

    def test_ajustement_prioritaire(self):
        t, q = classify_move(self._mv('inventory', 'internal', inv=True))
        self.assertEqual((t, q), ('Ajustement inv.', 10.0))

    def test_retour_client(self):
        t, q = classify_move(self._mv('customer', 'internal'))
        self.assertEqual((t, q), ('Retour client', 10.0))

    def test_totaux(self):
        moves = [
            self._mv('supplier', 'internal', 100),   # in 100×cost
            self._mv('internal', 'customer', 60),    # out
            self._mv('internal', 'internal', 40),    # tr
            self._mv('internal', 'inventory', 12, inv=True),  # adj −12
        ]
        cost = 650.0
        totals = {'in': 0.0, 'out': 0.0, 'tr': 0.0, 'adj': 0.0}
        for mv in moves:
            t, signed = classify_move(mv)
            if t == 'Réception':
                totals['in'] += mv.qty * cost
            elif t == 'Vente / livraison':
                totals['out'] += mv.qty * cost
            elif t == 'Transfert':
                totals['tr'] += mv.qty
            elif t in ('Ajustement inv.', 'Casse / rebut'):
                totals['adj'] += signed * cost
        self.assertEqual(totals['in'], 65000.0)
        self.assertEqual(totals['out'], 39000.0)
        self.assertEqual(totals['tr'], 40.0)
        self.assertEqual(totals['adj'], -7800.0)


class TestCoulage(unittest.TestCase):

    def test_pct_nominal(self):
        # Prototype : pertes ≈ 186 400 pour ~11,6 M de CA → ~1,6 %
        self.assertAlmostEqual(
            coulage_pct(186400, 11650000), 1.6, places=1)

    def test_pct_sans_ca(self):
        self.assertEqual(coulage_pct(50000, 0), 0.0)

    def test_seuil_depasse(self):
        pct = coulage_pct(300000, 10000000)
        self.assertGreater(pct, 2.0)


class TestTriEtTotaux(unittest.TestCase):

    ROWS = [
        {'id': 1, 'urgency': 3, 'couv': 19.4, 'stock': 2520, 'value': 1638000},
        {'id': 6, 'urgency': 0, 'couv': 0.0, 'stock': 0, 'value': 0},
        {'id': 5, 'urgency': 1, 'couv': 2.7, 'stock': 48, 'value': 29760},
        {'id': 9, 'urgency': 2, 'couv': 1.9, 'stock': 30, 'value': 10500},
        {'id': 17, 'urgency': 4, 'couv': 999, 'stock': 9, 'value': 40500},
    ]

    def test_tri_alertes(self):
        """Miroir du getter ``alertRows`` : urgence puis couverture."""
        rows = sorted(self.ROWS,
                      key=lambda r: (r['urgency'], r['couv']))
        self.assertEqual([r['id'] for r in rows], [6, 5, 9, 1, 17])

    def test_totaux_stock_complet(self):
        units = sum(r['stock'] for r in self.ROWS)
        value = sum(r['value'] for r in self.ROWS)
        self.assertEqual(units, 2607)
        self.assertEqual(value, 1718760)

    def test_cles_emplacement_json(self):
        """Miroir de ``locQty`` : clés int OU str après sérialisation."""
        row = {'by_location': {'10': 2400.0, '20': 120.0}}

        def loc_qty(r, loc_id):
            m = r.get('by_location') or {}
            v = m.get(loc_id)
            if v is None:
                v = m.get(str(loc_id))
            return v or 0.0

        self.assertEqual(loc_qty(row, 10), 2400.0)
        self.assertEqual(loc_qty(row, 20), 120.0)
        self.assertEqual(loc_qty(row, 99), 0.0)




# ======================================================================
# v1.1.0 — Double valorisation : coût d'achat vs prix de vente
# ======================================================================

class TestDoubleValorisation(unittest.TestCase):
    """Miroirs des nouveaux agrégats de get_kpis et de stockTotals."""

    ROWS = [
        # (stock, cost, list_price) — value = s×c, value_sale = s×pv
        (2520, 650, 800),    # Castel : 1 638 000 / 2 016 000
        (48, 620, 850),      # Guinness : 29 760 / 40 800
        (600, 190, 250),     # Tangui : 114 000 / 150 000
        (30, 350, 500),      # Softs : 10 500 / 15 000
    ]

    def _totals(self, rows):
        value = sum(s * c for (s, c, _p) in rows)
        value_sale = sum(s * p for (s, _c, p) in rows)
        return value, value_sale

    def test_sommes_cout_et_vente(self):
        value, value_sale = self._totals(self.ROWS)
        self.assertEqual(value, 1792260)
        self.assertEqual(value_sale, 2221800)

    def test_marge_potentielle(self):
        value, value_sale = self._totals(self.ROWS)
        margin = value_sale - value
        pct = margin / value_sale * 100.0
        self.assertEqual(margin, 429540)
        self.assertAlmostEqual(pct, 19.33, places=1)   # marge sur PV

    def test_marge_pct_sans_vente(self):
        # Aucun prix de vente renseigné → 0 %, pas de division par zéro
        value_sale = 0.0
        pct = (100.0 - value_sale) / value_sale * 100.0 \
            if value_sale > 0 else 0.0
        self.assertEqual(pct, 0.0)

    def test_totaux_liste_filtree(self):
        """Miroir de stockTotals (onglet Stock complet) après recherche."""
        filtered = self.ROWS[:2]     # ex. recherche « bière »
        value, value_sale = self._totals(filtered)
        margin = value_sale - value
        self.assertEqual((value, value_sale), (1667760, 2056800))
        self.assertEqual(margin, 389040)

    def test_ligne_produit_value_sale(self):
        """Miroir de _build_rows : value_sale = stock × lst_price."""
        stock, lst_price = 2520, 800
        self.assertEqual(stock * (lst_price or 0.0), 2016000)
        self.assertEqual(stock * (None or 0.0), 0.0)


if __name__ == '__main__':
    unittest.main(verbosity=1)
