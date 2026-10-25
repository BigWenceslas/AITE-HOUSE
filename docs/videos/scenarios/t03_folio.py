# -*- coding: utf-8 -*-
"""Tutoriel 3 — Un séjour, une note, une facture (le folio du séjour).

La réservation d'Estelle Ngono, saisie et confirmée d'office par la
Réservation rapide (t01_reception.py ; « Confirmer immédiatement » coché par
défaut, wizard/hotel_booking_wizard.py:60-61, :151-152), a ouvert son folio,
nuitées et taxe de séjour comprises ; la réceptionniste encaisse un acompte
en Mobile Money, lit la note, ajoute un extra, fait le check-out (une seule
facture, tirée des lignes du folio, l'acompte lettré), retrouve le solde
dans la liste des folios et l'encaisse avant que la cliente ne reparte : le
folio passe à Soldé, chaque règlement reste tracé.

Sources — libellés et règles (addons/) :

- aite_hotel_management/views/hotel_reservation_views.xml:43-70 (boutons
  « Confirmer », « Check-in », « Check-out », « Encaisser un acompte »,
  « Envoyer la confirmation », « Non présenté » — anciennement « No-show »,
  ECARTS n° 42 —, « Annuler » et leurs conditions ; barre d'état « Brouillon /
  Confirmée / Arrivé / Parti »), :72-83 (bouton « Folio » et son solde),
  :88-130 (groupes « Client », « Séjour », « Canal & commission »,
  « Occupation »), :131-166 (onglets « Chambres », « Demandes
  particulières » ; colonnes de l'onglet Chambres, dont « Prix fixé »
  (price_locked, optional="show") et le bouton « Changer de chambre ») ;
- aite_hotel_management/models/hotel_reservation.py:47-79 (Client, Téléphone,
  E-mail, Arrivée, Départ, Nuits, Canal), :103-116 (Nb chambres, Adultes,
  Enfants, Total hébergement (HT)), :130-142 (états), :143 (« Check-in
  réel »), :374-389 (la confirmation crée le folio une seule fois et y pose
  les nuitées), :446-455 (titre « Check-out — RES/… »), :499-517 (« Folio »
  ouvre le folio, « Encaisser un acompte » ouvre l'assistant d'encaissement
  du folio), :619-637 (« Prix / nuit », « Prix fixé », « Sous-total (HT) ») ;
- aite_guest_registry/views/hotel_reservation_views.xml:11-25 (« Fiches
  d'enregistrement » n/N, anciennement « Fiches clients », masqué en
  brouillon), :40-47 (« Registre des clients à jour. » / « Imprimer les
  fiches »), :50-54 (bouton d'en-tête « Imprimer les fiches », icône
  imprimante, anciennement « Fiches d'enregistrement ») ;
- aite_hotel_management/views/hotel_folio_views.xml:9-24 (liste « Folios » :
  colonnes, décorations — ouvert avec solde en orange, soldé grisé — badges
  d'état, sommes), :36-49 (« Encaisser », « Générer la facture » masqué une
  fois facturé ; « Annuler » réservé au Responsable, donc absent pour la
  réception ; barre d'état « Ouvert / Facturé / Soldé »), :51-62
  (« Règlements », « Facture »), :66-89 (groupes « Séjour » et « Montants »,
  « État facture » une fois facturé), :91-128 (onglet « Lignes du folio »,
  colonnes, badges, texte sous les lignes, lignes figées après facture,
  « Ajouter une ligne » et texte masqués), :130-156 (onglet
  « Règlements » : colonnes, badge « Validé », bouton « Annuler » en icône),
  :175-186 (filtres « Ouverts », « Avec solde dû », « Regrouper par » État,
  Client, Hôtel), :192-206 (action « Folios ») ;
- aite_hotel_management/models/hotel_folio.py:67-113 (Hébergement (HT),
  Services (HT), Total HT, Taxes, Total TTC, Encaissé, Solde dû, État
  facture, états), :120-146 (montants recalculés en direct ; Facturé passe
  seul à Soldé quand le solde tombe à 0), :253-276 (libellé de nuitée
  « Nuitée 204 (Confort) — 14/10/2026 → 16/10/2026 », au format français et
  à l'heure locale, _fmt_local_date, depuis la livraison 4 — ECARTS n° 37 ;
  la ligne est datée de l'arrivée, ECARTS n° 56), :282-338 (la facture
  reprend une à une les lignes du folio, est comptabilisée, une seule par
  folio ; créée, validée et lettrée en sudo() depuis 18.0.1.0.4 ; sans accès
  aux factures, « Valider le départ » laisse la réceptionniste sur le folio,
  passé à « Facturé »), :398-460 (_order 'date, id' ; Type « Nuitée /
  Service », Service, Libellé, Qté, Prix unitaire, Taxes, Sous-total (HT),
  Total (TTC)), :462-470 (choisir le service remplit libellé et prix),
  :546-630 (Date, Montant, Acompte, Moyen de paiement — cinq moyens —, Réf.
  transaction, Encaissé par, État « Validé ») ;
- aite_hotel_management/wizard/hotel_payment_wizard.py:18-62 et
  hotel_payment_wizard_views.xml:8-34 (« Encaisser un règlement » : Folio,
  Client, Solde dû actuel, Montant à encaisser pré-rempli avec le solde,
  Acompte coché seul tant que le client n'est pas arrivé, Moyen de paiement,
  Réf. transaction obligatoire en MTN / Orange, texte « ID transaction Mobile
  Money », Date, Note, « Encaisser » / « Annuler ») ;
- aite_hotel_management/wizard/hotel_checkout_wizard.py:20-63, :77-114 et
  hotel_checkout_wizard_views.xml:8-44 (groupes « Séjour » et « Folio »,
  Départ prévu, Départ réel, Total TTC, Déjà encaissé, Solde dû, Générer la
  facture cochée, bandeau « Un solde reste dû : … », « Valider le départ » ;
  au départ, le folio est resynchronisé, :100) ;
- aite_hotel_management/views/hotel_menus.xml:18-86 (menus de la réception :
  « Réception », anciennement « Front Desk », ECARTS n° 42 ; « Facturation »
  → « Folios », « Règlements ») ; views/hotel_dashboard_actions.xml:4-7
  (action « Tableau de bord — Réception », reprise par le fil d'Ariane) ;
  barre de l'application : ecrans.MENUS_MUK['hotel_reception'] ;
  aite_guest_registry/views/menus.xml:11-20 (« Registre de police
  (impression) » ; « Statistiques d'hébergement » et aite_city_tax « Taxe de
  séjour » réservés au Responsable, absents ici) ;
- aite_city_tax/models/hotel_folio.py:10-13 (badge « Taxe de séjour »),
  :28-44 (la ligne de taxe ne se supprime pas à la main, ECARTS n° 57),
  :56-59 (montant « Taxe de séjour »), :119-162 (une ligne, sans TVA,
  « Taxe de séjour — 4 nuitée(s) × personne (3 ★, Cameroun) », datée du jour
  de la synchronisation, :158), views/hotel_folio_views.xml:11-52 (Qté, Prix
  unitaire, Libellé et Taxes en lecture seule sur la ligne de taxe) ;
  aite_city_tax/models/hotel_hotel.py:108-109 et aite_hotel_management/models/
  hotel_room.py:108 (articles « Taxe de séjour — <hôtel> » et « Nuitée —
  <type> », repris sur la facture) ; aite_hotel_management/models/
  res_config_settings.py:67-82 (compte client du partenaire par défaut : les
  règlements se lettrent avec la facture, d'où « Partiellement réglé » puis
  « Payé » — lettrage au mieux, vérifié depuis la livraison 4 par
  test_folio.py:298-307).

Sources — Odoo 18 (../odoo18) : addons/account/i18n/fr.po (« Partiellement
réglé », « Payé »), addons/account/models/account_move.py:1237-1275
(règlements lettrés par écriture, sans paiement ni relevé : « partial » puis
« paid », jamais « En paiement ») ; aite_hotel_management/models/
hotel_folio.py:12-24 et :697-785 (chaque règlement passe une écriture 411,
lettrée avec la facture du folio) ; addons/web/i18n/fr.po
(« Filtres », « Regrouper par », « Favoris », « Ajouter un filtre
personnalisé », « Ajouter un groupe personnalisé », « Enregistrer la recherche
actuelle », « Ajouter une ligne », « Nouveau »).

Vérifié dans une transaction annulée (odoo-bin shell, base aite_dev), sous le
seul profil Réception : le 19/10/2026 (18.0.1.0.4), « Valider le départ » crée
et valide la facture, l'action renvoyée est le folio, « Facturé », « État
facture » lisible (« Partiellement réglé ») ; l'acompte est lettré. Le
23/10/2026 (livraison 4) : libellé « Nuitée 102 (…) — 21/10/2026 →
23/10/2026 » ; après le départ, le folio relu donne la nuitée (datée de
l'arrivée), puis l'extra de la veille, puis la taxe (re-datée du jour du
départ).

Sources — accroche, résultats : docs/guides/AITE_Guide_Note_de_chambre.pdf §1
(« Un client en séjour ne doit pas sortir sa monnaie à chaque repas » : ici
les petits-déjeuners vont sur la note), §4 (« une note en attente au moment
du check-out du client, c'est un encaissement à courir après » : ici le
solde est encaissé avant que la cliente ne reparte) ;
docs/etude_comparative/benchmark_pms.md:200 (Mobile Money : aucun natif
vérifié chez les 10 PMS ; AITE HOUSE n'intègre pas non plus MTN / Orange :
il les propose comme moyens de paiement, la référence se saisit à la main,
wizard/hotel_payment_wizard.py:42-51, :79-98) ; recette/cas_de_test.py:71-76
(A07 : acompte déduit à la facturation, solde exact) ; docs/etude_comparative/
benchmark_afrique_odoo.md:11 (taxe de séjour : « partout il faut ajouter une
ligne/taxe configurable ») ; hotel_folio.py:592-598 (cinq moyens de
paiement), :310-312 (« Le folio est déjà facturé » : une facture par folio) ;
addons/aite_hotel_management/tests/test_folio.py (39 tests) et
docs/GUIDE_TESTS.md:28.

Captures de référence (modèle visuel, jamais incrustées) :
aite-videos/ref_muk/027-…-reservations-fiche.png, 025-…-clients-presents-
fiche.png, 306-reception-reservations.png (menus et applications de la
réception), 029-…-folios.png et 029-…-folios-fiche.png, 030-…-reglements.png,
024-…-departs-du-jour.png.

Données : demo.py (Estelle Ngono, RES/2026/0214, FOL/2026/0214, chambre
204 [CFT] Confort à 45 000 FCFA, réceptionniste Mireille Ateba). Le séjour
suit t01_reception.py, qui en fixe le point de départ : réservation
confirmée le 14/10 par la Réservation rapide (canal par défaut « Direct /
comptoir », téléphone demo.CLIENT_TEL, plage de fiction de la série),
acompte MTN de 45 000 FCFA le 14/10 avec
la référence de t01 (8742156309), check-in réel 14/10/2026 14:06:12 (t01,
t06), quatre « Petit-déjeuner buffet » à 2 700 FCFA le 15/10 (service de
aite_demo_data/models/demo_generator.py:87, repris par t01), départ réel
16/10/2026 11:42:18 (t01) ; d'où 102 000 FCFA à la confirmation, 57 000
après l'acompte, 112 800 TTC et 67 800 dus au départ. Sans TVA sur aucun
article, comme dans toute la série (fiche d'harmonisation) : aucun taux
n'est livré par les modules. Fiches d'enregistrement 2/2 et registre à jour au
départ : t06_registre.py complète les deux fiches le 14/10 (bouton « Fiches
d'enregistrement » 2/2).

La liste des folios (16/10, vers 11 h 45) reprend les réservations de
t02_planning.py (CONFIRMEES, SEJOURS) et t08_site_web.py (TOUTES), mêmes
numéros, mêmes clients, mêmes chambres — Rodrigue Tamba (FOL/2026/0221) en
203 du 19 au 21/10, tel que t02 le laisse après la prolongation et le
changement de chambre ; Aristide Bella (0218) en 401 du 24 au 26/10 : un
folio Ouvert, sans encaissement, par réservation confirmée à venir (le folio naît à la confirmation,
hotel_reservation.py:374-389) ; RES/2026/0222 à 0224 sont des brouillons,
sans folio. Martin Ebode (FOL/2026/0209 : 105 000 FCFA d'hébergement,
demo.ARRIVEES, 35 000 dus) ; Brigitte Essomba (202, 13-16/10, t02 SEJOURS ;
198 000 / 100 000 / 98 000 FCFA, montants de l'en-tête de t04_note_chambre.py) sous
le numéro libre FOL/2026/0210 ; trois séjours passés de t02 SEJOURS, Soldé
(Nadine Ekambi 0208, Sylvie Mbarga 0207 comme t04, Pauline Ekotto 0206).
Numéros des séjours passés et total de 211 folios : fictifs. Filtre « Avec
solde dû » : 14 folios, 1 847 800 FCFA TTC, 224 000 encaissés, 1 623 800
dus (sommes calculées dans le script).

Profil : le seul profil Réception (barre MuK = APPS_PROFIL['reception'],
sans l'application Facturation). L'écart qui obligeait à lui donner le droit
Facturation d'Odoo (facture du départ créée sans sudo) est corrigé dans
18.0.1.0.4 ; « Valider le départ » laisse alors la réceptionniste sur le
folio (étape 5), plus sur la facture comptable.

Écarts relevés (docs/videos/ECARTS.md) ; ceux des n° 37 à 77 sont corrigés
dans la livraison 4 et le tutoriel montre le produit corrigé :
1. Libellé de nuitée en dates ISO (« — 2026-10-14 → 2026-10-16 ») :
   corrigé (n° 37), « — 14/10/2026 → 16/10/2026 », à l'heure locale,
   hotel_folio.py:263-266 ; repris tel quel sur la facture.
2. Départ avec facture et encaissement du solde sous le seul profil
   Réception : corrigés dans aite_hotel_management 18.0.1.0.4 (facture en
   sudo, hotel_folio.py:316-328) et 18.0.1.0.5 (lettrage du règlement avec la
   facture en sudo, _post_accounting_entry). Tests :
   test_receptionist_alone_checks_out_and_invoices,
   test_receptionist_collects_the_balance_after_invoicing. L'étape 7 (folio
   Soldé, État facture « Payé ») est donc vraie pour ce profil.
3. Nuitées re-datées du jour du départ, rangées après les extras : corrigé
   (n° 56), la nuitée est datée de l'arrivée (hotel_folio.py:272-275) et
   reste en tête du folio relu. La taxe de séjour, elle, reste datée du jour
   de sa dernière synchronisation (aite_city_tax hotel_folio.py:158) : au
   départ, elle passe après le petit-déjeuner — rejoué tel quel (étapes 5
   et 7).
4. L'aide « Départs du jour » promettait que Check-out encaisse le solde :
   corrigé (n° 48), elle renvoie au bouton « Encaisser » du folio
   (hotel_reservation_views.xml:314), comme l'assistant
   (hotel_checkout_wizard_views.xml:34-37) et l'étape 7. L'écran n'est pas
   rejoué.
5. « Partiellement réglé » puis « Payé » (État facture du folio) supposent
   le lettrage des règlements avec la facture, fait au mieux : depuis la
   livraison 4 (n° 75), il passe par un point de sauvegarde et un échec est
   écrit dans le journal du serveur au lieu d'interrompre la facturation
   (hotel_folio.py:769-785) ; le test vérifie l'état de la facture
   (test_folio.py:298-307, « partial », acompte lettré).
6. Libellés de la livraison 4 sur les écrans rejoués : menu « Réception »
   (n° 42), fil d'Ariane « Tableau de bord — Réception », « Non présenté »
   (n° 42), « Imprimer les fiches » et « Fiches d'enregistrement » (relecture
   de l'intégration), dates françaises de la nuitée (n° 37).

Cohérence de la série (fiche d'harmonisation) : Estelle Ngono reste en 204
du 14 au 16/10 dans tous les tutoriels (t02 prolonge et déplace Rodrigue
Tamba, pas elle) ; t04_note_chambre.py reprend cette liste (Brigitte
Essomba en FOL/2026/0210, mêmes folios ouverts) et y ajoute FOL/2026/0226
et 0227, créés le 16/10 ; t05_taxe_sejour.py suit Pélagie Ondobo
(RES/FOL 2026/0228), sans TVA, comme ici.
"""

