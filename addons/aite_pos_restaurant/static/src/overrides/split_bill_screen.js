/** Diviser l'addition (spécification, partie 4.1 ; Q29, F20 ; incrément 3).
 *
 * - toute l'addition sélectionnée : rien à diviser (R30) ;
 * - ce qui a été saisi sur l'addition est d'abord enregistré (journal des
 *   saisies), et une synchronisation en cours de l'origine est attendue
 *   (Odoo l'écarterait, et la part et l'origine seraient enregistrées
 *   ensemble avec les mêmes produits) ; la division est ensuite signalée au
 *   serveur comme un déplacement : ni saisie, ni retrait ;
 * - la part (« 12B ») reçoit l'origine, l'heure d'ouverture et « ouverte
 *   par » de l'addition divisée, et 0 personne : les personnes restent sur
 *   l'origine (Odoo lui en retire une). */
import { patch } from "@web/core/utils/patch";
import { SplitBillScreen } from "@pos_restaurant/app/split_bill_screen/split_bill_screen";
import { MESSAGES, TEXTES } from "@aite_pos_restaurant/utils/messages";

patch(SplitBillScreen.prototype, {
    setup() {
        super.setup(...arguments);
        this.aiteTextes = TEXTES; // « Créer l'addition à part » (gabarit)
    },
    async createSplittedOrder() {
        if (!this.pos.aiteActif) {
            return super.createSplittedOrder(...arguments);
        }
        const origine = this.currentOrder;
        const lignes = origine.lines;
        if (lignes.length && lignes.every((line) => this.qtyTracker[line.uuid] === line.get_quantity())) {
            this.pos.notification.add(MESSAGES.R30, { type: "danger" });
            return;
        }
        await this.pos.aiteQuitterAddition(origine);
        await this.pos.aiteAttendreSynchro(origine);
        this.pos.aiteDeplacementEnCours = true;
        try {
            return await super.createSplittedOrder(...arguments);
        } finally {
            this.pos.aiteDeplacementEnCours = false;
        }
    },
    async preSplitOrder(originalOrder, newOrder) {
        await super.preSplitOrder(...arguments);
        if (this.pos.aiteActif) {
            newOrder.update({
                aite_origine_uuid: originalOrder.uuid,
                aite_heure_ouverture: originalOrder.aite_heure_ouverture || false,
                aite_ouverte_par_id: originalOrder.aite_ouverte_par_id || this.pos.cashier,
            });
            newOrder.setCustomerCount(0);
        }
    },
    async postSplitOrder(originalOrder, newOrder) {
        await super.postSplitOrder(...arguments);
        if (this.pos.aiteActif) {
            // Odoo retire une personne à l'origine après l'enregistrement : elle
            // garde les siennes, comme sur le serveur.
            originalOrder.customer_count += 1;
        }
    },
});
