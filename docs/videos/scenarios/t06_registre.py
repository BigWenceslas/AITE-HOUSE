# -*- coding: utf-8 -*-
"""Tutoriel 6 — Fiche de police, registre et statistiques MINTOUL : tout part du check-in.

Personnage : la réceptionniste (demo.POSTES['reception'], Mireille Ateba),
profil Réception (aite_hotel_management.group_hotel_user) : c'est elle qui
fait le check-in, complète les fiches, les imprime et ouvre le registre
(aite_guest_registry/security/ir.model.access.csv:3 — lecture, écriture,
création ; views/menus.xml:4-8, menu sous Front Desk). Barre MuK :
ecrans.APPS_PROFIL['reception'] ; menus de l'application Hôtel du profil
Réception relevés sur ref_muk/306-reception-reservations.png (Front Desk,
Réservations, Espaces & Prestations, Notes de chambre en attente,
Facturation, Fidélité, Gouvernante). Les statistiques sont réservées au
profil Responsable (views/menus.xml:15-20) : la dernière étape change
d'écran pour la directrice (demo.POSTES['direction'], Danielle Eyenga),
barre ecrans.APPS_PROFIL['direction'] et menus du compte demo.direction
(relevés pour scenarios/t05_taxe_sejour.py:8-12).

Titre : la formule « la conformité se remplit toute seule » proposée pour
ce tutoriel n'est pas prouvée (la date de naissance se saisit toujours,
les accompagnants se saisissent en entier, le format officiel DGSN/MINTOUL
reste à confirmer : ROADMAP.md:62 et :78, vérification de l'analyse) ; le
titre retenu, « tout part du check-in », l'est (hotel_reservation.py:96-110).

Écrans et libellés (relevés mot pour mot, vérifiés par grep -rF dans addons/) :

1. Arrivées du jour — aite_hotel_management/views/hotel_menus.xml:17-46
   (Front Desk et ses sous-menus, séquences 10 à 50) ;
   views/hotel_reservation_views.xml:5-33 (colonnes, décoration info des
   réservations confirmées, somme « Total hébergement ») et :225-239, :291-300
   (filtre et action « Arrivées du jour ») ; colonne « Registre » ajoutée par
   aite_guest_registry/views/hotel_reservation_views.xml:56-69 (badge rouge
   « Aucune fiche », voir écart 2) ; libellés des champs :
   models/hotel_reservation.py:30-145. Sans colonne Hôtel pour la réception
   (groupe multi-société, hotel_reservation_views.xml:15-16 ; ref_muk/306).
2. Réservation — hotel_reservation_views.xml:39-160 (Check-in, Check-out,
   Encaisser un acompte, Envoyer la confirmation, No-show, Annuler ; barre
   Brouillon / Confirmée / Arrivé / Parti ; bouton Folio ; groupes Client,
   Séjour, Canal & commission, Occupation ; « Check-in réel » visible une
   fois renseigné ; onglets Chambres / Demandes particulières et colonnes
   de la ligne) ; check-in : models/hotel_reservation.py:365-386 (état
   Arrivé, heure réelle). Ajouts du registre :
   aite_guest_registry/views/hotel_reservation_views.xml:11-22 (bouton
   « Fiches clients » x/y = fiches complètes / occupants attendus),
   :25-41 (bandeau jaune « Registre des clients : … — compléter
   maintenant », bandeau vert « Registre des clients à jour. » et son lien
   « Imprimer les fiches »), :44-48 (bouton d'en-tête « Fiches
   d'enregistrement », icône imprimante) ; models/hotel_reservation.py
   :45-58 (occupants attendus = adultes + enfants ; état), :77-90 (phrase
   « 1 fiche(s) à compléter · 1 occupant(s) sans fiche »), :96-110 (au
   check-in, la fiche du client principal est créée et pré-remplie).
   Montants et heures du séjour d'Estelle repris de scenarios/t01_reception.py
   (folio 57 000 FCFA après l'acompte, check-in réel 14:06:12).
3. Fiches clients — models/hotel_reservation.py:112-148 (fenêtre
   « Fiches clients — RES/2026/0214 », facette Réservation, valeurs
   proposées : chambre du séjour, dates, nationalité et résidence = pays de
   l'hôtel) ; views/guest_registration_views.xml:5-33 (liste éditable en
   bas, lignes orange « À compléter » / vertes « Complète », colonnes
   Chambre, Nom, Prénom(s), Date de naissance, Nationalité, Type de pièce,
   N° de pièce, Client principal, Signée par le client, Il manque, Fiche,
   imprimante « Imprimer la fiche » ; Résidence et Téléphone masquées) ;
   models/guest_registration.py:70-79 (types de pièce), :182-206 (les six
   informations et la phrase « Il manque »), :218-241 (la fiche passe
   « Complète » toute seule à l'enregistrement), :255-280 (pré-remplissage
   depuis le contact : nom coupé au premier espace, nationalité, pièce,
   adresse, téléphone ; jamais la date de naissance). Boutons « Enregistrer »
   / « Ignorer » d'une ligne en saisie et fil d'Ariane à deux niveaux :
   odoo18/addons/web/static/src/views/list/list_controller.xml:7-13 et
   :105-114, search/breadcrumbs/breadcrumbs.xml:4-46 ; traductions
   odoo18/addons/web/i18n/fr.po (Save → Enregistrer, Discard → Ignorer).
   Modèle visuel : captures/11_fiches_du_sejour.png.
4. Fiche d'enregistrement imprimée — report/registration_card_report.xml
   :4-107 (« FICHE D'ENREGISTREMENT CLIENT », « Registre des voyageurs — »,
   N°, Chambre (nom de la chambre), Réservation, rubriques IDENTITÉ, PIÈCE
   D'IDENTITÉ, DOMICILE & DÉPLACEMENT, SÉJOUR, « Accompagnants » = fiches du
   séjour − 1, cadres « Signature du client » et « Cachet et signature de
   l'établissement », « Fiche établie le … », mention finale) ; une page
   par fiche (web.external_layout appelé pour chaque fiche, :17-18) ;
   numérotation FICHE/2026/00412 : data/sequence_data.xml:4-9. Le lien
   « Imprimer les fiches » imprime toutes les fiches du séjour :
   models/hotel_reservation.py:150-157.
5. Registre des clients — views/guest_registration_views.xml:36-61
   (colonnes, lignes orange « À compléter »), :155-188 (filtres « À
   compléter », « Non signées », regroupement « Date d'arrivée » par jour),
   :190-211 (action « Registre des clients », regroupée par jour par défaut,
   aide « l'état chronologique à présenter en cas de contrôle ») ; ordre
   « arrival_date desc, id desc » : models/guest_registration.py:20.
   Facette « Date d'arrivée: Jour » et groupes « 11 oct. 2026 (3) » :
   captures/nouvelles/13_registre_liste.png ; ref_muk/026.
6. Statistiques d'hébergement — views/guest_stats_views.xml:4-12 (pivot :
   mois en lignes, Résident / Non-résident en colonnes, mesures Arrivées et
   Nuitées), :35-59 (regroupements Mois, Nationalité, Motif, Hôtel ;
   filtres Résidents / Non-résidents), :60-79 (action, regroupée par mois
   par défaut, vues pivot, graphique, liste) ; models/guest_stats.py:5-97
   (une ligne par fiche des séjours Arrivé ou Parti : 1 arrivée, ses nuits
   = nuitées ; mois « 2026-10 » par to_char, voir écart 3 ; relue à chaque
   lecture) ; models/guest_registration.py:174-180 (résident = pays de
   résidence, à défaut nationalité, égal au pays de l'hôtel). Menu de
   regroupement d'un en-tête de pivot : odoo18/addons/web/static/src/views/
   pivot/pivot_header.xml:4-74 (« Ajouter un groupe personnalisé »,
   web/i18n/fr.po). Modèle visuel : captures/nouvelles/14_stats_pivot.png,
   ref_muk/033 (colonnes Non-résident puis Résident).

Accroche (douleurs), toutes sourcées :
- docs/etude_comparative/benchmark_afrique_odoo.md:13 et :66 — loi
  n° 2016/006, art. 28 : « la violation des obligations de police en
  matière d'enregistrement des clients » est sanctionnée (carte bouclier) ;
  :66 — la fiche à relever : nom, prénoms, date de naissance, nationalité,
  pièce, dates (carte fiche) ; :13 et :66 — « aucun modèle officiel de
  fiche/registre trouvé en ligne » (carte interrogation, formulée « trouvé
  en ligne », pas « publié ») ;
- :69 — statistiques exigées par le MINTOUL (art. 16), amende de 50 000 à
  500 000 FCFA (art. 45) (carte graphe et voix) ;
- :80 — Côte d'Ivoire : la fiche d'hébergement numérisée (HORA, Police
  nationale, 2023), « ex-fiche papier » (carte globe).

Résultats : « 1 clic » — le check-in crée et pré-remplit la fiche du client
principal (hotel_reservation.py:96-110) ; « 6 informations » obligatoires
suivies par « Il manque » (guest_registration.py:182-206, 234-241) ;
« 4 regroupements » des statistiques : Mois, Nationalité, Motif, Hôtel
(guest_stats_views.xml:43-57).

Données (fictives, demo.py) : Complexe Hôtelier — Démo, Démo Hôtellerie
SARL ; Estelle Ngono, RES/2026/0214, chambre 204 [CFT], 2 adultes, du 14 au
16/10/2026 ; Martin Ebode (RES/2026/0209, Kribi, chambre 201 [CFT] comme
dans t07) et Claire Durand (RES/2026/0201, Lyon, France, chambre 401
[VIP] comme dans t02) ; leurs montants comme dans t01. Ajoutés ici, fictifs :
Arnaud Ngono (l'accompagnant d'Estelle, repris de scenarios/c7_conformite.py),
dates de naissance et numéros de pièce, adresse « Bastos Yaoundé ». Le
contact d'Estelle porte déjà sa nationalité et sa pièce (cliente connue).
Les statistiques d'août à octobre 2026 sont celles de c7 (sommes
vérifiées), octobre détaillé par nationalité (sommes égales aux totaux).

Écarts relevés dans l'application, rejoués tels quels ou évités :
1. Le registre de police (Facturation → Registre de police (impression))
   ne s'imprime pas depuis l'interface : action_print place des dates dans
   le contexte (wizard/police_register_wizard.py:65-68) ; le client web les
   renvoie sérialisées en chaînes (odoo18 web/static/src/webclient/actions/
   action_service.js:1322-1326, reports/utils.js:14-20 ; controllers/
   report.py:35-37) et le gabarit appelle strftime dessus
   (report/police_register_report.xml:66) : QWebException. La vidéo ne
   montre donc pas ce PDF ; elle montre le registre des clients (liste) et
   la fiche imprimée, qui fonctionnent.
2. La colonne « Registre » des listes de réservations affiche « Aucune
   fiche » en rouge sur toutes les réservations pas encore arrivées
   (hotel_reservation.py:52-53, views:62-66) : rejoué tel quel sur les
   arrivées du jour, sans commentaire.
3. Le mois des statistiques s'affiche au format ISO « 2026-10 »
   (guest_stats.py:83, to_char 'YYYY-MM') : rejoué tel quel.
4. Le bandeau s'affiche sans espace après les deux-points (« Registre des
   clients :1 fiche(s)… », champ en ligne collé au libellé,
   hotel_reservation_views.xml:29-30 ; captures/10) : rejoué tel quel.
5. L'aide « Arrivées du jour » promet qu'au check-in « le registre des
   clients s'ouvre » (aite_hotel_management/views/hotel_reservation_views.xml
   :286) : aucune fenêtre ne s'ouvre, on reste sur la réservation avec le
   bandeau (action_checkin rend True) ; la vidéo montre le comportement réel.
6. Une nouvelle ligne reçoit d'office Résidence = pays de l'hôtel, colonne
   masquée (hotel_reservation.py:143-144, views:20) : un étranger dont on ne
   change que la nationalité serait compté résident. L'accompagnant de la
   vidéo est camerounais : sans effet ici.
7. « Mémoriser sur la fiche client » écrit sur le contact sans sudo
   (guest_registration.py:282-298) : refusé au seul profil Réception. Non
   montré.

Captures de référence (modèle visuel, jamais incrustées) : ref_muk/023,
026, 027, 032, 033, 306 ; captures/10, 11, 12, nouvelles/13, nouvelles/14.

Voix : « check-inne » pour que Kokoro ne lise pas « check-in » à
l'anglaise (comme t01) ; « Aïte haousse », « Aïte Consulting ».
"""

