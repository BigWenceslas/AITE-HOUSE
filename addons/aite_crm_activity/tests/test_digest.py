# -*- coding: utf-8 -*-
""" Récapitulatif du matin.

Règles vérifiées ici :

- chacun reçoit ses activités ouvertes (en retard, du jour, à venir dans la
  fenêtre réglée), lues avec ses propres droits, dans son fuseau horaire ;
- les activités restées ouvertes sur une opportunité perdue (archivée) ne
  comptent pas : ni dans l'e-mail, ni pour choisir les destinataires ;
- chaque retard porte sa gravité (seuils partagés avec le tableau de bord),
  affichée en pastille « critique » / « élevé » ; l'objet ajoute le nombre
  de retards critiques, accordé en nombre ;
- « Montant en jeu » : revenu attendu des opportunités en retard que
  l'utilisateur peut lire, chacune une seule fois, par devise ;
- le bouton ouvre la liste « En retard » du tableau de bord quand il y a
  du retard (et seulement pour les utilisateurs du CRM) ;
- l'e-mail rendu ne contient jamais « False » ni « None ».
"""
import re
from datetime import datetime, timedelta
from unittest.mock import patch

import pytz

from odoo import Command, fields, tools
from odoo.tests import new_test_user, tagged

from ..models.crm_activity_params import PARAM_CRITICAL_DAYS, PARAM_HIGH_DAYS
from .common import AiteCrmActivityCase

NBSP = '\N{NO-BREAK SPACE}'


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
        self.assertEqual(values['subject'], "Vos activités CRM du jour : 3, dont 1 en retard")
        body = str(values['body_html'])
        self.assertIn("Opportunité Alice", body)
        self.assertIn("Rappeler le client", body)
        self.assertIn("/odoo/activites-en-retard", body)
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


