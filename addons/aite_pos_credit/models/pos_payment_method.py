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
             "ardoise dans le module POS Crédit. Méthode généralement de "
             "type « Payer plus tard » (compte client).",
    )

    def _is_aite_credit_method(self):
        """
        Vrai si la méthode doit générer une ardoise.

        On considère soit le marqueur explicite ``is_aite_credit``, soit une
        méthode native de type *pay_later* (selon la version, le champ peut
        être ``type == 'pay_later'`` ou ``split_transactions`` + compte
        receivable). On teste de façon défensive.
        """
        self.ensure_one()
        if self.is_aite_credit:
            return True
        # Repli : détection d'une méthode "payer plus tard" native.
        method_type = getattr(self, 'type', False)
        if method_type == 'pay_later':
            return True
        return False
