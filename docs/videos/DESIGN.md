# AITE HOUSE — charte de la vidéo

Sources de vérité : les couleurs d'Odoo 18 (barre et boutons `#71639E`, fond
`#F8F9FA`), celles des tableaux de bord AITE (`#714B67` sur `#E8E6E0`, relevées
dans les `scss` des modules `aite_*_dashboard`), le logo AITE Consulting
(`docs/logo_aite.jpg`) et les captures de recette (`docs/captures_uat/`,
`captures/`) pour la forme des écrans. Les valeurs complètes sont dans
`shared/aite.css`.

## Le ton

Un outil d'hôtellerie, calme et sûr de lui. Le violet profond porte les
scènes ; l'orange du logo ne sert qu'à désigner : le chapitre en cours,
l'étape, le geste à faire. Pas d'effet pour l'effet : l'interface est rejouée
telle qu'elle est.

## Palette

| Rôle | Valeur | Origine |
|---|---|---|
| Fond des scènes | dégradé violet profond | dérivé du violet AITE `#902C8F` |
| Désigner (anneau, chapitre actif) | `#ED9720` | orange du logo AITE |
| Accent secondaire | `#3198BB` | bleu du logo AITE |
| Barre d'Odoo, bouton primaire | `#71639E` | Odoo 18 |
| Fond des vues Odoo | `#F8F9FA` | Odoo 18 |
| Titres et puces des tableaux de bord AITE | `#714B67` sur `#E8E6E0` | modules `aite_*_dashboard` |

Toutes les teintes de texte passent le contraste WCAG AA vérifié par
`hyperframes check`.

## Typographie

Inter seule, graisses 400 à 800 (copiée depuis les polices du système dans le
projet). Les montants en chiffres tabulaires.

## Échelle

La fenêtre d'Odoo occupe 1792 × 860 px de l'image 1920 × 1080 ; l'interface
est rejouée à environ ×1,25 de sa taille d'écran, assez grande pour se lire
sur un téléphone.

## Règles dures

- Pas de capture d'écran incrustée, pas d'émoji : les icônes sont des SVG.
- Un changement d'état est un changement de classe (statusbar, pastille,
  carte), jamais un fondu de couleur.
- Une seule action désignée à la fois : un clic, ou un anneau orange.
- Les boutons suivent les conditions d'affichage du code (« Rouvrir » remplace
  « Enregistrer un remboursement » sur une ardoise réglée).

## Données de démonstration

Une seule source, `demo.py`, et la fiche d'harmonisation de la série, pour
que le même séjour traverse les chapitres et les tutoriels : Estelle Ngono,
réservation `RES/2026/0214`, folio `FOL/2026/0214`, chambre `204 [CFT]`
(Confort, 45 000 FCFA la nuit), du 14/10 au 16/10/2026, dans le « Complexe
Hôtelier — Démo » (3 ★, Cameroun) de « Démo Hôtellerie SARL ». Jour de
référence : le mercredi 14/10/2026.

L'hôtel compte **20 chambres vendables** : 101-107 [STD] au rez-de-chaussée
(la 105 hors service), 201-206 [CFT] au 1er étage, 301-304 [SJR] au 2e,
401-403 [VIP] au 3e ; Standard 35 000, Confort 45 000, Suite Junior 75 000,
Suite VIP 120 000 FCFA la nuit. La société de démonstration est **sans
TVA** : hébergement, bar, restaurant et achats s'affichent HT = TTC ; seule
la taxe de séjour (3 000 FCFA par personne et par nuit, 3 ★) s'ajoute au
folio. Le folio d'Estelle : 102 000 FCFA, acompte MTN Mobile Money de
45 000, 57 000 FCFA dus.

La base est **mono-société**, comme celle du client : chaque profil n'a
accès qu'à « Démo Hôtellerie SARL ». Odoo 18 affiche quand même le nom de
la société dans la barre du haut (sélecteur désactivé,
`web/static/src/webclient/switch_company_menu/switch_company_menu.js:287-296`),
mais ne donne le groupe `base.group_multi_company` qu'aux utilisateurs qui
ont plusieurs sociétés (`odoo/addons/base/models/res_users.py:1907-1914`).
Aucun élément de vue réservé à ce groupe ne s'affiche donc : ni « Hôtel »
au folio ou dans la liste des réservations, ni « Société » sur une fiche
(capture de référence du profil Réception : `ref_muk/306`).

