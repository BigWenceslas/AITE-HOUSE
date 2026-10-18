# -*- coding: utf-8 -*-
"""Tutoriel 12 — Bar et restaurant : voyez enfin ce que vous gagnez.

La directrice (Danielle Eyenga, demo.POSTES['direction']) ouvre, dans le Point
de Vente, le menu « Analyse AITE » → « Tableau de bord » du module
aite_pos_analytics : chiffre d'affaires, marge brute, coût des marchandises
(CMV) et transactions ; elle saisit une période (du 01/10 au 13/10/2026) et
clique « Analyser » : tout se recalcule et la bande de comparaison à la
période précédente apparaît ; plus bas, la carte heure × jour et ses deux
repères (pic de deux heures, jour fort) ; l'onglet « Par caisse » compare le
bar et le restaurant ; l'onglet « Articles » cherche les bières et ouvre le
détail d'un article ; l'onglet « Écarts de caisse » classe les sessions de la
plus grave à la moins grave.

Profil rejoué : compte demo.direction de la base MuK. Le menu « Analyse AITE »
est réservé au groupe Utilisateur — Analyses POS (views/
pos_analytics_menus.xml:10-14) ; la Direction l'a parce que le groupe Manager
— Analyses POS, qui l'implique, lui est donné explicitement
(aite_demo_data/models/demo_generator.py:74-80 ; security/
pos_analytics_security.xml:16-30), ou parce que base.group_system implique ce
groupe Manager (pos_analytics_security.xml:33-39). Applications de la barre
MuK : ecrans.APPS_PROFIL['direction'] (relevées sur ref_muk/330-direction-
accueil.png). Menus du Point de Vente : ref_muk/015 et 600 (Tableau de bord,
Commandes, Produits, Analyse AITE, Analyse, Configuration ; libellés natifs :
odoo18/addons/point_of_sale/i18n/fr.po:2049-2050, 2483-2484, 5067-5068,
5652-5653, 6320-6321, 6631-6632).

Sources des libellés (relevés mot pour mot) :

- Écran d'accueil du Point de Vente (kanban des caisses) : odoo18/addons/
  point_of_sale/views/point_of_sale_dashboard.xml:101-131 (nom, bouton
  « Open Register », « Closing » et date, « Balance » et montant) et
  i18n/fr.po:298, 303, 4787 (« Fermeture », « Solde », « Ouvrir la
  caisse ») ; forme d'après ref_muk/600-pos-tableau-de-bord.png (deux
  colonnes, une carte par caisse). Montant au format monétaire d'Odoo, devise
  XAF de symbole « FCFA » (odoo18/odoo/addons/base/data/
  res_currency_data.xml:476-483).
- Menu « Analyse AITE » et ses six entrées : views/pos_analytics_menus.xml
  :10-50 (Tableau de bord, Par caisse, Sessions POS, Par catégorie, Écarts de
  caisse, Pivot & Graph).
- Onglets : static/src/js/services/utils.js:188-197 (huit onglets et leurs
  icônes ; fa-cash-register n'existe pas en Font Awesome 4.7 : l'onglet « Par
  caisse » n'a pas d'icône, voir écarts) ; gabarit static/src/xml/
  dashboard_shell.xml:103-114 ; onglet actif violet #714B67 :
  static/src/scss/pos_dashboard.scss:53-68.
- Barre de filtres : dashboard_shell.xml:119-217 (Période, six raccourcis,
  Du, au — deux <input type="date"> bornés par la première et la dernière
  ouverture de session :132-139 —, Analyser ; Caisse, « Toutes les caisses »
  et une pastille par caisse, ligne affichée à partir de deux caisses :143 ;
  Heure, cinq plages, 18 « h → » 23 « h » OK ; Jour, « Tous », Lun … Dim,
  « Semaine (lun–ven) », « Week-ends ») ; libellés des raccourcis :
  utils.js:131-187 ; « Toute la période » au premier chargement, bornes =
  première et dernière ouverture de session : static/src/js/dashboard.js
  :59-125 ; saisie libre : « Analyser » envoie la clé « custom », aucun
  raccourci ne reste allumé : components/filter_bar.js:79-96 ; couleurs des
  pastilles dans l'ordre des pos.config : models/pos_dashboard.py:651-654,
  905-912 (Bar violet, Restaurant bleu, Boutique vert, comme
  t10_ardoises.py, PALETTE) ; styles : pos_dashboard.scss:70-125, 451-511.
- Tableau de bord : static/src/xml/views.xml:5-420 — quatre grandes cartes
  (« Chiffre d'affaires » « <montant> / jour · <n>j », « Marge brute »
  « Taux: <x>% · <montant>/tx », « CMV (coût marchandises) » « <x>% du CA ·
  <montant>/u », « Transactions » « Panier moy. <montant> · <n> u ») :9-27 ;
  bande « CA vs N-1 · Marge vs N-1 · CMV vs N-1 · Commandes vs N-1 »,
  masquée quand la période précédente n'a pas de vente :29-60 ; cartes
  secondaires (« Ratio CMV/CA » « Bonne maîtrise ✓ » sous 65 %, « Taux de
  marge » « Objectif atteint ✓ » dès 35 %, « Articles actifs » « <n> / <n> »
  — lignes de quantité positive sur lignes de la période,
  dashboard_view.js:272-279 —, « références vendues », « Meilleur article »
  tronqué à 18 caractères, « <montant> CA ») :62-102 ; « Ventes &
  évolution », « CA · Marge · CMV », « Top 8 articles — CA vs Marge »,
  « Évolution mensuelle (CA · CMV · Marge) » et sa légende :104-146 ;
  « Marge & CMV par catégorie », « répartition de la rentabilité »,
  « Catégories — marge & CMV », « tx », « · CMV », « CMV vs Marge »
  :148-200 ; « Performance par caisse », « CA · marge totale & par point de
  vente », « Contribution au CA », « Synthèse par caisse », « du CA »,
  « TOTAL », « marge » :202-248 ; « Répartition des ventes — heure × jour »,
  « intensité = chiffre d'affaires · pour caler plannings & happy hours »,
  « Pic <h>h-<h>h (<x>%) », « Jour fort : <jour> », « Jour \\ h » :250-306 ;
  « Classements produits », « Bières · Marges · Moins vendus », « 🍺 Top
  bières (qté) », « ⭐ Meilleures marges », « 📉 Moins vendus » :308-357
  (marges et moins vendus sur les seules lignes positives :
  pos_dashboard.py:450-485). Formats : utils.js:58-107 (fmt « 1 234 567 »,
  fmtMoney « … F », fmtPct « 56.0% », fmtDelta « ▲ +9.4% », fmtSigned
  « −322 500 F ») ; couleurs : utils.js:11-18 ; graphiques :
  static/src/js/views/dashboard_view.js:125-237 (étiquettes tronquées à neuf
  caractères suivis de « … », graduations « k ») ; carte de chaleur :
  dashboard_view.js:253-268 et models/pos_dashboard.py:772-902 (7 × 24,
  jours Lun … Dim, créneau de deux heures glissant, « Samedi ») ; mois de
  l'évolution au format d'Odoo (« octobre 2026 ») :
  models/pos_dashboard.py:396-412.
- Calculs : marge = CA HT − CMV, CMV = quantité × coût unitaire, coût
  unitaire repris du prix de revient de l'article à la création de la ligne
  de ticket : models/pos_order_line.py:20-69 ; KPI, jours de la période
  (fin incluse), période précédente de même durée et variations :
  models/pos_dashboard.py:30-50, 98-224 ; seules les commandes payées,
  clôturées ou facturées : models/pos_analytics_report.py:133.
- Par caisse : views.xml:422-572 (« Caisse n°1 (CA) », « Caisse la +
  rentable » « taux », « Meilleur panier moyen », « Écart de caisse total »
  « sur la période », « Comparatif des caisses », « marge totale & par caisse
  sur la période », colonnes CAISSE · CA HT · % CA · MARGE · TAUX · CMV ·
  CMDES · PANIER MOY. · QTÉ · ÉCART CAISSE, « TOTAL », « 100% », « Part du CA
  par caisse », « Taux de marge par caisse ») ; badges vert dès 50 %, ambre
  dès 40 % : static/src/js/views/caisse_view.js:158-162 ; badge du TOTAL
  toujours ambre :533 ; une ligne par caisse qui a vendu (read_group par
  caisse) : la Boutique, sans vente sur la période, n'y figure pas ; écart =
  somme des écarts des sessions de la période : models/pos_dashboard.py
  :651-770.
- Articles : views.xml:635-718 (« Toutes catégories », pastilles triées par
  nom, « Rechercher un article ou une catégorie… », « <n> / <total>
  articles », colonnes, tri « CA ▼ » par défaut) ; recherche sur le nom et la
  catégorie : static/src/js/views/products_view.js:55-121 ; badge du taux
  vert dès 50 %, ambre dès 30 % :113-117 ; couleurs des catégories :
  utils.js:20-52.
- Panneau d'un article : dashboard_shell.xml:248-331 (« × », catégorie, CA,
  Marge, CMV, « Quantité vendue » « <n> unités », « Taux de marge », « Prix
  de vente moyen », « Coût moyen unitaire (CMV) », « Marge unitaire »,
  « / unité », « Période analysée ») ; static/src/js/components/
  product_panel.js:67-90 ; models/pos_dashboard.py:612-644 (prix, coût et
  marge à l'unité = montant ÷ quantité).
- Écarts de caisse : views.xml:876-941 (« Écart négatif total » « sessions
  clôturées », « Sessions avec écart » « <n> nég. · <n> pos. », « Écart
  moyen » « par session négative », « Plus grand écart » « à investiguer en
  priorité », bandeau à partir de six sessions négatives, colonnes Session ·
  Date · Caissier · CA · Écart (F) · Sévérité) ; libellés et couleurs des
  sévérités : static/src/js/views/discrepancies_view.js:8-14 ; seuils
  200 000 F (Critique) et 100 000 F (Élevé), écart = compté − théorique :
  models/pos_session.py:19-25, 120-155 ; tri Critique > Élevé > Modéré >
  Excédent puis montant : models/pos_dashboard.py:523-583 ; nom des sessions
  « <caisse>/<n° sur cinq chiffres> » d'après ref_muk/017 et 019.

Sources des affirmations : douleurs de l'accroche — docs/guides/
AITE_POS_Analytics_fiche_produit.pdf p. 2 (« Vendre sans savoir ce qu'on
gagne » : « quelle marge réelle dégage chaque article ? Quelle caisse tire le
chiffre ? À quelle heure le bar est-il rentable ? Et où partent les écarts de
caisse ? » ; « CA visible mais marge inconnue […] écarts de caisse noyés. On
pilote au ressenti, et la rentabilité se découvre trop tard. ») ; la
question de l'heure devient « Le bar tourne à quelle heure ? », car la carte
heure × jour montre le chiffre d'affaires (price_subtotal,
pos_dashboard.py:795-800, 843-845), pas la marge ; slogan « Décider sur des
chiffres, pas au ressenti » — même fiche p. 1 ; besoin du client « sur une
période donnée, déterminer la marge totale ET par caisse » —
models/pos_dashboard.py:666-667 et README.md:79. Promesse et voix : marge et
CMV calculés seuls à la ligne (pos_order_line.py:49-69) — « chaque vente dit
ce qu'elle rapporte », sans montrer de ticket ni promettre que marge + CMV =
CA dans le flux réel de caisse (voir le rapport) ; comparaison à la période
précédente de même durée (pos_dashboard.py:130-153) ; classement des écarts
(pos_session.py:120-155). Le « coût figé à la vente » de la fiche produit
n'est pas repris : la vérification l'a jugé non prouvé dans le flux réel de
caisse. La voix ne donne pas l'heure du pic : la carte l'affiche en UTC
(écart 11). Résultats : 8 onglets (utils.js:188-197), 7 × 24 = 168 cases et
créneau de deux heures (pos_dashboard.py:800-873), 4 niveaux de gravité pour
un écart non nul — Excédent, Modéré, Élevé, Critique (pos_session.py:78-84).

Données : demo.py (Démo Hôtellerie SARL, Danielle Eyenga directrice, Hervé
Tchakounté caissier du bar) ; trois caisses « Bar de la terrasse »,
« Restaurant » et « Boutique », comme t04_note_chambre.py:200 et
t10_ardoises.py (BAR, RESTO, BOUT) (la Boutique n'a rien vendu sur la période) ;
chiffres de la période repris de la présentation, scenarios/
c6_direction.py:100-108 (CA 3 120 000, marge 1 747 200 soit 56,0 %, CMV
1 372 800 soit 2 681 F/u, 128 tickets, panier 24 375, 512 unités, 42 articles
actifs sur 48, meilleur article « Bière blonde 65 cl » à 486 000 F) et de
t15_direction.py (CA en hausse de 9,4 %) ; articles, prix et coûts du bar et
de la cave repris de t13_stock.py (ARTICLES) (Bière blonde 65 cl : 1 500 F pour
650 F, soit 850 F de marge, comme t04:285, au TICKET de t10_ardoises.py et
au PRIX de t14_achats.py), plats de la
carte de t04:274-281 ; articles sans taxe, comme au ticket de t04 (t04:37-44,
282) : le CA des sessions (TTC) égale donc le CA HT. Paulin Essama et Larissa
Mbida (caissiers), les autres prix, quantités, sessions et montants sont
fictifs. Le jour rejoué est le mercredi 14/10/2026 au matin, navigateur en
français à Douala ; la période saisie va du 01/10 au 13/10/2026 (treize
jours ; « au » garde la dernière ouverture de session, 13/10) ; rien n'a été
vendu le 30/09 (inventaire de fin de mois, fictif), si bien que le « Ce mois »
de la présentation (30/09 → 14/10) donne les mêmes totaux. « Toute la
période » va de la première ouverture de session (04/05/2026 : les ardoises de
mai, en-tête de t10_ardoises.py) à la dernière (13/10/2026), 163 jours. La
période précédente (18/09 → 30/09) donne CA 2 852 000, marge 1 560 000, CMV
1 292 000 et 119 commandes, d'où ▲ +9.4 %, +12.0 %, +6.3 % et +7.6 %. Les
sessions en écart sont toutes clôturées (le matin du 14/10, aucune caisse
n'est encore ouverte). Les chiffres se tiennent : ils sont calculés
ci-dessous à partir des articles (sommes contrôlées par assert).

Captures de référence (modèle visuel, jamais incrustées) : ref_muk/015 à
020, 330-direction-accueil.png, 600-pos-tableau-de-bord.png ; chapitre déjà
rejoué dans la présentation : scenarios/c6_direction.py.

Ce que la vidéo montre, et ce qu'elle évite :
- Le contenu du tableau de bord défile sous la barre d'onglets, barre de
  filtres comprise (dashboard_shell.xml:12-29, scss:32-37) ; avant de changer
  d'onglet, on remonte en haut de page. Un changement de filtre, d'onglet ou de
  recherche remplace le contenu d'un coup, comme un nouveau rendu OWL.
- La période est saisie dans « Du » plutôt que par le raccourci « Ce mois »,
  qui afficherait « Du 30/09/2026 » (écart 1).
- Quatre zooms (carte Marge brute, carte heure × jour avec ses jours, détail
  de l'article, première ligne des écarts) ; pas de zoom sur le comparatif des
  caisses, plus large que l'écran zoomé.
- On ne clique ni « Semaine (lun–ven) » ni « Week-ends » (leurs jours
  actifs deviennent invisibles, écart 2).
- Réglages de lisibilité : les textes gris clairs du module (#888780 sur
  blanc, 3,6:1) sont foncés en #6B6A65 et le texte gris des cases claires de
  la carte de chaleur en #3D3C39, pour passer le contrôle de contraste AA ;
  les étiquettes des cases sont grossies (19 px, gras) pour rester lisibles
  à l'écran ; aucune case n'a une intensité comprise entre 0,55 et 0,70, où
  ni le texte blanc ni le texte foncé ne passent le contrôle.

Écarts relevés, rejoués tels quels ou évités (voir le rapport) :
1. « Ce mois » démarre la veille du 1er à Douala (UTC+1) : « Du 30/09/2026 »
   (utils.js:132, 143-156, toISOString d'un minuit local). Évité : la
   période est saisie.
2. Le bouton « Tous » de la ligne Jour est invisible (classe active sur
   var(--aite-teal), jamais définie : blanc sur blanc), d'où le vide entre
   « JOUR » et « Lun » (pos_dashboard.scss:12-23, 486-494).
3. « CA vs N-1 » compare à la période précédente de même durée, pas à
   l'année précédente (pos_dashboard.py:130-146) ; une hausse du CMV s'y
   affiche en vert comme une bonne nouvelle (views.xml:46-51,
   scss:537-538).
4. Le « CA » des sessions (onglet Écarts de caisse) est TTC (amount_total)
   alors que celui du tableau de bord et de « Par caisse » est HT
   (pos_session.py:106 ; pos_dashboard.py:107-114) ; invisible ici, les
   articles étant sans taxe.
5. Pourcentages à point décimal sans espace (« 56.0% », « Taux: 56.0% »),
   abréviations « /tx », « /u », « Cmdes », symbole « F » forcé, anglais
   résiduel « Pivot & Graph » et « happy hours » (utils.js:67-75 ;
   views.xml:17, 21, 261, 491 ; pos_analytics_menus.xml:47).
6. Pas d'icône sur l'onglet « Par caisse » ni sur le module « Performance
   par caisse » (fa-cash-register absent de Font Awesome 4.7 ;
   utils.js:190, views.xml:207).
7. Le badge de taux de la ligne TOTAL est toujours ambre, même à 56 %
   (views.xml:533, 242).
8. « Meilleur article » tronque le nom à 18 caractères (views.xml:96).
9. Deux menus d'analyse se suivent dans le Point de Vente : « Analyse
   AITE » et le natif « Analyse » (pos_analytics_menus.xml:10-14).
10. Contraste du gris du module (#888780 sur blanc : 3,6:1, sous le seuil
   AA de 4,5:1) ; texte gris (#5f5e5a) et blanc des cases moyennes de la
   carte de chaleur sous le seuil (dashboard_view.js:253-262).
11. La carte heure × jour et le repère « Pic » sont en UTC, une heure plus tôt
   qu'à Douala : la vue SQL convertit l'heure dans le fuseau de
   self.env.user.tz au moment de init() (pos_analytics_report.py:93,
   118-121), qui tourne en superutilisateur (odoo/modules/registry.py:588) ;
   OdooBot n'a pas de fuseau (base/data/res_partner_data.xml:15-20 ;
   odoo/service/db.py:87-89 ne règle que les utilisateurs actifs), d'où le
   repli UTC. Les ventes de 20 h à 22 h à Douala s'affichent « Pic
   19h-21h » ; une vente de samedi 0 h 30 tombe sur « Ven », 23 h.
"""

