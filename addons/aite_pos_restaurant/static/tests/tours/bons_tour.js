/* global posmodel, odoo */
/** Les bons de préparation et les notes (demandes du Messager : « imprimer
 * 3 fois d'un coup en cuisine » et « commentaires sur les commandes »).
 *
 * Écrits avant le développement : ils reproduisent les défauts constatés
 * et servent de spécification (18.0.1.0.13).
 *
 * Deux imprimantes de préparation, simulées par le tour : « Cuisine »
 * (famille Plats : Poulet DG, avec son accompagnement Riz ou Frites) et
 * « Bar » (famille Drinks : Coca-Cola). Chaque bon rendu est gardé dans
 * `window.aiteBons[nom de l'imprimante]` (son texte) ; une imprimante « en
 * panne » répond `successful: false`. La caisse est en français.
 *
 * - AiteBonsExemplairesTour (Cuisine réglée sur 3 exemplaires) : un envoi
 *   de plats sort 3 fois en cuisine, « Exemplaire 1/3 » à « 3/3 », en
 *   français (« Nouveau », « Table 5 »), une fois au bar (pas de mention
 *   d'exemplaire) ; une annulation sort en un exemplaire ; la règle des
 *   exemplaires (nouveaux plats mêlés d'annulations : 3 ; annulations,
 *   notes ou note générale seules : 1) ; une imprimante injoignable : une
 *   seule alerte, en français, et un seul essai.
 * - AiteNoteCoupureTour (B1) : « Note cuisine » sur une ligne envoyée à
 *   laquelle on a ajouté une unité ne change ni la quantité ni le total,
 *   n'ouvre pas la fenêtre des accompagnements et part en cuisine sans R29.
 * - AiteNoteIgnorerTour (B2) : « Ignorer » ne change rien — ni la note du
 *   plat, ni la ligne en partie envoyée, ni la note générale.
 * - AiteNoteClientTour (B3) : « Note au client » sur une ligne envoyée
 *   s'ouvre et s'enregistre.
 * - AiteNoteGeneraleSeuleTour (B4) : une note générale tapée seule est
 *   imprimée, sur les imprimantes qui ont déjà reçu un plat de la table, ou
 *   sur toutes si aucune n'en a reçu.
 * - AiteAdditionSansNoteTour (B5) : l'addition du client ne porte pas la
 *   note générale, mais porte la note au client.
 * - AiteBonEnFrancaisTour (B6) : le bon dit « Nouveau », « Annulé »,
 *   « Note », « Note générale » et « Table 5 ». */
import * as Chrome from "@point_of_sale/../tests/tours/utils/chrome_util";
import * as Dialog from "@point_of_sale/../tests/tours/utils/dialog_util";
import * as ProductScreen from "@point_of_sale/../tests/tours/utils/product_screen_util";
import * as ProductConfigurator from "@point_of_sale/../tests/tours/utils/product_configurator_util";
import * as TextInputPopup from "@point_of_sale/../tests/tours/utils/text_input_popup_util";
import * as FloorScreen from "@pos_restaurant/../tests/tours/utils/floor_screen_util";
import * as Aite from "@aite_pos_restaurant/../tests/tours/aite_util";
import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";

/** Les mots anglais (ou mal traduits) qui ne doivent pas paraître sur un bon. */
const ANGLAIS = /\b(New|Cancelled|Cancel|Message|Dine In|Take Out|By:|Tableau)\b/;

function normal(texte) {
    return (texte || "").replace(/\s+/g, " ").trim();
}

function ouvrir(table, code, personnes = null) {
    return [
        FloorScreen.clickTable(table),
        ...Aite.taperCode(code),
        ...(personnes ? Aite.personnes(personnes) : []),
        ...Aite.ecranCommande(),
    ];
}

/** Les imprimantes de préparation de la caisse remplacées par des
 * imprimantes qui gardent le texte de chaque bon. */
function imprimantesSimulees() {
    return Aite.verifier("les imprimantes de préparation simulées", () => {
        window.aiteBons = {};
        window.aitePanne = {};
        const noms = [];
        for (const imprimante of posmodel.unwatched.printers) {
            const nom = imprimante.config.name;
            noms.push(nom);
            window.aiteBons[nom] = [];
            imprimante.printReceipt = async (el) => {
                window.aiteBons[nom].push(normal(el.textContent));
                return window.aitePanne[nom]
                    ? { successful: false, message: { title: "Hors ligne", body: "" } }
                    : { successful: true };
            };
        }
        return noms.sort().join(",") === "Bar,Cuisine" || `imprimantes : ${noms}`;
    });
}

