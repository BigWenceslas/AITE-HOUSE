#!/usr/bin/env bash
# Produit docs/guides/AITE_Restaurant_Scenarios_de_tests.pdf et .xlsx à partir
# de scenarios.py (source unique), des captures réelles captures/restaurant/
# et du logo docs/logo_aite.jpg.
#
#   docs/guides/src/scenarios_restaurant/build.sh
#   WEASYPRINT=/chemin/vers/weasyprint docs/guides/src/scenarios_restaurant/build.sh
#
# Besoins : python3 avec Pillow et openpyxl ; weasyprint (variable WEASYPRINT,
# défaut « weasyprint »). Le dossier de travail (BUILD, défaut : un dossier
# temporaire) reçoit index.html, style.css et les images réduites.
set -euo pipefail
ICI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RACINE="$(cd "$ICI/../../../.." && pwd)"
WEASYPRINT="${WEASYPRINT:-weasyprint}"
BUILD="${BUILD:-$(mktemp -d)}"
PDF="$RACINE/docs/guides/AITE_Restaurant_Scenarios_de_tests.pdf"

mkdir -p "$BUILD/img"
cp "$ICI/style.css" "$BUILD/"
# Captures réduites à 1 600 px de large (lisibles à 150 mm, PDF léger) ; logo tel quel.
python3 - "$RACINE/captures/restaurant" "$BUILD/img" <<'EOF'
import glob, os, sys
from PIL import Image
src, dst = sys.argv[1], sys.argv[2]
for f in sorted(glob.glob(os.path.join(src, '*.jpg'))):
    im = Image.open(f).convert('RGB')
    im.thumbnail((1600, 1600))
    im.save(os.path.join(dst, os.path.basename(f)), quality=82, optimize=True)
EOF
cp "$RACINE/docs/logo_aite.jpg" "$BUILD/img/"

# HTML + classeur, avec le contrôle de couverture des cas R01..R104.
python3 "$ICI/generer.py" "$BUILD"

"$WEASYPRINT" "$BUILD/index.html" "$PDF"
echo "PDF : $PDF"
echo "XLSX : $RACINE/docs/guides/AITE_Restaurant_Scenarios_de_tests.xlsx"
