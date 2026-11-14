/** L'addition en caisse (spécification, partie 4.1 ; incrément 3).
 *
 * Personnes : pos_restaurant remet 1 personne à toute addition qui en a 0, à
 * chaque chargement (`customer_count || 1`). Une part née d'une division
 * (« 12B ») et une vente sans table ont 0 personne (Q29, Q76) : un 0 venu du
 * serveur est gardé.
 *
 * Incrément 4 : filet de `removeOrderline` — une ligne dont une part est
 * partie en cuisine ou au bar ne se retire pas sans autorisation (rend faux,
 * comme Odoo quand rien n'est retiré). */
import { patch } from "@web/core/utils/patch";
import { PosOrder } from "@point_of_sale/app/models/pos_order";
import "@pos_restaurant/overrides/models/pos_order";
import { partEnvoyee } from "@aite_pos_restaurant/utils/envoi";
import { caisseEnMode } from "@aite_pos_restaurant/models/pos_order_line";

patch(PosOrder.prototype, {
    setup(vals) {
        super.setup(...arguments);
        const config = this.config;
        if (
            config?.aite_mode_restaurant &&
            config.module_pos_restaurant &&
            config.module_pos_hr &&
            typeof vals?.id === "number" &&
            vals.customer_count === 0
        ) {
            this.customer_count = 0;
        }
    },
    removeOrderline(line) {
        if (caisseEnMode(this.config) && !this.uiState?.aiteAutorisation && partEnvoyee(line) > 0) {
            return false;
        }
        return super.removeOrderline(...arguments);
    },
});
