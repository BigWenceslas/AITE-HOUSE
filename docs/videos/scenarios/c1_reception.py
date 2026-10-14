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
« Fiches clients ») ; aite_city_tax (ligne « Taxe de séjour »). Menus visibles
du profil Réception relevés sur une base de recette (load_menus).
"""

import demo
from ecrans import (assistant, bouton, cell_puce, champ, cp_fiche, deux_colonnes, entree, fenetre, graphe_anneau,
                    graphe_courbe, graphes, groupe, icone, kpi, lien, m_champ, m_champs, num, onglets, statusbar, table,
                    tdb_entete, tdb_filtres, tdb_section, titre_fiche, toast, vue_fiche, vue_liste, vue_tdb, calendrier,
                    e)
from moteur import (animer, anneau, cacher, choisir, clic, classe, compter, defiler, fermer, montrer, notifier, ouvrir,
                    pause, saisir, survol, vue)

NOM, ROLE = demo.POSTES['reception']
MENUS = ['Front Desk', 'Réservations', 'Espaces & Prestations', 'Notes de chambre en attente', 'Facturation',
         'Fidélité', 'Gouvernante']

# ------------------------------------------------------------ Front Desk --
FRONT = vue_tdb('c1-front', (
    tdb_entete('Front Desk — Réception', 'Occupation, arrivées & départs, room board · ' + demo.SOCIETE,
               'Nouvelle réservation')
    + tdb_filtres([('Période', ["Aujourd'hui", '7 derniers jours', 'Ce mois', 'Mois dernier'], 2)])
    + tdb_section('Photo du jour', [
        kpi('c1-k-occ', 'Occupation ce soir', '62,5 %', '15 / 24 chambres occupées', 'violet'),
        kpi('c1-k-arr', 'Arrivées attendues', '3', 'réservations confirmées du jour', 'bleu'),
        kpi('c1-k-dep', 'Départs prévus', '2', "check-out attendus aujourd'hui", 'ambre'),
        kpi('c1-k-pre', 'Clients présents', '27', '15 séjours en cours', 'vert')])
    + tdb_section('Performance de la période', [
        kpi('c1-k-to', "Taux d'occupation", '58,7 %', '183 nuitées vendues', None, ('7,3 % vs N-1', 'haut')),
        kpi('c1-k-adr', 'ADR — prix moyen / nuit', '46 800 FCFA', 'CA hébergement / nuitées vendues', None,
            ('2,0 % vs N-1', 'haut')),
        kpi('c1-k-rev', 'RevPAR', '27 472 FCFA', 'revenu / chambre disponible', None, ('9,4 % vs N-1', 'haut')),
        kpi('c1-k-ca', "Chiffre d'affaires (HT)", '9 004 400 FCFA', 'Hébergement 8 564 400 · Services 440 000',
            None, ('9,2 % vs N-1', 'haut'))])
    + graphes(graphe_courbe('c1-g-occ', "Taux d'occupation par jour",
                            [46, 58, 55, 61, 63, 70, 74, 66, 52, 49, 57, 62, 71, 68],
                            etiquettes=['01/10', '03/10', '05/10', '07/10', '09/10', '11/10', '14/10']),
              graphe_anneau('c1-g-type', 'CA hébergement par type de chambre',
                            [('Suite VIP', 34, '#714B67'), ('Confort', 27, '#3B6D11'), ('Suite Junior', 22, '#185FA5'),
                             ('Standard', 17, '#854F0B')]))
), initiale=True)

# ---------------------------------------------------- Arrivées du jour --
COLS_ARR = [('Référence', '200px'), ('Client', '230px'), ('Arrivée', '240px'), ('Départ', '240px'), ('Nuits', '80px', 'd'),
            ('Total hébergement', '200px', 'd'), ('Solde folio', '170px', 'd'), ('Registre', '150px'), ('État', '1fr')]
ARRIVEES = vue_liste('c1-arrivees', 'Arrivées du jour', COLS_ARR, [
    {'id': 'c1-a%d' % i, 'cellules': [lien(ref), cli, arr, dep, nuits, num(tot), num(solde),
                                      cell_puce('Aucune fiche', 'rouge'), cell_puce('Confirmée', 'info')]}
    for i, (ref, cli, arr, dep, nuits, _ch, tot, solde) in enumerate(demo.ARRIVEES)],
    facettes=[('c1-fac-arr', 'Arrivées du jour')], pager='1-3 / 3', total=['', '', '', '', '', '315 000 FCFA', '125 000 FCFA', '', ''])

# --------------------------------------------------------- Planning --
NUMEROS = [28, 29, 30, 1, 2, 3, 4] + list(range(5, 32)) + [1]
PLANNING = calendrier('c1-planning', 'octobre 2026', NUMEROS, gris={0, 1, 2, 34}, aujourdhui=16, evenements=[
    (0, 3, 3, '201 · Armand Mvogo', '#E8D5F0'), (0, 4, 3, '104 · Joël Kamga', '#D6EAF8'),
    (1, 0, 2, '302 · Sylvie Mbarga', '#FCE4D6'), (1, 1, 4, '102 · Patrick Nkoulou', '#D5F5E3'),
    (1, 4, 3, '401 · Brigitte Essomba', '#FDEBD0'), (2, 0, 3, '305 · Paul Durand', '#E8DAEF'),
    (2, 2, 2, '204 · Estelle Ngono', '#F9E79F'), (2, 2, 3, '206 · Martin Ebode', '#D6EAF8'),
    (2, 2, 1, '401 · Claire Durand', '#FADBD8'), (2, 4, 3, '103 · Joël Kamga', '#D5F5E3'),
    (3, 1, 4, '202 · Sylvie Mbarga', '#FCE4D6'), (3, 3, 3, '402 · Armand Mvogo', '#E8D5F0'),
    (4, 0, 3, '101 · Patrick Nkoulou', '#D6EAF8')])

# ------------------------------------------------------- Réservation --
STATUTS = ['Brouillon', 'Confirmée', 'Arrivé', 'Parti']
CHAMBRES = table([('Type', '1fr'), ('Chambre', '170px'), ('Adultes', '100px', 'd'), ('Enfants', '100px', 'd'),
                  ('Nuits', '80px', 'd'), ('Prix / nuit', '180px', 'd'), ('Sous-total (HT)', '200px', 'd')],
                 [('c1-l1', [demo.TYPE, demo.CHAMBRE, '2', '0', '2', demo.PRIX_NUIT, demo.TOTAL_HEB])],
                 total=['', '', '', '', '', '', demo.TOTAL_HEB])
FEUILLE_RES = (
    titre_fiche(demo.RESA)
    + deux_colonnes(
        groupe('Client', [champ('Client', demo.CLIENT, lien_=True), champ('Téléphone', demo.CLIENT_TEL),
                          champ('E-mail', demo.CLIENT_MAIL), champ('Hôtel', demo.HOTEL, lien_=True)])
        + groupe('Canal & commission', [champ('Canal', 'Téléphone / WhatsApp', gras=True)]),
        groupe('Séjour', [champ('Arrivée', demo.ARRIVEE, gras=True), champ('Départ', demo.DEPART, gras=True),
                          champ('Nuits', '2'), champ('Total hébergement (HT)', demo.TOTAL_HEB)])
        + '<div class="masque" id="c1-cireel" style="margin:-12px 0 18px">%s</div>' % champ('Check-in réel', '14/10/2026 14:12:05')
        + groupe('Occupation', [champ('Nb chambres', '1'), champ('Adultes', '2'), champ('Enfants', '0')]))
    + onglets(['Chambres', 'Demandes particulières']) + CHAMBRES)
BANDEAU = ('<div class="bandeau masque" id="c1-bandeau">%s<b>Registre des clients :</b> 2 fiche(s) à compléter — '
           '<span class="act">compléter maintenant</span></div>' % icone('fiche'))
B_CONF = [bouton('c1-b-checkin', 'Check-in', 'primaire'), bouton('c1-b-acompte', 'Encaisser un acompte'),
          bouton('c1-b-conf', 'Envoyer la confirmation'), bouton('c1-b-fiches', "Fiches d'enregistrement", ico='imprimer'),
          bouton('c1-b-noshow', 'No-show'), bouton('c1-b-annuler', 'Annuler')]
B_ARRIVE = [bouton('c1-b-checkout', 'Check-out', 'primaire'), bouton('c1-b-acompte2', 'Encaisser un acompte'),
            bouton('c1-b-conf2', 'Envoyer la confirmation'), bouton('c1-b-fiches2', "Fiches d'enregistrement", ico='imprimer'),
            bouton('c1-b-annuler2', 'Annuler')]
RESA = vue_fiche('c1-resa', cp_fiche('Réservations', demo.RESA, '1 / 3', stats=[
    ('c1-st-folio', 'document', 'Folio', demo.TOTAL_HEB), ('c1-st-fiches', 'fiche', 'Fiches clients', '0/2')]),
    B_CONF, statusbar('c1-sb', STATUTS, 1), FEUILLE_RES, bandeau=BANDEAU, boutons_apres=[B_ARRIVE])

ACOMPTE = assistant('c1-as-acompte', 'Encaisser un règlement', m_champs(
    [m_champ('Folio', e(demo.FOLIO)), m_champ('Client', e(demo.CLIENT)), m_champ('Solde dû actuel', e('90 000 FCFA'))],
    [m_champ('Montant à encaisser', entree('c1-montant', '0 FCFA')),
     m_champ('Acompte', '<span class="case coche"><i></i></span>'),
     m_champ('Moyen de paiement', entree('c1-moyen', 'Espèces')),
     m_champ('Réf. transaction', entree('c1-ref', 'ID transaction Mobile Money')),
     m_champ('Date', e('14/10/2026'))]),
    [('c1-as-ok', 'Encaisser', 'primaire', None), ('c1-as-non', 'Annuler', 'gris', None)], haut=150)
TOAST = toast('c1-toast', 'Acompte encaissé', '45 000 FCFA en MTN Mobile Money — le solde du folio baisse d\'autant.')

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
    + '<div class="m-aide masque" id="c1-r-res" style="margin-top:16px"><b>6 chambres disponibles</b> — Suite Junior : '
      '301, 302, 303 · Suite VIP : 401, 402, 403. Choisissez la chambre : la réservation est créée en brouillon, '
      'prête à confirmer.</div>',
    [('c1-r-fermer', 'Fermer', 'gris', None)], haut=150)

ECRAN = fenetre('app-c1', 'Hôtel', MENUS, [FRONT, ARRIVEES, PLANNING, RESA, FOLIO], actif='Front Desk',
                societe=demo.SOCIETE, initiale=NOM[0], calques=ACOMPTE + TOAST + RAPIDE)

CHAPITRE = {
    'court': 'Réception',
    'poste': 'Réception',
    'titre': 'La journée de la réception',
    'personne': (NOM, ROLE),
    'objectif': "Prendre connaissance de la journée, retrouver une réservation, faire le check-in, "
                "encaisser un acompte et lire le folio du séjour.",
    'voix': "Premier chapitre : la réception. Mireille ouvre sa journée, accueille une cliente, "
            "encaisse un acompte et suit le folio du séjour, sans quitter son écran.",
    'app': 'app-c1',
    'ecran': ECRAN,
    'vues_initiales': {'odoo': 'c1-front'},
    'etapes': [
        {'titre': 'Le Front Desk', 'texte': "L'occupation du soir, les arrivées, les départs et la performance du mois.",
         'voix': "Le Front Desk résume la journée : l'occupation de ce soir, les arrivées attendues, les départs "
                 "prévus, puis la performance du mois, avec le revpar et l'écart sur l'an dernier.",
         'gestes': [compter('#c1-k-occ-v', 0, 62.5, d=1.0, decimales=1, apres=' %'),
                    compter('#c1-k-arr-v', 0, 3, d=0.8, avec=True), compter('#c1-k-dep-v', 0, 2, d=0.8, avec=True),
                    compter('#c1-k-pre-v', 0, 27, d=0.9, avec=True),
                    animer('#c1-g-occ', {'scaleX': 1}, {'scaleX': 0}, d=1.6, avec=True),
                    anneau('#c1-k-arr', d=1.6, decale=0.3), anneau('#c1-k-rev', d=1.8, puis=0.4)]},
        {'titre': 'Les arrivées du jour', 'texte': 'Seules les réservations confirmées qui arrivent aujourd\'hui.',
         'voix': "Le menu Arrivées du jour ne garde que les réservations confirmées qui arrivent aujourd'hui. "
                 "La colonne Registre signale déjà qu'aucune fiche de police n'est encore remplie.",
         'gestes': [clic('#app-c1 .o-haut .menu.actif', d=0.6), vue('c1-arrivees'), pause(0.4),
                    anneau('#c1-fac-arr', d=1.3), survol('#c1-a0'), anneau('#c1-a0 .puce.rouge', d=1.5, decale=0.3)]},
        {'titre': 'Le planning des chambres', 'texte': 'Chaque séjour sur sa chambre, mois par mois.',
         'voix': "Le planning des chambres montre chaque séjour sur sa chambre. En calendrier sur la version "
                 "Community, en Gantt sur Enterprise, sans rien régler.",
         'gestes': [vue('c1-planning'), animer('#c1-planning-evs', {'autoAlpha': 0}, {'autoAlpha': 1}, d=0.8),
                    pause(1.2), anneau('#c1-planning .auj', d=1.6)]},
        {'titre': 'La réservation et le check-in', 'texte': 'Un clic : la cliente est arrivée, la chambre devient occupée.',
         'voix': "Voici la réservation d'Estelle Ngono : deux nuits en chambre Confort. À son arrivée, un clic sur "
                 "Check-in. La réservation passe à Arrivé, et un bandeau rappelle les deux fiches de police à compléter.",
         'gestes': [vue('c1-resa'), pause(0.4), defiler('#c1-resa-defil', -330, d=0.9), anneau('#c1-l1', d=1.3),
                    defiler('#c1-resa-defil', 0, d=0.7), clic('#c1-b-checkin'),
                    classe('#c1-sb-1', retirer=['actif']), classe('#c1-sb-2', ajouter=['actif']),
                    cacher('#c1-resa-ga', d=0.2), montrer('#c1-resa-gb', d=0.3, y=0),
                    montrer('#c1-cireel', d=0.3, y=0),
                    montrer('#c1-bandeau', d=0.4, y=-10), defiler('#c1-resa-defil', 52, d=0.4, avec=True),
                    anneau('#c1-bandeau', d=1.6, decale=0.2), anneau('#c1-st-fiches', d=1.3)]},
        {'titre': 'Encaisser un acompte', 'texte': 'Mobile Money, espèces ou carte, avec la référence de la transaction.',
         'voix': "L'acompte s'encaisse depuis la réservation : montant, moyen de paiement, MTN Mobile Moni ici, "
                 "et la référence de la transaction. Le règlement s'inscrit aussitôt sur le folio.",
         'gestes': [clic('#c1-b-acompte2'), ouvrir('c1-as-acompte'), saisir('c1-montant', '45 000 FCFA'),
                    choisir('c1-moyen', 'MTN Mobile Money'), saisir('c1-ref', 'MP261014.1452.C18842'),
                    clic('#c1-as-ok'), fermer('c1-as-acompte'), notifier('c1-toast', duree=2.4)]},
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
