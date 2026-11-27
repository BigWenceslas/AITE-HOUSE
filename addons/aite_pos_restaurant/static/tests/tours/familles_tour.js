/* global posmodel, odoo */
/** Les familles de la carte (demandes du restaurant de Douala, 18.0.1.0.14) :
 * « quand le serveur touche Envoyer, ça imprime directement sur chaque
 * imprimante selon son type : chaud, froid, bar, pizza et autre » et « au
 * niveau de la facture, grouper les produits par famille ».
 *
 * Écrits avant le développement : ils servent de spécification.
 *
 * La carte des tests (tests/test_tours.py, AiteToursFamillesCommon) :
 * Plats > Grillades (Poulet braisé 7 000) ; Pizzas & burgers > Pizzas
 * (Pizza Marguerite 5 000) et Burgers (Burger maison 4 000) ; Desserts
 * (Glace vanille 1 500, aucune imprimante ne la prend) ; Bar > Vins > Vins
 * blancs (Vin blanc au verre 3 000, trois niveaux) ; Pain maison (500, sans
 * famille). Imprimantes : Chaud (Plats, Burgers), Pizza (Pizzas), Bar (Bar,
 * la famille de niveau 1 seulement) et, selon le test, Autre (« Prend tout ce
 * qu'aucune autre imprimante ne prend », 2 exemplaires).
 *
 * - AiteFamilleParenteTour : cocher « Bar » sur l'imprimante couvre ses
 *   sous-familles (Vins blancs, au 3e niveau) ; vérification du code d'Odoo.
 * - AiteImprimanteAutreTour : le dessert et le pain partent sur « Autre »
 *   (2 exemplaires), jamais ailleurs ; une annulation suit le même chemin ;
 *   une note générale tapée seule va aux imprimantes qui ont reçu un plat.
 * - AiteEpsonDirectTour : les imprimantes Epson sont de vraies imprimantes
 *   ePOS (requête directe à l'adresse de l'imprimante, au protocole de la
 *   page) : « J'envoie » imprime sans aucune fenêtre ni aperçu.
 * - AiteAdditionFamillesTour : l'addition et le ticket final (et sa
 *   réimpression) sont groupés par famille de niveau 1 avec un sous-total
 *   par famille ; le total, les paiements, la note au client ne changent pas.
 * - AiteAdditionFamillesDiviseeTour : la fenêtre des additions d'une table
 *   divisée montre chaque addition groupée.
 * - AiteAdditionSansFamillesTour : réglage décoché, le ticket d'Odoo. */
import * as Dialog from "@point_of_sale/../tests/tours/utils/dialog_util";
import * as ProductScreen from "@point_of_sale/../tests/tours/utils/product_screen_util";
import * as PaymentScreen from "@point_of_sale/../tests/tours/utils/payment_screen_util";
import * as TextInputPopup from "@point_of_sale/../tests/tours/utils/text_input_popup_util";
import * as FloorScreen from "@pos_restaurant/../tests/tours/utils/floor_screen_util";
import * as SplitBillScreen from "@pos_restaurant/../tests/tours/utils/split_bill_screen_util";
import * as Aite from "@aite_pos_restaurant/../tests/tours/aite_util";
import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";

const POULET = "Poulet braisé";
const PIZZA = "Pizza Marguerite";
const BURGER = "Burger maison";
const VIN = "Vin blanc au verre";
const GLACE = "Glace vanille";
const PAIN = "Pain maison";

function normal(texte) {
    return String(texte ?? "").replace(/\s+/g, " ").trim();
}

function montant(valeur) {
    return normal(posmodel.env.utils.formatCurrency(valeur));
}

function ouvrir(table, code, personnes = null) {
    return [
        FloorScreen.clickTable(table),
        ...Aite.taperCode(code),
        ...(personnes ? Aite.personnes(personnes) : []),
        ...Aite.ecranCommande(),
    ];
}

function produits(...noms) {
    return noms.map((nom) => ProductScreen.clickDisplayedProduct(nom));
}

/** Les imprimantes de préparation remplacées par des imprimantes qui
 * gardent le texte de chaque bon ; `attendues` : leurs noms. */