import demo
from ecrans import (APPS_PROFIL, ICONES, bouton, champ, cp_fiche, deux_colonnes, e, entree, fenetre_muk, groupe,
                    icone, navigateur, onglets, statusbar, titre_fiche, vue_fiche, vue_libre)
from marketing import bulle, dezoom, reaction, zoom
from moteur import anneau, animer, cacher, choisir, clic, classe, curseur, defiler, etat, montrer, pause, saisir, texte, vue

NOM, ROLE = demo.POSTES['reception']            # Mireille Ateba, réceptionniste
DIRECTRICE = demo.POSTES['direction'][0]        # Danielle Eyenga
APP = 'app-t6'
MENUS = ['Front Desk', 'Réservations', 'Espaces & Prestations', 'Notes de chambre en attente', 'Facturation',
         'Fidélité', 'Gouvernante']
MENUS_DIR = ['Direction', 'Front Desk', 'Réservations', 'Espaces & Prestations', 'Notes de chambre en attente',
             'Facturation', 'Fidélité', 'Gouvernante', 'Configuration']
MENU_FD = '#app-t6 .o-haut .menu.actif'
SOLDE = '57 000 FCFA'                 # le folio d'Estelle après l'acompte (t01)
CHECKIN_REEL = '14/10/2026 14:06:12'  # comme t01

# ------------------------------------------------------------ icônes --
# Dessinées ici (oi-group, fa-cog, fa-download, sélecteur de vues) :
# ecrans.ICONES n'a pas ces glyphes, on ne le modifie pas.
CALQUES = ('<svg viewBox="0 0 24 24" fill="#fff"><path d="M12 3l9 4.5-9 4.5-9-4.5z"/>'
           '<path d="M4.6 11.2L12 15l7.4-3.8L21 12l-9 4.5L3 12z"/><path d="M4.6 15.7L12 19.5l7.4-3.8L21 16.5 12 21l-9-4.5z"/></svg>')
ENGRENAGE = ('<svg viewBox="0 0 24 24" fill="currentColor"><path d="M10.3 2h3.4l.5 2.6 1.8.8 2.2-1.5 2.4 2.4-1.5 2.2.8 '
             '1.8 2.6.5v3.4l-2.6.5-.8 1.8 1.5 2.2-2.4 2.4-2.2-1.5-1.8.8-.5 2.6h-3.4l-.5-2.6-1.8-.8-2.2 1.5-2.4-2.4 '
             '1.5-2.2-.8-1.8L2 13.7v-3.4l2.6-.5.8-1.8-1.5-2.2 2.4-2.4 2.2 1.5 1.8-.8zM12 8.6a3.4 3.4 0 100 6.8 3.4 3.4 '
             '0 000-6.8z"/></svg>')
TELECHARGER = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" '
               'stroke-linejoin="round"><path d="M12 3v12M7 10l5 5 5-5M4 20h16"/></svg>')
