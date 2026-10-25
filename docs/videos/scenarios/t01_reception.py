# -*- coding: utf-8 -*-
"""Tutoriel 1 — La réception AITE HOUSE : de la réservation à la facture.

Le parcours d'un séjour à la réception, dans l'ordre réel d'usage : le
tableau de bord de la réception, la réservation rapide (chambres libres
seulement), l'acompte Mobile Money tracé sur le folio, le check-in, le folio
du séjour (nuitées, taxe de séjour, prestations), le check-out et la
facture. Personnage : la réceptionniste (demo.POSTES['reception']), au seul
profil Réception, sans le droit Facturation d'Odoo : depuis
aite_hotel_management 18.0.1.0.4, la facture du départ est créée, validée et
lettrée en sudo() (voir écarts). Barre MuK : celle du profil Réception
(ecrans.APPS_PROFIL['reception']), sans l'application Facturation ; menus de
l'application Hôtel : ecrans.MENUS_MUK['hotel_reception']. Données fictives :
demo.py (Estelle Ngono, RES/2026/0214, FOL/2026/0214, chambre 204 [CFT],
45 000 FCFA la nuit) ; types, étages et prix des autres chambres composés
pour la démonstration (Standard 35 000, Confort 45 000, Suite Junior 75 000,
Suite VIP 120 000). Téléphone de la cliente : demo.CLIENT_TEL, dans la plage
de fiction « +237 6 00 00 00 xx » de la série ; référence MoMo numérique,
comme les identifiants de transaction MTN. La société de démonstration est
paramétrée sans TVA (articles de nuitée et de service sans taxe de vente) :
« Taxes 0 FCFA » et Total TTC = Total HT. Une société assujettie verrait la
TVA de 19,25 % (benchmark_afrique_odoo.md:14) sur les nuitées et le
petit-déjeuner ; la taxe de séjour, elle, n'en porte jamais
(aite_city_tax/models/hotel_folio.py:119-166). Formats : ecrans.fcfa (champs
d'Odoo, espace insécable ; tableaux de bord, espace fine avec tdb=True),
ecrans.pct, ecrans.compte et la variation de ecrans.kpi, tels que le produit
les écrit depuis la livraison 4.

Base mono-société, comme celle du client (DESIGN.md, « La base est
mono-société » ; odoo18/odoo/addons/base/models/res_users.py:1907-1914) :
aucun élément réservé à groups="base.group_multi_company" n'est affiché, ni
« Hôtel » dans les arrivées du jour, ni au folio (ref_muk/306).

Sources des libellés (addons/, livraison 4, vérifiés mot pour mot par
grep -rF ; `git diff ae3aab6..HEAD` pour ce qui a changé) :

- Menus : aite_hotel_management/views/hotel_menus.xml:18-50 (Hôtel,
  Réception — anciennement « Front Desk », ECARTS n° 42 —, Tableau de bord,
  Réservation rapide, Arrivées du jour, Départs du jour, Clients présents) ;
  aite_guest_registry/views/menus.xml:4-8 (Registre des clients, séquence
  45). Menus du profil Réception : capture MuK
  ref_muk/306-reception-reservations.png.
- Tableau de bord de la réception : action « Tableau de bord — Réception »
  (views/hotel_dashboard_actions.xml:4-7 ; son nom est celui du fil
  d'Ariane de la réservation créée depuis le bouton) ;
  static/src/xml/hotel_dashboard.xml:28-126 (titre « Tableau de bord —
  Réception », sous-titre « Occupation, arrivées & départs, plan des
  chambres · », « Nouvelle réservation », Période et ses quatre puces, les
  deux dates « → » et « Appliquer » (:45-60 ; période « Ce mois » = du 1er
  du mois à aujourd'hui, js/services/hotel_utils.js:119-144), Photo du
  jour, Performance de la période, les huit cartes et leurs sous-titres :
  « 13 chambres occupées sur 20 », « chambres à libérer aujourd'hui »,
  « 13 séjours en cours », « Prix moyen par nuit (ADR) » / « CA hébergement
  ÷ nuitées vendues », « Revenu par chambre disponible (RevPAR) » / « par
  chambre disponible, vendue ou non », les deux graphiques) ;
  js/services/hotel_utils.js:46-115 (fmtMoney, fmtPct « 65,0 % » à une
  décimale fixe, fmtDelta « ▲ +7,3 % », fmtInt, fmtCount : accord sans
  « (s) ») ; js/views/hotel_dashboard_view.js:155-202 (count, occupiedSub,
  deltaOf : « vs période précédente », la variation comparant à la période
  précédente de même durée, hotel_dashboard.py:376-384, ECARTS n° 62).
  Chiffres de l'hôtel de la série (20 chambres, fiche d'harmonisation),
  cohérents entre eux et avec le cockpit de la direction (179 nuitées du
  01/10 au 14/10, ADR 45 000, comme t15_direction.py:513-519 et
  c6_direction.py:139-140) : 13 chambres occupées sur 20 ce soir (65,0 %),
  13 séjours en cours, 22 clients présents ; du 01/10 au 14/10, 179 nuitées
  sur 14 jours × 20 chambres = 280 disponibles, soit 63,9 % — la somme des
  14 points de la courbe (chambres occupées par jour / 20 : 11, 12, 13, 13,
  14, 15, 14, 12, 12, 12, 13, 14, 11, 13) ; ADR 45 000 × 179 = 8 055 000 ;
  RevPAR = 8 055 000 / 280 = 28 768 ; CA = 8 055 000 + 440 000 de services.
  Anneau du CA hébergement : 84 nuitées Confort (3 780 000), 78 Standard
  (2 730 000), 11 Suite Junior (825 000), 6 Suite VIP (720 000), soit 179
  nuitées et 8 055 000, colorées selon leur rang (types triés par montant
  décroissant, hotel_dashboard.py:491-505 ; palette[i] de _renderRevenue,
  hotel_dashboard_view.js:322-337, COLORS de hotel_utils.js:10-18 : violet,
  vert, bleu, ocre). Courbe : une étiquette par jour, « 01/10 » à « 14/10 »
  (hotel_dashboard.py:476-489), axe vertical de 0 à 100 « v + " %" »
  (hotel_dashboard_view.js:277-315). Le tableau de bord ne compte que les
  chambres qui ne sont pas hors service (hotel_dashboard.py:105-109) :
  « sur 20 » suppose la 105
  encore vendable ce matin-là (elle est hors service au tutoriel 7, le
  15/10). Le bouton ouvre la réservation rapide (même action que le menu,
  hotel_dashboard_view.js:395-398).
- Réservation rapide : wizard/hotel_booking_wizard_views.xml:8-71 (champs,
  « Rechercher les chambres disponibles », colonnes Réserver, Chambre, Type,
  Étage, Cap. adultes, Nuits, Prix / nuit, Total séjour (HT), Client, Canal
  (:49-54, sous le client), « Confirmer immédiatement », Réserver, Fermer) ;
  wizard/hotel_booking_wizard.py:18-66 (valeurs par défaut : 1 adulte, canal
  « Direct / comptoir », confirmation cochée, dates du jour à 14:00 →
  lendemain 12:00 ; « ? » d'aide après Type de chambre, dans les deux
  fenêtres, Canal et Confirmer immédiatement, qui portent un help=, :36-39,
  :49-54, :60-63), :87-123 (seules les chambres hors service exclues, de
  capacité suffisante, libres selon is_available, triées par type puis
  numéro ; fenêtre rouverte sous le nom « Réservation rapide », :116-118,
  ECARTS n° 45), :125-158 (réservation créée avec le canal choisi, ECARTS
  n° 56, puis confirmée) ; models/hotel_room.py:474-488 (is_available :
  chevauchement et hors service).
- Réservation : views/hotel_reservation_views.xml:5-35 (liste, décorations
  info / success, somme « Total hébergement », colonne « Canal » en badge
  affichée par défaut, :23-25, ECARTS n° 58), :43-69 (boutons et barre
  d'état Brouillon, Confirmée, Arrivé, Parti ; « Non présenté », :59-61,
  ECARTS n° 42), :72-83 (bouton Folio), :88-130 (groupes Client, Séjour,
  Canal & commission, Occupation ; Check-in réel ; « ? » après Nuits, seul
  champ affiché qui porte un help=, models/hotel_reservation.py:64-68), :131-166 (onglets
  Chambres, Demandes particulières ; colonnes Type, Chambre, Adultes,
  Enfants, Occupants, Nuits, Prix / nuit, « Prix fixé » (case,
  optional="show"), Sous-total (HT), bouton de changement de chambre) ;
  models/hotel_reservation.py:27 (_order checkin_date desc), :30-145
  (libellés, « Direct / comptoir », « Téléphone / WhatsApp »), :323-360 et
  :744-800 (les deux verrous contre la double réservation), :374-418
  (confirmation : folio ouvert, nuitées synchronisées), :420-444 (check-in :
  état Arrivé, Check-in réel), :446-458 (« Check-out — RES/… »), :512-523
  (Encaisser un acompte). Libellés des champs modifiables en gras, des
  autres en graisse normale, atténués (odoo18 form_controller.scss, .o_form_label
  et .o_form_label_readonly ; form_label.js:20-36) : à l'état Confirmée,
  Client, Arrivée, Départ et Canal ; dès l'arrivée, Client (readonly hors
  brouillon / confirmée, :88-92) et Arrivée (:102-103) passent en lecture
  seule, le client devient un lien. Fil d'Ariane : « Tableau de bord —
  Réception » quand la réservation sort de l'assistant (action_book renvoie
  la fiche, hotel_booking_wizard.py:153-159), « Arrivées du jour » ensuite ;
  pager « 1 / 1 » puis « 2 / 3 » (odoo18 form_controller.js:304-313,
  relational_model.js:242-244 ; capture ref_muk/023-…-fiche.png). Canal
  des autres arrivées du jour : Martin Ebode
  « Direct / comptoir », Claire Durand « Téléphone / WhatsApp » (elle
  appelle de France) — à reporter dans demo.py si la série les reprend.
- Registre des clients : aite_guest_registry/views/hotel_reservation_views.xml
  :11-25 (bouton « Fiches d'enregistrement », anciennement « Fiches
  clients »), :27-47 (bandeau « Registre des clients : … — compléter
  maintenant », avec l'espace après les deux-points depuis la livraison 4,
  :35, ECARTS n° 47 ; « Registre des clients à jour. », « Imprimer les
  fiches »), :49-54 (bouton d'en-tête « Imprimer les fiches »,
  anciennement « Fiches d'enregistrement ») et :65-77 (colonne Registre :
  « Aucune fiche » en rouge seulement pour un client arrivé, neutre avant,
  ECARTS n° 54 : un badge sans décoration applicable prend la pastille grise
  « text-bg-300 », odoo18 badge_field.js:26-37 et bootstrap_review_backend.scss
  :239-248, comme la colonne Canal) ; models/hotel_reservation.py:31-40 (Aucune fiche, À
  compléter, Registre à jour), :77-102 (« 1 fiche à compléter · 1 occupant
  sans fiche », accordé), :108-122 (fiche du client principal créée et
  pré-remplie au check-in). Au check-in, 0/2 ; au départ, le registre est à
  jour (2/2, bandeau vert) : t06_registre.py complète les deux fiches le
  14/10 (la date de naissance, exigée pour une fiche complète, n'est
  mémorisée qu'à ce moment et ne sera pré-remplie qu'au séjour suivant :
  guest_registration.py:281-325, res_partner.py:11-20).
- Acompte : wizard/hotel_payment_wizard_views.xml:8-34 (« Encaisser un
  règlement », champs, référence exigée pour MTN et Orange, texte indicatif
  « ID transaction Mobile Money », Encaisser, Annuler) ;
  wizard/hotel_payment_wizard.py:18-62 (Solde dû actuel, Acompte coché tout
  seul avant l'arrivée, les cinq moyens de paiement ; « ? » après Acompte,
  qui porte un help=, :36-41).
- Folio : views/hotel_folio_views.xml:35-163 (Encaisser, Générer la facture,
  Ouvert / Facturé / Soldé, Règlements, Facture, groupes Séjour et Montants,
  Lignes du folio, Ajouter une ligne, Règlements, Note ; Total TTC et
  Solde dû en gras, class="fw-bold", :83, :85) ; fil d'Ariane « Arrivées du
  jour / RES/2026/0214 » (pile Arrivées du jour → réservation → folio,
  action_view_folio, hotel_reservation.py:499-510 ; deux niveaux affichés,
  odoo18 breadcrumbs.xml:5-7), pager « 1 / 1 » ;
  models/hotel_folio.py:43-111 (libellés des montants, État facture) et
  :253-276 (libellé « Nuitée 204 (Confort) — 14/10/2026 → 16/10/2026 » au
  format français, à l'heure locale, ECARTS n° 37 ; nuitée datée de
  l'arrivée, ECARTS n° 56) ; liste éditable des lignes
  (views/hotel_folio_views.xml:91-121 : ligne entière en bleu pour une
  nuitée, decoration-info ; nouvelle ligne : type « Service », date du jour
  et quantité 1 par défaut, models/hotel_folio.py:405-448 ; le service
  choisi remplit libellé et prix, :463-470) ; ligne entière en ambre pour la
  taxe (aite_city_tax/views/hotel_folio_views.xml:27-29, decoration-warning,
  teinte foncée pour le contraste) ; champ « Séjour » (reservation_state,
  related) qui passe à « Parti » au check-out
  (wizard/hotel_checkout_wizard.py:101-105) ;
  aite_city_tax/models/hotel_folio.py:119-166 (ligne « Taxe de séjour — 4
  nuitée(s) × personne (3 ★, Cameroun) », sans TVA, hors Services, datée du
  jour de chaque synchronisation, :158), views/hotel_folio_views.xml:10-24
  (montant « Taxe de séjour », avec le « ? » de son help=,
  aite_city_tax/models/hotel_folio.py:56-60 ; « Recalculer la taxe de séjour » réservé au
  Responsable, donc absent ici). Barème 3 ★ : 3 000 FCFA par nuitée
  (docs/etude_comparative/benchmark_afrique_odoo.md:12). Prestation :
  « Petit-déjeuner buffet », 2 700 FCFA
  (aite_demo_data/models/demo_generator.py:96).
- Check-out : wizard/hotel_checkout_wizard_views.xml:8-44 (groupes Séjour et
  Folio, Départ prévu, Départ réel, Total TTC, Déjà encaissé, Solde dû,
  « Générer la facture » coché par défaut, bandeau « Un solde reste dû … »,
  Valider le départ, Annuler) ; wizard/hotel_checkout_wizard.py:77-114 (le
  départ resynchronise les nuitées, puis facture) ;
  models/hotel_folio.py:304-339 (facture tirée des lignes du folio, créée,
  validée et lettrée en sudo(), folio « Facturé » ; sans accès aux
  factures, l'action renvoyée reste sur le folio) ; vue du folio facturé
  (views/hotel_folio_views.xml:36-62, :86-87 : « Générer la facture »
  masqué, bouton « Facture », « État facture ») ; lignes rangées par date
  (_order 'date, id', hotel_folio.py:407) : la nuitée datée du 14/10 reste
  en tête, le petit-déjeuner du 15/10 suit, la taxe, re-datée du 16/10 par
  la synchronisation du départ, passe en dernier ;
  models/hotel_housekeeping.py:40, 58, 169-180 (« Recouche (départ) »,
  priorité « Urgente », chambre à nettoyer).
- État facture « Partiellement réglé » : traduction Odoo 18 de « Partially
  Paid » (odoo18/addons/account/i18n/fr.po), l'acompte comptabilisé
  (res_config_settings.py, activé par défaut) étant lettré sur la facture.

Douleurs de l'accroche : recette/cas_de_test.py:48 (A03, double réservation,
critique), :71 (A07, acompte déduit, solde exact), :83 (A09, chambre hors
service proposée), :89 (A10, arrivées, départs, présents du jour) ;
docs/etude_comparative/benchmark_afrique_odoo.md:10 (aucun PMS international
ne gère nativement la taxe de séjour d'Afrique francophone : « partout il faut
ajouter une ligne/taxe configurable », d'où « à paramétrer à la main ») et :13 (loi
n° 2016/006, art. 28 : obligations de police en matière d'enregistrement).
Résultats : deux verrous (hotel_reservation.py:323-360 et :744-800), cinq
moyens d'encaissement (hotel_payment_wizard.py:42-51), 252 tests automatisés
dans addons/aite_hotel_management/tests (décompte des « def test_ », dont
test_receptionist_alone_checks_out_and_invoices, ajouté avec 18.0.1.0.4, et
ceux des écarts de la livraison 4, test_ecarts_nb.py).

Écarts corrigés dans la livraison 4 (ECARTS.md), désormais montés tels que
le produit les affiche :
- n° 42 et 62 : « Front Desk » devient « Réception » (menu) et « Tableau de
  bord — Réception » (titre, fil d'Ariane) ; « room board » → « plan des
  chambres » ; « check-out attendus aujourd'hui » → « chambres à libérer
  aujourd'hui » ; « ADR — prix moyen / nuit » → « Prix moyen par nuit
  (ADR) » ; « RevPAR » → « Revenu par chambre disponible (RevPAR) » ;
  « No-show » → « Non présenté » ; « ▲ 7,3 % vs N-1 » → « ▲ +7,3 % vs
  période précédente » (la comparaison réelle) ; « 13 / 20 chambres
  occupées » → « 13 chambres occupées sur 20 ».
- n° 45 : après la recherche, la fenêtre garde son titre « Réservation
  rapide » (elle s'intitulait « Odoo »).
- n° 56 : la réservation rapide demande le canal (« Direct / comptoir » par
  défaut, Estelle est au comptoir) ; la nuitée est datée de l'arrivée et
  reste en tête du folio au départ.
- n° 37 : le libellé de la nuitée porte des dates françaises
  (« 14/10/2026 → 16/10/2026 » au lieu de « 2026-10-14 → 2026-10-16 »).
- n° 47 : espace après « Registre des clients : » ; le bandeau est accordé
  (« 1 fiche à compléter · 1 occupant sans fiche », plus de « (s) »).
- n° 54 : « Aucune fiche » n'est plus rouge avant l'arrivée (badge neutre).
- Un seul nom pour la fiche (intégration) : bouton intelligent « Fiches
  d'enregistrement » (anciennement « Fiches clients »), bouton d'en-tête
  « Imprimer les fiches » (anciennement « Fiches d'enregistrement »).
- n° 58 : colonne « Canal » visible dans la liste des réservations.
Rien d'autre de visible ici : les dates locales du départ anticipé (n° 37)
et le lettrage protégé (n° 75) ne changent rien à Douala aux heures
normales ni pour un lettrage qui réussit.

Écarts encore rejoués tels quels :
- « Check-in », « Check-out », « ADR » et « RevPAR » (entre parenthèses)
  restent à l'écran : d'usage dans l'hôtellerie, à trancher (ECARTS n° 42).
- La taxe garde « 4 nuitée(s) » dans son libellé
  (aite_city_tax/models/hotel_folio.py:145) et, re-datée du jour du départ
  par la synchronisation, passe après le petit-déjeuner sur le folio
  facturé.
- Corrigé dans 18.0.1.0.4 : la création de la facture n'était pas en sudo ;
  sans le droit Facturation d'Odoo (account.group_account_invoice), un compte
  au seul profil Réception obtenait une erreur d'accès au check-out.
  Désormais la facture est une écriture technique (hotel_folio.py:316-320)
  et, sans accès aux factures, « Valider le départ » laisse la
  réceptionniste sur le folio, passé à « Facturé », la facture liée
  (hotel_folio.py:329-339) : c'est ce que montre l'étape 6, sans montage.
- « État facture » suppose le lettrage de l'acompte, fait au mieux
  (« best-effort », hotel_folio.py:754-790) : sans écriture d'acompte, la
  facture resterait « Non payé ».

Mise en scène : le menu déroulant « Réception » est composé ici (sous-menus
dans l'ordre des séquences) ; l'enregistrement de la ligne de service (clic
hors de la ligne) n'est pas montré ; l'écran de la réservation et du folio est
resserré (champs à 34-37 px) pour tenir dans la fenêtre ; la courbe du
tableau de bord, plus basse que celle du produit (220 px), est graduée de 20 en
20 comme Chart.js le ferait à cette hauteur (de 10 en 10 chez le client) ; les
pastilles grises gardent la teinte de la série ; la voix écrit
« check-inne » et paraphrase le titre du tutoriel suivant (« planning » est
lu à l'anglaise par Kokoro) ; « Consulting » reste lu à l'anglaise, comme
dans le pilote (nom de marque).
"""

