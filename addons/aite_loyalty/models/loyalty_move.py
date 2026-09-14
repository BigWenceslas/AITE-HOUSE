# -*- coding: utf-8 -*-
import logging
import math
from datetime import date

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)

ORIGINS = [
    ('pos', "Restaurant / Boutique (POS)"),
    ('hotel', "Hébergement (folio)"),
    ('slot_space', "Espace VIP / VVIP"),
    ('slot_spa', "SPA"),
    ('slot_hair', "Coiffure"),
    ('slot_pressing', "Pressing"),
    ('manual', "Ajustement manuel"),
]

TIERS = [
    ('standard', "Standard"),
    ('vip', "VIP"),
    ('vvip', "VVIP"),
]


class LoyaltyMove(models.Model):
    """
    Grand livre de fidélité : un mouvement de points par événement.

    Chaque gain porte son origine détaillée (POS, folio, famille de
    prestation) et le montant de base — c'est ce grand livre qui
    alimente à la fois le solde de points et la segmentation (dépenses,
    visites = jours distincts, diversité = origines distinctes).
    """
    _name = 'aite.loyalty.move'
    _description = "Mouvement de fidélité"
    _order = 'date desc, id desc'

    partner_id = fields.Many2one(
        'res.partner', string="Client", required=True, index=True,
        ondelete='cascade',
    )
    company_id = fields.Many2one(
        'res.company', string="Société", required=True,
        default=lambda self: self.env.company, index=True,
    )
    currency_id = fields.Many2one(
        related='company_id.currency_id', readonly=True)
    date = fields.Date(
        string="Date", required=True, index=True,
        default=fields.Date.context_today,
    )
    points = fields.Integer(string="Points", required=True)
    amount_base = fields.Monetary(
        string="Montant de base", currency_field='currency_id',
        help="Montant de la transaction ayant généré les points.",
    )
    origin_detail = fields.Selection(
        selection=ORIGINS, string="Origine", required=True, index=True,
    )
    ref = fields.Char(string="Référence", index=True)
    note = fields.Char(string="Note")

    def _sync_partner_balance(self, partners):
        for partner in partners:
            partner._compute_loyalty_points()

    @api.model_create_multi
    def create(self, vals_list):
        moves = super().create(vals_list)
        self._sync_partner_balance(moves.mapped('partner_id'))
        return moves

    def unlink(self):
        partners = self.mapped('partner_id')
        res = super().unlink()
        self._sync_partner_balance(partners)
        return res


