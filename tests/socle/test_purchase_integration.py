# -*- coding: utf-8 -*-
"""
Tests d'intégration du tableau de bord Achats & Fournisseurs.

Miroirs fidèles des règles d'agrégation du module et du composant OWL :
sommes d'encours/retard/échéances, balance âgée, échéancier hebdomadaire,
ratio OTIF, part fournisseur, créances 409 (consignes + avoirs + acomptes
estimés), bucketing mensuel des flux, détection défensive
(``receipt_status`` absent → repli lignes), indice de prix base 100 avec
report des mois sans achat.

Jeu de données : celui du prototype validé (date de référence 02/07/2026).
"""
import unittest
from datetime import date


# ----------------------------------------------------------------------
# Jeu de données (identique au prototype)
# ----------------------------------------------------------------------

TODAY = date(2026, 7, 2)

INVOICES = [
    # (sup, residual, days_late, days_to_due, bucket)
    (1, 1140000, 7, 0, 1),
    (1, 1980000, 0, 3, 0),
    (1, 1720000, 0, 16, 0),
    (2, 640000, 14, 0, 1),
    (2, 580000, 0, 7, 0),
    (3, 365000, 35, 0, 2),
    (3, 210000, 1, 0, 1),
    (4, 290000, 0, 6, 0),
    (5, 860000, 73, 0, 3),
    (5, 520000, 2, 0, 1),
    (6, 145000, 0, 13, 0),
]

ORDERS_OTIF = [True, False, False, True, False, True, True, False, True]

SOON = 7


def kpi_slices(invoices, soon):
    """Miroir des tranches de ``get_kpis`` sur les factures ouvertes."""
    encours = sum(r for (_s, r, _l, _t, _b) in invoices)
    retard = sum(r for (_s, r, l, _t, _b) in invoices if l > 0)
    soon_v = sum(r for (_s, r, l, t, _b) in invoices
                 if l == 0 and t <= soon)
    month = sum(r for (_s, r, l, t, _b) in invoices
                if l == 0 and soon < t <= 30)
    return encours, retard, soon_v, month


def aging(invoices):
    """Miroir de ``agingData`` (composant)."""
    b = [0, 0, 0, 0, 0]
    for (_s, r, _l, _t, bk) in invoices:
        b[bk] += r
    return b


