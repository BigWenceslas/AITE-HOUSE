// Prêt à poster : convertit dans le navigateur les vidéos du Pixel 8 Pro
// (HEVC 10 bits, HDR HLG, 4K) en MP4 H.264 SDR pour WhatsApp, TikTok et
// Facebook. Tout se passe sur le téléphone : WebCodecs utilise le décodeur
// et l'encodeur matériels, Mediabunny lit et écrit les fichiers MP4.
//
// Le même code tourne dans l'appli web installable (index.html) et dans
// l'artefact claude.ai ; seules les façons d'enregistrer et de partager
// le fichier diffèrent.

const PROFILS = {
  whatsapp: { libelle: 'WhatsApp', suffixe: 'whatsapp', debit: 4e6, cadre: 'origine' },
  statut: { libelle: 'Statut WhatsApp', suffixe: 'statut', debit: 4e6, cadre: 'origine', decoupe: 59 },
  tiktok: { libelle: 'TikTok et Reels', suffixe: 'tiktok', debit: 12e6, cadre: 'vertical' },
  facebook: { libelle: 'Facebook', suffixe: 'facebook', debit: 8e6, cadre: 'origine' },
};

const $ = (sel) => document.querySelector(sel);

let MB = null;
let fichier = null;
let infos = null;
let conversion = null;
let annulee = false;
let telechargements = null;

export async function demarrer(mediabunny) {
  MB = mediabunny;

  $('#choisir').addEventListener('change', (e) => {
    const f = e.target.files?.[0];
    if (f) charger(f);
    e.target.value = '';
  });
  $('#convertir').addEventListener('click', lancer);
  surveillerSelecteur();
  $('#annuler').addEventListener('click', () => {
    annulee = true;
    conversion?.cancel();
  });
  document.querySelectorAll('[name="profil"]').forEach((c) => c.addEventListener('change', majBouton));

  if (!('VideoEncoder' in window)) {
    afficherErreur("Ce navigateur ne sait pas convertir de vidéo. Ouvrez cette page dans Chrome sur Android.");
    $('#convertir').disabled = true;
  }

  // Dans l'artefact claude.ai, l'enregistrement passe par la capacité « downloads ».
  if (window.claude?.use) {
    window.claude.use('downloads').then((d) => { telechargements = d; }).catch(() => {});
  }

  await recupererPartage();
  majBouton();
}

// Dans la visionneuse intégrée d'une appli (l'appli Claude Android, par
// exemple), toucher le champ fichier ne fait rien. Quand le sélecteur
// s'ouvre, la page perd le focus ; sans cela au bout de 1,5 s, on explique
// comment ouvrir la page dans Chrome.
function surveillerSelecteur() {
  const adresse = document.querySelector('main').dataset.adresse || location.href.split(/[?#]/)[0];
  $('#adresse').textContent = adresse;
  $('#copier-adresse').addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText(adresse);
      $('#copier-adresse').textContent = 'Copiée';
    } catch {
      getSelection().selectAllChildren($('#adresse'));
    }
  });
  $('.choisir').addEventListener('click', () => {
    let ouvert = false;
    const marquer = () => { ouvert = true; };
    window.addEventListener('blur', marquer, { once: true });
    document.addEventListener('visibilitychange', marquer, { once: true });
    setTimeout(() => {
      window.removeEventListener('blur', marquer);
      document.removeEventListener('visibilitychange', marquer);
      if (!ouvert && !fichier) $('#aide-selecteur').hidden = false;
    }, 1500);
  });
}

// Vidéo reçue par « Partager » depuis Google Photos (appli installée) :
// le service worker l'a déposée dans le cache avant d'ouvrir la page.
async function recupererPartage() {
  if (!new URLSearchParams(location.search).has('partage') || !('caches' in window)) return;
  try {
    const cache = await caches.open('partage');
    const rep = await cache.match('fichier-partage');
    if (!rep) return;
    const nom = decodeURIComponent(rep.headers.get('X-Nom') || 'video.mp4');
    const blob = await rep.blob();
    await cache.delete('fichier-partage');
    history.replaceState(null, '', location.pathname);
    await charger(new File([blob], nom, { type: blob.type || 'video/mp4' }));
  } catch (err) {
    afficherErreur("La vidéo partagée n'a pas pu être lue. Choisissez-la depuis la galerie.");
  }
}

