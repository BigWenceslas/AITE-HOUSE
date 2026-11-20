/** @odoo-module **/
import { Component } from "@odoo/owl";
import { OrderWidget } from "@point_of_sale/app/generic_components/order_widget/order_widget";
import { Orderline } from "@point_of_sale/app/generic_components/orderline/orderline";
import { ReceiptHeader } from "@point_of_sale/app/screens/receipt_screen/receipt/receipt_header/receipt_header";
import { omit } from "@web/core/utils/objects";

/**
 * Le « Bon d'ardoise » : ticket imprimé au toucher de « Mettre sur ardoise ».
 * Le client le signe ; le restaurant le garde comme preuve de la dette.
 * Il reprend l'en-tête du ticket d'Odoo (société), les produits de la
 * commande, le client, la date et le montant mis sur ardoise.
 */
export class BonArdoise extends Component {
    static template = "aite_pos_credit.BonArdoise";
    static components = { OrderWidget, Orderline, ReceiptHeader };
    static props = {
        data: Object,
        client: Object,
        montant: Number,
        date: String,
        table: { type: String, optional: true },
        servi: { type: String, optional: true },
        formatCurrency: Function,
    };
    omit(...args) {
        return omit(...args);
    }
}
