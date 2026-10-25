# -*- coding: utf-8 -*-
"""Chapitre 1 — La journée de la réception.

Source : fiche de recette n° 1 « La journée de la réception »
(docs/GUIDE_RECETTE_UAT.md : tableau de bord de la réception, arrivées du
jour, planning, réservation, folio, réservation rapide), complétée par les
nouveautés de la vague 1 jouées au check-in (registre des clients,
aite_guest_registry) et sur le folio (taxe de séjour, aite_city_tax).

Libellés relevés dans (livraison 4, écarts n° 37-77) :
- aite_hotel_management/views/hotel_menus.xml (menu « Réception »,
  anciennement « Front Desk », écart n° 42 ; barre ecrans.MENUS_MUK) ;
- static/src/xml/hotel_dashboard.xml:30-32 (« Tableau de bord — Réception »,
  « Occupation, arrivées & départs, plan des chambres · ») et :86-127 (cartes :
  « 13 chambres occupées sur 20 », « chambres à libérer aujourd'hui », « Prix
  moyen par nuit (ADR) », « Revenu par chambre disponible (RevPAR) », mêmes
  libellés que la Direction), static/src/js/views/hotel_dashboard_view.js:188-201
  (variations « ▲ +7,3 % vs période précédente », écart n° 62) et
  services/hotel_utils.js (fmtPct « 63,9 % », fmtCount, fmtMoney) ;
- views/hotel_reservation_views.xml (liste : colonne « Canal » en badge,
  visible par défaut entre « Solde folio » et « Registre », écart n° 58 ;
  boutons « Non présenté », écart n° 42, « Encaisser un acompte », statusbar),
  hotel_folio_views.xml (boutons « Encaisser » et « Générer la facture » de
  la réception, « Annuler » réservé au Responsable :43-46 ; « Taxes » :79-84),
  aite_city_tax/views/hotel_folio_views.xml:17-23 (« Recalculer la taxe de
  séjour », Responsable seulement, non montré), models/hotel_folio.py:263 (« Nuitée 204 (Confort) —
  14/10/2026 → 16/10/2026 », écart n° 37), wizard/hotel_payment_wizard*.py|xml
  (« Encaisser un règlement », moyens de paiement), wizard/
  hotel_booking_wizard_views.xml et .py (« Réservation rapide », colonne
  « Réserver », champs « Client », « Canal » et « Confirmer immédiatement »
  après la recherche, bouton « Réserver » ; écarts n° 45 et 56) ;
- aite_guest_registry/views/hotel_reservation_views.xml (badge « Aucune
  fiche » neutre avant l'arrivée, écart n° 54 ; bouton intelligent « Fiches
  d'enregistrement » et bouton « Imprimer les fiches », relecture de
  l'intégration ; bandeau « Registre des clients : ») et
  models/hotel_reservation.py:77-102 (« 1 fiche à compléter · 1 occupant sans
  fiche », accordé, écarts n° 44 et 47) ; aite_city_tax (ligne « Taxe de
  séjour »).

Données harmonisées avec la série (fiche d'harmonisation, demo.py et
scenarios/t01_reception.py, qui rejoue les mêmes écrans le même jour) :
mercredi 14/10/2026, 20 chambres vendables, sans TVA. Tableau de bord : les
chiffres de t01 (13 / 20 chambres ce soir, 179 nuitées du 01/10 au 14/10 sur
20 × 14 = 280, ADR 45 000 FCFA, RevPAR 8 055 000 / 280 = 28 768 FCFA) ; trois
arrivées confirmées, celles de la liste (Estelle Ngono est déjà réservée).
Liste des arrivées triée comme le code (checkin_date desc : Claire Durand à
18:00 en tête) ; seule la colonne « Total hébergement » porte une somme
(hotel_reservation_views.xml:5-33). Canal : « Direct / comptoir » pour Estelle
Ngono (fiche d'harmonisation) et Martin Ebode, « Téléphone / WhatsApp » pour
Claire Durand, comme scenarios/t01_reception.py (demo.py ne fixe pas le canal). Planning : les séjours de
scenarios/t02_planning.py (SEJOURS), chambres de la liste commune des
20 chambres ; « aujourd'hui » = le 14 (index 16 des 35 cases). Réservation :
canal « Direct / comptoir », acompte encaissé avant le check-in (la case
« Acompte » est cochée tant que le client n'est pas arrivé,
hotel_payment_wizard.py:36-41), montant proposé = solde du folio
(hotel_folio.py:337, 102 000 FCFA), référence MTN numérique 8742156309,
check-in réel 14:06:12. Le bouton « Folio » affiche le solde du folio.
Planning : Réservations → Planning des chambres, le menu actif passe à
« Réservations » (hotel_menus.xml:51-64). Folio ouvert par le bouton
« Folio » : fil d'Ariane « Réservations / RES/2026/0214 », pager « 1 / 1 ».
Anneau du CA par type : couleurs par rang de CA (Confort violet, Standard
vert, Suite Junior bleu, Suite VIP ambre), comme t01.
Réservation rapide : ouverte sur aujourd'hui 14:00 → demain 12:00
(hotel_booking_wizard.py:27-36), Mireille saisit du 20 au 22/10, Suite Junior, 1 adulte : les quatre
suites junior sont libres (t02 SEJOURS) ; colonnes de
wizard/hotel_booking_wizard_views.xml:8-72, comme t01 ; la demande arrive au
téléphone, Mireille passe le canal à « Téléphone / WhatsApp » (par défaut
« Direct / comptoir », hotel_booking_wizard.py:46-55).
« ? » d'aide : Odoo 18 le pose après le libellé d'un champ de formulaire qui
porte un help= (form_label.xml:6, form_label.js:39-50), hors mode debug :
« Nuits » de la réservation (hotel_reservation.py:64-68), « Acompte » de
l'encaissement (hotel_payment_wizard.py:36-40), « Taxe de séjour » du folio
(aite_city_tax/models/hotel_folio.py:56-60), « Type de chambre », « Canal » et
« Confirmer immédiatement » de la réservation rapide (hotel_booking_wizard.py
:36-39, :49-55, :60-63). Le « Canal » de la fiche Réservation n'en a pas
(hotel_reservation.py:70-80, sans help), ni les autres champs rejoués.
Base mono-société, comme celle du client (docs/videos/DESIGN.md ;
base.group_multi_company n'est donné qu'aux utilisateurs de plusieurs
sociétés, res_users.py:1907-1914) : le folio ne montre pas « Hôtel »
(groups="base.group_multi_company", hotel_folio_views.xml:73-74).
« Total TTC » et « Solde dû » portent class="fw-bold" (hotel_folio_views.xml
:83 et :85) : c'est la valeur qui est en gras ; le libellé, en lecture seule,
reste en graisse normale (form_controller.scss:589-600), comme t04.
"""

