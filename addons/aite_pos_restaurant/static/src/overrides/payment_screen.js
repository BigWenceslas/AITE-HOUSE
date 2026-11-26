/** L'écran de paiement de la caisse au service à table contrôlé.
 *
 * AH-02 : les modes « payer plus tard » (ardoise, compte client) ne sont
 * proposés qu'au manager. Le serveur les marque au chargement
 * (`_aite_reserve_manager`) ; la note de chambre d'aite_hotel_pos_link, si
 * ce module est installé, reste proposée.
 *
 * La liste suit la personne identifiée à chaque affichage : une caissière
 * qui reprend la main au manager sur l'écran de paiement ne voit plus les
 * modes réservés.
 *
 * Partager à parts égales (demande du Messager : « diviser la facture à
 * part égale par le nombre de personnes qui doivent payer ») :
 * - « Partager à parts égales » ouvre « Combien de personnes paient ? »
 *   (`AitePartsPopup`) ; les parts se calculent sur le reste dû à ce
 *   moment-là (tout le total s'il n'y a pas encore de paiement) ;
 * - le bandeau dit la part en cours (« Part 1 sur 3 : 33 333 FCFA ») ;
 *   toucher un mode de paiement crée une ligne du montant de cette part,
 *   la dernière est le reste dû (elle absorbe l'arrondi) ; le pavé
 *   numérique d'Odoo change le montant de la ligne comme d'habitude ;
 * - monnaie rendue : Odoo ne la calcule que sur l'addition entière (le
 *   total payé moins le total). Une part intermédiaire ne dépasse donc
 *   jamais le reste dû. Si la caissière tape ce que la personne donne en
 *   espèces (50 000 pour une part de 33 333), le bandeau dit « Monnaie à
 *   rendre : 16 667 FCFA » ; au mode suivant (ou à la validation), la
 *   ligne revient à 33 333 : la caisse enregistre ce qui reste dans le
 *   tiroir, et la dernière part ne change pas. Un mode autre que les
 *   espèces ne rend pas de monnaie : un montant tapé au-delà de la part y
 *   est payé et la dernière part diminue d'autant. Sur la dernière part,
 *   taper ce que la personne donne affiche la monnaie d'Odoo, comme sans
 *   partage ;
 * - arrondi des espèces : les parts intermédiaires sont des multiples de
 *   l'arrondi (`pasDuPartage`) ; la dernière part en espèces est arrondie
 *   par Odoo, et le bandeau dit alors les deux montants (« 2 685 FCFA
 *   (2 675 FCFA en espèces) ») ;
 * - le partage est tenu par l'addition : revenir au panier puis au
 *   paiement le retrouve, tant que le total de l'addition n'a pas changé ;
 *   si un produit ou un pourboire a été ajouté ou retiré, le partage est
 *   oublié (il se refait d'un toucher) ;
 * - « Annuler le partage » rend le comportement d'Odoo : les lignes déjà
 *   créées restent, la ligne suivante paie le reste dû ; il n'est plus
 *   proposé quand toutes les parts sont encaissées. */
