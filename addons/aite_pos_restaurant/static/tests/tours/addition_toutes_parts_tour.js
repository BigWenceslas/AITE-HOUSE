/** @odoo-module */
/* global posmodel */
/**
 * « Addition » sur une table divisée montre toutes les additions encore
 * ouvertes du groupe (constat du client, table 7B : « quand je clique sur
 * Addition, je dois pouvoir voir toutes les additions dans le cas où j'ai
 * divisé une addition ; actuellement je ne vois que l'autre partie »).
 *
 * Table 5 : Coca-Cola, Water × 2, Minute Maid, envoyés. La part « 5B » prend
 * les deux Water, puis la part de la part « 5BB » en prend un. « Addition »
 * depuis l'origine, depuis la part et depuis la part de la part montre les
 * trois additions (nom, lignes, total), dans l'ordre de création ; une part
 * payée n'y figure plus ; une table sans division garde l'aperçu d'Odoo.
 */
import * as Chrome from "@point_of_sale/../tests/tours/utils/chrome_util";
import * as ProductScreen from "@point_of_sale/../tests/tours/utils/product_screen_util";
import * as PaymentScreen from "@point_of_sale/../tests/tours/utils/payment_screen_util";
import * as FloorScreen from "@pos_restaurant/../tests/tours/utils/floor_screen_util";
import * as SplitBillScreen from "@pos_restaurant/../tests/tours/utils/split_bill_screen_util";
import * as Aite from "@aite_pos_restaurant/../tests/tours/aite_util";
import { registry } from "@web/core/registry";

/** Le nom d'une addition, comme sur ses onglets (« 5 », « 5B »). */
function nomDe(order) {
    return String(order.table_id?.table_number ?? order.getFloatingOrderName?.() ?? "");
}

function additionNommee(nom) {
    return posmodel.models["pos.order"].find((o) => !o.finalized && nomDe(o) === nom);
}

/** Diviser l'addition courante : `produits` est la liste des lignes touchées
 * sur l'écran de division (un toucher = une unité). */
function diviser(...produits) {
    return [
        Aite.ouvrirActions(),
        {
            content: "« Diviser l'addition »",
            trigger: ".modal .control-buttons-modal button:has(.fa-files-o)",
            run: "click",
        },
        { content: "l'écran de division", trigger: ".splitbill-screen" },
        ...produits.map((produit) => SplitBillScreen.clickOrderline(produit)),
        SplitBillScreen.clickPay(),
        ...Aite.ecranCommande(),
    ];
}

function addition() {
    return {
        content: "« Addition »",
        trigger: ".control-buttons .aite-addition-btn:not([disabled])",
        run: "click",
    };
}

/** La fenêtre des additions montre exactement `noms`, dans cet ordre, chacune
 * avec son nom, son ticket (lignes) et son total. */
function additionsAffichees(noms) {
    return [
        { content: "la fenêtre des additions", trigger: ".modal .aite-additions .pos-receipt" },
        Aite.verifier(`les additions ${noms.join(", ")}`, () => {
            const blocs = [...document.querySelectorAll(".modal .aite-additions .aite-addition")];
            const vus = blocs.map((b) => b.querySelector(".aite-addition-nom")?.textContent.trim());
            const attendus = noms.map((nom) => `Table ${nom}`);
            if (JSON.stringify(vus) !== JSON.stringify(attendus)) {
                return `vu ${JSON.stringify(vus)}`;
            }
            for (const [i, nom] of noms.entries()) {
                const order = additionNommee(nom);
                if (!order) {
                    return `addition ${nom} introuvable`;
                }
                const total = posmodel.env.utils.formatCurrency(order.get_total_with_tax());
                const bloc = blocs[i];
                const lu = bloc.querySelector(".aite-addition-total")?.textContent.trim();
                if (lu !== total) {
                    return `${nom} : total ${lu}, attendu ${total}`;
                }
                if (!bloc.querySelector(".pos-receipt")) {
                    return `${nom} : pas de ticket`;
                }
                for (const ligne of order.lines) {
                    if (!bloc.querySelector(".pos-receipt").textContent.includes(ligne.get_product().name)) {
                        return `${nom} : ${ligne.get_product().name} absent du ticket`;
                    }
                }
            }
            return true;
        }),
        {
            content: "le bouton pour imprimer depuis le navigateur",
            trigger: ".modal .aite-additions-imprimer",
        },
    ];
}

