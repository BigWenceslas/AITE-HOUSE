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

/** Pourcentage formaté (entier). */
export function fmtPct(value) {
    return (Math.round((value || 0) * 10) / 10).toString().replace(".", ",") + " %";
}

/** Variation signée colorée : renvoie {text, cls}. */
export function fmtDelta(pct) {
    const v = Math.round((pct || 0) * 10) / 10;
    const arrow = v > 0 ? "▲" : v < 0 ? "▼" : "■";
    return {
        text: `${arrow} ${Math.abs(v).toString().replace(".", ",")} %`,
        value: v,
    };
}

/** Périodes rapides : renvoie {date_from, date_to} en YYYY-MM-DD. */
export function periodRange(key) {
    const today = new Date();
    const iso = (d) => d.toISOString().slice(0, 10);
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
