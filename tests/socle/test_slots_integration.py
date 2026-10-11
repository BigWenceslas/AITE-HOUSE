# -*- coding: utf-8 -*-
"""
Tests d'intégration du moteur Espaces & Prestations — miroirs fidèles
des règles serveur et du composant OWL : conflits sous capacité, règle
du cron no-show, clipping des couloirs du planning, positionnement des
blocs (laneStyle), agrégats KPI, mix par famille, scénarios métier
(journée SPA, pressing multi-pièces).
"""
import unittest
from datetime import datetime, timedelta


# Réimport des fonctions réelles via le module de tests logique
from test_slots_logic import (
    _overlap_count, _build_day_slots, _slot_price, _check_alignment,
    _fill_rate,
)


def conflict_blocked(existing, new_start, new_stop, capacity):
    """Miroir de _check_no_conflict : bloqué si used + 1 > capacité."""
    busy = [(s, e) for (s, e) in existing]
    used = _overlap_count(busy, new_start, new_stop)
    return used + 1 > capacity


def cron_no_show(bookings, now, grace_hours):
    """Miroir du cron : confirmées avec stop < now − grâce → no_show."""
    limit = now - timedelta(hours=grace_hours)
    out = []
    for (state, stop) in bookings:
        if state == 'confirmed' and stop < limit:
            out.append('no_show')
        else:
            out.append(state)
    return out


def clip_to_day(s_h, e_h, open_h, close_h):
    """Miroir du clipping des couloirs dans get_day_grid."""
    s = max(s_h, open_h)
    e = min(e_h, close_h)
    return (s, e) if e > s else None


def lane_style(start_h, stop_h, open_h, close_h):
    """Miroir de laneStyle (composant) : position en %."""
    span = (close_h - open_h) or 1
    left = (start_h - open_h) / span * 100
    width = (stop_h - start_h) / span * 100
    return round(left, 2), round(width, 2)


class TestConflitsCapacite(unittest.TestCase):

    D = datetime

    def test_capacite_1_double_reservation_bloquee(self):
        existing = [(self.D(2026, 7, 20, 10), self.D(2026, 7, 20, 12))]
        self.assertTrue(conflict_blocked(
            existing, self.D(2026, 7, 20, 11), self.D(2026, 7, 20, 13), 1))

    def test_creneaux_adjacents_autorises(self):
        existing = [(self.D(2026, 7, 20, 10), self.D(2026, 7, 20, 12))]
        self.assertFalse(conflict_blocked(
            existing, self.D(2026, 7, 20, 12), self.D(2026, 7, 20, 14), 1))

    def test_capacite_2_deux_ok_trois_bloque(self):
        one = [(self.D(2026, 7, 20, 10), self.D(2026, 7, 20, 12))]
        two = one + [(self.D(2026, 7, 20, 10), self.D(2026, 7, 20, 12))]
        new = (self.D(2026, 7, 20, 10, 30), self.D(2026, 7, 20, 11, 30))
        self.assertFalse(conflict_blocked(one, *new, 2))   # 2e OK
        self.assertTrue(conflict_blocked(two, *new, 2))    # 3e bloquée

    def test_annulees_ne_bloquent_pas(self):
        # Le domaine serveur exclut cancelled/no_show → liste vide ici
        self.assertFalse(conflict_blocked(
            [], self.D(2026, 7, 20, 10), self.D(2026, 7, 20, 12), 1))


class TestCronNoShow(unittest.TestCase):

    NOW = datetime(2026, 7, 20, 18, 0)

    def test_regle_de_grace(self):
        bookings = [
            ('confirmed', datetime(2026, 7, 20, 10)),   # fin +8h → no-show
            ('confirmed', datetime(2026, 7, 20, 14)),   # fin +4h → garde
            ('done', datetime(2026, 7, 20, 9)),         # réalisée → garde
            ('draft', datetime(2026, 7, 19, 10)),       # brouillon → garde
        ]
        out = cron_no_show(bookings, self.NOW, 6)
        self.assertEqual(out, ['no_show', 'confirmed', 'done', 'draft'])

    def test_grace_zero(self):
        bookings = [('confirmed', datetime(2026, 7, 20, 17, 59))]
        self.assertEqual(
            cron_no_show(bookings, self.NOW, 0), ['no_show'])


