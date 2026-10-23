/** @odoo-module **/
/*
 * Direction — Vue consolidée (LAVERANDAH).
 *
 * Un composant racine porte l'état (filtres globaux + données par
 * onglet, chargées à la demande) ; les sous-composants sont purs.
 * Défilement : pattern d'aite_pos_analytics — racine `.add-dashboard`
 * flex column plein cadre, corps `.add-dashboard-body` (flex 1,
 * overflow-y auto) qui défile sous les filtres et onglets fixes.
 */
import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

const DRILL_TAGS = {
    pos: "aite_pos_analytics.dashboard",
    credit: "aite_pos_credit_dashboard",
    stock: "aite_stock_dashboard",
    purchase: "aite_purchase_dashboard",
};
const CAISSE_COLORS = ["#714B67", "#185FA5", "#3B6D11", "#854F0B",
                       "#0F6E56", "#A32D2D"];
const TRANCHES = [
    { key: null, label: "Toute la journée" },
    { key: "matin", label: "Matin 6–12h" },
    { key: "am", label: "Après-midi 12–18h" },
    { key: "soir", label: "Soir 18–23h" },
    { key: "nuit", label: "Nuit 23–6h" },
];
const JOURS = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"];
const PERIODS = [
    { key: "all", label: "Toute la période" },
    { key: "today", label: "Aujourd'hui" },
    { key: "week", label: "Cette semaine" },
    { key: "month", label: "Ce mois" },
    { key: "quarter", label: "Ce trimestre" },
    { key: "year", label: "Cette année" },
];
const TABS = [
    { key: "vue", label: "Vue d'ensemble" },
    { key: "pos", label: "Ventes (POS)" },
    { key: "credit", label: "Crédit clients" },
    { key: "stock", label: "Stock" },
    { key: "achat", label: "Achats" },
    { key: "todo", label: "À traiter" },
];

function asList(x) {
    if (Array.isArray(x)) {
        return x;
    }
    if (x && Array.isArray(x.rows)) {
        return x.rows;
    }
    return [];
}
/*
 * Date LOCALE en AAAA-MM-JJ (borne de période envoyée au serveur).
 * ``toISOString()`` passe par l'UTC : à Douala (UTC+1), minuit le 1er
 * devenait le 30 du mois précédent — « Ce mois » démarrait la veille
 * (écart n° 38).
 */
export function localIsoDate(d) {
    const pad = (n) => (n < 10 ? "0" : "") + n;
    return d.getFullYear() + "-" + pad(d.getMonth() + 1) + "-"
        + pad(d.getDate());
}
export function rangeFor(key, today) {
    const t = new Date(today + "T00:00:00");
    const from = new Date(t);
    if (key === "today") {
        /* rien */
    } else if (key === "week") {
        const dow = (t.getDay() + 6) % 7;             // lundi = 0
        from.setDate(t.getDate() - dow);
    } else if (key === "month") {
        from.setDate(1);
    } else if (key === "quarter") {
        from.setMonth(Math.floor(t.getMonth() / 3) * 3, 1);
    } else if (key === "year") {
        from.setMonth(0, 1);
    } else {
        return ["2000-01-01", today];
    }
    return [localIsoDate(from), today];
}

/* ── formatage ─────────────────────────────────────────────────── */
/* Montant à la française : séparateur de milliers fr-FR (espace fine
   INSÉCABLE, comme les autres tableaux de bord — les espaces ordinaires
   coupaient un montant en fin de ligne). */
export function fmtMoney(v, symbol) {
    const s = Math.round(v || 0).toLocaleString("fr-FR");
    return symbol ? `${s} ${symbol}` : s;
}
/* Nombre entier à la française : « 1 234 » (« 1234 tickets » ici). */
export function fmtInt(v) {
    return Math.round(Number(v) || 0).toLocaleString("fr-FR");
}
/* Arrondi à une décimale ; « || 0 » évite un « -0,0 ». */
export function round1(v) {
    return Math.round((Number(v) || 0) * 10) / 10 || 0;
}
/* Pourcentages à la française : virgule, espace insécable avant %,
   décimales fixées (écart n° 41 — même rendu que l'exécutif). */
