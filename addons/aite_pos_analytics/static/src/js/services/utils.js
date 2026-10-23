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
    // Texte secondaire (graduations, légendes) : #888780 n'offrait que
    // 3,6:1 sur fond blanc ; ce gris passe le seuil AA de 4,5:1 sur les
    // fonds du tableau de bord (écart n° 71).
    muted: "#66655f",
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
 * Quantité vendue, en toutes lettres et accordée : « 1 unité »,
 * « 926 unités » (plus de « 926 u » dans les classements). Accord sur le
 * nombre affiché (arrondi), règle française : pluriel à partir de 2.
 */
export function fmtUnits(n) {
    const shown = Math.abs(Math.round(Number(n) || 0));
    return `${fmt(n)} ${shown >= 2 ? "unités" : "unité"}`;
}

/**
 * Symbole de la devise de la société (« FCFA » chez LAVERANDAH), fixé au
 * chargement du tableau de bord (``get_dashboard_meta``). Les montants
 * s'écrivaient « 4 127 500 F » ici et « 4 127 500 FCFA » sur tous les
 * autres tableaux de bord pour le même CA (relecture de l'intégration).
 */
let CURRENCY_SYMBOL = "FCFA";

export function setCurrencySymbol(symbol) {
    if (symbol) {
        CURRENCY_SYMBOL = symbol;
    }
}

/** Montant arrondi, séparateurs fr-FR, suivi du symbole de la devise. */
export function fmtMoney(n, symbol) {
    return `${fmt(n)} ${symbol || CURRENCY_SYMBOL}`;
}

/**
 * Graduation compacte d'un axe : « 250 k », « 4,0 M » (et non « 250k »,
 * « 4000k ») — le rendu des autres tableaux de bord AITE.
 */
export function fmtCompact(value) {
    const n = Number(value) || 0;
    const abs = Math.abs(n);
    if (abs >= 1e6) {
        return (n / 1e6).toFixed(1).replace(".", ",") + " M";
    }
    if (abs >= 1e3) {
        return Math.round(n / 1e3) + " k";
    }
    return String(Math.round(n));
}

/** Arrondi à une décimale ; « || 0 » évite un « -0,0 ». */
function round1(v) {
    return Math.round((Number(v) || 0) * 10) / 10 || 0;
}

/** Nombre à une décimale, virgule française : 56 → « 56,0 ». */
function fmtDecimal1(v) {
    return round1(v).toFixed(1).replace(".", ",");
}

/**
 * Pourcentage à la française : une décimale, virgule, espace insécable
 * avant « % » — « 56,0 % » et non « 56.0% » (règle 6 ; écarts n° 5, 41).
 */
export function fmtPct(n) {
    if (n === null || n === undefined || isNaN(n)) return "0,0\u00a0%";
    return `${fmtDecimal1(n)}\u00a0%`;
}

/**
 * Formate une variation (delta %) avec signe et flèche :
 * « ▲ +12,5 % », « ▼ 3,0 % », « ■ 0,0 % » — le rendu unique des tableaux
 * de bord AITE (POS Crédit, Direction) : la flèche dit le sens, pas de
 * « − » en plus (« ▼ −3,0 % » ici seulement — relecture de l'intégration).
 * Retourne null si la valeur n'est pas comparable (pas de base de
 * comparaison sur la période précédente).
 */
export function fmtDelta(n) {
    if (n === null || n === undefined || isNaN(n)) return null;
    const v = round1(n);
    const arrow = v > 0 ? "▲ +" : (v < 0 ? "▼ " : "■ ");
    return `${arrow}${fmtDecimal1(Math.abs(v))}\u00a0%`;
}

/**
 * Classe CSS (up = vert / down = rouge / flat) d'une variation, sur la
 * valeur AFFICHÉE (arrondie) : « ■ 0,0 % » est toujours neutre.
 * ``higherIsBetter`` à false pour un coût : un CMV qui monte est une
 * mauvaise nouvelle et s'affiche en rouge (écart n° 62).
 */
export function deltaClass(n, higherIsBetter = true) {
    if (n === null || n === undefined || isNaN(n)) return "flat";
    const v = round1(n);
    const good = higherIsBetter ? v > 0 : v < 0;
    const bad = higherIsBetter ? v < 0 : v > 0;
    if (good) return "up";
    if (bad) return "down";
    return "flat";
}

/**
 * Formate un montant signé (utile pour les écarts de caisse).
 * Ex : -42000 → "−42 000 FCFA" ; 12000 → "+12 000 FCFA".
 */
