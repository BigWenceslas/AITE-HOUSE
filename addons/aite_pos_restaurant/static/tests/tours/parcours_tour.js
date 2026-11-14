/* global posmodel */
/** Incrément 6 : AiteParcoursTour (spécification, parties 1.2 et 6.3) — un
 * service complet sur une caisse du restaurant, de l'ouverture de la caisse
 * à sa fermeture, rôle par rôle, qui joue chaque ligne de la partie 1.2 :
 * - la table 5 servie de bout en bout : la caissière ouvre la caisse, Awa
 *   (serveuse) ouvre la table 5 et envoie, revient ajouter un produit, change
 *   le nombre de personnes, retire ce qui n'est pas parti, se voit refuser un
 *   produit épuisé, fait annuler par Paul (chef de salle) un produit envoyé,
 *   imprime l'addition ; Carine (caissière) encaisse en espèces ;
 * - puis (revue de 6b, constat 8) les autres lignes : Paul seul annule un
 *   produit envoyé ; Carine encaisse au poste d'Awa restée identifiée ; Fanta
 *   (manager) encaisse une table ouverte par Awa, puis prend la main sur une
 *   addition ouverte au nom de Carine et l'encaisse ; Carine encaisse les deux
 *   parts d'une addition divisée ; Paul sort des espèces ; Paul seul annule
 *   une table ; Paul ferme la caisse avec deux tables encore ouvertes et les
 *   annule ; le lendemain, Carine rouvre la caisse et Paul la ferme sans table
 *   ouverte. La fenêtre de fermeture d'Odoo dit « Entrée ou sortie
 *   d'espèces », comme le menu ≡, et « 1 commande » au singulier (revue de 6b,
 *   constat 6).
 *
 * Une étape par touche (« run: click », ou les chiffres et les lettres tapés
 * d'un coup dans un champ) : chaque geste compte ses touches, les compare à
 * la partie 1.2 et écrit sa mesure dans le journal du test
 * (« AiteParcoursTour — … : n touche(s) »). Le compte déclaré de chaque
 * morceau est contrôlé contre les étapes réellement jouées.
 *
 * Comme les autres tours, ce fichier n'importe aucun module de la caisse :
 * il est aussi chargé dans la gestion. */
import * as Chrome from "@point_of_sale/../tests/tours/utils/chrome_util";
import * as Dialog from "@point_of_sale/../tests/tours/utils/dialog_util";
import * as ProductScreen from "@point_of_sale/../tests/tours/utils/product_screen_util";
import * as PaymentScreen from "@point_of_sale/../tests/tours/utils/payment_screen_util";
import * as FloorScreen from "@pos_restaurant/../tests/tours/utils/floor_screen_util";
import * as SplitBillScreen from "@pos_restaurant/../tests/tours/utils/split_bill_screen_util";
import * as Aite from "@aite_pos_restaurant/../tests/tours/aite_util";
import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";

const TABLE = "5";
/** Les espèces comptées à la fermeture : les additions encaissées en
 * espèces (table 5 : 1 500 ; table 4 : 1 000 ; table 2 : 1 000 puis 500 ;
 * les deux parts de la table 4 : 500 et 1 000), moins la sortie de 1 000.
 * Le lendemain, la caisse s'ouvre avec ce fond, et se ferme sans vente. */
const ESPECES = "4500";
const SORTIE = "1000";
const MOTIF_SORTIE = "Monnaie";

/** Un morceau de geste qui coûte `touches` touches à l'écran. */
function touche(touches, ...etapes) {
    return { touches, etapes: etapes.flat() };
}

/** Des chiffres tapés d'un coup dans un champ (une étape « edit ») : autant
 * de touches que de chiffres. */
function chiffres(valeur, etape) {
    return { touches: valeur.length, saisie: true, etapes: [{ ...etape, run: `edit ${valeur}` }] };
}

/** Des lettres tapées d'un coup dans un champ : une touche par lettre. */
const lettres = chiffres;

/** Des vérifications, sans aucune touche. */
function rien(...etapes) {
    return { touches: 0, etapes: etapes.flat() };
}

/** Les clics réellement joués par les étapes (les étapes réservées au
 * téléphone ne jouent pas sur la tablette). */
