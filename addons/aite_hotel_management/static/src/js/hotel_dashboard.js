/** @odoo-module **/

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { HotelDashboardView } from "./views/hotel_dashboard_view";

/**
 * Conteneur racine du tableau de bord Front Desk, branché sur l'action
 * cliente ``aite_hotel_dashboard``.
 */
export class HotelDashboard extends Component {
    static template = "aite_hotel_management.Dashboard";
    static components = { HotelDashboardView };
    static props = ["*"];
}

registry.category("actions").add("aite_hotel_dashboard", HotelDashboard);
