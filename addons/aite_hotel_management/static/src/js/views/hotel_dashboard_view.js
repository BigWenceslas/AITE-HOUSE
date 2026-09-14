/** @odoo-module **/

import { Component, useState, useRef, onWillStart, onMounted, onPatched, onWillUnmount } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { loadChart, destroyChart } from "../services/chartjs_loader";
import { KpiCard } from "../components/kpi_card";
import {
    COLORS, ROOM_STATUS_COLORS, ROOM_STATUS_LABELS, ROOM_STATUS_ORDER,
    fmtMoney, fmtCompact, fmtPct, periodRange, PERIOD_PRESETS,
} from "../services/hotel_utils";

/**
 * Tableau de bord Front Desk — vue d'ensemble opérationnelle de l'hôtel.
 *
 * Photo du jour (occupation, arrivées, départs, clients présents),
 * indicateurs de performance de la période (Occupation / ADR / RevPAR / CA
 * avec variation vs période N-1), room board interactif, mouvements du
 * jour et résumé gouvernante.
 *
 * Règle d'or apprise sur le terrain : AUCUNE fonction globale JS (String,
 * Math…) dans le template OWL — tout calcul/formatage passe par des
 * méthodes du composant.
 */
export class HotelDashboardView extends Component {
    static template = "aite_hotel_management.DashboardView";
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
            hotelId: 0,
            hotels: [],
            currencySymbol: "F",
            companyName: "",
            kpis: { today: {}, period: {}, deltas: {} },
            board: [],
            movements: { arrivals: [], departures: [] },
            hk: {},
        });

        this.occRef = useRef("occChart");
        this.revRef = useRef("revChart");
        this._charts = {};

        onWillStart(async () => {
            await loadChart();
            const M = "aite.hotel.dashboard";
            const [meta, hotels] = await Promise.all([
                this.orm.call(M, "get_dashboard_meta", []),
                this.orm.call(M, "get_hotels", []),
            ]);
            this.state.currencySymbol = meta.currency_symbol || "F";
            this.state.companyName = meta.company_name || "";
            this.state.hotels = hotels;
            await this.loadAll();
        });
        onMounted(() => this.renderCharts());
        // Après un refresh, le DOM (canvas) n'est re-rendu qu'au patch
        // suivant : c'est ici que les refs sont garanties valides.
        onPatched(() => this.renderCharts());
        onWillUnmount(() => this.destroyCharts());
    }

    // ------------------------------------------------------------------
    // Data
    // ------------------------------------------------------------------

    async loadAll() {
        this.state.loading = true;
        const df = this.state.dateFrom;
        const dt = this.state.dateTo;
        const hotel = this.state.hotelId || null;
        const M = "aite.hotel.dashboard";
        const [kpis, board, movements, occEvo, revType, hk] =
            await Promise.all([
                this.orm.call(M, "get_kpis", [df, dt, hotel]),
                this.orm.call(M, "get_room_board", [hotel]),
                this.orm.call(M, "get_today_movements", [hotel]),
                this.orm.call(M, "get_occupancy_evolution", [df, dt, hotel]),
                this.orm.call(M, "get_revenue_by_type", [df, dt, hotel]),
                this.orm.call(M, "get_housekeeping_summary", [hotel]),
            ]);
        this.state.kpis = kpis;
        this.state.board = board;
        this.state.movements = movements;
        this.occEvolution = occEvo;
        this.revByType = revType;
        this.state.hk = hk;
        this.state.loading = false;
    }

    async refresh() {
        await this.loadAll();
        // Le rendu des graphiques est déclenché par onPatched, une fois
        // les <canvas> effectivement re-rendus dans le DOM.
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

    async setHotel(hotelId) {
        this.state.hotelId = hotelId;
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

    /** "12 / 20" — chambres occupées sur total vendable. */
    occFraction() {
        const t = this.state.kpis.today || {};
        return this.num(t.occupied) + " / " + this.num(t.total_rooms);
    }

    /** Extrait l'heure locale HH:MM d'un datetime serveur (UTC). */
    hour(dtStr) {
        if (!dtStr) {
            return "";
        }
        const d = new Date(dtStr.replace(" ", "T") + "Z");
        if (isNaN(d.getTime())) {
            return dtStr.slice(11, 16);
        }
        const hh = String(d.getHours()).padStart(2, "0");
        const mm = String(d.getMinutes()).padStart(2, "0");
        return hh + ":" + mm;
    }

    /**
     * Variation formatée pour un KPI.
     * :param pct: variation en % (peut être null → pas de delta affiché)
     * :param goodWhenUp: true si une hausse est positive (vert)
     * :returns: {text, cls} ou undefined
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

    get periodPresets() {
        return PERIOD_PRESETS;
    }

    get statusLegend() {
        return ROOM_STATUS_ORDER.map((key) => ({
            key,
            label: ROOM_STATUS_LABELS[key],
            color: ROOM_STATUS_COLORS[key],
        }));
    }

    /** Room board regroupé par hôtel puis étage, prêt pour le template. */
    get boardGroups() {
        const groups = [];
        const index = {};
        for (const room of this.state.board) {
            const label = this.state.hotels.length > 1
                ? room.hotel + (room.floor ? " · " + room.floor : "")
                : (room.floor || "Chambres");
            if (!(label in index)) {
                index[label] = groups.length;
                groups.push({ label, rooms: [] });
            }
            groups[index[label]].rooms.push(room);
        }
        return groups;
    }

    roomTitle(room) {
        const status = ROOM_STATUS_LABELS[room.status] || room.status;
        let title = room.name + " — " + status;
        if (room.guest) {
            title += " · " + room.guest;
        }
        if (room.until) {
            title += " (jusqu'au " + room.until + ")";
        }
        return title;
    }

    /** Solde dû mis en évidence sur les départs. */
    residualBadge(row) {
        return (row.residual || 0) > 0.005
            ? this.money(row.residual) : "";
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
        this._renderOccupancy();
        this._renderRevenue();
    }

    _mk(el, cfg) {
        if (!el || typeof window.Chart === "undefined") {
            return null;
        }
        return new window.Chart(el, cfg);
    }

    _renderOccupancy() {
        const data = this.occEvolution || { labels: [], values: [] };
        const chart = this._mk(this.occRef.el, {
            type: "line",
            data: {
                labels: data.labels,
                datasets: [{
                    label: "Occupation",
                    data: data.values,
                    borderColor: COLORS.primary,
                    backgroundColor: COLORS.primary + "22",
                    tension: 0.3,
                    fill: true,
                    pointRadius: 2,
                }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: (ctx) => fmtPct(ctx.parsed.y),
                        },
                    },
                },
                scales: {
                    y: {
                        min: 0,
                        max: 100,
                        ticks: {
                            callback: (v) => v + " %",
                            font: { size: 9 },
                        },
                    },
                    x: { ticks: { font: { size: 9 }, maxRotation: 60 } },
                },
            },
        });
        if (chart) {
            this._charts.occ = chart;
        }
    }

    _renderRevenue() {
        const data = this.revByType || { labels: [], values: [] };
        const palette = [
            COLORS.primary, COLORS.success, COLORS.info,
            COLORS.warning, COLORS.teal, COLORS.danger, COLORS.muted,
        ];
        const chart = this._mk(this.revRef.el, {
            type: "doughnut",
            data: {
                labels: data.labels,
                datasets: [{
                    data: data.values,
                    backgroundColor: data.labels.map(
                        (_l, i) => palette[i % palette.length]),
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
                    tooltip: {
                        callbacks: {
                            label: (ctx) => " " + ctx.label + " : " +
                                fmtCompact(ctx.parsed),
                        },
                    },
                },
            },
        });
        if (chart) {
            this._charts.rev = chart;
        }
    }

    // ------------------------------------------------------------------
    // Actions
    // ------------------------------------------------------------------

    openReservation(resId) {
        if (!resId) {
            return;
        }
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "aite.hotel.reservation",
            res_id: resId,
            views: [[false, "form"]],
            target: "current",
        });
    }

    /** Clic sur une chambre : réservation en cours sinon fiche chambre. */
    openRoom(room) {
        if (room.reservation_id) {
            this.openReservation(room.reservation_id);
            return;
        }
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "aite.hotel.room",
            res_id: room.id,
            views: [[false, "form"]],
            target: "current",
        });
    }

    openBookingWizard() {
        this.action.doAction(
            "aite_hotel_management.action_hotel_booking_wizard");
    }

    openArrivals() {
        this.action.doAction(
            "aite_hotel_management.action_hotel_arrivals_today");
    }

    openDepartures() {
        this.action.doAction(
            "aite_hotel_management.action_hotel_departures_today");
    }

    openHousekeeping() {
        this.action.doAction(
            "aite_hotel_management.action_hotel_housekeeping");
    }
}
