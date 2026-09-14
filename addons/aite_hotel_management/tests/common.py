# -*- coding: utf-8 -*-
"""Socle commun des tests du PMS AITE.

Monte un établissement minimal mais complet — hôtel, étage, types de
chambre, chambres, services, client — sur lequel s'appuient tous les cas
de test du module. Les montants sont exprimés dans la devise de la
société de test.
"""
from datetime import timedelta

from odoo import fields
from odoo.tests import common


class HotelCommon(common.TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.company = cls.env.company
        # Fuseau déterministe : les heures d'arrivée / départ sont
        # composées en heure locale puis converties en UTC.
        cls.env.user.tz = 'UTC'

        cls.hotel = cls.env['aite.hotel.hotel'].create({
            'name': "Hôtel de test",
            'code': 'TST',
            'company_id': cls.company.id,
            'checkin_hour': 14.0,
            'checkout_hour': 12.0,
        })
        cls.floor = cls.env['aite.hotel.floor'].create({
            'name': "Rez-de-chaussée",
            'hotel_id': cls.hotel.id,
        })

        cls.type_std = cls.env['aite.hotel.room.type'].create({
            'name': "Standard",
            'code': 'STD',
            'company_id': cls.company.id,
            'base_price': 50000.0,
            'extra_person_price': 10000.0,
            'capacity_adults': 2,
            'capacity_children': 1,
        })
        cls.type_suite = cls.env['aite.hotel.room.type'].create({
            'name': "Suite",
            'code': 'STE',
            'company_id': cls.company.id,
            'base_price': 120000.0,
            'capacity_adults': 3,
            'capacity_children': 2,
        })

        cls.room_101 = cls.env['aite.hotel.room'].create({
            'name': '101',
            'hotel_id': cls.hotel.id,
            'floor_id': cls.floor.id,
            'room_type_id': cls.type_std.id,
        })
        cls.room_102 = cls.env['aite.hotel.room'].create({
            'name': '102',
            'hotel_id': cls.hotel.id,
            'floor_id': cls.floor.id,
            'room_type_id': cls.type_std.id,
        })
        cls.room_201 = cls.env['aite.hotel.room'].create({
            'name': '201',
            'hotel_id': cls.hotel.id,
            'room_type_id': cls.type_suite.id,
        })

        cls.service_resto = cls.env['aite.hotel.service'].create({
            'name': "Petit-déjeuner",
            'category': 'restaurant',
            'company_id': cls.company.id,
            'price': 7500.0,
        })
        cls.service_laundry = cls.env['aite.hotel.service'].create({
            'name': "Blanchisserie",
            'category': 'laundry',
            'company_id': cls.company.id,
            'price': 5000.0,
        })

        # Les articles support héritent de la taxe de vente par défaut de
        # la société. On la retire du jeu d'essai pour que les montants
        # attendus soient lisibles ; la mécanique de taxe est vérifiée
        # explicitement par ``test_taxes_are_computed_like_the_invoice``.
        (cls.type_std | cls.type_suite).mapped('product_id').write(
            {'taxes_id': [(5, 0, 0)]})
        (cls.service_resto | cls.service_laundry).mapped('product_id').write(
            {'taxes_id': [(5, 0, 0)]})

        cls.guest = cls.env['res.partner'].create({
            'name': "Client Test",
            'is_company': False,
            'email': 'client.test@example.com',
            'phone': '+224 600 00 00 00',
        })
        cls.guest_2 = cls.env['res.partner'].create({
            'name': "Second Client",
            'is_company': False,
            'email': 'client2.test@example.com',
        })
        cls.agent = cls.env['res.partner'].create({
            'name': "Agence Voyages Test",
            'is_company': True,
            'is_booking_agent': True,
        })

    # ------------------------------------------------------------------
    # Fabriques
    # ------------------------------------------------------------------

    @classmethod
    def _dt(cls, days_from_today, hour):
        """Datetime UTC à J+``days``, à l'heure locale ``hour``."""
        day = fields.Date.context_today(cls.env.user) + timedelta(
            days=days_from_today)
        return cls.env['aite.hotel.reservation']._compose_datetime(day, hour)

    def _make_reservation(self, rooms=None, checkin_offset=0,
                          checkout_offset=1, partner=None, **kwargs):
        """Réservation brouillon d'une ou plusieurs chambres."""
        rooms = rooms or self.room_101
        vals = {
            'hotel_id': self.hotel.id,
            'partner_id': (partner or self.guest).id,
            'checkin_date': self._dt(checkin_offset, 14.0),
            'checkout_date': self._dt(checkout_offset, 12.0),
            'line_ids': [
                (0, 0, {
                    'room_type_id': room.room_type_id.id,
                    'room_id': room.id,
                    'adults': 1,
                }) for room in rooms
            ],
        }
        vals.update(kwargs)
        return self.env['aite.hotel.reservation'].create(vals)
