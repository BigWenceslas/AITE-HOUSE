/** L'addition en caisse (spécification, partie 4.1 ; incrément 3).
 *
 * Personnes : pos_restaurant remet 1 personne à toute addition qui en a 0, à
 * chaque chargement (`customer_count || 1`). Une part née d'une division
 * (« 12B ») et une vente sans table ont 0 personne (Q29, Q76) : un 0 venu du
 * serveur est gardé. */
import { patch } from "@web/core/utils/patch";
import { PosOrder } from "@point_of_sale/app/models/pos_order";
import "@pos_restaurant/overrides/models/pos_order";

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
});
