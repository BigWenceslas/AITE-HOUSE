/** @odoo-module **/

import { Component, useState, onWillStart, onWillUpdateProps } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { KpiCard } from "../components/kpi_card";
import { fmt, fmtMoney, fmtPct, fmtDate, COLORS } from "../services/utils";

const SEVERITY_LABEL = {
    none: "OK", over: "Excédent",
    low: "Modéré", med: "Élevé", high: "Critique",
};
const SEVERITY_BADGE = {
    none: "b-teal", over: "b-blu",
    low: "b-amb", med: "b-amb", high: "b-red",
};
const STATE_LABEL = {
    opening_control: "Ouverture", opened: "En cours",
    closing_control: "Clôture", closed: "Clôturée",
};

export class SessionsView extends Component {
    static template = "aite_pos_analytics.SessionsView";
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
            sessions: [],
        });
        onWillStart(() => this.fetchData());
        onWillUpdateProps((next) => {
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
            this.state.sessions = await this.orm.call(
                "aite.pos.dashboard", "get_sessions",
                [props.dateFrom, props.dateTo, props.configId || null],
            );
        } finally {
            this.state.loading = false;
        }
    }

    // Stats agrégées calculées côté JS pour éviter un aller-retour
    get totalCA() {
        return this.state.sessions.reduce((s, x) => s + (x.total_ca || 0), 0);
    }
    get totalMargin() {
        return this.state.sessions.reduce((s, x) => s + (x.total_margin || 0), 0);
    }
    get totalOrders() {
        return this.state.sessions.reduce((s, x) => s + (x.order_count || 0), 0);
    }
    get avgBasket() {
        return this.totalOrders ? this.totalCA / this.totalOrders : 0;
    }

    severityLabel(s) { return SEVERITY_LABEL[s] || s; }
    severityBadge(s) { return SEVERITY_BADGE[s] || "b-blu"; }
    stateLabel(s) { return STATE_LABEL[s] || s; }

    get fmt() { return fmt; }
    get fmtMoney() { return fmtMoney; }
    get fmtPct() { return fmtPct; }
    get fmtDate() { return fmtDate; }
    get COLORS() { return COLORS; }
}
