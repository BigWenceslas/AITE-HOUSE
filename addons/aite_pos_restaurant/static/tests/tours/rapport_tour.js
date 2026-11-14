/* global posmodel, odoo */
/** Incrément 6 : le rapport de fermeture imprimé depuis la caisse
 * (« Imprimer le rapport », gabarit `point_of_sale.SaleDetailsReport`) porte
 * les tables, les personnes, les ventes sans table et les annulations de la
 * session (spécification, partie 5.3). Il n'y a pas d'imprimante dans les
 * tests : le tour rend le gabarit avec les données du serveur, comme
 * `handleSaleDetails` d'Odoo, puis lit les attributs `data-aite`.
 *
 * Ce fichier est chargé avec les tours de toute la base, gestion comprise :
 * il n'importe que `@web`, et lit le reste au moment de l'étape. */
import { registry } from "@web/core/registry";

function verifierRapport() {
    return {
        content: "le rapport de fermeture rendu par la caisse",
        trigger: "body",
        async run() {
            const { renderToElement } = odoo.loader.modules.get("@web/core/utils/render");
            const donnees = await posmodel.data.call(
                "report.point_of_sale.report_saledetails",
                "get_sale_details",
                [false, false, false, [posmodel.session.id]]
            );
            const rapport = renderToElement(
                "point_of_sale.SaleDetailsReport",
                Object.assign({}, donnees, {
                    date: "",
                    pos: posmodel,
                    formatCurrency: posmodel.env.utils.formatCurrency,
                })
            );
            const bloc = rapport.querySelector(".aite-rapport-restaurant");
            if (!bloc) {
                throw new Error("le bloc des tables et des annulations est absent du rapport");
            }
            const lu = (cle) => bloc.querySelector(`[data-aite="${cle}"]`)?.textContent.trim();
            const attendus = { tables: "1", personnes: "3", sans_table: "0" };
            for (const [cle, valeur] of Object.entries(attendus)) {
                if (lu(cle) !== valeur) {
                    throw new Error(`${cle} : « ${lu(cle)} » au lieu de « ${valeur} »`);
                }
            }
            const annulations = bloc.querySelectorAll(".aite-annulation");
            if (annulations.length !== 1) {
                throw new Error(`${annulations.length} lignes d'annulation au lieu d'une`);
            }
            const motif = donnees.aite_annulations[0].motif;
            if (!annulations[0].textContent.includes(motif)) {
                throw new Error(`motif « ${motif} » absent : ${annulations[0].textContent}`);
            }
            const total = bloc.querySelector("[data-aite-quantite]")?.dataset.aiteQuantite;
            if (total !== "1") {
                throw new Error(`total annulé : « ${total} »`);
            }
        },
    };
}

registry.category("web_tour.tours").add("AiteRapportFermetureTour", {
    steps: () => [
        { content: "le plan est affiché", trigger: ".floor-screen .floor-map" },
        verifierRapport(),
    ],
});
