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
    # Un ticket peut donner plusieurs lignes de folio (une par jeu de
    # taxes) ; ``aite_folio_line_id`` garde la première (idempotence et
    # compatibilité), celle-ci les donne toutes.
    aite_folio_line_ids = fields.One2many(
        'aite.hotel.folio.line', 'aite_pos_order_id',
        string="Lignes de folio (note de chambre)", readonly=True,
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
                             amount, tax_ids=None):
        """Contrat de ligne du PMS : service, article requis, qté 1.

        ``amount`` est le prix unitaire au sens du folio : hors taxes, sauf
        pour les taxes « prix TTC » (``price_include``) qui y restent
        comprises — le folio les retire lui-même au calcul.
        """
        return {
            'folio_id': folio_id,
            'line_type': 'service',
            'product_id': product_id,
            'name': label,
            'date': date_str,
            'quantity': 1,
            'price_unit': amount,
            'tax_ids': [(6, 0, list(tax_ids or []))],
        }

    def _aite_room_charge_parts(self, amount):
        """
        Découpe le montant reporté par jeu de taxes du ticket.

        Le folio doit recevoir le **HT avec ses taxes** (et non le TTC rangé
        en « Services (HT) ») : la facture du séjour porte alors la bonne
        base et la bonne TVA. En paiement mixte, seule la part réglée en
        note de chambre est reportée, au prorata du ticket.

        :returns: liste de (taxes, prix unitaire pour le folio)
        """
        self.ensure_one()
        total = self.amount_total
        groups = {}
        for line in self.lines:
            taxes = line.tax_ids_after_fiscal_position
            key = tuple(sorted(taxes.ids))
            group = groups.setdefault(key, [taxes, 0.0, 0.0])
            group[1] += line.price_subtotal
            group[2] += line.price_subtotal_incl
        if not total or not groups or all(not key for key in groups):
            # Ticket sans taxe (ou sans lignes lisibles) : report tel quel.
            return [(self.env['account.tax'], amount)]
        ratio = amount / total
        parts = []
        for taxes, untaxed, taxed in groups.values():
            if not taxed:
                continue
            if not taxes:
                parts.append((taxes, taxed * ratio))
                continue
            base = untaxed * ratio
            # Une taxe « prix TTC » est retirée par le folio au calcul : on
            # la remet dans le prix unitaire pour retrouver la même base.
            res = taxes.compute_all(
                base, currency=self.currency_id, quantity=1.0,
                handle_price_include=False)
            included = sum(
                t['amount'] for t in res['taxes']
                if self.env['account.tax'].browse(t['id']).price_include)
            parts.append((taxes, base + included))
        return parts or [(self.env['account.tax'], amount)]

    # ------------------------------------------------------------------
    # Accroches (triple, comme Crédit clients v2)
    # ------------------------------------------------------------------

    def _aite_process_room_charge(self):
        # Écriture technique (cf. CLAUDE.md) : le caissier encaisse en
        # « Note de chambre » sans avoir — ni avoir à avoir — de profil
        # hôtel. Recherche du folio, ligne de folio et note en attente se
        # font donc en ``sudo()`` ; sinon la synchronisation du ticket
        # échoue (AccessError) et la caisse garde la vente en souffrance.
        Pending = self.env['aite.roomcharge.pending'].sudo()
        for order in self.sudo():
            if order.aite_folio_line_id or order.aite_roomcharge_pending_id:
                continue  # idempotence
            if order.state not in _PAID_STATES:
                continue
            pairs = [(p.payment_method_id.is_room_charge, p.amount)
                     for p in order.payment_ids]
            amount = order._room_charge_amount(pairs)
            if amount <= 0:
                continue

            folios = order.env['aite.hotel.folio']  # sudo (voir plus haut)
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
        # Écriture technique en ``sudo()`` : appelée pour le caissier (sans
        # profil hôtel) comme pour la réception qui tranche la file
        # d'attente (sans droits sur la caisse). Le contrôle d'accès porte
        # sur le geste d'origine, pas sur cette mécanique de report.
        order = self.sudo()
        product = order.company_id.aite_roomcharge_product_id
        if not product:
            product = self.env.ref(
                'aite_hotel_pos_link.product_roomcharge_pos',
                raise_if_not_found=False)
        if not product:
            # Pas d'article configuré : file d'attente plutôt que perte.
            order.aite_roomcharge_pending_id = \
                self.env['aite.roomcharge.pending'].sudo().create({
                    'order_id': order.id,
                    'partner_id': order.partner_id.id or False,
                    'amount': amount,
                    'note': _("Article de report non configuré"),
                }).id
            return False
        label = _("POS %(ref)s", ref=order.name)
        date_str = fields.Date.to_string(fields.Date.context_today(order))
        vals_list = []
        # Une ligne par jeu de taxes : HT + taxes, comme sur le ticket.
        for taxes, price_unit in order._aite_room_charge_parts(amount):
            vals = order._pos_folio_line_vals(
                folio.id, product.id, label, date_str, price_unit,
                tax_ids=taxes.ids)
            vals['aite_pos_order_id'] = order.id
            vals_list.append(vals)
        lines = self.env['aite.hotel.folio.line'].sudo().create(vals_list)
        order.aite_folio_line_id = lines[:1].id
        _logger.info(
            "Note de chambre : %s → folio %s (%.0f).",
            order.name, folio.name, amount)
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


class HotelFolioLine(models.Model):
    _inherit = 'aite.hotel.folio.line'

    aite_pos_order_id = fields.Many2one(
        'pos.order', string="Ticket de caisse (note de chambre)",
        readonly=True, copy=False, index='btree_not_null',
        ondelete='set null',
    )
