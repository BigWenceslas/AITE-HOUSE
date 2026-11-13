/* global posmodel */
/** Incrément 2 : le code et le plan verrouillé (spécification, partie 6.3).
 * AiteVerrouTour, AiteOuvertureTour, AiteDroitsTour, AitePaiementTour, et
 * AiteArdoiseTour (AH-02, joué seulement si aite_pos_credit est installé) ;
 * puis les tours des correctifs de la revue (prise en main au paiement,
 * déplacement après un abandon, avant l'ouverture, onglets, deux postes à
 * l'ouverture, écart de caisse à la fermeture). */
import * as Chrome from "@point_of_sale/../tests/tours/utils/chrome_util";
import * as Dialog from "@point_of_sale/../tests/tours/utils/dialog_util";
import * as ProductScreen from "@point_of_sale/../tests/tours/utils/product_screen_util";
import * as PaymentScreen from "@point_of_sale/../tests/tours/utils/payment_screen_util";
import * as FloorScreen from "@pos_restaurant/../tests/tours/utils/floor_screen_util";
import * as NumberPopup from "@point_of_sale/../tests/tours/utils/number_popup_util";
import * as Aite from "@aite_pos_restaurant/../tests/tours/aite_util";
import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add("AiteVerrouTour", {
    steps: () =>
        [
            // Démarrage : le plan, verrouillé, sans écran de connexion.
            ...Aite.planVerrouille(),
            // Un code inconnu : R1 dans la fenêtre, les points vidés.
            FloorScreen.clickTable("5"),
            ...Aite.taperCode("9999"),
            ...Aite.codeInconnu(),
            ...Aite.taperCode("1111"),
            ...Aite.ecranCommande(),
            Aite.identifie("Awa"),
            { content: "le nom d'Awa en haut", trigger: ".pos-rightheader .cashier-name" },
            ProductScreen.clickDisplayedProduct("Coca-Cola"),
            Aite.jEnvoie(),
            // Après « J'envoie » : le plan, verrouillé, et la notification.
            ...Aite.planVerrouille(),
            Aite.notificationQuiCommencePar("Envoyé : "),
            { content: "plus de nom en haut", trigger: ".pos-rightheader:not(:has(.cashier-name))" },
            // La table demande de nouveau le code ; « Retour » laisse le plan.
            FloorScreen.clickTable("5"),
            Aite.popupCode(),
            Aite.retour(),
            ...Aite.planVerrouille(),
            // « Déplacer ou réunir » abandonné : le plan reste verrouillé.
            FloorScreen.clickTable("5"),
            ...Aite.taperCode("1111"),
            ...Aite.ecranCommande(),
            Aite.ouvrirActions(),
            {
                content: "« Déplacer ou réunir »",
                trigger: ".modal .control-buttons-modal button:has(.oi-arrow-right)",
                run: "click",
            },
            Aite.verifier(
                "mode déplacement, Awa toujours identifiée",
                () => posmodel.isOrderTransferMode && posmodel.cashier?.name === "Awa"
            ),
            {
                content: "toucher le plan hors d'une table",
                trigger: ".floor-screen .floor-map",
                run: "click",
            },
            ...Aite.planVerrouille(),
            // Menu ≡ utilisable sur le plan verrouillé, sans « Installer l'application ».
            Chrome.clickMenuButton(),
            Aite.menuAvec("Close Register"),
            Aite.menuSans("Install App"),
            // La liste des commandes demande le code ; le retour au plan verrouille.
            Aite.entreeDuMenu("Orders"),
            ...Aite.taperCode("1111"),
            { content: "la liste des commandes", trigger: ".pos .ticket-screen" },
            Aite.identifie("Awa"),
            Chrome.clickPlanButton(),
            ...Aite.planVerrouille(),
            // 5 minutes sans toucher l'écran : une seule étape (un tour ne peut
            // pas attendre ; l'étape d'Odoo est appelée directement).
            Aite.verifier(
                "une seule étape d'inactivité, de 5 minutes",
                () => posmodel.idleTimeout.length === 1 && posmodel.idleTimeout[0].timeout === 300000
            ),
            Aite.verifier("plus d'écran de veille", () => posmodel.showScreen("SaverScreen") === false),
            FloorScreen.clickTable("5"),
            ...Aite.taperCode("1111"),
            ...Aite.ecranCommande(),
            Aite.verifier(
                "5 minutes sans activité sur l'écran de commande",
                () => posmodel.idleTimeout[0].action() === false
            ),
            ...Aite.planVerrouille(),
            // Un déplacement abandonné par l'inactivité : la table touchée
            // ensuite ne reçoit pas l'addition, et une seule fenêtre du code s'ouvre.
            FloorScreen.clickTable("5"),
            ...Aite.taperCode("1111"),
            Aite.ouvrirActions(),
            {
                content: "« Déplacer ou réunir »",
                trigger: ".modal .control-buttons-modal button:has(.oi-arrow-right)",
                run: "click",
            },
            Aite.verifier("mode déplacement", () => posmodel.isOrderTransferMode),
            Aite.verifier("5 minutes sans activité", () => posmodel.idleTimeout[0].action() === false),
            ...Aite.planVerrouille(),
            FloorScreen.clickTable("2"),
            Aite.popupCode(),
            Aite.verifier(
                "une seule fenêtre du code",
                () => document.querySelectorAll(".aite-code-popup").length === 1
            ),
            Aite.retour(),
            ...Aite.planVerrouille(),
        ].flat(),
});

