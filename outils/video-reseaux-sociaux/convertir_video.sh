#!/usr/bin/env bash
# Convertit les vidéos du Google Pixel 8 Pro (HEVC 10 bits, HDR HLG, 4K,
# fréquence d'images variable, pistes de métadonnées Google) en MP4 H.264
# 8 bits SDR que WhatsApp, TikTok et Facebook acceptent sans délaver les
# couleurs ni refuser le fichier.
#
# Fonctionne sur PC (Linux, macOS, Windows via Git Bash/WSL) et directement
# sur le téléphone avec Termux. Seule dépendance : ffmpeg (avec ffprobe).

set -euo pipefail

PROFILS_VALIDES="whatsapp statut tiktok facebook tous"

usage() {
  cat <<'AIDE'
Usage : convertir_video.sh [options] VIDEO|DOSSIER [VIDEO|DOSSIER ...]

Profils (-p) :
  whatsapp   MP4 H.264 1080p, 30 i/s, poids maîtrisé (discussion, groupes)
  statut     comme whatsapp, découpé en morceaux de 59 s pour les statuts
  tiktok     1080x1920 vertical 9:16 (fond flouté si la vidéo est horizontale),
             aussi valable pour Facebook Reels et Instagram Reels
  facebook   MP4 H.264 1080p haute qualité, format d'origine conservé
  tous       whatsapp + tiktok + facebook (par défaut)

Options :
  -p PROFIL  profil de sortie (voir ci-dessus), défaut : tous
  -f IPS     images par seconde visées : 30 (défaut) ou 60 ; jamais plus
             que la vidéo d'origine
  -o DOSSIER dossier de sortie, défaut : ./converties
  -n         TikTok : recadrer au centre au lieu d'ajouter un fond flouté
  -h         afficher cette aide

Exemples :
  convertir_video.sh PXL_20261016_101500123.mp4
  convertir_video.sh -p tiktok -f 60 ~/storage/dcim/Camera
  convertir_video.sh -p statut -o ~/storage/movies/statuts video.mp4
AIDE
}

erreur() { echo "Erreur : $*" >&2; exit 1; }

profil="tous"
ips_vise=30
sortie="./converties"
recadrer=0

while getopts ":p:f:o:nh" opt; do
  case "$opt" in
    p) profil="$OPTARG" ;;
    f) ips_vise="$OPTARG" ;;
    o) sortie="$OPTARG" ;;
    n) recadrer=1 ;;
    h) usage; exit 0 ;;
    :) erreur "l'option -$OPTARG attend une valeur" ;;
    *) erreur "option inconnue -$OPTARG (voir -h)" ;;
  esac
done
shift $((OPTIND - 1))

[[ " $PROFILS_VALIDES " == *" $profil "* ]] || erreur "profil inconnu « $profil » ($PROFILS_VALIDES)"
[[ "$ips_vise" == 30 || "$ips_vise" == 60 ]] || erreur "-f accepte 30 ou 60"
[[ $# -gt 0 ]] || { usage; exit 1; }
command -v ffmpeg >/dev/null || erreur "ffmpeg est introuvable (Termux : pkg install ffmpeg)"
command -v ffprobe >/dev/null || erreur "ffprobe est introuvable (il est livré avec ffmpeg)"

mkdir -p "$sortie"

# Le tone mapping HDR -> SDR passe par zscale (libzimg). Sans lui, on se
# rabat sur le filtre colorspace : les couleurs restent correctes mais les
# hautes lumières sont moins bien rendues.
# (Sortie capturée d'abord : avec pipefail, « | grep -q » coupe ffmpeg et
# ferait croire à tort que zscale manque.)
filtres_ffmpeg="$(ffmpeg -hide_banner -filters 2>/dev/null || true)"
if grep -q ' zscale ' <<<"$filtres_ffmpeg"; then
  a_zscale=1
else
  a_zscale=0
fi

sonde() { # sonde FICHIER CHAMP -> valeur du premier flux vidéo
  ffprobe -v error -select_streams v:0 -show_entries "stream=$2" \
    -of default=noprint_wrappers=1:nokey=1 "$1" | head -1
}

# Chaîne de filtres qui ramène la vidéo en SDR BT.709 8 bits.
filtre_couleur() { # filtre_couleur TRANSFERT
  case "$1" in
    arib-std-b67|smpte2084)
      if (( a_zscale )); then
        echo "zscale=tin=$1:min=bt2020nc:pin=bt2020:rin=tv:t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p"
      else
        echo "colorspace=all=bt709:iall=bt2020:itrc=bt2020-10:fast=1:format=yuv420p"
      fi ;;
    *)
      echo "format=yuv420p" ;;
  esac
}

# Réglages d'encodage par profil : CRF, débit max, débit audio.
reglages() { # reglages PROFIL -> "crf maxrate audio"
  case "$1" in
    whatsapp|statut) echo "23 5M 128k" ;;
    tiktok)          echo "19 15M 192k" ;;
    facebook)        echo "20 10M 192k" ;;
  esac
}

