# -*- coding: utf-8 -*-
"""Écarts non bloquants relevés en tournant les tutoriels vidéo
(docs/videos/ECARTS.md, n° 37 à 77, partie socle).

Chaque classe reproduit un écart avant sa correction :

* n° 37 — dates lisibles (``%d/%m/%Y``, fuseau de l'utilisateur) dans le
  libellé de nuitée (repris sur la facture) et dans les refus ;
* n° 40 — montant du surclassement gracieux écrit avec la devise ;
* n° 42 — état « Non présenté » plutôt que « No-show » ;
* n° 43 — « Réservation créée » (et non « Réservation hôtelière créé ») ;
* n° 45 — l'assistant de réservation rapide garde son titre ;
* n° 52 — la recouche terminée crée la tâche d'inspection ;
* n° 56 — canal choisi dans la réservation rapide ; nuitée datée de
  l'arrivée (elle ne passe plus après les extras au départ) ;
* n° 75 — l'acompte est réellement lettré avec la facture.
"""
import re
from datetime import timedelta
from unittest.mock import patch

from odoo import fields
from odoo.exceptions import UserError
from odoo.tests import tagged
from odoo.tools.misc import format_amount

from .common import HotelCommon

ISO_DATE = re.compile(r'\d{4}-\d{2}-\d{2}')


def _user(env, login, group_xmlid):
    return env['res.users'].create({
        'name': login,
        'login': login,
        'groups_id': [(6, 0, [
            env.ref('base.group_user').id, env.ref(group_xmlid).id,
        ])],
    })


@tagged('post_install', '-at_install', 'aite_hotel')
class TestReadableDates(HotelCommon):
    """Écart n° 37 : dates au format français, à l'heure locale."""

    def setUp(self):
        super().setUp()
        # Fuseau très en avance sur l'UTC : une arrivée à 8 h locale tombe
        # la veille en UTC, ce qui révèle une date lue sans conversion.
        self.env.user.tz = 'Asia/Tokyo'
        self.day = fields.Date.context_today(self.env.user) + timedelta(
            days=1)
        Res = self.env['aite.hotel.reservation']
        self.cin = Res._compose_datetime(self.day, 8.0)
        self.cout = Res._compose_datetime(self.day + timedelta(days=2), 12.0)

    def _stay(self, partner=None):
        return self.env['aite.hotel.reservation'].create({
            'hotel_id': self.hotel.id,
            'partner_id': (partner or self.guest).id,
            'checkin_date': self.cin,
            'checkout_date': self.cout,
            'line_ids': [(0, 0, {
                'room_type_id': self.type_std.id,
                'room_id': self.room_101.id,
                'adults': 1,
            })],
        })

    def test_night_label_uses_local_french_dates(self):
        self.assertNotEqual(self.cin.date(), self.day,
                            "Le jeu d'essai doit franchir minuit en UTC.")
        reservation = self._stay()
        reservation.action_confirm()
        label = reservation.folio_id.line_ids.filtered(
            lambda l: l.line_type == 'room').name
        self.assertIn(self.day.strftime('%d/%m/%Y'), label)
        self.assertIn(
            (self.day + timedelta(days=2)).strftime('%d/%m/%Y'), label)
        self.assertFalse(ISO_DATE.search(label), label)

    def test_unavailability_message_in_local_time(self):
        self._stay().action_confirm()
        other = self._stay(partner=self.guest_2)
        with self.assertRaises(UserError) as err:
            other.action_confirm()
        message = str(err.exception)
        self.assertIn(self.day.strftime('%d/%m/%Y') + " 08:00", message)
        self.assertFalse(ISO_DATE.search(message), message)

    def test_hotel_change_keeps_the_local_day(self):
        """Choisir l'hôtel recale les heures sur les siennes, le même jour
        local : composé depuis le jour UTC, l'arrivée reculait d'un jour."""
        Res = self.env['aite.hotel.reservation']
        reservation = Res.new({
            'hotel_id': self.hotel.id,
            'partner_id': self.guest.id,
            'checkin_date': self.cin,
            'checkout_date': self.cout,
        })
        reservation._onchange_hotel_id()
        self.assertEqual(reservation.checkin_date,
                         Res._compose_datetime(self.day, 14.0))
        self.assertEqual(reservation.checkout_date,
                         Res._compose_datetime(
                             self.day + timedelta(days=2), 12.0))

    def test_early_checkin_message_in_french_format(self):
        receptionist = _user(self.env, 'reception.ecart37',
                             'aite_hotel_management.group_hotel_user')
        receptionist.tz = 'Asia/Tokyo'
        reservation = self._stay()
        reservation.action_confirm()
        self.env.invalidate_all()
        with self.assertRaises(UserError) as err:
            reservation.with_user(receptionist).action_checkin()
        message = str(err.exception)
        self.assertIn(self.day.strftime('%d/%m/%Y'), message)
        self.assertFalse(ISO_DATE.search(message), message)


