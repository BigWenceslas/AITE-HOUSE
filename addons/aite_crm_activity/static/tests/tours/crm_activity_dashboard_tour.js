import { registry } from "@web/core/registry";

/**
 * Parcours du tableau de bord « Suivi des activités ».
 *
 * 1. Actions directes : marquer une activité comme faite (avec compte
 *    rendu), en reporter une autre, en réassigner une troisième, puis
 *    planifier une activité sur une opportunité qui n'en avait pas.
 * 2. Panneau d'aperçu : ouverture depuis la liste, compte rendu affiché,
 *    fermeture par le bouton puis par Échap.
 * 3. Période des activités réalisées (« Ce mois », « Personnalisée »),
 *    conservée avec la sélection au retour d'une opportunité par le fil
 *    d'Ariane.
 * 4. Onglet « Équipe » : un nombre du tableau par commercial et une case
 *    du plan de charge mènent à « À traiter », filtré.
 * 5. Onglet « Tendances » : graphique dessiné, classements, lien vers
 *    l'analyse ; l'onglet est retrouvé au retour par le fil d'Ariane.
 *
 * Les données sont créées par tests/test_ui.py ; les libellés se terminent
 * par « (tour) » pour ne viser qu'elles. Les fenêtres d'Odoo s'affichent
 * hors du tableau de bord : on vérifie leur fermeture sur body. Le texte
 * d'une action « run » ne doit pas finir par une parenthèse (l'outil de
 * parcours la retirerait).
 */
const LEAD_LINK = "tr.o_aite_cad_activity:contains('Préparer la réunion (tour)') .o_aite_cad_lead_link";
const NO_PANEL = ".o_aite_cad:not(:has(.o_aite_cad_panel))";

