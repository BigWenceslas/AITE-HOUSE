# -*- coding: utf-8 -*-
from odoo import models

DIGEST_CRON_XMLID = 'aite_crm_activity.ir_cron_crm_activity_digest'


class IrCron(models.Model):
    _inherit = 'ir.cron'

    def _reschedule_later(self, job):
        """ Odoo avance une tâche quotidienne d'un jour dans le fuseau
        horaire de son utilisateur (Europe/Brussels pour l'utilisateur
        système) : au passage à l'heure d'été européenne, le récapitulatif
        partirait une heure plus tôt à Douala. On l'avance dans le fuseau
        choisi dans les Paramètres du CRM. """
        digest_cron_id = self.env['ir.model.data']._xmlid_to_res_id(
            DIGEST_CRON_XMLID, raise_if_not_found=False)
        if digest_cron_id and job['id'] == digest_cron_id:
            tz = self.env['aite.crm.activity.digest']._get_tz_name()
            return super(IrCron, self.with_context(tz=tz))._reschedule_later(job)
        return super()._reschedule_later(job)
