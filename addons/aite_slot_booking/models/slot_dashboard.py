# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from collections import defaultdict

from odoo import api, fields, models, _

from .booking_resource import KINDS


class SlotDashboard(models.AbstractModel):
    """
    Fournisseur de données du tableau de bord Espaces & Prestations.

    Une source de vérité : la grille de disponibilité vient de
    ``aite.booking.resource.get_day_grid`` (la même API que le site
    web) ; les agrégats de période sont calculés ici. Le taux de
    remplissage est une fonction pure testée (``_fill_rate``).
    """
    _name = 'aite.slot.dashboard'
    _description = "Espaces & Prestations — Data Provider"

    _KIND_COLORS = {
        'space': '#714B67', 'spa': '#0F6E56', 'hair': '#185FA5',
        'pressing': '#854F0B', 'other': '#888780',
    }

    # ------------------------------------------------------------------
    # Calcul pur (extrait et exécuté tel quel par les tests)
    # ------------------------------------------------------------------

    @staticmethod
    def _fill_rate(booked_hours, open_hours):
        """Taux de remplissage en % (0 si pas d'heures ouvrées)."""
        if not open_hours or open_hours <= 0:
            return 0.0
        return min(100.0, booked_hours / open_hours * 100.0)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _parse_period(self, date_from, date_to):
        try:
            dt_from = datetime.strptime(date_from, '%Y-%m-%d').date()
            dt_to = datetime.strptime(date_to, '%Y-%m-%d').date()
        except (TypeError, ValueError):
            today = fields.Date.context_today(self)
            dt_from = today
            dt_to = today
        if dt_from > dt_to:
            dt_from, dt_to = dt_to, dt_from
        return dt_from, dt_to

    def _booking_domain(self, dt_from, dt_to, kind=None, resource_id=None,
                        states=None):
        d0 = fields.Datetime.to_string(
            datetime.combine(dt_from, datetime.min.time()))
        d1 = fields.Datetime.to_string(
            datetime.combine(dt_to, datetime.max.time()))
        domain = [
            ('company_id', '=', self.env.company.id),
            ('start', '>=', d0), ('start', '<=', d1),
        ]
        if states:
            domain.append(('state', 'in', list(states)))
        if kind:
            domain.append(('kind', '=', kind))
        if resource_id:
            domain.append(('resource_id', '=', int(resource_id)))
        return domain

    # ------------------------------------------------------------------
    # Référentiels
    # ------------------------------------------------------------------

    @api.model
    def get_meta(self):
        company = self.env.company
        return {
            'company_name': company.name,
            'currency_symbol': company.currency_id.symbol or 'F',
            'kinds': [{'key': k, 'label': l,
                       'color': self._KIND_COLORS.get(k, '#888780')}
                      for (k, l) in KINDS],
            'is_manager': self.env.user.has_group(
                'aite_hotel_management.group_hotel_manager'),
            'today': fields.Date.to_string(
                fields.Date.context_today(self)),
        }

    @api.model
    def get_resources(self, kind=None):
        domain = [('company_id', '=', self.env.company.id)]
        if kind:
            domain.append(('kind', '=', kind))
        return [{
            'id': r.id, 'name': r.name, 'kind': r.kind,
            'color': r.color or '#714B67', 'capacity': r.capacity,
            'open_hour': r.open_hour, 'close_hour': r.close_hour,
        } for r in self.env['aite.booking.resource'].search(domain)]

    # ------------------------------------------------------------------
    # Planning du jour
    # ------------------------------------------------------------------

    @api.model
    def get_day_board(self, day, kind=None):
        """Couloirs du planning : une grille par ressource (API
        partagée avec le site web)."""
        Resource = self.env['aite.booking.resource']
        domain = [('company_id', '=', self.env.company.id)]
        if kind:
            domain.append(('kind', '=', kind))
        boards = []
        for res in Resource.search(domain):
            boards.append(Resource.get_day_grid(res.id, day))
        return boards

    # ------------------------------------------------------------------
    # KPIs & séries
    # ------------------------------------------------------------------

    @api.model
    def get_kpis(self, date_from, date_to, kind=None, resource_id=None):
        Booking = self.env['aite.slot.booking']
        dt_from, dt_to = self._parse_period(date_from, date_to)
        days = (dt_to - dt_from).days + 1

        all_states = Booking.search(self._booking_domain(
            dt_from, dt_to, kind, resource_id))
        by_state = defaultdict(list)
        for b in all_states:
            by_state[b.state].append(b)

        done = by_state.get('done', [])
        confirmed = by_state.get('confirmed', [])
        no_show = by_state.get('no_show', [])
        held = done + confirmed + no_show
        ca_done = sum(b.amount for b in done)
        no_show_pct = (len(no_show) / len(held) * 100.0) if held else 0.0

        # Remplissage : heures réservées (confirmées + réalisées) vs
        # heures ouvrées des ressources du périmètre.
        res_domain = [('company_id', '=', self.env.company.id)]
        if kind:
            res_domain.append(('kind', '=', kind))
        if resource_id:
            res_domain.append(('id', '=', int(resource_id)))
        resources = self.env['aite.booking.resource'].search(res_domain)
        open_hours = sum(
            (r.close_hour - r.open_hour) * r.capacity
            for r in resources) * days
        booked_hours = sum(
            b.duration_hours for b in done + confirmed)
        fill = self._fill_rate(booked_hours, open_hours)

        pickups_waiting = Booking.search_count([
            ('company_id', '=', self.env.company.id),
            ('kind', '=', 'pressing'),
            ('state', 'in', ('confirmed', 'done')),
            ('pickup_done', '=', False),
        ])

        return {
            'total_count': len(all_states),
            'done_count': len(done),
            'confirmed_count': len(confirmed),
            'no_show_count': len(no_show),
            'cancelled_count': len(by_state.get('cancelled', [])),
            'ca_done': ca_done,
            'no_show_pct': no_show_pct,
            'fill_rate': fill,
            'booked_hours': booked_hours,
            'open_hours': open_hours,
            'pickups_waiting': pickups_waiting,
        }

    @api.model
    def get_bookings(self, date_from, date_to, kind=None,
                     resource_id=None, limit=80):
        Booking = self.env['aite.slot.booking']
        dt_from, dt_to = self._parse_period(date_from, date_to)
        rows = Booking.search(
            self._booking_domain(dt_from, dt_to, kind, resource_id),
            order='start desc', limit=limit)
        out = []
        for b in rows:
            local_start = fields.Datetime.context_timestamp(b, b.start)
            out.append({
                'id': b.id,
                'ref': b.name,
                'date': local_start.strftime('%d/%m %H:%M'),
                'partner': b.partner_id.name or "",
                'resource': b.resource_id.name,
                'kind': b.kind,
                'service': b.service_id.name or "—",
                'qty': b.qty,
                'amount': b.amount,
                'state': b.state,
                'source': b.source,
                'posted': bool(b.posted_line_id),
                'pickup_done': b.pickup_done,
            })
        return out

    @api.model
    def get_service_mix(self, date_from, date_to, kind=None):
        """CA réalisé par famille (donut)."""
        Booking = self.env['aite.slot.booking']
        dt_from, dt_to = self._parse_period(date_from, date_to)
        rows = Booking.search(self._booking_domain(
            dt_from, dt_to, kind, None, states=('done',)))
        agg = defaultdict(float)
        for b in rows:
            agg[b.kind] += b.amount
        labels = dict(KINDS)
        return [{
            'kind': k,
            'label': labels.get(k, k),
            'amount': v,
            'color': self._KIND_COLORS.get(k, '#888780'),
        } for k, v in sorted(agg.items(), key=lambda kv: -kv[1])]

    @api.model
    def get_fill_by_resource(self, date_from, date_to, kind=None):
        """Taux de remplissage par ressource (barres)."""
        Booking = self.env['aite.slot.booking']
        dt_from, dt_to = self._parse_period(date_from, date_to)
        days = (dt_to - dt_from).days + 1
        res_domain = [('company_id', '=', self.env.company.id)]
        if kind:
            res_domain.append(('kind', '=', kind))
        out = []
        for r in self.env['aite.booking.resource'].search(res_domain):
            bookings = Booking.search(self._booking_domain(
                dt_from, dt_to, None, r.id,
                states=('confirmed', 'done')))
            booked = sum(b.duration_hours for b in bookings)
            open_h = (r.close_hour - r.open_hour) * r.capacity * days
            out.append({
                'name': r.name,
                'color': r.color or '#714B67',
                'fill': self._fill_rate(booked, open_h),
            })
        out.sort(key=lambda x: -x['fill'])
        return out