import math
from decimal import ROUND_HALF_UP, Decimal

import demo
from ecrans import APPS_PROFIL, ICONES, e, entree, fenetre_muk, navigateur, recherche, vue_libre
from marketing import bulle, dezoom, reaction, zoom
from moteur import anneau, cacher, clic, classe, compter, curseur, defiler, montrer, pause, saisir, texte, vue

NOM, ROLE = demo.POSTES['direction']
CAISSIER = demo.POSTES['caisse'][0]          # Hervé Tchakounté, caissier du bar
SOCIETE = demo.SOCIETE
NB = ' '                                # l'espace insécable des montants (aite-motion.js : nombre)
MENUS = ['Tableau de bord', 'Commandes', 'Produits', 'Analyse AITE', 'Analyse', 'Configuration']
MENU_AITE = '#t12-app .o-haut > span:nth-child(6)'

# Couleurs du module (utils.js:11-18).
PRIMARY, SUCCESS, INFO, WARNING, DANGER, TEAL = '#714B67', '#3B6D11', '#185FA5', '#854F0B', '#A32D2D', '#0F6E56'


# ------------------------------------------------------------ formats --
def _arrondi(n, chiffres=0):
    """L'arrondi de JavaScript (Math.round, toFixed) : au plus proche, l'égalité vers le haut."""
    q = Decimal(1).scaleb(-chiffres)
    return Decimal(n).quantize(q, rounding=ROUND_HALF_UP)


def fmt(n):
    """utils.js fmt : groupes fr-FR, sans décimale."""
    v = int(_arrondi(n))
    s = '{:,}'.format(abs(v)).replace(',', NB)
    return ('-' if v < 0 else '') + s


def fmt_money(n):
    return fmt(n) + ' F'


def fmt_pct(n):
    return '%s%%' % _arrondi(n, 1)


def fmt_delta(n):
    fleche = '▲' if n > 0 else ('▼' if n < 0 else '■')
    return '%s %s%s%%' % (fleche, '+' if n > 0 else '', _arrondi(n, 1))


def fmt_signed(n):
    v = int(_arrondi(n))
    if v == 0:
        return '0 F'
    return '%s%s F' % ('+' if v > 0 else '−', '{:,}'.format(abs(v)).replace(',', NB))


def pct(a, b):
    return a / float(b) * 100.0 if b else 0.0


# ------------------------------------------------------------- données --
# Les articles vendus du 01/10 au 13/10/2026 : (nom, catégorie, prix de vente,
# coût unitaire, quantité au bar, quantité au restaurant, remboursé). Noms,
# prix et coûts du bar et de la cave : scenarios/t13_stock.py (ARTICLES) (Bière
# blonde 65 cl à 1 500 F pour 650 F, comme t04:285, le TICKET de t10_ardoises.py
# et les PRIX de t14_achats.py) ;
# plats et accompagnements : la carte de t04_note_chambre.py:274-281 (Poisson
# braisé et Plantain frit à 7 000 et 1 500 F, t04:283-284), prix fictifs pour
# les autres. Catégories d'article (product.category, celles que lit le
# module) : celles de t13 pour le bar et la cave, celles de la carte de t04
# (Grillades, Plats, Accompagnements) pour la cuisine ; catégories racines,
# pour que « Bières » prenne sa couleur (utils.js:20-33). Articles sans taxe,
# comme au ticket de t04 (t04:37-44, 282) : HT = TTC. « remboursé » : vendu
# puis remboursé dans la période, d'où une ligne à zéro (42 articles actifs
# sur 48 lignes, comme c6_direction.py:107).
BAR, RESTO, BOUT = 'Bar de la terrasse', 'Restaurant', 'Boutique'
ARTICLES = [
    ('Bière blonde 65 cl', 'Bières', 1500, 650, 290, 34, False),
    ('Bière brune 65 cl', 'Bières', 1500, 700, 7, 0, False),
    ('Bière blonde 33 cl', 'Bières', 1000, 400, 5, 0, False),
    ('Bière sans alcool 33 cl', 'Bières', 1000, 450, 2, 0, False),
    ('Eau minérale 1,5 L', 'Eaux', 1000, 300, 0, 4, False),
    ('Eau minérale 50 cl', 'Eaux', 500, 150, 1, 0, False),
    ('Eau gazeuse 1 L', 'Eaux', 1500, 500, 0, 1, False),
    ("Jus d'ananas 1 L", 'Jus & softs', 2000, 900, 0, 2, False),
    ('Soda orange 33 cl', 'Jus & softs', 1000, 300, 2, 0, False),
    ('Cola 33 cl', 'Jus & softs', 1000, 300, 2, 1, False),
    ('Tonic 33 cl', 'Jus & softs', 1000, 350, 2, 0, False),
    ('Jus de bissap 50 cl', 'Jus & softs', 1000, 400, 0, 1, False),
    ('Jus de gingembre 50 cl', 'Jus & softs', 1000, 400, 0, 1, False),
    ('Citronnade 50 cl', 'Jus & softs', 1000, 300, 0, 0, RESTO),
    ('Arachides grillées', 'Snacks & confiseries', 700, 250, 1, 0, False),
    ('Chips de plantain', 'Snacks & confiseries', 800, 300, 1, 0, False),
    ('Biscuits apéritifs', 'Snacks & confiseries', 1000, 400, 0, 0, BAR),
    ('Chocolat noir 100 g', 'Snacks & confiseries', 2000, 900, 0, 0, BAR),
    ('Vin rouge 75 cl', 'Vins & spiritueux', 12000, 4500, 10, 16, False),
    ('Vin blanc 75 cl', 'Vins & spiritueux', 11000, 4000, 4, 8, False),
    ('Vin rosé 75 cl', 'Vins & spiritueux', 11000, 4000, 0, 0, RESTO),
    ('Champagne brut 75 cl', 'Vins & spiritueux', 45000, 22000, 10, 0, False),
    ('Whisky 12 ans 70 cl', 'Vins & spiritueux', 40000, 18000, 11, 0, False),
    ('Cognac VSOP 70 cl', 'Vins & spiritueux', 60000, 28000, 7, 0, False),
    ('Rhum ambré 70 cl', 'Vins & spiritueux', 20000, 9000, 11, 0, False),
    ('Gin 70 cl', 'Vins & spiritueux', 22000, 10000, 13, 0, False),
    ('Liqueur de café 70 cl', 'Vins & spiritueux', 18000, 8000, 0, 0, BAR),
    ('Whisky 12 ans (verre)', 'Vins & spiritueux', 5000, 1600, 11, 0, False),
    ('Cocktail maison', 'Vins & spiritueux', 4000, 1200, 5, 0, False),
    ('Poisson braisé', 'Grillades', 7000, 3200, 3, 8, False),
    ('Poulet braisé', 'Grillades', 6000, 2700, 0, 1, False),
    ('Brochettes de bœuf', 'Grillades', 3000, 1300, 1, 0, False),
    ('Soya', 'Grillades', 2000, 900, 2, 0, False),
    ('Porc braisé', 'Grillades', 5000, 2300, 0, 2, False),
    ('Maquereau braisé', 'Grillades', 5000, 2200, 0, 1, False),
    ('Ndolè', 'Plats', 6000, 2600, 0, 4, False),
    ('Poulet DG', 'Plats', 8000, 3600, 0, 10, False),
    ('Eru', 'Plats', 5000, 2100, 0, 3, False),
    ('Mbongo tchobi', 'Plats', 6000, 2700, 0, 2, False),
    ('Koki', 'Plats', 3000, 1150, 0, 1, False),
    ('Okok', 'Plats', 4000, 1700, 0, 1, False),
    ('Kondrè', 'Plats', 6000, 2700, 0, 1, False),
    ('Plantain frit', 'Accompagnements', 1500, 500, 1, 2, False),
    ('Bâton de manioc', 'Accompagnements', 500, 200, 0, 1, False),
    ('Miondo', 'Accompagnements', 500, 200, 0, 0, RESTO),
    ('Frites de plantain', 'Accompagnements', 1500, 500, 1, 2, False),
    ('Riz blanc', 'Accompagnements', 1000, 350, 0, 1, False),
    ('Frites de pomme', 'Accompagnements', 1500, 600, 0, 1, False),
]


def _produit(nom, cat, prix, cout, q_bar, q_resto, rembourse):
    q = q_bar + q_resto
    p = {'nom': nom, 'cat': cat, 'prix': prix, 'cout': cout, 'qty': q, 'ca': q * prix, 'cmv': q * cout,
         'marge': q * (prix - cout), 'par': {BAR: q_bar, RESTO: q_resto}, 'rembourse': rembourse}
    p['taux'] = pct(p['marge'], p['ca'])
    return p


