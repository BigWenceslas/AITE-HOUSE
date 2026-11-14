# -*- coding: utf-8 -*-
"""
Captures d'écran du parcours du restaurant (lot 1) — ce que voient la
caissière, la serveuse, le chef de salle et le manager.

Le parcours ouvre la caisse, sert la table 4, annule un produit envoyé avec
le code du chef de salle et encaisse : il ÉCRIT dans la base. Le jouer sur
une copie jetable de la base du restaurant (créée par
``dev/setup_env.sh --restaurant``, avec sa graine), caisse fermée :

    createdb -h localhost -U odoo -T aite_resto aite_resto_captures   # + copie du filestore
    ODOO_DB=aite_resto_captures dev/srv.sh start
    python3 tests/restaurant/shots.py                     # → captures/restaurant/
    ODOO_URL=http://localhost:8069 SHOTS_DIR=/tmp/shots python3 tests/restaurant/shots.py

Prérequis : ``pip install playwright`` ; le navigateur est Chrome
(``CHROME``, défaut /usr/bin/google-chrome), sinon celui de Playwright.

Comptes de la graine (mot de passe = identifiant) : « caisse » (la
tablette), « manager », et admin / admin. Codes : Clarisse 2001
(caissière), Brice 1001 et Nadège 1002 (serveurs), Hervé 3001 (chef de
salle).

Ce que le script fait de lui-même, et pourquoi :
- la Guinness 33 cl est ramenée à 0 en stock (inventaire, compte manager),
  pour montrer le refus d'un produit épuisé ;
- pour la capture du plan en couleurs, l'horloge de la PAGE est avancée de
  75 minutes (rien n'est écrit sur le serveur), comme le font les tours.

Règles apprises sur Odoo 18 (voir tests/vague1/shots.py) : jamais
``networkidle`` (long-polling), attendre un sélecteur ; à la connexion,
cliquer ``button[type=submit]:visible``. Les captures gardées dans le dépôt
sont prises à 1 280 × 800, deviceScaleFactor 2, en JPEG (poids raisonnable).
"""
import json
import os
import re
import sys

from playwright.sync_api import sync_playwright

BASE = os.environ.get("ODOO_URL", "http://localhost:8069")
OUT = os.environ.get("SHOTS_DIR", os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "captures", "restaurant"))
CHROME = os.environ.get("CHROME", "/usr/bin/google-chrome")
QUALITE = int(os.environ.get("SHOTS_JPEG_QUALITY", "78"))
os.makedirs(OUT, exist_ok=True)

POPUP = ".modal:not(.o_inactive_modal) .aite-code-popup"
ANNULATION = ".modal:not(.o_inactive_modal) .aite-annulation-popup"
erreurs_js = []


def connexion(contexte, login, mot_de_passe=None):
    page = contexte.new_page()
    page.on("pageerror", lambda e: erreurs_js.append("%s : %s" % (login, e)))
    page.goto(BASE + "/web/login", wait_until="domcontentloaded")
    page.fill("input[name=login]", login)
    page.fill("input[name=password]", mot_de_passe or login)
    # Avec le module Site web, la page porte d'autres boutons « submit » cachés.
    page.click("button[type=submit]:visible")
    page.wait_for_selector(".o_navbar, .o_home_menu, .o_action_manager, .o_main_navbar",
                           timeout=45000)
    return page


def capture(page, nom, attendre=800):
    page.wait_for_timeout(attendre)
    chemin = os.path.join(OUT, nom + ".jpg")
    page.screenshot(path=chemin, type="jpeg", quality=QUALITE)
    print("  📸", nom)


def rpc(page, modele, methode, args, kwargs=None):
    """Un appel JSON-RPC au serveur, sous le compte de la page."""
    reponse = page.evaluate(
        """async ([modele, methode, args, kwargs]) => {
            const r = await fetch('/web/dataset/call_kw', {method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({jsonrpc: '2.0', method: 'call',
                    params: {model: modele, method: methode, args, kwargs}})});
            return await r.json();
        }""", [modele, methode, args, kwargs or {}])
    if reponse.get("error"):
        raise RuntimeError(json.dumps(reponse["error"].get("data", {}).get("message")))
    return reponse.get("result")  # Odoo n'écrit pas « result » quand la méthode rend None


# ------------------------------------------------------------- la caisse
def taper_code(page, code, fenetre=POPUP):
    page.wait_for_selector(fenetre + " .aite-code-pave")
    for chiffre in code:
        page.click('%s [data-aite-chiffre="%s"]' % (fenetre, chiffre))


