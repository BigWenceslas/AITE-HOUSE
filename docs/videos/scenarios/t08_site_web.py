# -*- coding: utf-8 -*-
"""Tutoriel 8 — Réservation en ligne : vos clients réservent seuls, sur les créneaux encore libres.

Format marketing du pilote ``t07_gouvernante.py`` : accroche, révélation,
sept étapes (le site public, puis la réception), résultats, appel.

Sources des écrans (libellés vérifiés mot pour mot par ``grep -rF`` dans
``addons/``) :

- Site public — ``aite_website_booking/views/website_templates.xml`` :
  accueil « Réserver en ligne » et ses trois cartes (l. 5-41) ; liste
  « Espaces VIP & VVIP », « Ouvert de HH:MM à HH:MM », prix « 15 000 FCFA /
  heure » (format ``'{:,.0f}'`` + espace + symbole de la devise, l. 44-71) ;
  grille « ← Tous les espaces », « Date », « Voir ce jour », « Créneaux
  disponibles », « Vos coordonnées », « Réserver ce créneau », mention de
  l'acompte, bandeau « Ce créneau vient d'être pris — choisissez-en un
  autre. » (l. 74-130) ; « Demande de séjour » et ses champs (l. 233-277) ;
  page « Merci ! » d'un créneau et d'un séjour (l. 280-300). Menu du site
  « Réservation » : ``data/website_menu_data.xml`` ; autres entrées de
  l'en-tête (Accueil, Contactez-nous, Se connecter) et pied de page par
  défaut d'Odoo 18 (``odoo18/addons/website/views/website_templates.xml``
  l. 1661-1690 : « Liens utiles », « À propos de nous » et son texte,
  « Rejoignez-nous ») dans sa traduction française
  (``odoo18/addons/website/i18n/fr.po`` l. 2388, 4539, 4617, 7865, 9309,
  11846, 12967, 15364, 15701-15713 ; ``portal/i18n/fr.po`` « Se connecter »).
- Tunnel — ``aite_website_booking/controllers/main.py`` : routes
  ``auth='public'`` (l. 69-146, 228-238) ; seules les ressources
  « Réservable en ligne » (l. 59-63, 78-91) ; grille = ``get_day_grid``, seuls
  les créneaux ``free`` (l. 92-100) ; fin = début + un pas, création
  ``source='online'`` puis ``action_confirm`` sous point de sauvegarde, refus
  → retour sur la grille avec ``error=slot`` (l. 157-222) ; demande de séjour
  en brouillon, canal ``website``, arrivée 14:00 et départ 11:00 (l. 236-278) ;
  client retrouvé par téléphone normalisé puis par e-mail, sinon créé
  (``models/website_booking.py`` l. 21-31, 74-91).
- Moteur de créneaux — ``aite_slot_booking/models/booking_resource.py``
  (``get_day_grid``, « source de vérité unique » du site et du tableau de
  bord, l. 27-30, 157-223 : seules les réservations confirmées ou réalisées
  occupent la grille, l. 182-183 ; champ « Réservable en ligne », l. 74-77) ;
  ``models/booking_booking.py`` (états, « Origine » Comptoir / En ligne
  l. 87-101, montant = heures × tarif horaire ``_slot_price`` l. 126-138,
  conflit refusé au-delà de la capacité ``_check_no_conflict`` l. 260-282) ;
  ``data/slot_sequence_data.xml`` (référence ``RES/%(y)s/`` sur 4 chiffres
  → RES/26/0131).
- Réception — tableau de bord ``aite_slot_booking/static/src/xml/dashboard.xml``
  (titre, filtres Jour / Période stats / Famille / Ressource, quatre
  indicateurs, « Chargement… » pendant le rechargement l. 71-73, « Planning
  du <t t-esc="state.day"/> », couloirs, « x/y créneaux libres », l. 18-128 ;
  section « Répartition & remplissage » et ses deux cartes, l. 131-140 ;
  rangées de puces à la ligne, ``slot_dashboard.scss`` l. 58-69),
  ``static/src/js/views/slot_dashboard_view.js`` (un changement de jour
  recharge tout l'écran, l. 72-112 ; repères toutes les deux heures
  l. 204-215, texte des créneaux libres l. 221-231, clic sur un bloc → fiche
  l. 322-330), ``static/src/js/services/utils.js`` (formats montant, %,
  heures), ``static/src/scss/slot_dashboard.scss`` (couleurs, l. 148-152),
  ``models/slot_dashboard.py`` (couleurs des familles l. 22-25, indicateurs
  ``get_kpis`` l. 124-176 : CA des réalisées, heures réservées / heures
  ouvrées, réservations à venir) ; fiche ``views/booking_booking_views.xml``
  (boutons et statusbar l. 37-59, champs l. 60-91, ``<chatter/>`` l. 92) ;
  nom de l'action ``views/slot_dashboard_actions.xml``. Discussion : message
  de création « %s créé » (``odoo18/addons/mail/models/mail_thread.py``
  l. 452-458, ``mail/i18n/fr.po`` l. 269-270) et suivi de l'état (champ
  ``tracking=True``, booking_booking.py l. 95), signés par l'utilisateur
  courant (mail_thread.py l. 2913-2919), soit l'utilisateur public du site
  (``odoo18/addons/website/models/ir_http.py`` l. 175-182) dont le contact
  s'appelle « Public user » (``odoo18/odoo/addons/base/data/res_partner_data.xml``
  l. 28-31) avec l'avatar gris par défaut (base/models/res_partner.py
  l. 344-350) ; date « Aujourd'hui » / « Aujourd'hui à HH:MM »
  (mail/static/src/core/common/message_model.js l. 225-251) ; boutons
  « Envoyer message », « Note », « Suivre » (mail/i18n/fr.po), pas
  d'« Activités » (le modèle n'hérite que de ``mail.thread``) ; mise en page :
  ref_muk/027.
- Réservations hôtel — ``aite_hotel_management/views/hotel_reservation_views.xml``
  (liste l. 5-33, décorations, filtres « Arrivées du jour », « Départs du
  jour », « Clients présents », « Brouillons », « Confirmées », « No-show »,
  regroupements « État », « Client », « Hôtel », « Canal », « Date
  d'arrivée » l. 225-262 ; action sans filtre par défaut, vues
  list,kanban,form,calendar l. 265-279), ``models/hotel_reservation.py``
  (« Canal » et « Site web » l. 70-80, ordre ``checkin_date desc, id desc``
  l. 27, nuits / chambres / total stockés et donc sommés par groupe
  l. 64-116, Confirmer vérifie la disponibilité puis ouvre le folio
  l. 288-337, heures standard 14:00 / 12:00 l. 152-165) ;
  ``models/hotel_room.py`` l. 431-446 (seules les lignes confirmées ou en
  séjour occupent une chambre) ; colonne « Registre » / « Aucune fiche » :
  ``aite_guest_registry/views/hotel_reservation_views.xml`` l. 57-67 ; menus
  ``aite_hotel_management/views/hotel_menus.xml`` et
  ``aite_slot_booking/views/slot_menus.xml``. Cadre web d'Odoo 18
  (``odoo18/addons/web/i18n/fr.po``) : « Filtres », « Regrouper par »,
  « Favoris », « Ajouter un filtre personnalisé », « Ajouter un groupe
  personnalisé », « Enregistrer la recherche actuelle », « Rechercher… » ;
  menu de recherche ``web/static/src/search/search_bar_menu/search_bar_menu.xml``
  l. 4-135 ; sommes : ``web/static/src/views/list/list_renderer.js`` l. 561-660
  (liste simple : avec la devise ; liste regroupée : sans devise, à deux
  décimales — ``web/static/src/core/currency.js`` l. 32-51).
- Thème MuK et mise en page : captures de référence
  ``../aite-videos/ref_muk/500-site-reservation.png``, ``501-site-espaces.png``,
  ``502-site-chambres.png``, ``027-…-fiche.png``, ``049-…-tableau-de-bord.png``,
  ``050-…``, ``306-reception-reservations.png`` (engrenage, flèches du pager,
  sélecteur de vues, sélecteur de colonnes) ; captures de recette
  ``docs/captures_uat/r5-site-web-0[1-6]-*.png`` (modèle visuel seulement,
  jamais incrustées).

Douleurs de l'accroche : ``recette/cas_de_test.py`` l. 132-137 (B03, double
réservation d'un créneau) et l. 178-182 (C03, réservation « sans aucune
ressaisie ») ; ``docs/etude_comparative/benchmark_pms.md`` l. 150 (moteur de
réservation direct : 10 leaders sur 10) ; ``docs/etude_comparative/build_etude.py``
l. 420 (SaaS étrangers à 280-480 KFCFA par mois : Cloudbeds, Mews,
SiteMinder, c'est-à-dire PMS et channel manager) ;
``docs/etude_comparative/benchmark_afrique_odoo.md`` l. 153 (Community :
« moteur de réservation à développer »).

Promesse : bornée à ce que la vidéo montre et que le code garantit. Un
salon se réserve en ligne et se confirme aussitôt (``_confirm_slot``) ; un
séjour n'est qu'une demande en brouillon (``rooms_submit``). Les prestations
(spa, coiffure) ne sont pas promises : une prestation dont la durée n'est pas
un multiple du pas de la ressource échoue à chaque fois (voir les écarts). Le
refus d'un créneau déjà confirmé est prouvé pour des validations successives
(``test_double_booking_is_refused``) : le contrôle ne pose ni verrou ni
contrainte SQL (voir les écarts), d'où l'absence de toute promesse absolue
(« sans double vente », « jamais »). Titre et accroche disent « encore
libres » et « déjà vendu », pas « vraiment libre » : la grille ne cache que
les heures déjà réservées (confirmées ou réalisées) ; une heure déjà passée
du jour reste proposée et acceptée (pas d'attribut ``min`` sur le champ Date,
``website_templates.xml`` l. 90 ; ``_safe_day`` l. 52-57 ; ``get_day_grid``
l. 92-94 ; aucun contrôle début ≥ maintenant dans ``_confirm_slot`` ni dans
``_check_slot_valid``). La vidéo réserve un samedi à venir.

Résultats : trois parcours publics (``website_templates.xml`` l. 10-38) ;
une seule grille pour le site et la réception (``booking_resource.py``
l. 27-30, ``slot_dashboard.py`` l. 107-117, ``controllers/main.py`` l. 93) ;
45 tests Odoo du module, dont ``test_double_booking_is_refused``
(``docs/GUIDE_TESTS.md`` l. 31, ``aite_website_booking/tests/test_controllers.py``
l. 155-173 : 22 tests, ``test_helpers.py`` : 23 tests).

Données : fictives (``demo.py``). Claire Durand (cliente), Mireille Ateba
(réception). Les huit ressources (salons « Wouri », « Sanaga »,
« Bonabéri », cabines SPA 1 et 2, fauteuils homme 1 et femme 1, comptoir
pressing), leurs horaires, pas, capacités, tarifs horaires des salons
(15 000 / 25 000 FCFA) et le catalogue (massage relaxant 60 min 27 000,
coupe homme 6 200, tresses 19 000, chemise 4 800) sont ceux du tutoriel 9
(``scenarios/t09_espaces.py`` l. 192-219), qui suit celui-ci. Indicateurs du
14/10 recalculés sur ces huit ressources : 109 h ouvrées comme au tutoriel 9,
et deux dépôts de pressing non retirés, que le tutoriel 9 compte encore le
15/10 au matin avec celui de Samuel Etoga (``RETRAITS``, 3 puis 2). La
référence du créneau, RES/26/0131, précède celles que le tutoriel 9 crée le
15/10 (RES/26/0158 à 11:09). Claire reprend l'adresse de la série
(claire.durand@exemple.fr, ``t04_note_chambre.py`` l. 333) : le site
retrouve sa fiche, la réservation affiche le téléphone déjà enregistré
(voir ``TEL_FICHE``). Les réservations confirmées de la liste de l'hôtel,
celle de Rodrigue Tamba et le brouillon de Jacques Owona sont ceux du
tutoriel 2 (``scenarios/t02_planning.py`` l. 231-260, 277-289, 648-680 ;
tarifs Standard 35 000, Confort 45 000, Suite Junior 75 000, Suite VIP
120 000) ; le solde d'une réservation confirmée non réglée est son folio :
nuitées (sans TVA, convention de la série) plus la taxe de séjour, deux
adultes (``solde_folio``, comme au tutoriel 2 : 102 000 FCFA pour Rodrigue,
``FOLIO_RODRIGUE``, t02_planning.py l. 302-308). Les demandes du site
(RES/2026/0223, RES/2026/0224), le visiteur Arnaud Fotsing et les clients des
couloirs sont inventés. Numéros de fiction : plage ARCEP réservée à la
fiction (+33 6 39 98 …) et numéros camerounais en 6 00 00 00 … ; adresses
``exemple.cm``. Le pied de page du site est celui d'Odoo 18, personnalisé
par l'établissement (liens et texte « À propos de nous » fictifs, à la place
du texte d'exemple du gabarit).

Chronologie : « aujourd'hui » vaut le mercredi 14/10/2026 (``demo.ARRIVEES``).
Claire réserve le salon à 07:52, avant l'ouverture : la grille du jour
commence donc à 09:00 sans heure déjà passée. Le salon est réservé pour le
samedi 17/10/2026. Elle envoie sa demande de séjour plus tard dans la
matinée, vers 10:40 : après les réservations RES/2026/0221 et 0222 que le
tutoriel 2 crée à 10:06 et 10:09, et après celle de Yannick Mbassi
(RES/2026/0223) ; d'où RES/2026/0224. Mireille ouvre le tableau de bord vers
11:30 (prestations de 8 h à 11 h réalisées).

Écarts rejoués tels quels (voir le rapport) : « Planning du 2026-10-17 »
(date ISO, ``dashboard.xml`` l. 99) ; menu « Front Desk » en anglais
(``hotel_menus.xml`` l. 18) ; deux numérotations « RES » (RES/26/0131 pour
le créneau, RES/2026/0224 pour le séjour) ; départ de la demande de séjour
à 11:00, fixé en dur (``controllers/main.py`` l. 264-267) ; discussion signée
« Public user » (nom anglais du contact public) et « … créé » au masculin ;
sommes de groupe sans devise et à deux décimales (« 90 000,00 »). La liste
non filtrée des réservations charge 80 lignes (« 1-80 / 224 ») : sa ligne de
total, après la 80e, n'est pas à l'écran (le pied de liste d'Odoo 18 n'est
pas collant, ``web/static/src/views/list/list_renderer.scss`` l. 14-24,
194-199 ; somme sur les lignes chargées, ``list_renderer.js`` l. 561-570).
"""

