/** La fenêtre du code (spécification, partie 1.1 B ; `AiteCodePopup`).
 *
 * Un pavé, quatre points qui se remplissent, validation seule au quatrième
 * chiffre, un seul « Retour ». La fenêtre ne connaît pas les employés : la
 * reconnaissance du code est faite par l'appelant (`reconnaitre`), qui rend
 * - l'employé reconnu : la fenêtre se ferme et rend `{employe, code}` ;
 * - un texte : il s'affiche dans la fenêtre (R1), les points sont vidés ;
 * - faux : les points sont vidés (l'appelant a déjà prévenu, par exemple
 *   R3 ou R10 en notification) et la fenêtre attend un autre code.
 * Incrément 2 : l'étape « code ». L'étape « personnes » vient à
 * l'incrément 3. */
import { Component, useState } from "@odoo/owl";
import { Dialog } from "@web/core/dialog/dialog";
import { TEXTES } from "@aite_pos_restaurant/utils/messages";

export class AiteCodePopup extends Component {
    static template = "aite_pos_restaurant.AiteCodePopup";
    static components = { Dialog };
    static props = {
        titre: String,
        sousTitre: { type: String, optional: true },
        reconnaitre: Function,
        getPayload: Function,
        close: Function,
    };

    setup() {
        this.textes = TEXTES;
        this.touches = ["1", "2", "3", "4", "5", "6", "7", "8", "9"];
        this.state = useState({ code: "", erreur: "", verification: false });
    }

    async toucher(chiffre) {
        if (this.state.verification || this.state.code.length >= 4) {
            return;
        }
        this.state.erreur = "";
        this.state.code += chiffre;
        if (this.state.code.length === 4) {
            await this.valider();
        }
    }

    effacer() {
        if (!this.state.verification) {
            this.state.code = this.state.code.slice(0, -1);
        }
    }

    async valider() {
        const code = this.state.code;
        this.state.verification = true;
        let reponse;
        try {
            reponse = await this.props.reconnaitre(code);
        } catch (erreur) {
            this.state.code = "";
            throw erreur;
        } finally {
            this.state.verification = false;
        }
        if (reponse && typeof reponse === "object") {
            this.props.getPayload({ employe: reponse, code });
            this.props.close();
            return;
        }
        this.state.code = "";
        this.state.erreur = typeof reponse === "string" ? reponse : "";
    }
}
