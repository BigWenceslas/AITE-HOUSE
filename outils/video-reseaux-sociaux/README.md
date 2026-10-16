# Vidéos du Pixel 8 Pro pour WhatsApp, TikTok et Facebook

## Pourquoi les vidéos du Pixel posent problème

Par défaut, le Pixel 8 Pro filme dans un format pensé pour la qualité, pas
pour le partage :

| Réglage du Pixel                    | Conséquence sur les réseaux                               |
|-------------------------------------|-----------------------------------------------------------|
| **HDR 10 bits (HLG)**               | couleurs délavées ou grises sur WhatsApp et Facebook      |
| **HEVC / H.265**                    | envoi refusé ou très long sur certains téléphones / PC    |
| **4K, 60 i/s**                      | fichiers énormes, recompression agressive par l'appli    |
| fréquence d'images variable         | son décalé, saccades après publication                    |
| pistes de données Google (mouvement)| échec d'import dans certains éditeurs et sur le web       |

Le format accepté partout est : **MP4, H.264, 8 bits, SDR BT.709, son AAC,
1080p, fréquence d'images constante**. Le script `convertir_video.sh` produit
exactement cela.

## Solution 1 : régler l'appareil photo (pour les prochaines vidéos)

Dans **Pixel Caméra → Paramètres (roue dentée) → Vidéo** :

1. **HDR 10 bits** (ou *Ultra HDR* pour la vidéo) : **désactivé**. C'est la
   cause n° 1 des couleurs délavées.
2. **Résolution** : **1080p**, **30 i/s** (60 i/s pour le sport, 4K seulement
   si vous montez la vidéo ensuite).
3. **Codec / format multimédia** : choisir **H.264** ou **« le plus
   compatible »** si l'option est proposée (selon la version de l'appli, dans
   *Vidéo* ou *Paramètres avancés*).
4. **Video Boost** : laisser désactivé pour les vidéos à partager vite ;
   le traitement passe par Google Photos et prend du temps.

Option système utile : **Paramètres → Système → Options pour les
développeurs → Transcodage multimédia** (activer *Remplacer les paramètres
de transcodage* / *Activer le transcodage*). Android convertit alors le HEVC
en H.264 pour les applis qui ne le gèrent pas.

## Solution 2 : convertir les vidéos existantes avec le script

### Sur PC

Installer ffmpeg :

- Windows : `winget install Gyan.FFmpeg`, puis lancer le script dans Git Bash
  ou WSL ;
- macOS : `brew install ffmpeg` ;
- Linux : `sudo apt install ffmpeg`.

### Directement sur le Pixel, avec Termux

1. Installer **Termux** depuis F-Droid (la version du Play Store est ancienne).
2. Dans Termux :

   ```bash
   pkg update && pkg install ffmpeg
   termux-setup-storage            # autoriser l'accès aux photos et vidéos
   curl -LO <lien brut vers convertir_video.sh>   # ou copier le fichier
   chmod +x convertir_video.sh
   ```

3. Les vidéos du Pixel sont dans `~/storage/dcim/Camera`. Pour que les
   vidéos converties apparaissent dans la galerie, écrivez-les dans
   `~/storage/movies` :

   ```bash
   ./convertir_video.sh -o ~/storage/movies/Reseaux ~/storage/dcim/Camera/PXL_20261016_101500123.mp4
   ```

### Utilisation

```bash
./convertir_video.sh VIDEO.mp4                 # les 3 versions d'un coup
./convertir_video.sh -p whatsapp VIDEO.mp4     # une seule version
./convertir_video.sh -p statut VIDEO.mp4       # morceaux de 59 s pour les statuts
./convertir_video.sh -p tiktok -f 60 VIDEO.mp4 # TikTok en 60 i/s
./convertir_video.sh -p tiktok -n VIDEO.mp4    # recadrage au lieu du fond flou
./convertir_video.sh ~/storage/dcim/Camera     # tout un dossier
```

Les fichiers sortent dans `./converties` (option `-o` pour changer) :
`VIDEO_whatsapp.mp4`, `VIDEO_tiktok.mp4`, `VIDEO_facebook.mp4`,
`VIDEO_statut_00.mp4`, `VIDEO_statut_01.mp4`…

## Ce que produit chaque profil

| Profil     | Image                                   | Qualité vidéo        | Son       | Usage                                  |
|------------|-----------------------------------------|----------------------|-----------|----------------------------------------|
| `whatsapp` | 1080p max, format d'origine, 30 i/s     | CRF 23, ≤ 5 Mbit/s   | AAC 128k  | discussions, groupes, envoi en « HD »  |
| `statut`   | idem, découpé toutes les 59 s           | CRF 23, ≤ 5 Mbit/s   | AAC 128k  | statuts WhatsApp (1 min max)           |
| `tiktok`   | **1080x1920 (9:16)**, fond flouté       | CRF 19, ≤ 15 Mbit/s  | AAC 192k  | TikTok, Facebook Reels, Instagram Reels|
| `facebook` | 1080p max, format d'origine, 30 i/s     | CRF 20, ≤ 10 Mbit/s  | AAC 192k  | publications et vidéos de page         |

Dans tous les cas : HDR converti en SDR (tone mapping), H.264 High 8 bits,
fréquence constante, rotation appliquée, pistes de données Google retirées,
lecture immédiate sur le web (`faststart`).

## Conseils de publication

- **WhatsApp** : appuyer sur **HD** avant l'envoi, sinon WhatsApp réduit à
  480p. Pour garder la qualité exacte, envoyer la vidéo **en tant que
  document** (limite 2 Go).
- **TikTok** : importer le fichier `_tiktok.mp4` sans le retoucher dans
  l'appli ; activer **Paramètres → Données → Importer en haute qualité**.
  Garder textes et visages hors des 15 % du bas et de la marge de droite
  (boutons de l'interface).
- **Facebook** : dans l'appli, **Paramètres → Multimédia → Qualité de la
  vidéo : HD / Optimisé**, sinon Facebook importe en basse définition sur
  données mobiles. Pour un Reel, utiliser le fichier `_tiktok.mp4`.
- Toujours **convertir avant de monter** dans CapCut ou InShot si les
  couleurs paraissent délavées dans l'éditeur.
