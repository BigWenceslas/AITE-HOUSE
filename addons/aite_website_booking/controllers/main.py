# -*- coding: utf-8 -*-
import logging
from datetime import datetime, timedelta

import pytz

from odoo import fields, http, _
from odoo.exceptions import ValidationError
from odoo.http import request

_logger = logging.getLogger(__name__)


class WebsiteBooking(http.Controller):
    """
    Tunnel public de réservation.

    Les disponibilités viennent de ``aite.booking.resource.get_day_grid``
    — la même API que le tableau de bord interne. Point d'ancrage
    paiement en ligne : ``_confirm_slot`` (brancher un
    ``payment.provider`` avant la page de remerciement ; repli actuel :
    acompte au comptoir Orange Money / MTN MoMo).
    """

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _tz(self):
        return pytz.timezone(
            request.env.company.partner_id.tz
            or request.env.user.tz or 'Africa/Conakry')

    def _local_to_utc(self, day_str, hour_float):
        """'YYYY-MM-DD' + heure décimale locale → datetime UTC naïf."""
        day = datetime.strptime(day_str, '%Y-%m-%d')
        hh = int(hour_float)
        mm = int(round((hour_float - hh) * 60))
        naive = day.replace(hour=hh, minute=mm)
        localized = self._tz().localize(naive)
        return localized.astimezone(pytz.utc).replace(tzinfo=None)

    def _today_str(self):
        return fields.Date.to_string(
            fields.Date.context_today(request.env.user))

    def _safe_day(self, day):
        try:
            datetime.strptime(day or '', '%Y-%m-%d')
            return day
        except ValueError:
            return self._today_str()

    def _resources(self, kinds):
        return request.env['aite.booking.resource'].sudo().search([
            ('kind', 'in', list(kinds)),
            ('allow_online', '=', True),
        ])

    # ------------------------------------------------------------------
    # Accueil
    # ------------------------------------------------------------------

    @http.route('/reservation', type='http', auth='public',
                website=True, sitemap=True)
    def landing(self, **kw):
        return request.render('aite_website_booking.landing', {})

    # ------------------------------------------------------------------
    # Espaces VIP / VVIP (D1)
    # ------------------------------------------------------------------

    @http.route('/reservation/espaces', type='http', auth='public',
                website=True, sitemap=True)
    def spaces(self, **kw):
        return request.render('aite_website_booking.spaces', {
            'resources': self._resources(('space',)),
        })

    @http.route('/reservation/espace/<int:resource_id>', type='http',
                auth='public', website=True, sitemap=False)
    def space_grid(self, resource_id, date=None, error='', **kw):
        Resource = request.env['aite.booking.resource'].sudo()
        resource = Resource.browse(resource_id).exists()
        if not resource or not resource.allow_online:
            return request.redirect('/reservation/espaces')
        day = self._safe_day(date)
        grid = Resource.get_day_grid(resource.id, day)
        free = [s for s in grid['slots'] if s['state'] == 'free']
        return request.render('aite_website_booking.space_grid', {
            'resource': resource,
            'day': day,
            'free_slots': free,
            'error': error,
        })

    # ------------------------------------------------------------------
    # Prestations SPA & coiffure (D2)
    # ------------------------------------------------------------------

    @http.route('/reservation/prestations', type='http', auth='public',
                website=True, sitemap=True)
    def services(self, **kw):
        services = request.env['aite.booking.service'].sudo().search([
            ('kind', 'in', ('spa', 'hair')),
        ])
        return request.render('aite_website_booking.services', {
            'services': services,
        })

    @http.route('/reservation/prestation/<int:service_id>', type='http',
                auth='public', website=True, sitemap=False)
    def service_grid(self, service_id, resource_id=None, date=None,
                     error='', **kw):
        Service = request.env['aite.booking.service'].sudo()
        service = Service.browse(service_id).exists()
        if not service:
            return request.redirect('/reservation/prestations')
        resources = self._resources((service.kind,))
        if not resources:
            return request.redirect('/reservation/prestations')
        resource = resources.filtered(
            lambda r: r.id == int(resource_id or 0)) or resources[0]
        day = self._safe_day(date)

        Resource = request.env['aite.booking.resource'].sudo()
        grid = Resource.get_day_grid(resource.id, day)
        helper = request.env['aite.website.booking']
        step = grid['resource']['slot_minutes']
        k = max(1, -(-(service.duration_minutes or step) // step))
        starts = helper._fit_starts(grid['slots'], k)
        start_slots = [grid['slots'][i] for i in starts]
        return request.render('aite_website_booking.service_grid', {
            'service': service,
            'resource': resource,
            'resources': resources,
            'day': day,
            'start_slots': start_slots,
            'duration_slots': k,
            'error': error,
        })

    # ------------------------------------------------------------------
    # Confirmation créneau (espaces & prestations)
    # ------------------------------------------------------------------

    @http.route('/reservation/confirmer', type='http', auth='public',
                website=True, methods=['POST'], csrf=True)
    def confirm_slot(self, **post):
        return self._confirm_slot(post)

    def _confirm_slot(self, post):
        env = request.env
        helper = env['aite.website.booking']
        Resource = env['aite.booking.resource'].sudo()

        resource = Resource.browse(
            int(post.get('resource_id') or 0)).exists()
        day = self._safe_day(post.get('date'))
        try:
            start_h = float(post.get('start_h') or -1)
        except ValueError:
            start_h = -1.0
        service = env['aite.booking.service'].sudo().browse(
            int(post.get('service_id') or 0)).exists()

        back = ('/reservation/prestation/%s?resource_id=%s&date=%s'
                % (service.id, resource.id, day)) if service else \
            ('/reservation/espace/%s?date=%s'
             % (resource.id if resource else 0, day))

        code = helper._validate_online_booking(
            post.get('name'), post.get('phone'),
            bool(resource) and start_h >= 0)
        if code:
            return request.redirect(back + '&error=' + code)

        # Fin de créneau : durée de la prestation, sinon 1 pas.
        step = int(resource.slot_minutes or '60')
        minutes = (service.duration_minutes
                   if service else step) or step
        start_dt = self._local_to_utc(day, start_h)
        stop_dt = start_dt + timedelta(minutes=minutes)

        partner = helper.find_or_create_partner(
            post.get('name'), post.get('phone'), post.get('email'))

        Booking = env['aite.slot.booking'].sudo()
        try:
            booking = Booking.create({
                'resource_id': resource.id,
                'partner_id': partner.id,
                'service_id': service.id if service else False,
                'start': fields.Datetime.to_string(start_dt),
                'stop': fields.Datetime.to_string(stop_dt),
                'source': 'online',
            })
            booking.action_confirm()
        except ValidationError:
            _logger.info(
                "Résa en ligne refusée (conflit/créneau) : %s %s %.2f",
                resource.name, day, start_h)
            return request.redirect(back + '&error=slot')

        # ── Point d'ancrage paiement en ligne ─────────────────────────
        # Brancher ici un payment.provider (agrégateur OM / MoMo) :
        # rediriger vers le checkout avec booking.amount, puis
        # confirmer au retour. Repli actuel : acompte au comptoir.
        return request.render('aite_website_booking.thanks', {
            'mode': 'slot',
            'booking': booking,
        })

    # ------------------------------------------------------------------
    # Séjours — demande de réservation (PMS)
    # ------------------------------------------------------------------

    @http.route('/reservation/chambres', type='http', auth='public',
                website=True, sitemap=True)
    def rooms_form(self, error='', **kw):
        return request.render('aite_website_booking.rooms_form', {
            'error': error,
            'today': self._today_str(),
        })

    @http.route('/reservation/chambres/envoyer', type='http',
                auth='public', website=True, methods=['POST'], csrf=True)
    def rooms_submit(self, **post):
        env = request.env
        helper = env['aite.website.booking']
        code = helper._validate_online_booking(
            post.get('name'), post.get('phone'), True)
        checkin = self._safe_day(post.get('checkin'))
        checkout = post.get('checkout') or ''
        if not code:
            try:
                if datetime.strptime(checkout, '%Y-%m-%d') <= \
                        datetime.strptime(checkin, '%Y-%m-%d'):
                    code = 'dates'
            except ValueError:
                code = 'dates'
        if code:
            return request.redirect(
                '/reservation/chambres?error=' + code)

        partner = helper.find_or_create_partner(
            post.get('name'), post.get('phone'), post.get('email'))
        try:
            adults = max(1, int(post.get('adults') or 1))
        except ValueError:
            adults = 1
        reservation = env['aite.hotel.reservation'].sudo().create({
            'partner_id': partner.id,
            'checkin_date': fields.Datetime.to_string(
                self._local_to_utc(checkin, 14.0)),
            'checkout_date': fields.Datetime.to_string(
                self._local_to_utc(checkout, 11.0)),
            'adults': adults,
            'source': 'website',
            'note': _("Demande site web — %(n)s adulte(s). %(msg)s",
                      n=adults, msg=(post.get('message') or '')),
        })
        _logger.info("Demande de séjour site web : %s (%s).",
                     reservation.name, partner.name)
        return request.render('aite_website_booking.thanks', {
            'mode': 'room',
            'reservation': reservation,
        })

    # ------------------------------------------------------------------
    # Espace client
    # ------------------------------------------------------------------

    @http.route('/mes-reservations', type='http', auth='user',
                website=True, sitemap=False)
    def my_bookings(self, **kw):
        partner = request.env.user.partner_id
        bookings = request.env['aite.slot.booking'].sudo().search([
            ('partner_id', '=', partner.id),
        ], order='start desc', limit=40)
        stays = request.env['aite.hotel.reservation'].sudo().search([
            ('partner_id', '=', partner.id),
        ], order='checkin_date desc', limit=40)
        return request.render('aite_website_booking.my_bookings', {
            'bookings': bookings,
            'stays': stays,
        })