import demo
from ecrans import (MENUS_MUK, NBSP, NNBSP, assistant, bouton, calendrier, cell_puce, champ, compte, cp_fiche,
                    deux_colonnes, e, entier, entree, fcfa, fenetre, graphe_anneau, graphe_courbe, graphes, groupe, icone,
                    interrupteur, kpi, lien, m_champ, m_champs, num, onglets, pct, statusbar, table, tdb_entete,
                    tdb_filtres, tdb_section, titre_fiche, vue_fiche, vue_liste, vue_tdb)
from moteur import (animer, anneau, cacher, choisir, clic, classe, compter, defiler, fermer, montrer, ouvrir,
                    pause, saisir, survol, texte, vue)

NOM, ROLE = demo.POSTES['reception']
MENUS = MENUS_MUK['hotel_reception']
VS = 'vs période précédente'        # libellé des variations (hotel_dashboard_view.js:198)

# ---------------------------------------------- tableau de bord Réception --
# Les chiffres du tableau de bord (hotel_dashboard.py:269-356), les mêmes que t01 :
# période « Ce mois » du 01/10 au 14/10, 20 chambres × 14 jours.
CHAMBRES_VENDABLES, JOURS = 20, 14
DISPO = CHAMBRES_VENDABLES * JOURS
PAR_JOUR = [11, 12, 13, 13, 14, 15, 14, 12, 12, 12, 13, 14, 11, 13]     # chambres occupées, nuit du 01/10 au 14/10
NUITEES = sum(PAR_JOUR)
TYPES_CA = {'STD': ('Standard', 35000), 'CFT': ('Confort', 45000), 'SJR': ('Suite Junior', 75000),
            'VIP': ('Suite VIP', 120000)}
NUITEES_TYPE = {'STD': 78, 'CFT': 84, 'SJR': 11, 'VIP': 6}
# L'anneau colore les types par rang de CA décroissant (hotel_dashboard.py:491-505, trié) avec la palette
# primary, success, info, warning (hotel_dashboard_view.js:322-337, hotel_utils.js:10-14), comme t01 (PALETTE_CA).
PALETTE_CA = ['#714B67', '#3B6D11', '#185FA5', '#854F0B']
TYPES_RANG = sorted(NUITEES_TYPE, key=lambda k: -NUITEES_TYPE[k] * TYPES_CA[k][1])
assert TYPES_RANG == ['CFT', 'STD', 'SJR', 'VIP']
CA_HEB = sum(n * TYPES_CA[k][1] for k, n in NUITEES_TYPE.items())
CA_SERV = 440000
OCCUPEES = 13                                                           # ce soir


def _sp(t):
    return t.replace(NBSP, ' ').replace(NNBSP, ' ')


def aide(html):
    """Le « ? » qu'Odoo 18 pose après le libellé d'un champ qui porte une aide (help= du modèle ; form_label.xml:6) :
    ajouté au libellé d'un ecrans.champ ou d'un ecrans.m_champ, dont le premier span est le libellé."""
    assert html.startswith(('<div class="ch">', '<div class="m-ch"'))
    return html.replace('</span>', '<sup class="c1-aide">?</sup></span>', 1)


