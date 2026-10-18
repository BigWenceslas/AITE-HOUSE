# -*- coding: utf-8 -*-
"""Tutoriel 5 — Taxe de séjour : elle se calcule toute seule.

Personnage : la directrice (demo.POSTES['conformite']), profil Responsable
(aite_hotel_management.group_hotel_manager) : c'est elle qui règle l'hôtel,
tient les barèmes et ouvre l'état mensuel, réservés à ce groupe
(aite_city_tax/views/menus.xml:5-10 ; security/ir.model.access.csv).
Applications de la barre MuK : ecrans.APPS_PROFIL['direction'] ; menus de
l'application Hôtel relevés pour le compte demo.direction sur la base MuK
(load_menus) : Direction, Front Desk, Réservations, Espaces & Prestations,
Notes de chambre en attente, Facturation, Fidélité, Gouvernante,
Configuration.

Accroche (douleurs) — docs/etude_comparative/benchmark_afrique_odoo.md :
- :10 « Aucun PMS international ne gère nativement la taxe de séjour
  d'Afrique francophone : partout il faut ajouter une ligne/taxe
  configurable » (carte « Ailleurs, une ligne à ajouter soi-même ») ;
- :12 et :65 barème par nuitée selon les étoiles (5 000 / 4 000 / 3 000 /
  1 000 / 500 F), déclaration mensuelle DGI (formulaire I/PL-TVA-IR),
  échéance le 15 ; ligne « nuitée × personnes selon catégorie, exclue de la
  base TVA » (cartes étoiles, nuits × personnes, nuitées du mois, DGI) ;
- :68 facture : « TVA 19,25 % incluse + taxe de séjour distincte » (carte
  « La taxe à garder hors de la TVA »).

Écrans et libellés (relevés mot pour mot) :
1. Fiche hôtel — aite_hotel_management/views/hotel_hotel_views.xml:22-83
   (Identité, Code, Catégorie, Horaires standards, Coordonnées, Structure,
   Chambres vendables, onglet « Politique / informations » et son texte
   indicatif) ; models/hotel_hotel.py:20-79 (libellés, « 3 ★ ») ; onglet
   ajouté par aite_city_tax/views/hotel_hotel_views.xml:11-41 (« Taxe de
   séjour », « Réglage », « Pays (fiche hôtel) », « Catégorie (fiche
   hôtel) », « Ce qui s'applique », bandeau alert-info, texte gris) ;
   models/hotel_hotel.py:13-34 (« Collecter la taxe de séjour », « Barème
   appliqué », « Montant par nuitée », « Base ») et :73-77 (la phrase
   « Chaque séjour portera une ligne « Taxe de séjour » de 3 000 XAF par
   personne et par nuit, hors TVA. ») ; models/city_tax_rate.py:18-20,
   :71-80 (libellé du barème, stocké : « Cameroon — 3 ★ : 3 000 XAF »,
   voir ÉCARTS).
2. Barèmes — aite_city_tax/views/city_tax_rate_views.xml:4-56 (liste
   éditable, colonnes, regroupement par pays par défaut) ;
   models/city_tax_rate.py:21-58 (Pays, Catégorie, Montant par nuitée,
   Devise, Base de calcul, Compter les enfants, Référence légale) ;
   data/city_tax_data.xml:5-59 (barème Cameroun, références légales) et
   :3-215 (24 barèmes : 4 pays × 6 catégories) ; menu menus.xml:13-17.
   Sommes des lignes de regroupement (14 000, 9 000, 60 000, 6 000) d'après
   ref_muk/046 et captures/05_baremes.png.
3. Réservation — aite_hotel_management/views/hotel_reservation_views.xml:
   40-157 (Confirmer, Annuler, Check-in, Encaisser un acompte, Envoyer la
   confirmation, No-show, statusbar, bouton « Folio », groupes Client /
   Séjour / Canal & commission / Occupation, onglets Chambres / Demandes
   particulières) ; models/hotel_reservation.py:48-145 (libellés, états,
   « Téléphone / WhatsApp ») ; aite_guest_registry/views/
   hotel_reservation_views.xml:11-47 (« Fiches clients », « Fiches
   d'enregistrement »). Confirmer crée le folio puis la taxe :
   hotel_reservation.py:319-333 ; aite_city_tax/models/hotel_folio.py:76-80.
4. Folio — aite_hotel_management/views/hotel_folio_views.xml:31-128
   (Encaisser, Générer la facture, Annuler, Ouvert / Facturé / Soldé,
   Règlements, Séjour, Montants, Lignes du folio, colonnes, note grise) ;
   models/hotel_folio.py:28-114, :249-265 (libellé de la nuitée, dates
   ISO), :395-436 ; aite_city_tax/views/hotel_folio_views.xml:10-45
   (« Taxe de séjour » dans Montants, « Recalculer la taxe de séjour »,
   ligne orange) ; models/hotel_folio.py:9-12, :37-41, :100-144 (une seule
   ligne, quantité, prix, aucune TVA, libellé « Taxe de séjour — 4
   nuitée(s) × personne (3 ★, Cameroun) »). TVA de la nuitée : taxe de
   vente « 19.25% » du plan comptable camerounais d'Odoo
   (odoo18/addons/l10n_cm/data/template/account.tax-cm.csv:2), posée sur
   l'article du type de chambre — un réglage de l'établissement, pas du
   module ; le module garantit seulement que la ligne de taxe n'a aucune
   TVA. Aspect : captures/03_folio.png, ref_muk/029. Discussion sous la
   feuille (le folio hérite de mail.thread, hotel_folio.py:24 ; Odoo 18 la
   place sous la fiche à cette largeur d'écran) : « Envoyer message »,
   « Note », « Activités », « Suivre », message de création « %s créé »
   (odoo18/addons/mail/i18n/fr.po).
5. Le séjour change — hotel_reservation.py:264-273 (dates modifiées sur une
   réservation confirmée → resynchronisation des nuitées puis de la taxe) ;
   tests/vague1/scenario_city_tax.py:103-109 (une nuit de plus : 6
   nuitées, 18 000 F, toujours une seule ligne) ; gel après facture :
   aite_city_tax/models/hotel_folio.py:111-113, scenario_city_tax.py:131-135.
6. État mensuel — aite_city_tax/views/city_tax_report_views.xml:5-96
   (pivot mois × hôtel, « Nuitées taxées », « Taxe collectée », filtres
   « Départs du mois », « Départs du mois dernier », « Séjours terminés (à
   déclarer) », « Séjours en cours (prévision) », regroupements « Mois » /
   « Hôtel », aide « … le montant à déclarer et à reverser avant le 15 ») ;
   models/city_tax_report.py:6-87 (mois du départ « AAAA-MM ») ; menu
   menus.xml:5-10. Cadre web d'Odoo 18 (odoo18/addons/web/i18n/fr.po) :
   « Filtres », « Regrouper par », « Favoris », « Ajouter un filtre
   personnalisé », « Ajouter un groupe personnalisé », « Enregistrer la
   recherche actuelle », « Mesures », « Nouveau », « Ajouter une ligne ».
   Montants du pivot avec décimales (« 1 293 000,00 ») : captures/04.

Chiffres des résultats : 24 barèmes (city_tax_data.xml ; ROADMAP.md:63) ;
aucune saisie de la réception (aite_city_tax/__manifest__.py:23
« Aucune action de la réception » ; CLAUDE.md, règle d'intuitivité 3 ;
scenario_city_tax.py:80) ; une ligne par folio, hors TVA, recalculée,
figée à la facture (hotel_folio.py:100-144).

Captures de référence (modèle visuel, jamais incrustées) : ref_muk/040,
046, 029, 031, 027 ; captures/02, 02b, 03, 04, 05 ; captures prises en
lecture seule sur la base MuK (compte demo.direction) pour la mise en page
des en-têtes de fiche, du menu de recherche et des menus déroulants.

ÉCARTS rejoués tels quels (signalés, jamais corrigés) : barème affiché en
anglais et en code ISO (« Cameroon — 3 ★ : 3 000 XAF », city_tax_rate.py:
71-80, champ stocké calculé à l'installation) ; « XAF » au lieu de « FCFA »
dans la phrase de l'onglet (hotel_hotel.py:73-77) ; chemin de menu inexact
dans le texte gris (« Hôtel → Configuration → Taxe de séjour → Barèmes »,
le menu réel est « Configuration → Barèmes de taxe de séjour ») ; sommes
absurdes sur les lignes de regroupement des barèmes ; dates ISO dans le
libellé de la nuitée (hotel_folio.py:256-260) ; mois au format « 2026-10 »
et montants à décimales dans l'état mensuel (city_tax_report.py:32-33, :78) ;
taxe « 19.25% » à point décimal (l10n_cm d'Odoo).

Données : demo.py (Complexe Hôtelier — Démo, Démo Hôtellerie SARL, Estelle
Ngono, RES/2026/0214, FOL/2026/0214, chambre 204 [CFT] Confort à 45 000
FCFA la nuit). Chiffres de l'état mensuel fictifs, cohérents avec un 3 ★ à
3 000 F l'unité ; août et septembre repris du chapitre 7 de la
présentation (scenarios/c7_conformite.py).
"""

