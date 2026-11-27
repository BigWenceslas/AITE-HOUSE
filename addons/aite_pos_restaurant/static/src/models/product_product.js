/** Les familles d'un produit pour les imprimantes de préparation
 * (18.0.1.0.14). Un produit sans famille de caisse n'a, pour Odoo, aucune
 * famille : `getOrderChanges` l'écarte de l'envoi dès qu'une imprimante a
 * des familles cochées, et il ne sort sur aucun bon. Quand la caisse a une
 * imprimante « Autre » (« Prend tout ce qu'aucune autre imprimante ne
 * prend »), il porte le repère `AUCUNE_FAMILLE` : il part en préparation et
 * l'imprimante « Autre » le reçoit. Sans imprimante « Autre », rien ne
 * change. Le repère ne figure sur aucune imprimante : il ne fait rien
 * prendre à une autre imprimante. */
import { patch } from "@web/core/utils/patch";
import { ProductProduct } from "@point_of_sale/app/models/product_product";
import { AUCUNE_FAMILLE } from "@aite_pos_restaurant/utils/familles";

patch(ProductProduct.prototype, {
    get parentPosCategIds() {
        const familles = super.parentPosCategIds;
        if (familles.length) {
            return familles;
        }
        const imprimantes = this.models?.["pos.printer"]?.getAll?.() || [];
        return imprimantes.some((imprimante) => imprimante.aite_prend_le_reste) ? [AUCUNE_FAMILLE] : familles;
    },
});
