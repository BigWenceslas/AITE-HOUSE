# -*- coding: utf-8 -*-
"""Chapitre 6 — Le cockpit de la direction.

Source : fiche de recette n° 4 « Le cockpit de la direction » (Ventes —
POS Analytics, Recouvrement, Stock, Achats & Fournisseurs, Espaces &
Prestations, Cockpit Direction, Tableau de bord exécutif) et cahier de
recette, domaine Q (F06 : RevPAR, pickup, pace, écarts N-1, tuile
Hébergement du cockpit).

Libellés relevés dans :
- aite_direction_dashboard/static/src/xml (« Direction — Vue consolidée »,
  filtres Période / Caisse / Heure / Jour / Vue, « Santé de l'affaire »,
  « L'essentiel par pôle — cliquer une carte ouvre l'onglet », cartes et
  sous-titres, rangée « Hébergement — écarts vs même période N-1 »),
  static/src/js/direction_dashboard.js (netPositionSub, hotelPaceSub,
  hotelPickupSub) ;
- aite_exec_dashboard/static/src/xml/dashboard.xml (cartes, section
  « Hébergement — indicateurs de performance », pickupSub / paceSub),
  models/exec_dashboard.py (KPI_HINTS : texte de l'infobulle RevPAR),
  static/src/js/services/utils.js (fmtDelta « ▲ + », monthLabel « oct 26 ») ;
- aite_pos_analytics/static/src/xml/views.xml (cartes et sous-titres,
  « Bonne maîtrise ✓ », « Objectif atteint ✓ ») ;
- aite_purchase_dashboard (capture de recette r4-direction-04 et vues :
  cartes, onglets, « negMoney ») ;
- aite_slot_booking/static/src/xml (« Espaces & Prestations », filtres,
  « Activité de la période », « Planning du <jour> », « créneaux libres »).
Les dates ISO (« 2026-09-30 → 2026-10-14 », « Planning du 2026-10-17 ») et
les pourcentages à point décimal de POS Analytics sont rejoués tels que
le code les affiche : relevés dans ECARTS.md.

Jour rejoué : le mercredi 14/10/2026, comme scenarios/t15_direction.py. La
période « Ce mois » démarre la veille du 1er à Douala (écart 1 de t15) :
« 2026-09-30 → 2026-10-14 », quinze jours ; 192 nuitées sur 20 chambres × 15
jours = 300, d'où 64,0 % et RevPAR 28 800 FCFA. Espaces & Prestations : les
indicateurs de la période par défaut, « Aujourd'hui » (slot_dashboard_view.js
:30-34), et le planning du samedi 17/10, celui de scenarios/t08_site_web.py
(JOUR_17, mêmes ressources, mêmes réservations) : la réservation en ligne de
Claire Durand (RES/26/0131, 16:00-17:00) est sur le salon Wouri. Indicateurs
du 14/10 repris de t08 : 61 800 FCFA réalisés (5 prestations), 20 h
réservées sur 109 h ouvrées (huit ressources), aucun no-show, 2 retraits
pressing en attente, 6 réservations à venir.
"""

import demo
from ecrans import (ICONES, e, fenetre, graphe_anneau, graphe_barres, graphes, kpi, tdb_entete, tdb_filtres, tdb_section,
                    vue_tdb)
from moteur import anneau, cacher, clic, compter, defiler, montrer, pause, vue

NOM, ROLE = demo.POSTES['direction']


def barre(ident, app, menus, actif=None, societe=demo.SOCIETE):
    """Une barre d'application de rechange, posée sur celle de la fenêtre."""
    entrees = ''.join('<span class="menu%s">%s</span>' % (' actif' if m == actif else '', e(m)) for m in menus)
    return ('<div class="o-haut barre-app masque" id="%s"><span class="grille">%s</span><span class="nom-app">%s</span>%s'
            '<span class="droite"><span class="pictos">%s</span><span class="societe">%s</span>'
            '<span class="avatar" style="background:#854F0B">%s</span></span></div>'
            % (ident, ICONES['grille'], e(app), entrees, ICONES['bulle'], e(societe), e(NOM[0])))