function imprimantesSimulees(attendues) {
    return Aite.verifier("les imprimantes de préparation simulées", () => {
        window.aiteBons = {};
        const noms = [];
        for (const imprimante of posmodel.unwatched.printers) {
            const nom = imprimante.config.name;
            noms.push(nom);
            window.aiteBons[nom] = [];
            imprimante.printReceipt = async (el) => {
                window.aiteBons[nom].push(normal(el.textContent));
                return { successful: true };
            };
        }
        return noms.sort().join(",") === [...attendues].sort().join(",") || `imprimantes : ${noms}`;
    });
}

/** L'imprimante `nom` a reçu exactement `nombre` bons, qui contiennent tous
 * `presents` et aucun de `absents`. Les bons sont ensuite oubliés. */
function bons(nom, nombre, presents = [], absents = []) {
    return Aite.verifier(`${nombre} bon(s) sur « ${nom} »`, () => {
        const recus = window.aiteBons[nom] || [];
        if (recus.length !== nombre) {
            return `${recus.length} bon(s) : ${JSON.stringify(recus)}`;
        }
        for (const [i, texte] of recus.entries()) {
            for (const morceau of presents) {
                if (!texte.includes(morceau)) {
                    return `bon ${i + 1} : « ${morceau} » absent — ${texte}`;
                }
            }
            for (const morceau of absents) {
                if (texte.includes(morceau)) {
                    return `bon ${i + 1} : « ${morceau} » présent — ${texte}`;
                }
            }
        }
        window.aiteBons[nom] = [];
        return true;
    });
}

function attendre(ms = 800) {
    return {
        content: "laisser le temps à un bon d'arriver",
        trigger: "body",
        async run() {
            await new Promise((r) => setTimeout(r, ms));
        },
    };
}

function choisirLigne(nom) {
    return Aite.verifier(`choisir la ligne ${nom}`, () => {
        const order = posmodel.get_order();
        const ligne = order.lines.find((l) => l.get_product().name === nom);
        if (!ligne) {
            return "ligne introuvable";
        }
        order.select_orderline(ligne);
        return true;
    });
}

function noteGenerale(texte) {
    return [
        Aite.ouvrirActions(),
        {
            content: "« Note générale »",
            trigger: ".modal .control-buttons-modal button",
            run() {
                const libelle = _t("General Note");
                const bouton = [...document.querySelectorAll(".modal .control-buttons-modal button")].find(
                    (b) => b.textContent.trim() === libelle
                );
                if (!bouton) {
                    throw new Error(`bouton « ${libelle} » absent`);
                }
                bouton.click();
            },
        },
        { content: "la fenêtre de note", trigger: ".modal:not(.o_inactive_modal) textarea" },
        TextInputPopup.inputText(texte),
        Dialog.confirm(),
    ];
}

const SIX = [POULET, PIZZA, BURGER, VIN, GLACE, PAIN];

registry.category("web_tour.tours").add("AiteFamilleParenteTour", {
    steps: () =>
        [
            ...Aite.planVerrouille(),
            imprimantesSimulees(["Chaud", "Pizza", "Bar"]),
            ...ouvrir("5", "1111", "2"),
            ...produits(POULET, PIZZA, BURGER, VIN),
            Aite.jEnvoie(),
            ...Aite.planVerrouille(),
            // « Plats » coché : le poulet (sous-famille Grillades) ; « Burgers ».
            bons("Chaud", 1, [POULET, BURGER], [PIZZA, VIN]),
            bons("Pizza", 1, [PIZZA], [POULET, BURGER, VIN]),
            // « Bar » coché (niveau 1) : le vin blanc, au 3e niveau.
            bons("Bar", 1, [VIN], [POULET, PIZZA, BURGER]),
        ].flat(),
});