/** L'imprimante `nom` a reçu exactement `nombre` bons ; `test(textes)` doit
 * rendre vrai (sinon un texte d'erreur). Les bons sont ensuite oubliés. */
function bons(nom, nombre, test = () => true, delai = 5000) {
    return Aite.verifier(
        `${nombre} bon(s) sur « ${nom} »`,
        () => {
            const recus = window.aiteBons[nom] || [];
            if (recus.length !== nombre) {
                return `${recus.length} bon(s) : ${JSON.stringify(recus)}`;
            }
            const resultat = test(recus);
            if (resultat !== true) {
                return `${resultat} — ${JSON.stringify(recus)}`;
            }
            window.aiteBons[nom] = [];
            return true;
        },
        delai
    );
}

/** Aucun bon sur `nom` (après une attente : un bon pourrait arriver tard). */
function aucunBon(nom) {
    return [
        {
            content: "laisser le temps à un bon d'arriver",
            trigger: "body",
            async run() {
                await new Promise((r) => setTimeout(r, 800));
            },
        },
        bons(nom, 0),
    ];
}

/** Chaque texte contient tous les morceaux de `attendus` et aucun mot anglais. */
function contient(attendus) {
    return (textes) => {
        for (const [i, texte] of textes.entries()) {
            for (const morceau of attendus) {
                if (!texte.includes(morceau)) {
                    return `bon ${i + 1} : « ${morceau} » absent`;
                }
            }
            const anglais = texte.match(ANGLAIS);
            if (anglais) {
                return `bon ${i + 1} : « ${anglais[0]} »`;
            }
        }
        return true;
    };
}

function sansExemplaire(textes) {
    return textes.every((t) => !t.includes("Exemplaire")) || "mention « Exemplaire » sur un bon unique";
}

function poulet(accompagnement = "Riz") {
    return [
        ProductScreen.clickDisplayedProduct("Poulet DG"),
        ProductConfigurator.pickRadio(accompagnement),
        Dialog.confirm(),
    ];
}

/** Aucune fenêtre ouverte (la fenêtre des accompagnements ne doit pas se
 * rouvrir quand on pose une note). */
function aucuneFenetre() {
    return [
        {
            content: "laisser le temps à une fenêtre de s'ouvrir",
            trigger: "body",
            async run() {
                await new Promise((r) => setTimeout(r, 600));
            },
        },
        Aite.verifier("aucune fenêtre ouverte", () =>
            !document.querySelector(".modal") ||
            `fenêtre : ${normal(document.querySelector(".modal").textContent).slice(0, 120)}`
        ),
    ];
}

/** Sélectionne la ligne de `nom` dont la note cuisine vaut `note` (et la
 * quantité `quantite`, si elle est donnée). */
function choisirLigne(nom, note = "", quantite = null) {
    return Aite.verifier(`choisir la ligne ${nom} [${note}]`, () => {
        const order = posmodel.get_order();
        const ligne = order.lines.find(
            (l) =>
                l.get_product().name === nom &&
                (l.getNote() || "") === note &&
                (quantite === null || l.get_quantity() === quantite)
        );
        if (!ligne) {
            return "ligne introuvable";
        }
        order.select_orderline(ligne);
        return true;
    });
}

/** Le total de l'addition et le nombre total d'unités de `nom`. */
function addition(nom, unites, total) {
    return Aite.verifier(`${unites} ${nom}, total ${total}`, () => {
        const order = posmodel.get_order();
        const lu = order.lines
            .filter((l) => l.get_product().name === nom)
            .reduce((somme, l) => somme + l.get_quantity(), 0);
        const montant = order.get_total_with_tax();
        return (lu === unites && Math.abs(montant - total) < 0.01) || `${lu} unités, total ${montant}`;
    });
}

/** « Ignorer » dans la fenêtre de note. */
function ignorer() {
    return {
        content: "« Ignorer »",
        trigger: ".modal:not(.o_inactive_modal) .modal-footer .btn-secondary",
        run: "click",
    };
}

function fenetreDeNote() {
    return { content: "la fenêtre de note", trigger: ".modal:not(.o_inactive_modal) textarea" };
}

/** « Note générale », dans « Actions ». */
function noteGenerale() {
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
        fenetreDeNote(),
    ];
}

