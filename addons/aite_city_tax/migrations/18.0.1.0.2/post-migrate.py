# -*- coding: utf-8 -*-
"""18.0.1.0.2 — barème appliqué des hôtels existants (ECARTS n° 73).

Un hôtel créé avant l'installation du module a gardé « Barème appliqué »
vide : le champ stocké a été calculé avant le chargement des barèmes. Le
code corrigé recalcule les hôtels quand un barème est créé, ce qui couvre
une installation, pas une base déjà installée (les barèmes livrés sont en
``noupdate`` et ne sont pas recréés à la mise à niveau).

On recalcule donc le barème de tous les hôtels, puis, pour ceux dont le
barème a changé, on remet à jour la taxe des folios encore ouverts et non
facturés — exactement ce que fait un changement de catégorie de l'hôtel
(``aite.hotel.hotel.write``). Les folios facturés ne bougent pas.
"""
import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    if not version:
        return
    env = api.Environment(cr, SUPERUSER_ID, {})
    Hotel = env['aite.hotel.hotel'].with_context(active_test=False)
    hotels = Hotel.search([])
    if not hotels:
        return
    before = {hotel.id: hotel.city_tax_rate_id.id for hotel in hotels}
    env['aite.city.tax.rate']._recompute_hotel_rates()
    env.flush_all()
    changed = hotels.filtered(
        lambda h: h.city_tax_rate_id.id != before[h.id])
    if not changed:
        return
    folios = env['aite.hotel.folio'].search([
        ('hotel_id', 'in', changed.ids),
        ('state', '=', 'open'),
        ('move_id', '=', False),
    ])
    folios._sync_city_tax_line()
    _logger.info(
        "Taxe de séjour : barème appliqué recalculé pour %s ; %d folio(s) "
        "ouvert(s) mis à jour.",
        ", ".join(changed.mapped('name')), len(folios))
