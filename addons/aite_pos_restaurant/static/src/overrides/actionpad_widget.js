/** « J'envoie » (spécification, partie 1.3 ; REST-02-P1, F6).
 *
 * Après l'envoi d'Odoo (bons imprimés s'il y a une imprimante), l'addition
 * est enregistrée sur le serveur, bon imprimé ou non, puis une notification
 * passagère dit ce qui est parti et le poste revient au plan verrouillé. Si
 * rien n'est parti (« Commande dépassée » : un autre poste avait modifié la
 * table), le poste reste sur la table et affiche R29. Hors connexion, Odoo
 * refuse l'envoi : retour au plan, verrouillé, et le message d'Odoo. */
import { patch } from "@web/core/utils/patch";
import { ConnectionLostError } from "@web/core/network/rpc";
import { ActionpadWidget } from "@point_of_sale/app/screens/product_screen/action_pad/action_pad";
import "@pos_restaurant/overrides/components/product_screen/actionpad_widget/actionpad_widget";
import { MESSAGES, TEXTES } from "@aite_pos_restaurant/utils/messages";

patch(ActionpadWidget.prototype, {
    async submitOrder() {
        if (!this.pos.aiteActif) {
            return super.submitOrder(...arguments);
        }
        if (this.uiState.clicked) {
            return;
        }
        const order = this.currentOrder;
        const compte = this.pos.categoryCount
            .map((ligne) => `${this.env.utils.formatProductQty(ligne.count, false)} ${ligne.name}`)
            .join(", ");
        try {
            await super.submitOrder(...arguments);
            await this.pos.syncAllOrders({ orders: [order] });
        } catch (erreur) {
            if (erreur instanceof ConnectionLostError) {
                this.pos.showScreen("FloorScreen");
                // Le message « hors connexion » d'Odoo, dans une autre pile.
                Promise.reject(erreur);
                return;
            }
            throw erreur;
        }
        if (this.pos.getOrderChanges(false, order).count) {
            this.pos.notification.add(MESSAGES.R29, { type: "danger" });
            return;
        }
        this.pos.notification.add(TEXTES.envoye(compte), { type: "info" });
        this.pos.showScreen("FloorScreen");
    },
});