import demo
from ecrans import (APPS_PROFIL, ICONES, _id, bouton, deux_colonnes, e, fenetre_muk, groupe, icone, navigateur,
                    statusbar, titre_fiche, vue_fiche, vue_libre)
from marketing import bulle, dezoom, reaction, zoom
from moteur import anneau, cacher, clic, classe, curseur, defiler, montrer, pause, saisir, texte, vue

NOM, ROLE = demo.POSTES['conformite']
MENUS = ['Direction', 'Front Desk', 'Réservations', 'Espaces & Prestations', 'Notes de chambre en attente',
         'Facturation', 'Fidélité', 'Gouvernante', 'Configuration']

# Les montants du séjour d'Estelle Ngono : deux nuits, puis trois (une nuit de plus).
# Nuitée à 45 000 FCFA (demo.PRIX_NUIT), TVA « 19.25% » sur la nuitée seule,
# taxe de séjour 3 ★ Cameroun : 3 000 F par personne et par nuit, 2 adultes.
AVANT = {'nuits': '2', 'dep': demo.DEPART, 'heb': '90 000 FCFA', 'qte_n': '2,00', 'ttc_n': '107 325 FCFA',
         'taxe': '12 000 FCFA', 'qte_t': '4,00', 'ht': '102 000 FCFA', 'tva': '17 325 FCFA', 'ttc': '119 325 FCFA',
         'lib_n': 'Nuitée 204 (Confort) — 2026-10-14 → 2026-10-16',
         'lib_t': 'Taxe de séjour — 4 nuitée(s) × personne (3 ★, Cameroun)', 'date': '12/10/2026'}
APRES = {'nuits': '3', 'dep': '17/10/2026 12:00:00', 'heb': '135 000 FCFA', 'qte_n': '3,00', 'ttc_n': '160 988 FCFA',
         'taxe': '18 000 FCFA', 'qte_t': '6,00', 'ht': '153 000 FCFA', 'tva': '25 988 FCFA', 'ttc': '178 988 FCFA',
         'lib_n': 'Nuitée 204 (Confort) — 2026-10-14 → 2026-10-17',
         'lib_t': 'Taxe de séjour — 6 nuitée(s) × personne (3 ★, Cameroun)', 'date': '13/10/2026'}

# Icônes du cadre web : regroupement (couches), engrenage, téléchargement, vues.
COUCHES = ('<svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linejoin="round">'
           '<path d="M12 3l9 4.5-9 4.5-9-4.5z" fill="#fff"/><path d="M3 12l9 4.5 9-4.5M3 16.5l9 4.5 9-4.5"/></svg>')
ROUAGE = ('<svg viewBox="0 0 24 24" fill="#495057"><path d="M10.3 2h3.4l.5 2.6 1.9.8 2.2-1.5 2.4 2.4-1.5 2.2.8 1.9 '
          '2.6.5v3.4l-2.6.5-.8 1.9 1.5 2.2-2.4 2.4-2.2-1.5-1.9.8-.5 2.6h-3.4l-.5-2.6-1.9-.8-2.2 1.5-2.4-2.4 1.5-2.2-.8-1.9'
          'L2 13.7v-3.4l2.6-.5.8-1.9-1.5-2.2 2.4-2.4 2.2 1.5 1.9-.8z"/><circle cx="12" cy="12" r="3.4" fill="#fff"/></svg>')
TELECHARGER = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" '
               'stroke-linejoin="round"><path d="M12 3v12M7 10l5 5 5-5M4 20h16"/></svg>')
V_PIVOT = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" '
           'height="16" rx="1"/><path d="M3 9h18M3 14h18M9 4v16M15 4v16"/></svg>')
V_LISTE = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round">'
           '<path d="M4 6h16M4 12h16M4 18h16"/></svg>')
V_GRAPHE = ('<svg viewBox="0 0 24 24" fill="currentColor"><path d="M3 20h18v1.5H3z"/><path d="M4 18l4-7 4 4 4-8 4 6v5H4z"/>'
            '</svg>')


def menu(nom):
    """Le sélecteur d'un menu de la barre (grille, nom de l'application, puis les menus)."""
    return '#app-t05 .o-haut .menu:nth-child(%d)' % (MENUS.index(nom) + 3)


def aide(libelle):
    """Un libellé qui porte une aide (le « ? » d'Odoo)."""
    return '%s<sup class="t05-aide">?</sup>' % e(libelle)


def ch(libelle, valeur, ident=None, aide_=False, gras=False, lien=False, saisie=False, html=False):
    """Un champ de fiche : libellé (gras s'il est modifiable), valeur ; ``saisie`` souligne un champ éditable."""
    l = aide(libelle) if aide_ else e(libelle)
    v = valeur if html else e(valeur)
    classes = 'v' + (' lien' if lien else '') + (' t05-saisie' if saisie else '')
    return ('<div class="ch"><span class="l%s">%s</span><span class="%s"%s>%s</span></div>'
            % (' gras' if gras else '', l, classes, _id(ident), v))


def facette(libelle, ico, ident=None):
    return ('<span class="facette"%s><span class="fic">%s</span><span class="ell">%s</span><span class="fx">×</span></span>'
            % (_id(ident), ico, e(libelle)))


def recherche(facettes, ident=None, toggler=None):
    return ('<div class="recherche"%s>%s%s<span class="ph">Rechercher…</span><span class="deroule"%s>▾</span></div>'
            % (_id(ident), icone('loupe', 'loupe'), ''.join(facettes), _id(toggler)))


def stat(ident, ico, libelle, valeur):
    return ('<span class="stat"%s>%s<span class="st-t"><span>%s</span><b id="%s-v">%s</b></span></span>'
            % (_id(ident), icone(ico, 'sic'), e(libelle), ident, e(valeur)))


