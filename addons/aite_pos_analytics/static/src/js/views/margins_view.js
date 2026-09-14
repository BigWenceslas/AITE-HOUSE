/** @odoo-module **/

import { Component, useState, useRef, onWillStart, onMounted, onWillUnmount, onWillUpdateProps, onPatched } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { KpiCard } from "../components/kpi_card";
import { loadChart, destroyChart } from "../services/chartjs_loader";
import { fmt, fmtMoney, fmtPct, COLORS, getCategoryColors } from "../services/utils";

/**
 * Vue Marges & CMV — focus rentabilité.
 *
 * Affiche les KPIs de rentabilité (taux marge, ratio CMV/CA, marge/tx)
 * et un waterfall implicite : CA → CMV → Marge avec analyse par
 * catégorie.
 */
export class MarginsView extends Component {
    static template = "aite_pos_analytics.MarginsView";
    static components = { KpiCard };
    static props = {
        dateFrom: String,
        dateTo: String,
        configId: { type: [Number, { value: null }], optional: true },
    };

    setup() {
        this.orm = useService("orm");
        this.state = useState({
            loading: true,
            kpis: null,
            categories: [],
            products: [],
        });
        this.chartRef = useRef("chartMargin");
        this.chart = null;
        onWillStart(async () => {
            await loadChart();
            await this.fetchData();
        });
        onMounted(() => this.renderChart());
        onWillUnmount(() => destroyChart(this.chart));
        onWillUpdateProps(async (next) => {
            if (next.dateFrom !== this.props.dateFrom
                || next.dateTo !== this.props.dateTo
                || next.configId !== this.props.configId) {
                this.needsChartRender = true;
                await this.fetchData(next);
            }
        });
        onPatched(() => {
            if (this.needsChartRender && !this.state.loading && this.state.kpis) {
                this.needsChartRender = false;
                this.renderChart();
            }
        });
    }

    async fetchData(p) {
        const props = p || this.props;
        this.state.loading = true;
        try {
            const [kpis, cats, prods] = await Promise.all([
                this.orm.call("aite.pos.dashboard", "get_kpis",
                              [props.dateFrom, props.dateTo, props.configId || null]),
                this.orm.call("aite.pos.dashboard", "get_category_breakdown",
                              [props.dateFrom, props.dateTo, props.configId || null]),
                this.orm.call("aite.pos.dashboard", "get_products_full",
                              [props.dateFrom, props.dateTo, props.configId || null]),
            ]);
            this.state.kpis = kpis;
            this.state.categories = cats;
            this.state.products = prods;
        } finally {
            this.state.loading = false;
        }
    }

    renderChart() {
        if (!window.Chart || !this.chartRef.el) return;
        destroyChart(this.chart);
        const labels = this.state.categories.map(c => c.name);
        this.chart = new window.Chart(this.chartRef.el, {
            type: "bar",
            data: {
                labels,
                datasets: [
                    { label: "CA", data: this.state.categories.map(c => c.ca),
                      backgroundColor: COLORS.info + "AA" },
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
                    y: { ticks: {
                        font: { size: 9 },
                        callback: v => v >= 1000 ? Math.round(v / 1000) + "k" : v,
                    } },
                },
            },
        });
    }

    topMarginProducts() {
        return [...this.state.products]
            .filter(p => p.ca > 100)
            .sort((a, b) => b.margin_rate - a.margin_rate)
            .slice(0, 10);
    }
    lowMarginProducts() {
        return [...this.state.products]
            .filter(p => p.ca > 100)
            .sort((a, b) => a.margin_rate - b.margin_rate)
            .slice(0, 10);
    }

    get fmt() { return fmt; }
    get fmtMoney() { return fmtMoney; }
    get fmtPct() { return fmtPct; }
    get COLORS() { return COLORS; }
    catColors(name, idx) { return getCategoryColors(name, idx); }

    marginBadgeClass(rate) {
        if (rate >= 50) return "b-teal";
        if (rate >= 30) return "b-amb";
        return "b-red";
    }
}
