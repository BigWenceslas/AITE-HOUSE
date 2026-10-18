# -*- coding: utf-8 -*-
"""Tutoriel 4 — Bar, restaurant, boutique : tout sur la note de chambre.

Personnage : le caissier du bar (demo.POSTES['caisse']), qui encaisse sur le
mode « Note de chambre » ; la mise en place est faite une fois par la
direction (Point de Vente → Configuration → Modes de paiement, réservé au
responsable du point de vente), la file d'attente est traitée par la
réception (menu réservé à aite_hotel_management.group_hotel_user,
aite_hotel_pos_link/views/roomcharge_menus.xml:3-8). Public visé du guide :
« Caissiers (restaurant & boutique), réception »
(docs/guides/AITE_Guide_Note_de_chambre.pdf p.1).

Sources des libellés (relevés mot pour mot) :

1. Le mode de paiement — odoo18/addons/point_of_sale/views/
   pos_payment_method_views.xml:7-24 (fiche : nom, « Identifier le client »
   split_transactions, « Journal » requis sauf si l'on identifie le client
   :19-20, « Intégration », image) ; i18n/fr.po : « Mode » :4284-4285,
   « par ex. Espèces » :9547-9548, « Identifier le client » :3518-3519,
   « Laisser vide pour utiliser le compte débiteur du client » :4016-4017,
   « Intégration » :3641-3642, « Non requis » :4601-4602, « Modes de
   paiement » :5276-5277, menus « Tableau de bord », « Commandes »,
   « Produits », « Analyse », « Configuration » :2483, :5067, :6320, :6631,
   :2049 ; « Paiement en ligne » : pos_online_payment/i18n/fr.po:168-169 ;
   menu « Analyse AITE » : aite_pos_analytics/views/pos_analytics_menus.xml:11.
   La case ajoutée par le module, juste après « Journal », et son infobulle :
   aite_hotel_pos_link/views/pos_payment_method_views.xml:8-10,
   models/pos_payment_method.py:9-13 (« Note de chambre », « Les
   encaissements sur ce moyen sont reportés au folio du séjour du client (ou
   en file d'attente si ambigu). »). Mise en page, case « Société » (base
   multi-sociétés) et infobulle noire : capture en lecture seule de la base
   MuK (Point de Vente → Configuration → Modes de paiement → Note de chambre).
2. La caisse — odoo18/addons/point_of_sale/static/src/app : écran de vente
   (ecrans.pos_produits, captures ref_muk/611 et 612) ; bouton Client qui
   prend le nom du client screens/product_screen/control_buttons/
   select_partner_button/select_partner_button.xml:4-7 ; fenêtre des clients
   screens/partner_list/partner_list.xml:5-56 et partner_line/
   partner_line.xml:46-86 (« Créer », « Recherche des clients... », « Nom »,
   « Adresse », « Contact », « Rechercher plus », « Ignorer » :
   point_of_sale/i18n/fr.po:2261-2262, :6921-6922, :4363-4364, :721-722,
   :2170-2171, :6939-6940, :2768-2769 ; la colonne « Solde » n'est affichée
   qu'avec pos_loyalty, partner_list.js:112-114) ; numéro de commande
   « <caisse>/<4 chiffres> » : models/pos_config.py:479-480 ; numéro de
   suivi à trois chiffres : models/pos_order.py:58-60.
3. Le paiement — screens/payment_screen/payment_screen.xml:27-140 (modes,
   « Client » qui prend le nom du client :100-107, « Facture », « Retour »,
   « Valider ») ; payment_status/payment_status.xml:4-22 (« Veuillez
   sélectionner un mode de paiement », « Restant ») ; « Mettre sur ardoise » :
   aite_pos_credit/static/src/js/pos/payment_screen_button.xml:12-18 ;
   l'avertissement d'un mode « payer plus tard » sans facture :
   payment_screen.js:113-125 et fr.po:8607-8612 (« Avertissement », « Pour
   assurer le suivi des soldes dûs, générez une facture ou téléchargez
   l'application comptabilité. ») ; « Client requis » si le client manque :
   payment_screen.js:424-439, fr.po:2442-2451. Aspect : ref_muk/613, 614.
4. Le folio — aite_hotel_management/views/hotel_folio_views.xml:31-128
   (« Encaisser », « Générer la facture » ; « Annuler » et « Recalculer la
   taxe de séjour » sont réservés au responsable :43-46 et
   aite_city_tax/views/hotel_folio_views.xml:17-24, la réception ne les voit
   pas ; « Règlements », « Séjour », « Montants », onglets, colonnes, note
   grise) ; models/hotel_folio.py:28-114 et :395-436 (libellés, états
   Ouvert / Facturé / Soldé, types Nuitée / Service) ; libellé de nuitée à
   dates ISO :256-260 ; aite_city_tax : ligne et montant « Taxe de séjour »
   models/hotel_folio.py:9-12, :37-41, :120-130 ; menu Facturation → Folios
   hotel_menus.xml:66-75. La ligne reportée : aite_hotel_pos_link/models/
   pos_order.py:69-81 (type service, quantité 1, prix = montant) et :146-156
   (libellé « POS <commande> », date du jour, sans taxe). TVA « 19.25% » de
   la nuitée et montants du séjour d'Estelle Ngono repris de
   scenarios/t05_taxe_sejour.py (même folio), acompte de 45 000 FCFA repris
   de scenarios/c1_reception.py. Aspect : ref_muk/029.
5. La file — aite_hotel_pos_link/views/roomcharge_pending_views.xml:3-21
   (liste sans « Nouveau », lignes orange « À rattacher », somme du montant
   sans libellé en pied, colonne « Created on » non traduite), :51-61
   (action, filtre « À rattacher » par défaut), :63-74 (recherche) ;
   models/roomcharge_pending.py:12-35 (« Commande POS », « Client »,
   « Montant », « Motif », « Folio choisi » limité aux folios ouverts,
   « À rattacher » / « Rattachée ») ; motifs : models/pos_order.py:112-117
   (« Aucun folio ouvert », « %(n)s folios ouverts »). Aspect : ref_muk/048.
6. Le rattachement — roomcharge_pending_views.xml:22-50 (« Rattacher au
   folio », statusbar, « Folio choisi » verrouillé une fois rattachée) ;
   models/roomcharge_pending.py:37-56 (action_resolve) ; liste déroulante
   d'Odoo : odoo18/addons/web/static/src/views/fields/relational_utils.js:
   362-382 et web/i18n/fr.po:5713-5714 (« Recherche avancée... »),
   :6141-6142 (« Commencer à écrire... ») ; fil d'Ariane technique
   « aite.roomcharge.pending,<id> » : ref_muk/048-…-fiche.png.

Sources des affirmations :

- douleurs : « Un client en séjour ne doit pas sortir sa monnaie à chaque
  repas » (guide p.1 §1) ; ticket recopié à la main : sans report, le folio
  invite à « ajouter librement des lignes de service (restaurant,
  blanchisserie, minibar…) » (hotel_folio_views.xml:122-128) ; « Deux
  séjours au même nom » et « Le client n'est finalement pas un résident »
  (guide p.2 FAQ) ; « une note en attente au moment du check-out du client,
  c'est un encaissement à courir après » (guide p.2 §4, règle d'or) ;
- promesse : client identifié et un seul folio ouvert → report direct ;
  sinon file d'attente, la réception choisit (pos_order.py:55-67, :87-127 ;
  guide FAQ « le système ne devine jamais ») ;
- mise en place une fois, ajout aux caisses du bar, du restaurant et de la
  boutique : guide p.1 §2 ; « Identifier le client » obligatoire pour
  laisser le journal vide (pos_payment_method_views.xml:19-20) et « Client
  requis » à la caisse (payment_screen.js:424-439) ;
- lien par la fiche client, pas par le numéro de chambre : guide p.1 §3
  (« Bon réflexe ») et pos_order.py:100-106 (recherche par partner_id) ;
- paiement mixte : pos_order.py:41-53, :94-96 ; tests/test_room_charge.py:
  192-201 (5 000 en espèces + 7 000 en note de chambre → 7 000 sur le
  folio) ; guide p.1 §3 ;
- une ligne par ticket : pos_order.py:89-91 (garde d'idempotence),
  tests/test_room_charge.py:210-217 ; « C'est tout » : guide p.1 §3 ;
- le motif dit pourquoi : guide p.2, légende de l'écran 3 ; seuls les
  folios ouverts : roomcharge_pending.py:28-31 ; une réservation confirmée a
  déjà son folio ouvert (d'où « 2 folios ouverts » pour un client qui a déjà
  réservé un autre séjour) : aite_hotel_management/models/
  hotel_reservation.py:320-331, tests/test_room_charge.py:262-269 ;
- résultats : 1 ligne par ticket (ci-dessus) ; 7 000 FCFA sur 12 000
  (test_room_charge.py:192-201) ; 23 tests Odoo dans
  addons/aite_hotel_pos_link/tests/test_room_charge.py (décompte des
  « def test_ », confirmé par docs/GUIDE_TESTS.md:36).

Écarts rejoués tels quels (voir le rapport) : en-tête « Created on » en
anglais (roomcharge_pending_views.xml:9) ; fil d'Ariane technique
« aite.roomcharge.pending,12 » (aucun champ name) ; « Nouveau » sur la fiche
d'une note en attente alors que la liste interdit la création
(roomcharge_pending_views.xml:7-8, 26) ; « Folio choisi » ne propose que des
références, sans nom de client ; avertissement d'Odoo « soldes dûs » au choix
du mode (payment_screen.js:113-125) ; dates ISO dans le libellé de la
nuitée ; la ligne reportée est le montant TTC du ticket posé sans taxe et
compté dans « Services (HT) » (pos_order.py:69-81) ; « Mettre sur ardoise »
voisin de « Note de chambre ».

Écarts de fond, non montrés et volontairement absents de la voix (voir le
rapport) : avec aite_pos_credit installé, le mode « Note de chambre » (sans
journal, donc « payer plus tard ») ouvre AUSSI une ardoise du même montant
(aite_pos_credit/models/pos_payment_method.py:24-40, pos_order.py:103-130) —
la vidéo ne promet donc ni « une seule facture » ni « rien ne se perd » ; le
report n'utilise pas sudo() (pos_order.py:100-123, :151) alors que folios,
lignes de folio et file sont réservés aux profils Réception et Responsable
(aite_hotel_management/security/ir.model.access.csv:21-23,
aite_hotel_pos_link/security/ir.model.access.csv:2-3) : un caissier sans
profil hôtel échoue à la synchronisation du ticket ; le motif « Client non
identifié » est inaccessible depuis la caisse quand « Identifier le client »
est coché (Odoo demande « Client requis ») et n'est donc pas montré.

Étapes : 1 mise en place (direction) ; 2-3 à la caisse (Hervé) ; 4 folio,
5 file, 6 choix du folio, 7 rattachement (réception, Mireille).

Données fictives : demo.py (Complexe Hôtelier — Démo, Démo Hôtellerie SARL,
Estelle Ngono, RES/2026/0214, FOL/2026/0214, chambre 204 [CFT] ; Martin Ebode,
RES/2026/0209 ; Hervé Tchakounté, Mireille Ateba, Danielle Eyenga ; Patrick
Nkoulou et Sylvie Mbarga, clients du bar) ; caisses « Bar de la terrasse »,
« Restaurant », « Boutique » ; carte du bar fictive.
"""

