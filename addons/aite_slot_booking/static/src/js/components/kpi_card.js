/** @odoo-module **/

import { Component } from "@odoo/owl";

/** Carte KPI AITE (props optionnelles : undefined, jamais null). */
export class KpiCard extends Component {
    static template = "aite_slot_booking.KpiCard";
    static props = {
        label: { type: String },
        value: { type: String },
        sub: { type: String, optional: true },
        accent: { type: String, optional: true },
        mega: { type: Boolean, optional: true },
    };
    static defaultProps = { sub: "", accent: "primary", mega: false };
}
