/** @odoo-module **/

import { Component, useState, useRef, onMounted, onWillUnmount, onWillStart, onWillUpdateProps, onPatched } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { KpiCard } from "../components/kpi_card";
import { RankRow } from "../components/rank_row";
import { loadChart, destroyChart } from "../services/chartjs_loader";
import { fmt, fmtMoney, fmtPct, fmtDelta, deltaClass, fmtSigned, COLORS, getCategoryColors } from "../services/utils";

/**
 * Vue "Tableau de bord" — la vue principale et la plus dense.
 *
 * Compose : KPIs méga + KPIs secondaires, charts (Top 8, évolution),
 * blocs catégories, classements (top bières, marges, moins vendus),
 * table détaillée de tous les articles.
 *
 * Charge les données via une seule promesse parallèle (Promise.all)
 * pour réduire la latence perçue.
 */
export class DashboardView extends Component {
    static template = "aite_pos_analytics.DashboardView";
    static components = { KpiCard, RankRow };
    static props = {
        dateFrom: String,
        dateTo: String,
        configId: { type: [Number, { value: null }], optional: true },
        filters: { type: Object, optional: true },
        onSelectProduct: Function,
    };

    setup() {
        this.orm = useService("orm");
        this.state = useState({
            loading: true,
            kpis: null,
            topProducts: [],
            evolution: [],
            categories: [],
            rankings: { top_beers: [], best_margins: [], low_sellers: [] },
            products: [],
            caisses: [],
            caisseTotal: null,
            heatmap: null,
            insights: null,
        });
        this.chartTopRef = useRef("chartTop");
        this.chartLineRef = useRef("chartLine");
        this.chartCmvRef = useRef("chartCmv");
        this.chartCaisseRef = useRef("chartCaisse");
        this.charts = {};

        onWillStart(async () => {
            await loadChart();
            await this.fetchData();
        });

        onMounted(() => this.renderCharts());
        onWillUnmount(() => this.cleanupCharts());

        // Recharger les données lorsque période/PdV changent.
        // Note : on n'appelle PAS renderCharts ici car le DOM n'est pas
        // encore patché — les canvas refs pointent vers les anciens
        // éléments. On laisse onPatched s'en charger après le re-render.
        onWillUpdateProps(async (next) => {
            const propsChanged =
                next.dateFrom !== this.props.dateFrom
                || next.dateTo   !== this.props.dateTo
                || next.configId !== this.props.configId
                || JSON.stringify(next.filters || {})
                   !== JSON.stringify(this.props.filters || {});
            if (propsChanged) {
                this.needsChartRender = true;
                await this.fetchData(next);
            }
        });

        // Après chaque patch du DOM : si les données ont changé,
        // re-render les charts sur les nouveaux canvas.
        onPatched(() => {
            if (this.needsChartRender && !this.state.loading && this.state.kpis) {
                this.needsChartRender = false;
                this.renderCharts();
            }
        });
    }

    async fetchData(propsOverride) {
        this.state.loading = true;
        const p = propsOverride || this.props;
        const [from, to, cfg] = [p.dateFrom, p.dateTo, p.configId || null];
        const filters = p.filters || {};
        try {
            const [kpis, top, evo, cats, rks, prods, caisse, heat, insights] =
                await Promise.all([
                    this.orm.call("aite.pos.dashboard", "get_kpis", [from, to, cfg, filters]),
                    this.orm.call("aite.pos.dashboard", "get_top_products", [from, to, 8, cfg]),
                    this.orm.call("aite.pos.dashboard", "get_monthly_evolution", [from, to, cfg]),
                    this.orm.call("aite.pos.dashboard", "get_category_breakdown", [from, to, cfg]),
                    this.orm.call("aite.pos.dashboard", "get_rankings", [from, to, cfg]),
                    this.orm.call("aite.pos.dashboard", "get_products_full", [from, to, cfg]),
                    this.orm.call("aite.pos.dashboard", "get_caisse_breakdown", [from, to, cfg, filters]),
                    this.orm.call("aite.pos.dashboard", "get_hourly_heatmap", [from, to, cfg, filters]),
                    this.orm.call("aite.pos.dashboard", "get_time_insights", [from, to, cfg, filters]),
                ]);
            this.state.kpis = kpis;
            this.state.topProducts = top;
            this.state.evolution = evo;
            this.state.categories = cats;
            this.state.rankings = rks;
            this.state.products = prods;
            this.state.caisses = caisse.caisses || [];
            this.state.caisseTotal = caisse.total || null;
            this.state.heatmap = heat || null;
            this.state.insights = insights || null;
        } finally {
            this.state.loading = false;
        }
    }

    cleanupCharts() {
        Object.values(this.charts).forEach(destroyChart);
        this.charts = {};
    }

    renderCharts() {
        this.cleanupCharts();
        const Chart = window.Chart;
        if (!Chart) return;

        // Chart 1 : Top 8 articles — CA vs Marge
        if (this.chartTopRef.el && this.state.topProducts.length) {
            const labels = this.state.topProducts.map(p =>
                p.name.length > 10 ? p.name.slice(0, 9) + "…" : p.name);
            this.charts.top = new Chart(this.chartTopRef.el, {
                type: "bar",
                data: {
                    labels,
                    datasets: [
                        { label: "CA", data: this.state.topProducts.map(p => p.ca),
                          backgroundColor: COLORS.primary, borderRadius: 3 },
                        { label: "Marge", data: this.state.topProducts.map(p => p.margin),
                          backgroundColor: COLORS.success, borderRadius: 3 },
                    ],
                },
                options: {
                    responsive: true, maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        x: { ticks: { font: { size: 10 }, color: "#888780", maxRotation: 30 } },
                        y: { ticks: { font: { size: 9 }, color: "#888780",
                                      callback: v => v >= 1000 ? Math.round(v / 1000) + "k" : v } },
                    },
                },
            });
        }