registry.category("web_tour.tours").add("AiteImprimanteAutreTour", {
    steps: () =>
        [
            ...Aite.planVerrouille(),
            imprimantesSimulees(["Chaud", "Pizza", "Bar", "Autre"]),
            ...ouvrir("5", "1111", "2"),
            ...produits(...SIX, PAIN),
            Aite.jEnvoie(),
            ...Aite.planVerrouille(),
            bons("Chaud", 1, [POULET, BURGER], [PIZZA, VIN, GLACE, PAIN]),
            bons("Pizza", 1, [PIZZA], [POULET, GLACE, PAIN]),
            bons("Bar", 1, [VIN], [GLACE, PAIN]),
            // Ce qu'aucune autre imprimante ne prend : le dessert (famille
            // non cochée) et le pain (sans famille), en 2 exemplaires.
            bons("Autre", 2, [GLACE, "2 " + PAIN, "Nouveau", "Exemplaire"], [POULET, PIZZA, BURGER, VIN]),
            // Une annulation suit le même chemin : sur « Autre » seulement.
            ...ouvrir("5", "1111"),
            choisirLigne(PAIN),
            ProductScreen.clickNumpad("⌫"),
            ProductScreen.clickNumpad("⌫"),
            ...Aite.popupAnnulation(),
            ...Aite.combien("1"),
            ...Aite.codeAnnulation("4444"),
            ...Aite.motif(0),
            Aite.pasDePopupAnnulation(),
            bons("Autre", 1, ["Annulé", "1 " + PAIN], ["Exemplaire"]),
            attendre(),
            bons("Chaud", 0),
            bons("Pizza", 0),
            bons("Bar", 0),
            // Une note générale tapée seule : les quatre imprimantes ont reçu
            // un plat de la table, les quatre la reçoivent.
            ...noteGenerale("Client pressé"),
            Aite.jEnvoie(),
            ...Aite.planVerrouille(),
            bons("Chaud", 1, ["Note générale", "Client pressé"]),
            bons("Pizza", 1, ["Note générale", "Client pressé"]),
            bons("Bar", 1, ["Note générale", "Client pressé"]),
            bons("Autre", 1, ["Note générale", "Client pressé"], ["Exemplaire"]),
        ].flat(),
});

/** L'envoi aux imprimantes Epson, sans les remplacer : la requête ePOS est
 * interceptée à la sortie du navigateur (aucune vraie imprimante). */
registry.category("web_tour.tours").add("AiteEpsonDirectTour", {
    steps: () =>
        [
            ...Aite.planVerrouille(),
            Aite.verifier("des imprimantes Epson ePOS, au protocole de la page", () => {
                const { EpsonPrinter } = odoo.loader.modules.get("@pos_epson_printer/app/epson_printer");
                const imprimantes = posmodel.unwatched.printers;
                if (imprimantes.length !== 2) {
                    return `${imprimantes.length} imprimantes`;
                }
                for (const imprimante of imprimantes) {
                    if (!(imprimante instanceof EpsonPrinter)) {
                        return `« ${imprimante.config.name} » n'est pas une imprimante Epson`;
                    }
                    const attendu = `${window.location.protocol}//${imprimante.config.epson_printer_ip}/cgi-bin/epos/service.cgi`;
                    if (!imprimante.address.startsWith(attendu)) {
                        return `adresse ${imprimante.address}`;
                    }
                }
                window.aiteEpos = [];
                window.aiteApercus = 0;
                window.print = () => {
                    window.aiteApercus += 1;
                };
                const vraiFetch = window.fetch;
                window.fetch = async (url, params) => {
                    if (String(url).includes("/cgi-bin/epos/service.cgi")) {
                        window.aiteEpos.push({ url: String(url), corps: String(params?.body || "") });
                        return new Response('<?xml version="1.0"?><response success="true" code="" status="1"/>', {
                            status: 200,
                            headers: { "Content-Type": "application/xml" },
                        });
                    }
                    return vraiFetch(url, params);
                };
                return true;
            }),
            ...ouvrir("5", "1111", "2"),
            ...produits(POULET, GLACE),
            Aite.jEnvoie(),
            ...Aite.planVerrouille(),
            // Chaud : 1 exemplaire ; Autre : 2 exemplaires (deux requêtes).
            Aite.verifier("une requête ePOS par exemplaire, une image et une coupe", () => {
                const requetes = window.aiteEpos || [];
                const adresses = requetes.map((r) => new URL(r.url).host).sort();
                if (JSON.stringify(adresses) !== JSON.stringify(["127.0.0.1", "127.0.0.4", "127.0.0.4"])) {
                    return `requêtes vers ${JSON.stringify(adresses)}`;
                }
                return (
                    requetes.every((r) => r.corps.includes("<image") && r.corps.includes("<cut")) ||
                    "requête sans image"
                );
            }),
            Aite.verifier("aucune fenêtre ni aperçu d'impression", () => {
                const fenetre = document.querySelector(".modal");
                if (fenetre) {
                    return `fenêtre : ${normal(fenetre.textContent).slice(0, 120)}`;
                }
                return window.aiteApercus === 0 || `${window.aiteApercus} aperçu(s)`;
            }),
        ].flat(),
});