import demo
from ecrans import (APPS_PROFIL, MENUS_MUK, NBSP, assistant, cell_puce, champ, compte, cp_fiche, deux_colonnes, e,
                    entree, fcfa, fenetre_muk, graphe_anneau, graphe_courbe, graphes, groupe, icone, interrupteur, kpi,
                    lien, m_champ, navigateur, num, onglets, pct, statusbar, tdb_entete, tdb_filtres, tdb_section,
                    titre_fiche, vue_fiche, vue_liste, vue_tdb, bouton)
from marketing import bulle, dezoom, reaction, zoom
from moteur import (animer, anneau, cacher, choisir, clic, classe, compter, curseur, defiler, fermer, montrer, ouvrir,
                    pause, saisir, survol, texte, vue)

NOM, ROLE = demo.POSTES['reception']
# Le seul profil Réception : la facture du départ est une écriture technique
# (sudo, aite_hotel_management 18.0.1.0.4), le droit Facturation n'est plus utile.
APPS = APPS_PROFIL['reception']
# Numéro de la plage de fiction de la série (demo.py).
TEL = demo.CLIENT_TEL
# Menus de l'application Hôtel pour la Réception : « Réception » (anciennement
# « Front Desk », hotel_menus.xml:21-25), puis les sections du socle et des modules.
MENUS = MENUS_MUK['hotel_reception']
MENU_RECEPTION = 'Réception'
# Le nom de l'action du tableau de bord, repris par le fil d'Ariane
# (hotel_dashboard_actions.xml:4-7).
TDB = 'Tableau de bord — Réception'
CANAL = 'Direct / comptoir'          # canal par défaut, choisi au comptoir (hotel_booking_wizard.py:49-55)

