# -*- coding: utf-8 -*-
"""Tutoriel 8 — Réservation en ligne : vos clients réservent seuls, sans double vente.

Format marketing du pilote ``t07_gouvernante.py`` : accroche, révélation,
sept étapes (le site public, puis la réception), résultats, appel.

Sources des écrans (libellés vérifiés mot pour mot par ``grep -rF`` dans
``addons/``) :

- Site public — ``aite_website_booking/views/website_templates.xml`` :
  accueil « Réserver en ligne » et ses trois cartes (l. 5-41) ; liste
  « Espaces VIP & VVIP », « Ouvert de HH:MM à HH:MM », prix « 11 500 FCFA /
  heure » (format ``'{:,.0f}'`` + espace + symbole de la devise, l. 44-71) ;
  grille « ← Tous les espaces », « Date », « Voir ce jour », « Créneaux
  disponibles », « Vos coordonnées », « Réserver ce créneau », mention de
  l'acompte, bandeau « Ce créneau vient d'être pris — choisissez-en un
  autre. » (l. 74-130) ; « Demande de séjour » et ses champs (l. 233-277) ;
  page « Merci ! » d'un créneau et d'un séjour (l. 280-300). Menu du site
  « Réservation » : ``data/website_menu_data.xml`` ; autres entrées de
  l'en-tête (Accueil, Contactez-nous, Se connecter) et du pied de page
  (Liens utiles, À propos de nous, Produits, Services, Juridique,
  Rejoignez-nous) : traduction française d'Odoo 18
  (``odoo18/addons/website/i18n/fr.po``, ``portal/i18n/fr.po``).
- Tunnel — ``aite_website_booking/controllers/main.py`` : routes
  ``auth='public'`` (l. 69-146, 228-238) ; seules les ressources
  « Réservable en ligne » (l. 59-63, 78-91) ; grille = ``get_day_grid``, seuls
  les créneaux ``free`` (l. 92-100) ; fin = début + un pas, création
  ``source='online'`` puis ``action_confirm`` sous point de sauvegarde, refus
  → retour sur la grille avec ``error=slot`` (l. 157-222) ; demande de séjour
  en brouillon, canal ``website``, arrivée 14:00 et départ 11:00 (l. 236-278).
- Moteur de créneaux — ``aite_slot_booking/models/booking_resource.py``
  (``get_day_grid``, « source de vérité unique » du site et du tableau de
  bord, l. 27-30, 157-223 ; champ « Réservable en ligne », l. 74-77) ;
  ``models/booking_booking.py`` (états, « Origine » Comptoir / En ligne
  l. 87-101, montant = heures × tarif horaire ``_slot_price`` l. 126-138,
  conflit refusé au-delà de la capacité ``_check_no_conflict`` l. 260-282) ;
  ``data/slot_sequence_data.xml`` (référence ``RES/%(y)s/`` sur 4 chiffres
  → RES/26/0418).
- Réception — tableau de bord ``aite_slot_booking/static/src/xml/dashboard.xml``
  (titre, filtres Jour / Période stats / Famille, quatre indicateurs,
  « Planning du <t t-esc="state.day"/> », couloirs, « x/y créneaux libres »,
  l. 18-128), ``static/src/js/views/slot_dashboard_view.js`` (repères toutes
  les deux heures l. 204-215, texte des créneaux libres l. 221-231, clic sur
  un bloc → fiche l. 322-330), ``static/src/js/services/utils.js`` (formats
  montant, %, heures), ``static/src/scss/slot_dashboard.scss`` (couleurs),
  ``models/slot_dashboard.py`` (indicateurs ``get_kpis`` l. 124-176 : CA des
  réalisées, heures réservées / heures ouvrées, réservations à venir) ;
  fiche ``views/booking_booking_views.xml`` (boutons et statusbar l. 37-59,
  champs l. 60-91) ; nom de l'action ``views/slot_dashboard_actions.xml``.
- Réservations hôtel — ``aite_hotel_management/views/hotel_reservation_views.xml``
  (liste l. 5-33, filtre « Brouillons » l. 240 et regroupement « Canal »
  l. 253), ``models/hotel_reservation.py`` (« Canal » et « Site web »
  l. 70-80, ordre ``checkin_date desc`` l. 27, Confirmer vérifie la
  disponibilité puis ouvre le folio l. 288-337) ; ``models/hotel_room.py``
  l. 431-446 (seules les lignes confirmées ou en séjour occupent une
  chambre) ; capture réelle de la liste regroupée (groupes repliés, totaux
  par groupe sans symbole) prise en lecture sur la base MuK ; colonne
  « Registre » / « Aucune fiche » :
  ``aite_guest_registry/views/hotel_reservation_views.xml`` l. 57-67 ;
  menus ``aite_hotel_management/views/hotel_menus.xml`` et
  ``aite_slot_booking/views/slot_menus.xml``.
- Thème MuK et mise en page : captures de référence
  ``../aite-videos/ref_muk/500-site-reservation.png``, ``501-site-espaces.png``,
  ``502-site-chambres.png``, ``049-…-tableau-de-bord.png``, ``050-…``,
  ``306-reception-reservations.png`` ; captures de recette
  ``docs/captures_uat/r5-site-web-0[1-6]-*.png`` (modèle visuel seulement,
  jamais incrustées).

Douleurs de l'accroche : ``recette/cas_de_test.py`` l. 132-137 (B03, double
réservation d'un créneau) et l. 178-182 (C03, réservation « sans aucune
ressaisie ») ; ``docs/etude_comparative/benchmark_pms.md`` l. 150 (moteur de
réservation direct : 10 leaders sur 10) ; ``docs/etude_comparative/build_etude.py``
l. 420 (SaaS étrangers à 280-480 KFCFA par mois) ;
``docs/etude_comparative/benchmark_afrique_odoo.md`` l. 153 (Community :
« moteur de réservation à développer »).

Résultats : trois parcours publics (``website_templates.xml`` l. 10-38) ;
une seule grille pour le site et la réception (``booking_resource.py``
l. 27-30, ``slot_dashboard.py`` l. 116, ``controllers/main.py`` l. 93) ;
45 tests Odoo du module, dont ``test_double_booking_is_refused``
(``docs/GUIDE_TESTS.md`` l. 31, ``aite_website_booking/tests/test_controllers.py``
l. 155-173 : 22 tests, ``test_helpers.py`` : 23 tests).

Données : fictives (``demo.py``). Claire Durand (cliente), Mireille Ateba
(réception), les salons « Sanaga », « Nyong », « Dibamba » et les autres
clients sont inventés ; les tarifs horaires (11 500 / 23 000) reprennent
ceux du jeu de démonstration, pas ses noms. « Aujourd'hui » vaut le
14/10/2026 (``demo.ARRIVEES``) ; le salon est réservé pour le samedi
17/10/2026 (une date future : une heure passée serait encore proposée,
voir les écarts).

Écarts rejoués tels quels : « Planning du 2026-10-17 » (date ISO,
``dashboard.xml`` l. 99) ; menu « Front Desk » en anglais
(``hotel_menus.xml`` l. 18) ; deux numérotations « RES » (RES/26/0418 pour
le créneau, RES/2026/0221 pour le séjour) ; départ de la demande de séjour
à 11:00, fixé en dur (``controllers/main.py`` l. 264-267).
"""

