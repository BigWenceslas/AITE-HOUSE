/** Le contrôle d'ouverture d'Odoo (fond de caisse), après le code : à sa
 * fermeture, le plan se verrouille (la caissière n'y reste pas identifiée).
 * Abandonné (« Retour »), la caisse reste fermée : le code tapé n'autorise
 * plus l'ouverture sur le serveur. */
import { patch } from "@web/core/utils/patch";
import { onWillUnmount } from "@odoo/owl";
import { OpeningControlPopup } from "@point_of_sale/app/store/opening_control_popup/opening_control_popup";

patch(OpeningControlPopup.prototype, {
    setup() {
        super.setup(...arguments);
        if (this.pos.aiteActif) {
            onWillUnmount(() => {
                if (this.pos.session.state === "opening_control") {
                    this.pos.aiteAbandonnerCode();
                }
                this.pos.aiteVerrouillerSurPlan();
            });
        }
    },
});
