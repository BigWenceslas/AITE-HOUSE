/** « Combien de personnes paient ? » : la fenêtre du partage à parts égales
 * (demande du Messager), ouverte par « Partager à parts égales » sur l'écran
 * de paiement.
 *
 * Sept gros boutons (2 à 8) et « Plus » (9 à 20) ; le nombre de personnes
 * de la table est présélectionné (2 s'il y en a moins de 2). La phrase « ce
 * qui va se passer » suit le choix : « Chaque personne paiera 33 333 FCFA ;
 * le dernier paie ce qui reste. » ; quand un paiement est déjà fait, la
 * fenêtre dit aussi le reste dû partagé. Un nombre dont la part serait nulle
 * (un très petit montant) est grisé. « Valider » rend le nombre choisi,
 * « Retour » ne change rien. Sélecteurs des tours : classes aite-parts-* et
 * attributs data-aite-parts (2 à 20, « plus »). */
import { Component, useState } from "@odoo/owl";
import { Dialog } from "@web/core/dialog/dialog";
import { TEXTES, TITRES } from "@aite_pos_restaurant/utils/messages";
import {
    PARTS_BOUTONS,
    PARTS_MAXIMUM,
    fourchetteDesParts,
    partagePossible,
    preselection,
} from "@aite_pos_restaurant/utils/parts_egales";

export class AitePartsPopup extends Component {
    static template = "aite_pos_restaurant.AitePartsPopup";
    static components = { Dialog };
    static props = {
        base: Number,
        pas: Number,
        unite: { type: Number, optional: true },
        personnes: { type: Number, optional: true },
        surLeReste: { type: Boolean, optional: true },
        getPayload: Function,
        close: Function,
    };

    setup() {
        this.textes = TEXTES;
        this.titre = TITRES.combienPaient;
        let nombre = preselection(this.props.personnes);
        while (nombre > 2 && !this.possible(nombre)) {
            nombre--;
        }
        this.state = useState({ nombre, plus: nombre > PARTS_BOUTONS.at(-1) });
    }

    get boutons() {
        return PARTS_BOUTONS;
    }

    get autres() {
        const autres = [];
        for (let nombre = PARTS_BOUTONS.at(-1) + 1; nombre <= PARTS_MAXIMUM; nombre++) {
            autres.push(nombre);
        }
        return autres;
    }

    possible(nombre) {
        return partagePossible(this.props.base, nombre, this.props.pas);
    }

    /** « Chaque personne paiera 33 333 FCFA » ; quand les pas ne se
     * partagent pas également (arrondi des espèces), « entre 2 650 et
     * 2 675 FCFA ». */
    get phrase() {
        const { min, max } = fourchetteDesParts(
            this.props.base,
            this.state.nombre,
            this.props.pas,
            this.props.unite ?? 1
        );
        const format = (montant) => this.env.utils.formatCurrency(montant);
        return min === max
            ? TEXTES.chaquePersonne(format(min))
            : TEXTES.chaquePersonneEntre(format(min), format(max));
    }

    get reste() {
        return TEXTES.resteAPartager(this.env.utils.formatCurrency(this.props.base));
    }

    choisir(nombre) {
        if (this.possible(nombre)) {
            this.state.nombre = nombre;
        }
    }

    valider() {
        if (this.possible(this.state.nombre)) {
            this.props.getPayload(this.state.nombre);
            this.props.close();
        }
    }
}