# Le séjour qui traverse le tutoriel (demo.py) et ses montants, tels que le
# code les calcule : 2 nuits × 45 000 ; taxe 3 ★ = 2 adultes × 2 nuits × 3 000 ;
# acompte de 45 000 ; quatre petits-déjeuners à 2 700. Montants des champs
# d'Odoo (fiches, listes, assistants) : ecrans.fcfa, espace insécable.
PRIX = fcfa(45000)
HEB = fcfa(90000)                    # 2 nuitées
TAXE = fcfa(12000)                   # 4 nuitées × personne à 3 000
TOTAL_RESA = fcfa(102000)            # nuitées + taxe de séjour, à la confirmation
ACOMPTE = fcfa(45000)
SOLDE_1 = fcfa(57000)                # après l'acompte
PDJ = fcfa(2700)                     # « Petit-déjeuner buffet »
PDJ_4 = fcfa(4 * 2700)
SOLDE_2 = fcfa(67800)                # après les petits-déjeuners
TOTAL_2 = fcfa(112800)
ZERO = fcfa(0)
assert (90000 + 12000, 102000 - 45000, 102000 + 4 * 2700, 112800 - 45000) == (102000, 57000, 112800, 67800)
REF_MOMO = '8742156309'          # identifiant numérique, comme ceux de MTN MoMo


def badge(texte_, genre):
    return '<span class="puce %s">%s</span>' % (genre, e(texte_))


# ------------------------------------- Tableau de bord de la réception --
# Les chiffres du tableau de bord (hotel_dashboard.py:303-390), période « Ce
# mois » du 01/10 au 14/10 : 20 chambres de la série × 14 jours. Les nuitées
# sont celles du cockpit de la direction (179 du 01/10 au 14/10, comme t15 et
# c6) ; ADR 45 000 comme au cockpit.
CHAMBRES_VENDABLES, JOURS = 20, 14
DISPO = CHAMBRES_VENDABLES * JOURS
PAR_JOUR = [11, 12, 13, 13, 14, 15, 14, 12, 12, 12, 13, 14, 11, 13]     # chambres occupées, nuit du 01/10 au 14/10
NUITEES = sum(PAR_JOUR)
TYPES_CA = {'STD': ('Standard', 35000), 'CFT': ('Confort', 45000), 'SJR': ('Suite Junior', 75000),
            'VIP': ('Suite VIP', 120000)}
NUITEES_TYPE = {'STD': 78, 'CFT': 84, 'SJR': 11, 'VIP': 6}
CA_HEB = sum(n * TYPES_CA[k][1] for k, n in NUITEES_TYPE.items())
# L'anneau colore les types selon leur rang, du plus gros CA au plus petit
# (get_revenue_by_type trie par montant décroissant, hotel_dashboard.py:491-505 ;
# _renderRevenue prend palette[i], hotel_dashboard_view.js:322-337 ; COLORS,
# hotel_utils.js:10-18) : primary, success, info, warning.
PALETTE_CA = ['#714B67', '#3B6D11', '#185FA5', '#854F0B']
TYPES_RANG = sorted(NUITEES_TYPE, key=lambda k: -NUITEES_TYPE[k] * TYPES_CA[k][1])
assert TYPES_RANG == ['CFT', 'STD', 'SJR', 'VIP']
CA_SERV = 440000
ADR = CA_HEB / NUITEES
assert (NUITEES, sum(NUITEES_TYPE.values()), CA_HEB, ADR) == (179, 179, 8055000, 45000)
assert PAR_JOUR[-1] == 13 and max(PAR_JOUR) <= CHAMBRES_VENDABLES - 1


def argent(n):
    """Un montant du tableau de bord (fmtMoney, hotel_utils.js:46-50) : espace fine entre les milliers,
    symbole de la devise de la société (« FCFA »)."""
    return fcfa(n, tdb=True)


OCC_SOIR = 13                       # chambres occupées ce soir
assert (pct(NUITEES * 100.0 / DISPO), argent(CA_HEB / DISPO), pct(OCC_SOIR * 100.0 / CHAMBRES_VENDABLES)) == (
    '63,9' + NBSP + '%', '28\u202f768 FCFA', '65,0' + NBSP + '%')
# Variations « vs période précédente » de même durée (hotel_dashboard_view.js:188-202, fmtDelta).
VS = 'vs période précédente'


def courbe_occupation():
    """« Taux d'occupation par jour » (_renderOccupancy, hotel_dashboard_view.js:277-315) : une étiquette
    par jour au format « %d/%m » (get_occupancy_evolution, hotel_dashboard.py:476-489), centrée sous son
    point ; axe vertical de 0 à 100, graduations « v + " %" ». Chart.js (v4.4.1, computeTickLimit) gradue de
    10 en 10 sur la courbe de 220 px de l'écran du client ; ramenée ici à la hauteur d'une courbe
    deux fois plus basse, il en garde une sur deux : 0 %, 20 % … 100 %, les six lignes de la grille.
    Lignes verticales : la grille de l'axe des jours (affichée par défaut)."""
    jours = ['%02d/10' % (i + 1) for i in range(JOURS)]
    html = graphe_courbe('t1-g-occ', "Taux d'occupation par jour",
                         [n * 100.0 / CHAMBRES_VENDABLES for n in PAR_JOUR])
    verticales = ''.join('<line x1="%.1f" x2="%.1f" y1="0" y2="210" stroke="#E5E7EB"/>' % (i * 760.0 / (JOURS - 1),
                                                                                        i * 760.0 / (JOURS - 1))
                         for i in range(JOURS))
    axe_y = '<div class="t1-yax">%s</div>' % ''.join(
        '<span style="top:%d%%">%d %%</span>' % (100 - v, v) for v in range(0, 101, 20))
    axe_x = ''.join('<span style="left:%.3f%%">%s</span>' % (i * 100.0 / (JOURS - 1), j) for i, j in enumerate(jours))
    assert html.count('<path ') == 1 and html.count('<div class="g-lab"></div>') == 1
    return (html.replace('<div class="g-carte">', '<div class="g-carte t1-courbe">', 1)
            .replace('<path ', verticales + '<path ', 1)
            .replace('<div class="g-zone">', axe_y + '<div class="g-zone">', 1)
            .replace('<div class="g-lab"></div>', '<div class="g-lab">%s</div>' % axe_x, 1))


FRONT = vue_tdb('t1-front', (
    tdb_entete(TDB, 'Occupation, arrivées & départs, plan des chambres · ' + demo.SOCIETE, 'Nouvelle réservation')
    + tdb_filtres([('Période', ["Aujourd'hui", '7 derniers jours', 'Ce mois', 'Mois dernier'], 2)]).replace(
        '</div></div>', '<span class="t1-esp"></span><span class="t1-date">01/10/2026</span><span class="t1-fl">→</span>'
        '<span class="t1-date">14/10/2026</span><span class="chip t1-appl">Appliquer</span></div></div>')
    + tdb_section('Photo du jour', [
        kpi('t1-k-occ', 'Occupation ce soir', pct(OCC_SOIR * 100.0 / CHAMBRES_VENDABLES),
            '%s sur %d' % (compte(OCC_SOIR, 'chambre occupée', 'chambres occupées'), CHAMBRES_VENDABLES), 'violet'),
        kpi('t1-k-arr', 'Arrivées attendues', '2', 'réservations confirmées du jour', 'bleu'),
        kpi('t1-k-dep', 'Départs prévus', '2', "chambres à libérer aujourd'hui", 'ambre'),
        kpi('t1-k-pre', 'Clients présents', '22', compte(OCC_SOIR, 'séjour en cours', 'séjours en cours'), 'vert')])
    + tdb_section('Performance de la période', [
        kpi('t1-k-to', "Taux d'occupation", pct(NUITEES * 100.0 / DISPO),
            compte(NUITEES, 'nuitée vendue', 'nuitées vendues'), None, (7.3, VS)),
        kpi('t1-k-adr', 'Prix moyen par nuit (ADR)', argent(ADR), 'CA hébergement ÷ nuitées vendues', None, (2.0, VS)),
        kpi('t1-k-rev', 'Revenu par chambre disponible (RevPAR)', argent(CA_HEB / DISPO),
            'par chambre disponible, vendue ou non', None, (9.4, VS)),
        kpi('t1-k-ca', "Chiffre d'affaires (HT)", argent(CA_HEB + CA_SERV),
            'Hébergement %s · Services %s' % (argent(CA_HEB), argent(CA_SERV)), None, (9.2, VS))])
    + '<div class="t1-graphes">%s</div>' % graphes(
        courbe_occupation(),
        graphe_anneau('t1-g-type', 'CA hébergement par type de chambre',
                      [(TYPES_CA[k][0], NUITEES_TYPE[k] * TYPES_CA[k][1], PALETTE_CA[i])
                       for i, k in enumerate(TYPES_RANG)]))
), initiale=True)

