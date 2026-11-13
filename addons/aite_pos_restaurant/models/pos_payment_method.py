# -*- coding: utf-8 -*-
"""Modes de paiement réservés au manager en caisse (AH-02 ; spécification,
partie 4.2).

Un mode « payer plus tard » (ardoise, compte client) n'est proposé qu'au
manager. La note de chambre d'``aite_hotel_pos_link`` (``is_room_charge``),
qui est aussi un mode « payer plus tard », reste proposée : ce champ n'étant
pas chargé en caisse, c'est le serveur qui marque chaque mode
(``_aite_reserve_manager``). ``getattr`` : le module hôtelier n'est pas une
dépendance (AH-12).
"""
from odoo import models


class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    def _load_pos_data(self, data):
        res = super()._load_pos_data(data)
        config = self.env['pos.config'].browse(data['pos.config']['data'][0]['id'])
        if not config._aite_actif():
            return res
        modes = {mode.id: mode for mode in self.browse([m['id'] for m in res['data']])}
        for valeurs in res['data']:
            mode = modes[valeurs['id']]
            valeurs['_aite_reserve_manager'] = bool(
                mode.type == 'pay_later' and not getattr(mode, 'is_room_charge', False))
        return res