def table(page, numero):
    return page.locator(".floor-map .table").filter(
        has=page.locator(".label", has_text=re.compile(r"^\s*%s\s*$" % numero)))


def ouvrir_table(page, numero, code, personnes=None):
    table(page, numero).click()
    taper_code(page, code)
    if personnes:
        page.click('%s [data-aite-personnes="%s"]' % (POPUP, personnes))
    page.wait_for_selector(".pos .product-screen")


def produit(page, nom):
    page.locator("article.product .product-name", has_text=nom).first.click()


def familles(page, *chemin):
    """Toucher les familles de la carte, de la racine à la sous-famille
    (« Boisson », « Alcoolisé », « Bière ») ; toucher la famille déjà
    choisie remonterait d'un niveau : le chemin commence toujours par une
    famille racine qui n'est pas la famille choisie."""
    for nom in chemin:
        page.locator(".product-screen .category-button",
                     has_text=re.compile(r"^\s*%s\s*$" % re.escape(nom))).first.click()
        page.wait_for_timeout(400)


def plan(page):
    page.wait_for_selector(".floor-screen .floor-map")
    page.wait_for_selector(".floor-screen .aite-plan-etat")


def parcours_caisse(navigateur, config_id):
    contexte = navigateur.new_context(viewport={"width": 1280, "height": 800},
                                      device_scale_factor=2, locale="fr-FR")
    page = connexion(contexte, "caisse")
    # Point de Vente → « Restaurant » → Ouvrir la caisse (le bouton du tableau
    # de bord fait cet appel), puis la caisse.
    rpc(page, "pos.config", "open_ui", [[config_id]])
    page.goto(BASE + "/pos/ui?config_id=%d" % config_id, wait_until="domcontentloaded")

    # 1. Le matin : la fenêtre du code s'ouvre d'elle-même.
    page.wait_for_selector(POPUP + " .aite-code-pave", timeout=60000)
    capture(page, "01_ouverture_code_de_la_caissiere")
    taper_code(page, "2001")
    page.wait_for_selector(".modal .opening-cash-control, .modal .modal-footer .btn-primary")
    capture(page, "02_ouverture_j_ouvre_la_caisse")
    page.click(".modal:not(.o_inactive_modal) .modal-footer .btn-primary")
    plan(page)
    capture(page, "03_plan_verrouille", attendre=1500)

    # 2. Brice ouvre la table 4 : son code, puis les personnes.
    table(page, 4).click()
    page.wait_for_selector(POPUP + " .aite-code-pave")
    capture(page, "04_table_4_votre_code")
    taper_code(page, "1001")
    page.wait_for_selector(POPUP + ' [data-aite-personnes="8"]')
    capture(page, "05_table_4_combien_de_personnes")
    page.click(POPUP + ' [data-aite-personnes="4"]')
    page.wait_for_selector(".pos .product-screen .aite-commande-etat")
    # La carte en familles : Boisson > Alcoolisé > Bière.
    familles(page, "Boisson", "Alcoolisé", "Bière")
    produit(page, "Castel 65 cl")
    produit(page, "Castel 65 cl")
    capture(page, "06_ecran_de_commande_familles", attendre=1000)
    familles(page, "Nourriture", "Pizzas")
    produit(page, "Pizza Margherita")
    page.click(".actionpad .submit-order")  # « J'envoie »
    plan(page)
    page.wait_for_selector(".o_notification_content")
    capture(page, "07_apres_j_envoie_plan_verrouille", attendre=600)

    # 3. Nadège ouvre la table 7 ; le plan en couleurs (horloge de la page
    # avancée de 75 minutes, rien n'est écrit sur le serveur).
    ouvrir_table(page, 7, "1002", personnes="2")
    familles(page, "Boisson", "Non alcoolisé", "Café")
    produit(page, "Café expresso")
    page.click(".actionpad .submit-order")
    plan(page)
    page.evaluate("""() => {
        const { DateTime } = luxon;
        window.__aiteNow = DateTime.now;
        const instant = DateTime.now().plus({ minutes: 75 }).toMillis();
        DateTime.now = () => DateTime.fromMillis(instant);
        posmodel.aiteTic();
    }""")
    page.wait_for_selector('.floor-map .table[data-aite-alerte="orange"]')
    capture(page, "08_plan_en_couleurs", attendre=1200)
    page.evaluate("() => { luxon.DateTime.now = window.__aiteNow; posmodel.aiteTic(); }")

    # 4. Brice revient à la table 4 : un produit épuisé est refusé.
    ouvrir_table(page, 4, "1001")
    familles(page, "Boisson", "Alcoolisé", "Bière")
    produit(page, "Guinness 33 cl")
    page.wait_for_selector(".o_notification_title")
    capture(page, "09_produit_epuise", attendre=500)
    page.locator(".o_notification_close").first.click()

    # 5. Une Castel envoyée est annulée : Brice touche la ligne, ⌫ ⌫, puis
    # Hervé (chef de salle) tape son code et touche le motif.
    page.locator(".order-container .orderline", has=page.locator(
        ".product-name", has_text="Castel")).first.click()
    for _ in range(2):
        page.locator('div.numpad button[value="⌫"]').first.click()
        page.wait_for_timeout(300)
    page.wait_for_selector(ANNULATION + " .aite-annulation-quantites")
    capture(page, "10_annulation_combien")
    page.click(ANNULATION + ' [data-aite-quantite="1"]')
    taper_code(page, "3001", fenetre=ANNULATION)
    page.wait_for_selector(ANNULATION + " .aite-annulation-motifs")
    capture(page, "11_annulation_pourquoi")
    page.locator(ANNULATION + " .aite-annulation-motifs [data-aite-motif-id]").nth(1).click()
    page.wait_for_selector("body:not(:has(.aite-annulation-popup))")
    page.wait_for_selector(".o_notification_content")
    capture(page, "12_annulation_faite_brice_reste_identifie", attendre=600)

    # 6. Clarisse encaisse la table 4 en espèces.
    page.click(".pos-leftheader .back-button")  # « Plan »
    plan(page)
    ouvrir_table(page, 4, "2001")
    page.click(".actionpad .pay-order-button")  # « J'encaisse »
    page.wait_for_selector(".pos .payment-screen .paymentmethod")
    page.locator(".paymentmethods .paymentmethod .payment-name", has_text="Espèces").click()
    capture(page, "13_paiement_especes", attendre=800)
    page.click(".payment-screen button.validation-button.next")
    plan(page)

    # 7. Le soir : Hervé ferme la caisse (la table 7 est encore ouverte).
    page.click(".pos-rightheader button:has(.fa-bars)")
    page.locator(".pos-burger-menu-items span.dropdown-item", has_text="Fermer la caisse").click()
    taper_code(page, "3001")
    page.wait_for_selector(".modal .close-pos-popup")
    # Les espèces comptées : ce que la caissière a encaissé (aucun écart).
    page.fill(".modal .close-pos-popup .cash-input input", "6000")
    capture(page, "14_fermeture_de_la_caisse", attendre=1000)
    page.click(".modal .close-pos-popup button.highlight.btn-primary")  # « Fermer la caisse »
    # La table 7 est encore ouverte : notre message, « Annuler ces tables ».
    page.wait_for_selector(".modal:not(.o_inactive_modal) .modal-footer .btn-secondary")
    capture(page, "15_fermeture_une_table_encore_ouverte", attendre=800)
    page.click(".modal:not(.o_inactive_modal) .modal-footer .btn-secondary")
    page.wait_for_selector(ANNULATION + " .aite-annulation-motifs")
    capture(page, "16_fermeture_annuler_ces_tables", attendre=600)
    # Le code d'Hervé est déjà tapé : le motif seul ; la caisse se ferme et
    # la page se recharge (une nouvelle session attend le code d'ouverture).
    page.locator(ANNULATION + " .aite-annulation-motifs [data-aite-motif-id]").nth(1).click()
    page.wait_for_selector(POPUP + " .aite-code-pave", timeout=60000)
    contexte.close()


