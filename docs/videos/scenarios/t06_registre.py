# -*- coding: utf-8 -*-
"""Tutoriel 6 — Fiche de police, registre et statistiques d'hébergement : tout part du check-in.

Personnage : la réceptionniste (demo.POSTES['reception'], Mireille Ateba),
profil Réception (aite_hotel_management.group_hotel_user) : c'est elle qui
fait le check-in, complète les fiches, les imprime et ouvre le registre
(aite_guest_registry/security/ir.model.access.csv:3 — lecture, écriture,
création ; views/menus.xml:4-8, menu sous « Réception »). Barre MuK :
ecrans.APPS_PROFIL['reception'] ; menus de l'application Hôtel du profil
Réception : ecrans.MENUS_MUK['hotel_reception'] (Réception, anciennement
« Front Desk », aite_hotel_management/views/hotel_menus.xml:18-25, ECARTS
n° 42 ; Réservations, Espaces & Prestations, Notes de chambre en attente,
Facturation, Fidélité, Gouvernante ; ordre relevé sur
ref_muk/306-reception-reservations.png). Les statistiques sont réservées au
profil Responsable (views/menus.xml:15-20) : la dernière étape change
d'écran pour la directrice (demo.POSTES['direction'], Danielle Eyenga),
barre ecrans.APPS_PROFIL['direction'] et menus
ecrans.MENUS_MUK['hotel_direction'] (« Activité par pôle » en tête) ; la
pastille du personnage passe alors à « Danielle Eyenga · Directrice »,
initiale D sur la couleur de son avatar (#854F0B), selon le mécanisme de
scenarios/t04_note_chambre.py:456-475.

Titre : la formule « la conformité se remplit toute seule » proposée pour
ce tutoriel n'est pas prouvée (la date de naissance se saisit au premier
séjour, les accompagnants se saisissent en entier, le format officiel
DGSN/MINTOUL reste à confirmer : ROADMAP.md:62 et :78, vérification de
l'analyse) ; le titre retenu, « tout part du check-in », l'est
(aite_guest_registry models/hotel_reservation.py:108-122). Il dit
« statistiques d'hébergement », le nom de l'écran (guest_stats_views.xml
:67-86), et pas « statistiques MINTOUL » : F14 n'est que partiel (TO,
durée moyenne de séjour, état mensuel officiel et export restent à faire,
ROADMAP.md:78 ; la durée moyenne n'est pas une mesure, elle se déduit,
guest_stats.py:9-13 ; le rapport MINTOUL attendu contient TO et DMS,
benchmark_afrique_odoo.md:69). Le MINTOUL ne paraît que dans la douleur
(exigence sourcée), jamais comme un résultat. Le produit n'a plus qu'un nom
pour la fiche, « fiche d'enregistrement » (bouton, fenêtre, aide,
imprimé) : les étapes et la voix le reprennent ; « fiche de police » ne
sert qu'à l'accroche, pour dire l'obligation, et à la promesse, entre
parenthèses après « fiche d'enregistrement », pour relier les deux noms.

Écrans et libellés (relevés mot pour mot, vérifiés par grep -rF dans addons/,
produit de la livraison 4) :

1. Arrivées du jour — aite_hotel_management/views/hotel_menus.xml:18-50
   (Réception et ses sous-menus, séquences 10 à 50) ;
   views/hotel_reservation_views.xml:5-35 (colonnes, décoration info des
   réservations confirmées, somme « Total hébergement » ; colonne « Canal »
   en badge sans couleur, affichée par défaut entre « Solde folio » et
   « Registre » depuis la livraison 4, :23-25, ECARTS n° 58) et :242-243,
   :294-305 (filtre et action « Arrivées du jour ») ; colonne « Registre »
   ajoutée par aite_guest_registry/views/hotel_reservation_views.xml:62-78
   (badge « Aucune fiche » neutre avant l'arrivée, rouge seulement pour un
   client arrivé : ECARTS n° 54) ; libellés des champs et du canal
   (« Direct / comptoir », « Téléphone / WhatsApp ») :
   models/hotel_reservation.py:28-145. Sans colonne Hôtel pour la réception
   (groupe multi-société, hotel_reservation_views.xml:15-16 ; ref_muk/306).
2. Réservation — hotel_reservation_views.xml:37-170 (en-tête :43-70 :
   Check-in, Encaisser un acompte, Envoyer la confirmation, Non présenté
   (anciennement « No-show », ECARTS n° 42), Annuler ; barre Brouillon /
   Confirmée / Arrivé / Parti ; bouton Folio ; groupes Client, Séjour,
   Canal & commission, Occupation ; « Check-in réel » visible une fois
   renseigné ; onglets Chambres / Demandes particulières et colonnes de la
   ligne, :133-160, dont « Prix fixé » (price_locked, case,
   optional="show") et la somme « Total » en pied, comme t01) ; check-in :
   models/hotel_reservation.py:420-444 (état Arrivé, heure réelle). Ajouts
   du registre : aite_guest_registry/views/hotel_reservation_views.xml
   :11-25 (bouton « Fiches d'enregistrement » x/y = fiches complètes /
   occupants attendus, anciennement « Fiches clients »), :27-47 (bandeau
   jaune « Registre des clients : … — compléter maintenant », avec l'espace
   après les deux-points, ECARTS n° 47 ; bandeau vert « Registre des clients
   à jour. » et son lien « Imprimer les fiches »), :49-54 (bouton d'en-tête
   « Imprimer les fiches », icône imprimante, anciennement « Fiches
   d'enregistrement ») ; models/hotel_reservation.py :45-58 (occupants
   attendus = adultes + enfants ; état), :77-102 (phrase accordée
   « 1 fiche à compléter · 1 occupant sans fiche », plus de « (s) »),
   :108-122 (au check-in, la fiche du client principal est créée et
   pré-remplie). Montants et heures du séjour d'Estelle repris de
   scenarios/t01_reception.py (folio 57 000 FCFA après l'acompte, check-in
   réel 14:06:12), canaux comme t01 et c1.
3. Fiches d'enregistrement du séjour — models/hotel_reservation.py:124-163
   (fenêtre « Fiches d'enregistrement — RES/2026/0214 », anciennement
   « Fiches clients — … » ; facette Réservation, valeurs proposées :
   chambre du séjour, dates, nationalité = pays de l'hôtel ; pas de
   résidence par défaut, :155-159) ; views/guest_registration_views.xml:5-33
   (liste éditable en bas, lignes orange « À compléter » / vertes
   « Complète », colonnes Chambre, Nom, Prénom(s), Date de naissance,
   Nationalité, Type de pièce, N° de pièce, Client principal, Signée par le
   client, Il manque, Fiche, imprimante « Imprimer la fiche » ; Résidence et
   Téléphone masquées) ; models/guest_registration.py:70-79 (types de
   pièce), :182-206 (les six informations et la phrase « Il manque »),
   :240-247 (la fiche passe « Complète » toute seule à l'enregistrement),
   :261-304 (pré-remplissage depuis le contact : nom, nationalité,
   résidence, pièce, adresse, téléphone, et la date de naissance si elle a
   été mémorisée sur le contact, guest_birth_date, ECARTS n° 54).
   _name_parts (:261-279) : le contact n'a qu'un nom complet, le module ne
   le coupe pas ; « Estelle Ngono » (demo.CLIENT) donne Nom « Estelle
   Ngono » et Prénom(s) vide, et « Il manque » commence par « le prénom ».
   Mireille sépare elle-même le nom et le prénom avant de saisir la date de
   naissance (tests/test_guest_registry.py,
   test_prefill_keeps_full_name_in_last_name). Le contact d'Estelle porte
   sa nationalité et sa pièce, pas encore sa date de naissance (le champ
   « Date de naissance » de l'onglet Hôtel du contact vient de la livraison
   4, models/res_partner.py:11-19, views/res_partner_views.xml:19-30) :
   elle se saisit ce jour-là ; « Mémoriser sur la fiche client »
   (guest_registration.py:306-328) la reportera sur le contact pour le
   séjour suivant — non montré. Boutons « Enregistrer » / « Ignorer » d'une
   ligne en saisie et fil d'Ariane à deux niveaux :
   odoo18/addons/web/static/src/views/list/list_controller.xml:7-13 et
   :105-114, search/breadcrumbs/breadcrumbs.xml:4-46 ; traductions
   odoo18/addons/web/i18n/fr.po (Save → Enregistrer, Discard → Ignorer).
   Modèle visuel : captures/11_fiches_du_sejour.png.
4. Fiche d'enregistrement imprimée — report/registration_card_report.xml
   :4-109 (« FICHE D'ENREGISTREMENT CLIENT », « Registre des clients — »,
   anciennement « Registre des voyageurs — » ; N°, Chambre (nom de la
   chambre), Réservation, rubriques IDENTITÉ, PIÈCE D'IDENTITÉ, DOMICILE &
   DÉPLACEMENT, SÉJOUR, « Accompagnants » = fiches du séjour − 1, cadres
   « Signature du client » et « Cachet et signature de l'établissement »,
   « Fiche établie le … », mention finale) ; une page par fiche
   (web.external_layout appelé pour chaque fiche, :17-18) ; numérotation
   FICHE/%(year)s/ sur 5 chiffres, sans remise à zéro par période
   (data/sequence_data.xml:4-9), attribuée à la création
   (guest_registration.py:225-232). Le registre commence le 01/08 et ne
   compte que des fiches de séjours arrivés : 399 fiches, autant que
   d'arrivées dans les statistiques. Avec l'ordre « arrival_date desc, id
   desc », Estelle est la première fiche créée le 14/10 (puis Arnaud,
   Martin, Claire) : FICHE/2026/00396, Arnaud FICHE/2026/00397 (Martin
   00398, Claire 00399, non montrés). Le lien « Imprimer les
   fiches » imprime toutes les fiches du séjour :
   models/hotel_reservation.py:165-172. Rapport qweb-pdf : Odoo le
   télécharge, sous le nom du rapport, « Fiche d'enregistrement.pdf »,
   puisqu'il y a plusieurs fiches (name de registration_card_report.xml:5 ;
   odoo18/addons/web/controllers/report.py:130-137, le print_report_name
   « Fiche - … » ne sert qu'à une fiche seule). La vidéo montre le fichier
   téléchargé puis la visionneuse du navigateur, avec sa barre et le nom du
   fichier ; elle ne dit jamais qu'Odoo l'affiche. Adresse imprimée =
   street + city du contact (guest_registration.py:300-301) : « Bonapriso
   Douala » pour Estelle (son contact : t04_note_chambre.py:412), vide pour
   Arnaud, saisi dans une ligne sans colonne Adresse et sans contact lié
   (rapport :65). Pays de résidence et nationalité « Cameroun » pour
   Estelle (country_id de son contact, guest_registration.py:295-297) ;
   pour Arnaud, nationalité « Cameroun » proposée (default_nationality_id,
   hotel_reservation.py:159) et pays de résidence vide ; il est compté
   résident par sa nationalité (guest_registration.py:174-180) ; motif
   « Loisirs / tourisme » (guest_registration.py:102-111, valeur par
   défaut).
5. Registre des clients — views/guest_registration_views.xml:36-61
   (colonnes, lignes orange « À compléter »), :155-188 (filtres « À
   compléter », « Non signées », regroupement « Date d'arrivée » par jour),
   :190-211 (action « Registre des clients », regroupée par jour par défaut,
   aide « l'état chronologique à présenter en cas de contrôle », qui renvoie
   depuis la livraison 4 au bouton « Fiches d'enregistrement » et à « Hôtel
   → Facturation → Registre de police (impression) », ECARTS n° 46 — non
   montrée, le registre n'est pas vide) ; ordre « arrival_date desc, id
   desc » : models/guest_registration.py:20 (date sans heure : le 14/10, la
   fiche créée la dernière vient en tête, d'où Claire, Martin, Arnaud,
   Estelle). Facette « Date d'arrivée: Jour » (odoo18 web/static/src/search/
   search_model.js:1797-1802, « ${description}: ${option} », sans espace
   avant les deux-points) et groupes « 11 oct. 2026 (3) » :
   captures/nouvelles/13_registre_liste.png ; ref_muk/026 ; jour sur deux
   chiffres (« 08 oct. 2026 », format « dd MMM yyyy » :
   odoo18/odoo/models.py:390). Le pager d'une liste groupée compte les
   groupes : un jour d'arrivées du 01/08 au 14/10, soit 75 groupes
   (« 1-75 / 75 »), cohérent avec les 399 arrivées des statistiques depuis
   août ; du 08 au 14/10, les groupes font 54 fiches, comme
   scenarios/c7_conformite.py, et 34 du 01 au 07/10, soit les 88 arrivées
   d'octobre des statistiques. La liste continue jusqu'au bas de l'écran :
   repliée, jusqu'au « 03 oct. 2026 » ; le 14/10 ouvert, jusqu'au
   « 07 oct. 2026 », chaque fois coupé par le bas de la fenêtre.
6. Statistiques d'hébergement — views/guest_stats_views.xml:3-16 (pivot :
   mois d'arrivée en lignes, arrival_date interval="month" : « août 2026 »,
   « septembre 2026 », « octobre 2026 », et non plus « 2026-08 », ECARTS
   n° 4 ; Résident / Non-résident en colonnes, mesures Arrivées et
   Nuitées), :44-66 (filtres Résidents / Non-résidents, regroupements
   « Date d'arrivée » — anciennement « Mois » —, Nationalité, Motif,
   Hôtel), :67-86 (action, regroupée par mois d'arrivée par défaut,
   search_default_group_month, d'où la facette « Date d'arrivée: Mois » ;
   vues pivot, graphique, liste) ; models/guest_stats.py:5-101 (une ligne
   par fiche des séjours Arrivé ou Parti : 1 arrivée, ses nuits = nuitées ;
   relue à chaque lecture ; le mois « AAAA-MM » ne reste qu'un champ
   technique pour les exports, :29-32) ; models/guest_registration.py
   :174-180 (résident = pays de résidence, à défaut nationalité, égal au
   pays de l'hôtel). Menu de regroupement d'un en-tête de pivot, ouvert
   sous la cellule et aligné sur son bord droit pour un en-tête de ligne
   (position « bottom-end », pivot_header.xml:5) :
   odoo18/addons/web/static/src/views/pivot/pivot_header.xml:4-74 et
   pivot_header.js:62-87 (les regroupements de la recherche, aucun coché ;
   « Date d'arrivée » ouvre ses intervalles, flèche à droite,
   core/dropdown/dropdown.js:250-263 ; « Ajouter un groupe personnalisé »,
   web/i18n/fr.po). Modèle visuel : captures/nouvelles/14_stats_pivot.png,
   ref_muk/033 (colonnes Non-résident puis Résident).

Accroche (douleurs), toutes sourcées :
- docs/etude_comparative/benchmark_afrique_odoo.md:13 et :66 — loi
  n° 2016/006, art. 28 : « la violation des obligations de police en
  matière d'enregistrement des clients » est sanctionnée (carte bouclier) ;
  :66 — les champs usuels à relever, colonne « ce qu'il faut prévoir »
  d'AITE : nom, prénoms, date de naissance, nationalité, pièce, dates (carte
  fiche, dite « champs usuels », pas « obligatoires ») ; :13 et :66 — « aucun modèle officiel de
  fiche/registre trouvé en ligne » (carte interrogation, formulée « trouvé
  en ligne », pas « publié ») ;
- :69 — statistiques exigées par le MINTOUL (art. 16), amende de 50 000 à
  500 000 FCFA (art. 45) (carte graphe et voix). L'amende n'est sourcée que
  pour les statistiques : pour l'enregistrement, la source parle
  d'« infraction » (art. 28) sans sanction chiffrée, et la voix dit
  seulement « obligation de police » ;
- :80 — Côte d'Ivoire : la fiche d'hébergement numérisée (HORA, Police
  nationale, 2023), « ex-fiche papier » (carte globe).

Résultats : « 1 clic » — le check-in crée et pré-remplit la fiche du client
principal (aite_guest_registry models/hotel_reservation.py:108-122) ;
« 6 informations » requises par la fiche pour passer « Complète », suivies
par « Il manque » (guest_registration.py:182-206, 240-247 : c'est la liste
du module, pas une liste légale ; la source n'en fixe aucune,
benchmark_afrique_odoo.md:66, « aucun modèle officiel ») ;
« 4 regroupements » des statistiques : Date d'arrivée (par mois),
Nationalité, Motif, Hôtel (guest_stats_views.xml:54-63), dits « mois
d'arrivée, nationalité, motif, hôtel » sur la carte.

Données (fictives, demo.py) : Complexe Hôtelier — Démo, Démo Hôtellerie
SARL ; Estelle Ngono, RES/2026/0214, chambre 204 [CFT], 2 adultes, du 14 au
16/10/2026, canal « Direct / comptoir », contact « Bonapriso Douala
Cameroun » (t04_note_chambre.py:412 ; t11 : elle habite Douala) ; Martin
Ebode (RES/2026/0209, Kribi, chambre 104 [STD] : 105 000 FCFA pour 3 nuits
= 35 000 FCFA, tarif Standard, comme dans t07_gouvernante.py (CLIENTS) et
t02_planning.py, canal « Direct / comptoir ») et Claire Durand
(RES/2026/0201, Lyon, France, chambre 401 [VIP] comme dans t02, canal
« Téléphone / WhatsApp » : elle appelle de France, comme t01 et c1) ;
leurs montants comme dans t01. Ajoutés ici, fictifs : Arnaud Ngono
(l'accompagnant d'Estelle, repris de scenarios/c7_conformite.py), dates de
naissance et numéros de pièce. Les fiches de Claire et de Martin, créées à
leur check-in et pas encore reprises, portent le nom complet du contact et
un prénom vide (Nom « Claire Durand », Nom « Martin Ebode ») : elles
restent « À compléter ». Groupes du registre du 08 au 14/10 : 9, 8, 9, 7,
10, 7 et 4 fiches = 54 (c7), soit 4 à 10 arrivées par jour pour les 20
chambres de l'hôtel (environ 1,5 occupant par chambre). Les statistiques
d'août à octobre 2026 sont celles de c7 (sommes vérifiées), octobre
détaillé par nationalité (sommes égales aux totaux) ; octobre est partiel
(du 01 au 14/10), d'où « en cours de mois » dans la voix. Plausibles pour
20 chambres : 408 nuitées en septembre, soit environ 270 nuits-chambres sur
600 possibles (20 × 30) à 1,5 occupant.

Écarts relevés dans l'application, et leur sort à la livraison 4 :
1. Corrigé dans aite_guest_registry 18.0.1.0.2 (ECARTS n° 16) : le registre
   de police (Facturation → Registre de police (impression)) s'imprime
   depuis l'interface ; depuis la livraison 4, une période vide le dit en
   jj/mm/aaaa (wizard/police_register_wizard.py:63-69). Ce tutoriel ne le
   montre pas (durée) : il montre le registre des clients (liste) et la
   fiche imprimée ; le chapitre 7 de la présentation montre le registre
   imprimé.
2. Corrigé dans la livraison 4 (ECARTS n° 54) : la colonne « Registre »
   affichait « Aucune fiche » en rouge sur toutes les réservations pas
   encore arrivées ; le badge est désormais neutre avant l'arrivée
   (aite_guest_registry hotel_reservation_views.xml:69-75) : gris sur les
   arrivées du jour.
3. Corrigé dans la livraison 4 (ECARTS n° 4) : le mois des statistiques ne
   s'affiche plus « 2026-10 » mais « octobre 2026 » (regroupement
   arrival_date:month, guest_stats_views.xml:10 et :55-56).
4. Corrigé dans la livraison 4 (ECARTS n° 47 et relecture de l'écart
   n° 44) : le bandeau porte l'espace après les deux-points et une phrase
   accordée, « Registre des clients : 1 fiche à compléter · 1 occupant sans
   fiche » (et non plus « clients :1 fiche(s) … 1 occupant(s) »).
5. Corrigé dans la livraison 4 (ECARTS n° 48) : l'aide « Arrivées du jour »
   ne promet plus qu'au check-in « le registre des clients s'ouvre » ; elle
   annonce le bandeau de la réservation (aite_hotel_management/views/
   hotel_reservation_views.xml:300-303), ce que la vidéo montre. L'aide
   n'est pas affichée (la liste n'est pas vide).
6. Corrigé dans aite_guest_registry 18.0.1.0.2 (ECARTS n° 30 b) : une
   nouvelle ligne ne reçoit plus d'office Résidence = pays de l'hôtel
   (hotel_reservation.py:155-159) ; la page d'Arnaud du PDF a donc un pays
   de résidence vide.
7. Corrigé dans aite_guest_registry 18.0.1.0.2 (ECARTS n° 14) :
   « Mémoriser sur la fiche client » écrit sur le contact en sudo
   (guest_registration.py:306-328, test_reception_copies_back_to_partner)
   et fonctionne pour la Réception ; depuis la livraison 4, il mémorise
   aussi la date de naissance (ECARTS n° 54). Non montré.
8. Corrigé dans aite_guest_registry 18.0.1.0.2 (ECARTS n° 30 a) : le
   pré-remplissage ne coupe plus le nom au premier espace ; le nom complet
   du contact va dans « Nom », « Prénom(s) » reste vide et « Il manque » le
   signale (guest_registration.py:261-279). Montré à l'étape 2 : Mireille
   sépare elle-même « Ngono » et « Estelle ».
9. Corrigé dans la livraison 4 (relecture de l'intégration) : un seul nom,
   « fiche d'enregistrement » — bouton intelligent « Fiches
   d'enregistrement » (anciennement « Fiches clients »), fenêtre
   « Fiches d'enregistrement — RES/… », bouton d'en-tête « Imprimer les
   fiches », imprimé « Registre des clients — » ; « Non présenté »
   remplace « No-show », « Réception » remplace « Front Desk » (ECARTS
   n° 42). Le fil de la fiche dirait « Fiche d'enregistrement créée »
   (guest_registration.py:208-212) : t06 ne montre pas ce fil.

Captures de référence (modèle visuel, jamais incrustées) : ref_muk/023,
026, 027, 032, 033, 306 ; captures/10, 11, 12, nouvelles/13, nouvelles/14.

Voix : « check-inne » pour que Kokoro ne lise pas « check-in » à
l'anglaise (comme t01) ; « Aïte haousse », « Aïte Consulting ».
"""

