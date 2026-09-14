/** @odoo-module **/

import { Component } from "@odoo/owl";

/**
 * Carte KPI réutilisable (pattern éprouvé AITE).
 * ``delta`` : {text, cls} optionnel — passer undefined, jamais null.
 */
export class KpiCard extends Component {
    static template = "aite_purchase_dashboard.KpiCard";
    static props = {
        label: { type: String },
        value: { type: String },
        sub: { type: String, optional: true },
        delta: { type: Object, optional: true },
        accent: { type: String, optional: true },
        mega: { type: Boolean, optional: true },
    };
    static defaultProps = {
        sub: "",
        accent: "primary",
        mega: false,
    };

    get deltaClass() {
        const d = this.props.delta;
        return d && d.cls ? d.cls : "";
    }
}
