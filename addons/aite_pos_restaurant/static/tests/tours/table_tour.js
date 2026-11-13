/* global posmodel */
/** Incrément 3 : la table — personnes, qui a ouvert ; numéro inconnu, vente
 * sans table (spécification, partie 6.3). AitePersonnesTour,
 * AiteVenteSansTableTour (case décochée), AiteVenteSansTableCocheeTour (case
 * cochée), AiteReunionTour ; depuis la revue de l'incrément 3,
 * AiteSaisieOngletTour (T19 : l'addition quittée par un onglet), et dans les
 * deux tours de la vente sans table : « Actions » sans « Modifier le nom de la
 * commande », « Retour » d'un numéro tapé depuis l'écran de commande, la
 * vente sans table nommée comme telle. Les vérifications côté serveur sont
 * faites en Python après chaque tour (test_tours.py, TestToursTable). */
import * as Chrome from "@point_of_sale/../tests/tours/utils/chrome_util";
import * as Dialog from "@point_of_sale/../tests/tours/utils/dialog_util";
import * as ProductScreen from "@point_of_sale/../tests/tours/utils/product_screen_util";
import * as NumberPopup from "@point_of_sale/../tests/tours/utils/number_popup_util";
import * as FloorScreen from "@pos_restaurant/../tests/tours/utils/floor_screen_util";
import * as SplitBillScreen from "@pos_restaurant/../tests/tours/utils/split_bill_screen_util";
import * as Aite from "@aite_pos_restaurant/../tests/tours/aite_util";
import { registry } from "@web/core/registry";

const POPUP = ".modal:not(.o_inactive_modal) .aite-code-popup";

function tableDuSelecteur(numero) {
    return [Aite.boutonTable(), ...NumberPopup.enterValue(numero), Dialog.confirm()];
}

function commandeCourante(test, content) {
    return Aite.verifier(content, () => {
        const order = posmodel.get_order();
        return (order && test(order)) || JSON.stringify({
            table: order?.table_id?.table_number,
            nom: order?.getFloatingOrderName?.(),
            personnes: order?.customer_count,
        });
    });
}