def champ_aide(libelle, valeur, identifiant=None, lien_=False):
    """Un champ de fiche qui porte une aide : le « ? » d'Odoo après le libellé (ecrans.champ, plus l'exposant) ;
    Nuits (hotel_reservation.py:64-68) et Taxe de séjour (aite_city_tax hotel_folio.py:56-60) portent un help=."""
    return ('<div class="ch"><span class="l">%s<sup class="t1-aide">?</sup></span><span class="v%s"%s>%s</span></div>'
            % (e(libelle), ' lien' if lien_ else '', ' id="%s"' % identifiant if identifiant else '', e(valeur)))


def m_champ_aide(libelle, valeur_html, identifiant=None):
    """Un champ d'assistant qui porte une aide : Odoo met un « ? » après le libellé
    (hotel_booking_wizard.py : help= sur Type de chambre, Canal, Confirmer immédiatement ; Acompte de
    l'assistant Encaisser un règlement, hotel_payment_wizard.py:36-41)."""
    return ('<div class="m-ch"%s><span class="l">%s<sup class="t1-aide">?</sup></span><span class="v">%s</span></div>'
            % (' id="%s"' % identifiant if identifiant else '', e(libelle), valeur_html))


# Le menu déroulant « Réception » (hotel_menus.xml:21-50 et aite_guest_registry
# menus.xml:4-8, sous-menus par séquence).
DEROULANT = ('<div class="t1-dd masque" id="t1-dd" data-layout-allow-overlap data-layout-allow-occlusion>%s</div>'
             % ''.join('<div class="t1-dd-i" id="t1-dd-%s">%s</div>' % (i, e(t)) for i, t in (
                 ('tdb', 'Tableau de bord'), ('rap', 'Réservation rapide'), ('arr', 'Arrivées du jour'),
                 ('dep', 'Départs du jour'), ('reg', 'Registre des clients'), ('pre', 'Clients présents'))))

# ----------------------------------------------------- Réservation rapide --
# Avant la recherche : la fenêtre « Réservation rapide » ; après, l'assistant
# est rouvert sous le même titre (hotel_booking_wizard.py:116-118, ECARTS
# n° 45), avec la liste des chambres libres, le client et le canal.
CHERCHER = '<div class="t1-chercher">%s</div>'

RAPIDE = assistant('t1-rap', 'Réservation rapide', (
    '<div class="m-grille"><div>%s%s%s</div><div>%s%s%s</div></div>' % (
        m_champ('Hôtel', entree('t1-r-hotel', '', demo.HOTEL)),
        m_champ('Arrivée', entree('t1-r-arr', '', '14/10/2026 14:00:00')),
        m_champ('Départ', entree('t1-r-dep', '', '15/10/2026 12:00:00')),
        m_champ_aide('Type de chambre', entree('t1-r-type', '')),
        m_champ('Adultes', entree('t1-r-ad', '', '1')),
        m_champ('Enfants', entree('t1-r-enf', '', '0')))
    + CHERCHER % bouton('t1-r-chercher', 'Rechercher les chambres disponibles', 'gris', 'loupe')),
    [('t1-r-fermer', 'Fermer', 'gris', None)], haut=150, largeur=1360)

RESULTATS = [
    # (id, chambre, type, étage, capacité adultes, prix / nuit, total séjour)
    ('t1-rr-102', '102 [STD]', 'Standard', 'Rez-de-chaussée', '2', fcfa(35000), fcfa(70000)),
    ('t1-rr-204', '204 [CFT]', 'Confort', '1er étage', '2', PRIX, HEB),
    ('t1-rr-205', '205 [CFT]', 'Confort', '1er étage', '2', PRIX, HEB),
    ('t1-rr-303', '303 [SJR]', 'Suite Junior', '2e étage', '3', fcfa(75000), fcfa(150000)),
    ('t1-rr-403', '403 [VIP]', 'Suite VIP', '3e étage', '4', fcfa(120000), fcfa(240000)),
]
GAB_RES = '120px 150px 1fr 200px 140px 80px 170px 200px'
TABLE_RES = (
    '<div class="t1-res" id="t1-res"><div class="t1-res-t" style="grid-template-columns:%s">%s</div>%s</div>' % (
        GAB_RES, ''.join('<span class="ell%s">%s</span>' % (' d' if d else '', e(t)) for t, d in (
            ('Réserver', 0), ('Chambre', 0), ('Type', 0), ('Étage', 0), ('Cap. adultes', 1), ('Nuits', 1),
            ('Prix / nuit', 1), ('Total séjour (HT)', 1))),
        ''.join('<div class="t1-res-l" id="%s" style="grid-template-columns:%s"><span>%s</span><span>%s</span>'
                '<span class="ell">%s</span><span class="ell">%s</span><span class="d">%s</span><span class="d">2</span>'
                '<span class="d">%s</span><span class="d">%s</span></div>'
                % (i, GAB_RES, interrupteur(i + '-tg'), e(ch), e(ty), e(et), e(cap), e(px), e(tot))
                for i, ch, ty, et, cap, px, tot in RESULTATS)))
RAPIDE_2 = assistant('t1-rap2', 'Réservation rapide', (
    '<div class="m-grille"><div>%s%s%s</div><div>%s%s%s</div></div>' % (
        m_champ('Hôtel', entree('t1-q-hotel', '', demo.HOTEL)),
        m_champ('Arrivée', entree('t1-q-arr', '', '14/10/2026 14:00:00')),
        m_champ('Départ', entree('t1-q-dep', '', '16/10/2026 12:00:00')),
        m_champ_aide('Type de chambre', entree('t1-q-type', '')),
        m_champ('Adultes', entree('t1-q-ad', '', '2')),
        m_champ('Enfants', entree('t1-q-enf', '', '0')))
    + CHERCHER % bouton('t1-q-chercher', 'Rechercher les chambres disponibles', 'gris', 'loupe')
    + TABLE_RES
    # Sous le client, le canal (hotel_booking_wizard_views.xml:49-54), « Direct / comptoir » par défaut.
    + '<div class="m-grille t1-client"><div>%s%s</div><div>%s</div></div>' % (
        m_champ('Client', entree('t1-q-cli', '')),
        m_champ_aide('Canal', entree('t1-q-canal', '', CANAL), 't1-q-canal-l'),
        m_champ_aide('Confirmer immédiatement', '<span class="case coche"><i></i></span>'))),
    [('t1-q-ok', 'Réserver', 'primaire', None), ('t1-q-fermer', 'Fermer', 'gris', None)], haut=40, largeur=1360)

# ------------------------------------------------------------ Réservation --
# Les lignes de la réservation (hotel_reservation_views.xml:131-160) : « Prix fixé »
# (price_locked, case décochée, optional="show") entre « Prix / nuit » et « Sous-total (HT) ».
LIGNE_CH = (
    '<div class="table t1-tab"><div class="t-tete" style="grid-template-columns:%(g)s">%(t)s</div>'
    '<div class="t-ligne" id="t1-l1" style="grid-template-columns:%(g)s"><span>Confort</span><span>204 [CFT]</span>'
    '<span class="d">2</span><span class="d">0</span><span></span><span class="d">2</span><span class="d">%(px)s</span>'
    '<span class="t1-pf"><span class="case"><i></i></span></span>'
    '<span class="d">%(heb)s</span><span class="t1-ech">%(ech)s</span></div>'
    '<div class="t-ajout">Ajouter une ligne</div>'
    '<div class="t-total" style="grid-template-columns:%(g)s"><span></span><span></span><span></span><span></span>'
    '<span></span><span></span><span></span><span></span><span class="d">%(heb)s</span><span></span></div></div>'
    % {'g': '1fr 160px 100px 100px 130px 70px 160px 110px 180px 40px',
       't': ''.join('<span class="ell%s">%s</span>' % (' d' if d else '', e(x)) for x, d in (
           ('Type', 0), ('Chambre', 0), ('Adultes', 1), ('Enfants', 1), ('Occupants', 0), ('Nuits', 1),
           ('Prix / nuit', 1), ('Prix fixé', 0), ('Sous-total (HT)', 1), ('', 0))),
       'px': e(PRIX), 'heb': e(HEB), 'ech': icone('echange')})
def champ_modif(ident, libelle, valeur, lien_=False):
    """Un champ modifiable de la fiche : libellé en gras (.o_form_label) ; ``<ident>-l`` pour le
    passer en lecture seule (.o_form_label_readonly : graisse normale, atténué), valeur ``<ident>``."""
    html = champ(libelle, valeur, ident, lien_=lien_, gras=True)
    assert html.count('<span class="l gras">') == 1
    return html.replace('<span class="l gras">', '<span class="l gras" id="%s-l">' % ident)


# Libellés en gras pour les champs modifiables à l'état Confirmée
# (hotel_reservation_views.xml:88-122 ; form_controller.scss, .o_form_label et
# .o_form_label_readonly ; form_label.js:20-36) : Client (readonly hors
# brouillon / confirmée), Arrivée (readonly dès l'arrivée), Départ (jusqu'au
# départ), Canal (toujours) ; Téléphone, E-mail (related), Hôtel (hors
# brouillon) et les champs calculés sont en lecture seule. Le client modifiable
# s'écrit dans sa zone de saisie ; en lecture seule, c'est un lien.
FEUILLE_RESA = (
    titre_fiche(demo.RESA)
    + deux_colonnes(
        groupe('Client', [champ_modif('t1-rf-cli', 'Client', demo.CLIENT), champ('Téléphone', TEL),
                          champ('E-mail', demo.CLIENT_MAIL), champ('Hôtel', demo.HOTEL, lien_=True)])
        + groupe('Canal & commission', [champ_modif('t1-rf-canal', 'Canal', CANAL)]),
        groupe('Séjour', [champ_modif('t1-rf-arr', 'Arrivée', demo.ARRIVEE),
                          champ_modif('t1-rf-dep', 'Départ', demo.DEPART),
                          champ_aide('Nuits', '2'), champ('Total hébergement (HT)', HEB)])
        + '<div class="masque t1-cireel" id="t1-cireel">%s</div>' % champ('Check-in réel', '14/10/2026 14:06:12')
        + groupe('Occupation', [champ('Nb chambres', '1'), champ('Adultes', '2'), champ('Enfants', '0')]))
    + onglets(['Chambres', 'Demandes particulières']) + LIGNE_CH)
