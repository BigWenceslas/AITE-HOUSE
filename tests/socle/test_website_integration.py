# -*- coding: utf-8 -*-
"""
Tests d'intégration — aite_website_booking (D4).

Deux familles :
1. **Miroirs** : reproduction exacte des décisions du contrôleur
   (recherche client, garde des dates, conversion locale→UTC) validées
   sur cas concrets ;
2. **Contrats croisés** : lecture du code réel (contrôleur, modèles du
   moteur de créneaux, PMS) pour garantir que les valeurs écrites
   existent bien côté cible — le test casse si un contrat bouge.
"""
import ast
import re
import unittest
from datetime import datetime, timedelta

import pytz

import os
BASE = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "addons"))
CTRL = BASE + "/aite_website_booking/controllers/main.py"
TPL = BASE + "/aite_website_booking/views/website_templates.xml"
MANIFEST = BASE + "/aite_website_booking/__manifest__.py"
SLOT_BOOKING = BASE + "/aite_slot_booking/models/booking_booking.py"
SLOT_RESOURCE = BASE + "/aite_slot_booking/models/booking_resource.py"
PMS_RESA = (BASE + "/aite_hotel_management/models/"
            "hotel_reservation.py")


def _read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


# ----------------------------------------------------------------------
# 1. MIROIRS COMPORTEMENTAUX
# ----------------------------------------------------------------------

class FakePartnerPool:
    """Répertoire minimal pour rejouer la décision find_or_create."""

    def __init__(self, rows):
        self.rows = list(rows)      # dicts {id, phone, email}
        self.created = []

    def by_phone(self, phone_n):
        return next((r for r in self.rows if r["phone"] == phone_n), None)

    def by_email(self, email):
        e = (email or "").strip().lower()
        return next(
            (r for r in self.rows
             if (r.get("email") or "").lower() == e), None)

    def create(self, vals):
        row = dict(vals, id=100 + len(self.created))
        self.created.append(row)
        return row


def mirror_find_or_create(pool, norm_phone, name, phone, email):
    """Miroir exact de find_or_create_partner (ordre des recherches)."""
    phone_n = norm_phone(phone)
    partner = pool.by_phone(phone_n) if phone_n else None
    if not partner and email:
        partner = pool.by_email(email)
    if not partner:
        partner = pool.create({
            "name": str(name).strip(),
            "phone": phone_n or False,
            "email": (email or "").strip() or False,
        })
    return partner


def _norm_phone_real():
    """Récupère la vraie _norm_phone (même extraction que la suite logique)."""
    import textwrap
    code = _read(BASE + "/aite_website_booking/models/website_booking.py")
    m = re.search(
        r"^    def _norm_phone\(.*?(?=^    @staticmethod)", code, re.S | re.M)
    ns = {}
    exec(textwrap.dedent(m.group(0)), ns)
    return ns["_norm_phone"]


class TestFindOrCreateMirror(unittest.TestCase):
    def setUp(self):
        self.norm = _norm_phone_real()
        self.pool = FakePartnerPool([
            {"id": 1, "phone": "+224620123456", "email": "bah@ex.gn"},
            {"id": 2, "phone": "628999888", "email": ""},
        ])

    def test_retrouve_par_telephone_normalise(self):
        # Saisie avec espaces/tirets → même fiche (pas de doublon).
        p = mirror_find_or_create(
            self.pool, self.norm, "M. Bah", "+224 620-12-34-56", "")
        self.assertEqual(p["id"], 1)
        self.assertEqual(self.pool.created, [])

    def test_retrouve_par_email_si_telephone_inconnu(self):
        p = mirror_find_or_create(
            self.pool, self.norm, "Bah", "699000111", "BAH@ex.gn")
        self.assertEqual(p["id"], 1)

    def test_telephone_prioritaire_sur_email(self):
        # Le téléphone matche la fiche 2, l'email la fiche 1 → fiche 2.
        p = mirror_find_or_create(
            self.pool, self.norm, "X", "628 999 888", "bah@ex.gn")
        self.assertEqual(p["id"], 2)

    def test_creation_si_inconnu_avec_normalisation(self):
        p = mirror_find_or_create(
            self.pool, self.norm, "  Aïcha Diallo ", "621 00 11 22", "")
        self.assertEqual(len(self.pool.created), 1)
        self.assertEqual(p["name"], "Aïcha Diallo")
        self.assertEqual(p["phone"], "621001122")
        self.assertFalse(p["email"])

    def test_pas_de_recherche_telephone_vide(self):
        # Téléphone vide ne doit pas matcher une fiche au phone vide.
        self.pool.rows.append({"id": 3, "phone": "", "email": ""})
        p = mirror_find_or_create(
            self.pool, self.norm, "Sans Tel", "", "nouveau@ex.gn")
        self.assertEqual(len(self.pool.created), 1)


def mirror_room_dates_guard(checkin, checkout):
    """Miroir de la garde des dates du séjour (rooms_submit)."""
    try:
        if datetime.strptime(checkout, "%Y-%m-%d") <= \
                datetime.strptime(checkin, "%Y-%m-%d"):
            return "dates"
    except ValueError:
        return "dates"
    return ""


class TestRoomDatesGuard(unittest.TestCase):
    def test_sejour_valide(self):
        self.assertEqual(
            mirror_room_dates_guard("2026-08-01", "2026-08-03"), "")

    def test_checkout_avant_checkin(self):
        self.assertEqual(
            mirror_room_dates_guard("2026-08-03", "2026-08-01"), "dates")

    def test_meme_jour_refuse(self):
        self.assertEqual(
            mirror_room_dates_guard("2026-08-01", "2026-08-01"), "dates")

    def test_format_invalide(self):
        self.assertEqual(mirror_room_dates_guard("2026-08-01", ""), "dates")
        self.assertEqual(
            mirror_room_dates_guard("2026-08-01", "01/08/2026"), "dates")


