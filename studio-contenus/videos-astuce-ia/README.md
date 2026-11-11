# Vidéos « Astuce IA » (AITE Consulting)

Vidéos verticales 1080 × 1920 de 40 à 50 secondes : une astuce sur un outil d'IA (ChatGPT, Gemini,
Copilot, Claude, Le Chat de Mistral…), voix off française (Kokoro, voix `ff_siwis`, gratuite et locale),
sous-titres incrustés pour la lecture sans le son, photo du DG en ouverture et en fin, appel à l'action
« Diagnostic 360° gratuit · WhatsApp (+237) 656 80 10 98 ».

```bash
./preparer.sh                      # polices, logo, photo, voix (une fois) ; numpy est requis par sons.py
python3 voix.py                    # synthèse et durées de chaque scène → plan.json
.venv-tts/bin/python ecoute.py     # contrôle : retranscrit chaque phrase et la compare au sous-titre
node rendre.js astuce-ia-1-formule --apercu   # une image par scène dans apercu/
node rendre.js astuce-ia-1-formule            # MP4 final (H.264 + AAC, 30 i/s)
```

- `scenarios.py` : une vidéo = une liste de scènes. `voix` est le texte lu (graphie phonétique),
  `sous` le sous-titre affiché. Types de scène : `titre`, `chips`, `chat`, `mail`, `telephone`,
  `renomme`, `notebook`, `alerte`, `fin` (définis dans `page.html`).
- Prononciation Kokoro vérifiée par retranscription : écrire « intelligence artificielle » (pas « IA »,
  lu « ya »), « Tchatte Gé Pé Té », « Gémini », « Copilote », « Aoutlouk », « Gougueule », « Ouatsape »,
  « imèles », « Oueurde », « Paoueur-Pointe », « notebouk », « pages ouèbe ».
- Animation (version 2, d'après les modèles de vidéos produit transmis par le DG le 11 novembre 2026) :
  fond clair à pois violets, titres révélés mot à mot dans un masque, noms révélés lettre par lettre,
  cartes qui surgissent avec rebond, caméra virtuelle qui s'approche de l'élément utile, curseur sur
  trajet courbe avec onde de clic, voile sombre et fenêtre qui surgit, téléphone en 3D, volet violet
  entre deux scènes, fin sur un cercle violet qui envahit l'écran, sous-titres « karaoké ».
- Son : `sons.py` synthétise une musique de fond discrète (96 battements par minute, la mineur) et
  les bruitages (souffle aux transitions, « pop » aux apparitions, clic du curseur) ; la page déclare
  ses évènements sonores, `rendre.js` les mixe sous la voix.
- Règle de fond : chaque fonction montrée vient de la page d'aide officielle de l'éditeur, avec les
  libellés exacts de l'interface ; les noms de produits changent vite (NotebookLM est devenu Gemini
  Notebook en juillet 2026) : revérifier avant chaque nouvel épisode. Les données de démonstration
  (chantier, factures, appel d'offres) sont fictives.
