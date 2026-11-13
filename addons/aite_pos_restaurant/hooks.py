# -*- coding: utf-8 -*-
"""Crochet d'installation : une caisse « Restaurant » prête au premier lancement
(spécification, partie 4.4).

Sur une base qui a déjà son plan comptable, la caisse est créée ici. Sur une
base neuve, Odoo charge le plan comptable à la fin du chargement du registre,
**après** les crochets d'installation : la caisse est alors créée par la
surcharge de ``account.chart.template._load`` (même constat que
``aite_pos_credit/hooks.py``). Dans les deux cas, ``_aite_preparer_caisse`` est
idempotente et ne modifie jamais une caisse existante (T16).
"""


def post_init_hook(env):
    for company in env['res.company'].search([]):
        if company.chart_template:
            env['pos.config']._aite_preparer_caisse(company)
