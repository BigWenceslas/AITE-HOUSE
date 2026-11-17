/** @odoo-module */
/* global posmodel */
/**
 * L'addition d'une part (« 4B ») s'imprime comme celle d'une table (constat du
 * client : « quand je divise une facture, je ne parviens pas à imprimer la
 * facture divisée »).
 */
import * as ProductScreen from "@point_of_sale/../tests/tours/utils/product_screen_util";
import * as FloorScreen from "@pos_restaurant/../tests/tours/utils/floor_screen_util";
import * as SplitBillScreen from "@pos_restaurant/../tests/tours/utils/split_bill_screen_util";
import * as Aite from "@aite_pos_restaurant/../tests/tours/aite_util";
import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add("AiteAdditionPartTour", {
    steps: () =>
        [
            ...Aite.planVerrouille(),
            FloorScreen.clickTable("4"),
            ...Aite.taperCode("3333"),
            ...Aite.personnes("2"),
            ...Aite.ecranCommande(),
            ProductScreen.clickDisplayedProduct("Coca-Cola"),
            ProductScreen.clickDisplayedProduct("Water"),
            Aite.jEnvoie(),
            ...Aite.planVerrouille(),
            FloorScreen.clickTable("4"),
            ...Aite.taperCode("3333"),
            ...Aite.ecranCommande(),
            Aite.ouvrirActions(),
            {
                content: "« Diviser l'addition »",
                trigger: ".modal .control-buttons-modal button:has(.fa-files-o)",
                run: "click",
            },
            { content: "l'écran de division", trigger: ".splitbill-screen" },
            SplitBillScreen.clickOrderline("Water"),
            SplitBillScreen.clickPay(),
            ...Aite.ecranCommande(),
            Aite.verifier("la part « 4B » est l'addition courante", () =>
                posmodel.get_order().getName?.().includes("4B") ||
                String(posmodel.get_order().floating_order_name || "").includes("4B") ||
                `addition courante : ${posmodel.get_order().getName?.()}`
            ),
            // Sans imprimante : l'aperçu de l'addition s'ouvre.
            {
                content: "« Addition » sur la part",
                trigger: ".control-buttons .aite-addition-btn:not([disabled])",
                run: "click",
            },
            { content: "l'aperçu de l'addition de la part", trigger: ".modal .pos-receipt" },
            {
                content: "l'aperçu montre la part (Water)",
                trigger: ".modal .pos-receipt:contains('Water')",
            },
            Aite.fermerFenetre(),
            // Avec une imprimante : l'addition part, et la caissière reste sur la
            // part (elle n'a pas de table sur le plan, où on ne la retrouverait pas).
            Aite.verifier("une imprimante de tickets simulée", () => {
                posmodel.hardwareProxy.printer = { printReceipt: async () => ({ successful: true }) };
                return true;
            }),
            {
                content: "« Addition » sur la part, avec l'imprimante",
                trigger: ".control-buttons .aite-addition-btn:not([disabled])",
                run: "click",
            },
            ...Aite.ecranCommande(),
            Aite.verifier("toujours sur la part « 4B » après l'impression", () => {
                const order = posmodel.get_order();
                return (posmodel.mainScreen.component?.name === "ProductScreen" && !order.table_id) ||
                    `écran ${posmodel.mainScreen.component?.name}, table ${order?.table_id?.table_number}`;
            }),
            Aite.verifier("plus d'imprimante", () => {
                posmodel.hardwareProxy.printer = null;
                return true;
            }),
        ].flat(),
});
