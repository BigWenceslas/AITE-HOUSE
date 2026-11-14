/* global posmodel */
/** Incrément 5 : le plan en couleurs ; les produits épuisés (spécification,
 * partie 6.3). AiteCouleursTour (joué deux fois : délai de 60 et de 90
 * minutes, lu dans la caisse), AiteEpuiseRefusTour, puis AiteEpuiseVenteTour
 * après une entrée de stock faite en Python. Les vérifications côté serveur
 * sont faites en Python après chaque tour (test_tours.py, TestToursPlanStock). */
import * as ProductScreen from "@point_of_sale/../tests/tours/utils/product_screen_util";
import * as PaymentScreen from "@point_of_sale/../tests/tours/utils/payment_screen_util";
import * as ProductConfigurator from "@point_of_sale/../tests/tours/utils/product_configurator_util";
import * as TextInputPopup from "@point_of_sale/../tests/tours/utils/text_input_popup_util";
import * as Dialog from "@point_of_sale/../tests/tours/utils/dialog_util";
import * as FloorScreen from "@pos_restaurant/../tests/tours/utils/floor_screen_util";
import * as Aite from "@aite_pos_restaurant/../tests/tours/aite_util";
import { scan_barcode } from "@point_of_sale/../tests/tours/utils/common";
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

/** Le délai de la caisse (réglage « Délai avant l'orange »), lu au moment de
 * l'étape, plus `ecart` minutes. */
function delai(ecart) {
    return () => posmodel.config.aite_delai_alerte + ecart;
}

registry.category("web_tour.tours").add("AiteCouleursTour", {
    steps: () =>
        [
            ...Aite.planVerrouille(),
            Aite.legende(),
            // Une table libre : grise, sans durée.
            Aite.couleurDeLaTable("5", "libre"),
            Aite.dureeDeLaTable("5", ""),
            // Awa ouvre la table 5 et envoie un Coca-Cola.
            ...ouvrir("5", "1111", "4"),
            ProductScreen.clickDisplayedProduct("Coca-Cola"),
            Aite.jEnvoie(),
            ...Aite.planVerrouille(),
            // Ouverte : verte, « 0 min » sous le numéro.
            Aite.couleurDeLaTable("5", "vert"),
            Aite.dureeDeLaTable("5", Aite.texte("duree", 0)),
            // Une minute avant le délai : toujours verte (REST-17 critère 1).
            Aite.avancerLHorloge("5", delai(-1)),
            Aite.couleurDeLaTable("5", "vert"),
            Aite.dureeDeLaTable("5", () => Aite.texte("duree", delai(-1)())()),
            // Le délai atteint, puis dépassé : orange, sans que personne ne
            // touche l'écran (le tic de la minuterie du plan).
            Aite.avancerLHorloge("5", delai(0)),
            Aite.couleurDeLaTable("5", "orange"),
            Aite.avancerLHorloge("5", delai(1)),
            Aite.couleurDeLaTable("5", "orange"),
            Aite.dureeDeLaTable("5", () => Aite.texte("duree", delai(1)())()),
            Aite.couleurDeLaTable("4", "libre"),
            // Pas d'écran de veille : le plan et ses couleurs restent.
            Aite.verifier(
                "showScreen(« SaverScreen ») rend faux",
                () => posmodel.showScreen("SaverScreen") === false
            ),
            { content: "pas d'écran de veille", trigger: "body:not(:has(.screen-saver))" },
            Aite.couleurDeLaTable("5", "orange"),
            // REST-17 critère 3 : encaissée, la table orange redevient libre.
            ...ouvrir("5", "3333"),
            Aite.jEncaisse(),
            PaymentScreen.isShown(),
            PaymentScreen.clickPaymentMethod("Cash"),
            PaymentScreen.clickValidate(),
            ...Aite.planVerrouille(),
            Aite.couleurDeLaTable("5", "libre"),
            Aite.dureeDeLaTable("5", ""),
        ].flat(),
});

registry.category("web_tour.tours").add("AiteEpuiseRefusTour", {
    steps: () =>
        [
            ...Aite.planVerrouille(),
            ...ouvrir("5", "1111", "4"),
            // Coca-Cola suivi en stock, à 0 : refusé (R11), rien n'est ajouté.
            ProductScreen.clickDisplayedProduct("Coca-Cola"),
            Aite.produitEpuise("Coca-Cola"),
            Aite.pasDeLigne("Coca-Cola"),
            // Lu au code-barres : le même refus (revue de l'incrément 5 : le
            // contrôle est fait aux gestes qui ajoutent).
            ...scan_barcode("5449000000996"),
            Aite.produitEpuise("Coca-Cola"),
            Aite.pasDeLigne("Coca-Cola"),
            // Water n'est pas suivi : la vente passe (REST-19 critère 3).
            ProductScreen.clickDisplayedProduct("Water"),
            Aite.quantiteDeLaLigne("Water", 1),
            Aite.pasDeLigne("Coca-Cola"),
            Aite.jEnvoie(),
            ...Aite.planVerrouille(),
        ].flat(),
});

