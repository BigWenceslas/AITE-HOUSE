# -*- coding: utf-8 -*-
"""
Scénarios de recette (UAT) de la suite AITE HOUSE.

Chaque scénario est joué dans un vrai navigateur, avec le profil métier
concerné, comme le ferait la personne à son poste. Les captures
produites alimentent directement le cahier de recette.
"""
from uat_common import Scenario, UatSession


def _is_access_denied(session, model_name):
    """
    L'écran affiche-t-il un refus d'accès portant sur ce modèle ?

    Assertion volontairement stricte : on exige la boîte « Access Error »
    d'Odoo **et** le nom technique du modèle. Chercher « accès » dans la
    page laisserait passer n'importe quel écran contenant ce mot.
    """
    body = session.text()
    denied = ("Access Error" in body
              or "Erreur d'accès" in body
              or "not allowed to access" in body
              or "n'êtes pas autorisé" in body)
    return denied and model_name in body


def _apply_filter(page, label):
    """Applique un filtre de la barre de recherche, comme à la souris."""
    try:
        page.locator('.o_searchview_dropdown_toggler, '
                     '.o_cp_searchview .dropdown-toggle').first.click()
        page.wait_for_timeout(300)
        page.locator('.o_filter_menu, .dropdown-menu').locator(
            'span:has-text("%s"), a:has-text("%s")' % (label, label)
        ).first.click()
        page.wait_for_timeout(600)
        page.keyboard.press('Escape')
        return True
    except Exception:  # noqa: BLE001
        return False


# ======================================================================
# 1 — Réception : la journée du front desk
# ======================================================================

def scenario_front_desk(page):
    scenario = Scenario(
        key='r1-front-desk',
        title="La journée de la réception",
        persona="Réception (Awa Diallo)",
        goal="Prendre connaissance de la journée, retrouver une "
             "réservation, ouvrir un folio et encaisser un acompte.",
    )
    ses = UatSession(page, scenario)
    ses.login('reception')

    # -- Étape 1 : le tableau de bord d'ouverture ----------------------
    ses.open_action('aite_hotel_management.action_hotel_dashboard')
    ses.check(
        "Ouvrir le Front Desk",
        "Le tableau de bord affiche l'occupation du jour, les arrivées, "
        "les départs et le room board.",
        ses.has("Front Desk") and ses.has("ROOM BOARD"),
        "Occupation, arrivées, départs et room board sont affichés.",
        "Le tableau de bord ne s'affiche pas.")

    # -- Étape 2 : les arrivées attendues ------------------------------
    ses.open_action('aite_hotel_management.action_hotel_arrivals_today')
    ses.check(
        "Consulter les arrivées du jour",
        "La liste ne montre que les réservations confirmées arrivant "
        "aujourd'hui.",
        ses.has("Arrivées"),
        "La liste des arrivées du jour s'affiche.",
        "La liste des arrivées est introuvable.")

    # -- Étape 3 : le planning des chambres ----------------------------
    ses.open_action('aite_hotel_management.action_hotel_room_planning')
    ses.check(
        "Ouvrir le planning des chambres",
        "Le planning s'affiche — calendrier sur Community, Gantt sur "
        "Enterprise — avec les séjours de la période.",
        (ses.count('.o_calendar_view') or ses.count('.o_gantt_view')
         or ses.count('.o_content .fc')) and not ses.has("Server Error"),
        "Le planning s'ouvre et présente les séjours.",
        "Aucune vue planning n'est rendue.")

    # -- Étape 4 : ouvrir une réservation ------------------------------
    ses.open_action('aite_hotel_management.action_hotel_reservation')
    ses.shoot("Lister les réservations",
              "La liste des réservations du séjour s'affiche.")

    rows = page.locator('.o_data_row')
    if rows.count():
        rows.first.click()
        ses.settle()
        ses.check(
            "Ouvrir une réservation",
            "La fiche montre le client, les chambres, le folio et les "
            "boutons du workflow.",
            ses.has("Folio") or ses.has("Chambres"),
            "La fiche réservation s'ouvre avec son folio.",
            "La fiche réservation ne s'ouvre pas.")

    # -- Étape 5 : le folio ---------------------------------------------
    ses.open_action('aite_hotel_management.action_hotel_folio')
    ses.check(
        "Consulter les folios",
        "Les notes de séjour listent hébergement, services et solde dû.",
        ses.has("Folio") or ses.has("Solde"),
        "Les folios s'affichent avec leur solde.",
        "Les folios ne s'affichent pas.")

    # -- Étape 6 : la réservation rapide -------------------------------
    ses.open_action('aite_hotel_management.action_hotel_booking_wizard')
    ses.check(
        "Ouvrir la réservation rapide",
        "L'assistant propose dates, occupation et recherche de "
        "disponibilité.",
        ses.has("Arrivée") or ses.has("disponib"),
        "L'assistant de réservation rapide s'ouvre.",
        "L'assistant ne s'ouvre pas.")

    ses.logout()
    return scenario