/** « Note au client », dans « Actions » (le bouton à l'icône de note). */
function noteAuClient() {
    return [
        Aite.ouvrirActions(),
        {
            content: "« Note au client »",
            trigger: ".modal .control-buttons-modal button:has(.fa-sticky-note)",
            run: "click",
        },
    ];
}

function noteGeneraleVaut(attendu) {
    return Aite.verifier(`note générale « ${attendu} »`, () =>
        (posmodel.get_order().general_note || "") === attendu ||
        `note générale « ${posmodel.get_order().general_note} »`
    );
}

/** La règle des exemplaires (module pur), lue dans la caisse. */
function regle() {
    return odoo.loader.modules.get("@aite_pos_restaurant/utils/bons");
}

registry.category("web_tour.tours").add("AiteBonsExemplairesTour", {
    steps: () =>
        [
            ...Aite.planVerrouille(),
            imprimantesSimulees(),
            ...ouvrir("5", "1111", "2"),
            ...poulet("Riz"),
            ...poulet("Riz"),
            ProductScreen.clickDisplayedProduct("Coca-Cola"),
            Aite.jEnvoie(),
            ...Aite.planVerrouille(),
            // Trois exemplaires identiques en cuisine, numérotés.
            bons("Cuisine", 3, (textes) => {
                const base = contient(["Nouveau", "Table 5", "2 Poulet DG", "Riz", "Awa"])(textes);
                if (base !== true) {
                    return base;
                }
                for (const [i, texte] of textes.entries()) {
                    if (!texte.includes(`Exemplaire ${i + 1}/3`)) {
                        return `bon ${i + 1} : « Exemplaire ${i + 1}/3 » absent`;
                    }
                }
                const sansMention = textes.map((t) => t.replace(/Exemplaire \d\/3/, ""));
                return sansMention.every((t) => t === sansMention[0]) || "exemplaires différents";
            }),
            // Un seul au bar, sans mention d'exemplaire.
            bons("Bar", 1, (textes) => {
                const base = contient(["Nouveau", "Table 5", "1 Coca-Cola"])(textes);
                return base === true ? sansExemplaire(textes) : base;
            }),
            // Une annulation : un seul exemplaire.
            ...ouvrir("5", "1111"),
            choisirLigne("Poulet DG"),
            ProductScreen.clickNumpad("⌫"),
            ProductScreen.clickNumpad("⌫"),
            ...Aite.popupAnnulation(),
            ...Aite.combien("1"),
            ...Aite.codeAnnulation("4444"),
            ...Aite.motif(0),
            Aite.pasDePopupAnnulation(),
            bons("Cuisine", 1, (textes) => {
                const base = contient(["Annulé", "Table 5", "1 Poulet DG"])(textes);
                return base === true ? sansExemplaire(textes) : base;
            }),
            ...aucunBon("Bar"),
            // La règle : des nouveaux plats (même mêlés d'annulations) → le
            // réglage ; des annulations, des notes, une note générale seules → 1.
            Aite.verifier("la règle des exemplaires", () => {
                const { nombreDExemplaires } = regle();
                const plat = { quantity: 1 };
                const cas = [
                    [{ nouveau: [plat], annule: [], notes: [], noteGenerale: "" }, 3, 3],
                    [{ nouveau: [plat], annule: [plat], notes: [], noteGenerale: "" }, 3, 3],
                    [{ nouveau: [], annule: [plat], notes: [plat], noteGenerale: "" }, 3, 1],
                    [{ nouveau: [], annule: [], notes: [], noteGenerale: "Client pressé" }, 3, 1],
                    [{ nouveau: [plat], annule: [], notes: [], noteGenerale: "" }, 1, 1],
                    [{ nouveau: [plat], annule: [], notes: [], noteGenerale: "" }, undefined, 1],
                ];
                for (const [sections, reglage, attendu] of cas) {
                    const lu = nombreDExemplaires(sections, reglage);
                    if (lu !== attendu) {
                        return `${JSON.stringify(sections)} / ${reglage} : ${lu} au lieu de ${attendu}`;
                    }
                }
                return true;
            }),
            // La cuisine ne répond plus : une seule alerte, un seul essai.
            Aite.verifier("la cuisine tombe en panne", () => {
                window.aitePanne.Cuisine = true;
                return true;
            }),
            ...poulet("Frites"),
            Aite.jEnvoie(),
            bons("Cuisine", 1),
            Aite.verifier("une seule alerte, en français", () => {
                const fenetres = [...document.querySelectorAll(".modal .modal-content")];
                if (fenetres.length !== 1) {
                    return `${fenetres.length} fenêtres`;
                }
                const texte = normal(fenetres[0].textContent);
                return (
                    (texte.includes("Cuisine") &&
                        texte.includes("imprim") &&
                        !/Printing failed|Failed in printing/.test(texte)) ||
                    texte
                );
            }),
            Dialog.confirm(),
            ...Aite.planVerrouille(),
        ].flat(),
});

