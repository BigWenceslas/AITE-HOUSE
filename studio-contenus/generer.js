#!/usr/bin/env node
/*
 * Studio de contenus AITE — construction et génération.
 *
 *   node generer.js                     construit studio.html puis génère tous les visuels (format carré)
 *   node generer.js studio              construit seulement studio.html
 *   node generer.js visuels             génère les visuels de contenus/publications.json
 *        --format carre|portrait|story|tous   (défaut : carre)
 *        --id S01-lundi[,S02-mercredi]        (défaut : toutes les publications)
 *        --echelle 2                          (défaut : 1, soit 1080 px de large)
 *        --png                                PNG au lieu de JPEG (fichiers 4 à 6 fois plus lourds)
 *        --dossier chemin                     ailleurs que dans sortie/ (sans CALENDRIER.md)
 *
 * studio.html est autonome : polices, logo, photos et publications y sont
 * intégrés. Il s'ouvre d'un double-clic, sans serveur ni connexion.
 */
'use strict';
const fs = require('fs');
const path = require('path');

const ICI = __dirname;
const p = (...a) => path.join(ICI, ...a);

const LATIN = 'U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD';
const LATIN_EXT = 'U+0100-02BA, U+02BD-02C5, U+02C7-02CC, U+02CE-02D7, U+02DD-02FF, U+1D00-1DBF, U+1E00-1E9F, U+1EF2-1EFF, U+2020, U+20A0-20AB, U+20AD-20C0, U+2113, U+2C60-2C7F, U+A720-A7FF';

function base64(fichier, type) {
  return 'data:' + type + ';base64,' + fs.readFileSync(fichier).toString('base64');
}

function ressources() {
  const polices = [];
  for (const f of fs.readdirSync(p('assets/polices')).filter(f => f.endsWith('.woff2')).sort()) {
    const m = f.match(/^(space-grotesk|ibm-plex-sans)-(latin|latin-ext)-(\d+)-(normal|italic)\.woff2$/);
    if (!m) continue;
    polices.push({
      famille: m[1] === 'space-grotesk' ? 'Space Grotesk' : 'IBM Plex Sans',
      poids: Number(m[3]), style: m[4], plage: m[2] === 'latin' ? LATIN : LATIN_EXT,
      src: base64(p('assets/polices', f), 'font/woff2'),
    });
  }
  // Toute image détourée déposée dans assets/photos/ est proposée dans le studio.
  // reperes.json donne son nom et, si besoin, ses repères de cadrage ; sans
  // repères, le moteur les calcule lui-même à partir de la transparence.
  const reperes = JSON.parse(fs.readFileSync(p('assets/photos/reperes.json'), 'utf8'));
  const photos = {};
  const fichiers = fs.readdirSync(p('assets/photos')).filter(f => /\.(webp|png)$/i.test(f));
  const ordre = Object.keys(reperes);
  fichiers.sort((a, b) => rang(ordre, a) - rang(ordre, b) || a.localeCompare(b));
  for (const f of fichiers) {
    const cle = f.replace(/\.(webp|png)$/i, '');
    const r = reperes[cle] || {};
    photos[cle] = {
      nom: r.nom || cle, src: base64(p('assets/photos', f), /png$/i.test(f) ? 'image/png' : 'image/webp'),
      reperes: r.teteHaut != null ? { teteHaut: r.teteHaut, menton: r.menton, visageX: r.visageX } : null,
    };
  }
  return { polices, logo: base64(p('assets/logo/aite-consulting.png'), 'image/png'), photos };
}

function rang(ordre, f) {
  const i = ordre.indexOf(f.replace(/\.(webp|png)$/i, ''));
  return i < 0 ? ordre.length : i;
}

function lirePublications() {
  return JSON.parse(fs.readFileSync(p('contenus/publications.json'), 'utf8'));
}

// Empêche un « </script> » contenu dans les données de fermer la balise.
const sur = s => s.replace(/<\/(script)/gi, '<\\/$1');

function construireStudio() {
  const gabarit = fs.readFileSync(p('src/studio.html'), 'utf8');
  const remplacements = {
    '/*RESSOURCES*/': 'window.AITE_RESSOURCES = ' + sur(JSON.stringify(ressources())) + ';',
    '/*PUBLICATIONS*/': 'window.AITE_PUBLICATIONS = ' + sur(JSON.stringify(lirePublications())) + ';',
    '/*RENDU*/': sur(fs.readFileSync(p('src/rendu.js'), 'utf8')),
    '/*EDITEUR*/': sur(fs.readFileSync(p('src/editeur.js'), 'utf8')),
  };
  // remplacement par découpe (et non String.replace) : les « $ » des données restent intacts
  let html = gabarit;
  for (const [cle, val] of Object.entries(remplacements)) {
    const i = html.indexOf(cle);
    if (i < 0) throw new Error('Repère ' + cle + ' absent de src/studio.html');
    html = html.slice(0, i) + val + html.slice(i + cle.length);
  }
  fs.writeFileSync(p('studio.html'), html);
  const ko = Math.round(Buffer.byteLength(html) / 1024);
  console.log('studio.html construit (' + ko + ' Ko)');
}

