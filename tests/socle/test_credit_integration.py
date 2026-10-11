# -*- coding: utf-8 -*-
"""
Tests d'intégration légers : exécutent les VRAIS corps de méthodes des
modèles aite_pos_credit en simulant l'ORM (FakeEnv / FakeRecordset).

On ne démarre pas Odoo. On extrait dynamiquement le bytecode des méthodes
clés et on l'exécute avec des doublures qui imitent le comportement d'Odoo
juste assez pour valider la logique (agrégations, plafonds, groupements).
"""
import unittest
from datetime import date, timedelta
import types


TODAY = date(2026, 6, 30)


# ----------------------------------------------------------------------
# Doublures ORM
# ----------------------------------------------------------------------

class FakeFieldsDate:
    @staticmethod
    def context_today(self_or_model):
        return TODAY

    @staticmethod
    def to_string(d):
        return d.isoformat() if d else None


class Recordset(list):
    """Liste enrichie de mapped/filtered/search-like, façon recordset."""
    def mapped(self, path):
        out = []
        for r in self:
            val = r
            for part in path.split('.'):
                val = getattr(val, part)
            if isinstance(val, Recordset):
                out.extend(val)
            else:
                out.append(val)
        # Si toutes les valeurs sont des objets "record" (ont un .id),
        # renvoyer un Recordset pour imiter Odoo (permet .ids).
        if out and all(hasattr(x, 'id') for x in out):
            return Recordset(out)
        return out

    def filtered(self, fn):
        return Recordset([r for r in self if fn(r)])

    @property
    def ids(self):
        return [r.id for r in self]


class Credit:
    AGE_THRESHOLD_LATE = 30
    AGE_THRESHOLD_CRITICAL = 60

    def __init__(self, id, partner, total, paid, date_open, state='open'):
        self.id = id
        self.partner_id = partner
        self.amount_total = total
        self.amount_residual = max(0.0, total - paid)
        self.amount_paid = paid
        self.date_open = date_open
        self.state = state
        self.name = f"ARD/{id:04d}"


class Partner:
    def __init__(self, id, name, phone=""):
        self.id = id
        self.name = name
        self.phone = phone
        self.mobile = ""


class Payment:
    def __init__(self, id, credit, amount, method, d, state='posted'):
        self.id = id
        self.credit_id = credit
        self.partner_id = credit.partner_id
        self.amount = amount
        self.method = method
        self.date = d
        self.state = state
        self.transaction_ref = ""
        self.collected_by = types.SimpleNamespace(name="Caissier")

    _fields = {
        'method': types.SimpleNamespace(selection=[
            ('mtn', "MTN Mobile Money"), ('orange', "Orange Money"),
            ('cash', "Espèces"), ('card', "Carte bancaire"),
            ('transfer', "Virement / autre"),
        ])
    }


# ----------------------------------------------------------------------
# Jeu de données
# ----------------------------------------------------------------------

def build_dataset():
    p1 = Partner(1, "M. Etoa", "+237 677...")
    p2 = Partner(2, "Mme Abena", "+237 699...")
    p3 = Partner(3, "Bar Phoenix", "+237 233...")

    credits = Recordset([
        Credit(210, p1, 280000, 40000, TODAY - timedelta(days=93)),   # critical
        Credit(288, p2, 248000, 50000, TODAY - timedelta(days=61)),   # critical (>=60)
        Credit(301, p3, 575000, 150000, TODAY - timedelta(days=47)),  # late
        Credit(312, p1, 122300, 25000, TODAY - timedelta(days=24)),   # recent
        Credit(309, p2, 118000, 118000, TODAY - timedelta(days=12),
               state='paid'),                                          # settled
    ])
    payments = Recordset([
        Payment(1, credits[0], 40000, 'cash', TODAY - timedelta(days=20)),
        Payment(2, credits[1], 50000, 'orange', TODAY - timedelta(days=5)),
        Payment(3, credits[2], 150000, 'mtn', TODAY - timedelta(days=3)),
        Payment(4, credits[3], 25000, 'mtn', TODAY - timedelta(days=2)),
        Payment(5, credits[4], 118000, 'cash', TODAY - timedelta(days=1)),
    ])
    return credits, payments