Seule exception à l'image : la barre « Hôtel » du profil Direction (neuf
menus, chapitres c6 et c7 de la présentation) n'a pas la place du nom de la
société. Odoo rangerait les derniers menus sous « + »
(`web/static/src/webclient/navbar/navbar.js:120-190`), ce qui cacherait
« Configuration », que c7 ouvre au premier geste ; la vidéo garde les menus
et omet le nom.

Claire Durand réserve en ligne le salon VIP Wouri pour le samedi 17/10 à
16:00 (`CRN/2026/0131`) ; on retrouve sa réservation dans le planning des
espaces de la direction. Les réservations de créneaux portent le préfixe
`CRN/` et l'année sur quatre chiffres depuis la livraison 4
(`demo.CRENEAU_SALON`, `CRENEAU_MASSAGE` `CRN/2026/0158`,
`CRENEAU_PRESSING` `CRN/2026/0141`) ; les séjours restent en `RES/2026/…`.

Les nombres s'écrivent comme le produit depuis la livraison 4 (helpers de
`ecrans.py`) : montants « 45 000 FCFA » (`fcfa`), pourcentages à une
décimale fixe « 56,0 % » (`pct`), variations « ▲ +12,5 % », « ▼ 3,0 % »,
« ■ 0,0 % » en gris (`variation`, `kpi(delta=…)`), durées « 12,3 j »
(`jours`), âges « 160 j » (`age`), mots accordés sans « (s) » (`compte`),
dates « 14/10/2026 » (`date_fr`), mois « sept. » / « octobre 2026 »
(`mois_abrege`, `mois_long`). Champs d'Odoo : espace insécable entre les
milliers ; tableaux de bord AITE : espace fine (`tdb=True`). Les barres de
menus de chaque profil sont dans `ecrans.MENUS_MUK` (« Réception », et non
plus « Front Desk » ; « Activité par pôle », et non plus « Direction »).

Les personnes sont **fictives**, une par poste : Mireille Ateba (réception),
Josiane Fouda (gouvernante, avec Clarisse et Sidonie), Hervé Tchakounté (caisse du
bar), Claire Durand (cliente), Serge Nana (magasin), Danielle Eyenga
(direction). Les jeux d'essai de recette et les données du client pilote
n'apparaissent jamais (pas de « Paul Durand », nom des seeds). Les
téléphones sont des **numéros de fiction** : « +237 6 00 00 00 xx » (deux
chiffres finaux propres à chaque personne : Estelle 01, l'hôtel 10) et, pour
Claire, la plage française réservée à la fiction (+33 6 39 98 21 47) ;
adresses `exemple.cm` / `exemple.fr`.

## Le restaurant (tutoriels 16 à 23)

Les tutoriels du restaurant (lot 1 : `aite_pos_restaurant`, `aite_pos_analytics`,
`aite_pos_analytics_hr`) montrent un **restaurant sans hôtel** : le module ne
dépend pas du socle hôtelier et n'est pas installé chez le client pilote de
l'hôtel. Autre établissement, autre société, autre barre d'applications ; la
même charte, le même thème MuK, le même jour de référence (14/10/2026).
Données : `demo.py`, bloc « le restaurant ».

- Établissement fictif **« Café-Restaurant — Démo »** (pizza, café, petit
  déjeuner, bar et cuisine) de **« Démo Restauration SARL »**, téléphone
  `+237 6 00 00 00 50` (la plage 50-59 est réservée au restaurant). Base
  mono-société, **sans TVA**, comme toute la série : une base créée au
  Cameroun pose pourtant une TVA de 19,25 % hors taxes (`docs/INSTALLATION.md`
  §9.6, point 2) ; la vidéo suppose qu'AITE a réglé la carte « sans taxe »
  avec le comptable.
- La caisse « Restaurant », la salle « Salle », les modes « Espèces » et
  « Mobile Money » : les noms que le module pose à l'installation.
- L'équipe, fictive, prénom seul sur la fiche et à la caisse : **Edwige
  Bilongo** (manager), **Prisca Tamo** (caissière), **Loïc Ewodo** (serveur),
  **Inès Fotabong** (serveuse), **Landry Essola** (chef de salle) ; codes
  caisse de quatre chiffres « tirés au hasard ». Aucun nom du jeu d'essai
  (`dev/seeds/seed_restaurant.py`), des captures ni de la série hôtelière ;
  les noms ont été cherchés dans tout le dépôt. Les réglages du Point de
  Vente sont joués sous le compte de l'administrateur d'Odoo (AITE), sans
  nom de personne.
- La salle : douze tables, disposées comme le jeu d'essai (rangée de quatre
  tables carrées, rangée de quatre rondes, puis 9 et 10 plus larges, 11 et
  12) ; les familles sur trois niveaux, Nourriture (Pizzas, Petit déjeuner,
  Plats) et Boisson (Alcoolisé : Bière, Vin, Whisky ; Non alcoolisé : Sodas,
  Café), aux couleurs d'Odoo relevées sur la base du restaurant (7 et 8) ;
  une carte de 18 articles génériques, **sans aucune marque** (le jeu d'essai
  et les captures portent de vraies marques de boissons) ; seules les bières
  sont suivies en stock.