import { patch } from "@web/core/utils/patch";
import { floatIsZero } from "@web/core/utils/numbers";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { makeAwaitable } from "@point_of_sale/app/store/make_awaitable_dialog";
import { AitePartsPopup } from "@aite_pos_restaurant/components/parts_popup/parts_popup";
import { TEXTES } from "@aite_pos_restaurant/utils/messages";
import { partagePossible, pasDuPartage } from "@aite_pos_restaurant/utils/parts_egales";

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
            this.aiteTextes = TEXTES;
            this.aiteVerifierLePartage();
        }
    },

    // ------------------------------------------------------------------
    // Partager à parts égales
    // ------------------------------------------------------------------

    /** Retour au paiement : un partage dont l'addition a changé est oublié. */
    aiteVerifierLePartage() {
        const order = this.currentOrder;
        if (order?.uiState?.aitePartage && !order.aitePartageEnCours()) {
            order.uiState.aitePartage = null;
        }
    },

    get aitePasDuPartage() {
        return pasDuPartage(this.pos.config, this.pos.currency);
    },

    /** Le bouton « Partager à parts égales » : en mode, sans partage en
     * cours, quand il reste au moins deux pas à payer. */
    get aitePeutPartager() {
        const order = this.currentOrder;
        return (
            this.pos.aiteActif &&
            Boolean(order) &&
            !order.aitePartageEnCours() &&
            order.getTotalDue() > 0 &&
            partagePossible(order.get_due(), 2, this.aitePasDuPartage)
        );
    },

    get aitePart() {
        return this.pos.aiteActif ? this.currentOrder?.aitePartEnCours() : null;
    },

    /** La dernière part payée en espèces, quand l'arrondi des espèces la
     * change (sinon null). */
    aiteDernierePartEnEspeces(part) {
        const order = this.currentOrder;
        const especes = this.payment_methods_from_config.find((mode) => mode.is_cash_count);
        if (!part.derniere || !especes || !order.shouldRound(especes)) {
            return null;
        }
        const arrondi = order.getRoundedRemaining(this.pos.config.rounding_method, part.montant);
        return floatIsZero(arrondi - part.montant, this.pos.currency.decimal_places) ? null : arrondi;
    },

    /** La phrase du bandeau : « Part 2 sur 3 : 33 333 FCFA ». */
    get aiteTexteDeLaPart() {
        const part = this.aitePart;
        if (!part) {
            return "";
        }
        if (part.reglee) {
            return part.complet ? TEXTES.partsReglees(part.nombre) : TEXTES.additionReglee;
        }
        const format = (montant) => this.env.utils.formatCurrency(montant);
        const especes = this.aiteDernierePartEnEspeces(part);
        return especes === null
            ? TEXTES.part(part.rang, part.nombre, format(part.montant))
            : TEXTES.partEspeces(part.rang, part.nombre, format(part.montant), format(especes));
    },

    /** « Monnaie à rendre : 16 667 FCFA » : une part intermédiaire payée en
     * espèces au-delà de la part. */
    get aiteMonnaieDeLaPart() {
        const monnaie = this.aitePart?.monnaie || 0;
        return monnaie > 0 ? TEXTES.monnaieARendre(this.env.utils.formatCurrency(monnaie)) : "";
    },

    /** Sous la part, quand des paiements existaient avant le partage. */
    get aiteResteDuPartage() {
        const partage = this.currentOrder?.aitePartageEnCours();
        return partage?.surLeReste
            ? TEXTES.resteAPartager(this.env.utils.formatCurrency(partage.base))
            : "";
    },

    async aitePartager() {
        const order = this.currentOrder;
        if (!this.aitePeutPartager) {
            return;
        }
        this.numberBuffer.capture();
        const base = order.get_due();
        const pas = this.aitePasDuPartage;
        const surLeReste = !floatIsZero(order.get_total_paid(), this.pos.currency.decimal_places);
        const nombre = await makeAwaitable(this.dialog, AitePartsPopup, {
            base,
            pas,
            unite: this.pos.currency.rounding,
            personnes: order.getCustomerCount?.() ?? order.customer_count ?? 0,
            surLeReste,
        });
        if (!nombre || order.aitePartageEnCours()) {
            return;
        }
        order.uiState.aitePartage = {
            nombre,
            base,
            pas,
            total: order.getTotalDue(),
            surLeReste,
            lignes: [],
        };
        this.numberBuffer.reset();
    },

    aiteAnnulerLePartage() {
        this.currentOrder.uiState.aitePartage = null;
        this.numberBuffer.reset();
    },

    /** Toucher un mode de paiement : le montant tapé au pavé est pris
     * d'abord, pour que la monnaie d'une part payée en espèces soit rendue
     * (`add_paymentline` de l'addition fait la part). */
    async addNewPaymentLine(paymentMethod) {
        if (this.aitePart) {
            this.numberBuffer.capture();
        }
        return super.addNewPaymentLine(...arguments);
    },

    /** Les parts payées en espèces au-delà de la part reviennent à leur
     * montant (la monnaie a été rendue) ; le nombre de parts est écrit sur
     * l'addition (le ticket le dit) quand toutes les parts sont encaissées,
     * 0 sinon (partage annulé ou inachevé). */
    async validateOrder() {
        if (this.pos.aiteActif && this.currentOrder) {
            const order = this.currentOrder;
            if (order.aitePartageEnCours()) {
                this.numberBuffer.capture();
                order.aiteRamenerAuxParts();
            }
            order.aite_parts_egales = order.aitePartageComplet()
                ? order.aitePartageEnCours().nombre
                : 0;
        }
        return super.validateOrder(...arguments);
    },
});