// --------------------------------------------------------------- l'addition

function imprimanteDeTickets() {
    return Aite.verifier("une imprimante de tickets simulée", () => {
        window.aiteTickets = [];
        window.aiteTicketsHtml = [];
        posmodel.hardwareProxy.printer = {
            printReceipt: async (el) => {
                window.aiteTickets.push(normal(el.textContent));
                window.aiteTicketsHtml.push(el.outerHTML);
                return { successful: true };
            },
        };
        return true;
    });
}

function plusDImprimanteDeTickets() {
    return Aite.verifier("plus d'imprimante de tickets", () => {
        posmodel.hardwareProxy.printer = null;
        return true;
    });
}

function boutonAddition() {
    return {
        content: "« Addition »",
        trigger: ".control-buttons .aite-addition-btn:not([disabled])",
        run: "click",
    };
}

/** Les rubriques d'un ticket rendu : [{ titre, lignes: [texte], sousTotal }]. */
function rubriques(racine) {
    return [...racine.querySelectorAll(".aite-famille")].map((bloc) => ({
        titre: normal(bloc.querySelector(".aite-famille-titre")?.textContent),
        lignes: [...bloc.querySelectorAll(".orderline")].map((l) => normal(l.textContent)),
        sousTotal: normal(bloc.querySelector(".aite-famille-sous-total")?.textContent),
    }));
}

/** Le ticket table 5 : 2 poulets, 1 pizza, 1 burger, 1 vin, 1 pain. */
const ATTENDU = [
    ["Plats", [POULET], 14000],
    ["Pizzas & burgers", [PIZZA, BURGER], 9000],
    ["Bar", [VIN], 3000],
    ["Autres", [PAIN], 500],
];

/** `hors` : les lignes attendues après les familles, hors rubrique et sans
 * sous-total (pourboire, remise globale ; relecture de 18.0.1.0.14). */
function ticketGroupe(html, attendu = ATTENDU, hors = []) {
    const racine = document.createElement("div");
    racine.innerHTML = html;
    const lu = rubriques(racine);
    const blocHors = racine.querySelector(".aite-hors-familles");
    const luHors = blocHors ? [...blocHors.querySelectorAll(".orderline")].map((l) => normal(l.textContent)) : [];
    if (luHors.length !== hors.length || hors.some((n, k) => !luHors[k]?.includes(n))) {
        return `hors familles : ${JSON.stringify(luHors)} au lieu de ${JSON.stringify(hors)}`;
    }
    if (blocHors && (blocHors.closest(".aite-famille") || blocHors.querySelector(".aite-famille-sous-total"))) {
        return "les lignes hors familles ont une rubrique ou un sous-total";
    }
    if (lu.length !== attendu.length) {
        return `${lu.length} rubriques : ${JSON.stringify(lu)}`;
    }
    for (const [i, [titre, noms, sousTotal]] of attendu.entries()) {
        const rubrique = lu[i];
        if (rubrique.titre.toLowerCase() !== titre.toLowerCase()) {
            return `rubrique ${i + 1} : « ${rubrique.titre} » au lieu de « ${titre} »`;
        }
        if (rubrique.lignes.length !== noms.length || noms.some((n, k) => !rubrique.lignes[k]?.includes(n))) {
            return `${titre} : lignes ${JSON.stringify(rubrique.lignes)}`;
        }
        const phrase = normal(`Sous-total ${titre} : ${montant(sousTotal)}`);
        if (rubrique.sousTotal !== phrase) {
            return `${titre} : « ${rubrique.sousTotal} » au lieu de « ${phrase} »`;
        }
    }
    // Aucune ligne de produit hors d'une rubrique.
    const horsRubrique = [...racine.querySelectorAll(".orderline")].filter(
        (l) => !l.closest(".aite-famille") && !l.closest(".aite-hors-familles")
    );
    return !horsRubrique.length || `${horsRubrique.length} ligne(s) hors rubrique`;
}

