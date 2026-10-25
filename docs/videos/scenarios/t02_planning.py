# -*- coding: utf-8 -*-
"""Tutoriel 2 — Planning des chambres : tout l'hôtel d'un coup d'œil, une chambre prise refusée à la confirmation.

Personnage : la réceptionniste (demo.POSTES['reception']), profil Réception
(aite_hotel_management.group_hotel_user) : c'est elle qui consulte le
planning, cherche les disponibilités, réserve, prolonge et change un client
de chambre (security/ir.model.access.csv ; menus réservés à ce groupe,
views/hotel_menus.xml:21-66). Applications de la barre MuK :
ecrans.APPS_PROFIL['reception'] ; menus de l'application Hôtel :
ecrans.MENUS_MUK['hotel_reception'] (Réception — anciennement « Front
Desk », écart n° 42 corrigé dans la livraison 4 —, Réservations, Espaces &
Prestations, Notes de chambre en attente, Facturation, Fidélité,
Gouvernante) ; sous-menus : hotel_menus.xml:21-66 (« Tableau de bord »,
« Réservation rapide », « Arrivées du jour », « Départs du jour », « Clients
présents » ; « Réservations », « Planning des chambres »).

Accroche (douleurs, toutes sourcées) :
- « La même chambre vendue deux fois » — recette/cas_de_test.py:48-53 (A03,
  priorité 1 : « Empêcher la double réservation d'une même chambre ») ;
- « Qui dort dans quelle chambre jeudi ? » — docs/etude_comparative/
  benchmark_pms.md:107 et :267 (le planning visuel, premier des quinze
  points du « socle minimum » attendu par le marché ; seul le besoin d'une
  vue d'ensemble est repris, pas le glisser-déposer, absent d'AITE HOUSE) ;
- « Les nuits et le total comptés à la main » — recette A02
  (cas_de_test.py:41-47 : « le nombre de nuits et le montant total sont
  calculés automatiquement ») ;
- « Changement de chambre : la note ne suit pas » — recette A13
  (cas_de_test.py:107-112 : « Le folio suit le client sans perte de
  lignes ») ;
- « Le Gantt d'Odoo, réservé à Enterprise » — docs/RAPPORT_TESTS.md:44-68
  (web_gantt « réservé à Odoo Enterprise ») ; addons/aite_hotel_gantt/
  __manifest__.py:9-24 ; CLAUDE.md (« la vue Gantt (web_gantt,
  Enterprise) »).

Promesse et révélation : le planning (action « Planning des chambres »,
views/hotel_reservation_views.xml:334-359 et :410-420 : calendrier, une
barre par ligne de séjour, couleur par chambre, états Confirmée / Arrivé /
Parti seulement) ; la Réservation rapide (wizard/hotel_booking_wizard.py:
87-159) ; le refus à la confirmation (models/hotel_reservation.py:323-360,
:374-390) et la contrainte de chevauchement (hotel_reservation.py:744-768).
Deux protections de plus, livrées avec aite_hotel_management 18.0.1.0.6 :
un séjour « Arrivé » dont le départ est dépassé bloque sa chambre jusqu'au
check-out (_overlap_domain, hotel_reservation.py:684-702 ; message « La
chambre %(room)s est toujours occupée par %(ref)s (%(guest)s), dont le
départ était prévu le %(cout)s : faites d'abord son check-out, ou
prolongez son séjour. », :341-351), et les chambres sont verrouillées à la
confirmation (_lock_for_booking, hotel_room.py:502). Ni l'une ni l'autre
ne se voit dans ce tutoriel : la promesse, la voix de la révélation et le
titre restent sur ce qu'il montre, une chambre déjà réservée sur ces dates
refusée à la confirmation.

Écrans et libellés (relevés mot pour mot) :
1. Réservations (vue de départ) — views/hotel_reservation_views.xml:5-34
   (colonnes « Référence », « Client », « Arrivée », « Départ », « Nuits »,
   « Nb chambres », « Total hébergement (HT) », « État », somme du total ;
   décorations info / success / muted) ; filtre « Confirmées » (:255-256) ;
   « Solde folio » (:22), « Canal » (:25, badge, affiché par défaut depuis
   la livraison 4, écart n° 58) et « Registre » (aite_guest_registry/views/
   hotel_reservation_views.xml:62-79) sont des colonnes optionnelles,
   masquées ici par le sélecteur de colonnes (⇋) : la liste ne sert que de
   point de départ, une seconde à l'écran ; libellés des champs :
   models/hotel_reservation.py:29-145. Mise en page : ref_muk/027 (liste).
2. Planning des chambres — views/hotel_reservation_views.xml:334-359 et
   :410-420 (calendar string « Planning des chambres », date_start /
   date_stop, color="room_id", mode="month", hide_date="1", champs
   « Arrivée » et « Départ » sans les secondes (options show_seconds), filtre
   « Chambre » (filters="1"), « Client », « Réservation », « État ») ;
   libellé d'une barre « <chambre> · <client> » (hotel_reservation.py:
   715-719), chambre « 204 [CFT] » (models/hotel_room.py:374-380) ; domaine
   confirmed / checked_in / checked_out (:414). Cadre du calendrier d'Odoo 18
   (odoo18/addons/web/i18n/fr.po : « Aujourd'hui », « Mois », « Rechercher… »,
   « Modifier », « en plus ») ; empilement des barres : eventLimit = 5
   (calendar_arch_parser.js:26) passé en dayMaxEventRows
   (calendar_common_renderer.js:87) : jusqu'à cinq rangées par case, au-delà
   quatre et « +N en plus » (lib/fullcalendar/daygrid/index.global.js:284-292,
   core/index.global.js:4851-4855) ; ici aucune case ne dépasse cinq rangées
   (contrôlé par disposer), donc toutes les barres sont visibles, plus basses
   que dans ref_muk/028 pour tenir dans la hauteur de la vidéo ; tri « début,
   durée décroissante, libellé » ; barres passées voilées (calendar_common_renderer.js:266-268,
   calendar_renderer.scss:58-64) ; numéros de semaine (weekNumbers: true,
   calendar_common_renderer.js:119). Forme, couleurs des chambres, fenêtre
   de détail : ref_muk/028 et captures en lecture seule sur la base MuK
   (compte demo.reception). La fenêtre de détail n'a plus d'en-tête de date :
   hide_date masque la date du cadre d'Odoo (« octobre 14-16, 2026 », écart
   n° 43 corrigé dans la livraison 4 ; calendar_arch_parser.js:106-107,
   calendar_common_popover.js:96-107) et la plage n'étant pas d'un seul
   jour, aucune heure ne s'affiche ; les champs suivent dans l'ordre de la
   vue (calendar_arch_parser.js:129, calendar_common_popover.xml:44-66,
   libellé en gras) : « Arrivée 14/10/2026 14:00 », « Départ 16/10/2026
   12:00 » (formatDateTime sans les secondes, web/core/l10n/dates.js:
   395-411), Chambre, Client, Réservation, État. Pas de bouton « Supprimer » :
   calendrier delete="0" (:344, aite_hotel_management 18.0.1.0.6), et une
   ligne confirmée ou arrivée ne se supprime plus directement
   (_unlink_guard_line, hotel_reservation.py:770-800).
3. Réservation rapide — views/hotel_menus.xml:31-35 ; wizard/
   hotel_booking_wizard_views.xml:8-66 (« Hôtel », « Arrivée », « Départ »,
   « Type de chambre » et son aide, « Adultes », « Enfants », « Rechercher
   les chambres disponibles », colonnes « Réserver », « Chambre », « Type »,
   « Étage », « Cap. adultes », « Nuits », « Prix / nuit », « Total séjour
   (HT) », « Client », « Canal », « Confirmer immédiatement », « Réserver »,
   « Fermer ») ; wizard/hotel_booking_wizard.py:18-123 et :162-200 (défauts,
   recherche : chambres libres seulement, triées par type puis numéro, hors
   service et capacité exclues ; réservation confirmée d'un clic). Depuis la
   livraison 4 : la fenêtre garde son titre « Réservation rapide » après la
   recherche (action nommée, hotel_booking_wizard.py:116-118, écart n° 45
   corrigé : elle s'intitulait « Odoo ») ; le champ « Canal » (mêmes canaux
   que la réservation, « Direct / comptoir » par défaut, avec son aide :
   « Canal ? », comme « Type de chambre ? ») suit « Client » et
   passe sur la réservation (hotel_booking_wizard.py:46-55, :125-140 ;
   hotel_booking_wizard_views.xml:49-56 ; écart n° 56 corrigé). Rodrigue
   Tamba appelle : Mireille choisit « Téléphone / WhatsApp »
   (hotel_reservation.py:70-79 ; test_ecarts_nb.py:181-189 fait la même
   chose). Mise en page : ref_muk/022.
4. Fiche réservation — views/hotel_reservation_views.xml:37-170 (« Confirmer »,
   « Check-in », « Encaisser un acompte », « Envoyer la confirmation »,
   « Non présenté » (:59-61, anciennement « No-show », écart n° 42 corrigé),
   « Annuler », statusbar Brouillon / Confirmée / Arrivé / Parti, bouton
   « Folio » (:73-83), groupes « Client », « Séjour », « Canal &
   commission », « Occupation », onglets « Chambres » / « Demandes
   particulières », colonnes des lignes dont « Prix fixé » (price_locked,
   optional="show", :145-146 ; hotel_reservation.py:626-633), icône ⇄
   « Changer de chambre » (:155-158)) ; aite_guest_registry/views/
   hotel_reservation_views.xml:11-25 (bouton intelligent « Fiches
   d'enregistrement », anciennement « Fiches clients ») et :50-54 (bouton
   d'impression « Imprimer les fiches », anciennement « Fiches
   d'enregistrement ») ; canal « Direct / comptoir » pour la saisie au
   comptoir de Jacques Owona (défaut, hotel_reservation.py:70-79).
   « Client » est modifiable en brouillon et confirmée, « Hôtel » en
   brouillon seulement (:91-97) : champs de saisie (libellé gras, valeur
   soulignée, pas en lien — web/…/many2one_field.xml) ; « Hôtel » en lien
   sur la fiche confirmée de Rodrigue, en saisie sur le brouillon de
   Jacques.
   Statusbar réduite à l'état courant et boutons sur deux rangées,
   discussion à droite : ref_muk/027 (fiche). Discussion d'Odoo 18 :
   « Envoyer message », « Note », « Activités », séparateur de date
   « Aujourd'hui », « Aujourd'hui à 10:12 »
   (odoo18/addons/mail/static/src/core/common/message_model.js:225-262 ;
   mail/i18n/fr.po:10407-10408), suivi « ancien → nouveau (Champ) »
   (mail/static/src/core/web/message_patch.xml:15-19, dates avec les
   secondes : message_patch.js:92-97), message de création « Réservation
   créée » (_creation_message, hotel_reservation.py:286-290, écart n° 43
   corrigé : « Réservation hôtelière créé »).
5. Double réservation refusée — hotel_reservation.py:352-360 (message
   « La chambre %(room)s n'est pas disponible du %(cin)s au %(cout)s (déjà
   réservée ou hors service). », dates à l'heure de l'utilisateur au format
   « 15/10/2026 14:00 » : _fmt_local_datetime, :197-200, écart n° 37 corrigé
   — elles s'écrivaient en ISO et en UTC) ; UserError → « Opération
   invalide » et bouton « Fermer » (odoo18/addons/web/static/src/core/
   errors/error_dialogs.js:36, error_dialogs.xml:4-13, fr.po:3267-3269 et
   :1500-1502) ; la réservation reste « Brouillon » (le contrôle précède le
   changement d'état, :374-390). Le zoom cadre tout le message, la bulle dit
   qu'il nomme la chambre et les dates.
6. Prolonger — hotel_reservation.py:292-307 (dates modifiées sur une
   réservation confirmée : disponibilité revérifiée, folio resynchronisé),
   :206-214 (nuits), :216-223 (totaux) ; suivi du champ « Départ »
   (tracking=True, :60-62) ; test_reservation.py:370-377
   (test_extending_stay_updates_folio). Le bouton « Folio » affiche le solde
   (folio_amount_residual, views/hotel_reservation_views.xml:73-83 ;
   hotel_reservation.py:121-124). Convention de la série (fiche
   d'harmonisation) : aucun article sans TVA, taxe de séjour 3 ★ de
   3 000 FCFA par personne et par nuit. Rodrigue Tamba (RES/2026/0221), sans
   acompte, réservé pour une nuit en 201 : 45 000 + 6 000 = 51 000 FCFA ;
   prolongé d'une nuit : 90 000 + 12 000 = 102 000 FCFA, le folio de la
   série (t03_folio.py, t08_site_web.py). Estelle Ngono n'est ni prolongée
   ni déplacée : elle garde la 204 du 14 au 16/10 (fiche d'harmonisation).
   Montants des champs au format d'Odoo (ecrans.fcfa : espace insécable).
7. Changer de chambre — wizard/hotel_room_change_wizard_views.xml:4-38
   (« Changer de chambre », groupes « Séjour » / « Nouvelle chambre »,
   « Client », « Chambre actuelle », « Arrivée », « Départ », « Nouvelle
   chambre », « Conserver le prix actuel », « Prix actuel / nuit »,
   « Nouveau prix / nuit », « ? » après « Prix actuel / nuit » (champ lié à
   price_night, dont il hérite l'aide : hotel_reservation.py:619-625,
   odoo18/odoo/fields.py:767), « Changer la chambre », « Annuler » ; le
   bandeau « Surclassement gracieux : … » n'apparaît que case cochée,
   invisible="not keep_price") ; wizard/hotel_room_change_wizard.py:20-102
   (aides, prix ; case cochée, la ligne passe « Prix fixé » et le message
   « Surclassement gracieux : le tarif de 45 000 FCFA / nuit est conservé. »
   est posté — montant avec la devise depuis la livraison 4, format_amount,
   :95-101, écart n° 40 corrigé ; le prix fixé n'est plus recalculé par une
   prolongation : _compute_price_night, hotel_reservation.py:657-678, et
   l'aide du champ « Prix fixé » ; tests test_ecarts_videos.py:87-139).
   Ici, de la 201 à la 203, deux Confort à 45 000, la case reste décochée,
   « Prix fixé » aussi, et la bulle en dit l'usage d'après les deux aides ;
   hotel_reservation.py:816-849 (disponibilité contrôlée, message
   « Changement de chambre : %(old)s → %(new)s. », folio resynchronisé) ;
   tests test_reservation.py:305-338, test_wizards.py:264-282. Rodrigue
   Tamba finit en 203, du 19 au 21/10 : la réservation de la série
   (t03_folio.py, t08_site_web.py).

Chiffres des résultats : 49 tests automatisés — addons/aite_hotel_management/
tests/test_room_pricing.py:209-249 (7 tests de disponibilité),
test_reservation.py:133, 148, 241, 305, 315, 326, 370, 379, 390, 406 (10),
test_wizards.py:27-114, 264 et 273 (14), test_ecarts_videos.py:87-240 (12 :
prix fixé et prolongation 3, double vente 4, suppression depuis le
planning 5, ajoutés avec aite_hotel_management 18.0.1.0.6),
test_ecarts_nb.py:82, 126, 177, 181, 191, 201 (6, livraison 4 : dates du
refus, montant du surclassement, titre et canal de la Réservation rapide) ;
1 clic — bouton « Rechercher les chambres disponibles »
(hotel_booking_wizard_views.xml:24-26) ; 2 éditions — le même menu
« Planning des chambres », sur Community comme sur Enterprise : le socle ne
dépend d'aucun module Enterprise et porte la vue calendrier
(docs/RAPPORT_TESTS.md:44-68, A1 ; views/hotel_reservation_views.xml:
334-420 ; vérifié par installation sur Community) ; sur Enterprise, le
module passerelle aite_hotel_gantt garde la vue calendrier dans l'action
(view_mode « gantt,calendar,list,form », aite_hotel_gantt/views/
hotel_reservation_gantt_views.xml:8-35). Ni le Gantt ni une installation
automatique ne sont annoncés : web_gantt n'est ni dans le dépôt ni sur une
base de démonstration, et sur une base Enterprise où le socle est déjà
installé, aite_hotel_gantt ne s'installe pas seul à la mise à niveau (il
s'installe à la main depuis Apps, écart n° 72).

ÉCARTS : ceux que ce tutoriel rejouait tels quels sont corrigés dans la
livraison 4 et l'écran suit le produit — dates du refus en heure locale
au format français (n° 37) ; titre « Réservation rapide » conservé après la
recherche (n° 45) ; fenêtre de détail sans la date « octobre 14-16, 2026 »,
avec Arrivée et Départ (n° 43) ; « Réception » et « Non présenté » au lieu
de « Front Desk » et « No-show » (n° 42) ; « Réservation créée » au lieu de
« Réservation hôtelière créé » (n° 43) ; montant du surclassement avec la
devise (n° 40, non montré). « Check-in » (bouton de la fiche confirmée)
reste tel quel : décision laissée à l'équipe (ECARTS.md, « Restent à
trancher », et n° 42). Déjà corrigés dans aite_hotel_management 18.0.1.0.6
(ECARTS n° 31, 32, 33) : le prix
conservé par un surclassement gracieux survit à la prolongation (colonne
« Prix fixé », rejouée) ; un séjour « Arrivé » dont le départ est dépassé
bloque sa chambre jusqu'au check-out (non montré) ; plus de bouton
« Supprimer » dans la fenêtre de détail du planning (rejoué : « Modifier »
seul).

Cohérence de la série (fiche d'harmonisation) : nuitées sans TVA partout
(t01, t03, t05, t06) ; Martin Ebode en 104 [STD] comme dans t06 et t07, et
comme le veut son tarif (105 000 FCFA pour 3 nuits, demo.ARRIVEES) ; Estelle
Ngono en 204 du 14 au 16/10, jamais prolongée ni déplacée. Limite assumée :
le calendrier d'Odoo n'empile que cinq séjours par case avant « +N en plus »
(voir 2.) ; le planning ne peut donc pas montrer les 55-65 % d'occupation des
tableaux de bord (t01, t15) sans masquer le séjour d'Estelle derrière un
« +N en plus » : il garde une occupation lisible, jusqu'à cinq séjours par
jour, et les nuits passées ne sont qu'en partie remplies.

Voix : « planning » s'écrit « planinng » dans les phrases de la voix
seulement (Kokoro lit « planning » à l'anglaise ; « planinng » donne la
prononciation française [planiŋ]), jamais à l'écran.

Données : demo.py (Complexe Hôtelier — Démo, Démo Hôtellerie SARL, Estelle
Ngono, RES/2026/0214, chambre 204 [CFT] Confort à 45 000 FCFA la nuit,
arrivée le 14/10/2026 à 14:00, départ le 16/10/2026 à 12:00 ; Claire Durand,
RES/2026/0201, 401 [VIP]) ; les 20 chambres de la série (fiche
d'harmonisation) : 101-107 [STD] au rez-de-chaussée, dont la 105 hors
service, donc sans séjour et absente du filtre « Chambre » (le calendrier
ne liste que les chambres des séjours chargés) ; 201-206 [CFT] au 1er
étage, 301-304 [SJR] au 2e, 401-403 [VIP] au 3e ; tarifs Standard 35 000,
Confort 45 000, Suite Junior 75 000, Suite VIP 120 000 FCFA. Couleurs des
chambres : relevées sur la base MuK, puis, pour 107, 206, 304 et 403, la
suite de la palette d'Odoo ($o-colors-secondary, odoo18/addons/web/static/
src/scss/secondary_variables.scss:11-18). Les autres clients sont fictifs
(Martin Ebode, RES/2026/0209, 104 [STD], du 14/10/2026 14:00:00 au
17/10/2026 12:00:00 : demo.ARRIVEES ; Brigitte Essomba en 202 du 13 au
16/10, Gaston Mbida en 103 du 15 au 17/10, Joël Kamga en 204 du 18 au 20/10,
Aristide Bella en 401 du 24 au 26/10 ; téléphones de Rodrigue Tamba et
Jacques Owona dans la plage de fiction +237 6 00 00 00 xx ; Rodrigue Tamba
réserve au téléphone, canal « Téléphone / WhatsApp ») ; « aujourd'hui » est
le mercredi 14/10/2026, comme dans la vidéo de présentation.
"""