convertir() { # convertir FICHIER PROFIL
  local src="$1" prof="$2"
  local base nom transfert ips_src ips largeur hauteur rotation
  base="$(basename "$src")"; nom="${base%.*}"

  transfert="$(sonde "$src" color_transfer)"
  largeur="$(sonde "$src" width)"; hauteur="$(sonde "$src" height)"
  # Le Pixel enregistre souvent en paysage avec une rotation en métadonnée.
  rotation="$(ffprobe -v error -select_streams v:0 -show_entries stream_side_data=rotation \
    -of default=noprint_wrappers=1:nokey=1 "$src" | head -1)"
  if [[ "${rotation#-}" == 90 || "${rotation#-}" == 270 ]]; then
    local t="$largeur"; largeur="$hauteur"; hauteur="$t"
  fi

  # Ne jamais inventer d'images : 24 i/s reste 24, 60 i/s descend à 30 si demandé.
  ips_src="$(sonde "$src" avg_frame_rate)"
  ips="$(awk -v r="$ips_src" -v v="$ips_vise" 'BEGIN {
    n = split(r, p, "/"); f = (n == 2 && p[2] > 0) ? p[1] / p[2] : r + 0
    if (f <= 0) f = v
    f = int(f + 0.5); print (f < v) ? f : v }')"

  local couleur echelle filtre
  couleur="$(filtre_couleur "$transfert")"
  # Côté le plus long limité à 1920 px : 4K -> 1080p, dimensions paires.
  echelle="scale=w='if(gte(iw,ih),min(iw,1920),-2)':h='if(gte(iw,ih),-2,min(ih,1920))':flags=lanczos"

  if [[ "$prof" == tiktok ]]; then
    if (( largeur * 16 == hauteur * 9 )); then
      filtre="scale=1080:1920:flags=lanczos,$couleur"
    elif (( recadrer )); then
      filtre="scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920,$couleur"
    else
      filtre="$couleur,split[a][b];[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=30:2,eq=brightness=-0.06[fond];[b]scale=1080:1920:force_original_aspect_ratio=decrease:flags=lanczos[avant];[fond][avant]overlay=(W-w)/2:(H-h)/2,setsar=1"
    fi
  else
    filtre="$echelle,$couleur,setsar=1"
  fi

  local crf maxrate audio
  read -r crf maxrate audio <<<"$(reglages "$prof")"

  local entree=(-hide_banner -loglevel error -stats -y)
  local args=(
    # Seulement l'image et le son : les pistes de données Google (mouvement,
    # métadonnées de caméra) font échouer certains envois.
    -filter_complex "[0:v:0]$filtre,fps=$ips[v]" -map "[v]" -map "0:a:0?"
    -map_metadata 0
    -c:v libx264 -preset medium -profile:v high -level:v 4.2 -pix_fmt yuv420p
    -crf "$crf" -maxrate "$maxrate" -bufsize "$((${maxrate%M} * 2))M"
    -g "$((ips * 2))" -fps_mode cfr
    -color_primaries bt709 -color_trc bt709 -colorspace bt709 -color_range tv
    -c:a aac -b:a "$audio" -ar 48000 -ac 2
  )

  local hdr="SDR"
  [[ "$transfert" == arib-std-b67 || "$transfert" == smpte2084 ]] && hdr="HDR→SDR"
  echo "▶ $base → $prof (${largeur}x${hauteur}, $hdr, ${ips} i/s)"

  local cible duree_src
  if [[ "$prof" == statut ]]; then
    # Un encodage par morceau de 59 s : coupe exacte, sous la limite d'une
    # minute des statuts WhatsApp.
    duree_src="$(ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 "$src")"
    local debut=0 i=0
    while awk -v d="$duree_src" -v s="$debut" 'BEGIN { exit !(d - s > 0.5) }'; do
      cible="$sortie/$(printf '%s_statut_%02d.mp4' "$nom" "$i")"
      ffmpeg "${entree[@]}" -ss "$debut" -t 59 -i "$src" "${args[@]}" -movflags +faststart "$cible"
      echo "  ✓ $cible"
      debut=$((debut + 59)); i=$((i + 1))
    done
    return
  fi

  cible="$sortie/${nom}_${prof}.mp4"
  ffmpeg "${entree[@]}" -i "$src" "${args[@]}" -movflags +faststart "$cible"

  local duree taille
  duree="$(ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 "$cible")"
  taille="$(du -h "$cible" | cut -f1)"
  echo "  ✓ $cible ($taille, $(printf '%.0f' "$duree") s)"
  if [[ "$prof" == tiktok ]] && awk -v d="$duree" 'BEGIN { exit !(d > 600) }'; then
    echo "  ⚠ plus de 10 min : TikTok n'accepte cette durée que depuis l'ordinateur"
  fi
}

# Récupère les vidéos des arguments (fichiers ou dossiers entiers).
videos=()
for arg in "$@"; do
  if [[ -d "$arg" ]]; then
    while IFS= read -r -d '' f; do videos+=("$f"); done < <(
      find "$arg" -maxdepth 1 -type f \( -iname '*.mp4' -o -iname '*.mov' -o -iname '*.mkv' -o -iname '*.3gp' \) -print0 | sort -z)
  elif [[ -f "$arg" ]]; then
    videos+=("$arg")
  else
    echo "Ignoré (introuvable) : $arg" >&2
  fi
done
[[ ${#videos[@]} -gt 0 ]] || erreur "aucune vidéo à convertir"

case "$profil" in
  tous) profils=(whatsapp tiktok facebook) ;;
  *)    profils=("$profil") ;;
esac

echecs=0
for v in "${videos[@]}"; do
  for p in "${profils[@]}"; do
    convertir "$v" "$p" || { echo "  ✗ échec : $v ($p)" >&2; echecs=$((echecs + 1)); }
  done
done

(( a_zscale )) || echo "Note : ffmpeg sans zscale, conversion HDR simplifiée (installez un ffmpeg complet pour un meilleur rendu)."
(( echecs == 0 )) || { echo "$echecs conversion(s) en échec." >&2; exit 1; }
echo "Terminé : vidéos dans $sortie"
