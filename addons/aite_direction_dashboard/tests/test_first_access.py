# -*- coding: utf-8 -*-
"""Premier clic : l'administrateur ouvre le cockpit sans réglage de droits.

Sur une base neuve, personne n'a encore coché les profils « Analyses POS »
ou « Crédit clients ». L'administrateur système doit pourtant pouvoir
ouvrir la vue consolidée — c'est le premier écran qu'il essaie.
"""
from datetime import timedelta

from odoo import fields
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install', 'aite_direction')
class TestFirstAccess(TransactionCase):

    def test_admin_opens_every_tab_without_access_error(self):
        admin = self.env.ref('base.user_admin')
        cockpit = self.env['aite.direction.dashboard'].with_user(admin)
        today = fields.Date.context_today(cockpit)
        d_from = fields.Date.to_string(today - timedelta(days=30))
        d_to = fields.Date.to_string(today)
        cockpit.get_meta()
        cockpit.get_overview(d_from, d_to)
        cockpit.get_pos_tab(d_from, d_to)
        cockpit.get_credit_tab(d_from, d_to)
        cockpit.get_stock_tab(d_from, d_to)
        cockpit.get_purchase_tab(d_from, d_to)
        cockpit.get_actions(d_from, d_to)

    def test_admin_holds_the_manager_profiles(self):
        admin = self.env.ref('base.user_admin')
        self.assertTrue(admin.has_group(
            'aite_pos_analytics.group_aite_pos_analytics_manager'))
        self.assertTrue(admin.has_group(
            'aite_pos_credit.group_pos_credit_manager'))
