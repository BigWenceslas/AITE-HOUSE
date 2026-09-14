# -*- coding: utf-8 -*-
"""Socle commun des tests Espaces & Prestations."""
from datetime import timedelta

from odoo import fields
from odoo.tests import common


class SlotCommon(common.TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.env.user.tz = 'UTC'

        cls.salon = cls.env['aite.booking.resource'].create({
            'name': "Salon VIP",
            'kind': 'space',
            'company_id': cls.company.id,
            'capacity': 1,
            'open_hour': 9.0,
            'close_hour': 22.0,
            'slot_minutes': '60',
            'price_hour': 25000.0,
        })
        cls.cabine = cls.env['aite.booking.resource'].create({
            'name': "Cabine SPA",
            'kind': 'spa',
            'company_id': cls.company.id,
            'capacity': 2,
            'open_hour': 10.0,
            'close_hour': 18.0,
            'slot_minutes': '30',
        })

        cls.product_spa = cls.env['product.product'].create({
            'name': "Soin SPA 60 min",
            'type': 'service',
            'list_price': 45000.0,
            'sale_ok': True,
            'taxes_id': [(5, 0, 0)],
        })
        cls.service_spa = cls.env['aite.booking.service'].create({
            'name': "Massage relaxant",
            'kind': 'spa',
            'company_id': cls.company.id,
            'duration_minutes': 60,
            'price': 45000.0,
            'product_id': cls.product_spa.id,
        })
        cls.product_pressing = cls.env['product.product'].create({
            'name': "Pressing chemise",
            'type': 'service',
            'list_price': 3000.0,
            'sale_ok': True,
            'taxes_id': [(5, 0, 0)],
        })
        cls.service_pressing = cls.env['aite.booking.service'].create({
            'name': "Chemise",
            'kind': 'pressing',
            'company_id': cls.company.id,
            'duration_minutes': 30,
            'price': 3000.0,
            'product_id': cls.product_pressing.id,
        })

        cls.client = cls.env['res.partner'].create({
            'name': "Client Créneau",
            'email': 'creneau@example.com',
        })
        cls.client_2 = cls.env['res.partner'].create({
            'name': "Second Créneau",
        })

    # ------------------------------------------------------------------
    # Fabriques
    # ------------------------------------------------------------------

    @classmethod
    def _at(cls, days, hour):
        """Datetime UTC à J+``days``, heure locale décimale ``hour``."""
        day = fields.Date.context_today(cls.env.user) + timedelta(days=days)
        base = fields.Datetime.to_datetime(str(day))
        return base + timedelta(hours=hour)

    def _booking(self, resource=None, start_h=10.0, stop_h=11.0, days=1,
                 partner=None, **kwargs):
        vals = {
            'resource_id': (resource or self.salon).id,
            'partner_id': (partner or self.client).id,
            'company_id': self.company.id,
            'start': self._at(days, start_h),
            'stop': self._at(days, stop_h),
        }
        vals.update(kwargs)
        return self.env['aite.slot.booking'].create(vals)