import demo
from ecrans import (APPS_PROFIL, ICONES, bouton, champ, cp_fiche, deux_colonnes, e, entree, fenetre_muk, groupe,
                    icone, navigateur, s_vue, statusbar, titre_fiche, vue_fiche, vue_libre)
from marketing import bulle, dezoom, reaction, zoom
from moteur import animer, anneau, cacher, clic, classe, curseur, montrer, pause, saisir, texte, vue

NOM, ROLE = demo.POSTES['client']                 # Claire Durand, la cliente
RECEPTION, ROLE_RECEPTION = demo.POSTES['reception']   # Mireille Ateba, réceptionniste
VISITEUR, ROLE_VISITEUR = 'Arnaud Fotsing', 'Autre visiteur'
SITE = 'Complexe Hôtelier'
TEL_HOTEL = '+237 6 00 00 00 10'
TEL_CLAIRE = '+33 6 39 98 21 47'                  # saisi sur le site (plage ARCEP réservée à la fiction)
MAIL_CLAIRE = 'claire.durand@exemple.fr'          # l'adresse de Claire dans la série (t04_note_chambre.py l. 333)
# find_or_create_partner cherche d'abord le téléphone normalisé (égalité stricte,
# website_booking.py l. 80-82 : la fiche porte le numéro avec ses espaces, pas
# « +33639982147 »), puis l'e-mail (l. 83-85) : la fiche existante de Claire est
# retrouvée, sans doublon. La réservation affiche donc le téléphone déjà
# enregistré sur ce contact (partner_phone = related partner_id.phone,
# booking_booking.py l. 53-54) : le même numéro, celui de Claire dans toute la série.
TEL_FICHE = TEL_CLAIRE
TEL_VISITEUR = '+237 6 00 00 00 27'
SALON = 'Salon VIP Wouri'
REF_CRENEAU = 'RES/26/0131'                       # séquence RES/%(y)s/ (créneaux), avant celles du 15/10 (t09)
REF_SEJOUR = 'RES/2026/0224'                      # séquence RES/%(year)s/ (séjours)
REF_YANNICK = 'RES/2026/0223'
HEURE_RESA = '07:52'                              # l'heure où Claire a réservé le salon
# Tarif horaire des salons, comme au tutoriel 9 (t09_espaces.py l. 192-201).
TARIF_SALON, TARIF_VVIP = 15000, 25000

# Une icône de calendrier (champ date du navigateur), l'icône « regrouper
# par » des facettes d'Odoo 18 et celles du cadre web, redessinées en SVG.
CAL = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><rect x="3" y="4.5" width="18" '
       'height="16" rx="2"/><path d="M3 9.5h18M8 2.5v4M16 2.5v4"/></svg>')
COUCHES = ('<svg viewBox="0 0 24 24" fill="#fff"><path d="M12 3l9 4.5-9 4.5-9-4.5z"/><path d="M3 12l9 4.5 9-4.5" '
           'fill="none" stroke="#fff" stroke-width="2"/><path d="M3 16.5l9 4.5 9-4.5" fill="none" stroke="#fff" '
           'stroke-width="2"/></svg>')
COUCHES_N = COUCHES.replace('#fff', '#212529')
ROUAGE = ('<svg viewBox="0 0 24 24" fill="#495057"><path d="M10.3 2h3.4l.5 2.6 1.9.8 2.2-1.5 2.4 2.4-1.5 2.2.8 1.9 '
          '2.6.5v3.4l-2.6.5-.8 1.9 1.5 2.2-2.4 2.4-2.2-1.5-1.9.8-.5 2.6h-3.4l-.5-2.6-1.9-.8-2.2 1.5-2.4-2.4 1.5-2.2-.8-1.9'
          'L2 13.7v-3.4l2.6-.5.8-1.9-1.5-2.2 2.4-2.4 2.2 1.5 1.9-.8z"/><circle cx="12" cy="12" r="3.4" fill="#fff"/></svg>')
V_LISTE = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round">'
           '<path d="M4 6h16M4 12h16M4 18h16"/></svg>')
V_KANBAN = ('<svg viewBox="0 0 24 24" fill="currentColor"><rect x="3" y="4" width="7.5" height="16" rx="1"/>'
            '<rect x="13.5" y="4" width="7.5" height="10" rx="1"/></svg>')
V_CAL = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="5" width="18" '
         'height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/><path d="M7 14h3M14 14h3M7 17.5h3" stroke-width="2.4"/>'
         '</svg>')
REGLAGES = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">'
            '<path d="M4 7h10M18 7h2M4 17h4M12 17h8"/><circle cx="16" cy="7" r="2"/><circle cx="10" cy="17" r="2"/></svg>')
