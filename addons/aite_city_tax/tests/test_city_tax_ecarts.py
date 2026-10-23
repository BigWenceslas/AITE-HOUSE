# -*- coding: utf-8 -*-
"""Taxe de séjour : écarts non bloquants relevés par les tutoriels vidéo.

Libellés lisibles (langue de l'utilisateur, symbole de la devise), chemins
de menu exacts, barème appliqué même quand il arrive après l'hôtel, ligne de
taxe protégée, montants FCFA sans centimes.
"""
from odoo.exceptions import UserError
from odoo.tests import tagged

from odoo.addons.aite_hotel_management.tests.common import HotelCommon


@tagged('post_install', '-at_install', 'aite_city_tax')
class TestCityTaxEcarts(HotelCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Rate = cls.env['aite.city.tax.rate']
        cls.cameroon = cls.env.ref('base.cm')
        cls.gabon = cls.env.ref('base.ga')
        cls.xaf = cls.env.ref('base.XAF')
        cls.rate_cm_3 = cls.env.ref('aite_city_tax.rate_cm_3')
        cls.receptionist = cls.env['res.users'].create({
            'name': "Réception taxe",
            'login': 'reception.taxe.ecarts',
            'groups_id': [(6, 0, [
                cls.env.ref('base.group_user').id,
                cls.env.ref('aite_hotel_management.group_hotel_user').id,
            ])],
        })
        # Hôtel 3 étoiles au Cameroun : barème DGI de 3 000 F par nuitée.
        cls.hotel.write({'country_id': cls.cameroon.id, 'stars': '3'})

    def _city_tax_line(self, folio):
        return folio.line_ids.filtered(lambda l: l.line_type == 'city_tax')

    # ------------------------------------------------------------------
    # ECARTS n° 39 et n° 7 : libellé du barème et phrase de l'hôtel
    # ------------------------------------------------------------------

    def test_rate_label_follows_language_and_currency_symbol(self):
        """Le libellé du barème n'est plus figé à l'installation : il suit
        la langue de l'utilisateur (pays traduit) et affiche le symbole de
        la devise (« FCFA »), pas son code ISO (« XAF »)."""
        self.env['res.lang']._activate_lang('fr_FR')
        self.cameroon.update_field_translations(
            'name', {'fr_FR': "Cameroun"})
        label_fr = self.rate_cm_3.with_context(lang='fr_FR').display_name
        self.assertIn("Cameroun", label_fr)
        self.assertIn("3 000 FCFA", label_fr)
        self.assertNotIn("XAF", label_fr)
        label_en = self.rate_cm_3.with_context(lang='en_US').display_name
        self.assertIn("Cameroon", label_en)

    def test_hotel_help_uses_currency_symbol(self):
        """« 3 000 FCFA par personne et par nuit », pas « 3 000 XAF »."""
        help_text = self.hotel.city_tax_help
        self.assertIn("3 000 FCFA", help_text)
        self.assertNotIn("XAF", help_text)

    # ------------------------------------------------------------------
    # ECARTS n° 46 : la phrase d'aide cite le vrai chemin du menu
    # ------------------------------------------------------------------

    def test_help_names_the_real_menu(self):
        """« Aucun barème connu pour … » renvoie au menu réel :
        Hôtel → Configuration → Barèmes de taxe de séjour."""
        self.hotel.write({'country_id': self.gabon.id})
        self.assertFalse(self.hotel.city_tax_rate_id)
        menu = self.env.ref('aite_city_tax.menu_city_tax_rates')
        path = " → ".join(menu.complete_name.split('/'))
        self.assertIn(path, self.hotel.city_tax_help)
        # Même chemin dans le texte fixe de l'onglet « Taxe de séjour ».
        arch = self.env.ref(
            'aite_city_tax.view_hotel_hotel_form_city_tax').arch
        self.assertIn(path, " ".join(arch.split()))

    # ------------------------------------------------------------------
    # ECARTS n° 73 : un barème arrivé après l'hôtel s'applique
    # ------------------------------------------------------------------

    def test_rate_created_after_the_hotel_is_applied(self):
        """C'est le cas d'une installation sur une base où l'hôtel existe
        déjà : le barème est chargé après le calcul du champ. Créer (ou
        réactiver) un barème met à jour les hôtels concernés ; l'archiver
        les libère."""
        self.hotel.write({'country_id': self.gabon.id})
        self.assertFalse(self.hotel.city_tax_rate_id)
        rate = self.Rate.create({
            'country_id': self.gabon.id,
            'stars': '3',
            'amount': 1500,
            'currency_id': self.xaf.id,
        })
        self.assertEqual(self.hotel.city_tax_rate_id, rate)
        rate.active = False
        self.assertFalse(self.hotel.city_tax_rate_id)
        rate.active = True
        self.assertEqual(self.hotel.city_tax_rate_id, rate)
        rate.stars = '4'
        self.assertFalse(self.hotel.city_tax_rate_id)

    # ------------------------------------------------------------------
    # ECARTS n° 57 : barèmes groupés et ligne de taxe protégée
    # ------------------------------------------------------------------

    def test_rate_amounts_are_not_summed_by_country(self):
        """Additionner des montants par nuitée (« Cameroun 14 000 ») n'a
        pas de sens : le montant n'a pas d'agrégat."""
        self.assertFalse(
            self.Rate.fields_get(['amount'])['amount'].get('aggregator'))
        groups = self.Rate.read_group([], ['amount'], ['country_id'])
        self.assertTrue(groups)
        for group in groups:
            self.assertFalse(group.get('amount'))

    def test_city_tax_line_cannot_be_deleted_by_hand(self):
        """La ligne « ne s'édite pas à la main » : la réception ne peut pas
        la supprimer ; la synchronisation, elle, la retire quand la taxe
        ne s'applique plus."""
        reservation = self._make_reservation()
        reservation.action_confirm()
        folio = reservation.folio_id
        line = self._city_tax_line(folio)
        self.assertTrue(line)
        self.env.invalidate_all()
        with self.assertRaisesRegex(UserError, "Taxe de séjour"):
            line.with_user(self.receptionist).unlink()
        self.assertTrue(line.exists())
        # Hôtel exonéré : la ligne disparaît d'elle-même.
        self.hotel.city_tax_enabled = False
        self.assertFalse(self._city_tax_line(folio))

    # ------------------------------------------------------------------
    # ECARTS n° 40 : l'état mensuel en FCFA, sans centimes
    # ------------------------------------------------------------------

    def test_monthly_report_amount_has_no_decimals(self):
        """Le tableau croisé formate la mesure avec la précision du champ :
        « 1 293 000 », pas « 1 293 000,00 »."""
        digits = self.env['aite.city.tax.report'].fields_get(
            ['amount'])['amount'].get('digits')
        self.assertEqual(tuple(digits or ()), (16, 0))