import demo
from ecrans import (APPS_PROFIL, ICONES, MENUS_MUK, NBSP, bouton, champ, compte, cp_fiche, deux_colonnes, e, entier,
                    entree, fcfa, fenetre_muk, groupe, icone, mois_long, navigateur, onglets, statusbar, titre_fiche,
                    vue_fiche, vue_libre)
from marketing import bulle, dezoom, reaction, zoom
from moteur import anneau, animer, cacher, choisir, clic, classe, curseur, defiler, etat, montrer, pause, saisir, texte, vue

NOM, ROLE = demo.POSTES['reception']            # Mireille Ateba, réceptionniste
DIRECTRICE = demo.POSTES['direction'][0]        # Danielle Eyenga
APP = 'app-t6'
# Barres de menus de l'application Hôtel (hotel_menus.xml : « Réception »,
# anciennement « Front Desk », ECARTS n° 42 ; exec_menus.xml : « Activité par pôle »).
MENUS = MENUS_MUK['hotel_reception']
MENUS_DIR = MENUS_MUK['hotel_direction']
MENU_RECEPTION = '#app-t6 .o-haut .menu.actif'
SOLDE = fcfa(57000)                   # le folio d'Estelle après l'acompte (t01)
CHECKIN_REEL = '14/10/2026 14:06:12'  # comme t01
# Canal des arrivées du jour, comme t01 et c1 : Estelle et Martin au comptoir,
# Claire au téléphone depuis la France (hotel_reservation.py:70-80).
CANAL = 'Direct / comptoir'
CANAL_CLAIRE = 'Téléphone / WhatsApp'

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
# Colonnes de la liste (hotel_reservation_views.xml:9-33) : « Canal » en badge
# sans couleur, affiché par défaut depuis la livraison 4 (:23-25, ECARTS n° 58),
# entre « Solde folio » et « Registre » ; « Aucune fiche » neutre avant
# l'arrivée (aite_guest_registry hotel_reservation_views.xml:69-75, ECARTS n° 54).
COLS_ARR = [('Référence', '136px'), ('Client', '116px'), ('Arrivée', '168px'), ('Départ', '168px'), ('Nuits', '46px', 'd'),
            ('Nb chambres', '64px', 'd'), ('Total hébergement (HT)', '124px', 'd'), ('Solde folio', '108px', 'd'),
            ('Canal', '194px'), ('Registre', '124px'), ('État', '1fr')]


