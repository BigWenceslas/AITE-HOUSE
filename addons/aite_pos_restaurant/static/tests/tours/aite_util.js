/* global posmodel, odoo */
/** Étapes communes des tours de la caisse du restaurant (spécification,
 * partie 6.3). Sélecteurs CSS et attributs `data-aite-*` seulement : aucun
 * libellé d'Odoo n'est cherché par son texte (les tours passent dans toutes
 * les langues). Les textes comparés sont ceux d'AITE (`MESSAGES`), ou ceux
 * d'Odoo passés par `_t` (la langue de la page).
 *
 * Ce fichier est chargé avec les tours de toute la base, y compris dans la
 * gestion, où les modules de la caisse n'existent pas : il n'importe que
 * `@web`, et lit les messages de la caisse au moment de l'étape. */
import { _t } from "@web/core/l10n/translation";

/** Les messages de la caisse (R1, R3…), lus dans le module déjà chargé par
 * la page de la caisse. */
function message(cle) {
    return odoo.loader.modules.get("@aite_pos_restaurant/utils/messages").MESSAGES[cle];
}

/** Un titre de la fenêtre du code (`TITRES`, partie 1.4), calculé au moment
 * de l'étape : `titre("personnes", 5)` rend une fonction, que les étapes
 * ci-dessous appellent. Les titres portent des espaces insécables. */
export function titre(cle, ...valeurs) {
    return () => {
        const modele = odoo.loader.modules.get("@aite_pos_restaurant/utils/messages").TITRES[cle];
        return typeof modele === "function" ? modele(...valeurs.map(valeur)) : modele;
    };
}

/** Une valeur donnée à une étape, ou calculée au moment de l'étape. */
function valeur(v) {
    return typeof v === "function" ? v() : v;
}

const POPUP = ".modal:not(.o_inactive_modal) .aite-code-popup";

/** Une étape qui vérifie l'état de la caisse : `test()` doit rendre vrai,
 * au plus tard après `delai` millisecondes. */
export function verifier(content, test, delai = 5000) {
    return {
        content,
        trigger: "body",
        async run() {
            const fin = Date.now() + delai;
            let dernier;
            while (Date.now() < fin) {
                dernier = test();
                if (dernier === true) {
                    return;
                }
                await new Promise((r) => setTimeout(r, 100));
            }
            throw new Error(`${content} : vérification fausse (${dernier})`);
        },
    };
}

export function personneIdentifiee() {
    return verifier("personne n'est identifié", () => !posmodel.cashier);
}

export function identifie(nom) {
    return verifier(`${nom} est identifié`, () => posmodel.cashier?.name === nom);
}

/** Le plan, verrouillé : aucun écran de connexion, personne d'identifié,
 * la phrase d'état affichée, pas de mode déplacement. */
export function planVerrouille() {
    return [
        { content: "le plan est affiché", trigger: ".floor-screen .floor-map" },
        {
            content: "aucun écran « Déverrouiller la caisse »",
            trigger: "body:not(:has(.screen-login)) .floor-screen",
        },
        { content: "la phrase d'état du plan", trigger: ".floor-screen .aite-plan-etat" },
        personneIdentifiee(),
        verifier("pas de mode déplacement", () => !posmodel.isOrderTransferMode),
    ];
}

export function popupCode() {
    return { content: "la fenêtre du code est ouverte", trigger: `${POPUP} .aite-code-pave` };
}

export function pasDePopupCode() {
    return { content: "aucune fenêtre du code", trigger: "body:not(:has(.aite-code-popup))" };
}

export function taperCode(code) {
    return [
        popupCode(),
        ...[...code].map((chiffre) => ({
            content: `touche ${chiffre}`,
            trigger: `${POPUP} [data-aite-chiffre="${chiffre}"]`,
            run: "click",
        })),
    ];
}

export function retour() {
    return { content: "« Retour »", trigger: `${POPUP} .aite-code-retour`, run: "click" };
}