def tdb_fcfa(n):
    """fmtMoney de hotel_utils.js : toLocaleString fr-FR (espace fine) et le symbole de la société."""
    return fcfa(n, tdb=True)


assert (NUITEES, CA_HEB, CA_HEB / NUITEES) == (179, 8055000, 45000)
assert _sp(pct(NUITEES * 100.0 / DISPO) + tdb_fcfa(CA_HEB / DISPO) + pct(OCCUPEES * 100.0 / CHAMBRES_VENDABLES)) == (
    '63,9 %28 768 FCFA65,0 %')

FRONT = vue_tdb('c1-front', (
    tdb_entete('Tableau de bord — Réception', 'Occupation, arrivées & départs, plan des chambres · ' + demo.SOCIETE,
               'Nouvelle réservation')
    + tdb_filtres([('Période', ["Aujourd'hui", '7 derniers jours', 'Ce mois', 'Mois dernier'], 2)])
    + tdb_section('Photo du jour', [
        kpi('c1-k-occ', 'Occupation ce soir', pct(OCCUPEES * 100.0 / CHAMBRES_VENDABLES),
            compte(OCCUPEES, 'chambre occupée', 'chambres occupées') + ' sur ' + entier(CHAMBRES_VENDABLES, tdb=True),
            'violet'),
        kpi('c1-k-arr', 'Arrivées attendues', '3', 'réservations confirmées du jour', 'bleu'),
        kpi('c1-k-dep', 'Départs prévus', '2', "chambres à libérer aujourd'hui", 'ambre'),
        kpi('c1-k-pre', 'Clients présents', '22', compte(OCCUPEES, 'séjour en cours', 'séjours en cours'), 'vert')])
    + tdb_section('Performance de la période', [
        kpi('c1-k-to', "Taux d'occupation", pct(NUITEES * 100.0 / DISPO),
            compte(NUITEES, 'nuitée vendue', 'nuitées vendues'), None, (7.3, VS)),
        kpi('c1-k-adr', 'Prix moyen par nuit (ADR)', tdb_fcfa(CA_HEB / NUITEES), 'CA hébergement ÷ nuitées vendues',
            None, (2.0, VS)),
        kpi('c1-k-rev', 'Revenu par chambre disponible (RevPAR)', tdb_fcfa(CA_HEB / DISPO),
            'par chambre disponible, vendue ou non', None, (9.4, VS)),
        kpi('c1-k-ca', "Chiffre d'affaires (HT)", tdb_fcfa(CA_HEB + CA_SERV),
            'Hébergement %s · Services %s' % (tdb_fcfa(CA_HEB), tdb_fcfa(CA_SERV)), None, (9.2, VS))])
    + graphes(graphe_courbe('c1-g-occ', "Taux d'occupation par jour",
                            [n * 100.0 / CHAMBRES_VENDABLES for n in PAR_JOUR],
                            etiquettes=['01/10', '03/10', '05/10', '07/10', '09/10', '11/10', '14/10']),
              graphe_anneau('c1-g-type', 'CA hébergement par type de chambre',
                            [(TYPES_CA[k][0], NUITEES_TYPE[k] * TYPES_CA[k][1], PALETTE_CA[i])
                             for i, k in enumerate(TYPES_RANG)]))
), initiale=True)

# ---------------------------------------------------- Arrivées du jour --
COLS_ARR = [('Référence', '146px'), ('Client', '136px'), ('Arrivée', '200px'), ('Départ', '200px'), ('Nuits', '50px', 'd'),
            ('Nb chambres', '88px', 'd'), ('Total hébergement (HT)', '150px', 'd'), ('Solde folio', '134px', 'd'),
            ('Canal', '206px'), ('Registre', '134px'), ('État', '1fr')]
# Canal (badge sans décoration, gris « text-bg-300 » d'Odoo 18) ; Registre « Aucune fiche » neutre avant l'arrivée.
CANAL = {demo.RESA: 'Direct / comptoir', 'RES/2026/0209': 'Direct / comptoir', 'RES/2026/0201': 'Téléphone / WhatsApp'}
# Ordre du code (checkin_date desc, puis la plus récente) : Claire Durand (18:00), Estelle Ngono, Martin Ebode.
# Le matin, l'acompte d'Estelle n'est pas encore encaissé : son solde est encore le folio entier (102 000),
# il passe à 57 000 (demo.ARRIVEES) à l'étape de l'acompte.
ORDRE_ARR = ['RES/2026/0201', demo.RESA, 'RES/2026/0209']
SOLDE_MATIN = {demo.RESA: '102 000 FCFA'}
ARRIVEES = vue_liste('c1-arrivees', 'Arrivées du jour', COLS_ARR, [
    {'id': 'c1-a%d' % ORDRE_ARR.index(ref), 'cellules': [
        lien(ref), cli, arr, dep, nuits, ch, num(tot), num(SOLDE_MATIN.get(ref, solde)), cell_puce(CANAL[ref], 'gris'),
        cell_puce('Aucune fiche', 'gris', 'c1-a%d-reg' % ORDRE_ARR.index(ref)), cell_puce('Confirmée', 'info')]}
    for (ref, cli, arr, dep, nuits, ch, tot, solde) in sorted(demo.ARRIVEES, key=lambda a: ORDRE_ARR.index(a[0]))],
    facettes=[('c1-fac-arr', 'Arrivées du jour')], pager='1-3 / 3',
    total=['', '', '', '', '', '', '315 000 FCFA', '', '', '', ''])

