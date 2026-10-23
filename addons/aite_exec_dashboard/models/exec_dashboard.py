# -*- coding: utf-8 -*-
from datetime import date, datetime, timedelta

import pytz

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

# Une phrase par indicateur hôtelier, pour un gérant qui découvre le
# vocabulaire. Servie par ``get_meta`` (infobulles) et reprise telle
# quelle par le cockpit Direction : un seul texte pour un seul chiffre.
KPI_HINTS = {
    'occupancy': "Taux d'occupation : part des chambres disponibles qui "
                 "ont été vendues sur la période (chambres hors service "
                 "exclues).",
    'adr': "Prix moyen par nuit (ADR) : ce que rapporte en moyenne une "
           "chambre vendue par nuit, hors taxes et hors services.",
    'revpar': "Revenu par chambre disponible (RevPAR) : ce que rapporte "
              "chaque chambre disponible, vendue ou non — c'est "
              "l'indicateur qui combine prix et remplissage.",
    'pickup': "Réservations récentes (pickup) : nuitées prises ces 7 "
              "derniers jours pour les 30 prochains jours — la demande qui "
              "arrive en ce moment.",
    'pace': "Rythme du mois (pace) : nuitées déjà réservées pour le mois "
            "en cours, comparées à celles qui l'étaient à la même date l'an "
            "dernier.",
    'last_year': "Écart en couleur : par rapport à la même période l'an "
                 "dernier (vert = mieux, rouge = moins bien).",
}


class ExecDashboard(models.AbstractModel):
    """
    Fournisseur du tableau de bord Direction — consolidation des trois
    pôles du complexe.

    Sources (une par pôle, jamais deux chiffres pour la même chose — cas
    K04 de la recette, écart n° 25) :

    * hébergement : CA des nuitées HORS TAXES, nuit par nuit, relu
      depuis le fournisseur du PMS (``room_revenue``) — le même chiffre
      que le cockpit Direction et le tableau de bord hôtelier, cohérent
      avec ADR et RevPAR (ADR × nuitées = CA) ; occupation et ADR
      viennent du même appel ;
    * restauration & boutique : commandes POS réglées (date de
      commande), HORS TAXES (somme des lignes) — comme l'analyse des
      ventes et le cockpit Direction ;
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

    def _period_tz(self):
        """Fuseau des jours de la période : celui du contexte, sinon celui
        de l'utilisateur, sinon UTC — la règle du moteur Ventes
        (``aite.pos.dashboard._period_tz``) et du tableau de bord des
        créneaux. Copiée ici : ce module ne dépend pas de l'analyse des
        ventes."""
        tz_name = self.env.context.get('tz') or self.env.user.tz
        if tz_name in pytz.all_timezones_set:
            return pytz.timezone(tz_name)
        return pytz.utc

    def _day_bounds(self, dt_from, dt_to):
        """Jours LOCAUX ``dt_from`` → ``dt_to`` (inclus) en bornes UTC
        pour un champ date-heure : [minuit local du premier jour, minuit
        local du lendemain du dernier jour[ — borne de fin EXCLUSIVE.

        Les bornes étaient 00:00 → 23:59:59 UTC : à Douala (UTC+1), un
        ticket encaissé à 0 h 30 le 1er du mois (23 h 30 UTC la veille)
        comptait dans le mois précédent ici, et dans le bon mois sur le
        cockpit Direction et l'analyse des ventes (relecture du cas K04).
        """
        tz = self._period_tz()

        def to_utc(day):
            local = tz.localize(datetime.combine(day, datetime.min.time()))
            return fields.Datetime.to_string(
                local.astimezone(pytz.utc).replace(tzinfo=None))
        return to_utc(dt_from), to_utc(dt_to + timedelta(days=1))

    # ------------------------------------------------------------------
    # Sources par pôle (une seule définition chacune)
    # ------------------------------------------------------------------

    def _hotel_revenue(self, dt_from, dt_to):
        """CA hébergement HT, nuit par nuit, de la société courante :
        la formule du PMS (``_room_revenue``), pas une copie. Le TTC des
        folios facturés au départ datait tout le séjour du jour de départ
        et n'était ni le chiffre du cockpit ni la base de l'ADR."""
        hk = self.env['aite.hotel.dashboard']
        return hk._room_revenue(hk._hotels(), dt_from, dt_to)

    @staticmethod
    def _pos_revenue(orders):
        """CA POS hors taxes : somme des lignes (``price_subtotal``)."""
        return sum(orders.mapped('lines.price_subtotal'))

    def _pos_orders(self, dt_from, dt_to):
        d0, d1 = self._day_bounds(dt_from, dt_to)
        return self.env['pos.order'].search([
            ('company_id', '=', self.env.company.id),
            ('state', 'in', _POS_PAID_STATES),
            ('date_order', '>=', d0), ('date_order', '<', d1),
        ])

    def _slot_bookings(self, dt_from, dt_to):
        d0, d1 = self._day_bounds(dt_from, dt_to)
        return self.env['aite.slot.booking'].search([
            ('company_id', '=', self.env.company.id),
            ('state', '=', 'done'),
            ('start', '>=', d0), ('start', '<', d1),
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
            'hints': dict(KPI_HINTS),
            'poles': [
                {'key': k, 'label': _POLE_LABELS[k],
                 'color': _POLE_COLORS[k]}
                for k in ('hotel', 'pos', 'slots')
            ],
        }

    @api.model
    def get_kpis(self, date_from, date_to):
        dt_from, dt_to = self._parse_period(date_from, date_to)

        # Hébergement — occupation, ADR, RevPAR, N-1, pickup et pace sont
        # relus depuis le fournisseur du PMS : mêmes chiffres que son
        # propre tableau de bord, aucune formule dupliquée ici.
        hotel_ca = self._hotel_revenue(dt_from, dt_to)
        occupancy = adr = revpar = 0.0
        nights_sold = 0
        deltas_ly = {'occupancy': None, 'adr': None, 'revpar': None,
                     'room_revenue': None}
        pickup = {'nights': 0, 'reservations': 0,
                  'window_days': 7, 'horizon_days': 30}
        pace = {'month': dt_to.strftime('%Y-%m'), 'nights': 0,
                'nights_ly': 0, 'delta': None}
        try:
            hk = self.env['aite.hotel.dashboard'].get_kpis(
                fields.Date.to_string(dt_from),
                fields.Date.to_string(dt_to))
            period = hk.get('period') or {}
            occupancy = period.get('occupancy') or 0.0
            adr = period.get('adr') or 0.0
            revpar = period.get('revpar') or 0.0
            nights_sold = period.get('nights_sold') or 0
            deltas_ly.update(hk.get('deltas_ly') or {})
            pickup.update(hk.get('pickup') or {})
            pace.update(hk.get('pace') or {})
        except Exception:
            pass  # le consolidé reste servi même si le PMS évolue

        # Restauration & boutique
        orders = self._pos_orders(dt_from, dt_to)
        pos_ca = self._pos_revenue(orders)
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
            'revpar': revpar,
            'nights_sold': nights_sold,
            'deltas_ly': deltas_ly,
            'pickup': pickup,
            'pace': pace,
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
            pos_s.append(self._pos_revenue(self._pos_orders(start, end)))
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