import datetime as dt

import demo
from ecrans import APPS_PROFIL, ICONES, MENUS_MUK, NBSP, _id, e, entree, fcfa, fenetre_muk, icone, navigateur, vue_libre
from marketing import bulle, dezoom, reaction, zoom
from moteur import anneau, cacher, choisir, clic, classe, curseur, fermer, montrer, ouvrir, pause, saisir, texte, vue

NOM, ROLE = demo.POSTES['reception']
MENUS = MENUS_MUK['hotel_reception']     # « Réception » (anciennement « Front Desk », écart n° 42)
APP = 'app-t02'


def menu(nom):
    """Le sélecteur d'un menu de la barre (grille, nom de l'application, puis les menus)."""
    return '#%s .o-haut .menu:nth-child(%d)' % (APP, MENUS.index(nom) + 3)


# ------------------------------------------------------------ les données --
J0 = dt.date(2026, 9, 28)          # le lundi de la semaine 40 : première case du mois affiché
AUJ = dt.date(2026, 10, 14)        # aujourd'hui (mercredi) : arrivée d'Estelle Ngono

# Les 20 chambres de la série (fiche d'harmonisation) : type, étage ; couleurs du
# calendrier relevées sur la base MuK (ref_muk/028, panneau « Chambre »), puis la
# suite de la palette d'Odoo pour 107, 206, 304 et 403. La 105, hors service, n'a
# aucun séjour : le filtre « Chambre » ne la liste pas.
TYPES = {'STD': ('Standard', 35000), 'CFT': ('Confort', 45000), 'SJR': ('Suite Junior', 75000),
         'VIP': ('Suite VIP', 120000)}
CHAMBRES = {
    '101': ('STD', 'Rez-de-chaussée', '#EE2F8A'), '102': ('STD', 'Rez-de-chaussée', '#61C36E'),
    '103': ('STD', 'Rez-de-chaussée', '#9872E6'), '104': ('STD', 'Rez-de-chaussée', '#AA4B6B'),
    '106': ('STD', 'Rez-de-chaussée', '#97743A'), '107': ('STD', 'Rez-de-chaussée', '#999966'),
    '201': ('CFT', '1er étage', '#F7CD1F'), '202': ('CFT', '1er étage', '#4285F4'), '203': ('CFT', '1er étage', '#8E24AA'),
    '204': ('CFT', '1er étage', '#D6145F'), '205': ('CFT', '1er étage', '#173E43'), '206': ('CFT', '1er étage', '#E9D362'),
    '301': ('SJR', '2e étage', '#348F50'), '302': ('SJR', '2e étage', '#AA3A38'), '303': ('SJR', '2e étage', '#795548'),
    '304': ('SJR', '2e étage', '#B56969'),
    '401': ('VIP', '3e étage', '#5E0231'), '402': ('VIP', '3e étage', '#6BE585'), '403': ('VIP', '3e étage', '#649173'),
}
assert len(CHAMBRES) == 19           # 20 chambres, moins la 105 hors service


