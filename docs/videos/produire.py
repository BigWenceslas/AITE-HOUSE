# -*- coding: utf-8 -*-
"""Produire la vidéo de présentation AITE HOUSE : voix off, projet HyperFrames, rendu.

    python3 docs/videos/produire.py presentation                 # projet + voix + check
    python3 docs/videos/produire.py presentation --planche       # + planche contact
    python3 docs/videos/produire.py presentation --rendu         # + rendu et compression
    python3 docs/videos/produire.py presentation --muet --rendu  # sans voix off

Le projet, les rendus et les voix vivent **hors du dépôt**, dans le dossier
de travail (``--dossier``, par défaut ``../aite-videos`` à côté du dépôt) :
ce sont des sorties régénérables. Seule la vidéo compressée et sa vignette
entrent dans ``docs/guides/videos``.

Voix off : Kokoro, gratuit et local, voix française ``ff_siwis``, installé
à la première utilisation dans ``<dossier>/.venv-tts``. Ou ElevenLabs,
payant, avec ``--moteur-voix elevenlabs --voix-id <ID>`` et la clé dans
``ELEVENLABS_API_KEY`` (ou ``<dossier>/.env``). Chaque phrase est mise en
cache : relancer ne resynthétise que les phrases modifiées.
"""

import argparse
import glob
import hashlib
import importlib
import json
import os
import re
import shutil
import subprocess
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)

import marketing  # noqa: E402
import moteur  # noqa: E402
import musique  # noqa: E402
import presentateur  # noqa: E402
import sons  # noqa: E402

RACINE = os.path.abspath(os.path.join(ICI, '..', '..'))
HYPERFRAMES = 'hyperframes@0.8.139'
GSAP = 'gsap@3.14.2'
VOIX = 'ff_siwis'
VITESSE = '1.0'
SORTIE_DEPOT = os.path.join(RACINE, 'docs', 'guides', 'videos')

# Le document de référence de chaque vidéo, relatif à docs/.
GUIDES = {'presentation': 'GUIDE_RECETTE_UAT.md'}

# Les tutoriels marketing, une vidéo par fonctionnalité (scenarios/t*.py).
TUTORIELS = ['t01_reception', 't02_planning', 't03_folio', 't04_note_chambre', 't05_taxe_sejour', 't06_registre',
             't07_gouvernante', 't08_site_web', 't09_espaces', 't10_ardoises', 't11_fidelite', 't12_ventes',
             't13_stock', 't14_achats', 't15_direction']

# Les vidéos de la série : la présentation, puis les tutoriels.
ORDRE = ['presentation'] + TUTORIELS

# Les icônes des applications de la barre MuK, celles que livrent les modules
# (jamais redessinées) : chemin relatif au dossier d'Odoo 18, ou au dépôt.
ODOO = os.environ.get('ODOO_DIR', os.path.abspath(os.path.join(RACINE, '..', 'odoo18')))
ICONES_APPS = {
    'direction': ('odoo', 'addons/web/static/img/default_icon_app.png'),
    'discussion': ('odoo', 'addons/mail/static/description/icon.png'),
    'hotel': ('depot', 'addons/aite_hotel_management/static/description/icon.png'),
    'tableaux': ('odoo', 'addons/spreadsheet_dashboard/static/description/icon.png'),
    'pos-credit': ('depot', 'addons/aite_pos_credit/static/description/icon.png'),
    'point-de-vente': ('odoo', 'addons/point_of_sale/static/description/icon.png'),
    'facturation': ('odoo', 'addons/account/static/description/icon.png'),
    'site-web': ('odoo', 'addons/website/static/description/icon.png'),
    'achats': ('odoo', 'addons/purchase/static/description/icon.png'),
    'inventaire': ('odoo', 'addons/stock/static/description/icon.png'),
    'maintenance': ('odoo', 'addons/maintenance/static/description/icon.png'),
    'apps': ('odoo', 'odoo/addons/base/static/description/modules.png'),
    'parametres': ('odoo', 'odoo/addons/base/static/description/settings.png'),
}

# La police de l'interface rejouée : Inter, installée sur la machine de
# production (paquet fonts-inter) ; copiée dans le projet, jamais dans le dépôt.
POLICES = '/usr/share/fonts/opentype/inter'
GRAISSES = ('Regular', 'Medium', 'SemiBold', 'Bold', 'ExtraBold')


def journal(*morceaux):
    print(' '.join(str(m) for m in morceaux), flush=True)