import demo
from ecrans import (APPS_PROFIL, bouton, champ, cp_fiche, deux_colonnes, e, entree, fenetre_muk, groupe,
                    icone, navigateur, s_vue, statusbar, titre_fiche, vue_fiche, vue_libre)
from marketing import bulle, dezoom, reaction, zoom
from moteur import anneau, cacher, clic, classe, montrer, pause, saisir, texte, vue
from scenarios.c4_site_web import s_carte

NOM, ROLE = demo.POSTES['client']                 # Claire Durand, la cliente
RECEPTION = demo.POSTES['reception'][0]           # Mireille Ateba
SITE = 'Complexe Hôtelier'
TEL_CLAIRE = '+33 6 45 21 87 90'
TEL_CLAIRE_N = '+33645218790'                     # _norm_phone : chiffres et « + » de tête
MAIL_CLAIRE = 'claire.durand@exemple.fr'
SALON = 'Salon VIP Sanaga'
REF_CRENEAU = 'RES/26/0418'                       # séquence RES/%(y)s/ (créneaux)
REF_SEJOUR = 'RES/2026/0221'                      # séquence RES/%(year)s/ (séjours)

# Une icône de calendrier (champ date du navigateur) et l'icône « regrouper
# par » des facettes d'Odoo 18, redessinées en SVG.
CAL = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><rect x="3" y="4.5" width="18" '
       'height="16" rx="2"/><path d="M3 9.5h18M8 2.5v4M16 2.5v4"/></svg>')
COUCHES = ('<svg viewBox="0 0 24 24" fill="#fff"><path d="M12 3l9 4.5-9 4.5-9-4.5z"/><path d="M3 12l9 4.5 9-4.5" '
           'fill="none" stroke="#fff" stroke-width="2"/><path d="M3 16.5l9 4.5 9-4.5" fill="none" stroke="#fff" '
           'stroke-width="2"/></svg>')


# ======================================================== le site public ==

NAV = ('<div class="s-nav t08-nav"><span class="s-logo t08-logo">%s</span><span class="s-m">Accueil</span>'
       '<span class="s-m actif">Réservation</span><span class="s-m">Contactez-nous</span>'
       '<span class="t08-loupe">%s</span><span class="s-tel t08-tel">%s+237 6 99 00 00 00</span>'
       '<span class="t08-connexion">Se connecter</span><span class="bt primaire s-bt t08-contact">Contactez-nous</span>'
       '</div>' % (e(SITE), icone('loupe'), icone('telephone')))


def pied(haut):
    """Le pied de page du site, qui suit le contenu et file sous le bord de
    la fenêtre (rubriques du pied de page par défaut d'Odoo 18, en français :
    « Liens utiles », « Rejoignez-nous » ; coordonnées fictives)."""
    liens = ''.join('<div class="t08-pl">%s</div>' % x for x in (
        'Accueil', 'À propos de nous', 'Produits', 'Services', 'Juridique', 'Contactez-nous'))
    return ('<div class="t08-pied" style="top:%dpx"><div class="t08-pc"><div class="t08-ph">Liens utiles</div>%s</div>'
            '<div class="t08-pc t08-pc-d"><div class="t08-ph">Rejoignez-nous</div><div class="t08-pl">Contactez-nous</div>'
            '<div class="t08-pl">reservation@exemple.cm</div><div class="t08-pl">+237 6 99 00 00 00</div></div></div>'
            % (haut, liens))


def vue_site(ident, contenu, haut_pied=None, initiale=False):
    """Une page du site (comme ``ecrans.s_vue``), avec son pied de page."""
    return '<div class="vue s-vue%s" id="%s"><div class="s-cadre">%s</div>%s</div>' % (
        ' initiale' if initiale else '', ident, contenu, pied(haut_pied) if haut_pied else '')


def site_t08(ident, vues):
    """Le site de l'établissement, en-tête en français (le composant partagé
    ``ecrans.site`` écrit « Nous contacter », absent d'Odoo)."""
    return '<div class="app site t08-site" id="%s">%s<div class="s-page">%s</div></div>' % (ident, NAV, ''.join(vues))


ACCUEIL = vue_site('t08-accueil', (
    '<div class="s-h1"><span id="t08-acc-titre">Réserver en ligne</span></div>'
    '<div class="s-p">Disponibilités en temps réel — confirmation immédiate par e-mail.</div>'
    '<div class="s-cartes" id="t08-acc-cartes">%s%s%s</div>'
    % (s_carte('t08-vip', 'Espaces VIP & VVIP', "Salons privés à l'heure, pour vos rencontres et célébrations.",
               'Choisir un espace'),
       s_carte('t08-spa', 'SPA & Coiffure', 'Soins et rendez-vous coiffure homme & femme.', 'Prendre rendez-vous'),
       s_carte('t08-ch', 'Chambres & Suites', 'Votre séjour, confirmé par notre réception.', 'Demander un séjour'))),
    haut_pied=440, initiale=True)

ESPACES = vue_site('t08-espaces', (
    '<div class="s-h1">Espaces VIP & VVIP</div><div class="s-cartes t08-salons" id="t08-salons">%s%s%s</div>'
    % (s_carte('t08-e1', SALON, 'Ouvert de 09:00 à 23:00', 'Voir les créneaux', True, '11 500 FCFA / heure'),
       s_carte('t08-e2', 'Salon VIP Nyong', 'Ouvert de 09:00 à 23:00', 'Voir les créneaux', True, '11 500 FCFA / heure'),
       s_carte('t08-e3', 'Salon VVIP Dibamba', 'Ouvert de 10:00 à 23:00', 'Voir les créneaux', True,
               '23 000 FCFA / heure'))), haut_pied=440)

# Les créneaux libres du salon (pas d'une heure, 09:00 → 23:00), cohérents
# avec le planning de la réception : le mercredi 14/10 (12:00-14:00 et
# 16:00-20:00 vendus), et le samedi 17/10 (12:00-14:00 et 19:00-21:00 vendus).
LIBRES_14 = ['09:00', '10:00', '11:00', '14:00', '15:00', '20:00', '21:00', '22:00']
LIBRES_17 = ['09:00', '10:00', '11:00', '14:00', '15:00', '16:00', '17:00', '18:00', '21:00', '22:00']