registry.category("web_tour.tours").add("AiteOuvertureTour", {
    steps: () =>
        [
            // Caisse pas encore ouverte : la fenêtre du code s'ouvre d'elle-même.
            Aite.popupCode(),
            ...Aite.taperCode("1111"),
            Aite.notificationDanger("R3"),
            Aite.popupCode(),
            Aite.retour(),
            { content: "le bandeau « caisse fermée »", trigger: ".floor-screen .aite-caisse-fermee" },
            FloorScreen.clickTable("5"),
            Aite.notificationDanger("R3"),
            Aite.pasDePopupCode(),
            {
                content: "« Ouvrir la caisse »",
                trigger: ".aite-caisse-fermee .aite-ouvrir-caisse",
                run: "click",
            },
            ...Aite.taperCode("3333"),
            // Le contrôle d'ouverture d'Odoo : fond prérempli, « J'ouvre la caisse ».
            Dialog.confirm(),
            ...Aite.planVerrouille(),
            { content: "plus de bandeau", trigger: ".floor-screen:not(:has(.aite-caisse-fermee))" },
            Aite.verifier("session ouverte", () => posmodel.session.state === "opened"),
        ].flat(),
});

registry.category("web_tour.tours").add("AiteDroitsTour", {
    steps: () =>
        [
            FloorScreen.clickTable("5"),
            ...Aite.taperCode("1111"),
            ProductScreen.clickDisplayedProduct("Coca-Cola"),
            // Une serveuse touche « J'encaisse » : le code de qui encaisse.
            Aite.jEncaisse(),
            Aite.popupCode(),
            {
                content: "le sous-titre dit qu'Awa n'encaisse pas",
                trigger: ".aite-code-popup .aite-code-sous-titre",
            },
            ...Aite.taperCode("1111"),
            Aite.notificationDanger("R10"),
            ...Aite.taperCode("3333"),
            PaymentScreen.isShown(),
            Aite.identifie("Carine"),
            Chrome.clickPlanButton(),
            ...Aite.planVerrouille(),
            // L'addition s'était arrêtée sur le paiement : une serveuse
            // retrouve l'écran de commande.
            FloorScreen.clickTable("5"),
            ...Aite.taperCode("1111"),
            ...Aite.ecranCommande(),
            Aite.identifie("Awa"),
            // Prise en main par le nom en haut.
            Aite.prendreLaMain(),
            ...Aite.taperCode("5555"),
            Aite.identifie("Fanta"),
            Aite.ouvrirActions(),
            Aite.remboursement(true),
            Aite.fermerFenetre(),
            Aite.prendreLaMain(),
            ...Aite.taperCode("3333"),
            Aite.identifie("Carine"),
            Aite.ouvrirActions(),
            Aite.remboursement(false),
            Aite.fermerFenetre(),
            // Fermer la caisse : la caissière ne ferme pas (R13).
            Chrome.clickMenuButton(),
            Aite.entreeDuMenu("Close Register"),
            ...Aite.taperCode("3333"),
            Aite.notificationDanger("R13"),
            Aite.retour(),
            // Le menu ≡ du plan verrouillé (partie 1.1 A) : « Commandes »,
            // « Entrée ou sortie d'espèces », « Fermer la caisse » ; ni
            // « Changer de vue de salle » ni « Installer l'application ».
            Chrome.clickPlanButton(),
            ...Aite.planVerrouille(),
            Chrome.clickMenuButton(),
            Aite.menuAvec("Orders"),
            Aite.menuAvec("Close Register"),
            Aite.menuSans("Cash In/Out"),
            Aite.menuSans("Switch Floor View"),
            Aite.menuSans("Install App"),
            // Espèces depuis le plan : une serveuse est refusée (R15).
            Aite.entreeAite("Entrée ou sortie d'espèces"),
            ...Aite.taperCode("1111"),
            Aite.notificationDanger("R15"),
            ...Aite.planVerrouille(),
            // Le chef de salle tape son code : la fenêtre des espèces.
            Chrome.clickMenuButton(),
            Aite.entreeAite("Entrée ou sortie d'espèces"),
            ...Aite.taperCode("4444"),
            { content: "la fenêtre des espèces", trigger: ".modal .input-amount" },
            Aite.identifie("Paul"),
            Aite.verifier("fermer la fenêtre des espèces", () => {
                posmodel.dialog.closeAll();
                return true;
            }),
            ...Aite.planVerrouille(),
            // « Imprimer le rapport » (affiché s'il y a une imprimante,
            // simulée ici) : une serveuse est refusée (R21).
            Aite.verifier("une imprimante simulée", () => {
                posmodel.hardwareProxy.printer = { simulee: true };
                return true;
            }),
            Chrome.clickMenuButton(),
            Aite.entreeDuMenu("Print Report"),
            ...Aite.taperCode("1111"),
            Aite.notificationDanger("R21"),
            ...Aite.planVerrouille(),
            Aite.verifier("plus d'imprimante", () => {
                posmodel.hardwareProxy.printer = null;
                return true;
            }),
            // Le sélecteur de table : « Retour », pas « Discard » (règle 6).
            Aite.boutonTable(),
            {
                content: "« Retour » dans le sélecteur de table",
                trigger: ".modal .modal-footer button.btn-secondary:contains('Retour')",
            },
            Aite.verifier("pas de « Discard » dans le sélecteur de table", () => {
                const pied = document.querySelector(".modal .modal-footer");
                return Boolean(pied) && !pied.textContent.includes("Discard");
            }),
            {
                content: "« Retour »",
                trigger: ".modal .modal-footer button.btn-secondary:contains('Retour')",
                run: "click",
            },
            ...Aite.planVerrouille(),
        ].flat(),
});

