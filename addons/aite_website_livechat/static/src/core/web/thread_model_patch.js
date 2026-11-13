import { Thread } from "@mail/core/common/thread_model";
import { patch } from "@web/core/utils/patch";

/**
 * Message d'absence : message automatique d'une conversation du chat, signé
 * de l'opérateur mais publié pendant son absence.
 */
function isLivechatAwayMessage(thread, message) {
    return thread.channel_type === "livechat" && message?.message_type === "auto_comment";
}

patch(Thread.prototype, {
    /**
     * Aperçu de la conversation dans la liste des messages de l'opérateur :
     * la question du visiteur plutôt que « Vous : Merci pour votre
     * message ! … ».
     */
    get aiteLivechatPreviewMessage() {
        return (
            this.newestPersistentAllMessages.find(
                (message) => !isLivechatAwayMessage(this, message)
            ) ?? this.newestPersistentOfAllMessage
        );
    },
    /**
     * Un message que l'opérateur publie lui-même marque la conversation
     * comme lue pour lui ; le message d'absence, publié sans lui, ne doit pas
     * faire passer la question du visiteur pour lue.
     */
    onNewSelfMessage(message) {
        if (isLivechatAwayMessage(this, message)) {
            return;
        }
        return super.onNewSelfMessage(...arguments);
    },
});