# --------------------------------------------------------- Planning --
# Les 35 cases vont du lundi 28/09 au dimanche 01/11 : la case d'index 16 est le mercredi 14/10.
# Séjours de scenarios/t02_planning.py (SEJOURS), une barre par nuit : (semaine, jour, nuits, libellé).
NUMEROS = [28, 29, 30, 1, 2, 3, 4] + list(range(5, 32)) + [1]
assert NUMEROS[16] == 14
SEJOURS_MOIS = [
    (0, 0, 1, '101 · Patrick Nkoulou', '#D5F5E3'), (0, 2, 2, '301 · Armand Mvogo', '#E8D5F0'),
    (0, 3, 2, '102 · Boris Nguema', '#D6EAF8'), (0, 4, 2, '104 · Franck Moukoko', '#FDEBD0'),
    (1, 0, 2, '302 · Sylvie Mbarga', '#FCE4D6'), (1, 1, 3, '205 · Pauline Ekotto', '#D5F5E3'),
    (1, 3, 2, '103 · Esther Mengue', '#E8DAEF'), (1, 4, 3, '401 · Laurent Abega', '#FADBD8'),
    (2, 0, 2, '302 · Gisèle Abanda', '#FCE4D6'), (2, 1, 3, '202 · Brigitte Essomba', '#FDEBD0'),
    (2, 2, 2, '204 · Estelle Ngono', '#F9E79F'), (2, 2, 3, '104 · Martin Ebode', '#D6EAF8'),
    (2, 2, 1, '401 · Claire Durand', '#FADBD8'), (2, 3, 2, '103 · Gaston Mbida', '#D5F5E3'),
    (2, 6, 1, '204 · Joël Kamga', '#E8D5F0'), (3, 0, 1, '204 · Joël Kamga', '#E8D5F0'),
    (3, 2, 2, '102 · Christelle Ndongo', '#D6EAF8'), (3, 3, 2, '302 · Carine Manga', '#FCE4D6'),
    (3, 5, 2, '401 · Aristide Bella', '#FADBD8'), (4, 2, 3, '205 · Blaise Atangana', '#D5F5E3'),
    (4, 4, 2, '104 · Mathieu Nkodo', '#FDEBD0')]


def planning_mois(identifiant, evenements):
    """Le calendrier de ecrans.calendrier, dont chaque semaine grandit avec ses séjours, comme le mois
    d'Odoo 18 (FullCalendar, dayMaxEventRows = event_limit 5 : calendar_arch_parser.js:26) : le 14/10,
    quatre séjours se chevauchent (Brigitte Essomba, Estelle Ngono, Martin Ebode, Claire Durand)."""
    html = calendrier(identifiant, 'octobre 2026', NUMEROS, gris={0, 1, 2, 34}, aujourdhui=16, evenements=[])
    rangs, semaines = {}, {s: '' for s in range(5)}
    for s, j, d, lib, coul in evenements:
        r = 0
        while any(rangs.get((s, k, r)) for k in range(j, j + d)):
            r += 1
        for k in range(j, j + d):
            rangs[(s, k, r)] = True
        semaines[s] += ('<div class="c-ev" style="left:calc(%d * 100%% / 7 + 4px);width:calc(%d * 100%% / 7 - 8px);'
                        'top:%dpx;background:%s"><span class="ell">%s</span></div>' % (j, d, 46 + r * 31, coul, e(lib)))
    hauteurs = [46 + 31 * (1 + max([r for (s_, _, r) in rangs if s_ == s] or [-1])) + 2 for s in range(5)]
    lignes = ' '.join('minmax(%dpx, 1fr)' % h for h in hauteurs)
    couches = ''.join('<div class="c-evs %s-sem" style="position:relative;inset:auto;grid-row:%d;grid-column:1 / span 7">'
                      '%s</div>' % (identifiant, s + 1, semaines[s]) for s in range(5))
    vide = '<div class="c-evs" id="%s-evs"></div>' % identifiant
    assert html.count(vide) == 1 and html.count('<div class="c-grille">') == 1
    return (html.replace(vide, couches)
            .replace('<div class="c-grille">', '<div class="c-grille" style="grid-template-rows:%s">' % lignes))


PLANNING = planning_mois('c1-planning', SEJOURS_MOIS)

