/** @odoo-module **/

import { Component, useState, onWillUpdateProps } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { fmtMoney, fmtPct, fmtDate, getCategoryColors, COLORS } from "../services/utils";

/**
 * Panneau slide-over à droite affichant le détail d'un article.
 * Chargé asynchronement à l'ouverture via RPC.
 */
export class ProductPanel extends Component {
    static template = "aite_pos_analytics.ProductPanel";
    static props = {
        productId: { type: [Number, { value: null }] },
        dateFrom: String,
        dateTo: String,
        configId: { type: [Number, { value: null }], optional: true },
        onClose: Function,
    };

    setup() {
        this.orm = useService("orm");
        this.state = useState({
            loading: false,
            data: null,
        });
        // Recharger si productId change
        onWillUpdateProps((next) => {
            if (next.productId && next.productId !== this.props.productId) {
                this.loadDetail(next.productId, next.dateFrom, next.dateTo, next.configId);
            }
        });
        if (this.props.productId) {
            this.loadDetail(
                this.props.productId,
                this.props.dateFrom,
                this.props.dateTo,
                this.props.configId,
            );
        }
    }

    async loadDetail(productId, from, to, configId) {
        this.state.loading = true;
        try {
            const data = await this.orm.call(
                "aite.pos.dashboard",
                "get_product_detail",
                [productId, from, to, configId || null],
            );
            this.state.data = data;
        } finally {
            this.state.loading = false;
        }
    }

    // Helpers exposés au template
    get fmtMoney() { return fmtMoney; }
    get fmtPct() { return fmtPct; }
    get fmtDate() { return fmtDate; }
    get COLORS() { return COLORS; }

    getCatColors() {
        return getCategoryColors(this.state.data && this.state.data.category);
    }

    marginColor(rate) {
        if (rate >= 50) return COLORS.success;
        if (rate >= 30) return COLORS.warning;
        return COLORS.danger;
    }
}
