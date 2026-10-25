# -*- coding: utf-8 -*-
"""Tutoriel 5 — Taxe de séjour : elle se calcule toute seule.

Personnage : la directrice (demo.POSTES['conformite']), profil Responsable
(aite_hotel_management.group_hotel_manager) : c'est elle qui règle l'hôtel,
tient les barèmes et ouvre l'état mensuel, réservés à ce groupe
(aite_city_tax/views/menus.xml:5-17 ; security/ir.model.access.csv).
Applications de la barre MuK : ecrans.APPS_PROFIL['direction'] ; menus de
l'application Hôtel : ecrans.MENUS_MUK['hotel_direction'] (Activité par
pôle, Réception, Réservations, Espaces & Prestations, Notes de chambre en
attente, Facturation, Fidélité, Gouvernante, Configuration ; « Direction »
et « Front Desk » renommés à la livraison 4, hotel_menus.xml:18-22 et
aite_exec_dashboard). Menus déroulants : hotel_menus.xml (Réservations,
Facturation, Configuration), aite_city_tax/views/menus.xml,
aite_guest_registry/views/menus.xml:10-20, aite_housekeeping/views/
menus.xml:29-30 — inchangés à la livraison 4.

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

Écrans et libellés (relevés mot pour mot, livraison 4) :
1. Fiche hôtel — aite_hotel_management/views/hotel_hotel_views.xml:22-83
   (Identité, Code, Catégorie, Horaires standards, Coordonnées, Structure,
   Chambres vendables, onglet « Politique / informations » et son texte
   indicatif) ; models/hotel_hotel.py (libellés, « 3 ★ ») ; onglet ajouté
   par aite_city_tax/views/hotel_hotel_views.xml:11-42 (« Taxe de séjour »,
   « Réglage », « Pays (fiche hôtel) », « Catégorie (fiche hôtel) », « Ce
   qui s'applique », bandeau alert-info, texte gris dont le chemin
   « Hôtel → Configuration → Barèmes de taxe de séjour », :40-41) ;
   models/hotel_hotel.py:13-34 (« Collecter la taxe de séjour », « Barème
   appliqué », « Montant par nuitée », « Base ») et :79-83 (la phrase
   « Chaque séjour portera une ligne « Taxe de séjour » de 3 000 FCFA par
   personne et par nuit, hors TVA. », symbole de la devise ; milliers par
   une espace simple, .replace(",", " ")) ; models/city_tax_rate.py:28,
   :79-88 (libellé du barème calculé à l'affichage, pays traduit, symbole :
   « Cameroun — 3 ★ : 3 000 FCFA » ; res_currency_data.xml, XAF → symbole
   « FCFA »). L'anneau porte désormais sur le barème appliqué, qui dit à lui
   seul pays, étoiles et montant.
2. Barèmes — aite_city_tax/views/city_tax_rate_views.xml:4-56 (liste
   éditable, colonnes, regroupement par pays par défaut) ;
   models/city_tax_rate.py:21-70 (Pays, Catégorie, Montant par nuitée,
   Devise, Base de calcul, Compter les enfants, Référence légale) ;
   data/city_tax_data.xml:5-59 (barème Cameroun, références légales) et
   :3-215 (24 barèmes : 4 pays × 6 catégories) ; menu menus.xml:13-17. Plus
   de somme sur les lignes de regroupement (aggregator=None,
   city_tax_rate.py:42-48) ; la colonne Devise garde le nom de la devise
   (« XAF », many2one currency_id).
3. Réservation — aite_hotel_management/views/hotel_reservation_views.xml:
   42-160 (Confirmer, Annuler, Check-in, Encaisser un acompte, Envoyer la
   confirmation, « Non présenté » (:59-61), statusbar, bouton « Folio »,
   groupes Client / Séjour / Canal & commission / Occupation, onglets
   Chambres / Demandes particulières, colonnes des lignes dont « Prix
   fixé », optional="show" :145-146, corbeille et sélecteur de colonnes de
   la liste éditable ; « Hôtel » en lecture seule une fois confirmée,
   readonly="state != 'draft'", :95-97 : libellé non gras, valeur en lien) ;
   models/hotel_reservation.py:48-145, :612-636
   (libellés, états, « Téléphone / WhatsApp », « Prix fixé ») ;
   aite_guest_registry/views/hotel_reservation_views.xml:11-25 (bouton
   « Fiches d'enregistrement », 0/2) et :49-54 (bouton « Imprimer les
   fiches », icône d'impression). Confirmer crée le folio (sans l'ouvrir :
   la méthode renvoie True) puis la taxe : hotel_reservation.py:374-389 ;
   aite_city_tax/models/hotel_folio.py:95-99. Le bouton « Folio » affiche
   le solde (folio_amount_residual), resynchronisé à l'enregistrement
   (hotel_reservation.py:293-308) : il ne change qu'au clic, qui enregistre.
4. Folio — aite_hotel_management/views/hotel_folio_views.xml:31-160
   (Encaisser, Générer la facture, Annuler, Ouvert / Facturé / Soldé,
   Règlements, Séjour, Montants, Lignes du folio, colonnes, note grise) ;
   models/hotel_folio.py:253-276 (nuitée « Nuitée 201 (Confort) —
   26/10/2026 → 28/10/2026 », dates locales jj/mm/aaaa, et datée du jour
   d'arrivée, :275) ; lignes triées par date puis id (_order = 'date, id',
   :407) : la ligne de taxe, datée du jour de la synchronisation
   (aite_city_tax/models/hotel_folio.py:158), passe donc AVANT la nuitée,
   datée du 26/10 ; aite_city_tax/views/hotel_folio_views.xml:10-52 (« Taxe
   de séjour » dans Montants, « Recalculer la taxe de séjour », ligne
   orange, Qté / Prix / Libellé / Taxes en lecture seule) ;
   models/hotel_folio.py:28-44 (suppression refusée par le serveur : la
   corbeille reste affichée, rien ne la montre cliquée), :119-163 (une
   seule ligne, quantité, prix, aucune TVA, libellé « Taxe de séjour — 4
   nuitée(s) × personne (3 ★, Cameroun) », 'tax_ids': [(6, 0, [])]).
   Nuitée sans TVA, convention de la série (t01_reception.py, TOTAL_RESA ;
   t02_planning.py, commentaire « Convention de la série » ; t03_folio.py,
   docstring « Sans TVA sur l'article de nuitée » : aucun taux n'est livré
   par les modules, la TVA de la nuitée vient de l'article du type de
   chambre, hotel_folio.py:270-272) : Taxes 0 FCFA, TTC = HT.
   Aspect : captures/03_folio.png, ref_muk/029. Discussion sous la
   feuille (le folio hérite de mail.thread ; Odoo 18 la place sous la fiche
   à cette largeur d'écran) : « Envoyer message », « Note », « Activités »,
   « Suivre », message de création « %s créé » avec la description du
   modèle (« Folio client (note de séjour) », hotel_folio.py:27 ;
   odoo18/addons/mail/i18n/fr.po) ; daté « Aujourd'hui » / « Aujourd'hui à
   10:05 » le 20/10, « 20 oct. 2026 » / « 20 oct., 10:05 » le 22/10
   (mail/static/src/core/common/message_model.js:225-247).
5. Le séjour change — hotel_reservation.py:293-308 (dates modifiées sur une
   réservation confirmée → resynchronisation des nuitées puis de la taxe) ;
   tests/vague1/scenario_city_tax.py:103-109 (une nuit de plus : 6
   nuitées, 18 000 F, toujours une seule ligne) ; la ligne de taxe est
   réécrite, datée du 22/10 ; la nuitée garde sa date d'arrivée ; gel après
   facture : aite_city_tax/models/hotel_folio.py:128-131,
   scenario_city_tax.py:131-135.
6. État mensuel — aite_city_tax/views/city_tax_report_views.xml:4-101 :
   pivot regroupé par « checkout_date:month » × hôtel, « Nuitées taxées »,
   « Taxe collectée » ; l'action s'ouvre filtrée « Séjours terminés (à
   déclarer) » et regroupée « Date de départ » par mois (:87) ; filtres
   « Départs du mois », « Départs du mois dernier » | « Séjours terminés (à
   déclarer) », « Séjours en cours (prévision) » (deux groupes séparés par
   <separator/>, :65 : cochés ensemble, ils se cumulent en deux facettes) ;
   regroupements « Date de départ » (date : entrée dépliable, mois coché)
   et « Hôtel » ; nouvelle aide « Chaque mois, ajoutez le filtre « Départs
   du mois dernier » : le total Taxe collectée est le montant à déclarer
   et à reverser avant le 15 » (:93-98). models/city_tax_report.py:29-56
   (« Taxe collectée » en Float sans décimale : « 1 293 000 »).
   Cadre web d'Odoo 18 (odoo18/addons/web/static/src/search/
   search_model.js:1799-1801, facette `${description}: ${option}`, sans
   espace avant les deux-points : « Date de départ: Mois » ; ordre des
   facettes = ordre d'activation, _getGroups :2020 ; défauts dans l'ordre
   de la vue, :1227-1247 ; core/dropdown/accordion_item.xml ;
   web/i18n/fr.po : « Filtres », « Regrouper par », « Favoris », « Mois »,
   « Ajouter un filtre personnalisé », « Ajouter un groupe personnalisé »,
   « Enregistrer la recherche actuelle », « Mesures », « Nouveau »,
   « Ajouter une ligne »). Lignes du pivot au nom du mois (« octobre
   2026 », ecrans.mois_long).

Chiffres des résultats : 24 barèmes (city_tax_data.xml ; ROADMAP.md:63) ;
aucune saisie de la réception (aite_city_tax/__manifest__.py « Aucune
action de la réception » ; CLAUDE.md, règle d'intuitivité 3 ;
scenario_city_tax.py:80 ; formulée « 0 saisie de taxe à la confirmation »,
toujours vraie) ; une ligne par folio, hors TVA, recalculée, figée à la
facture (hotel_folio.py:119-163).

Captures de référence (modèle visuel, jamais incrustées) : ref_muk/040,
046, 029, 031, 027 ; captures/02, 02b, 03, 04, 05 ; captures prises en
lecture seule sur la base MuK (compte demo.direction) pour la mise en page
des en-têtes de fiche, du menu de recherche et des menus déroulants.

ÉCARTS corrigés à la livraison 4 et rejoués corrigés : barème en français
et en FCFA (n° 39 et 7, city_tax_rate.py:79-88) ; phrase de l'onglet en
FCFA (n° 7, hotel_hotel.py:79-83) ; chemin de menu exact dans le texte gris
(n° 46) ; plus de somme sur les regroupements des barèmes (n° 57) ; colonne
Taxes de la ligne de taxe en lecture seule et suppression refusée (n° 57,
sans effet visible ici) ; dates de la nuitée au format jj/mm/aaaa et nuitée
datée de l'arrivée (n° 37 et 56) ; « Fiches d'enregistrement » et
« Imprimer les fiches » (relecture de l'intégration), « Non présenté »
(n° 42) ; état mensuel : mois en toutes lettres (n° 4), montants sans
décimale (n° 40), ouverture sur « Séjours terminés (à déclarer) » et aide
réécrite (n° 48) — la vidéo ajoute donc le seul filtre « Départs du mois
dernier », comme le dit l'aide.

Rejoué tel quel (le code l'écrit ainsi) : « nuitée(s) » dans le libellé de
la ligne de taxe (aite_city_tax/models/hotel_folio.py:145) ; espace simple
et non insécable dans le barème et la phrase (format Python) ; secondes des
champs Arrivée / Départ de la réservation (pas de show_seconds sur le
formulaire).

LIMITES d'avant, levées : un hôtel créé avant l'installation d'aite_city_tax
retrouve son « Barème appliqué » (n° 73, city_tax_rate.py:98-137 et
migrations/18.0.1.0.2) ; l'article « Taxe de séjour — <hôtel> » est créé en
sudo() (n° 11, hotel_hotel.py:89-120). La révélation et la carte « 0 saisie
de taxe à la confirmation » restent telles quelles : elles sont vraies.

Données : demo.py (Complexe Hôtelier — Démo, Démo Hôtellerie SARL, postes,
Confort à 45 000 FCFA la nuit) ; quatre étages, du rez-de-chaussée au 3e
(harmonisation de la série : 4xx au 3e étage). Le séjour des étapes 3 à 5 est propre à ce
tutoriel (RESA_R…), pour laisser intact celui d'Estelle Ngono que suivent
les autres : Pélagie Ondobo (fictive, téléphone de la plage de fiction de
la série), RES/2026/0228, FOL/2026/0228 (numéro suivant FOL/2026/0226-0227,
créés le 16/10 au t04_note_chambre.py),
chambre 201 [CFT] (libre fin octobre au planning de t02_planning.py,
liste SEJOURS), 2 adultes, du 26 au 28/10/2026 puis au 29/10/2026 ; confirmée
le 20/10/2026 par la directrice, qui tient l'écran. État mensuel ouvert le
mois suivant (début novembre) : chiffres fictifs, cohérents avec un 3 ★ à
3 000 F l'unité ; août et septembre repris du chapitre 7 de la présentation
(scenarios/c7_conformite.py) ; octobre entièrement facturé ; quelques
départs de début novembre déjà facturés.
"""