def lancer(commande, dossier=None, env=None, capture=True, delai=1800):
    resultat = subprocess.run(commande, cwd=dossier, env=env, capture_output=capture, text=True, timeout=delai)
    return resultat


def sans_couleurs(texte):
    return re.sub(r'\x1b\[[0-9;?]*[A-Za-z]', '', texte or '')


# ------------------------------------------------------------ prérequis --

# Un Chrome sans interface déjà installé : Playwright, dans les environnements
# cloud de Claude Code.
NAVIGATEURS_LOCAUX = ['/opt/pw-browsers/chromium_headless_shell-*/chrome-linux/headless_shell']


def navigateur():
    """HyperFrames télécharge son Chrome (storage.googleapis.com) au premier
    rendu. Tant que ce téléchargement n'a pas eu lieu, on lui désigne un Chrome
    sans interface déjà présent sur la machine, s'il y en a un : un accès
    réseau restreint n'a plus alors à laisser passer ce téléchargement.
    ``HYPERFRAMES_BROWSER_PATH``, s'il est posé, reste prioritaire."""
    if os.environ.get('HYPERFRAMES_BROWSER_PATH'):
        return
    cache = os.path.expanduser('~/.cache/hyperframes/chrome')
    if os.path.isdir(cache) and os.listdir(cache):
        return
    for motif in NAVIGATEURS_LOCAUX:
        trouves = sorted(glob.glob(motif))
        if trouves:
            os.environ['HYPERFRAMES_BROWSER_PATH'] = trouves[-1]
            journal('navigateur local :', trouves[-1])
            return


def preparer(dossier):
    os.makedirs(dossier, exist_ok=True)
    navigateur()
    gsap = os.path.join(dossier, 'node_modules', 'gsap', 'dist', 'gsap.min.js')
    if not os.path.exists(gsap):
        journal('· installation de', GSAP)
        if not os.path.exists(os.path.join(dossier, 'package.json')):
            with open(os.path.join(dossier, 'package.json'), 'w') as f:
                f.write('{"name": "aite-videos", "private": true}\n')
        r = lancer(['npm', 'install', '--no-audit', '--no-fund', GSAP], dossier)
        if r.returncode != 0:
            sys.exit('npm install %s a échoué :\n%s' % (GSAP, r.stderr))
    return gsap


def python_tts(dossier):
    venv = os.path.join(dossier, '.venv-tts')
    py = os.path.join(venv, 'bin', 'python')
    if not os.path.exists(py):
        journal('· installation de Kokoro (voix off locale)')
        lancer([sys.executable, '-m', 'venv', venv], capture=False)
        r = lancer([os.path.join(venv, 'bin', 'pip'), 'install', '-q', 'kokoro-onnx', 'soundfile'])
        if r.returncode != 0:
            sys.exit('Installation de Kokoro impossible :\n%s' % r.stderr)
    return py