import demo
from ecrans import (APPS_PROFIL, bouton, champ, cp_fiche, deux_colonnes, e, entree, fenetre_muk, fenetre_pos,
                    groupe, icone, navigateur, onglets, pos_ligne_paiement, pos_paiement, pos_produits, statusbar,
                    table, titre_fiche, toast, vue_fiche, vue_libre, vue_liste, cell_puce, num)
from marketing import bulle, dezoom, reaction, zoom
from moteur import (anneau, cacher, clic, classe, curseur, defiler, fermer, montrer, notifier, ouvrir, pause, saisir,
                    survol, texte, vue)

NOM, ROLE = demo.POSTES['caisse']              # Hervé Tchakounté, caissier du bar
RECEPTION = demo.POSTES['reception'][0]        # Mireille Ateba
DIRECTION = demo.POSTES['direction'][0]        # Danielle Eyenga
COMMANDE = 'Bar de la terrasse/0042'           # le ticket d'Estelle Ngono
TICKET = '13 500 FCFA'


def masque(nav):
    """Un second cadre de navigateur, superposé et caché : un changement d'écran."""
    return nav.replace('class="navigateur"', 'class="navigateur masque"', 1)


# ===================================================== 1. la mise en place --
# Point de Vente → Configuration → Modes de paiement → Nouveau (direction).
APPAREIL = ('<svg viewBox="0 0 24 24" fill="none" stroke="#ADB5BD" stroke-width="1.6" stroke-linejoin="round">'
            '<path d="M3 8h4l2-3h6l2 3h4v11H3z"/><circle cx="12" cy="13" r="3.6"/>'
            '<circle cx="18" cy="17.5" r="4" fill="#fff"/><path d="M18 15.5v4M16 17.5h4" stroke-linecap="round"/></svg>')


