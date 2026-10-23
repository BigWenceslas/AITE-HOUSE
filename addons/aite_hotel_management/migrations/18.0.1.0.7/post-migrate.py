# -*- coding: utf-8 -*-
"""18.0.1.0.7 — nom de la tâche planifiée quotidienne.

La tâche est livrée en ``noupdate`` (le client peut en changer l'heure) :
son nouveau nom (« non-présentations » au lieu de « no-show », ECARTS
n° 42) n'arrive pas sur une base déjà installée. On la renomme dans chaque
langue où elle porte encore l'ancien nom ; un nom choisi par le client
n'est pas touché.
"""
import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)

OLD_NAME = "Hôtel : tâches quotidiennes (no-show, ménage)"
NEW_NAME = "Hôtel : tâches quotidiennes (non-présentations, ménage)"


def migrate(cr, version):
    if not version:
        return
    env = api.Environment(cr, SUPERUSER_ID, {})
    cron = env.ref('aite_hotel_management.ir_cron_hotel_daily',
                   raise_if_not_found=False)
    if not cron:
        return
    action = cron.ir_actions_server_id
    langs = {'en_US'} | {code for code, __ in env['res.lang'].get_installed()}
    translations = {
        lang: NEW_NAME for lang in langs
        if action.with_context(lang=lang).name == OLD_NAME
    }
    if translations:
        action.update_field_translations('name', translations)
        _logger.info("Tâche planifiée renommée « %s » (%s).",
                     NEW_NAME, ", ".join(sorted(translations)))
