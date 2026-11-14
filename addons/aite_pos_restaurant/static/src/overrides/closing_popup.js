/** La fenêtre de fermeture d'Odoo (spécification, partie 4.1 ; R14).
 *
 * - le chef de salle ferme ; au-delà de l'écart maximum (s'il est réglé),
 *   seul le manager (R14), au lieu du rôle « admin » de pos_hr ;
 * - à sa disparition sans fermeture, le plan se verrouille : la personne
 *   qui a tapé son code pour fermer n'y reste pas identifiée, et ce code
 *   n'autorise plus la fermeture sur le serveur (sauf si la fenêtre se
 *   rouvre aussitôt, après une sortie d'espèces faite depuis elle) ;
 * - incrément 4 (REST-10 critère 9) : des tables encore ouvertes empêchent
 *   la fermeture ; la fenêtre le dit (« {k} tables sont encore ouvertes : … »)
 *   et propose « Voir les tables » (la liste des commandes) ou « Annuler ces
 *   tables » : une seule fenêtre d'annulation et un seul motif pour toutes
 *   (le code de la personne qui ferme sert), puis la fermeture reprend. */
import { patch } from "@web/core/utils/patch";
import { onWillUnmount } from "@odoo/owl";
import { ClosePosPopup } from "@point_of_sale/app/navbar/closing_popup/closing_popup";
import "@pos_hr/overrides/components/closing_popup/closing_popup";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { MESSAGES, TEXTES, TITRES } from "@aite_pos_restaurant/utils/messages";

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
    async handleClosingError(response) {
        const ids = response?.open_order_ids || [];
        if (!this.pos.aiteActif || response?.redirect || !ids.length) {
            return super.handleClosingError(...arguments);
        }
        const ouvertes = this.pos.models["pos.order"].filter((o) => !o.finalized);
        this.dialog.add(ConfirmationDialog, {
            title: TITRES.fermerLaCaisse,
            body: TEXTES.tablesOuvertes(ids.length, this.pos.aiteListeDesTables(ouvertes, ids)),
            confirmLabel: TEXTES.voirLesTables,
            cancelLabel: TEXTES.annulerCesTables,
            confirm: () => {
                this.props.close();
                this.pos.showScreen("TicketScreen");
            },
            cancel: async () => {
                const tables = this.pos.models["pos.order"].filter((o) => !o.finalized);
                if (!(await this.pos.aiteAnnulerTables(tables, ids))) {
                    return false;
                }
                await this.pos.deleteOrders(tables, ids);
                this.closeSession();
            },
            dismiss: async () => {},
        });
    },
});
