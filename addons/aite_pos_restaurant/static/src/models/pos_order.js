/** L'addition en caisse (spécification, partie 4.1 ; incrément 3).
 *
 * Personnes : pos_restaurant remet 1 personne à toute addition qui en a 0, à
 * chaque chargement (`customer_count || 1`). Une part née d'une division
 * (« 12B ») et une vente sans table ont 0 personne (Q29, Q76) : un 0 venu du
 * serveur est gardé.
 *
 * Incrément 4 : filet de `removeOrderline` — une ligne dont une part est
 * partie en cuisine ou au bar ne se retire pas sans autorisation (rend faux,
 * comme Odoo quand rien n'est retiré).
 *
 * Partager à parts égales (demande du Messager) : le partage choisi sur
 * l'écran de paiement est tenu par l'addition (`uiState.aitePartage`, en
 * mémoire du poste, tant que le total ne change pas) ; chaque ligne de
 * paiement créée pendant le partage (bouton de mode, « Mettre sur
 * ardoise ») est une part et garde son montant ; la part en cours se déduit
 * des lignes qui existent encore et ne sont pas à 0 (une ligne supprimée
 * remet le compteur en cohérence). Une part intermédiaire payée en espèces
 * au-delà de la part : la différence est la « monnaie à rendre » que dit
 * le bandeau, et la ligne revient au montant de la part au mode suivant ou
 * à la validation. Le nombre de parts est écrit sur l'addition
 * (`aite_parts_egales`) à la validation, quand toutes les parts sont
 * encaissées : le ticket le dit sous les paiements, même réimprimé. */
import { patch } from "@web/core/utils/patch";
import { PosOrder } from "@point_of_sale/app/models/pos_order";
import "@pos_restaurant/overrides/models/pos_order";
import { partEnvoyee } from "@aite_pos_restaurant/utils/envoi";
import { caisseEnMode } from "@aite_pos_restaurant/models/pos_order_line";
import { floatIsZero } from "@web/core/utils/numbers";
import { TEXTES } from "@aite_pos_restaurant/utils/messages";
import { montantDUnePart } from "@aite_pos_restaurant/utils/parts_egales";
import { grouperParFamille } from "@aite_pos_restaurant/utils/familles";
import { formatCurrency } from "@point_of_sale/app/models/utils/currency";
import { omit } from "@web/core/utils/objects";