import demo
from ecrans import (APPS_PROFIL, ICONES, MENUS_MUK, NBSP, assistant, bouton, cell_puce, champ, cp_fiche, deux_colonnes,
                    e, entree, fcfa, fenetre_muk, groupe, icone, m_champ, navigateur, puce, statusbar, titre_fiche,
                    vue_fiche, vue_liste)
from marketing import bulle, dezoom, reaction, zoom
from moteur import (anneau, cacher, choisir, clic, classe, compter, curseur, defiler, fermer, montrer, ouvrir, pause,
                    saisir, survol, texte, vue)

NOM, ROLE = demo.POSTES['reception']
RESA, FOLIO, CLIENT = demo.RESA, demo.FOLIO, demo.CLIENT
# Le séjour tel que t01_reception.py le fixe : réservation confirmée et
# acompte MTN le 14/10 (REF_MOMO de t01), check-in réel 14:06:12, quatre
# petits-déjeuners buffet à 2 700 FCFA le 15/10, départ réel 16/10 11:42:18.
REF_MOMO = '8742156309'
TEL = demo.CLIENT_TEL                # plage de fiction de la série, comme t01
SERVICE = 'Petit-déjeuner buffet'   # aite_demo_data/models/demo_generator.py:87, 2 700 FCFA
# Jour de l'arrivée (= jour de la confirmation, le matin), de l'extra, du départ.
J_ARRIVEE, J_EXTRA, J_DEPART = '14/10/2026', '15/10/2026', '16/10/2026'
J_CONF = J_ARRIVEE
CHECKIN_REEL, DEPART_REEL = '14/10/2026 14:06:12', '16/10/2026 11:42:18'
# Montants des champs d'Odoo (ecrans.fcfa : espace insécable, symbole FCFA) :
# 2 nuits × 45 000 + taxe 3 ★ 2 adultes × 2 nuits × 3 000 = 102 000 ; acompte
# 45 000 ; 4 × 2 700 = 10 800 ; 112 800 TTC (sans TVA), 67 800 dus.
assert (2 * 45000 + 2 * 2 * 3000, 102000 - 45000, 102000 + 4 * 2700, 112800 - 45000) == (102000, 57000, 112800,
                                                                                         67800)
