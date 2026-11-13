/** Caisse du restaurant AITE : le cœur, patch de PosStore (spécification, partie 4.1).
 *
 * Incrément 1 : l'accesseur unique du mode « Service à table contrôlé ». Tous
 * les patchs des incréments suivants commencent par
 * `if (!this.pos.aiteActif) return super…` : une autre caisse de la même base
 * n'est pas touchée.
 */
import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";
// Fixe l'ordre des patchs : ceux de pos_hr et du restaurant d'abord.
import "@pos_hr/overrides/models/pos_store";
import "@pos_restaurant/overrides/models/pos_store";

patch(PosStore.prototype, {
    /** Vrai si la case « Service à table contrôlé » est cochée sur une caisse
     * de restaurant qui se connecte avec les employés (pos.config est chargé
     * avec tous ses champs). */
    get aiteActif() {
        const config = this.config;
        return Boolean(
            config?.aite_mode_restaurant && config.module_pos_restaurant && config.module_pos_hr
        );
    },
});