def ligne_pm(libelle, valeur_html, ident=None, aide=True, leger=False):
    sup = ('<sup%s>?</sup>' % (' id="%s-aide"' % ident if ident else '')) if aide else ''
    return ('<div class="t04-r"><span class="l%s"%s>%s%s</span>%s</div>'
            % (' leger' if leger else '', ' id="%s"' % ident if ident else '', e(libelle), sup, valeur_html))


MODE = vue_libre('t4-mode', (
    cp_fiche('Modes de paiement', 'Nouveau')
    + '<div class="t04-pm" id="t4-pm">'
      '<div class="t04-lab">Mode<sup>?</sup></div>'
    + entree('t4-nom', 'par ex. Espèces', classe='entree t04-nom')
    + '<div class="t04-cols"><div id="t4-pm-g">'
    + ligne_pm('Paiement en ligne', '<span class="t04-cb"></span>')
    + ligne_pm('Identifier le client', '<span class="t04-cb" id="t4-cb-ident"></span>', 't4-l-ident')
    + ligne_pm('Journal', '<span class="t04-in" id="t4-journal">Laisser vide pour utiliser le compte débiteur du '
                          'client</span>')
    + ligne_pm('Note de chambre', '<span class="t04-cb" id="t4-cb-note"></span>', 't4-l-note')
    + ligne_pm('Société', '<span class="t04-lien">%s</span>' % e(demo.SOCIETE), aide=False, leger=True)
    + '</div><div>'
    + ligne_pm('Intégration', '<span class="t04-in noir">Non requis</span>', aide=False)
    + '</div></div><div class="t04-img">%s</div>' % APPAREIL
    + '<div class="t04-tip masque" id="t4-tip">Les encaissements sur ce moyen sont reportés au folio du séjour du '
      'client (ou en file d\'attente si ambigu).</div></div>'), initiale=True)

MENUS_POS = ['Tableau de bord', 'Commandes', 'Produits', 'Analyse AITE', 'Analyse', 'Configuration']
NAV_CONFIG = navigateur(fenetre_muk('app-t4c', 'Point de Vente', MENUS_POS, [MODE], actif='Configuration',
                                    societe=demo.SOCIETE, initiale=DIRECTION[0], avatar='#8E3B46',
                                    apps=APPS_PROFIL['direction'], app_active='Point de Vente'))

# ============================================================ 2. la caisse --
BIERES, SOFTS, GRILLADES, PLATS, ACCOMP = '#F9D7A6', '#CDE6F7', '#F7C6C0', '#D9EFC9', '#E6DAF2'
CATEGORIES = [('Bières', BIERES), ('Jus & softs', SOFTS), ('Grillades', GRILLADES), ('Plats', PLATS),
              ('Accompagnements', ACCOMP)]
CARTE_BAR = [
    ('Bière blonde 65 cl', BIERES), ('Bière brune 65 cl', BIERES), ('Bière blonde 33 cl', BIERES),
    ('Bière sans alcool 33 cl', BIERES), ('Jus de bissap 50 cl', SOFTS), ("Jus d'ananas 1 L", SOFTS),
    ('Cola 33 cl', SOFTS), ('Tonic 33 cl', SOFTS), ('Eau minérale 50 cl', SOFTS), ('Eau gazeuse 1 L', SOFTS),
    ('Poisson braisé', GRILLADES), ('Poulet braisé', GRILLADES), ('Brochettes de bœuf', GRILLADES),
    ('Soya', GRILLADES), ('Ndolè', PLATS), ('Poulet DG', PLATS), ('Eru', PLATS), ('Mbongo tchobi', PLATS),
    ('Plantain frit', ACCOMP), ('Bâton de manioc', ACCOMP), ('Miondo', ACCOMP), ('Frites de plantain', ACCOMP),
    ('Arachides grillées', ACCOMP), ('Chips de plantain', ACCOMP)]
# Le ticket d'Estelle Ngono (prix TTC, TVA 19,25 % incluse : 2 179 FCFA).
LIGNES_TICKET = [('t4-l1', 'Poisson braisé', '1,00', '7 000 FCFA', '7 000 FCFA'),
                 ('t4-l2', 'Plantain frit', '1,00', '1 500 FCFA', '1 500 FCFA'),
                 ('t4-l3', 'Bière blonde 65 cl', '2,00', '1 500 FCFA', '3 000 FCFA'),
                 ('t4-l4', 'Jus de bissap 50 cl', '2,00', '1 000 FCFA', '2 000 FCFA')]
VENTE = (pos_produits('t4-vente', CATEGORIES, [('t4-p%d' % i, n, c) for i, (n, c) in enumerate(CARTE_BAR)],
                      LIGNES_TICKET, TICKET, '2 179 FCFA', initiale=True)
         .replace('class="pv-ligne" id="t4-l4"', 'class="pv-ligne sel" id="t4-l4"')
         .replace('<span>Client</span>', '<span id="t4-cli"><b id="t4-cli-t">Client</b></span>', 1)
         .replace('<div class="pos-acts">', '<div class="pos-acts" id="t4-acts">', 1))

MODES = [('t4-m-esp', 'Espèces'), ('t4-m-om', 'Orange Money'), ('t4-m-momo', 'MTN MoMo'),
         ('t4-m-note', 'Note de chambre')]
