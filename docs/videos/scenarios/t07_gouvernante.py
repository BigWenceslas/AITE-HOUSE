# -*- coding: utf-8 -*-
"""Tutoriel 7 — Gouvernante : chaque chambre dit où elle en est.

La gouvernante (Josiane Fouda, demo.POSTES) suit l'état de chaque chambre sur
le tableau des chambres et répartit les chambres du jour entre ses
équipières, qui travaillent depuis « Ma journée » sur leur téléphone. Elle
passe la checklist de huit points de la tâche d'inspection, créée à la main
(écart 4 : la voix le dit en une demi-phrase, le geste n'est pas montré). Elle signale
une panne qui retire une chambre libre de la vente, puis passe elle-même la
demande à « Réparé » : la chambre revient en vente, à nettoyer.

Profil rejoué, et dit à l'écran. Josiane a le profil Réception, qui implique
Gouvernante (aite_hotel_management/security/hotel_security.xml:11-24). Le menu
« Répartir les chambres du jour » et son assistant sont réservés à ce profil
(aite_housekeeping/views/menus.xml:9-12 ; security/ir.model.access.csv:9), de
même que les boutons « Conforme » / « À refaire » (views/hotel_room_views.xml
:60-71). La pastille du personnage l'affiche (« Gouvernante (profil
Réception) ») et la légende de l'étape 2 le rappelle (écart 2). Menus de la
barre : ceux du profil Réception, relevés sur ref_muk/306-reception-
reservations.png (comme scenarios/c1_reception.py:30-31). Applications :
ecrans.APPS_PROFIL['gouvernante'], identiques à celles du profil Réception.
Le profil Réception ne crée pas de chambre : pas de bouton « Nouveau » sur
le tableau (aite_hotel_management/security/ir.model.access.csv:10-11 ;
ref_muk/300-gouv-tableau.png).

Les équipières viennent de demo.EQUIPIERES, la source unique des données de
la série (comme scenarios/c2_gouvernante.py) : aucun prénom n'est codé ici.
Elles n'ont que le profil Gouvernante. Leurs prénoms (« Clarisse »,
« Sidonie ») sont fictifs, absents des seeds et des jeux de recette
(E1, E2 = sorted(demo.EQUIPIERES)).

Comment l'équipière arrive sur « Ma journée ». Avec le seul profil
Gouvernante, l'icône de l'application Hôtel ouvre le tableau de bord Front
Desk, qui échoue (écart 11) : la vidéo ne montre donc ni cette icône ni le
menu de l'application sur le téléphone. Elle rejoue la configuration
standard d'Odoo qui l'évite : « Ma journée » posée comme « Action de la page
d'accueil » sur la fiche de l'équipière (res.users.action_id, « If
specified, this action will be opened at log on for this user » :
odoo18/odoo/addons/base/models/res_users.py:384-385 ; libellé français
odoo/addons/base/i18n/fr.po:30391-30392 ; champ du groupe « Personnalisation
des menus », visible en mode développeur : base/views/res_users_views.xml
:239-242 ; ouverture : web/models/ir_http.py:125 et web/static/src/webclient/
actions/action_service.js:571-572). Ce n'est pas un réglage du module : la
légende de l'étape 3 le dit (« sa page d'accueil »).

La journée rejouée : le jeudi 15/10/2026, le matin.
- L'hôtel de la série compte 20 chambres vendables, la liste commune à
  tous les tutoriels (fiche d'harmonisation de la série ; le module
  aite_demo_data en déclare 16, aite_demo_data/data/10_hotel_structure.xml
  :68-160). Au rez-de-chaussée : 101-107 [STD], dont la 105 hors service
  (:92-98). Au 1er étage : 201-206 [CFT]. Au 2e étage : 301-304 [SJR]. Au
  3e étage : 401-403 [VIP]. Types : Standard, Confort, Suite Junior, Suite
  VIP.
- Les séjours du 15/10 viennent de scenarios/t02_planning.py:213-228
  (SEJOURS) et de demo.ARRIVEES. Brigitte Essomba est en 202 (13-16/10),
  Estelle Ngono en 204 (14-16/10) et Claire Durand en 401 : elle part le
  15/10 à 12:00 et elle est encore là le matin. Gaston Mbida est attendu en
  103 le 15/10 à 14:00. Martin Ebode (RES/2026/0209) paie 105 000 FCFA pour
  3 nuits, soit 35 000 FCFA la nuit, le tarif Standard (demo.ARRIVEES ;
  t02_planning.py:196) : il est placé en 104 [STD], comme au planning de t02
  (t02_planning.py:223 et :255) et au registre de t06. Toutes les autres
  chambres (101, 102, 106, 107, 201, 203, 205, 206, 301-304, 402, 403) sont
  libres et propres ce jour-là ; elles n'entrent pas dans la répartition.
- Les tâches du jour. Le ménage quotidien des chambres occupées est créé
  chaque matin : 104, 202, 204 et 401 (réglage « Ménage quotidien
  automatique », coché par défaut, aite_hotel_management/models/
  res_config_settings.py:58-61 et :125-130 ; hotel_reservation.py:490-492 ;
  hotel_housekeeping.py:151-170). S'y ajoute la recouche de la 103, remise
  « À nettoyer » le matin avant l'arrivée : le bouton « À nettoyer » crée une
  tâche « Recouche (départ) » pour une chambre non occupée (aite_housekeeping/
  models/hotel_room.py:173-185). Il y a donc 5 chambres à répartir.
- La répartition se fait à tour de rôle sur les tâches triées par étage puis
  par chambre (assign_wizard.py:30-48), les équipières étant triées par nom
  (res.users « name, login »). Vérifié sur la base MuK : name_search et le
  Many2many rendent l'ordre alphabétique. Résultat, E1 et E2 dans l'ordre
  alphabétique : 103 E1, 104 E2, 202 E1, 204 E2, 401 E1.
- « Inspection après recouche » est cochée (res_config_settings.py:62-65 et
  :131-136). E2 a commencé la 104 quand E1 termine la 103.
- « Équipières présentes » propose tous les utilisateurs du groupe
  Gouvernante, y compris ceux dont le profil l'implique (assign_wizard.py:21-24 ;
  écart 3). Rejoué dans l'ordre alphabétique : les deux équipières, Danielle
  Eyenga, la directrice, qui est le compte administrateur renommé, placé par
  le socle dans le profil Responsable (hotel_security.xml:26-31), Josiane
  Fouda et Mireille Ateba.

Sources des libellés et des règles (relevés mot pour mot) :

- Tableau des chambres : addons/aite_housekeeping/views/hotel_room_views.xml
  :5-103. Fond rouge d'une chambre hors service :26. Badge clé et nombre,
  infobulle « Pannes ouvertes » :28-33. Phrase d'état :35. « type · étage »
  :36-39. Client (fa-user) :40-42. « Arrivée prévue » en couleur info :43-45.
  Équipière (fa-female, « Affectée à ») :46-48. Boutons « Commencer » :50-54,
  « Terminé » :55-59, « Conforme » :60-65, « À refaire » :66-71 (groupe
  Réception), « À nettoyer » :72-76, clé « Signaler un problème (panne,
  dégât) » :77-81. Titre de l'action :91.
  Les phrases d'état : aite_housekeeping/models/hotel_room.py:69-85
  (_hint_for : « À nettoyer », « Recouche à faire », « Nettoyage en cours »,
  « À inspecter par la gouvernante », « Propre — client présent », « Propre
  — prête pour l'arrivée », « Propre — libre », « Hors service — ne pas
  vendre »). « Arrivée prévue 14h00 » au format %Hh%M :59-61. Équipière de
  la tâche ouverte du jour :50-56 (_compute_today, :46-67).
  Colonnes : libellés de hk_state, aite_hotel_management/models/hotel_room.py
  :263-271. Elles sont rejouées dans l'ordre où Odoo 18 les affiche
  (écart 1). Une colonne vide n'est pas affichée : le regroupement par
  sélection n'a pas de group_expand, et ref_muk/300 ne montre que deux
  colonnes. Dans une colonne, les cartes suivent le numéro (default_order
  … name, :13). Seules les premières cartes d'une colonne tiennent à l'écran
  (le tableau défile), et le compteur donne le total.
- Menu Gouvernante : aite_housekeeping/views/menus.xml:3-18 (Tableau des
  chambres 5, Ma journée 8, Répartir les chambres du jour 12, Pannes &
  réparations 30, Objets trouvés 40) et aite_hotel_management/views/
  hotel_menus.xml:83-92 (Tâches de ménage 10).
- Répartir : aite_housekeeping/wizard/assign_wizard_views.xml:7-20 (texte,
  champs, « Répartir » icône fa-random, « Annuler ») ; wizard/
  assign_wizard.py:15-28 (Hôtel, Jour, Équipières présentes, Redistribuer…,
  Chambres à répartir) et :59-68 (notification « Chambres réparties »,
  « %(n)d chambre(s) réparties entre %(u)d équipière(s). »). Bouton
  d'agrandissement et lien interne du champ Hôtel : ref_muk/037.
- Ma journée : aite_housekeeping/views/housekeeping_task_views.xml:5-70.
  Liseré rouge d'une tâche urgente :18. « Chambre <chambre> » et pastille
  d'état :20-24. « Quoi faire » :26. Client :27-29. Consigne en rouge :30-32.
  « Je commence » :34-38, « C'est fait » :39-43, « Passer la checklist »
  :44-48. Titre :58. Domaine :62 ; filtre « Mes chambres » (les tâches
  affectées à l'utilisatrice et celles de personne) :63 et :147-148. État
  vide « Rien à faire pour l'instant » :64-69. Libellés des tâches et
  « URGENT — » : aite_housekeeping/models/housekeeping_task.py:82-93. Ordre
  « date desc, priority desc, id desc » : aite_hotel_management/models/
  hotel_housekeeping.py:19. États À faire / En cours / Terminé :61-69.
  « Inspection après recouche » : la recouche passe la chambre « à
  inspecter » (:101-115).
- Téléphone : barre MuK, bulle, horloge des activités et avatar relevés sur
  ref_muk/400-mobile-ma-journee.png. Il s'ouvre directement sur Ma journée,
  la page d'accueil de l'équipière (voir plus haut).
- Tâche d'inspection : type Inspection (hotel_housekeeping.py:38-46), créée
  depuis Tâches de ménage (hotel_menus.xml:83-92 ;
  hotel_housekeeping_views.xml:75-125). Le geste n'est pas montré ; la voix
  de l'étape 4 dit « Josiane a créé la tâche d'inspection » (écart 4).
- Inspection : housekeeping_task_views.xml:73-108 (titre « Chambre … »,
  « contrôle 0 / 8 », consigne, colonnes « OK » / « Point de contrôle » /
  « Remarque », indication « Remarque si non conforme », boutons « Tout
  cocher », « Valider l'inspection », « Fermer »). Titre de la fenêtre
  « Inspection — chambre %s » : housekeeping_task.py:155-168. Compteur
  :59-65. Une case non cochée fait repasser la chambre « À nettoyer » et crée
  une recouche urgente avec la consigne « Inspection refusée. À reprendre :
  <point> — <remarque> », confiée à l'équipière de la dernière tâche de
  ménage affectée (:121-153). Les huit points :
  aite_housekeeping/data/housekeeping_data.xml:3-12 (noupdate).
- Signaler un problème : hotel_room.py:149-159 (titre « Signaler un problème
  — chambre %s ») ; wizard/report_issue_wizard.py:10-23 (Chambre, Quel est le
  problème ?, Précisions, La chambre ne peut pas être vendue en l'état,
  Urgence Normal / Important par défaut / Urgent / Très urgent, Photo) ;
  :29-30 (« Chambre 102 — Climatiseur en panne ») ; :47-55 (notification
  « Problème signalé »). wizard/report_issue_wizard_views.xml:8-20
  (indications, « Envoyer à la maintenance » fa-paper-plane, « Annuler »).
  Hors service si la chambre n'est pas occupée :
  aite_housekeeping/models/maintenance_request.py:39-58 (recette P05, P07).
  Plus disponible à la vente : aite_hotel_management/models/hotel_room.py
  :431-442. Check-in refusé : aite_hotel_management/models/
  hotel_reservation.py:379-383.
- Pannes & réparations : aite_housekeeping/views/maintenance_views.xml:29-55
  (chambre et case « chambre invendable » sur la carte, facette « À faire »,
  titre). Carte, fiche et étapes de l'app Maintenance : odoo18/addons/
  maintenance/views/maintenance_views.xml:76-151 (fiche) et :155-190
  (carte) ; data/maintenance_data.xml:6-26 (étapes, Réparé et Rebut
  repliées) ; i18n/fr.po (Nouvelle demande, En cours, Réparé, Rebut, Demandé
  par :, Demande, Équipement, Date de la demande, Date de clôture, Type de
  maintenance, Corrective, Préventive, Équipe, Maintenance interne,
  Responsable, Date planifiée, Durée, heures, Priorité, Annuler, Notes,
  Instructions, Notes internes, À faire). « Chambre invendable pendant
  l'intervention » : maintenance_request.py:19-22 et maintenance_views.xml:9-12.
  Remise en vente, « À nettoyer » et tâche « Remise en service après
  intervention : … » : maintenance_request.py:59-69 (recette P06). Date de
  clôture posée au passage à une étape terminée : odoo18/addons/
  maintenance/models/maintenance.py:336-339. « ? » d'aide : Chambre
  (maintenance_request.py:13-16), Chambre invendable…, Date de clôture,
  Date planifiée, Durée (odoo18 maintenance.py:258, :264, :267). Discussion :
  message de création (sous-type « Demande créée », description « Demande de
  maintenance créée » : maintenance.py:227-228, data/mail_message_subtype_
  data.xml:5-11, i18n/fr.po:903-904) et suivi d'étape (sous-type « Statut
  modifié », :12-17, fr.po:1447-1448 ; « Nouvelle demande → Réparé (Étape) »,
  mail/static/src/core/web/message_patch.xml:5-21, fr.po:1418-1419) ; date
  « Aujourd'hui à 09:40 » (mail/static/src/core/common/message_model.js
  :241-247, mail/i18n/fr.po:10407-10408). Le suivi des champs à la création
  est écarté (mail/models/mail_thread.py:333-334).
- Notifications en haut à droite : odoo18/addons/web/static/src/core/
  notifications/notification.scss:5-13.

Douleurs de l'accroche : docs/etude_comparative/build_etude.py:132-133
(statut des chambres en temps réel, présent chez 10 leaders sur 10),
:134-135 (affectation des tâches, feuilles de travail, mobile), :138-139
(inspections, checklists), :106-107 (chambre hors service sans lien avec la
maintenance), :144-145 (pas de flux réception ↔ étages ↔ maintenance), :443
(« des registres saisis sur mobile à la place du papier »).

Promesse : « Chaque équipière retrouve ses chambres dans Ma journée » (filtre
« Mes chambres », housekeeping_task_views.xml:63, :147-148). « Une panne
bloquante retire une chambre libre de la vente » : une chambre occupée n'est
pas bloquée (maintenance_request.py:51-54, recette P07).

Résultats : 8 phrases d'état (hotel_room.py:69-85). 8 points de contrôle
livrés en noupdate, modifiables dans Configuration → Points de contrôle
(inspection) (housekeeping_data.xml:3-12, menus.xml:23-25,
housekeeping_task_views.xml:155-176). 3 boutons dans Ma journée : Je
commence, C'est fait, Passer la checklist (housekeeping_task_views.xml:33-48).

Captures de référence (modèle visuel, jamais incrustées) : ref_muk/034 à 039,
047, 300-gouv-tableau, 400-mobile-ma-journee, 401-mobile-tableau.

Ce que la vidéo montre, et ce qu'elle évite :
- Odoo 18 ne rafraîchit pas un kanban tout seul. Le tableau ne change qu'au
  rechargement (menu Gouvernante → Tableau des chambres) ou après un bouton
  de ses cartes (la clé, dont la fenêtre se referme en rechargeant la vue).
  L'assistant Répartir, ouvert par le menu, ne recharge pas le tableau
  (odoo18/addons/web/static/src/webclient/actions/action_service.js
  :1382-1394) : la notification d'abord, puis le tableau rechargé par le
  menu. Chaque changement d'écran passe par le menu Gouvernante, sauf
  l'ouverture d'une fiche ou d'une fenêtre.
- Sur le téléphone, l'équipière arrive sur Ma journée, sa page d'accueil.
  L'application Hôtel n'est pas montrée : avec le seul profil Gouvernante,
  elle échoue (écart 11).
- Après « C'est fait », la tâche est « Terminé » et sa carte n'a plus de
  bouton (housekeeping_task_views.xml:34-48). Elle quitte Ma journée au
  rechargement (domaine :62).
- La tâche d'inspection a été créée à la main (écart 4), sans « Assignée à » :
  elle paraît dans Ma journée de Josiane (filtre « Mes chambres ») et « Je
  commence » la lui affecte (hotel_housekeeping.py:97-98).
- Le bouton « Conforme » est visible sur la carte « À inspecter » de la 103,
  comme dans Odoo pour le profil Réception (écart 5) : il n'est ni montré du
  doigt ni cliqué.
- La remarque de la checklist n'est saisissable qu'une fois la ligne en
  édition : l'indication « Remarque si non conforme » apparaît alors.
- On ne clique ni « Tout cocher » (il ferme la fenêtre, écart 6) ni
  « Conforme » (écart 5).
- Après la validation, Ma journée de Josiane est vide : la recouche urgente
  est affectée à E1. Son état vide s'affiche, sans compteur.
- C'est Josiane, auteure de la demande, qui la passe à « Réparé » : la voix
  et la légende le disent (écart 9).
- Un seul réglage de couleur : le texte gris « Standard · Rez-de-chaussée »
  d'une carte hors service est foncé (#565D64) pour passer le contrôle de
  contraste AA. Dans Odoo, text-muted sur bg-danger-subtle donne 3,6:1
  (écart 10).

Écarts relevés, rejoués tels quels (voir le rapport) :
1. Les colonnes du tableau s'affichent dans l'ordre À nettoyer · À inspecter ·
   Nettoyage en cours · Propre. Odoo 18 trie la sélection par clé : « hk_state
   desc » donne to_clean, inspect, cleaning, clean. Le commentaire de la vue
   dit le contraire (hotel_room_views.xml:10-12). Vérifié par read_group sur
   la base de démonstration MuK : « desc » rend cleaning avant clean.
2. Le profil nommé « Gouvernante » ne voit ni « Répartir les chambres du
   jour » ni « Conforme » / « À refaire » : il faut le profil Réception
   (menus.xml:9-12, hotel_room_views.xml:60-71). La gouvernante du jeu de
   démonstration n'a que le profil Gouvernante. La recette (P02) attend
   pourtant ce menu sous le profil Gouvernante.
3. « Équipières présentes » propose aussi la directrice, la réception et la
   gouvernante (domaine sur un groupe impliqué), assign_wizard.py:21-24.
4. Aucune tâche d'inspection n'est créée quand une chambre passe « à
   inspecter » (aite_hotel_management/models/hotel_housekeeping.py:101-115).
   La checklist n'est atteignable qu'après avoir créé à la main une tâche
   « Inspection » : la voix le dit, le geste n'est pas montré.
5. « Conforme » clôt la tâche d'inspection ouverte par action_done alors que
   ses huit cases sont décochées. Une recouche urgente « Inspection refusée »
   est créée, puis la chambre est forcée « Propre » (hotel_room.py:126-135,
   housekeeping_task.py:121-153).
6. « Tout cocher » renvoie True : Odoo ferme la fenêtre d'inspection
   (housekeeping_task.py:170-172).
7. L'urgence de l'assistant (Normal / Important / Urgent / Très urgent) est
   recopiée telle quelle dans la priorité Maintenance (Très basse / Basse /
   Normal / Haute) : « Important » devient « Basse » (report_issue_wizard.py:
   19-22, 33 ; odoo18 maintenance.py:256).
8. Avec deux demandes bloquantes sur une chambre, toutes deux passées à
   « Réparé », la chambre reste hors service (maintenance_request.py:46-63).
9. Un technicien sans profil hôtel ne peut pas passer la demande à
   « Réparé » : la chambre est écrite sans sudo (maintenance_request.py:33-69).
   Il ne voit pas non plus une demande dont il n'est ni l'auteur, ni le
   suiveur, ni le responsable : c'est la règle standard de Maintenance, et la
   demande créée par l'assistant n'a pas de responsable (odoo18/addons/
   maintenance/security/maintenance.xml:15-20).
10. Contraste du texte gris sur une carte hors service : 3,6:1 (sous le seuil
   AA de 4,5:1).
11. Une équipière qui n'a que le profil Gouvernante et qui ouvre
   l'application Hôtel arrive sur le tableau de bord Front Desk
   (hotel_menus.xml:9-14). Celui-ci appelle get_kpis dès le chargement
   (static/src/js/views/hotel_dashboard_view.js:76-90), qui lit
   aite.hotel.folio.line sans sudo (hotel_dashboard.py:173-181). Ce modèle
   est réservé à la Réception (ir.model.access.csv:23) : erreur d'accès.
12. Un même geste porte trois libellés selon l'écran : « Commencer /
   Terminé » (tableau), « Je commence / C'est fait » (Ma journée),
   « Démarrer / Terminer » (Tâches de ménage). C'est contraire à la règle 4
   de CLAUDE.md.
13. « Recouche complète (départ) » s'affiche pour une chambre remise à
   nettoyer avant une arrivée : « À nettoyer » crée une tâche de type
   Recouche (départ) pour toute chambre non occupée (hotel_room.py:173-185).
"""