ETOILE = ('<svg viewBox="0 0 24 24" fill="#E8A33D"><path d="M12 2.8l2.8 5.9 6.4.8-4.7 4.4 1.2 6.4L12 17.2 6.3 20.3l1.2-6.4'
          'L2.8 9.5l6.4-.8z"/></svg>')
ENVELOPPE = ('<svg viewBox="0 0 24 24" fill="currentColor"><path d="M2.5 5h19v14h-19z" fill="none" stroke="currentColor" '
             'stroke-width="2"/><path d="M3 6l9 7 9-7" fill="none" stroke="currentColor" stroke-width="2"/></svg>')
NOTE = ('<svg viewBox="0 0 24 24" fill="currentColor"><path d="M4 3h16v12l-6 6H4z"/><path d="M14 21v-6h6" fill="#fff" '
        'opacity=".55"/></svg>')
OEIL = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1.5 12S5.5 5 12 5s10.5 7 '
        '10.5 7-4 7-10.5 7S1.5 12 1.5 12z"/><circle cx="12" cy="12" r="3.2" fill="currentColor"/></svg>')
TROMBONE = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path '
            'd="M20 11.5l-8.2 8.2a5 5 0 01-7.1-7.1l8.6-8.6a3.4 3.4 0 014.8 4.8l-8.4 8.4a1.7 1.7 0 01-2.4-2.4l7.6-7.6"/></svg>')
ABONNES = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="8" r="4.2"/>'
           '<path d="M4 21c0-4.6 3.6-7.4 8-7.4s8 2.8 8 7.4z"/></svg>')
SILHOUETTE = ('<svg viewBox="0 0 40 40"><rect width="40" height="40" fill="#D9DCE0"/><circle cx="20" cy="15" r="7.5" '
              'fill="#A3A9B1"/><path d="M5 40c0-9 6.6-14 15-14s15 5 15 14z" fill="#A3A9B1"/></svg>')
SPIN = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round">'
        '<path d="M12 3a9 9 0 109 9" /></svg>')


def fcfa(n):
    return '{:,.0f}'.format(n).replace(',', ' ') + ' FCFA'


def svg(code, classe_='t08-svg'):
    return '<span class="%s">%s</span>' % (classe_, code)


def s_carte(ident, titre, texte_, bouton_, contour=False, prix=None):
    """Une carte du site (même gabarit que ``scenarios/c4_site_web.s_carte``)."""
    px = '<div class="px">%s</div>' % e(prix) if prix else ''
    return ('<div class="s-carte" id="%s"><div class="h">%s</div><div class="p">%s</div>%s'
            '<div class="s-bouton%s" id="%s-bt">%s</div></div>'
            % (ident, e(titre), e(texte_), px, ' contour' if contour else '', ident, e(bouton_)))


# ======================================================== le site public ==

NAV = ('<div class="s-nav t08-nav"><span class="s-logo t08-logo">%s</span><span class="s-m">Accueil</span>'
       '<span class="s-m actif">Réservation</span><span class="s-m">Contactez-nous</span>'
       '<span class="t08-loupe">%s</span><span class="s-tel t08-tel">%s%s</span>'
       '<span class="t08-connexion">Se connecter</span><span class="bt primaire s-bt t08-contact">Contactez-nous</span>'
       '</div>' % (e(SITE), icone('loupe'), icone('telephone'), e(TEL_HOTEL)))

# Le texte « À propos de nous » et les liens du pied de page sont du contenu
# que l'hôtel saisit dans l'éditeur du site (le gabarit d'Odoo y met un texte
# d'exemple) : ici, un texte neutre d'établissement, fictif.
A_PROPOS = ("Chambres et suites, salons privés, spa, coiffure et pressing : réservez vos créneaux en ligne, notre "
            "réception confirme vos séjours.")


def pied(haut):
    """Le pied de page d'Odoo 18 (« Liens utiles », « À propos de nous »,
    « Rejoignez-nous »), personnalisé par l'établissement, qui suit le
    contenu et file sous le bord de la fenêtre."""
    liens = ''.join('<div class="t08-pl">%s</div>' % x for x in ('Accueil', 'Réservation', 'Contactez-nous'))
    return ('<div class="t08-pied" style="top:%dpx"><div class="t08-pc"><div class="t08-ph">Liens utiles</div>%s</div>'
            '<div class="t08-pc t08-pc-m"><div class="t08-ph">À propos de nous</div><div class="t08-pt">%s</div></div>'
            '<div class="t08-pc t08-pc-d"><div class="t08-ph">Rejoignez-nous</div><div class="t08-pl">Contactez-nous</div>'
            '<div class="t08-pl">reservation@exemple.cm</div><div class="t08-pl">%s</div></div></div>'
            % (haut, liens, e(A_PROPOS), e(TEL_HOTEL)))


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
    % (s_carte('t08-e1', SALON, 'Ouvert de 09:00 à 23:00', 'Voir les créneaux', True, fcfa(TARIF_SALON) + ' / heure'),
       s_carte('t08-e2', 'Salon VIP Sanaga', 'Ouvert de 09:00 à 23:00', 'Voir les créneaux', True,
               fcfa(TARIF_SALON) + ' / heure'),
       s_carte('t08-e3', 'Salon VVIP Bonabéri', 'Ouvert de 10:00 à 23:00', 'Voir les créneaux', True,
               fcfa(TARIF_VVIP) + ' / heure'))), haut_pied=440)

# Les créneaux libres du salon (pas d'une heure, 09:00 → 23:00), cohérents
# avec le planning de la réception : le mercredi 14/10 à 07:52 (12:00-14:00
# et 16:00-20:00 vendus, aucune heure encore passée), et le samedi 17/10
# (12:00-14:00 et 19:00-21:00 vendus).
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
        '<div class="s-h1 t08-h1">%s</div><div class="s-p t08-prix">%s / heure</div>%s'
        '<div class="s-lab">Date</div><div class="t08-ligne-date"><div class="t08-date">%s<span class="t08-cal">%s'
        '</span></div><span class="t08-voir" id="%s-voir">Voir ce jour</span></div>'
        '<div class="t08-h5">Créneaux disponibles</div><div class="creneaux t08-creneaux" id="%s-creneaux">%s</div>'
        '<div class="t08-h5">Vos coordonnées</div><div class="s-ligne3 t08-coord">%s%s%s</div>'
        '<div class="s-gros-bt t08-gros" id="%s-reserver">Réserver ce créneau</div>'
        '<div class="s-note">Acompte à régler au comptoir — Orange Money, MTN MoMo ou espèces.</div></div>'
        % (e(SALON), fcfa(TARIF_SALON), bandeau, champ_date, CAL, ident, ident, creneaux,
           entree(ident + '-nom', '' if nom else 'Nom complet', nom),
           entree(ident + '-tel', '' if tel else 'Téléphone', tel),
           entree(ident + '-mail', 'E-mail (confirmation)'), ident)))


GRILLE_14 = grille('t08-g14', '14/10/2026', LIBRES_14, saisie_date=True)
GRILLE_17 = grille('t08-g17', '17/10/2026', LIBRES_17)
# Un autre visiteur avait ouvert la même page avant Claire : seize heures y est encore libre.
AUTRE = grille('t08-ga', '17/10/2026', LIBRES_17, coche='16:00', nom=VISITEUR, tel=TEL_VISITEUR)
# Sa validation est refusée : il revient sur la grille, seize heures n'y est plus.
REFUS = grille('t08-gr', '17/10/2026', [h for h in LIBRES_17 if h != '16:00'], alerte=True)

MERCI = vue_site('t08-merci', (
    '<div class="s-merci" id="t08-merci-bloc"><div class="h">Merci !</div>'
    '<div class="p">Votre réservation <b id="t08-merci-ref">%s</b> est <b>confirmée</b>.</div>'
    '<div class="q t08-noir">%s</div><div class="q">Un e-mail de confirmation vous a été envoyé.</div>'
    '<div class="s-alerte" id="t08-acompte">L\'acompte se règle au comptoir à votre arrivée — <b>Orange Money, MTN MoMo '
    'ou espèces</b>.</div><div class="t08-retour-bt"><span class="s-bouton contour">Retour aux réservations</span></div>'
    '</div>' % (REF_CRENEAU, e(SALON))), haut_pied=480)

def avec_calendrier(champ_html):
    """Un champ date du navigateur : l'icône du calendrier à droite."""
    return '<div class="t08-dw">%s<span class="t08-cal">%s</span></div>' % (champ_html, CAL)


