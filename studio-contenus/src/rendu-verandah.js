/*
 * Modèles de La Vérandah (cave · lounge · restaurant, Douala), d'après ses
 * affiches : crème, rouge vin et vert, écriture manuscrite (Great Vibes),
 * capitales condensées (Oswald), capitales fines (Montserrat).
 * S'appuie sur les outils de mise en page de rendu.js.
 */
(function (global) {
  'use strict';

  const A = global.AITE;
  const { police, typo, ajuster, ecrire, rect, remplirRect, tailleLigne, photo, sombre, THEME_SOMBRE } = A.outils;

  const VD = {
    rouge: '#9E1B2E', rougeFonce: '#6E1020', vert: '#1F6B3A', vertFonce: '#0E3522', vertVif: '#2E9E57',
    or: '#D9AE55', creme: '#FBF5EA', noir: '#120A06', blanc: '#FFFFFF', whatsapp: '#25D366',
  };
  const SCRIPT = "'Great Vibes', cursive";
  const COND = "'Oswald', 'Arial Narrow', sans-serif";
  const MONT = "'Montserrat', 'Segoe UI', sans-serif";
  const COORD = {
    adresse: 'Makepe, en face de l’église Sainte Monique',
    adresseCourte: 'Makepe, face Sainte Monique',
    telephone: '656 80 10 98',
  };
  const SANTE = ['L’abus d’alcool est dangereux pour la santé.', 'À consommer avec modération.'];
  // En story, les 260 px du bas sont couverts par « Répondre » (WhatsApp) ou « Envoyer un message » (Instagram).
  const SURE_BAS = 260;

  // Écriture manuscrite : la majuscule « À » de Great Vibes colle au mot suivant, on l'espace.
  const manuscrit = t => String(t || '').replace(/(^|[\s*])À /g, '$1À\u00A0\u2009');

  const maj = t => String(t || '').toLocaleUpperCase('fr-FR');
  const coord = pub => ({
    adresse: pub.adresse || COORD.adresse,
    adresseCourte: pub.adresseCourte || pub.adresse || COORD.adresseCourte,
    telephone: pub.telephone || COORD.telephone,
  });

  // ───────────── fonds ─────────────

  // Générateur pseudo-aléatoire à graine fixe : le même visuel à chaque rendu.
  function alea(graine) {
    let s = graine >>> 0;
    return () => ((s = (s * 1664525 + 1013904223) >>> 0) / 4294967296);
  }

  // Lumières de bar floues (bokeh) sur un dégradé sombre.
  function bokeh(ctx, W, H, o) {
    const g = ctx.createLinearGradient(0, 0, W * 0.3, H);
    g.addColorStop(0, o.haut); g.addColorStop(1, o.bas);
    ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
    const r = alea(o.graine || 11);
    for (let i = 0; i < (o.n || 46); i++) {
      const x = r() * W, y = r() * H * (o.zone || 0.75), rad = (18 + r() * 95) * W / 1080, a = 0.05 + r() * 0.22;
      const [cr, cg, cb] = o.couleurs[i % o.couleurs.length];
      const gr = ctx.createRadialGradient(x, y, 0, x, y, rad);
      gr.addColorStop(0, `rgba(${cr},${cg},${cb},${a})`);
      gr.addColorStop(0.65, `rgba(${cr},${cg},${cb},${a * 0.7})`);
      gr.addColorStop(1, `rgba(${cr},${cg},${cb},0)`);
      ctx.fillStyle = gr; ctx.beginPath(); ctx.arc(x, y, rad, 0, Math.PI * 2); ctx.fill();
    }
    const v = ctx.createRadialGradient(W / 2, H / 2, Math.min(W, H) * 0.35, W / 2, H / 2, Math.max(W, H) * 0.8);
    v.addColorStop(0, 'rgba(0,0,0,0)'); v.addColorStop(1, 'rgba(0,0,0,.55)');
    ctx.fillStyle = v; ctx.fillRect(0, 0, W, H);
  }

  const BAR = { haut: '#2A170C', bas: '#0C0604', couleurs: [[255, 176, 80], [255, 205, 130], [240, 140, 60], [255, 230, 180]] };

  // Photo qui couvre une zone (recadrage centré, foyer vertical réglable).
  function couvrir(ctx, ph, x, y, l, h, fy) {
    const e = Math.max(l / ph.l, h / ph.h);
    const dl = ph.l * e, dh = ph.h * e;
    ctx.save();
    ctx.beginPath(); ctx.rect(x, y, l, h); ctx.clip();
    ctx.drawImage(ph.img, x + (l - dl) / 2, y + (h - dh) * (fy == null ? 0.5 : fy), dl, dh);
    ctx.restore();
  }

  function degrade(ctx, x, y, l, h, de, a) {
    const g = ctx.createLinearGradient(0, y, 0, y + h);
    g.addColorStop(0, de); g.addColorStop(1, a);
    ctx.fillStyle = g; ctx.fillRect(x, y, l, h);
  }

  // ───────────── éléments de marque ─────────────

  // Logo (sur fond blanc d'origine) : posé en « produit » sur un fond clair, ou dans un panneau blanc.
  function logoVd(ctx, cx, y, h, mode) {
    const img = A.logos.verandah;
    if (!img) return { l: 0, h: 0 };
    const l = h * img.naturalWidth / img.naturalHeight;
    const x = cx - l / 2;
    if (mode === 'panneau') {
      const p = h * 0.12;
      ctx.save();
      ctx.shadowColor = 'rgba(0,0,0,.35)'; ctx.shadowBlur = 24; ctx.shadowOffsetY = 6;
      remplirRect(ctx, x - p * 1.4, y - p, l + p * 2.8, h + p * 2, h * 0.16, VD.blanc);
      ctx.restore();
      ctx.drawImage(img, x, y, l, h);
    } else {
      ctx.save(); ctx.globalCompositeOperation = 'multiply'; ctx.drawImage(img, x, y, l, h); ctx.restore();
    }
    return { l, h };
  }

  function epingle(ctx, x, y, h, couleur) {
    const r = h * 0.34, cy = y + r;
    ctx.save();
    ctx.fillStyle = couleur;
    ctx.beginPath();
    ctx.arc(x, cy, r, Math.PI * 0.82, Math.PI * 2.18);
    ctx.lineTo(x, y + h);
    ctx.closePath(); ctx.fill();
    ctx.fillStyle = VD.blanc; ctx.beginPath(); ctx.arc(x, cy, r * 0.42, 0, Math.PI * 2); ctx.fill();
    ctx.restore();
  }

  function whatsapp(ctx, cx, cy, r) {
    ctx.save();
    ctx.fillStyle = VD.whatsapp; ctx.beginPath(); ctx.arc(cx, cy, r, 0, Math.PI * 2); ctx.fill();
    ctx.strokeStyle = VD.blanc; ctx.lineWidth = r * 0.12;
    ctx.beginPath(); ctx.arc(cx, cy, r * 0.58, Math.PI * 0.72, Math.PI * 2.62); ctx.stroke();
    ctx.fillStyle = VD.blanc;
    ctx.beginPath(); ctx.moveTo(cx - r * 0.42, cy + r * 0.34); ctx.lineTo(cx - r * 0.62, cy + r * 0.66); ctx.lineTo(cx - r * 0.2, cy + r * 0.54); ctx.closePath(); ctx.fill();
    // combiné
    ctx.translate(cx, cy); ctx.rotate(-0.75);
    ctx.lineCap = 'round'; ctx.lineWidth = r * 0.17;
    ctx.beginPath(); ctx.arc(0, 0, r * 0.26, Math.PI * 0.55, Math.PI * 1.45); ctx.stroke();
    ctx.restore();
  }

  // Ligne de texte simple, réduite si elle dépasse la largeur.
  function ligne(ctx, texte, x, y, o) {
    const t = tailleLigne(ctx, texte, o.poids, o.famille, o.taille, o.largeur, o.espacement || 0);
    ctx.font = police(o.poids, t, o.famille);
    ctx.fillStyle = o.couleur; ctx.textBaseline = 'middle';
    const l = ctx.measureText(texte).width + (o.espacement || 0) * t * Math.max(0, [...texte].length - 1);
    let cx = o.aligner === 'centre' ? x - l / 2 : o.aligner === 'droite' ? x - l : x;
    if (o.espacement) {
      for (const c of texte) { ctx.fillText(c, cx, y); cx += ctx.measureText(c).width + o.espacement * t; }
    } else ctx.fillText(texte, cx, y);
    ctx.textBaseline = 'alphabetic';
    return { l, t };
  }

  function sante(ctx, x, y, o) {
    const une = SANTE.join(' ');
    ctx.font = police(500, o.taille, MONT);
    const lignes = ctx.measureText(une).width <= o.largeur ? [une] : SANTE;
    lignes.forEach((t, i) => ligne(ctx, t, x, y + i * o.taille * 1.35, { poids: 500, famille: MONT, taille: o.taille, largeur: o.largeur, couleur: o.couleur, aligner: o.aligner }));
    return lignes.length * o.taille * 1.35;
  }

  // Ligne « appels et WhatsApp » : icône + numéro.
  function telephone(ctx, x, y, o) {
    const r = o.taille * 0.62;
    ctx.font = police(o.poids || 600, o.taille, o.famille || MONT);
    const texte = (o.prefixe || '') + o.numero;
    const l = ctx.measureText(texte).width + r * 2 + o.taille * 0.4;
    const x0 = o.aligner === 'centre' ? x - l / 2 : x;
    whatsapp(ctx, x0 + r, y, r);
    ligne(ctx, texte, x0 + r * 2 + o.taille * 0.4, y, { poids: o.poids || 600, famille: o.famille || MONT, taille: o.taille, largeur: o.largeur, couleur: o.couleur });
    return l;
  }

  function adresse(ctx, texte, x, y, o) {
    const h = o.taille * 1.5;
    epingle(ctx, x + h * 0.35, y - h * 0.55, h, o.couleurIcone || VD.rouge);
    return ligne(ctx, texte, x + h * 1.05, y, { poids: o.poids || 600, famille: o.famille || MONT, taille: o.taille, largeur: o.largeur - h * 1.05, couleur: o.couleur, espacement: o.espacement });
  }

  const avecAlcool = pub => pub.alcool !== false;

  // ───────────── 1. annonce (vœux, annonce) ─────────────

  function annonce(ctx, W, H, pub, fmt) {
    const ph = photo(pub.photo);
    const story = fmt === 'story';
    const c = coord(pub);
    ctx.fillStyle = VD.creme; ctx.fillRect(0, 0, W, H);
    const bandeD = W * 0.06;
    const cx = (W - bandeD) / 2;           // centre de la zone crème

    let yLogo;
    const lh = story ? 250 : ph ? 170 : 200;
    if (ph) {
      const hp = H * (story ? 0.40 : 0.44);
      couvrir(ctx, ph, 0, 0, W, hp, 0.4);
      degrade(ctx, 0, hp * 0.55, W, hp * 0.45 + 2, 'rgba(251,245,234,0)', VD.creme);
      yLogo = hp - lh * 0.55;
    } else yLogo = story ? 210 : 52;

    // vague rouge en bas, liseré or, bande à droite
    const bande = story ? 200 : 150;
    const vague = (dy) => {
      ctx.beginPath();
      ctx.moveTo(0, H - bande * 0.62 + dy);
      ctx.bezierCurveTo(W * 0.3, H - bande * 1.15 + dy, W * 0.62, H - bande * 0.35 + dy, W, H - bande * 0.95 + dy);
    };
    ctx.save();
    ctx.fillStyle = VD.rouge; vague(0); ctx.lineTo(W, H); ctx.lineTo(0, H); ctx.closePath(); ctx.fill();
    ctx.strokeStyle = VD.or; ctx.lineWidth = 4; vague(-12); ctx.stroke();
    const gb = ctx.createLinearGradient(W - bandeD, 0, W, 0);
    gb.addColorStop(0, 'rgba(158,27,46,0)'); gb.addColorStop(1, 'rgba(158,27,46,.9)');
    ctx.fillStyle = gb; ctx.fillRect(W - bandeD, 0, bandeD, H);
    ctx.restore();

    logoVd(ctx, cx, yLogo, lh, ph ? 'panneau' : 'produit');

    // mention santé : dans la vague (carré, portrait) ou au-dessus de la zone couverte (story)
    const ts = story ? 24 : 20;
    let basContenu;
    if (story) {
      const hs = avecAlcool(pub) ? sante(ctx, cx, H - SURE_BAS - ts * 2.2, { taille: ts, largeur: W - bandeD - 160, couleur: VD.vertFonce, aligner: 'centre' }) : 0;
      basContenu = H - SURE_BAS - ts * 2.2 - (hs ? 30 : -ts * 2);
    } else {
      if (avecAlcool(pub)) sante(ctx, cx, H - ts * 2.7, { taille: ts, largeur: W - bandeD - 120, couleur: 'rgba(255,255,255,.92)', aligner: 'centre' });
      basContenu = H - bande * 1.15 - 22;
    }

    // coordonnées
    const tc = story ? 30 : 25;
    const yTel = basContenu - tc * 0.9;
    const yAdr = yTel - tc * 2.5;
    ctx.font = police(600, tc * 0.92, MONT);
    const ta = maj(c.adresse);
    const la = Math.min(W - bandeD - 120, ctx.measureText(ta).width + tc * 2.8);
    remplirRect(ctx, cx - la / 2, yAdr - tc * 1.05, la, tc * 2.1, tc * 1.05, VD.rouge);
    epingle(ctx, cx - la / 2 + tc * 0.95, yAdr - tc * 0.8, tc * 1.55, VD.blanc);
    ligne(ctx, ta, cx + tc * 0.6, yAdr, { poids: 600, famille: MONT, taille: tc * 0.92, largeur: la - tc * 2.6, couleur: VD.blanc, aligner: 'centre' });
    telephone(ctx, cx, yTel, { numero: c.telephone, prefixe: 'Appels et WhatsApp : ', taille: tc * 1.1, couleur: VD.vertFonce, largeur: W - bandeD - 200, aligner: 'centre' });

    // textes centrés entre le logo et les coordonnées
    const haut = yLogo + lh + (story ? 60 : 24), bas = yAdr - tc * 1.05 - (story ? 70 : 28);
    const l = W - bandeD - 150, x = cx - l / 2;
    const bt = pub.titre ? ajuster(ctx, manuscrit(pub.titre), { l, h: (bas - haut) * 0.3 }, { poids: 400, famille: SCRIPT, min: 34, max: story ? 110 : 90, interligne: 1.12 }) : null;
    const bx = ajuster(ctx, maj(pub.texte), { l, h: (bas - haut) * 0.54 }, { poids: 700, famille: COND, min: 50, max: story ? 190 : 150, interligne: 1.1, soigne: true });
    const bp = pub.points && pub.points[0] ? ajuster(ctx, manuscrit(pub.points[0]), { l, h: (bas - haut) * 0.18 }, { poids: 400, famille: SCRIPT, min: 30, max: story ? 84 : 66, interligne: 1.1 }) : null;
    const ecart = story ? 26 : 12;
    const total = (bt ? bt.hauteur + ecart : 0) + bx.hauteur + (bp ? bp.hauteur + ecart : 0);
    let y = haut + Math.max(0, (bas - haut - total) / 2);
    if (bt) { ecrire(ctx, bt, x, y, { couleur: VD.rouge, couleurRelief: VD.vert, aligner: 'centre', largeur: l }); y += bt.hauteur + ecart; }
    ecrire(ctx, bx, x, y, { couleur: VD.vert, couleurRelief: VD.rouge, aligner: 'centre', largeur: l });
    y += bx.hauteur + ecart;
    if (bp) ecrire(ctx, bp, x, y, { couleur: VD.rouge, couleurRelief: VD.vert, aligner: 'centre', largeur: l });
  }

  // ───────────── 2. ambiance (invitation, après le travail, week-end) ─────────────

  function ambiance(ctx, W, H, pub, fmt) {
    const ph = photo(pub.photo);
    const story = fmt === 'story';
    const c = coord(pub);
    if (ph) couvrir(ctx, ph, 0, 0, W, H, 0.35); else bokeh(ctx, W, H, { ...BAR, graine: 23 });
    degrade(ctx, 0, 0, W, H * 0.42, 'rgba(10,5,3,.62)', 'rgba(10,5,3,0)');
    degrade(ctx, 0, H * 0.45, W, H * 0.55, 'rgba(10,5,3,0)', 'rgba(10,5,3,.9)');

    const barre = story ? 230 : 190;
    const yB = story ? H - SURE_BAS - barre : H - barre;
    const mx = story ? 70 : 56;
    const pl = W * 0.36;

    // barre basse (prolongée jusqu'en bas en story) et panneau blanc arrondi du logo
    ctx.fillStyle = 'rgba(8,4,2,.94)'; ctx.fillRect(0, yB, W, H - yB);
    ctx.fillStyle = VD.vertVif; ctx.fillRect(0, yB, W - pl, 4);
    ctx.save();
    ctx.shadowColor = 'rgba(0,0,0,.4)'; ctx.shadowBlur = 20;
    ctx.beginPath(); rect(ctx, W - pl, yB - 46, pl + 80, H - yB + 120, 90); ctx.fillStyle = VD.blanc; ctx.fill();
    ctx.restore();
    const lh = Math.min(story ? 190 : 160, barre * 0.86);
    logoVd(ctx, W - pl / 2 + 10, yB - 46 + (barre + 46 - lh) / 2, lh, 'produit');

    const lg = W - pl - mx - 30;
    const tc = story ? 32 : 27;
    adresse(ctx, maj(c.adresseCourte), mx, yB + barre * 0.2, { taille: tc, famille: COND, poids: 500, couleur: VD.blanc, largeur: lg, couleurIcone: VD.blanc });
    telephone(ctx, mx, yB + barre * 0.45, { numero: c.telephone, taille: tc * 1.1, famille: COND, poids: 500, couleur: VD.blanc, largeur: lg });
    if (avecAlcool(pub)) sante(ctx, mx, yB + barre * 0.69, { taille: story ? 23 : 20, largeur: lg, couleur: 'rgba(255,255,255,.88)' });

    // accroche manuscrite en haut à gauche, phrase en capitales au-dessus du panneau
    const yt = story ? 230 : 58;
    ctx.save();
    ctx.shadowColor = 'rgba(0,0,0,.55)'; ctx.shadowBlur = 18; ctx.shadowOffsetY = 3;
    const bt = ajuster(ctx, manuscrit(pub.titre), { l: W * (story ? 0.86 : 0.74), h: H * (story ? 0.2 : 0.25) }, { poids: 400, famille: SCRIPT, min: 44, max: story ? 132 : 118, interligne: 1.05 });
    ecrire(ctx, bt, mx, yt, { couleur: VD.blanc, couleurRelief: VD.or, largeur: W });
    const lb = W - mx * 2;
    const bx = ajuster(ctx, maj(pub.texte), { l: lb, h: story ? 340 : 200 }, { poids: 700, famille: COND, min: 34, max: story ? 84 : 64, interligne: 1.2, soigne: true });
    ecrire(ctx, bx, mx, yB - 46 - 44 - bx.hauteur, { couleur: VD.blanc, couleurRelief: VD.or, largeur: lb });
    ctx.restore();
  }

  // ───────────── 3. carte (la cave, une sélection) ─────────────

  function carte(ctx, W, H, pub, fmt) {
    const story = fmt === 'story';
    const c = coord(pub);
    const g = ctx.createLinearGradient(0, 0, W * 0.4, H);
    g.addColorStop(0, '#155033'); g.addColorStop(1, '#071F14');
    ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
    const r = alea(31);
    for (let i = 0; i < 26; i++) {
      const x = r() * W, y = r() * H, rad = (20 + r() * 80) * W / 1080, a = 0.03 + r() * 0.08;
      const gr = ctx.createRadialGradient(x, y, 0, x, y, rad);
      gr.addColorStop(0, `rgba(217,174,85,${a})`); gr.addColorStop(1, 'rgba(217,174,85,0)');
      ctx.fillStyle = gr; ctx.beginPath(); ctx.arc(x, y, rad, 0, Math.PI * 2); ctx.fill();
    }
    const m = story ? 44 : 30;
    ctx.strokeStyle = VD.or; ctx.lineWidth = 3;
    ctx.beginPath(); rect(ctx, m, m, W - 2 * m, H - 2 * m, 18); ctx.stroke();
    ctx.globalAlpha = 0.5; ctx.lineWidth = 1.5;
    ctx.beginPath(); rect(ctx, m + 12, m + 12, W - 2 * m - 24, H - 2 * m - 24, 12); ctx.stroke();
    ctx.globalAlpha = 1;

    const lh = story ? 190 : 132;
    const yl = story ? 230 : m + 52;
    logoVd(ctx, W / 2, yl, lh, 'panneau');

    // pied : coordonnées et mention (au-dessus de la zone couverte en story)
    const tc = story ? 30 : 24;
    const ts = story ? 23 : 19;
    const basPied = story ? H - SURE_BAS : H - m - 26;
    const hs = avecAlcool(pub) ? ts * 1.35 * 2 : 0;
    const yS = basPied - hs;
    const yTel = yS - tc * 1.6;
    const yAdr = yTel - tc * 1.9;
    ctx.font = police(600, tc, MONT);
    const ta = c.adresse;
    const la = ctx.measureText(ta).width + tc * 1.5;
    adresse(ctx, ta, W / 2 - Math.min(la, W - 200) / 2, yAdr, { taille: tc, couleur: VD.creme, largeur: W - 200, couleurIcone: VD.or });
    telephone(ctx, W / 2, yTel, { numero: c.telephone, prefixe: 'Appels et WhatsApp : ', taille: tc, couleur: VD.creme, largeur: W - 200, aligner: 'centre' });
    if (avecAlcool(pub)) sante(ctx, W / 2, yS + ts * 0.5, { taille: ts, largeur: W * 0.5, couleur: 'rgba(251,245,234,.88)', aligner: 'centre' });

    // en-tête : ligne manuscrite, titre, filet
    const l = W - 2 * m - 100, x = (W - l) / 2;
    let y = yl + lh + (story ? 96 : 58);
    if (pub.etiquette) {
      const be = ajuster(ctx, manuscrit(pub.etiquette), { l, h: story ? 110 : 84 }, { poids: 400, famille: SCRIPT, min: 36, max: story ? 96 : 72, interligne: 1.05 });
      ecrire(ctx, be, x, y, { couleur: VD.or, couleurRelief: VD.blanc, aligner: 'centre', largeur: l });
      y += be.hauteur + be.taille * 0.22;
    }
    const bt = ajuster(ctx, maj(pub.titre), { l, h: story ? 220 : 130 }, { poids: 700, famille: COND, min: 40, max: story ? 110 : 84, interligne: 1.12 });
    ecrire(ctx, bt, x, y, { couleur: VD.blanc, couleurRelief: VD.or, aligner: 'centre', largeur: l });
    y += bt.hauteur + (story ? 34 : 22);
    ctx.fillStyle = VD.or;
    ctx.fillRect(W / 2 - 90, y, 70, 2); ctx.fillRect(W / 2 + 20, y, 70, 2);
    ctx.save(); ctx.translate(W / 2, y + 1); ctx.rotate(Math.PI / 4); ctx.fillStyle = '#C42A3F'; ctx.fillRect(-7, -7, 14, 14); ctx.restore();
    y += story ? 60 : 36;

    // liste : produit et, s'il est donné après « | », son prix
    const pts = (pub.points || []).filter(s => String(s).trim()).slice(0, 8);
    const pied = (pub.texte ? (story ? 120 : 76) : 0);
    const dispo = yAdr - tc * 1.6 - (story ? 70 : 34) - pied - y;
    const n = Math.max(1, pts.length);
    const prix = pts.some(s => s.includes('|'));
    let t = story ? 56 : fmt === 'portrait' ? 46 : 40;
    const pas = () => t * (story ? 2.05 : 1.85);
    while (t > 20 && n * pas() > dispo) t -= 1;
    let yy = y + Math.max(0, (dispo - n * pas()) / 2) + pas() / 2;
    for (const s of pts) {
      const [nom, montant] = s.split('|').map(v => v.trim());
      if (prix) {
        const xl = W / 2 - l * 0.42, xr = W / 2 + l * 0.42;
        const ln = ligne(ctx, typo(nom), xl, yy, { poids: 600, famille: MONT, taille: t, largeur: l * 0.6, couleur: VD.creme });
        const lp = montant ? ligne(ctx, typo(montant), xr, yy, { poids: 500, famille: COND, taille: t * 1.05, largeur: l * 0.3, couleur: VD.or, aligner: 'droite' }) : { l: 0 };
        ctx.fillStyle = 'rgba(217,174,85,.65)';
        for (let xd = xl + ln.l + 14; xd < xr - lp.l - 14; xd += 12) { ctx.beginPath(); ctx.arc(xd, yy + t * 0.25, 1.8, 0, Math.PI * 2); ctx.fill(); }
      } else {
        ligne(ctx, typo(nom), W / 2, yy, { poids: 600, famille: MONT, taille: t, largeur: l, couleur: VD.creme, aligner: 'centre' });
      }
      yy += pas();
    }
    if (pub.texte) {
      const bf = ajuster(ctx, manuscrit(pub.texte), { l, h: pied }, { poids: 400, famille: SCRIPT, min: 30, max: story ? 76 : 58, interligne: 1.05 });
      ecrire(ctx, bf, x, y + dispo + (pied - bf.hauteur) / 2, { couleur: VD.or, couleurRelief: VD.blanc, aligner: 'centre', largeur: l });
    }
  }

  // ───────────── 4. photo pleine page (titre fin, programme) ─────────────

  function photoPleine(ctx, W, H, pub, fmt) {
    const ph = photo(pub.photo);
    const story = fmt === 'story';
    const c = coord(pub);
    if (ph) couvrir(ctx, ph, 0, 0, W, H, 0.45);
    else bokeh(ctx, W, H, { haut: '#3A1418', bas: '#0B0507', couleurs: [[255, 170, 90], [240, 110, 120], [255, 210, 150]], graine: 41, zone: 0.9 });
    degrade(ctx, 0, 0, W, H * 0.42, 'rgba(0,0,0,.6)', 'rgba(0,0,0,0)');
    degrade(ctx, 0, H * 0.5, W, H * 0.5, 'rgba(0,0,0,0)', 'rgba(0,0,0,.85)');

    const mx = W * 0.08;
    let y = story ? 250 : H * 0.07;
    ctx.save();
    ctx.shadowColor = 'rgba(0,0,0,.5)'; ctx.shadowBlur = 14; ctx.shadowOffsetY = 2;
    if (pub.etiquette) {
      ligne(ctx, maj(pub.etiquette), mx, y, { poids: 600, famille: MONT, taille: story ? 30 : 24, largeur: W - 2 * mx, couleur: VD.blanc, espacement: 0.14 });
      y += story ? 70 : 54;
    }
    const bt = ajuster(ctx, maj(pub.titre), { l: W - 2 * mx, h: H * (story ? 0.24 : 0.26) }, { poids: 300, poidsRelief: 700, famille: MONT, min: 36, max: story ? 98 : 84, interligne: 1.1, soigne: true });
    ecrire(ctx, bt, mx, y, { couleur: VD.blanc, couleurRelief: VD.blanc, largeur: W });
    ctx.restore();

    // pied : logo à droite, coordonnées et mention à gauche, sur la même marge basse
    const marge = story ? SURE_BAS : Math.round(W * 0.07);
    const lh = story ? 170 : 140;
    const lw = lh * (A.logos.verandah ? A.logos.verandah.naturalWidth / A.logos.verandah.naturalHeight : 1.4);
    const yLogo = H - marge - lh;
    logoVd(ctx, W - mx - lw / 2 - lh * 0.17, yLogo, lh, 'panneau');
    const lg = W - 2 * mx - lw - lh * 0.6;
    const tc = story ? 26 : 22, ts = story ? 21 : 18;
    const hs = avecAlcool(pub) ? ts * 1.35 * 2 : 0;
    const yS = H - marge - hs + ts * 0.5;
    const yTel = yS - (hs ? ts * 0.5 : 0) - tc * 1.1;
    const yAdr = yTel - tc * 1.75;
    adresse(ctx, c.adresseCourte, mx, yAdr, { taille: tc, couleur: VD.blanc, largeur: lg, couleurIcone: VD.blanc });
    telephone(ctx, mx, yTel, { numero: c.telephone, prefixe: 'Appels et WhatsApp : ', taille: tc, couleur: VD.blanc, largeur: lg });
    if (hs) sante(ctx, mx, yS, { taille: ts, largeur: lg, couleur: 'rgba(255,255,255,.88)' });

    // programme : la partie avant « : » en gras
    const pts = (pub.points || []).filter(v => String(v).trim()).slice(0, 6).map(v => typo(v));
    let t = story ? 40 : 32;
    const largeurMax = W - 2 * mx;
    const mesure = v => {
      const i = v.indexOf(':');
      ctx.font = police(700, t, MONT); const a = i > 0 ? ctx.measureText(v.slice(0, i + 1)).width : 0;
      ctx.font = police(400, t, MONT); return a + ctx.measureText(i > 0 ? v.slice(i + 1) : v).width;
    };
    while (t > 18 && pts.some(v => mesure(v) > largeurMax)) t -= 1;
    const pas = t * 1.5;
    let yy = Math.min(yAdr, yLogo) - (story ? 80 : 56) - (pts.length - 1) * pas;
    ctx.save();
    ctx.shadowColor = 'rgba(0,0,0,.5)'; ctx.shadowBlur = 12;
    for (const v of pts) {
      const i = v.indexOf(':');
      let x = mx;
      ctx.textBaseline = 'middle'; ctx.fillStyle = VD.blanc;
      if (i > 0) { ctx.font = police(700, t, MONT); ctx.fillText(v.slice(0, i + 1), x, yy); x += ctx.measureText(v.slice(0, i + 1)).width; }
      ctx.font = police(400, t, MONT); ctx.fillText(i > 0 ? v.slice(i + 1) : v, x, yy);
      ctx.textBaseline = 'alphabetic';
      yy += pas;
    }
    ctx.restore();
  }

  // ───────────── 5. pensée (fond sombre, photo ronde du promoteur) ─────────────

  // Le modèle « fond sombre » d'AITE, aux couleurs de La Vérandah.
  const THEME = Object.assign({}, THEME_SOMBRE, {
    fond: ['#2B1714', '#0E0706'],
    eclats: {
      hg: [VD.rougeFonce, VD.rouge, VD.or, VD.vert], hd: [VD.rougeFonce, VD.vert, VD.creme],
      bg: [VD.creme, VD.or, VD.rouge, VD.vert], bd: [VD.rougeFonce, VD.vert, VD.or],
    },
    logo: (ctx, cx, y, h) => logoVd(ctx, cx, y, h, 'panneau'),
    logoH: [128, 150],
    anneau: VD.or, medaillon: ['#B32A40', '#5A0F1C'],
    famille: MONT, poids: 300, poidsRelief: 700, texte: '#F6EFE6', relief: VD.blanc, souligne: VD.or,
    etiquette: VD.or, nom: VD.blanc, fonction: '#E6D6C4', storyBas: 450,
    signature: { nom: 'Cyrille Donald ABOLO', fonction: 'La Vérandah · Makepe' },
    // mention santé : en bas à gauche à côté du médaillon, au-dessus du nom sans photo, hors zone couverte en story
    apres: (ctx, W, H, pub, fmt, g) => {
      if (!avecAlcool(pub)) return;
      const t = g.story ? 23 : 19;
      if (g.story) sante(ctx, W / 2, H - SURE_BAS - t * 1.4, { taille: t, largeur: W - 200, couleur: 'rgba(246,239,230,.85)', aligner: 'centre' });
      else if (!g.ph) sante(ctx, W / 2, g.ny - g.tn - 64, { taille: t, largeur: W - 200, couleur: 'rgba(246,239,230,.85)', aligner: 'centre' });
      else sante(ctx, 64, H - 112, { taille: t, largeur: g.cx - g.r - 110, couleur: 'rgba(246,239,230,.85)' });
    },
  });
  const pensee = (ctx, W, H, pub, fmt) => sombre(ctx, W, H, pub, fmt, THEME);

  const M = 'verandah';
  A.enregistrer('vd-annonce', { nom: 'Annonce', marque: M, etiquette: '', champs: {
    titre: ['Ligne manuscrite', 40], texte: ['Grandes capitales (mots en relief en rouge)', 28], points: ['Petite ligne finale (facultative)'],
  } }, annonce);
  A.enregistrer('vd-ambiance', { nom: 'Ambiance', marque: M, etiquette: '', champs: {
    titre: ['Accroche manuscrite', 40], texte: ['Phrase en capitales', 90],
  } }, ambiance);
  A.enregistrer('vd-carte', { nom: 'La cave', court: 'La cave', marque: M, etiquette: 'Notre cave', champs: {
    etiquette: ['Ligne manuscrite'], titre: ['Titre en capitales', 28], points: ['Produits, un par ligne (prix facultatif après « | »)'], texte: ['Ligne finale (facultative)', 50],
  } }, carte);
  A.enregistrer('vd-sombre', { nom: 'Pensée (photo ronde)', court: 'Pensée', marque: M, etiquette: '', champs: {
    etiquette: ['Petit libellé (facultatif)'], texte: ['Pensée (mots clés entre astérisques)', 160], signature: true, photoDG: true,
  } }, pensee);
  A.enregistrer('vd-photo', { nom: 'Photo pleine page', court: 'Photo', marque: M, etiquette: 'Vendredi soir', champs: {
    etiquette: ['Petit libellé en capitales'], titre: ['Titre en capitales (mots en gras entre astérisques)', 50], points: ['Programme, une ligne par étape (ex. « 18h : Apéritif »)'],
  } }, photoPleine);
})(window);
