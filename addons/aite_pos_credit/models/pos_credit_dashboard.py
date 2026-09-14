# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from collections import defaultdict

from odoo import api, fields, models, _


class PosCreditDashboard(models.AbstractModel):
    """
    Fournisseur de données pour le tableau de bord de recouvrement.

    Expose des méthodes RPC consommées par le dashboard OWL : KPIs globaux
    (avec comparaison vs période précédente), balance âgée, top débiteurs,
    répartition des remboursements par moyen, remboursements journaliers,
    encours par caisse et évolution.

    Filtres transverses :
    * ``date_from`` / ``date_to`` (``YYYY-MM-DD``) — appliqués aux flux
      (remboursements, ouvertures) ; l'encours reste une photo présente.
    * ``config_id`` — restreint à une caisse (via la caisse d'origine de
      l'ardoise). ``None`` / 0 = toutes les caisses.
    * ``source`` — restreint au canal d'origine : ``'pos'`` (Point de
      vente) ou ``'sale'`` (module Ventes). ``None`` = les deux flux
      ensemble. Combiner une caisse avec ``source='sale'`` donne
      logiquement un résultat vide (les ventes hors POS n'ont pas de
      caisse).
    """
    _name = 'aite.pos.credit.dashboard'
    _description = "POS Crédit — Data Provider (recouvrement)"

    # Palette stable des caisses (alignée sur le module Analytics).
    _CAISSE_PALETTE = [
        '#714B67', '#185FA5', '#3B6D11', '#854F0B',
        '#A32D2D', '#0F6E56', '#5B4B8A', '#B0655A',
    ]
    # Couleur dédiée du canal « Ventes (hors POS) » dans les répartitions.
    _SALE_COLOR = '#46414E'

    # ------------------------------------------------------------------
    # Helpers
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

    def _company_currency(self):
        return self.env.company.currency_id

    def _credit_domain(self, config_id=None, states=('open',), source=None):
        domain = [('state', 'in', list(states))]
        if config_id:
            domain.append(('config_id', '=', int(config_id)))
        if source:
            domain.append(('source', '=', source))
        return domain

    def _payment_domain(self, dt_from, dt_to, config_id=None, source=None):
        domain = [
            ('state', '=', 'posted'),
            ('date', '>=', dt_from),
            ('date', '<=', dt_to),
        ]
        if config_id:
            domain.append(('credit_id.config_id', '=', int(config_id)))
        if source:
            domain.append(('credit_id.source', '=', source))
        return domain

    @staticmethod
    def _delta_pct(current, previous):
        """Variation en % vs période précédente ; None si non significatif."""
        if previous:
            return (current - previous) / previous * 100.0
        if current:
            return 100.0
        return 0.0

    # ------------------------------------------------------------------
    # Référentiels
    # ------------------------------------------------------------------

    @api.model
    def get_pos_configs(self):
        """Caisses disponibles, avec couleur stable pour les filtres."""
        configs = self.env['pos.config'].search([])
        palette = self._CAISSE_PALETTE
        return [{
            'id': c.id,
            'name': c.name,
            'color': palette[i % len(palette)],
        } for i, c in enumerate(configs)]

    @api.model
    def get_dashboard_meta(self):
        company = self.env.company
        return {
            'currency_id': company.currency_id.id,
            'currency_symbol': company.currency_id.symbol,
            'company_name': company.name,
        }

    # ------------------------------------------------------------------
    # KPIs (avec comparaison N-1)
    # ------------------------------------------------------------------

    @api.model
    def get_kpis(self, date_from, date_to, config_id=None, source=None):
        """
        KPIs principaux du recouvrement, avec deltas vs période précédente
        de même durée (None quand la comparaison n'a pas de sens, par
        exemple sur « Toute la période »).
        """
        Credit = self.env['aite.pos.credit']
        Payment = self.env['aite.pos.credit.payment']
        dt_from, dt_to = self._parse_period(date_from, date_to)
        today = fields.Date.context_today(self)

        # --- Encours (photo présente) ---
        open_credits = Credit.search(self._credit_domain(config_id,
                                                         source=source))
        outstanding = sum(open_credits.mapped('amount_residual'))
        debtor_count = len(set(open_credits.mapped('partner_id').ids))
        pos_outstanding = sum(
            c.amount_residual for c in open_credits if c.source != 'sale')
        sale_outstanding = sum(
            c.amount_residual for c in open_credits if c.source == 'sale')

        late_threshold = Credit.AGE_THRESHOLD_LATE
        late_amount = 0.0
        for c in open_credits:
            age = (today - c.date_open).days if c.date_open else 0
            if age >= late_threshold:
                late_amount += c.amount_residual

        oldest_age = 0
        oldest_partner = ""
        oldest_amount = 0.0
        if open_credits:
            oldest = min(open_credits, key=lambda c: c.date_open or today)
            oldest_age = (today - oldest.date_open).days if oldest.date_open else 0
            oldest_partner = oldest.partner_id.name or ""
            oldest_amount = oldest.amount_residual

        # --- Flux de la période courante ---
        period_payments = Payment.search(
            self._payment_domain(dt_from, dt_to, config_id, source))
        recovered = sum(period_payments.mapped('amount'))

        opened_domain = [
            ('date_open', '>=', dt_from), ('date_open', '<=', dt_to),
        ]
        if config_id:
            opened_domain.append(('config_id', '=', int(config_id)))
        if source:
            opened_domain.append(('source', '=', source))
        opened_credits = Credit.search(opened_domain)
        opened_amount = sum(opened_credits.mapped('amount_total'))
        new_credits = len(opened_credits)

        denom = outstanding + recovered
        recovery_rate = (recovered / denom * 100.0) if denom else 0.0
        avg_ardoise = (outstanding / debtor_count) if debtor_count else 0.0
        net_flow = opened_amount - recovered

        # --- Ardoises réglées sur la période + délai moyen ---
        paid_domain = self._credit_domain(config_id, states=('paid',),
                                          source=source)
        paid_credits = Credit.search(paid_domain)
        settled_count = 0
        settle_days = []
        for c in paid_credits:
            posted = c.payment_ids.filtered(lambda p: p.state == 'posted')
            if not posted:
                continue
            last_date = max(posted.mapped('date'))
            if last_date and dt_from <= last_date <= dt_to:
                settled_count += 1
                if c.date_open:
                    settle_days.append((last_date - c.date_open).days)
        avg_settle_days = (
            sum(settle_days) / len(settle_days)) if settle_days else 0.0

        # --- Période précédente (même durée) pour les deltas ---
        span = (dt_to - dt_from).days
        recovered_delta = None
        opened_delta = None
        if span <= 400:  # pas de comparaison sur « toute la période »
            prev_to = dt_from - timedelta(days=1)
            prev_from = prev_to - timedelta(days=span)

            prev_payments = Payment.search(
                self._payment_domain(prev_from, prev_to, config_id, source))
            prev_recovered = sum(prev_payments.mapped('amount'))

            prev_opened_domain = [
                ('date_open', '>=', prev_from), ('date_open', '<=', prev_to),
            ]
            if config_id:
                prev_opened_domain.append(('config_id', '=', int(config_id)))
            if source:
                prev_opened_domain.append(('source', '=', source))
            prev_opened = Credit.search(prev_opened_domain)
            prev_opened_amount = sum(prev_opened.mapped('amount_total'))

            recovered_delta = self._delta_pct(recovered, prev_recovered)
            opened_delta = self._delta_pct(opened_amount, prev_opened_amount)

        return {
            'outstanding': outstanding,
            'pos_outstanding': pos_outstanding,
            'sale_outstanding': sale_outstanding,
            'debtor_count': debtor_count,
            'recovered': recovered,
            'recovered_delta': recovered_delta,
            'recovery_rate': recovery_rate,
            'avg_ardoise': avg_ardoise,
            'late_amount': late_amount,
            'late_pct': (late_amount / outstanding * 100.0) if outstanding else 0.0,
            'new_credits': new_credits,
            'opened_amount': opened_amount,
            'opened_delta': opened_delta,
            'net_flow': net_flow,
            'payment_count': len(period_payments),
            'settled_count': settled_count,
            'avg_settle_days': avg_settle_days,
            'oldest_age': oldest_age,
            'oldest_partner': oldest_partner,
            'oldest_amount': oldest_amount,
            'currency_id': self._company_currency().id,
        }

    # ------------------------------------------------------------------
    # Répartitions & séries
    # ------------------------------------------------------------------

    @api.model
    def get_aging(self, config_id=None, source=None):
        """Balance âgée de l'encours ouvert, en 4 tranches d'ancienneté."""
        Credit = self.env['aite.pos.credit']
        today = fields.Date.context_today(self)
        open_credits = Credit.search(self._credit_domain(config_id,
                                                         source=source))

        buckets = [
            {'label': "0–30 j", 'min': 0, 'max': 30, 'amount': 0.0, 'count': 0},
            {'label': "30–60 j", 'min': 30, 'max': 60, 'amount': 0.0, 'count': 0},
            {'label': "60–90 j", 'min': 60, 'max': 90, 'amount': 0.0, 'count': 0},
            {'label': "+90 j", 'min': 90, 'max': 10 ** 9, 'amount': 0.0, 'count': 0},
        ]
        for c in open_credits:
            age = (today - c.date_open).days if c.date_open else 0
            for b in buckets:
                if b['min'] <= age < b['max']:
                    b['amount'] += c.amount_residual
                    b['count'] += 1
                    break
        return [
            {'label': b['label'], 'amount': b['amount'], 'count': b['count']}
            for b in buckets
        ]

    @api.model
    def get_caisse_breakdown(self, source=None):
        """
        Encours ouvert réparti par origine (pour le donut) : une part par
        caisse POS, plus une part « Ventes (hors POS) » pour les ardoises
        du module Ventes.
        """
        Credit = self.env['aite.pos.credit']
        domain = [('state', '=', 'open')]
        if source:
            domain.append(('source', '=', source))
        open_credits = Credit.search(domain)

        by_config = defaultdict(lambda: {'amount': 0.0, 'count': 0})
        for c in open_credits:
            if c.source == 'sale':
                key = 'sale'
                name = _("Ventes (hors POS)")
            else:
                key = c.config_id.id if c.config_id else 0
                name = c.config_id.name if c.config_id else _("Sans caisse")
            by_config[key]['amount'] += c.amount_residual
            by_config[key]['count'] += 1
            by_config[key]['name'] = name

        configs = {c['id']: c for c in self.get_pos_configs()}
        rows = []
        for key, d in by_config.items():
            if key == 'sale':
                color = self._SALE_COLOR
            else:
                color = configs.get(key, {}).get('color', '#888780')
            rows.append({
                'config_id': key,
                'name': d['name'],
                'amount': d['amount'],
                'count': d['count'],
                'color': color,
            })
        rows.sort(key=lambda r: r['amount'], reverse=True)
        return rows

    @api.model
    def get_daily_recoveries(self, date_from, date_to, config_id=None,
                             source=None):
        """
        Remboursements agrégés par jour (période courte) ou par mois
        (période longue), pour le graphe en barres.
        """
        Payment = self.env['aite.pos.credit.payment']
        dt_from, dt_to = self._parse_period(date_from, date_to)
        payments = Payment.search(
            self._payment_domain(dt_from, dt_to, config_id, source))

        span = (dt_to - dt_from).days + 1
        MONTHS_FR = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin',
                     'Juil', 'Août', 'Sep', 'Oct', 'Nov', 'Déc']

        if span <= 62:
            # Buckets journaliers, zéros compris.
            totals = defaultdict(float)
            for p in payments:
                totals[p.date] += p.amount
            rows = []
            day = dt_from
            while day <= dt_to:
                rows.append({
                    'label': day.strftime('%d/%m'),
                    'amount': totals.get(day, 0.0),
                })
                day += timedelta(days=1)
            return rows

        # Buckets mensuels.
        totals = defaultdict(float)
        for p in payments:
            totals[(p.date.year, p.date.month)] += p.amount
        rows = []
        y, m = dt_from.year, dt_from.month
        while (y, m) <= (dt_to.year, dt_to.month):
            rows.append({
                'label': "%s %s" % (MONTHS_FR[m - 1], str(y)[2:]),
                'amount': totals.get((y, m), 0.0),
            })
            m += 1
            if m == 13:
                m = 1
                y += 1
        return rows

    @api.model
    def get_top_debtors(self, limit=8, config_id=None, source=None):
        """Top N débiteurs par encours (reste dû agrégé)."""
        Credit = self.env['aite.pos.credit']
        today = fields.Date.context_today(self)
        open_credits = Credit.search(self._credit_domain(config_id,
                                                         source=source))

        by_partner = defaultdict(lambda: {
            'outstanding': 0.0, 'max_age': 0, 'last_payment': None,
        })
        for c in open_credits:
            d = by_partner[c.partner_id]
            d['partner'] = c.partner_id
            d['outstanding'] += c.amount_residual
            age = (today - c.date_open).days if c.date_open else 0
            d['max_age'] = max(d['max_age'], age)

        Payment = self.env['aite.pos.credit.payment']
        for partner in list(by_partner.keys()):
            last = Payment.search([
                ('partner_id', '=', partner.id),
                ('state', '=', 'posted'),
            ], order='date desc', limit=1)
            by_partner[partner]['last_payment'] = (
                fields.Date.to_string(last.date) if last else None)

        rows = []
        late = Credit.AGE_THRESHOLD_LATE
        crit = Credit.AGE_THRESHOLD_CRITICAL
        for partner, d in by_partner.items():
            age = d['max_age']
            if age >= crit:
                sev = 'critical'
            elif age >= late:
                sev = 'late'
            else:
                sev = 'recent'
            rows.append({
                'partner_id': partner.id,
                'name': partner.name or _("(sans nom)"),
                'phone': partner.phone or partner.mobile or "",
                'outstanding': d['outstanding'],
                'max_age': age,
                'last_payment': d['last_payment'],
                'severity': sev,
            })
        rows.sort(key=lambda r: r['outstanding'], reverse=True)
        return rows[:limit]

    @api.model
    def get_payment_breakdown(self, date_from, date_to, config_id=None,
                              source=None):
        """Répartition des remboursements par moyen de paiement (période)."""
        Payment = self.env['aite.pos.credit.payment']
        dt_from, dt_to = self._parse_period(date_from, date_to)
        rows = Payment.read_group(
            self._payment_domain(dt_from, dt_to, config_id, source),
            fields=['amount:sum'],
            groupby=['method'],
            lazy=False,
        )
        total = sum(r.get('amount') or 0.0 for r in rows)
        label_map = dict(Payment._fields['method'].selection)
        result = []
        for r in rows:
            method = r.get('method')
            amount = r.get('amount') or 0.0
            result.append({
                'method': method,
                'label': label_map.get(method, method or _("Inconnu")),
                'amount': amount,
                'count': r.get('__count') or 0,
                'pct': (amount / total * 100.0) if total else 0.0,
            })
        result.sort(key=lambda x: x['amount'], reverse=True)
        return result

    @api.model
    def get_evolution(self, months=6, config_id=None, source=None):
        """Évolution mensuelle : nouvelles ardoises vs recouvré."""
        Credit = self.env['aite.pos.credit']
        Payment = self.env['aite.pos.credit.payment']
        today = fields.Date.context_today(self)

        periods = []
        y, m = today.year, today.month
        for _i in range(months):
            periods.append((y, m))
            m -= 1
            if m == 0:
                m = 12
                y -= 1
        periods.reverse()

        MONTHS_FR = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin',
                     'Juil', 'Août', 'Sep', 'Oct', 'Nov', 'Déc']

        result = []
        for (yy, mm) in periods:
            start = datetime(yy, mm, 1).date()
            if mm == 12:
                end = datetime(yy + 1, 1, 1).date() - timedelta(days=1)
            else:
                end = datetime(yy, mm + 1, 1).date() - timedelta(days=1)

            opened_domain = [
                ('date_open', '>=', start), ('date_open', '<=', end),
            ]
            if config_id:
                opened_domain.append(('config_id', '=', int(config_id)))
            if source:
                opened_domain.append(('source', '=', source))
            opened = Credit.search(opened_domain)
            opened_amount = sum(opened.mapped('amount_total'))

            recovered = Payment.search(
                self._payment_domain(start, end, config_id, source))
            recovered_amount = sum(recovered.mapped('amount'))

            result.append({
                'period': MONTHS_FR[mm - 1],
                'opened': opened_amount,
                'recovered': recovered_amount,
            })
        return result

    @api.model
    def get_recent_payments(self, date_from, date_to, limit=50,
                            config_id=None, source=None):
        """Journal des remboursements récents (période)."""
        Payment = self.env['aite.pos.credit.payment']
        dt_from, dt_to = self._parse_period(date_from, date_to)
        payments = Payment.search(
            self._payment_domain(dt_from, dt_to, config_id, source),
            order='date desc, id desc', limit=limit)
        label_map = dict(Payment._fields['method'].selection)
        return [{
            'id': p.id,
            'date': fields.Date.to_string(p.date),
            'partner_name': p.partner_id.name or "",
            'credit_ref': p.credit_id.name or "",
            'method': p.method,
            'method_label': label_map.get(p.method, p.method),
            'transaction_ref': p.transaction_ref or "",
            'collected_by': p.collected_by.name or "",
            'amount': p.amount,
            'residual_after': p.credit_id.amount_residual,
        } for p in payments]