/** R1, dans la fenêtre ; les points sont vidés. */
export function codeInconnu() {
    return [
        verifier("R1 dans la fenêtre", () => {
            const erreur = document.querySelector(`${POPUP} .aite-code-erreur`);
            return erreur?.textContent.trim() === message("R1") || erreur?.textContent;
        }),
        {
            content: "les quatre points sont vidés",
            trigger: `${POPUP} .aite-code-points:not(:has(.aite-point-plein))`,
        },
    ];
}

/** Une notification « danger » qui porte exactement le message `cle`
 * (« R3 »…, ou « R19 » avec ses `valeurs`) ; elle est fermée ensuite, pour
 * qu'une vérification suivante ne la retrouve pas. */
export function notificationDanger(cle, ...valeurs) {
    return verifier(`notification ${cle}`, () => {
        const modele = message(cle);
        const attendu = typeof modele === "function" ? modele(...valeurs.map(valeur)) : modele;
        for (const contenu of document.querySelectorAll(".o_notification_content")) {
            const notification = contenu.closest(".o_notification");
            if (
                contenu.textContent.trim() === attendu &&
                notification.querySelector(".o_notification_bar.bg-danger")
            ) {
                notification.querySelector(".o_notification_close")?.click();
                return true;
            }
        }
        return false;
    });
}

export function notificationQuiCommencePar(debut) {
    return verifier(`notification « ${debut}… »`, () =>
        [...document.querySelectorAll(".o_notification_content")].some((c) =>
            c.textContent.trim().startsWith(debut)
        )
    );
}

export function jEnvoie() {
    return { content: "« J'envoie »", trigger: ".actionpad .submit-order", run: "click" };
}

export function jEncaisse() {
    return {
        content: "« J'encaisse »",
        trigger: ".actionpad .pay-order-button:not(.pay)",
        run: "click",
    };
}

export function ecranCommande() {
    return [
        { content: "écran de commande", trigger: ".pos .product-screen" },
        { content: "pas l'écran de paiement", trigger: "body:not(:has(.payment-screen))" },
    ];
}

export function prendreLaMain() {
    return {
        content: "toucher le nom en haut pour prendre la main",
        trigger: ".pos-rightheader .cashier-name",
        run: "click",
    };
}

export function ouvrirActions() {
    return { content: "« Actions »", trigger: ".control-buttons .more-btn", run: "click" };
}

export function fermerFenetre() {
    return {
        content: "fermer la fenêtre",
        trigger: ".modal:not(.o_inactive_modal) .modal-header .btn-close",
        run: "click",
    };
}

export function remboursement(present) {
    if (present) {
        return {
            content: "« Remboursement » proposé",
            trigger: ".modal .control-buttons-modal button:has(.fa-undo)",
        };
    }
    return verifier("« Remboursement » absent", () => {
        const actions = document.querySelector(".modal .control-buttons-modal");
        return Boolean(actions) && !actions.querySelector(".fa-undo");
    });
}

/** Une entrée du menu ≡, désignée par son libellé d'Odoo (en anglais dans
 * le code, traduit par `_t` comme à l'écran). */
export function entreeDuMenu(libelleOdoo) {
    return {
        content: `menu : ${libelleOdoo}`,
        trigger: `.pos-burger-menu-items span.dropdown-item:contains("${_t(libelleOdoo)}")`,
        run: "click",
    };
}

export function menuSans(libelleOdoo) {
    return verifier(`menu ≡ sans « ${libelleOdoo} »`, () => {
        const menu = document.querySelector(".pos-burger-menu-items");
        if (!menu) {
            return "menu fermé";
        }
        return ![...menu.querySelectorAll(".dropdown-item")].some((item) =>
            item.textContent.includes(_t(libelleOdoo))
        );
    });
}

export function menuAvec(libelleOdoo) {
    return {
        content: `menu ≡ avec « ${libelleOdoo} »`,
        trigger: `.pos-burger-menu-items span.dropdown-item:contains("${_t(libelleOdoo)}")`,
    };
}

