/** @odoo-module **/

/**
 * Utilitaires partagés du tableau de bord Front Desk.
 *
 * Formatage FCFA / devise courante, palette de couleurs (charte Odoo),
 * libellés et couleurs des statuts de chambres, presets de période.
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

// Couleurs des statuts de chambre (room rack / room board).
export const ROOM_STATUS_COLORS = {
    free: "#3B6D11",         // libre → vert
    arrival: "#185FA5",      // arrivée prévue → bleu
    occupied: "#A32D2D",     // occupée → rouge
    cleaning: "#854F0B",     // ménage / à contrôler → ocre
    out_of_order: "#5f5e5a", // hors service → gris foncé
};

export const ROOM_STATUS_LABELS = {
    free: "Libre",
    arrival: "Arrivée prévue",
    occupied: "Occupée",
    cleaning: "Ménage",
    out_of_order: "Hors service",
};

// Ordre d'affichage de la légende du room board.
export const ROOM_STATUS_ORDER = [
    "free", "arrival", "occupied", "cleaning", "out_of_order",
];

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

/** Pourcentage formaté (1 décimale, virgule française). */
export function fmtPct(value) {
    return (Math.round((value || 0) * 10) / 10)
        .toString().replace(".", ",") + " %";
}

/** Périodes rapides : renvoie {date_from, date_to} en YYYY-MM-DD. */
export function periodRange(key) {
    const today = new Date();
    const iso = (d) =>
        d.getFullYear() + "-" +
        String(d.getMonth() + 1).padStart(2, "0") + "-" +
        String(d.getDate()).padStart(2, "0");
    let from = new Date(today);
    let to = new Date(today);
    switch (key) {
        case "today":
            break;
        case "7d":
            from.setDate(today.getDate() - 6);
            break;
        case "month":
            from = new Date(today.getFullYear(), today.getMonth(), 1);
            break;
        case "last_month":
            from = new Date(today.getFullYear(), today.getMonth() - 1, 1);
            to = new Date(today.getFullYear(), today.getMonth(), 0);
            break;
        default:
            from = new Date(today.getFullYear(), today.getMonth(), 1);
    }
    return { date_from: iso(from), date_to: iso(to) };
}

export const PERIOD_PRESETS = [
    { key: "today", label: "Aujourd'hui" },
    { key: "7d", label: "7 derniers jours" },
    { key: "month", label: "Ce mois" },
    { key: "last_month", label: "Mois dernier" },
];