def cp_fiche(parent_html, reference, stats_html='', pager='', ident_stats=None, stats_masque=False):
    """Le panneau d'une fiche : « Nouveau », fil d'Ariane, boutons intelligents, pagination."""
    return ('<div class="cp"><span class="bt contour">Nouveau</span>'
            '<div class="fil"><span class="parent">%s</span><span class="ref">%s<span class="t05-rouage">%s</span></span>'
            '</div><div class="stats%s"%s>%s</div><span class="pager">%s</span>'
            '<span class="t05-fleches"><i>‹</i><i>›</i></span></div>'
            % (parent_html, e(reference), ROUAGE, ' masque' if stats_masque else '', _id(ident_stats), stats_html,
               e(pager)))


def fiche(ident, cp, boutons, statut, contenu, apres_feuille='', initiale=False):
    """Une fiche Odoo 18 (même gabarit que ``ecrans.vue_fiche``) ; ``apres_feuille`` : ce qui défile sous la
    feuille, ici la discussion, qu'Odoo place sous la fiche à cette largeur d'écran."""
    bande = '<div class="bande"><div class="bb-groupe" id="%s-ga">%s</div>%s</div>' % (ident, ''.join(boutons), statut)
    feuille = ('<div class="feuille-cadre" id="%s-feuille" data-layout-allow-overflow data-layout-allow-occlusion>'
               '<div class="defil" id="%s-defil" data-layout-allow-overflow data-layout-allow-occlusion>'
               '<div class="feuille">%s</div>%s</div></div>' % (ident, ident, contenu, apres_feuille))
    return '<div class="vue%s" id="%s">%s</div>' % (' initiale' if initiale else '', ident, cp + bande + feuille)


def discussion(auteur, quand, jour, message):
    """La discussion d'Odoo 18 sous la fiche : boutons, séparateur de date, un message."""
    return ('<div class="t05-chatter"><div class="t05-ch-bts"><span class="bt primaire">%sEnvoyer message</span>'
            '<span class="bt gris">Note</span><span class="bt gris">%sActivités</span>'
            '<span class="t05-ch-droite">%s<span>Suivre</span></span></div>'
            '<div class="t05-ch-sep">%s</div><div class="ch-msg"><span class="ch-av">%s</span><div><div class="ch-a">'
            '<b>%s</b> <small>%s</small></div><div class="ch-t">%s</div></div></div></div>'
            % (icone('message'), icone('horloge'), icone('loupe', 'ico'), e(jour), e(auteur[0]), e(auteur), e(quand),
               e(message)))


def case(cochee=True):
    return '<span class="case%s"><i></i></span>' % (' coche' if cochee else '')


# ------------------------------------------------------------ fiche hôtel --
# Hôtel → Configuration → Hôtels → Complexe Hôtelier — Démo ; aucun <header> :
# la feuille suit le panneau (pas de bande de boutons).
H_GAUCHE = (
    groupe('Identité', [ch('Code', 'CHD', aide_=True, gras=True, saisie=True),
                        ch('Catégorie', demo.ETOILES, 't05-h-cat', gras=True, saisie=True)])
    + groupe('Coordonnées', [ch('Rue', 'Akwa', gras=True, saisie=True), ch('Ville', demo.VILLE, gras=True, saisie=True),
                             ch('Pays', 'Cameroun', 't05-h-pays', gras=True, saisie=True),
                             ch('Téléphone', '+237 6 99 00 00 00', gras=True, saisie=True),
                             ch('E-mail', '', gras=True, saisie=True), ch('Site web', '', gras=True, saisie=True)]))
ETAGES = ''.join('<div class="t05-etage"><span class="t05-poignee">⠿</span><span>%s</span>%s</div>'
                 % (n, icone('corbeille', 't05-corb')) for n in ('Rez-de-chaussée', '1er étage', '2e étage'))
H_DROITE = (
    groupe('Horaires standards', [ch("Heure d'arrivée standard", '14:00', aide_=True, gras=True, saisie=True),
                                  ch('Heure de départ standard', '12:00', aide_=True, gras=True, saisie=True)])
    + groupe('Structure', [ch('Chambres vendables', '20', aide_=True),
                           '<div class="t05-etages"><div class="t05-etage t05-tete"><span></span><span>Nom</span></div>'
                           '%s<div class="t05-etage t05-ajout"><span></span><span>Ajouter une ligne</span></div></div>'
                           % ETAGES]))
H_TAXE = (
    '<div class="t05-onglet-corps">'
    + deux_colonnes(groupe('Réglage', [ch('Collecter la taxe de séjour', case(), aide_=True, gras=True, html=True),
                                       ch('Pays (fiche hôtel)', 'Cameroun', lien=True),
                                       ch('Catégorie (fiche hôtel)', demo.ETOILES)]),
                    groupe("Ce qui s'applique", [ch('Barème appliqué', 'Cameroon — 3 ★ : 3 000 XAF', 't05-h-bareme',
                                                    aide_=True),
                                                 ch('Montant par nuitée', '3 000', aide_=True),
                                                 ch('Base', 'Par personne et par nuit', aide_=True)]))
    + '<div class="alerte-info t05-alerte" id="t05-h-phrase"><b class="t05-i">i</b>Chaque séjour portera une ligne '
      '« Taxe de séjour » de 3 000 XAF par personne et par nuit, hors TVA.</div>'
      '<div class="note-pied t05-gris" id="t05-h-aide">La taxe est ajoutée automatiquement à chaque folio et recalculée si '
      'les dates, les chambres ou le nombre de personnes changent. Elle n\'entre pas dans la base de la TVA. Pour modifier '
      'un montant (nouvelle loi de finances) : <b>Hôtel → Configuration → Taxe de séjour → Barèmes</b>.</div></div>')
H_POLITIQUE = ('<div class="t05-onglet-corps t05-ph" id="t05-h-pol">Conditions d\'annulation, acompte demandé, animaux, '
               'taxes de séjour…</div>')
FEUILLE_HOTEL = (
    '<div class="t05-photo">%s</div>' % icone('fiche', 't05-photo-i')
    + titre_fiche(demo.HOTEL)
    + deux_colonnes(H_GAUCHE, H_DROITE)
    + '<div class="onglets t05-onglets"><span class="onglet actif" id="t05-h-ong-pol">Politique / informations</span>'
      '<span class="onglet" id="t05-h-ong-taxe">Taxe de séjour</span></div>'
    # l'onglet « Taxe de séjour » reste dans le flux (la feuille garde sa hauteur) ; la politique se pose dessus
    + '<div class="pile"><div class="masque" id="t05-h-taxe">%s</div>%s</div>' % (H_TAXE, H_POLITIQUE))
HOTEL = vue_fiche('t05-hotel', cp_fiche('Hôtels', demo.HOTEL, stat('t05-h-st', 'lit', 'Chambres', '20'), '1 / 1'),
                  [], '', FEUILLE_HOTEL, initiale=True)

# ------------------------------------------------------------ barèmes --
# Hôtel → Configuration → Barèmes de taxe de séjour : liste éditable, regroupée par pays.
GAB_B = '40px 170px 210px 190px 90px 270px 200px 1fr 30px'
REF_CM = 'Loi de finances 2017 — déclaration mensuelle DGI (formulaire I/PL-TVA-IR)'
REF_CM0 = 'Loi de finances 2017 — « autres établissements et meublés »'
TETE_B = ('<div class="tete" style="grid-template-columns:%s"><span class="cb"></span><span class="t05-tri">Pays '
          '<b>⌃</b></span><span>Catégorie</span><span class="d">Montant par nuitée</span><span>Devise</span>'
          '<span>Base de calcul</span><span class="ell">Compter les enfants</span><span>Référence légale</span>'
          '<span class="t05-opt">⇋</span></div>' % GAB_B)