/** Trois poulets envoyés à la table 4, puis un quatrième saisi. */
function troisEnvoyesUnDePlus() {
    return [
        ...ouvrir("4", "1111", "2"),
        ...poulet("Riz"),
        ...poulet("Riz"),
        ...poulet("Riz"),
        Aite.jEnvoie(),
        ...Aite.planVerrouille(),
        bons("Cuisine", 1, contient(["3 Poulet DG"])),
        ...ouvrir("4", "1111"),
        ...poulet("Riz"),
        Aite.lignesDuProduit("Poulet DG", ["4/"]),
        addition("Poulet DG", 4, 28000),
    ];
}

registry.category("web_tour.tours").add("AiteNoteCoupureTour", {
    steps: () =>
        [
            ...Aite.planVerrouille(),
            imprimantesSimulees(),
            ...troisEnvoyesUnDePlus(),
            Aite.noteCuisine(),
            fenetreDeNote(),
            TextInputPopup.inputText("bien cuit"),
            Dialog.confirm(),
            ...aucuneFenetre(),
            Aite.lignesDuProduit("Poulet DG", ["3/", "1/bien cuit"]),
            addition("Poulet DG", 4, 28000),
            Aite.pasDErreur(),
            Aite.jEnvoie(),
            ...Aite.planVerrouille(),
            bons("Cuisine", 1, contient(["1 Poulet DG", "bien cuit"])),
            ...ouvrir("4", "1111"),
            Aite.lignesDuProduit("Poulet DG", ["3/", "1/bien cuit"]),
            addition("Poulet DG", 4, 28000),
            Chrome.clickPlanButton(),
            ...Aite.planVerrouille(),
        ].flat(),
});

registry.category("web_tour.tours").add("AiteNoteIgnorerTour", {
    steps: () =>
        [
            ...Aite.planVerrouille(),
            imprimantesSimulees(),
            ...troisEnvoyesUnDePlus(),
            // Une ligne en partie envoyée : « Ignorer » ne la coupe pas.
            Aite.noteCuisine(),
            fenetreDeNote(),
            ignorer(),
            ...aucuneFenetre(),
            Aite.lignesDuProduit("Poulet DG", ["4/"]),
            addition("Poulet DG", 4, 28000),
            Aite.jEnvoie(),
            ...Aite.planVerrouille(),
        ].flat(),
});

/** B2, la note d'un plat (relecture de 18.0.1.0.13 : un tour par cas, pour
 * voir chacun échouer avant la correction). */
registry.category("web_tour.tours").add("AiteNoteIgnorerNotePlatTour", {
    steps: () =>
        [
            ...Aite.planVerrouille(),
            imprimantesSimulees(),
            ...ouvrir("4", "1111", "2"),
            ProductScreen.clickDisplayedProduct("Coca-Cola"),
            Aite.noteCuisine(),
            fenetreDeNote(),
            TextInputPopup.inputText("sans glaçon"),
            Dialog.confirm(),
            Aite.lignesDuProduit("Coca-Cola", ["1/sans glaçon"]),
            Aite.noteCuisine(),
            fenetreDeNote(),
            TextInputPopup.inputText("autre chose"),
            ignorer(),
            ...aucuneFenetre(),
            Aite.lignesDuProduit("Coca-Cola", ["1/sans glaçon"]),
            Aite.jEnvoie(),
            ...Aite.planVerrouille(),
        ].flat(),
});

/** B2, la note générale. */
registry.category("web_tour.tours").add("AiteNoteIgnorerNoteGeneraleTour", {
    steps: () =>
        [
            ...Aite.planVerrouille(),
            imprimantesSimulees(),
            ...ouvrir("4", "1111", "2"),
            ProductScreen.clickDisplayedProduct("Coca-Cola"),
            ...noteGenerale(),
            TextInputPopup.inputText("Client pressé"),
            Dialog.confirm(),
            noteGeneraleVaut("Client pressé"),
            ...noteGenerale(),
            TextInputPopup.inputText("autre chose"),
            ignorer(),
            ...aucuneFenetre(),
            noteGeneraleVaut("Client pressé"),
            Aite.jEnvoie(),
            ...Aite.planVerrouille(),
        ].flat(),
});