def grille(ident, date, heures, coche=None, nom='', tel='', alerte=False, saisie_date=False):
    """La page d'un salon : date, créneaux libres, coordonnées.

    ``ident`` préfixe les identifiants de la page ; ``coche`` : l'heure déjà
    cochée ; ``alerte`` : le bandeau du créneau pris ; ``saisie_date`` : le
    champ date affiche sa valeur comme un texte que l'on remplace."""
    creneaux = ''.join('<span class="creneau t08-cr%s" id="%s-h%s"><i></i>%s</span>'
                       % (' coche' if h == coche else '', ident, h[:2], h) for h in heures)
    champ_date = entree(ident + '-date', date) if saisie_date else entree(ident + '-date', '', date)
    bandeau = ('<div class="t08-alerte" id="%s-alerte">Ce créneau vient d\'être pris — choisissez-en un autre.</div>'
               % ident) if alerte else ''
    return s_vue(ident, (
        '<div class="s-form t08-form"><div class="t08-retour">← Tous les espaces</div>'
        '<div class="s-h1 t08-h1">%s</div><div class="s-p t08-prix">11 500 FCFA / heure</div>%s'
        '<div class="s-lab">Date</div><div class="t08-ligne-date"><div class="t08-date">%s<span class="t08-cal">%s'
        '</span></div><span class="t08-voir" id="%s-voir">Voir ce jour</span></div>'
        '<div class="t08-h5">Créneaux disponibles</div><div class="creneaux t08-creneaux" id="%s-creneaux">%s</div>'
        '<div class="t08-h5">Vos coordonnées</div><div class="s-ligne3 t08-coord">%s%s%s</div>'
        '<div class="s-gros-bt t08-gros" id="%s-reserver">Réserver ce créneau</div>'
        '<div class="s-note">Acompte à régler au comptoir — Orange Money, MTN MoMo ou espèces.</div></div>'
        % (e(SALON), bandeau, champ_date, CAL, ident, ident, creneaux,
           entree(ident + '-nom', '' if nom else 'Nom complet', nom),
           entree(ident + '-tel', '' if tel else 'Téléphone', tel),
           entree(ident + '-mail', 'E-mail (confirmation)'), ident)))


GRILLE_14 = grille('t08-g14', '14/10/2026', LIBRES_14, saisie_date=True)
GRILLE_17 = grille('t08-g17', '17/10/2026', LIBRES_17)
# Un autre visiteur avait ouvert la même page avant Claire : seize heures y est encore libre.
AUTRE = grille('t08-ga', '17/10/2026', LIBRES_17, coche='16:00', nom='Arnaud Fotsing', tel='+237 699 52 18 40')
# Sa validation est refusée : il revient sur la grille, seize heures n'y est plus.
REFUS = grille('t08-gr', '17/10/2026', [h for h in LIBRES_17 if h != '16:00'], alerte=True)

MERCI = vue_site('t08-merci', (
    '<div class="s-merci" id="t08-merci-bloc"><div class="h">Merci !</div>'
    '<div class="p">Votre réservation <b id="t08-merci-ref">%s</b> est <b>confirmée</b>.</div>'
    '<div class="q t08-noir">%s</div><div class="q">Un e-mail de confirmation vous a été envoyé.</div>'
    '<div class="s-alerte" id="t08-acompte">L\'acompte se règle au comptoir à votre arrivée — <b>Orange Money, MTN MoMo '
    'ou espèces</b>.</div><div class="t08-retour-bt"><span class="s-bouton contour">Retour aux réservations</span></div>'
    '</div>' % (REF_CRENEAU, e(SALON))), haut_pied=480)

SEJOUR = s_vue('t08-sejour', (
    '<div class="s-form t08-form-s"><div class="s-h1 t08-h1">Demande de séjour</div>'
    '<div class="s-p">Notre réception confirme votre chambre et vous rappelle rapidement.</div>'
    '<div class="s-ligne"><div><div class="s-lab">Arrivée</div>%s</div><div><div class="s-lab">Départ</div>%s</div></div>'
    '<div class="s-ligne t08-l12"><div><div class="s-lab">Adultes</div>%s</div>'
    '<div><div class="s-lab">Nom complet</div>%s</div></div>'
    '<div class="s-ligne"><div><div class="s-lab">Téléphone</div>%s</div><div><div class="s-lab">E-mail</div>%s</div></div>'
    '<div class="s-lab">Message (optionnel)</div><div class="t08-zone"></div>'
    '<div class="s-gros-bt t08-gros" id="t08-envoyer">Envoyer la demande</div></div>'
    % (entree('t08-s-arr', 'jj/mm/aaaa'), entree('t08-s-dep', 'jj/mm/aaaa'), entree('t08-s-ad', '', '2'),
       entree('t08-s-nom'), entree('t08-s-tel'), entree('t08-s-mail'))))

MERCI_SEJOUR = vue_site('t08-merci2', (
    '<div class="s-merci"><div class="h">Merci !</div>'
    '<div class="p">Votre demande de séjour <b id="t08-merci2-ref">%s</b> est bien transmise.</div>'
    '<div class="q">Notre réception vous confirme la chambre et le tarif très rapidement.</div>'
    '<div class="t08-retour-bt"><span class="s-bouton contour">Retour aux réservations</span></div></div>' % REF_SEJOUR),
    haut_pied=380)

SITE_WEB = site_t08('t08-site', [ACCUEIL, ESPACES, GRILLE_14, GRILLE_17, MERCI, AUTRE, REFUS, SEJOUR, MERCI_SEJOUR])


# ==================================================== la réception (MuK) ==

def chip(libelle, actif=False, point=None, ident=None):
    p = '<i class="t08-point" style="background:%s"></i>' % point if point else ''
    return '<span class="t08-chip%s"%s>%s%s</span>' % (' actif' if actif else '', ' id="%s"' % ident if ident else '',
                                                      p, e(libelle))


def kpi_t08(libelle, valeur, sous, accent):
    return ('<div class="t08-kpi %s"><div class="l">%s</div><div class="v">%s</div><div class="s">%s</div></div>'
            % (accent, e(libelle), e(valeur), e(sous)))


