# -*- coding: utf-8 -*-
"""Chapitre 5 — Stock, ruptures et réapprovisionnement.

Source : fiche de recette n° 6 « Stock, ruptures et réapprovisionnement »
(magasin : tableau de bord Stock — valorisation, références, ruptures,
couverture — puis refus d'accès aux ardoises clients).

Libellés relevés dans : aite_stock_dashboard/static/src/xml/dashboard.xml
(titre, sous-titre, filtres Période / Emplacement / Catégorie, sections
« Vue d'ensemble », « Indicateurs », « Valorisation & flux », onglet
« Alertes de réapprovisionnement », colonnes du tableau « Références à
traiter (triées par urgence) », note « Point de commande = … »),
static/src/js/views/stock_dashboard_view.js (onglets), models/stock_dashboard.py
(statuts Rupture / Critique / Sous seuil / OK et leur calcul),
models/res_config_settings.py (valeurs par défaut : 3 j de délai, 2 j de
sécurité, 7 j d'horizon, critique sous 3 j). Les chiffres des lignes sont
calculés avec ces règles. Menus du profil Magasin relevés sur une base de
recette (load_menus). Le refus reprend la capture de recette
r6-magasin-02 (modèle aite.pos.credit, groupes POS Crédit).
"""

import demo
from ecrans import (cell_puce, erreur_acces, fenetre, graphe_anneau, graphe_barres, graphes, kpi, table, tdb_entete,
                    tdb_filtres, tdb_section, vue_tdb)
from moteur import anneau, clic, compter, defiler, fermer, ouvrir, pause, survol, vue

NOM, ROLE = demo.POSTES['magasin']
MENUS = ["Vue d'ensemble", 'Opérations', 'Tableau de bord AITE', 'Produits']
ONGLETS = ['Tableau de bord', 'Alertes & réappro', 'Stock complet', 'Rotation & dormants', 'Inventaires & écarts',
           'Mouvements']
CATEGORIES = ['Toutes', 'Bières', 'Eaux', 'Jus & softs', 'Snacks & confiseries', 'Vins & spiritueux',
              'Épicerie fine locale']


def tete(prefixe, actif):
    chips = ''.join('<span class="chip%s" id="%s%d">%s</span>' % (' actif' if i == actif else '', prefixe, i, o)
                    for i, o in enumerate(ONGLETS))
    return (tdb_entete('Stock & Inventaire — Tableau de bord', 'Valorisation · alertes de réappro · rotation · écarts & coulage')
            + tdb_filtres([('Période', ["Aujourd'hui", 'Cette semaine', 'Ce mois', '3 mois'], 2),
                           ('Emplacement', ['Tous', 'Stock'], 0), ('Catégorie', CATEGORIES, 0)])
            + '<div class="tdb-filtres"><div class="tdb-rang">%s</div></div>' % chips)


TABLEAU = vue_tdb('c5-dash', '<div id="c5-in">%s</div>' % (
    tete('c5-ta', 0)
    + tdb_section("Vue d'ensemble", [
        kpi('c5-k-cout', "Valeur stock — coût d'achat", '3 185 000 FCFA', '58 références · 1 940 unités', 'bleu'),
        kpi('c5-k-pv', 'Valeur stock — prix de vente', '6 950 000 FCFA', 'marge potentielle +3 765 000 FCFA (54,2 % du PV)',
            'vert'),
        kpi('c5-k-rupt', 'Ruptures & critiques', '2 réfs', '1 rupture · 1 sous 3 j', 'rouge'),
        kpi('c5-k-coul', 'Coulage (période)', '41 500 FCFA', '0,6 % du CA estimé · seuil 2 %', 'vert')])
    + tdb_section('Indicateurs', [
        kpi('c5-k-couv', 'Couverture moyenne', '18,4 j', 'rotation moyenne 1,6× / mois'),
        kpi('c5-k-dorm', 'Stock dormant', '212 000 FCFA', '4 réfs (+60 j de couverture)'),
        kpi('c5-k-seuil', 'Sous seuil de commande', '2 réfs', 'valeur à commander 126 300 FCFA'),
        kpi('c5-k-ecart', "Écarts d'inventaire (période)", '41 500 FCFA', '3 réfs concernées')])
    + tdb_section('Valorisation & flux', [])
    + graphes(graphe_anneau('c5-g-cat', 'Valeur du stock par catégorie',
                            [('Vins & spiritueux', 34, '#714B67'), ('Bières', 22, '#185FA5'),
                             ('Épicerie fine locale', 14, '#3B6D11'), ('Jus & softs', 12, '#854F0B'),
                             ('Snacks & confiseries', 10, '#A32D2D'), ('Eaux', 8, '#0F6E56')]),
              graphe_barres('c5-g-flux', 'Entrées vs Sorties — 6 mois (au coût)',
                            [(62, '#3B6D11'), (55, '#714B67'), (48, '#3B6D11'), (58, '#714B67'), (70, '#3B6D11'),
                             (64, '#714B67'), (52, '#3B6D11'), (60, '#714B67'), (66, '#3B6D11'), (61, '#714B67'),
                             (74, '#3B6D11'), (69, '#714B67')],
                            etiquettes=['Mai', 'Juin', 'Juil', 'Août', 'Sep', 'Oct']))),
    initiale=True)

