# -*- coding: utf-8 -*-
from . import models


def _init_pos_margin_data(env):
    """
    Hook post-installation.

    Rétro-peuple le champ ``cost_unit`` sur les lignes POS existantes en
    utilisant le ``standard_price`` courant du produit. Ce snapshot fige
    la marge historique : si le coût d'achat évolue plus tard, les marges
    déjà calculées restent stables.

    Le déclenchement du recompute via ``flush_recordset`` met à jour
    ``total_cost``, ``margin`` et ``margin_rate`` (champs stored avec
    depends sur ``cost_unit``).
    """
    PosLine = env['pos.order.line']
    lines = PosLine.search([('cost_unit', '=', 0)])
    if not lines:
        return

    # Traitement par lots de 1000 pour éviter la saturation mémoire
    # sur les bases avec un fort historique POS.
    batch_size = 1000
    for offset in range(0, len(lines), batch_size):
        batch = lines[offset:offset + batch_size]
        for line in batch:
            if line.product_id and line.product_id.standard_price:
                line.cost_unit = line.product_id.standard_price
        batch.flush_recordset(['cost_unit'])
        env.cr.commit()