PAIEMENT = (pos_paiement('t4-paie', MODES, TICKET)
            .replace(icone('personne') + 'Client</span>', icone('personne') + '<b class="t04-nomcli">%s</b></span>'
                     % e(demo.CLIENT), 1)
            .replace('class="v" id="t4-paie-valider"', 'class="v t04-off" id="t4-paie-valider"', 1)
            .replace('<div class="pos-zone">', '<div class="t04-choix" id="t4-paie-msg">Veuillez sélectionner un mode '
                                               'de paiement</div><div class="pos-zone">', 1)
            .replace('class="pos-restant" id="t4-paie-restant"', 'class="pos-restant masque" id="t4-paie-restant"', 1)
            .replace('<span id="t4-paie-reste">%s</span>' % TICKET, '<span id="t4-paie-reste">0 FCFA</span>', 1)
            .replace('<div id="t4-paie-lignes"></div>', '<div id="t4-paie-lignes">%s</div>'
                     % pos_ligne_paiement('t4-pl', 'Note de chambre', TICKET), 1))

# La fenêtre des clients (bouton « Client »).
TEL = '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M6.6 10.8a15.2 15.2 0 006.6 6.6l2.2-2.2a1 1 0 011-.25 11.4 11.4 0 003.6.6 1 1 0 011 1V20a1 1 0 01-1 1A17 17 0 013 4a1 1 0 011-1h3.5a1 1 0 011 1 11.4 11.4 0 00.6 3.6 1 1 0 01-.25 1z"/></svg>'
AVION = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M22 2L11 13M22 2l-7 20-4-9-9-4z"/></svg>'
CLIENTS = [('Armand Mvogo', 'Bastos Yaoundé Cameroun', '+237 699 12 40 77', 'armand.mvogo@exemple.cm'),
           ('Brigitte Essomba', 'Akwa Douala Cameroun', '+237 677 08 51 23', 'b.essomba@exemple.cm'),
           ('Claire Durand', 'Lyon France', '+33 6 12 48 90 31', 'claire.durand@exemple.fr'),
           (demo.CLIENT, 'Bonapriso Douala Cameroun', demo.CLIENT_TEL, demo.CLIENT_MAIL),
           ('Joël Kamga', 'Bonamoussadi Douala Cameroun', '+237 655 30 17 64', 'joel.kamga@exemple.cm'),
           ('Martin Ebode', 'Kribi Cameroun', '+237 690 22 75 18', 'martin.ebode@exemple.cm')]
TROUVES = [(demo.CLIENT, 'Bonapriso Douala Cameroun', demo.CLIENT_TEL, demo.CLIENT_MAIL),
           ('Albert Ngono', 'Mvog-Ada Yaoundé Cameroun', '+237 699 54 03 12', 'albert.ngono@exemple.cm')]


def ligne_client(ident, nom, adresse, tel, mail):
    return ('<div class="t04-cl"%s><b>%s</b><span>%s</span><span class="t04-ct"><span>%s%s</span><span>%s%s</span>'
            '</span><span class="t04-menu">☰</span></div>'
            % (' id="%s"' % ident if ident else '', e(nom), e(adresse), icone('telephone', 't04-ci'), e(tel),
               '<span class="t04-ci">%s</span>' % AVION, e(mail)))


TETE_CLIENTS = '<div class="t04-cl t04-cl-tete"><span>Nom</span><span>Adresse</span><span>Contact</span><span></span></div>'
DIALOGUE = (
    '<div class="voile masque" id="t4-dlg-voile" data-layout-allow-overlap data-layout-allow-occlusion></div>'
    '<div class="modale masque t04-dlg" id="t4-dlg" data-layout-allow-overlap data-layout-allow-occlusion>'
    '<div class="t04-dlg-h"><span class="bt primaire t04-creer">Créer</span>%s</div>'
    '<div class="t04-dlg-c">%s<div class="t04-pile"><div id="t4-tous">%s</div>'
    '<div class="masque" id="t4-trouves">%s<div class="t04-plus"><span class="bt primaire">Rechercher plus</span></div>'
    '</div></div></div><div class="t04-dlg-p"><span class="bt gris">Ignorer</span></div></div>'
    % (entree('t4-q', 'Recherche des clients...', classe='entree t04-q'), TETE_CLIENTS,
       ''.join(ligne_client(None, *c) for c in CLIENTS),
       ligne_client('t4-c-estelle', *TROUVES[0]) + ligne_client(None, *TROUVES[1])))
AVERT = toast('t4-avert', 'Avertissement', "Pour assurer le suivi des soldes dûs, générez une facture ou téléchargez "
                                           "l'application comptabilité.", genre='alerte')
NAV_POS = masque(navigateur(fenetre_pos('app-t4p', [VENTE, PAIEMENT], NOM, numero='342', calques=DIALOGUE + AVERT),
                            'nav-pos'))

# ============================================================= 3. l'hôtel --
MENUS_HOTEL = ['Front Desk', 'Réservations', 'Espaces & Prestations', 'Notes de chambre en attente', 'Facturation',
               'Fidélité', 'Gouvernante']

# -- le folio d'Estelle Ngono, la ligne du bar déjà reportée
TAG = '<span class="t04-tag">19.25%</span>'
COLS_F = [('Date', '124px'), ('Type', '150px'), ('Service', '84px'), ('Libellé', '1fr'), ('Qté', '64px', 'd'),
          ('Prix unitaire', '146px', 'd'), ('Taxes', '92px'), ('Sous-total (HT)', '156px', 'd'),
          ('Total (TTC)', '146px', 'd')]
LIGNES_F = table(COLS_F, [
    ('t4-fl1', ['12/10/2026', ('<span><span class="puce info">Nuitée</span></span>',), '',
                'Nuitée 204 (Confort) — 2026-10-14 → 2026-10-16', '2,00', demo.PRIX_NUIT, (TAG,), demo.TOTAL_HEB,
                '107 325 FCFA']),
    ('t4-fl2', ['12/10/2026', ('<span><span class="puce orange">Taxe de séjour</span></span>',), '',
                'Taxe de séjour — 4 nuitée(s) × personne (3 ★, Cameroun)', '4,00', '3 000 FCFA', '', '12 000 FCFA',
                '12 000 FCFA']),
    ('t4-fl3', ['14/10/2026', ('<span><span class="puce violet">Service</span></span>',), '',
                'POS ' + COMMANDE, '1,00', TICKET, '', TICKET, TICKET])],
    total=['', '', '', '', '', '', '', '115 500 FCFA', '132 825 FCFA'])