@tagged('post_install', '-at_install', 'aite_hotel')
class TestReadableAmounts(HotelCommon):
    """Écart n° 40 : le tarif conservé est écrit comme un montant."""

    def test_kept_price_message_is_formatted_with_currency(self):
        reservation = self._make_reservation(checkin_offset=0,
                                             checkout_offset=2)
        reservation.action_confirm()
        self.env['aite.hotel.room.change.wizard'].create({
            'line_id': reservation.line_ids.id,
            'new_room_id': self.room_201.id,
            'keep_price': True,
        }).action_confirm()
        # Le corps HTML écrit l'espace insécable du montant « &nbsp; ».
        body = str(reservation.message_ids[:1].body).replace(
            '&nbsp;', '\xa0')
        expected = format_amount(self.env, 50000.0,
                                 reservation.currency_id)
        self.assertIn(expected, body)
        self.assertNotIn("50000.0", body)


@tagged('post_install', '-at_install', 'aite_hotel')
class TestFrenchLabels(HotelCommon):
    """Écarts n° 42 et 43 : libellés français et accord du chatter."""

    def test_no_show_state_is_french(self):
        states = dict(self.env['aite.hotel.reservation']
                      ._fields['state'].selection)
        self.assertEqual(states['no_show'], "Non présenté")

    def test_creation_message_agrees_in_gender(self):
        reservation = self._make_reservation()
        self.assertEqual(reservation._creation_message(),
                         "Réservation créée")
        task = self.env['aite.hotel.housekeeping'].create({
            'room_id': self.room_101.id,
        })
        self.assertEqual(task._creation_message(),
                         "Tâche de ménage créée")


@tagged('post_install', '-at_install', 'aite_hotel')
class TestQuickBookingWizard(HotelCommon):
    """Écarts n° 45 et 56 : titre et canal de la réservation rapide."""

    def _wizard(self, **vals):
        values = {
            'hotel_id': self.hotel.id,
            'checkin_date': self._dt(1, 14.0),
            'checkout_date': self._dt(3, 12.0),
        }
        values.update(vals)
        return self.env['aite.hotel.booking.wizard'].create(values)

    def test_search_keeps_the_window_title(self):
        action = self._wizard().action_search()
        self.assertEqual(action.get('name'), "Réservation rapide")

    def test_channel_is_carried_to_the_reservation(self):
        wizard = self._wizard(partner_id=self.guest.id, source='phone')
        wizard.action_search()
        wizard.line_ids.filtered(
            lambda l: l.room_id == self.room_101).selected = True
        action = wizard.action_book()
        reservation = self.env['aite.hotel.reservation'].browse(
            action['res_id'])
        self.assertEqual(reservation.source, 'phone')

    def test_agent_channel_carries_the_agent(self):
        wizard = self._wizard(partner_id=self.guest.id, source='agent',
                              agent_id=self.agent.id)
        wizard.action_search()
        wizard.line_ids[:1].selected = True
        reservation = self.env['aite.hotel.reservation'].browse(
            wizard.action_book()['res_id'])
        self.assertEqual(reservation.source, 'agent')
        self.assertEqual(reservation.agent_id, self.agent)

    def test_default_channel_stays_direct(self):
        self.assertEqual(self._wizard().source, 'direct')


