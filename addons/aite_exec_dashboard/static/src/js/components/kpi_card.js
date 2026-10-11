/** @odoo-module **/

import { Component } from "@odoo/owl";
import { fmtDelta } from "../services/utils";

/**
 * Carte indicateur. ``hint`` est la phrase d'explication (infobulle au
 * survol et petit « ? ») ; ``delta`` l'écart N-1 en %, coloré.
 */
export class KpiCard extends Component {
    static template = "aite_exec_dashboard.KpiCard";
    static props = {
        label: { type: String },
        value: { type: String },
        sub: { type: String, optional: true },
        accent: { type: String, optional: true },
        mega: { type: Boolean, optional: true },
        hint: { type: String, optional: true },
        delta: { type: [Number, { value: null }], optional: true },
        deltaLabel: { type: String, optional: true },
    };
    static defaultProps = {
        sub: "", accent: "primary", mega: false, hint: "", delta: null,
        deltaLabel: "vs N-1",
    };

    get hasDelta() {
        return this.props.delta !== null && this.props.delta !== undefined;
    }

    get deltaText() {
        return fmtDelta(this.props.delta) + " " + this.props.deltaLabel;
    }

    get deltaCls() {
        return (this.props.delta || 0) >= 0 ? "aed-up" : "aed-down";
    }
}
