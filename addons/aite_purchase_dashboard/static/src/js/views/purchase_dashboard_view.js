/** @odoo-module **/

import { Component, useState, useRef, onWillStart, onMounted, onWillUnmount } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { loadChart, destroyChart } from "../services/chartjs_loader";
import { KpiCard } from "../components/kpi_card";
import {
    COLORS, AGING_COLORS, BADGE_CLS,
    fmtMoney, fmtCompact, fmtQty, fmtPct, fmtDays,
    PERIOD_PRESETS, periodRange,
} from "../services/utils";

/**
 * Tableau de bord Achats & Fournisseurs — 6 onglets.
 *
 * Une source de vérité pour les dettes : ``get_open_invoices`` alimente le
 * tableau des factures ET (côté client) la balance âgée et l'échéancier —
 * cohérence garantie. Règles OWL de production : aucun global JS dans les
 * templates, formatage par méthodes, props optionnelles jamais null,
 * t-key partout.
 */
export class PurchaseDashboardView extends Component {
    static template = "aite_purchase_dashboard.DashboardView";
    static components = { KpiCard };
    static props = {};

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.notification = useService("notification");

        const initial = periodRange("month");
        this.state = useState({
            loading: true,
            tab: "dashboard",
            period: "month",
            dateFrom: initial.date_from,
            dateTo: initial.date_to,
            supplierId: 0,
            suppliers: [],
            meta: { currency_symbol: "F", cfg: {}, is_manager: false },
            kpis: { cfg: {} },
            invoices: [],
            supplierRows: [],
            flux: [],
            claims: { deposits: [], avoirs: [] },
            orders: [],
            prices: [],
            priceIndex: { labels: [], series: [] },
            showCfg: false,
            cfgSaving: false,
            cfgGlobal: {},
        });

        this.supRef = useRef("supChart");
        this.fluxRef = useRef("fluxChart");
        this.agingRef = useRef("agingChart");
        this.topProdRef = useRef("topProdChart");
        this.agingDRef = useRef("agingDChart");
        this.echRef = useRef("echChart");
        this.prixRef = useRef("prixChart");
        this._charts = {};