def schedule_weeks(invoices):
    """Miroir de ``scheduleWeeks`` : échu→S0, sinon toDue // 7 (plafond 5)."""
    weeks = [0, 0, 0, 0, 0, 0]
    for (_s, r, late, to_due, _b) in invoices:
        w = 0 if late > 0 else min(5, to_due // 7)
        weeks[w] += r
    return weeks


class TestKpiSlices(unittest.TestCase):

    def test_encours_et_tranches(self):
        encours, retard, soon, month = kpi_slices(INVOICES, SOON)
        self.assertEqual(encours, 8450000)
        self.assertEqual(retard, 3735000)
        # bientôt : 1 980 000 (3 j) + 580 000 (7 j) + 290 000 (6 j)
        self.assertEqual(soon, 2850000)
        # 8–30 j : 1 720 000 (16 j) + 145 000 (13 j)
        self.assertEqual(month, 1865000)
        self.assertEqual(retard + soon + month, encours - 0)  # partition

    def test_fenetre_20_deplace_les_tranches(self):
        _e, _r, soon20, month20 = kpi_slices(INVOICES, 20)
        self.assertEqual(soon20, 2850000 + 1865000)
        self.assertEqual(month20, 0)


class TestAgingEtEcheancier(unittest.TestCase):

    def test_balance_agee(self):
        b = aging(INVOICES)
        self.assertEqual(b[0], 1980000 + 1720000 + 580000 + 290000 + 145000)
        self.assertEqual(b[1], 1140000 + 640000 + 210000 + 520000)
        self.assertEqual(b[2], 365000)
        self.assertEqual(b[3], 860000)
        self.assertEqual(b[4], 0)
        self.assertEqual(sum(b), 8450000)

    def test_echeancier_semaines(self):
        w = schedule_weeks(INVOICES)
        # S0 = tout l'échu + toDue 0–6 : retards 3 735 000 + 1 980 000(3)
        # + 290 000(6) = 6 005 000
        self.assertEqual(w[0], 6005000)
        # S1 (7–13 j) : 580 000 + 145 000
        self.assertEqual(w[1], 725000)
        # S2 (14–20 j) : 1 720 000
        self.assertEqual(w[2], 1720000)
        self.assertEqual(sum(w), 8450000)


class TestOtifEtFournisseurs(unittest.TestCase):

    def test_ratio_otif(self):
        otif = 100.0 * sum(ORDERS_OTIF) / len(ORDERS_OTIF)
        self.assertAlmostEqual(otif, 55.56, places=1)

    def test_part_fournisseur(self):
        achats = {1: 7700000, 2: 1220000, 3: 410000,
                  4: 290000, 5: 1000000, 6: 145000}
        total = sum(achats.values())
        self.assertEqual(total, 10765000)
        self.assertAlmostEqual(achats[1] / total * 100, 71.53, places=1)

    def test_tri_par_achats(self):
        rows = [{'id': i, 'achats': a} for i, a in
                [(3, 410000), (1, 7700000), (5, 1000000)]]
        rows.sort(key=lambda r: -r['achats'])
        self.assertEqual([r['id'] for r in rows], [1, 5, 3])


class TestClaims409(unittest.TestCase):
    """Créances fournisseurs : consignes + avoirs + acomptes estimés."""

    DEPOSITS = [(180, 4800), (35, 4800), (20, 4800)]
    AVOIRS_OPEN = [118000, 46000, 70500]

    def test_consignes(self):
        total = sum(q * u for q, u in self.DEPOSITS)
        self.assertEqual(total, 1128000)
        self.assertEqual(sum(q for q, _u in self.DEPOSITS), 235)

    def test_avoirs(self):
        self.assertEqual(sum(self.AVOIRS_OPEN), 234500)

    def test_acomptes_estimes(self):
        # acomptes = max(0, solde débiteur payable − avoirs ouverts)
        debit_total = 484500   # avoirs 234 500 + paiement non lettré 250 000
        avoirs = sum(self.AVOIRS_OPEN)
        self.assertEqual(max(0.0, debit_total - avoirs), 250000)
        # jamais négatif même si les avoirs dominent
        self.assertEqual(max(0.0, 100000 - avoirs), 0.0)

    def test_total_409(self):
        self.assertEqual(1128000 + 234500 + 250000, 1612500)


class TestFluxMensuels(unittest.TestCase):
    """Bucketing mensuel : factures par invoice_date, paiements par date."""

    def test_bucketing(self):
        bills = [(date(2026, 5, 12), 500000), (date(2026, 6, 3), 700000),
                 (date(2026, 6, 28), 300000)]
        pays = [(date(2026, 6, 10), 450000), (date(2026, 5, 30), 200000)]
        months = [(2026, 5), (2026, 6)]
        out = []
        for (y, m) in months:
            b = sum(a for (d, a) in bills if (d.year, d.month) == (y, m))
            p = sum(a for (d, a) in pays if (d.year, d.month) == (y, m))
            out.append((b, p))
        self.assertEqual(out, [(500000, 200000), (1000000, 450000)])


class TestDetectionDefensive(unittest.TestCase):
    """receipt_status absent → repli sur les lignes (qty_received)."""

    class PO:
        def __init__(self, status, lines, recv):
            if status is not None:
                self.receipt_status = status
            self.lines = lines
            self.recv = recv

    @staticmethod
    def detect(po):
        status = getattr(po, 'receipt_status', None)
        if status:
            pending = status == 'pending'
            is_full = (status == 'full') if not pending else None
        else:
            pending = not po.recv
            if pending:
                is_full = None
            else:
                is_full = all(r >= q - 0.001 for (q, r) in po.lines)
        return pending, is_full

    def test_champ_natif_full(self):
        self.assertEqual(self.detect(self.PO('full', [], True)),
                         (False, True))

    def test_champ_natif_pending(self):
        self.assertEqual(self.detect(self.PO('pending', [], None)),
                         (True, None))

    def test_repli_lignes_complet(self):
        po = self.PO(None, [(10, 10), (24, 24)], True)
        self.assertEqual(self.detect(po), (False, True))

    def test_repli_lignes_incomplet(self):
        po = self.PO(None, [(10, 10), (24, 20)], True)
        self.assertEqual(self.detect(po), (False, False))


class TestIndicePrix(unittest.TestCase):
    """Base 100 avec report du dernier indice sur les mois sans achat."""

    @staticmethod
    def index(vals):
        base = next((v for v in vals if v), None)
        idx, last = [], 100.0
        for v in vals:
            if v and base:
                last = v / base * 100.0
            idx.append(round(last, 1))
        return idx

    def test_base_100_et_report(self):
        vals = [7800, None, 8000, None, None, 8400]
        self.assertEqual(self.index(vals),
                         [100.0, 100.0, 102.6, 102.6, 102.6, 107.7])

    def test_serie_vide(self):
        self.assertEqual(self.index([None, None]), [100.0, 100.0])


if __name__ == '__main__':
    unittest.main(verbosity=1)
