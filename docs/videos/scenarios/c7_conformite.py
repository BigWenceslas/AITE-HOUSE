# -*- coding: utf-8 -*-
"""Chapitre 7 — La conformité, sans saisie de plus.

Source : cahier de recette, domaines N (taxe de séjour : N01 barème sur la
fiche hôtel, N02 ligne ajoutée seule, N05 état mensuel, N08 nouvelle loi de
finances) et O (registre des clients : O01 fiche pré-remplie au check-in,
O02 compléter jusqu'à « Complète », O05 registre de police, O06
statistiques d'hébergement) ; captures de la vague 1 (captures/02*, 04, 11,
14).

Libellés relevés dans (livraison 4, écarts n° 37-77) :
- aite_city_tax/views/hotel_hotel_views.xml (onglet « Taxe de séjour »,
  groupes « Réglage » / « Ce qui s'applique », texte d'aide et son chemin de
  menu « Hôtel → Configuration → Barèmes de taxe de séjour », écart n° 46),
  models/hotel_hotel.py:57-83 (phrase « Chaque séjour portera une ligne … »,
  la devise par son symbole, « 3 000 FCFA », et non plus par son code ISO,
  écart n° 7), models/city_tax_rate.py:24-92 (libellé du barème calculé à
  la lecture, dans la langue de l'utilisateur et avec le symbole : « Cameroun
  — 3 ★ : 3 000 FCFA », écart n° 39 ; « Montant par nuitée », bases,
  catégories ; la colonne « Devise » de la liste garde le code « XAF »),
  data/city_tax_data.xml (barème Cameroun et sa référence légale),
  views/city_tax_report_views.xml et menus.xml (« Taxe de séjour — état
  mensuel », ouvert filtré « Séjours terminés (à déclarer) » et regroupé
  « Date de départ » par mois, facette « Date de départ: Mois », écart n° 48 ;
  lignes « août 2026 » au lieu de « 2026-08 », écart n° 4 ; « Taxe collectée »
  sans décimales, écart n° 40 ; mesures « Nuitées taxées » / « Taxe
  collectée ») ;
- aite_guest_registry/views/guest_registration_views.xml (liste « Fiches
  d'enregistrement — RES/… », action_open_registrations,
  models/hotel_reservation.py:124-160 ; colonnes, « Il manque », états « À
  compléter » / « Complète »), report/police_register_report.xml (assistant
  sous le nom de l'action « Registre de police » :30-35, ouvert par le menu
  Facturation → « Registre de police (impression) », menus.xml:10-14 ; son
  texte, ses cinq champs sur une colonne :8-27, « Du » à aujourd'hui − 7
  jours, wizard/police_register_wizard.py:23-26 ; l'en-tête du registre
  imprimé), views/city_tax_rate_views.xml (liste des barèmes regroupée par
  pays, « stars desc », :8-17 et :40-44), views/guest_stats_views.xml (pivot « Statistiques
  d'hébergement » par mois d'arrivée, facette « Date d'arrivée: Mois »,
  lignes « octobre 2026 », écart n° 4). Facettes de regroupement par date
  écrites « ${description}: ${option} », sans espace avant les deux-points
  (web/static/src/search/search_model.js:1801).

Au check-in, seule la fiche du client principal est créée
(aite_guest_registry/models/hotel_reservation.py:108-123), pré-remplie depuis
le contact, le nom complet dans « Nom » (« Estelle Ngono »), « Prénom(s) »
vide, et « Il manque » : « le prénom, la date de naissance »
(guest_registration.py:189-206 et :281-305, ECARTS n° 30, écart 8 de t06,
corrigé : le nom n'est plus coupé au premier espace) ; la réception sépare
elle-même le prénom, comme dans t06 : d'où le bandeau « 1 fiche à
compléter · 1 occupant sans fiche » du chapitre 1, accordé depuis la
livraison 4 (écarts n° 44 et 47) ; l'accompagnant,
Arnaud Ngono, est saisi ensuite (scenarios/t06_registre.py). Registre de
police imprimé : arrivées de la période triées par date d'arrivée, chambre
et nom (wizard/police_register_wizard.py:46-53), nom en capitales, libellé
du type de pièce (report/police_register_report.xml:80-90) ; du 07 au 14/10,
extrait de sept lignes sur 60, séjours de scenarios/t02_planning.py (SEJOURS)
et fiches de t06 (la 105 est hors service toute la série). État mensuel au 14/10 : août et
septembre comme scenarios/t05_taxe_sejour.py (347 et 408 nuitées taxées) ;
octobre ne compte que les séjours terminés (facturés ou soldés), partis du 01
au 13/10 : 198 nuitées taxées, les séjours en cours (folios ouverts) n'y sont
pas ; septembre, le mois à déclarer avant le 15, est entouré.

« ? » d'aide (form_label.xml:6, hors mode debug ; un champ related reprend le
help de sa cible, odoo/fields.py:635-640) sur les champs qui portent un
help=, comme scenarios/t05_taxe_sejour.py : fiche hôtel, « Code », « Heure
d'arrivée standard », « Heure de départ standard », « Chambres vendables »
(aite_hotel_management/models/hotel_hotel.py:21-25, :54-62, :74-78), « Collecter la
taxe de séjour », « Barème appliqué » (aite_city_tax/models/hotel_hotel.py
:13-23), « Montant par nuitée » et « Base » (related, help de
models/city_tax_rate.py:45-61) ; registre de police, « Inclure les fiches
incomplètes » (wizard/police_register_wizard.py:31-34). « Catégorie »,
« Pays (fiche hôtel) », « Catégorie (fiche hôtel) », « Hôtel », « Du »,
« Au » et « Fiches trouvées » n'en ont pas.

Fiche hôtel entière, comme t05 (H_GAUCHE, H_DROITE) : les quatre groupes du
<group> de hotel_hotel_views.xml:44-72, Identité, Horaires standards,
Coordonnées (Rue, Ville, Pays, Téléphone +237 6 00 00 00 10, E-mail, Site
web) et Structure (Chambres vendables 20, les quatre étages de la série) ;
libellés en gras pour les champs modifiables (form_controller.scss:589-600 :
Code, Catégorie, les deux heures, les coordonnées, « Collecter la taxe de
séjour »), en graisse normale pour les champs calculés ou en lecture seule.
La feuille défile de 350 px jusqu'à l'onglet « Taxe de séjour ».
"""