def duree_media(chemin):
    r = lancer(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', chemin])
    return float(r.stdout.strip())


# ------------------------------------------------------------- voix off --

# Les mots que Kokoro lit « à l'anglaise » : réécrits pour la voix seulement,
# juste avant la synthèse (les scénarios gardent l'orthographe de l'écran).
PRONONCIATION = {'Odoo': 'Odou', 'VVIP': 'double VIP', 'pressing': 'pressinng'}


def prononcer(texte):
    for mot, dit in PRONONCIATION.items():
        texte = re.sub(r'\b%s\b' % re.escape(mot), dit, texte)
    return texte


def est_tutoriel(scenario):
    return 'accroche' in scenario


def textes_voix(scenario):
    """Toutes les phrases de la vidéo, par case : scènes fixes, cartes de
    chapitre (``chap-N``) et étapes (``cN-etape-M``) ; pour un tutoriel,
    accroche, révélation, étapes (``etape-N``), résultats, appel à l'action."""
    if est_tutoriel(scenario):
        return {case: prononcer(t) for case, t in marketing.textes_voix(scenario).items()}
    textes = dict(scenario.get('voix', {}))
    for n, chap in enumerate(scenario['chapitres'], 1):
        if chap.get('voix'):
            textes['chap-%d' % n] = chap['voix']
        for m, etape in enumerate(chap['etapes'], 1):
            if etape.get('voix'):
                textes['c%d-etape-%d' % (n, m)] = etape['voix']
    return {case: prononcer(t) for case, t in textes.items()}


def cle_elevenlabs(dossier):
    """La clé ElevenLabs : variable d'environnement, ou ``.env`` du dossier de
    travail. Jamais dans le dépôt, jamais affichée.

    Rend None si elle est introuvable : dans un environnement cloud de Claude
    Code, la clé peut être un « API credential » de l'environnement, que le
    proxy ajoute lui-même aux requêtes vers api.elevenlabs.io (en-tête
    ``xi-api-key``, sans préfixe). La session ne la voit jamais ; le script
    n'envoie alors aucun en-tête d'authentification.
    """
    cle = os.environ.get('ELEVENLABS_API_KEY')
    env = os.path.join(dossier, '.env')
    if not cle and os.path.exists(env):
        for ligne in open(env):
            if ligne.startswith('ELEVENLABS_API_KEY='):
                cle = ligne.split('=', 1)[1].strip().strip('"\'')
    return cle or None


AIDE_CLE = ('Clé ElevenLabs refusée ou absente. Deux façons de la fournir : la variable '
            'ELEVENLABS_API_KEY (ou le fichier .env du dossier de travail) ; ou, dans un environnement '
            'cloud de Claude Code, un « API credential » pour l\'hôte api.elevenlabs.io, en-tête '
            '« xi-api-key », préfixe vide. Permissions de la clé : Text to Speech, Voices → Read.')


def elevenlabs(dossier, texte, voix_id, modele, sortie):
    import urllib.error
    import urllib.request
    corps = {'text': texte, 'model_id': modele,
             'voice_settings': {'stability': 0.5, 'similarity_boost': 0.75, 'style': 0.0, 'use_speaker_boost': True}}
    requete = urllib.request.Request(
        'https://api.elevenlabs.io/v1/text-to-speech/%s?output_format=mp3_44100_128' % voix_id,
        data=json.dumps(corps).encode(), method='POST',
        headers={'Content-Type': 'application/json'})
    cle = cle_elevenlabs(dossier)
    if cle:
        requete.add_header('xi-api-key', cle)
    try:
        with urllib.request.urlopen(requete, timeout=120) as reponse:
            with open(sortie, 'wb') as f:
                f.write(reponse.read())
    except urllib.error.HTTPError as erreur:
        detail = erreur.read().decode(errors='replace')[:300]
        if erreur.code == 401:
            sys.exit('ElevenLabs 401 : %s\n%s' % (detail, AIDE_CLE))
        sys.exit('ElevenLabs %s : %s' % (erreur.code, detail))


def synthetiser(dossier, textes, moteur_voix='kokoro', voix_id=None, modele='eleven_multilingual_v2'):
    """Rend {case: chemin du .wav normalisé}, {case: durée}.

    Kokoro (défaut) : gratuit, local, voix ``ff_siwis``. ElevenLabs : payant,
    une voix choisie (``voix_id``), la clé dans ``ELEVENLABS_API_KEY``.
    """
    cache = os.path.join(dossier, 'voix-cache')
    os.makedirs(cache, exist_ok=True)
    if moteur_voix == 'elevenlabs' and not voix_id:
        sys.exit('--voix-id est requis avec ElevenLabs (Voices → Copy voice ID).')
    env = dict(os.environ, HYPERFRAMES_PYTHON=python_tts(dossier)) if moteur_voix == 'kokoro' else None
    fichiers, durees = {}, {}
    for case, texte in textes.items():
        if moteur_voix == 'kokoro':
            cle = [VOIX, VITESSE, texte]
        else:
            cle = ['elevenlabs', voix_id, modele, texte]
        empreinte = hashlib.sha256(json.dumps(cle).encode()).hexdigest()[:16]
        brut = os.path.join(cache, empreinte + ('.wav' if moteur_voix == 'kokoro' else '.mp3'))
        norme = os.path.join(cache, empreinte + '-n.wav')
        if not os.path.exists(norme):
            journal('  voix', case, '—', texte[:70] + ('…' if len(texte) > 70 else ''))
            if moteur_voix == 'kokoro':
                r = lancer(['npx', '--yes', HYPERFRAMES, 'tts', texte, '-v', VOIX, '-s', VITESSE, '-o', brut],
                           dossier, env=env)
                if r.returncode != 0 or not os.path.exists(brut):
                    sys.exit('Synthèse impossible pour %s :\n%s' % (case, sans_couleurs(r.stdout + r.stderr)[-2000:]))
            else:
                elevenlabs(dossier, texte, voix_id, modele, brut)
            # Volume homogène d'une phrase à l'autre et d'une vidéo à l'autre.
            r = lancer(['ffmpeg', '-v', 'error', '-y', '-i', brut, '-af', 'loudnorm=I=-16:TP=-1.5:LRA=7',
                        '-ar', '48000', '-ac', '1', norme])
            if r.returncode != 0:
                sys.exit('Normalisation impossible pour %s :\n%s' % (case, r.stderr))
        fichiers[case] = norme
        durees[case] = round(duree_media(norme), 3)
    return fichiers, durees


# -------------------------------------------------------------- projet --

def charger(profil):
    module = importlib.import_module('scenarios.%s' % profil)
    importlib.reload(module)
    return getattr(module, 'TUTORIEL', None) or module.SCENARIO


def ecrire_projet(dossier, scenario, gsap, voix, pres=None, avec_musique=True):
    """``pres`` (mode présentateur) : {'enregistrement', 'debuts', 'nom',
    'fonction', 'recadrage'}, voir presentateur.py."""
    slug = scenario['slug']
    projet = os.path.join(dossier, 'fr', slug)
    assets = os.path.join(projet, 'assets')
    for sous in ('fonts', 'logos', 'voix', 'sons', 'presentateur', 'icones'):
        shutil.rmtree(os.path.join(assets, sous), ignore_errors=True)
        os.makedirs(os.path.join(assets, sous), exist_ok=True)
    shutil.copy(os.path.join(ICI, 'shared', 'aite.css'), assets)
    shutil.copy(os.path.join(ICI, 'shared', 'aite-marketing.css'), assets)
    if est_tutoriel(scenario):
        for nom, (base, relatif) in ICONES_APPS.items():
            source = os.path.join(ODOO if base == 'odoo' else RACINE, relatif)
            if not os.path.exists(source):
                sys.exit('Icône introuvable : %s (ODOO_DIR = %s)' % (source, ODOO))
            shutil.copy(source, os.path.join(assets, 'icones', nom + '.png'))
    shutil.copy(os.path.join(ICI, 'shared', 'aite-motion.js'), assets)
    shutil.copy(gsap, assets)
    for graisse in GRAISSES:
        nom = 'Inter-%s.otf' % graisse
        source = os.path.join(POLICES, nom)
        if not os.path.exists(source):
            sys.exit('Police introuvable : %s (installer le paquet fonts-inter)' % source)
        shutil.copy(source, os.path.join(assets, 'fonts', nom))
    # Le logo d'AITE Consulting (docs/logo_aite.jpg, 220 × 120) agrandi deux
    # fois en Lanczos : il s'affiche jusqu'à 190 px de haut dans la vidéo.
    r = lancer(['ffmpeg', '-v', 'error', '-y', '-i', os.path.join(RACINE, 'docs', 'logo_aite.jpg'),
                '-vf', 'scale=440:-1:flags=lanczos', os.path.join(assets, 'logos', 'aite.png')])
    if r.returncode != 0:
        sys.exit('Logo AITE impossible à préparer :\n%s' % r.stderr)

    fichiers, durees = voix if voix else ({}, {})
    relatifs = {}
    for case, chemin in fichiers.items():
        nom = os.path.basename(chemin)
        shutil.copy(chemin, os.path.join(assets, 'voix', nom))
        relatifs[case] = 'assets/voix/' + nom

    # Les bruitages (son d'ouverture, clics) accompagnent la voix : une vidéo
    # muette n'en a pas.
    medaillon = {'video': 'assets/presentateur/piste.mp4', 'nom': pres['nom'], 'fonction': pres['fonction']} if pres else None
    classe = marketing.Tutoriel if est_tutoriel(scenario) else moteur.Video
    video = classe(scenario, durees_voix=durees, fichiers_voix=relatifs,
                   bruitages='assets/sons/bruitages.wav' if voix else None, presentateur=medaillon)
    html, total = video.construire()
    if video.bruitages:
        piste = os.path.join(projet, video.bruitages)
        sons.piste(video.sons, total, piste)
        if est_tutoriel(scenario) and avec_musique:
            # la musique de fond, mêlée aux bruitages, s'efface sous la voix
            musique.piste(total, video.phrases(), piste, piste, debut_plein=video.t_plein, debut_fin=video.t_cta)
    if pres:
        presentateur.piste_video(pres['enregistrement'], pres['debuts'], video.plages, total, moteur.AVANT_VOIX,
                                 os.path.join(projet, medaillon['video']), pres.get('recadrage'))
    with open(os.path.join(projet, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(html)
    with open(os.path.join(projet, 'hyperframes.json'), 'w') as f:
        json.dump({'paths': {'blocks': 'compositions', 'components': 'compositions/components', 'assets': 'assets'},
                   'media': {'autoProxy': True}}, f, indent=2)
    with open(os.path.join(projet, 'meta.json'), 'w') as f:
        json.dump({'id': video.id, 'name': 'AITE HOUSE — ' + scenario['titre']}, f, ensure_ascii=False, indent=2)
    with open(os.path.join(projet, 'package.json'), 'w') as f:
        json.dump({'name': 'aite-' + video.id, 'private': True, 'type': 'module',
                   'scripts': {'check': 'npx --yes %s check' % HYPERFRAMES,
                               'render': 'npx --yes %s render' % HYPERFRAMES}}, f, indent=2)
    with open(os.path.join(projet, 'plan-scenes.json'), 'w') as f:
        json.dump(instants_cles(video), f, indent=2)
    return projet, total, video


def instants_cles(video):
    """Les instants à photographier pour la planche contact : la fin de
    chaque scène et de chaque étape, juste avant les fondus."""
    instants = []
    for couche in video.couches:
        m = re.match(r'<div id="([^"]+)" class="[^"]*" data-start="([\d.]+)" data-duration="([\d.]+)"', couche)
        if m and m.group(1).startswith('sc-') and not m.group(1).startswith('sc-app'):
            instants.append(round(float(m.group(2)) + float(m.group(3)) - 0.5, 2))
    for o in video.ops:
        if o.get('op') == 'fromTo' and str(o.get('sel', '')).startswith('#leg-') and o['a'].get('autoAlpha') == 0:
            instants.append(round(o['t'] - 0.1, 2))
    instants.extend(video.reperes)
    return sorted(set(instants))


def verifier(projet):
    r = lancer(['npx', '--yes', HYPERFRAMES, 'check'], projet)
    sortie = sans_couleurs(r.stdout + r.stderr)
    erreurs = re.findall(r'(\d+) error\(s\)', sortie)
    resume = [l for l in sortie.splitlines() if re.search(r'error|✗|issues|checks pass|Check (passed|failed)', l)]
    return r.returncode, sortie, resume


def planche(projet):
    with open(os.path.join(projet, 'plan-scenes.json')) as f:
        instants = json.load(f)
    shutil.rmtree(os.path.join(projet, 'snapshots'), ignore_errors=True)
    r = lancer(['npx', '--yes', HYPERFRAMES, 'snapshot', '--at', ','.join('%.2f' % t for t in instants), '--no-end',
                '--timeout', '15000'], projet)
    # une planche par groupe d'images : contact-sheet.jpg, ou contact-sheet-1.jpg, -2.jpg…
    planches = sorted(glob.glob(os.path.join(projet, 'snapshots', 'contact-sheet*.jpg')))
    return ', '.join(planches) or '(aucune planche)', sans_couleurs(r.stdout + r.stderr)


def rendre(projet, scenario, muet):
    slug = scenario['slug']
    sortie = os.path.join(projet, 'renders', '%s-fr.mp4' % slug)
    os.makedirs(os.path.dirname(sortie), exist_ok=True)
    r = lancer(['npx', '--yes', HYPERFRAMES, 'render', '-o', sortie, '-w', '2', '-q', 'high'], projet, delai=3600)
    if r.returncode != 0 or not os.path.exists(sortie):
        sys.exit('Rendu impossible pour %s :\n%s' % (slug, sans_couleurs(r.stdout + r.stderr)[-3000:]))
    return sortie


# La piste stéréo du rendu ramenée en mono par la moyenne des deux canaux :
# « -ac 1 » les additionne à −3 dB chacun, soit +3 dB sur une voix identique
# des deux côtés, et les crêtes saturaient après l'encodage AAC.
MONO = 'pan=mono|c0=0.5*c0+0.5*c1'
SONIE = -16.0        # LUFS, la sonie de chaque vidéo livrée
PLAFOND = 0.794      # −2 dBFS : la marge que l'encodage AAC consomme


def sonie(source):
    """La sonie intégrée (LUFS) de la piste mono du rendu."""
    r = lancer(['ffmpeg', '-hide_banner', '-nostats', '-i', source, '-vn', '-af', MONO + ',ebur128', '-f', 'null', '-'])
    valeurs = re.findall(r'^\s+I:\s+(-?[\d.]+) LUFS', r.stderr, re.M)
    if not valeurs:
        sys.exit('Sonie illisible pour %s :\n%s' % (source, r.stderr[-1500:]))
    return float(valeurs[-1])


def compresser(source, scenario, dossier, muet, instant, sortie=SORTIE_DEPOT):
    """Copie web : H.264 CRF 28, +faststart ; voix et bruitages en AAC mono,
    ramenés à ``SONIE`` LUFS, crêtes plafonnées ; vignette à ``instant``
    (``Video.vignette``).

    ``sortie`` : le dossier des vidéos livrées (par défaut celui de la
    documentation) ; un autre dossier pour un essai qui ne doit rien écraser.
    """
    nom = nom_livre(scenario)
    os.makedirs(sortie, exist_ok=True)
    muette = os.path.join(dossier, 'muettes', nom + '.mp4')
    os.makedirs(os.path.dirname(muette), exist_ok=True)
    cible = os.path.join(sortie, nom + '.mp4')
    if muet:
        audio = ['-an']
    else:
        gain = SONIE - sonie(source)
        audio = ['-af', '%s,volume=%.2fdB,alimiter=limit=%.3f:level=false' % (MONO, gain, PLAFOND),
                 '-c:a', 'aac', '-b:a', '96k']
    r = lancer(['ffmpeg', '-v', 'error', '-y', '-i', source, '-c:v', 'libx264', '-preset', 'slow', '-crf', '28',
                '-pix_fmt', 'yuv420p', '-movflags', '+faststart'] + audio + [cible])
    if r.returncode != 0:
        sys.exit('Compression impossible :\n%s' % r.stderr)
    lancer(['ffmpeg', '-v', 'error', '-y', '-i', cible, '-c:v', 'copy', '-an', muette])
    return cible, vignette(cible, instant)


def nom_livre(scenario):
    """``NN-profil`` : le nom de la vidéo livrée, NN son rang dans ``ORDRE`` ;
    ``NN-tutoriel-fonction`` pour un tutoriel."""
    rang = ORDRE.index(scenario['profil']) + 1
    if est_tutoriel(scenario):
        return '%02d-tutoriel-%s' % (rang, scenario['slug'].split('-', 1)[-1])
    return '%02d-%s' % (rang, scenario['slug'].split('-', 1)[-1])


def vignette(cible, instant):
    """La vignette d'une vidéo livrée : son image à ``instant``, en .jpg à côté d'elle."""
    chemin = os.path.splitext(cible)[0] + '.jpg'
    lancer(['ffmpeg', '-v', 'error', '-y', '-ss', '%.2f' % instant, '-i', cible, '-frames:v', '1', '-q:v', '3',
            '-vf', 'scale=1280:-2', chemin])
    return chemin


PAGE = """<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AITE HOUSE — Vidéos</title>
<style>
  :root { --marine: #2A0F2B; --marine-700: #5A2160; --or: #ED9720; --sable: #ED9720; --fond: #F6F4F7;
          --texte: #1C2B39; --texte-2: #4A5B6B; }
  * { box-sizing: border-box; }
  body { margin: 0; font-family: Inter, "Segoe UI", Roboto, Arial, sans-serif; background: var(--fond); color: var(--texte); }
  header { background: linear-gradient(110deg, #902C8F, var(--marine)); color: #fff; padding: 40px 16px 34px;
           border-bottom: 5px solid var(--sable); }
  .cadre { max-width: 1240px; margin: 0 auto; padding: 0 16px; }
  header .k { font-size: 13px; font-weight: 700; letter-spacing: .22em; color: #F7BE6A; text-transform: uppercase; }
  header h1 { margin: 10px 0 8px; font-size: 34px; }
  header p { margin: 0; max-width: 760px; line-height: 1.55; color: #F3E8F3; }
  main { padding: 28px 0 48px; }
  .grille { display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 22px; }
  article { background: #fff; border-radius: 14px; overflow: hidden; border: 1px solid #E3E8EE;
            box-shadow: 0 6px 18px rgba(42,15,43,.06); }
  video { display: block; width: 100%; aspect-ratio: 16 / 9; background: var(--marine); }
  .corps { padding: 16px 18px 18px; }
  .num { font-size: 12px; font-weight: 800; letter-spacing: .16em; color: #8A4E00; }
  h2 { margin: 6px 0 4px; font-size: 19px; }
  .meta { font-size: 14px; color: var(--texte-2); }
  .liens { margin-top: 12px; display: flex; gap: 14px; flex-wrap: wrap; font-size: 14px; }
  .liens a { color: #714B67; font-weight: 600; text-decoration: none; }
  .liens a:hover { text-decoration: underline; }
  footer { padding: 0 16px 40px; font-size: 13px; color: var(--texte-2); text-align: center; }
</style>
</head>
<body>
<header><div class="cadre"><div class="k">AITE HOUSE · Suite hôtelière sur Odoo 18</div>
<h1>Vidéos de présentation et tutoriels</h1>
<p>La solution présentée poste par poste, puis un tutoriel par fonctionnalité : chaque geste est rejoué dans
l'interface (Odoo 18, thème MuK), avec ses vrais libellés, sur des données de démonstration fictives.</p></div></header>
<main><div class="cadre"><div class="grille">
%(cartes)s
</div></div></main>
<footer>AITE Consulting · AITE HOUSE · générée par docs/videos/produire.py</footer>
</body>
</html>
"""


def ecrire_index():
    """La page qui présente la série : une carte par vidéo présente."""
    cartes = []
    for rang, profil in enumerate(ORDRE, 1):
        try:
            scenario = charger(profil)
        except ModuleNotFoundError:
            continue
        nom = nom_livre(scenario)
        video = os.path.join(SORTIE_DEPOT, nom + '.mp4')
        if not os.path.exists(video):
            continue
        duree = duree_media(video)
        mo = os.path.getsize(video) / 1e6
        pdf = GUIDES.get(profil)
        lien_pdf = '<a href="../%s">Document de référence</a>' % pdf if pdf else ''
        genre = ('TUTORIEL %d' % scenario['numero']) if est_tutoriel(scenario) else 'PRÉSENTATION'
        cartes.append(
            '<article><video controls preload="none" poster="%s.jpg" src="%s.mp4"></video><div class="corps">'
            '<div class="num">%02d · %s</div><h2>%s</h2><div class="meta">%d min %02d s · %.1f Mo</div>'
            '<div class="liens">%s<a href="%s.mp4" download>Télécharger</a></div></div></article>'
            % (nom, nom, rang, genre, escape_html(scenario['titre']), int(duree) // 60, int(duree) % 60, mo,
               lien_pdf, nom))
    with open(os.path.join(SORTIE_DEPOT, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(PAGE.replace('%(cartes)s', '\n'.join(cartes)))
    return len(cartes)


def escape_html(texte):
    import html
    return html.escape(texte)


def produire(profil, args, gsap):
    scenario = charger(profil)
    journal('▶', scenario['slug'], '—', scenario['titre'])
    if args.script:
        os.makedirs(os.path.join(args.dossier, 'scripts'), exist_ok=True)
        chemin = presentateur.script(scenario, textes_voix(scenario),
                                     os.path.join(args.dossier, 'scripts', 'script-%s.md' % scenario['slug']))
        journal('  script du présentateur', chemin)
        return {'profil': profil, 'script': chemin}
    voix, pres = None, None
    if args.presentateur:
        # la voix et l'image du présentateur remplacent la voix de synthèse
        fichiers, durees, debuts = presentateur.preparer(args.presentateur, scenario, textes_voix(scenario), args.dossier)
        voix = (fichiers, durees)
        pres = {'enregistrement': os.path.abspath(args.presentateur), 'debuts': debuts, 'nom': args.presentateur_nom,
                'fonction': args.presentateur_fonction, 'recadrage': args.recadrage}
    elif not args.muet:
        voix = synthetiser(args.dossier, textes_voix(scenario), args.moteur_voix, args.voix_id)
    projet, total, video = ecrire_projet(args.dossier, scenario, gsap, voix, pres, avec_musique=not args.sans_musique)
    journal('  projet', projet, '— %.1f s' % total)
    for alerte in video.alertes:
        journal('  ⚠', alerte)
    resultat = {'profil': profil, 'slug': scenario['slug'], 'duree': total, 'projet': projet}
    if args.vignettes:
        # la vidéo livrée garde son rendu ; seule sa vignette est refaite
        cible = os.path.join(args.sortie, nom_livre(scenario) + '.mp4')
        resultat['vignette'] = vignette(cible, video.vignette())
        journal('  vignette', os.path.relpath(resultat['vignette'], RACINE), 'à %.2f s' % video.vignette())
        return resultat
    if not args.sans_check:
        code, sortie, resume = verifier(projet)
        resultat['check'] = 'ok' if code == 0 else 'échec'
        for ligne in resume:
            journal('   ', ligne.strip())
        # le journal est écrit à chaque passe : un échec ancien ne survit pas à un check réussi
        with open(os.path.join(projet, 'check.log'), 'w') as f:
            f.write(sortie)
        if code != 0:
            journal('  check en échec — détail dans', os.path.join(projet, 'check.log'))
    if args.planche:
        chemin, sortie = planche(projet)
        resultat['planche'] = chemin
        journal('  planche', chemin)
    if args.rendu:
        source = rendre(projet, scenario, args.muet)
        cible, image = compresser(source, scenario, args.dossier, args.muet, video.vignette(), args.sortie)
        taille = os.path.getsize(cible) / 1e6
        resultat.update({'video': cible, 'vignette': image, 'mo': round(taille, 2)})
        journal('  vidéo', os.path.relpath(cible, RACINE), '— %.1f Mo' % taille)
    return resultat


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('profils', nargs='*', help='profils à produire (nom du fichier de scénario)')
    p.add_argument('--tout', action='store_true')
    p.add_argument('--dossier', default=os.path.abspath(os.path.join(RACINE, '..', 'aite-videos')))
    p.add_argument('--muet', action='store_true', help='sans voix off')
    p.add_argument('--moteur-voix', choices=['kokoro', 'elevenlabs'], default='kokoro',
                   help='kokoro (gratuit, local) ou elevenlabs (payant, clé ELEVENLABS_API_KEY)')
    p.add_argument('--voix-id', help='identifiant de la voix ElevenLabs')
    p.add_argument('--sortie', default=None,
                   help='dossier des vidéos compressées (par défaut docs/guides/videos ; en mode présentateur, '
                        '<dossier>/presentateur) ; un autre dossier pour un essai, par exemple ../aite-videos/essais')
    p.add_argument('--script', action='store_true', help='écrire le script à lire face caméra (mode présentateur)')
    p.add_argument('--presentateur', help='votre enregistrement face caméra : il remplace la voix de synthèse')
    p.add_argument('--presentateur-nom', default='', help='le nom affiché sous le médaillon')
    p.add_argument('--presentateur-fonction', default='', help='la fonction affichée sous le nom')
    p.add_argument('--recadrage', help='recadrage ffmpeg largeur:hauteur:x:y (par défaut, un carré au centre)')
    p.add_argument('--planche', action='store_true', help='planche contact (snapshots)')
    p.add_argument('--rendu', action='store_true', help='rendu MP4 et compression')
    p.add_argument('--sans-check', action='store_true')
    p.add_argument('--sans-musique', action='store_true', help='tutoriels : sans la musique de fond')
    p.add_argument('--vignettes', action='store_true',
                   help='refaire seulement les vignettes des vidéos livrées, sans rendu ; avec les options de voix '
                        'de la série, dont dépend le découpage')
    p.add_argument('--index', action='store_true', help='régénérer seulement la page de la série')
    args = p.parse_args()
    profils = ORDRE if args.tout else args.profils
    if args.index and not profils:
        journal('page de la série :', ecrire_index(), 'vidéo(s)')
        return
    if not profils:
        p.error('indiquer un profil, ou --tout')
    args.dossier = os.path.abspath(args.dossier)
    if args.presentateur and len(profils) != 1:
        p.error('un enregistrement par vidéo : --presentateur avec un seul profil')
    if args.presentateur and any(p_.startswith('t') and p_[1:3].isdigit() for p_ in profils):
        p.error('le mode présentateur ne prend pas encore en charge les tutoriels')
    # une vidéo avec présentateur ne remplace jamais la série livrée sans --sortie explicite
    args.sortie = args.sortie or (os.path.join(args.dossier, 'presentateur') if args.presentateur else SORTIE_DEPOT)
    gsap = preparer(args.dossier)
    bilan = [produire(profil, args, gsap) for profil in profils]
    # Un essai rendu ailleurs (--sortie) ne touche pas la page de la série.
    if args.index or (args.rendu and os.path.abspath(args.sortie) == SORTIE_DEPOT):
        journal('page de la série :', ecrire_index(), 'vidéo(s) dans', os.path.relpath(SORTIE_DEPOT, RACINE))
    with open(os.path.join(args.dossier, 'bilan.json'), 'w') as f:
        json.dump(bilan, f, ensure_ascii=False, indent=2)
    journal('bilan :', os.path.join(args.dossier, 'bilan.json'))


if __name__ == '__main__':
    main()