registry.category("web_tour.tours").add("AiteEpuiseVenteTour", {
    steps: () =>
        [
            ...Aite.planVerrouille(),
            ...ouvrir("4", "1111", "2"),
            // Le poste avait gardé en mémoire « 0 Coca-Cola » avant l'entrée
            // de stock : 2 ou moins, le serveur est réinterrogé avant
            // d'ajouter (T20) ; la vente repasse sans recharger la caisse
            // (REST-19 critère 2).
            Aite.verifier("le poste garde en mémoire 0 Coca-Cola", () => {
                const coca = posmodel.models["product.product"].find((p) => p.name === "Coca-Cola");
                posmodel.aiteStock = { produits: { [coca.id]: 0 }, date: Date.now() };
                return true;
            }),
            // Une seule bouteille en stock, touchée deux fois très vite
            // (double toucher) : la seconde attend la première, et elle est
            // refusée si le réglage est coché (rien n'est vendu deux fois).
            {
                content: "double toucher sur Coca-Cola",
                trigger: 'article.product .product-content .product-name:contains("Coca-Cola")',
                run() {
                    const carte = this.anchor.closest("article.product");
                    carte.click();
                    carte.click();
                },
            },
            Aite.verifier(
                "une bouteille ajoutée et R11 si le réglage est coché ; deux sinon",
                () => {
                    const refus = posmodel.config.aite_refus_epuise;
                    const ligne = posmodel
                        .get_order()
                        .lines.find((l) => l.get_product().name === "Coca-Cola");
                    const quantite = ligne?.get_quantity();
                    const titre = Aite.titre("produitEpuise")();
                    const r11 = [...document.querySelectorAll(".o_notification_title")].some(
                        (t) => t.textContent.trim() === titre
                    );
                    const attendu = refus ? quantite === 1 && r11 : quantite === 2 && !r11;
                    return attendu || `quantité ${quantite}, R11 ${r11}`;
                }
            ),
            Aite.jEnvoie(),
            ...Aite.planVerrouille(),
        ].flat(),
});

// ----------------------------------------------------------------------
// Revue de l'incrément 5 : chaque tour reproduit un constat, écrit avant
// sa correction (vérifications côté serveur : TestToursEpuiseCorrectifs).
// ----------------------------------------------------------------------

/** Constat 1 : une quantité tapée au pavé ne contourne pas le refus. Deux
 * Coca-Cola en stock : « 5 » est refusé (R11, la ligne reste à 1), « 2 »
 * passe. */
registry.category("web_tour.tours").add("AiteEpuisePaveTour", {
    steps: () =>
        [
            ...Aite.planVerrouille(),
            ...ouvrir("5", "1111", "4"),
            ProductScreen.clickDisplayedProduct("Coca-Cola"),
            Aite.quantiteDeLaLigne("Coca-Cola", 1),
            ProductScreen.clickNumpad("5"),
            Aite.produitEpuise("Coca-Cola"),
            Aite.quantiteDeLaLigne("Coca-Cola", 1),
            ProductScreen.clickNumpad("2"),
            Aite.quantiteDeLaLigne("Coca-Cola", 2),
            Aite.pasDeProduitEpuise(),
            Aite.jEnvoie(),
            ...Aite.planVerrouille(),
        ].flat(),
});

/** Constat 2 : « Note cuisine » sur une ligne en partie envoyée d'un
 * produit au bout de son stock (2 en stock, 1 parti, 1 saisi) : Odoo scinde
 * la ligne sans rien ajouter ; ni R11 ni erreur, la note est posée. */
registry.category("web_tour.tours").add("AiteEpuiseNoteTour", {
    steps: () =>
        [
            ...Aite.planVerrouille(),
            ...ouvrir("5", "1111", "4"),
            ProductScreen.clickDisplayedProduct("Coca-Cola"),
            Aite.jEnvoie(),
            ...Aite.planVerrouille(),
            ...ouvrir("5", "1111"),
            ProductScreen.clickDisplayedProduct("Coca-Cola"),
            Aite.quantiteDeLaLigne("Coca-Cola", 2),
            Aite.noteCuisine(),
            TextInputPopup.inputText("bien fraîche"),
            Dialog.confirm(),
            Aite.lignesDuProduit("Coca-Cola", ["1/", "1/bien fraîche"]),
            Aite.pasDeProduitEpuise(),
            Aite.pasDErreur(),
            Aite.jEnvoie(),
            ...Aite.planVerrouille(),
        ].flat(),
});