def D(mois, jour):
    return dt.date(2026, mois, jour)


# Les séjours du mois (chambre, client, arrivée, départ), un par réservation.
SEJOURS = [
    ('101', 'Patrick Nkoulou', D(9, 25), D(9, 29)), ('402', 'Lydie Eboa', D(9, 27), D(10, 3)),
    ('203', 'Simon Nyemb', D(9, 28), D(10, 1)), ('205', 'Thierry Ewane', D(9, 29), D(9, 30)),
    ('301', 'Armand Mvogo', D(9, 30), D(10, 2)), ('102', 'Boris Nguema', D(10, 1), D(10, 3)),
    ('303', 'Didier Onana', D(10, 1), D(10, 4)), ('104', 'Franck Moukoko', D(10, 2), D(10, 4)),
    ('201', 'Aurélie Tchinda', D(10, 3), D(10, 5)), ('302', 'Sylvie Mbarga', D(10, 5), D(10, 7)),
    ('106', 'Hugues Ondoa', D(10, 5), D(10, 6)), ('205', 'Pauline Ekotto', D(10, 6), D(10, 9)),
    ('202', 'Nadine Ekambi', D(10, 7), D(10, 9)), ('103', 'Esther Mengue', D(10, 8), D(10, 10)),
    ('401', 'Laurent Abega', D(10, 9), D(10, 12)), ('101', 'Cyrille Owono', D(10, 10), D(10, 13)),
    ('107', 'Ernest Abomo', D(10, 5), D(10, 7)), ('206', 'Nathalie Kotto', D(10, 5), D(10, 8)),
    ('403', 'Alice Ngo Mbe', D(10, 9), D(10, 11)), ('304', 'Ulrich Ekane', D(10, 12), D(10, 13)),
    ('302', 'Gisèle Abanda', D(10, 12), D(10, 14)), ('202', 'Brigitte Essomba', D(10, 13), D(10, 16)),
    ('204', demo.CLIENT, D(10, 14), D(10, 16)), ('104', 'Martin Ebode', D(10, 14), D(10, 17)),
    ('401', 'Claire Durand', D(10, 14), D(10, 15)),
    ('103', 'Gaston Mbida', D(10, 15), D(10, 17)), ('301', 'Paul Abessolo', D(10, 16), D(10, 18)),
    ('204', 'Joël Kamga', D(10, 18), D(10, 20)), ('102', 'Christelle Ndongo', D(10, 21), D(10, 23)),
    ('302', 'Carine Manga', D(10, 22), D(10, 24)), ('106', 'Olivier Ndzana', D(10, 23), D(10, 25)),
    ('401', 'Aristide Bella', D(10, 24), D(10, 26)), ('205', 'Blaise Atangana', D(10, 28), D(10, 31)),
    ('104', 'Mathieu Nkodo', D(10, 30), D(11, 1)), ('303', 'Viviane Eyoum', D(11, 4), D(11, 6)),
]
# Rodrigue Tamba, réservé au téléphone pendant le tutoriel (Réservation rapide) : une
# nuit en 201 ; il rappelle, reste une nuit de plus et passe en 203 — la réservation
# de la série (203, du 19 au 21/10). Estelle Ngono, elle, ne bouge pas.
RODRIGUE = ('201', 'Rodrigue Tamba', D(10, 19), D(10, 20))
RODRIGUE_FIN = ('203', 'Rodrigue Tamba', D(10, 19), D(10, 21))
ETATS = {
    'initial': SEJOURS,
    'reserve': SEJOURS + [RODRIGUE],
    'final': SEJOURS + [RODRIGUE_FIN],
}

# Les réservations confirmées de la liste de départ (référence, client, arrivée, départ, chambre).
CONFIRMEES = [
    ('RES/2026/0220', 'Viviane Eyoum', '04/11/2026 14:00:00', '06/11/2026 12:00:00', 2, '303'),
    ('RES/2026/0219', 'Mathieu Nkodo', '30/10/2026 14:00:00', '01/11/2026 12:00:00', 2, '104'),
    ('RES/2026/0215', 'Blaise Atangana', '28/10/2026 14:00:00', '31/10/2026 12:00:00', 3, '205'),
    ('RES/2026/0218', 'Aristide Bella', '24/10/2026 14:00:00', '26/10/2026 12:00:00', 2, '401'),
    ('RES/2026/0217', 'Olivier Ndzana', '23/10/2026 14:00:00', '25/10/2026 12:00:00', 2, '106'),
    ('RES/2026/0212', 'Carine Manga', '22/10/2026 14:00:00', '24/10/2026 12:00:00', 2, '302'),
    ('RES/2026/0216', 'Christelle Ndongo', '21/10/2026 14:00:00', '23/10/2026 12:00:00', 2, '102'),
    ('RES/2026/0211', 'Joël Kamga', '18/10/2026 14:00:00', '20/10/2026 12:00:00', 2, '204'),
    ('RES/2026/0205', 'Paul Abessolo', '16/10/2026 14:00:00', '18/10/2026 12:00:00', 2, '301'),
    ('RES/2026/0213', 'Gaston Mbida', '15/10/2026 14:00:00', '17/10/2026 12:00:00', 2, '103'),
    ('RES/2026/0201', 'Claire Durand', '14/10/2026 18:00:00', '15/10/2026 12:00:00', 1, '401'),
    (demo.RESA, demo.CLIENT, demo.ARRIVEE, demo.DEPART, 2, '204'),
    ('RES/2026/0209', 'Martin Ebode', '14/10/2026 14:00:00', '17/10/2026 12:00:00', 3, '104'),
]

# Le bouton « Folio » affiche le solde du folio (folio_amount_residual). Convention de la série
# (fiche d'harmonisation) : nuitée sans TVA, taxe de séjour 3 ★ de 3 000 FCFA par personne et
# par nuit. Rodrigue Tamba, deux adultes, sans acompte : une nuit, 45 000 + 2 × 3 000 = 51 000 ;
# prolongé d'une nuit, 2 × 45 000 + 2 × 2 × 3 000 = 102 000 (t03_folio.py, t08_site_web.py).
TAXE_NUIT_PERS = 3000


def solde_folio(nuits, acompte=0, prix=45000, personnes=2):
    return fcfa(nuits * prix + nuits * personnes * TAXE_NUIT_PERS - acompte)


FOLIO_AVANT, FOLIO_RODRIGUE = solde_folio(1), solde_folio(2)
TOTAL_AVANT, TOTAL_APRES = fcfa(45000), fcfa(2 * 45000)
# Montants des champs d'Odoo : espace insécable entre les milliers et avant « FCFA » (ecrans.fcfa).
PRIX_CFT = fcfa(TYPES['CFT'][1])
assert [m.replace(NBSP, ' ') for m in (FOLIO_AVANT, FOLIO_RODRIGUE, TOTAL_AVANT, TOTAL_APRES, PRIX_CFT)] == [
    '51 000 FCFA', '102 000 FCFA', '45 000 FCFA', '90 000 FCFA', demo.PRIX_NUIT]


# ------------------------------------------------------------ le planning --

def _teinte(couleur, part):
    """La couleur d'une chambre mêlée de blanc (part = poids de la couleur)."""
    r, v, b = (int(couleur[i:i + 2], 16) for i in (1, 3, 5))
    return '#%02X%02X%02X' % tuple(int(round(part * x + (1 - part) * 255)) for x in (r, v, b))


# Le calendrier d'Odoo 18 : eventLimit = 5 (calendar_arch_parser.js:26) passé à FullCalendar
# en dayMaxEventRows (calendar_common_renderer.js:87). Une case montre jusqu'à cinq rangées ;
# au-delà, quatre rangées et « +N en plus » (fullcalendar/daygrid/index.global.js:284-292,
# core/index.global.js:4851-4855 : insertion valide tant que la pile compte moins de 5).
MAX_RANGEES = 5
HAUT_GRILLE = 584          # 796 (fenêtre MuK) - 58 (barre du haut) - 126 (titre, barre) - 28 (jours)
TETE_CASE, PAS, H_BARRE = 24, 18, 17


def disposer(sejours):
    """Les barres du mois, semaine par semaine, comme FullCalendar les empile :
    triées par arrivée, la plus longue d'abord, puis par libellé (« start,
    -duration, title »), chacune sur la première rangée libre. Aucune case
    de ces données ne dépasse cinq rangées : toutes les barres sont visibles,
    sans « +N en plus » (contrôlé)."""
    segs = []
    for ch, cli, a, d in sejours:
        for r in range(6):
            r0 = J0 + dt.timedelta(days=7 * r)
            r1 = r0 + dt.timedelta(days=6)
            if d < r0 or a > r1:
                continue
            s0, s1 = max(a, r0), min(d, r1)
            segs.append({'ch': ch, 'cli': cli, 'a': a, 'd': d, 'r': r, 'c': (s0 - r0).days, 'n': (s1 - s0).days + 1,
                         'debut': a >= r0, 'fin': d <= r1})
    niveaux = [0] * 6
    for r in range(6):
        rang = sorted((s for s in segs if s['r'] == r), key=lambda s: (s['a'], -(s['d'] - s['a']).days, s['ch']))
        occupe = set()
        for s in rang:
            ligne = 0
            while any((ligne, c) in occupe for c in range(s['c'], s['c'] + s['n'])):
                ligne += 1
            occupe.update((ligne, c) for c in range(s['c'], s['c'] + s['n']))
            s['l'] = ligne
            niveaux[r] = max(niveaux[r], ligne + 1)
    assert max(niveaux) <= MAX_RANGEES, 'une case dépasse %d rangées : il faudrait « +N en plus »' % MAX_RANGEES
    return segs, niveaux


def hauteurs(niveaux):
    """La hauteur de chaque semaine : la grille remplit l'écran (height: 100 %), une
    semaine dont les barres ne tiennent pas dans sa part s'allonge, les autres se
    partagent le reste."""
    besoin = [TETE_CASE + PAS * n + 3 for n in niveaux]
    h, libres, reste = [0.0] * 6, list(range(6)), float(HAUT_GRILLE)
    while True:
        part = reste / len(libres)
        gros = [r for r in libres if besoin[r] > part]
        if not gros:
            break
        for r in gros:
            h[r] = float(besoin[r])
            reste -= besoin[r]
            libres.remove(r)
    for r in libres:
        h[r] = part
    return h


def _cle(s):
    return (s['ch'], s['cli'], s['r'], s['c'], s['n'], s['l'])


def _barre(s, hauts, ident=None, cache=False):
    couleur = CHAMBRES[s['ch']][2]
    passe = s['d'] < AUJ          # départ à 12 h, avant maintenant : la barre est voilée
    top = sum(hauts[:s['r']]) + TETE_CASE + PAS * s['l']
    style = ('left:calc(%d * 100%% / 7 + %dpx);width:calc(%d * 100%% / 7 - %dpx);top:%.1fpx;'
             'background:%s;border-color:%s'
             % (s['c'], 3 if s['debut'] else 0, s['n'], (3 if s['debut'] else 0) + (3 if s['fin'] else 0), top,
                _teinte(couleur, .42), _teinte(couleur, .7)))
    classes = 't02-ev' + (' passe' if passe else '') + ('' if s['debut'] else ' suite') + ('' if s['fin'] else ' coupe')
    return ('<div class="%s%s"%s style="%s"><span class="ell">%s · %s</span></div>'
            % (classes, ' masque' if cache else '', _id(ident), style, e(s['ch']), e(s['cli'])))