def couloir(ident, nom, couleur, ouverture, fermeture, pas, blocs):
    """Un couloir du planning : repères toutes les deux heures, blocs
    réservés {client, de, a, etat, id} (heures décimales ; état
    ``confirmed`` bleu, ``done`` vert), créneaux libres « x/y »."""
    span = float(fermeture - ouverture)
    reperes = ''.join('<i class="t08-rep" style="left:%.2f%%"></i>' % ((h - ouverture) / span * 100)
                      for h in range(ouverture, fermeture + 1, 2) if h > ouverture)
    total = int(round(span * 60 / pas))
    pris = int(round(sum((b['a'] - b['de']) * 60 / pas for b in blocs)))
    html = ''.join('<div class="t08-bk%s"%s style="left:%.2f%%;width:%.2f%%">%s</div>'
                   % (' fait' if b.get('etat') == 'done' else '', ' id="%s"' % b['id'] if b.get('id') else '',
                      (b['de'] - ouverture) / span * 100, (b['a'] - b['de']) / span * 100, e(b['client']))
                   for b in blocs)
    return ('<div class="t08-lane" id="%s"><div class="t08-lane-nom"><i class="t08-point" style="background:%s"></i>'
            '<span>%s</span></div><div class="t08-piste">%s%s</div><div class="t08-libre">%d/%d créneaux libres</div>'
            '</div>' % (ident, couleur, e(nom), reperes, html, total - pris, total))


def bloc(client, de, a, etat='confirmed', ident=None):
    return {'client': client, 'de': de, 'a': a, 'etat': etat, 'id': ident}


VIOLET, VERT, BRUN = '#714B67', '#0F6E56', '#854F0B'
# Les cinq ressources de l'établissement de démonstration : (nom, couleur,
# ouverture, fermeture, pas en minutes).
RESSOURCES = [(SALON, VIOLET, 9, 23, 60), ('Salon VIP Nyong', VIOLET, 9, 23, 60), ('Salon VVIP Dibamba', VIOLET, 10, 23, 60),
              ('Cabine massage 1', VERT, 9, 21, 30), ('Fauteuil tresses 1', BRUN, 9, 20, 30)]
# Le mercredi 14/10 (aujourd'hui, en fin de matinée) : deux prestations du
# matin réalisées, cinq réservations confirmées à venir.
JOUR_14 = [[bloc('Cécile Ondoa', 12, 14), bloc('Bertrand Mvondo', 16, 20)],
           [bloc('Thierry Ngando', 18, 22)],
           [bloc('Rachel Ebongue', 14, 17)],
           [bloc('Estelle Ngono', 10, 11, 'done'), bloc('Nadia Belinga', 16, 17.5)],
           [bloc('Linda Eboa', 9, 11, 'done')]]
# Le samedi 17/10 : la réservation en ligne de Claire est déjà dans le couloir du salon.
JOUR_17 = [[bloc('Aline Nkengue', 12, 14), bloc(NOM, 16, 17, ident='t08-bk-claire'), bloc('Rodrigue Tchoua', 19, 21)],
           [bloc('Carine Mbida', 10, 12), bloc('Joseph Ekani', 18, 20)],
           [bloc('Grâce Nguene', 15, 19)],
           [bloc('Nadège Owona', 11, 12), bloc('Sandrine Kemajou', 15, 16.5)],
           [bloc('Gisèle Tamba', 9.5, 11.5), bloc('Linda Eboa', 14, 15)]]
COULOIRS_14 = ''.join(couloir('t08-c14-%d' % i, *r, blocs=j) for i, (r, j) in enumerate(zip(RESSOURCES, JOUR_14), 1))
COULOIRS_17 = ''.join(couloir('t08-c17-%d' % i, *r, blocs=j) for i, (r, j) in enumerate(zip(RESSOURCES, JOUR_17), 1))

# Les indicateurs de la période « Aujourd'hui » (slot_dashboard.get_kpis),
# cohérents avec le planning du 14/10 : CA des deux prestations réalisées
# (20 000 + 15 000), heures réservées (confirmées + réalisées) sur les heures
# ouvrées des cinq ressources (64 h), aucune ressource de pressing.
HEURES = sum(b['a'] - b['de'] for jour in JOUR_14 for b in jour)
OUVERTES = sum(r[3] - r[2] for r in RESSOURCES)
A_VENIR = sum(1 for jour in JOUR_14 for b in jour if b['etat'] == 'confirmed')
REMPLISSAGE = ('%.1f %%' % (HEURES / OUVERTES * 100)).replace('.', ',')
HEURES_TXT = ('%g h' % HEURES).replace('.', ',')

TDB = vue_libre('t08-tdb', (
    '<div class="t08-d"><div class="t08-d-top"><div><div class="t08-d-titre">Espaces & Prestations</div>'
    '<div class="t08-d-sous">Planning des créneaux · SPA, coiffure, pressing, espaces VIP / VVIP</div></div>'
    '<span class="t08-d-nouv">+ Nouvelle réservation</span></div>'
    '<div class="t08-d-filtres"><div class="t08-d-rang"><span class="t08-d-lab">Jour</span>%s'
    '<span class="t08-d-date"><span id="t08-jour">14/10/2026</span><span class="t08-cal">%s</span></span>%s%s'
    '<span class="t08-esp"></span><span class="t08-d-lab">Période stats</span>%s%s%s</div>'
    '<div class="t08-d-rang"><span class="t08-d-lab">Famille</span>%s%s%s%s%s%s</div>'
    '<div class="t08-d-rang"><span class="t08-d-lab">Ressource</span>%s%s</div></div>'
    '<div class="t08-d-sect">Activité de la période</div><div class="t08-d-kpis">%s%s%s%s</div>'
    '<div class="t08-d-sect" id="t08-plan-t">Planning du 2026-10-14</div>'
    '<div class="t08-d-carte"><div class="t08-lanes" id="t08-l14">%s</div>'
    '<div class="t08-lanes t08-dessus masque" id="t08-l17">%s</div></div></div>'
    % (chip('‹', ident='t08-prec'), CAL, chip('›', ident='t08-suiv'), chip("Aujourd'hui"),
       chip("Aujourd'hui", True), chip('Cette semaine'), chip('Ce mois'),
       chip('Toutes', True), chip('Espace VIP / VVIP', point=VIOLET), chip('SPA', point=VERT),
       chip('Coiffure', point='#185FA5'), chip('Pressing', point=BRUN), chip('Autre', point='#888780'),
       chip('Toutes', True), ''.join(chip(r[0], point=r[1]) for r in RESSOURCES),
       kpi_t08('CA prestations réalisées', '35 000 FCFA', '2 réalisée(s)', 'a-violet'),
       kpi_t08('Taux de remplissage', REMPLISSAGE, '%s réservées / %d h ouvrées' % (HEURES_TXT, OUVERTES), 'a-bleu'),
       kpi_t08('No-show', '0 %', '0 rendez-vous manqué(s)', 'a-rouge'),
       kpi_t08('Retraits pressing en attente', '0', '%d réservation(s) à venir' % A_VENIR, 'a-ambre'),
       COULOIRS_14, COULOIRS_17)), initiale=True, fond='tdb')

