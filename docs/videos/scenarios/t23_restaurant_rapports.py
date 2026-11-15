# -*- coding: utf-8 -*-
"""Tutoriel 23 — Les rapports du restaurant.

Le dernier des huit tutoriels du restaurant (lot 1 : aite_pos_restaurant,
aite_pos_analytics, aite_pos_analytics_hr ; restaurant SANS hôtel, comme t16 :
demo.RESTO, demo.SOCIETE_RESTO). Le soir du jour de référence de la série
(mercredi 14/10/2026), après la fermeture de la caisse (t22), Edwige, la
manager (demo.POSTES_RESTO['manager']), lit les chiffres du jour dans la
gestion ; puis Landry, le chef de salle (demo.POSTES_RESTO['chef']), relit les
annulations avec son propre compte. La pastille du haut change de personne
par une classe (ecrans.css_personnage, comme t16 à t22). Storyboard :
scratchpad videos_resto/storyboards/t23.md (adapté : « Écarts au storyboard »).

Abréviations : R/ = addons/aite_pos_restaurant/ ; A/ = addons/aite_pos_analytics/ ;
H/ = addons/aite_pos_analytics_hr/ ; O/ = ../odoo18/addons/ ; N =
docs/NOTES_DE_VERSION_restaurant_lot1.md ; rec = recette/cas_de_test.py ;
C/nn = captures/restaurant/nn_*.jpg (modèle visuel seulement). Les libellés
des vues et des modèles sont relus dans le code au chargement (garde-fous plus
bas) : un libellé changé dans un module fait échouer la construction de la
vidéo au lieu de la rendre fausse.

Le monde rejoué (conditions) :
- la gestion d'Odoo 18 sous le thème MuK ; la manager a le Point de Vente en
  administratrice et l'analyse AITE (barre ecrans.APPS_PROFIL['resto_manager'],
  menus ecrans.MENUS_MUK['point_de_vente'] ; docs/INSTALLATION.md §9.5) ; le
  chef de salle n'a que le profil « Restaurant : lecture des rapports »
  (APPS_PROFIL['resto_chef'], MENUS_MUK['restaurant']) ;
- la journée du 14/10 (JOURNEE ci-dessous) : les douze additions réglées de
  la session POS/00014 (le nom de session de t22). Elle tient ensemble ce que
  les tutoriels précédents MONTRENT : demo.TABLES_JOUR_RESTO (t17 à t20 :
  qui a ouvert quelle table, quand, avec quoi) ; t21 (la table 4 encaissée à
  13:52, 18 000 FCFA ; la table 2 divisée à 14:11, part « 2B » 6 000 FCFA en
  Mobile Money puis table 2, 9 000 FCFA en espèces ; la table 10 du soir,
  20 000 FCFA, à 19:56, toutes par Prisca) ; t22 (12 commandes, 188 500 FCFA,
  121 500 en espèces, 67 000 en Mobile Money, 11 tables, 33 personnes, aucune
  vente sans table ; tables 11 et 12 encore ouvertes à 22:30, annulées à la
  fermeture par Landry). Les autres additions reprennent celles de t22
  (JOURNEE interne de t22, jamais à l'écran), sauf la division : t22 la met
  sur la table 9 du soir, t21 la montre sur la table 2 ; la vidéo suit t21
  (la table 9 du soir devient une addition entière de 11 000 FCFA, pour garder
  les agrégats de t22). Les tables 3 et 8, les dernières du soir, sont
  encaissées par Landry (Prisca partie ; jamais montré ailleurs) ;
- les compteurs de chaque addition sont calculés par la règle du module
  (R/models/regles.py, ``compteurs`` et ``articles``, chargé tel quel) ; la
  marge de chaque ligne comme A/models/pos_order_line.py:50-58 (CA HT −
  coût, taux = marge ÷ CA HT × 100, arrondi à deux décimales) ; « Taux marge
  (%) » d'un groupe = moyenne simple des lignes (aggregator='avg',
  A/models/pos_analytics_report.py:51-55) ; une ligne par produit et par
  addition ; coûts de demo.CARTE_RESTO ;
- les annulations du jour : demo.ANNULATIONS_JOUR_RESTO (t19), puis les trois
  produits des tables 11 et 12 annulés à la fermeture (t22), à 22:31,
  « Demandée par » la personne identifiée sur le poste, Landry
  (R/models/pos_order.py:673-685), « Autorisée par » Landry, « Client parti ».

Écrans et libellés :

1. Point de Vente › Analyse › Personnes et tables (menu : R/views/
   restaurant_menus.xml:18-20, groupe point_of_sale.group_pos_manager) ; le
   menu « Analyse » déroulé : « Commandes », « Détails des ventes »,
   « Rapport de session », « Personnes et tables », puis la section « Analyse
   AITE » et ses six entrées (ecrans.MENU_ANALYSE_RESTO, MENU_ANALYSE_AITE ;
   A/views/pos_analytics_menus.xml:16-56 ; rendu d'un en-tête de section :
   O/web/static/src/webclient/navbar/navbar.xml:209-231, comme t12). La vue
   croisée (R/views/pos_order_views.xml:46-60 ; action :128-143 ; C/20) :
   titre « Personnes et tables », facette « Aujourd'hui » posée d'office
   (:134), « Rechercher… », boutons vue croisée / liste (view_mode
   « pivot,list », :131) ; « Mesures », inverser, tout déplier, télécharger
   (O/web/i18n/fr.po « Mesures », « Total ») ; colonnes « Tables »,
   « Personnes », « Ventes sans table », « Articles », « Total » (chaînes :
   R/models/pos_order.py:112-131 ; amount_total « Total », C/20) ; lignes
   « Total » et « 14 oct. 2026 » (date_order par jour, format de C/20) ;
   nombres d'Odoo : « 61,00 », « 188 500,00 » (C/20 ; N §7 l.589-591).
2. Le panneau de recherche (O/web/static/src/search/search_bar_menu/
   search_bar_menu.xml : trois colonnes « Filtres », « Regrouper par »,
   « Favoris » ; entrée cochée en gras avec la coche, webclient.scss:70-90 ;
   regroupement par date dépliable, search_arch_parser.js:196-203,
   accordion_item.xml) : « Aujourd'hui » coché, « Cette semaine », « Ce mois »,
   « Cette année », « Période », puis « Ajouter un filtre personnalisé » ;
   « Jour », « Session », « Ouverte par », « Encaissée par », puis « Ajouter
   un groupe personnalisé » (custom_group_by_item.xml) ; « Enregistrer la
   recherche actuelle » (custom_favorite_item.xml) — R/views/
   pos_order_views.xml:98-124. « Ouverte par » coché : facette de
   regroupement (icône des regroupements, couleur « action » d'Odoo, la
   couleur principale : primary_variables.scss:83 ; search_bar.xml:18-24), la
   vue croisée par serveur : « Inès », « Loïc » (hr.employee, ordre par nom).
3. La liste de « Personnes et tables » (R/views/pos_order_views.xml:66-85 ;
   C/21) : « Date », « Table », « Personnes », « Articles », « Ouverte par »,
   « Encaissée par », « Total » ; « Tables » et « Ventes sans table » masquées
   d'office (optional="hide") ; la table s'écrit « Salle, 4 » (nom affiché de
   la table, C/21) ; la part « 2B » n'a pas de table (O/pos_restaurant/static/
   src/app/split_bill_screen/split_bill_screen.js:101-109 : la commande de la
   part est créée sans table) ; date = heure du paiement (O/point_of_sale/
   static/src/app/screens/payment_screen/payment_screen.js:296), rangée la
   plus récente d'abord (O/point_of_sale/models/pos_order.py:30) ; sommes en
   pied (sum=) ; « 1-12 / 12 ».
4. Point de Vente › Analyse › Analyse AITE › Tableau croisé & graphique,
   favori « Ventes par famille » puis la session du jour : on y passe par un
   fondu (l'action s'ouvre regroupée par catégorie de produit,
   A/views/pos_analytics_report_views.xml:119 ; N l.447-449 : écran non
   rejoué, voir « Écarts ») ; titre « Analyse POS — Marge & CMV » (:115) ;
   facette favori (étoile jaune, C/23) « Ventes par famille » (:142-152) et
   facette de champ « Session » « POS/00014 » (:76) ; vues croisée, graphique,
   liste (:117 ; C/23) ; colonnes « CA HT », « CMV », « Marge », « Taux marge
   (%) » (A/models/pos_analytics_report.py:39-55) sous une seule colonne
   « Total » (pivot_column_groupby vide, :150) ; lignes « Nourriture »,
   « Nourriture / Pizzas », « Boisson », « Boisson / Alcoolisé », « Boisson /
   Non alcoolisé » (nom complet de la famille : O/point_of_sale/models/
   pos_category.py:52-54 ; C/23 ; ordre des familles de C/23). Le panneau :
   « Date », « Ajouter un filtre personnalisé » ; « Article », « Catégorie »,
   « Famille », « Sous-famille », « Sous-sous-famille », « Point de vente »,
   « Session », « Serveur », « Encaissée par », « Compte Odoo », « Jour »,
   « Semaine », « Mois » (A/views/pos_analytics_report_views.xml:83-109 ;
   H/views/pos_analytics_report_views.xml:16-24) ; « Ventes par famille »
   coché (favori partagé : search_bar_menu.js:156-166, poubelle :
   search_bar_menu.xml FavoriteItem), « Enregistrer la recherche actuelle ».
5. Le compte de Landry : barre « Discussion », « Restaurant », « Tableaux de
   bord », « Employés », « Apps » (ni Point de Vente ni configuration :
   R/security/restaurant_security.xml:18-23 ; rec R83) ; Restaurant ›
   Annulations (R/views/restaurant_menus.xml:9-14 ; action R/views/
   restaurant_annulation_views.xml:101-112 ; C/22) : « Aujourd'hui »,
   « 1-7 / 7 », vues liste, tableau croisé, graphique ; colonnes « Date »,
   « Table », « Produit », « Quantité », « Montant TTC », « Demandée par »,
   « Autorisée par », « Motif », « Précision » (:20-28 ; R/models/
   restaurant_annulation.py:40-74) ; la ligne sans code en rouge
   (decoration-danger, :15) ; totaux (:23-24). Le panneau (:68-97) :
   « Aujourd'hui », « Cette semaine », « Ce mois », « Cette année »,
   « Période », « Sans code », « Ajouter un filtre personnalisé » ; « Motif »,
   « Demandée par », « Autorisée par », « Produit », « Jour », « Ajouter un
   groupe personnalisé » ; « Enregistrer la recherche actuelle ». Regroupée
   par « Motif » : « Autre (1) », « Client parti (5) », « Aucun (1) » (motif
   vide : O/web/i18n/fr.po « None » → « Aucun » ; les groupes rangés par
   motif, le vide en dernier), sommes de chaque groupe ; « 1-3 / 3 ».

Règles dites par la voix, les bulles, la réaction et les résultats :
- seules les additions réglées comptent, ni ouvertes ni annulées :
  R/views/pos_order_views.xml:42-43, :132 ; rec R94 ;
- tables, personnes, ventes sans table, articles et total « sur la même
  page », « Aujourd'hui » d'office : :51-58, :134 ; rec R91 ; N l.145-149 ;
- une part divisée a 0 personne, la table ne compte qu'une fois :
  R/models/regles.py:169-185 ; R/models/pos_order.py:112-121 ; aide de
  l'action :140 ; rec R93 ;
- les périodes (aujourd'hui, semaine, mois, année, période libre) et les
  regroupements par « Ouverte par » et « Encaissée par » : :87-124 ; rec R07,
  R88, R89 ; « Ouverte par » figé, « Encaissée par » écrit au paiement :
  R/models/pos_order.py:82-94, :241-244 ;
- le favori « Ventes par famille » : Famille puis Sous-famille, une seule
  colonne « Total », en deux touches : A/views/pos_analytics_report_views.
  xml:134-152 ; N l.177-180 ; rec R84 ; il remplace la recherche en cours :
  O/web/static/src/search/search_model.js:927-928 ; trois niveaux de
  familles : A/models/pos_analytics_report.py:69-87 ; N l.173-176 ;
- le chef de salle lit les annulations sans la caisse ni la configuration :
  R/security/restaurant_security.xml:4-23 ; rec R83 ; la ligne rouge, passée
  sans code, jamais refusée, toujours tracée : R/models/
  restaurant_annulation.py:9-13, R/views/restaurant_annulation_views.xml:15 ;
  N l.124-125 ; regroupement par motif : rec R81.

Écarts au storyboard :
- l'équipe est celle de demo.EQUIPE_RESTO (Edwige, Landry ; Inès et Loïc
  serveurs ; Prisca caissière) : les prénoms du storyboard sont déjà pris
  dans le dépôt ;
- la journée suit t21 pour la division (table 2, part « 2B ») et garde les
  agrégats de t22 ; 61 articles (et non 60) ; les montants par famille,
  par serveur et par personne qui encaisse en découlent (calculés ici) ;
- étape 4 : pas de clic sur « Tableau croisé & graphique » suivi du favori :
  l'action s'ouvre par catégorie de produit, et la catégorie d'une base neuve
  s'appelle « All » (O/product/data/product_data.xml:4-6, sans traduction dans
  O/product/i18n/fr.po) ; on passe à l'état « favori + session » par un fondu,
  puis le panneau montre le favori coché ;
- pas de recherche « Alcoolisé » ni de regroupement par « Serveur » dans
  l'analyse : la proposition d'autocomplétion et le menu d'en-tête de la vue
  croisée ne sont relevés sur aucune capture, et l'étape 2 donne déjà le
  chiffre de chaque serveur (« Personnes et tables » regroupée par « Ouverte
  par ») ;
- étape 5 (le chef de salle) : une liste du jour entier (sept lignes), puis
  regroupée par motif, angle que t19 (la manager, à 13:48) ne montre pas ;
- le tutoriel suivant annoncé est le premier de la série (t23 la ferme).
"""