async function charger(f) {
  fichier = f;
  $('#aide-selecteur').hidden = true;
  infos = null;
  effacerErreur();
  $('#source').hidden = false;
  $('#source-nom').textContent = f.name;
  $('#source-details').textContent = 'Analyse…';
  $('#source-badges').replaceChildren();
  majBouton();

  const input = new MB.Input({ source: new MB.BlobSource(f), formats: MB.ALL_FORMATS });
  try {
    const video = await input.getPrimaryVideoTrack();
    if (!video) throw new Error("Ce fichier ne contient pas d'image vidéo.");
    const audio = await input.getPrimaryAudioTrack();
    const [largeur, hauteur, duree, hdr, codec, decodable, stats] = await Promise.all([
      video.getDisplayWidth(), video.getDisplayHeight(), input.computeDuration(),
      video.hasHighDynamicRange(), video.getCodec(), video.canDecode(), video.computePacketStats(120),
    ]);
    infos = {
      largeur, hauteur, duree, hdr, codec, decodable,
      ips: Math.round(stats.averagePacketRate) || 30,
      audio: audio ? await audio.getCodec() : null,
    };
  } catch (err) {
    $('#source-details').textContent = '';
    afficherErreur(err.message || "Ce fichier n'est pas une vidéo lisible.");
    return;
  } finally {
    input.dispose();
  }

  $('#source-details').textContent =
    `${infos.largeur} × ${infos.hauteur} · ${infos.ips} i/s · ${duree(infos.duree)} · ${taille(f.size)}`;
  const badges = [];
  if (infos.codec) badges.push(infos.codec === 'hevc' ? 'HEVC' : infos.codec.toUpperCase());
  if (infos.hdr) badges.push('HDR');
  if (Math.max(infos.largeur, infos.hauteur) >= 3840) badges.push('4K');
  if (!infos.audio) badges.push('sans son');
  $('#source-badges').replaceChildren(...badges.map((b) => {
    const s = document.createElement('span');
    s.className = 'badge' + (b === 'HDR' ? ' badge-hdr' : '');
    s.textContent = b;
    return s;
  }));
  if (!infos.decodable) {
    afficherErreur(`Ce téléphone ne sait pas lire le format ${infos.codec ?? 'de cette vidéo'} dans le navigateur.`);
  }
  majBouton();
}

function profilsChoisis() {
  return [...document.querySelectorAll('[name="profil"]:checked')].map((c) => c.value);
}

function majBouton() {
  const n = profilsChoisis().length;
  const pret = !!infos?.decodable && n > 0 && !conversion && 'VideoEncoder' in window;
  $('#convertir').disabled = !pret;
  $('#convertir').textContent = n > 1 ? `Convertir en ${n} versions` : 'Convertir';
}

async function lancer() {
  const choix = profilsChoisis();
  if (!infos || !choix.length) return;
  effacerErreur();
  annulee = false;
  const ipsMax = Number(document.querySelector('[name="ips"]:checked').value);
  const recadrer = document.querySelector('[name="vertical"]:checked').value === 'recadrer';

  // Liste des fichiers à produire (un statut long donne plusieurs morceaux).
  const taches = [];
  for (const cle of choix) {
    const p = PROFILS[cle];
    if (p.decoupe && infos.duree > p.decoupe + 0.5) {
      const n = Math.ceil((infos.duree - 0.5) / p.decoupe);
      for (let i = 0; i < n; i++) {
        taches.push({ p, debut: i * p.decoupe, fin: Math.min(infos.duree, (i + 1) * p.decoupe), partie: i + 1, total: n });
      }
    } else {
      taches.push({ p });
    }
  }

  const verrou = await garderEcranAllume();
  $('#progression').hidden = false;
  $('#convertir').hidden = true;
  $('#annuler').hidden = false;

  try {
    for (const [i, t] of taches.entries()) {
      if (annulee) break;
      const etape = taches.length > 1 ? `${i + 1}/${taches.length} · ` : '';
      const libelle = t.partie ? `${t.p.libelle} ${t.partie}/${t.total}` : t.p.libelle;
      $('#progression-libelle').textContent = `${etape}${libelle}`;
      majProgression(0);
      const debut = performance.now();
      const res = await convertirUne(t, ipsMax, recadrer);
      if (!res) break;
      ajouterResultat(t, res, (performance.now() - debut) / 1000);
    }
  } catch (err) {
    if (!annulee) {
      console.error(err);
      afficherErreur(`La conversion a échoué : ${err.message || err}. Essayez le profil 30 i/s ou une vidéo plus courte.`);
    }
  } finally {
    conversion = null;
    verrou?.release().catch(() => {});
    $('#progression').hidden = true;
    $('#convertir').hidden = false;
    $('#annuler').hidden = true;
    majBouton();
  }
}