# Trié comme get_products_full (pos_dashboard.py:494-521) : CA décroissant.
PRODUITS = sorted((_produit(*a) for a in ARTICLES), key=lambda x: -x['ca'])
TICKETS = {BAR: 108, RESTO: 20}


def _somme(liste, cle):
    return sum(x[cle] for x in liste)


CA, CMV, MARGE, QTE = (_somme(PRODUITS, k) for k in ('ca', 'cmv', 'marge', 'qty'))
CMDES = sum(TICKETS.values())
ACTIFS = len([p for p in PRODUITS if p['qty'] > 0])
# Les chiffres de la présentation (c6_direction.py:100-108) : CA, CMV, tickets,
# unités, 42 articles actifs sur 48, meilleur article.
assert (CA, CMV, MARGE, CMDES, QTE) == (3120000, 1372800, 1747200, 128, 512)
assert (ACTIFS, len(PRODUITS)) == (42, 48)
assert (PRODUITS[0]['nom'], PRODUITS[0]['ca']) == ('Bière blonde 65 cl', 486000)
JOURS_PERIODE = 13                                                     # 01/10 → 13/10 inclus
# La période précédente (18/09 → 30/09, même durée) : CA, marge, CMV, commandes.
PREC = {'ca': 2852000, 'marge': 1560000, 'cmv': 1292000, 'cmdes': 119}
assert PREC['ca'] == PREC['marge'] + PREC['cmv']
DELTAS = [('CA vs N-1', pct(CA - PREC['ca'], PREC['ca'])), ('Marge vs N-1', pct(MARGE - PREC['marge'], PREC['marge'])),
          ('CMV vs N-1', pct(CMV - PREC['cmv'], PREC['cmv'])),
          ('Commandes vs N-1', pct(CMDES - PREC['cmdes'], PREC['cmdes']))]

# Les sessions de la période qui portent un écart (compté − théorique) :
# (nom, date, caissier, caisse, CA de la session, écart).
SESSIONS = [
    ('Bar de la terrasse/00131', '10/10/2026', 'Paulin Essama', BAR, 312400, -212500),
    ('Bar de la terrasse/00124', '03/10/2026', 'Paulin Essama', BAR, 298600, -104500),
    ('Restaurant/00128', '07/10/2026', 'Larissa Mbida', RESTO, 61500, -8500),
    ('Bar de la terrasse/00127', '06/10/2026', CAISSIER, BAR, 141200, -2000),
    ('Restaurant/00122', '01/10/2026', 'Larissa Mbida', RESTO, 38000, 5000),
]


def severite(ecart):
    """pos_session.py:137-155."""
    if ecart == 0:
        return 'none'
    if ecart > 0:
        return 'over'
    return 'high' if -ecart >= 200000 else ('med' if -ecart >= 100000 else 'low')


SEV_LIB = {'none': 'OK', 'over': 'Excédent', 'low': 'Modéré', 'med': 'Élevé', 'high': 'Critique'}
SEV_BADGE = {'over': 'b-blu', 'low': 'b-amb', 'med': 'b-amb', 'high': 'b-red'}
_ORDRE = {'high': 0, 'med': 1, 'low': 2, 'over': 3, 'none': 4}
assert [s[0] for s in SESSIONS] == [s[0] for s in sorted(SESSIONS, key=lambda s: (_ORDRE[severite(s[5])], -abs(s[5])))]


def par_caisse():
    """get_caisse_breakdown (pos_dashboard.py:651-770) : une ligne par caisse qui a vendu, triée par CA ;
    la Boutique, sans vente sur la période, n'y figure pas."""
    lignes = []
    for i, k in enumerate(sorted((BAR, RESTO), key=lambda k: -sum(p['par'][k] * p['prix'] for p in PRODUITS))):
        ca = sum(p['par'][k] * p['prix'] for p in PRODUITS)
        cmv = sum(p['par'][k] * p['cout'] for p in PRODUITS)
        qty = sum(p['par'][k] for p in PRODUITS)
        lignes.append({'nom': k, 'couleur': [PRIMARY, INFO][i], 'ca': ca, 'marge': ca - cmv, 'cmv': cmv,
                       'qty': qty, 'taux': pct(ca - cmv, ca), 'cmdes': TICKETS[k],
                       'panier': ca / float(TICKETS[k]), 'part': pct(ca, CA),
                       'ecart': sum(s[5] for s in SESSIONS if s[3] == k)})
    return lignes


CAISSES = par_caisse()
ECART_TOTAL = sum(c['ecart'] for c in CAISSES)
assert sum(c['ca'] for c in CAISSES) == CA and sum(c['qty'] for c in CAISSES) == QTE


def par_categorie():
    """get_category_breakdown (pos_dashboard.py:256-294), trié par CA."""
    cats = []
    for c in sorted({p['cat'] for p in PRODUITS}, key=lambda c: -_somme([p for p in PRODUITS if p['cat'] == c], 'ca')):
        lot = [p for p in PRODUITS if p['cat'] == c]
        ca, marge = _somme(lot, 'ca'), _somme(lot, 'marge')
        cats.append({'nom': c, 'ca': ca, 'cmv': _somme(lot, 'cmv'), 'marge': marge, 'taux': pct(marge, ca)})
    return cats


CATEGORIES = par_categorie()

# Couleurs des catégories (utils.js:20-52) : par nom exact pour « Bières » ;
# sinon la palette circulaire, au rang de la ligne.
PALETTE_NOM = {'bières': ('#714B67', '#EEEDFE', '#3C3489'), 'softs': ('#1D9E75', '#E1F5EE', '#0F6E56'),
               'vins': ('#185FA5', '#E6F1FB', '#0C447C'), 'eau': ('#888780', '#F1EFE8', '#5F5E5A')}
REPLI = ['#714B67', '#1D9E75', '#BA7517', '#185FA5', '#888780', '#A32D2D', '#0F6E56', '#854F0B']


def couleurs_cat(nom, rang):
    return PALETTE_NOM.get(nom.lower(), (REPLI[rang % len(REPLI)], '#F1EFE8', '#5F5E5A'))


# La carte de chaleur. Les ventes sont posées à l'heure de Douala (UTC+1) :
# déjeuner au restaurant, soirée au bar, après minuit les nuits du vendredi et
# du samedi. La vue SQL convertit l'heure dans le fuseau de l'utilisateur qui
# a installé le module, OdooBot, qui n'en a pas : la carte et les repères
# sont donc en UTC, une heure plus tôt (écart 11). Treize jours de vente :
# deux de chaque jour, un seul mercredi (le 07/10).
NB_JOURS = [2, 2, 1, 2, 2, 2, 2]                    # Lun … Dim, du 01/10 au 13/10
POIDS_JOUR = [0.75, 0.8, 0.85, 0.9, 1.35, 1.6, 1.0]
POIDS_HEURE = {10: 0.2, 11: 0.6, 12: 1.6, 13: 1.9, 14: 1.0, 15: 0.5, 16: 0.5, 17: 0.8, 18: 1.4, 19: 2.0, 20: 2.6,
               21: 2.5, 22: 1.6, 23: 0.8}
JOURS_SEMAINE = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim']


def carte_chaleur():
    local = [[0.0] * 24 for _ in range(7)]
    for d, pj in enumerate(POIDS_JOUR):
        for h, ph in POIDS_HEURE.items():
            local[d][h] = NB_JOURS[d] * pj * ph
    # après minuit : la nuit du vendredi au samedi (Sam 0 h) et du samedi au dimanche (Dim 0 h)
    local[5][0] = NB_JOURS[4] * 0.3 * POIDS_JOUR[4]
    local[6][0] = NB_JOURS[5] * 0.3 * POIDS_JOUR[5]
    # heure de Douala → UTC (pos_analytics_report.py:93, 118-121) : une heure plus tôt
    brut = [[0.0] * 24 for _ in range(7)]
    for d in range(7):
        for h in range(24):
            if h:
                brut[d][h - 1] += local[d][h]
            else:
                brut[(d - 1) % 7][23] += local[d][h]
    total = sum(map(sum, brut))
    mat = [[int(round(v * CA / total, -2)) for v in ligne] for ligne in brut]
    # Pas de case d'intensité entre 0,55 et 0,70 (voir l'en-tête) : on la pousse
    # au bord le plus proche, en gardant le total.
    vmax = max(map(max, mat))
    for d in range(7):
        for h in range(24):
            a = mat[d][h] / float(vmax)
            if 0.55 < a < 0.70:
                mat[d][h] = (int(math.floor(vmax * 0.55 / 100.0)) * 100 if a < 0.625
                             else int(math.ceil(vmax * 0.70 / 100.0)) * 100)
    # le reliquat, réparti sur les cases claires au prorata, puis la poussière sur la plus forte d'entre elles
    claires = [(d, h) for d in range(7) for h in range(24) if 0 < mat[d][h] < 0.45 * vmax]
    base = float(sum(mat[d][h] for d, h in claires))
    reliquat = CA - sum(map(sum, mat))
    for d, h in claires:
        mat[d][h] += int(round(reliquat * mat[d][h] / base, -2))
    d, h = max(claires, key=lambda c: mat[c[0]][c[1]])
    mat[d][h] += CA - sum(map(sum, mat))
    return mat


CHALEUR = carte_chaleur()
CHALEUR_MAX = max(map(max, CHALEUR))
assert sum(map(sum, CHALEUR)) == CA
for _l in CHALEUR:
    for _v in _l:
        assert not 0.55 < _v / float(CHALEUR_MAX) < 0.70


def insights():
    """get_time_insights (pos_dashboard.py:821-902)."""
    par_heure = [sum(CHALEUR[d][h] for d in range(7)) for h in range(24)]
    best = max(range(24), key=lambda h: (par_heure[h] + par_heure[(h + 1) % 24], -h))
    pic = 'Pic %dh-%dh (%s)' % (best, (best + 2) % 24, fmt_pct(pct(par_heure[best] + par_heure[(best + 1) % 24], CA)))
    noms = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
    fort = max(range(7), key=lambda d: sum(CHALEUR[d]))
    return pic, 'Jour fort : %s' % noms[fort], best, fort


PIC, JOUR_FORT, H_PIC, J_FORT = insights()
assert (H_PIC, J_FORT) == (19, 5)          # 20 h – 22 h à Douala, affiché « 19h-21h » ; samedi

# « Toute la période » : du 04/05/2026 (première ouverture de session : les
# ardoises de mai, en-tête de t10_ardoises.py) au 13/10/2026 (dernière
# ouverture), 163 jours ; rien de vendu le 30/09, jour d'inventaire (fictif),
# si bien que octobre = la période analysée ; mois au format d'Odoo (date:month).
EVO_TOUT = [('mai 2026', 5480000, 2466000), ('juin 2026', 6120000, 2692800), ('juillet 2026', 6950000, 3058000),
            ('août 2026', 7310000, 3216400), ('septembre 2026', 6104000, 2685800), ('octobre 2026', CA, CMV)]
TOUT = {'ca': sum(x[1] for x in EVO_TOUT), 'cmv': sum(x[2] for x in EVO_TOUT), 'cmdes': 1440, 'qty': 5760,
        'jours': 163, 'articles': 48, 'actifs': 48}
TOUT['marge'] = TOUT['ca'] - TOUT['cmv']
EVO_MOIS = [('octobre 2026', CA, CMV)]
# Top 8 de toute la période : (nom, quantité, prix, coût moyen) ; la bière
# blonde au coût d'achat de chaque mois (PRIX de t14_achats.py : 600 → 650 F).
TOP8_TOUT = [('Bière blonde 65 cl', 3960, 1500, 621), ('Whisky 12 ans 70 cl', 124, 40000, 18000),
             ('Champagne brut 75 cl', 107, 45000, 22000), ('Vin rouge 75 cl', 342, 12000, 4500),
             ('Cognac VSOP 70 cl', 65, 60000, 28000), ('Gin 70 cl', 139, 22000, 10000),
             ('Rhum ambré 70 cl', 130, 20000, 9000), ('Poulet DG', 198, 8000, 3600)]
TOP8_TOUT = [(n, q * p, q * (p - c)) for n, q, p, c in TOP8_TOUT]
assert TOP8_TOUT == sorted(TOP8_TOUT, key=lambda x: -x[1])
TOUT['meilleur'] = TOP8_TOUT[0][:2]
TOP8_MOIS = [(p['nom'], p['ca'], p['marge']) for p in PRODUITS[:8]]


# ------------------------------------------------------------- icônes --
# Dessinées ici (fa-tachometer, fa-th-large, fa-pie-chart, fa-trophy,
# fa-table, fa-calendar) : ecrans.ICONES n'a pas ces glyphes, on ne le modifie pas.
JAUGE = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round">'
         '<path d="M3.5 17a8.5 8.5 0 1117 0"/><path d="M12 17l4.5-5.5"/><circle cx="12" cy="17" r="1.6" '
         'fill="currentColor"/></svg>')
TH_LARGE = ('<svg viewBox="0 0 24 24" fill="currentColor"><rect x="3" y="3" width="8" height="8" rx="1"/>'
            '<rect x="13" y="3" width="8" height="8" rx="1"/><rect x="3" y="13" width="8" height="8" rx="1"/>'
            '<rect x="13" y="13" width="8" height="8" rx="1"/></svg>')
CAMEMBERT = ('<svg viewBox="0 0 24 24" fill="#fff"><path d="M11 3.1A9 9 0 1020.9 13H11z"/>'
             '<path d="M13 1.5V11h9.5A9.5 9.5 0 0013 1.5z"/></svg>')
TROPHEE = ('<svg viewBox="0 0 24 24" fill="#fff"><path d="M6 3h12v4a6 6 0 01-12 0zM4 4h2v3H4.5A2.5 2.5 0 012 '
           '4.5V4zm16 0h-2v3h1.5A2.5 2.5 0 0022 4.5V4zM10.5 12.5h3V17H17v3H7v-3h3.5z"/></svg>')
