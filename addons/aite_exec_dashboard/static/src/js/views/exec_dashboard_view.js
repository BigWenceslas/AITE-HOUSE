/** @odoo-module **/

import { Component, useState, useRef, onWillStart, onMounted, onWillUnmount } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { loadChart, destroyChart } from "../services/chartjs_loader";
import { KpiCard } from "../components/kpi_card";
import {
    fmtMoney, fmtPct, fmtInt, fmtCount, fmtDate, PERIOD_PRESETS,
    periodRange, monthLabel,
} from "../services/utils";

/**
 * Tableau de bord Direction — une page, trois pôles.
 * Règles OWL de production : aucun global JS dans les templates,
 * formats et dérivations exposés par des méthodes du composant.
 */
export class ExecDashboardView extends Component {
    static template = "aite_exec_dashboard.DashboardView";
    static components = { KpiCard };
    static props = {};

    setup() {
        this.orm = useService("orm");

        const initial = periodRange("month");
        this.state = useState({
            loading: true,
            period: "month",
            dateFrom: initial.date_from,
            dateTo: initial.date_to,
            meta: { currency_symbol: "F", has_loyalty: false, poles: [],
                    hints: {} },
            kpis: { mix: [], deltas_ly: {}, pickup: {}, pace: {} },
            evolution: { labels: [], series: [] },
        });

        this.mixRef = useRef("mixChart");
        this.evoRef = useRef("evoChart");
        this._charts = {};

        onWillStart(async () => {
            await loadChart();
            this.state.meta = await this.orm.call(
                "aite.exec.dashboard", "get_meta", []);
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
        const M = "aite.exec.dashboard";
        const [kpis, evolution] = await Promise.all([
            this.orm.call(M, "get_kpis",
                [this.state.dateFrom, this.state.dateTo]),
            this.orm.call(M, "get_evolution", [6]),
        ]);
        this.state.kpis = kpis;
        this.state.evolution = evolution;
        this.state.loading = false;
    }

    async refresh() {
        await this.loadAll();
        this.renderCharts();
    }

    async setPeriod(key) {
        this.state.period = key;
        const r = periodRange(key);
        this.state.dateFrom = r.date_from;
        this.state.dateTo = r.date_to;
        await this.refresh();
    }

    onFromInput(ev) {
        this.state.period = "custom";
        this.state.dateFrom = ev.target.value;
        this.refresh();
    }

    onToInput(ev) {
        this.state.period = "custom";
        this.state.dateTo = ev.target.value;
        this.refresh();
    }

    // ------------------------------------------------------------------
    // Formats & dérivations
    // ------------------------------------------------------------------

    get periodPresets() {
        return PERIOD_PRESETS;
    }

    money(v) {
        return fmtMoney(v, this.state.meta.currency_symbol);
    }

    pct(v) {
        return fmtPct(v);
    }

    num(v) {
        return fmtInt(v);
    }

    poleLabel(key) {
        for (const p of this.state.meta.poles) {
            if (p.key === key) {
                return p.label;
            }
        }
        return key;
    }

    poleColor(key) {
        for (const p of this.state.meta.poles) {
            if (p.key === key) {
                return p.color;
            }
        }
        return "#888780";
    }

    dotStyle(key) {
        return "background:" + this.poleColor(key);
    }

    /** « Du 01/10/2026 au 15/10/2026 » (règle 6 ; écart n° 2). */
    get periodText() {
        return "Du " + fmtDate(this.state.dateFrom) + " au "
            + fmtDate(this.state.dateTo);
    }

    mixLine(row) {
        return this.money(row.amount) + " · " + this.pct(row.pct);
    }

    /** Phrase d'explication d'un indicateur (servie par le serveur). */
    hint(key) {
        return (this.state.meta.hints || {})[key] || "";
    }

    /** « 1 nuitée », « 12 nuitées » : accord en nombre, sans « (s) ». */
    count(n, one, many) {
        return fmtCount(n, one, many);
    }

    get pickupSub() {
        const p = this.state.kpis.pickup || {};
        // Le libellé de la carte ne porte plus « 7 j → 30 j » : la fenêtre
        // est dite ici, en toutes lettres.
        return fmtCount(p.reservations, "réservation prise",
            "réservations prises") + " ces "
            + (p.window_days || 7) + " derniers jours pour les "
            + (p.horizon_days || 30) + " prochains";
    }

    get paceSub() {
        const p = this.state.kpis.pace || {};
        return "mois " + (p.month ? monthLabel(p.month) : "") + " · N-1 à la même date : "
            + fmtCount(p.nights_ly, "nuitée", "nuitées");
    }

    /** Graduation de l'axe au format français : « 1,5 M », « 250 k »,
     *  « 0,5 » (l'axe écrivait « 2.5k », au point décimal). */
    kTick(v) {
        const opt = { maximumFractionDigits: 1 };
        const a = Math.abs(v);
        if (a >= 1e6) {
            return (v / 1e6).toLocaleString("fr-FR", opt) + "\u00a0M";
        }
        if (a >= 1e3) {
            return (v / 1e3).toLocaleString("fr-FR", opt) + "\u00a0k";
        }
        return v.toLocaleString("fr-FR", opt);
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
            this._renderEvolution();
        });
    }

    _mk(key, el, cfg) {
        if (!el || typeof window.Chart === "undefined") {
            return;
        }
        this._charts[key] = new window.Chart(el, cfg);
    }

    _renderMix() {
        const rows = this.state.kpis.mix || [];
        this._mk("mix", this.mixRef.el, {
            type: "doughnut",
            data: {
                labels: rows.map((r) => this.poleLabel(r.key)),
                datasets: [{
                    data: rows.map((r) => r.amount),
                    backgroundColor: rows.map((r) => this.poleColor(r.key)),
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

    _renderEvolution() {
        const evo = this.state.evolution;
        this._mk("evo", this.evoRef.el, {
            type: "bar",
            data: {
                labels: (evo.labels || []).map(monthLabel),
                datasets: (evo.series || []).map((s) => ({
                    label: s.label,
                    data: s.data,
                    backgroundColor: s.color,
                    borderRadius: 3,
                })),
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: "bottom",
                        labels: { font: { size: 10 }, boxWidth: 12 },
                    },
                },
                scales: {
                    x: { ticks: { font: { size: 10 } } },
                    y: {
                        ticks: {
                            font: { size: 9 },
                            callback: (v) => this.kTick(v),
                        },
                    },
                },
            },
        });
    }
}
