# -*- coding: utf-8 -*-
from datetime import timedelta
from unittest.mock import patch

from markupsafe import Markup

from odoo import fields
from odoo.tests import new_test_user, tagged
from odoo.tools import mute_logger

from odoo.addons.aite_website_livechat.models.discuss_channel import (
    EMAIL_GROUPING_DELAY,
    EMAIL_MIN_INTERVAL,
)

from .common import AiteLivechatCommon

VISITOR_EMAIL = 'jean.dupont@exemple.cm'


@tagged('post_install', '-at_install', 'aite_website_livechat')
class TestLivechatVisitorContact(AiteLivechatCommon):
    """ E-mail et téléphone écrits par le visiteur. """

    def test_find_emails_and_phones_in_text(self):
        Channel = self.env['discuss.channel']
        self.assertEqual(
            Channel._aite_find_emails("Écrivez-moi : Jean.Dupont@Exemple.CM. Ou (bis@exemple.cm) merci"),
            ['jean.dupont@exemple.cm', 'bis@exemple.cm'],
        )
        self.assertEqual(Channel._aite_find_emails("mailto:x@y.cm, pas une adresse : a@b, @test"), ['x@y.cm'])
        self.assertEqual(
            Channel._aite_find_phones("Mon numéro : +237 6 99 11 22 33, ou le 699-11-22-33."),
            ['+237 6 99 11 22 33', '699-11-22-33'],
        )
        self.assertEqual(Channel._aite_find_phones("Commande 1234, le 13/11/2026, mail a1234567890@x.cm"), [])

    def test_contact_detected_in_visitor_messages_only(self):
        channel = self._start_session()
        self._visitor_post(channel, "Bonjour")
        self.assertFalse(channel.aite_visitor_email)
        self._visitor_post(channel, f"Mon e-mail : {VISITOR_EMAIL.upper()} et mon téléphone +237 699 11 22 33")
        self.assertEqual(channel.aite_visitor_email, VISITOR_EMAIL)
        self.assertEqual(channel.aite_visitor_phone, '+237 699 11 22 33')
        # La plus récente l'emporte (correction de saisie).
        self._visitor_post(channel, "Pardon, plutôt jean@exemple.cm")
        self.assertEqual(channel.aite_visitor_email, 'jean@exemple.cm')
        # Une adresse écrite par l'opératrice n'est jamais retenue.
        self._operator_post(channel, "Écrivez aussi à commercial@aite.example.com")
        self.assertEqual(channel.aite_visitor_email, 'jean@exemple.cm')

    def test_email_of_logged_in_visitor(self):
        portal = new_test_user(self.env, login='aite_lc_client', name="Client Portail",
                               email='client@exemple.cm', groups='base.group_portal')
        self.authenticate(portal.login, portal.login)
        channel = self._start_session()
        self._visitor_post(channel, "Bonjour")
        self.assertEqual(channel.aite_visitor_email, 'client@exemple.cm')


