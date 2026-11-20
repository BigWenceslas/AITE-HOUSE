/** Le « Bon d'ardoise » : au toucher de « Mettre sur ardoise », la caisse
 * imprime un ticket que le client signe (demande du client du restaurant :
 * « il faut une facture d'ardoise »). L'imprimante de tickets est simulée :
 * le tour lit le texte du ticket qu'elle reçoit. */
/* global posmodel */
import * as Chrome from "@point_of_sale/../tests/tours/utils/chrome_util";
import * as Dialog from "@point_of_sale/../tests/tours/utils/dialog_util";
import * as ProductScreen from "@point_of_sale/../tests/tours/utils/product_screen_util";
import * as PaymentScreen from "@point_of_sale/../tests/tours/utils/payment_screen_util";
import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add("AiteBonArdoiseTour", {
    steps: () =>
        [
            Chrome.startPoS(),
            Dialog.confirm(),
            {
                content: "une imprimante de tickets simulée",
                trigger: "body",
                run() {
                    window.aiteTickets = [];
                    posmodel.hardwareProxy.printer = {
                        printReceipt: async (el) => {
                            window.aiteTickets.push(el.innerText);
                            return { successful: true };
                        },
                    };
                },
            },
            ProductScreen.clickDisplayedProduct("Letter Tray"),
            ProductScreen.clickPartnerButton(),
            ProductScreen.clickCustomer("Acme Corporation"),
            ProductScreen.clickPayButton(),
            PaymentScreen.isShown(),
            { content: "« Mettre sur ardoise »", trigger: ".payment-screen .aite-credit-btn", run: "click" },
            {
                content: "le bon d'ardoise est imprimé : titre, client, produit, montant dû, signature",
                trigger: "body",
                async run() {
                    const fin = Date.now() + 10000;
                    while (Date.now() < fin) {
                        const bon = (window.aiteTickets || []).find((t) => t.includes("BON D'ARDOISE"));
                        if (bon) {
                            for (const attendu of ["Acme Corporation", "Letter Tray", "Montant dû", "Signature du client"]) {
                                if (!bon.includes(attendu)) {
                                    throw new Error(`bon d'ardoise sans « ${attendu} » : ${bon}`);
                                }
                            }
                            return;
                        }
                        await new Promise((r) => setTimeout(r, 100));
                    }
                    throw new Error(`aucun bon d'ardoise imprimé (${(window.aiteTickets || []).length} ticket(s))`);
                },
            },
        ].flat(),
});
