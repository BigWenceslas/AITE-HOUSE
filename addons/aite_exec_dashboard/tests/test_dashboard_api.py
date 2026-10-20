# -*- coding: utf-8 -*-
"""Tableau de bord exécutif : consolidation hôtel + POS + prestations."""
from datetime import timedelta

from odoo import fields
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install', 'aite_exec')
class TestExecDashboard(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.env.user.tz = 'UTC'
        cls.dashboard = cls.env['aite.exec.dashboard']
        cls.today = fields.Date.context_today(cls.env.user)

        cls.hotel = cls.env['aite.hotel.hotel'].create({
            'name': "Hôtel Exec",
            'code': 'EXE',
            'company_id': cls.company.id,
        })
        cls.rtype = cls.env['aite.hotel.room.type'].create({
            'name': "Chambre Exec",
            'company_id': cls.company.id,
            'base_price': 80000.0,
            'capacity_adults': 2,
        })
        cls.rtype.product_id.sudo().write({'taxes_id': [(5, 0, 0)]})
        cls.room = cls.env['aite.hotel.room'].create({
            'name': 'EX1',
            'hotel_id': cls.hotel.id,
            'room_type_id': cls.rtype.id,
        })
        cls.guest = cls.env['res.partner'].create({'name': "Client Exec"})

    def _stay(self):
        Res = self.env['aite.hotel.reservation']
        reservation = Res.create({
            'hotel_id': self.hotel.id,
            'partner_id': self.guest.id,
            'checkin_date': Res._compose_datetime(self.today, 14.0),
            'checkout_date': Res._compose_datetime(
                self.today + timedelta(days=2), 12.0),
            'line_ids': [(0, 0, {
                'room_type_id': self.rtype.id,
                'room_id': self.room.id,
                'adults': 1,
            })],
        })
        reservation.action_confirm()
        self.env.flush_all()
        return reservation

    def _endpoints(self, date_from, date_to):
        d = self.dashboard
        return [
            ('get_meta', lambda: d.get_meta()),
            ('get_kpis', lambda: d.get_kpis(date_from, date_to)),
            ('get_evolution', lambda: d.get_evolution()),
            ('get_evolution[12]', lambda: d.get_evolution(months=12)),
        ]

    # ------------------------------------------------------------------
    # Robustesse
    # ------------------------------------------------------------------

    def test_every_endpoint_answers_on_an_empty_period(self):
        far = fields.Date.to_string(self.today - timedelta(days=900))
        near = fields.Date.to_string(self.today - timedelta(days=895))
        for name, call in self._endpoints(far, near):
            with self.subTest(endpoint=name):
                self.assertIsNotNone(call(), "%s ne renvoie rien" % name)

    def test_every_endpoint_answers_with_activity(self):
        self._stay()
        d_from = fields.Date.to_string(self.today - timedelta(days=7))
        d_to = fields.Date.to_string(self.today)
        for name, call in self._endpoints(d_from, d_to):
            with self.subTest(endpoint=name):
                self.assertIsNotNone(call(), "%s ne renvoie rien" % name)

    def test_bad_dates_do_not_crash(self):
        for name, call in self._endpoints('pas-une-date', None):
            with self.subTest(endpoint=name):
                self.assertIsNotNone(call())

    # ------------------------------------------------------------------
    # Contenu
    # ------------------------------------------------------------------

    def test_meta_lists_the_business_poles(self):
        meta = self.dashboard.get_meta()
        self.assertIn('poles', meta)
        self.assertTrue(meta['poles'])
        self.assertTrue(all(
            {'key', 'label', 'color'} <= set(p) for p in meta['poles']))

    def test_meta_carries_the_company_identity(self):
        meta = self.dashboard.get_meta()
        self.assertEqual(meta['company_name'], self.company.name)
        self.assertTrue(meta['currency_symbol'])

    def test_kpis_expose_the_three_poles(self):
        kpis = self.dashboard.get_kpis(
            fields.Date.to_string(self.today - timedelta(days=7)),
            fields.Date.to_string(self.today))
        for key in ('total_ca', 'hotel_ca', 'pos_ca', 'slots_ca',
                    'occupancy', 'adr', 'tickets', 'basket', 'mix'):
            self.assertIn(key, kpis)

    def test_total_is_the_sum_of_the_poles(self):
        self._stay()
        kpis = self.dashboard.get_kpis(
            fields.Date.to_string(self.today - timedelta(days=7)),
            fields.Date.to_string(self.today))
        self.assertAlmostEqual(
            kpis['total_ca'],
            kpis['hotel_ca'] + kpis['pos_ca'] + kpis['slots_ca'],
            places=2)

    def test_hotel_revenue_reaches_the_consolidation(self):
        """Les deux nuits du séjour (2 × 80 000 HT) entrent dans la
        consolidation dès qu'elles tombent dans la période — sans
        attendre la facturation du folio au départ."""
        self._stay()
        kpis = self.dashboard.get_kpis(
            fields.Date.to_string(self.today - timedelta(days=7)),
            fields.Date.to_string(self.today + timedelta(days=7)))
        self.assertGreaterEqual(kpis['hotel_ca'], 160000.0)

    def test_hotel_revenue_is_the_one_of_the_pms(self):
        """Écart n° 25 / cas K04 : le CA hébergement est celui du PMS et
        du cockpit Direction — HT, nuit par nuit — pas le TTC des folios
        facturés au départ."""
        d_from = fields.Date.to_string(self.today - timedelta(days=7))
        d_to = fields.Date.to_string(self.today)
        # La base peut porter d'autres séjours (jeu de démonstration) : on
        # mesure l'apport du séjour de ce test.
        before = self.dashboard.get_kpis(d_from, d_to)['hotel_ca']
        self._stay()
        kpis = self.dashboard.get_kpis(d_from, d_to)
        pms = self.env['aite.hotel.dashboard'].get_kpis(d_from, d_to)
        self.assertEqual(kpis['hotel_ca'] - before, 80000.0,
                         "une seule nuit dans la période, HT")
        self.assertAlmostEqual(kpis['hotel_ca'],
                               pms['period']['room_revenue'], places=2)
        evo = self.dashboard.get_evolution(months=1)
        hotel = next(s for s in evo['series'] if s['key'] == 'hotel')
        month = self.dashboard._last_months(1, self.today)[0]
        pms_month = self.env['aite.hotel.dashboard'].get_kpis(
            fields.Date.to_string(month[1]),
            fields.Date.to_string(month[2] - timedelta(days=1)))
        self.assertAlmostEqual(hotel['data'][-1],
                               pms_month['period']['room_revenue'], places=2)

    def test_restaurant_revenue_is_excluding_tax(self):
        """Écart n° 25 / cas K04 : restauration HT, comme le cockpit
        Direction et l'analyse des ventes."""
        journal = self.env['account.journal'].create({
            'name': "Caisse Exec (test)", 'type': 'cash', 'code': 'CEXT',
            'company_id': self.company.id,
        })
        method = self.env['pos.payment.method'].create({
            'name': "Espèces Exec", 'journal_id': journal.id,
            'company_id': self.company.id,
        })
        config = self.env['pos.config'].create({
            'name': "Bar Exec", 'payment_method_ids': [(6, 0, method.ids)],
        })
        config.open_ui()
        product = self.env['product.product'].create({
            'name': "Jus Exec", 'type': 'consu', 'available_in_pos': True,
            'list_price': 5000.0, 'taxes_id': [(5, 0, 0)],
        })
        order = self.env['pos.order'].create({
            'session_id': config.current_session_id.id,
            'company_id': self.company.id,
            'amount_tax': 1925.0, 'amount_total': 11925.0,
            'amount_paid': 11925.0, 'amount_return': 0.0,
            'lines': [(0, 0, {
                'product_id': product.id, 'qty': 2, 'price_unit': 5000.0,
                'price_subtotal': 10000.0, 'price_subtotal_incl': 11925.0,
            })],
        })
        order.write({'state': 'paid'})
        self.env.flush_all()
        kpis = self.dashboard.get_kpis(
            fields.Date.to_string(self.today),
            fields.Date.to_string(self.today))
        self.assertEqual(kpis['pos_ca'], 10000.0)
        self.assertEqual(kpis['basket'], 10000.0)

    def test_mix_percentages_stay_within_bounds(self):
        self._stay()
        kpis = self.dashboard.get_kpis(
            fields.Date.to_string(self.today - timedelta(days=7)),
            fields.Date.to_string(self.today))
        for row in kpis['mix']:
            self.assertGreaterEqual(row.get('pct', 0.0), 0.0)
            self.assertLessEqual(row.get('pct', 0.0), 100.0)

    def test_empty_period_returns_zeros(self):
        kpis = self.dashboard.get_kpis(
            fields.Date.to_string(self.today - timedelta(days=900)),
            fields.Date.to_string(self.today - timedelta(days=895)))
        self.assertEqual(kpis['total_ca'], 0.0)
        self.assertEqual(kpis['basket'], 0.0)
        self.assertEqual(kpis['adr'], 0.0)

    # ------------------------------------------------------------------
    # F06 — RevPAR, pickup, pace, N-1, phrases d'explication
    # ------------------------------------------------------------------

    def test_meta_explains_every_hotel_indicator(self):
        hints = self.dashboard.get_meta().get('hints') or {}
        for key in ('occupancy', 'adr', 'revpar', 'pickup', 'pace',
                    'last_year'):
            self.assertGreaterEqual(len(hints.get(key, "")), 40, key)

    def test_kpis_expose_the_performance_indicators(self):
        self._stay()
        kpis = self.dashboard.get_kpis(
            fields.Date.to_string(self.today - timedelta(days=7)),
            fields.Date.to_string(self.today))
        for key in ('revpar', 'nights_sold', 'deltas_ly', 'pickup', 'pace'):
            self.assertIn(key, kpis)
        self.assertEqual(kpis['pickup']['window_days'], 7)
        self.assertEqual(kpis['pickup']['horizon_days'], 30)
        self.assertEqual(kpis['pace']['month'], self.today.strftime('%Y-%m'))
        for key in ('occupancy', 'adr', 'revpar'):
            self.assertIn(key, kpis['deltas_ly'])

    def test_revpar_is_the_one_of_the_pms(self):
        """Un seul chiffre pour une seule chose : le RevPAR vient du PMS."""
        self._stay()
        d_from = fields.Date.to_string(self.today - timedelta(days=7))
        d_to = fields.Date.to_string(self.today)
        kpis = self.dashboard.get_kpis(d_from, d_to)
        pms = self.env['aite.hotel.dashboard'].get_kpis(d_from, d_to)
        self.assertAlmostEqual(kpis['revpar'], pms['period']['revpar'],
                               places=2)
        self.assertAlmostEqual(kpis['adr'] * kpis['occupancy'] / 100.0,
                               kpis['revpar'], delta=1.0)

    def test_pickup_counts_the_stay_taken_today(self):
        """Le séjour de ce test est pris aujourd'hui pour aujourd'hui :
        il entre dans le pickup 7 j → 30 j."""
        before = self.dashboard.get_kpis(
            fields.Date.to_string(self.today),
            fields.Date.to_string(self.today))['pickup']['nights']
        self._stay()
        after = self.dashboard.get_kpis(
            fields.Date.to_string(self.today),
            fields.Date.to_string(self.today))['pickup']['nights']
        self.assertEqual(after - before, 2)

    def test_empty_period_has_no_year_on_year_delta(self):
        kpis = self.dashboard.get_kpis(
            fields.Date.to_string(self.today - timedelta(days=900)),
            fields.Date.to_string(self.today - timedelta(days=895)))
        self.assertEqual(kpis['revpar'], 0.0)
        self.assertIsNone(kpis['deltas_ly']['revpar'])

    def test_evolution_returns_one_point_per_month(self):
        data = self.dashboard.get_evolution(months=6)
        labels = data['labels'] if isinstance(data, dict) else data
        self.assertEqual(len(labels), 6)