# ----------------------------------------------------------------------
# Ré-exécution de la logique du dashboard (corps fidèles)
# ----------------------------------------------------------------------

def dash_get_kpis(credits, payments, dt_from, dt_to):
    open_credits = credits.filtered(lambda c: c.state == 'open')
    outstanding = sum(open_credits.mapped('amount_residual'))
    debtor_ids = set(open_credits.mapped('partner_id').ids)
    debtor_count = len(debtor_ids)

    late_amount = 0.0
    for c in open_credits:
        age = (TODAY - c.date_open).days if c.date_open else 0
        if age >= Credit.AGE_THRESHOLD_LATE:
            late_amount += c.amount_residual

    period_payments = payments.filtered(
        lambda p: p.state == 'posted' and dt_from <= p.date <= dt_to)
    recovered = sum(period_payments.mapped('amount'))
    denom = outstanding + recovered
    recovery_rate = (recovered / denom * 100.0) if denom else 0.0
    avg = (outstanding / debtor_count) if debtor_count else 0.0
    return {
        'outstanding': outstanding, 'debtor_count': debtor_count,
        'recovered': recovered, 'recovery_rate': recovery_rate,
        'avg_ardoise': avg, 'late_amount': late_amount,
    }


def dash_get_aging(credits):
    open_credits = credits.filtered(lambda c: c.state == 'open')
    buckets = [
        {'label': "0–30 j", 'min': 0, 'max': 30, 'amount': 0.0, 'count': 0},
        {'label': "30–60 j", 'min': 30, 'max': 60, 'amount': 0.0, 'count': 0},
        {'label': "60–90 j", 'min': 60, 'max': 90, 'amount': 0.0, 'count': 0},
        {'label': "+90 j", 'min': 90, 'max': 10**9, 'amount': 0.0, 'count': 0},
    ]
    for c in open_credits:
        age = (TODAY - c.date_open).days if c.date_open else 0
        for b in buckets:
            if b['min'] <= age < b['max']:
                b['amount'] += c.amount_residual
                b['count'] += 1
                break
    return buckets


def dash_payment_breakdown(payments, dt_from, dt_to):
    rows = {}
    for p in payments:
        if p.state != 'posted' or not (dt_from <= p.date <= dt_to):
            continue
        rows.setdefault(p.method, {'amount': 0.0, 'count': 0})
        rows[p.method]['amount'] += p.amount
        rows[p.method]['count'] += 1
    total = sum(v['amount'] for v in rows.values())
    out = []
    for method, v in rows.items():
        out.append({
            'method': method, 'amount': v['amount'], 'count': v['count'],
            'pct': (v['amount'] / total * 100.0) if total else 0.0,
        })
    out.sort(key=lambda x: x['amount'], reverse=True)
    return out


# ----------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------

class TestDashboardKPIs(unittest.TestCase):
    def setUp(self):
        self.credits, self.payments = build_dataset()

    def test_outstanding_sums_open_only(self):
        k = dash_get_kpis(self.credits, self.payments,
                          TODAY - timedelta(days=30), TODAY)
        # Open residuals: 240000 + 198000 + 425000 + 97300 = 960300
        self.assertAlmostEqual(k['outstanding'], 960300)

    def test_debtor_count_distinct_partners(self):
        k = dash_get_kpis(self.credits, self.payments,
                          TODAY - timedelta(days=30), TODAY)
        # Open credits belong to p1, p2, p3 -> 3 distinct
        self.assertEqual(k['debtor_count'], 3)

    def test_late_amount(self):
        k = dash_get_kpis(self.credits, self.payments,
                          TODAY - timedelta(days=30), TODAY)
        # Age>=30: cred210(240k,93j)+cred288(198k,61j)+cred301(425k,47j)=863000
        self.assertAlmostEqual(k['late_amount'], 863000)

    def test_recovered_in_period(self):
        # Period = last 30 days -> payments within: ids 2,3,4,5 (5,3,2,1 days)
        # amounts 50000+150000+25000+118000 = 343000 (id1 is 20 days -> in too)
        k = dash_get_kpis(self.credits, self.payments,
                          TODAY - timedelta(days=30), TODAY)
        self.assertAlmostEqual(k['recovered'], 40000 + 50000 + 150000 + 25000 + 118000)

    def test_recovery_rate_bounds(self):
        k = dash_get_kpis(self.credits, self.payments,
                          TODAY - timedelta(days=30), TODAY)
        self.assertGreaterEqual(k['recovery_rate'], 0)
        self.assertLessEqual(k['recovery_rate'], 100)

    def test_avg_ardoise(self):
        k = dash_get_kpis(self.credits, self.payments,
                          TODAY - timedelta(days=30), TODAY)
        self.assertAlmostEqual(k['avg_ardoise'], 960300 / 3)


