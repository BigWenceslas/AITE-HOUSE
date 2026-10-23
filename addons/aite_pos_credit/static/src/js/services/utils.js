/** @odoo-module **/

/**
 * Utilitaires partagés du tableau de bord POS Crédit (recouvrement).
 *
 * Formatage FCFA / devise courante, palette de couleurs (charte Odoo +
 * codes Mobile Money), libellés des moyens de paiement et des sévérités.
 */

export const COLORS = {
    primary: "#714B67",
    success: "#3B6D11",
    info: "#185FA5",
    warning: "#854F0B",
    danger: "#A32D2D",
    teal: "#0F6E56",
    critical: "#5e1b1b",
};

// Couleurs des moyens de paiement (cohérence avec le prototype).
export const PAYMENT_COLORS = {
    mtn: "#FFC403",      // jaune MTN
    orange: "#FF7900",   // orange Orange Money
    cash: "#3B6D11",     // vert espèces
    card: "#185FA5",
    transfer: "#888780",
};

export const PAYMENT_LABELS = {
    mtn: "MTN Mobile Money",
    orange: "Orange Money",
    cash: "Espèces",
    card: "Carte bancaire",
    transfer: "Virement / autre",
};

// Couleurs des tranches d'âge (aging) — du plus sain au plus risqué.
export const AGING_COLORS = ["#3B6D11", "#854F0B", "#A32D2D", "#5e1b1b"];

export const SEVERITY_BADGE = {
    recent: { label: "Récente", cls: "text-bg-success" },
    late: { label: "En retard", cls: "text-bg-warning" },
    critical: { label: "Critique", cls: "text-bg-danger" },
    settled: { label: "Réglée", cls: "text-bg-secondary" },
};

/**
 * Formate un montant dans la devise courante, style FCFA (suffixe " F").
 * Best-effort : si l'API d'Odoo expose un symbole, on l'utilise.
 */
export function fmtMoney(value, symbol = "F") {
    const n = Math.round(value || 0);
    return n.toLocaleString("fr-FR") + " " + symbol;
}

/** Format compact pour les axes (ex. 1 250 000 -> "1,3 M"). */
export function fmtCompact(value) {
    const n = value || 0;
    if (Math.abs(n) >= 1e6) {
        return (n / 1e6).toFixed(1).replace(".", ",") + " M";
    }
    if (Math.abs(n) >= 1e3) {
        return Math.round(n / 1e3) + " k";
    }
    return String(Math.round(n));
}

/** Arrondi à une décimale ; « || 0 » évite un « -0,0 » pour -0,04. */
function round1(value) {
    return Math.round((value || 0) * 10) / 10 || 0;
}

/**
 * Pourcentage à la française, une décimale FIXE : « 64,0 % » (virgule,
 * espace insécable avant %). Même rendu que la carte du cockpit Direction,
 * qui reprend ces chiffres (écart n° 41 : « 64 % » ici, « 64,0 % » là-bas).
 */
export function fmtPct(value) {
    return round1(value).toFixed(1).replace(".", ",") + "\u00a0%";
}

/**
 * Variation signée : « ▲ +12,5 % », « ▼ 3,0 % », « ■ 0,0 % » (même rendu
 * que le cockpit Direction). Renvoie {text, value} ; ``value`` est la
 * variation arrondie à une décimale, qui décide de la couleur.
 */
export function fmtDelta(pct) {
    const v = round1(pct);
    const arrow = v > 0 ? "▲ +" : v < 0 ? "▼ " : "■ ";
    return {
        text: arrow + fmtPct(Math.abs(v)),
        value: v,
    };
}

/** Nombre entier à la française : « 1 234 » (espace fine insécable). */
export function fmtInt(value) {
    return Math.round(Number(value) || 0).toLocaleString("fr-FR");
}

/**
 * Nombre suivi du mot accordé : « 1 ardoise ouverte », « 12 ardoises
 * ouvertes » — pluriel à partir de 2, jamais de « (s) ».
 */
export function fmtCount(n, one, many) {
    const k = Math.round(Number(n) || 0);
    return fmtInt(k) + " " + (Math.abs(k) > 1 ? many : one);
}

/**
 * Durée en jours, une décimale FIXE : « 12,3 j », « 45,0 j » — le rendu du
 * cockpit Direction et des Achats pour le même délai (« 12 j » ici, arrondi
 * à l'entier — relecture de l'écart n° 41).
 */
export function fmtDays(value) {
    return round1(value).toFixed(1).replace(".", ",") + " j";
}

/**
 * Âge d'une ardoise, en jours entiers : « 160 j » — le même rendu que le
 * cockpit Direction (« Plus ancienne dette », « Top débiteurs »). Une
 * MOYENNE de jours garde sa décimale (:func:`fmtDays`).
 */
export function fmtAge(value) {
    return fmtInt(value) + " j";
}

/**
 * Date LOCALE au format AAAA-MM-JJ (paramètre de période envoyé au serveur).
 *
 * Pas de ``toISOString()`` : elle passe par UTC, et le minuit local du 1er
 * devenait la veille sur un poste à l'est de Greenwich (Douala, UTC+1) —
 * « Ce mois » démarrait le 30 du mois précédent.
 */
export function localIsoDate(d) {
    const pad = (n) => (n < 10 ? "0" : "") + n;
    return d.getFullYear() + "-" + pad(d.getMonth() + 1) + "-" + pad(d.getDate());
}

/**
 * Périodes rapides : renvoie {date_from, date_to} en YYYY-MM-DD (date locale).
 * ``now`` (facultatif, maintenant par défaut) sert aux tests.
 */
export function periodRange(key, now = new Date()) {
    const today = new Date(now);
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
        case "month":
            from = new Date(today.getFullYear(), today.getMonth(), 1);
            break;
        case "all":
            from = new Date(2000, 0, 1);
            break;
        default:
            from = new Date(today.getFullYear(), today.getMonth(), 1);
    }
    return { date_from: iso(from), date_to: iso(to) };
}

export const PERIOD_PRESETS = [
    { key: "today", label: "Aujourd'hui" },
    { key: "week", label: "Cette semaine" },
    { key: "month", label: "Ce mois" },
    { key: "all", label: "Tout" },
];
