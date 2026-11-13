# -*- coding: utf-8 -*-
"""Tours de la caisse (spécification, partie 6.3).

Incrément 1 : un tour de fumée seulement. La caisse s'ouvre avec le module
installé et ``PosStore.aiteActif`` suit la case « Service à table contrôlé ».
Il prouve aussi que les tours tournent sur ce poste (``websocket-client``
présent : sans lui, un tour est ignoré, pas en échec).
"""
from odoo.tests import tagged

from odoo.addons.pos_restaurant.tests.test_frontend import TestFrontendCommon


@tagged('post_install', '-at_install', 'aite_pos_restaurant')
class TestTours(TestFrontendCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Pas d'imprimante de préparation : un bon non imprimé ouvrirait la
        # fenêtre « Printing failed ».
        cls.pos_config.write({'printer_ids': [(5, 0, 0)], 'is_order_printer': False})
        # Compte de la caisse comme le pose AITE : courriel et Facturation.
        cls.pos_user.partner_id.email = 'pos_user@test.com'
        cls.pos_user.groups_id += cls.env.ref('account.group_account_invoice')
        for nom, code, niveau in (("Awa", '1111', 'serveur'),
                                  ("Carine", '3333', 'caissiere'),
                                  ("Paul", '4444', 'superviseur'),
                                  ("Fanta", '5555', 'manager')):
            cls.env['hr.employee'].create({
                'name': nom, 'pin': code, 'aite_niveau_caisse': niveau,
                'company_id': cls.env.company.id})

    def test_mode_actif(self):
        self.pos_config.write({'module_pos_hr': True, 'aite_mode_restaurant': True})
        self.pos_config.with_user(self.pos_user).open_ui()
        self.start_pos_tour('AiteModeActifTour', login='pos_user')

    def test_mode_inactif(self):
        """Une caisse de restaurant dont la case est décochée (T16)."""
        self.assertFalse(self.pos_config.aite_mode_restaurant)
        self.pos_config.with_user(self.pos_user).open_ui()
        self.start_pos_tour('AiteModeInactifTour', login='pos_user')