import demo
from ecrans import (ICONES, MENUS_MUK, assistant, bouton, cell_html, cell_puce, champ, cp_fiche, deux_colonnes, e, entier,
                    fenetre, groupe, icone, m_champ, m_champs, mois_long, onglets, titre_fiche, vue_fiche, vue_libre,
                    vue_liste)
from moteur import anneau, cacher, classe, clic, defiler, etat, fermer, montrer, ouvrir, pause, texte, vue

NOM, ROLE = demo.POSTES['conformite']
MENUS = MENUS_MUK['hotel_direction']


def aide(html):
    """Le « ? » qu'Odoo 18 pose après le libellé d'un champ qui porte une aide (help= du modèle ; form_label.xml:6) :
    ajouté au libellé d'un ecrans.champ ou d'un ecrans.m_champ, dont le premier span est le libellé."""
    assert html.startswith(('<div class="ch">', '<div class="m-ch"'))
    return html.replace('</span>', '<sup class="c7-aide">?</sup></span>', 1)
# Icône d'un regroupement dans une facette (fa-layer-group d'Odoo 18), celle d'un filtre est ICONES['filtre'].
COUCHES = ('<svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linejoin="round">'
           '<path d="M12 3l9 4.5-9 4.5-9-4.5z" fill="#fff"/><path d="M3 12l9 4.5 9-4.5M3 16.5l9 4.5 9-4.5"/></svg>')