import ast
import importlib.util
import os
import re
import xml.etree.ElementTree as ET

import demo
from ecrans import (APPS_PROFIL, ICONES, MENU_ANALYSE_AITE, MENU_ANALYSE_RESTO, MENUS_MUK, NBSP, _odoo_dir,
                    css_personnage, e, entier, fcfa, fenetre_muk, icone, navigateur, superpose)
from marketing import bulle, dezoom, reaction, zoom
from moteur import anneau, cacher, classe, clic, curseur, montrer, pause, survol, vue

RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
R = os.path.join(RACINE, 'addons', 'aite_pos_restaurant')
A = os.path.join(RACINE, 'addons', 'aite_pos_analytics')
H = os.path.join(RACINE, 'addons', 'aite_pos_analytics_hr')
O = os.path.join(_odoo_dir(), 'addons')


def _lire(*chemin):
    with open(os.path.join(*chemin), encoding='utf-8') as f:
        return f.read()


def _une_ligne(texte_):
    return ' '.join((texte_ or '').split())


def dans(extrait, source, quoi):
    """Garde-fou : ``extrait`` doit être mot pour mot dans ``source`` (espaces ramenées à une seule)."""
    assert _une_ligne(extrait) in _une_ligne(source), ('t23 : %s changé' % quoi, extrait)


def _arch(*chemin):
    """Les vues d'un fichier XML d'Odoo : {id du record: élément <field name="arch">}."""
    return {rec.get('id'): rec.find("field[@name='arch']") for rec in ET.parse(os.path.join(*chemin)).iter('record')
            if rec.find("field[@name='arch']") is not None}


def _chaine(source, champ):
    """Le libellé (``string``) d'un champ déclaré dans un modèle Python : ``champ = fields.X(… string="…"`` ou
    ``fields.X("…"``."""
    m = re.search(r'\n\s+%s = fields\.\w+\(\s*(?:[\'"][\w.]+[\'"],\s*)?(?:string=)?"([^"]+)"' % re.escape(champ), source)
    assert m, ('t23 : champ introuvable', champ)
    return m.group(1)


# ============================================================== garde-fous --
# 1. « Personnes et tables » : la vue croisée, la liste, la recherche et l'action (R/views/pos_order_views.xml).
_PT = _arch(R, 'views', 'pos_order_views.xml')
_PIVOT = _PT['view_pos_order_pivot_personnes_tables'].find('pivot')
assert _PIVOT.get('string') == 'Personnes et tables'
assert [(f.get('name'), f.get('type')) for f in _PIVOT] == [
    ('date_order', 'row'), ('aite_tables', 'measure'), ('aite_personnes', 'measure'), ('aite_sans_table', 'measure'),
    ('aite_articles', 'measure'), ('amount_total', 'measure')], 't23 : mesures de « Personnes et tables » changées'
assert _PIVOT[0].get('interval') == 'day'
_LISTE_PT = _PT['view_pos_order_list_personnes_tables'].find('list')
assert [(f.get('name'), f.get('string'), f.get('optional'), f.get('sum')) for f in _LISTE_PT
        if f.get('column_invisible') != '1'] == [
    ('date_order', 'Date', None, None), ('table_id', None, None, None), ('aite_tables', None, 'hide', 'Tables'),
    ('aite_personnes', None, None, 'Personnes'), ('aite_sans_table', None, 'hide', 'Ventes sans table'),
    ('aite_articles', None, None, 'Articles'), ('aite_ouverte_par_id', None, None, None),
    ('aite_encaissee_par_id', None, None, None), ('amount_total', 'Total', None, 'Total')], \
    't23 : colonnes de la liste « Personnes et tables » changées'
_RECH_PT = _PT['view_pos_order_search_personnes_tables'].find('search')
FILTRES_PT = [f.get('string') for f in _RECH_PT.findall('filter')]
GROUPES_PT = [f.get('string') for f in _RECH_PT.find('group').findall('filter')]
assert FILTRES_PT == ["Aujourd'hui", 'Cette semaine', 'Ce mois', 'Cette année', 'Période'], FILTRES_PT
assert _RECH_PT.findall('filter')[-1].get('date') == 'date_order'     # « Période » : le filtre de date d'Odoo
assert GROUPES_PT == ['Jour', 'Session', 'Ouverte par', 'Encaissée par'], GROUPES_PT
assert _RECH_PT.find('group').findall('filter')[0].get('context') == "{'group_by': 'date_order:day'}"
_PT_XML = _lire(R, 'views', 'pos_order_views.xml')
for _x in ('<field name="name">Personnes et tables</field>', '<field name="view_mode">pivot,list</field>',
           "<field name=\"domain\">[('state', 'in', ('paid', 'done', 'invoiced'))]</field>",
           "<field name=\"context\">{'search_default_aujourd_hui': 1, 'create': False}</field>",
           "une part d'addition divisée ne compte pas deux fois, et une vente sans table est comptée à part."):
    dans(_x, _PT_XML, 'l\'action « Personnes et tables »')
_POS_ORDER = _lire(R, 'models', 'pos_order.py')
assert [_chaine(_POS_ORDER, c) for c in ('aite_tables', 'aite_personnes', 'aite_sans_table', 'aite_articles',
                                         'aite_ouverte_par_id', 'aite_encaissee_par_id')] == [
    'Tables', 'Personnes', 'Ventes sans table', 'Articles', 'Ouverte par', 'Encaissée par'], \
    't23 : libellés des compteurs changés'
for _x in ('help="L\'employé qui a ouvert la table, reconnu par son code. Ne change " "plus ensuite.")',
           'help="L\'employé qui a validé le paiement avec son code.")',
           "vals['aite_encaissee_par_id'] = employe.id",
           # la trace d'une annulation : demandée par la personne identifiée sur le poste
           'serveur=demandeur or commande.employee_id.sudo() or None,'):
    dans(_x, _POS_ORDER, 'pos_order.py')

# 2. Les menus (R/views/restaurant_menus.xml) et le profil de lecture (R/security/restaurant_security.xml).
_MENUS = {m.get('id'): m for m in ET.parse(os.path.join(R, 'views', 'restaurant_menus.xml')).iter('menuitem')}
assert (_MENUS['menu_restaurant_root'].get('name'), _MENUS['menu_restaurant_annulation'].get('name')) == \
    ('Restaurant', 'Annulations')
assert _MENUS['menu_restaurant_root'].get('groups') == 'group_lecture_rapports'
assert (_MENUS['menu_personnes_tables'].get('name'), _MENUS['menu_personnes_tables'].get('parent'),
        _MENUS['menu_personnes_tables'].get('groups')) == ('Personnes et tables', 'point_of_sale.menu_point_rep',
                                                             'point_of_sale.group_pos_manager')
assert MENU_ANALYSE_RESTO[-1] == 'Personnes et tables'
_SECU = _lire(R, 'security', 'restaurant_security.xml')
for _x in ('<field name="name">Restaurant : lecture des rapports</field>',
           "<field name=\"implied_ids\" eval=\"[(4, ref('base.group_user'))]\"/>",
           'sans aucun droit sur la caisse ni sur les commandes : pour le chef de salle.'):
    dans(_x, _SECU, 'le profil de lecture')

# 3. Restaurant › Annulations (R/views/restaurant_annulation_views.xml, R/models/restaurant_annulation.py).
_AN = _arch(R, 'views', 'restaurant_annulation_views.xml')
_LISTE_AN = _AN['view_restaurant_annulation_list'].find('list')
assert (_LISTE_AN.get('decoration-danger'), _LISTE_AN.get('create'), _LISTE_AN.get('edit')) == \
    ('not autorisee', '0', '0'), 't23 : la liste des annulations a changé'
_COL_AN = [f.get('name') for f in _LISTE_AN if f.get('optional') != 'hide' and f.get('column_invisible') != 'True']
assert _COL_AN == ['date', 'table_nom', 'produit_nom', 'quantite', 'montant', 'serveur_nom', 'superieur_nom',
                   'motif_nom', 'commentaire'], _COL_AN
assert [f.get('name') for f in _LISTE_AN if f.get('sum')] == ['quantite', 'montant']
_MOD_AN = _lire(R, 'models', 'restaurant_annulation.py')
COLONNES_AN = [_chaine(_MOD_AN, c) for c in _COL_AN]
assert COLONNES_AN == ['Date', 'Table', 'Produit', 'Quantité', 'Montant TTC', 'Demandée par', 'Autorisée par',
                       'Motif', 'Précision'], COLONNES_AN