TOTAL_1, SOLDE_1 = fcfa(102000), fcfa(57000)
SERVICES, TOTAL_2, SOLDE_2 = fcfa(4 * 2700), fcfa(112800), fcfa(67800)
ACOMPTE, PDJ, TAXE_PU, TAXE_MT, ZERO = fcfa(45000), fcfa(2700), fcfa(3000), fcfa(12000), fcfa(0)
# Libellé de la nuitée au format français, à l'heure locale (hotel_folio.py:263-266,
# _fmt_local_date, livraison 4, ECARTS n° 37), repris tel quel sur la facture ; il
# tient en entier dans la colonne Libellé (largeurs de COLS_LIGNES, 17 px).
LIB_NUIT = 'Nuitée 204 (Confort) — 14/10/2026 → 16/10/2026'
LIB_TAXE = 'Taxe de séjour — 4 nuitée(s) × personne (3 ★, Cameroun)'     # aite_city_tax hotel_folio.py:144-150

# Barre de l'application Hôtel du profil Réception : « Réception »
# (anciennement « Front Desk », hotel_menus.xml:18-25, ECARTS n° 42).
MENUS = MENUS_MUK['hotel_reception']
MENU_RECEPTION = 'Réception'
# Le fil d'Ariane reprend le nom de l'action du tableau de bord, d'où la
# réservation est ouverte (hotel_dashboard_actions.xml:4-7).
TDB = 'Tableau de bord — Réception'
# Le seul profil Réception : la facture du départ est une écriture technique
# (sudo, aite_hotel_management 18.0.1.0.4), le droit Facturation n'est plus utile.
APPS = list(APPS_PROFIL['reception'])

# icônes du panneau de recherche (filtre, regroupement, favori), redessinées
ICO_FILTRE = ('<svg viewBox="0 0 24 24" fill="#4A7892"><path d="M3 4h18l-7 8.5V19l-4 2v-8.5z"/></svg>')
ICO_GROUPE = ('<svg viewBox="0 0 24 24" fill="none" stroke="#1E7B34" stroke-width="2.2" stroke-linejoin="round">'
              '<path d="M12 3l9 4.5-9 4.5-9-4.5z"/><path d="M3 12l9 4.5 9-4.5M3 16.5l9 4.5 9-4.5"/></svg>')
ICO_FAVORI = ('<svg viewBox="0 0 24 24" fill="#C98A00"><path d="M12 2.5l2.9 6.3 6.9.7-5.2 4.6 1.5 6.8L12 17.4l-6.1 '
              '3.5 1.5-6.8L2.2 9.5l6.9-.7z"/></svg>')


def remplacer(html, avant, apres):
    """Retouche d'un fragment composé par ecrans.py ; le fragment doit exister une fois."""
    assert html.count(avant) == 1, avant
    return html.replace(avant, apres)


def lien(texte_):
    return '<span class="t03-lien">%s</span>' % e(texte_)


def case(cochee, ident=None):
    return '<span class="case%s"%s><i></i></span>' % (' coche' if cochee else '', ' id="%s"' % ident if ident else '')


def tableau(ident, colonnes, lignes, total=None, ajouter=None, classe_=''):
    """Un tableau de lignes (one2many) avec ses classes de ligne et des cellules
    de total adressables : ``lignes`` = (id, [cellules], classe) ; ``total`` =
    [(texte, id)]."""
    gab = ' '.join(c[1] for c in colonnes)
    tete = '<div class="t-tete" style="grid-template-columns:%s">%s</div>' % (
        gab, ''.join('<span class="ell%s">%s</span>' % (' d' if len(c) > 2 else '', e(c[0])) for c in colonnes))
    corps = []
    for lid, cellules, cl in lignes:
        cs = []
        for k, c in enumerate(cellules):
            cs.append(c[0] if isinstance(c, tuple) else '<span class="ell%s">%s</span>'
                      % (' d' if len(colonnes[k]) > 2 else '', e(c)))
        corps.append('<div class="t-ligne %s" id="%s" style="grid-template-columns:%s">%s</div>'
                      % (cl, lid, gab, ''.join(cs)))
    ajout = '<div class="t-ajout" id="%s-ajout">%s</div>' % (ident, e(ajouter)) if ajouter else ''
    pied = ''
    if total:
        pied = '<div class="t-total" style="grid-template-columns:%s">%s</div>' % (gab, ''.join(
            '<span class="d" id="%s">%s</span>' % (i, e(t)) if t else '<span></span>' for t, i in total))
    return '<div class="table %s" id="%s">%s%s%s%s</div>' % (classe_, ident, tete, ''.join(corps), ajout, pied)


def ligne(lid, libelle, valeur, id_val):
    """Une ligne de champ de fiche, adressable en entier (``lid``) pour l'anneau."""
    return '<div id="%s">%s</div>' % (lid, champ(libelle, valeur, id_val))


# ------------------------------------------------------------ la réservation --
# En-tête (hotel_reservation_views.xml:43-70) : « Non présenté » (anciennement
# « No-show », ECARTS n° 42) ; bouton d'impression « Imprimer les fiches »
# (anciennement « Fiches d'enregistrement », aite_guest_registry
# hotel_reservation_views.xml:50-54), posé après « Envoyer la confirmation ».
B_CONFIRMEE = [bouton('t03-b-checkin', 'Check-in', 'primaire'), bouton('t03-b-acompte', 'Encaisser un acompte'),
               bouton('t03-b-conf', 'Envoyer la confirmation'),
               bouton('t03-b-fiches', 'Imprimer les fiches', ico='imprimer'), bouton('t03-b-noshow', 'Non présenté'),
               bouton('t03-b-ann1', 'Annuler')]
B_ARRIVE = [bouton('t03-b-checkout', 'Check-out', 'primaire'), bouton('t03-b-acompte2', 'Encaisser un acompte'),
            bouton('t03-b-conf2', 'Envoyer la confirmation'),
            bouton('t03-b-fiches2', 'Imprimer les fiches', ico='imprimer'), bouton('t03-b-ann2', 'Annuler')]
# Six boutons et la barre d'état ne tiennent pas sur une ligne : Odoo replie
# alors la barre sur l'état courant (captures 025 et 027 du thème MuK). La
# réservation arrive confirmée de la Réservation rapide (t01_reception.py).
ETAT_RESA = '<div class="t03-sbc" id="t03-sbc"><span id="t03-sbc-t">Confirmée</span></div>'
# Onglet Chambres (hotel_reservation_views.xml:131-161) : « Prix fixé »
# (price_locked, optional="show", case décochée) entre « Prix / nuit » et
# « Sous-total (HT) », puis le bouton « Changer de chambre » (icône, réservation
# confirmée ou arrivée) — comme t01_reception.py.
ECHANGE = ('<span class="t03-ech" title="Changer de chambre">%s</span>' % icone('echange'),)
CHAMBRES = tableau('t03-ch', [('Type', '1fr'), ('Chambre', '160px'), ('Adultes', '100px', 'd'),
                              ('Enfants', '100px', 'd'), ('Occupants', '130px'), ('Nuits', '70px', 'd'),
                              ('Prix / nuit', '160px', 'd'), ('Prix fixé', '110px'), ('Sous-total (HT)', '180px', 'd'),
                              ('', '40px')],
                   [('t03-rl1', [demo.TYPE, demo.CHAMBRE, '2', '0', '', '2', demo.PRIX_NUIT, (case(False),),
                                 demo.TOTAL_HEB, ECHANGE], '')],
                   total=[('', '')] * 8 + [(demo.TOTAL_HEB, 't03-ch-tot'), ('', '')], ajouter='Ajouter une ligne')
