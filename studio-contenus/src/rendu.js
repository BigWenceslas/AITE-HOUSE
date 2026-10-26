/*
 * Moteur de rendu des visuels AITE Consulting.
 * Dessine une publication (citation, affiche, conseil) sur un <canvas>, aux
 * couleurs et polices de la charte AITE. Utilisé par l'éditeur (studio.html)
 * et par la génération en lot (generer.js).
 */
(function (global) {
  'use strict';

  const C = {
    violet: '#8E2A8E',
    violetFonce: '#6A1E6C',
    violetNuit: '#43124A',
    orange: '#F0921F',
    orangeTexte: '#F8A63E', // orange de la charte, à peine éclairci pour la lisibilité sur violet
    bleu: '#2E8CB2',
    encre: '#1C1620',
    gris: '#6E6675',
    grisClair: '#9A93A0',
    creme: '#FAF8FB',
    mauve: '#F6ECF6',
    mauveTexte: '#E9D3EA',
    blanc: '#FFFFFF',
    bordure: '#E7E3EC',
  };
  const TITRE = "'Space Grotesk', 'Segoe UI', sans-serif";
  const TEXTE = "'IBM Plex Sans', 'Segoe UI', sans-serif";

  const FORMATS = {
    carre: { l: 1080, h: 1080, nom: 'Carré 1:1' },
    portrait: { l: 1080, h: 1350, nom: 'Portrait 4:5' },
    story: { l: 1080, h: 1920, nom: 'Story 9:16' },
  };

  const MODELES = {
    citation: { nom: 'Citation', etiquette: '' },
    affiche: { nom: 'Affiche motivation', etiquette: 'Motivation du lundi' },
    conseil: { nom: 'Conseil pratique', etiquette: 'Conseil pratique' },
    sombre: { nom: 'Fond sombre', court: 'Sombre', etiquette: '' },
  };

  const SIGNATURE = { nom: 'Cyrille Donald ABOLO', fonction: 'Directeur Général, AITE Consulting' };
  const SITE = 'www.aite-consulting.com';

  const R = { logo: null, logos: {}, photos: {} };

  // ───────────────────────── chargement ─────────────────────────

  function image(src) {
    return new Promise((ok, ko) => {
      const i = new Image();
      i.onload = () => ok(i);
      i.onerror = () => ko(new Error('Image illisible'));
      i.src = src;
    });
  }

  async function charger(res) {
    const polices = (res.polices || []).map(p => {
      const ff = new FontFace(p.famille, 'url(' + p.src + ')', {
        weight: String(p.poids), style: p.style || 'normal', unicodeRange: p.plage || 'U+0-10FFFF',
      });
      document.fonts.add(ff);
      return ff.load();
    });
    R.logo = await image(res.logo);
    for (const [cle, src] of Object.entries(res.logos || {})) R.logos[cle] = await image(src);
    for (const [cle, ph] of Object.entries(res.photos || {})) {
      R.photos[cle] = await preparerPhoto(await image(ph.src), ph.reperes, ph.nom);
    }
    await Promise.all(polices);
  }

  // Repères d'une photo détourée : haut du crâne, base de la tête (cou),
  // axe du visage, et bords gauche/droit de la silhouette ligne par ligne.
  async function preparerPhoto(img, reperes, nom) {
    const l = img.naturalWidth, h = img.naturalHeight;
    const cv = document.createElement('canvas');
    cv.width = l; cv.height = h;
    const cx = cv.getContext('2d');
    cx.drawImage(img, 0, 0);
    const px = cx.getImageData(0, 0, l, h).data;
    const gauche = new Int32Array(h).fill(-1), droite = new Int32Array(h).fill(-1);
    for (let y = 0; y < h; y++) {
      const o = y * l * 4;
      for (let x = 0; x < l; x++) if (px[o + x * 4 + 3] > 128) { gauche[y] = x; break; }
      for (let x = l - 1; x >= 0; x--) if (px[o + x * 4 + 3] > 128) { droite[y] = x; break; }
    }
    const coins = [0, l - 1, (h - 1) * l, h * l - 1].map(i => px[i * 4 + 3]);
    const detouree = coins.filter(a => a < 50).length >= 2;
    let rep = reperes;
    if (!rep && detouree) rep = reperesAuto(gauche, droite, l, h);
    return { img, l, h, gauche, droite, detouree, nom: nom || 'Photo', ...(rep || {}) };
  }

  function reperesAuto(gauche, droite, l, h) {
    const larg = y => (gauche[y] < 0 ? 0 : droite[y] - gauche[y]);
    let haut = 0;
    while (haut < h && larg(haut) === 0) haut++;
    const bande = Math.floor(h * 0.25);
    let maxI = haut, maxL = 0;
    for (let y = haut; y < Math.min(h, haut + Math.floor(bande * 0.6)); y++) if (larg(y) > maxL) { maxL = larg(y); maxI = y; }
    let cou = maxI, minL = Infinity;
    for (let y = maxI; y < Math.min(h, maxI + Math.floor((maxI - haut) * 1.6) + 20); y++) if (larg(y) < minL) { minL = larg(y); cou = y; }
    let s = 0, n = 0;
    for (let y = haut + 5; y <= maxI; y++) if (gauche[y] >= 0) { s += (gauche[y] + droite[y]) / 2; n++; }
    return { teteHaut: haut, menton: cou, visageX: n ? Math.round(s / n) : l / 2 };
  }

  // ───────────────────────── typographie ─────────────────────────

  // Espaces fines insécables à la française, apostrophe typographique, points de suspension.
  function typo(s) {
    s = String(s || '').replace(/\.\.\./g, '…').replace(/([\p{L}\d])'(?=[\p{L}\d*])/gu, '$1’');
    s = s.replace(/(\d)[ \u00A0](?=\d{3}(?!\d))/g, '$1\u202F').replace(/(\d)[ \u00A0]?%/g, '$1\u202F%');
    s = s.replace(/[ \u00A0\u202F]*([;:!?»])/g, (m, p, i, t) => {
      const av = t[i - 1], ap = t[i + m.length];
      if (i === 0 || /[;:!?]/.test(av)) return p;
      if (p === ':' && /\d/.test(av || '') && /\d/.test(ap || '')) return p; // heure 10:30
      if (p === ':' && ap === '/') return p; // adresse web
      return '\u202F' + p;
    });
    // le point médian part avec le mot qui le suit (« · RESTAURANT ») : il ne finit jamais une ligne
    s = s.replace(/ · /g, ' ·\u00A0');
    // pas de « 4 » ni de « à » en fin de ligne, séparés de leur mot
    s = s.replace(/(^|[\s(])(\d+) (?=[\p{L}*])/gu, '$1$2\u00A0');
    // mots d'une ou deux lettres (à, le, de, un, Si…) gardés avec le mot qui suit
    s = s.replace(/(?<=^|[\s*«(])([\p{L}’]{1,2}) (?=[\p{L}\d*«])/gu, '$1\u00A0');
    return s.replace(/«[ \u00A0\u202F]*/g, '«\u202F');
  }

  // Découpe un texte « avec *mise en relief* » en mots composés de morceaux stylés.
  function mots(texte) {
    const out = [];
    let cur = { morceaux: [] }, relief = false;
    const pousser = () => { if (cur.morceaux.length) out.push(cur); cur = { morceaux: [] }; };
    const parties = typo(texte).split('*');
    parties.forEach((partie, i) => {
      relief = i % 2 === 1;
      if (relief) partie = partie.replace(/(?<=^|\s)(\S{1,3}) (?=\S)/g, '$1\u00A0');
      const bouts = partie.split(/( |\n)/);
      for (const b of bouts) {
        if (b === ' ') { pousser(); continue; }
        if (b === '\n') { pousser(); out.push({ saut: true }); continue; }
        if (!b) continue;
        (relief ? [b] : b.split(/(?<=[\p{L}’]{4}-)(?=\p{L}{5})/u)).forEach((seg, k) => {
          if (k) { pousser(); cur.colle = true; }
          cur.morceaux.push({ t: seg, relief });
        });
      }
    });
    pousser();
    return out;
  }

  function police(poids, taille, famille) { return poids + ' ' + taille + 'px ' + famille; }

  // Police des mots en relief quand elle diffère du texte (poids, famille),
  // fixée le temps d'un ajuster() ou d'un ecrire().
  let RELIEF = null;

  function policeRelief(ctx) {
    return police(RELIEF.poids, parseFloat(/([\d.]+)px/.exec(ctx.font)[1]), RELIEF.famille);
  }

  function largeurMorceau(ctx, p) {
    if (!p.relief || !RELIEF) return ctx.measureText(p.t).width;
    const f = ctx.font;
    ctx.font = policeRelief(ctx);
    const l = ctx.measureText(p.t).width;
    ctx.font = f;
    return l;
  }

  function mesurerMot(ctx, mot) {
    let l = 0;
    for (const m of mot.morceaux) l += largeurMorceau(ctx, m);
    return l;
  }

  function couper(ctx, ms, largeur) {
    const espace = ctx.measureText(' ').width;
    const lignes = [];
    let ligne = [], l = 0;
    for (const m of ms) {
      if (m.saut) { lignes.push(ligne); ligne = []; l = 0; continue; }
      const lm = mesurerMot(ctx, m), sep = m.colle ? 0 : espace;
      if (ligne.length && l + sep + lm > largeur) { lignes.push(ligne); ligne = [m]; l = lm; }
      else { l += (ligne.length ? sep : 0) + lm; ligne.push(m); }
    }
    if (ligne.length) lignes.push(ligne);
    return lignes;
  }

  // Taille la plus grande qui tient dans la boîte, puis lignes équilibrées.
  function ajuster(ctx, texte, boite, o) {
    RELIEF = o.poidsRelief ? { poids: o.poidsRelief, famille: o.familleRelief || o.famille } : null;
    const ms = mots(texte);
    // les mots soudés par une insécable comptent chacun pour un mot
    const nbMots = ms.filter(m => !m.saut).reduce((n, m) => n + m.morceaux.map(p => p.t).join('').split('\u00A0').length, 0);
    const maxLignes = o.motsParLigne ? Math.max(1, Math.ceil(nbMots / o.motsParLigne)) : Infinity;
    const essai = (taille, limite) => {
      ctx.font = police(o.poids, taille, o.famille);
      if (ms.some(m => !m.saut && mesurerMot(ctx, m) > boite.l)) return false;
      const lignes = couper(ctx, ms, boite.l);
      if (lignes.length > limite && taille > o.min) return false;
      return lignes.length * taille * o.interligne <= boite.h;
    };
    const chercher = limite => {
      let bas = o.min, haut = o.max, t = o.min;
      while (haut - bas > 0.5) {
        const mil = (bas + haut) / 2;
        if (essai(mil, limite)) { t = mil; bas = mil; } else haut = mil;
      }
      return t;
    };
    // Le minimum de mots par ligne est une préférence : on y renonce s'il
    // coûte plus d'un cinquième de la taille (mot long dans une colonne étroite).
    const libre = chercher(Infinity);
    const contraint = maxLignes < Infinity ? chercher(maxLignes) : libre;
    let taille = contraint >= libre * 0.8 ? contraint : libre;
    const disposer = t => {
      ctx.font = police(o.poids, t, o.famille);
      let lignes = couper(ctx, ms, boite.l);
      if (o.equilibrer !== false && lignes.length > 1) {
        let b = boite.l * (o.equilibreMin || 0.45), h = boite.l;
        while (h - b > 2) {
          const mil = (b + h) / 2;
          if (couper(ctx, ms, mil).length <= lignes.length && !ms.some(m => !m.saut && mesurerMot(ctx, m) > mil)) h = mil; else b = mil;
        }
        lignes = couper(ctx, ms, h);
      }
      return lignes;
    };
    // un mot seul en dernière ligne : on réduit un peu la taille pour le raccrocher
    const orphelin = li => li.length >= 3 && li[li.length - 1].length === 1;
    taille = Math.floor(taille);
    let lignes = disposer(taille);
    for (let t = taille - 1; orphelin(lignes) && t >= Math.max(o.min, taille * 0.9); t--) {
      const autre = disposer(t);
      if (!orphelin(autre) && autre.length * t * o.interligne <= boite.h) { taille = t; lignes = autre; }
    }
    // Coupures soignées : parmi plusieurs largeurs de ligne et des tailles un peu
    // réduites, on garde la disposition la moins pénalisée (début de phrase en
    // fin de ligne, fin de phrase rejetée, mise en relief coupée, mot seul…).
    if (o.soigne && ms.filter(m => !m.saut).length > 1) {
      const info = new Map();
      let fin = true, run = 0, avant = false;
      for (const m of ms) {
        if (m.saut) { fin = true; avant = false; continue; }
        const t = m.morceaux.map(p => p.t).join('');
        const rel = m.morceaux.some(p => p.relief);
        if (rel && !avant) run++;
        const fp = /[.!?…][»”")\u202F]*$/u.test(t);
        info.set(m, { debut: fin, fin: fp, run: rel ? run : null });
        fin = fp; avant = rel;
      }
      const penalite = li => {
        let p = 0;
        const n = li.length;
        li.forEach((l, i) => {
          const der = info.get(l[l.length - 1]), prem = info.get(l[0]);
          if (i < n - 1) {
            const suiv = info.get(li[i + 1][0]);
            if (l.length > 1 && der.debut && !der.fin) p += 70;
            if (der.run !== null && der.run === suiv.run) p += 60;
            if (l.length === 1) p += 20;
          }
          if (i > 0 && l.length > 1 && prem.fin && !prem.debut) p += 40;
          if (i > 0 && /^·/.test(l[0].morceaux[0].t)) p += 30;
        });
        if (n > 1 && li[n - 1].length === 1) p += 25;
        const esp = ctx.measureText(' ').width;
        const ws = li.map(l => l.reduce((s, m, i) => s + mesurerMot(ctx, m) + (i && !m.colle ? esp : 0), 0));
        const wmax = Math.max(...ws);
        ws.slice(0, -1).forEach(w => { p += 20 * (1 - w / wmax) ** 2; });
        return p;
      };
      let meilleur = null;
      const t0 = Math.floor(taille);
      for (let t = t0; t >= Math.max(o.min, t0 * 0.78); t -= Math.max(1, Math.round(t0 * 0.02))) {
        ctx.font = police(o.poids, t, o.famille);
        if (ms.some(m => !m.saut && mesurerMot(ctx, m) > boite.l)) continue;
        const nmin = couper(ctx, ms, boite.l).length;
        for (let k = 0; k <= 24; k++) {
          const l = boite.l * (0.5 + 0.5 * k / 24);
          if (ms.some(m => !m.saut && mesurerMot(ctx, m) > l)) continue;
          const li = couper(ctx, ms, l);
          if (li.length * t * o.interligne > boite.h) continue;
          const score = penalite(li) + 12 * (li.length - nmin) + 100 * (t0 - t) / t0;
          if (!meilleur || score < meilleur.score) meilleur = { score, t, lignes: li };
        }
      }
      if (meilleur) { taille = meilleur.t; lignes = meilleur.lignes; }
    }
    // Affiches : une ligne réduite à un petit mot (« pas », « juste ») hache la
    // lecture ; on accepte jusqu'à un cinquième de taille en moins pour l'éviter.
    if (o.eviterMotsSeuls) {
      const seuls = li => li.slice(0, -1).filter(l => l.length === 1 && l[0].morceaux.map(m => m.t).join('').length <= 6).length;
      let meilleur = { t: taille, lignes, n: seuls(lignes) };
      for (let t = taille - 1; meilleur.n > 0 && t >= taille * 0.8; t--) {
        const autre = disposer(t);
        if (autre.length * t * o.interligne > boite.h) continue;
        const n = seuls(autre);
        if (n < meilleur.n) meilleur = { t, lignes: autre, n };
      }
      taille = meilleur.t; lignes = meilleur.lignes;
    }
    ctx.font = police(o.poids, taille, o.famille);
    const espace = ctx.measureText(' ').width;
    const largeurs = lignes.map(li => li.reduce((s, m, i) => s + mesurerMot(ctx, m) + (i && !m.colle ? espace : 0), 0));
    RELIEF = null;
    return { taille, lignes, largeurs, hauteur: lignes.length * taille * o.interligne, interligne: o.interligne, o };
  }

  // Dessine un bloc ajusté. Relief : 'couleur' (texte orange) ou 'surligne' (bande orange sous le texte).
  function ecrire(ctx, bloc, x, y, o) {
    const { taille, lignes, largeurs, interligne } = bloc;
    ctx.font = police(bloc.o.poids, taille, bloc.o.famille);
    RELIEF = bloc.o.poidsRelief ? { poids: bloc.o.poidsRelief, famille: bloc.o.familleRelief || bloc.o.famille } : null;
    const normale = ctx.font, forte = RELIEF ? policeRelief(ctx) : normale;
    ctx.textBaseline = 'alphabetic';
    const espace = ctx.measureText(' ').width;
    const pas = taille * interligne;
    const asc = taille * (interligne - 1) / 2 + taille * 0.8;

    // position de chaque morceau, et bandes continues d'un mot en relief au
    // suivant (sans la ponctuation finale)
    const places = [], bandes = [];
    lignes.forEach((ligne, i) => {
      let cx = x;
      if (o.aligner === 'centre') cx = x + (o.largeur - largeurs[i]) / 2;
      const by = y + i * pas + asc;
      let debut = null, fin = null;
      const clore = () => { if (debut !== null) bandes.push({ by, debut, fin }); debut = null; };
      ligne.forEach((m, j) => {
        if (j && !m.colle) cx += espace;
        for (const p of m.morceaux) {
          const lp = largeurMorceau(ctx, p);
          places.push({ p, x: cx, by });
          if (p.relief) {
            if (debut === null) debut = cx;
            const sans = p.t.replace(/[.,;:!?…»\u202F\u00A0]+$/u, '');
            fin = cx + (sans === p.t ? lp : largeurMorceau(ctx, { t: sans, relief: true }));
          } else clore();
          cx += lp;
        }
      });
      clore();
    });

    if (o.relief === 'surligne') {
      ctx.fillStyle = o.couleurSurligne || '#F6CD9F';
      for (const b of bandes) ctx.fillRect(b.debut - 2, b.by - taille * 0.30, b.fin - b.debut + 4, taille * 0.36);
    }
    if (o.relief === 'souligne' && bandes.length) {
      // trait tracé à part, puis découpé autour des lettres qui descendent (g, j, p)
      const off = document.createElement('canvas');
      off.width = ctx.canvas.width; off.height = ctx.canvas.height;
      const oc = off.getContext('2d');
      oc.setTransform(ctx.getTransform());
      oc.fillStyle = o.couleurSurligne || C.orange;
      for (const b of bandes) { oc.beginPath(); rect(oc, b.debut, b.by + taille * 0.14, b.fin - b.debut, taille * 0.085, taille * 0.042); oc.fill(); }
      oc.globalCompositeOperation = 'destination-out';
      oc.font = forte; oc.textBaseline = 'alphabetic'; oc.lineWidth = taille * 0.16; oc.lineJoin = 'round';
      for (const q of places) if (q.p.relief) oc.strokeText(q.p.t, q.x, q.by);
      ctx.save();
      ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.shadowColor = 'transparent';
      ctx.drawImage(off, 0, 0);
      ctx.restore();
    }
    for (const q of places) {
      ctx.font = q.p.relief ? forte : normale;
      ctx.fillStyle = q.p.relief ? o.couleurRelief : o.couleur;
      ctx.fillText(q.p.t, q.x, q.by);
    }
    ctx.font = normale;
    RELIEF = null;
  }

  function espace(ctx, texte, x, y, espacement, aligner) {
    const lettres = [...texte];
    const larg = lettres.reduce((s, c) => s + ctx.measureText(c).width, 0) + espacement * (lettres.length - 1);
    let cx = aligner === 'droite' ? x - larg : aligner === 'centre' ? x - larg / 2 : x;
    for (const c of lettres) { ctx.fillText(c, cx, y); cx += ctx.measureText(c).width + espacement; }
    return larg;
  }

  function largeurEspacee(ctx, texte, espacement) {
    const lettres = [...texte];
    return lettres.reduce((s, c) => s + ctx.measureText(c).width, 0) + espacement * (lettres.length - 1);
  }

  // Réduit la taille d'une ligne de texte jusqu'à ce qu'elle tienne dans la largeur.
  function tailleLigne(ctx, texte, poids, famille, taille, largeur, espacement) {
    for (let t = taille; t > 10; t -= 0.5) {
      ctx.font = police(poids, t, famille);
      if (largeurEspacee(ctx, texte, (espacement || 0) * t) <= largeur) return t;
    }
    return 10;
  }

  // ───────────────────────── formes ─────────────────────────

  function rect(ctx, x, y, l, h, r) {
    r = Math.min(r, l / 2, h / 2);
    ctx.moveTo(x + r, y);
    ctx.arcTo(x + l, y, x + l, y + h, r);
    ctx.arcTo(x + l, y + h, x, y + h, r);
    ctx.arcTo(x, y + h, x, y, r);
    ctx.arcTo(x, y, x + l, y, r);
    ctx.closePath();
  }

  function remplirRect(ctx, x, y, l, h, r, style) {
    ctx.beginPath(); rect(ctx, x, y, l, h, r); ctx.fillStyle = style; ctx.fill();
  }

  // Trame de points qui s'estompe à partir d'un foyer.
  function trame(ctx, zone, foyer, portee, o) {
    const pas = o.pas || 24, rMax = o.rMax || 3.4;
    ctx.fillStyle = o.couleur;
    for (let y = zone.y + pas / 2; y < zone.y + zone.h; y += pas) {
      for (let x = zone.x + pas / 2; x < zone.x + zone.l; x += pas) {
        const d = Math.hypot(x - foyer[0], y - foyer[1]);
        const r = rMax * (1 - d / portee);
        if (r < 0.6) continue;
        ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI * 2); ctx.fill();
      }
    }
  }

  // Croissant, motif repris des arcs du logo AITE.
  function croissant(ctx, cx, cy, rayon, epaisseur, angle, couleur) {
    const d = epaisseur * 1.35;
    const r2 = rayon - epaisseur + d;
    const t = Math.ceil(rayon * 2 + 8);
    const off = document.createElement('canvas');
    off.width = t; off.height = t;
    const o = off.getContext('2d');
    const c = t / 2;
    o.fillStyle = couleur;
    o.beginPath(); o.arc(c, c, rayon, 0, Math.PI * 2); o.fill();
    // gomme opaque : avec une couleur translucide, destination-out n'effacerait qu'en partie
    o.globalCompositeOperation = 'destination-out';
    o.fillStyle = '#000';
    o.beginPath(); o.arc(c + d * Math.cos(angle), c + d * Math.sin(angle), r2, 0, Math.PI * 2); o.fill();
    ctx.drawImage(off, cx - c, cy - c);
  }

  // Guillemets dessinés (forme « 99 »), pleins, cerclés de blanc.
  function guillemets(ctx, x, y, taille, couleur, ouvrant) {
    const r = taille * 0.30;
    const forme = (cx, cy) => {
      ctx.save();
      ctx.translate(cx, cy);
      if (ouvrant) ctx.rotate(Math.PI);
      ctx.beginPath();
      ctx.arc(0, 0, r, 0, Math.PI * 2);
      ctx.moveTo(r * 0.98, r * 0.1);
      ctx.bezierCurveTo(r * 1.05, r * 1.25, r * 0.35, r * 2.15, -r * 0.85, r * 2.45);
      ctx.bezierCurveTo(-r * 0.2, r * 1.85, r * 0.05, r * 1.35, -r * 0.1, r * 0.98);
      ctx.closePath();
      ctx.restore();
    };
    ctx.save();
    ctx.lineJoin = 'round';
    ctx.shadowColor = 'rgba(28,22,32,.22)'; ctx.shadowBlur = taille * 0.18; ctx.shadowOffsetY = taille * 0.05;
    ctx.lineWidth = taille * 0.11; ctx.strokeStyle = C.blanc;
    for (const dx of [0, r * 2.55]) { ctx.beginPath(); forme(x + dx, y); ctx.stroke(); }
    ctx.shadowColor = 'transparent';
    ctx.fillStyle = couleur;
    for (const dx of [0, r * 2.55]) { ctx.beginPath(); forme(x + dx, y); ctx.fill(); }
    ctx.restore();
  }

  function globe(ctx, x, y, r, couleur) {
    ctx.save();
    ctx.strokeStyle = couleur; ctx.lineWidth = Math.max(1.5, r * 0.16);
    ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI * 2); ctx.stroke();
    ctx.beginPath(); ctx.ellipse(x, y, r * 0.45, r, 0, 0, Math.PI * 2); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(x - r, y); ctx.lineTo(x + r, y); ctx.stroke();
    ctx.restore();
  }

  // ───────────────────────── logo, photo, signature ─────────────────────────

  function logo(ctx, x, y, hauteur, pastille) {
    if (!R.logo) return 0;
    const l = hauteur * R.logo.naturalWidth / R.logo.naturalHeight;
    if (pastille) {
      const p = hauteur * 0.22;
      ctx.save();
      ctx.shadowColor = 'rgba(20,6,24,.25)'; ctx.shadowBlur = 18; ctx.shadowOffsetY = 4;
      remplirRect(ctx, x - p * 1.3, y - p, l + p * 2.6, hauteur + p * 2, hauteur * 0.24, C.blanc);
      ctx.restore();
    }
    ctx.drawImage(R.logo, x, y, l, hauteur);
    return l;
  }

  function photo(cle) {
    if (!cle) return null;
    if (typeof cle === 'object') return cle;
    return R.photos[cle] || null;
  }

  // Place la personne : haut du crâne en (visageX, teteHaut), tête de hauteur teteH,
  // agrandie si besoin pour que le buste descende jusqu'au bas du cadre.
  function placer(ph, regle, basCadre) {
    const tete = Math.max(1, ph.menton - ph.teteHaut);
    let e = regle.teteH / tete;
    e = Math.max(e, (basCadre - regle.teteHaut) / (ph.h - ph.teteHaut));
    return { e, x: regle.visageX - ph.visageX * e, y: regle.teteHaut - ph.teteHaut * e };
  }

  // Bord gauche de la silhouette (coordonnées du visuel) entre deux hauteurs.
  function bordGauche(ph, pl, y1, y2) {
    let min = Infinity;
    const a = Math.max(0, Math.floor((y1 - pl.y) / pl.e)), b = Math.min(ph.h - 1, Math.ceil((y2 - pl.y) / pl.e));
    for (let y = a; y <= b; y++) if (ph.gauche[y] >= 0) min = Math.min(min, ph.gauche[y]);
    return min === Infinity ? Infinity : pl.x + min * pl.e;
  }

  // Cadre la personne entière dans la bande [x1, x2] : jamais coupée sur les
  // côtés, seulement en bas (bord du visuel ou du cadre, à la hauteur bas).
  // La tête mesure au plus teteH ; si la silhouette est trop large, la personne
  // est réduite, et descend pour que le bas de la photo tombe sur le bas de la zone
  // (sans remonter au-dessus de hautMin).
  function cadrer(ph, z) {
    const tete = Math.max(1, ph.menton - ph.teteHaut);
    const emax = z.teteH / tete;
    const mesurer = e => {
      const haut = Math.max(z.hautMin, z.bas - e * (ph.h - ph.teteHaut));
      const y = haut - ph.teteHaut * e;
      const derniere = Math.min(ph.h - 1, Math.floor((z.bas - y) / e));
      let g = Infinity, d = -Infinity;
      for (let r = 0; r <= derniere; r++) if (ph.gauche[r] >= 0) { g = Math.min(g, ph.gauche[r]); d = Math.max(d, ph.droite[r]); }
      return { haut, y, g, d };
    };
    let e = emax;
    for (let i = 0; i < 6; i++) {
      const m = mesurer(e);
      const e2 = Math.min(emax, (z.x2 - z.x1) / Math.max(1, m.d - m.g));
      if (Math.abs(e2 - e) < 1e-4) break;
      e = e2;
    }
    const m = mesurer(e);
    return { e, y: m.y, x: (z.x1 + z.x2) / 2 - (m.g + m.d) / 2 * e, haut: m.haut, tete: tete * e };
  }

  function silhouette(ctx, ph, pl, bas, ombre) {
    ctx.save();
    ctx.beginPath(); ctx.rect(-50, -50, 99999, bas + 50); ctx.clip();
    if (ombre) { ctx.shadowColor = ombre; ctx.shadowBlur = 36; ctx.shadowOffsetY = 10; }
    ctx.drawImage(ph.img, pl.x, pl.y, ph.l * pl.e, ph.h * pl.e);
    ctx.restore();
  }

  // Dessine la personne dans un cadre arrondi ; la tête peut dépasser au-dessus du cadre.
  function personne(ctx, ph, cadre, pl, o) {
    o = o || {};
    ctx.save();
    ctx.beginPath();
    rect(ctx, cadre.x, cadre.y, cadre.l, cadre.h, cadre.r || 0);
    if (o.depasse !== false && ph.detouree) {
      const marge = o.marge || 0;
      ctx.rect(cadre.x - marge, 0, cadre.l + marge * 2, cadre.y + (cadre.r || 0));
    }
    ctx.clip();
    if (o.ombre) { ctx.shadowColor = o.ombre; ctx.shadowBlur = 40; ctx.shadowOffsetY = 12; }
    if (ph.detouree) {
      ctx.drawImage(ph.img, pl.x, pl.y, ph.l * pl.e, ph.h * pl.e);
    } else {
      // photo non détourée : remplissage du cadre, visage centré
      const e = Math.max(cadre.l / ph.l, cadre.h / ph.h);
      ctx.drawImage(ph.img, cadre.x + (cadre.l - ph.l * e) / 2, cadre.y + (cadre.h - ph.h * e) * 0.15, ph.l * e, ph.h * e);
    }
    ctx.restore();
  }

  function signature(ctx, sig, x, y, o) {
    const nom = (sig.nom || '').toUpperCase(), fonction = sig.fonction || '';
    const barre = o.barre || 7;
    ctx.fillStyle = C.orange;
    ctx.fillRect(x, y, barre, o.hauteur);
    const tx = x + barre + o.retrait;
    const tn = tailleLigne(ctx, nom, 700, TITRE, o.tailleNom, o.largeur - barre - o.retrait, 0.04);
    ctx.fillStyle = o.couleurNom; ctx.textBaseline = 'alphabetic';
    espace(ctx, nom, tx, y + tn * 0.95, tn * 0.04);
    const tf = tailleLigne(ctx, fonction, 500, TEXTE, o.tailleFonction, o.largeur - barre - o.retrait, 0);
    ctx.fillStyle = o.couleurFonction;
    ctx.fillText(fonction, tx, y + tn * 0.95 + tf * 1.45);
  }

  function pastille(ctx, texte, x, y, o) {
    ctx.font = police(700, o.taille, TITRE);
    const esp = o.taille * 0.14;
    const l = largeurEspacee(ctx, texte, esp);
    const h = o.taille * 2.1, p = o.taille * 0.95;
    remplirRect(ctx, x, y, l + p * 2, h, h / 2, o.fond);
    ctx.fillStyle = o.couleur; ctx.textBaseline = 'middle';
    espace(ctx, texte, x + p, y + h / 2 + o.taille * 0.04, esp);
    ctx.textBaseline = 'alphabetic';
    return { l: l + p * 2, h };
  }

  // ───────────────────────── modèle « citation » ─────────────────────────

  function citation(ctx, W, H, pub, fmt) {
    const ph = photo(pub.photo);
    const story = fmt === 'story';
    const k = H / 1080;
    const sig = pub.signature || SIGNATURE;

    ctx.fillStyle = C.creme; ctx.fillRect(0, 0, W, H);
    trame(ctx, { x: 0, y: 0, l: W, h: H }, [0, 0], 560, { couleur: 'rgba(142,42,142,.20)' });
    trame(ctx, { x: 0, y: 0, l: W, h: H }, [W, H], 620, { couleur: 'rgba(142,42,142,.20)' });

    // géométrie
    // Le filet d'encadrement passe derrière le panneau et la carte photo :
    // seuls dépassent son bord haut et l'amorce de ses côtés.
    let panneau, carte, regle, sigPos, sitePos, logoPos, cadreLigne;
    if (!story) {
      panneau = ph ? { x: 40, y: 170 + 40 * (k - 1), l: 600, h: H - 170 - 40 * (k - 1) - 210 } : { x: 40, y: 170, l: W - 80, h: H - 170 - 190 };
      carte = { x: 600, y: 250 + 60 * (k - 1), l: 440, h: H - 250 - 60 * (k - 1) - 180, r: 40 };
      regle = { teteH: 205 + 45 * (k - 1) };
      sigPos = { x: carte.x + 8, y: carte.y + carte.h + 34, largeur: W - carte.x - 48 };
      sitePos = { x: 64, y: H - 50 };
      logoPos = { x: W - 48, y: 26, h: 80 };
      const bas = Math.min(panneau.y + panneau.h, carte.y + carte.h) - 60;
      cadreLigne = ph ? { x: 250, y: 128, l: 740, h: bas - 128 } : { x: 250, y: 128, l: 740, h: panneau.h - 60 };
    } else {
      panneau = { x: 56, y: 280, l: W - 112, h: ph ? 790 : 1000 };
      // la carte descend jusqu'au bas du visuel : la personne y tient debout,
      // la signature à sa gauche
      carte = { x: 70, y: 1170, l: W - 140, h: H - 1170 + 60, r: 44 };
      regle = { teteH: 250 };
      sigPos = { x: 110, y: 1330, largeur: 400 };
      sitePos = ph ? { x: 110, y: 1475 } : { x: W / 2, y: 1785, centre: true };
      logoPos = { x: W - 64, y: 118, h: 92 };
      cadreLigne = { x: 150, y: 235, l: W - 300, h: ph ? 1065 : 800 };
    }

    ctx.save();
    ctx.strokeStyle = C.violet; ctx.lineWidth = 9;
    ctx.beginPath(); ctx.rect(cadreLigne.x, cadreLigne.y, cadreLigne.l, cadreLigne.h); ctx.stroke();
    ctx.restore();

    // carte photo
    if (ph) {
      ctx.save();
      ctx.shadowColor = 'rgba(28,22,32,.16)'; ctx.shadowBlur = 30; ctx.shadowOffsetY = 10;
      const g = ctx.createLinearGradient(0, carte.y, 0, carte.y + carte.h);
      g.addColorStop(0, '#F3EAF4'); g.addColorStop(1, '#DCC8E0');
      remplirRect(ctx, carte.x, carte.y, carte.l, carte.h, carte.r, g);
      ctx.restore();
      if (ph.detouree) {
        const z = story
          ? { x1: 530, x2: W - 80, bas: H, hautMin: panneau.y + panneau.h + 24, teteH: regle.teteH }
          : { x1: panneau.x + panneau.l + 14, x2: carte.x + carte.l - 14, bas: carte.y + carte.h, hautMin: 150, teteH: regle.teteH };
        silhouette(ctx, ph, cadrer(ph, z), z.bas);
      } else {
        personne(ctx, ph, carte, null, {});
      }
    }

    // panneau violet
    ctx.save();
    ctx.shadowColor = 'rgba(67,18,74,.30)'; ctx.shadowBlur = 40; ctx.shadowOffsetY = 14;
    const gp = ctx.createLinearGradient(panneau.x, panneau.y, panneau.x + panneau.l, panneau.y + panneau.h);
    gp.addColorStop(0, '#9A309A'); gp.addColorStop(1, '#7A2179');
    remplirRect(ctx, panneau.x, panneau.y, panneau.l, panneau.h, 52, gp);
    ctx.restore();
    ctx.save();
    ctx.beginPath(); rect(ctx, panneau.x, panneau.y, panneau.l, panneau.h, 52); ctx.clip();
    ctx.fillStyle = 'rgba(255,255,255,.07)';
    ctx.beginPath(); ctx.arc(panneau.x + panneau.l * 0.95, panneau.y + panneau.h * 1.02, panneau.l * 0.78, 0, Math.PI * 2); ctx.fill();
    trame(ctx, panneau, [panneau.x + panneau.l, panneau.y], panneau.l * 0.6, { couleur: 'rgba(255,255,255,.10)', pas: 22, rMax: 3 });
    ctx.restore();

    // guillemets
    const tg = story ? 150 : 128;
    guillemets(ctx, panneau.x + 34, panneau.y - 6, tg, C.orange, true);
    guillemets(ctx, panneau.x + panneau.l - tg * (ph && !story ? 1.05 : 0.98), panneau.y + panneau.h - tg * (ph && !story ? 0.45 : 0.40), tg, C.orange, false);

    // texte
    const marge = story ? 76 : 58;
    const boite = { x: panneau.x + marge, y: panneau.y + (story ? 120 : 96), l: panneau.l - marge * 2, h: panneau.h - (story ? 230 : 200) };
    if (pub.etiquette) {
      ctx.font = police(700, story ? 24 : 19, TITRE); ctx.fillStyle = C.mauveTexte;
      espace(ctx, typo(pub.etiquette).toUpperCase(), boite.x, boite.y - (story ? 30 : 22), (story ? 24 : 19) * 0.16);
    }
    const bloc = ajuster(ctx, pub.texte, boite, { poids: 600, famille: TITRE, min: 30, max: story ? 84 : 70 * Math.min(k, 1.15), interligne: 1.2, motsParLigne: 2.4 });
    ecrire(ctx, bloc, boite.x, boite.y + (boite.h - bloc.hauteur) / 2, { couleur: C.blanc, couleurRelief: C.orangeTexte, largeur: boite.l });

    // signature
    {
      const sp = ph ? sigPos : { x: story ? 130 : 64, y: panneau.y + panneau.h + (story ? 80 : 34), largeur: story ? W - 260 : 600 };
      signature(ctx, sig, sp.x, sp.y, {
        hauteur: story ? 82 : 66, retrait: 18, largeur: sp.largeur, tailleNom: story ? 34 : 27, tailleFonction: story ? 25 : 20,
        couleurNom: C.violet, couleurFonction: C.gris,
      });
    }
    // logo
    ctx.save();
    const lw = logoPos.h * R.logo.naturalWidth / R.logo.naturalHeight;
    logo(ctx, logoPos.x - lw, logoPos.y, logoPos.h, false);
    ctx.restore();
    // site
    ctx.font = police(500, story ? 28 : 21, TEXTE);
    ctx.fillStyle = C.gris; ctx.textBaseline = 'middle';
    const site = pub.site || SITE;
    const ls = ctx.measureText(site).width;
    const sx = sitePos.centre ? sitePos.x - (ls + 34) / 2 : sitePos.x;
    globe(ctx, sx + 11, sitePos.y, 11, C.violet);
    ctx.fillText(site, sx + 32, sitePos.y + 1);
    ctx.textBaseline = 'alphabetic';
  }

  // ───────────────────────── modèle « affiche » ─────────────────────────

  function affiche(ctx, W, H, pub, fmt) {
    const ph = photo(pub.photo);
    const story = fmt === 'story';
    const k = H / 1080;
    const sig = pub.signature || SIGNATURE;
    const mx = story ? 70 : 60;

    const g = ctx.createLinearGradient(0, 0, W * 0.7, H);
    g.addColorStop(0, '#9C319C'); g.addColorStop(0.55, '#7A2179'); g.addColorStop(1, '#4A134F');
    ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
    trame(ctx, { x: 0, y: 0, l: W, h: H }, [0, H], 640, { couleur: 'rgba(255,255,255,.08)' });
    trame(ctx, { x: 0, y: 0, l: W, h: H }, [W * 0.35, 0], 420, { couleur: 'rgba(255,255,255,.06)' });

    const boite = story ? { x: mx, y: 290, l: W - mx * 2, h: 560 }
      : ph ? { x: mx, y: 160 * k, l: 520, h: H - 160 * k - 250 } : { x: mx, y: 170, l: W - mx * 2, h: H - 170 - 260 };

    if (ph) {
      let regle = story ? { visageX: W * 0.62, teteHaut: 1060, teteH: 330 } : { visageX: 805, teteHaut: 205 + 140 * (k - 1), teteH: 225 };
      const pl = placer(ph, regle, H);
      const tete = pl.e * (ph.menton - ph.teteHaut);
      if (!story) {
        // La colonne de texte s'arrête avant la silhouette ; si elle devient
        // trop étroite, la personne glisse vers la droite, tête toujours entière.
        const ecart = 30, minimum = 450;
        let bg = bordGauche(ph, pl, boite.y, boite.y + boite.h);
        if (bg - ecart - boite.x < minimum) {
          const dx = Math.max(0, Math.min(W - tete * 0.55 - regle.visageX, boite.x + minimum + ecart - bg));
          pl.x += dx; regle = Object.assign({}, regle, { visageX: regle.visageX + dx }); bg += dx;
        }
        boite.l = Math.max(400, Math.min(boite.l, bg - ecart - boite.x));
      }
      const cx = regle.visageX + 10, cy = regle.teteHaut + tete * 0.75;
      const rr = story ? 430 : 340 * Math.min(k, 1.15);
      const halo = ctx.createRadialGradient(cx, cy, 10, cx, cy, rr * 1.25);
      halo.addColorStop(0, 'rgba(255,255,255,.20)'); halo.addColorStop(1, 'rgba(255,255,255,0)');
      ctx.fillStyle = halo; ctx.fillRect(0, 0, W, H);
      // la pointe basse des croissants dépasserait en traits fins à droite de la silhouette
      ctx.save();
      ctx.beginPath(); ctx.rect(0, 0, cx + rr * 0.3, H); ctx.clip();
      croissant(ctx, cx, cy, rr, rr * 0.11, -0.75, 'rgba(255,255,255,.12)');
      croissant(ctx, cx, cy, rr * 0.86, rr * 0.075, -0.75, C.bleu);
      croissant(ctx, cx, cy, rr * 0.72, rr * 0.06, -0.75, C.orange);
      ctx.restore();
      personne(ctx, ph, { x: 0, y: 0, l: W, h: H, r: 0 }, pl, { depasse: false, ombre: 'rgba(30,6,34,.35)' });
      const hf = story ? 300 : 260;
      const f = ctx.createLinearGradient(0, H - hf, 0, H);
      f.addColorStop(0, 'rgba(67,18,74,0)'); f.addColorStop(1, 'rgba(52,12,58,.55)');
      ctx.fillStyle = f; ctx.fillRect(0, H - hf, W, hf);
    }

    // étiquette et logo (dans sa pastille blanche, comme le veut la charte sur fond violet)
    const etiquette = typo(pub.etiquette ? pub.etiquette : MODELES.affiche.etiquette).toUpperCase();
    const ey = story ? 170 : 62;
    const pst = etiquette ? pastille(ctx, etiquette, mx, ey, { taille: story ? 24 : 19, fond: C.orange, couleur: C.blanc }) : { h: 40 };
    const lh = story ? 74 : 60;
    const lw = lh * R.logo.naturalWidth / R.logo.naturalHeight;
    logo(ctx, W - mx - lw - lh * 0.29, ey + pst.h / 2 - lh / 2, lh, true);

    // texte : une phrase seule en grand, ou une accroche (titre) en grand suivie
    // du texte en paragraphe, pour les messages plus longs
    const accroche = (pub.titre || '').trim();
    let ty, hauteur;
    ctx.save();
    ctx.shadowColor = 'rgba(30,6,34,.35)'; ctx.shadowBlur = 16; ctx.shadowOffsetY = 3;
    if (accroche) {
      const bt = ajuster(ctx, accroche, { l: boite.l, h: boite.h * 0.58 }, { poids: 700, famille: TITRE, min: 36, max: story ? 96 : ph ? 76 : 96, interligne: 1.08, eviterMotsSeuls: true });
      const ecart = story ? 34 : 26;
      const bp = ajuster(ctx, pub.texte || '', { l: boite.l, h: boite.h - bt.hauteur - ecart }, { poids: 500, famille: TEXTE, min: 20, max: story ? 40 : 34, interligne: 1.4 });
      hauteur = bt.hauteur + ecart + bp.hauteur;
      ty = story ? boite.y : boite.y + (boite.h - hauteur) / 2;
      ecrire(ctx, bt, boite.x, ty, { couleur: C.blanc, couleurRelief: C.orangeTexte, largeur: boite.l });
      ecrire(ctx, bp, boite.x, ty + bt.hauteur + ecart, { couleur: '#F3E6F4', couleurRelief: C.orangeTexte, largeur: boite.l });
    } else {
      const bloc = ajuster(ctx, pub.texte, boite, { poids: 700, famille: TITRE, min: 40, max: story ? 112 : ph ? 96 : 120, interligne: 1.08, motsParLigne: 1.8, eviterMotsSeuls: true });
      hauteur = bloc.hauteur;
      ty = story ? boite.y : boite.y + (boite.h - hauteur) / 2;
      ecrire(ctx, bloc, boite.x, ty, { couleur: C.blanc, couleurRelief: C.orangeTexte, largeur: boite.l });
    }
    ctx.restore();
    const barreY = ty + hauteur + (story ? 34 : 26);
    ctx.fillStyle = C.orange;
    ctx.fillRect(boite.x, barreY, story ? 110 : 90, story ? 10 : 8);

    // signature : sous le texte en story, en pied sinon
    const sy = story ? barreY + 60 : H - 130;
    signature(ctx, sig, mx, sy, {
      hauteur: story ? 84 : 68, retrait: 18, largeur: story ? 520 : boite.l, tailleNom: story ? 34 : 27, tailleFonction: story ? 25 : 20,
      couleurNom: C.blanc, couleurFonction: C.mauveTexte,
    });
  }

  // ───────────────────────── modèle « conseil » ─────────────────────────

  function conseil(ctx, W, H, pub, fmt) {
    const ph = photo(pub.photo);
    const story = fmt === 'story';
    const k = H / 1080;
    const sig = pub.signature || SIGNATURE;
    const mx = story ? 70 : 60;

    ctx.fillStyle = C.creme; ctx.fillRect(0, 0, W, H);
    trame(ctx, { x: 0, y: 0, l: W, h: H }, [W, 0], 520, { couleur: 'rgba(142,42,142,.18)' });
    trame(ctx, { x: 0, y: 0, l: W, h: H }, [0, H], 520, { couleur: 'rgba(142,42,142,.14)' });

    // Bloc violet et personne. En story, le bloc occupe toute la largeur du
    // bas et porte aussi la signature ; sinon il tient la colonne de droite.
    let bloc = null, pl = null, zp = null;
    if (ph || story) {
      if (ph && ph.detouree) {
        zp = story ? { x1: 600, x2: W - 30, bas: H, hautMin: 1150, teteH: 215 } : { x1: 672, x2: W - 14, bas: H, hautMin: 170, teteH: 172 + 40 * (k - 1) };
        pl = cadrer(ph, zp);
      }
      // le bloc commence sous le menton (la tête dépasse) et descend jusqu'au bas du visuel
      const haut = pl && !story ? Math.max(300, Math.min(560, pl.haut + pl.tete * 0.62)) : 430 + 120 * (k - 1);
      bloc = story ? { x: 50, y: 1290, l: W - 100, h: H - 1290 + 60, r: 44 }
        : pl ? { x: 700, y: haut, l: W - 700 - 40, h: H - haut + 60, r: 40 }
        : { x: 710, y: haut, l: W - 710 - 40, h: H - haut - 40, r: 40 };
      ctx.save();
      ctx.shadowColor = 'rgba(67,18,74,.28)'; ctx.shadowBlur = 34; ctx.shadowOffsetY = 12;
      const gb = ctx.createLinearGradient(bloc.x, bloc.y, bloc.x + bloc.l * 0.4, bloc.y + bloc.h);
      gb.addColorStop(0, '#9A309A'); gb.addColorStop(1, '#6A1E6C');
      remplirRect(ctx, bloc.x, bloc.y, bloc.l, bloc.h, bloc.r, gb);
      ctx.restore();
      ctx.save();
      ctx.beginPath(); rect(ctx, bloc.x, bloc.y, bloc.l, bloc.h, bloc.r); ctx.clip();
      const zone = story ? { x: bloc.x + bloc.l - 420, l: 420 } : { x: bloc.x, l: bloc.l };
      const cxr = zone.x + zone.l * 0.55, cyr = bloc.y + (story ? 150 : 80);
      croissant(ctx, cxr, cyr, zone.l * 0.62, zone.l * 0.07, -0.7, 'rgba(46,140,178,.85)');
      croissant(ctx, cxr, cyr, zone.l * 0.50, zone.l * 0.055, -0.7, 'rgba(240,146,31,.95)');
      trame(ctx, bloc, [bloc.x, bloc.y + bloc.h], bloc.l * 0.6, { couleur: 'rgba(255,255,255,.09)', pas: 22, rMax: 3 });
      ctx.restore();
      if (pl) silhouette(ctx, ph, pl, H, 'rgba(40,10,45,.30)');
      else if (ph) personne(ctx, ph, bloc, null, {});
    }

    // en-tête : étiquette, numéro, logo
    const hy = story ? 170 : 58;
    const etiquette = typo(pub.etiquette || MODELES.conseil.etiquette).toUpperCase();
    const pst = pastille(ctx, etiquette, mx, hy, { taille: story ? 23 : 18, fond: C.violet, couleur: C.blanc });
    if (pub.numero) {
      ctx.font = police(700, story ? 26 : 21, TITRE); ctx.fillStyle = C.orange; ctx.textBaseline = 'middle';
      espace(ctx, 'N° ' + String(pub.numero).padStart(2, '0'), mx + pst.l + 18, hy + pst.h / 2 + 1, 1.5);
      ctx.textBaseline = 'alphabetic';
    }
    const lh = story ? 84 : 72;
    const lw = lh * R.logo.naturalWidth / R.logo.naturalHeight;
    logo(ctx, W - mx - lw, hy + pst.h / 2 - lh / 2 - 4, lh, false);

    // titre
    const colonne = ph && !story ? 620 : W - mx * 2;
    const tBoite = { x: mx, y: hy + pst.h + (story ? 50 : 34), l: colonne, h: story ? 330 : 200 + 60 * (k - 1) };
    const bt = ajuster(ctx, pub.titre || '', tBoite, { poids: 700, famille: TITRE, min: 34, max: story ? 84 : 62 + 8 * (k - 1) * 4, interligne: 1.1 });
    ecrire(ctx, bt, tBoite.x, tBoite.y, { couleur: C.encre, couleurRelief: C.encre, relief: 'surligne', couleurSurligne: '#F6CD9F', largeur: tBoite.l });

    // points, tous à la même taille ; l'espace restant aère la liste
    const points = (pub.points || []).filter(p => String(p).trim()).slice(0, 5);
    const n = Math.max(1, points.length);
    const py = tBoite.y + bt.hauteur + (story ? 60 : 40);
    const basPoints = story ? bloc.y - 170 : H - 185;
    const badge = story ? 64 : 52;
    const ecartMin = story ? 30 : 20;
    const textX = mx + badge + (story ? 28 : 22);
    const largeurTexte = (ph && !story ? 655 : W - mx) - textX;
    const dispo = basPoints - py - ecartMin * (n - 1);
    let blocs = [];
    for (let taille = story ? 42 : 34 + 4 * (k - 1) * 4; taille >= 20; taille -= 0.5) {
      blocs = points.map(p => ajuster(ctx, p, { l: largeurTexte, h: 9999 }, { poids: 500, famille: TEXTE, min: taille, max: taille, interligne: 1.32, equilibreMin: 0.8 }));
      if (blocs.reduce((s, b) => s + Math.max(b.hauteur, badge), 0) <= dispo) break;
    }
    const hauteurs = blocs.map(b => Math.max(b.hauteur, badge));
    const reste = dispo - hauteurs.reduce((s, h) => s + h, 0);
    const ecart = n > 1 ? ecartMin + Math.min(Math.max(0, reste) / (n - 1), ecartMin * 1.6) : 0;
    const couleurs = [C.violet, C.bleu, C.orange];
    let y = py;
    blocs.forEach((b, i) => {
      remplirRect(ctx, mx, y, badge, badge, badge * 0.28, couleurs[i % 3]);
      ctx.font = police(700, badge * 0.42, TITRE); ctx.fillStyle = C.blanc; ctx.textBaseline = 'middle';
      // puces « lettres » pour un sondage ou un quiz : A, B, C, D
      const num = pub.puces === 'lettres' ? 'ABCDE'[i] : String(i + 1).padStart(2, '0');
      ctx.fillText(num, mx + (badge - ctx.measureText(num).width) / 2, y + badge / 2 + 1);
      ctx.textBaseline = 'alphabetic';
      const ty = y + (b.lignes.length === 1 ? (badge - b.hauteur) / 2 : -b.taille * 0.12);
      ecrire(ctx, b, textX, ty, { couleur: C.encre, couleurRelief: C.violet, largeur: largeurTexte });
      y += hauteurs[i] + ecart;
      if (i < blocs.length - 1) {
        ctx.fillStyle = C.bordure;
        ctx.fillRect(textX, y - ecart / 2 - 1, largeurTexte, 2);
      }
    });

    // pied : signature et site
    const site = pub.site || SITE;
    if (story) {
      const sx = bloc.x + 44, sy = 1560;
      signature(ctx, sig, sx, sy, { hauteur: 84, retrait: 18, largeur: ph ? 470 : bloc.l - 88, tailleNom: 31, tailleFonction: 23, couleurNom: C.blanc, couleurFonction: C.mauveTexte });
      ctx.font = police(500, 24, TEXTE); ctx.fillStyle = C.mauveTexte; ctx.textBaseline = 'middle';
      globe(ctx, sx + 12, sy + 132, 12, C.mauveTexte);
      ctx.fillText(site, sx + 36, sy + 133);
    } else {
      const sy = H - 150;
      signature(ctx, sig, mx, sy, { hauteur: 66, retrait: 18, largeur: ph ? 600 : W - mx * 2, tailleNom: 25, tailleFonction: 19, couleurNom: C.violet, couleurFonction: C.gris });
      ctx.font = police(500, 19, TEXTE); ctx.fillStyle = C.gris; ctx.textBaseline = 'middle';
      globe(ctx, mx + 10, sy + 100, 10, C.violet);
      ctx.fillText(site, mx + 30, sy + 101);
    }
    ctx.textBaseline = 'alphabetic';
  }

  // ───────────────────────── modèle « fond sombre » ─────────────────────────

  // Éclats de couleur dans un coin : un biseau découpé en bandes obliques.
  // (tx, ty) est le coin ; sx, sy = ±1 orientent le biseau vers l'intérieur.
  function eclat(ctx, tx, ty, sx, sy, L, D, couleurs) {
    ctx.save();
    ctx.translate(tx, ty); ctx.scale(sx, sy);
    ctx.beginPath();
    ctx.moveTo(0, 0); ctx.lineTo(L, 0); ctx.lineTo(L * 0.42, D); ctx.lineTo(0, D * 0.62); ctx.closePath();
    ctx.clip();
    const pente = L * 0.58, w = (L + pente) / couleurs.length;
    couleurs.forEach((c, i) => {
      const x0 = i * w;
      ctx.beginPath();
      ctx.moveTo(x0, 0); ctx.lineTo(x0 + w + 1, 0); ctx.lineTo(x0 + w + 1 - pente, D); ctx.lineTo(x0 - pente, D); ctx.closePath();
      ctx.fillStyle = c; ctx.fill();
    });
    ctx.restore();
  }

  // Photo dans un médaillon rond, cerclé d'orange : tête et épaules.
  function medaillon(ctx, ph, cx, cy, r) {
    ctx.save();
    ctx.shadowColor = 'rgba(0,0,0,.45)'; ctx.shadowBlur = 30; ctx.shadowOffsetY = 8;
    ctx.beginPath(); ctx.arc(cx, cy, r + 7, 0, Math.PI * 2); ctx.fillStyle = C.orange; ctx.fill();
    ctx.restore();
    ctx.save();
    ctx.beginPath(); ctx.arc(cx, cy, r, 0, Math.PI * 2); ctx.clip();
    const g = ctx.createRadialGradient(cx, cy - r * 0.3, r * 0.1, cx, cy, r * 1.1);
    g.addColorStop(0, '#A8399F'); g.addColorStop(1, '#5A1A5E');
    ctx.fillStyle = g; ctx.fillRect(cx - r, cy - r, r * 2, r * 2);
    if (ph.detouree) {
      const e = (r * 2 * 0.60) / Math.max(1, ph.menton - ph.teteHaut);
      ctx.drawImage(ph.img, cx - ph.visageX * e, cy - r * 0.84 - ph.teteHaut * e, ph.l * e, ph.h * e);
    } else {
      const c = Math.min(ph.l, ph.h) * 0.72;
      ctx.drawImage(ph.img, (ph.l - c) / 2, ph.h * 0.03, c, c, cx - r, cy - r, 2 * r, 2 * r);
    }
    ctx.restore();
  }

  function sombre(ctx, W, H, pub, fmt) {
    const ph = photo(pub.photo);
    const story = fmt === 'story';
    const s = W / 1080;
    const sig = pub.signature || SIGNATURE;

    const g = ctx.createRadialGradient(W / 2, H * 0.45, 40, W / 2, H * 0.45, Math.max(W, H) * 0.75);
    g.addColorStop(0, '#2C2532'); g.addColorStop(1, '#141017');
    ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);

    const ep = story ? 1.3 : 1;
    eclat(ctx, 0, 0, 1, 1, 360 * s, 64 * s * ep, [C.violetNuit, C.violet, C.orange, C.bleu]);
    eclat(ctx, W, 0, -1, 1, 280 * s, 64 * s * ep, [C.violetNuit, C.bleu, C.blanc]);
    eclat(ctx, 0, H, 1, -1, 300 * s, 56 * s * ep, [C.blanc, C.orange, C.violet, C.bleu]);
    // le coin bas droit reçoit un éclat quand le médaillon ne l'occupe pas
    if (story || !ph) eclat(ctx, W, H, -1, -1, 240 * s, 56 * s * ep, [C.violetNuit, C.bleu, C.orange]);

    // logo, dans sa pastille blanche
    const lh = story ? 88 : 72;
    const lw = lh * R.logo.naturalWidth / R.logo.naturalHeight;
    const ly = story ? 200 : 58;
    logo(ctx, (W - lw) / 2, ly, lh, true);

    // médaillon et nom
    const r = story ? 175 : fmt === 'portrait' ? 142 : 128;
    const tn = story ? 34 : 26, tf = story ? 25 : 21;
    let cx, cy;
    if (story || !ph) { cx = W / 2; cy = story ? H - 370 - r : H - 52 - tn - tf * 1.6 - 18 - r; }
    else { cx = W - 62 - r; cy = H - 52 - tn - tf * 1.6 - 18 - r; }
    if (ph) medaillon(ctx, ph, cx, cy, r);
    const nom = sig.nom || '', fonction = sig.fonction || '';
    ctx.font = police(600, tn, TEXTE);
    const ln = ctx.measureText(nom).width;
    ctx.font = police(400, tf, TEXTE);
    const lf = ctx.measureText(fonction).width;
    const centre = Math.min(cx, W - 64 - Math.max(ln, lf) / 2);
    const ny = ph ? cy + r + 18 + tn : (story ? H - 370 : H - 60 - tf * 1.6);
    ctx.textBaseline = 'alphabetic';
    ctx.font = police(600, tn, TEXTE); ctx.fillStyle = C.blanc;
    ctx.fillText(nom, centre - ln / 2, ny);
    ctx.font = police(400, tf, TEXTE); ctx.fillStyle = '#CFC6D6';
    ctx.fillText(fonction, centre - lf / 2, ny + tf * 1.6);

    // étiquette facultative et texte, centrés
    const haut = ly + lh + (story ? 110 : 70);
    const bas = !ph ? ny - tn - (story ? 160 : 90) : story ? cy - r - 90 : cy - r - (fmt === 'portrait' ? 80 : 50);
    const boite = { x: story ? 80 : 100, l: W - (story ? 160 : 200), y: haut, h: bas - haut };
    let dy = 0;
    if (pub.etiquette) {
      const te = story ? 24 : 19;
      ctx.font = police(700, te, TITRE); ctx.fillStyle = C.orange;
      dy = te * 2.4;
      boite.y += dy; boite.h -= dy;
    }
    // un texte de un à trois mots s'écrit nettement plus grand
    const court = typo(pub.texte).replace(/\*/g, '').split(/\s+/).filter(Boolean).length <= 3;
    const max = (story ? 110 : fmt === 'portrait' ? 94 : 90) * (court ? 1.7 : 1);
    const bloc = ajuster(ctx, pub.texte, boite, {
      poids: 300, poidsRelief: 600, famille: TEXTE, min: 34, max, interligne: 1.3, soigne: true,
    });
    const ty = boite.y + (boite.h - bloc.hauteur) / 2;
    if (pub.etiquette) {
      const te = story ? 24 : 19;
      ctx.font = police(700, te, TITRE); ctx.fillStyle = C.orange;
      espace(ctx, typo(pub.etiquette).toUpperCase(), W / 2, ty - dy + te, te * 0.16, 'centre');
    }
    ecrire(ctx, bloc, boite.x, ty, {
      couleur: '#F2EEF4', couleurRelief: C.blanc, relief: 'souligne', couleurSurligne: C.orange, aligner: 'centre', largeur: boite.l,
    });
  }

  // ───────────────────────── point d'entrée ─────────────────────────

  function dessiner(canvas, pub, o) {
    o = o || {};
    const fmt = FORMATS[o.format || pub.format] ? (o.format || pub.format) : 'carre';
    const { l: W, h: H } = FORMATS[fmt];
    const echelle = o.echelle || 1;
    canvas.width = W * echelle; canvas.height = H * echelle;
    const ctx = canvas.getContext('2d');
    ctx.setTransform(echelle, 0, 0, echelle, 0, 0);
    ctx.imageSmoothingQuality = 'high';
    const modele = { citation, affiche, conseil, sombre, ...AUTRES }[pub.modele] || citation;
    modele(ctx, W, H, pub, fmt);
    return canvas;
  }

  // Modèles d'autres marques (ex. La Vérandah), ajoutés par un fichier séparé
  // qui s'appuie sur les mêmes outils de mise en page.
  const AUTRES = {};
  function enregistrer(cle, definition, fonction) {
    MODELES[cle] = definition;
    AUTRES[cle] = fonction;
  }
  const outils = { police, typo, mots, ajuster, ecrire, rect, remplirRect, espace, largeurEspacee, tailleLigne, trame, photo, cadrer, silhouette };

  global.AITE = { C, FORMATS, MODELES, SIGNATURE, SITE, charger, preparerPhoto, dessiner, typo, photos: R.photos, logos: R.logos, enregistrer, outils };
})(window);
