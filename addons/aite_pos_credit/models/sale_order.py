# -*- coding: utf-8 -*-
import logging
from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    """
    Extension commande de vente : mise sur ardoise (vente à crédit).

    Toutes les ventes ne passent pas par le POS (événements, livraisons,
    ventes en gros au voisinage) : ce flux crée la même ardoise que le
    POS, suivie dans le même tableau de bord et remboursée par le même
    circuit (espèces / MTN MoMo / Orange Money).

    Deux chemins créent l'ardoise :

    1. **À la confirmation** — cochez « Mettre sur ardoise » sur le devis
       (onglet *Ardoise AITE*) ; à la confirmation, une ardoise est créée
       pour le total moins l'acompte éventuellement reçu comptant.
    2. **Manuel** — bouton « Mettre sur ardoise » sur une commande déjà
       confirmée (rattrapage).

    L'ardoise porte ``source='sale'`` : dans le tableau de bord, le filtre
    « Origine » permet de suivre chaque canal ou les deux ensemble.
    """
    _inherit = 'sale.order'

    aite_credit_id = fields.Many2one(
        'aite.pos.credit', string="Ardoise générée", readonly=True,
        copy=False, index=True,
    )
    aite_put_on_credit = fields.Boolean(
        string="Mettre sur ardoise à la confirmation", copy=False,
        help="À la confirmation de la commande, le total (moins l'acompte "
             "comptant éventuel) sera porté sur l'ardoise du client.",
    )
    aite_credit_down_payment = fields.Monetary(
        string="Acompte reçu comptant", copy=False,
        help="Part déjà réglée immédiatement (espèces, Mobile Money…) : "
             "elle est déduite du montant mis sur ardoise.",
    )

    # ------------------------------------------------------------------
    # Calcul pur (extrait et exécuté tel quel par les tests)
    # ------------------------------------------------------------------

    @staticmethod
    def _aite_sale_credit_amount(amount_total, down_payment):
        """
        Montant à porter sur ardoise pour une vente = total − acompte.

        :raises ValueError: si le résultat n'est pas strictement positif
            (acompte supérieur ou égal au total, ou commande vide).
        """
        amount = (amount_total or 0.0) - (down_payment or 0.0)
        if amount <= 0:
            raise ValueError(
                "Le montant à mettre sur ardoise doit être strictement "
                "positif (acompte trop élevé ou commande vide).")
        if (down_payment or 0.0) < 0:
            raise ValueError("L'acompte ne peut pas être négatif.")
        return amount

    # ------------------------------------------------------------------
    # Hook de confirmation
    # ------------------------------------------------------------------

    def action_confirm(self):
        res = super().action_confirm()
        for order in self:
            if order.aite_put_on_credit and not order.aite_credit_id:
                order._aite_create_credit_from_sale()
        return res

    def _aite_create_credit_from_sale(self):
        """Crée l'ardoise pour cette vente. Idempotent."""
        self.ensure_one()
        if self.aite_credit_id:
            return self.aite_credit_id
        if not self.partner_id:
            raise UserError(
                _("Un client doit être sélectionné pour une vente à "
                  "crédit."))
        try:
            amount = self._aite_sale_credit_amount(
                self.amount_total, self.aite_credit_down_payment)
        except ValueError as e:
            raise UserError(str(e)) from e

        credit = self.env['aite.pos.credit'].sudo().create({
            'partner_id': self.partner_id.id,
            'source': 'sale',
            'sale_order_id': self.id,
            'company_id': self.company_id.id,
            'amount_total': amount,
            'date_open': fields.Date.context_today(self),
            'note': _("Commande de vente %s", self.name),
        })
        self.aite_credit_id = credit.id
        _logger.info(
            "POS Crédit : ardoise %s de %s créée pour la vente %s "
            "(acompte comptant : %s).",
            credit.name, amount, self.name,
            self.aite_credit_down_payment or 0.0)
        return credit

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def action_aite_put_on_credit(self):
        """Rattrapage : met sur ardoise une commande déjà confirmée."""
        self.ensure_one()
        if self.aite_credit_id:
            raise UserError(
                _("Cette commande est déjà sur ardoise (%s).",
                  self.aite_credit_id.name))
        if self.state not in ('sale', 'done'):
            raise UserError(
                _("Confirmez la commande avant de la mettre sur ardoise "
                  "(ou cochez « Mettre sur ardoise à la confirmation »)."))
        self._aite_create_credit_from_sale()
        return self.action_aite_view_credit()

    def action_aite_view_credit(self):
        self.ensure_one()
        if not self.aite_credit_id:
            raise UserError(_("Aucune ardoise liée à cette commande."))
        return {
            'type': 'ir.actions.act_window',
            'name': _("Ardoise"),
            'res_model': 'aite.pos.credit',
            'res_id': self.aite_credit_id.id,
            'view_mode': 'form',
        }
