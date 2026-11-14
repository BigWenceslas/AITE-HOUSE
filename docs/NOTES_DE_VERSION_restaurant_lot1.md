# AITE HOUSE — Restaurant, lot 1 · notes de version (14 novembre 2026)

Contenu : la caisse de service à table du lot 1 du périmètre « restaurant »
(`docs/PERIMETRE_FONCTIONNEL_RESTAURANT.md`, partie 6.2), en six incréments,
sur Odoo 18. Deux modules nouveaux, deux modules modifiés, une correction
dans le pont hôtelier, et l'outillage « restaurant seul » d'AITE.

**Pour qui.** Un restaurant, un bar ou une pizzeria qui sert à table, avec ou
sans hôtel : chaque employé a un code personnel et un niveau (serveur,
caissière, chef de salle, manager), le plan de salle est l'écran de repos de
chaque tablette, ce qui est parti en cuisine ou au bar ne s'annule plus
qu'avec le code d'un chef de salle et un motif, et le manager lit le nombre
de tables, de personnes et les annulations. Pour le client pilote (hôtel),
seules les corrections d'`aite_pos_credit`, d'`aite_pos_analytics` et
d'`aite_hotel_pos_link` le concernent (voir « Base hôtelière »).

**Édition d'Odoo.** Développé et testé sur **Community**. Aucune base
**Enterprise** n'était disponible : rien n'a été joué sur Enterprise
(écran de cuisine, réservation de tables et deux sélecteurs d'écran par
texte ou par position restent à essayer, voir les points à valider).

---

## 1. En bref

| Module | Version | Livré ? | Rôle |
|---|---|---|---|
| `aite_pos_restaurant` | **18.0.1.0.6** (nouveau) | jamais livré | toute la caisse du lot 1 |
| `aite_pos_analytics_hr` | **18.0.1.0.0** (nouveau, passerelle) | jamais livré | le serveur et la caissière dans les analyses AITE ; s'installe seule |
| `aite_pos_credit` | 18.0.2.0.5 → **18.0.2.0.6** | 18.0.2.0.6 jamais livrée | l'ardoise ne naît que d'une addition réglée ; réservée au manager en mode restaurant |
| `aite_pos_analytics` | 18.0.2.1.4 → **18.0.2.1.6** | **18.0.2.1.4 livrée** chez le client pilote (18.0.2.1.5 n'a jamais été livrée) | ventes par famille sur trois niveaux ; rien ne change dans les rapports existants |
| `aite_hotel_pos_link` | **18.0.1.0.3** (inchangée, Python seul) | livrée | ne réécrit plus ses liens de folio renvoyés par la caisse |

Aucun de ces modules ne dépend du socle hôtelier (AH-12) : un restaurant
seul installe 4 dossiers (`docs/INSTALLATION.md`, §9).

**Le parcours en trois règles.**
1. Sur le plan, toucher une table demande toujours le code (4 chiffres,
   validés seuls au quatrième). Une table libre demande ensuite le nombre de
   personnes, dans la même fenêtre (huit gros boutons, 1 à 8).
2. Le plan est l'écran de repos, toujours verrouillé : tout retour au plan
   fait oublier l'employé (après « J'envoie », après l'encaissement, après
   « Plan », après 5 minutes sans toucher l'écran).
3. Annuler ce qui est parti tient dans une seule fenêtre : combien, le code
   d'un chef de salle vérifié par le serveur, le motif.

## 2. Ce qui est livré

### `aite_pos_restaurant` 18.0.1.0.6 — la caisse du restaurant

**Mise en service (incrément 1).**
- Case **« Service à table contrôlé »** sur la caisse (réglages du Point de
  Vente, bloc Restaurant, juste après « Est un bar/restaurant », avec sa
  phrase). La cocher pose la connexion par code, le contrôle des prix, les
  remises désactivées, le partage et l'impression de l'addition ; décocher
  « Se connecter avec Employés » ou « Est un bar/restaurant » est refusé
  tant qu'elle est cochée (R31) ; elle ne change pas caisse ouverte.
- **Caisse « Restaurant »** posée d'office (Espèces, Mobile Money, salle
  « Salle »), à l'installation si le plan comptable est déjà chargé, sinon
  au premier chargement du plan comptable de la société ; jamais recréée par
  un rechargement ; une caisse existante n'est jamais modifiée.
- Fiche employé, première page : **« Niveau en caisse »** et **« Code
  caisse »** (4 chiffres, obligatoire, unique dans la société, proposé
  d'office ; le refus ne nomme jamais le collègue ; « Dupliquer » donne une
  copie sans niveau ni code). Aucun courriel demandé aux employés.
- Le tableau des droits (quatre niveaux) dans un seul fichier Python pur,
  envoyé à la caisse ; rôle de `pos_hr` dérivé du niveau ; badge retiré.

**Le code et le plan verrouillé ; les gestes réservés (incrément 2).**
- Plus d'écran « Déverrouiller la caisse » ni d'écran de veille ; un
  rechargement verrouille ; la prise de main par le nom en haut redemande un
  code.
- Ouverture et fermeture de la caisse par code **vérifié par le serveur**
  (caissière pour ouvrir, chef de salle pour fermer) ; « Caisse ouverte par »
  et « Caisse fermée par » sur la fiche de session.
- Gestes réservés : encaisser (caissière et au-dessus), espèces et fermeture
  (chef de salle), imprimer le rapport (caissière), rembourser, prix,
  ardoise (manager), écart de caisse au-delà du maximum (manager).
- « J'envoie » (notification « Envoyé : … », retour au plan), « J'encaisse »,
  « J'ouvre la caisse », « Retour » au lieu de « Discard » ; menu ≡ réduit à
  Commandes, Entrée ou sortie d'espèces, Fermer la caisse (et Imprimer le
  rapport s'il y a une imprimante).

**La table (incrément 3).**
- Personnes demandées à l'ouverture (pas de zéro ; « 9 et plus ») ; la table
  est réservée sur tous les postes dès la validation ; « 4 personnes » sur
  l'écran de commande change le nombre en deux touches.
- « Ouverte par » (figé), « Heure d'ouverture » (horloge du serveur),
  « Encaissée par » (écrit par le serveur) sur la fiche de l'addition.
- **Journal des saisies** : qui a ajouté chaque produit, à quelle heure
  (bouton « Saisies » de la fiche) ; ni la division ni la réunion ne sont
  des saisies.