import demo
from ecrans import (APPS_PROFIL, ICONES, MENUS_MUK, _id, bouton, date_fr, deux_colonnes, e, entier, fcfa, fenetre_muk,
                    groupe, icone, mois_long, navigateur, statusbar, titre_fiche, vue_fiche, vue_libre)
from marketing import bulle, dezoom, reaction, zoom
from moteur import anneau, cacher, clic, classe, curseur, defiler, montrer, pause, saisir, texte, vue

NOM, ROLE = demo.POSTES['conformite']
MENUS = MENUS_MUK['hotel_direction']

# Le séjour de ce tutoriel : une réservation fictive propre à t05, pour laisser intact celui
# d'Estelle Ngono (demo.py) que suivent t01, t02, t03, t06, t07 et t11. Confirmée par la
# directrice le 20/10/2026, prolongée d'une nuit le 22/10/2026 ; départ en octobre, donc
# compté dans l'état d'octobre de l'étape 6.
RESA_R, FOLIO_R = 'RES/2026/0228', 'FOL/2026/0228'
CLIENT_R, TEL_R, MAIL_R = 'Pélagie Ondobo', '+237 6 00 00 00 64', 'pelagie.ondobo@exemple.cm'
ARRIVEE_R, DEPART_R, CHAMBRE_R = '26/10/2026 14:00:00', '28/10/2026 12:00:00', '201 [CFT]'
# Taxe de séjour 3 ★ Cameroun : 3 000 FCFA par personne et par nuit (city_tax_data.xml).
TAUX = 3000
# Libellé du barème et phrase de l'onglet : milliers par une espace simple (format Python,
# city_tax_rate.py:83-88, hotel_hotel.py:79-83), symbole de la devise.
TAUX_TXT = '{:,}'.format(TAUX).replace(',', ' ')