# ======================================================================
# 2 — Gouvernante : le tour des chambres
# ======================================================================

def scenario_housekeeping(page):
    scenario = Scenario(
        key='r2-gouvernante',
        title="Le tour des chambres",
        persona="Gouvernante (Fanta Souaré)",
        goal="Prendre ses tâches du jour, démarrer une recouche, la "
             "terminer et voir l'état des chambres changer.",
    )
    ses = UatSession(page, scenario)
    ses.login('housekeeping')

    # -- Étape 1 : les tâches du jour ----------------------------------
    ses.open_action('aite_hotel_management.action_hotel_housekeeping')
    ses.check(
        "Ouvrir les tâches de gouvernante",
        "Les tâches du jour s'affichent, groupées par état.",
        ses.has("Gouvernante") or ses.has("nettoyer")
        or ses.has("À faire"),
        "Les tâches de ménage du jour sont listées.",
        "Les tâches ne s'affichent pas.")

    # -- Étape 2 : démarrer une tâche depuis le kanban -----------------
    # La gouvernante travaille sur le kanban : les boutons Démarrer /
    # Terminer sont directement sur les cartes, sans ouvrir de fiche.
    todo_before = ses.count('button[name="action_start"]')
    started = False
    start_button = page.locator('button[name="action_start"]')
    if start_button.count():
        start_button.first.click()
        ses.settle()
        started = True
    ses.check(
        "Démarrer une recouche depuis le kanban",
        "La carte bascule dans la colonne « En cours » et la chambre "
        "passe en « Nettoyage en cours ».",
        started and ses.count('button[name="action_start"]') < todo_before,
        "La tâche est démarrée : elle quitte la colonne « À faire ».",
        "Le bouton « Démarrer » du kanban n'a pas produit d'effet.")

    # -- Étape 3 : terminer --------------------------------------------
    done_before = ses.count('button[name="action_done"]')
    finished = False
    done_button = page.locator('button[name="action_done"]')
    if done_button.count():
        done_button.first.click()
        ses.settle()
        finished = True
    ses.check(
        "Terminer la tâche",
        "La tâche passe « Terminé » et la chambre redevient propre "
        "(ou « à inspecter » si l'inspection est exigée).",
        finished and ses.count('button[name="action_done"]') < done_before,
        "La tâche est clôturée, la chambre est rendue au service.",
        "Le bouton « Terminer » du kanban n'a pas produit d'effet.")

    # -- Étape 4 : le tarif est hors de son périmètre ------------------
    ses.open_action('aite_hotel_management.action_hotel_room')
    body = ses.text()
    ses.check(
        "Consulter les chambres",
        "La gouvernante voit l'état de chaque chambre, mais ni le tarif "
        "spécifique ni le tarif du jour : ces données relèvent de la "
        "Réception.",
        ("tarif" not in body.lower()
         and ("propre" in body.lower() or "chambre" in body.lower())),
        "Les chambres s'affichent sans aucune donnée tarifaire.",
        "Un tarif est visible sur l'écran de la gouvernante.")

    # -- Étape 5 : la gouvernante ne voit pas l'argent -----------------
    ses.open_action('aite_hotel_management.action_hotel_folio')
    ses.check(
        "Tenter d'ouvrir les folios",
        "Le profil Gouvernante n'a pas accès aux notes de séjour : "
        "Odoo doit afficher un refus nommant le modèle concerné.",
        _is_access_denied(ses, 'aite.hotel.folio'),
        "L'accès aux folios est refusé, avec le motif affiché.",
        "La gouvernante accède aux folios — cloisonnement insuffisant.")

    ses.logout()
    return scenario