- Un numéro tapé qui n'est pas sur le plan ouvre une table à ce nom ;
  réglage « Autoriser la vente sans table » (décoché d'office).
- Phrase d'état « Table 12 · ouverte par Awa · 35 min » ; « Addition »,
  « Diviser l'addition », « Déplacer ou réunir », « Annuler la table ».

**Annuler ce qui est parti (incrément 4).**
- Verrou après envoi, sur tous les chemins (⌫, « +/- », quantité tapée,
  « Annuler la table », corbeille des commandes, fermeture avec des tables
  ouvertes) ; ⌫ retire librement ce qui n'est pas parti.
- Fenêtre d'annulation : combien, code d'un chef de salle vérifié par le
  serveur, motif ; un chef de salle identifié ne retape pas son code ; la
  serveuse reste identifiée. À la fermeture, « Annuler ces tables » : une
  fenêtre, un motif.
- Rien n'est jamais refusé à la synchronisation : ce qui arrive sans code est
  tracé « Retrait sans code » ou « Annulation sans code ».
- **Restaurant → Annulations** (aujourd'hui d'office, semaine, mois, année,
  période ; « Sans code » ; par motif, employé, produit) ; cinq motifs posés
  d'office (Point de Vente → Configuration → Motifs d'annulation) ; profil
  **« Restaurant : lecture des rapports »** pour le chef de salle, sans accès
  à la caisse.

**Le plan en couleurs ; les produits épuisés (incrément 5).**
- Gris = libre, vert = ouverte, orange = ouverte depuis le délai (60 minutes
  d'office, réglable) ; durée sous le numéro (« 35 min », « 1 h 05 »),
  comptée depuis l'ouverture même après un déplacement ; minuterie de 30 s ;
  légende en bas du plan.
- Un produit suivi en stock et épuisé n'est pas ajouté (toucher, code-barres,
  pavé, variante choisie) : « Produit épuisé », avec ce qu'il faut faire ; ce
  qui est parti sur les tables ouvertes est déduit ; une entrée de stock rend
  la vente en moins d'une minute, sans recharger ; hors connexion, la caisse
  vend.

**Les rapports (incrément 6).**
- **« Personnes et tables »** (Point de Vente → Analyse) : tables,
  personnes, ventes sans table, articles et total, par jour, session,
  « Ouverte par », « Encaissée par » ; une division ne compte qu'une fois,
  une réunion additionne les personnes ; ni les additions ouvertes ou
  annulées, ni les remboursements.
- **Rapport de fermeture** (caisse et gestion) : tables, personnes, ventes
  sans table, annulations de la session avec leur motif et qui les a
  autorisées.
- Les quantités vendues de chaque produit (REST-25 critère 2) se lisent dans
  **« Détails des ventes »** d'Odoo (Point de Vente → Analyse), sur la même
  période, et dans le rapport de fermeture.
- La fenêtre de fermeture d'Odoo dit **« Entrée ou sortie d'espèces »**
  (bouton) et **« Entrées et sorties d'espèces »** (détail), comme le menu ≡,
  au lieu de « Cash entrant/sortant » ; « 1 commande » au singulier
  (18.0.1.0.6, revue de la partie 6b).

### `aite_pos_credit` 18.0.2.0.6 — l'ardoise
- **AH-01** : l'ardoise ne naît que d'une commande réglée (payée,
  terminée, facturée) ; annuler la commande annule son ardoise ouverte, sans
  remboursement.
- **AH-02** : sur une caisse au service à table contrôlé, « Mettre sur
  ardoise » et les modes « payer plus tard » réservés ne sont proposés qu'au
  manager. **Hors de ce mode** (toute autre caisse, hôtel compris), le
  bouton se comporte exactement comme avant.
- Réglages renommés `aite_credit_*` : Odoo n'écrit plus trois
  avertissements à chaque enregistrement des réglages du Point de Vente.

### `aite_pos_analytics` 18.0.2.1.6 — les ventes par famille
- Trois colonnes **Famille, Sous-famille, Sous-sous-famille** (familles de
  l'écran de commande, jusqu'à la racine ; un article rangé plus bas compte
  sous son ancêtre de 3ᵉ niveau ; un article dans plusieurs familles ne
  compte que dans la première).
- Un seul champ de recherche **« Famille »** : « Alcoolisé » tapé ne ramène
  que la famille de ce nom (pas « Non alcoolisé ») ; favori partagé **« Ventes
  par famille »** (Famille > Sous-famille en deux touches, une seule colonne
  « Total » avec ses quatre mesures : 18.0.2.1.6). Le favori est posé une
  fois (le client peut le renommer) : une base déjà en 18.0.2.1.5 — bases
  d'AITE seulement — garde l'ancien favori, qui répète les quatre mesures
  pour chaque catégorie de produit en colonne.
- La vue relit des données à jour (`flush_model`) ; point d'extension pour la
  passerelle. **Rien ne change** dans les rapports existants (vérifié par une
  mise à niveau d'une base qui a des ventes).

### `aite_pos_analytics_hr` 18.0.1.0.0 — le serveur dans les analyses (AH-03)
« Serveur (ouverte par) » et « Encaissée par » dans l'analyse AITE ;
`user_id` affiché « Compte Odoo ». Passerelle `auto_install` : elle ne
s'installe que si le restaurant est installé.

### `aite_hotel_pos_link` 18.0.1.0.3 — correction (Python seul)
Une addition de table déjà enregistrée échouait à la synchronisation
suivante pour un caissier sans profil hôtel (« Access Denied … »). Version
inchangée (aucune vue ni donnée) : un **redémarrage** suffit.

### Outillage d'AITE (environnement de développement)
- `dev/setup_env.sh --restaurant` : base `aite_resto` créée comme l'écran de
  création (Cameroun, français, sans démonstration), modules du restaurant,
  graine `dev/seeds/seed_restaurant.py` (12 tables ; familles Nourriture >
  Pizzas, Petit déjeuner, Plats ; Boisson > Alcoolisé > Bière, Vin, Whisky ;
  Boisson > Non alcoolisé > Sodas, Café, et les mêmes catégories de produit ;
  33 produits en FCFA ; bières suivies avec leur stock de départ ; cinq
  employés fictifs aux quatre niveaux, sans courriel ; comptes « caisse »,
  « manager », « chef ») ; `websocket-client` installé (sans lui, les tours
  sont ignorés sans erreur). **Garde-fou** (revue de 6b) : une base existante
  qui n'est pas celle du restaurant (base hôtelière, ou base sans
  `aite_pos_restaurant`) est refusée, sans rien y installer — un
  `ODOO_DB=aite_dev` resté dans le shell ne peut plus y verser le restaurant
  et sa graine ; de même, le mode hôtel refuse la base du restaurant
  (`dev/etat_base.py`).
- `dev/run_tests.sh restaurant` : tests purs, scénario novice
  `tests/restaurant/scenario_restaurant.py`, audit des menus ; refuse une base
  absente, hôtelière ou sans restaurant, avec la commande à lancer. Le
  scénario se rejoue sur la base de travail après chaque service : la
  session « Contrôle d'ouverture » qu'Odoo rouvre après chaque fermeture est
  fermée le temps du scénario (rollback final). **Correction** : la ligne
  « Tests purs — vague 1 » ne faisait jamais échouer le script.