registry.category("web_tour.tours").add("AitePersonnesTour", {
    steps: () =>
        [
            ...Aite.planVerrouille(),
            // Table libre : le code, puis le nombre de personnes, dans la même fenêtre.
            FloorScreen.clickTable("5"),
            ...Aite.taperCode("1111"),
            ...Aite.popupPersonnes(Aite.titre("personnes", 5)),
            Aite.verifier(
                "le zéro n'existe pas",
                () => !document.querySelector(`${POPUP} [data-aite-personnes="0"]`)
            ),
            // « 9 et plus » puis 0 : « Valider » grisé (R5).
            {
                content: "« 9 et plus »",
                trigger: `${POPUP} [data-aite-personnes="plus"]`,
                run: "click",
            },
            {
                content: "« Valider » grisé tant que rien n'est tapé",
                trigger: `${POPUP} .aite-personnes-valider:disabled`,
            },
            { content: "0", trigger: `${POPUP} [data-aite-nombre="0"]`, run: "click" },
            { content: "« Valider » grisé (R5)", trigger: `${POPUP} .aite-personnes-valider:disabled` },
            Aite.verifier("R5 dans la fenêtre", () => {
                const texte = document.querySelector(`${POPUP} .aite-personnes-erreur`)?.textContent;
                return texte?.trim() === "Il faut au moins une personne à table." || texte;
            }),
            // « 4 » valide.
            {
                content: "« 4 »",
                trigger: `${POPUP} [data-aite-personnes="4"]`,
                run: "click",
            },
            ...Aite.ecranCommande(),
            Aite.identifie("Awa"),
            Aite.boutonPersonnes("4 personnes"),
            Aite.etatCommande("Table 5 · ouverte par Awa"),
            // Retour au plan : la table est occupée, sans produit.
            Chrome.clickPlanButton(),
            ...Aite.planVerrouille(),
            Aite.tableOccupee("5"),
            Aite.verifier("l'addition de la table 5 est enregistrée, sans produit", () => {
                const order = posmodel.models["pos.order"].find(
                    (o) => o.table_id?.table_number === 5 && !o.finalized
                );
                return (
                    (order && typeof order.id === "number" && !order.lines.length &&
                        order.customer_count === 4) ||
                    JSON.stringify({ id: order?.id, personnes: order?.customer_count })
                );
            }),
            // Table occupée : le code seulement.
            FloorScreen.clickTable("5"),
            ...Aite.taperCode("1111"),
            ...Aite.ecranCommande(),
            Aite.pasDePopupPersonnes(),
            // « 4 personnes » → « 6 » : 2 touches.
            Aite.toucherBoutonPersonnes(),
            ...Aite.popupPersonnes(Aite.titre("personnes", 5)),
            Aite.verifier(
                "pas de pavé du code pour changer les personnes",
                () => !document.querySelector(`${POPUP} .aite-code-points`)
            ),
            ...Aite.personnes("6"),
            Aite.boutonPersonnes("6 personnes"),
            // Le sélecteur « Table » depuis l'écran de commande, vers une table
            // libre : l'étape personnes, sans code.
            ...tableDuSelecteur("4"),
            ...Aite.popupPersonnes(Aite.titre("personnes", 4)),
            Aite.verifier(
                "pas de code demandé depuis l'écran de commande",
                () => !document.querySelector(`${POPUP} .aite-code-points`)
            ),
            ...Aite.personnes("3"),
            ...Aite.ecranCommande(),
            commandeCourante((o) => o.table_id?.table_number === 4, "la table 4"),
            Aite.boutonPersonnes("3 personnes"),
            ProductScreen.clickDisplayedProduct("Water"),
            // Division de la table 5 (6 personnes) : origine 6, part 0.
            ...tableDuSelecteur("5"),
            ...Aite.ecranCommande(),
            commandeCourante((o) => o.table_id?.table_number === 5, "la table 5"),
            ProductScreen.clickDisplayedProduct("Coca-Cola"),
            ProductScreen.clickDisplayedProduct("Coca-Cola"),
            ProductScreen.clickDisplayedProduct("Water"),
            Aite.ouvrirActions(),
            {
                content: "« Diviser l'addition »",
                trigger: ".modal .control-buttons-modal button:has(.fa-files-o):contains('Diviser l')",
                run: "click",
            },
            { content: "l'écran de division", trigger: ".splitbill-screen" },
            // Tout sélectionner : R30, rien n'est divisé.
            SplitBillScreen.clickOrderline("Coca-Cola"),
            SplitBillScreen.clickOrderline("Coca-Cola"),
            SplitBillScreen.clickOrderline("Water"),
            ...SplitBillScreen.clickPay(),
            Aite.notificationDanger("R30"),
            { content: "toujours l'écran de division", trigger: ".splitbill-screen" },
            SplitBillScreen.clickOrderline("Water"),
            ...SplitBillScreen.clickPay(),
            ...Aite.ecranCommande(),
            commandeCourante((o) => {
                const origine = posmodel.models["pos.order"].find(
                    (x) => x.uuid === o.aite_origine_uuid
                );
                return (
                    o.getFloatingOrderName?.() === "5B" &&
                    o.customer_count === 0 &&
                    origine?.customer_count === 6
                );
            }, "la part 5B a 0 personne, l'origine en garde 6"),
            // Réunion 3 + 4 → 7 : la table 4 (3 personnes) versée dans la table 2 (4).
            Chrome.clickPlanButton(),
            ...Aite.planVerrouille(),
            FloorScreen.clickTable("2"),
            ...Aite.taperCode("1111"),
            ...Aite.personnes("4"),
            ...Aite.ecranCommande(),
            ProductScreen.clickDisplayedProduct("Coca-Cola"),
            ...tableDuSelecteur("4"),
            ...Aite.ecranCommande(),
            commandeCourante((o) => o.table_id?.table_number === 4, "la table 4"),
            ...Aite.deplacer(),
            FloorScreen.clickTable("2"),
            ...Aite.ecranCommande(),
            Aite.pasDePopupPersonnes(),
            commandeCourante(
                (o) => o.table_id?.table_number === 2 && o.customer_count === 7,
                "table 2 : 7 personnes"
            ),
            Aite.boutonPersonnes("7 personnes"),
            Chrome.clickPlanButton(),
            ...Aite.planVerrouille(),
        ].flat(),
});