def sejour(nuits, depart, jour):
    """Les montants du séjour pour ``nuits`` nuits, 2 adultes, synchronisés le ``jour`` (AAAA-MM-JJ).
    Nuitée Confort à 45 000 FCFA (demo.PRIX_NUIT) sans TVA, convention de la série (t01_reception.py
    TOTAL_RESA, t02_planning.py, t03_folio.py, chapitre 1 de la présentation). La nuitée est datée de
    l'arrivée (hotel_folio.py:275), la ligne de taxe du jour de la synchronisation (aite_city_tax/
    models/hotel_folio.py:158) ; libellé de la nuitée en dates locales jj/mm/aaaa (hotel_folio.py:263-267)."""
    heb, unites = 45000 * nuits, 2 * nuits
    taxe = TAUX * unites
    return {'nuits': str(nuits), 'dep': '%s 12:00:00' % date_fr(depart), 'heb': fcfa(heb),
            'qte_n': '%d,00' % nuits, 'ttc_n': fcfa(heb), 'taxe': fcfa(taxe), 'qte_t': '%d,00' % unites,
            'ht': fcfa(heb + taxe), 'tva': fcfa(0), 'ttc': fcfa(heb + taxe),
            'lib_n': 'Nuitée 201 (Confort) — %s → %s' % (date_fr('2026-10-26'), date_fr(depart)),
            'lib_t': 'Taxe de séjour — %d nuitée(s) × personne (3 ★, Cameroun)' % unites,
            'date_n': date_fr('2026-10-26'), 'date_t': date_fr(jour)}


# Deux nuits (confirmée le 20/10), puis trois (prolongée le 22/10).
AVANT = sejour(2, '2026-10-28', '2026-10-20')
APRES = sejour(3, '2026-10-29', '2026-10-22')
assert (AVANT['ttc'], APRES['taxe'], APRES['lib_n']) == (fcfa(102000), fcfa(18000),
                                                        'Nuitée 201 (Confort) — 26/10/2026 → 29/10/2026')
assert AVANT['dep'] == DEPART_R

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


def ch(libelle, valeur, ident=None, aide_=False, gras=False, lien=False, saisie=False, html=False, ident_l=None):
    """Un champ de fiche : libellé (gras s'il est modifiable), valeur ; ``saisie`` souligne un champ éditable ;
    ``ident_l`` : l'id du libellé, pour le passer en lecture seule."""
    l = aide(libelle) if aide_ else e(libelle)
    v = valeur if html else e(valeur)
    classes = 'v' + (' lien' if lien else '') + (' t05-saisie' if saisie else '')
    return ('<div class="ch"><span class="l%s"%s>%s</span><span class="%s"%s>%s</span></div>'
            % (' gras' if gras else '', _id(ident_l), l, classes, _id(ident), v))


def facette(libelle, ico, ident=None):
    return ('<span class="facette"%s><span class="fic">%s</span><span class="ell">%s</span><span class="fx">×</span></span>'
            % (_id(ident), ico, e(libelle)))


def recherche(facettes, ident=None, toggler=None, deux_lignes=False):
    """La barre de recherche ; ``deux_lignes`` : les facettes ne tiennent plus avec la saisie, qui passe à la
    ligne (o_searchview_input_container « d-flex flex-wrap », web/static/src/search/search_bar/search_bar.xml:118) :
    la barre, et avec elle le panneau de contrôle, grandit."""
    if deux_lignes:
        return ('<div class="recherche t05-r2"%s>%s<div class="t05-r2-in">%s<span class="ph">Rechercher…</span></div>'
                '<span class="deroule"%s>▾</span></div>'
                % (_id(ident), icone('loupe', 'loupe'), ''.join(facettes), _id(toggler)))
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


def discussion(ident, auteur, quand, jour, message):
    """La discussion d'Odoo 18 sous la fiche : boutons, séparateur de date (``<ident>-jour``), un message daté
    (``<ident>-quand``)."""
    return ('<div class="t05-chatter"><div class="t05-ch-bts"><span class="bt primaire">%sEnvoyer message</span>'
            '<span class="bt gris">Note</span><span class="bt gris">%sActivités</span>'
            '<span class="t05-ch-droite">%s<span>Suivre</span></span></div>'
            '<div class="t05-ch-sep"><span id="%s-jour">%s</span></div><div class="ch-msg"><span class="ch-av">%s</span>'
            '<div><div class="ch-a"><b>%s</b> <small id="%s-quand">%s</small></div><div class="ch-t">%s</div></div></div>'
            '</div>'
            % (icone('message'), icone('horloge'), icone('loupe', 'ico'), ident, e(jour), e(auteur[0]), e(auteur), ident,
               e(quand), e(message)))


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
                             ch('Téléphone', '+237 6 00 00 00 10', gras=True, saisie=True),
                             ch('E-mail', '', gras=True, saisie=True), ch('Site web', '', gras=True, saisie=True)]))