# ------------------------------------------------------- Réservation --
STATUTS = ['Brouillon', 'Confirmée', 'Arrivé', 'Parti']
# Les montants du séjour, comme t01 : 2 nuits × 45 000 + taxe 2 adultes × 2 nuits × 3 000 ; acompte de 45 000.
TOTAL_RESA = '102 000 FCFA'
ACOMPTE_MT = '45 000 FCFA'
SOLDE_1 = '57 000 FCFA'
REF_MOMO = '8742156309'
assert SOLDE_1 == demo.ARRIVEES[0][7]
CHAMBRES = table([('Type', '1fr'), ('Chambre', '170px'), ('Adultes', '100px', 'd'), ('Enfants', '100px', 'd'),
                  ('Nuits', '80px', 'd'), ('Prix / nuit', '180px', 'd'), ('Sous-total (HT)', '200px', 'd')],
                 [('c1-l1', [demo.TYPE, demo.CHAMBRE, '2', '0', '2', demo.PRIX_NUIT, demo.TOTAL_HEB])],
                 total=['', '', '', '', '', '', demo.TOTAL_HEB])
FEUILLE_RES = (
    titre_fiche(demo.RESA)
    + deux_colonnes(
        groupe('Client', [champ('Client', demo.CLIENT, lien_=True), champ('Téléphone', demo.CLIENT_TEL),
                          champ('E-mail', demo.CLIENT_MAIL), champ('Hôtel', demo.HOTEL, lien_=True)])
        + groupe('Canal & commission', [champ('Canal', 'Direct / comptoir', gras=True)]),
        groupe('Séjour', [champ('Arrivée', demo.ARRIVEE, gras=True), champ('Départ', demo.DEPART, gras=True),
                          aide(champ('Nuits', '2')), champ('Total hébergement (HT)', demo.TOTAL_HEB)])
        + '<div class="masque" id="c1-cireel" style="margin:-12px 0 18px">%s</div>' % champ('Check-in réel', '14/10/2026 14:06:12')
        + groupe('Occupation', [champ('Nb chambres', '1'), champ('Adultes', '2'), champ('Enfants', '0')]))
    + onglets(['Chambres', 'Demandes particulières']) + CHAMBRES)
# Bandeau (aite_guest_registry/views/hotel_reservation_views.xml:29-41) : « Registre des clients » + espace
# insécable + « : », puis registration_hint, accordé (models/hotel_reservation.py:77-102).
BANDEAU = ('<div class="bandeau masque" id="c1-bandeau">%s<b>Registre des clients%s:</b> 1 fiche à compléter · '
           '1 occupant sans fiche — <span class="act">compléter maintenant</span></div>' % (icone('fiche'), NBSP))
B_CONF = [bouton('c1-b-checkin', 'Check-in', 'primaire'), bouton('c1-b-acompte', 'Encaisser un acompte'),
          bouton('c1-b-conf', 'Envoyer la confirmation'), bouton('c1-b-fiches', 'Imprimer les fiches', ico='imprimer'),
          bouton('c1-b-noshow', 'Non présenté'), bouton('c1-b-annuler', 'Annuler')]
B_ARRIVE = [bouton('c1-b-checkout', 'Check-out', 'primaire'), bouton('c1-b-acompte2', 'Encaisser un acompte'),
            bouton('c1-b-conf2', 'Envoyer la confirmation'), bouton('c1-b-fiches2', 'Imprimer les fiches', ico='imprimer'),
            bouton('c1-b-annuler2', 'Annuler')]
RESA = vue_fiche('c1-resa', cp_fiche('Réservations', demo.RESA, '1 / 3', stats=[
    ('c1-st-folio', 'document', 'Folio', TOTAL_RESA), ('c1-st-fiches', 'fiche', "Fiches d'enregistrement", '0/2')]),
    B_CONF, statusbar('c1-sb', STATUTS, 1), FEUILLE_RES, bandeau=BANDEAU, boutons_apres=[B_ARRIVE])

ACOMPTE = assistant('c1-as-acompte', 'Encaisser un règlement', m_champs(
    [m_champ('Folio', e(demo.FOLIO)), m_champ('Client', e(demo.CLIENT)), m_champ('Solde dû actuel', e(TOTAL_RESA))],
    [m_champ('Montant à encaisser', entree('c1-montant', '', TOTAL_RESA)),
     aide(m_champ('Acompte', '<span class="case coche"><i></i></span>')),
     m_champ('Moyen de paiement', entree('c1-moyen', 'Espèces')),
     m_champ('Réf. transaction', entree('c1-ref', 'ID transaction Mobile Money')),
     m_champ('Date', e('14/10/2026'))]),
    [('c1-as-ok', 'Encaisser', 'primaire', None), ('c1-as-non', 'Annuler', 'gris', None)], haut=150)

