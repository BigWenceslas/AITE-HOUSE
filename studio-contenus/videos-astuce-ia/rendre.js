// node rendre.js <nom> [--apercu]  → MP4 1080x1920 30 i/s, ou planche d'images fixes
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path'); const { spawn, execFileSync } = require('child_process');
const V = __dirname, nom = process.argv[2], apercu = process.argv.includes('--apercu'), FPS = 30;
const plan = JSON.parse(fs.readFileSync(path.join(V, 'plan.json')))[nom];
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.goto('file://' + path.join(V, 'page.html')); await p.evaluate(pl => window.charger(pl), plan);
  if (apercu) {
    fs.mkdirSync(path.join(V, 'apercu'), { recursive: true });
    for (const [i, s] of plan.scenes.entries()) {
      await p.evaluate(t => window.seek(t), s.debut + s.duree * 0.8);
      await p.screenshot({ path: path.join(V, 'apercu', `${nom}-${i}.jpg`), type: 'jpeg', quality: 80 });
    }
    await b.close(); return;
  }
  const n = Math.ceil(plan.total * FPS), video = path.join(V, nom + '-video.mp4');
  const ff = spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p', video]);
  for (let f = 0; f < n; f++) {
    await p.evaluate(t => window.seek(t), f / FPS);
    const buf = await p.screenshot({ type: 'jpeg', quality: 92 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
  }
  ff.stdin.end(); await new Promise(r => ff.on('close', r));
  // sons : musique et bruitages synthétisés, puis voix posée 0,3 s après le début de chaque scène
  const evs = await p.evaluate(() => window.EVENEMENTS); fs.writeFileSync(path.join(V, nom + '-ev.json'), JSON.stringify(evs));
  const mus = path.join(V, nom + '-musique.wav'), bru = path.join(V, nom + '-bruitages.wav');
  execFileSync(path.join(V, '.venv-tts/bin/python'), [path.join(V, 'sons.py'), path.join(V, nom + '-ev.json'), String(plan.total), mus, bru]);
  const args = ['-v', 'error', '-y', '-i', video, '-i', mus, '-i', bru]; const filt = [];
  plan.scenes.forEach((s, i) => { args.push('-i', s.audio); const d = Math.round((s.debut + 0.3) * 1000); filt.push(`[${i + 3}]adelay=${d}|${d}[a${i}]`); });
  filt.push(plan.scenes.map((_, i) => `[a${i}]`).join('') + `amix=inputs=${plan.scenes.length}:normalize=0,apad,atrim=0:${plan.total}[voix]`);
  filt.push(`[1]volume=0.11[m]`, `[2]volume=0.55[b]`, `[voix][m][b]amix=inputs=3:normalize=0,loudnorm=I=-16:TP=-2[a]`);
  args.push('-filter_complex', filt.join(';'), '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', '-ar', '48000', '-movflags', '+faststart', path.join(V, nom + '.mp4'));
  execFileSync('ffmpeg', args); fs.unlinkSync(video); await b.close(); console.log('ok', nom, n, 'images');
})();
