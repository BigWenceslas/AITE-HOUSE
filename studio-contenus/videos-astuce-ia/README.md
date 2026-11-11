# Vidéos « Astuce IA » (AITE Consulting)

Vidéos verticales 1080 × 1920 de 40 à 50 secondes : une astuce sur un outil d'IA (ChatGPT, Gemini,
Copilot, Claude, Le Chat de Mistral…), voix off française (Kokoro, voix `ff_siwis`, gratuite et locale),
sous-titres incrustés pour la lecture sans le son, photo du DG en ouverture et en fin, appel à l'action
« Diagnostic 360° gratuit · WhatsApp (+237) 656 80 10 98 ».

```bash
./preparer.sh                      # polices, logo, photo, voix (une fois)
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
- Règle de fond : chaque fonction montrée vient de la page d'aide officielle de l'éditeur, avec les
  libellés exacts de l'interface ; les noms de produits changent vite (NotebookLM est devenu Gemini
  Notebook en juillet 2026) : revérifier avant chaque nouvel épisode. Les données de démonstration
  (chantier, factures, appel d'offres) sont fictives.