dans("_order = 'date desc, id desc'", _MOD_AN, "l'ordre du journal")
dans('Elle ne se modifie pas et ne s\'efface pas, même en ``sudo()`` ou pour l\'administrateur.', _MOD_AN,
     'le journal figé')
_RECH_AN = _AN['view_restaurant_annulation_search'].find('search')
FILTRES_AN = [f.get('string') for f in _RECH_AN.findall('filter')]
GROUPES_AN = [f.get('string') for f in _RECH_AN.find('group').findall('filter')]
assert FILTRES_AN == ["Aujourd'hui", 'Cette semaine', 'Ce mois', 'Cette année', 'Période', 'Sans code'], FILTRES_AN
assert [c.tag for c in _RECH_AN][-3:] == ['separator', 'filter', 'group'], "t23 : le séparateur avant « Sans code »"
assert GROUPES_AN == ['Motif', 'Demandée par', 'Autorisée par', 'Produit', 'Jour'], GROUPES_AN
assert _RECH_AN.find('group').findall('filter')[0].get('context') == "{'group_by': 'motif_nom'}"
_AN_XML = _lire(R, 'views', 'restaurant_annulation_views.xml')
for _x in ('<field name="name">Annulations</field>', '<field name="view_mode">list,pivot,graph</field>',
           "<field name=\"context\">{'search_default_aujourd_hui': 1, 'create': False}</field>"):
    dans(_x, _AN_XML, "l'action « Annulations »")

# 4. L'analyse AITE (A/) et la passerelle par employé (H/).
_ANA = _arch(A, 'views', 'pos_analytics_report_views.xml')
_PIVOT_A = _ANA['view_pos_daily_report_pivot'].find('pivot')
MESURES_A = [f.get('name') for f in _PIVOT_A if f.get('type') == 'measure']
assert MESURES_A == ['price_subtotal', 'total_cost', 'margin', 'margin_rate'], MESURES_A
_MOD_A = _lire(A, 'models', 'pos_analytics_report.py')
COLONNES_A = [_chaine(_MOD_A, c) for c in MESURES_A]
assert COLONNES_A == ['CA HT', 'CMV', 'Marge', 'Taux marge (%)'], COLONNES_A
assert [_chaine(_MOD_A, c) for c in ('famille_n1_id', 'famille_n2_id', 'famille_n3_id', 'session_id')] == \
    ['Famille', 'Sous-famille', 'Sous-sous-famille', 'Session']
dans("aggregator='avg',", _MOD_A, '« Taux marge (%) » en moyenne')
_RECH_A = _ANA['view_pos_daily_report_search'].find('search')
assert [f.get('string') for f in _RECH_A.findall('filter')] == ['Date'] and \
    _RECH_A.findall('filter')[0].get('date') == 'date'
_GROUPES_A = [f.get('string') for f in _RECH_A.find('group').findall('filter')]
assert _GROUPES_A == ['Article', 'Catégorie', 'Famille', 'Sous-famille', 'Sous-sous-famille', 'Point de vente',
                      'Session', 'Caissier', 'Jour', 'Semaine', 'Mois'], _GROUPES_A
_A_XML = _lire(A, 'views', 'pos_analytics_report_views.xml')
for _x in ('<field name="name">Analyse POS — Marge &amp; CMV</field>',
           '<field name="view_mode">pivot,graph,list</field>',
           "<field name=\"context\">{'group_by': ['categ_id']}</field>",
           '<field name="name">Ventes par famille</field>', '<field name="user_id" eval="False"/>',
           "<field name=\"context\">{'group_by': ['famille_n1_id', 'famille_n2_id'], 'pivot_column_groupby': []}"
           "</field>", '<data noupdate="1">'):
    dans(_x, _A_XML, 'l\'analyse AITE (vues)')
_MENUS_A = {m.get('id'): m.get('name') for m in ET.parse(os.path.join(A, 'views', 'pos_analytics_menus.xml'))
            .iter('menuitem')}
assert _MENUS_A['menu_aite_pos_analytics_root'] == 'Analyse AITE'
assert [_MENUS_A[k] for k in ('menu_aite_pos_dashboard', 'menu_aite_pos_caisse', 'menu_aite_pos_sessions',
                              'menu_aite_pos_categories', 'menu_aite_pos_discrepancies',
                              'menu_aite_pos_daily_report')] == MENU_ANALYSE_AITE
# H/ : « Serveur » et « Encaissée par » avant le regroupement par compte, renommé « Compte Odoo ».
_H_XML = _lire(H, 'views', 'pos_analytics_report_views.xml')
for _x in ('<filter string="Serveur" name="grp_serveur"', '<filter string="Encaissée par" name="grp_encaisse_par"',
           '<xpath expr="//filter[@name=\'grp_user\']" position="before">',
           '<attribute name="string">Compte Odoo</attribute>'):
    dans(_x, _H_XML, 'la passerelle par employé')
GROUPES_A = [g for g in _GROUPES_A]
GROUPES_A[GROUPES_A.index('Caissier'):GROUPES_A.index('Caissier') + 1] = ['Serveur', 'Encaissée par', 'Compte Odoo']

# 5. Odoo : les libellés français du panneau de recherche, des vues et du menu (O/web/i18n/fr.po ; les chaînes du
#    panneau : search_bar_menu.xml, custom_group_by_item.xml, custom_favorite_item.xml).
_PO = _lire(O, 'web', 'i18n', 'fr.po')
for _id, _str in (('Filters', 'Filtres'), ('Group By', 'Regrouper par'), ('Favorites', 'Favoris'),
                  ('Add Custom Filter', 'Ajouter un filtre personnalisé'),
                  ('Add Custom Group', 'Ajouter un groupe personnalisé'),
                  ('Save current search', 'Enregistrer la recherche actuelle'), ('Measures', 'Mesures'),
                  ('Total', 'Total'), ('Search...', 'Rechercher…'), ('None', 'Aucun')):
    assert re.search(r'\nmsgid "%s"\nmsgstr "%s"\n' % (re.escape(_id), re.escape(_str)), _PO), \
        ("t23 : libellé d'Odoo changé", _id, _str)
_MENU_XML = _lire(O, 'web', 'static', 'src', 'search', 'search_bar_menu', 'search_bar_menu.xml')
for _x in ('<h5 class="o_dropdown_title d-inline">Filters</h5>', '<h5 class="o_dropdown_title d-inline">Group By</h5>',
           '<h5 class="o_dropdown_title d-inline">Favorites</h5>', 'sharedFavoritesItems',
           'class="ms-1 fa fa-trash-o"'):
    dans(_x, _MENU_XML, 'le panneau de recherche d\'Odoo')
dans('if (searchItem.type === "favorite") { this.query = []; }',
     _lire(O, 'web', 'static', 'src', 'search', 'search_model.js'), 'le favori qui remplace la recherche')
dans('newOrder.floating_order_name = newOrderName;',
     _lire(O, 'pos_restaurant', 'static', 'src', 'app', 'split_bill_screen', 'split_bill_screen.js'),
     'la part sans table')
dans('this.currentOrder.date_order = serializeDateTime(luxon.DateTime.now());',
     _lire(O, 'point_of_sale', 'static', 'src', 'app', 'screens', 'payment_screen', 'payment_screen.js'),
     "l'heure du paiement")
dans('et 0 personne : les personnes restent sur * l\'origine (Odoo lui en retire une). */',
     _lire(R, 'static', 'src', 'overrides', 'split_bill_screen.js'), 'la part sans personne')
dans('cat.display_name = " / ".join(cat._get_hierarchy())',
     _lire(O, 'point_of_sale', 'models', 'pos_category.py'), 'le nom complet de la famille')

# 6. Les notes de version et la recette citées.
_NOTES = _lire(RACINE, 'docs', 'NOTES_DE_VERSION_restaurant_lot1.md')
for _x in ('favori partagé **« Ventes par famille »** (Famille > Sous-famille en deux touches, une seule colonne '
           '« Total » avec ses quatre mesures',
           'Trois colonnes **Famille, Sous-famille, Sous-sous-famille**',
           'tables, personnes, ventes sans table, articles et total, par jour, session, « Ouverte par », « Encaissée '
           'par » ; une division ne compte qu\'une fois',
           'tracé « Retrait sans code » ou « Annulation sans code ».'):
    dans(_x, _NOTES, 'les notes de version')
_REC = _lire(RACINE, 'recette', 'cas_de_test.py')
for _x in ('REST-25 c.1 — Tables, personnes et ventes sur la même page', 'REST-25 c.3 — Une table divisée compte une fois',
           'REST-02 c.4 — Regrouper par « Ouverte par » et « Encaissée par »',
           'REST-22 c.4, AH-05 — Le chef de salle lit sans accès à la caisse',
           'REST-22 c.2 — Sous-totaux par responsable ou par motif', 'REST-23 c.1 — Une famille additionne ses sous-familles'):
    dans(_x, _REC, 'la recette')

# 7. La règle des compteurs, chargée telle quelle (R/models/regles.py : Python pur, sans Odoo).
_spec = importlib.util.spec_from_file_location('t23_regles', os.path.join(R, 'models', 'regles.py'))
REGLES = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(REGLES)
assert REGLES.compteurs(0, True, False) == (0, 0, 0) and REGLES.compteurs(6, False, False) == (1, 6, 0)


def _source(relatif, nom, racine=R):
    """Une constante d'un fichier Python d'un module, lue sans importer Odoo (comme t16)."""
    for noeud in ast.parse(_lire(racine, relatif)).body:
        if isinstance(noeud, ast.Assign) and any(getattr(c, 'id', None) == nom for c in noeud.targets):
            return ast.literal_eval(noeud.value)
    raise ValueError('t23 : %s introuvable dans %s' % (nom, relatif))


_NATURES = dict(_source('models/restaurant_annulation.py', 'TYPES_ANNULATION'))
assert _NATURES['fermeture'] == 'Table annulée à la fermeture'
assert _source('models/pos_config.py', 'NOM_SALLE') == demo.SALLE_RESTO
assert [lib for _c, lib in _source('models/regles.py', 'NIVEAUX')][2] == demo.EQUIPE_RESTO[4][2]

# ============================================================== les données --
EDWIGE, ROLE_EDWIGE = demo.POSTES_RESTO['manager']
LANDRY, ROLE_LANDRY = demo.POSTES_RESTO['chef']
P_EDWIGE, P_LANDRY, P_PRISCA, P_INES, P_LOIC = (
    next(x[1] for x in demo.EQUIPE_RESTO if x[0] == demo.POSTES_RESTO[cle][0])
    for cle in ('manager', 'chef', 'caisse', 'serveuse', 'serveur'))
assert (P_EDWIGE, P_LANDRY, P_PRISCA, P_INES, P_LOIC) == ('Edwige', 'Landry', 'Prisca', 'Inès', 'Loïc')
PRIX = {nom: prix for nom, _f, prix, _c, _s in demo.CARTE_RESTO}
COUT = {nom: cout for nom, _f, _p, cout, _s in demo.CARTE_RESTO}
FAMILLE = {nom: fam for nom, fam, _p, _c, _s in demo.CARTE_RESTO}
SESSION = demo.SESSION_RESTO   # la session du 14/10 (t22)
assert SESSION == 'POS/00014'
ESP, MM = demo.MODES_RESTO
JOUR = demo.JOUR_RESTO

