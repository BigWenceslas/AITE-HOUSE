/** @odoo-module **/

import { Component, useState, useRef, onWillStart, onMounted, onWillUnmount, onWillUpdateProps, onPatched } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { KpiCard } from "../components/kpi_card";
import { loadChart, destroyChart } from "../services/chartjs_loader";
import { fmt, fmtMoney, fmtPct, COLORS } from "../services/utils";

const PIE_COLORS = [
    "#3B6D11", "#185FA5", "#714B67", "#854F0B", "#0F6E56", "#A32D2D", "#888780",
];

export class PaymentsView extends Component {
    static template = "aite_pos_analytics.PaymentsView";
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
            payments: [],
        });
        this.chartRef = useRef("chartPay");
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
            if (this.needsChartRender && !this.state.loading && this.state.payments.length) {
                this.needsChartRender = false;
                this.renderChart();
            }
        });
    }

    async fetchData(p) {
        const props = p || this.props;
        this.state.loading = true;
        try {
            this.state.payments = await this.orm.call(
                "aite.pos.dashboard", "get_payment_breakdown",
                [props.dateFrom, props.dateTo, props.configId || null],
            );
        } finally {
            this.state.loading = false;
        }
    }

    renderChart() {
        if (!window.Chart || !this.chartRef.el || !this.state.payments.length) return;
        destroyChart(this.chart);
        this.chart = new window.Chart(this.chartRef.el, {
            type: "doughnut",
            data: {
                labels: this.state.payments.map(p => p.method_name),
                datasets: [{
                    data: this.state.payments.map(p => p.amount),
                    backgroundColor: this.state.payments.map((_, i) => PIE_COLORS[i % PIE_COLORS.length]),
                    borderWidth: 2,
                    borderColor: "#fff",
                }],
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                plugins: {
                    legend: { position: "right", labels: { font: { size: 11 } } },
                },
            },
        });
    }

    get totalAmount() {
        return this.state.payments.reduce((s, p) => s + (p.amount || 0), 0);
    }
    get totalCount() {
        return this.state.payments.reduce((s, p) => s + (p.count || 0), 0);
    }

    get fmt() { return fmt; }
    get fmtMoney() { return fmtMoney; }
    get fmtPct() { return fmtPct; }
    get COLORS() { return COLORS; }
}
