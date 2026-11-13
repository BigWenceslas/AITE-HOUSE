/** Le nom en haut se touche pour « prendre la main » (M1) : notre fenêtre
 * du code, sans liste de noms ; la personne qui tape le sien devient
 * l'employé du poste, et l'écran affiché repasse par les contrôles du point
 * de passage (une serveuse qui reprend la main sur le paiement revient à
 * l'écran de commande). */
import { patch } from "@web/core/utils/patch";
import { CashierName } from "@point_of_sale/app/navbar/cashier_name/cashier_name";
import "@pos_hr/overrides/components/cashier_name/cashier_name";
import { TITRES } from "@aite_pos_restaurant/utils/messages";

patch(CashierName.prototype, {
    async selectCashier() {
        if (!this.pos.aiteActif) {
            return super.selectCashier(...arguments);
        }
        const employe = await this.pos.aiteIdentifier({ titre: TITRES.prendreLaMain });
        if (employe) {
            this.pos.aiteApresPriseEnMain();
        }
        return employe;
    },
});
