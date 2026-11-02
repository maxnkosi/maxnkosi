const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ args: ['--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist','--no-sandbox'] });
  const p = await (await b.newContext({ viewport: { width: 700, height: 700 } })).newPage();
  p.on('pageerror', e => console.log('pageerror:', e.message));
  const reqs = []; p.on('request', r => reqs.push(r.url().replace('http://127.0.0.1:5173','')));
  await p.addInitScript(() => { window.__raf = 0; const o = window.requestAnimationFrame.bind(window); window.requestAnimationFrame = (f) => { window.__raf++; return o(f); }; });
  await p.goto('http://127.0.0.1:5173/?material=clear&view=oblique&panel=0', { waitUntil: 'commit', timeout: 90000 });
  await p.waitForFunction('window.__logoReady === true', null, { timeout: 120000, polling: 500 });
  await p.waitForTimeout(1500);
  const a = await p.evaluate(() => window.__raf); await p.waitForTimeout(3000); const c = await p.evaluate(() => window.__raf);
  console.log('rAF calls in 3s while idle:', c - a);
  console.log('AO/GUI chunks fetched before use:', reqs.filter(u => /GTAO|lil-gui|EffectComposer/.test(u)).length);
  await p.evaluate(() => { __logo.settings.occlusion.enabled = true; __logo.update(); });
  await p.waitForTimeout(5000);
  console.log('AO chunks fetched after enabling:', reqs.filter(u => /GTAO|EffectComposer/.test(u)).length);
  await p.screenshot({ path: 'reference/screenshots/opt-clear-oblique-ao.png' });
  await b.close();
})();