def arrivee(ident, ref, client, arr, dep, nuits, total, solde, canal):
    return ligne6(ident, COLS_ARR, [('<span class="lien ell">%s</span>' % e(ref),), client, arr, dep, nuits, '1',
                                    fcfa(total), fcfa(solde), badge(canal, 'gris'), badge('Aucune fiche', 'gris'),
                                    badge('Confirmée', 'info')], 't06-info')


ARRIVEES = vue_libre('t06-arr', cp_liste6('Arrivées du jour', facette_filtre('Arrivées du jour'), '1-3 / 3') + (
    '<div class="liste">%s%s%s%s<div class="total" style="grid-template-columns:40px %s"><span></span>%s</div></div>'
    % (tete(COLS_ARR),
       arrivee('t06-a0', 'RES/2026/0201', 'Claire Durand', '14/10/2026 18:00:00', '15/10/2026 12:00:00', '1',
               120000, 0, CANAL_CLAIRE),
       arrivee('t06-a1', demo.RESA, demo.CLIENT, demo.ARRIVEE, demo.DEPART, '2', 90000, 57000, CANAL),
       arrivee('t06-a2', 'RES/2026/0209', 'Martin Ebode', '14/10/2026 14:00:00', '17/10/2026 12:00:00', '3',
               105000, 35000, CANAL),
       ' '.join(c[1] for c in COLS_ARR),
       ''.join('<span class="d">%s</span>' % e(t) if t else '<span></span>'
               for t in ['', '', '', '', '', '', fcfa(120000 + 90000 + 105000), '', '', '', '']))), initiale=True)

