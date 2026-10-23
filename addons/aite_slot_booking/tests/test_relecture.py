# -*- coding: utf-8 -*-
"""Relecture croisée de l'intégration (cohérence entre écrans).

* Le refus d'un créneau hors horaires annonçait « (8.00 – 22.50) » pour
  une ressource ouverte de 08:00 à 22:30 : point décimal (règle 6) et
  heure fausse (22.50 se lit 22 h 50). La fiche, le site et le tableau de
  bord écrivent « 08:00 – 22:30 ».
* Le tableau de bord bornait ses périodes en jours UTC : à Douala
  (UTC+1), une prestation de 0 h 30 le 1er du mois tombait dans le mois
  précédent, et l'activité par pôle de la Direction (qui doit donner le
  même chiffre, cas K04) reprenait la même erreur.
"""
from datetime import timedelta

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import tagged

from .common import SlotCommon


@tagged('post_install', '-at_install', 'aite_slot')
class TestSlotRelecture(SlotCommon):

    def test_opening_hours_are_written_hh_mm_in_the_refusal(self):
        self.company.partner_id.tz = 'UTC'
        self.salon.write({'open_hour': 8.0, 'close_hour': 22.5,
                          'slot_minutes': '30'})
        with self.assertRaises(ValidationError) as err:
            self._booking(start_h=6.0, stop_h=7.0)
        message = str(err.exception)
        self.assertIn("08:00 – 22:30", message)
        self.assertNotIn("22.50", message)

    def test_dashboard_periods_are_local_days(self):
        """Prestation de 0 h 00 à 1 h 00, heure de Douala, le 1er du mois
        (23 h 00 UTC la veille) : comptée le 1er, pas la veille."""
        self.company.partner_id.tz = 'Africa/Douala'
        night = self.env['aite.booking.resource'].create({
            'name': "Salle de nuit",
            'kind': 'space',
            'company_id': self.company.id,
            'capacity': 1,
            'open_hour': 0.0,
            'close_hour': 23.0,
            'slot_minutes': '60',
            'price_hour': 10000.0,
        })
        today = fields.Date.context_today(self.env.user)
        first = today.replace(day=1)
        eve = first - timedelta(days=1)
        start = fields.Datetime.to_datetime('%s 23:00:00' % eve)
        booking = self.env['aite.slot.booking'].create({
            'resource_id': night.id,
            'partner_id': self.client.id,
            'company_id': self.company.id,
            'start': start,
            'stop': start + timedelta(hours=1),
        })
        booking.action_confirm()
        board = self.env['aite.slot.dashboard'].with_context(
            tz='Africa/Douala')
        day_first = board.get_kpis(str(first), str(first),
                                   resource_id=night.id)
        day_eve = board.get_kpis(str(eve), str(eve), resource_id=night.id)
        self.assertEqual(day_first['total_count'], 1, "compté le 1er")
        self.assertEqual(day_eve['total_count'], 0, "pas la veille")
        rows = board.get_bookings(str(first), str(first),
                                  resource_id=night.id)
        self.assertEqual([r['id'] for r in rows], [booking.id])
