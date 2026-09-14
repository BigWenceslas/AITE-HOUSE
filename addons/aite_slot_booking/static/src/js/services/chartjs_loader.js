/** @odoo-module **/

import { loadJS } from "@web/core/assets";

/**
 * Charge Chart.js depuis la lib bundlée d'Odoo.
 *
 * Le chemin ``/web/static/lib/Chart/Chart.js`` est disponible nativement
 * dans Odoo (utilisé par les vues graph). On évite ainsi tout CDN externe
 * et le module fonctionne en environnement déconnecté.
 *
 * La fonction garantit qu'un seul chargement est effectué, même si
 * plusieurs composants en font la demande en parallèle.
 */

let chartLoadPromise = null;

export async function loadChart() {
    if (typeof window.Chart !== "undefined") {
        return window.Chart;
    }
    if (!chartLoadPromise) {
        chartLoadPromise = loadJS("/web/static/lib/Chart/Chart.js");
    }
    await chartLoadPromise;
    return window.Chart;
}

/**
 * Détruit proprement une instance Chart.js.
 * Sécurisé contre les références nulles.
 */
export function destroyChart(chart) {
    if (chart && typeof chart.destroy === "function") {
        try { chart.destroy(); } catch (e) { /* swallow */ }
    }
}