def _ident(s):
    if s['cli'] == demo.CLIENT and s['r'] == 2:
        return 't02-b-estelle'
    if s['cli'] == RODRIGUE[1]:
        return 't02-b-rodrigue' if s['ch'] == RODRIGUE[0] else 't02-b-rodrigue2'
    return None


def couches():
    """Les barres de l'état initial, puis celles qui apparaissent ou
    disparaissent à chaque étape : les autres ne bougent pas (contrôlé)."""
    etats = {k: disposer(v) for k, v in ETATS.items()}
    base, niv0 = etats['initial']
    hauts = hauteurs(niv0)
    for k in ('reserve', 'final'):
        assert etats[k][1] == niv0, 'la hauteur des semaines change : %s' % k
        cles = {_cle(s) for s in etats[k][0]}
        for s in base:
            assert _cle(s) in cles, 'une barre change de rangée : %s %s' % (k, s['cli'])
    html = ''.join(_barre(s, hauts, _ident(s)) for s in base)
    deja = {_cle(s) for s in base}
    for k in ('reserve', 'final'):
        for s in etats[k][0]:
            if _cle(s) not in deja:
                deja.add(_cle(s))
                html += _barre(s, hauts, _ident(s), cache=True)
    return html, hauts


BARRES, HAUTS = couches()


JOURS = ['LUN.', 'MAR.', 'MER.', 'JEU.', 'VEN.', 'SAM.', 'DIM.']
VUE_CAL = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="5" width="18" '
           'height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/><path d="M7 14h3M14 14h3M7 17.5h3" stroke-width="2.4"/>'
           '</svg>')
VUE_LISTE = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round">'
             '<path d="M4 6h16M4 12h16M4 18h16"/></svg>')
PANNEAU_I = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" '
             'height="16" rx="1.5"/><path d="M15 4v16" stroke-width="5"/></svg>')
ROUAGE = ('<svg viewBox="0 0 24 24" fill="#495057"><path d="M10.3 2h3.4l.5 2.6 1.9.8 2.2-1.5 2.4 2.4-1.5 2.2.8 1.9 '
          '2.6.5v3.4l-2.6.5-.8 1.9 1.5 2.2-2.4 2.4-2.2-1.5-1.9.8-.5 2.6h-3.4l-.5-2.6-1.9-.8-2.2 1.5-2.4-2.4 1.5-2.2-.8-1.9'
          'L2 13.7v-3.4l2.6-.5.8-1.9-1.5-2.2 2.4-2.4 2.2 1.5 1.9-.8z"/><circle cx="12" cy="12" r="3.4" fill="#fff"/></svg>')
NUAGE = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
         'stroke-linejoin="round"><path d="M7 18h10.5a4 4 0 00.6-7.95A6 6 0 006.3 9.2 4.5 4.5 0 007 18z"/>'
         '<path d="M12 16v-6M9.5 12.5L12 10l2.5 2.5"/></svg>')
ANNULER_I = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" '
             'stroke-linejoin="round"><path d="M9 7H4V2"/><path d="M4.5 7A8 8 0 1112 20"/></svg>')
IMPRIMER_I = icone('imprimer', 't02-bi')


def _cellules():
    cases = []
    for r in range(6):
        for c in range(7):
            jour = J0 + dt.timedelta(days=7 * r + c)
            hors = jour.month != 10
            num = '<b class="t02-auj">%d</b>' % jour.day if jour == AUJ else str(jour.day)
            sem = '<span class="t02-sem">%d</span>' % (40 + r) if c == 0 else ''
            cases.append('<div class="t02-case%s">%s<span class="t02-num">%s</span></div>'
                         % (' hors' if hors else '', sem, num))
    return ''.join(cases)


def _mini():
    tete = ''.join('<span>%s</span>' % j for j in 'LMMJVSD')
    jours = []
    for i in range(35):
        jour = J0 + dt.timedelta(days=i)
        if jour.month != 10:
            jours.append('<span></span>')
        else:
            jours.append('<span class="%s">%d</span>' % ('auj' if jour == AUJ else '', jour.day))
    return ('<div class="t02-mini"><div class="t02-mini-t"><span>‹</span><b>octobre 2026</b><span>›</span></div>'
            '<div class="t02-mini-g">%s%s</div></div>' % (tete, ''.join(jours)))


def _filtres():
    lignes = ''.join('<div class="t02-filtre"><i style="background:%s;border-color:%s"></i>%s [%s]</div>'
                     % (CHAMBRES[ch][2], CHAMBRES[ch][2], ch, CHAMBRES[ch][0]) for ch in CHAMBRES)
    return ('<div class="t02-filtres" id="t02-filtres"><div class="t02-filtre tete"><i class="coche"></i><b>Chambre</b> ▾'
            '</div>%s</div>' % lignes)


def _recherche():
    return ('<div class="recherche t02-rech">%s<span class="ph">Rechercher…</span><span class="deroule">▾</span></div>'
            % icone('loupe', 'loupe'))


# La fenêtre de détail d'une barre : sans en-tête de date (hide_date="1", écart n° 43 corrigé), les
# champs du calendrier dans l'ordre de la vue, Arrivée et Départ sans les secondes (show_seconds).
POP_ARRIVEE, POP_DEPART = demo.ARRIVEE[:-3], demo.DEPART[:-3]          # « 14/10/2026 14:00 »
POPOVER = (
    '<div class="t02-pop masque" id="t02-pop" data-layout-allow-overlap data-layout-allow-occlusion>'
    '<div class="t02-pop-t" style="background:%s"><span>%s · %s</span><span class="t02-pop-x">%s</span></div>'
    '<div class="t02-pop-c">'
    '<div class="t02-pop-ch"><span>Arrivée</span><i>%s</i></div><div class="t02-pop-ch"><span>Départ</span><i>%s</i></div>'
    '<div class="t02-pop-ch"><span>Chambre</span><b>%s</b></div><div class="t02-pop-ch"><span>Client</span><b>%s</b></div>'
    '<div class="t02-pop-ch"><span>Réservation</span><b>%s</b></div>'
    '<div class="t02-pop-ch"><span>État</span><i>Confirmée</i></div></div>'
    '<div class="t02-pop-p"><span class="bt primaire">Modifier</span></div></div>'
    % (_teinte(CHAMBRES['204'][2], .3), '204', e(demo.CLIENT), ICONES['x'], e(POP_ARRIVEE), e(POP_DEPART),
       e(demo.CHAMBRE), e(demo.CLIENT), e(demo.RESA)))
assert (POP_ARRIVEE, POP_DEPART) == ('14/10/2026 14:00', '16/10/2026 12:00')

PLANNING = vue_libre('t02-planning', (
    '<div class="t02-pl">'
    '<div class="t02-cp"><span class="t02-titre">Planning des chambres</span>%s'
    '<span class="t02-vues"><span class="actif">%s</span><span>%s</span></span></div>'
    '<div class="t02-barre"><span class="t02-fl"><span>←</span><span>→</span></span><span class="bt gris">Mois ▾</span>'
    '<span class="bt gris">Aujourd\'hui</span><span class="t02-mois">octobre 2026</span>'
    '<span class="t02-panneau-i">%s</span></div>'
    '<div class="t02-cal"><div class="t02-jours">%s</div>'
    '<div class="t02-grille" id="t02-grille" style="grid-template-rows:%s">%s<div class="t02-evs" id="t02-evs">%s'
    '</div></div></div>'
    '<div class="t02-panneau">%s%s</div>%s</div>'
    % (_recherche(), VUE_CAL, VUE_LISTE, PANNEAU_I, ''.join('<span>%s</span>' % j for j in JOURS),
       ' '.join('%.1fpx' % h for h in HAUTS), _cellules(), BARRES, _mini(), _filtres(), POPOVER)))


# ------------------------------------------------- la liste de départ --

def _liste():
    gab = '40px 172px 1fr 204px 204px 64px 120px 200px 128px 34px'
    tete = ('<div class="t02-l-tete" style="grid-template-columns:%s"><span class="cb"></span><span>Référence</span>'
            '<span>Client</span><span>Arrivée</span><span>Départ</span><span class="d">Nuits</span>'
            '<span class="d">Nb chambres</span><span class="d ell">Total hébergement (HT)</span><span>État</span>'
            '<span class="t02-opt">⇋</span></div>' % gab)
    lignes, total = [], 0
    for ref, cli, arr, dep, nuits, ch in CONFIRMEES:
        montant = nuits * TYPES[CHAMBRES[ch][0]][1]
        total += montant
        lignes.append('<div class="t02-l-ligne" style="grid-template-columns:%s"><span class="cb"></span>'
                      '<span>%s</span><span class="ell">%s</span><span>%s</span><span>%s</span><span class="d">%d</span>'
                      '<span class="d">1</span><span class="d">%s</span><span>%s</span><span></span></div>'
                      % (gab, e(ref), e(cli), e(arr), e(dep), nuits, fcfa(montant),
                         '<span class="puce info">Confirmée</span>'))
    pied = ('<div class="t02-l-total" style="grid-template-columns:%s"><span></span><span></span><span></span><span></span>'
            '<span></span><span></span><span></span><span class="d">%s</span><span></span><span></span></div>'
            % (gab, fcfa(total)))
    filtre = ('<span class="facette"><span class="fic">%s</span><span class="ell">Confirmées</span><span class="fx">×</span>'
              '</span>' % ICONES['filtre'])
    cp = ('<div class="t02-cp"><span class="bt primaire">Nouveau</span><span class="t02-titre">Réservations'
          '<span class="t02-rouage">%s</span></span><div class="recherche t02-rech">%s%s<span class="ph"></span>'
          '<span class="deroule">▾</span></div><span class="t02-pager">1-13 / 13</span>'
          '<span class="t02-vues"><span class="actif">%s</span><span>▦</span><span>%s</span></span></div>'
          % (ROUAGE, icone('loupe', 'loupe'), filtre, VUE_LISTE, VUE_CAL))
    return vue_libre('t02-liste', '<div class="t02-pl">%s<div class="t02-l">%s%s%s</div></div>'
                     % (cp, tete, ''.join(lignes), pied), initiale=True)


LISTE = _liste()


# ------------------------------------------------- les fiches réservation --

def ch(libelle, valeur, ident=None, saisie=False, lien=False, aide=False, html=False):
    """Un champ de fiche : libellé gras s'il est modifiable (Odoo 18), valeur soulignée si saisissable."""
    lib = e(libelle) + ('<sup class="t02-aide">?</sup>' if aide else '')
    val = valeur if html else e(valeur)
    return ('<div class="t02-ch"><span class="l%s">%s</span><span class="v%s%s"%s>%s</span></div>'
            % (' gras' if saisie else '', lib, ' saisie' if saisie else '', ' lien' if lien else '', _id(ident), val))


def grp(titre, champs):
    return '<div class="t02-grp"><div class="t02-grp-t">%s</div>%s</div>' % (e(titre), ''.join(champs))


def stat(ident, ico, libelle, valeur):
    return ('<span class="t02-stat"%s>%s<span class="t"><span>%s</span><b%s>%s</b></span></span>'
            % (_id(ident), icone(ico, 't02-sic'), e(libelle), _id(ident and ident + '-v'), e(valeur)))


def bt(ident, libelle, style='gris', ico=''):
    return '<span class="bt %s"%s>%s%s</span>' % (style, _id(ident), ico, e(libelle))


# « Prix fixé » (price_locked, optional="show") entre « Prix / nuit » et « Sous-total (HT) ».
GAB_L = '104px 104px 70px 72px 92px 52px 120px 84px 132px 30px 26px'


