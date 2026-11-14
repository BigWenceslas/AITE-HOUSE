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
 * - au-dessus de ce qui est parti : Odoo ;
 * - incrément 5 (revue, constat 1) : une hausse d'un produit suivi en stock
 *   passe par le même contrôle qu'un ajout (`pos.aiteProduitDisponible`) ;
 *   refusée, elle affiche R11, le chiffre est ignoré et le pavé repart de
 *   zéro (« 5 » refusé, puis « 2 » vaut 2, pas 52). Quand la mémoire du stock
 *   ne suffit pas pour décider, le chiffre est appliqué au retour du
 *   serveur, s'il est encore celui du pavé et de la même ligne.
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
        const selectionnee = this.currentOrder?.get_selected_orderline();
        let line = selectionnee;
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
        if (envoye > 0) {
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
        }
        // Incrément 5 : une hausse d'un produit suivi en stock (constat 1).
        const hausse = quantite === null || Number.isNaN(quantite) ? 0 : quantite - line.get_quantity();
        if (hausse > 0 && !line.refunded_orderline_id) {
            const order = this.currentOrder;
            const product = line.get_product();
            if (!this.pos.aiteDecisionImmediate(order, product, hausse)) {
                this.pos.aiteProduitDisponible(order, product, hausse).then((permis) => {
                    const toujours =
                        this.pos.get_order() === order &&
                        this.numberBuffer.get() === val &&
                        order.get_selected_orderline() === selectionnee &&
                        this.pos.numpadMode === "quantity";
                    if (!toujours) {
                        return; // un autre chiffre, une autre ligne ou un autre écran entre-temps
                    }
                    if (permis) {
                        super._setValue(val);
                        return;
                    }
                    this.numberBuffer.reset();
                    this.pos.aiteNotifierEpuise(product);
                });
                return;
            }
        }
        return super._setValue(...arguments);
    },
});
