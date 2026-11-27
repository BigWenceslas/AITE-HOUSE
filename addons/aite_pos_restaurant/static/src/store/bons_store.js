/* global luxon */
/** Les bons de préparation et les notes de la caisse du restaurant
 * (demandes du Messager ; 18.0.1.0.13). Patch de PosStore, actif seulement
 * en mode (`aiteActif`) : une autre caisse de la base garde les bons d'Odoo.
 *
 * - Un envoi donne, par imprimante de préparation, UN bon en français
 *   (`aite_pos_restaurant.BonDePreparation`) : « Nouveau », « Annulé »,
 *   « Note » (note changée d'un plat déjà parti) et « Note générale ».
 *   Odoo en faisait jusqu'à quatre feuilles, titrées en anglais (« New »,
 *   « Cancelled », « Note », « Message »), et l'en-tête disait « Tableau 7 »
 *   (la traduction de « Table » par l'éditeur de texte).
 * - Le bon sort en autant d'exemplaires que le réglage de l'imprimante
 *   (« Nombre d'exemplaires du bon ») s'il porte un nouveau plat, en un seul
 *   sinon ; chaque exemplaire dit « Exemplaire 2/3 » en haut (rien si un seul).
 * - La note générale tapée seule part sur les imprimantes qui ont déjà reçu
 *   un plat de la table (toutes s'il n'y en a aucune) ; Odoo ne l'imprimait
 *   qu'avec un nouveau plat, tout en affichant « Envoyé : Message × 1 ».
 *   Sur un bon qui porte de nouveaux plats, la note générale de la table est
 *   rappelée en bas, comme dans Odoo.
 * - Une imprimante qui ne répond pas : on n'essaie pas ses autres
 *   exemplaires, et une seule alerte, en français, nomme les imprimantes en
 *   cause. Comme dans Odoo, l'envoi reste enregistré (la cuisine est
 *   prévenue de vive voix).
 * - « Note cuisine » sur une ligne en partie envoyée : la note va aux seules
 *   unités pas encore parties, sur une ligne à part, sans rouvrir la fenêtre
 *   des accompagnements ; la quantité et le total ne changent pas
 *   (`aiteScinderPourLaNote`). La coupure est un déplacement pour le journal
 *   des saisies (ni saisie, ni retrait).
 *
 * Relecture de 18.0.1.0.13 :
 * - une note changée sur un plat parti puis une unité de plus au pavé : Odoo
 *   (`getOrderChanges`) range le même objet dans « nouveau » et « note » et
 *   lui donne la quantité déjà partie ; le bon disait « Nouveau 3 » pour un
 *   seul plat ajouté. La quantité nouvelle est recalculée
 *   (`aiteQuantitesReelles`) ;
 * - une erreur au rendu d'un bon compte comme une imprimante qui ne répond
 *   pas (alerte « Bon non imprimé »), au lieu de passer sans bruit ;
 * - une note effacée sur un plat parti : « Note retirée : sans glaçon » ;
 * - les imprimantes en panne restent connues après l'envoi
 *   (`aiteBonsNonSortis`) : la notification « Envoyé » le dit ;
 * - « Message » (le compte de « J'envoie » et de « Envoyé : … ») devient
 *   « Note générale », le nom du bon. */
import { patch } from "@web/core/utils/patch";
import { renderToElement } from "@web/core/utils/render";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { PosStore } from "@point_of_sale/app/store/pos_store";
import "@aite_pos_restaurant/store/pos_store";
import { MESSAGES, TEXTES, TITRES, nombre } from "@aite_pos_restaurant/utils/messages";
import { bonVide, imprimantesDeLaNote, nombreDExemplaires } from "@aite_pos_restaurant/utils/bons";