def groupe_b(ident, pays, n, somme, ouvert=False):
    return ('<div class="ligne t05-grp"%s style="grid-template-columns:%s"><span class="t05-caret">%s</span>'
            '<span class="t05-grp-l">%s (%d)</span><span class="d">%s</span></div>'
            % (_id(ident), GAB_B, '▾' if ouvert else '▸', e(pays), n, e(somme)))


def ligne_b(ident, cat, montant, ref):
    return ('<div class="ligne" id="%s" style="grid-template-columns:%s"><span class="cb"></span><span>Cameroun</span>'
            '<span class="ell">%s</span><span class="d" id="%s-mt">%s</span><span>XAF</span>'
            '<span class="ell">Par personne et par nuit</span><span>%s</span><span class="ell" id="%s-ref">%s</span>'
            '<span></span></div>' % (ident, GAB_B, e(cat), ident, e(montant), case(False), ident, e(ref)))


AUTRES = [('Côte d\'Ivoire', '9 000'), ('Guinée', '60 000'), ('Sénégal', '6 000')]
FERME = (groupe_b('t05-g-cm', 'Cameroun', 6, '14 000')
         + ''.join(groupe_b(None, p, 6, s) for p, s in AUTRES))
OUVERT = (groupe_b(None, 'Cameroun', 6, '14 000', ouvert=True)
          + ''.join(ligne_b('t05-b%d' % i, c, m, REF_CM0 if c.startswith('Non') else REF_CM)
                    for i, (c, m) in enumerate([('5 ★', '5 000'), ('4 ★', '4 000'), ('3 ★', '3 000'), ('2 ★', '1 000'),
                                                ('1 ★', '500'), ('Non classé / meublé', '500')], 1))
          + '<div class="ligne t05-ajout-l" style="grid-template-columns:%s"><span></span><span class="t05-lien">'
            'Ajouter une ligne</span></div>' % GAB_B
          + ''.join(groupe_b(None, p, 6, s) for p, s in AUTRES))
CP_BAREMES = ('<div class="cp"><span class="bt primaire">Nouveau</span><span class="titre">Barèmes de taxe de séjour'
              '<span class="t05-rouage">%s</span></span>%s<span class="pager">1-4 / 4</span>'
              '<span class="t05-fleches"><i>‹</i><i>›</i></span></div>'
              % (ROUAGE, recherche([facette('Pays', COUCHES)])))
BAREMES = vue_libre('t05-baremes', CP_BAREMES + '<div class="liste t05-liste">%s<div class="pile">'
                    '<div id="t05-bar-ferme">%s</div><div class="masque" id="t05-bar-ouvert">%s</div></div></div>'
                    % (TETE_B, FERME, OUVERT))

# ------------------------------------------------------------ réservation --
# Réservations → RES/2026/0214 : en brouillon, puis confirmée d'un clic.
R_STATS = (stat('t05-r-st-folio', 'document', 'Folio', AVANT['ttc'])
           + stat('t05-r-st-fiches', 'fiche', 'Fiches clients', '0/2'))
DEPART = ('<span class="t05-champ" id="t05-r-dep"><span class="ph" id="t05-r-dep-ph"></span>'
          '<span class="val" id="t05-r-dep-val">%s</span></span>' % e(demo.DEPART))
FEUILLE_RESA = (
    titre_fiche(demo.RESA)
    + deux_colonnes(
        groupe('Client', [ch('Client', demo.CLIENT, gras=True, saisie=True), ch('Téléphone', demo.CLIENT_TEL),
                          ch('E-mail', demo.CLIENT_MAIL), ch('Hôtel', demo.HOTEL, gras=True, saisie=True)])
        + groupe('Canal & commission', [ch('Canal', 'Téléphone / WhatsApp', gras=True, saisie=True)]),
        groupe('Séjour', [ch('Arrivée', demo.ARRIVEE, gras=True, saisie=True),
                          ch('Départ', DEPART, gras=True, html=True),
                          ch('Nuits', AVANT['nuits'], 't05-r-nuits', aide_=True),
                          ch('Total hébergement (HT)', AVANT['heb'], 't05-r-total')])
        + groupe('Occupation', [ch('Nb chambres', '1'), ch('Adultes', '2'), ch('Enfants', '0')], 't05-r-occ'))
    + '<div class="onglets"><span class="onglet actif">Chambres</span><span class="onglet">Demandes particulières</span></div>'
    + '<div class="table t05-table"><div class="t-tete" style="grid-template-columns:%s"><span>Type</span>'
      '<span>Chambre</span><span class="d">Adultes</span><span class="d">Enfants</span><span>Occupants</span>'
      '<span class="d">Nuits</span><span class="d">Prix / nuit</span><span class="d">Sous-total (HT)</span><span></span>'
      '</div><div class="t-ligne" style="grid-template-columns:%s"><span>%s</span><span>%s</span><span class="d">2</span>'
      '<span class="d">0</span><span></span><span class="d" id="t05-r-l-nuits">2</span><span class="d">%s</span>'
      '<span class="d" id="t05-r-l-st">%s</span><span class="t05-ech">⇄</span></div>'
      '<div class="t-ajout">Ajouter une ligne</div></div>'
      % (('1fr 170px 110px 110px 170px 90px 170px 200px 40px',) * 2 + (demo.TYPE, demo.CHAMBRE, demo.PRIX_NUIT,
                                                                       AVANT['heb'])))
B_BROUILLON = [bouton('t05-r-confirmer', 'Confirmer', 'primaire'), bouton(None, 'Annuler')]
B_CONFIRMEE = [bouton(None, 'Check-in', 'primaire'), bouton(None, 'Encaisser un acompte'),
               bouton(None, 'Envoyer la confirmation'), bouton(None, "Fiches d'enregistrement", ico='imprimer'),
               bouton(None, 'No-show'), bouton(None, 'Annuler')]
RESA = vue_fiche('t05-resa', cp_fiche('Réservations', demo.RESA, R_STATS, '4 / 18', 't05-r-stats', stats_masque=True),
                 B_BROUILLON, statusbar('t05-r-sb', ['Brouillon', 'Confirmée', 'Arrivé', 'Parti'], 0), FEUILLE_RESA,
                 boutons_apres=[B_CONFIRMEE])

# ------------------------------------------------------------ folio --
# Bouton « Folio » de la réservation → FOL/2026/0214 ; la ligne de taxe est en orange.
GAB_F = '110px 150px 74px 1fr 52px 120px 84px 134px 126px 22px'


def ligne_f(ident, valeurs, nuitee):
    badge = ('<span class="puce info">Nuitée</span>' if nuitee
             else '<span class="puce orange">Taxe de séjour</span>')
    taxe = '<span class="t05-tag">19.25%</span>' if nuitee else ''
    k = 'n' if nuitee else 't'
    return ('<div class="t-ligne %s" id="%s" style="grid-template-columns:%s"><span id="%s-date">%s</span>'
            '<span>%s</span><span></span><span class="ell" id="%s-lib">%s</span><span class="d" id="%s-qte">%s</span>'
            '<span class="d">%s</span><span id="%s-taxes">%s</span><span class="d" id="%s-st">%s</span>'
            '<span class="d" id="%s-ttc">%s</span><span class="t05-corb2">%s</span></div>'
            % ('t05-nuitee' if nuitee else 't05-taxe', ident, GAB_F, ident, valeurs['date'], badge, ident,
               valeurs['lib_' + k], ident, valeurs['qte_' + k], demo.PRIX_NUIT if nuitee else '3 000 FCFA', ident, taxe,
               ident, valeurs['heb'] if nuitee else valeurs['taxe'], ident,
               valeurs['ttc_n'] if nuitee else valeurs['taxe'], ICONES['corbeille']))


