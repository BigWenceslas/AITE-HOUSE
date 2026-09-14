/** @odoo-module **/

import { Component, useState, useRef, onWillStart, onMounted,
         onWillUnmount, onWillUpdateProps, onPatched } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { loadChart, destroyChart } from "../services/chartjs_loader";
import { fmt, fmtMoney, fmtPct, fmtSigned, COLORS } from "../services/utils";

/**
 * Vue "Par caisse" — comparatif multi-points-de-vente.
 *
 * Répond à la demande : sur une période donnée, déterminer la marge
 * totale ET la marge par caisse, plus CA, CMV, taux, panier moyen,
 * nb commandes et écart de caisse par point de vente.
 *
 * Affiche :
 *   - 4 KPIs de tête (caisse n°1, plus rentable, meilleur panier, écart total)
 *   - un tableau comparatif complet (une ligne par caisse + total)
 *   - 2 graphiques : part du CA (camembert) et taux de marge (barres)
 */
export class CaisseView extends Component {
    static template = "aite_pos_analytics.CaisseView";
    static props = {
        dateFrom: String,
        dateTo: String,
        configId: { type: [Number, { value: null }], optional: true },
        filters: { type: Object, optional: true },
    };

    setup() {
        this.orm = useService("orm");
        this.state = useState({
            loading: true,
            caisses: [],
            total: null,
        });
        this.chartShareRef = useRef("chartShare");
        this.chartRateRef = useRef("chartRate");
        this.charts = {};

        onWillStart(async () => {
            await loadChart();
            await this.fetchData();
        });
        onMounted(() => this.renderCharts());
        onWillUnmount(() => this.cleanupCharts());

        onWillUpdateProps(async (next) => {
            const changed =
                next.dateFrom !== this.props.dateFrom
                || next.dateTo !== this.props.dateTo
                || next.configId !== this.props.configId
                || JSON.stringify(next.filters || {})
                   !== JSON.stringify(this.props.filters || {});
            if (changed) {
                this.needsRender = true;
                await this.fetchData(next);
            }
        });
        onPatched(() => {
            if (this.needsRender && !this.state.loading) {
                this.needsRender = false;
                this.renderCharts();
            }
        });
    }

    async fetchData(p) {
        const props = p || this.props;
        this.state.loading = true;
        try {
            const data = await this.orm.call(
                "aite.pos.dashboard", "get_caisse_breakdown",
                [props.dateFrom, props.dateTo, props.configId || null,
                 props.filters || {}],
            );
            this.state.caisses = data.caisses || [];
            this.state.total = data.total || null;
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
        if (!Chart || !this.state.caisses.length) return;

        // Part du CA (camembert)
        if (this.chartShareRef.el) {
            this.charts.share = new Chart(this.chartShareRef.el, {
                type: "pie",
                data: {
                    labels: this.state.caisses.map(c => c.name),
                    datasets: [{
                        data: this.state.caisses.map(c => c.ca),
                        backgroundColor: this.state.caisses.map(c => c.color),
                        borderWidth: 2, borderColor: "#fff",
                    }],
                },
                options: {
                    responsive: true, maintainAspectRatio: false,
                    plugins: {
                        legend: { position: "right",
                                  labels: { font: { size: 10 }, boxWidth: 12 } },
                    },
                },
            });
        }

        // Taux de marge par caisse (barres)
        if (this.chartRateRef.el) {
            this.charts.rate = new Chart(this.chartRateRef.el, {
                type: "bar",
                data: {
                    labels: this.state.caisses.map(c => c.name),
                    datasets: [{
                        label: "Taux de marge %",
                        data: this.state.caisses.map(c => +c.margin_rate.toFixed(1)),
                        backgroundColor: this.state.caisses.map(c => c.color),
                        borderRadius: 3,
                    }],
                },
                options: {
                    responsive: true, maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        x: { ticks: { font: { size: 10 } } },
                        y: { ticks: { font: { size: 9 }, color: "#888780",
                                      callback: v => v + "%" } },
                    },
                },
            });
        }
    }

    // ---- KPIs dérivés ----
    get mostProfitable() {
        if (!this.state.caisses.length) return null;
        return [...this.state.caisses].sort(
            (a, b) => b.margin_rate - a.margin_rate)[0];
    }
    get bestBasket() {
        if (!this.state.caisses.length) return null;
        return [...this.state.caisses].sort(
            (a, b) => b.average_basket - a.average_basket)[0];
    }
    get topContributor() {
        if (!this.state.caisses.length) return null;
        return [...this.state.caisses].sort((a, b) => b.ca - a.ca)[0];
    }

    marginBadgeClass(rate) {
        if (rate >= 50) return "b-teal";
        if (rate >= 40) return "b-amb";
        return "b-red";
    }

    get fmt() { return fmt; }
    get fmtMoney() { return fmtMoney; }
    get fmtPct() { return fmtPct; }
    get fmtSigned() { return fmtSigned; }
    get COLORS() { return COLORS; }
}
