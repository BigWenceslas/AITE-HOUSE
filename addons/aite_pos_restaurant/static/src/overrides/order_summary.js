/** Le pavé de l'écran de commande sur une ligne envoyée (spécification,
 * partie 4.1 ; F19 ; incrément 4). Un seul point pour tout le pavé, en mode
 * « quantité » :
 * - ⌫ jusqu'au vide (« remove ») : ce qui n'est pas encore parti s'en va
 *   librement (la ligne redescend à ce qui est parti, sans code ni trace,
 *   Q34) ; une ligne entièrement partie ouvre la fenêtre d'annulation ;
 * - « +/- » (valeur négative, hors remboursement) : comme ⌫ (revue de
 *   l'incrément 4, constats 1 et 2) — une ligne pas encore envoyée s'en va,
 *   une ligne qui a une part pas encore envoyée redescend à ce qui est parti,
 *   une ligne entièrement partie ouvre la fenêtre d'annulation ; jamais de
 *   ligne négative, qui baisserait l'addition sans code ;
 * - un chiffre qui donnerait moins que ce qui est parti est ignoré : le pavé
 *   appelle `_setValue` à chaque chiffre, et taper « 12 » sur une ligne de 3
 *   ne doit rien ouvrir au « 1 » ;
 * - au-dessus de ce qui est parti : Odoo.
 * `disallowLineQuantityChange` d'Odoo n'est pas utilisé : il crée une ligne
 * négative sans code. */
import { patch } from "@web/core/utils/patch";
import { OrderSummary } from "@point_of_sale/app/screens/product_screen/order_summary/order_summary";
import "@pos_restaurant/app/product_screen/order_summary/order_summary";
import { partEnvoyee } from "@aite_pos_restaurant/utils/envoi";

patch(OrderSummary.prototype, {
    _setValue(val) {
        if (!this.pos.aiteActif || this.pos.numpadMode !== "quantity") {
            return super._setValue(...arguments);
        }
        let line = this.currentOrder?.get_selected_orderline();
        if (line?.combo_parent_id) {
            line = line.combo_parent_id;
        }
        if (!line) {
            return super._setValue(...arguments);
        }
        const envoye = partEnvoyee(line);
        const quantite = val === "remove" ? null : parseFloat("" + (val ? val : 0));
        const negative = quantite !== null && quantite < 0 && !line.refunded_orderline_id;
        if (negative) {
            this.numberBuffer.reset(); // le pavé garde « -4 » : le « +/- » suivant le rendrait positif
            if (envoye <= 0) {
                this.currentOrder.removeOrderline(line);
                return;
            }
        }
        if (envoye <= 0) {
            return super._setValue(...arguments);
        }
        if (val === "remove" || negative) {
            if (line.get_quantity() > envoye) {
                line.set_quantity(envoye);
                return;
            }
            this.numberBuffer.reset();
            this.pos.aiteAnnulerLigne(line);
            return;
        }
        if (Number.isNaN(quantite) || quantite < envoye) {
            return; // sous ce qui est parti : ignoré
        }
        return super._setValue(...arguments);
    },
});
