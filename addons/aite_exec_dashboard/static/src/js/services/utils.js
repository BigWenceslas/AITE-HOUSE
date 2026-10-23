/** @odoo-module **/

/** Utilitaires du tableau de bord Direction (charte AITE). */

export function fmtMoney(value, symbol = "F") {
    const n = value || 0;
    const rounded = n >= 0 ? (n + 0.5) | 0 : -((-n + 0.5) | 0);
    return rounded.toLocaleString("fr-FR") + " " + symbol;
}

/**
 * Pourcentage à la française, une décimale FIXE : « 64,0 % » (virgule,
 * espace insécable avant %) — le même rendu que le cockpit Direction
 * (écart n° 41 : « 64 % » ici, « 64,0 % » là-bas).
 */
export function fmtPct(value, digits = 1) {
    const n = value || 0;
    return n.toFixed(digits).replace(".", ",") + "\u00a0%";
}

export function fmtInt(value) {
    return (value || 0).toLocaleString("fr-FR");
}

/** Écart en % avec son sens : « ▲ +12,5 % » / « ▼ 3,0 % ». */
export function fmtDelta(value) {
    if (value === null || value === undefined) {
        return "";
    }
    const sign = value >= 0 ? "▲ +" : "▼ ";
    return sign + fmtPct(Math.abs(value));
}

export const PERIOD_PRESETS = [
    { key: "month", label: "Ce mois" },
    { key: "quarter", label: "Ce trimestre" },
    { key: "year", label: "Cette année" },
];

/**
 * Date LOCALE au format AAAA-MM-JJ (paramètre de période envoyé au
 * serveur). ``toISOString()`` passe par l'UTC : à Douala (UTC+1), minuit
 * le 1er devenait le 30 du mois précédent (écart n° 38).
 */
export function localIsoDate(d) {
    const pad = (n) => (n < 10 ? "0" : "") + n;
    return d.getFullYear() + "-" + pad(d.getMonth() + 1) + "-"
        + pad(d.getDate());
}

/** « 2026-10-01 » → « 01/10/2026 » (règle 6) ; tout autre texte inchangé. */
export function fmtDate(value) {
    const m = /^(\d{4})-(\d{2})-(\d{2})/.exec(value || "");
    return m ? m[3] + "/" + m[2] + "/" + m[1] : (value || "");
}

export function periodRange(key) {
    const today = new Date();
    const iso = localIsoDate;
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
