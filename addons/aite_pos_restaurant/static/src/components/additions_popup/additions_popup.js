/** Les additions d'une table divisée (constat du client, table 7B : « quand
 * je clique sur Addition, je dois pouvoir voir toutes les additions dans le
 * cas où j'ai divisé une addition »).
 *
 * L'aperçu de « Addition » sans imprimante de tickets, quand l'addition
 * courante fait partie d'un groupe (l'origine et ses parts encore ouvertes,
 * `PosStore.aiteAdditionsDuGroupe`) : les additions sont empilées, dans
 * l'ordre de création, chacune avec son nom, son ticket (le rendu
 * `OrderReceipt` d'Odoo, comme l'aperçu d'Odoo pour une seule addition) et
 * son total. « J'imprime les additions » les imprime depuis le navigateur,
 * un ticket par addition (un saut de page entre deux). */
import { Component, useState } from "@odoo/owl";
import { Dialog } from "@web/core/dialog/dialog";
import { useService } from "@web/core/utils/hooks";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { OrderReceipt } from "@point_of_sale/app/screens/receipt_screen/receipt/order_receipt";
import { TEXTES } from "@aite_pos_restaurant/utils/messages";

export class AiteAdditionsPopup extends Component {
    static template = "aite_pos_restaurant.AiteAdditionsPopup";
    static components = { Dialog, OrderReceipt };
    static props = {
        orders: Array,
        dejaImprimees: { type: Number, optional: true },
        close: Function,
    };

    setup() {
        this.pos = usePos();
        this.printer = useService("printer");
        this.textes = TEXTES;
        // L'impression du navigateur ne passe pas par `printer.print` : son
        // « en cours » est tenu ici (pictogramme, bouton verrouillé contre le
        // double toucher).
        this.state = useState({ enCours: false });
    }

    /** Les additions encore ouvertes : une part payée depuis l'ouverture de
     * la fenêtre n'y figure plus. */
    get additions() {
        return this.props.orders.filter((order) => !order.finalized);
    }

    get titre() {
        return this.pos.aiteTitreDesAdditions(this.additions);
    }

    nom(order) {
        return TEXTES.table(this.pos.aiteNomAddition(order));
    }

    total(order) {
        return this.env.utils.formatCurrency(order.get_total_with_tax());
    }

    get totalGeneral() {
        return this.env.utils.formatCurrency(
            this.additions.reduce((somme, order) => somme + order.get_total_with_tax(), 0)
        );
    }

    donnees(order) {
        return { ...this.pos.orderExportForPrinting(order), isBill: true, show_change: false };
    }

    /** Un ticket par addition, empilés dans une seule impression du
     * navigateur (le rendu d'Odoo, addition par addition). */
    async imprimer() {
        if (this.state.enCours) {
            return;
        }
        this.state.enCours = true;
        try {
            const pile = document.createElement("div");
            pile.className = "aite-additions-impression";
            for (const [rang, order] of this.additions.entries()) {
                if (rang) {
                    await this.pos.aiteAttendreRendu();
                }
                const ticket = await this.printer.renderer.toHtml(OrderReceipt, {
                    data: this.donnees(order),
                    formatCurrency: this.env.utils.formatCurrency,
                });
                pile.appendChild(ticket.cloneNode(true));
            }
            await this.pos.aiteAttendreRendu();
            this.printer.printWeb(pile);
        } finally {
            this.state.enCours = false;
        }
    }
}
