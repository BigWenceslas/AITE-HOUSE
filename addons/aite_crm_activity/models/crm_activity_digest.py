# -*- coding: utf-8 -*-
import logging
from datetime import timedelta
from urllib.parse import urlencode

from odoo import api, fields, models, tools

_logger = logging.getLogger(__name__)

PARAM_UPCOMING_DAYS = 'aite_crm_activity.digest_upcoming_days'
DEFAULT_UPCOMING_DAYS = 3
MAX_ROWS_PER_SECTION = 50


class AiteCrmActivityDigest(models.AbstractModel):
    """ Récapitulatif quotidien : chaque utilisateur reçoit, le matin, la
    liste de ses activités en cours sur les pistes et opportunités — en
    retard, du jour et à venir. """
    _name = 'aite.crm.activity.digest'
    _description = "Récapitulatif quotidien des activités CRM"

    # ------------------------------------------------------------------
    # Destinataires
    # ------------------------------------------------------------------

    @api.model
    def _get_upcoming_days(self):
        value = self.env['ir.config_parameter'].sudo().get_param(PARAM_UPCOMING_DAYS)
        try:
            return max(0, int(value)) if value not in (None, False, '') else DEFAULT_UPCOMING_DAYS
        except ValueError:
            return DEFAULT_UPCOMING_DAYS

    @api.model
    def _get_recipients(self):
        """ Utilisateurs internes actifs, abonnés, ayant une adresse e-mail et
        au moins une activité ouverte sur une piste ou opportunité dont
        l'échéance tombe dans la fenêtre du récapitulatif, et qui n'ont pas
        encore reçu celui du jour. La fenêtre est élargie d'un jour pour
        couvrir les fuseaux horaires ; chaque utilisateur est ensuite filtré
        selon sa propre date du jour. """
        today = fields.Date.today()
        horizon = today + timedelta(days=self._get_upcoming_days() + 1)
        groups = self.env['mail.activity'].sudo()._read_group(
            [('res_model', '=', 'crm.lead'), ('date_deadline', '<=', horizon),
             ('user_id', '!=', False)],
            ['user_id'],
        )
        users = self.env['res.users'].sudo().union(*(user for (user,) in groups))
        return users.filtered(
            lambda u: u.active and not u.share and u.email and u.aite_crm_digest_subscribed
            and u.aite_crm_digest_last_sent != today
        )

    # ------------------------------------------------------------------
    # Contenu
    # ------------------------------------------------------------------

    @api.model
    def _get_user_digest(self, user, now=None):
        """ Activités de l'utilisateur, lues avec ses propres droits, dans
        son fuseau horaire et sa langue. Renvoie None s'il n'a rien.

        :param now: instant de référence (datetime UTC naïf), pour les tests
        """
        env = self.with_user(user).with_context(
            lang=user.lang or self.env.lang or 'en_US', tz=user.tz or 'UTC').env
        today = fields.Date.context_today(self.with_env(env), timestamp=now)
        horizon = today + timedelta(days=self._get_upcoming_days())
        activities = env['mail.activity'].search([
            ('res_model', '=', 'crm.lead'),
            ('user_id', '=', user.id),
            ('date_deadline', '<=', horizon),
        ], order='date_deadline asc, id asc')
        if not activities:
            return None

        leads = env['crm.lead'].browse(activities.mapped('res_id'))
        readable = {lead.id: lead for lead in leads._filtered_access('read')}
        base_url = self.get_base_url()

        sections = {'overdue': [], 'today': [], 'upcoming': []}
        for activity in activities:
            deadline = activity.date_deadline
            key = 'overdue' if deadline < today else 'today' if deadline == today else 'upcoming'
            lead = readable.get(activity.res_id)
            sections[key].append({
                'type': activity.activity_type_id.name or '',
                'summary': activity.summary or '',
                'deadline': tools.format_date(env, deadline),
                'late_days': (today - deadline).days if key == 'overdue' else 0,
                'lead_name': lead.name if lead else activity.res_name,
                'partner': lead.partner_id.display_name if lead else '',
                'stage': lead.stage_id.name if lead else '',
                'revenue': tools.format_amount(env, lead.expected_revenue, lead.company_currency)
                           if lead and lead.expected_revenue else '',
                'url': '%s/mail/view?%s' % (base_url, urlencode({
                    'model': 'crm.lead', 'res_id': activity.res_id})),
            })
        counts = {key: len(rows) for key, rows in sections.items()}
        for key in sections:
            sections[key] = sections[key][:MAX_ROWS_PER_SECTION]
        return {
            'lang_env': env,
            'user': user,
            'company': user.company_id,
            'today': tools.format_date(env, today, date_format='EEEE d MMMM y'),
            'sections': sections,
            'counts': counts,
            'total': sum(counts.values()),
            'upcoming_days': self._get_upcoming_days(),
            'max_rows': MAX_ROWS_PER_SECTION,
            'dashboard_url': '%s/odoo/suivi-activites' % base_url,
        }

    @api.model
    def _prepare_mail_values(self, user, digest):
        env = digest['lang_env']
        values = {key: value for key, value in digest.items() if key != 'lang_env'}
        body = env['ir.qweb']._render('aite_crm_activity.digest_email', values)
        counts = digest['counts']
        if counts['overdue']:
            subject = env._(
                "Vos activités CRM du jour : %(total)s, dont %(overdue)s en retard",
                total=digest['total'], overdue=counts['overdue'])
        else:
            subject = env._("Vos activités CRM du jour : %(total)s", total=digest['total'])
        company = user.company_id
        return {
            'subject': subject,
            'body_html': body,
            'email_from': (company.partner_id.email_formatted
                           or self.env.ref('base.user_root').email_formatted),
            'email_to': user.email_formatted,
            'author_id': self.env.ref('base.partner_root').id,
            'auto_delete': True,
            'state': 'outgoing',
            'headers': {'X-Auto-Response-Suppress': 'OOF'},
        }

    @api.model
    def _send_to_user(self, user):
        """ Met en file le récapitulatif d'un utilisateur. Renvoie le
        mail.mail créé, ou un enregistrement vide s'il n'a rien à faire. """
        digest = self._get_user_digest(user)
        if not digest:
            return self.env['mail.mail']
        return self.env['mail.mail'].sudo().create(self._prepare_mail_values(user, digest))

    # ------------------------------------------------------------------
    # Envoi
    # ------------------------------------------------------------------

    @api.model
    def _cron_send_daily_digest(self):
        users = self._get_recipients()
        today = fields.Date.today()
        in_cron = bool(self.env.context.get('ir_cron_progress_id'))
        if in_cron:
            self.env['ir.cron']._commit_progress(remaining=len(users))
        sent = 0
        for user in users:
            try:
                with self.env.cr.savepoint():
                    if self._send_to_user(user):
                        sent += 1
                    user.sudo().aite_crm_digest_last_sent = today
            except Exception:
                _logger.exception("Récapitulatif CRM : échec pour l'utilisateur %s", user.id)
            if in_cron:
                self.env['ir.cron']._commit_progress(1)
        _logger.info("Récapitulatif CRM : %s e-mail(s) mis en file sur %s destinataire(s).",
                     sent, len(users))
        return sent

    @api.model
    def action_send_my_digest(self):
        """ Bouton des Paramètres : envoie tout de suite son propre
        récapitulatif à l'utilisateur, pour voir à quoi il ressemble. """
        user = self.env.user
        mail = self._send_to_user(user) if user.email else self.env['mail.mail']
        if mail:
            mail.send(raise_exception=False)
            message = self.env._("Récapitulatif envoyé à %(email)s.", email=user.email)
            kind = 'success'
        elif not user.email:
            message = self.env._("Renseignez votre adresse e-mail dans vos préférences.")
            kind = 'warning'
        else:
            message = self.env._("Aucune activité en cours : rien à envoyer pour l'instant.")
            kind = 'info'
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {'message': message, 'type': kind, 'sticky': False},
        }
