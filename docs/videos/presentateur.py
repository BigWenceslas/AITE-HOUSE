# -*- coding: utf-8 -*-
"""Le mode présentateur : votre enregistrement remplace la voix de synthèse.

    python3 docs/videos/produire.py crc --script                  # le texte à lire
    python3 docs/videos/produire.py crc --presentateur moi.mp4 --planche
    python3 docs/videos/produire.py presentation --presentateur moi.mp4 --rendu --sortie ../aite-videos/essais

Le présentateur lit le script de la vidéo d'une traite, face caméra, en
marquant deux secondes de silence entre deux parties. Le découpage retient
les plus longs silences : autant de parties que de phrases au script. Chaque
partie devient la « voix » de sa scène, normalisée à −16 LUFS : la même
mécanique que la voix de synthèse, la voix pilote les durées. L'image, recadrée
en carré, devient une piste vidéo de la durée de la vidéo, en médaillon en
haut à droite ; quand une scène dure plus longtemps que la parole, la dernière
image se fige plutôt que de montrer le début de la partie suivante.

Aucun modèle à télécharger : le découpage lit les silences. La transcription
(``hyperframes transcribe``) peut servir de contrôle quand le réseau laisse
passer huggingface.co.
"""

import os
import re
import subprocess
import sys

PAUSE = 2.0          # le silence demandé entre deux parties, en secondes
SILENCE_DB = -38     # en dessous, c'est du silence (enregistrement normalisé)
SILENCE_MIN = 0.45   # un silence plus court est une respiration
MARGE = 0.15         # la voix garde un souffle avant et après la parole (fins de phrase douces)
TAILLE = 560         # le carré du médaillon, en pixels (affiché à 300)
IMAGES = 30          # la cadence des rendus HyperFrames


def lancer(commande):
    r = subprocess.run(commande, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit('Échec : %s\n%s' % (' '.join(commande[:6]), r.stderr[-1500:]))
    return r


def duree(chemin):
    r = lancer(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', chemin])
    return float(r.stdout.strip())


def ordre(scenario, textes):
    """Les parties dans l'ordre où elles passent à l'écran (et où on les lit)."""
    cases = ['ouverture', 'poste', 'circuit', 'connexion']
    for n, chap in enumerate(scenario['chapitres'], 1):
        cases.append('chap-%d' % n)
        cases += ['c%d-etape-%d' % (n, m) for m in range(1, len(chap['etapes']) + 1)]
    cases += ['retenir', 'fin']
    return [c for c in cases if c in textes]


def nom_partie(case):
    noms = {'ouverture': 'Ouverture', 'poste': 'La solution', 'circuit': 'Le parcours', 'connexion': 'La connexion',
            'retenir': 'À retenir', 'fin': 'Fin'}
    if case in noms:
        return noms[case]
    if case.startswith('chap-'):
        return 'Chapitre %s' % case.split('-')[1]
    chapitre, _, etape = case.partition('-etape-')
    return 'Chapitre %s, étape %s' % (chapitre[1:], etape)


def script(scenario, textes, chemin):
    """Le texte à lire face caméra, partie par partie, avec la durée visée."""
    lignes = ['# %s — script du présentateur' % scenario['titre'], '',
              'Lisez d\'une traite, face caméra, sans couper. Entre deux parties, '
              'marquez **%d secondes de silence** en regardant la caméra : le découpage '
              'les repère. Une hésitation dans une partie ne gêne pas ; une pause '
              'aussi longue que celle entre deux parties, si.' % PAUSE, '',
              'Cadrage : visage et épaules au centre, fond calme, lumière de face, '
              'micro proche (casque ou cravate). Format 16:9 ou 9:16, 25 ou 30 images/s.', '']
    for i, case in enumerate(ordre(scenario, textes), 1):
        texte = textes[case]
        lignes += ['## %d. %s  (≈ %d s)' % (i, nom_partie(case), round(len(texte) / 15.0)), '', texte, '',
                   '*— silence, %d s —*' % PAUSE, '']
    with open(chemin, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lignes))
    return chemin


def silences(audio):
    """Les silences de l'enregistrement : [(début, fin)]."""
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', audio, '-af',
                        'silencedetect=noise=%ddB:d=%.2f' % (SILENCE_DB, SILENCE_MIN), '-f', 'null', '-'],
                       capture_output=True, text=True)
    debuts = [float(x) for x in re.findall(r'silence_start: (-?[\d.]+)', r.stderr)]
    fins = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', r.stderr)]
    total = duree(audio)
    if len(fins) < len(debuts):        # un silence qui court jusqu'à la fin
        fins.append(total)
    return [(max(0.0, d), f) for d, f in zip(debuts, fins)], total


