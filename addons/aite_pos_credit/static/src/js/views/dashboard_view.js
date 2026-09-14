/** @odoo-module **/

import { Component, useState, useRef, onWillStart, onMounted, onWillUnmount } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { loadChart, destroyChart } from "../services/chartjs_loader";
import { KpiCard } from "../components/kpi_card";
import {
    COLORS, PAYMENT_COLORS, AGING_COLORS, SEVERITY_BADGE, PAYMENT_LABELS,
    fmtMoney, fmtCompact, fmtPct, periodRange, PERIOD_PRESETS,
} from "../services/utils";

/**
 * Tableau de bord de recouvrement — version enrichie.
 *
 * Inspiré du dashboard Analytics : filtres période (presets + plage libre),
 * filtre par caisse, KPI avec variation vs période N-1, encours par caisse,
 * remboursements journaliers et top débiteurs avec barres proportionnelles.
 *
 * Règle d'or apprise sur le terrain : AUCUNE fonction globale JS (String,
 * Math…) dans le template OWL — tout calcul/formatage passe par des
 * méthodes du composant.
 */
export class CreditDashboardView extends Component {
    static template = "aite_pos_credit.DashboardView";
    static components = { KpiCard };
    static props = {};

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");

        const initial = periodRange("month");
        this.state = useState({
            loading: true,
            period: "month",
            dateFrom: initial.date_from,
            dateTo: initial.date_to,
            configId: 0,
            source: "all",
            configs: [],
            kpis: {},
            aging: [],
            topDebtors: [],
            paymentBreakdown: [],
            evolution: [],
            recentPayments: [],
            caisseBreakdown: [],
            dailyRecoveries: [],
            currencySymbol: "F",
        });

        this.agingRef = useRef("agingChart");
        this.evoRef = useRef("evoChart");
        this.payRef = useRef("payChart");
        this.caisseRef = useRef("caisseChart");
        this.dailyRef = useRef("dailyChart");
        this._charts = {};