TABLE = ('<svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2"><rect x="3" y="4" width="18" '
         'height="16" rx="1.5"/><path d="M3 9h18M3 14.5h18M9 9v11"/></svg>')
CAL = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3.5" y="5" width="17" '
       'height="15.5" rx="1.5"/><path d="M3.5 10h17M8 3v4M16 3v4"/></svg>')
KANBAN = ('<svg viewBox="0 0 24 24" fill="currentColor"><rect x="3" y="4" width="7.5" height="16" rx="1"/>'
          '<rect x="12.5" y="4" width="8.5" height="7.5" rx="1"/></svg>')


def ico(svg, classe_='ico'):
    return '<span class="%s">%s</span>' % (classe_, svg)


# --------------------------------------------- Point de Vente (accueil) --
def carte_pos(nom, fermeture, solde):
    return ('<div class="t12-pc"><div class="t12-pc-n">%s</div><span class="t12-pc-bt">Ouvrir la caisse</span>'
            '<div class="t12-pc-i"><span>Fermeture</span><span>%s</span><span>Solde</span><span>%s</span></div></div>'
            % (e(nom), e(fermeture), e(solde)))


CP_POS = ('<div class="cp"><span class="titre">Point de Vente</span>%s<span class="pager">1-3 / 3</span>'
          '<span class="t12-vues"><i class="on">%s</i><i>%s</i></span></div>'
          % (recherche(), KANBAN, ICONES['liste']))
# Trois caisses, comme t04_note_chambre.py:200 et t10_ardoises.py (BOUT) ;
# la Boutique a clôturé sa dernière session le 26/09 (fictif).
POS = vue_libre('t12-pos', CP_POS + '<div class="t12-pk">%s%s%s</div>' % (
    carte_pos(BAR, '13/10/2026', '25' + NB + '000' + NB + 'FCFA'),
    carte_pos(RESTO, '13/10/2026', '20' + NB + '000' + NB + 'FCFA'),
    carte_pos(BOUT, '26/09/2026', '10' + NB + '000' + NB + 'FCFA')), initiale=True)

# Le menu déroulant « Analyse AITE » (pos_analytics_menus.xml:16-50).
ENTREES = [('tdb', 'Tableau de bord'), ('caisse', 'Par caisse'), ('sess', 'Sessions POS'), ('cat', 'Par catégorie'),
           ('ecarts', 'Écarts de caisse'), ('pivot', 'Pivot & Graph')]
MENU = ('<div class="t12-menu masque" id="t12-menu" data-layout-allow-overlap data-layout-allow-occlusion>%s</div>'
        % ''.join('<div id="t12-menu-%s">%s</div>' % (i, e(lib)) for i, lib in ENTREES))

# ------------------------------------------------------ Analyse AITE --
ONGLETS = [('dash', 'Tableau de bord', JAUGE), ('caisse', 'Par caisse', None), ('sess', 'Sessions POS', ICONES['liste']),
           ('art', 'Articles', ICONES['boite']), ('marg', 'Marges & CMV', ICONES['graphe']),
           ('cat', 'Par catégorie', TH_LARGE), ('ecarts', 'Écarts de caisse', ICONES['alerte']),
           ('pay', 'Paiements', ICONES['carte'])]
TABS = '<div class="t12-tabs">%s</div>' % ''.join(
    '<span class="t12-tab%s%s" id="t12-tab-%s">%s%s</span>'
    % (' on' if k == 'dash' else '', '' if svg else ' t12-sans', k, ico(svg) if svg else '', e(lib))
    for k, lib, svg in ONGLETS)


def fb(libelle, ident=None, on=False, alt=False, jour=False, point=None):
    """Un bouton de filtre (o_aite_fbtn) ; ``alt`` : la variante bleue de la ligne Heure."""
    cls = 't12-fb' + (' on' if on and not alt else '') + (' alt-on' if on and alt else '') + (' jour' if jour else '')
    p = '<i class="t12-dot" style="background:%s"></i>' % point if point else ''
    return '<span class="%s"%s>%s%s</span>' % (cls, ' id="%s"' % ident if ident else '', p, e(libelle))


def date_(ident, valeur):
    """Un champ <input type="date"> (dashboard_shell.xml:133-138) ; ``ident-val`` reçoit la saisie."""
    return ('<span class="t12-date" id="%s"><span class="ph" id="%s-ph"></span><span id="%s-val">%s</span>'
            '<span class="t12-cal">%s</span></span>' % (ident, ident, ident, e(valeur), CAL))


FILTRES = '<div class="t12-fbar" id="t12-fbar">%s</div>' % ''.join([
    '<div class="t12-frow"><span class="t12-flab">Période</span>%s<span class="t12-esp"></span>'
    '<span class="t12-du">Du</span>%s<span class="t12-du">au</span>%s<span class="t12-ok" id="t12-ok-p">Analyser</span></div>'
    % (''.join([fb('Toute la période', 't12-pe-all', True), fb("Aujourd'hui"), fb('Cette semaine'),
                fb('Ce mois'), fb('Ce trimestre'), fb('Cette année')]),
       date_('t12-du', '04/05/2026'), date_('t12-au', '13/10/2026')),
    # couleurs dans l'ordre des pos.config (pos_dashboard.py:651-654, 905-912 ; PALETTE de t10_ardoises.py)
    '<div class="t12-frow"><span class="t12-flab">Caisse</span>%s</div>'
    % ''.join([fb('Toutes les caisses', on=True), fb(BAR, point=PRIMARY), fb(RESTO, point=INFO),
               fb(BOUT, point=SUCCESS)]),
    '<div class="t12-frow"><span class="t12-flab">Heure</span>%s<span class="t12-esp"></span>'
    '<span class="t12-heure">18</span><span class="t12-du">h →</span><span class="t12-heure">23</span>'
    '<span class="t12-du">h</span><span class="t12-ok">OK</span></div>'
    % ''.join([fb('Toute la journée', on=True, alt=True), fb('Matin 6–12h'), fb('Après-midi 12–18h'),
               fb('Soir 18–23h', 't12-h-soir'), fb('Nuit 23–6h')]),
    # « Tous » est actif mais blanc sur blanc (écart 2) : sa place reste vide
    '<div class="t12-frow"><span class="t12-flab">Jour</span><span class="t12-tous"></span>%s'
    '<span class="t12-esp"></span>%s%s</div>'
    % (''.join(fb(j, jour=True) for j in JOURS_SEMAINE), fb('Semaine (lun–ven)', jour=True), fb('Week-ends', jour=True)),
])


# -- composants du tableau de bord --
def kpi(ident, libelle, valeur, sous, couleur=None, haut=True, petite=False):
    """KpiCard (dashboard_shell.xml:222-231) ou carte secondaire (views.xml:62-102)."""
    style = ' style="border-top-color:%s"' % couleur if haut and couleur else ''
    vstyle = ' style="color:%s"' % couleur if couleur else ''
    return ('<div class="t12-kpi%s%s" id="%s"%s><div class="l">%s</div><div class="v" id="%s-v"%s>%s</div>'
            '<div class="s" id="%s-s">%s</div></div>'
            % (' t12-haut' if haut else '', ' t12-petite' if petite else '', ident, style, e(libelle), ident, vstyle,
               valeur, ident, e(sous)))


def module(ident, titre, sous, couleur, svg, corps, droite='', classe_=''):
    """o_aite_mod_card (views.xml) : pastille d'icône, titre coloré, sous-titre."""
    return ('<div class="t12-mod %s"%s><div class="t12-mh"><div class="t12-mhl"%s><span class="t12-mi" style="background:%s">'
            '%s</span><div><div class="t12-mt" style="color:%s">%s</div><div class="t12-ms">%s</div></div></div>%s</div>'
            '<div class="t12-mb">%s</div></div>'
            % (classe_, ' id="%s"' % ident if ident else '', ' id="%s-t"' % ident if ident else '', couleur, svg or '',
               couleur, e(titre), e(sous), droite, corps))


def graduations(vmax):
    """Les graduations « k » de Chart.js (pas de 1, 2 ou 5 × 10^n)."""
    brut = vmax / 6.0
    puissance = 10 ** int(math.floor(math.log10(brut)))
    pas = next(m * puissance for m in (1, 2, 2.5, 5, 10) if m * puissance >= brut)
    haut = pas * math.ceil(vmax / pas)
    return haut, [int(v) for v in frange(0, haut, pas)]


def frange(a, b, pas):
    v = a
    while v <= b + 1e-6:
        yield v
        v += pas


def k(v):
    return '%dk' % round(v / 1000.0) if v >= 1000 else '%d' % v


def barres_top(ident, top):
    """Top 8 articles — CA (violet) vs Marge (vert), étiquettes tronquées à 9 caractères + « … »."""
    w, h, g, b = 720, 236, 52, 24
    haut, ticks = graduations(max(x[1] for x in top))
    zone = w - g - 6
    pas = zone / float(len(top))
    svg = []
    for t in ticks:
        y = 10 + (h - 40) * (1 - t / float(haut))
        svg.append('<line x1="%d" x2="%d" y1="%.1f" y2="%.1f" stroke="#ECEBE7"/><text x="%d" y="%.1f" '
                   'class="t12-ax" text-anchor="end">%s</text>' % (g, w, y, y, g - 8, y + 5, k(t)))
    for i, (nom, ca, marge) in enumerate(top):
        x = g + i * pas + pas / 2.0
        for j, (v, c) in enumerate(((ca, PRIMARY), (marge, SUCCESS))):
            hb = (h - 40) * v / float(haut)
            svg.append('<rect x="%.1f" y="%.1f" width="%d" height="%.1f" rx="3" fill="%s"/>'
                       % (x - b - 1 + j * (b + 2), 10 + (h - 40) - hb, b, hb, c))
        lib = nom if len(nom) <= 10 else nom[:9] + '…'
        svg.append('<text x="%.1f" y="%d" class="t12-ax" text-anchor="middle">%s</text>' % (x, h - 8, e(lib)))
    return '<svg class="t12-svg" id="%s" viewBox="0 0 %d %d">%s</svg>' % (ident, w, h, ''.join(svg))


def courbes(ident, evo):
    """Évolution mensuelle : CA (plein, aire), CMV et marge (pointillés)."""
    w, h, g = 720, 214, 64
    haut, ticks = graduations(max(x[1] for x in evo))
    svg = []
    for t in ticks:
        y = 10 + (h - 40) * (1 - t / float(haut))
        svg.append('<line x1="%d" x2="%d" y1="%.1f" y2="%.1f" stroke="#ECEBE7"/><text x="%d" y="%.1f" '
                   'class="t12-ax" text-anchor="end">%s</text>' % (g, w, y, y, g - 8, y + 5, k(t)))
    n = len(evo)
    xs = [g + 20 + i * (w - g - 40) / float(max(1, n - 1)) for i in range(n)]

    def y_(v):
        return 10 + (h - 40) * (1 - v / float(haut))
    series = [([x[1] for x in evo], PRIMARY, ''), ([x[2] for x in evo], DANGER, ' stroke-dasharray="7 6"'),
              ([x[1] - x[2] for x in evo], SUCCESS, ' stroke-dasharray="7 6"')]
    pts = ' '.join('%.1f,%.1f' % (x, y_(v)) for x, v in zip(xs, series[0][0]))
    svg.append('<path d="M%.1f,%.1f L%s L%.1f,%.1f Z" fill="%s" fill-opacity=".13"/>'
               % (xs[0], y_(0), pts.replace(' ', ' L'), xs[-1], y_(0), PRIMARY))
    for vals, c, tirets in series:
        svg.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"%s/>'
                   % (' '.join('%.1f,%.1f' % (x, y_(v)) for x, v in zip(xs, vals)), c, tirets))
        svg.extend('<circle cx="%.1f" cy="%.1f" r="4" fill="#fff" stroke="%s" stroke-width="2"/>' % (x, y_(v), c)
                   for x, v in zip(xs, vals))
    svg.extend('<text x="%.1f" y="%d" class="t12-ax" text-anchor="%s">%s</text>'
               % (x, h - 6, 'middle' if 0 < i < n - 1 else ('start' if i == 0 else 'end'), e(lab))
               for i, (x, (lab, _, _)) in enumerate(zip(xs, evo)))
    return '<svg class="t12-svg t12-courbe" id="%s" viewBox="0 0 %d %d">%s</svg>' % (ident, w, h, ''.join(svg))


LEGENDE_EVO = ('<div class="t12-leg"><span><i style="border-top:3px solid %s"></i>CA</span>'
               '<span><i style="border-top:3px dashed %s"></i>CMV</span>'
               '<span><i style="border-top:3px dashed %s"></i>Marge</span></div>' % (PRIMARY, DANGER, SUCCESS))


def module_ventes(ident, top, evo):
    corps = ('<div class="t12-g2"><div><div class="t12-st">Top 8 articles — CA vs Marge</div>%s</div>'
             '<div><div class="t12-st">Évolution mensuelle (CA · CMV · Marge)</div>%s%s</div></div>'
             % (barres_top(ident + '-top', top), LEGENDE_EVO, courbes(ident + '-evo', evo)))
    return module(ident, 'Ventes & évolution', 'CA · Marge · CMV', PRIMARY, ICONES['graphe'], corps, classe_='t12-m1')