FEUILLE_RESA = (
    titre_fiche(RESA)
    + deux_colonnes(
        groupe('Client', [champ('Client', CLIENT, lien_=True, gras=True), champ('Téléphone', TEL),
                          champ('E-mail', demo.CLIENT_MAIL), champ('Hôtel', demo.HOTEL, lien_=True)])
        + groupe('Canal & commission', [champ('Canal', 'Direct / comptoir')]),
        groupe('Séjour', [champ('Arrivée', demo.ARRIVEE, gras=True), champ('Départ', demo.DEPART, gras=True),
                          champ('Nuits', '2'), champ('Total hébergement (HT)', demo.TOTAL_HEB),
                          '<div class="t03-cache" id="t03-cireel">%s</div>'
                          % champ('Check-in réel', CHECKIN_REEL)], identifiant='t03-grp-sejour')
        + groupe('Occupation', [champ('Nb chambres', '1'), champ('Adultes', '2'), champ('Enfants', '0')]))
    + '<div class="onglets"><span class="onglet actif">Chambres</span><span class="onglet">Demandes particulières'
      '</span></div>' + CHAMBRES)
BANDEAU_REGISTRE = ('<div class="bandeau t03-ok t03-cache" id="t03-bandeau">%s<b>Registre des clients à jour.</b>'
                    '<span class="act">Imprimer les fiches</span></div>' % icone('coche'))
# Boutons intelligents : « Folio » (son solde) puis « Fiches d'enregistrement »
# (anciennement « Fiches clients », aite_guest_registry
# hotel_reservation_views.xml:11-25).
V_RESA = vue_fiche('t03-resa', cp_fiche(TDB, RESA, '', stats=[
    ('t03-st-folio', 'document', 'Folio', TOTAL_1), ('t03-st-fiches', 'fiche', "Fiches d'enregistrement", '0/2')]),
    B_CONFIRMEE, ETAT_RESA, FEUILLE_RESA, initiale=True, bandeau=BANDEAU_REGISTRE,
    boutons_apres=[B_ARRIVE])

# ----------------------------------------------------- le folio (pendant le séjour) --
COLS_LIGNES = [('Date', '104px'), ('Type', '136px'), ('Service', '172px'), ('Libellé', '1fr'), ('Qté', '56px', 'd'),
               ('Prix unitaire', '124px', 'd'), ('Taxes', '58px'), ('Sous-total (HT)', '140px', 'd'),
               ('Total (TTC)', '130px', 'd')]
NUIT = ('<span>%s</span>' % puce('Nuitée', 'info'),)
TAXE = ('<span>%s</span>' % puce('Taxe de séjour', 'orange'),)
SERV = ('<span>%s</span>' % puce('Service', 'violet'),)


def _cell(ident, valeur, droite=False):
    return ('<span class="ell%s" id="%s">%s</span>' % (' d' if droite else '', ident, e(valeur)),)


LIGNES = tableau('t03-lignes', COLS_LIGNES, [
    # la nuitée est datée de l'arrivée (hotel_folio.py:272-275, ECARTS n° 56) ;
    # la taxe, du jour de sa synchronisation (la confirmation, le 14/10 au matin)
    ('t03-fl1', [J_ARRIVEE, NUIT, '', LIB_NUIT, '2,00', demo.PRIX_NUIT, '', demo.TOTAL_HEB, demo.TOTAL_HEB],
     't03-nuit'),
    ('t03-fl2', [J_CONF, TAXE, '', LIB_TAXE, '4,00', TAXE_PU, '', TAXE_MT, TAXE_MT], 'taxe'),
    # la ligne ajoutée pendant le séjour, en saisie
    ('t03-fl3', [J_EXTRA, SERV, (entree('t03-svc', '', '', classe='t03-cell'),), _cell('t03-fl3-lib', ''),
                 (entree('t03-qte', '', '1,00', classe='t03-cell d'),), _cell('t03-fl3-pu', ZERO, True), '',
                 _cell('t03-fl3-st', ZERO, True), _cell('t03-fl3-tt', ZERO, True)], 't03-edit t03-cache'),
], total=[('', '')] * 7 + [(TOTAL_1, 't03-lt-ht'), (TOTAL_1, 't03-lt-ttc')],
    ajouter='Ajouter une ligne', classe_='t03-lignes')
FEUILLE_FOLIO = (
    titre_fiche(FOLIO)
    + deux_colonnes(
        groupe('Séjour', [champ('Client', CLIENT, lien_=True), champ('Réservation', RESA, lien_=True),
                          champ('Séjour', 'Confirmée', 't03-f-sejour'), champ('Arrivée', demo.ARRIVEE),
                          champ('Départ', demo.DEPART)]),
        groupe('Montants', [champ('Hébergement (HT)', demo.TOTAL_HEB), champ('Services (HT)', ZERO, 't03-f-serv'),
                            champ('Taxe de séjour', TAXE_MT), champ('Total HT', TOTAL_1, 't03-f-ht'),
                            champ('Taxes', ZERO), champ('Total TTC', TOTAL_1, 't03-f-ttc'),
                            ligne('t03-r-paye', 'Encaissé', ACOMPTE, 't03-f-paye'),
                            ligne('t03-r-solde', 'Solde dû', SOLDE_1, 't03-f-solde')],
               identifiant='t03-grp-montants'))
    + '<div class="onglets"><span class="onglet actif">Lignes du folio</span><span class="onglet">Règlements</span>'
      '<span class="onglet">Note</span></div>' + LIGNES
    + '<div class="note-pied">Les lignes « nuitée » sont synchronisées depuis la réservation ; ajoutez librement des '
      'lignes de service (restaurant, blanchisserie, minibar…).</div>')
V_FOLIO = vue_fiche('t03-folio', cp_fiche(TDB + ' / ' + RESA, FOLIO, '', stats=[
    ('t03-st-regl', 'billet', 'Règlements', '1')]),
    [bouton('t03-f-enc', 'Encaisser', 'primaire'), bouton('t03-f-fact', 'Générer la facture')],
    statusbar('t03-fsb', ['Ouvert', 'Facturé', 'Soldé'], 0), FEUILLE_FOLIO)
# le fil d'Ariane : un clic sur « RES/2026/0214 » ramène à la réservation
V_FOLIO = remplacer(V_FOLIO, '<span class="parent">%s / %s</span>' % (e(TDB), RESA),
                    '<span class="parent">%s / <span id="t03-fil-res">%s</span></span>' % (e(TDB), RESA))

# ---------------------------------------------------- la liste des folios --
COLS_LISTE = [('Référence', '200px'), ('Client', '1fr'), ('Réservation', '200px'), ('Total TTC', '190px', 'd'),
              ('Encaissé', '170px', 'd'), ('Solde dû', '170px', 'd'), ('État', '150px')]
ETATS = {'Ouvert': 'info', 'Facturé': 'orange', 'Soldé': 'vert'}


def folio_resa(type_, nuits, adultes=2):
    """Le folio d'une réservation confirmée : nuitées sans TVA (convention de
    la série) + taxe de séjour 3 ★, 3 000 FCFA par adulte et par nuit
    (t08_site_web.py solde_folio, t02_planning.py)."""
    return {'STD': 35000, 'CFT': 45000, 'SJR': 75000, 'VIP': 120000}[type_] * nuits + 3000 * adultes * nuits