def ligne_chambre(p, type_, chambre, nuits, prix, total, echange=True):
    return ('<div class="t02-t-ligne" style="grid-template-columns:%s"><span id="%s-type">%s</span>'
            '<span id="%s-ch">%s</span><span class="d">2</span><span class="d">0</span><span></span>'
            '<span class="d" id="%s-n">%s</span><span class="d">%s</span><span class="t02-pf"><span class="case"><i></i>'
            '</span></span><span class="d ell" id="%s-st">%s</span>'
            '<span class="t02-ech"%s>%s</span><span class="t02-corb">%s</span></div>'
            % (GAB_L, p, e(type_), p, e(chambre), p, e(nuits), e(prix), p, e(total), _id(p + '-ech') if echange else '',
               '⇄' if echange else '', icone('corbeille', 't02-ci')))


def table_chambres(lignes_html):
    return ('<div class="t02-onglets"><span class="actif">Chambres</span><span>Demandes particulières</span></div>'
            '<div class="t02-table"><div class="t02-t-tete" style="grid-template-columns:%s"><span>Type</span>'
            '<span>Chambre</span><span class="d">Adultes</span><span class="d">Enfants</span><span>Occupants</span>'
            '<span class="d">Nuits</span><span class="d">Prix / nuit</span><span class="ell">Prix fixé</span>'
            '<span class="d ell">Sous-total (HT)</span>'
            '<span></span><span class="t02-opt">⇋</span></div>%s<div class="t02-t-ajout">Ajouter une ligne</div></div>'
            % (GAB_L, lignes_html))


def message(auteur, date, corps, ident=None):
    return ('<div class="t02-msg"%s><span class="t02-av">%s</span><div><div class="t02-msg-a"><b>%s</b> <small>%s</small>'
            '</div><div class="t02-msg-t">%s</div></div></div>' % (_id(ident), e(auteur[0]), e(auteur), e(date), corps))


def separateur(texte_):
    return '<div class="t02-sep"><span>%s</span></div>' % e(texte_)


def discussion(etats, ident):
    """La discussion à droite (thème MuK) ; ``etats`` : ses contenus successifs, superposés."""
    piles = ''.join('<div class="t02-ch-etat%s" id="%s-%d">%s</div>' % ('' if i == 0 else ' masque', ident, i, h)
                    for i, h in enumerate(etats))
    return ('<div class="t02-chatter"><div class="t02-ch-bts"><span class="bt primaire">%sEnvoyer message</span>'
            '<span class="bt gris">Note</span><span class="bt gris">%sActivités</span>'
            '<span class="t02-ch-ic">%s</span></div><div class="t02-ch-fil">%s</div></div>'
            % (icone('message', 't02-bi'), icone('horloge', 't02-bi'), icone('loupe', 't02-bi'), piles))


def fiche(p, parent, ref, entete, stats, client, sejour, canal, occupation, lignes, chatter, enregistrer=False):
    """Une réservation : panneau, en-tête (boutons, état), feuille à gauche, discussion à droite."""
    save = ('<span class="t02-save masque" id="%s-save"><span class="t02-si" id="%s-save-ok">%s</span>'
            '<span class="t02-si">%s</span></span>' % (p, p, NUAGE, ANNULER_I)) if enregistrer else ''
    cp = ('<div class="t02-f-cp"><span class="bt contour">Nouveau</span><div class="t02-fil"><span class="t02-parent">%s'
          '</span><span class="t02-ref">%s<span class="t02-rouage">%s</span>%s</span></div><div class="t02-stats">%s</div>'
          '</div>' % (e(parent), e(ref), ROUAGE, save, stats))
    feuille = ('<div class="t02-f-titre">%s</div><div class="t02-cols"><div>%s%s</div><div>%s%s</div></div>%s'
               % (e(ref), client, canal, sejour, occupation, table_chambres(lignes)))
    gauche = ('<div class="t02-f-g"><div class="t02-hd">%s</div><div class="t02-feuille" id="%s-feuille">'
              '<div class="t02-defil" id="%s-defil">%s</div></div></div>' % (entete, p, p, feuille))
    return vue_libre(p, '<div class="t02-f">%s%s%s</div>' % (cp, gauche, chatter))


def client_grp(nom, tel, mail, brouillon=False):
    """Groupe « Client » : le client reste modifiable en brouillon et confirmée, l'hôtel en brouillon seulement
    (hotel_reservation_views.xml:91-97). Un many2one modifiable est un champ de saisie, pas un lien
    (web/…/many2one_field.xml) ; en lecture seule, l'hôtel s'affiche en lien."""
    hotel = ch('Hôtel', demo.HOTEL, saisie=True) if brouillon else ch('Hôtel', demo.HOTEL, lien=True)
    return grp('Client', [ch('Client', nom, saisie=True), ch('Téléphone', tel), ch('E-mail', mail), hotel])


def occupation_grp():
    return grp('Occupation', [ch('Nb chambres', '1'), ch('Adultes', '2'), ch('Enfants', '0')])


def canal_grp(canal):
    return grp('Canal & commission', [ch('Canal', canal, saisie=True)])


ETATS_RESA = ['Brouillon', 'Confirmée', 'Arrivé', 'Parti']
# « Imprimer les fiches » (aite_guest_registry, anciennement « Fiches d'enregistrement ») et
# « Non présenté » (anciennement « No-show », écart n° 42).
ENTETE_CONFIRMEE = ('<div class="t02-bts">%s%s%s%s%s<span class="t02-etat">Confirmée</span></div>'
                    '<div class="t02-bts">%s</div>'
                    % (bt(None, 'Check-in', 'primaire'), bt(None, 'Encaisser un acompte'),
                       bt(None, 'Envoyer la confirmation'), bt(None, 'Imprimer les fiches', ico=IMPRIMER_I),
                       bt(None, 'Non présenté'), bt(None, 'Annuler')))

# Rodrigue Tamba : réservé au téléphone par la Réservation rapide (une nuit en 201, canal
# « Téléphone / WhatsApp »), confirmé d'emblée, folio ouvert ; il rappelle : une nuit de plus
# (10:12), puis la 203 (10:14). Message de création : « Réservation créée » (écart n° 43 corrigé).
SUIVI = ('<div class="t02-suivi"><b class="anc">20/10/2026 12:00:00</b><span class="sep">→</span>'
         '<b class="nouv">21/10/2026 12:00:00</b> <i>(Départ)</i></div>')
CREE = 'Réservation créée'
CREE_R = message(NOM, "Aujourd'hui à 10:06", CREE)
FIL_R0 = separateur("Aujourd'hui") + CREE_R
FIL_R1 = separateur("Aujourd'hui") + message(NOM, "Aujourd'hui à 10:12", SUIVI, 't02-r-m1') + CREE_R
FIL_R2 = (separateur("Aujourd'hui")
          + message(NOM, "Aujourd'hui à 10:14", 'Changement de chambre : 201 [CFT] → 203 [CFT].', 't02-r-m2')
          + message(NOM, "Aujourd'hui à 10:12", SUIVI) + CREE_R)
CANAL_R = 'Téléphone / WhatsApp'
DEPART_R = ('<span class="t02-champ" id="t02-r-dep"><span class="ph" id="t02-r-dep-ph"></span>'
            '<span class="val" id="t02-r-dep-val">20/10/2026 12:00:00</span></span>')
RODRIGUE_FICHE = fiche(
    't02-rodrigue', 'Planning des chambres', 'RES/2026/0221', ENTETE_CONFIRMEE,
    stat('t02-r-folio', 'document', 'Folio', FOLIO_AVANT) + stat(None, 'fiche', "Fiches d'enregistrement", '0/2'),
    client_grp('Rodrigue Tamba', '+237 6 00 00 00 21', 'rodrigue.tamba@exemple.cm'),
    grp('Séjour', [ch('Arrivée', '19/10/2026 14:00:00', saisie=True), ch('Départ', DEPART_R, saisie=True, html=True),
                   ch('Nuits', '1', 't02-r-nuits', aide=True), ch('Total hébergement (HT)', TOTAL_AVANT, 't02-r-tot')]),
    canal_grp(CANAL_R), occupation_grp(),
    ligne_chambre('t02-r-l', 'Confort', '201 [CFT]', '1', PRIX_CFT, TOTAL_AVANT),
    discussion([FIL_R0, FIL_R1, FIL_R2], 't02-r-fil'), enregistrer=True)

# Jacques Owona : saisi à la main sur la 204, aux dates du séjour d'Estelle — refusé à la confirmation.
JACQUES = fiche(
    't02-jacques', 'Réservations', 'RES/2026/0222',
    '<div class="t02-bts">%s%s<span class="t02-sb">%s</span></div>'
    % (bt('t02-j-confirmer', 'Confirmer', 'primaire'), bt(None, 'Annuler'),
       ''.join('<span class="t02-sb-e%s">%s</span>' % (' actif' if i == 0 else '', x) for i, x in enumerate(ETATS_RESA))),
    '',
    client_grp('Jacques Owona', '+237 6 00 00 00 22', 'jacques.owona@exemple.cm', brouillon=True),
    grp('Séjour', [ch('Arrivée', '15/10/2026 14:00:00', 't02-j-arr', saisie=True),
                   ch('Départ', '17/10/2026 12:00:00', 't02-j-dep', saisie=True),
                   ch('Nuits', '2', aide=True), ch('Total hébergement (HT)', TOTAL_APRES)]),
    canal_grp('Direct / comptoir'), occupation_grp(),
    ligne_chambre('t02-j-l', 'Confort', demo.CHAMBRE, '2', PRIX_CFT, TOTAL_APRES, echange=False),
    discussion([separateur("Aujourd'hui") + message(NOM, "Aujourd'hui à 10:09", CREE)],
               't02-j-fil'))


# ------------------------------------------------------------ les calques --

def deroulant(ident, gauche, items):
    return ('<div class="t02-dd masque" id="%s" style="left:%dpx" data-layout-allow-overlap data-layout-allow-occlusion>%s'
            '</div>' % (ident, gauche, ''.join('<div class="t02-dd-i"%s>%s</div>' % (_id(i), e(t)) for i, t in items)))


# Positions relevées sur la barre du haut rendue : 10 px à gauche du texte des menus « Réception »
# (x = 158) et « Réservations » (x = 279, plus à gauche qu'avec « Front Desk »), hotel_menus.xml:21-66.
DD_RECEP = deroulant('t02-dd-recep', 148, [(None, 'Tableau de bord'), ('t02-dd-rapide', 'Réservation rapide'),
                                           (None, 'Arrivées du jour'), (None, 'Départs du jour'),
                                           (None, 'Clients présents')])
DD_RESA = deroulant('t02-dd-resa', 269, [(None, 'Réservations'), ('t02-dd-planning', 'Planning des chambres')])


def modale(ident, titre, corps, pied, haut, largeur, titre_id=None, agrandir=True):
    return ('<div class="voile masque" id="%s-voile" data-layout-allow-overlap data-layout-allow-occlusion></div>'
            '<div class="modale masque t02-modale" id="%s" style="top:%dpx;width:%dpx;margin-left:-%dpx" '
            'data-layout-allow-overlap data-layout-allow-occlusion>'
            '<div class="m-tete"><span%s>%s</span><span class="t02-m-ic">%s'
            '<span class="m-x">%s</span></span></div><div class="m-corps">%s</div><div class="m-pied">%s</div></div>'
            % (ident, ident, haut, largeur, largeur // 2, _id(titre_id), e(titre),
               '<span class="t02-agr">⤢</span>' if agrandir else '', ICONES['x'], corps, pied))


def mch(libelle, valeur_html, aide=False, ident=None):
    return ('<div class="m-ch"%s><span class="l">%s%s</span><span class="v">%s</span></div>'
            % (_id(ident), e(libelle), '<sup class="t02-aide">?</sup>' if aide else '', valeur_html))


