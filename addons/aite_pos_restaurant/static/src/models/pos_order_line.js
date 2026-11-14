/** Filet de la ligne d'addition (spécification, partie 4.1 ; incrément 4).
 *
 * Le pavé (`OrderSummary._setValue`) ouvre la fenêtre d'annulation ; ce filet
 * attrape les autres chemins de la caisse qui baisseraient une quantité sous
 * ce qui est parti : sans autorisation (`order.uiState.aiteAutorisation`,
 * posée pendant l'application d'une annulation autorisée), `set_quantity`
 * rend `{title: "Produit déjà envoyé", body: R9}`, comme les refus d'Odoo,
 * et la quantité ne change pas. Le serveur trace quand même (« Retrait sans
 * code ») : un module qui ne lirait pas ce refus n'afficherait rien
 * (limite, partie 8.3). */
import { patch } from "@web/core/utils/patch";
import { PosOrderline } from "@point_of_sale/app/models/pos_order_line";
import { MESSAGES, TITRES } from "@aite_pos_restaurant/utils/messages";
import { partEnvoyee } from "@aite_pos_restaurant/utils/envoi";

/** Même règle que `PosStore.aiteActif` (la ligne n'a pas accès au store). */
export function caisseEnMode(config) {
    return Boolean(
        config?.aite_mode_restaurant && config.module_pos_restaurant && config.module_pos_hr
    );
}

patch(PosOrderline.prototype, {
    set_quantity(quantity, keep_price) {
        const order = this.order_id;
        if (order && caisseEnMode(order.config) && !order.uiState?.aiteAutorisation) {
            const quantite =
                typeof quantity === "number" ? quantity : parseFloat("" + (quantity ? quantity : 0));
            const envoye = partEnvoyee(this);
            if (envoye > 0 && quantite < envoye - 1e-9) {
                return {
                    title: TITRES.produitDejaEnvoye,
                    body: MESSAGES.R9(envoye, this.get_full_product_name()),
                };
            }
        }
        return super.set_quantity(...arguments);
    },
});