# La liste le 16/10 vers 11 h 45, après le départ d'Estelle Ngono ; ordre
# « create_date desc » (hotel_folio.py:29), numéros FOL = numéros RES (convention
# de la série). Réservations, clients, chambres et dates de t02_planning.py
# (CONFIRMEES, SEJOURS) et t08_site_web.py (TOUTES) : un folio par réservation
# confirmée ; RES/2026/0222 à 0224 sont des brouillons, donc sans folio
# (hotel_reservation.py:374-389). Les folios des réservations à venir n'ont
# aucun encaissement (t08 : « Solde folio » = folio entier). Martin Ebode :
# 105 000 FCFA d'hébergement (demo.ARRIVEES), 1 adulte, 35 000 FCFA dus.
# Brigitte Essomba (202 [CFT], 13-16/10, t02 SEJOURS ; montants de
# l'en-tête de t04_note_chambre.py, bar compris) : départ pas encore validé. Les
# séjours passés (t02 SEJOURS) sont facturés et réglés : Soldé.
FOLIOS = [
    ('0221', 'Rodrigue Tamba', folio_resa('CFT', 2), 0, 'Ouvert'),        # 203, 19-21/10
    ('0220', 'Viviane Eyoum', folio_resa('SJR', 2), 0, 'Ouvert'),         # 303, 04-06/11
    ('0219', 'Mathieu Nkodo', folio_resa('STD', 2), 0, 'Ouvert'),         # 104, 30/10-01/11
    ('0218', 'Aristide Bella', folio_resa('VIP', 2), 0, 'Ouvert'),        # 401, 24-26/10
    ('0217', 'Olivier Ndzana', folio_resa('STD', 2), 0, 'Ouvert'),        # 106, 23-25/10
    ('0216', 'Christelle Ndongo', folio_resa('STD', 2), 0, 'Ouvert'),     # 102, 21-23/10
    ('0215', 'Blaise Atangana', folio_resa('CFT', 3), 0, 'Ouvert'),       # 205, 28-31/10
    ('0214', CLIENT, 112800, 45000, 'Facturé'),                           # 204, 14-16/10
    ('0213', 'Gaston Mbida', folio_resa('STD', 2), 0, 'Ouvert'),          # 103, 15-17/10
    ('0212', 'Carine Manga', folio_resa('SJR', 2), 0, 'Ouvert'),          # 302, 22-24/10
    ('0211', 'Joël Kamga', folio_resa('CFT', 2), 0, 'Ouvert'),            # 204, 18-20/10
    ('0210', 'Brigitte Essomba', 198000, 100000, 'Ouvert'),               # 202, 13-16/10
    ('0209', 'Martin Ebode', 105000 + 9000, 79000, 'Ouvert'),             # 104, 14-17/10
    ('0208', 'Nadine Ekambi', folio_resa('CFT', 2), folio_resa('CFT', 2), 'Soldé'),       # 202, 07-09/10
    ('0207', 'Sylvie Mbarga', folio_resa('SJR', 2), folio_resa('SJR', 2), 'Soldé'),       # 302, 05-07/10
    ('0206', 'Pauline Ekotto', folio_resa('CFT', 3), folio_resa('CFT', 3), 'Soldé'),      # 205, 06-09/10
    ('0205', 'Paul Abessolo', folio_resa('SJR', 2), 0, 'Ouvert'),         # 301, 16-18/10
]
DUS = [f for f in FOLIOS if f[2] > f[3]]                 # filtre « Avec solde dû »
SOMMES = [fcfa(sum(f[k] for f in DUS)) for k in (2, 3)] + [fcfa(sum(f[2] - f[3] for f in DUS))]
PAGER, PAGER_DU = '1-80 / 211', '1-%d / %d' % (len(DUS), len(DUS))
assert SOMMES == [fcfa(1847800), fcfa(224000), fcfa(1623800)], SOMMES
V_LISTE = vue_liste('t03-liste', 'Folios', COLS_LISTE, [
    {'id': 't03-l-' + n, 'cellules': ['FOL/2026/' + n, cli, 'RES/2026/' + n, fcfa(ttc), fcfa(paye), fcfa(ttc - paye),
                                      cell_puce(etat_, ETATS[etat_])],
     'classe': 'retard' if etat_ == 'Ouvert' else ('t03-muet' if etat_ == 'Soldé' else '')}
    for n, cli, ttc, paye, etat_ in FOLIOS],
    facettes=[('t03-fac', 'Avec solde dû')], pager=PAGER,
    total=['', '', ''] + SOMMES + [''])
V_LISTE = remplacer(V_LISTE, '<span class="facette" id="t03-fac">', '<span class="facette t03-cache" id="t03-fac">')
V_LISTE = remplacer(V_LISTE, '<span class="pager">%s</span>' % PAGER, '<span class="pager" id="t03-pager">%s</span>' % PAGER)
# la somme en pied de liste n'est visible qu'une fois la liste filtrée (80 lignes sinon)
V_LISTE = remplacer(V_LISTE, '<div class="total" ', '<div class="total t03-cache" id="t03-lt" ')
PANNEAU = (
    '<div class="t03-panneau masque" id="t03-panneau">'
    '<div class="t03-pc"><div class="t03-ph">%sFiltres</div><div class="t03-pi">Ouverts</div>'
    '<div class="t03-pi" id="t03-pf-solde"><span class="t03-coche t03-cache" id="t03-pf-coche">✓</span>Avec solde dû'
    '</div><div class="t03-sep"></div><div class="t03-pi">Ajouter un filtre personnalisé</div></div>'
    '<div class="t03-pc"><div class="t03-ph">%sRegrouper par</div><div class="t03-pi">État</div>'
    '<div class="t03-pi">Client</div><div class="t03-pi">Hôtel</div><div class="t03-sep"></div>'
    '<div class="t03-pi">Ajouter un groupe personnalisé</div></div>'
    '<div class="t03-pc"><div class="t03-ph">%sFavoris</div><div class="t03-pi">Enregistrer la recherche actuelle'
    '</div></div></div>' % (ICO_FILTRE, ICO_GROUPE, ICO_FAVORI))
V_LISTE = remplacer(V_LISTE, '<span class="deroule">▾</span></div>', '<span class="deroule">▾</span>%s</div>' % PANNEAU)

# ------------------------------------------- le folio après le check-out --
# Les lignes relues après le départ (_order 'date, id', hotel_folio.py:407) :
# le départ resynchronise le folio (hotel_checkout_wizard.py:100) ; la nuitée
# garde la date de l'arrivée (hotel_folio.py:272-275, ECARTS n° 56) et reste en
# tête, la taxe est re-datée du jour du départ (aite_city_tax hotel_folio.py:158)
# et passe après le petit-déjeuner. Vérifié le 23/10/2026 sur aite_dev, sous le
# seul profil Réception, dans une transaction annulée.
def lignes_apres(ident, pref):
    return tableau(ident, COLS_LIGNES, [
        (pref + '1', [J_ARRIVEE, NUIT, '', LIB_NUIT, '2,00', demo.PRIX_NUIT, '', demo.TOTAL_HEB, demo.TOTAL_HEB],
         't03-nuit'),
        (pref + '2', [J_EXTRA, SERV, SERVICE, SERVICE, '4,00', PDJ, '', SERVICES, SERVICES], ''),
        (pref + '3', [J_DEPART, TAXE, '', LIB_TAXE, '4,00', TAXE_PU, '', TAXE_MT, TAXE_MT], 'taxe'),
    ], total=[('', '')] * 7 + [(TOTAL_2, ident + '-ht'), (TOTAL_2, ident + '-ttc')], classe_='t03-lignes')


LIGNES2 = lignes_apres('t03-f2-lignes', 't03-gl')
VALIDE = ('<span>%s</span>' % puce('Validé', 'vert'),)
ANNULER = ('<span class="t03-x" title="Annuler">%s</span>' % ICONES['x'],)
REGLEMENTS = tableau('t03-f2-regl', [('Date', '130px'), ('Acompte', '110px'), ('Moyen de paiement', '240px'),
                                     ('Réf. transaction', '1fr'), ('Montant', '160px', 'd'), ('Encaissé par', '220px'),
                                     ('État', '110px'), ('', '40px')], [
    ('t03-p1', [J_DEPART, (case(False),), 'Espèces', '', SOLDE_2, NOM, VALIDE, ANNULER], ''),
    ('t03-p2', [J_CONF, (case(True),), 'MTN Mobile Money', REF_MOMO, ACOMPTE, NOM, VALIDE, ANNULER], ''),
], total=[('', '')] * 4 + [(TOTAL_2, 't03-p-tot')] + [('', '')] * 3, ajouter='Ajouter une ligne',
    classe_='t03-regl masque')