registry.category("web_tour.tours").add("AitePaiementTour", {
    steps: () =>
        [
            FloorScreen.clickTable("5"),
            ...Aite.taperCode("1111"),
            ProductScreen.clickDisplayedProduct("Coca-Cola"),
            Aite.jEnvoie(),
            ...Aite.planVerrouille(),
            FloorScreen.clickTable("5"),
            ...Aite.taperCode("3333"),
            ...Aite.ecranCommande(),
            Aite.jEncaisse(),
            PaymentScreen.isShown(),
            PaymentScreen.clickPaymentMethod("Cash"),
            PaymentScreen.clickValidate(),
            // Retour au plan verrouillé, sans l'écran « Paiement réussi ».
            ...Aite.planVerrouille(),
            { content: "pas d'écran de ticket", trigger: "body:not(:has(.receipt-screen))" },
            // Rembourser l'addition payée : réservé au manager (R16).
            Chrome.clickMenuButton(),
            Aite.entreeDuMenu("Orders"),
            ...Aite.taperCode("3333"),
            { content: "la liste des commandes", trigger: ".pos .ticket-screen" },
            ...Aite.commandesPayees(),
            { content: "l'addition payée", trigger: ".ticket-screen .order-row", run: "click" },
            {
                content: "« Rembourser »",
                trigger: ".ticket-screen .pads .pay-order-button",
                run: "click",
            },
            Aite.notificationDanger("R16"),
            Chrome.clickPlanButton(),
            ...Aite.planVerrouille(),
        ].flat(),
});