SEJOUR = s_vue('t08-sejour', (
    '<div class="s-form t08-form-s"><div class="s-h1 t08-h1">Demande de séjour</div>'
    '<div class="s-p">Notre réception confirme votre chambre et vous rappelle rapidement.</div>'
    '<div class="s-ligne"><div><div class="s-lab">Arrivée</div>%s</div><div><div class="s-lab">Départ</div>%s</div></div>'
    '<div class="s-ligne t08-l12"><div><div class="s-lab">Adultes</div>%s</div>'
    '<div><div class="s-lab">Nom complet</div>%s</div></div>'
    '<div class="s-ligne"><div><div class="s-lab">Téléphone</div>%s</div><div><div class="s-lab">E-mail</div>%s</div></div>'
    '<div class="s-lab">Message (optionnel)</div><div class="t08-zone"></div>'
    '<div class="s-gros-bt t08-gros" id="t08-envoyer">Envoyer la demande</div></div>'
    % (avec_calendrier(entree('t08-s-arr', 'jj/mm/aaaa')), avec_calendrier(entree('t08-s-dep', 'jj/mm/aaaa')),
       entree('t08-s-ad', '', '2'),
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


def bloc(client, de, a, etat='confirmed', ident=None, montant=0):
    return {'client': client, 'de': de, 'a': a, 'etat': etat, 'id': ident, 'montant': montant}


# Couleurs des familles (slot_dashboard.py l. 22-25), reprises comme couleur de chaque ressource.
VIOLET, VERT, BLEU, BRUN = '#714B67', '#0F6E56', '#185FA5', '#854F0B'
# Les huit ressources de l'établissement, celles du tutoriel 9
# (t09_espaces.py l. 192-201, même ordre) : (nom, couleur, ouverture,
# fermeture, pas en minutes, capacité). Les tarifs horaires des salons sont
# TARIF_SALON et TARIF_VVIP.
RESSOURCES = [(SALON, VIOLET, 9, 23, 60, 1), ('Salon VIP Sanaga', VIOLET, 9, 23, 60, 1),
              ('Salon VVIP Bonabéri', VIOLET, 10, 23, 60, 1), ('Cabine SPA 1', VERT, 9, 21, 30, 1),
              ('Cabine SPA 2', VERT, 9, 21, 30, 1), ('Fauteuil homme 1', BLEU, 9, 20, 30, 1),
              ('Fauteuil femme 1', BLEU, 9, 20, 30, 1), ('Comptoir pressing', BRUN, 8, 19, 30, 2)]
# Le mercredi 14/10 (aujourd'hui, en fin de matinée) : cinq prestations du
# matin réalisées, au catalogue et aux prix du tutoriel 9 (massage relaxant
# 60 min 27 000, coupe homme 6 200, tresses forfait 2 h 19 000, deux dépôts
# de chemise au pressing à 4 800), et six réservations confirmées à venir.
JOUR_14 = [[bloc('Cécile Ondoa', 12, 14), bloc('Bertrand Mvondo', 16, 20)],
           [bloc('Thierry Ngando', 18, 22)],
           [bloc('Rachel Ebongue', 14, 17)],
           [bloc('Nadine Ebalé', 10, 11, 'done', montant=27000), bloc('Nadia Belinga', 16, 17.5)],
           [bloc('Hélène Mouelle', 15, 16)],
           [bloc('Didier Abanda', 9.5, 10, 'done', montant=6200)],
           [bloc('Odile Ekwalla', 9, 11, 'done', montant=19000)],
           [bloc('Fabrice Nkolo', 8, 8.5, 'done', montant=4800), bloc('Esther Mvogo', 9, 9.5, 'done', montant=4800)]]
# Le samedi 17/10 : la réservation en ligne de Claire est déjà dans le couloir du salon.
JOUR_17 = [[bloc('Aline Nkengue', 12, 14), bloc(NOM, 16, 17, ident='t08-bk-claire'), bloc('Gilbert Tchoua', 19, 21)],
           [bloc('Josué Mbida', 10, 12), bloc('Joseph Ekani', 18, 20)],
           [bloc('Grâce Nguene', 15, 19)],
           [bloc('Nadège Owona', 11, 12), bloc('Sandrine Kemajou', 15, 16.5)],
           [bloc('Pauline Etame', 10, 11)],
           [bloc('Armel Tsala', 9, 9.5), bloc('Hugo Biyong', 14, 14.5)],
           [bloc('Gisèle Kouam', 9.5, 11.5), bloc('Odile Ekwalla', 14, 15)],
           []]
COULOIRS_14 = ''.join(couloir('t08-c14-%d' % i, *r[:5], blocs=j)
                      for i, (r, j) in enumerate(zip(RESSOURCES, JOUR_14), 1))
COULOIRS_17 = ''.join(couloir('t08-c17-%d' % i, *r[:5], blocs=j)
                      for i, (r, j) in enumerate(zip(RESSOURCES, JOUR_17), 1))


def virgule(x):
    """Une décimale, virgule française, sans « ,0 » (fmtPct / fmtHours, utils.js l. 30-40)."""
    return ('%g' % (int(x * 10 + 0.5) / 10.0)).replace('.', ',')


# Les indicateurs de la période « Aujourd'hui » (slot_dashboard.get_kpis
# l. 123-176), cohérents avec le planning du 14/10 : CA des prestations
# réalisées, heures réservées (confirmées + réalisées) sur les heures ouvrées
# (amplitude × capacité, l. 147-150 : 109 h, comme au tutoriel 9), retraits
# pressing en attente (dépôts confirmés ou réalisés non retirés, toutes
# périodes, l. 155-160 : les deux chemises du matin, encore là le 15/10 au
# tutoriel 9). Ils ne dépendent pas du jour affiché : ils restent les mêmes au 17/10.
FAITES = [b for jour in JOUR_14 for b in jour if b['etat'] == 'done']
CA_FAIT = sum(b['montant'] for b in FAITES)
HEURES = sum(b['a'] - b['de'] for jour in JOUR_14 for b in jour)
OUVERTES = sum((r[3] - r[2]) * r[5] for r in RESSOURCES)
A_VENIR = sum(1 for jour in JOUR_14 for b in jour if b['etat'] == 'confirmed')
REMPLISSAGE = virgule(HEURES / OUVERTES * 100) + ' %'
RETRAITS = len(JOUR_14[7])

TDB = vue_libre('t08-tdb', (
    '<div class="t08-d"><div class="t08-d-top"><div><div class="t08-d-titre">Espaces & Prestations</div>'
    '<div class="t08-d-sous">Planning des créneaux · SPA, coiffure, pressing, espaces VIP / VVIP</div></div>'
    '<span class="t08-d-nouv">+ Nouvelle réservation</span></div>'
    '<div class="t08-d-filtres"><div class="t08-d-rang"><span class="t08-d-lab">Jour</span>%s'
    '<span class="t08-d-date" id="t08-d-date"><span id="t08-jour">14/10/2026</span><span class="t08-cal">%s</span></span>%s%s'
    '<span class="t08-esp"></span><span class="t08-d-lab">Période stats</span>%s%s%s</div>'
    '<div class="t08-d-rang"><span class="t08-d-lab">Famille</span>%s%s%s%s%s%s</div>'
    '<div class="t08-d-rang"><span class="t08-d-lab">Ressource</span>%s%s</div></div>'
    '<div class="t08-corps" id="t08-corps">'
    '<div class="t08-d-sect">Activité de la période</div><div class="t08-d-kpis">%s%s%s%s</div>'
    '<div class="t08-d-sect" id="t08-plan-t">Planning du 2026-10-14</div>'
    '<div class="t08-d-carte"><div class="t08-lanes" id="t08-l14">%s</div>'
    '<div class="t08-lanes t08-dessus masque" id="t08-l17">%s</div></div>'
    '<div class="t08-d-sect">Répartition & remplissage</div><div class="t08-d-deux">'
    '<div class="t08-d-carte t08-d-graphe"><div class="t08-d-h3">CA réalisé par famille (période)</div></div>'
    '<div class="t08-d-carte t08-d-graphe"><div class="t08-d-h3">Remplissage par ressource</div></div></div></div>'
    '<div class="t08-charge masque" id="t08-charge">%sChargement…</div></div>'
    % (chip('‹', ident='t08-prec'), CAL, chip('›', ident='t08-suiv'), chip("Aujourd'hui"),
       chip("Aujourd'hui", True), chip('Cette semaine'), chip('Ce mois'),
       chip('Toutes', True), chip('Espace VIP / VVIP', point=VIOLET), chip('SPA', point=VERT),
       chip('Coiffure', point=BLEU), chip('Pressing', point=BRUN), chip('Autre', point='#888780'),
       chip('Toutes', True), ''.join(chip(r[0], point=r[1]) for r in RESSOURCES),
       kpi_t08('CA prestations réalisées', fcfa(CA_FAIT), '%d réalisée(s)' % len(FAITES), 'a-violet'),
       kpi_t08('Taux de remplissage', REMPLISSAGE,
               '%s h réservées / %s h ouvrées' % (virgule(HEURES), virgule(OUVERTES)), 'a-bleu'),
       kpi_t08('No-show', '0 %', '0 rendez-vous manqué(s)', 'a-rouge'),
       kpi_t08('Retraits pressing en attente', str(RETRAITS), '%d réservation(s) à venir' % A_VENIR, 'a-ambre'),
       COULOIRS_14, COULOIRS_17, svg(SPIN, 't08-spin'))), initiale=True, fond='tdb')


# --------------------------------------------- la fiche, et sa discussion --
def message(texte_html, ident=None):
    """Un message de la discussion, signé par l'utilisateur public du site."""
    return ('<div class="t08-ch-msg"%s><span class="t08-ch-av">%s</span><div><div class="t08-ch-a"><b>Public user</b> '
            '<small>Aujourd\'hui à %s</small></div><div class="t08-ch-t">%s</div></div></div>'
            % (' id="%s"' % ident if ident else '', SILHOUETTE, HEURE_RESA, texte_html))


DISCUSSION = (
    '<div class="chatter t08-chat"><div class="t08-ch-bts"><span class="bt primaire">%sEnvoyer message</span>'
    '<span class="bt gris">%sNote</span><span class="t08-ch-i">%s</span><span class="t08-ch-i">%s</span>'
    '<span class="t08-ch-i">%s</span><span class="t08-ch-i">%s<sup>0</sup></span></div>'
    '<div class="t08-ch-jour"><span>Aujourd\'hui</span></div>%s%s</div>'
    % (svg(ENVELOPPE, 't08-ch-ico'), svg(NOTE, 't08-ch-ico'), icone('loupe', 't08-svg'), svg(OEIL), svg(TROMBONE),
       svg(ABONNES),
       message('<span class="t08-anc">Brouillon</span><span class="t08-sep">→</span><span class="t08-nouv">Confirmée'
               '</span> <i>(État)</i>', 't08-ch-suivi'),
       message('Réservation de créneau (espace / prestation) créé', 't08-ch-cree')))


def avec_discussion(vue_html, panneau):
    """Pose la discussion à droite de la fiche, comme ``ecrans.avec_chatter``
    (qui ajoute un bouton « Activités » : ce modèle n'en a pas)."""
    debut = vue_html.index('>') + 1
    tete = vue_html[:debut].replace('class="vue', 'class="vue avec-chatter', 1)
    return tete + vue_html[debut:-len('</div>')] + panneau + '</div>'


FICHE = avec_discussion(vue_fiche(
    't08-fiche', cp_fiche('Espaces & Prestations — Tableau de bord', REF_CRENEAU).replace(
        '<span class="ref">%s</span>' % REF_CRENEAU,
        '<span class="ref">%s<span class="t08-rouage">%s</span></span>' % (REF_CRENEAU, ROUAGE), 1),
    [bouton('t08-realisee', 'Réalisée', 'primaire'), bouton(None, "Renvoyer l'e-mail", 'gris'),
     bouton(None, 'No-show', 'gris'), bouton(None, 'Annuler', 'gris')],
    statusbar('t08-sb', ['Brouillon', 'Confirmée', 'Réalisée'], 1),
    titre_fiche(REF_CRENEAU)
    + deux_colonnes(champ('Client', NOM) + champ('Téléphone', TEL_FICHE) + champ('Ressource', SALON)
                    + champ('Prestation', '') + champ('Origine', 'En ligne', 't08-f-origine'),
                    champ('Début', '17/10/2026 16:00:00') + champ('Fin', '17/10/2026 17:00:00')
                    + champ('Durée (h)', '01:00') + champ('Montant', fcfa(TARIF_SALON), 't08-f-montant')
                    + champ('Prix manuel', '0 FCFA'))
    + groupe('Séjour (note de chambre)', [champ('Folio du séjour', ''), champ('Ligne de folio', '')])
    + '<div class="t08-note">Note interne…</div>'), DISCUSSION)


# ------------------------------------------------- les réservations hôtel --
# Tarifs des types de chambre (t02_planning.py l. 231-260) et les 20 chambres de la série : 101-107 Standard
# (la 105 hors service, jamais vendue), 201-206 Confort, 301-304 Suite Junior, 401-403 Suite VIP.
PRIX = {'STD': 35000, 'CFT': 45000, 'SJR': 75000, 'VIP': 120000}
TYPE = dict([('%d' % n, 'STD') for n in range(101, 108) if n != 105] + [('%d' % n, 'CFT') for n in range(201, 207)]
            + [('%d' % n, 'SJR') for n in range(301, 305)] + [('%d' % n, 'VIP') for n in range(401, 404)])
assert len(TYPE) == 19                            # 20 chambres, moins la 105 hors service


# (référence, client, arrivée, départ, nuits, chambre — None : pas encore de
# chambre —, état). Ordre de la liste : arrivée décroissante, puis id
# décroissant (hotel_reservation.py l. 27).
TOUTES = [
    ('RES/2026/0220', 'Viviane Eyoum', '04/11/2026 14:00:00', '06/11/2026 12:00:00', 2, '303', 'confirmed'),
    ('RES/2026/0219', 'Mathieu Nkodo', '30/10/2026 14:00:00', '01/11/2026 12:00:00', 2, '104', 'confirmed'),
    ('RES/2026/0215', 'Blaise Atangana', '28/10/2026 14:00:00', '31/10/2026 12:00:00', 3, '205', 'confirmed'),
    (REF_YANNICK, 'Yannick Mbassi', '24/10/2026 14:00:00', '26/10/2026 11:00:00', 2, None, 'draft'),
    ('RES/2026/0218', 'Aristide Bella', '24/10/2026 14:00:00', '26/10/2026 12:00:00', 2, '401', 'confirmed'),
    ('RES/2026/0217', 'Olivier Ndzana', '23/10/2026 14:00:00', '25/10/2026 12:00:00', 2, '106', 'confirmed'),
    ('RES/2026/0212', 'Carine Manga', '22/10/2026 14:00:00', '24/10/2026 12:00:00', 2, '302', 'confirmed'),
    ('RES/2026/0216', 'Christelle Ndongo', '21/10/2026 14:00:00', '23/10/2026 12:00:00', 2, '102', 'confirmed'),
    (REF_SEJOUR, NOM, '20/10/2026 14:00:00', '23/10/2026 11:00:00', 3, None, 'draft'),
    ('RES/2026/0221', 'Rodrigue Tamba', '19/10/2026 14:00:00', '21/10/2026 12:00:00', 2, '203', 'confirmed'),
    ('RES/2026/0211', 'Joël Kamga', '18/10/2026 14:00:00', '20/10/2026 12:00:00', 2, '204', 'confirmed'),
    ('RES/2026/0205', 'Paul Abessolo', '16/10/2026 14:00:00', '18/10/2026 12:00:00', 2, '301', 'confirmed'),
]
# Le brouillon de Jacques Owona, saisi au comptoir (canal « Direct / comptoir ») au tutoriel 2.
JACQUES = ('RES/2026/0222', 'Jacques Owona', '15/10/2026 14:00:00', '17/10/2026 12:00:00', 2, '204', 'draft')
BROUILLONS = [r for r in TOUTES if r[6] == 'draft'] + [JACQUES]
# La liste non filtrée charge 80 lignes : sous les douze premières, la suite
# (Jacques Owona, puis Gaston Mbida, t02_planning.py l. 287) file sous le bord.
SUITE = [JACQUES, ('RES/2026/0213', 'Gaston Mbida', '15/10/2026 14:00:00', '17/10/2026 12:00:00', 2, '103', 'confirmed')]

COLS = '142px 168px 180px 180px 50px 94px 1fr 118px 126px 108px 28px'
TETE = ['Référence', 'Client', 'Arrivée', 'Départ', 'Nuits', 'Nb chambres', 'Total hébergement (HT)', 'Solde folio',
        'Registre', 'État']
DROITE = {4, 5, 6, 7}


def total_resa(r):
    return r[4] * PRIX[TYPE[r[5]]] if r[5] else 0


def solde_folio(r, adultes=2):
    """Le folio ouvert à la confirmation, rien n'étant réglé : nuitées (sans
    TVA, convention de la série) + taxe de séjour 3 ★ (3 000 F par adulte et
    par nuit), comme ``solde_folio`` du tutoriel 2 (t02_planning.py
    l. 302-308 : 102 000 FCFA pour Rodrigue Tamba, deux nuits à 45 000, deux
    adultes) et le folio du tutoriel 5 (t05_taxe_sejour.py l. 166-172) ;
    deux adultes par séjour."""
    return total_resa(r) + 3000 * adultes * r[4]


def ligne_resa(ident, r, masque=False):
    """Une ligne de la liste : texte bleu (decoration-info, foncé pour le
    contraste) si confirmée ; solde = le folio, taxe de séjour comprise,
    tant que rien n'est réglé ; pas de folio (solde 0) pour un brouillon."""
    total = total_resa(r)
    confirmee = r[6] == 'confirmed'
    valeurs = [r[0], r[1], r[2], r[3], str(r[4]), '1' if r[5] else '0', fcfa(total),
               fcfa(solde_folio(r) if confirmee else 0)]
    cs = ['<span class="ell%s">%s</span>' % (' d' if k in DROITE else '', e(v)) for k, v in enumerate(valeurs)]
    cs.append('<span><span class="puce rouge t08-badge">Aucune fiche</span></span>')
    cs.append('<span><span class="puce %s t08-badge"%s>%s</span></span>'
              % ('info' if confirmee else 'orange', ' id="%s-etat"' % ident, 'Confirmée' if confirmee else 'Brouillon'))
    cs.append('<span></span>')
    return ('<div class="ligne t08-ligne%s%s" id="%s" style="grid-template-columns:40px %s"><span class="cb"></span>%s'
            '</div>' % (' t08-conf' if confirmee else '', ' masque' if masque else '', ident, COLS, ''.join(cs)))


def tete_liste():
    return ('<div class="tete" style="grid-template-columns:40px %s"><span class="cb"></span>%s'
            '<span class="t08-optcol">%s</span></div>'
            % (COLS, ''.join('<span class="ell%s">%s</span>' % (' d' if k in DROITE else '', e(t))
                             for k, t in enumerate(TETE)), REGLAGES))


def total_liste(valeur, ident=None, masque=False):
    return ('<div class="total t08-total%s"%s style="grid-template-columns:40px %s">%s<span class="d">%s</span>%s</div>'
            % (' masque' if masque else '', ' id="%s"' % ident if ident else '', COLS, '<span></span>' * 7, e(valeur),
               '<span></span>' * 4))


def groupe_resa(ident, libelle, nuits, chambres, total):
    """Un groupe replié : libellé « Canal (nombre) », sommes des colonnes
    stockées ; la somme monétaire est formatée sans devise, à deux décimales."""
    return ('<div class="ligne t08-grp" id="%s" style="grid-template-columns:40px %s"><span></span>'
            '<span class="t08-grp-l"><b id="%s-fl">▸</b> %s</span><span class="d">%s</span><span class="d">%s</span>'
            '<span class="d">%s</span>%s</div>'
            % (ident, COLS, ident, e(libelle), nuits, chambres, total, '<span></span>' * 4))


def rid(r):
    return 't08-r-' + r[0][-4:]


def deux(n):
    return '{:,.0f}'.format(n).replace(',', ' ') + ',00'


def recherche_t08(ident, facettes, masque=False):
    """La barre de recherche et ses facettes : (libellé, icône svg)."""
    f = ''.join('<span class="facette">%s<span class="ell">%s</span><span class="fx">×</span></span>'
                % ('<span class="fic">%s</span>' % ic, e(lib)) for lib, ic in facettes)
    return ('<div class="recherche t08-rech%s" id="%s">%s%s<span class="ph">%s</span><span class="deroule">▾</span></div>'
            % (' masque' if masque else '', ident, icone('loupe', 'loupe'), f, '' if facettes else 'Rechercher…'))


FILTRE = ICONES['filtre']
LISTE_A = ('<div class="liste t08-liste" id="t08-la">%s%s</div>'
           % (tete_liste(), ''.join(ligne_resa(rid(r) + 'a', r) for r in TOUTES + SUITE)))
LISTE_B = ('<div class="liste t08-liste masque" id="t08-lb">%s%s%s</div>'
           % (tete_liste(), ''.join(ligne_resa(rid(r) + 'b', r) for r in BROUILLONS),
              total_liste(fcfa(sum(total_resa(r) for r in BROUILLONS)))))
WEB = [r for r in BROUILLONS if r[0] in (REF_YANNICK, REF_SEJOUR)]
LISTE_C = ('<div class="liste t08-liste masque" id="t08-lc">%s%s%s%s%s%s</div>'
           % (tete_liste(),
              groupe_resa('t08-g-dir', 'Direct / comptoir (1)', JACQUES[4], 1, deux(total_resa(JACQUES))),
              groupe_resa('t08-g-web', 'Site web (%d)' % len(WEB), sum(r[4] for r in WEB), 0, deux(0)),
              ''.join(ligne_resa(rid(r), r, masque=True) for r in WEB),
              total_liste(deux(total_resa(JACQUES)), 't08-tot-c2', masque=True),
              # tant que le groupe est replié, la somme suit directement les groupes (hors du flux :
              # les lignes masquées, qui gardent leur place, passent dessous)
              total_liste(deux(total_resa(JACQUES)), 't08-tot-c1').replace('class="total t08-total"',
                                                                         'class="total t08-total t08-tot-c1"', 1)))


def item(libelle, ident=None, classe_=''):
    return '<div class="%s"%s>%s</div>' % (('t08-mi ' + classe_).strip(), ' id="%s"' % ident if ident else '', e(libelle))


MENU_RECH = (
    '<div class="t08-menu masque" id="t08-menu">'
    '<div class="t08-mcol"><div class="t08-mt">%sFiltres</div>%s%s%s<hr>%s%s%s<hr>%s</div>'
    '<div class="t08-mcol"><div class="t08-mt">%sRegrouper par</div>%s%s%s%s%s<hr>%s</div>'
    '<div class="t08-mcol"><div class="t08-mt">%sFavoris</div>%s</div></div>'
    % (svg(FILTRE, 't08-mic t08-mic-f'), item('Arrivées du jour'), item('Départs du jour'), item('Clients présents'),
       item('Brouillons', 't08-mf-brouillons'), item('Confirmées'), item('No-show'), item('Ajouter un filtre personnalisé'),
       svg(COUCHES_N, 't08-mic'), item('État'), item('Client'), item('Hôtel'), item('Canal', 't08-mg-canal'),
       item("Date d'arrivée", classe_='t08-acc'), item('Ajouter un groupe personnalisé', classe_='t08-acc'),
       svg(ETOILE, 't08-mic'), item('Enregistrer la recherche actuelle', classe_='t08-acc')))

RESAS = vue_libre('t08-resas', (
    '<div class="cp t08-cp"><span class="bt primaire">Nouveau</span><span class="titre t08-titre">Réservations'
    '<span class="t08-rouage">%s</span></span>%s%s%s'
    '<span class="t08-pager"><span id="t08-pager">1-80 / 224</span><span class="t08-fl">‹</span>'
    '<span class="t08-fl">›</span></span><span class="t08-vues"><span class="actif">%s</span><span>%s</span>'
    '<span>%s</span></span></div><div class="t08-pile">%s%s%s</div>%s'
    % (ROUAGE, recherche_t08('t08-rech-a', []),
       recherche_t08('t08-rech-b', [('Brouillons', FILTRE)], masque=True),
       recherche_t08('t08-rech-c', [('Brouillons', FILTRE), ('Canal', COUCHES)], masque=True),
       V_LISTE, V_KANBAN, V_CAL, LISTE_A, LISTE_B, LISTE_C, MENU_RECH)))

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


def perso_css(cle, nom, role):
    """La pastille du personnage change avec l'acteur de l'étape : la classe
    ``cle`` posée sur ``#tu-perso`` remplace le nom, le rôle et l'initiale."""
    return ("#tu-perso.%(c)s > span:last-child, #tu-perso.%(c)s .av { font-size: 0; }\n"
            "#tu-perso.%(c)s .av::after { content: '%(i)s'; font-size: 20px; }\n"
            "#tu-perso.%(c)s > span:last-child::before { content: '%(n)s'; font-size: 21px; font-weight: 700; }\n"
            "#tu-perso.%(c)s > span:last-child::after { content: ' · %(r)s'; font-size: 21px; white-space: pre; }\n"
            % {'c': cle, 'i': nom[0], 'n': nom, 'r': role})


def acteur(cle=None):
    """Les gestes qui passent la pastille au visiteur (``t08-pa``), à la
    réceptionniste (``t08-pm``) ou, sans clé, à Claire."""
    autres = [c for c in ('t08-pa', 't08-pm') if c != cle]
    return [classe('#tu-perso', ajouter=[cle] if cle else [], retirer=autres),
            animer('#tu-perso', {'scale': 0.88}, {'scale': 1}, d=0.35, avec=True)]


CSS = perso_css('t08-pa', VISITEUR, ROLE_VISITEUR) + perso_css('t08-pm', RECEPTION, ROLE_RECEPTION) + """
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
.t08-dw { position: relative; }
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
.t08-pc { width: 240px; flex: none; }
.t08-pc-m { width: 560px; margin-left: 40px; }
.t08-pc-d { margin-left: auto; width: 420px; }
.t08-ph { font-size: 25px; font-weight: 500; color: #F8F9FA; margin-bottom: 18px; }
.t08-pl { font-size: 20px; line-height: 1.6; color: #9DB8CA; }
.t08-pt { font-size: 19px; line-height: 1.55; color: #CED4DA; margin-bottom: 14px; }
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
.t08-d-rang { display: flex; align-items: center; gap: 6px; height: 40px; }
.t08-d-rang + .t08-d-rang { margin-top: 4px; padding-top: 4px; height: 44px; border-top: 1px dashed rgba(0,0,0,.12); }
.t08-d-lab { min-width: 100px; font-size: 14px; font-weight: 600; letter-spacing: .05em; text-transform: uppercase;
  color: #6E6D68; }
.t08-chip { height: 36px; padding: 0 9px; border: 1px solid rgba(0,0,0,.12); border-radius: 8px; display: inline-flex;
  align-items: center; gap: 7px; font-size: 15px; color: #4F4E4A; background: #fff; white-space: nowrap; }
.t08-chip.actif { background: #714B67; border-color: #714B67; color: #fff; }
#t08-prec, #t08-suiv { width: 40px; justify-content: center; padding: 0; font-size: 20px; background: #F5F5F4; }
.t08-point { width: 11px; height: 11px; border-radius: 50%; display: inline-block; flex: none; }
.t08-d-date { position: relative; height: 40px; width: 180px; border: 1px solid rgba(0,0,0,.12); border-radius: 8px;
  display: inline-flex; align-items: center; padding-left: 12px; font-size: 16px; color: #2B2A28; background: #fff; }
.t08-d-date.focus { border-color: #4A7892; box-shadow: 0 0 0 3px rgba(74,120,146,.25); }
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
.t08-d-carte { position: relative; background: #fff; border: 1px solid rgba(0,0,0,.08); border-radius: 12px; padding: 8px 16px; }
.t08-dessus { top: 8px; }
.t08-d-deux { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.t08-d-graphe { height: 220px; }
.t08-d-h3 { font-size: 17px; font-weight: 600; color: #2B2A28; }
#r-merci { bottom: 236px; }
.t08-lanes { display: flex; flex-direction: column; gap: 4px; }
.t08-dessus { position: absolute; left: 16px; right: 16px; top: 10px; background: #fff; }
.t08-lane { display: flex; align-items: center; gap: 12px; }
.t08-lane-nom { width: 190px; flex: none; display: flex; align-items: center; gap: 9px; font-size: 16px; font-weight: 600;
  color: #46414E; white-space: nowrap; }
.t08-piste { position: relative; flex: 1; height: 31px; background: #F6F4F3; border: 1px solid #E7E2DF; border-radius: 6px;
  overflow: hidden; }
.t08-rep { position: absolute; top: 0; bottom: 0; border-left: 1px dashed #E1DBD7; }
.t08-bk { position: absolute; top: 4px; bottom: 4px; border-radius: 4px; background: #185FA5; color: #fff; font-size: 13px;
  line-height: 23px; padding: 0 6px; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; }
.t08-bk.fait { background: #0F6E56; }
.t08-libre { width: 175px; flex: none; text-align: right; font-size: 15px; color: #0F6E56; white-space: nowrap; }
.t08-charge { position: absolute; left: 18px; right: 18px; top: 236px; padding: 40px; text-align: center; font-size: 18px;
  color: #6E6D68; display: flex; align-items: center; justify-content: center; gap: 10px; }
.t08-spin { width: 20px; height: 20px; display: inline-flex; }
.t08-spin svg { width: 100%; height: 100%; }

.t08-rouage { width: 18px; height: 18px; display: inline-flex; margin-left: 10px; vertical-align: -2px; }
.t08-rouage svg { width: 100%; height: 100%; }
.t08-svg { width: 20px; height: 20px; display: inline-flex; }
.t08-svg svg { width: 100%; height: 100%; }
.t08-note { margin-top: 18px; padding-bottom: 12px; border-bottom: 1px solid var(--o-filet); font-size: 19px; color: #6C757D; }
#t08-fiche .st-et { color: #545B62; }
#t08-fiche .st-et.actif { color: #212529; }
#t08-fiche .grp { margin-top: 18px; }
#t08-fiche .ch { grid-template-columns: 190px 1fr; }
#t08-fiche .bb-groupe .bt { padding: 0 14px; }
.t08-chat { background: #F8F9FA; padding: 14px 16px; }
.t08-ch-bts { display: flex; align-items: center; gap: 6px; }
.t08-ch-bts .bt { height: 40px; font-size: 17px; padding: 0 11px; display: inline-flex; align-items: center; gap: 7px; }
.t08-ch-ico { width: 17px; height: 17px; display: inline-flex; }
.t08-ch-ico svg { width: 100%; height: 100%; }
.t08-ch-i { width: 32px; height: 40px; display: inline-flex; align-items: center; justify-content: center; color: #495057;
  position: relative; }
.t08-ch-bts .bt + .t08-ch-i { margin-left: auto; }
.t08-ch-i .t08-svg, .t08-ch-i svg { width: 19px; height: 19px; }
.t08-ch-i sup { position: absolute; right: 0; top: 6px; font-size: 12px; color: #495057; }
.t08-ch-jour { position: relative; margin: 22px 0 6px; text-align: center; font-size: 15px; color: #495057; }
.t08-ch-jour::before { content: ''; position: absolute; left: 0; right: 0; top: 50%; border-top: 1px solid #DEE2E6; }
.t08-ch-jour span { position: relative; padding: 0 12px; background: #F8F9FA; }
.t08-ch-msg { display: flex; gap: 12px; margin-top: 14px; font-size: 17px; color: #495057; }
.t08-ch-av { width: 40px; height: 40px; border-radius: 6px; overflow: hidden; flex: none; display: inline-flex; }
.t08-ch-av svg { width: 100%; height: 100%; }
.t08-ch-a b { color: #212529; }
.t08-ch-a small { margin-left: 4px; font-size: 13px; color: #495057; }
.t08-ch-t { margin-top: 4px; line-height: 1.4; }
.t08-anc { font-weight: 700; color: #495057; padding: 0 4px; }
.t08-sep { margin: 0 6px; color: #495057; }
.t08-nouv { font-weight: 700; color: #0E7490; }
.t08-ch-t i { color: #495057; }

.t08-cp { position: relative; display: block; }
.t08-cp > .bt { position: absolute; left: 22px; top: 17px; height: 46px; }
.t08-titre { position: absolute; left: 156px; top: 22px; display: inline-flex; align-items: center; }
.t08-rech { position: absolute; left: 520px; top: 15px; width: 600px; margin-left: 0; }
.t08-rech .facette { height: 34px; font-size: 18px; }
.t08-rech .facette .fic svg { width: 100%; height: 100%; }
.t08-pager { position: absolute; right: 196px; top: 17px; height: 46px; display: flex; align-items: center; gap: 0;
  font-size: 19px; color: #495057; }
.t08-pager > span:first-child { margin-right: 14px; }
.t08-fl { width: 40px; height: 42px; display: inline-flex; align-items: center; justify-content: center; background: #E9ECEF;
  color: #343A40; font-size: 24px; }
.t08-fl + .t08-fl { border-left: 1px solid #fff; }
.t08-vues { position: absolute; right: 22px; top: 18px; display: flex; }
.t08-vues span { width: 50px; height: 42px; display: inline-flex; align-items: center; justify-content: center;
  background: #E9ECEF; color: #343A40; }
.t08-vues span + span { border-left: 1px solid #fff; }
.t08-vues span.actif { background: #CFDCE5; box-shadow: inset 0 0 0 1px #4A7892; }
.t08-vues svg { width: 22px; height: 22px; }
.t08-pile { position: absolute; left: 0; right: 0; top: 80px; bottom: 0; }
.t08-liste { position: absolute; left: 0; right: 0; top: 0; }
.t08-liste .ligne, .t08-liste .tete, .t08-liste .total { column-gap: 10px; padding-right: 14px; }
.t08-liste .tete { font-size: 16px; height: 50px; }
.liste .ligne.t08-ligne { height: 47px; font-size: 16px; color: #495057; }
.liste .ligne.t08-ligne.t08-conf { color: #0E7490; }
.t08-optcol { display: inline-flex; width: 20px; height: 20px; color: #495057; }
.t08-optcol svg { width: 100%; height: 100%; }
.liste .ligne.t08-grp { height: 50px; background: #F1F3F5; font-weight: 500; font-size: 17px; }
.t08-tot-c1 { position: absolute; left: 0; right: 0; top: 150px; }
.t08-grp-l { grid-column: 2 / span 4; white-space: nowrap; }
.t08-grp-l b { display: inline-block; width: 18px; font-weight: 400; }
.t08-badge { height: 26px; font-size: 14px; padding: 0 10px; }
.t08-badge.orange { background: #F3B21B; color: #2B2100; }
.liste .total.t08-total { height: 50px; color: #212529; font-size: 16px; }
.t08-menu { position: absolute; right: 424px; top: 72px; padding: 18px 0; display: flex; z-index: 30;
  background: #fff; border: 1px solid #DEE2E6; border-radius: 6px; box-shadow: 0 10px 28px rgba(0,0,0,.18);
  font-size: 18px; color: #212529; }
.t08-mcol { flex: none; padding: 0 22px; border-right: 1px solid #DEE2E6; }
.t08-mcol:last-child { border-right: 0; }
.t08-mt { display: flex; align-items: center; gap: 10px; height: 36px; padding-left: 8px; font-size: 20px; font-weight: 500; }
.t08-mic { width: 18px; height: 18px; display: inline-flex; color: #4A7892; }
.t08-mic svg { width: 100%; height: 100%; }
.t08-mic-f svg path { fill: #4A7892; }
.t08-mi { position: relative; height: 36px; display: flex; align-items: center; padding-left: 32px; white-space: nowrap; }
.t08-mi.coche { font-weight: 600; }
.t08-mi.coche::before { content: '✓'; position: absolute; left: 10px; color: #4A7892; font-weight: 700; }
.t08-mi.t08-acc::after { content: '▾'; margin-left: 8px; color: #495057; font-size: 15px; }
.t08-mcol hr { border: 0; border-top: 1px solid #DEE2E6; margin: 6px 0 6px 8px; }
"""

TUTORIEL = {
    'slug': 't08-site-web',
    'profil': 't08_site_web',
    'numero': 8,
    'titre': 'Réservation en ligne : vos clients réservent seuls, sur les créneaux encore libres',
    'fonction': 'Réservation en ligne',
    'personnage': (NOM, ROLE),
    'accroche': {
        'kicker': 'La réservation en ligne',
        'question': 'Votre site sait-il ce qui est *déjà* *vendu* ?',
        'douleurs': [('echange', 'Le même salon vendu deux fois'),
                     ('cahier', 'Chaque réservation ressaisie à la main'),
                     ('globe', 'Les 10 PMS leaders\u00a0: réservation directe'),
                     ('pieces', 'SaaS étrangers\u00a0: 280\u00a0à\u00a0480\u00a0KFCFA par\u00a0mois'),
                     ('cadenas', 'Odoo Community\u00a0: réservation «\u00a0à\u00a0développer\u00a0»')],
        'voix': "Votre site sait-il ce qui est déjà vendu ? Un salon vendu deux fois, des réservations ressaisies "
                "à la main, des abonnements étrangers coûteux.",
    },
    'revelation': {
        'promesse': "Salons réservés en ligne, confirmés et déjà au planning ; les séjours arrivent en demande.",
        'voix': "Avec Aïte haousse, vos clients réservent seuls leurs salons, confirmés tout de suite. Les séjours, "
                "eux, arrivent en demande à la réception.",
    },
    'temps': ['Choisir', 'Réserver', 'Retrouver'],
    'app': 't08-site',
    'ecran': ECRAN,
    'css': CSS,
    'vues_initiales': {'site': 't08-accueil', 'odoo': 't08-tdb'},
    'bulles': {
        'b-public': 'Pages publiques : ni compte à créer, ni mot de passe.',
        'b-grille': "La même grille qu'à la réception.",
        'b-refus': 'Créneau confirmé entre-temps : la validation tardive est refusée.',
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
         'texte': 'Une date, et la grille ne propose que les créneaux libres ce jour-là.',
         'voix': "Claire choisit samedi : la grille ne montre que les heures encore libres. Ce qui est déjà confirmé, "
                 "au comptoir ou en ligne, n'y figure plus. Elle coche seize heures, pour une heure.",
         'gestes': [clic('#t08-g14-date', fx=0.3), saisir('t08-g14-date', '17/10/2026'), clic('#t08-g14-voir'),
                    vue('t08-g17', 'site'), pause(0.2), zoom('#t08-g17-creneaux', s=1.55, d=0.7),
                    bulle('b-grille', '#t08-g17-h22', cote='droite', d=2.4), pause(1.6), clic('#t08-g17-h16'),
                    classe('#t08-g17-h16', ajouter=['coche']), pause(0.7), dezoom(d=0.6)]},
        {'temps': 1, 'titre': 'Réservé, confirmé sur-le-champ',
         'texte': "Nom, téléphone, e-mail : la référence s'affiche, l'acompte se règle au comptoir.",
         'voix': "Nom, téléphone, courriel, puis Réserver ce créneau : c'est confirmé sur-le-champ, et la référence "
                 "s'affiche aussitôt. L'acompte se règle au comptoir : Orange Moni, MTN MoMo ou espèces.",
         'gestes': [clic('#t08-g17-nom', fx=0.2, d=0.35, puis=0.05), saisir('t08-g17-nom', NOM, d=0.5, puis=0.1),
                    clic('#t08-g17-tel', fx=0.2, d=0.3, puis=0.05), saisir('t08-g17-tel', TEL_CLAIRE, d=0.6, puis=0.1),
                    clic('#t08-g17-mail', fx=0.2, d=0.3, puis=0.05), saisir('t08-g17-mail', MAIL_CLAIRE, d=0.75,
                                                                           puis=0.1),
                    clic('#t08-g17-reserver', d=0.5, puis=0.1), vue('t08-merci', 'site', puis=0.1),
                    curseur('#t08-acompte', fx=0.9, fy=-0.3, d=0.35, avec=True),
                    zoom('#t08-merci-bloc', s=1.4, d=0.6), anneau('#t08-merci-ref', d=1.2),
                    reaction('r-merci', d=2.2), curseur('#t08-acompte', fx=0.97, fy=0.85, d=0.3),
                    anneau('#t08-acompte', d=1.4), dezoom(d=0.5)]},
        {'temps': 1, 'titre': 'Une validation tardive est refusée',
         'texte': "Un second visiteur valide le même créneau : refusé, le site lui demande d'en choisir un autre.",
         'voix': "Un autre visiteur, resté sur la page, valide seize heures à son tour : trop tard. Le site refuse la "
                 "seconde réservation, lui demande un autre créneau, et seize heures a disparu de la grille.",
         'gestes': acteur('t08-pa') + [
             vue('t08-ga', 'site', avec=True), pause(0.4), anneau('#t08-ga-h16', d=1.0), clic('#t08-ga-reserver'),
             vue('t08-gr', 'site'), pause(0.3), zoom('#t08-gr-alerte', s=1.5, d=0.7),
             bulle('b-refus', '#t08-gr-alerte', cote='bas', d=2.6), pause(2.3), dezoom(d=0.6),
             anneau('#t08-gr-creneaux', d=1.4)]},
        {'temps': 1, 'titre': 'Demander un séjour',
         'texte': 'Dates, adultes, coordonnées : la demande arrive en brouillon dans les réservations, avec sa '
                  'référence.',
         'voix': "Pour une chambre, Claire envoie une demande de séjour : ses dates, le nombre d'adultes, ses "
                 "coordonnées. Sa référence s'affiche aussitôt, et la réception la rappellera.",
         'gestes': acteur() + [
             vue('t08-accueil', 'site', avec=True), clic('#t08-ch-bt', d=0.45, puis=0.1),
             vue('t08-sejour', 'site', puis=0.1),
             clic('#t08-s-arr', fx=0.2, d=0.4, puis=0.05), saisir('t08-s-arr', '20/10/2026', d=0.4, puis=0.05),
             clic('#t08-s-dep', fx=0.2, d=0.3, puis=0.05), saisir('t08-s-dep', '23/10/2026', d=0.4, puis=0.05),
             clic('#t08-s-nom', fx=0.2, d=0.35, puis=0.05), saisir('t08-s-nom', NOM, d=0.5, puis=0.05),
             # le téléphone et l'e-mail se remplissent au clavier (touche Tab) : le curseur ne bouge pas
             saisir('t08-s-tel', TEL_CLAIRE, d=0.55, puis=0.05), saisir('t08-s-mail', MAIL_CLAIRE, d=0.6, puis=0.05),
             clic('#t08-envoyer', d=0.45, puis=0.1), vue('t08-merci2', 'site', puis=0.1),
             curseur('#t08-merci2 .t08-retour-bt .s-bouton', fx=1.25, fy=0.5, d=0.35, avec=True), anneau('#t08-merci2-ref', d=1.3)]},
        {'temps': 2, 'titre': 'Déjà au planning de la réception',
         'texte': 'Confirmée, origine « En ligne », montant calculé : rien à ressaisir.',
         'voix': "À la réception, Mireille ouvre le tableau de bord Espaces et Prestations, puis passe à samedi : la "
                 "réservation de Claire occupe déjà le salon. Confirmée, origine en ligne, quinze mille francs "
                 "calculés tout seuls : rien à ressaisir.",
         'gestes': acteur('t08-pm') + [
             montrer('#t08-nav-bo', d=0.45, y=0, avec=True), pause(0.4),
             clic('#t08-jour', fx=0.12, d=0.6, avec=True), classe('#t08-d-date', ajouter=['focus']), pause(0.15),
             texte('#t08-jour', '17/10/2026'), pause(0.1),
             cacher('#t08-corps', d=0.1), montrer('#t08-charge', d=0.1, y=0, avec=True), pause(0.4),
             texte('#t08-plan-t', 'Planning du 2026-10-17'), montrer('#t08-l17', d=0.05, y=0),
             cacher('#t08-charge', d=0.1), animer('#t08-corps', {'autoAlpha': 0}, {'autoAlpha': 1}, d=0.25, avec=True),
             classe('#t08-d-date', retirer=['focus']), pause(0.3),
             anneau('#t08-c17-1', d=1.4), curseur('#t08-bk-claire', fx=1.35, d=0.6, avec=True),
             anneau('#t08-bk-claire', d=1.2), clic('#t08-bk-claire'),
             vue('t08-fiche', 'odoo'), curseur('#t08-sb-1', fx=0.5, fy=0.75, d=0.5), pause(0.1),
             anneau('#t08-f-origine', d=1.1), bulle('b-origine', '#t08-ch-cree', cote='bas', d=2.4), pause(1.4),
             anneau('#t08-f-montant', d=1.5), pause(0.3)]},
        {'temps': 2, 'titre': 'La demande de séjour, en brouillon',
         'texte': "Brouillons regroupés par canal : la chambre ne sera bloquée qu'à la confirmation.",
         'voix': "Côté chambres, Mireille ouvre la liste des réservations, puis filtre les brouillons et les regroupe "
                 "par canal : la demande de Claire attend là, venue du site, encore sans chambre.",
         'gestes': [clic('#t08-m-res', d=0.4, puis=0.05), montrer('#t08-dd-res', d=0.15, y=0, puis=0.05),
                    clic('#t08-dd-res-1', d=0.3, puis=0.05), cacher('#t08-dd-res', d=0.15),
                    classe('#t08-m-ep', retirer=['actif'], avec=True), classe('#t08-m-res', ajouter=['actif'], avec=True),
                    vue('t08-resas', 'odoo', avec=True),
                    clic('#t08-rech-a .deroule', d=0.4, puis=0.05), montrer('#t08-menu', d=0.2, y=-6, puis=0.05),
                    clic('#t08-mf-brouillons', d=0.35, puis=0.05),
                    classe('#t08-mf-brouillons', ajouter=['coche'], puis=0.05),
                    cacher('#t08-rech-a', d=0.1, avec=True), montrer('#t08-rech-b', d=0.15, y=0, avec=True),
                    cacher('#t08-la', d=0.15, avec=True), montrer('#t08-lb', d=0.2, y=0, avec=True),
                    texte('#t08-pager', '1-3 / 3', avec=True), pause(0.25),
                    clic('#t08-mg-canal', fx=0.85, d=0.35, puis=0.05), classe('#t08-mg-canal', ajouter=['coche'], puis=0.05),
                    cacher('#t08-rech-b', d=0.1, avec=True), montrer('#t08-rech-c', d=0.15, y=0, avec=True),
                    cacher('#t08-lb', d=0.15, avec=True), montrer('#t08-lc', d=0.2, y=0, avec=True),
                    texte('#t08-pager', '1-2 / 2', avec=True), pause(0.25),
                    # un clic hors du menu (sur le groupe) le referme
                    clic('#t08-g-web', fx=0.12, d=0.45, puis=0.05), cacher('#t08-menu', d=0.15, avec=True),
                    texte('#t08-g-web-fl', '▾', avec=True), cacher('#t08-tot-c1', d=0.1, avec=True),
                    montrer('#t08-r-0223', d=0.25, y=0, avec=True), montrer('#t08-r-0224', d=0.25, y=0, avec=True),
                    montrer('#t08-tot-c2', d=0.25, y=0, avec=True), curseur('#t08-r-0224-etat', fx=1.35, d=0.35),
                    zoom('#t08-r-0224', s=1.12, d=0.6), anneau('#t08-r-0224-etat', d=1.1),
                    bulle('b-brouillon', '#t08-r-0224', cote='bas', d=2.3), pause(1.2)]},
    ],
    'resultats': {
        'titre': 'Réservé en ligne, retrouvé à la réception',
        'cartes': [
            {'valeur': '3', 'compter': 3, 'unite': 'parcours', 'icone': 'globe',
             'texte': 'publics sur une même page : salons, spa et coiffure, chambres — sans compte'},
            {'valeur': '1', 'compter': 1, 'unite': 'grille', 'icone': 'horloge',
             'texte': 'de disponibilités pour le site et la réception : une seule source'},
            {'valeur': '45', 'compter': 45, 'unite': 'tests', 'icone': 'bouclier',
             'texte': "automatisés du tunnel public, dont le refus d'un créneau déjà pris"},
        ],
        'voix': "Trois parcours publics, une seule grille pour le site et la réception, et quarante-cinq tests "
                "automatisés, dont le refus d'un créneau déjà pris.",
    },
    'cta': {
        'appel': 'Demandez votre démonstration',
        'suivant': 'Espaces et prestations',
        'voix': "Aïte haousse, par Aïte Consulting. Demandez votre démonstration, et retrouvez tous nos tutoriels sur "
                "notre chaîne.",
    },
    'vignette': {'etape': 6, 'apres': 6.4},
}
