# -*- coding: utf-8 -*-
"""
Parcours métier bout-en-bout — la suite prise comme un tout.

Chaque test rejoue un scénario complet d'exploitation, en traversant
plusieurs modules, et vérifie que l'argent et les statuts arrivent au
bon endroit : c'est là que se logent les régressions d'intégration que
les tests unitaires de chaque module ne voient pas.
"""
from datetime import timedelta

from odoo import fields
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install', 'aite_journey')
class TestBusinessJourneys(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.env.user.tz = 'UTC'
        cls.today = fields.Date.context_today(cls.env.user)

        # --- Établissement -------------------------------------------------
        cls.hotel = cls.env['aite.hotel.hotel'].create({
            'name': "Hôtel Parcours",
            'code': 'PRC',
            'company_id': cls.company.id,
        })
        cls.rtype = cls.env['aite.hotel.room.type'].create({
            'name': "Chambre Parcours",
            'company_id': cls.company.id,
            'base_price': 100000.0,
            'capacity_adults': 2,
        })
        cls.rtype.product_id.sudo().write({'taxes_id': [(5, 0, 0)]})
        cls.room = cls.env['aite.hotel.room'].create({
            'name': 'PR1',
            'hotel_id': cls.hotel.id,
            'room_type_id': cls.rtype.id,
        })
        cls.breakfast = cls.env['aite.hotel.service'].create({
            'name': "Petit-déjeuner Parcours",
            'category': 'restaurant',
            'company_id': cls.company.id,
            'price': 20000.0,
        })
        cls.breakfast.product_id.sudo().write({'taxes_id': [(5, 0, 0)]})

        # --- Caisse --------------------------------------------------------
        # Journal dédié : un journal de caisse ne peut servir qu'à un
        # seul moyen de paiement « espèces », et la base porte déjà le
        # jeu d'essai avec sa propre caisse.
        cls.cash_journal = cls.env['account.journal'].create({
            'name': "Caisse Parcours (test)",
            'type': 'cash',
            'code': 'CPRTS',
            'company_id': cls.company.id,
        })
        cls.method_cash = cls.env['pos.payment.method'].create({
            'name': "Espèces Parcours",
            'journal_id': cls.cash_journal.id,
            'company_id': cls.company.id,
        })
        cls.method_room = cls.env['pos.payment.method'].create({
            'name': "Note de chambre Parcours",
            'is_room_charge': True,
            'company_id': cls.company.id,
        })
        cls.method_credit = cls.env['pos.payment.method'].create({
            'name': "Ardoise Parcours",
            'is_aite_credit': True,
            'company_id': cls.company.id,
        })
        cls.pos_config = cls.env['pos.config'].create({
            'name': "Bar Parcours",
            'payment_method_ids': [(6, 0, (
                cls.method_cash | cls.method_room | cls.method_credit).ids)],
        })
        cls.drink = cls.env['product.product'].create({
            'name': "Jus de bissap",
            'type': 'consu',
            'available_in_pos': True,
            'list_price': 8000.0,
            'standard_price': 3000.0,
            'taxes_id': [(5, 0, 0)],
        })
        cls.pos_config.open_ui()
        cls.session = cls.pos_config.current_session_id

        # --- Espace réservable ---------------------------------------------
        cls.spa = cls.env['aite.booking.resource'].create({
            'name': "SPA Parcours",
            'kind': 'spa',
            'company_id': cls.company.id,
            'capacity': 1,
            'open_hour': 9.0,
            'close_hour': 20.0,
            'slot_minutes': '60',
        })
        cls.massage_product = cls.env['product.product'].create({
            'name': "Massage Parcours",
            'type': 'service',
            'sale_ok': True,
            'list_price': 60000.0,
            'taxes_id': [(5, 0, 0)],
        })
        cls.massage = cls.env['aite.booking.service'].create({
            'name': "Massage 60 min",
            'kind': 'spa',
            'company_id': cls.company.id,
            'duration_minutes': 60,
            'price': 60000.0,
            'product_id': cls.massage_product.id,
        })

        cls.guest = cls.env['res.partner'].create({
            'name': "Aïcha Touré",
            'email': 'aicha.parcours@example.com',
            'phone': '+224 600 12 34 56',
        })

    # ------------------------------------------------------------------
    # Fabriques
    # ------------------------------------------------------------------

    def _pos_order(self, method, amount, partner=None):
        order = self.env['pos.order'].create({
            'session_id': self.session.id,
            'company_id': self.company.id,
            'partner_id': partner.id if partner else False,
            'amount_tax': 0.0,
            'amount_total': amount,
            'amount_paid': amount,
            'amount_return': 0.0,
            'lines': [(0, 0, {
                'product_id': self.drink.id,
                'qty': 1,
                'price_unit': amount,
                'price_subtotal': amount,
                'price_subtotal_incl': amount,
            })],
        })
        self.env['pos.payment'].create({
            'pos_order_id': order.id,
            'payment_method_id': method.id,
            'amount': amount,
        })
        order.write({'state': 'paid'})
        return order

    # ==================================================================
    # Parcours 1 — le séjour complet
    # ==================================================================

    def test_journey_full_stay(self):
        """
        Réserver → acompte → check-in → consommations (bar + SPA) →
        check-out → facture soldée.

        C'est le parcours nominal du PMS : on suit l'argent de bout en
        bout et on vérifie qu'aucune consommation ne se perd.
        """
        Res = self.env['aite.hotel.reservation']

        # 1. La réception enregistre une réservation de 2 nuits.
        reservation = Res.create({
            'hotel_id': self.hotel.id,
            'partner_id': self.guest.id,
            'checkin_date': Res._compose_datetime(self.today, 14.0),
            'checkout_date': Res._compose_datetime(
                self.today + timedelta(days=2), 12.0),
            'line_ids': [(0, 0, {
                'room_type_id': self.rtype.id,
                'room_id': self.room.id,
                'adults': 2,
            })],
        })
        reservation.action_confirm()
        folio = reservation.folio_id
        self.assertEqual(folio.amount_total, 200000.0,
                         "2 nuits à 100 000")

        # 2. Acompte Mobile Money avant l'arrivée.
        self.env['aite.hotel.payment.wizard'].create({
            'folio_id': folio.id,
            'amount': 80000.0,
            'method': 'orange',
            'transaction_ref': 'OM-PARCOURS-1',
        }).action_confirm()
        folio.invalidate_recordset()
        self.assertEqual(folio.amount_paid, 80000.0)
        self.assertEqual(folio.amount_residual, 120000.0)

        # 3. Arrivée du client.
        reservation.action_checkin()
        self.assertEqual(reservation.state, 'checked_in')
        self.room.invalidate_recordset()
        self.assertEqual(self.room.status, 'occupied')

        # 4. Consommation au bar, portée sur la note de chambre.
        bar_order = self._pos_order(self.method_room, 8000.0,
                                    partner=self.guest)
        self.assertTrue(bar_order.aite_folio_line_id,
                        "la consommation doit rejoindre le folio")
        self.assertEqual(bar_order.aite_folio_line_id.folio_id, folio)

        # 5. Soin au SPA, également reporté sur le folio.
        booking = self.env['aite.slot.booking'].create({
            'resource_id': self.spa.id,
            'partner_id': self.guest.id,
            'company_id': self.company.id,
            'service_id': self.massage.id,
            'start': fields.Datetime.to_datetime(
                '%s 15:00:00' % (self.today + timedelta(days=1))),
            'stop': fields.Datetime.to_datetime(
                '%s 16:00:00' % (self.today + timedelta(days=1))),
        })
        booking.action_confirm()
        booking.action_done()
        self.assertTrue(booking.posted_line_id,
                        "la prestation doit rejoindre le folio")

        # 6. Le folio porte bien nuitées + extras.
        folio.invalidate_recordset()
        self.assertEqual(folio.amount_room, 200000.0)
        self.assertEqual(folio.amount_service, 68000.0)
        self.assertEqual(folio.amount_total, 268000.0)

        # 7. Check-out : facture émise, chambre au ménage.
        self.env['aite.hotel.checkout.wizard'].create({
            'reservation_id': reservation.id,
            'checkout_now': Res._compose_datetime(
                self.today + timedelta(days=2), 12.0),
        }).action_confirm()
        self.assertEqual(reservation.state, 'checked_out')
        invoice = folio.move_id
        self.assertTrue(invoice)
        self.assertEqual(invoice.amount_total, 268000.0,
                         "la facture reprend exactement le folio")
        self.assertEqual(self.room.hk_state, 'to_clean')

        # 8. Solde réglé au comptoir.
        self.env['aite.hotel.payment.wizard'].create({
            'folio_id': folio.id,
            'amount': folio.amount_residual,
            'method': 'cash',
        }).action_confirm()
        folio.invalidate_recordset()
        self.assertEqual(folio.amount_residual, 0.0)
        self.assertEqual(folio.state, 'paid')

    # ==================================================================
    # Parcours 2 — la vente à crédit et son recouvrement
    # ==================================================================

    def test_journey_credit_sale_and_recovery(self):
        """
        Vente mixte au bar (comptant + ardoise) → encours client →
        remboursements successifs → ardoise soldée, encours à zéro.
        """
        # 1. Vente de 50 000 : 20 000 comptant, 30 000 sur ardoise.
        order = self.env['pos.order'].create({
            'session_id': self.session.id,
            'company_id': self.company.id,
            'partner_id': self.guest.id,
            'amount_tax': 0.0,
            'amount_total': 50000.0,
            'amount_paid': 50000.0,
            'amount_return': 0.0,
            'lines': [(0, 0, {
                'product_id': self.drink.id,
                'qty': 1,
                'price_unit': 50000.0,
                'price_subtotal': 50000.0,
                'price_subtotal_incl': 50000.0,
            })],
        })
        for method, amount in ((self.method_cash, 20000.0),
                               (self.method_credit, 30000.0)):
            self.env['pos.payment'].create({
                'pos_order_id': order.id,
                'payment_method_id': method.id,
                'amount': amount,
            })
        order.write({'state': 'paid'})
        order._aite_create_credit_if_needed()

        credit = order.credit_id
        self.assertTrue(credit, "la part à crédit doit créer une ardoise")
        self.assertEqual(credit.amount_total, 30000.0)
        self.assertEqual(order.amount_paid_direct, 20000.0)

        # 2. L'encours remonte sur la fiche client.
        self.guest.invalidate_recordset()
        self.assertEqual(self.guest.credit_outstanding, 30000.0)
        self.assertEqual(self.guest.credit_ardoise_count, 1)

        # 3. Premier remboursement partiel.
        self.env['aite.pos.credit.repay.wizard'].create({
            'credit_id': credit.id,
            'amount': 10000.0,
            'method': 'mtn',
        }).action_confirm()
        credit.invalidate_recordset()
        self.assertEqual(credit.amount_residual, 20000.0)
        self.assertEqual(credit.state, 'open')

        # 4. Solde : l'ardoise se referme et l'encours retombe à zéro.
        self.env['aite.pos.credit.repay.wizard'].create({
            'credit_id': credit.id,
            'amount': 20000.0,
            'method': 'cash',
        }).action_confirm()
        credit.invalidate_recordset()
        self.assertEqual(credit.amount_residual, 0.0)
        self.assertEqual(credit.state, 'paid')
        self.guest.invalidate_recordset()
        self.assertEqual(self.guest.credit_outstanding, 0.0)

    # ==================================================================
    # Parcours 3 — la note de chambre ambiguë
    # ==================================================================

    def test_journey_ambiguous_room_charge(self):
        """
        Consommation anonyme au bar → file d'attente → la réception
        choisit le folio → la consommation rejoint la note de séjour.
        """
        Res = self.env['aite.hotel.reservation']
        reservation = Res.create({
            'hotel_id': self.hotel.id,
            'partner_id': self.guest.id,
            'checkin_date': Res._compose_datetime(self.today, 14.0),
            'checkout_date': Res._compose_datetime(
                self.today + timedelta(days=1), 12.0),
            'line_ids': [(0, 0, {
                'room_type_id': self.rtype.id,
                'room_id': self.room.id,
                'adults': 1,
            })],
        })
        reservation.action_confirm()
        folio = reservation.folio_id
        before = folio.amount_total

        # Le serveur oublie d'identifier le client.
        order = self._pos_order(self.method_room, 12000.0, partner=None)
        pending = order.aite_roomcharge_pending_id
        self.assertTrue(pending, "la note doit partir en file d'attente")
        self.assertFalse(order.aite_folio_line_id)

        # La réception tranche.
        pending.folio_id = folio.id
        pending.action_resolve()
        self.assertEqual(pending.state, 'done')
        self.assertTrue(order.aite_folio_line_id)
        folio.invalidate_recordset()
        self.assertEqual(folio.amount_total, before + 12000.0)
        self.assertEqual(pending.partner_id, self.guest,
                         "le client est complété depuis le folio")

    # ==================================================================
    # Parcours 4 — la fidélité multi-services
    # ==================================================================

    def test_journey_loyalty_across_services(self):
        """
        Le client consomme au bar, à l'hôtel et au SPA : un capital de
        points unique, et la diversité compte pour le statut VVIP.
        """
        engine = self.env['aite.loyalty.engine']
        self.company.write({
            'aite_loyalty_rate_per_1000': 1.0,
            'aite_loyalty_min_amount': 1000.0,
            'aite_loyalty_vip_min_spend': 300000.0,
            'aite_loyalty_vip_min_visits': 3,
            'aite_loyalty_vvip_min_spend': 600000.0,
            'aite_loyalty_vvip_min_visits': 3,
            'aite_loyalty_vvip_min_domains': 3,
        })
        # Trois domaines, trois jours distincts.
        for offset, (amount, origin) in enumerate([
            (250000.0, 'pos'),
            (300000.0, 'hotel'),
            (150000.0, 'slot_spa'),
        ]):
            engine.award(self.guest, amount, origin,
                         when=self.today - timedelta(days=offset + 1))

        self.guest.invalidate_recordset()
        self.assertEqual(self.guest.loyalty_points, 250 + 300 + 150)

        engine.recompute_tiers(partner_ids=[self.guest.id])
        self.guest.invalidate_recordset()
        self.assertEqual(self.guest.loyalty_tier, 'vvip',
                         "700 000 dépensés, 3 visites, 3 domaines ⇒ VVIP")

    # ==================================================================
    # Parcours 5 — la vue consolidée de la direction
    # ==================================================================

    def test_journey_management_consolidation(self):
        """
        Activité sur trois pôles → le cockpit Direction et le tableau
        exécutif la restituent sans divergence avec les moteurs.
        """
        Res = self.env['aite.hotel.reservation']
        reservation = Res.create({
            'hotel_id': self.hotel.id,
            'partner_id': self.guest.id,
            'checkin_date': Res._compose_datetime(self.today, 14.0),
            'checkout_date': Res._compose_datetime(
                self.today + timedelta(days=1), 12.0),
            'line_ids': [(0, 0, {
                'room_type_id': self.rtype.id,
                'room_id': self.room.id,
                'adults': 1,
            })],
        })
        reservation.action_confirm()
        self._pos_order(self.method_cash, 25000.0, partner=self.guest)
        self.env.flush_all()

        d_from = fields.Date.to_string(self.today - timedelta(days=7))
        d_to = fields.Date.to_string(self.today)

        # Le cockpit ne recalcule pas : il orchestre.
        direction = self.env['aite.direction.dashboard']
        pos_engine = self.env['aite.pos.dashboard']
        self.assertEqual(
            direction.get_pos_tab(d_from, d_to)['kpis']['ca'],
            pos_engine.get_kpis(d_from, d_to)['ca'])

        # Le tableau exécutif consolide les trois pôles.
        exec_kpis = self.env['aite.exec.dashboard'].get_kpis(d_from, d_to)
        self.assertAlmostEqual(
            exec_kpis['total_ca'],
            exec_kpis['hotel_ca'] + exec_kpis['pos_ca']
            + exec_kpis['slots_ca'], places=2)
        self.assertGreater(exec_kpis['hotel_ca'], 0.0)

    # ==================================================================
    # Parcours 6 — la gouvernante suit le départ
    # ==================================================================

    def test_journey_housekeeping_after_checkout(self):
        """Départ → recouche créée → ménage fait → chambre revendable."""
        Res = self.env['aite.hotel.reservation']
        reservation = Res.create({
            'hotel_id': self.hotel.id,
            'partner_id': self.guest.id,
            'checkin_date': Res._compose_datetime(self.today, 14.0),
            'checkout_date': Res._compose_datetime(
                self.today + timedelta(days=1), 12.0),
            'line_ids': [(0, 0, {
                'room_type_id': self.rtype.id,
                'room_id': self.room.id,
                'adults': 1,
            })],
        })
        reservation.action_confirm()
        reservation.action_checkin()
        self.env['aite.hotel.checkout.wizard'].create({
            'reservation_id': reservation.id,
            'checkout_now': Res._compose_datetime(
                self.today + timedelta(days=1), 12.0),
            'create_invoice': False,
        }).action_confirm()

        task = self.env['aite.hotel.housekeeping'].search([
            ('room_id', '=', self.room.id),
            ('task_type', '=', 'checkout_clean'),
        ], limit=1)
        self.assertTrue(task, "le départ doit créer la recouche")
        self.assertEqual(self.room.hk_state, 'to_clean')

        task.action_start()
        self.assertEqual(self.room.hk_state, 'cleaning')
        task.action_done()
        self.assertEqual(self.room.hk_state, 'clean')

        # La chambre est de nouveau vendable.
        self.room.invalidate_recordset()
        self.assertEqual(self.room.status, 'free')
        self.assertTrue(self.room.is_available(
            Res._compose_datetime(self.today + timedelta(days=3), 14.0),
            Res._compose_datetime(self.today + timedelta(days=4), 12.0)))