/** Une entrée du menu ≡ dont le libellé est celui d'AITE (partie 1.4). */
export function entreeAite(texte) {
    return {
        content: `menu : ${texte}`,
        trigger: `.pos-burger-menu-items span.dropdown-item:contains("${texte}")`,
        run: "click",
    };
}

/** Aucune notification « danger » ne porte le message `cle`. */
export function pasDeNotification(cle) {
    return verifier(`pas de notification ${cle}`, () =>
        ![...document.querySelectorAll(".o_notification_content")].some(
            (contenu) => contenu.textContent.trim() === message(cle)
        )
    );
}

export function deplacer() {
    return [
        ouvrirActions(),
        {
            content: "« Déplacer ou réunir »",
            trigger: ".modal .control-buttons-modal button:has(.oi-arrow-right)",
            run: "click",
        },
        verifier("mode déplacement", () => posmodel.isOrderTransferMode),
    ];
}

/** Le bouton « Table » de la barre (sélecteur de table d'Odoo). */
export function boutonTable() {
    return {
        content: "« Table » dans la barre",
        trigger: ".pos-leftheader .table-free-order-label",
        run: "click",
    };
}

/** Un second poste ouvre la caisse pendant que celui-ci la croit fermée :
 * les requêtes partent de ce poste sans toucher son état local (deux postes
 * ne peuvent pas être joués par un tour). */
export function autrePosteOuvreLaCaisse(code) {
    return {
        content: "un autre poste ouvre la caisse",
        trigger: "body",
        async run() {
            const id = posmodel.session.id;
            const reponse = await posmodel.data.call("pos.session", "aite_ouvrir_caisse", [
                [id],
                code,
            ]);
            if (reponse?.erreur) {
                throw new Error(reponse.erreur);
            }
            await posmodel.data.call("pos.session", "set_opening_control", [[id], 0, ""]);
            if (posmodel.session.state !== "opening_control") {
                throw new Error("le poste devait croire la caisse fermée");
            }
        },
    };
}

/** Le bandeau « caisse fermée » est affiché, ou ne l'est pas. */
export function bandeauCaisseFermee(present = true) {
    return present
        ? { content: "le bandeau « caisse fermée »", trigger: ".floor-screen .aite-caisse-fermee" }
        : {
              content: "plus de bandeau « caisse fermée »",
              trigger: ".floor-screen:not(:has(.aite-caisse-fermee))",
          };
}

/** La liste des commandes, filtre « Payé » (libellé d'Odoo, passé par `_t`). */
export function commandesPayees() {
    return [
        { content: "le filtre de la liste", trigger: ".pos-search-bar .filter", run: "click" },
        {
            content: "filtre « Payé »",
            trigger: `.pos-search-bar .filter ul li:contains("${_t("Paid")}")`,
            run: "click",
        },
    ];
}

// ----------------------------------------------------------------------
// Incrément 3 : l'étape « personnes », l'écran de commande
// ----------------------------------------------------------------------

/** Le titre de la fenêtre du code est `attendu` (un texte, ou `titre(…)`). */
export function titreDeLaFenetre(attendu) {
    return verifier("titre de la fenêtre", () => {
        const texte = document.querySelector(`${POPUP} .aite-code-titre`)?.textContent;
        return texte?.trim() === valeur(attendu) || JSON.stringify(texte);
    });
}

/** L'étape « personnes » est affichée (huit gros boutons, « 9 et plus »),
 * avec le titre `attendu` s'il est donné (`titre("personnes", 5)`). */
export function popupPersonnes(attendu = null) {
    return [
        {
            content: "l'étape « personnes » est ouverte",
            trigger: `${POPUP} .aite-personnes [data-aite-personnes="8"]`,
        },
        ...(attendu ? [titreDeLaFenetre(attendu)] : []),
    ];
}