registry.category("web_tour.tours").add("AiteVenteSansTableTour", {
    steps: () =>
        [
            ...Aite.planVerrouille(),
            { content: "pas de « + »", trigger: ".pos-leftheader:not(:has(.list-plus-btn))" },
            // Un numéro qui n'est pas sur le plan : code, personnes, table à ce nom.
            ...tableDuSelecteur("99"),
            ...Aite.taperCode("1111"),
            ...Aite.popupPersonnes(Aite.titre("personnes", 99)),
            ...Aite.personnes("2"),
            ...Aite.ecranCommande(),
            Aite.identifie("Awa"),
            commandeCourante(
                (o) => o.getFloatingOrderName?.() === "99" && o.customer_count === 2,
                "l'addition « 99 » à 2 personnes"
            ),
            Aite.boutonPersonnes("2 personnes"),
            Aite.etatCommande("Table 99 · ouverte par Awa"),
            { content: "toujours pas de « + »", trigger: ".pos-leftheader:not(:has(.list-plus-btn))" },
            // « Actions » d'un numéro tapé : pas de « Modifier le nom de la
            // commande » (revue, constat 5).
            ...Aite.actionsSansRenommer(),
            // Depuis l'écran de commande, un autre numéro inconnu puis
            // « Retour » : Awa reste sur « 99 », toujours identifiée (revue,
            // constat 4).
            ...tableDuSelecteur("98"),
            ...Aite.popupPersonnes(Aite.titre("personnes", 98)),
            Aite.retour(),
            ...Aite.ecranCommande(),
            Aite.identifie("Awa"),
            commandeCourante((o) => o.getFloatingOrderName?.() === "99", "retour à l'addition « 99 »"),
            Aite.verifier(
                "aucune addition « 98 »",
                () => !posmodel.get_open_orders().some((o) => o.getFloatingOrderName?.() === "98")
            ),
            Chrome.clickPlanButton(),
            ...Aite.planVerrouille(),
            // « Retour » à l'étape personnes : aucune addition « 98 ».
            ...tableDuSelecteur("98"),
            ...Aite.taperCode("1111"),
            ...Aite.popupPersonnes(),
            Aite.retour(),
            ...Aite.planVerrouille(),
            Aite.verifier(
                "aucune addition « 98 »",
                () => !posmodel.get_open_orders().some((o) => o.getFloatingOrderName?.() === "98")
            ),
        ].flat(),
});

registry.category("web_tour.tours").add("AiteVenteSansTableCocheeTour", {
    steps: () =>
        [
            ...Aite.planVerrouille(),
            // Case cochée : le « + » ; une serveuse n'ouvre pas de vente sans table (R17).
            { content: "« + »", trigger: ".pos-leftheader .list-plus-btn", run: "click" },
            ...Aite.taperCode("1111"),
            Aite.notificationDanger("R17"),
            ...Aite.planVerrouille(),
            Aite.verifier("aucune addition ouverte", () => posmodel.get_open_orders().length === 0 ||
                posmodel.get_open_orders().length),
            // La caissière : une vente sans table, à 0 personne.
            { content: "« + »", trigger: ".pos-leftheader .list-plus-btn", run: "click" },
            ...Aite.taperCode("3333"),
            Aite.pasDePopupPersonnes(),
            ...Aite.ecranCommande(),
            Aite.identifie("Carine"),
            commandeCourante(
                (o) => !o.table_id && o.customer_count === 0,
                "vente sans table, 0 personne"
            ),
            { content: "pas de bouton des personnes", trigger: "body:not(:has(.aite-personnes-btn))" },
            Aite.etatCommande("Vente sans table · ouverte par Carine"),
            ...Aite.actionsSansRenommer(),
            ProductScreen.clickDisplayedProduct("Coca-Cola"),
            Chrome.clickPlanButton(),
            ...Aite.planVerrouille(),
            // Son onglet : la fenêtre du code dit « Vente sans table », pas
            // « Table 1001 » ; une serveuse est renvoyée (R4, revue, constat 7).
            {
                content: "l'onglet de la vente sans table",
                trigger: ".pos-leftheader .list-container-items button",
                run: "click",
            },
            Aite.popupCode(),
            Aite.titreDeLaFenetre(Aite.titre("venteSansTable", numeroDeLaVente)),
            ...Aite.taperCode("1111"),
            Aite.notificationDanger("R4vente", numeroDeLaVente, "Carine"),
            ...Aite.planVerrouille(),
        ].flat(),
});

/** Le numéro de l'onglet de la vente sans table ouverte (son numéro de
 * suivi : elle n'a ni table ni nom). */
function numeroDeLaVente() {
    return posmodel.get_open_orders().find((o) => !o.table_id)?.getFloatingOrderName();
}

/** La table d'un collègue (incrément 3) : une serveuse n'ouvre pas la table
 * d'une collègue (Q19, R4) et ne réunit pas sa table à la sienne (R19) ; elle
 * retrouve alors sa propre table. « Déplacer ou réunir » : une part
 * (« 5B ») portée sur une table libre demande son nombre de personnes. */
