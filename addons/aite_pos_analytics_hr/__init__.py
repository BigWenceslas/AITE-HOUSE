# -*- coding: utf-8 -*-
from . import models


def uninstall_hook(env):
    """La passerelle désinstallée (seule, ou avec le restaurant ou pos_hr) :
    la vue de l'analyse AITE est recréée sans ses colonnes. Sinon Odoo, en
    supprimant ensuite les colonnes qu'elles lisent sur l'addition
    (``aite_ouverte_par_id``, ``aite_encaissee_par_id``, ``employee_id``, par
    ``DROP COLUMN … CASCADE``), supprimerait la vue avec elles, et l'analyse
    ne s'ouvrirait plus jusqu'à la mise à niveau d'``aite_pos_analytics``.

    Seules les colonnes de la passerelle sont retirées : celles qu'un autre
    module ajoute par le même point d'extension restent (revue de 6a,
    constat 8)."""
    rapport = env['aite.pos.daily.report'].with_context(aite_sans_employe=True)
    rapport._aite_creer_vue(rapport._aite_colonnes_supplementaires())