def module_categories():
    lignes = ''.join(
        '<div class="t12-cr"><div class="t12-crh"><span class="t12-crn"><i class="t12-cd" style="background:%s"></i>'
        '<b>%s</b><small>tx %s</small></span><span><b style="color:%s">%s</b><small> · CMV %s</small></span></div>'
        '<div class="t12-pb"><i style="width:%.1f%%;background:%s"></i></div></div>'
        % (couleurs_cat(c['nom'], i)[0], e(c['nom']), fmt_pct(c['taux']), SUCCESS, fmt_money(c['marge']),
           fmt_money(c['cmv']), min(c['taux'], 100), couleurs_cat(c['nom'], i)[0])
        for i, c in enumerate(CATEGORIES))
    # « CMV vs Marge » : barres groupées par catégorie, légende en bas
    w, h, g = 720, 270, 64
    haut, ticks = graduations(max(max(c['cmv'], c['marge']) for c in CATEGORIES))
    svg = []
    for t in ticks:
        y = 10 + (h - 66) * (1 - t / float(haut))
        svg.append('<line x1="%d" x2="%d" y1="%.1f" y2="%.1f" stroke="#ECEBE7"/><text x="%d" y="%.1f" '
                   'class="t12-ax" text-anchor="end">%s</text>' % (g, w, y, y, g - 8, y + 5, k(t)))
    pas = (w - g) / float(len(CATEGORIES))
    for i, c in enumerate(CATEGORIES):
        x = g + i * pas + pas / 2.0
        for j, (v, coul) in enumerate(((c['cmv'], '#C77272'), (c['marge'], '#7C9C5E'))):
            hb = (h - 66) * v / float(haut)
            svg.append('<rect x="%.1f" y="%.1f" width="26" height="%.1f" fill="%s"/>'
                       % (x - 27 + j * 28, 10 + (h - 66) - hb, hb, coul))
        svg.append('<text x="%.1f" y="%d" class="t12-ax" text-anchor="middle">%s</text>' % (x, h - 34, e(c['nom'])))
    svg.append('<rect x="%d" y="%d" width="30" height="12" fill="#C77272"/><text x="%d" y="%d" class="t12-ax">CMV</text>'
               '<rect x="%d" y="%d" width="30" height="12" fill="#7C9C5E"/><text x="%d" y="%d" class="t12-ax">Marge</text>'
               % (w / 2 - 110, h - 18, w / 2 - 74, h - 7, w / 2 + 6, h - 18, w / 2 + 42, h - 7))
    corps = ('<div class="t12-g2"><div><div class="t12-st">Catégories — marge &amp; CMV</div>%s</div>'
             '<div><div class="t12-st">CMV vs Marge</div><svg class="t12-svg" viewBox="0 0 %d %d">%s</svg></div></div>'
             % (lignes, w, h, ''.join(svg)))
    return module(None, 'Marge & CMV par catégorie', 'répartition de la rentabilité', SUCCESS, CAMEMBERT, corps,
                  classe_='t12-m2')


def anneau_caisses(plein=False):
    """« Contribution au CA » (doughnut, dashboard_view.js:212-236) ou « Part du CA par caisse » (pie,
    caisse_view.js:94-112)."""
    r, ep = (48, 96) if plein else (74, 52)
    c = 2 * math.pi * r
    debut, arcs = 0.0, []
    for x in CAISSES:
        lg = c * x['part'] / 100.0
        arcs.append('<circle r="%d" cx="100" cy="100" fill="none" stroke="%s" stroke-width="%d" '
                    'stroke-dasharray="%.1f %.1f" stroke-dashoffset="%.1f"/>'
                    % (r, x['couleur'], ep, lg - 1, c - lg + 1, -debut))
        debut += lg
    leg = ''.join('<div><i style="background:%s"></i>%s</div>' % (x['couleur'], e(x['nom'])) for x in CAISSES)
    return ('<div class="t12-ann"><svg viewBox="0 0 200 200"><g transform="rotate(-90 100 100)">%s</g></svg>'
            '<div class="t12-annleg">%s</div></div>' % (''.join(arcs), leg))


def badge(taux, seuil_ambre=40):
    return 'b-teal' if taux >= 50 else ('b-amb' if taux >= seuil_ambre else 'b-red')


def module_caisses():
    lignes = ''.join('<div class="t12-cl"><i class="t12-cd" style="background:%s"></i><b class="t12-cln">%s</b>'
                     '<span class="t12-clca">%s</span><span class="t12-b %s">%s</span><span class="t12-clp">%s du CA</span>'
                     '</div>' % (x['couleur'], e(x['nom']), fmt_money(x['ca']), badge(x['taux']), fmt_pct(x['taux']),
                                 fmt_pct(x['part'])) for x in CAISSES)
    lignes += ('<div class="t12-cl t12-cltot"><i class="t12-cd" style="background:#888780"></i><b class="t12-cln">TOTAL</b>'
               '<b class="t12-clca">%s</b><span class="t12-b b-amb">%s</span><span class="t12-clp">marge %s</span></div>'
               % (fmt_money(CA), fmt_pct(pct(MARGE, CA)), fmt_money(MARGE)))
    corps = ('<div class="t12-g2"><div><div class="t12-st">Contribution au CA</div>%s</div>'
             '<div><div class="t12-st">Synthèse par caisse</div>%s</div></div>' % (anneau_caisses(), lignes))
    # fa-cash-register n'existe pas en Font Awesome 4.7 : la pastille reste vide (écart 6)
    return module(None, 'Performance par caisse', 'CA · marge totale & par point de vente', INFO, '', corps,
                  classe_='t12-m3')


def chaleur():
    tete = '<tr><th class="t12-hc">Jour \\ h</th>%s</tr>' % ''.join('<th>%d</th>' % h for h in range(24))
    corps = []
    for d, jour in enumerate(JOURS_SEMAINE):
        cases = []
        for h in range(24):
            v = CHALEUR[d][h]
            a = v / float(CHALEUR_MAX)
            fond = 'rgba(113, 75, 103, %.3f)' % (0.06 + a * 0.85)
            coul = '#ffffff' if a > 0.55 else '#3d3c39'
            cases.append('<td style="background:%s;color:%s">%s</td>' % (fond, coul, k(v) if v else ''))
        corps.append('<tr id="t12-hm-d%d"><td class="t12-hd">%s</td>%s</tr>' % (d, jour, ''.join(cases)))
    droite = ('<div class="t12-ins" id="t12-ins"><span class="t12-chip">%s</span><span class="t12-chip">%s</span></div>'
              % (e(PIC), e(JOUR_FORT)))
    # le créneau du pic (deux colonnes, heures UTC : écart 11), cible de l'anneau et de la bulle ;
    # rentré de 7 px de chaque côté, pour que l'anneau (10 px de marge) tombe sur les bords des deux colonnes
    soir = ('<div class="t12-soir" id="t12-hm-soir" style="left:calc(86px + %d * (100%% - 83px) / 24 + 7px);'
            'width:calc(2 * (100%% - 83px) / 24 - 17px)"></div>' % H_PIC)
    corps_html = ('<div class="t12-hmw" id="t12-hm-tab"><table class="t12-hm">%s%s</table>%s</div>'
                  % (tete, ''.join(corps), soir))
    return module('t12-hm', 'Répartition des ventes — heure × jour',
                  "intensité = chiffre d'affaires · pour caler plannings & happy hours", PRIMARY, ICONES['grille'],
                  corps_html, droite=droite, classe_='t12-m4')


def module_classements():
    def rang(i, nom, pctg, val, coul):
        return ('<div class="t12-rk"><span class="n">%d</span><span class="nm">%s</span><span class="bg"><i style="width:%.1f%%;'
                'background:%s"></i></span><span class="vl">%s</span></div>' % (i, e(nom), min(pctg, 100), coul, e(val)))
    bieres = sorted([p for p in PRODUITS if p['cat'] == 'Bières'], key=lambda p: -p['qty'])
    # « Meilleures marges » et « Moins vendus » ne lisent que les lignes positives
    # (pos_dashboard.py:450-485) : un article vendu puis remboursé y compte sa vente.
    positifs = [dict(p, qty=1, taux=pct(p['prix'] - p['cout'], p['prix'])) if p['rembourse'] else p for p in PRODUITS]
    marges = sorted(positifs, key=lambda p: -p['taux'])[:8]
    moins = sorted(positifs, key=lambda p: p['qty'])[:8]
    qmax_b, qmax_m = max(p['qty'] for p in bieres), max(p['qty'] for p in moins)
    corps = ('<div class="t12-g3"><div><div class="t12-st">🍺 Top bières (qté)</div>%s</div>'
             '<div><div class="t12-st">⭐ Meilleures marges</div>%s</div><div><div class="t12-st">📉 Moins vendus</div>'
             '%s</div></div>'
             % (''.join(rang(i + 1, p['nom'], p['qty'] * 100.0 / qmax_b, '%s u' % fmt(p['qty']), PRIMARY)
                        for i, p in enumerate(bieres)),
                ''.join(rang(i + 1, p['nom'], p['taux'], fmt_pct(p['taux']), SUCCESS) for i, p in enumerate(marges)),
                ''.join(rang(i + 1, p['nom'], p['qty'] * 100.0 / qmax_m, '%s u' % fmt(p['qty']), DANGER)
                        for i, p in enumerate(moins))))
    return module(None, 'Classements produits', 'Bières · Marges · Moins vendus', WARNING, TROPHEE, corps,
                  classe_='t12-m5')


def contenu_tableau(cle, d, top, evo, articles, meilleur, delta=False):
    """Le tableau de bord d'une période : ``d`` = ca, cmv, marge, cmdes, qty, jours."""
    i = 't12-%s' % cle
    rangee1 = '<div class="t12-g4" id="%s-r1">%s</div>' % (i, ''.join([
        kpi(i + '-ca', "Chiffre d'affaires", fmt_money(d['ca']),
            '%s / jour · %dj' % (fmt_money(d['ca'] / float(d['jours'])), d['jours']), INFO),
        kpi(i + '-marge', 'Marge brute', fmt_money(d['marge']),
            'Taux: %s · %s/tx' % (fmt_pct(pct(d['marge'], d['ca'])), fmt_money(d['marge'] / float(d['cmdes']))), SUCCESS),
        kpi(i + '-cmv', 'CMV (coût marchandises)', fmt_money(d['cmv']),
            '%s du CA · %s/u' % (fmt_pct(pct(d['cmv'], d['ca'])), fmt_money(d['cmv'] / float(d['qty']))), DANGER),
        kpi(i + '-tx', 'Transactions', fmt(d['cmdes']),
            'Panier moy. %s · %s u' % (fmt_money(d['ca'] / float(d['cmdes'])), fmt(d['qty'])), PRIMARY)]))
    bande = ''
    if delta:
        bande = '<div class="t12-strip" id="t12-strip">%s</div>' % ''.join(
            '<div class="t12-dc" id="t12-strip-%d"><span class="t12-dl">%s</span><span class="t12-dv %s">%s</span></div>'
            % (n, e(lib), 'up' if v > 0 else 'down', fmt_delta(v)) for n, (lib, v) in enumerate(DELTAS))
    ratio, taux = pct(d['cmv'], d['ca']), pct(d['marge'], d['ca'])
    rangee2 = '<div class="t12-g4" id="%s-r2">%s</div>' % (i, ''.join([
        kpi(i + '-ratio', 'Ratio CMV/CA', fmt_pct(ratio), 'Bonne maîtrise ✓' if ratio < 65 else 'À optimiser ⚠',
            SUCCESS if ratio < 65 else DANGER, haut=False, petite=True),
        kpi(i + '-taux', 'Taux de marge', fmt_pct(taux), 'Objectif atteint ✓' if taux >= 35 else 'Sous objectif',
            SUCCESS if taux >= 35 else WARNING, haut=False, petite=True),
        kpi(i + '-art', 'Articles actifs', '%d <span class="t12-sur">/ %d</span>' % articles,
            'références vendues', haut=False, petite=True),
        kpi(i + '-best', 'Meilleur article', e(meilleur[0][:18]), '%s CA' % fmt_money(meilleur[1]), PRIMARY, haut=False,
            petite=True)]))
    suite = module_ventes(i + '-ventes', top, evo)
    if delta:
        suite += module_categories() + module_caisses() + chaleur() + module_classements()
    return '<div class="t12-c%s" id="%s">%s%s%s%s</div>' % ('' if cle == 'all' else ' masque', i, rangee1, bande, rangee2,
                                                          suite)


MOIS = {'ca': CA, 'cmv': CMV, 'marge': MARGE, 'cmdes': CMDES, 'qty': QTE, 'jours': JOURS_PERIODE}
C_ALL = contenu_tableau('all', TOUT, TOP8_TOUT, EVO_TOUT, (TOUT['actifs'], TOUT['articles']), TOUT['meilleur'])
C_MOIS = contenu_tableau('m', MOIS, TOP8_MOIS, EVO_MOIS, (ACTIFS, len(PRODUITS)), (PRODUITS[0]['nom'], PRODUITS[0]['ca']),
                         delta=True)


# -- onglet Par caisse --
def kpi_caisse(ident, libelle, nom, sous, couleur):
    return ('<div class="t12-kpi t12-haut t12-kc" id="%s" style="border-top-color:%s"><div class="l">%s</div>'
            '<div class="v" style="color:%s">%s</div><div class="s">%s</div></div>'
            % (ident, couleur, e(libelle), couleur, e(nom), e(sous)))


TOP_CA = max(CAISSES, key=lambda x: x['ca'])
TOP_TAUX = max(CAISSES, key=lambda x: x['taux'])
TOP_PANIER = max(CAISSES, key=lambda x: x['panier'])
COLS_CAISSE = ['Caisse', 'CA HT', '% CA', 'Marge', 'Taux', 'CMV', 'Cmdes', 'Panier moy.', 'Qté', 'Écart caisse']


