/** Messages de la caisse du restaurant (spécification, parties 1.4 et 1.5).
 *
 * Écrits en français dans le code, comme dans les autres modules AITE. Les
 * refus que le serveur vérifie (ouverture, fermeture, espèces) reviennent
 * aussi de Python, mot pour mot : la caisse affiche alors le message reçu.
 *
 * Typographie : une espace insécable (`ESP`) avant « : » et « ? », à
 * l'intérieur des guillemets et dans « votre code », pour qu'un signe ou un
 * mot ne passe pas seul à la ligne dans les petites fenêtres de la caisse. */

/** Espace insécable. */
const ESP = "\u00a0";

export const MESSAGES = {
    R1: "Code inconnu. Retapez votre code.",
    R3:
        "La caisse n'est pas encore ouverte. La caissière ou un chef de salle " +
        "doit l'ouvrir avec son code.",
    R5: "Il faut au moins une personne à table.",
    R4: (table, nom) =>
        `Table ${table}${ESP}: c'est la table de ${nom}. Seuls ${nom}, la caissière ` +
        "ou un chef de salle peuvent la modifier.",
    /** R4 pour une vente sans table (« + ») : elle n'a pas de numéro de table,
     * seulement le numéro de son onglet. */
    R4vente: (numero, nom) =>
        `Vente sans table ${numero}${ESP}: c'est la vente de ${nom}. Seuls ${nom}, ` +
        "la caissière ou un chef de salle peuvent la modifier.",
    R10: `Vous ne pouvez pas encaisser. Appelez la caissière${ESP}: elle tapera son code ici.`,
    R13: "Seul un chef de salle ou le manager ferme la caisse.",
    R14:
        `L'écart de caisse dépasse le maximum autorisé${ESP}: seul le manager peut ` +
        "fermer. Recomptez, ou appelez le manager.",
    R15: "Seul un chef de salle ou le manager peut sortir ou entrer des espèces.",
    R16: "Seul le manager peut rembourser une addition payée.",
    R17: "La vente sans table n'est pas ouverte ici. Ouvrez une table du plan.",
    R19: (table, nom) =>
        `La table ${table} est celle de ${nom}${ESP}: la caissière ou un chef de salle peut ` +
        "réunir ces tables.",
    R21: "Seuls la caissière, le chef de salle et le manager impriment le rapport des ventes.",
    R27: (geste) =>
        `Pas de réseau${ESP}: ${geste} est impossible pour l'instant. Réessayez dans un moment.`,
    R29:
        `Rien n'est parti${ESP}: un autre poste a modifié cette table. Vérifiez ` +
        `l'addition, puis touchez de nouveau «${ESP}J'envoie${ESP}».`,
    R30:
        `Toute l'addition est sélectionnée${ESP}: il n'y a rien à diviser. Encaissez ` +
        "la table directement.",
};

export const TITRES = {
    table: (numero) => `Table ${numero} — votre${ESP}code`,
    ouvrir: "Votre code pour ouvrir la caisse",
    encaisser: "Code de la personne qui encaisse",
    fermer: "Votre code pour fermer la caisse",
    especes: "Votre code — entrée ou sortie d'espèces",
    commandes: "Votre code — liste des commandes",
    rapport: "Votre code — rapport des ventes",
    prendreLaMain: `Qui prend la main${ESP}? Tapez votre code`,
    personnes: (numero) => `Table ${numero} — combien de personnes${ESP}?`,
    /** Une vente sans table (« + ») : le numéro de son onglet. */
    venteSansTable: (numero) => `Vente sans table ${numero} — votre${ESP}code`,
};

export const TEXTES = {
    planEtat: "Touchez une table, puis tapez votre code.",
    caisseFermee:
        "La caisse est fermée. La caissière ou un chef de salle tape son code pour l'ouvrir.",
    ouvrirLaCaisse: "Ouvrir la caisse",
    neSaitPasEncaisser: (nom) =>
        `${nom} ne peut pas encaisser${ESP}: la caissière tape son code ici.`,
    envoye: (compte) => `Envoyé${ESP}: ${compte}.`,
    retour: "Retour",
    // Incrément 3 : la table
    neufEtPlus: "9 et plus",
    valider: "Valider",
    personnes: (nombre) => (nombre === 1 || nombre === 0 ? `${nombre} personne` : `${nombre} personnes`),
    addition: "Addition",
    diviser: "Diviser l'addition",
    deplacer: "Déplacer ou réunir",
    annulerLaTable: "Annuler la table",
    creerLaPart: "Créer l'addition à part",
    table: (numero) => `Table ${numero}`,
    venteSansTable: "Vente sans table",
    ouvertePar: (nom) => `ouverte par ${nom}`,
    /** « 35 min » ; à partir d'une heure, « 1 h 05 ». */
    duree: (minutes) => {
        if (minutes < 60) {
            return `${minutes} min`;
        }
        const heures = Math.floor(minutes / 60);
        return `${heures} h ${String(minutes % 60).padStart(2, "0")}`;
    },
};