def m2o(ident, ph='', valeur=''):
    return '<span class="t02-m2o">%s<span class="t02-car">▾</span></span>' % entree(ident, ph, valeur)


def toggle(ident, actif=False):
    return '<span class="toggle%s" id="%s"><i></i></span>' % (' on' if actif else '', ident)


def case(ident, coche=True):
    return '<span class="case%s"%s><i></i></span>' % (' coche' if coche else '', _id(ident))


GAB_RR = '96px 130px 110px 130px 125px 60px 140px 170px'
# Les Confort libres du 19 au 20/10 pour deux adultes : la 204 est à Joël Kamga du 18 au 20/10.
LIBRES = [('201', '1er étage'), ('202', '1er étage'), ('203', '1er étage'), ('205', '1er étage'), ('206', '1er étage')]
RESULTATS = (
    '<div class="masque" id="t02-rr-res"><div class="t02-rr-table"><div class="t02-rr-tete" style="grid-template-columns:%s">'
    '<span>Réserver</span><span>Chambre</span><span>Type</span><span>Étage</span><span class="d">Cap. adultes</span>'
    '<span class="d">Nuits</span><span class="d">Prix / nuit</span><span class="d">Total séjour (HT)</span></div>%s</div>'
    '<div class="m-grille t02-rr-client"><div>%s</div><div>%s</div></div></div>'
    % (GAB_RR, ''.join('<div class="t02-rr-ligne" id="t02-rr-%s" style="grid-template-columns:%s"><span>%s</span>'
                       '<span>%s [CFT]</span><span>Confort</span><span>%s</span><span class="d">2</span>'
                       '<span class="d">1</span><span class="d">%s</span><span class="d">%s</span></div>'
                       % (n, GAB_RR, toggle('t02-rr-t' + n), n, et, PRIX_CFT, PRIX_CFT) for n, et in LIBRES),
       mch('Client', m2o('t02-rr-client')) + mch('Canal', m2o('t02-rr-canal', '', 'Direct / comptoir'), aide=True),
       mch('Confirmer immédiatement', case(None), aide=True)))
RAPIDE = modale('t02-rr', 'Réservation rapide', (
    '<div class="m-grille"><div>%s%s%s</div><div>%s%s%s</div></div>'
    '<div class="t02-rr-bt"><span class="bt gris" id="t02-rr-chercher">%sRechercher les chambres disponibles</span>'
    '</div>%s'
    % (mch('Hôtel', m2o('t02-rr-hotel', '', demo.HOTEL)), mch('Arrivée', entree('t02-rr-arr', '', '14/10/2026 14:00:00')),
       mch('Départ', entree('t02-rr-dep', '', '15/10/2026 12:00:00')),
       mch('Type de chambre', m2o('t02-rr-type'), aide=True), mch('Adultes', entree('t02-rr-ad', '', '1')),
       mch('Enfants', entree('t02-rr-enf', '', '0')), icone('loupe', 't02-bi'), RESULTATS)),
    '<span class="bt primaire masque t02-rr-reserver" id="t02-rr-reserver">Réserver</span>'
    '<span class="bt gris t02-rr-fermer" id="t02-rr-fermer">Fermer</span>', 44, 1180, 't02-rr-titre')

# Le refus de Jacques Owona (15/10 14:00 → 17/10 12:00 sur la 204) : dates à l'heure de l'utilisateur, au
# format français, sans les secondes (_fmt_local_datetime, hotel_reservation.py:197-200 et :350-360 ;
# écart n° 37 corrigé).
REFUS = ("La chambre %s n'est pas disponible du %s au %s (déjà réservée ou hors service)."
         % (demo.CHAMBRE, '15/10/2026 14:00', '17/10/2026 12:00'))
ERREUR = modale('t02-err', 'Opération invalide', (
    '<p class="t02-err-p" id="t02-err-p">%s</p>' % e(REFUS)),
    '<span class="bt primaire" id="t02-err-ok">Fermer</span>', 260, 1120, agrandir=False)

# De la 201 à la 203, deux Confort au même tarif : la case « Conserver le prix actuel » reste
# décochée, le bandeau du surclassement gracieux (invisible="not keep_price") ne s'affiche pas.
CHANGER = modale('t02-cc', 'Changer de chambre', (
    '<div class="m-grille"><div><div class="t02-grp-t">Séjour</div>%s%s%s%s</div>'
    '<div id="t02-cc-nouv"><div class="t02-grp-t">Nouvelle chambre</div>%s%s%s%s</div></div>'
    % (mch('Client', '<span class="t02-lien">Rodrigue Tamba</span>'),
       mch('Chambre actuelle', '<span class="t02-lien">201 [CFT]</span>'), mch('Arrivée', '19/10/2026 14:00:00'),
       mch('Départ', '21/10/2026 12:00:00'), mch('Nouvelle chambre', m2o('t02-cc-nc')),
       mch('Conserver le prix actuel', case('t02-cc-garder', coche=False), aide=True, ident='t02-cc-garder-l'),
       mch('Prix actuel / nuit', e(PRIX_CFT), aide=True),
       mch('Nouveau prix / nuit', '<span id="t02-cc-prix">%s</span>' % e(PRIX_CFT), aide=True))),
    '<span class="bt primaire" id="t02-cc-ok">Changer la chambre</span><span class="bt gris">Annuler</span>', 120, 1180)

ECRAN = navigateur(fenetre_muk(APP, 'Hôtel', MENUS, [LISTE, PLANNING, RODRIGUE_FICHE, JACQUES],
                               societe=demo.SOCIETE, initiale=NOM[0], avatar='#185FA5',
                               apps=APPS_PROFIL['reception'], app_active='Hôtel',
                               calques=DD_RECEP + DD_RESA + RAPIDE + ERREUR + CHANGER))

