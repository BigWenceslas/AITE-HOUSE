import {
    Component,
    onMounted,
    onWillStart,
    onWillUnmount,
    onWillUpdateProps,
    useRef,
    useState,
} from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";
import { useHotkey } from "@web/core/hotkeys/hotkey_hook";
import { RPCError } from "@web/core/network/rpc";
import { Dropdown } from "@web/core/dropdown/dropdown";
import { DropdownItem } from "@web/core/dropdown/dropdown_item";
import {
    DASHBOARD_MODEL,
    deadlineLabel,
    formatAmount,
    formatDay,
    formatDays,
    severityBadge,
} from "./dashboard_utils";

/**
 * Aperçu d'une opportunité, ouvert depuis le tableau de bord sans le
 * quitter : panneau à droite sur ordinateur, plein écran sur téléphone.
 *
 * Les données viennent de get_lead_preview (droits de lecture vérifiés par
 * le serveur). Si l'on passe vite d'une opportunité à l'autre, seule la
 * réponse à la dernière demande est affichée. Les boutons des activités
 * (Fait, Reporter, Réassigner) appellent les mêmes actions que la liste du
 * tableau de bord, qui recharge ensuite l'aperçu (``refreshKey``).
 *
 * Fermeture : bouton « Fermer » ou touche Échap (une fenêtre ou un menu
 * ouvert par-dessus se ferme d'abord, Odoo donnant la touche au dernier
 * élément ouvert).
 */
export class AiteLeadPanel extends Component {
    static template = "aite_crm_activity.LeadPanel";
    static components = { Dropdown, DropdownItem };
    static props = {
        leadId: Number,
        refreshKey: Number,
        busyIds: Object,
        canReassign: Boolean,
        onClose: Function,
        onOpenLead: Function,
        onSchedule: Function,
        onMarkDone: Function,
        onReschedule: Function,
        onRescheduleOnDate: Function,
        onReassign: Function,
    };

    setup() {
        this.orm = useService("orm");
        this.closeRef = useRef("close");
        this.state = useState({ lead: null, loading: true, error: false });
        this.lastRequest = 0;
        useHotkey("escape", () => this.props.onClose());
        // Pas d'attente : le panneau s'ouvre tout de suite, avec son
        // indicateur de chargement et son bouton « Fermer ».
        onWillStart(() => {
            this.fetch(this.props.leadId);
        });
        onWillUpdateProps((nextProps) => {
            if (nextProps.leadId !== this.props.leadId) {
                this.fetch(nextProps.leadId, { reset: true });
            } else if (nextProps.refreshKey !== this.props.refreshKey) {
                this.fetch(nextProps.leadId);
            }
        });
        onMounted(() => {
            // Les notifications se décalent à gauche du panneau (voir le SCSS).
            document.body.classList.add("o_aite_cad_panel_open");
            this.closeRef.el?.focus();
        });
        onWillUnmount(() => document.body.classList.remove("o_aite_cad_panel_open"));
    }

    /**
     * Charge l'aperçu. ``reset`` : autre opportunité, on n'affiche plus
     * l'ancienne pendant le chargement. Une erreur du serveur (opportunité
     * supprimée, accès refusé) s'affiche dans le panneau.
     */
    async fetch(leadId, { reset = false } = {}) {
        const request = ++this.lastRequest;
        if (reset) {
            this.state.lead = null;
        }
        this.state.loading = true;
        this.state.error = false;
        try {
            const lead = await this.orm.call(DASHBOARD_MODEL, "get_lead_preview", [leadId]);
            if (request === this.lastRequest) {
                this.state.lead = lead;
            }
        } catch (error) {
            if (request !== this.lastRequest) {
                return;
            }
            if (!(error instanceof RPCError)) {
                throw error;
            }
            this.state.lead = null;
            this.state.error = error.data?.message || _t("L'aperçu n'a pas pu être chargé.");
        } finally {
            if (request === this.lastRequest) {
                this.state.loading = false;
            }
        }
    }

    retry() {
        this.fetch(this.props.leadId, { reset: true });
    }

    get lead() {
        return this.state.lead;
    }

    get titleId() {
        return `o_aite_cad_panel_title_${this.props.leadId}`;
    }

    /** Activité de l'aperçu, complétée pour les fenêtres du tableau de bord. */
    asActivity(activity) {
        return { ...activity, lead: { id: this.lead.id, name: this.lead.name } };
    }

    isBusy(activity) {
        return Boolean(this.props.busyIds[activity.id]);
    }

    get stars() {
        const priority = parseInt(this.lead.priority || "0") || 0;
        return [1, 2, 3].map((index) => index <= priority);
    }

    get priorityLabel() {
        const priority = parseInt(this.lead.priority || "0") || 0;
        return _t("Priorité : %(count)s sur 3", { count: priority });
    }

    get idleText() {
        if (!this.lead.last_action_date) {
            return _t("Aucune action enregistrée");
        }
        if (this.lead.idle_days === 0) {
            return _t("%s (aujourd'hui)", formatDay(this.lead.last_action_date));
        }
        return _t("%(date)s (il y a %(days)s)", {
            date: formatDay(this.lead.last_action_date),
            days: formatDays(this.lead.idle_days),
        });
    }

    formatDay(value) {
        return formatDay(value);
    }

    formatAmount(lead) {
        return formatAmount(lead.expected_revenue, lead.currency_id);
    }

    formatProbability(value) {
        return `${Math.round(value || 0)} %`;
    }

    deadlineLabel(activity) {
        return deadlineLabel(activity);
    }

    severityBadge(level) {
        return severityBadge(level);
    }

    openLead() {
        this.props.onOpenLead(this.props.leadId);
    }

    schedule() {
        this.props.onSchedule({ id: this.props.leadId });
    }
}
