# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from odoo import api, fields, models, _

# Familles de ressources — le même moteur sert D1 (espaces) et D2
# (prestations). Réutilisées par le service, la réservation, le tableau
# de bord et le site web.
KINDS = [
    ('space', "Espace VIP / VVIP"),
    ('spa', "SPA"),
    ('hair', "Coiffure"),
    ('pressing', "Pressing"),
    ('other', "Autre"),
]


class BookingResource(models.Model):
    """
    Ressource réservable par créneaux : salon VIP/VVIP, cabine SPA,
    fauteuil de coiffure, comptoir pressing…

    Chaque ressource porte ses horaires d'ouverture, son pas de créneau
    (30 ou 60 min), sa capacité (nombre de réservations simultanées) et,
    pour les espaces, un tarif horaire.

    Elle expose l'API de disponibilité ``get_day_grid`` — la **source de
    vérité unique** des créneaux, consommée par le tableau de bord ET par
    la réservation en ligne. Le calcul de grille est une fonction pure
    (``_build_day_slots``), extraite et exécutée telle quelle par les
    tests.
    """
    _name = 'aite.booking.resource'
    _description = "Ressource réservable (espace / prestation)"
    _order = 'sequence, name'

    name = fields.Char(string="Nom", required=True, translate=True)
    kind = fields.Selection(
        selection=KINDS, string="Famille", required=True, default='space',
        index=True,
    )
    sequence = fields.Integer(string="Séquence", default=10)
    active = fields.Boolean(default=True)
    hotel_id = fields.Many2one(
        'aite.hotel.hotel', string="Établissement", ondelete='set null',
    )
    company_id = fields.Many2one(
        'res.company', string="Société", required=True,
        default=lambda self: self.env.company,
    )
    currency_id = fields.Many2one(
        related='company_id.currency_id', readonly=True)

    capacity = fields.Integer(
        string="Capacité", default=1,
        help="Nombre de réservations simultanées possibles sur un même "
             "créneau (ex. 2 fauteuils interchangeables).",
    )
    open_hour = fields.Float(
        string="Ouverture", default=9.0,
        help="Heure d'ouverture (ex. 9,5 = 09:30).",
    )
    close_hour = fields.Float(string="Fermeture", default=22.0)
    slot_minutes = fields.Selection(
        selection=[('30', "30 minutes"), ('60', "1 heure")],
        string="Pas de créneau", default='60', required=True,
    )
    price_hour = fields.Monetary(
        string="Tarif horaire", currency_field='currency_id',
        help="Utilisé quand la réservation n'est pas liée à une "
             "prestation du catalogue (espaces VIP / VVIP).",
    )
    color = fields.Char(string="Couleur", default='#714B67')
    allow_online = fields.Boolean(
        string="Réservable en ligne", default=True,
        help="Proposée sur le site web (module réservation en ligne).",
    )
    note = fields.Text(string="Consignes internes")

    _sql_constraints = [
        ('capacity_positive', 'CHECK(capacity > 0)',
         "La capacité doit être strictement positive."),
        ('hours_order', 'CHECK(close_hour > open_hour)',
         "L'heure de fermeture doit être après l'ouverture."),
    ]

    # ------------------------------------------------------------------
    # Calcul pur (extrait et exécuté tel quel par les tests)
    # ------------------------------------------------------------------

    @staticmethod
    def _overlap_count(busy, start, stop):
        """
        Nombre d'intervalles de ``busy`` chevauchant [start, stop).

        Fonctionne sur tout type ordonnable (datetimes ou heures en
        float). Deux créneaux qui se touchent (fin == début) ne se
        chevauchent PAS.
        """
        n = 0
        for (s, e) in busy:
            if s < stop and e > start:
                n += 1
        return n

    @staticmethod
    def _build_day_slots(open_h, close_h, step_min, busy, capacity):
        """
        Grille des créneaux d'une journée.

        :param open_h/close_h: bornes en heures décimales (9.0, 22.0)
        :param step_min: pas en minutes (30 ou 60)
        :param busy: liste de (start_h, end_h) occupés, heures décimales
        :param capacity: capacité de la ressource
        :returns: liste de dicts {start, stop, label 'HH:MM', used,
            state 'free'|'partial'|'full'}
        """
        slots = []
        step = (step_min or 60) / 60.0
        h = float(open_h)
        while h + step <= float(close_h) + 1e-6:
            used = 0
            for (s, e) in busy:
                if s < h + step and e > h:
                    used += 1
            if capacity <= 0 or used >= capacity:
                state = 'full'
            elif used > 0:
                state = 'partial'
            else:
                state = 'free'
            hh = int(h + 1e-6)
            mm = int(round((h - hh) * 60))
            slots.append({
                'start': round(h, 4),
                'stop': round(h + step, 4),
                'label': '%02d:%02d' % (hh, mm),
                'used': used,
                'state': state,
            })
            h += step
        return slots

    # ------------------------------------------------------------------
    # API de disponibilité (source unique : dashboard + site web)
    # ------------------------------------------------------------------

    def _local_hours(self, dt):
        """Datetime UTC stocké → heure locale décimale (tz utilisateur)."""
        local = fields.Datetime.context_timestamp(self, dt)
        return local.hour + local.minute / 60.0

    def _local_date(self, dt):
        return fields.Datetime.context_timestamp(self, dt).date()

    @api.model
    def get_day_grid(self, resource_id, day):
        """
        Grille de disponibilité d'une ressource pour un jour local.

        :param day: 'YYYY-MM-DD' (jour dans le fuseau de l'utilisateur)
        :returns: {resource, slots, bookings} — ``bookings`` alimente les
            couloirs du planning (heures locales, clippées aux horaires).
        """
        res = self.browse(int(resource_id))
        res.ensure_one()
        try:
            day_date = datetime.strptime(day, '%Y-%m-%d').date()
        except (TypeError, ValueError):
            day_date = fields.Date.context_today(self)

        # Fenêtre UTC large (±1 jour) puis filtrage sur le jour LOCAL.
        d0 = fields.Datetime.to_string(
            datetime.combine(day_date - timedelta(days=1),
                             datetime.min.time()))
        d1 = fields.Datetime.to_string(
            datetime.combine(day_date + timedelta(days=1),
                             datetime.max.time()))
        Booking = self.env['aite.slot.booking']
        bookings = Booking.search([
            ('resource_id', '=', res.id),
            ('state', 'in', ('confirmed', 'done')),
            ('start', '<=', d1), ('stop', '>=', d0),
        ])

        busy = []
        lanes = []
        for b in bookings:
            if self._local_date(b.start) != day_date \
                    and self._local_date(b.stop) != day_date:
                continue
            s_h = self._local_hours(b.start) \
                if self._local_date(b.start) == day_date else res.open_hour
            e_h = self._local_hours(b.stop) \
                if self._local_date(b.stop) == day_date else res.close_hour
            s_h = max(s_h, res.open_hour)
            e_h = min(e_h, res.close_hour)
            if e_h <= s_h:
                continue
            busy.append((s_h, e_h))
            lanes.append({
                'id': b.id,
                'partner': b.partner_id.name or "",
                'label': b.service_id.name or b.name,
                'start_h': round(s_h, 4),
                'stop_h': round(e_h, 4),
                'state': b.state,
            })

        slots = self._build_day_slots(
            res.open_hour, res.close_hour, int(res.slot_minutes or '60'),
            busy, res.capacity)
        return {
            'resource': {
                'id': res.id, 'name': res.name, 'kind': res.kind,
                'capacity': res.capacity, 'color': res.color or '#714B67',
                'open_hour': res.open_hour, 'close_hour': res.close_hour,
                'slot_minutes': int(res.slot_minutes or '60'),
                'price_hour': res.price_hour,
            },
            'slots': slots,
            'bookings': lanes,
        }
