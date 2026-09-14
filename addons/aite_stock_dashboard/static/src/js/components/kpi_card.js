/** @odoo-module **/

import { Component } from "@odoo/owl";

/**
 * Carte KPI réutilisable (pattern éprouvé sur les modules AITE).
 *
 * Props :
 *  - label  : intitulé (string)
 *  - value  : valeur déjà formatée (string)
 *  - sub    : sous-texte optionnel (string)
 *  - delta  : {text, cls} optionnel — le parent décide de la sémantique de
 *             couleur ; passer ``undefined`` (jamais ``null``) pour omettre
 *  - accent : 'primary' | 'success' | 'danger' | 'warning' | 'info'
 *  - mega   : style accentué (bordure gauche)
 */
export class KpiCard extends Component {
    static template = "aite_stock_dashboard.KpiCard";
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
        if (!d) {
            return "";
        }
        return d.cls || "";
    }
}
