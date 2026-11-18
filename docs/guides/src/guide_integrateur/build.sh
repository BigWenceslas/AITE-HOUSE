#!/usr/bin/env bash
# Produit docs/guides/AITE_Guide_Integrateur.pdf à partir de guide.html et guide.css.
# Les images sont lues à leur place dans le dépôt (captures/restaurant/,
# captures/integrateur/, docs/logo_aite.jpg).
# WEASYPRINT : chemin de weasyprint (défaut « weasyprint »).
set -euo pipefail
ICI="$(cd "$(dirname "$0")" && pwd)"
WEASYPRINT="${WEASYPRINT:-weasyprint}"
SORTIE="$ICI/../../AITE_Guide_Integrateur.pdf"
"$WEASYPRINT" --base-url "$ICI/" "$ICI/guide.html" "$SORTIE"
echo "PDF : $(cd "$(dirname "$SORTIE")" && pwd)/$(basename "$SORTIE")"
