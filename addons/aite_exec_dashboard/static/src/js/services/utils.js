/** @odoo-module **/

/** Utilitaires du tableau de bord Direction (charte AITE). */

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

export function fmtInt(value) {
    return (value || 0).toLocaleString("fr-FR");
}

export const PERIOD_PRESETS = [
    { key: "month", label: "Ce mois" },
    { key: "quarter", label: "Ce trimestre" },
    { key: "year", label: "Cette année" },
];

export function periodRange(key) {
    const today = new Date();
    const iso = (d) => d.toISOString().slice(0, 10);
    let from;
    if (key === "quarter") {
        const q = (today.getMonth() / 3) | 0;
        from = new Date(today.getFullYear(), q * 3, 1);
    } else if (key === "year") {
        from = new Date(today.getFullYear(), 0, 1);
    } else {
        from = new Date(today.getFullYear(), today.getMonth(), 1);
    }
    return { date_from: iso(from), date_to: iso(today) };
}

export function monthLabel(key) {
    const NAMES = ["janv", "févr", "mars", "avr", "mai", "juin",
        "juil", "août", "sept", "oct", "nov", "déc"];
    const parts = key.split("-");
    const m = parseInt(parts[1], 10) - 1;
    return NAMES[m] + " " + parts[0].slice(2);
}