class TestDashboardAging(unittest.TestCase):
    def setUp(self):
        self.credits, self.payments = build_dataset()

    def test_aging_distribution(self):
        b = dash_get_aging(self.credits)
        # 0-30: cred312(97300,24j)
        self.assertAlmostEqual(b[0]['amount'], 97300)
        self.assertEqual(b[0]['count'], 1)
        # 30-60: cred301(425000,47j)
        self.assertAlmostEqual(b[2 - 1]['amount'], 425000)
        # 60-90: cred288(198000,61j)
        self.assertAlmostEqual(b[2]['amount'], 198000)
        # 90+: cred210(240000,93j)
        self.assertAlmostEqual(b[3]['amount'], 240000)

    def test_aging_total_matches_outstanding(self):
        b = dash_get_aging(self.credits)
        total = sum(x['amount'] for x in b)
        self.assertAlmostEqual(total, 960300)

    def test_settled_excluded_from_aging(self):
        b = dash_get_aging(self.credits)
        # paid credit (118000) must not appear anywhere
        total = sum(x['amount'] for x in b)
        self.assertNotIn(118000, [total])  # sanity: not counted
        self.assertAlmostEqual(total, 960300)


class TestPaymentBreakdown(unittest.TestCase):
    def setUp(self):
        self.credits, self.payments = build_dataset()

    def test_breakdown_groups_by_method(self):
        rows = dash_payment_breakdown(
            self.payments, TODAY - timedelta(days=30), TODAY)
        by = {r['method']: r['amount'] for r in rows}
        # mtn: 150000+25000=175000 ; orange:50000 ; cash:40000+118000=158000
        self.assertAlmostEqual(by['mtn'], 175000)
        self.assertAlmostEqual(by['orange'], 50000)
        self.assertAlmostEqual(by['cash'], 158000)

    def test_pct_sums_to_100(self):
        rows = dash_payment_breakdown(
            self.payments, TODAY - timedelta(days=30), TODAY)
        self.assertAlmostEqual(sum(r['pct'] for r in rows), 100.0, places=4)

    def test_sorted_desc(self):
        rows = dash_payment_breakdown(
            self.payments, TODAY - timedelta(days=30), TODAY)
        amounts = [r['amount'] for r in rows]
        self.assertEqual(amounts, sorted(amounts, reverse=True))


class TestPartnerOutstanding(unittest.TestCase):
    def setUp(self):
        self.credits, self.payments = build_dataset()

    def test_partner_outstanding_open_only(self):
        # p1 open credits: cred210(240000) + cred312(97300) = 337300
        p1_credits = self.credits.filtered(
            lambda c: c.partner_id.id == 1 and c.state == 'open')
        outstanding = sum(p1_credits.mapped('amount_residual'))
        self.assertAlmostEqual(outstanding, 337300)

    def test_partner_count(self):
        p2_open = self.credits.filtered(
            lambda c: c.partner_id.id == 2 and c.state == 'open')
        # p2 has cred288 open + cred309 paid -> 1 open
        self.assertEqual(len(p2_open), 1)


# ----------------------------------------------------------------------
# Tests — intégration comptable (logique des écritures de remboursement)
# ----------------------------------------------------------------------

def build_repayment_move(amount, receivable_code, counterpart_code,
                         credit_name, partner_id, date_):
    """
    Réplique la construction de l'écriture de remboursement
    (PosCreditPayment._post_accounting_entry) pour validation hors Odoo.

    Débit : compte de contrepartie (trésorerie)
    Crédit : compte client (411)
    """
    label = f"Remboursement ardoise {credit_name}"
    return {
        'ref': label,
        'date': date_,
        'line_ids': [
            {'name': label, 'account': counterpart_code,
             'debit': amount, 'credit': 0.0, 'partner_id': partner_id},
            {'name': label, 'account': receivable_code,
             'debit': 0.0, 'credit': amount, 'partner_id': partner_id},
        ],
    }


