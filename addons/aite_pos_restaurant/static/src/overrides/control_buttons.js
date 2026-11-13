/** Boutons de l'écran de commande (spécification, partie 4.1).
 *
 * - « Déplacer ou réunir » abandonné (toucher le plan hors d'une table) :
 *   Odoo reste sur le plan sans changer d'écran, au nom de la personne
 *   identifiée ; un second écouteur, à usage unique, verrouille alors le plan.
 *   Le même écouteur fait retomber le drapeau d'un déplacement abandonné par
 *   les 5 minutes sans activité quand le premier toucher qui suit n'est pas
 *   une table (l'écouteur d'Odoo ne rappelle alors pas transferOrder) ; un
 *   nouveau déplacement le fait retomber aussi ;
 * - « Remboursement » : réservé au manager (R16). */
import { patch } from "@web/core/utils/patch";
import { ControlButtons } from "@point_of_sale/app/screens/product_screen/control_buttons/control_buttons";
import "@pos_restaurant/app/control_buttons/control_buttons";
import { MESSAGES } from "@aite_pos_restaurant/utils/messages";

patch(ControlButtons.prototype, {
    clickTransferOrder() {
        if (this.pos.aiteActif) {
            this.pos.aiteTransfertAbandonne = false; // un nouveau déplacement
        }
        const resultat = super.clickTransferOrder(...arguments);
        if (this.pos.aiteActif) {
            const pos = this.pos;
            const surveiller = (ev) => {
                if (ev.target.closest(".button-floor")) {
                    return; // changer de salle : le déplacement continue
                }
                document.removeEventListener("click", surveiller);
                if (!ev.target.closest(".table")) {
                    // Odoo a retiré son écouteur sans appeler transferOrder.
                    pos.aiteTransfertAbandonne = false;
                    pos.aiteVerrouillerSurPlan();
                }
            };
            document.addEventListener("click", surveiller);
        }
        return resultat;
    },
    clickRefund() {
        if (this.pos.aiteActif && !this.pos.aitePeut("rembourser")) {
            this.pos.notification.add(MESSAGES.R16, { type: "danger" });
            return;
        }
        return super.clickRefund(...arguments);
    },
});
