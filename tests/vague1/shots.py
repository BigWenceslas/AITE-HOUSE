# -*- coding: utf-8 -*-
"""
Captures d'écran des parcours — ce que voit réellement l'utilisateur.

Usage (serveur démarré, base avec le jeu de données dev/seeds/) :
    python3 tests/vague1/shots.py              # toutes les captures standard
    ODOO_URL=http://localhost:8069 SHOTS_DIR=/tmp/shots python3 tests/vague1/shots.py

Règles apprises sur Odoo 18 :
- ne JAMAIS attendre ``networkidle`` (le long-polling ne s'arrête pas) :
  attendre un sélecteur puis un court délai ;
- les écrans s'ouvrent par ``/odoo/action-<module>.<xml_id>`` ;
- une vue « téléphone » = viewport 390×844.
"""
import os
import sys

from playwright.sync_api import sync_playwright

BASE = os.environ.get("ODOO_URL", "http://localhost:8069")
OUT = os.environ.get("SHOTS_DIR", os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "captures", "nouvelles"))
LOGIN = os.environ.get("ODOO_LOGIN", "admin")
PASSWORD = os.environ.get("ODOO_PASSWORD", "admin")
CHROMIUM = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
os.makedirs(OUT, exist_ok=True)


def login(page, user=LOGIN, password=PASSWORD):
    page.goto(BASE + "/web/login", wait_until="domcontentloaded")
    page.fill("input[name=login]", user)
    page.fill("input[name=password]", password)
    page.click("button[type=submit]")
    page.wait_for_selector(".o_navbar, .o_home_menu, .o_action_manager",
                           timeout=45000)


def shot(page, url, name, wait_selector=None, settle=1500, full=False):
    page.goto(BASE + url, wait_until="domcontentloaded")
    page.wait_for_selector(wait_selector or ".o_action_manager", timeout=30000)
    page.wait_for_timeout(settle)
    page.screenshot(path=f"{OUT}/{name}.png", full_page=full)
    print("  📸", name)


def action(xmlid, extra=""):
    return f"/odoo/action-{xmlid}{extra}"


# ---------------------------------------------------------------- étapes
def step_taxe(page):
    shot(page, action("aite_hotel_management.action_hotel_hotel"), "01_hotels_liste",
         ".o_list_view, .o_kanban_view")
    shot(page, action("aite_city_tax.action_city_tax_report"), "04_etat_mensuel_pivot",
         ".o_pivot, .o_view_nocontent")
    shot(page, action("aite_city_tax.action_city_tax_rate"), "05_baremes",
         ".o_list_view")


def step_registre(page):
    shot(page, action("aite_hotel_management.action_hotel_inhouse"), "10_clients_presents",
         ".o_list_view, .o_kanban_view, .o_view_nocontent")
    shot(page, action("aite_guest_registry.action_guest_registration"), "13_registre_liste",
         ".o_list_view, .o_view_nocontent")
    shot(page, action("aite_guest_registry.action_guest_stats"), "14_stats_pivot",
         ".o_pivot, .o_view_nocontent")


def step_gouvernante(page):
    shot(page, action("aite_housekeeping.action_room_board"), "30_tableau_chambres",
         ".o_kanban_view")
    shot(page, action("aite_housekeeping.action_room_maintenance"), "33_pannes",
         ".o_kanban_view, .o_view_nocontent")
    shot(page, action("aite_housekeeping.action_lost_found"), "35_objets_trouves",
         ".o_list_view, .o_view_nocontent")


def step_mobile(page):
    """« Ma journée » telle que la voit une équipière sur son téléphone."""
    page.set_viewport_size({"width": 390, "height": 844})
    shot(page, action("aite_housekeeping.action_my_day"), "31_ma_journee_mobile",
         ".o_kanban_view, .o_view_nocontent", settle=2000)
    page.set_viewport_size({"width": 1440, "height": 900})


def step_indicateurs(page):
    """F06 — RevPAR, pickup, pace : tableau exécutif et cockpit Direction."""
    shot(page, action("aite_exec_dashboard.action_aite_exec_dashboard"),
         "40_tableau_executif_indicateurs", ".aed-kpi-help", settle=3000)
    shot(page, action("aite_direction_dashboard.action_direction_dashboard"),
         "41_cockpit_direction_hebergement", ".add-help", settle=3000)


STEPS = [step_taxe, step_registre, step_gouvernante, step_mobile,
         step_indicateurs]


def main(steps=STEPS):
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=CHROMIUM if os.path.exists(CHROMIUM) else None)
        ctx = browser.new_context(viewport={"width": 1440, "height": 900},
                                  locale="fr-FR")
        page = ctx.new_page()
        login(page)
        failed = 0
        for s in steps:
            try:
                s(page)
            except Exception as e:  # noqa: BLE001
                failed += 1
                print("  ✗ étape %s échouée : %s" % (s.__name__, str(e)[:160]))
        browser.close()
        print("captures dans", os.path.abspath(OUT), "— étapes en échec :", failed)
        return failed


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
