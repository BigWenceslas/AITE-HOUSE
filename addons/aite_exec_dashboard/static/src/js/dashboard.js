/** @odoo-module **/

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { ExecDashboardView } from "./views/exec_dashboard_view";

export class ExecDashboard extends Component {
    static template = "aite_exec_dashboard.Dashboard";
    static components = { ExecDashboardView };
    static props = ["*"];
}

registry.category("actions").add("aite_exec_dashboard", ExecDashboard);