V_PIVOT = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" '
           'height="16" rx="1"/><path d="M3 9h18M3 14h18M9 4v16M15 4v16"/></svg>')
V_GRAPHE = '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M3 20V9l5 4 4-7 4 5 5-4v13z"/></svg>'
V_LISTE = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round">'
           '<path d="M4 6h16M4 12h16M4 18h16"/></svg>')
REGLAGES = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">'
            '<path d="M4 7h10M18 7h2M4 17h4M12 17h8"/><circle cx="16" cy="7" r="2"/><circle cx="10" cy="17" r="2"/></svg>')


def ico(svg, classe_='ico'):
    return '<span class="%s">%s</span>' % (classe_, svg)


def engrenage():
    return ico(ENGRENAGE, 'ico t06-gear')


# ---------------------------------------------------- barre de recherche --
def facette_filtre(lib):
    return ('<span class="facette">%s<span class="ell">%s</span><span class="fx">×</span></span>'
            % (icone('filtre', 'fic'), e(lib)))


def facette_groupe(lib):
    return ('<span class="facette">%s<span class="ell">%s</span><span class="fx">×</span></span>'
            % (ico(CALQUES, 'fic'), e(lib)))


def facette_champ(champ_, valeur):
    """La facette d'un champ (Odoo 18) : le libellé du champ dans la pastille colorée."""
    return ('<span class="facette t06-fch"><span class="t06-fch-l">%s</span><span class="ell">%s</span>'
            '<span class="fx">×</span></span>' % (e(champ_), e(valeur)))


def recherche6(facettes):
    return ('<div class="recherche">%s%s<span class="ph">Rechercher…</span><span class="deroule">▾</span></div>'
            % (icone('loupe', 'loupe'), facettes))


def cp_liste6(titre, facettes, pager, ident_pager=None):
    return ('<div class="cp"><span class="bt primaire">Nouveau</span><span class="titre">%s %s</span>%s'
            '<span class="pager"%s>%s</span></div>'
            % (e(titre), engrenage(), recherche6(facettes), ' id="%s"' % ident_pager if ident_pager else '', e(pager)))


def tete(colonnes, fin=''):
    gab = ' '.join(c[1] for c in colonnes)
    return ('<div class="tete" style="grid-template-columns:40px %s"><span class="cb"></span>%s</div>'
            % (gab, ''.join('<span class="ell%s" data-layout-allow-overflow>%s</span>' % (' d' if len(c) > 2 else '',
                                                                                       e(c[0]))
                            for c in colonnes) + fin))


def ligne6(ident, colonnes, cellules, classe_='', masque=False):
    gab = ' '.join(c[1] for c in colonnes)
    cs = []
    for k, c in enumerate(cellules):
        if isinstance(c, tuple):
            cs.append(c[0])
        else:
            cs.append('<span class="ell%s">%s</span>' % (' d' if len(colonnes[k]) > 2 else '', e(c)))
    return ('<div class="ligne%s%s" id="%s" style="grid-template-columns:40px %s"><span class="cb"></span>%s</div>'
            % (' ' + classe_ if classe_ else '', ' masque' if masque else '', ident, gab, ''.join(cs)))


def badge(texte_, genre, ident=None):
    return ('<span><span class="puce %s"%s>%s</span></span>' % (genre, ' id="%s"' % ident if ident else '', e(texte_)),)


def case(coche=False):
    return ('<span><span class="case%s"><i></i></span></span>' % (' coche' if coche else ''),)


# ===================================================== 1. Arrivées du jour --
COLS_ARR = [('Référence', '140px'), ('Client', '134px'), ('Arrivée', '172px'), ('Départ', '172px'), ('Nuits', '56px', 'd'),
            ('Nb chambres', '116px', 'd'), ('Total hébergement (HT)', '206px', 'd'), ('Solde folio', '112px', 'd'),
            ('Registre', '134px'), ('État', '1fr')]


def arrivee(ident, ref, client, arr, dep, nuits, total, solde):
    return ligne6(ident, COLS_ARR, [('<span class="lien ell">%s</span>' % e(ref),), client, arr, dep, nuits, '1', total,
                                    solde, badge('Aucune fiche', 'rouge'), badge('Confirmée', 'info')], 't06-info')


ARRIVEES = vue_libre('t06-arr', cp_liste6('Arrivées du jour', facette_filtre('Arrivées du jour'), '1-3 / 3') + (
    '<div class="liste">%s%s%s%s<div class="total" style="grid-template-columns:40px %s"><span></span>%s</div></div>'
    % (tete(COLS_ARR),
       arrivee('t06-a0', 'RES/2026/0201', 'Claire Durand', '14/10/2026 18:00:00', '15/10/2026 12:00:00', '1',
               '120 000 FCFA', '0 FCFA'),
       arrivee('t06-a1', demo.RESA, demo.CLIENT, demo.ARRIVEE, demo.DEPART, '2', '90 000 FCFA', SOLDE),
       arrivee('t06-a2', 'RES/2026/0209', 'Martin Ebode', '14/10/2026 14:00:00', '17/10/2026 12:00:00', '3',
               '105 000 FCFA', '35 000 FCFA'),
       ' '.join(c[1] for c in COLS_ARR),
       ''.join('<span class="d">%s</span>' % e(t) if t else '<span></span>'
               for t in ['', '', '', '', '', '', '315 000 FCFA', '', '', '']))), initiale=True)

# ========================================================= 2. Réservation --
LIGNE_CH = (
    '<div class="table t06-tab"><div class="t-tete" style="grid-template-columns:%(g)s">%(t)s</div>'
    '<div class="t-ligne" style="grid-template-columns:%(g)s"><span>Confort</span><span>204 [CFT]</span>'
    '<span class="d">2</span><span class="d">0</span><span></span><span class="d">2</span><span class="d">45 000 FCFA</span>'
    '<span class="d">90 000 FCFA</span><span class="t06-ech">%(ech)s</span></div>'
    '<div class="t-ajout">Ajouter une ligne</div></div>'
    % {'g': '1fr 170px 110px 110px 150px 90px 170px 190px 40px',
       't': ''.join('<span class="ell%s">%s</span>' % (' d' if d else '', e(x)) for x, d in (
           ('Type', 0), ('Chambre', 0), ('Adultes', 1), ('Enfants', 1), ('Occupants', 0), ('Nuits', 1),
           ('Prix / nuit', 1), ('Sous-total (HT)', 1), ('', 0))),
       'ech': icone('echange')})
FEUILLE_RESA = (
    titre_fiche(demo.RESA)
    + deux_colonnes(
        groupe('Client', [champ('Client', demo.CLIENT, lien_=True), champ('Téléphone', demo.CLIENT_TEL),
                          champ('E-mail', demo.CLIENT_MAIL), champ('Hôtel', demo.HOTEL, lien_=True)])
        + groupe('Canal & commission', [champ('Canal', 'Direct / comptoir')]),
        groupe('Séjour', [champ('Arrivée', demo.ARRIVEE, gras=True), champ('Départ', demo.DEPART, gras=True),
                          champ('Nuits', '2'), champ('Total hébergement (HT)', '90 000 FCFA')])
        + '<div class="masque t06-cireel" id="t06-cireel">%s</div>' % champ('Check-in réel', CHECKIN_REEL)
        + groupe('Occupation', [champ('Nb chambres', '1'), champ('Adultes', '2'), champ('Enfants', '0')]))
    + onglets(['Chambres', 'Demandes particulières']) + LIGNE_CH)
BANDEAUX = (
    '<div class="bandeau masque" id="t06-bandeau">%s<span><b>Registre des clients :</b>1 fiche(s) à compléter · '
    '1 occupant(s) sans fiche — <span class="act" id="t06-completer">compléter maintenant</span></span></div>'
    '<div class="bandeau t06-ok-b masque" id="t06-bandeau-ok">%s<b>Registre des clients à jour.</b>'
    '<span class="act" id="t06-imprimer">Imprimer les fiches</span></div>' % (icone('fiche'), icone('coche')))