function clicsJoues(etapes) {
    return etapes.filter((e) => {
        if (e.isActive?.includes("mobile") && !e.isActive.includes("desktop")) {
            return false;
        }
        return (
            e.run === "click" ||
            (typeof e.run === "string" && e.run.startsWith("edit ")) ||
            (typeof e.run === "function" && String(e.content).startsWith("click numpad button"))
        );
    }).length;
}

/** Un geste de la partie 1.2 : ses morceaux, puis la mesure (et la
 * comparaison si `attendu` est donné ; `null` : geste hors du tableau). */
function geste(nom, attendu, morceaux) {
    const touches = morceaux.reduce((somme, m) => somme + m.touches, 0);
    const ecarts = morceaux
        .map((m) => {
            const joues = clicsJoues(m.etapes);
            const declares = m.saisie ? 1 : m.touches;
            return joues === declares
                ? null
                : `${nom} : ${joues} clic(s) joué(s) pour ${declares} déclaré(s)`;
        })
        .filter(Boolean);
    const mesure = `AiteParcoursTour — ${nom} : ${touches} touche(s)${
        attendu === null ? " (hors partie 1.2)" : `, partie 1.2 : ${attendu}`
    }`;
    return {
        nom,
        touches,
        etapes: [
            ...ecarts.map((ecart) => ({
                content: `compte des touches : ${ecart}`,
                trigger: "body",
                run() {
                    throw new Error(ecart);
                },
            })),
            ...morceaux.flatMap((m) => m.etapes),
            {
                content: mesure,
                trigger: "body",
                run() {
                    console.log(mesure);
                    if (attendu !== null && touches !== attendu) {
                        throw new Error(`${nom} : ${touches} touches au lieu de ${attendu}`);
                    }
                },
            },
        ],
    };
}

function ouvrirSaTable(code, table = TABLE) {
    return [touche(1, FloorScreen.clickTable(table)), touche(code.length, Aite.taperCode(code))];
}

/** Une table libre ouverte par `code`, `personnes`, des produits, puis
 * « J'envoie » (7 + n). */
function tableEnvoyee(table, code, personnes, produits) {
    return [
        ...ouvrirSaTable(code, table),
        touche(1, Aite.personnes(personnes)),
        rien(...Aite.ecranCommande()),
        ...produits.map((produit) => touche(1, ProductScreen.clickDisplayedProduct(produit))),
        touche(1, Aite.jEnvoie()),
        rien(...Aite.planVerrouille()),
    ];
}

/** « Espèces », « Valider » : l'addition est payée. */
function especesValider() {
    return [
        rien(PaymentScreen.isShown()),
        touche(1, PaymentScreen.clickPaymentMethod("Cash")),
        touche(1, PaymentScreen.clickValidate()),
    ];
}

/** L'addition courante est celle de la table `numero` (`part` : la part
 * « 4B » d'une division, qui n'a pas de table et garde son origine ; sinon
 * l'addition de la table elle-même). */
function additionCourante(numero, part = false) {
    return Aite.verifier(`l'addition ${part ? "à part " : ""}de la table ${numero}`, () => {
        const order = posmodel.get_order();
        const origine = order?.aite_origine_uuid
            ? posmodel.models["pos.order"].find((o) => o.uuid === order.aite_origine_uuid)
            : null;
        const table = (part ? origine : order)?.table_id?.table_number;
        return (
            (table === numero && Boolean(origine) === part) ||
            `table ${table}, part ${Boolean(origine)}`
        );
    });
}

/** Les libellés de la fenêtre de fermeture d'Odoo, en mode (revue de 6b,
 * constat 6) : « Entrée ou sortie d'espèces » comme dans le menu ≡, le titre
 * des mouvements d'espèces, « {n} commande(s) » accordé ; plus aucun
 * « Cash In/Out ». */