import demo
from ecrans import (APPS_PROFIL, ICONES, avec_chatter, cp_fiche, e, entree, fenetre_muk, icone, interrupteur,
                    navigateur, onglets, recherche, statusbar, toast, vue_fiche, vue_libre)
from marketing import bulle, dezoom, reaction, zoom
from moteur import (anneau, cacher, clic, classe, curseur, etat, fermer, montrer, notifier, ouvrir, pause, saisir,
                    texte, vue)

NOM, _ROLE = demo.POSTES['gouvernante']
ROLE = 'Gouvernante (profil Réception)'
# Les équipières de demo.py, dans l'ordre alphabétique où Odoo les trie (res.users « name, login »).
E1, E2 = sorted(demo.EQUIPIERES)
JOUR = '15/10/2026'
GASTON = 'Gaston Mbida'             # arrivée attendue en 103 le 15/10 à 14:00 (t02_planning.py:224, :251)
MENUS = ['Front Desk', 'Réservations', 'Espaces & Prestations', 'Notes de chambre en attente', 'Facturation',
         'Fidélité', 'Gouvernante']
MENU_GOUV = '#t07-app .o-haut .menu.actif'

# ------------------------------------------------------------ icônes --
# Dessinées ici (fa-female, fa-exclamation-circle, fa-random, fa-paper-plane…) :
# ecrans.ICONES n'a pas ces glyphes, on ne le modifie pas.
FEMME = ('<svg viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="4.4" r="2.9"/>'
         '<path d="M8.7 8.3h6.6l3.1 8.4h-3.2V22h-2.3v-5.3h-1.8V22H8.8v-5.3H5.6z"/></svg>')