FICHE = vue_fiche(
    't08-fiche', cp_fiche('Espaces & Prestations — Tableau de bord', REF_CRENEAU),
    [bouton('t08-realisee', 'Réalisée', 'primaire'), bouton(None, "Renvoyer l'e-mail", 'gris'),
     bouton(None, 'No-show', 'gris'), bouton(None, 'Annuler', 'gris')],
    statusbar('t08-sb', ['Brouillon', 'Confirmée', 'Réalisée'], 1),
    titre_fiche(REF_CRENEAU)
    + deux_colonnes(champ('Client', NOM) + champ('Téléphone', TEL_CLAIRE_N) + champ('Ressource', SALON)
                    + champ('Prestation', '') + champ('Origine', 'En ligne', 't08-f-origine', gras=False),
                    champ('Début', '17/10/2026 16:00:00') + champ('Fin', '17/10/2026 17:00:00')
                    + champ('Durée (h)', '01:00') + champ('Montant', '11 500 FCFA', 't08-f-montant')
                    + champ('Prix manuel', '0 FCFA'))
    + groupe('Séjour (note de chambre)', [champ('Folio du séjour', ''), champ('Ligne de folio', '')])
    + '<div class="t08-note">Note interne…</div>')

# Les réservations hôtel : brouillons regroupés par canal (groupes repliés).
COLS = '150px 180px 205px 205px 64px 104px 1fr 116px 136px 118px'
TETE = ['Référence', 'Client', 'Arrivée', 'Départ', 'Nuits', 'Nb chambres', 'Total hébergement (HT)', 'Solde folio',
        'Registre', 'État']
DROITE = {4, 5, 6, 7}


def ligne_resa(ident, cellules, masque=False):
    cs = []
    for k, c in enumerate(cellules):
        if k == 8:
            cs.append('<span><span class="puce rouge t08-badge">%s</span></span>' % e(c))
        elif k == 9:
            cs.append('<span><span class="puce orange t08-badge">%s</span></span>' % e(c))
        else:
            cs.append('<span class="ell%s">%s</span>' % (' d' if k in DROITE else '', e(c)))
    return ('<div class="ligne t08-ligne%s" id="%s" style="grid-template-columns:40px %s"><span class="cb"></span>%s</div>'
            % (' masque' if masque else '', ident, COLS, ''.join(cs)))


def groupe_resa(ident, libelle, nuits, chambres, total):
    return ('<div class="ligne t08-grp" id="%s" style="grid-template-columns:40px %s"><span></span>'
            '<span class="t08-grp-l"><b id="%s-fl">▸</b> %s</span><span class="d">%s</span><span class="d">%s</span>'
            '<span class="d">%s</span><span></span><span></span><span></span></div>'
            % (ident, COLS, ident, e(libelle), nuits, chambres, total))


RECH = ('<div class="recherche t08-rech">%s<span class="facette">%s<span class="ell">Brouillons</span><span class="fx">×'
        '</span></span><span class="facette">%s<span class="ell">Canal</span><span class="fx">×</span></span>'
        '<span class="ph">Rechercher…</span><span class="deroule">▾</span></div>'
        % (icone('loupe', 'loupe'), icone('filtre', 'fic'), '<span class="fic">%s</span>' % COUCHES))
RESAS = vue_libre('t08-resas', (
    '<div class="cp"><span class="bt primaire">Nouveau</span><span class="titre">Réservations</span>%s'
    '<span class="pager">1-2 / 2</span></div><div class="liste t08-liste">'
    '<div class="tete" style="grid-template-columns:40px %s"><span class="cb"></span>%s</div>%s%s%s%s'
    '<div class="total t08-total" style="grid-template-columns:40px %s"><span></span><span></span><span></span>'
    '<span></span><span></span><span></span><span></span><span class="d">90 000</span><span></span><span></span>'
    '<span></span></div></div>'
    % (RECH, COLS, ''.join('<span class="ell%s">%s</span>' % (' d' if k in DROITE else '', e(t))
                           for k, t in enumerate(TETE)),
       groupe_resa('t08-g-tel', 'Téléphone / WhatsApp (1)', '2', '1', '90 000'),
       groupe_resa('t08-g-web', 'Site web (2)', '5', '0', '0'),
       ligne_resa('t08-r-0219', ['RES/2026/0219', 'Yannick Mbassi', '24/10/2026 14:00:00', '26/10/2026 11:00:00', '2',
                                 '0', '0 FCFA', '0 FCFA', 'Aucune fiche', 'Brouillon'], masque=True),
       ligne_resa('t08-r-0221', [REF_SEJOUR, NOM, '20/10/2026 14:00:00', '23/10/2026 11:00:00', '3', '0', '0 FCFA',
                                 '0 FCFA', 'Aucune fiche', 'Brouillon'], masque=True),
       COLS)))

MENUS = ['Front Desk', 'Réservations', 'Espaces & Prestations', 'Notes de chambre en attente', 'Facturation',
         'Fidélité', 'Gouvernante']
DD_RES = ('<div class="t08-dd masque" id="t08-dd-res"><div id="t08-dd-res-1">Réservations</div>'
          '<div>Planning des chambres</div></div>')
BACK = fenetre_muk('t08-app', 'Hôtel', MENUS, [TDB, FICHE, RESAS], actif='Espaces & Prestations',
                   societe=demo.SOCIETE, initiale=RECEPTION[0], avatar='#185FA5', apps=APPS_PROFIL['reception'],
                   app_active='Hôtel')
BACK = BACK.replace('<span class="menu actif">Espaces &amp; Prestations</span>',
                    '<span class="menu actif t08-m" id="t08-m-ep">Espaces &amp; Prestations</span>', 1)
BACK = BACK.replace('<span class="menu">Réservations</span>',
                    '<span class="menu t08-m" id="t08-m-res">Réservations%s</span>' % DD_RES, 1)

# Deux cadres de navigateur superposés : le site public, puis le back-office
# de la réception, qui se pose dessus comme un changement d'écran.
ECRAN = (navigateur(SITE_WEB)
         + navigateur(BACK, identifiant='t08-nav-bo').replace('class="navigateur"', 'class="navigateur masque"', 1))

