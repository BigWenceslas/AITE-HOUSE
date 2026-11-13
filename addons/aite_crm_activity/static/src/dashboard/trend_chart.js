import { Component, onWillStart, onWillUnmount, useEffect, useRef } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { loadBundle } from "@web/core/assets";
import { formatShortDay } from "./dashboard_utils";

/**
 * Graphique des tendances (12 semaines) : activités réalisées à temps et en
 * retard (barres empilées), activités créées (ligne), sur un seul axe (ce
 * sont trois nombres d'activités).
 *
 * Chart.js n'est chargé qu'au premier affichage du composant, c'est-à-dire
 * à l'ouverture de l'onglet « Tendances ». Le graphique est créé au
 * montage, mis à jour quand les données changent et détruit au démontage
 * (changement d'onglet, fermeture du tableau de bord).
 *
 * Les couleurs viennent de variables CSS définies dans
 * crm_activity_dashboard.scss à partir des couleurs d'Odoo : elles suivent
 * le thème (clair ou sombre).
 */
export class AiteTrendChart extends Component {
    static template = "aite_crm_activity.TrendChart";
    static props = { trend: Object };

    setup() {
        this.containerRef = useRef("container");
        this.canvasRef = useRef("canvas");
        this.chart = null;
        onWillStart(() => loadBundle("web.chartjs_lib"));
        useEffect(
            () => this.renderChart(),
            () => [this.props.trend]
        );
        onWillUnmount(() => this.destroyChart());
    }

    get ariaLabel() {
        const { done_on_time, done_late, created } = this.props.trend;
        const sum = (values) => values.reduce((total, value) => total + value, 0);
        return _t(
            "Sur 12 semaines : %(onTime)s activités réalisées à temps, %(late)s en retard, %(created)s créées.",
            { onTime: sum(done_on_time), late: sum(done_late), created: sum(created) }
        );
    }

    /** Couleur lue dans une variable CSS du tableau de bord. */
    cssColor(name) {
        const el = this.containerRef.el;
        return (el && getComputedStyle(el).getPropertyValue(name).trim()) || undefined;
    }

    get config() {
        const trend = this.props.trend;
        const colors = {
            onTime: this.cssColor("--o-aite-cad-chart-on-time"),
            late: this.cssColor("--o-aite-cad-chart-late"),
            created: this.cssColor("--o-aite-cad-chart-created"),
            text: this.cssColor("--o-aite-cad-chart-text"),
            grid: this.cssColor("--o-aite-cad-chart-grid"),
            surface: this.cssColor("--o-aite-cad-chart-surface"),
        };
        const late = [...trend.done_late];
        // Arrondi en haut de la barre seulement : sur le segment « en
        // retard », ou sur « à temps » quand il n'y a pas de retard.
        const topRadius = { topLeft: 4, topRight: 4, bottomLeft: 0, bottomRight: 0 };
        return {
            type: "bar",
            data: {
                labels: trend.weeks.map((week) => week.label),
                datasets: [
                    {
                        label: _t("Réalisées à temps"),
                        data: [...trend.done_on_time],
                        backgroundColor: colors.onTime,
                        borderColor: colors.surface,
                        borderWidth: { top: 2, right: 0, bottom: 0, left: 0 },
                        borderSkipped: false,
                        borderRadius: (ctx) => (late[ctx.dataIndex] ? 0 : topRadius),
                        maxBarThickness: 24,
                        stack: "done",
                        order: 2,
                    },
                    {
                        label: _t("Réalisées en retard"),
                        data: late,
                        backgroundColor: colors.late,
                        borderRadius: topRadius,
                        borderSkipped: false,
                        maxBarThickness: 24,
                        stack: "done",
                        order: 2,
                    },
                    {
                        type: "line",
                        label: _t("Créées"),
                        data: [...trend.created],
                        borderColor: colors.created,
                        backgroundColor: colors.created,
                        borderWidth: 2,
                        pointRadius: 4,
                        pointHoverRadius: 5,
                        pointBorderColor: colors.surface,
                        pointBorderWidth: 2,
                        tension: 0,
                        stack: "created",
                        order: 1,
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: { duration: 250 },
                interaction: { mode: "index", intersect: false },
                scales: {
                    x: {
                        stacked: true,
                        grid: { display: false },
                        // Sur téléphone, des semaines sautées plutôt que des
                        // libellés penchés.
                        ticks: { color: colors.text, maxRotation: 0, autoSkip: true },
                        border: { color: colors.grid },
                    },
                    y: {
                        stacked: true,
                        beginAtZero: true,
                        ticks: { precision: 0, color: colors.text },
                        grid: { color: colors.grid },
                        border: { display: false },
                    },
                },
                plugins: {
                    legend: {
                        position: "top",
                        align: "start",
                        labels: {
                            color: colors.text,
                            usePointStyle: true,
                            boxWidth: 8,
                            boxHeight: 8,
                            // Ordre des séries, pas leur ordre de dessin.
                            sort: (a, b) => a.datasetIndex - b.datasetIndex,
                        },
                    },
                    tooltip: {
                        callbacks: {
                            title: (items) => {
                                const week = trend.weeks[items[0]?.dataIndex];
                                return week
                                    ? _t("Semaine du %(from)s au %(to)s", {
                                          from: formatShortDay(week.date_from),
                                          to: formatShortDay(week.date_to),
                                      })
                                    : "";
                            },
                        },
                    },
                },
            },
        };
    }

    renderChart() {
        if (!this.canvasRef.el) {
            return;
        }
        const config = this.config;
        if (this.chart) {
            this.chart.data = config.data;
            this.chart.options = config.options;
            this.chart.update();
        } else {
            this.chart = new Chart(this.canvasRef.el, config);
        }
    }

    destroyChart() {
        if (this.chart) {
            this.chart.destroy();
            this.chart = null;
        }
    }
}
