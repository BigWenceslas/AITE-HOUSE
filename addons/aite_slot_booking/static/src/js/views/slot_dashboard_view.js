/** @odoo-module **/

import { Component, useState, useRef, onWillStart, onMounted, onWillUnmount } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { loadChart, destroyChart } from "../services/chartjs_loader";
import { KpiCard } from "../components/kpi_card";
import {
    COLORS, STATE_BADGE, STATE_LABEL,
    fmtMoney, fmtPct, fmtHours, hourLabel,
    PERIOD_PRESETS, periodRange, shiftDay,
} from "../services/utils";

/**
 * Tableau de bord Espaces & Prestations.
 *
 * Le planning du jour consomme la même API de disponibilité que le site
 * web (``get_day_grid`` côté ressource) : une seule source de vérité.
 * Règles OWL de production : aucun global JS dans le template, tout le
 * positionnement des couloirs passe par des méthodes du composant.
 */
export class SlotDashboardView extends Component {
    static template = "aite_slot_booking.DashboardView";
    static components = { KpiCard };
    static props = {};

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");

        const initial = periodRange("today");
        this.state = useState({
            loading: true,
            day: initial.date_from,
            period: "today",
            dateFrom: initial.date_from,
            dateTo: initial.date_to,
            kind: "",
            resourceId: 0,
            meta: { currency_symbol: "F", kinds: [], is_manager: false },
            resources: [],
            board: [],
            kpis: {},
            bookings: [],
            mix: [],
            fill: [],
        });

        this.mixRef = useRef("mixChart");
        this.fillRef = useRef("fillChart");
        this._charts = {};