# ========================================================= 2. Réservation --
# Les lignes de la réservation (hotel_reservation_views.xml:133-160) : « Prix fixé »
# (price_locked, case décochée, optional="show") entre « Prix / nuit » et
# « Sous-total (HT) », somme « Total » en pied de liste — comme t01.
LIGNE_CH = (
    '<div class="table t06-tab"><div class="t-tete" style="grid-template-columns:%(g)s">%(t)s</div>'
    '<div class="t-ligne" style="grid-template-columns:%(g)s"><span>Confort</span><span>204 [CFT]</span>'
    '<span class="d">2</span><span class="d">0</span><span></span><span class="d">2</span><span class="d">%(px)s</span>'
    '<span class="t06-pf"><span class="case"><i></i></span></span>'
    '<span class="d">%(heb)s</span><span class="t06-ech">%(ech)s</span></div>'
    '<div class="t-ajout">Ajouter une ligne</div>'
    '<div class="t-total" style="grid-template-columns:%(g)s">%(vides)s<span class="d">%(heb)s</span><span></span></div>'
    '</div>'
    % {'g': '1fr 160px 100px 100px 130px 70px 160px 110px 180px 40px',
       't': ''.join('<span class="ell%s">%s</span>' % (' d' if d else '', e(x)) for x, d in (
           ('Type', 0), ('Chambre', 0), ('Adultes', 1), ('Enfants', 1), ('Occupants', 0), ('Nuits', 1),
           ('Prix / nuit', 1), ('Prix fixé', 0), ('Sous-total (HT)', 1), ('', 0))),
       'px': e(demo.PRIX_NUIT), 'heb': e(demo.TOTAL_HEB), 'vides': '<span></span>' * 8, 'ech': icone('echange')})
FEUILLE_RESA = (
    titre_fiche(demo.RESA)
    + deux_colonnes(
        groupe('Client', [champ('Client', demo.CLIENT, lien_=True), champ('Téléphone', demo.CLIENT_TEL),
                          champ('E-mail', demo.CLIENT_MAIL), champ('Hôtel', demo.HOTEL, lien_=True)])
        + groupe('Canal & commission', [champ('Canal', CANAL)]),
        groupe('Séjour', [champ('Arrivée', demo.ARRIVEE, gras=True), champ('Départ', demo.DEPART, gras=True),
                          champ('Nuits', '2'), champ('Total hébergement (HT)', demo.TOTAL_HEB)])
        + '<div class="masque t06-cireel" id="t06-cireel">%s</div>' % champ('Check-in réel', CHECKIN_REEL)
        + groupe('Occupation', [champ('Nb chambres', '1'), champ('Adultes', '2'), champ('Enfants', '0')]))
    + onglets(['Chambres', 'Demandes particulières']) + LIGNE_CH)
# Au check-in, le bandeau jaune, accordé (« 1 fiche à compléter · 1 occupant
# sans fiche », aite_guest_registry models/hotel_reservation.py:77-102) et avec
# l'espace après les deux-points (« clients&#160;: », vue :35, ECARTS n° 47) ;
# quand les deux fiches sont complètes, le bandeau vert (:40-46).
BANDEAUX = (
    '<div class="bandeau masque" id="t06-bandeau">%s<span><b>Registre des clients' + NBSP + ': </b>'
    + e(' · '.join([compte(1, 'fiche à compléter', 'fiches à compléter', tdb=False),
                    compte(1, 'occupant sans fiche', 'occupants sans fiche', tdb=False)]))
    + ' — <span class="act" id="t06-completer">compléter maintenant</span></span></div>'
    '<div class="bandeau t06-ok-b masque" id="t06-bandeau-ok">%s<b>Registre des clients à jour.</b>'
    '<span class="act" id="t06-imprimer">Imprimer les fiches</span></div>') % (icone('fiche'), icone('coche'))
# En-tête (hotel_reservation_views.xml:43-70) : « Imprimer les fiches » après
# « Envoyer la confirmation » (aite_guest_registry hotel_reservation_views.xml
# :49-54), « Non présenté » (anciennement « No-show ») tant qu'elle est confirmée.
B_CONF = [bouton('t06-b-checkin', 'Check-in', 'primaire'), bouton(None, 'Encaisser un acompte'),
          bouton(None, 'Envoyer la confirmation'), bouton(None, 'Imprimer les fiches', ico='imprimer'),
          bouton(None, 'Non présenté'), bouton(None, 'Annuler')]
B_ARRIVE = [bouton(None, 'Check-out', 'primaire'), bouton(None, 'Encaisser un acompte'),
            bouton(None, 'Envoyer la confirmation'), bouton(None, 'Imprimer les fiches', ico='imprimer'),
            bouton(None, 'Annuler')]