# La journée : les additions réglées de la session, dans l'ordre des paiements :
# (payée à, table ou part, ouverte par, personnes, contenu, mode, encaissée par).
JOURNEE = [
    ('12:35', '1', P_LOIC, 3, {'Pizza Reine': 1, 'Pizza Margherita': 2, 'Cola 33 cl': 2, 'Jus de bissap 50 cl': 1}, MM,
     P_PRISCA),
    ('13:15', '7', P_INES, 4, {'Pizza Margherita': 2, 'Pizza Reine': 2, 'Bière blonde 65 cl': 4}, MM, P_PRISCA),
    ('13:20', '10', P_LOIC, 2, {'Pizza Reine': 2, 'Bière blonde 65 cl': 4}, ESP, P_PRISCA),
    ('13:25', '6', P_INES, 2, {'Pizza quatre fromages': 1, 'Bière blonde 65 cl': 2}, ESP, P_PRISCA),
    ('13:52', '4', P_LOIC, 6, {'Pizza Margherita': 1, 'Bière blonde 65 cl': 2, 'Cola 33 cl': 2, 'Pizza quatre fromages': 1,
                               'Eau minérale 50 cl': 2}, ESP, P_PRISCA),
    ('14:05', '5', P_INES, 2, {'Pizza quatre fromages': 1, 'Bière blonde 65 cl': 2}, ESP, P_PRISCA),
    ('14:11', '2B', P_LOIC, 0, {'Pizza Reine': 1}, MM, P_PRISCA),
    ('14:12', '2', P_LOIC, 2, {'Cola 33 cl': 2, 'Pizza quatre fromages': 1}, ESP, P_PRISCA),
    ('19:56', '10', P_INES, 4, {'Pizza Reine': 1, 'Bière blonde 65 cl': 2, 'Cola 33 cl': 1, 'Pizza quatre fromages': 1,
                                'Bière brune 65 cl': 2}, ESP, P_PRISCA),
    ('20:48', '9', P_LOIC, 2, {'Pizza quatre fromages': 1, 'Bière blonde 65 cl': 2, 'Cola 33 cl': 1}, ESP, P_PRISCA),
    ('21:20', '3', P_LOIC, 4, {'Pizza quatre fromages': 2, 'Pizza Margherita': 1, 'Bière blonde 65 cl': 3,
                               'Cola 33 cl': 2}, ESP, P_LANDRY),
    ('21:35', '8', P_INES, 2, {'Pizza Reine': 2, 'Bière blonde 33 cl': 2}, MM, P_LANDRY),
]

assert JOURNEE == demo.JOURNEE_RESTO, 't23 : la journée commune (demo.JOURNEE_RESTO) a changé'

def _total(contenu):
    return sum(PRIX[p] * q for p, q in contenu.items())


# Ce que chaque addition compte (la règle du module : une part « 2B » n'a pas de personne).
ADDITIONS = []
for _h, _t, _ouv, _pers, _c, _mode, _enc in JOURNEE:
    _tab, _p, _sans = REGLES.compteurs(_pers, _t.endswith('B'), False)
    ADDITIONS.append({'heure': _h, 'table': _t, 'ouverte': _ouv, 'encaissee': _enc, 'tables': _tab, 'personnes': _p,
                      'sans_table': _sans, 'articles': REGLES.articles(list(_c.values())), 'total': _total(_c),
                      'mode': _mode, 'contenu': _c})


def somme(cle, filtre=lambda a: True):
    return sum(a[cle] for a in ADDITIONS if filtre(a))


TOTAL = {k: somme(k) for k in ('tables', 'personnes', 'sans_table', 'articles', 'total')}
# Ce que t22 affiche (fermeture : « 12 commandes : 188 500 FCFA », espèces, Mobile Money ; rapport : tables,
# personnes, ventes sans table) : la journée doit le redonner.
assert (len(ADDITIONS), TOTAL['total'], somme('total', lambda a: a['mode'] == ESP),
        somme('total', lambda a: a['mode'] == MM), TOTAL['tables'], TOTAL['personnes'], TOTAL['sans_table']) == \
    (12, 188500, 121500, 67000, 11, 33, 0), 't23 : la journée ne redonne plus les chiffres de t22'
assert TOTAL['articles'] == 61
# Ce que t21 affiche, et ce que demo.TABLES_JOUR_RESTO fixe (t17 à t20).
_PAR = {(a['table'], a['heure']): a for a in ADDITIONS}
assert (_PAR[('4', '13:52')]['total'], _PAR[('4', '13:52')]['articles'], _PAR[('4', '13:52')]['personnes']) == \
    (18000, 8, 6)
assert (_PAR[('2B', '14:11')]['total'], _PAR[('2B', '14:11')]['mode'], _PAR[('2B', '14:11')]['contenu']) == \
    (6000, MM, {'Pizza Reine': 1})
assert (_PAR[('2', '14:12')]['total'], _PAR[('2', '14:12')]['mode'], _PAR[('2', '14:12')]['personnes']) == (9000, ESP, 2)
assert (_PAR[('10', '19:56')]['total'], _PAR[('10', '19:56')]['mode'], _PAR[('10', '19:56')]['encaissee']) == \
    (20000, ESP, P_PRISCA)
_FIXE = {(t, ouv, h): (pers, contenu) for t, ouv, h, pers, contenu, _s, _tu in demo.TABLES_JOUR_RESTO}
assert _FIXE[(10, P_LOIC, '11:52')][1] == _PAR[('10', '13:20')]['contenu']
assert _FIXE[(5, P_INES, '13:05')] == (_PAR[('5', '14:05')]['personnes'], _PAR[('5', '14:05')]['contenu'])
assert _FIXE[(10, P_INES, '19:10')] == (_PAR[('10', '19:56')]['personnes'], _PAR[('10', '19:56')]['contenu'])
assert _FIXE[(4, P_LOIC, '12:15')][0] == _PAR[('4', '13:52')]['personnes']
assert all(_PAR[('4', '13:52')]['contenu'][p] >= q for p, q in _FIXE[(4, P_LOIC, '12:15')][1].items())
assert _FIXE[(2, P_LOIC, '12:55')][1] == {'Cola 33 cl': 2} and _PAR[('2', '14:12')]['contenu']['Cola 33 cl'] == 2

# Par serveur (« Ouverte par ») et par personne qui encaisse : (tables, personnes, ventes sans table, articles, total).
SERVEURS = sorted({a['ouverte'] for a in ADDITIONS})
PAR_SERVEUR = {s: tuple(somme(k, lambda a, s=s: a['ouverte'] == s)
                        for k in ('tables', 'personnes', 'sans_table', 'articles', 'total')) for s in SERVEURS}
assert SERVEURS == [P_INES, P_LOIC]
assert PAR_SERVEUR == {P_INES: (5, 14, 0, 25, 82000), P_LOIC: (6, 19, 0, 36, 106500)}, PAR_SERVEUR
assert sorted({a['encaissee'] for a in ADDITIONS}) == [P_LANDRY, P_PRISCA]

# L'analyse AITE de la session : une ligne par produit et par addition ; chemin de la famille depuis la racine.
CHEMIN = {}


def _chemins(branches, parents):
    for nom, _coul, sous in branches:
        CHEMIN[nom] = parents + [nom]
        _chemins(sous, parents + [nom])


_chemins(demo.FAMILLES_RESTO, [])
LIGNES_A = []
for _a in ADDITIONS:
    for _p, _q in _a['contenu'].items():
        _ca, _cmv = PRIX[_p] * _q, COUT[_p] * _q
        # A/models/pos_order_line.py:50-58 : marge = CA HT − CMV, taux = marge ÷ CA HT × 100 (2 décimales, digits=(5, 2))
        LIGNES_A.append({'chemin': CHEMIN[FAMILLE[_p]], 'ca': _ca, 'cmv': _cmv, 'marge': _ca - _cmv,
                         'taux': round((_ca - _cmv) / _ca * 100, 2)})


def analyse(filtre=lambda l: True):
    """(CA HT, CMV, Marge, Taux marge (%)) d'un groupe : sommes, et moyenne simple des taux (aggregator='avg')."""
    groupe = [l for l in LIGNES_A if filtre(l)]
    return (sum(l['ca'] for l in groupe), sum(l['cmv'] for l in groupe), sum(l['marge'] for l in groupe),
            sum(l['taux'] for l in groupe) / len(groupe) if groupe else 0)


FAMILLES_A = [('Total', 0, analyse())]
for _n1, _c1, _sous in demo.FAMILLES_RESTO:
    _g1 = analyse(lambda l, n=_n1: l['chemin'][0] == n)
    if not _g1[0]:
        continue
    FAMILLES_A.append((_n1, 1, _g1))
    for _n2, _c2, _s2 in _sous:
        _g2 = analyse(lambda l, n1=_n1, n2=_n2: l['chemin'][:2] == [n1, n2])
        if _g2[0]:
            FAMILLES_A.append(('%s / %s' % (_n1, _n2), 2, _g2))
assert [(lib, g[:3]) for lib, _n, g in FAMILLES_A] == [
    ('Total', (188500, 72550, 115950)), ('Nourriture', (140000, 53000, 87000)),
    ('Nourriture / Pizzas', (140000, 53000, 87000)), ('Boisson', (48500, 19550, 28950)),
    ('Boisson / Alcoolisé', (36500, 15850, 20650)), ('Boisson / Non alcoolisé', (12000, 3700, 8300))], FAMILLES_A
FAM_BOISSON = dict((lib, g) for lib, _n, g in FAMILLES_A)['Boisson']
FAM_ALCOOL = dict((lib, g) for lib, _n, g in FAMILLES_A)['Boisson / Alcoolisé']

# Les annulations du jour, dans l'ordre de la liste (« date desc, id desc ») : (date, table, produit, quantité,
# demandée par, autorisée par, motif, précision). D'abord les trois produits des tables 11 et 12 annulés à la
# fermeture (t22 : 11, Loïc, 2 Bière blonde 65 cl ; 12, Inès, Pizza Margherita puis Cola 33 cl), écrits dans l'ordre
# des additions et de leurs lignes, donc relus à l'envers ; puis le journal de t19.
FERMETURE = [('%s 22:31' % JOUR, '11', 'Bière blonde 65 cl', 2), ('%s 22:31' % JOUR, '12', 'Pizza Margherita', 1),
             ('%s 22:31' % JOUR, '12', 'Cola 33 cl', 1)]
ANNULATIONS = ([(d, t, p, q, P_LANDRY, P_LANDRY, demo.MOTIFS_RESTO[1], '') for d, t, p, q in reversed(FERMETURE)]
               + list(demo.ANNULATIONS_JOUR_RESTO))