def menu(n):
    """Le sélecteur d'un menu de la barre (grille, nom de l'application, puis les menus)."""
    return '#app-c7 .o-haut .menu:nth-child(%d)' % (MENUS.index(n) + 3)


def en_tete(titre, facettes):
    """Le panneau d'un pivot : titre, barre de recherche et ses facettes [(libellé, icône SVG)]."""
    # Les facettes s'affichent entières (« Séjours terminés (à déclarer) ») : la barre s'élargit.
    f = ''.join('<span class="facette" style="max-width:none"><span class="fic">%s</span><span class="ell">%s</span>'
                '<span class="fx">×</span></span>' % (ico, e(lib)) for lib, ico in facettes)
    rech = ('<div class="recherche" style="margin-left:80px;width:880px">%s%s<span class="ph">Rechercher…</span>'
            '<span class="deroule">▾</span></div>' % (icone('loupe', 'loupe'), f))
    return ('<div class="cp"><div class="fil"><span class="ref" style="font-size:24px">%s</span></div>%s'
            '<span class="pager"></span></div>' % (e(titre), rech))


# ---------------------------------------------------------- la fiche hôtel --
CASE = '<span class="case coche"><i>%s</i></span>' % icone('coche')
# Les quatre étages de la série (101-107 au rez-de-chaussée, 2xx au 1er, 3xx au 2e, 4xx au 3e), la liste éditable
# floor_ids (poignée, nom, corbeille), comme scenarios/t05_taxe_sejour.py (ETAGES).
ETAGES = ('<div class="c7-etages"><div class="c7-etage c7-tete"><span></span><span>Nom</span></div>%s'
          '<div class="c7-etage c7-ajout"><span></span><span>Ajouter une ligne</span></div></div>'
          % ''.join('<div class="c7-etage"><span class="c7-poignee">⠿</span><span>%s</span>%s</div>'
                    % (n, icone('corbeille', 'c7-corb')) for n in ('Rez-de-chaussée', '1er étage', '2e étage', '3e étage')))
# Le <group> de la fiche (hotel_hotel_views.xml:44-72) : Identité, Horaires standards, Coordonnées, Structure, deux
# par rangée ; libellés en gras pour les champs modifiables (form_controller.scss:589-600), comme t05 (H_GAUCHE,
# H_DROITE).
FEUILLE = (
    titre_fiche(demo.HOTEL)
    + deux_colonnes(groupe('Identité', [aide(champ('Code', 'CHD', gras=True)), champ('Catégorie', demo.ETOILES, gras=True)])
                    + groupe('Coordonnées', [champ('Rue', 'Akwa', gras=True), champ('Ville', demo.VILLE, gras=True),
                                             champ('Pays', 'Cameroun', gras=True),
                                             champ('Téléphone', '+237 6 00 00 00 10', gras=True),
                                             champ('E-mail', '', gras=True), champ('Site web', '', gras=True)]),
                    groupe('Horaires standards', [aide(champ("Heure d'arrivée standard", '14:00', gras=True)),
                                                  aide(champ('Heure de départ standard', '12:00', gras=True))])
                    + groupe('Structure', [aide(champ('Chambres vendables', '20')), ETAGES]))
    + onglets(['Politique / informations', 'Taxe de séjour'], 1)
    + deux_colonnes(groupe('Réglage', [aide(champ('Collecter la taxe de séjour', CASE, html=True, gras=True)),
                                       champ('Pays (fiche hôtel)', 'Cameroun', lien_=True),
                                       champ('Catégorie (fiche hôtel)', demo.ETOILES)]),
                    groupe("Ce qui s'applique", [aide(champ('Barème appliqué', 'Cameroun — 3 ★ : 3 000 FCFA', 'c7-bareme')),
                                                 aide(champ('Montant par nuitée', '3 000')),
                                                 aide(champ('Base', 'Par personne et par nuit'))]))
    + '<div class="alerte-info" id="c7-phrase">%s Chaque séjour portera une ligne « Taxe de séjour » de 3 000 FCFA par '
      'personne et par nuit, hors TVA.</div>' % '<b>i</b>'
    + '<div class="note-pied" id="c7-aide">La taxe est ajoutée automatiquement à chaque folio et recalculée si les dates, '
      'les chambres ou le nombre de personnes changent. Elle n\'entre pas dans la base de la TVA. Pour modifier un '
      'montant (nouvelle loi de finances) : <b>Hôtel → Configuration → Barèmes de taxe de séjour</b>.</div>')