# Les quatre étages de la série (101-107 au rez-de-chaussée, 2xx au 1er, 3xx au 2e, 4xx au 3e : t02_planning.py,
# t07_gouvernante.py).
ETAGES = ''.join('<div class="t05-etage"><span class="t05-poignee">⠿</span><span>%s</span>%s</div>'
                 % (n, icone('corbeille', 't05-corb'))
                 for n in ('Rez-de-chaussée', '1er étage', '2e étage', '3e étage'))
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
                    groupe("Ce qui s'applique", [ch('Barème appliqué',
                                                    'Cameroun — %s : %s FCFA' % (demo.ETOILES, TAUX_TXT),
                                                    't05-h-bareme', aide_=True),
                                                 ch('Montant par nuitée', entier(TAUX), 't05-h-mt', aide_=True),
                                                 ch('Base', 'Par personne et par nuit', aide_=True)]))
    + ('<div class="alerte-info t05-alerte" id="t05-h-phrase"><b class="t05-i">i</b>Chaque séjour portera une ligne '
       '« Taxe de séjour » de %s FCFA par personne et par nuit, hors TVA.<span class="t05-ancre" id="t05-h-ancre">'
       '</span></div>' % TAUX_TXT)
    + '<div class="note-pied t05-gris" id="t05-h-aide">La taxe est ajoutée automatiquement à chaque folio et recalculée si '
      'les dates, les chambres ou le nombre de personnes changent. Elle n\'entre pas dans la base de la TVA. Pour modifier '
      'un montant (nouvelle loi de finances) : <b>Hôtel → Configuration → Barèmes de taxe de séjour</b>.</div></div>')
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


def groupe_b(ident, pays, n, ouvert=False):
    """Une ligne de regroupement par pays : « Cameroun (6) », sans somme du montant par nuitée
    (aggregator=None, city_tax_rate.py:42-48, ECARTS n° 57)."""
    return ('<div class="ligne t05-grp"%s style="grid-template-columns:%s"><span class="t05-caret">%s</span>'
            '<span class="t05-grp-l">%s (%d)</span></div>'
            % (_id(ident), GAB_B, '▾' if ouvert else '▸', e(pays), n))


def ligne_b(ident, cat, montant, ref):
    return ('<div class="ligne" id="%s" style="grid-template-columns:%s"><span class="cb"></span><span>Cameroun</span>'
            '<span class="ell">%s</span><span class="d" id="%s-mt">%s</span><span>XAF</span>'
            '<span class="ell">Par personne et par nuit</span><span>%s</span><span class="ell" id="%s-ref">%s</span>'
            '<span></span></div>' % (ident, GAB_B, e(cat), ident, entier(montant), case(False), ident, e(ref)))


AUTRES = ['Côte d\'Ivoire', 'Guinée', 'Sénégal']
FERME = (groupe_b('t05-g-cm', 'Cameroun', 6)
         + ''.join(groupe_b(None, p, 6) for p in AUTRES))
OUVERT = (groupe_b(None, 'Cameroun', 6, ouvert=True)
          + ''.join(ligne_b('t05-b%d' % i, c, m, REF_CM0 if c.startswith('Non') else REF_CM)
                    for i, (c, m) in enumerate([('5 ★', 5000), ('4 ★', 4000), ('3 ★', TAUX), ('2 ★', 1000),
                                                ('1 ★', 500), ('Non classé / meublé', 500)], 1))
          + '<div class="ligne t05-ajout-l" style="grid-template-columns:%s"><span></span><span class="t05-lien">'
            'Ajouter une ligne</span></div>' % GAB_B
          + ''.join(groupe_b(None, p, 6) for p in AUTRES))
CP_BAREMES = ('<div class="cp"><span class="bt primaire">Nouveau</span><span class="titre">Barèmes de taxe de séjour'
              '<span class="t05-rouage">%s</span></span>%s<span class="pager">1-4 / 4</span>'
              '<span class="t05-fleches"><i>‹</i><i>›</i></span></div>'
              % (ROUAGE, recherche([facette('Pays', COUCHES)])))
BAREMES = vue_libre('t05-baremes', CP_BAREMES + '<div class="liste t05-liste">%s<div class="pile">'
                    '<div id="t05-bar-ferme">%s</div><div class="masque" id="t05-bar-ouvert">%s</div></div></div>'
                    % (TETE_B, FERME, OUVERT))

# ------------------------------------------------------------ réservation --
# Réservations → RES/2026/0228 : en brouillon, puis confirmée d'un clic.
R_STATS = (stat('t05-r-st-folio', 'document', 'Folio', AVANT['ttc'])
           + stat('t05-r-st-fiches', 'fiche', "Fiches d'enregistrement", '0/2'))
DEPART = ('<span class="t05-champ" id="t05-r-dep"><span class="ph" id="t05-r-dep-ph"></span>'
          '<span class="val" id="t05-r-dep-val">%s</span></span>' % e(DEPART_R))
FEUILLE_RESA = (
    titre_fiche(RESA_R)
    + deux_colonnes(
        groupe('Client', [ch('Client', CLIENT_R, gras=True, saisie=True), ch('Téléphone', TEL_R),
                          ch('E-mail', MAIL_R),
                          ch('Hôtel', demo.HOTEL, 't05-r-hotel', gras=True, saisie=True, ident_l='t05-r-hotel-l')])
        + groupe('Canal & commission', [ch('Canal', 'Téléphone / WhatsApp', gras=True, saisie=True)]),
        groupe('Séjour', [ch('Arrivée', ARRIVEE_R, gras=True, saisie=True),
                          ch('Départ', DEPART, gras=True, html=True),
                          ch('Nuits', AVANT['nuits'], 't05-r-nuits', aide_=True),
                          ch('Total hébergement (HT)', AVANT['heb'], 't05-r-total')])
        + groupe('Occupation', [ch('Nb chambres', '1'), ch('Adultes', '2'), ch('Enfants', '0')], 't05-r-occ'))
    + '<div class="onglets"><span class="onglet actif">Chambres</span><span class="onglet">Demandes particulières</span></div>'
    # Liste éditable des chambres : « Prix fixé » (price_locked, optional="show") entre « Prix / nuit » et
    # « Sous-total (HT) », bouton « Changer de chambre » (⇄), corbeille, sélecteur des colonnes (⇋).
    + '<div class="table t05-table"><div class="t-tete" style="grid-template-columns:%s"><span>Type</span>'
      '<span>Chambre</span><span class="d">Adultes</span><span class="d">Enfants</span><span>Occupants</span>'
      '<span class="d">Nuits</span><span class="d">Prix / nuit</span><span class="ell">Prix fixé</span>'
      '<span class="d">Sous-total (HT)</span><span></span><span class="t05-opt">⇋</span>'
      '</div><div class="t-ligne" style="grid-template-columns:%s"><span>%s</span><span>%s</span><span class="d">2</span>'
      '<span class="d">0</span><span></span><span class="d" id="t05-r-l-nuits">2</span><span class="d">%s</span>'
      '<span>%s</span><span class="d" id="t05-r-l-st">%s</span><span class="t05-ech">⇄</span>'
      '<span class="t05-corb2">%s</span></div>'
      '<div class="t-ajout">Ajouter une ligne</div></div>'
      % (('1fr 150px 104px 104px 150px 80px 160px 118px 190px 34px 30px',) * 2
         + (demo.TYPE, CHAMBRE_R, fcfa(45000), case(False), AVANT['heb'], ICONES['corbeille'])))
