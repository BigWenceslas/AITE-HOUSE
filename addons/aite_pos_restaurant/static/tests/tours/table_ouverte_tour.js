/** @odoo-module */
/**
 * Une table déjà ouverte (verte sur le plan) ne redemande jamais le nombre de
 * personnes, même quand c'est une autre personne qui la touche, ou un autre
 * poste qui vient de charger la caisse (constat du client : « j'ai une table
 * déjà ouverte, je me connecte avec un autre compte, ça recommence le
 * processus de zéro »).
 */
import * as ProductScreen from "@point_of_sale/../tests/tours/utils/product_screen_util";
import * as FloorScreen from "@pos_restaurant/../tests/tours/utils/floor_screen_util";
import * as Aite from "@aite_pos_restaurant/../tests/tours/aite_util";
import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add("AiteTableOuverteTour", {
    steps: () =>
        [
            ...Aite.planVerrouille(),
            // Awa ouvre la table 2 et envoie un Coca-Cola.
            FloorScreen.clickTable("2"),
            ...Aite.taperCode("1111"),
            ...Aite.personnes("2"),
            ...Aite.ecranCommande(),
            ProductScreen.clickDisplayedProduct("Coca-Cola"),
            Aite.jEnvoie(),
            ...Aite.planVerrouille(),
            // Un autre poste : la page est rechargée, la caisse relit les
            // additions ouvertes sur le serveur.
            {
                content: "recharger la caisse (un autre poste)",
                trigger: "body",
                run: () => window.location.reload(),
                expectUnloadPage: true,
            },
            ...Aite.planVerrouille(),
            { content: "la table 2 est ouverte sur le plan", trigger: ".floor-map .table:contains('2')" },
            // Odoo 18 plus ancien : ni `deviceSync`, ni la table dans la liste
            // des additions du poste, mais verte sur le plan.
            Aite.verifier("table verte sur le plan : jamais l'étape « personnes »", () => {
                const table = posmodel.models["restaurant.table"].find((x) => x.table_number === 2);
                const ancien = Object.create(posmodel);
                ancien.deviceSync = undefined;
                ancien.getActiveOrdersOnTable = () => [];
                return ancien.aiteTableLibre(table) === false || "la table 2 serait jugée libre";
            }),
            // Carine touche la table 2 : son code, puis directement l'addition.
            FloorScreen.clickTable("2"),
            ...Aite.taperCode("3333"),
            { content: "pas d'étape « personnes »", trigger: "body:not(:has([data-aite-personnes]))" },
            ...Aite.ecranCommande(),
            Aite.identifie("Carine"),
            { content: "l'addition de la table 2 (Coca-Cola)", trigger: ".order-container .orderline:contains('Coca-Cola')" },
            {
                content: "une seule addition sur la table 2",
                trigger: "body",
                run() {
                    /* global posmodel */
                    const t = posmodel.models["restaurant.table"].find((x) => x.table_number === 2);
                    const n = posmodel.models["pos.order"].filter((o) => o.table_id?.id === t.id && !o.finalized).length;
                    if (n !== 1) {
                        throw new Error(`${n} additions ouvertes sur la table 2`);
                    }
                },
            },
        ].flat(),
});