registry.category("web_tour.tours").add("AiteNoteClientTour", {
    steps: () =>
        [
            ...Aite.planVerrouille(),
            imprimantesSimulees(),
            ...ouvrir("4", "1111", "2"),
            ...poulet("Riz"),
            Aite.jEnvoie(),
            ...Aite.planVerrouille(),
            ...ouvrir("4", "1111"),
            choisirLigne("Poulet DG"),
            ...noteAuClient(),
            fenetreDeNote(),
            Aite.pasDErreur(),
            TextInputPopup.inputText("Joyeux anniversaire"),
            Dialog.confirm(),
            Aite.pasDErreur(),
            Aite.verifier("la note au client est posée", () => {
                const ligne = posmodel.get_order().get_selected_orderline();
                return ligne?.get_customer_note() === "Joyeux anniversaire" || `« ${ligne?.get_customer_note()} »`;
            }),
            Aite.lignesDuProduit("Poulet DG", ["1/"]),
            addition("Poulet DG", 1, 7000),
            Chrome.clickPlanButton(),
            ...Aite.planVerrouille(),
        ].flat(),
});

registry.category("web_tour.tours").add("AiteNoteGeneraleSeuleTour", {
    steps: () =>
        [
            ...Aite.planVerrouille(),
            imprimantesSimulees(),
            // Table 2 : du pain, qu'aucune imprimante ne prépare. La note
            // générale part alors sur toutes les imprimantes.
            ...ouvrir("2", "1111", "2"),
            ProductScreen.clickDisplayedProduct("Pain"),
            Aite.jEnvoie(),
            ...Aite.planVerrouille(),
            ...aucunBon("Cuisine"),
            bons("Bar", 0),
            ...ouvrir("2", "1111"),
            choisirLigne("Pain"),
            ...noteGenerale(),
            TextInputPopup.inputText("Allergie arachide"),
            Dialog.confirm(),
            Aite.jEnvoie(),
            ...Aite.planVerrouille(),
            bons("Cuisine", 1, contient(["Allergie arachide", "Table 2"])),
            bons("Bar", 1, contient(["Allergie arachide", "Table 2"])),
            // Table 5 : la cuisine a reçu un plat ; la note seule y part, pas
            // au bar, et le plat n'est pas réimprimé.
            ...ouvrir("5", "1111", "2"),
            ...poulet("Riz"),
            Aite.jEnvoie(),
            ...Aite.planVerrouille(),
            bons("Cuisine", 1, contient(["1 Poulet DG", "Table 5"])),
            ...ouvrir("5", "1111"),
            choisirLigne("Poulet DG"),
            ...noteGenerale(),
            TextInputPopup.inputText("Client pressé"),
            Dialog.confirm(),
            Aite.jEnvoie(),
            ...Aite.planVerrouille(),
            bons("Cuisine", 1, (textes) => {
                const base = contient(["Client pressé", "Table 5"])(textes);
                if (base !== true) {
                    return base;
                }
                return !textes[0].includes("Poulet DG") || "le plat est réimprimé";
            }),
            ...aucunBon("Bar"),
            ...ouvrir("5", "1111"),
            Aite.verifier("plus rien à envoyer", () => {
                const changes = posmodel.getOrderChanges();
                return (!changes.count && changes.generalNote === undefined) || JSON.stringify(changes);
            }),
            Chrome.clickPlanButton(),
            ...Aite.planVerrouille(),
        ].flat(),
});

