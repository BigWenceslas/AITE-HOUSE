# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError

# Fenêtres du tableau de bord, en jours.
UPCOMING_DAYS = 7      # « à venir » : de demain à J+7
DONE_DAYS = 7          # « réalisées » : les 7 derniers jours, aujourd'hui compris
ACTIVITY_LIMIT = 80    # lignes de la liste des activités
STALLED_LIMIT = 50     # lignes de la liste « sans activité »

# Sélections de la liste des activités.
BUCKETS = ('all', 'overdue', 'today', 'upcoming', 'done')


class AiteCrmActivityDashboard(models.AbstractModel):
    """ Données et actions du tableau de bord « Suivi des activités ».

    Toutes les lectures se font avec les droits de l'utilisateur : il ne
    voit que les activités et opportunités qu'Odoo l'autorise à voir. Une
    activité qui lui est assignée sur une opportunité qu'il ne peut pas
    ouvrir reste listée (Odoo la lui montre aussi), sans les détails de
    l'opportunité.
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
    def _clean_filters(self, filters):
        """ Filtres reçus du navigateur → valeurs sûres. Sans filtre de
        commercial explicite, un responsable voit toute l'équipe et un
        commercial ses propres activités. """
        filters = dict(filters or {})

        def _id(key):
            try:
                return int(filters.get(key) or 0) or False
            except (TypeError, ValueError):
                return False

        if 'user_id' in filters:
            user_id = _id('user_id')
        else:
            user_id = False if self._is_manager() else self.env.uid
        bucket = filters.get('bucket')
        return {
            'user_id': user_id,
            'team_id': _id('team_id'),
            'activity_type_id': _id('activity_type_id'),
            'bucket': bucket if bucket in BUCKETS else 'all',
        }

    @api.model
    def _dates(self):
        today = fields.Date.context_today(self)
        return {
            'today': today,
            'upcoming_end': today + timedelta(days=UPCOMING_DAYS),
            'done_start': today - timedelta(days=DONE_DAYS - 1),
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
    def _activity_domain(self, flt, lead_ids=None):
        """ Activités ouvertes sur les pistes et opportunités, filtrées. """
        domain = [('res_model', '=', 'crm.lead')]
        if flt['user_id']:
            domain.append(('user_id', '=', flt['user_id']))
        if flt['activity_type_id']:
            domain.append(('activity_type_id', '=', flt['activity_type_id']))
        if lead_ids is not None:
            domain.append(('res_id', 'in', lead_ids))
        return domain

    @api.model
    def _bucket_domain(self, bucket, dates):
        today = dates['today']
        return {
            'all': [],
            'overdue': [('date_deadline', '<', today)],
            'today': [('date_deadline', '=', today)],
            'upcoming': [('date_deadline', '>', today),
                         ('date_deadline', '<=', dates['upcoming_end'])],
            'done': [('active', '=', False), ('date_done', '>=', dates['done_start'])],
        }[bucket]

    @api.model
    def _activities(self, bucket):
        """ mail.activity, en incluant les activités réalisées (archivées)
        pour la sélection « done ». """
        activity = self.env['mail.activity']
        return activity.with_context(active_test=False) if bucket == 'done' else activity

    @api.model
    def _stalled_domain(self, flt, lead_ids=None):
        """ Opportunités ouvertes, ni gagnées ni perdues, sans activité. """
        domain = [
            ('type', '=', 'opportunity'),
            ('activity_ids', '=', False),
            ('won_status', '=', 'pending'),
        ]
        if flt['user_id']:
            domain.append(('user_id', '=', flt['user_id']))
        if lead_ids is not None:
            domain.append(('id', 'in', lead_ids))
        return domain

    # ------------------------------------------------------------------
    # Données
    # ------------------------------------------------------------------

    @api.model
    def get_dashboard_data(self, filters=None):
        flt = self._clean_filters(filters)
        dates = self._dates()
        lead_ids = self._team_lead_ids(flt['team_id']) if flt['team_id'] else None
        base = self._activity_domain(flt, lead_ids)

        kpis = {
            bucket: self._activities(bucket).search_count(base + self._bucket_domain(bucket, dates))
            for bucket in ('overdue', 'today', 'upcoming', 'done')
        }
        kpis['open'] = self.env['mail.activity'].search_count(base)
        kpis['stalled'] = self.env['crm.lead'].search_count(self._stalled_domain(flt, lead_ids))

        return {
            'filters': flt,
            'is_manager': self._is_manager(),
            'today': fields.Date.to_string(dates['today']),
            'upcoming_days': UPCOMING_DAYS,
            'done_days': DONE_DAYS,
            'kpis': kpis,
            'by_user': self._get_by_user(flt, dates, lead_ids),
            'activities': self._get_activities(flt, dates, base),
            'stalled': self._get_stalled(flt, lead_ids),
            'options': self._get_options(),
        }

    @api.model
    def _get_by_user(self, flt, dates, lead_ids):
        """ Une ligne par commercial : en retard, du jour, à venir,
        réalisées, opportunités sans activité. """
        rows = {}

        def _row(user):
            return rows.setdefault(user.id, {
                'user_id': user.id, 'name': user.name or self.env._("Non assigné"),
                'overdue': 0, 'today': 0, 'upcoming': 0, 'done': 0, 'stalled': 0,
            })

        by_user_flt = dict(flt, user_id=False) if not flt['user_id'] else flt
        base = self._activity_domain(by_user_flt, lead_ids)
        for bucket in ('overdue', 'today', 'upcoming', 'done'):
            groups = self._activities(bucket)._read_group(
                base + self._bucket_domain(bucket, dates), ['user_id'], ['__count'])
            for user, count in groups:
                _row(user)[bucket] += count
        for user, count in self.env['crm.lead']._read_group(
                self._stalled_domain(by_user_flt, lead_ids), ['user_id'], ['__count']):
            _row(user)['stalled'] += count

        return sorted(
            rows.values(),
            key=lambda r: (-r['overdue'], -r['today'], -r['upcoming'], r['name'].lower()),
        )

    @api.model
    def _lead_values(self, leads):
        """ Détails affichés des opportunités que l'utilisateur peut lire. """
        readable = leads._filtered_access('read')
        values = {}
        for lead in readable:
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
    def _get_activities(self, flt, dates, base):
        bucket = flt['bucket']
        Activity = self._activities(bucket)
        domain = base + self._bucket_domain(bucket, dates)
        order = 'date_done desc, id desc' if bucket == 'done' else 'date_deadline asc, id asc'
        activities = Activity.search(domain, order=order, limit=ACTIVITY_LIMIT)
        total = Activity.search_count(domain)
        leads = self._lead_values(self.env['crm.lead'].browse(activities.mapped('res_id')))
        today = dates['today']
        rows = []
        for activity in activities:
            deadline = activity.date_deadline
            if not activity.active:
                state = 'done'
            elif deadline < today:
                state = 'overdue'
            elif deadline == today:
                state = 'today'
            else:
                state = 'planned'
            rows.append({
                'id': activity.id,
                'type': activity.activity_type_id.name or '',
                'icon': activity.icon or 'fa-tasks',
                'summary': activity.summary or '',
                'date_deadline': fields.Date.to_string(deadline),
                'date_done': fields.Date.to_string(activity.date_done) if activity.date_done else False,
                'days': (deadline - today).days,
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
    def _get_stalled(self, flt, lead_ids):
        domain = self._stalled_domain(flt, lead_ids)
        Lead = self.env['crm.lead']
        leads = Lead.search(domain, order='priority desc, expected_revenue desc, id desc',
                            limit=STALLED_LIMIT)
        today = fields.Date.context_today(self)
        records = []
        for lead_id, vals in self._lead_values(leads).items():
            lead = Lead.browse(lead_id)
            last_update = lead.date_last_stage_update
            vals['idle_days'] = (today - last_update.date()).days if last_update else False
            records.append(vals)
        order = {lead.id: index for index, lead in enumerate(leads)}
        records.sort(key=lambda r: order[r['id']])
        return {'records': records, 'total': Lead.search_count(domain), 'limit': STALLED_LIMIT}

    @api.model
    def _get_options(self):
        """ Listes des filtres. Un commercial ne choisit que parmi les
        personnes dont il voit des activités. """
        users = self.env['mail.activity']._read_group(
            [('res_model', '=', 'crm.lead')], ['user_id'])
        user_records = self.env['res.users'].union(*(user for (user,) in users)) | self.env.user
        assignable = self.env['res.users']
        if self._is_manager():
            assignable = self.env['res.users'].search([
                ('share', '=', False),
                ('all_group_ids', 'in', self.env.ref('sales_team.group_sale_salesman').id),
            ])
        return {
            'users': [{'id': u.id, 'name': u.name} for u in user_records.filtered('id').sorted('name')],
            'assignable_users': [{'id': u.id, 'name': u.name} for u in assignable.sorted('name')],
            'teams': [{'id': t.id, 'name': t.name} for t in self.env['crm.team'].search([])],
            'activity_types': [
                {'id': t.id, 'name': t.name}
                for t in self.env['mail.activity.type'].search([('res_model', 'in', [False, 'crm.lead'])])
            ],
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
    def action_reschedule(self, activity_id, date_deadline):
        activity = self._get_open_activity(activity_id)
        new_date = fields.Date.to_date(date_deadline)
        if not new_date:
            raise UserError(self.env._("Choisissez une nouvelle échéance."))
        activity.write({'date_deadline': new_date})
        return True

    @api.model
    def action_reassign(self, activity_id, user_id):
        activity = self._get_open_activity(activity_id)
        user = self.env['res.users'].browse(int(user_id)).exists()
        if not user or user.share:
            raise UserError(self.env._("Choisissez un utilisateur interne."))
        activity.write({'user_id': user.id})
        return True
