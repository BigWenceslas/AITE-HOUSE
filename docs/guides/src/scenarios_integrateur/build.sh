#!/usr/bin/env bash
# Produit docs/guides/AITE_Scenarios_Integrateur.pdf et .xlsx à partir de
# scenarios.py (source unique), des captures réelles (captures/restaurant/,
# captures/integrateur/) et du logo docs/logo_aite.jpg.
#
#   docs/guides/src/scenarios_integrateur/build.sh
#   WEASYPRINT=/chemin/vers/weasyprint docs/guides/src/scenarios_integrateur/build.sh
#
# Besoins : python3 avec Pillow et openpyxl ; weasyprint (variable WEASYPRINT,
# défaut « weasyprint »). generer.py s'arrête si un cas des domaines D, F, H,
# I, J, K, R du cahier de recette n'est ni couvert ni écarté avec sa raison.
set -euo pipefail
ICI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RACINE="$(cd "$ICI/../../../.." && pwd)"
WEASYPRINT="${WEASYPRINT:-weasyprint}"
BUILD="${BUILD:-$(mktemp -d)}"
PDF="$RACINE/docs/guides/AITE_Scenarios_Integrateur.pdf"

mkdir -p "$BUILD/img"
cp "$ICI/style.css" "$BUILD/"
# Captures réduites à 1 600 px de large ; nom « dossier__fichier.jpg ».
python3 - "$RACINE/captures" "$BUILD/img" <<'PY'
import glob, os, sys
from PIL import Image
src, dst = sys.argv[1], sys.argv[2]
for dossier in ('restaurant', 'integrateur'):
    for f in sorted(glob.glob(os.path.join(src, dossier, '*.jpg'))):
        im = Image.open(f).convert('RGB')
        im.thumbnail((1600, 1600))
        im.save(os.path.join(dst, dossier + '__' + os.path.basename(f)), quality=82, optimize=True)
PY
cp "$RACINE/docs/logo_aite.jpg" "$BUILD/img/"

python3 "$ICI/generer.py" "$BUILD"

"$WEASYPRINT" "$BUILD/index.html" "$PDF"
echo "PDF : $PDF"
echo "XLSX : $RACINE/docs/guides/AITE_Scenarios_Integrateur.xlsx"
