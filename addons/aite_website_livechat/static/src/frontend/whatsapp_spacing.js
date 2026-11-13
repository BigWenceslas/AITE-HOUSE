import { registry } from "@web/core/registry";

/**
 * Bulle du chat et bouton WhatsApp (module aite_website_whatsapp) : le bouton
 * se place toujours au-dessus de la colonne de bulles du chat.
 *
 * La hauteur de cette colonne varie : conversations réduites empilées
 * au-dessus de la bulle, bouton d'options, marge plus grande sur téléphone
 * et tablette (Android, iPhone, iPad), décalage en fin de page ou pendant
 * une coupure de connexion. Elle est donc mesurée dans la page (le chat est
 * dessiné dans un « shadow DOM » ouvert) et le bouton WhatsApp est posé
 * 12 px au-dessus, par la variable CSS --o-aite-lc-wa-bottom
 * (static/src/scss/livechat_button.scss). Sans bouton WhatsApp à droite, ou
 * quand le visiteur a déplacé la bulle, rien ne change.
 */
const GAP = 12;
const BOTTOM_VAR = "--o-aite-lc-wa-bottom";

function getBubbleColumn() {
    const shadowRoot = document.querySelector("body > .o-livechat-root")?.shadowRoot;
    const hub = shadowRoot?.querySelector(".o-mail-ChatHub");
    if (!hub || hub.classList.contains("o-dragged")) {
        return null;
    }
    return hub.querySelector(".o-mail-ChatHub-bubbles > div");
}

function updateWhatsappButton() {
    const button = document.querySelector("#wrapwrap > .o_aite_wa_button_right");
    if (!button) {
        return;
    }
    const column = getBubbleColumn()?.getBoundingClientRect();
    const buttonRect = button.getBoundingClientRect();
    if (
        !column?.width ||
        !column.height ||
        column.right <= buttonRect.left ||
        buttonRect.right <= column.left
    ) {
        button.style.removeProperty(BOTTOM_VAR);
        return;
    }
    const bottom = Math.max(Math.ceil(window.innerHeight - column.top + GAP), 0);
    if (button.style.getPropertyValue(BOTTOM_VAR) !== `${bottom}px`) {
        button.style.setProperty(BOTTOM_VAR, `${bottom}px`);
    }
}

export const whatsappSpacingService = {
    start() {
        if (!document.querySelector("#wrapwrap > .o_aite_wa_button_right")) {
            return;
        }
        let frame = null;
        const schedule = () => {
            if (frame === null) {
                frame = requestAnimationFrame(() => {
                    frame = null;
                    updateWhatsappButton();
                });
            }
        };
        const observedShadowRoots = new WeakSet();
        const hubObserver = new MutationObserver(schedule);
        const observeLivechatRoot = () => {
            const shadowRoot = document.querySelector("body > .o-livechat-root")?.shadowRoot;
            if (shadowRoot && !observedShadowRoots.has(shadowRoot)) {
                observedShadowRoots.add(shadowRoot);
                hubObserver.observe(shadowRoot, {
                    subtree: true,
                    childList: true,
                    attributes: true,
                    attributeFilter: ["class", "style"],
                });
            }
            schedule();
        };
        // Le chat s'ajoute à la fin de la page après son chargement.
        new MutationObserver(observeLivechatRoot).observe(document.body, { childList: true });
        observeLivechatRoot();
        window.addEventListener("resize", schedule, { passive: true });
        document.addEventListener("scroll", schedule, { passive: true });
    },
};

registry.category("services").add("aite_website_livechat.whatsapp_spacing", whatsappSpacingService);