CSS = """
.t02-pl { position: absolute; inset: 0; background: #fff; color: #212529; }
.t02-cp { position: absolute; left: 0; right: 0; top: 0; height: 72px; display: flex; align-items: center; gap: 14px;
  padding: 0 20px; background: #fff; border-bottom: 1px solid #DEE2E6; }
.t02-titre { font-size: 24px; color: #212529; white-space: nowrap; display: inline-flex; align-items: center; gap: 10px; }
.t02-rouage { width: 18px; height: 18px; display: inline-flex; }
.t02-rouage svg { width: 18px; height: 18px; }
.t02 .t02-rech, .t02-rech { position: absolute; left: 520px; width: 520px; height: 46px; margin-left: 0; }
.t02-pager { position: absolute; right: 200px; font-size: 19px; color: #495057; }
.t02-vues { position: absolute; right: 20px; display: flex; }
.t02-vues span { width: 50px; height: 42px; display: inline-flex; align-items: center; justify-content: center;
  background: #E9ECEF; color: #343A40; font-size: 20px; }
.t02-vues span.actif { background: #CFDCE5; box-shadow: inset 0 0 0 1px #4A7892; }
.t02-vues svg { width: 22px; height: 22px; }
.t02-barre { position: absolute; left: 0; right: 0; top: 72px; height: 54px; display: flex; align-items: center; gap: 8px;
  padding: 0 20px; border-bottom: 1px solid #DEE2E6; }
.t02-barre .bt { height: 40px; font-size: 18px; }
.t02-fl { display: inline-flex; }
.t02-fl span { width: 44px; height: 42px; display: inline-flex; align-items: center; justify-content: center; background: #DEE2E6;
  font-size: 20px; color: #212529; }
.t02-barre .t02-fl span { height: 40px; }
.t02-fl span + span { border-left: 1px solid #fff; }
.t02-mois { margin-left: 10px; font-size: 21px; font-weight: 500; }
.t02-panneau-i { margin-left: auto; width: 26px; height: 26px; color: #343A40; display: inline-flex; }
.t02-cal { position: absolute; left: 0; top: 126px; width: 1268px; bottom: 0; border-right: 1px solid #DEE2E6; }
.t02-jours { height: 28px; display: grid; grid-template-columns: repeat(7, 1fr); align-items: center; text-align: center;
  font-size: 15px; color: #495057; border-bottom: 1px solid #DEE2E6; }
.t02-grille { position: absolute; left: 0; right: 0; top: 28px; bottom: 0; display: grid;
  grid-template-columns: repeat(7, 1fr); }
.t02-case { position: relative; border-right: 1px solid #E9ECEF; border-bottom: 1px solid #E9ECEF; text-align: center;
  padding-top: 1px; }
.t02-num { font-size: 16px; color: #343A40; line-height: 22px; }
.t02-case.hors .t02-num { color: #ADB5BD; }
.t02-auj { display: inline-flex; width: 22px; height: 22px; border-radius: 50%; background: #DC3545; color: #fff;
  align-items: center; justify-content: center; font-weight: 600; font-size: 14px; vertical-align: top; }
.t02-sem { position: absolute; left: 4px; top: 3px; padding: 0 5px; border-radius: 3px; background: #E9ECEF; font-size: 12px;
  color: #6C757D; }
.t02-evs { position: absolute; inset: 0; }
.t02-ev { position: absolute; height: 17px; border: 1px solid; border-radius: 3px; padding: 0 6px; font-size: 13.5px;
  line-height: 15px; color: #212529; overflow: hidden; }
.t02-ev.suite { border-left-width: 0; border-top-left-radius: 0; border-bottom-left-radius: 0; }
.t02-ev.coupe { border-right-width: 0; border-top-right-radius: 0; border-bottom-right-radius: 0; }
.t02-ev.passe::after { content: ''; position: absolute; inset: 0; background: rgba(255,255,255,.5); }
.t02-ev > span { display: block; }
.t02-panneau { position: absolute; right: 0; top: 126px; width: 276px; bottom: 0; padding: 12px 16px; overflow: hidden; }
.t02-mini-t { display: flex; justify-content: space-between; align-items: center; font-size: 18px; color: #343A40; height: 30px; }
.t02-mini-t b { font-weight: 500; }
.t02-mini-g { margin-top: 6px; display: grid; grid-template-columns: repeat(7, 1fr); row-gap: 2px; text-align: center;
  font-size: 14px; color: #343A40; }
.t02-mini-g span { height: 22px; line-height: 22px; }
.t02-mini-g span:nth-child(-n+7) { font-weight: 600; color: #212529; }
.t02-mini-g .auj { border-radius: 50%; box-shadow: inset 0 0 0 2px #4A7892; font-weight: 600; }
.t02-filtres { margin-top: 10px; }
.t02-filtre { display: flex; align-items: center; gap: 10px; height: 20px; font-size: 15px; color: #343A40; }
.t02-filtre i { width: 15px; height: 15px; border-radius: 3px; border: 1px solid; flex: none; }
.t02-filtre.tete { height: 28px; font-size: 17px; }
.t02-filtre.tete i { background: #4A7892; border-color: #4A7892; }
.t02-pop { position: absolute; left: 916px; top: 284px; width: 436px; background: #fff; border-radius: 6px; z-index: 6;
  box-shadow: 0 10px 34px rgba(0,0,0,.28); border: 1px solid #DEE2E6; overflow: hidden; }
.t02-pop-t { height: 54px; display: flex; align-items: center; justify-content: space-between; padding: 0 16px 0 18px;
  font-size: 19px; font-weight: 500; color: #212529; }
.t02-pop-x { width: 20px; height: 20px; display: inline-flex; color: #343A40; }
.t02-pop-c { padding: 14px 18px 6px; border-bottom: 1px solid #DEE2E6; }
.t02-pop-ch { display: flex; gap: 10px; align-items: baseline; height: 36px; font-size: 17px; color: #212529; }
.t02-pop-ch > span { font-weight: 500; }
.t02-pop-ch b { font-weight: 400; color: #3F6A83; }
.t02-pop-ch i { font-style: normal; }
.t02-pop-p { display: flex; gap: 8px; padding: 14px 18px; }
.t02-pop-p .bt { height: 40px; font-size: 17px; }
.t02-l { position: absolute; left: 0; right: 0; top: 72px; bottom: 0; }
.t02-l-tete, .t02-l-ligne, .t02-l-total { display: grid; align-items: center; column-gap: 12px; padding: 0 14px 0 6px; }
.t02-l-tete { height: 44px; font-size: 17px; font-weight: 600; border-bottom: 1px solid #DEE2E6; white-space: nowrap; }
.t02-l-ligne { height: 44px; font-size: 17px; border-bottom: 1px solid #EEF0F2; color: #0E7490; white-space: nowrap; }
.t02-l-total { height: 44px; font-size: 17px; font-weight: 700; }
.t02-l .cb { width: 17px; height: 17px; border: 1px solid #ADB5BD; border-radius: 3px; margin-left: 10px; }
.t02-l .puce { height: 26px; font-size: 15px; }
.t02-opt { color: #495057; font-size: 18px; text-align: right; }
.t02-rech .facette { height: 32px; font-size: 17px; }
.t02-rech .facette .fic svg { width: 16px; height: 16px; }
.t02-f { position: absolute; inset: 0; background: #F8F9FA; color: #212529; }
.t02-f-cp { position: absolute; left: 0; right: 0; top: 0; height: 72px; display: flex; align-items: center; gap: 14px;
  padding: 0 20px; background: #fff; border-bottom: 1px solid #DEE2E6; }
.t02-f-cp .bt { height: 42px; font-size: 18px; }
.t02-fil { display: flex; flex-direction: column; line-height: 1.2; }
.t02-parent { font-size: 16px; color: #3F6A83; }
.t02-ref { font-size: 20px; display: inline-flex; align-items: center; gap: 8px; }
.t02-save { display: inline-flex; gap: 6px; margin-left: 4px; }
.t02-si { width: 22px; height: 22px; display: inline-flex; color: #4A7892; }
.t02-si:last-child { color: #6C757D; }
.t02-stats { margin-left: 140px; display: flex; }
.t02-stat { display: flex; align-items: center; gap: 10px; height: 54px; padding: 0 16px; border: 1px solid #DEE2E6;
  background: #fff; }
.t02-stat + .t02-stat { border-left: 0; }
.t02-sic { width: 26px; height: 26px; display: inline-flex; color: #495057; }
.t02-stat .t { display: flex; flex-direction: column; line-height: 1.15; font-size: 16px; color: #495057; }
.t02-stat .t b { font-weight: 600; color: #3F6A83; }
.t02-f-g { position: absolute; left: 0; top: 72px; width: 1064px; bottom: 0; }
.t02-hd { padding: 10px 0 0 20px; }
.t02-bts { position: relative; display: flex; gap: 7px; margin-bottom: 7px; height: 42px; }
.t02-bts .bt { height: 42px; font-size: 17px; padding: 0 12px; }
.t02-bi { width: 17px; height: 17px; display: inline-flex; }
.t02-bi svg { width: 17px; height: 17px; }
.t02-etat { position: absolute; right: 0; height: 42px; padding: 0 14px; display: inline-flex; align-items: center;
  font-size: 17px; color: #495057; background: #E9ECEF; border-radius: 4px; }
.t02-sb { position: absolute; right: 0; display: flex; }
.t02-sb-e { height: 42px; padding: 0 20px 0 26px; display: flex; align-items: center; font-size: 17px; color: #495057;
  background: #E9ECEF; clip-path: polygon(0 0, calc(100% - 12px) 0, 100% 50%, calc(100% - 12px) 100%, 0 100%, 12px 50%); }
.t02-sb-e:first-child { padding-left: 16px; clip-path: polygon(0 0, calc(100% - 12px) 0, 100% 50%, calc(100% - 12px) 100%, 0 100%); }
.t02-sb-e.actif { background: #DCE6EC; color: #212529; font-weight: 600; }
.t02-feuille { position: absolute; left: 20px; right: 0; top: 108px; bottom: 0; background: #fff; border: 1px solid #DEE2E6;
  border-bottom: 0; overflow: hidden; }
#t02-jacques .t02-feuille { top: 60px; }
.t02-defil { position: absolute; left: 0; right: 0; top: 0; padding: 16px 24px 6px; }
.t02-f-titre { font-size: 32px; font-weight: 500; margin-bottom: 10px; }
.t02-cols { display: grid; grid-template-columns: 1fr 1fr; column-gap: 36px; }
.t02-grp { margin-bottom: 10px; }
.t02-grp-t { font-size: 15px; font-weight: 700; text-transform: uppercase; letter-spacing: .02em; color: #212529;
  padding-bottom: 6px; border-bottom: 1px solid #DEE2E6; margin-bottom: 6px; }
.t02-ch { display: grid; grid-template-columns: 200px 1fr; align-items: center; min-height: 32px; font-size: 17px; }
.t02-ch .l { color: #495057; white-space: nowrap; }
.t02-ch .l.gras { color: #212529; font-weight: 600; }
.t02-ch .v { color: #212529; white-space: nowrap; }
.t02-ch .v.saisie { border-bottom: 1px solid #DEE2E6; }
.t02-ch .v.lien { color: #3F6A83; }
.t02-aide { margin-left: 3px; color: #4A7892; font-size: 12px; font-weight: 700; }
.t02-champ { position: relative; display: block; height: 26px; }
.t02-champ.focus { box-shadow: 0 2px 0 #4A7892; }
.t02-champ .ph, .t02-champ .val { position: absolute; left: 0; top: 0; line-height: 26px; }
.t02-onglets { display: flex; margin: 6px -24px 0; padding: 0 24px; border-bottom: 1px solid #DEE2E6; }
.t02-onglets span { padding: 9px 16px; font-size: 17px; color: #3F6A83; }
.t02-onglets span.actif { color: #212529; border: 1px solid #DEE2E6; border-bottom-color: #fff; margin-bottom: -1px;
  border-radius: 6px 6px 0 0; }
.t02-table { margin: 0 -24px; }
.t02-t-tete, .t02-t-ligne { display: grid; align-items: center; column-gap: 8px; padding: 0 24px; white-space: nowrap; }
.t02-t-tete { height: 42px; font-size: 16px; font-weight: 600; border-bottom: 1px solid #DEE2E6; }
.t02-t-ligne { height: 44px; font-size: 16px; border-bottom: 1px solid #EEF0F2; }
.t02-t-ajout { height: 40px; display: flex; align-items: center; padding: 0 24px; font-size: 16px; color: #3F6A83; }
.t02-ech { color: #3F6A83; font-size: 20px; text-align: center; }
.t02-ci { width: 16px; height: 16px; display: inline-flex; color: #343A40; }
.t02-chatter { position: absolute; left: 1080px; right: 0; top: 72px; bottom: 0; padding: 12px 16px; background: #fff;
  border-left: 1px solid #DEE2E6; }
.t02-ch-bts { display: flex; gap: 6px; align-items: center; }
.t02-ch-bts .bt { height: 40px; font-size: 16px; padding: 0 11px; gap: 7px; }
.t02-ch-ic { margin-left: auto; width: 20px; height: 20px; display: inline-flex; }
.t02-ch-fil { position: relative; margin-top: 8px; }
.t02-ch-etat { position: absolute; left: 0; right: 0; top: 0; }
.t02-sep { display: flex; align-items: center; gap: 12px; margin: 10px 0 4px; font-size: 13px; color: #6C757D; }
.t02-sep::before, .t02-sep::after { content: ''; flex: 1; height: 1px; background: #DEE2E6; }
.t02-msg { display: flex; gap: 12px; padding: 8px 0; }
.t02-av { width: 36px; height: 36px; border-radius: 6px; background: #185FA5; color: #fff; display: flex; align-items: center;
  justify-content: center; font-weight: 700; flex: none; }
.t02-msg-a { font-size: 15px; color: #212529; }
.t02-msg-a small { font-size: 13px; color: #6C757D; margin-left: 4px; }
.t02-msg-t { margin-top: 3px; font-size: 16px; line-height: 1.38; color: #212529; }
.t02-suivi { font-size: 15px; color: #212529; }
.t02-suivi .anc { color: #6C757D; }
.t02-suivi .sep { margin: 0 6px; color: #6C757D; }
.t02-suivi .nouv { color: #0E7490; }
.t02-suivi i { color: #6C757D; }
.t02-dd { position: absolute; top: 58px; z-index: 32; min-width: 270px; padding: 8px 0; background: #fff; border-radius: 4px;
  border: 1px solid #DEE2E6; box-shadow: 0 8px 20px rgba(0,0,0,.18); }
.t02-dd-i { height: 40px; display: flex; align-items: center; padding: 0 22px; font-size: 18px; color: #212529; white-space: nowrap; }
.t02-dd-i.survol { background: #E9ECEF; }
.t02-modale .m-tete { height: 66px; }
.t02-m-ic { display: inline-flex; gap: 18px; align-items: center; color: #495057; }
.t02-agr { font-size: 22px; }
.t02-modale .m-corps { padding: 18px 28px 16px; }
.t02-modale .m-ch { min-height: 44px; grid-template-columns: 230px 1fr; }
.t02-rr-client .m-ch { grid-template-columns: 250px 1fr; }
.t02-modale .m-ch .l { white-space: nowrap; }
.t02-modale .m-ch .v .entree { height: 40px; }
.t02-m2o { position: relative; display: block; }
.t02-car { position: absolute; right: 8px; top: 50%; transform: translateY(-50%); font-size: 14px; color: #495057; }
.t02-rr-bt { position: relative; margin-top: 10px; }
/* b-libres sur une ligne, entre « Enfants » et l'en-tête du tableau : elle ne cache plus rien. */
#b-libres { max-width: none; white-space: nowrap; padding-top: 11px; padding-bottom: 11px; }
.t02-rr-bt .bt { height: 42px; font-size: 18px; }
.t02-rr-table { margin-top: 18px; border-top: 1px solid #DEE2E6; }
.t02-rr-tete, .t02-rr-ligne { display: grid; align-items: center; column-gap: 10px; padding: 0 10px; white-space: nowrap; }
.t02-rr-tete { height: 44px; font-size: 17px; font-weight: 600; border-bottom: 1px solid #DEE2E6; }
.t02-rr-ligne { height: 42px; font-size: 17px; border-bottom: 1px solid #EEF0F2; }
.t02-rr-client { margin-top: 14px; }
.t02-modale .m-pied { position: relative; }
.t02-rr-reserver { position: absolute; left: 28px; }
.t02-rr-fermer.decale { margin-left: 118px; }
.t02-err-p { font-size: 20px; line-height: 1.5; color: #212529; margin: 6px 0 10px; }
.t02-lien { color: #3F6A83; }
.t02-modale .case { display: inline-flex; }
.t02-pf { display: flex; justify-content: center; }
.t02-pf .case i { width: 18px; height: 18px; }
"""