@tagged('post_install', '-at_install', 'aite_hotel')
class TestNightLineDate(HotelCommon):
    """Écart n° 56 : la nuitée est datée de l'arrivée, pas du jour où le
    folio est resynchronisé (prolongation, départ)."""

    def test_night_line_is_dated_from_arrival(self):
        reservation = self._make_reservation(checkin_offset=1,
                                             checkout_offset=3)
        reservation.action_confirm()
        arrival = fields.Date.context_today(self.env.user) + timedelta(
            days=1)
        room_line = reservation.folio_id.line_ids.filtered(
            lambda l: l.line_type == 'room')
        self.assertEqual(room_line.date, arrival)
        # Prolongation : la nuitée garde sa date d'arrivée.
        reservation.checkout_date = self._dt(4, 12.0)
        self.assertEqual(room_line.date, arrival)

    def test_night_line_sorts_before_extras(self):
        reservation = self._make_reservation(checkin_offset=-2,
                                             checkout_offset=1)
        reservation.action_confirm()
        reservation.action_checkin()
        folio = reservation.folio_id
        self.env['aite.hotel.folio.line'].create({
            'folio_id': folio.id,
            'line_type': 'service',
            'service_id': self.service_resto.id,
            'product_id': self.service_resto.product_id.id,
            'name': "Petit-déjeuner",
            'quantity': 1,
            'price_unit': 7500.0,
            'date': fields.Date.context_today(self.env.user)
            - timedelta(days=1),
        })
        # Le départ resynchronise les nuitées.
        self.env['aite.hotel.checkout.wizard'].create({
            'reservation_id': reservation.id,
            'create_invoice': False,
        }).action_confirm()
        folio.invalidate_recordset(['line_ids'])
        self.assertEqual(folio.line_ids[:1].line_type, 'room')


