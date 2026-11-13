# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

import pytz

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.addons.base.models.res_partner import _tz_get

from .crm_activity_digest import DEFAULT_TZ, DEFAULT_UPCOMING_DAYS, PARAM_TZ, PARAM_UPCOMING_DAYS
from .crm_activity_params import (
    DEFAULT_CRITICAL_DAYS, DEFAULT_DASHBOARD_UPCOMING_DAYS, DEFAULT_DORMANT_DAYS, DEFAULT_HIGH_DAYS,
    MAX_DAYS, PARAM_CRITICAL_DAYS, PARAM_DASHBOARD_UPCOMING_DAYS, PARAM_DORMANT_DAYS, PARAM_HIGH_DAYS,
)
from .ir_cron import DIGEST_CRON_XMLID

# Réglages du tableau de bord et des seuils, validés à l'enregistrement.
ACTIVITY_DAY_FIELDS = (
    'aite_crm_dashboard_upcoming_days',
    'aite_crm_late_high_days',
    'aite_crm_late_critical_days',
    'aite_crm_dormant_days',
)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    aite_crm_digest_active = fields.Boolean(
        string="Récapitulatif quotidien des activités",
        help="Chaque matin, chaque utilisateur reçoit par e-mail la liste de "
             "ses activités en cours sur les opportunités.",
    )
    aite_crm_digest_hour = fields.Float(
        string="Heure d'envoi",
        help="Heure d'envoi du récapitulatif, dans le fuseau horaire choisi. "
             "Elle est la même pour tous les utilisateurs.",
    )
    aite_crm_digest_tz = fields.Selection(
        _tz_get,
        string="Fuseau horaire de l'envoi",
        config_parameter=PARAM_TZ,
        default=DEFAULT_TZ,
        help="Fuseau horaire de l'heure d'envoi. L'envoi garde la même heure "
             "locale toute l'année, changements d'heure compris.",
    )
    aite_crm_digest_upcoming_days = fields.Integer(
        string="Activités à venir incluses",
        config_parameter=PARAM_UPCOMING_DAYS,
        default=DEFAULT_UPCOMING_DAYS,
        help="Nombre de jours à venir inclus dans le récapitulatif, en plus "
             "des activités en retard et du jour.",
    )
    aite_crm_dashboard_upcoming_days = fields.Integer(
        string="Tableau de bord : activités à venir (jours)",
        config_parameter=PARAM_DASHBOARD_UPCOMING_DAYS,
        default=DEFAULT_DASHBOARD_UPCOMING_DAYS,
        help="Fenêtre « À venir » du tableau de bord : de demain à aujourd'hui "
             "plus ce nombre de jours. Le plan de charge en montre au plus 14.",
    )
    aite_crm_late_high_days = fields.Integer(
        string="Retard élevé à partir de (jours)",
        config_parameter=PARAM_HIGH_DAYS,
        default=DEFAULT_HIGH_DAYS,
        help="Une activité en retard d'au moins ce nombre de jours est signalée "
             "« élevé » (orange).",
    )
    aite_crm_late_critical_days = fields.Integer(
        string="Retard critique à partir de (jours)",
        config_parameter=PARAM_CRITICAL_DAYS,
        default=DEFAULT_CRITICAL_DAYS,
        help="Une activité en retard d'au moins ce nombre de jours est signalée "
             "« critique » (rouge) et déclenche une alerte sur le tableau de bord.",
    )
    aite_crm_dormant_days = fields.Integer(
        string="Opportunité dormante après (jours)",
        config_parameter=PARAM_DORMANT_DAYS,
        default=DEFAULT_DORMANT_DAYS,
        help="Une opportunité sans activité planifiée dont la dernière action "
             "(activité réalisée ou changement d'étape) date d'au moins ce nombre "
             "de jours est dite « dormante ».",
    )

    @api.model
    def _aite_digest_cron(self):
        return self.env.ref(DIGEST_CRON_XMLID, raise_if_not_found=False)

    @api.model
    def _aite_digest_tz(self):
        return pytz.timezone(self.env['aite.crm.activity.digest']._get_tz_name())

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

    def _aite_check_activity_days(self):
        """ Contrôle serveur des fenêtres et seuils : chaque valeur de 1 à 365
        jours, et le retard élevé strictement inférieur au retard critique. """
        for record in self:
            for fname in ACTIVITY_DAY_FIELDS:
                value = record[fname]
                if not 1 <= value <= MAX_DAYS:
                    raise ValidationError(self.env._(
                        "« %(setting)s » : saisissez un nombre de jours entre 1 et %(max)s "
                        "(valeur saisie : %(value)s).",
                        setting=record._fields[fname]._description_string(self.env),
                        max=MAX_DAYS, value=value))
            if record.aite_crm_late_high_days >= record.aite_crm_late_critical_days:
                raise ValidationError(self.env._(
                    "Le retard élevé (%(high)s j) doit commencer avant le retard critique "
                    "(%(critical)s j).",
                    high=record.aite_crm_late_high_days,
                    critical=record.aite_crm_late_critical_days))

    def set_values(self):
        # Rien n'est enregistré si un seuil est incohérent.
        self._aite_check_activity_days()
        # Le fuseau (paramètre système) est enregistré par super() : l'heure
        # ci-dessous est ensuite interprétée dans ce fuseau.
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
