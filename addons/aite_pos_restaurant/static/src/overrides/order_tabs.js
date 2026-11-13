/** Les onglets des additions sans table (barre du haut et sélecteur de
 * table).
 *
 * - Toucher un onglet : rien de propre, `showScreen` demande le code et
 *   contrôle la table d'un collègue (la fenêtre du code s'ouvre après le
 *   `dialog.closeAll()` d'Odoo) ;
 * - le « + » (nouvelle vente sans table) suit la case « Autoriser la vente
 *   sans table » de la caisse (PROF-04-P1) : décochée (d'office), il
 *   n'apparaît pas et une vente sans table est refusée (R17) ; cochée, il
 *   demande le code si personne n'est identifié, puis le droit
 *   « vente_sans_table » (caissière et au-dessus, R17) ; la vente compte 0
 *   personne (Q76). */
import { patch } from "@web/core/utils/patch";
import { OrderTabs } from "@point_of_sale/app/components/order_tabs/order_tabs";
import "@pos_restaurant/overrides/components/order_tabs/order_tabs";
import { MESSAGES } from "@aite_pos_restaurant/utils/messages";

patch(OrderTabs.prototype, {
    newFloatingOrder() {
        if (!this.pos.aiteActif) {
            return super.newFloatingOrder(...arguments);
        }
        if (!this.pos.config.aite_vente_sans_table) {
            this.pos.notification.add(MESSAGES.R17, { type: "danger" });
            return;
        }
        return this.pos.aiteVenteSansTable(() => super.newFloatingOrder(...arguments));
    },
});