registry.category("web_tour.tours").add("AiteAdditionSansNoteTour", {
    steps: () =>
        [
            ...Aite.planVerrouille(),
            imprimantesSimulees(),
            ...ouvrir("5", "3333", "2"),
            ...poulet("Riz"),
            ...noteGenerale(),
            TextInputPopup.inputText("Client pressé"),
            Dialog.confirm(),
            choisirLigne("Poulet DG"),
            ...noteAuClient(),
            fenetreDeNote(),
            TextInputPopup.inputText("Joyeux anniversaire"),
            Dialog.confirm(),
            // L'écran tourné vers le client ne montre pas la note générale
            // (relecture de 18.0.1.0.13).
            Aite.verifier("l'écran du client sans la note générale", () => {
                const donnees = posmodel.get_order().getCustomerDisplayData();
                return donnees.generalNote === "" || `« ${donnees.generalNote} »`;
            }),
            Aite.jEnvoie(),
            ...Aite.planVerrouille(),
            ...ouvrir("5", "3333"),
            Aite.verifier("une imprimante de tickets simulée", () => {
                window.aiteTickets = [];
                posmodel.hardwareProxy.printer = {
                    printReceipt: async (el) => {
                        window.aiteTickets.push(normal(el.textContent));
                        return { successful: true };
                    },
                };
                return true;
            }),
            {
                content: "« Addition »",
                trigger: ".control-buttons .aite-addition-btn:not([disabled])",
                run: "click",
            },
            Aite.verifier("l'addition porte la note au client, pas la note générale", () => {
                const tickets = window.aiteTickets || [];
                if (tickets.length !== 1) {
                    return `${tickets.length} tickets`;
                }
                return (
                    (tickets[0].includes("Joyeux anniversaire") && !tickets[0].includes("Client pressé")) ||
                    tickets[0]
                );
            }),
            Aite.verifier("plus d'imprimante de tickets", () => {
                posmodel.hardwareProxy.printer = null;
                return true;
            }),
            ...Aite.planVerrouille(),
        ].flat(),
});

registry.category("web_tour.tours").add("AiteBonEnFrancaisTour", {
    steps: () =>
        [
            ...Aite.planVerrouille(),
            imprimantesSimulees(),
            ...ouvrir("5", "1111", "2"),
            ...poulet("Riz"),
            ...poulet("Riz"),
            ...noteGenerale(),
            TextInputPopup.inputText("Client pressé"),
            Dialog.confirm(),
            Aite.jEnvoie(),
            ...Aite.planVerrouille(),
            bons("Cuisine", 1, (textes) => {
                const base = contient(["Sur place", "Par", "Awa", "Table 5", "Nouveau", "2 Poulet DG", "Riz",
                    "Note générale", "Client pressé"])(textes);
                return base === true ? sansExemplaire(textes) : base;
            }),
            // Une note changée sur un plat envoyé : « Note ».
            ...ouvrir("5", "1111"),
            choisirLigne("Poulet DG"),
            Aite.noteCuisine(),
            fenetreDeNote(),
            TextInputPopup.inputText("bien cuit"),
            Dialog.confirm(),
            Aite.jEnvoie(),
            ...Aite.planVerrouille(),
            bons("Cuisine", 1, contient(["Note", "2 Poulet DG", "bien cuit", "Table 5"])),
            // Une annulation : « Annulé ».
            ...ouvrir("5", "1111"),
            choisirLigne("Poulet DG", "bien cuit"),
            ProductScreen.clickNumpad("⌫"),
            ProductScreen.clickNumpad("⌫"),
            ...Aite.popupAnnulation(),
            ...Aite.combien("1"),
            ...Aite.codeAnnulation("4444"),
            ...Aite.motif(0),
            Aite.pasDePopupAnnulation(),
            bons("Cuisine", 1, contient(["Annulé", "1 Poulet DG", "Table 5"])),
            Chrome.clickPlanButton(),
            ...Aite.planVerrouille(),
        ].flat(),
});

/* --------------------------------------------------------------------
 * Relecture de 18.0.1.0.13 : un tour par constat, écrit avant sa
 * correction (journal integ/journal_avant_integ.log).
 * ------------------------------------------------------------------ */

/** Une notification dont le texte contient `morceau` ; rend son texte. */
function notificationAvec(morceau) {
    return Aite.verifier(`notification « …${morceau}… »`, () =>
        [...document.querySelectorAll(".o_notification_content")].some((c) =>
            c.textContent.includes(morceau)
        ) || [...document.querySelectorAll(".o_notification_content")].map((c) => c.textContent).join(" | ")
    );
}

/** Aucune notification ne commence par `debut` et ne se termine par un
 * point sans autre précision (« Envoyé : Plats × 1. » seul). */
function pasDeNotificationExacte(texte) {
    return Aite.verifier(`pas de notification « ${texte} »`, () =>
        ![...document.querySelectorAll(".o_notification_content")].some(
            (c) => c.textContent.trim() === texte
        ) || `notification « ${texte} »`
    );
}

/** Constat 1 : 3 poulets envoyés, un 4e saisi, l'addition enregistrée
 * (retour au plan), puis « Note cuisine » : le journal des saisies ne doit
 * pas compter deux fois le 4e poulet (contrôle côté serveur). */
