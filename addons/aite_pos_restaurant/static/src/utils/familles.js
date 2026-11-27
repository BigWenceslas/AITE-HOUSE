/** Les familles de la carte (demandes du restaurant de Douala ; 18.0.1.0.14).
 * Fonctions pures, sans Odoo.
 *
 * - `imprimantesDuProduit` : quelles imprimantes de préparation reçoivent un
 *   plat. Une imprimante prend les familles cochées et leurs sous-familles
 *   (la liste des familles d'un produit comprend ses familles parentes,
 *   règle d'Odoo `parentPosCategIds`) ; l'imprimante « Autre » (« Prend
 *   tout ce qu'aucune autre imprimante ne prend ») prend en plus tout plat
 *   qu'aucune autre ne prend, sans famille compris.
 * - `grouperParFamille` : les lignes de l'addition rangées par famille de
 *   niveau 1, avec un sous-total par famille. */

/** Le repère d'un produit sans famille dans la liste de ses familles : il ne
 * figure sur aucune imprimante, mais compte comme « une famille » pour Odoo
 * (`getOrderChanges` écarte sinon le produit de l'envoi). */
export const AUCUNE_FAMILLE = -1;

/** Vrai si le produit `produit` ({ id, type }) ne part jamais seul sur
 * l'imprimante « Autre » (relecture de 18.0.1.0.14) : le pourboire, le
 * produit de la remise globale, le produit de remise d'un programme de
 * fidélité ou de promotion (`recompenses`), et la ligne mère d'un menu
 * (type « combo » : ses éléments partent chacun sur leur imprimante, le
 * menu ne sort que là où sa famille est cochée, comme dans Odoo). Un
 * produit offert (une pizza gratuite) part en préparation comme les autres. */
export function estHorsCuisine(produit, { pourboire = null, remise = null, recompenses = [] } = {}) {
    if (!produit) {
        return false;
    }
    if (produit.type === "combo") {
        return true;
    }
    return [pourboire, remise, ...recompenses].filter(Boolean).includes(produit.id);
}

/** Les imprimantes qui reçoivent un produit de familles `famillesDuProduit`
 * (ids, parents compris). `famillesDe(imprimante)` : ses familles cochées ;
 * `estAutre(imprimante)` : la case « Autre » ; `horsCuisine` : un produit
 * qui ne va jamais en préparation (pourboire, remise) : l'imprimante
 * « Autre » ne le prend pas. */
export function imprimantesDuProduit(imprimantes, famillesDuProduit, famillesDe, estAutre, horsCuisine = false) {
    const prend = (imprimante) => famillesDe(imprimante).some((f) => famillesDuProduit.includes(f));
    const preneuses = imprimantes.filter(prend);
    if (horsCuisine) {
        return preneuses;
    }
    const parFamille = preneuses.filter((imprimante) => !estAutre(imprimante));
    if (parFamille.length) {
        return preneuses;
    }
    // Personne d'autre ne le prend : l'imprimante « Autre » (s'il y en a une).
    const autre = imprimantes.find(estAutre);
    return autre && !preneuses.includes(autre) ? [...preneuses, autre] : preneuses;
}

/** Les lignes `lignes` (dans l'ordre du ticket) rangées par famille :
 * [{ cle, titre, rang, lignes, sousTotal }].
 *
 * - `familleDe(ligne)` : la famille de niveau 1 de la ligne
 *   ({ cle, titre, rang }), ou null (produit sans famille) ;
 * - `parentDe(ligne)` : la ligne mère d'un élément de menu (il reste avec
 *   son menu) ;
 * - `horsFamille(ligne)` : pourboire, remise globale, récompense — après
 *   les familles et « Autres », dans un dernier groupe sans titre ni
 *   sous-total (`horsFamilles: true` ; relecture de 18.0.1.0.14 : un
 *   « Sous-total Autres » négatif ne voulait rien dire) ;
 * - `montant(ligne)` : le montant de la ligne, tel qu'imprimé.
 *
 * Les familles suivent leur rang (la séquence de la caisse), puis leur
 * titre (comme Odoo : « sequence, name »), puis leur clé ; « Autres » (les
 * produits sans famille) vient après, puis les lignes hors familles. Une ligne négative (un produit rendu) reste
 * dans sa famille et diminue son sous-total. */
export function grouperParFamille(lignes, { familleDe, parentDe = () => null, horsFamille = () => false, montant, titreAutres }) {
    const groupes = new Map();
    const autres = { cle: "autres", titre: titreAutres, rang: Infinity, lignes: [], fin: [], sousTotal: 0 };
    const placees = new Map();
    for (const ligne of lignes) {
        const mere = parentDe(ligne);
        let groupe = mere && placees.get(mere);
        let enFin = false;
        if (!groupe) {
            if (horsFamille(ligne)) {
                groupe = autres;
                enFin = true;
            } else {
                const famille = familleDe(mere || ligne);
                if (!famille) {
                    groupe = autres;
                } else {
                    if (!groupes.has(famille.cle)) {
                        groupes.set(famille.cle, { ...famille, lignes: [], sousTotal: 0 });
                    }
                    groupe = groupes.get(famille.cle);
                }
            }
        }
        placees.set(ligne, groupe);
        (enFin ? groupe.fin : groupe.lignes).push(ligne);
        groupe.sousTotal += Number(montant(ligne)) || 0;
    }
    const tries = [...groupes.values()].sort(
        (a, b) =>
            a.rang - b.rang ||
            String(a.titre || "").localeCompare(String(b.titre || ""), "fr") ||
            (a.cle < b.cle ? -1 : a.cle > b.cle ? 1 : 0)
    );
    const resultat = tries.map(({ cle, titre, rang, lignes: l, sousTotal }) => ({ cle, titre, rang, lignes: l, sousTotal }));
    const somme = (l) => l.reduce((total, ligne) => total + (Number(montant(ligne)) || 0), 0);
    if (autres.lignes.length) {
        resultat.push({
            cle: autres.cle,
            titre: autres.titre,
            rang: autres.rang,
            lignes: autres.lignes,
            sousTotal: somme(autres.lignes),
        });
    }
    if (autres.fin.length) {
        resultat.push({
            cle: "hors",
            titre: "",
            rang: Infinity,
            lignes: autres.fin,
            sousTotal: somme(autres.fin),
            horsFamilles: true,
        });
    }
    return resultat;
}