LIGNES_F = ('<div class="table t05-table t05-lignes"><div class="t-tete" style="grid-template-columns:%s"><span>Date</span>'
            '<span>Type</span><span>Service</span><span>Libellé</span><span class="d">Qté</span>'
            '<span class="d">Prix unitaire</span><span>Taxes</span><span class="d ell">Sous-total (HT)</span>'
            '<span class="d">Total (TTC)</span><span class="t05-opt">⇋</span></div>%s%s'
            '<div class="t-ajout">Ajouter une ligne</div><div class="t-total" style="grid-template-columns:%s">'
            '<span></span><span></span><span></span><span></span><span></span><span></span><span></span>'
            '<span class="d" id="t05-f-tot-ht">%s</span><span class="d" id="t05-f-tot-ttc">%s</span><span></span></div>'
            '</div>' % (GAB_F, ligne_f('t05-f-l1', AVANT, True), ligne_f('t05-f-l2', AVANT, False), GAB_F, AVANT['ht'],
                        AVANT['ttc']))
FEUILLE_FOLIO = (
    titre_fiche(demo.FOLIO)
    + deux_colonnes(
        groupe('Séjour', [ch('Client', demo.CLIENT, lien=True), ch('Réservation', demo.RESA, lien=True),
                          ch('Séjour', 'Confirmée'), ch('Arrivée', demo.ARRIVEE),
                          ch('Départ', AVANT['dep'], 't05-f-dep')]),
        groupe('Montants', [ch('Hébergement (HT)', AVANT['heb'], 't05-f-heb'), ch('Services (HT)', '0 FCFA'),
                            ch('Taxe de séjour', AVANT['taxe'], 't05-f-taxe', aide_=True),
                            ch('Total HT', AVANT['ht'], 't05-f-ht'), ch('Taxes', AVANT['tva'], 't05-f-tva'),
                            ch('Total TTC', '<b id="t05-f-ttc">%s</b>' % AVANT['ttc'], html=True),
                            ch('Encaissé', '0 FCFA'),
                            ch('Solde dû', '<b id="t05-f-solde">%s</b>' % AVANT['ttc'], html=True)], 't05-f-montants'))
    + '<div class="onglets"><span class="onglet actif">Lignes du folio</span><span class="onglet">Règlements</span>'
      '<span class="onglet">Note</span></div>' + LIGNES_F
    + '<div class="note-pied">Les lignes « nuitée » sont synchronisées depuis la réservation ; ajoutez librement des '
      'lignes de service (restaurant, blanchisserie, minibar…).</div>')
# Message de création d'Odoo (« %s créé », mail/i18n/fr.po) avec la description du modèle
# (« Folio client (note de séjour) », hotel_folio.py:23), signé par qui a confirmé.
FOLIO = fiche('t05-folio', cp_fiche('Réservations / <span id="t05-f-fil">%s</span>' % e(demo.RESA), demo.FOLIO,
                                    stat('t05-f-st', 'billet', 'Règlements', '0'), '1 / 1'),
              [bouton(None, 'Encaisser', 'primaire'), bouton(None, 'Générer la facture'),
               bouton(None, 'Recalculer la taxe de séjour', 'lien'), bouton(None, 'Annuler')],
              statusbar('t05-f-sb', ['Ouvert', 'Facturé', 'Soldé'], 0), FEUILLE_FOLIO,
              discussion(NOM, '12 oct., 10:05', '12 oct. 2026', 'Folio client (note de séjour) créé'))

# ------------------------------------------------------------ état mensuel --
# Hôtel → Facturation → Taxe de séjour : pivot mois × hôtel, regroupé par mois.
ENTETES = ('<tr><td class="vide"></td><th colspan="2">⊟ Total</th></tr>'
           '<tr><td class="vide"></td><th colspan="2">⊞ %s</th></tr>'
           '<tr><td class="vide"></td><th class="m">Nuitées taxées</th><th class="m">Taxe collectée</th></tr>'
           % e(demo.HOTEL))


def pivot(ident, lignes, total):
    corps = ''.join('<tr id="%s-%d"><td class="r n2">⊞ %s</td><td>%s</td><td>%s</td></tr>' % (ident, i, m, n, t)
                    for i, (m, n, t) in enumerate(lignes))
    return ('<table class="pv t05-pv" id="%s">%s<tr class="tot" id="%s-tot"><td class="r">⊟ Total</td><td>%s</td>'
            '<td>%s</td></tr>%s</table>' % (ident, ENTETES, ident, total[0], total[1], corps))


MOIS = [('2026-08', '347', '1 041 000,00'), ('2026-09', '408', '1 224 000,00'), ('2026-10', '431', '1 293 000,00'),
        ('2026-11', '64', '192 000,00')]
MENU_RECHERCHE = (
    '<div class="t05-rmenu masque" id="t05-e-menu" data-layout-allow-overlap data-layout-allow-occlusion>'
    '<div class="t05-rcol"><div class="t05-rtitre">%sFiltres</div><div>Départs du mois</div>'
    '<div id="t05-e-f-dernier">Départs du mois dernier</div><hr><div>Séjours terminés (à déclarer)</div>'
    '<div>Séjours en cours (prévision)</div><hr><div>Ajouter un filtre personnalisé</div></div>'
    '<div class="t05-rcol"><div class="t05-rtitre">%sRegrouper par</div><div class="t05-coche">Mois</div>'
    '<div>Hôtel</div><hr><div>Ajouter un groupe personnalisé ▾</div></div>'
    '<div class="t05-rcol"><div class="t05-rtitre">%sFavoris</div><div>Enregistrer la recherche actuelle ▾</div></div>'
    '</div>' % (icone('filtre', 't05-ri t05-ri-f'), '<span class="t05-ri t05-ri-c">%s</span>' % COUCHES,
                icone('etoile', 't05-ri')))
CP_ETAT = (
    '<div class="cp"><span class="titre t05-titre-pv">Taxe de séjour — état mensuel</span>'
    '<div class="pile t05-rpile"><div id="t05-e-rech-a">%s</div><div class="masque" id="t05-e-rech-b">%s</div></div>'
    '<span class="t05-vues"><span class="actif">%s</span><span>%s</span><span>%s</span></span></div>'
    % (recherche([facette('Mois', COUCHES)], toggler='t05-e-toggler'),
       recherche([facette('Mois', COUCHES), facette('Départs du mois dernier', ICONES['filtre'])]),
       V_PIVOT, V_LISTE, V_GRAPHE))
ETAT = vue_libre('t05-etat', CP_ETAT
                 + '<div class="pv-barre"><span class="bt primaire">Mesures ▾</span><span class="bt gris">⇄</span>'
                   '<span class="bt gris">✥</span><span class="bt gris t05-dl" id="t05-e-export">%s</span></div>'
                 % TELECHARGER
                 + '<div class="pile t05-pvpile"><div id="t05-e-tab-a">%s</div><div class="masque" id="t05-e-tab-b">%s'
                   '</div></div>' % (pivot('t05-e-a', MOIS, ('1 250', '3 750 000,00')),
                                     pivot('t05-e-b', MOIS[2:3], ('431', '1 293 000,00')))
                 + MENU_RECHERCHE)

# ------------------------------------------------------- menus déroulants --
# Les sous-menus de la barre (load_menus du compte demo.direction), posés sous leur menu ; celui de
# « Configuration » s'aligne sur le bord droit de la fenêtre, comme le fait Odoo quand la place manque.
def deroule(ident, gauche, items):
    return ('<div class="t05-deroule masque" id="%s" style="left:%dpx" data-layout-allow-overlap '
            'data-layout-allow-occlusion>%s</div>'
            % (ident, gauche, ''.join('<div%s>%s</div>' % (_id(i), e(t)) for i, t in items)))


