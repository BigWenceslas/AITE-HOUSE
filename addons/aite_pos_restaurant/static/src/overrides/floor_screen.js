/** Le plan verrouillé (spécification, partie 1.1 A ; T17).
 *
 * - une phrase d'état sous la barre ; caisse pas encore ouverte : un bandeau
 *   et le bouton « Ouvrir la caisse » (la fenêtre du code s'ouvre d'elle-même
 *   au montage du plan : Odoo appelle `openOpeningControl`) ;
 * - les tables ne se glissent plus : le glisser d'Odoo délie et lie les
 *   tables hors mode d'édition, et le compte de la caisse n'écrit pas les
 *   tables. Un écouteur `pointerdown` en phase de capture, posé sur le plan,
 *   arrête la propagation vers celui d'Odoo ; le `click` passe (il ouvre la
 *   table).
 *
 * Incrément 5 — le plan en couleurs (REST-17) : gris = libre, vert =
 * ouverte, orange = ouverte depuis le délai de la caisse ou plus ; la durée
 * sous le numéro (« 35 min », « 1 h 05 »), comptée depuis l'heure
 * d'ouverture posée par le serveur ; une légende en bas. Une minuterie de
 * 30 secondes appelle `pos.aiteTic()`, qui fait recalculer couleurs et
 * durées sans que personne ne touche l'écran ; l'heure est lue par
 * `luxon.DateTime.now()`. */
import { patch } from "@web/core/utils/patch";
import { onMounted, onWillUnmount } from "@odoo/owl";
import { FloorScreen } from "@pos_restaurant/app/floor_screen/floor_screen";
import { TEXTES } from "@aite_pos_restaurant/utils/messages";
import { TIC } from "@aite_pos_restaurant/utils/alerte";

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
        let minuterie = null;
        onMounted(() => {
            plan = this.floorMapRef.el;
            plan?.addEventListener("pointerdown", sansGlisser, true);
            if (this.pos.aiteActif) {
                minuterie = setInterval(() => this.pos.aiteTic(), TIC);
            }
        });
        onWillUnmount(() => {
            plan?.removeEventListener("pointerdown", sansGlisser, true);
            clearInterval(minuterie);
        });
    },
    get aiteCaisseFermee() {
        return this.pos.aiteActif && this.pos.session.state === "opening_control";
    },
    aiteOuvrirLaCaisse() {
        this.pos.openOpeningControl();
    },

    // ------------------------------------------------------------------
    // Incrément 5 : couleurs, durée, légende
    // ------------------------------------------------------------------

    /** Minutes depuis l'ouverture de la table (son addition ouverte, ou celle
     * de sa table parente), ou `null` pour une table libre ou une addition
     * pas encore enregistrée. Lire `pos.aiteHorloge` abonne le plan au tic de
     * la minuterie. */
    aiteMinutes(table) {
        void this.pos.aiteHorloge; // abonnement au tic de la minuterie
        const order = table.getOrder?.();
        return order ? this.pos.aiteMinutesOuverte(order) : null;
    },

    /** « libre », « vert » ou « orange » (attribut `data-aite-alerte`). Une
     * table occupée dont l'addition n'a pas encore d'heure (pas encore
     * enregistrée) est verte. */
    aiteAlerte(table) {
        if (!this.pos.tableHasOrders(table)) {
            return "libre";
        }
        return this.pos.aiteAlerte(this.aiteMinutes(table) ?? 0);
    },

    /** La durée sous le numéro : « 35 min », « 1 h 05 » ; rien pour une
     * table libre. */
    aiteDuree(table) {
        if (!this.pos.tableHasOrders(table)) {
            return "";
        }
        const minutes = this.aiteMinutes(table);
        return minutes === null ? "" : TEXTES.duree(minutes);
    },

    get aiteLegende() {
        return TEXTES.legendeParties(this.pos.config.aite_delai_alerte);
    },
});