registry.category("web_tour.tours").add("AiteReunionTour", {
    steps: () =>
        [
            // Carine ouvre la table 2.
            FloorScreen.clickTable("2"),
            ...Aite.taperCode("3333"),
            ...Aite.personnes("2"),
            ...Aite.ecranCommande(),
            ProductScreen.clickDisplayedProduct("Coca-Cola"),
            Chrome.clickPlanButton(),
            ...Aite.planVerrouille(),
            // Q19 : la table de Carine n'est pas celle d'Awa (R4), retour au plan.
            FloorScreen.clickTable("2"),
            ...Aite.taperCode("1111"),
            Aite.notificationDanger("R4", 2, "Carine"),
            ...Aite.planVerrouille(),
            // Awa ouvre la table 5, puis veut la réunir à la table 2 : R19.
            FloorScreen.clickTable("5"),
            ...Aite.taperCode("1111"),
            ...Aite.personnes("4"),
            ProductScreen.clickDisplayedProduct("Coca-Cola"),
            ProductScreen.clickDisplayedProduct("Coca-Cola"),
            ProductScreen.clickDisplayedProduct("Water"),
            ...Aite.deplacer(),
            FloorScreen.clickTable("2"),
            Aite.notificationDanger("R19", 2, "Carine"),
            ...Aite.ecranCommande(),
            Aite.identifie("Awa"),
            commandeCourante((o) => o.table_id?.table_number === 5, "retour à la table 5"),
            // Une part portée sur une table libre : l'étape personnes seule.
            Aite.ouvrirActions(),
            {
                content: "« Diviser l'addition »",
                trigger: ".modal .control-buttons-modal button:has(.fa-files-o):contains('Diviser l')",
                run: "click",
            },
            SplitBillScreen.clickOrderline("Water"),
            ...SplitBillScreen.clickPay(),
            ...Aite.ecranCommande(),
            commandeCourante((o) => o.getFloatingOrderName?.() === "5B", "la part 5B"),
            ...Aite.deplacer(),
            FloorScreen.clickTable("4"),
            ...Aite.popupPersonnes(Aite.titre("personnes", 4)),
            Aite.verifier(
                "pas de code pour la table d'arrivée",
                () => !document.querySelector(`${POPUP} .aite-code-points`)
            ),
            ...Aite.personnes("2"),
            ...Aite.ecranCommande(),
            commandeCourante(
                (o) => o.table_id?.table_number === 4 && o.customer_count === 2,
                "la part est sur la table 4, à 2 personnes"
            ),
            Chrome.clickPlanButton(),
            ...Aite.planVerrouille(),
        ].flat(),
});

/** T19 (revue de l'incrément 3, constat bloquant n° 2) : l'addition quittée
 * par un onglet est enregistrée au nom de la personne qui l'a remplie.
 * Awa ajoute un Coca-Cola sur la table 5 ; Paul prend la main et ajoute une
 * Water ; il quitte la table par l'onglet « 99 » puis revient au plan.
 * Carine ouvre ensuite la table 2 et touche « Table » (Odoo enregistre
 * alors toutes les additions en attente, au nom de la personne identifiée) :
 * rien de la table 5 ne passe à son nom (vérifié en Python). */
registry.category("web_tour.tours").add("AiteSaisieOngletTour", {
    steps: () =>
        [
            ...Aite.planVerrouille(),
            // Awa ouvre le numéro « 99 », puis la table 5.
            ...tableDuSelecteur("99"),
            ...Aite.taperCode("1111"),
            ...Aite.personnes("2"),
            ...Aite.ecranCommande(),
            Chrome.clickPlanButton(),
            ...Aite.planVerrouille(),
            FloorScreen.clickTable("5"),
            ...Aite.taperCode("1111"),
            ...Aite.personnes("4"),
            ...Aite.ecranCommande(),
            ProductScreen.clickDisplayedProduct("Coca-Cola"),
            // Paul prend la main (le Coca-Cola part au nom d'Awa) et ajoute une Water.
            Aite.prendreLaMain(),
            ...Aite.taperCode("4444"),
            Aite.identifie("Paul"),
            ...Aite.ecranCommande(),
            ProductScreen.clickDisplayedProduct("Water"),
            // Il quitte la table 5 par l'onglet « 99 ».
            Aite.onglet("99"),
            ...Aite.ecranCommande(),
            Aite.identifie("Paul"),
            commandeCourante((o) => o.getFloatingOrderName?.() === "99", "l'addition « 99 »"),
            Aite.verifier("la table 5 quittée est enregistrée", () => {
                const order = posmodel.models["pos.order"].find(
                    (o) => o.table_id?.table_number === 5 && !o.finalized
                );
                return (
                    (order && typeof order.id === "number" && !posmodel.aiteAModifier(order)) ||
                    JSON.stringify({ id: order?.id, enAttente: order && posmodel.aiteAModifier(order) })
                );
            }),
            Chrome.clickPlanButton(),
            ...Aite.planVerrouille(),
            // Carine ouvre la table 2 et touche « Table » : Odoo enregistre
            // toutes les additions en attente, à son nom.
            FloorScreen.clickTable("2"),
            ...Aite.taperCode("3333"),
            ...Aite.personnes("2"),
            ...Aite.ecranCommande(),
            Aite.boutonTable(),
            {
                content: "« Retour » du sélecteur de table",
                trigger: ".modal:not(.o_inactive_modal) .modal-footer .btn-secondary",
                run: "click",
            },
            Chrome.clickPlanButton(),
            ...Aite.planVerrouille(),
        ].flat(),
});

