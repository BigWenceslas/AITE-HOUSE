/** La fenêtre de fermeture d'Odoo (spécification, partie 4.1 ; R14).
 *
 * - le chef de salle ferme ; au-delà de l'écart maximum (s'il est réglé),
 *   seul le manager (R14), au lieu du rôle « admin » de pos_hr ;
 * - à sa disparition sans fermeture, le plan se verrouille : la personne
 *   qui a tapé son code pour fermer n'y reste pas identifiée, et ce code
 *   n'autorise plus la fermeture sur le serveur (sauf si la fenêtre se
 *   rouvre aussitôt, après une sortie d'espèces faite depuis elle). */
import { patch } from "@web/core/utils/patch";
import { onWillUnmount } from "@odoo/owl";
import { ClosePosPopup } from "@point_of_sale/app/navbar/closing_popup/closing_popup";
import "@pos_hr/overrides/components/closing_popup/closing_popup";
import { MESSAGES } from "@aite_pos_restaurant/utils/messages";

patch(ClosePosPopup.prototype, {
    setup() {
        super.setup(...arguments);
        if (this.pos.aiteActif) {
            this.pos.aiteGestesEnCours = (this.pos.aiteGestesEnCours || 0) + 1;
            onWillUnmount(() => {
                this.pos.aiteGestesEnCours--;
                this.pos.aiteFinDeGeste(() => this.pos.aiteAbandonnerCode());
            });
        }
    },
    hasUserAuthority() {
        if (!this.pos.aiteActif) {
            return super.hasUserAuthority(...arguments);
        }
        return this.pos.aitePeut("fermer_avec_ecart") || this.allowedDifference();
    },
    async confirm() {
        if (
            this.pos.aiteActif &&
            this.pos.config.cash_control &&
            !this.env.utils.floatIsZero(this.getMaxDifference()) &&
            !this.hasUserAuthority()
        ) {
            this.pos.notification.add(MESSAGES.R14, { type: "danger" });
            return;
        }
        return super.confirm(...arguments);
    },
});