EXCLAM = ('<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" fill="currentColor"/>'
          '<path d="M10.9 6.2h2.2l-.3 8h-1.6zM10.8 15.9h2.4v2.3h-2.4z" fill="#fff"/></svg>')
HASARD = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.3" stroke-linecap="round" '
          'stroke-linejoin="round"><path d="M3 7h3.5c4.5 0 6.5 10 11 10H21M3 17h3.5c1.6 0 2.8-1.4 3.8-3.1M13.7 '
          '10.1c1-1.7 2.2-3.1 3.8-3.1H21M18.4 4.4L21 7l-2.6 2.6M18.4 14.4L21 17l-2.6 2.6"/></svg>')
AVION = '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M2.4 11.1L21.6 3.2l-5.4 17.6-4.7-6.3z"/></svg>'
KANBAN = ('<svg viewBox="0 0 24 24" fill="currentColor"><rect x="3" y="4" width="7.5" height="16" rx="1"/>'
          '<rect x="12.5" y="4" width="8.5" height="7.5" rx="1"/></svg>')
CALENDRIER = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="5" '
              'width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/></svg>')
ETOILE_VIDE = ('<span class="ico t07-et0"><svg viewBox="0 0 24 24" fill="none" stroke="#ADB5BD" stroke-width="1.8">'
               '<path d="M12 2.5l2.9 6.3 6.9.7-5.2 4.6 1.5 6.8L12 17.4l-6.1 3.5 1.5-6.8L2.2 9.5l6.9-.7z"/></svg></span>')
PHOTO = ('<svg viewBox="0 0 24 24" fill="#ADB5BD"><path d="M4 5h16a1 1 0 011 1v12a1 1 0 01-1 1H4a1 1 0 01-1-1V6a1 1 0 '
         '011-1zm1 12h14l-4.5-6-3.5 4.5-2.5-3z"/><circle cx="8.5" cy="9" r="1.7"/></svg>')
SOURIRE = ('<svg viewBox="0 0 120 120"><circle cx="60" cy="64" r="44" fill="#E7DCE6"/><path d="M38 22h36l14 14v62H38z" '
           'fill="#fff" stroke="#C9CED3" stroke-width="2"/><path d="M74 22v14h14" fill="none" stroke="#C9CED3" '
           'stroke-width="2"/><circle cx="52" cy="54" r="3" fill="#6C757D"/><circle cx="72" cy="54" r="3" '
           'fill="#6C757D"/><path d="M50 66q12 9 24 0" fill="none" stroke="#6C757D" stroke-width="2.6" '
           'stroke-linecap="round"/></svg>')
# fa-expand de l'en-tête d'une fenêtre, lien interne d'un champ
AGRANDIR = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" '
            'stroke-linejoin="round"><path d="M14 4h6v6M20 4l-7 7M10 20H4v-6M4 20l7-7"/></svg>')
LIEN_INTERNE = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
                'stroke-linejoin="round"><path d="M19 13v6a1 1 0 01-1 1H5a1 1 0 01-1-1V6a1 1 0 011-1h6M15 3h6v6'
                'M10 14L21 3"/></svg>')


def ico(svg, classe_='ico'):
    return '<span class="%s">%s</span>' % (classe_, svg)


def etoiles(pleines, total=3):
    return '<span class="etoiles">%s%s</span>' % (icone('etoile') * pleines, ETOILE_VIDE * (total - pleines))


def vues_bt(*svgs):
    """Le sélecteur de vues du panneau de contrôle (la première est active)."""
    return '<span class="t07-vues">%s</span>' % ''.join(
        '<i class="%s">%s</i>' % ('on' if i == 0 else '', s) for i, s in enumerate(svgs))


