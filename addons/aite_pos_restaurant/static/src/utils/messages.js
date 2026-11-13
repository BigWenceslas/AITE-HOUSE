/** Messages de la caisse du restaurant (spécification, parties 1.4 et 1.5).
 *
 * Écrits en français dans le code, comme dans les autres modules AITE. Les
 * refus que le serveur vérifie (ouverture, fermeture, espèces) reviennent
 * aussi de Python, mot pour mot : la caisse affiche alors le message reçu. */

export const MESSAGES = {
    R1: "Code inconnu. Retapez votre code.",
    R3:
        "La caisse n'est pas encore ouverte. La caissière ou un chef de salle " +
        "doit l'ouvrir avec son code.",
    R4: (table, nom) =>
        `Table ${table} : c'est la table de ${nom}. Seuls ${nom}, la caissière ` +
        "ou un chef de salle peuvent la modifier.",
    R10: "Vous ne pouvez pas encaisser. Appelez la caissière : elle tapera son code ici.",
    R13: "Seul un chef de salle ou le manager ferme la caisse.",
    R14:
        "L'écart de caisse dépasse le maximum autorisé : seul le manager peut " +
        "fermer. Recomptez, ou appelez le manager.",
    R15: "Seul un chef de salle ou le manager peut sortir ou entrer des espèces.",
    R16: "Seul le manager peut rembourser une addition payée.",
    R17: "La vente sans table n'est pas ouverte ici. Ouvrez une table du plan.",
    R21: "Seuls la caissière, le chef de salle et le manager impriment le rapport des ventes.",
    R27: (geste) =>
        `Pas de réseau : ${geste} est impossible pour l'instant. Réessayez dans un moment.`,
    R29:
        "Rien n'est parti : un autre poste a modifié cette table. Vérifiez " +
        "l'addition, puis touchez de nouveau « J'envoie ».",
};

export const TITRES = {
    table: (numero) => `Table ${numero} — votre code`,
    ouvrir: "Votre code pour ouvrir la caisse",
    encaisser: "Code de la personne qui encaisse",
    fermer: "Votre code pour fermer la caisse",
    especes: "Votre code — entrée ou sortie d'espèces",
    commandes: "Votre code — liste des commandes",
    rapport: "Votre code — rapport des ventes",
    prendreLaMain: "Qui prend la main ? Tapez votre code",
};

export const TEXTES = {
    planEtat: "Touchez une table, puis tapez votre code.",
    caisseFermee:
        "La caisse est fermée. La caissière ou un chef de salle tape son code pour l'ouvrir.",
    ouvrirLaCaisse: "Ouvrir la caisse",
    neSaitPasEncaisser: (nom) => `${nom} ne peut pas encaisser : la caissière tape son code ici.`,
    envoye: (compte) => `Envoyé : ${compte}.`,
    retour: "Retour",
};
