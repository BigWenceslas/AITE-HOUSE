import { registry } from "@web/core/registry";

/**
 * Parcours du tableau de bord « Suivi des activités » :
 * marquer une activité comme faite (avec compte rendu), puis en reporter
 * une autre. Les données sont créées par tests/test_ui.py ; les libellés
 * se terminent par « (tour) » pour ne viser qu'elles.
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
            content: "L'activité a quitté la liste",
            trigger: ".o_aite_cad:not(:has(.modal)):not(:has(tr.o_aite_cad_activity:contains('Rappeler le client (tour)')))",
        },
        {
            content: "Onglet « Aujourd'hui »",
            trigger: ".o_aite_cad_tab_today",
            run: "click",
        },
        {
            content: "Reporter l'activité du jour à demain",
            trigger: ".o_aite_cad_tab_today.btn-primary",
        },
        {
            trigger: "tr.o_aite_cad_activity:contains('Envoyer le devis (tour)') select.o_aite_cad_reschedule",
            run: "select tomorrow",
        },
        {
            content: "L'activité reportée n'est plus « du jour »",
            trigger: ".o_aite_cad:not(:has(tr.o_aite_cad_activity:contains('Envoyer le devis (tour)')))",
        },
        {
            content: "Planifier une activité sur l'opportunité sans suite",
            trigger: "tr.o_aite_cad_stalled_row:contains('Opportunité à relancer (tour)') .o_aite_cad_schedule",
            run: "click",
        },
        {
            content: "La fenêtre de planification d'Odoo s'ouvre",
            trigger: ".modal .o_form_view",
        },
        {
            trigger: ".modal .btn-close",
            run: "click",
        },
        {
            content: "Retour au tableau de bord",
            trigger: ".o_aite_cad:not(:has(.modal)) .o_aite_cad_kpi",
        },
    ],
});