def modale(ident, titre, corps, pied, haut, largeur):
    """Une fenêtre d'Odoo 18 (même gabarit qu'ecrans.assistant), avec le bouton
    d'agrandissement de l'en-tête (ref_muk/037) et un pied composé ici pour les
    icônes de boutons qu'ecrans n'a pas."""
    return ('<div class="voile masque" id="%s-voile" data-layout-allow-overlap data-layout-allow-occlusion></div>'
            '<div class="modale masque" id="%s" style="top:%dpx;width:%dpx;margin-left:-%dpx" '
            'data-layout-allow-overlap data-layout-allow-occlusion>'
            '<div class="m-tete"><span>%s</span><span class="t07-m-bts"><span class="m-x t07-agr">%s</span>'
            '<span class="m-x">%s</span></span></div>'
            '<div class="m-corps">%s</div><div class="m-pied">%s</div></div>'
            % (ident, ident, haut, largeur, largeur // 2, e(titre), AGRANDIR, ICONES['x'], corps, pied))


def bt(ident, libelle, style='gris', svg=None):
    return '<span class="bt %s"%s>%s%s</span>' % (style, ' id="%s"' % ident if ident else '',
                                                   ico(svg) if svg else '', e(libelle))


def ligne(libelle, valeur_html, aide=False, ident=None, lecture=False):
    """Une ligne de formulaire d'assistant ; ``aide`` : le « ? » d'un champ qui porte une aide."""
    return ('<div class="m-ch"%s><span class="l%s">%s%s</span><span class="v">%s</span></div>'
            % (' id="%s"' % ident if ident else '', ' t07-lecture' if lecture else '', e(libelle),
               '<sup class="t07-aide">?</sup>' if aide else '', valeur_html))


# ------------------------------------------------- Tableau des chambres --
TYPES = {'STD': 'Standard', 'CFT': 'Confort', 'SJR': 'Suite Junior', 'VIP': 'Suite VIP'}
# Les 20 chambres de la série (101-107 au rez-de-chaussée, 2xx au 1er, 3xx au 2e, 4xx au 3e étage).
CHAMBRES = ([('%d' % n, 'STD', 'Rez-de-chaussée') for n in range(101, 108)]
            + [('%d' % n, 'CFT', '1er étage') for n in range(201, 207)]
            + [('%d' % n, 'SJR', '2e étage') for n in range(301, 305)]
            + [('%d' % n, 'VIP', '3e étage') for n in range(401, 404)])
assert len(CHAMBRES) == 20
# Les clients présents le 15/10 (t02_planning.py SEJOURS, demo.ARRIVEES ; Martin Ebode en Standard).
CLIENTS = {'104': 'Martin Ebode', '202': 'Brigitte Essomba', '204': demo.CLIENT, '401': 'Claire Durand'}
# La répartition : tâches triées étage puis chambre, équipières par nom, tour de rôle.
REPARTITION = {'103': E1, '104': E2, '202': E1, '204': E2, '401': E1}
ARR_103 = 'Arrivée prévue 14h00'
COLONNES = ['À nettoyer', 'À inspecter', 'Nettoyage en cours', 'Propre']   # ordre affiché par Odoo 18 (écart 1)
VISIBLES = 5            # cartes rendues par colonne : la suite est sous le bas de l'écran (le tableau défile)


def carte_ch(k, num, hint, type_etage, client=None, arrivee=None, equipiere=None, boutons=(), panne=0, hs=False):
    """Une carte du tableau, dans l'ordre de la vue kanban (hotel_room_views.xml:23-84)."""
    ident = 't07-b%d-%s' % (k, num)
    badge = '<span class="badge-panne">%s%d</span>' % (icone('cle'), panne) if panne else ''
    corps = '<div class="hint" id="%s-h">%s</div><div class="mini">%s</div>' % (ident, e(hint), e(type_etage))
    if client:
        corps += '<div class="lg">%s%s</div>' % (icone('personne'), e(client))
    if arrivee:
        corps += '<div class="lg t07-arr" id="%s-arr">%s%s</div>' % (ident, icone('horloge'), e(arrivee))
    if equipiere:
        corps += '<div class="lg" id="%s-eq">%s%s</div>' % (ident, ico(FEMME), e(equipiere))
    bts = ''.join(b(ident) for b in boutons)
    bts += '<span class="bt rouge-contour t07-cle" id="%s-cle">%s</span>' % (ident, icone('cle'))
    return ('<div class="k-carte%s" id="%s"><div class="num-ch"><span>%s</span>%s</div>%s<div class="bts" id="%s-bts">%s'
            '</div></div>' % (' hors-service' if hs else '', ident, e(num), badge, corps, ident, bts))


def COMMENCER(i):
    return bt(i + '-go', 'Commencer', 'primaire', ICONES['play'])


def TERMINE(i):
    return bt(i + '-fin', 'Terminé', 'vert', ICONES['coche'])


def CONFORME(i):
    return bt(i + '-ok', 'Conforme', 'vert', ICONES['coche'])


def A_REFAIRE(i):
    return bt(i + '-ko', 'À refaire', 'rouge-contour')


def A_NETTOYER(i):
    return bt(i + '-sale', 'À nettoyer', 'blanc')


def chambre(k, num, code, etage, etat_):
    """La colonne et la carte d'une chambre à l'instant ``k`` ; ``etat_`` dit où
    en sont les chambres qui changent dans la journée."""
    te = '%s · %s' % (TYPES[code], etage)
    eq = REPARTITION.get(num) if etat_.get('reparti') else None
    s = etat_.get(num)
    if num == '103':
        if s == 'inspecter':
            return 'À inspecter', carte_ch(k, num, 'À inspecter par la gouvernante', te, GASTON, ARR_103,
                                           boutons=[CONFORME, A_REFAIRE])
        if s == 'a_refaire':
            return 'À nettoyer', carte_ch(k, num, 'Recouche à faire', te, GASTON, ARR_103, E1, [COMMENCER])
        return 'À nettoyer', carte_ch(k, num, 'Recouche à faire', te, GASTON, ARR_103, eq, [COMMENCER])
    if s == 'en_cours':
        return 'Nettoyage en cours', carte_ch(k, num, 'Nettoyage en cours', te, CLIENTS.get(num), None,
                                              REPARTITION[num], [TERMINE])
    if s == 'hs':
        return 'Propre', carte_ch(k, num, 'Hors service — ne pas vendre', te, panne=1, hs=True)
    if s == 'a_nettoyer':
        return 'À nettoyer', carte_ch(k, num, 'À nettoyer', te, boutons=[COMMENCER])
    if num == '105':
        return 'Propre', carte_ch(k, num, 'Hors service — ne pas vendre', te, hs=True)
    if num in CLIENTS:
        return 'Propre', carte_ch(k, num, 'Propre — client présent', te, CLIENTS[num], None, eq, [A_NETTOYER])
    return 'Propre', carte_ch(k, num, 'Propre — libre', te, boutons=[A_NETTOYER])


def instant(k, etat_, initiale=False):
    """Le tableau à l'instant ``k`` : les colonnes non vides, dans l'ordre d'Odoo."""
    cols = {c: [] for c in COLONNES}
    for num, code, etage in CHAMBRES:
        col, html = chambre(k, num, code, etage, etat_)
        cols[col].append(html)
    pleines = [(c, cartes) for c, cartes in cols.items() if cartes]
    html = ''.join('<div class="k-col" id="t07-b%d-c%d"><div class="k-titre">%s <span>(%d)</span></div>%s</div>'
                   % (k, i, e(c), len(cartes), ''.join(cartes[:VISIBLES])) for i, (c, cartes) in enumerate(pleines, 1))
    largeur = 356 * len(pleines) + 20 * (len(pleines) - 1)
    tetes = '<div class="t07-tetes" id="t07-b%d-tetes" style="width:%dpx"></div>' % (k, largeur)
    return ('<div class="t07-instant%s" id="t07-b%d" data-layout-allow-overflow><div class="kanban t07-k">%s</div>%s'
            '</div>' % ('' if initiale else ' masque', k, html, tetes))


# Les instants du tableau : chaque rechargement (menu, bouton d'une carte) en
# affiche un nouveau, posé au même endroit.
B0 = instant(0, {'103': 'a_faire'}, initiale=True)
B1 = instant(1, {'reparti': True, '103': 'a_faire'})
B2 = instant(2, {'reparti': True, '103': 'inspecter', '104': 'en_cours'})
B3 = instant(3, {'reparti': True, '103': 'a_refaire', '104': 'en_cours'})
B4 = instant(4, {'reparti': True, '103': 'a_refaire', '104': 'en_cours', '102': 'hs'})
B5 = instant(5, {'reparti': True, '103': 'a_refaire', '104': 'en_cours', '102': 'a_nettoyer'})

CP_TABLEAU = ('<div class="cp"><span class="titre">Tableau des chambres</span>%s%s</div>'
              % (recherche(), vues_bt(KANBAN, ICONES['liste'])))
TABLEAU = vue_libre('t07-tableau', CP_TABLEAU + B0 + B1 + B2 + B3 + B4 + B5, initiale=True)

# ------------------------------------------------- menu « Gouvernante » --
ENTREES = [('tableau', 'Tableau des chambres'), ('journee', 'Ma journée'), ('taches', 'Tâches de ménage'),
           ('repartir', 'Répartir les chambres du jour'), ('pannes', 'Pannes & réparations'),
           ('objets', 'Objets trouvés')]
MENU = ('<div class="t07-menu masque" id="t07-menu" data-layout-allow-overlap data-layout-allow-occlusion>%s</div>'
        % ''.join('<div id="t07-menu-%s">%s</div>' % (i, e(lib)) for i, lib in ENTREES))


def naviguer(entree_, apres):
    """Gouvernante → entrée du menu, puis ce qui s'affiche (``apres`` : gestes)."""
    return [clic(MENU_GOUV, d=0.35, puis=0.05), montrer('#t07-menu', d=0.15, y=-6, puis=0.05),
            clic('#t07-menu-%s' % entree_, d=0.3, puis=0.05), cacher('#t07-menu', d=0.1)] + list(apres)


# ------------------------------------------- Répartir les chambres du jour --
# Tous les profils hôtel, dans l'ordre alphabétique (écart 3) ; les équipières portent t07-eq-e1 / t07-eq-e2.
PRESENTS = sorted([('e1', E1), ('e2', E2), ('danielle', demo.POSTES['direction'][0]), ('josiane', NOM),
                   ('mireille', demo.POSTES['reception'][0])], key=lambda x: x[1])
CASES = ''.join('<span class="case t07-case" id="t07-eq-%s"><i></i>%s</span>' % (i, e(n)) for i, n in PRESENTS)
REPARTIR = modale('t07-as-rep', 'Répartir les chambres du jour', (
    '<div class="m-aide" id="t07-rep-aide">Cochez les équipières présentes : les chambres à faire sont distribuées '
    'à tour de rôle, étage par étage.</div>'
    '<div class="m-grille un">%s%s%s%s%s</div>'
    % (ligne('Hôtel', '<span class="t07-m2o">%s<span class="t07-car">▾</span></span><span class="t07-li">%s</span>'
             % (e(demo.HOTEL), LIEN_INTERNE), ident='t07-l-hotel'),
       ligne('Jour', '<span class="t07-m2o">%s</span>' % JOUR),
       ligne('Équipières présentes', '<span class="t07-cases">%s</span>' % CASES, ident='t07-l-eq'),
       ligne('Redistribuer aussi les chambres déjà affectées', '<span class="case"><i></i></span>'),
       ligne('Chambres à répartir', '<b class="t07-n" id="t07-rep-n">5</b>', lecture=True))),
    bt('t07-rep-ok', 'Répartir', 'primaire', HASARD) + bt(None, 'Annuler'), haut=60, largeur=1120)
TOAST_REP = toast('t07-toast-rep', 'Chambres réparties', '5 chambre(s) réparties entre 2 équipière(s).')


# ------------------------------------------------ Ma journée (téléphones) --
def tache(ident, chambre_, quoi, client=None, note=None, urgent=False, etat_=('À faire', 'orange'), boutons=''):
    lignes = '<div class="s t07-quoi">%s</div>' % e(quoi)
    if client:
        lignes += '<div class="p">%s%s</div>' % (icone('personne'), e(client))
    if note:
        lignes += '<div class="t07-note" id="%s-note">%s<span>%s</span></div>' % (ident, ico(EXCLAM), e(note))
    return ('<div class="tel-carte%s" id="%s"><div class="h"><span>Chambre %s</span><span class="puce %s" id="%s-etat">'
            '%s</span></div>%s%s</div>' % (' t07-urg' if urgent else '', ident, e(chambre_), etat_[1], ident,
                                          e(etat_[0]), lignes, boutons))


def bts_tel(ident, second='fin'):
    """« Je commence », et dessous, à la même place, le bouton de l'étape suivante."""
    suite = {'fin': ('vert', ICONES['coche'], "C'est fait"), 'chk': ('vert', ICONES['liste'], 'Passer la checklist')}
    style, svg, lib = suite[second]
    return ('<div class="pile t07-pile"><div class="tel-bt violet" id="%s-go">%sJe commence</div>'
            '<div class="tel-bt %s masque" id="%s-%s">%s%s</div></div>' % (ident, ico(ICONES['play']), style, ident,
                                                                        second, ico(svg), e(lib)))


def telephone_(ident, initiale, cartes):
    """Le téléphone de l'équipière, thème MuK (ref_muk/400), ouvert sur Ma
    journée, sa page d'accueil."""
    return ('<div class="voile masque" id="%s-voile" data-layout-allow-overlap data-layout-allow-occlusion></div>'
            '<div class="tel masque t07-tel" id="%s" data-layout-allow-overlap data-layout-allow-occlusion>'
            '<div class="tel-ecran"><div class="tel-haut"><span class="burger">≡</span><span class="t07-tel-t">'
            'Ma journée</span><span class="t07-tel-pictos">%s%s<span class="t07-tel-av">%s</span>'
            '</span></div><div class="t07-tel-jour" id="%s-jour"><div class="t07-tel-barre"><span class="bt '
            'primaire">Nouveau</span><span class="t07-tel-g"><i>‹</i><i>›</i><i>%s</i><i>%s</i></span></div>'
            '<div class="tel-corps">%s</div></div></div></div>'
            % (ident, ident, ICONES['bulle'], ico(ICONES['horloge'], 't07-tel-act'), e(initiale), ident, KANBAN,
               ICONES['loupe'], cartes))


def menages_e1(p):
    """Les deux ménages quotidiens de E1, sous la 103 (ordre « date desc, priority desc, id desc »)."""
    return (tache('%s401' % p, '401 [VIP]', 'Ménage quotidien (client présent)', 'Claire Durand',
                  boutons=bts_tel('%s401' % p))
            + tache('%s202' % p, '202 [CFT]', 'Ménage quotidien (client présent)', 'Brigitte Essomba',
                    boutons=bts_tel('%s202' % p)))


TEL_A = telephone_('t07-tel-a', E1[0], tache('t07-ta103', '103 [STD]', 'Recouche complète (départ)', GASTON,
                                              boutons=bts_tel('t07-ta103')) + menages_e1('t07-ta'))
NOTE_103 = 'Inspection refusée. À reprendre : Salle de bain nettoyée, serviettes changées — serviettes manquantes'
TEL_B = telephone_('t07-tel-b', E1[0], tache('t07-tb103', '103 [STD]', 'URGENT — Recouche complète (départ)',
                                              GASTON, note=NOTE_103, urgent=True, boutons=bts_tel('t07-tb103'))
                   + menages_e1('t07-tb'))

def ch(libelle, valeur, gras=True, aide=False, ident=None):
    return ('<div class="ch"%s><span class="l%s">%s%s</span><span class="v">%s</span></div>'
            % (' id="%s"' % ident if ident else '', ' gras' if gras else '', e(libelle),
               '<sup class="t07-aide">?</sup>' if aide else '', valeur))


# ------------------------------------------------ Ma journée (Josiane) --
CARTE_J = ('<div class="t07-jcarte" id="t07-tj103"><div class="h"><span>Chambre 103 [STD]</span>'
           '<span class="puce orange" id="t07-tj103-etat">À faire</span></div>'
           '<div class="s">Inspection — passer la checklist</div><div class="p">%s%s</div>%s</div>'
           % (icone('personne'), e(GASTON), bts_tel('t07-tj103', 'chk')))
VIDE_J = ('<div class="t07-vide masque" id="t07-vide">%s<div class="t">Rien à faire pour l\'instant</div>'
          '<div class="p">Les chambres qui vous sont affectées apparaîtront ici. Si vous attendez du travail, '
          'demandez à la gouvernante de <b>répartir les chambres du jour</b>.</div></div>' % ico(SOURIRE, 't07-sourire'))
CP_JOURNEE = ('<div class="cp"><span class="bt primaire">Nouveau</span><span class="titre">Ma journée</span>%s'
              '<span class="pager" id="t07-pager-j">1-1 / 1</span>%s</div>' % (recherche([(None, 'Mes chambres')]),
                                                          vues_bt(KANBAN, ICONES['liste'])))
JOURNEE = vue_libre('t07-journee', CP_JOURNEE + '<div class="t07-grille">%s</div>%s' % (CARTE_J, VIDE_J))

# ------------------------------------------------------------- Inspection --
POINTS = ['Lit refait, draps propres', 'Salle de bain nettoyée, serviettes changées', 'Sol balayé et lavé',
          'Poubelles vidées', 'Savon, papier, eau de courtoisie réapprovisionnés', 'Minibar vérifié et recomplété',
          'Climatiseur, lumières et télécommande fonctionnent', 'Aucune odeur, aucun objet oublié']
LIGNES = ''.join('<div class="t07-ck" id="t07-ck-l%d"><span>%s</span><span class="ell">%s</span><span>%s</span></div>'
                 % (i, interrupteur('t07-ck%d' % i), e(p),
                    entree('t07-rq', 'Remarque si non conforme', classe='entree t07-rq') if i == 1 else '')
                 for i, p in enumerate(POINTS))
INSPECTION = modale('t07-as-insp', 'Inspection — chambre 103', (
    '<div class="t07-h1">Chambre <span>103 [STD]</span></div>'
    '<div class="t07-sous">Inspection — passer la checklist · contrôle <span id="t07-ctrl">0 / 8</span></div>'
    '<div class="m-aide">Cochez chaque point conforme. Un point non coché renverra la chambre en nettoyage avec '
    'votre remarque.</div>'
    '<div class="t07-ck tete"><span>OK</span><span>Point de contrôle</span><span>Remarque</span></div>' + LIGNES),
    bt(None, 'Tout cocher') + bt('t07-insp-ok', "Valider l'inspection", 'primaire') + bt(None, 'Fermer'),
    haut=16, largeur=1240)

# ------------------------------------------------------ Signaler un problème --
PROBLEME = modale('t07-as-pb', 'Signaler un problème — chambre 102', '<div class="m-grille un">%s</div>' % ''.join([
    ligne('Chambre', '<span class="t07-lien">102 [STD]</span>'),
    ligne('Quel est le problème ?', entree('t07-pb', 'Ex. : climatiseur en panne, fuite lavabo…', classe='entree t07-ligne'),
          aide=True),
    ligne('Urgence', etoiles(1)),
    ligne("La chambre ne peut pas être vendue en l'état", '<span class="case" id="t07-bloque"><i></i></span>', aide=True,
          ident='t07-bloque-l'),
    ligne('Précisions', entree('t07-precis', 'Précisions utiles au technicien', classe='entree t07-ligne')),
    ligne('Photo', '<span class="t07-photo">%s</span>' % PHOTO)]),
    bt('t07-pb-ok', 'Envoyer à la maintenance', 'primaire', AVION) + bt(None, 'Annuler'), haut=96, largeur=1120)
TOAST_PB = toast('t07-toast-pb', 'Problème signalé', 'La demande « Chambre 102 — Climatiseur en panne » est transmise '
                 'à la maintenance. La chambre est hors service jusqu\'à la réparation.')

# ------------------------------------------------------ Pannes & réparations --
CARTE_P = ('<div class="t07-pcarte" id="t07-pn-carte"><div>102 [STD]</div><span class="t07-cb">%s</span>'
           '<div class="n">Chambre 102 — Climatiseur en panne</div><div>Demandé par : %s</div>'
           '<div class="t07-pied">%s<span class="t07-pd"><i class="t07-ks"></i><i class="t07-av0"></i></span></div></div>'
           % (ICONES['coche'], e(NOM), etoiles(1)))


def colonne_p(titre, n, cartes=''):
    return ('<div class="t07-pcol%s"><div class="t"><span>%s</span><span class="plus">%s</span></div>'
            '<div class="t07-pbar"><i><b></b></i><span>%d</span></div>%s</div>'
            % ('' if n else ' vide', e(titre), ICONES['plus'], n, cartes))


def pliee(titre):
    return '<div class="t07-plie"><span>◂▸</span><b>%s</b></div>' % e(titre)


CP_PANNES = ('<div class="cp"><span class="bt primaire">Nouveau</span><span class="titre">Pannes &amp; réparations</span>'
             '%s%s</div>' % (recherche([(None, 'À faire')]), vues_bt(KANBAN, ICONES['liste'], CALENDRIER)))
PANNES = vue_libre('t07-pannes', CP_PANNES + '<div class="t07-pk">%s%s%s%s</div>' % (
    colonne_p('Nouvelle demande', 1, CARTE_P), colonne_p('En cours', 0), pliee('Réparé'), pliee('Rebut')))


# ------------------------------------------- La demande de maintenance --
def gauche(cloture):
    lignes = [ch('Chambre', '<span class="t07-lien">102 [STD]</span>', aide=True),
              ch("Chambre invendable pendant l'intervention", '<span class="case coche"><i></i></span>', aide=True),
              ch('Équipement', ''), ch('Date de la demande', JOUR, gras=False)]
    if cloture:
        lignes.append(ch('Date de clôture', JOUR, gras=False, aide=True))
    lignes.append(ch('Type de maintenance', '<span class="t07-radio"><i class="on"></i>Corrective <i></i>Préventive</span>'))
    return ''.join(lignes)


DROITE = ''.join([ch('Équipe', 'Maintenance interne'), ch('Responsable', ''), ch('Date planifiée', '', aide=True),
                  ch('Durée', '00:00 <span class="t07-gris">heures</span>', aide=True), ch('Priorité', etoiles(1))])
FICHE = ('<i class="t07-ks t07-ks-f"></i><div class="t07-lab">Demande</div>'
         '<div class="f-titre">Chambre 102 — Climatiseur en panne</div>'
         '<div class="f-cols"><div class="pile"><div class="masque" id="t07-dm-g1">%s</div><div id="t07-dm-g0">%s</div>'
         '</div><div>%s</div></div>%s<div class="t07-ph">Notes internes</div>'
         % (gauche(True), gauche(False), DROITE, onglets(['Notes', 'Instructions'])))
DEMANDE = avec_chatter(vue_fiche('t07-demande', cp_fiche('Pannes & réparations', 'Chambre 102 — Climatiseur en panne',
                                                         '1 / 1'),
                                 [bt(None, 'Annuler')],
                                 statusbar('t07-dm-st', ['Nouvelle demande', 'En cours', 'Réparé', 'Rebut'], 0), FICHE),
                       [(NOM, "Aujourd'hui à 09:40", 'Demande de maintenance créée')])
# Le suivi d'étape, posé au-dessus du message de création quand la demande passe à Réparé.
SUIVI = ('<div class="ch-msg masque" id="t07-dm-suivi"><span class="ch-av">%s</span><div><div class="ch-a"><b>%s</b> '
         '<small>Aujourd\'hui à 11:05</small></div><div class="ch-t">Statut modifié<div class="t07-trk">'
         '<b class="t07-old">Nouvelle demande</b><span class="t07-fle">→</span><b class="t07-new">Réparé</b>'
         '<i>(Étape)</i></div></div></div></div>' % (e(NOM[0]), e(NOM)))
DEMANDE = DEMANDE.replace('<div class="ch-msg">', SUIVI + '<div class="ch-msg">', 1)

# ---------------------------------------------------------------- la fenêtre --
ECRAN = navigateur(fenetre_muk('t07-app', 'Hôtel', MENUS, [TABLEAU, JOURNEE, PANNES, DEMANDE],
                               actif='Gouvernante', societe=demo.SOCIETE, initiale=NOM[0], avatar='#185FA5',
                               apps=APPS_PROFIL['gouvernante'], app_active='Hôtel',
                               calques=MENU + REPARTIR + TOAST_REP + TEL_A + INSPECTION + TEL_B + PROBLEME + TOAST_PB))

CSS = """
#t07-app .o-haut { font-size: 17px; gap: 22px; }
#t07-app .o-haut .nom-app { font-size: 21px; }
#t07-app .o-haut .menu.actif { font-weight: 600; }
#t07-app .cp .titre { font-size: 24px; }
.t07-vues { margin-left: auto; display: flex; }
.pager + .t07-vues { margin-left: 18px; }
.t07-vues i { width: 48px; height: 42px; display: flex; align-items: center; justify-content: center; background: #E9ECEF; color: #343A40; }
.t07-vues i + i { border-left: 1px solid #fff; }
.t07-vues i.on { background: #DCE6EC; box-shadow: inset 0 0 0 1px var(--muk-prim); }
.t07-vues svg { width: 20px; height: 20px; }
/* tableau des chambres */
.t07-instant { position: absolute; left: 0; right: 0; top: 80px; bottom: 0; overflow: hidden; }
.t07-k { gap: 20px; padding: 14px 20px; }
.t07-k .k-col { width: 356px; }
.t07-k .k-titre { font-size: 21px; margin-bottom: 10px; }
.t07-k .k-carte { padding: 12px 16px; line-height: 1.4; }
.t07-k .k-carte .hint { color: #243742; }
.t07-k .k-carte .t07-arr { color: #0E7490; }
.t07-k .k-carte.hors-service .mini { color: #565D64; }
.t07-k .k-carte .bts { margin-top: 8px; }
.t07-k .k-carte .lg .ico svg { width: 16px; height: 16px; }
.t07-k .t07-cle { padding: 0 10px; }
.t07-k .t07-cle .ico { width: 18px; height: 18px; }
.t07-k .t07-cle .ico svg { width: 18px; height: 18px; }
#t07-l-eq { align-items: start; }
#t07-l-eq .l { padding-top: 10px; }
.t07-tetes { position: absolute; left: 16px; top: 10px; height: 40px; }
/* menu déroulant « Gouvernante » */
.t07-menu { position: absolute; left: 1012px; top: 52px; width: 330px; padding: 6px 0; background: #fff; border: 1px solid var(--o-filet);
  border-radius: 6px; box-shadow: 0 14px 34px rgba(0,0,0,.22); z-index: 29; }
.t07-menu div { height: 44px; display: flex; align-items: center; padding: 0 20px; font-size: 19px; color: var(--o-texte); white-space: nowrap; }
/* assistants */
.t07-m-bts { display: flex; align-items: center; gap: 18px; }
.t07-agr { width: 22px; height: 22px; }
#t07-l-hotel .v { display: flex; align-items: center; gap: 12px; }
#t07-l-hotel .t07-m2o { flex: 1; }
.t07-li { width: 22px; height: 22px; display: inline-flex; color: var(--o-texte-2); }
.t07-m2o { display: block; border-bottom: 1px solid var(--o-filet); padding: 6px 4px; }
.t07-car { float: right; color: var(--o-texte-2); font-size: 15px; }
.t07-cases { display: flex; flex-direction: column; gap: 6px; padding: 6px 0; }
.t07-case { font-size: 19px; }
.t07-lecture { color: var(--o-texte-3) !important; font-weight: 400 !important; }
.t07-n { font-weight: 500; }
.t07-aide { color: var(--o-lien); font-size: 13px; margin-left: 3px; font-weight: 700; }
.t07-lien { color: var(--o-lien); }
.m-ch .v .entree.t07-ligne { margin-top: 0; height: 44px; border-width: 0 0 1px 0; border-radius: 0; padding: 0 4px; font-size: 19px; }
.m-ch .v .entree.t07-ligne .ph, .m-ch .v .entree.t07-ligne .val { left: 4px; }
.t07-photo { display: flex; align-items: center; justify-content: center; width: 150px; height: 110px; background: #F1F3F5; border: 1px solid var(--o-filet); }
.t07-photo svg { width: 64px; height: 64px; }
.etoiles .t07-et0 svg { width: 100%; height: 100%; }
/* inspection */
.t07-h1 { font-size: 32px; font-weight: 500; color: var(--o-texte); }
.t07-h1 span { color: var(--o-lien); }
.t07-sous { margin: 4px 0 8px; font-size: 18px; color: var(--o-texte-3); }
.t07-ck { display: grid; grid-template-columns: 90px 1fr 380px; align-items: center; height: 46px; border-bottom: 1px solid #EEF0F2; font-size: 19px; color: var(--o-texte); }
.t07-ck.tete { font-weight: 600; border-bottom: 1px solid var(--o-filet); }
.t07-ck .entree.t07-rq { margin: 0; height: 38px; border-width: 0 0 1px 0; border-radius: 0; padding: 0 4px; font-size: 18px; }
.t07-ck .entree.t07-rq .ph, .t07-ck .entree.t07-rq .val { left: 4px; }
#t07-rq-ph { opacity: 0; visibility: hidden; }
.t07-ck .entree.t07-rq { border-bottom-color: transparent; }
.t07-ck .entree.t07-rq.t07-edit { border-bottom-color: var(--muk-prim); }
/* téléphones */
.t07-tel { top: 14px; height: 768px; }
.t07-tel .tel-haut { background: #243742; height: 66px; font-size: 25px; padding: 0 18px; }
.t07-tel-pictos { margin-left: auto; display: flex; align-items: center; gap: 14px; }
.t07-tel-pictos svg { width: 26px; height: 26px; display: block; }
.t07-tel-act { display: inline-flex; color: #fff; }
.t07-tel-av { width: 36px; height: 36px; border-radius: 6px; background: #185FA5; color: #fff; font-size: 19px; font-weight: 700;
  display: flex; align-items: center; justify-content: center; }
.t07-tel-barre { height: 62px; background: #fff; display: flex; align-items: center; padding: 0 14px; border-bottom: 1px solid var(--o-filet); }
.t07-tel-barre .bt { height: 42px; font-size: 18px; }
.t07-tel-g { margin-left: auto; display: flex; gap: 6px; }
.t07-tel-g i { width: 40px; height: 40px; border-radius: 5px; background: #E9ECEF; color: #343A40; font-style: normal; font-size: 22px;
  display: flex; align-items: center; justify-content: center; }
.t07-tel-g svg { width: 18px; height: 18px; }
.t07-tel .tel-carte { padding: 14px 16px; }
.t07-tel .tel-carte.t07-urg { border-left: 6px solid #C82333; padding-left: 12px; }
.t07-tel .tel-bt.violet, .t07-jcarte .tel-bt.violet { background: var(--muk-prim); }
.t07-tel .tel-bt { height: 50px; font-size: 20px; }
.t07-quoi { font-weight: 700; color: var(--o-texte); }
.t07-note { margin-top: 6px; display: flex; gap: 8px; font-size: 16px; line-height: 1.35; color: #B02A37; }
.t07-note .ico { width: 16px; height: 16px; flex: none; margin-top: 2px; display: inline-flex; }
.t07-pile { margin-top: 12px; }
.t07-pile .tel-bt { margin-top: 0; }
/* Ma journée (bureau) */
.t07-grille { position: absolute; left: 0; right: 0; top: 80px; padding: 16px 20px; display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; }
.t07-jcarte { background: #fff; border: 1px solid var(--o-filet); padding: 16px 18px; color: var(--o-texte-2); }
.t07-jcarte .h { display: flex; justify-content: space-between; align-items: center; font-size: 23px; font-weight: 700; color: var(--o-texte); }
.t07-jcarte .s { margin-top: 6px; font-size: 18px; font-weight: 700; color: var(--o-texte); }
.t07-jcarte .p { margin-top: 4px; font-size: 17px; color: var(--o-texte-3); display: flex; align-items: center; gap: 6px; }
.t07-jcarte .p .ico { width: 15px; height: 15px; display: inline-flex; }
.t07-jcarte .tel-bt { height: 48px; font-size: 19px; }
.t07-vide { position: absolute; left: 260px; right: 260px; top: 230px; text-align: center; color: var(--o-texte-2); }
.t07-sourire { display: block; width: 130px; height: 130px; margin: 0 auto; }
.t07-sourire svg { width: 130px; height: 130px; }
.t07-vide .t { margin-top: 10px; font-size: 25px; font-weight: 700; color: var(--o-texte); }
.t07-vide .p { margin-top: 12px; font-size: 20px; line-height: 1.5; }
/* Pannes & réparations */
.t07-pk { position: absolute; left: 0; right: 0; top: 80px; display: flex; gap: 20px; padding: 14px 20px; }
.t07-pcol { width: 356px; flex: none; }
.t07-pcol .t { display: flex; justify-content: space-between; align-items: center; font-size: 21px; font-weight: 700; color: var(--o-texte); }
.t07-pcol .plus { width: 18px; height: 18px; color: #6C757D; display: inline-flex; }
.t07-pbar { display: flex; align-items: center; gap: 12px; margin: 10px 0 12px; }
.t07-pbar i { flex: 1; height: 8px; border-radius: 4px; background: #E9ECEF; overflow: hidden; }
.t07-pbar b { display: block; height: 100%; width: 100%; background: #ADB5BD; }
.t07-pbar span { font-size: 18px; color: var(--o-texte-2); }
.t07-pcol.vide .t07-pbar { opacity: .3; }
.t07-pcol.vide .t07-pbar b { width: 0; }
.t07-plie { width: 44px; flex: none; display: flex; flex-direction: column; align-items: center; gap: 14px; color: #495057; padding-top: 2px; font-size: 16px; }
.t07-plie b { writing-mode: vertical-rl; font-size: 21px; font-weight: 500; }
.t07-pcarte { background: #fff; border: 1px solid var(--o-filet); padding: 12px 16px; font-size: 17px; line-height: 1.45; color: var(--o-texte-2); }
.t07-pcarte .n { font-size: 20px; font-weight: 700; color: var(--o-texte); margin: 4px 0 2px; }
.t07-cb { width: 18px; height: 18px; margin-top: 4px; border-radius: 3px; background: var(--muk-prim); color: #fff; display: inline-flex; align-items: center; justify-content: center; }
.t07-cb svg { width: 13px; height: 13px; }
.t07-pied { display: flex; align-items: center; margin-top: 8px; }
.t07-pied .etoiles .ico { width: 20px; height: 20px; }
.t07-pd { margin-left: auto; display: flex; gap: 8px; align-items: center; }
.t07-ks { display: inline-block; width: 14px; height: 14px; border-radius: 50%; background: #DEE2E6; border: 1px solid #ADB5BD; }
.t07-av0 { display: inline-block; width: 26px; height: 26px; border-radius: 5px; background: #E9ECEF; border: 1px dashed #ADB5BD; }
/* la demande de maintenance */
.t07-ks-f { float: right; margin-top: 4px; }
.t07-lab { font-size: 17px; color: var(--o-texte-2); }
#t07-demande .f-titre { font-size: 34px; margin-bottom: 16px; }
#t07-demande .f-cols { gap: 34px; }
#t07-demande .ch { grid-template-columns: 210px 1fr; min-height: 44px; font-size: 18px; }
#t07-demande .ch .v { border-bottom: 1px solid #EEF0F2; min-height: 30px; padding-top: 3px; }
.t07-radio { display: inline-flex; align-items: center; gap: 8px; }
.t07-radio i { width: 16px; height: 16px; border-radius: 50%; border: 1px solid #ADB5BD; display: inline-block; margin-left: 6px; }
.t07-radio i.on { border: 5px solid var(--muk-prim); }
.t07-gris { color: var(--o-texte-3); }
.t07-ph { padding: 14px 0; font-size: 18px; color: #6C757D; }
#t07-demande .onglets { margin-top: 18px; }
.t07-trk { margin-top: 4px; padding-left: 18px; }
.t07-old { color: #6C757D; margin-right: 4px; }
.t07-fle { color: #6C757D; margin: 0 6px; }
.t07-new { color: #0E7490; }
.t07-trk i { margin-left: 8px; color: #6C757D; }
"""

TUTORIEL = {
    'slug': 't07-gouvernante',
    'profil': 't07_gouvernante',
    'numero': 7,
    'titre': 'Gouvernante : chaque chambre dit où elle en est',
    'fonction': 'Gouvernante & maintenance',
    'personnage': (NOM, ROLE),
    'accroche': {
        'kicker': 'Le tour des chambres',
        'question': 'Quelles chambres sont *vraiment* prêtes ce soir ?',
        'douleurs': [('interrogation', 'Chambre propre ? Il faut monter voir'),
                     ('cahier', 'Le ménage noté sur un cahier'),
                     ('balai', 'Qui fait quelle chambre ce matin ?'),
                     ('sablier', "L'inspection faite de mémoire"),
                     ('alerte', 'La clim en panne… et la chambre vendue'),
                     ('telephone', "On appelle l'étage pour savoir")],
        'voix': "Quelles chambres sont vraiment prêtes ce soir ? Entre le cahier de ménage, les appels à l'étage et "
                "la panne oubliée, la gouvernante court après l'information.",
    },
    'revelation': {
        'promesse': "Chaque chambre dit où elle en est. Chaque équipière retrouve ses chambres dans Ma journée. "
                    "Une panne bloquante retire une chambre libre de la vente.",
        'voix': "Avec Aïte haousse, chaque chambre dit où elle en est, et chaque équipière sait quoi faire.",
    },
    'temps': ['Organiser', 'Contrôler', 'Réparer'],
    'app': 't07-app',
    'ecran': ECRAN,
    'css': CSS,
    'vues_initiales': {'odoo': 't07-tableau'},
    'bulles': {
        'b-phrase': "Une phrase d'état par carte, calculée sans aucune saisie.",
        'b-rep': 'Les chambres à faire, à tour de rôle, étage par étage.',
        'b-tel': "Un bouton par étape : Je commence, puis C'est fait.",
        'b-check': 'Un point non coché renvoie la chambre en nettoyage, avec la remarque.',
        'b-hs': 'Hors service : retirée des disponibilités, check-in refusé.',
    },
    'reactions': {
        'r-consigne': '%s sait exactement quoi reprendre.' % E1,
        'r-fin': 'Réparée, elle revient en vente.',
    },
    'etapes': [
        {'temps': 0, 'titre': 'Le tableau des chambres',
         'texte': "Une colonne par état de ménage, une phrase claire sur chaque carte.",
         'voix': "Le tableau des chambres se lit d'un coup d'œil : une colonne par état de ménage. Sur chaque carte, "
                 "une phrase claire ; et si un client arrive, son nom et son heure d'arrivée.",
         'gestes': [pause(0.4), anneau('#t07-b0-tetes', d=1.3), zoom('#t07-b0-103', s=1.7, d=0.8),
                    bulle('b-phrase', '#t07-b0-103', cote='bas', d=2.6), pause(1.6),
                    anneau('#t07-b0-103-arr', d=1.1), dezoom(d=0.6), anneau('#t07-b0-104', d=1.2)]},
        {'temps': 0, 'titre': 'Répartir les chambres du jour',
         'texte': 'Un menu du profil Réception : on coche les équipières, les chambres partent à tour de rôle.',
         'voix': "Pour lancer la journée, Josiane ouvre Répartir les chambres du jour, un menu du profil Réception, "
                 "et coche %s et %s. Un clic sur Répartir : les cinq chambres à faire partent à tour de "
                 "rôle, et chaque carte dit qui s'en charge." % (E1, E2),
         'gestes': naviguer('repartir', [ouvrir('t07-as-rep')]) + [
             clic('#t07-eq-e1', fx=0.08, d=0.5), classe('#t07-eq-e1', ajouter=['coche']),
             clic('#t07-eq-e2', fx=0.1, d=0.4), classe('#t07-eq-e2', ajouter=['coche']),
             curseur('#t07-rep-ok', d=0.4), bulle('b-rep', '#t07-rep-n', cote='droite', d=2.2), pause(1.0),
             clic('#t07-rep-ok', d=0.45), fermer('t07-as-rep'), notifier('t07-toast-rep', duree=2.2), pause(1.6)]
                   + naviguer('tableau', [cacher('#t07-b0', d=0.2), montrer('#t07-b1', d=0.35, y=0, avec=True)])
                   + [anneau('#t07-b1-103-eq', d=1.1)]},
        {'temps': 0, 'titre': 'Ma journée, sur le téléphone',
         'texte': "Ma journée, sa page d'accueil : Je commence, puis C'est fait.",
         'voix': "Sur son téléphone, %s arrive sur Ma journée, sa page d'accueil. Sa première chambre, la cent "
                 "trois : Je commence, puis C'est fait. Comme l'hôtel exige l'inspection après recouche, la chambre "
                 "passe à inspecter." % E1,
         'gestes': [ouvrir('t07-tel-a'), pause(0.4),
                    bulle('b-tel', '#t07-ta103-go', cote='droite', d=2.4), pause(0.3),
                    clic('#t07-ta103-go', d=0.5), etat('#t07-ta103-etat', 'En cours', 'info'),
                    cacher('#t07-ta103-go', d=0.2), montrer('#t07-ta103-fin', d=0.3, y=0), pause(0.3),
                    clic('#t07-ta103-fin', d=0.45), etat('#t07-ta103-etat', 'Terminé', 'vert'),
                    cacher('#t07-ta103-fin', d=0.25), pause(0.3),
                    fermer('t07-tel-a')]
                   + naviguer('tableau', [cacher('#t07-b1', d=0.2), montrer('#t07-b2', d=0.35, y=0, avec=True)])
                   + [anneau('#t07-b2-103', d=1.2)]},
        {'temps': 1, 'titre': "L'inspection en huit points",
         'texte': 'Un point non coché, une remarque : la chambre repart en nettoyage.',
         'voix': "Josiane a créé la tâche d'inspection de la cent trois. Dans sa journée : Je commence, puis Passer la "
                 "checklist. Huit points de contrôle, un interrupteur chacun. Les serviettes manquent : Josiane laisse ce point "
                 "décoché, note sa remarque, et valide.",
         'gestes': naviguer('journee', [vue('t07-journee')]) + [
             clic('#t07-tj103-go', d=0.4), etat('#t07-tj103-etat', 'En cours', 'info', puis=0.15),
             cacher('#t07-tj103-go', d=0.2), montrer('#t07-tj103-chk', d=0.25, y=0), clic('#t07-tj103-chk', d=0.35),
             ouvrir('t07-as-insp'), curseur('#t07-ck0', d=0.35, avec=True),
             *[g for n, i in enumerate((0, 2, 3, 4, 5, 6, 7), 1)
               for g in (classe('#t07-ck%d' % i, ajouter=['on'], decale=0.03, puis=0.06),
                         texte('#t07-ctrl', '%d / 8' % n, avec=True), curseur('#t07-ck%d' % i, d=0.14, avec=True))],
             clic('#t07-rq', d=0.4), classe('#t07-rq', ajouter=['t07-edit'], puis=0.05), montrer('#t07-rq-ph', d=0.2, y=0),
             saisir('t07-rq', 'serviettes manquantes', d=0.9),
             zoom('#t07-ck-l1', s=1.45, d=0.4), bulle('b-check', '#t07-rq', cote='bas', d=1.8),
             dezoom(d=0.35), clic('#t07-insp-ok', d=0.35), fermer('t07-as-insp'),
             cacher('#t07-tj103', d=0.25), cacher('#t07-pager-j', d=0.2, avec=True), montrer('#t07-vide', d=0.4, y=10),
             cacher('#t07-b2', d=0.01, avec=True), montrer('#t07-b3', d=0.01, y=0, avec=True)]},
        {'temps': 1, 'titre': "La consigne arrive chez l'équipière",
         'texte': 'Une recouche urgente, avec le point à reprendre et la remarque.',
         'voix': "La cent trois repart aussitôt en nettoyage. %s reçoit une recouche urgente, avec la consigne "
                 "exacte : le point à reprendre, et la remarque de Josiane." % E1,
         'gestes': [pause(0.3), ouvrir('t07-tel-b'), zoom('#t07-tb103', s=1.5, d=0.8),
                    anneau('#t07-tb103-note', d=1.5), reaction('r-consigne', d=2.8), pause(2.2), dezoom(d=0.6),
                    fermer('t07-tel-b')]},
        {'temps': 2, 'titre': 'Signaler une panne',
         'texte': 'Depuis la carte : la chambre libre sort de la vente, sur fond rouge.',
         'voix': "Dans la cent deux, le climatiseur est en panne. Depuis la carte, la clé ouvre Signaler un "
                 "problème : Josiane décrit la panne et coche la case. La chambre, libre, sort aussitôt de la "
                 "vente : elle passe en rouge, hors service.",
         'gestes': naviguer('tableau', [vue('t07-tableau')]) + [
             clic('#t07-b3-102-cle', d=0.5), ouvrir('t07-as-pb'),
             saisir('t07-pb', 'Climatiseur en panne'), clic('#t07-bloque', d=0.4),
             classe('#t07-bloque', ajouter=['coche']), clic('#t07-pb-ok', d=0.5), fermer('t07-as-pb'),
             notifier('t07-toast-pb', duree=2.0), cacher('#t07-b3', d=0.2, avec=True),
             montrer('#t07-b4', d=0.35, y=0, avec=True),
             pause(0.7), zoom('#t07-b4-102', s=1.6, d=0.7), bulle('b-hs', '#t07-b4-102-bts', cote='droite', d=2.3),
             pause(1.5), dezoom(d=0.6)]},
        {'temps': 2, 'titre': 'Pannes & réparations',
         'texte': 'Josiane passe la demande à Réparé : la chambre revient en vente, à nettoyer.',
         'voix': "La demande arrive dans Pannes et réparations. Une fois le climatiseur réparé, Josiane ouvre la "
                 "demande et la passe à Réparé : la chambre revient en vente, à nettoyer, avec sa tâche de remise en "
                 "service.",
         'gestes': naviguer('pannes', [vue('t07-pannes'), cacher('#t07-b4', d=0.01, avec=True),
                                       montrer('#t07-b5', d=0.01, y=0, avec=True)]) + [
             clic('#t07-pn-carte', d=0.45), vue('t07-demande'), anneau('#t07-dm-st', d=0.6),
             clic('#t07-dm-st-2', d=0.45), classe('#t07-dm-st-0', retirer=['actif']),
             classe('#t07-dm-st-2', ajouter=['actif']), cacher('#t07-dm-g0', d=0.15),
             montrer('#t07-dm-g1', d=0.3, y=0, avec=True), montrer('#t07-dm-suivi', d=0.3, y=-6, avec=True),
             pause(0.6)]
                   + naviguer('tableau', [vue('t07-tableau')])
                   + [anneau('#t07-b5-102', d=1.1), reaction('r-fin', d=2.6), pause(1.6)]},
    ],
    'resultats': {
        'titre': "Un hôtel où chaque chambre dit où elle en est",
        'cartes': [
            {'valeur': '8', 'compter': 8, 'unite': "phrases d'état", 'icone': 'lit',
             'texte': "sur les cartes du tableau, calculées sans aucune saisie"},
            {'valeur': '8', 'compter': 8, 'unite': 'points de contrôle', 'icone': 'coche',
             'texte': "dans la checklist d'inspection, modifiables sans code"},
            {'valeur': '3', 'compter': 3, 'unite': 'boutons', 'icone': 'liste',
             'texte': "dans Ma journée : Je commence, C'est fait, Passer la checklist"},
        ],
        'voix': "Huit phrases d'état, huit points de contrôle, trois boutons dans Ma journée : la gouvernante "
                "pilote, le terrain suit.",
    },
    'cta': {
        'appel': 'Demandez votre démonstration',
        'suivant': 'La réservation en ligne',
        'voix': "Aïte haousse, par Aïte Consulting. Demandez votre démonstration, et retrouvez tous nos tutoriels sur "
                "notre chaîne.",
    },
    'vignette': {'etape': 6, 'apres': 12.0},
}
