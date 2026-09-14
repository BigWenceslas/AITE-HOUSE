/** @odoo-module **/

import { Component, useState, useRef, onWillStart, onMounted, onWillUnmount, onWillUpdateProps, onPatched } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { loadChart, destroyChart } from "../services/chartjs_loader";
import { fmt, fmtMoney, fmtPct, COLORS, getCategoryColors } from "../services/utils";

export class CategoriesView extends Component {
    static template = "aite_pos_analytics.CategoriesView";
    static props = {
        dateFrom: String,
        dateTo: String,
        configId: { type: [Number, { value: null }], optional: true },
        onSelectCategory: { type: Function, optional: true },
    };

    setup() {
        this.orm = useService("orm");
        this.state = useState({
            loading: true,
            categories: [],
            evolution: { labels: [], series: [] },
        });
        this.chartRef = useRef("chartCat");
        this.chartEvoRef = useRef("chartCatEvo");
        this.chart = null;
        this.chartEvo = null;
        onWillStart(async () => {
            await loadChart();
            await this.fetchData();
        });
        onMounted(() => this.renderChart());
        onWillUnmount(() => {
            destroyChart(this.chart);
            destroyChart(this.chartEvo);
        });
        onWillUpdateProps(async (next) => {
            if (next.dateFrom !== this.props.dateFrom
                || next.dateTo !== this.props.dateTo
                || next.configId !== this.props.configId) {
                this.needsChartRender = true;
                await this.fetchData(next);
            }
        });
        onPatched(() => {
            if (this.needsChartRender && !this.state.loading && this.state.categories.length) {
                this.needsChartRender = false;
                this.renderChart();
            }
        });
    }

    async fetchData(p) {
        const props = p || this.props;
        this.state.loading = true;
        try {
            const [categories, evolution] = await Promise.all([
                this.orm.call(
                    "aite.pos.dashboard", "get_category_breakdown",
                    [props.dateFrom, props.dateTo, props.configId || null]),
                this.orm.call(
                    "aite.pos.dashboard", "get_category_evolution",
                    [6, props.configId || null, 5]),
            ]);
            this.state.categories = categories;
            this.state.evolution = evolution;
        } finally {
            this.state.loading = false;
        }
    }

    renderChart() {
        this.renderEvoChart();
        if (!window.Chart || !this.chartRef.el || !this.state.categories.length) return;
        destroyChart(this.chart);
        const cats = this.state.categories;
        const labels = cats.map(c => c.name);
        this.chart = new window.Chart(this.chartRef.el, {
            type: "bar",
            data: {
                labels,
                datasets: [
                    { label: "CA", data: cats.map(c => c.ca),
                      backgroundColor: cats.map((c, i) => getCategoryColors(c.name, i).col),
                      borderRadius: 4 },
                    { label: "CMV", data: cats.map(c => c.cost),
                      backgroundColor: cats.map((c, i) => getCategoryColors(c.name, i).col + "55"),
                      borderRadius: 4 },
                    { label: "Marge", data: cats.map(c => c.margin),
                      backgroundColor: cats.map((c, i) => getCategoryColors(c.name, i).col + "99"),
                      borderRadius: 4 },
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

    renderEvoChart() {
        const evo = this.state.evolution;
        if (!window.Chart || !this.chartEvoRef.el || !evo.series.length) return;
        destroyChart(this.chartEvo);
        this.chartEvo = new window.Chart(this.chartEvoRef.el, {
            type: "line",
            data: {
                labels: evo.labels,
                datasets: evo.series.map((sr, i) => {
                    const col = sr.name === "Autres"
                        ? "#888780"
                        : getCategoryColors(sr.name, i).col;
                    return {
                        label: sr.name,
                        data: sr.values,
                        borderColor: col,
                        backgroundColor: col + "22",
                        tension: 0.3,
                        pointRadius: 2,
                        fill: false,
                    };
                }),
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                plugins: { legend: { position: "bottom", labels: { font: { size: 10 } } } },
                scales: {
                    y: { ticks: {
                        font: { size: 9 },
                        callback: v => v >= 1000 ? Math.round(v / 1000) + "k" : v,
                    } },
                    x: { ticks: { font: { size: 10 } } },
                },
            },
        });
    }

    /** Drill-down : ouvre la vue Articles filtrée sur cette catégorie. */
    selectCategory(cat) {
        if (this.props.onSelectCategory) {
            this.props.onSelectCategory(cat.name);
        }
    }

    get hasDrill() {
        return !!this.props.onSelectCategory;
    }

    get totalCA() {
        return this.state.categories.reduce((s, c) => s + (c.ca || 0), 0);
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
