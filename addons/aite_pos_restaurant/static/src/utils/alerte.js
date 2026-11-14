/** La couleur d'une table du plan (spécification, partie 4.1 ; incrément 5,
 * REST-17). Même règle que `regles.alerte` (Python), qui est testée sans
 * Odoo : « libre » pour une table sans addition ouverte, « vert » pour une
 * table ouverte, « orange » quand elle l'est depuis le délai de la caisse ou
 * plus (« 60 minutes révolues », REST-17 critère 1). Un délai vide ou nul
 * vaut 60 minutes (le réglage refuse moins d'une minute). */

/** Minutes (Q11) : le délai par défaut, `regles.DELAI_ALERTE`. */
export const DELAI_ALERTE = 60;

/** Les couleurs et les durées sont recalculées toutes les 30 secondes
 * (partie 1.3), sur le plan et sur l'écran de commande : orange au plus tard
 * 30 secondes après le délai. */
export const TIC = 30000;

/** `minutes` : depuis l'ouverture de la table, ou `null` pour une table
 * libre. Rend « libre », « vert » ou « orange ». */
export function alerte(minutes, delai) {
    if (minutes === null || minutes === undefined) {
        return "libre";
    }
    let seuil = Math.trunc(Number(delai) || 0);
    if (seuil < 1) {
        seuil = DELAI_ALERTE;
    }
    return (Number(minutes) || 0) >= seuil ? "orange" : "vert";
}
