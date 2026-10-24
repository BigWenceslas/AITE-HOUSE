// Exporte flyer.html en PNG carré : 1080 px (réseaux sociaux) et 2160 px (HD).
// Usage : node render.js [dossier_de_sortie]   (par défaut : le dossier parent)
const path = require('path');
const { chromium } = require('playwright');

(async () => {
  const out = process.argv[2] || path.join(__dirname, '..');
  const page_url = 'file://' + path.join(__dirname, 'flyer.html');
  const browser = await chromium.launch();
  for (const [scale, suffix] of [[1, ''], [2, '_HD']]) {
    const page = await browser.newPage({ viewport: { width: 1080, height: 1080 }, deviceScaleFactor: scale });
    await page.goto(page_url);
    await page.evaluate(() => document.fonts.ready);
    await page.screenshot({ path: path.join(out, `AITE_bon_week_end_famille${suffix}.png`) });
    await page.close();
  }
  await browser.close();
})();