export function fmtPct(v, digits = 1) {
    return (v === null || v === undefined)
        ? "—" : `${(v).toFixed(digits).replace(".", ",")}\u00a0%`;
}
/* Variation : « ▲ +12,5 % », « ▼ 3,0 % », « ■ 0,0 % » — le rendu unique
   des tableaux de bord AITE (un écart nul s'écrivait « ▲ +0,0 % »). */
export function fmtDelta(v) {
    if (v === null || v === undefined) return "";
    const r = round1(v);
    const s = r > 0 ? "▲ +" : r < 0 ? "▼ " : "■ ";
    return s + Math.abs(r).toFixed(1).replace(".", ",") + "\u00a0%";
}
/* Classe d'une variation : vert si elle est bonne, rouge sinon, gris si
   elle s'affiche « 0,0 ». ``upIsBad`` pour un coût ou une dette (nouvelles
   ardoises) : une hausse est alors rouge, comme sur POS Crédit et
   l'analyse des ventes (relecture de l'écart n° 62). */
export function deltaClass(v, upIsBad = false) {
    const r = round1(v);
    if (!r) return "flat";
    return (r > 0) !== Boolean(upIsBad) ? "up" : "down";
}
/* Durée en jours, une décimale : « 12,3 j » (le délai moyen de
   remboursement s'affichait sans arrondi — écart n° 41). */
export function fmtDays(v) {
    return round1(v).toFixed(1).replace(".", ",") + " j";
}
/* Âge d'une ardoise en jours entiers : « 160 j », comme POS Crédit ; une
   moyenne de jours garde sa décimale (``fmtDays``). */
export function fmtAge(v) {
    return fmtInt(v) + " j";
}
/* Couverture de stock : « ∞ » à partir d'un an (une référence sans vente
   a une couverture infinie, 999 j pour le moteur Stock), sinon
   ``fmtDays`` — la règle de l'écran Stock & Inventaire. */
export function fmtCoverage(v) {
    return (Number(v) || 0) >= 365 ? "∞" : fmtDays(v);
}
/* « 2026-10-14 » → « 14/10/2026 » (règle 6, écart n° 37) ; un texte déjà
   formaté par le moteur passe tel quel. */
export function fmtDate(v) {
    const m = /^(\d{4})-(\d{2})-(\d{2})/.exec(v || "");
    return m ? `${m[3]}/${m[2]}/${m[1]}` : (v || "");
}
/* Nombre suivi du mot accordé : « 1 facture », « 4 factures » — en
   toutes lettres, sans « fact. » ni « réfs » (reprise de l'écart n° 42). */
export function fmtCount(n, one, many) {
    const k = Math.round(Number(n) || 0);
    return fmtInt(k) + " " + (Math.abs(k) > 1 ? many : one);
}
/* Fenêtre « à payer bientôt » : celle du réglage des Achats (``cfg.soon``,
   7 j par défaut) — le libellé restait à « 7 j » quand le montant suivait
   une fenêtre réglée à 14 j (reprise de l'écart n° 69). */
export function dueSoonLabel(soon) {
    return "À payer sous " + (soon || 7) + " j";
}
/* Tranche de la balance âgée clients : la clé rendue par le moteur
   Crédit (``get_aging``) fait foi. Le repli sur les bornes compare aux
   bornes du moteur (30 / 60 / 90) — comparées à 31 / 61 / 91, les
   couleurs glissaient d'une tranche (écart n° 70). */
export function agingKey(r) {
    if (["0_30", "31_60", "61_90", "90p"].includes(r.key)) {
        return r.key;
    }
    const lo = r.min || 0;
    if (lo >= 90 || r.max === null || r.max === undefined) {
        return "90p";
    }
    return lo >= 60 ? "61_90" : lo >= 30 ? "31_60" : "0_30";
}