registry.category("web_tour.tours").add("AiteAdditionToutesLesPartsTour", {
    steps: () =>
        [
            ...Aite.planVerrouille(),
            FloorScreen.clickTable("5"),
            ...Aite.taperCode("3333"),
            ...Aite.personnes("3"),
            ...Aite.ecranCommande(),
            ProductScreen.clickDisplayedProduct("Coca-Cola"),
            ProductScreen.clickDisplayedProduct("Water"),
            ProductScreen.clickDisplayedProduct("Water"),
            ProductScreen.clickDisplayedProduct("Minute Maid"),
            Aite.jEnvoie(),
            ...Aite.planVerrouille(),
            FloorScreen.clickTable("5"),
            ...Aite.taperCode("3333"),
            ...Aite.ecranCommande(),
            // La part « 5B » : les deux Water.
            ...diviser("Water", "Water"),
            Aite.verifier("la part « 5B » est l'addition courante", () =>
                nomDe(posmodel.get_order()) === "5B" || `courante : ${nomDe(posmodel.get_order())}`
            ),
            // Depuis la part : les deux additions.
            addition(),
            ...additionsAffichees(["5", "5B"]),
            Aite.fermerFenetre(),
            // Retour sur l'origine (par le plan) : les deux additions aussi.
            Chrome.clickPlanButton(),
            ...Aite.planVerrouille(),
            FloorScreen.clickTable("5"),
            ...Aite.taperCode("3333"),
            ...Aite.ecranCommande(),
            Aite.verifier("l'origine « 5 » est l'addition courante", () =>
                nomDe(posmodel.get_order()) === "5" || `courante : ${nomDe(posmodel.get_order())}`
            ),
            addition(),
            ...additionsAffichees(["5", "5B"]),
            Aite.fermerFenetre(),
            // Une part de la part : « 5BB », depuis « 5B ».
            {
                content: "l'onglet « 5B »",
                trigger: ".pos-leftheader .list-container-items button:contains('5B')",
                run: "click",
            },
            ...Aite.ecranCommande(),
            Aite.verifier("la part « 5B » est l'addition courante", () =>
                nomDe(posmodel.get_order()) === "5B" || `courante : ${nomDe(posmodel.get_order())}`
            ),
            ...diviser("Water"),
            Aite.verifier("la part de la part « 5BB » est l'addition courante", () =>
                nomDe(posmodel.get_order()) === "5BB" || `courante : ${nomDe(posmodel.get_order())}`
            ),
            addition(),
            ...additionsAffichees(["5", "5B", "5BB"]),
            Aite.fermerFenetre(),
            // « 5BB » payée : elle n'est plus dans les additions de la table.
            Aite.jEncaisse(),
            PaymentScreen.isShown(),
            PaymentScreen.clickPaymentMethod("Cash"),
            PaymentScreen.clickValidate(),
            Aite.verifier("« 5BB » est payée", () =>
                !additionNommee("5BB") || "5BB encore ouverte"
            ),
            { content: "plus d'écran de paiement", trigger: "body:not(:has(.payment-screen))" },
            // Après une part payée, la caisse revient à la table, pour la part
            // suivante (receipt_screen.js).
            ...Aite.ecranCommande(),
            Aite.verifier("de retour sur une addition encore ouverte de la table", () =>
                ["5", "5B"].includes(nomDe(posmodel.get_order())) ||
                `courante : ${nomDe(posmodel.get_order())}`
            ),
            addition(),
            ...additionsAffichees(["5", "5B"]),
            // « J'imprime les additions » : l'impression du navigateur reçoit
            // un ticket par addition.
            Aite.verifier("l'impression du navigateur simulée", () => {
                window.aiteImpression = null;
                window.aiteVraiPrint = window.aiteVraiPrint || window.print;
                window.print = () => {
                    const zone = document.querySelector(".render-container");
                    window.aiteImpression = [...zone.querySelectorAll(".pos-receipt")].map(
                        (t) => t.textContent
                    );
                };
                return true;
            }),
            {
                content: "« J'imprime les additions »",
                trigger: ".modal .aite-additions-imprimer",
                run: "click",
            },
            Aite.verifier("deux tickets à l'impression du navigateur", () => {
                const tickets = window.aiteImpression;
                if (!tickets) {
                    return "rien d'imprimé";
                }
                window.print = window.aiteVraiPrint;
                return (tickets.length === 2 && tickets[0].includes("Coca-Cola") &&
                    tickets[1].includes("Water") && !tickets[1].includes("Coca-Cola")) ||
                    `${tickets.length} tickets`;
            }),
            Aite.fermerFenetre(),
            // Avec une imprimante : un ticket par addition, d'un seul geste.
            Aite.verifier("une imprimante de tickets simulée", () => {
                window.aiteTickets = [];
                posmodel.hardwareProxy.printer = {
                    printReceipt: async (el) => {
                        window.aiteTickets.push(el.textContent);
                        return { successful: true };
                    },
                };
                window.aiteSurUneTable = Boolean(posmodel.get_order()?.table_id);
                return true;
            }),
            addition(),
            Aite.verifier("deux tickets imprimés, un par addition", () => {
                const tickets = window.aiteTickets || [];
                const coca = tickets.filter((t) => t.includes("Coca-Cola")).length;
                const water = tickets.filter((t) => t.includes("Water")).length;
                return (tickets.length === 2 && coca === 1 && water === 1) ||
                    `${tickets.length} tickets (Coca-Cola ${coca}, Water ${water})`;
            }),
            // L'addition d'une table imprimée : retour au plan ; une part sans
            // table reste à l'écran.
            Aite.verifier("retour au plan après l'impression d'une table", () =>
                Boolean(document.querySelector(".floor-screen")) === window.aiteSurUneTable ||
                `plan ${Boolean(document.querySelector(".floor-screen"))}, table ${window.aiteSurUneTable}`
            ),
            Aite.verifier("plus d'imprimante", () => {
                posmodel.hardwareProxy.printer = null;
                return true;
            }),
        ].flat(),
});

