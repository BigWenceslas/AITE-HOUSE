/** @odoo-module **/

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { PurchaseDashboardView } from "./views/purchase_dashboard_view";

/**
 * Racine du tableau de bord Achats & Fournisseurs — le tag DOIT
 * correspondre à l'action cliente XML (leçon de production).
 */
export class PurchaseDashboard extends Component {
    static template = "aite_purchase_dashboard.Dashboard";
    static components = { PurchaseDashboardView };
    static props = ["*"];
}

registry.category("actions").add("aite_purchase_dashboard", PurchaseDashboard);
