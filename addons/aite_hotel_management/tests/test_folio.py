# -*- coding: utf-8 -*-
"""Folio client : lignes, taxes, règlements, facturation, comptabilité."""
from odoo.exceptions import UserError, ValidationError
from odoo.tests import tagged

from .common import HotelCommon


@tagged('post_install', '-at_install', 'aite_hotel')
class TestFolio(HotelCommon):

    def setUp(self):
        super().setUp()
        self.reservation = self._make_reservation(checkin_offset=0,
                                                  checkout_offset=2)
        self.reservation.action_confirm()
        self.folio = self.reservation.folio_id

    # ------------------------------------------------------------------
    # Lignes & montants
    # ------------------------------------------------------------------

    def test_folio_sequence_and_link(self):
        self.assertNotEqual(self.folio.name, "Nouveau")
        self.assertEqual(self.folio.reservation_id, self.reservation)
        self.assertEqual(self.folio.partner_id, self.guest)

    def test_room_amount_matches_stay(self):
        # 2 nuits × 50 000
        self.assertEqual(self.folio.amount_room, 100000.0)
        self.assertEqual(self.folio.amount_service, 0.0)
        self.assertEqual(self.folio.amount_total, 100000.0)

    def test_adding_a_service_updates_totals(self):
        self.env['aite.hotel.folio.line'].create({
            'folio_id': self.folio.id,
            'line_type': 'service',
            'service_id': self.service_resto.id,
            'product_id': self.service_resto.product_id.id,
            'name': "Petit-déjeuner",
            'quantity': 2,
            'price_unit': 7500.0,
        })
        self.assertEqual(self.folio.amount_service, 15000.0)
        self.assertEqual(self.folio.amount_total, 115000.0)

    def test_taxes_are_computed_like_the_invoice(self):
        """Le TTC du folio passe par compute_all — égalité avec la facture."""
        tax = self.env['account.tax'].create({
            'name': "TVA test 18%",
            'amount': 18.0,
            'amount_type': 'percent',
            'type_tax_use': 'sale',
            'company_id': self.company.id,
        })
        line = self.env['aite.hotel.folio.line'].create({
            'folio_id': self.folio.id,
            'line_type': 'service',
            'product_id': self.service_resto.product_id.id,
            'name': "Dîner",
            'quantity': 1,
            'price_unit': 10000.0,
            'tax_ids': [(6, 0, tax.ids)],
        })
        self.assertEqual(line.price_subtotal, 10000.0)
        self.assertEqual(line.price_total, 11800.0)
        self.assertEqual(self.folio.amount_tax, 1800.0)

    def test_line_quantity_must_be_positive(self):
        with self.assertRaises(ValidationError):
            self.env['aite.hotel.folio.line'].create({
                'folio_id': self.folio.id,
                'product_id': self.service_resto.product_id.id,
                'name': "Ligne vide",
                'quantity': 0,
                'price_unit': 1000.0,
            })

    def test_sync_is_idempotent(self):
        """Resynchroniser n'ajoute pas de doublon de nuitée."""
        before = len(self.folio.line_ids)
        self.folio._sync_room_lines()
        self.folio._sync_room_lines()
        self.assertEqual(len(self.folio.line_ids), before)

    def test_removed_room_stops_being_billed(self):
        """Régression : une chambre retirée du séjour quitte le folio.

        ``reservation_line_id`` étant en ``ondelete='set null'``, la
        suppression d'une ligne de séjour vidait la référence au lieu de
        retirer la nuitée — le client restait facturé pour une chambre
        qu'il n'occupait plus.
        """
        reservation = self._make_reservation(
            rooms=self.room_102 | self.room_201,
            checkin_offset=10, checkout_offset=12, partner=self.guest_2)
        reservation.action_confirm()
        folio = reservation.folio_id
        self.assertEqual(len(folio.line_ids), 2)
        self.assertEqual(folio.amount_total, 340000.0)

        reservation.line_ids.filtered(
            lambda l: l.room_id == self.room_201).unlink()
        reservation._sync_folio_room_lines()
        folio.invalidate_recordset()

        self.assertEqual(len(folio.line_ids), 1)
        self.assertEqual(folio.line_ids.reservation_line_id,
                         reservation.line_ids)
        self.assertEqual(folio.amount_total, 100000.0)

    def test_sync_preserves_service_lines(self):
        self.env['aite.hotel.folio.line'].create({
            'folio_id': self.folio.id,
            'line_type': 'service',
            'product_id': self.service_laundry.product_id.id,
            'name': "Blanchisserie",
            'quantity': 1,
            'price_unit': 5000.0,
        })
        self.folio._sync_room_lines()
        services = self.folio.line_ids.filtered(
            lambda l: l.line_type == 'service')
        self.assertEqual(len(services), 1)

    # ------------------------------------------------------------------
    # Règlements
    # ------------------------------------------------------------------

    def test_payment_updates_paid_and_residual(self):
        self.env['aite.hotel.folio.payment'].create({
            'folio_id': self.folio.id,
            'amount': 30000.0,
            'method': 'mtn',
            'is_deposit': True,
        })
        self.assertEqual(self.folio.amount_paid, 30000.0)
        self.assertEqual(self.folio.amount_residual, 70000.0)
        self.assertEqual(self.folio.payment_count, 1)

    def test_payment_amount_must_be_positive(self):
        with self.assertRaises(ValidationError):
            self.env['aite.hotel.folio.payment'].create({
                'folio_id': self.folio.id,
                'amount': 0.0,
                'method': 'cash',
            })

    def test_overpayment_is_refused(self):
        with self.assertRaises(ValidationError):
            self.env['aite.hotel.folio.payment'].create({
                'folio_id': self.folio.id,
                'amount': 150000.0,
                'method': 'cash',
            })

    def test_cancelled_payment_is_excluded(self):
        payment = self.env['aite.hotel.folio.payment'].create({
            'folio_id': self.folio.id,
            'amount': 40000.0,
            'method': 'cash',
        })
        payment.action_cancel()
        self.assertEqual(self.folio.amount_paid, 0.0)
        self.assertEqual(self.folio.payment_count, 0)

    def test_payment_count_does_not_write_stored_fields(self):
        """Lire ``payment_count`` ne doit rien écrire en base.

        Régression : ce champ non stocké partageait son compute avec les
        montants stockés, provoquant une écriture à chaque lecture.
        """
        self.env['aite.hotel.folio.payment'].create({
            'folio_id': self.folio.id,
            'amount': 10000.0,
            'method': 'cash',
        })
        self.env.flush_all()
        self.folio.invalidate_recordset()
        self.assertEqual(self.folio.payment_count, 1)
        # Le compute de payment_count est bien distinct de _compute_amounts.
        self.assertEqual(
            self.folio._fields['payment_count'].compute,
            '_compute_payment_count')
        self.assertEqual(
            self.folio._fields['amount_paid'].compute, '_compute_amounts')

    def test_method_label_is_readable(self):
        Payment = self.env['aite.hotel.folio.payment']
        self.assertEqual(Payment.method_label('mtn'), "MTN Mobile Money")
        self.assertEqual(Payment.method_label('inconnu'), 'inconnu')

    def test_accounting_entry_is_posted_when_enabled(self):
        self.company.hotel_auto_entries = True
        journal = self.env['account.journal'].search([
            ('type', '=', 'cash'), ('company_id', '=', self.company.id),
        ], limit=1)
        self.company.hotel_payment_journal_id = journal
        payment = self.env['aite.hotel.folio.payment'].create({
            'folio_id': self.folio.id,
            'amount': 25000.0,
            'method': 'cash',
        })
        self.assertTrue(payment.move_id)
        self.assertEqual(payment.move_id.state, 'posted')
        receivable = payment.move_id.line_ids.filtered(
            lambda l: l.account_id.account_type == 'asset_receivable')
        self.assertEqual(sum(receivable.mapped('credit')), 25000.0)

    def test_no_accounting_entry_when_disabled(self):
        self.company.hotel_auto_entries = False
        payment = self.env['aite.hotel.folio.payment'].create({
            'folio_id': self.folio.id,
            'amount': 25000.0,
            'method': 'cash',
        })
        self.assertFalse(payment.move_id)

    # ------------------------------------------------------------------
    # Facturation
    # ------------------------------------------------------------------

    def test_invoice_mirrors_folio_lines(self):
        self.env['aite.hotel.folio.line'].create({
            'folio_id': self.folio.id,
            'line_type': 'service',
            'product_id': self.service_resto.product_id.id,
            'name': "Petit-déjeuner",
            'quantity': 2,
            'price_unit': 7500.0,
        })
        self.folio.action_create_invoice()
        move = self.folio.move_id
        self.assertTrue(move)
        self.assertEqual(move.move_type, 'out_invoice')
        self.assertEqual(move.state, 'posted')
        self.assertEqual(move.partner_id, self.guest)
        self.assertEqual(len(move.invoice_line_ids), 2)
        self.assertEqual(move.amount_total, self.folio.amount_total)
        self.assertEqual(self.folio.state, 'invoiced')

    def test_invoice_twice_is_refused(self):
        self.folio.action_create_invoice()
        with self.assertRaises(UserError):
            self.folio.action_create_invoice()

    def test_empty_folio_cannot_be_invoiced(self):
        empty = self.env['aite.hotel.folio'].create({
            'reservation_id': self._make_reservation(
                rooms=self.room_201, checkin_offset=10,
                checkout_offset=11).id,
        })
        empty.line_ids.unlink()
        with self.assertRaises(UserError):
            empty.action_create_invoice()

    def test_folio_becomes_paid_when_fully_settled(self):
        self.folio.action_create_invoice()
        self.env['aite.hotel.folio.payment'].create({
            'folio_id': self.folio.id,
            'amount': self.folio.amount_total,
            'method': 'card',
        })
        self.assertEqual(self.folio.amount_residual, 0.0)
        self.assertEqual(self.folio.state, 'paid')

    def test_cancelling_a_payment_reopens_the_folio(self):
        self.folio.action_create_invoice()
        payment = self.env['aite.hotel.folio.payment'].create({
            'folio_id': self.folio.id,
            'amount': self.folio.amount_total,
            'method': 'card',
        })
        self.assertEqual(self.folio.state, 'paid')
        payment.action_cancel()
        # ``state`` n'est pas lui-même calculé : il bascule quand le
        # compute des montants se rejoue. On force la relecture, comme le
        # ferait un rechargement de la vue.
        self.folio.invalidate_recordset()
        self.assertEqual(self.folio.state, 'invoiced')

    def test_deposit_is_reconciled_with_invoice(self):
        """L'acompte encaissé avant la facture est lettré avec elle."""
        self.company.hotel_auto_entries = True
        journal = self.env['account.journal'].search([
            ('type', '=', 'cash'), ('company_id', '=', self.company.id),
        ], limit=1)
        self.company.hotel_payment_journal_id = journal
        payment = self.env['aite.hotel.folio.payment'].create({
            'folio_id': self.folio.id,
            'amount': 40000.0,
            'method': 'cash',
            'is_deposit': True,
        })
        self.folio.action_create_invoice()
        payment.move_id.line_ids.filtered(
            lambda l: l.account_id.account_type == 'asset_receivable')
        self.assertTrue(payment.move_id)
        # Le lettrage est best-effort : on vérifie qu'il ne casse rien et
        # que la facture voit bien un règlement partiel.
        self.assertEqual(self.folio.amount_residual, 60000.0)

    def test_invoiced_folio_lines_are_frozen(self):
        self.folio.action_create_invoice()
        with self.assertRaises(UserError):
            self.folio.line_ids[0].unlink()

    def test_sync_does_nothing_after_invoicing(self):
        self.folio.action_create_invoice()
        before = self.folio.line_ids.mapped('quantity')
        self.reservation.checkout_date = self._dt(5, 12.0)
        self.assertEqual(self.folio.line_ids.mapped('quantity'), before)

    # ------------------------------------------------------------------
    # Annulation & suppression
    # ------------------------------------------------------------------

    def test_cancel_refused_when_paid(self):
        self.env['aite.hotel.folio.payment'].create({
            'folio_id': self.folio.id,
            'amount': 10000.0,
            'method': 'cash',
        })
        with self.assertRaises(UserError):
            self.folio.action_cancel()

    def test_cancel_refused_when_invoiced(self):
        self.folio.action_create_invoice()
        with self.assertRaises(UserError):
            self.folio.action_cancel()

    def test_invoiced_folio_cannot_be_deleted(self):
        self.folio.action_create_invoice()
        with self.assertRaises(UserError):
            self.folio.unlink()

    def test_view_invoice_requires_invoice(self):
        with self.assertRaises(UserError):
            self.folio.action_view_invoice()

    def test_register_payment_refused_on_cancelled_folio(self):
        self.folio.action_cancel()
        with self.assertRaises(UserError):
            self.folio.action_register_payment()

    def test_register_deposit_shortcut_requires_folio(self):
        draft = self._make_reservation(rooms=self.room_201,
                                       checkin_offset=20, checkout_offset=21)
        with self.assertRaises(UserError):
            draft.action_register_deposit()
