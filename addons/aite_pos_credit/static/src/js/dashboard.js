/** @odoo-module **/

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { CreditDashboardView } from "./views/dashboard_view";

/**
 * Conteneur racine du tableau de bord POS Crédit, branché sur l'action
 * cliente ``aite_pos_credit_dashboard``.
 */
export class CreditDashboard extends Component {
    static template = "aite_pos_credit.Dashboard";
    static components = { CreditDashboardView };
    static props = ["*"];
}

registry.category("actions").add("aite_pos_credit_dashboard", CreditDashboard);