# ------------------------------------------------------------ Folio --
LIGNES = table([('Date', '150px'), ('Type', '170px'), ('Libellé', '1fr'), ('Qté', '80px', 'd'),
                ('Prix unitaire', '170px', 'd'), ('Sous-total (HT)', '180px', 'd')],
               [('c1-fl1', ['14/10/2026', ('<span>%s</span>' % '<span class="puce info">Nuitée</span>',),
                            ('<span class="lien ell">Nuitée 204 (Confort) — 14/10/2026 → 16/10/2026</span>',),
                            '2,00', demo.PRIX_NUIT, demo.TOTAL_HEB]),
                ('c1-fl2', ['14/10/2026', ('<span><span class="puce orange">Taxe de séjour</span></span>',),
                            ('<span class="ell taxe-l">Taxe de séjour — 4 nuitée(s) × personne (3 ★, Cameroun)</span>',),
                            '4,00', '3 000 FCFA', '12 000 FCFA'])],
               total=['', '', '', '', '', '102 000 FCFA'])
FEUILLE_FOLIO = (
    titre_fiche(demo.FOLIO)
    + deux_colonnes(
        groupe('Séjour', [champ('Client', demo.CLIENT, lien_=True), champ('Réservation', demo.RESA, lien_=True),
                          champ('Séjour', 'Arrivé'), champ('Arrivée', demo.ARRIVEE), champ('Départ', demo.DEPART)]),
        groupe('Montants', [champ('Hébergement (HT)', demo.TOTAL_HEB), champ('Services (HT)', '0 FCFA'),
                            aide(champ('Taxe de séjour', '12 000 FCFA', 'c1-f-taxe')), champ('Total HT', '102 000 FCFA'),
                            champ('Taxes', '0 FCFA'), champ('Total TTC', '<b>102 000 FCFA</b>', html=True),
                            champ('Encaissé', '45 000 FCFA'),
                            champ('Solde dû', '<b>57 000 FCFA</b>', 'c1-f-solde', html=True)]))
    + onglets(['Lignes du folio', 'Règlements', 'Note']) + LIGNES
    + '<div class="note-pied">Les lignes « nuitée » sont synchronisées depuis la réservation ; ajoutez librement des '
      'lignes de service (restaurant, blanchisserie, minibar…).</div>')
# Le folio est ouvert par le bouton « Folio » de la réservation (action_view_folio, hotel_reservation.py:499-510) :
# pile [Réservations, RES/2026/0214, FOL/2026/0214], Odoo 18 montre les deux niveaux précédents
# (breadcrumbs.xml:5-7, slice(-3, -1)) ; pager « 1 / 1 ». Boutons de la réception : « Encaisser » et « Générer la
# facture » ; « Recalculer la taxe de séjour » et « Annuler » sont réservés au Responsable (groups
# group_hotel_manager : aite_city_tax/views/hotel_folio_views.xml:17-23, hotel_folio_views.xml:43-46).
FIL_FOLIO = ('<span class="parent">Réservations<span style="margin:0 9px;color:var(--o-texte-3)">/</span>%s</span>'
             % e(demo.RESA))
_CP_FOLIO = cp_fiche('Réservations', demo.FOLIO, '1 / 1', stats=[('c1-st-regl', 'billet', 'Règlements', '1')])
assert _CP_FOLIO.count('<span class="parent">Réservations</span>') == 1
FOLIO = vue_fiche('c1-folio', _CP_FOLIO.replace('<span class="parent">Réservations</span>', FIL_FOLIO),
                  [bouton('c1-f-enc', 'Encaisser', 'primaire'), bouton('c1-f-fact', 'Générer la facture')],
                  statusbar('c1-fsb', ['Ouvert', 'Facturé', 'Soldé'], 0), FEUILLE_FOLIO)

RAPIDE = assistant('c1-as-rapide', 'Réservation rapide', m_champs(
    # Par défaut : aujourd'hui 14:00 → demain 12:00 (hotel_booking_wizard.py:27-36, _default_checkin / _checkout).
    [m_champ('Hôtel', entree('c1-r-hotel', '', demo.HOTEL)), m_champ('Arrivée', entree('c1-r-arr', '', '14/10/2026 14:00:00')),
     m_champ('Départ', entree('c1-r-dep', '', '15/10/2026 12:00:00'))],
    [aide(m_champ('Type de chambre', entree('c1-r-type', ''))), m_champ('Adultes', entree('c1-r-ad', '', '1')),
     m_champ('Enfants', entree('c1-r-enf', '', '0'))])
    + '<div style="margin-top:14px">%s</div>' % bouton('c1-r-chercher', 'Rechercher les chambres disponibles', 'gris', 'loupe')
    + '<div class="masque" id="c1-r-res" style="margin-top:16px">%s%s</div>' % (table(
        [('Réserver', '100px'), ('Chambre', '130px'), ('Type', '1fr'), ('Étage', '120px'), ('Cap. adultes', '130px', 'd'),
         ('Nuits', '70px', 'd'), ('Prix / nuit', '150px', 'd'), ('Total séjour (HT)', '180px', 'd')],
        [('c1-rr-%s' % n, [('<span>%s</span>' % interrupteur('c1-rr-%s-tg' % n),), '%s [SJR]' % n, 'Suite Junior',
                           '2e étage', '3', '2', '75 000 FCFA', '150 000 FCFA'])
         for n in ('301', '302', '303', '304')], ajouter=None, identifiant='c1-rr'),
        # Après la recherche : le client, le canal (par défaut « Direct / comptoir ») et la confirmation immédiate.
        '<div style="margin-top:16px">%s</div>' % m_champs(
            [m_champ('Client', entree('c1-r-cli', '')), aide(m_champ('Canal', entree('c1-r-canal', '', 'Direct / comptoir')))],
            [aide(m_champ('Confirmer immédiatement', '<span class="case coche"><i></i></span>'))])),
    [('c1-r-fermer', 'Fermer', 'gris', None)], haut=40, largeur=1300)