# ------------------------------------------------------------ la gestion
def gestion(navigateur):
    contexte = navigateur.new_context(viewport={"width": 1280, "height": 800},
                                      device_scale_factor=2, locale="fr-FR")
    page = connexion(contexte, "manager")

    def ouvrir(xmlid, attendre, extra=""):
        page.goto(BASE + "/odoo/action-%s%s" % (xmlid, extra), wait_until="domcontentloaded")
        page.wait_for_selector(attendre, timeout=30000)

    ouvrir("aite_pos_restaurant.action_personnes_tables", ".o_pivot, .o_view_nocontent")
    capture(page, "20_personnes_et_tables", attendre=1500)
    page.click(".o_switch_view.o_list")
    page.wait_for_selector(".o_list_view")
    capture(page, "21_personnes_et_tables_liste", attendre=1200)
    ouvrir("aite_pos_restaurant.action_restaurant_annulation", ".o_list_view, .o_view_nocontent")
    capture(page, "22_annulations_du_jour", attendre=1500)
    ouvrir("aite_pos_analytics.action_pos_daily_report", ".o_pivot, .o_view_nocontent")
    page.click(".o_searchview_dropdown_toggler")
    page.locator(".o_favorite_menu .o_menu_item, .o_favorite_menu span",
                 has_text="Ventes par famille").first.click()
    page.keyboard.press("Escape")
    capture(page, "23_ventes_par_famille", attendre=1800)
    # Le rapport de fermeture de la session (tables, personnes, annulations).
    session = rpc(page, "pos.session", "search", [[("state", "=", "closed")]],
                  {"order": "id desc", "limit": 1})
    page.goto(BASE + "/report/html/point_of_sale.report_saledetails/%d" % session[0],
              wait_until="domcontentloaded")
    page.wait_for_selector("body")
    page.get_by_text("Nombre de tables").first.scroll_into_view_if_needed()
    capture(page, "26_rapport_de_fermeture", attendre=1200)
    # La fiche de Brice : niveau et code sur la première page.
    employe = rpc(page, "hr.employee", "search", [[("name", "=", "Brice")]])
    page.goto(BASE + "/odoo/employees/%d" % employe[0], wait_until="domcontentloaded")
    page.wait_for_selector(".o_form_view [name=aite_niveau_caisse]")
    capture(page, "24_fiche_employe_niveau_et_code", attendre=1200)
    contexte.close()