registry.category("web_tour.tours").add("AiteNoteCoupureSynchroTour", {
    steps: () =>
        [
            ...Aite.planVerrouille(),
            imprimantesSimulees(),
            ...troisEnvoyesUnDePlus(),
            // Retour au plan : l'addition (4 poulets) est enregistrée.
            Chrome.clickPlanButton(),
            ...Aite.planVerrouille(),
            Aite.verifier("l'addition enregistrée", () => {
                const order = posmodel.models["pos.order"].find((o) => o.table_id?.table_number === 4);
                return (order && typeof order.id === "number" && !posmodel.syncingOrders.has(order.id)) || "en cours";
            }),
            ...ouvrir("4", "1111"),
            choisirLigne("Poulet DG"),
            Aite.noteCuisine(),
            fenetreDeNote(),
            TextInputPopup.inputText("bien cuit"),
            Dialog.confirm(),
            ...aucuneFenetre(),
            Aite.lignesDuProduit("Poulet DG", ["3/", "1/bien cuit"]),
            addition("Poulet DG", 4, 28000),
            Aite.jEnvoie(),
            ...Aite.planVerrouille(),
            bons("Cuisine", 1, (textes) => {
                const base = contient(["1 Poulet DG", "bien cuit"])(textes);
                return base === true ? !textes[0].includes("3 Poulet DG") || "3 poulets réimprimés" : base;
            }),
        ].flat(),
});

/** Constat 2 : une note posée sur un plat entièrement parti, puis une unité
 * de plus au pavé : le bon dit « Nouveau 1 Poulet DG » (et « Note 3 Poulet
 * DG »), pas « Nouveau 3 Poulet DG ». */
registry.category("web_tour.tours").add("AiteNotePuisPlusUnTour", {
    steps: () =>
        [
            ...Aite.planVerrouille(),
            imprimantesSimulees(),
            ...ouvrir("5", "1111", "2"),
            ...poulet("Riz"),
            ...poulet("Riz"),
            ...poulet("Riz"),
            Aite.jEnvoie(),
            ...Aite.planVerrouille(),
            bons("Cuisine", 1, contient(["3 Poulet DG"])),
            ...ouvrir("5", "1111"),
            choisirLigne("Poulet DG"),
            Aite.noteCuisine(),
            fenetreDeNote(),
            TextInputPopup.inputText("bien cuit"),
            Dialog.confirm(),
            Aite.lignesDuProduit("Poulet DG", ["3/bien cuit"]),
            ProductScreen.clickNumpad("4"),
            Aite.lignesDuProduit("Poulet DG", ["4/bien cuit"]),
            addition("Poulet DG", 4, 28000),
            Aite.jEnvoie(),
            ...Aite.planVerrouille(),
            bons("Cuisine", 1, (textes) => {
                const base = contient(["Nouveau", "Note", "bien cuit"])(textes);
                if (base !== true) {
                    return base;
                }
                // Le texte du bon, sans espaces entre les blocs :
                // « …Nouveau1 Poulet DG- Rizbien cuitNote3 Poulet DG… ».
                const [nouveau = "", note = ""] = (textes[0].split("Nouveau")[1] || "").split("Note");
                return (
                    (nouveau.includes("1 Poulet DG") &&
                        !nouveau.includes("3 Poulet DG") &&
                        note.includes("3 Poulet DG")) ||
                    `Nouveau « ${nouveau} » / Note « ${note} »`
                );
            }),
        ].flat(),
});

/** Constat 5 : une erreur au rendu du bon (simulée) ne doit pas passer
 * inaperçue : l'alerte unique « Bon non imprimé » nomme l'imprimante, et
 * les autres imprimantes reçoivent leur bon. */
registry.category("web_tour.tours").add("AiteBonRenduEnErreurTour", {
    steps: () =>
        [
            ...Aite.planVerrouille(),
            imprimantesSimulees(),
            ...ouvrir("5", "1111", "2"),
            ...poulet("Riz"),
            ProductScreen.clickDisplayedProduct("Coca-Cola"),
            Aite.verifier("le rendu du bon de la cuisine échoue une fois", () => {
                const original = posmodel.aiteDonneesDuBon;
                let fois = 0;
                posmodel.aiteDonneesDuBon = function (order, sections) {
                    if (sections.nouveau.some((l) => (l.basic_name || l.name || "").includes("Poulet")) && !fois++) {
                        throw new Error("rendu simulé en erreur");
                    }
                    return original.call(this, order, sections);
                };
                return typeof original === "function" || "aiteDonneesDuBon absent";
            }),
            Aite.jEnvoie(),
            Aite.verifier("une seule alerte, qui nomme la cuisine", () => {
                const fenetres = [...document.querySelectorAll(".modal .modal-content")];
                if (fenetres.length !== 1) {
                    return `${fenetres.length} fenêtres`;
                }
                const texte = normal(fenetres[0].textContent);
                return (texte.includes("Cuisine") && texte.includes("Bon non imprimé")) || texte;
            }),
            Dialog.confirm(),
            bons("Bar", 1, contient(["1 Coca-Cola"])),
            Aite.verifier("plus de rendu simulé", () => {
                delete posmodel.aiteDonneesDuBon;
                return true;
            }),
            ...Aite.planVerrouille(),
        ].flat(),
});