FEUILLE_FOLIO2 = (
    titre_fiche(FOLIO)
    + deux_colonnes(
        groupe('Séjour', [champ('Client', CLIENT, lien_=True), champ('Réservation', RESA, lien_=True),
                          champ('Séjour', 'Parti'), champ('Arrivée', demo.ARRIVEE), champ('Départ', demo.DEPART)]),
        groupe('Montants', [champ('Hébergement (HT)', demo.TOTAL_HEB), champ('Services (HT)', SERVICES),
                            champ('Taxe de séjour', TAXE_MT), champ('Total HT', TOTAL_2),
                            champ('Taxes', ZERO), champ('Total TTC', TOTAL_2, 't03-f2-ttc'),
                            champ('Encaissé', ACOMPTE, 't03-f2-paye'),
                            champ('Solde dû', SOLDE_2, 't03-f2-solde'),
                            champ('État facture', 'Partiellement réglé', 't03-f2-etat')]))
    + '<div class="onglets"><span class="onglet actif" id="t03-o-lignes">Lignes du folio</span>'
      '<span class="onglet" id="t03-o-regl">Règlements</span><span class="onglet">Note</span></div>'
    + '<div class="t03-pile">%s%s</div>' % (LIGNES2, REGLEMENTS))
RANG = '%d / %d' % ([f[0] for f in DUS].index('0214') + 1, len(DUS))
V_FOLIO2 = vue_fiche('t03-folio2', cp_fiche('Folios', FOLIO, RANG, stats=[
    ('t03-st-regl2', 'billet', 'Règlements', '1'), ('t03-st-fact', 'document', 'Facture', '')]),
    [bouton('t03-f2-enc', 'Encaisser', 'primaire')], statusbar('t03-f2sb', ['Ouvert', 'Facturé', 'Soldé'], 1),
    FEUILLE_FOLIO2)

# Le folio juste après « Valider le départ » : sans accès aux factures,
# l'action renvoyée est le folio lui-même (hotel_folio.py:329-338), empilé
# sur la réservation. Facturé, « Générer la facture » masqué, bouton
# « Facture », « État facture » ; lignes figées, dans l'ordre de V_FOLIO2.
LIGNES3 = lignes_apres('t03-f3-lignes', 't03-hl')
FEUILLE_FOLIO3 = (
    titre_fiche(FOLIO)
    + deux_colonnes(
        groupe('Séjour', [champ('Client', CLIENT, lien_=True), champ('Réservation', RESA, lien_=True),
                          champ('Séjour', 'Parti'), champ('Arrivée', demo.ARRIVEE), champ('Départ', demo.DEPART)]),
        groupe('Montants', [champ('Hébergement (HT)', demo.TOTAL_HEB), champ('Services (HT)', SERVICES),
                            champ('Taxe de séjour', TAXE_MT), champ('Total HT', TOTAL_2),
                            champ('Taxes', ZERO), champ('Total TTC', TOTAL_2, 't03-f3-ttc'),
                            champ('Encaissé', ACOMPTE),
                            ligne('t03-r3-solde', 'Solde dû', SOLDE_2, 't03-f3-solde'),
                            ligne('t03-r3-etat', 'État facture', 'Partiellement réglé', 't03-f3-etat')],
               identifiant='t03-grp-montants3'))
    + '<div class="onglets"><span class="onglet actif">Lignes du folio</span><span class="onglet">Règlements</span>'
      '<span class="onglet">Note</span></div>' + LIGNES3)
V_FOLIO3 = vue_fiche('t03-folio3', cp_fiche(TDB + ' / ' + RESA, FOLIO, '', stats=[
    ('t03-st-regl3', 'billet', 'Règlements', '1'), ('t03-st-fact3', 'document', 'Facture', '')]),
    [bouton('t03-f3-enc', 'Encaisser', 'primaire')], statusbar('t03-f3sb', ['Ouvert', 'Facturé', 'Soldé'], 1),
    FEUILLE_FOLIO3)

# ---------------------------------------------------------------- les assistants --


def _encaisser(ident, solde, montant, acompte, date):
    """L'assistant « Encaisser un règlement », pré-rempli avec le solde dû."""
    gauche = (m_champ('Folio', lien(FOLIO)) + m_champ('Client', lien(CLIENT))
              + m_champ('Solde dû actuel', e(solde)))
    droite = (m_champ('Montant à encaisser', entree(ident + '-montant', '', montant))
              + m_champ('Acompte', case(acompte, ident + '-case'), ident + '-ch-acompte')
              + m_champ('Moyen de paiement', entree(ident + '-moyen', '', 'Espèces'))
              + m_champ('Réf. transaction', entree(ident + '-ref', 'ID transaction Mobile Money'), ident + '-ch-ref')
              + m_champ('Date', e(date)))
    corps = ('<div class="m-grille"><div>%s</div><div id="%s-droite">%s</div></div>'
             '<div class="m-grille un t03-note">%s</div>' % (gauche, ident, droite, m_champ('Note', entree(ident + '-note'))))
    return assistant(ident, 'Encaisser un règlement', corps, [(ident + '-ok', 'Encaisser', 'primaire', None),
                                                              (ident + '-non', 'Annuler', 'gris', None)], haut=110)


AS_ACOMPTE = _encaisser('t03-ac', TOTAL_1, TOTAL_1, True, J_CONF)
AS_SOLDE = _encaisser('t03-so', SOLDE_2, SOLDE_2, False, J_DEPART)
AS_DEPART = assistant('t03-co', 'Check-out — ' + RESA, (
    '<div class="m-grille"><div><div class="grp-t">Séjour</div>%s%s%s%s</div>'
    '<div><div class="grp-t">Folio</div>%s%s%s%s%s</div></div>'
    '<div class="t03-info">Un solde reste dû : vous pourrez l\'encaisser depuis le folio après la facturation '
    '(bouton « Encaisser »).</div>'
    % (m_champ('Réservation', lien(RESA)), m_champ('Client', lien(CLIENT)),
       m_champ('Départ prévu', e(demo.DEPART)), m_champ('Départ réel', entree('t03-co-dep', '', DEPART_REEL)),
       m_champ('Folio', lien(FOLIO)), m_champ('Total TTC', e(TOTAL_2)),
       m_champ('Déjà encaissé', e(ACOMPTE)), m_champ('Solde dû', '<b>%s</b>' % e(SOLDE_2), 't03-co-solde'),
       m_champ('Générer la facture', case(True)))),
    [('t03-co-ok', 'Valider le départ', 'primaire', None), ('t03-co-non', 'Annuler', 'gris', None)], haut=110)

# --------------------------------------------------------------- la fenêtre --
ECRAN = navigateur(fenetre_muk('app-t03', 'Hôtel', MENUS, [V_RESA, V_FOLIO, V_FOLIO3, V_LISTE, V_FOLIO2],
                               actif=MENU_RECEPTION, societe=demo.SOCIETE, initiale=NOM[0], avatar='#185FA5',
                               apps=APPS, app_active='Hôtel', calques=AS_ACOMPTE + AS_DEPART + AS_SOLDE))
ECRAN = remplacer(ECRAN, '<span class="menu actif">%s</span>' % MENU_RECEPTION,
                  '<span class="menu actif" id="t03-m-fd">%s</span>' % MENU_RECEPTION)
ECRAN = remplacer(ECRAN, '<span class="menu">Facturation</span>', (
    '<span class="menu t03-m" id="t03-m-fact">Facturation<span class="t03-dd masque" id="t03-dd">'
    '<span id="t03-dd-folios">Folios</span><span>Règlements</span><span>Registre de police (impression)</span>'
    '</span></span>'))