export function fmtSigned(n, symbol) {
    const sym = symbol || CURRENCY_SYMBOL;
    if (n === null || n === undefined || isNaN(n)) return `0 ${sym}`;
    const v = Math.round(Number(n));
    if (v === 0) return `0 ${sym}`;
    const sign = v > 0 ? "+" : "−";
    return `${sign}${Math.abs(v).toLocaleString("fr-FR")} ${sym}`;
}

/**
 * Nombre suivi du mot accordé : « 1 commande », « 1 234 commandes » —
 * pluriel à partir de 2, jamais de « (s) ».
 */
export function fmtCount(n, one, many) {
    const k = Math.round(Number(n) || 0);
    return `${fmt(k)} ${Math.abs(k) > 1 ? many : one}`;
}

/**
 * Lit une date rendue par le serveur.
 *
 * - « AAAA-MM-JJ » (borne de période) : la date telle quelle, à minuit
 *   local. ``new Date("2026-10-01")`` la lisait comme minuit UTC, soit le
 *   30/09 sur un poste à l'ouest de Greenwich.
 * - « AAAA-MM-JJ HH:MM:SS » (date-heure du serveur, toujours en UTC) :
 *   ramenée dans le fuseau du poste — une session ouverte à 23 h 30 UTC
 *   le 30/09 l'a été le 01/10 à Douala.
 *
 * @returns {Date|null} null si la valeur est illisible.
 */
export function parseServerDate(s) {
    if (!s) return null;
    const m = /^(\d{4})-(\d{2})-(\d{2})(?:[ T](\d{2}):(\d{2})(?::(\d{2}))?)?/.exec(s);
    let d;
    if (m && m[4] === undefined) {
        d = new Date(+m[1], +m[2] - 1, +m[3]);
    } else if (m) {
        d = new Date(Date.UTC(+m[1], +m[2] - 1, +m[3], +m[4], +m[5], +(m[6] || 0)));
    } else {
        d = new Date(s);
    }
    return isNaN(d.getTime()) ? null : d;
}

/** Date à afficher en JJ/MM/AAAA (voir :func:`parseServerDate`). */
export function fmtDate(s) {
    if (!s) return "";
    const d = parseServerDate(s);
    if (!d) return s;
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
 * Date LOCALE au format AAAA-MM-JJ (paramètres de période, champs
 * <input type="date">). ``toISOString()`` passe par UTC : à Douala
 * (UTC+1), le minuit local du 1er devenait le 30 du mois précédent et
 * « Ce mois » démarrait la veille (écart n° 38).
 */
export function localIsoDate(d) {
    const pad = (n) => (n < 10 ? "0" : "") + n;
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
}

/**
 * Jour LOCAL (AAAA-MM-JJ) d'une valeur date / date-heure lue sur le
 * serveur : chaîne, DateTime luxon ou Date. Le serveur filtre la période
 * sur des jours locaux : couper « 2026-10-22 23:30:00 » (UTC) à ses dix
 * premiers caractères donnait le 22/10 pour une session ouverte le 23/10
 * à 0 h 30 à Douala, et « Toute la période » la laissait dehors.
 */
export function toLocalDay(val) {
    if (!val) return null;
    if (typeof val === "string") {
        const d = parseServerDate(val);
        return d ? localIsoDate(d) : val.slice(0, 10);
    }
    if (typeof val.toFormat === "function") return val.toFormat("yyyy-MM-dd");
    if (val instanceof Date) return localIsoDate(val);
    return String(val).slice(0, 10);
}

/**
 * Génère la liste des périodes rapides. La période "Toute la période"
 * est calibrée sur la maquette LAVERANDAH (oct 2025 → mai 2026), mais
 * la première charge du dashboard remplace ces valeurs par les bornes
 * réelles trouvées dans pos.session.
 */
export function getQuickPeriods(today = new Date()) {
    const iso = localIsoDate;

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
    // « fa-cash-register » n'existe pas dans le Font Awesome 4.7 d'Odoo 18
    // (onglet sans icône) : calculatrice (écart n° 64).
    { key: "bycaisse",      label: "Par caisse",      icon: "fa-calculator" },
    { key: "sessions",      label: "Sessions POS",    icon: "fa-list" },
    { key: "products",      label: "Articles",        icon: "fa-cube" },
    { key: "margins",       label: "Marges & CMV",    icon: "fa-line-chart" },
    { key: "categories",    label: "Par catégorie",   icon: "fa-th-large" },
    { key: "discrepancies", label: "Écarts de caisse",icon: "fa-exclamation-triangle" },
    { key: "payments",      label: "Paiements",       icon: "fa-credit-card" },
];
