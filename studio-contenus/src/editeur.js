/*
 * Éditeur du studio : formulaire, aperçu en direct et export PNG.
 * En mode lot (?lot=1, utilisé par generer.js) seul window.AITE_STUDIO.exporter est exposé.
 */
(function () {
  'use strict';

  const BIBLIO = window.AITE_PUBLICATIONS || { publications: [] };
  const SIG = Object.assign({}, window.AITE.SIGNATURE, BIBLIO.signature || {});
  const CLE_BROUILLON = 'studio-aite-brouillon';
  const LIMITES = { citation: 190, affiche: 75, titre: 58, accroche: 70, paragraphe: 200, legende: 750 };

  const $ = id => document.getElementById(id);

  function exporter(pub, format, echelle, type) {
    const cv = document.createElement('canvas');
    window.AITE.dessiner(cv, completer(pub), { format, echelle: echelle || 1 });
    return type === 'image/jpeg' ? cv.toDataURL(type, 0.93) : cv.toDataURL('image/png');
  }

  function completer(pub) {
    return Object.assign({}, pub, {
      signature: {
        nom: (pub.signature && pub.signature.nom) || SIG.nom,
        fonction: (pub.signature && pub.signature.fonction) || SIG.fonction,
      },
    });
  }

  function vierge(modele) {
    return {
      id: '', modele: modele || 'citation', etiquette: '', texte: '', titre: '', points: [], numero: null,
      photo: premierePhoto(), legende: '', hashtags: ['#AITEConsulting'], signature: { nom: SIG.nom, fonction: SIG.fonction }, site: window.AITE.SITE,
    };
  }

  const premierePhoto = () => Object.keys(window.AITE.photos)[0] || null;

  const etat = { pub: null, format: 'carre' };

  function lireBrouillon() {
    try { const s = localStorage.getItem(CLE_BROUILLON); return s ? JSON.parse(s) : null; } catch (e) { return null; }
  }
  function ecrireBrouillon() {
    try { localStorage.setItem(CLE_BROUILLON, JSON.stringify({ pub: etat.pub, format: etat.format })); } catch (e) { /* stockage indisponible */ }
  }

  let toastMinuteur = null;
  function toast(msg) {
    const t = $('toast');
    t.textContent = msg; t.classList.add('visible');
    clearTimeout(toastMinuteur);
    toastMinuteur = setTimeout(() => t.classList.remove('visible'), 2200);
  }

  async function copier(texte) {
    try { await navigator.clipboard.writeText(texte); return true; } catch (e) {
      const z = document.createElement('textarea');
      z.value = texte; z.style.position = 'fixed'; z.style.opacity = '0';
      document.body.appendChild(z); z.select();
      let ok = false;
      try { ok = document.execCommand('copy'); } catch (e2) { ok = false; }
      z.remove();
      return ok;
    }
  }

  function nomFichier(format) {
    const p = etat.pub;
    return (p.id ? p.id + '-' : 'aite-') + p.modele + (format === 'carre' ? '' : '-' + format) + '.png';
  }

  function telecharger(format) {
    const cv = document.createElement('canvas');
    window.AITE.dessiner(cv, completer(etat.pub), { format, echelle: 1 });
    return new Promise(ok => cv.toBlob(b => {
      const a = document.createElement('a');
      a.href = URL.createObjectURL(b);
      a.download = nomFichier(format);
      document.body.appendChild(a); a.click(); a.remove();
      setTimeout(() => URL.revokeObjectURL(a.href), 4000);
      ok();
    }, 'image/png'));
  }

  // ───────────── interface ─────────────

  function construire() {
    const app = $('app');
    app.innerHTML = '';
    app.appendChild($('gabarit').content.cloneNode(true));
    $('logo').src = window.AITE_RESSOURCES.logo;

    // bibliothèque
    const sel = $('biblio');
    const vide = document.createElement('option');
    vide.value = ''; vide.textContent = 'Choisir une publication…';
    sel.appendChild(vide);
    let groupe = null, libelle = null;
    BIBLIO.publications.forEach((p, i) => {
      const l = p.serie || 'Semaine ' + p.semaine;
      if (l !== libelle) {
        libelle = l;
        groupe = document.createElement('optgroup');
        groupe.label = l;
        sel.appendChild(groupe);
      }
      const o = document.createElement('option');
      o.value = String(i);
      const txt = (p.modele === 'conseil' ? p.titre : p.texte).replace(/\*/g, '');
      o.textContent = cap(p.jour) + ' · ' + txt.slice(0, 60) + (txt.length > 60 ? '…' : '');
      (groupe || sel).appendChild(o);
    });
    sel.addEventListener('change', () => {
      if (sel.value === '') return;
      etat.pub = JSON.parse(JSON.stringify(BIBLIO.publications[Number(sel.value)]));
      etat.pub.signature = etat.pub.signature || { nom: SIG.nom, fonction: SIG.fonction };
      etat.pub.site = etat.pub.site || window.AITE.SITE;
      remplir(); rendre();
    });
    $('nouveau').addEventListener('click', () => {
      etat.pub = vierge(etat.pub.modele);
      sel.value = '';
      remplir(); rendre();
      $(etat.pub.modele === 'conseil' ? 'titre' : 'texte').focus();
    });

    segments('modeles', v => { etat.pub.modele = v; remplir(); rendre(); });
    segments('formats', v => { etat.format = v; majSegments(); rendre(); });

    const lier = (id, f) => $(id).addEventListener('input', () => { f($(id).value); rendre(); compteurs(); });
    lier('etiquette', v => { etat.pub.etiquette = v; });
    lier('texte', v => { etat.pub.texte = v; });
    lier('titre', v => { etat.pub.titre = v; });
    lier('points', v => { etat.pub.points = v.split('\n').map(s => s.trim()).filter(Boolean); });
    lier('numero', v => { etat.pub.numero = v ? Number(v) : null; });
    lier('puces', v => { etat.pub.puces = v; });
    lier('nom', v => { etat.pub.signature.nom = v; });
    lier('fonction', v => { etat.pub.signature.fonction = v; });
    lier('site', v => { etat.pub.site = v; });
    lier('legende', v => { etat.pub.legende = v; });
    lier('hashtags', v => { etat.pub.hashtags = v.split(/\s+/).filter(Boolean); });

    photos();
    $('fichier').addEventListener('change', importer);

    $('telecharger').addEventListener('click', () => telecharger(etat.format).then(() => toast('Visuel téléchargé')));
    $('trois').addEventListener('click', async () => {
      for (const f of ['carre', 'portrait', 'story']) await telecharger(f);
      toast('Les 3 formats sont téléchargés');
    });
    $('grand').addEventListener('click', () => {
      $('modale-img').src = exporter(etat.pub, etat.format, 1);
      $('modale').classList.add('ouverte');
    });
    $('modale').addEventListener('click', e => { if (e.target.id !== 'modale-img') $('modale').classList.remove('ouverte'); });
    $('copier-legende').addEventListener('click', async () => {
      const t = (etat.pub.legende || '').trim() + (etat.pub.hashtags.length ? '\n\n' + etat.pub.hashtags.join(' ') : '');
      toast(await copier(t) ? 'Légende copiée' : 'Copie impossible : sélectionnez le texte à la main');
    });
    $('copier-json').addEventListener('click', async () => {
      toast(await copier(JSON.stringify(etat.pub, null, 2)) ? 'Fiche copiée (à coller dans contenus/publications.json)' : 'Copie impossible');
    });

    remplir();
    rendre();
  }

  function segments(id, f) {
    $(id).querySelectorAll('button').forEach(b => b.addEventListener('click', () => f(b.dataset.v)));
  }

  function majSegments() {
    $('modeles').querySelectorAll('button').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.v === etat.pub.modele)));
    $('formats').querySelectorAll('button').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.v === etat.format)));
    const f = window.AITE.FORMATS[etat.format];
    $('dimensions').textContent = f.nom + ' · ' + f.l + ' × ' + f.h + ' px';
  }

  function photos() {
    const zone = $('photos');
    zone.innerHTML = '';
    const ajouter = (cle, libelle, src) => {
      const b = document.createElement('button');
      b.type = 'button'; b.dataset.v = cle; b.title = libelle;
      if (src) { const i = document.createElement('img'); i.src = src; i.alt = libelle; b.appendChild(i); }
      else { const s = document.createElement('span'); s.textContent = libelle; b.appendChild(s); }
      b.addEventListener('click', () => { etat.pub.photo = cle || null; majPhotos(); rendre(); });
      zone.appendChild(b);
    };
    for (const [cle, ph] of Object.entries(window.AITE.photos)) ajouter(cle, ph.nom, ph.img.src);
    ajouter('', 'Sans photo', null);
    majPhotos();
  }

  function majPhotos() {
    $('photos').querySelectorAll('button').forEach(b => b.setAttribute('aria-pressed', String((b.dataset.v || null) === (etat.pub.photo || null))));
  }

  async function importer(e) {
    const f = e.target.files && e.target.files[0];
    if (!f) return;
    const url = await new Promise(ok => { const r = new FileReader(); r.onload = () => ok(r.result); r.readAsDataURL(f); });
    const img = await new Promise((ok, ko) => { const i = new Image(); i.onload = () => ok(i); i.onerror = ko; i.src = url; });
    const cle = 'import-' + (Object.keys(window.AITE.photos).length + 1);
    window.AITE.photos[cle] = await window.AITE.preparerPhoto(img, null, f.name);
    etat.pub.photo = cle;
    photos(); rendre();
    toast(window.AITE.photos[cle].detouree ? 'Photo importée' : 'Photo importée (non détourée : elle remplira le cadre)');
  }

  function remplir() {
    const p = etat.pub;
    $('etiquette').value = p.etiquette || '';
    $('etiquette').placeholder = p.modele === 'citation' ? 'Ex. La pensée du vendredi' : 'Ex. ' + window.AITE.MODELES[p.modele].etiquette;
    $('texte').value = p.texte || '';
    $('titre').value = p.titre || '';
    $('points').value = (p.points || []).join('\n');
    $('numero').value = p.numero || '';
    $('puces').value = p.puces || 'chiffres';
    $('nom').value = p.signature.nom || '';
    $('fonction').value = p.signature.fonction || '';
    $('site').value = p.site || '';
    $('legende').value = p.legende || '';
    $('hashtags').value = (p.hashtags || []).join(' ');
    $('zone-texte').style.display = p.modele === 'conseil' ? 'none' : '';
    $('zone-conseil').style.display = p.modele === 'conseil' ? '' : 'none';
    $('zone-titre').style.display = p.modele === 'citation' ? 'none' : '';
    $('libelle-titre').textContent = p.modele === 'affiche' ? 'Accroche (facultative)' : 'Titre';
    $('aide-titre').style.display = p.modele === 'affiche' ? '' : 'none';
    if (p.photo && !window.AITE.photos[p.photo]) p.photo = premierePhoto();
    majSegments(); majPhotos(); compteurs();
  }

  function compteurs() {
    const p = etat.pub;
    const n = s => (s || '').replace(/\*/g, '').length;
    const c = (id, val, max) => {
      const el = $(id);
      el.textContent = val + ' / ' + max;
      el.classList.toggle('trop', val > max);
    };
    const paragraphe = p.modele === 'affiche' && (p.titre || '').trim();
    c('c-texte', n(p.texte), paragraphe ? LIMITES.paragraphe : p.modele === 'affiche' ? LIMITES.affiche : LIMITES.citation);
    c('c-titre', n(p.titre), p.modele === 'affiche' ? LIMITES.accroche : LIMITES.titre);
    c('c-legende', (p.legende || '').length, LIMITES.legende);
  }

  let rendu = null;
  function rendre() {
    if (rendu) return;
    rendu = requestAnimationFrame(() => {
      rendu = null;
      window.AITE.dessiner($('toile'), completer(etat.pub), { format: etat.format, echelle: 1 });
      ecrireBrouillon();
    });
  }

  const cap = s => (s ? s.charAt(0).toUpperCase() + s.slice(1) : '');

  // ───────────── démarrage ─────────────

  window.AITE_STUDIO = { exporter };
  window.AITE.charger(window.AITE_RESSOURCES).then(() => {
    window.AITE_PRET = true;
    if (/[?&]lot=1/.test(location.search)) return;
    const b = lireBrouillon();
    etat.pub = (b && b.pub) || (BIBLIO.publications[0] ? JSON.parse(JSON.stringify(BIBLIO.publications[0])) : vierge('citation'));
    etat.pub.signature = etat.pub.signature || { nom: SIG.nom, fonction: SIG.fonction };
    etat.pub.site = etat.pub.site || window.AITE.SITE;
    etat.pub.hashtags = etat.pub.hashtags || [];
    etat.format = (b && b.format) || 'carre';
    construire();
  }).catch(e => {
    window.AITE_ERREUR = String(e && e.message || e);
    $('chargement').textContent = 'Le studio n’a pas pu se charger : ' + window.AITE_ERREUR;
  });
})();
