# -*- coding: utf-8 -*-
from collections import defaultdict
from datetime import datetime, timedelta

from odoo import api, fields, models, _


class HotelDashboard(models.AbstractModel):
    """
    Fournisseur de données du tableau de bord hôtelier.

    Expose des méthodes RPC consommées par le dashboard OWL (même
    architecture que ``aite.pos.credit.dashboard``) : KPIs du jour et de
    période avec comparaison N-1 (occupation, ADR, RevPAR, chiffre
    d'affaires), room board temps réel, mouvements du jour, évolution de
    l'occupation et répartition du CA par type de chambre.

    Définitions (standards hôteliers) :

    * **Taux d'occupation** = chambres occupées / chambres vendables.
    * **ADR** (Average Daily Rate) = CA hébergement / nuitées vendues.
    * **RevPAR** = CA hébergement / nuitées disponibles
      (= ADR × occupation).

    Filtres transverses : ``date_from`` / ``date_to`` (YYYY-MM-DD) pour
    les flux ; ``hotel_id`` (0 / None = tous les hôtels de la société).
    """
    _name = 'aite.hotel.dashboard'
    _description = "Gestion Hôtelière — Data Provider"

    _HOTEL_PALETTE = [
        '#714B67', '#185FA5', '#3B6D11', '#854F0B',
        '#A32D2D', '#0F6E56', '#5B4B8A', '#B0655A',
    ]

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

    def _hotels(self, hotel_id=None):
        domain = [('company_id', '=', self.env.company.id)]
        if hotel_id:
            domain.append(('id', '=', hotel_id))
        return self.env['aite.hotel.hotel'].search(domain)

    def _sellable_rooms(self, hotels):
        return self.env['aite.hotel.room'].search([
            ('hotel_id', 'in', hotels.ids),
            ('out_of_order', '=', False),
        ])

    @api.model
    def _occupied_room_nights(self, hotels, dt_from, dt_to):
        """
        Nuitées occupées sur [dt_from, dt_to] (bornes incluses), par
        recoupement des lignes confirmées / arrivées / parties avec la
        période. Une nuit « n » est occupée si checkin ≤ n < checkout.
        """
        lines = self.env['aite.hotel.reservation.line'].search([
            ('hotel_id', 'in', hotels.ids),
            ('state', 'in', ('confirmed', 'checked_in', 'checked_out')),
            ('checkin_date', '<=',
             fields.Datetime.to_datetime(str(dt_to)) + timedelta(days=1)),
            ('checkout_date', '>', fields.Datetime.to_datetime(str(dt_from))),
        ])
        nights = 0
        per_day = defaultdict(int)
        for line in lines:
            start = max(line.checkin_date.date(), dt_from)
            end = min(line.checkout_date.date(), dt_to + timedelta(days=1))
            day = start
            while day < end:
                per_day[day] += 1
                nights += 1
                day += timedelta(days=1)
        return nights, per_day

    def _room_revenue(self, hotels, dt_from, dt_to):
        """CA hébergement HT de la période (lignes de folio « nuitée »)."""
        lines = self.env['aite.hotel.folio.line'].search([
            ('folio_id.hotel_id', 'in', hotels.ids),
            ('line_type', '=', 'room'),
            ('folio_id.state', '!=', 'cancelled'),
            ('date', '>=', dt_from),
            ('date', '<=', dt_to),
        ])
        return sum(lines.mapped('price_subtotal'))

    def _service_revenue(self, hotels, dt_from, dt_to):
        lines = self.env['aite.hotel.folio.line'].search([
            ('folio_id.hotel_id', 'in', hotels.ids),
            ('line_type', '=', 'service'),
            ('folio_id.state', '!=', 'cancelled'),
            ('date', '>=', dt_from),
            ('date', '<=', dt_to),
        ])
        return sum(lines.mapped('price_subtotal'))

    # ------------------------------------------------------------------
    # Méta / filtres
    # ------------------------------------------------------------------

    @api.model
    def get_dashboard_meta(self):
        currency = self.env.company.currency_id
        return {
            'currency_symbol': currency.symbol or 'F',
            'company_name': self.env.company.name,
            'today': fields.Date.to_string(fields.Date.context_today(self)),
        }

    @api.model
    def get_hotels(self):
        hotels = self._hotels()
        return [{
            'id': hotel.id,
            'name': hotel.name,
            'color': self._HOTEL_PALETTE[i % len(self._HOTEL_PALETTE)],
        } for i, hotel in enumerate(hotels)]

    # ------------------------------------------------------------------
    # KPIs
    # ------------------------------------------------------------------

    @api.model
    def get_kpis(self, date_from, date_to, hotel_id=None):
        dt_from, dt_to = self._parse_period(date_from, date_to)
        hotels = self._hotels(hotel_id)
        today = fields.Date.context_today(self)
        rooms = self._sellable_rooms(hotels)
        total_rooms = len(rooms) or 1

        # --- Photo du jour ------------------------------------------------
        occupied_today = len(rooms.filtered(
            lambda r: r.occupancy_state == 'occupied'))
        Res = self.env['aite.hotel.reservation']
        day_start = fields.Datetime.to_datetime(str(today))
        day_end = day_start + timedelta(days=1)
        arrivals = Res.search_count([
            ('hotel_id', 'in', hotels.ids),
            ('state', '=', 'confirmed'),
            ('checkin_date', '>=', day_start),
            ('checkin_date', '<', day_end),
        ])
        departures = Res.search_count([
            ('hotel_id', 'in', hotels.ids),
            ('state', '=', 'checked_in'),
            ('checkout_date', '>=', day_start),
            ('checkout_date', '<', day_end),
        ])
        inhouse = Res.search([
            ('hotel_id', 'in', hotels.ids),
            ('state', '=', 'checked_in'),
        ])
        inhouse_guests = sum(inhouse.mapped('adults')) \
            + sum(inhouse.mapped('children'))

        # --- Période ------------------------------------------------------
        def period_stats(p_from, p_to):
            days = (p_to - p_from).days + 1
            available = len(rooms) * days
            sold, _per_day = self._occupied_room_nights(
                hotels, p_from, p_to)
            room_rev = self._room_revenue(hotels, p_from, p_to)
            svc_rev = self._service_revenue(hotels, p_from, p_to)
            occ = (sold / available * 100.0) if available else 0.0
            adr = (room_rev / sold) if sold else 0.0
            revpar = (room_rev / available) if available else 0.0
            return {
                'nights_sold': sold,
                'occupancy': occ,
                'adr': adr,
                'revpar': revpar,
                'room_revenue': room_rev,
                'service_revenue': svc_rev,
                'total_revenue': room_rev + svc_rev,
            }

        current = period_stats(dt_from, dt_to)
        span = (dt_to - dt_from).days + 1
        prev = period_stats(
            dt_from - timedelta(days=span), dt_from - timedelta(days=1))

        def delta(cur, old):
            if not old:
                return None
            return (cur - old) / old * 100.0

        return {
            'today': {
                'occupied': occupied_today,
                'total_rooms': len(rooms),
                'occupancy': occupied_today / total_rooms * 100.0,
                'arrivals': arrivals,
                'departures': departures,
                'inhouse_guests': inhouse_guests,
                'inhouse_reservations': len(inhouse),
            },
            'period': current,
            'deltas': {
                'occupancy': delta(current['occupancy'],
                                   prev['occupancy']),
                'adr': delta(current['adr'], prev['adr']),
                'revpar': delta(current['revpar'], prev['revpar']),
                'total_revenue': delta(current['total_revenue'],
                                       prev['total_revenue']),
            },
        }

    # ------------------------------------------------------------------
    # Room board
    # ------------------------------------------------------------------

    @api.model
    def get_room_board(self, hotel_id=None):
        hotels = self._hotels(hotel_id)
        rooms = self.env['aite.hotel.room'].search([
            ('hotel_id', 'in', hotels.ids),
        ], order='hotel_id, floor_id, name')
        board = []
        for room in rooms:
            line = room.current_line_id
            board.append({
                'id': room.id,
                'name': room.name,
                'type': room.room_type_id.code or room.room_type_id.name,
                'floor': room.floor_id.name or "",
                'hotel': room.hotel_id.name,
                'status': room.status,
                'hk_state': room.hk_state,
                'guest': line.partner_id.name if line else "",
                'until': fields.Date.to_string(line.checkout_date.date())
                         if line and room.status == 'occupied' else "",
                'reservation_id': line.reservation_id.id if line else 0,
            })
        return board

    # ------------------------------------------------------------------
    # Mouvements du jour
    # ------------------------------------------------------------------

    @api.model
    def get_today_movements(self, hotel_id=None):
        hotels = self._hotels(hotel_id)
        today = fields.Date.context_today(self)
        day_start = fields.Datetime.to_datetime(str(today))
        day_end = day_start + timedelta(days=1)
        Res = self.env['aite.hotel.reservation']

        def serialize(reservations, date_field):
            return [{
                'id': r.id,
                'name': r.name,
                'guest': r.partner_id.name,
                'rooms': ", ".join(r.line_ids.mapped('room_id.name')),
                'time': fields.Datetime.to_string(r[date_field]),
                'residual': r.folio_id.amount_residual if r.folio_id
                            else 0.0,
            } for r in reservations]

        arrivals = Res.search([
            ('hotel_id', 'in', hotels.ids),
            ('state', '=', 'confirmed'),
            ('checkin_date', '>=', day_start),
            ('checkin_date', '<', day_end),
        ], order='checkin_date')
        departures = Res.search([
            ('hotel_id', 'in', hotels.ids),
            ('state', '=', 'checked_in'),
            ('checkout_date', '>=', day_start),
            ('checkout_date', '<', day_end),
        ], order='checkout_date')
        return {
            'arrivals': serialize(arrivals, 'checkin_date'),
            'departures': serialize(departures, 'checkout_date'),
        }

    # ------------------------------------------------------------------
    # Graphiques
    # ------------------------------------------------------------------

    @api.model
    def get_occupancy_evolution(self, date_from, date_to, hotel_id=None):
        """Taux d'occupation jour par jour sur la période."""
        dt_from, dt_to = self._parse_period(date_from, date_to)
        hotels = self._hotels(hotel_id)
        total = len(self._sellable_rooms(hotels)) or 1
        _nights, per_day = self._occupied_room_nights(
            hotels, dt_from, dt_to)
        labels, values = [], []
        day = dt_from
        while day <= dt_to:
            labels.append(day.strftime('%d/%m'))
            values.append(round(per_day.get(day, 0) / total * 100.0, 1))
            day += timedelta(days=1)
        return {'labels': labels, 'values': values}

    @api.model
    def get_revenue_by_type(self, date_from, date_to, hotel_id=None):
        """CA hébergement HT ventilé par type de chambre."""
        dt_from, dt_to = self._parse_period(date_from, date_to)
        hotels = self._hotels(hotel_id)
        lines = self.env['aite.hotel.folio.line'].search([
            ('folio_id.hotel_id', 'in', hotels.ids),
            ('line_type', '=', 'room'),
            ('folio_id.state', '!=', 'cancelled'),
            ('date', '>=', dt_from),
            ('date', '<=', dt_to),
        ])
        totals = defaultdict(float)
        for line in lines:
            rtype = line.reservation_line_id.room_type_id
            totals[rtype.name or _("Autre")] += line.price_subtotal
        items = sorted(totals.items(), key=lambda kv: -kv[1])
        return {
            'labels': [name for name, _v in items],
            'values': [round(v, 0) for _n, v in items],
        }

    @api.model
    def get_housekeeping_summary(self, hotel_id=None):
        hotels = self._hotels(hotel_id)
        rooms = self.env['aite.hotel.room'].search([
            ('hotel_id', 'in', hotels.ids),
        ])
        return {
            'to_clean': len(rooms.filtered(
                lambda r: r.hk_state == 'to_clean')),
            'cleaning': len(rooms.filtered(
                lambda r: r.hk_state == 'cleaning')),
            'inspect': len(rooms.filtered(
                lambda r: r.hk_state == 'inspect')),
            'out_of_order': len(rooms.filtered('out_of_order')),
        }
