/** Liste des commandes : le remboursement est réservé au manager (R16). Le
 * code et la table d'un collègue sont contrôlés par `showScreen`. */
import { patch } from "@web/core/utils/patch";
import { TicketScreen } from "@point_of_sale/app/screens/ticket_screen/ticket_screen";
import { MESSAGES } from "@aite_pos_restaurant/utils/messages";

patch(TicketScreen.prototype, {
    async onDoRefund() {
        if (this.pos.aiteActif && !this.pos.aitePeut("rembourser")) {
            this.pos.notification.add(MESSAGES.R16, { type: "danger" });
            return;
        }
        return super.onDoRefund(...arguments);
    },
});