assert ANNULATIONS[:3] == demo.ANNULATIONS_FERMETURE_RESTO, 't23 : les annulations de la fermeture ont changé'
assert demo.MOTIFS_RESTO[1] == 'Client parti'
QTE_AN = sum(a[3] for a in ANNULATIONS)
MONTANT_AN = sum(a[3] * PRIX[a[2]] for a in ANNULATIONS)
assert (len(ANNULATIONS), QTE_AN, MONTANT_AN) == (7, 9, 18500), 't23 : les annulations ne redonnent plus t22'
assert [a[5] for a in ANNULATIONS].count('') == 1 and ANNULATIONS[-1][5] == ''   # la ligne sans code, la plus ancienne
# Regroupées par motif : rangées par motif, le motif vide (« Aucun ») en dernier.
MOTIFS_AN = []
for _m in sorted({a[6] for a in ANNULATIONS if a[6]}) + ['']:
    _g = [a for a in ANNULATIONS if a[6] == _m]
    MOTIFS_AN.append((_m or 'Aucun', len(_g), sum(a[3] for a in _g), sum(a[3] * PRIX[a[2]] for a in _g)))
assert MOTIFS_AN == [('Autre', 1, 1, 1500), ('Client parti', 5, 7, 16000), ('Aucun', 1, 1, 1000)], MOTIFS_AN


# ============================================================ les écrans --
def odoo2(n):
    """Un nombre des vues croisées d'Odoo : deux décimales, sans devise (« 188 500,00 », C/20, C/23)."""
    entiers, dec = ('%.2f' % n).split('.')
    return entier(int(entiers)) + ',' + dec


def qte(n):
    """Une quantité d'Odoo (« 4,00 », C/21, C/22)."""
    return odoo2(n)


assert odoo2(188500) == '188' + NBSP + '500,00' and odoo2(62.3809) == '62,38'

# Icônes d'Odoo dessinées ici (ecrans.ICONES n'en a pas l'équivalent) : la case pleine « + » et la case vide « − »
# des en-têtes de la vue croisée (fa-plus-square, fa-minus-square-o, C/20), inverser les axes (fa-exchange), tout
# déplier (fa-arrows), les regroupements (oi-group, rendu comme t05), l'étoile des favoris (fa-star), la poubelle
# (fa-trash-o), la flèche d'un groupe de liste (fa-caret-right).
PLUS = ('<svg class="t23-pm" viewBox="0 0 16 16"><rect x="1" y="1" width="14" height="14" rx="2.5" fill="#343A40"/>'
        '<path d="M8 4.5v7M4.5 8h7" stroke="#fff" stroke-width="2"/></svg>')
MOINS = ('<svg class="t23-pm" viewBox="0 0 16 16"><rect x="1.6" y="1.6" width="12.8" height="12.8" rx="2.2" fill="none" '
         'stroke="#343A40" stroke-width="1.3"/><path d="M4.8 8h6.4" stroke="#343A40" stroke-width="1.5"/></svg>')
INVERSER = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" '
            'stroke-linejoin="round"><path d="M4 8h16l-4-4M20 16H4l4 4"/></svg>')
DEPLIER = ('<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 1.5l4 4h-2.8v5.3h5.3V8l4 4-4 4v-2.8h-5.3v5.3H16l-4 '
           '4-4-4h2.8v-5.3H5.5V16l-4-4 4-4v2.8h5.3V5.5H8z"/></svg>')
GROUPE = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round">'
          '<path d="M12 3l9 4.5-9 4.5-9-4.5z" fill="currentColor"/><path d="M3 12l9 4.5 9-4.5M3 16.5l9 4.5 9-4.5"/></svg>')
ETOILE = ('<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2.5l2.9 6.3 6.9.7-5.2 4.6 1.5 6.8L12 17.4l-6.1 '
          '3.5 1.5-6.8L2.2 9.5l6.9-.7z"/></svg>')
POUBELLE = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" '
            'stroke-linejoin="round"><path d="M4 6h16M9 6V4h6v2M6 6l1 14h10l1-14M10 10v7M14 10v7"/></svg>')
FLECHE_GROUPE = '<svg viewBox="0 0 16 16" fill="currentColor"><path d="M6 3.5l5 4.5-5 4.5z"/></svg>'


def facette(ident, genre, libelle, titre=None):
    """Une facette de la barre de recherche (O/web/static/src/search/search_bar/search_bar.xml:4-58) : l'étiquette
    colorée (filtre : entonnoir ; regroupement : icône des regroupements ; favori : étoile sur le jaune des favoris ;
    champ : le nom du champ en petit), la valeur, la croix. Identifiants : <ident>, <ident>-x."""
    tete = {'filtre': icone('filtre'), 'groupe': GROUPE, 'favori': ETOILE}.get(genre) or '<small>%s</small>' % e(titre)
    return ('<span class="facette t23-fac t23-fac-%s" id="%s"><span class="fic">%s</span><span class="ell">%s</span>'
            '<span class="fx" id="%s-x">×</span></span>' % (genre, ident, tete, e(libelle), ident))


VUES = {'pivot': ICONES['vue-pivot'], 'liste': ICONES['vue-liste'], 'graphe': ICONES['vue-graphe']}


def panneau_cp(ident, titre, facettes, vues, actif, pager=None):
    """Le panneau de contrôle d'une vue (thème MuK, C/20 à C/23) : le titre, la recherche au milieu (facettes,
    « Rechercher… », ▾), à droite la pagination et ses flèches (liste seulement) et le sélecteur des vues (l'ordre de
    ``view_mode``). Identifiants : <ident>-titre, <ident>-rech, <ident>-tg (▾), <ident>-v-<vue>."""
    boutons = ''.join('<i id="%s-v-%s"%s>%s</i>' % (ident, v, ' class="actif"' if v == actif else '', VUES[v])
                      for v in vues)
    droite = ('<span class="pager" id="%s-pager">%s</span><span class="cp-fl"><i>‹</i><i>›</i></span>'
              % (ident, e(pager))) if pager else ''
    return ('<div class="cp t23-cp"><span class="titre" id="%s-titre">%s</span>'
            '<div class="recherche t23-rech" id="%s-rech">%s%s<span class="ph">Rechercher…</span>'
            '<span class="deroule" id="%s-tg">▾</span></div>'
            '<span class="t23-cp-d">%s<span class="cp-vues">%s</span></span></div>'
            % (ident, e(titre), ident, icone('loupe', 'loupe'), ''.join(facettes), ident, droite, boutons))


BARRE_PIVOT = ('<div class="pv-barre t23-pvb"><span class="bt primaire">Mesures ▾</span><span class="bt gris">%s</span>'
               '<span class="bt gris">%s</span><span class="bt gris">%s</span></div>'
               % (INVERSER, DEPLIER, ICONES['telecharger']))


def table_pivot(ident, mesures, lignes):
    """Une vue croisée d'Odoo 18 (C/20, C/23) : une seule colonne « Total » repliée (case pleine), ses mesures, puis
    les lignes [(suffixe, niveau, signe, libellé, valeurs)] ; niveau 0 = « Total », signe 'moins' (déplié) ou 'plus'
    (replié). Identifiants : <ident>-r-<suffixe> (la ligne), <ident>-c-<suffixe>-<k> (la k-ième valeur)."""
    tete = ('<tr><td class="vide" rowspan="2"></td><th class="t23-ct" colspan="%d">%s<span>Total</span></th></tr>'
            '<tr>%s</tr>' % (len(mesures), PLUS, ''.join('<th class="m">%s</th>' % e(m) for m in mesures)))
    corps = ''.join(
        '<tr id="%s-r-%s"><td class="r t23-n%d">%s<span>%s</span></td>%s</tr>'
        % (ident, suf, niveau, MOINS if signe == 'moins' else PLUS, e(lib),
           ''.join('<td id="%s-c-%s-%d">%s</td>' % (ident, suf, k, v) for k, v in enumerate(vals)))
        for suf, niveau, signe, lib, vals in lignes)
    return '<table class="pv t23-pv" id="%s">%s%s</table>' % (ident, tete, corps)


def vue_odoo(ident, contenu, initiale=False):
    return '<div class="vue%s" id="%s">%s</div>' % (' initiale' if initiale else '', ident, contenu)


# -- 1. Personnes et tables, par jour (C/20)
MESURES_PT = ['Tables', 'Personnes', 'Ventes sans table', 'Articles', 'Total']
assert MESURES_PT == [_chaine(_POS_ORDER, c) for c in ('aite_tables', 'aite_personnes', 'aite_sans_table',
                                                       'aite_articles')] + ['Total']
JOUR_PIVOT = '14 oct. 2026'            # date_order par jour (format de C/20 : « 14 nov. 2026 »)
assert JOUR == '14/10/2026'


def valeurs_pt(t):
    tables, personnes, sans, articles, total = t
    return [str(tables), str(personnes), str(sans), qte(articles), odoo2(total)]


_TOT_PT = (TOTAL['tables'], TOTAL['personnes'], TOTAL['sans_table'], TOTAL['articles'], TOTAL['total'])
FAC_AUJ = lambda ident: facette(ident, 'filtre', FILTRES_PT[0])      # noqa: E731
V_PT = vue_odoo('t23-pt', panneau_cp('t23-pt', 'Personnes et tables', [FAC_AUJ('t23-pt-auj')], ['pivot', 'liste'],
                                     'pivot')
                + BARRE_PIVOT + table_pivot('t23-ptp', MESURES_PT, [
                    ('tot', 0, 'moins', 'Total', valeurs_pt(_TOT_PT)),
                    ('jour', 1, 'plus', JOUR_PIVOT, valeurs_pt(_TOT_PT))]), initiale=True)
# -- 2. regroupée par « Ouverte par »
V_PO = vue_odoo('t23-po', panneau_cp('t23-po', 'Personnes et tables',
                                     [FAC_AUJ('t23-po-auj'), facette('t23-po-ouv', 'groupe', GROUPES_PT[2])],
                                     ['pivot', 'liste'], 'pivot')
                + BARRE_PIVOT + table_pivot('t23-pop', MESURES_PT, [('tot', 0, 'moins', 'Total', valeurs_pt(_TOT_PT))] + [
                    (s.lower().replace('è', 'e').replace('ï', 'i'), 1, 'plus', s, valeurs_pt(PAR_SERVEUR[s]))
                    for s in SERVEURS]))
assert 'id="t23-pop-r-ines"' in V_PO and 'id="t23-pop-r-loic"' in V_PO


# -- 3. la liste (C/21) : la plus récente d'abord
def _cel(texte_, droite=False, ident=None):
    return '<span class="ell%s"%s>%s</span>' % (' d' if droite else '', ' id="%s"' % ident if ident else '', e(texte_))


COLS_LI = [('Date', '196px'), ('Table', '150px'), ('Personnes', '128px', 'd'), ('Articles', '112px', 'd'),
           ('Ouverte par', '1fr'), ('Encaissée par', '1fr'), ('Total', '176px', 'd')]
GAB_LI = '34px ' + ' '.join(c[1] for c in COLS_LI)
ICO_COLONNES = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round">'
                '<path d="M4 8h16M4 16h16"/><circle cx="15" cy="8" r="2.2" fill="#fff"/><circle cx="9" cy="16" r="2.2" '
                'fill="#fff"/></svg>')