# Bouton intelligent « Fiches d'enregistrement » x/y (vue :11-25, anciennement « Fiches clients »).
RESA = vue_fiche('t06-resa', cp_fiche('Arrivées du jour', demo.RESA, '2 / 3', stats=[
    ('t06-st-folio', 'document', 'Folio', SOLDE), ('t06-st-fiches', 'fiche', "Fiches d'enregistrement", '0/2')]),
    B_CONF, statusbar('t06-sb', ['Brouillon', 'Confirmée', 'Arrivé', 'Parti'], 1), FEUILLE_RESA, bandeau=BANDEAUX,
    boutons_apres=[B_ARRIVE])

# ======================================= 3. Fiches d'enregistrement du séjour --
# Fenêtre « Fiches d'enregistrement — RES/… » (anciennement « Fiches clients »,
# aite_guest_registry models/hotel_reservation.py:124-163).
COLS_F = [('Chambre', '96px'), ('Nom', '124px'), ('Prénom(s)', '86px'), ('Date de naissance', '118px'),
          ('Nationalité', '100px'), ('Type de pièce', '206px'), ('N° de pièce', '108px'), ('Client principal', '68px'),
          ('Signée par le client', '68px'), ('Il manque', '1fr'), ('Fiche', '116px'), ('', '30px')]
CNI = "Carte nationale d'identité"
MANQUE_NOUVELLE = ['le nom, le prénom, la date de naissance, le type de pièce, le numéro de pièce',
                   'le prénom, la date de naissance, le type de pièce, le numéro de pièce',
                   'la date de naissance, le type de pièce, le numéro de pièce',
                   'le type de pièce, le numéro de pièce', 'le numéro de pièce', '']
# La fiche d'Estelle pré-remplie depuis son contact : nom complet dans « Nom », prénom vide
# (_name_parts, guest_registration.py:261-279) ; nationalité et pièce viennent du contact
# (_vals_from_partner, :280-304).
MANQUE_ESTELLE = ['le prénom, la date de naissance', 'la date de naissance', '']


def cel(ident, valeur=''):
    """Une cellule de la ligne en saisie (champ de liste éditable)."""
    return (entree(ident, '', valeur, classe='entree t06-c'),)


