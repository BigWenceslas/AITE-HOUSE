# -*- coding: utf-8 -*-
"""
Harnais des scénarios UAT — pilotage d'un vrai navigateur.

Les scénarios de recette s'exécutent dans Chromium via Playwright, avec
les **profils utilisateurs réels** du jeu d'essai (réception,
gouvernante, caisse, magasin, direction). Chaque étape produit une
capture d'écran numérotée, reprise telle quelle dans les guides de test.

Lancement :

    python tests_uat/run_uat.py [--url http://127.0.0.1:8069] [--headed]
"""
import json
import os
import re
import time
import unicodedata
from dataclasses import dataclass, field

BASE_URL = os.environ.get('AITE_UAT_URL', 'http://127.0.0.1:8069')
SHOTS_DIR = os.environ.get(
    'AITE_UAT_SHOTS',
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 '..', 'documentation', 'captures'))

# Profils du jeu d'essai : (login, mot de passe, libellé métier).
USERS = {
    'admin': ('admin', 'admin', "Administrateur"),
    'reception': ('demo.reception', 'demo.reception', "Réception"),
    'housekeeping': ('demo.gouvernante', 'demo.gouvernante', "Gouvernante"),
    'cashier': ('demo.caisse', 'demo.caisse', "Caisse"),
    'stock': ('demo.magasin', 'demo.magasin', "Magasin"),
    'manager': ('demo.direction', 'demo.direction', "Direction"),
}


def slugify(text):
    """Nom de fichier sûr à partir d'un libellé français."""
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii', 'ignore').decode('ascii')
    text = re.sub(r'[^a-zA-Z0-9]+', '-', text).strip('-').lower()
    return text or 'etape'


@dataclass
class Step:
    """Une étape de recette : ce qu'on a fait, ce qu'on a constaté."""
    number: int
    title: str
    expected: str
    observed: str
    screenshot: str
    status: str  # 'OK' | 'KO'
    detail: str = ""


@dataclass
class Scenario:
    """Un scénario UAT joué par un profil métier."""
    key: str
    title: str
    persona: str
    goal: str
    steps: list = field(default_factory=list)

    @property
    def status(self):
        return 'KO' if any(s.status == 'KO' for s in self.steps) else 'OK'

    def as_dict(self):
        return {
            'key': self.key,
            'title': self.title,
            'persona': self.persona,
            'goal': self.goal,
            'status': self.status,
            'steps': [vars(s) for s in self.steps],
        }


