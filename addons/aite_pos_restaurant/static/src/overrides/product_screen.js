/** L'écran de commande (revue de l'incrément 5).
 *
 * - Les gestes qui ajoutent un produit — toucher d'une carte, lecture d'un
 *   code-barres (simple ou GS1) — passent par `pos.aiteGesteAjout` : un
 *   produit suivi en stock qui n'en a plus n'est pas ajouté (R11). Le
 *   contrôle n'est pas dans `addLineToCurrentOrder`, que des boutons d'Odoo
 *   appellent pour scinder une ligne sans rien ajouter (« Note cuisine »,
 *   « Note au client » sur une ligne en partie envoyée).
 * - Une minuterie de 30 secondes appelle `pos.aiteTic()`, comme sur le plan :
 *   la durée de la phrase d'état (« Table 12 · ouverte par Awa · 35 min »)
 *   suit sans qu'on touche l'écran (partie 1.3). */
import { patch } from "@web/core/utils/patch";
import { onMounted, onWillUnmount } from "@odoo/owl";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { TIC } from "@aite_pos_restaurant/utils/alerte";

patch(ProductScreen.prototype, {
    setup() {
        super.setup(...arguments);
        let minuterie = null;
        onMounted(() => {
            if (this.pos.aiteActif) {
                minuterie = setInterval(() => this.pos.aiteTic(), TIC);
            }
        });
        onWillUnmount(() => clearInterval(minuterie));
    },
    async addProductToOrder(product) {
        return this.pos.aiteGesteAjout(() => super.addProductToOrder(...arguments));
    },
    async _barcodeProductAction(code) {
        return this.pos.aiteGesteAjout(() => super._barcodeProductAction(...arguments));
    },
    async _barcodeGS1Action(parsedResults) {
        return this.pos.aiteGesteAjout(() => super._barcodeGS1Action(...arguments));
    },
});
