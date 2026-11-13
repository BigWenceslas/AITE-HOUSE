/** La barre et son menu ≡ sur le plan verrouillé (spécification, partie
 * 4.1).
 *
 * - « Modifier le plan » disparaît de la caisse : le plan se dessine dans la
 *   gestion (T17) ;
 * - « Imprimer le rapport » : code, puis le droit « rapport_ventes »
 *   (caissière et au-dessus), sinon R21 ;
 * - incrément 3 : un numéro tapé dans « Table » qui n'est ni sur le plan ni
 *   déjà ouvert ouvre une table à ce nom (Q25, T11) : code si personne
 *   n'est identifié, puis le nombre de personnes ; l'addition est enregistrée
 *   aussitôt. Une addition déjà ouverte (« 12B », numéro déjà tapé) passe par
 *   `showScreen` (code, table d'un collègue). « Retour » à l'étape personnes
 *   ramène, depuis l'écran de commande, à l'addition qui était affichée quand
 *   « Table » a été touché (revue de l'incrément 3). */
import { patch } from "@web/core/utils/patch";
import { Navbar } from "@point_of_sale/app/navbar/navbar";
import "@pos_hr/overrides/components/navbar/navbar";
import "@pos_restaurant/overrides/components/navbar/navbar";
import { MESSAGES, TITRES } from "@aite_pos_restaurant/utils/messages";

patch(Navbar.prototype, {
    get showEditPlanButton() {
        return this.pos.aiteActif ? false : super.showEditPlanButton;
    },
    async onClickTableTab() {
        if (this.pos.aiteActif) {
            // L'addition affichée : Odoo en pose une neuve pour un numéro
            // inconnu, avant de nous la donner (setFloatingOrder).
            this.aiteAdditionAvantNumero = this.pos.get_order() || null;
        }
        return super.onClickTableTab(...arguments);
    },
    setFloatingOrder(floatingOrder) {
        const neuve =
            this.pos.aiteActif &&
            floatingOrder &&
            typeof floatingOrder.id !== "number" &&
            !floatingOrder.lines.length &&
            !floatingOrder.aite_ouverte_par_id;
        if (!neuve) {
            return super.setFloatingOrder(...arguments);
        }
        return this.pos.aiteOuvrirNumero(
            floatingOrder,
            () => super.setFloatingOrder(floatingOrder),
            this.aiteAdditionAvantNumero
        );
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