def ligne_caisse(x):
    ecart = ('<span style="color:%s;font-weight:600">%s</span>' % (DANGER if x['ecart'] < 0 else SUCCESS,
                                                                 fmt_signed(x['ecart'])) if x['ecart'] else
             '<span class="t12-muet">0</span>')
    return ('<tr><td class="t12-b6"><i class="t12-cd" style="background:%s"></i>%s</td><td class="r t12-b6">%s</td>'
            '<td class="r t12-muet">%s</td><td class="r" style="color:%s">%s</td><td class="r"><span class="t12-b %s">%s</span>'
            '</td><td class="r" style="color:%s">%s</td><td class="r t12-muet">%s</td><td class="r">%s</td>'
            '<td class="r t12-muet">%s</td><td class="r">%s</td></tr>'
            % (x['couleur'], e(x['nom']), fmt_money(x['ca']), fmt_pct(x['part']), SUCCESS, fmt_money(x['marge']),
               badge(x['taux']), fmt_pct(x['taux']), DANGER, fmt_money(x['cmv']), fmt(x['cmdes']), fmt_money(x['panier']),
               fmt(x['qty']), ecart))


TABLE_CAISSES = ('<table class="t12-t" id="t12-ctab"><thead><tr>%s</tr></thead><tbody>%s</tbody><tfoot><tr id="t12-ctot">'
                 '<td class="t12-b6">TOTAL</td><td class="r t12-b6">%s</td><td class="r">100%%</td>'
                 '<td class="r t12-b6" style="color:%s">%s</td><td class="r"><span class="t12-b b-amb">%s</span></td>'
                 '<td class="r t12-b6" style="color:%s">%s</td><td class="r">%s</td><td class="r">%s</td><td class="r">%s</td>'
                 '<td class="r"><span style="color:%s;font-weight:600">%s</span></td></tr></tfoot></table>'
                 % (''.join('<th%s>%s</th>' % ('' if i == 0 else ' class="r"', e(c)) for i, c in enumerate(COLS_CAISSE)),
                    ''.join(ligne_caisse(x) for x in CAISSES), fmt_money(CA), SUCCESS, fmt_money(MARGE),
                    fmt_pct(pct(MARGE, CA)), DANGER, fmt_money(CMV), fmt(CMDES), fmt_money(CA / float(CMDES)), fmt(QTE),
                    DANGER if ECART_TOTAL < 0 else SUCCESS, fmt_signed(ECART_TOTAL)))


def barres_taux():
    w, h = 720, 230
    svg = []
    for t in range(0, 101, 20):
        y = 10 + (h - 40) * (1 - t / 100.0)
        svg.append('<line x1="56" x2="%d" y1="%.1f" y2="%.1f" stroke="#ECEBE7"/><text x="48" y="%.1f" class="t12-ax" '
                   'text-anchor="end">%d%%</text>' % (w, y, y, y + 5, t))
    pas = (w - 56) / float(len(CAISSES))
    for i, x in enumerate(CAISSES):
        cx = 56 + i * pas + pas / 2.0
        hb = (h - 40) * x['taux'] / 100.0
        svg.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="3" fill="%s"/><text x="%.1f" y="%d" '
                   'class="t12-ax" text-anchor="middle">%s</text>'
                   % (cx - pas * 0.36, 10 + h - 40 - hb, pas * 0.72, hb, x['couleur'], cx, h - 8, e(x['nom'])))
    return '<svg class="t12-svg" viewBox="0 0 %d %d">%s</svg>' % (w, h, ''.join(svg))


C_CAISSE = ('<div class="t12-c masque" id="t12-c-caisse"><div class="t12-g4" id="t12-ck">%s</div>%s'
            '<div class="t12-g2 t12-mt14"><div class="t12-mod t12-nomt"><div class="t12-mb"><div class="t12-st">Part du CA '
            'par caisse</div>%s</div></div><div class="t12-mod t12-nomt"><div class="t12-mb"><div class="t12-st">Taux de '
            'marge par caisse</div>%s</div></div></div></div>'
            % (''.join([kpi_caisse('t12-ck-1', 'Caisse n°1 (CA)', TOP_CA['nom'],
                                   '%s · %s' % (fmt_money(TOP_CA['ca']), fmt_pct(TOP_CA['part'])), INFO),
                        kpi_caisse('t12-ck-2', 'Caisse la + rentable', TOP_TAUX['nom'], 'taux %s' % fmt_pct(TOP_TAUX['taux']),
                                   SUCCESS),
                        kpi_caisse('t12-ck-3', 'Meilleur panier moyen', TOP_PANIER['nom'], fmt_money(TOP_PANIER['panier']),
                                   WARNING),
                        '<div class="t12-kpi t12-haut t12-kc" id="t12-ck-4" style="border-top-color:%s"><div class="l">'
                        'Écart de caisse total</div><div class="v" style="color:%s">%s</div><div class="s">sur la période'
                        '</div></div>' % (DANGER, DANGER if ECART_TOTAL < 0 else SUCCESS, fmt_signed(ECART_TOTAL))]),
               module('t12-cmod', 'Comparatif des caisses', 'marge totale & par caisse sur la période', PRIMARY, TABLE,
                      TABLE_CAISSES, classe_='t12-mtable'),
               anneau_caisses(plein=True), barres_taux()))


# -- onglet Articles --
CATS_TRIEES = sorted({p['cat'] for p in PRODUITS})
COLS_ART = [('Article', ''), ('Qté', 'r'), ('CA ▼', 'r'), ('CMV', 'r'), ('Marge', 'r'), ('Taux', 'r'), ('Catégorie', ''),
            ('Performance', '')]
GRILLE_ART = 'grid-template-columns:minmax(0,1fr) 80px 120px 120px 120px 100px 150px 190px'
CA_MAX = max(p['ca'] for p in PRODUITS)


def carte_articles(ident, produits, prefixe, masque=False):
    """Le tableau des articles (views.xml:659-715), trié par CA décroissant."""
    tete = '<div class="t12-ah" style="%s">%s</div>' % (GRILLE_ART, ''.join(
        '<span%s>%s</span>' % (' class="r"' if a else '', e(c)) for c, a in COLS_ART))
    corps = []
    for i, p in enumerate(produits):
        _, bg, txt = couleurs_cat(p['cat'], i)
        corps.append('<div class="t12-arow" id="%s-%d" style="%s"><span class="t12-b6 ell">%s</span><span class="r t12-muet">%s'
                     '</span><span class="r t12-b6">%s</span><span class="r" style="color:%s">%s</span><span class="r" '
                     'style="color:%s">%s</span><span class="r"><span class="t12-b %s">%s</span></span><span><span '
                     'class="t12-b" style="background:%s;color:%s">%s</span></span><span><div class="t12-pb"><i style="'
                     'width:%.1f%%;background:%s"></i></div></span></div>'
                     % (prefixe, i, GRILLE_ART, e(p['nom']), fmt(p['qty']), fmt(p['ca']), DANGER, fmt(p['cmv']), SUCCESS,
                        fmt(p['marge']), badge(p['taux'], 30), fmt_pct(p['taux']), bg, txt, e(p['cat']),
                        p['ca'] * 100.0 / CA_MAX, PRIMARY))
    return '<div class="t12-mod t12-artmod%s" id="%s">%s%s</div>' % (' masque' if masque else '', ident, tete, ''.join(corps))


BIERES = [p for p in PRODUITS if 'bière' in p['nom'].lower() or 'bière' in p['cat'].lower()]
C_ART = ('<div class="t12-c masque" id="t12-c-art"><div class="t12-cats">%s%s</div>'
         '<div class="t12-sb">%s<span class="t12-sbn" id="t12-art-n">%d / %d articles</span></div>'
         '<div class="t12-artpile">%s%s</div></div>'
         % (fb('Toutes catégories', on=True),
            ''.join(fb(c, point=couleurs_cat(c, i)[0]) for i, c in enumerate(CATS_TRIEES)),
            entree('t12-q', 'Rechercher un article ou une catégorie…', classe='entree t12-q'), len(PRODUITS),
            len(PRODUITS), carte_articles('t12-art-tous', PRODUITS, 't12-ar'),
            carte_articles('t12-art-bieres', BIERES, 't12-ab', masque=True)))
B65 = BIERES[0]
assert B65['nom'] == 'Bière blonde 65 cl'

# -- le panneau d'un article (slide-over, position fixed) --
VOILE = '<div class="t12-voile masque" id="t12-voile" data-layout-allow-overlap data-layout-allow-occlusion></div>'
_c, _bg, _tx = couleurs_cat(B65['cat'], 0)
PANNEAU = ('<div class="t12-panel masque" id="t12-panel" data-layout-allow-overlap data-layout-allow-occlusion>'
           '<div class="t12-ph"><span>%s</span><span class="t12-px" id="t12-pn-x">×</span></div><div class="t12-pbody">'
           '<span class="t12-b t12-pcat" style="background:%s;color:%s">%s</span>'
           '<div class="t12-mini">%s</div>'
           '<div class="t12-f"><div class="t12-fl">Quantité vendue</div><div class="t12-fv t12-big">%s unités</div></div>'
           '<div class="t12-f" id="t12-pn-taux"><div class="t12-fl">Taux de marge</div><div class="t12-ft"><b style="color:%s">'
           '%s</b><div class="t12-pb t12-pbl"><i style="width:%.1f%%;background:%s"></i></div></div></div>'
           '<div class="t12-sep"></div><div id="t12-pn-unit">'
           '<div class="t12-f"><div class="t12-fl">Prix de vente moyen</div><div class="t12-fv">%s / unité</div></div>'
           '<div class="t12-f"><div class="t12-fl">Coût moyen unitaire (CMV)</div><div class="t12-fv" style="color:%s">'
           '%s / unité</div></div>'
           '<div class="t12-f"><div class="t12-fl">Marge unitaire</div><div class="t12-fv" style="color:%s">%s / unité</div>'
           '</div></div><div class="t12-sep"></div><div class="t12-fl">Période analysée</div>'
           '<div class="t12-fv">01/10/2026 → 13/10/2026</div></div></div>'
           % (e(B65['nom']), _bg, _tx, e(B65['cat']),
              ''.join('<div class="t12-kpi"><div class="l">%s</div><div class="v" style="color:%s">%s</div></div>'
                      % (lib, coul, fmt_money(v)) for lib, coul, v in (('CA', INFO, B65['ca']),
                                                                       ('Marge', SUCCESS, B65['marge']),
                                                                       ('CMV', DANGER, B65['cmv']))),
              fmt(B65['qty']), SUCCESS if B65['taux'] >= 50 else WARNING, fmt_pct(B65['taux']), min(B65['taux'], 100),
              SUCCESS if B65['taux'] >= 50 else WARNING, fmt_money(B65['ca'] / float(B65['qty'])), DANGER,
              fmt_money(B65['cmv'] / float(B65['qty'])), SUCCESS, fmt_money(B65['marge'] / float(B65['qty']))))

# -- onglet Écarts de caisse --
NEG = [s for s in SESSIONS if s[5] < 0]
POSI = [s for s in SESSIONS if s[5] > 0]
ECARTS_KPI = ''.join([
    kpi('t12-ek-1', 'Écart négatif total', fmt_money(abs(sum(s[5] for s in NEG))), 'sessions clôturées', DANGER),
    kpi('t12-ek-2', 'Sessions avec écart', fmt(len(SESSIONS)), '%d nég. · %d pos.' % (len(NEG), len(POSI)), WARNING),
    kpi('t12-ek-3', 'Écart moyen', fmt_money(abs(sum(s[5] for s in NEG)) / float(len(NEG))), 'par session négative',
        PRIMARY),
    kpi('t12-ek-4', 'Plus grand écart', fmt_money(abs(min(s[5] for s in NEG))), 'à investiguer en priorité', DANGER)])
assert len(NEG) <= 5            # pas de bandeau « Plusieurs sessions… » (views.xml:900)
LIGNES_ECARTS = ''.join(
    '<tr id="t12-e-r%d"><td class="t12-b6" style="color:%s">%s</td><td>%s</td><td id="t12-e-r%d-qui">%s</td><td class="r">%s</td>'
    '<td class="r t12-b6" style="color:%s">%s</td><td><span class="t12-b %s" id="t12-e-r%d-sev">%s</span></td></tr>'
    % (i, INFO, e(nom), date, i, e(qui), fmt(ca_ttc), DANGER if ec < 0 else INFO, fmt(ec), SEV_BADGE[severite(ec)], i,
       SEV_LIB[severite(ec)])
    for i, (nom, date, qui, _, ca_ttc, ec) in enumerate(SESSIONS))
C_ECARTS = ('<div class="t12-c masque" id="t12-c-ecarts"><div class="t12-g4">%s</div><div class="t12-mod t12-nomt">'
            '<table class="t12-t" id="t12-etab"><thead><tr><th>Session</th><th>Date</th><th>Caissier</th><th class="r">CA</th>'
            '<th class="r">Écart (F)</th><th>Sévérité</th></tr></thead><tbody>%s</tbody></table></div></div>'
            % (ECARTS_KPI, LIGNES_ECARTS))

ANALYSE = vue_libre('t12-ana', TABS + '<div class="t12-corps"><div class="t12-defil" id="t12-defil" '
                    'data-layout-allow-overflow data-layout-allow-occlusion>%s<div class="t12-contenu">%s%s%s%s%s</div>'
                    '</div></div>' % (FILTRES, C_ALL, C_MOIS, C_CAISSE, C_ART, C_ECARTS), fond='tdb')

ECRAN = navigateur(fenetre_muk('t12-app', 'Point de Vente', MENUS, [POS, ANALYSE], societe=SOCIETE, initiale=NOM[0],
                               avatar='#854F0B', apps=APPS_PROFIL['direction'], app_active='Point de Vente',
                               calques=MENU + VOILE + PANNEAU))

# Le défilement jusqu'à la carte de chaleur (mesuré sur la composition).
DEFIL_CHALEUR = -1610
# Le zoom sur la carte de chaleur : cadré sur la gauche du tableau, pour garder
# les jours (Lun … Dim) et les colonnes du pic dans l'image.
ZOOM_HM_FX = 0.45