function dimensions(p) {
  if (p.cadre === 'vertical') return { w: 1080, h: 1920 };
  const k = Math.min(1, 1920 / Math.max(infos.largeur, infos.hauteur));
  const pair = (x) => Math.max(2, Math.round((x * k) / 2) * 2);
  return { w: pair(infos.largeur), h: pair(infos.hauteur) };
}

// Chaque image passe par une toile sRGB 8 bits : Chrome y convertit le HDR
// en SDR, et c'est là qu'on redimensionne et qu'on compose le format 9:16.
function dessinateur(p, w, h, recadrer) {
  const toile = new OffscreenCanvas(w, h);
  const ctx = toile.getContext('2d', { alpha: false, colorSpace: 'srgb' });
  ctx.imageSmoothingQuality = 'high';
  const vertical = p.cadre === 'vertical';
  const dejaVertical = Math.abs(infos.largeur / infos.hauteur - 9 / 16) < 0.02;

  if (!vertical || dejaVertical) {
    return (s) => { s.drawWithFit(ctx, { fit: 'fill' }); return toile; };
  }
  if (recadrer) {
    return (s) => { s.drawWithFit(ctx, { fit: 'cover' }); return toile; };
  }
  // Fond flouté : l'image réduite à 36 × 64 puis agrandie donne un flou
  // doux pour presque rien en calcul.
  const mini = new OffscreenCanvas(36, 64);
  const mctx = mini.getContext('2d', { alpha: false, colorSpace: 'srgb' });
  return (s) => {
    s.drawWithFit(mctx, { fit: 'cover' });
    ctx.drawImage(mini, 0, 0, w, h);
    ctx.fillStyle = 'rgba(0, 0, 0, 0.28)';
    ctx.fillRect(0, 0, w, h);
    s.drawWithFit(ctx, { fit: 'contain' });
    return toile;
  };
}

async function convertirUne(t, ipsMax, recadrer) {
  const { p } = t;
  const { w, h } = dimensions(p);
  const debit = Math.max(1.5e6, Math.round(p.debit * Math.min(1, (w * h) / (1080 * 1920))));
  const ips = Math.min(ipsMax, infos.ips);

  if (!(await MB.canEncodeVideo('avc', { width: w, height: h, bitrate: debit }))) {
    throw new Error("l'encodeur H.264 de ce navigateur n'est pas disponible");
  }

  const input = new MB.Input({ source: new MB.BlobSource(fichier), formats: MB.ALL_FORMATS });
  const output = new MB.Output({
    format: new MB.Mp4OutputFormat({ fastStart: 'in-memory' }),
    target: new MB.BufferTarget(),
  });

  try {
    conversion = await MB.Conversion.init({
      input,
      output,
      tracks: 'primary',
      trim: t.debut !== undefined ? { start: t.debut, end: t.fin } : undefined,
      video: {
        codec: 'avc',
        quality: new MB.Quality({ bitrate: debit }),
        frameRate: ips,
        keyFrameInterval: 2,
        forceTranscode: true,
        process: dessinateur(p, w, h, recadrer),
        processedWidth: w,
        processedHeight: h,
      },
      // Le son AAC du Pixel est recopié tel quel ; les autres sont réencodés.
      audio: { codec: 'aac' },
    });
    if (!conversion.isValid) {
      const raisons = conversion.discardedTracks.map((d) => d.reason).join(', ');
      throw new Error(`format non pris en charge (${raisons})`);
    }
    const sansSon = !!infos.audio && conversion.discardedTracks.some((d) => d.track.type === 'audio');
    conversion.onProgress = (v) => majProgression(v);
    await conversion.execute();
    return { blob: new Blob([output.target.buffer], { type: 'video/mp4' }), w, h, ips, sansSon };
  } catch (err) {
    if (annulee || err?.name === 'ConversionCanceledError') return null;
    throw err;
  } finally {
    input.dispose();
  }
}