- La caisse plein écran est rejouée par `ecrans.py` (« La caisse du
  restaurant ») : plan en couleurs (gris libre, vert ouverte, orange après le
  délai, pastille rouge), fenêtre du code, écran de commande par familles,
  annulation, paiement, menu ≡, ouverture et fermeture de la caisse, rapport
  de fermeture ; styles `shared/aite-marketing.css` (classes `rs-*`, `rg-*`,
  `fe-*`). Ce qui suit la couleur primaire d'Odoo prend le bleu acier de MuK
  (le thème habille aussi la caisse) ; les couleurs codées en dur par AITE et
  par Odoo (tables, légende, pavé, familles, notifications) restent telles
  quelles, sauf les gris des éléments inactifs (« Addition » et « Note cuisine »
  grisés, « % » et « Prix », « J'envoie » sans rien à envoyer, la quantité d'une
  tuile), un ton plus foncés que le rendu d'Odoo pour le contraste WCAG AA du
  contrôle (`aite-marketing.css`, relectures de t17 à t20). Échelle : la caisse fait 1 720 px de large, 1,34 fois la tablette
  de 1 280 points des captures (barres, boutons, fenêtres), mais 796 px de
  haut pour 800 points : le cadre est plus large que la tablette. Le plan est
  donc rejoué **×1,05** (une table de 120 points fait 126 px), tassé en
  hauteur pour tenir avec le bandeau et la légende : il occupe la moitié de
  la largeur de la caisse, contre les deux tiers sur la tablette. La fenêtre
  du code s'ouvre à 205 px du haut de la caisse, sous la ligne de texte du
  bandeau (capture 01), et non au centre.
- Le monde de la série : la caisse a une imprimante de tickets (« Addition »
  imprime), mais **pas d'imprimante de préparation**, comme les captures et les
  tours (`R/tests/test_tours.py:41-43`) ; la pastille rouge compte donc tous les
  produits pas encore envoyés. Le bon d'annulation et la phrase « Bon
  d'annulation envoyé. » ne sont montrés dans aucun tutoriel tant qu'ils n'ont
  pas été vus sur une imprimante réelle (notes de version §8 ; t19 : `BON_VU`).
- La journée du 14/10 en salle (qui ouvre quelle table, à quelle heure, ce
  qu'elle porte, ce qui en est sûr) est dans `demo.TABLES_JOUR_RESTO`, le journal
  des annulations dans `demo.ANNULATIONS_JOUR_RESTO`, le fond de caisse dans
  `demo.FOND_RESTO` : t21 à t23 les reprennent. Midi (t17 à t19), puis le
  service du soir (t20 : la table 10 rouverte par Inès).
- La fin des tutoriels du restaurant dit « Caisse de restaurant sur Odoo 18 »
  (`demo.SOUS_MARQUE_RESTO`) au lieu de « Suite hôtelière sur Odoo 18 ».
- Les textes de la caisse sont recopiés de `static/src/utils/messages.js`
  (`ecrans.MESSAGES_RESTO`, `TITRES_RESTO`, `TEXTES_RESTO`, espace insécable
  comprise) ; les phrases des réglages et de la fiche employé sont relues
  dans le code du module au chargement du scénario.

## Ouverture et fin

Le logo AITE Consulting (jamais redessiné) sur une carte blanche, « AITE
HOUSE », « Suite hôtelière sur Odoo 18 ». En fin de vidéo : le logo, le
titre du cahier de recette et la signature « AITE Consulting · Douala ·
aite-consulting.com ».

## Son

La voix off d'abord (Kokoro, voix française féminine `ff_siwis`, −16 LUFS).
Deux bruitages seulement, synthétisés par `sons.py` : un souffle et deux notes
à l'ouverture, un clic discret à chaque clic du curseur. Pas de musique.