# ======================================================================
# 3 — Caisse : ardoise et recouvrement
# ======================================================================

def scenario_credit(page):
    scenario = Scenario(
        key='r3-ardoises',
        title="Ardoises clients et recouvrement",
        persona="Caisse (Ibrahima Sylla)",
        goal="Suivre l'encours, ouvrir une ardoise, enregistrer un "
             "remboursement et vérifier le solde.",
    )
    ses = UatSession(page, scenario)
    ses.login('cashier')

    # -- Étape 1 : le tableau de bord du recouvrement ------------------
    ses.open_action('aite_pos_credit.action_pos_credit_dashboard')
    ses.check(
        "Ouvrir le tableau de bord Recouvrement",
        "Encours total, balance âgée et top débiteurs sont affichés.",
        ses.has("ncours") or ses.has("Recouvrement"),
        "Le tableau de bord du recouvrement s'affiche.",
        "Le tableau de bord ne s'affiche pas.")

    # -- Étape 2 : la liste des ardoises -------------------------------
    ses.open_action('aite_pos_credit.action_aite_pos_credit')
    ses.check(
        "Lister les ardoises",
        "Les ardoises s'affichent avec client, montant, reste dû et "
        "ancienneté.",
        ses.has("Ardoise") or ses.has("Reste"),
        "Les ardoises sont listées avec leur reste dû.",
        "Les ardoises ne s'affichent pas.")

    # -- Étape 3 : ne garder que les ardoises ouvertes ------------------
    # Une ardoise soldée n'accepte plus de remboursement (le bouton
    # disparaît, à raison) : on applique le filtre « Ouvertes ».
    _apply_filter(page, "Ouvertes")
    ses.settle()
    ses.shoot("Filtrer les ardoises ouvertes",
              "Seules les ardoises encore dues restent affichées.")

    # -- Étape 4 : ouvrir une ardoise et encaisser ---------------------
    repaid = False
    rows = page.locator('.o_data_row')
    for index in range(min(rows.count(), 5)):
        page.locator('.o_data_row').nth(index).click()
        ses.settle()
        button = page.locator('button[name="action_register_payment"]')
        if not button.count():
            page.go_back()
            ses.settle()
            continue
        ses.shoot("Ouvrir une ardoise",
                  "La fiche montre le reste dû et le bouton "
                  "« Enregistrer un remboursement ».")
        button.first.click()
        ses.settle()
        ses.shoot("Assistant de remboursement",
                  "Le montant est pré-rempli avec le reste dû et le "
                  "moyen de paiement est proposé.")
        confirm = page.locator('.modal button[name="action_confirm"]')
        if confirm.count():
            confirm.first.click()
            ses.settle()
            repaid = True
        break

    ses.check(
        "Enregistrer le remboursement",
        "Le reste dû tombe à zéro et l'ardoise passe « Réglée ».",
        repaid and ses.has("Réglée"),
        "Le remboursement est enregistré : l'ardoise est soldée.",
        "Le remboursement n'a pas pu être enregistré depuis l'écran.")

    # -- Étape 4 : cloisonnement ---------------------------------------
    ses.open_action('aite_hotel_management.action_hotel_reservation')
    ses.check(
        "Tenter d'ouvrir les réservations hôtel",
        "Le profil Caisse n'a pas de droits hôteliers : Odoo doit "
        "afficher un refus nommant le modèle concerné.",
        _is_access_denied(ses, 'aite.hotel.reservation'),
        "L'accès au PMS est refusé, avec le motif affiché.",
        "Le caissier accède au PMS — cloisonnement insuffisant.")

    ses.logout()
    return scenario


