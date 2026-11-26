/* global posmodel, odoo */
/** Partager l'addition à parts égales (demande du Messager : « diviser la
 * facture à part égale par le nombre de personnes qui doivent payer »).
 *
 * Écrits avant le développement : ils servent de spécification.
 *
 * - AitePartsEgalesTour : table 5, 3 personnes, 100 000 (Coca-Cola 60 000 +
 *   Water 40 000) ; la fenêtre présélectionne 3 ; 33 333 en espèces,
 *   33 333 par carte (supprimée puis refaite : le compteur suit), 33 334 en
 *   Mobile Money ; pas de monnaie sur une part intermédiaire ; le ticket dit
 *   « Partagée en 3 parts égales ».
 * - AitePartsEgalesChangerTour : table 4, 3 personnes, 75 001 ; la
 *   caissière choisit 2 : 37 500 par carte, puis la dernière part
 *   (37 501) en espèces, avec 40 000 tapés au pavé : 2 499 rendus.
 * - AitePartsEgalesAnnulerTour : table 2, 55 001 ; 10 000 en espèces
 *   d'abord, puis le partage du reste (45 001 → 15 000) ; retour au panier
 *   et retour au paiement : le partage est retrouvé ; « Annuler le partage »
 *   rend le comportement d'Odoo (la ligne suivante paie tout le reste).
 * - AitePartsEgalesArrondiTour : arrondi des espèces de 25 : 33 325,
 *   33 325, puis la dernière part en espèces arrondie par Odoo (33 350).
 * - AitePartsEgalesHorsModeTour : une caisse hors mode n'a pas le bouton.
 *
 * Après la revue :
 * - AitePartsEgalesMonnaieTour : la 1re personne donne 50 000 en espèces
 *   pour une part de 33 333 : « Monnaie à rendre : 16 667 », et la ligne
 *   revient à 33 333 au mode suivant ; une ligne ramenée à 0 ne compte pas
 *   pour une part ; la dernière part créée hors des boutons de mode (comme
 *   « Mettre sur ardoise ») compte ; « Annuler le partage » est caché quand
 *   toutes les parts sont encaissées.
 * - AitePartsEgalesArrondiRepartiTour : arrondi de 25, 8 010 en 3 : les pas
 *   restants vont aux dernières personnes (2 650, 2 675, puis 2 685 dont
 *   2 675 en espèces) ; la fenêtre dit « entre 2 650 et 2 675 » ; le
 *   bandeau de la dernière part dit le montant en espèces.
 * - AitePartsEgalesPourboireTour : un pourboire ajouté sur l'écran de
 *   paiement change le total : le partage est oublié, il se refait.
 *
 * Sélecteurs : classes aite-* et attributs data-aite-parts ; les textes
 * comparés sont ceux d'AITE (`TEXTES`, `TITRES`) et les montants passent
 * par le format de la caisse. */
import * as Chrome from "@point_of_sale/../tests/tours/utils/chrome_util";
import * as Dialog from "@point_of_sale/../tests/tours/utils/dialog_util";
import * as ProductScreen from "@point_of_sale/../tests/tours/utils/product_screen_util";
import * as PaymentScreen from "@point_of_sale/../tests/tours/utils/payment_screen_util";
import * as FloorScreen from "@pos_restaurant/../tests/tours/utils/floor_screen_util";
import * as Aite from "@aite_pos_restaurant/../tests/tours/aite_util";
import { registry } from "@web/core/registry";

const POPUP = ".modal:not(.o_inactive_modal) .aite-parts-popup";
const BANDEAU = ".payment-screen .aite-partage-bandeau";

function messages() {
    return odoo.loader.modules.get("@aite_pos_restaurant/utils/messages");
}

/** Un montant au format de la caisse (« 33 333 FCFA »). */
function montant(valeur) {
    return posmodel.env.utils.formatCurrency(valeur);
}

/** Un texte du module, espaces normalisées (insécables comprises). */
function normal(texte) {
    return String(texte ?? "").replace(/\s+/g, " ").trim();
}

function ouvrirLaTable(table, personnes, produits) {
    return [
        ...Aite.planVerrouille(),
        FloorScreen.clickTable(table),
        ...Aite.taperCode("1111"),
        ...Aite.personnes(personnes),
        ...produits.map((produit) => ProductScreen.clickDisplayedProduct(produit)),
        Aite.jEnvoie(),
        ...Aite.planVerrouille(),
        FloorScreen.clickTable(table),
        ...Aite.taperCode("3333"),
        ...Aite.ecranCommande(),
        Aite.jEncaisse(),
        PaymentScreen.isShown(),
    ];
}

