# -*- coding: utf-8 -*-
"""18.0.2.0.5 — mode de paiement « Ardoise client » (ECARTS n° 74).

Le crochet d'installation livré ne créait jamais le mode (recherche sur
``account.account.company_id``, absent d'Odoo 18, erreur avalée). Il est
corrigé, mais un crochet d'installation ne s'exécute pas à la mise à
niveau : une base déjà installée restait sans « Ardoise client ».

Pour chaque société qui n'a AUCUN mode « ardoise » (même archivé : un mode
archivé l'a été volontairement), on fait ce que fait l'installation :
création du mode « Compte client » et ajout aux caisses de la société. Une
caisse dont la session est ouverte ne peut pas changer de modes de
paiement : elle est signalée dans le journal (avertissement) et le mode
s'y ajoute à la main.
"""
import logging

from odoo import SUPERUSER_ID, api

from odoo.addons.aite_pos_credit import hooks

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    if not version:
        return
    env = api.Environment(cr, SUPERUSER_ID, {})
    Method = env['pos.payment.method'].with_context(active_test=False)
    for company in env['res.company'].search([]):
        if Method.search_count([('is_aite_credit', '=', True),
                                ('company_id', '=', company.id)]):
            continue
        try:
            with env.cr.savepoint():
                hooks._setup_company(env, company)
            _logger.info("POS Crédit : mode « %s » créé pour la société %s.",
                         hooks.CREDIT_METHOD_NAME, company.name)
        except Exception:
            _logger.warning(
                "POS Crédit : mode « %s » non créé pour la société %s.",
                hooks.CREDIT_METHOD_NAME, company.name, exc_info=True)
