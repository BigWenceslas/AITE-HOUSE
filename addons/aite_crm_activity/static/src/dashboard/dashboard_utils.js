import { _t } from "@web/core/l10n/translation";
import { deserializeDate, formatDate } from "@web/core/l10n/dates";
import { formatFloat, formatMonetary } from "@web/views/fields/formatters";

/**
 * Outils partagés par le tableau de bord et ses composants (panneau
 * d'aperçu, tendances) : formats des dates, montants et taux, libellés
 * des échéances et des retards. Les textes passent tous par _t.
 */

export const DASHBOARD_MODEL = "aite.crm.activity.dashboard";

// Valeur du filtre « Commercial » pour ce qui n'est assigné à personne.
export const UNASSIGNED = "unassigned";

/** Date AAAA-MM-JJ du serveur → date affichée dans la langue de l'utilisateur. */
export function formatDay(value) {
    return value ? formatDate(deserializeDate(value)) : "";
}

/** Date AAAA-MM-JJ → jour et mois seulement (ex. « 05/11 »). */
export function formatShortDay(value) {
    return value ? deserializeDate(value).toLocaleString({ day: "2-digit", month: "2-digit" }) : "";
}

/** Montant arrondi à l'unité, dans la devise donnée (rien si nul). */
export function formatAmount(amount, currencyId) {
    if (!amount) {
        return "";
    }
    return formatMonetary(amount, { currencyId, digits: [69, 0] });
}

/** [{currency_id, amount}] → un texte par devise. */
export function formatAmounts(amounts) {
    return (amounts || [])
        .map((line) => formatAmount(line.amount, line.currency_id))
        .filter(Boolean);
}

/** Taux en % (0 à 100) ; « — » quand il n'y a rien à mesurer. */
export function formatRate(rate) {
    if (rate === null || rate === undefined || rate === false) {
        return "—";
    }
    return `${formatFloat(rate, { digits: [69, 1], trailingZeros: false })} %`;
}

/** Nombre de jours : « 1 j », « 12 j ». */
export function formatDays(days) {
    return _t("%s j", days);
}

/**
 * Libellé sous l'échéance d'une activité : « Aujourd'hui », « Demain »,
 * « 3 j de retard », « Dans 4 j », ou « Faite le … » pour une activité
 * réalisée.
 */
export function deadlineLabel(activity) {
    if (activity.state === "done") {
        return _t("Faite le %s", formatDay(activity.date_done));
    }
    if (activity.days === 0) {
        return _t("Aujourd'hui");
    }
    if (activity.days === 1) {
        return _t("Demain");
    }
    if (activity.days < 0) {
        return _t("%s j de retard", -activity.days);
    }
    return _t("Dans %s j", activity.days);
}

/**
 * Badge de gravité d'un retard (seuils réglés dans CRM → Configuration) :
 * « critique » et « élevé » ; rien pour un retard léger.
 */
export function severityBadge(level) {
    if (level === "critical") {
        return { label: _t("critique"), class: "text-bg-danger" };
    }
    if (level === "high") {
        return { label: _t("élevé"), class: "text-bg-warning" };
    }
    return null;
}
