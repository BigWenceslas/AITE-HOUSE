import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";
import { deserializeDate, formatDate, serializeDate } from "@web/core/l10n/dates";
import { formatMonetary } from "@web/views/fields/formatters";
import { standardActionServiceProps } from "@web/webclient/actions/action_service";
import { AiteActivityDateDialog, AiteActivityDoneDialog } from "./activity_dialogs";

const { DateTime } = luxon;

const DASHBOARD_MODEL = "aite.crm.activity.dashboard";

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
    static props = { ...standardActionServiceProps };

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.dialog = useService("dialog");
        this.notification = useService("notification");
        this.state = useState({
            data: null,
            filters: {},
            loading: true,
            busyId: null,
        });
        onWillStart(() => this.load());
    }

    // ------------------------------------------------------------------
    // Chargement
    // ------------------------------------------------------------------

    async load(changes = {}) {
        this.state.loading = true;
        try {
            const filters = { ...this.state.filters, ...changes };
            const data = await this.orm.call(DASHBOARD_MODEL, "get_dashboard_data", [], {
                filters,
            });
            this.state.data = data;
            this.state.filters = { ...data.filters };
        } finally {
            this.state.loading = false;
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

    // ------------------------------------------------------------------
    // Filtres
    // ------------------------------------------------------------------

    onFilterChange(key, ev) {
        const value = ev.target.value;
        this.load({ [key]: value ? parseInt(value) : false });
    }

    selectBucket(bucket) {
        this.load({ bucket });
    }

    onKpiClick(card) {
        if (card.key === "stalled") {
            document.querySelector(".o_aite_cad_stalled")?.scrollIntoView({ behavior: "smooth" });
            return;
        }
        this.selectBucket(card.key);
    }

    filterOnUser(userId) {
        this.load({ user_id: userId || false });
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

    async runAction(activity, method, args, message) {
        this.state.busyId = activity.id;
        try {
            await this.orm.call(DASHBOARD_MODEL, method, args);
            this.notification.add(message, { type: "success" });
            await this.load();
        } finally {
            this.state.busyId = null;
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

    onReschedule(activity, ev) {
        const choice = ev.target.value;
        ev.target.value = "";
        const today = DateTime.fromISO(this.data.today);
        let date;
        if (choice === "tomorrow") {
            date = today.plus({ days: 1 });
        } else if (choice === "monday") {
            date = today.plus({ weeks: 1 }).startOf("week");
        } else if (choice === "week") {
            date = today.plus({ days: 7 });
        } else if (choice === "custom") {
            this.dialog.add(AiteActivityDateDialog, {
                activity,
                defaultDate: serializeDate(today.plus({ days: 1 })),
                onConfirm: (value) =>
                    this.runAction(activity, "action_reschedule", [activity.id, value],
                        _t("Activité reportée au %s.", this.formatDate(value))),
            });
            return;
        } else {
            return;
        }
        const value = serializeDate(date);
        this.runAction(activity, "action_reschedule", [activity.id, value],
            _t("Activité reportée au %s.", this.formatDate(value)));
    }

    onReassign(activity, ev) {
        const userId = parseInt(ev.target.value);
        ev.target.value = "";
        if (!userId || userId === activity.user_id) {
            return;
        }
        const user = this.data.options.assignable_users.find((u) => u.id === userId);
        this.runAction(activity, "action_reassign", [activity.id, userId],
            _t("Activité réassignée à %s.", user ? user.name : ""));
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
