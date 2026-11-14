/* global Sha1, luxon */
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
 *
 * Incrément 3 — la table :
 * - une table libre demande le nombre de personnes, dans la même fenêtre que
 *   le code, après avoir relu l'état des tables sur le serveur ; l'addition
 *   est enregistrée aussitôt, sans produit, « ouverte par » la personne
 *   identifiée ;
 * - l'addition quittée (retour au plan, autre table, autre code, onglet,
 *   liste des commandes, numéro tapé, « + ») est enregistrée au nom de la
 *   personne qui l'a remplie, avant tout changement d'identité (T19) ; la
 *   caisse envoie au serveur la personne identifiée et le déplacement en
 *   cours (division, réunion), pour le journal des saisies ;
 * - « Déplacer ou réunir » : la table d'un collègue (R19), les personnes qui
 *   s'additionnent et l'heure la plus ancienne, une part portée sur une table
 *   libre (étape personnes) ;
 * - un numéro qui n'est pas sur le plan ouvre une table à ce nom (code,
 *   personnes) ; la vente sans table (« + ») suit la case de la caisse.
 *
 * Incrément 4 — annuler ce qui est parti :
 * - tout produit compte comme « à envoyer », même d'une famille sans
 *   imprimante (REST-10 critère 4) ;
 * - une seule fenêtre (`AiteAnnulationPopup`) pour annuler un produit
 *   envoyé, une table qui a des produits envoyés (« Annuler la table », la
 *   corbeille de « Commandes ») et les tables encore ouvertes à la
 *   fermeture : combien, le code d'un responsable vérifié par le serveur, le
 *   motif ; la personne identifiée ne change pas ; une clé de demande par
 *   annulation, gardée jusqu'à ce que la baisse soit appliquée (un nouvel
 *   essai après R27 la réutilise) ;
 * - l'addition absorbée par « Déplacer ou réunir » est signalée au serveur
 *   avant d'être annulée (`aite_marquer_fusion`) : ce n'est pas une
 *   annulation.
 */
