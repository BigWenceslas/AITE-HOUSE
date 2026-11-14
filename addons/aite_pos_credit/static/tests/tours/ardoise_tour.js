/** « Mettre sur ardoise » sur une caisse hors service à table contrôlé
 * (décision d'arbitrage de l'intégrateur sur AH-02, incrément 4 du
 * restaurant) : le bouton reste affiché comme avant AH-02, même sans mode
 * « ardoise » sur la caisse, et le toucher affiche l'aide à la configuration.
 * La caisse de boutique de la suite d'Odoo (sans « Est un bar/restaurant »)
 * n'a ni mode « ardoise » ni service à table contrôlé ; ce tour passe avec ou
 * sans aite_pos_restaurant installé (`pos.aiteActif` faux, ou absent).
 * Le texte attendu est celui d'AITE, écrit en français dans le code. */
import * as Chrome from "@point_of_sale/../tests/tours/utils/chrome_util";
import * as Dialog from "@point_of_sale/../tests/tours/utils/dialog_util";
import * as ProductScreen from "@point_of_sale/../tests/tours/utils/product_screen_util";
import * as PaymentScreen from "@point_of_sale/../tests/tours/utils/payment_screen_util";
import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add("AiteArdoiseHorsModeTour", {
    steps: () =>
        [
            Chrome.startPoS(),
            // Le contrôle d'ouverture d'Odoo (fond de caisse) : « Ouvrir la caisse ».
            Dialog.confirm(),
            ProductScreen.clickDisplayedProduct("Letter Tray"),
            ProductScreen.clickPartnerButton(),
            ProductScreen.clickCustomer("Acme Corporation"),
            ProductScreen.clickPayButton(),
            PaymentScreen.isShown(),
            {
                content: "« Mettre sur ardoise » est affiché, sans mode « ardoise » sur la caisse",
                trigger: ".payment-screen .aite-credit-btn",
                run: "click",
            },
            {
                content: "l'aide à la configuration du mode « ardoise »",
                trigger:
                    ".o_notification_content:contains('Aucun mode de paiement « ardoise » sur cette caisse.')",
            },
            { content: "toujours l'écran de paiement", trigger: ".pos .payment-screen" },
        ].flat(),
});