- `tests/restaurant/shots.py` : captures du parcours (`captures/restaurant/`),
  à prendre sur une copie jetable de la base (le parcours écrit des ventes et
  ferme la caisse).
- Tour **`AiteParcoursTour`** : un service complet joué à l'écran, qui compte
  les touches de chaque ligne de la partie 1.2 (partie 3 ci-dessous).
- Cahier de recette : domaine **R** (`recette/cas_de_test.py`).

## 3. Le parcours mesuré à l'écran (`AiteParcoursTour`)

Un service complet, de l'ouverture de la caisse à sa fermeture, puis le
lendemain (réouverture, fermeture sans vente), joué dans Chrome sur une caisse
au service à table contrôlé ; une étape par touche, et chaque ligne de la
partie 1.2 de la spécification jouée au moins une fois (revue de 6b).

| Rôle — geste | Partie 1.2 | Mesuré |
|---|---|---|
| Tous — prendre son poste | 0 | le tour commence sur le plan, la fenêtre du code ouverte d'elle-même |
| Caissière — ouvrir la caisse le matin | 5 | **5** (et **5** le lendemain, fond prérempli) |
| Serveur — ouvrir une table et envoyer | 7 + n | **9** (n = 2), **8** (n = 1) |
| Serveur — ajouter à sa table et envoyer | 6 + n | **7** (n = 1) |
| Serveur — imprimer l'addition | 6 | **6** (imprimante de tickets simulée) |
| Serveur — retirer un produit pas encore envoyé | 3 (2 si la ligne est sélectionnée) | **2** (ligne sélectionnée) |
| Serveur — changer le nombre de personnes | 2 | **2** |
| Serveur — produit épuisé refusé | — | **1** (« Produit épuisé », rien n'est ajouté) |
| Serveur + chef — annuler un produit envoyé, sur le poste du serveur | 3 + 5, + 1 si plus d'une unité | **9** (2 unités envoyées) |
| Chef seul — annuler un produit envoyé | 9 | **9** |
| Chef seul — annuler une table qui a des produits envoyés | 8 | **8** |
| Caissière — encaisser en espèces, somme exacte | 8 | **8** |
| Caissière — encaisser au poste d'un serveur resté identifié | 7 | **7** |
| Manager — prendre la main sur une addition ouverte au nom d'une caissière, puis encaisser | 8 | **8** |
| Caissière — deux parts d'une addition divisée | 14 + n | **15** (n = 1) ; la caisse revient d'elle-même à la table, la caissière toujours identifiée |
| Chef — sortir des espèces | 7 + saisie | **18** (7 + « 1000 » + « Monnaie ») |
| Chef — fermer la caisse, sans table ouverte | 7 + chiffres | **11** (4 chiffres) |
| Chef — fermer avec des tables ouvertes et les annuler | + 2 | **13** (7 + 4 chiffres + 2), avec 2 tables ouvertes |
| Manager — encaisser une table ouverte par une autre | 8 | **8** (« ouverte par » reste figé) |
| Une table servie de bout en bout | 27 + n | **30** (n = 3) |
| Le service, de l'ouverture à la dernière table (hors fermetures et lendemain) | — | **221** |

Le serveur garde ensuite ce qui a été fait (vérifié en Python après le
tour) : caisse ouverte par la caissière et fermée par le chef de salle, deux
fois ; six additions payées pour 5 500 FCFA, une sortie de 1 000, 4 500
comptés à la fermeture et repris en fond le lendemain ; « ouverte par » et
« encaissée par » de chaque addition (la table d'Awa encaissée par le
manager garde « ouverte par Awa ») ; la part « 4B » rattachée à son origine ;
cinq annulations, toutes autorisées par le chef de salle (deux produits, une
table, deux tables à la fermeture), aucune sans code ; le produit retiré
avant envoi n'est ni une saisie ni une annulation ; le produit épuisé n'a
jamais été ajouté ; le stock suit (la bouteille d'une table annulée à la
fermeture ne sort pas). La fenêtre de fermeture dit « Entrée ou sortie
d'espèces » et « 6 commandes », puis « 0 commande » le lendemain.

## 4. Installer, mettre à niveau

- **Restaurant seul** : `docs/INSTALLATION.md`, §9 (4 dossiers ; base créée
  avec le pays Cameroun ; ce qui est posé d'office ; les comptes ; ce que fait
  le manager avant le premier service).
- **Mise à niveau** d'une base qui a déjà ces modules : fermer les caisses,
  déposer les dossiers (jamais remplacer le répertoire entier), redémarrer,
  Apps (mode développeur) → « Mettre à jour la liste des Apps » → **Mettre à
  niveau** `aite_pos_restaurant`, `aite_pos_analytics`, `aite_pos_credit` ;
  installer à la main « AITE — Analyses du restaurant par employé » s'il est
  resté « Non installé ». Ne rien désinstaller pour une mise à niveau ; ne
  jamais retirer des fichiers avant d'avoir désinstallé le module depuis Apps.
- **Base hôtelière (client pilote)** : mettre à niveau `aite_pos_analytics`
  (18.0.2.1.6) et `aite_pos_credit` (18.0.2.0.6) ; redémarrer pour
  `aite_hotel_pos_link`. `aite_pos_restaurant` n'y est pas installé : les
  caisses ne changent pas. Vérifié sur une copie de la base de développement
  hôtelière (`dev/run_tests.sh` : « TOUT EST VERT »).
- **Ce que la mise à niveau fait seule** : la migration 18.0.2.0.6
  d'`aite_pos_credit` annule les ardoises restées ouvertes sur une commande
  annulée sans remboursement, et **signale au journal** (sans y toucher)
  celles qui sont déjà remboursées ou rattachées à une addition encore
  ouverte ; la vue de l'analyse AITE est recréée avec les familles.

## 5. Écart à nos choix par défaut : Q17

| Choix par défaut | Ce que fait le lot 1 | Pourquoi |
|---|---|---|
| Q17 : « pas de délai d'inactivité au départ » | Après **5 minutes** sans toucher l'écran, le poste revient au plan verrouillé ; la personne suivante retape son code. Le délai n'est pas réglable (REST-02-P2, lot 2). | REST-17 critère 2 exige le plan affiché sur un poste laissé seul 10 minutes, et le plan est verrouillé. Sans ce délai, ce critère dépendrait de la discipline du personnel. |

## 6. Écarts à la spécification

Regroupés par sujet ; chacun a été décidé et écrit au moment de son
incrément.

**Mise en service et réglages**
- Vue des réglages héritée de celle du Point de Vente (elle vise aussi les
  listes de `pos_hr`) ; la case est placée juste après « Est un
  bar/restaurant » (sa phrase dit « ci-dessous »), pas en fin de bloc.
- Caisse « Restaurant » posée au seul **premier** chargement du plan
  comptable de chaque société.
- Réglages d'`aite_pos_credit` renommés `aite_credit_*` et migration
  18.0.2.0.6 : non prévus par la spécification.
- Les réglages du Point de Vente sont réservés à Administration /
  Paramètres : c'est AITE qui coche la case et règle le délai, pas le
  compte du manager de la partie 4.4.
- Profil du manager : Administrateur du Point de Vente, Employés
  « Gestionnaire : Gérer tous les employés » (la spécification écrivait
  « Agent ») **et Facturation** (sans lui, Odoo refuse le rapport de session
  dès qu'une vente est payée).
- « Autoriser la vente sans table » se change caisse fermée, comme la case
  (la partie 4.3 ne le disait que de la case). Délai et refus des épuisés se
  changent caisse ouverte et s'appliquent à la réouverture ; ordre des
  réglages : case, délai, vente sans table, refus.
- Délai de moins d'une minute refusé par une contrainte (texte ajouté) ; un
  délai vide vaut 60 ; la phrase passe au singulier pour 1 minute.
- `_barcode = False` dès l'incrément 1 ; deux tours de fumée non prévus
  (`AiteModeActifTour`, `AiteModeInactifTour`).
- La phrase de la case décrit le lot 1 complet : l'incrément 1 n'a jamais été
  livré seul (point de l'incrément 1, réglé par cette livraison d'ensemble).

**Le code, le plan, les gestes réservés**
- `aite_ouvrir_caisse`, `aite_fermer_caisse` et `aite_autoriser_annulation`
  rendent `{'erreur': message}` au lieu de lever une erreur (la fenêtre
  reste ouverte, rien dans le journal) ; les gardes du serveur lèvent
  toujours une erreur.
- « Ouverte par » et « fermée par » (et leurs notes) sont écrits à
  l'ouverture et à la fermeture **effectives**, pas dans les requêtes ;
  fermer une caisse pas encore ouverte répond R3.
- Le compte de la caisse ne ferme plus depuis la gestion sans code ; seul un
  responsable du Point de Vente le fait. Les champs de session sont protégés
  en écriture et en création.
- Le plan se reverrouille après un geste du menu ≡ ; la fermeture réutilise
  le code de la visite si la personne a le droit de fermer (T3).
- R14 remplace aussi la fenêtre d'Odoo à la confirmation de la fermeture.
- « Obtenir des codes QR » reste dans le menu ≡ sur petit écran (le masquer
  demanderait de dépendre de `pos_self_order`).
- Hors mode, `aitePeut` rend toujours vrai ; « Retour » remplace « Discard »
  sur toutes les fenêtres numériques, hors mode compris.
- Bouton d'ardoise : décision d'arbitrage sur AH-02 — hors mode, exactement
  le comportement d'avant ; en mode, manager seul et seulement s'il existe un
  mode « ardoise ».

**La table et le journal des saisies**
- Code et personnes dans une seule fenêtre, en deux étapes, avec une
  relecture du serveur entre les deux ; R5 affiché dans la fenêtre ; « 9 et
  plus » ouvre son pavé sous les huit boutons ; étape des personnes aussi pour
  une vente « + » portée sur une table libre.
- L'addition quittée est enregistrée à **chaque** changement d'addition
  courante (onglet, liste, sélecteur, numéro tapé), au nom de qui l'a
  remplie (T19 étendu), sauf pendant une division ou un déplacement.
- Une table touchée ne reprend qu'une addition résiduelle (jamais enregistrée
  ni réservée) ; pas de synchronisation de plus après une division.
- Phrase d'état au-dessus de l'addition ; bouton des personnes masqué sur une
  vente sans table ou une part ; rangée principale sans icône.
- Numéro inconnu : « Retour » depuis le plan laisse le plan verrouillé, depuis
  l'écran de commande ramène à l'addition d'avant. R4 a une variante pour la
  vente sans table.
- Heure reçue de la caisse acceptée seulement si elle est plus ancienne et
  pas dans le futur ; textes des notes de traçage écrits par nous (la
  spécification ne les donnait pas) ; journal : libellés « Employé » et
  « Article ».
- Espaces insécables dans tous les textes de la caisse (« ? » et « : » ne
  passent plus seuls à la ligne).

**Les annulations**
- La demande d'annulation prend aussi sa nature (produit, table,
  fermeture) ; pour une table ou la fermeture, le serveur annule tout ce
  qu'il sait parti et rend les quantités annulées ; une clé rejouée ailleurs
  ou une ligne en double : « Demande d'annulation incomplète. » ; motif
  disparu : « Motif inconnu : rouvrez la fenêtre d'annulation. » (textes
  ajoutés).