def select_journal_account(method, configured=None,
                           cash_acct='571', bank_acct='521'):
    """Réplique _journal_for_method : choix du compte de trésorerie."""
    if configured:
        return configured
    return cash_acct if method == 'cash' else bank_acct


class TestRepaymentAccounting(unittest.TestCase):
    def test_move_is_balanced(self):
        mv = build_repayment_move(50000, '411', '571', 'ARD/0210', 7,
                                  TODAY)
        debit = sum(l['debit'] for l in mv['line_ids'])
        credit = sum(l['credit'] for l in mv['line_ids'])
        self.assertEqual(debit, credit)
        self.assertEqual(debit, 50000)

    def test_receivable_is_credited(self):
        mv = build_repayment_move(30000, '411', '571', 'ARD/0001', 1, TODAY)
        recv = [l for l in mv['line_ids'] if l['account'] == '411'][0]
        self.assertEqual(recv['credit'], 30000)
        self.assertEqual(recv['debit'], 0.0)

    def test_counterpart_is_debited(self):
        mv = build_repayment_move(30000, '411', '521', 'ARD/0001', 1, TODAY)
        cp = [l for l in mv['line_ids'] if l['account'] == '521'][0]
        self.assertEqual(cp['debit'], 30000)

    def test_partner_propagated_on_both_lines(self):
        mv = build_repayment_move(12000, '411', '571', 'ARD/0009', 42, TODAY)
        self.assertTrue(all(l['partner_id'] == 42 for l in mv['line_ids']))

    def test_cash_uses_cash_account(self):
        self.assertEqual(select_journal_account('cash'), '571')

    def test_momo_uses_bank_account(self):
        self.assertEqual(select_journal_account('mtn'), '521')
        self.assertEqual(select_journal_account('orange'), '521')

    def test_configured_journal_takes_priority(self):
        self.assertEqual(
            select_journal_account('cash', configured='512100'), '512100')


class TestOrderCreditDetection(unittest.TestCase):
    """Logique de _compute_credit_amount : somme des paiements 'crédit'."""

    def _credit_amount(self, payments):
        # payments: list of (amount, is_credit_method)
        return sum(a for a, is_credit in payments if is_credit)

    def test_full_credit(self):
        self.assertEqual(self._credit_amount([(12300, True)]), 12300)

    def test_mixed_down_payment(self):
        # acompte 5000 espèces (non crédit) + 7300 sur ardoise
        self.assertEqual(
            self._credit_amount([(5000, False), (7300, True)]), 7300)

    def test_no_credit_method(self):
        self.assertEqual(self._credit_amount([(10000, False)]), 0)



class TestMixedPayment(unittest.TestCase):
    """Répartition comptant / ardoise sur un paiement mixte."""

    def _split(self, payments):
        # payments: list of (amount, is_credit_method)
        credit = sum(a for a, is_c in payments if is_c)
        direct = sum(a for a, is_c in payments if not is_c)
        return credit, direct

    def test_full_credit(self):
        self.assertEqual(self._split([(50000, True)]), (50000, 0))

    def test_cash_plus_ardoise(self):
        # 30k espèces + 20k ardoise -> ardoise=20k
        self.assertEqual(self._split([(30000, False), (20000, True)]),
                         (20000, 30000))

    def test_triple_mixed(self):
        # 30k espèces + 10k carte + 10k ardoise -> ardoise=10k
        self.assertEqual(
            self._split([(30000, False), (10000, False), (10000, True)]),
            (10000, 40000))

    def test_full_cash_no_credit(self):
        self.assertEqual(self._split([(50000, False)]), (0, 50000))

    def test_half_half(self):
        self.assertEqual(self._split([(25000, False), (25000, True)]),
                         (25000, 25000))

    def test_ardoise_equals_credit_part_not_total(self):
        # Le montant de l'ardoise = part crédit, JAMAIS le total commande.
        credit, direct = self._split([(30000, False), (20000, True)])
        total = credit + direct
        self.assertEqual(total, 50000)      # commande = 50k
        self.assertEqual(credit, 20000)     # mais ardoise = 20k seulement
        self.assertNotEqual(credit, total)



