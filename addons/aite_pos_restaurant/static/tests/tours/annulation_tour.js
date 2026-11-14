/* global posmodel */
/** Incrément 4 : verrou après envoi, code d'un responsable, motifs
 * (spécification, partie 6.3). AiteAnnulationTour, AiteAnnulerTableTour,
 * AiteDeplacementTour, AiteFermetureTour ; et AiteArdoiseSansModeTour (AH-02 :
 * en mode, pas de bouton d'ardoise sans mode « ardoise », même pour le
 * manager). Les vérifications côté serveur sont faites en Python après chaque
 * tour (test_tours.py, TestToursAnnulation). */
import * as Chrome from "@point_of_sale/../tests/tours/utils/chrome_util";
import * as ProductScreen from "@point_of_sale/../tests/tours/utils/product_screen_util";
import * as PaymentScreen from "@point_of_sale/../tests/tours/utils/payment_screen_util";
import * as FloorScreen from "@pos_restaurant/../tests/tours/utils/floor_screen_util";
import * as SplitBillScreen from "@pos_restaurant/../tests/tours/utils/split_bill_screen_util";
import * as Aite from "@aite_pos_restaurant/../tests/tours/aite_util";
import { registry } from "@web/core/registry";

/** Toucher une table du plan, taper le code ; une table libre demande aussi
 * le nombre de personnes. */
function ouvrir(table, code, personnes = null) {
    return [
        FloorScreen.clickTable(table),
        ...Aite.taperCode(code),
        ...(personnes ? Aite.personnes(personnes) : []),
        ...Aite.ecranCommande(),
    ];
}

function annulerLaTable() {
    return [
        Aite.ouvrirActions(),
        {
            content: "« Annuler la table »",
            trigger: ".modal .control-buttons-modal button:has(.fa-trash)",
            run: "click",
        },
    ];
}

registry.category("web_tour.tours").add("AiteAnnulationTour", {
    steps: () =>
        [
            ...Aite.planVerrouille(),
            // Awa envoie 3 Coca-Cola, puis en saisit une 4ᵉ (même ligne).
            ...ouvrir("5", "1111", "4"),
            ProductScreen.clickDisplayedProduct("Coca-Cola"),
            ProductScreen.clickDisplayedProduct("Coca-Cola"),
            ProductScreen.clickDisplayedProduct("Coca-Cola"),
            Aite.jEnvoie(),
            ...Aite.planVerrouille(),
            ...ouvrir("5", "1111"),
            ProductScreen.clickDisplayedProduct("Coca-Cola"),
            Aite.quantiteDeLaLigne("Coca-Cola", 4),
            // ⌫ ⌫ : la 4ᵉ, pas encore envoyée, part librement (Q34).
            ProductScreen.clickNumpad("⌫"),
            ProductScreen.clickNumpad("⌫"),
            Aite.quantiteDeLaLigne("Coca-Cola", 3),
            Aite.pasDePopupAnnulation(),
            // « 1 » tapé sur la ligne envoyée : rien (chiffre sous l'envoyé ignoré).
            ProductScreen.clickNumpad("1"),
            Aite.quantiteDeLaLigne("Coca-Cola", 3),
            Aite.pasDePopupAnnulation(),
            // ⌫ ⌫ : la fenêtre d'annulation.
            ProductScreen.clickNumpad("⌫"),
            ProductScreen.clickNumpad("⌫"),
            ...Aite.popupAnnulation(
                Aite.titre("annulerProduit", "Coca-Cola", 5),
                Aite.messageDe("R9", 3, "Coca-Cola")
            ),
            ...Aite.combien("2", ["1", "2", "3"]),
            // Le code d'un serveur : R8, la fenêtre attend un autre code.
            ...Aite.codeAnnulation("2222"),
            Aite.notificationDanger("R8"),
            ...Aite.codeAnnulation("4444"),
            ...Aite.motif(0),
            Aite.pasDePopupAnnulation(),
            Aite.notification(Aite.texte("annulationFaite", 2, "Coca-Cola", "Paul")),
            Aite.quantiteDeLaLigne("Coca-Cola", 1),
            // REST-11-P1 : la personne identifiée ne change pas.
            Aite.identifie("Awa"),
            { content: "le nom d'Awa toujours en haut", trigger: ".pos-rightheader .cashier-name" },
            // Le filet du modèle : une baisse sous l'envoyé sans autorisation
            // est refusée, avec R9.
            Aite.verifier("set_quantity refuse une baisse sous l'envoyé", () => {
                const ligne = posmodel.get_order().lines[0];
                const refus = ligne.set_quantity(0);
                return (refus?.title === "Produit déjà envoyé" && ligne.get_quantity() === 1) ||
                    JSON.stringify(refus);
            }),
            Aite.verifier("removeOrderline refuse une ligne envoyée", () => {
                const order = posmodel.get_order();
                return (order.removeOrderline(order.lines[0]) === false && order.lines.length === 1) ||
                    "ligne retirée";
            }),
            Chrome.clickPlanButton(),
            ...Aite.planVerrouille(),
        ].flat(),
});