# ======================================================================
# 4 — Direction : le cockpit
# ======================================================================

def scenario_management(page):
    scenario = Scenario(
        key='r4-direction',
        title="Le cockpit de la direction",
        persona="Direction (Aminata Bah)",
        goal="Consulter les tableaux de bord consolidés et vérifier "
             "que les chiffres concordent entre les vues.",
    )
    ses = UatSession(page, scenario)
    ses.login('manager')

    # Pour chaque tableau de bord : un libellé qui n'apparaît QUE s'il a
    # produit ses chiffres. Constater « pas d'erreur » ne suffirait pas —
    # un écran vide passerait.
    dashboards = [
        ("Ventes (POS Analytics)",
         'aite_pos_analytics.action_pos_analytics_dashboard',
         "Chiffre d'affaires, marge, CMV et panier moyen sont affichés.",
         ("CMV", "MARGE")),
        ("Recouvrement (Crédit clients)",
         'aite_pos_credit.action_pos_credit_dashboard',
         "Encours, balance âgée et débiteurs à relancer sont affichés.",
         ("ENCOURS", "0–30 j")),
        ("Stock & Inventaire",
         'aite_stock_dashboard.action_aite_stock_dashboard',
         "Valorisation, ruptures, couverture et alertes sont affichées.",
         ("RUPTURE", "VALEUR")),
        ("Achats & Fournisseurs",
         'aite_purchase_dashboard.action_aite_purchase_dashboard',
         "Échéancier fournisseurs et évolution des prix sont affichés.",
         ("FOURNISSEUR",)),
        ("Espaces & Prestations",
         'aite_slot_booking.action_aite_slot_dashboard',
         "Taux d'occupation des espaces et planning du jour s'affichent.",
         ("OCCUPATION", "RÉSERVATION")),
        ("Cockpit Direction",
         'aite_direction_dashboard.action_direction_dashboard',
         "La vue consolidée reprend les quatre pôles et la balance âgée "
         "en miroir.",
         ("SANTÉ DE L'AFFAIRE", "Balance âgée")),
        ("Tableau de bord exécutif",
         'aite_exec_dashboard.action_aite_exec_dashboard',
         "Hébergement, restauration et prestations sont consolidés.",
         ("OCCUPATION", "CA")),
    ]
    for title, xmlid, expected, markers in dashboards:
        ses.open_action(xmlid)
        body = ses.text()
        broken = ("Internal Server Error" in body
                  or "Traceback" in body
                  or "Odoo Server Error" in body)
        rendered = any(m.lower() in body.lower() for m in markers)
        ses.check(
            "Ouvrir — %s" % title,
            expected,
            rendered and not broken,
            "Le tableau de bord s'affiche et présente ses indicateurs.",
            "Le tableau de bord renvoie une erreur ou reste vide.")

    ses.logout()
    return scenario


# ======================================================================
# 5 — Client : la réservation en ligne
# ======================================================================

