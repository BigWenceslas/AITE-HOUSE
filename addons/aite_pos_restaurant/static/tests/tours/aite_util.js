/* global posmodel, odoo, luxon */
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

// ----------------------------------------------------------------------
// Incrément 5 : le plan en couleurs, les produits épuisés
// ----------------------------------------------------------------------

/** La table `numero` sur le plan (l'élément `.table` dont le numéro est
 * `numero`). */
function tableDuPlan(numero) {
    return [...document.querySelectorAll(".floor-screen .floor-map .table")].find(
        (el) => el.querySelector(".label")?.textContent.trim() === String(numero)
    );
}

/** Les couleurs attendues à l'écran (feuille de style d'AITE, `!important`
 * sur le style en ligne d'Odoo). */
const FONDS = { vert: "rgb(53, 211, 116)", orange: "rgb(255, 152, 0)" };

/** La table `numero` porte l'alerte `attendu` (« libre », « vert »,
 * « orange ») ; pour une table ouverte, la couleur affichée est bien celle de
 * l'alerte. */
export function couleurDeLaTable(numero, attendu) {
    return verifier(`la table ${numero} est « ${attendu} »`, () => {
        const el = tableDuPlan(numero);
        if (!el) {
            return "table absente du plan";
        }
        const alerte = el.dataset.aiteAlerte;
        const fond = getComputedStyle(el).backgroundColor;
        if (alerte !== attendu) {
            return `alerte ${alerte}`;
        }
        return !FONDS[attendu] || fond === FONDS[attendu] || `fond ${fond}`;
    });
}

/** La durée écrite sous le numéro de la table : `attendu` (un texte, ou
 * `texte("duree", m)`), ou aucune durée si `attendu` est vide. */
export function dureeDeLaTable(numero, attendu) {
    return verifier(`la durée de la table ${numero}`, () => {
        const el = tableDuPlan(numero);
        const duree = el?.querySelector(".aite-duree")?.textContent.trim() || "";
        return duree === (valeur(attendu) || "") || JSON.stringify(duree);
    });
}

/** L'horloge de la caisse avancée à `minutes` (un nombre, ou une fonction
 * appelée au moment de l'étape) après l'ouverture de la table `numero`, posée
 * par le serveur ; puis le tic de la minuterie du plan (`posmodel.aiteTic()`,
 * appelé toutes les 30 secondes à l'écran). L'horloge est celle de luxon,
 * comme `freezeDateTime` d'Odoo. */
export function avancerLHorloge(numero, minutes) {
    return {
        content: `horloge avancée après l'ouverture de la table ${numero}`,
        trigger: "body",
        run() {
            const { DateTime } = luxon;
            const table = posmodel.models["restaurant.table"].find(
                (t) => String(t.table_number) === String(numero)
            );
            const heure = table?.getOrder()?.aite_heure_ouverture;
            if (!heure) {
                throw new Error(`la table ${numero} n'a pas d'heure d'ouverture`);
            }
            const debut =
                typeof heure === "string" ? DateTime.fromSQL(heure, { zone: "utc" }) : heure;
            const instant = debut.plus({ minutes: valeur(minutes), seconds: 10 }).toMillis();
            DateTime.now = () => DateTime.fromMillis(instant);
            posmodel.aiteTic();
        },
    };
}

/** La légende du plan, avec le délai de la caisse. */
export function legende() {
    return verifier("la légende du plan", () => {
        const modele = odoo.loader.modules.get("@aite_pos_restaurant/utils/messages").TEXTES;
        const attendu = modele.legende(posmodel.config.aite_delai_alerte);
        const lu = document.querySelector(".floor-screen .aite-legende")?.textContent;
        const net = (t) => (t || "").replace(/\s+/g, " ").trim();
        return net(lu) === net(attendu) || JSON.stringify(lu);
    });
}

/** R11 : notification « danger » titrée « Produit épuisé » pour `produit` ;
 * elle est fermée ensuite. */