IMPRIMANTE = ('<span class="t06-print">%s</span>' % ICONES['imprimer'],)
FICHE_ESTELLE = ligne6('t06-f0', COLS_F, [
    '204 [CFT]', cel('t06-f0-nom', demo.CLIENT), cel('t06-f0-pre'), cel('t06-f0-dn'), 'Cameroun', CNI,
    '114208815', case(True), case(False),
    ('<span class="ell" id="t06-f0-im">%s</span>' % e(MANQUE_ESTELLE[0]),), badge('À compléter', 'orange', 't06-f0-et'),
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
    '<span id="t06-f-fil-resa">%s</span></span><span class="ref">Fiches d\'enregistrement — %s %s</span></div>%s'
    '<span class="pager" id="t06-f-pager">1-1 / 1</span></div>'
    % (e(demo.RESA), e(demo.RESA), engrenage(), recherche6(facette_champ('Réservation', demo.RESA))))
FICHES = vue_libre('t06-fiches', CP_FICHES + '<div class="liste t06-lf">%s%s%s</div>' % (
    tete(COLS_F, '<span class="t06-opt">%s</span>' % REGLAGES), FICHE_ESTELLE, FICHE_ARNAUD))

# ======================================= 4. La fiche d'enregistrement (PDF) --
def pdf_page(ident, num, nom, prenom, ne, tel, piece, adresse, residence):
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
        + '<tr><td><b>Adresse</b></td><td colspan="3">%s</td></tr>' % e(adresse)
        + lig('Pays de résidence', e(residence), 'Motif du séjour', 'Loisirs / tourisme')
        + lig('Provenance', '', 'Destination', '')
        + '<tr><th colspan="4">SÉJOUR</th></tr>'
        + lig('Arrivée', '14/10/2026', 'Départ prévu', '16/10/2026') + lig('Nuits', '2', 'Accompagnants', '1'))
    return (
        '<div class="t06-page" id="%s"><div class="t06-soc">%s</div>'
        '<div class="t06-ph"><div><h3>FICHE D\'ENREGISTREMENT CLIENT</h3><div class="t06-gris">Registre des clients — %s'
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


# Numéros : les 399 fiches du registre depuis le 01/08, Estelle la première du 14/10, puis Arnaud,
# Martin et Claire (ordre « arrival_date desc, id desc » du registre ; sequence_data.xml, sans plage de dates).
FICHE_ESTELLE_N, FICHE_ARNAUD_N = 'FICHE/2026/00396', 'FICHE/2026/00397'
# Odoo télécharge le rapport (qweb-pdf) sous le nom « Fiche d'enregistrement.pdf » (report.py:130-137) ;
# on l'ouvre ensuite dans la visionneuse du navigateur, avec sa barre et le nom du fichier.
FICHIER_PDF = "Fiche d'enregistrement.pdf"
TELECHARGE = ('<div class="t06-dlc masque" id="t06-dlc" data-layout-allow-overlap data-layout-allow-occlusion>'
              '<span class="t06-dlc-i">%s</span><span class="t06-dlc-n">%s</span></div>'
              % (ico(TELECHARGER), e(FICHIER_PDF)))
PDF = ('<div class="t06-pdf masque" id="t06-pdf" data-layout-allow-overlap data-layout-allow-occlusion>'
       '<div class="t06-pdfb"><span class="t06-pdfb-n">%s</span><span class="t06-pdfb-p">1 / 2</span></div>'
       '<div class="t06-pages">%s%s</div></div>'
       % (e(FICHIER_PDF),
          pdf_page('t06-p1', FICHE_ESTELLE_N, 'Ngono', 'Estelle', '12/03/1991', demo.CLIENT_TEL, '114208815',
                   'Bonapriso Douala', 'Cameroun'),
          pdf_page('t06-p2', FICHE_ARNAUD_N, 'Ngono', 'Arnaud', '27/08/1989', '', '116502371', '', '')))   # pas de résidence par défaut

# ============================================== 5. Le registre des clients --
DEROULANT = ('<div class="t06-dd masque" id="t06-dd" data-layout-allow-overlap data-layout-allow-occlusion>%s</div>'
             % ''.join('<div class="t06-dd-i" id="t06-dd-%s">%s</div>' % (i, e(t)) for i, t in (
                 ('tdb', 'Tableau de bord'), ('rap', 'Réservation rapide'), ('arr', 'Arrivées du jour'),
                 ('dep', 'Départs du jour'), ('reg', 'Registre des clients'), ('pre', 'Clients présents'))))
COLS_R = [('Arrivée', '112px'), ('Départ', '112px'), ('Chambre', '104px'), ('Nom', '136px'), ('Prénom(s)', '92px'),
          ('Date de naissance', '136px'), ('Nationalité', '110px'), ('Type de pièce', '222px'), ('N° de pièce', '112px'),
          ('Fiche', '124px'), ('Signée par le client', '1fr')]
GROUPES = [('14 oct. 2026', 4), ('13 oct. 2026', 7), ('12 oct. 2026', 10), ('11 oct. 2026', 7), ('10 oct. 2026', 9),
           ('09 oct. 2026', 8), ('08 oct. 2026', 9)]
assert sum(n for _, n in GROUPES) == 54      # du 08 au 14/10, comme c7
# Du 01 au 07/10 : 34 fiches, pour les 88 arrivées d'octobre des statistiques (vérifié plus bas).
# La liste groupée continue jusqu'au bas de l'écran (75 groupes) : les jours suivants, coupés par le
# bas de la fenêtre, se devinent sous les autres.
GROUPES_AVANT = [('07 oct. 2026', 6), ('06 oct. 2026', 4), ('05 oct. 2026', 5), ('04 oct. 2026', 3),
                 ('03 oct. 2026', 5), ('02 oct. 2026', 6), ('01 oct. 2026', 5)]
assert sum(n for _, n in GROUPES_AVANT) == 34


def groupe_r(ident, lib, n, ouvert=False):
    return ('<div class="groupe t06-gr" id="%s"><span class="t06-car">%s</span>%s (%d)</div>'
            % (ident, '▾' if ouvert else '▸', e(lib), n))


def personne(ident, dep, ch, nom, prenom, ne, nat, piece, num_, complete):
    return ligne6(ident, COLS_R, ['14/10/2026', dep, ch, nom, prenom, ne, nat, piece, num_,
                                  badge('Complète', 'vert') if complete else badge('À compléter', 'orange'),
                                  case(False)], '' if complete else 'avert')


TETE_R = tete(COLS_R, '<span class="t06-opt">%s</span>' % REGLAGES)
# Tout replié : du 14 au 03/10, le dernier coupé par le bas de la fenêtre.
REG_A = ('<div class="liste t06-lr" id="t06-rg-a">%s%s</div>'
         % (TETE_R, ''.join(groupe_r('t06-rg-g%d' % i, lib, n)
                            for i, (lib, n) in enumerate(GROUPES + GROUPES_AVANT[:5]))))
REG_B = ('<div class="liste t06-lr masque" id="t06-rg-b">%s%s%s%s</div>' % (
    TETE_R, groupe_r('t06-rg-b-g0', GROUPES[0][0], GROUPES[0][1], ouvert=True),
    # ordre « arrival_date desc, id desc » : la dernière fiche créée en tête ; Claire et Martin, pas encore
    # repris, gardent le nom complet du contact et un prénom vide (guest_registration.py:261-279)
    personne('t06-rg-claire', '15/10/2026', '401 [VIP]', 'Claire Durand', '', '', 'France', '', '', False)
    + personne('t06-rg-martin', '17/10/2026', '104 [STD]', 'Martin Ebode', '', '', 'Cameroun', CNI, '112640339', False)
    + personne('t06-rg-arnaud', '16/10/2026', '204 [CFT]', 'Ngono', 'Arnaud', '27/08/1989', 'Cameroun', CNI,
               '116502371', True)
    + personne('t06-rg-estelle', '16/10/2026', '204 [CFT]', 'Ngono', 'Estelle', '12/03/1991', 'Cameroun', CNI,
               '114208815', True),
    # le 14/10 ouvert : les jours suivants jusqu'au 07/10, coupé par le bas de la fenêtre
    ''.join(groupe_r('t06-rg-b-g%d' % i, lib, n) for i, (lib, n) in enumerate(GROUPES + GROUPES_AVANT[:1]) if i)))
REGISTRE = vue_libre('t06-registre', cp_liste6('Registre des clients', facette_groupe("Date d'arrivée: Jour"),
                                               '1-75 / 75') + REG_A + REG_B)

ECRAN_RECEPTION = fenetre_muk(APP, 'Hôtel', MENUS, [ARRIVEES, RESA, FICHES, REGISTRE], actif='Réception',
                              societe=demo.SOCIETE, initiale=NOM[0], avatar='#185FA5', apps=APPS_PROFIL['reception'],
                              app_active='Hôtel', calques=DEROULANT + TELECHARGE + PDF)

# ================================== 6. Les statistiques (écran direction) --
# Lignes par mois d'arrivée (guest_stats_views.xml:7-13, arrival_date
# interval="month") : « octobre 2026 » et non plus « 2026-10 » (ECARTS n° 4).
# (libellé, [arrivées NR, nuitées NR, arrivées R, nuitées R, arrivées, nuitées])
MOIS = [(mois_long(8, 2026), [38, 96, 112, 251, 150, 347]), (mois_long(9, 2026), [41, 118, 120, 290, 161, 408]),
        (mois_long(10, 2026), [22, 71, 66, 185, 88, 256])]
OCTOBRE = mois_long(10, 2026)
TOTAL = [101, 285, 298, 726, 399, 1011]
PAYS_OCT = [('Cameroun', [3, 9, 63, 177, 66, 186]), ('Chine', [2, 6, None, None, 2, 6]),
            ('France', [9, 31, 2, 5, 11, 36]), ('Gabon', [3, 11, 1, 3, 4, 14]), ('Nigeria', [5, 14, None, None, 5, 14])]
# les sommes d'octobre par pays égalent la ligne du mois
assert [sum(v[i] or 0 for _, v in PAYS_OCT) for i in range(6)] == MOIS[2][1]
assert [sum(v[i] for _, v in MOIS) for i in range(6)] == TOTAL
# le registre d'octobre (du 01 au 14/10) compte autant de fiches que d'arrivées en octobre
assert sum(n for _, n in GROUPES + GROUPES_AVANT) == MOIS[2][1][4]


def n_(v):
    """Un entier du pivot, milliers séparés par l'espace insécable de fr_FR (res.lang.csv)."""
    return '' if v is None else entier(v)


def pv_tr(ident, lib, vals, niveau, ouvert=False, classe_=''):
    return ('<tr%s%s><th class="t06-pvh" style="padding-left:%dpx"%s>%s %s</th>%s</tr>'
            % (' id="%s"' % ident if ident else '', ' class="%s"' % classe_ if classe_ else '', 14 + 24 * niveau,
               '', '⊟' if ouvert else '⊞', e(lib), ''.join('<td>%s</td>' % n_(v) for v in vals)))


ENTETES = ('<tr><td class="vide"></td><th colspan="4">⊟ Total</th><td class="vide" colspan="2" rowspan="2"></td></tr>'
           '<tr><td class="vide"></td><th colspan="2">⊞ Non-résident</th><th colspan="2">⊞ Résident</th></tr>'
           '<tr><td class="vide"></td>%s</tr>' % ('<th class="m">Arrivées</th><th class="m">Nuitées</th>' * 3))


def pivot(ident, detail=False):
    lignes = pv_tr(None, 'Total', TOTAL, 0, ouvert=True, classe_='tot')
    for lib, vals in MOIS:
        if lib == OCTOBRE:
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
    % (recherche6(facette_groupe("Date d'arrivée: Mois")), VUES_PV, ico(TELECHARGER), pivot('t06-pv-a'),
       pivot('t06-pv-b', True))),
    initiale=True)
# Le menu d'un en-tête du pivot (odoo18 web/views/pivot/pivot_header.xml et
# .js:62-87), ouvert sous la cellule et aligné sur son bord droit pour un
# en-tête de ligne (position « bottom-end », pivot_header.xml:5), reprend les
# regroupements de la recherche (guest_stats_views.xml
# :54-63) : « Date d'arrivée », regroupement par date ouvert sur ses
# intervalles (flèche à droite), puis Nationalité, Motif, Hôtel ; aucune
# entrée cochée (isActive: false) ; puis « Ajouter un groupe personnalisé ».
MENU_PV = ('<div class="t06-pvm masque" id="t06-pvm" data-layout-allow-overlap data-layout-allow-occlusion>'
           '<div class="t06-pvm-i t06-pvm-d">Date d\'arrivée<span>▸</span></div>'
           '<div class="t06-pvm-i" id="t06-pvm-nat">Nationalité</div>'
           '<div class="t06-pvm-i">Motif</div><div class="t06-pvm-i">Hôtel</div><div class="t06-pvm-sep"></div>'
           '<div class="t06-pvm-i t06-pvm-c">Ajouter un groupe personnalisé<span>▾</span></div></div>')
ECRAN_DIRECTION = fenetre_muk('app-t6d', 'Hôtel', MENUS_DIR, [STATS], actif='Facturation', societe=demo.SOCIETE,
                              initiale=DIRECTRICE[0], avatar='#854F0B', apps=APPS_PROFIL['direction'],
                              app_active='Hôtel', calques=MENU_PV)

