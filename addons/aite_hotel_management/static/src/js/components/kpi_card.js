/** @odoo-module **/

import { Component } from "@odoo/owl";

/**
 * Carte KPI réutilisable du tableau de bord Front Desk.
 *
 * Props :
 *  - label   : intitulé (string)
 *  - value   : valeur déjà formatée (string)
 *  - sub     : sous-texte optionnel (string)
 *  - delta   : objet {text, cls} pour la variation vs N-1 (optionnel) ;
 *              ``cls`` porte la sémantique métier
 *  - accent  : 'primary' | 'success' | 'danger' | 'warning' | 'info'
 *  - mega    : booléen pour le style accentué (bordure gauche colorée)
 */
export class KpiCard extends Component {
    static template = "aite_hotel_management.KpiCard";
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
        if (d.cls) {
            return d.cls;
        }
        return d.value >= 0 ? "text-success" : "text-danger";
    }
}
