import { Component, onWillStart, useRef, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";
import { deserializeDate, formatDate, serializeDate } from "@web/core/l10n/dates";
import { Dropdown } from "@web/core/dropdown/dropdown";
import { DropdownItem } from "@web/core/dropdown/dropdown_item";
import { formatMonetary } from "@web/views/fields/formatters";
import { useSetupAction } from "@web/search/action_hook";
import { standardActionServiceProps } from "@web/webclient/actions/action_service";
import {
    AiteActivityDateDialog,
    AiteActivityDoneDialog,
    AiteActivityReassignDialog,
} from "./activity_dialogs";

const { DateTime } = luxon;

const DASHBOARD_MODEL = "aite.crm.activity.dashboard";
// Valeur du filtre « Commercial » pour ce qui n'est assigné à personne.
const UNASSIGNED = "unassigned";

/**
 * CRM → Suivi des activités.
 *
 * Toutes les données viennent de aite.crm.activity.dashboard
 * (get_dashboard_data), calculées côté serveur avec les droits de
 * l'utilisateur ; les actions (fait, reporter, réassigner) passent par
 * les méthodes action_* du même modèle, puis le tableau est rechargé.
 */
export class AiteCrmActivityDashboard extends Component {
    static template = "aite_crm_activity.Dashboard";
    static components = { Dropdown, DropdownItem };
    static props = { ...standardActionServiceProps };

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.dialog = useService("dialog");
        this.notification = useService("notification");
        this.UNASSIGNED = UNASSIGNED;
        this.rootRef = useRef("root");
        // Retour par le fil d'Ariane : on retrouve ses filtres (et la
        // position de défilement, gérée par Odoo via .o_content).
        const restored = this.props.state?.filters;
        this.state = useState({
            data: null,
            filters: restored ? { ...restored } : {},
            loading: true,
            busyIds: {},
        });
        this.lastRequest = 0;
        useSetupAction({
            rootRef: this.rootRef,
            getLocalState: () => ({ filters: { ...this.state.filters } }),
        });
        onWillStart(() => this.load());
    }

    // ------------------------------------------------------------------
    // Chargement
    // ------------------------------------------------------------------

    /**
     * Recharge le tableau avec les filtres modifiés. Les filtres sont
     * appliqués tout de suite (deux changements rapprochés se cumulent) et
     * seule la réponse à la dernière demande est affichée.
     */
    async load(changes = {}) {
        const filters = { ...this.state.filters, ...changes };
        this.state.filters = filters;
        const request = ++this.lastRequest;
        this.state.loading = true;
        try {
            const data = await this.orm.call(DASHBOARD_MODEL, "get_dashboard_data", [], {
                filters,
            });
            if (request === this.lastRequest) {
                this.state.data = data;
                this.state.filters = { ...data.filters };
            }
        } finally {
            if (request === this.lastRequest) {
                this.state.loading = false;
            }
        }
    }

    get data() {
        return this.state.data;
    }

    get kpiCards() {
        const k = this.data.kpis;
        return [
            { key: "overdue", label: _t("En retard"), value: k.overdue, tone: "danger", icon: "fa-exclamation-circle" },
            { key: "today", label: _t("Aujourd'hui"), value: k.today, tone: "warning", icon: "fa-calendar-check-o" },
            { key: "upcoming", label: _t("À venir (%s j)", this.data.upcoming_days), value: k.upcoming, tone: "info", icon: "fa-calendar" },
            { key: "done", label: _t("Réalisées (%s j)", this.data.done_days), value: k.done, tone: "success", icon: "fa-check-circle" },
            { key: "stalled", label: _t("Opportunités sans activité"), value: k.stalled, tone: "body", icon: "fa-pause-circle" },
        ];
    }

    get bucketTabs() {
        const k = this.data.kpis;
        return [
            { key: "all", label: _t("En cours"), count: k.open },
            { key: "overdue", label: _t("En retard"), count: k.overdue },
            { key: "today", label: _t("Aujourd'hui"), count: k.today },
            { key: "upcoming", label: _t("À venir"), count: k.upcoming },
            { key: "done", label: _t("Réalisées"), count: k.done },
        ];
    }

    isBusy(activity) {
        return Boolean(this.state.busyIds[activity.id]);
    }

    // ------------------------------------------------------------------
    // Filtres
    // ------------------------------------------------------------------

    onFilterChange(key, ev) {
        const value = ev.target.value;
        let parsed = false;
        if (value === UNASSIGNED) {
            parsed = UNASSIGNED;
        } else if (value) {
            parsed = parseInt(value);
        }
        this.load({ [key]: parsed });
    }

    selectBucket(bucket) {
        this.load({ bucket });
    }

    onKpiClick(card) {
        if (card.key === "stalled") {
            this.rootRef.el
                ?.querySelector(".o_aite_cad_stalled")
                ?.scrollIntoView({ behavior: "smooth" });
            return;
        }
        this.selectBucket(card.key);
    }

    /** Clic sur une ligne « Par commercial » : filtre sur lui, ou retire
     * le filtre si la ligne était déjà sélectionnée. */
    filterOnUser(userId) {
        this.load({ user_id: this.state.filters.user_id === userId ? false : userId });
    }

    onUserRowKeydown(ev, userId) {
        if (ev.key === "Enter" || ev.key === " ") {
            ev.preventDefault();
            this.filterOnUser(userId);
        }
    }

    // ------------------------------------------------------------------
    // Affichage
    // ------------------------------------------------------------------

    formatDate(value) {
        return value ? formatDate(deserializeDate(value)) : "";
    }

    formatAmount(lead) {
        if (!lead || !lead.expected_revenue) {
            return "";
        }
        return formatMonetary(lead.expected_revenue, { currencyId: lead.currency_id, digits: [69, 0] });
    }

    deadlineLabel(activity) {
        if (activity.state === "done") {
            return _t("Faite le %s", this.formatDate(activity.date_done));
        }
        if (activity.days === 0) {
            return _t("Aujourd'hui");
        }
        if (activity.days === 1) {
            return _t("Demain");
        }
        if (activity.days < 0) {
            return _t("%s j de retard", -activity.days);
        }
        return _t("Dans %s j", activity.days);
    }

    // ------------------------------------------------------------------
    // Actions
    // ------------------------------------------------------------------

    /**
     * Appelle une action du serveur sur une activité, puis recharge.
     * `message` peut être une fonction recevant le résultat de l'action.
     */
    async runAction(activity, method, args, message) {
        this.state.busyIds[activity.id] = true;
        try {
            const result = await this.orm.call(DASHBOARD_MODEL, method, args);
            const text = typeof message === "function" ? message(result) : message;
            this.notification.add(text, { type: "success" });
            await this.load();
        } finally {
            delete this.state.busyIds[activity.id];
        }
    }

    markDone(activity) {
        this.dialog.add(AiteActivityDoneDialog, {
            activity,
            onConfirm: (feedback) =>
                this.runAction(activity, "action_mark_done", [activity.id, feedback],
                    _t("Activité marquée comme faite.")),
        });
    }

    /**
     * Nouvelle échéance : 'tomorrow', 'monday' ou 'week' (calculés par le
     * serveur sur la date du jour), ou une date AAAA-MM-JJ.
     */
    reschedule(activity, value) {
        return this.runAction(activity, "action_reschedule", [activity.id, value],
            (date) => _t("Nouvelle échéance : %s.", this.formatDate(date)));
    }

    rescheduleOnDate(activity) {
        const today = DateTime.local().startOf("day");
        this.dialog.add(AiteActivityDateDialog, {
            activity,
            defaultDate: serializeDate(today.plus({ days: 1 })),
            minDate: serializeDate(today),
            onConfirm: (value) => this.reschedule(activity, value),
        });
    }

    reassign(activity) {
        this.dialog.add(AiteActivityReassignDialog, {
            activity,
            users: this.data.options.assignable_users.filter((u) => u.id !== activity.user_id),
            onConfirm: (user) =>
                this.runAction(activity, "action_reassign", [activity.id, user.id],
                    _t("Activité réassignée à %s.", user.name)),
        });
    }

    openLead(leadId) {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "crm.lead",
            res_id: leadId,
            views: [[false, "form"]],
        });
    }

    async scheduleActivity(lead) {
        // Même fenêtre que le bouton « Planifier une activité » d'Odoo.
        await new Promise((resolve) =>
            this.action.doAction(
                {
                    type: "ir.actions.act_window",
                    name: _t("Planifier une activité"),
                    res_model: "mail.activity.schedule",
                    view_mode: "form",
                    views: [[false, "form"]],
                    target: "new",
                    context: {
                        active_model: "crm.lead",
                        active_ids: [lead.id],
                        active_id: lead.id,
                    },
                },
                { onClose: resolve, additionalContext: { dialog_size: "large" } }
            )
        );
        await this.load();
    }
}

registry.category("actions").add("aite_crm_activity_dashboard", AiteCrmActivityDashboard);
