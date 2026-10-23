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

/**
 * Montant à retrancher, précédé de « − » seulement s'il est non nul :
 * « −0 FCFA » s'affichait quand rien n'était en retard (écarts n° 6, 69).
 */
export function fmtNegMoney(value, symbol = "F") {
    const n = value || 0;
    const rounded = n >= 0 ? (n + 0.5) | 0 : -((-n + 0.5) | 0);
    return (rounded > 0 ? "−" : "") + fmtMoney(rounded, symbol);
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
 * Pourcentage à la française, une décimale FIXE : « 40,0 % » (virgule,
 * espace insécable avant %), comme les autres tableaux de bord AITE
 * (écart n° 41 : « 40 % » ici, « 40,5 % » là).
 */
export function fmtPct(value, digits = 1) {
    const n = value || 0;
    return n.toFixed(digits).replace(".", ",") + "\u00a0%";
}

/** « 2026-10-14 » → « 14/10/2026 » (règle 6, écart n° 37). */
export function fmtDate(value) {
    const m = /^(\d{4})-(\d{2})-(\d{2})/.exec(value || "");
    return m ? m[3] + "/" + m[2] + "/" + m[1] : (value || "");
}

/**
 * Libellé de la carte des échéances situées entre la fenêtre d'alerte
 * (réglable, 7 j par défaut) et 30 j — même borne que le calcul du
 * serveur (``soon < jours avant échéance <= 30``). Le libellé était figé
 * à « 8–30 j » (écart n° 69).
 */
export function dueWindowLabel(soon) {
    const lo = (soon || 0) + 1;
    if (lo < 30) {
        return "À payer sous " + lo + "–30 j";
    }
    if (lo === 30) {
        return "À payer à 30 j";
    }
    return "Au-delà de l'alerte, jusqu'à 30 j";
}

/**
 * Nombre suivi du mot accordé : « 1 commande », « 3 commandes » — en
 * toutes lettres (« 3 cmd » — reprise de l'écart n° 42).
 */
export function fmtCount(n, one, many) {
    const k = Math.round(Number(n) || 0);
    return fmtInt(k) + " " + (Math.abs(k) > 1 ? many : one);
}

/** Nombre entier à la française : « 1 234 » (espace fine insécable). */
export function fmtInt(value) {
    return Math.round(Number(value) || 0).toLocaleString("fr-FR");
}

/**
 * Libellés de l'axe de l'échéancier, calculés depuis les tranches de
 * ``scheduleWeeks`` (tranche k = 7k à 7k + 6 jours avant l'échéance, la
 * première avec les factures échues, la dernière ouverte). L'axe disait
 * « S1 … S5+ » (reprise de l'écart n° 42).
 */
export function scheduleLabels() {
    const out = ["Échu ou sous 7 j"];
    for (let k = 1; k < 5; k++) {
        out.push((7 * k) + " à " + (7 * k + 6) + " j");
    }
    out.push("35 j et +");
    return out;
}

/** Durée en jours, une décimale fixe : « 23,0 j » — même rendu que le
 *  cockpit Direction pour le même délai (écart n° 41). */
export function fmtDays(value) {
    const n = Math.round((Number(value) || 0) * 10) / 10 || 0;
    return n.toFixed(1).replace(".", ",") + " j";
}

export const PERIOD_PRESETS = [
    { key: "today", label: "Aujourd'hui" },
    { key: "week", label: "Cette semaine" },
    { key: "month", label: "Ce mois" },
    { key: "quarter", label: "3 mois" },
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

export function periodRange(key) {
    const today = new Date();
    const iso = localIsoDate;
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
