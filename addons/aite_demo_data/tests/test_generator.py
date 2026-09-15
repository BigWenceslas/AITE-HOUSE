# -*- coding: utf-8 -*-
"""Le générateur de jeu d'essai : idempotence, cohérence, purge."""
from datetime import timedelta

from odoo import fields
from odoo.tools import float_is_zero
from odoo.tests import TransactionCase, tagged

from odoo.addons.aite_demo_data.models.demo_generator import SCALE


@tagged('post_install', '-at_install', 'aite_demo')
class TestDemoGenerator(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.generator = cls.env['aite.demo.generator']
        cls.today = fields.Date.context_today(cls.env.user)

    # ------------------------------------------------------------------
    # Génération
    # ------------------------------------------------------------------

    def test_generation_reports_what_it_created(self):
        created = self.generator.generate_all(scale='small')
        for key in ('users', 'hotel_services', 'credits', 'housekeeping',
                    'purchases', 'deposits', 'pos_orders'):
            self.assertIn(key, created)

    def test_generation_is_idempotent(self):
        """Relancer la génération ne duplique rien."""
        self.generator.generate_all(scale='small')
        counts_before = self._counts()
        self.generator.generate_all(scale='small')
        self.assertEqual(self._counts(), counts_before)

    def test_scales_are_ordered(self):
        """Les trois volumes vont bien du plus léger au plus étendu."""
        self.assertLess(SCALE['small']['credits'],
                        SCALE['normal']['credits'])
        self.assertLess(SCALE['normal']['credits'],
                        SCALE['large']['credits'])
        self.assertLess(SCALE['small']['pos_days'],
                        SCALE['large']['pos_days'])

    def test_unknown_scale_falls_back_to_normal(self):
        created = self.generator.generate_all(scale='inconnu')
        self.assertIn('credits', created)

    def _counts(self):
        return {
            model: self.env[model].search_count([])
            for model in ('aite.pos.credit', 'aite.hotel.housekeeping',
                          'aite.purchase.deposit', 'aite.hotel.service')
        }

    # ------------------------------------------------------------------
    # Devise
    # ------------------------------------------------------------------

    def test_currency_switches_on_an_untouched_company(self):
        """Société encore vierge : le jeu d'essai pose sa devise."""
        company = self.env['res.company'].create({
            'name': "Société vierge (test)",
            'currency_id': self.env.ref('base.USD').id,
        })
        self.env.user.write({'company_ids': [(4, company.id)]})
        generator = self.generator.with_company(company)
        self.assertEqual(generator._ensure_currency(), 'GNF')
        self.assertEqual(company.currency_id.name, 'GNF')

    def test_currency_is_left_alone_once_entries_exist(self):
        """Une écriture comptable fige la devise : on n'y touche plus."""
        company = self.env.company
        before = company.currency_id.name
        has_entries = self.env['account.move.line'].search_count(
            [('company_id', '=', company.id)])
        if not has_entries:
            self.skipTest("aucune écriture sur la société courante")
        self.generator._ensure_currency()
        self.assertEqual(company.currency_id.name, before)

    def test_currency_is_left_alone_when_deliberately_chosen(self):
        """Une devise déjà choisie (ni USD ni EUR) n'est pas écrasée."""
        xof = self.env['res.currency'].with_context(
            active_test=False).search([('name', '=', 'XOF')], limit=1)
        if not xof:
            self.skipTest("devise XOF absente de la base")
        xof.write({'active': True})
        company = self.env['res.company'].create({
            'name': "Société XOF (test)",
            'currency_id': xof.id,
        })
        self.env.user.write({'company_ids': [(4, company.id)]})
        generator = self.generator.with_company(company)
        self.assertEqual(generator._ensure_currency(), 'XOF')
        self.assertEqual(company.currency_id.name, 'XOF')

    def test_currency_is_idempotent(self):
        company = self.env['res.company'].create({
            'name': "Société idempotente (test)",
            'currency_id': self.env.ref('base.USD').id,
        })
        self.env.user.write({'company_ids': [(4, company.id)]})
        generator = self.generator.with_company(company)
        generator._ensure_currency()
        self.assertEqual(generator._ensure_currency(), 'GNF')

    def test_generation_reports_the_currency(self):
        created = self.generator.generate_all(scale='small')
        self.assertIn('currency', created)

    # ------------------------------------------------------------------
    # Profils métier
    # ------------------------------------------------------------------

    def test_business_profiles_exist_and_are_scoped(self):
        self.generator.generate_all(scale='small')
        Users = self.env['res.users']
        reception = Users.search([('login', '=', 'demo.reception')], limit=1)
        self.assertTrue(reception, "le profil Réception doit exister")
        self.assertTrue(reception.has_group(
            'aite_hotel_management.group_hotel_user'))
        self.assertFalse(reception.has_group(
            'aite_hotel_management.group_hotel_manager'),
            "la réception ne doit pas avoir les droits Responsable")

    def test_housekeeper_profile_is_limited(self):
        self.generator.generate_all(scale='small')
        housekeeper = self.env['res.users'].search(
            [('login', '=', 'demo.gouvernante')], limit=1)
        self.assertTrue(housekeeper)
        self.assertTrue(housekeeper.has_group(
            'aite_hotel_management.group_hotel_housekeeping'))
        self.assertFalse(housekeeper.has_group(
            'aite_hotel_management.group_hotel_user'))

    def test_manager_profile_sees_the_dashboards(self):
        self.generator.generate_all(scale='small')
        manager = self.env['res.users'].search(
            [('login', '=', 'demo.direction')], limit=1)
        self.assertTrue(manager)
        self.assertTrue(manager.has_group(
            'aite_pos_analytics.group_aite_pos_analytics_manager'))
        self.assertTrue(manager.has_group(
            'aite_pos_credit.group_pos_credit_manager'))

    # ------------------------------------------------------------------
    # Cohérence du jeu produit
    # ------------------------------------------------------------------

    def test_credits_span_every_aging_bucket(self):
        """La balance âgée doit être peuplée sur ses quatre tranches."""
        self.generator.generate_all(scale='normal')
        self.env.flush_all()
        buckets = self.env['aite.pos.credit.dashboard'].get_aging()
        populated = [b for b in buckets if b['count'] > 0]
        self.assertGreaterEqual(
            len(populated), 3,
            "au moins trois tranches d'ancienneté doivent être servies")

    def test_credits_include_partial_repayments(self):
        self.generator.generate_all(scale='normal')
        partial = self.env['aite.pos.credit'].search([
            ('amount_paid', '>', 0), ('state', '=', 'open'),
        ])
        self.assertTrue(
            partial, "des ardoises partiellement remboursées sont attendues")

    def test_housekeeping_covers_several_task_types(self):
        self.generator.generate_all(scale='normal')
        types = set(self.env['aite.hotel.housekeeping'].search(
            [('date', '=', self.today)]).mapped('task_type'))
        self.assertGreaterEqual(len(types), 2)

    def test_hotel_services_carry_a_product(self):
        self.generator.generate_all(scale='small')
        services = self.env['aite.hotel.service'].search([])
        self.assertTrue(services)
        self.assertTrue(all(s.product_id for s in services),
                        "chaque service doit porter son article de folio")

    def test_season_prices_are_in_the_future(self):
        self.generator.generate_all(scale='small')
        seasons = self.env['aite.hotel.season.price'].search(
            [('name', 'like', 'saison')])
        self.assertTrue(seasons)
        self.assertTrue(all(s.date_to >= self.today for s in seasons))

    def test_purchase_orders_mix_confirmed_and_draft(self):
        self.generator.generate_all(scale='normal')
        orders = self.env['purchase.order'].search(
            [('origin', 'like', '%démo%')])
        states = set(orders.mapped('state'))
        self.assertTrue(orders)
        self.assertIn('purchase', states)

    def test_deposits_have_a_value(self):
        self.generator.generate_all(scale='small')
        deposits = self.env['aite.purchase.deposit'].search([])
        self.assertTrue(deposits)
        self.assertTrue(all(d.value >= 0 for d in deposits))

    # ------------------------------------------------------------------
    # Ventes en caisse
    # ------------------------------------------------------------------

    def test_pos_history_feeds_the_sales_dashboard(self):
        self.generator.generate_all(scale='small')
        self.env.flush_all()
        dashboard = self.env['aite.pos.dashboard']
        kpis = dashboard.get_kpis(
            fields.Date.to_string(self.today - timedelta(days=30)),
            fields.Date.to_string(self.today))
        self.assertGreater(kpis['ca'], 0.0,
                           "le tableau de bord Ventes doit être alimenté")
        self.assertGreater(kpis['order_count'], 0)

    def test_pos_sales_spread_over_business_hours(self):
        """Les ventes doivent couvrir midi ET le soir (heatmap)."""
        self.generator.generate_all(scale='small')
        hours = {
            fields.Datetime.context_timestamp(
                self.env.user, o.date_order).hour
            for o in self.env['pos.order'].search([], limit=200)
            if o.date_order
        }
        self.assertTrue(any(11 <= h <= 15 for h in hours))
        self.assertTrue(any(18 <= h <= 23 for h in hours))

    def test_some_sessions_show_a_cash_gap(self):
        """Des clôtures doivent présenter un écart réel à traiter.

        ``cash_register_difference`` est calculé et non stocké : le
        filtrer côté SQL ne filtre rien — Odoo journalise « Non-stored
        field … cannot be searched » et laisse passer **toutes** les
        sessions, ce qui rendait cette vérification toujours vraie. Le
        tri se fait donc en Python, sur la valeur réellement calculée.
        """
        gaps = self._generated_sessions_with_a_gap()
        self.assertTrue(
            gaps, "des écarts de caisse sont attendus pour la démonstration")
        self.assertTrue(
            any(s.cash_register_difference > 0 for s in gaps)
            and any(s.cash_register_difference < 0 for s in gaps),
            "les deux sens d'écart — excédent et manquant — sont attendus")

    def test_cash_gaps_do_not_touch_every_session(self):
        """Un écart partout ne ressemblerait pas à une caisse réelle."""
        sessions = self._generated_sessions()
        gaps = self._generated_sessions_with_a_gap()
        clean = sessions - gaps
        self.assertTrue(clean, "la plupart des clôtures doivent tomber juste")
        self.assertGreater(len(clean), len(gaps))

    def test_a_cash_gap_reaches_the_critical_grade(self):
        """Le barème de sévérité doit être servi jusqu'en haut.

        Sans manquant au-delà du seuil « critique », l'écran des écarts
        de caisse n'a rien à montrer de son alerte la plus forte.
        """
        self._generated_sessions_with_a_gap()
        graded = self._generated_sessions().mapped(
            'cash_discrepancy_severity')
        self.assertIn('high', graded)
        self.assertIn('over', graded)

    def _generated_sessions(self):
        """Les sessions du jeu d'essai, et elles seules.

        Une recherche globale ramènerait aussi les sessions d'une base
        déjà vécue — le constat porterait alors sur des données qui ne
        sont pas celles du générateur.
        """
        self.generator.generate_all(scale='large')
        self.env.flush_all()
        sessions = self.generator._tagged_all('pos.session')
        self.assertTrue(sessions, "le jeu d'essai doit poser des sessions")
        return sessions

    def _generated_sessions_with_a_gap(self):
        return self._generated_sessions().filtered(
            lambda s: not float_is_zero(
                s.cash_register_difference,
                precision_rounding=s.currency_id.rounding))

    # ------------------------------------------------------------------
    # Purge
    # ------------------------------------------------------------------

    def test_purge_keeps_the_cash_history(self):
        """Une vente encaissée n'est jamais détruite par la purge."""
        self.generator.generate_all(scale='small')
        sold_before = self.env['pos.order'].search_count(
            [('state', 'in', ('paid', 'done', 'invoiced'))])
        report = self.generator.purge_generated()
        self.assertIn('pos.order (conservées)', report)
        self.assertEqual(
            self.env['pos.order'].search_count(
                [('state', 'in', ('paid', 'done', 'invoiced'))]),
            sold_before)

    def test_purge_removes_what_was_generated(self):
        self.generator.generate_all(scale='small')
        self.assertTrue(self.env['aite.pos.credit'].search_count(
            [('note', 'like', '%démo%')]))
        self.generator.purge_generated()
        self.assertFalse(self.env['aite.pos.credit'].search_count(
            [('note', 'like', '%démo%')]))

    def test_purge_keeps_the_xml_reference_data(self):
        """Le référentiel posé à l'installation survit à la purge."""
        hotel = self.env.ref('aite_demo_data.hotel_main',
                             raise_if_not_found=False)
        rooms_before = self.env['aite.hotel.room'].search_count([])
        self.generator.generate_all(scale='small')
        self.generator.purge_generated()
        self.assertTrue(hotel.exists())
        self.assertEqual(
            self.env['aite.hotel.room'].search_count([]), rooms_before)

    def test_generation_after_purge_restores_the_set(self):
        self.generator.generate_all(scale='small')
        self.generator.purge_generated()
        created = self.generator.generate_all(scale='small')
        self.assertGreater(created['credits'], 0)

    # ------------------------------------------------------------------
    # Assistant
    # ------------------------------------------------------------------

    def test_wizard_generates_and_reports(self):
        wizard = self.env['aite.demo.generate.wizard'].create({
            'scale': 'small',
        })
        wizard.action_generate()
        self.assertIn("Créé", wizard.result)

    def test_wizard_can_purge_first(self):
        self.generator.generate_all(scale='small')
        wizard = self.env['aite.demo.generate.wizard'].create({
            'scale': 'small', 'purge_first': True,
        })
        wizard.action_generate()
        self.assertIn("Purgé", wizard.result)
        self.assertIn("Créé", wizard.result)
