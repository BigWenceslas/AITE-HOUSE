# -*- coding: utf-8 -*-
""" Analyse des activités CRM (CRM → Analyse → Suivi des activités (analyse)).

Une ligne par activité planifiée sur une piste ou une opportunité, ouverte
OU réalisée, pour les tableaux croisés, graphiques et exports qui dépassent
le tableau de bord (limité à quelques dizaines de lignes).

Règles de calcul, alignées sur le tableau de bord :

- « aujourd'hui » est la date du jour dans le fuseau de la personne
  assignée (UTC si elle n'en a pas), comme l'état natif des activités
  d'Odoo ; il est évalué à chaque requête (``_table_query``), jamais figé
  à l'installation ;
- une activité ouverte sur une opportunité archivée (perdue) n'est plus
  « à faire » : elle sort du rapport, comme du tableau de bord
  (``actionable_activity_domain``). Une activité réalisée reste comptée,
  même si l'opportunité a été perdue ensuite ;
- les seuils de retard élevé / critique sont ceux des Paramètres du CRM
  (``get_thresholds``), passés en paramètres SQL ;
- aucun montant d'opportunité sur les lignes : une opportunité serait
  comptée une fois par activité.

Une vue SQL échappe aux contrôles propres à mail.activity : les règles
d'accès du fichier security/aite_crm_activity_security.xml (copiées de
celles des opportunités) sont donc indispensables.

Un commercial « mes documents » garde dans le rapport les activités qui
lui sont assignées sur l'opportunité d'un collègue, comme dans ses
activités Odoo, mais rien de plus sur cette opportunité que son nom (ce
qu'Odoo lui montre) : client, étape, commercial, piste ou opportunité,
issue et archivage restent vides sur ces lignes, en liste comme en
regroupement, filtre ou export. L'équipe et la société restent
renseignées : le tableau de bord filtre déjà ces activités par équipe, et
la société sert à la règle multi-société.
"""
from odoo import api, fields, models
from odoo.exceptions import AccessError
from odoo.tools import SQL

from .crm_activity_params import get_thresholds

STATES = [
    ('overdue', "En retard"),
    ('today', "Aujourd'hui"),
    ('planned', "À venir"),
    ('done', "Réalisée"),
]

SEVERITIES = [
    ('low', "Léger"),
    ('high', "Élevé"),
    ('critical', "Critique"),
]