DEROULES = (
    deroule('t05-dd-resa', 365, [('t05-dd-resa-res', 'Réservations'), (None, 'Planning des chambres')])
    + deroule('t05-dd-fact', 1030, [(None, 'Folios'), (None, 'Règlements'), ('t05-dd-fact-taxe', 'Taxe de séjour'),
                                     (None, 'Registre de police (impression)'), (None, "Statistiques d'hébergement")])
    + deroule('t05-dd-conf', 1362, [(None, 'Hôtels'), (None, 'Types de chambre'), (None, 'Chambres'),
                                     (None, 'Aménités'), (None, 'Services hôteliers'), (None, 'Tarifs saisonniers'),
                                     ('t05-dd-conf-bar', 'Barèmes de taxe de séjour'),
                                     (None, 'Points de contrôle (inspection)')]))

ECRAN = navigateur(fenetre_muk('app-t05', 'Hôtel', MENUS, [HOTEL, BAREMES, RESA, FOLIO, ETAT], actif='Configuration',
                               societe='', initiale=NOM[0], avatar='#854F0B', apps=APPS_PROFIL['direction'],
                               app_active='Hôtel', calques=DEROULES))


def aller(depuis, vers, deroule_id, item):
    """Ouvrir un menu de la barre, choisir l'entrée : le menu choisi passe en gras."""
    return [clic(menu(vers), d=0.55), montrer('#' + deroule_id, d=0.2, y=-8), pause(0.25), clic(item, d=0.45),
            cacher('#' + deroule_id, d=0.15)] + ([classe(menu(depuis), retirer=['actif']),
                                                   classe(menu(vers), ajouter=['actif'], avec=True)]
                                                  if depuis != vers else [])


def maj_folio(v):
    """Le folio relu après la prolongation : chaque montant suit."""
    return [texte(s, v[k], avec=True) for s, k in (
        ('#t05-f-dep', 'dep'), ('#t05-f-heb', 'heb'), ('#t05-f-taxe', 'taxe'), ('#t05-f-ht', 'ht'), ('#t05-f-tva', 'tva'),
        ('#t05-f-ttc', 'ttc'), ('#t05-f-solde', 'ttc'), ('#t05-f-l1-date', 'date'), ('#t05-f-l1-lib', 'lib_n'),
        ('#t05-f-l1-qte', 'qte_n'), ('#t05-f-l1-st', 'heb'), ('#t05-f-l1-ttc', 'ttc_n'), ('#t05-f-l2-date', 'date'),
        ('#t05-f-l2-lib', 'lib_t'), ('#t05-f-l2-qte', 'qte_t'), ('#t05-f-l2-st', 'taxe'), ('#t05-f-l2-ttc', 'taxe'),
        ('#t05-f-tot-ht', 'ht'), ('#t05-f-tot-ttc', 'ttc'))]


