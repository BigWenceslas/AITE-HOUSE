import {
    Component,
    onMounted,
    onPatched,
    onWillStart,
    onWillUnmount,
    useRef,
    useState,
} from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";
import { deserializeDate, serializeDate } from "@web/core/l10n/dates";
import { RPCError } from "@web/core/network/rpc";
import { Dropdown } from "@web/core/dropdown/dropdown";
import { DropdownItem } from "@web/core/dropdown/dropdown_item";
import { useSetupAction } from "@web/search/action_hook";
import { standardActionServiceProps } from "@web/webclient/actions/action_service";
import {
    AiteActivityDateDialog,
    AiteActivityDoneDialog,
    AiteActivityReassignDialog,
} from "./activity_dialogs";
import {
    DASHBOARD_MODEL,
    UNASSIGNED,
    deadlineLabel,
    formatAmount,
    formatAmounts,
    formatDay,
    formatDays,
    formatRate,
    formatShortDay,
    severityBadge,
} from "./dashboard_utils";
import { AiteLeadPanel } from "./lead_panel";
import { AiteTrendChart } from "./trend_chart";

// Onglets, dans l'ordre d'affichage.
const TABS = ["todo", "team", "trends"];
// Filtres acceptés depuis un lien direct (paramètres de l'action) ; le
// serveur les valide de toute façon.
const FILTER_KEYS = ["user_id", "team_id", "activity_type_id", "bucket", "period", "date_from", "date_to"];
// Filtres suivis par les tendances (la période et la sélection n'y jouent pas).
const TREND_FILTER_KEYS = ["user_id", "team_id", "activity_type_id"];
// Niveaux de couleur du plan de charge (classes o_aite_cad_heat_1 … 4).
const HEAT_LEVELS = 4;
// Dates « Du / au » de la période personnalisée : Chrome signale un
// changement à chaque chiffre tapé au clavier (l'année passe par 0002,
// 0020, 0202…). Une date n'est envoyée au serveur que complète (année
// 1900 ou plus, comme le serveur), et après une courte pause de saisie,
// à la sortie du champ ou sur Entrée.
const CUSTOM_DATE_DELAY = 700;
const CUSTOM_DATE_MIN_YEAR = 1900;

function isCompleteDate(value) {
    const match = /^(\d{4})-\d{2}-\d{2}$/.exec(value || "");
    return Boolean(match) && parseInt(match[1]) >= CUSTOM_DATE_MIN_YEAR;
}

let nextInstanceId = 0;

function pickFilters(params) {
    const filters = {};
    for (const key of FILTER_KEYS) {
        if (params && params[key] !== undefined && params[key] !== null) {
            filters[key] = params[key];
        }
    }
    return filters;
}

/**
 * CRM → Suivi des activités.
 *
 * Toutes les données viennent de aite.crm.activity.dashboard, calculées
 * côté serveur avec les droits de l'utilisateur :
 *
 * - get_dashboard_data : un seul appel pour les indicateurs, les alertes,
 *   les listes, le tableau par commercial et le plan de charge ;
 * - get_trend_data : chargé seulement quand l'onglet « Tendances » est
 *   affiché, puis gardé tant que les filtres qui le concernent ne changent
 *   pas ;
 * - get_lead_preview : le panneau d'aperçu d'une opportunité.
 *
 * Chaque appel a son propre garde-fou : seule la réponse à la dernière
 * demande est affichée. Les actions (fait, reporter, réassigner) passent
 * par les méthodes action_* du même modèle, puis le tableau est rechargé.
 *
 * Les filtres (période comprise) et l'onglet sont gardés quand on revient
 * par le fil d'Ariane ; un lien direct (action « Activités en retard »)
 * fournit les filtres de départ dans ses paramètres.
 */
export class AiteCrmActivityDashboard extends Component {
    static template = "aite_crm_activity.Dashboard";
    static components = { Dropdown, DropdownItem, AiteLeadPanel, AiteTrendChart };
    static props = { ...standardActionServiceProps };

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.dialog = useService("dialog");
        this.notification = useService("notification");
        this.UNASSIGNED = UNASSIGNED;
        this.uid = `o_aite_cad_${++nextInstanceId}`;
        this.rootRef = useRef("root");