function ajouterResultat(t, res, secondes) {
  const base = fichier.name.replace(/\.[^.]+$/, '');
  const nom = t.partie
    ? `${base}_${t.p.suffixe}_${String(t.partie).padStart(2, '0')}.mp4`
    : `${base}_${t.p.suffixe}.mp4`;
  const f = new File([res.blob], nom, { type: 'video/mp4' });
  const url = URL.createObjectURL(f);

  const carte = $('#modele-resultat').content.firstElementChild.cloneNode(true);
  carte.dataset.profil = t.p.suffixe;
  carte.querySelector('.r-titre').textContent = t.partie ? `${t.p.libelle} ${t.partie}/${t.total}` : t.p.libelle;
  carte.querySelector('.r-details').textContent =
    `${res.w} × ${res.h} · ${res.ips} i/s · ${taille(f.size)} · converti en ${Math.max(1, Math.round(secondes))} s`;
  const v = carte.querySelector('video');
  v.src = url;
  if (res.sansSon) carte.querySelector('.r-alerte').hidden = false;

  const partager = carte.querySelector('.r-partager');
  // Le cadre de claude.ai refuse Web Share : on ne garde qu'« Enregistrer ».
  if (!window.claude?.use && navigator.canShare?.({ files: [f] })) {
    partager.addEventListener('click', () => navigator.share({ files: [f] }).catch(() => {}));
  } else {
    partager.hidden = true;
  }
  carte.querySelector('.r-enregistrer').addEventListener('click', () => enregistrer(f, url, carte));

  $('#resultats').hidden = false;
  $('#liste-resultats').prepend(carte);
  carte.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

async function enregistrer(f, url, carte) {
  const etat = carte.querySelector('.r-etat');
  if (telechargements) {
    try {
      await telechargements.save({ filename: f.name, data: f });
      etat.textContent = 'Enregistrée dans Téléchargements.';
    } catch (err) {
      if (err?.code !== 'declined') etat.textContent = "L'enregistrement n'est pas possible ici.";
    }
    return;
  }
  const a = document.createElement('a');
  a.href = url;
  a.download = f.name;
  document.body.append(a);
  a.click();
  a.remove();
  etat.textContent = 'Enregistrée dans Téléchargements (visible dans Google Photos › Bibliothèque).';
}

async function garderEcranAllume() {
  try { return await navigator.wakeLock?.request('screen'); } catch { return null; }
}

function majProgression(v) {
  const pc = Math.round(Math.min(1, Math.max(0, v)) * 100);
  $('#barre').style.setProperty('--avance', `${pc}%`);
  $('#barre').setAttribute('aria-valuenow', String(pc));
  $('#progression-pc').textContent = `${pc} %`;
}

function afficherErreur(msg) {
  $('#erreur').textContent = msg;
  $('#erreur').hidden = false;
}

function effacerErreur() {
  $('#erreur').hidden = true;
}

function duree(s) {
  const m = Math.floor(s / 60);
  const r = Math.round(s % 60);
  return m ? `${m} min ${String(r).padStart(2, '0')} s` : `${r} s`;
}

function taille(o) {
  return o >= 1e9 ? `${(o / 1e9).toFixed(1)} Go` : o >= 1e6 ? `${(o / 1e6).toFixed(1)} Mo` : `${Math.max(1, Math.round(o / 1e3))} Ko`;
}
