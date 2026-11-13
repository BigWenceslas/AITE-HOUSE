/** La fenêtre du code (spécification, partie 1.1 B ; `AiteCodePopup`).
 *
 * Étape « code » : un pavé, quatre points qui se remplissent, validation
 * seule au quatrième chiffre, un seul « Retour ». La fenêtre ne connaît pas
 * les employés : la reconnaissance du code est faite par l'appelant
 * (`reconnaitre`), qui rend
 * - l'employé reconnu ;
 * - un texte : il s'affiche dans la fenêtre (R1), les points sont vidés ;
 * - faux : les points sont vidés (l'appelant a déjà prévenu, par exemple
 *   R3 ou R10 en notification) et la fenêtre attend un autre code.
 *
 * Étape « personnes » (incrément 3) : huit gros boutons 1 à 8, qui valident ;
 * « 9 et plus » ouvre un pavé et « Valider », grisé tant que la valeur est
 * vide ou nulle (R5) ; le zéro n'existe pas ; le même « Retour ». Elle
 * s'enchaîne dans la même fenêtre après un code reconnu si `etapePersonnes`
 * (appelé avec l'employé) rend un titre — une table libre : l'appelant y
 * relit l'état des tables sur le serveur ; ou elle est demandée seule
 * (`etape: "personnes"`, bouton « 4 personnes »).
 *
 * La fenêtre rend `{employe, code, personnes}` (`personnes` : 0 si l'étape
 * n'a pas eu lieu), ou rien (« Retour »). */
import { Component, useState } from "@odoo/owl";
import { Dialog } from "@web/core/dialog/dialog";
import { MESSAGES, TEXTES } from "@aite_pos_restaurant/utils/messages";

export class AiteCodePopup extends Component {
    static template = "aite_pos_restaurant.AiteCodePopup";
    static components = { Dialog };
    static props = {
        titre: String,
        sousTitre: { type: String, optional: true },
        etape: { type: String, optional: true },
        reconnaitre: { type: Function, optional: true },
        etapePersonnes: { type: Function, optional: true },
        getPayload: Function,
        close: Function,
    };

    setup() {
        this.textes = TEXTES;
        this.touches = ["1", "2", "3", "4", "5", "6", "7", "8", "9"];
        this.boutonsPersonnes = ["1", "2", "3", "4", "5", "6", "7", "8"];
        this.state = useState({
            etape: this.props.etape || "code",
            titre: this.props.titre,
            code: "",
            erreur: "",
            verification: false,
            plus: false,
            nombre: "",
        });
        this.employe = null;
        this.codeReconnu = "";
    }

    // ------------------------------------------------------------------
    // Étape « code »
    // ------------------------------------------------------------------

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
        let titrePersonnes = false;
        try {
            reponse = await this.props.reconnaitre(code);
            if (reponse && typeof reponse === "object" && this.props.etapePersonnes) {
                titrePersonnes = await this.props.etapePersonnes(reponse);
            }
        } catch (erreur) {
            this.state.code = "";
            throw erreur;
        } finally {
            this.state.verification = false;
        }
        if (reponse && typeof reponse === "object") {
            this.employe = reponse;
            this.codeReconnu = code;
            if (titrePersonnes) {
                this.state.etape = "personnes";
                this.state.titre = titrePersonnes;
                return;
            }
            this.terminer(0);
            return;
        }
        this.state.code = "";
        this.state.erreur = typeof reponse === "string" ? reponse : "";
    }

    // ------------------------------------------------------------------
    // Étape « personnes »
    // ------------------------------------------------------------------

    choisir(nombre) {
        this.terminer(parseInt(nombre, 10));
    }

    ouvrirPlus() {
        this.state.plus = true;
    }

    toucherNombre(chiffre) {
        if (this.state.nombre.length < 3) {
            this.state.nombre += chiffre;
        }
    }

    effacerNombre() {
        this.state.nombre = this.state.nombre.slice(0, -1);
    }

    get nombreValide() {
        return parseInt(this.state.nombre, 10) >= 1;
    }

    /** R5, sous le nombre tapé : affiché dès qu'un zéro est tapé. */
    get erreurPersonnes() {
        return this.state.nombre !== "" && !this.nombreValide ? MESSAGES.R5 : "";
    }

    validerNombre() {
        if (this.nombreValide) {
            this.terminer(parseInt(this.state.nombre, 10));
        }
    }

    terminer(personnes) {
        this.props.getPayload({ employe: this.employe, code: this.codeReconnu, personnes });
        this.props.close();
    }
}
