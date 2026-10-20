# -*- coding: utf-8 -*-
"""18.0.2.1.2 — recalcul des agrégats stockés des sessions POS.

* ``total_ca`` (et donc ``margin_rate``, ``average_basket``) passe en
  hors taxes, comme le tableau de bord et le cockpit Direction ;
* ``cash_discrepancy_severity`` ne classe plus une caisse ouverte que
  personne n'a comptée.

Les champs calculés stockés ne sont pas recalculés d'eux-mêmes à la mise à
niveau : on les remet en file de calcul pour toutes les sessions.
"""
from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    if not version:
        return
    env = api.Environment(cr, SUPERUSER_ID, {})
    Session = env['pos.session']
    sessions = Session.with_context(active_test=False).search([])
    for fname in ('total_ca', 'margin_rate', 'average_basket',
                  'cash_discrepancy_severity'):
        env.add_to_compute(Session._fields[fname], sessions)
    env.flush_all()
