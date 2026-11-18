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


def _jouer(env, nom, mode_module):
    """Joue le script ``data/<nom>`` ; rend ses variables."""
    chemin = os.path.join(os.path.dirname(__file__), 'data', nom)
    with open(chemin, encoding='utf-8') as fichier:
        code = compile(fichier.read(), chemin, 'exec')
    contexte = {'env': env, 'MODE_MODULE': mode_module, '__name__': 'aite_resto_carte_messager.' + nom[:-3]}
    exec(code, contexte)  # noqa: S102 — script du module, jamais une saisie
    return contexte


def jouer_carte(env, mode_module=True):
    """Pose (ou remet à jour) la salle, l'équipe et la carte dans la société courante de ``env`` ;
    rend la phrase de bilan.

    En mode module (bouton « Poser la carte Le Messager », installation, mise à
    niveau), un bilan lisible par un manager : « Carte posée : 101 produits en
    30 familles ; salle : 12 tables ; équipe : 7 employés, 3 comptes. Rien n'a
    été créé en double. », précédé de ce qui vient d'être créé ou remis à jour.
    Hors mode module (graine dev/seeds/seed_carte_messager.py), le bilan
    technique de la carte."""
    if not mode_module:
        # la base de développement reçoit la salle et l'équipe de dev/seeds/seed_restaurant.py
        return _jouer(env, 'carte.py', False).get('RESULTAT') or ''
    # la salle et l'équipe d'abord, puis la carte
    equipe = _jouer(env, 'equipe.py', True)
    carte = _jouer(env, 'carte.py', True)
    bilan = "%s ; %s." % (carte['BILAN'], equipe['BILAN_EQUIPE'])
    crees = carte['BILAN_CREES'] + equipe['BILAN_EQUIPE_CREES']
    if crees:
        bilan += " Créés cette fois : %s." % ", ".join(crees)
    if carte['BILAN_AUTRES']:
        bilan += " Mis à jour : %s." % " ; ".join(carte['BILAN_AUTRES'])
    return bilan + " Rien n'a été créé en double."


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