- Bon d'annulation fait de la seule ligne annulée (au lieu de la fonction
  d'Odoo qui enverrait aussi les autres produits pas encore partis).
- « Annulation sans code » écrite à l'annulation et à la suppression d'une
  addition, d'où qu'elles viennent ; « Retrait sans code » pour toute baisse
  ou suppression directe d'une ligne envoyée et toute part négative hors
  remboursement.
- Pavé : ⌫ et « +/- » ramènent d'abord librement une ligne à ce qui est
  parti, puis ouvrent la fenêtre ; « +/- » sur une ligne pas envoyée la
  retire (jamais de ligne négative hors remboursement) ; filet « Quantité
  négative » (titre et texte ajoutés).
- Fenêtre : code inconnu → R1 dans la fenêtre ; code sans le droit → R8 en
  notification ; R24 dans la fenêtre ; R27 : la fenêtre reste, même clé au
  nouvel essai ; R26 : la fenêtre se ferme ; un motif archivé pendant que la
  fenêtre est ouverte est accepté.
- Fermeture : fenêtre de confirmation d'Odoo avec nos textes et le titre
  « Fermer la caisse », variante au singulier ; pas de fenêtre de motif si
  aucune table n'a de produit envoyé ; pas de notification après
  l'annulation d'une table ou à la fermeture.
- Libellés de champs distincts (« Employé demandeur » / « Demandée par »,
  « Responsable » / « Autorisée par », « Fiche du motif » / « Motif ») ;
  icône du menu Restaurant ; colonne « Nature » masquée par défaut ; bouton
  « Annulations » de la fiche réservé au groupe de lecture.
- Auteur d'une trace sans code : la gestion est reconnue à l'action du menu
  « Action » ou à un compte autre que celui qui a ouvert la session ; la
  tablette doit donc être ouverte sous le compte de la caisse.