CSS = '''
#app-t03 .o-haut { z-index: 6; font-size: 17px; gap: 22px; }
#app-t03 .o-haut .nom-app { font-size: 21px; }
#app-t03 .o-haut .menu.actif { font-weight: 600; }
#app-t03 .st-et { color: #5C636A; }
#app-t03 .st-et.actif { color: var(--o-texte); }
.t03-cache { display: none !important; }
.t03-lien { color: var(--o-lien); }
.t03-m { position: relative; }
.t03-dd { position: absolute; left: -18px; top: 42px; width: 390px; padding: 8px 0; border-radius: 6px; background: #fff;
  border: 1px solid var(--o-filet); box-shadow: 0 14px 34px rgba(0,0,0,.24); display: flex; flex-direction: column; }
.t03-dd span { padding: 12px 22px; font-size: 19px; font-weight: 400; color: var(--o-texte); white-space: nowrap; }
.t03-sbc { position: absolute; right: 22px; top: 11px; height: 44px; padding: 0 22px; display: flex; align-items: center;
  border-radius: 4px; background: var(--o-gris); color: #495057; font-size: 19px; }
.bandeau.t03-ok { background: #D4EDDA; border-color: #C3E6CB; color: #155724; }
.bandeau.t03-ok .act { color: #155724; margin-left: 12px; }
.t03-req .l { font-weight: 700; }
.t03-note { margin-top: 6px; }
.modale .case { display: inline-flex; }
.t03-info { margin-top: 16px; padding: 14px 20px; border-radius: 6px; background: #D1ECF1; border: 1px solid #BEE5EB;
  color: #0C4A55; font-size: 19px; line-height: 1.45; }
.t03-lignes .t-ligne { font-size: 17px; }
.t03-lignes .t-ligne.t03-nuit { color: #0B6375; }
.t03-lignes .t-ligne .puce { height: 28px; font-size: 15px; padding: 0 11px; }
.t03-lignes .t-ligne.t03-edit { background: #F1F5F8; }
.t03-cell { position: relative; height: 36px; border-bottom: 1px solid var(--o-prim); overflow: hidden; }
.t03-cell.focus { border-bottom: 2px solid var(--o-prim); }
.t03-cell .ph, .t03-cell .val { position: absolute; left: 2px; top: 50%; transform: translateY(-50%); white-space: nowrap; }
.t03-cell .ph { color: #6C757D; }
.t03-cell.d .val { left: auto; right: 2px; }
.t03-lignes .t-ligne:not(.t03-edit) .t03-cell { border-bottom-color: transparent; }
#app-t03 .m-ch .v .entree { font-size: 20px; overflow: hidden; }
.t03-pile { position: relative; }
.t03-pile .t03-regl { position: absolute; left: 0; right: 0; top: 0; min-height: 270px; background: #fff; }
.t03-regl .case i { width: 20px; height: 20px; }
#t03-ch .case { display: flex; align-items: center; }
#t03-ch .case i { width: 18px; height: 18px; border-color: #CED4DA; }
.t03-ech { color: #3F6A83; display: inline-flex; width: 22px; height: 22px; }
.t03-ech svg { width: 22px; height: 22px; }
.t03-x { width: 22px; height: 22px; display: inline-flex; color: #6C757D; }
.t03-x svg { width: 100%; height: 100%; }
#t03-f-ttc, #t03-f-solde, #t03-f2-ttc, #t03-f2-solde, #t03-f3-ttc, #t03-f3-solde { font-weight: 700; }
#b-facture { max-width: 760px; }
.liste .ligne.t03-muet { color: #6C757D; }
.t03-panneau { position: absolute; right: -1px; top: 58px; width: 1010px; display: grid; grid-template-columns: repeat(3, 1fr);
  padding: 14px 4px 10px; background: #fff; border: 1px solid var(--o-filet); border-radius: 6px; z-index: 8;
  box-shadow: 0 14px 34px rgba(0,0,0,.20); color: var(--o-texte); }
.t03-pc { padding: 0 18px; border-left: 1px solid var(--o-filet); }
.t03-pc:first-child { border-left: 0; }
.t03-ph { display: flex; align-items: center; gap: 10px; height: 42px; font-size: 19px; font-weight: 700; }
.t03-ph svg { width: 20px; height: 20px; flex: none; }
.t03-pi { position: relative; padding: 9px 0 9px 28px; font-size: 18px; white-space: nowrap; }
.t03-coche { position: absolute; left: 4px; color: var(--o-prim); font-weight: 700; }
.t03-sep { height: 1px; margin: 8px 0; background: var(--o-filet); }
#t03-liste .liste .tete { height: 46px; font-size: 18px; }
#t03-liste .liste .ligne { height: 38px; font-size: 17px; }
#t03-liste .liste .ligne .puce { height: 26px; font-size: 15px; padding: 0 10px; }
#t03-liste .liste .total { height: 44px; font-size: 18px; }
'''

