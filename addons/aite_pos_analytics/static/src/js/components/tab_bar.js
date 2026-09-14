/** @odoo-module **/

import { Component } from "@odoo/owl";
import { TABS } from "../services/utils";

/**
 * Barre d'onglets de navigation entre les 8 vues du dashboard.
 */
export class TabBar extends Component {
    static template = "aite_pos_analytics.TabBar";
    static props = {
        currentTab: String,
        onSelect: Function,
    };

    get tabs() {
        return TABS;
    }

    select(key) {
        if (key !== this.props.currentTab) this.props.onSelect(key);
    }
}