**Couleurs et stock**
- Le refus des épuisés n'est pas dans `addLineToCurrentOrder` (que la note
  cuisine et d'autres modules utilisent pour autre chose) mais aux gestes qui
  ajoutent : toucher, code-barres, fenêtre de configuration, pavé.
- Avant tout refus, le stock est relu sur le serveur : à 2 ou moins (T20),
  et aussi quand la quantité demandée dépasse le reste connu ; un produit
  sans suivi n'attend jamais ; une erreur du serveur laisse vendre.
- Pavé : un chiffre qui demande une relecture est appliqué au retour du
  serveur s'il est encore celui du pavé, de la même ligne, de la même
  addition ; les gestes passent l'un après l'autre (double toucher sur la
  dernière bouteille : le second est refusé), attente bornée à 10 s.
- Le disponible peut être négatif ; il est limité à la société de la
  caisse ; tables libres marquées « libre » ; pastille de couleur dans la
  légende.

**Rapports et analyses**
- Le tableau croisé de l'analyse AITE s'ouvre toujours par catégorie de
  produit (une base hôtelière garde ses rapports) ; les lignes Famille >
  Sous-famille viennent du favori « Ventes par famille » (partie 5.4).
- Le champ « Famille » est un champ de recherche (nom exact d'abord, puis
  « contient »), pas un filtre « contient » sur les trois niveaux.
- Liste propre à « Personnes et tables » (Date, Table, Personnes, Articles,
  Ouverte par, Encaissée par, Total en FCFA, sommes) : la spécification ne
  la décrivait pas.
- Bloc du rapport de fermeture seulement pour une caisse au service à table
  contrôlé, et pas dans le rapport par employé de `pos_hr` ; quantités
  écrites par le serveur dans la langue de l'utilisateur (« 1,5 »).
- Crochet de désinstallation de la passerelle (sans lui, Odoo emporterait la
  vue de l'analyse).
- La « première » famille d'un article est triée sur le nom anglais du champ
  traduisible (`name->>'en_US'`) ; la vue relit aussi les familles et les
  produits à jour (`flush_model` sur les catégories de caisse et les
  produits), en plus des commandes.

**Outillage et tests**
- Scénario de l'incrément 5 : la Guinness remplace la Castel pour le stock
  (Odoo refuse de changer le suivi d'un produit déjà vendu) ; tours joués
  au-delà de la spécification (couleurs à 60 et 90 minutes, REST-17 critère
  3, mémoire du stock forcée à 0, réglage décoché, tours des correctifs,
  code-barres).
- Écarts d'étape, devenus sans objet avec la livraison complète : pas de
  fichiers de sécurité à l'incrément 1 (ajoutés à l'incrément 4) ; scénario
  de l'incrément 1 écrit après le code (les corrections, elles, ont été
  jouées en rouge d'abord) ; Q19 (R4) inerte jusqu'à l'incrément 3, puis en
  vigueur avec R19 ; drapeaux de déplacement, « Remboursement » masqué, « + »
  masqué et R17 pris en avance à l'incrément 2 ; compteurs en logique pure à
  l'incrément 3 (champs à l'incrément 6) ; « Retrait sans code » écrit au
  journal à partir de l'incrément 4 ; tour de prise en main réécrit à
  l'incrément 3 (le manager encaisse par le code de « J'encaisse »).
- Le scénario novice se joue aussi sur la base de travail `aite_resto` : il
  reprend l'équipe, la salle et les familles de la graine, ferme le temps du
  scénario la session « Contrôle d'ouverture » qu'Odoo rouvre après chaque
  fermeture (rollback final), et ne s'arrête que sur une caisse vraiment en
  service (ouverte ou en cours de fermeture).
- La graine ne pose aucune taxe : les prix de la carte sont des prix TTC
  ronds ; ses codes d'employés sont des codes de démonstration (le premier
  chiffre suit le niveau).
- `dev/setup_env.sh` garde le thème MuK dans `dev/odoo.conf` quand il y
  était : préparer la base du restaurant ne retire pas le thème d'`aite_dev`.

**Revue de la partie 6b (outillage, documentation, recette)**
- Fenêtre de fermeture d'Odoo, en mode : « Entrée ou sortie d'espèces »
  (bouton), « Entrées et sorties d'espèces » (détail des mouvements) et
  « {n} commande » / « {n} commandes » remplacent « Cash entrant/sortant » et
  « 1 commandes » ; ces textes ne figurent pas dans la partie 1.4 (règle 6 :
  pas d'anglais résiduel, et le même geste porte le même nom que dans le menu
  ≡). `aite_pos_restaurant` passe en 18.0.1.0.6.
- Favori « Ventes par famille » : en plus des lignes Famille > Sous-famille
  (partie 5.4), aucune colonne (une colonne « Total » avec ses quatre
  mesures, au lieu de quatre mesures répétées pour chaque catégorie de
  produit) ; `aite_pos_analytics` passe en 18.0.2.1.6 (donnée).
- `dev/setup_env.sh` et `dev/run_tests.sh restaurant` refusent une base qui
  n'est pas du bon genre (nouveau fichier `dev/etat_base.py`) : la variable
  `ODOO_DB` est gardée (elle sert aussi aux bases jetables), mais elle ne peut
  plus désigner la base hôtelière en mode restaurant.
- `AiteParcoursTour` joue toutes les lignes de la partie 1.2 (la consigne de
  6b n'en demandait qu'une partie), puis le lendemain : réouverture avec le
  fond prérempli et fermeture sans vente ; 516 étapes.
- `recette/build_xlsx.py` et `build_plan.py` : 50 lignes libres après le
  dernier cas dans les formules, nombre de modules compté dans `addons/`,
  version du cahier dans `cas_de_test.py`, conditions préalables propres au
  restaurant seul.

## 7. Limites (à dire au client)

**Partie 8.3 de la spécification**
- **L'identité est affirmée par le poste.** Comme dans `pos_hr`, le code est
  comparé sur la tablette (empreinte sans sel) : suffisant pour savoir qui a
  fait quoi, pas une sécurité forte. Les codes d'ouverture, de fermeture et
  d'annulation sont vérifiés par le serveur, mais restent lisibles de la même
  façon. Une badgeuse pour les supérieurs est au lot 2 (Q18).
- **Le déplacement est déclaratif** : quelqu'un qui modifie le code de la page
  pourrait faire passer un retrait pour un déplacement (même niveau
  d'attaque que la falsification de l'identité).
- **Le code de la visite reste en mémoire** du poste jusqu'au verrou suivant.
- **Hors connexion**, on vend sans contrôle de stock, sans annulation, sans
  ouverture ni fermeture de caisse (Q59) ; les saisies faites pendant la
  coupure sont attribuées à la personne identifiée quand l'addition est
  enfin enregistrée.
