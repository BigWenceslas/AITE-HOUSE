/* global Sha1 */
/** Caisse du restaurant AITE : le cœur, patch de PosStore (spécification,
 * partie 4.1).
 *
 * Tous les patchs commencent par `if (!this.aiteActif) return super…` : une
 * autre caisse de la même base n'est pas touchée.
 *
 * Incrément 2 — le code et le plan verrouillé :
 * - le plan est l'écran de repos, toujours verrouillé : tout retour au plan
 *   fait oublier l'employé (`showScreen("FloorScreen")`), sauf pendant
 *   « Déplacer ou réunir » ; plus d'écran « Déverrouiller la caisse » ni
 *   d'écran de veille ; retour au plan après 5 minutes sans toucher l'écran ;
 * - toucher une table depuis le plan demande toujours le code ;
 * - `showScreen` est le point de passage unique des écrans de commande, de
 *   paiement et de la liste des commandes (code, table d'un collègue,
 *   paiement réservé) ;
 * - les gestes réservés : ouvrir et fermer la caisse (code vérifié par le
 *   serveur), espèces, encaisser, imprimer le rapport.
 */
import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { makeAwaitable } from "@point_of_sale/app/store/make_awaitable_dialog";
import { ConnectionLostError, RPCError } from "@web/core/network/rpc";
// Fixe l'ordre des patchs : ceux de pos_hr et du restaurant d'abord.
import "@pos_hr/overrides/models/pos_store";
import "@pos_restaurant/overrides/models/pos_store";
import { AiteCodePopup } from "@aite_pos_restaurant/components/code_popup/code_popup";
import { MESSAGES, TEXTES, TITRES } from "@aite_pos_restaurant/utils/messages";

/** Écrans qui demandent quelqu'un d'identifié (point de passage `showScreen`). */
const ECRANS_A_CODE = ["ProductScreen", "PaymentScreen", "TicketScreen"];