def parties(audio, n):
    """Les n parties parlées : entre les n − 1 plus longs silences intérieurs.

    Rend [(début, fin)] de la parole, sans les silences du bord."""
    liste, total = silences(audio)
    interieurs = [s for s in liste if s[0] > 0.05 and s[1] < total - 0.05]
    if len(interieurs) < n - 1:
        sys.exit('%d parties attendues, %d seulement trouvées : marquez %d secondes de silence entre deux parties.'
                 % (n, len(interieurs) + 1, PAUSE))
    coupes = sorted(sorted(interieurs, key=lambda s: s[1] - s[0], reverse=True)[:n - 1])
    debut_parole = liste[0][1] if liste and liste[0][0] <= 0.05 else 0.0
    fin_parole = liste[-1][0] if liste and liste[-1][1] >= total - 0.05 else total
    bornes = [debut_parole] + [x for s in coupes for x in s] + [fin_parole]
    return [(round(bornes[2 * i], 3), round(bornes[2 * i + 1], 3)) for i in range(n)], coupes


def preparer(enregistrement, scenario, textes, dossier):
    """Découpe l'enregistrement : la voix de chaque scène et l'instant où elle
    commence dans l'enregistrement. Rend ({case: wav}, {case: durée}, {case: début})."""
    travail = os.path.join(dossier, 'presentateur', scenario['slug'])
    os.makedirs(travail, exist_ok=True)
    audio = os.path.join(travail, 'enregistrement.wav')
    # le niveau d'abord : le seuil de silence vaut pour toutes les prises
    lancer(['ffmpeg', '-v', 'error', '-y', '-i', enregistrement, '-vn', '-ac', '1', '-ar', '48000',
            '-af', 'highpass=f=80,loudnorm=I=-16:TP=-1.5:LRA=11', audio])
    cases = ordre(scenario, textes)
    morceaux, coupes = parties(audio, len(cases))
    fichiers, durees, debuts = {}, {}, {}
    print('  présentateur : %d parties, silences de coupe %s s'
          % (len(cases), ', '.join('%.1f' % (f - d) for d, f in coupes)))
    for case, (d, f) in zip(cases, morceaux):
        voix = os.path.join(travail, '%s.wav' % case)
        lancer(['ffmpeg', '-v', 'error', '-y', '-ss', '%.3f' % max(0.0, d - MARGE), '-to', '%.3f' % (f + MARGE),
                '-i', audio, '-af', 'loudnorm=I=-16:TP=-1.5:LRA=7', '-ar', '48000', '-ac', '1', voix])
        fichiers[case], durees[case], debuts[case] = voix, round(duree(voix), 3), max(0.0, d - MARGE)
        vise = len(textes[case]) / 15.0
        alerte = '  ⚠ à vérifier' if not 0.5 <= (f - d) / vise <= 2.0 else ''
        print('    %-10s %6.1f → %6.1f s  (%4.1f s, script ≈ %4.1f s)%s' % (case, d, f, f - d, vise, alerte))
    return fichiers, durees, debuts


def piste_video(enregistrement, debuts, plages, total, avant_voix, chemin, recadrage=None):
    """La piste du médaillon, de la durée de la vidéo : pour chaque scène, le
    présentateur depuis ``avant_voix`` secondes avant sa parole, jusqu'à la
    scène suivante ; la dernière image se fige s'il a fini avant."""
    travail = os.path.dirname(chemin)
    os.makedirs(travail, exist_ok=True)
    fin_enregistrement = duree(enregistrement)
    cadre = 'crop=%s' % recadrage if recadrage else "crop='min(iw,ih)':'min(iw,ih)'"
    plages = [p for p in plages if p[0] in debuts]
    # les bornes sur la grille des images : arrondir morceau par morceau
    # ferait dériver la piste, et les lèvres, d'une image à chaque scène
    bornes = [0] + [round(p[1] * IMAGES) for p in plages[1:]] + [round(total * IMAGES)]
    morceaux = []
    for i, (case, debut_scene) in enumerate(plages):
        images = bornes[i + 1] - bornes[i]
        avance = round(debut_scene * IMAGES) if i == 0 else 0   # avant la première scène : médaillon caché
        source = max(0.0, debuts[case] - avant_voix)
        suivant = debuts[plages[i + 1][0]] - avant_voix if i + 1 < len(plages) else fin_enregistrement
        prises = max(1, min(images - avance, int((suivant - source) * IMAGES)))   # sans la partie suivante
        figees = images - avance - prises
        filtre = ('%s,scale=%d:%d,fps=%d,tpad=start_mode=clone:start_duration=%.4f:stop_mode=clone:stop_duration=%.4f'
                  % (cadre, TAILLE, TAILLE, IMAGES, avance / float(IMAGES), (figees + IMAGES) / float(IMAGES)))
        morceau = os.path.join(travail, 'morceau-%02d.mp4' % i)
        lancer(['ffmpeg', '-v', 'error', '-y', '-ss', '%.3f' % source, '-t', '%.3f' % (prises / float(IMAGES)),
                '-i', enregistrement, '-vf', filtre, '-frames:v', str(images), '-an', '-c:v', 'libx264', '-crf', '20',
                '-preset', 'veryfast', '-pix_fmt', 'yuv420p', morceau])
        morceaux.append(morceau)
    liste = os.path.join(travail, 'morceaux.txt')
    with open(liste, 'w') as f:
        f.write(''.join("file '%s'\n" % os.path.basename(m) for m in morceaux))
    lancer(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', liste, '-c', 'copy', chemin])
    return chemin
