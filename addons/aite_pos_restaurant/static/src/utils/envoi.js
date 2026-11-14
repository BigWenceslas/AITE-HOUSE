/** Ce qui est parti en cuisine ou au bar, d'après la caisse (spécification,
 * partie 4.1 ; incrément 4).
 *
 * `quantiteEnvoyee(line)` : la somme des `quantity` de
 * `order.last_order_preparation_change.lines` dont la clé commence par
 * l'`uuid` de la ligne (la clé peut porter la note). C'est une donnée
 * enregistrée et partagée entre les postes ; `saved_quantity`, elle, n'est
 * qu'en mémoire du poste. Le serveur tient sa propre quantité envoyée
 * (`aite_qte_envoyee`), qui fait foi pour l'annulation (R26). */
export function quantiteEnvoyee(line) {
    const lignes = line?.order_id?.last_order_preparation_change?.lines || {};
    let total = 0;
    for (const [cle, entree] of Object.entries(lignes)) {
        if (cle.startsWith(line.uuid) || entree?.uuid === line.uuid) {
            total += Number(entree?.quantity) || 0;
        }
    }
    return total;
}

/** La part envoyée de la ligne : jamais plus que sa quantité. */
export function partEnvoyee(line) {
    return Math.max(0, Math.min(line.get_quantity(), quantiteEnvoyee(line)));
}
