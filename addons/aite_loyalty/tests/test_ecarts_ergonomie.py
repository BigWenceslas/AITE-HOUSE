# -*- coding: utf-8 -*-
"""Écarts non bloquants relevés en tournant les vidéos (ECARTS.md).

n° 44 (titre « Points — client »), n° 48 (Clients VIP : statut et points
visibles), n° 53 (« Ajuster des points » recharge l'écran), n° 63 (facette
« Clients » retirée, libellés d'origine, barème accessible au Responsable).
"""
from odoo.exceptions import AccessError
from odoo.tests import TransactionCase, tagged
from odoo.tools.misc import formatLang

from ..models.loyalty_move import ORIGINS


@tagged('post_install', '-at_install', 'aite_loyalty')
class TestLoyaltyEcartsErgonomie(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        base = cls.env.ref('base.group_user')
        cls.manager = cls.env['res.users'].create({
            'name': "Directrice fidélité",
            'login': 'directrice.fidelite.test',
            'groups_id': [(6, 0, [
                base.id,
                cls.env.ref('aite_hotel_management.group_hotel_manager').id,
            ])],
        })
        cls.reception = cls.env['res.users'].create({
            'name': "Réception fidélité",
            'login': 'reception.fidelite.test',
            'groups_id': [(6, 0, [
                base.id,
                cls.env.ref('aite_hotel_management.group_hotel_user').id,
            ])],
        })
        cls.client = cls.env['res.partner'].create({'name': "Estelle Ngono"})

    # ------------------------------------------------------------------
    # N° 44 — « Points de Estelle Ngono » (pas d'élision)
    # ------------------------------------------------------------------

    def test_titre_des_mouvements_du_client(self):
        action = self.client.action_view_loyalty_moves()
        self.assertEqual(action['name'], "Points — Estelle Ngono")

    # ------------------------------------------------------------------
    # N° 53 — l'ajustement recharge l'écran du dessous
    # ------------------------------------------------------------------

    def test_ajustement_recharge_l_ecran(self):
        wizard = self.env['aite.loyalty.adjust.wizard'].with_user(
            self.manager).create({
                'partner_id': self.client.id,
                'points': 50,
                'note': "Geste commercial",
            })
        action = wizard.action_apply()
        self.assertEqual(self.client.loyalty_points, 50)
        # Notification, puis rechargement du contrôleur courant (le solde
        # affiché n'est plus périmé).
        self.assertEqual(action['type'], 'ir.actions.client')
        self.assertEqual(action['tag'], 'display_notification')
        self.assertIn("Estelle Ngono", action['params']['message'])
        self.assertEqual(action['params']['next'],
                         {'type': 'ir.actions.client', 'tag': 'soft_reload'})

    def test_ajustement_solde_avec_separateur_de_milliers(self):
        """La notification écrit « 12 500 » comme la carte, la liste et le
        bouton de la fiche (règle 6), pas « 12500 »."""
        self.env['res.lang']._activate_lang('fr_FR')
        Wizard = self.env['aite.loyalty.adjust.wizard'].with_user(
            self.manager).with_context(lang='fr_FR')
        first = Wizard.create({
            'partner_id': self.client.id,
            'points': 12450,
            'note': "Reprise de l'ancien programme",
        }).action_apply()
        action = Wizard.create({
            'partner_id': self.client.id,
            'points': 50,
            'note': "Geste commercial",
        }).action_apply()
        fr = self.env(context=dict(self.env.context, lang='fr_FR'))
        message = action['params']['message']
        self.assertNotIn("12500", message)
        self.assertIn(formatLang(fr, 12500, digits=0), message)
        self.assertIn("+" + formatLang(fr, 12450, digits=0),
                      first['params']['message'])

    # ------------------------------------------------------------------
    # N° 63 — Clients VIP / VVIP : pas de facette « Clients »
    # ------------------------------------------------------------------

    def test_vip_sans_facette_clients(self):
        action = self.env.ref('aite_loyalty.action_loyalty_vip_partners')
        self.assertNotIn('search_default_customer', action.context or '')

    def test_libelles_d_origine(self):
        labels = dict(ORIGINS)
        self.assertEqual(labels['pos'], "Bar & restaurant")
        self.assertEqual(labels['slot_space'], "Espaces réservés")

    # ------------------------------------------------------------------
    # N° 48 — la carte et la liste VIP montrent statut et points
    # ------------------------------------------------------------------

    def test_vip_carte_et_liste_avec_statut_et_points(self):
        action = self.env.ref('aite_loyalty.action_loyalty_vip_partners')
        views = {v.view_mode: v.view_id for v in action.view_ids}
        for mode in ('kanban', 'list'):
            self.assertIn(mode, views, "Vue %s dédiée attendue." % mode)
            arch = self.env['res.partner'].get_views(
                [(views[mode].id, mode)])['views'][mode]['arch']
            self.assertIn('loyalty_tier', arch)
            self.assertIn('loyalty_points', arch)

    # ------------------------------------------------------------------
    # N° 63 — barème accessible au Responsable (sans l'administration)
    # ------------------------------------------------------------------

    def test_bareme_ouvert_au_responsable(self):
        self.company.aite_loyalty_rate_per_1000 = 1.0
        self.assertFalse(self.manager.has_group('base.group_system'))
        Wizard = self.env['aite.loyalty.bareme.wizard'].with_user(
            self.manager)
        wizard = Wizard.create({})
        # Le barème en vigueur est pré-rempli.
        self.assertEqual(wizard.rate_per_1000, 1.0)
        self.assertEqual(wizard.vip_min_visits,
                         self.company.aite_loyalty_vip_min_visits)
        # Règle 1 : la phrase « ce qui va se passer » suit le barème saisi.
        self.assertIn("rapporte 25 point", wizard.summary)
        wizard.write({'rate_per_1000': 2.0, 'vip_min_visits': 8})
        self.env.invalidate_all()
        wizard.action_save()
        self.env.invalidate_all()
        self.assertEqual(self.company.aite_loyalty_rate_per_1000, 2.0)
        self.assertEqual(self.company.aite_loyalty_vip_min_visits, 8)

    def test_bareme_ferme_a_la_reception(self):
        with self.assertRaises(AccessError):
            self.env['aite.loyalty.bareme.wizard'].with_user(
                self.reception).create({})

    def test_bareme_dans_le_menu_fidelite(self):
        menu = self.env.ref('aite_loyalty.menu_loyalty_bareme')
        self.assertEqual(
            menu.action, self.env.ref('aite_loyalty.action_loyalty_bareme'))
        visible = self.env['ir.ui.menu'].with_user(
            self.manager)._visible_menu_ids()
        self.assertIn(menu.id, visible)
        hidden = self.env['ir.ui.menu'].with_user(
            self.reception)._visible_menu_ids()
        self.assertNotIn(menu.id, hidden)
