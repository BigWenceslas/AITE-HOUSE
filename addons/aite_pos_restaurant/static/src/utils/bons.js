/** Les bons de préparation (demande du Messager : « imprimer 3 fois d'un
 * coup en cuisine » ; 18.0.1.0.13). Fonctions pures, sans Odoo.
 *
 * Un « bon » est ce qu'une imprimante reçoit pour un envoi : ses nouveaux
 * plats, ses annulations, ses notes modifiées et, le cas échéant, la note
 * générale de la table. Odoo en faisait plusieurs feuilles (« New »,
 * « Cancelled », « Note », « Message ») ; la caisse du restaurant en fait une
 * seule, en français. */

/** Le nombre d'exemplaires d'un bon : le réglage de l'imprimante (1 à 5)
 * dès que le bon porte un nouveau plat, même mêlé d'annulations ; un seul
 * exemplaire pour un bon fait seulement d'annulations, de notes ou de la
 * note générale (pas de papier gaspillé). `sections` : `{ nouveau, annule,
 * notes, noteGenerale }`. */
export function nombreDExemplaires(sections, reglage) {
    const nombre = Math.min(5, Math.max(1, Math.floor(Number(reglage) || 1)));
    return sections?.nouveau?.length ? nombre : 1;
}

/** Vrai si le bon n'a rien à dire. */
export function bonVide(sections) {
    return !(
        sections.nouveau.length ||
        sections.annule.length ||
        sections.notes.length ||
        sections.noteGenerale ||
        sections.changementDeMode
    );
}

/** Les imprimantes qui reçoivent une note générale envoyée sans plat :
 * celles qui ont déjà reçu (ou reçoivent dans ce même envoi) un plat de la
 * table — la note concerne ce qu'elles préparent ; aucune → toutes (on ne
 * sait pas encore qui préparera, la note ne doit pas se perdre).
 * `familles(imprimante)` rend les familles de l'imprimante ;
 * `famillesDuProduit(id)` celles d'un produit (avec leurs parents). */
export function imprimantesDeLaNote(imprimantes, produits, familles, famillesDuProduit) {
    const concernees = imprimantes.filter((imprimante) => {
        const siennes = familles(imprimante);
        return produits.some((id) => famillesDuProduit(id).some((f) => siennes.includes(f)));
    });
    return concernees.length ? concernees : [...imprimantes];
}