patch(PosStore.prototype, {
    /** Les bons d'un envoi, imprimante par imprimante (voir l'en-tête). Rend
     * vrai si au moins un bon est sorti. */
    async printChanges(order, orderChange) {
        if (!this.aiteActif) {
            return super.printChanges(...arguments);
        }
        const reelles = this.aiteQuantitesReelles(order, orderChange);
        const nouveau = this.aiteTrierNouveau(reelles.new);
        // La note générale a changé : un texte (Odoo n'en met pas sinon ;
        // le bon d'annulation passe `false`), ou une note effacée qui avait
        // été envoyée.
        const generale = orderChange.generalNote;
        const noteChangee =
            typeof generale === "string" &&
            (generale !== "" || Boolean(order.last_order_preparation_change?.generalNote));
        const pourLaNote = noteChangee ? this.aiteImprimantesDeLaNote(order, nouveau) : [];
        const enPanne = [];
        this.aiteBonsNonSortis = enPanne;
        let imprime = false;
        for (const imprimante of this.unwatched.printers) {
            const changes = this._getPrintingCategoriesChanges(
                imprimante.config.product_categories_ids,
                { ...orderChange, ...reelles, new: nouveau }
            );
            const sections = {
                nouveau: changes.new,
                annule: changes.cancelled,
                notes: changes.noteUpdated,
                // La note générale : changée (sur les imprimantes concernées),
                // ou rappelée sous de nouveaux plats.
                noteGenerale:
                    (noteChangee && pourLaNote.includes(imprimante)) ||
                    (changes.new.length && order.general_note)
                        ? order.general_note || TEXTES.bonNoteRetiree
                        : "",
                changementDeMode: Boolean(orderChange.modeUpdate),
            };
            if (bonVide(sections)) {
                continue;
            }
            const total = nombreDExemplaires(sections, imprimante.config.aite_exemplaires);
            for (let rang = 1; rang <= total; rang++) {
                // Tout le bon est sous garde : une erreur de rendu (donnée
                // inattendue) compte comme une imprimante qui ne répond pas,
                // sinon Odoo l'avalerait et la caisse dirait « Envoyé ».
                let reponse;
                try {
                    const bon = this.aiteDonneesDuBon(order, sections);
                    const element = renderToElement("aite_pos_restaurant.BonDePreparation", {
                        bon: { ...bon, exemplaire: total > 1 ? TEXTES.exemplaire(rang, total) : "" },
                    });
                    reponse = await imprimante.printReceipt(element);
                } catch (erreur) {
                    console.info("Restaurant : bon non imprimé", erreur);
                    reponse = { successful: false };
                }
                if (!reponse?.successful) {
                    enPanne.push(imprimante.config.name);
                    break; // les autres exemplaires ne sortiraient pas mieux
                }
                imprime = true;
            }
        }
        if (enPanne.length) {
            this.dialog.add(AlertDialog, {
                title: TITRES.bonNonImprime,
                body: MESSAGES.bonNonImprime(enPanne),
            });
        }
        return imprime;
    },

    /** `orderChange.new` et `orderChange.cancelled` avec leurs vraies
     * quantités. Odoo (`getOrderChanges`) range le même objet dans les
     * changements et dans les notes modifiées quand une ligne partie change
     * à la fois de note et de quantité, et lui donne la quantité déjà partie
     * (celle de la section « Note ») : « Nouveau 3 Poulet DG » pour un seul
     * poulet ajouté. Ici, la quantité nouvelle (ou annulée) d'une telle ligne
     * est recalculée — sa quantité moins ce qui est parti —, sur une copie ;
     * la section « Note » garde la quantité partie. */
    aiteQuantitesReelles(order, orderChange) {
        const parties = order.last_order_preparation_change?.lines || {};
        const notes = new Set((orderChange.noteUpdated || []).map((ligne) => ligne.uuid));
        const corriger = (ligne) => {
            const partie = parties[ligne.uuid];
            const actuelle = order.lines.find((l) => l.uuid === ligne.uuid);
            if (!notes.has(ligne.uuid) || !partie || !actuelle) {
                return ligne;
            }
            const ecart = actuelle.get_quantity() - (partie.quantity || 0);
            return { ...ligne, quantity: Math.abs(ecart) };
        };
        return {
            new: (orderChange.new || []).map(corriger),
            cancelled: (orderChange.cancelled || []).map(corriger),
        };
    },

    /** Le compte de « J'envoie » et de la notification « Envoyé : … » : la
     * note générale s'y appelle « Note générale » (le nom du bon), pas
     * « Message ». */
    get categoryCount() {
        const compte = super.categoryCount;
        if (!this.aiteActif || !("generalNote" in this.getOrderChanges())) {
            return compte;
        }
        const message = compte.at(-1);
        return [...compte.slice(0, -1), { ...message, name: TEXTES.bonNoteGenerale }];
    },

    /** Les nouveaux plats dans l'ordre d'Odoo : les menus d'abord, puis les
     * familles par séquence. */
    aiteTrierNouveau(lignes) {
        const estUnMenu = (ligne) =>
            ligne.isCombo || this.models["product.product"].get(ligne.product_id)?.type === "combo";
        const menus = lignes.filter(estUnMenu);
        const autres = lignes.filter((ligne) => !estUnMenu(ligne));
        autres.sort((a, b) => {
            if (a.pos_categ_sequence === 0 && b.pos_categ_sequence === 0) {
                return a.pos_categ_id - b.pos_categ_id;
            }
            return a.pos_categ_sequence - b.pos_categ_sequence;
        });
        return [...menus, ...autres];
    },

    /** Les imprimantes qui reçoivent une note générale changée : celles qui
     * ont déjà reçu, ou reçoivent maintenant, un plat de la table ; toutes
     * si aucune (`imprimantesDeLaNote`). */
    aiteImprimantesDeLaNote(order, nouveau) {
        const produits = [
            ...Object.values(order.last_order_preparation_change?.lines || {}).map((l) => l.product_id),
            ...nouveau.map((l) => l.product_id),
        ];
        return imprimantesDeLaNote(
            this.unwatched.printers,
            produits,
            (imprimante) => imprimante.config.product_categories_ids || [],
            (id) => this.models["product.product"].get(id)?.parentPosCategIds || []
        );
    },

    /** Ce que dit le bon (le même pour tous ses exemplaires, heure comprise). */
    aiteDonneesDuBon(order, sections) {
        const emporter = Boolean(order.config.takeaway && order.takeaway);
        let mode = emporter ? TEXTES.bonAEmporter : TEXTES.bonSurPlace;
        if (sections.changementDeMode) {
            mode = emporter ? TEXTES.bonVersAEmporter : TEXTES.bonVersSurPlace;
        }
        const employe = order.employee_id?.name || order.user_id?.name || "";
        const nom = order.table_id?.table_number ?? order.floating_order_name;
        const enLigne = (texte) =>
            (typeof texte === "string" ? texte : "")
                .split("\n")
                .filter((n) => n.trim())
                .join(", ");
        // Avant l'envoi, ce qui est parti garde l'ancienne note de chaque plat.
        const parties = order.last_order_preparation_change?.lines || {};
        const lignes = (liste, sectionNote = false) =>
            liste.map((ligne) => {
                let note = enLigne(ligne.note);
                if (sectionNote && !note) {
                    // La note d'un plat parti a été effacée : le dire.
                    const ancienne = enLigne(parties[ligne.uuid]?.note);
                    note = ancienne ? TEXTES.bonNoteRetireeDe(ancienne) : TEXTES.bonNoteRetiree;
                }
                return {
                    quantite: nombre(ligne.quantity),
                    nom: ligne.display_name || ligne.basic_name || ligne.name,
                    attributs: (ligne.attribute_value_ids || []).map((a) => a.name).filter(Boolean),
                    note,
                    combo: Boolean(ligne.isCombo),
                };
            });
        const blocs = [
            [TEXTES.bonNouveau, sections.nouveau, false],
            [TEXTES.bonAnnule, sections.annule, false],
            [TEXTES.bonNote, sections.notes, true],
        ];
        return {
            mode,
            poste: `${order.config.name} : ${luxon.DateTime.now().toFormat("HH:mm")}`,
            par: employe ? TEXTES.bonPar(employe) : "",
            table: nom !== undefined && nom !== false && nom !== "" ? TEXTES.table(nom) : TEXTES.venteSansTable,
            numero: order.tracking_number ? `# ${order.tracking_number}` : "",
            sections: blocs
                .filter(([, liste]) => liste.length)
                .map(([titre, liste, sectionNote]) => ({ titre, lignes: lignes(liste, sectionNote) })),
            noteGenerale: sections.noteGenerale
                ? { titre: TEXTES.bonNoteGenerale, texte: enLigne(sections.noteGenerale) }
                : null,
        };
    },

    /** « Note cuisine » sur une ligne dont une part est partie : la note va
     * aux unités pas encore envoyées, sur une ligne à part (même produit,
     * mêmes accompagnements, même prix) ; la ligne d'origine garde ce qui
     * est parti. Ni la quantité ni le total de l'addition ne changent ; rien
     * n'est demandé (pas de fenêtre des accompagnements, pas de contrôle du
     * stock : rien n'est ajouté). Rend la nouvelle ligne. */
    async aiteScinderPourLaNote(order, ligne, envoye, enPlus, note) {
        // D'abord ce qui a été saisi est enregistré, au nom de la personne
        // identifiée ; puis la coupure part comme un déplacement (ni saisie,
        // ni retrait), comme une division. Sinon, si l'addition avait déjà
        // été enregistrée avec l'unité de plus, le serveur voyait la ligne
        // neuve comme une nouvelle saisie : un plat compté deux fois au
        // journal des saisies (relecture de 18.0.1.0.13).
        await this.aiteSynchroniser(order, { deplacement: false });
        this.aiteDeplacementEnCours = true;
        try {
            const nouvelle = this.aiteCouperLaLigne(order, ligne, envoye, enPlus, note);
            await this.aiteSynchroniser(order, { deplacement: true });
            return nouvelle;
        } finally {
            this.aiteDeplacementEnCours = false;
        }
    },

    /** La coupure elle-même (voir `aiteScinderPourLaNote`). */
    aiteCouperLaLigne(order, ligne, envoye, enPlus, note) {
        const nouvelle = this.models["pos.order.line"].create({
            order_id: order,
            product_id: ligne.product_id,
            qty: enPlus,
            note,
            price_unit: ligne.price_unit,
            price_type: ligne.price_type,
            price_extra: ligne.price_extra,
            discount: ligne.discount,
            customer_note: ligne.customer_note || "",
            full_product_name: ligne.full_product_name,
            tax_ids: ligne.tax_ids.map((taxe) => ["link", taxe]),
            attribute_value_ids: ligne.attribute_value_ids.map((valeur) => ["link", valeur]),
            custom_attribute_value_ids: ligne.custom_attribute_value_ids.map((valeur) => [
                "create",
                {
                    custom_product_template_attribute_value_id:
                        valeur.custom_product_template_attribute_value_id,
                    custom_value: valeur.custom_value,
                },
            ]),
        });
        ligne.set_quantity(envoye, true);
        this.selectOrderLine(order, nouvelle);
        return nouvelle;
    },
});
