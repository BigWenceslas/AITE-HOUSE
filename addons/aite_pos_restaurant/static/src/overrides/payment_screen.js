/** AH-02 : les modes « payer plus tard » (ardoise, compte client) ne sont
 * proposés qu'au manager. Le serveur les marque au chargement
 * (`_aite_reserve_manager`) ; la note de chambre d'aite_hotel_pos_link, si
 * ce module est installé, reste proposée.
 *
 * La liste suit la personne identifiée à chaque affichage : une caissière
 * qui reprend la main au manager sur l'écran de paiement ne voit plus les
 * modes réservés. */
import { patch } from "@web/core/utils/patch";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";

patch(PaymentScreen.prototype, {
    setup() {
        super.setup(...arguments);
        if (this.pos.aiteActif) {
            const tous = this.payment_methods_from_config;
            Object.defineProperty(this, "payment_methods_from_config", {
                configurable: true,
                get: () =>
                    this.pos.aitePeut("ardoise")
                        ? tous
                        : tous.filter((mode) => !mode._aite_reserve_manager),
            });
        }
    },
});