B_CONF = [bouton('t06-b-checkin', 'Check-in', 'primaire'), bouton(None, 'Encaisser un acompte'),
          bouton(None, 'Envoyer la confirmation'), bouton(None, "Fiches d'enregistrement", ico='imprimer'),
          bouton(None, 'No-show'), bouton(None, 'Annuler')]
B_ARRIVE = [bouton(None, 'Check-out', 'primaire'), bouton(None, 'Encaisser un acompte'),
            bouton(None, 'Envoyer la confirmation'), bouton(None, "Fiches d'enregistrement", ico='imprimer'),
            bouton(None, 'Annuler')]
RESA = vue_fiche('t06-resa', cp_fiche('Arrivées du jour', demo.RESA, '2 / 3', stats=[
    ('t06-st-folio', 'document', 'Folio', SOLDE), ('t06-st-fiches', 'fiche', 'Fiches clients', '0/2')]),
    B_CONF, statusbar('t06-sb', ['Brouillon', 'Confirmée', 'Arrivé', 'Parti'], 1), FEUILLE_RESA, bandeau=BANDEAUX,
    boutons_apres=[B_ARRIVE])

# ====================================================== 3. Fiches clients --
COLS_F = [('Chambre', '104px'), ('Nom', '86px'), ('Prénom(s)', '98px'), ('Date de naissance', '132px'),
          ('Nationalité', '108px'), ('Type de pièce', '218px'), ('N° de pièce', '112px'), ('Client principal', '84px'),
          ('Signée par le client', '84px'), ('Il manque', '1fr'), ('Fiche', '120px'), ('', '30px')]
CNI = "Carte nationale d'identité"
MANQUE_NOUVELLE = ['le nom, le prénom, la date de naissance, le type de pièce, le numéro de pièce',
                   'le prénom, la date de naissance, le type de pièce, le numéro de pièce',
                   'la date de naissance, le type de pièce, le numéro de pièce',
                   'le type de pièce, le numéro de pièce', 'le numéro de pièce', '']


def cel(ident, valeur=''):
    """Une cellule de la ligne en saisie (champ de liste éditable)."""
    return (entree(ident, '', valeur, classe='entree t06-c'),)


IMPRIMANTE = ('<span class="t06-print">%s</span>' % ICONES['imprimer'],)
FICHE_ESTELLE = ligne6('t06-f0', COLS_F, [
    '204 [CFT]', 'Ngono', 'Estelle', cel('t06-f0-dn'), 'Cameroun', CNI, '114208815', case(True), case(False),
    ('<span class="ell" id="t06-f0-im">la date de naissance</span>',), badge('À compléter', 'orange', 't06-f0-et'),
    IMPRIMANTE], 'avert')
FICHE_ARNAUD = ligne6('t06-f1', COLS_F, [
    '204 [CFT]', cel('t06-f1-nom'), cel('t06-f1-pre'), cel('t06-f1-dn'), cel('t06-f1-nat', 'Cameroun'),
    cel('t06-f1-type'), cel('t06-f1-num'), case(False), case(False),
    ('<span class="ell" id="t06-f1-im">%s</span>' % e(MANQUE_NOUVELLE[0]),),
    badge('À compléter', 'orange', 't06-f1-et'), IMPRIMANTE], 'avert t06-edit', masque=True)
CP_FICHES = (
    '<div class="cp"><span class="pile t06-pbts"><span class="bt primaire" id="t06-f-nouveau">Nouveau</span>'
    '<span class="t06-sbts masque" id="t06-f-sbts"><span class="bt primaire" id="t06-f-save">Enregistrer</span>'
    '<span class="bt gris">Ignorer</span></span></span>'
    '<div class="fil" id="t06-f-fil"><span class="parent"><span>Arrivées du jour</span><span class="t06-sep">/</span>'
    '<span id="t06-f-fil-resa">%s</span></span><span class="ref">Fiches clients — %s %s</span></div>%s'
    '<span class="pager" id="t06-f-pager">1-1 / 1</span></div>'
    % (e(demo.RESA), e(demo.RESA), engrenage(), recherche6(facette_champ('Réservation', demo.RESA))))
FICHES = vue_libre('t06-fiches', CP_FICHES + '<div class="liste t06-lf">%s%s%s</div>' % (
    tete(COLS_F, '<span class="t06-opt">%s</span>' % REGLAGES), FICHE_ESTELLE, FICHE_ARNAUD))

# ======================================= 4. La fiche d'enregistrement (PDF) --
def pdf_page(ident, num, nom, prenom, ne, tel, piece):
    """Une page du PDF « Fiche d'enregistrement » (registration_card_report.xml), telle que l'imprime Odoo."""
    def lig(a, va, b, vb):
        return '<tr><td><b>%s</b></td><td>%s</td><td><b>%s</b></td><td>%s</td></tr>' % (e(a), va, e(b), vb)
    corps = (
        '<tr><th colspan="4">IDENTITÉ</th></tr>'
        + lig('Nom', '<span class="t06-maj">%s</span>' % e(nom), 'Prénom(s)', e(prenom))
        + lig('Né(e) le', e(ne), 'À', '') + lig('Sexe', '', 'Nationalité', 'Cameroun')
        + lig('Profession', '', 'Téléphone', e(tel))
        + '<tr><th colspan="4">PIÈCE D\'IDENTITÉ</th></tr>'
        + lig('Type', e(CNI), 'Numéro', e(piece)) + lig('Délivrée le', '', 'Par', '')
        + '<tr><th colspan="4">DOMICILE &amp; DÉPLACEMENT</th></tr>'
        + '<tr><td><b>Adresse</b></td><td colspan="3">Bastos Yaoundé</td></tr>'
        + lig('Pays de résidence', 'Cameroun', 'Motif du séjour', 'Loisirs / tourisme')
        + lig('Provenance', '', 'Destination', '')
        + '<tr><th colspan="4">SÉJOUR</th></tr>'
        + lig('Arrivée', '14/10/2026', 'Départ prévu', '16/10/2026') + lig('Nuits', '2', 'Accompagnants', '1'))
    return (
        '<div class="t06-page" id="%s"><div class="t06-soc">%s</div>'
        '<div class="t06-ph"><div><h3>FICHE D\'ENREGISTREMENT CLIENT</h3><div class="t06-gris">Registre des voyageurs — %s'
        '</div></div><div class="t06-ref"><div><b>N°</b> %s</div><div><b>Chambre</b> 204</div>'
        '<div><b>Réservation</b> %s</div></div></div>'
        '<table class="t06-pt" id="%s-id">%s</table>'
        '<div class="t06-sig" id="%s-sig"><div><b>Signature du client</b><i></i><small>Je certifie l\'exactitude des '
        'informations ci-dessus.</small></div><div><b>Cachet et signature de l\'établissement</b><i></i>'
        '<small>Fiche établie le 14/10/2026.</small></div></div>'
        '<p class="t06-legal">Document établi conformément aux obligations d\'enregistrement des clients des '
        'établissements d\'hébergement touristique. Conservé par l\'établissement et présenté à toute réquisition '
        'des autorités compétentes.</p></div>'
        % (ident, e(demo.SOCIETE), e(demo.HOTEL), e(num), e(demo.RESA), ident, corps, ident))


PDF = ('<div class="t06-pdf masque" id="t06-pdf" data-layout-allow-overlap data-layout-allow-occlusion>%s%s</div>'
       % (pdf_page('t06-p1', 'FICHE/2026/00412', 'Ngono', 'Estelle', '12/03/1991', demo.CLIENT_TEL, '114208815'),
          pdf_page('t06-p2', 'FICHE/2026/00413', 'Ngono', 'Arnaud', '27/08/1989', '', '116502371')))