# Au check-in : le bandeau d'avertissement, accordé (« 1 fiche à compléter ·
# 1 occupant sans fiche », aite_guest_registry hotel_reservation.py:77-102) et
# avec l'espace après les deux-points (« clients&#160;: », vue :35) ; au départ,
# les deux fiches complétées (t06_registre.py, le 14/10) : « Registre des
# clients à jour. ».
BANDEAUX = (
    '<div class="bandeau masque" id="t1-bandeau">%s<span><b>Registre des clients' + NBSP + ': </b>'
    + e(' · '.join([compte(1, 'fiche à compléter', 'fiches à compléter', tdb=False),
                    compte(1, 'occupant sans fiche', 'occupants sans fiche', tdb=False)]))
    + ' — <span class="act">compléter maintenant</span></span></div>'
    '<div class="bandeau t1-ok t1-cache" id="t1-bandeau-ok">%s<b>Registre des clients à jour.</b>'
    '<span class="act">Imprimer les fiches</span></div>') % (icone('fiche'), icone('coche'))
# En-tête de la réservation (hotel_reservation_views.xml:43-69 ; « Imprimer les
# fiches », aite_guest_registry hotel_reservation_views.xml:49-54) : « Non
# présenté » (anciennement « No-show ») tant qu'elle est confirmée.
B_CONF = [bouton('t1-b-checkin', 'Check-in', 'primaire'), bouton('t1-b-acompte', 'Encaisser un acompte'),
          bouton(None, 'Envoyer la confirmation'), bouton(None, 'Imprimer les fiches', ico='imprimer'),
          bouton(None, 'Non présenté'), bouton(None, 'Annuler')]
B_ARRIVE = [bouton('t1-b-checkout', 'Check-out', 'primaire'), bouton(None, 'Encaisser un acompte'),
            bouton(None, 'Envoyer la confirmation'), bouton(None, 'Imprimer les fiches', ico='imprimer'),
            bouton(None, 'Annuler')]
# Pager : « 1 / 1 » pour la réservation ouverte par l'assistant (une seule fiche,
# form_controller.js:304-313, relational_model.js:242-244), « 2 / 3 » une fois
# ouverte depuis les arrivées du jour (Estelle en 2e ligne).
RESA = vue_fiche('t1-resa', cp_fiche(TDB, demo.RESA, '1 / 1', stats=[
    ('t1-st-folio', 'document', 'Folio', TOTAL_RESA), ('t1-st-fiches', 'fiche', "Fiches d'enregistrement", '0/2')]),
    B_CONF, statusbar('t1-sb', ['Brouillon', 'Confirmée', 'Arrivé', 'Parti'], 1), FEUILLE_RESA, bandeau=BANDEAUX,
    boutons_apres=[B_ARRIVE])

# ----------------------------------------------------------------- Acompte --
ACOMPTE_AS = assistant('t1-as-acompte', 'Encaisser un règlement', (
    '<div class="m-grille"><div>%s</div><div id="t1-p-droite">%s</div></div>'
    '<div class="m-grille un t1-note">%s</div>' % (
        m_champ('Folio', '<span class="lien">%s</span>' % e(demo.FOLIO))
        + m_champ('Client', '<span class="lien">%s</span>' % e(demo.CLIENT))
        + m_champ('Solde dû actuel', e(TOTAL_RESA)),
        m_champ('Montant à encaisser', entree('t1-p-mt', '', TOTAL_RESA))
        + m_champ_aide('Acompte', '<span class="case coche"><i></i></span>')
        + m_champ('Moyen de paiement', entree('t1-p-moyen', '', 'Espèces'))
        + m_champ('Réf. transaction', entree('t1-p-ref', 'ID transaction Mobile Money'), 't1-p-ref-l')
        + m_champ('Date', e('14/10/2026'), 't1-p-date-l'),
        m_champ('Note', entree('t1-p-note', '')))),
    [('t1-p-ok', 'Encaisser', 'primaire', None), ('t1-p-non', 'Annuler', 'gris', None)], haut=120, largeur=1300)

# ------------------------------------------------------- Listes du jour --
# Liste des réservations (hotel_reservation_views.xml:5-35) : « Canal » en badge
# sans couleur, affiché par défaut depuis la livraison 4 (:23-25, ECARTS n° 58),
# entre « Solde folio » et « Registre » ; « Aucune fiche » neutre avant
# l'arrivée (aite_guest_registry hotel_reservation_views.xml:69-75, ECARTS n° 54).
COLS = [('Référence', '124px'), ('Client', '118px'), ('Arrivée', '158px'), ('Départ', '158px'), ('Nuits', '44px', 'd'),
        ('Nb chambres', '96px', 'd'), ('Total hébergement (HT)', '160px', 'd'), ('Solde folio', '100px', 'd'),
        ('Canal', '180px'), ('Registre', '112px'), ('État', '1fr')]
AUCUNE_FICHE = ('Aucune fiche', 'gris')


def ligne_resa(ident, ref, client, arr, dep, nuits, total, solde, canal, registre, etat, classe_):
    return {'id': ident, 'classe': classe_,
            'cellules': [lien(ref), client, arr, dep, nuits, '1', num(total), num(solde), cell_puce(canal, 'gris'),
                         cell_puce(*registre), cell_puce(*etat)]}


ARRIVEES = vue_liste('t1-arrivees', 'Arrivées du jour', COLS, [
    ligne_resa('t1-a0', 'RES/2026/0201', 'Claire Durand', '14/10/2026 18:00:00', '15/10/2026 12:00:00', '1',
               fcfa(120000), ZERO, 'Téléphone / WhatsApp', AUCUNE_FICHE, ('Confirmée', 'info'), 't1-info'),
    ligne_resa('t1-a1', demo.RESA, demo.CLIENT, demo.ARRIVEE, demo.DEPART, '2', HEB, SOLDE_1, CANAL,
               AUCUNE_FICHE, ('Confirmée', 'info'), 't1-info'),
    ligne_resa('t1-a2', 'RES/2026/0209', 'Martin Ebode', '14/10/2026 14:00:00', '17/10/2026 12:00:00', '3',
               fcfa(105000), fcfa(35000), CANAL, AUCUNE_FICHE, ('Confirmée', 'info'), 't1-info')],
    facettes=[('t1-fac-arr', 'Arrivées du jour')], pager='1-3 / 3',
    total=['', '', '', '', '', '', fcfa(120000 + 90000 + 105000), '', '', '', ''])

# -------------------------------------------------------------------- Folio --
GAB_FL = '104px 142px 170px 1fr 54px 124px 56px 140px 124px'


def ligne_folio(ident, date, type_, genre, service, libelle, qte, pu, montant, classe_=''):
    return ('<div class="t-ligne %s" id="%s" style="grid-template-columns:%s"><span>%s</span><span>%s</span>'
            '<span class="ell">%s</span><span class="ell t1-lib">%s</span><span class="d">%s</span><span class="d">%s</span>'
            '<span></span><span class="d">%s</span><span class="d">%s</span></div>'
            % (classe_, ident, GAB_FL, e(date), badge(type_, genre), e(service), e(libelle),
               e(qte), e(pu), e(montant), e(montant)))


# La nouvelle ligne de service, en saisie dans la liste éditable : type
# « Service » par défaut, date du jour, quantité 1 (hotel_folio.py:419-446) ;
# le choix du service remplit le libellé et le prix (_onchange_service_id, :463).
LIGNE_SAISIE = (
    '<div class="t-ligne masque t1-saisie" id="t1-fl3" style="grid-template-columns:%s"><span>15/10/2026</span>'
    '<span>%s</span><span>%s</span><span class="ell t1-lib" id="t1-fl3-lib"></span><span class="d">%s</span>'
    '<span class="d" id="t1-fl3-pu">%s</span><span></span><span class="d" id="t1-fl3-st">%s</span>'
    '<span class="d" id="t1-fl3-tt">%s</span></div>'
    % (GAB_FL, badge('Service', 'violet'), entree('t1-fl3-srv', '', '', 'entree t1-ent'),
       entree('t1-fl3-q', '', '1,00', 'entree t1-ent d'), e(ZERO), e(ZERO), e(ZERO)))

# Le libellé de la nuitée, au format français et à l'heure locale depuis la
# livraison 4 (hotel_folio.py:263-266, _fmt_local_date, ECARTS n° 37) ; la
# ligne est datée de l'arrivée (:275, ECARTS n° 56).
LIB_NUIT = 'Nuitée 204 (Confort) — 14/10/2026 → 16/10/2026'
LIB_TAXE = 'Taxe de séjour — 4 nuitée(s) × personne (3 ★, Cameroun)'     # aite_city_tax hotel_folio.py:144-150


LIGNES_FOLIO = (
    '<div class="table t1-tab" id="t1-fl"><div class="t-tete" style="grid-template-columns:%s">%s</div>%s%s'
    '<div class="pile t1-pile"><div class="t-ajout" id="t1-aj1">Ajouter une ligne</div>%s</div>'
    '<div class="t-ajout masque" id="t1-aj2">Ajouter une ligne</div>'
    '<div class="t-total" style="grid-template-columns:%s"><span></span><span></span><span></span><span></span>'
    '<span></span><span></span><span></span><span class="d" id="t1-ft-ht">%s</span><span class="d" id="t1-ft-ttc">%s</span>'
    '</div></div>' % (
        GAB_FL, ''.join('<span class="ell%s">%s</span>' % (' d' if d else '', e(x)) for x, d in (
            ('Date', 0), ('Type', 0), ('Service', 0), ('Libellé', 0), ('Qté', 1), ('Prix unitaire', 1), ('Taxes', 0),
            ('Sous-total (HT)', 1), ('Total (TTC)', 1))),
        ligne_folio('t1-fl1', '14/10/2026', 'Nuitée', 'info', '', LIB_NUIT, '2,00', PRIX, HEB, 't1-dinfo'),
        ligne_folio('t1-fl2', '14/10/2026', 'Taxe de séjour', 'orange', '', LIB_TAXE, '4,00', fcfa(3000), TAXE,
                    'taxe'),
        LIGNE_SAISIE,
        GAB_FL, TOTAL_RESA, TOTAL_RESA))
