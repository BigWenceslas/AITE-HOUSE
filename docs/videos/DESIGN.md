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

## Ouverture et fin

Le logo AITE Consulting (jamais redessiné) sur une carte blanche, « AITE
HOUSE », « Suite hôtelière sur Odoo 18 ». En fin de vidéo : le logo, le
titre du cahier de recette et la signature « AITE Consulting · Douala ·
aite-consulting.com ».

## Son

La voix off d'abord (Kokoro, voix française féminine `ff_siwis`, −16 LUFS).
Deux bruitages seulement, synthétisés par `sons.py` : un souffle et deux notes
à l'ouverture, un clic discret à chaque clic du curseur. Pas de musique.
