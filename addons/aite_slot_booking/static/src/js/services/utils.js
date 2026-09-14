/** @odoo-module **/

/** Utilitaires du tableau de bord Espaces & Prestations (charte AITE). */

export const COLORS = {
    primary: "#714B67", success: "#3B6D11", info: "#185FA5",
    warning: "#854F0B", danger: "#A32D2D", teal: "#0F6E56",
    muted: "#888780",
};

export const STATE_BADGE = {
    draft: "text-bg-secondary",
    confirmed: "text-bg-info",
    done: "text-bg-success",
    cancelled: "text-bg-secondary",
    no_show: "text-bg-danger",
};

export const STATE_LABEL = {
    draft: "Brouillon", confirmed: "Confirmée", done: "Réalisée",
    cancelled: "Annulée", no_show: "No-show",
};

export function fmtMoney(value, symbol = "F") {
    const n = value || 0;
    const rounded = n >= 0 ? (n + 0.5) | 0 : -((-n + 0.5) | 0);
    return rounded.toLocaleString("fr-FR") + " " + symbol;
}

export function fmtPct(value) {
    const n = value || 0;
    const r = ((n * 10 + (n >= 0 ? 0.5 : -0.5)) | 0) / 10;
    return ("" + r).replace(".", ",") + " %";
}

export function fmtHours(value) {
    const n = value || 0;
    const r = ((n * 10 + 0.5) | 0) / 10;
    return ("" + r).replace(".", ",") + " h";
}

export function hourLabel(h) {
    const hh = h | 0;
    const mm = ((h - hh) * 60 + 0.5) | 0;
    return ("" + (hh < 10 ? "0" + hh : hh)) + ":" +
        ("" + (mm < 10 ? "0" + mm : mm));
}

export const PERIOD_PRESETS = [
    { key: "today", label: "Aujourd'hui" },
    { key: "week", label: "Cette semaine" },
    { key: "month", label: "Ce mois" },
];

export function periodRange(key) {
    const today = new Date();
    const iso = (d) => d.toISOString().slice(0, 10);
    let from = new Date(today);
    const to = new Date(today);
    if (key === "week") {
        const dow = (today.getDay() + 6) % 7;
        from.setDate(today.getDate() - dow);
    } else if (key === "month") {
        from = new Date(today.getFullYear(), today.getMonth(), 1);
    }
    return { date_from: iso(from), date_to: iso(to) };
}

export function shiftDay(iso, delta) {
    const d = new Date(iso + "T12:00:00");
    d.setDate(d.getDate() + delta);
    return d.toISOString().slice(0, 10);
}