function ardoiseProposee(proposee) {
    return Aite.verifier(
        proposee ? "ardoise proposée au manager" : "ardoise absente pour la caissière",
        () => {
            const bouton = Boolean(document.querySelector(".payment-screen .aite-credit-btn"));
            const mode = [
                ...document.querySelectorAll(".payment-screen .paymentmethod .payment-name"),
            ].some((nom) => nom.textContent.includes("Ardoise client"));
            return (bouton === proposee && mode === proposee) || `bouton ${bouton}, mode ${mode}`;
        }
    );
}

registry.category("web_tour.tours").add("AiteArdoiseTour", {
    steps: () =>
        [
            FloorScreen.clickTable("5"),
            ...Aite.taperCode("3333"),
            ProductScreen.clickDisplayedProduct("Coca-Cola"),
            Aite.jEncaisse(),
            PaymentScreen.isShown(),
            { content: "les modes sont affichés", trigger: ".payment-screen .paymentmethod" },
            ardoiseProposee(false),
            Chrome.clickPlanButton(),
            FloorScreen.clickTable("5"),
            ...Aite.taperCode("5555"),
            PaymentScreen.isShown(),
            { content: "les modes sont affichés", trigger: ".payment-screen .paymentmethod" },
            ardoiseProposee(true),
        ].flat(),
});

// ----------------------------------------------------------------------
// Correctifs de la revue de l'incrément 2 : chaque tour reproduit un défaut
// trouvé par la revue, avant sa correction.
// ----------------------------------------------------------------------

function modeReserve(present) {
    return Aite.verifier(
        present ? "le mode réservé est proposé" : "le mode réservé n'est pas proposé",
        () => {
            const noms = [
                ...document.querySelectorAll(".payment-screen .paymentmethod .payment-name"),
            ].map((nom) => nom.textContent);
            if (!noms.length) {
                return "modes pas encore affichés";
            }
            return noms.some((nom) => nom.includes("Ardoise AITE")) === present || noms.join(", ");
        }
    );
}

/** Prendre la main par le nom en haut sur l'écran de paiement : une
 * serveuse revient à l'écran de commande (REST-03) ; la caissière qui
 * reprend la main au manager ne voit plus le mode réservé (AH-02). */
registry.category("web_tour.tours").add("AitePriseEnMainTour", {
    steps: () =>
        [
            // Fanta (manager) encaisse : le mode réservé est proposé.
            FloorScreen.clickTable("5"),
            ...Aite.taperCode("5555"),
            ProductScreen.clickDisplayedProduct("Coca-Cola"),
            Aite.jEncaisse(),
            PaymentScreen.isShown(),
            Aite.identifie("Fanta"),
            modeReserve(true),
            // Carine reprend la main : elle encaisse, sans le mode réservé.
            Aite.prendreLaMain(),
            ...Aite.taperCode("3333"),
            Aite.identifie("Carine"),
            PaymentScreen.isShown(),
            modeReserve(false),
            // Awa reprend la main sur le paiement : elle n'encaisse pas.
            Aite.prendreLaMain(),
            ...Aite.taperCode("1111"),
            Aite.identifie("Awa"),
            ...Aite.ecranCommande(),
        ].flat(),
});

