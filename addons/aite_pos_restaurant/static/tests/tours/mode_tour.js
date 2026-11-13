/* global posmodel */
/** Tour de fumée de l'incrément 1 : la caisse s'ouvre avec le module et
 * reconnaît son mode. Sélecteurs CSS seulement (aucun texte : le tour passe
 * dans toutes les langues). */
import { registry } from "@web/core/registry";

function verifierMode(attendu) {
    return [
        {
            content: "la caisse est chargée",
            trigger: ".pos",
        },
        {
            // body : en mode, la fenêtre du code d'ouverture couvre la caisse
            // (incrément 2) ; une étape ne peut agir sous une fenêtre.
            content: `le mode « Service à table contrôlé » vaut ${attendu}`,
            trigger: "body",
            run: () => {
                if (posmodel.aiteActif !== attendu) {
                    throw new Error(
                        `aiteActif vaut ${posmodel.aiteActif}, attendu : ${attendu}`
                    );
                }
            },
        },
    ];
}

registry.category("web_tour.tours").add("AiteModeActifTour", {
    steps: () => verifierMode(true),
});

registry.category("web_tour.tours").add("AiteModeInactifTour", {
    steps: () => verifierMode(false),
});