MENUS_HOTEL = ['Direction', 'Front Desk', 'Réservations', 'Espaces & Prestations', 'Notes de chambre en attente',
               'Facturation', 'Fidélité', 'Gouvernante', 'Configuration']
BARRES = (barre('c6-nav-pos', 'Point de Vente', ['Tableau de bord', 'Commandes', 'Produits', 'Analyse AITE', 'Rapports',
                                                 'Configuration'], 'Analyse AITE')
          + barre('c6-nav-achats', 'Achats', ['Commandes', 'Tableau de bord AITE', 'Produits', 'Rapports', 'Configuration'],
                  'Tableau de bord AITE')
          + barre('c6-nav-esp', 'Hôtel', MENUS_HOTEL, 'Espaces & Prestations', '')
          + barre('c6-nav-exec', 'Hôtel', MENUS_HOTEL, 'Direction', ''))

# ----------------------------------------------------------- le cockpit --
VUES = ["Vue d'ensemble", 'Ventes (POS)', 'Crédit clients', 'Stock', 'Achats', 'À traiter']
COCKPIT = vue_tdb('c6-cockpit', '<div id="c6-in">%s</div>' % (
    tdb_entete('Direction — Vue consolidée', 'POS · Crédit clients · Stock · Achats — %s' % demo.SOCIETE)
    + tdb_filtres([('Période', ['Toute la période', "Aujourd'hui", 'Cette semaine', 'Ce mois', 'Ce trimestre',
                                'Cette année'], 3),
                   ('Caisse', ['Toutes les caisses', 'Bar de la terrasse', 'Restaurant'], 0),
                   ('Heure', ['Toute la journée', 'Matin 6–12h', 'Après-midi 12–18h', 'Soir 18–23h', 'Nuit 23–6h'], 0),
                   ('Vue', VUES, 0)])
    + tdb_section("Santé de l'affaire", [
        kpi('c6-k-ca', 'CA encaissé', '3 120 000 FCFA', '128 tickets · POS payés / facturés', 'vert'),
        kpi('c6-k-marge', 'Marge brute réalisée', '1 747 200 FCFA', '56,0 % du CA · CA − coût des ventes', 'teal'),
        kpi('c6-k-risque', 'Cash à risque', '143 000 FCFA', 'ardoises +30 j (101 500) + coulage (41 500)', 'rouge'),
        kpi('c6-k-net', 'Crédits clients − dettes fournisseurs', '−1 130 000 FCFA',
            "150 000 d'ardoises · 1 280 000 de dettes — les fournisseurs financent l'exploitation", 'bleu')])
    + tdb_section("L'essentiel par pôle — cliquer une carte ouvre l'onglet", [
        kpi('c6-p-tix', 'Ventes — tickets', '128', 'panier moyen 24 375 FCFA', 'violet'),
        kpi('c6-p-ard', 'Encours ardoises', '150 000 FCFA', '5 clients · 101 500 au-delà de 30 j', 'ambre'),
        kpi('c6-p-four', 'Dettes fournisseurs', '1 280 000 FCFA', '180 000 échues · 420 000 sous 7 j', 'bleu'),
        kpi('c6-p-stock', 'Stock — valeur / alertes', '3 185 000 FCFA', '2 réfs en alerte · coulage 0,6 %', 'violet')])
    + tdb_section('Hébergement — écarts vs même période N-1 ; cliquer une carte ouvre le tableau de bord exécutif', [
        kpi('c6-h-ca', 'CA des nuitées (HT)', '8 640 000 FCFA', '192 nuitée(s) vendue(s) · pace du mois : 412 (N-1 : 387)',
            'vert', ('+11,6 % vs N-1', 'haut'), aide=True),
        kpi('c6-h-occ', "Taux d'occupation", '64,0 %', 'pickup 46 nuitée(s) prises ces 7 j pour les 30 prochains',
            None, ('+8,2 % vs N-1', 'haut'), aide=True),
        kpi('c6-h-adr', 'ADR — prix moyen par nuit', '45 000 FCFA', 'CA hébergement ÷ nuitées vendues', None,
            ('+3,1 % vs N-1', 'haut'), aide=True),
        kpi('c6-h-revpar', 'RevPAR', '28 800 FCFA', 'par chambre disponible, vendue ou non', None,
            ('+11,6 % vs N-1', 'haut'), aide=True)])),
    initiale=True)

