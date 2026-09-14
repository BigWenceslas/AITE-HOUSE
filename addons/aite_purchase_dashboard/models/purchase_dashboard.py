# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from collections import defaultdict

from odoo import api, fields, models, _
from odoo.exceptions import AccessError


class AitePurchaseDashboard(models.AbstractModel):
    """
    Fournisseur de données du tableau de bord Achats & Fournisseurs.

    Principes (pipeline AITE éprouvé) :

    * **Calcul pur et testable** — la logique de classification (statut de
      facture, tranche de balance âgée, OTIF, badge fournisseur, badge
      prix, DPO) est isolée dans des méthodes statiques sans ORM ; les
      tests extraient et exécutent ce code exact.
    * **Agrégations sûres** — ``read_group`` uniquement sur des champs
      stockés (``price_subtotal``, ``amount_residual``…), le reste sommé
      en Python.
    * **Défensif entre versions** — champs optionnels lus via ``getattr``
      (``receipt_status``…), domaines d'état volontairement larges.

    Conventions métier :

    * Dettes (401) : factures fournisseurs comptabilisées non soldées ;
      la **balance âgée** est ventilée par jours de retard (non échu /
      1-30 / 31-60 / 61-90 / +90) et l'**échéancier** par semaine.
    * Créances (409) : consignes (registre dédié), avoirs fournisseurs
      ouverts, et soldes débiteurs du compte fournisseurs (paiements non
      lettrés) — les « acomptes » sont estimés comme solde débiteur moins
      avoirs ouverts.
    * **OTIF strict** (à l'heure ET complet) ; un badge distinct tolère
      les petits retards sous le seuil configuré.
    """
    _name = 'aite.purchase.dashboard'
    _description = "AITE Achats — Data Provider (tableau de bord)"

    _SUP_PALETTE = [
        '#714B67', '#185FA5', '#3B6D11', '#0F6E56',
        '#854F0B', '#A32D2D', '#5B4B8A', '#B0655A',
        '#8A7B4B', '#4B7B8A',
    ]

    # ------------------------------------------------------------------
    # Calcul pur (extrait et exécuté tel quel par les tests)
    # ------------------------------------------------------------------

    @staticmethod
    def _bucket(days_late):
        """Tranche de balance âgée selon les jours de retard."""
        if days_late <= 0:
            return 0
        if days_late <= 30:
            return 1
        if days_late <= 60:
            return 2
        if days_late <= 90:
            return 3
        return 4

    @staticmethod
    def _invoice_metrics(residual, days_late, days_to_due, soon_days):
        """
        Statut et urgence d'une facture fournisseur ouverte.

        :returns: dict {status, status_cls, urgency}
        """
        if residual <= 0:
            return {'status': 'Payée', 'status_cls': 'teal', 'urgency': 5}
        if days_late > 0:
            return {'status': 'En retard', 'status_cls': 'red', 'urgency': 0}
        if days_to_due <= soon_days:
            return {'status': 'À payer bientôt', 'status_cls': 'amber',
                    'urgency': 1}
        return {'status': 'À échoir', 'status_cls': 'blue', 'urgency': 2}

    @staticmethod
    def _order_metrics(pending, days_late, is_full, late_threshold):
        """
        Statut d'une commande et OTIF strict.

        :param pending: True si non encore reçue
        :param days_late: retard vs date prévue (réception réelle, ou
            aujourd'hui si en attente)
        :param is_full: réception complète (True/False/None si en attente)
        :param late_threshold: tolérance de retard (badge uniquement)
        :returns: dict {on_time, otif, status, status_cls}
        """
        on_time = (not pending) and days_late <= 0
        otif = None if pending else bool(on_time and is_full is True)
        if pending and days_late > late_threshold:
            status, cls = 'En retard', 'red'
        elif pending:
            status, cls = 'En attente', 'blue'
        elif days_late > late_threshold:
            status, cls = 'Reçue en retard', 'amber'
        elif is_full is False:
            status, cls = 'Reçue incomplète', 'amber'
        else:
            status, cls = 'Reçue conforme', 'teal'
        return {'on_time': on_time, 'otif': otif,
                'status': status, 'status_cls': cls}

    @staticmethod
    def _price_metrics(p0, p1, vol_month, threshold_pct):
        """
        Variation de prix d'achat et impact annuel.

        :returns: dict {delta, impact, badge, badge_cls}
        """
        delta = ((p1 - p0) / p0 * 100.0) if p0 else 0.0
        impact = (p1 - p0) * (vol_month or 0.0) * 12.0
        if delta >= threshold_pct:
            badge, cls = 'Hausse forte', 'red'
        elif delta > 0.5:
            badge, cls = 'Hausse', 'amber'
        elif delta < -0.5:
            badge, cls = 'Baisse', 'teal'
        else:
            badge, cls = 'Stable', 'blue'
        return {'delta': delta, 'impact': impact,
                'badge': badge, 'badge_cls': cls}

    @staticmethod
    def _supplier_badge(part_pct, late_amount, purchases, dep_threshold):
        """Badge fournisseur : dépendance > retards > OK > inactif."""
        if purchases > 0 and part_pct >= dep_threshold:
            return {'badge': 'Dépendance', 'badge_cls': 'red'}
        if late_amount > 0:
            return {'badge': 'Retards', 'badge_cls': 'amber'}
        if purchases > 0:
            return {'badge': 'OK', 'badge_cls': 'teal'}
        return {'badge': 'Inactif', 'badge_cls': 'gray'}

    @staticmethod
    def _dpo(outstanding, purchases_period, days):
        """DPO = encours / achats de la période × jours (0 si pas d'achats)."""
        if purchases_period <= 0:
            return 0.0
        return outstanding / purchases_period * float(days)

    # ------------------------------------------------------------------
    # Helpers ORM
    # ------------------------------------------------------------------

    def _cfg(self):
        c = self.env.company
        return {
            'soon': c.aite_purchase_due_soon_days or 7,
            'late': c.aite_purchase_late_days or 0,
            'dep': c.aite_purchase_dependency_pct or 40.0,
            'price': c.aite_purchase_price_increase_pct or 5.0,
        }

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

    def _dt_range(self, dt_from, dt_to):
        return (
            fields.Datetime.to_string(
                datetime.combine(dt_from, datetime.min.time())),
            fields.Datetime.to_string(
                datetime.combine(dt_to, datetime.max.time())),
        )

    def _supplier_universe(self):
        """Fournisseurs actifs : commandes confirmées sur 12 mois ou
        factures ouvertes."""
        since = fields.Datetime.now() - timedelta(days=365)
        po_partners = self.env['purchase.order'].read_group(
            [('state', 'in', ('purchase', 'done')),
             ('company_id', '=', self.env.company.id),
             ('date_order', '>=', since)],
            fields=['id:count'], groupby=['partner_id'], lazy=False)
        ids = {r['partner_id'][0] for r in po_partners if r['partner_id']}
        bills = self.env['account.move'].read_group(
            [('move_type', '=', 'in_invoice'), ('state', '=', 'posted'),
             ('company_id', '=', self.env.company.id),
             ('payment_state', 'in', ('not_paid', 'partial'))],
            fields=['id:count'], groupby=['partner_id'], lazy=False)
        ids |= {r['partner_id'][0] for r in bills if r['partner_id']}
        partners = self.env['res.partner'].browse(list(ids))
        return partners.sorted(lambda p: (p.name or '').lower())

    # ------------------------------------------------------------------
    # Référentiels
    # ------------------------------------------------------------------

    @api.model
    def get_meta(self):
        company = self.env.company
        return {
            'company_name': company.name,
            'currency_symbol': company.currency_id.symbol or 'F',
            'cfg': self._cfg(),
            'is_manager': self.env.user.has_group(
                'purchase.group_purchase_manager'),
        }

    @api.model
    def get_suppliers(self):
        partners = self._supplier_universe()
        palette = self._SUP_PALETTE
        return [{
            'id': p.id,
            'name': p.name or _("(sans nom)"),
            'color': palette[i % len(palette)],
        } for i, p in enumerate(partners)]

    # ------------------------------------------------------------------
    # Factures fournisseurs ouvertes (source des dettes)
    # ------------------------------------------------------------------

    def _open_bill_rows(self, supplier_id=None):
        cfg = self._cfg()
        today = fields.Date.context_today(self)
        domain = [
            ('move_type', '=', 'in_invoice'),
            ('state', '=', 'posted'),
            ('payment_state', 'in', ('not_paid', 'partial')),
            ('company_id', '=', self.env.company.id),
        ]
        if supplier_id:
            domain.append(('partner_id', '=', int(supplier_id)))
        rows = []
        for mv in self.env['account.move'].search(domain):
            residual = abs(mv.amount_residual or 0.0)
            if residual <= 0:
                continue
            due = mv.invoice_date_due or mv.invoice_date or today
            days_late = max(0, (today - due).days)
            days_to_due = max(0, (due - today).days)
            m = self._invoice_metrics(
                residual, days_late, days_to_due, cfg['soon'])
            rows.append({
                'id': mv.id,
                'partner_id': mv.partner_id.id,
                'partner': mv.partner_id.name or "",
                'ref': mv.name or "",
                'due': fields.Date.to_string(due),
                'total': abs(mv.amount_total or 0.0),
                'paid': abs(mv.amount_total or 0.0) - residual,
                'residual': residual,
                'days_late': days_late,
                'days_to_due': days_to_due,
                'bucket': self._bucket(days_late),
                **m,
            })
        return rows

    @api.model
    def get_open_invoices(self, supplier_id=None):
        rows = self._open_bill_rows(supplier_id)
        rows.sort(key=lambda r: (r['urgency'], r['days_to_due'],
                                 -r['days_late']))
        return rows

    # ------------------------------------------------------------------
    # Commandes & réceptions
    # ------------------------------------------------------------------

    def _order_rows(self, dt_from, dt_to, supplier_id=None):
        cfg = self._cfg()
        today = fields.Date.context_today(self)
        d0, d1 = self._dt_range(dt_from, dt_to)
        domain = [
            ('state', 'in', ('purchase', 'done')),
            ('company_id', '=', self.env.company.id),
            ('date_order', '>=', d0), ('date_order', '<=', d1),
        ]
        if supplier_id:
            domain.append(('partner_id', '=', int(supplier_id)))
        rows = []
        for po in self.env['purchase.order'].search(
                domain, order='date_order desc'):
            done_picks = po.picking_ids.filtered(
                lambda p: p.state == 'done')
            recv = max(done_picks.mapped('date_done')) if done_picks else None
            status_field = getattr(po, 'receipt_status', None)
            if status_field:
                pending = status_field == 'pending'
                is_full = (status_field == 'full') if not pending else None
            else:
                lines = po.order_line.filtered(
                    lambda l: l.product_id and
                    l.product_id.type != 'service')
                received_any = bool(recv)
                pending = not received_any
                if pending:
                    is_full = None
                else:
                    is_full = all(
                        (l.qty_received or 0.0) >= (l.product_qty or 0.0)
                        - 0.001 for l in lines) if lines else True
            planned = po.date_planned.date() if po.date_planned else None
            if pending:
                days_late = max(0, (today - planned).days) if planned else 0
            else:
                rdate = recv.date() if recv else today
                days_late = max(0, (rdate - planned).days) if planned else 0
            delai = None
            if recv and po.date_order:
                delai = (recv.date() - po.date_order.date()).days
            m = self._order_metrics(pending, days_late, is_full, cfg['late'])
            rows.append({
                'id': po.id,
                'partner_id': po.partner_id.id,
                'partner': po.partner_id.name or "",
                'ref': po.name or "",
                'date': fields.Date.to_string(po.date_order),
                'amount': po.amount_total or 0.0,
                'planned': fields.Date.to_string(planned) if planned else "",
                'recv': fields.Date.to_string(recv) if recv else "",
                'days_late': days_late,
                'delai': delai,
                'pending': pending,
                'is_full': is_full,
                **m,
            })
        return rows

    @api.model
    def get_orders_journal(self, date_from, date_to,
                           supplier_id=None, limit=60):
        dt_from, dt_to = self._parse_period(date_from, date_to)
        return self._order_rows(dt_from, dt_to, supplier_id)[:limit]

    # ------------------------------------------------------------------
    # Créances fournisseurs (409)
    # ------------------------------------------------------------------

    @api.model
    def get_claims(self, supplier_id=None):
        Deposit = self.env['aite.purchase.deposit']
        dep_domain = [('company_id', '=', self.env.company.id)]
        if supplier_id:
            dep_domain.append(('partner_id', '=', int(supplier_id)))
        deposits = [{
            'id': d.id,
            'partner_id': d.partner_id.id,
            'partner': d.partner_id.name or "",
            'qty': d.qty,
            'unit_value': d.unit_value,
            'value': d.value,
            'last': fields.Date.to_string(d.last_return_date)
            if d.last_return_date else "",
        } for d in Deposit.search(dep_domain)]
        deposits_total = sum(d['value'] for d in deposits)

        refund_domain = [
            ('move_type', '=', 'in_refund'), ('state', '=', 'posted'),
            ('payment_state', 'in', ('not_paid', 'partial')),
            ('company_id', '=', self.env.company.id),
        ]
        if supplier_id:
            refund_domain.append(('partner_id', '=', int(supplier_id)))
        avoirs = []
        for mv in self.env['account.move'].search(
                refund_domain, order='invoice_date desc'):
            residual = abs(mv.amount_residual or 0.0)
            if residual <= 0:
                continue
            avoirs.append({
                'id': mv.id,
                'partner_id': mv.partner_id.id,
                'partner': mv.partner_id.name or "",
                'ref': mv.name or "",
                'date': fields.Date.to_string(
                    mv.invoice_date or mv.date),
                'motif': mv.ref or mv.invoice_origin or "",
                'amount': residual,
            })
        avoirs_total = sum(a['amount'] for a in avoirs)

        # Soldes débiteurs du compte fournisseurs (paiements non lettrés,
        # avoirs) — l'approximation « acomptes » = débiteur − avoirs.
        aml_domain = [
            ('account_id.account_type', '=', 'liability_payable'),
            ('parent_state', '=', 'posted'),
            ('company_id', '=', self.env.company.id),
            ('amount_residual', '<', -0.005),
        ]
        if supplier_id:
            aml_domain.append(('partner_id', '=', int(supplier_id)))
        debit_total = 0.0
        for line in self.env['account.move.line'].search(aml_domain):
            debit_total += -(line.amount_residual or 0.0)
        acomptes_est = max(0.0, debit_total - avoirs_total)

        return {
            'deposits': deposits,
            'deposits_total': deposits_total,
            'deposits_qty': sum(d['qty'] for d in deposits),
            'avoirs': avoirs,
            'avoirs_total': avoirs_total,
            'debit_total': debit_total,
            'acomptes_est': acomptes_est,
            'total': deposits_total + avoirs_total + acomptes_est,
        }

    # ------------------------------------------------------------------
    # Flux mensuels & prix
    # ------------------------------------------------------------------

    @api.model
    def get_flux_months(self, months=6, supplier_id=None):
        today = fields.Date.context_today(self)
        periods = []
        y, m = today.year, today.month
        for _i in range(months):
            periods.append((y, m))
            m -= 1
            if m == 0:
                y, m = y - 1, 12
        periods.reverse()
        MONTHS_FR = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin',
                     'Juil', 'Août', 'Sep', 'Oct', 'Nov', 'Déc']
        Move = self.env['account.move']
        Payment = self.env['account.payment']
        out = []
        for (yy, mm) in periods:
            start = datetime(yy, mm, 1).date()
            end = (datetime(yy + (mm == 12), (mm % 12) + 1, 1).date()
                   - timedelta(days=1))
            bill_domain = [
                ('move_type', '=', 'in_invoice'), ('state', '=', 'posted'),
                ('company_id', '=', self.env.company.id),
                ('invoice_date', '>=', start), ('invoice_date', '<=', end),
            ]
            pay_domain = [
                ('payment_type', '=', 'outbound'),
                ('partner_type', '=', 'supplier'),
                ('company_id', '=', self.env.company.id),
                ('state', 'not in', ('draft', 'cancel', 'canceled')),
                ('date', '>=', start), ('date', '<=', end),
            ]
            if supplier_id:
                bill_domain.append(('partner_id', '=', int(supplier_id)))
                pay_domain.append(('partner_id', '=', int(supplier_id)))
            bills = sum(abs(b.amount_total or 0.0)
                        for b in Move.search(bill_domain))
            pays = sum(abs(p.amount or 0.0)
                       for p in Payment.search(pay_domain))
            out.append({'period': MONTHS_FR[mm - 1],
                        'bills': bills, 'payments': pays})
        return out

    def _price_lines(self, day_from, day_to, supplier_id=None):
        d0, d1 = self._dt_range(day_from, day_to)
        domain = [
            ('order_id.state', 'in', ('purchase', 'done')),
            ('order_id.company_id', '=', self.env.company.id),
            ('order_id.date_order', '>=', d0),
            ('order_id.date_order', '<=', d1),
            ('product_id', '!=', False),
        ]
        if supplier_id:
            domain.append(('order_id.partner_id', '=', int(supplier_id)))
        return self.env['purchase.order.line'].search(domain)

    @api.model
    def get_price_moves(self, supplier_id=None, limit=8):
        cfg = self._cfg()
        today = fields.Date.context_today(self)
        recent = self._price_lines(today - timedelta(days=45), today,
                                   supplier_id)
        old = self._price_lines(today - timedelta(days=210),
                                today - timedelta(days=120), supplier_id)

        def agg(lines):
            data = defaultdict(lambda: {'qty': 0.0, 'val': 0.0,
                                        'spend': 0.0, 'name': '',
                                        'partner': ''})
            for l in lines:
                d = data[l.product_id.id]
                qty = l.product_qty or 0.0
                d['qty'] += qty
                d['val'] += (l.price_unit or 0.0) * qty
                d['spend'] += l.price_subtotal or 0.0
                d['name'] = l.product_id.display_name
                d['partner'] = l.order_id.partner_id.name or ""
            return data

        rec, oldd = agg(recent), agg(old)
        rows = []
        for pid, r in rec.items():
            if pid not in oldd or r['qty'] <= 0 or oldd[pid]['qty'] <= 0:
                continue
            p1 = r['val'] / r['qty']
            p0 = oldd[pid]['val'] / oldd[pid]['qty']
            vol_month = r['qty'] / 45.0 * 30.0
            m = self._price_metrics(p0, p1, vol_month, cfg['price'])
            rows.append({
                'product_id': pid,
                'name': r['name'],
                'partner': r['partner'],
                'p0': p0, 'p1': p1,
                'vol_month': vol_month,
                'spend': r['spend'],
                **m,
            })
        rows.sort(key=lambda x: -x['spend'])
        return rows[:limit]

    @api.model
    def get_price_index(self, months=6, supplier_id=None):
        today = fields.Date.context_today(self)
        moves = self.get_price_moves(supplier_id, limit=5)
        pids = [r['product_id'] for r in moves]
        names = {r['product_id']: r['name'] for r in moves}
        periods = []
        y, m = today.year, today.month
        for _i in range(months):
            periods.append((y, m))
            m -= 1
            if m == 0:
                y, m = y - 1, 12
        periods.reverse()
        MONTHS_FR = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin',
                     'Juil', 'Août', 'Sep', 'Oct', 'Nov', 'Déc']
        labels = [MONTHS_FR[mm - 1] for (_yy, mm) in periods]
        series = []
        palette = self._SUP_PALETTE
        for i, pid in enumerate(pids):
            vals = []
            for (yy, mm) in periods:
                start = datetime(yy, mm, 1).date()
                end = (datetime(yy + (mm == 12), (mm % 12) + 1, 1).date()
                       - timedelta(days=1))
                lines = self._price_lines(start, end, supplier_id).filtered(
                    lambda l: l.product_id.id == pid)
                qty = sum(l.product_qty or 0.0 for l in lines)
                val = sum((l.price_unit or 0.0) * (l.product_qty or 0.0)
                          for l in lines)
                vals.append(val / qty if qty > 0 else None)
            base = next((v for v in vals if v), None)
            idx, lastv = [], 100.0
            for v in vals:
                if v and base:
                    lastv = v / base * 100.0
                idx.append(round(lastv, 1))
            series.append({'name': names[pid],
                           'color': palette[i % len(palette)],
                           'values': idx})
        return {'labels': labels, 'series': series}

    # ------------------------------------------------------------------
    # Agrégats fournisseurs & KPIs
    # ------------------------------------------------------------------

    @api.model
    def get_supplier_rows(self, date_from, date_to):
        cfg = self._cfg()
        dt_from, dt_to = self._parse_period(date_from, date_to)
        partners = self._supplier_universe()
        colors = {s['id']: s['color'] for s in self.get_suppliers()}
        orders = self._order_rows(dt_from, dt_to)
        bills = self._open_bill_rows()
        claims = self.get_claims()
        dep_by_partner = defaultdict(float)
        for d in claims['deposits']:
            dep_by_partner[d['partner_id']] += d['value']
        avr_by_partner = defaultdict(float)
        for a in claims['avoirs']:
            avr_by_partner[a['partner_id']] += a['amount']

        total = sum(o['amount'] for o in orders) or 0.0
        rows = []
        for p in partners:
            po = [o for o in orders if o['partner_id'] == p.id]
            bi = [b for b in bills if b['partner_id'] == p.id]
            achats = sum(o['amount'] for o in po)
            part = (achats / total * 100.0) if total else 0.0
            du = sum(b['residual'] for b in bi)
            retard = sum(b['residual'] for b in bi if b['days_late'] > 0)
            recus = [o for o in po if not o['pending']]
            delai = (sum(o['delai'] or 0 for o in recus) / len(recus)) \
                if recus else 0.0
            otif = (100.0 * len([o for o in recus if o['otif']])
                    / len(recus)) if recus else 0.0
            badge = self._supplier_badge(part, retard, achats, cfg['dep'])
            rows.append({
                'id': p.id,
                'name': p.name or "",
                'color': colors.get(p.id, '#888780'),
                'achats': achats,
                'part': part,
                'du': du,
                'retard': retard,
                'delai': delai,
                'otif': otif,
                'deposits': dep_by_partner.get(p.id, 0.0),
                'avoirs': avr_by_partner.get(p.id, 0.0),
                **badge,
            })
        rows.sort(key=lambda r: -r['achats'])
        return rows

    @api.model
    def get_kpis(self, date_from, date_to, supplier_id=None):
        cfg = self._cfg()
        dt_from, dt_to = self._parse_period(date_from, date_to)
        days = (dt_to - dt_from).days + 1

        orders = self._order_rows(dt_from, dt_to, supplier_id)
        achats = sum(o['amount'] for o in orders)
        recus = [o for o in orders if not o['pending']]
        otif = (100.0 * len([o for o in recus if o['otif']]) / len(recus)) \
            if recus else 0.0
        delai_moy = (sum(o['delai'] or 0 for o in recus) / len(recus)) \
            if recus else 0.0
        pending = [o for o in orders if o['pending']]
        pending_late = [o for o in pending
                        if o['days_late'] > cfg['late']]
        recv_late = [o for o in recus if o['days_late'] > cfg['late']]

        bills = self._open_bill_rows(supplier_id)
        encours = sum(b['residual'] for b in bills)
        retard_rows = [b for b in bills if b['days_late'] > 0]
        retard = sum(b['residual'] for b in retard_rows)
        soon_rows = [b for b in bills if b['days_late'] == 0
                     and b['days_to_due'] <= cfg['soon']]
        soon = sum(b['residual'] for b in soon_rows)
        month = sum(b['residual'] for b in bills
                    if b['days_late'] == 0
                    and cfg['soon'] < b['days_to_due'] <= 30)

        d0, d1 = dt_from, dt_to
        bill_domain = [
            ('move_type', '=', 'in_invoice'), ('state', '=', 'posted'),
            ('company_id', '=', self.env.company.id),
            ('invoice_date', '>=', d0), ('invoice_date', '<=', d1),
        ]
        if supplier_id:
            bill_domain.append(('partner_id', '=', int(supplier_id)))
        bills_period = sum(abs(b.amount_total or 0.0)
                           for b in self.env['account.move'].search(
                               bill_domain))
        dpo = self._dpo(encours, bills_period or achats, days)

        claims = self.get_claims(supplier_id)
        prices = self.get_price_moves(supplier_id)
        w = sum(p['p1'] * p['vol_month'] for p in prices)
        var_moy = (sum(p['delta'] * p['p1'] * p['vol_month']
                       for p in prices) / w) if w else 0.0
        top_h = max(prices, key=lambda p: p['delta']) if prices else None
        nb_h = len([p for p in prices if p['delta'] >= cfg['price']])
        impact = sum(p['impact'] for p in prices if p['impact'] > 0)

        # Top produits achetés (période)
        dd0, dd1 = self._dt_range(dt_from, dt_to)
        pol_domain = [
            ('order_id.state', 'in', ('purchase', 'done')),
            ('order_id.company_id', '=', self.env.company.id),
            ('order_id.date_order', '>=', dd0),
            ('order_id.date_order', '<=', dd1),
            ('product_id', '!=', False),
        ]
        if supplier_id:
            pol_domain.append(
                ('order_id.partner_id', '=', int(supplier_id)))
        grp = self.env['purchase.order.line'].read_group(
            pol_domain, fields=['price_subtotal:sum'],
            groupby=['product_id'], lazy=False)
        top_products = sorted(
            [{'name': g['product_id'][1],
              'value': g.get('price_subtotal') or 0.0}
             for g in grp if g['product_id']],
            key=lambda x: -x['value'])[:8]

        suppliers = self.get_supplier_rows(date_from, date_to)
        actifs = [s for s in suppliers if s['achats'] > 0]
        top_sup = actifs[0] if actifs else None

        return {
            'achats': achats,
            'orders_count': len(orders),
            'recus_count': len(recus),
            'encours': encours,
            'open_count': len(bills),
            'retard': retard,
            'retard_count': len(retard_rows),
            'retard_pct': (retard / encours * 100.0) if encours else 0.0,
            'soon': soon,
            'soon_count': len(soon_rows),
            'month': month,
            'dpo': dpo,
            'otif': otif,
            'delai_moy': delai_moy,
            'pending_count': len(pending),
            'pending_amount': sum(o['amount'] for o in pending),
            'pending_late': len(pending_late),
            'recv_late': len(recv_late),
            'claims_total': claims['total'],
            'deposits_total': claims['deposits_total'],
            'deposits_qty': claims['deposits_qty'],
            'avoirs_total': claims['avoirs_total'],
            'avoirs_count': len(claims['avoirs']),
            'acomptes_est': claims['acomptes_est'],
            'var_moy': var_moy,
            'top_hausse': top_h['delta'] if top_h else 0.0,
            'top_hausse_name': top_h['name'] if top_h else "",
            'nb_hausses': nb_h,
            'impact': impact,
            'top_products': top_products,
            'suppliers_count': len(actifs),
            'top_sup_name': top_sup['name'] if top_sup else "",
            'top_sup_part': top_sup['part'] if top_sup else 0.0,
            'cfg': cfg,
        }

    # ------------------------------------------------------------------
    # Sauvegarde configuration
    # ------------------------------------------------------------------

    @api.model
    def save_alert_config(self, global_cfg):
        if not self.env.user.has_group('purchase.group_purchase_manager'):
            raise AccessError(_(
                "Seul un responsable Achats peut modifier la configuration "
                "des alertes."))
        company = self.env.company.sudo()
        mapping = {
            'soon': 'aite_purchase_due_soon_days',
            'late': 'aite_purchase_late_days',
            'dep': 'aite_purchase_dependency_pct',
            'price': 'aite_purchase_price_increase_pct',
        }
        vals = {}
        for key, fname in mapping.items():
            if key in (global_cfg or {}):
                vals[fname] = global_cfg[key]
        if vals:
            company.write(vals)
        return True
