const { chromium } = require('playwright');
(async () => {
  const [base, outDir] = process.argv.slice(2);
  const b = await chromium.launch({ args: ['--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist','--no-sandbox'] });
  const p = await b.newPage({ viewport: { width: 700, height: 700 } });
  p.on('pageerror', e => console.log('pageerror:', e.message));
  for (const [name, js, extra] of [
    ['ao-rough', 's.glass.roughness=0.02', ''],
    ['ao-solidbg', 's.occlusion.intensity=1', '&bg=eee'],
  ]) {
    const mat = 'clear';
    await p.goto(`${base}/?view=oblique&material=${mat}&panel=0${extra}`, { waitUntil: 'commit', timeout: 120000 });
    await p.waitForFunction('window.__logoReady === true', null, { timeout: 120000 });
    await p.evaluate((js) => { const s = __logo.settings; s.occlusion.enabled = true; eval(js); __logo.update(); }, js);
    await p.waitForTimeout(4000);
    await p.screenshot({ path: `${outDir}/${name}.png`, timeout: 120000 }); console.log(name);
  }
  await b.close();
})();
