import {
    Component,
    onMounted,
    onWillStart,
    onWillUnmount,
    onWillUpdateProps,
    useEffect,
    useRef,
    useState,
} from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";
import { getActiveHotkey } from "@web/core/hotkeys/hotkey_service";
import { RPCError } from "@web/core/network/rpc";
import { SIZES, getFirstAndLastTabableElements } from "@web/core/ui/ui_service";
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
 *
 * Sous 992 px, le panneau couvre toute la page (voir le SCSS) : il se
 * comporte alors en fenêtre modale (aria-modal, focus gardé dans le
 * panneau, raccourcis d'Odoo limités au panneau). Sur ordinateur, il reste
 * un panneau latéral : la page à côté reste utilisable au clavier.
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
        this.hotkey = useService("hotkey");
        this.uiService = useService("ui");
        // Suit la largeur de l'écran (passage plein écran / panneau latéral).
        this.ui = useState(this.uiService);
        this.panelRef = useRef("panel");
        this.closeRef = useRef("close");
        this.state = useState({ lead: null, loading: true, error: false });
        this.lastRequest = 0;
        useEffect(
            (el, modal) => (el && modal ? this.activateModal(el) : undefined),
            () => [this.panelRef.el, this.isModal]
        );
        // Échap, inscrite après le passage en modale : Odoo la rattache à
        // l'élément actif du moment (le panneau plein écran, ou la page).
        useEffect(
            () => this.hotkey.add("escape", () => this.props.onClose()),
            () => [this.isModal]
        );
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
            // Message dans le panneau, avec « Réessayer », quelle que soit
            // l'erreur (connexion perdue comprise, qu'Odoo signale aussi).
            const message = error instanceof RPCError ? error.data?.message : null;
            this.state.lead = null;
            this.state.error = message || _t("L'aperçu n'a pas pu être chargé.");
            if (!(error instanceof RPCError)) {
                throw error;
            }
        } finally {
            if (request === this.lastRequest) {
                this.state.loading = false;
            }
        }
    }

    retry() {
        this.fetch(this.props.leadId, { reset: true });
    }

    /** Plein écran (téléphone, tablette) : le panneau masque la page. */
    get isModal() {
        return this.ui.size < SIZES.LG;
    }

    /**
     * Panneau plein écran : il devient l'élément actif d'Odoo, et Tab /
     * Maj+Tab bouclent sur ses boutons et liens au lieu de partir vers la
     * page cachée derrière (comme dans les fenêtres d'Odoo). Renvoie la
     * fonction qui rétablit le comportement de panneau latéral.
     */
    activateModal(el) {
        const trapFocus = (ev) => {
            const hotkey = getActiveHotkey(ev);
            if (hotkey !== "tab" && hotkey !== "shift+tab") {
                return;
            }
            const [first, last] = getFirstAndLastTabableElements(el);
            let target = null;
            if (!first) {
                target = el;
            } else if (hotkey === "tab" && document.activeElement === last) {
                target = first;
            } else if (hotkey === "shift+tab" && document.activeElement === first) {
                target = last;
            }
            if (target) {
                ev.preventDefault();
                ev.stopPropagation();
                if (target !== el) {
                    target.focus();
                }
            }
        };
        this.uiService.activateElement(el);
        el.addEventListener("keydown", trapFocus);
        if (!el.contains(document.activeElement)) {
            this.closeRef.el?.focus();
        }
        return () => {
            el.removeEventListener("keydown", trapFocus);
            this.uiService.deactivateElement(el);
        };
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