/** Toucher un des huit gros boutons (1 à 8) : il valide. */
export function personnes(nombre) {
    return [
        ...popupPersonnes(),
        {
            content: `${nombre} personnes`,
            trigger: `${POPUP} [data-aite-personnes="${nombre}"]`,
            run: "click",
        },
    ];
}

export function pasDePopupPersonnes() {
    return { content: "pas d'étape « personnes »", trigger: "body:not(:has(.aite-personnes))" };
}

/** Le bouton « {p} personnes » de l'écran de commande. */
export function boutonPersonnes(libelle) {
    return {
        content: `le bouton « ${libelle} »`,
        trigger: `.control-buttons .aite-personnes-btn:contains("${libelle}")`,
    };
}

export function toucherBoutonPersonnes() {
    return {
        content: "toucher le bouton des personnes",
        trigger: ".control-buttons .aite-personnes-btn",
        run: "click",
    };
}

/** La phrase d'état de l'écran de commande commence par `debut`. */
export function etatCommande(debut) {
    return verifier(`phrase d'état « ${debut}… »`, () => {
        const texte = document.querySelector(".product-screen .aite-commande-etat")?.textContent;
        return texte?.trim().startsWith(debut) || texte;
    });
}

/** La table `numero` est occupée sur le plan (fond coloré, pas le gris des
 * tables libres), même sans produit. */
export function tableOccupee(numero) {
    return {
        content: `la table ${numero} est occupée`,
        trigger: `.floor-map .table:has(.label:contains("${numero}")):not([style*="00000020"]):not([style*="rgba(0, 0, 0, 0.12"])`,
    };
}

/** L'onglet d'une addition sans table (barre du haut), désigné par son
 * libellé. */
export function onglet(libelle) {
    return {
        content: `l'onglet « ${libelle} »`,
        trigger: `.pos-leftheader .list-container-items button:contains('${libelle}')`,
        run: "click",
    };
}

/** Les boutons d'« Actions » ne proposent pas « Modifier le nom de la
 * commande » d'Odoo (partie 1.1 C). La fenêtre est fermée ensuite. */
export function actionsSansRenommer() {
    return [
        ouvrirActions(),
        { content: "les boutons d'« Actions »", trigger: ".modal .control-buttons-modal" },
        verifier(
            "pas de « Modifier le nom de la commande »",
            () => !document.querySelector(".modal .control-buttons-modal .fa-pencil-square-o")
        ),
        fermerFenetre(),
    ];
}


// ----------------------------------------------------------------------
// Incrément 4 : la fenêtre d'annulation (`AiteAnnulationPopup`)
// ----------------------------------------------------------------------

const ANNULATION = ".modal:not(.o_inactive_modal) .aite-annulation-popup";

/** Un texte de la caisse (`TEXTES`), calculé au moment de l'étape. */
export function texte(cle, ...valeurs) {
    return () => {
        const modele = odoo.loader.modules.get("@aite_pos_restaurant/utils/messages").TEXTES[cle];
        return typeof modele === "function" ? modele(...valeurs.map(valeur)) : modele;
    };
}

/** Un message de refus (`MESSAGES`), calculé au moment de l'étape. */
export function messageDe(cle, ...valeurs) {
    return () => {
        const modele = message(cle);
        return typeof modele === "function" ? modele(...valeurs.map(valeur)) : modele;
    };
}

/** La fenêtre d'annulation est ouverte, avec le titre et le sous-titre
 * attendus s'ils sont donnés (`titre(…)`, `texte(…)`, `messageDe(…)`). */
export function popupAnnulation(titreAttendu = null, sousTitre = null) {
    return [
        { content: "la fenêtre d'annulation est ouverte", trigger: ANNULATION },
        ...(titreAttendu
            ? [
                  verifier("titre de la fenêtre d'annulation", () => {
                      const t = document.querySelector(`${ANNULATION} .aite-annulation-titre`);
                      return t?.textContent.trim() === valeur(titreAttendu) || JSON.stringify(t?.textContent);
                  }),
              ]
            : []),
        ...(sousTitre
            ? [
                  verifier("sous-titre de la fenêtre d'annulation", () => {
                      const t = document.querySelector(`${ANNULATION} .aite-annulation-sous-titre`);
                      return t?.textContent.trim() === valeur(sousTitre) || JSON.stringify(t?.textContent);
                  }),
              ]
            : []),
    ];
}