/** Constat 3 : un produit à variantes est contrôlé sur la variante choisie
 * dans la fenêtre de configuration. « Jus » : 33 cl à 0, 50 cl à 5 ; la
 * carte affiche 33 cl. 50 cl passe, 33 cl est refusé (R11 à son nom). */
registry.category("web_tour.tours").add("AiteEpuiseVarianteTour", {
    steps: () =>
        [
            ...Aite.planVerrouille(),
            ...ouvrir("5", "1111", "4"),
            ProductScreen.clickDisplayedProduct("Jus"),
            ProductConfigurator.pickRadio("50 cl"),
            Dialog.confirm(),
            Aite.quantiteDeLaVariante("Jus", "50 cl", 1),
            Aite.pasDeProduitEpuise(),
            ProductScreen.clickDisplayedProduct("Jus"),
            ProductConfigurator.pickRadio("33 cl"),
            Dialog.confirm(),
            Aite.produitEpuise(() => Aite.variante("Jus", "33 cl").display_name),
            Aite.quantiteDeLaVariante("Jus", "33 cl", 0),
            Aite.quantiteDeLaVariante("Jus", "50 cl", 1),
            Aite.jEnvoie(),
            ...Aite.planVerrouille(),
        ].flat(),
});

/** Constat 4 : hors connexion, ou quand la relecture du stock n'aboutit
 * pas, la caisse vend (Q59, partie 8.3) au lieu de se fier à sa mémoire.
 * Coca-Cola est à 0 sur le serveur. */
registry.category("web_tour.tours").add("AiteEpuiseHorsConnexionTour", {
    steps: () =>
        [
            ...Aite.planVerrouille(),
            ...ouvrir("5", "1111", "4"),
            Aite.verifier("hors connexion, la mémoire dit 0 Coca-Cola", () => {
                const coca = posmodel.models["product.product"].find((p) => p.name === "Coca-Cola");
                posmodel.aiteStock = { produits: { [coca.id]: 0 }, date: Date.now() };
                posmodel.data.network.offline = true;
                return true;
            }),
            ProductScreen.clickDisplayedProduct("Coca-Cola"),
            Aite.quantiteDeLaLigne("Coca-Cola", 1),
            Aite.pasDeProduitEpuise(),
            // En ligne, mémoire de plus de 60 secondes et relecture en
            // erreur : la caisse vend aussi.
            Aite.verifier("en ligne, mémoire périmée, relecture en erreur", () => {
                const coca = posmodel.models["product.product"].find((p) => p.name === "Coca-Cola");
                posmodel.data.network.offline = false;
                posmodel.aiteStock = { produits: { [coca.id]: 0 }, date: Date.now() - 61000 };
                const appel = posmodel.data.call.bind(posmodel.data);
                posmodel.data.aiteAppelOrigine = appel;
                posmodel.data.call = (modele, methode, ...reste) =>
                    methode === "aite_stock_disponible"
                        ? Promise.reject(new Error("serveur indisponible (tour)"))
                        : appel(modele, methode, ...reste);
                return true;
            }),
            ProductScreen.clickDisplayedProduct("Coca-Cola"),
            Aite.quantiteDeLaLigne("Coca-Cola", 2),
            Aite.pasDeProduitEpuise(),
            Aite.verifier("relecture rendue au serveur", () => {
                posmodel.data.call = posmodel.data.aiteAppelOrigine;
                return true;
            }),
            // Les deux bouteilles ne partent pas : ⌫ les retire (pas encore
            // envoyées), puis une eau part.
            ProductScreen.clickNumpad("⌫"),
            ProductScreen.clickNumpad("⌫"),
            Aite.pasDeLigne("Coca-Cola"),
            ProductScreen.clickDisplayedProduct("Water"),
            Aite.jEnvoie(),
            ...Aite.planVerrouille(),
        ].flat(),
});

/** Constat 7 : la durée de la phrase d'état de l'écran de commande suit la
 * minuterie (partie 1.3 : « durées recalculées toutes les 30 secondes »). */
registry.category("web_tour.tours").add("AiteDureeCommandeTour", {
    steps: () =>
        [
            ...Aite.planVerrouille(),
            ...ouvrir("5", "1111", "4"),
            Aite.verifier("« 0 min » sur l'écran de commande", () => {
                const lu = document.querySelector(".product-screen .aite-commande-etat")?.textContent;
                return lu?.trim().endsWith(Aite.texte("duree", 0)()) || lu;
            }),
            Aite.avancerLHorloge("5", 7),
            Aite.verifier("« 7 min » sans toucher l'écran", () => {
                const lu = document.querySelector(".product-screen .aite-commande-etat")?.textContent;
                return lu?.trim().endsWith(Aite.texte("duree", 7)()) || lu;
            }),
            ProductScreen.clickDisplayedProduct("Water"),
            Aite.jEnvoie(),
            ...Aite.planVerrouille(),
        ].flat(),
});
