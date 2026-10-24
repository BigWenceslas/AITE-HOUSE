---
name: contenus-aite
description: Rédige et produit les visuels réseaux sociaux d'AITE Consulting signés par le Directeur Général avec sa photo — citations, affiches de motivation du lundi, conseils pratiques numérotés — au format carré, portrait ou story, avec la légende du post et les hashtags. À utiliser dès qu'il est question d'un post LinkedIn, Facebook ou Instagram d'AITE, d'une citation ou pensée du DG, d'une phrase de motivation, d'un conseil pratique à publier, du calendrier éditorial ou du studio de contenus : « fais une citation sur la délégation », « un conseil sur les sauvegardes », « prépare les posts de la semaine », « refais le visuel du mercredi en story ».
---

# Contenus réseaux sociaux AITE

Le studio est dans `studio-contenus/` (lire son `README.md`). Tout visuel passe par
son moteur : ne pas dessiner de visuel à la main ni avec un autre outil.

## Produire une publication

1. Rédiger selon les règles ci-dessous, en choisissant le modèle :
   - `affiche` : une phrase de motivation, 18 à 75 caractères ;
   - `conseil` : `titre` de 20 à 58 caractères, 3 ou 4 `points` de 25 à 90 caractères
     commençant par un impératif (vouvoiement), `numero` = suivant du calendrier ;
   - `citation` : une pensée du DG, 70 à 190 caractères.
   Mettre en relief 1 à 4 mots avec des astérisques simples, une seule fois par texte.
2. Ajouter l'entrée à `studio-contenus/contenus/publications.json` (même structure
   que les autres, `id` du type `S11-lundi`, photo différente de la publication
   précédente : `boubou`, `blazer` ou `tunique`).
3. Générer : `cd studio-contenus && node generer.js studio && node generer.js visuels --id <id>`
   (`--format tous` pour le portrait et la story).
4. Regarder l'image produite dans `sortie/` avant de la présenter : texte lisible,
   rien de coupé, relief au bon endroit. Corriger le texte plutôt que le moteur.
5. Livrer l'image et la légende prête à coller, hashtags compris.

## Règles d'écriture

- Voix du DG : dirigeant pragmatique, exigeant et bienveillant, qui parle de terrain
  (PME, hôtels, administrations, équipes). Français impeccable, accents sur les
  majuscules, phrases courtes, verbes d'action.
- Citations **originales** : vérifier qu'aucune citation célèbre, aucun proverbe connu
  ni aucune formule d'un autre auteur n'est attribué au DG.
- Aucun chiffre, statistique ou nom de client inventé ; pas de superlatifs, pas de
  jargon (« synergie », « disruptif », « booster »), pas de clichés de développement
  personnel. Conseils techniques exacts et prudents.
- Légende : 350 à 750 caractères, 2 ou 3 paragraphes (accroche, situation vécue,
  question ouverte), au plus un emoji ; au plus une légende sur trois mentionne AITE.
  3 à 6 hashtags en CamelCase sans accents (`#AITEConsulting`, `#TransformationDigitale`).
- Devise maison, citable telle quelle : « On ne vend pas de la technologie, on vend la
  fin d'un problème de gestion. »

Signature par défaut : Cyrille Donald ABOLO, Directeur Général, AITE Consulting
(champ `signature` de `publications.json`).
