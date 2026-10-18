# -*- coding: utf-8 -*-
"""Chapitre 1 — La journée de la réception.

Source : fiche de recette n° 1 « La journée de la réception »
(docs/GUIDE_RECETTE_UAT.md : Front Desk, arrivées du jour, planning,
réservation, folio, réservation rapide), complétée par les nouveautés de la
vague 1 jouées au check-in (registre des clients, aite_guest_registry) et
sur le folio (taxe de séjour, aite_city_tax).

Libellés relevés dans : aite_hotel_management/views/hotel_menus.xml,
hotel_reservation_views.xml (boutons et conditions d'affichage, statusbar),
hotel_folio_views.xml, wizard/hotel_payment_wizard_views.xml et
hotel_payment_wizard.py (« Encaisser un règlement », moyens de paiement),
wizard/hotel_booking_wizard_views.xml (« Réservation rapide »),
static/src/xml/hotel_dashboard.xml (Front Desk — Réception) ;
aite_guest_registry/views/hotel_reservation_views.xml (bandeau, bouton
« Fiches clients ») et models/hotel_reservation.py:77-90 (« 1 fiche(s) à
compléter · 1 occupant(s) sans fiche ») ; aite_city_tax (ligne « Taxe de
séjour »). Menus visibles du profil Réception relevés sur une base de recette
(load_menus).

Données harmonisées avec la série (fiche d'harmonisation, demo.py et
scenarios/t01_reception.py, qui rejoue les mêmes écrans le même jour) :
mercredi 14/10/2026, 20 chambres vendables, sans TVA. Front Desk : les
chiffres de t01 (13 / 20 chambres ce soir, 179 nuitées du 01/10 au 14/10 sur
20 × 14 = 280, ADR 45 000 FCFA, RevPAR 8 055 000 / 280 = 28 768 FCFA) ; trois
arrivées confirmées, celles de la liste (Estelle Ngono est déjà réservée).
Liste des arrivées triée comme le code (checkin_date desc : Claire Durand à
18:00 en tête) ; seule la colonne « Total hébergement » porte une somme
(hotel_reservation_views.xml:5-33). Planning : les séjours de
scenarios/t02_planning.py (SEJOURS), chambres de la liste commune des
20 chambres ; « aujourd'hui » = le 14 (index 16 des 35 cases). Réservation :
canal « Direct / comptoir », acompte encaissé avant le check-in (la case
« Acompte » est cochée tant que le client n'est pas arrivé,
hotel_payment_wizard.py:36-41), montant proposé = solde du folio
(hotel_folio.py:337, 102 000 FCFA), référence MTN numérique 8742156309,
check-in réel 14:06:12. Le bouton « Folio » affiche le solde du folio.
Réservation rapide : du 20 au 22/10, Suite Junior, 1 adulte : les quatre
suites junior sont libres (t02 SEJOURS) ; colonnes de
wizard/hotel_booking_wizard_views.xml:8-72, comme t01.
"""

import demo
from ecrans import (assistant, bouton, cell_puce, champ, cp_fiche, deux_colonnes, entree, fenetre, graphe_anneau,
                    graphe_courbe, graphes, groupe, icone, kpi, lien, m_champ, m_champs, num, onglets, statusbar, table,
                    tdb_entete, tdb_filtres, tdb_section, titre_fiche, vue_fiche, vue_liste, vue_tdb, calendrier,
                    e)
from moteur import (animer, anneau, cacher, choisir, clic, classe, compter, defiler, fermer, montrer, ouvrir,
                    pause, saisir, survol, texte, vue)

NOM, ROLE = demo.POSTES['reception']
MENUS = ['Front Desk', 'Réservations', 'Espaces & Prestations', 'Notes de chambre en attente', 'Facturation',
         'Fidélité', 'Gouvernante']

# ------------------------------------------------------------ Front Desk --
# Les chiffres du Front Desk (hotel_dashboard.py:269-356), les mêmes que t01 :
# période « Ce mois » du 01/10 au 14/10, 20 chambres × 14 jours.
CHAMBRES_VENDABLES, JOURS = 20, 14
DISPO = CHAMBRES_VENDABLES * JOURS
PAR_JOUR = [11, 12, 13, 13, 14, 15, 14, 12, 12, 12, 13, 14, 11, 13]     # chambres occupées, nuit du 01/10 au 14/10
NUITEES = sum(PAR_JOUR)
TYPES_CA = {'STD': ('Standard', 35000, '#854F0B'), 'CFT': ('Confort', 45000, '#3B6D11'),
            'SJR': ('Suite Junior', 75000, '#185FA5'), 'VIP': ('Suite VIP', 120000, '#714B67')}
NUITEES_TYPE = {'STD': 78, 'CFT': 84, 'SJR': 11, 'VIP': 6}
CA_HEB = sum(n * TYPES_CA[k][1] for k, n in NUITEES_TYPE.items())
CA_SERV = 440000


