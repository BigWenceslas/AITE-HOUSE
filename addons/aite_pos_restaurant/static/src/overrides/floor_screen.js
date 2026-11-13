/** Le plan verrouillé (spécification, partie 1.1 A ; T17).
 *
 * - une phrase d'état sous la barre ; caisse pas encore ouverte : un bandeau
 *   et le bouton « Ouvrir la caisse » (la fenêtre du code s'ouvre d'elle-même
 *   au montage du plan : Odoo appelle `openOpeningControl`) ;
 * - les tables ne se glissent plus : le glisser d'Odoo délie et lie les
 *   tables hors mode d'édition, et le compte de la caisse n'écrit pas les
 *   tables. Un écouteur `pointerdown` en phase de capture, posé sur le plan,
 *   arrête la propagation vers celui d'Odoo ; le `click` passe (il ouvre la
 *   table). */
import { patch } from "@web/core/utils/patch";
import { onMounted, onWillUnmount } from "@odoo/owl";
import { FloorScreen } from "@pos_restaurant/app/floor_screen/floor_screen";
import { TEXTES } from "@aite_pos_restaurant/utils/messages";

patch(FloorScreen.prototype, {
    setup() {
        super.setup(...arguments);
        this.aiteTextes = TEXTES;
        const sansGlisser = (ev) => {
            if (this.pos.aiteActif && !this.pos.isEditMode && ev.target.closest?.(".table")) {
                ev.stopPropagation();
            }
        };
        let plan = null;
        onMounted(() => {
            plan = this.floorMapRef.el;
            plan?.addEventListener("pointerdown", sansGlisser, true);
        });
        onWillUnmount(() => plan?.removeEventListener("pointerdown", sansGlisser, true));
    },
    get aiteCaisseFermee() {
        return this.pos.aiteActif && this.pos.session.state === "opening_control";
    },
    aiteOuvrirLaCaisse() {
        this.pos.openOpeningControl();
    },
});
