# -*- coding: utf-8 -*-
"""La musique de fond des tutoriels, synthétisée ici.

Aucun fichier son ni aucune musique sous licence : un court motif pop
« corporate », composé et joué par le code. Deux rendus donnent la même
piste (le bruit des balais a sa graine).

- tempo 100 battements par minute, ré majeur, grille I – vi – IV – V
  (ré, si mineur, sol, la), une mesure par accord ;
- un tapis d'accords doux (sinus légèrement désaccordés, attaque lente),
  une basse ronde sur les temps 1 et 3, un arpège pincé en croches
  (Karplus-Strong), une pulsation discrète (grosse caisse feutrée, balais) ;
- l'accroche n'a que le tapis et l'arpège qui monte ; tout entre à la
  révélation ; un accord final tenu sur l'appel à l'action ;
- la musique s'efface sous la voix (« ducking ») : −9 dB pendant chaque
  phrase, avec des pentes douces pour qu'on ne l'entende pas respirer.

``piste()`` écrit un WAV mono 48 kHz de la durée de la vidéo, déjà mêlé aux
bruitages de ``sons.py`` ; la sonie finale de la vidéo est fixée à la
compression (``produire.compresser``).
"""

import wave

import numpy as np

TAUX = 48000
TEMPO = 100.0
TEMPS = 60.0 / TEMPO            # un temps, en secondes
MESURE = 4 * TEMPS              # une mesure de quatre temps

# Ré majeur : ré, si mineur, sol, la — en hertz, voix du tapis (octave 3-4).
LA4 = 440.0


def note(demi_tons):
    """Fréquence d'une note, en demi-tons depuis le la 440."""
    return LA4 * 2.0 ** (demi_tons / 12.0)


# Accords en demi-tons depuis la4 : (basse, notes du tapis, notes de l'arpège)
GRILLE = [
    (note(-31), [note(-19), note(-15), note(-12), note(-7)], [note(-7), note(-3), note(0), note(5)]),      # ré
    (note(-34), [note(-22), note(-19), note(-15), note(-10)], [note(-10), note(-7), note(-3), note(2)]),   # si m
    (note(-26), [note(-14), note(-10), note(-7), note(-2)], [note(-2), note(2), note(5), note(10)]),       # sol
    (note(-24), [note(-12), note(-8), note(-5), note(0)], [note(0), note(4), note(7), note(12)]),          # la
]
NIVEAUX = {'tapis': 0.22, 'basse': 0.30, 'arpege': 0.17, 'caisse': 0.32, 'balais': 0.05}
DUCK = 10 ** (-9 / 20.0)        # −9 dB sous la voix


def _temps(n):
    return np.arange(n) / TAUX


def _enveloppe(n, attaque, relache):
    env = np.ones(n)
    a = min(n, int(attaque * TAUX))
    r = min(n - a, int(relache * TAUX))
    if a:
        env[:a] = np.linspace(0.0, 1.0, a)
    if r:
        env[n - r:] *= np.linspace(1.0, 0.0, r)
    return env


def tapis(accord, duree):
    n = int(duree * TAUX)
    t = _temps(n)
    v = np.zeros(n)
    for f in accord:
        for desaccord in (-0.0035, 0.0035):
            ff = f * (1 + desaccord)
            v += np.sin(2 * np.pi * ff * t) + 0.18 * np.sin(2 * np.pi * 2 * ff * t)
    v /= 2 * len(accord)
    # un léger trémolo lent donne du mouvement au tapis
    v *= 0.85 + 0.15 * np.sin(2 * np.pi * 0.5 * t)
    return v * _enveloppe(n, 0.35, 0.45)


def basse(f, duree):
    n = int(duree * TAUX)
    t = _temps(n)
    v = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * 2 * f * t)
    return v * np.exp(-t / 0.55) * _enveloppe(n, 0.008, 0.06)


def pince(f, duree, graine):
    """Une corde pincée (Karplus-Strong) : un bruit bref filtré en boucle."""
    n = int(duree * TAUX)
    periode = max(2, int(round(TAUX / f)))
    hasard = np.random.default_rng(graine)
    tampon = hasard.uniform(-1.0, 1.0, periode)
    sortie = np.zeros(n)
    for i in range(n):
        j = i % periode
        sortie[i] = tampon[j]
        tampon[j] = 0.4985 * (tampon[j] + tampon[(j + 1) % periode])
    return sortie * _enveloppe(n, 0.002, 0.05)


def caisse(duree=0.35):
    n = int(duree * TAUX)
    t = _temps(n)
    f = 52.0 + 70.0 * np.exp(-t / 0.035)
    phase = 2 * np.pi * np.cumsum(f) / TAUX
    return np.sin(phase) * np.exp(-t / 0.11)


def balais(duree=0.09, graine=11):
    n = int(duree * TAUX)
    t = _temps(n)
    bruit = np.random.default_rng(graine).uniform(-1.0, 1.0, n)
    # passe-haut grossier : la différence première garde le souffle aigu
    haut = np.concatenate([[0.0], np.diff(bruit)])
    return haut * np.exp(-t / 0.025)