export function pasDePopupAnnulation() {
    return {
        content: "aucune fenêtre d'annulation",
        trigger: "body:not(:has(.aite-annulation-popup))",
    };
}

/** « Combien ? » : les boutons proposés, puis toucher `nombre`. */
export function combien(nombre, proposes = null) {
    return [
        { content: "« Combien ? »", trigger: `${ANNULATION} .aite-annulation-quantites` },
        ...(proposes
            ? [
                  verifier("les quantités proposées", () => {
                      const boutons = [
                          ...document.querySelectorAll(`${ANNULATION} [data-aite-quantite]`),
                      ].map((b) => b.dataset.aiteQuantite);
                      return JSON.stringify(boutons) === JSON.stringify(proposes) || JSON.stringify(boutons);
                  }),
              ]
            : []),
        {
            content: `annuler ${nombre}`,
            trigger: `${ANNULATION} [data-aite-quantite="${nombre}"]`,
            run: "click",
        },
    ];
}

/** Le pavé « Code d'un chef de salle » de la fenêtre d'annulation. */
export function codeAnnulation(code) {
    return [
        { content: "« Code d'un chef de salle »", trigger: `${ANNULATION} .aite-code-pave` },
        ...[...code].map((chiffre) => ({
            content: `touche ${chiffre}`,
            trigger: `${ANNULATION} [data-aite-chiffre="${chiffre}"]`,
            run: "click",
        })),
    ];
}

export function pasDeCodeAnnulation() {
    return verifier(
        "pas de code demandé",
        () => !document.querySelector(`${ANNULATION} .aite-code-pave`)
    );
}

/** « Pourquoi ? » : toucher le motif de rang `rang` (0 = le premier, dans
 * l'ordre des motifs : « Erreur de saisie »), qui valide. */
export function motif(rang = 0) {
    return [
        { content: "« Pourquoi ? »", trigger: `${ANNULATION} .aite-annulation-motifs` },
        {
            content: `le motif n° ${rang + 1}`,
            trigger: `${ANNULATION} .aite-annulation-motifs [data-aite-motif-id]:eq(${rang})`,
            run: "click",
        },
    ];
}

export function retourAnnulation() {
    return { content: "« Retour »", trigger: `${ANNULATION} .aite-annulation-retour`, run: "click" };
}

/** Une notification (de tout type) dont le texte vaut exactement `attendu`. */
export function notification(attendu) {
    return verifier("notification attendue", () =>
        [...document.querySelectorAll(".o_notification_content")].some(
            (c) => c.textContent.trim() === valeur(attendu)
        ) || [...document.querySelectorAll(".o_notification_content")].map((c) => c.textContent).join(" | ")
    );
}

/** La ligne du produit `nom` sur l'écran de commande, sa quantité affichée
 * (lue dans le modèle de la caisse, pas dans le texte). */
export function quantiteDeLaLigne(nom, attendu) {
    return verifier(`la ligne ${nom} est à ${attendu}`, () => {
        const ligne = posmodel.get_order()?.lines.find((l) => l.get_product().name === nom);
        const quantite = ligne ? ligne.get_quantity() : 0;
        return quantite === attendu || `quantité ${quantite}`;
    });
}

/** La table `numero` est libre sur le plan (aucune addition ouverte). */
export function tableLibre(numero) {
    return verifier(`la table ${numero} est libre`, () => {
        const table = posmodel.models["restaurant.table"].find((t) => t.table_number === numero);
        return (table && !posmodel.getActiveOrdersOnTable(table).length) || "table occupée";
    });
}