- **Deux postes peuvent encore ouvrir la même table libre** dans la seconde
  qui sépare la relecture du serveur de l'enregistrement de l'addition.
- **Les horloges des tablettes** doivent être à l'heure : l'heure d'ouverture
  vient du serveur, mais la durée et la couleur sont comptées par chaque
  poste.
- **Le stock** suppose le mode « temps réel » d'Odoo (réglage par défaut) ; un
  produit suivi vendu dans une **formule** n'est pas contrôlé (Q69).
- **Les filets de la caisse** rendent un message que seul le pavé affiche ; un
  module tiers qui baisse une quantité sans le lire (fidélité, cartes
  cadeaux) n'afficherait rien ; le serveur trace quand même.

**Trouvées en développement**
- Le **refus des épuisés est fait par le poste** : une vente qui le contourne
  (requête forgée, module tiers, poste hors connexion) n'est ni refusée ni
  tracée par le serveur, et le disponible peut devenir négatif. Un produit
  dont « Suivre l'inventaire » change pendant le service est vu à la
  réouverture de la caisse.
- Le **prix et la remise d'une ligne envoyée** ne sont pas surveillés : la
  touche « Prix » est réservée au manager et les remises sont décochées, mais
  une requête forgée du compte de la caisse peut baisser un prix sans trace.
- Un **remboursement** est reconnu à sa ligne d'origine, déclarée par le
  poste : une requête forgée qui la pose sur une ligne négative échappe au
  « Retrait sans code ».
- Une trace sans code écrite par le compte de la caisse **depuis la gestion**
  sans passer par le menu « Action » (suppression depuis la liste) est au
  nom de l'employé de l'addition.
- Un second poste resté sur une **copie ancienne** qui renvoie une ligne plus
  basse fait noter deux fois la même unité au journal des saisies (le
  serveur ne la distingue pas d'un vrai retrait suivi d'un ajout).
- Deux postes sur la même table : la synchronisation d'Odoo peut tracer à
  tort « Annulation sans code » sur une addition en double ; deux demandes
  d'annulation simultanées avec la même clé écrivent une ligne ERROR « bad
  query » dans le journal du serveur (Odoo rejoue la seconde, qui rend la
  première réponse).
- Une tablette dont l'horloge retarde peut faire garder au serveur sa propre
  copie de ce qui est parti (le verrou, baissé par le serveur, n'en dépend
  pas).
- Le pavé d'Odoo ignore plus de deux touches très rapprochées : ⌫ ⌫ tapé
  trop vite est perdu.
- **« Tableau » au lieu de « Table »** dans la barre du plan et la colonne
  « Table » de « Commandes » (collision de traductions d'Odoo : « Table » est
  traduit « Tableau » par des modules installés avec le Point de Vente).
  Constaté aussi sur une base **restaurant seul**, sans aucun module
  hôtelier, et **instable** : sur la même base, la caisse ouverte par le
  tableau de bord (« Ouvrir la caisse ») comme par son adresse directe a
  affiché « Tableau » avant le premier service, puis « Table » après ; les
  captures de `captures/restaurant/` montrent « Table ». Le client du
  restaurant peut donc le voir. À traiter avec les traductions (AH-09).
- La notification après « J'envoie » reprend, comme les compteurs du bouton
  d'Odoo, le nom de la famille la plus fine du produit, tel quel :
  « Envoyé : 1 Pizzas, 2 Bière. » avec la carte de démonstration (la partie
  1.4 donnait l'exemple « 2 Boisson, 1 Nourriture »).
- **Après chaque fermeture, la tablette rouvre une session** en « Contrôle
  d'ouverture » (comportement d'Odoo : la page se recharge et Odoo crée la
  session suivante). Tant qu'elle existe, Odoo grise « Service à table
  contrôlé » et « Autoriser la vente sans table » dans les réglages, et
  l'administrateur ne peut pas supprimer cette session (droits d'Odoo). Le
  délai de l'orange et le refus des épuisés, eux, se changent à tout
  moment.
- **« Articles »** est un décimal (un produit pesé compte 0,5) et s'affiche
  « 20,00 » dans le tableau croisé ; les montants du tableau croisé n'ont
  pas « FCFA » (format d'Odoo).
- **Caisses mêlées** : « Ventes sans table » et « Personnes et tables »
  comptent aussi les ventes d'une caisse qui n'est pas au service à table,
  quand plusieurs caisses partagent la base.
- La passerelle `aite_pos_analytics_hr` ne s'installe seule qu'à
  l'installation : sur une base où `aite_pos_analytics` et
  `aite_pos_restaurant` étaient déjà installés, l'installer à la main.
- Le prix moyen par personne reste celui du tableau de bord standard d'Odoo,
  qui compte les ventes sans table et les remboursements comme des personnes
  (REST-26-P1, lot 2). La carte « par caissier » du tableau de bord AITE lit
  toujours le compte Odoo (hors lot 1).
- Le rendu du rapport par employé de `pos_hr` écrit un avertissement « t-key »
  d'Odoo dans le journal du serveur (sans effet à l'écran).
- Le test d'Odoo `point_of_sale` `test_report_listing` est en erreur dès
  qu'`aite_pos_restaurant` est installé (journal d'espèces de la caisse posée
  d'office) ; sans effet pour l'utilisateur, non corrigé.
- Le nom d'application d'`aite_pos_analytics` porte encore le nom du client
  pilote (« AITE — POS Analytics (LAVERANDAH) ») : visible dans les
  Applications d'un autre client (AH-11).

## 8. Ce qui n'a pas été essayé

À jouer avant de le promettre au client, sur sa tablette et sur
l'hébergement réel (partie 8.2 de la spécification, et ce que les tours ne
peuvent pas jouer) :
- **Enterprise** : écran de cuisine (`pos_preparation_display`), réservation
  de tables, et les deux sélecteurs d'écran visés par texte ou par position
  (« Fermer la caisse », libellé de « J'envoie ») ;
- une imprimante de cuisine réelle : le bon d'annulation imprimé et ce qui
  part avec lui ; « Bon d'annulation envoyé. » n'a jamais été vu ;
- deux postes réels sur la même table (« Commande dépassée » et R29,
  annulation sur un poste resté sur une copie ancienne, même table libre
  ouverte à deux) ; le canal temps réel derrière l'hébergement ; R27 hors
  connexion ;
- le délai de 5 minutes et la minuterie de 30 s de l'écran de commande
  mesurés à l'écran (les tours appellent l'étape directement ; la minuterie
  du plan, elle, a été vue à l'écran) ;
- la taille des touches et des gros boutons sur la tablette du client, la
  lisibilité des couleurs, le temps de la requête de stock sur le réseau du
  client ;
- la lecture d'un code-barres GS1 ou de quantité ; une horloge de tablette
  déréglée ;
- les libellés d'Odoo restés en anglais hors de nos écrans (« Backend »,
  « Your logo » : AH-09) ;
