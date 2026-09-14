/** @odoo-module **/

/**
 * Utilitaires partagés du dashboard POS Analytics.
 *
 * - Formatage des nombres en FCFA / devise courante (séparateur fr-FR).
 * - Palette de couleurs alignée sur la charte Odoo + maquette LAVERANDAH.
 * - Définitions des périodes rapides (toute, mois, semaine, jour, T1, T4).
 */

export const COLORS = {
    primary: "#714B67",   // violet Odoo
    success: "#3B6D11",   // vert marge
    info: "#185FA5",      // bleu CA
    warning: "#854F0B",   // ambre
    danger: "#A32D2D",    // rouge CMV / écart
    teal: "#0F6E56",      // catégorie soft
};

export const CATEGORY_PALETTE = {
    // Mapping fallback par nom de catégorie. À terme, à stocker sur
    // pos.category via un champ couleur custom.
    bière: { col: "#714B67", bg: "#EEEDFE", text: "#3C3489" },
    biere: { col: "#714B67", bg: "#EEEDFE", text: "#3C3489" },
    bières: { col: "#714B67", bg: "#EEEDFE", text: "#3C3489" },
    soft: { col: "#1D9E75", bg: "#E1F5EE", text: "#0F6E56" },
    softs: { col: "#1D9E75", bg: "#E1F5EE", text: "#0F6E56" },
    malt: { col: "#BA7517", bg: "#FAEEDA", text: "#854F0B" },
    malts: { col: "#BA7517", bg: "#FAEEDA", text: "#854F0B" },
    vin: { col: "#185FA5", bg: "#E6F1FB", text: "#0C447C" },
    vins: { col: "#185FA5", bg: "#E6F1FB", text: "#0C447C" },
    eau: { col: "#888780", bg: "#F1EFE8", text: "#5F5E5A" },
};

const FALLBACK_COLORS = ["#714B67", "#1D9E75", "#BA7517", "#185FA5", "#888780",
                        "#A32D2D", "#0F6E56", "#854F0B"];

/**
 * Retourne une palette pour une catégorie donnée. Fait du best-effort
 * sur le nom, fallback sur la palette circulaire.
 */
export function getCategoryColors(name, index = 0) {
    if (!name) return { col: FALLBACK_COLORS[index % FALLBACK_COLORS.length],
                       bg: "#F1EFE8", text: "#5F5E5A" };
    const key = name.toLowerCase().trim();
    if (CATEGORY_PALETTE[key]) return CATEGORY_PALETTE[key];
    return {
        col: FALLBACK_COLORS[index % FALLBACK_COLORS.length],
        bg: "#F1EFE8",
        text: "#5F5E5A",
    };
}

/**
 * Format un nombre en groupes fr-FR sans décimales.
 * Ex : 1234567 → "1 234 567"
 */
export function fmt(n) {
    if (n === null || n === undefined || isNaN(n)) return "0";
    return Math.round(Number(n)).toLocaleString("fr-FR");
}

/**
 * Format un montant avec symbole de devise (suffixe par défaut).
 * On utilise "F" pour FCFA car le symbole "FCFA" est trop long pour les KPIs.
 */
export function fmtMoney(n, symbol = "F") {
    return `${fmt(n)} ${symbol}`;
}

/** Format un pourcentage avec 1 décimale. */
export function fmtPct(n) {
    if (n === null || n === undefined || isNaN(n)) return "0%";
    return `${Number(n).toFixed(1)}%`;
}

/**
 * Formate une variation (delta %) avec signe et flèche.
 * Retourne null si la valeur n'est pas comparable (pas de base N-1).
 */
export function fmtDelta(n) {
    if (n === null || n === undefined || isNaN(n)) return null;
    const v = Number(n);
    const arrow = v > 0 ? "▲" : (v < 0 ? "▼" : "■");
    const sign = v > 0 ? "+" : "";
    return `${arrow} ${sign}${v.toFixed(1)}%`;
}

/** Classe CSS (up/down/flat) selon le signe d'une variation. */
export function deltaClass(n) {
    if (n === null || n === undefined || isNaN(n)) return "flat";
    if (n > 0) return "up";
    if (n < 0) return "down";
    return "flat";
}

/**
 * Formate un montant signé (utile pour les écarts de caisse).
 * Ex : -42000 → "−42 000 F" ; 12000 → "+12 000 F".
 */