def mirror_local_to_utc(day_str, hour_float, tzname):
    """Miroir de _local_to_utc du contrôleur."""
    day = datetime.strptime(day_str, "%Y-%m-%d")
    hh = int(hour_float)
    mm = int(round((hour_float - hh) * 60))
    naive = day.replace(hour=hh, minute=mm)
    localized = pytz.timezone(tzname).localize(naive)
    return localized.astimezone(pytz.utc).replace(tzinfo=None)


class TestLocalToUtcMirror(unittest.TestCase):
    def test_conakry_utc_plus_zero(self):
        dt = mirror_local_to_utc("2026-08-01", 18.5, "Africa/Conakry")
        self.assertEqual(dt, datetime(2026, 8, 1, 18, 30))

    def test_douala_utc_plus_un(self):
        dt = mirror_local_to_utc("2026-08-01", 18.5, "Africa/Douala")
        self.assertEqual(dt, datetime(2026, 8, 1, 17, 30))

    def test_demi_heure_et_arrondi_minutes(self):
        dt = mirror_local_to_utc("2026-08-01", 9.25, "Africa/Conakry")
        self.assertEqual((dt.hour, dt.minute), (9, 15))

    def test_duree_prestation_ajoutee_apres_conversion(self):
        start = mirror_local_to_utc("2026-08-01", 10.0, "Africa/Douala")
        stop = start + timedelta(minutes=90)
        self.assertEqual(stop, datetime(2026, 8, 1, 10, 30))


# ----------------------------------------------------------------------
# 2. CONTRATS CROISÉS SUR LE CODE RÉEL
# ----------------------------------------------------------------------

class TestCrossContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ctrl = _read(CTRL)
        cls.slot_bk = _read(SLOT_BOOKING)
        cls.slot_rs = _read(SLOT_RESOURCE)
        cls.pms = _read(PMS_RESA)
        cls.tpl = _read(TPL)

    def test_source_online_existe_dans_slot_booking(self):
        self.assertIn("'source': 'online'", self.ctrl)
        self.assertIn("('online', ", self.slot_bk)

    def test_source_website_existe_dans_pms(self):
        self.assertIn("'source': 'website'", self.ctrl)
        self.assertIn("('website', ", self.pms)

    def test_confirmation_appelee_apres_creation(self):
        # create(...) puis action_confirm() → e-mail auto du moteur.
        create_pos = self.ctrl.index("Booking.create(")
        confirm_pos = self.ctrl.index("booking.action_confirm()")
        self.assertLess(create_pos, confirm_pos)

    def test_conflit_redirige_vers_erreur_slot(self):
        m = re.search(
            r"except ValidationError:.*?error=slot", self.ctrl, re.S)
        self.assertIsNotNone(
            m, "Le conflit de créneau doit renvoyer error=slot")

    def test_get_day_grid_renvoie_slot_minutes_entier(self):
        # Le contrôleur divise par grid['resource']['slot_minutes'] :
        # la source doit le convertir en int (Selection = chaîne).
        self.assertIn("'slot_minutes': int(res.slot_minutes",
                      self.slot_rs)

    def test_routes_post_avec_csrf(self):
        posts = re.findall(
            r"@http\.route\([^)]*methods=\['POST'\][^)]*\)", self.ctrl)
        self.assertEqual(len(posts), 2)
        for route in posts:
            self.assertIn("csrf=True", route)

    def test_espace_client_reserve_aux_connectes(self):
        m = re.search(
            r"@http\.route\('/mes-reservations'[^)]*\)", self.ctrl)
        self.assertIn("auth='user'", m.group(0))

    def test_pages_publiques_en_auth_public(self):
        for path in ("/reservation'", "/reservation/espaces",
                     "/reservation/prestations", "/reservation/chambres'"):
            m = re.search(
                r"@http\.route\('" + re.escape(path.rstrip("'")) +
                r"'[^)]*\)", self.ctrl)
            self.assertIsNotNone(m, path)
            self.assertIn("auth='public'", m.group(0))

    def test_ecritures_publiques_en_sudo_controle(self):
        # Les créations issues du public passent par sudo() explicite.
        for pattern in ("env['aite.slot.booking'].sudo()",
                        "env['aite.hotel.reservation'].sudo()"):
            self.assertIn(pattern, self.ctrl)

    def test_manifest_fichiers_presents(self):
        import os
        data = ast.literal_eval(
            re.search(r"\{.*\}", _read(MANIFEST), re.S).group(0))
        for f in data["data"]:
            self.assertTrue(
                os.path.isfile(BASE + "/aite_website_booking/" + f),
                "Manifest référence un fichier absent : " + f)

    def test_dependances_minimales(self):
        data = ast.literal_eval(
            re.search(r"\{.*\}", _read(MANIFEST), re.S).group(0))
        self.assertEqual(
            set(data["depends"]),
            {"website", "portal", "aite_slot_booking",
             "aite_hotel_management"})

    def test_templates_postent_start_h_depuis_slot_start(self):
        # La valeur postée doit être l'heure décimale s['start'].
        self.assertIn('name="start_h"', self.tpl)
        self.assertRegex(
            self.tpl, r'name="start_h"[^>]*t-att-value="s\[\'start\'\]"')


if __name__ == "__main__":
    unittest.main(verbosity=2)