# Le folio relu après « Valider le départ » : lignes figées (liste en lecture
# seule, plus de « Ajouter une ligne », hotel_folio_views.xml:92) ; le départ
# resynchronise le folio (hotel_checkout_wizard.py:100) : la nuitée garde la
# date de l'arrivée (hotel_folio.py:275, ECARTS n° 56) et reste en tête, la
# taxe est re-datée du jour (aite_city_tax hotel_folio.py:158) et passe après
# le petit-déjeuner (_order 'date, id', hotel_folio.py:407) ; le texte sous
# les lignes disparaît (invisible="bool(move_id)").
TETE_FL = '<div class="t-tete" style="grid-template-columns:%s">%s</div>' % (
    GAB_FL, ''.join('<span class="ell%s">%s</span>' % (' d' if d else '', e(x)) for x, d in (
        ('Date', 0), ('Type', 0), ('Service', 0), ('Libellé', 0), ('Qté', 1), ('Prix unitaire', 1), ('Taxes', 0),
        ('Sous-total (HT)', 1), ('Total (TTC)', 1))))
LIGNES_APRES = (
    '<div class="table t1-tab t1-cache" id="t1-fl-apres">%s%s%s%s'
    '<div class="t-total" style="grid-template-columns:%s"><span></span><span></span><span></span><span></span>'
    '<span></span><span></span><span></span><span class="d">%s</span><span class="d">%s</span></div></div>' % (
        TETE_FL,
        ligne_folio('t1-fa1', '14/10/2026', 'Nuitée', 'info', '', LIB_NUIT, '2,00', PRIX, HEB, 't1-dinfo'),
        ligne_folio('t1-fa2', '15/10/2026', 'Service', 'violet', 'Petit-déjeuner buffet', 'Petit-déjeuner buffet',
                    '4,00', PDJ, PDJ_4),
        ligne_folio('t1-fa3', '16/10/2026', 'Taxe de séjour', 'orange', '', LIB_TAXE, '4,00', fcfa(3000), TAXE,
                    'taxe'),
        GAB_FL, TOTAL_2, TOTAL_2))
FEUILLE_FOLIO = (
    titre_fiche(demo.FOLIO)
    + deux_colonnes(
        groupe('Séjour', [champ('Client', demo.CLIENT, lien_=True), champ('Réservation', demo.RESA, lien_=True),
                          champ('Séjour', 'Arrivé', 't1-f-sej'), champ('Arrivée', demo.ARRIVEE), champ('Départ', demo.DEPART)]),
        groupe('Montants', [champ('Hébergement (HT)', HEB), champ('Services (HT)', ZERO, 't1-f-serv'),
                            champ_aide('Taxe de séjour', TAXE), champ('Total HT', TOTAL_RESA, 't1-f-ht'),
                            champ('Taxes', ZERO), champ('Total TTC', TOTAL_RESA, 't1-f-ttc'),
                            champ('Encaissé', ACOMPTE), champ('Solde dû', SOLDE_1, 't1-f-solde')], 't1-f-montants')
        + '<div class="masque" id="t1-f-etat">%s</div>' % champ('État facture', 'Partiellement réglé'))
    + onglets(['Lignes du folio', 'Règlements', 'Note']) + LIGNES_FOLIO + LIGNES_APRES
    + '<div class="note-pied" id="t1-f-note">Les lignes « nuitée » sont synchronisées depuis la réservation ; ajoutez librement des '
      'lignes de service (restaurant, blanchisserie, minibar…).</div>')
# Le folio est ouvert depuis la réservation, elle-même ouverte depuis les
# arrivées du jour : pile [Arrivées du jour, RES/2026/0214, FOL/2026/0214] à
# l'étape 5 (action_view_folio, hotel_reservation.py:499-510) comme à l'étape 6
# (« Valider le départ » rouvre le folio, hotel_folio.py:329-339). Odoo 18 montre
# les deux niveaux précédents (breadcrumbs.xml:5-7, slice(-3, -1)), séparés par
# « / » ; pager « 1 / 1 » (une seule fiche dans l'action).
FIL_FOLIO = ('<span class="parent"><span id="t1-fil-arr">Arrivées du jour</span><span class="t1-sep">/</span>'
             '<span id="t1-fil-resa">%s</span></span>' % e(demo.RESA))
FOLIO = vue_fiche('t1-folio', cp_fiche('Arrivées du jour', demo.FOLIO, '1 / 1', stats=[
    ('t1-st-regl', 'billet', 'Règlements', '1'), ('t1-st-fact', 'document', 'Facture', '')]).replace(
        '<span class="stat" id="t1-st-fact">', '<span class="stat masque" id="t1-st-fact">').replace(
        '<span class="parent">Arrivées du jour</span>', FIL_FOLIO),
    [bouton('t1-f-enc', 'Encaisser', 'primaire'), bouton('t1-f-fact', 'Générer la facture')],
    statusbar('t1-fsb', ['Ouvert', 'Facturé', 'Soldé'], 0), FEUILLE_FOLIO)

# --------------------------------------------------------------- Check-out --
CHECKOUT = assistant('t1-as-co', 'Check-out — %s' % demo.RESA, (
    '<div class="m-grille"><div><div class="grp-t">Séjour</div>%s</div><div id="t1-co-folio"><div class="grp-t">Folio</div>'
    '%s</div></div><div class="alerte-info">%s</div>' % (
        m_champ('Réservation', '<span class="lien">%s</span>' % e(demo.RESA))
        + m_champ('Client', '<span class="lien">%s</span>' % e(demo.CLIENT))
        + m_champ('Départ prévu', e(demo.DEPART))
        + m_champ('Départ réel', entree('t1-co-reel', '', '16/10/2026 11:42:18')),
        m_champ('Folio', '<span class="lien">%s</span>' % e(demo.FOLIO))
        + m_champ('Total TTC', e(TOTAL_2)) + m_champ('Déjà encaissé', e(ACOMPTE))
        + m_champ('Solde dû', '<b>%s</b>' % e(SOLDE_2))
        + m_champ('Générer la facture', '<span class="case coche"><i></i></span>', 't1-co-fact'),
        e("Un solde reste dû : vous pourrez l'encaisser depuis le folio après la facturation (bouton « Encaisser »)."))),
    [('t1-co-ok', 'Valider le départ', 'primaire', None), ('t1-co-non', 'Annuler', 'gris', None)], haut=120,
    largeur=1300)

ECRAN = navigateur(fenetre_muk('app-t1', 'Hôtel', MENUS, [FRONT, ARRIVEES, RESA, FOLIO], actif=MENU_RECEPTION,
                               societe=demo.SOCIETE, initiale=NOM[0], avatar='#185FA5',
                               apps=APPS, app_active='Hôtel',
                               calques=DEROULANT + RAPIDE + RAPIDE_2 + ACOMPTE_AS + CHECKOUT))

MENU_FD = '#app-t1 .o-haut .menu.actif'