def scenario_website(page):
    scenario = Scenario(
        key='r5-site-web',
        title="La réservation en ligne",
        persona="Client (visiteur du site)",
        goal="Réserver un espace depuis le site public, sans compte, "
             "et recevoir la confirmation.",
    )
    ses = UatSession(page, scenario)
    ses.logout()

    # -- Étape 1 : la page d'accueil -----------------------------------
    ses.open_url('/reservation')
    ses.check(
        "Ouvrir la page de réservation",
        "La page publique s'affiche sans authentification.",
        not ses.has("Se connecter à") and len(ses.text()) > 100,
        "La page de réservation est accessible au public.",
        "La page publique est inaccessible.")

    # -- Étape 2 : le choix de l'espace --------------------------------
    ses.open_url('/reservation/espaces')
    ses.check(
        "Choisir un espace",
        "Les espaces réservables en ligne sont listés ; ceux réservés "
        "au comptoir n'apparaissent pas.",
        len(ses.text()) > 100,
        "La liste des espaces réservables s'affiche.",
        "Les espaces ne s'affichent pas.")

    # -- Étape 3 : la grille de créneaux -------------------------------
    booked = False
    links = page.locator('a[href*="/reservation/espace/"]')
    if links.count():
        links.first.click()
        ses.settle()
        ses.shoot("Voir les créneaux libres",
                  "La grille du jour montre les créneaux encore "
                  "disponibles.")

        # -- Étape 4 : choisir un créneau et se présenter ---------------
        form = page.locator('form[action*="confirmer"]').first
        if form.count():
            # Les créneaux sont des boutons radio : il faut en cocher un,
            # sinon le navigateur bloque l'envoi (champ obligatoire).
            slots = form.locator('input[name="start_h"]')
            if slots.count():
                slots.first.check()
            for name, value in (('name', "Mariama Condé"),
                                ('phone', "+224 620 45 67 89"),
                                ('email', "mariama.conde@example.com")):
                field = form.locator('[name="%s"]' % name)
                if field.count():
                    field.first.fill(value)
            ses.check(
                "Choisir un créneau et se présenter",
                "Un créneau est coché et les coordonnées sont saisies ; "
                "le formulaire est prêt à partir.",
                slots.count() and slots.first.is_checked(),
                "Créneau sélectionné, coordonnées renseignées.",
                "Aucun créneau n'a pu être sélectionné.")
            submit = form.locator('button[type="submit"]')
            if submit.count():
                submit.first.click()
                ses.settle()
                booked = True

    # La page de remerciement porte la référence de la réservation :
    # c'est le seul signal qui prouve l'enregistrement côté serveur.
    confirmed = booked and ses.has("Merci") and ses.has("confirmée")
    ses.check(
        "Valider la réservation",
        "La page de remerciement affiche la référence de la réservation, "
        "preuve de son enregistrement côté back-office.",
        confirmed,
        "La réservation est confirmée et sa référence s'affiche.",
        "La réservation n'a pas abouti : pas de page de confirmation.")

    # -- Étape 5 : la demande de séjour --------------------------------
    ses.open_url('/reservation/chambres')
    ses.check(
        "Demander un séjour",
        "Le formulaire de demande de chambre s'affiche (dates, "
        "occupation, coordonnées).",
        ses.has("rriv") or ses.has("chambre"),
        "Le formulaire de demande de séjour s'affiche.",
        "Le formulaire de demande de séjour est absent.")

    return scenario


# ======================================================================
# 6 — Magasin : stock et alertes
# ======================================================================

def scenario_stock(page):
    scenario = Scenario(
        key='r6-magasin',
        title="Stock, ruptures et réapprovisionnement",
        persona="Magasin (Moussa Camara)",
        goal="Repérer les ruptures et les articles sous seuil, et "
             "consulter la valorisation du stock.",
    )
    ses = UatSession(page, scenario)
    ses.login('stock')

    ses.open_action('aite_stock_dashboard.action_aite_stock_dashboard')
    ses.check(
        "Ouvrir le tableau de bord Stock",
        "Valorisation, nombre de références, ruptures et couverture "
        "moyenne sont affichés.",
        (ses.has("rupture") or ses.has("valeur"))
        and not ses.has("Server Error"),
        "Le tableau de bord Stock s'affiche avec ses indicateurs.",
        "Le tableau de bord Stock renvoie une erreur ou reste vide.")

    ses.open_action('aite_pos_credit.action_aite_pos_credit')
    ses.check(
        "Tenter d'ouvrir les ardoises clients",
        "Le profil Magasin n'a pas de droits sur le crédit clients : "
        "Odoo doit afficher un refus nommant le modèle concerné.",
        _is_access_denied(ses, 'aite.pos.credit'),
        "L'accès au crédit clients est refusé, avec le motif affiché.",
        "Le magasinier accède aux ardoises — cloisonnement insuffisant.")

    ses.logout()
    return scenario


ALL_SCENARIOS = [
    scenario_front_desk,
    scenario_housekeeping,
    scenario_credit,
    scenario_management,
    scenario_website,
    scenario_stock,
]