class UatSession:
    """
    Une session de recette : un navigateur, un utilisateur, des étapes.

    L'API est volontairement proche du geste humain — ``open``,
    ``click_menu``, ``fill``, ``shoot`` — pour que le script se lise
    comme le cahier de recette qu'il produit.
    """

    def __init__(self, page, scenario, shots_dir=SHOTS_DIR,
                 base_url=BASE_URL):
        self.page = page
        self.scenario = scenario
        self.shots_dir = os.path.abspath(shots_dir)
        self.base_url = base_url.rstrip('/')
        os.makedirs(self.shots_dir, exist_ok=True)
        self._counter = 0

    # ------------------------------------------------------------------
    # Authentification
    # ------------------------------------------------------------------

    def login(self, user_key):
        login, password, label = USERS[user_key]
        page = self.page
        # Toujours repartir d'une session vierge : connecté, Odoo remplace
        # le formulaire par un panneau « déjà connecté » dont les champs
        # sont présents mais masqués.
        page.goto('%s/web/session/logout' % self.base_url,
                  wait_until='domcontentloaded')
        page.goto('%s/web/login' % self.base_url,
                  wait_until='domcontentloaded')
        # Le module Website ajoute ses propres boutons « submit » à la
        # page : on reste donc à l'intérieur du formulaire de connexion.
        form = page.locator('form.oe_login_form').first
        if not form.count():
            form = page.locator('form:has(input[name="password"])').first
        # Odoo 18 mémorise les comptes déjà utilisés et masque le
        # formulaire (« d-none ») derrière un sélecteur de comptes : on
        # le déplie comme le ferait l'utilisateur.
        if not form.locator('input[name="login"]').first.is_visible():
            for label in ("autre compte", "another account",
                          "autre utilisateur", "another user"):
                link = page.locator(
                    'a:has-text("%s"), button:has-text("%s")'
                    % (label, label))
                if link.count():
                    link.first.click()
                    page.wait_for_timeout(400)
                    break
            else:
                # Dernier recours : retirer la classe qui masque le bloc.
                page.evaluate(
                    "document.querySelectorAll('form.oe_login_form')"
                    ".forEach(f => f.classList.remove('d-none'))")
                page.wait_for_timeout(200)
        form.locator('input[name="login"]').fill(login)
        form.locator('input[name="password"]').fill(password)
        form.locator('button[type="submit"]').first.click()
        # Le client web d'Odoo maintient un canal ouvert en permanence :
        # attendre « networkidle » ne rendrait jamais la main. On attend
        # donc la barre de navigation du back-office.
        try:
            page.wait_for_selector('.o_main_navbar', timeout=30000)
        except Exception:  # noqa: BLE001
            page.wait_for_timeout(2000)
        self.settle()
        return label

    def logout(self):
        self.page.goto('%s/web/session/logout' % self.base_url,
                       wait_until='domcontentloaded')

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    def open_action(self, xmlid):
        """Ouvre une action par son identifiant externe (comme un menu)."""
        self.page.goto('%s/odoo/action-%s' % (self.base_url, xmlid),
                       wait_until='domcontentloaded')
        self.settle()

    def open_url(self, path):
        self.page.goto('%s%s' % (self.base_url, path),
                       wait_until='domcontentloaded')
        self.settle()

    def settle(self, timeout=20000):
        """
        Attend que l'écran soit stable.

        ``networkidle`` est inutilisable ici : le bus d'Odoo garde une
        requête ouverte en permanence. On attend donc la disparition de
        l'indicateur de chargement, puis on laisse les graphiques
        Chart.js terminer leur animation.
        """
        page = self.page
        try:
            page.wait_for_load_state('domcontentloaded', timeout=timeout)
        except Exception:  # noqa: BLE001
            pass
        for selector in ('.o_loading_indicator', '.o_blockUI'):
            try:
                page.wait_for_selector(selector, state='hidden',
                                       timeout=3000)
            except Exception:  # noqa: BLE001
                pass
        time.sleep(1.2)

    # ------------------------------------------------------------------
    # Constat & capture
    # ------------------------------------------------------------------

    def shoot(self, title, expected, observed=None, ok=True, detail="",
              full_page=True):
        """Consigne une étape et capture l'écran."""
        self._counter += 1
        name = '%s-%02d-%s.png' % (
            self.scenario.key, self._counter, slugify(title))
        path = os.path.join(self.shots_dir, name)
        try:
            self.page.screenshot(path=path, full_page=full_page)
        except Exception as exc:  # noqa: BLE001
            detail = (detail + " | capture impossible : %s" % exc).strip()
            name = ""
        self.scenario.steps.append(Step(
            number=self._counter,
            title=title,
            expected=expected,
            observed=observed if observed is not None else expected,
            screenshot=name,
            status='OK' if ok else 'KO',
            detail=detail,
        ))
        return path

    def check(self, title, expected, condition, observed_ok, observed_ko,
              detail=""):
        """Capture + verdict en une seule opération."""
        ok = bool(condition)
        return self.shoot(
            title, expected,
            observed=observed_ok if ok else observed_ko,
            ok=ok, detail=detail)

    # ------------------------------------------------------------------
    # Lectures d'écran
    # ------------------------------------------------------------------

    def text(self):
        try:
            return self.page.inner_text('body')
        except Exception:  # noqa: BLE001
            return ""

    def has(self, needle):
        return needle.lower() in self.text().lower()

    def count(self, selector):
        try:
            return self.page.locator(selector).count()
        except Exception:  # noqa: BLE001
            return 0


def save_report(scenarios, path):
    """Écrit le rapport machine des scénarios joués."""
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    payload = {
        'generated_at': time.strftime('%Y-%m-%d %H:%M'),
        'base_url': BASE_URL,
        'scenarios': [s.as_dict() for s in scenarios],
    }
    with open(path, 'w', encoding='utf-8') as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
    return path