# Délai 3 j, sécurité 2 j, horizon 7 j, critique sous 3 j (valeurs par défaut du module) :
# point de commande = ventes/j × 5 ; à commander = ventes/j × 10 − stock.
COLS = [('Produit', '1fr'), ('Catégorie', '250px'), ('Stock', '100px', 'd'), ('Ventes/j', '110px', 'd'),
        ('Couverture', '130px', 'd'), ('Point de cmde', '150px', 'd'), ('À commander', '150px', 'd'), ('Statut', '150px')]
LIGNES = [
    ('c5-r1', ['Eau minérale 1,5 L', 'Eaux', '0', '12', '0 j', '60', ('<span class="d"><b>120</b></span>',),
               ('<span><span class="puce rouge">Rupture</span></span>',)]),
    ('c5-r2', ['Bière blonde 65 cl', 'Bières', '30', '14', '2,1 j', '70', ('<span class="d"><b>110</b></span>',),
               ('<span><span class="puce rouge">Critique</span></span>',)]),
    ('c5-r3', ["Jus d'ananas 1 L", 'Jus & softs', '18', '4', '4,5 j', '20', ('<span class="d"><b>22</b></span>',),
               ('<span><span class="puce orange">Sous seuil</span></span>',)]),
    ('c5-r4', ['Arachides grillées', 'Snacks & confiseries', '25', '6', '4,2 j', '30', ('<span class="d"><b>35</b></span>',),
               ('<span><span class="puce orange">Sous seuil</span></span>',)]),
    ('c5-r5', ['Vin rouge 75 cl', 'Vins & spiritueux', '40', '2', '20 j', '10', ('<span class="d"><b>—</b></span>',),
               ('<span><span class="puce vert">OK</span></span>',)]),
]
ALERTES = vue_tdb('c5-alertes', '<div id="c5-in2">%s</div>' % (
    tete('c5-tb', 1)
    + tdb_section('Alertes de réapprovisionnement', [
        kpi('c5-a-rupt', 'En rupture', '1', 'références à zéro', 'rouge'),
        kpi('c5-a-crit', 'Critiques', '1', 'couverture sous 3 jours', 'ambre'),
        kpi('c5-a-seuil', 'Sous seuil de commande', '2 réfs', 'point de commande atteint'),
        kpi('c5-a-cmd', 'Valeur à commander', '126 300 FCFA', 'suggestion de réappro')])
    + '<div class="g-carte" style="height:auto;margin-top:14px;padding:16px 0 4px"><div class="g-titre" style="padding:0 20px">'
      'Références à traiter (triées par urgence)</div>%s</div>'
      % table(COLS, LIGNES, ajouter=None, identifiant='c5-table')
    + '<div class="tdb-sous" id="c5-note" style="margin:12px 4px"><b>Point de commande</b> = ventes moy./jour × (délai '
      'réappro + <b>2</b> j de sécurité). Quantité suggérée : <b>7</b> jours de couverture après livraison — à arrondir '
      'au casier.</div>'))