function tableCinq() {
    return [
        ...ouvrir("5", "3333", "2"),
        ...produits(POULET, POULET, PIZZA, BURGER, VIN, PAIN),
        choisirLigne(PIZZA),
        Aite.ouvrirActions(),
        {
            content: "« Note au client »",
            trigger: ".modal .control-buttons-modal button:has(.fa-sticky-note)",
            run: "click",
        },
        { content: "la fenêtre de note", trigger: ".modal:not(.o_inactive_modal) textarea" },
        TextInputPopup.inputText("Bien chaude"),
        Dialog.confirm(),
        Aite.jEnvoie(),
        ...Aite.planVerrouille(),
        ...ouvrir("5", "3333"),
    ];
}

registry.category("web_tour.tours").add("AiteAdditionFamillesTour", {
    steps: () =>
        [
            ...Aite.planVerrouille(),
            imprimantesSimulees(["Chaud", "Pizza", "Bar"]),
            ...tableCinq(),
            Aite.verifier("la règle des rubriques (remise, pourboire, sans famille)", () => {
                const module = odoo.loader.modules.get("@aite_pos_restaurant/utils/familles");
                if (!module?.grouperParFamille) {
                    return "pas de règle des rubriques";
                }
                const familles = { 1: { cle: 1, titre: "Plats", rang: 2 }, 2: { cle: 2, titre: "Bar", rang: 5 } };
                const lignes = [
                    { nom: "Bière", famille: 2, montant: 1000 },
                    { nom: "Remise", horsFamille: true, montant: -500 },
                    { nom: "Poulet", famille: 1, montant: 7000 },
                    { nom: "Pourboire", horsFamille: true, montant: 1000 },
                    { nom: "Poulet rendu", famille: 1, montant: -7000 },
                    { nom: "Pain", famille: null, montant: 500 },
                ];
                const groupes = module.grouperParFamille(lignes, {
                    familleDe: (l) => familles[l.famille] || null,
                    horsFamille: (l) => Boolean(l.horsFamille),
                    montant: (l) => l.montant,
                    titreAutres: "Autres",
                });
                const lu = groupes.map((g) => [
                    g.titre,
                    g.lignes.map((l) => l.nom),
                    g.sousTotal,
                    Boolean(g.horsFamilles),
                ]);
                // Relecture (terrain, 3) : « Autres » ne garde que les
                // produits sans famille ; la remise et le pourboire viennent
                // après, hors rubrique (pas de « Sous-total Autres » négatif).
                const attendu = [
                    ["Plats", ["Poulet", "Poulet rendu"], 0, false],
                    ["Bar", ["Bière"], 1000, false],
                    ["Autres", ["Pain"], 500, false],
                    ["", ["Remise", "Pourboire"], 500, true],
                ];
                return JSON.stringify(lu) === JSON.stringify(attendu) || JSON.stringify(lu);
            }),
            imprimanteDeTickets(),
            boutonAddition(),
            Aite.verifier("l'addition groupée par famille, avec les sous-totaux", () => {
                const tickets = window.aiteTicketsHtml || [];
                if (tickets.length !== 1) {
                    return `${tickets.length} tickets`;
                }
                const groupe = ticketGroupe(tickets[0]);
                if (groupe !== true) {
                    return groupe;
                }
                const texte = window.aiteTickets[0];
                // Le total, la note au client restent ceux d'Odoo.
                return (
                    (texte.includes(montant(26500)) && texte.includes("Bien chaude")) || texte
                );
            }),
            // Après « Addition », la caisse revient au plan verrouillé.
            ...Aite.planVerrouille(),
            ...ouvrir("5", "3333"),
            // Le ticket final, à la validation (« Impression automatique »).
            imprimanteDeTickets(),
            Aite.jEncaisse(),
            PaymentScreen.isShown(),
            Aite.verifier("payer en espèces", () => {
                const especes = posmodel.models["pos.payment.method"].find((m) => m.is_cash_count);
                const bouton = [...document.querySelectorAll(".paymentmethods .button.paymentmethod")].find(
                    (b) => b.textContent.includes(especes.name)
                );
                if (!bouton) {
                    return "pas de bouton d'espèces";
                }
                window.aiteEspeces = especes.name;
                bouton.click();
                return true;
            }),
            PaymentScreen.clickValidate(),
            ...Aite.planVerrouille(),
            Aite.verifier("le ticket final groupé, paiements et total inchangés", () => {
                const tickets = window.aiteTicketsHtml || [];
                if (tickets.length !== 1) {
                    return `${tickets.length} tickets`;
                }
                const groupe = ticketGroupe(tickets[0]);
                if (groupe !== true) {
                    return groupe;
                }
                const texte = window.aiteTickets[0];
                return (texte.includes(montant(26500)) && texte.includes(window.aiteEspeces)) || texte;
            }),
            // La réimpression du ticket de la commande payée.
            imprimanteDeTickets(),
            {
                content: "réimprimer le ticket de la commande payée",
                trigger: "body",
                async run() {
                    const payee = posmodel.models["pos.order"].find((o) => o.finalized);
                    if (!payee) {
                        throw new Error("commande payée introuvable");
                    }
                    await posmodel.printReceipt({ order: payee });
                },
            },
            Aite.verifier("le ticket réimprimé est groupé", () => {
                const tickets = window.aiteTicketsHtml || [];
                return (tickets.length === 1 && ticketGroupe(tickets[0])) || `${tickets.length} tickets`;
            }),
            plusDImprimanteDeTickets(),
        ].flat(),
});

