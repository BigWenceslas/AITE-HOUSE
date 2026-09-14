# -*- coding: utf-8 -*-
from datetime import date, datetime, timedelta

from odoo import api, fields, models

_POS_PAID_STATES = ('paid', 'done', 'invoiced')

_POLE_COLORS = {
    'hotel': '#714B67',   # violet AITE
    'pos': '#185FA5',     # bleu info
    'slots': '#0F6E56',   # teal
}

_POLE_LABELS = {
    'hotel': "Hébergement",
    'pos': "Restauration & boutique",
    'slots': "Prestations",
}


class ExecDashboard(models.AbstractModel):
    """
    Fournisseur du tableau de bord Direction — consolidation des trois
    pôles du complexe.

    Sources (une par pôle, jamais deux chiffres pour la même chose) :

    * hébergement : folios facturés / soldés, datés par le check-out
      réel du séjour (sinon prévu) ; occupation et ADR relus depuis le
      provider du PMS (mêmes chiffres que son propre tableau de bord) ;
    * restauration & boutique : commandes POS réglées (date de
      commande) ;
    * prestations : réservations de créneaux réalisées (date de début).

    Fidélité : détection dynamique du module (aucune dépendance dure).
    Les répartitions (``_mix_rows``) et le découpage mensuel
    (``_last_months``, ``_month_key``) sont des fonctions pures testées.
    """
    _name = 'aite.exec.dashboard'
    _description = "Tableau de bord Direction — Data Provider"

    # ------------------------------------------------------------------
    # Calcul pur (extrait et exécuté tel quel par les tests)
    # ------------------------------------------------------------------

    @staticmethod
    def _mix_rows(hotel, pos, slots):
        """
        Répartition du CA par pôle, avec parts en % (une décimale).
        Les pôles à zéro sont conservés (lisibilité direction).
        """
        total = (hotel or 0.0) + (pos or 0.0) + (slots or 0.0)
        rows = []
        for key, amount in (('hotel', hotel or 0.0),
                            ('pos', pos or 0.0),
                            ('slots', slots or 0.0)):
            pct = (amount / total * 100.0) if total else 0.0
            rows.append({
                'key': key,
                'amount': amount,
                'pct': round(pct, 1),
            })
        rows.sort(key=lambda r: -r['amount'])
        return rows

    @staticmethod
    def _month_key(d):
        """date → 'YYYY-MM' (clé de bucket mensuel)."""
        return '%04d-%02d' % (d.year, d.month)

    @staticmethod
    def _last_months(n, today):
        """
        Les ``n`` derniers mois (mois courant inclus), du plus ancien au
        plus récent : [(clé 'YYYY-MM', 1er du mois, 1er du mois
        suivant)].
        """
        months = []
        year, month = today.year, today.month
        for _i in range(n):
            months.append((year, month))
            month -= 1
            if month == 0:
                month = 12
                year -= 1
        months.reverse()
        out = []
        for (y, m) in months:
            start = date(y, m, 1)
            ny, nm = (y + 1, 1) if m == 12 else (y, m + 1)
            out.append(('%04d-%02d' % (y, m), start, date(ny, nm, 1)))
        return out

    # ------------------------------------------------------------------
    # Helpers de période
    # ------------------------------------------------------------------

    def _parse_period(self, date_from, date_to):
        try:
            dt_from = datetime.strptime(date_from, '%Y-%m-%d').date()
            dt_to = datetime.strptime(date_to, '%Y-%m-%d').date()
        except (TypeError, ValueError):
            today = fields.Date.context_today(self)
            dt_from = today.replace(day=1)
            dt_to = today
        if dt_from > dt_to:
            dt_from, dt_to = dt_to, dt_from
        return dt_from, dt_to

    @staticmethod
    def _day_bounds(dt_from, dt_to):
        d0 = fields.Datetime.to_string(
            datetime.combine(dt_from, datetime.min.time()))
        d1 = fields.Datetime.to_string(
            datetime.combine(dt_to, datetime.max.time()))
        return d0, d1

    # ------------------------------------------------------------------
    # Sources par pôle (une seule définition chacune)
    # ------------------------------------------------------------------

    def _hotel_folios(self, dt_from, dt_to):
        """Folios facturés / soldés dont le séjour se termine dans la
        période (check-out réel, sinon prévu)."""
        folios = self.env['aite.hotel.folio'].search([
            ('company_id', '=', self.env.company.id),
            ('state', 'in', ('invoiced', 'paid')),
        ])
        d0 = datetime.combine(dt_from, datetime.min.time())
        d1 = datetime.combine(dt_to, datetime.max.time())
        keep = folios.browse()
        for folio in folios:
            res = folio.reservation_id
            out_dt = res.actual_checkout or res.checkout_date
            if out_dt and d0 <= out_dt <= d1:
                keep |= folio
        return keep

    def _hotel_revenue(self, dt_from, dt_to):
        return sum(self._hotel_folios(dt_from, dt_to)
                   .mapped('amount_total'))

    def _pos_orders(self, dt_from, dt_to):
        d0, d1 = self._day_bounds(dt_from, dt_to)
        return self.env['pos.order'].search([
            ('company_id', '=', self.env.company.id),
            ('state', 'in', _POS_PAID_STATES),
            ('date_order', '>=', d0), ('date_order', '<=', d1),
        ])

    def _slot_bookings(self, dt_from, dt_to):
        d0, d1 = self._day_bounds(dt_from, dt_to)
        return self.env['aite.slot.booking'].search([
            ('company_id', '=', self.env.company.id),
            ('state', '=', 'done'),
            ('start', '>=', d0), ('start', '<=', d1),
        ])

    def _has_loyalty(self):
        return 'aite.loyalty.move' in self.env

    def _loyalty_points(self, dt_from, dt_to):
        if not self._has_loyalty():
            return 0
        moves = self.env['aite.loyalty.move'].search([
            ('company_id', '=', self.env.company.id),
            ('date', '>=', dt_from), ('date', '<=', dt_to),
            ('points', '>', 0),
        ])
        return sum(moves.mapped('points'))

    # ------------------------------------------------------------------
    # API
    # ------------------------------------------------------------------

    @api.model
    def get_meta(self):
        company = self.env.company
        today = fields.Date.context_today(self)
        return {
            'company_name': company.name,
            'currency_symbol': company.currency_id.symbol or 'F',
            'has_loyalty': self._has_loyalty(),
            'today': fields.Date.to_string(today),
            'month_start': fields.Date.to_string(today.replace(day=1)),
            'poles': [
                {'key': k, 'label': _POLE_LABELS[k],
                 'color': _POLE_COLORS[k]}
                for k in ('hotel', 'pos', 'slots')
            ],
        }

    @api.model
    def get_kpis(self, date_from, date_to):
        dt_from, dt_to = self._parse_period(date_from, date_to)

        # Hébergement
        hotel_ca = self._hotel_revenue(dt_from, dt_to)
        occupancy = 0.0
        adr = 0.0
        try:
            hk = self.env['aite.hotel.dashboard'].get_kpis(
                fields.Date.to_string(dt_from),
                fields.Date.to_string(dt_to))
            period = hk.get('period') or {}
            occupancy = period.get('occupancy') or 0.0
            adr = period.get('adr') or 0.0
        except Exception:
            pass  # le consolidé reste servi même si le PMS évolue

        # Restauration & boutique
        orders = self._pos_orders(dt_from, dt_to)
        pos_ca = sum(orders.mapped('amount_total'))
        tickets = len(orders)
        basket = pos_ca / tickets if tickets else 0.0

        # Prestations
        bookings = self._slot_bookings(dt_from, dt_to)
        slots_ca = sum(bookings.mapped('amount'))

        total = hotel_ca + pos_ca + slots_ca
        return {
            'total_ca': total,
            'hotel_ca': hotel_ca,
            'occupancy': occupancy,
            'adr': adr,
            'pos_ca': pos_ca,
            'tickets': tickets,
            'basket': basket,
            'slots_ca': slots_ca,
            'slots_count': len(bookings),
            'points_issued': self._loyalty_points(dt_from, dt_to),
            'mix': self._mix_rows(hotel_ca, pos_ca, slots_ca),
        }

    @api.model
    def get_evolution(self, months=6):
        """Trois séries mensuelles (hébergement / POS / prestations)."""
        today = fields.Date.context_today(self)
        buckets = self._last_months(months, today)
        labels = []
        hotel_s, pos_s, slots_s = [], [], []
        for (key, start, nxt) in buckets:
            end = nxt - timedelta(days=1)
            labels.append(key)
            hotel_s.append(self._hotel_revenue(start, end))
            pos_s.append(sum(
                self._pos_orders(start, end).mapped('amount_total')))
            slots_s.append(sum(
                self._slot_bookings(start, end).mapped('amount')))
        return {
            'labels': labels,
            'series': [
                {'key': 'hotel', 'label': _POLE_LABELS['hotel'],
                 'color': _POLE_COLORS['hotel'], 'data': hotel_s},
                {'key': 'pos', 'label': _POLE_LABELS['pos'],
                 'color': _POLE_COLORS['pos'], 'data': pos_s},
                {'key': 'slots', 'label': _POLE_LABELS['slots'],
                 'color': _POLE_COLORS['slots'], 'data': slots_s},
            ],
        }