@tagged('post_install', '-at_install', 'aite_crm_activity')
class TestCrmActivityDigestPriorities(AiteCrmActivityCase):
    """ Ce qui aide à prioriser : opportunités perdues écartées, gravité des
    retards, montant en jeu, lien direct vers la liste « En retard ». """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Digest = cls.env['aite.crm.activity.digest']
        cls.ICP = cls.env['ir.config_parameter'].sudo()
        cls.ICP.set_param('aite_crm_activity.digest_upcoming_days', 3)
        # Seuils par défaut, posés explicitement : 3 j élevé, 7 j critique.
        cls.ICP.set_param(PARAM_HIGH_DAYS, 3)
        cls.ICP.set_param(PARAM_CRITICAL_DAYS, 7)
        cls.base_url = cls.Digest.get_base_url()

    def _render(self, user):
        """ Récapitulatif réellement rendu : (données, objet, corps HTML). """
        digest = self.Digest._get_user_digest(user)
        values = self.Digest._prepare_mail_values(user, digest)
        return digest, values['subject'], str(values['body_html'])

    def _subject(self, user):
        return self._render(user)[1]

    def _lead(self, name, user, revenue=0.0, **values):
        return self.env['crm.lead'].create({
            'name': name, 'type': 'opportunity', 'user_id': user.id, 'team_id': self.team.id,
            'expected_revenue': revenue, **values,
        })

    def _clerk(self):
        """ Utilisateur interne sans droits sur le CRM. """
        return new_test_user(self.env, login='aite_cad_clerk2', groups='base.group_user',
                             name="Comptable", email='clerk2@aite.example', tz='UTC')

    # Opportunités perdues ----------------------------------------------

    def test_lost_opportunity_activities_are_left_out(self):
        # « Marquer comme perdue » archive l'opportunité mais laisse ses
        # activités ouvertes : elles ne sont plus à faire.
        self.lead_bob.action_set_lost()
        self.assertFalse(self.lead_bob.active)
        self.assertTrue(self.act_bob.exists() and self.act_bob.active, "Odoo laisse l'activité ouverte")

        recipients = self.Digest._get_recipients()
        self.assertNotIn(self.bob, recipients, "Sa seule activité est sur une opportunité perdue")
        self.assertIsNone(self.Digest._get_user_digest(self.bob))
        self.assertFalse(self.Digest._send_to_user(self.bob))
        self.assertIn(self.alice, recipients)
        digest = self.Digest._get_user_digest(self.alice)
        self.assertEqual(digest['counts'], {'overdue': 1, 'today': 1, 'upcoming': 0},
                         "« Aider Bob » était sur l'opportunité perdue")
        self.assertEqual([row['summary'] for rows in digest['sections'].values() for row in rows],
                         ["Rappeler le client", "Envoyer le devis"])

        self.lead_alice.action_set_lost()
        self.assertNotIn(self.alice, self.Digest._get_recipients())
        self.assertIsNone(self.Digest._get_user_digest(self.alice))

        # Opportunité restaurée : ses activités redeviennent à faire.
        self.lead_bob.action_unarchive()
        self.assertIn(self.bob, self.Digest._get_recipients())
        self.assertEqual(self.Digest._get_user_digest(self.bob)['counts'],
                         {'overdue': 0, 'today': 0, 'upcoming': 1})

    def test_cron_sends_nothing_for_lost_opportunities_only(self):
        """ Seuls les utilisateurs du jeu d'essai sont vérifiés : la tâche
        écrit aussi aux autres utilisateurs de la base qui ont des activités
        (données de démonstration, base du client), et le nombre total
        d'e-mails dépend donc de la base et du jour. """
        (self.lead_alice | self.lead_bob).action_set_lost()
        fixture_users = self.alice | self.bob | self.manager
        self.assertFalse(self.Digest._get_recipients() & fixture_users)
        before = self.env['mail.mail'].sudo().search([('email_to', 'ilike', '@aite.example')])
        self.Digest._cron_send_daily_digest()
        after = self.env['mail.mail'].sudo().search([('email_to', 'ilike', '@aite.example')])
        self.assertEqual(after, before)
        self.assertFalse(any(fixture_users.mapped('aite_crm_digest_last_sent')),
                         "Aucun récapitulatif traité pour eux")

    # Gravité des retards -----------------------------------------------

    def test_severity_of_each_overdue_row(self):
        for days in (-1, -3, -7, -10):
            self._activity(self.lead_alice, self.alice, days, self.type_call, "Retard %s j" % -days)
        digest = self.Digest._get_user_digest(self.alice)
        # Le plus ancien retard en premier.
        self.assertEqual(
            [(row['summary'], row['late_days'], row['severity']) for row in digest['sections']['overdue']],
            [("Retard 10 j", 10, 'critical'),
             ("Retard 7 j", 7, 'critical'),
             ("Retard 3 j", 3, 'high'),
             ("Rappeler le client", 2, 'low'),
             ("Retard 1 j", 1, 'low')])
        self.assertEqual(
            [(row['late_days'], row['severity'])
             for row in digest['sections']['today'] + digest['sections']['upcoming']],
            [(0, False), (0, False)])
        self.assertEqual(digest['critical_count'], 2)
        self.assertEqual(digest['critical_label'], "2 critiques")

    def test_severity_follows_the_settings(self):
        self.ICP.set_param(PARAM_HIGH_DAYS, 1)
        self.ICP.set_param(PARAM_CRITICAL_DAYS, 2)
        self._activity(self.lead_alice, self.alice, -1, self.type_call, "Retard 1 j")
        digest = self.Digest._get_user_digest(self.alice)
        self.assertEqual([(row['late_days'], row['severity']) for row in digest['sections']['overdue']],
                         [(2, 'critical'), (1, 'high')])
        self.assertEqual(digest['critical_count'], 1)
        self.assertEqual(digest['critical_label'], "1 critique")

    def test_severity_badges_in_the_email(self):
        for days in (-3, -7, -10):
            self._activity(self.lead_alice, self.alice, days, self.type_call, "Retard %s j" % -days)
        digest, subject, body = self._render(self.alice)
        self.assertEqual(len(re.findall(r'>critique</span>', body)), 2)
        self.assertEqual(len(re.findall(r'>élevé</span>', body)), 1)
        # Pastille à côté de la ligne « N j de retard » : rouge pour
        # critique, orange pour élevé, rien pour un retard léger.
        self.assertRegex(body, r'10 j de retard\s*<span [^>]*background-color: #D92D20;[^>]*>critique</span>')
        self.assertRegex(body, r'7 j de retard\s*<span [^>]*background-color: #D92D20;[^>]*>critique</span>')
        self.assertRegex(body, r'3 j de retard\s*<span [^>]*background-color: #FEF0C7;[^>]*>élevé</span>')
        self.assertRegex(body, r'2 j de retard\s*</div>')
        self.assertIn("en retard</strong> (dont 2 critiques),", body)

    def test_subject_counts_critical_delays_with_plural(self):
        self.assertEqual(self._subject(self.bob), "Vos activités CRM du jour : 1")
        self.assertEqual(self._subject(self.alice), "Vos activités CRM du jour : 3, dont 1 en retard")
        self._activity(self.lead_alice, self.alice, -8, self.type_call, "Critique 1")
        digest, subject, body = self._render(self.alice)
        self.assertEqual(subject, "Vos activités CRM du jour : 4, dont 2 en retard (1 critique)")
        self.assertIn("en retard</strong> (dont 1 critique),", body)
        self._activity(self.lead_alice, self.alice, -15, self.type_call, "Critique 2")
        self.assertEqual(self._subject(self.alice),
                         "Vos activités CRM du jour : 5, dont 3 en retard (2 critiques)")

    def test_counts_and_amount_cover_rows_beyond_the_display_limit(self):
        lead_extra = self._lead("Opportunité ancienne", self.alice, 400000)
        for days in (-20, -15, -9):
            self._activity(lead_extra, self.alice, days, self.type_call, "Ancien retard %s j" % -days)
        with patch('odoo.addons.aite_crm_activity.models.crm_activity_digest.MAX_ROWS_PER_SECTION', 2):
            digest, subject, body = self._render(self.alice)
        self.assertEqual([row['late_days'] for row in digest['sections']['overdue']], [20, 15])
        self.assertEqual(digest['counts']['overdue'], 4)
        self.assertEqual(digest['critical_count'], 3)
        self.assertEqual(subject, "Vos activités CRM du jour : 6, dont 4 en retard (3 critiques)")
        # L'opportunité d'Alice (ligne coupée à l'affichage) reste dans le montant.
        self.assertEqual([amount['amount'] for amount in digest['overdue_amounts']], [1900000.0])
        self.assertIn("… et 2 autre(s) : voir le tableau de bord.", re.sub(r'\s+', ' ', body))

    # Montant en jeu ------------------------------------------------------

    def test_amount_at_stake_counts_each_readable_opportunity_once(self):
        currency = self.lead_alice.company_currency
        # Deuxième retard sur la même opportunité : comptée une seule fois.
        self._activity(self.lead_alice, self.alice, -5, self.type_todo, "Relancer encore")
        # Retard sur l'opportunité de Bob, qu'Alice ne peut pas lire : son
        # montant n'est pas dévoilé.
        self._activity(self.lead_bob, self.alice, -1, self.type_todo, "Aider Bob, en retard")
        # Opportunité sans montant : rien à ajouter.
        self._activity(self.lead_quiet, self.alice, -1, self.type_todo, "Relancer")
        # Activité du jour (pas en retard) : hors du montant en jeu.
        self._activity(self._lead("Opportunité du jour", self.alice, 999000), self.alice, 0,
                       self.type_todo, "Appeler aujourd'hui")

        digest, subject, body = self._render(self.alice)
        self.assertEqual(digest['counts']['overdue'], 4)
        label = tools.format_amount(digest['lang_env'], 1500000, currency)
        self.assertEqual(digest['overdue_amounts'],
                         [{'currency_id': currency.id, 'amount': 1500000.0, 'label': label}])
        self.assertIn("Montant en jeu : %s</strong>" % label, body)

        # Le responsable lit toutes les opportunités : les deux montants,
        # chaque opportunité une fois malgré deux retards sur celle de Bob.
        for lead, days in ((self.lead_alice, -1), (self.lead_bob, -2), (self.lead_bob, -3)):
            self._activity(lead, self.manager, days, self.type_call, "Suivi responsable")
        digest = self.Digest._get_user_digest(self.manager)
        self.assertEqual([(amount['currency_id'], amount['amount']) for amount in digest['overdue_amounts']],
                         [(currency.id, 2300000.0)])

    def test_amount_at_stake_per_currency_in_the_user_language(self):
        self.env['res.lang']._activate_lang('fr_FR')
        self.alice.lang = 'fr_FR'
        xaf = self.env.ref('base.XAF')
        main_currency = self.alice.company_id.currency_id
        other_currency = xaf if main_currency != xaf else self.env.ref('base.EUR')
        other_currency.active = True
        company_2 = self.env['res.company'].create({
            'name': "AITE Filiale (test)", 'currency_id': other_currency.id})
        self.alice.company_ids = [Command.link(company_2.id)]
        lead_2 = self._lead("Opportunité filiale", self.alice, 1500000, company_id=company_2.id)
        self.assertEqual(lead_2.company_id, company_2)
        self._activity(lead_2, self.alice, -4, self.type_call, "Relancer la filiale")

        digest, subject, body = self._render(self.alice)
        amounts = digest['overdue_amounts']
        # Une ligne par devise, celle de la société de l'utilisateur en premier.
        self.assertEqual([(amount['currency_id'], amount['amount']) for amount in amounts],
                         [(main_currency.id, 1500000.0), (other_currency.id, 1500000.0)])
        labels = {amount['currency_id']: amount['label'] for amount in amounts}
        # Mise en forme française : espaces insécables, symbole après.
        self.assertEqual(labels[xaf.id], "1{0}500{0}000{0}FCFA".format(NBSP))
        self.assertIn("Montant en jeu : %s · %s</strong>" % (amounts[0]['label'], amounts[1]['label']), body)

        # Sans accès à la filiale, l'opportunité devient illisible : son
        # montant disparaît, l'activité reste (sans lien ni détails).
        self.alice.company_ids = [Command.unlink(company_2.id)]
        digest = self.Digest._get_user_digest(self.alice)
        self.assertEqual([(amount['currency_id'], amount['amount']) for amount in digest['overdue_amounts']],
                         [(main_currency.id, 1500000.0)])
        row = next(row for row in digest['sections']['overdue'] if row['summary'] == "Relancer la filiale")
        self.assertEqual((row['lead_name'], row['url'], row['revenue']), ("Opportunité filiale", False, ''))

    def test_amount_line_is_omitted_without_money_at_stake(self):
        # Bob : rien en retard.
        digest, subject, body = self._render(self.bob)
        self.assertEqual(digest['overdue_amounts'], [])
        self.assertNotIn("Montant en jeu", body)
        # Alice : en retard, mais sur une opportunité sans montant.
        self.lead_alice.expected_revenue = 0
        digest, subject, body = self._render(self.alice)
        self.assertEqual(digest['counts']['overdue'], 1)
        self.assertEqual(digest['overdue_amounts'], [])
        self.assertNotIn("Montant en jeu", body)

    # Lien vers le tableau de bord ----------------------------------------

    def test_dashboard_button_opens_the_overdue_list(self):
        digest, subject, body = self._render(self.alice)
        self.assertEqual(digest['dashboard_url'], self.base_url + '/odoo/activites-en-retard')
        self.assertIn('href="%s/odoo/activites-en-retard"' % self.base_url, body)
        self.assertNotIn('/odoo/suivi-activites', body)

        digest, subject, body = self._render(self.bob)
        self.assertEqual(digest['dashboard_url'], self.base_url + '/odoo/suivi-activites')
        self.assertIn('href="%s/odoo/suivi-activites"' % self.base_url, body)
        self.assertNotIn('activites-en-retard', body)

        # Retard traité : retour au tableau de bord général.
        self.act_overdue.action_feedback(feedback="Client rappelé")
        digest = self.Digest._get_user_digest(self.alice)
        self.assertEqual(digest['counts']['overdue'], 0)
        self.assertEqual(digest['dashboard_url'], self.base_url + '/odoo/suivi-activites')

    def test_no_dashboard_nor_amount_for_non_crm_user_even_when_late(self):
        clerk = self._clerk()
        self._activity(self.lead_alice, clerk, -9, self.type_todo, "Facture en retard")
        digest, subject, body = self._render(clerk)
        self.assertEqual(digest['counts'], {'overdue': 1, 'today': 0, 'upcoming': 0})
        self.assertFalse(digest['can_open_dashboard'])
        self.assertEqual(digest['dashboard_url'], self.base_url + '/odoo/suivi-activites')
        self.assertNotIn('/odoo/activites-en-retard', body)
        self.assertNotIn('/odoo/suivi-activites', body)
        self.assertEqual(digest['overdue_amounts'], [], "Il ne peut pas lire l'opportunité")
        self.assertNotIn("Montant en jeu", body)
        self.assertEqual(subject, "Vos activités CRM du jour : 1, dont 1 en retard (1 critique)")

    # Rendu ---------------------------------------------------------------

    def test_rendered_email_never_shows_false_or_none(self):
        # Valeurs vides partout : opportunité sans client, sans étape ni
        # montant ; activité sans type ni résumé ; activité sur une
        # opportunité illisible ; utilisateur sans droits sur le CRM.
        dora = new_test_user(
            self.env, login='aite_cad_dora', groups='sales_team.group_sale_salesman',
            name="Dora Commerciale", email='dora@aite.example', tz='UTC')
        bare = self.env['crm.lead'].create({'name': "Opportunité nue", 'type': 'opportunity',
                                            'user_id': dora.id})
        bare.write({'stage_id': False, 'partner_id': False, 'expected_revenue': 0})
        self.env['mail.activity'].create({
            'res_model_id': self.env['ir.model']._get_id('crm.lead'),
            'res_id': bare.id,
            'user_id': dora.id,
            'activity_type_id': False,
            'date_deadline': self.today - timedelta(days=8),
        })
        self._activity(self.lead_bob, dora, 0, self.type_todo, False)
        self._activity(bare, dora, 2, self.type_call, False)
        clerk = self._clerk()
        self._activity(self.lead_alice, clerk, -4, self.type_todo, False)

        digest = self.Digest._get_user_digest(dora)
        overdue = digest['sections']['overdue'][0]
        self.assertEqual(
            {key: overdue[key] for key in ('type', 'summary', 'partner', 'stage', 'revenue', 'severity')},
            {'type': '', 'summary': '', 'partner': '', 'stage': '', 'revenue': '', 'severity': 'critical'})
        today = digest['sections']['today'][0]
        self.assertEqual((today['lead_name'], today['partner'], today['stage'], today['url']),
                         ("Opportunité Bob", '', '', False))

        for user in (dora, clerk, self.alice, self.bob):
            with self.subTest(user=user.login):
                digest, subject, body = self._render(user)
                self.assertEqual(re.findall(r'\b(?:False|None)\b', subject + body), [])

    def test_digest_counts_match_the_dashboard(self):
        # Mêmes « en retard » et « aujourd'hui » que le tableau de bord
        # d'Alice (le tableau de bord a sa propre fenêtre « à venir »).
        self._activity(self.lead_alice, self.alice, -9, self.type_call, "Très en retard")
        digest = self.Digest._get_user_digest(self.alice)
        kpis = self.dashboard(self.alice, team_id=False)['kpis']
        self.assertEqual(digest['counts'], {'overdue': 2, 'today': 1, 'upcoming': 1})
        self.assertEqual((kpis['overdue'], kpis['today']), (2, 1))
