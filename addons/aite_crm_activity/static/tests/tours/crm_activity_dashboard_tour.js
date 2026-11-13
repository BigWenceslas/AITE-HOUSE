import { registry } from "@web/core/registry";
import { SIZES } from "@web/core/ui/ui_service";

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
 * parcours la retirerait) : un libellé qui en contient une se met entre
 * apostrophes (« selectByLabel 'Collègue (tour)' »), sans quoi l'option
 * visée ne serait pas trouvée et la dernière de la liste serait choisie.
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
            run: "selectByLabel 'Collègue (tour)'",
        },
        {
            content: "C'est bien la collègue qui est choisie (d'autres commerciaux sont listés)",
            trigger: ".modal select.o_aite_cad_reassign_user:has(option:selected:text('Collègue (tour)'))",
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

/**
 * Aperçu plein écran (sous 992 px) et changement de largeur pendant qu'une
 * fenêtre ou le menu « Reporter » est ouvert depuis l'aperçu ; focus après
 * une action refusée.
 *
 * La largeur est simulée en changeant la taille d'écran d'Odoo (comme une
 * tablette qu'on tourne) : l'aperçu change de comportement, la page garde
 * sa mise en page d'ordinateur. Données créées par tests/test_ui.py.
 */
const uiService = () => odoo.__WOWL_DEBUG__.root.env.services.ui;

/** Change la taille d'écran, puis attend le rendu qui suit. */
async function setScreenSize(size) {
    uiService().size = size;
    await new Promise((resolve) =>
        requestAnimationFrame(() => requestAnimationFrame(() => setTimeout(resolve)))
    );
}

function check(condition, message) {
    if (!condition) {
        throw new Error(message);
    }
}

const PREVIEW_LINK = "tr.o_aite_cad_activity:contains('Appeler (tour)') .o_aite_cad_lead_link";
const CALL_ITEM = ".o_aite_cad_panel_activity:contains('Appeler (tour)')";
const STALE_ITEM = ".o_aite_cad_panel_activity:contains('Relancer (tour)')";

registry.category("web_tour.tours").add("aite_crm_activity_panel_modal_tour", {
    steps: () => [
        // 1. Fenêtre « Fait » ouverte pendant le passage en plein écran -----
        {
            content: "Ouvrir l'aperçu (ordinateur : panneau latéral)",
            trigger: PREVIEW_LINK,
            run: "click",
        },
        {
            content: "Marquer comme fait depuis l'aperçu",
            trigger: `.o_aite_cad_panel[aria-modal='false'] ${CALL_ITEM} .o_aite_cad_done`,
            run: "click",
        },
        {
            content: "Saisir le compte rendu",
            trigger: ".modal .o_aite_cad_feedback",
            run: "edit Client rappelé",
        },
        {
            content: "Passage sous 992 px pendant la saisie",
            trigger: ".modal .o_aite_cad_feedback:focus",
            run: () => setScreenSize(SIZES.MD),
        },
        {
            content: "La saisie garde le focus ; l'aperçu attend la fermeture de la fenêtre",
            trigger: "body:has(.o_aite_cad_panel[aria-modal='false']) .modal .o_aite_cad_feedback:focus",
            run() {
                check(uiService().activeElement.contains(this.anchor), "La fenêtre doit rester l'élément actif");
            },
        },
        {
            content: "Échap ferme la fenêtre, pas l'aperçu",
            trigger: ".modal .o_aite_cad_feedback:focus",
            run: "press Escape",
        },
        {
            content: "L'aperçu reste ouvert et devient une fenêtre modale",
            trigger: "body:not(:has(.modal)) .o_aite_cad_panel[aria-modal='true']",
            run() {
                check(uiService().activeElement === this.anchor, "L'aperçu doit être l'élément actif");
                check(this.anchor.contains(document.activeElement), "Le focus doit être dans l'aperçu");
            },
        },
        {
            content: "Échap ferme maintenant l'aperçu",
            trigger: ".o_aite_cad_panel[aria-modal='true'] .o_aite_cad_panel_title:contains('Opportunité de l')",
            run: "press Escape",
        },
        {
            content: "L'aperçu est fermé",
            trigger: NO_PANEL,
        },

        // 2. Menu « Reporter » ouvert pendant le retour au panneau latéral ---
        {
            content: "Rouvrir l'aperçu, plein écran",
            trigger: PREVIEW_LINK,
            run: "click",
        },
        {
            content: "Ouvrir le menu « Reporter » de l'aperçu",
            trigger: `.o_aite_cad_panel[aria-modal='true'] ${CALL_ITEM} .o_aite_cad_reschedule`,
            run: "click",
        },
        {
            content: "Passage au-dessus de 992 px, menu ouvert",
            trigger: ".o-dropdown--menu .o_aite_cad_reschedule_tomorrow",
            run: () => setScreenSize(SIZES.XL),
        },
        {
            content: "Échap ferme le menu, pas l'aperçu",
            trigger: ".o-dropdown--menu .o_aite_cad_reschedule_tomorrow",
            run: "press Escape",
        },
        {
            content: "L'aperçu reste ouvert et redevient un panneau latéral",
            trigger: "body:not(:has(.o-dropdown--menu)) .o_aite_cad_panel[aria-modal='false']",
            run() {
                check(uiService().activeElement === document, "La page doit redevenir l'élément actif");
            },
        },
        {
            content: "Échap ferme l'aperçu",
            trigger: ".o_aite_cad_panel[aria-modal='false'] .o_aite_cad_panel_title:contains('Opportunité de l')",
            run: "press Escape",
        },
        {
            content: "L'aperçu est fermé ; repasser sous 992 px",
            trigger: NO_PANEL,
            run: () => setScreenSize(SIZES.MD),
        },

        // 3. Action refusée depuis l'aperçu plein écran ---------------------
        {
            content: "Rouvrir l'aperçu, plein écran",
            trigger: PREVIEW_LINK,
            run: "click",
        },
        {
            content: "Une autre session supprime l'activité « Relancer »",
            trigger: `.o_aite_cad_panel[aria-modal='true'] ${STALE_ITEM}`,
            async run() {
                const orm = odoo.__WOWL_DEBUG__.root.env.services.orm;
                await orm.unlink("mail.activity", [parseInt(this.anchor.dataset.activityId)]);
            },
        },
        {
            content: "La reporter à demain depuis l'aperçu",
            trigger: `.o_aite_cad_panel ${STALE_ITEM} .o_aite_cad_reschedule`,
            run: "click",
        },
        {
            trigger: ".o-dropdown--menu .o_aite_cad_reschedule_tomorrow",
            run: "click",
        },
        {
            content: "Odoo refuse l'action ; l'aperçu rechargé n'a plus l'activité",
            trigger: `body:not(:has(${STALE_ITEM})) .modal:contains('existe plus')`,
        },
        {
            content: "Fermer le message par Échap",
            trigger: ".modal:contains('existe plus')",
            run: "press Escape",
        },
        {
            content: "Le focus revient à l'aperçu (le bouton qui avait ouvert le menu a disparu)",
            trigger: "body:not(:has(.modal)) .o_aite_cad_panel[aria-modal='true'] .o_aite_cad_panel_close:focus",
        },
        {
            content: "Focus perdu sur la page : Tab revient dans l'aperçu",
            trigger: ".o_aite_cad_panel .o_aite_cad_panel_close:focus",
            async run(helpers) {
                document.activeElement.blur();
                check(document.activeElement === document.body, "Le focus doit être sur la page");
                await helpers.press("Tab");
            },
        },
        {
            content: "Tab est resté dans l'aperçu ; Échap le ferme",
            trigger: ".o_aite_cad_panel .o_aite_cad_panel_close:focus",
            run: "press Escape",
        },
        {
            content: "L'aperçu est fermé ; largeur d'ordinateur rétablie",
            trigger: NO_PANEL,
            run: () => setScreenSize(SIZES.XL),
        },
    ],
});