        onWillStart(async () => {
            await loadChart();
            const M = "aite.pos.credit.dashboard";
            const [meta, configs] = await Promise.all([
                this.orm.call(M, "get_dashboard_meta", []),
                this.orm.call(M, "get_pos_configs", []),
            ]);
            this.state.currencySymbol = meta.currency_symbol || "F";
            this.state.configs = configs;
            await this.loadAll();
        });
        onMounted(() => this.renderCharts());
        onWillUnmount(() => this.destroyCharts());
    }

    // ------------------------------------------------------------------
    // Data
    // ------------------------------------------------------------------

    async loadAll() {
        this.state.loading = true;
        const df = this.state.dateFrom;
        const dt = this.state.dateTo;
        const cfg = this.state.configId || null;
        const src = this.state.source === "all" ? null : this.state.source;
        const M = "aite.pos.credit.dashboard";
        const [kpis, aging, top, pay, evo, recent, caisse, daily] =
            await Promise.all([
                this.orm.call(M, "get_kpis", [df, dt, cfg, src]),
                this.orm.call(M, "get_aging", [cfg, src]),
                this.orm.call(M, "get_top_debtors", [8, cfg, src]),
                this.orm.call(M, "get_payment_breakdown", [df, dt, cfg, src]),
                this.orm.call(M, "get_evolution", [6, cfg, src]),
                this.orm.call(M, "get_recent_payments", [df, dt, 50, cfg, src]),
                this.orm.call(M, "get_caisse_breakdown", [src]),
                this.orm.call(M, "get_daily_recoveries", [df, dt, cfg, src]),
            ]);
        this.state.kpis = kpis;
        this.state.aging = aging;
        this.state.topDebtors = top;
        this.state.paymentBreakdown = pay;
        this.state.evolution = evo;
        this.state.recentPayments = recent;
        this.state.caisseBreakdown = caisse;
        this.state.dailyRecoveries = daily;
        this.state.loading = false;
    }

    async refresh() {
        await this.loadAll();
        this.renderCharts();
    }

    async setPeriod(key) {
        this.state.period = key;
        const range = periodRange(key);
        this.state.dateFrom = range.date_from;
        this.state.dateTo = range.date_to;
        await this.refresh();
    }

    onDateFrom(ev) {
        this.state.dateFrom = ev.target.value;
    }

    onDateTo(ev) {
        this.state.dateTo = ev.target.value;
    }

    async applyCustomRange() {
        if (!this.state.dateFrom || !this.state.dateTo) {
            return;
        }
        this.state.period = "custom";
        await this.refresh();
    }

    async setSource(source) {
        this.state.source = source;
        await this.refresh();
    }

    async setConfig(configId) {
        this.state.configId = configId;
        await this.refresh();
    }

    // ------------------------------------------------------------------
    // Formatage exposé au template (jamais de globals JS dans le XML)
    // ------------------------------------------------------------------

    money(v) {
        return fmtMoney(v, this.state.currencySymbol);
    }

    pct(v) {
        return fmtPct(v);
    }

    num(v) {
        return "" + (v === undefined || v === null ? 0 : v);
    }

    days(v) {
        const n = v === undefined || v === null ? 0 : v;
        // Arrondi à l'entier côté JS (pas de Math dans le template).
        const rounded = n >= 0 ? (n + 0.5) | 0 : -((-n + 0.5) | 0);
        return "" + rounded + " j";
    }

    /**
     * Variation formatée pour un KPI.
     * :param pct: variation en % (peut être null → pas de delta affiché)
     * :param goodWhenUp: true si une hausse est positive (vert)
     * :returns: {text, cls} ou null
     */
    deltaOf(pct, goodWhenUp) {
        if (pct === null || pct === undefined) {
            return undefined;
        }
        const rounded = ((pct * 10 + (pct >= 0 ? 0.5 : -0.5)) | 0) / 10;
        const abs = rounded < 0 ? -rounded : rounded;
        const arrow = rounded > 0 ? "▲" : rounded < 0 ? "▼" : "■";
        const isGood = goodWhenUp ? rounded >= 0 : rounded <= 0;
        return {
            text: arrow + " " + ("" + abs).replace(".", ",") + " % vs N-1",
            cls: isGood ? "text-success" : "text-danger",
        };
    }

    /** Sous-texte de la carte Encours : flux net de la période. */
    netFlowSub() {
        const nf = this.state.kpis.net_flow || 0;
        const sign = nf > 0 ? "+" : "";
        return "flux période : " + sign + this.money(nf);
    }

    /**
     * Sous-texte enrichi de la carte Encours : quand les deux canaux
     * coexistent (filtre « Toutes origines » et encours Ventes non nul),
     * affiche la répartition POS / Ventes ; sinon, le flux net habituel.
     */
    outstandingSub() {
        const k = this.state.kpis;
        if (this.state.source === "all" && (k.sale_outstanding || 0) > 0) {
            return "POS " + this.money(k.pos_outstanding) +
                " · Ventes " + this.money(k.sale_outstanding);
        }
        return this.netFlowSub();
    }

    severityBadge(sev) {
        return SEVERITY_BADGE[sev] || SEVERITY_BADGE.recent;
    }

    paymentLabel(method) {
        return PAYMENT_LABELS[method] || method;
    }

    lastPay(row) {
        return row.last_payment ? row.last_payment : "—";
    }

    get periodPresets() {
        return PERIOD_PRESETS;
    }

    /** Style de barre proportionnelle pour le top débiteurs. */
    debtorBarStyle(row) {
        let max = 0;
        for (const d of this.state.topDebtors) {
            if (d.outstanding > max) {
                max = d.outstanding;
            }
        }
        const width = max ? (row.outstanding / max) * 100 : 0;
        return "width:" + width + "%";
    }

    // ------------------------------------------------------------------
    // Charts
    // ------------------------------------------------------------------

    destroyCharts() {
        Object.values(this._charts).forEach(destroyChart);
        this._charts = {};
    }

    renderCharts() {
        if (this.state.loading) {
            return;
        }
        this.destroyCharts();
        this._renderAging();
        this._renderEvolution();
        this._renderPayments();
        this._renderCaisse();
        this._renderDaily();
    }

    _mk(el, cfg) {
        if (!el || typeof window.Chart === "undefined") {
            return null;
        }
        return new window.Chart(el, cfg);
    }

    _moneyTicks() {
        return {
            ticks: { callback: (v) => fmtCompact(v), font: { size: 9 } },
        };
    }

    _renderAging() {
        const chart = this._mk(this.agingRef.el, {
            type: "bar",
            data: {
                labels: this.state.aging.map((b) => b.label),
                datasets: [{
                    label: "Encours",
                    data: this.state.aging.map((b) => b.amount),
                    backgroundColor: AGING_COLORS,
                    borderRadius: 3,
                }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: this._moneyTicks(),
                    x: { ticks: { font: { size: 10 } } },
                },
            },
        });
        if (chart) {
            this._charts.aging = chart;
        }
    }

    _renderEvolution() {
        const chart = this._mk(this.evoRef.el, {
            type: "line",
            data: {
                labels: this.state.evolution.map((e) => e.period),
                datasets: [
                    {
                        label: "Nouvelles ardoises",
                        data: this.state.evolution.map((e) => e.opened),
                        borderColor: COLORS.danger,
                        backgroundColor: COLORS.danger + "22",
                        tension: 0.3,
                        fill: true,
                    },
                    {
                        label: "Recouvré",
                        data: this.state.evolution.map((e) => e.recovered),
                        borderColor: COLORS.success,
                        backgroundColor: COLORS.success + "22",
                        tension: 0.3,
                        fill: true,
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: "bottom", labels: { font: { size: 10 } } },
                },
                scales: {
                    y: this._moneyTicks(),
                    x: { ticks: { font: { size: 10 } } },
                },
            },
        });
        if (chart) {
            this._charts.evo = chart;
        }
    }

    _renderPayments() {
        const rows = this.state.paymentBreakdown;
        const chart = this._mk(this.payRef.el, {
            type: "doughnut",
            data: {
                labels: rows.map((p) => p.label),
                datasets: [{
                    data: rows.map((p) => p.amount),
                    backgroundColor: rows.map(
                        (p) => PAYMENT_COLORS[p.method] || COLORS.primary),
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
        if (chart) {
            this._charts.pay = chart;
        }
    }

    _renderCaisse() {
        const rows = this.state.caisseBreakdown;
        const chart = this._mk(this.caisseRef.el, {
            type: "doughnut",
            data: {
                labels: rows.map((r) => r.name),
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
        if (chart) {
            this._charts.caisse = chart;
        }
    }

    _renderDaily() {
        const rows = this.state.dailyRecoveries;
        const chart = this._mk(this.dailyRef.el, {
            type: "bar",
            data: {
                labels: rows.map((r) => r.label),
                datasets: [{
                    label: "Remboursé",
                    data: rows.map((r) => r.amount),
                    backgroundColor: COLORS.primary,
                    borderRadius: 2,
                }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: this._moneyTicks(),
                    x: { ticks: { font: { size: 9 }, maxRotation: 60 } },
                },
            },
        });
        if (chart) {
            this._charts.daily = chart;
        }
    }

    // ------------------------------------------------------------------
    // Actions
    // ------------------------------------------------------------------

    openDebtor(partnerId) {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "aite.pos.credit",
            name: "Ardoises du client",
            views: [[false, "list"], [false, "form"]],
            domain: [["partner_id", "=", partnerId], ["state", "=", "open"]],
            target: "current",
        });
    }

    openAllArdoises() {
        this.action.doAction("aite_pos_credit.action_aite_pos_credit");
    }

    openAllPayments() {
        this.action.doAction("aite_pos_credit.action_aite_pos_credit_payment");
    }
}