        const restored = this.props.state || {};
        const params = this.props.action?.params || {};
        let tab = "todo";
        if (TABS.includes(restored.tab)) {
            tab = restored.tab;
        } else if (!restored.filters && TABS.includes(params.tab)) {
            tab = params.tab;
        }
        this.state = useState({
            data: null,
            filters: restored.filters ? { ...restored.filters } : pickFilters(params),
            tab,
            loading: true,
            busyIds: {},
            trend: null,
            trendLoading: false,
            trendError: false,
            // Aperçu ouvert : { leadId, refreshKey }.
            preview: null,
        });
        this.lastRequest = 0;
        this.lastTrendRequest = 0;
        this.trendStale = true;
        // Après le prochain rendu : élément à faire défiler / onglet à focaliser.
        this.pendingScroll = null;
        this.pendingFocus = null;
        this.previewOpener = null;
        // Dates personnalisées saisies, pas encore envoyées.
        this.pendingDates = {};
        this.customDateTimer = null;

        useSetupAction({
            rootRef: this.rootRef,
            getLocalState: () => ({ filters: { ...this.state.filters }, tab: this.state.tab }),
        });
        onWillStart(() => this.load());
        onMounted(() => this.afterRender());
        onPatched(() => this.afterRender());
        onWillUnmount(() => clearTimeout(this.customDateTimer));
    }

    // ------------------------------------------------------------------
    // Chargement
    // ------------------------------------------------------------------

    /**
     * Recharge le tableau avec les filtres modifiés. Les filtres sont
     * appliqués tout de suite (deux changements rapprochés se cumulent) et
     * seule la réponse à la dernière demande est affichée. Les tendances
     * sont rechargées si elles sont affichées et concernées.
     *
     * Si la dernière demande échoue (erreur du serveur, connexion perdue,
     * proxy en 502/504), les filtres reviennent à ceux des chiffres
     * affichés : jamais de nouveaux filtres au-dessus d'anciens chiffres.
     * Odoo affiche l'erreur (l'exception est relancée).
     */
    async load(changes = {}) {
        const filters = { ...this.state.filters, ...changes };
        this.state.filters = filters;
        const trendPromise = this.refreshTrends(changes);
        const request = ++this.lastRequest;
        this.state.loading = true;
        try {
            const data = await this.orm.call(DASHBOARD_MODEL, "get_dashboard_data", [], {
                filters,
            });
            if (request === this.lastRequest) {
                this.state.data = data;
                this.state.filters = { ...data.filters };
            }
        } catch (error) {
            if (request === this.lastRequest && this.state.data) {
                this.state.filters = { ...this.state.data.filters };
                // Tendances : à recharger avec ces filtres-là.
                this.trendStale = true;
                if (this.state.tab === "trends") {
                    this.loadTrends();
                }
            }
            throw error;
        } finally {
            if (request === this.lastRequest) {
                this.state.loading = false;
            }
        }
        await trendPromise;
    }

    /** Recharge complète (bouton « Actualiser », après une action). */
    async reload() {
        await this.load();
        if (this.state.preview) {
            this.state.preview.refreshKey++;
        }
    }

    /**
     * Les tendances ne dépendent que du commercial, de l'équipe et du
     * type : un changement de période ou de sélection ne les recharge pas.
     */
    refreshTrends(changes) {
        const keys = Object.keys(changes);
        if (keys.length && !keys.some((key) => TREND_FILTER_KEYS.includes(key))) {
            return null;
        }
        this.trendStale = true;
        return this.state.tab === "trends" ? this.loadTrends() : null;
    }

    async loadTrends() {
        const request = ++this.lastTrendRequest;
        this.trendStale = false;
        this.state.trendLoading = true;
        this.state.trendError = false;
        try {
            const trend = await this.orm.call(DASHBOARD_MODEL, "get_trend_data", [], {
                filters: this.state.filters,
            });
            if (request === this.lastTrendRequest) {
                this.state.trend = trend;
            }
        } catch (error) {
            if (request !== this.lastTrendRequest) {
                return;
            }
            this.trendStale = true;
            // Message dans l'onglet, avec « Réessayer », quelle que soit
            // l'erreur (connexion perdue comprise, qu'Odoo signale aussi).
            const message = error instanceof RPCError ? error.data?.message : null;
            this.state.trendError = message || _t("Les tendances n'ont pas pu être chargées.");
            if (!(error instanceof RPCError)) {
                throw error;
            }
        } finally {
            if (request === this.lastTrendRequest) {
                this.state.trendLoading = false;
            }
        }
    }

    get data() {
        return this.state.data;
    }

    // ------------------------------------------------------------------
    // Onglets
    // ------------------------------------------------------------------

    get tabs() {
        return [
            { key: "todo", label: _t("À traiter"), icon: "fa-list-ul" },
            { key: "team", label: _t("Équipe"), icon: "fa-users" },
            { key: "trends", label: _t("Tendances"), icon: "fa-line-chart" },
        ];
    }

    tabId(key) {
        return `${this.uid}_tab_${key}`;
    }

    tabPanelId(key) {
        return `${this.uid}_tabpanel_${key}`;
    }

    selectTab(tab) {
        if (this.state.tab === tab) {
            return;
        }
        this.state.tab = tab;
        if (tab === "trends" && (this.trendStale || !this.state.trend)) {
            this.loadTrends();
        }
    }

    /** Flèches, Début et Fin dans la barre d'onglets (modèle ARIA). */
    onTabKeydown(ev) {
        const index = TABS.indexOf(this.state.tab);
        const moves = {
            ArrowRight: (index + 1) % TABS.length,
            ArrowLeft: (index - 1 + TABS.length) % TABS.length,
            Home: 0,
            End: TABS.length - 1,
        };
        if (!(ev.key in moves)) {
            return;
        }
        ev.preventDefault();
        const tab = TABS[moves[ev.key]];
        this.selectTab(tab);
        this.pendingFocus = `#${this.tabId(tab)}`;
        this.afterRender();
    }

    /** Défilement ou focus demandés avant le rendu, une fois l'élément affiché. */
    afterRender() {
        const root = this.rootRef.el;
        if (!root) {
            return;
        }
        if (this.pendingFocus) {
            const el = root.querySelector(this.pendingFocus);
            if (el) {
                el.focus();
                this.pendingFocus = null;
            }
        }
        if (this.pendingScroll) {
            const el = root.querySelector(this.pendingScroll);
            if (el) {
                el.scrollIntoView({ behavior: "smooth", block: "start" });
                this.pendingScroll = null;
            }
        }
    }

    scrollTo(selector) {
        this.pendingScroll = selector;
        this.afterRender();
    }

    // ------------------------------------------------------------------
    // Indicateurs et alertes
    // ------------------------------------------------------------------

    get kpiCards() {
        const { kpis, period } = this.data;
        const overdue = {
            key: "overdue",
            label: _t("En retard"),
            value: kpis.overdue,
            tone: "danger",
            icon: "fa-exclamation-circle",
            lines: [],
            chips: [],
        };
        if (kpis.critical) {
            overdue.lines.push({
                text: kpis.critical === 1 ? _t("dont 1 critique") : _t("dont %s critiques", kpis.critical),
                class: "text-danger fw-semibold",
            });
        } else if (kpis.high) {
            overdue.lines.push({
                text: kpis.high === 1 ? _t("dont 1 élevé") : _t("dont %s élevés", kpis.high),
                class: "o_aite_cad_text_warning fw-semibold",
            });
        }
        if (kpis.overdue_leads) {
            overdue.lines.push({
                text:
                    kpis.overdue_leads === 1
                        ? _t("sur 1 opportunité")
                        : _t("sur %s opportunités", kpis.overdue_leads),
                class: "text-muted",
            });
        }
        overdue.chips = this.amountChips(kpis.overdue_amounts);

        const done = {
            key: "done",
            label: _t("Réalisées · %s", period.label),
            value: kpis.done,
            tone: "success",
            icon: "fa-check-circle",
            lines: [this.deltaLine(kpis.done_delta, kpis.done_prev)],
            chips: [],
        };
        if (kpis.on_time_rate !== null && kpis.on_time_rate !== undefined) {
            done.lines.push({
                text: _t("%s à temps", formatRate(kpis.on_time_rate)),
                class: "text-muted",
                title: _t("Activités réalisées au plus tard le jour de leur échéance"),
            });
        }

        const stalled = {
            key: "stalled",
            label: _t("Opportunités sans activité"),
            value: kpis.stalled,
            tone: "body",
            icon: "fa-pause-circle",
            lines: [],
            chips: this.amountChips(kpis.stalled_amounts),
        };
        if (this.data.stalled.dormant) {
            const count = this.data.stalled.dormant;
            stalled.lines.push({
                text: count === 1 ? _t("dont 1 dormante") : _t("dont %s dormantes", count),
                class: "o_aite_cad_text_warning fw-semibold",
                title: _t("Sans action depuis %s ou plus", formatDays(this.data.thresholds.dormant_days)),
            });
        }
        if (this.data.filter_notes.stalled_ignores_type) {
            stalled.lines.push({
                text: _t("Le filtre Type ne s'applique pas ici"),
                class: "text-muted fst-italic",
                icon: "fa-info-circle",
            });
        }

        return [
            overdue,
            {
                key: "today",
                label: _t("Aujourd'hui"),
                value: kpis.today,
                tone: "warning",
                icon: "fa-calendar-check-o",
                lines: [],
                chips: [],
            },
            {
                key: "upcoming",
                label: _t("À venir (%s j)", this.data.upcoming_days),
                value: kpis.upcoming,
                tone: "info",
                icon: "fa-calendar",
                lines: [],
                chips: [],
            },
            done,
            stalled,
        ];
    }

    amountChips(amounts) {
        return formatAmounts(amounts).map((text) => ({
            text,
            title: _t("Montant attendu des opportunités concernées"),
        }));
    }

    /**
     * Évolution des activités réalisées par rapport à la période précédente
     * de même durée (plus, c'est mieux : hausse en vert).
     */
    deltaLine(delta, previous) {
        const { prev_from, prev_to } = this.data.period;
        const range = _t("%(from)s – %(to)s", {
            from: formatShortDay(prev_from),
            to: formatShortDay(prev_to),
        });
        const title = _t("Période précédente : du %(from)s au %(to)s, %(count)s réalisées", {
            from: formatDay(prev_from),
            to: formatDay(prev_to),
            count: previous,
        });
        if (delta === null || delta === undefined) {
            return { text: _t("aucune sur la période précédente"), class: "text-muted", title };
        }
        const value = formatRate(Math.abs(delta));
        if (delta > 0) {
            return { text: _t("▲ +%(value)s vs %(range)s", { value, range }), class: "text-success fw-semibold", title };
        }
        if (delta < 0) {
            return { text: _t("▼ −%(value)s vs %(range)s", { value, range }), class: "text-danger fw-semibold", title };
        }
        return { text: _t("= stable vs %s", range), class: "text-muted", title };
    }

    onKpiClick(card) {
        if (card.key === "stalled") {
            this.focusStalled();
            return;
        }
        this.state.tab = "todo";
        this.load({ bucket: card.key });
    }

    focusStalled() {
        this.state.tab = "todo";
        this.scrollTo(".o_aite_cad_stalled");
    }

    applyAlert(alert) {
        const action = alert.action || {};
        if (action.bucket) {
            this.state.tab = "todo";
            this.load({ bucket: action.bucket });
            this.scrollTo(".o_aite_cad_activities_card");
        } else if (action.focus === "stalled") {
            this.focusStalled();
        }
    }

    alertButtonLabel(alert) {
        if (alert.action?.focus === "stalled") {
            return _t("Voir les opportunités");
        }
        return _t("Voir les activités");
    }

    // ------------------------------------------------------------------
    // Filtres
    // ------------------------------------------------------------------

    get bucketTabs() {
        const k = this.data.kpis;
        return [
            { key: "all", label: _t("En cours"), count: k.open },
            { key: "overdue", label: _t("En retard"), count: k.overdue },
            { key: "today", label: _t("Aujourd'hui"), count: k.today },
            { key: "upcoming", label: _t("À venir"), count: k.upcoming },
            { key: "done", label: _t("Réalisées"), count: k.done },
        ];
    }

    onFilterChange(key, ev) {
        const value = ev.target.value;
        let parsed = false;
        if (value === UNASSIGNED) {
            parsed = UNASSIGNED;
        } else if (value) {
            parsed = parseInt(value);
        }
        this.load({ [key]: parsed });
    }

    /**
     * Période des activités réalisées. « Personnalisée » part de la période
     * affichée, que l'on ajuste ensuite avec les deux dates.
     */
    onPeriodChange(ev) {
        const period = ev.target.value;
        if (period === "custom") {
            this.load({
                period,
                date_from: this.data.period.date_from,
                date_to: this.data.period.date_to,
            });
        } else {
            this.load({ period });
        }
    }

    /** Saisie d'une date « Du » ou « au » : gardée en attente, puis
     * envoyée après une pause (voir CUSTOM_DATE_DELAY). Une date
     * incomplète n'est jamais envoyée. */
    onCustomDateChange(key, ev) {
        clearTimeout(this.customDateTimer);
        this.customDateTimer = null;
        if (isCompleteDate(ev.target.value)) {
            this.pendingDates[key] = ev.target.value;
        } else {
            delete this.pendingDates[key];
        }
        if (Object.keys(this.pendingDates).length) {
            this.customDateTimer = setTimeout(() => this.commitCustomDates(), CUSTOM_DATE_DELAY);
        }
    }

    /** Sortie du champ ou touche Entrée : envoi immédiat. Une date restée
     * incomplète à la sortie du champ est remplacée par celle en vigueur. */
    onCustomDateCommit(key, ev) {
        if (ev.type === "keydown" && ev.key !== "Enter") {
            return;
        }
        this.commitCustomDates();
        if (ev.type === "blur") {
            // Après coup : Chrome valide la saisie en cours après « blur ».
            const input = ev.target;
            setTimeout(() => {
                if (document.activeElement !== input && !isCompleteDate(input.value)) {
                    input.value = this.state.filters[key] || "";
                }
            });
        }
    }

    commitCustomDates() {
        clearTimeout(this.customDateTimer);
        this.customDateTimer = null;
        const changes = this.pendingDates;
        this.pendingDates = {};
        const changed = Object.entries(changes).some(
            ([key, value]) => this.state.filters[key] !== value
        );
        if (changed && this.state.filters.period === "custom") {
            this.load({ period: "custom", ...changes });
        }
    }

    selectBucket(bucket) {
        this.load({ bucket });
    }

    /** Clic sur un nom « Par commercial » : filtre sur lui, ou retire le
     * filtre si la ligne était déjà sélectionnée. */
    filterOnUser(userId) {
        this.load({ user_id: this.state.filters.user_id === userId ? false : userId });
    }

    /**
     * Clic sur un nombre de l'onglet « Équipe » : ce commercial et cette
     * sélection dans « À traiter » (« sans activité » : la liste des
     * opportunités sans activité).
     */
    async drill(userId, bucket) {
        this.state.tab = "todo";
        // Défilement après l'affichage des nouvelles données (la liste
        // change de hauteur).
        if (bucket === "stalled") {
            await this.load({ user_id: userId });
            this.pendingScroll = ".o_aite_cad_stalled";
        } else {
            await this.load({ user_id: userId, bucket });
            this.pendingScroll = ".o_aite_cad_activities_card";
        }
    }

    /** Case du plan de charge : ``dayIndex`` null pour la colonne « Retard ». */
    drillWorkload(row, dayIndex) {
        let bucket = "upcoming";
        if (dayIndex === null) {
            bucket = "overdue";
        } else if (dayIndex === 0) {
            bucket = "today";
        }
        return this.drill(row.user_id, bucket);
    }

    // ------------------------------------------------------------------
    // Équipe
    // ------------------------------------------------------------------

    get busiestOpen() {
        return Math.max(1, ...this.data.by_user.rows.map((row) => row.open));
    }

    /** Barre empilée d'une ligne : largeur relative au commercial le plus chargé. */
    loadBar(row) {
        const open = row.open || 0;
        const part = (value) => (open ? (value * 100) / open : 0);
        return {
            width: (open * 100) / this.busiestOpen,
            overdue: part(row.overdue),
            today: part(row.today),
            upcoming: part(row.upcoming),
            label: _t("%(overdue)s en retard, %(today)s aujourd'hui, %(upcoming)s à venir", {
                overdue: row.overdue,
                today: row.today,
                upcoming: row.upcoming,
            }),
        };
    }

    get teamColumns() {
        return [
            { key: "overdue", label: _t("Retard"), title: _t("En retard") },
            { key: "today", label: _t("Jour"), title: _t("Aujourd'hui") },
            { key: "upcoming", label: _t("À venir"), title: _t("À venir") },
            { key: "done", label: _t("Faites"), title: _t("Réalisées sur la période") },
            { key: "stalled", label: _t("Sans act."), title: _t("Opportunités sans activité") },
        ];
    }

    drillTitle(row, column) {
        return _t("%(name)s : voir « %(column)s »", { name: row.name, column: column.title });
    }

    heatClass(count) {
        const max = this.data.workload.max;
        if (!count || !max) {
            return "";
        }
        const level = Math.min(HEAT_LEVELS, Math.max(1, Math.ceil((count * HEAT_LEVELS) / max)));
        return `o_aite_cad_heat_${level}`;
    }

    get workloadTotals() {
        const { days, rows } = this.data.workload;
        return {
            overdue: rows.reduce((sum, row) => sum + row.overdue, 0),
            cells: days.map((day, index) => rows.reduce((sum, row) => sum + row.cells[index], 0)),
            total: rows.reduce((sum, row) => sum + row.total, 0),
        };
    }

    workloadDayTitle(day) {
        return day.is_today ? _t("Aujourd'hui") : formatDay(day.date);
    }

    workloadOverdueTitle(row) {
        return _t("%(name)s : %(count)s en retard", { name: row.name, count: row.overdue });
    }

    userFilterTitle(selected) {
        return selected
            ? _t("Retirer le filtre sur ce commercial")
            : _t("Filtrer le tableau de bord sur ce commercial");
    }

    get dormantTitle() {
        return _t("Sans action depuis %s ou plus", formatDays(this.data.thresholds.dormant_days));
    }

    workloadCellTitle(row, day, count) {
        return _t("%(name)s, %(day)s : %(count)s activité(s)", {
            name: row.name,
            day: formatDay(day.date),
            count,
        });
    }

    // ------------------------------------------------------------------
    // Tendances
    // ------------------------------------------------------------------

    get trendIsEmpty() {
        const trend = this.state.trend;
        const sum = (values) => values.reduce((total, value) => total + value, 0);
        return !sum(trend.done_on_time) && !sum(trend.done_late) && !sum(trend.created);
    }

    get trendTotals() {
        const trend = this.state.trend;
        const sum = (values) => values.reduce((total, value) => total + value, 0);
        return {
            onTime: sum(trend.done_on_time),
            late: sum(trend.done_late),
            created: sum(trend.created),
        };
    }

    openReport() {
        this.action.doAction("aite_crm_activity.action_crm_activity_report");
    }

    // ------------------------------------------------------------------
    // Affichage
    // ------------------------------------------------------------------

    formatDay(value) {
        return formatDay(value);
    }

    formatShortDay(value) {
        return formatShortDay(value);
    }

    formatRate(value) {
        return formatRate(value);
    }

    formatDays(value) {
        return formatDays(value);
    }

    formatAmount(lead) {
        return lead ? formatAmount(lead.expected_revenue, lead.currency_id) : "";
    }

    formatAmounts(amounts) {
        return formatAmounts(amounts);
    }

    deadlineLabel(activity) {
        return deadlineLabel(activity);
    }

    severityBadge(level) {
        return severityBadge(level);
    }

    isBusy(activity) {
        return Boolean(this.state.busyIds[activity.id]);
    }

    // ------------------------------------------------------------------
    // Aperçu d'une opportunité
    // ------------------------------------------------------------------

    openPreview(leadId, ev) {
        // Le focus revient sur le dernier lien utilisé à la fermeture.
        this.previewOpener = ev?.currentTarget || this.previewOpener;
        if (this.state.preview?.leadId === leadId) {
            // Même opportunité : l'aperçu est rechargé (utile après un échec).
            this.state.preview.refreshKey++;
            return;
        }
        this.state.preview = { leadId, refreshKey: 0 };
    }

    closePreview() {
        this.state.preview = null;
        const opener = this.previewOpener;
        this.previewOpener = null;
        if (opener?.isConnected) {
            opener.focus();
        }
    }

    isPreviewed(leadId) {
        return this.state.preview?.leadId === leadId;
    }

    // ------------------------------------------------------------------
    // Actions
    // ------------------------------------------------------------------

    /**
     * Appelle une action du serveur sur une activité, puis recharge.
     * `message` peut être une fonction recevant le résultat de l'action.
     */
    async runAction(activity, method, args, message) {
        this.state.busyIds[activity.id] = true;
        try {
            const result = await this.orm.call(DASHBOARD_MODEL, method, args);
            const text = typeof message === "function" ? message(result) : message;
            this.notification.add(text, { type: "success" });
            await this.reload();
        } finally {
            delete this.state.busyIds[activity.id];
        }
    }

    markDone(activity) {
        this.dialog.add(AiteActivityDoneDialog, {
            activity,
            onConfirm: (feedback) =>
                this.runAction(activity, "action_mark_done", [activity.id, feedback],
                    _t("Activité marquée comme faite.")),
        });
    }

    /**
     * Nouvelle échéance : 'tomorrow', 'monday' ou 'week' (calculés par le
     * serveur sur la date du jour), ou une date AAAA-MM-JJ.
     */
    reschedule(activity, value) {
        return this.runAction(activity, "action_reschedule", [activity.id, value],
            (date) => _t("Nouvelle échéance : %s.", formatDay(date)));
    }

    /** Date libre, à partir du jour du serveur (pas de la date du navigateur). */
    rescheduleOnDate(activity) {
        const today = deserializeDate(this.data.today);
        this.dialog.add(AiteActivityDateDialog, {
            activity,
            defaultDate: serializeDate(today.plus({ days: 1 })),
            minDate: serializeDate(today),
            onConfirm: (value) => this.reschedule(activity, value),
        });
    }

    reassign(activity) {
        this.dialog.add(AiteActivityReassignDialog, {
            activity,
            users: this.data.options.assignable_users.filter((u) => u.id !== activity.user_id),
            onConfirm: (user) =>
                this.runAction(activity, "action_reassign", [activity.id, user.id],
                    _t("Activité réassignée à %s.", user.name)),
        });
    }

    openLead(leadId) {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "crm.lead",
            res_id: leadId,
            views: [[false, "form"]],
        });
    }

    async scheduleActivity(lead) {
        // Même fenêtre que le bouton « Planifier une activité » d'Odoo.
        await new Promise((resolve) =>
            this.action.doAction(
                {
                    type: "ir.actions.act_window",
                    name: _t("Planifier une activité"),
                    res_model: "mail.activity.schedule",
                    view_mode: "form",
                    views: [[false, "form"]],
                    target: "new",
                    context: {
                        active_model: "crm.lead",
                        active_ids: [lead.id],
                        active_id: lead.id,
                    },
                },
                { onClose: resolve, additionalContext: { dialog_size: "large" } }
            )
        );
        await this.reload();
    }
}

registry.category("actions").add("aite_crm_activity_dashboard", AiteCrmActivityDashboard);