function boutonPartager() {
    return [
        Aite.verifier("le libellé « Partager à parts égales »", () => {
            const bouton = document.querySelector(".payment-screen .aite-partage-btn");
            return (
                (Boolean(bouton) &&
                    normal(bouton.textContent) === normal(messages().TEXTES.partager)) ||
                `bouton : ${JSON.stringify(bouton?.textContent)}`
            );
        }),
        {
            content: "l'icône du bouton a un titre",
            trigger: ".payment-screen .aite-partage-btn i.fa[title]",
        },
        {
            content: "« Partager à parts égales »",
            trigger: ".payment-screen .aite-partage-btn",
            run: "click",
        },
        { content: "la fenêtre « Combien de personnes paient ? »", trigger: POPUP },
        Aite.verifier("le titre de la fenêtre", () => {
            const titre = document.querySelector(`${POPUP} .aite-parts-titre`)?.textContent;
            return normal(titre) === normal(messages().TITRES.combienPaient) || JSON.stringify(titre);
        }),
    ];
}

function choisi(nombre) {
    return {
        content: `${nombre} est choisi`,
        trigger: `${POPUP} [data-aite-parts="${nombre}"].aite-parts-choisi`,
    };
}

function choisir(nombre) {
    return [
        {
            content: `toucher ${nombre}`,
            trigger: `${POPUP} [data-aite-parts="${nombre}"]`,
            run: "click",
        },
        choisi(nombre),
    ];
}

function phrase(part) {
    return Aite.verifier(`« Chaque personne paiera ${part} »`, () => {
        const texte = document.querySelector(`${POPUP} .aite-parts-phrase`)?.textContent;
        return normal(texte) === normal(messages().TEXTES.chaquePersonne(montant(part))) ||
            JSON.stringify(texte);
    });
}

function phraseEntre(min, max) {
    return Aite.verifier(`« Chaque personne paiera entre ${min} et ${max} »`, () => {
        const texte = document.querySelector(`${POPUP} .aite-parts-phrase`)?.textContent;
        return normal(texte) ===
            normal(messages().TEXTES.chaquePersonneEntre(montant(min), montant(max))) ||
            JSON.stringify(texte);
    });
}

function monnaie(valeur) {
    return Aite.verifier(`« Monnaie à rendre : ${valeur} »`, () => {
        const texte = document.querySelector(`${BANDEAU} .aite-partage-monnaie`)?.textContent;
        return normal(texte) === normal(messages().TEXTES.monnaieARendre(montant(valeur))) ||
            JSON.stringify(texte);
    });
}

function pasDeMonnaieAuBandeau() {
    return {
        content: "le bandeau ne parle pas de monnaie",
        trigger: `${BANDEAU}:not(:has(.aite-partage-monnaie))`,
    };
}

function valider() {
    return [
        { content: "« Valider »", trigger: `${POPUP} .aite-parts-valider`, run: "click" },
        { content: "la fenêtre est fermée", trigger: "body:not(:has(.aite-parts-popup))" },
    ];
}

function bandeau(rang, nombre, part) {
    return Aite.verifier(`bandeau « Part ${rang} sur ${nombre} : ${part} »`, () => {
        const texte = document.querySelector(`${BANDEAU} .aite-partage-part`)?.textContent;
        return normal(texte) === normal(messages().TEXTES.part(rang, nombre, montant(part))) ||
            JSON.stringify(texte);
    });
}

function bandeauRegle(nombre) {
    return Aite.verifier(`bandeau « les ${nombre} parts sont réglées »`, () => {
        const texte = document.querySelector(`${BANDEAU} .aite-partage-part`)?.textContent;
        return normal(texte) === normal(messages().TEXTES.partsReglees(nombre)) ||
            JSON.stringify(texte);
    });
}

function pasDeBandeau() {
    return { content: "pas de bandeau de partage", trigger: `body:not(:has(${BANDEAU}))` };
}

