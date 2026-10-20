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
        # ``sudo`` obligatoire : la fiche partenaire de la société n'est pas
        # lisible par le visiteur public (règle d'enregistrement sur
        # res.partner). Sans cela, TOUT envoi du formulaire — créneau comme
        # demande de séjour — se soldait par une page 403 : le tunnel
        # s'affichait mais aucune réservation ne pouvait aboutir.
        company_tz = request.env.company.sudo().partner_id.tz
        return pytz.timezone(
            company_tz or request.env.user.sudo().tz or 'Africa/Conakry')

    def _local_to_utc(self, day_str, hour_float):
        """'YYYY-MM-DD' + heure décimale locale → datetime UTC naïf."""
        day = datetime.strptime(day_str, '%Y-%m-%d')
        hh = int(hour_float)
        mm = int(round((hour_float - hh) * 60))
        naive = day.replace(hour=hh, minute=mm)
        localized = self._tz().localize(naive)
        return localized.astimezone(pytz.utc).replace(tzinfo=None)

    def _now_local(self):
        """Maintenant, dans le fuseau de l'établissement."""
        return datetime.now(self._tz())

    def _today_str(self):
        # Le jour de l'établissement, pas celui du visiteur public.
        return fields.Date.to_string(self._now_local().date())

    def _safe_day(self, day):
        """Jour demandé, ramené à aujourd'hui s'il est illisible ou passé
        (écart n° 34 : les jours passés ne sont plus proposés)."""
        today = self._today_str()
        try:
            datetime.strptime(day or '', '%Y-%m-%d')
        except ValueError:
            return today
        return day if day >= today else today

    def _now_h(self, day):
        """Heure locale décimale actuelle si ``day`` est aujourd'hui (les
        créneaux déjà commencés ne sont plus proposés), sinon ``None``."""
        if day != self._today_str():
            return None
        now = self._now_local()
        return now.hour + now.minute / 60.0

    def _grid(self, resource, day):
        """Grille du jour, lue dans le fuseau de l'établissement — le même
        que celui qui convertit l'heure choisie (``_local_to_utc``)."""
        return request.env['aite.booking.resource'].sudo().with_context(
            tz=self._tz().zone).get_day_grid(resource.id, day)

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
        grid = self._grid(resource, day)
        free = [s for s in grid['slots'] if s['state'] == 'free']
        free = request.env['aite.website.booking']._future_slots(
            free, self._now_h(day))
        return request.render('aite_website_booking.space_grid', {
            'resource': resource,
            'day': day,
            'today': self._today_str(),
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

        start_slots, k = self._service_starts(resource, service, day)
        start_slots = request.env['aite.website.booking']._future_slots(
            start_slots, self._now_h(day))
        return request.render('aite_website_booking.service_grid', {
            'service': service,
            'resource': resource,
            'resources': resources,
            'day': day,
            'today': self._today_str(),
            'start_slots': start_slots,
            'duration_slots': k,
            'error': error,
        })

    def _service_starts(self, resource, service, day):
        """Heures de début libres pour une prestation de ``k`` créneaux
        consécutifs (``k`` = durée arrondie au pas, cf.
        ``_slot_minutes_for``)."""
        grid = self._grid(resource, day)
        helper = request.env['aite.website.booking']
        step = grid['resource']['slot_minutes']
        minutes = helper._slot_minutes_for(
            service.duration_minutes if service else step, step)
        k = minutes // step
        starts = helper._fit_starts(grid['slots'], k)
        return [grid['slots'][i] for i in starts], k

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
        # Jour posté tel quel (non ramené à aujourd'hui) : un jour passé
        # doit être refusé ci-dessous, pas réservé à la date du jour.
        day = post.get('date') or ''
        try:
            datetime.strptime(day, '%Y-%m-%d')
        except ValueError:
            day = self._today_str()
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

        # Fin de créneau : durée de la prestation arrondie au pas de la
        # ressource (écart n° 34), sinon 1 pas.
        step = int(resource.slot_minutes or '60')
        minutes = helper._slot_minutes_for(
            service.duration_minutes if service else step, step)
        start_dt = self._local_to_utc(day, start_h)
        stop_dt = start_dt + timedelta(minutes=minutes)

        # Écart n° 34 : un créneau déjà commencé (ou d'un jour passé) n'est
        # pas vendu, même si l'adresse ou le formulaire a été forgé.
        if start_dt <= fields.Datetime.now():
            return request.redirect(back + '&error=past')

        # Créneau encore proposé par la grille ? Refus immédiat sinon : ni
        # contact ni numéro de réservation consommés pour une tentative
        # perdue d'avance (écart n° 35).
        if service:
            offered, _k = self._service_starts(resource, service, day)
        else:
            offered = [s for s in self._grid(resource, day)['slots']
                       if s['state'] == 'free']
        if not any(abs(s['start'] - start_h) < 1e-4 for s in offered):
            return request.redirect(back + '&error=slot')

        Booking = env['aite.slot.booking'].sudo()
        try:
            # Point de sauvegarde : si le créneau vient d'être pris entre
            # l'affichage et l'envoi (ou n'est pas valide), la création est
            # annulée avec la confirmation — y compris le contact client
            # (écart n° 35). Sans cela, chaque tentative refusée laissait
            # une réservation fantôme en brouillon dans le back-office.
            with env.cr.savepoint():
                partner = helper.find_or_create_partner(
                    post.get('name'), post.get('phone'), post.get('email'))
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
