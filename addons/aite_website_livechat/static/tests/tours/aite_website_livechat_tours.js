import { registry } from "@web/core/registry";

/**
 * Visiteur public, aucun opérateur en ligne : la bulle est là, le visiteur
 * écrit et reçoit aussitôt le message d'absence.
 */
registry.category("web_tour.tours").add("aite_website_livechat_offline_tour", {
    steps: () => [
        {
            content: "Aucun opérateur en ligne : la bulle du chat est affichée",
            trigger: ".o-livechat-root:shadow .o-livechat-LivechatButton",
            run: "click",
        },
        {
            content: "Le visiteur écrit",
            trigger: ".o-livechat-root:shadow .o-mail-Composer-input",
            run: "edit Bonjour, écrivez-moi à visiteur.tour@exemple.cm",
        },
        {
            trigger: ".o-livechat-root:shadow .o-mail-Composer-input",
            run: "press Enter",
        },
        {
            content: "Son message est envoyé",
            trigger:
                ".o-livechat-root:shadow .o-mail-Thread:not([data-transient]) .o-mail-Message:contains('visiteur.tour@exemple.cm')",
        },
        {
            content: "Le message d'absence s'affiche",
            trigger:
                ".o-livechat-root:shadow .o-mail-Message:contains('Nous ne sommes pas en ligne pour le moment')",
        },
    ],
});

function delay(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * La bulle du chat et le bouton WhatsApp (module aite_website_whatsapp) ne
 * se chevauchent pas, en haut de page comme en fin de page (la bulle
 * remonte alors de 40 px).
 */
function checkNoOverlap(where) {
    const bubble = document
        .querySelector(".o-livechat-root")
        .shadowRoot.querySelector(".o-livechat-LivechatButton")
        .getBoundingClientRect();
    const whatsapp = document.querySelector(".o_aite_wa_button").getBoundingClientRect();
    const overlap = !(
        bubble.right <= whatsapp.left ||
        whatsapp.right <= bubble.left ||
        bubble.bottom <= whatsapp.top ||
        whatsapp.bottom <= bubble.top
    );
    const geometry = `bulle ${JSON.stringify(bubble)}, WhatsApp ${JSON.stringify(whatsapp)}`;
    if (overlap) {
        throw new Error(`${where} : la bulle et le bouton WhatsApp se chevauchent (${geometry})`);
    }
    if (whatsapp.bottom > bubble.top) {
        throw new Error(`${where} : le bouton WhatsApp n'est pas au-dessus de la bulle (${geometry})`);
    }
}

registry.category("web_tour.tours").add("aite_website_livechat_whatsapp_overlap_tour", {
    steps: () => [
        {
            content: "La bulle du chat est affichée",
            trigger: ".o-livechat-root:shadow .o-livechat-LivechatButton",
        },
        {
            content: "Le bouton WhatsApp est affiché, à droite",
            trigger: ".o_aite_wa_button.o_aite_wa_button_right",
            async run() {
                // Fin de l'animation d'apparition du bouton WhatsApp.
                await delay(800);
                checkNoOverlap("En haut de page");
                window.scrollTo(0, document.documentElement.scrollHeight);
                document.dispatchEvent(new Event("scroll"));
            },
        },
        {
            content: "En fin de page, toujours sans chevauchement",
            trigger: ".o-livechat-root:shadow .o-livechat-LivechatButton",
            async run() {
                await delay(800);
                checkNoOverlap("En fin de page");
            },
        },
    ],
});