/* ── sous-composants purs ──────────────────────────────────────── */
export class KpiCard extends Component {
    static template = "aite_direction_dashboard.KpiCard";
    static props = {
        label: String,
        value: String,
        sub: { type: String, optional: true },
        badge: { type: String, optional: true },     // 'per' | 'photo'
        accent: { type: String, optional: true },
        delta: { type: [Number, { value: null }], optional: true },
        deltaLabel: { type: String, optional: true },
        // Une hausse est une mauvaise nouvelle (coût, nouvelles ardoises).
        upIsBad: { type: Boolean, optional: true },
        mega: { type: Boolean, optional: true },
        onClick: { type: Function, optional: true },
        hint: { type: String, optional: true },   // phrase d'explication
    };
    get deltaText() {
        const t = fmtDelta(this.props.delta);
        return t && this.props.deltaLabel ? t + " " + this.props.deltaLabel : t;
    }
    get deltaCls() {
        return deltaClass(this.props.delta, this.props.upIsBad);
    }
}

export class HBar extends Component {
    static template = "aite_direction_dashboard.HBar";
    static props = {
        label: String, pct: Number, color: String,
        value: String, hint: { type: String, optional: true },
    };
    get width() {
        return Math.max(1, Math.min(100, this.props.pct));
    }
}

export class TrendChart extends Component {
    static template = "aite_direction_dashboard.TrendChart";
    static props = { rows: Array, currency: String };
    get maxBar() {
        let m = 0;
        for (const r of this.props.rows) {
            m = Math.max(m, r.ca || 0, r.bills || 0);
        }
        return m || 1;
    }
    get maxLine() {
        let m = 0;
        for (const r of this.props.rows) {
            m = Math.max(m, r.outstanding || 0);
        }
        return m || 1;
    }
    get bars() {
        const rows = this.props.rows;
        const n = rows.length || 1;
        const slot = 500 / n;
        return rows.map((r, i) => {
            const x0 = 45 + i * slot;
            const hCa = (r.ca / this.maxBar) * 160;
            const hBi = (r.bills / this.maxBar) * 160;
            return {
                period: r.period,
                xLabel: x0 + slot / 2,
                caX: x0 + slot / 2 - 24, caY: 180 - hCa, caH: hCa,
                biX: x0 + slot / 2 + 2, biY: 180 - hBi, biH: hBi,
            };
        });
    }
    get line() {
        const rows = this.props.rows;
        const n = rows.length || 1;
        const slot = 500 / n;
        return rows.map((r, i) => ({
            x: 45 + i * slot + slot / 2,
            y: 180 - (r.outstanding / this.maxLine) * 160,
        }));
    }
    get linePoints() {
        return this.line.map((p) => `${p.x},${p.y}`).join(" ");
    }
    get maxBarLabel() {
        return fmtMoney(this.maxBar, "");
    }
    get maxLineLabel() {
        return fmtMoney(this.maxLine, "");
    }
}

export class MirrorAging extends Component {
    static template = "aite_direction_dashboard.MirrorAging";
    static props = { clients: Object, suppliers: Object,
                     currency: String };
    // Libellés alignés sur ceux du moteur Crédit (get_aging) : le
    // miroir et l'onglet « Crédit clients » doivent nommer les mêmes
    // tranches de la même façon.
    static ORDER = [["0_30", "0–30 j"], ["31_60", "30–60 j"],
                    ["61_90", "60–90 j"], ["90p", "+90 j"]];
    static CLI = { "0_30": "#3B6D11", "31_60": "#854F0B",
                   "61_90": "#a3702a", "90p": "#A32D2D" };
    static SUP = { "0_30": "#185FA5", "31_60": "#5b83b0",
                   "61_90": "#8fa8c4", "90p": "#b9c9da" };
    get rows() {
        const cli = this.props.clients || {};
        const sup = this.props.suppliers || {};
        const maxC = Math.max(1, ...Object.values(cli));
        const maxS = Math.max(1, ...Object.values(sup));
        return MirrorAging.ORDER.map(([k, label]) => ({
            key: k, label,
            cAmount: fmtMoney(cli[k] || 0, ""),
            cPct: Math.max(2, ((cli[k] || 0) / maxC) * 100),
            cColor: MirrorAging.CLI[k],
            sAmount: fmtMoney(sup[k] || 0, ""),
            sPct: Math.max(2, ((sup[k] || 0) / maxS) * 100),
            sColor: MirrorAging.SUP[k],
        }));
    }
}