/** Sans division, rien ne change : « Addition » ouvre l'aperçu d'Odoo, pour
 * cette addition seule. */
registry.category("web_tour.tours").add("AiteAdditionSansDivisionTour", {
    steps: () =>
        [
            ...Aite.planVerrouille(),
            FloorScreen.clickTable("5"),
            ...Aite.taperCode("3333"),
            ...Aite.personnes("2"),
            ...Aite.ecranCommande(),
            ProductScreen.clickDisplayedProduct("Coca-Cola"),
            addition(),
            { content: "l'aperçu d'Odoo", trigger: ".modal .pos-receipt" },
            {
                content: "pas la fenêtre des additions",
                trigger: ".modal:not(:has(.aite-additions)) .pos-receipt",
            },
            Aite.fermerFenetre(),
        ].flat(),
});

/** Toucher l'onglet dont le libellé est exactement `nom` (« 5B » et non
 * « 5BB »). */
function ongletExact(nom) {
    return {
        content: `l'onglet « ${nom} »`,
        trigger: ".pos-leftheader .list-container-items button",
        run() {
            const boutons = [...document.querySelectorAll(".pos-leftheader .list-container-items button")];
            const bouton = boutons.find((b) => b.textContent.trim() === nom);
            if (!bouton) {
                throw new Error(`onglet ${nom} introuvable : ${boutons.map((b) => b.textContent.trim())}`);
            }
            bouton.click();
        },
    };
}

function courante(nom) {
    return Aite.verifier(`« ${nom} » est l'addition courante`, () =>
        nomDe(posmodel.get_order()) === nom || `courante : ${nomDe(posmodel.get_order())}`
    );
}

/** L'aperçu d'Odoo, pour une seule addition : pas la fenêtre des additions. */
function apercuOdooSeul() {
    return [
        { content: "l'aperçu d'Odoo", trigger: ".modal .pos-receipt" },
        {
            content: "pas la fenêtre des additions",
            trigger: ".modal:not(:has(.aite-additions)) .pos-receipt",
        },
        Aite.verifier("un seul ticket dans l'aperçu", () =>
            document.querySelectorAll(".modal .pos-receipt").length === 1 ||
            `${document.querySelectorAll(".modal .pos-receipt").length} tickets`
        ),
    ];
}

function titreDesAdditions(attendu) {
    return Aite.verifier(`titre « ${attendu} »`, () => {
        const lu = document.querySelector(".modal .modal-title")?.textContent.trim();
        return lu === attendu || JSON.stringify(lu);
    });
}

/** Une part déplacée sur une table libre devient l'addition de cette table
 * (revue, constat 1) : « Addition » sur chacune des deux tables ne montre que
 * la sienne, l'aperçu d'Odoo. */
