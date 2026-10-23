# -*- coding: utf-8 -*-
"""Mise à niveau d'une base livrée (LAVERANDAH, livraison 2).

ECARTS n° 73 : un hôtel créé AVANT l'installation du module garde
« Barème appliqué » vide (le champ stocké est calculé avant le chargement
des barèmes). Le correctif du code couvre l'installation (création d'un
barème → recalcul des hôtels) mais pas une base déjà installée : les
barèmes livrés sont ``noupdate``, la mise à niveau ne les recrée pas et
l'hôtel restait sans taxe. Le script de migration 18.0.1.0.2 recalcule le
barème de tous les hôtels et, comme un changement de catégorie, remet à
jour la taxe des folios encore ouverts.
"""
from odoo.tests import tagged

from odoo.addons.aite_hotel_management.tests.common import HotelCommon
from odoo.addons.aite_hotel_management.tests.test_migration import (
    load_migration,
)


@tagged('post_install', '-at_install', 'aite_city_tax')
class TestCityTaxMigration(HotelCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.migration = load_migration('aite_city_tax', '18.0.1.0.2')
        cls.rate_cm_3 = cls.env.ref('aite_city_tax.rate_cm_3')
        cls.hotel.write({'country_id': cls.env.ref('base.cm').id,
                         'stars': '3'})

    def _empty_rate_as_delivered(self):
        """État de la base livrée : barème resté vide en base."""
        self.env.flush_all()
        self.env.cr.execute(
            "UPDATE aite_hotel_hotel SET city_tax_rate_id = NULL "
            "WHERE id = %s", [self.hotel.id])
        self.hotel.invalidate_recordset(['city_tax_rate_id'])
        self.assertFalse(self.hotel.city_tax_rate_id)

    def test_bareme_applique_aux_hotels_existants(self):
        self._empty_rate_as_delivered()
        self.migration.migrate(self.env.cr, '18.0.1.0.0')
        self.hotel.invalidate_recordset(['city_tax_rate_id'])
        self.assertEqual(self.hotel.city_tax_rate_id, self.rate_cm_3)
        self.assertIn("3 000", self.hotel.city_tax_help)

    def test_folio_ouvert_recoit_sa_taxe(self):
        """Séjour en cours, non facturé : la ligne de taxe apparaît, comme
        après un changement de catégorie de l'hôtel."""
        reservation = self._make_reservation(checkout_offset=2)
        reservation.action_confirm()
        folio = reservation.folio_id
        tax = folio.line_ids.filtered(lambda l: l.line_type == 'city_tax')
        tax.with_context(aite_city_tax_sync=True).unlink()
        self._empty_rate_as_delivered()

        self.migration.migrate(self.env.cr, '18.0.1.0.0')

        folio.invalidate_recordset()
        tax = folio.line_ids.filtered(lambda l: l.line_type == 'city_tax')
        self.assertEqual(len(tax), 1)
        self.assertEqual(tax.price_unit, 3000)
        self.assertEqual(tax.quantity, 2)  # 2 nuits × 1 adulte

    def test_hotel_exonere_reste_sans_bareme(self):
        self.hotel.city_tax_enabled = False
        self.migration.migrate(self.env.cr, '18.0.1.0.0')
        self.hotel.invalidate_recordset(['city_tax_rate_id'])
        self.assertFalse(self.hotel.city_tax_rate_id)

    def test_installation_neuve_ignoree(self):
        self._empty_rate_as_delivered()
        self.migration.migrate(self.env.cr, None)
        self.hotel.invalidate_recordset(['city_tax_rate_id'])
        self.assertFalse(self.hotel.city_tax_rate_id)