HOTEL = vue_fiche('c7-hotel', cp_fiche('Hôtels', demo.HOTEL, '1 / 1', stats=[('c7-st', 'lit', 'Chambres', '20')]),
                  [], '', FEUILLE, initiale=True)

# ---------------------------------------------------------------- barèmes --
# L'action s'ouvre regroupée par pays (search_default_group_country, city_tax_rate_views.xml:40-44) : facette
# de regroupement « Pays », quatre groupes de six barèmes (city_tax_data.xml), pager « 1-4 / 4 » (il compte les
# groupes) ; Cameroun déplié, lignes triées « country_id, stars desc » (5 ★ → Non classé), « Compter les
# enfants » décoché (count_children False), référence légale propre au « Non classé / meublé » (:53-58).
# Comme scenarios/t05_taxe_sejour.py (FERME / OUVERT).
REF = 'Loi de finances 2017 — déclaration mensuelle DGI (formulaire I/PL-TVA-IR)'
REF_CM0 = 'Loi de finances 2017 — « autres établissements et meublés »'
CASE_NON = '<span><span class="case"><i></i></span></span>'
BAREMES_L = []
for etoiles, cat, mt in [(5, '5 ★', '5 000'), (4, '4 ★', '4 000'), (3, '3 ★', '3 000'), (2, '2 ★', '1 000'),
                         (1, '1 ★', '500'), (0, 'Non classé / meublé', '500')]:
    BAREMES_L.append({'id': 'c7-b%d' % etoiles,
                      'cellules': ['Cameroun', cat, mt, 'XAF', 'Par personne et par nuit', cell_html(CASE_NON),
                                   REF_CM0 if etoiles == 0 else REF],
                      'classe': 'survol' if etoiles == 3 else ''})
BAREMES = vue_liste('c7-baremes', 'Barèmes de taxe de séjour',
                    [('Pays', '170px'), ('Catégorie', '220px'), ('Montant par nuitée', '200px', 'd'), ('Devise', '100px'),
                     ('Base de calcul', '270px'), ('Compter les enfants', '200px'), ('Référence légale', '1fr')],
                    BAREMES_L, facettes=[('c7-fac-pays', 'Pays')], pager='1-4 / 4', groupes={0: 'Cameroun (6)'})
_FAC = '<span class="facette" id="c7-fac-pays">%s' % icone('filtre', 'fic')
assert BAREMES.count(_FAC) == 1 and BAREMES.endswith('</div></div>')
BAREMES = (BAREMES.replace(_FAC, '<span class="facette" id="c7-fac-pays"><span class="fic">%s</span>' % COUCHES)[:-12]
           + ''.join('<div class="groupe">▸ %s (6)</div>' % e(p) for p in ("Côte d'Ivoire", 'Guinée', 'Sénégal'))
           + '</div></div>')