# Deux cadres de navigateur superposés : la réception, puis l'écran de la
# directrice qui se pose dessus (un changement d'écran, comme t04 et t08).
ECRAN = (navigateur(ECRAN_RECEPTION)
         + navigateur(ECRAN_DIRECTION, 't06-nav-dir').replace('class="navigateur"', 'class="navigateur masque"', 1))

# La pastille du personnage passe à la directrice à l'étape 6 (mécanisme de t04_note_chambre.py:456-475).
PASTILLE_DIR = (
    '#tu-perso.t06-pd > span:last-child { font-size: 0; }\n'
    '#tu-perso.t06-pd > span:last-child::before { content: "%s"; font-size: 21px; font-weight: 700; }\n'
    '#tu-perso.t06-pd > span:last-child::after { content: " · %s"; font-size: 21px; white-space: pre; }\n'
    '#tu-perso.t06-pd .av { background: #854F0B; color: #fff; }\n' % demo.POSTES['direction'])

CSS = PASTILLE_DIR + """
/* t06 — registre des clients : listes resserrées, réservation, fiche PDF, pivot */
#app-t6 .o-haut, #app-t6d .o-haut { gap: 22px; font-size: 19px; }
#app-t6d .o-haut { gap: 15px; font-size: 16px; }
#app-t6d .o-haut .nom-app { font-size: 21px; }
#app-t6d .o-haut .menu.actif { font-weight: 600; }
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
#app-t6 .t06-tab .t-ajout, #app-t6 .t06-tab .t-total { height: 46px; font-size: 17px; }
#app-t6 .t06-pf { display: flex; align-items: center; }
#app-t6 .t06-pf .case i { width: 18px; height: 18px; border-color: #CED4DA; }
#app-t6 .t06-ech { color: #3F6A83; display: inline-flex; width: 22px; height: 22px; }
#app-t6 .t06-ech svg { width: 22px; height: 22px; }
#app-t6 .bandeau.t06-ok-b { background: #D1E7DD; border-color: #A3CFBB; color: #0A3622; }
#app-t6 .bandeau.t06-ok-b .act { color: #0A3622; margin-left: 10px; }
/* fiches clients : liste éditable */
.t06-pbts { display: inline-flex; }
.t06-sbts { display: inline-flex; gap: 6px; white-space: nowrap; }
.t06-sep { margin: 0 8px; color: var(--o-texte-3); }
#t06-f-fil .parent { display: flex; font-weight: 600; }
#t06-f-fil { flex: none; }
#t06-f-fil .ref { display: inline-flex; align-items: center; gap: 8px; white-space: nowrap; }
/* titre plus long depuis la livraison 4 (« Fiches d'enregistrement — … ») : la
   recherche se cale à droite, contre le pager, pour laisser le fil sur une ligne */
#t06-fiches .cp .recherche { margin-left: auto; }
#t06-fiches .cp .pager { margin-left: 0; }
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
/* menu déroulant « Réception » */
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
.t06-pdf { position: absolute; left: 0; top: 0; right: 0; bottom: 0; z-index: 27; background: #525659; overflow: hidden; }
.t06-pdfb { height: 52px; background: #323639; color: #F1F3F4; display: flex; align-items: center; padding: 0 24px;
  font-size: 18px; box-shadow: 0 2px 6px rgba(0,0,0,.35); position: relative; }
.t06-pdfb-p { position: absolute; left: 50%; transform: translateX(-50%); background: #191B1C; padding: 4px 12px; }
.t06-pages { display: flex; justify-content: center; gap: 30px; padding-top: 18px; }
/* le fichier téléchargé (navigateur) */
.t06-dlc { position: absolute; right: 22px; top: 70px; z-index: 28; background: #fff; border: 1px solid #DEE2E6;
  border-radius: 10px; box-shadow: 0 12px 28px rgba(0,0,0,.22); display: flex; align-items: center; gap: 14px;
  padding: 12px 20px 12px 14px; font-size: 18px; color: #212529; }
.t06-dlc-i { width: 40px; height: 40px; border-radius: 50%; background: #E7F1F7; color: #185FA5; display: inline-flex;
  align-items: center; justify-content: center; }
.t06-dlc-i svg { width: 22px; height: 22px; }
.t06-dlc-n { font-weight: 600; }
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
/* le menu de regroupement d'un en-tête de ligne du pivot : position « bottom-end »
   (pivot_header.xml:5), bord droit calé sur celui de la cellule « octobre 2026 »
   (x = 420 px dans la fenêtre), ouvert vers la gauche, par-dessus la barre des applications */
.t06-pvm { position: absolute; left: 90px; top: 486px; width: 330px; z-index: 26; background: #fff; padding: 6px 0;
  border: 1px solid #DEE2E6; border-radius: 6px; box-shadow: 0 12px 28px rgba(0,0,0,.22); }
.t06-pvm-i { height: 42px; display: flex; align-items: center; padding: 0 18px 0 40px; font-size: 18px; color: #212529; position: relative; }
.t06-pvm-d { justify-content: space-between; }
.t06-pvm-d span { color: #495057; font-size: 15px; }
.t06-pvm-i.survol { background: #E9ECEF; }
.t06-pvm-sep { height: 1px; background: #DEE2E6; margin: 6px 0; }
.t06-pvm-c { justify-content: space-between; color: #495057; padding-left: 18px; }
"""

