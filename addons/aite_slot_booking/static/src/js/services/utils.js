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
    cancelled: "Annulée", no_show: "Non présenté",
};

export function fmtMoney(value, symbol = "F") {
    const n = value || 0;
    const rounded = n >= 0 ? (n + 0.5) | 0 : -((-n + 0.5) | 0);
    return rounded.toLocaleString("fr-FR") + " " + symbol;
}

/** « 56,0 % » : une décimale fixe, espace insécable (règle 6, comme les
 *  autres tableaux de bord) — jamais « 56 % ». */
export function fmtPct(value) {
    const n = value || 0;
    return n.toFixed(1).replace(".", ",") + "\u00a0%";
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

/**
 * Date LOCALE au format AAAA-MM-JJ (paramètre envoyé au serveur).
 *
 * Écart n° 38 : ``toISOString()`` convertit en UTC ; à Douala (UTC+1), le
 * 1er du mois à minuit devenait le 30 du mois précédent (« Ce mois »
 * démarrait la veille). On lit donc l'année, le mois et le jour du poste.
 */
export function localIsoDate(d) {
    const pad = (n) => (n < 10 ? "0" : "") + n;
    return d.getFullYear() + "-" + pad(d.getMonth() + 1) + "-" +
        pad(d.getDate());
}

/** Période d'un préréglage (``today`` : maintenant, injectable en test). */
export function periodRange(key, today = new Date()) {
    let from = new Date(today);
    const to = new Date(today);
    if (key === "week") {
        const dow = (today.getDay() + 6) % 7;
        from.setDate(today.getDate() - dow);
    } else if (key === "month") {
        from = new Date(today.getFullYear(), today.getMonth(), 1);
    }
    return { date_from: localIsoDate(from), date_to: localIsoDate(to) };
}

/** Jour AAAA-MM-JJ décalé de ``delta`` jours, sans passer par l'UTC. */
export function shiftDay(iso, delta) {
    const [y, m, d] = iso.split("-").map((x) => parseInt(x, 10));
    return localIsoDate(new Date(y, m - 1, d + delta));
}

/** Jour AAAA-MM-JJ affiché JJ/MM/AAAA (règle 6 ; écart n° 3). */
export function fmtDay(iso) {
    const [y, m, d] = (iso || "").split("-");
    return d && m && y ? d + "/" + m + "/" + y : iso || "";
}