# ------------------------------------------------------ ventes (POS) --
ONGLETS_POS = ['Tableau de bord', 'Par caisse', 'Sessions POS', 'Articles', 'Marges & CMV', 'Par catégorie',
               'Écarts de caisse', 'Paiements']
VENTES = vue_tdb('c6-ventes', (
    '<div class="tdb-filtres" style="margin-top:0"><div class="tdb-rang">%s</div></div>'
    % ''.join('<span class="chip%s">%s</span>' % (' actif' if i == 0 else '', e(o)) for i, o in enumerate(ONGLETS_POS))
    + tdb_filtres([('Période', ['Toute la période', "Aujourd'hui", 'Cette semaine', 'Ce mois', 'Ce trimestre',
                              'Cette année'], 3),
                 ('Heure', ['Toute la journée', 'Matin 6–12h', 'Après-midi 12–18h', 'Soir 18–23h', 'Nuit 23–6h'], 0),
                 ('Jour', ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'], -1)])
    + '<div style="height:14px"></div><div class="tdb-grille c4">%s</div>' % ''.join([
        kpi('c6-v-ca', "Chiffre d'affaires", '3 120 000 F', '208 000 F / jour · 15j', 'bleu'),
        kpi('c6-v-marge', 'Marge brute', '1 747 200 F', 'Taux: 56.0% · 13 650 F/tx', 'vert'),
        kpi('c6-v-cmv', 'CMV (coût marchandises)', '1 372 800 F', '44.0% du CA · 2 681 F/u', 'rouge'),
        kpi('c6-v-tx', 'Transactions', '128', 'Panier moy. 24 375 F · 512 u', 'violet')])
    + '<div style="height:14px"></div><div class="tdb-grille c4">%s</div>' % ''.join([
        kpi('c6-v-ratio', 'Ratio CMV/CA', '44.0%', 'Bonne maîtrise ✓'),
        kpi('c6-v-taux', 'Taux de marge', '56.0%', 'Objectif atteint ✓'),
        kpi('c6-v-art', 'Articles actifs', '42 / 48', 'références vendues'),
        kpi('c6-v-best', 'Meilleur article', 'Bière blonde 65 cl', '486 000 F CA')])
    + '<div style="height:14px"></div>'
    + graphes(graphe_barres('c6-g-top', 'Top 8 articles — CA vs marge',
                            [(92, '#714B67'), (51, '#3B6D11'), (64, '#714B67'), (36, '#3B6D11'), (48, '#714B67'),
                             (27, '#3B6D11'), (40, '#714B67'), (22, '#3B6D11')],
                            etiquettes=['Bière blonde', 'Poulet DG', 'Poisson braisé', 'Jus ananas']),
              graphe_barres('c6-g-evo', 'Évolution mensuelle (CA · CMV · marge)',
                            [(58, '#714B67'), (63, '#714B67'), (70, '#714B67'), (66, '#714B67'), (74, '#714B67'),
                             (80, '#714B67')], etiquettes=['Mai', 'Juin', 'Juil', 'Août', 'Sep', 'Oct']))))

# --------------------------------------------------------------- achats --
ACHATS = vue_tdb('c6-achats', (
    tdb_entete('Achats & Fournisseurs — Tableau de bord', 'Dettes (401) & créances fournisseurs (409) · échéancier · OTIF · prix')
    + tdb_filtres([('Période', ["Aujourd'hui", 'Cette semaine', 'Ce mois', '3 mois'], 2),
                   ('Fournisseur', ['Tous', 'Boissons du Wouri SARL', 'Dépôt Akwa Distribution', 'Épicerie Fine Bonapriso',
                                    'Hygiène Pro Littoral'], 0)])
    + tdb_section("Vue d'ensemble", [
        kpi('c6-a-achats', 'Achats (période)', '1 850 000 FCFA', '6 commandes · 5 réceptions', 'bleu'),
        kpi('c6-a-dette', 'Dette fournisseurs (401)', '1 280 000 FCFA', '4 factures ouvertes', 'rouge'),
        kpi('c6-a-7j', 'À payer sous 7 j', '420 000 FCFA', '1 facture(s) · trésorerie à prévoir', 'ambre'),
        kpi('c6-a-dpo', 'DPO — délai moyen de paiement', '24 j', 'encours / factures période · tenir les délais négociés',
            'violet')])
    + tdb_section('Indicateurs', [
        kpi('c6-a-retard', 'En retard de paiement', '−180 000 FCFA', "1 facture(s) · 14,1 % de l'encours"),
        kpi('c6-a-409', 'Créances fournisseurs (409)', '95 000 FCFA', 'consignes + avoirs + acomptes'),
        kpi('c6-a-otif', 'Taux de service (OTIF)', '83 %', "livré à l'heure et complet · cible ≥ 90 %"),
        kpi('c6-a-cmd', 'Commandes en cours', '2 cmd', '640 000 FCFA attendus · 1 en retard')])
    + graphes(graphe_anneau('c6-g-four', 'Achats par fournisseur (période)',
                            [('Boissons du Wouri SARL', 52, '#714B67'), ('Dépôt Akwa Distribution', 26, '#185FA5'),
                             ('Épicerie Fine Bonapriso', 14, '#3B6D11'), ('Hygiène Pro Littoral', 8, '#854F0B')]),
              graphe_barres('c6-g-fp', 'Factures vs Paiements — 6 mois',
                            [(60, '#714B67'), (54, '#3B6D11'), (66, '#714B67'), (62, '#3B6D11'), (58, '#714B67'),
                             (50, '#3B6D11'), (72, '#714B67'), (64, '#3B6D11'), (70, '#714B67'), (61, '#3B6D11'),
                             (76, '#714B67'), (55, '#3B6D11')],
                            etiquettes=['Mai', 'Juin', 'Juil', 'Août', 'Sep', 'Oct']))))

# ---------------------------------------------------- espaces & prestations --
# Les huit ressources (scenarios/t09_espaces.py, même ordre ; couleur de la famille) et le planning du
# samedi 17/10 (scenarios/t08_site_web.py, JOUR_17) : (nom, couleur, ouverture, fermeture, pas en minutes,
# [(début h, fin h, client, identifiant)]). Créneaux libres = créneaux entièrement vides (booking_resource.py:106-142).
RESSOURCES = [
    ('Salon VIP Wouri', '#714B67', 9, 23, 60, [(12, 14, 'Aline Nkengue', None),
                                               (16, 17, demo.POSTES['client'][0], 'c6-bk-claire'),
                                               (19, 21, 'Gilbert Tchoua', None)]),
    ('Salon VIP Sanaga', '#714B67', 9, 23, 60, [(10, 12, 'Josué Mbida', None), (18, 20, 'Joseph Ekani', None)]),
    ('Salon VVIP Bonabéri', '#714B67', 10, 23, 60, [(15, 19, 'Grâce Nguene', None)]),
    ('Cabine SPA 1', '#0F6E56', 9, 21, 30, [(11, 12, 'Nadège Owona', None), (15, 16.5, 'Sandrine Kemajou', None)]),
    ('Cabine SPA 2', '#0F6E56', 9, 21, 30, [(10, 11, 'Pauline Etame', None)]),
    ('Fauteuil homme 1', '#185FA5', 9, 20, 30, [(9, 9.5, 'Armel Tsala', None), (14, 14.5, 'Hugo Biyong', None)]),
    ('Fauteuil femme 1', '#185FA5', 9, 20, 30, [(9.5, 11.5, 'Gisèle Kouam', None), (14, 15, 'Odile Ekwalla', None)]),
]


def libres(ouv, ferm, pas, creneaux):
    """« x/y » : les créneaux du pas de la ressource qui ne touchent aucune réservation."""
    step, h, n, total = pas / 60.0, float(ouv), 0, 0
    while h + step <= ferm + 1e-6:
        total += 1
        n += 0 if any(d < h + step and f > h for d, f, _, _ in creneaux) else 1
        h += step
    return '%d/%d' % (n, total)


assert [libres(*r[2:]) for r in RESSOURCES] == ['9/14', '10/14', '9/13', '19/24', '22/24', '20/22', '16/22']


def ligne_planning(i, nom, couleur, ouv, ferm, pas, creneaux):
    barres = ''.join('<span class="pl-b"%s style="left:%.2f%%;width:%.2f%%">%s</span>'
                     % (' id="%s"' % ident if ident else '', (d - 9) * 100 / 14.0, (f - d) * 100 / 14.0, e(c))
                     for d, f, c, ident in creneaux)
    return ('<div class="pl-l" id="c6-pl%d"><span class="pl-n"><i style="background:%s"></i>%s</span>'
            '<div class="pl-p">%s</div><span class="pl-x">%s créneaux libres</span></div>'
            % (i, couleur, e(nom), barres, libres(ouv, ferm, pas, creneaux)))


ESPACES = vue_tdb('c6-espaces', (
    tdb_entete('Espaces & Prestations', 'Planning des créneaux · SPA, coiffure, pressing, espaces VIP / VVIP',
               'Nouvelle réservation')
    + tdb_filtres([('Jour', ['‹', '17/10/2026', '›', "Aujourd'hui"], -1),
                   ('Période stats', ["Aujourd'hui", 'Cette semaine', 'Ce mois'], 0),
                   ('Famille', ['Toutes', 'Espace VIP / VVIP', 'SPA', 'Coiffure', 'Pressing', 'Autre'], 0)])
    + tdb_section('Activité de la période', [
        kpi('c6-e-ca', 'CA prestations réalisées', '61 800 FCFA', '5 réalisée(s)', 'violet'),
        kpi('c6-e-remp', 'Taux de remplissage', '18,3 %', '20 h réservées / 109 h ouvrées', 'bleu'),
        kpi('c6-e-ns', 'No-show', '0 %', '0 rendez-vous manqué(s)', 'rouge'),
        kpi('c6-e-pr', 'Retraits pressing en attente', '2', '6 réservation(s) à venir', 'ambre')])
    + '<div class="tdb-sect">Planning du 2026-10-17</div><div class="pl">'
      '<div class="pl-h"><span></span><div><span>09:00</span><span>11:00</span><span>13:00</span><span>15:00</span>'
      '<span>17:00</span><span>19:00</span><span>21:00</span><span>23:00</span></div><span></span></div>%s</div>'
      % ''.join(ligne_planning(i, *r) for i, r in enumerate(RESSOURCES))))

# ------------------------------------------------- tableau de bord exécutif --
INFOBULLE = ('<div class="infobulle masque" id="c6-bulle" style="left:1180px;top:500px">RevPAR : ce que rapporte chaque '
             "chambre disponible, vendue ou non — c'est l'indicateur qui combine prix et remplissage.</div>")
EXEC = vue_tdb('c6-exec', (
    tdb_entete('Direction — Vue consolidée', 'Hébergement · Restauration & boutique · Prestations')
    + tdb_filtres([('Période', ['Ce mois', 'Ce trimestre', 'Cette année'], 0)])
    + '<div style="height:14px"></div><div class="tdb-grille c4">%s</div>' % ''.join([
        kpi('c6-x-tot', "Chiffre d'affaires total", '13 000 000 FCFA', 'Période 2026-09-30 → 2026-10-14', 'violet'),
        kpi('c6-x-heb', 'Hébergement', '8 640 000 FCFA', 'Occupation 64,0 % · ADR 45 000 FCFA', 'violet'),
        kpi('c6-x-pos', 'Restauration & boutique', '3 120 000 FCFA', '128 tickets · panier 24 375 FCFA', 'bleu'),
        kpi('c6-x-pre', 'Prestations', '1 240 000 FCFA', '46 prestation(s) réalisée(s)', 'teal')])
    + '<div class="tdb-sect">Hébergement — indicateurs de performance <span style="text-transform:none;'
      'letter-spacing:0;font-weight:500;color:var(--o-texte-3)">écarts vs même période N-1</span></div>'
    + '<div class="tdb-grille c5">%s</div>' % ''.join([
        kpi('c6-x-occ', "Taux d'occupation", '64,0 %', '192 nuitée(s) vendue(s)', None, ('+8,2 % vs N-1', 'haut'),
            aide=True),
        kpi('c6-x-adr', 'ADR — prix moyen par nuit', '45 000 FCFA', 'CA hébergement ÷ nuitées vendues', None,
            ('+3,1 % vs N-1', 'haut'), aide=True),
        kpi('c6-x-revpar', 'RevPAR', '28 800 FCFA', 'par chambre disponible, vendue ou non', None,
            ('+11,6 % vs N-1', 'haut'), aide=True),
        kpi('c6-x-pick', 'Pickup 7 j → 30 j', '46 nuitée(s)', '18 réservation(s) prise(s) ces 7 derniers jours', None,
            aide=True),
        kpi('c6-x-pace', 'Pace du mois', '412 nuitée(s)', 'mois oct 26 · N-1 à la même date : 387 nuitée(s)', None,
            ('+6,5 % vs même date N-1', 'haut'), aide=True)])
    + '<div style="height:14px"></div>'
    + graphes(graphe_anneau('c6-g-mix', "Mix du chiffre d'affaires par pôle",
                            [('Hébergement', 66.5, '#714B67'), ('Restauration & boutique', 24.0, '#185FA5'),
                             ('Prestations', 9.5, '#0F6E56')]),
              graphe_barres('c6-g-mois', 'Évolution mensuelle — 6 mois',
                            [(55, '#714B67'), (60, '#714B67'), (72, '#714B67'), (78, '#714B67'), (64, '#714B67'),
                             (70, '#714B67')], etiquettes=['mai 26', 'juin 26', 'juil 26', 'août 26', 'sept 26', 'oct 26']))
    + INFOBULLE))

ECRAN = fenetre('app-c6', 'Direction', [], [COCKPIT, VENTES, ACHATS, ESPACES, EXEC], societe=demo.SOCIETE,
                initiale=NOM[0], avatar='#854F0B', calques=BARRES)


def changer_app(depuis, vers, vue_):
    """Le menu des applications : on quitte une application pour une autre."""
    gestes = [clic('#app-c6 .o-haut .grille', d=0.5)]
    if depuis:
        gestes.append(cacher('#%s' % depuis, d=0.15))
    gestes += [montrer('#%s' % vers, d=0.2, y=0, avec=True), vue(vue_)]
    return gestes


CHAPITRE = {
    'court': 'Direction',
    'poste': 'Direction',
    'titre': 'Le cockpit de la direction',
    'personne': (NOM, ROLE),
    'objectif': "Lire la santé de l'établissement d'un coup d'œil, puis descendre pôle par pôle : ventes, achats, "
                "espaces, hébergement.",
    'voix': "Sixième chapitre : la direction. Danielle ne saisit rien : elle lit les chiffres que le terrain vient "
            "de produire, avec les mêmes montants dans chaque tableau de bord.",
    'app': 'app-c6',
    'ecran': ECRAN,
    'vues_initiales': {'odoo': 'c6-cockpit'},
    'etapes': [
        {'titre': 'Le cockpit Direction', 'texte': "Ce qui rentre, ce qu'on gagne, ce qui est à risque.",
         'voix': "Le cockpit Direction réunit les ventes, le crédit clients, le stock et les achats. En tête, la "
                 "santé de l'affaire : le chiffre encaissé, la marge réalisée, et le cash à risque, ardoises en "
                 "retard et pertes de stock comprises.",
         'gestes': [compter('#c6-k-ca-v', 0, 3120000, d=1.1, apres=' FCFA'), anneau('#c6-k-marge', d=1.2),
                    anneau('#c6-k-risque', d=1.6), anneau('#c6-k-net', d=1.4)]},
        {'titre': "L'essentiel par pôle", 'texte': "Les mêmes chiffres qu'à la caisse, au magasin et à l'hôtel.",
         'voix': "Dessous, l'essentiel par pôle : on retrouve l'encours des ardoises vu à la caisse et la valeur du "
                 "stock vue au magasin. Et l'hébergement, comparé à l'an dernier : occupation, prix moyen, revpar.",
         'gestes': [defiler('#c6-in', -330, d=0.9), anneau('#c6-p-ard', d=1.2), anneau('#c6-p-stock', d=1.2),
                    anneau('#c6-h-occ', d=1.0), anneau('#c6-h-revpar', d=1.2)]},
        {'titre': 'Les ventes du bar et du restaurant', 'texte': "Chiffre d'affaires, marge, coût des marchandises.",
         'voix': "Dans le point de vente, l'analyse des ventes détaille le chiffre d'affaires, la marge et le coût "
                 "des marchandises, par article, par heure et par jour. Le ratio dit tout de suite si la marge est "
                 "maîtrisée.",
         'gestes': changer_app(None, 'c6-nav-pos', 'c6-ventes')
                   + [pause(0.4), anneau('#c6-v-ca', d=1.0), anneau('#c6-v-marge', d=1.0), anneau('#c6-v-ratio', d=1.2),
                      anneau('#c6-v-best', d=1.0)]},
        {'titre': 'Les achats et les fournisseurs', 'texte': 'Ce qui est dû, ce qui tombe cette semaine, la ponctualité.',
         'voix': "Côté achats : la dette fournisseurs, ce qui est à payer dans les sept jours, le délai moyen de "
                 "paiement, et le taux de service des fournisseurs, livré à l'heure et complet.",
         'gestes': changer_app('c6-nav-pos', 'c6-nav-achats', 'c6-achats')
                   + [pause(0.4), anneau('#c6-a-dette', d=1.0), anneau('#c6-a-7j', d=1.2), anneau('#c6-a-otif', d=1.4)]},
        {'titre': 'Les espaces et prestations', 'texte': 'Le remplissage du jour, et le planning de samedi, ressource par ressource.',
         'voix': "Les espaces et prestations montrent le remplissage du jour et le planning de chaque salon, cabine "
                 "ou fauteuil. Samedi, la réservation faite par Claire sur le site est déjà là, sur le salon Wouri.",
         'gestes': changer_app('c6-nav-achats', 'c6-nav-esp', 'c6-espaces')
                   + [pause(0.4), anneau('#c6-e-remp', d=1.0), anneau('#c6-bk-claire', d=1.8), anneau('#c6-pl0 .pl-x', d=0.9)]},
        {'titre': 'Le tableau de bord exécutif', 'texte': 'Hébergement, restauration et prestations, consolidés.',
         'voix': "Le tableau de bord exécutif consolide les trois pôles : hébergement, restauration et boutique, "
                 "prestations. La restauration y affiche exactement le chiffre de l'analyse des ventes.",
         'gestes': [cacher('#c6-nav-esp', d=0.15), montrer('#c6-nav-exec', d=0.2, y=0, avec=True),
                    clic('#c6-nav-exec .menu:nth-child(3)', d=0.5), vue('c6-exec'), pause(0.4),
                    compter('#c6-x-tot-v', 0, 13000000, d=1.1, apres=' FCFA'), anneau('#c6-x-pos', d=1.6),
                    anneau('#c6-g-mix', d=1.2)]},
        {'titre': 'RevPAR, pickup et pace', 'texte': 'Chaque indicateur a sa phrase « ? » pour qui le découvre.',
         'voix': "Pour l'hôtel, le revpar combine prix et remplissage. Le pikeup mesure la demande qui arrive cette "
                 "semaine, et les nuitées déjà réservées pour le mois se comparent à l'an dernier, à la même date. Chaque indicateur porte sa "
                 "phrase d'explication.",
         'gestes': [anneau('#c6-x-revpar', d=1.0), montrer('#c6-bulle', d=0.3, y=8), pause(2.2),
                    cacher('#c6-bulle', d=0.2), anneau('#c6-x-pick', d=1.4), anneau('#c6-x-pace', d=1.6)]},
    ],
}