import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { makeAwaitable } from "@point_of_sale/app/store/make_awaitable_dialog";
import { ConnectionLostError, RPCError } from "@web/core/network/rpc";
import { deserializeDateTime, serializeDateTime } from "@web/core/l10n/dates";
import { uuidv4 } from "@point_of_sale/utils";
import { getOrderChanges } from "@point_of_sale/app/models/utils/order_change";
// Fixe l'ordre des patchs : ceux de pos_hr et du restaurant d'abord.
import "@pos_hr/overrides/models/pos_store";
import "@pos_restaurant/overrides/models/pos_store";
import { AiteCodePopup } from "@aite_pos_restaurant/components/code_popup/code_popup";
import { AiteAnnulationPopup } from "@aite_pos_restaurant/components/annulation_popup/annulation_popup";
import { MESSAGES, TEXTES, TITRES } from "@aite_pos_restaurant/utils/messages";
import { partEnvoyee, quantiteEnvoyee } from "@aite_pos_restaurant/utils/envoi";

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

    /** Ouvre la fenêtre du code, sans identifier personne. `verifier(employe,
     * code)`, s'il est donné, peut refuser la personne : la fenêtre reste
     * alors ouverte pour un autre code. `personnes(employe)`, s'il est donné,
     * est appelé une fois le code reconnu : s'il rend un titre, la même
     * fenêtre passe à l'étape « personnes » (table libre). Rend
     * `{employe, code, personnes}`, ou faux (« Retour »). Une seule fenêtre à
     * la fois : un second appel pendant qu'elle est ouverte rend faux. */
    async aiteDemanderCode({ titre, sousTitre = "", verifier = null, personnes = null } = {}) {
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
                ...(personnes ? { etapePersonnes: personnes } : {}),
            });
            return resultat?.employe ? resultat : false;
        } finally {
            this.aiteIdentificationEnCours = false;
        }
    },

    /** La fenêtre du code ; la personne reconnue devient l'employé du poste
     * (`aiteDevenir`). Rend l'employé, ou faux (« Retour »). */
    async aiteIdentifier(options = {}) {
        const resultat = await this.aiteDemanderCode(options);
        if (!resultat) {
            return false;
        }
        await this.aiteDevenir(resultat.employe, resultat.code);
        return resultat.employe;
    },

    /** `employe` devient l'employé du poste (`set_cashier`) et son code est
     * gardé jusqu'au verrou suivant (T3). Si une autre personne était
     * identifiée, l'addition en cours est d'abord enregistrée à son nom
     * (T19) : ce qu'elle a saisi ne passe pas au nom de la suivante. */
    async aiteDevenir(employe, code) {
        if (this.cashier && this.cashier.id !== employe.id) {
            await this.aiteQuitterAddition();
        }
        this.set_cashier(employe);
        this.aiteCodeVisite = code;
    },

    /** L'étape « personnes » seule (bouton « 4 personnes », table libre
     * touchée depuis l'écran de commande, part portée sur une table libre,
     * numéro tapé) : rend un entier ≥ 1, ou faux (« Retour »). */
    async aiteDemanderPersonnes(titre) {
        if (this.aiteIdentificationEnCours) {
            return false;
        }
        this.aiteIdentificationEnCours = true;
        try {
            const resultat = await makeAwaitable(this.dialog, AiteCodePopup, {
                titre,
                etape: "personnes",
            });
            return resultat?.personnes || false;
        } finally {
            this.aiteIdentificationEnCours = false;
        }
    },

    // ------------------------------------------------------------------
    // L'addition enregistrée au nom de qui l'a remplie (T19)
    // ------------------------------------------------------------------

    /** Vrai si l'addition a changé depuis son dernier enregistrement sur le
     * serveur (ou n'y a jamais été enregistrée alors qu'elle est ouverte). */
    aiteAModifier(order) {
        if (!order || order.finalized) {
            return false;
        }
        if (typeof order.id !== "number") {
            return Boolean(order.isBooked || order.lines.length);
        }
        const commandes = this.models.commands || {};
        if (
            this.pendingOrder.write.has(order.id) ||
            commandes["pos.order"]?.update.has(order.id) ||
            order.getCommand("delete", "lines") ||
            order.getCommand("unlink", "lines")
        ) {
            return true;
        }
        return order.lines.some(
            (line) =>
                typeof line.id !== "number" || commandes["pos.order.line"]?.update.has(line.id)
        );
    },

    /** Attend la fin d'une synchronisation déjà en cours de l'addition : Odoo
     * écarterait la suivante (`syncAllOrders` ne reprend pas une addition en
     * cours d'envoi). */
    async aiteAttendreSynchro(order) {
        const fin = Date.now() + 10000;
        while (order && this.syncingOrders.has(order.id) && Date.now() < fin) {
            await new Promise((resolve) => setTimeout(resolve, 50));
        }
    },

    /** Enregistre l'addition sur le serveur, au nom de la personne identifiée
     * à l'instant de l'appel (`employe`) : le serveur écrit le journal des
     * saisies à ce nom. `deplacement` : division ou réunion en cours (ni
     * saisie, ni retrait). */
    async aiteSynchroniser(
        order,
        { employe = this.cashier, deplacement = this.aiteDeplacementEnCours } = {}
    ) {
        if (!order) {
            return;
        }
        const context = {
            aite_employee_id: employe?.id || false,
            aite_deplacement: Boolean(deplacement),
        };
        await this.aiteAttendreSynchro(order);
        return this.syncAllOrders({ orders: [order], context });
    },

    /** Avant tout verrou, tout changement d'addition courante et toute
     * nouvelle identification : l'addition quittée, si elle a changé, est
     * enregistrée au nom de la personne identifiée à l'instant de l'appel
     * (T19), même si le poste se verrouille aussitôt après. Une
     * synchronisation déjà en cours est d'abord attendue : si elle a tout
     * emporté, rien n'est renvoyé. */
    async aiteQuitterAddition(order = this.get_order()) {
        if (!this.aiteActif || !this.aiteAModifier(order)) {
            return;
        }
        const employe = this.cashier || null; // pris à l'appel, avant tout verrou
        await this.aiteAttendreSynchro(order);
        if (!this.aiteAModifier(order)) {
            return;
        }
        return this.aiteSynchroniser(order, { employe, deplacement: false });
    },

    /** L'addition courante change (onglet, liste des commandes, sélecteur
     * « Table », numéro tapé, « + », prise de la table suivante) : celle qu'on
     * quitte est enregistrée au nom de la personne identifiée (T19, revue de
     * l'incrément 3). Sinon elle partirait plus tard, avec la synchronisation
     * de toutes les additions d'Odoo, au nom de la personne identifiée à ce
     * moment-là. Rien pendant « Déplacer ou réunir » ni une division, qui
     * enregistrent elles-mêmes ce qui a été saisi avant le déplacement ; rien
     * sur le plan verrouillé (l'addition a été enregistrée au verrou). */
    aiteAvantChangementDAddition(nouvelle) {
        const precedente = this.get_order();
        if (
            this.aiteActif &&
            this.cashier &&
            precedente &&
            precedente.uuid !== nouvelle?.uuid &&
            !this.aiteDeplacementEnCours &&
            !this.isOrderTransferMode
        ) {
            this.aiteQuitterAddition(precedente);
        }
    },

    set_order(order) {
        this.aiteAvantChangementDAddition(order);
        return super.set_order(...arguments);
    },

    add_new_order() {
        this.aiteAvantChangementDAddition(null);
        return super.add_new_order(...arguments);
    },

    /** La personne identifiée et le déplacement en cours, envoyés avec chaque
     * synchronisation (journal des saisies). Une valeur passée par l'appelant
     * (`aiteSynchroniser`) l'emporte. */
    getSyncAllOrdersContext(orders, options = {}) {
        const context = super.getSyncAllOrdersContext(...arguments);
        if (!this.aiteActif) {
            return context;
        }
        return {
            aite_employee_id: this.cashier?.id || false,
            aite_deplacement: Boolean(this.aiteDeplacementEnCours),
            ...context,
        };
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
                // L'addition quittée est enregistrée au nom de qui l'a remplie
                // (la personne est prise à l'appel), puis le poste se verrouille.
                this.aiteQuitterAddition();
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
            const message = this.aiteEstVenteSansTable(order)
                ? MESSAGES.R4vente(order.getFloatingOrderName(), ouvertePar.name)
                : MESSAGES.R4(this.aiteNomAddition(order), ouvertePar.name);
            this.notification.add(message, { type: "danger" });
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

    /** Une vente sans table (« + ») : ni table, ni nom (numéro tapé, part
     * « 12B »), ni personne. Son onglet porte son numéro de suivi, qu'Odoo
     * donne à toute addition : ce n'est pas un numéro de table (revue de
     * l'incrément 3). */
    aiteEstVenteSansTable(order) {
        return Boolean(
            order &&
                !order.table_id &&
                !order.floating_order_name &&
                !order.aite_origine_uuid &&
                !(order.customer_count >= 1)
        );
    },

    aiteTitreEcran(name, order) {
        if (name === "TicketScreen") {
            return TITRES.commandes;
        }
        if (this.aiteEstVenteSansTable(order)) {
            return TITRES.venteSansTable(order.getFloatingOrderName());
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
        if (this.aiteAnnulationEnvoi) {
            return false; // une annulation en cours d'envoi au serveur (partie 1.3)
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
     * la caisse : R3, après avoir relu l'état sur le serveur. Depuis l'écran
     * de commande (sélecteur « Table »), la personne identifiée continue,
     * après avoir enregistré l'addition qu'elle quitte ; `showScreen`
     * contrôle la table d'un collègue.
     *
     * Une table libre (incrément 3) : l'état des tables est relu sur le
     * serveur (un autre poste a pu l'ouvrir), puis le nombre de personnes est
     * demandé — dans la fenêtre du code depuis le plan, seul depuis l'écran
     * de commande ; « Retour » n'ouvre rien. L'addition est alors posée à ce
     * nombre, « ouverte par » la personne identifiée, réservée (occupée sur
     * tous les postes, même sans produit) et enregistrée aussitôt : le
     * serveur pose l'heure d'ouverture. */
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
        if (this.aiteRetourApresTransfert) {
            return this.aiteRevenirApresTransfert();
        }
        const tete = table.parent_id ? table.getParent() : table;
        let personnes = 0;
        if (this.mainScreen.component?.name === "FloorScreen") {
            if (this.aiteSuiteTransfert) {
                this.aiteSuiteTransfert = false;
            } else {
                if (this.aiteIdentificationEnCours) {
                    return; // second toucher pendant que la fenêtre est ouverte
                }
                this.aiteVerrouiller();
                const resultat = await this.aiteDemanderCode({
                    titre: TITRES.table(tete.table_number),
                    personnes: () => this.aiteEtapePersonnes(tete),
                });
                if (!resultat) {
                    return;
                }
                await this.aiteDevenir(resultat.employe, resultat.code);
                personnes = resultat.personnes;
            }
        } else {
            if (this.aiteIdentificationEnCours) {
                return;
            }
            await this.aiteQuitterAddition();
            const titre = await this.aiteEtapePersonnes(tete);
            if (titre) {
                personnes = await this.aiteDemanderPersonnes(titre);
                if (!personnes) {
                    return; // « Retour » : on reste sur l'addition en cours
                }
            }
        }
        const resultat = await super.setTableFromUi(...arguments);
        if (personnes) {
            await this.aiteOuvrirLAddition(this.get_order(), personnes, tete);
        }
        return resultat;
    },

    /** Vrai si la table (ou sa table parente) n'a aucune addition ouverte sur
     * ce poste. */
    aiteTableLibre(tete) {
        return !this.getActiveOrdersOnTable(tete).length;
    },

    /** Avant l'étape « personnes » : la table semble libre ? L'état des
     * tables est relu sur le serveur (Odoo ne l'attend pas), et l'étape n'a
     * lieu que si elle l'est toujours, hors déplacement. Rend le titre de
     * l'étape, ou faux. Si la relecture échoue (hors connexion), l'état
     * connu du poste fait foi. */
    async aiteEtapePersonnes(tete) {
        if (this.isOrderTransferMode || !this.aiteTableLibre(tete)) {
            return false;
        }
        try {
            await this.deviceSync.readDataFromServer();
        } catch (erreur) {
            console.warn("Restaurant : relecture des tables impossible", erreur);
        }
        return this.aiteTableLibre(tete) ? TITRES.personnes(tete.table_number) : false;
    },

    /** Une addition qui s'ouvre (table libre, numéro tapé, part portée sur une
     * table libre) : son nombre de personnes, « ouverte par » la personne
     * identifiée, réservée, puis enregistrée aussitôt. */
    async aiteOuvrirLAddition(order, personnes, tete = null) {
        if (!order || order.finalized || (tete && order.table_id?.id !== tete.id)) {
            return;
        }
        order.setCustomerCount(personnes);
        if (!order.aite_ouverte_par_id) {
            order.update({ aite_ouverte_par_id: this.cashier });
        }
        order.setBooked(true);
        await this.aiteSynchroniser(order);
    },

    /** Odoo reprend, pour une table touchée, une addition sans table et sans
     * produit : en mode, seulement une addition résiduelle (jamais
     * enregistrée, jamais réservée, sans nom), pas un numéro tapé, une vente
     * sans table ni une part encore vides. Sinon une addition neuve est
     * posée sur la table, et Odoo la retrouve. */
    async setTable(table, orderUuid = null) {
        if (
            this.aiteActif &&
            table &&
            !table.orders.some((o) => o.uuid === orderUuid || !o.finalized)
        ) {
            const residuelle = this.models["pos.order"].find(
                (o) =>
                    !o.table_id &&
                    !o.finalized &&
                    o.lines.length === 0 &&
                    !o.isBooked &&
                    !o.floating_order_name &&
                    !o.aite_ouverte_par_id
            );
            if (residuelle) {
                residuelle.update({ table_id: table });
            } else {
                this.selectedTable = table;
                this.add_new_order();
            }
        }
        return super.setTable(...arguments);
    },

    /** « Déplacer ou réunir » : la table d'arrivée s'ouvre sans code (la
     * même personne continue). Un déplacement abandonné au retour au plan
     * sans activité ne transfère rien : Odoo laisse son écouteur de clic en
     * place, et la table touchée ensuite sur le plan verrouillé recevrait
     * l'addition. Le drapeau d'abandon ne vaut que pour ce premier toucher :
     * il est retombé si ce toucher n'est pas une table, et à chaque nouveau
     * déplacement (control_buttons.js).
     *
     * Incrément 3 :
     * - la table d'un collègue (R19) : rien n'est réuni, retour à l'addition ;
     * - ce qui a été saisi est d'abord enregistré (journal des saisies), puis
     *   le déplacement est signalé au serveur : ni saisie, ni retrait ;
     * - table d'arrivée occupée : les personnes s'additionnent et l'heure
     *   d'ouverture la plus ancienne est gardée (Q29) ;
     * - une addition sans table et sans personne (part « 12B », vente sans
     *   table) portée sur une table libre : l'étape personnes seule ;
     *   « Retour » : rien n'est déplacé. */
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
        const order = this.models["pos.order"].getBy("uuid", orderUuid);
        const destination = this.getActiveOrdersOnTable(destinationTable)[0];
        const reunion = Boolean(destination && order && destination !== order);
        const collegue = reunion ? destination.aite_ouverte_par_id : null;
        if (collegue && collegue.id !== this.cashier?.id && !this.aitePeut("table_collegue")) {
            this.notification.add(MESSAGES.R19(destinationTable.table_number, collegue.name), {
                type: "danger",
            });
            this.aiteRetourApresTransfert = orderUuid;
            return;
        }
        let personnes = 0;
        if (order && !destination && !order.table_id && !(order.customer_count >= 1)) {
            personnes = await this.aiteDemanderPersonnes(
                TITRES.personnes(destinationTable.table_number)
            );
            if (!personnes) {
                this.aiteRetourApresTransfert = orderUuid;
                return;
            }
        }
        await this.aiteQuitterAddition(order);
        const personnesSource = order?.customer_count || 0;
        const heureSource = order?.aite_heure_ouverture;
        if (personnes) {
            // Avant Odoo, qui enregistre l'addition sur sa nouvelle table : le
            // serveur ne la reçoit jamais à table avec 0 personne.
            order.setCustomerCount(personnes);
        }
        this.aiteDeplacementEnCours = true;
        try {
            await super.transferOrder(...arguments);
            if (reunion) {
                destination.setCustomerCount((destination.customer_count || 0) + personnesSource);
                if (
                    heureSource &&
                    (!destination.aite_heure_ouverture ||
                        heureSource < destination.aite_heure_ouverture)
                ) {
                    destination.update({ aite_heure_ouverture: heureSource });
                }
                await this.aiteSynchroniser(destination, { deplacement: true });
            }
        } finally {
            this.aiteDeplacementEnCours = false;
        }
        this.aiteSuiteTransfert = true;
    },

    /** Après un déplacement refusé (R19) ou abandonné (« Retour » à l'étape
     * personnes), Odoo touche la table d'arrivée : on revient à l'addition
     * de départ, avec la même personne. */
    aiteRevenirApresTransfert() {
        const uuid = this.aiteRetourApresTransfert;
        this.aiteRetourApresTransfert = null;
        const order = this.models["pos.order"].getBy("uuid", uuid);
        if (!order || order.finalized || !this.cashier) {
            return this.showScreen("FloorScreen");
        }
        this.selectedTable = order.table_id || null;
        this.set_order(order);
        return this.showScreen("ProductScreen");
    },

    // ------------------------------------------------------------------
    // Numéro qui n'est pas sur le plan, vente sans table (incrément 3)
    // ------------------------------------------------------------------

    /** Un numéro tapé qui n'est pas sur le plan ouvre une table à ce nom
     * (Q25, T11) : avant l'ouverture de la caisse, R3 ; sur le plan
     * verrouillé, le code puis le nombre de personnes, dans la même fenêtre ;
     * depuis l'écran de commande, le nombre seul. « Retour » : l'addition
     * neuve est retirée ; depuis l'écran de commande, la même personne
     * revient à l'addition d'avant (`precedente`, celle qui était affichée
     * quand « Table » a été touché), comme pour une table libre du
     * sélecteur ; depuis le plan, le plan reste verrouillé. Puis `ouvrir()`
     * (l'écran de commande d'Odoo). */
    async aiteOuvrirNumero(order, ouvrir, precedente = null) {
        const numero = order.floating_order_name;
        const abandonner = () => {
            this.removeOrder(order, false);
            const avant = precedente && this.models["pos.order"].getBy("uuid", precedente.uuid);
            if (this.cashier && avant && !avant.finalized) {
                this.selectedTable = avant.table_id || null;
                this.set_order(avant);
                return this.showScreen("ProductScreen");
            }
            this.showScreen("FloorScreen");
        };
        if (!(await this.aiteCaisseOuverte())) {
            this.notification.add(MESSAGES.R3, { type: "danger" });
            return abandonner();
        }
        let personnes;
        if (!this.cashier) {
            const resultat = await this.aiteDemanderCode({
                titre: TITRES.table(numero),
                personnes: async () => TITRES.personnes(numero),
            });
            if (!resultat) {
                return abandonner();
            }
            await this.aiteDevenir(resultat.employe, resultat.code);
            personnes = resultat.personnes;
        } else {
            personnes = await this.aiteDemanderPersonnes(TITRES.personnes(numero));
        }
        if (!personnes) {
            return abandonner();
        }
        await this.aiteOuvrirLAddition(order, personnes);
        return ouvrir();
    },

    /** Le « + » (case « Autoriser la vente sans table » cochée) : le code si
     * personne n'est identifié ; il faut le droit « vente_sans_table »
     * (caissière et au-dessus), sinon R17. La vente compte 0 personne (Q76). */
    aiteVenteSansTable(ouvrir) {
        return this.aiteGeste({
            titre: TITRES.prendreLaMain,
            geste: "vente_sans_table",
            refus: MESSAGES.R17,
            action: () => {
                // pos_restaurant ne rend pas l'addition créée : c'est la courante.
                const order = ouvrir() || this.get_order();
                if (order) {
                    order.setCustomerCount(0);
                    order.update({ aite_ouverte_par_id: this.cashier });
                }
                return order;
            },
        });
    },

    // ------------------------------------------------------------------
    // L'écran de commande : phrase d'état
    // ------------------------------------------------------------------

    /** Minutes écoulées depuis l'heure d'ouverture posée par le serveur, ou
     * `null` (pas encore enregistrée). */
    aiteMinutesOuverte(order) {
        const heure = order?.aite_heure_ouverture;
        if (!heure) {
            return null;
        }
        const debut = typeof heure === "string" ? deserializeDateTime(heure) : heure;
        if (!debut?.isValid) {
            return null;
        }
        return Math.max(0, Math.floor(luxon.DateTime.now().diff(debut, "minutes").minutes));
    },

    /** « Table 12 · ouverte par Awa · 35 min ». */
    aiteEtatCommande(order) {
        if (!order) {
            return "";
        }
        const nom = order.table_id?.table_number ?? order.floating_order_name;
        const parties = [nom ? TEXTES.table(nom) : TEXTES.venteSansTable];
        if (order.aite_ouverte_par_id?.name) {
            parties.push(TEXTES.ouvertePar(order.aite_ouverte_par_id.name));
        }
        const minutes = this.aiteMinutesOuverte(order);
        if (minutes !== null) {
            parties.push(TEXTES.duree(minutes));
        }
        return parties.join(" · ");
    },

    // ------------------------------------------------------------------
    // Incrément 4 : ce qui est parti, et son annulation
    // ------------------------------------------------------------------

    /** Tout produit compte comme « à envoyer », même d'une famille sans
     * imprimante (REST-10 critère 4) : sinon il ne serait jamais « parti »,
     * donc jamais verrouillé. L'impression reste filtrée imprimante par
     * imprimante (sendOrderInPreparation ne passe pas par ici). */
    getOrderChanges(skipped = false, order = this.get_order()) {
        if (!this.aiteActif) {
            return super.getOrderChanges(...arguments);
        }
        return getOrderChanges(order, skipped, new Set());
    },

    /** Les lignes de l'addition dont une part est partie en cuisine ou au bar. */
    aiteLignesEnvoyees(order) {
        return (order?.lines || []).filter((line) => partEnvoyee(line) > 0);
    },

    aitePorteDesEnvois(order) {
        return this.aiteLignesEnvoyees(order).length > 0;
    },

    /** R4 si l'addition est celle d'un collègue (Q19), sinon rien. */
    aiteRefusTableDUnCollegue(order) {
        const ouvertePar = order?.aite_ouverte_par_id;
        if (
            !ouvertePar ||
            !this.cashier ||
            ouvertePar.id === this.cashier.id ||
            this.aitePeut("table_collegue")
        ) {
            return null;
        }
        return this.aiteEstVenteSansTable(order)
            ? MESSAGES.R4vente(order.getFloatingOrderName(), ouvertePar.name)
            : MESSAGES.R4(this.aiteNomAddition(order), ouvertePar.name);
    },

    /** Les motifs actifs, lus sur le serveur à l'ouverture de la fenêtre
     * (REST-12 critère 5). Hors connexion : R27, et rien. */
    async aiteMotifs() {
        try {
            return await this.data.call("pos.session", "aite_motifs_annulation", [
                [this.session.id],
            ]);
        } catch (erreur) {
            if (erreur instanceof ConnectionLostError) {
                this.notification.add(MESSAGES.R27(TEXTES.annuler), { type: "danger" });
                return null;
            }
            throw erreur;
        }
    },

    /** La requête de la fenêtre d'annulation (`aite_autoriser_annulation`).
     * Rend la réponse du serveur, `"fermer"` (refus : la fenêtre se ferme) ou
     * `false` (pas de réseau, R27 : la fenêtre reste, la clé est gardée). */
    async aiteDemanderAnnulation({ orderIds, lignes, code, motif_id, commentaire, demande, nature }) {
        this.aiteAnnulationEnvoi = true;
        let reponse;
        try {
            reponse = await this.data.call("pos.order", "aite_autoriser_annulation", [
                orderIds,
                lignes,
                code,
                motif_id,
                commentaire || false,
                this.cashier?.id || false,
                demande,
                nature,
            ]);
        } catch (erreur) {
            if (erreur instanceof ConnectionLostError) {
                this.notification.add(MESSAGES.R27(TEXTES.annuler), { type: "danger" });
                return false;
            }
            if (erreur instanceof RPCError && erreur.data?.message) {
                this.notification.add(erreur.data.message, { type: "danger" });
                return "fermer";
            }
            throw erreur;
        } finally {
            this.aiteAnnulationEnvoi = false;
        }
        if (reponse?.erreur) {
            this.notification.add(reponse.erreur, { type: "danger" });
            return "fermer";
        }
        return reponse;
    },

    /** La fenêtre d'annulation, pour un produit, une table ou les tables à
     * la fermeture. Le code est demandé seulement si la personne identifiée
     * ne peut pas annuler (sinon son code de visite sert, T3) ; le code tapé
     * ne change pas la personne identifiée (REST-11-P1). `requete(choix)`
     * rend ce qui part au serveur. Rend `{reponse, choix}`, ou faux. */
    async aiteFenetreAnnulation({ titre, sousTitre, sousTitreCode, quantites = [], requete }) {
        if (this.aiteAnnulationEnCours) {
            return false;
        }
        this.aiteAnnulationEnCours = true;
        try {
            const motifs = await this.aiteMotifs();
            if (!motifs) {
                return false;
            }
            const codeRequis = !(this.aitePeut("annuler_envoye") && this.aiteCodeVisite);
            let reponse = null;
            const choix = await makeAwaitable(this.dialog, AiteAnnulationPopup, {
                titre,
                sousTitre: (codeRequis ? sousTitreCode : sousTitre) || "",
                quantites,
                codeRequis,
                motifs,
                reconnaitre: (code) => {
                    const employe = this.aiteEmployeParCode(code);
                    if (!employe) {
                        return MESSAGES.R1;
                    }
                    if (!this.aiteEmployePeut(employe, "annuler_envoye")) {
                        this.notification.add(MESSAGES.R8, { type: "danger" });
                        return false;
                    }
                    return employe;
                },
                envoyer: async (demande) => {
                    const resultat = await this.aiteDemanderAnnulation({
                        ...requete(demande),
                        ...demande,
                        code: demande.code || this.aiteCodeVisite,
                    });
                    if (resultat && typeof resultat === "object") {
                        reponse = resultat;
                        return true;
                    }
                    return resultat;
                },
            });
            return choix && reponse ? { reponse, choix } : false;
        } finally {
            this.aiteAnnulationEnCours = false;
        }
    },

    /** Annuler une part envoyée d'une ligne (⌫ ou « +/- » sous ce qui est
     * parti) : la fenêtre, puis la baisse appliquée aussitôt, le bon
     * d'annulation de cette ligne seule, l'enregistrement et la
     * notification. */
    async aiteAnnulerLigne(line) {
        const order = line?.order_id;
        const envoye = line ? partEnvoyee(line) : 0;
        if (!order || envoye <= 0 || this.aiteAnnulationEnCours) {
            return false;
        }
        // Le serveur doit savoir ce qui est parti avant de l'annuler.
        await this.aiteQuitterAddition(order);
        const uuid = line.uuid;
        const produit = line.get_full_product_name();
        order.uiState.aiteDemandes = order.uiState.aiteDemandes || {};
        const demande = (order.uiState.aiteDemandes[uuid] ||= uuidv4());
        const entieres = Array.from({ length: Math.floor(envoye) }, (_v, i) => i + 1);
        const quantites = entieres.at(-1) === envoye ? entieres : [...entieres, envoye];
        const resultat = await this.aiteFenetreAnnulation({
            titre: TITRES.annulerProduit(produit, this.aiteNomAddition(order)),
            sousTitre: TEXTES.dejaEnvoye(envoye),
            sousTitreCode: MESSAGES.R9(envoye, produit),
            quantites,
            requete: (choix) => ({
                orderIds: [order.id],
                lignes: [{ uuid, quantite: choix.quantite || envoye }],
                demande,
                nature: "produit",
            }),
        });
        if (!resultat) {
            return false;
        }
        // Une demande renvoyée (réponse perdue) : la quantité annulée la
        // première fois, que le serveur rend, fait foi.
        const quantite = resultat.reponse.quantites?.[uuid] || resultat.choix.quantite || envoye;
        const ligne = order.lines.find((l) => l.uuid === uuid);
        if (ligne) {
            order.uiState.aiteAutorisation = true;
            try {
                const reste = ligne.get_quantity() - quantite;
                if (reste > 0) {
                    ligne.set_quantity(reste);
                } else {
                    order.removeOrderline(ligne);
                }
            } finally {
                order.uiState.aiteAutorisation = false;
            }
        }
        delete order.uiState.aiteDemandes[uuid];
        const imprime = await this.aiteBonDAnnulation(order, uuid, quantite);
        await this.aiteSynchroniser(order);
        const texte = TEXTES.annulationFaite(quantite, produit, resultat.reponse.superieur_nom);
        this.notification.add(imprime ? `${texte} ${TEXTES.bonEnvoye}` : texte, { type: "info" });
        return true;
    },

    /** Le bon d'annulation de la seule ligne annulée (REST-11 critère 1), et
     * ce qui est parti pour elle mis à jour. Les autres produits de la table
     * pas encore envoyés ne partent pas avec lui (écart à la partie 4.1, qui
     * prévoyait sendOrderInPreparationUpdateLastChange : celui-ci envoie toute
     * l'addition). Ce qui est parti baisse de la quantité annulée, et de rien
     * d'autre : une part de la ligne pas encore envoyée reste à envoyer (revue
     * de l'incrément 4, constat 2). Rend vrai si un bon est sorti. */
    async aiteBonDAnnulation(order, uuid, quantite) {
        const preparation = order.last_order_preparation_change;
        const ligne = order.lines.find((l) => l.uuid === uuid);
        // Ce qui part sur le bon : la quantité annulée, prise sur ce qui est
        // parti pour cette ligne (une entrée par note envoyée), au format des
        // entrées enregistrées, celui du bon d'annulation d'Odoo.
        const annules = [];
        let aRetirer = Number(quantite) || 0;
        for (const [cle, entree] of Object.entries(preparation.lines || {})) {
            if (cle.startsWith(uuid) || entree?.uuid === uuid) {
                const parti = Number(entree?.quantity) || 0;
                const retire = Math.min(parti, aRetirer);
                aRetirer -= retire;
                if (retire > 1e-9) {
                    annules.push({ ...entree, quantity: retire });
                }
                if (ligne && parti - retire > 1e-9) {
                    entree.quantity = parti - retire;
                } else {
                    delete preparation.lines[cle];
                }
            }
        }
        preparation.metadata = {
            ...(preparation.metadata || {}),
            serverDate: serializeDateTime(luxon.DateTime.now()),
        };
        if (ligne) {
            ligne.saved_quantity = ligne.get_quantity();
            ligne.setHasChange(ligne.get_quantity() > quantiteEnvoyee(ligne) + 1e-9);
        }
        let imprime = false;
        if (this.printers_category_ids_set?.size && annules.length) {
            try {
                imprime = await this.printChanges(order, {
                    new: [],
                    cancelled: annules,
                    noteUpdated: [],
                    generalNote: false,
                    modeUpdate: false,
                });
            } catch (erreur) {
                console.info("Restaurant : bon d'annulation non imprimé", erreur);
            }
        }
        return imprime;
    },

    /** Annuler une table qui porte des produits envoyés : une fenêtre (sans
     * « Combien ? »), le code d'un responsable si besoin, le motif. Rend vrai
     * si le serveur a autorisé (l'addition peut alors être annulée). */
    async aiteAnnulerTable(order) {
        if (!this.aitePorteDesEnvois(order)) {
            return true;
        }
        await this.aiteQuitterAddition(order);
        const liste = this.aiteLignesEnvoyees(order)
            .map((line) => TEXTES.envoi(partEnvoyee(line), line.get_full_product_name()))
            .join(", ");
        order.uiState.aiteDemande ||= uuidv4();
        const resultat = await this.aiteFenetreAnnulation({
            titre: TITRES.annulerTable(this.aiteNomAddition(order)),
            sousTitre: TEXTES.dejaEnvoyeListe(liste),
            sousTitreCode: TEXTES.dejaEnvoyeListe(liste),
            requete: () => ({
                orderIds: [order.id],
                lignes: false,
                demande: order.uiState.aiteDemande,
                nature: "table",
            }),
        });
        if (!resultat) {
            return false;
        }
        this.aiteAnnulationsAutorisees.add(order.uuid);
        return true;
    },

    /** À la fermeture, « Annuler ces tables » : une seule fenêtre et un seul
     * motif pour toutes les tables encore ouvertes (REST-10 critère 9). Sans
     * aucun produit envoyé, rien à autoriser. Rend vrai si l'on peut les
     * annuler. */
    async aiteAnnulerTables(orders, ids = []) {
        const ouvertes = orders.filter((o) => !o.finalized);
        if (!ouvertes.some((o) => this.aitePorteDesEnvois(o))) {
            return true;
        }
        for (const order of ouvertes) {
            await this.aiteQuitterAddition(order);
        }
        const identifiants = [
            ...new Set([
                ...ids.filter((id) => typeof id === "number"),
                ...ouvertes.map((o) => o.id).filter((id) => typeof id === "number"),
            ]),
        ];
        this.aiteDemandeFermeture ||= uuidv4();
        const resultat = await this.aiteFenetreAnnulation({
            titre: TITRES.annulerTables(this.aiteListeDesTables(ouvertes, ids)),
            requete: () => ({
                orderIds: identifiants,
                lignes: false,
                demande: this.aiteDemandeFermeture,
                nature: "fermeture",
            }),
        });
        if (!resultat) {
            return false;
        }
        this.aiteDemandeFermeture = null;
        for (const order of ouvertes) {
            this.aiteAnnulationsAutorisees.add(order.uuid);
        }
        return true;
    },

    /** « 4, 5, 99 » : les tables (et numéros) des additions ouvertes connues
     * du serveur (`ids`, à la fermeture) ou qui portent des produits. */
    aiteListeDesTables(orders, ids = []) {
        const noms = orders
            .filter(
                (o) =>
                    !o.finalized &&
                    (ids.includes(o.id) || o.lines.length || o.isBooked || o.table_id)
            )
            .map((o) => String(this.aiteNomAddition(o)))
            .filter(Boolean);
        return [...new Set(noms)]
            .sort((a, b) => a.localeCompare(b, undefined, { numeric: true }))
            .join(", ");
    },

    get aiteAnnulationsAutorisees() {
        if (!this._aiteAnnulationsAutorisees) {
            this._aiteAnnulationsAutorisees = new Set();
        }
        return this._aiteAnnulationsAutorisees;
    },

    /** « Annuler la table » et la corbeille de « Commandes » (T14) : une
     * addition qui porte des produits envoyés ouvre directement notre
     * fenêtre, sans la confirmation d'Odoo ; une addition d'un collègue est
     * refusée (R4). Sans produit envoyé : Odoo. L'addition annulée n'est pas
     * une saisie (drapeau de déplacement posé pendant l'annulation, T19). */
    async onDeleteOrder(order) {
        if (!this.aiteActif || !order) {
            return super.onDeleteOrder(...arguments);
        }
        const refus = this.aiteRefusTableDUnCollegue(order);
        if (refus) {
            this.notification.add(refus, { type: "danger" });
            return false;
        }
        if (!this.aitePorteDesEnvois(order)) {
            return super.onDeleteOrder(...arguments);
        }
        if (!(await this.aiteAnnulerTable(order))) {
            return false;
        }
        const depuisCommandes = this.mainScreen.component?.name === "TicketScreen";
        this.aiteDeplacementEnCours = true;
        try {
            if (!(await this.deleteOrders([order]))) {
                return false;
            }
            order.uiState.displayed = false;
            this.afterOrderDeletion();
        } finally {
            this.aiteDeplacementEnCours = false;
        }
        if (!depuisCommandes) {
            this.showScreen("FloorScreen");
        }
        return true;
    },

    /** Filet pour tous les chemins de `deleteOrders` : une annulation déjà
     * autorisée passe ; l'addition absorbée par une réunion est signalée au
     * serveur ; une addition qui porte encore des produits envoyés ouvre la
     * fenêtre d'annulation. */
    async _onBeforeDeleteOrder(order) {
        if (!this.aiteActif) {
            return super._onBeforeDeleteOrder(...arguments);
        }
        if (this.aiteAnnulationsAutorisees.has(order.uuid)) {
            this.aiteAnnulationsAutorisees.delete(order.uuid);
            return super._onBeforeDeleteOrder(...arguments);
        }
        if (this.aiteDeplacementEnCours) {
            if (typeof order.id === "number") {
                try {
                    await this.data.call("pos.order", "aite_marquer_fusion", [order.id]);
                } catch (erreur) {
                    if (!(erreur instanceof ConnectionLostError)) {
                        throw erreur;
                    }
                }
            }
            return super._onBeforeDeleteOrder(...arguments);
        }
        if (this.aitePorteDesEnvois(order)) {
            if (!(await this.aiteAnnulerTable(order))) {
                return false;
            }
            this.aiteAnnulationsAutorisees.delete(order.uuid);
        }
        return super._onBeforeDeleteOrder(...arguments);
    },
});
