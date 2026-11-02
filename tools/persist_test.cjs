const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ args: ['--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist','--no-sandbox'] });
  const p = await (await b.newContext({ viewport: { width: 700, height: 700 } })).newPage();
  p.on('pageerror', e => console.log('pageerror:', e.message));
  const url = 'http://127.0.0.1:5173/?material=clear';
  const ready = async (tag) => {
    await p.goto(url, { waitUntil: 'commit', timeout: 60000 });
    await p.waitForFunction('window.__logoReady === true', null, { timeout: 90000, polling: 500 });
    console.log('ready', tag);
  };
  await ready('first');
  await p.evaluate(() => { const s = __logo.settings; s.glass.ior = 1.83; s.glass.dispersion = 1.7; s.occlusion.intensity = 0.6; __logo.update(); });
  await ready('after reload');
  console.log('restored:', await p.evaluate(() => { const s = __logo.settings; return [s.glass.ior, s.glass.dispersion, s.occlusion.intensity].join(', '); }));
  // paste-JSON path through the same API the panel uses
  await p.evaluate(() => { const gui = document.querySelector('.lil-gui'); window.__before = __logo.settings.glass.ior; });
  const txt = await p.evaluate(() => { const j = JSON.parse(JSON.stringify(__logo.settings)); j.glass.ior = 1.2; return JSON.stringify(j); });
  // set via the JSON text field in the panel
  await p.evaluate(() => { document.querySelectorAll('.lil-gui .lil-title, .lil-gui .title').forEach((t) => { if (t.textContent.includes('Save')) t.click(); }); });
  const input = p.locator('.lil-gui input[type=text]').last();
  await input.fill(txt); await input.press('Enter'); await p.waitForTimeout(500);
  console.log('after paste:', await p.evaluate(() => __logo.settings.glass.ior));
  await p.screenshot({ path: '/tmp/claude-0/persist.png' });
  await b.close();
})();
