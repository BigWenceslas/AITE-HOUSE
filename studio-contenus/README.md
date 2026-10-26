# Studio de contenus AITE Consulting

Visuels pour LinkedIn, Facebook et Instagram, signés par le Directeur Général
d'AITE Consulting et illustrés de sa photo : **citations**, **affiches de
motivation** et **conseils pratiques**, aux couleurs de la charte AITE (violet
`#8E2A8E`, orange `#F0921F`, bleu `#2E8CB2`, Space Grotesk et IBM Plex Sans).

| Modèle | Usage | Jour proposé |
|---|---|---|
| **Affiche** | une phrase courte de motivation, en grand, sur fond violet | lundi |
| **Conseil** | un titre et 3 ou 4 conseils numérotés, applicables dès demain | mercredi |
| **Citation** | une pensée du DG, entre guillemets, dans le panneau violet | vendredi |
| **Fond sombre** | une pensée centrée en lettres fines sur fond sombre, le mot clé en gras souligné d'orange, la photo du DG en médaillon rond | au choix |

Le week-end, le ton change (détente et sourire le samedi, repos le dimanche) avec
les mêmes modèles et une étiquette adaptée : « Samedi détente », « Dimanche repos »…

Chaque modèle existe en trois formats : **carré** 1080 × 1080 (fil LinkedIn,
Facebook, Instagram), **portrait** 1080 × 1350 (le plus visible sur Instagram
et LinkedIn mobile) et **story** 1080 × 1920.

## La Vérandah

