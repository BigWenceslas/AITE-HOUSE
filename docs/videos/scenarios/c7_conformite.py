# -*- coding: utf-8 -*-
"""Chapitre 7 — La conformité, sans saisie de plus.

Source : cahier de recette, domaines N (taxe de séjour : N01 barème sur la
fiche hôtel, N02 ligne ajoutée seule, N05 état mensuel, N08 nouvelle loi de
finances) et O (registre des clients : O01 fiche pré-remplie au check-in,
O02 compléter jusqu'à « Complète », O05 registre de police, O06
statistiques d'hébergement) ; captures de la vague 1 (captures/02*, 04, 11,
14).

Libellés relevés dans :
- aite_city_tax/views/hotel_hotel_views.xml (onglet « Taxe de séjour »,
  groupes « Réglage » / « Ce qui s'applique », texte d'aide),
  models/hotel_hotel.py (phrase « Chaque séjour portera une ligne … », la
  devise y est écrite par son code ISO, XAF), models/city_tax_rate.py
  (libellé du barème, « Montant par nuitée », bases, catégories),
  data/city_tax_data.xml (barème Cameroun et sa référence légale),
  views/city_tax_report_views.xml et menus.xml (« Taxe de séjour — état
  mensuel », mesures « Nuitées taxées » / « Taxe collectée ») ;
- aite_guest_registry/views/guest_registration_views.xml (liste « Fiches
  clients », colonnes, « Il manque », états « À compléter » / « Complète »),
  report/police_register_report.xml (assistant « Imprimer le registre de
  police », son texte, ses champs, et l'en-tête du registre imprimé),
  views/guest_stats_views.xml (pivot « Statistiques d'hébergement »).

Rejoué tel que le code l'affiche : le libellé du barème est calculé et
stocké à l'installation, en anglais et avec le code de devise (« Cameroon —
3 ★ : 3 000 XAF », city_tax_rate.py:71-80 ; ECARTS.md n° 39, comme t05) ;
au check-in, seule la fiche du client principal est créée
(aite_guest_registry/models/hotel_reservation.py:96-110), pré-remplie depuis
le contact, le nom complet dans « Nom » (« Estelle Ngono »), « Prénom(s) »
vide, et « Il manque » : « le prénom, la date de naissance »
(guest_registration.py:183-205 et :255-296, ECARTS n° 30, écart 8 de t06,
corrigé : le nom n'est plus coupé au premier espace) ; la réception sépare
elle-même le prénom, comme dans t06 : d'où le bandeau « 1 fiche(s)
à compléter · 1 occupant(s) sans fiche » du chapitre 1 ; l'accompagnant,
Arnaud Ngono, est saisi ensuite (scenarios/t06_registre.py). Registre de
police imprimé : arrivées de la période triées par date d'arrivée, chambre
et nom (wizard/police_register_wizard.py:46-53), nom en capitales, libellé
du type de pièce (report/police_register_report.xml:80-90) ; extrait de six
lignes sur 54, séjours de scenarios/t02_planning.py (SEJOURS) et fiches de
t06 (la 105 est hors service toute la série).
"""

import demo
from ecrans import (assistant, bouton, cell_html, cell_puce, champ, cp_fiche, deux_colonnes, e, fenetre, groupe, icone,
                    m_champ, m_champs, onglets, recherche, titre_fiche, vue_fiche, vue_libre, vue_liste)
from moteur import anneau, cacher, classe, clic, defiler, etat, fermer, montrer, ouvrir, pause, texte, vue

NOM, ROLE = demo.POSTES['conformite']
MENUS = ['Direction', 'Front Desk', 'Réservations', 'Espaces & Prestations', 'Notes de chambre en attente',
         'Facturation', 'Fidélité', 'Gouvernante', 'Configuration']


def menu(n):
    """Le sélecteur d'un menu de la barre (grille, nom de l'application, puis les menus)."""
    return '#app-c7 .o-haut .menu:nth-child(%d)' % (MENUS.index(n) + 3)


def en_tete(titre, facette):
    return ('<div class="cp"><div class="fil"><span class="ref" style="font-size:24px">%s</span></div>%s'
            '<span class="pager"></span></div>' % (e(titre), recherche([(None, facette)])))


# ---------------------------------------------------------- la fiche hôtel --
CASE = '<span class="case coche"><i>%s</i></span>' % icone('coche')
FEUILLE = (
    titre_fiche(demo.HOTEL)
    + deux_colonnes(groupe('Identité', [champ('Code', 'CHD'), champ('Catégorie', demo.ETOILES)]),
                    groupe('Horaires standards', [champ("Heure d'arrivée standard", '14:00'),
                                                  champ('Heure de départ standard', '12:00')]))
    + onglets(['Politique / informations', 'Taxe de séjour'], 1)
    + deux_colonnes(groupe('Réglage', [champ('Collecter la taxe de séjour', CASE, html=True),
                                       champ('Pays (fiche hôtel)', 'Cameroun', lien_=True),
                                       champ('Catégorie (fiche hôtel)', demo.ETOILES)]),
                    groupe("Ce qui s'applique", [champ('Barème appliqué', 'Cameroon — 3 ★ : 3 000 XAF', 'c7-bareme'),
                                                 champ('Montant par nuitée', '3 000'),
                                                 champ('Base', 'Par personne et par nuit')]))
    + '<div class="alerte-info" id="c7-phrase">%s Chaque séjour portera une ligne « Taxe de séjour » de 3 000 XAF par '
      'personne et par nuit, hors TVA.</div>' % '<b>i</b>'
    + '<div class="note-pied" id="c7-aide">La taxe est ajoutée automatiquement à chaque folio et recalculée si les dates, '
      'les chambres ou le nombre de personnes changent. Elle n\'entre pas dans la base de la TVA. Pour modifier un '
      'montant (nouvelle loi de finances) : <b>Hôtel → Configuration → Taxe de séjour → Barèmes</b>.</div>')
