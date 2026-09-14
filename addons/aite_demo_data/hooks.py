# -*- coding: utf-8 -*-
"""Accroche d'installation du jeu d'essai."""
import logging

_logger = logging.getLogger(__name__)


def post_init_generate(env):
    """
    Complète le référentiel XML par le jeu opérationnel.

    Exécuté après le chargement des fichiers de données : ardoises,
    notes de chambre en attente, tâches de gouvernante, achats,
    consignes, services hôteliers, tarifs saisonniers et profils
    utilisateurs métier.
    """
    try:
        env['aite.demo.generator'].generate_all()
    except Exception:  # noqa: BLE001
        # Une base de démonstration ne doit jamais échouer à s'installer
        # à cause d'un module optionnel absent ou d'une configuration
        # comptable incomplète : on trace et on laisse l'installation
        # aboutir avec le référentiel XML.
        _logger.exception(
            "Jeu d'essai : génération opérationnelle interrompue ; le "
            "référentiel reste installé. Relancer manuellement via "
            "env['aite.demo.generator'].generate_all().")