/** Les lignes de paiement, dans l'ordre : [[mode, montant], …]. */
function lignes(attendu) {
    return Aite.verifier(`lignes de paiement ${JSON.stringify(attendu)}`, () => {
        const lues = posmodel
            .get_order()
            .payment_ids.map((ligne) => [ligne.payment_method_id.name, ligne.get_amount()]);
        return JSON.stringify(lues) === JSON.stringify(attendu) || JSON.stringify(lues);
    });
}

function pasDeMonnaie() {
    return Aite.verifier("aucune monnaie à rendre", () => {
        const order = posmodel.get_order();
        return order.get_change() <= 0 || `monnaie ${order.get_change()}`;
    });
}

function imprimanteSimulee() {
    return Aite.verifier("une imprimante de tickets simulée", () => {
        window.aiteTickets = [];
        posmodel.hardwareProxy.printer = {
            printReceipt: async (el) => {
                window.aiteTickets.push(el.textContent);
                return { successful: true };
            },
        };
        return true;
    });
}

function ticket(test, content) {
    return Aite.verifier(content, () => {
        const tickets = window.aiteTickets || [];
        if (tickets.length !== 1) {
            return `${tickets.length} tickets`;
        }
        return test(normal(tickets[0])) || normal(tickets[0]);
    });
}

function plusDImprimante() {
    return Aite.verifier("plus d'imprimante", () => {
        posmodel.hardwareProxy.printer = null;
        return true;
    });
}

function valide() {
    return [PaymentScreen.clickValidate(), ...Aite.planVerrouille()];
}

function mention(nombre) {
    return normal(messages().TEXTES.partagee(nombre));
}

registry.category("web_tour.tours").add("AitePartsEgalesTour", {
    steps: () =>
        [
            ...ouvrirLaTable("5", "3", ["Coca-Cola", "Water"]),
            Aite.verifier("le calcul des parts (FCFA, arrondi, centimes)", () => {
                const { montantDUnePart } = odoo.loader.modules.get(
                    "@aite_pos_restaurant/utils/parts_egales"
                );
                const cas = [
                    [montantDUnePart(100000, 3, 1), 33333],
                    [montantDUnePart(75001, 2, 1), 37500],
                    [montantDUnePart(100000, 3, 25), 33325],
                    [montantDUnePart(100, 3, 0.01), 33.33],
                    [montantDUnePart(10, 20, 1), 0],
                    // Sans arrondi : le dernier paie le reste (1 FCFA près).
                    [montantDUnePart(100001, 3, 1, 1), 33333],
                    [montantDUnePart(100001, 3, 1, 2), 33333],
                    [montantDUnePart(100001, 3, 1, 3), 33335],
                    // Avec l'arrondi de 25 : les pas restants vont aux
                    // dernières personnes.
                    [montantDUnePart(1000, 7, 25, 1), 125],
                    [montantDUnePart(1000, 7, 25, 3), 150],
                    [montantDUnePart(8010, 3, 25, 2), 2675],
                ];
                const faux = cas.filter(([lu, attendu]) => lu !== attendu);
                const { partsDuPartage } = odoo.loader.modules.get(
                    "@aite_pos_restaurant/utils/parts_egales"
                );
                const repartitions = [
                    [partsDuPartage(1000, 7, 25), [125, 125, 150, 150, 150, 150, 150]],
                    [partsDuPartage(8010, 3, 25), [2650, 2675, 2685]],
                    [partsDuPartage(100000, 3, 1), [33333, 33333, 33334]],
                    [partsDuPartage(1000, 7, 1), [142, 142, 142, 142, 142, 142, 148]],
                    [partsDuPartage(100, 3, 0.01, 0.01), [33.33, 33.33, 33.34]],
                ];
                for (const [lu, attendu] of repartitions) {
                    if (JSON.stringify(lu) !== JSON.stringify(attendu)) {
                        faux.push([lu, attendu]);
                    }
                }
                return !faux.length || JSON.stringify(faux);
            }),
            pasDeBandeau(),
            ...boutonPartager(),
            // Présélection : les 3 personnes de la table.
            choisi("3"),
            phrase(33333),
            // Au-delà de 8 : jusqu'à 20.
            { content: "« Plus »", trigger: `${POPUP} [data-aite-parts="plus"]`, run: "click" },
            { content: "20 est proposé", trigger: `${POPUP} [data-aite-parts="20"]` },
            { content: "pas de 21", trigger: `${POPUP}:not(:has([data-aite-parts="21"]))` },
            choisi("3"),
            ...valider(),
            bandeau(1, 3, 33333),
            {
                content: "« Annuler le partage » a un titre",
                trigger: `${BANDEAU} .aite-partage-annuler i.fa[title]`,
            },
            { content: "le bouton est caché pendant le partage", trigger: "body:not(:has(.aite-partage-btn))" },
            // Part 1 en espèces : la part, pas le reste dû ; aucune monnaie.
            PaymentScreen.clickPaymentMethod("Cash"),
            lignes([["Cash", 33333]]),
            pasDeMonnaie(),
            bandeau(2, 3, 33333),
            // Part 2 par carte, supprimée puis refaite : le compteur suit.
            PaymentScreen.clickPaymentMethod("Bank"),
            lignes([["Cash", 33333], ["Bank", 33333]]),
            bandeau(3, 3, 33334),
            {
                content: "supprimer la ligne de la carte",
                trigger: ".paymentlines .paymentline.selected .delete-button",
                run: "click",
            },
            lignes([["Cash", 33333]]),
            bandeau(2, 3, 33333),
            PaymentScreen.clickPaymentMethod("Bank"),
            lignes([["Cash", 33333], ["Bank", 33333]]),
            pasDeMonnaie(),
            bandeau(3, 3, 33334),
            // La dernière part : exactement le reste dû.
            PaymentScreen.clickPaymentMethod("Mobile Money"),
            lignes([["Cash", 33333], ["Bank", 33333], ["Mobile Money", 33334]]),
            bandeauRegle(3),
            Aite.verifier("tout est payé, sans monnaie", () => {
                const order = posmodel.get_order();
                return (order.is_paid() && order.get_change() === 0) ||
                    `payé ${order.is_paid()}, monnaie ${order.get_change()}`;
            }),
            imprimanteSimulee(),
            ...valide(),
            ticket(
                (texte) =>
                    texte.includes(mention(3)) &&
                    texte.includes(normal(montant(33334))) &&
                    texte.includes(normal(montant(33333))),
                "le ticket dit « Partagée en 3 parts égales »"
            ),
            plusDImprimante(),
        ].flat(),
});