export function fmtSigned(n, symbol = "F") {
    if (n === null || n === undefined || isNaN(n)) return `0 ${symbol}`;
    const v = Math.round(Number(n));
    if (v === 0) return `0 ${symbol}`;
    const sign = v > 0 ? "+" : "−";
    return `${sign}${Math.abs(v).toLocaleString("fr-FR")} ${symbol}`;
}

/** Format une date ISO → fr-FR (DD/MM/YYYY). */
export function fmtDate(s) {
    if (!s) return "";
    const d = new Date(s);
    if (isNaN(d.getTime())) return s;
    return d.toLocaleDateString("fr-FR", {
        day: "2-digit", month: "2-digit", year: "numeric",
    });
}

/** Nombre de jours entre deux dates ISO (inclusif). */
export function daysBetween(from, to) {
    const a = new Date(from), b = new Date(to);
    return Math.max(1, Math.round((b - a) / 86400000) + 1);
}

/**
 * Génère la liste des périodes rapides. La période "Toute la période"
 * est calibrée sur la maquette LAVERANDAH (oct 2025 → mai 2026), mais
 * la première charge du dashboard remplace ces valeurs par les bornes
 * réelles trouvées dans pos.session.
 */
export function getQuickPeriods(today = new Date()) {
    const iso = (d) => d.toISOString().slice(0, 10);

    // Aujourd'hui
    const todayStr = iso(today);

    // Cette semaine (lundi → aujourd'hui)
    const dow = (today.getDay() + 6) % 7;  // 0 = lundi
    const monday = new Date(today);
    monday.setDate(today.getDate() - dow);

    // Ce mois
    const monthStart = new Date(today.getFullYear(), today.getMonth(), 1);

    // Trimestre courant
    const q = Math.floor(today.getMonth() / 3);
    const qStart = new Date(today.getFullYear(), q * 3, 1);

    // Année
    const yStart = new Date(today.getFullYear(), 0, 1);

    return {
        all: { label: "Toute la période", from: null, to: null },
        today: { label: "Aujourd'hui", from: todayStr, to: todayStr },
        week: { label: "Cette semaine", from: iso(monday), to: todayStr },
        month: { label: "Ce mois", from: iso(monthStart), to: todayStr },
        quarter: { label: "Ce trimestre", from: iso(qStart), to: todayStr },
        year: { label: "Cette année", from: iso(yStart), to: todayStr },
    };
}

/**
 * Plages horaires rapides. ``from``/``to`` en heures pleines [0-23],
 * borne haute incluse côté backend. ``null`` = pas de filtre horaire.
 */
export const HOUR_PRESETS = {
    all:       { label: "Toute la journée", from: null, to: null },
    morning:   { label: "Matin 6–12h",      from: 6,  to: 11 },
    afternoon: { label: "Après-midi 12–18h",from: 12, to: 17 },
    evening:   { label: "Soir 18–23h",      from: 18, to: 23 },
    night:     { label: "Nuit 23–6h",       from: 23, to: 5  },  // à cheval minuit
};

/**
 * Jours de semaine (ISO : 1 = lundi … 7 = dimanche).
 * Les raccourcis ``week`` / ``weekend`` renvoient des listes.
 */
export const WEEKDAYS = [
    { key: 1, label: "Lun" }, { key: 2, label: "Mar" }, { key: 3, label: "Mer" },
    { key: 4, label: "Jeu" }, { key: 5, label: "Ven" }, { key: 6, label: "Sam" },
    { key: 7, label: "Dim" },
];
export const WEEKDAY_PRESETS = {
    all:     [],
    week:    [1, 2, 3, 4, 5],
    weekend: [6, 7],
};
export const TABS = [
    { key: "dashboard",     label: "Tableau de bord", icon: "fa-tachometer" },
    { key: "bycaisse",      label: "Par caisse",      icon: "fa-cash-register" },
    { key: "sessions",      label: "Sessions POS",    icon: "fa-list" },
    { key: "products",      label: "Articles",        icon: "fa-cube" },
    { key: "margins",       label: "Marges & CMV",    icon: "fa-line-chart" },
    { key: "categories",    label: "Par catégorie",   icon: "fa-th-large" },
    { key: "discrepancies", label: "Écarts de caisse",icon: "fa-exclamation-triangle" },
    { key: "payments",      label: "Paiements",       icon: "fa-credit-card" },
];