registry.category("web_tour.tours").add("AiteAnnulerTableTour", {
    steps: () =>
        [
            ...Aite.planVerrouille(),
            // Awa : table 5, Coca-Cola et Water envoyés.
            ...ouvrir("5", "1111", "4"),
            ProductScreen.clickDisplayedProduct("Coca-Cola"),
            ProductScreen.clickDisplayedProduct("Water"),
            Aite.jEnvoie(),
            ...Aite.planVerrouille(),
            ...ouvrir("5", "1111"),
            // « Annuler la table » : notre fenêtre directement, sans la
            // confirmation d'Odoo (T14).
            ...annulerLaTable(),
            ...Aite.popupAnnulation(Aite.titre("annulerTable", 5)),
            Aite.verifier(
                "pas de confirmation d'Odoo : une seule fenêtre",
                () => document.querySelectorAll(".modal .modal-dialog").length === 1
            ),
            ...Aite.codeAnnulation("4444"),
            ...Aite.motif(1),
            ...Aite.planVerrouille(),
            Aite.tableLibre(5),
            // Paul seul (chef de salle) : son code tapé au toucher de la table
            // sert aussi à l'annulation (T3) — 8 touches.
            ...ouvrir("4", "4444", "2"),
            ProductScreen.clickDisplayedProduct("Coca-Cola"),
            Aite.jEnvoie(),
            ...Aite.planVerrouille(),
            ...ouvrir("4", "4444"),
            ...annulerLaTable(),
            ...Aite.popupAnnulation(Aite.titre("annulerTable", 4)),
            Aite.pasDeCodeAnnulation(),
            ...Aite.motif(0),
            ...Aite.planVerrouille(),
            Aite.tableLibre(4),
        ].flat(),
});

registry.category("web_tour.tours").add("AiteDeplacementTour", {
    steps: () =>
        [
            ...Aite.planVerrouille(),
            // Table 5 : 2 Coca-Cola et 1 Water envoyés ; table 4 : 1 Coca-Cola envoyé.
            ...ouvrir("5", "1111", "4"),
            ProductScreen.clickDisplayedProduct("Coca-Cola"),
            ProductScreen.clickDisplayedProduct("Coca-Cola"),
            ProductScreen.clickDisplayedProduct("Water"),
            Aite.jEnvoie(),
            ...Aite.planVerrouille(),
            ...ouvrir("4", "1111", "2"),
            ProductScreen.clickDisplayedProduct("Coca-Cola"),
            Aite.jEnvoie(),
            ...Aite.planVerrouille(),
            // Diviser la table 5 : le Water dans la part « 5B », sans fenêtre.
            ...ouvrir("5", "1111"),
            Aite.ouvrirActions(),
            {
                content: "« Diviser l'addition »",
                trigger: ".modal .control-buttons-modal button:has(.fa-files-o)",
                run: "click",
            },
            { content: "l'écran de division", trigger: ".splitbill-screen" },
            SplitBillScreen.clickOrderline("Water"),
            ...SplitBillScreen.clickPay(),
            ...Aite.ecranCommande(),
            Aite.pasDePopupAnnulation(),
            // Réunir la table 5 (2 Coca-Cola) à la table 4, sans fenêtre.
            Chrome.clickPlanButton(),
            ...Aite.planVerrouille(),
            ...ouvrir("5", "1111"),
            ...Aite.deplacer(),
            FloorScreen.clickTable("4"),
            ...Aite.ecranCommande(),
            Aite.pasDePopupAnnulation(),
            Aite.verifier(
                "la table 4 a les 3 Coca-Cola",
                () =>
                    (posmodel.get_order()?.table_id?.table_number === 4 &&
                        posmodel.get_order().lines.reduce((s, l) => s + l.get_quantity(), 0) === 3) ||
                    "table 4 incomplète"
            ),
            Aite.tableLibre(5),
            Chrome.clickPlanButton(),
            ...Aite.planVerrouille(),
        ].flat(),
});

