/** @odoo-module **/

/**
 * Utilitaires du tableau de bord Achats & Fournisseurs (charte AITE).
 * Tout le formatage vit ici et dans le composant — jamais dans les
 * templates OWL (règle de production : pas de String/Math/… en XML).
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

export const AGING_COLORS = [
    "#0F6E56", "#854F0B", "#A85A18", "#A32D2D", "#5e1b1b",
];

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

export function fmtPct(value) {
    const n = value || 0;
    const r = ((n * 10 + (n >= 0 ? 0.5 : -0.5)) | 0) / 10;
    return ("" + r).replace(".", ",") + " %";
}

export function fmtDays(value) {
    const n = value || 0;
    const r = ((n * 10 + 0.5) | 0) / 10;
    return ("" + r).replace(".", ",") + " j";
}

export const PERIOD_PRESETS = [
    { key: "today", label: "Aujourd'hui" },
    { key: "week", label: "Cette semaine" },
    { key: "month", label: "Ce mois" },
    { key: "quarter", label: "3 mois" },
];

export function periodRange(key) {
    const today = new Date();
    const iso = (d) => d.toISOString().slice(0, 10);
    let from = new Date(today);
    const to = new Date(today);
    switch (key) {
        case "today":
            break;
        case "week": {
            const dow = (today.getDay() + 6) % 7;
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