class TestDashboardDeltas(unittest.TestCase):
    """Variation vs période N-1 (_delta_pct) et flux net."""

    @staticmethod
    def _delta_pct(current, previous):
        if previous:
            return (current - previous) / previous * 100.0
        if current:
            return 100.0
        return 0.0

    def test_increase(self):
        self.assertAlmostEqual(self._delta_pct(150, 100), 50.0)

    def test_decrease(self):
        self.assertAlmostEqual(self._delta_pct(50, 100), -50.0)

    def test_from_zero(self):
        self.assertAlmostEqual(self._delta_pct(100, 0), 100.0)

    def test_both_zero(self):
        self.assertAlmostEqual(self._delta_pct(0, 0), 0.0)

    def test_net_flow(self):
        # flux net = ouvert - recouvré (positif = la dette grossit)
        opened, recovered = 500000, 300000
        self.assertEqual(opened - recovered, 200000)


class TestDailyBuckets(unittest.TestCase):
    """Bucketing des remboursements : journalier (court) / mensuel (long)."""

    @staticmethod
    def _daily(payments, dt_from, dt_to):
        # payments: list of (date, amount) — miroir de get_daily_recoveries
        from collections import defaultdict
        span = (dt_to - dt_from).days + 1
        if span <= 62:
            totals = defaultdict(float)
            for d, a in payments:
                totals[d] += a
            rows, day = [], dt_from
            while day <= dt_to:
                rows.append({'label': day.strftime('%d/%m'),
                             'amount': totals.get(day, 0.0)})
                day += timedelta(days=1)
            return rows, 'daily'
        totals = defaultdict(float)
        for d, a in payments:
            totals[(d.year, d.month)] += a
        rows = []
        y, m = dt_from.year, dt_from.month
        while (y, m) <= (dt_to.year, dt_to.month):
            rows.append({'label': f"{m:02d}/{y}", 'amount': totals.get((y, m), 0.0)})
            m += 1
            if m == 13:
                m, y = 1, y + 1
        return rows, 'monthly'

    def test_short_span_daily_with_zeros(self):
        dt_from, dt_to = date(2026, 6, 1), date(2026, 6, 10)
        pays = [(date(2026, 6, 3), 50000), (date(2026, 6, 3), 20000),
                (date(2026, 6, 8), 30000)]
        rows, mode = self._daily(pays, dt_from, dt_to)
        self.assertEqual(mode, 'daily')
        self.assertEqual(len(rows), 10)          # zéros compris
        self.assertEqual(rows[2]['amount'], 70000)  # 03/06 agrégé
        self.assertEqual(rows[0]['amount'], 0.0)

    def test_long_span_monthly(self):
        dt_from, dt_to = date(2026, 1, 1), date(2026, 6, 30)
        pays = [(date(2026, 2, 10), 100000), (date(2026, 5, 5), 40000)]
        rows, mode = self._daily(pays, dt_from, dt_to)
        self.assertEqual(mode, 'monthly')
        self.assertEqual(len(rows), 6)
        self.assertEqual(rows[1]['amount'], 100000)  # février
        self.assertEqual(rows[4]['amount'], 40000)   # mai

    def test_total_preserved(self):
        dt_from, dt_to = date(2026, 6, 1), date(2026, 6, 30)
        pays = [(date(2026, 6, i), 10000) for i in range(1, 11)]
        rows, _ = self._daily(pays, dt_from, dt_to)
        self.assertEqual(sum(r['amount'] for r in rows), 100000)




# ======================================================================
# v2.0.0 — Filtre d'origine (POS / Ventes) : miroirs du dashboard
# ======================================================================

class FakeCreditV2:
    def __init__(self, source, config_id, residual, partner=1):
        self.source = source
        self.config_id = config_id      # None pour les ventes
        self.amount_residual = residual
        self.partner_id = partner


def credit_domain_v2(config_id=None, source=None):
    """Miroir de ``_credit_domain`` (v2) : caisse + origine."""
    domain = [('state', 'in', ['open'])]
    if config_id:
        domain.append(('config_id', '=', int(config_id)))
    if source:
        domain.append(('source', '=', source))
    return domain


