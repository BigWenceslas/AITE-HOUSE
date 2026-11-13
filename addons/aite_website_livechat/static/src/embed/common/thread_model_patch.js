import { Thread } from "@mail/core/common/thread_model";
import { patch } from "@web/core/utils/patch";

patch(Thread.prototype, {
    /**
     * Fenêtre du chat du visiteur : le message d'absence revient avec la
     * réponse à l'envoi de son premier message. Il est ajouté aussitôt à la
     * conversation, sans attendre la connexion en temps réel (websocket), qui
     * peut manquer (proxy mal réglé, réseau d'entreprise, reconnexion).
     */
    async post() {
        const message = await super.post(...arguments);
        if (message && this.channel_type === "livechat") {
            for (const other of Object.values(this.store["mail.message"].records)) {
                if (
                    other.message_type === "auto_comment" &&
                    other.id > message.id &&
                    other.thread?.eq(this) &&
                    other.notIn(this.messages)
                ) {
                    this.addOrReplaceMessage(other);
                }
            }
        }
        return message;
    },
});
