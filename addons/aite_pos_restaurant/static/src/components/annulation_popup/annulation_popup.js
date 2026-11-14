/** La fenêtre d'annulation (spécification, partie 1.1 D ; T4 ;
 * `AiteAnnulationPopup` ; incrément 4).
 *
 * Une seule fenêtre, trois étapes dans cet ordre, chacune seulement si elle
 * sert :
 * 1. « Combien ? » : un bouton par quantité (« 1 », « 2 »… « 3 (tout) »),
 *    seulement si plus d'une unité est partie ;
 * 2. « Code d'un chef de salle » : le pavé, validé au 4ᵉ chiffre ; sautée si
 *    la personne identifiée sur le poste peut annuler (son code de visite est
 *    réutilisé, T3). Le code est contrôlé sur le poste avant d'aller plus
 *    loin (`reconnaitre`) : un code inconnu affiche R1 dans la fenêtre, un
 *    code qui ne peut pas annuler fait afficher R8 par l'appelant ;
 * 3. « Pourquoi ? » : un bouton par motif (lus sur le serveur à l'ouverture
 *    de la fenêtre) ; toucher un motif valide ; un motif à précision montre
 *    « Précision » et « Valider » (R24 dans la fenêtre si rien n'est écrit).
 *
 * Valider envoie la demande (`envoyer`, la requête au serveur, faite par
 * l'appelant) pendant que la fenêtre est ouverte : `true` la ferme et rend
 * `{quantite, code, motif_id, commentaire}` ; `"fermer"` la ferme sans rien
 * rendre (R26 : déjà annulé ailleurs) ; `false` la garde ouverte (R27 : pas
 * de réseau, toucher de nouveau le motif réessaie avec la même clé de
 * demande). Un seul « Retour », qui ferme sans rien annuler. Sélecteurs des
 * tours : `data-aite-quantite`, `data-aite-chiffre`, `data-aite-motif-id`. */
import { Component, useState } from "@odoo/owl";
import { Dialog } from "@web/core/dialog/dialog";
import { MESSAGES, TEXTES } from "@aite_pos_restaurant/utils/messages";

export class AiteAnnulationPopup extends Component {
    static template = "aite_pos_restaurant.AiteAnnulationPopup";
    static components = { Dialog };
    static props = {
        titre: String,
        sousTitre: { type: String, optional: true },
        quantites: { type: Array, optional: true },
        codeRequis: Boolean,
        reconnaitre: Function,
        motifs: Array,
        envoyer: Function,
        getPayload: Function,
        close: Function,
    };

    setup() {
        this.textes = TEXTES;
        this.touches = ["1", "2", "3", "4", "5", "6", "7", "8", "9"];
        const quantites = this.props.quantites || [];
        this.state = useState({
            etape: quantites.length > 1 ? "quantite" : this.etapeApresQuantite,
            code: "",
            erreur: "",
            verification: false,
            motif: null,
            precision: "",
            envoi: false,
        });
        this.choix = { quantite: quantites.at(-1) || 0, code: "" };
    }

    get etapeApresQuantite() {
        return this.props.codeRequis ? "code" : "motif";
    }

    libelleQuantite(quantite) {
        const quantites = this.props.quantites;
        return quantite === quantites.at(-1) ? TEXTES.tout(quantite) : String(quantite);
    }

    choisirQuantite(quantite) {
        this.choix.quantite = quantite;
        this.state.etape = this.etapeApresQuantite;
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
            await this.validerCode();
        }
    }

    effacer() {
        if (!this.state.verification) {
            this.state.code = this.state.code.slice(0, -1);
        }
    }

    async validerCode() {
        const code = this.state.code;
        this.state.verification = true;
        let reponse;
        try {
            reponse = await this.props.reconnaitre(code);
        } finally {
            this.state.verification = false;
        }
        if (reponse && typeof reponse === "object") {
            this.choix.code = code;
            this.state.etape = "motif";
            return;
        }
        this.state.code = "";
        this.state.erreur = typeof reponse === "string" ? reponse : "";
    }

    // ------------------------------------------------------------------
    // Étape « motif »
    // ------------------------------------------------------------------

    async choisirMotif(motif) {
        if (this.state.envoi) {
            return;
        }
        this.state.erreur = "";
        if (motif.precision_requise) {
            this.state.motif = motif;
            return;
        }
        await this.envoyer(motif, false);
    }

    async validerPrecision() {
        const precision = this.state.precision.trim();
        if (!precision) {
            this.state.erreur = MESSAGES.R24;
            return;
        }
        await this.envoyer(this.state.motif, precision);
    }

    async envoyer(motif, commentaire) {
        if (this.state.envoi) {
            return;
        }
        const demande = {
            quantite: this.choix.quantite,
            code: this.choix.code,
            motif_id: motif.id,
            commentaire,
        };
        this.state.envoi = true;
        let resultat;
        try {
            resultat = await this.props.envoyer(demande);
        } finally {
            this.state.envoi = false;
        }
        if (resultat === true) {
            this.props.getPayload(demande);
            this.props.close();
        } else if (resultat === "fermer") {
            this.props.close();
        }
    }
}
