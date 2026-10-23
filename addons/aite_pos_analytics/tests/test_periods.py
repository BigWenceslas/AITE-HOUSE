# -*- coding: utf-8 -*-
"""Une période est faite de jours LOCAUX (relecture des écarts n° 37 / 38).

Les dates s'affichent dans le fuseau de l'utilisateur : l'onglet Sessions
montre « 01/10/2026 » pour une session ouverte le 30/09 à 23 h 30 UTC
(0 h 30 à Douala). Si les bornes de période restaient des jours UTC, cette
session — et ses ventes, ses paiements — tomberait en septembre alors que
l'écran la date d'octobre. Un bar qui travaille après minuit le verrait
chaque nuit.
"""
from datetime import datetime

from odoo.tests import tagged

from .common import PosAnalyticsCommon

# 30/09/2026 à 23 h 30 UTC = 01/10/2026 à 0 h 30 à Douala (UTC+1).
AFTER_MIDNIGHT = datetime(2026, 9, 30, 23, 30)


@tagged('post_install', '-at_install', 'aite_analytics')
class TestPosLocalPeriods(PosAnalyticsCommon):

    def setUp(self):
        super().setUp()
        self.dash = self.env['aite.pos.dashboard'].with_context(
            tz='Africa/Douala')
        self.session.start_at = AFTER_MIDNIGHT
        order = self._sale([(self.beer, 2, 5000.0)])
        order.date_order = AFTER_MIDNIGHT
        order.payment_ids.payment_date = AFTER_MIDNIGHT
        self.env.flush_all()

    def test_a_session_after_midnight_belongs_to_the_local_day(self):
        october = self.dash.get_sessions('2026-10-01', '2026-10-31')
        self.assertIn(self.session.id, [s['id'] for s in october])
        september = self.dash.get_sessions('2026-09-01', '2026-09-30')
        self.assertNotIn(self.session.id, [s['id'] for s in september])

    def test_sales_after_midnight_count_in_the_local_day(self):
        cfg = self.pos_config.id
        self.assertEqual(
            self.dash.get_kpis('2026-10-01', '2026-10-01', cfg)['ca'],
            10000.0)
        self.assertEqual(
            self.dash.get_kpis('2026-09-30', '2026-09-30', cfg)['ca'], 0.0)
        # Même règle pour la répartition par caisse et les paiements.
        caisses = self.dash.get_caisse_breakdown(
            '2026-10-01', '2026-10-01', cfg)['caisses']
        self.assertEqual(sum(c['ca'] for c in caisses), 10000.0)
        paid = self.dash.get_payment_breakdown('2026-10-01', '2026-10-01',
                                               cfg)
        self.assertEqual(sum(p['amount'] for p in paid), 10000.0)
        self.assertFalse(self.dash.get_payment_breakdown(
            '2026-09-30', '2026-09-30', cfg))

    def test_the_day_count_is_unchanged(self):
        """Le nombre de jours de la période (CA / jour) reste celui du
        calendrier : un mois de 31 jours vaut 31 jours."""
        kpis = self.dash.get_kpis('2026-10-01', '2026-10-31',
                                  self.pos_config.id)
        self.assertEqual(kpis['days'], 31)
        self.assertEqual(kpis['prev_from'], '2026-08-31')
        self.assertEqual(kpis['prev_to'], '2026-09-30')
