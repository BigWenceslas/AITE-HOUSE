/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { _t } from "@web/core/l10n/translation";
import { BonArdoise } from "@aite_pos_credit/js/pos/bon_ardoise";

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
        // AH-02 : même garde que le gabarit (ardoise réservée au manager sur
        // une caisse au service à table contrôlé d'aite_pos_restaurant) ; sur
        // toute autre caisse, rien ne change (comportement d'avant AH-02).
        if (this.pos.aiteActif && !this.pos.aitePeut("ardoise")) {
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
                    "Aucun mode de paiement « ardoise » sur cette caisse. " +
                    "Dans Point de Vente → Configuration → Modes de paiement, " +
                    "ouvrez « Ardoise client » (ou créez un mode de type " +
                    "« Compte client » : sans journal, « Identifier le " +
                    "client » coché), cochez « Vente à crédit (ardoise) », " +
                    "puis ajoutez-le à la caisse."
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

        // Ce que portera le bon d'ardoise, pris avant la validation (la
        // caisse passe ensuite à l'addition suivante).
        const bon = this._aiteDonneesBon(order, partner, due);

        // Valide la commande → synchro serveur → ardoise + écriture 411.
        await this.validateOrder(false);

        // Le bon d'ardoise, signé par le client et gardé par l'établissement.
        if (bon && order.finalized) {
            await this._aiteImprimerBon(bon);
        }
    },

    /** Les données du « Bon d'ardoise » (ticket que le client signe). */
    _aiteDonneesBon(order, partner, montant) {
        try {
            const employe = order.employee_id || this.pos.cashier;
            return {
                data: this.pos.orderExportForPrinting(order),
                client: { name: partner.name || "", phone: partner.phone || "", mobile: partner.mobile || "" },
                montant,
                date: new Date().toLocaleString("fr-FR", {
                    day: "2-digit", month: "2-digit", year: "numeric", hour: "2-digit", minute: "2-digit",
                }),
                table: order.table_id?.table_number ? String(order.table_id.table_number) : "",
                servi: employe?.name || "",
                formatCurrency: this.env.utils.formatCurrency,
            };
        } catch (erreur) {
            console.error("Bon d'ardoise : données indisponibles", erreur);
            return null;
        }
    },

    /** Imprime le bon sur l'imprimante de tickets ; sans imprimante, par
     * l'impression du navigateur. Une panne d'impression ne défait pas
     * l'ardoise : elle est dite, et le bon peut être réimprimé depuis
     * POS Crédit → Ardoises (Relevé d'ardoises). */
    async _aiteImprimerBon(bon) {
        try {
            await this.printer.print(BonArdoise, bon, { webPrintFallback: true });
        } catch {
            this.notification.add(
                _t("Ardoise enregistrée, mais le bon d'ardoise n'a pas pu être imprimé : vérifiez l'imprimante."),
                { type: "warning" }
            );
        }
    },
});