registry.category("web_tour.tours").add("AitePartsEgalesChangerTour", {
    steps: () =>
        [
            ...ouvrirLaTable("4", "3", ["Coca-Cola", "Minute Maid"]),
            ...boutonPartager(),
            choisi("3"),
            phrase(25000),
            // Je change d'avis : 2 personnes paient.
            ...choisir("2"),
            phrase(37500),
            ...valider(),
            bandeau(1, 2, 37500),
            PaymentScreen.clickPaymentMethod("Bank"),
            lignes([["Bank", 37500]]),
            bandeau(2, 2, 37501),
            // La dernière part en espèces : la personne donne 40 000.
            PaymentScreen.clickPaymentMethod("Cash"),
            lignes([["Bank", 37500], ["Cash", 37501]]),
            bandeauRegle(2),
            PaymentScreen.enterPaymentLineAmount("Cash", "40000"),
            lignes([["Bank", 37500], ["Cash", 40000]]),
            Aite.verifier("2 499 à rendre", () => {
                const order = posmodel.get_order();
                return order.get_change() === 2499 || `monnaie ${order.get_change()}`;
            }),
            imprimanteSimulee(),
            ...valide(),
            ticket((texte) => texte.includes(mention(2)), "le ticket dit « Partagée en 2 parts égales »"),
            plusDImprimante(),
        ].flat(),
});

