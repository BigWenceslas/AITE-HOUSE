/** Boutons de l'écran de commande (spécification, partie 4.1).
 *
 * - « Déplacer ou réunir » abandonné (toucher le plan hors d'une table) :
 *   Odoo reste sur le plan sans changer d'écran, au nom de la personne
 *   identifiée ; un second écouteur, à usage unique, verrouille alors le plan.
 *   Le même écouteur fait retomber le drapeau d'un déplacement abandonné par
 *   les 5 minutes sans activité quand le premier toucher qui suit n'est pas
 *   une table (l'écouteur d'Odoo ne rappelle alors pas transferOrder) ; un
 *   nouveau déplacement le fait retomber aussi ;
 * - « Remboursement » : réservé au manager (R16) ;
 * - incrément 3 : « {p} personnes » ouvre l'étape personnes de notre fenêtre
 *   (huit gros boutons, pas de zéro) au lieu de la fenêtre numérique d'Odoo
 *   (« Des convives ? », touche 0, virgule, « Discard ») ; après une
 *   « Addition » imprimée, le poste revient au plan verrouillé. */
import { patch } from "@web/core/utils/patch";
import { ControlButtons } from "@point_of_sale/app/screens/product_screen/control_buttons/control_buttons";
import { OrderReceipt } from "@point_of_sale/app/screens/receipt_screen/receipt/order_receipt";
import "@pos_restaurant/app/control_buttons/control_buttons";
import { BillScreen } from "@pos_restaurant/app/bill_screen/bill_screen";
import { MESSAGES, TEXTES, TITRES } from "@aite_pos_restaurant/utils/messages";

patch(ControlButtons.prototype, {
    setup() {
        super.setup(...arguments);
        this.aiteTextes = TEXTES;
    },
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
    async clickTableGuests() {
        if (!this.pos.aiteActif) {
            return super.clickTableGuests(...arguments);
        }
        const order = this.currentOrder;
        if (!order) {
            return;
        }
        this.dialog.closeAll(); // depuis « Actions » sur petit écran
        const personnes = await this.pos.aiteDemanderPersonnes(
            TITRES.personnes(this.pos.aiteNomAddition(order))
        );
        if (personnes) {
            order.setCustomerCount(personnes);
            this.pos.addPendingOrder([order.id]);
        }
    },
    async clickPrintBill() {
        if (!this.pos.aiteActif) {
            return super.clickPrintBill(...arguments);
        }
        const imprime = await this.printer.print(OrderReceipt, {
            data: this.pos.orderExportForPrinting(this.pos.get_order()),
            formatCurrency: this.env.utils.formatCurrency,
        });
        if (imprime) {
            // L'addition est partie à l'imprimante : retour au plan verrouillé.
            this.dialog.closeAll();
            this.pos.showScreen("FloorScreen");
        } else {
            this.dialog.add(BillScreen);
        }
    },
});
