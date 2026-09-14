/** @odoo-module **/

import { Component } from "@odoo/owl";

/**
 * Carte KPI principale.
 *
 * Props :
 *   label    : libellé court ("Chiffre d'affaires")
 *   value    : valeur principale (déjà formatée si nécessaire)
 *   subtitle : ligne secondaire (ex: "12 543 F / jour · 222j")
 *   color    : couleur de la bordure haute (hex)
 *   size     : "mega" | "secondary" (densité visuelle)
 */
export class KpiCard extends Component {
    static template = "aite_pos_analytics.KpiCard";
    static props = {
        label: String,
        value: { type: [String, Number] },
        subtitle: { type: String, optional: true },
        color: { type: String, optional: true },
        size: { type: String, optional: true },
    };
    static defaultProps = {
        subtitle: "",
        color: "#714B67",
        size: "mega",
    };
}