# Ce que dit l'onglet Par caisse, vérifié sur les chiffres.
assert TOP_CA['nom'] == BAR and CAISSES[0]['part'] > 80
assert TOP_TAUX['nom'] == RESTO and TOP_PANIER['nom'] == RESTO
VOIX_CAISSES = ("L'onglet Par caisse compare le bar de la terrasse et le restaurant. Le bar fait plus de quatre-vingts "
                "pour cent du chiffre, le restaurant a le meilleur taux de marge et le meilleur panier. Dans le "
                "tableau : chiffre d'affaires, marge, taux, panier moyen et écart de caisse ; la ligne total donne la "
                "marge de toute la période choisie.")


def onglet(depuis, vers, contenu_depuis, contenu_vers):
    """Un clic sur un onglet : l'onglet s'allume, le contenu change sous la barre de filtres."""
    return [clic('#t12-tab-%s' % vers, d=0.6), classe('#t12-tab-%s' % depuis, retirer=['on']),
            classe('#t12-tab-%s' % vers, ajouter=['on'], avec=True), cacher('#%s' % contenu_depuis, d=0.2),
            montrer('#%s' % contenu_vers, d=0.35, y=0, avec=True)]


CSS = """
#t12-app { --t12-muet: #6B6A65; }
#t12-app .o-haut .nom-app { font-size: 23px; }
#t12-app .cp .titre { font-size: 24px; }
/* accueil du Point de Vente (kanban des caisses, thème MuK) */
.t12-vues { margin-left: 18px; display: flex; }
.t12-vues i { width: 48px; height: 42px; display: flex; align-items: center; justify-content: center; background: #E9ECEF; color: #343A40; }
.t12-vues i + i { border-left: 1px solid #fff; }
.t12-vues i.on { background: #DCE6EC; box-shadow: inset 0 0 0 1px var(--muk-prim); }
.t12-vues svg { width: 20px; height: 20px; }
.t12-pk { position: absolute; left: 0; right: 0; top: 80px; padding: 16px 20px; display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.t12-pc { position: relative; height: 196px; background: #fff; border: 1px solid var(--o-filet); padding: 20px 24px; }
.t12-pc-n { font-size: 24px; font-weight: 500; color: var(--o-texte); }
.t12-pc-bt { position: absolute; left: 24px; top: 84px; height: 46px; padding: 0 16px; display: inline-flex; align-items: center;
  background: var(--muk-prim); color: #fff; font-size: 19px; font-weight: 500; border-radius: 4px; }
.t12-pc-i { position: absolute; left: 380px; top: 80px; display: grid; grid-template-columns: 220px auto; row-gap: 6px; font-size: 19px; color: var(--o-texte); }
/* menu déroulant « Analyse AITE » */
.t12-menu { position: absolute; left: 676px; top: 54px; width: 300px; padding: 6px 0; background: #fff; border: 1px solid var(--o-filet);
  border-radius: 6px; box-shadow: 0 14px 34px rgba(0,0,0,.22); z-index: 29; }
.t12-menu div { height: 46px; display: flex; align-items: center; padding: 0 22px; font-size: 19px; color: var(--o-texte); white-space: nowrap; }
/* l'action « Analyse AITE » (pos_dashboard.scss, à l'échelle de la vidéo) */
.t12-tabs { position: absolute; left: 0; right: 0; top: 0; height: 62px; background: #fff; border-bottom: 1px solid rgba(0,0,0,.08);
  display: flex; align-items: center; gap: 6px; padding: 0 16px; }
.t12-tab { height: 44px; padding: 0 16px; border: 1px solid transparent; border-radius: 10px; display: inline-flex; align-items: center; gap: 8px;
  font-size: 17px; color: #5f5e5a; white-space: nowrap; }
.t12-tab.t12-sans { padding-left: 20px; }
.t12-tab .ico { width: 18px; height: 18px; display: inline-flex; }
.t12-tab .ico svg { width: 18px; height: 18px; }
.t12-tab.on { background: #714B67; border-color: #714B67; color: #fff; }
.t12-corps { position: absolute; left: 0; right: 0; top: 62px; bottom: 0; overflow: hidden; background: #e8e6e0; }
.t12-defil { position: absolute; left: 0; right: 0; top: 0; padding: 14px 16px; }
.t12-fbar { background: #fff; border: 1px solid rgba(0,0,0,.08); border-radius: 14px; padding: 2px 18px; }
.t12-frow { height: 50px; display: flex; align-items: center; gap: 8px; }
.t12-frow + .t12-frow { border-top: 1px dashed rgba(0,0,0,.14); }
.t12-flab { min-width: 86px; font-size: 13.5px; font-weight: 600; letter-spacing: .5px; text-transform: uppercase; color: var(--t12-muet); }
.t12-fb { height: 34px; padding: 0 14px; border: 1px solid rgba(0,0,0,.1); border-radius: 17px; font-size: 15.5px; color: #5f5e5a;
  background: #fff; display: inline-flex; align-items: center; white-space: nowrap; flex: none; }
.t12-fb.on { background: #714B67; border-color: #714B67; color: #fff; }
.t12-fb.alt-on { background: #185FA5; border-color: #185FA5; color: #fff; }
.t12-fb.jour { min-width: 52px; justify-content: center; }
.t12-tous { width: 60px; height: 34px; flex: none; }
.t12-dot { width: 11px; height: 11px; border-radius: 50%; margin-right: 7px; display: inline-block; }
.t12-esp { flex: 1; }
.t12-du { font-size: 15px; color: #6c757d; white-space: nowrap; }
.t12-date { height: 36px; padding: 0 10px 0 12px; border: 1px solid rgba(0,0,0,.12); border-radius: 8px; font-size: 15.5px; color: #212529;
  display: inline-flex; align-items: center; gap: 22px; white-space: nowrap; }
.t12-date.focus { border-color: #714B67; box-shadow: 0 0 0 3px rgba(113,75,103,.18); }
.t12-date .ph { display: none; }
.t12-cal { width: 16px; height: 16px; display: inline-flex; color: #212529; }
.t12-cal svg { width: 16px; height: 16px; }
.t12-ok { height: 34px; padding: 0 18px; border-radius: 17px; background: #714B67; color: #fff; font-size: 15.5px; display: inline-flex; align-items: center; }
.t12-heure { width: 62px; height: 38px; border: 1px solid rgba(0,0,0,.12); border-radius: 8px; font-size: 16px; color: #212529;
  display: inline-flex; align-items: center; justify-content: center; }
.t12-contenu { position: relative; margin-top: 14px; }
.t12-c { position: absolute; left: 0; right: 0; top: 0; }
.t12-g4 { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; }
.t12-g4 + .t12-g4, .t12-strip + .t12-g4, .t12-g4 + .t12-strip { margin-top: 12px; }
.t12-g2 { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); gap: 24px; }
.t12-g3 { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 22px; }
.t12-mt14 { margin-top: 14px; }
.t12-kpi { min-width: 0; background: #f5f5f4; border-radius: 10px; padding: 12px 18px 13px; }
.t12-haut { border-top: 4px solid transparent; }
.t12-kpi .l { font-size: 15px; color: #5f5e5a; white-space: nowrap; }
.t12-kpi .v { margin-top: 3px; font-size: 28px; font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: #212529; }
.t12-kpi.t12-petite .v { font-size: 22px; }
.t12-kpi .s { margin-top: 3px; font-size: 14px; color: #5f5e5a; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.t12-sur { font-size: 15px; color: var(--t12-muet); }
.t12-kc .v { font-size: 23px; }
.t12-strip { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
.t12-dc { height: 52px; background: #fff; border: 1px solid rgba(0,0,0,.08); border-radius: 10px; padding: 0 18px; display: flex;
  align-items: center; justify-content: space-between; }
.t12-dl { font-size: 16px; color: var(--t12-muet); }
.t12-dv { font-size: 19px; font-weight: 700; }
.t12-dv.up { color: #3B6D11; } .t12-dv.down { color: #A32D2D; }
.t12-mod { background: #fff; border: 1px solid rgba(0,0,0,.08); border-radius: 14px; overflow: hidden; margin-top: 14px; }
.t12-mh { height: 66px; padding: 0 18px; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid rgba(0,0,0,.06); }
.t12-mhl { display: flex; align-items: center; gap: 14px; }
.t12-mi { width: 42px; height: 42px; border-radius: 10px; display: flex; align-items: center; justify-content: center; color: #fff; flex: none; }
.t12-mi svg { width: 22px; height: 22px; }
.t12-mt { font-size: 19px; font-weight: 500; }
.t12-ms { margin-top: 1px; font-size: 14px; color: var(--t12-muet); }
.t12-mb { padding: 14px 18px 16px; }
.t12-st { margin-bottom: 10px; font-size: 14px; font-weight: 500; letter-spacing: .04em; text-transform: uppercase; color: #5f5e5a; }
.t12-svg { display: block; width: 100%; height: auto; }
.t12-ax { font-size: 13px; fill: var(--t12-muet); font-family: var(--sans); }
.t12-leg { display: flex; gap: 22px; margin: -2px 0 6px; font-size: 15px; color: #212529; }
.t12-leg span { display: inline-flex; align-items: center; gap: 7px; }
.t12-leg i { width: 22px; display: inline-block; }
/* catégories */
.t12-cr { margin-bottom: 11px; }
.t12-crh { display: flex; justify-content: space-between; align-items: center; font-size: 16px; margin-bottom: 5px; color: #212529; }
.t12-crn { display: flex; align-items: center; gap: 9px; }
.t12-crh small { font-size: 13px; color: var(--t12-muet); margin-left: 4px; }
.t12-cd { width: 11px; height: 11px; border-radius: 50%; display: inline-block; flex: none; margin-right: 8px; }
.t12-crn .t12-cd { margin-right: 0; }
.t12-pb { height: 7px; background: #f5f5f4; border-radius: 4px; overflow: hidden; }
.t12-pb i { display: block; height: 100%; border-radius: 4px; }
/* caisses (module du tableau de bord) */
.t12-ann { display: flex; align-items: center; gap: 34px; padding: 4px 0 0 30px; }
.t12-ann svg { width: 200px; height: 200px; flex: none; }
.t12-annleg div { display: flex; align-items: center; gap: 9px; font-size: 15px; color: #212529; margin: 6px 0; }
.t12-annleg i { width: 16px; height: 13px; display: inline-block; }
.t12-cl { display: flex; align-items: center; gap: 12px; padding: 10px 4px; border-bottom: 1px solid rgba(0,0,0,.08); font-size: 17px; color: #212529; }
.t12-cl .t12-cd { margin-right: 0; }
.t12-cln { flex: 0 0 200px; font-weight: 700; }
.t12-clca { flex: 0 0 150px; text-align: right; font-weight: 600; }
.t12-clp { flex: 1; text-align: right; font-size: 15px; color: #6c757d; }
.t12-cltot { border-bottom: 0; border-top: 2px solid #eeede8; }
/* badges (badge_pill) */
.t12-b { display: inline-block; padding: 2px 11px; border-radius: 12px; font-size: 14.5px; font-weight: 500; white-space: nowrap; }
.b-teal { background: #E1F5EE; color: #0F6E56; } .b-amb { background: #FAEEDA; color: #854F0B; }
.b-red { background: #FCEBEB; color: #A32D2D; } .b-blu { background: #E6F1FB; color: #185FA5; }
/* carte de chaleur */
.t12-ins { display: flex; gap: 8px; }
.t12-chip { height: 32px; padding: 0 14px; border-radius: 16px; background: #eeede8; color: #5f5e5a; font-size: 15.5px; font-weight: 500;
  display: inline-flex; align-items: center; white-space: nowrap; }
.t12-hmw { position: relative; }
.t12-hm { width: 100%; border-collapse: separate; border-spacing: 3px; table-layout: fixed; }
.t12-hm th { height: 28px; font-size: 14px; font-weight: 600; color: var(--t12-muet); text-align: center; }
.t12-hm th.t12-hc { width: 80px; text-align: left; white-space: nowrap; }
.t12-hm td { height: 38px; text-align: center; font-size: 19px; font-weight: 700; letter-spacing: -.02em; }
.t12-hm td.t12-hd { font-size: 15px; font-weight: 600; color: var(--t12-muet); text-align: left; letter-spacing: 0; }
.t12-soir { position: absolute; top: 32px; bottom: 0; }
/* classements */
.t12-rk { display: flex; align-items: center; gap: 9px; padding: 6px 0; border-bottom: 1px solid rgba(0,0,0,.05); font-size: 15px; color: #212529; }
.t12-rk .n { width: 18px; text-align: right; font-size: 14px; color: var(--t12-muet); }
.t12-rk .nm { flex: 1; min-width: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.t12-rk .bg { flex: 0 0 80px; height: 7px; background: #f5f5f4; border-radius: 3px; overflow: hidden; }
.t12-rk .bg i { display: block; height: 7px; }
.t12-rk .vl { width: 70px; text-align: right; font-size: 14px; color: #5f5e5a; }
/* tableaux (o_aite_table) */
.t12-t { width: 100%; border-collapse: collapse; font-size: 16.5px; color: #212529; }
.t12-t thead { background: #f5f5f4; }
.t12-t th { height: 42px; padding: 0 14px; font-size: 14px; font-weight: 500; letter-spacing: .03em; text-transform: uppercase; color: #5f5e5a;
  text-align: left; white-space: nowrap; }
.t12-t td { height: 48px; padding: 0 14px; border-bottom: 1px solid rgba(0,0,0,.05); white-space: nowrap; }
.t12-t .r { text-align: right; }
.t12-t tfoot td { border-bottom: 0; border-top: 2px solid #eeede8; }
.t12-b6 { font-weight: 600; }
.t12-muet { color: #6c757d; }
.t12-nomt { margin-top: 14px; }
.t12-mtable .t12-mb { padding: 0; }
/* articles */
.t12-cats { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }
.t12-sb { margin-top: 12px; height: 52px; background: #fff; border: 1px solid rgba(0,0,0,.08); border-radius: 10px; padding: 0 16px;
  display: flex; align-items: center; gap: 14px; }
.t12-sb .entree.t12-q { flex: 1; margin: 0; height: 40px; border: 0; padding: 0 2px; font-size: 17px; box-shadow: none; }
.t12-sb .entree.t12-q .ph, .t12-sb .entree.t12-q .val { left: 2px; }
.t12-sbn { font-size: 15px; color: #6c757d; white-space: nowrap; }
.t12-artpile { position: relative; }
.t12-artmod { position: absolute; left: 0; right: 0; top: 0; }
.t12-ah, .t12-arow { display: grid; align-items: center; column-gap: 0; }
.t12-ah { height: 42px; background: #f5f5f4; font-size: 14px; font-weight: 500; letter-spacing: .03em; text-transform: uppercase; color: #5f5e5a; }
.t12-arow { height: 48px; border-bottom: 1px solid rgba(0,0,0,.05); font-size: 16.5px; color: #212529; }
.t12-ah > span, .t12-arow > span { padding: 0 14px; white-space: nowrap; min-width: 0; }
.t12-ah .r, .t12-arow .r { text-align: right; }
/* le panneau d'un article (slide-over) */
.t12-voile { position: absolute; inset: 0; background: rgba(0,0,0,.25); z-index: 30; }
.t12-panel { position: absolute; right: 0; top: 0; bottom: 0; width: 540px; background: #fff; z-index: 31; box-shadow: -6px 0 28px rgba(0,0,0,.18); }
.t12-ph { height: 64px; padding: 0 20px 0 24px; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid rgba(0,0,0,.08);
  font-size: 20px; font-weight: 500; color: #212529; }
.t12-px { font-size: 34px; line-height: 1; color: var(--t12-muet); padding: 0 6px; }
.t12-pbody { padding: 22px 24px; }
.t12-pcat { margin-bottom: 16px; }
.t12-mini { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 9px; margin-bottom: 18px; }
.t12-mini .t12-kpi { padding: 12px 14px; }
.t12-mini .t12-kpi .v { font-size: 19px; }
.t12-f { margin-bottom: 14px; }
.t12-fl { font-size: 15px; color: #5f5e5a; margin-bottom: 3px; }
.t12-fv { font-size: 18px; font-weight: 700; color: #212529; }
.t12-fv.t12-big { font-size: 22px; }
.t12-ft { display: flex; align-items: center; gap: 14px; margin-top: 2px; }
.t12-ft b { font-size: 27px; }
.t12-pbl { flex: 1; }
.t12-sep { height: 1px; background: rgba(0,0,0,.08); margin: 14px 0; }
/* les réactions de Danielle, loin de ce qu'elles commentent */
#t12-r-biere { left: 140px; right: auto; top: 150px; bottom: auto; }
#t12-r-ecart { top: 488px; bottom: auto; }
"""

