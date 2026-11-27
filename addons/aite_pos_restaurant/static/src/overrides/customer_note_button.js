/** Les boutons de note de l'écran de commande (« Note cuisine », « Note au
 * client », « Note générale ») : les défauts constatés au Messager
 * (18.0.1.0.13). En mode seulement ; hors mode, le comportement d'Odoo.
 *
 * - « Ignorer » (ou la croix) ne change rien. Odoo effaçait la note du plat
 *   et la note générale, et coupait quand même une ligne en partie envoyée.
 * - « Note cuisine » sur une ligne en partie envoyée (3 poulets partis, un
 *   4ᵉ saisi) : la note va au 4ᵉ, sur une ligne à part, sans rouvrir la
 *   fenêtre des accompagnements ; l'addition garde sa quantité et son total
 *   (`PosStore.aiteScinderPourLaNote`). Odoo passait par un nouvel ajout de
 *   produit : la fenêtre des accompagnements se rouvrait et l'addition
 *   pouvait grossir.
 * - « Note au client » ne coupe jamais la ligne (elle ne va pas en cuisine)
 *   et s'ouvre sur une ligne déjà envoyée (Odoo plantait : la note lue du
 *   serveur vaut `false`, pas un texte).
 * - Une note existante peut être effacée : « Appliquer » est permis sur un
 *   champ vidé (sinon « Ignorer » était le seul moyen, et il ne doit plus
 *   rien changer). */
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { OrderlineNoteButton } from "@point_of_sale/app/screens/product_screen/control_buttons/customer_note_button/customer_note_button";
import { TextInputPopup } from "@point_of_sale/app/utils/input_popups/text_input_popup";
import { makeAwaitable } from "@point_of_sale/app/store/make_awaitable_dialog";
import { partEnvoyee } from "@aite_pos_restaurant/utils/envoi";

/** Le champ peut être vidé puis appliqué (effacer une note existante). */
TextInputPopup.props = { ...TextInputPopup.props, aiteVider: { type: Boolean, optional: true } };

patch(OrderlineNoteButton.prototype, {
    async addLineNotes() {
        if (!this.pos.aiteActif) {
            return super.addLineNotes(...arguments);
        }
        const order = this.pos.get_order();
        const ligne = order?.get_selected_orderline();
        if (!ligne) {
            return { confirmed: false };
        }
        const avant = this.props.getter(ligne) || "";
        const oldNote = ligne.getNote();
        const payload = await this.openTextInput(avant);
        if (typeof payload !== "string") {
            return { confirmed: false, inputNote: payload, oldNote }; // « Ignorer »
        }
        if (payload === avant) {
            return { confirmed: true, inputNote: payload, oldNote };
        }
        const envoye = partEnvoyee(ligne);
        const enPlus = ligne.get_quantity() - envoye;
        const menu = ligne.combo_line_ids?.length || ligne.combo_parent_id;
        if (this._isInternalNote() && envoye > 1e-9 && enPlus > 1e-9 && !menu) {
            await this.pos.aiteScinderPourLaNote(order, ligne, envoye, enPlus, payload);
        } else {
            this.props.setter(ligne, payload);
        }
        return { confirmed: true, inputNote: payload, oldNote };
    },

    async addGeneralNote() {
        if (!this.pos.aiteActif) {
            return super.addGeneralNote(...arguments);
        }
        const order = this.pos.get_order();
        const payload = await this.openTextInput(order.general_note || "");
        if (typeof payload !== "string") {
            return { confirmed: false, inputNote: payload }; // « Ignorer »
        }
        order.general_note = payload;
        return { confirmed: true, inputNote: payload };
    },

    async openTextInput(selectedNote) {
        if (!this.pos.aiteActif) {
            return super.openTextInput(...arguments);
        }
        const texte = typeof selectedNote === "string" ? selectedNote : "";
        let buttons = [];
        if (this._isInternalNote() || this.props.label == _t("General Note")) {
            buttons = this.pos.models["pos.note"].getAll().map((note) => ({
                label: note.name,
                isSelected: texte.split("\n").includes(note.name),
            }));
        }
        return await makeAwaitable(this.dialog, TextInputPopup, {
            title: _t("Add %s", this.props.label),
            buttons,
            rows: 4,
            startingValue: texte,
            aiteVider: Boolean(texte),
        });
    },
});
