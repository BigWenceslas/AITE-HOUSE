/** Partager l'addition à parts égales : le calcul, sans rien d'Odoo (demande
 * du Messager : « diviser la facture à part égale par le nombre de
 * personnes qui doivent payer »).
 *
 * Le montant à partager est compté en « pas » : l'unité de la devise
 * (1 FCFA ; 0,01 pour une devise à centimes), ou le pas de l'arrondi des
 * espèces d'Odoo s'il est actif sur la caisse (25 FCFA, par exemple).
 * - Sans arrondi des espèces, chaque part sauf la dernière est le montant
 *   divisé par le nombre de personnes, arrondi vers le bas à l'unité ; la
 *   dernière est ce qui reste, au plus quelques francs de plus (moins d'un
 *   franc par personne) : 100 000 FCFA en 3 → 33 333, 33 333, 33 334. La
 *   fenêtre dit un seul montant, comme demandé.
 * - Avec l'arrondi des espèces, le reste de la division peut valoir
 *   plusieurs pas : laissé au dernier, il lui ferait payer jusqu'au double
 *   des autres (1 000 en 7 au pas de 25 : 125 × 6 et 250). Les pas restants
 *   vont donc, un chacun, aux dernières personnes, et la dernière part est
 *   ce qui reste (elle absorbe ce qui est plus petit qu'un pas) : deux parts
 *   diffèrent d'un pas au plus. 1 000 en 7 → 125, 125, 150, 150, 150, 150,
 *   150 ; 8 010 en 3 → 2 650, 2 675, 2 685 (2 675 en espèces).
 *
 * Chaque part, sauf la dernière, est un multiple de l'arrondi : elle se
 * paie en espèces sans « Erreur d'arrondi » d'Odoo, et dans n'importe quel
 * autre mode ; seule la dernière, payée en espèces, est arrondie par Odoo,
 * comme tout dernier paiement. */

/** Le plus grand nombre de personnes proposé. */
export const PARTS_MAXIMUM = 20;
/** Les gros boutons de la fenêtre ; « Plus » ouvre les autres jusqu'à 20. */
export const PARTS_BOUTONS = [2, 3, 4, 5, 6, 7, 8];

/** Le pas du partage : l'arrondi des espèces s'il est actif et plus grand
 * que l'unité de la devise, sinon l'unité de la devise. */
export function pasDuPartage(config, currency) {
    const unite = currency?.rounding || 1;
    const arrondi = config?.cash_rounding ? config.rounding_method?.rounding || 0 : 0;
    return arrondi > unite ? arrondi : unite;
}

/** Un montant sans les restes de la virgule flottante. */
function propre(montant, pas) {
    const decimales = Math.max(0, Math.ceil(-Math.log10(pas)) + 2);
    return Number(montant.toFixed(decimales));
}

/** Les pas à partager : `q` chacun, et `r` pas restants (moins que le
 * nombre de personnes). */
function repartition(base, nombre, pas) {
    const unites = Math.floor(base / pas + 1e-9);
    return { q: Math.floor(unites / nombre), r: unites % nombre };
}

/** Les pas restants sont répartis quand le pas est celui de l'arrondi des
 * espèces (plus grand que l'unité de la devise). */
function arepartir(pas, unite) {
    return pas > unite * (1 + 1e-9);
}

function partageValide(base, nombre, pas) {
    return base > 0 && nombre >= 2 && pas > 0 && repartition(base, nombre, pas).q > 0;
}

/** La part de la personne de rang `rang` (1 = la première) : `q` pas ;
 * avec l'arrondi des espèces (`pas` plus grand que `unite`, l'unité de la
 * devise), un pas de plus pour les `r` dernières. La dernière (rang =
 * nombre) est ce qui reste du montant. 0 quand le montant ne se partage
 * pas en autant de parts (moins d'un pas chacun). */
export function montantDUnePart(base, nombre, pas, rang = 1, unite = 1) {
    if (!partageValide(base, nombre, pas)) {
        return 0;
    }
    const { q } = repartition(base, nombre, pas);
    const r = arepartir(pas, unite) ? repartition(base, nombre, pas).r : 0;
    if (rang >= nombre) {
        // Les nombre − 1 premières : q pas chacune, et un de plus pour
        // celles des r dernières qui ne sont pas la toute dernière.
        const avant = (nombre - 1) * q + Math.max(0, r - 1);
        return propre(base - avant * pas, pas);
    }
    const unites = rang > nombre - r ? q + 1 : q;
    return propre(unites * pas, pas);
}

/** Toutes les parts, dans l'ordre (la dernière comprise). */
export function partsDuPartage(base, nombre, pas, unite = 1) {
    if (!partageValide(base, nombre, pas)) {
        return [];
    }
    return Array.from({ length: nombre }, (_, i) =>
        montantDUnePart(base, nombre, pas, i + 1, unite)
    );
}

/** La plus petite et la plus grande part, sans la dernière (qui « paie ce
 * qui reste ») : ce que dit la fenêtre. */
export function fourchetteDesParts(base, nombre, pas, unite = 1) {
    const parts = partsDuPartage(base, nombre, pas, unite).slice(0, -1);
    return parts.length ? { min: Math.min(...parts), max: Math.max(...parts) } : { min: 0, max: 0 };
}

/** Le nombre de personnes est possible : chaque part vaut au moins un pas. */
export function partagePossible(base, nombre, pas) {
    return nombre >= 2 && nombre <= PARTS_MAXIMUM && montantDUnePart(base, nombre, pas) > 0;
}

/** La présélection : les personnes de la table si elles sont au moins 2
 * (20 au plus), sinon 2. */
export function preselection(personnes) {
    const nombre = Math.floor(Number(personnes) || 0);
    return nombre >= 2 ? Math.min(nombre, PARTS_MAXIMUM) : 2;
}