B_BROUILLON = [bouton('t05-r-confirmer', 'Confirmer', 'primaire'), bouton(None, 'Annuler')]
B_CONFIRMEE = [bouton(None, 'Check-in', 'primaire'), bouton(None, 'Encaisser un acompte'),
               bouton(None, 'Envoyer la confirmation'), bouton(None, 'Imprimer les fiches', ico='imprimer'),
               bouton(None, 'Non présenté'), bouton(None, 'Annuler')]
RESA = vue_fiche('t05-resa', cp_fiche('Réservations', RESA_R, R_STATS, '4 / 18', 't05-r-stats', stats_masque=True),
                 B_BROUILLON, statusbar('t05-r-sb', ['Brouillon', 'Confirmée', 'Arrivé', 'Parti'], 0), FEUILLE_RESA,
                 boutons_apres=[B_CONFIRMEE])

# ------------------------------------------------------------ folio --
# Bouton « Folio » de la réservation → FOL/2026/0228 ; la ligne de taxe est en orange.
GAB_F = '110px 150px 74px 1fr 52px 120px 84px 134px 126px 22px'


def ligne_f(ident, valeurs, nuitee):
    badge = ('<span class="puce info">Nuitée</span>' if nuitee
             else '<span class="puce orange">Taxe de séjour</span>')
    taxe = ''                     # aucune TVA, ni sur la nuitée (convention de la série) ni sur la taxe
    k = 'n' if nuitee else 't'
    return ('<div class="t-ligne %s" id="%s" style="grid-template-columns:%s"><span id="%s-date">%s</span>'
            '<span>%s</span><span></span><span class="ell" id="%s-lib">%s</span><span class="d" id="%s-qte">%s</span>'
            '<span class="d">%s</span><span id="%s-taxes">%s</span><span class="d" id="%s-st">%s</span>'
            '<span class="d" id="%s-ttc">%s</span><span class="t05-corb2">%s</span></div>'
            % ('t05-nuitee' if nuitee else 't05-taxe', ident, GAB_F, ident, valeurs['date_' + k], badge, ident,
               valeurs['lib_' + k], ident, valeurs['qte_' + k], fcfa(45000 if nuitee else TAUX), ident, taxe,
               ident, valeurs['heb'] if nuitee else valeurs['taxe'], ident,
               valeurs['ttc_n'] if nuitee else valeurs['taxe'], ICONES['corbeille']))


# Lignes triées par date puis id (_order = 'date, id', hotel_folio.py:407) : la taxe, datée du jour de la
# synchronisation, passe avant la nuitée, datée de l'arrivée (26/10).
LIGNES_F = ('<div class="table t05-table t05-lignes"><div class="t-tete" style="grid-template-columns:%s"><span>Date</span>'
            '<span>Type</span><span>Service</span><span>Libellé</span><span class="d">Qté</span>'
            '<span class="d">Prix unitaire</span><span>Taxes</span><span class="d ell">Sous-total (HT)</span>'
            '<span class="d">Total (TTC)</span><span class="t05-opt">⇋</span></div>%s%s'
            '<div class="t-ajout">Ajouter une ligne</div><div class="t-total" style="grid-template-columns:%s">'
            '<span></span><span></span><span></span><span></span><span></span><span></span><span></span>'
            '<span class="d" id="t05-f-tot-ht">%s</span><span class="d" id="t05-f-tot-ttc">%s</span><span></span></div>'
            '</div>' % (GAB_F, ligne_f('t05-f-l2', AVANT, False), ligne_f('t05-f-l1', AVANT, True), GAB_F, AVANT['ht'],
                        AVANT['ttc']))
