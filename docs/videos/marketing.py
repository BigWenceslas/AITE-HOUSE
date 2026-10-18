# -*- coding: utf-8 -*-
"""Le moteur des tutoriels marketing d'AITE HOUSE : une vidéo par fonctionnalité.

Même méthode que la vidéo de présentation (``moteur.py``) — l'interface est
rejouée en HTML avec les libellés exacts du code, la voix off pilote les
durées, les gestes sont posés sur une timeline GSAP déterministe — mais une
autre forme, celle des vidéos de lancement de logiciels :

    accroche → révélation → tutoriel (étapes, zooms, bulles) → résultats → appel à l'action

- **accroche** : la question qui fâche, et les cartes « problème » qui
  s'agitent autour (chacune tirée d'un document du dépôt) ;
- **révélation** : de grands cercles violets balaient l'écran, la carte AITE
  se pose, « AITE HOUSE », puis le nom de la fonctionnalité et sa promesse ;
- **tutoriel** : la fenêtre du navigateur, Odoo 18 habillé par le thème MuK,
  sur un fond violet ; en haut, les temps forts du tutoriel en pastilles ;
  en bas, la légende de l'étape ; la caméra peut zoomer sur un détail
  (geste ``zoom``) et des bulles désignent ce qu'il faut retenir
  (geste ``bulle``) ;
- **résultats** : trois cartes chiffrées, vérifiables dans le code ;
- **appel à l'action** : AITE Consulting, ses coordonnées publiques, et le
  tutoriel suivant de la série.

Une musique de fond synthétisée (``musique.py``) s'efface sous la voix.
"""

import json
from html import escape

import moteur
import sons
from ecrans import ICONES, curseur_svg, e, icone
from moteur import AVANT_VOIX, APRES_VOIX, CLIC_SONORE, PUIS, SORTIE, _g

MARQUE = moteur.MARQUE
SOUS_MARQUE = moteur.SOUS_MARQUE
# Coordonnées publiques d'AITE Consulting (README.md, docs/etude_comparative/build_etude.py).
CONTACT = ['info@aite-consulting.com', '(+237) 673 373 367', 'aite-consulting.com']
CHAINE = 'youtube.com/@aiteconsulting'

BASE = {'accroche': 7.5, 'revelation': 5.2, 'resultats': 7.0, 'cta': 6.5}
REVELATION_CERCLES = 0.9        # les cercles ont balayé l'écran : la carte AITE se pose

# Emplacements des cartes « problème » autour de la question (gauche, droite).
PLACES = [(110, 190), (1400, 170), (150, 470), (1440, 450), (110, 760), (1400, 740)]


# ------------------------------------------------------- gestes nouveaux --

def zoom(sel, s=1.5, d=0.8, fx=0.5, fy=0.5, **kw):
    """La caméra s'approche de l'élément ``sel`` (facteur ``s``), sans jamais
    laisser voir le bord de la fenêtre. Le curseur, l'anneau et les bulles
    sont dans la caméra : ils suivent."""
    return _g('zoom', sel=sel, s=s, d=d, fx=fx, fy=fy, **kw)


def dezoom(d=0.7, **kw):
    """La caméra revient au plan large."""
    return _g('dezoom', d=d, **kw)


def bulle(ident, sel, cote='droite', d=2.4, **kw):
    """Une bulle (``Tutoriel`` la compose depuis ``TUTORIEL['bulles']``)
    s'ouvre à côté de ``sel`` et se referme après ``d`` secondes, sans bloquer
    la suite des gestes."""
    return _g('bulle', ident=ident, sel=sel, cote=cote, d=d, **kw)


def reaction(ident, d=2.6, **kw):
    """Le personnage du tutoriel réagit (``TUTORIEL['reactions']``), dans le
    coin bas droit, sans bloquer."""
    return _g('reaction', ident=ident, d=d, **kw)


PUIS.update({'zoom': 0.2, 'dezoom': 0.15, 'bulle': 0.3, 'reaction': 0.2})