# ============================================== 5. Le registre des clients --
DEROULANT = ('<div class="t06-dd masque" id="t06-dd" data-layout-allow-overlap data-layout-allow-occlusion>%s</div>'
             % ''.join('<div class="t06-dd-i" id="t06-dd-%s">%s</div>' % (i, e(t)) for i, t in (
                 ('tdb', 'Tableau de bord'), ('rap', 'Réservation rapide'), ('arr', 'Arrivées du jour'),
                 ('dep', 'Départs du jour'), ('reg', 'Registre des clients'), ('pre', 'Clients présents'))))
COLS_R = [('Arrivée', '112px'), ('Départ', '112px'), ('Chambre', '104px'), ('Nom', '100px'), ('Prénom(s)', '100px'),
          ('Date de naissance', '136px'), ('Nationalité', '110px'), ('Type de pièce', '222px'), ('N° de pièce', '112px'),
          ('Fiche', '124px'), ('Signée par le client', '1fr')]
GROUPES = [('14 oct. 2026', 4), ('13 oct. 2026', 3), ('12 oct. 2026', 5), ('11 oct. 2026', 2), ('10 oct. 2026', 4)]


def groupe_r(ident, lib, n, ouvert=False):
    return ('<div class="groupe t06-gr" id="%s"><span class="t06-car">%s</span>%s (%d)</div>'
            % (ident, '▾' if ouvert else '▸', e(lib), n))


def personne(ident, dep, ch, nom, prenom, ne, nat, piece, num_, complete):
    return ligne6(ident, COLS_R, ['14/10/2026', dep, ch, nom, prenom, ne, nat, piece, num_,
                                  badge('Complète', 'vert') if complete else badge('À compléter', 'orange'),
                                  case(False)], '' if complete else 'avert')


TETE_R = tete(COLS_R, '<span class="t06-opt">%s</span>' % REGLAGES)
REG_A = ('<div class="liste t06-lr" id="t06-rg-a">%s%s</div>'
         % (TETE_R, ''.join(groupe_r('t06-rg-g%d' % i, lib, n) for i, (lib, n) in enumerate(GROUPES))))
REG_B = ('<div class="liste t06-lr masque" id="t06-rg-b">%s%s%s%s</div>' % (
    TETE_R, groupe_r('t06-rg-b-g0', GROUPES[0][0], GROUPES[0][1], ouvert=True),
    personne('t06-rg-claire', '15/10/2026', '401 [VIP]', 'Durand', 'Claire', '', 'France', '', '', False)
    + personne('t06-rg-arnaud', '16/10/2026', '204 [CFT]', 'Ngono', 'Arnaud', '27/08/1989', 'Cameroun', CNI,
               '116502371', True)
    + personne('t06-rg-estelle', '16/10/2026', '204 [CFT]', 'Ngono', 'Estelle', '12/03/1991', 'Cameroun', CNI,
               '114208815', True)
    + personne('t06-rg-martin', '17/10/2026', '201 [CFT]', 'Ebode', 'Martin', '', 'Cameroun', CNI, '112640339', False),
    ''.join(groupe_r('t06-rg-b-g%d' % i, lib, n) for i, (lib, n) in enumerate(GROUPES) if i)))
REGISTRE = vue_libre('t06-registre', cp_liste6('Registre des clients', facette_groupe("Date d'arrivée: Jour"),
                                               '1-5 / 5') + REG_A + REG_B)

ECRAN_RECEPTION = fenetre_muk(APP, 'Hôtel', MENUS, [ARRIVEES, RESA, FICHES, REGISTRE], actif='Front Desk',
                              societe=demo.SOCIETE, initiale=NOM[0], avatar='#185FA5', apps=APPS_PROFIL['reception'],
                              app_active='Hôtel', calques=DEROULANT + PDF)

# ================================== 6. Les statistiques (écran direction) --
# (libellé, [arrivées NR, nuitées NR, arrivées R, nuitées R, arrivées, nuitées])
MOIS = [('2026-08', [38, 96, 112, 251, 150, 347]), ('2026-09', [41, 118, 120, 290, 161, 408]),
        ('2026-10', [22, 71, 66, 185, 88, 256])]
TOTAL = [101, 285, 298, 726, 399, 1011]
PAYS_OCT = [('Cameroun', [3, 9, 63, 177, 66, 186]), ('Chine', [2, 6, None, None, 2, 6]),
            ('France', [9, 31, 2, 5, 11, 36]), ('Gabon', [3, 11, 1, 3, 4, 14]), ('Nigeria', [5, 14, None, None, 5, 14])]
# les sommes d'octobre par pays égalent la ligne du mois
assert [sum(v[i] or 0 for _, v in PAYS_OCT) for i in range(6)] == MOIS[2][1]
assert [sum(v[i] for _, v in MOIS) for i in range(6)] == TOTAL


def n_(v):
    return '' if v is None else '{:,}'.format(v).replace(',', ' ')


def pv_tr(ident, lib, vals, niveau, ouvert=False, classe_=''):
    return ('<tr%s%s><th class="t06-pvh" style="padding-left:%dpx"%s>%s %s</th>%s</tr>'
            % (' id="%s"' % ident if ident else '', ' class="%s"' % classe_ if classe_ else '', 14 + 24 * niveau,
               '', '⊟' if ouvert else '⊞', e(lib), ''.join('<td>%s</td>' % n_(v) for v in vals)))


ENTETES = ('<tr><td class="vide"></td><th colspan="6">⊟ Total</th></tr>'
           '<tr><td class="vide"></td><th colspan="2">⊞ Non-résident</th><th colspan="2">⊞ Résident</th>'
           '<th colspan="2" class="t06-pv-vt"></th></tr>'
           '<tr><td class="vide"></td>%s</tr>' % ('<th class="m">Arrivées</th><th class="m">Nuitées</th>' * 3))


def pivot(ident, detail=False):
    lignes = pv_tr(None, 'Total', TOTAL, 0, ouvert=True, classe_='tot')
    for lib, vals in MOIS:
        if lib == '2026-10':
            lignes += pv_tr('%s-oct' % ident, lib, vals, 1, ouvert=detail)
            if detail:
                lignes += ''.join(pv_tr('%s-%s' % (ident, p[:3].lower()), p, v, 2) for p, v in PAYS_OCT)
        else:
            lignes += pv_tr(None, lib, vals, 1)
    return '<table class="pv t06-pv%s" id="%s">%s%s</table>' % ('' if not detail else ' masque', ident, ENTETES, lignes)


VUES_PV = '<span class="t06-vues">%s</span>' % ''.join('<i class="%s">%s</i>' % ('on' if i == 0 else '', s)
                                                        for i, s in enumerate((V_PIVOT, V_GRAPHE, V_LISTE)))
STATS = vue_libre('t06-stats', (
    '<div class="cp"><span class="titre">Statistiques d\'hébergement</span>%s%s</div>'
    '<div class="pv-barre"><span class="bt primaire">Mesures ▾</span><span class="bt gris">⇄</span>'
    '<span class="bt gris">✥</span><span class="bt gris t06-dl">%s</span></div>'
    '<div class="t06-pvz" id="t06-pvz">%s%s</div>'
    % (recherche6(facette_groupe('Mois')), VUES_PV, ico(TELECHARGER), pivot('t06-pv-a'), pivot('t06-pv-b', True))),
    initiale=True)
MENU_PV = ('<div class="t06-pvm masque" id="t06-pvm" data-layout-allow-overlap data-layout-allow-occlusion>'
           '<div class="t06-pvm-i t06-sel">Mois</div><div class="t06-pvm-i" id="t06-pvm-nat">Nationalité</div>'
           '<div class="t06-pvm-i">Motif</div><div class="t06-pvm-i">Hôtel</div><div class="t06-pvm-sep"></div>'
           '<div class="t06-pvm-i t06-pvm-c">Ajouter un groupe personnalisé<span>▾</span></div></div>')