Le même studio produit aussi les visuels de **La Vérandah** (cave · lounge ·
restaurant, Makepe, en face de l'église Sainte Monique) : ouvrir
**`studio-verandah.html`**. Quatre modèles aux couleurs de ses affiches (crème,
rouge vin, vert, écriture manuscrite et capitales condensées), plus une
« Pensée » sur fond sombre avec la photo ronde du promoteur :

| Modèle | Usage |
|---|---|
| **Annonce** | vœux et annonces : ligne manuscrite rouge, grandes capitales vertes |
| **Ambiance** | invitation, après le travail, week-end : fond de bar, logo dans un panneau blanc |
| **La cave** | une sélection de bouteilles, prix facultatifs (`Produit \| 15 000 FCFA`) |
| **Photo** | photo pleine page, titre en capitales fines, programme en bas (`18h : …`) |
| **Pensée** | le modèle « fond sombre » d'AITE aux couleurs de La Vérandah : pensée centrée, mot clé souligné d'or, photo ronde et nom |

Les publications sont dans `contenus/verandah.json`, les visuels dans
`sortie/verandah/` (`node generer.js --marque verandah --format tous`). Les photos
déposées dans `assets/verandah/photos/` (JPEG, PNG ou WebP) apparaissent dans le
studio, suivies des photos détourées du promoteur (pour la « Pensée ») ; on
peut aussi en importer une directement. Le nom et la mention sous la photo ronde
viennent du champ `signature` de `contenus/verandah.json`. La mention « L'abus d'alcool est
dangereux pour la santé » s'ajoute d'office ; la décocher pour un visuel sans alcool.
Le logo de `assets/verandah/logo/` est provisoire (extrait d'une affiche) : le
remplacer par le fichier d'origine dès qu'il est disponible.

## Utiliser le studio (sans rien installer)

Ouvrir **`studio.html`** dans Chrome, Edge, Firefox ou Safari, d'un double-clic.
Le fichier contient tout (polices, logo, photos, calendrier) et fonctionne hors
connexion, sur ordinateur comme sur téléphone.

1. **Calendrier** : choisir une des publications prêtes, ou « Nouvelle publication ».
2. **Modèle** et **format** : citation, affiche ou conseil ; carré, portrait ou story.
3. **Texte** : entourer d'astérisques les mots à mettre en relief
   (`On vend *la fin d'un problème de gestion*.`) ; ils passent en orange.
   Les espaces avant `: ; ! ?` et dans les guillemets « » sont posées
   automatiquement.
4. **Photo** : une des trois photos détourées, une photo importée, ou aucune.
5. **Télécharger en PNG** (ou « Les 3 formats »). Sur téléphone, « Voir en
   grand » puis appui long sur l'image pour l'enregistrer.
6. **Copier la légende** : le texte du post et ses hashtags, à coller sous le visuel.

Le travail en cours est conservé dans le navigateur d'une ouverture à l'autre.

## Le calendrier prêt à publier

`contenus/publications.json` contient 30 publications rédigées (10 semaines,
lundi, mercredi, vendredi), chacune avec sa légende et ses hashtags.
Les visuels correspondants sont déjà générés dans `sortie/`, et
**`sortie/CALENDRIER.md`** les présente semaine par semaine avec la légende à
copier.

## Règles éditoriales

- Citations **originales** : jamais une citation célèbre ni un proverbe connu
  attribué au DG.
- Aucun chiffre, pourcentage ou nom de client inventé ; pas de superlatifs ni de
  jargon (« synergie », « booster »…).
- Phrases courtes, verbes d'action, vouvoiement dans les conseils.
- Longueurs qui rendent bien : citation 70 à 190 caractères ; affiche 18 à 75 ;
  conseil : titre de 20 à 58 caractères et 3 ou 4 points de 25 à 90 caractères.
  Le studio affiche un compteur et réduit la taille du texte au besoin.
- Une seule mise en relief par texte, de 1 à 4 mots.

## Générer les visuels en lot

Pour régénérer `sortie/` après avoir modifié `contenus/publications.json`
(Node.js 18 ou plus) :

```bash
cd studio-contenus
npm install                     # une fois : installe Playwright
npx playwright install chromium # une fois
node generer.js                 # reconstruit studio.html et génère tous les visuels carrés (JPEG)
node generer.js visuels --format tous          # carré, portrait et story
node generer.js visuels --id S03-mercredi      # une seule publication
node generer.js visuels --png --echelle 2 --dossier ../visuels-hd   # PNG 2160 px, hors du dépôt
node generer.js studio                         # seulement studio.html
```

Une publication dans `contenus/publications.json` :

```json
{
  "id": "S01-vendredi", "semaine": 1, "jour": "vendredi",
  "modele": "citation", "theme": "devise", "etiquette": "",
  "texte": "On ne vend pas de la technologie. On vend *la fin d'un problème de gestion*.",
  "titre": "", "points": [], "numero": null,
  "photo": "tunique",
  "legende": "Texte du post…", "hashtags": ["#AITEConsulting", "#Gestion"]
}
```

Champs facultatifs : `serie` range la publication hors des semaines
numérotées (ex. `"serie": "Week-end"`), `moment` indique l'heure conseillée
(`"samedi 10h"`) ; tous deux apparaissent dans le studio et dans `CALENDRIER.md`.

`modele` vaut `citation`, `affiche`, `conseil` ou `sombre` ; `photo` est le nom d'un
fichier de `assets/photos/` sans extension (`boubou`, `blazer`, `tunique`), ou
`null`. Pour un conseil, remplir `titre`, `points` et `numero`, et laisser
`texte` vide ; `"puces": "lettres"` affiche A, B, C, D au lieu de 01, 02, 03
(sondage, quiz). Le bouton « Copier la fiche (JSON) » du studio produit ce bloc.

## Ajouter une photo

1. Partir de la photo originale du photographe, pas d'une copie passée par
   WhatsApp ou une capture d'écran : le visage doit rester net une fois agrandi.
   Détourer la photo (fond transparent) : remove.bg, Canva, ou
   `rembg` (`pip install rembg`, modèle `birefnet-portrait`).
2. L'enregistrer en WebP ou PNG dans `assets/photos/` (`costume.webp`), recadrée
   au plus près de la silhouette, la tête en haut.
3. Lui donner un nom dans `assets/photos/reperes.json` (`"costume": { "nom": "Costume" }`).
   Les repères de cadrage (haut du crâne, menton, axe du visage) sont calculés
   automatiquement ; on peut les fixer à la main s'ils tombent mal.
4. `node generer.js studio` : la photo apparaît dans le studio.

## Contenu du dossier

```
studio-contenus/
├── studio.html              le studio AITE, autonome (généré : ne pas modifier à la main)
├── studio-verandah.html     le studio La Vérandah (généré)
├── generer.js               construit studio.html et génère les visuels
├── contenus/
│   └── publications.json    le calendrier : textes, légendes, hashtags
├── sortie/                  visuels générés et CALENDRIER.md
├── src/
│   ├── rendu.js             moteur de dessin et modèles AITE (canvas)
│   ├── rendu-verandah.js    modèles de La Vérandah
│   ├── editeur.js           interface du studio
│   └── studio.html          gabarit de la page
└── assets/
    ├── photos/              photos détourées du DG et repères de cadrage
    ├── logo/                logo AITE Consulting (fond transparent)
    └── polices/             Space Grotesk et IBM Plex Sans (licence OFL)
```

Pour changer un modèle, modifier `src/rendu.js`, puis `node generer.js`.