def reglages(navigateur):
    """Le bloc Restaurant des réglages du Point de Vente (administrateur)."""
    contexte = navigateur.new_context(viewport={"width": 1280, "height": 800},
                                      device_scale_factor=2, locale="fr-FR")
    page = connexion(contexte, "admin", "admin")
    page.goto(BASE + "/odoo/action-point_of_sale.action_pos_configuration",
              wait_until="domcontentloaded")
    page.wait_for_selector("#aite_mode_restaurant", timeout=30000)
    page.locator("#aite_mode_restaurant").scroll_into_view_if_needed()
    page.evaluate("() => document.querySelector('#aite_mode_restaurant').scrollIntoView({block: 'start'})")
    capture(page, "25_reglages_service_a_table_controle", attendre=1200)
    contexte.close()


def preparer(navigateur):
    """La Guinness 33 cl à 0 en stock (inventaire, compte manager) ; rend
    l'identifiant de la caisse « Restaurant »."""
    contexte = navigateur.new_context(locale="fr-FR")
    page = connexion(contexte, "manager")
    config = rpc(page, "pos.config", "search_read",
                 [[("aite_mode_restaurant", "=", True)]], {"fields": ["id", "current_session_id"]})
    if not config or config[0]["current_session_id"]:
        raise SystemExit("✗ la caisse « Restaurant » doit exister et être fermée")
    produit_id = rpc(page, "product.product", "search", [[("name", "=", "Guinness 33 cl")]])
    quants = rpc(page, "stock.quant", "search_read",
                 [[("product_id", "in", produit_id), ("location_id.usage", "=", "internal")]],
                 {"fields": ["id"]})
    if quants:
        ids = [q["id"] for q in quants]
        rpc(page, "stock.quant", "write", [ids, {"inventory_quantity": 0}],
            {"context": {"inventory_mode": True}})
        rpc(page, "stock.quant", "action_apply_inventory", [ids])
    contexte.close()
    return config[0]["id"]


# Les réglages d'abord : dès qu'une tablette a ouvert la caisse (même une
# session en attente d'ouverture), Odoo grise la case du service à table.
ETAPES = [reglages, parcours_caisse, gestion]


def main():
    with sync_playwright() as p:
        navigateur = p.chromium.launch(
            executable_path=CHROME if os.path.exists(CHROME) else None)
        echecs = 0
        try:
            config_id = preparer(navigateur)
            for etape in ETAPES:
                try:
                    etape(navigateur, config_id) if etape is parcours_caisse else etape(navigateur)
                except Exception as e:  # noqa: BLE001
                    echecs += 1
                    print("  ✗ étape %s échouée : %s" % (etape.__name__, str(e)[:300]))
        finally:
            navigateur.close()
        print("captures dans", os.path.abspath(OUT), "— étapes en échec :", echecs,
              "— erreurs JS :", len(erreurs_js))
        for e in erreurs_js:
            print("   JS :", e[:200])
        return echecs or bool(erreurs_js)


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