ECRAN_DIRECTION = fenetre_muk('app-t6d', 'Hôtel', MENUS_DIR, [STATS], actif='Facturation', societe='',
                              initiale=DIRECTRICE[0], avatar='#854F0B', apps=APPS_PROFIL['direction'],
                              app_active='Hôtel', calques=MENU_PV)

# Deux cadres de navigateur superposés : la réception, puis l'écran de la
# directrice qui se pose dessus (un changement d'écran, comme t04 et t08).
ECRAN = (navigateur(ECRAN_RECEPTION)
         + navigateur(ECRAN_DIRECTION, 't06-nav-dir').replace('class="navigateur"', 'class="navigateur masque"', 1))

CSS = """
/* t06 — registre des clients : listes resserrées, réservation, fiche PDF, pivot */
#app-t6 .o-haut, #app-t6d .o-haut { gap: 22px; font-size: 19px; }
#app-t6d .o-haut { gap: 18px; font-size: 18px; }
#app-t6 .cp .titre, #app-t6d .cp .titre { display: inline-flex; align-items: center; gap: 10px; }
.t06-gear { width: 16px; height: 16px; display: inline-flex; color: #343A40; }
.t06-gear svg { width: 16px; height: 16px; }
#app-t6 .facette .fic svg, #app-t6d .facette .fic svg { width: 100%; height: 100%; }
#app-t6 .t06-fch { padding-left: 0; }
#app-t6 .t06-fch-l { height: 34px; padding: 0 10px; display: inline-flex; align-items: center; background: var(--o-prim); color: #fff; }
#app-t6 .liste .tete, #app-t6 .liste .ligne, #app-t6 .liste .total { font-size: 17px; column-gap: 10px; padding-right: 14px; }
#app-t6 .liste .ligne { height: 54px; }
#app-t6 .liste .tete { position: relative; }
#app-t6 .liste .ligne.t06-info { color: #0B6178; }
#app-t6 .liste .ligne.t06-info .lien { color: inherit; }
#app-t6 .liste .ligne.survol { background: #E6EEF3; }
#app-t6 .liste .ligne.t06-vert { color: #1B6E2F; }
#app-t6 .liste .puce { font-size: 15px; height: 28px; }
#app-t6 .liste .case i { width: 20px; height: 20px; }
.t06-opt { position: absolute; right: 12px; top: 15px; width: 22px; height: 22px; color: #495057; display: inline-flex; }
.t06-opt svg { width: 22px; height: 22px; }
/* la réservation, resserrée comme dans t01 */
#t06-resa .bb-groupe .bt { font-size: 18px; padding: 0 13px; height: 42px; }
#t06-resa .bb-groupe .bt .ico { width: 17px; height: 17px; }
#t06-resa .st-et { font-size: 18px; height: 42px; }
#app-t6 .st-et:not(.actif) { color: #5C636A; }
#t06-resa .ch { min-height: 34px; font-size: 18px; grid-template-columns: 230px 1fr; }
#t06-resa .grp { margin-bottom: 12px; }
#t06-resa .grp-t { padding-bottom: 6px; margin-bottom: 8px; }
#t06-resa .f-titre { font-size: 36px; margin-bottom: 10px; }
#t06-resa .feuille { padding: 16px 34px 30px; }
#app-t6 .t06-cireel { margin: -12px 0 12px; }
#app-t6 .t06-tab .t-tete { height: 46px; font-size: 17px; }
#app-t6 .t06-tab .t-ligne { height: 48px; font-size: 17px; }
#app-t6 .t06-tab .t-ajout { height: 46px; font-size: 17px; }
#app-t6 .t06-ech { color: #3F6A83; display: inline-flex; width: 22px; height: 22px; }
#app-t6 .t06-ech svg { width: 22px; height: 22px; }
#app-t6 .bandeau.t06-ok-b { background: #D1E7DD; border-color: #A3CFBB; color: #0A3622; }
#app-t6 .bandeau.t06-ok-b .act { color: #0A3622; margin-left: 10px; }
/* fiches clients : liste éditable */
.t06-pbts { display: inline-flex; }
.t06-sbts { display: inline-flex; gap: 6px; white-space: nowrap; }
.t06-sep { margin: 0 8px; color: var(--o-texte-3); }
#t06-f-fil .parent { display: flex; font-weight: 600; }
#t06-f-fil .ref { display: inline-flex; align-items: center; gap: 8px; }
#app-t6 .t06-lf .tete, #app-t6 .t06-lf .ligne { font-size: 16px; column-gap: 9px; padding-right: 10px; }
#app-t6 .t06-lf .ligne.avert { color: #8A6100; }
#app-t6 .t06-lf .ligne.t06-edit { background: #EEF3F6; }
.t06-c.entree { margin: 0; height: 32px; border-width: 0 0 1px 0; border-color: transparent; border-radius: 0; padding: 0 2px;
  font-size: 16px; background: transparent; color: inherit; }
.t06-c.entree .ph, .t06-c.entree .val { left: 2px; font-weight: 400; }
.t06-edit .t06-c.entree { border-color: #ADB5BD; }
.t06-c.entree.focus { border-color: var(--muk-prim); box-shadow: none; }
.t06-print { width: 18px; height: 18px; display: inline-flex; color: #3F6A83; }
.t06-print svg { width: 18px; height: 18px; }
/* menu déroulant « Front Desk » */
#app-t6 .t06-dd { position: absolute; left: 152px; top: 58px; width: 300px; z-index: 26; background: #fff; padding: 6px 0;
  border: 1px solid #DEE2E6; border-radius: 0 0 6px 6px; box-shadow: 0 12px 28px rgba(0,0,0,.20); }
#app-t6 .t06-dd-i { height: 46px; display: flex; align-items: center; padding: 0 22px; font-size: 19px; color: #212529; }
#app-t6 .t06-dd-i.survol { background: #E9ECEF; }
/* le registre des clients */
.t06-lr { position: absolute; left: 0; right: 0; top: 80px; }
#app-t6 .t06-lr .tete, #app-t6 .t06-lr .ligne { padding-right: 46px; }
#app-t6 .t06-gr { font-weight: 500; gap: 10px; background: #fff; height: 52px; font-size: 18px; }
.t06-car { width: 14px; color: #495057; }
#app-t6 .t06-lr .ligne { height: 52px; }
/* la fiche imprimée : le PDF, page par page */
.t06-pdf { position: absolute; left: 0; top: 0; right: 0; bottom: 0; z-index: 27; background: #525659;
  display: flex; justify-content: center; gap: 30px; padding-top: 20px; }
.t06-page { width: 720px; height: 1000px; flex: none; background: #fff; box-shadow: 0 10px 34px rgba(0,0,0,.45);
  padding: 22px 32px; color: #212529; font-size: 13px; }
.t06-soc { font-size: 14px; font-weight: 700; color: #495057; padding-bottom: 8px; border-bottom: 2px solid #495057; margin-bottom: 14px; }
.t06-ph { display: flex; justify-content: space-between; margin-bottom: 10px; }
.t06-ph h3 { margin: 0; font-size: 21px; font-weight: 700; }
.t06-gris { color: #6C757D; font-size: 13px; margin-top: 2px; }
.t06-ref { text-align: right; line-height: 1.5; }
.t06-pt { width: 100%; border-collapse: collapse; }
.t06-pt td, .t06-pt th { border: 1px solid #DEE2E6; padding: 4px 7px; height: 25px; text-align: left; font-size: 13px; }
.t06-pt th { background: #F8F9FA; font-weight: 700; }
.t06-pt td:nth-child(1), .t06-pt td:nth-child(3) { width: 22%; }
.t06-maj { text-transform: uppercase; }
.t06-sig { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-top: 14px; }
.t06-sig i { display: block; height: 52px; border: 1px solid #999; margin-top: 4px; }
.t06-sig small { display: block; margin-top: 3px; color: #6C757D; font-size: 11.5px; }
.t06-legal { margin: 10px 0 0; color: #6C757D; font-size: 11.5px; line-height: 1.4; }
/* statistiques : pivot de la directrice */
#app-t6d .cp .titre { font-size: 24px; }
.t06-vues { margin-left: auto; display: flex; }
.t06-vues i { width: 46px; height: 40px; display: flex; align-items: center; justify-content: center; background: #E9ECEF; color: #343A40; }
.t06-vues i + i { border-left: 1px solid #fff; }
.t06-vues i.on { background: #DCE6EC; box-shadow: inset 0 0 0 1px var(--muk-prim); }
.t06-vues svg { width: 20px; height: 20px; }
.t06-dl .ico { width: 18px; height: 18px; display: inline-flex; }
.t06-dl svg { width: 18px; height: 18px; }
.t06-pvz { position: relative; }
.t06-pvz .t06-pv { position: absolute; left: 0; top: 0; }
.t06-pv td, .t06-pv th { height: 40px; font-size: 18px; }
.t06-pv td { min-width: 96px; }
.t06-pvh { text-align: left; background: #F8F9FA !important; font-weight: 400 !important; min-width: 220px; }
.t06-pv tr.tot td, .t06-pv tr.tot th { font-weight: 600 !important; background: #F1F3F5 !important; }
.t06-pv .t06-pv-vt { border-top: 0; }
/* le menu de regroupement d'un en-tête du pivot */
.t06-pvm { position: absolute; left: 210px; top: 486px; width: 330px; z-index: 26; background: #fff; padding: 6px 0;
  border: 1px solid #DEE2E6; border-radius: 6px; box-shadow: 0 12px 28px rgba(0,0,0,.22); }
.t06-pvm-i { height: 42px; display: flex; align-items: center; padding: 0 18px 0 40px; font-size: 18px; color: #212529; position: relative; }
.t06-pvm-i.t06-sel::before { content: '✓'; position: absolute; left: 16px; color: #212529; font-weight: 700; }
.t06-pvm-i.survol { background: #E9ECEF; }
.t06-pvm-sep { height: 1px; background: #DEE2E6; margin: 6px 0; }
.t06-pvm-c { justify-content: space-between; color: #495057; padding-left: 18px; }
"""

