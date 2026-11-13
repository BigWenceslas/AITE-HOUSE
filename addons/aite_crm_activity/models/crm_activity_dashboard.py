# -*- coding: utf-8 -*-
import re
from collections import defaultdict
from datetime import date, datetime, time, timedelta

import pytz
from dateutil.relativedelta import MO, relativedelta
from markupsafe import Markup

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError
from odoo.tools.mail import html_to_inner_content

from .crm_activity_params import actionable_activity_domain, get_thresholds, severity

ACTIVITY_LIMIT = 80    # lignes de la liste des activités
STALLED_LIMIT = 50     # lignes de la liste « sans activité »

# Sélections de la liste des activités.
BUCKETS = ('all', 'overdue', 'today', 'upcoming', 'done')

# Valeur du filtre « Commercial » pour les activités et opportunités sans
# personne assignée.
UNASSIGNED = 'unassigned'

# Reports proposés par le menu « Reporter » (calculés côté serveur, sur la
# date du jour de l'utilisateur).
RESCHEDULE_PRESETS = ('tomorrow', 'monday', 'week')

# Périodes des activités réalisées. « 7d » : les 7 derniers jours,
# aujourd'hui compris (période par défaut).
PERIODS = ('7d', 'month', 'last_month', 'quarter', 'custom')
DEFAULT_PERIOD = '7d'
MAX_PERIOD_DAYS = 366          # une période personnalisée couvre au plus 366 jours
MIN_PERIOD_DATE = date(1900, 1, 1)

WORKLOAD_MAX_DAYS = 13         # plan de charge : aujourd'hui + 13 jours au plus
TREND_WEEKS = 12               # tendances : les 12 dernières semaines ISO
PREVIEW_DONE_LIMIT = 5         # aperçu : les 5 dernières activités réalisées

# Jours abrégés du plan de charge (lundi = 0, comme date.weekday()).
WEEKDAYS_SHORT = ('lun.', 'mar.', 'mer.', 'jeu.', 'ven.', 'sam.', 'dim.')


# ----------------------------------------------------------------------
# Calculs sans base de données (testables isolément)
# ----------------------------------------------------------------------

def _to_date(value):
    """ Date lue d'une chaîne AAAA-MM-JJ (ou d'une date) ; None si illisible. """
    if not isinstance(value, (str, date)):
        return None
    try:
        return fields.Date.to_date(value) or None
    except (TypeError, ValueError):
        return None