TUTORIEL = {
    'slug': 't12-ventes',
    'profil': 't12_ventes',
    'numero': 12,
    'titre': 'Bar et restaurant : voyez enfin ce que vous gagnez',
    'fonction': 'Analyse des ventes',
    'personnage': (NOM, ROLE),
    'accroche': {
        'kicker': 'Bar et restaurant',
        'question': 'Votre bar encaisse. Mais que *gagne-t-il* vraiment ?',
        'douleurs': [('interrogation', 'Quelle marge sur chaque article ?'),
                     ('pieces', 'Quelle caisse tire le chiffre ?'),
                     ('horloge', 'Le bar tourne à quelle heure ?'),
                     ('alerte', 'Des écarts de caisse noyés'),
                     ('graphe', 'Le CA visible, la marge inconnue'),
                     ('sablier', 'La rentabilité découverte trop tard')],
        'voix': "Votre bar encaisse tous les soirs. Mais que gagne-t-il vraiment ? Quel article rapporte, quelle caisse "
                "tire le chiffre, à quelle heure le bar tourne-t-il ?",
    },
    'revelation': {
        'promesse': "Marge et coût des marchandises calculés seuls, sur chaque ligne vendue. Par caisse, par article, "
                    "par heure, et les écarts de caisse classés par gravité.",
        'voix': "Avec Aïte haousse, chaque vente dit ce qu'elle rapporte, et chaque caisse ce qu'il lui manque.",
    },
    'temps': ['Mesurer', 'Comprendre', 'Contrôler'],
    'app': 't12-app',
    'ecran': ECRAN,
    'css': CSS,
    'vues_initiales': {'odoo': 't12-pos'},
    'bulles': {
        't12-b-marge': "Marge = CA HT − coût d'achat, calculée sur chaque ligne de ticket.",
        't12-b-n1': 'Comparé à la période précédente, de même durée.',
        't12-b-heat': "Plus la case est foncée, plus le chiffre d'affaires est fort.",
        't12-b-caisse': 'Marge totale et par caisse.',
        't12-b-grav': '200 000 F manquants ou plus : Critique, en tête de liste.',
    },
    'reactions': {
        't12-r-biere': '850 F de marge sur chaque bouteille.',
        't12-r-ecart': 'Je sais quelle clôture vérifier en premier.',
    },
    'etapes': [
        {'temps': 0, 'titre': 'Le tableau de bord des ventes',
         'texte': "Point de Vente → Analyse AITE : chiffre d'affaires, marge, coût des marchandises, tickets.",
         'voix': "Dans le point de vente, Danielle ouvre Analyse Aïte, puis Tableau de bord. En tête : le chiffre "
                 "d'affaires, la marge brute, le coût des marchandises et les tickets. La marge se calcule sur chaque "
                 "ligne de ticket, sans rien saisir.",
         'gestes': [pause(0.3), clic(MENU_AITE, d=0.6, puis=0.1), montrer('#t12-menu', d=0.2, y=-6),
                    clic('#t12-menu-tdb', d=0.45, puis=0.1), cacher('#t12-menu', d=0.15), vue('t12-ana'), pause(0.4),
                    anneau('#t12-all-r1', d=1.6), curseur('#t12-all-marge', fx=0.7, fy=0.6, d=0.6, avec=True),
                    zoom('#t12-all-marge', s=1.6, d=0.8),
                    bulle('t12-b-marge', '#t12-all-marge', cote='bas', d=3.0), pause(2.8), dezoom(d=0.6),
                    anneau('#t12-all-ratio', d=1.1), anneau('#t12-all-taux', d=1.1)]},
        {'temps': 0, 'titre': 'Une période, face à la précédente',
         'texte': 'Du 01/10 au 13/10, puis « Analyser » : tout se recalcule, et une bande compare à la période '
                  'précédente.',
         'voix': "Danielle choisit ses dates, du premier au treize octobre, puis clique sur Analyser : tout se "
                 "recalcule. Une bande compare aussitôt le chiffre d'affaires, la marge, le coût et les commandes à la "
                 "période précédente, de même durée. Ici, la marge gagne douze pour cent.",
         'gestes': [clic('#t12-du', fx=0.2, d=0.7), saisir('t12-du', '01/10/2026', d=0.8), pause(0.2),
                    clic('#t12-ok-p', d=0.6), classe('#t12-pe-all', retirer=['on']), cacher('#t12-all', d=0.12),
                    montrer('#t12-m', d=0.25, y=0),
                    compter('#t12-m-ca-v', 0, CA, d=1.0, apres=' F', avec=True), pause(0.6),
                    anneau('#t12-strip', d=1.4), bulle('t12-b-n1', '#t12-strip', cote='bas', d=3.0),
                    anneau('#t12-strip-1', d=1.6), pause(0.8), anneau('#t12-m-r1', d=1.4)]},
        {'temps': 1, 'titre': 'Les heures de pointe',
         'texte': "La carte heure × jour : le pic de deux heures et le jour fort, calculés seuls.",
         'voix': "Plus bas, la carte des heures et des jours : plus la case est foncée, plus la vente est forte. Les "
                 "deux repères se calculent seuls : le meilleur créneau de deux heures tombe en soirée, et le samedi "
                 "est le jour fort. De quoi organiser le service du soir, et renforcer l'équipe le samedi.",
         'gestes': [defiler('#t12-defil', DEFIL_CHALEUR, d=1.6), pause(0.4),
                    curseur('#t12-ins', fx=0.25, fy=0.85, d=0.6), anneau('#t12-ins', d=1.6),
                    zoom('#t12-hm-tab', s=1.3, fx=ZOOM_HM_FX, fy=0.5, d=0.8),
                    anneau('#t12-hm-soir', d=1.6),
                    bulle('t12-b-heat', '#t12-hm-soir', cote='gauche', d=3.0), pause(2.8),
                    anneau('#t12-hm-d%d' % J_FORT, d=1.8), pause(0.4), dezoom(d=0.6)]},
        {'temps': 1, 'titre': 'Marge totale et par caisse',
         'texte': 'Bar de la terrasse et restaurant côte à côte : CA, marge, taux, panier, écart de caisse.',
         'voix': VOIX_CAISSES,
         'gestes': [defiler('#t12-defil', 0, d=0.9)] + onglet('dash', 'caisse', 't12-m', 't12-c-caisse')
                   + [pause(0.3), anneau('#t12-ck-1', d=1.1), anneau('#t12-ck-2', d=1.1), anneau('#t12-ck-3', d=1.0),
                      curseur('#t12-ctot', fx=0.1, d=0.6), anneau('#t12-ctab', d=1.6),
                      bulle('t12-b-caisse', '#t12-cmod-t', cote='droite', d=3.2), anneau('#t12-ctot', d=1.6),
                      pause(1.6), anneau('#t12-ck-4', d=1.2)]},
        {'temps': 1, 'titre': 'Les articles qui rapportent',
         'texte': "Recherche, puis le détail d'un article : prix, coût et marge ramenés à l'unité.",
         'voix': "Dans l'onglet Articles, Danielle tape bière : seules les bières restent. Un clic sur la bière "
                 "blonde ouvre son détail : quantité vendue, taux de marge, et surtout le prix, le coût et la marge "
                 "ramenés à l'unité. Ici, chaque bouteille laisse huit cent cinquante francs de marge.",
         'gestes': onglet('caisse', 'art', 't12-c-caisse', 't12-c-art')
                   + [clic('#t12-q', fx=0.2, d=0.6), saisir('t12-q', 'bière', d=0.6),
                      cacher('#t12-art-tous', d=0.05), montrer('#t12-art-bieres', d=0.05, y=0, avec=True),
                      texte('#t12-art-n', '%d / %d articles' % (len(BIERES), len(PRODUITS)), avec=True),
                      clic('#t12-ab-0', fx=0.12, d=0.6), montrer('#t12-voile', d=0.25, y=0),
                      montrer('#t12-panel', d=0.45, y=0, avec=True), pause(0.3), anneau('#t12-pn-taux', d=1.1),
                      zoom('#t12-pn-unit', s=1.45, fx=0.3, fy=0.1, d=0.7), anneau('#t12-pn-unit', d=1.6),
                      reaction('t12-r-biere', d=2.6), pause(2.2), dezoom(d=0.5),
                      clic('#t12-pn-x', d=0.5), cacher('#t12-panel', d=0.25), cacher('#t12-voile', d=0.2, avec=True)]},
        {'temps': 2, 'titre': 'Les écarts de caisse, classés par gravité',
         'texte': "Critique, élevé, modéré, excédent : la session à vérifier d'abord est en tête.",
         'voix': "Restent les écarts de caisse. À chaque clôture, l'argent compté est comparé à l'attendu, et "
                 "chaque session se classe toute seule, de la plus grave à la moins grave. En tête : à partir de deux "
                 "cent mille francs manquants, elle est critique. Un excédent ferme la liste.",
         'gestes': onglet('art', 'ecarts', 't12-c-art', 't12-c-ecarts')
                   + [pause(0.3), anneau('#t12-ek-1', d=1.0), anneau('#t12-ek-4', d=1.0),
                      curseur('#t12-e-r0-sev', fx=0.9, fy=1.1, d=0.6), zoom('#t12-e-r0', s=1.3, fx=0.5, d=0.8),
                      anneau('#t12-e-r0', d=1.6), bulle('t12-b-grav', '#t12-e-r0-qui', cote='bas', d=3.0), pause(2.8),
                      dezoom(d=0.6), curseur('#t12-e-r4-sev', fx=0.9, fy=1.1, d=0.5), anneau('#t12-e-r4', d=1.6),
                      reaction('t12-r-ecart', d=2.6), pause(1.6)]},
    ],
    'resultats': {
        'titre': 'Ce que vous gagnez, enfin visible',
        'cartes': [
            {'valeur': '8', 'compter': 8, 'unite': "onglets d'analyse", 'icone': 'graphe',
             'texte': 'tableau de bord, caisses, sessions, articles, marges, catégories, écarts, paiements'},
            {'valeur': '168', 'compter': 168, 'unite': 'cases heure × jour', 'icone': 'horloge',
             'texte': "7 jours × 24 heures, et le meilleur créneau de deux heures repéré seul"},
            {'valeur': '4', 'compter': 4, 'unite': 'niveaux de gravité', 'icone': 'alerte',
             'texte': 'pour les écarts de caisse : excédent, modéré, élevé, critique'},
        ],
        'voix': "Huit onglets d'analyse, une carte de cent soixante-huit cases heure par jour, quatre niveaux de "
                "gravité pour les écarts : on décide sur des chiffres, pas au ressenti.",
    },
    'cta': {
        'appel': 'Demandez votre démonstration',
        'suivant': 'Stock bar & cave',
        'voix': "Aïte haousse, par Aïte Consulting. Demandez votre démonstration, et retrouvez tous nos tutoriels sur "
                "notre chaîne.",
    },
    'vignette': {'etape': 3, 'apres': 3.2},
}
