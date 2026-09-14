/** @odoo-module **/

import { Component } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

/**
 * Vue Configuration — accès rapide aux paramètres POS pertinents
 * et aux points de configuration de l'analyse.
 *
 * Sert de point d'entrée vers les écrans natifs Odoo (points de vente,
 * catégories POS, modes de paiement) avec des raccourcis.
 */
export class ConfigView extends Component {
    static template = "aite_pos_analytics.ConfigView";
    static props = {};

    setup() {
        this.action = useService("action");
    }

    openPosConfig() {
        this.action.doAction("point_of_sale.action_pos_config_kanban");
    }
    openPosCategory() {
        // Maintenant pointe vers les catégories produit (product.category)
        // utilisées pour l'analyse, plutôt que les catégories POS.
        this.action.doAction("product.product_category_action_form");
    }
    openPaymentMethods() {
        this.action.doAction("point_of_sale.action_pos_payment_method_form");
    }
    openProducts() {
        this.action.doAction("point_of_sale.product_template_action_pos_product");
    }
    openAnalyticsReport() {
        this.action.doAction("aite_pos_analytics.action_pos_daily_report");
    }
}