# ------------------------------------------------------------ état mensuel --
def pivot(identifiant, titre, facette, entetes, lignes, total):
    """Une vue pivot d'Odoo : ``entetes`` = lignes d'en-tête déjà composées."""
    corps = ''.join('<tr id="%s-%d"><td class="r n2">⊞ %s</td>%s</tr>'
                    % (identifiant, i, e(lib), ''.join('<td>%s</td>' % v for v in vals))
                    for i, (lib, vals) in enumerate(lignes))
    tot = '<tr class="tot" id="%s-tot"><td class="r">⊟ Total</td>%s</tr>' % (identifiant, ''.join('<td>%s</td>' % v
                                                                                                for v in total))
    barre = ('<div class="pv-barre"><span class="bt primaire">Mesures ▾</span><span class="bt gris">⇄</span>'
             '<span class="bt gris">✥</span><span class="bt gris" id="%s-export">%s</span></div>'
             % (identifiant, icone('document')))
    return vue_libre(identifiant, en_tete(titre, facette) + barre
                     + '<table class="pv">%s%s%s</table>' % (entetes, tot, corps))


# Séjours terminés (facturés ou soldés) par mois de départ, au 14/10 : nuitées taxées × 3 000 FCFA.
TAUX = 3000
TAXE_MOIS = [(8, 347), (9, 408), (10, 198)]
ETAT = pivot('c7-etat', 'Taxe de séjour — état mensuel',
             [('Séjours terminés (à déclarer)', ICONES['filtre']), ('Date de départ: Mois', COUCHES)],
             '<tr><td class="vide"></td><th colspan="2">⊟ Total</th></tr>'
             '<tr><td class="vide"></td><th colspan="2">⊞ %s</th></tr>'
             '<tr><td class="vide"></td><th class="m">Nuitées taxées</th><th class="m">Taxe collectée</th></tr>'
             % e(demo.HOTEL),
             [(mois_long(mo, 2026), [entier(n), entier(n * TAUX)]) for mo, n in TAXE_MOIS],
             [entier(sum(n for _, n in TAXE_MOIS)), entier(sum(n for _, n in TAXE_MOIS) * TAUX)])

# ---------------------------------------------------- fiches clients (O01) --
FICHES_COLS = [('Chambre', '110px'), ('Nom', '150px'), ('Prénom(s)', '100px'), ('Date de naissance', '140px'),
               ('Nationalité', '110px'), ('Type de pièce', '170px'), ('N° de pièce', '120px'), ('Client principal', '70px'),
               ('Signée par le client', '70px'), ('Il manque', '1fr'), ('Fiche', '120px'), ('', '40px')]
CASE_VIDE = '<span class="case"><i></i></span>'
# La fiche créée au check-in : celle du client principal, pré-remplie depuis le contact (nom complet dans « Nom »).
FICHES_L = [{'id': 'c7-f0', 'classe': 'avert', 'cellules': [
    '204 [CFT]', cell_html('<span class="ell" id="c7-nom0">Estelle Ngono</span>'),
    cell_html('<span class="ell" id="c7-pre0"></span>'), cell_html('<span class="ell" id="c7-dn0"></span>'),
    'Cameroun', "Carte nationale d'identité", '114208815', cell_html(CASE), cell_html(CASE_VIDE),
    cell_html('<span class="ell" id="c7-im0" style="color:#8A6100">le prénom, la date de naissance</span>'),
    cell_puce('À compléter', 'orange', 'c7-et0'), cell_html('<span>%s</span>' % icone('imprimer'))]}]
FICHES = vue_liste('c7-fiches', "Fiches d'enregistrement — %s" % demo.RESA, FICHES_COLS, FICHES_L,
                   facettes=[(None, 'Réservation %s' % demo.RESA)], pager='1-1 / 1')

