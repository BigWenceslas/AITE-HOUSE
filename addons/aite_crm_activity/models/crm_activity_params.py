# -*- coding: utf-8 -*-
""" Réglages partagés du suivi des activités (tableau de bord, récapitulatif,
rapport d'analyse) : fenêtres et seuils, stockés en paramètres système et
modifiables dans CRM → Configuration → Paramètres.

Les valeurs illisibles ou incohérentes retombent sur les valeurs par défaut :
un réglage mal saisi ne doit jamais casser le tableau de bord ni l'envoi du
matin. """

PARAM_DASHBOARD_UPCOMING_DAYS = 'aite_crm_activity.dashboard_upcoming_days'
PARAM_HIGH_DAYS = 'aite_crm_activity.late_high_days'
PARAM_CRITICAL_DAYS = 'aite_crm_activity.late_critical_days'
PARAM_DORMANT_DAYS = 'aite_crm_activity.dormant_days'

DEFAULT_DASHBOARD_UPCOMING_DAYS = 7   # « À venir » : de demain à J+7
DEFAULT_HIGH_DAYS = 3                 # retard « élevé » à partir de 3 jours
DEFAULT_CRITICAL_DAYS = 7             # retard « critique » à partir de 7 jours
DEFAULT_DORMANT_DAYS = 14             # opportunité « dormante » après 14 jours sans action

MAX_DAYS = 365


def get_int_param(env, key, default, minimum=0, maximum=MAX_DAYS):
    """ Entier lu dans les paramètres système, borné ; valeur par défaut si
    absent ou illisible. """
    value = env['ir.config_parameter'].sudo().get_param(key)
    if value in (None, False, ''):
        return default
    try:
        value = int(value)
    except (TypeError, ValueError):
        return default
    return min(max(value, minimum), maximum)


def get_thresholds(env):
    """ Fenêtres et seuils en vigueur.

    - ``upcoming_days`` : fenêtre « À venir » du tableau de bord (1 à 365) ;
    - ``high_days`` / ``critical_days`` : retard élevé / critique (jours de
      retard, 1 à 365, ``high_days < critical_days``, sinon valeurs par
      défaut pour les deux) ;
    - ``dormant_days`` : opportunité sans action depuis ce nombre de jours.
    """
    high = get_int_param(env, PARAM_HIGH_DAYS, DEFAULT_HIGH_DAYS, minimum=1)
    critical = get_int_param(env, PARAM_CRITICAL_DAYS, DEFAULT_CRITICAL_DAYS, minimum=1)
    if high >= critical:
        high, critical = DEFAULT_HIGH_DAYS, DEFAULT_CRITICAL_DAYS
    return {
        'upcoming_days': get_int_param(
            env, PARAM_DASHBOARD_UPCOMING_DAYS, DEFAULT_DASHBOARD_UPCOMING_DAYS, minimum=1),
        'high_days': high,
        'critical_days': critical,
        'dormant_days': get_int_param(env, PARAM_DORMANT_DAYS, DEFAULT_DORMANT_DAYS, minimum=1),
    }


def severity(days_late, thresholds):
    """ Gravité d'un retard : False (pas en retard), 'low' (léger),
    'high' (élevé) ou 'critical' (critique). ``days_late`` est le nombre
    de jours de retard (> 0 si l'échéance est dépassée). """
    if not days_late or days_late <= 0:
        return False
    if days_late >= thresholds['critical_days']:
        return 'critical'
    if days_late >= thresholds['high_days']:
        return 'high'
    return 'low'


def actionable_activity_domain(env):
    """ Domaine (sur mail.activity) restreignant aux activités sur lesquelles
    on peut encore agir. Contrat partagé par le tableau de bord et le
    récapitulatif : voir l'implémentation pour la règle retenue. """
    return []