def fcfa(n):
    return '{:,}'.format(int(round(n))).replace(',', ' ') + ' FCFA'


def pct(x):
    return ('%.1f' % x).replace('.', ',')


assert (NUITEES, CA_HEB, CA_HEB / NUITEES) == (179, 8055000, 45000)
assert (pct(NUITEES * 100.0 / DISPO), fcfa(CA_HEB / DISPO), pct(13 * 100.0 / CHAMBRES_VENDABLES)) == (
    '63,9', '28 768 FCFA', '65,0')

FRONT = vue_tdb('c1-front', (
    tdb_entete('Front Desk — Réception', 'Occupation, arrivées & départs, room board · ' + demo.SOCIETE,
               'Nouvelle réservation')
    + tdb_filtres([('Période', ["Aujourd'hui", '7 derniers jours', 'Ce mois', 'Mois dernier'], 2)])
    + tdb_section('Photo du jour', [
        kpi('c1-k-occ', 'Occupation ce soir', '65,0 %', '13 / 20 chambres occupées', 'violet'),
        kpi('c1-k-arr', 'Arrivées attendues', '3', 'réservations confirmées du jour', 'bleu'),
        kpi('c1-k-dep', 'Départs prévus', '2', "check-out attendus aujourd'hui", 'ambre'),
        kpi('c1-k-pre', 'Clients présents', '22', '13 séjours en cours', 'vert')])
    + tdb_section('Performance de la période', [
        kpi('c1-k-to', "Taux d'occupation", '%s %%' % pct(NUITEES * 100.0 / DISPO), '%d nuitées vendues' % NUITEES,
            None, ('7,3 % vs N-1', 'haut')),
        kpi('c1-k-adr', 'ADR — prix moyen / nuit', fcfa(CA_HEB / NUITEES), 'CA hébergement / nuitées vendues', None,
            ('2,0 % vs N-1', 'haut')),
        kpi('c1-k-rev', 'RevPAR', fcfa(CA_HEB / DISPO), 'revenu / chambre disponible', None, ('9,4 % vs N-1', 'haut')),
        kpi('c1-k-ca', "Chiffre d'affaires (HT)", fcfa(CA_HEB + CA_SERV),
            'Hébergement %s · Services %s' % (fcfa(CA_HEB), fcfa(CA_SERV)), None, ('9,2 % vs N-1', 'haut'))])
    + graphes(graphe_courbe('c1-g-occ', "Taux d'occupation par jour",
                            [n * 100.0 / CHAMBRES_VENDABLES for n in PAR_JOUR],
                            etiquettes=['01/10', '03/10', '05/10', '07/10', '09/10', '11/10', '14/10']),
              graphe_anneau('c1-g-type', 'CA hébergement par type de chambre',
                            [(TYPES_CA[k][0], NUITEES_TYPE[k] * TYPES_CA[k][1], TYPES_CA[k][2])
                             for k in sorted(NUITEES_TYPE, key=lambda k: -NUITEES_TYPE[k] * TYPES_CA[k][1])]))
), initiale=True)

# ---------------------------------------------------- Arrivées du jour --
COLS_ARR = [('Référence', '178px'), ('Client', '178px'), ('Arrivée', '212px'), ('Départ', '212px'), ('Nuits', '64px', 'd'),
            ('Nb chambres', '124px', 'd'), ('Total hébergement (HT)', '212px', 'd'), ('Solde folio', '132px', 'd'),
            ('Registre', '140px'), ('État', '1fr')]
# Ordre du code (checkin_date desc, puis la plus récente) : Claire Durand (18:00), Estelle Ngono, Martin Ebode.
# Le matin, l'acompte d'Estelle n'est pas encore encaissé : son solde est encore le folio entier (102 000),
# il passe à 57 000 (demo.ARRIVEES) à l'étape de l'acompte.
ORDRE_ARR = ['RES/2026/0201', demo.RESA, 'RES/2026/0209']
SOLDE_MATIN = {demo.RESA: '102 000 FCFA'}
ARRIVEES = vue_liste('c1-arrivees', 'Arrivées du jour', COLS_ARR, [
    {'id': 'c1-a%d' % ORDRE_ARR.index(ref), 'cellules': [
        lien(ref), cli, arr, dep, nuits, ch, num(tot), num(SOLDE_MATIN.get(ref, solde)),
        cell_puce('Aucune fiche', 'rouge'), cell_puce('Confirmée', 'info')]}
    for (ref, cli, arr, dep, nuits, ch, tot, solde) in sorted(demo.ARRIVEES, key=lambda a: ORDRE_ARR.index(a[0]))],
    facettes=[('c1-fac-arr', 'Arrivées du jour')], pager='1-3 / 3',
    total=['', '', '', '', '', '', '315 000 FCFA', '', '', ''])

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
                          champ('Nuits', '2'), champ('Total hébergement (HT)', demo.TOTAL_HEB)])
        + '<div class="masque" id="c1-cireel" style="margin:-12px 0 18px">%s</div>' % champ('Check-in réel', '14/10/2026 14:06:12')
        + groupe('Occupation', [champ('Nb chambres', '1'), champ('Adultes', '2'), champ('Enfants', '0')]))
    + onglets(['Chambres', 'Demandes particulières']) + CHAMBRES)