registry.category("web_tour.tours").add("AitePartsEgalesAnnulerTour", {
    steps: () =>
        [
            ...ouvrirLaTable("2", "3", ["Water", "Minute Maid"]),
            // Un premier paiement de 10 000 en espèces, tapé au pavé.
            PaymentScreen.clickPaymentMethod("Cash"),
            PaymentScreen.enterPaymentLineAmount("Cash", "10000"),
            lignes([["Cash", 10000]]),
            // Le partage du reste : 45 001 en 3.
            ...boutonPartager(),
            choisi("3"),
            phrase(15000),
            Aite.verifier("la fenêtre dit le reste dû", () => {
                const texte = document.querySelector(`${POPUP} .aite-parts-reste`)?.textContent;
                return normal(texte) === normal(messages().TEXTES.resteAPartager(montant(45001))) ||
                    JSON.stringify(texte);
            }),
            ...valider(),
            bandeau(1, 3, 15000),
            Aite.verifier("le bandeau dit le reste partagé", () => {
                const texte = document.querySelector(`${BANDEAU} .aite-partage-reste`)?.textContent;
                return normal(texte) === normal(messages().TEXTES.resteAPartager(montant(45001))) ||
                    JSON.stringify(texte);
            }),
            PaymentScreen.clickPaymentMethod("Bank"),
            lignes([["Cash", 10000], ["Bank", 15000]]),
            bandeau(2, 3, 15000),
            // Retour au panier, puis au paiement : le partage est retrouvé.
            {
                content: "« Retour » de l'écran de paiement",
                trigger: ".payment-screen .back-button",
                run: "click",
            },
            ...Aite.ecranCommande(),
            Aite.jEncaisse(),
            PaymentScreen.isShown(),
            bandeau(2, 3, 15000),
            // J'annule le partage : la ligne suivante paie tout le reste.
            {
                content: "« Annuler le partage »",
                trigger: `${BANDEAU} .aite-partage-annuler`,
                run: "click",
            },
            pasDeBandeau(),
            { content: "le bouton revient", trigger: ".payment-screen .aite-partage-btn" },
            PaymentScreen.clickPaymentMethod("Mobile Money"),
            lignes([["Cash", 10000], ["Bank", 15000], ["Mobile Money", 30001]]),
            imprimanteSimulee(),
            ...valide(),
            ticket((texte) => !texte.includes(mention(3)), "le ticket ne parle pas de partage"),
            plusDImprimante(),
        ].flat(),
});

registry.category("web_tour.tours").add("AitePartsEgalesArrondiTour", {
    steps: () =>
        [
            ...ouvrirLaTable("5", "3", ["Coca-Cola", "Water"]),
            ...boutonPartager(),
            choisi("3"),
            phrase(33325),
            ...valider(),
            bandeau(1, 3, 33325),
            PaymentScreen.clickPaymentMethod("Cash"),
            bandeau(2, 3, 33325),
            PaymentScreen.clickPaymentMethod("Bank"),
            bandeau(3, 3, 33350),
            PaymentScreen.clickPaymentMethod("Cash"),
            lignes([["Cash", 33325], ["Bank", 33325], ["Cash", 33350]]),
            bandeauRegle(3),
            ...valide(),
            { content: "pas d'erreur d'arrondi", trigger: "body:not(:has(.modal))" },
        ].flat(),
});

registry.category("web_tour.tours").add("AitePartsEgalesHorsModeTour", {
    steps: () =>
        [
            Chrome.startPoS(),
            Dialog.confirm("Open Register"),
            FloorScreen.clickTable("5"),
            ProductScreen.clickDisplayedProduct("Coca-Cola"),
            ProductScreen.clickPayButton(),
            PaymentScreen.isShown(),
            { content: "l'écran de paiement est affiché", trigger: ".payment-screen .paymentmethods" },
            {
                content: "pas de bouton « Partager à parts égales »",
                trigger: ".payment-screen:not(:has(.aite-partage-btn))",
            },
            Aite.verifier("le mode est éteint", () => posmodel.aiteActif === false),
        ].flat(),
});

/** Une ligne de paiement créée sans les boutons de mode, comme le fait
 * « Mettre sur ardoise » (aite_pos_credit) : add_paymentline puis le reste dû. */
function ligneHorsDesBoutons(nom) {
    return Aite.verifier(`une ligne ${nom} du reste dû, hors des boutons`, () => {
        const order = posmodel.get_order();
        const mode = posmodel.config.payment_method_ids.find((m) => m.name === nom);
        const du = order.get_due();
        const ligne = order.add_paymentline(mode);
        ligne.set_amount(du);
        return true;
    });
}

