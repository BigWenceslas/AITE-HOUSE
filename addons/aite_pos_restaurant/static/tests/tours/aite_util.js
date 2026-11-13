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
 * (« R3 »…) ; elle est fermée ensuite, pour qu'une vérification suivante ne
 * la retrouve pas. */
export function notificationDanger(cle) {
    return verifier(`notification ${cle}`, () => {
        for (const contenu of document.querySelectorAll(".o_notification_content")) {
            const notification = contenu.closest(".o_notification");
            if (
                contenu.textContent.trim() === message(cle) &&
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