def textes_voix(tuto):
    """Les phrases d'un tutoriel, par case."""
    textes = {'accroche': tuto['accroche']['voix'], 'revelation': tuto['revelation']['voix'],
              'resultats': tuto['resultats']['voix'], 'cta': tuto['cta']['voix']}
    for m, etape in enumerate(tuto['etapes'], 1):
        if etape.get('voix'):
            textes['etape-%d' % m] = etape['voix']
    return textes


class Tutoriel(moteur.Video):
    """Un tutoriel marketing, construit à partir de ``TUTORIEL``."""

    def __init__(self, tuto, **kw):
        super().__init__(tuto, **kw)
        self.t_plein = 0.0          # l'instant où la musique passe au groupe complet
        self.t_cta = None           # l'instant de l'accord final

    # ------------------------------------------------------------ scènes --
    def scene_accroche(self, t):
        a = self.s['accroche']
        d = self.duree('accroche', BASE['accroche'])
        mots = ' '.join('<span class="mot%s">%s</span>' % (' fort' if m.startswith('*') else '', e(m.strip('*')))
                        for m in a['question'].split())
        cartes = ''.join('<div class="acc-carte acc-c%d" id="acc-c%d" style="left:%dpx;top:%dpx">%s<span>%s</span></div>'
                         % (i % 3, i, PLACES[i][0], PLACES[i][1], icone(ic, 'acc-ico'), e(txt))
                         for i, (ic, txt) in enumerate(a['douleurs'][:6]))
        html = ('<div class="scene-in mk-clair" id="acc-in"><div class="mk-rond r1"></div><div class="mk-rond r2"></div>'
                '<div class="acc-kicker" id="acc-k">%s</div><div class="acc-question" id="acc-q">%s</div>%s</div>'
                % (e(a.get('kicker', 'Et si on simplifiait ?')), mots, cartes))
        self.clip('sc-accroche', t, d, html, 1)
        self.entree('#acc-k', t + 0.15, y=16)
        self.entree('#acc-q .mot', t + 0.3, d=0.6, y=60, decalage=0.08)
        n = len(a['douleurs'][:6])
        for i in range(n):
            ti = t + 0.9 + 0.32 * i
            self.op(op='fromTo', sel='#acc-c%d' % i, de={'autoAlpha': 0, 'scale': 0.5, 'rotation': -8 + 4 * (i % 4)},
                    a={'autoAlpha': 1, 'scale': 1, 'rotation': -3 + 2 * (i % 4), 'duration': 0.55,
                       'ease': 'back.out(1.8)', 'immediateRender': True}, t=round(ti, 3))
            # les cartes flottent, chacune à son rythme : le désordre du quotidien
            self.op(op='fromTo', sel='#acc-c%d' % i, de={'y': 0},
                    a={'y': -14 + 4 * (i % 3), 'duration': 0.9 + 0.17 * i, 'yoyo': True,
                       'repeat': max(1, int((d - 2.4) / (0.9 + 0.17 * i))), 'ease': 'sine.inOut'}, t=round(ti + 0.55, 3))
        # à la fin, les cartes sont aspirées vers le centre : place à la solution
        fin = t + d - 0.75
        for i in range(n):
            self.op(op='to', sel='#acc-c%d' % i,
                    vars={'x': 960 - PLACES[i][0] - 170, 'y': 520 - PLACES[i][1], 'scale': 0.2, 'autoAlpha': 0,
                          'rotation': 0, 'duration': 0.55, 'ease': 'power3.in'}, t=round(fin + 0.03 * i, 3))
        self.op(op='to', sel='#acc-q', vars={'scale': 0.92, 'autoAlpha': 0, 'duration': 0.45, 'ease': 'power2.in'},
                t=round(fin + 0.15, 3))
        self.op(op='to', sel='#acc-k', vars={'autoAlpha': 0, 'duration': 0.3}, t=round(fin + 0.1, 3))
        self.poser_voix('accroche', t)
        self.reperes.append(round(t + d - 1.2, 2))
        return t + d

    def scene_revelation(self, t):
        r = self.s['revelation']
        d = self.duree('revelation', BASE['revelation'])
        html = ('<div class="scene-in mk-clair" id="rev-in"><div class="rev-cercle c1" id="rev-c1"></div>'
                '<div class="rev-cercle c2" id="rev-c2"></div><div class="rev-cercle c3" id="rev-c3"></div>'
                '<div class="rev-bloc"><div class="logo-carte" id="rev-logo"><img src="assets/logos/aite.png" alt=""></div>'
                '<div class="rev-marque" id="rev-marque">%s</div>'
                '<div class="rev-fonction" id="rev-f"><span class="num">Tutoriel %d</span>%s</div>'
                '<div class="rev-promesse" id="rev-p">%s</div></div></div>'
                % (''.join('<span class="espace"></span>' if c == ' ' else '<span class="lettre">%s</span>' % c
                           for c in MARQUE), self.s['numero'], e(self.s['fonction']), e(r['promesse'])))
        self.clip('sc-revelation', t, d, html, 2)
        self.op(op='fromTo', sel='#rev-c1', de={'scale': 0}, a={'scale': 1, 'duration': 0.9, 'ease': 'power3.out',
                                                                 'immediateRender': True}, t=round(t, 3))
        self.op(op='fromTo', sel='#rev-c2', de={'scale': 0}, a={'scale': 1, 'duration': 0.9, 'ease': 'power3.out',
                                                                 'immediateRender': True}, t=round(t + 0.12, 3))
        self.op(op='fromTo', sel='#rev-c3', de={'scale': 0}, a={'scale': 1, 'duration': 1.0, 'ease': 'power3.out',
                                                                 'immediateRender': True}, t=round(t + 0.22, 3))
        tl = t + REVELATION_CERCLES - 0.5
        self.op(op='fromTo', sel='#rev-logo', de={'autoAlpha': 0, 'y': 26, 'scale': 0.8},
                a={'autoAlpha': 1, 'y': 0, 'scale': 1, 'duration': 0.6, 'ease': 'back.out(1.7)', 'immediateRender': True},
                t=round(tl, 3))
        self.entree('#rev-marque .lettre', tl + 0.35, d=0.5, y=46, decalage=0.045)
        self.entree('#rev-f', tl + 0.95, d=0.55, y=30)
        self.entree('#rev-p', tl + 1.35, d=0.5, y=20)
        self.sons.append((round(t + REVELATION_CERCLES - sons.CARILLON, 3), 'ouverture'))
        self.sortie('#rev-in', t + d - SORTIE)
        self.poser_voix('revelation', t + 0.6)
        self.reperes.append(round(t + d - 0.6, 2))
        self.t_plein = t
        return t + d

    def scene_tutoriel(self, t):
        s = self.s
        etapes = s['etapes']
        temps = s.get('temps', [])
        nom, role = s['personnage']
        self.vues = dict(s.get('vues_initiales', {}))
        pastilles = ''.join('<span class="tu-pastille" id="tu-p%d"><b>%d</b>%s</span>' % (i, i + 1, e(x))
                            for i, x in enumerate(temps))
        bulles = ''.join('<div class="bulle masque" id="%s"><span class="b-ico">%s</span><span>%s</span></div>'
                         % (i, ICONES['eclair'], e(txt)) for i, txt in s.get('bulles', {}).items())
        reactions = ''.join('<div class="reaction masque" id="%s"><span class="av">%s</span><div><b>%s</b>'
                            '<span>%s</span></div></div>' % (i, e(nom[0]), e(nom.split()[0]), e(txt))
                            for i, txt in s.get('reactions', {}).items())
        legendes = []
        debut = t
        self.entree('#tu-fond', t, d=0.5, y=0)
        self.entree('#tu-perso', t + 0.3, y=-16)
        self.entree('#tu-pastilles .tu-pastille', t + 0.35, d=0.4, y=-20, decalage=0.08)
        self.op(op='fromTo', sel='#navigateur', de={'autoAlpha': 0, 'y': 120, 'scale': 0.94},
                a={'autoAlpha': 1, 'y': 0, 'scale': 1, 'duration': 0.8, 'ease': 'power3.out', 'immediateRender': True},
                t=round(t + 0.15, 3))
        cle = self.cible('#' + s['app'], 0.55, 0.5)
        self.op(op='set', sel='#curseur', vars={'x': 1500, 'y': 1000, 'autoAlpha': 0}, t=round(t, 3))
        self.op(op='to', sel='#curseur', vars={'autoAlpha': 1, 'duration': 0.3}, t=round(t + 0.6, 3))
        self.op(op='curseur', cle=cle, t=round(t + 0.7, 3), d=0.8)
        k = t + 1.2
        actif = None
        for m, etape in enumerate(etapes, 1):
            case = 'etape-%d' % m
            t0 = k
            if temps and etape.get('temps') is not None and etape['temps'] != actif:
                if actif is not None:
                    self.op(op='classe', sel='#tu-p%d' % actif, ajouter=['fait'], retirer=['actif'], t=round(t0, 3))
                self.op(op='classe', sel='#tu-p%d' % etape['temps'], ajouter=['actif'], retirer=[], t=round(t0, 3))
                actif = etape['temps']
            fin_gestes = self.jouer(etape['gestes'], t0 + 0.35)
            d = max(fin_gestes - t0 + 0.5, etape.get('min', 0))
            dv = self.durees_voix.get(case)
            if dv and d - (AVANT_VOIX + dv) > 3.0:
                self.alertes.append('étape %d : %.1f s d\'image pour %.1f s de voix — allonger la phrase ou scinder'
                                    % (m, d, dv))
            d = self.duree(case, d)
            self.etapes_t[(1, m)] = (round(t0, 3), round(d, 3))
            legendes.append('<div class="tu-leg masque" id="leg-1-%d"><div class="num">%d</div><div class="txt">'
                            '<div class="t">%s</div><div class="s">%s</div></div></div>'
                            % (m, m, e(etape['titre']), e(etape['texte'])))
            self.entree('#leg-1-%d' % m, t0, d=0.45, x=-40, y=0)
            self.sortie('#leg-1-%d' % m, t0 + d - 0.3, d=0.3)
            self.poser_voix(case, t0)
            self.reperes.append(round(t0 + d / 2.0, 2))
            k = t0 + d
        fin = k + 0.6
        self.op(op='to', sel='#cam', vars={'x': 0, 'y': 0, 'scale': 1, 'duration': 0.4, 'ease': 'power2.inOut'},
                t=round(fin - 0.9, 3))
        self.op(op='to', sel='#curseur', vars={'autoAlpha': 0, 'duration': 0.25}, t=round(fin - 0.9, 3))
        self.sortie('#tu-in', fin - SORTIE)
        avancement = ('<div class="tu-avance"><i id="tu-barre"></i></div>')
        self.op(op='fromTo', sel='#tu-barre', de={'scaleX': 0, 'transformOrigin': '0% 50%'},
                a={'scaleX': 1, 'duration': round(fin - debut - 0.6, 3), 'ease': 'none', 'immediateRender': True},
                t=round(debut + 0.3, 3))
        html = ('<div class="scene-in" id="tu-in"><div class="tu-fond" id="tu-fond"><div class="mk-rond r3"></div>'
                '<div class="mk-rond r4"></div></div>'
                '<div class="tu-pastilles" id="tu-pastilles">%s</div>'
                '<div class="tu-perso" id="tu-perso"><span class="av">%s</span><span><b>%s</b> · %s</span></div>'
                '<div class="camera" id="cam">%s'
                '<div id="curseur">%s</div><div id="onde"></div><div class="anneau" id="anneau"></div>%s</div>'
                '%s%s%s</div>'
                % (pastilles, e(nom[0]), e(nom), e(role), s['ecran'], curseur_svg(), bulles, ''.join(legendes),
                   reactions, avancement))
        self.clip('sc-tutoriel', debut, fin - debut, html, 3)
        return fin

    def scene_resultats(self, t):
        r = self.s['resultats']
        d = self.duree('resultats', BASE['resultats'])
        cartes = []
        for i, c in enumerate(r['cartes'][:3]):
            valeur = c['valeur']
            cartes.append('<div class="res-carte" id="res-c%d"><div class="res-ico">%s</div>'
                          '<div class="res-v"><b id="res-v%d">%s</b><small>%s</small></div><div class="res-t">%s</div></div>'
                          % (i, ICONES[c.get('icone', 'coche')], i, e(valeur), e(c.get('unite', '')), e(c['texte'])))
        html = ('<div class="scene-in mk-clair" id="res-in"><div class="mk-rond r1"></div>'
                '<div class="res-k" id="res-k">%s</div><div class="res-titre" id="res-t">%s</div>'
                '<div class="res-cartes">%s</div></div>'
                % (e(r.get('kicker', 'Ce qui change')), e(r['titre']), ''.join(cartes)))
        self.clip('sc-resultats', t, d, html, 4)
        self.entree('#res-k', t + 0.1, y=16)
        self.entree('#res-t', t + 0.25, d=0.6, y=40)
        self.entree('#res-in .res-carte', t + 0.7, d=0.6, y=60, decalage=0.18)
        for i, c in enumerate(r['cartes'][:3]):
            if isinstance(c.get('compter'), (int, float)):
                self.op(op='compteur', sel='#res-v%d' % i, de=0, a=c['compter'], d=1.1,
                        decimales=c.get('decimales', 0), avant='', apres='', t=round(t + 0.9 + 0.18 * i, 3))
        self.sortie('#res-in', t + d - SORTIE)
        self.poser_voix('resultats', t)
        self.reperes.append(round(t + d - 0.6, 2))
        return t + d

    def scene_cta(self, t):
        c = self.s['cta']
        d = self.duree('cta', BASE['cta'])
        suivant = ('<div class="cta-suivant" id="cta-s">Tutoriel suivant · <b>%s</b></div>' % e(c['suivant'])
                   if c.get('suivant') else '')
        contacts = ''.join('<span>%s</span>' % e(x) for x in CONTACT)
        html = ('<div class="scene-in mk-clair" id="cta-in"><div class="rev-cercle c1 fixe"></div>'
                '<div class="rev-cercle c3 fixe"></div><div class="cta-bloc">'
                '<div class="logo-carte" id="cta-logo"><img src="assets/logos/aite.png" alt=""></div>'
                '<div class="cta-marque" id="cta-m">%s</div><div class="cta-sous" id="cta-ss">%s</div>'
                '<div class="cta-bouton" id="cta-b">%s</div>'
                '<div class="cta-contacts" id="cta-c">%s</div>'
                '<div class="cta-chaine" id="cta-ch">%s</div>%s</div></div>'
                % (e(MARQUE), e(SOUS_MARQUE), e(c.get('appel', 'Demandez votre démonstration')), contacts,
                   e(CHAINE), suivant))
        self.clip('sc-cta', t, d, html, 4)
        self.entree('#cta-logo', t + 0.1, d=0.6, y=30, echelle=0.9)
        self.entree('#cta-m', t + 0.4, d=0.6, y=30)
        self.entree('#cta-ss', t + 0.6, y=20)
        self.op(op='fromTo', sel='#cta-b', de={'autoAlpha': 0, 'scale': 0.7},
                a={'autoAlpha': 1, 'scale': 1, 'duration': 0.55, 'ease': 'back.out(2)', 'immediateRender': True},
                t=round(t + 0.9, 3))
        self.op(op='fromTo', sel='#cta-b', de={'scale': 1}, a={'scale': 1.05, 'duration': 0.5, 'yoyo': True,
                                                                'repeat': 3, 'ease': 'sine.inOut'}, t=round(t + 1.6, 3))
        self.entree('#cta-c', t + 1.2, y=16)
        self.entree('#cta-ch', t + 1.4, y=12)
        if suivant:
            self.entree('#cta-s', t + 1.7, y=12)
        self.poser_voix('cta', t)
        self.reperes.append(round(t + d - 0.3, 2))
        self.t_cta = t
        return t + d

    # ---------------------------------------------------- gestes posés --
    def _poser(self, g, t):
        k = g['geste']
        if k == 'zoom':
            cle = self.cible(g['sel'], g['fx'], g['fy'])
            self.op(op='camera', cle=cle, s=g['s'], d=g['d'], t=t)
            return g['d']
        if k == 'dezoom':
            self.op(op='to', sel='#cam', vars={'x': 0, 'y': 0, 'scale': 1, 'duration': g['d'], 'ease': 'power2.inOut'},
                    t=t)
            return g['d']
        if k == 'bulle':
            cle = self.cible(g['sel'])
            self.op(op='bulle', sel='#' + g['ident'], cle=cle, cote=g['cote'], d=g['d'], t=t)
            self.reperes.append(round(t + 0.8, 2))
            return 0.45
        if k == 'reaction':
            i = '#' + g['ident']
            self.op(op='fromTo', sel=i, de={'autoAlpha': 0, 'y': 30, 'scale': 0.9},
                    a={'autoAlpha': 1, 'y': 0, 'scale': 1, 'duration': 0.45, 'ease': 'back.out(1.6)'}, t=t)
            self.sortie(i, t + g['d'], d=0.3)
            self.reperes.append(round(t + 0.9, 2))
            return 0.45
        return super()._poser(g, t)

    def vignette(self):
        v = self.s.get('vignette', {'etape': 1})
        if isinstance(v, dict):
            t0, d = self.etapes_t[(1, v['etape'])]
            return round(t0 + v.get('apres', d / 2.0), 2)
        return float(v)

    # -------------------------------------------------------- assemblage --
    def construire(self):
        t = 0.0
        t = self.scene_accroche(t)
        t = self.scene_revelation(t)
        t = self.scene_tutoriel(t)
        t = self.scene_resultats(t)
        t = self.scene_cta(t)
        total = round(t, 2)
        fond = ('<div id="fond-mk" class="clip" data-start="0" data-duration="%.3f" data-track-index="0"></div>' % total)
        audios = ''.join(
            '<audio id="voix-%s" src="%s" data-start="%.3f" data-duration="%.3f" data-track-index="%d"></audio>'
            % (case, chemin, debut, max(0.1, duree - 0.06), 20 + i)
            for i, (case, chemin, debut, duree) in enumerate(self.audios))
        self.sons.extend(sorted((round(o['t'] + CLIC_SONORE, 3), 'clic') for o in self.ops if o['op'] == 'clic'))
        if self.bruitages:
            audios += ('<audio id="bruitages" src="%s" data-start="0" data-duration="%.3f" data-track-index="19"></audio>'
                       % (self.bruitages, total))
        plan = {'duree': total, 'cibles': self.cibles, 'defilements': sorted(self.defilements, key=lambda d: d['t']),
                'ops': self.ops}
        plan_json = json.dumps(plan, ensure_ascii=False).replace('</', '<\\/')
        html = moteur.TEMPLATE % {
            'titre': escape('%s — %s' % (MARQUE, self.s['titre'])),
            'id': self.id, 'duree': total,
            'couches': fond + ''.join(self.couches) + audios,
            'plan': plan_json,
            'css': '<link rel="stylesheet" href="assets/aite-marketing.css">'
                   + ('<style>%s</style>' % self.s['css'] if self.s.get('css') else ''),
        }
        return html, total

    def phrases(self):
        """Les phrases de la voix off : [(début, durée)], pour la musique."""
        return [(debut, duree) for _, _, debut, duree in self.audios]
