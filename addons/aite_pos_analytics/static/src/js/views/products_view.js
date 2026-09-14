/** @odoo-module **/

import { Component, useState, onWillStart, onWillUpdateProps } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { KpiCard } from "../components/kpi_card";
import { fmt, fmtMoney, fmtPct, COLORS, getCategoryColors } from "../services/utils";

export class ProductsView extends Component {
    static template = "aite_pos_analytics.ProductsView";
    static components = { KpiCard };
    static props = {
        dateFrom: String,
        dateTo: String,
        configId: { type: [Number, { value: null }], optional: true },
        onSelectProduct: Function,
        initialCategory: { type: [String, { value: null }], optional: true },
    };

    setup() {
        this.orm = useService("orm");
        this.state = useState({
            loading: true,
            products: [],
            search: "",
            categFilter: this.props.initialCategory || null,
            sortBy: "ca",
            sortDir: "desc",
        });
        onWillStart(() => this.fetchData());
        onWillUpdateProps((next) => {
            if (next.initialCategory !== this.props.initialCategory) {
                this.state.categFilter = next.initialCategory || null;
            }
            if (next.dateFrom !== this.props.dateFrom
                || next.dateTo !== this.props.dateTo
                || next.configId !== this.props.configId) {
                this.fetchData(next);
            }
        });
    }

    async fetchData(p) {
        const props = p || this.props;
        this.state.loading = true;
        try {
            this.state.products = await this.orm.call(
                "aite.pos.dashboard", "get_products_full",
                [props.dateFrom, props.dateTo, props.configId || null],
            );
        } finally {
            this.state.loading = false;
        }
    }

    get filteredProducts() {
        const q = (this.state.search || "").toLowerCase().trim();
        let list = this.state.products;
        if (this.state.categFilter) {
            list = list.filter(p => p.category === this.state.categFilter);
        }
        if (q) {
            list = list.filter(p =>
                (p.name || "").toLowerCase().includes(q)
                || (p.category || "").toLowerCase().includes(q),
            );
        }
        const dir = this.state.sortDir === "asc" ? 1 : -1;
        const key = this.state.sortBy;
        return [...list].sort((a, b) => {
            const va = a[key], vb = b[key];
            if (typeof va === "string") return va.localeCompare(vb) * dir;
            return ((va || 0) - (vb || 0)) * dir;
        });
    }

    setSort(key) {
        if (this.state.sortBy === key) {
            this.state.sortDir = this.state.sortDir === "asc" ? "desc" : "asc";
        } else {
            this.state.sortBy = key;
            this.state.sortDir = "desc";
        }
    }

    /** Catégories distinctes présentes dans les ventes (pour les chips). */
    get categoriesList() {
        const seen = {};
        for (const p of this.state.products) {
            if (p.category) {
                seen[p.category] = true;
            }
        }
        return Object.keys(seen).sort((a, b) => a.localeCompare(b));
    }

    setCateg(name) {
        this.state.categFilter = name;
    }

    sortIndicator(key) {
        if (this.state.sortBy !== key) return "";
        return this.state.sortDir === "asc" ? " ▲" : " ▼";
    }

    onSearchInput(ev) { this.state.search = ev.target.value; }

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

    maxCA() {
        return Math.max(1, ...this.state.products.map(p => p.ca));
    }
}