        onWillStart(async () => {
            await loadChart();
            const M = "aite.purchase.dashboard";
            const [meta, suppliers] = await Promise.all([
                this.orm.call(M, "get_meta", []),
                this.orm.call(M, "get_suppliers", []),
            ]);
            this.state.meta = meta;
            this.state.suppliers = suppliers;
            await this.loadAll();
        });
        onMounted(() => this.renderTabCharts());
        onWillUnmount(() => this.destroyAllCharts());
    }

    // ------------------------------------------------------------------
    // Chargement
    // ------------------------------------------------------------------

    async loadAll() {
        this.state.loading = true;
        const M = "aite.purchase.dashboard";
        const df = this.state.dateFrom;
        const dt = this.state.dateTo;
        const sup = this.state.supplierId || null;
        const [kpis, invoices, supplierRows, flux, claims, orders,
               prices, priceIndex] = await Promise.all([
            this.orm.call(M, "get_kpis", [df, dt, sup]),
            this.orm.call(M, "get_open_invoices", [sup]),
            this.orm.call(M, "get_supplier_rows", [df, dt]),
            this.orm.call(M, "get_flux_months", [6, sup]),
            this.orm.call(M, "get_claims", [sup]),
            this.orm.call(M, "get_orders_journal", [df, dt, sup, 60]),
            this.orm.call(M, "get_price_moves", [sup, 8]),
            this.orm.call(M, "get_price_index", [6, sup]),
        ]);
        this.state.kpis = kpis;
        this.state.invoices = invoices;
        this.state.supplierRows = supplierRows;
        this.state.flux = flux;
        this.state.claims = claims;
        this.state.orders = orders;
        this.state.prices = prices;
        this.state.priceIndex = priceIndex;
        this.state.loading = false;
    }

    async refresh() {
        await this.loadAll();
        this.renderTabCharts();
    }

    setTab(tab) {
        this.state.tab = tab;
        this.renderTabCharts();
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

    async setSupplier(supId) {
        this.state.supplierId = supId;
        await this.refresh();
    }

    // ------------------------------------------------------------------
    // Dérivations client
    // ------------------------------------------------------------------

    get tabs() {
        return [
            { key: "dashboard", label: "Tableau de bord" },
            { key: "suppliers", label: "Fournisseurs" },
            { key: "debts", label: "Dettes & échéancier" },
            { key: "claims", label: "Avoirs & consignes" },
            { key: "orders", label: "Commandes & réceptions" },
            { key: "prices", label: "Prix & variations" },
        ];
    }

    get periodPresets() {
        return PERIOD_PRESETS;
    }

    /** Balance âgée : sommes par tranche de retard (depuis les factures). */
    agingData() {
        const b = [0, 0, 0, 0, 0];
        for (const inv of this.state.invoices) {
            b[inv.bucket] += inv.residual;
        }
        return b;
    }

    /** Échéancier : reste dû groupé par semaine d'échéance (6 semaines). */
    scheduleWeeks() {
        const weeks = [0, 0, 0, 0, 0, 0];
        for (const inv of this.state.invoices) {
            const w = inv.days_late > 0 ? 0
                : ((inv.days_to_due / 7) | 0) > 5 ? 5
                : (inv.days_to_due / 7) | 0;
            weeks[w] += inv.residual;
        }
        return weeks;
    }

    supColor(partnerId) {
        for (const s of this.state.suppliers) {
            if (s.id === partnerId) {
                return s.color;
            }
        }
        return "#888780";
    }

    // ------------------------------------------------------------------
    // Formatage (exposé au template)
    // ------------------------------------------------------------------

    money(v) {
        return fmtMoney(v, this.state.meta.currency_symbol);
    }

    negMoney(v) {
        return "−" + fmtMoney(v, this.state.meta.currency_symbol);
    }

    qty(v) {
        return fmtQty(v);
    }

    pct(v) {
        return fmtPct(v);
    }

    signedPct(v) {
        const n = v || 0;
        return (n > 0 ? "+" : "") + fmtPct(n);
    }

    days(v) {
        return fmtDays(v);
    }

    num(v) {
        return "" + (v === undefined || v === null ? 0 : v);
    }

    badge(cls) {
        return BADGE_CLS[cls] || BADGE_CLS.gray;
    }

    dotStyle(partnerId) {
        return "background:" + this.supColor(partnerId);
    }

    lateText(inv) {
        if (inv.days_late > 0) {
            return inv.days_late + " j";
        }
        if (inv.days_to_due > 0) {
            return "dans " + inv.days_to_due + " j";
        }
        return "auj.";
    }

    fullMark(o) {
        if (o.is_full === null || o.is_full === undefined) {
            return "—";
        }
        return o.is_full ? "✓" : "✗";
    }

    orDash(v) {
        return v ? v : "—";
    }

    moneyOrDash(v) {
        return v ? this.money(v) : "—";
    }

    impactText(p) {
        const n = p.impact || 0;
        if (n > 0) {
            return "−" + this.money(n);
        }
        if (n < 0) {
            return "+" + this.money(-n);
        }
        return "—";
    }

    impactClass(p) {
        return (p.impact || 0) > 0 ? "text-danger" : "text-success";
    }

    valueClass(v) {
        return (v || 0) > 0 ? "text-danger" : "";
    }

    depSub() {
        const k = this.state.kpis;
        const over = (k.top_sup_part || 0) >= (k.cfg.dep || 40);
        return this.pct(k.top_sup_part) + " des achats" +
            (over ? " · seuil de dépendance dépassé" : "");
    }

    // ------------------------------------------------------------------
    // Graphiques (rendus par onglet)
    // ------------------------------------------------------------------

    destroyAllCharts() {
        Object.values(this._charts).forEach(destroyChart);
        this._charts = {};
    }

    _destroy(ids) {
        for (const id of ids) {
            if (this._charts[id]) {
                destroyChart(this._charts[id]);
                delete this._charts[id];
            }
        }
    }

    renderTabCharts() {
        if (this.state.loading) {
            return;
        }
        requestAnimationFrame(() => {
            const tab = this.state.tab;
            if (tab === "dashboard") {
                this._destroy(["sup", "flux", "aging", "topprod"]);
                this._renderSup();
                this._renderFlux();
                this._renderAging(this.agingRef.el, "aging");
                this._renderTopProd();
            } else if (tab === "debts") {
                this._destroy(["agingd", "ech"]);
                this._renderAging(this.agingDRef.el, "agingd");
                this._renderEch();
            } else if (tab === "prices") {
                this._destroy(["prix"]);
                this._renderPrix();
            }
        });
    }

    _mk(key, el, cfg) {
        if (!el || typeof window.Chart === "undefined") {
            return;
        }
        this._charts[key] = new window.Chart(el, cfg);
    }

    _moneyTicks() {
        return {
            ticks: { callback: (v) => fmtCompact(v), font: { size: 9 } },
        };
    }

    _renderSup() {
        const rows = this.state.supplierRows.filter((s) => s.achats > 0);
        this._mk("sup", this.supRef.el, {
            type: "doughnut",
            data: {
                labels: rows.map((s) => s.name),
                datasets: [{
                    data: rows.map((s) => s.achats),
                    backgroundColor: rows.map((s) => s.color),
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

    _renderFlux() {
        const rows = this.state.flux;
        this._mk("flux", this.fluxRef.el, {
            type: "bar",
            data: {
                labels: rows.map((r) => r.period),
                datasets: [
                    {
                        label: "Factures fournisseurs",
                        data: rows.map((r) => r.bills),
                        backgroundColor: COLORS.primary,
                        borderRadius: 3,
                    },
                    {
                        label: "Paiements",
                        data: rows.map((r) => r.payments),
                        backgroundColor: COLORS.success,
                        borderRadius: 3,
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
    }

    _renderAging(el, key) {
        this._mk(key, el, {
            type: "bar",
            data: {
                labels: ["Non échu", "1–30 j", "31–60 j", "61–90 j", "+90 j"],
                datasets: [{
                    data: this.agingData(),
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
    }

    _renderTopProd() {
        const rows = this.state.kpis.top_products || [];
        this._mk("topprod", this.topProdRef.el, {
            type: "bar",
            data: {
                labels: rows.map((r) => r.name),
                datasets: [{
                    data: rows.map((r) => r.value),
                    backgroundColor: COLORS.primary,
                    borderRadius: 3,
                }],
            },
            options: {
                indexAxis: "y",
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: this._moneyTicks(),
                    y: { ticks: { font: { size: 10 } } },
                },
            },
        });
    }

    _renderEch() {
        this._mk("ech", this.echRef.el, {
            type: "bar",
            data: {
                labels: ["Échu / S0", "S1", "S2", "S3", "S4", "S5+"],
                datasets: [{
                    label: "À décaisser",
                    data: this.scheduleWeeks(),
                    backgroundColor: COLORS.info,
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
    }

    _renderPrix() {
        const idx = this.state.priceIndex;
        this._mk("prix", this.prixRef.el, {
            type: "line",
            data: {
                labels: idx.labels || [],
                datasets: (idx.series || []).map((s) => ({
                    label: s.name,
                    data: s.values,
                    borderColor: s.color,
                    backgroundColor: s.color + "22",
                    tension: 0.3,
                    fill: false,
                    pointRadius: 2,
                })),
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: "bottom", labels: { font: { size: 10 } } },
                },
                scales: {
                    y: { ticks: { font: { size: 9 } } },
                    x: { ticks: { font: { size: 10 } } },
                },
            },
        });
    }

    // ------------------------------------------------------------------
    // Configuration (modal)
    // ------------------------------------------------------------------

    openCfg() {
        this.state.cfgGlobal = { ...(this.state.meta.cfg || {}) };
        this.state.showCfg = true;
    }

    closeCfg() {
        this.state.showCfg = false;
    }

    async saveCfg() {
        this.state.cfgSaving = true;
        const g = this.state.cfgGlobal;
        const cfg = {
            soon: this._int(g.soon, 7),
            late: this._int(g.late, 0),
            dep: this._float(g.dep, 40),
            price: this._float(g.price, 5),
        };
        try {
            await this.orm.call(
                "aite.purchase.dashboard", "save_alert_config", [cfg]);
            this.notification.add("Configuration des alertes enregistrée.", {
                type: "success",
            });
            this.state.showCfg = false;
            const meta = await this.orm.call(
                "aite.purchase.dashboard", "get_meta", []);
            this.state.meta = meta;
            await this.refresh();
        } finally {
            this.state.cfgSaving = false;
        }
    }

    _int(v, dflt) {
        const n = parseInt(v, 10);
        return isNaN(n) ? dflt : n;
    }

    _float(v, dflt) {
        const n = parseFloat(("" + v).replace(",", "."));
        return isNaN(n) ? dflt : n;
    }

    // ------------------------------------------------------------------
    // Navigation
    // ------------------------------------------------------------------

    openPartner(partnerId) {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "res.partner",
            res_id: partnerId,
            views: [[false, "form"]],
            target: "current",
        });
    }

    openMove(moveId) {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "account.move",
            res_id: moveId,
            views: [[false, "form"]],
            target: "current",
        });
    }

    openOrder(orderId) {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "purchase.order",
            res_id: orderId,
            views: [[false, "form"]],
            target: "current",
        });
    }

    openDeposits() {
        this.action.doAction(
            "aite_purchase_dashboard.action_aite_purchase_deposit");
    }
}