export function produitEpuise(produit) {
    return verifier(`« Produit épuisé » : ${typeof produit === "function" ? "variante" : produit}`, () => {
        const messages = odoo.loader.modules.get("@aite_pos_restaurant/utils/messages");
        const attendu = messages.MESSAGES.R11(valeur(produit));
        for (const contenu of document.querySelectorAll(".o_notification_content")) {
            const notification = contenu.closest(".o_notification");
            const titre = notification.querySelector(".o_notification_title")?.textContent.trim();
            if (
                contenu.textContent.trim() === attendu &&
                titre === messages.TITRES.produitEpuise &&
                notification.querySelector(".o_notification_bar.bg-danger")
            ) {
                notification.querySelector(".o_notification_close")?.click();
                return true;
            }
        }
        return [...document.querySelectorAll(".o_notification")].map((n) => n.textContent).join(" | ");
    });
}

/** Aucune ligne du produit `nom` sur l'addition. */
export function pasDeLigne(nom) {
    return verifier(`aucune ligne ${nom}`, () =>
        !posmodel.get_order()?.lines.some((l) => l.get_product().name === nom) || "ligne présente"
    );
}

// Revue de l'incrément 5 : les gestes qui ajoutent, les variantes, la note.

/** Aucune notification « Produit épuisé » n'est affichée. */
export function pasDeProduitEpuise() {
    return verifier("pas de « Produit épuisé »", () => {
        const titre = odoo.loader.modules.get("@aite_pos_restaurant/utils/messages").TITRES
            .produitEpuise;
        const titres = [...document.querySelectorAll(".o_notification_title")].map((t) =>
            t.textContent.trim()
        );
        return !titres.includes(titre) || "R11 affiché";
    });
}

/** La variante de `nom` dont le nom affiché contient `variante` (« 50 cl »). */
export function variante(nom, variante) {
    return posmodel.models["product.product"].find(
        (p) => p.name === nom && p.display_name.includes(variante)
    );
}

/** Les lignes de l'addition, en texte : « Jus (50 cl) × 1 | … ». */
function lignes() {
    return (posmodel.get_order()?.lines || [])
        .map((l) => `${l.get_product().display_name} × ${l.get_quantity()} [${l.getNote()}]`)
        .join(" | ");
}

/** La variante `variante` de `nom` est sur l'addition, à `quantite`
 * (0 : absente). */
export function quantiteDeLaVariante(nom, variante_, quantite) {
    return verifier(`${nom} ${variante_} à ${quantite}`, () => {
        const produit = variante(nom, variante_);
        const total = (posmodel.get_order()?.lines || [])
            .filter((l) => l.get_product().id === produit?.id)
            .reduce((somme, l) => somme + l.get_quantity(), 0);
        return total === quantite || lignes();
    });
}

/** « Note cuisine » de la rangée principale (le bouton d'Odoo, reconnu à
 * son libellé traduit dans la langue de la page). */
export function noteCuisine() {
    return {
        content: "« Note cuisine »",
        trigger: ".product-screen .control-buttons button",
        run() {
            const libelle = _t("Kitchen Note");
            const bouton = [
                ...document.querySelectorAll(".product-screen .control-buttons button"),
            ].find((b) => b.textContent.trim() === libelle);
            if (!bouton) {
                throw new Error(`bouton « ${libelle} » absent`);
            }
            bouton.click();
        },
    };
}

/** Les lignes de `nom` : `attendu` est la liste des « quantité/note »
 * (« 1/ », « 1/bien fraîche »), dans n'importe quel ordre. */
export function lignesDuProduit(nom, attendu) {
    return verifier(`lignes ${nom} : ${attendu.join(", ")}`, () => {
        const lu = (posmodel.get_order()?.lines || [])
            .filter((l) => l.get_product().name === nom)
            .map((l) => `${l.get_quantity()}/${l.getNote() || ""}`)
            .sort();
        return JSON.stringify(lu) === JSON.stringify([...attendu].sort()) || lignes();
    });
}

/** Aucune fenêtre d'erreur d'Odoo (« Oups ! … »). */
export function pasDErreur() {
    return verifier("pas de fenêtre d'erreur", () =>
        !document.querySelector(".o_error_dialog, .modal .o_error_detail") || "erreur affichée"
    );
}