# ----------------------------------------------------- registre de police --
# Ouverte par le menu, la fenêtre prend le nom de l'action, « Registre de police » (Odoo 18 n'affiche pas le string
# du formulaire, comme ECARTS n° 45) ; les cinq champs sur une colonne (un seul <group>) ; « Du » : aujourd'hui
# − 7 jours (police_register_wizard.py:23-26), le 07/10. Fiches du 07 au 14/10 : 54 du 08 au 14 et 6 le 07,
# celles du registre de scenarios/t06_registre.py (GROUPES, GROUPES_AVANT), soit 60.
DU_REG, NB_REG = '07/10/2026', 60
ASSISTANT = assistant('c7-as', 'Registre de police', (
    '<div class="m-aide">Le registre liste, par ordre d\'arrivée, toutes les personnes hébergées sur la période — '
    'c\'est le document à présenter en cas de contrôle.</div>'
    + m_champs([m_champ('Hôtel', e(demo.HOTEL)), m_champ('Du', e(DU_REG)), m_champ('Au', e('14/10/2026')),
                aide(m_champ('Inclure les fiches incomplètes', CASE)), m_champ('Fiches trouvées', '<b>%d</b>' % NB_REG)])),
    [('c7-imprimer', 'Imprimer', 'primaire', 'imprimer'), ('c7-annuler', 'Annuler', 'gris', None)], haut=140)

CNI = "Carte nationale d'identité"
# Extrait : Nadine Ekambi, arrivée le 07/10 en 202 (scenarios/t02_planning.py SEJOURS, t03), en tête.
PERSONNES = [
    ('07/10/2026', '09/10/2026', '202', 'EKAMBI', 'Nadine', '17/06/1986', 'Cameroun', CNI, '113516940', 'Nkongsamba',
     'Nkongsamba'),
    ('08/10/2026', '10/10/2026', '103', 'MENGUE', 'Esther', '04/02/1984', 'Cameroun', CNI, '112004517', 'Yaoundé', 'Kribi'),
    ('09/10/2026', '12/10/2026', '401', 'ABEGA', 'Laurent', '21/07/1979', 'France', 'Passeport', '18FR22914', 'Paris', 'Limbé'),
    ('10/10/2026', '13/10/2026', '101', 'OWONO', 'Cyrille', '09/11/1982', 'Cameroun', CNI, '115330284', 'Bafoussam', 'Bafoussam'),
    ('13/10/2026', '16/10/2026', '202', 'ESSOMBA', 'Brigitte', '30/05/1988', 'Cameroun', CNI, '113870106', 'Édéa', 'Édéa'),
    ('14/10/2026', '16/10/2026', '204', 'NGONO', 'Estelle', '12/03/1991', 'Cameroun', CNI, '114208815', 'Yaoundé', 'Yaoundé'),
    ('14/10/2026', '16/10/2026', '204', 'NGONO', 'Arnaud', '27/08/1989', 'Cameroun', CNI, '116502371', 'Yaoundé', 'Yaoundé'),
]
RAPPORT = ('<div class="rapport masque" id="c7-rapport"><h2>REGISTRE DES CLIENTS HÉBERGÉS</h2>'
           '<div class="sous">%s — du %s au 14/10/2026 — %d personne(s)</div><table><tr>%s</tr>%s</table>'
           '<div class="pied"><span>Arrêté le 14/10/2026</span><span>Cachet et signature de l\'établissement</span></div></div>'
           % (e(demo.HOTEL), DU_REG, NB_REG, ''.join('<th>%s</th>' % e(t) for t in ['Arrivée', 'Départ', 'Ch.', 'Nom', 'Prénom(s)',
                                                                   'Né(e) le', 'Nationalité', 'Pièce', 'N°', 'Provenance',
                                                                   'Destination']),
              ''.join('<tr>%s</tr>' % ''.join('<td>%s</td>' % e(c) for c in p) for p in PERSONNES)))

