/** @odoo-module **/

import { Component, useState, useRef, onWillStart, onMounted, onWillUnmount } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { loadChart, destroyChart } from "../services/chartjs_loader";
import { KpiCard } from "../components/kpi_card";
import {
    COLORS, CATEG_PALETTE, BADGE_CLS,
    fmtMoney, fmtCompact, fmtQty, fmtPct, fmtDays,
    PERIOD_PRESETS, periodRange,
} from "../services/utils";

/**
 * Tableau de bord Stock & Inventaire — 6 onglets.
 *
 * Un seul appel ``get_stock_list`` alimente Alertes, Stock complet,
 * Rotation et quatre graphiques (dérivés côté client) : cohérence garantie
 * et moins d'aller-retours serveur. Les flux liés à la période (entrées/
 * sorties, écarts, coulage, mouvements) viennent de RPC dédiés.
 *
 * Règles OWL appliquées (leçons de production) : aucun global JS dans les
 * templates, tout formatage via méthodes ; props optionnelles jamais null ;
 * t-key sur chaque t-foreach.
 */
export class StockDashboardView extends Component {
    static template = "aite_stock_dashboard.DashboardView";
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
            locationId: 0,
            categId: 0,
            search: "",
            locations: [],
            categories: [],
            meta: { currency_symbol: "F", cfg: {}, is_manager: false },
            kpis: {},
            rows: [],
            flux: [],
            coulage: { rows: [], seuil: 2 },
            gaps: [],
            moves: { rows: [], totals: {} },
            // Modal de configuration des alertes
            showCfg: false,
            cfgSaving: false,
            cfgGlobal: {},
            cfgRows: [],
        });

        this.catRef = useRef("catChart");
        this.fluxRef = useRef("fluxChart");
        this.couvRef = useRef("couvChart");
        this.topValRef = useRef("topValChart");
        this.rotRef = useRef("rotChart");
        this.dormRef = useRef("dormChart");
        this.ecartRef = useRef("ecartChart");
        this.coulRef = useRef("coulChart");
        this._charts = {};

        onWillStart(async () => {
            await loadChart();
            const M = "aite.stock.dashboard";
            const [meta, locations, categories] = await Promise.all([
                this.orm.call(M, "get_meta", []),
                this.orm.call(M, "get_locations", []),
                this.orm.call(M, "get_categories", []),
            ]);
            this.state.meta = meta;
            this.state.locations = locations;
            this.state.categories = categories;
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
        const M = "aite.stock.dashboard";
        const df = this.state.dateFrom;
        const dt = this.state.dateTo;
        const loc = this.state.locationId || null;
        const cat = this.state.categId || null;
        const [kpis, rows, flux, coulage, gaps, moves] = await Promise.all([
            this.orm.call(M, "get_kpis", [df, dt, loc, cat]),
            this.orm.call(M, "get_stock_list", [loc, cat]),
            this.orm.call(M, "get_flux_months", [6, cat]),
            this.orm.call(M, "get_coulage_series", [6, cat]),
            this.orm.call(M, "get_inventory_gaps", [df, dt, loc, cat]),
            this.orm.call(M, "get_moves_journal", [df, dt, 80, loc, cat]),
        ]);
        this.state.kpis = kpis;
        this.state.rows = rows;
        this.state.flux = flux;
        this.state.coulage = coulage;
        this.state.gaps = gaps;
        this.state.moves = moves;
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

    async setLocation(locId) {
        this.state.locationId = locId;
        await this.refresh();
    }

    async setCateg(categId) {
        this.state.categId = categId;
        await this.refresh();
    }

    onSearch(ev) {
        this.state.search = ev.target.value || "";
    }

    // ------------------------------------------------------------------
    // Dérivations client (une source : state.rows)
    // ------------------------------------------------------------------

    get tabs() {
        return [
            { key: "dashboard", label: "Tableau de bord" },
            { key: "alerts", label: "Alertes & réappro" },
            { key: "stocklist", label: "Stock complet" },
            { key: "rotation", label: "Rotation & dormants" },
            { key: "inventory", label: "Inventaires & écarts" },
            { key: "moves", label: "Mouvements" },
        ];
    }

    get periodPresets() {
        return PERIOD_PRESETS;
    }

    get alertRows() {
        return [...this.state.rows].sort(
            (a, b) => a.urgency - b.urgency || a.couv - b.couv);
    }

    get rotationRows() {
        return [...this.state.rows].sort((a, b) => b.rot - a.rot);
    }

    get stockRows() {
        const q = (this.state.search || "").toLowerCase();
        if (!q) {
            return this.state.rows;
        }
        return this.state.rows.filter(
            (r) => (r.name || "").toLowerCase().includes(q));
    }

    get stockTotals() {
        const rows = this.stockRows;
        let units = 0;
        let value = 0;
        let valueSale = 0;
        for (const r of rows) {
            units += r.stock;
            value += r.value;
            valueSale += r.value_sale || 0;
        }
        return { count: rows.length, units, value, valueSale };
    }

    get maxRowValue() {
        let max = 0;
        for (const r of this.state.rows) {
            if (r.value > max) {
                max = r.value;
            }
        }
        return max || 1;
    }

    get dormantRows() {
        return this.state.rows
            .filter((r) => r.classe === "Dormant")
            .sort((a, b) => b.value - a.value);
    }

    _byCategValue() {
        const agg = {};
        for (const r of this.state.rows) {
            const k = r.categ || "Sans catégorie";
            agg[k] = (agg[k] || 0) + r.value;
        }
        return Object.keys(agg)
            .map((k) => ({ name: k, value: agg[k] }))
            .sort((a, b) => b.value - a.value);
    }

    _coverageByCateg() {
        const agg = {};
        for (const r of this.state.rows) {
            const k = r.categ || "Sans catégorie";
            agg[k] = agg[k] || { stock: 0, vday: 0 };
            agg[k].stock += r.stock;
            agg[k].vday += r.vday;
        }
        return Object.keys(agg)
            .map((k) => ({
                name: k,
                couv: agg[k].vday > 0 ? agg[k].stock / agg[k].vday : 0,
            }))
            .sort((a, b) => b.couv - a.couv);
    }

    _gapsByCateg() {
        const byId = {};
        for (const r of this.state.rows) {
            byId[r.id] = r.categ || "Sans catégorie";
        }
        const agg = {};
        for (const g of this.state.gaps) {
            const k = byId[g.product_id] || "Autres";
            agg[k] = (agg[k] || 0) + g.value;
        }
        return Object.keys(agg)
            .map((k) => ({ name: k, value: agg[k] }))
            .sort((a, b) => a.value - b.value);
    }

    // ------------------------------------------------------------------
    // Formatage (exposé au template — jamais de globals JS en XML)
    // ------------------------------------------------------------------

    money(v) {
        return fmtMoney(v, this.state.meta.currency_symbol);
    }

    signedMoney(v) {
        const n = v || 0;
        return (n > 0 ? "+" : "") + this.money(n);
    }

    qty(v) {
        return fmtQty(v);
    }

    signedQty(v) {
        const n = v || 0;
        return (n > 0 ? "+" : "") + fmtQty(n);
    }

    pct(v) {
        return fmtPct(v);
    }

    days(v) {
        return fmtDays(v);
    }

    num(v) {
        return "" + (v === undefined || v === null ? 0 : v);
    }

    rotX(v) {
        const n = v || 0;
        const r = ((n * 10 + 0.5) | 0) / 10;
        return ("" + r).replace(".", ",") + "×";
    }

    badge(cls) {
        return BADGE_CLS[cls] || BADGE_CLS.gray;
    }

    barStyle(value, max) {
        const width = max ? (value / max) * 100 : 0;
        return "width:" + width + "%";
    }

    locQty(row, loc) {
        const m = row.by_location || {};
        let v = m[loc.id];
        if (v === undefined) {
            v = m["" + loc.id];
        }
        return fmtQty(v || 0);
    }

    coulAccent() {
        const k = this.state.kpis;
        return (k.coul_pct || 0) > (k.coul_seuil || 2) ? "danger" : "success";
    }

    coulSub() {
        const k = this.state.kpis;
        return this.pct(k.coul_pct) + " du CA estimé · seuil " +
            this.pct(k.coul_seuil);
    }

    /** Marge potentielle immobilisée (vente − coût), KPIs globaux. */
    marginSub() {
        const k = this.state.kpis;
        return "marge potentielle +" + this.money(k.margin_value) +
            " (" + this.pct(k.margin_pct) + " du PV)";
    }

    /** Marge potentielle sur les lignes filtrées (onglet Stock complet). */
    listMarginSub() {
        const t = this.stockTotals;
        const margin = t.valueSale - t.value;
        const pctv = t.valueSale > 0 ? margin / t.valueSale * 100 : 0;
        return "marge potentielle +" + this.money(margin) +
            " (" + this.pct(pctv) + ")";
    }

    /** Couverture ↔ rotation : deux faces du même indicateur. */
    rotSub() {
        return "rotation moyenne " + this.rotX(this.state.kpis.rot_moy) +
            " / mois";
    }

    valueClass(v) {
        return (v || 0) < 0 ? "text-danger" : "text-success";
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
                this._destroy(["cat", "flux", "couv", "topval"]);
                this._renderCat();
                this._renderFlux();
                this._renderCouv();
                this._renderTopVal();
            } else if (tab === "rotation") {
                this._destroy(["rot", "dorm"]);
                this._renderRot();
                this._renderDorm();
            } else if (tab === "inventory") {
                this._destroy(["ecart", "coul"]);
                this._renderEcart();
                this._renderCoul();
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

    _renderCat() {
        const rows = this._byCategValue();
        this._mk("cat", this.catRef.el, {
            type: "doughnut",
            data: {
                labels: rows.map((r) => r.name),
                datasets: [{
                    data: rows.map((r) => r.value),
                    backgroundColor: rows.map(
                        (_r, i) => CATEG_PALETTE[i % CATEG_PALETTE.length]),
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
                        label: "Entrées (réceptions)",
                        data: rows.map((r) => r.in_value),
                        backgroundColor: COLORS.success,
                        borderRadius: 3,
                    },
                    {
                        label: "Sorties (ventes)",
                        data: rows.map((r) => r.out_value),
                        backgroundColor: COLORS.primary,
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

    _renderCouv() {
        const data = this._coverageByCateg();
        const crit = this.state.meta.cfg.crit || 3;
        const dorm = this.state.meta.cfg.dorm || 60;
        const colorOf = (c) => {
            if (c < crit) {
                return COLORS.danger;
            }
            if (c >= dorm) {
                return "#5e1b1b";
            }
            if (c > 21) {
                return COLORS.warning;
            }
            return COLORS.success;
        };
        this._mk("couv", this.couvRef.el, {
            type: "bar",
            data: {
                labels: data.map((r) => r.name),
                datasets: [{
                    label: "Couverture (j)",
                    data: data.map((r) => r.couv),
                    backgroundColor: data.map((r) => colorOf(r.couv)),
                    borderRadius: 3,
                }],
            },
            options: {
                indexAxis: "y",
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: {
                        ticks: {
                            font: { size: 9 },
                            callback: (v) => v + " j",
                        },
                    },
                    y: { ticks: { font: { size: 10 } } },
                },
            },
        });
    }

    _renderTopVal() {
        const rows = [...this.state.rows]
            .sort((a, b) => b.value - a.value)
            .slice(0, 8);
        this._mk("topval", this.topValRef.el, {
            type: "bar",
            data: {
                labels: rows.map((r) => r.name),
                datasets: [{
                    label: "Valeur immobilisée",
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

    _renderRot() {
        const rows = [...this.state.rows]
            .filter((r) => r.rot > 0)
            .sort((a, b) => b.rot - a.rot)
            .slice(0, 8);
        this._mk("rot", this.rotRef.el, {
            type: "bar",
            data: {
                labels: rows.map((r) => r.name),
                datasets: [{
                    label: "Rotation (× / mois)",
                    data: rows.map((r) => r.rot),
                    backgroundColor: COLORS.teal,
                    borderRadius: 3,
                }],
            },
            options: {
                indexAxis: "y",
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { ticks: { font: { size: 9 } } },
                    y: { ticks: { font: { size: 10 } } },
                },
            },
        });
    }

    _renderDorm() {
        const rows = this.dormantRows.slice(0, 8);
        this._mk("dorm", this.dormRef.el, {
            type: "bar",
            data: {
                labels: rows.map((r) => r.name),
                datasets: [{
                    label: "Valeur dormante",
                    data: rows.map((r) => r.value),
                    backgroundColor: COLORS.danger,
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

    _renderEcart() {
        const rows = this._gapsByCateg();
        this._mk("ecart", this.ecartRef.el, {
            type: "bar",
            data: {
                labels: rows.map((r) => r.name),
                datasets: [{
                    label: "Écart valorisé",
                    data: rows.map((r) => r.value),
                    backgroundColor: rows.map(
                        (r) => (r.value < 0 ? COLORS.danger : COLORS.success)),
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

    _renderCoul() {
        const serie = this.state.coulage;
        const rows = serie.rows || [];
        this._mk("coul", this.coulRef.el, {
            type: "line",
            data: {
                labels: rows.map((r) => r.period),
                datasets: [
                    {
                        label: "Coulage (% CA estimé)",
                        data: rows.map((r) => r.pct),
                        borderColor: COLORS.warning,
                        backgroundColor: COLORS.warning + "22",
                        tension: 0.3,
                        fill: true,
                    },
                    {
                        label: "Seuil",
                        data: rows.map(() => serie.seuil),
                        borderColor: COLORS.danger,
                        borderDash: [6, 4],
                        pointRadius: 0,
                        fill: false,
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
                    y: {
                        ticks: {
                            font: { size: 9 },
                            callback: (v) => v + " %",
                        },
                        suggestedMax: (serie.seuil || 2) + 1,
                    },
                    x: { ticks: { font: { size: 10 } } },
                },
            },
        });
    }

    // ------------------------------------------------------------------
    // Configuration des alertes (modal)
    // ------------------------------------------------------------------

    async openCfg() {
        const M = "aite.stock.dashboard";
        const data = await this.orm.call(M, "get_alert_products", [null, null]);
        this.state.cfgGlobal = { ...data.cfg };
        this.state.cfgRows = data.rows.map((r) => ({ ...r }));
        this.state.showCfg = true;
    }

    closeCfg() {
        this.state.showCfg = false;
    }

    async saveCfg() {
        this.state.cfgSaving = true;
        const g = this.state.cfgGlobal;
        const globalCfg = {
            sec: this._int(g.sec, 0),
            hor: this._int(g.hor, 7),
            crit: this._int(g.crit, 3),
            dorm: this._int(g.dorm, 60),
            lead_default: this._int(g.lead_default, 3),
            coul_seuil: this._float(g.coul_seuil, 2.0),
        };
        const rows = this.state.cfgRows.map((r) => ({
            tmpl_id: r.tmpl_id,
            lead_raw: this._int(r.lead_raw, 0),
            manual_threshold: this._float(r.manual_threshold, 0),
            alert_active: !!r.alert_active,
        }));
        try {
            await this.orm.call(
                "aite.stock.dashboard", "save_alert_config",
                [globalCfg, rows]);
            this.notification.add("Configuration des alertes enregistrée.", {
                type: "success",
            });
            this.state.showCfg = false;
            const meta = await this.orm.call(
                "aite.stock.dashboard", "get_meta", []);
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
    // Actions
    // ------------------------------------------------------------------

    openProduct(productId) {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "product.product",
            res_id: productId,
            views: [[false, "form"]],
            target: "current",
        });
    }
}