registry.category("web_tour.tours").add("AiteFermetureTour", {
    steps: () =>
        [
            ...Aite.planVerrouille(),
            // Deux tables ouvertes, chacune avec un produit envoyé.
            ...ouvrir("5", "1111", "2"),
            ProductScreen.clickDisplayedProduct("Coca-Cola"),
            Aite.jEnvoie(),
            ...Aite.planVerrouille(),
            ...ouvrir("4", "1111", "3"),
            ProductScreen.clickDisplayedProduct("Water"),
            Aite.jEnvoie(),
            ...Aite.planVerrouille(),
            // Paul ferme la caisse.
            Chrome.clickMenuButton(),
            Aite.entreeDuMenu("Close Register"),
            ...Aite.taperCode("4444"),
            {
                content: "les espèces comptées",
                trigger: ".modal .close-pos-popup .cash-input input",
                run: "edit 0",
            },
            {
                content: "« Fermer la caisse »",
                trigger: ".modal .close-pos-popup button.highlight.btn-primary",
                run: "click",
            },
            // Deux tables encore ouvertes : notre message, « Annuler ces tables ».
            Aite.verifier("le message des tables encore ouvertes", () => {
                const corps = [...document.querySelectorAll(".modal .modal-body")].map((b) =>
                    b.textContent.trim()
                );
                const attendu = Aite.texte("tablesOuvertes", 2, "4, 5")();
                return corps.some((c) => c === attendu) || corps.join(" | ");
            }),
            {
                content: "« Annuler ces tables » (bouton secondaire de la fenêtre)",
                trigger: ".modal:not(.o_inactive_modal) .modal-footer .btn-secondary",
                run: "click",
            },
            ...Aite.popupAnnulation(Aite.titre("annulerTables", "4, 5")),
            // Le code de Paul est déjà tapé : le motif seul.
            Aite.pasDeCodeAnnulation(),
            { content: "« Pourquoi ? »", trigger: ".modal .aite-annulation-motifs" },
            {
                content: "« Client parti » : les tables sont annulées, la caisse se ferme",
                trigger: ".modal .aite-annulation-motifs [data-aite-motif-id]:eq(1)",
                run: "click",
                expectUnloadPage: true,
            },
            // La page se recharge : une nouvelle session, en contrôle
            // d'ouverture (la fenêtre du code s'ouvre d'elle-même).
            Aite.popupCode(),
            Aite.titreDeLaFenetre(Aite.titre("ouvrir")),
        ].flat(),
});

registry.category("web_tour.tours").add("AiteArdoiseSansModeTour", {
    steps: () =>
        [
            ...ouvrir("5", "5555", "2"),
            ProductScreen.clickDisplayedProduct("Coca-Cola"),
            Aite.jEncaisse(),
            PaymentScreen.isShown(),
            { content: "les modes sont affichés", trigger: ".payment-screen .paymentmethod" },
            Aite.verifier(
                "pas de « Mettre sur ardoise » sans mode « ardoise », même pour le manager",
                () => !document.querySelector(".payment-screen .aite-credit-btn")
            ),
        ].flat(),
});
