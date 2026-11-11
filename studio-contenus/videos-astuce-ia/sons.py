"""Musique de fond et bruitages, synthétisés (aucun fichier son extérieur, aucun hasard non fixé).
python sons.py <evenements.json> <duree> <sortie_musique.wav> <sortie_bruitages.wav>"""
import json, sys, numpy as np, wave
R = 48000
def ecrire(ch, x):
    x = np.clip(x, -1, 1); w = wave.open(ch, 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(R)
    w.writeframes((x * 32767).astype('<i2').tobytes()); w.close()
def env(n, a, r):  # attaque / relâche linéaires
    e = np.ones(n); a, r = int(a * R), int(r * R); e[:a] = np.linspace(0, 1, a) if a else 1; e[-r:] *= np.linspace(1, 0, r); return e
def note(f, d, forme='sin'):
    t = np.arange(int(d * R)) / R
    if forme == 'sin': return np.sin(2 * np.pi * f * t)
    return sum(np.sin(2 * np.pi * f * k * t) / k ** 2 * (-1) ** ((k - 1) // 2) for k in (1, 3, 5, 7))  # triangle doux
def musique(duree):
    bpm = 96; b = 60 / bpm; out = np.zeros(int((duree + 2) * R))
    # La mineur : Am7 · Fmaj7 · C · G, une mesure (4 temps) chacun
    acc = [[57, 60, 64, 67], [53, 57, 60, 64], [48, 55, 60, 64], [55, 59, 62, 67]]
    hz = lambda m: 440 * 2 ** ((m - 69) / 12)
    mesure = 4 * b; k = 0; t0 = 0.0
    while t0 < duree:
        c = acc[k % 4]; i0 = int(t0 * R)
        for m in c:  # nappe
            x = note(hz(m), mesure + .6, 'tri') * env(int((mesure + .6) * R), .5, .8) * .05
            out[i0:i0 + len(x)] += x[:len(out) - i0]
        x = note(hz(c[0] - 12), mesure, 'sin') * env(int(mesure * R), .02, .4) * .09  # basse
        out[i0:i0 + len(x)] += x[:len(out) - i0]
        for j in range(8):  # arpège en croches, pincé
            m = c[[0, 1, 2, 3, 2, 1, 2, 3][j]] + 12; d = b / 2; ij = i0 + int(j * d * R)
            n = int(1.2 * R); t = np.arange(n) / R
            x = (np.sin(2 * np.pi * hz(m) * t) + .3 * np.sin(4 * np.pi * hz(m) * t)) * np.exp(-t * 6) * .045
            out[ij:ij + n] += x[:max(0, len(out) - ij)]
        for j in range(4):  # pulsation douce : grosse caisse feutrée sur chaque temps
            ij = i0 + int(j * b * R); n = int(.25 * R); t = np.arange(n) / R
            x = np.sin(2 * np.pi * (55 + 60 * np.exp(-t * 30)) * t) * np.exp(-t * 18) * (.12 if j % 2 == 0 else .07)
            out[ij:ij + n] += x[:max(0, len(out) - ij)]
        t0 += mesure; k += 1
    out = out[:int(duree * R)]; n = len(out)
    out *= np.minimum(1, np.minimum(np.arange(n) / (1.5 * R), (n - np.arange(n)) / (2.5 * R)))
    return out / (np.abs(out).max() + 1e-9) * .8
def bruit(n, graine):
    return np.random.default_rng(graine).standard_normal(n)
def souffle():
    n = int(.6 * R); t = np.arange(n) / R; x = bruit(n, 7)
    # filtre passe-bas glissant (moyenne mobile qui se resserre) : le souffle monte puis s'éteint
    y = np.zeros(n); a = 0.0
    for i in range(n):
        k = .02 + .25 * min(1, t[i] / .35); a += k * (x[i] - a); y[i] = a
    return y * np.sin(np.pi * np.clip(t / .6, 0, 1)) ** 2 * 1.4
def pop():
    n = int(.12 * R); t = np.arange(n) / R
    return np.sin(2 * np.pi * (520 + 900 * np.exp(-t * 60)) * t) * np.exp(-t * 45) * .55
def clic():
    n = int(.05 * R); t = np.arange(n) / R
    return (np.sin(2 * np.pi * 2200 * t) * .5 + bruit(n, 3) * .3) * np.exp(-t * 160) * .6
if __name__ == '__main__':
    evs, duree, sm, sb = json.load(open(sys.argv[1])), float(sys.argv[2]), sys.argv[3], sys.argv[4]
    ecrire(sm, musique(duree))
    out = np.zeros(int((duree + 1) * R)); S = {'souffle': (souffle(), .22), 'pop': (pop(), .16), 'clic': (clic(), .28)}
    vus = set()
    for t, ty in sorted(evs):
        if (round(t, 2), ty) in vus or t < 0: continue
        vus.add((round(t, 2), ty)); x, g = S[ty]; i = int(t * R); out[i:i + len(x)] += x[:len(out) - i] * g
    ecrire(sb, out[:int(duree * R)])