function options(argv) {
  const o = { format: 'carre', id: null, echelle: 1, png: false, dossier: p('sortie') };
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === '--format') o.format = argv[++i];
    else if (argv[i] === '--id') o.id = argv[++i].split(',');
    else if (argv[i] === '--echelle') o.echelle = Number(argv[++i]);
    else if (argv[i] === '--png') o.png = true;
    else if (argv[i] === '--dossier') o.dossier = path.resolve(argv[++i]);
  }
  return o;
}

async function genererVisuels(o) {
  let chromium;
  try { ({ chromium } = require('playwright')); } catch (e) {
    console.error('Playwright est requis : npm install (dans studio-contenus), puis npx playwright install chromium');
    process.exit(1);
  }
  const { publications } = lirePublications();
  const liste = o.id ? publications.filter(x => o.id.includes(x.id)) : publications;
  const photos = fs.readdirSync(p('assets/photos')).map(f => f.replace(/\.(webp|png)$/i, ''));
  for (const x of liste) {
    if (x.photo && !photos.includes(x.photo)) throw new Error(x.id + ' : photo « ' + x.photo + ' » absente de assets/photos/');
  }
  if (!liste.length) { console.error('Aucune publication ne correspond.'); process.exit(1); }
  const formats = o.format === 'tous' ? ['carre', 'portrait', 'story'] : [o.format];
  fs.mkdirSync(o.dossier, { recursive: true });

  const navigateur = await chromium.launch();
  const page = await navigateur.newPage();
  const erreurs = [];
  page.on('pageerror', e => erreurs.push(e.message));
  await page.goto('file://' + p('studio.html') + '?lot=1');
  await page.waitForFunction(() => window.AITE_PRET === true || window.AITE_ERREUR, null, { timeout: 60000 });
  const err = await page.evaluate(() => window.AITE_ERREUR || null);
  if (err || erreurs.length) throw new Error('Le studio ne se charge pas : ' + (err || erreurs.join(' | ')));

  for (const pub of liste) {
    for (const format of formats) {
      const type = o.png ? 'image/png' : 'image/jpeg';
      const url = await page.evaluate(([pub, format, echelle, type]) => window.AITE_STUDIO.exporter(pub, format, echelle, type), [pub, format, o.echelle, type]);
      const nom = nomFichier(pub, format, o.png ? 'png' : 'jpg');
      fs.writeFileSync(path.join(o.dossier, nom), Buffer.from(url.split(',')[1], 'base64'));
      console.log('  ' + nom);
    }
  }
  await navigateur.close();
  if (o.dossier === p('sortie')) ecrireCalendrier(publications, o.png ? 'png' : 'jpg');
  console.log(liste.length * formats.length + ' visuel(s) dans ' + path.relative(process.cwd(), o.dossier) + '/');
}

function nomFichier(pub, format, ext) {
  return pub.id + '-' + pub.modele + (format === 'carre' ? '' : '-' + format) + '.' + ext;
}

// Récapitulatif lisible : visuel, texte et légende prête à copier, semaine par
// semaine (ou par série : une publication peut porter « serie », ex. « Week-end »).
function ecrireCalendrier(publications, ext) {
  const lignes = ['# Calendrier de publication', '',
    'Généré par `node generer.js` à partir de `contenus/publications.json`. Ne pas modifier à la main.', '',
    'Rythme proposé : lundi, une affiche de motivation ; mercredi, un conseil pratique ; vendredi, une citation.',
    'Le week-end : détente et sourire le samedi, repos le dimanche.', ''];
  let groupe = null;
  for (const x of publications) {
    if (groupeDe(x) !== groupe) { groupe = groupeDe(x); lignes.push('## ' + groupe, ''); }
    const titre = x.modele === 'conseil' ? x.titre : x.texte;
    lignes.push('### ' + cap(x.moment || x.jour) + ' — ' + ({ conseil: 'Conseil', affiche: 'Affiche', citation: 'Citation', sombre: 'Fond sombre' }[x.modele] || 'Citation') + ' · ' + x.theme, '');
    lignes.push('![' + x.id + '](' + nomFichier(x, 'carre', ext) + ')', '');
    lignes.push('**Visuel :** ' + titre.replace(/\*/g, ''), '');
    if (x.modele === 'conseil') { x.points.forEach((pt, i) => lignes.push((i + 1) + '. ' + pt.replace(/\*/g, ''))); lignes.push(''); }
    lignes.push('**Légende à publier :**', '', '```text', x.legende, '', x.hashtags.join(' '), '```', '');
  }
  fs.writeFileSync(p('sortie', 'CALENDRIER.md'), lignes.join('\n'));
}

const cap = s => s.charAt(0).toUpperCase() + s.slice(1);
const groupeDe = x => x.serie || 'Semaine ' + x.semaine;

(async () => {
  const [cmd, ...reste] = process.argv.slice(2);
  const o = options(cmd && cmd.startsWith('--') ? [cmd, ...reste] : reste);
  if (!cmd || cmd.startsWith('--')) { construireStudio(); await genererVisuels(o); }
  else if (cmd === 'studio') construireStudio();
  else if (cmd === 'visuels') await genererVisuels(o);
  else { console.error('Commande inconnue : ' + cmd); process.exit(1); }
})().catch(e => { console.error(e.message || e); process.exit(1); });