function libellesDeLaFermeture(commandes) {
    return Aite.verifier(`les libellés de la fermeture (${commandes} commandes)`, () => {
        const fenetre = document.querySelector(".modal .close-pos-popup");
        if (!fenetre) {
            return "pas de fenêtre de fermeture";
        }
        const especes = Aite.texte("especes")();
        const mouvements = Aite.texte("mouvementsEspeces")();
        const entete = Aite.texte("commandes", commandes)();
        const boutons = [...fenetre.querySelectorAll(".modal-footer button")].map((b) =>
            b.textContent.trim()
        );
        const titres = [...fenetre.querySelectorAll(".name-amount > span:first-child")].map((t) =>
            t.textContent.trim()
        );
        const total = fenetre.querySelector(".total-orders")?.textContent.trim() || "";
        const anglais = [_t("Cash In/Out"), _t("Cash in/out"), _t("Cash In / Out")].some((t) =>
            fenetre.textContent.includes(t)
        );
        return (
            (boutons.includes(especes) &&
                titres.includes(mouvements) &&
                total.startsWith(entete) &&
                !anglais) ||
            JSON.stringify({ boutons, titres, total, anglais })
        );
    });
}

/** Paul ferme la caisse : ≡, « Fermer la caisse », son code, les espèces
 * comptées ; `commandes` : le nombre d'additions payées de la session. */
function fermerLaCaisse(commandes, apres) {
    return [
        touche(1, Chrome.clickMenuButton()),
        touche(1, Aite.entreeDuMenu("Close Register")),
        touche(4, Aite.taperCode("4444")),
        rien(
            { content: "la fenêtre de fermeture", trigger: ".modal .close-pos-popup .cash-input input" },
            libellesDeLaFermeture(commandes)
        ),
        chiffres(ESPECES, {
            content: "les espèces comptées",
            trigger: ".modal .close-pos-popup .cash-input input",
        }),
        ...apres,
    ];
}

function personnesALaTable(nombre) {
    return Aite.verifier(`${nombre} personnes à la table`, () => {
        const personnes = posmodel.get_order()?.customer_count;
        return personnes === nombre || `${personnes} personnes`;
    });
}

function ligneDe(nom) {
    return {
        content: `toucher la ligne ${nom}`,
        trigger: `.order-container .orderline:has(.product-name:contains("${nom}"))`,
        run: "click",
    };
}