        onWillStart(async () => {
            await loadChart();
            const M = "aite.slot.dashboard";
            const [meta, resources] = await Promise.all([
                this.orm.call(M, "get_meta", []),
                this.orm.call(M, "get_resources", []),
            ]);
            this.state.meta = meta;
            this.state.day = meta.today || this.state.day;
            this.state.resources = resources;
            await this.loadAll();
        });
        onMounted(() => this.renderCharts());
        onWillUnmount(() => this.destroyCharts());
    }

    // ------------------------------------------------------------------
    // Chargement
    // ------------------------------------------------------------------

    async loadAll() {
        this.state.loading = true;
        const M = "aite.slot.dashboard";
        const kind = this.state.kind || null;
        const res = this.state.resourceId || null;
        const df = this.state.dateFrom;
        const dt = this.state.dateTo;
        const [board, kpis, bookings, mix, fill] = await Promise.all([
            this.orm.call(M, "get_day_board", [this.state.day, kind]),
            this.orm.call(M, "get_kpis", [df, dt, kind, res]),
            this.orm.call(M, "get_bookings", [df, dt, kind, res, 80]),
            this.orm.call(M, "get_service_mix", [df, dt, kind]),
            this.orm.call(M, "get_fill_by_resource", [df, dt, kind]),
        ]);
        this.state.board = board;
        this.state.kpis = kpis;
        this.state.bookings = bookings;
        this.state.mix = mix;
        this.state.fill = fill;
        this.state.loading = false;
    }

    async refresh() {
        await this.loadAll();
        this.renderCharts();
    }

    async setDay(delta) {
        this.state.day = shiftDay(this.state.day, delta);
        await this.refresh();
    }

    async setToday() {
        this.state.day = this.state.meta.today;
        await this.refresh();
    }

    onDayInput(ev) {
        this.state.day = ev.target.value;
        this.refresh();
    }

    async setPeriod(key) {
        this.state.period = key;
        const r = periodRange(key);
        this.state.dateFrom = r.date_from;
        this.state.dateTo = r.date_to;
        await this.refresh();
    }

    async setKind(kind) {
        this.state.kind = kind;
        this.state.resourceId = 0;
        await this.refresh();
    }

    async setResource(id) {
        this.state.resourceId = id;
        await this.refresh();
    }

    // ------------------------------------------------------------------
    // Dérivations & formatage (exposés au template)
    // ------------------------------------------------------------------

    get periodPresets() {
        return PERIOD_PRESETS;
    }

    get kindChips() {
        return this.state.meta.kinds || [];
    }

    get resourceChips() {
        const kind = this.state.kind;
        return this.state.resources.filter(
            (r) => !kind || r.kind === kind);
    }

    money(v) {
        return fmtMoney(v, this.state.meta.currency_symbol);
    }

    pct(v) {
        return fmtPct(v);
    }

    hours(v) {
        return fmtHours(v);
    }

    num(v) {
        return "" + (v === undefined || v === null ? 0 : v);
    }

    badge(state) {
        return STATE_BADGE[state] || STATE_BADGE.draft;
    }

    stateLabel(state) {
        return STATE_LABEL[state] || state;
    }

    dotStyle(color) {
        return "background:" + (color || "#714B67");
    }

    sourceLabel(src) {
        return src === "online" ? "En ligne" : "Comptoir";
    }

    postedMark(b) {
        return b.posted ? "✓ folio" : "—";
    }

    pickupMark(b) {
        if (b.kind !== "pressing") {
            return "";
        }
        return b.pickup_done ? "retiré" : "à retirer";
    }

    /** Position d'un bloc réservation dans son couloir (en %). */
    laneStyle(b, res) {
        const span = (res.close_hour - res.open_hour) || 1;
        const left = (b.start_h - res.open_hour) / span * 100;
        const width = (b.stop_h - b.start_h) / span * 100;
        return "left:" + left.toFixed(2) + "%;width:" +
            width.toFixed(2) + "%";
    }

    /** Graduations horaires du couloir (une par pas de 2 h). */
    laneTicks(res) {
        const ticks = [];
        const span = (res.close_hour - res.open_hour) || 1;
        for (let h = res.open_hour; h <= res.close_hour; h += 2) {
            ticks.push({
                key: "" + h,
                left: ((h - res.open_hour) / span * 100).toFixed(2),
                label: hourLabel(h),
            });
        }
        return ticks;
    }

    tickStyle(t) {
        return "left:" + t.left + "%";
    }

    boardFreeText(board) {
        let free = 0;
        let total = 0;
        for (const s of board.slots) {
            total += 1;
            if (s.state === "free") {
                free += 1;
            }
        }
        return free + "/" + total + " créneaux libres";
    }

    // ------------------------------------------------------------------
    // Graphiques
    // ------------------------------------------------------------------

    destroyCharts() {
        Object.values(this._charts).forEach(destroyChart);
        this._charts = {};
    }

    renderCharts() {
        if (this.state.loading) {
            return;
        }
        requestAnimationFrame(() => {
            this.destroyCharts();
            this._renderMix();
            this._renderFill();
        });
    }

    _mk(key, el, cfg) {
        if (!el || typeof window.Chart === "undefined") {
            return;
        }
        this._charts[key] = new window.Chart(el, cfg);
    }

    _renderMix() {
        const rows = this.state.mix;
        this._mk("mix", this.mixRef.el, {
            type: "doughnut",
            data: {
                labels: rows.map((r) => r.label),
                datasets: [{
                    data: rows.map((r) => r.amount),
                    backgroundColor: rows.map((r) => r.color),
                    borderWidth: 2,
                    borderColor: "#fff",
                }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: "56%",
                plugins: {
                    legend: {
                        position: "right",
                        labels: { font: { size: 11 }, boxWidth: 12 },
                    },
                },
            },
        });
    }

    _renderFill() {
        const rows = this.state.fill;
        this._mk("fill", this.fillRef.el, {
            type: "bar",
            data: {
                labels: rows.map((r) => r.name),
                datasets: [{
                    data: rows.map((r) => r.fill),
                    backgroundColor: rows.map((r) => r.color),
                    borderRadius: 3,
                }],
            },
            options: {
                indexAxis: "y",
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: {
                        max: 100,
                        ticks: {
                            callback: (v) => v + " %",
                            font: { size: 9 },
                        },
                    },
                    y: { ticks: { font: { size: 10 } } },
                },
            },
        });
    }

    // ------------------------------------------------------------------
    // Navigation
    // ------------------------------------------------------------------

    openBooking(id) {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "aite.slot.booking",
            res_id: id,
            views: [[false, "form"]],
            target: "current",
        });
    }

    newBooking() {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "aite.slot.booking",
            views: [[false, "form"]],
            target: "current",
        });
    }
}
