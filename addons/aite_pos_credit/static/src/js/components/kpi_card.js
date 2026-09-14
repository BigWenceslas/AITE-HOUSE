/** @odoo-module **/

import { Component } from "@odoo/owl";

/**
 * Carte KPI réutilisable du tableau de bord recouvrement.
 *
 * Props :
 *  - label   : intitulé (string)
 *  - value   : valeur déjà formatée (string)
 *  - sub     : sous-texte optionnel (string)
 *  - delta   : objet {text, cls} pour la variation (optionnel) ; ``cls``
 *              porte la sémantique métier (une hausse de dette est rouge,
 *              une hausse de recouvrement est verte)
 *  - accent  : 'primary' | 'success' | 'danger' | 'warning'
 *  - mega    : booléen pour le style accentué
 */
export class KpiCard extends Component {
    static template = "aite_pos_credit.KpiCard";
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
