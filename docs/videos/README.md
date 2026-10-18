# Vidéo de présentation AITE HOUSE

Une vidéo motion design qui présente la suite hôtelière complète, poste par
poste, à partir des **fiches de recette** (`docs/GUIDE_RECETTE_UAT.md`) et du
cahier de recette (`recette/cas_de_test.py`, domaines N à Q pour la
vague 1). L'interface d'Odoo 18 y est **rejouée en HTML** avec les couleurs
et les libellés exacts du code — jamais filmée, jamais capturée — puis rendue
en MP4 par [HyperFrames](https://hyperframes.heygen.com), avec une voix off
française féminine.

La méthode est celle du skill `aite-motion-design-1` (méthode PGest).

| Ce qui est versionné | Où |
|---|---|
| Les sources : moteur, écrans, scénarios, feuille de style | `docs/videos/` |
| La vidéo compressée, sa vignette et la page qui la sert | `docs/guides/videos/` |

Les projets HyperFrames, les rendus pleine qualité et les voix sont des
**sorties régénérables** : elles vivent hors du dépôt, dans le dossier de
travail (`../aite-videos` par défaut).

## Produire

```
python3 docs/videos/produire.py presentation               # projet + voix + check
python3 docs/videos/produire.py presentation --planche     # + planches contact à relire
python3 docs/videos/produire.py presentation --rendu       # + rendu MP4 et compression
python3 docs/videos/produire.py presentation --muet --rendu  # sans voix off
python3 docs/videos/ecouter.py presentation                # contrôle des phonèmes
```

Prérequis : Node.js (`npx`), `ffmpeg`, Python 3. Au premier lancement, le
script installe GSAP dans le dossier de travail et Kokoro (voix off locale,
gratuite, voix française féminine `ff_siwis`) dans `<dossier>/.venv-tts`.
HyperFrames est figé à la version `0.8.139` pour que les rendus restent
reproductibles.

Avec une voix ElevenLabs (payant) : la clé dans `ELEVENLABS_API_KEY`, ou en
secret d'un environnement cloud, **jamais dans le dépôt** ; l'identifiant de
la voix en argument (`--moteur-voix elevenlabs --voix-id <ID>`). Dans un
environnement cloud Claude Code, le secret doit être injecté dans l'en-tête
`xi-api-key` (préfixe vide) : un en-tête `Authorization: Bearer` est refusé
par ElevenLabs (401 `invalid_api_key`).

Les écarts relevés entre la recette, les règles du projet et le code, en
écrivant les scénarios, sont dans `ECARTS.md`.

## Les fichiers

| Fichier | Rôle |
|---|---|
| `DESIGN.md` | La charte vidéo : palette, typographie, échelle, données de démo |
| `demo.py` | Les données de démonstration, fictives, communes à toute la vidéo |
| `ecrans.py` | Les écrans d'Odoo 18 rejoués : fenêtre, liste, fiche, kanban, assistant, tableaux de bord, téléphone, site web |
| `moteur.py` | Les scènes, les gestes, la composition HyperFrames |
| `produire.py` | Voix off, projet, contrôles, rendu, compression, page de la vidéo |
| `sons.py` | Les deux bruitages, synthétisés par le code : le son d'ouverture et le clic |
| `presentateur.py` | Mode présentateur : script à lire, découpage de la prise par les silences |
| `ecouter.py` | Contrôle hors ligne de la prononciation des voix off |
| `scenarios/presentation.py` | La trame : ouverture, la solution, le parcours, la connexion, les chapitres, à retenir |
| `scenarios/cN_<poste>.py` | Un chapitre par poste, avec ses sources dans l'en-tête |
| `scenarios/tNN_<fonction>.py` | Un tutoriel marketing par fonctionnalité |
| `marketing.py` | Le moteur des tutoriels : accroche, révélation, tutoriel (zoom, bulles), résultats, appel à l'action |
| `musique.py` | La musique de fond des tutoriels, synthétisée par le code |
| `shared/aite-marketing.css` | Les styles des tutoriels et du thème MuK |
| `shared/aite.css` | Les jetons de couleur et les composants, à l'échelle vidéo |
| `shared/aite-motion.js` | Le moteur d'animation : lit le plan, construit la timeline GSAP |

## Le découpage

1. **Ouverture** — le logo AITE, « AITE HOUSE », la mission.
2. **La solution** — trois verbes (accueillir, servir, piloter) et quatre faits.
3. **Le parcours** — d'un client, du site web à la direction.
4. **Se connecter** — identifiant, mot de passe ; le profil décide des menus.
5. **Sept chapitres**, chacun annoncé par sa carte (poste, personne, objectif),
   puis rejoué étape par étape dans l'application, avec sa légende :

   | Chapitre | Source | Étapes |
   |---|---|---|
   | 1. La journée de la réception | fiche UAT 1, cas O01 / N02 | 7 |
   | 2. Le tour des chambres | fiche UAT 2, domaine P | 6 |
   | 3. Ardoises clients et recouvrement | fiche UAT 3 | 6 |
   | 4. La réservation en ligne | fiche UAT 5 | 6 |
   | 5. Stock, ruptures et réapprovisionnement | fiche UAT 6 | 5 |
   | 6. Le cockpit de la direction | fiche UAT 4, domaine Q | 7 |
   | 7. La conformité, sans saisie de plus | domaines N et O | 6 |

6. **À retenir**, puis la **fin** (logo, renvoi au cahier de recette).

Chaque scène a une durée de base ; la voix off l'allonge si sa phrase est plus
longue. Une étape dont l'image tourne plus de trois secondes sans voix est
signalée au moment de produire.

## Les tutoriels marketing

Une vidéo par fonctionnalité (`scenarios/tNN_<fonction>.py`, liste dans
`produire.TUTORIELS`), dans le registre des vidéos de lancement de
logiciels : 1 min 30 à 2 min, moteur `marketing.py`, styles
`shared/aite-marketing.css`.

    accroche → révélation → tutoriel (étapes) → résultats → appel à l'action

| Scène | Ce qu'on voit | Source du contenu |
|---|---|---|
| Accroche | la question qui fâche, et jusqu'à six cartes « problème » qui flottent, puis sont aspirées | les douleurs relevées dans les documents du dépôt (étude comparative, feuille de route, notes) |
| Révélation | trois grands cercles aux couleurs du logo, la carte AITE, « AITE HOUSE », le numéro du tutoriel, la fonctionnalité et sa promesse | la promesse, vérifiable dans le code |
| Tutoriel | le navigateur, Odoo 18 habillé par le **thème MuK** (barre ardoise, barre des applications, bleu acier), sur un fond violet ; en haut les temps forts en pastilles et le personnage ; en bas la légende de l'étape | les vues, modèles, gabarits ; les applications de la barre MuK sont celles du profil (`ecrans.APPS_PROFIL`) |
| Résultats | trois cartes chiffrées | des chiffres vrais (barèmes, réglages par défaut, données de démonstration) |
| Appel à l'action | AITE Consulting, ses coordonnées publiques, la chaîne YouTube, le tutoriel suivant | `README.md` du dépôt |

`TUTORIEL` porte : `slug`, `profil`, `numero`, `titre`, `fonction`,
`personnage`, `accroche` (`kicker`, `question` — un mot entre astérisques
ressort en violet —, `douleurs` [(icône, texte)], `voix`), `revelation`
(`promesse`, `voix`), `temps` (les pastilles), `app`, `ecran` (la fenêtre
composée avec `ecrans.navigateur(ecrans.fenetre_muk(...))`),
`vues_initiales`, `bulles` {id: texte}, `reactions` {id: texte}, `etapes`
(`temps`, `titre`, `texte`, `voix`, `gestes`), `resultats` (`titre`,
`cartes` [{valeur, compter, unite, icone, texte}], `voix`), `cta` (`appel`,
`suivant`, `voix`), `vignette`, et au besoin `css` (styles propres au
tutoriel, pour un écran composé à la main).

Gestes propres aux tutoriels (`marketing.py`) :

| Geste | Effet |
|---|---|
| `zoom(sel, s=1.5)` | la caméra s'approche de l'élément, sans laisser voir le bord du navigateur ; curseur, anneau et bulles suivent |
| `dezoom()` | retour au plan large |
| `bulle(id, sel, cote)` | une bulle « à retenir » s'ouvre à côté de l'élément (droite, gauche, haut, bas), puis se referme |
| `reaction(id)` | le personnage réagit, dans le coin bas droit |

La **musique de fond** (`musique.py`) est composée par le code : ré majeur,
100 battements par minute, tapis, basse, arpège pincé, pulsation feutrée ;
elle s'efface de 9 dB sous chaque phrase de la voix et se termine sur un
accord tenu à l'appel à l'action. `--sans-musique` la retire. Claude ne
l'entend pas : elle est à valider à l'oreille.

Les captures de référence du thème MuK (modèle visuel, jamais incrustées)
se prennent sur une base de démonstration où `muk_web_theme` est installé,
hors du dépôt (`../aite-videos/ref_muk`).

## Écrire un chapitre

`scenarios/cN_<poste>.py` définit un dictionnaire `CHAPITRE` : `court`
(sommaire), `poste`, `titre`, `personne`, `objectif`, `voix` (la carte du
chapitre), `app` et `ecran` (le HTML de la fenêtre, composé avec
`ecrans.py`), `vues_initiales`, `etapes` (liste de `{titre, texte, voix,
gestes}`). L'en-tête du fichier cite les fichiers d'où viennent les
libellés.

### Les gestes

Posés l'un après l'autre ; `avec=True` les lance en même temps que le
précédent, `decale=` attend avant.

| Geste | Effet |
|---|---|
| `clic(sel)` | amène le curseur sur l'élément et clique |
| `saisir(ident, texte)` | tape dans un champ `ecrans.entree` |
| `choisir(ident, valeur)` | remplit un champ (liste déroulante) |
| `vue(ident, groupe)` | passe d'une vue à l'autre (`'odoo'` ou `'site'`) |
| `ouvrir(ident)` / `fermer(ident)` | un assistant, une erreur d'accès, le téléphone |
| `etat(sel, libellé, genre)` | change une pastille d'état |
| `classe(sel, ajouter, retirer)` | change une classe (statusbar, menu actif, carte) |
| `texte(sel, après)` | change un texte (compteur de colonne, montant) |
| `montrer(sel)` / `cacher(sel)` | fait apparaître ou disparaître un élément `masque` |
| `defiler(sel, y)` | fait défiler un contenu, y négatif vers le bas |
| `anneau(sel)` | entoure un élément d'un anneau orange, sans cliquer |
| `survol(sel)` | surligne une ligne |
| `compter(sel, de, a)` | fait monter un nombre |
| `animer(sel, de, a)` | anime un graphique (barres, courbe) |
| `notifier(ident)` | affiche une notification `ecrans.toast` |
| `pause(d)` | laisse l'image respirer |

## Les règles

- **Rien d'inventé.** Un libellé à l'écran existe mot pour mot dans le code
  (vues, modèles, gabarits OWL et QWeb) ; une règle dite par la voix se
  retrouve dans les fiches de recette, le cahier de recette ou le code. Ce
  qui s'affiche mal dans l'application (date ISO, point décimal) est rejoué
  tel quel et relevé dans `ECARTS.md`.
- **Personnes fictives.** Les jeux d'essai de recette n'apparaissent jamais :
  noms, références et montants viennent de `demo.py`.
- **La voix off** dit ce que l'image montre sans la lire ; environ 15
  caractères par seconde ; les mots que Kokoro lit mal sont réécrits pour
  la voix seulement (« Aïte haousse », « revpar », « Orange Moni »,
  « pikeup »), jamais à l'écran.
- **Contrôles avant rendu** : `check` sans erreur, planches contact relues
  image par image, aucune alerte « image sans voix ».