patch(PosStore.prototype, {
    /** Vrai si la case « Service à table contrôlé » est cochée sur une caisse
     * de restaurant qui se connecte avec les employés (pos.config est chargé
     * avec tous ses champs). */
    get aiteActif() {
        const config = this.config;
        return Boolean(
            config?.aite_mode_restaurant && config.module_pos_restaurant && config.module_pos_hr
        );
    },

    // ------------------------------------------------------------------
    // Les droits : même algorithme que regles.autorise (Python)
    // ------------------------------------------------------------------

    /** Vrai si le niveau de `employe` suffit pour `geste`, d'après le
     * tableau reçu du serveur (`session._aite_droits`). Inconnu → faux. */
    aiteEmployePeut(employe, geste) {
        const niveaux = this.session?._aite_niveaux || [];
        const requis = (this.session?._aite_droits || {})[geste];
        const rang = niveaux.indexOf(employe?._aite_niveau);
        return Boolean(requis) && rang >= 0 && rang >= niveaux.indexOf(requis);
    },

    /** Droit de l'employé identifié sur le poste ; faux sans employé. Hors
     * mode, rien n'est réservé : vrai (le bouton d'ardoise d'aite_pos_credit
     * reste ainsi affiché sur les autres caisses). */
    aitePeut(geste) {
        if (!this.aiteActif) {
            return true;
        }
        return this.aiteEmployePeut(this.cashier, geste);
    },

    // ------------------------------------------------------------------
    // Identifier, verrouiller
    // ------------------------------------------------------------------

    aiteEmployeParCode(code) {
        const empreinte = Sha1.hash(code);
        return this.models["hr.employee"].find((employe) => employe._pin === empreinte);
    },

    /** Ouvre la fenêtre du code ; la personne reconnue devient l'employé du
     * poste (`set_cashier`) et son code est gardé jusqu'au verrou suivant
     * (T3). `verifier(employe, code)`, s'il est donné, peut refuser la
     * personne : la fenêtre reste alors ouverte pour un autre code. Rend
     * l'employé, ou faux (« Retour »). Une seule fenêtre à la fois : un
     * second appel pendant qu'elle est ouverte rend faux. */
    async aiteIdentifier({ titre, sousTitre = "", verifier = null } = {}) {
        if (this.aiteIdentificationEnCours) {
            return false;
        }
        this.aiteIdentificationEnCours = true;
        try {
            const resultat = await makeAwaitable(this.dialog, AiteCodePopup, {
                titre: titre || TITRES.prendreLaMain,
                sousTitre,
                reconnaitre: async (code) => {
                    const employe = this.aiteEmployeParCode(code);
                    if (!employe) {
                        return MESSAGES.R1;
                    }
                    if (verifier && !(await verifier(employe, code))) {
                        return false;
                    }
                    return employe;
                },
            });
            if (!resultat?.employe) {
                return false;
            }
            this.set_cashier(resultat.employe);
            this.aiteCodeVisite = resultat.code;
            return resultat.employe;
        } finally {
            this.aiteIdentificationEnCours = false;
        }
    },

    aiteVerrouiller() {
        this.reset_cashier();
        this.aiteCodeVisite = null;
    },

    /** Verrouille si le poste est sur le plan (hors « Déplacer ou
     * réunir ») : après un geste fait depuis le plan (espèces, rapport,
     * fermeture abandonnée, ouverture), le plan ne reste jamais au nom de
     * quelqu'un. */
    aiteVerrouillerSurPlan() {
        if (
            this.aiteActif &&
            this.mainScreen.component?.name === "FloorScreen" &&
            !this.isOrderTransferMode
        ) {
            this.aiteVerrouiller();
        }
    },

    /** Un geste du menu ≡ : demande le code si personne n'est identifié,
     * refuse sans le droit (`refus`), puis lance `action`. Verrouille ensuite
     * si le poste est sur le plan. */
    async aiteGeste({ titre, geste, refus, action }) {
        this.aiteGestesEnCours = (this.aiteGestesEnCours || 0) + 1;
        try {
            if (!this.cashier && !(await this.aiteIdentifier({ titre }))) {
                return;
            }
            if (!this.aitePeut(geste)) {
                this.notification.add(refus, { type: "danger" });
                return;
            }
            return await action();
        } finally {
            this.aiteGestesEnCours--;
            this.aiteFinDeGeste();
        }
    },

    /** Fin d'un geste (ou d'une fenêtre ouverte par un geste) : verrouille le
     * plan, sauf si un autre geste a commencé entre-temps (la fenêtre de
     * fermeture ferme tout puis se rouvre après une sortie d'espèces) ;
     * `abandon`, s'il est donné, est alors appelé aussi. */
    aiteFinDeGeste(abandon = null) {
        setTimeout(() => {
            if (!this.aiteGestesEnCours) {
                abandon?.();
                this.aiteVerrouillerSurPlan();
            }
        }, 0);
    },

    /** La fenêtre d'ouverture ou de fermeture est abandonnée : le code tapé
     * n'autorise plus rien sur le serveur (`aite_abandonner_code`). Hors
     * connexion, l'autorisation reste ; elle ne sert qu'à la fenêtre
     * suivante, qui redemande le code. */
    aiteAbandonnerCode() {
        this.data
            .call("pos.session", "aite_abandonner_code", [[this.session.id]])
            .catch((erreur) => {
                if (!(erreur instanceof ConnectionLostError)) {
                    throw erreur;
                }
            });
    },

    /** Requête à code vérifiée par le serveur (ouverture, fermeture). Rend
     * la réponse, ou faux après avoir affiché le refus (R1, R3, R13), ou R27
     * hors connexion. */
    async aiteRequeteCode(methode, code, geste) {
        let reponse;
        try {
            reponse = await this.data.call("pos.session", methode, [[this.session.id], code]);
        } catch (erreur) {
            if (erreur instanceof ConnectionLostError) {
                this.notification.add(MESSAGES.R27(geste), { type: "danger" });
                return false;
            }
            if (erreur instanceof RPCError && erreur.data?.message) {
                this.notification.add(erreur.data.message, { type: "danger" });
                return false;
            }
            throw erreur;
        }
        if (reponse?.erreur) {
            this.notification.add(reponse.erreur, { type: "danger" });
            return false;
        }
        return reponse;
    },

    // ------------------------------------------------------------------
    // Le plan verrouillé, écran de repos
    // ------------------------------------------------------------------

    get firstScreen() {
        const ecran = super.firstScreen;
        return this.aiteActif ? "FloorScreen" : ecran;
    },

    /** Point de passage unique. Synchrone : quand un code est à demander (ou
     * l'état de la caisse à relire), la fenêtre est lancée, `false` est rendu,
     * puis l'écran est rouvert par le même chemin une fois la personne
     * identifiée. La fenêtre s'ouvre après la pile en cours : les onglets
     * d'Odoo appellent `dialog.closeAll()` juste après `showScreen`, ce qui
     * la refermerait aussitôt (OrderTabs.selectFloatingOrder). */
    showScreen(name, props) {
        if (!this.aiteActif) {
            return super.showScreen(...arguments);
        }
        if (name === "SaverScreen") {
            return false; // plus d'écran de veille : le plan reste affiché
        }
        if (name === "LoginScreen") {
            name = "FloorScreen";
            props = undefined;
        }
        if (name === "FloorScreen") {
            if (!this.isOrderTransferMode) {
                this.aiteVerrouiller();
            }
            return super.showScreen(name, props);
        }
        if (!ECRANS_A_CODE.includes(name)) {
            return super.showScreen(name, props);
        }
        // Avant l'ouverture de la caisse, pas d'écran de commande ni de
        // paiement (R3), quel que soit le chemin (numéro tapé dans « Table »,
        // onglet) ; l'état est relu sur le serveur (un autre poste a pu
        // ouvrir la caisse).
        if (name !== "TicketScreen" && this.session.state === "opening_control") {
            this.aiteCaisseOuverte().then((ouverte) => {
                if (ouverte) {
                    this.showScreen(name, props);
                } else {
                    this.notification.add(MESSAGES.R3, { type: "danger" });
                    this.aiteOublierAdditionVide();
                    this.showScreen("FloorScreen");
                }
            });
            return false;
        }
        const order = this.get_order();
        if (!this.cashier) {
            Promise.resolve()
                .then(() => this.aiteIdentifier({ titre: this.aiteTitreEcran(name, order) }))
                .then((employe) => {
                    if (employe) {
                        this.showScreen(name, props);
                    }
                });
            return false;
        }
        const permis = this.aiteEcranPermis(name, order);
        if (permis !== name) {
            return this.showScreen(permis);
        }
        return super.showScreen(name, props);
    },

    /** Les contrôles du point de passage pour la personne identifiée : rend
     * l'écran à afficher à la place de `name` (ou `name`).
     * - Q19 : la table d'un collègue (« ouverte par » arrive à
     *   l'incrément 3) → R4, le plan ;
     * - l'écran de paiement sans le droit d'encaisser (écran mémorisé sur
     *   l'addition, onglet, liste des commandes, prise de main) → l'écran de
     *   commande. */
    aiteEcranPermis(name, order) {
        const ouvertePar = order?.aite_ouverte_par_id;
        if (ouvertePar && ouvertePar.id !== this.cashier.id && !this.aitePeut("table_collegue")) {
            this.notification.add(MESSAGES.R4(this.aiteNomAddition(order), ouvertePar.name), {
                type: "danger",
            });
            return "FloorScreen";
        }
        if (name === "PaymentScreen" && !this.aitePeut("encaisser")) {
            return "ProductScreen";
        }
        return name;
    },

    /** Prise en main par le nom en haut : l'écran affiché repasse par les
     * contrôles du point de passage pour la nouvelle personne (une serveuse
     * qui reprend la main sur le paiement revient à l'écran de commande). */
    aiteApresPriseEnMain() {
        const ecran = this.mainScreen.component?.name;
        if (!this.aiteActif || !this.cashier || !ECRANS_A_CODE.includes(ecran)) {
            return;
        }
        const permis = this.aiteEcranPermis(ecran, this.get_order());
        if (permis !== ecran) {
            this.showScreen(permis);
        }
    },

    /** Vrai si la caisse est ouverte. Le poste peut la croire fermée alors
     * qu'un autre poste l'a ouverte : l'état est alors relu sur le serveur,
     * et mis à jour sur ce poste. Hors connexion : l'état connu du poste. */
    async aiteCaisseOuverte() {
        if (this.session.state !== "opening_control") {
            return true;
        }
        try {
            const [session] = await this.data.call("pos.session", "read", [
                [this.session.id],
                ["state"],
            ]);
            if (session && session.state !== "opening_control") {
                this.session.state = session.state;
                return true;
            }
        } catch (erreur) {
            if (!(erreur instanceof ConnectionLostError)) {
                throw erreur;
            }
        }
        return false;
    },

    /** Après R3 : l'addition sans table créée par un numéro tapé, vide et
     * jamais enregistrée, ne reste pas dans les onglets. */
    aiteOublierAdditionVide() {
        const order = this.get_order();
        if (order && !order.table_id && !order.lines.length && typeof order.id !== "number") {
            this.removeOrder(order, false);
        }
    },

    aiteNomAddition(order) {
        return (
            order?.table_id?.table_number ??
            order?.getFloatingOrderName?.() ??
            order?.floating_order_name ??
            ""
        );
    },

    aiteTitreEcran(name, order) {
        if (name === "TicketScreen") {
            return TITRES.commandes;
        }
        const numero = this.aiteNomAddition(order);
        return numero ? TITRES.table(numero) : TITRES.prendreLaMain;
    },

    async showLoginScreen() {
        if (!this.aiteActif) {
            return super.showLoginScreen(...arguments);
        }
        // Le cadenas et le « Retour » du contrôle d'ouverture d'Odoo mènent
        // au plan verrouillé.
        this.showScreen("FloorScreen");
        this.dialog.closeAll();
    },

    /** Un rechargement de la page verrouille : on ne reprend pas l'employé
     * gardé par le navigateur. */
    _getConnectedCashier() {
        if (this.aiteActif) {
            return false;
        }
        return super._getConnectedCashier(...arguments);
    },

    /** Une seule étape : après 5 minutes sans toucher l'écran, fenêtres
     * fermées et retour au plan verrouillé (T10 ; écart à Q17, partie 0.4).
     * Le délai d'Odoo (3 minutes, restaurant) et l'écran de veille
     * disparaissent. Exception : l'écran de paiement avec un paiement
     * commencé. */
    get idleTimeout() {
        if (!this.aiteActif) {
            return super.idleTimeout;
        }
        return [
            {
                timeout: (this.session._aite_delai_retour_plan || 300) * 1000,
                action: () => this.aiteRetourAuPlanSansActivite(),
            },
        ];
    },

    aiteRetourAuPlanSansActivite() {
        const ecran = this.mainScreen.component?.name;
        if (ecran === "PaymentScreen" && this.get_order()?.payment_ids?.length) {
            return false;
        }
        this.dialog.closeAll();
        if (this.isOrderTransferMode) {
            // Le déplacement est abandonné : la table touchée ensuite sur le
            // plan ne recevra pas l'addition (transferOrder).
            this.aiteTransfertAbandonne = true;
            this.isOrderTransferMode = false;
        }
        this.showScreen("FloorScreen");
        return false; // la minuterie d'Odoo ne passe pas en « inactif »
    },

    // ------------------------------------------------------------------
    // Garde-fous : sans employé identifié, pos_hr lit `cashier._role` et
    // `cashier.user_id` (menu ≡ ouvert sur le plan verrouillé)
    // ------------------------------------------------------------------

    get employeeIsAdmin() {
        if (this.aiteActif && !this.cashier) {
            return false;
        }
        return super.employeeIsAdmin;
    },

    get_cashier_user_id() {
        if (this.aiteActif && !this.cashier) {
            return null;
        }
        return super.get_cashier_user_id(...arguments);
    },

    cashierHasPriceControlRights() {
        if (this.aiteActif && !this.cashier) {
            return false;
        }
        return super.cashierHasPriceControlRights(...arguments);
    },

    // ------------------------------------------------------------------
    // Les gestes réservés
    // ------------------------------------------------------------------

    /** Le matin : la fenêtre du code s'ouvre d'elle-même à l'affichage du
     * plan (Odoo appelle cette méthode au montage du plan), et le bouton du
     * bandeau « Ouvrir la caisse » la rappelle. Le serveur vérifie le code
     * (`aite_ouvrir_caisse` ; R3, R27) ; puis vient le contrôle d'ouverture
     * d'Odoo (fond de caisse) ; à sa fermeture, le plan se verrouille
     * (opening_control_popup.js). Rien hors du plan. Une caisse déjà ouverte
     * par un autre poste ne redemande rien : l'état est relu sur le serveur
     * avant la fenêtre, et le serveur le dit aussi au code tapé. */
    async openOpeningControl() {
        if (!this.aiteActif) {
            return super.openOpeningControl(...arguments);
        }
        if (
            this.session.state !== "opening_control" ||
            this.aiteOuvertureEnCours ||
            this.mainScreen.component?.name !== "FloorScreen"
        ) {
            return;
        }
        this.aiteOuvertureEnCours = true;
        try {
            this.aiteVerrouiller();
            if (await this.aiteCaisseOuverte()) {
                return;
            }
            let reponse = null;
            const employe = await this.aiteIdentifier({
                titre: TITRES.ouvrir,
                verifier: async (_employe, code) =>
                    (reponse = await this.aiteRequeteCode(
                        "aite_ouvrir_caisse",
                        code,
                        "ouvrir la caisse"
                    )),
            });
            if (!employe) {
                return;
            }
            if (reponse?.deja_ouverte) {
                this.session.state = "opened";
                this.aiteVerrouiller();
                return;
            }
            this.hasLoggedIn = true;
            return super.openOpeningControl(...arguments);
        } finally {
            this.aiteOuvertureEnCours = false;
        }
    },

    /** Fermer la caisse : le code d'un chef de salle ou du manager, vérifié
     * par le serveur (`aite_fermer_caisse` ; R13, R27), puis la fenêtre de
     * fermeture d'Odoo. Le code déjà tapé pendant la visite sert s'il en a
     * le droit (une seule saisie, T3). */
    async closeSession() {
        if (!this.aiteActif) {
            return super.closeSession(...arguments);
        }
        // Le compteur retient le verrou du plan pendant que cette méthode
        // tourne ; une fois ouverte, la fenêtre de fermeture le retient à son
        // tour et verrouille le plan à sa disparition (closing_popup.js).
        this.aiteGestesEnCours = (this.aiteGestesEnCours || 0) + 1;
        let fenetreOuverte = false;
        try {
            const verifier = (_employe, code) =>
                this.aiteRequeteCode("aite_fermer_caisse", code, "fermer la caisse");
            let autorise;
            if (this.cashier && this.aiteCodeVisite && this.aitePeut("fermer_caisse")) {
                autorise = await verifier(this.cashier, this.aiteCodeVisite);
            } else {
                autorise = await this.aiteIdentifier({ titre: TITRES.fermer, verifier });
            }
            if (!autorise) {
                return;
            }
            const resultat = await super.closeSession(...arguments);
            fenetreOuverte = true;
            return resultat;
        } finally {
            this.aiteGestesEnCours--;
            if (!fenetreOuverte) {
                this.aiteFinDeGeste();
            }
        }
    },

    /** Entrée ou sortie d'espèces : code si personne n'est identifié ; sans
     * le droit, R15 (le serveur vérifie aussi, `try_cash_in_out`). */
    async cashMove() {
        if (!this.aiteActif) {
            return super.cashMove(...arguments);
        }
        return this.aiteGeste({
            titre: TITRES.especes,
            geste: "especes",
            refus: MESSAGES.R15,
            action: () => super.cashMove(...arguments),
        });
    },

    /** « J'encaisse » : une personne qui n'encaisse pas fait taper le code
     * de la caissière, dans la même fenêtre ; un autre code de serveur est
     * refusé (R10) et la fenêtre attend. La caissière reste identifiée
     * jusqu'au verrou (« encaissée par » = elle). */
    async pay() {
        if (!this.aiteActif || this.aitePeut("encaisser")) {
            return super.pay(...arguments);
        }
        const nom = this.cashier?.name;
        const employe = await this.aiteIdentifier({
            titre: TITRES.encaisser,
            sousTitre: nom ? TEXTES.neSaitPasEncaisser(nom) : "",
            verifier: (personne) => {
                if (this.aiteEmployePeut(personne, "encaisser")) {
                    return true;
                }
                this.notification.add(MESSAGES.R10, { type: "danger" });
                return false;
            },
        });
        if (!employe) {
            return;
        }
        return super.pay(...arguments);
    },

    /** Toucher une table depuis le plan demande toujours le code (T1), sauf
     * la table d'arrivée d'un « Déplacer ou réunir ». Avant l'ouverture de
     * la caisse : R3, après avoir relu l'état sur le serveur. Depuis l'écran de commande (sélecteur « Table »), la
     * personne identifiée continue ; `showScreen` contrôle la table d'un
     * collègue. */
    async setTableFromUi(table, orderUuid = null) {
        if (!this.aiteActif) {
            return super.setTableFromUi(...arguments);
        }
        if (this.session.state === "opening_control") {
            if (this.aiteRelectureEnCours) {
                return; // second toucher pendant la relecture
            }
            this.aiteRelectureEnCours = true;
            try {
                if (!(await this.aiteCaisseOuverte())) {
                    this.notification.add(MESSAGES.R3, { type: "danger" });
                    return;
                }
            } finally {
                this.aiteRelectureEnCours = false;
            }
        }
        if (this.mainScreen.component?.name === "FloorScreen") {
            if (this.aiteSuiteTransfert) {
                this.aiteSuiteTransfert = false;
            } else {
                if (this.aiteIdentificationEnCours) {
                    return; // second toucher pendant que la fenêtre est ouverte
                }
                const tete = table.parent_id ? table.getParent() : table;
                this.aiteVerrouiller();
                const employe = await this.aiteIdentifier({
                    titre: TITRES.table(tete.table_number),
                });
                if (!employe) {
                    return;
                }
            }
        }
        return super.setTableFromUi(...arguments);
    },

    /** « Déplacer ou réunir » : la table d'arrivée s'ouvre sans code (la
     * même personne continue). Un déplacement abandonné au retour au plan
     * sans activité ne transfère rien : Odoo laisse son écouteur de clic en
     * place, et la table touchée ensuite sur le plan verrouillé recevrait
     * l'addition. Le drapeau d'abandon ne vaut que pour ce premier toucher :
     * il est retombé si ce toucher n'est pas une table, et à chaque nouveau
     * déplacement (control_buttons.js). */
    async transferOrder(orderUuid, destinationTable) {
        if (!this.aiteActif) {
            return super.transferOrder(...arguments);
        }
        if (this.aiteTransfertAbandonne) {
            // Odoo appelle ensuite setTableFromUi : la fenêtre du code ouverte
            // par le toucher de la table le tient (un seul code demandé).
            this.aiteTransfertAbandonne = false;
            return;
        }
        await super.transferOrder(...arguments);
        this.aiteSuiteTransfert = true;
    },
});
