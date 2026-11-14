/** Le pavé de l'écran de commande sur une ligne envoyée (spécification,
 * partie 4.1 ; F19 ; incrément 4). Un seul point pour tout le pavé, en mode
 * « quantité » :
 * - ⌫ jusqu'au vide (« remove ») : ce qui n'est pas encore parti s'en va
 *   librement (la ligne redescend à ce qui est parti, sans code ni trace,
 *   Q34) ; une ligne entièrement partie ouvre la fenêtre d'annulation ;
 * - « +/- » (valeur négative) : la fenêtre d'annulation ;
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
        const envoye = line ? partEnvoyee(line) : 0;
        if (!line || envoye <= 0) {
            return super._setValue(...arguments);
        }
        if (val === "remove") {
            if (line.get_quantity() > envoye) {
                line.set_quantity(envoye);
                return;
            }
            this.numberBuffer.reset();
            this.pos.aiteAnnulerLigne(line);
            return;
        }
        const quantite = parseFloat("" + (val ? val : 0));
        if (quantite < 0) {
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