HOTEL = vue_fiche('c7-hotel', cp_fiche('Hôtels', demo.HOTEL, '1 / 1', stats=[('c7-st', 'lit', 'Chambres', '20')]),
                  [], '', FEUILLE, initiale=True)

# ---------------------------------------------------------------- barèmes --
REF = 'Loi de finances 2017 — déclaration mensuelle DGI (formulaire I/PL-TVA-IR)'
BAREMES_L = []
for i, (cat, mt) in enumerate([('Non classé / meublé', '500'), ('1 ★', '500'), ('2 ★', '1 000'), ('3 ★', '3 000'),
                                ('4 ★', '4 000'), ('5 ★', '5 000')]):
    BAREMES_L.append({'id': 'c7-b%d' % i, 'cellules': ['Cameroun', cat, (('<span class="d"><b>%s</b></span>' % mt,)
                                                                         if cat == '3 ★' else mt), 'XAF',
                                                       'Par personne et par nuit', '', REF],
                      'classe': 'survol' if cat == '3 ★' else ''})
BAREMES = vue_liste('c7-baremes', 'Barèmes de taxe de séjour',
                    [('Pays', '170px'), ('Catégorie', '220px'), ('Montant par nuitée', '200px', 'd'), ('Devise', '100px'),
                     ('Base de calcul', '270px'), ('Compter les enfants', '200px'), ('Référence légale', '1fr')],
                    BAREMES_L, facettes=[(None, 'Pays : Cameroun')], pager='1-6 / 6')

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


ETAT = pivot('c7-etat', 'Taxe de séjour — état mensuel', 'Mois',
             '<tr><td class="vide"></td><th colspan="2">⊟ Total</th></tr>'
             '<tr><td class="vide"></td><th colspan="2">⊞ %s</th></tr>'
             '<tr><td class="vide"></td><th class="m">Nuitées taxées</th><th class="m">Taxe collectée</th></tr>'
             % e(demo.HOTEL),
             [('2026-08', ['347', '1 041 000,00']), ('2026-09', ['408', '1 224 000,00']),
              ('2026-10', ['256', '768 000,00'])],
             ['1 011', '3 033 000,00'])

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
FICHES = vue_liste('c7-fiches', 'Fiches clients — %s' % demo.RESA, FICHES_COLS, FICHES_L,
                   facettes=[(None, 'Réservation %s' % demo.RESA)], pager='1-1 / 1')

# ----------------------------------------------------- registre de police --
ASSISTANT = assistant('c7-as', 'Imprimer le registre de police', (
    '<div class="m-aide">Le registre liste, par ordre d\'arrivée, toutes les personnes hébergées sur la période — '
    'c\'est le document à présenter en cas de contrôle.</div>'
    + m_champs([m_champ('Hôtel', e(demo.HOTEL)), m_champ('Du', e('08/10/2026')), m_champ('Au', e('14/10/2026'))],
               [m_champ('Inclure les fiches incomplètes', CASE), m_champ('Fiches trouvées', '<b>54</b>')])),
    [('c7-imprimer', 'Imprimer', 'primaire', 'imprimer'), ('c7-annuler', 'Annuler', 'gris', None)], haut=140)

CNI = "Carte nationale d'identité"
PERSONNES = [
    ('08/10/2026', '10/10/2026', '103', 'MENGUE', 'Esther', '04/02/1984', 'Cameroun', CNI, '112004517', 'Yaoundé', 'Kribi'),
    ('09/10/2026', '12/10/2026', '401', 'ABEGA', 'Laurent', '21/07/1979', 'France', 'Passeport', '18FR22914', 'Paris', 'Limbé'),
    ('10/10/2026', '13/10/2026', '101', 'OWONO', 'Cyrille', '09/11/1982', 'Cameroun', CNI, '115330284', 'Bafoussam', 'Bafoussam'),
    ('13/10/2026', '16/10/2026', '202', 'ESSOMBA', 'Brigitte', '30/05/1988', 'Cameroun', CNI, '113870106', 'Édéa', 'Édéa'),
    ('14/10/2026', '16/10/2026', '204', 'NGONO', 'Estelle', '12/03/1991', 'Cameroun', CNI, '114208815', 'Yaoundé', 'Yaoundé'),
    ('14/10/2026', '16/10/2026', '204', 'NGONO', 'Arnaud', '27/08/1989', 'Cameroun', CNI, '116502371', 'Yaoundé', 'Yaoundé'),
]
RAPPORT = ('<div class="rapport masque" id="c7-rapport"><h2>REGISTRE DES CLIENTS HÉBERGÉS</h2>'
           '<div class="sous">%s — du 08/10/2026 au 14/10/2026 — 54 personne(s)</div><table><tr>%s</tr>%s</table>'
           '<div class="pied"><span>Arrêté le 14/10/2026</span><span>Cachet et signature de l\'établissement</span></div></div>'
           % (e(demo.HOTEL), ''.join('<th>%s</th>' % e(t) for t in ['Arrivée', 'Départ', 'Ch.', 'Nom', 'Prénom(s)',
                                                                   'Né(e) le', 'Nationalité', 'Pièce', 'N°', 'Provenance',
                                                                   'Destination']),
              ''.join('<tr>%s</tr>' % ''.join('<td>%s</td>' % e(c) for c in p) for p in PERSONNES)))