LIGNES_F = (LIGNES_F.replace('class="t-ligne" id="t4-fl1"', 'class="t-ligne t04-nuitee" id="t4-fl1"', 1)
            .replace('class="t-ligne" id="t4-fl2"', 'class="t-ligne taxe" id="t4-fl2"', 1))
FEUILLE_FOLIO = (
    titre_fiche(demo.FOLIO)
    + deux_colonnes(
        groupe('Séjour', [champ('Client', demo.CLIENT, lien_=True), champ('Réservation', demo.RESA, lien_=True),
                          champ('Séjour', 'Arrivé'), champ('Arrivée', demo.ARRIVEE), champ('Départ', demo.DEPART),
                          champ('Hôtel', demo.HOTEL, lien_=True)]),
        groupe('Montants', [champ('Hébergement (HT)', demo.TOTAL_HEB), champ('Services (HT)', TICKET, 't4-f-serv'),
                            champ('Taxe de séjour', '12 000 FCFA'), champ('Total HT', '115 500 FCFA'),
                            champ('Taxes', '17 325 FCFA'), champ('Total TTC', '<b>132 825 FCFA</b>', html=True),
                            champ('Encaissé', '45 000 FCFA'),
                            champ('Solde dû', '<b>87 825 FCFA</b>', 't4-f-solde', html=True)], 't4-f-montants'))
    + onglets(['Lignes du folio', 'Règlements', 'Note']) + LIGNES_F
    + '<div class="note-pied">Les lignes « nuitée » sont synchronisées depuis la réservation ; ajoutez librement des '
      'lignes de service (restaurant, blanchisserie, minibar…).</div>')
FOLIO = vue_fiche('t4-folio', cp_fiche('Folios', demo.FOLIO, '3 / 15', stats=[('t4-st-regl', 'billet', 'Règlements', '1')]),
                  [bouton('t4-f-enc', 'Encaisser', 'primaire'), bouton('t4-f-fact', 'Générer la facture')],
                  statusbar('t4-fsb', ['Ouvert', 'Facturé', 'Soldé'], 0), FEUILLE_FOLIO, initiale=True)

# -- la file « Notes de chambre en attente » (filtre À rattacher)
COLS_N = [('Created on', '212px'), ('Commande POS', '262px'), ('Client', '196px'), ('Montant', '150px', 'd'),
          ('Motif', '1fr'), ('Folio choisi', '170px'), ('État', '140px')]
ATTENTE = [('14/10/2026 22:41:17', 'Bar de la terrasse/0047', 'Martin Ebode', '9 500 FCFA', '2 folios ouverts'),
           ('14/10/2026 20:18:03', 'Restaurant/0031', 'Patrick Nkoulou', '21 000 FCFA', 'Aucun folio ouvert'),
           ('14/10/2026 16:52:40', 'Boutique/0018', 'Sylvie Mbarga', '6 000 FCFA', 'Aucun folio ouvert')]


def file_attente(ident, lignes, total):
    vue_html = vue_liste(ident, 'Notes de chambre en attente', COLS_N, [
        {'id': '%s-%s' % (ident, i), 'classe': 'avert',
         'cellules': [d, ref, cli, num(mt), (('<span class="ell" id="%s-%s-motif">%s</span>' % (ident, i, e(motif))),),
                      '', cell_puce('À rattacher', 'orange')]}
        for i, (d, ref, cli, mt, motif) in enumerate(lignes)],
        facettes=[('%s-fac' % ident, 'À rattacher')], pager='1-%d / %d' % (len(lignes), len(lignes)),
        total=['', '', '', total, '', '', ''], nouveau=False)
    pied = '<span class="d">%s</span><span></span>' % e(total)
    return vue_html.replace(pied, '<span class="d">%s</span><span id="%s-ancre"></span>' % (e(total), ident), 1)


FILE = file_attente('t4-file', ATTENTE, '36 500 FCFA')
FILE_APRES = file_attente('t4-file2', ATTENTE[1:], '27 000 FCFA')

# -- la note en attente de Martin Ebode : deux folios ouverts (séjour en cours et réservation de novembre)
OUVERTS = ['FOL/2026/0198', 'FOL/2026/0201', 'FOL/2026/0205', 'FOL/2026/0209', 'FOL/2026/0214', 'FOL/2026/0219',
           'FOL/2026/0226', 'FOL/2026/0233']
DEROULANT = ('<div class="t04-dd masque" id="t4-dd" data-layout-allow-overlap data-layout-allow-occlusion>%s'
             '<div class="t04-dd-o lien">Recherche avancée...</div><div class="t04-dd-o ital">Commencer à écrire...</div>'
             '</div>' % ''.join('<div class="t04-dd-o" id="t4-dd-%s">%s</div>' % (f[-4:], f) for f in OUVERTS))
FOLIO_CHOISI = ('<div class="t04-m2o" id="t4-fc"><span class="t04-m2o-v" id="t4-fc-v"></span><span class="t04-car">▾</span>'
                '%s</div>' % DEROULANT)
FEUILLE_NOTE = deux_colonnes(
    '<div class="grp">%s</div>' % ''.join([champ('Commande POS', 'Bar de la terrasse/0047', lien_=True),
                                         champ('Client', 'Martin Ebode', lien_=True), champ('Montant', '9 500 FCFA'),
                                         champ('Motif', '2 folios ouverts', 't4-motif')]),
    '<div class="grp">%s</div>' % champ('Folio choisi', FOLIO_CHOISI, html=True, gras=True))
NOTE = vue_fiche('t4-note', cp_fiche('Notes de chambre en attente', 'aite.roomcharge.pending,12', '1 / 3'),
                 [bouton('t4-b-ratt', 'Rattacher au folio', 'primaire')],
                 statusbar('t4-nsb', ['À rattacher', 'Rattachée'], 0), FEUILLE_NOTE)
NOTE = NOTE.replace('<span class="parent">', '<span class="parent" id="t4-fil">', 1)

HOTEL = fenetre_muk('app-t4h', 'Hôtel', MENUS_HOTEL, [FOLIO, FILE, NOTE, FILE_APRES], actif='Facturation',
                    societe=demo.SOCIETE, initiale=RECEPTION[0], avatar='#7C5295', apps=APPS_PROFIL['reception'],
                    app_active='Hôtel')