# ------------------------------------------------ statistiques (MINTOUL) --
STATS = pivot('c7-stats', "Statistiques d'hébergement", [("Date d'arrivée: Mois", COUCHES)],
              '<tr><td class="vide"></td><th colspan="6">⊟ Total</th></tr>'
              '<tr><td class="vide"></td><th colspan="2" id="c7-nr">⊞ Non-résident</th><th colspan="2">⊞ Résident</th>'
              '<th colspan="2"></th></tr>'
              '<tr><td class="vide"></td>%s</tr>' % ('<th class="m">Arrivées</th><th class="m">Nuitées</th>' * 3),
              [(mois_long(mo, 2026), [entier(v) for v in vals]) for mo, vals in (
                  (8, [38, 96, 112, 251, 150, 347]), (9, [41, 118, 120, 290, 161, 408]),
                  (10, [22, 71, 66, 185, 88, 256]))],
              [entier(v) for v in (101, 285, 298, 726, 399, 1011)])

# Neuf menus : la barre de la vidéo n'a pas la place du nom de la société, et ses menus se resserrent
# (espacement de 17 px au lieu de 26) pour que la grille et l'avatar restent dans la fenêtre.
ECRAN = fenetre('app-c7', 'Hôtel', MENUS, [HOTEL, BAREMES, ETAT, FICHES, STATS], actif='Configuration',
                societe='', initiale=NOM[0], avatar='#854F0B', calques=ASSISTANT + RAPPORT)
assert ECRAN.count('<div class="o-haut">') == 1
ECRAN = ECRAN.replace('<div class="o-haut">', '<div class="o-haut" style="gap:17px">')


def aller(depuis, vers):
    return [clic(menu(vers), d=0.5), classe(menu(depuis), retirer=['actif']), classe(menu(vers), ajouter=['actif'])]


# Le « ? » d'aide, comme celui de scenarios/t01_reception.py (.t1-aide) ; presentation.py réunit le CSS des chapitres.
# La colonne des libellés de la fiche hôtel s'élargit de 20 px : « Heure de départ standard » et « Collecter la taxe de
# séjour », suivis du « ? », ne touchent plus leur valeur.
CSS = '''
.c7-aide { color: var(--o-lien); font-size: 13px; margin-left: 3px; font-weight: 700; }
#c7-hotel .ch { grid-template-columns: 270px 1fr; }
.c7-etages { margin-top: 6px; }
.c7-etage { display: grid; grid-template-columns: 40px 1fr 30px; align-items: center; height: 42px;
  border-bottom: 1px solid #EEF0F2; font-size: 18px; color: var(--o-texte); }
.c7-etage.c7-tete { font-weight: 600; border-bottom-color: #DEE2E6; }
.c7-etage.c7-ajout { color: var(--o-prim); border-bottom: 0; }
.c7-poignee { color: #6C757D; text-align: center; }
.c7-corb { width: 17px; height: 17px; display: inline-flex; color: #495057; }
.c7-corb svg { width: 100%; height: 100%; }
'''