class TestClippingCouloirs(unittest.TestCase):

    def test_dans_les_horaires(self):
        self.assertEqual(clip_to_day(10.0, 12.0, 9.0, 22.0), (10.0, 12.0))

    def test_deborde_avant_ouverture(self):
        self.assertEqual(clip_to_day(8.0, 10.0, 9.0, 22.0), (9.0, 10.0))

    def test_deborde_apres_fermeture(self):
        self.assertEqual(clip_to_day(21.0, 23.5, 9.0, 22.0), (21.0, 22.0))

    def test_entierement_hors_plage(self):
        self.assertIsNone(clip_to_day(6.0, 8.0, 9.0, 22.0))


class TestLaneStyle(unittest.TestCase):
    """Positionnement des blocs du planning (miroir composant)."""

    def test_positions(self):
        # Ressource 9h-22h (13 h). Bloc 10h-12h.
        left, width = lane_style(10.0, 12.0, 9.0, 22.0)
        self.assertAlmostEqual(left, 7.69, places=1)
        self.assertAlmostEqual(width, 15.38, places=1)

    def test_pleine_journee(self):
        left, width = lane_style(9.0, 22.0, 9.0, 22.0)
        self.assertEqual((left, width), (0.0, 100.0))


class TestScenarioJourneeSpa(unittest.TestCase):
    """Journée type cabine SPA : 3 soins, 1 no-show, remplissage."""

    def test_journee(self):
        # Cabine 9h-19h (10 h ouvrées), capacité 1.
        done = [(10.0, 11.5), (14.0, 15.0)]        # 2,5 h réalisées
        confirmed = [(16.0, 17.5)]                 # 1,5 h à venir
        booked = sum(e - s for (s, e) in done + confirmed)
        self.assertEqual(booked, 4.0)
        self.assertAlmostEqual(_fill_rate(booked, 10.0), 40.0)

        # Grille : le 10h et le 14h et le 16h/17h occupés
        slots = _build_day_slots(9.0, 19.0, 60, done + confirmed, 1)
        full = [s['label'] for s in slots if s['state'] == 'full']
        self.assertEqual(full, ['10:00', '11:00', '14:00',
                                '16:00', '17:00'])

    def test_kpi_no_show_pct(self):
        # 2 réalisées + 1 confirmée + 1 no-show → 25 % (miroir get_kpis)
        done_n, confirmed_n, no_show_n = 2, 1, 1
        held = done_n + confirmed_n + no_show_n
        self.assertEqual(no_show_n / held * 100.0, 25.0)


class TestScenarioPressing(unittest.TestCase):

    def test_depot_8_chemises(self):
        # Dépôt 30 min, 8 chemises × 2 500 → 20 000, retrait à J+2
        amount = _slot_price(2500, 8, 0.5, 0, 0)
        self.assertEqual(amount, 20000)
        # Report au folio : prix unitaire = montant / qté
        self.assertEqual(amount / 8, 2500)

    def test_alignement_depot(self):
        # Comptoir 8h-18h pas 30 : dépôt 9h30-10h valide
        self.assertEqual(_check_alignment(9.5, 10.0, 8.0, 18.0, 30), '')


class TestMixParFamille(unittest.TestCase):
    """Miroir de get_service_mix : CA réalisé agrégé par famille."""

    def test_agregation_et_tri(self):
        rows = [('spa', 40000), ('hair', 15000), ('spa', 55000),
                ('space', 75000), ('pressing', 20000)]
        agg = {}
        for k, v in rows:
            agg[k] = agg.get(k, 0) + v
        ordered = sorted(agg.items(), key=lambda kv: -kv[1])
        self.assertEqual(ordered[0], ('spa', 95000))
        self.assertEqual(ordered[1], ('space', 75000))
        self.assertEqual(sum(agg.values()), 205000)


class TestOuvertureHeuresKpi(unittest.TestCase):
    """Miroir des heures ouvrées de get_kpis (capacité × jours)."""

    def test_heures_ouvrees(self):
        # 2 fauteuils (capacité 2, 9h-19h) + 1 cabine (9h-19h), 5 jours
        resources = [(9.0, 19.0, 2), (9.0, 19.0, 1)]
        days = 5
        open_hours = sum((c - o) * cap for (o, c, cap) in resources) * days
        self.assertEqual(open_hours, 150.0)
        self.assertAlmostEqual(_fill_rate(45.0, open_hours), 30.0)


if __name__ == '__main__':
    unittest.main(verbosity=1)
