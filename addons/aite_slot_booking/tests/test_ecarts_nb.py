# -*- coding: utf-8 -*-
"""Écarts non bloquants relevés par les vidéos (docs/videos/ECARTS.md).

Chaque test reproduit le constat d'origine : il échouait avant la
correction.
"""
from unittest.mock import patch

from odoo.exceptions import ValidationError
from odoo.tests import tagged

from .common import SlotCommon


@tagged('post_install', '-at_install', 'aite_slot')
class TestSlotEcartsNonBloquants(SlotCommon):

    # ------------------------------------------------------------------
    # Écart n° 42 : pas d'anglais résiduel (« No-show »)
    # ------------------------------------------------------------------

    def test_no_show_state_is_labelled_in_french(self):
        """L'état « no_show » s'affiche « Non présenté » (liste, badge,
        espace client du site), pas « No-show »."""
        labels = dict(
            self.env['aite.slot.booking']._fields['state'].selection)
        self.assertEqual(labels['no_show'], "Non présenté")

    # ------------------------------------------------------------------
    # Écart n° 43 : message de création du fil de discussion
    # ------------------------------------------------------------------

    def test_creation_message_is_french(self):
        """Le fil dit « Réservation créée », pas « Réservation de créneau
        (espace / prestation) créé » (ni « … created »)."""
        booking = self._booking()
        bodies = ' '.join(str(m.body) for m in booking.message_ids)
        self.assertIn("Réservation créée", bodies)
        self.assertNotIn("created", bodies)
        self.assertNotIn("(espace / prestation)", bodies)

    # ------------------------------------------------------------------
    # Écart n° 44 : accord du message de conflit
    # ------------------------------------------------------------------

    def test_conflict_message_does_not_assume_a_feminine_resource(self):
        """« Conflit : « Salon VIP » est complète » supposait une ressource
        féminine : le message parle désormais de la place restante."""
        self._booking(start_h=10.0, stop_h=12.0).action_confirm()
        clash = self._booking(start_h=11.0, stop_h=13.0,
                              partner=self.client_2)
        with self.assertRaisesRegex(
                ValidationError,
                "Plus de place sur « Salon VIP » pour ce créneau"):
            clash.action_confirm()

    # ------------------------------------------------------------------
    # Écart n° 49 : l'e-mail de confirmation part tout de suite
    # ------------------------------------------------------------------

    def _outgoing_mails(self, booking):
        return self.env['mail.mail'].sudo().search([
            ('model', '=', 'aite.slot.booking'),
            ('res_id', '=', booking.id),
            ('state', '=', 'outgoing'),
        ])

    def test_confirmation_mail_is_sent_at_once(self):
        """Le guide promet l'e-mail « dès le clic sur Confirmer » : il ne
        doit pas attendre la tâche horaire d'envoi des e-mails."""
        self.company.aite_slot_mail_on_confirm = True
        booking = self._booking()
        booking.action_confirm()
        self.assertFalse(
            self._outgoing_mails(booking),
            "la confirmation ne doit pas rester en file d'attente")

    def test_resent_mail_is_sent_at_once(self):
        """« Renvoyer l'e-mail » envoie, lui aussi, immédiatement."""
        self.company.aite_slot_mail_on_confirm = False
        booking = self._booking()
        booking.action_confirm()
        booking.action_send_confirmation()
        self.assertFalse(self._outgoing_mails(booking))

    # Envoi immédiat, mais APRÈS la validation de la transaction (comme les
    # notifications du standard, ``send_after_commit``) : envoyé pendant la
    # transaction, l'e-mail gardait le verrou de la ressource posé par
    # ``_check_no_conflict`` pendant tout l'échange SMTP (jusqu'à 60 s si le
    # serveur ne répond pas), et partait même si la confirmation échouait
    # ensuite. En test, ``send_after_commit`` envoie aussitôt : on le
    # remplace donc pour vérifier que rien ne part avant.

    def _patch_send_after_commit(self):
        return patch.object(
            type(self.env['mail.mail']), 'send_after_commit', autospec=True)

    def test_confirmation_mail_waits_for_the_commit(self):
        self.company.aite_slot_mail_on_confirm = True
        booking = self._booking()
        with self._patch_send_after_commit() as after_commit:
            booking.action_confirm()
        after_commit.assert_called_once()
        mail = after_commit.call_args.args[0]
        self.assertEqual(mail.res_id, booking.id)
        self.assertEqual(
            mail.state, 'outgoing',
            "rien ne doit partir avant la fin de la transaction")

    def test_resent_mail_waits_for_the_commit(self):
        self.company.aite_slot_mail_on_confirm = False
        booking = self._booking()
        booking.action_confirm()
        with self._patch_send_after_commit() as after_commit:
            booking.action_send_confirmation()
        after_commit.assert_called_once()
        self.assertEqual(after_commit.call_args.args[0].state, 'outgoing')

    # ------------------------------------------------------------------
    # Règle 6 : la colonne Date du journal porte l'année
    # ------------------------------------------------------------------

    def test_journal_date_shows_the_year(self):
        """« Cette semaine » à cheval sur le 1er janvier : sans l'année, le
        31/12 et le 02/01 se lisaient mal (« %d/%m %H:%M »)."""
        booking = self._booking(days=1, start_h=10.0, stop_h=11.0)
        day = booking.start.date()
        rows = self.env['aite.slot.dashboard'].get_bookings(
            str(day), str(day))
        row = next(r for r in rows if r['id'] == booking.id)
        self.assertEqual(row['date'], booking.start.strftime('%d/%m/%Y %H:%M'))

    # ------------------------------------------------------------------
    # Écart n° 60 : rien reporté au folio → on le dit
    # ------------------------------------------------------------------

    def test_done_without_folio_says_nothing_was_posted(self):
        """Client de passage (aucun folio ouvert) : la prestation se
        clôture et le fil dit pourquoi rien n'a été reporté."""
        self.company.aite_slot_auto_post_folio = True
        booking = self._booking(resource=self.cabine, start_h=10.0,
                                stop_h=11.0, service_id=self.service_spa.id,
                                partner=self.client_2)
        booking.action_confirm()
        booking.action_done()
        self.assertEqual(booking.state, 'done')
        self.assertFalse(booking.posted_line_id)
        bodies = ' '.join(str(m.body) for m in booking.message_ids)
        self.assertIn("Rien reporté au folio", bodies)

    def test_post_button_hidden_for_a_walk_in_client(self):
        """« Reporter au folio » n'est pas proposé sans folio possible."""
        booking = self._booking(resource=self.cabine, start_h=10.0,
                                stop_h=11.0, service_id=self.service_spa.id,
                                partner=self.client_2)
        self.assertFalse(booking.can_post_to_folio)

    # ------------------------------------------------------------------
    # Écart n° 61 : numérotation propre aux créneaux, annuelle
    # ------------------------------------------------------------------

    def test_slot_reference_is_not_confused_with_a_stay(self):
        """Une réservation de créneau ne porte plus le préfixe « RES/ » des
        séjours hôteliers."""
        booking = self._booking()
        self.assertFalse(booking.name.startswith('RES/'), booking.name)

    def test_slot_numbering_restarts_each_year(self):
        """La numérotation des créneaux repart à 1 chaque année (plages de
        dates annuelles), comme celle des séjours."""
        seq = self.env.ref('aite_slot_booking.seq_aite_slot_booking')
        self.assertTrue(seq.use_date_range)
        first = seq.with_context(
            ir_sequence_date='2031-03-01').next_by_id()
        self.assertTrue(first.endswith('/2031/0001'), first)
