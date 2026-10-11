# -*- coding: utf-8 -*-
"""
Tests du moteur Espaces & Prestations (aite_slot_booking).

Technique signature AITE : on **extrait le code source réel** des
fonctions pures et on l'exécute — ``_build_day_slots`` et
``_overlap_count`` (ressource), ``_slot_price``, ``_check_alignment`` et
``_folio_line_vals`` (réservation), ``_fill_rate`` (dashboard).
"""
import os
import re
import textwrap
import unittest
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ADDONS = os.path.normpath(os.path.join(HERE, '..', '..', 'addons'))
MOD = os.path.join(ADDONS, 'aite_slot_booking', 'models')


def _extract(path, names):
    src = open(path, encoding='utf-8').read()
    ns = {}
    for name in names:
        m = re.search(
            r'^    def %s\(.*?(?=^    @staticmethod|^    @api\.|'
            r'^    # -{10,}|^    def )' % name,
            src, re.S | re.M)
        assert m, "%s introuvable dans %s" % (name, path)
        exec(compile(textwrap.dedent(m.group(0)), path, 'exec'), ns)
    return ns


_res = _extract(os.path.join(MOD, 'booking_resource.py'),
                ['_overlap_count', '_build_day_slots'])
_bk = _extract(os.path.join(MOD, 'booking_booking.py'),
               ['_slot_price', '_check_alignment', '_folio_line_vals'])
_dash = _extract(os.path.join(MOD, 'slot_dashboard.py'), ['_fill_rate'])

_overlap_count = _res['_overlap_count']
_build_day_slots = _res['_build_day_slots']
_slot_price = _bk['_slot_price']
_check_alignment = _bk['_check_alignment']
_folio_line_vals = _bk['_folio_line_vals']
_fill_rate = _dash['_fill_rate']


class TestOverlapCount(unittest.TestCase):
    """Chevauchements : la règle qui bloque les conflits."""

    def test_chevauchement_simple(self):
        busy = [(10.0, 12.0)]
        self.assertEqual(_overlap_count(busy, 11.0, 13.0), 1)

    def test_adjacents_ne_se_chevauchent_pas(self):
        # 10-12 puis 12-14 : fin == début → PAS de conflit
        busy = [(10.0, 12.0)]
        self.assertEqual(_overlap_count(busy, 12.0, 14.0), 0)
        self.assertEqual(_overlap_count(busy, 8.0, 10.0), 0)

    def test_englobant_et_inclus(self):
        busy = [(10.0, 12.0)]
        self.assertEqual(_overlap_count(busy, 9.0, 13.0), 1)   # englobe
        self.assertEqual(_overlap_count(busy, 10.5, 11.5), 1)  # inclus

    def test_plusieurs_simultanes(self):
        busy = [(10.0, 12.0), (11.0, 13.0), (14.0, 15.0)]
        self.assertEqual(_overlap_count(busy, 11.0, 12.0), 2)

    def test_datetimes(self):
        d = datetime
        busy = [(d(2026, 7, 20, 10), d(2026, 7, 20, 12))]
        self.assertEqual(
            _overlap_count(busy, d(2026, 7, 20, 11), d(2026, 7, 20, 13)),
            1)
        self.assertEqual(
            _overlap_count(busy, d(2026, 7, 20, 12), d(2026, 7, 20, 14)),
            0)


class TestBuildDaySlots(unittest.TestCase):
    """Grille de disponibilité — la source unique dashboard + site."""

    def test_grille_9_22_pas_60(self):
        slots = _build_day_slots(9.0, 22.0, 60, [], 1)
        self.assertEqual(len(slots), 13)
        self.assertEqual(slots[0]['label'], '09:00')
        self.assertEqual(slots[-1]['label'], '21:00')
        self.assertTrue(all(s['state'] == 'free' for s in slots))

    def test_pas_30_minutes(self):
        slots = _build_day_slots(9.0, 12.0, 30, [], 1)
        self.assertEqual(len(slots), 6)
        self.assertEqual(slots[1]['label'], '09:30')

    def test_occupation_full(self):
        # SPA 10h-12h réservé, capacité 1 → 2 créneaux full
        slots = _build_day_slots(9.0, 13.0, 60, [(10.0, 12.0)], 1)
        states = [s['state'] for s in slots]
        self.assertEqual(states, ['free', 'full', 'full', 'free'])

    def test_capacite_2_partial_puis_full(self):
        busy = [(10.0, 11.0), (10.0, 11.0), (11.0, 12.0)]
        slots = _build_day_slots(9.0, 13.0, 60, busy, 2)
        states = [s['state'] for s in slots]
        self.assertEqual(states, ['free', 'full', 'partial', 'free'])
        self.assertEqual(slots[1]['used'], 2)
        self.assertEqual(slots[2]['used'], 1)

    def test_ouverture_demi_heure(self):
        slots = _build_day_slots(9.5, 11.5, 60, [], 1)
        self.assertEqual([s['label'] for s in slots], ['09:30', '10:30'])


