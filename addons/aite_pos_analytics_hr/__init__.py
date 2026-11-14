# -*- coding: utf-8 -*-
from . import models


def uninstall_hook(env):
    """La passerelle désinstallée (seule, ou avec le restaurant ou pos_hr) :
    la vue de l'analyse AITE est recréée sans ses colonnes. Sinon Odoo, en
    supprimant ensuite les colonnes qu'elles lisent sur l'addition
    (``aite_ouverte_par_id``, ``aite_encaissee_par_id``, ``employee_id``, par
    ``DROP COLUMN … CASCADE``), supprimerait la vue avec elles, et l'analyse
    ne s'ouvrirait plus jusqu'à la mise à niveau d'``aite_pos_analytics``."""
    env['aite.pos.daily.report']._aite_creer_vue('')