registry.category("web_tour.tours").add("aite_crm_activity_dashboard_tour", {
    steps: () => [
        // 1. Actions directes -------------------------------------------
        {
            content: "Le tableau de bord est chargé",
            trigger: ".o_aite_cad .o_aite_cad_kpi_overdue",
            run: "click",
        },
        {
            content: "Onglet « À traiter » affiché",
            trigger: ".o_aite_cad_navtab_todo[aria-selected='true']",
        },
        {
            content: "Sélection « En retard »",
            trigger: ".o_aite_cad_tab_overdue.btn-primary",
        },
        {
            content: "Marquer l'activité en retard comme faite",
            trigger: "tr.o_aite_cad_activity:contains('Rappeler le client (tour)') .o_aite_cad_done",
            run: "click",
        },
        {
            content: "Saisir le compte rendu",
            trigger: ".modal .o_aite_cad_feedback",
            run: "edit Client rappelé, devis vendredi",
        },
        {
            content: "Valider",
            trigger: ".modal .o_aite_cad_confirm_done",
            run: "click",
        },
        {
            content: "La fenêtre est fermée et l'activité a quitté la liste",
            trigger: "body:not(:has(.modal)) .o_aite_cad:not(:has(tr.o_aite_cad_activity:contains('Rappeler le client (tour)')))",
        },
        {
            content: "Sélection « Aujourd'hui »",
            trigger: ".o_aite_cad_tab_today",
            run: "click",
        },
        {
            content: "Ouvrir le menu « Reporter » de l'activité du jour",
            trigger: ".o_aite_cad_tab_today.btn-primary",
        },
        {
            trigger: "tr.o_aite_cad_activity:contains('Envoyer le devis (tour)') .o_aite_cad_reschedule",
            run: "click",
        },
        {
            content: "Reporter à demain",
            trigger: ".o-dropdown--menu .o_aite_cad_reschedule_tomorrow",
            run: "click",
        },
        {
            content: "L'activité reportée n'est plus « du jour »",
            trigger: ".o_aite_cad:not(:has(tr.o_aite_cad_activity:contains('Envoyer le devis (tour)')))",
        },
        {
            content: "Sélection « À venir »",
            trigger: ".o_aite_cad_tab_upcoming",
            run: "click",
        },
        {
            content: "Réassigner une activité à venir",
            trigger: "tr.o_aite_cad_activity:contains('Préparer la réunion (tour)') .o_aite_cad_reassign",
            run: "click",
        },
        {
            content: "Choisir la personne",
            trigger: ".modal select.o_aite_cad_reassign_user",
            run: "selectByLabel Collègue (tour)",
        },
        {
            content: "Confirmer la réassignation",
            trigger: ".modal .o_aite_cad_confirm_reassign:enabled",
            run: "click",
        },
        {
            content: "L'activité est assignée à la collègue",
            trigger: "body:not(:has(.modal)) tr.o_aite_cad_activity:contains('Préparer la réunion (tour)'):contains('Collègue (tour)')",
        },
        {
            content: "Planifier une activité sur l'opportunité sans suite",
            trigger: "tr.o_aite_cad_stalled_row:contains('Opportunité à relancer (tour)') .o_aite_cad_schedule",
            run: "click",
        },
        {
            content: "La fenêtre de planification d'Odoo s'ouvre",
            trigger: ".modal .o_form_view .o_field_widget[name='summary'] input",
            // Pas de parenthèse finale : l'outil de parcours la retirerait.
            run: "edit Relancer le client - tour",
        },
        {
            content: "Enregistrer l'activité",
            trigger: ".modal button[name='action_schedule_activities']",
            run: "click",
        },
        {
            content: "Retour au tableau de bord : l'opportunité a maintenant une activité",
            trigger: "body:not(:has(.modal)) .o_aite_cad:not(:has(tr.o_aite_cad_stalled_row:contains('Opportunité à relancer (tour)'))) .o_aite_cad_kpi",
        },

        // 2. Panneau d'aperçu -------------------------------------------
        {
            content: "Ouvrir l'aperçu de l'opportunité depuis la liste",
            trigger: LEAD_LINK,
            run: "click",
        },
        {
            content: "L'aperçu montre le compte rendu de l'activité faite",
            trigger: ".o_aite_cad_panel:contains('Opportunité suivie (tour)') .o_aite_cad_feedback_text:contains('Client rappelé, devis vendredi')",
        },
        {
            content: "… et les activités à faire",
            trigger: ".o_aite_cad_panel .o_aite_cad_panel_activity:contains('Préparer la réunion (tour)')",
        },
        {
            content: "Fermer l'aperçu",
            trigger: ".o_aite_cad_panel .o_aite_cad_panel_close",
            run: "click",
        },
        {
            content: "L'aperçu est fermé",
            trigger: NO_PANEL,
        },
        {
            content: "Rouvrir l'aperçu",
            trigger: LEAD_LINK,
            run: "click",
        },
        {
            content: "La touche Échap ferme l'aperçu",
            trigger: ".o_aite_cad_panel .o_aite_cad_panel_title:contains('Opportunité suivie (tour)')",
            run: "press Escape",
        },
        {
            content: "L'aperçu est fermé",
            trigger: NO_PANEL,
        },

        // 3. Période, conservée par le fil d'Ariane ------------------------
        {
            content: "Période « Ce mois »",
            trigger: ".o_aite_cad_filter_period",
            run: "select month",
        },
        {
            content: "La carte des activités réalisées suit la période",
            trigger: ".o_aite_cad_kpi_done .o_aite_cad_kpi_label:contains('Ce mois')",
        },
        {
            content: "Ouvrir l'aperçu",
            trigger: LEAD_LINK,
            run: "click",
        },
        {
            content: "Ouvrir la fiche de l'opportunité",
            trigger: ".o_aite_cad_panel .o_aite_cad_panel_open_form:enabled",
            run: "click",
        },
        {
            content: "La fiche est ouverte ; revenir par le fil d'Ariane",
            trigger: ".o_form_view .o_last_breadcrumb_item:contains('Opportunité suivie (tour)')",
        },
        {
            trigger: ".breadcrumb-item.o_back_button",
            run: "click",
        },
        {
            content: "Période et sélection retrouvées, aperçu fermé",
            trigger: ".o_aite_cad_kpi_done .o_aite_cad_kpi_label:contains('Ce mois')",
        },
        {
            trigger: ".o_aite_cad:not(:has(.o_aite_cad_panel)) .o_aite_cad_tab_upcoming.btn-primary",
        },
        {
            content: "Période personnalisée : deux dates apparaissent",
            trigger: ".o_aite_cad_filter_period",
            run: "select custom",
        },
        {
            trigger: ".o_aite_cad_custom_period .o_aite_cad_date_from",
        },
        {
            content: "Le libellé de la période donne les dates",
            trigger: ".o_aite_cad_kpi_done .o_aite_cad_kpi_label:contains('Du ')",
        },
        {
            content: "Retour aux 7 derniers jours",
            trigger: ".o_aite_cad_filter_period",
            run: "select 7d",
        },
        {
            trigger: ".o_aite_cad:not(:has(.o_aite_cad_custom_period)) .o_aite_cad_kpi_done .o_aite_cad_kpi_label:contains('7 derniers jours')",
        },

        // 4. Équipe : du chiffre à la liste --------------------------------
        {
            content: "Onglet « Équipe »",
            trigger: ".o_aite_cad_navtab_team",
            run: "click",
        },
        {
            content: "Le tableau par commercial a sa ligne de total",
            trigger: ".o_aite_cad_navtab_team[aria-selected='true']",
        },
        {
            trigger: ".o_aite_cad_by_user tfoot:contains('Total équipe')",
        },
        {
            content: "Cliquer sur le nombre « À venir » de la collègue",
            trigger: "tr.o_aite_cad_by_user_row:contains('Collègue (tour)') .o_aite_cad_drill_upcoming",
            run: "click",
        },
        {
            content: "Retour sur « À traiter », sélection « À venir »",
            trigger: ".o_aite_cad_navtab_todo[aria-selected='true']",
        },
        {
            content: "Seules les activités de la collègue sont listées",
            trigger: ".o_aite_cad_tab_upcoming.btn-primary",
        },
        {
            trigger: ".o_aite_cad:has(tr.o_aite_cad_activity:contains('Préparer la réunion (tour)')):not(:has(tr.o_aite_cad_activity:contains('Envoyer le devis (tour)')))",
        },
        {
            content: "Sélection « En cours »",
            trigger: ".o_aite_cad_tab_all",
            run: "click",
        },
        {
            trigger: ".o_aite_cad_tab_all.btn-primary",
        },
        {
            content: "Onglet « Équipe », plan de charge",
            trigger: ".o_aite_cad_navtab_team",
            run: "click",
        },
        {
            content: "Cliquer sur une case de la collègue",
            trigger: ".o_aite_cad_workload tr.o_aite_cad_wl_row:contains('Collègue (tour)') .o_aite_cad_wl_cell",
            run: "click",
        },
        {
            content: "La liste s'ouvre sur « À venir »",
            trigger: ".o_aite_cad_navtab_todo[aria-selected='true']",
        },
        {
            trigger: ".o_aite_cad_tab_upcoming.btn-primary",
        },
        {
            trigger: "tr.o_aite_cad_activity:contains('Préparer la réunion (tour)')",
        },

        // 5. Tendances ------------------------------------------------------
        {
            content: "Retirer le filtre sur la collègue",
            trigger: ".o_aite_cad_filter_user",
            run: "selectByLabel Tous les commerciaux",
        },
        {
            trigger: ".o_aite_cad:has(tr.o_aite_cad_activity:contains('Envoyer le devis (tour)'))",
        },
        {
            content: "Onglet « Tendances »",
            trigger: ".o_aite_cad_navtab_trends",
            run: "click",
        },
        {
            content: "Le graphique est dessiné",
            trigger: ".o_aite_cad_trends .o_aite_cad_chart canvas",
            run: "canvasNotEmpty",
        },
        {
            content: "Le classement par personne a au moins une ligne",
            trigger: ".o_aite_cad_trend_by_user .o_aite_cad_ranking_row",
        },
        {
            content: "Analyser dans le tableau croisé",
            trigger: ".o_aite_cad_open_report",
            run: "click",
        },
        {
            content: "Le rapport d'analyse s'ouvre ; revenir au tableau de bord",
            trigger: ".o_pivot_view",
        },
        {
            trigger: ".breadcrumb-item.o_back_button",
            run: "click",
        },
        {
            content: "L'onglet « Tendances » est retrouvé",
            trigger: ".o_aite_cad_navtab_trends[aria-selected='true']",
        },
        {
            trigger: ".o_aite_cad_trends .o_aite_cad_chart canvas",
            run: "canvasNotEmpty",
        },
        {
            content: "Retour sur « À traiter » : le graphique est retiré",
            trigger: ".o_aite_cad_navtab_todo",
            run: "click",
        },
        {
            trigger: ".o_aite_cad:not(:has(canvas)) .o_aite_cad_navtab_todo[aria-selected='true']",
        },
    ],
});

/**
 * Lien direct « Activités en retard » (bouton du récapitulatif du matin) :
 * le tableau de bord s'ouvre sur la sélection « En retard ».
 */
registry.category("web_tour.tours").add("aite_crm_activity_overdue_link_tour", {
    steps: () => [
        {
            content: "La sélection « En retard » est choisie d'emblée",
            trigger: ".o_aite_cad .o_aite_cad_tab_overdue.btn-primary",
        },
        {
            content: "L'activité en retard est listée",
            trigger: "tr.o_aite_cad_activity:contains('Relance en retard (tour)')",
        },
        {
            content: "… mais pas celle du jour",
            trigger: ".o_aite_cad:not(:has(tr.o_aite_cad_activity:contains('Appel du jour (tour)')))",
        },
    ],
});
