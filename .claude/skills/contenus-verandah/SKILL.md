---
name: contenus-verandah
description: Rédige et produit les visuels réseaux sociaux de La Vérandah (cave · lounge · restaurant à Makepe, Douala) — vœux du mois, annonces, ambiance après le travail et week-end, mise en avant de la cave, photo pleine page avec programme — au format carré, portrait ou story, avec la légende et les hashtags. À utiliser dès qu'il est question d'une publication, d'une affiche, d'un flyer, d'un statut WhatsApp ou d'un post Facebook ou Instagram pour La Vérandah ou La Verandah : « fais un post pour la Verandah », « bon mois de décembre pour la Verandah », « mets nos whiskies en avant », « une affiche pour vendredi soir ».
---

# Contenus de La Vérandah

Le studio est dans `studio-contenus/` (lire la section « La Vérandah » de son
`README.md`). Tout visuel passe par son moteur (`src/rendu-verandah.js`).

## Produire une publication

1. Choisir le modèle : `vd-annonce` (vœux, annonce), `vd-ambiance` (invitation,
   ambiance), `vd-carte` (sélection de la cave), `vd-photo` (photo pleine page et
   programme). Champs et longueurs : voir les libellés du studio (`champs` de
   chaque modèle dans `src/rendu-verandah.js`).
2. Ajouter l'entrée à `studio-contenus/contenus/verandah.json` (`id` du type
   `VD-JJ-MM-jour`, `alcool: false` pour un visuel qui ne parle pas d'alcool).
3. Générer : `cd studio-contenus && node generer.js studio --marque verandah && node generer.js visuels --marque verandah --id <id> --format tous`.
4. Regarder l'image dans `sortie/verandah/` avant de la présenter, puis livrer
   l'image et la légende prête à coller.

## Règles

- Faits connus uniquement : nom, cave · lounge · restaurant, adresse (Makepe, en face
  de l'église Sainte Monique), appels et WhatsApp 656 80 10 98, produits vus sur les
  affiches (Guinness, Heineken, Jack Daniel's, Johnnie Walker Red Label, Chivas
  Regal 12 ans, Moët & Chandon, Ruinart, vins rouges, blancs et rosés). Horaires,
  prix, plats, soirées, terrasse, livraison : seulement si le gérant les donne.
- Pas de chicha dans les publications, pas d'incitation à boire, pas d'alcool au
  volant, pas de mineurs. Mention santé sur tout visuel et toute légende qui parlent
  d'alcool : « L'abus d'alcool est dangereux pour la santé. À consommer avec modération. »
- Ton chaleureux et convivial, français naturel de Douala, sans superlatif mensonger.
  Ce n'est pas AITE Consulting : pas de mention d'AITE ni de son DG.
- Hashtags : #LaVerandah, #Douala, #Makepe…, en CamelCase sans accents.
