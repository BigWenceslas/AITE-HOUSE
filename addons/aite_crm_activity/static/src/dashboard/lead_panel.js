import {
    Component,
    onMounted,
    onWillStart,
    onWillUnmount,
    onWillUpdateProps,
    status,
    useEffect,
    useRef,
    useState,
} from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { useBus, useService } from "@web/core/utils/hooks";
import { getActiveHotkey } from "@web/core/hotkeys/hotkey_service";
import { useHotkey } from "@web/core/hotkeys/hotkey_hook";
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
 * un panneau latéral : la page à côté reste utilisable au clavier. Si la
 * largeur change (rotation d'une tablette, fenêtre redimensionnée) pendant
 * qu'une fenêtre ou le menu « Reporter » est ouvert depuis le panneau, le
 * passage d'un mode à l'autre attend sa fermeture : elle garde Échap et le
 * focus.
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
        this.uiService = useService("ui");
        // Suit la largeur de l'écran (passage plein écran / panneau latéral).
        this.ui = useState(this.uiService);
        this.panelRef = useRef("panel");
        this.closeRef = useRef("close");
        this.state = useState({
            lead: null,
            loading: true,
            error: false,
            // Fenêtre modale en ce moment : suit isModal (voir syncModal).
            modal: this.isModal && !this.hasOverlay,
        });
        this.lastRequest = 0;
        useEffect(
            (el, modal) => (el && modal ? this.activateModal(el) : undefined),
            () => [this.panelRef.el, this.state.modal]
        );
        // Changement de largeur. Un passage différé (fenêtre ou menu ouvert)
        // est refait à la fermeture d'une fenêtre d'Odoo, ou du menu (voir
        // onMenuToggle).
        useEffect(
            () => this.syncModal(),
            () => [this.isModal]
        );
        useBus(this.uiService.bus, "active-element-changed", () => this.syncModal());
        // Échap, inscrite une seule fois : une fenêtre ou un menu ouvert
        // ensuite par-dessus, inscrit après, la reçoit d'abord. Le panneau
        // ne la prend que si rien n'est ouvert au-dessus de lui.
        useHotkey("escape", () => this.props.onClose(), {
            global: true,
            isAvailable: () => this.isOnTop,
        });
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
     * Une fenêtre d'Odoo (Fait, Réassigner, erreur…) ou le menu « Reporter »
     * du panneau est ouvert par-dessus lui. Le menu ne devient pas l'élément
     * actif d'Odoo : ses raccourcis restent rattachés à celui de son
     * ouverture.
     */
    get hasOverlay() {
        const el = this.panelRef.el;
        if (el?.querySelector(".o-dropdown.show")) {
            return true;
        }
        const top = this.uiService.activeElement;
        return !(top === document || top === el || (el && top.contains(el)));
    }

    /** Rien n'est ouvert au-dessus du panneau : Échap lui revient. */
    get isOnTop() {
        const top = this.uiService.activeElement;
        return top === document || top === this.panelRef.el;
    }

    /**
     * Passe en fenêtre modale ou en panneau latéral selon la largeur, mais
     * pas sous une fenêtre ou un menu ouvert : changer l'élément actif
     * d'Odoo lui prendrait Échap et le focus. Refait à sa fermeture.
     */
    syncModal() {
        if (this.state.modal !== this.isModal && !this.hasOverlay) {
            this.state.modal = this.isModal;
        }
    }

    /** Menu « Reporter » ouvert ou fermé (après la mise à jour de sa classe). */
    onMenuToggle() {
        Promise.resolve().then(() => {
            if (status(this) === "mounted") {
                this.syncModal();
            }
        });
    }

    /**
     * Panneau plein écran : il devient l'élément actif d'Odoo, et Tab /
     * Maj+Tab bouclent sur ses boutons et liens au lieu de partir vers la
     * page cachée derrière (comme dans les fenêtres d'Odoo), y compris quand
     * le focus n'est plus nulle part (bouton retiré par un rechargement).
     * Renvoie la fonction qui rétablit le comportement de panneau latéral.
     */
    activateModal(el) {
        const ui = this.uiService;
        const trapFocus = (ev) => {
            const hotkey = getActiveHotkey(ev);
            if ((hotkey !== "tab" && hotkey !== "shift+tab") || ui.activeElement !== el) {
                return;
            }
            const focused = document.activeElement;
            const inside = el.contains(focused);
            if (!inside && focused?.closest(".o-overlay-container")) {
                // Menu « Reporter » du panneau, affiché hors de lui.
                return;
            }
            const [first, last] = getFirstAndLastTabableElements(el);
            let target = null;
            if (!first) {
                target = el;
            } else if (!inside) {
                // Focus sur la page cachée derrière, ou nulle part.
                target = hotkey === "tab" ? first : last;
            } else if (hotkey === "tab" && focused === last) {
                target = first;
            } else if (hotkey === "shift+tab" && focused === first) {
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
        // Une fenêtre ouverte depuis le panneau se ferme : Odoo rend le focus
        // au bouton qui l'a ouverte, sauf si un rechargement l'a retiré
        // entre-temps (action refusée, activité disparue). Il revient alors au
        // bouton « Fermer » du panneau.
        let timer;
        const recoverFocus = () => {
            if (ui.activeElement !== el) {
                return;
            }
            clearTimeout(timer);
            timer = setTimeout(() => {
                const focused = document.activeElement;
                if (ui.activeElement === el && (!focused || focused === document.body)) {
                    this.closeRef.el?.focus();
                }
            });
        };
        ui.activateElement(el);
        document.addEventListener("keydown", trapFocus);
        ui.bus.addEventListener("active-element-changed", recoverFocus);
        if (!el.contains(document.activeElement)) {
            this.closeRef.el?.focus();
        }
        return () => {
            clearTimeout(timer);
            ui.bus.removeEventListener("active-element-changed", recoverFocus);
            document.removeEventListener("keydown", trapFocus);
            ui.deactivateElement(el);
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