HOTEL = (HOTEL.replace('<span class="menu">Notes de chambre en attente</span>',
                       '<span class="menu" id="t4-menu-file">Notes de chambre en attente</span>', 1)
         .replace('<span class="menu actif">Facturation</span>', '<span class="menu actif" id="t4-menu-fact">Facturation</span>', 1))
NAV_HOTEL = masque(navigateur(HOTEL, 'nav-hotel'))

ECRAN = NAV_CONFIG + NAV_POS + NAV_HOTEL

CSS = """
/* -- 1. fiche du mode de paiement (thème MuK) -- */
#t4-mode .cp { height: 80px; }
.t04-pm { position: absolute; left: 22px; right: 22px; top: 102px; height: 430px; background: #fff;
  border: 1px solid var(--o-filet); padding: 22px 30px; color: var(--o-texte); }
.t04-lab { font-size: 19px; font-weight: 600; }
.t04-pm sup { margin-left: 3px; font-size: 13px; color: #3F6A83; font-weight: 600; }
.t04-nom { margin-top: 4px; width: 640px; height: 64px; border-width: 0 0 1px 0; border-radius: 0; padding: 0 4px; font-size: 40px; }
.t04-nom .ph, .t04-nom .val { left: 4px; }
.t04-nom .val { font-weight: 400; }
.t04-cols { display: grid; grid-template-columns: 780px 420px; column-gap: 56px; margin-top: 24px; }
.t04-r { display: grid; grid-template-columns: 230px 1fr; align-items: center; min-height: 52px; font-size: 19px; }
.t04-r .l { font-weight: 600; white-space: nowrap; }
.t04-r .l.leger { font-weight: 400; color: var(--o-texte-2); }
.t04-cb { width: 20px; height: 20px; border: 1px solid #ADB5BD; border-radius: 3px; background: #fff; display: inline-flex;
  align-items: center; justify-content: center; }
.t04-cb.on { background: var(--muk-prim); border-color: var(--muk-prim); }
.t04-cb.on::after { content: '✓'; color: #fff; font-size: 15px; font-weight: 700; }
.t04-in { height: 42px; border-bottom: 1px solid #CED4DA; display: block; line-height: 42px; padding: 0 4px; color: #6C757D;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.t04-in.noir { color: var(--o-texte); }
.t04-lien { color: #3F6A83; }
.t04-img { position: absolute; left: 1330px; top: 130px; width: 130px; height: 130px; border: 1px solid var(--o-filet);
  display: flex; align-items: center; justify-content: center; }
.t04-img svg { width: 82px; height: 82px; }
.t04-tip { position: absolute; left: 30px; top: 352px; width: 560px; padding: 14px 22px; background: #000; color: #fff;
  font-size: 19px; line-height: 1.45; z-index: 5; }
.t04-tip::before { content: ''; position: absolute; left: 155px; top: -9px; border: 9px solid transparent; border-top: 0;
  border-bottom-color: #000; }

/* -- 2. la caisse -- */
#t4-cli .t04-cli-t, #t4-cli b { font-weight: 400; }
#t4-cli.t04-actif b { color: #3F6A83; font-weight: 500; }
.t04-nomcli { font-weight: 500; color: #3F6A83; }
.pos-rv .v.t04-off { background: #A3BCCB; }
.t04-choix { position: absolute; left: 0; right: 0; top: 410px; text-align: center; font-size: 24px; color: var(--o-texte); }
.pos-pd .pos-zone { top: 380px; }
#t4-paie-restant { color: #1A6E2E; border-color: #1A6E2E; }
.pos-mode.actif { background: #E9ECEF; }
.t04-dlg { top: 50px; width: 1260px; margin-left: -630px; }
.t04-dlg-h { display: flex; align-items: center; height: 84px; padding: 0 24px; border-bottom: 1px solid var(--o-filet); }
.t04-creer { height: 50px; font-size: 21px; padding: 0 22px; }
.t04-q { margin: 0 0 0 auto; width: 480px; height: 52px; font-size: 21px; }
.t04-dlg-c { position: relative; height: 520px; padding: 0 24px; }
.t04-pile { position: relative; }
.t04-pile > div:nth-child(2) { position: absolute; left: 0; right: 0; top: 0; }
.t04-cl { display: grid; grid-template-columns: 300px 360px 1fr 60px; align-items: center; gap: 16px; min-height: 76px;
  padding: 0 12px; border-bottom: 1px solid #EEF0F2; font-size: 19px; color: var(--o-texte); }
.t04-cl b { font-weight: 700; }
.t04-cl-tete { min-height: 52px; font-weight: 600; border-bottom: 1px solid var(--o-filet); }
.t04-cl.survol { background: #E3ECF2; }
.t04-ct { display: flex; flex-direction: column; gap: 3px; font-size: 17px; color: var(--o-texte-2); }
.t04-ct > span { display: flex; align-items: center; gap: 8px; white-space: nowrap; }
.t04-ci { width: 16px; height: 16px; display: inline-flex; color: var(--o-texte-2); }
.t04-ci svg { width: 16px; height: 16px; }
.t04-menu { width: 46px; height: 42px; border: 1px solid var(--o-filet); border-radius: 4px; display: flex; align-items: center;
  justify-content: center; font-size: 20px; color: var(--o-texte); background: #F8F9FA; }
.t04-plus { display: flex; justify-content: center; margin-top: 16px; }
.t04-plus .bt { height: 50px; font-size: 20px; }
.t04-dlg-p { height: 84px; display: flex; align-items: center; padding: 0 24px; border-top: 1px solid var(--o-filet); }
.t04-dlg-p .bt { height: 50px; font-size: 20px; }
#t4-avert { top: 74px; width: 600px; }

/* -- 3. l'hôtel -- */
#t4-fsb .st-et, #t4-nsb .st-et { color: #5C636A; }
#b-ident { max-width: 780px; }
.t04-tag { display: inline-flex; align-items: center; height: 26px; padding: 0 9px; border-radius: 13px; background: #E9ECEF;
  color: var(--o-texte); font-size: 15px; }
.table .t-ligne.t04-nuitee { color: var(--info); }
#t4-folio .ch { min-height: 38px; }
#t4-folio .f-titre { margin-bottom: 14px; }
#t4-note .feuille { min-height: 0; border-bottom: 1px solid var(--o-filet); padding-bottom: 26px; }
.t04-m2o { position: relative; height: 42px; border-bottom: 1px solid #CED4DA; }
.t04-m2o.focus { border-bottom-color: var(--muk-prim); }
.t04-m2o.lecture { border-bottom-color: transparent; }
.t04-m2o-v { position: absolute; left: 4px; top: 50%; transform: translateY(-50%); color: var(--o-texte); white-space: nowrap; }
.t04-m2o.lecture .t04-m2o-v { color: #3F6A83; }
.t04-car { position: absolute; right: 6px; top: 50%; transform: translateY(-50%); font-size: 14px; color: var(--o-texte-2); }
.t04-m2o.lecture .t04-car { opacity: 0; }
.t04-dd { position: absolute; left: 0; top: 44px; width: 290px; background: #fff; border: 1px solid var(--o-filet);
  box-shadow: 0 10px 24px rgba(0,0,0,.14); padding: 6px 0; z-index: 6; }
.t04-dd-o { height: 40px; display: flex; align-items: center; padding: 0 20px; font-size: 19px; color: var(--o-texte); white-space: nowrap; }
.t04-dd-o.survol { background: #E9ECEF; }
.t04-dd-o.lien { color: #3F6A83; padding-left: 30px; }
.t04-dd-o.ital { font-style: italic; color: var(--o-texte-2); padding-left: 30px; }
"""

