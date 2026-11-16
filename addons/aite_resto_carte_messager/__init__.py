# -*- coding: utf-8 -*-
"""Le crochet d'installation : joue data/carte.py, la même source que la graine
de développement (dev/seeds/seed_carte_messager.py), en « mode module ».

La carte va dans la caisse au service à table contrôlé. Sur une base neuve
installée d'un seul geste, Odoo charge le plan comptable APRÈS les crochets
d'installation : la caisse n'existe pas encore. La carte est alors posée
juste après le chargement du plan (models/account_chart_template.py)."""
import logging
import os

from . import models

_logger = logging.getLogger(__name__)


def jouer_carte(env, mode_module=True):
    """Pose (ou remet à jour) la carte ; rend la phrase de bilan."""
    chemin = os.path.join(os.path.dirname(__file__), 'data', 'carte.py')
    with open(chemin, encoding='utf-8') as fichier:
        code = compile(fichier.read(), chemin, 'exec')
    contexte = {'env': env, 'MODE_MODULE': mode_module, '__name__': 'aite_resto_carte_messager.carte'}
    exec(code, contexte)  # noqa: S102 — script du module, jamais une saisie
    return contexte.get('RESULTAT')


def caisse_restaurant(env, company):
    """La caisse au service à table contrôlé de la société ; posée par
    aite_pos_restaurant si la société a un plan comptable mais pas encore de caisse."""
    Caisses = env['pos.config']
    domaine = [('company_id', '=', company.id), ('aite_mode_restaurant', '=', True)]
    caisse = Caisses.search(domaine, limit=1)
    if not caisse and company.chart_template:
        Caisses._aite_preparer_caisse(company)
        caisse = Caisses.search(domaine, limit=1)
    return caisse


def poser_carte(env):
    if caisse_restaurant(env, env.company):
        _logger.info("Carte Le Messager : %s", jouer_carte(env))
    else:
        _logger.info("Carte Le Messager : pas encore de plan comptable, la carte sera posée "
                     "juste après son chargement.")