@tagged('post_install', '-at_install', 'aite_hotel')
class TestInspectionTask(HotelCommon):
    """Écart n° 52 (partie socle) : une chambre « à inspecter » a sa
    tâche d'inspection, la gouvernante n'a rien à créer."""

    def _clean(self, room):
        task = self.env['aite.hotel.housekeeping'].create({
            'room_id': room.id,
            'task_type': 'checkout_clean',
        })
        task.action_start()
        task.action_done()
        return task

    def _inspections(self, room):
        return self.env['aite.hotel.housekeeping'].search([
            ('room_id', '=', room.id),
            ('task_type', '=', 'inspection'),
            ('state', 'in', ('todo', 'in_progress')),
        ])

    def test_checkout_clean_creates_inspection_when_required(self):
        self.company.hotel_inspection_required = True
        self._clean(self.room_101)
        self.assertEqual(self.room_101.hk_state, 'inspect')
        self.assertEqual(len(self._inspections(self.room_101)), 1)

    def test_no_duplicate_inspection(self):
        self.company.hotel_inspection_required = True
        self._clean(self.room_101)
        self._clean(self.room_101)
        self.assertEqual(len(self._inspections(self.room_101)), 1)

    def test_room_attendant_finishing_creates_the_inspection(self):
        """L'équipière (profil Gouvernante seul) clique « C'est fait » :
        la tâche d'inspection se crée sans erreur d'accès."""
        self.company.hotel_inspection_required = True
        attendant = _user(self.env, 'equipiere.ecart52',
                          'aite_hotel_management.group_hotel_housekeeping')
        task = self.env['aite.hotel.housekeeping'].create({
            'room_id': self.room_102.id,
            'task_type': 'checkout_clean',
        })
        self.env.invalidate_all()
        task.with_user(attendant).action_start()
        task.with_user(attendant).action_done()
        self.assertEqual(len(self._inspections(self.room_102)), 1)

    def test_no_inspection_when_not_required(self):
        self.company.hotel_inspection_required = False
        self._clean(self.room_101)
        self.assertEqual(self.room_101.hk_state, 'clean')
        self.assertFalse(self._inspections(self.room_101))

    def test_room_declared_clean_closes_its_inspection(self):
        """« Conforme » sur la chambre (bouton de la carte ou de la fiche,
        visible en « À inspecter ») : l'inspection ouverte est close avec
        elle, elle ne traîne plus dans les tâches (relecture du n° 52)."""
        self.company.hotel_inspection_required = True
        self._clean(self.room_101)
        inspection = self._inspections(self.room_101)
        self.room_101.action_set_clean()
        self.assertEqual(self.room_101.hk_state, 'clean')
        self.assertFalse(self._inspections(self.room_101))
        # La chambre a été acceptée : l'inspection est faite.
        self.assertEqual(inspection.state, 'done')

    def test_next_cleaning_gets_a_fresh_inspection(self):
        """Recouche → « Conforme » sur la chambre → recouche suivante
        (jours plus tard) : une inspection du jour, pas l'ancienne."""
        self.company.hotel_inspection_required = True
        self._clean(self.room_101)
        old = self._inspections(self.room_101)
        old.date = fields.Date.context_today(self.env.user) - timedelta(
            days=3)
        self.room_101.action_set_clean()
        self._clean(self.room_101)
        fresh = self._inspections(self.room_101)
        self.assertEqual(len(fresh), 1)
        self.assertNotEqual(fresh, old)
        self.assertEqual(fresh.date,
                         fields.Date.context_today(self.env.user))

    def test_room_forced_clean_cancels_a_pending_inspection(self):
        """Inspection en attente pendant qu'on refait la chambre, puis
        chambre déclarée propre sans repasser par « À inspecter » :
        l'inspection n'a pas eu lieu, elle est annulée (pas laissée
        ouverte)."""
        self.company.hotel_inspection_required = True
        self._clean(self.room_101)
        inspection = self._inspections(self.room_101)
        # Refus « à la main » : la chambre repart en ménage, l'inspection
        # attend la recouche suivante.
        self.room_101.hk_state = 'cleaning'
        self.room_101.action_set_clean()
        self.assertFalse(self._inspections(self.room_101))
        self.assertEqual(inspection.state, 'cancelled')

    def test_reused_inspection_is_dated_today(self):
        """Une recouche refaite retrouve l'inspection qui attend déjà :
        elle est ramenée au jour, sinon elle sortait des listes du
        jour."""
        self.company.hotel_inspection_required = True
        self._clean(self.room_101)
        inspection = self._inspections(self.room_101)
        inspection.date = fields.Date.context_today(
            self.env.user) - timedelta(days=2)
        self.room_101.hk_state = 'to_clean'
        self._clean(self.room_101)
        self.assertEqual(self._inspections(self.room_101), inspection)
        self.assertEqual(inspection.date,
                         fields.Date.context_today(self.env.user))

    def test_receptionist_checkin_closes_the_inspection(self):
        """Le check-in déclare la chambre propre : la Réception (sans
        droit de suppression ni rôle de gouvernante particulier) clôt
        l'inspection sans erreur d'accès."""
        self.company.hotel_inspection_required = True
        self._clean(self.room_101)
        receptionist = _user(self.env, 'reception.ecart52',
                             'aite_hotel_management.group_hotel_user')
        reservation = self._make_reservation(checkin_offset=0,
                                             checkout_offset=1)
        reservation.action_confirm()
        self.env.invalidate_all()
        reservation.with_user(receptionist).action_checkin()
        self.assertEqual(self.room_101.hk_state, 'clean')
        self.assertFalse(self._inspections(self.room_101))


@tagged('post_install', '-at_install', 'aite_hotel')
class TestCheckoutLocalDay(HotelCommon):
    """Écart n° 37 (relecture) : le départ se juge sur le jour local.

    Fuseau très en avance sur l'UTC : un départ à 8 h locales tombe la
    veille en UTC. Comparé en UTC, un départ le jour prévu passait pour
    « anticipé » et la date de départ était recomposée la veille — une
    nuitée de moins facturée."""

    def setUp(self):
        super().setUp()
        self.env.user.tz = 'Asia/Tokyo'
        self.today = fields.Date.context_today(self.env.user)
        Res = self.env['aite.hotel.reservation']
        self.compose = Res._compose_datetime
        self.reservation = Res.create({
            'hotel_id': self.hotel.id,
            'partner_id': self.guest.id,
            'checkin_date': self.compose(self.today - timedelta(days=2),
                                         14.0),
            'checkout_date': self.compose(self.today, 12.0),
            'line_ids': [(0, 0, {
                'room_type_id': self.type_std.id,
                'room_id': self.room_101.id,
                'adults': 1,
            })],
        })
        self.reservation.action_confirm()
        self.reservation.action_checkin()

    def _wizard(self, when):
        return self.env['aite.hotel.checkout.wizard'].create({
            'reservation_id': self.reservation.id,
            'checkout_now': when,
            'create_invoice': False,
        })

    def test_morning_departure_on_the_planned_day_is_not_early(self):
        when = self.compose(self.today, 8.0)
        self.assertNotEqual(when.date(), self.today,
                            "Le jeu d'essai doit franchir minuit en UTC.")
        wizard = self._wizard(when)
        self.assertFalse(wizard.is_early)
        wizard.action_confirm()
        self.assertEqual(self.reservation.checkout_date,
                         self.compose(self.today, 12.0))
        self.assertEqual(self.reservation.nights, 2)

    def test_early_departure_is_set_on_the_local_day(self):
        yesterday = self.today - timedelta(days=1)
        wizard = self._wizard(self.compose(yesterday, 8.0))
        self.assertTrue(wizard.is_early)
        wizard.action_confirm()
        # Départ ramené à l'heure de départ de l'hôtel, le jour (local)
        # où le client est parti.
        self.assertEqual(self.reservation.checkout_date,
                         self.compose(yesterday, 12.0))