def resolve_period(key, date_from, date_to, today):
    """ Période des activités réalisées → ``(clé, début, fin)`` (dates
    incluses), toujours calculée à partir de ``today``, la date du jour de
    l'utilisateur côté serveur.

    - clé inconnue → « 7 derniers jours » ;
    - « custom » : dates illisibles → « 7 derniers jours » ; bornes
      inversées → échangées ; fin future → ramenée à aujourd'hui ; plus de
      366 jours → la fin est gardée, le début rapproché.
    """
    if key not in PERIODS:
        key = DEFAULT_PERIOD
    if key == 'custom':
        start, end = _to_date(date_from), _to_date(date_to)
        if not start or not end or start < MIN_PERIOD_DATE or end < MIN_PERIOD_DATE:
            key = DEFAULT_PERIOD
        else:
            if start > end:
                start, end = end, start
            end = min(end, today)
            start = min(start, end)
            if (end - start).days + 1 > MAX_PERIOD_DAYS:
                start = end - timedelta(days=MAX_PERIOD_DAYS - 1)
            return key, start, end
    if key == 'month':
        return key, today.replace(day=1), today
    if key == 'last_month':
        end = today.replace(day=1) - timedelta(days=1)
        return key, end.replace(day=1), end
    if key == 'quarter':
        return key, date(today.year, 3 * ((today.month - 1) // 3) + 1, 1), today
    return DEFAULT_PERIOD, today - timedelta(days=6), today


def previous_period(date_from, date_to):
    """ Période précédente de même durée, qui finit la veille de ``date_from``. """
    days = (date_to - date_from).days + 1
    prev_to = date_from - timedelta(days=1)
    return prev_to - timedelta(days=days - 1), prev_to


def delta_pct(current, previous):
    """ Évolution en % par rapport à la période précédente (1 décimale) ;
    None quand la période précédente est à 0 (pas de base de comparaison).
    On divise par la valeur absolue : le signe suit toujours le sens de
    l'évolution. """
    if not previous:
        return None
    return round((current - previous) / abs(previous) * 100, 1)


def percentage(part, total):
    """ Part en % (0 à 100, 1 décimale) ; None si ``total`` est nul. """
    if not total:
        return None
    return round(part * 100.0 / total, 1)


def iso_weeks(today, count=TREND_WEEKS):
    """ Les ``count`` semaines ISO (lundi → dimanche) qui finissent par la
    semaine de ``today``, de la plus ancienne à la plus récente. """
    monday = today - timedelta(days=today.weekday())
    weeks = []
    for index in range(count - 1, -1, -1):
        start = monday - timedelta(weeks=index)
        year, week, __ = start.isocalendar()
        weeks.append({
            'key': '%04d-W%02d' % (year, week),
            'label': start.strftime('%d/%m'),
            'date_from': start,
            'date_to': start + timedelta(days=6),
        })
    return weeks


def week_index(first_monday, day, count):
    """ Rang de la semaine de ``day`` parmi ``count`` semaines qui commencent
    le lundi ``first_monday`` ; None si ``day`` est en dehors. """
    if not day:
        return None
    if isinstance(day, datetime):
        day = day.date()
    index = (day - first_monday).days // 7
    return index if 0 <= index < count else None


def bucket_counts_by_week(rows, first_monday, count):
    """ ``rows`` : couples (date, nombre) → nombre par semaine. """
    result = [0] * count
    for day, number in rows:
        index = week_index(first_monday, day, count)
        if index is not None:
            result[index] += number
    return result


def bucket_done_by_week(rows, first_monday, count):
    """ ``rows`` : triplets (date de réalisation, échéance, nombre) des
    activités réalisées → (à temps, en retard), deux listes d'un nombre par
    semaine. « À temps » : réalisée au plus tard le jour de l'échéance. """
    on_time, late = [0] * count, [0] * count
    for done, deadline, number in rows:
        index = week_index(first_monday, done, count)
        if index is None:
            continue
        if is_done_late(done, deadline):
            late[index] += number
        else:
            on_time[index] += number
    return on_time, late


def is_done_late(date_done, date_deadline):
    """ Réalisée après l'échéance ? (date_done est une date UTC, voir
    ``_bucket_domain``.) """
    return bool(date_done and date_deadline and date_done > date_deadline)


class AiteCrmActivityDashboard(models.AbstractModel):
    """ Données et actions du tableau de bord « Suivi des activités ».

    Toutes les lectures se font avec les droits de l'utilisateur : il ne
    voit que les activités et opportunités qu'Odoo l'autorise à voir. Une
    activité qui lui est assignée sur une opportunité qu'il ne peut pas
    ouvrir reste listée (Odoo la lui montre aussi), sans les détails de
    l'opportunité.

    Les activités ouvertes des opportunités archivées (perdues) ne sont pas
    « à faire » : elles sortent des indicateurs, des listes, du tableau par
    commercial et du plan de charge (``actionable_activity_domain``). Les
    activités déjà réalisées restent comptées.
    """
    _name = 'aite.crm.activity.dashboard'
    _description = "Suivi des activités CRM"

    # ------------------------------------------------------------------
    # Filtres et domaines
    # ------------------------------------------------------------------

    @api.model
    def _is_manager(self):
        return self.env.user.has_group('sales_team.group_sale_salesman_all_leads')

    @api.model
    def _check_dashboard_access(self):
        if not self.env.user.has_group('sales_team.group_sale_salesman'):
            raise AccessError(self.env._(
                "Le suivi des activités est réservé aux utilisateurs du CRM. Vos activités "
                "restent visibles dans le menu Activités (icône horloge)."))

    @api.model
    def _clean_filters(self, filters, today=None):
        """ Filtres reçus du navigateur → valeurs sûres. Sans filtre de
        commercial explicite, un responsable voit toute l'équipe et un
        commercial ses propres activités. La période est résolue côté
        serveur : ``date_from`` / ``date_to`` sont toujours les dates
        retenues (AAAA-MM-JJ). """
        filters = dict(filters or {})
        today = today or fields.Date.context_today(self)

        def _id(key):
            try:
                return int(filters.get(key) or 0) or False
            except (TypeError, ValueError):
                return False

        if filters.get('user_id') == UNASSIGNED:
            user_id = UNASSIGNED
        elif 'user_id' in filters:
            user_id = _id('user_id')
        else:
            user_id = False if self._is_manager() else self.env.uid
        bucket = filters.get('bucket')
        period, date_from, date_to = resolve_period(
            filters.get('period'), filters.get('date_from'), filters.get('date_to'), today)
        return {
            'user_id': user_id,
            'team_id': _id('team_id'),
            'activity_type_id': _id('activity_type_id'),
            'bucket': bucket if bucket in BUCKETS else 'all',
            'period': period,
            'date_from': fields.Date.to_string(date_from),
            'date_to': fields.Date.to_string(date_to),
        }

    @api.model
    def _dates(self, flt, today=None):
        today = today or fields.Date.context_today(self)
        thresholds = get_thresholds(self.env)
        done_from = fields.Date.to_date(flt['date_from'])
        done_to = fields.Date.to_date(flt['date_to'])
        prev_from, prev_to = previous_period(done_from, done_to)
        return {
            'today': today,
            'thresholds': thresholds,
            'upcoming_end': today + timedelta(days=thresholds['upcoming_days']),
            'done_from': done_from,
            'done_to': done_to,
            'prev_from': prev_from,
            'prev_to': prev_to,
        }

    @api.model
    def _period_label(self, key, date_from, date_to):
        labels = self._period_labels()
        if key == 'custom':
            return self.env._("Du %(date_from)s au %(date_to)s",
                              date_from=date_from.strftime('%d/%m/%Y'),
                              date_to=date_to.strftime('%d/%m/%Y'))
        return labels[key]

    @api.model
    def _period_labels(self):
        return {
            '7d': self.env._("7 derniers jours"),
            'month': self.env._("Ce mois"),
            'last_month': self.env._("Mois dernier"),
            'quarter': self.env._("Ce trimestre"),
            'custom': self.env._("Personnalisée"),
        }

    @api.model
    def _team_lead_ids(self, team_id):
        # Identifiants seulement, en sudo : les droits s'appliquent ensuite
        # aux activités elles-mêmes (une activité assignée à l'utilisateur
        # sur une opportunité de l'équipe qu'il ne peut pas ouvrir reste
        # visible, comme partout dans Odoo).
        return self.env['crm.lead'].sudo().with_context(active_test=False).search(
            [('team_id', '=', team_id)]).ids

    @api.model
    def _user_domain(self, flt):
        if flt['user_id'] == UNASSIGNED:
            return [('user_id', '=', False)]
        if flt['user_id']:
            return [('user_id', '=', flt['user_id'])]
        return []

    @api.model
    def _activity_domain(self, flt, lead_ids=None):
        """ Activités sur les pistes et opportunités, filtrées (commercial,
        équipe, type). Les domaines de ``_bucket_domain`` y ajoutent l'état
        (ouvertes « à faire », ou réalisées). """
        domain = [('res_model', '=', 'crm.lead')] + self._user_domain(flt)
        if flt['activity_type_id']:
            domain.append(('activity_type_id', '=', flt['activity_type_id']))
        if lead_ids is not None:
            domain.append(('res_id', 'in', lead_ids))
        return domain

    @api.model
    def _open_domain(self):
        """ Activités ouvertes « à faire » : celles des opportunités actives
        seulement (une opportunité perdue est archivée sans que ses
        activités soient fermées). """
        return actionable_activity_domain(self.env)

    @api.model
    def _bucket_domain(self, bucket, dates):
        """ Domaine d'une sélection. « done » : activités réalisées (donc
        archivées) dont la date de réalisation tombe dans la période.
        Attention : Odoo enregistre ``date_done`` comme la date UTC du
        moment où l'activité est marquée faite ; à Douala (UTC+1), une
        activité faite entre minuit et 1 h compte pour la veille.

        Les activités réalisées ne passent pas par ``_open_domain`` : une
        activité faite avant que l'opportunité soit perdue reste comptée. """
        if bucket == 'done':
            return [('active', '=', False),
                    ('date_done', '>=', dates['done_from']),
                    ('date_done', '<=', dates['done_to'])]
        today = dates['today']
        return self._open_domain() + {
            'all': [],
            'overdue': [('date_deadline', '<', today)],
            'today': [('date_deadline', '=', today)],
            'upcoming': [('date_deadline', '>', today),
                         ('date_deadline', '<=', dates['upcoming_end'])],
        }[bucket]

    @api.model
    def _activities(self, bucket):
        """ mail.activity, en incluant les activités réalisées (archivées)
        pour la sélection « done ». """
        activity = self.env['mail.activity']
        return activity.with_context(active_test=False) if bucket == 'done' else activity

    @api.model
    def _stalled_domain(self, flt, lead_ids=None):
        """ Opportunités ouvertes, ni gagnées ni perdues, sans activité
        planifiée. « activity_state = False » ne compte que les activités
        ouvertes : une opportunité dont la dernière activité vient d'être
        marquée comme faite (archivée) y figure bien, contrairement à
        « activity_ids = False ». Le filtre de type d'activité ne peut pas
        s'appliquer ici (il n'y a justement pas d'activité). """
        domain = [
            ('type', '=', 'opportunity'),
            ('activity_state', '=', False),
            ('won_status', '=', 'pending'),
        ] + self._user_domain(flt)
        if lead_ids is not None:
            domain.append(('id', 'in', lead_ids))
        return domain

    @api.model
    def _utc_bounds(self, date_from, date_to):
        """ Journées locales [date_from, date_to] de l'utilisateur → bornes
        UTC naïves [début, fin[ pour un champ Datetime (create_date). """
        tz = self.env.tz

        def _utc(day):
            local = tz.localize(datetime.combine(day, time.min))
            return local.astimezone(pytz.utc).replace(tzinfo=None)
        return _utc(date_from), _utc(date_to + timedelta(days=1))

    # ------------------------------------------------------------------
    # Données
    # ------------------------------------------------------------------

    @api.model
    @api.readonly
    def get_dashboard_data(self, filters=None):
        self._check_dashboard_access()
        today = fields.Date.context_today(self)
        flt = self._clean_filters(filters, today=today)
        dates = self._dates(flt, today=today)
        thresholds = dates['thresholds']
        lead_ids = self._team_lead_ids(flt['team_id']) if flt['team_id'] else None
        base = self._activity_domain(flt, lead_ids)

        open_groups = self._open_groups_by_user(flt, dates, lead_ids)
        by_user = self._get_by_user(flt, dates, lead_ids, open_groups)
        stalled = self._get_stalled(flt, dates, lead_ids)
        kpis = self._get_kpis(dates, base)
        kpis['stalled'] = stalled['total']
        kpis['stalled_amounts'] = stalled['amounts']

        return {
            'filters': flt,
            'is_manager': self._is_manager(),
            'today': fields.Date.to_string(today),
            'upcoming_days': thresholds['upcoming_days'],
            'done_days': (dates['done_to'] - dates['done_from']).days + 1,
            'period': {
                'key': flt['period'],
                'label': self._period_label(flt['period'], dates['done_from'], dates['done_to']),
                'date_from': flt['date_from'],
                'date_to': flt['date_to'],
                'prev_from': fields.Date.to_string(dates['prev_from']),
                'prev_to': fields.Date.to_string(dates['prev_to']),
                'days': (dates['done_to'] - dates['done_from']).days + 1,
            },
            'thresholds': thresholds,
            'kpis': kpis,
            'alerts': self._get_alerts(kpis, stalled, thresholds),
            'filter_notes': {'stalled_ignores_type': bool(flt['activity_type_id'])},
            'by_user': by_user,
            'activities': self._get_activities(flt, dates, base),
            'stalled': stalled,
            'workload': self._get_workload(dates, open_groups),
            'options': self._get_options(flt, by_user),
        }

    @api.model
    def _new_open_counts(self):
        return {'overdue': 0, 'today': 0, 'upcoming': 0, 'high': 0, 'critical': 0}

    @api.model
    def _add_open_count(self, counts, deadline, count, dates):
        """ Range ``count`` activités ouvertes d'échéance ``deadline`` dans
        ``counts`` (en retard, dont élevé / critique ; du jour ; à venir). """
        today = dates['today']
        if deadline < today:
            counts['overdue'] += count
            level = severity((today - deadline).days, dates['thresholds'])
            if level in ('high', 'critical'):
                counts['high'] += count
            if level == 'critical':
                counts['critical'] += count
        elif deadline == today:
            counts['today'] += count
        elif deadline <= dates['upcoming_end']:
            counts['upcoming'] += count

    @api.model
    def _done_stats(self, base, date_from, date_to):
        """ (réalisées, dont à temps) sur la période [date_from, date_to].
        Un domaine ne peut pas comparer deux colonnes : on regroupe par
        (date de réalisation, échéance) et on compare ensuite. """
        groups = self._activities('done')._read_group(
            base + self._bucket_domain('done', {'done_from': date_from, 'done_to': date_to}),
            ['date_done:day', 'date_deadline:day'], ['__count'])
        done = sum(count for __, __, count in groups)
        late = sum(count for date_done, deadline, count in groups if is_done_late(date_done, deadline))
        return done, done - late

    @api.model
    def _created_count(self, base, date_from, date_to):
        """ Activités créées pendant la période (journées locales), qu'elles
        soient encore ouvertes ou déjà réalisées. """
        start, end = self._utc_bounds(date_from, date_to)
        return self._activities('done').search_count(
            base + [('create_date', '>=', start), ('create_date', '<', end)])

    @api.model
    def _get_kpis(self, dates, base):
        Activity = self.env['mail.activity']
        today = dates['today']
        open_domain = base + self._open_domain()
        kpis = self._new_open_counts()
        for deadline, count in Activity._read_group(
                open_domain + [('date_deadline', '<=', dates['upcoming_end'])],
                ['date_deadline:day'], ['__count']):
            self._add_open_count(kpis, deadline, count, dates)
        kpis['open'] = Activity.search_count(open_domain)

        done, on_time = self._done_stats(base, dates['done_from'], dates['done_to'])
        done_prev, on_time_prev = self._done_stats(base, dates['prev_from'], dates['prev_to'])
        created = self._created_count(base, dates['done_from'], dates['done_to'])
        created_prev = self._created_count(base, dates['prev_from'], dates['prev_to'])
        kpis.update(
            done=done, done_prev=done_prev, done_delta=delta_pct(done, done_prev),
            created=created, created_prev=created_prev, created_delta=delta_pct(created, created_prev),
            on_time_rate=percentage(on_time, done),
            on_time_rate_prev=percentage(on_time_prev, done_prev),
        )

        # Opportunités derrière les activités en retard : chacune une seule
        # fois. Le nombre les compte toutes (même celles que l'utilisateur
        # ne peut pas ouvrir, où une activité lui est assignée) ; le montant
        # en jeu ne somme que celles qu'il peut lire.
        overdue_leads = [res_id for (res_id,) in Activity._read_group(
            open_domain + [('date_deadline', '<', today)], ['res_id'])]
        kpis['overdue_leads'] = len(overdue_leads)
        kpis['overdue_amounts'] = self._amounts(
            self.env['crm.lead'].browse(overdue_leads)._filtered_access('read'))
        return kpis

    @api.model
    def _amounts(self, leads):
        """ Somme des montants attendus des opportunités données (chacune une
        fois), par devise de société : [{currency_id, amount}], sans les
        devises à 0. Les opportunités doivent déjà être lisibles par
        l'utilisateur. """
        if not leads:
            return []
        groups = leads.sudo().with_context(active_test=False)._read_group(
            [('id', 'in', leads.ids)], ['company_id'], ['expected_revenue:sum'])
        totals = defaultdict(float)
        for company, amount in groups:
            currency = company.currency_id or self.env.company.currency_id
            totals[currency.id] += amount or 0.0
        return [{'currency_id': currency_id, 'amount': amount}
                for currency_id, amount in sorted(totals.items()) if amount]

    @api.model
    def _open_groups_by_user(self, flt, dates, lead_ids):
        """ Activités ouvertes « à faire » jusqu'à la fin de la fenêtre
        « À venir », regroupées par (personne assignée, échéance), sans le
        filtre de commercial : base du tableau « Par commercial » et du plan
        de charge. """
        base = self._activity_domain(dict(flt, user_id=False), lead_ids)
        return self.env['mail.activity']._read_group(
            base + self._open_domain() + [('date_deadline', '<=', dates['upcoming_end'])],
            ['user_id', 'date_deadline:day'], ['__count'])

    @api.model
    def _user_key_name(self, user):
        return user.id or UNASSIGNED, user.name or self.env._("Non assigné")

    @api.model
    def _get_by_user(self, flt, dates, lead_ids, open_groups):
        """ Une ligne par commercial : en retard (dont élevé / critique), du
        jour, à venir, réalisées sur la période, opportunités sans activité,
        avec le total de l'équipe. Le tableau sert à naviguer : il garde
        toutes les lignes quel que soit le commercial filtré (la ligne
        choisie est mise en avant) ; les droits d'Odoo limitent toujours ce
        que chacun voit. Sans filtre de commercial, les totaux sont égaux
        aux indicateurs. """
        rows = {}
        counters = ('overdue', 'today', 'upcoming', 'done', 'stalled', 'high', 'critical')

        def _row(user):
            key, name = self._user_key_name(user)
            return rows.setdefault(key, dict({'user_id': key, 'name': name}, **dict.fromkeys(counters, 0)))

        for user, deadline, count in open_groups:
            self._add_open_count(_row(user), deadline, count, dates)
        by_user_flt = dict(flt, user_id=False)
        base = self._activity_domain(by_user_flt, lead_ids)
        for user, count in self._activities('done')._read_group(
                base + self._bucket_domain('done', dates), ['user_id'], ['__count']):
            _row(user)['done'] += count
        for user, count in self.env['crm.lead']._read_group(
                self._stalled_domain(by_user_flt, lead_ids), ['user_id'], ['__count']):
            _row(user)['stalled'] += count

        total = dict.fromkeys(counters, 0)
        for row in rows.values():
            self._add_rates(row)
            for key in counters:
                total[key] += row[key]
        self._add_rates(total)
        return {
            'rows': sorted(
                rows.values(),
                key=lambda r: (-r['overdue'], -r['today'], -r['upcoming'], r['name'].lower()),
            ),
            'total': total,
        }

    @api.model
    def _add_rates(self, row):
        """ ``open`` = en retard + du jour + à venir ; ``overdue_rate`` : part
        des retards, en % arrondi (0 sans activité ouverte). """
        row['open'] = row['overdue'] + row['today'] + row['upcoming']
        row['overdue_rate'] = round(row['overdue'] * 100.0 / row['open']) if row['open'] else 0
        return row

    @api.model
    def _get_workload(self, dates, open_groups):
        """ Plan de charge : activités ouvertes par personne et par jour,
        d'aujourd'hui à J+N (N = fenêtre « À venir », 13 jours au plus), avec
        les retards dans une colonne à part. Comme le tableau « Par
        commercial », il ignore le filtre de commercial mais suit l'équipe
        et le type. ``weekday`` : 0 = lundi … 6 = dimanche. ``max`` est la
        plus grande case journalière (échelle des couleurs), retards non
        compris. """
        today = dates['today']
        span = min(dates['thresholds']['upcoming_days'], WORKLOAD_MAX_DAYS)
        days = [today + timedelta(days=index) for index in range(span + 1)]
        last_day = days[-1]
        rows = {}
        for user, deadline, count in open_groups:
            if deadline > last_day:
                continue
            key, name = self._user_key_name(user)
            row = rows.setdefault(key, {
                'user_id': key, 'name': name, 'overdue': 0, 'cells': [0] * len(days), 'total': 0,
            })
            if deadline < today:
                row['overdue'] += count
            else:
                row['cells'][(deadline - today).days] += count
            row['total'] += count
        return {
            'days': [{
                'date': fields.Date.to_string(day),
                'label': '%s %d' % (WEEKDAYS_SHORT[day.weekday()], day.day),
                'weekday': day.weekday(),
                'is_today': day == today,
                'is_weekend': day.weekday() >= 5,
            } for day in days],
            'rows': sorted(rows.values(), key=lambda r: (-r['overdue'], -r['total'], r['name'].lower())),
            'max': max((cell for row in rows.values() for cell in row['cells']), default=0),
        }

    @api.model
    def _get_alerts(self, kpis, stalled, thresholds):
        """ Bandeau d'alertes, construit côté serveur. """
        alerts = []
        critical = kpis['critical']
        if critical:
            days = self._days_text(thresholds['critical_days'])
            if critical == 1:
                message = self.env._("%(count)s activité en retard de %(days)s ou plus",
                                     count=critical, days=days)
            else:
                message = self.env._("%(count)s activités en retard de %(days)s ou plus",
                                     count=critical, days=days)
            alerts.append({'level': 'danger', 'message': message, 'action': {'bucket': 'overdue'}})
        dormant = stalled['dormant']
        if dormant:
            days = self._days_text(thresholds['dormant_days'])
            if dormant == 1:
                message = self.env._("%(count)s opportunité sans action depuis %(days)s ou plus",
                                     count=dormant, days=days)
            else:
                message = self.env._("%(count)s opportunités sans action depuis %(days)s ou plus",
                                     count=dormant, days=days)
            alerts.append({'level': 'warning', 'message': message, 'action': {'focus': 'stalled'}})
        return alerts

    @api.model
    def _days_text(self, days):
        return self.env._("%s jour", days) if days == 1 else self.env._("%s jours", days)

    @api.model
    def _lead_values(self, leads):
        """ Détails affichés des opportunités que l'utilisateur peut lire.
        Le droit de lecture est vérifié sur l'opportunité ; ses libellés
        (client, étape…) sont ensuite lus en sudo, comme le fait Odoo pour
        les noms des champs relationnels d'un formulaire : un client passé
        dans une autre société ne bloque pas le tableau de bord. """
        readable = leads._filtered_access('read')
        values = {}
        for lead in readable.sudo():
            values[lead.id] = {
                'id': lead.id,
                'name': lead.name,
                'partner': lead.partner_id.display_name or '',
                'stage': lead.stage_id.name or '',
                'team': lead.team_id.name or '',
                'user': lead.user_id.name or '',
                'expected_revenue': lead.expected_revenue,
                'currency_id': lead.company_currency.id,
                'probability': lead.probability,
                'type': lead.type,
            }
        return values

    @api.model
    def _activity_state(self, activity, today):
        deadline = activity.date_deadline
        if not activity.active:
            return 'done'
        if deadline < today:
            return 'overdue'
        if deadline == today:
            return 'today'
        return 'planned'

    @api.model
    def _get_activities(self, flt, dates, base):
        """ Liste des activités de la sélection. ``days_late`` : jours de
        retard (0 si l'échéance n'est pas dépassée ; pour une activité
        réalisée, le retard avec lequel elle a été faite) ; ``severity`` :
        gravité du retard des activités ouvertes (False sinon). """
        bucket = flt['bucket']
        Activity = self._activities(bucket)
        domain = base + self._bucket_domain(bucket, dates)
        order = 'date_done desc, id desc' if bucket == 'done' else 'date_deadline asc, id asc'
        # Pas de LIMIT SQL : pour un utilisateur non administrateur, Odoo
        # filtre les activités selon ses droits après la requête ; une
        # limite appliquée avant ce filtre pourrait vider la liste. On
        # découpe donc après.
        activities = Activity.search(domain, order=order)
        total = len(activities)
        activities = Activity.browse(activities.ids[:ACTIVITY_LIMIT])
        leads = self._lead_values(self.env['crm.lead'].browse(activities.mapped('res_id')))
        today = dates['today']
        thresholds = dates['thresholds']
        rows = []
        for activity in activities:
            deadline = activity.date_deadline
            state = self._activity_state(activity, today)
            if state == 'done':
                days_late = max((activity.date_done - deadline).days, 0) if activity.date_done else 0
                level = False
            else:
                days_late = max((today - deadline).days, 0)
                level = severity(days_late, thresholds)
            rows.append({
                'id': activity.id,
                'type': activity.activity_type_id.name or '',
                'icon': activity.icon or 'fa-tasks',
                'summary': activity.summary or '',
                'date_deadline': fields.Date.to_string(deadline),
                'date_done': fields.Date.to_string(activity.date_done) if activity.date_done else False,
                'days': (deadline - today).days,
                'days_late': days_late,
                'severity': level,
                'state': state,
                'user_id': activity.user_id.id,
                'user': activity.user_id.name or '',
                'res_id': activity.res_id,
                'res_name': activity.res_name or '',
                'lead': leads.get(activity.res_id),
                'can_write': activity.active and activity.can_write,
            })
        return {'records': rows, 'total': total, 'limit': ACTIVITY_LIMIT}

    @api.model
    def _last_action_dates(self, leads):
        """ Date de la dernière action sur chaque opportunité : la plus
        récente entre la dernière activité réalisée et le dernier changement
        d'étape (date locale). Les notes et e-mails de l'historique ne
        comptent pas. À n'appeler que sur des opportunités que
        l'utilisateur peut lire (la date est lue en sudo, quelle que soit
        la personne qui a réalisé l'activité). """
        if not leads:
            return {}
        leads = leads.sudo()
        last_done = dict(self.env['mail.activity'].sudo().with_context(active_test=False)._read_group(
            [('res_model', '=', 'crm.lead'), ('res_id', 'in', leads.ids), ('active', '=', False)],
            ['res_id'], ['date_done:max']))
        result = {}
        for lead in leads:
            candidates = [last_done.get(lead.id)]
            if lead.date_last_stage_update:
                candidates.append(fields.Datetime.context_timestamp(
                    self, lead.date_last_stage_update).date())
            candidates = [day for day in candidates if day]
            result[lead.id] = max(candidates) if candidates else False
        return result

    @api.model
    def _idle_values(self, last_action, today, thresholds):
        idle_days = (today - last_action).days if last_action else False
        return {
            'last_action_date': fields.Date.to_string(last_action) if last_action else False,
            'idle_days': idle_days,
            'dormant': idle_days is not False and idle_days >= thresholds['dormant_days'],
        }

    @api.model
    def _get_stalled(self, flt, dates, lead_ids):
        """ Opportunités sans activité planifiée, avec la date de leur
        dernière action, le nombre de jours depuis et le statut
        « dormante » (``dormant`` : nombre d'opportunités dormantes parmi
        toutes celles de la liste, pas seulement les lignes affichées). """
        domain = self._stalled_domain(flt, lead_ids)
        leads = self.env['crm.lead'].search(domain, order='priority desc, expected_revenue desc, id desc')
        today = dates['today']
        thresholds = dates['thresholds']
        last_actions = self._last_action_dates(leads)
        idle = {lead_id: self._idle_values(day, today, thresholds) for lead_id, day in last_actions.items()}
        page = leads[:STALLED_LIMIT]
        values = self._lead_values(page)
        records = []
        for lead in page:
            if lead.id in values:
                records.append(dict(values[lead.id], **idle[lead.id]))
        return {
            'records': records,
            'total': len(leads),
            'limit': STALLED_LIMIT,
            'amounts': self._amounts(leads),
            'dormant': sum(1 for vals in idle.values() if vals['dormant']),
        }

    @api.model
    def _get_options(self, flt, by_user):
        """ Listes des filtres. Un commercial ne choisit que parmi les
        personnes dont il voit des activités ou des opportunités ; chaque
        ligne du tableau « Par commercial » et le commercial filtré y
        figurent toujours. """
        users = self.env['mail.activity']._read_group(
            [('res_model', '=', 'crm.lead')], ['user_id'])
        user_ids = {user.id for (user,) in users if user} | {self.env.uid}
        user_ids |= {row['user_id'] for row in by_user['rows'] if isinstance(row['user_id'], int)}
        if isinstance(flt['user_id'], int) and flt['user_id']:
            user_ids.add(flt['user_id'])
        user_records = self.env['res.users'].browse(user_ids).exists()
        assignable = self.env['res.users']
        if self._is_manager():
            assignable = self.env['res.users'].search([
                ('share', '=', False),
                ('all_group_ids', 'in', self.env.ref('sales_team.group_sale_salesman').id),
            ])
        return {
            'users': [{'id': u.id, 'name': u.name} for u in user_records.sorted('name')],
            'assignable_users': [{'id': u.id, 'name': u.name} for u in assignable.sorted('name')],
            'teams': [{'id': t.id, 'name': t.name} for t in self.env['crm.team'].search([])],
            'activity_types': [
                {'id': t.id, 'name': t.name}
                for t in self.env['mail.activity.type'].search([('res_model', 'in', [False, 'crm.lead'])])
            ],
            'periods': [{'key': key, 'label': label} for key, label in self._period_labels().items()],
        }

    # ------------------------------------------------------------------
    # Tendances (onglet « Tendances », chargé à la demande)
    # ------------------------------------------------------------------

    @api.model
    @api.readonly
    def get_trend_data(self, filters=None):
        """ Les 12 dernières semaines ISO (semaine en cours comprise) :
        activités réalisées à temps / en retard et activités créées par
        semaine, taux de réalisation à temps, et classements par type et
        par personne. Suit les filtres commercial / équipe / type, pas la
        période. ``done`` : nombre d'activités réalisées, ``late`` : dont
        réalisées après l'échéance. """
        self._check_dashboard_access()
        today = fields.Date.context_today(self)
        flt = self._clean_filters(filters, today=today)
        weeks = iso_weeks(today)
        start, end = weeks[0]['date_from'], weeks[-1]['date_to']
        lead_ids = self._team_lead_ids(flt['team_id']) if flt['team_id'] else None
        base = self._activity_domain(flt, lead_ids)

        groups = self._activities('done')._read_group(
            base + self._bucket_domain('done', {'done_from': start, 'done_to': end}),
            ['date_done:day', 'date_deadline:day', 'activity_type_id', 'user_id'], ['__count'])
        on_time, late = bucket_done_by_week(
            ((done, deadline, count) for done, deadline, __, __, count in groups), start, len(weeks))

        by_type, by_user = {}, {}
        for done, deadline, activity_type, user, count in groups:
            is_late = is_done_late(done, deadline)
            type_row = by_type.setdefault(activity_type.id, {
                'type_id': activity_type.id or False,
                'name': activity_type.name or self.env._("Sans type"),
                'done': 0, 'late': 0,
            })
            key, name = self._user_key_name(user)
            user_row = by_user.setdefault(key, {'user_id': key, 'name': name, 'done': 0, 'late': 0})
            for row in (type_row, user_row):
                row['done'] += count
                row['late'] += count if is_late else 0

        def _ranking(rows):
            for row in rows.values():
                row['on_time_rate'] = percentage(row['done'] - row['late'], row['done'])
            return sorted(rows.values(), key=lambda r: (-r['done'], r['name'].lower()))

        created_start, created_end = self._utc_bounds(start, end)
        created_groups = self._activities('done').with_context(tz=self.env.tz.zone)._read_group(
            base + [('create_date', '>=', created_start), ('create_date', '<', created_end)],
            ['create_date:day'], ['__count'])
        total_done = sum(on_time) + sum(late)
        return {
            'weeks': [dict(week, date_from=fields.Date.to_string(week['date_from']),
                           date_to=fields.Date.to_string(week['date_to'])) for week in weeks],
            'done_on_time': on_time,
            'done_late': late,
            'created': bucket_counts_by_week(created_groups, start, len(weeks)),
            'on_time_rate': percentage(sum(on_time), total_done),
            'by_type': _ranking(by_type),
            'by_user': _ranking(by_user),
        }

    # ------------------------------------------------------------------
    # Aperçu d'une opportunité (panneau latéral)
    # ------------------------------------------------------------------

    @api.model
    def _plain_text(self, text):
        """ Compte rendu d'une activité, en texte brut. mail.activity.feedback
        est un champ Text : le texte saisi est rendu tel quel (« < » et « > »
        compris, retours à la ligne gardés). Seul un contenu réellement HTML
        (valeur Markup, ou texte qui commence par une balise comme <p>) est
        converti. """
        if not text:
            return ''
        if isinstance(text, Markup) or re.match(r'\s*<(p|div|br|ul|ol|span|b|strong|i|em)\b', text, re.I):
            return html_to_inner_content(text)
        return text.strip()

    @api.model
    @api.readonly
    def get_lead_preview(self, lead_id):
        """ Détails d'une opportunité pour le panneau d'aperçu : fiche,
        activités à faire, 5 dernières activités réalisées (avec leur compte
        rendu) et dernière action. Le droit de lecture est vérifié sur
        l'opportunité ; les libellés sont lus ensuite en sudo. """
        self._check_dashboard_access()
        try:
            lead_id = int(lead_id)
        except (TypeError, ValueError):
            lead_id = 0
        lead = self.env['crm.lead'].browse(lead_id).exists() if lead_id > 0 else self.env['crm.lead']
        if not lead:
            raise UserError(self.env._("Cette opportunité n'existe plus : actualisez le tableau de bord."))
        if not lead._filtered_access('read'):
            raise AccessError(self.env._("Vous n'avez pas accès à cette opportunité."))
        today = fields.Date.context_today(self)
        thresholds = get_thresholds(self.env)
        lead_domain = [('res_model', '=', 'crm.lead'), ('res_id', '=', lead.id)]

        open_activities = []
        for activity in self.env['mail.activity'].search(
                lead_domain + self._open_domain(), order='date_deadline asc, id asc'):
            deadline = activity.date_deadline
            activity_sudo = activity.sudo()
            open_activities.append({
                'id': activity.id,
                'type': activity_sudo.activity_type_id.name or '',
                'icon': activity_sudo.icon or 'fa-tasks',
                'summary': activity_sudo.summary or '',
                'date_deadline': fields.Date.to_string(deadline),
                'days': (deadline - today).days,
                'state': self._activity_state(activity_sudo, today),
                'severity': severity((today - deadline).days, thresholds),
                'user': activity_sudo.user_id.name or '',
                'can_write': activity.can_write,
            })

        done_activities = [{
            'type': activity.activity_type_id.name or '',
            'icon': activity.icon or 'fa-tasks',
            'summary': activity.summary or '',
            'date_done': fields.Date.to_string(activity.date_done) if activity.date_done else False,
            'feedback': self._plain_text(activity.feedback),
            'user': activity.user_id.name or '',
        } for activity in self.env['mail.activity'].sudo().with_context(active_test=False).search(
            lead_domain + [('active', '=', False)], order='date_done desc, id desc',
            limit=PREVIEW_DONE_LIMIT)]

        lead_sudo = lead.sudo()
        idle = self._idle_values(self._last_action_dates(lead)[lead.id], today, thresholds)
        return {
            'id': lead.id,
            'name': lead_sudo.name,
            'partner': lead_sudo.partner_id.display_name or '',
            'phone': lead_sudo.phone or '',
            'email': lead_sudo.email_from or '',
            'stage': lead_sudo.stage_id.name or '',
            'team': lead_sudo.team_id.name or '',
            'user': lead_sudo.user_id.name or '',
            'expected_revenue': lead_sudo.expected_revenue,
            'currency_id': lead_sudo.company_currency.id,
            'probability': lead_sudo.probability,
            'priority': lead_sudo.priority,
            'date_deadline': fields.Date.to_string(lead_sudo.date_deadline) if lead_sudo.date_deadline else False,
            'open_activities': open_activities,
            'done_activities': done_activities,
            'last_action_date': idle['last_action_date'],
            'idle_days': idle['idle_days'],
        }

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    @api.model
    def _get_open_activity(self, activity_id):
        activity = self.env['mail.activity'].with_context(active_test=False).browse(
            int(activity_id)).exists()
        if not activity or activity.res_model != 'crm.lead':
            raise UserError(self.env._("Cette activité n'existe plus : actualisez le tableau de bord."))
        if not activity.active:
            # action_feedback ne vérifie pas l'état : sans ce contrôle, un
            # double clic publierait deux fois « fait » dans l'historique.
            raise UserError(self.env._("Cette activité est déjà marquée comme faite."))
        return activity

    @api.model
    def action_mark_done(self, activity_id, feedback=False):
        """ Marque l'activité comme faite (message dans l'historique de
        l'opportunité, avec le compte rendu éventuel). """
        activity = self._get_open_activity(activity_id)
        activity.action_feedback(feedback=(feedback or '').strip() or False)
        return True

    @api.model
    def _preset_date(self, preset):
        """ Date d'un report rapide, à partir de la date du jour de
        l'utilisateur (et non d'une date gardée par le navigateur, qui
        peut dater de la veille). """
        today = fields.Date.context_today(self)
        if preset == 'tomorrow':
            return today + timedelta(days=1)
        if preset == 'monday':
            return today + relativedelta(weeks=1, weekday=MO(-1))
        return today + timedelta(days=7)

    @api.model
    def action_reschedule(self, activity_id, date_deadline):
        """ Nouvelle échéance : une date (AAAA-MM-JJ) ou un report rapide
        ('tomorrow', 'monday', 'week'). Renvoie la date retenue. """
        activity = self._get_open_activity(activity_id)
        if date_deadline in RESCHEDULE_PRESETS:
            new_date = self._preset_date(date_deadline)
        else:
            try:
                new_date = fields.Date.to_date(date_deadline)
            except (TypeError, ValueError):
                new_date = False
        if not new_date:
            raise UserError(self.env._("Choisissez une nouvelle échéance."))
        activity.write({'date_deadline': new_date})
        return fields.Date.to_string(new_date)

    @api.model
    def action_reassign(self, activity_id, user_id):
        """ Réassignation, réservée aux responsables (droits « tous les
        documents » ou administrateur) : Odoo laisserait sinon un commercial
        réassigner ses propres activités par un simple appel au serveur. """
        if not self._is_manager():
            raise AccessError(self.env._(
                "Seul un responsable commercial (droits « tous les documents ») peut "
                "réassigner une activité."))
        activity = self._get_open_activity(activity_id)
        user = self.env['res.users'].browse(int(user_id)).exists()
        if not user or user.share:
            raise UserError(self.env._("Choisissez un utilisateur interne."))
        activity.write({'user_id': user.id})
        return True
