/** La barre et son menu ≡ sur le plan verrouillé (spécification, partie
 * 4.1).
 *
 * - « Modifier le plan » disparaît de la caisse : le plan se dessine dans la
 *   gestion (T17) ;
 * - « Imprimer le rapport » : code, puis le droit « rapport_ventes »
 *   (caissière et au-dessus), sinon R21. */
import { patch } from "@web/core/utils/patch";
import { Navbar } from "@point_of_sale/app/navbar/navbar";
import "@pos_hr/overrides/components/navbar/navbar";
import "@pos_restaurant/overrides/components/navbar/navbar";
import { MESSAGES, TITRES } from "@aite_pos_restaurant/utils/messages";

patch(Navbar.prototype, {
    get showEditPlanButton() {
        return this.pos.aiteActif ? false : super.showEditPlanButton;
    },
    async showSaleDetails() {
        if (!this.pos.aiteActif) {
            return super.showSaleDetails(...arguments);
        }
        return this.pos.aiteGeste({
            titre: TITRES.rapport,
            geste: "rapport_ventes",
            refus: MESSAGES.R21,
            action: () => super.showSaleDetails(...arguments),
        });
    },
});