TUTORIEL = {
    'slug': 't04-note-chambre',
    'profil': 't04_note_chambre',
    'numero': 4,
    'titre': 'Bar, restaurant, boutique : tout sur la note de chambre',
    'fonction': 'Note de chambre',
    'personnage': (NOM, ROLE),
    'accroche': {
        'kicker': 'Bar, restaurant, boutique',
        'question': 'Au départ du client, le bar a-t-il *tout* reporté sur sa note ?',
        'douleurs': [('pieces', 'La monnaie sortie à chaque verre'),
                     ('cahier', 'Le ticket du bar recopié sur le folio'),
                     ('interrogation', 'Deux séjours au même nom : lequel ?'),
                     ('alerte', "Un client qui n'est pas résident"),
                     ('sablier', 'Une note encore en attente au départ')],
        'voix': "Au départ du client, le bar a-t-il tout reporté sur sa note ? Sinon, c'est un encaissement à courir "
                "après.",
    },
    'revelation': {
        'promesse': 'La consommation rejoint seule le folio du séjour. Au moindre doute, c\'est la réception qui '
                    'choisit.',
        'voix': "Avec Aïte haousse, la consommation rejoint toute seule le folio du séjour. Au moindre doute, c'est la "
                "réception qui choisit.",
    },
    'temps': ['Mettre en place', 'Encaisser', 'Reporter', 'Rattacher'],
    'app': 'app-t4c',
    'ecran': ECRAN,
    'css': CSS,
    'vues_initiales': {'odoo': 't4-mode', 'pos': 't4-vente', 'hotel': 't4-folio'},
    'bulles': {
        'b-ident': 'Sans client, la caisse demande « Client requis » avant de valider.',
        'b-mixte': 'Paiement mixte : seule la part « Note de chambre » part sur la chambre.',
        'b-ligne': 'Une seule ligne par ticket, avec sa référence : la caisse et le numéro.',
        'b-motif': 'Le motif dit pourquoi le rattachement automatique n\'a pas eu lieu.',
        'b-folio': 'Seuls les folios ouverts sont proposés.',
    },
    'reactions': {
        'r-caisse': "Je choisis le client, je touche Note de chambre, je valide. C'est tout.",
    },
    'etapes': [
        {'temps': 0, 'titre': 'Une case, une fois pour toutes',
         'texte': 'Le mode « Note de chambre », ajouté aux caisses du bar, du restaurant et de la boutique.',
         'voix': "Une fois pour toutes, la direction crée le mode de paiement Note de chambre : Identifier le client "
                 "coché, journal laissé vide, et la case Note de chambre. On l'ajoute ensuite aux caisses du bar, du "
                 "restaurant et de la boutique.",
         'gestes': [clic('#t4-nom', fx=0.3), saisir('t4-nom', 'Note de chambre'), clic('#t4-cb-ident'),
                    classe('#t4-cb-ident', ajouter=['on']), zoom('#t4-pm-g', s=1.45, d=0.8, fx=0.4),
                    bulle('b-ident', '#t4-cb-ident', cote='droite', d=2.2), pause(2.0), anneau('#t4-journal', d=1.2),
                    clic('#t4-cb-note'), classe('#t4-cb-note', ajouter=['on']),
                    curseur('#t4-l-note-aide', fx=0.3, fy=0.2, d=0.5), montrer('#t4-tip', d=0.35, y=8),
                    pause(2.3), cacher('#t4-tip', d=0.3), dezoom(d=0.6)]},
        {'temps': 1, 'titre': 'Au bar : le ticket et le client',
         'texte': 'Le bouton Client relie le ticket à la fiche du client, pas au numéro de chambre.',
         'voix': "Au bar de la terrasse, Estelle Ngono, cliente de la chambre deux cent quatre, termine son dîner. "
                 "Hervé touche Client et la choisit : c'est sa fiche, et non le numéro de chambre, qui relie le "
                 "ticket à son séjour.",
         'gestes': [montrer('#nav-pos', d=0.5, y=0), pause(0.6), anneau('#t4-vente-ticket', d=1.4), clic('#t4-cli'),
                    ouvrir('t4-dlg'), saisir('t4-q', 'Ngono', d=0.6), cacher('#t4-tous', d=0.25),
                    montrer('#t4-trouves', d=0.3, y=0), pause(0.4), survol('#t4-c-estelle'),
                    anneau('#t4-c-estelle', d=1.6), clic('#t4-c-estelle', fx=0.15), fermer('t4-dlg'), texte('#t4-cli-t', demo.CLIENT),
                    classe('#t4-cli', ajouter=['t04-actif']), curseur('#t4-cli', fx=0.5, fy=0.7, d=0.5),
                    anneau('#t4-acts', d=1.8)]},
        {'temps': 1, 'titre': 'Paiement : « Note de chambre »',
         'texte': 'Le reste à payer tombe à zéro ; le ticket se valide comme d\'habitude.',
         'voix': "Au paiement, il touche Note de chambre : le reste à payer tombe à zéro. Un paiement mixte est "
                 "possible, une part en espèces et le reste sur la chambre ; seule cette part sera reportée. Puis il "
                 "valide, comme d'habitude.",
         'gestes': [clic('#t4-vente-payer'), vue('t4-paie', 'pos'), cacher('#app-t4p .pos-cherche', d=0.2, avec=True),
                    pause(0.4), clic('#t4-m-note'), classe('#t4-m-note', ajouter=['actif']),
                    cacher('#t4-paie-msg', d=0.2), montrer('#t4-paie-restant', d=0.3, y=0), montrer('#t4-pl', d=0.3, y=0),
                    classe('#t4-paie-valider', retirer=['t04-off']), notifier('t4-avert', duree=2.6),
                    zoom('#t4-pl', s=1.3, d=0.7, fy=0.0), bulle('b-mixte', '#t4-paie-restant', cote='haut', d=2.6),
                    pause(2.2), dezoom(d=0.6), reaction('r-caisse', d=3.0), clic('#t4-paie-valider'), pause(1.2)]},
        {'temps': 2, 'titre': 'Sur le folio, sans ressaisie',
         'texte': 'Une ligne de service « POS Bar de la terrasse/0042 », et le solde dû à jour.',
         'voix': "À la réception, Mireille ouvre le folio d'Estelle : le dîner y est déjà, en ligne de service, avec la "
                 "référence du ticket. Les services et le solde dû sont à jour, sans rien ressaisir.",
         'gestes': [montrer('#nav-hotel', d=0.5, y=0), pause(0.5), defiler('#t4-folio-defil', -300, d=0.9),
                    anneau('#t4-fl3', d=1.2), zoom('#t4-fl3', s=1.5, d=0.7, fx=0.3),
                    bulle('b-ligne', '#t4-fl3', cote='haut', d=2.6), pause(2.4), dezoom(d=0.6),
                    defiler('#t4-folio-defil', 0, d=0.8), anneau('#t4-f-serv', d=1.3), anneau('#t4-f-solde', d=1.4)]},
        {'temps': 3, 'titre': 'Un doute ? La file d\'attente',
         'texte': 'Notes de chambre en attente : chaque ticket avec son motif, en orange.',
         'voix': "Quand le rattachement n'est pas certain, le système ne devine pas : le ticket attend dans Notes de "
                 "chambre en attente, avec son motif. Aucun folio ouvert, ou deux folios au même nom.",
         'gestes': [clic('#t4-menu-file'), classe('#t4-menu-fact', retirer=['actif']),
                    classe('#t4-menu-file', ajouter=['actif']), vue('t4-file', 'hotel'), pause(0.5),
                    anneau('#t4-file-fac', d=1.2), survol('#t4-file-0'), anneau('#t4-file-0-motif', d=1.4),
                    bulle('b-motif', '#t4-file-ancre', cote='bas', d=2.6), pause(1.8),
                    anneau('#t4-file-1-motif', d=1.2)]},
        {'temps': 3, 'titre': 'Choisir le bon folio',
         'texte': 'Folio choisi : la liste des folios ouverts, par référence.',
         'voix': "Martin Ebode a deux folios ouverts : son séjour en cours, et une réservation déjà confirmée pour "
                 "novembre. Mireille ouvre la ligne et choisit le folio du séjour en cours.",
         'gestes': [clic('#t4-file-0', fx=0.3), vue('t4-note', 'hotel'), pause(0.3), anneau('#t4-motif', d=1.0),
                    clic('#t4-fc', fx=0.3), classe('#t4-fc', ajouter=['focus']), montrer('#t4-dd', d=0.3, y=-6),
                    zoom('#t4-dd', s=1.35, d=0.6, fy=0.3), bulle('b-folio', '#t4-dd', cote='gauche', d=2.4),
                    survol('#t4-dd-0209'), pause(1.2), clic('#t4-dd-0209', fx=0.3), cacher('#t4-dd', d=0.2),
                    texte('#t4-fc-v', 'FOL/2026/0209'), classe('#t4-fc', retirer=['focus']), dezoom(d=0.5),
                    anneau('#t4-fc', d=1.0)]},
        {'temps': 3, 'titre': '« Rattacher au folio »',
         'texte': 'La note passe « Rattachée » et quitte la file d\'attente.',
         'voix': "Un clic sur Rattacher au folio : la note passe Rattachée, la consommation rejoint le séjour, et la "
                 "ligne quitte la file d'attente.",
         'gestes': [clic('#t4-b-ratt'), cacher('#t4-b-ratt', d=0.2), classe('#t4-nsb-0', retirer=['actif']),
                    classe('#t4-nsb-1', ajouter=['actif']), classe('#t4-fc', ajouter=['lecture']),
                    anneau('#t4-nsb', d=1.3), anneau('#t4-fc', d=1.0), clic('#t4-fil'), vue('t4-file2', 'hotel'),
                    pause(0.3), anneau('#t4-file2 .liste', d=1.6)]},
    ],
    'resultats': {
        'titre': 'Le bar encaisse, le folio suit',
        'cartes': [
            {'valeur': '1', 'compter': 1, 'unite': 'ligne', 'icone': 'document',
             'texte': 'par ticket sur le folio du séjour, avec la référence du ticket'},
            {'valeur': '7 000', 'compter': 7000, 'unite': 'FCFA', 'icone': 'pieces',
             'texte': 'reportés sur un ticket de 12 000 réglé 5 000 en espèces : seule la part « Note de chambre »'},
            {'valeur': '23', 'compter': 23, 'unite': 'tests', 'icone': 'bouclier',
             'texte': 'automatiques vérifient le report, la file d\'attente et le rattachement'},
        ],
        'voix': "Une ligne par ticket, seule la part réglée en note de chambre reportée, et vingt-trois tests "
                "automatiques qui le vérifient.",
    },
    'cta': {
        'appel': 'Demandez votre démonstration',
        'suivant': 'La taxe de séjour',
        'voix': "Aïte haousse, par Aïte Consulting. Demandez votre démonstration. Prochain tutoriel : la taxe de "
                "séjour.",
    },
    'vignette': {'etape': 4, 'apres': 2.95},
}