@tagged('post_install', '-at_install', 'aite_website_livechat')
class TestLivechatEmailReply(AiteLivechatCommon):
    """ Réponse de l'opérateur envoyée par e-mail au visiteur parti. """

    def setUp(self):
        super().setUp()
        self.channel = self._start_session()
        self._visitor_post(self.channel, f"Une question. Répondez-moi à {VISITOR_EMAIL}")
        self.guest = self._visitor_guest(self.channel)
        self.assertEqual(self.channel.aite_visitor_email, VISITOR_EMAIL)

    def test_no_email_while_visitor_online(self):
        self._set_online(self.guest)
        self._operator_post(self.channel, "Bonjour, je regarde.")
        self.assertFalse(self._mails_to(VISITOR_EMAIL))

    def test_email_queued_when_visitor_away(self):
        self._set_online(self.guest)
        self._set_offline(self.guest)
        now = fields.Datetime.now()
        with patch.object(fields.Datetime, 'now', return_value=now):
            self._operator_post(self.channel, "Bonjour, voici notre tarif : 50 000 FCFA.")
        mail = self._mails_to(VISITOR_EMAIL)
        self.assertEqual(len(mail), 1)
        self.assertEqual(mail.state, 'outgoing')
        self.assertEqual(mail.scheduled_date, now + EMAIL_GROUPING_DELAY)
        self.assertEqual(mail.email_from, self.company.email_formatted)
        self.assertFalse(mail.recipient_ids)
        self.assertFalse(mail.email_cc)
        # Hors de la conversation : invisible dans Discuss et chez le visiteur.
        self.assertFalse(mail.model)
        self.assertNotIn(mail.mail_message_id, self.channel.message_ids)
        self.assertIn(self.company.name, mail.subject)
        self.assertIn("voici notre tarif : 50 000 FCFA.", mail.body_html)
        self.assertIn(self.website.get_base_url(), mail.body_html)
        # Seulement ce que l'opératrice a écrit : ni le visiteur, ni le
        # message d'absence.
        self.assertNotIn("Une question.", mail.body_html)
        self.assertNotIn("Nous ne sommes pas en ligne", mail.body_html)
        # La file d'envoi est réveillée à l'heure prévue.
        cron = self.env.ref('mail.ir_cron_mail_scheduler_action')
        self.assertTrue(self.env['ir.cron.trigger'].sudo().search([
            ('cron_id', '=', cron.id), ('call_at', '=', now + EMAIL_GROUPING_DELAY)]))

    def test_burst_grouped_and_throttled(self):
        now = fields.Datetime.now()
        with patch.object(fields.Datetime, 'now', return_value=now):
            for text in ("Premier message.", "Deuxième message.", "Troisième message."):
                self._operator_post(self.channel, text)
        mail = self._mails_to(VISITOR_EMAIL)
        self.assertEqual(len(mail), 1, "Une rafale de messages ne donne qu'un e-mail.")
        for text in ("Premier message.", "Deuxième message.", "Troisième message."):
            self.assertIn(text, mail.body_html)

        # L'e-mail part (la file l'efface), puis l'opératrice écrit encore :
        # l'e-mail suivant attend 10 minutes après le précédent et ne reprend
        # que les nouvelles réponses.
        first_scheduled = mail.scheduled_date
        mail.unlink()
        with patch.object(fields.Datetime, 'now', return_value=now + timedelta(minutes=3)):
            self._operator_post(self.channel, "Quatrième message.")
        mail_2 = self._mails_to(VISITOR_EMAIL)
        self.assertEqual(len(mail_2), 1)
        self.assertEqual(mail_2.scheduled_date, first_scheduled + EMAIL_MIN_INTERVAL)
        self.assertIn("Quatrième message.", mail_2.body_html)
        self.assertNotIn("Premier message.", mail_2.body_html)

        # Bien plus tard : de nouveau 2 minutes de regroupement seulement.
        mail_2.unlink()
        later = now + timedelta(hours=2)
        with patch.object(fields.Datetime, 'now', return_value=later):
            self._operator_post(self.channel, "Cinquième message.")
        self.assertEqual(self._mails_to(VISITOR_EMAIL).scheduled_date, later + EMAIL_GROUPING_DELAY)

    def test_pending_email_cancelled_when_visitor_writes_again(self):
        self._operator_post(self.channel, "Voici notre réponse.")
        self.assertEqual(len(self._mails_to(VISITOR_EMAIL)), 1)
        self._visitor_post(self.channel, "Merci, j'ai vu votre réponse.")
        self.assertFalse(self._mails_to(VISITOR_EMAIL))
        self.assertFalse(self.channel.aite_email_scheduled_dt)

    def test_content_escaped(self):
        self._operator_post(self.channel, Markup(
            "<p>Tarif &lt;script&gt;alert(1)&lt;/script&gt; <b>gras</b> &amp; "
            "<a href='https://exemple.cm/x'>lien</a></p>"))
        body = self._mails_to(VISITOR_EMAIL).body_html
        self.assertNotIn("<script", body)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", body)
        self.assertNotIn("<b>gras</b>", body)
        self.assertIn("&amp;", body)

    def test_never_to_undetected_address(self):
        other = self._start_session_for_other_visitor()
        self.assertFalse(other.aite_visitor_email)
        mails_before = self.env['mail.mail'].sudo().search_count([])
        self._operator_post(other, "Bonjour")
        self.assertEqual(self.env['mail.mail'].sudo().search_count([]), mails_before)

    def test_nothing_from_other_conversations(self):
        other = self._start_session_for_other_visitor()
        self._operator_post(other, "Message d'une autre conversation.")
        self._operator_post(self.channel, "Réponse pour Jean.")
        body = self._mails_to(VISITOR_EMAIL).body_html
        self.assertIn("Réponse pour Jean.", body)
        self.assertNotIn("autre conversation", body)

    def test_operator_can_read_email_fields(self):
        # Un opérateur (non administrateur) qui lit la conversation, par un
        # export par exemple : pas d'erreur d'accès.
        self._operator_post(self.channel, "Réponse lisible.")
        values = self.channel.with_user(self.operator).read(['aite_email_reply_html', 'aite_email_website_id'])[0]
        self.assertIn("Réponse lisible.", values['aite_email_reply_html'])
        self.assertEqual(values['aite_email_website_id'][0], self.website.id)

    def test_option_off(self):
        self.livechat_channel.aite_email_reply = False
        self._operator_post(self.channel, "Bonjour")
        self.assertFalse(self._mails_to(VISITOR_EMAIL))

    def test_email_problem_never_blocks_the_operator(self):
        # Modèle d'e-mail modifié et devenu invalide : le message de
        # l'opératrice est publié quand même, l'erreur va au journal.
        # (Odoo refuse d'enregistrer un modèle invalide : on passe par SQL.)
        template = self.env.ref('aite_website_livechat.mail_template_livechat_email_reply')
        self.env.cr.execute(
            "UPDATE mail_template SET body_html = jsonb_build_object('en_US', %s, 'fr_FR', %s) WHERE id = %s",
            ['<p><t t-out="object.aite_champ_inexistant"/></p>'] * 2 + [template.id],
        )
        template.invalidate_recordset()
        with mute_logger('odoo.addons.mail.models.mail_render_mixin'), \
                self.assertLogs('odoo.addons.aite_website_livechat.models.discuss_channel', level='ERROR'):
            message = self._operator_post(self.channel, "Bonjour")
        self.assertIn(message, self.channel.message_ids)
        self.assertFalse(self._mails_to(VISITOR_EMAIL))

    def _start_session_for_other_visitor(self):
        cookies = self.opener.cookies.copy()
        self.opener.cookies.clear()
        channel = self._start_session()
        self._visitor_post(channel, "Bonjour, autre visiteur.")
        self.opener.cookies = cookies
        return channel
