# -*- coding: utf-8 -*-
"""Contrôler la voix off sans l'écouter.

    python3 docs/videos/ecouter.py presentation           # phonèmes (hors ligne)
    python3 docs/videos/ecouter.py --tout
    python3 docs/videos/ecouter.py presentation --transcrire  # retranscription

Deux contrôles :

- **Phonèmes** (par défaut, hors ligne) : chaque phrase passe par le
  phonétiseur de Kokoro, et les mots qu'il lit « en anglais » ou qu'il
  écrase en une syllabe sont signalés. C'est là que se cachent les mots mal
  prononcés : « AITE HOUSE » lu « ète ouze », « SPA » épelé, « pace » lu
  « pas ». La parade est d'écrire le mot autrement, pour la voix seulement
  (« Aïte haousse », « spa », « le rythme du mois »).
- **Retranscription** (``--transcrire``) : la phrase synthétisée est
  retranscrite par faster-whisper puis comparée au texte. Il faut
  ``pip install faster-whisper`` dans ``<dossier>/.venv-tts`` et un accès à
  huggingface.co pour télécharger le modèle au premier usage.
"""

import argparse
import difflib
import json
import os
import re
import subprocess
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)

import produire  # noqa: E402

PHONEMES = r'''
import json, re, sys
from kokoro_onnx.tokenizer import Tokenizer
t = Tokenizer()
for texte in json.loads(sys.argv[1]):
    ph = t.phonemize(texte, "fr-fr")
    anglais = re.findall(r"\(en\)(.*?)\(fr\)", ph)
    sigles = {m: t.phonemize(m, "fr-fr") for m in set(re.findall(r"\b[A-ZÀ-Ý][A-ZÀ-Ý0-9]+\b", texte))}
    print(json.dumps({"anglais": anglais, "sigles": sigles}, ensure_ascii=False), flush=True)
'''

# Sigles que la voix lit bien (vérifiés au phonétiseur), et ceux à réécrire.
BONS = {'MTN', 'TVA', 'SARL', 'PDF', 'CNI', 'VIP', 'VVIP', 'OTIF', 'DGI', 'MINTOUL', 'CFA'}
A_REECRIRE = {'AITE': 'Aïte', 'HOUSE': 'haousse', 'FCFA': 'francs', 'XAF': 'francs', 'ADR': 'prix moyen',
              'SPA': 'spa', 'POS': 'point de vente', 'UAT': 'recette', 'OTP': 'code', 'KPI': 'indicateur'}

TRANSCRIPTION = r'''
import json, sys
from faster_whisper import WhisperModel
modele = WhisperModel(sys.argv[1], device="cpu", compute_type="int8")
for chemin in json.loads(sys.argv[2]):
    segments, _ = modele.transcribe(chemin, language="fr", beam_size=5)
    print(json.dumps({"f": chemin, "t": " ".join(s.text.strip() for s in segments)}, ensure_ascii=False), flush=True)
'''

# Mots anglais que l'application emploie tels quels et que la voix peut garder.
ADMIS = {'Desk', 'FrontDesk', 'SWIFT', 'swift', 'Swift'}


def normaliser(texte):
    texte = texte.lower().replace('’', "'")
    texte = re.sub(r"[^\w' ]+", ' ', texte)
    return re.sub(r'\s+', ' ', texte).strip()


def phonemes(py, profil, textes):
    """Signale les passages lus en anglais et les sigles mal prononcés."""
    ordre = list(textes)
    r = subprocess.run([py, '-c', PHONEMES, json.dumps([textes[c] for c in ordre])], capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(r.stderr[-2000:])
    resultats = [json.loads(l) for l in r.stdout.splitlines() if l.startswith('{')]
    alertes = 0
    for case, res in zip(ordre, resultats):
        texte = textes[case]
        for segment in res['anglais']:
            mots = [m for m in re.findall(r"[A-Za-zÀ-ÿ']+", texte) if m in ADMIS]
            if mots and len(segment) < 12:
                continue                      # « Desk », « SWIFT » : admis
            alertes += 1
            print('⚠ %-24s %-10s lu en anglais : %s' % (profil, case, segment))
        for sigle, ph in sorted(res['sigles'].items()):
            if sigle in A_REECRIRE:
                alertes += 1
                print('⚠ %-24s %-10s « %s » → %s — écrire « %s »' % (profil, case, sigle, ph, A_REECRIRE[sigle]))
            elif sigle == 'CFA' and 'francs CFA' not in texte:
                alertes += 1
                print('⚠ %-24s %-10s « CFA » seul est lu « kfa » — écrire « francs CFA »' % (profil, case))
            elif sigle not in BONS:
                alertes += 1
                print('? %-24s %-10s « %s » → %s — sigle à vérifier' % (profil, case, sigle, ph))
    return alertes


def transcrire(py, args, profil, scenario):
    textes = produire.textes_voix(scenario)
    fichiers, _ = produire.synthetiser(args.dossier, textes)
    ordre = list(fichiers)
    r = subprocess.run([py, '-c', TRANSCRIPTION, args.modele, json.dumps([fichiers[c] for c in ordre])],
                       capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(r.stderr[-2000:])
    lus = [json.loads(l) for l in r.stdout.splitlines() if l.startswith('{')]
    for case, lu in zip(ordre, lus):
        ratio = difflib.SequenceMatcher(None, normaliser(textes[case]), normaliser(lu['t'])).ratio()
        marque = '  ' if ratio >= args.seuil else '⚠ '
        print('%s%-24s %-10s %.2f' % (marque, profil, case, ratio))
        if ratio < args.seuil:
            print('     écrit   :', textes[case])
            print('     entendu :', lu['t'])


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('profils', nargs='*')
    p.add_argument('--tout', action='store_true')
    p.add_argument('--transcrire', action='store_true')
    p.add_argument('--modele', default='small')
    p.add_argument('--seuil', type=float, default=0.85)
    p.add_argument('--dossier', default=os.path.abspath(os.path.join(produire.RACINE, '..', 'aite-videos')))
    args = p.parse_args()
    profils = produire.ORDRE if args.tout else args.profils
    if not profils:
        p.error('indiquer un profil, ou --tout')
    py = produire.python_tts(args.dossier)
    total = 0
    for profil in profils:
        try:
            scenario = produire.charger(profil)
        except ModuleNotFoundError:
            print('· %s : pas encore de scénario' % profil)
            continue
        if args.transcrire:
            transcrire(py, args, profil, scenario)
        else:
            total += phonemes(py, profil, produire.textes_voix(scenario))
    if not args.transcrire:
        print('%d mot(s) à reprendre' % total if total else 'aucun mot suspect')


if __name__ == '__main__':
    main()
