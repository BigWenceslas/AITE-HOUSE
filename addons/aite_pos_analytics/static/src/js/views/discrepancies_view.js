/** @odoo-module **/

import { Component, useState, onWillStart, onWillUpdateProps } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { KpiCard } from "../components/kpi_card";
import { fmt, fmtMoney, fmtDate, COLORS } from "../services/utils";

const SEV_LABEL = {
    none: "OK", over: "Excédent",
    low: "Modéré", med: "Élevé", high: "Critique",
};
const SEV_BADGE = {
    over: "b-blu", low: "b-amb", med: "b-amb", high: "b-red",
};

/**
 * Vue Écarts de caisse — purement visualisation.
 *
 * Affiche KPIs (total négatif, nb sessions concernées, écart moyen,
 * plus grand écart) et liste détaillée des sessions concernées.
 * Sur la base du diagnostic LAVERANDAH (tous les comptés à 0),
 * inclut un bandeau d'alerte si une majorité de clôtures sont à zéro.
 */
export class DiscrepanciesView extends Component {
    static template = "aite_pos_analytics.DiscrepanciesView";
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
            data: null,
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
            this.state.data = await this.orm.call(
                "aite.pos.dashboard", "get_cash_discrepancies",
                [props.dateFrom, props.dateTo, props.configId || null],
            );
        } finally {
            this.state.loading = false;
        }
    }

    severityLabel(s) { return SEV_LABEL[s] || s; }
    severityBadge(s) { return SEV_BADGE[s] || "b-blu"; }

    get fmt() { return fmt; }
    get fmtMoney() { return fmtMoney; }
    get fmtDate() { return fmtDate; }
    get COLORS() { return COLORS; }
}
