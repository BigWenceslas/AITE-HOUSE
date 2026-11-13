/** Les onglets des additions sans table (barre du haut et sélecteur de
 * table).
 *
 * - Toucher un onglet : rien de propre, `showScreen` demande le code et
 *   contrôle la table d'un collègue (la fenêtre du code s'ouvre après le
 *   `dialog.closeAll()` d'Odoo) ;
 * - le « + » (nouvelle vente sans table) n'est pas proposé en mode : chaque
 *   vente se fait sur une table du plan, ou sur un numéro tapé dans
 *   « Table » (pris en avance sur l'incrément 3 : sans la case « Autoriser
 *   la vente sans table », décochée d'office, le « + » disparaît ; R17). */
import { patch } from "@web/core/utils/patch";
import { OrderTabs } from "@point_of_sale/app/components/order_tabs/order_tabs";
import { MESSAGES } from "@aite_pos_restaurant/utils/messages";

patch(OrderTabs.prototype, {
    newFloatingOrder() {
        if (this.pos.aiteActif) {
            this.pos.notification.add(MESSAGES.R17, { type: "danger" });
            return;
        }
        return super.newFloatingOrder(...arguments);
    },
});