class TestSlotPrice(unittest.TestCase):
    """Tarif : manuel > prestation × qté > heures × tarif horaire."""

    def test_espace_tarif_horaire(self):
        # Salon VVIP 25 000 F/h × 3 h
        self.assertEqual(_slot_price(0, 1, 3.0, 25000, 0), 75000)

    def test_prestation(self):
        # Soin SPA 40 000 F (le tarif horaire de la cabine est ignoré)
        self.assertEqual(_slot_price(40000, 1, 1.5, 15000, 0), 40000)

    def test_pressing_quantite(self):
        # 8 chemises × 2 500 F
        self.assertEqual(_slot_price(2500, 8, 0.5, 0, 0), 20000)

    def test_prix_manuel_prioritaire(self):
        self.assertEqual(_slot_price(40000, 2, 3.0, 25000, 60000), 60000)

    def test_qty_zero_traitee_comme_un(self):
        self.assertEqual(_slot_price(2500, 0, 0.5, 0, 0), 2500)


class TestCheckAlignment(unittest.TestCase):
    """Validité d'un créneau : ordre, horaires, grille."""

    def test_valide(self):
        self.assertEqual(_check_alignment(10.0, 12.0, 9.0, 22.0, 60), '')
        self.assertEqual(_check_alignment(9.5, 10.5, 9.5, 20.0, 30), '')

    def test_fin_avant_debut(self):
        self.assertEqual(
            _check_alignment(12.0, 10.0, 9.0, 22.0, 60), 'order')

    def test_hors_horaires(self):
        self.assertEqual(
            _check_alignment(8.0, 10.0, 9.0, 22.0, 60), 'hours')
        self.assertEqual(
            _check_alignment(21.0, 23.0, 9.0, 22.0, 60), 'hours')

    def test_hors_grille(self):
        # 10h15 sur un pas de 60 min ouvrant à 9h → refusé
        self.assertEqual(
            _check_alignment(10.25, 11.25, 9.0, 22.0, 60), 'grid')
        # …mais OK sur un pas de 30 min ? 10h15 non plus (9h + k×0,5)
        self.assertEqual(
            _check_alignment(10.25, 11.25, 9.0, 22.0, 30), 'grid')

    def test_grille_relative_a_l_ouverture(self):
        # Ouverture 9h30, pas 60 → 10h30 OK, 10h00 hors grille
        self.assertEqual(
            _check_alignment(10.5, 11.5, 9.5, 20.0, 60), '')
        self.assertEqual(
            _check_alignment(10.0, 11.0, 9.5, 20.0, 60), 'grid')


class TestFolioLineVals(unittest.TestCase):
    """Contrat du PMS : line_type service, product requis, quantité."""

    def test_vals_completes(self):
        vals = _folio_line_vals(7, 42, "Soin détente — RES/26/0001",
                                '2026-07-20', 1, 40000)
        self.assertEqual(vals['folio_id'], 7)
        self.assertEqual(vals['line_type'], 'service')
        self.assertEqual(vals['product_id'], 42)
        self.assertEqual(vals['quantity'], 1)
        self.assertEqual(vals['price_unit'], 40000)
        self.assertEqual(vals['date'], '2026-07-20')

    def test_quantite_pressing(self):
        vals = _folio_line_vals(7, 42, "Pressing chemises",
                                '2026-07-20', 8, 2500)
        self.assertEqual(vals['quantity'], 8)

    def test_quantite_zero_corrigee(self):
        vals = _folio_line_vals(7, 42, "x", '2026-07-20', 0, 100)
        self.assertEqual(vals['quantity'], 1)


class TestFillRate(unittest.TestCase):

    def test_nominal(self):
        # 26 h réservées / 65 h ouvrées (cabine 13 h × 5 j) = 40 %
        self.assertAlmostEqual(_fill_rate(26, 65), 40.0)

    def test_plafond_100(self):
        self.assertEqual(_fill_rate(80, 65), 100.0)

    def test_zero_ouvre(self):
        self.assertEqual(_fill_rate(10, 0), 0.0)


if __name__ == '__main__':
    unittest.main(verbosity=1)
