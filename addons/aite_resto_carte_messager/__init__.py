# -*- coding: utf-8 -*-
"""Pose la carte du restaurant Le Messager.

La source unique est data/carte.py (aussi jouée par la graine de
développement dev/seeds/seed_carte_messager.py). Elle est jouée :
- à l'installation ET à chaque mise à niveau du module
  (data/carte_data.xml → pos.config._aite_poser_carte_messager), pour chaque
  société qui a un plan comptable ;
- juste après le premier chargement d'un plan comptable (base neuve installée
  d'un seul geste : Odoo charge le plan APRÈS les données des modules) ;
- à la demande : Point de Vente → Configuration → « Poser la carte Le Messager ».
"""
import logging
import os

from . import models

_logger = logging.getLogger(__name__)


def jouer_carte(env, mode_module=True):
    """Pose (ou remet à jour) la carte dans la société courante de ``env`` ;
    rend la phrase de bilan."""
    chemin = os.path.join(os.path.dirname(__file__), 'data', 'carte.py')
    with open(chemin, encoding='utf-8') as fichier:
        code = compile(fichier.read(), chemin, 'exec')
    contexte = {'env': env, 'MODE_MODULE': mode_module, '__name__': 'aite_resto_carte_messager.carte'}
    exec(code, contexte)  # noqa: S102 — script du module, jamais une saisie
    return contexte.get('RESULTAT')


def caisse_restaurant(env, company):
    """La caisse au service à table contrôlé de la société ; posée par
    aite_pos_restaurant si la société a un plan comptable mais pas encore de caisse."""
    Caisses = env['pos.config'].sudo()
    domaine = [('company_id', '=', company.id), ('aite_mode_restaurant', '=', True)]
    caisse = Caisses.search(domaine, limit=1)
    if not caisse and company.chart_template:
        Caisses._aite_preparer_caisse(company)
        caisse = Caisses.search(domaine, limit=1)
    return caisse