CSS = """
.app.t08-site { left: 0; top: 40px; width: 1720px; height: 796px; border-radius: 0; box-shadow: none; z-index: 1;
  background: #fff; color: #212529; }
.t08-site .s-nav { padding: 0 150px; gap: 24px; }
.t08-site .t08-logo { color: #243742; margin-right: 18px; }
.t08-site .s-m { color: #495057; }
.t08-site .s-m.actif { color: #212529; font-weight: 500; }
.t08-loupe { margin-left: auto; width: 50px; height: 50px; border-radius: 50%; background: #E9ECEF; display: flex;
  align-items: center; justify-content: center; }
.t08-loupe .ico { width: 22px; height: 22px; display: inline-flex; }
.t08-site .t08-tel { margin-left: 0; color: #495057; }
.t08-connexion { height: 46px; padding: 0 16px; border: 1px solid #DEE2E6; border-radius: 6px; display: flex;
  align-items: center; font-size: 19px; color: #495057; }
.t08-site .s-bt, .t08-site .s-bouton, .t08-site .s-gros-bt { background: #243742; color: #fff; }
.t08-site .s-bouton.contour { background: #fff; color: #243742; border: 1px solid #243742; }
.t08-site .s-carte .p { color: #495057; }
.t08-salons .s-carte .p { min-height: 0; color: #5C636A; }
.t08-site .entree { height: 56px; font-size: 21px; }
.t08-site .entree.focus { border-color: #243742; box-shadow: 0 0 0 4px rgba(36,55,66,.18); }
.t08-form { width: 900px; }
.t08-retour { font-size: 20px; color: #5C636A; }
.t08-h1.s-h1 { font-size: 50px; margin-top: 4px; }
.t08-prix { margin-top: 6px; color: #5C636A; }
.t08-alerte { margin-top: 12px; padding: 12px 20px; border-radius: 6px; background: #FFF3CD; border: 1px solid #FFE69C;
  color: #664D03; font-size: 20px; }
.t08-ligne-date { display: flex; gap: 10px; align-items: flex-end; margin-top: 6px; }
.t08-date { position: relative; width: 270px; }
.t08-date .entree { margin-top: 0; }
#t08-g14-date-ph { color: #212529; font-weight: 500; }
.t08-cal { position: absolute; right: 16px; top: 50%; width: 22px; height: 22px; margin-top: -11px; color: #212529;
  display: inline-flex; }
.t08-cal svg { width: 100%; height: 100%; }
.t08-voir { height: 56px; padding: 0 22px; border-radius: 6px; background: #2D3142; color: #fff; display: inline-flex;
  align-items: center; font-size: 21px; }
.t08-h5 { margin-top: 18px; font-size: 24px; font-weight: 500; color: #212529; }
.t08-creneaux { margin-top: 10px; gap: 10px; }
.t08-site .t08-cr { width: 116px; height: 46px; border-color: #198754; color: #146C43; font-size: 20px; }
.t08-site .t08-cr.coche { background: #D1E7DD; }
.t08-site .t08-cr.coche i { border: 5px solid #243742; }
.t08-coord { margin-top: 10px; }
.t08-coord .entree { margin-top: 0; }
.t08-gros.s-gros-bt { margin-top: 18px; height: 60px; }
.t08-site .s-note { margin-top: 10px; color: #5C636A; }
.t08-noir.q { color: #212529; }
.t08-retour-bt { margin-top: 22px; }
.t08-retour-bt .s-bouton { display: inline-flex; padding: 0 22px; }
.t08-form-s { width: 820px; }
.t08-form-s .s-lab { margin-top: 14px; }
.t08-l12 { grid-template-columns: 1fr 2fr; }
.t08-pied { position: absolute; left: 0; right: 0; height: 420px; background: #111827; padding: 54px 150px 0;
  display: flex; gap: 0; }
.t08-pc { width: 300px; }
.t08-pc-d { margin-left: auto; width: 440px; }
.t08-ph { font-size: 25px; font-weight: 500; color: #F8F9FA; margin-bottom: 18px; }
.t08-pl { font-size: 20px; line-height: 1.6; color: #9DB8CA; }
.t08-zone { margin-top: 10px; height: 74px; border: 1px solid #CED4DA; border-radius: 6px; background: #fff; }

.t08-m { position: relative; }
.t08-dd { position: absolute; left: -14px; top: 42px; min-width: 270px; padding: 8px 0; background: #fff; border-radius: 6px;
  box-shadow: 0 10px 28px rgba(0,0,0,.22); z-index: 30; color: #212529; font-size: 19px; font-weight: 400; }
.t08-dd div { padding: 9px 22px; white-space: nowrap; }
.t08-dd div:first-child { background: #EEF2F5; }

.t08-d { position: absolute; inset: 0; padding: 12px 18px; overflow: hidden; color: #2B2A28; }
.t08-d-top { background: #fff; border: 1px solid rgba(0,0,0,.08); border-radius: 12px; padding: 10px 20px; display: flex;
  align-items: center; justify-content: space-between; }
.t08-d-titre { font-size: 25px; font-weight: 700; color: #714B67; }
.t08-d-sous { margin-top: 2px; font-size: 16px; color: #6E6D68; }
.t08-d-nouv { height: 42px; padding: 0 16px; border-radius: 6px; background: var(--muk-prim); color: #fff; font-size: 18px;
  display: inline-flex; align-items: center; }
.t08-d-filtres { margin-top: 8px; background: #fff; border: 1px solid rgba(0,0,0,.08); border-radius: 12px; padding: 6px 16px; }
.t08-d-rang { display: flex; align-items: center; gap: 8px; height: 42px; }
.t08-d-rang + .t08-d-rang { margin-top: 6px; padding-top: 6px; height: 48px; border-top: 1px dashed rgba(0,0,0,.12); }
.t08-d-lab { min-width: 108px; font-size: 14px; font-weight: 600; letter-spacing: .05em; text-transform: uppercase;
  color: #6E6D68; }
.t08-chip { height: 38px; padding: 0 14px; border: 1px solid rgba(0,0,0,.12); border-radius: 8px; display: inline-flex;
  align-items: center; gap: 7px; font-size: 16px; color: #4F4E4A; background: #fff; white-space: nowrap; }
.t08-chip.actif { background: #714B67; border-color: #714B67; color: #fff; }
#t08-prec, #t08-suiv { width: 40px; justify-content: center; padding: 0; font-size: 20px; background: #F5F5F4; }
.t08-point { width: 11px; height: 11px; border-radius: 50%; display: inline-block; flex: none; }
.t08-d-date { position: relative; height: 40px; width: 180px; border: 1px solid rgba(0,0,0,.12); border-radius: 8px;
  display: inline-flex; align-items: center; padding-left: 12px; font-size: 16px; color: #2B2A28; }
.t08-d-date .t08-cal { right: 10px; width: 18px; height: 18px; margin-top: -9px; }
.t08-esp { flex: 1; }
.t08-d-sect { margin: 10px 4px 6px; font-size: 15px; font-weight: 700; letter-spacing: .06em; text-transform: uppercase;
  color: #6E6D68; }
.t08-d-kpis { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
.t08-kpi { background: #fff; border: 1px solid rgba(0,0,0,.08); border-left: 5px solid #714B67; border-radius: 12px;
  padding: 8px 16px; }
.t08-kpi.a-bleu { border-left-color: #185FA5; } .t08-kpi.a-rouge { border-left-color: #A32D2D; }
.t08-kpi.a-ambre { border-left-color: #854F0B; }
.t08-kpi .l { font-size: 13px; font-weight: 600; letter-spacing: .05em; text-transform: uppercase; color: #6E6D68;
  white-space: nowrap; }
.t08-kpi .v { margin-top: 2px; font-size: 26px; font-weight: 700; color: #2B2A28; white-space: nowrap; }
.t08-kpi .s { margin-top: 2px; font-size: 14px; color: #6E6D68; white-space: nowrap; }
.t08-d-carte { position: relative; background: #fff; border: 1px solid rgba(0,0,0,.08); border-radius: 12px; padding: 10px 16px; }
.t08-lanes { display: flex; flex-direction: column; gap: 7px; }
.t08-dessus { position: absolute; left: 16px; right: 16px; top: 10px; background: #fff; }
.t08-lane { display: flex; align-items: center; gap: 12px; }
.t08-lane-nom { width: 190px; flex: none; display: flex; align-items: center; gap: 9px; font-size: 16px; font-weight: 600;
  color: #46414E; white-space: nowrap; }
.t08-piste { position: relative; flex: 1; height: 38px; background: #F6F4F3; border: 1px solid #E7E2DF; border-radius: 6px;
  overflow: hidden; }
.t08-rep { position: absolute; top: 0; bottom: 0; border-left: 1px dashed #E1DBD7; }
.t08-bk { position: absolute; top: 4px; bottom: 4px; border-radius: 4px; background: #185FA5; color: #fff; font-size: 13px;
  line-height: 30px; padding: 0 6px; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; }
.t08-bk.fait { background: #0F6E56; }
.t08-libre { width: 175px; flex: none; text-align: right; font-size: 15px; color: #0F6E56; white-space: nowrap; }

#t08-fiche .feuille-cadre { right: 22px; }
.t08-note { margin-top: 18px; padding-bottom: 12px; border-bottom: 1px solid var(--o-filet); font-size: 19px; color: #6C757D; }
#t08-fiche .st-et { color: #545B62; }
#t08-fiche .st-et.actif { color: #212529; }
#t08-fiche .grp { margin-top: 18px; }

.t08-rech { margin-left: 150px; width: 700px; }
.t08-rech .facette .fic svg { width: 100%; height: 100%; }
.t08-liste .ligne, .t08-liste .tete, .t08-liste .total { column-gap: 12px; }
.t08-liste .tete { font-size: 18px; }
.t08-ligne { font-size: 18px; }
.t08-grp { background: #F1F3F5; font-weight: 500; }
.t08-grp-l { grid-column: 2 / span 4; white-space: nowrap; }
.t08-grp-l b { display: inline-block; width: 18px; font-weight: 400; }
.t08-badge { height: 28px; font-size: 15px; }
.t08-badge.orange { background: #F3B21B; color: #2B2100; }
.t08-total { color: #212529; }
"""

