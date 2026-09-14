/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

import { FilterBar } from "./components/filter_bar";
import { TabBar } from "./components/tab_bar";
import { ProductPanel } from "./components/product_panel";

import { DashboardView } from "./views/dashboard_view";
import { CaisseView } from "./views/caisse_view";
import { SessionsView } from "./views/sessions_view";
import { ProductsView } from "./views/products_view";
import { MarginsView } from "./views/margins_view";
import { CategoriesView } from "./views/categories_view";
import { DiscrepanciesView } from "./views/discrepancies_view";
import { PaymentsView } from "./views/payments_view";
import { ConfigView } from "./views/config_view";

/**
 * Action client AITE POS Analytics — composant racine.
 *
 * Architecture :
 *   ┌─────────────────────────────────────────┐
 *   │ TabBar (8 onglets)                      │
 *   ├──────────────────────────────┬──────────┤
 *   │ FilterBar (période, POS)     │          │
 *   ├──────────────────────────────┤ Product  │
 *   │                              │ Panel    │
 *   │   <currentView />            │ (slide   │
 *   │                              │  over,   │
 *   │                              │  modal)  │
 *   └──────────────────────────────┴──────────┘
 *
 * État central : période, POS sélectionné, onglet actif, produit affiché
 * dans le slide-over. Les vues filles reçoivent les props correspondantes
 * et se rechargent automatiquement via ``onWillUpdateProps``.
 *
 * Au démarrage, ``get_dashboard_meta`` détermine les bornes de période
 * réelles (date de première / dernière session) pour pré-remplir les
 * filtres.
 */
export class PosAnalyticsDashboard extends Component {
    static template = "aite_pos_analytics.Dashboard";
    static components = {
        FilterBar, TabBar, ProductPanel,
        DashboardView, CaisseView, SessionsView, ProductsView, MarginsView,
        CategoriesView, DiscrepanciesView, PaymentsView, ConfigView,
    };
    static props = { "*": true };  // accepte les props injectés par l'action

    setup() {
        this.orm = useService("orm");

        // L'action peut transmettre un onglet par défaut via params.
        const params = (this.props.action && this.props.action.params) || {};

        this.state = useState({
            tab: params.default_view || "dashboard",
            // Période par défaut : on remplit après le get_dashboard_meta
            periodKey: "all",
            dateFrom: null,
            dateTo: null,
            configId: null,
            minDate: null,
            maxDate: null,
            // Filtres temporels (heure / jour de semaine)
            hourKey: "all",
            hourFrom: null,
            hourTo: null,
            weekdayKey: "all",
            weekdays: [],
            // Slide-over
            panelProductId: null,
            productsCategory: null,
            // Métadonnées
            meta: null,
        });

        onWillStart(() => this.loadMeta());
    }

    async loadMeta() {
        const meta = await this.orm.call(
            "aite.pos.dashboard", "get_dashboard_meta", [],
        );
        this.state.meta = meta;

        /**
         * Conversion défensive d'une valeur datetime Odoo vers string ISO
         * (YYYY-MM-DD). Odoo 18 peut retourner :
         *   - string "2025-10-01 08:00:00"  → on slice
         *   - luxon DateTime                → .toFormat('yyyy-MM-dd')
         *   - JS Date                       → .toISOString().slice
         *   - false / null                  → null (session sans date)
         */
        const toISO = (val) => {
            if (!val) return null;
            if (typeof val === "string") return val.slice(0, 10);
            if (typeof val.toFormat === "function") return val.toFormat("yyyy-MM-dd");
            if (typeof val.toISOString === "function") return val.toISOString().slice(0, 10);
            return String(val).slice(0, 10);
        };

        const today = new Date().toISOString().slice(0, 10);

        // Filtrer start_at != false pour exclure les sessions en cours
        // d'ouverture qui n'ont pas encore de date de démarrage.
        const domain = [["start_at", "!=", false]];
        const [first, last] = await Promise.all([
            this.orm.searchRead("pos.session", domain, ["start_at"],
                                { order: "start_at asc",  limit: 1 }),
            this.orm.searchRead("pos.session", domain, ["start_at"],
                                { order: "start_at desc", limit: 1 }),
        ]);

        const minDate = first.length ? toISO(first[0].start_at) : "2025-01-01";
        const maxDate = last.length  ? toISO(last[0].start_at)  : today;

        this.state.minDate  = minDate  || "2025-01-01";
        this.state.maxDate  = maxDate  || today;
        this.state.dateFrom = this.state.minDate;
        this.state.dateTo   = this.state.maxDate;
    }

    onTabChange(tab) {
        this.state.tab = tab;
        // Fermer le panneau si on quitte une vue produit
        this.state.panelProductId = null;
        // Un clic manuel sur un onglet réinitialise le drill catégorie
        // (le drill Catégories → Articles passe par onSelectCategory,
        // qui contourne ce handler et conserve donc sa sélection).
        this.state.productsCategory = null;
    }

    onFilterChange(payload) {
        const {
            key, from, to, configId,
            hourKey, hourFrom, hourTo, weekdayKey, weekdays,
        } = payload;
        this.state.periodKey = key;
        this.state.dateFrom = from;
        this.state.dateTo = to;
        this.state.configId = configId;
        if (hourKey !== undefined) this.state.hourKey = hourKey;
        if (hourFrom !== undefined) this.state.hourFrom = hourFrom;
        if (hourTo !== undefined) this.state.hourTo = hourTo;
        if (weekdayKey !== undefined) this.state.weekdayKey = weekdayKey;
        if (weekdays !== undefined) this.state.weekdays = weekdays;
    }

    onSelectProduct(productId) {
        this.state.panelProductId = productId;
    }

    /**
     * Drill-down Catégories → Articles : mémorise la catégorie choisie
     * et bascule sur l'onglet Articles, pré-filtré dessus.
     */
    onSelectCategory(categName) {
        this.state.productsCategory = categName || null;
        this.state.tab = "products";
        this.state.panelProductId = null;
    }

    closePanel() {
        this.state.panelProductId = null;
    }

    /**
     * Dict de filtres temporels transmis aux méthodes backend qui le
     * supportent (get_kpis, get_caisse_breakdown, heatmap…). Construit à
     * partir de l'état central ; ``null`` quand aucun filtre n'est actif.
     */
    get filters() {
        const f = {};
        if (this.state.hourFrom != null && this.state.hourTo != null) {
            f.hour_from = this.state.hourFrom;
            f.hour_to = this.state.hourTo;
        }
        if (this.state.weekdays && this.state.weekdays.length) {
            f.weekdays = this.state.weekdays;
        }
        return f;
    }

    get viewProps() {
        return {
            dateFrom: this.state.dateFrom,
            dateTo: this.state.dateTo,
            configId: this.state.configId,
            filters: this.filters,
        };
    }
}

registry.category("actions").add(
    "aite_pos_analytics.dashboard", PosAnalyticsDashboard,
);