registry.category("web_tour.tours").add("AiteAdditionFamillesDiviseeTour", {
    steps: () =>
        [
            ...Aite.planVerrouille(),
            imprimantesSimulees(["Chaud", "Pizza", "Bar"]),
            ...ouvrir("5", "3333", "2"),
            ...produits(POULET, POULET, PIZZA, VIN),
            Aite.jEnvoie(),
            ...Aite.planVerrouille(),
            ...ouvrir("5", "3333"),
            // La part « 5B » : un poulet et le vin.
            Aite.ouvrirActions(),
            {
                content: "« Diviser l'addition »",
                trigger: ".modal .control-buttons-modal button:has(.fa-files-o)",
                run: "click",
            },
            { content: "l'écran de division", trigger: ".splitbill-screen" },
            SplitBillScreen.clickOrderline(POULET),
            SplitBillScreen.clickOrderline(VIN),
            SplitBillScreen.clickPay(),
            ...Aite.ecranCommande(),
            // Sans imprimante de tickets : la fenêtre des additions.
            boutonAddition(),
            { content: "la fenêtre des additions", trigger: ".modal .aite-additions .pos-receipt" },
            Aite.verifier("chaque addition groupée par famille", () => {
                const blocs = [...document.querySelectorAll(".modal .aite-additions .aite-addition")];
                if (blocs.length !== 2) {
                    return `${blocs.length} additions`;
                }
                const attendus = [
                    [["Plats", [POULET], 7000], ["Pizzas & burgers", [PIZZA], 5000]],
                    [["Plats", [POULET], 7000], ["Bar", [VIN], 3000]],
                ];
                for (const [i, bloc] of blocs.entries()) {
                    const resultat = ticketGroupe(bloc.querySelector(".pos-receipt").outerHTML, attendus[i]);
                    if (resultat !== true) {
                        return `addition ${i + 1} : ${resultat}`;
                    }
                }
                return true;
            }),
            Aite.fermerFenetre(),
        ].flat(),
});

registry.category("web_tour.tours").add("AiteAdditionSansFamillesTour", {
    steps: () =>
        [
            ...Aite.planVerrouille(),
            imprimantesSimulees(["Chaud", "Pizza", "Bar"]),
            ...tableCinq(),
            imprimanteDeTickets(),
            boutonAddition(),
            Aite.verifier("le ticket d'Odoo, sans rubrique ni sous-total", () => {
                const tickets = window.aiteTicketsHtml || [];
                if (tickets.length !== 1) {
                    return `${tickets.length} tickets`;
                }
                const racine = document.createElement("div");
                racine.innerHTML = tickets[0];
                if (racine.querySelector(".aite-famille, .aite-famille-titre, .aite-famille-sous-total")) {
                    return "rubriques présentes";
                }
                const texte = window.aiteTickets[0];
                if (texte.includes("Sous-total")) {
                    return texte;
                }
                // L'ordre des lignes d'Odoo : celui de la saisie.
                const lignes = [...racine.querySelectorAll(".orderline")].map((l) => normal(l.textContent));
                const ordre = [POULET, PIZZA, BURGER, VIN, PAIN];
                const ok = lignes.length === 5 && ordre.every((nom, k) => lignes[k].includes(nom));
                return (ok && texte.includes(montant(26500))) || JSON.stringify(lignes);
            }),
            plusDImprimanteDeTickets(),
        ].flat(),
});

// ------------------------------------------------- relectures de 18.0.1.0.14