# « Réserver » n'apparaît qu'après la recherche (invisible="not searched") : deux pieds superposés, le second, avec
# « Réserver » devant « Fermer », remplace le premier après la recherche.
_PIED = '<div class="m-pied">%s</div>' % bouton('c1-r-fermer', 'Fermer', 'gris')
assert RAPIDE.count(_PIED) == 1
RAPIDE = RAPIDE.replace(_PIED, '<div class="m-pied"><div class="pile" style="flex:1"><div id="c1-r-pied1">%s</div>'
                        '<div class="masque" id="c1-r-pied2" style="display:flex;gap:10px">%s%s</div></div></div>'
                        % (bouton('c1-r-fermer', 'Fermer', 'gris'), bouton('c1-r-ok', 'Réserver', 'primaire'),
                           bouton('c1-r-fermer2', 'Fermer', 'gris')))

# Les menus de la barre : grille, nom de l'application, puis Réception, Réservations…
MENU_RECEPTION, MENU_RESAS = '#app-c1 .o-haut .menu:nth-child(3)', '#app-c1 .o-haut .menu:nth-child(4)'
assert MENUS[:2] == ['Réception', 'Réservations']
ECRAN = fenetre('app-c1', 'Hôtel', MENUS, [FRONT, ARRIVEES, PLANNING, RESA, FOLIO], actif='Réception',
                societe=demo.SOCIETE, initiale=NOM[0], calques=ACOMPTE + RAPIDE)

# Le « ? » d'aide, comme celui de scenarios/t01_reception.py (.t1-aide) ; presentation.py réunit le CSS des chapitres.
CSS = '.c1-aide { color: var(--o-lien); font-size: 13px; margin-left: 3px; font-weight: 700; }'

