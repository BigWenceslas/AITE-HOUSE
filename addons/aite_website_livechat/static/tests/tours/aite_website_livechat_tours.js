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
 * remonte alors de 40 px) :
 * - aucun recouvrement entre l'icône WhatsApp et la colonne de bulles du
 *   chat (bulle, conversations réduites, bouton d'options même invisible) ;
 * - le bouton WhatsApp est au-dessus de la bulle ;
 * - un appui en haut, au milieu et en bas de l'icône WhatsApp touche bien
 *   le bouton WhatsApp, pas le chat.
 */
function checkNoOverlap(where) {
    const shadowRoot = document.querySelector(".o-livechat-root").shadowRoot;
    const bubble = shadowRoot
        .querySelector(".o-livechat-LivechatButton, .o-mail-ChatBubble")
        .getBoundingClientRect();
    const column = shadowRoot
        .querySelector(".o-mail-ChatHub-bubbles > div")
        .getBoundingClientRect();
    const whatsapp = document.querySelector(".o_aite_wa_button .o_aite_wa_icon").getBoundingClientRect();
    const geometry = `bulle ${JSON.stringify(bubble)}, colonne ${JSON.stringify(
        column
    )}, WhatsApp ${JSON.stringify(whatsapp)}`;
    for (const [name, rect] of [
        ["la bulle", bubble],
        ["la colonne de bulles", column],
    ]) {
        const overlap = !(
            rect.right <= whatsapp.left ||
            whatsapp.right <= rect.left ||
            rect.bottom <= whatsapp.top ||
            whatsapp.bottom <= rect.top
        );
        if (overlap) {
            throw new Error(`${where} : ${name} et le bouton WhatsApp se chevauchent (${geometry})`);
        }
    }
    if (whatsapp.bottom > bubble.top) {
        throw new Error(`${where} : le bouton WhatsApp n'est pas au-dessus de la bulle (${geometry})`);
    }
    for (const ratio of [0.2, 0.5, 0.8]) {
        const x = whatsapp.left + whatsapp.width / 2;
        const y = whatsapp.top + whatsapp.height * ratio;
        if (!document.elementFromPoint(x, y)?.closest(".o_aite_wa_button")) {
            throw new Error(
                `${where} : un appui à ${ratio * 100} % de la hauteur de l'icône WhatsApp ne la touche pas (${geometry})`
            );
        }
    }
}

function checkTopAndBottomSteps(label) {
    return [
        {
            content: `${label} : en haut de page, sans chevauchement`,
            trigger: ".o_aite_wa_button.o_aite_wa_button_right",
            async run() {
                window.scrollTo(0, 0);
                // Fin de l'animation d'apparition du bouton WhatsApp.
                await delay(800);
                checkNoOverlap(`${label}, en haut de page`);
                window.scrollTo(0, document.documentElement.scrollHeight);
                document.dispatchEvent(new Event("scroll"));
            },
        },
        {
            content: `${label} : en fin de page, toujours sans chevauchement`,
            trigger: ".o-livechat-root:shadow .o-mail-ChatHub-bubbles",
            async run() {
                await delay(800);
                checkNoOverlap(`${label}, en fin de page`);
            },
        },
    ];
}

function whatsappOverlapSteps({ mobileOS = false } = {}) {
    const steps = [
        {
            content: "La bulle du chat est affichée",
            trigger: ".o-livechat-root:shadow .o-livechat-LivechatButton",
        },
    ];
    if (mobileOS) {
        steps.push({
            content: "Téléphone (Android) : colonne de bulles en version mobile, plus haute",
            trigger: ".o-livechat-root:shadow .o-mail-ChatHub-bubbles.o-mobile",
        });
    }
    return [
        ...steps,
        {
            content: "Le bouton WhatsApp est affiché, à droite",
            trigger: ".o_aite_wa_button.o_aite_wa_button_right",
        },
        ...checkTopAndBottomSteps("Bulle seule"),
    ];
}

/**
 * Le visiteur écrit puis réduit la conversation : une bulle de plus
 * (conversation réduite) et le bouton d'options s'empilent dans la colonne.
 */
function foldedConversationSteps() {
    return [
        {
            trigger: ".o-livechat-root:shadow .o-livechat-LivechatButton",
            run: "click",
        },
        {
            trigger: ".o-livechat-root:shadow .o-mail-Composer-input",
            run: "edit Bonjour, je reviens plus tard.",
        },
        {
            trigger: ".o-livechat-root:shadow .o-mail-Composer button:has(.fa-paper-plane-o)",
            run: "click",
        },
        {
            content: "Le message d'absence s'affiche",
            trigger:
                ".o-livechat-root:shadow .o-mail-Message:contains('Nous ne sommes pas en ligne pour le moment')",
        },
        {
            content: "Le visiteur réduit la conversation",
            trigger: ".o-livechat-root:shadow .o-mail-ChatWindow-header button:has(.oi-minus)",
            run: "click",
        },
        {
            content: "La conversation réduite est dans la colonne de bulles",
            trigger: ".o-livechat-root:shadow .o-mail-ChatHub-bubbles .o-mail-ChatBubble",
        },
        ...checkTopAndBottomSteps("Conversation réduite"),
    ];
}

registry.category("web_tour.tours").add("aite_website_livechat_whatsapp_overlap_tour", {
    steps: () => whatsappOverlapSteps(),
});

registry.category("web_tour.tours").add("aite_website_livechat_whatsapp_folded_tour", {
    steps: () => [...whatsappOverlapSteps(), ...foldedConversationSteps()],
});

registry.category("web_tour.tours").add("aite_website_livechat_whatsapp_android_tour", {
    steps: () => [...whatsappOverlapSteps({ mobileOS: true }), ...foldedConversationSteps()],
});

/**
 * Opératrice : dans sa liste de messages, la conversation montre la question
 * du visiteur (pas « Vous : Merci pour votre message ! … ») et compte un
 * message non lu.
 */
registry.category("web_tour.tours").add("aite_website_livechat_operator_preview_tour", {
    steps: () => [
        {
            content: "Ouvrir la liste des messages",
            trigger: ".o_menu_systray i.fa-comments",
            run: "click",
        },
        {
            content: "La conversation montre la question du visiteur, un message non lu",
            trigger:
                ".o-mail-NotificationItem:contains('Bonjour, avez-vous ce modèle en stock ?'):has(.o-mail-NotificationItem-counter:contains('1'))",
        },
        {
            content: "Pas le message d'absence en aperçu",
            trigger:
                ".o-mail-NotificationItem:contains('Bonjour, avez-vous ce modèle en stock ?'):not(:contains('Nous ne sommes pas en ligne'))",
        },
    ],
});
