/** @odoo-module **/

import { Component } from "@odoo/owl";

/**
 * Ligne de classement utilisée dans les modules "Top bières / marges /
 * moins vendus" et autres rankings.
 *
 * Props :
 *   rank    : numéro (1, 2, 3...)
 *   name    : libellé
 *   pct     : largeur de la barre en % (0-100)
 *   value   : valeur à afficher à droite ("926 u", "55%")
 *   color   : couleur de la barre
 *   onClick : callback optionnel au clic (pour ouvrir le panel détail)
 */
export class RankRow extends Component {
    static template = "aite_pos_analytics.RankRow";
    static props = {
        rank: Number,
        name: String,
        pct: Number,
        value: String,
        color: { type: String, optional: true },
        onClick: { type: Function, optional: true },
    };
    static defaultProps = {
        color: "#714B67",
        onClick: null,
    };

    onClick() {
        if (this.props.onClick) this.props.onClick();
    }
}