CHAPITRE = {
    'court': 'Conformité',
    'poste': 'Direction',
    'titre': 'La conformité, sans saisie de plus',
    'personne': (NOM, ROLE),
    'objectif': "Taxe de séjour, registre de police et statistiques d'hébergement : réglés une fois, puis produits "
                "tout seuls à partir des séjours.",
    'voix': "Septième chapitre : la conformité. La taxe de séjour, le registre des clients et les statistiques du "
            "ministère se font à partir des séjours, sans rien saisir de plus.",
    'app': 'app-c7',
    'ecran': ECRAN,
    'css': CSS,
    'vues_initiales': {'odoo': 'c7-hotel'},
    'etapes': [
        {'titre': 'La taxe de séjour, réglée une fois', 'texte': "Le pays et les étoiles de l'hôtel choisissent le barème.",
         'voix': "Sur la fiche de l'hôtel, l'onglet Taxe de séjour dit ce qui va se passer : pour un trois étoiles au "
                 "Cameroun, chaque séjour portera une ligne de trois mille francs par personne et par nuit, hors TVA.",
         'gestes': [pause(0.4), defiler('#c7-hotel-defil', -350, d=0.9), anneau('#c7-bareme', d=1.4),
                    anneau('#c7-phrase', d=2.0), anneau('#c7-aide', d=1.2)]},
        {'titre': 'Les barèmes, sans code', 'texte': 'Une nouvelle loi de finances ? On change le montant ici.',
         'voix': "Les barèmes officiels sont livrés, avec leur référence légale. Si une loi de finances change un "
                 "montant, on le modifie ici, sans programmeur : il s'applique aux nouveaux séjours, les factures "
                 "passées ne bougent pas.",
         'gestes': [clic(menu('Configuration'), d=0.5), vue('c7-baremes'), pause(0.4), anneau('#c7-b3', d=1.6),
                    anneau('#c7-b3 span:nth-child(8)', d=1.4)]},
        {'titre': "L'état mensuel à déclarer", 'texte': 'Séjours terminés : nuitées taxées et taxe collectée, mois par mois.',
         'voix': "La taxe se calcule toute seule sur chaque folio. L'état mensuel s'ouvre sur les séjours terminés : "
                 "les nuitées taxées et le montant collecté de chaque mois, prêts à déclarer, avec l'export Excel.",
         'gestes': aller('Configuration', 'Facturation') + [vue('c7-etat'), pause(0.4), anneau('#c7-etat-1', d=1.6),
                                                            anneau('#c7-etat-tot', d=1.2), anneau('#c7-etat-export', d=1.0)]},
        {'titre': 'Le registre des clients', 'texte': 'Fiches pré-remplies au check-in ; « Il manque » dit quoi ajouter.',
         'voix': "Au check-in, la fiche du client principal est créée, pré-remplie depuis le contact, nom complet "
                 "compris. La colonne Il manque dit ce qu'il reste à demander : le prénom et la date de naissance. "
                 "La réception sépare le prénom, saisit la date, et la fiche passe Complète.",
         'gestes': aller('Facturation', 'Réservations') + [
             vue('c7-fiches'), pause(0.4), anneau('#c7-nom0', d=0.9), anneau('#c7-im0', d=1.4),
             texte('#c7-nom0', 'Ngono'), texte('#c7-pre0', 'Estelle', avec=True),
             texte('#c7-im0', 'la date de naissance', avec=True), texte('#c7-dn0', '12/03/1991'), texte('#c7-im0', ''), etat('#c7-et0', 'Complète', 'vert'),
             classe('#c7-f0', retirer=['avert']), anneau('#c7-et0', d=1.0)]},
        {'titre': 'Le registre de police', 'texte': 'Toutes les personnes hébergées sur la période, prêt pour un contrôle.',
         'voix': "Le registre de police s'imprime pour n'importe quelle période : toutes les personnes hébergées, "
                 "dans l'ordre d'arrivée, avec leur pièce d'identité. C'est le document à présenter en cas de "
                 "contrôle.",
         'gestes': aller('Réservations', 'Facturation') + [
             ouvrir('c7-as'), pause(0.6), anneau('#c7-as .m-aide', d=1.4), clic('#c7-imprimer'), fermer('c7-as'),
             montrer('#c7-rapport', d=0.5, y=30), pause(0.6), anneau('#c7-rapport tr:nth-child(7)', d=1.4),
             anneau('#c7-rapport .pied', d=1.2)]},
        {'titre': "Les statistiques d'hébergement", 'texte': 'Arrivées et nuitées, résidents et non-résidents.',
         'voix': "Enfin, les statistiques d'hébergement : arrivées et nuitées, résidents et non-résidents, mois par "
                 "mois, tirées des mêmes fiches. Elles se regroupent aussi par nationalité ou par motif de séjour.",
         'gestes': [cacher('#c7-rapport', d=0.3), vue('c7-stats'), pause(0.4),
                    anneau('#c7-nr', d=1.4), anneau('#c7-stats-2', d=1.4), anneau('#c7-stats-tot', d=1.2)]},
    ],
}