class LoyaltyEngine(models.AbstractModel):
    """
    Moteur de fidélité : attribution des points et segmentation.

    Les deux règles métier sont des fonctions **pures** (extraites et
    exécutées par les tests) :

    * ``_points_for`` — barème : ``floor(montant / 1000 × taux)``, zéro
      sous le montant minimum ;
    * ``_tier_for`` — statut : VVIP si dépenses ET visites ET diversité
      atteignent leurs seuils ; sinon VIP si dépenses ET visites ;
      sinon Standard.
    """
    _name = 'aite.loyalty.engine'
    _description = "Moteur de fidélité AITE"

    # ------------------------------------------------------------------
    # Calcul pur (extrait et exécuté tel quel par les tests)
    # ------------------------------------------------------------------

    @staticmethod
    def _points_for(amount, rate_per_1000, min_amount):
        """
        Points gagnés pour une transaction.

        Zéro si le montant est sous le minimum ; sinon partie entière de
        (montant / 1000 × taux). Jamais négatif.
        """
        amt = amount or 0.0
        if amt < (min_amount or 0.0) or amt <= 0:
            return 0
        pts = math.floor(amt / 1000.0 * (rate_per_1000 or 0.0))
        return max(0, int(pts))

    @staticmethod
    def _tier_for(spend, visits, domains, cfg):
        """
        Statut client selon les trois critères du cahier des charges.

        :param cfg: dict {vip_spend, vip_visits, vvip_spend,
            vvip_visits, vvip_domains}
        """
        if (spend >= cfg.get('vvip_spend', float('inf'))
                and visits >= cfg.get('vvip_visits', float('inf'))
                and domains >= cfg.get('vvip_domains', float('inf'))):
            return 'vvip'
        if (spend >= cfg.get('vip_spend', float('inf'))
                and visits >= cfg.get('vip_visits', float('inf'))):
            return 'vip'
        return 'standard'

    # ------------------------------------------------------------------
    # Attribution
    # ------------------------------------------------------------------

    def _cfg(self, company=None):
        c = company or self.env.company
        return {
            'rate': c.aite_loyalty_rate_per_1000 or 0.0,
            'min_amount': c.aite_loyalty_min_amount or 0.0,
            'window': c.aite_loyalty_window_months or 12,
            'vip_spend': c.aite_loyalty_vip_min_spend or 0.0,
            'vip_visits': c.aite_loyalty_vip_min_visits or 0,
            'vvip_spend': c.aite_loyalty_vvip_min_spend or 0.0,
            'vvip_visits': c.aite_loyalty_vvip_min_visits or 0,
            'vvip_domains': c.aite_loyalty_vvip_min_domains or 0,
        }

    @api.model
    def award(self, partner, amount, origin_detail, ref="",
              company=None, when=None):
        """
        Crée le mouvement de points pour une transaction. Retourne le
        mouvement (vide si zéro point) — l'appelant stocke l'ID pour
        l'idempotence.
        """
        company = company or self.env.company
        cfg = self._cfg(company)
        points = self._points_for(amount, cfg['rate'], cfg['min_amount'])
        if points <= 0 or not partner:
            return self.env['aite.loyalty.move']
        move = self.env['aite.loyalty.move'].sudo().create({
            'partner_id': partner.id,
            'company_id': company.id,
            'date': when or fields.Date.context_today(self),
            'points': points,
            'amount_base': amount,
            'origin_detail': origin_detail,
            'ref': ref,
        })
        _logger.info(
            "Fidélité : +%s pts pour %s (%s, %s).",
            points, partner.name, origin_detail, ref)
        return move

    # ------------------------------------------------------------------
    # Segmentation (cron quotidien)
    # ------------------------------------------------------------------

    @api.model
    def recompute_tiers(self, partner_ids=None):
        """
        Recalcule le statut des clients sur la fenêtre glissante :
        dépenses = somme des montants de base ; visites = jours
        distincts ; diversité = origines distinctes (hors manuel).
        """
        Move = self.env['aite.loyalty.move']
        for company in self.env['res.company'].search([]):
            cfg = self._cfg(company)
            since = date.today() - relativedelta(months=cfg['window'])
            domain = [
                ('company_id', '=', company.id),
                ('date', '>=', since),
                ('points', '>', 0),
            ]
            if partner_ids:
                domain.append(('partner_id', 'in', list(partner_ids)))
            moves = Move.search(domain)

            data = {}
            for mv in moves:
                d = data.setdefault(mv.partner_id.id, {
                    'spend': 0.0, 'days': set(), 'domains': set(),
                })
                d['spend'] += mv.amount_base or 0.0
                d['days'].add(mv.date)
                if mv.origin_detail != 'manual':
                    d['domains'].add(mv.origin_detail)

            partners = self.env['res.partner'].browse(list(data.keys()))
            changed = 0
            for partner in partners:
                d = data[partner.id]
                tier = self._tier_for(
                    d['spend'], len(d['days']), len(d['domains']), cfg)
                if partner.loyalty_tier != tier:
                    partner.write({
                        'loyalty_tier': tier,
                        'loyalty_tier_date': fields.Date.today(),
                    })
                    changed += 1
            # Rétrogradation : clients segmentés sans activité fenêtre
            stale_domain = [
                ('loyalty_tier', 'in', ('vip', 'vvip')),
            ]
            if partner_ids:
                stale_domain.append(('id', 'in', list(partner_ids)))
            for partner in self.env['res.partner'].search(stale_domain):
                if partner.id not in data:
                    partner.write({
                        'loyalty_tier': 'standard',
                        'loyalty_tier_date': fields.Date.today(),
                    })
                    changed += 1
            if changed:
                _logger.info(
                    "Fidélité : %s statut(s) recalculé(s) (%s).",
                    changed, company.name)
        return True
