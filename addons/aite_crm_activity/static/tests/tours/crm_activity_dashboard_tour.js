import { registry } from "@web/core/registry";

/**
 * Parcours du tableau de bord « Suivi des activités » : marquer une
 * activité comme faite (avec compte rendu), en reporter une autre, en
 * réassigner une troisième, puis planifier une activité sur une
 * opportunité qui n'en avait pas. Les données sont créées par
 * tests/test_ui.py ; les libellés se terminent par « (tour) » pour ne viser
 * qu'elles. Les fenêtres d'Odoo s'affichent hors du tableau de bord : on
 * vérifie leur fermeture sur body.
 */
registry.category("web_tour.tours").add("aite_crm_activity_dashboard_tour", {
    steps: () => [
        {
            content: "Le tableau de bord est chargé",
            trigger: ".o_aite_cad .o_aite_cad_kpi_overdue",
            run: "click",
        },
        {
            content: "Onglet « En retard » sélectionné",
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
            content: "Onglet « Aujourd'hui »",
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
            content: "Onglet « À venir »",
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
    ],
});