_ORDRE_LI = sorted(ADDITIONS, key=lambda a: a['heure'], reverse=True)
LIGNES_LI = ''.join(
    '<div class="ligne" id="t23-li-%s" style="grid-template-columns:%s"><span class="cb"></span>%s</div>'
    % (a['table'].lower() + ('s' if a['heure'] > '19:00' and a['table'] == '10' else ''), GAB_LI, ''.join([
        _cel('%s %s' % (JOUR, a['heure'])),
        _cel('' if a['table'].endswith('B') else '%s, %s' % (demo.SALLE_RESTO, a['table'])),
        _cel(str(a['personnes']), True), _cel(qte(a['articles']), True), _cel(a['ouverte']), _cel(a['encaissee']),
        _cel(fcfa(a['total']), True)]))
    for a in _ORDRE_LI)
assert LIGNES_LI.count('class="ligne"') == 12 and 'id="t23-li-2b"' in LIGNES_LI
TETE_LI = ('<div class="tete" style="grid-template-columns:%s"><span class="cb"></span>%s<i class="t23-col">%s</i></div>'
           % (GAB_LI, ''.join('<span class="ell%s" id="t23-li-h%d">%s</span>' % (' d' if len(c) > 2 else '', k, e(c[0]))
                              for k, c in enumerate(COLS_LI, 1)), ICO_COLONNES))
PIED_LI = ('<div class="total" id="t23-li-tot" style="grid-template-columns:%s"><span></span><span></span><span></span>'
           '<span class="d" id="t23-li-tot-p">%s</span><span class="d">%s</span><span></span><span></span>'
           '<span class="d">%s</span></div>' % (GAB_LI, TOTAL['personnes'], qte(TOTAL['articles']), fcfa(TOTAL['total'])))
V_LI = vue_odoo('t23-li', panneau_cp('t23-li', 'Personnes et tables', [FAC_AUJ('t23-li-auj')], ['pivot', 'liste'],
                                     'liste', pager='1-%d / %d' % (len(ADDITIONS), len(ADDITIONS)))
                + '<div class="liste t23-liste">%s%s%s</div>' % (TETE_LI, LIGNES_LI, PIED_LI))

# -- 4. l'analyse AITE : favori « Ventes par famille », puis la session du jour (C/23)
V_FA = vue_odoo('t23-fa', panneau_cp('t23-fa', 'Analyse POS — Marge & CMV',
                                     [facette('t23-fa-fav', 'favori', 'Ventes par famille'),
                                      facette('t23-fa-ses', 'champ', SESSION, titre='Session')],
                                     ['pivot', 'graphe', 'liste'], 'pivot')
                + BARRE_PIVOT + table_pivot('t23-fap', COLONNES_A, [
                    (lib.split(' / ')[-1][:3].lower(),
                     niveau, 'moins' if niveau < 2 else 'plus', lib,
                     [odoo2(g[0]), odoo2(g[1]), odoo2(g[2]), odoo2(g[3])])
                    for lib, niveau, g in FAMILLES_A]))
for _suf in ('tot', 'nou', 'piz', 'boi', 'alc', 'non'):   # le début du dernier nom de la ligne
    assert 'id="t23-fap-r-%s"' % _suf in V_FA, _suf


# -- les panneaux de recherche
def entree(ident, texte_, coche=False, accordeon=False, poubelle=False):
    return ('<div class="t23-it%s%s"%s><span>%s</span>%s</div>'
            % (' coche' if coche else '', ' acc' if accordeon else '', ' id="%s"' % ident if ident else '', e(texte_),
               '<i class="t23-car">▾</i>' if accordeon else ('<i class="t23-pb">%s</i>' % POUBELLE if poubelle else '')))


HR = '<hr>'


def panneau(ident, filtres, groupes, favoris):
    """Le panneau de recherche d'Odoo 18 (search_bar_menu.xml) : trois colonnes, ouvert sous la barre et aligné sur
    son bord droit (position « bottom-end ») ; masqué, le geste ``montrer`` l'ouvre."""
    col = lambda titre_, ico, cls, corps: ('<div class="t23-col-p"><div class="t23-pt"><i class="%s">%s</i>%s</div>%s'
                                          '</div>' % (cls, ico, e(titre_), corps))  # noqa: E731
    return superpose('<div class="t23-pan masque" id="%s">%s%s%s</div>' % (
        ident, col('Filtres', icone('filtre'), 't23-i-f', filtres), col('Regrouper par', GROUPE, 't23-i-g', groupes),
        col('Favoris', ETOILE, 't23-i-s', favoris)))


AJ_FILTRE = entree(None, 'Ajouter un filtre personnalisé')
AJ_GROUPE = entree(None, 'Ajouter un groupe personnalisé', accordeon=True)
ENREGISTRER = entree(None, 'Enregistrer la recherche actuelle', accordeon=True)
PAN_PT = panneau('t23-pp',
                 '<div id="t23-pp-per">%s</div>' % ''.join(
                     entree('t23-pp-f%d' % k, f, coche=(k == 0), accordeon=(f == 'Période'))
                     for k, f in enumerate(FILTRES_PT)) + HR + AJ_FILTRE,
                 ''.join(entree('t23-pp-g%d' % k, g, accordeon=(g == 'Jour')) for k, g in enumerate(GROUPES_PT))
                 + HR + AJ_GROUPE, ENREGISTRER)
PAN_A = panneau('t23-pa', entree(None, 'Date', accordeon=True) + HR + AJ_FILTRE,
                ''.join(entree(None, g, accordeon=g in ('Jour', 'Semaine', 'Mois')) for g in GROUPES_A) + HR + AJ_GROUPE,
                entree('t23-pa-fav', 'Ventes par famille', coche=True, poubelle=True) + HR + ENREGISTRER)
PAN_AN = panneau('t23-pn',
                 ''.join(entree(None, f, coche=(k == 0), accordeon=(f == 'Période')) for k, f in enumerate(FILTRES_AN[:5]))
                 + HR + entree(None, FILTRES_AN[5]) + HR + AJ_FILTRE,
                 ''.join(entree('t23-pn-g%d' % k, g, accordeon=(g == 'Jour')) for k, g in enumerate(GROUPES_AN))
                 + HR + AJ_GROUPE, ENREGISTRER)

# -- le menu « Analyse » du Point de Vente, déroulé (comme t12)
DD = superpose('<div class="t23-dd masque" id="t23-dd">%s<div class="t23-dd-h">Analyse AITE</div>%s</div>' % (
    ''.join('<div%s>%s</div>' % (' id="t23-dd-pt"' if m == 'Personnes et tables' else '', e(m))
            for m in MENU_ANALYSE_RESTO),
    ''.join('<div class="t23-dd-g"%s>%s</div>' % (' id="t23-dd-tcg"' if m == 'Tableau croisé & graphique' else '', e(m))
            for m in MENU_ANALYSE_AITE)))

GESTION = fenetre_muk('t23-ges', 'Point de Vente', MENUS_MUK['point_de_vente'], [V_PT, V_PO, V_LI, V_FA],
                      societe=demo.SOCIETE_RESTO, initiale=P_EDWIGE[0], avatar=demo.AVATARS_RESTO[P_EDWIGE],
                      calques=DD + PAN_PT + PAN_A, apps=APPS_PROFIL['resto_manager'], app_active='Point de Vente')
GESTION = GESTION.replace('<span class="menu">Analyse</span>', '<span class="menu" id="t23-m-analyse">Analyse</span>', 1)
assert 'id="t23-m-analyse"' in GESTION and 'id="t23-ges-app-point-de-vente"' in GESTION


# -- 5. le compte du chef de salle : Restaurant › Annulations (C/22), puis regroupées par motif
COLS_AN = list(zip(COLONNES_AN, ['176px', '64px', '200px', '104px', '146px', '150px', '146px', '128px', '1fr'],
                   ['', '', '', 'd', 'd', '', '', '', '']))
GAB_AN = '34px ' + ' '.join(c[1] for c in COLS_AN)
def tete_an(ident):
    return ('<div class="tete" style="grid-template-columns:%s"><span class="cb"></span>%s<i class="t23-col">%s</i>'
            '</div>' % (GAB_AN, ''.join('<span class="ell%s" id="%s-h%d">%s</span>' % (' d' if c[2] else '', ident, k,
                                                                                      e(c[0]))
                                        for k, c in enumerate(COLS_AN, 1)), ICO_COLONNES))
LIGNES_AN = ''.join(
    '<div class="ligne%s" id="t23-an-%d" style="grid-template-columns:%s"><span class="cb"></span>%s</div>'
    % ('' if autorisee else ' t23-rouge', k, GAB_AN, ''.join([
        _cel(date), _cel(table), _cel(produit), _cel(qte(q), True), _cel(fcfa(q * PRIX[produit]), True), _cel(dem),
        _cel(autorisee), _cel(motif), _cel(precision)]))
    for k, (date, table, produit, q, dem, autorisee, motif, precision) in enumerate(ANNULATIONS, 1))
PIED_AN = ('<div class="total" style="grid-template-columns:%s"><span></span>%s<span class="d">%s</span>'
           '<span class="d">%s</span>%s</div>' % (GAB_AN, '<span></span>' * 3, qte(QTE_AN), fcfa(MONTANT_AN),
                                                   '<span></span>' * 4))
GROUPES_HTML = ''.join(
    '<div class="ligne t23-grp" id="t23-ag-%d" style="grid-template-columns:%s"><span class="t23-grp-n">'
    '<i class="t23-car-g">%s</i>%s (%d)</span><span class="d">%s</span><span class="d">%s</span>%s</div>'
    % (k, GAB_AN, FLECHE_GROUPE, e(m), n, qte(q), fcfa(montant), '<span></span>' * 4)
    for k, (m, n, q, montant) in enumerate(MOTIFS_AN, 1))
V_AN = vue_odoo('t23-an', panneau_cp('t23-an', 'Annulations', [facette('t23-an-auj', 'filtre', FILTRES_AN[0])],
                                     ['liste', 'pivot', 'graphe'], 'liste',
                                     pager='1-%d / %d' % (len(ANNULATIONS), len(ANNULATIONS)))
                + '<div class="liste t23-liste">%s%s%s</div>' % (tete_an('t23-an'), LIGNES_AN, PIED_AN), initiale=True)
V_AM = vue_odoo('t23-am', panneau_cp('t23-am', 'Annulations', [facette('t23-am-auj', 'filtre', FILTRES_AN[0]),
                                                                facette('t23-am-mot', 'groupe', GROUPES_AN[0])],
                                     ['liste', 'pivot', 'graphe'], 'liste',
                                     pager='1-%d / %d' % (len(MOTIFS_AN), len(MOTIFS_AN)))
                + '<div class="liste t23-liste">%s%s%s</div>' % (tete_an('t23-am'), GROUPES_HTML, PIED_AN))
LECTURE = fenetre_muk('t23-lec', 'Restaurant', MENUS_MUK['restaurant'], [V_AN, V_AM], actif=None,
                      societe=demo.SOCIETE_RESTO, initiale=P_LANDRY[0], avatar=demo.AVATARS_RESTO[P_LANDRY],
                      calques=PAN_AN, apps=APPS_PROFIL['resto_chef'], app_active='Restaurant')
