# -*- coding: utf-8 -*-
"""Taxe de séjour : la première confirmation marche sous chaque profil."""
from odoo.tests import tagged

from odoo.addons.aite_hotel_management.tests.common import HotelCommon


@tagged('post_install', '-at_install', 'aite_city_tax')
class TestCityTaxSecurity(HotelCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        base_user = cls.env.ref('base.group_user')

        def _user(login, group_xmlid):
            return cls.env['res.users'].create({
                'name': login,
                'login': login,
                'groups_id': [(6, 0, [
                    base_user.id, cls.env.ref(group_xmlid).id,
                ])],
            })

        cls.receptionist = _user(
            'reception.taxe.test', 'aite_hotel_management.group_hotel_user')
        cls.manager = _user(
            'responsable.taxe.test',
            'aite_hotel_management.group_hotel_manager')
        # Hôtel 3 étoiles au Cameroun : barème DGI de 3 000 F par nuitée.
        cls.hotel.write({
            'country_id': cls.env.ref('base.cm').id,
            'stars': '3',
        })

    def _first_confirmation_as(self, user):
        """Première confirmation : l'article de taxe n'existe pas encore."""
        self.assertFalse(self.hotel.city_tax_product_id)
        self.assertTrue(self.hotel.city_tax_rate_id)
        reservation = self._make_reservation()
        self.env.invalidate_all()
        reservation.with_user(user).action_confirm()
        self.env.invalidate_all()
        folio = reservation.folio_id
        self.assertTrue(folio)
        self.assertEqual(folio.amount_city_tax,
                         self.hotel.city_tax_rate_id.amount)
        product = self.hotel.city_tax_product_id
        self.assertTrue(product, "L'article doit être mémorisé sur l'hôtel.")
        self.assertFalse(product.taxes_id, "La taxe de séjour est hors TVA.")
        return folio

    def test_first_confirmation_by_reception(self):
        """ECARTS n° 11 : la réception ne peut ni créer d'article ni
        écrire sur l'hôtel — l'article est une écriture technique."""
        self._first_confirmation_as(self.receptionist)

    def test_first_confirmation_by_manager(self):
        """ECARTS n° 11 : le responsable n'a pas les droits produit."""
        self._first_confirmation_as(self.manager)

    def test_product_is_reused(self):
        """Un seul article par hôtel, réutilisé au séjour suivant."""
        self._first_confirmation_as(self.receptionist)
        product = self.hotel.city_tax_product_id
        res2 = self._make_reservation(rooms=self.room_102)
        res2.with_user(self.receptionist).action_confirm()
        line = res2.folio_id.line_ids.filtered(
            lambda l: l.line_type == 'city_tax')
        self.assertEqual(line.product_id, product)