/** Un « Déplacer ou réunir » abandonné par les 5 minutes, puis un premier
 * toucher hors d'une table : le déplacement suivant porte l'addition sur la
 * table d'arrivée, sans code. */
registry.category("web_tour.tours").add("AiteTransfertApresAbandonTour", {
    steps: () =>
        [
            FloorScreen.clickTable("5"),
            ...Aite.taperCode("1111"),
            ProductScreen.clickDisplayedProduct("Coca-Cola"),
            ...Aite.deplacer(),
            Aite.verifier("5 minutes sans activité", () => posmodel.idleTimeout[0].action() === false),
            ...Aite.planVerrouille(),
            {
                content: "premier toucher hors d'une table : la phrase d'état",
                trigger: ".floor-screen .aite-plan-etat",
                run: "click",
            },
            FloorScreen.clickTable("5"),
            ...Aite.taperCode("1111"),
            ...Aite.ecranCommande(),
            ...Aite.deplacer(),
            FloorScreen.clickTable("2"),
            ...Aite.ecranCommande(),
            Aite.pasDePopupCode(),
            Aite.identifie("Awa"),
            Aite.verifier(
                "l'addition est sur la table 2",
                () => posmodel.get_order()?.table_id?.table_number === 2 ||
                    `table ${posmodel.get_order()?.table_id?.table_number}`
            ),
        ].flat(),
});

/** Caisse pas encore ouverte : un numéro de table inconnu tapé dans « Table »
 * ne mène pas à l'écran de commande (R3), et ne laisse pas d'addition vide. */
registry.category("web_tour.tours").add("AiteAvantOuvertureTour", {
    steps: () =>
        [
            Aite.popupCode(),
            Aite.retour(),
            Aite.bandeauCaisseFermee(),
            Aite.boutonTable(),
            ...NumberPopup.enterValue("99"),
            Dialog.confirm(),
            Aite.notificationDanger("R3"),
            Aite.pasDePopupCode(),
            Aite.bandeauCaisseFermee(),
            { content: "le plan est affiché", trigger: ".floor-screen .floor-map" },
            Aite.personneIdentifiee(),
            Aite.verifier(
                "aucune addition ouverte",
                () => posmodel.get_open_orders().length === 0 || posmodel.get_open_orders().length
            ),
        ].flat(),
});

/** L'onglet d'une addition sans table, touché sur le plan verrouillé,
 * demande le code (point de passage showScreen) ; le « + » n'est pas
 * proposé. */
registry.category("web_tour.tours").add("AiteOngletTour", {
    steps: () =>
        [
            ...Aite.planVerrouille(),
            Aite.boutonTable(),
            ...NumberPopup.enterValue("99"),
            Dialog.confirm(),
            ...Aite.taperCode("1111"),
            ...Aite.ecranCommande(),
            Aite.identifie("Awa"),
            ProductScreen.clickDisplayedProduct("Coca-Cola"),
            Chrome.clickPlanButton(),
            ...Aite.planVerrouille(),
            {
                content: "l'onglet « 99 » sur le plan",
                trigger: ".pos-leftheader .list-container-items button:contains('99')",
                run: "click",
            },
            ...Aite.taperCode("1111"),
            ...Aite.ecranCommande(),
            Aite.identifie("Awa"),
            Aite.verifier(
                "l'addition « 99 »",
                () => posmodel.get_order()?.getFloatingOrderName?.() === "99"
            ),
            // Le « + » des onglets n'est pas proposé (pas de vente sans table).
            { content: "pas de « + »", trigger: ".pos-leftheader:not(:has(.list-plus-btn))" },
        ].flat(),
});

/** Deux postes : la caisse a été ouverte sur un autre poste, celui-ci la
 * croit encore fermée. Le code tapé dans la fenêtre d'ouverture n'est pas
 * refusé (R3) : la caisse est déjà ouverte, rien n'est redemandé. */