REFUS = erreur_acces('c5-refus', 'Ardoise POS (vente à crédit)', 'aite.pos.credit',
                     ['POS Crédit/Responsable', 'POS Crédit/Utilisateur'])

ECRAN = fenetre('app-c5', 'Inventaire', MENUS, [TABLEAU, ALERTES], actif='Tableau de bord AITE', societe=demo.SOCIETE,
                initiale=NOM[0], avatar='#0F6E56', calques=REFUS)

CHAPITRE = {
    'court': 'Magasin',
    'poste': 'Magasin',
    'titre': 'Stock, ruptures et réapprovisionnement',
    'personne': (NOM, ROLE),
    'objectif': "Repérer les ruptures et les articles sous seuil, savoir quoi commander, et suivre la valeur du stock.",
    'voix': "Cinquième chapitre : le magasin. Serge veille à ce que le bar ne manque de rien, sans immobiliser "
            "trop d'argent dans les réserves.",
    'app': 'app-c5',
    'ecran': ECRAN,
    'vues_initiales': {'odoo': 'c5-dash'},
    'etapes': [
        {'titre': 'Le tableau de bord Stock', 'texte': "La valeur du stock au coût d'achat et au prix de vente.",
         'voix': "Le tableau de bord Stock et Inventaire donne la valeur du stock, au coût d'achat et au prix de "
                 "vente, donc la marge qui dort dans les réserves. On filtre par période, emplacement et catégorie.",
         'gestes': [compter('#c5-k-cout-v', 0, 3185000, d=1.1, apres=' FCFA'), anneau('#c5-k-pv', d=1.4),
                    anneau('#c5-ta0', d=0.6, decale=0.2), anneau('#c5-dash .tdb-filtres .tdb-rang:nth-child(3)', d=1.0)]},
        {'titre': 'Ruptures, couverture, dormants', 'texte': 'Ce qui manque, ce qui dort, ce qui se perd.',
         'voix': "Les indicateurs disent ce qui manque, ce qui dort et ce qui se perd : ruptures, couverture en "
                 "jours de vente, stock dormant, et coulage comparé à son seuil.",
         'gestes': [defiler('#c5-in', -250, d=0.9), anneau('#c5-k-rupt', d=1.2), anneau('#c5-k-couv', d=1.0),
                    anneau('#c5-k-dorm', d=1.0), anneau('#c5-k-coul', d=1.0)]},
        {'titre': 'Les alertes de réappro', 'texte': "Les références à traiter, de la plus urgente à l'OK.",
         'voix': "L'onglet Alertes et réappro trie les références par urgence : la rupture d'abord, puis le "
                 "critique, puis ce qui passe sous le point de commande.",
         'gestes': [defiler('#c5-in', 0, d=0.6), clic('#c5-ta1'), vue('c5-alertes'), pause(0.3),
                    defiler('#c5-in2', -330, d=0.8),
                    anneau('#c5-r1 .puce', d=0.9), anneau('#c5-r2 .puce', d=0.9), anneau('#c5-r3 .puce', d=0.9),
                    survol('#c5-r4')]},
        {'titre': 'Combien commander', 'texte': 'Point de commande et quantité suggérée, calculés sur les ventes.',
         'voix': "Pour chaque référence, l'outil calcule le point de commande à partir des ventes du jour et du "
                 "délai de livraison, puis la quantité à commander. Serge n'a plus qu'à passer la commande.",
         'gestes': [anneau('#c5-r1 span:nth-child(6)', d=1.0), anneau('#c5-r1 span:nth-child(7)', d=1.2),
                    anneau('#c5-note', d=1.8), anneau('#c5-a-cmd', d=1.2)]},
        {'titre': 'Hors de son périmètre', 'texte': 'Le magasin ne voit pas les ardoises des clients.',
         'voix': "Le magasin n'a pas à connaître les dettes des clients : s'il tente d'ouvrir les ardoises, Odoo "
                 "refuse et nomme les profils autorisés.",
         'gestes': [ouvrir('c5-refus'), pause(0.6), anneau('#c5-refus .refus', d=2.0), clic('#c5-refus-ok'),
                    fermer('c5-refus')]},
    ],
}