/** Constat 9 : la cuisine ne répond pas. La notification ne dit pas
 * seulement « Envoyé » : elle dit que le bon de la cuisine n'est pas sorti. */
registry.category("web_tour.tours").add("AiteBonPanneNotificationTour", {
    steps: () =>
        [
            ...Aite.planVerrouille(),
            imprimantesSimulees(),
            Aite.verifier("la cuisine en panne", () => {
                window.aitePanne.Cuisine = true;
                return true;
            }),
            ...ouvrir("5", "1111", "2"),
            ...poulet("Riz"),
            ProductScreen.clickDisplayedProduct("Coca-Cola"),
            Aite.jEnvoie(),
            Aite.verifier("l'alerte « Bon non imprimé »", () =>
                normal(document.querySelector(".modal .modal-content")?.textContent).includes("Cuisine") || "pas d'alerte"
            ),
            Dialog.confirm(),
            ...Aite.planVerrouille(),
            notificationAvec("Cuisine"),
            notificationAvec("n'est pas sorti"),
            pasDeNotificationExacte("Envoyé\u00a0: Plats\u00a0×\u00a01, Drinks\u00a0×\u00a01."),
            bons("Bar", 1),
        ].flat(),
});

/** Constat 6 : une note effacée sur un plat déjà parti : le bon dit « Note
 * retirée : sans glaçon », pas un plat sans rien. */
registry.category("web_tour.tours").add("AiteNoteRetireeTour", {
    steps: () =>
        [
            ...Aite.planVerrouille(),
            imprimantesSimulees(),
            ...ouvrir("5", "1111", "2"),
            ProductScreen.clickDisplayedProduct("Coca-Cola"),
            Aite.noteCuisine(),
            fenetreDeNote(),
            TextInputPopup.inputText("sans glaçon"),
            Dialog.confirm(),
            Aite.jEnvoie(),
            ...Aite.planVerrouille(),
            bons("Bar", 1, contient(["1 Coca-Cola", "sans glaçon"])),
            ...ouvrir("5", "1111"),
            choisirLigne("Coca-Cola", "sans glaçon"),
            Aite.noteCuisine(),
            fenetreDeNote(),
            {
                content: "vider le champ",
                trigger: ".modal:not(.o_inactive_modal) textarea",
                run: "clear",
            },
            Dialog.confirm(),
            Aite.lignesDuProduit("Coca-Cola", ["1/"]),
            Aite.jEnvoie(),
            ...Aite.planVerrouille(),
            bons("Bar", 1, contient(["Note", "1 Coca-Cola", "Note retirée", "sans glaçon"])),
        ].flat(),
});

/** Constat 8 : la note générale porte le même nom partout — sur « J'envoie »
 * et dans « Envoyé : … », « Note générale », pas « Message ». */
registry.category("web_tour.tours").add("AiteNoteGeneraleLibelleTour", {
    steps: () =>
        [
            ...Aite.planVerrouille(),
            imprimantesSimulees(),
            ...ouvrir("5", "1111", "2"),
            ...poulet("Riz"),
            Aite.jEnvoie(),
            ...Aite.planVerrouille(),
            bons("Cuisine", 1),
            ...ouvrir("5", "1111"),
            choisirLigne("Poulet DG"),
            ...noteGenerale(),
            TextInputPopup.inputText("Client pressé"),
            Dialog.confirm(),
            Aite.verifier("« J'envoie » dit « Note générale »", () => {
                const texte = normal(document.querySelector(".actionpad .submit-order")?.textContent);
                return (texte.includes("Note générale") && !texte.includes("Message")) || texte;
            }),
            Aite.jEnvoie(),
            ...Aite.planVerrouille(),
            Aite.notificationExacte("Envoyé\u00a0: Note générale\u00a0×\u00a01."),
            bons("Cuisine", 1, contient(["Client pressé"])),
        ].flat(),
});