/** Relecture (code, 8) : une imprimante « Autre » seule, sans aucune famille
 * cochée, est l'unique imprimante de la caisse : elle reçoit tout. */
registry.category("web_tour.tours").add("AiteAutreSeuleTour", {
    steps: () =>
        [
            ...Aite.planVerrouille(),
            imprimantesSimulees(["Autre"]),
            ...ouvrir("5", "1111", "2"),
            ...produits(POULET, PAIN),
            Aite.jEnvoie(),
            ...Aite.planVerrouille(),
            bons("Autre", 2, [POULET, PAIN, "Nouveau", "Exemplaire"]),
        ].flat(),
});

/** Relectures (code 8, terrain 3) : un pourboire saisi avant « J'envoie »
 * ne part sur aucune imprimante, « Autre » comprise ; sur l'addition
 * groupée, « Autres » ne garde que le pain (sans famille) et le pourboire
 * vient après les familles, sans rubrique ni sous-total. */
registry.category("web_tour.tours").add("AiteAutreHorsCuisineTour", {
    steps: () =>
        [
            ...Aite.planVerrouille(),
            imprimantesSimulees(["Chaud", "Pizza", "Bar", "Autre"]),
            ...ouvrir("5", "3333", "2"),
            ...produits(POULET, PAIN),
            {
                content: "un pourboire de 500 avant l'envoi",
                trigger: "body",
                async run() {
                    await posmodel.set_tip(500);
                    window.aitePourboire = posmodel.config.tip_product_id.name;
                },
            },
            Aite.jEnvoie(),
            ...Aite.planVerrouille(),
            Aite.verifier("le pourboire n'est sur aucun bon", () => {
                const nom = window.aitePourboire;
                for (const [imprimante, recus] of Object.entries(window.aiteBons)) {
                    if (recus.some((texte) => texte.includes(nom))) {
                        return `« ${nom} » sur « ${imprimante} » : ${JSON.stringify(recus)}`;
                    }
                }
                return true;
            }),
            bons("Chaud", 1, [POULET], [PAIN]),
            bons("Autre", 2, [PAIN], [POULET]),
            ...ouvrir("5", "3333"),
            imprimanteDeTickets(),
            boutonAddition(),
            Aite.verifier("« Autres » sans le pourboire ; le pourboire hors rubrique", () => {
                const tickets = window.aiteTicketsHtml || [];
                if (tickets.length !== 1) {
                    return `${tickets.length} tickets`;
                }
                const groupe = ticketGroupe(
                    tickets[0],
                    [
                        ["Plats", [POULET], 7000],
                        ["Autres", [PAIN], 500],
                    ],
                    [window.aitePourboire]
                );
                if (groupe !== true) {
                    return groupe;
                }
                return window.aiteTickets[0].includes(montant(8000)) || window.aiteTickets[0];
            }),
            ...Aite.planVerrouille(),
            plusDImprimanteDeTickets(),
        ].flat(),
});

/** Relecture (code, 7) : à séquence égale, les familles de l'addition
 * suivent leur nom, comme dans Odoo (pos.category : « sequence, name »). */
registry.category("web_tour.tours").add("AiteRegleOrdreFamillesTour", {
    steps: () =>
        [
            ...Aite.planVerrouille(),
            Aite.verifier("à séquence égale, l'ordre des noms", () => {
                const { grouperParFamille } = odoo.loader.modules.get("@aite_pos_restaurant/utils/familles");
                const familles = {
                    1: { cle: 1, titre: "Zébu grillé", rang: 0 },
                    2: { cle: 2, titre: "Apéritifs", rang: 0 },
                    3: { cle: 3, titre: "Desserts", rang: 1 },
                };
                const lignes = [
                    { nom: "Brochette", famille: 1 },
                    { nom: "Glace", famille: 3 },
                    { nom: "Kir", famille: 2 },
                ];
                const groupes = grouperParFamille(lignes, {
                    familleDe: (l) => familles[l.famille],
                    montant: () => 1000,
                    titreAutres: "Autres",
                });
                const titres = groupes.map((g) => g.titre);
                return (
                    JSON.stringify(titres) === JSON.stringify(["Apéritifs", "Zébu grillé", "Desserts"]) ||
                    JSON.stringify(titres)
                );
            }),
        ].flat(),
});