TUTORIEL = {
    'slug': 't06-registre',
    'profil': 't06_registre',
    'numero': 6,
    'titre': "Fiche de police, registre et statistiques d'hébergement : tout part du check-in",
    'fonction': 'Fiche de police et statistiques',
    'personnage': (NOM, ROLE),
    'accroche': {
        'kicker': 'Fiche de police et statistiques',
        'question': 'Un contrôle ce soir : votre registre est-il *à* *jour* ?',
        'douleurs': [('bouclier', 'Enregistrer chaque client : une obligation de police'),
                     ('fiche', 'Nom, naissance, nationalité, pièce : les champs usuels à relever'),
                     ('graphe', 'Statistiques MINTOUL exigées, sous peine d\'amende'),
                     ('interrogation', 'Le format de la fiche ? Aucun modèle trouvé en ligne'),
                     ('globe', 'En Côte d\'Ivoire, la fiche papier est déjà numérique')],
        'voix': "Un contrôle de police ce soir : votre registre est-il à jour ? Une fiche pour chaque client, c'est "
                "une obligation de police ; des statistiques pour le MINTOUL, sous peine d'amende.",
    },
    'revelation': {
        'promesse': "Au check-in, la fiche d'enregistrement (la fiche de police) se crée et se pré-remplit. La "
                    "réservation dit ce qui manque. "
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
        'b-complete': 'Six informations requises par la fiche : elle passe Complète toute seule.',
        'b-pdf': 'Une page par occupant : identité, pièce, domicile, séjour, deux signatures.',
        'b-orange': 'En orange, les fiches encore à compléter.',
        'b-stats': 'Une fiche, une arrivée ; ses nuits, les nuitées. Résident ou non : selon le pays de résidence, à défaut la nationalité.',
    },
    'reactions': {
        'r-ajour': 'Deux fiches sur deux : le registre du séjour est à jour.',
    },
    'etapes': [
        {'temps': 0, 'titre': 'Le check-in crée la fiche',
         'texte': 'Un clic sur Check-in : la fiche du client principal est créée, le bandeau dit ce qui manque.',
         'voix': "À quatorze heures, Estelle Ngono arrive avec un accompagnant. Mireille ouvre sa réservation et clique "
                 "sur check-inne : la fiche d'enregistrement d'Estelle est créée aussitôt, et un bandeau dit ce qui manque.",
         'gestes': [pause(0.3), classe('#t06-a1', ajouter=['survol']), clic('#t06-a1', fx=0.09, d=0.7), vue('t06-resa'),
                    anneau('#t06-st-fiches', d=1.0), clic('#t06-b-checkin', d=0.6),
                    classe('#t06-sb-1', retirer=['actif']), classe('#t06-sb-2', ajouter=['actif']),
                    curseur('#t06-sb-2', d=0.5),
                    cacher('#t06-resa-ga', d=0.2), montrer('#t06-resa-gb', d=0.3, y=0),
                    montrer('#t06-cireel', d=0.3, y=0), montrer('#t06-bandeau', d=0.4, y=-10),
                    defiler('#t06-resa-defil', 52, d=0.4, avec=True),
                    zoom('#t06-bandeau', s=1.6, d=0.8, fx=0.35), bulle('b-fiche', '#t06-bandeau', cote='bas', d=3.0),
                    pause(2.8), dezoom(d=0.6)]},
        {'temps': 1, 'titre': 'Le prénom et la date de naissance',
         'texte': "La fiche reprend le contact, nom complet compris ; « Il manque » dit le prénom et la date de naissance.",
         'voix': "Le lien ouvre les fiches du séjour. Tout vient du contact, le nom complet compris ; Il manque "
                 "signale le prénom. Mireille sépare elle-même : Ngono en nom, Estelle en prénom. Reste la date de "
                 "naissance : elle la saisit, enregistre, et la fiche passe Complète, toute seule.",
         'gestes': [clic('#t06-completer', d=0.6), vue('t06-fiches'), pause(0.3),
                    zoom('#t06-f0', s=1.25, d=0.8, fx=0.55), anneau('#t06-f0-nom', d=1.0),
                    anneau('#t06-f0-im', d=1.0),
                    clic('#t06-f0-nom', fx=0.4, d=0.6), classe('#t06-f0', ajouter=['t06-edit']),
                    classe('#t06-f-nouveau', ajouter=['masque']), classe('#t06-f-sbts', retirer=['masque'], avec=True),
                    animer('#t06-f-fil', {'x': 0}, {'x': 140}, d=0.2, avec=True),
                    saisir('t06-f0-nom', 'Ngono', d=0.5), curseur('#t06-f0-pre', d=0.3, avec=True),
                    saisir('t06-f0-pre', 'Estelle', d=0.5), texte('#t06-f0-im', MANQUE_ESTELLE[1]),
                    anneau('#t06-f0-im', d=1.0),
                    curseur('#t06-f0-dn', fx=0.3, d=0.4),
                    saisir('t06-f0-dn', '12/03/1991', d=0.8), texte('#t06-f0-im', MANQUE_ESTELLE[2]),
                    clic('#t06-f-save', d=0.7), classe('#t06-f0', retirer=['avert', 't06-edit'], ajouter=['t06-vert']),
                    etat('#t06-f0-et', 'Complète', 'vert'),
                    classe('#t06-f-sbts', ajouter=['masque']), classe('#t06-f-nouveau', retirer=['masque'], avec=True),
                    animer('#t06-f-fil', {'x': 140}, {'x': 0}, d=0.2, avec=True),
                    bulle('b-complete', '#t06-f0-dn', cote='bas', d=2.8), pause(2.4)]},
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
         'texte': 'Un seul PDF téléchargé, une page par occupant, avec les deux cadres de signature.',
         'voix': "Imprimer les fiches télécharge un seul PDF, que Mireille ouvre d'un clic : une page par occupant, "
                 "avec l'identité, la pièce d'identité, le domicile et le séjour, puis deux cadres de signature, l'un "
                 "pour le client, l'autre pour le cachet de l'établissement.",
         'gestes': [clic('#t06-imprimer', d=0.6), montrer('#t06-dlc', d=0.3, y=-10), anneau('#t06-dlc', d=0.9),
                    clic('#t06-dlc', fx=0.3, d=0.5), montrer('#t06-pdf', d=0.5, y=30), cacher('#t06-dlc', d=0.2, avec=True),
                    pause(0.5),
                    zoom('#t06-p1-id', s=1.45, d=0.8, fx=0.9, fy=0.25), bulle('b-pdf', '#t06-p1-id', cote='droite', d=2.8),
                    pause(2.6), zoom('#t06-p1-sig', s=1.5, d=0.7, fx=0.5), anneau('#t06-p1-sig', d=1.4),
                    pause(0.6), dezoom(d=0.6), anneau('#t06-p2', d=1.0)]},
        {'temps': 2, 'titre': 'Le registre des clients',
         'texte': "Toutes les fiches, jour par jour : l'état à présenter en cas de contrôle.",
         'voix': "Le soir, Mireille ouvre le registre des clients : toutes les fiches d'enregistrement, jour après "
                 "jour. Les fiches incomplètes ressortent en orange, comme celle de Claire Durand. C'est l'état à "
                 "présenter en cas de contrôle.",
         'gestes': [cacher('#t06-pdf', d=0.3), clic(MENU_RECEPTION, d=0.6), montrer('#t06-dd', d=0.25, y=-8),
                    classe('#t06-dd-reg', ajouter=['survol']), clic('#t06-dd-reg', d=0.5), cacher('#t06-dd', d=0.15),
                    vue('t06-registre'), pause(0.4), clic('#t06-rg-g0', fx=0.1, d=0.6), cacher('#t06-rg-a', d=0.15),
                    montrer('#t06-rg-b', d=0.3, y=0, avec=True), pause(0.4), anneau('#t06-rg-claire', d=1.3),
                    anneau('#t06-rg-martin', d=1.2), bulle('b-orange', '#t06-rg-martin', cote='bas', d=3.0), pause(1.6),
                    anneau('#t06-rg-estelle', d=1.0)]},
        {'temps': 3, 'titre': "Les statistiques d'hébergement",
         'texte': 'Côté direction : arrivées et nuitées, résidents et non-résidents, par mois et par nationalité.',
         'voix': "En cours de mois, Danielle, la directrice, ouvre les statistiques d'hébergement : arrivées et nuitées, "
                 "résidents et non-résidents, tirées des mêmes fiches. Un clic sur le mois, puis Nationalité : le "
                 "détail par pays.",
         'gestes': [montrer('#t06-nav-dir', d=0.5, y=0), classe('#tu-perso', ajouter=['t06-pd'], avec=True),
                    texte('#tu-perso .av', DIRECTRICE[0], avec=True),
                    animer('#tu-perso', {'scale': 0.88}, {'scale': 1}, d=0.35, avec=True),
                    pause(0.6), anneau('#t06-pv-a tr.tot', d=1.2),
                    clic('#t06-pv-a-oct th', fx=0.3, d=0.6), montrer('#t06-pvm', d=0.25, y=-6),
                    classe('#t06-pvm-nat', ajouter=['survol']), clic('#t06-pvm-nat', d=0.5), cacher('#t06-pvm', d=0.15),
                    cacher('#t06-pv-a', d=0.15), montrer('#t06-pv-b', d=0.3, y=0, avec=True),
                    zoom('#t06-pv-b', s=1.3, d=0.8, fx=0.78, fy=0.75), anneau('#t06-pv-b-fra', d=1.2),
                    bulle('b-stats', '#t06-pv-b-fra', cote='droite', d=4.0), pause(3.6), dezoom(d=0.6)]},
    ],
    'resultats': {
        'titre': 'Un registre qui suit chaque séjour',
        'cartes': [
            {'valeur': '1', 'compter': 1, 'unite': 'clic', 'icone': 'fiche',
             'texte': 'au check-in : la fiche du client principal est créée et pré-remplie depuis son contact'},
            {'valeur': '6', 'compter': 6, 'unite': 'informations', 'icone': 'coche',
             'texte': 'requises par la fiche, suivies par « Il manque » : elle passe Complète toute seule'},
            {'valeur': '4', 'compter': 4, 'unite': 'regroupements', 'icone': 'graphe',
             'texte': "des statistiques : mois d'arrivée, nationalité, motif, hôtel, tirés des mêmes fiches"},
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
    'vignette': {'etape': 4, 'apres': 2.9},
}