BANDEAU = ('<div class="bandeau masque" id="c1-bandeau">%s<b>Registre des clients :</b> 1 fiche(s) à compléter · '
           '1 occupant(s) sans fiche — <span class="act">compléter maintenant</span></div>' % icone('fiche'))
B_CONF = [bouton('c1-b-checkin', 'Check-in', 'primaire'), bouton('c1-b-acompte', 'Encaisser un acompte'),
          bouton('c1-b-conf', 'Envoyer la confirmation'), bouton('c1-b-fiches', "Fiches d'enregistrement", ico='imprimer'),
          bouton('c1-b-noshow', 'No-show'), bouton('c1-b-annuler', 'Annuler')]
B_ARRIVE = [bouton('c1-b-checkout', 'Check-out', 'primaire'), bouton('c1-b-acompte2', 'Encaisser un acompte'),
            bouton('c1-b-conf2', 'Envoyer la confirmation'), bouton('c1-b-fiches2', "Fiches d'enregistrement", ico='imprimer'),
            bouton('c1-b-annuler2', 'Annuler')]
RESA = vue_fiche('c1-resa', cp_fiche('Réservations', demo.RESA, '1 / 3', stats=[
    ('c1-st-folio', 'document', 'Folio', TOTAL_RESA), ('c1-st-fiches', 'fiche', 'Fiches clients', '0/2')]),
    B_CONF, statusbar('c1-sb', STATUTS, 1), FEUILLE_RES, bandeau=BANDEAU, boutons_apres=[B_ARRIVE])

ACOMPTE = assistant('c1-as-acompte', 'Encaisser un règlement', m_champs(
    [m_champ('Folio', e(demo.FOLIO)), m_champ('Client', e(demo.CLIENT)), m_champ('Solde dû actuel', e(TOTAL_RESA))],
    [m_champ('Montant à encaisser', entree('c1-montant', '', TOTAL_RESA)),
     m_champ('Acompte', '<span class="case coche"><i></i></span>'),
     m_champ('Moyen de paiement', entree('c1-moyen', 'Espèces')),
     m_champ('Réf. transaction', entree('c1-ref', 'ID transaction Mobile Money')),
     m_champ('Date', e('14/10/2026'))]),
    [('c1-as-ok', 'Encaisser', 'primaire', None), ('c1-as-non', 'Annuler', 'gris', None)], haut=150)

# ------------------------------------------------------------ Folio --
LIGNES = table([('Date', '150px'), ('Type', '170px'), ('Libellé', '1fr'), ('Qté', '80px', 'd'),
                ('Prix unitaire', '170px', 'd'), ('Sous-total (HT)', '180px', 'd')],
               [('c1-fl1', ['14/10/2026', ('<span>%s</span>' % '<span class="puce info">Nuitée</span>',),
                            ('<span class="lien ell">Nuitée 204 (Confort) — 2026-10-14 → 2026-10-16</span>',),
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
                            champ('Taxe de séjour', '12 000 FCFA', 'c1-f-taxe'), champ('Total HT', '102 000 FCFA'),
                            champ('Total TTC', '102 000 FCFA'), champ('Encaissé', '45 000 FCFA'),
                            champ('Solde dû', '57 000 FCFA', 'c1-f-solde', gras=True)]))
    + onglets(['Lignes du folio', 'Règlements', 'Note']) + LIGNES
    + '<div class="note-pied">Les lignes « nuitée » sont synchronisées depuis la réservation ; ajoutez librement des '
      'lignes de service (restaurant, blanchisserie, minibar…).</div>')
FOLIO = vue_fiche('c1-folio', cp_fiche('Folios', demo.FOLIO, '1 / 15', stats=[('c1-st-regl', 'billet', 'Règlements', '1')]),
                  [bouton('c1-f-enc', 'Encaisser', 'primaire'), bouton('c1-f-fact', 'Générer la facture'),
                   bouton('c1-f-recalc', 'Recalculer la taxe de séjour', 'lien'), bouton('c1-f-ann', 'Annuler')],
                  statusbar('c1-fsb', ['Ouvert', 'Facturé', 'Soldé'], 0), FEUILLE_FOLIO)

