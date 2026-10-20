/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { _t } from "@web/core/l10n/translation";

/**
 * Geste « Mettre sur ardoise » ajouté à l'écran de paiement POS.
 *
 * En Odoo 18.0, l'API ``PaymentScreen.addControlButton`` n'existe pas : on
 * ajoute donc la méthode au prototype du PaymentScreen via ``patch`` et on
 * injecte le bouton par héritage du template ``PaymentScreenButtons``.
 *
 * Le bouton s'appuie sur la méthode de paiement marquée « Vente à crédit »
 * (``is_aite_credit``, chargé dans la caisse par ``_load_pos_data_fields``). Il exige un client, impute le
 * solde dû sur cette méthode, puis valide la commande. L'ardoise et son
 * écriture au compte client (411) sont créées côté serveur.
 */
patch(PaymentScreen.prototype, {
    /**
     * Retrouve la méthode de paiement « ardoise » disponible sur ce POS.
     * Tolère les variations d'API entre points de version 18.x.
     */
    _aiteGetCreditMethod() {
        const config = this.pos.config;
        let methods = config.payment_method_ids || [];
        // Selon la version, payment_method_ids peut être une collection de
        // records ou d'ids ; on récupère les records si besoin.
        if (methods.length && typeof methods[0] !== "object") {
            const store = this.pos.models?.["pos.payment.method"];
            if (store) {
                methods = methods.map((id) => store.get(id)).filter(Boolean);
            }
        }
        // Seule la méthode marquée « Vente à crédit (ardoise) » convient :
        // un autre mode « payer plus tard » (Note de chambre, Compte
        // client) porterait la dette ailleurs — pas de repli.
        return methods.find((m) => m.is_aite_credit && !m.is_room_charge);
    },

    /** Commande courante, quelle que soit l'API de la version. */
    _aiteGetOrder() {
        if (this.currentOrder) {
            return this.currentOrder;
        }
        if (this.pos.get_order) {
            return this.pos.get_order();
        }
        return this.pos.getOrder ? this.pos.getOrder() : null;
    },

    /**
     * Met la commande courante sur ardoise.
     */
    async putOnCredit() {
        const order = this._aiteGetOrder();
        if (!order) {
            return;
        }
        const partner = order.get_partner
            ? order.get_partner()
            : order.partner_id;
        if (!partner) {
            this.notification.add(
                _t("Sélectionnez d'abord un client pour une vente à crédit."),
                { type: "warning" }
            );
            if (this.pos.selectPartner) {
                await this.pos.selectPartner();
            }
            return;
        }

        const method = this._aiteGetCreditMethod();
        if (!method) {
            this.notification.add(
                _t(
                    "Aucune méthode de paiement « ardoise » n'est configurée. " +
                    "Créez-en une (type « Payer plus tard ») et cochez " +
                    "« Vente à crédit » dans sa fiche, puis ajoutez-la au POS."
                ),
                { type: "danger" }
            );
            return;
        }

        const due = order.get_due ? order.get_due() : order.amount_total;
        if (due <= 0) {
            this.notification.add(_t("Cette commande est déjà réglée."), {
                type: "info",
            });
            return;
        }

        // Impute le solde dû sur la méthode crédit.
        const line = order.add_paymentline
            ? order.add_paymentline(method)
            : order.addPaymentline(method);
        if (line) {
            if (line.set_amount) {
                line.set_amount(due);
            } else if (line.setAmount) {
                line.setAmount(due);
            }
        }

        // Valide la commande → synchro serveur → ardoise + écriture 411.
        await this.validateOrder(false);
    },
});
