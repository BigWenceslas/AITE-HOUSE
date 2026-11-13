/** Après le paiement : pas d'écran « Paiement réussi » (spécification,
 * partie 1.1 E). La caisse revient au plan verrouillé ; après une part
 * d'addition divisée (« 12B »), elle revient à la table, avec la même
 * personne identifiée, pour encaisser la part suivante. Rien n'est imprimé
 * ici : Odoo imprime à la validation si « Impression automatique du reçu »
 * est coché. */
import { patch } from "@web/core/utils/patch";
import { onMounted } from "@odoo/owl";
import { ReceiptScreen } from "@point_of_sale/app/screens/receipt_screen/receipt_screen";
import "@pos_restaurant/overrides/components/receipt_screen/receipt_screen";

patch(ReceiptScreen.prototype, {
    setup() {
        super.setup(...arguments);
        if (this.pos.aiteActif) {
            onMounted(() => (this.isContinueSplitting() ? this.continueSplitting() : this.orderDone()));
        }
    },
});