TUTORIEL = {
    'slug': 't02-planning',
    'profil': 't02_planning',
    'numero': 2,
    'titre': "Planning des chambres : tout l'hôtel d'un coup d'œil, une chambre prise refusée à la confirmation",
    'fonction': 'Planning des chambres',
    'personnage': (NOM, ROLE),
    'accroche': {
        'kicker': 'Le planning des chambres',
        'question': 'Cette chambre est-elle *vraiment* libre jeudi ?',
        'douleurs': [('alerte', 'La même chambre vendue deux fois'),
                     ('interrogation', 'Qui dort dans quelle chambre jeudi ?'),
                     ('calculatrice', 'Les nuits et le total comptés à la main'),
                     ('echange', 'Changement de chambre : la note ne suit pas'),
                     ('cadenas', "Le Gantt d'Odoo, réservé à Enterprise")],
        'voix': "Cette chambre est-elle vraiment libre jeudi ? Sans planinng, on la vend deux fois, et la note se perd "
                "quand le client change de chambre.",
    },
    'revelation': {
        'promesse': "Tout l'hôtel sur un planning, les chambres libres en un clic, la double réservation refusée à la "
                    "confirmation.",
        'voix': "Avec Aïte haousse, tout l'hôtel tient sur un planinng, et une chambre déjà réservée sur ces dates est "
                "refusée à la confirmation.",
    },
    'temps': ['Voir', 'Réserver', 'Protéger', 'Ajuster'],
    'app': APP,
    'ecran': ECRAN,
    'vues_initiales': {'odoo': 't02-liste'},
    'bulles': {
        'b-barre': 'Une barre par séjour : la chambre et le client, de l\'arrivée au départ.',
        'b-libres': 'Seules les chambres libres, avec le prix par nuit et le total.',
        'b-refus': 'La chambre et les dates en conflit sont nommées : la réservation reste en brouillon.',
        'b-suit': 'Nuits, total et folio recalculés dès l\'enregistrement.',
        'b-prix': 'Cochée, la nouvelle chambre garde le tarif de l\'ancienne, même si le séjour est prolongé : '
                  'un surclassement gracieux.',
    },
    'reactions': {
        'r-refus': 'La 204 reste à Estelle : la réservation en double est bloquée.',
        'r-suit': 'Une nuit de plus, une autre chambre : le planning a suivi.',
    },
    'etapes': [
        {'temps': 0, 'titre': 'Le planning des chambres',
         'texte': 'Réservations › Planning des chambres : le mois entier, une barre par séjour, une couleur par chambre.',
         'voix': "Mireille ouvre le planinng des chambres : tout le mois sur un écran, une barre par séjour, une couleur "
                 "par chambre. Un clic sur une barre, et le séjour s'affiche : arrivée, départ, chambre, cliente, "
                 "réservation, état.",
         'gestes': [clic(menu('Réservations'), d=0.6), montrer('#t02-dd-resa', d=0.25, y=-6),
                    clic('#t02-dd-planning', d=0.5), cacher('#t02-dd-resa', d=0.15), vue('t02-planning'),
                    curseur('#t02-b-estelle', fx=0.62, d=0.8), pause(0.4), anneau('#t02-planning .t02-auj', d=1.0),
                    clic('#t02-b-estelle', fx=0.4, d=0.4),
                    montrer('#t02-pop', d=0.3, y=8), zoom('#t02-pop', s=1.45, fx=0.05, d=0.8),
                    bulle('b-barre', '#t02-b-estelle', cote='bas', d=2.8), pause(3.0), cacher('#t02-pop', d=0.25),
                    dezoom(d=0.6)]},
        {'temps': 1, 'titre': 'Les chambres libres, avec leur prix',
         'texte': 'Réception › Réservation rapide : dates, type, adultes, et seules les chambres libres s\'affichent.',
         'voix': "Au téléphone, un client cherche une chambre Confort pour une nuit, lundi. Mireille "
                 "ouvre la réservation rapide : seules les chambres libres sur ces dates s'affichent, avec le prix par "
                 "nuit et le total du séjour.",
         'gestes': [clic(menu('Réception'), d=0.6), montrer('#t02-dd-recep', d=0.25, y=-6),
                    clic('#t02-dd-rapide', d=0.5), cacher('#t02-dd-recep', d=0.15), ouvrir('t02-rr'),
                    saisir('t02-rr-arr', '19/10/2026 14:00:00', d=0.7), curseur('#t02-rr-arr', fx=0.92, d=0.4, avec=True),
                    saisir('t02-rr-dep', '20/10/2026 12:00:00', d=0.7), curseur('#t02-rr-dep', fx=0.92, d=0.4, avec=True),
                    choisir('t02-rr-type', 'Confort'), curseur('#t02-rr-type', fx=0.6, d=0.4, avec=True),
                    saisir('t02-rr-ad', '2', d=0.2), curseur('#t02-rr-ad', fx=0.4, d=0.3, avec=True),
                    clic('#t02-rr-chercher', d=0.6),
                    montrer('#t02-rr-res', d=0.35, y=10), montrer('#t02-rr-reserver', d=0.2, y=0, avec=True),
                    classe('#t02-rr-fermer', ajouter=['decale'], avec=True),
                    zoom('#t02-rr-res .t02-rr-table', s=1.3, fy=0.4, d=0.7),
                    bulle('b-libres', '#t02-rr-chercher', cote='droite', d=2.6), pause(2.4)]},
        {'temps': 1, 'titre': 'Réservé, et déjà au planning',
         'texte': 'Une chambre cochée, le client, le canal, Réserver : la réservation est confirmée, son folio ouvert.',
         'voix': "Mireille coche la deux cent un, choisit le client et le canal, téléphone, puis réserve. La "
                 "réservation est aussitôt confirmée, son folio ouvert, et le séjour apparaît déjà au planinng, sur sa "
                 "chambre.",
         'gestes': [clic('#t02-rr-t201', d=0.6), classe('#t02-rr-t201', ajouter=['on']), dezoom(d=0.5, avec=True),
                    saisir('t02-rr-client', 'Rodrigue Tamba', d=0.6), curseur('#t02-rr-canal', fx=0.6, d=0.4),
                    choisir('t02-rr-canal', CANAL_R), clic('#t02-rr-reserver', d=0.6),
                    fermer('t02-rr'), vue('t02-rodrigue'), pause(0.5), anneau('#t02-rodrigue .t02-etat', d=1.0),
                    anneau('#t02-r-folio', d=1.0), clic('#t02-rodrigue .t02-parent', d=0.6), vue('t02-planning'),
                    montrer('#t02-b-rodrigue', d=0.4, y=0), anneau('#t02-b-rodrigue', d=1.4)]},
        {'temps': 2, 'titre': 'La double réservation refusée',
         'texte': 'La 204 saisie à la main sur des dates déjà prises : la confirmation est refusée.',
         'voix': "Et si on saisit à la main la deux cent quatre, déjà prise ces jours-là ? À la confirmation, "
                 "Aïte haousse refuse net, en nommant la chambre et les dates en conflit : la réservation reste "
                 "simplement en brouillon.",
         'gestes': [vue('t02-jacques'), pause(0.4), anneau('#t02-j-l-ch', d=0.9), anneau('#t02-j-arr', d=0.8),
                    clic('#t02-j-confirmer', d=0.6), ouvrir('t02-err'), zoom('#t02-err-p', s=1.4, d=0.7),
                    bulle('b-refus', '#t02-err-p', cote='bas', d=2.6), pause(1.6), reaction('r-refus', d=2.6),
                    pause(1.0), dezoom(d=0.5), clic('#t02-err-ok', d=0.5), fermer('t02-err')]},
        {'temps': 3, 'titre': 'Une nuit de plus : tout suit',
         'texte': 'La date de départ repoussée : nuits, total et folio recalculés, la modification tracée.',
         'voix': "Quelques minutes plus tard, Rodrigue rappelle : il reste une nuit de plus. Mireille repousse la date "
                 "de départ : les nuits, le total et le folio se recalculent, et la modification est tracée sur la "
                 "réservation.",
         'gestes': [vue('t02-rodrigue'), pause(0.3), clic('#t02-r-dep', fx=0.3, d=0.6),
                    saisir('t02-r-dep', '21/10/2026 12:00:00', d=0.8), montrer('#t02-rodrigue-save', d=0.2, y=0),
                    texte('#t02-r-nuits', '2', decale=0.2), texte('#t02-r-tot', TOTAL_APRES),
                    texte('#t02-r-l-n', '2'), texte('#t02-r-l-st', TOTAL_APRES), anneau('#t02-r-tot', d=1.0),
                    clic('#t02-rodrigue-save-ok', d=0.6), cacher('#t02-rodrigue-save', d=0.2),
                    texte('#t02-r-folio-v', FOLIO_RODRIGUE), cacher('#t02-r-fil-0', d=0.2),
                    montrer('#t02-r-fil-1', d=0.35, y=-10), bulle('b-suit', '#t02-r-folio', cote='bas', d=2.6),
                    anneau('#t02-r-folio', d=1.2), anneau('#t02-r-m1', d=1.4)]},
        {'temps': 3, 'titre': 'Changer de chambre, sans rien perdre',
         'texte': "L'assistant contrôle la nouvelle chambre et peut garder le tarif ; le changement est noté, le folio suit.",
         'voix': "Il préfère aussi la deux cent trois. Mireille ouvre l'assistant Changer de chambre : il vérifie que "
                 "la chambre est libre, et pourrait même garder l'ancien tarif. Le changement s'inscrit aussitôt sur "
                 "la réservation, et le folio suit le client.",
         'gestes': [clic('#t02-r-l-ech', d=0.6), ouvrir('t02-cc'), choisir('t02-cc-nc', '203 [CFT]'),
                    curseur('#t02-cc-garder', d=0.5), zoom('#t02-cc-nouv', s=1.3, fy=0.4, d=0.6),
                    anneau('#t02-cc-prix', d=1.0), bulle('b-prix', '#t02-cc-prix', cote='bas', d=2.6), pause(1.8),
                    dezoom(d=0.5), clic('#t02-cc-ok', d=0.4), fermer('t02-cc'), texte('#t02-r-l-ch', '203 [CFT]'),
                    cacher('#t02-r-fil-1', d=0.2), montrer('#t02-r-fil-2', d=0.35, y=-10), anneau('#t02-r-l-ch', d=1.0),
                    anneau('#t02-r-m2', d=1.4)]},
        {'temps': 3, 'titre': 'Le planning a suivi',
         'texte': 'Retour au planning : la barre est passée sur la 203, une nuit de plus.',
         'voix': "Retour au planinng : la barre a suivi. Rodrigue occupera la deux cent trois, du lundi au "
                 "mercredi.",
         'gestes': [clic('#t02-rodrigue .t02-parent', d=0.6), vue('t02-planning'), pause(0.3),
                    cacher('#t02-b-rodrigue', d=0.3), montrer('#t02-b-rodrigue2', d=0.4, y=0),
                    anneau('#t02-b-rodrigue2', d=1.4), reaction('r-suit', d=2.8), pause(2.2)]},
    ],
    'resultats': {
        'titre': "Le planning qui tient l'hôtel à jour",
        'cartes': [
            {'valeur': '49', 'compter': 49, 'unite': 'tests', 'icone': 'bouclier',
             'texte': 'automatisés : disponibilité, réservation rapide, planning, prolongation, changement de chambre'},
            {'valeur': '1', 'compter': 1, 'unite': 'clic', 'icone': 'eclair',
             'texte': 'pour lister les chambres libres, avec le prix par nuit et le total du séjour'},
            {'valeur': '2', 'compter': 2, 'unite': 'éditions', 'icone': 'coche',
             'texte': "d'Odoo : le même menu Planning des chambres, sur Community comme sur Enterprise"},
        ],
        'voix': "Quarante-neuf tests automatisés, un clic pour trouver une chambre libre, et un planinng qui s'ouvre sur "
                "les deux éditions d'Odoo.",
    },
    'cta': {
        'appel': 'Demandez votre démonstration',
        'suivant': 'Un séjour, une note, une facture',
        'voix': "Aïte haousse, par Aïte Consulting. Demandez votre démonstration. Prochain tutoriel : un séjour, une "
                "note, une facture.",
    },
    'vignette': {'etape': 1, 'apres': 5.9},
    'css': CSS,
}