@tagged('post_install', '-at_install', 'aite_hotel')
class TestRoomBoardLocalDay(HotelCommon):
    """Écart n° 37 : le plan des chambres donne le jour de départ local
    (« jusqu'au … »), pas le jour UTC."""

    def test_until_is_the_local_departure_day(self):
        self.env.user.tz = 'Asia/Tokyo'
        today = fields.Date.context_today(self.env.user)
        Res = self.env['aite.hotel.reservation']
        departure_day = today + timedelta(days=1)
        reservation = Res.create({
            'hotel_id': self.hotel.id,
            'partner_id': self.guest.id,
            'checkin_date': Res._compose_datetime(
                today - timedelta(days=1), 14.0),
            # 8 h à Tokyo = 23 h UTC la veille.
            'checkout_date': Res._compose_datetime(departure_day, 8.0),
            'line_ids': [(0, 0, {
                'room_type_id': self.type_std.id,
                'room_id': self.room_101.id,
                'adults': 1,
            })],
        })
        reservation.action_confirm()
        reservation.action_checkin()
        self.assertNotEqual(reservation.checkout_date.date(), departure_day)
        board = self.env['aite.hotel.dashboard'].get_room_board(
            hotel_id=self.hotel.id)
        entry = next(r for r in board if r['name'] == '101')
        self.assertEqual(entry['until'], fields.Date.to_string(departure_day))


@tagged('post_install', '-at_install', 'aite_hotel')
class TestReconcileNeverBreaksTheInvoice(HotelCommon):
    """Écart n° 75 (relecture) : un lettrage qui échoue en base ne doit
    ni bloquer la facture du départ, ni laisser la transaction
    interrompue."""

    def test_failed_reconcile_is_rolled_back_and_logged(self):
        self.company.hotel_auto_entries = True
        self.company.hotel_payment_journal_id = self.env[
            'account.journal'].search([
                ('type', '=', 'cash'),
                ('company_id', '=', self.company.id)], limit=1)
        reservation = self._make_reservation(checkin_offset=0,
                                             checkout_offset=2)
        reservation.action_confirm()
        folio = reservation.folio_id
        payment = self.env['aite.hotel.folio.payment'].create({
            'folio_id': folio.id,
            'amount': 40000.0,
            'method': 'cash',
            'is_deposit': True,
        })
        self.assertTrue(payment.move_id)

        def failing_reconcile(lines):
            # Erreur SQL en plein lettrage : sans point de sauvegarde, la
            # transaction reste interrompue et la suite de la facturation
            # échoue (« current transaction is aborted »).
            lines.env.cr.execute("SELECT 1 / 0")

        AML = type(self.env['account.move.line'])
        with patch.object(AML, 'reconcile', failing_reconcile), \
                self.assertLogs('odoo.addons.aite_hotel_management.models'
                                '.hotel_folio', level='WARNING') as logs:
            folio.action_create_invoice()
        self.assertIn("Lettrage impossible", logs.output[0])
        self.assertTrue(folio.move_id)
        self.assertEqual(folio.move_id.state, 'posted')
        self.assertEqual(folio.state, 'invoiced')
        # La transaction est toujours utilisable.
        self.env.cr.execute("SELECT 1")
        self.assertEqual(folio.move_id.payment_state, 'not_paid')