CSS = """
.t1-aide { color: var(--o-lien); font-size: 13px; margin-left: 3px; font-weight: 700; }
/* t01 — la réception : menu déroulant, assistants et fiches resserrés */
#app-t1 .t1-dd { position: absolute; left: 152px; top: 58px; width: 300px; z-index: 26; background: #fff; padding: 6px 0;
  border: 1px solid #DEE2E6; border-radius: 0 0 6px 6px; box-shadow: 0 12px 28px rgba(0,0,0,.20); }
#app-t1 .t1-dd-i { height: 46px; display: flex; align-items: center; padding: 0 22px; font-size: 19px; color: #212529; }
#app-t1 .t1-dd-i.survol { background: #E9ECEF; }
#t1-front .t1-graphes { margin-top: 10px; }
#t1-front .kpi { padding: 12px 18px; min-height: 0; }
/* Quatre colonnes égales, comme .ahm-grid-4 ; libellés et sous-titres longs
   (« Revenu par chambre disponible (RevPAR) ») passent à la ligne, comme
   .ahm-kpi-label / .ahm-kpi-sub (aucun nowrap dans le produit). */
#t1-front .tdb-grille.c4 { grid-template-columns: repeat(4, minmax(0, 1fr)); }
#t1-front .kpi-l, #t1-front .kpi-s { white-space: normal; }
#t1-front .tdb-sect { margin: 12px 2px 8px; }
#t1-front .g-carte { height: 168px; padding: 12px 20px; }
#t1-front .g-zone { top: 46px; bottom: 34px; }
#t1-front .g-lab { bottom: 8px; }
/* Courbe : axe vertical gradué à gauche, une étiquette par jour centrée sous son point. */
#t1-front .t1-courbe .g-zone { left: 68px; right: 30px; }
#t1-front .t1-yax { position: absolute; left: 14px; width: 46px; top: 46px; bottom: 34px; }
#t1-front .t1-yax span { position: absolute; right: 0; transform: translateY(-50%); font-size: 12px; line-height: 1;
  color: var(--o-texte-3); white-space: nowrap; }
#t1-front .t1-courbe .g-lab { left: 68px; right: 30px; height: 16px; display: block; font-size: 12.5px; }
#t1-front .t1-courbe .g-lab span { position: absolute; top: 0; transform: translateX(-50%); white-space: nowrap; }
/* Fil d'Ariane à deux niveaux (séparateur « / » de .breadcrumb, gris). */
#app-t1 .fil .t1-sep { color: var(--o-texte-3); margin: 0 7px; }
/* Total TTC et Solde dû en gras (class="fw-bold", hotel_folio_views.xml:83, :85). */
#t1-folio #t1-f-ttc, #t1-folio #t1-f-solde { font-weight: 600; }
#t1-front .g-anneau { margin-top: 6px; gap: 26px; }
#t1-front .g-anneau svg { width: 120px; height: 120px; }
#t1-front .g-legs { gap: 4px; }
#t1-front .t1-esp { flex: 1; }
#t1-front .t1-date { height: 38px; padding: 0 12px; border: 1px solid #DEE2E6; border-radius: 8px; display: inline-flex;
  align-items: center; font-size: 17px; color: #212529; }
#t1-front .t1-fl { font-size: 17px; color: #5C636A; }
#t1-front .t1-appl { background: #714B67; border-color: #714B67; color: #fff; }
#t1-rap2-voile { background: transparent; }
#t1-rap .m-tete, #t1-rap2 .m-tete, #t1-as-co .m-tete, #t1-as-acompte .m-tete { height: 64px; }
#t1-rap .m-ch, #t1-rap2 .m-ch { min-height: 46px; }
#t1-rap .m-corps, #t1-rap2 .m-corps { padding: 16px 28px 12px; }
#app-t1 .t1-chercher { margin: 8px 0 10px; }
#app-t1 .t1-chercher .bt { height: 42px; font-size: 19px; }
#app-t1 .t1-chercher .bt .ico svg { width: 20px; height: 20px; }
#t1-res { border-top: 1px solid #DEE2E6; }
#t1-res .t1-res-t, #t1-res .t1-res-l { display: grid; column-gap: 12px; align-items: center; padding: 0 16px; }
#t1-res .t1-res-t { height: 44px; font-size: 18px; font-weight: 600; border-bottom: 1px solid #DEE2E6; }
#t1-res .t1-res-l { height: 46px; font-size: 18px; border-bottom: 1px solid #EEF0F2; }
#t1-res .t1-res-l.survol { background: #EEF3F6; }
#t1-rap2 .t1-client { margin-top: 6px; }
#t1-rap2 .m-tete { height: 56px; }
#t1-rap2 .m-ch { min-height: 40px; }
#t1-rap2 .m-ch .v .entree { height: 40px; }
#t1-rap2 .m-corps { padding: 10px 28px 6px; }
#t1-rap2 .t1-chercher { margin: 4px 0 6px; }
#t1-rap2 #t1-res .t1-res-t { height: 40px; }
#t1-rap2 #t1-res .t1-res-l { height: 40px; }
#app-t1 #t1-rap2 .m-pied { padding: 10px 28px 12px; }
#t1-rap2 .m-pied, #t1-rap .m-pied { padding: 14px 28px 16px; }
#app-t1 .liste .tete, #app-t1 .liste .ligne, #app-t1 .liste .total { font-size: 17px; column-gap: 12px; }
#app-t1 .liste .ligne.t1-info { color: #0B6178; }
#app-t1 .liste .ligne.t1-succes { color: #1B6E2F; }
#app-t1 .liste .ligne.t1-info .lien, #app-t1 .liste .ligne.t1-succes .lien { color: inherit; }
#app-t1 .liste .ligne.survol { background: #E6EEF3; }
#app-t1 .liste .puce { font-size: 15px; height: 28px; }
/* Onze colonnes depuis la colonne « Canal » : liste des arrivées resserrée. */
#t1-arrivees .liste .tete, #t1-arrivees .liste .ligne, #t1-arrivees .liste .total { font-size: 16px; column-gap: 10px; }
#t1-arrivees .liste .puce { font-size: 14px; height: 27px; padding: 0 10px; }
#t1-resa .bb-groupe .bt { font-size: 18px; padding: 0 13px; height: 42px; }
#t1-resa .bb-groupe .bt .ico { width: 17px; height: 17px; }
#t1-resa .st-et, #t1-folio .st-et { font-size: 18px; height: 42px; }
#t1-resa .ch, #t1-folio .ch { min-height: 37px; font-size: 18px; grid-template-columns: 230px 1fr; }
#t1-resa .ch { min-height: 34px; }
#app-t1 .st-et:not(.actif) { color: #5C636A; }
#t1-resa .grp, #t1-folio .grp { margin-bottom: 12px; }
#t1-resa .grp-t, #t1-folio .grp-t { padding-bottom: 6px; margin-bottom: 8px; }
#t1-resa .f-titre, #t1-folio .f-titre { font-size: 36px; margin-bottom: 14px; }
#t1-resa .f-titre { margin-bottom: 10px; }
#t1-resa .feuille, #t1-folio .feuille { padding: 20px 34px 30px; }
#t1-resa .feuille { padding-top: 16px; }
#app-t1 .t1-cireel { margin: -12px 0 12px; }
#app-t1 .t1-tab .t-tete { height: 46px; font-size: 17px; }
#app-t1 .t1-tab .t-ligne { height: 48px; font-size: 17px; }
#app-t1 .t1-tab .t-ajout, #app-t1 .t1-tab .t-total { height: 46px; font-size: 17px; }
#app-t1 .t1-tab .puce { font-size: 15px; height: 28px; }
#app-t1 .t1-tab .t1-lib { color: #3F6A83; }
#app-t1 .t1-tab .t-ligne.t1-dinfo, #app-t1 .t1-tab .t-ligne.t1-dinfo .t1-lib { color: #0B6178; }
#app-t1 .t1-tab .t-ligne.taxe .t1-lib { color: inherit; }
#app-t1 .t1-tab .t-ligne.t1-saisie { background: #F4F1F8; }
#app-t1 .t1-ent { font-size: 17px; height: 36px; border-width: 0 0 1px 0; border-radius: 0; padding: 0 4px; margin: 0; background: transparent; }
#app-t1 .t1-ent .ph, #app-t1 .t1-ent .val { left: 4px; right: 4px; overflow: hidden; text-overflow: ellipsis; }
#app-t1 .t1-ent.d .val { text-align: right; }
#app-t1 .t1-pile { height: 48px; }
#app-t1 .t1-pile > .t-ajout { height: 48px; }
#app-t1 .t1-pf { display: flex; align-items: center; }
#app-t1 .t1-pf .case i { width: 18px; height: 18px; border-color: #CED4DA; }
#app-t1 .t1-ech { color: #3F6A83; display: inline-flex; width: 22px; height: 22px; }
#app-t1 .t1-ech svg { width: 22px; height: 22px; }
#t1-as-acompte .m-ch, #t1-as-co .m-ch { min-height: 50px; }
#t1-as-acompte .lien, #t1-as-co .lien { color: #3F6A83; }
#t1-as-acompte .t1-note { margin-top: 10px; }
#t1-as-co .grp-t { font-size: 17px; font-weight: 700; text-transform: uppercase; padding-bottom: 8px;
  border-bottom: 1px solid #DEE2E6; margin: 4px 0 8px; color: #212529; }
#t1-as-co .alerte-info { margin: 18px 0 4px; }
#t1-b-libres { max-width: none; white-space: nowrap; }
.t1-cache { display: none !important; }
#app-t1 .bandeau.t1-ok { background: #D4EDDA; border-color: #C3E6CB; color: #155724; }
#app-t1 .bandeau.t1-ok .act { color: #155724; margin-left: 12px; }
#t1-b-taxe { max-width: 760px; }
#t1-b-momo { max-width: 400px; }
#t1-b-facture { max-width: 400px; }
"""

