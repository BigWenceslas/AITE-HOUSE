/** @odoo-module **/

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { SlotDashboardView } from "./views/slot_dashboard_view";

export class SlotDashboard extends Component {
    static template = "aite_slot_booking.Dashboard";
    static components = { SlotDashboardView };
    static props = ["*"];
}

registry.category("actions").add("aite_slot_dashboard", SlotDashboard);
