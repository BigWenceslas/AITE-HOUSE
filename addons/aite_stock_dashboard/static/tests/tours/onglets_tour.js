/** @odoo-module */
/**
 * Les graphiques d'un onglet sont dessinés dès le premier clic sur l'onglet
 * (constat de recette : « Inventaires & écarts » et « Rotation » restaient
 * vides au premier clic : le dessin partait avant qu'OWL affiche l'onglet).
 */
import { registry } from "@web/core/registry";

function dessine(content, selecteur) {
    return {
        content,
        trigger: selecteur,
        async run() {
            const fin = Date.now() + 5000;
            while (Date.now() < fin) {
                const canevas = document.querySelectorAll(selecteur);
                if (canevas.length && [...canevas].every((c) => window.Chart?.getChart(c))) {
                    return;
                }
                await new Promise((r) => setTimeout(r, 100));
            }
            throw new Error(`${content} : graphique non dessiné`);
        },
    };
}

registry.category("web_tour.tours").add("AiteStockOngletsTour", {
    steps: () => [
        { content: "le tableau de bord", trigger: ".asd-chartbox canvas" },
        { content: "onglet « Inventaires & écarts »", trigger: "button:contains('Inventaires & écarts')", run: "click" },
        dessine("graphiques des écarts dessinés au premier clic", ".asd-chartbox canvas"),
        { content: "onglet « Rotation »", trigger: "button:contains('Rotation')", run: "click" },
        dessine("graphiques de rotation dessinés au premier clic", ".asd-chartbox canvas"),
    ],
});
