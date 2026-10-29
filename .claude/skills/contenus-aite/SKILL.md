---
name: contenus-aite
description: Rédige et produit les visuels réseaux sociaux d'AITE Consulting signés par le Directeur Général avec sa photo — citations, affiches de motivation, conseils pratiques numérotés, pensées sur fond sombre avec photo ronde, annonces de recrutement — au format carré, portrait ou story, avec la légende du post et les hashtags. À utiliser dès qu'il est question d'un post LinkedIn, Facebook ou Instagram d'AITE, d'une citation ou pensée du DG, d'une phrase de motivation, d'un conseil pratique à publier, d'une offre d'emploi ou d'un flyer de recrutement, du calendrier éditorial ou du studio de contenus : « fais une citation sur la délégation », « un conseil sur les sauvegardes », « prépare les posts de la semaine », « refais le visuel du mercredi en story ».
---

# Contenus réseaux sociaux AITE

Le studio est dans `studio-contenus/` (lire son `README.md`). Tout visuel passe par
son moteur : ne pas dessiner de visuel à la main ni avec un autre outil.

**Avant d'écrire, lire `references/ligne-editoriale.md`** : la ligne tirée de la stratégie
commerciale et marketing du DG. Elle prime sur les règles plus anciennes ci-dessous. En bref :
écrire pour le décideur qui signe (coûts, délais, risques, comparatifs, preuves), enseigner
quelque chose à chaque publication, citer uniquement les références et chiffres de la plaquette,
et finir chaque légende par l'appel à l'action unique (Diagnostic Digital 360°, WhatsApp).
Le DG a rejeté les publications « juste motivation » et les conseils génériques sans lien avec
une décision d'achat.

## Produire une publication

1. Rédiger selon les règles ci-dessous, en choisissant le modèle :
   - `affiche` : une phrase de motivation, 18 à 75 caractères ;
   - `conseil` : `titre` de 20 à 58 caractères, 3 ou 4 `points` de 25 à 90 caractères
     commençant par un impératif (vouvoiement), `numero` = suivant du calendrier ;
   - `citation` : une pensée du DG, 70 à 190 caractères ;
   - `sombre` : même usage qu'une citation (une pensée, 40 à 190 caractères), en version
     sobre sur fond sombre, photo du DG en médaillon rond ;
   - `recrutement` : offre d'emploi. `titre` = intitulé du poste (relief sur 1 ou 2 mots),
     `texte` = 2 ou 3 étiquettes séparées par « · » (lieu, secteur), `etiquette` = pastille
     (« Nous recrutons »), `points` = rubriques `# Vos missions`, `# Votre profil`, puis
     `# Pour postuler` (affichée en encadré : e-mail en relief, objet du mail). 4 points
     au plus par rubrique, 60 caractères au plus chacun ; le détail va dans la légende.
     Ne rien promettre (contrat, salaire, avantages, dates) que la direction n'a pas
     confirmé : lister ces points à faire valider en livrant le visuel.
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
  ni aucune formule d'un autre auteur n'est attribué au DG. Une citation célèbre peut être
  publiée (modèle `sombre`, champ `auteur` : « — Sénèque, Lettres à Lucilius ») si son
  attribution est confirmée par une source fiable (œuvre précise, Wikiquote hors
  « attribuées », Quote Investigator) ; écarter les citations apocryphes.
- Aucun chiffre, statistique ou nom de client inventé : seuls les références et chiffres
  de la plaquette (liste dans `references/ligne-editoriale.md`) sont publiables. Pas de
  superlatifs, pas de jargon (« synergie », « disruptif », « booster »), pas de clichés de
  développement personnel, jamais « nous sommes leaders ». Conseils exacts et prudents.
- Légende : 450 à 900 caractères en 3 paragraphes (ce que le décideur apprend, le concret
  et la preuve, l'appel à l'action Diagnostic Digital 360° par WhatsApp), au plus un emoji.
  4 à 6 hashtags en CamelCase sans accents, dont `#AITEConsulting` et un mot-clé local
  (`#Douala`, `#Cameroun`).
- Devise maison, citable telle quelle : « On ne vend pas de la technologie, on vend la
  fin d'un problème de gestion. »

Signature par défaut : Cyrille Donald ABOLO, Directeur Général, AITE Consulting
(champ `signature` de `publications.json`).
