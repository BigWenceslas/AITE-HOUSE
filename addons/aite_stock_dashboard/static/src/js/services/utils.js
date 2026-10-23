/** @odoo-module **/

/**
 * Utilitaires du tableau de bord Stock & Inventaire (charte AITE).
 * Tout le formatage vit ici et dans le composant — jamais dans les
 * templates OWL (leçon de production : pas de String/Math/… en XML).
 */

export const COLORS = {
    primary: "#714B67",
    success: "#3B6D11",
    info: "#185FA5",
    warning: "#854F0B",
    danger: "#A32D2D",
    teal: "#0F6E56",
    muted: "#888780",
};

export const CATEG_PALETTE = [
    "#714B67", "#185FA5", "#3B6D11", "#854F0B",
    "#A32D2D", "#0F6E56", "#5B4B8A", "#B0655A",
    "#8A7B4B", "#4B7B8A",
];

// Badges Bootstrap par classe sémantique renvoyée par le backend.
export const BADGE_CLS = {
    red: "text-bg-danger",
    amber: "text-bg-warning",
    teal: "text-bg-success",
    blue: "text-bg-info",
    prim: "text-bg-primary",
    gray: "text-bg-secondary",
};

export function fmtMoney(value, symbol = "F") {
    const n = value || 0;
    const rounded = n >= 0 ? (n + 0.5) | 0 : -((-n + 0.5) | 0);
    return rounded.toLocaleString("fr-FR") + " " + symbol;
}

export function fmtCompact(value) {
    const n = value || 0;
    const abs = n < 0 ? -n : n;
    if (abs >= 1e6) {
        return (n / 1e6).toFixed(1).replace(".", ",") + " M";
    }
    if (abs >= 1e3) {
        const k = n / 1e3;
        return ((k >= 0 ? (k + 0.5) | 0 : -((-k + 0.5) | 0))) + " k";
    }
    return "" + (n >= 0 ? (n + 0.5) | 0 : -((-n + 0.5) | 0));
}

export function fmtQty(value) {
    const n = value || 0;
    const r = ((n * 10 + (n >= 0 ? 0.5 : -0.5)) | 0) / 10;
    return r.toLocaleString("fr-FR");
}

/**
 * Pourcentage à la française, une décimale fixe, espace insécable avant
 * « % » : 0.5 → « 0,5 % », 2 → « 2,0 % » (règle 6 ; écart n° 41 : un même
 * taux ne s'écrit plus « 2 % » ici et « 2,0 % » ailleurs).
 */
export function fmtPct(value) {
    const n = Number(value) || 0;
    return n.toFixed(1).replace(".", ",") + "\u00a0%";
}

/** Forme accordée seule : « référence à zéro » / « références à zéro ». */
export function pluralWord(n, singular, pluralForm) {
    return (Number(n) || 0) > 1 ? pluralForm : singular;
}

/** Nombre entier à la française : « 1 234 » (espace fine insécable). */
export function fmtInt(value) {
    return Math.round(Number(value) || 0).toLocaleString("fr-FR");
}

/** Accord en nombre : « 1 rupture », « 0 rupture », « 1 234 ruptures ». */
export function plural(n, singular, pluralForm) {
    const count = Number(n) || 0;
    return fmtInt(count) + " " + pluralWord(count, singular, pluralForm);
}

/**
 * Quantité accordée : « 1 unité », « 1,5 unité », « 24 unités ». Une
 * quantité peut être décimale : règle française, pluriel à partir de 2,
 * sur le nombre tel qu'il s'affiche (arrondi au dixième par ``fmtQty``).
 */
export function fmtUnits(value) {
    const n = value || 0;
    const shown = Math.abs(((n * 10 + (n >= 0 ? 0.5 : -0.5)) | 0) / 10);
    return fmtQty(value) + " " + (shown >= 2 ? "unités" : "unité");
}

/**
 * Durée en jours, une décimale FIXE : « 12,0 j », « 12,3 j » — le rendu du
 * cockpit Direction et des Achats (« 12 j » ici — relecture de l'écart
 * n° 41).
 */
export function fmtDays(value) {
    const n = Number(value) || 0;
    const r = Math.round(n * 10) / 10 || 0;
    return r.toFixed(1).replace(".", ",") + " j";
}

/**
 * Couverture de stock : « ∞ » à partir d'un an — une référence sans
 * vente a une couverture infinie (999 j pour le moteur) — sinon
 * :func:`fmtDays`. Même règle sur le cockpit Direction.
 */
export function fmtCoverage(value) {
    return (Number(value) || 0) >= 365 ? "∞" : fmtDays(value);
}

export const PERIOD_PRESETS = [
    { key: "today", label: "Aujourd'hui" },
    { key: "week", label: "Cette semaine" },
    { key: "month", label: "Ce mois" },
    { key: "quarter", label: "3 mois" },
];

/**
 * Date LOCALE au format AAAA-MM-JJ attendu par le serveur et les champs
 * <input type="date">. ``toISOString()`` passe par UTC : à Douala (UTC+1),
 * le minuit local du 1er devenait le 30 du mois précédent (écart n° 38).
 */
export function localIsoDate(d) {
    const pad = (n) => (n < 10 ? "0" : "") + n;
    return d.getFullYear() + "-" + pad(d.getMonth() + 1) + "-" + pad(d.getDate());
}

export function periodRange(key, today = new Date()) {
    const iso = localIsoDate;
    let from = new Date(today);
    const to = new Date(today);
    switch (key) {
        case "today":
            break;
        case "week": {
            const dow = (today.getDay() + 6) % 7; // lundi = 0
            from.setDate(today.getDate() - dow);
            break;
        }
        case "quarter":
            from = new Date(today.getFullYear(), today.getMonth() - 2, 1);
            break;
        case "month":
        default:
            from = new Date(today.getFullYear(), today.getMonth(), 1);
    }
    return { date_from: iso(from), date_to: iso(to) };
}
