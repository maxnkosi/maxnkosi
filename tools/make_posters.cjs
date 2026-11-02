const { chromium } = require('playwright');
const sharp = require('sharp');
(async () => {
  const b = await chromium.launch({ args: ['--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist','--no-sandbox'] });
  const p = await (await b.newContext({ viewport: { width: 640, height: 640 } })).newPage();
  p.on('pageerror', e => console.log('pageerror:', e.message));
  for (const mat of ['branded', 'clear']) {
    await p.goto(`http://127.0.0.1:5173/?material=${mat}&panel=0&view=front`, { waitUntil: 'commit', timeout: 90000 });
    await p.waitForFunction('window.__logoReady === true && document.querySelector("#logo").dataset.ready', null, { timeout: 120000, polling: 500 });
    await p.waitForTimeout(1200);
    const png = await p.screenshot();
    await sharp(png).resize(512).webp({ quality: 80 }).toFile(`public/posters/${mat}.webp`);
    await p.screenshot({ path: `reference/screenshots/opt-${mat}-front.png` });
    console.log('poster', mat);
  }
  await b.close();
})();