- une imprimante de tickets réelle : l'addition et le bon de sortie
  d'espèces ont été joués avec une imprimante simulée (sans imprimante, Odoo
  affiche un aperçu : une touche de plus pour le fermer) ;
- les touches de la partie 3 ont été comptées dans Chrome à 1 280 × 800, pas
  sur la tablette du client ; le retrait d'un produit pas encore envoyé n'a
  été compté que ligne déjà sélectionnée (2 touches, pas 3) ;
- les trois comptes du §9.5 d'INSTALLATION créés à la main jusqu'au bout :
  la graine les crée par programme, avec les mêmes droits, et le scénario
  novice vérifie ces droits.

## 9. Tests de la livraison

Bases jetables, Odoo 18 Community, chaque base créée comme l'écran de
création (Cameroun, français, sans démonstration) ; une seule base, un seul
Odoo à la fois. Chiffres du rejeu final de la partie 6b (14/11/2026, après
la revue) ; ceux des incréments 1 à 6a sont dans les corps de leurs commits.
- **Installation à froid** des modules du restaurant (`pos_restaurant`,
  `pos_hr`, `aite_pos_restaurant`, `aite_pos_credit`, `aite_pos_analytics`) :
  sortie 0 en 64 s, 0 ligne ERROR ou WARNING d'Odoo ; la passerelle
  `aite_pos_analytics_hr` installée seule ; caisse « Restaurant » cochée
  (délai 60, refus des épuisés coché, vente sans table décochée) ; FCFA ;
  aucun modèle hôtelier ; favori « Ventes par famille » sans colonne.
- **Installation par l'écran** (développeur), en suivant
  `docs/INSTALLATION.md` §9 dans le navigateur (base créée par l'écran de
  création d'Odoo, modules activés par Apps) : 29 contrôles sur 31 du premier
  coup, les 2 écarts étant deux libellés de la fiche produit, corrigés dans
  le §9 ; ce parcours-là ouvrait les écrans par leur adresse.
- **Chemins de menus du §9 suivis clic par clic** (revue de 6b : trois
  chemins étaient faux, corrigés) : menu des applications, puis le menu,
  puis l'entrée, avec les comptes administrateur, manager, chef de salle et
  caisse de la graine : 22 contrôles OK, 0 erreur JavaScript (dont « Mettre
  à jour la liste des Apps » en mode développeur, les six réglages du bloc
  Restaurant, « Mettre la quantité à jour », « Niveau en caisse » et « Code
  caisse » sur la fiche d'un nouvel employé, la fenêtre du code à
  l'ouverture de la caisse par « Ouvrir la caisse »).
- **Tests Odoo** d'`aite_pos_restaurant`, `aite_pos_credit`,
  `aite_pos_analytics` et `aite_pos_analytics_hr`, sans mise à niveau : 440
  tests, 0 échec, 0 erreur, 39 tours de caisse réellement joués dans Chrome
  (« tour succeeded »), 0 ligne ERROR ou WARNING ; avec `aite_hotel_pos_link`
  installé : 481 tests, 0 échec, 39 tours ; seul test sauté : le kit
  (Fabrication absente).
- **`AiteParcoursTour`** : toutes les lignes de la partie 1.2 (partie 3),
  516 étapes ; il échoue bien si une mesure s'écarte de la partie 1.2 (essais
  du développeur : compte faux, valeur attendue fausse) et si la fenêtre de
  fermeture affiche encore « Cash entrant/sortant » (essai de la revue :
  rouge avant la correction).
- **Tours standard d'Odoo** (base en anglais, `pos_hr`, `pos_restaurant`,
  `pos_hr_restaurant`) : 43 tests, 0 échec, 55 tours ; une seule ligne
  ERROR, connue (bibliothèque `rlPyCairo` absente).
- **Scénario novice** (`dev/run_tests.sh restaurant`) : 154 vérifications,
  0 KO, sur la base de travail `aite_resto` créée par `dev/setup_env.sh
  --restaurant`, et sur une base où la caisse a servi puis fermé (session
  « Contrôle d'ouverture » en attente, cas qui rendait le script rouge avant
  la revue) ; audit des menus : 6 menus, aucun problème ; tests purs :
  vague 1 28, restaurant 29, socle 18 fichiers.
- **Garde-fous** : `dev/setup_env.sh --restaurant` sur une copie de la base
  hôtelière, ou sur une base sans restaurant, s'arrête en erreur sans rien y
  installer (modules, produits, comptes et caisses inchangés) ;
  `dev/run_tests.sh restaurant` refuse une base absente, hôtelière ou sans
  restaurant ; le mode hôtel refuse la base du restaurant.
- **Graine relancée** : rien n'est créé deux fois (mêmes comptes en base
  avant et après).
- **Non-régression de l'hôtel** : copie de la base de développement
  hôtelière, mise à niveau d'`aite_pos_credit` (migration 18.0.2.0.6 jouée)
  et d'`aite_pos_analytics` (18.0.2.1.4 → 18.0.2.1.6), 0 ligne ERROR ou
  WARNING, puis `dev/run_tests.sh` : scénarios 38, 36, 46 et 33
  vérifications, 0 KO, audit de 38 menus, « TOUT EST VERT ».
- **Captures** (`captures/restaurant/`, 23 images, 2,8 Mo) prises par
  `tests/restaurant/shots.py` sur une copie de la base du restaurant, 0
  erreur JavaScript, 0 ligne ERROR ou WARNING du serveur, regardées une à
  une.
- **Cahier de recette** régénéré : 249 cas dont 103 du domaine R, PDF de 23
  pages, totaux recalculés par LibreOffice.
- **Enterprise** : aucune base Enterprise n'était disponible ; rien n'y a
  été joué, rien n'a été simulé.
- `dev/run_tests.sh` n'a pas été joué sur la base de développement hôtelière
  elle-même, mais sur une copie jetable (consigne : la base de travail n'est
  jamais modifiée par les essais).

## 10. Points à valider par AITE

1. **Q17, délai de 5 minutes.** Le poste revient au plan verrouillé après
   5 minutes sans activité (partie 5). Question au client : « Acceptez-vous
   ce retour automatique, sachant que sans lui un poste laissé seul ne
   montre plus le plan ? »
2. **Encaissement par le manager à la place d'une caissière restée
   identifiée** (REST-02 critère 2, cas résiduel) : il doit toucher le nom en
   haut et taper son code. Garde-t-on ce geste, ou demande-t-on le code à
   chaque « J'encaisse » (4 touches de plus par encaissement) ?