FEUILLE_FOLIO = (
    titre_fiche(FOLIO_R)
    + deux_colonnes(
        groupe('Séjour', [ch('Client', CLIENT_R, lien=True), ch('Réservation', RESA_R, lien=True),
                          ch('Séjour', 'Confirmée'), ch('Arrivée', ARRIVEE_R),
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
# (« Folio client (note de séjour) », hotel_folio.py:27), signé par qui a confirmé. Le 20/10, jour de la
# confirmation, Odoo date le message du jour même : séparateur « Aujourd'hui » et « Aujourd'hui à 10:05 »
# (mail/static/src/core/common/message_model.js:225-247, dateDay et dateSimpleWithDay ; mail/i18n/fr.po :
# « Today » → « Aujourd'hui », « Today at %(time)s » → « Aujourd'hui à %(time)s ») ; rouvert le 22/10
# (étape 5) : « 20 oct. 2026 » et « 20 oct., 10:05 » (DATE_MED, et DATETIME_MED sans l'année).
FOLIO = fiche('t05-folio', cp_fiche('Réservations / <span id="t05-f-fil">%s</span>' % e(RESA_R), FOLIO_R,
                                    stat('t05-f-st', 'billet', 'Règlements', '0'), '1 / 1'),
              [bouton(None, 'Encaisser', 'primaire'), bouton(None, 'Générer la facture'),
               bouton(None, 'Recalculer la taxe de séjour', 'lien'), bouton(None, 'Annuler')],
              statusbar('t05-f-sb', ['Ouvert', 'Facturé', 'Soldé'], 0), FEUILLE_FOLIO,
              discussion('t05-f-ch', NOM, "Aujourd'hui à 10:05", "Aujourd'hui", 'Folio client (note de séjour) créé'))

# ------------------------------------------------------------ état mensuel --
# Hôtel → Facturation → Taxe de séjour : pivot mois de départ × hôtel. L'action s'ouvre filtrée
# « Séjours terminés (à déclarer) » et regroupée « Date de départ » par mois (city_tax_report_views.xml:87) ;
# lignes au nom du mois (« octobre 2026 »), montants sans décimale (Float digits=(16, 0)).
ENTETES = ('<tr><td class="vide"></td><th colspan="2">⊟ Total</th></tr>'
           '<tr><td class="vide"></td><th colspan="2">⊞ %s</th></tr>'
           '<tr><td class="vide"></td><th class="m">Nuitées taxées</th><th class="m">Taxe collectée</th></tr>'
           % e(demo.HOTEL))


def pivot(ident, lignes):
    """Un pivot : une ligne par mois de départ (mois, nuitées taxées), puis le total."""
    corps = ''.join('<tr id="%s-%d"><td class="r n2">⊞ %s</td><td>%s</td><td>%s</td></tr>'
                    % (ident, i, e(mois_long(m, 2026)), entier(n), entier(n * TAUX)) for i, (m, n) in enumerate(lignes))
    total = sum(n for _, n in lignes)
    return ('<table class="pv t05-pv" id="%s">%s<tr class="tot" id="%s-tot"><td class="r">⊟ Total</td><td>%s</td>'
            '<td>%s</td></tr>%s</table>' % (ident, ENTETES, ident, entier(total), entier(total * TAUX), corps))


# Séjours terminés (facturés ou soldés), par mois de départ, au début de novembre : août et septembre
# repris du chapitre 7 ; octobre entièrement facturé (dont Pélagie Ondobo) ; premiers départs de novembre.
MOIS = [(8, 347), (9, 408), (10, 431), (11, 26)]
# Le panneau de recherche, sous la barre : 74 px du haut de la vue, et plus bas quand la barre passe sur
# deux lignes (panneau de contrôle de 80 à 118 px, barre de 50 à 90 px).
T05_MENU_B = 74 + 39


def coche(texte_, ident=None, accordeon=False):
    """Une entrée cochée du panneau de recherche ; ``accordeon`` : un regroupement par date, qui se déplie
    sur Année / Trimestre / Mois / Semaine / Jour (core/dropdown/accordion_item.xml)."""
    return ('<div class="t05-coche%s"%s>%s%s</div>'
            % (' t05-acc' if accordeon else '', _id(ident), e(texte_), '<i>▾</i>' if accordeon else ''))


def menu_recherche(ident, dernier=False, haut=None):
    """Le panneau Filtres / Regrouper par / Favoris, ouvert sous la barre ; ``dernier`` : « Départs du mois
    dernier » coché ; ``haut`` : le panneau suit la barre quand elle grandit."""
    return (
        '<div class="t05-rmenu masque" id="%s"%s data-layout-allow-overlap data-layout-allow-occlusion>'
        '<div class="t05-rcol"><div class="t05-rtitre">%sFiltres</div><div>Départs du mois</div>%s<hr>%s'
        '<div>Séjours en cours (prévision)</div><hr><div>Ajouter un filtre personnalisé</div></div>'
        '<div class="t05-rcol"><div class="t05-rtitre">%sRegrouper par</div>%s'
        '<div>Hôtel</div><hr><div>Ajouter un groupe personnalisé ▾</div></div>'
        '<div class="t05-rcol"><div class="t05-rtitre">%sFavoris</div><div>Enregistrer la recherche actuelle ▾</div></div>'
        '</div>' % (ident, ' style="top:%dpx"' % haut if haut else '', icone('filtre', 't05-ri t05-ri-f'),
                    coche('Départs du mois dernier', '%s-dernier' % ident) if dernier
                    else '<div id="%s-dernier">Départs du mois dernier</div>' % ident,
                    coche('Séjours terminés (à déclarer)'), '<span class="t05-ri t05-ri-c">%s</span>' % COUCHES,
                    coche('Date de départ', accordeon=True), icone('etoile', 't05-ri')))


def cp_etat(facettes, toggler=None, deux_lignes=False):
    return ('<div class="cp%s"><span class="titre t05-titre-pv">Taxe de séjour — état mensuel</span>'
            '<div class="t05-rpile">%s</div>'
            '<span class="t05-vues"><span class="actif">%s</span><span>%s</span><span>%s</span></span></div>'
            % (' t05-cp2' if deux_lignes else '', recherche(facettes, toggler=toggler, deux_lignes=deux_lignes),
               V_PIVOT, V_LISTE, V_GRAPHE))


def barre_pivot(export=None):
    return ('<div class="pv-barre"><span class="bt primaire">Mesures ▾</span><span class="bt gris">⇄</span>'
            '<span class="bt gris">✥</span><span class="bt gris t05-dl"%s>%s</span></div>' % (_id(export), TELECHARGER))


# Facettes dans l'ordre d'activation (search_model.js:2020) ; regroupement par date écrit
# « ${description}: ${option} », sans espace avant les deux-points (:1801).
F_TERMINES = facette('Séjours terminés (à déclarer)', ICONES['filtre'], 't05-e-fac-term')
F_MOIS = facette('Date de départ: Mois', COUCHES)
# Deux états complets de l'écran, superposés : à l'ouverture (deux facettes, quatre mois), puis avec
# « Départs du mois dernier » (trois facettes sur une barre de deux lignes, octobre seul).
ETAT_A = cp_etat([F_TERMINES, F_MOIS], toggler='t05-e-toggler') + barre_pivot() + pivot('t05-e-a', MOIS)
ETAT_B = (cp_etat([facette('Séjours terminés (à déclarer)', ICONES['filtre']), facette('Date de départ: Mois', COUCHES),
                   facette('Départs du mois dernier', ICONES['filtre'], 't05-e-fac-dernier')], deux_lignes=True)
          + barre_pivot('t05-e-export') + pivot('t05-e-b', MOIS[2:3]))
ETAT = vue_libre('t05-etat', '<div class="pile t05-epile"><div class="t05-etat-s" id="t05-e-sa">%s</div>'
                             '<div class="t05-etat-s masque" id="t05-e-sb">%s</div></div>' % (ETAT_A, ETAT_B)
                 + menu_recherche('t05-e-menu') + menu_recherche('t05-e-menu-b', dernier=True, haut=T05_MENU_B))

# ------------------------------------------------------- menus déroulants --
# Les sous-menus de la barre (load_menus du compte demo.direction), posés sous leur menu (bord gauche du
# bouton, soit 8 à 9 px avant le libellé, mesuré sur la barre MENUS_MUK['hotel_direction']) ; celui de
# « Configuration » s'aligne sur le bord droit de la fenêtre, comme le fait Odoo quand la place manque.
def deroule(ident, gauche, items):
    return ('<div class="t05-deroule masque" id="%s" style="left:%dpx" data-layout-allow-overlap '
            'data-layout-allow-occlusion>%s</div>'
            % (ident, gauche, ''.join('<div%s>%s</div>' % (_id(i), e(t)) for i, t in items)))


DEROULES = (
    deroule('t05-dd-resa', 415, [('t05-dd-resa-res', 'Réservations'), (None, 'Planning des chambres')])
    + deroule('t05-dd-fact', 1071, [(None, 'Folios'), (None, 'Règlements'), ('t05-dd-fact-taxe', 'Taxe de séjour'),
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
    """Le folio relu après la prolongation, le 22/10 : chaque montant suit ; la nuitée garde sa date d'arrivée,
    la ligne de taxe prend celle du jour ; le message de création, d'avant-hier, n'est plus « Aujourd'hui »."""
    return [texte('#t05-f-ch-jour', '20 oct. 2026', avec=True), texte('#t05-f-ch-quand', '20 oct., 10:05', avec=True)] + [
        texte(s, v[k], avec=True) for s, k in (
        ('#t05-f-dep', 'dep'), ('#t05-f-heb', 'heb'), ('#t05-f-taxe', 'taxe'), ('#t05-f-ht', 'ht'), ('#t05-f-tva', 'tva'),
        ('#t05-f-ttc', 'ttc'), ('#t05-f-solde', 'ttc'), ('#t05-f-l1-lib', 'lib_n'),
        ('#t05-f-l1-qte', 'qte_n'), ('#t05-f-l1-st', 'heb'), ('#t05-f-l1-ttc', 'ttc_n'), ('#t05-f-l2-date', 'date_t'),
        ('#t05-f-l2-lib', 'lib_t'), ('#t05-f-l2-qte', 'qte_t'), ('#t05-f-l2-st', 'taxe'), ('#t05-f-l2-ttc', 'taxe'),
        ('#t05-f-tot-ht', 'ht'), ('#t05-f-tot-ttc', 'ttc'))]


CSS = """
/* barre MuK : neuf menus depuis « Activité par pôle » ; l'écart de 17 px les fait tenir sans écraser la grille */
#app-t05 .o-haut { gap: 17px; }
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
/* point d'ancrage de la bulle de l'étape 1 : sous la phrase, sur le texte gris (rien n'y est désigné) */
#t05-h-phrase { position: relative; }
.t05-ancre { position: absolute; left: 40%; bottom: 0; width: 2px; height: 2px; }
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
/* la barre de recherche la plus large que permet le panneau ; le menu s'aligne sur son bord droit */
.t05-rpile { margin-left: 8px; flex: none; }
.t05-rpile .recherche { margin-left: 0; width: 950px; }
.t05-rpile .facette { flex: none; max-width: none; }
.t05-rpile .ph { overflow: hidden; white-space: nowrap; }
/* trois facettes : la saisie passe à la ligne, la barre et le panneau de contrôle grandissent */
#t05-etat .cp.t05-cp2 { height: 118px; }
.t05-rpile .recherche.t05-r2 { height: auto; align-items: flex-start; padding: 7px 56px 7px 12px; }
.t05-r2 .loupe { margin-top: 6px; flex: none; }
.t05-r2-in { display: flex; flex-wrap: wrap; gap: 6px; flex: 1; min-width: 0; }
.t05-r2-in .ph { height: 34px; display: flex; align-items: center; padding-left: 4px; }
.t05-vues { margin-left: auto; display: flex; flex: none; }
.t05-vues span { width: 52px; height: 44px; display: flex; align-items: center; justify-content: center; background: #E9ECEF;
  color: #343A40; border: 1px solid #DEE2E6; }
.t05-vues span.actif { background: #DCE6EC; border-color: var(--muk-prim); }
.t05-vues svg { width: 22px; height: 22px; }
.t05-dl { width: 52px; justify-content: center; padding: 0; }
.t05-dl svg { width: 22px; height: 22px; }
.t05-pv { font-size: 20px; }
.t05-pv td, .t05-pv th { height: 50px; padding: 0 18px; }
/* le panneau prend la largeur de ses trois colonnes et s'aligne sur le bord droit de la barre (1 360 px du
   bord gauche de la vue, soit 184 px de son bord droit) */
.t05-rmenu { position: absolute; top: 74px; right: 184px; z-index: 30; background: #fff;
  border: 1px solid rgba(0,0,0,.15); border-radius: 4px; box-shadow: 0 10px 28px rgba(0,0,0,.18); padding: 18px 0;
  display: grid; grid-template-columns: repeat(3, minmax(320px, max-content)); color: var(--o-texte); font-size: 19px; }
.t05-rcol { padding: 0 22px; border-right: 1px solid #DEE2E6; }
.t05-rcol:last-child { border-right: 0; }
.t05-rcol > div { height: 40px; display: flex; align-items: center; padding-left: 32px; white-space: nowrap; }
.t05-rcol > div.t05-rtitre { padding-left: 0; font-size: 21px; font-weight: 600; gap: 10px; margin-bottom: 4px; }
.t05-rcol > div.t05-coche { font-weight: 600; position: relative; }
.t05-rcol > div.t05-coche::before { content: '✓'; position: absolute; left: 8px; color: var(--muk-prim); }
/* regroupement par date : entrée dépliable (accordion_item.scss, flèche à droite) */
.t05-rcol > div.t05-acc i { margin-left: auto; font-style: normal; font-size: 15px; color: #495057; padding-right: 4px; }
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
        'promesse': "Le pays et les étoiles de l'hôtel choisissent le barème : la taxe s'ajoute seule à chaque "
                    "folio, hors TVA, et l'état du mois est prêt à déclarer.",
        'voix': "Avec Aïte haousse, la taxe de séjour se règle sur la fiche de l'hôtel, puis se calcule toute seule.",
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
         # Les onglets sont sous le bord de l'écran (quatre étages dans Structure) : on descend d'abord.
         'gestes': [pause(0.4), anneau('#t05-h-cat', d=1.0), anneau('#t05-h-pays', d=1.0),
                    defiler('#t05-hotel-defil', -427, d=0.9), clic('#t05-h-ong-taxe'),
                    classe('#t05-h-ong-pol', retirer=['actif']), classe('#t05-h-ong-taxe', ajouter=['actif'], avec=True),
                    cacher('#t05-h-pol', d=0.15), montrer('#t05-h-taxe', d=0.35, y=10), anneau('#t05-h-bareme', d=1.3),
                    curseur('#t05-h-phrase', fx=0.96, fy=0.6, d=0.5), anneau('#t05-h-phrase', d=1.2),
                    bulle('b-phrase', '#t05-h-ancre', cote='bas', d=3.4), pause(3.4)]},
        {'temps': 0, 'titre': 'Les barèmes, déjà là', 'texte': 'Quatre pays, six catégories, une référence par barème.',
         'voix': "Les barèmes sont déjà là : Cameroun, Côte d'Ivoire, Sénégal et Guinée, chacun avec sa référence. "
                 "Une loi de finances change un montant ? On le corrige dans la liste, sans programmeur.",
         'gestes': aller('Configuration', 'Configuration', 't05-dd-conf', '#t05-dd-conf-bar')
         + [vue('t05-baremes'), pause(0.4), clic('#t05-g-cm', fx=0.1), cacher('#t05-bar-ferme', d=0.15),
            montrer('#t05-bar-ouvert', d=0.3, y=0), anneau('#t05-b3', d=1.3),
            bulle('b-loi', '#t05-b3-mt', cote='bas', d=2.6), pause(1.6), anneau('#t05-b3-ref', d=1.2)]},
        {'temps': 1, 'titre': 'Un clic sur Confirmer', 'texte': 'Rien à saisir pour la taxe : le folio est créé aussitôt, taxe comprise.',
         'voix': "Pour l'équipe, rien à saisir pour la taxe. La réservation de Pélagie Ondobo, deux nuits pour deux "
                 "adultes, se confirme d'un clic, et le folio est créé aussitôt, taxe comprise.",
         'gestes': aller('Configuration', 'Réservations', 't05-dd-resa', '#t05-dd-resa-res')
         + [vue('t05-resa'), pause(0.4), anneau('#t05-r-occ', d=1.2),
            bulle('b-zero', '#t05-resa-ga', cote='droite', d=2.4), pause(1.0), clic('#t05-r-confirmer'),
            classe('#t05-r-sb-0', retirer=['actif']), classe('#t05-r-sb-1', ajouter=['actif']),
            # Confirmée : l'hôtel n'est plus modifiable (readonly="state != 'draft'", hotel_reservation_views.xml:
            # 95-97) : libellé en graisse normale (o_form_label_readonly), valeur en lien (many2one en lecture).
            classe('#t05-r-hotel-l', retirer=['gras'], avec=True),
            classe('#t05-r-hotel', ajouter=['lien'], retirer=['t05-saisie'], avec=True),
            cacher('#t05-resa-ga', d=0.2), montrer('#t05-resa-gb', d=0.3, y=0), montrer('#t05-r-stats', d=0.4, y=0),
            anneau('#t05-r-st-folio', d=1.4)]},
        {'temps': 1, 'titre': 'La ligne Taxe de séjour', 'texte': 'Ajoutée seule au folio : 4 nuitées × %s, sans TVA.' % fcfa(TAUX),
         'voix': "Dans le folio, la ligne Taxe de séjour est apparue toute seule : quatre nuitées à trois mille francs, "
                 "douze mille francs. Elle ne porte aucune TVA : la taxe reste hors de la base.",
         'gestes': [clic('#t05-r-st-folio'), vue('t05-folio'), pause(0.4), anneau('#t05-f-taxe', d=1.1),
                    defiler('#t05-folio-defil', -470, d=0.8), curseur('#t05-f-l2-taxes', fx=0.3, d=0.5),
                    zoom('#t05-f-l2', s=1.4, fx=0.56, d=0.8),
                    bulle('b-tva', '#t05-f-l2-lib', cote='haut', d=2.6), pause(2.2), dezoom(d=0.6),
                    anneau('#t05-f-l2-ttc', d=1.0)]},
        {'temps': 1, 'titre': 'Le séjour change, la taxe suit', 'texte': 'Une nuit de plus : 6 nuitées, %s.' % APRES['taxe'],
         'voix': "Pélagie appelle : elle restera une nuit de plus. On repousse simplement sa date de départ : dans le "
                 "folio, la ligne passe à six nuitées, dix-huit mille francs, sans rien retoucher. Une fois le folio "
                 "facturé, elle ne bougera plus.",
         'gestes': [clic('#t05-f-fil', d=0.6), vue('t05-resa'), pause(0.3), clic('#t05-r-dep', fx=0.3, d=0.5),
                    saisir('t05-r-dep', APRES['dep'], d=1.0), texte('#t05-r-nuits', APRES['nuits']),
                    texte('#t05-r-total', APRES['heb'], avec=True), texte('#t05-r-l-nuits', APRES['nuits'], avec=True),
                    texte('#t05-r-l-st', APRES['heb'], avec=True), anneau('#t05-r-nuits', d=0.9),
                    *maj_folio(APRES), defiler('#t05-folio-defil', 0, d=0.05, avec=True),
                    # « Folio » enregistre la réservation puis ouvre le folio : le bouton garde l'ancien
                    # solde jusque-là (folio_amount_residual, resynchronisé à l'enregistrement).
                    clic('#t05-r-st-folio'), texte('#t05-r-st-folio-v', APRES['ttc'], avec=True, decale=0.7),
                    vue('t05-folio'),
                    pause(0.3), defiler('#t05-folio-defil', -470, d=0.7), curseur('#t05-f-l2-taxes', fx=0.3, d=0.5),
                    zoom('#t05-f-l2', s=1.4, fx=0.56, d=0.8), bulle('b-fige', '#t05-f-l2-lib', cote='haut', d=2.6),
                    pause(1.8), dezoom(d=0.6)]},
        {'temps': 2, 'titre': "L'état du mois, prêt à déclarer", 'texte': 'Nuitées taxées et taxe collectée, mois par mois.',
         'voix': "Le mois suivant, l'état de la taxe de séjour s'ouvre déjà sur les séjours terminés, facturés ou "
                 "soldés, regroupés par mois de départ. On ajoute le filtre Départs du mois dernier : il ne reste "
                 "qu'octobre. Son total est le montant à déclarer et à reverser avant le quinze, et il s'exporte en "
                 "Excel.",
         'gestes': aller('Réservations', 'Facturation', 't05-dd-fact', '#t05-dd-fact-taxe')
         + [pause(0.5), vue('t05-etat'), pause(0.4), anneau('#t05-e-fac-term', d=1.1), anneau('#t05-e-a-2', d=1.0),
            clic('#t05-e-toggler', d=0.55), montrer('#t05-e-menu', d=0.2, y=-6), pause(0.4),
            # Odoo garde le menu ouvert : le filtre coché s'ajoute aussitôt en facette, après les deux autres.
            # La coche au clic (decale = trajet du curseur + 0,08 s) ; l'écran redessiné (barre sur deux lignes,
            # panneau descendu de 39 px) 0,4 s plus tard, une fois l'onde du clic éteinte sur « Départs du mois
            # dernier » ; le curseur suit l'entrée cochée, qui descend avec le panneau.
            clic('#t05-e-menu-dernier', d=0.5),
            classe('#t05-e-menu-dernier', ajouter=['t05-coche'], avec=True, decale=0.58),
            cacher('#t05-e-sa', d=0.06, avec=True, decale=0.4), montrer('#t05-e-sb', d=0.06, y=0, avec=True),
            cacher('#t05-e-menu', d=0.06, avec=True), montrer('#t05-e-menu-b', d=0.06, y=0, avec=True),
            curseur('#t05-e-menu-b-dernier', d=0.15, avec=True), pause(0.4),
            cacher('#t05-e-menu-b', d=0.15), anneau('#t05-e-fac-dernier', d=1.0, avec=True),
            # « Son total… » : le zoom sur octobre et son total ; « … s'exporte en Excel » : le téléchargement.
            curseur('#t05-e-b', fx=1.6, fy=0.7, d=0.5), zoom('#t05-e-b', s=1.6, d=0.8, avec=True),
            reaction('r-fin', d=2.4), anneau('#t05-e-b-tot', d=1.4, avec=True, decale=0.2), dezoom(d=0.6),
            anneau('#t05-e-export', d=1.3)]},
    ],
    'resultats': {
        'titre': 'Réglée sur la fiche, calculée à chaque séjour',
        'cartes': [
            {'valeur': '24', 'compter': 24, 'unite': 'barèmes', 'icone': 'globe',
             'texte': "livrés pour 4 pays et 6 catégories, modifiables sans code"},
            {'valeur': '0', 'unite': 'saisie', 'icone': 'personne',
             'texte': "de taxe à la confirmation : la ligne s'ajoute seule au folio"},
            {'valeur': '1', 'compter': 1, 'unite': 'ligne', 'icone': 'document',
             'texte': "par folio, hors TVA, recalculée si le séjour change, figée à la facture"},
        ],
        'voix': "Vingt-quatre barèmes livrés, aucune saisie de taxe à la confirmation, une seule ligne par folio, "
                "hors TVA : "
                "la taxe de séjour se calcule toute seule.",
    },
    'cta': {
        'appel': 'Demandez votre démonstration',
        'suivant': 'Fiche de police et statistiques',
        'voix': "Aïte haousse, par Aïte Consulting. Demandez votre démonstration, et retrouvez tous nos tutoriels sur "
                "notre chaîne.",
    },
    'vignette': {'etape': 4, 'apres': 10.0},
}