/** Relecture (code, 4 et 5) : ni une récompense de fidélité ou de
 * promotion (produit de remise d'un programme), ni la ligne mère d'un menu,
 * ne partent seules sur l'imprimante « Autre ». Un produit offert (une
 * pizza gratuite), lui, part en préparation. */
registry.category("web_tour.tours").add("AiteRegleHorsCuisineTour", {
    steps: () =>
        [
            ...Aite.planVerrouille(),
            Aite.verifier("la règle « hors cuisine »", () => {
                const module = odoo.loader.modules.get("@aite_pos_restaurant/utils/familles");
                if (!module?.estHorsCuisine) {
                    return "pas de règle estHorsCuisine";
                }
                const { estHorsCuisine, imprimantesDuProduit } = module;
                const speciaux = { pourboire: 10, remise: 11, recompenses: [12] };
                const cas = [
                    [{ id: 10, type: "service" }, true, "pourboire"],
                    [{ id: 11, type: "service" }, true, "remise globale"],
                    [{ id: 12, type: "service" }, true, "récompense de fidélité"],
                    [{ id: 13, type: "combo" }, true, "ligne mère d'un menu"],
                    [{ id: 14, type: "consu" }, false, "pizza (même offerte)"],
                ];
                for (const [produit, attendu, nom] of cas) {
                    if (estHorsCuisine(produit, speciaux) !== attendu) {
                        return `${nom} : ${!attendu}`;
                    }
                }
                // Un menu dont la famille est cochée sur Chaud y va encore ;
                // sans famille, il ne va pas seul sur « Autre ».
                const chaud = { nom: "Chaud", familles: [1] };
                const autre = { nom: "Autre", familles: [], autre: true };
                const routage = (familles, hors) =>
                    imprimantesDuProduit(
                        [chaud, autre],
                        familles,
                        (i) => i.familles,
                        (i) => Boolean(i.autre),
                        hors
                    ).map((i) => i.nom);
                const menuChaud = routage([1], estHorsCuisine({ id: 13, type: "combo" }, speciaux));
                const menuSansFamille = routage([-1], estHorsCuisine({ id: 13, type: "combo" }, speciaux));
                const pizza = routage([-1], estHorsCuisine({ id: 14, type: "consu" }, speciaux));
                return (
                    (JSON.stringify([menuChaud, menuSansFamille, pizza]) ===
                        JSON.stringify([["Chaud"], [], ["Autre"]])) ||
                    JSON.stringify([menuChaud, menuSansFamille, pizza])
                );
            }),
        ].flat(),
});

/** Relecture (code, 6) : Odoo servi en https, une Epson qui ne répond
 * pas : l'alerte « Bon non imprimé » dit, en français, d'ouvrir une fois
 * https://<IP> sur la tablette et d'accepter le certificat. */
registry.category("web_tour.tours").add("AiteRegleCertificatTour", {
    steps: () =>
        [
            ...Aite.planVerrouille(),
            Aite.verifier("le conseil du certificat", () => {
                const bons = odoo.loader.modules.get("@aite_pos_restaurant/utils/bons");
                const { MESSAGES } = odoo.loader.modules.get("@aite_pos_restaurant/utils/messages");
                if (!bons?.adressesACertifier) {
                    return "pas de règle adressesACertifier";
                }
                const epson = { config: { printer_type: "epson_epos", epson_printer_ip: "192.168.1.51" } };
                const iot = { config: { printer_type: "iot", proxy_ip: "192.168.1.9" } };
                const enHttps = bons.adressesACertifier("https:", false, [epson, iot]);
                if (JSON.stringify(enHttps) !== JSON.stringify(["192.168.1.51"])) {
                    return `https : ${JSON.stringify(enHttps)}`;
                }
                if (bons.adressesACertifier("http:", false, [epson]).length) {
                    return "conseil en http";
                }
                if (bons.adressesACertifier("https:", true, [epson]).length) {
                    return "conseil alors que la caisse parle en http aux imprimantes";
                }
                const texte = MESSAGES.bonNonImprime(["Chaud"], ["192.168.1.51"]);
                const sansConseil = MESSAGES.bonNonImprime(["Chaud"]);
                return (
                    (texte.includes("https://192.168.1.51") &&
                        texte.includes("certificat") &&
                        !sansConseil.includes("certificat") &&
                        !/\b(accept|secure|server|certificate)\b/i.test(texte)) ||
                    texte
                );
            }),
        ].flat(),
});