3. **Passage en force d'un produit épuisé par un supérieur (19d)** : hors
   lot 1 ; en attendant, R11 fait enregistrer l'entrée de stock par le
   manager. Le client accepte-t-il d'attendre le lot 2 ?
4. **Compte de la caisse « Utilisateur »** : le plan se dessine dans la
   gestion et la réunion de tables passe seulement par « Déplacer ou
   réunir ». Valide-t-on ce choix, laissé ouvert dans le périmètre ?
5. **« Suivi des modifications de commandes » décoché** alors que le
   périmètre le cochait : le journal AITE le remplace. Le confirme-t-on au
   client ?
6. **Deux classements de familles** (familles de la caisse et catégories de
   produit) à tenir tant que le tableau de bord AITE et l'onglet « Par
   catégorie » lisent la catégorie de produit, et l'analyse s'ouvre par
   catégorie (familles par le favori). Les reprend-on au lot 2 ?
7. **Fermer au-delà de l'écart maximum** réservé au manager (Q8) ; **Mobile
   Money** créé comme mode manuel, sans « Carte » (Q56). Valide-t-on ces deux
   choix par défaut ?
8. **Enterprise** : quand et sur quelle base joue-t-on le tour de fumée
   (écran de cuisine, réservation de tables, deux sélecteurs par texte ou
   position) avant la livraison ?
9. **Droit Facturation du manager** : sans lui, Odoo refuse le rapport de
   session dès qu'une vente est payée. L'ajoute-t-on à la partie 4.4 de la
   spécification (il est déjà dans la graine et dans INSTALLATION) ?
10. **Qui règle la caisse** : la case, le délai de l'orange, la vente sans
    table et le refus des épuisés sont dans les réglages du Point de Vente,
    réservés à l'administrateur d'Odoo. AITE garde-t-il ces réglages, ou
    donne-t-on au manager l'accès aux réglages ?
11. **« Articles » décimal et montants sans « FCFA »** dans le tableau croisé
    (format d'Odoo) : passe-t-on « Articles » en entier (au prix des
    quantités pesées), et accepte-t-on l'affichage des montants ?
12. **Caisses mêlées** : les ventes d'une caisse hors service à table
    comptent dans « Ventes sans table » et « Personnes et tables ».
    Le dit-on au client, ou filtre-t-on ces rapports par caisse ?
13. **Qui est « la gestion »** pour une trace sans code : la tablette doit
    être ouverte sous le compte de la caisse, et une addition supprimée depuis
    la liste de la gestion par ce même compte est au nom de l'employé de
    l'addition. Est-ce acceptable ?
14. **Prix et remise d'une ligne envoyée** non surveillés (requête forgée) :
    garde-t-on cette limite, ou trace-t-on au lot 2, et comment distinguer
    alors les vrais changements de prix du manager ?
15. **Refus des épuisés fait par le poste seul** : garde-t-on la limite, ou
    ajoute-t-on au lot 2 une note dans l'historique de l'addition quand une
    synchronisation fait passer le disponible sous zéro ?
16. **Relecture du stock quand la quantité demandée dépasse le reste connu**
    (écart léger à T20, qui ne relisait qu'à 2 ou moins) : la valide-t-on ?
17. **« Tableau » au lieu de « Table »** dans la barre du plan, constaté aussi
    sur un restaurant seul, de façon instable (avant le premier service, puis
    plus après) : le client du restaurant comme le client pilote peuvent le
    voir. Le traite-t-on avant la livraison du lot 1, ou avec les
    traductions (AH-09, lot 2) ?
18. **Textes ajoutés hors spécification** : « Pas de quantité négative sur
    une addition : pour retirer un produit, touchez ⌫. » (titre « Quantité
    négative ») ; « Demande d'annulation incomplète. » ; « Motif inconnu :
    rouvrez la fenêtre d'annulation. » ; « Le délai avant l'orange doit être
    d'au moins 1 minute. » ; le libellé « Ce qui va se passer ». Les
    valide-t-on tels quels ?
19. **Deux journaux « Espèces »** (celui du plan comptable et celui de la
    caisse posée d'office), cause aussi de l'erreur du test d'Odoo
    `test_report_listing` : n'en garde-t-on qu'un ?
20. **Ardoises signalées par la migration 18.0.2.0.6** chez le client pilote
    (déjà remboursées, ou rattachées à une addition encore ouverte) : qui les
    reprend, et quand ?
21. **Livraison au client pilote** : lui livre-t-on maintenant
    `aite_pos_credit` 18.0.2.0.6 (AH-01 change la naissance des ardoises),
    `aite_pos_analytics` 18.0.2.1.6 et la correction d'`aite_hotel_pos_link`
    (version inchangée, redémarrage seul) ?
22. **Passerelle installée à la main** sur une base où l'analyse et le
    restaurant étaient déjà installés : acceptable, ou prévoit-on une
    installation automatique à la mise à niveau ?
23. **Noms hérités du client pilote** dans les fiches d'applications et les
    cartes (AH-11 : « AITE — POS Analytics (LAVERANDAH) », « Top bières »,
    « Consignes d'emballages ») et **étude comparative** (AH-10) : les
    corrige-t-on avant toute présentation au client du restaurant ?
24. **TVA de la carte** : Odoo pose d'office sur chaque nouveau produit la TVA
    de 19,25 % hors taxes (un prix de 1 000 FCFA est encaissé 1 193 FCFA,
    constaté sur une base neuve) ; la graine de démonstration ne pose aucune
    taxe. Quelle taxe « prix TTC » AITE règle-t-il avec le comptable du client
    avant la saisie de la carte ?
25. **Essais sur place** (partie 8 ci-dessus) : quand les joue-t-on sur la
    tablette et l'hébergement du client, imprimantes de cuisine et deux
    postes compris ?
26. **Changer la case ou la vente sans table sur une caisse déjà utilisée** :
    après chaque fermeture, la tablette rouvre une session « Contrôle
    d'ouverture » qui grise ces deux réglages, et l'administrateur ne peut pas
    la supprimer. Accepte-t-on cette contrainte d'Odoo (faire ces réglages
    avant la mise en service), ou faut-il un moyen de les changer ensuite ?
27. **Compte de la notification « Envoyé : … »** : par famille la plus fine
    du produit, comme les compteurs du bouton « J'envoie » d'Odoo (« 1 Pizzas,
    2 Bière ») ; le nom de la famille est repris tel quel, d'où « 1 Pizzas ».
    Garde-t-on ce compte, ou compte-t-on par famille de premier niveau
    (« 1 Nourriture, 2 Boisson », l'exemple de la partie 1.4) ?
