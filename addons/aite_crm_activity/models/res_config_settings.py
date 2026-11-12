# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

import pytz

from odoo import api, fields, models

from .crm_activity_digest import DEFAULT_UPCOMING_DAYS, PARAM_UPCOMING_DAYS

DIGEST_CRON_XMLID = 'aite_crm_activity.ir_cron_crm_activity_digest'
DEFAULT_TZ = 'Africa/Douala'


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    aite_crm_digest_active = fields.Boolean(
        string="Récapitulatif quotidien des activités",
        help="Chaque matin, chaque utilisateur reçoit par e-mail la liste de "
             "ses activités en cours sur les opportunités.",
    )
    aite_crm_digest_hour = fields.Float(
        string="Heure d'envoi",
        help="Heure locale d'envoi du récapitulatif (fuseau horaire de "
             "l'utilisateur qui fait le réglage).",
    )
    aite_crm_digest_upcoming_days = fields.Integer(
        string="Activités à venir incluses",
        config_parameter=PARAM_UPCOMING_DAYS,
        default=DEFAULT_UPCOMING_DAYS,
        help="Nombre de jours à venir inclus dans le récapitulatif, en plus "
             "des activités en retard et du jour.",
    )

    @api.model
    def _aite_digest_cron(self):
        return self.env.ref(DIGEST_CRON_XMLID, raise_if_not_found=False)

    @api.model
    def _aite_digest_tz(self):
        return pytz.timezone(self.env.user.tz or DEFAULT_TZ)

    @api.model
    def get_values(self):
        res = super().get_values()
        cron = self._aite_digest_cron()
        if cron:
            cron = cron.sudo()
            local = pytz.utc.localize(cron.nextcall).astimezone(self._aite_digest_tz())
            res.update(
                aite_crm_digest_active=cron.active,
                aite_crm_digest_hour=local.hour + local.minute / 60.0,
            )
        return res

    def set_values(self):
        super().set_values()
        cron = self._aite_digest_cron()
        if not cron:
            return
        cron = cron.sudo()
        vals = {}
        if cron.active != self.aite_crm_digest_active:
            vals['active'] = self.aite_crm_digest_active
        local = pytz.utc.localize(cron.nextcall).astimezone(self._aite_digest_tz())
        hour_changed = abs(local.hour + local.minute / 60.0 - self.aite_crm_digest_hour) > 1 / 120
        stale = cron.nextcall < fields.Datetime.now()
        # Nouvelle heure, ou réactivation / échéance dépassée : on cale le
        # prochain envoi sur la prochaine occurrence de l'heure choisie (et
        # non « tout de suite », ce qu'Odoo ferait avec une échéance passée).
        if hour_changed or stale or vals.get('active'):
            vals['nextcall'] = self._aite_digest_next_call(self.aite_crm_digest_hour)
        if vals:
            cron.write(vals)

    @api.model
    def _aite_digest_next_call(self, hour):
        """ Prochaine occurrence de l'heure locale demandée, en UTC naïf
        (format de ir.cron.nextcall). """
        hour = min(max(hour or 0.0, 0.0), 23.99)
        tz = self._aite_digest_tz()
        now_local = datetime.now(pytz.utc).astimezone(tz)
        hours, minutes = int(hour), int(round((hour % 1) * 60)) % 60
        target = tz.localize(datetime(now_local.year, now_local.month, now_local.day, hours, minutes))
        if target <= now_local:
            target = tz.localize(datetime.combine(target.date() + timedelta(days=1),
                                                  target.time().replace(tzinfo=None)))
        return target.astimezone(pytz.utc).replace(tzinfo=None)

    def action_aite_send_my_digest(self):
        return self.env['aite.crm.activity.digest'].action_send_my_digest()