TUTORIEL = {
    'slug': 't01-reception',
    'profil': 't01_reception',
    'numero': 1,
    'titre': 'La réception AITE HOUSE : de la réservation à la facture',
    'fonction': 'La réception, de la réservation à la facture',
    'personnage': (NOM, ROLE),
    'accroche': {
        'kicker': 'La réception',
        'question': 'Cette chambre est-elle *vraiment* libre ce soir ?',
        'douleurs': [('alerte', 'La même chambre vendue deux fois'),
                     ('pieces', "L'acompte à déduire au franc près au départ"),
                     ('calculatrice', 'La taxe de séjour, à paramétrer à la main dans les logiciels étrangers'),
                     ('fiche', "La fiche de police, une obligation légale"),
                     ('interrogation', 'Qui arrive, qui part, qui reste ce soir ?'),
                     ('cle', 'La chambre en panne proposée au client')],
        'voix': "Cette chambre est-elle vraiment libre ce soir ? Double réservation, acompte à retrouver, taxe de "
                "séjour, fiche de police : la réception jongle.",
    },
    'revelation': {
        'promesse': "Une chambre libre en un écran, l'acompte Mobile Money tracé, le check-in en un clic, "
                    "le folio prêt à facturer.",
        'voix': "Avec Aïte haousse, la réception suit chaque séjour, de la réservation à la facture.",
    },
    'temps': ['Réserver', 'Encaisser', 'Accueillir', 'Facturer'],
    'app': 'app-t1',
    'ecran': ECRAN,
    'vues_initiales': {'odoo': 't1-front'},
    'css': CSS,
    'bulles': {
        't1-b-libres': 'Chambres réservées ou hors service : écartées de la recherche.',
        't1-b-momo': 'Référence de transaction exigée pour MTN Mobile Money et Orange Money.',
        't1-b-taxe': 'Taxe de séjour ajoutée toute seule, sans TVA : 4 nuitées × personne à %s (3 ★).' % fcfa(3000),
        't1-b-facture': "Cochée d'office : la facture se crée et se valide toute seule, avec les lignes du folio.",
    },
    'reactions': {
        't1-r-fiche': "La fiche d'enregistrement du client principal est déjà créée, pré-remplie.",
        't1-r-fin': 'La 204 part au ménage, en recouche urgente.',
    },
    'etapes': [
        {'temps': 0, 'titre': 'Le tableau de bord', 'texte': "L'occupation du soir, les arrivées, les départs et les "
                                                             "clients présents, d'un coup d'œil.",
         'voix': "Le matin, Mireille ouvre le tableau de bord de la réception : l'occupation de ce soir, les arrivées "
                 "attendues, les départs prévus. Une cliente demande une chambre : nouvelle réservation.",
         'gestes': [compter('#t1-k-occ-v', 0, 65.0, d=1.0, decimales=1, apres=NBSP + '%'),
                    compter('#t1-k-arr-v', 0, 2, d=0.8, avec=True), compter('#t1-k-dep-v', 0, 2, d=0.8, avec=True),
                    compter('#t1-k-pre-v', 0, 22, d=0.9, avec=True),
                    animer('#t1-g-occ', {'scaleX': 1}, {'scaleX': 0}, d=1.6, avec=True),
                    anneau('#t1-k-occ', d=1.1, decale=0.3), anneau('#t1-k-arr', d=1.1), anneau('#t1-k-dep', d=1.1),
                    clic('#t1-front .tdb-bt', d=0.7)]},
        {'temps': 0, 'titre': 'La réservation rapide', 'texte': 'Les dates, deux adultes : seules les chambres libres, '
                                                                'avec le prix du séjour.',
         'voix': "Pour chercher, la réservation rapide ne demande que les dates et le nombre d'adultes. La recherche ne montre que "
                 "les chambres libres, avec le prix par nuit et le total du séjour. On active la deux cent quatre, "
                 "on choisit la cliente, le canal, ici le comptoir, et on réserve.",
         'gestes': [ouvrir('t1-rap'), pause(0.3), choisir('t1-r-dep', '16/10/2026 12:00:00'),
                    choisir('t1-r-ad', '2'), clic('#t1-r-chercher'), cacher('#t1-rap', d=0.2),
                    ouvrir('t1-rap2', avec=True), pause(0.3), zoom('#t1-res', s=1.25, d=0.7, fy=0.8),
                    curseur('#t1-rr-204-tg', d=0.5), bulle('t1-b-libres', '#t1-q-chercher', cote='droite', d=2.6), pause(2.0),
                    clic('#t1-rr-204-tg'),
                    classe('#t1-rr-204-tg', ajouter=['on']), classe('#t1-rr-204', ajouter=['survol'], avec=True),
                    pause(0.4), dezoom(d=0.6), choisir('t1-q-cli', demo.CLIENT), anneau('#t1-q-canal-l', d=0.9),
                    clic('#t1-q-ok'),
                    fermer('t1-rap2'), cacher('#t1-rap-voile', d=0.25, avec=True), vue('t1-resa', avec=True)]},
        {'temps': 1, 'titre': "L'acompte Mobile Money", 'texte': 'Montant, moyen de paiement, référence : le règlement '
                                                                 'est tracé sur le folio.',
         'voix': "La réservation arrive confirmée, avec son folio déjà ouvert. Estelle verse un acompte par MTN MoMo : "
                 "le montant, le moyen de paiement, la référence de la transaction. Le solde du folio baisse aussitôt.",
         'gestes': [anneau('#t1-sb-1', d=0.8), anneau('#t1-st-folio', d=0.8), clic('#t1-b-acompte'),
                    ouvrir('t1-as-acompte'), zoom('#t1-as-acompte', s=1.2, d=0.7), saisir('t1-p-mt', ACOMPTE), curseur('#t1-p-mt', fx=0.3, d=0.4, avec=True),
                    choisir('t1-p-moyen', 'MTN Mobile Money'), saisir('t1-p-ref', REF_MOMO), curseur('#t1-p-ref', fx=0.55, d=0.4, avec=True),
                    bulle('t1-b-momo', '#t1-p-date-l', cote='gauche', d=2.2), pause(1.4), dezoom(d=0.6),
                    clic('#t1-p-ok'), fermer('t1-as-acompte'), texte('#t1-st-folio-v', SOLDE_1),
                    anneau('#t1-st-folio', d=1.3)]},
        {'temps': 2, 'titre': 'Le check-in', 'texte': "Un clic : la cliente est arrivée, le registre dit ce qui "
                                                      "manque.",
         'voix': "À quatorze heures, Estelle arrive. Depuis les arrivées du jour, Mireille ouvre sa réservation et "
                 "clique sur check-inne : la réservation passe à Arrivé, et un bandeau dit ce qui manque au registre "
                 "des clients.",
         'gestes': [clic(MENU_FD, d=0.6), montrer('#t1-dd', d=0.25, y=-8), classe('#t1-dd-arr', ajouter=['survol']),
                    clic('#t1-dd-arr', d=0.5), cacher('#t1-dd', d=0.15), vue('t1-arrivees'),
                    texte('#t1-resa .fil .parent', 'Arrivées du jour', avec=True),
                    texte('#t1-resa .pager', '2 / 3', avec=True),
                    survol('#t1-a1'), clic('#t1-a1', fx=0.15), vue('t1-resa'), clic('#t1-b-checkin'),
                    classe('#t1-sb-1', retirer=['actif']), classe('#t1-sb-2', ajouter=['actif']),
                    # Arrivé : Client et Arrivée passent en lecture seule (le client devient un lien),
                    # Départ et Canal restent modifiables.
                    classe('#t1-rf-cli-l', retirer=['gras'], avec=True), classe('#t1-rf-arr-l', retirer=['gras'], avec=True),
                    classe('#t1-rf-cli', ajouter=['lien'], avec=True),
                    cacher('#t1-resa-ga', d=0.2), montrer('#t1-resa-gb', d=0.3, y=0), montrer('#t1-cireel', d=0.3, y=0),
                    montrer('#t1-bandeau', d=0.4, y=-10), defiler('#t1-resa-defil', 52, d=0.4, avec=True),
                    anneau('#t1-bandeau', d=1.1, decale=0.2), reaction('t1-r-fiche', d=2.8), pause(1.2)]},
        {'temps': 3, 'titre': 'Le folio du séjour', 'texte': 'Nuitées, taxe de séjour calculée seule, prestations, '
                                                             'acompte déduit.',
         'voix': "Le folio rassemble tout le séjour : les nuitées, puis la taxe de séjour, ajoutée toute seule selon "
                 "le classement de l'hôtel. Pour une prestation, comme le petit-déjeuner, Mireille ajoute une ligne : "
                 "le service choisi donne le libellé et le prix, il reste la quantité. L'acompte est déjà déduit du "
                 "solde.",
         'gestes': [clic('#t1-st-folio'), vue('t1-folio'), pause(0.3), anneau('#t1-f-solde', d=1.0),
                    defiler('#t1-folio-defil', -330, d=0.8), curseur('#t1-fl2', fx=0.06, d=0.5), anneau('#t1-fl1', d=0.9, avec=True),
                    zoom('#t1-fl', s=1.25, d=0.7, fy=0.3), bulle('t1-b-taxe', '#t1-fl2', cote='bas', d=2.5),
                    pause(2.0), dezoom(d=0.5), clic('#t1-aj1', fx=0.1), cacher('#t1-aj1', d=0.15),
                    montrer('#t1-fl3', d=0.3, y=0), clic('#t1-fl3-srv', d=0.45), choisir('t1-fl3-srv', 'Petit-déjeuner buffet'),
                    texte('#t1-fl3-lib', 'Petit-déjeuner buffet', avec=True), texte('#t1-fl3-pu', PDJ, avec=True),
                    texte('#t1-fl3-st', PDJ, avec=True), texte('#t1-fl3-tt', PDJ, avec=True),
                    clic('#t1-fl3-q', d=0.45), choisir('t1-fl3-q', '4,00'), texte('#t1-fl3-st', PDJ_4),
                    texte('#t1-fl3-tt', PDJ_4, avec=True), classe('#t1-fl3', retirer=['t1-saisie'], avec=True),
                    montrer('#t1-aj2', d=0.3, y=0),
                    texte('#t1-ft-ht', TOTAL_2), texte('#t1-ft-ttc', TOTAL_2, avec=True),
                    texte('#t1-f-serv', PDJ_4, avec=True), texte('#t1-f-ht', TOTAL_2, avec=True),
                    texte('#t1-f-ttc', TOTAL_2, avec=True), texte('#t1-f-solde', SOLDE_2, avec=True),
                    texte('#t1-st-folio-v', SOLDE_2, avec=True), anneau('#t1-fl3', d=1.0), anneau('#t1-ft-ttc', d=1.0)]},
        {'temps': 3, 'titre': 'Le départ et la facture', 'texte': 'Valider le départ : la facture se crée seule, le '
                                                                  'folio passe à Facturé.',
         'voix': "Le jour du départ, le registre est à jour ; Mireille lance le check-out. L'assistant récapitule "
                 "le total, l'acompte déjà encaissé et le solde dû ; la facture est cochée d'office. Valider le "
                 "départ : la facture est créée et validée toute seule, le folio passe à Facturé, et la chambre "
                 "part au ménage.",
         'gestes': [clic('#t1-fil-resa', d=0.6),
                    # entre-temps, les deux fiches ont été complétées (t06) : registre à jour, 2/2
                    classe('#t1-bandeau', ajouter=['t1-cache'], avec=True),
                    classe('#t1-bandeau-ok', retirer=['t1-cache'], avec=True),
                    texte('#t1-st-fiches-v', '2/2', avec=True),
                    vue('t1-resa'), anneau('#t1-bandeau-ok', d=0.9), clic('#t1-b-checkout'), ouvrir('t1-as-co'), zoom('#t1-as-co', s=1.2, d=0.7),
                    bulle('t1-b-facture', '#t1-co-fact', cote='bas', d=2.3), pause(1.6), dezoom(d=0.5),
                    clic('#t1-co-ok'), fermer('t1-as-co'), defiler('#t1-folio-defil', 0, d=0.05),
                    classe('#t1-fsb-0', retirer=['actif'], avec=True), classe('#t1-fsb-1', ajouter=['actif'], avec=True),
                    cacher('#t1-f-fact', d=0.05, avec=True), montrer('#t1-st-fact', d=0.05, y=0, avec=True),
                    montrer('#t1-f-etat', d=0.05, y=0, avec=True), texte('#t1-f-sej', 'Parti', avec=True),
                    classe('#t1-fl', ajouter=['t1-cache'], avec=True),
                    classe('#t1-fl-apres', retirer=['t1-cache'], avec=True),
                    classe('#t1-f-note', ajouter=['t1-cache'], avec=True),
                    vue('t1-folio'), anneau('#t1-fsb-1', d=1.1),
                    anneau('#t1-st-fact', d=0.9), reaction('t1-r-fin', d=2.4), pause(1.0)]},
    ],
    'resultats': {
        'titre': 'Chaque séjour suivi, de la réservation au départ',
        'cartes': [
            {'valeur': '2', 'compter': 2, 'unite': 'verrous', 'icone': 'bouclier',
             'texte': 'contre la double réservation : à la confirmation, puis sur chaque séjour actif'},
            {'valeur': '5', 'compter': 5, 'unite': 'moyens', 'icone': 'pieces',
             'texte': "d'encaissement tracés sur le folio, dont MTN Mobile Money et Orange Money"},
            {'valeur': '252', 'compter': 252, 'unite': 'tests', 'icone': 'coche',
             'texte': 'automatisés sur le socle de la réception : réservations, folios, assistants, droits'},
        ],
        'voix': "Deux verrous contre la double réservation, cinq moyens d'encaissement tracés, et deux cent cinquante-deux "
                "tests automatisés sur le socle de la réception.",
    },
    'cta': {
        'appel': 'Demandez votre démonstration',
        'suivant': 'Le planning des chambres',
        'voix': "Aïte haousse, par Aïte Consulting. Demandez votre démonstration ; prochain tutoriel : chaque "
                "séjour sur sa chambre, d'un coup d'œil.",
    },
    'vignette': {'etape': 5, 'apres': 8.4},
}