# ------------------------------------------------ statistiques (MINTOUL) --
STATS = pivot('c7-stats', "Statistiques d'hébergement", 'Mois',
              '<tr><td class="vide"></td><th colspan="6">⊟ Total</th></tr>'
              '<tr><td class="vide"></td><th colspan="2" id="c7-nr">⊞ Non-résident</th><th colspan="2">⊞ Résident</th>'
              '<th colspan="2"></th></tr>'
              '<tr><td class="vide"></td>%s</tr>' % ('<th class="m">Arrivées</th><th class="m">Nuitées</th>' * 3),
              [('2026-08', ['38', '96', '112', '251', '150', '347']), ('2026-09', ['41', '118', '120', '290', '161', '408']),
               ('2026-10', ['22', '71', '66', '185', '88', '256'])],
              ['101', '285', '298', '726', '399', '1 011'])

# Neuf menus : la barre de la vidéo n'a pas la place du nom de la société.
ECRAN = fenetre('app-c7', 'Hôtel', MENUS, [HOTEL, BAREMES, ETAT, FICHES, STATS], actif='Configuration',
                societe='', initiale=NOM[0], avatar='#854F0B', calques=ASSISTANT + RAPPORT)


def aller(depuis, vers):
    return [clic(menu(vers), d=0.5), classe(menu(depuis), retirer=['actif']), classe(menu(vers), ajouter=['actif'])]


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
    'vues_initiales': {'odoo': 'c7-hotel'},
    'etapes': [
        {'titre': 'La taxe de séjour, réglée une fois', 'texte': "Le pays et les étoiles de l'hôtel choisissent le barème.",
         'voix': "Sur la fiche de l'hôtel, l'onglet Taxe de séjour dit ce qui va se passer : pour un trois étoiles au "
                 "Cameroun, chaque séjour portera une ligne de trois mille francs par personne et par nuit, hors TVA.",
         'gestes': [pause(0.4), defiler('#c7-hotel-defil', -250, d=0.9), anneau('#c7-bareme', d=1.4),
                    anneau('#c7-phrase', d=2.0), anneau('#c7-aide', d=1.2)]},
        {'titre': 'Les barèmes, sans code', 'texte': 'Une nouvelle loi de finances ? On change le montant ici.',
         'voix': "Les barèmes officiels sont livrés, avec leur référence légale. Si une loi de finances change un "
                 "montant, on le modifie ici, sans programmeur : il s'applique aux nouveaux séjours, les factures "
                 "passées ne bougent pas.",
         'gestes': [clic(menu('Configuration'), d=0.5), vue('c7-baremes'), pause(0.4), anneau('#c7-b3', d=1.6),
                    anneau('#c7-b3 span:nth-child(8)', d=1.4)]},
        {'titre': "L'état mensuel à déclarer", 'texte': 'Nuitées taxées et taxe collectée, mois par mois.',
         'voix': "La taxe se calcule toute seule sur chaque folio. En fin de mois, l'état mensuel donne les nuitées "
                 "taxées et le montant collecté, prêts à déclarer, avec l'export Excel.",
         'gestes': aller('Configuration', 'Facturation') + [vue('c7-etat'), pause(0.4), anneau('#c7-etat-2', d=1.6),
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
             montrer('#c7-rapport', d=0.5, y=30), pause(0.6), anneau('#c7-rapport tr:nth-child(6)', d=1.4),
             anneau('#c7-rapport .pied', d=1.2)]},
        {'titre': "Les statistiques d'hébergement", 'texte': 'Arrivées et nuitées, résidents et non-résidents.',
         'voix': "Enfin, les statistiques d'hébergement : arrivées et nuitées, résidents et non-résidents, mois par "
                 "mois, tirées des mêmes fiches. Elles se regroupent aussi par nationalité ou par motif de séjour.",
         'gestes': [cacher('#c7-rapport', d=0.3), vue('c7-stats'), pause(0.4),
                    anneau('#c7-nr', d=1.4), anneau('#c7-stats-2', d=1.4), anneau('#c7-stats-tot', d=1.2)]},
    ],
}