patch(PosOrder.prototype, {
    setup(vals) {
        super.setup(...arguments);
        const config = this.config;
        if (
            config?.aite_mode_restaurant &&
            config.module_pos_restaurant &&
            config.module_pos_hr &&
            typeof vals?.id === "number" &&
            vals.customer_count === 0
        ) {
            this.customer_count = 0;
        }
    },
    removeOrderline(line) {
        if (caisseEnMode(this.config) && !this.uiState?.aiteAutorisation && partEnvoyee(line) > 0) {
            return false;
        }
        return super.removeOrderline(...arguments);
    },
    /** Le partage en cours, tant qu'il porte sur le total de l'addition :
     * un pourboire ou un produit ajouté le rend caduc (null), il se refait
     * d'un toucher. */
    aitePartageEnCours() {
        const partage = this.uiState?.aitePartage;
        if (!partage) {
            return null;
        }
        const ecart = partage.total - this.getTotalDue();
        return floatIsZero(ecart, this.currency.decimal_places) ? partage : null;
    },
    /** Les lignes de paiement nées du partage qui existent encore et ne sont
     * pas à 0 (Odoo retire les lignes à 0 à la validation) :
     * [{ ligne, part, derniere }]. */
    aiteLignesDuPartage() {
        const partage = this.aitePartageEnCours();
        if (!partage) {
            return [];
        }
        const decimales = this.currency.decimal_places;
        return partage.lignes
            .map(({ uuid, part, derniere }) => ({
                ligne: this.payment_ids.find((ligne) => ligne.uuid === uuid),
                part,
                derniere,
            }))
            .filter(({ ligne }) => ligne && !floatIsZero(ligne.get_amount(), decimales));
    },
    /** Les parts intermédiaires payées en espèces au-delà de la part : la
     * personne a donné plus, la différence lui est rendue. */
    aiteSurplusDesParts() {
        return this.aiteLignesDuPartage().filter(
            ({ ligne, part, derniere }) =>
                !derniere && ligne.payment_method_id.is_cash_count && ligne.get_amount() > part
        );
    },
    /** La monnaie à rendre sur ces parts (0 s'il n'y en a pas). */
    aiteMonnaieDesParts() {
        const monnaie = this.aiteSurplusDesParts().reduce(
            (somme, { ligne, part }) => somme + ligne.get_amount() - part,
            0
        );
        return Number(monnaie.toFixed(this.currency.decimal_places));
    },
    /** Ces lignes reviennent au montant de leur part : la caisse enregistre
     * ce qui reste dans le tiroir une fois la monnaie rendue. */
    aiteRamenerAuxParts() {
        for (const { ligne, part } of this.aiteSurplusDesParts()) {
            ligne.set_amount(part);
        }
    },
    /** La part en cours : { rang, nombre, montant, derniere, monnaie }, ou
     * { reglee: true, complet } quand il n'y a plus rien à partager ; null
     * sans partage. Le reste dû compte la monnaie à rendre comme déjà
     * rendue. Une part intermédiaire ne dépasse jamais ce reste ; la
     * dernière est ce reste. */
    aitePartEnCours() {
        const partage = this.aitePartageEnCours();
        if (!partage) {
            return null;
        }
        const decimales = this.currency.decimal_places;
        const rang = this.aiteLignesDuPartage().length + 1;
        const monnaie = this.aiteMonnaieDesParts();
        const du = Number((this.get_due() + monnaie).toFixed(decimales));
        if (rang > partage.nombre || du <= 0) {
            return { reglee: true, nombre: partage.nombre, complet: rang > partage.nombre, monnaie };
        }
        const derniere = rang === partage.nombre;
        const part = montantDUnePart(
            partage.base,
            partage.nombre,
            partage.pas,
            rang,
            this.currency.rounding
        );
        return {
            rang,
            nombre: partage.nombre,
            derniere,
            montant: derniere ? du : Math.min(part, du),
            monnaie,
        };
    },
    /** Toucher un mode de paiement (ou « Mettre sur ardoise ») pendant un
     * partage : les parts payées en espèces au-delà de la part reviennent à
     * leur montant, puis la nouvelle ligne est la part en cours (la
     * dernière : le reste dû, montant d'Odoo, arrondi en espèces). */
    add_paymentline(paymentMethod) {
        const partage = this.aitePartageEnCours();
        if (!partage) {
            return super.add_paymentline(...arguments);
        }
        this.aiteRamenerAuxParts();
        const part = this.aitePartEnCours();
        const ligne = super.add_paymentline(...arguments);
        if (ligne && part && !part.reglee) {
            if (!part.derniere) {
                ligne.set_amount(part.montant);
            }
            partage.lignes = [
                ...partage.lignes,
                { uuid: ligne.uuid, part: part.montant, derniere: part.derniere },
            ];
        }
        return ligne;
    },
    /** Toutes les parts du partage sont encaissées (lignes à 0 exclues). */
    aitePartageComplet() {
        const partage = this.aitePartageEnCours();
        return Boolean(partage) && this.aiteLignesDuPartage().length >= partage.nombre;
    },
    export_for_printing() {
        const donnees = super.export_for_printing(...arguments);
        donnees.aitePartage = this.aite_parts_egales ? TEXTES.partagee(this.aite_parts_egales) : "";
        if (caisseEnMode(this.config)) {
            // La note générale est une consigne pour la cuisine : elle ne va
            // ni sur l'addition ni sur le ticket du client (18.0.1.0.13).
            donnees.generalNote = "";
            if (this.config.aite_grouper_familles) {
                donnees.aiteFamilles = this.aiteFamillesDuTicket(donnees.orderlines);
            }
        }
        return donnees;
    },

    /** L'addition et le ticket groupés par famille (réglage « Grouper les
     * produits par famille sur l'addition et le ticket », 18.0.1.0.14) :
     * [{ titre, lignes, libelle, sousTotal }], les lignes au format du ticket
     * d'Odoo (`affichees`, dans l'ordre de `getSortedOrderlines`).
     *
     * La famille d'une ligne est la famille de niveau 1 (la racine) de la
     * première famille de caisse du produit ; les familles suivent l'ordre
     * de la caisse (séquence). Un élément de menu reste avec son menu. Le
     * sous-total est la somme des montants imprimés des lignes (TTC si la
     * caisse affiche les prix TTC, comme les lignes). Les produits sans
     * famille sont sous « Autres » ; le pourboire, la remise globale et les
     * récompenses viennent ensuite, sans titre ni sous-total (ce ne sont pas
     * des produits de la carte) : la somme des sous-totaux et de ces lignes
     * reste égale au total. */
    aiteFamillesDuTicket(affichees) {
        const lignes = this.getSortedOrderlines();
        if (!Array.isArray(affichees) || affichees.length !== lignes.length) {
            affichees = lignes.map((l) => omit(l.getDisplayData(), "internalNote"));
        }
        const affichage = new Map(lignes.map((ligne, i) => [ligne, affichees[i]]));
        const horsFamille = [this.config.tip_product_id?.id, this.config.discount_product_id?.id].filter(
            Boolean
        );
        const groupes = grouperParFamille(lignes, {
            familleDe: (ligne) => {
                let famille = ligne.get_product()?.pos_categ_ids?.[0];
                if (!famille) {
                    return null;
                }
                while (famille.parent_id) {
                    famille = famille.parent_id;
                }
                return { cle: famille.id, titre: famille.name, rang: famille.sequence || 0 };
            },
            parentDe: (ligne) => ligne.combo_parent_id || null,
            horsFamille: (ligne) =>
                horsFamille.includes(ligne.get_product()?.id) || Boolean(ligne.is_reward_line),
            montant: (ligne) => ligne.get_display_price(),
            titreAutres: TEXTES.familleAutres,
        });
        // Le dernier groupe (pourboire, remise globale, récompenses) n'a ni
        // titre ni sous-total : il vient après les familles, avant le total.
        return groupes.map((groupe) => ({
            titre: groupe.titre,
            horsFamilles: Boolean(groupe.horsFamilles),
            lignes: groupe.lignes.map((ligne) => affichage.get(ligne)),
            libelle: groupe.horsFamilles ? "" : TEXTES.sousTotal(groupe.titre),
            sousTotal: groupe.horsFamilles ? "" : formatCurrency(groupe.sousTotal, this.currency),
        }));
    },

    /** L'écran tourné vers le client ne montre pas non plus la note générale
     * (relecture de 18.0.1.0.13) ; la note au client, oui. */
    getCustomerDisplayData() {
        const donnees = super.getCustomerDisplayData(...arguments);
        if (caisseEnMode(this.config)) {
            donnees.generalNote = "";
        }
        return donnees;
    },
});