TUTORIEL = {
    'slug': 't08-site-web',
    'profil': 't08_site_web',
    'numero': 8,
    'titre': 'Réservation en ligne : vos clients réservent seuls, sans double vente',
    'fonction': 'Réservation en ligne',
    'personnage': (NOM, ROLE),
    'accroche': {
        'kicker': 'La réservation en ligne',
        'question': 'Votre site sait-il ce qui est *vraiment* libre ?',
        'douleurs': [('echange', 'Le même salon vendu deux fois'),
                     ('cahier', 'Chaque réservation ressaisie au back-office'),
                     ('globe', 'Pas de réservation directe ? 10 PMS leaders sur 10 en ont une'),
                     ('pieces', 'SaaS étrangers : 280 à 480 KFCFA par mois'),
                     ('cadenas', 'Odoo Community : moteur de réservation « à développer »')],
        'voix': "Votre site sait-il ce qui est vraiment libre ? Un salon vendu deux fois, des réservations ressaisies "
                "à la main, des abonnements étrangers coûteux.",
    },
    'revelation': {
        'promesse': "Le client réserve seul, parmi les créneaux libres : c'est confirmé et déjà au planning.",
        'voix': "Avec Aïte haousse, vos clients réservent seuls : confirmé tout de suite, et déjà inscrit à la "
                "réception.",
    },
    'temps': ['Choisir', 'Réserver', 'Retrouver'],
    'app': 't08-site',
    'ecran': ECRAN,
    'css': CSS,
    'vues_initiales': {'site': 't08-accueil', 'odoo': 't08-tdb'},
    'bulles': {
        'b-public': 'Pages publiques : ni compte à créer, ni mot de passe.',
        'b-grille': "La même grille qu'à la réception.",
        'b-refus': 'Créneau pris entre-temps : la seconde réservation est refusée.',
        'b-origine': 'Créée et confirmée par le site : rien à ressaisir.',
        'b-brouillon': "Aucune chambre n'est bloquée tant que la réception n'a pas confirmé.",
    },
    'reactions': {
        'r-merci': "Réservé et confirmé, sans passer un seul appel.",
    },
    'etapes': [
        {'temps': 0, 'titre': 'Réserver en ligne, sans compte',
         'texte': 'Trois entrées publiques ; seuls les salons ouverts en ligne sont proposés.',
         'voix': "Sur le site de l'hôtel, la page Réserver en ligne est publique : ni compte, ni mot de passe. Claire "
                 "choisit un salon : seuls ceux ouverts en ligne par l'hôtel s'affichent, avec horaires et prix à "
                 "l'heure.",
         'gestes': [pause(0.3), anneau('#t08-acc-cartes', d=1.3), bulle('b-public', '#t08-acc-titre', cote='droite', d=2.6),
                    pause(2.2), clic('#t08-vip-bt'), vue('t08-espaces', 'site'), pause(0.4),
                    anneau('#t08-salons', d=1.4), pause(0.6), clic('#t08-e1-bt'), vue('t08-g14', 'site'), pause(0.3)]},
        {'temps': 0, 'titre': 'Les créneaux encore libres',
         'texte': 'Une date, et la grille ne propose que les heures disponibles.',
         'voix': "Claire choisit samedi : la grille ne montre que les heures encore libres. Ce qui est déjà réservé, "
                 "au comptoir ou en ligne, n'y figure plus. Elle coche seize heures, pour une heure.",
         'gestes': [clic('#t08-g14-date', fx=0.3), saisir('t08-g14-date', '17/10/2026'), clic('#t08-g14-voir'),
                    vue('t08-g17', 'site'), pause(0.2), zoom('#t08-g17-creneaux', s=1.55, d=0.7),
                    bulle('b-grille', '#t08-g17-h22', cote='droite', d=2.4), pause(1.6), clic('#t08-g17-h16'),
                    classe('#t08-g17-h16', ajouter=['coche']), pause(0.7), dezoom(d=0.6)]},
        {'temps': 1, 'titre': 'Réservé, confirmé sur-le-champ',
         'texte': "Nom, téléphone, e-mail : la référence s'affiche, l'acompte se règle au comptoir.",
         'voix': "Nom, téléphone, courriel, puis Réserver ce créneau : c'est confirmé sur-le-champ, avec sa référence. "
                 "L'acompte se règle au comptoir, Orange Moni, MTN MoMo ou espèces.",
         'gestes': [saisir('t08-g17-nom', NOM), saisir('t08-g17-tel', TEL_CLAIRE), saisir('t08-g17-mail', MAIL_CLAIRE),
                    clic('#t08-g17-reserver'), vue('t08-merci', 'site'), zoom('#t08-merci-bloc', s=1.4, d=0.7),
                    anneau('#t08-merci-ref', d=1.4), reaction('r-merci', d=3.0), pause(0.6),
                    anneau('#t08-acompte', d=1.6), pause(0.6), dezoom(d=0.6)]},
        {'temps': 1, 'titre': 'Pas de double vente',
         'texte': 'Un second visiteur valide le même créneau : refusé, il en choisit un autre.',
         'voix': "Un autre visiteur, resté sur la page, valide seize heures à son tour : trop tard. Le site refuse la "
                 "seconde réservation, lui demande un autre créneau, et seize heures a disparu de la grille.",
         'gestes': [vue('t08-ga', 'site'), pause(0.4), anneau('#t08-ga-h16', d=1.0), clic('#t08-ga-reserver'),
                    vue('t08-gr', 'site'), pause(0.3), zoom('#t08-gr-alerte', s=1.5, d=0.7),
                    bulle('b-refus', '#t08-gr-alerte', cote='bas', d=2.6), pause(2.3), dezoom(d=0.6),
                    anneau('#t08-gr-creneaux', d=1.4)]},
        {'temps': 1, 'titre': 'Demander un séjour',
         'texte': 'Dates, adultes, coordonnées : la demande part à la réception, avec sa référence.',
         'voix': "Pour une chambre, Claire envoie une demande de séjour : ses dates, le nombre d'adultes, ses "
                 "coordonnées. Sa référence s'affiche aussitôt. La réception vérifiera la disponibilité, puis lui "
                 "confirmera la chambre et le tarif.",
         'gestes': [vue('t08-accueil', 'site'), pause(0.2), clic('#t08-ch-bt'), vue('t08-sejour', 'site'),
                    saisir('t08-s-arr', '20/10/2026'), saisir('t08-s-dep', '23/10/2026'), saisir('t08-s-nom', NOM),
                    saisir('t08-s-tel', TEL_CLAIRE), saisir('t08-s-mail', MAIL_CLAIRE), clic('#t08-envoyer'),
                    vue('t08-merci2', 'site'), pause(0.3), anneau('#t08-merci2-ref', d=1.5), pause(0.5)]},
        {'temps': 2, 'titre': 'Déjà au planning de la réception',
         'texte': 'Confirmée, origine « En ligne », montant calculé : rien à ressaisir.',
         'voix': "À la réception, Mireille ouvre le tableau de bord Espaces et Prestations et passe à samedi : la "
                 "réservation de Claire occupe déjà le salon. Confirmée, origine en ligne, onze mille cinq cents "
                 "francs calculés tout seuls : rien à ressaisir.",
         'gestes': [montrer('#t08-nav-bo', d=0.45, y=0), pause(0.4), clic('#t08-suiv'),
                    texte('#t08-jour', '15/10/2026'), texte('#t08-plan-t', 'Planning du 2026-10-15'),
                    clic('#t08-suiv', deplacer=False, puis=0.1), texte('#t08-jour', '16/10/2026'),
                    texte('#t08-plan-t', 'Planning du 2026-10-16'),
                    clic('#t08-suiv', deplacer=False, puis=0.1), texte('#t08-jour', '17/10/2026'),
                    texte('#t08-plan-t', 'Planning du 2026-10-17'), montrer('#t08-l17', d=0.3, y=0), pause(0.3),
                    anneau('#t08-c17-1', d=1.4), anneau('#t08-bk-claire', d=1.2), clic('#t08-bk-claire'),
                    vue('t08-fiche', 'odoo'), pause(0.3), bulle('b-origine', '#t08-f-origine', cote='bas', d=2.4),
                    pause(2.2), anneau('#t08-f-montant', d=1.5), pause(0.6)]},
        {'temps': 2, 'titre': 'La demande de séjour, en brouillon',
         'texte': "Canal « Site web » : la chambre n'est bloquée qu'à la confirmation.",
         'voix': "La demande de séjour, elle, attend en brouillon, avec le site pour canal. Mireille y ajoute une "
                 "chambre et clique sur Confirmer : la disponibilité est vérifiée, la chambre bloquée, le folio "
                 "ouvert.",
         'gestes': [clic('#t08-m-res'), montrer('#t08-dd-res', d=0.2, y=0), clic('#t08-dd-res-1', d=0.4),
                    cacher('#t08-dd-res', d=0.15), classe('#t08-m-ep', retirer=['actif']),
                    classe('#t08-m-res', ajouter=['actif']), vue('t08-resas', 'odoo'), pause(0.4),
                    clic('#t08-g-web', fx=0.12), texte('#t08-g-web-fl', '▾'), montrer('#t08-r-0219', d=0.25, y=0),
                    montrer('#t08-r-0221', d=0.25, y=0, avec=True), zoom('#t08-r-0221', s=1.35, d=0.7),
                    anneau('#t08-r-0221', d=1.2), bulle('b-brouillon', '#t08-r-0221', cote='bas', d=2.6),
                    pause(2.2), dezoom(d=0.6)]},
    ],
    'resultats': {
        'titre': 'Réservé en ligne, retrouvé à la réception',
        'cartes': [
            {'valeur': '3', 'compter': 3, 'unite': 'parcours', 'icone': 'globe',
             'texte': 'publics sur une même page : salons, spa et coiffure, chambres — sans compte'},
            {'valeur': '1', 'compter': 1, 'unite': 'grille', 'icone': 'horloge',
             'texte': 'de disponibilités pour le site et la réception : une seule source'},
            {'valeur': '45', 'compter': 45, 'unite': 'tests', 'icone': 'bouclier',
             'texte': "automatisés du tunnel public, dont le refus d'une double réservation"},
        ],
        'voix': "Trois parcours publics, une seule grille pour le site et la réception, et quarante-cinq tests "
                "automatisés, dont le refus d'une double réservation.",
    },
    'cta': {
        'appel': 'Demandez votre démonstration',
        'suivant': 'Espaces et prestations',
        'voix': "Aïte haousse, par Aïte Consulting. Demandez votre démonstration, et retrouvez tous nos tutoriels sur "
                "notre chaîne.",
    },
    'vignette': {'etape': 6, 'apres': 6.0},
}