registry.category("web_tour.tours").add("AiteAdditionPartDeplaceeTour", {
    steps: () =>
        [
            ...Aite.planVerrouille(),
            FloorScreen.clickTable("4"),
            ...Aite.taperCode("3333"),
            ...Aite.personnes("3"),
            ...Aite.ecranCommande(),
            ProductScreen.clickDisplayedProduct("Coca-Cola"),
            ProductScreen.clickDisplayedProduct("Water"),
            Aite.jEnvoie(),
            ...Aite.planVerrouille(),
            FloorScreen.clickTable("4"),
            ...Aite.taperCode("3333"),
            ...Aite.ecranCommande(),
            ...diviser("Water"),
            courante("4B"),
            // La part « 4B » portée sur la table libre 2.
            ...Aite.deplacer(),
            FloorScreen.clickTable("2"),
            ...Aite.personnes("2"),
            ...Aite.ecranCommande(),
            courante("2"),
            addition(),
            ...apercuOdooSeul(),
            Aite.fermerFenetre(),
            Chrome.clickPlanButton(),
            ...Aite.planVerrouille(),
            FloorScreen.clickTable("4"),
            ...Aite.taperCode("3333"),
            ...Aite.ecranCommande(),
            courante("4"),
            addition(),
            ...apercuOdooSeul(),
            Aite.fermerFenetre(),
        ].flat(),
});

/** Une part intermédiaire payée (revue, constat 2) : 5 divisée en 5B, puis
 * 5B en 5BB ; 5B est payée. Après un rechargement de la caisse (un autre
 * poste), 5B n'est plus chargée : « Addition » sur la table 5 montre encore
 * 5 et 5BB. Puis une imprimante qui tombe en panne au second ticket : la
 * fenêtre ne reprend que l'addition non imprimée (revue, constat 8). */
registry.category("web_tour.tours").add("AiteAdditionApresRechargementTour", {
    steps: () =>
        [
            ...Aite.planVerrouille(),
            FloorScreen.clickTable("5"),
            ...Aite.taperCode("3333"),
            ...Aite.personnes("3"),
            ...Aite.ecranCommande(),
            ProductScreen.clickDisplayedProduct("Coca-Cola"),
            ProductScreen.clickDisplayedProduct("Water"),
            ProductScreen.clickDisplayedProduct("Minute Maid"),
            Aite.jEnvoie(),
            ...Aite.planVerrouille(),
            FloorScreen.clickTable("5"),
            ...Aite.taperCode("3333"),
            ...Aite.ecranCommande(),
            ...diviser("Water", "Minute Maid"),
            courante("5B"),
            ...diviser("Minute Maid"),
            courante("5BB"),
            // 5B (Water) payée.
            ongletExact("5B"),
            ...Aite.ecranCommande(),
            courante("5B"),
            Aite.jEncaisse(),
            PaymentScreen.isShown(),
            PaymentScreen.clickPaymentMethod("Cash"),
            PaymentScreen.clickValidate(),
            Aite.verifier("« 5B » est payée", () => !additionNommee("5B") || "5B encore ouverte"),
            { content: "plus d'écran de paiement", trigger: "body:not(:has(.payment-screen))" },
            ...Aite.ecranCommande(),
            Chrome.clickPlanButton(),
            ...Aite.planVerrouille(),
            {
                content: "recharger la caisse (un autre poste)",
                trigger: "body",
                run: () => window.location.reload(),
                expectUnloadPage: true,
            },
            ...Aite.planVerrouille(),
            Aite.verifier("5B payée n'est plus chargée, 5BB l'est", () =>
                (!posmodel.models["pos.order"].find((o) => nomDe(o) === "5B") && Boolean(additionNommee("5BB"))) ||
                "état inattendu"
            ),
            FloorScreen.clickTable("5"),
            ...Aite.taperCode("3333"),
            ...Aite.ecranCommande(),
            courante("5"),
            addition(),
            ...additionsAffichees(["5", "5BB"]),
            titreDesAdditions("Les additions de la table 5"),
            Aite.fermerFenetre(),
            // Une imprimante qui tombe en panne au second ticket.
            Aite.verifier("une imprimante qui tombe en panne au second ticket", () => {
                window.aiteTickets = [];
                posmodel.hardwareProxy.printer = {
                    printReceipt: async (el) => {
                        window.aiteTickets.push(el.textContent);
                        return window.aiteTickets.length === 1
                            ? { successful: true }
                            : { successful: false, message: { title: "Panne", body: "papier" } };
                    },
                };
                return true;
            }),
            addition(),
            {
                content: "Odoo propose l'imprimante du navigateur : non",
                trigger: ".modal:not(.o_inactive_modal) .modal-footer .btn-secondary",
                run: "click",
            },
            ...additionsAffichees(["5BB"]),
            Aite.verifier("le ticket déjà imprimé est signalé", () =>
                document.querySelector(".modal .aite-additions-sous-titre")?.textContent.includes("déjà") ||
                "pas de mention"
            ),
            Aite.verifier("plus d'imprimante", () => {
                posmodel.hardwareProxy.printer = null;
                return true;
            }),
            Aite.fermerFenetre(),
        ].flat(),
});
