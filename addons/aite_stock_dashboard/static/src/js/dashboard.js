/** @odoo-module **/

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { StockDashboardView } from "./views/stock_dashboard_view";

/**
 * Racine du tableau de bord Stock & Inventaire, branchée sur l'action
 * cliente ``aite_stock_dashboard`` (le tag DOIT correspondre à l'action
 * XML — leçon du module Crédit).
 */
export class StockDashboard extends Component {
    static template = "aite_stock_dashboard.Dashboard";
    static components = { StockDashboardView };
    static props = ["*"];
}

registry.category("actions").add("aite_stock_dashboard", StockDashboard);