export class Heatmap extends Component {
    static template = "aite_direction_dashboard.Heatmap";
    static props = { rows: Array };
    static HOURS = [...Array(16).keys()].map((h) => h + 8);   // 8→23
    get hours() {
        return Heatmap.HOURS;
    }
    get grid() {
        const byKey = {};
        let max = 1;
        for (const r of asList(this.props.rows)) {
            byKey[`${r.weekday}-${r.hour}`] = r.ca;
            max = Math.max(max, r.ca);
        }
        return JOURS.map((label, i) => ({
            label,
            cells: Heatmap.HOURS.map((h) => {
                const v = byKey[`${i + 1}-${h}`] || 0;
                return { h, alpha: 0.06 + (v / max) * 0.9, v };
            }),
        }));
    }
}

/* ── racine ────────────────────────────────────────────────────── */
export class DirectionDashboard extends Component {
    static template = "aite_direction_dashboard.Dashboard";
    static components = { KpiCard, HBar, TrendChart, MirrorAging,
                          Heatmap };
    static props = { "*": true };

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.tabs = TABS;
        this.periods = PERIODS;
        this.tranches = TRANCHES;
        this.jours = JOURS;
        this.state = useState({
            tab: "vue",
            period: "month", from: "", to: "", custom: false,
            configId: null, tranche: null, days: [],
            creditSource: null, locationId: null, stockCategId: null,
            supplierId: null,
            meta: null, loading: true,
            data: { vue: null, pos: null, credit: null, stock: null,
                    achat: null, todo: null },
        });
        onWillStart(async () => {
            this.state.meta = await this.orm.call(
                "aite.direction.dashboard", "get_meta", []);
            const [f, t] = rangeFor("month", this.state.meta.today);
            this.state.from = f;
            this.state.to = t;
            await this.loadTab("vue", true);
            this.state.loading = false;
        });
    }

    /* — helpers d'affichage — */
    get cur() {
        return this.state.meta ? this.state.meta.currency.symbol : "";
    }
    money(v) {
        return fmtMoney(v, this.cur);
    }
    moneyShort(v) {
        return fmtMoney(v, "");
    }
    pct(v, d = 1) {
        return fmtPct(v, d);
    }
    days(v) {
        return fmtDays(v);
    }
    coverage(v) {
        return fmtCoverage(v);
    }
    age(v) {
        return fmtAge(v);
    }
    num(v) {
        return fmtInt(v);
    }
    date(v) {
        return fmtDate(v);
    }
    count(n, one, many) {
        return fmtCount(n, one, many);
    }
    soonDays(k) {
        return (k && k.cfg && k.cfg.soon) || 7;
    }
    soonLabel(k) {
        return dueSoonLabel(this.soonDays(k));
    }

    /* — dérivés pour les templates (pas de logique dans le XML) — */
    get netPositionSub() {
        const o = this.state.data.vue;
        if (!o) return "";
        const c = this.moneyShort(o.credit.outstanding);
        const s = this.moneyShort(o.purchase.encours);
        // Phrase servie par le serveur (``_net_position_text``, testée) :
        // ardoises > dettes = VOUS financez vos clients (écart n° 24).
        const who = o.net_side_text || "";
        return `${c} d'ardoises · ${s} de dettes — ${who}`;
    }
    /* — tuile Hébergement (présente si le PMS est installé) — */
    get hotelPaceSub() {
        const h = this.state.data.vue && this.state.data.vue.hotel;
        if (!h || !h.pace) return "";
        return fmtCount(h.nights_sold, "nuitée vendue", "nuitées vendues")
            + ` · rythme du mois (pace) : ${fmtInt(h.pace.nights)}`
            + ` (N-1 : ${fmtInt(h.pace.nights_ly)})`;
    }
    get hotelPickupSub() {
        const h = this.state.data.vue && this.state.data.vue.hotel;
        if (!h || !h.pickup) return "";
        return "réservations récentes (pickup) : "
            + fmtCount(h.pickup.nights, "nuitée prise", "nuitées prises")
            + ` ces ${h.pickup.window_days} j pour les `
            + `${h.pickup.horizon_days} prochains`;
    }
    hotelHint(key) {
        const h = this.state.data.vue && this.state.data.vue.hotel;
        return (h && h.hints && h.hints[key]) || "";
    }
    openExec() {
        const h = this.state.data.vue && this.state.data.vue.hotel;
        if (h && h.exec_action) {
            this.action.doAction(h.exec_action);
        }
    }
    get qtyPerTicket() {
        const k = this.state.data.pos && this.state.data.pos.kpis;
        if (!k || !k.order_count) return "0";
        return (k.qty / k.order_count).toFixed(1).replace(".", ",");
    }
    get posQty() {
        const k = this.state.data.pos && this.state.data.pos.kpis;
        return fmtInt(k ? k.qty : 0);
    }
    get caisseLabel() {
        if (!this.state.configId) return "toutes les caisses";
        const c = this.configs.find((x) => x.id === this.state.configId);
        return c ? c.name : "—";
    }
    static PALETTE = ["#714B67", "#185FA5", "#3B6D11", "#854F0B",
                      "#0F6E56", "#A32D2D", "#5b83b0", "#a3702a"];
    _colored(rows, valueKey) {
        rows = asList(rows);
        const total = rows.reduce((s, r) => s + (r[valueKey] || 0), 0)
            || 1;
        const P = DirectionDashboard.PALETTE;
        return rows.map((r, i) => ({
            ...r,
            pct: ((r[valueKey] || 0) / total) * 100,
            color: P[i % P.length],
        }));
    }
    get posCategories() {
        const d = this.state.data.pos;
        if (!d) return [];
        const rows = asList(d.categories).map((r) => ({
            name: r.cat_name || r.name || "(sans catégorie)",
            ca: r.ca || r.price_subtotal || 0,
        })).sort((a, b) => b.ca - a.ca).slice(0, 6);
        return this._colored(rows, "ca");
    }
    get posPayments() {
        const d = this.state.data.pos;
        if (!d) return [];
        const rows = asList(d.payments).map((r) => ({
            name: r.method_name || "—",
            amount: r.amount || 0,
            pct: r.pct || 0,
        }));
        const P = DirectionDashboard.PALETTE;
        return rows.map((r, i) => ({ ...r, color: P[i % P.length] }));
    }
    static AGING_COLORS = { "0_30": "#3B6D11", "31_60": "#854F0B",
                            "61_90": "#a3702a", "90p": "#A32D2D" };
    get creditAging() {
        const d = this.state.data.credit;
        if (!d) return [];
        const rows = asList(d.aging);
        const max = Math.max(1, ...rows.map((r) => r.amount || 0));
        return rows.map((r) => ({
            label: r.label,
            amount: r.amount || 0,
            count: r.count || 0,
            pct: Math.max(2, ((r.amount || 0) / max) * 100),
            color: DirectionDashboard.AGING_COLORS[agingKey(r)],
        }));
    }
    get creditLinePoints() {
        const d = this.state.data.credit;
        const rows = asList(d && d.evolution);
        if (!rows.length) return "";
        const max = Math.max(1, ...rows.map((r) => r.outstanding || 0));
        const slot = 490 / rows.length;
        return rows.map((r, i) => {
            const x = 15 + i * slot + slot / 2;
            const y = 105 - ((r.outstanding || 0) / max) * 90;
            return `${x},${y}`;
        }).join(" ");
    }
    get creditLineLegend() {
        const d = this.state.data.credit;
        const rows = asList(d && d.evolution);
        if (!rows.length) return "";
        const last = rows[rows.length - 1];
        return `${rows[0].period} → ${last.period} · dernier point : `
            + this.money(last.outstanding);
    }
    get netFlowText() {
        const d = this.state.data.credit;
        if (!d) return "";
        // Signe seulement pour un flux non nul : ni « +0 » ni « −0 »
        // (même règle que les cartes Achats, écarts n° 6 et 69).
        const v = Math.round(d.kpis.net_flow || 0);
        return (v > 0 ? "+" : v < 0 ? "−" : "") + this.money(Math.abs(v));
    }
    get stockByCat() {
        const d = this.state.data.stock;
        if (!d) return [];
        const rows = asList(d.by_category).slice(0, 6);
        return this._colored(rows, "value");
    }
    /* « 1 unité », « 1 234 unités » (accord et séparateur français). */
    get stockUnits() {
        const d = this.state.data.stock;
        return fmtCount(d ? d.kpis.total_units : 0, "unité", "unités");
    }
    get stockCoverage() {
        const d = this.state.data.stock;
        if (!d) return [];
        const rows = asList(d.coverage).map((r) => ({
            name: r.name || "—",
            couv: r.couv !== undefined ? r.couv : (r.value || 0),
        })).slice(0, 6);
        const max = Math.max(1, ...rows.map((r) => r.couv));
        const P = DirectionDashboard.PALETTE;
        return rows.map((r, i) => ({
            ...r,
            pct: Math.max(2, (r.couv / max) * 100),
            color: P[i % P.length],
            text: fmtCoverage(r.couv),
        }));
    }
    penaltyText(r) {
        return r.loss_day
            ? `≈ ${this.money(r.loss_day)} / j`
            : this.money(r.value);
    }
    get supplierChips() {
        const s = (this.state.meta && this.state.meta.suppliers) || [];
        return s.slice(0, 4);
    }
    // Mêmes tranches que ``_bucket_supplier_invoices`` (jours avant
    // l'échéance : 0–7, 8–14, 15–21, 22 et plus), dites en toutes lettres
    // (« S + 1 » — reprise de l'écart n° 42). « Sous 7 jours » couvre
    // exactement la carte « À payer sous 7 j » (réglage par défaut).
    static SCHED = [["overdue", "Échues", "#A32D2D"],
                    ["w0", "Sous 7 jours", "#A32D2D"],
                    ["w1", "Dans 8 à 14 jours", "#854F0B"],
                    ["w2", "Dans 15 à 21 jours", "#185FA5"],
                    ["w3p", "Dans 22 jours et +", "#8fa8c4"]];
    get purchaseSchedule() {
        const d = this.state.data.achat;
        if (!d) return [];
        const sched = d.buckets.schedule || {};
        const counts = d.buckets.schedule_counts || {};
        const max = Math.max(1, ...Object.values(sched));
        return DirectionDashboard.SCHED.map(([k, label, color]) => ({
            key: k, label, color,
            amount: sched[k] || 0,
            count: counts[k] || 0,
            pct: Math.max(2, ((sched[k] || 0) / max) * 100),
        }));
    }
    get priceUp() {
        const d = this.state.data.achat;
        if (!d) return [];
        return asList(d.price_moves)
            .filter((m) => (m.p1 || 0) > (m.p0 || 0))
            .map((m) => ({
                name: m.name,
                partner: m.partner || "",
                // une décimale, comme la colonne du tableau Achats
                deltaText: "+" + fmtPct(((m.p1 || 0) / (m.p0 || 1) - 1)
                    * 100),
            }));
    }
    get priceUpCount() {
        return fmtCount(this.priceUp.length, "référence", "références");
    }
    get dpoText() {
        // Même rendu que le tableau de bord Achats (« 23,0 j »).
        const d = this.state.data.achat;
        return fmtDays(d ? d.kpis.dpo : 0);
    }
    get configs() {
        return (this.state.meta ? this.state.meta.configs : []).map(
            (c, i) => ({ ...c,
                         color: CAISSE_COLORS[i % CAISSE_COLORS.length] }));
    }
    get weekdays() {
        return this.state.days.length
            ? this.state.days.map((i) => i + 1) : null;
    }
    get badges() {
        const o = this.state.data.vue;
        const todo = this.state.data.todo;
        return {
            credit: o ? o.badges.credit : 0,
            stock: o ? o.badges.stock : 0,
            achat: o ? o.badges.purchase : 0,
            todo: todo ? todo.count : null,
        };
    }

    /* — chargement — */
    async loadTab(tab, force = false) {
        if (this.state.data[tab] && !force) {
            return;
        }
        const s = this.state;
        const args = [s.from, s.to];
        const M = "aite.direction.dashboard";
        if (tab === "vue") {
            s.data.vue = await this.orm.call(M, "get_overview",
                [...args, s.configId, s.tranche, this.weekdays]);
        } else if (tab === "pos") {
            s.data.pos = await this.orm.call(M, "get_pos_tab",
                [...args, s.configId, s.tranche, this.weekdays]);
        } else if (tab === "credit") {
            s.data.credit = await this.orm.call(M, "get_credit_tab",
                [...args, s.configId, s.creditSource]);
        } else if (tab === "stock") {
            s.data.stock = await this.orm.call(M, "get_stock_tab",
                [...args, s.locationId, s.stockCategId]);
        } else if (tab === "achat") {
            s.data.achat = await this.orm.call(M, "get_purchase_tab",
                [...args, s.supplierId]);
        } else if (tab === "todo") {
            s.data.todo = await this.orm.call(M, "get_actions",
                [...args, s.configId]);
        }
    }
    async refresh(tabsToClear) {
        for (const t of tabsToClear) {
            this.state.data[t] = null;
        }
        await this.loadTab(this.state.tab, true);
        if (this.state.tab !== "vue" && tabsToClear.includes("vue")) {
            await this.loadTab("vue", true);
        }
    }

    /* — interactions — */
    async setTab(tab) {
        this.state.tab = tab;
        await this.loadTab(tab);
    }
    async setPeriod(key) {
        this.state.period = key;
        this.state.custom = false;
        const [f, t] = rangeFor(key, this.state.meta.today);
        this.state.from = f;
        this.state.to = t;
        await this.refresh(["vue", "pos", "credit", "stock", "achat",
                            "todo"]);
    }
    async applyCustom(ev) {
        const root = ev.target.closest(".add-filters");
        const f = root.querySelector(".add-date-from").value;
        const t = root.querySelector(".add-date-to").value;
        if (!f || !t || f > t) {
            return;
        }
        this.state.period = null;
        this.state.custom = true;
        this.state.from = f;
        this.state.to = t;
        await this.refresh(["vue", "pos", "credit", "stock", "achat",
                            "todo"]);
    }
    async setCaisse(id) {
        this.state.configId = id;
        await this.refresh(["vue", "pos", "credit", "todo"]);
    }
    async setTranche(key) {
        this.state.tranche = key;
        await this.refresh(["vue", "pos"]);
    }
    async togJour(i) {
        const d = this.state.days;
        const at = d.indexOf(i);
        if (at >= 0) {
            d.splice(at, 1);
        } else {
            d.push(i);
        }
        await this.refresh(["vue", "pos"]);
    }
    async setCreditSource(src) {
        this.state.creditSource = src;
        await this.refresh(["credit"]);
    }
    async setLocation(id) {
        this.state.locationId = id;
        await this.refresh(["stock"]);
    }
    async setStockCateg(id) {
        this.state.stockCategId = id;
        await this.refresh(["stock"]);
    }
    async setSupplier(id) {
        this.state.supplierId = id;
        await this.refresh(["achat"]);
    }
    drill(key) {
        this.action.doAction({
            type: "ir.actions.client",
            tag: DRILL_TAGS[key],
            name: "Tableau de bord",
        });
    }
}

registry.category("actions").add("aite_direction_dashboard.dashboard",
                                 DirectionDashboard);
