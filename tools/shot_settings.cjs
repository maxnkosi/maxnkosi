const { chromium } = require('playwright');
(async () => {
  const [base, outDir] = process.argv.slice(2);
  const b = await chromium.launch({ args: ['--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist','--no-sandbox'] });
  const p = await b.newPage({ viewport: { width: 1000, height: 900 } });
  p.on('pageerror', e => console.log('pageerror:', e.message));
  p.on('console', m => { if (m.type()==='error'||m.type()==='warning') console.log('console:', m.text().slice(0,300)); });
  await p.goto(`${base}/?view=oblique&material=clear`, { waitUntil: 'commit', timeout: 120000 });
  await p.waitForFunction('window.__logoReady === true', null, { timeout: 120000 });
  await p.waitForTimeout(1000);
  await p.screenshot({ path: `${outDir}/panel-default.png`, timeout: 120000 }); console.log('default');
  await p.evaluate(() => { const s = __logo.settings; s.glass.ior = 1.9; s.glass.dispersion = 2.5; s.glass.absorption = 0.4; s.glass.tint = '#7fe0f0'; s.occlusion.enabled = true; s.occlusion.intensity = 1.3; __logo.update(); });
  await p.waitForTimeout(4000);
  await p.screenshot({ path: `${outDir}/panel-changed.png`, timeout: 120000 }); console.log('changed');
  await b.close();
})();
