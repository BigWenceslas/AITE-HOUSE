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

Une seule source, `demo.py`, pour que le même séjour traverse la vidéo :
Estelle Ngono, réservation `RES/2026/0214`, folio `FOL/2026/0214`, chambre
`204 [CFT]` (Confort, 45 000 FCFA la nuit), du 14/10 au 16/10/2026, dans le
« Complexe Hôtelier — Démo » (3 ★, Cameroun) de « Démo Hôtellerie SARL ».
Claire Durand réserve le salon VIP Wouri en ligne ; on retrouve sa
réservation dans le planning des espaces de la direction.

Les personnes sont **fictives**, une par poste : Mireille Ateba (réception),
Josiane Fouda (gouvernante, avec Clarisse et Sidonie), Hervé Tchakounté (caisse du
bar), Claire Durand (cliente), Serge Nana (magasin), Danielle Eyenga
(direction). Les jeux d'essai de recette et les données du client pilote
n'apparaissent jamais.

## Ouverture et fin

Le logo AITE Consulting (jamais redessiné) sur une carte blanche, « AITE
HOUSE », « Suite hôtelière sur Odoo 18 ». En fin de vidéo : le logo, le
titre du cahier de recette et la signature « AITE Consulting · Douala ·
aite-consulting.com ».

## Son

La voix off d'abord (Kokoro, voix française féminine `ff_siwis`, −16 LUFS).
Deux bruitages seulement, synthétisés par `sons.py` : un souffle et deux notes
à l'ouverture, un clic discret à chaque clic du curseur. Pas de musique.