registry.category("web_tour.tours").add("AiteRetardCodeTour", {
    steps: () =>
        [
            Aite.popupCode(),
            Aite.autrePosteOuvreLaCaisse("3333"),
            ...Aite.taperCode("1111"),
            Aite.pasDePopupCode(),
            Aite.bandeauCaisseFermee(false),
            ...Aite.planVerrouille(),
            Aite.pasDeNotification("R3"),
            { content: "pas de contrôle d'ouverture", trigger: "body:not(:has(.modal))" },
            Aite.verifier("la caisse est ouverte", () => posmodel.session.state === "opened"),
            FloorScreen.clickTable("5"),
            ...Aite.taperCode("1111"),
            ...Aite.ecranCommande(),
        ].flat(),
});

/** Deux postes : une table touchée sur un poste qui croit la caisse fermée
 * relit l'état du serveur avant de répondre R3. */
registry.category("web_tour.tours").add("AiteRetardTableTour", {
    steps: () =>
        [
            Aite.popupCode(),
            Aite.retour(),
            Aite.bandeauCaisseFermee(),
            Aite.autrePosteOuvreLaCaisse("3333"),
            FloorScreen.clickTable("5"),
            ...Aite.taperCode("1111"),
            ...Aite.ecranCommande(),
            Aite.identifie("Awa"),
            Aite.pasDeNotification("R3"),
        ].flat(),
});

/** Deux postes : « Ouvrir la caisse » sur un poste qui la croit fermée ne
 * demande pas de code si la caisse est déjà ouverte. */
registry.category("web_tour.tours").add("AiteRetardBandeauTour", {
    steps: () =>
        [
            Aite.popupCode(),
            Aite.retour(),
            Aite.bandeauCaisseFermee(),
            Aite.autrePosteOuvreLaCaisse("3333"),
            {
                content: "« Ouvrir la caisse »",
                trigger: ".aite-caisse-fermee .aite-ouvrir-caisse",
                run: "click",
            },
            Aite.bandeauCaisseFermee(false),
            Aite.pasDePopupCode(),
            ...Aite.planVerrouille(),
            Aite.verifier("la caisse est ouverte", () => posmodel.session.state === "opened"),
        ].flat(),
});

/** Fermer au-delà de l'écart maximum : le chef de salle est refusé (R14) ;
 * la fenêtre abandonnée, rien n'est noté « fermée par ». */
registry.category("web_tour.tours").add("AiteFermetureEcartTour", {
    steps: () =>
        [
            ...Aite.planVerrouille(),
            Chrome.clickMenuButton(),
            Aite.entreeDuMenu("Close Register"),
            ...Aite.taperCode("4444"),
            {
                content: "les espèces comptées, loin de l'attendu",
                trigger: ".modal .close-pos-popup .cash-input input",
                run: "edit 50000",
            },
            {
                content: "« Fermer la caisse »",
                trigger: ".modal .close-pos-popup button.highlight.btn-primary",
                run: "click",
            },
            Aite.notificationDanger("R14"),
            { content: "la fenêtre de fermeture reste", trigger: ".modal .close-pos-popup" },
            Aite.verifier("abandonner la fenêtre de fermeture", () => {
                posmodel.dialog.closeAll();
                return true;
            }),
            ...Aite.planVerrouille(),
            Aite.verifier("la caisse est toujours ouverte", () => posmodel.session.state === "opened"),
            {
                content: "le code de Paul n'autorise plus la fermeture sur le serveur",
                trigger: "body",
                async run() {
                    const fin = Date.now() + 5000;
                    while (Date.now() < fin) {
                        const [session] = await posmodel.data.call("pos.session", "read", [
                            [posmodel.session.id],
                            ["aite_autorisation_id"],
                        ]);
                        if (!session.aite_autorisation_id) {
                            return;
                        }
                        await new Promise((r) => setTimeout(r, 200));
                    }
                    throw new Error("autorisation de fermeture toujours posée");
                },
            },
        ].flat(),
});
