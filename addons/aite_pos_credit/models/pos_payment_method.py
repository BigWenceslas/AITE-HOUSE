# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class PosPaymentMethod(models.Model):
    """
    Extension méthode de paiement POS.

    On marque la (ou les) méthode(s) de paiement qui matérialisent une vente
    à crédit (« ardoise »). En standard Odoo, une telle méthode est de type
    *pay_later* : elle ne mouvemente pas la caisse mais porte le montant au
    compte client. On s'appuie dessus pour déclencher la création de
    l'ardoise côté module, plutôt que de réimplémenter le flux POS.
    """
    _inherit = 'pos.payment.method'

    is_aite_credit = fields.Boolean(
        string="Vente à crédit (ardoise)",
        help="Cochez pour que les paiements via cette méthode créent une "
             "ardoise dans le module POS Crédit. Méthode de type « Compte "
             "client » : sans journal, « Identifier le client » coché.",
    )

    def _is_aite_credit_method(self):
        """
        Vrai si la méthode doit générer une ardoise.

        Seul le marqueur explicite ``is_aite_credit`` compte. Le repli sur
        « tout mode *pay_later* » est abandonné : « Note de chambre »
        (``is_room_charge``, module Note de chambre) et le « Compte client »
        standard sont aussi des modes *pay_later*, et un ticket réglé ainsi
        ouvrait une ardoise en plus du report au folio — la consommation
        était réclamée deux fois. Une note de chambre n'ouvre jamais
        d'ardoise, même cochée par erreur.
        """
        self.ensure_one()
        if getattr(self, 'is_room_charge', False):
            return False
        return bool(self.is_aite_credit)

    @api.model
    def _load_pos_data_fields(self, config_id):
        """Charge le marqueur dans la caisse : « Mettre sur ardoise » doit
        viser la méthode ardoise, pas le premier mode « payer plus tard »
        venu (qui peut être « Note de chambre »)."""
        fields_list = super()._load_pos_data_fields(config_id)
        if fields_list and 'is_aite_credit' not in fields_list:
            fields_list = list(fields_list) + ['is_aite_credit']
        return fields_list
