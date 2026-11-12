# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from unittest.mock import patch

import pytz

from odoo import fields
from odoo.tests import new_test_user, tagged

from .common import AiteCrmActivityCase


def _fake_send_ok(self, **kwargs):
    """ Remplace l'envoi SMTP (désactivé pendant les tests) : réussi. """
    self.write({'state': 'sent'})


@tagged('post_install', '-at_install', 'aite_crm_activity')
class TestCrmActivityDigest(AiteCrmActivityCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Digest = cls.env['aite.crm.activity.digest']
        cls.env['ir.config_parameter'].sudo().set_param('aite_crm_activity.digest_upcoming_days', 3)

    def _our_mails(self):
        return self.env['mail.mail'].sudo().search([
            ('email_to', 'ilike', '@aite.example'),
        ])

    # Destinataires -----------------------------------------------------

    def test_recipients(self):
        recipients = self.Digest._get_recipients()
        self.assertIn(self.alice, recipients)
        self.assertIn(self.bob, recipients)
        self.assertNotIn(self.manager, recipients, "Pas d'activité : pas d'e-mail")

    def test_unsubscribed_user_is_skipped(self):
        self.alice.with_user(self.alice).write({'aite_crm_digest_subscribed': False})
        self.assertNotIn(self.alice, self.Digest._get_recipients())

    def test_user_without_email_is_skipped(self):
        self.bob.email = False
        self.assertNotIn(self.bob, self.Digest._get_recipients())

    def test_recipient_skipped_only_for_its_own_day(self):
        # Le « déjà envoyé » suit la journée de l'utilisateur, pas la date UTC.
        self.alice.tz = 'Pacific/Kiritimati'  # UTC+14
        local_today = self.Digest._user_today(self.alice)
        self.alice.aite_crm_digest_last_sent = local_today - timedelta(days=1)
        self.assertIn(self.alice, self.Digest._get_recipients())
        self.alice.aite_crm_digest_last_sent = local_today
        self.assertNotIn(self.alice, self.Digest._get_recipients())

    def test_non_crm_user_gets_digest_without_dashboard(self):
        # Une activité confiée à une personne sans droits sur le CRM : elle
        # la reçoit (Odoo la lui montre), sans lien qu'elle ne pourrait pas
        # ouvrir.
        clerk = new_test_user(self.env, login='aite_cad_clerk', groups='base.group_user',
                              name="Comptable", email='clerk@aite.example', tz='UTC')
        self._activity(self.lead_alice, clerk, 0, self.type_todo, "Vérifier la facture")
        self.assertIn(clerk, self.Digest._get_recipients())
        digest = self.Digest._get_user_digest(clerk)
        self.assertFalse(digest['can_open_dashboard'])
        row = digest['sections']['today'][0]
        self.assertEqual(row['lead_name'], "Opportunité Alice")
        self.assertFalse(row['url'])
        body = str(self.Digest._prepare_mail_values(clerk, digest)['body_html'])
        self.assertIn("Vérifier la facture", body)
        self.assertNotIn("/odoo/suivi-activites", body)
        self.assertNotIn("/mail/view", body)
        self.assertTrue(self.Digest._get_user_digest(self.alice)['can_open_dashboard'])

    # Contenu -----------------------------------------------------------

    def test_content_of_alice(self):
        digest = self.Digest._get_user_digest(self.alice)
        self.assertEqual(digest['counts'], {'overdue': 1, 'today': 1, 'upcoming': 1})
        overdue = digest['sections']['overdue'][0]
        self.assertEqual(overdue['lead_name'], "Opportunité Alice")
        self.assertEqual(overdue['late_days'], 2)
        self.assertEqual(overdue['partner'], "Client Test")
        self.assertIn('/mail/view?model=crm.lead&res_id=%s' % self.lead_alice.id, overdue['url'])
        upcoming = digest['sections']['upcoming'][0]
        self.assertEqual(upcoming['lead_name'], "Opportunité Bob",
                         "Activité visible même sur une opportunité qu'elle ne peut pas ouvrir")
        self.assertFalse(upcoming['partner'], "…mais sans ses détails")

    def test_far_activities_are_left_out(self):
        summaries = [row['summary'] for rows in self.Digest._get_user_digest(self.alice)['sections'].values()
                     for row in rows]
        self.assertNotIn("Point trimestriel", summaries, "J+30 au-delà de la fenêtre de 3 jours")

    def test_upcoming_window_is_configurable(self):
        self.env['ir.config_parameter'].sudo().set_param('aite_crm_activity.digest_upcoming_days', 0)
        digest = self.Digest._get_user_digest(self.alice)
        self.assertEqual(digest['counts'], {'overdue': 1, 'today': 1, 'upcoming': 0})

    def test_nothing_to_send(self):
        self.assertIsNone(self.Digest._get_user_digest(self.manager))
        self.assertFalse(self.Digest._send_to_user(self.manager))

    def test_today_follows_user_timezone(self):
        # À 23 h 30 UTC, il est déjà le lendemain à Douala (UTC+1) : l'activité
        # « du jour » en UTC y est en retard, et celle de demain devient celle
        # du jour.
        self.alice.tz = 'Africa/Douala'
        late_evening = datetime.combine(self.today, datetime.min.time()) + timedelta(hours=23, minutes=30)
        digest = self.Digest._get_user_digest(self.alice, now=late_evening)
        self.assertEqual(digest['counts']['overdue'], 2)
        self.assertEqual(digest['counts']['today'], 1)
        self.assertEqual(digest['sections']['today'][0]['summary'], "Aider Bob")

    def test_mail_values(self):
        digest = self.Digest._get_user_digest(self.alice)
        values = self.Digest._prepare_mail_values(self.alice, digest)
        self.assertEqual(values['email_to'], self.alice.email_formatted)
        self.assertIn("1 en retard", values['subject'])
        body = str(values['body_html'])
        self.assertIn("Opportunité Alice", body)
        self.assertIn("Rappeler le client", body)
        self.assertIn("/odoo/suivi-activites", body)
        self.assertNotIn("Point trimestriel", body)

    # Envoi -------------------------------------------------------------

    def test_cron_queues_one_mail_per_recipient(self):
        before = self._our_mails()
        self.Digest._cron_send_daily_digest()
        mails = self._our_mails() - before
        self.assertEqual(sorted(mails.mapped('email_to')),
                         sorted([self.alice.email_formatted, self.bob.email_formatted]))
        self.assertTrue(all(m.state == 'outgoing' for m in mails))
        bob_mail = mails.filtered(lambda m: m.email_to == self.bob.email_formatted)
        self.assertIn("Opportunité Bob", bob_mail.body_html)
        self.assertNotIn("Opportunité Alice", bob_mail.body_html, "Chacun ne reçoit que ses activités")

    def test_cron_does_not_send_twice_the_same_day(self):
        # Odoo peut relancer une tâche planifiée interrompue : pas de doublon.
        self.Digest._cron_send_daily_digest()
        before = self._our_mails()
        self.assertEqual(self.Digest._cron_send_daily_digest(), 0)
        self.assertEqual(self._our_mails(), before)
        self.assertEqual(self.alice.aite_crm_digest_last_sent, self.Digest._user_today(self.alice))
        # Le bouton « M'envoyer mon récapitulatif » reste disponible.
        with patch.object(type(self.env['mail.mail']), '_send', _fake_send_ok):
            action = self.Digest.with_user(self.alice).action_send_my_digest()
        self.assertEqual(action['params']['type'], 'success')

    def test_cron_wakes_up_the_mail_queue(self):
        # La file d'attente des e-mails ne passe qu'une fois par heure : la
        # tâche la réveille pour un envoi dans les minutes qui suivent.
        queue = self.env.ref('mail.ir_cron_mail_scheduler_action')
        with patch.object(type(self.env['ir.cron']), '_trigger', autospec=True) as trigger:
            self.Digest._cron_send_daily_digest()
        self.assertIn(queue, [call.args[0] for call in trigger.call_args_list])

    def test_cron_record_points_to_digest(self):
        cron = self.env.ref('aite_crm_activity.ir_cron_crm_activity_digest')
        self.assertEqual(cron.model_id.model, 'aite.crm.activity.digest')
        self.assertEqual(cron.interval_type, 'days')
        self.assertEqual(cron.interval_number, 1)

    def test_send_my_digest_button(self):
        with patch.object(type(self.env['mail.mail']), '_send', _fake_send_ok):
            action = self.Digest.with_user(self.alice).action_send_my_digest()
        self.assertEqual(action['params']['type'], 'success')
        self.assertIn(self.alice.email, action['params']['message'])
        action = self.Digest.with_user(self.manager).action_send_my_digest()
        self.assertEqual(action['params']['type'], 'info')
        self.bob.email = False
        action = self.Digest.with_user(self.bob).action_send_my_digest()
        self.assertEqual(action['params']['type'], 'warning')

    def test_send_my_digest_reports_a_failed_send(self):
        # Pas de serveur de messagerie joignable : le bouton doit le dire,
        # pas annoncer un envoi réussi.
        MailServer = type(self.env['ir.mail_server'])
        with patch.object(MailServer, '_connect__', side_effect=ConnectionRefusedError("Connection refused")):
            action = self.Digest.with_user(self.alice).action_send_my_digest()
        self.assertEqual(action['params']['type'], 'danger')
        self.assertIn("Connection refused", action['params']['message'])
        self.assertIn("Serveurs de messagerie sortants", action['params']['message'])
        mail = self._our_mails().filtered(lambda m: m.email_to == self.alice.email_formatted)
        self.assertEqual(mail.state, 'exception')

    # Réglages ----------------------------------------------------------

    def test_settings_drive_the_cron(self):
        cron = self.env.ref('aite_crm_activity.ir_cron_crm_activity_digest')
        admin = self.env.ref('base.user_admin')
        admin.tz = 'Africa/Douala'
        Settings = self.env['res.config.settings'].with_user(admin)
        Settings.create({
            'aite_crm_digest_active': True,
            'aite_crm_digest_hour': 7.5,
            'aite_crm_digest_upcoming_days': 5,
        }).execute()
        self.assertTrue(cron.active)
        local = pytz.utc.localize(cron.nextcall).astimezone(pytz.timezone('Africa/Douala'))
        self.assertEqual((local.hour, local.minute), (7, 30))
        self.assertGreater(cron.nextcall, fields.Datetime.now())
        self.assertEqual(self.Digest._get_upcoming_days(), 5)
        values = Settings.default_get(['aite_crm_digest_active', 'aite_crm_digest_hour'])
        self.assertTrue(values['aite_crm_digest_active'])
        self.assertAlmostEqual(values['aite_crm_digest_hour'], 7.5)

        Settings.create({'aite_crm_digest_active': False, 'aite_crm_digest_hour': 7.5}).execute()
        self.assertFalse(cron.active)

    def test_settings_timezone(self):
        cron = self.env.ref('aite_crm_activity.ir_cron_crm_activity_digest')
        Settings = self.env['res.config.settings'].with_user(self.env.ref('base.user_admin'))
        Settings.create({
            'aite_crm_digest_active': True,
            'aite_crm_digest_hour': 6.0,
            'aite_crm_digest_tz': 'Asia/Tokyo',
        }).execute()
        self.assertEqual(self.Digest._get_tz_name(), 'Asia/Tokyo')
        local = pytz.utc.localize(cron.nextcall).astimezone(pytz.timezone('Asia/Tokyo'))
        self.assertEqual((local.hour, local.minute), (6, 0))

    def test_daily_reschedule_keeps_the_local_hour(self):
        # Odoo avance une tâche quotidienne dans le fuseau de son utilisateur
        # (Europe/Brussels pour l'utilisateur système) : sans correction, le
        # récapitulatif de 7 h à Douala partirait à 6 h l'été, ou à 8 h l'hiver.
        cron = self.env.ref('aite_crm_activity.ir_cron_crm_activity_digest')
        self.env.user.tz = 'Europe/Brussels'
        self.env['ir.config_parameter'].sudo().set_param('aite_crm_activity.digest_tz', 'Africa/Douala')
        # Point de départ six mois plus tôt, à 7 h à Douala (6 h UTC) : de
        # l'autre côté d'un changement d'heure européen.
        start = datetime.combine(fields.Date.today() - timedelta(days=182), datetime.min.time())
        start += timedelta(hours=6)
        self.env['ir.cron']._reschedule_later({
            'id': cron.id, 'nextcall': start, 'interval_type': 'days', 'interval_number': 1,
        })
        cron.invalidate_recordset(['nextcall'])
        local = pytz.utc.localize(cron.nextcall).astimezone(pytz.timezone('Africa/Douala'))
        self.assertEqual((local.hour, local.minute), (7, 0))
        self.assertGreater(cron.nextcall, fields.Datetime.now())

    def test_subscription_is_a_self_writeable_preference(self):
        self.bob.with_user(self.bob).write({'aite_crm_digest_subscribed': False})
        self.assertFalse(self.bob.aite_crm_digest_subscribed)