CSS = """
#app-t05 .o-haut { gap: 20px; }
#t05-bar-ouvert { background: #fff; }
.t05-aide { font-size: 13px; font-weight: 600; color: #1B6A82; margin-left: 3px; position: relative; top: -8px; }
.t05-rouage { display: inline-flex; width: 17px; height: 17px; margin-left: 8px; vertical-align: -1px; }
.t05-rouage svg { width: 100%; height: 100%; }
.t05-fleches { display: inline-flex; gap: 2px; margin-left: 12px; }
.t05-fleches i { width: 40px; height: 40px; border-radius: 4px; background: #E9ECEF; color: #495057; font-style: normal;
  font-size: 26px; display: flex; align-items: center; justify-content: center; }
.t05-saisie { border-bottom: 1px solid #DEE2E6; padding: 4px 0 6px; min-height: 34px; }
.t05-champ { position: relative; display: block; height: 38px; border-bottom: 1px solid #DEE2E6; }
.t05-champ.focus { border-bottom: 2px solid var(--muk-prim); }
.t05-champ .ph, .t05-champ .val { position: absolute; left: 0; top: 50%; transform: translateY(-50%); white-space: nowrap; }
.t05-champ .val { color: var(--o-texte); }
/* fiche hôtel : pas de <header>, la feuille suit le panneau */
#t05-hotel .bande { display: none; }
#t05-hotel .feuille-cadre { top: 96px; }
#t05-hotel .feuille { position: relative; }
.t05-photo { position: absolute; right: 34px; top: 24px; width: 112px; height: 112px; border: 1px solid #DEE2E6;
  border-radius: 4px; background: #F8F9FA; display: flex; align-items: center; justify-content: center; color: #ADB5BD; }
.t05-photo-i { width: 60px; height: 60px; display: inline-flex; }
.t05-photo-i svg { width: 100%; height: 100%; }
#t05-hotel .f-titre { width: 1100px; border-bottom: 1px solid #DEE2E6; padding-bottom: 6px; }
#t05-hotel .f-cols { margin-right: 150px; }
.t05-etages { margin-top: 6px; }
.t05-etage { display: grid; grid-template-columns: 40px 1fr 30px; align-items: center; height: 42px;
  border-bottom: 1px solid #EEF0F2; font-size: 18px; color: var(--o-texte); }
.t05-etage.t05-tete { font-weight: 600; border-bottom-color: #DEE2E6; }
.t05-etage.t05-ajout { color: var(--o-prim); border-bottom: 0; }
.t05-poignee { color: #6C757D; text-align: center; }
.t05-corb { width: 17px; height: 17px; display: inline-flex; color: #495057; }
.t05-corb svg, .t05-corb2 svg { width: 100%; height: 100%; }
.t05-corb2 { width: 18px; height: 18px; display: inline-flex; color: #495057; }
.t05-onglets { margin-top: 24px; }
.t05-onglet-corps { padding-top: 22px; }
.t05-ph { color: #ADB5BD; font-size: 19px; }
.t05-alerte { display: flex; gap: 12px; align-items: center; }
.t05-i { flex: none; width: 22px; height: 22px; border-radius: 50%; background: #055160; color: #CFF4FC; font-size: 15px;
  display: inline-flex; align-items: center; justify-content: center; font-family: Georgia, serif; }
.t05-gris { line-height: 1.5; }
.t05-gris b { color: var(--o-texte-2); }
/* listes */
.t05-liste .tete span, .t05-liste .ligne span { white-space: nowrap; }
.t05-tri b { font-weight: 400; color: #495057; margin-left: 6px; }
.t05-opt { color: #495057; text-align: center; }
.t05-grp { background: #F1F3F5; font-weight: 600; height: 50px !important; }
.t05-caret { text-align: center; font-size: 15px; color: #495057; }
.t05-grp-l { grid-column: 2 / span 2; }
.t05-grp .d { grid-column: 4; }
.t05-ajout-l { height: 50px !important; }
.t05-lien { color: var(--o-prim); }
/* bandes de boutons : à la taille d'Odoo, pour que boutons et étapes tiennent sur une ligne */
#t05-resa .bande .bt, #t05-folio .bande .bt { font-size: 17px; height: 42px; padding: 0 13px; }
#t05-resa .bb-groupe, #t05-folio .bb-groupe { gap: 6px; }
#t05-resa .st-et, #t05-folio .st-et { font-size: 17px; height: 42px; padding: 0 16px 0 26px; }
#t05-resa .st-et:first-child, #t05-folio .st-et:first-child { padding-left: 16px; }
#t05-resa .st-et:not(.actif), #t05-folio .st-et:not(.actif) { color: #555C63; }
/* la discussion, sous la feuille */
.t05-chatter { padding: 22px 0 40px; color: var(--o-texte); }
.t05-ch-bts { display: flex; gap: 8px; align-items: center; }
.t05-ch-bts .bt { height: 42px; font-size: 17px; padding: 0 13px; }
.t05-ch-bts .bt .ico { width: 17px; height: 17px; }
.t05-ch-droite { margin-left: auto; display: flex; gap: 22px; align-items: center; font-size: 18px; color: #495057; }
.t05-ch-droite .ico { width: 20px; height: 20px; display: inline-flex; }
.t05-ch-sep { display: flex; align-items: center; gap: 16px; margin: 24px 0 4px; font-size: 15px; color: #5C636A; }
.t05-ch-sep::before, .t05-ch-sep::after { content: ''; flex: 1; border-top: 1px solid #DEE2E6; }
.t05-chatter .ch-a small { color: #5C636A; }
.t05-chatter .ch-msg { border-top: 0; margin-top: 10px; padding-top: 6px; font-size: 18px; }
.t05-table .t-tete span, .t05-table .t-ligne span { white-space: nowrap; }
.t05-ech { color: var(--o-prim); text-align: center; }
.t05-lignes .t-tete, .t05-lignes .t-ligne, .t05-lignes .t-total { padding: 0 26px; column-gap: 10px; font-size: 17px; }
.t05-lignes .t-ligne.t05-nuitee { color: #0E7490; }
.t05-lignes .t-ligne.t05-taxe { color: #8A5300; }
.t05-lignes .puce { font-size: 15px; height: 27px; }
.t05-tag { display: inline-flex; align-items: center; height: 26px; padding: 0 9px; border-radius: 999px;
  background: #E9ECEF; color: #343A40; font-size: 15px; }
/* état mensuel */
.t05-titre-pv { font-size: 24px; }
.t05-rpile { margin-left: 120px; }
.t05-rpile .recherche { margin-left: 0; width: 700px; }
.t05-vues { margin-left: auto; display: flex; }
.t05-vues span { width: 52px; height: 44px; display: flex; align-items: center; justify-content: center; background: #E9ECEF;
  color: #343A40; border: 1px solid #DEE2E6; }
.t05-vues span.actif { background: #DCE6EC; border-color: var(--muk-prim); }
.t05-vues svg { width: 22px; height: 22px; }
.t05-dl { width: 52px; justify-content: center; padding: 0; }
.t05-dl svg { width: 22px; height: 22px; }
.t05-pvpile { margin: 4px 0 0; }
.t05-pv { font-size: 20px; }
.t05-pv td, .t05-pv th { height: 50px; padding: 0 18px; }
.t05-rmenu { position: absolute; top: 74px; left: 222px; width: 1000px; z-index: 30; background: #fff;
  border: 1px solid rgba(0,0,0,.15); border-radius: 4px; box-shadow: 0 10px 28px rgba(0,0,0,.18); padding: 18px 0;
  display: grid; grid-template-columns: 1fr 1fr 1fr; color: var(--o-texte); font-size: 19px; }
.t05-rcol { padding: 0 22px; border-right: 1px solid #DEE2E6; }
.t05-rcol:last-child { border-right: 0; }
.t05-rcol > div { height: 40px; display: flex; align-items: center; padding-left: 32px; white-space: nowrap; }
.t05-rcol > div.t05-rtitre { padding-left: 0; font-size: 21px; font-weight: 600; gap: 10px; margin-bottom: 4px; }
.t05-rcol > div.t05-coche { font-weight: 600; position: relative; }
.t05-rcol > div.t05-coche::before { content: '✓'; position: absolute; left: 8px; color: var(--muk-prim); }
.t05-rcol hr { border: 0; border-top: 1px solid #DEE2E6; margin: 8px 0 8px 22px; }
.t05-ri { width: 20px; height: 20px; display: inline-flex; color: #212529; }
.t05-ri svg { width: 100%; height: 100%; }
.t05-ri-f svg path { fill: #212529; }
.t05-ri-c svg { stroke: #212529; }
.t05-ri-c svg path:first-child { fill: #212529; }
/* menus déroulants de la barre */
.t05-deroule { position: absolute; top: 58px; z-index: 35; min-width: 300px; padding: 8px 0; background: #fff;
  border: 1px solid rgba(0,0,0,.15); border-radius: 4px; box-shadow: 0 10px 26px rgba(0,0,0,.20); }
.t05-deroule div { height: 40px; padding: 0 24px; display: flex; align-items: center; font-size: 19px;
  color: var(--o-texte); white-space: nowrap; }
"""