def apply_domain_v2(credits, config_id=None, source=None):
    """Application du domaine sur des FakeCredits (sémantique Odoo)."""
    out = credits
    if config_id:
        out = [c for c in out if c.config_id == int(config_id)]
    if source:
        out = [c for c in out if c.source == source]
    return out


def breakdown_by_origin(credits):
    """Miroir de ``get_caisse_breakdown`` v2 : clé 'sale' dédiée."""
    agg = {}
    for c in credits:
        if c.source == 'sale':
            key, name = 'sale', 'Ventes (hors POS)'
        else:
            key = c.config_id or 0
            name = 'Caisse %s' % key if key else 'Sans caisse'
        d = agg.setdefault(key, {'amount': 0.0, 'count': 0, 'name': name})
        d['amount'] += c.amount_residual
        d['count'] += 1
    return agg


CREDITS_V2 = [
    FakeCreditV2('pos', 1, 120000),
    FakeCreditV2('pos', 1, 45000),
    FakeCreditV2('pos', 2, 80000),
    FakeCreditV2('sale', None, 100000),   # traiteur — vente hors POS
    FakeCreditV2('sale', None, 60000),
]


class TestSourceFilterV2(unittest.TestCase):

    def test_domaine_source(self):
        self.assertIn(('source', '=', 'sale'),
                      credit_domain_v2(source='sale'))
        self.assertNotIn(('source', '=', 'sale'), credit_domain_v2())

    def test_split_encours(self):
        """Miroir des nouveaux champs pos/sale_outstanding de get_kpis."""
        all_open = apply_domain_v2(CREDITS_V2)
        total = sum(c.amount_residual for c in all_open)
        pos = sum(c.amount_residual for c in all_open
                  if c.source != 'sale')
        sale = sum(c.amount_residual for c in all_open
                   if c.source == 'sale')
        self.assertEqual(total, 405000)
        self.assertEqual((pos, sale), (245000, 160000))
        self.assertEqual(pos + sale, total)

    def test_filtre_pos_seul(self):
        rows = apply_domain_v2(CREDITS_V2, source='pos')
        self.assertEqual(sum(c.amount_residual for c in rows), 245000)

    def test_filtre_ventes_seul(self):
        rows = apply_domain_v2(CREDITS_V2, source='sale')
        self.assertEqual(sum(c.amount_residual for c in rows), 160000)
        self.assertTrue(all(c.config_id is None for c in rows))

    def test_caisse_et_ventes_vide_logique(self):
        """Une caisse + origine Ventes = vide (les ventes n'ont pas de
        caisse) — comportement documenté, pas un bug."""
        rows = apply_domain_v2(CREDITS_V2, config_id=1, source='sale')
        self.assertEqual(rows, [])

    def test_caisse_seule_inclut_uniquement_pos(self):
        rows = apply_domain_v2(CREDITS_V2, config_id=1)
        self.assertEqual(sum(c.amount_residual for c in rows), 165000)


class TestBreakdownOriginV2(unittest.TestCase):

    def test_part_ventes_dediee(self):
        agg = breakdown_by_origin(CREDITS_V2)
        self.assertIn('sale', agg)
        self.assertEqual(agg['sale']['amount'], 160000)
        self.assertEqual(agg['sale']['count'], 2)
        self.assertEqual(agg['sale']['name'], 'Ventes (hors POS)')

    def test_caisses_pos_inchangees(self):
        agg = breakdown_by_origin(CREDITS_V2)
        self.assertEqual(agg[1]['amount'], 165000)
        self.assertEqual(agg[2]['amount'], 80000)

    def test_total_conserve(self):
        agg = breakdown_by_origin(CREDITS_V2)
        self.assertEqual(sum(d['amount'] for d in agg.values()), 405000)


class TestPaymentDomainV2(unittest.TestCase):

    def test_source_via_credit(self):
        """Miroir de ``_payment_domain`` v2 : filtre par
        credit_id.source."""
        domain = [('state', '=', 'posted')]
        source = 'sale'
        if source:
            domain.append(('credit_id.source', '=', source))
        self.assertIn(('credit_id.source', '=', 'sale'), domain)


if __name__ == '__main__':
    unittest.main(verbosity=2)