        // Chart 2 : Évolution mensuelle CA / CMV / Marge
        if (this.chartLineRef.el && this.state.evolution.length) {
            const labels = this.state.evolution.map(e => e.period);
            this.charts.line = new Chart(this.chartLineRef.el, {
                type: "line",
                data: {
                    labels,
                    datasets: [
                        { label: "CA", data: this.state.evolution.map(e => e.ca),
                          borderColor: COLORS.primary, backgroundColor: COLORS.primary + "22",
                          tension: 0.3, fill: true },
                        { label: "CMV", data: this.state.evolution.map(e => e.cost),
                          borderColor: COLORS.danger, borderDash: [4, 4], tension: 0.3, fill: false },
                        { label: "Marge", data: this.state.evolution.map(e => e.margin),
                          borderColor: COLORS.success, borderDash: [4, 4], tension: 0.3, fill: false },
                    ],
                },
                options: {
                    responsive: true, maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        x: { ticks: { font: { size: 9 }, color: "#888780" } },
                        y: { ticks: { font: { size: 9 }, color: "#888780",
                                      callback: v => v >= 1000 ? Math.round(v / 1000) + "k" : v } },
                    },
                },
            });
        }

        // Chart 3 : CMV vs Marge par catégorie
        if (this.chartCmvRef.el && this.state.categories.length) {
            const labels = this.state.categories.map(c => c.name);
            this.charts.cmv = new Chart(this.chartCmvRef.el, {
                type: "bar",
                data: {
                    labels,
                    datasets: [
                        { label: "CMV", data: this.state.categories.map(c => c.cost),
                          backgroundColor: COLORS.danger + "AA" },
                        { label: "Marge", data: this.state.categories.map(c => c.margin),
                          backgroundColor: COLORS.success + "AA" },
                    ],
                },
                options: {
                    responsive: true, maintainAspectRatio: false,
                    plugins: { legend: { position: "bottom", labels: { font: { size: 10 } } } },
                    scales: {
                        x: { ticks: { font: { size: 10 } } },
                        y: { ticks: { font: { size: 9 }, color: "#888780",
                                      callback: v => v >= 1000 ? Math.round(v / 1000) + "k" : v } },
                    },
                },
            });
        }

        // Chart 4 : Contribution au CA par caisse (doughnut)
        if (this.chartCaisseRef.el && this.state.caisses.length) {
            this.charts.caisse = new Chart(this.chartCaisseRef.el, {
                type: "doughnut",
                data: {
                    labels: this.state.caisses.map(c => c.name),
                    datasets: [{
                        data: this.state.caisses.map(c => c.ca),
                        backgroundColor: this.state.caisses.map(c => c.color),
                        borderWidth: 2,
                        borderColor: "#fff",
                    }],
                },
                options: {
                    responsive: true, maintainAspectRatio: false,
                    cutout: "58%",
                    plugins: {
                        legend: {
                            position: "right",
                            labels: { font: { size: 10 }, boxWidth: 12 },
                        },
                    },
                },
            });
        }
    }

    // ----- Helpers de présentation -----

    get fmt() { return fmt; }
    get fmtMoney() { return fmtMoney; }
    get fmtPct() { return fmtPct; }
    get fmtDelta() { return fmtDelta; }
    get deltaClass() { return deltaClass; }
    get fmtSigned() { return fmtSigned; }
    get COLORS() { return COLORS; }

    /**
     * Couleur de fond d'une cellule de heatmap selon l'intensité du CA.
     * Dégradé du violet primaire ; opacité proportionnelle au max.
     */
    heatColor(value) {
        const max = (this.state.heatmap && this.state.heatmap.max) || 0;
        const a = max > 0 ? value / max : 0;
        return `rgba(113, 75, 103, ${(0.06 + a * 0.85).toFixed(3)})`;
    }
    heatTextColor(value) {
        const max = (this.state.heatmap && this.state.heatmap.max) || 0;
        const a = max > 0 ? value / max : 0;
        return a > 0.55 ? "#ffffff" : "#5f5e5a";
    }
    /** Abrège un montant pour l'affichage compact dans la heatmap. */
    heatLabel(value) {
        if (!value) return "";
        if (value >= 1000) return Math.round(value / 1000) + "k";
        return Math.round(value).toString();
    }

    catColors(name, idx) { return getCategoryColors(name, idx); }

    bestProduct() {
        if (!this.state.products.length) return null;
        return [...this.state.products].sort((a, b) => b.ca - a.ca)[0];
    }

    activeProducts() {
        return this.state.products.filter(p => p.qty > 0).length;
    }

    maxTopBeerQty() {
        return Math.max(1, ...this.state.rankings.top_beers.map(p => p.qty));
    }
    maxLowSellerQty() {
        return Math.max(1, ...this.state.rankings.low_sellers.map(p => p.qty));
    }
    maxProductCA() {
        return Math.max(1, ...this.state.products.map(p => p.ca));
    }

    marginBadgeClass(rate) {
        if (rate >= 50) return "b-teal";
        if (rate >= 30) return "b-amb";
        return "b-red";
    }

    onProductClick(productId) {
        this.props.onSelectProduct(productId);
    }
}