LECTURE = LECTURE.replace('class="app muk"', 'class="app muk masque"', 1)
LECTURE = LECTURE.replace('<span class="menu">Annulations</span>', '<span class="menu" id="t23-lec-menu">Annulations</span>', 1)
assert 'Point de Vente' not in APPS_PROFIL['resto_chef'] and 'Paramètres' not in APPS_PROFIL['resto_chef']
assert 'id="t23-lec-apps"' in LECTURE and 'id="t23-lec-menu"' in LECTURE and 'id="t23-an-h8"' in LECTURE and 'id="t23-an-7"' in LECTURE and ' t23-rouge' in LECTURE

APP = 't23-ges'
ECRAN = navigateur(GESTION + LECTURE)

CSS = ("/* -- la pastille : Edwige (le personnage), puis Landry à l'étape 5 -- */\n"
       + css_personnage('#tu-perso.t23-landry', LANDRY, ROLE_LANDRY, P_LANDRY[0]) + """
/* -- le panneau de contrôle des vues (C/20 à C/23) : titre, recherche au milieu, pagination et vues à droite -- */
.t23-cp { display: grid; grid-template-columns: 1fr 720px 1fr; gap: 16px; }
.t23-cp .titre { font-size: 24px; overflow: hidden; text-overflow: ellipsis; }
.t23-rech { margin-left: 0; width: 720px; position: relative; display: flex; align-items: center; gap: 8px;
  padding: 0 52px 0 12px; overflow: hidden; }
.t23-rech .ph { white-space: nowrap; overflow: hidden; }
.t23-cp-d { display: flex; align-items: center; justify-content: flex-end; gap: 10px; }
.t23-cp-d .pager { margin-left: 0; }
.t23-cp .cp-vues { margin-left: 4px; }
/* les facettes : étiquette colorée (filtre, regroupement : couleur principale ; favori : jaune ; champ : son nom) */
.t23-fac { flex: none; max-width: none; }
.t23-fac .fic svg { width: 16px; height: 16px; }
.t23-fac-groupe .fic { color: #fff; }
.t23-fac-favori .fic { background: #F3CC00; color: #212529; }
.t23-fac-champ .fic { width: auto; padding: 0 8px; color: #fff; }
.t23-fac-champ .fic small { font-size: 15px; }
.t23-fac .fx { padding-left: 2px; }
/* -- la vue croisée (C/20, C/23) -- */
.t23-pvb .bt { padding: 0 14px; }
.t23-pvb .bt svg { width: 20px; height: 20px; }
.t23-pv { margin: 8px 24px; }
.t23-pv th, .t23-pv td { height: 48px; padding: 0 12px; }
.t23-pv td.vide { border: 0; }
.t23-pv th.t23-ct { text-align: left; font-weight: 400; }
.t23-pv th.m { text-align: center; }
.t23-pv td.r { background: #fff; text-align: left; }
.t23-pv td.r, .t23-pv th.t23-ct { white-space: nowrap; }
.t23-pv td.r > *, .t23-pv th.t23-ct > * { vertical-align: middle; }
.t23-pv .t23-pm { width: 17px; height: 17px; margin-right: 8px; }
.t23-pv td.t23-n1 { padding-left: 50px; }
.t23-pv td.t23-n2 { padding-left: 86px; }
/* -- les listes (C/21, C/22) : 12 lignes tiennent sous le panneau de contrôle -- */
.t23-liste .tete { position: relative; height: 48px; font-size: 18px; column-gap: 12px; padding: 0 44px 0 6px; }
.t23-liste .ligne { height: 47px; font-size: 18px; column-gap: 12px; padding: 0 44px 0 6px; }
.t23-liste .total { height: 48px; font-size: 18px; column-gap: 12px; padding: 0 44px 0 6px; }
.t23-liste .cb { margin-left: 8px; }
.t23-liste .ligne.survol { background: #E3ECF2; }
.t23-liste .ligne.t23-rouge { color: #DC3545; }
.t23-col { position: absolute; right: 12px; top: 12px; width: 24px; height: 24px; display: inline-flex; color: #343A40; }
.t23-col svg { width: 24px; height: 24px; }
/* une ligne de groupe (o_group_header) : le nom et le compte, puis les sommes de ses colonnes */
.t23-liste .t23-grp { background: #F1F3F5; font-weight: 600; }
.t23-grp-n { grid-column: 1 / span 4; display: flex; align-items: center; gap: 8px; padding-left: 8px; }
.t23-car-g { width: 16px; height: 16px; display: inline-flex; color: #495057; }
.t23-car-g svg { width: 16px; height: 16px; }
/* -- le menu « Analyse » déroulé (navbar.xml : section « Analyse AITE », entrées décalées) -- */
.t23-dd { position: absolute; left: 676px; top: 56px; width: 340px; padding: 6px 0; background: #fff;
  border: 1px solid var(--o-filet); border-radius: 6px; box-shadow: 0 14px 34px rgba(0,0,0,.22); z-index: 29; }
.t23-dd div { height: 42px; display: flex; align-items: center; padding: 0 20px; font-size: 19px; color: var(--o-texte);
  white-space: nowrap; }
.t23-dd div.t23-dd-h { height: 34px; margin-top: 4px; padding-top: 6px; font-size: 16px; font-weight: 700; color: #5C636A; }
.t23-dd div.t23-dd-g { padding-left: 32px; }
/* -- le panneau de recherche (search_bar_menu.xml), aligné sur le bord droit de la barre (bottom-end) -- */
.t23-pan { position: absolute; top: 130px; right: 412px; z-index: 30; background: #fff; border: 1px solid rgba(0,0,0,.15);
  border-radius: 4px; box-shadow: 0 10px 28px rgba(0,0,0,.18); padding: 14px 0; display: grid;
  grid-template-columns: repeat(3, minmax(250px, max-content)); color: var(--o-texte); font-size: 18px; }
.t23-col-p { padding: 0 14px; border-right: 1px solid #DEE2E6; }
.t23-col-p:last-child { border-right: 0; }
.t23-pt { height: 38px; display: flex; align-items: center; gap: 9px; font-size: 20px; font-weight: 600; margin-bottom: 4px;
  padding-left: 10px; }
.t23-pt i { width: 20px; height: 20px; display: inline-flex; }
.t23-pt i svg { width: 20px; height: 20px; }
.t23-i-f svg path { fill: var(--muk-prim); }
.t23-i-g { color: var(--muk-prim); }
.t23-i-s { color: #F3CC00; }
.t23-it { height: 36px; display: flex; align-items: center; padding-left: 32px; padding-right: 6px; white-space: nowrap;
  position: relative; }
.t23-it.coche { font-weight: 700; }
.t23-it.coche::before { content: '✓'; position: absolute; left: 10px; font-size: 16px; color: var(--o-lien); }
.t23-it i { margin-left: auto; padding-left: 14px; font-style: normal; display: inline-flex; color: #495057; }
.t23-it .t23-car { font-size: 15px; }
.t23-it .t23-pb svg { width: 18px; height: 18px; }
.t23-pan hr { border: 0; border-top: 1px solid #DEE2E6; margin: 6px 0 6px 12px; }
""")