TUTORIEL = {
    'slug': 't05-taxe-sejour',
    'profil': 't05_taxe_sejour',
    'numero': 5,
    'titre': 'Taxe de séjour : elle se calcule toute seule',
    'fonction': 'Taxe de séjour automatique',
    'personnage': (NOM, ROLE),
    'accroche': {
        'kicker': 'La taxe de séjour',
        'question': 'Combien de taxe de séjour devez-vous *vraiment* déclarer ?',
        'douleurs': [('calculatrice', 'Nuits × personnes × barème, à la main'),
                     ('globe', 'Ailleurs, une ligne à ajouter soi-même'),
                     ('etoile', 'Un montant différent selon les étoiles'),
                     ('sablier', 'La déclaration DGI avant le 15'),
                     ('alerte', 'La taxe à garder hors de la TVA'),
                     ('cahier', 'Les nuitées du mois, recomptées')],
        'voix': "Combien de taxe de séjour devez-vous vraiment déclarer ? Étoiles, nuits, personnes, TVA à part : "
                "tout se recompte à la main.",
    },
    'revelation': {
        'promesse': "Réglée une fois sur la fiche de l'hôtel, la taxe s'ajoute seule à chaque folio, hors TVA, et "
                    "l'état du mois est prêt à déclarer.",
        'voix': "Avec Aïte haousse, la taxe de séjour se règle une fois, puis se calcule toute seule.",
    },
    'temps': ['Régler', 'Calculer', 'Déclarer'],
    'app': 'app-t05',
    'ecran': ECRAN,
    'vues_initiales': {'odoo': 't05-hotel'},
    'css': CSS,
    'bulles': {
        'b-phrase': "Une phrase dit ce qui sera facturé, avant le premier séjour.",
        'b-loi': "Une loi de finances change un montant ? On le corrige ici, sans code.",
        'b-zero': "Rien à saisir pour la taxe : un clic sur Confirmer.",
        'b-tva': "Aucune TVA sur cette ligne : la taxe reste hors base.",
        'b-fige': "Recalculée tant que le folio est ouvert, figée dès la facture.",
    },
    'reactions': {
        'r-fin': "Le montant à déclarer, prêt avant le 15.",
    },
    'etapes': [
        {'temps': 0, 'titre': "La fiche de l'hôtel", 'texte': 'Le pays et les étoiles choisissent le barème.',
         'voix': "Tout part de la fiche de l'hôtel. Dans l'onglet Taxe de séjour, le pays et les étoiles choisissent le "
                 "barème, et une phrase dit ce qui va se passer : trois mille francs par personne et par nuit, hors TVA.",
         'gestes': [pause(0.4), anneau('#t05-h-cat', d=1.0), anneau('#t05-h-pays', d=1.0), clic('#t05-h-ong-taxe'),
                    classe('#t05-h-ong-pol', retirer=['actif']), classe('#t05-h-ong-taxe', ajouter=['actif'], avec=True),
                    cacher('#t05-h-pol', d=0.15), montrer('#t05-h-taxe', d=0.35, y=10),
                    defiler('#t05-hotel-defil', -385, d=0.9), anneau('#t05-h-bareme', d=1.3),
                    zoom('#t05-h-phrase', s=1.6, fx=0.42, d=0.8), bulle('b-phrase', '#t05-h-phrase', cote='haut', d=2.6),
                    pause(2.4), dezoom(d=0.6)]},
        {'temps': 0, 'titre': 'Les barèmes, déjà là', 'texte': 'Quatre pays, six catégories, la référence légale.',
         'voix': "Les barèmes sont déjà là : Cameroun, Côte d'Ivoire, Sénégal et Guinée, avec leur référence légale. "
                 "Une loi de finances change un montant ? On le corrige dans la liste, sans programmeur.",
         'gestes': aller('Configuration', 'Configuration', 't05-dd-conf', '#t05-dd-conf-bar')
         + [vue('t05-baremes'), pause(0.4), clic('#t05-g-cm', fx=0.15), cacher('#t05-bar-ferme', d=0.15),
            montrer('#t05-bar-ouvert', d=0.3, y=0), anneau('#t05-b3', d=1.3),
            bulle('b-loi', '#t05-b3-mt', cote='bas', d=2.6), pause(1.6), anneau('#t05-b3-ref', d=1.2)]},
        {'temps': 1, 'titre': 'Un clic sur Confirmer', 'texte': 'Rien à saisir pour la taxe : le folio s\'ouvre, taxe comprise.',
         'voix': "Côté réception, rien à saisir pour la taxe. La réservation d'Estelle Ngono, deux nuits pour deux "
                 "adultes, se confirme d'un clic, et le folio s'ouvre aussitôt, taxe comprise.",
         'gestes': aller('Configuration', 'Réservations', 't05-dd-resa', '#t05-dd-resa-res')
         + [vue('t05-resa'), pause(0.4), anneau('#t05-r-occ', d=1.2),
            bulle('b-zero', '#t05-resa-ga', cote='droite', d=2.4), pause(1.0), clic('#t05-r-confirmer'),
            classe('#t05-r-sb-0', retirer=['actif']), classe('#t05-r-sb-1', ajouter=['actif']),
            cacher('#t05-resa-ga', d=0.2), montrer('#t05-resa-gb', d=0.3, y=0), montrer('#t05-r-stats', d=0.4, y=0),
            anneau('#t05-r-st-folio', d=1.4)]},
        {'temps': 1, 'titre': 'La ligne Taxe de séjour', 'texte': 'Ajoutée seule au folio : 4 nuitées × 3 000 F, sans TVA.',
         'voix': "Dans le folio, la ligne Taxe de séjour est apparue toute seule : quatre nuitées à trois mille francs, "
                 "douze mille francs. Elle n'a aucune TVA : seule la nuitée est taxée.",
         'gestes': [clic('#t05-r-st-folio'), vue('t05-folio'), pause(0.4), anneau('#t05-f-taxe', d=1.1),
                    defiler('#t05-folio-defil', -470, d=0.8), zoom('#t05-f-l2', s=1.5, fx=0.42, d=0.8),
                    bulle('b-tva', '#t05-f-l2', cote='bas', d=2.6), pause(2.2), dezoom(d=0.6),
                    anneau('#t05-f-l1-taxes', d=1.0)]},
        {'temps': 1, 'titre': 'Le séjour change, la taxe suit', 'texte': 'Une nuit de plus : 6 nuitées, 18 000 F.',
         'voix': "Estelle appelle : elle restera une nuit de plus. On repousse simplement sa date de départ : dans le "
                 "folio, la ligne passe à six nuitées, dix-huit mille francs, sans rien retoucher. Une fois le folio "
                 "facturé, elle ne bougera plus.",
         'gestes': [clic('#t05-f-fil', d=0.6), vue('t05-resa'), pause(0.3), clic('#t05-r-dep', fx=0.3, d=0.5),
                    saisir('t05-r-dep', APRES['dep'], d=1.0), texte('#t05-r-nuits', APRES['nuits']),
                    texte('#t05-r-total', APRES['heb'], avec=True), texte('#t05-r-l-nuits', APRES['nuits'], avec=True),
                    texte('#t05-r-l-st', APRES['heb'], avec=True), anneau('#t05-r-nuits', d=0.9),
                    *maj_folio(APRES), texte('#t05-r-st-folio-v', APRES['ttc'], avec=True),
                    defiler('#t05-folio-defil', 0, d=0.05, avec=True),
                    clic('#t05-r-st-folio'), vue('t05-folio'), pause(0.3), defiler('#t05-folio-defil', -470, d=0.7),
                    zoom('#t05-f-l2', s=1.5, fx=0.42, d=0.8), bulle('b-fige', '#t05-f-l2', cote='bas', d=2.6),
                    pause(1.8), dezoom(d=0.6)]},
        {'temps': 2, 'titre': "L'état du mois, prêt à déclarer", 'texte': 'Nuitées taxées et taxe collectée, mois par mois.',
         'voix': "Le mois suivant, l'état de la taxe de séjour est prêt : nuitées taxées et taxe collectée, mois par "
                 "mois. Avec le filtre Départs du mois dernier, il ne reste qu'octobre : son total est le montant à "
                 "déclarer et à reverser avant le quinze, et il s'exporte en Excel.",
         'gestes': aller('Réservations', 'Facturation', 't05-dd-fact', '#t05-dd-fact-taxe')
         + [vue('t05-etat'), pause(0.4), anneau('#t05-e-a-2', d=1.0), clic('#t05-e-toggler', d=0.55),
            montrer('#t05-e-menu', d=0.2, y=-6), pause(0.3), clic('#t05-e-f-dernier', d=0.5),
            cacher('#t05-e-menu', d=0.15), curseur('#t05-e-tab-b', fx=1.6, fy=0.7, d=0.5, avec=True),
            cacher('#t05-e-rech-a', d=0.1, avec=True),
            montrer('#t05-e-rech-b', d=0.2, y=0, avec=True), cacher('#t05-e-tab-a', d=0.2, avec=True),
            montrer('#t05-e-tab-b', d=0.3, y=0, avec=True), zoom('#t05-e-b', s=1.6, d=0.8),
            reaction('r-fin', d=3.0), anneau('#t05-e-b-tot', d=1.4), pause(1.2), dezoom(d=0.6),
            anneau('#t05-e-export', d=1.0)]},
    ],
    'resultats': {
        'titre': 'Réglée une fois, calculée à chaque séjour',
        'cartes': [
            {'valeur': '24', 'compter': 24, 'unite': 'barèmes', 'icone': 'globe',
             'texte': "livrés pour 4 pays et 6 catégories, modifiables sans code"},
            {'valeur': '0', 'unite': 'saisie', 'icone': 'personne',
             'texte': "pour la réception : la ligne s'ajoute à la confirmation"},
            {'valeur': '1', 'compter': 1, 'unite': 'ligne', 'icone': 'document',
             'texte': "par folio, hors TVA, recalculée si le séjour change, figée à la facture"},
        ],
        'voix': "Vingt-quatre barèmes livrés, aucune saisie pour la réception, une seule ligne par folio, hors TVA : "
                "la taxe de séjour se calcule toute seule.",
    },
    'cta': {
        'appel': 'Demandez votre démonstration',
        'suivant': 'Registre et fiche de police',
        'voix': "Aïte haousse, par Aïte Consulting. Demandez votre démonstration, et retrouvez tous nos tutoriels sur "
                "notre chaîne.",
    },
    'vignette': {'etape': 4, 'apres': 10.0},
}