RAPIDE = assistant('c1-as-rapide', 'Réservation rapide', m_champs(
    [m_champ('Hôtel', entree('c1-r-hotel', '', demo.HOTEL)), m_champ('Arrivée', entree('c1-r-arr', '', '20/10/2026 14:00:00')),
     m_champ('Départ', entree('c1-r-dep', '', '22/10/2026 12:00:00'))],
    [m_champ('Type de chambre', entree('c1-r-type', '')), m_champ('Adultes', entree('c1-r-ad', '', '1')),
     m_champ('Enfants', entree('c1-r-enf', '', '0'))])
    + '<div style="margin-top:14px">%s</div>' % bouton('c1-r-chercher', 'Rechercher les chambres disponibles', 'gris', 'loupe')
    + '<div class="masque" id="c1-r-res" style="margin-top:16px">%s</div>' % table(
        [('Chambre', '170px'), ('Type', '1fr'), ('Étage', '170px'), ('Cap. adultes', '150px', 'd'), ('Nuits', '90px', 'd'),
         ('Prix / nuit', '160px', 'd'), ('Total séjour (HT)', '200px', 'd')],
        [('c1-rr-%s' % n, ['%s [SJR]' % n, 'Suite Junior', '2e étage', '3', '2', '75 000 FCFA', '150 000 FCFA'])
         for n in ('301', '302', '303', '304')], ajouter=None, identifiant='c1-rr'),
    [('c1-r-fermer', 'Fermer', 'gris', None)], haut=150)

ECRAN = fenetre('app-c1', 'Hôtel', MENUS, [FRONT, ARRIVEES, PLANNING, RESA, FOLIO], actif='Front Desk',
                societe=demo.SOCIETE, initiale=NOM[0], calques=ACOMPTE + RAPIDE)

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
    'vues_initiales': {'odoo': 'c1-front'},
    'etapes': [
        {'titre': 'Le Front Desk', 'texte': "L'occupation du soir, les arrivées, les départs et la performance du mois.",
         'voix': "Le Front Desk résume la journée : l'occupation de ce soir, les arrivées attendues, les départs "
                 "prévus, puis la performance du mois, avec le revpar et l'écart sur l'an dernier.",
         'gestes': [compter('#c1-k-occ-v', 0, 65.0, d=1.0, decimales=1, apres=' %'),
                    compter('#c1-k-arr-v', 0, 3, d=0.8, avec=True), compter('#c1-k-dep-v', 0, 2, d=0.8, avec=True),
                    compter('#c1-k-pre-v', 0, 22, d=0.9, avec=True),
                    animer('#c1-g-occ', {'scaleX': 1}, {'scaleX': 0}, d=1.6, avec=True),
                    anneau('#c1-k-arr', d=1.6, decale=0.3), anneau('#c1-k-rev', d=1.8, puis=0.4)]},
        {'titre': 'Les arrivées du jour', 'texte': 'Seules les réservations confirmées qui arrivent aujourd\'hui.',
         'voix': "Le menu Arrivées du jour ne garde que les réservations confirmées qui arrivent aujourd'hui. "
                 "La colonne Registre signale déjà qu'aucune fiche de police n'est encore remplie.",
         'gestes': [clic('#app-c1 .o-haut .menu.actif', d=0.6), vue('c1-arrivees'), pause(0.4),
                    anneau('#c1-fac-arr', d=1.3), survol('#c1-a1'), anneau('#c1-a1 .puce.rouge', d=1.5, decale=0.3)]},
        {'titre': 'Le planning des chambres', 'texte': 'Chaque séjour sur sa chambre, mois par mois.',
         'voix': "Le planning des chambres montre chaque séjour sur sa chambre. En calendrier sur la version "
                 "Community, en Gantt sur Enterprise, sans rien régler.",
         'gestes': [vue('c1-planning'), animer('#c1-planning .c1-planning-sem', {'autoAlpha': 0}, {'autoAlpha': 1}, d=0.8),
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
         'gestes': [clic('#c1-st-folio'), vue('c1-folio'), pause(0.6), anneau('#c1-fl1', d=1.2),
                    anneau('#c1-fl2', d=1.6), anneau('#c1-f-solde', d=1.4)]},
        {'titre': 'La réservation rapide', 'texte': 'Dates, occupation, et les chambres libres en un clic.',
         'voix': "Au téléphone, la réservation rapide suffit : l'hôtel, les dates, le nombre d'adultes, et la "
                 "recherche affiche les chambres disponibles.",
         'gestes': [clic('#app-c1 .o-haut .menu.actif', d=0.6), ouvrir('c1-as-rapide'), pause(0.3),
                    choisir('c1-r-type', 'Suite Junior'), pause(0.3),
                    clic('#c1-r-chercher'), montrer('#c1-r-res', d=0.4), anneau('#c1-r-res', d=1.8)]},
    ],
}
