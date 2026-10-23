# -*- coding: utf-8 -*-
"""18.0.1.0.2 — lien ligne de folio → ticket de caisse (fidélité).

La livraison 3 ajoute ``aite.hotel.folio.line.aite_pos_order_id`` : la
fidélité s'en sert pour ne pas créditer deux fois une consommation de bar
déjà créditée sur son ticket (ticket « Note de chambre » puis folio). Sous
la livraison 2, le seul lien était ``pos.order.aite_folio_line_id`` : les
lignes reportées par la caisse avant la mise à niveau avaient le nouveau
champ vide, et un séjour en cours facturé après la mise à niveau rapportait
encore ses consommations de bar deux fois (statut VIP / VVIP gonflé).

On recopie le lien existant, sans toucher à une ligne déjà rattachée :
idempotent, une ligne par ticket sous la livraison 2.
"""
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    if not version:
        return
    cr.execute("""
        UPDATE aite_hotel_folio_line l
           SET aite_pos_order_id = o.id
          FROM pos_order o
         WHERE o.aite_folio_line_id = l.id
           AND l.aite_pos_order_id IS NULL
    """)
    if cr.rowcount:
        _logger.info(
            "Note de chambre : %d ligne(s) de folio rattachée(s) à leur "
            "ticket de caisse.", cr.rowcount)