registry.category("web_tour.tours").add("AitePartsEgalesMonnaieTour", {
    steps: () =>
        [
            ...ouvrirLaTable("5", "3", ["Coca-Cola", "Water"]),
            ...boutonPartager(),
            choisi("3"),
            ...valider(),
            bandeau(1, 3, 33333),
            pasDeMonnaieAuBandeau(),
            // La 1re personne donne 50 000 en espèces pour sa part.
            PaymentScreen.clickPaymentMethod("Cash"),
            PaymentScreen.enterPaymentLineAmount("Cash", "50000"),
            lignes([["Cash", 50000]]),
            monnaie(16667),
            bandeau(2, 3, 33333),
            // Au mode suivant, la ligne des espèces garde la part : la caisse
            // enregistre ce qui reste dans le tiroir.
            PaymentScreen.clickPaymentMethod("Bank"),
            lignes([["Cash", 33333], ["Bank", 33333]]),
            pasDeMonnaieAuBandeau(),
            bandeau(3, 3, 33334),
            // Une ligne ramenée à 0 ne compte pas pour une part.
            Aite.verifier("la ligne de la carte ramenée à 0", () => {
                posmodel.get_order().get_selected_paymentline().set_amount(0);
                return true;
            }),
            bandeau(2, 3, 33333),
            PaymentScreen.clickPaymentMethod("Bank"),
            lignes([["Cash", 33333], ["Bank", 0], ["Bank", 33333]]),
            bandeau(3, 3, 33334),
            // La dernière part, créée hors des boutons (comme l'ardoise).
            ligneHorsDesBoutons("Mobile Money"),
            lignes([["Cash", 33333], ["Bank", 0], ["Bank", 33333], ["Mobile Money", 33334]]),
            bandeauRegle(3),
            {
                content: "« Annuler le partage » est caché : tout est encaissé",
                trigger: `${BANDEAU}:not(:has(.aite-partage-annuler))`,
            },
            pasDeMonnaie(),
            imprimanteSimulee(),
            ...valide(),
            ticket((texte) => texte.includes(mention(3)), "le ticket dit « Partagée en 3 parts égales »"),
            plusDImprimante(),
        ].flat(),
});

registry.category("web_tour.tours").add("AitePartsEgalesArrondiRepartiTour", {
    steps: () =>
        [
            ...ouvrirLaTable("5", "3", ["Minute Maid"]),
            ...boutonPartager(),
            choisi("3"),
            phraseEntre(2650, 2675),
            ...valider(),
            bandeau(1, 3, 2650),
            PaymentScreen.clickPaymentMethod("Cash"),
            bandeau(2, 3, 2675),
            PaymentScreen.clickPaymentMethod("Bank"),
            Aite.verifier("bandeau « Part 3 sur 3 : 2 685 FCFA (2 675 FCFA en espèces) »", () => {
                const texte = document.querySelector(`${BANDEAU} .aite-partage-part`)?.textContent;
                return normal(texte) ===
                    normal(messages().TEXTES.partEspeces(3, 3, montant(2685), montant(2675))) ||
                    JSON.stringify(texte);
            }),
            PaymentScreen.clickPaymentMethod("Cash"),
            lignes([["Cash", 2650], ["Bank", 2675], ["Cash", 2675]]),
            bandeauRegle(3),
            ...valide(),
            { content: "pas d'erreur d'arrondi", trigger: "body:not(:has(.modal))" },
        ].flat(),
});

registry.category("web_tour.tours").add("AitePartsEgalesPourboireTour", {
    steps: () =>
        [
            ...ouvrirLaTable("5", "3", ["Coca-Cola", "Water"]),
            ...boutonPartager(),
            choisi("3"),
            ...valider(),
            PaymentScreen.clickPaymentMethod("Cash"),
            lignes([["Cash", 33333]]),
            bandeau(2, 3, 33333),
            // Un pourboire de 5 000 ajouté sur l'écran de paiement.
            {
                content: "un pourboire de 5 000",
                trigger: ".payment-screen",
                async run() {
                    await posmodel.set_tip(5000);
                },
            },
            pasDeBandeau(),
            { content: "le bouton revient", trigger: ".payment-screen .aite-partage-btn" },
            // Le partage se refait sur le nouveau reste dû (71 667).
            ...boutonPartager(),
            ...choisir("2"),
            phrase(35833),
            ...valider(),
            bandeau(1, 2, 35833),
            PaymentScreen.clickPaymentMethod("Bank"),
            bandeau(2, 2, 35834),
            PaymentScreen.clickPaymentMethod("Mobile Money"),
            lignes([["Cash", 33333], ["Bank", 35833], ["Mobile Money", 35834]]),
            bandeauRegle(2),
            imprimanteSimulee(),
            ...valide(),
            ticket((texte) => texte.includes(mention(2)), "le ticket dit « Partagée en 2 parts égales »"),
            plusDImprimante(),
        ].flat(),
});