TUTORIEL = {
    'slug': 't03-folio',
    'profil': 't03_folio',
    'numero': 3,
    'titre': 'Un séjour, une note, une facture',
    'fonction': 'Le folio du séjour',
    'personnage': (NOM, ROLE),
    'accroche': {
        'kicker': 'La note du séjour',
        'question': 'Que doit *vraiment* le client qui part ?',
        'douleurs': [('pieces', 'Le client sort sa monnaie à chaque repas'),
                     ('telephone', 'Le Mobile Money absent des moyens de paiement du logiciel'),
                     ('calculatrice', 'La taxe de séjour ajoutée à la main'),
                     ('cahier', "L'acompte à déduire de tête au départ"),
                     ('sablier', 'Une note oubliée au départ : un encaissement à courir après')],
        'voix': "Que doit vraiment le client qui part ? Les nuitées, l'acompte en Mobile Moni, les petits-déjeuners, "
                "la taxe de séjour : chacun tient un bout de la note.",
    },
    'revelation': {
        'promesse': "Nuitées, taxe de séjour, extras et acomptes sur un seul folio, et une seule facture au départ.",
        'voix': "Avec Aïte haousse : un séjour, une note, une facture.",
    },
    'temps': ['Ouvrir', 'Encaisser', 'Suivre', 'Clôturer'],
    'app': 'app-t03',
    'ecran': ECRAN,
    'vues_initiales': {'odoo': 't03-resa'},
    'bulles': {
        'b-folio': "Le folio s'est ouvert tout seul à la confirmation : une seule note pour tout le séjour.",
        'b-acompte': "Cochée toute seule : la cliente n'est pas encore arrivée.",
        'b-taxe': "La taxe de séjour se calcule seule, selon les étoiles, sur sa propre ligne, sans TVA.",
        'b-facture': "La facture est créée et validée toute seule, avec les lignes du folio, une par une.",
        'b-du': "L'acompte du 14/10 est déjà déduit.",
        'b-solde': "Solde à zéro : le folio passe à Soldé, sans un clic de plus.",
    },
    'reactions': {
        'r-fin': "Une note, une facture, deux règlements : tout est tracé.",
    },
    'etapes': [
        {'temps': 0, 'titre': 'Confirmée : le folio est ouvert',
         'texte': 'La réservation confirmée a ouvert son folio : nuitées et taxe de séjour déjà comptées.',
         'voix': "Le matin, Mireille vient d'enregistrer la réservation d'Estelle Ngono : deux nuits en chambre "
                 "Confort, confirmée d'office. Le folio du séjour s'est ouvert aussitôt, nuitées et taxe de séjour "
                 "déjà comptées : cent deux mille francs.",
         'gestes': [pause(0.3), anneau('#t03-sbc', d=1.0), anneau('#t03-grp-sejour', d=1.3),
                    zoom('#t03-st-folio', s=1.45, d=0.8), bulle('b-folio', '#t03-st-folio', cote='bas', d=2.8),
                    pause(2.5), dezoom(d=0.6)]},
        {'temps': 1, 'titre': "L'acompte en Mobile Money",
         'texte': 'MTN Mobile Money ou Orange Money, avec la référence de la transaction.',
         'voix': "Estelle verse un acompte par MTN Mobile Moni. La case Acompte est déjà cochée, la cliente n'est pas "
                 "encore arrivée ; Mireille saisit le montant et la référence de la transaction.",
         'gestes': [clic('#t03-b-acompte'), ouvrir('t03-ac'), anneau('#t03-ac-ch-acompte', d=1.0),
                    bulle('b-acompte', '#t03-ac-case', cote='bas', d=2.4), pause(2.1),
                    saisir('t03-ac-montant', ACOMPTE), choisir('t03-ac-moyen', 'MTN Mobile Money'),
                    classe('#t03-ac-ch-ref', ajouter=['t03-req']), saisir('t03-ac-ref', REF_MOMO), pause(0.4),
                    clic('#t03-ac-ok'), fermer('t03-ac'), texte('#t03-st-folio-v', SOLDE_1),
                    anneau('#t03-st-folio', d=1.4)]},
        {'temps': 2, 'titre': 'Le folio : toute la note',
         'texte': 'Acompte, solde dû calculé en direct, nuitées et taxe de séjour sur leurs lignes.',
         'voix': "Un clic sur Folio, et toute la note est là : l'acompte encaissé, le solde dû recalculé en direct, "
                 "puis les lignes du séjour : les deux nuitées, et la taxe de séjour sur sa propre ligne, sans TVA.",
         'gestes': [clic('#t03-st-folio', d=0.6), vue('t03-folio'), pause(0.2), zoom('#t03-grp-montants', s=1.45, d=0.8),
                    anneau('#t03-r-paye', d=1.1), anneau('#t03-r-solde', d=1.3), dezoom(d=0.6),
                    defiler('#t03-folio-defil', -340, d=0.8), anneau('#t03-fl1', d=1.1), anneau('#t03-fl2', d=1.0),
                    bulle('b-taxe', '#t03-fl2', cote='bas', d=2.6), pause(2.2)]},
        {'temps': 2, 'titre': 'Un extra pendant le séjour',
         'texte': 'Ajouter une ligne, choisir le service : libellé, prix et solde dû suivent.',
         'voix': "Le lendemain, quatre petits-déjeuners buffet. Mireille ajoute une ligne et choisit le service : "
                 "libellé et prix se remplissent, et le solde dû suit aussitôt.",
         'gestes': [texte('#t03-f-sejour', 'Arrivé'), clic('#t03-lignes-ajout', fx=0.1),
                    classe('#t03-fl3', retirer=['t03-cache']), zoom('#t03-lignes', s=1.25, d=0.8),
                    choisir('t03-svc', SERVICE), texte('#t03-fl3-lib', SERVICE, avec=True),
                    texte('#t03-fl3-pu', PDJ, avec=True), texte('#t03-fl3-st', PDJ, avec=True),
                    texte('#t03-fl3-tt', PDJ, avec=True), pause(0.6), saisir('t03-qte', '4,00'),
                    texte('#t03-fl3-st', SERVICES), texte('#t03-fl3-tt', SERVICES, avec=True),
                    texte('#t03-lt-ht', TOTAL_2, avec=True), texte('#t03-lt-ttc', TOTAL_2, avec=True),
                    pause(0.6), classe('#t03-fl3', retirer=['t03-edit']), dezoom(d=0.6),
                    texte('#t03-f-serv', SERVICES), texte('#t03-f-ht', TOTAL_2, avec=True),
                    compter('#t03-f-ttc', 102000, 112800, d=0.8, apres=NBSP + 'FCFA'),
                    compter('#t03-f-solde', 57000, 67800, d=0.8, apres=NBSP + 'FCFA', avec=True),
                    anneau('#t03-r-solde', d=1.5)]},
        {'temps': 3, 'titre': 'Check-out : une seule facture',
         'texte': 'Valider le départ : la facture se crée et se valide seule, le folio passe à Facturé.',
         'voix': "Le jour du départ, Estelle est au comptoir. Mireille lance le check-out : l'assistant récapitule "
                 "le total, l'acompte et le solde. Valider le départ : la facture est créée et validée toute seule, "
                 "et l'écran reste sur le folio, passé à Facturé, avec son bouton Facture. L'acompte est déjà "
                 "déduit, la facture est partiellement réglée : il reste soixante-sept mille huit cents francs.",
         'gestes': [clic('#t03-fil-res'),
                    # la réservation, encore cachée, a vécu le séjour : arrivée, fiches remplies (t06)
                    cacher('#t03-resa-ga', d=0.05, avec=True), montrer('#t03-resa-gb', d=0.05, y=0, avec=True),
                    texte('#t03-sbc-t', 'Arrivé', avec=True), classe('#t03-cireel', retirer=['t03-cache'], avec=True),
                    classe('#t03-bandeau', retirer=['t03-cache'], avec=True),
                    defiler('#t03-resa-defil', 52, d=0.05, avec=True),
                    texte('#t03-st-fiches-v', '2/2', avec=True), texte('#t03-st-folio-v', SOLDE_2, avec=True),
                    vue('t03-resa'), clic('#t03-b-checkout', d=0.6), ouvrir('t03-co'),
                    anneau('#t03-co-solde', d=1.0), clic('#t03-co-ok', d=0.6), fermer('t03-co'), vue('t03-folio3'),
                    pause(0.5), anneau('#t03-f3sb-1', d=1.1),
                    zoom('#t03-st-fact3', s=1.45, d=0.8), bulle('b-facture', '#t03-st-fact3', cote='bas', d=2.6),
                    pause(2.0), dezoom(d=0.6),
                    defiler('#t03-folio3-defil', -160, d=0.6), zoom('#t03-r3-solde', s=1.4, d=0.8), anneau('#t03-r3-solde', d=1.0),
                    bulle('b-du', '#t03-r3-solde', cote='gauche', d=2.2), anneau('#t03-r3-etat', d=1.0),
                    pause(0.6), dezoom(d=0.6)]},
        {'temps': 3, 'titre': "Les soldes dus d'un coup d'œil",
         'texte': 'Facturation, Folios, filtre Avec solde dû : les notes qui restent à encaisser.',
         'voix': "Avant qu'Estelle ne reparte, Mireille ouvre la liste des folios. Le filtre Avec solde dû ne garde que "
                 "les notes à régler : celle d'Estelle attend soixante-sept mille huit cents francs.",
         'gestes': [clic('#t03-m-fact'), classe('#t03-m-fd', retirer=['actif'], avec=True),
                    classe('#t03-m-fact', ajouter=['actif'], avec=True), montrer('#t03-dd', d=0.25, y=-6),
                    clic('#t03-dd-folios', d=0.5), cacher('#t03-dd', d=0.15), vue('t03-liste'), pause(0.4),
                    clic('#t03-liste-rech .deroule', d=0.6), montrer('#t03-panneau', d=0.25, y=-6),
                    clic('#t03-pf-solde', d=0.5), classe('#t03-pf-coche', retirer=['t03-cache']),
                    classe('#t03-fac', retirer=['t03-cache'], avec=True)]
                   + [classe('#t03-l-' + f[0], ajouter=['t03-cache'], avec=True) for f in FOLIOS if f not in DUS]
                   + [texte('#t03-pager', PAGER_DU, avec=True), classe('#t03-lt', retirer=['t03-cache'], avec=True),
                      pause(0.5), cacher('#t03-panneau', d=0.2), curseur('#t03-l-0214', fx=0.3, d=0.5),
                      survol('#t03-l-0214'), anneau('#t03-l-0214', d=1.6)]},
        {'temps': 3, 'titre': 'Soldé, et tout est tracé',
         'texte': 'Encaisser le solde : le folio passe à Soldé ; chaque règlement reste dans son onglet.',
         'voix': "Mireille ouvre le folio : Encaisser, en espèces. Le solde tombe à zéro, et le folio passe à Soldé, "
                 "tout seul. Dans l'onglet Règlements, l'acompte Mobile Moni et le solde restent tracés, avec la "
                 "personne qui les a encaissés.",
         'gestes': [clic('#t03-l-0214', fx=0.3, d=0.6), vue('t03-folio2'), clic('#t03-f2-enc', d=0.6), ouvrir('t03-so'), pause(0.3),
                    clic('#t03-so-ok', d=0.6), fermer('t03-so'), cacher('#t03-folio2-ga', d=0.2),
                    classe('#t03-f2sb-1', retirer=['actif'], avec=True),
                    classe('#t03-f2sb-2', ajouter=['actif'], avec=True),
                    texte('#t03-f2-paye', TOTAL_2, avec=True), texte('#t03-f2-solde', ZERO, avec=True),
                    texte('#t03-f2-etat', 'Payé', avec=True), texte('#t03-st-regl2-v', '2', avec=True),
                    anneau('#t03-f2sb', d=1.4), bulle('b-solde', '#t03-f2sb', cote='bas', d=2.4, avec=True),
                    pause(0.5), defiler('#t03-folio2-defil', -380, d=0.7), clic('#t03-o-regl', d=0.5),
                    classe('#t03-o-lignes', retirer=['actif']), classe('#t03-o-regl', ajouter=['actif'], avec=True),
                    cacher('#t03-f2-lignes', d=0.15, avec=True), montrer('#t03-f2-regl', d=0.3, y=0, avec=True),
                    anneau('#t03-p2', d=1.3), reaction('r-fin', d=2.8), pause(1.9)]},
    ],
    'resultats': {
        'titre': 'Toute la note du séjour, une seule facture au départ',
        'cartes': [
            {'valeur': '5', 'compter': 5, 'unite': 'moyens', 'icone': 'pieces',
             'texte': 'de paiement sur le folio : MTN Mobile Money, Orange Money, espèces, carte, virement'},
            {'valeur': '1', 'compter': 1, 'unite': 'facture', 'icone': 'document',
             'texte': 'par séjour, générée au départ depuis les lignes du folio'},
            {'valeur': '39', 'compter': 39, 'unite': 'tests', 'icone': 'bouclier',
             'texte': 'automatisés vérifient le folio : nuitées, règlements, facture et état'},
        ],
        'voix': "Cinq moyens de paiement, une seule facture par séjour, et trente-neuf tests automatisés qui vérifient "
                "le folio.",
    },
    'cta': {
        'appel': 'Demandez votre démonstration',
        'suivant': 'Bar et restaurant sur la note de chambre',
        'voix': "Aïte haousse, par Aïte Consulting. Demandez votre démonstration. Prochain tutoriel : le bar et le "
                "restaurant sur la note de chambre.",
    },
    'vignette': {'etape': 4, 'apres': 9.0},
    'css': CSS,
}
