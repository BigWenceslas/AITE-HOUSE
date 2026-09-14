# -*- coding: utf-8 -*-
"""
Report des consommations POS au folio du séjour (« note de chambre »).

Chemin nominal : commande réglée avec un moyen de paiement marqué
« Note de chambre » + client identifié + un seul folio ouvert → ligne de
service créée sur le folio, idempotente (``folio_line_id``).

Tout cas ambigu (pas de client, zéro ou plusieurs folios ouverts) part
en file d'attente ``aite.roomcharge.pending`` : la réception tranche.

Les décisions sont des fonctions **pures** (extraites et exécutées par
les tests) : ``_room_charge_amount`` (somme des paiements marqués) et
``_match_decision`` (report direct ou file d'attente).
"""
import logging

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)

_PAID_STATES = ('paid', 'done', 'invoiced')


class PosOrder(models.Model):
    _inherit = 'pos.order'

    aite_folio_line_id = fields.Many2one(
        'aite.hotel.folio.line', string="Ligne de folio (note de chambre)",
        readonly=True, copy=False,
    )
    aite_roomcharge_pending_id = fields.Many2one(
        'aite.roomcharge.pending', string="Note de chambre en attente",
        readonly=True, copy=False,
    )

    # ------------------------------------------------------------------
    # Calcul pur (extrait et exécuté tel quel par les tests)
    # ------------------------------------------------------------------

    @staticmethod
    def _room_charge_amount(pairs):
        """
        Montant total « note de chambre » d'une commande.

        :param pairs: liste de (is_room_charge, amount)
        :returns: somme des montants dont le moyen est marqué.
        """
        total = 0.0
        for (flag, amount) in pairs:
            if flag:
                total += amount or 0.0
        return total

    @staticmethod
    def _match_decision(has_partner, open_folio_count):
        """
        Décision de rattachement.

        :returns: 'post' (report direct), sinon 'pending' avec le motif
            implicite (client absent, aucun folio, plusieurs folios).
        """
        if not has_partner:
            return 'pending'
        if open_folio_count == 1:
            return 'post'
        return 'pending'

    @staticmethod
    def _pos_folio_line_vals(folio_id, product_id, label, date_str,
                             amount):
        """Contrat de ligne du PMS : service, article requis, qté 1."""
        return {
            'folio_id': folio_id,
            'line_type': 'service',
            'product_id': product_id,
            'name': label,
            'date': date_str,
            'quantity': 1,
            'price_unit': amount,
        }

    # ------------------------------------------------------------------
    # Accroches (triple, comme Crédit clients v2)
    # ------------------------------------------------------------------

    def _aite_process_room_charge(self):
        Pending = self.env['aite.roomcharge.pending']
        for order in self:
            if order.aite_folio_line_id or order.aite_roomcharge_pending_id:
                continue  # idempotence
            if order.state not in _PAID_STATES:
                continue
            pairs = [(p.payment_method_id.is_room_charge, p.amount)
                     for p in order.payment_ids]
            amount = order._room_charge_amount(pairs)
            if amount <= 0:
                continue

            folios = self.env['aite.hotel.folio']
            if order.partner_id:
                folios = folios.search([
                    ('partner_id', '=', order.partner_id.id),
                    ('state', '=', 'open'),
                    ('company_id', '=', order.company_id.id),
                ])
            decision = order._match_decision(
                bool(order.partner_id), len(folios))

            if decision == 'post':
                order._aite_post_to_folio(folios, amount)
            else:
                reason = (_("Client non identifié")
                          if not order.partner_id
                          else _("Aucun folio ouvert")
                          if not folios
                          else _("%(n)s folios ouverts", n=len(folios)))
                order.aite_roomcharge_pending_id = Pending.create({
                    'order_id': order.id,
                    'partner_id': order.partner_id.id or False,
                    'amount': amount,
                    'note': reason,
                }).id
                _logger.info(
                    "Note de chambre en attente : %s (%s, %.0f).",
                    order.name, reason, amount)
        return True

    def _aite_post_to_folio(self, folio, amount):
        self.ensure_one()
        product = self.company_id.aite_roomcharge_product_id
        if not product:
            product = self.env.ref(
                'aite_hotel_pos_link.product_roomcharge_pos',
                raise_if_not_found=False)
        if not product:
            # Pas d'article configuré : file d'attente plutôt que perte.
            self.aite_roomcharge_pending_id = \
                self.env['aite.roomcharge.pending'].create({
                    'order_id': self.id,
                    'partner_id': self.partner_id.id or False,
                    'amount': amount,
                    'note': _("Article de report non configuré"),
                }).id
            return False
        vals = self._pos_folio_line_vals(
            folio.id, product.id,
            _("POS %(ref)s", ref=self.name),
            fields.Date.to_string(fields.Date.context_today(self)),
            amount)
        line = self.env['aite.hotel.folio.line'].create(vals)
        self.aite_folio_line_id = line.id
        _logger.info(
            "Note de chambre : %s → folio %s (%.0f).",
            self.name, folio.name, amount)
        return True

    @api.model_create_multi
    def create(self, vals_list):
        orders = super().create(vals_list)
        orders._aite_process_room_charge()
        return orders

    def write(self, vals):
        res = super().write(vals)
        if 'state' in vals or 'partner_id' in vals:
            self._aite_process_room_charge()
        return res

    @api.model
    def _process_order(self, order, existing_order):
        order_id = super()._process_order(order, existing_order)
        if order_id:
            self.browse(order_id)._aite_process_room_charge()
        return order_id