def _poser(piste, son, instant, niveau):
    d = int(round(instant * TAUX))
    if d >= len(piste):
        return
    f = min(len(piste), d + len(son))
    piste[d:f] += niveau * son[:f - d]


def composer(duree, debut_plein=0.0, debut_fin=None):
    """La musique sur ``duree`` secondes. Avant ``debut_plein`` (l'accroche) :
    tapis et arpège seuls ; ensuite tout le groupe ; à partir de
    ``debut_fin`` : un accord de ré tenu qui s'éteint."""
    n = int(np.ceil(duree * TAUX)) + TAUX
    piste = np.zeros(n)
    fin = duree if debut_fin is None else debut_fin
    cache_pince = {}
    mesure = 0
    t = 0.0
    while t < fin:
        b, accord, arpege = GRILLE[mesure % len(GRILLE)]
        _poser(piste, tapis(accord, MESURE + 0.4), t, NIVEAUX['tapis'])
        plein = t >= debut_plein - 1e-6
        for k in range(8):                                   # huit croches par mesure
            tk = t + k * TEMPS / 2
            if tk >= fin:
                break
            f = arpege[(k if mesure % 2 == 0 else 7 - k) % 4]
            cle = (round(f, 2), k % 3)
            if cle not in cache_pince:
                cache_pince[cle] = pince(f, 0.9, graine=k % 3 + 1)
            montee = 1.0 if plein else min(1.0, 0.35 + 0.65 * tk / max(0.1, debut_plein))
            _poser(piste, cache_pince[cle], tk, NIVEAUX['arpege'] * montee * (1.0 if k % 2 == 0 else 0.7))
        if plein:
            for k in (0, 2):
                _poser(piste, basse(b, TEMPS * 2), t + k * TEMPS, NIVEAUX['basse'])
            for k in range(4):
                _poser(piste, caisse(), t + k * TEMPS, NIVEAUX['caisse'] * (1.0 if k % 2 == 0 else 0.55))
                _poser(piste, balais(graine=11 + k), t + k * TEMPS + TEMPS / 2, NIVEAUX['balais'])
        t += MESURE
        mesure += 1
    if debut_fin is not None:
        reste = max(1.0, duree - debut_fin + 0.6)
        b, accord, arpege = GRILLE[0]
        n_reste = int(reste * TAUX)
        accord_fin = tapis(accord + [accord[0] * 2], reste)
        accord_fin *= np.exp(-_temps(n_reste) / max(0.8, reste / 2.5))
        _poser(piste, accord_fin, debut_fin, NIVEAUX['tapis'] * 1.2)
        _poser(piste, basse(b, reste), debut_fin, NIVEAUX['basse'])
        for k, f in enumerate(arpege + [arpege[0] * 2]):
            _poser(piste, pince(f, 1.6, graine=k + 1), debut_fin + 0.09 * k, NIVEAUX['arpege'])
    piste = piste[:int(np.ceil(duree * TAUX))]
    # fondu d'entrée et de sortie
    fondu = int(0.8 * TAUX)
    piste[:fondu] *= np.linspace(0.0, 1.0, fondu)
    piste[-fondu:] *= np.linspace(1.0, 0.0, fondu)
    return piste


def ducking(n, phrases, pente=0.25):
    """Le gain de la musique : 1 hors des phrases, ``DUCK`` pendant, avec des
    pentes de ``pente`` secondes. ``phrases`` = [(début, durée)]."""
    gain = np.ones(n)
    p = int(pente * TAUX)
    for debut, duree in phrases:
        a = int((debut - pente) * TAUX)
        b = int((debut + duree + 0.1) * TAUX)
        for i0, i1, de, a_ in ((a, a + p, 1.0, DUCK), (b, b + p, DUCK, 1.0)):
            lo, hi = max(0, i0), min(n, i1)
            if hi > lo:
                rampe = np.linspace(de, a_, i1 - i0)[lo - i0:hi - i0]
                gain[lo:hi] = np.minimum(gain[lo:hi], rampe)
        lo, hi = max(0, a + p), min(n, b)
        if hi > lo:
            gain[lo:hi] = np.minimum(gain[lo:hi], DUCK)
    return gain


def piste(duree, phrases, bruitages, chemin, debut_plein=0.0, debut_fin=None, crete_musique=0.30):
    """Écrit la piste « musique + bruitages » : ``phrases`` = [(début, durée)]
    de la voix off, ``bruitages`` = chemin du WAV de ``sons.piste`` (mono
    48 kHz), ``crete_musique`` : la crête de la musique hors voix."""
    musique = composer(duree, debut_plein, debut_fin)
    musique *= crete_musique / (np.max(np.abs(musique)) or 1.0)
    musique *= ducking(len(musique), phrases)
    with wave.open(bruitages, 'rb') as f:
        brut = np.frombuffer(f.readframes(f.getnframes()), dtype=np.int16).astype(np.float64) / 32767.0
    n = max(len(musique), len(brut))
    mix = np.zeros(n)
    mix[:len(musique)] += musique
    mix[:len(brut)] += brut
    mix = np.clip(mix, -0.99, 0.99)
    with wave.open(chemin, 'wb') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(TAUX)
        f.writeframes((mix * 32767).astype(np.int16).tobytes())
    return chemin