TUTORIEL = {
    'slug': 't23-restaurant-rapports',
    'profil': 't23_restaurant_rapports',
    'numero': 23,
    'titre': 'Les rapports du restaurant',
    'fonction': 'Rapports du restaurant',
    'personnage': (EDWIGE, ROLE_EDWIGE),
    'accroche': {
        'kicker': 'Après le service',
        # Les douleurs : docs/PERIMETRE_FONCTIONNEL_RESTAURANT.md:536 (REST-25 : AITE HOUSE compte des additions, pas des
        # tables ni des personnes ; le total des personnes n'est pas affiché ; une table divisée compte pour deux ; le
        # classement par responsable suit le compte Odoo), :493 (REST-22 : « Détails des ventes » sans rubrique
        # d'annulations), :507 (REST-23 : le regroupement ne montre que les familles finales).
        'question': 'Combien de *personnes* avez-vous servies ?',
        'douleurs': [('graphe', 'Le rapport compte des additions, pas des tables'),
                     ('personne', 'Le total des personnes servies, nulle part'),
                     ('echange', 'Une table divisée comptée deux fois'),
                     ('cle', 'Tout passe sous le compte de la caisse : qui a servi ?'),
                     ('liste', 'Les boissons ? Aucun sous-total par niveau'),
                     ('corbeille', 'Les annulations absentes des rapports')],
        'voix': "Combien de personnes avez-vous servies aujourd'hui ? Quand le rapport compte des additions, une table "
                "divisée compte deux fois, et les annulations n'y figurent pas.",
    },
    'revelation': {
        # R/views/pos_order_views.xml:46-143 ; A/views/pos_analytics_report_views.xml:134-152 ;
        # R/views/restaurant_annulation_views.xml:10-112 ; périodes : pos_order_views.xml:87-115.
        'promesse': 'Tables et personnes, chiffre de chaque serveur, ventes par famille, annulations : les chiffres '
                    'du jour, ou de la période choisie, sans rien recompter.',
        'voix': "Avec Aïte haousse, la manager lit ses tables, ses personnes, ses familles et ses annulations, sur la "
                "période qu'elle choisit.",
    },
    'temps': ['Personnes et tables', 'Par serveur', 'Par famille', 'Annulations'],
    'app': APP,
    'ecran': ECRAN,
    'css': CSS,
    'vues_initiales': {'odoo': 't23-pt', 'lecture': 't23-an'},
    'bulles': {
        # R/views/pos_order_views.xml:42-43, :132 ; rec R94.
        'b-reglees': 'Les tables encore ouvertes et les tables annulées ne comptent pas.',
        # R/models/pos_order.py:82-94 (aides des champs), :241-244.
        'b-figee': '« Ouverte par » ne change plus ; « Encaissée par » est écrite au paiement.',
        # R/models/regles.py:169-185 ; R/models/pos_order.py:112-121 ; S/overrides/split_bill_screen.js:9-11, 44-56 ;
        # la part n'a pas de table : O/pos_restaurant/…/split_bill_screen.js:101-109 ; rec R93.
        'b-part': 'La part 2B, sans table : 0 personne. La table 2 garde ses 2 personnes.',
        # O/web/static/src/search/search_model.js:927-928 ; A/views/pos_analytics_report_views.xml:76.
        'b-session': 'Le favori remplace la recherche : la session du jour s\'ajoute ensuite.',
        # R/views/restaurant_annulation_views.xml:15 ; R/models/restaurant_annulation.py:9-13 ; N l.124-125.
        'b-sans-code': 'En rouge : un retrait passé sans code ni motif. Jamais refusé, toujours tracé.',
    },
    'reactions': {
        'r-page': 'Je n\'ai plus rien à recompter.',
    },
    'etapes': [
        {'temps': 0, 'titre': 'Personnes et tables, aujourd\'hui d\'office',
         'texte': 'Point de Vente › Analyse › Personnes et tables : tables, personnes, ventes sans table, articles et '
                  'total, sur une page.',
         'voix': "Le soir, Edwige, la manager, ouvre Point de Vente, Analyse, Personnes et tables. Aujourd'hui "
                 "d'office : onze tables, trente-trois personnes, et cent quatre-vingt-huit mille cinq cents francs CFA. "
                 "Seules les additions encaissées y entrent.",
         'gestes': [pause(0.9), curseur('#t23-ges-app-point-de-vente', fx=0.6, d=0.6),
                    anneau('#t23-ges-app-point-de-vente', d=0.9),
                    clic('#t23-m-analyse', d=0.6), montrer('#t23-dd', d=0.2, y=-6), pause(0.4),
                    clic('#t23-dd-pt', fx=0.4, d=0.5), cacher('#t23-dd', d=0.15), pause(0.2),
                    anneau('#t23-pt-auj', d=1.0), zoom('#t23-ptp', s=1.55, d=0.8, fx=0.5, fy=0.4),
                    anneau('#t23-ptp-c-tot-0', d=1.1), anneau('#t23-ptp-c-tot-1', d=1.1), anneau('#t23-ptp-c-tot-4', d=1.3),
                    bulle('b-reglees', '#t23-ptp', cote='bas', d=2.6), pause(1.5), dezoom(d=0.6)]},
        {'temps': 1, 'titre': 'La période, et chaque serveur',
         'texte': 'Aujourd\'hui, cette semaine, ce mois, cette année ou une période libre ; regrouper par « Ouverte par » '
                  'ou « Encaissée par ».',
         'voix': "La période se change au même endroit : cette semaine, ce mois, ou une période libre. Regroupée par "
                 "Ouverte par, la journée se lit serveur par serveur : Inès, cinq tables et quatorze personnes ; Loïc, "
                 "six tables et dix-neuf personnes.",
         'gestes': [clic('#t23-pt-tg', d=0.7), montrer('#t23-pp', d=0.2, y=-6), pause(0.3),
                    anneau('#t23-pp-per', d=2.4), pause(0.4),
                    clic('#t23-pp-g2', fx=0.3, d=0.6), classe('#t23-pp-g2', ajouter=['coche']), vue('t23-po'),
                    pause(0.4), clic('#t23-po-tg', d=0.5), cacher('#t23-pp', d=0.15), pause(0.2),
                    anneau('#t23-pop-r-ines', d=1.5), pause(0.7), anneau('#t23-pop-r-loic', d=1.5),
                    bulle('b-figee', '#t23-pop', cote='droite', d=2.4), pause(1.6)]},
        {'temps': 1, 'titre': 'Chaque addition, en liste',
         'texte': 'En liste : la table, les personnes, qui a ouvert, qui a encaissé. La part 2B, sans table, compte '
                  '0 personne.',
         'voix': "Edwige retire le regroupement et passe en liste : chaque addition encaissée, sa table, ses personnes, "
                 "qui l'a ouverte, qui l'a encaissée. La part deux B n'a ni table ni personne : la table deux ne compte "
                 "qu'une fois. En bas, les sommes du jour.",
         'gestes': [clic('#t23-po-ouv-x', d=0.6), vue('t23-pt'), pause(0.1), clic('#t23-pt-v-liste', d=0.6),
                    vue('t23-li'), pause(1.5), anneau('#t23-li-h5', d=1.0), anneau('#t23-li-h6', d=1.0),
                    curseur('#t23-li-2b', fx=0.25, d=0.5), survol('#t23-li-2b'), anneau('#t23-li-2b', d=1.4),
                    bulle('b-part', '#t23-li-2b', cote='haut', d=2.6), pause(1.6), anneau('#t23-li-tot-p', d=1.2)]},
        {'temps': 2, 'titre': 'Les ventes par famille',
         'texte': 'Analyse › Analyse AITE › Tableau croisé & graphique : favori « Ventes par famille », puis la session '
                  'du jour.',
         'voix': "Dans l'analyse Aïte, le favori Ventes par famille, sur la session du jour, range le chiffre par "
                 "famille, puis par sous-famille. Les boissons : quarante-huit mille cinq cents "
                 "francs, dont trente-six mille cinq cents d'alcoolisé, avec leur coût et leur marge.",
         'gestes': [vue('t23-fa'), clic('#t23-fa-tg', d=0.6), montrer('#t23-pa', d=0.2, y=-6),
                    anneau('#t23-pa-fav', d=1.4), pause(0.2), clic('#t23-fa-tg', d=0.5), cacher('#t23-pa', d=0.15),
                    anneau('#t23-fap-r-piz', d=0.9),
                    bulle('b-session', '#t23-fa-ses', cote='bas', d=1.9), pause(1.2),
                    anneau('#t23-fap-r-boi', d=1.4), pause(0.4), anneau('#t23-fap-r-alc', d=1.4), pause(0.4),
                    anneau('#t23-fap-c-alc-1', d=0.8), anneau('#t23-fap-c-alc-2', d=0.8),
                    reaction('r-page', d=2.0), pause(0.8)]},
        {'temps': 3, 'titre': 'Les annulations, en lecture seule',
         'texte': 'Le chef de salle, profil « Restaurant : lecture des rapports » : Restaurant › Annulations, sans la '
                  'caisse.',
         'voix': "Landry, le chef de salle, n'a que la lecture des rapports : ni caisse, ni configuration. Dans "
                 "Restaurant, Annulations, il relit les sept du jour : qui a demandé, qui a autorisé, pourquoi ; en "
                 "rouge, le retrait passé sans code. Regroupées par motif, avec leurs sommes : cinq clients partis, "
                 "pour seize mille francs.",
         'gestes': [montrer('#t23-lec', d=0.5, y=0), classe('#tu-perso', ajouter=['t23-landry'], avec=True),
                    pause(2.4), anneau('#t23-lec-apps', d=1.6), pause(0.4), anneau('#t23-lec-menu', d=1.0), pause(0.5),
                    anneau('#t23-an-pager', d=0.8), anneau('#t23-an-h6', d=0.6), anneau('#t23-an-h7', d=0.6),
                    anneau('#t23-an-h8', d=0.6), curseur('#t23-an-7', fx=0.3, d=0.45),
                    bulle('b-sans-code', '#t23-an-7', cote='bas', d=1.8), pause(0.7),
                    # « Regroupées par motif » : le panneau s'ouvre au début de la phrase et se referme avant
                    # « cinq clients partis », dit pendant l'anneau sur « Client parti (5) ».
                    clic('#t23-an-tg', d=0.35, puis=0.05), montrer('#t23-pn', d=0.2, y=-6, puis=0),
                    clic('#t23-pn-g0', fx=0.3, d=0.35, puis=0), classe('#t23-pn-g0', ajouter=['coche'], puis=0),
                    vue('t23-am', 'lecture', puis=0), clic('#t23-am-tg', d=0.3, puis=0),
                    cacher('#t23-pn', d=0.15), anneau('#t23-ag-2', d=1.8), pause(1.0)]},
    ],
    'resultats': {
        'titre': 'Les chiffres du soir, sans rien recompter',
        'cartes': [
            # R/views/pos_order_views.xml:53-57 ; rec R91 (« sur la même page »).
            {'valeur': '5', 'compter': 5, 'unite': 'mesures', 'icone': 'personne',
             'texte': 'sur une page : tables, personnes, ventes sans table, articles et total'},
            # A/models/pos_analytics_report.py:69-87 ; N l.173-176.
            {'valeur': '3', 'compter': 3, 'unite': 'niveaux', 'icone': 'piles',
             'texte': 'de familles : famille, sous-famille, sous-sous-famille'},
            # A/views/pos_analytics_report_views.xml:134-141 ; N l.177-180.
            # Les deux touches montrées à l'étape 4 : ▾ de la recherche (le panneau, colonne « Favoris »), puis le favori.
            {'valeur': '2', 'compter': 2, 'unite': 'touches', 'icone': 'etoile',
             'texte': 'pour les ventes par famille : le panneau de recherche, puis « Ventes par famille »'},
        ],
        'voix': "Cinq mesures sur une page, trois niveaux de familles, deux touches pour les ventes par famille.",
    },
    'cta': {
        'appel': 'Demandez votre démonstration',
        'sous_marque': demo.SOUS_MARQUE_RESTO,
        # t23 ferme la série du restaurant : on revient à la mise en place (t16), comme t15 renvoie à la présentation.
        'suivant': 'Service à table contrôlé : la mise en place',
        'voix': "Aïte haousse, par Aïte Consulting. Demandez votre démonstration, et revoyez la série du restaurant "
                "depuis la mise en place.",
    },
    # La vue croisée « Personnes et tables », zoom posé sur les totaux (C/20).
    'vignette': {'etape': 1, 'apres': 9.0},
}

# Les nombres dits par la voix : ceux que l'écran montre (calculés plus haut).
_V = [_e['voix'] for _e in TUTORIEL['etapes']]
for _n, _dit, _vrai in ((0, 'onze tables', TOTAL['tables'] == 11), (0, 'trente-trois personnes', TOTAL['personnes'] == 33),
                        (0, 'cent quatre-vingt-huit mille cinq cents', TOTAL['total'] == 188500),
                        (1, 'Inès, cinq tables et quatorze personnes', PAR_SERVEUR[P_INES][:2] == (5, 14)),
                        (1, 'Loïc, six tables et dix-neuf personnes', PAR_SERVEUR[P_LOIC][:2] == (6, 19)),
                        (2, 'La part deux B', _PAR[('2B', '14:11')]['tables'] == 0),
                        (3, 'quarante-huit mille cinq cents', FAM_BOISSON[0] == 48500),
                        (3, 'trente-six mille cinq cents', FAM_ALCOOL[0] == 36500),
                        (4, 'les sept du jour', len(ANNULATIONS) == 7),
                        (4, 'cinq clients partis, pour seize mille', MOTIFS_AN[1][1:4:2] == (5, 16000))):
    assert _dit in _V[_n] and _vrai, ('t23 : voix et écran ne disent plus la même chose', _n + 1, _dit)
assert len(MESURES_PT) == 5 and len(_GROUPES_A[2:5]) == 3 and _GROUPES_A[2:5] == ['Famille', 'Sous-famille',
                                                                                   'Sous-sous-famille']


def _typo(texte_):
    """Les textes à l'écran écrits ici (pas la voix) : une espace insécable dans les guillemets et avant « : »,
    « ; », « ? », pour qu'un signe ne passe pas seul à la ligne (comme S/utils/messages.js:7-9 ; t17, t19)."""
    for avant, apres in (('« ', '« '), (' »', ' »'), (' :', ' :'), (' ;', ' ;'), (' ?', ' ?')):
        texte_ = texte_.replace(avant, apres)
    return texte_


for _etape in TUTORIEL['etapes']:
    _etape['titre'], _etape['texte'] = _typo(_etape['titre']), _typo(_etape['texte'])
for _groupe in ('bulles', 'reactions'):
    TUTORIEL[_groupe] = {_k: _typo(_v) for _k, _v in TUTORIEL[_groupe].items()}
for _carte in TUTORIEL['resultats']['cartes']:
    _carte['texte'] = _typo(_carte['texte'])
TUTORIEL['revelation']['promesse'] = _typo(TUTORIEL['revelation']['promesse'])
TUTORIEL['accroche']['question'] = _typo(TUTORIEL['accroche']['question'])
TUTORIEL['accroche']['douleurs'] = [(_i, _typo(_t)) for _i, _t in TUTORIEL['accroche']['douleurs']]