TUTORIEL = {
    'slug': 't06-registre',
    'profil': 't06_registre',
    'numero': 6,
    'titre': 'Fiche de police, registre et statistiques MINTOUL : tout part du check-in',
    'fonction': 'Fiche de police et statistiques',
    'personnage': (NOM, ROLE),
    'accroche': {
        'kicker': 'Fiche de police et statistiques',
        'question': 'Un contrôle ce soir : votre registre est-il *à* *jour* ?',
        'douleurs': [('bouclier', 'Enregistrer chaque client : une obligation de police'),
                     ('fiche', 'Nom, naissance, nationalité, pièce : à relever pour chacun'),
                     ('graphe', 'Statistiques MINTOUL exigées, sous peine d\'amende'),
                     ('interrogation', 'Le format de la fiche ? Aucun modèle trouvé en ligne'),
                     ('globe', 'En Côte d\'Ivoire, la fiche papier est déjà numérique')],
        'voix': "Un contrôle de police ce soir : votre registre est-il à jour ? Une fiche pour chaque client, des "
                "statistiques pour le MINTOUL : la loi l'exige, sous peine d'amende.",
    },
    'revelation': {
        'promesse': "Au check-in, la fiche de police se crée et se pré-remplit. La réservation dit ce qui manque. "
                    "Le registre et les statistiques se tirent des mêmes fiches.",
        'voix': "Avec Aïte haousse, tout part du check-inne : la fiche se crée, et la réservation dit ce qui manque.",
    },
    'temps': ['Accueillir', 'Compléter', 'Contrôler', 'Mesurer'],
    'app': APP,
    'ecran': ECRAN,
    'css': CSS,
    'vues_initiales': {'odoo': 't06-arr'},
    'bulles': {
        'b-fiche': 'La fiche du client principal est déjà créée, pré-remplie depuis son contact.',
        'b-complete': 'Six informations obligatoires : la fiche passe Complète toute seule.',
        'b-pdf': 'Une page par occupant : identité, pièce, domicile, séjour, deux signatures.',
        'b-orange': 'En orange, les fiches à compléter. Les filtres À compléter et Non signées les isolent.',
        'b-stats': 'Une fiche, une arrivée ; ses nuits, les nuitées. Résident ou non : selon le pays de résidence.',
    },
    'reactions': {
        'r-ajour': 'Deux fiches sur deux : le registre du séjour est à jour.',
    },
    'etapes': [
        {'temps': 0, 'titre': 'Le check-in crée la fiche',
         'texte': 'Un clic sur Check-in : la fiche du client principal est créée, le bandeau dit ce qui manque.',
         'voix': "À quatorze heures, Estelle Ngono arrive avec un accompagnant. Mireille ouvre sa réservation et clique "
                 "sur check-inne : la fiche de police d'Estelle est créée aussitôt, et un bandeau dit ce qui manque.",
         'gestes': [pause(0.3), classe('#t06-a1', ajouter=['survol']), clic('#t06-a1', fx=0.09, d=0.7), vue('t06-resa'),
                    anneau('#t06-st-fiches', d=1.0), clic('#t06-b-checkin', d=0.6),
                    classe('#t06-sb-1', retirer=['actif']), classe('#t06-sb-2', ajouter=['actif']),
                    cacher('#t06-resa-ga', d=0.2), montrer('#t06-resa-gb', d=0.3, y=0),
                    montrer('#t06-cireel', d=0.3, y=0), montrer('#t06-bandeau', d=0.4, y=-10),
                    defiler('#t06-resa-defil', 52, d=0.4, avec=True),
                    zoom('#t06-bandeau', s=1.6, d=0.8, fx=0.3), bulle('b-fiche', '#t06-bandeau', cote='bas', d=3.0),
                    pause(2.8), dezoom(d=0.6)]},
        {'temps': 1, 'titre': 'Il ne manque que la date de naissance',
         'texte': 'La fiche reprend le contact ; « Il manque » dit le reste. Enregistrée, elle passe « Complète ».',
         'voix': "Le lien ouvre les fiches du séjour. Nom, prénom, nationalité et pièce viennent du contact ; il ne "
                 "manque que la date de naissance. Mireille la saisit, enregistre : la fiche passe Complète, toute seule.",
         'gestes': [clic('#t06-completer', d=0.6), vue('t06-fiches'), pause(0.3),
                    zoom('#t06-f0', s=1.25, d=0.8, fx=0.6), anneau('#t06-f0-im', d=1.4),
                    clic('#t06-f0-dn', fx=0.3, d=0.6), classe('#t06-f0', ajouter=['t06-edit']),
                    classe('#t06-f-nouveau', ajouter=['masque']), classe('#t06-f-sbts', retirer=['masque'], avec=True),
                    animer('#t06-f-fil', {'x': 0}, {'x': 140}, d=0.2, avec=True),
                    saisir('t06-f0-dn', '12/03/1991', d=0.8), texte('#t06-f0-im', ''),
                    clic('#t06-f-save', d=0.7), classe('#t06-f0', retirer=['avert', 't06-edit'], ajouter=['t06-vert']),
                    etat('#t06-f0-et', 'Complète', 'vert'),
                    classe('#t06-f-sbts', ajouter=['masque']), classe('#t06-f-nouveau', retirer=['masque'], avec=True),
                    animer('#t06-f-fil', {'x': 140}, {'x': 0}, d=0.2, avec=True),
                    bulle('b-complete', '#t06-f0-et', cote='bas', d=2.8), pause(2.4)]},
        {'temps': 1, 'titre': "L'accompagnant, en une ligne",
         'texte': 'Chambre et nationalité proposées ; « Il manque » raccourcit à chaque saisie.',
         'voix': "Pour l'accompagnant, Mireille clique sur Nouveau : une ligne suffit. La chambre et la nationalité sont "
                 "proposées d'office, et ce qui manque se réduit à chaque saisie. De retour sur la réservation, le "
                 "bandeau passe au vert : deux fiches complètes, pour deux occupants.",
         'gestes': [clic('#t06-f-nouveau', d=0.6), classe('#t06-f-nouveau', ajouter=['masque']),
                    classe('#t06-f-sbts', retirer=['masque'], avec=True),
                    animer('#t06-f-fil', {'x': 0}, {'x': 140}, d=0.2, avec=True), montrer('#t06-f1', d=0.3, y=0),
                    texte('#t06-f-pager', '1-2 / 2', avec=True),
                    saisir('t06-f1-nom', 'Ngono', d=0.45), curseur('#t06-f1-nom', d=0.3, avec=True),
                    texte('#t06-f1-im', MANQUE_NOUVELLE[1]),
                    saisir('t06-f1-pre', 'Arnaud', d=0.45), curseur('#t06-f1-pre', d=0.3, avec=True),
                    texte('#t06-f1-im', MANQUE_NOUVELLE[2]),
                    saisir('t06-f1-dn', '27/08/1989', d=0.6), curseur('#t06-f1-dn', d=0.3, avec=True),
                    texte('#t06-f1-im', MANQUE_NOUVELLE[3]),
                    choisir('t06-f1-type', CNI), curseur('#t06-f1-type', d=0.3, avec=True),
                    texte('#t06-f1-im', MANQUE_NOUVELLE[4]),
                    saisir('t06-f1-num', '116502371', d=0.6), curseur('#t06-f1-num', d=0.3, avec=True),
                    texte('#t06-f1-im', MANQUE_NOUVELLE[5]),
                    clic('#t06-f-save', d=0.6), classe('#t06-f1', retirer=['avert', 't06-edit'], ajouter=['t06-vert']),
                    etat('#t06-f1-et', 'Complète', 'vert'),
                    classe('#t06-f-sbts', ajouter=['masque']), classe('#t06-f-nouveau', retirer=['masque'], avec=True),
                    animer('#t06-f-fil', {'x': 140}, {'x': 0}, d=0.2, avec=True),
                    dezoom(d=0.5), clic('#t06-f-fil-resa', d=0.6), cacher('#t06-bandeau', d=0.05),
                    montrer('#t06-bandeau-ok', d=0.05, y=0, avec=True), texte('#t06-st-fiches-v', '2/2', avec=True),
                    vue('t06-resa', avec=True), anneau('#t06-bandeau-ok', d=1.2, decale=0.3),
                    anneau('#t06-st-fiches', d=1.0), reaction('r-ajour', d=2.8), pause(1.4)]},
        {'temps': 1, 'titre': "La fiche d'enregistrement, prête à signer",
         'texte': 'Un seul PDF, une page par occupant, avec les deux cadres de signature.',
         'voix': "Imprimer les fiches : une page par occupant, avec l'identité, la pièce, le domicile et le séjour, "
                 "puis deux cadres de signature, pour le client et pour l'établissement.",
         'gestes': [clic('#t06-imprimer', d=0.6), montrer('#t06-pdf', d=0.5, y=30), pause(0.6),
                    zoom('#t06-p1-id', s=1.45, d=0.8, fx=0.9, fy=0.25), bulle('b-pdf', '#t06-p1-id', cote='droite', d=2.8),
                    pause(2.6), zoom('#t06-p1-sig', s=1.5, d=0.7, fx=0.5), anneau('#t06-p1-sig', d=1.4),
                    pause(0.6), dezoom(d=0.6), anneau('#t06-p2', d=1.0)]},
        {'temps': 2, 'titre': 'Le registre des clients',
         'texte': "Toutes les personnes hébergées, jour par jour : l'état à présenter en cas de contrôle.",
         'voix': "Le soir, Mireille ouvre le registre des clients : toutes les personnes hébergées, jour après jour. "
                 "Les fiches incomplètes ressortent en orange, comme celle de Claire Durand. C'est l'état à présenter "
                 "en cas de contrôle.",
         'gestes': [cacher('#t06-pdf', d=0.3), clic(MENU_FD, d=0.6), montrer('#t06-dd', d=0.25, y=-8),
                    classe('#t06-dd-reg', ajouter=['survol']), clic('#t06-dd-reg', d=0.5), cacher('#t06-dd', d=0.15),
                    vue('t06-registre'), pause(0.4), clic('#t06-rg-g0', fx=0.1, d=0.6), cacher('#t06-rg-a', d=0.15),
                    montrer('#t06-rg-b', d=0.3, y=0, avec=True), pause(0.4), anneau('#t06-rg-claire', d=1.3),
                    anneau('#t06-rg-martin', d=1.2), bulle('b-orange', '#t06-rg-martin', cote='bas', d=3.0), pause(1.6),
                    anneau('#t06-rg-estelle', d=1.0)]},
        {'temps': 3, 'titre': "Les statistiques d'hébergement",
         'texte': 'Côté direction : arrivées et nuitées, résidents et non-résidents, par mois et par nationalité.',
         'voix': "En fin de mois, Danielle, la directrice, ouvre les statistiques d'hébergement : arrivées et nuitées, "
                 "résidents et non-résidents, tirées des mêmes fiches. Un clic sur le mois, puis Nationalité : le "
                 "détail par pays.",
         'gestes': [montrer('#t06-nav-dir', d=0.5, y=0), pause(0.6), anneau('#t06-pv-a tr.tot', d=1.2),
                    clic('#t06-pv-a-oct th', fx=0.3, d=0.6), montrer('#t06-pvm', d=0.25, y=-6),
                    classe('#t06-pvm-nat', ajouter=['survol']), clic('#t06-pvm-nat', d=0.5), cacher('#t06-pvm', d=0.15),
                    cacher('#t06-pv-a', d=0.15), montrer('#t06-pv-b', d=0.3, y=0, avec=True),
                    zoom('#t06-pv-b', s=1.3, d=0.8, fx=0.7, fy=0.75), anneau('#t06-pv-b-fra', d=1.2),
                    bulle('b-stats', '#t06-pv-b-fra', cote='droite', d=3.0), pause(2.8), dezoom(d=0.6)]},
    ],
    'resultats': {
        'titre': 'Un registre qui suit chaque séjour',
        'cartes': [
            {'valeur': '1', 'compter': 1, 'unite': 'clic', 'icone': 'fiche',
             'texte': 'au check-in : la fiche du client principal est créée et pré-remplie depuis son contact'},
            {'valeur': '6', 'compter': 6, 'unite': 'informations', 'icone': 'coche',
             'texte': 'obligatoires suivies par « Il manque » : la fiche passe Complète toute seule'},
            {'valeur': '4', 'compter': 4, 'unite': 'regroupements', 'icone': 'graphe',
             'texte': 'des statistiques : mois, nationalité, motif, hôtel, tirés des mêmes fiches'},
        ],
        'voix': "Un clic au check-inne, six informations suivies, quatre regroupements de statistiques : le registre "
                "suit chaque séjour.",
    },
    'cta': {
        'appel': 'Demandez votre démonstration',
        'suivant': 'Gouvernante et maintenance',
        'voix': "Aïte haousse, par Aïte Consulting. Demandez votre démonstration ; prochain tutoriel : la gouvernante "
                "et la maintenance.",
    },
    'vignette': {'etape': 4, 'apres': 2.6},
}