CHAPITRE = {
    'court': 'Réception',
    'poste': 'Réception',
    'titre': 'La journée de la réception',
    'personne': (NOM, ROLE),
    'objectif': "Prendre connaissance de la journée, retrouver une réservation, encaisser un acompte, "
                "faire le check-in et lire le folio du séjour.",
    'voix': "Premier chapitre : la réception. Mireille ouvre sa journée, accueille une cliente, "
            "encaisse un acompte et suit le folio du séjour, sans quitter son écran.",
    'app': 'app-c1',
    'ecran': ECRAN,
    'css': CSS,
    'vues_initiales': {'odoo': 'c1-front'},
    'etapes': [
        {'titre': 'Le tableau de bord', 'texte': "L'occupation du soir, les arrivées, les départs et la performance du mois.",
         'voix': "Le tableau de bord de la réception résume la journée : l'occupation de ce soir, les arrivées "
                 "attendues, les départs prévus, puis la performance du mois, avec le revpar et sa variation sur la "
                 "période précédente.",
         'gestes': [compter('#c1-k-occ-v', 0, 65.0, d=1.0, decimales=1, apres=NBSP + '%'),
                    compter('#c1-k-arr-v', 0, 3, d=0.8, avec=True), compter('#c1-k-dep-v', 0, 2, d=0.8, avec=True),
                    compter('#c1-k-pre-v', 0, 22, d=0.9, avec=True),
                    animer('#c1-g-occ', {'scaleX': 1}, {'scaleX': 0}, d=1.6, avec=True),
                    anneau('#c1-k-arr', d=1.6, decale=0.3), anneau('#c1-k-rev', d=1.8, puis=0.4)]},
        {'titre': 'Les arrivées du jour', 'texte': 'Seules les réservations confirmées qui arrivent aujourd\'hui.',
         'voix': "Le menu Arrivées du jour ne garde que les réservations confirmées qui arrivent aujourd'hui. "
                 "La colonne Canal dit d'où vient chacune, et la colonne Registre qu'aucune fiche n'est encore "
                 "remplie, ce qui est normal avant l'arrivée.",
         'gestes': [clic(MENU_RECEPTION, d=0.6), vue('c1-arrivees'), pause(0.4),
                    anneau('#c1-fac-arr', d=1.3), survol('#c1-a1'), anneau('#c1-a1 .puce.gris', d=1.3, decale=0.3),
                    anneau('#c1-a1-reg', d=1.5)]},
        {'titre': 'Le planning des chambres', 'texte': 'Chaque séjour sur sa chambre, mois par mois.',
         'voix': "Le planning des chambres montre chaque séjour sur sa chambre. En calendrier sur la version "
                 "Community, en Gantt sur Enterprise, sans rien régler.",
         # Réservations → Planning des chambres (hotel_menus.xml:51-64) : le menu actif suit l'écran.
         'gestes': [clic(MENU_RESAS, d=0.5), classe(MENU_RECEPTION, retirer=['actif']),
                    classe(MENU_RESAS, ajouter=['actif']), vue('c1-planning'), animer('#c1-planning .c1-planning-sem', {'autoAlpha': 0}, {'autoAlpha': 1}, d=0.8),
                    pause(1.2), anneau('#c1-planning .auj', d=1.6)]},
        {'titre': "La réservation et l'acompte", 'texte': 'Mobile Money, espèces ou carte, avec la référence de la transaction.',
         'voix': "Voici la réservation d'Estelle Ngono : deux nuits en chambre Confort. À son arrivée, elle verse un "
                 "acompte : le montant, le moyen de paiement, MTN Mobile Moni ici, et la référence de la transaction. "
                 "Le solde du folio baisse aussitôt.",
         'gestes': [vue('c1-resa'), pause(0.4), defiler('#c1-resa-defil', -330, d=0.9), anneau('#c1-l1', d=1.3),
                    defiler('#c1-resa-defil', 0, d=0.7), clic('#c1-b-acompte'), ouvrir('c1-as-acompte'),
                    saisir('c1-montant', ACOMPTE_MT), choisir('c1-moyen', 'MTN Mobile Money'),
                    saisir('c1-ref', REF_MOMO), clic('#c1-as-ok'), fermer('c1-as-acompte'),
                    texte('#c1-st-folio-v', SOLDE_1), anneau('#c1-st-folio', d=1.3)]},
        {'titre': 'Le check-in', 'texte': 'Un clic : la cliente est arrivée, le registre dit ce qui manque.',
         'voix': "Puis un clic sur Check-in : la réservation passe à Arrivé, et un bandeau dit ce qui manque au "
                 "registre des clients : une fiche à compléter, et un occupant sans fiche.",
         'gestes': [clic('#c1-b-checkin'),
                    classe('#c1-sb-1', retirer=['actif']), classe('#c1-sb-2', ajouter=['actif']),
                    cacher('#c1-resa-ga', d=0.2), montrer('#c1-resa-gb', d=0.3, y=0),
                    montrer('#c1-cireel', d=0.3, y=0),
                    montrer('#c1-bandeau', d=0.4, y=-10), defiler('#c1-resa-defil', 52, d=0.4, avec=True),
                    anneau('#c1-bandeau', d=1.6, decale=0.2), anneau('#c1-st-fiches', d=1.3)]},
        {'titre': 'Le folio du séjour', 'texte': 'Nuitées, taxe de séjour calculée seule, règlements et solde dû.',
         'voix': "Le folio rassemble tout le séjour : les nuitées, la taxe de séjour ajoutée toute seule selon les "
                 "étoiles de l'hôtel, hors TVA, puis l'acompte encaissé et le solde dû.",
         # la feuille défile jusqu'aux lignes (le groupe Montants, avec « Taxes », les pousse sous le bas)
         'gestes': [clic('#c1-st-folio'), vue('c1-folio'), pause(0.6), defiler('#c1-folio-defil', -170, d=0.8),
                    anneau('#c1-fl1', d=1.2),
                    anneau('#c1-fl2', d=1.6), anneau('#c1-f-solde', d=1.4)]},
        {'titre': 'La réservation rapide', 'texte': 'Dates, occupation, et les chambres libres en un clic.',
         'voix': "Au téléphone, la réservation rapide suffit : l'hôtel, les dates, le nombre d'adultes, et la "
                 "recherche affiche les chambres disponibles. Le canal passe à Téléphone, pour les statistiques.",
         'gestes': [clic(MENU_RECEPTION, d=0.6), classe(MENU_RESAS, retirer=['actif']),
                    classe(MENU_RECEPTION, ajouter=['actif']), ouvrir('c1-as-rapide'), pause(0.3),
                    choisir('c1-r-arr', '20/10/2026 14:00:00'), choisir('c1-r-dep', '22/10/2026 12:00:00'),
                    choisir('c1-r-type', 'Suite Junior'), pause(0.3),
                    clic('#c1-r-chercher'), montrer('#c1-r-res', d=0.4), cacher('#c1-r-pied1', d=0.2, avec=True),
                    montrer('#c1-r-pied2', d=0.3, y=0, avec=True),
                    anneau('#c1-rr', d=1.4), choisir('c1-r-canal', 'Téléphone / WhatsApp'),
                    anneau('#c1-r-canal', d=1.4)]},
    ],
}