class AiteCrmActivityReport(models.Model):
    _name = 'aite.crm.activity.report'
    _description = "Analyse des activités CRM"
    _auto = False
    _rec_name = 'summary'
    _order = 'date_deadline desc, id desc'

    # Champs lus par la requête : vidés en base avant chaque lecture du
    # rapport, pour qu'une activité tout juste marquée comme faite (encore
    # en cache) y figure déjà comme réalisée.
    _depends = {
        'mail.activity': [
            'res_model', 'res_id', 'user_id', 'user_tz', 'activity_type_id', 'summary',
            'date_deadline', 'date_done', 'active', 'create_date',
        ],
        'crm.lead': [
            'user_id', 'team_id', 'stage_id', 'partner_id', 'company_id', 'type',
            'won_status', 'active',
        ],
    }

    # Activité
    activity_id = fields.Many2one('mail.activity', string="Activité", readonly=True)
    summary = fields.Char(string="Résumé", readonly=True)
    activity_type_id = fields.Many2one('mail.activity.type', string="Type d'activité", readonly=True)
    user_id = fields.Many2one('res.users', string="Assignée à", readonly=True)
    date_deadline = fields.Date(string="Échéance", readonly=True)
    # date_done est enregistrée par Odoo en date UTC (jour du passage à
    # « fait » à Greenwich) : à Douala (UTC+1), une activité faite entre
    # minuit et 1 h compte pour la veille.
    date_done = fields.Date(string="Réalisée le", readonly=True)
    create_date = fields.Date(string="Créée le", readonly=True)
    state = fields.Selection(STATES, string="État", readonly=True)
    severity = fields.Selection(SEVERITIES, string="Gravité du retard", readonly=True)

    # Opportunité. Les champs marqués « depends_context » sont vides sur les
    # lignes d'une opportunité que l'utilisateur ne peut pas lire (voir
    # _table_query) : leur valeur dépend de qui lit le rapport, et le cache
    # ne doit pas la partager entre utilisateurs, ni avec le mode sudo.
    lead_id = fields.Many2one('crm.lead', string="Opportunité", readonly=True)
    lead_user_id = fields.Many2one(
        'res.users', string="Commercial de l'opportunité", readonly=True, depends_context=('uid',))
    team_id = fields.Many2one('crm.team', string="Équipe commerciale", readonly=True)
    stage_id = fields.Many2one('crm.stage', string="Étape", readonly=True, depends_context=('uid',))
    partner_id = fields.Many2one('res.partner', string="Client", readonly=True, depends_context=('uid',))
    company_id = fields.Many2one('res.company', string="Société", readonly=True)
    lead_type = fields.Selection(
        [('lead', "Piste"), ('opportunity', "Opportunité")], string="Piste ou opportunité",
        readonly=True, depends_context=('uid',))
    won_status = fields.Selection(
        [('won', "Gagnée"), ('lost', "Perdue"), ('pending', "En cours")],
        string="Issue de l'opportunité", readonly=True, depends_context=('uid',))
    lead_active = fields.Boolean(string="Opportunité active", readonly=True, depends_context=('uid',))

    # Mesures
    nbr = fields.Integer(string="Nombre d'activités", readonly=True, aggregator='sum')
    is_overdue = fields.Integer(string="En retard (nombre)", readonly=True, aggregator='sum')
    days_late = fields.Integer(
        string="Jours de retard", readonly=True, aggregator='avg',
        help="Activité en cours : jours écoulés depuis l'échéance (0 si elle n'est pas dépassée). "
             "Activité réalisée : jours de retard au moment où elle a été faite.")
    done_on_time = fields.Integer(
        string="Réalisées à temps (%)", readonly=True, aggregator='avg',
        help="Part des activités réalisées au plus tard à leur échéance. "
             "Vide pour les activités en cours.")

    # ------------------------------------------------------------------
    # Requête
    # ------------------------------------------------------------------

    @property
    def _table_query(self):
        """ Requête évaluée à chaque lecture : la date du jour et les seuils
        des Paramètres sont ceux du moment (et non ceux de l'installation,
        comme le ferait une vue créée dans ``init()``).

        Elle l'est aussi avec les droits de qui lit le rapport : les détails
        d'une opportunité qu'il ne peut pas lire (activité qui lui est
        assignée sur l'opportunité d'un collègue) sont vidés. Le commercial
        de l'opportunité n'est vidé que sur les lignes assignées au lecteur :
        sur les autres, la règle d'accès « mes activités et mes
        opportunités » s'évalue sur sa vraie valeur (vide, il ouvrirait les
        lignes à tous comme « opportunité sans commercial »). """
        thresholds = get_thresholds(self.env)
        return SQL(
            """
            SELECT
                r.id,
                r.id AS activity_id,
                r.summary,
                r.activity_type_id,
                r.user_id,
                r.date_deadline,
                r.date_done,
                r.create_date,
                r.lead_id,
                CASE WHEN r.lead_readable OR r.user_id IS DISTINCT FROM %(uid)s
                    THEN r.lead_user_id END AS lead_user_id,
                r.team_id,
                CASE WHEN r.lead_readable THEN r.stage_id END AS stage_id,
                CASE WHEN r.lead_readable THEN r.partner_id END AS partner_id,
                r.company_id,
                CASE WHEN r.lead_readable THEN r.lead_type END AS lead_type,
                CASE WHEN r.lead_readable THEN r.won_status END AS won_status,
                CASE WHEN r.lead_readable THEN r.lead_active END AS lead_active,
                CASE
                    WHEN NOT r.is_open THEN 'done'
                    WHEN r.date_deadline < r.today THEN 'overdue'
                    WHEN r.date_deadline = r.today THEN 'today'
                    ELSE 'planned'
                END AS state,
                CASE
                    WHEN NOT r.is_open OR r.date_deadline >= r.today THEN NULL
                    WHEN r.today - r.date_deadline >= %(critical)s THEN 'critical'
                    WHEN r.today - r.date_deadline >= %(high)s THEN 'high'
                    ELSE 'low'
                END AS severity,
                CASE
                    WHEN r.is_open AND r.date_deadline < r.today
                        THEN r.today - r.date_deadline
                    WHEN NOT r.is_open AND r.date_done > r.date_deadline
                        THEN r.date_done - r.date_deadline
                    ELSE 0
                END AS days_late,
                CASE WHEN r.is_open AND r.date_deadline < r.today THEN 1 ELSE 0 END AS is_overdue,
                CASE
                    WHEN r.is_open OR r.date_done IS NULL THEN NULL
                    WHEN r.date_done <= r.date_deadline THEN 100
                    ELSE 0
                END AS done_on_time,
                1 AS nbr
            FROM (
                SELECT
                    a.id,
                    a.summary,
                    a.activity_type_id,
                    a.user_id,
                    a.date_deadline,
                    a.date_done,
                    (a.create_date AT TIME ZONE 'UTC'
                        AT TIME ZONE COALESCE(a.user_tz, 'UTC'))::date AS create_date,
                    COALESCE(a.active, FALSE) AS is_open,
                    (%(now)s::timestamp AT TIME ZONE 'UTC'
                        AT TIME ZONE COALESCE(a.user_tz, 'UTC'))::date AS today,
                    l.id AS lead_id,
                    l.user_id AS lead_user_id,
                    l.team_id,
                    l.stage_id,
                    l.partner_id,
                    l.company_id,
                    l.type AS lead_type,
                    l.won_status,
                    l.active AS lead_active,
                    %(lead_readable)s AS lead_readable
                FROM mail_activity a
                LEFT JOIN crm_lead l ON l.id = a.res_id
                WHERE a.res_model = 'crm.lead'
                  -- Comme actionable_activity_domain : une activité ouverte
                  -- ne compte que sur une piste ou opportunité active.
                  AND (a.active IS NOT TRUE OR l.active IS TRUE)
            ) r
            """,
            critical=thresholds['critical_days'],
            high=thresholds['high_days'],
            now=fields.Datetime.now(),
            uid=self.env.uid,
            lead_readable=self._lead_readable_sql(),
        )

    def _lead_readable_sql(self):
        """ Condition SQL sur ``l`` (crm_lead) : l'utilisateur peut lire
        cette piste ou opportunité, archivée (perdue) comprise. Ce sont les
        règles d'accès d'Odoo sur crm.lead qui en décident. """
        if self.env.su:
            return SQL("TRUE")
        leads = self.env['crm.lead'].with_context(active_test=False)
        if not leads.has_access('read'):
            return SQL("FALSE")
        return SQL("l.id IN %s", leads._search([]).subselect())

    # ------------------------------------------------------------------
    # Export
    # ------------------------------------------------------------------

    def export_data(self, fields_to_export):
        """ Export (liste → Actions → Exporter) : la colonne « Opportunité »
        donne le nom de l'opportunité, comme la liste.

        Une ligne peut porter sur l'opportunité d'un collègue que
        l'utilisateur ne peut pas lire (activité qui lui est assignée) :
        Odoo refuserait alors tout l'export, faute de pouvoir lire le nom de
        cette opportunité. Ce nom est donc lu en sudo, comme le fait la liste
        (web_read) ; l'export passe par les droits de l'utilisateur pour tout
        le reste, détails de l'opportunité compris (lead_id/…). """
        name_columns = [
            index for index, path in enumerate(fields_to_export)
            if path in ('lead_id', 'lead_id/display_name')
        ]
        if not name_columns:
            return super().export_data(fields_to_export)
        # Identifiant de l'opportunité à la place de son nom (aucune lecture
        # de crm.lead), remplacé ensuite par le nom.
        paths = [
            'lead_id/.id' if index in name_columns else path
            for index, path in enumerate(fields_to_export)
        ]
        result = super().export_data(paths)
        lead_ids = {int(row[index]) for row in result['datas'] for index in name_columns if row[index]}
        names = {
            lead.id: lead.display_name
            for lead in self.env['crm.lead'].sudo().with_context(active_test=False).browse(lead_ids)
        }
        for row in result['datas']:
            for index in name_columns:
                if row[index]:
                    row[index] = names.get(int(row[index]), '')
        return result

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    @api.readonly
    def action_open_lead(self):
        """ Clic sur une ligne de la liste : ouvre l'opportunité, si
        l'utilisateur a le droit de la lire (une activité qui lui est
        assignée sur l'opportunité d'un collègue reste dans le rapport,
        sans ouvrir cette opportunité). """
        self.ensure_one()
        lead = self.lead_id.with_context(active_test=False)
        if not lead or not lead._filtered_access('read'):
            raise AccessError(self.env._(
                "Vous n'avez pas accès à cette opportunité. L'activité qui vous est "
                "assignée reste visible dans vos activités (icône horloge)."))
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'crm.lead',
            'res_id': lead.id,
            'views': [(False, 'form')],
            'target': 'current',
        }