registry.category("web_tour.tours").add("AiteParcoursTour", {
    steps: () => {
        const ouvrirLaCaisse = geste("Caissière — ouvrir la caisse le matin", 5, [
            rien(Aite.popupCode(), Aite.titreDeLaFenetre(Aite.titre("ouvrir"))),
            touche(4, Aite.taperCode("3333")),
            // Le contrôle d'ouverture d'Odoo : fond prérempli, « J'ouvre la caisse ».
            touche(1, Dialog.confirm()),
            rien(
                ...Aite.planVerrouille(),
                Aite.verifier("la caisse est ouverte", () => posmodel.session.state === "opened")
            ),
        ]);
        const ouvrirEtEnvoyer = geste("Serveur — ouvrir une table et envoyer (n = 2)", 7 + 2, [
            ...ouvrirSaTable("1111"),
            touche(1, Aite.personnes("4")),
            rien(...Aite.ecranCommande(), Aite.identifie("Awa"), personnesALaTable(4)),
            touche(1, ProductScreen.clickDisplayedProduct("Coca-Cola")),
            touche(1, ProductScreen.clickDisplayedProduct("Water")),
            touche(1, Aite.jEnvoie()),
            rien(...Aite.planVerrouille(), Aite.notificationQuiCommencePar("Envoyé : ")),
        ]);
        const ajouter = geste("Serveur — ajouter à sa table et envoyer (n = 1)", 6 + 1, [
            ...ouvrirSaTable("1111"),
            rien(...Aite.ecranCommande(), Aite.identifie("Awa")),
            touche(1, ProductScreen.clickDisplayedProduct("Water")),
            rien(Aite.quantiteDeLaLigne("Water", 2)),
            touche(1, Aite.jEnvoie()),
            rien(...Aite.planVerrouille()),
        ]);
        const rouvrir = geste("Serveur — rouvrir sa table (table, code)", 1 + 4, [
            ...ouvrirSaTable("1111"),
            rien(...Aite.ecranCommande(), Aite.identifie("Awa")),
        ]);
        const changerPersonnes = geste("Serveur — changer le nombre de personnes", 2, [
            touche(1, Aite.toucherBoutonPersonnes()),
            touche(1, Aite.personnes("6")),
            rien(...Aite.ecranCommande(), personnesALaTable(6)),
        ]);
        const saisirSansEnvoyer = geste("Serveur — saisir un produit, sans l'envoyer", null, [
            touche(1, ProductScreen.clickDisplayedProduct("Coca-Cola")),
            rien(Aite.quantiteDeLaLigne("Coca-Cola", 2)),
        ]);
        // La ligne vient d'être touchée par le produit : elle est sélectionnée
        // (partie 1.2 : 3 touches, 2 si la ligne est déjà sélectionnée).
        const retirer = geste("Serveur — retirer un produit pas encore envoyé (ligne déjà sélectionnée)", 2, [
            touche(1, ProductScreen.clickNumpad("⌫")),
            touche(1, ProductScreen.clickNumpad("⌫")),
            rien(Aite.quantiteDeLaLigne("Coca-Cola", 1), Aite.pasDePopupAnnulation()),
        ]);
        const epuise = geste("Serveur — un produit épuisé est refusé", 1, [
            touche(1, ProductScreen.clickDisplayedProduct("Minute Maid")),
            rien(Aite.produitEpuise("Minute Maid"), Aite.pasDeLigne("Minute Maid")),
        ]);
        // Deux Water sont partis : « Combien ? » ajoute une touche.
        const annuler = geste(
            "Serveur + chef — annuler un produit envoyé sur le poste du serveur (2 envoyés)",
            3 + 5 + 1,
            [
                touche(1, ligneDe("Water")),
                touche(1, ProductScreen.clickNumpad("⌫")),
                touche(1, ProductScreen.clickNumpad("⌫")),
                rien(
                    ...Aite.popupAnnulation(
                        Aite.titre("annulerProduit", "Water", 5),
                        Aite.messageDe("R9", 2, "Water")
                    )
                ),
                touche(1, Aite.combien("1", ["1", "2"])),
                touche(4, Aite.codeAnnulation("4444")),
                touche(1, Aite.motif(0)),
                rien(
                    Aite.pasDePopupAnnulation(),
                    Aite.notification(Aite.texte("annulationFaite", 1, "Water", "Paul")),
                    Aite.quantiteDeLaLigne("Water", 1),
                    // REST-11-P1 : la serveuse reste identifiée.
                    Aite.identifie("Awa")
                ),
            ]
        );
        const auPlan = geste("Serveur — revenir au plan (« Plan »)", null, [
            touche(1, Chrome.clickPlanButton()),
            rien(...Aite.planVerrouille()),
        ]);
        // « Addition » : l'imprimante de tickets est simulée (sans elle, Odoo
        // affiche l'aperçu au lieu d'imprimer, et la caisse reste sur la table).
        const addition = geste("Serveur — imprimer l'addition", 6, [
            rien(
                Aite.verifier("une imprimante de tickets simulée", () => {
                    posmodel.hardwareProxy.printer = {
                        printReceipt: async () => ({ successful: true }),
                    };
                    return true;
                })
            ),
            ...ouvrirSaTable("1111"),
            rien(...Aite.ecranCommande()),
            touche(1, {
                content: "« Addition »",
                trigger: ".control-buttons .aite-addition-btn",
                run: "click",
            }),
            rien(
                ...Aite.planVerrouille(),
                Aite.verifier("plus d'imprimante", () => {
                    posmodel.hardwareProxy.printer = null;
                    return true;
                })
            ),
        ]);
        const encaisser = geste("Caissière — encaisser en espèces, somme exacte", 8, [
            ...ouvrirSaTable("3333"),
            rien(...Aite.ecranCommande(), Aite.identifie("Carine")),
            touche(1, Aite.jEncaisse()),
            rien(PaymentScreen.isShown()),
            touche(1, PaymentScreen.clickPaymentMethod("Cash")),
            touche(1, PaymentScreen.clickValidate()),
            rien(
                ...Aite.planVerrouille(),
                { content: "pas d'écran de ticket", trigger: "body:not(:has(.receipt-screen))" },
                Aite.tableLibre(5)
            ),
        ]);
        const deBoutEnBout = [ouvrirEtEnvoyer, ajouter, addition, encaisser];
        const n = 3;
        const table = deBoutEnBout.reduce((somme, g) => somme + g.touches, 0);
        const bilanTable = `AiteParcoursTour — une table servie de bout en bout : ${table} touches (partie 1.2 : 27 + n, n = ${n})`;

        // Les autres lignes de la partie 1.2 (revue de 6b, constat 8).
        // Table 4 : Water, puis Coca-Cola (la Coca-Cola reste la ligne
        // sélectionnée : toucher la ligne Water la sélectionne).
        const table4 = geste("Serveur — ouvrir la table 4 et envoyer (n = 2)", 7 + 2,
            tableEnvoyee("4", "1111", "2", ["Water", "Coca-Cola"]));
        const chefAnnule = geste("Chef seul — annuler un produit envoyé (1 envoyé)", 9, [
            ...ouvrirSaTable("4444", "4"),
            rien(...Aite.ecranCommande(), Aite.identifie("Paul")),
            touche(1, ligneDe("Water")),
            touche(1, ProductScreen.clickNumpad("⌫")),
            touche(1, ProductScreen.clickNumpad("⌫")),
            rien(
                ...Aite.popupAnnulation(Aite.titre("annulerProduit", "Water", 4)),
                // Le code tapé à la table sert : pas de code, pas de « Combien ? ».
                Aite.pasDeCodeAnnulation()
            ),
            touche(1, Aite.motif(0)),
            rien(
                Aite.pasDePopupAnnulation(),
                Aite.notification(Aite.texte("annulationFaite", 1, "Water", "Paul")),
                Aite.quantiteDeLaLigne("Water", 0),
                Aite.identifie("Paul")
            ),
        ]);
        const chefAuPlan = geste("Chef — revenir au plan (« Plan »)", null, [
            touche(1, Chrome.clickPlanButton()),
            rien(...Aite.planVerrouille()),
        ]);
        const awaRouvre4 = geste("Serveur — rouvrir sa table 4 (table, code)", 1 + 4, [
            ...ouvrirSaTable("1111", "4"),
            rien(...Aite.ecranCommande(), Aite.identifie("Awa")),
        ]);
        const caissiereAuPoste = geste("Caissière — encaisser au poste d'un serveur resté identifié", 7, [
            touche(1, Aite.jEncaisse()),
            rien(Aite.popupCode(), Aite.titreDeLaFenetre(Aite.titre("encaisser"))),
            touche(4, Aite.taperCode("3333")),
            rien(Aite.identifie("Carine")),
            ...especesValider(),
            rien(...Aite.planVerrouille(), Aite.tableLibre(4)),
        ]);
        const table2 = geste("Serveur — ouvrir la table 2 et envoyer (n = 1)", 7 + 1,
            tableEnvoyee("2", "1111", "3", ["Coca-Cola"]));
        const managerEncaisse = geste("Manager — encaisser une table ouverte par une autre", 8, [
            ...ouvrirSaTable("5555", "2"),
            rien(...Aite.ecranCommande(), Aite.identifie("Fanta")),
            touche(1, Aite.jEncaisse()),
            ...especesValider(),
            rien(...Aite.planVerrouille(), Aite.tableLibre(2)),
        ]);
        const caissiereOuvre2 = geste("Caissière — ouvrir la table 2 et saisir (n = 1), sans envoyer", null, [
            ...ouvrirSaTable("3333", "2"),
            touche(1, Aite.personnes("1")),
            rien(...Aite.ecranCommande(), Aite.identifie("Carine")),
            touche(1, ProductScreen.clickDisplayedProduct("Water")),
        ]);
        const priseEnMain = geste(
            "Manager — prendre la main sur une addition ouverte au nom d'une caissière, puis encaisser",
            8,
            [
                touche(1, Aite.prendreLaMain()),
                rien(Aite.popupCode(), Aite.titreDeLaFenetre(Aite.titre("prendreLaMain"))),
                touche(4, Aite.taperCode("5555")),
                rien(Aite.identifie("Fanta")),
                touche(1, Aite.jEncaisse()),
                ...especesValider(),
                rien(...Aite.planVerrouille(), Aite.tableLibre(2)),
            ]
        );
        const table4Bis = geste("Serveur — ouvrir la table 4 et envoyer (n = 2), de nouveau", 7 + 2,
            tableEnvoyee("4", "1111", "2", ["Coca-Cola", "Water"]));
        const deuxParts = geste("Caissière — deux parts d'une addition divisée (n = 1)", 14 + 1, [
            ...ouvrirSaTable("3333", "4"),
            rien(...Aite.ecranCommande(), Aite.identifie("Carine")),
            touche(1, Aite.ouvrirActions()),
            touche(1, {
                content: "« Diviser l'addition »",
                trigger: ".modal .control-buttons-modal button:has(.fa-files-o)",
                run: "click",
            }),
            rien({ content: "l'écran de division", trigger: ".splitbill-screen" }),
            touche(1, SplitBillScreen.clickOrderline("Water")),
            touche(1, SplitBillScreen.clickPay()),
            // La part « 4B » : Carine l'encaisse, sans code.
            rien(...Aite.ecranCommande(), additionCourante(4, true), Aite.identifie("Carine")),
            touche(1, Aite.jEncaisse()),
            ...especesValider(),
            // Retour à la table 4, Carine toujours identifiée : la seconde part.
            rien(...Aite.ecranCommande(), additionCourante(4), Aite.identifie("Carine")),
            touche(1, Aite.jEncaisse()),
            ...especesValider(),
            rien(...Aite.planVerrouille(), Aite.tableLibre(4)),
        ]);
        const especes = geste(
            `Chef — sortir des espèces (saisie : « ${SORTIE} » et « ${MOTIF_SORTIE} »)`,
            7 + SORTIE.length + MOTIF_SORTIE.length,
            [
                rien(
                    Aite.verifier("une imprimante de tickets simulée (bon de sortie)", () => {
                        posmodel.hardwareProxy.printer = {
                            printReceipt: async () => ({ successful: true }),
                        };
                        return true;
                    })
                ),
                touche(1, Chrome.clickMenuButton()),
                touche(1, Aite.entreeAite("Entrée ou sortie d'espèces")),
                rien(Aite.popupCode(), Aite.titreDeLaFenetre(Aite.titre("especes"))),
                touche(4, Aite.taperCode("4444")),
                // « Sortie » est le choix d'Odoo par défaut : aucune touche.
                chiffres(SORTIE, { content: "le montant", trigger: ".modal .input-amount input" }),
                lettres(MOTIF_SORTIE, { content: "le motif", trigger: ".modal textarea.cash-reason" }),
                touche(1, {
                    content: "« Confirmer »",
                    trigger: ".modal .modal-footer button.confirm:not([disabled])",
                    run: "click",
                }),
                rien(
                    ...Aite.planVerrouille(),
                    Aite.verifier("plus d'imprimante", () => {
                        posmodel.hardwareProxy.printer = null;
                        return true;
                    })
                ),
            ]
        );
        const table4Ter = geste("Serveur — ouvrir la table 4 et envoyer (n = 1), pour le chef", 7 + 1,
            tableEnvoyee("4", "1111", "2", ["Water"]));
        const chefAnnuleTable = geste("Chef seul — annuler une table qui a des produits envoyés", 8, [
            ...ouvrirSaTable("4444", "4"),
            rien(...Aite.ecranCommande(), Aite.identifie("Paul")),
            touche(1, Aite.ouvrirActions()),
            touche(1, {
                content: "« Annuler la table »",
                trigger: ".modal .control-buttons-modal button:has(.fa-trash)",
                run: "click",
            }),
            rien(...Aite.popupAnnulation(Aite.titre("annulerTable", 4)), Aite.pasDeCodeAnnulation()),
            touche(1, Aite.motif(1)),
            rien(...Aite.planVerrouille(), Aite.tableLibre(4)),
        ]);
        // Deux tables encore ouvertes à la fermeture (5 et 2).
        const table5Soir = geste("Serveur — ouvrir la table 5 et envoyer (n = 1), le soir", 7 + 1,
            tableEnvoyee(TABLE, "1111", "2", ["Coca-Cola"]));
        const table2Soir = geste("Serveur — ouvrir la table 2 et envoyer (n = 1), le soir", 7 + 1,
            tableEnvoyee("2", "1111", "2", ["Water"]));
        const service = [
            ouvrirLaCaisse,
            ouvrirEtEnvoyer,
            ajouter,
            rouvrir,
            changerPersonnes,
            saisirSansEnvoyer,
            retirer,
            epuise,
            annuler,
            auPlan,
            addition,
            encaisser,
            table4,
            chefAnnule,
            chefAuPlan,
            awaRouvre4,
            caissiereAuPoste,
            table2,
            managerEncaisse,
            caissiereOuvre2,
            priseEnMain,
            table4Bis,
            deuxParts,
            especes,
            table4Ter,
            chefAnnuleTable,
            table5Soir,
            table2Soir,
        ];
        // Six additions payées dans la session : table 5, table 4, table 2
        // (deux fois), et les deux parts de la table 4.
        const fermerAvecTables = geste(
            "Chef — fermer la caisse avec 2 tables ouvertes et les annuler",
            7 + ESPECES.length + 2,
            fermerLaCaisse(6, [
                touche(1, {
                    content: "« Fermer la caisse »",
                    trigger: ".modal .close-pos-popup button.highlight.btn-primary",
                    run: "click",
                }),
                rien(
                    Aite.verifier("le message des tables encore ouvertes", () => {
                        const corps = [...document.querySelectorAll(".modal .modal-body")].map((b) =>
                            b.textContent.trim()
                        );
                        const attendu = Aite.texte("tablesOuvertes", 2, "2, 5")();
                        return corps.some((c) => c === attendu) || corps.join(" | ");
                    })
                ),
                touche(1, {
                    content: "« Annuler ces tables » (bouton secondaire de la fenêtre)",
                    trigger: ".modal:not(.o_inactive_modal) .modal-footer .btn-secondary",
                    run: "click",
                }),
                rien(
                    ...Aite.popupAnnulation(Aite.titre("annulerTables", "2, 5")),
                    // Le code de Paul est déjà tapé : le motif seul.
                    Aite.pasDeCodeAnnulation(),
                    { content: "« Pourquoi ? »", trigger: ".modal .aite-annulation-motifs" }
                ),
                touche(1, {
                    content: "« Client parti » : les tables sont annulées, la caisse se ferme",
                    trigger: ".modal .aite-annulation-motifs [data-aite-motif-id]:eq(1)",
                    run: "click",
                    expectUnloadPage: true,
                }),
                // La page se recharge : une nouvelle session, en contrôle
                // d'ouverture (la fenêtre du code s'ouvre d'elle-même).
                rien(Aite.popupCode(), Aite.titreDeLaFenetre(Aite.titre("ouvrir"))),
            ])
        );
        const rouvrirLaCaisse = geste("Caissière — ouvrir la caisse le lendemain (fond prérempli)", 5, [
            rien(Aite.popupCode(), Aite.titreDeLaFenetre(Aite.titre("ouvrir"))),
            touche(4, Aite.taperCode("3333")),
            touche(1, Dialog.confirm()),
            rien(
                ...Aite.planVerrouille(),
                Aite.verifier("la caisse est ouverte", () => posmodel.session.state === "opened")
            ),
        ]);
        const fermer = geste(
            "Chef — fermer la caisse, sans table ouverte",
            7 + ESPECES.length,
            fermerLaCaisse(0, [
                touche(1, {
                    content: "« Fermer la caisse » : la caisse se ferme, la page se recharge",
                    trigger: ".modal .close-pos-popup button.highlight.btn-primary",
                    run: "click",
                    expectUnloadPage: true,
                }),
                // Une nouvelle session, en contrôle d'ouverture : la fenêtre du
                // code s'ouvre d'elle-même pour le lendemain.
                rien(Aite.popupCode(), Aite.titreDeLaFenetre(Aite.titre("ouvrir"))),
            ])
        );
        const total = [...service, fermerAvecTables, rouvrirLaCaisse, fermer].reduce(
            (somme, g) => somme + g.touches,
            0
        );
        const bilan = `${bilanTable} ; le service complet, de l'ouverture à la fermeture, et le lendemain : ${total} touches`;
        return [
            ...service.flatMap((g) => g.etapes),
            {
                content: bilan,
                trigger: "body",
                run() {
                    console.log(bilan);
                    if (table !== 27 + n) {
                        throw new Error(`table servie : ${table} touches au lieu de ${27 + n}`);
                    }
                },
            },
            ...fermerAvecTables.etapes,
            ...rouvrirLaCaisse.etapes,
            ...fermer.etapes,
        ];
    },
});
